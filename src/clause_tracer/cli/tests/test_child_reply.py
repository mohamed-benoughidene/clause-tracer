"""The codec for the reply the child process writes (S5-M1-T6, S5-M2-T6)."""

import json
from pathlib import Path

import pytest

from clause_tracer.cli.child_reply import (
    MAX_CHILD_REPLY_BYTES,
    ChildDone,
    ChildFailed,
    decode_child_reply,
    encode_child_reply,
    input_error_for_code,
)
from clause_tracer.core import (
    Document,
    FileKind,
    Glyph,
    HiddenReason,
    HiddenText,
    InputError,
    InputWarning,
    Page,
    PageBox,
    SideText,
    SideTextKind,
    SourceFile,
    Span,
    TrackedChange,
    UnreadableFileError,
)

SOURCE = Path(__file__).resolve().parents[1] / "child_reply.py"


def _document() -> Document:
    text = "Pay in 30 days."
    return Document(
        schema_version=2,
        source=SourceFile(name="a.pdf", kind=FileKind.PDF, sha256="ab" * 32, size=15),
        text=text,
        char_map=(None,) * len(text),
        glyphs=(Glyph(page=1, box=PageBox(page=1, x0=1.0, top=2.0, x1=3.0, bottom=4.0)),),
        pages=(Page(number=1, width=612.0, height=792.0),),
        furniture=(Span(start=0, end=3),),
        hidden=(HiddenText(span=None, reason=HiddenReason.HIDDEN_LAYER, boxes=()),),
        undecodable=(Span(start=4, end=5),),
        tracked_changes=(
            TrackedChange(earlier="Pay", new="Pay now", author="A", span=Span(start=0, end=3)),
        ),
        warnings=(InputWarning(code="undecodable_page", page=1),),
        side_text=(SideText(kind=SideTextKind.COMMENT, ref="0", author="A", text="x"),),
    )


def _reason(error: InputError) -> object:
    return error.context["reason"]


def _input_error_classes() -> list[type[InputError]]:
    found: list[type[InputError]] = []
    pending: list[type[InputError]] = [InputError]
    while pending:
        error_class = pending.pop()
        for child in error_class.__subclasses__():
            pending.append(child)
            if child.code:
                found.append(child)
    return found


def test_done_round_trip() -> None:
    reply = ChildDone(document=_document())

    decoded = decode_child_reply(encode_child_reply(reply))

    assert decoded == reply


def test_failed_round_trip() -> None:
    reply = ChildFailed(code="scanned_pdf", context={"pages": 3})

    assert decode_child_reply(encode_child_reply(reply)) == reply


def test_every_input_error_code_maps_back() -> None:
    error_classes = _input_error_classes()

    assert error_classes
    for error_class in error_classes:
        rebuilt = input_error_for_code(error_class.code, {})
        assert type(rebuilt) is error_class


def test_unknown_code() -> None:
    error = input_error_for_code("not_a_code", {})

    assert isinstance(error, UnreadableFileError)
    assert _reason(error) == "child_error_code_unknown"


def test_context_is_kept() -> None:
    context: dict[str, str | int] = {"pages": 3, "name": "a.pdf"}

    assert dict(input_error_for_code("scanned_pdf", context).context) == context


@pytest.mark.parametrize("data", [b"", b"{", b'{"kind":"done"}', b'{"kind":"other"}'])
def test_bad_reply_raises(data: bytes) -> None:
    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(data)

    assert _reason(raised.value) == "child_reply_invalid"


def test_decode_refuses_large_reply() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(b"x" * (MAX_CHILD_REPLY_BYTES + 1))

    assert _reason(raised.value) == "child_reply_too_large"


def test_decode_is_strict() -> None:
    document = Document(
        schema_version=2,
        source=SourceFile(name="a.txt", kind=FileKind.TEXT, sha256="ab", size=1),
        text="x",
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )
    data = encode_child_reply(ChildDone(document=document))
    changed = data.replace(b'"size":1', b'"size":"1"')
    assert changed != data

    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(changed)

    assert _reason(raised.value) == "child_reply_invalid"


def test_decode_refuses_extra_field() -> None:
    reply = ChildDone(document=_document())
    payload = json.loads(encode_child_reply(reply))
    payload["extra"] = 1

    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(json.dumps(payload).encode())

    assert _reason(raised.value) == "child_reply_invalid"

    payload = json.loads(encode_child_reply(reply))
    payload["document"]["extra"] = 1

    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(json.dumps(payload).encode())

    assert _reason(raised.value) == "child_reply_invalid"


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_decode_refuses_non_finite_float(value: float) -> None:
    reply = ChildDone(document=_document())
    payload = json.loads(encode_child_reply(reply))
    payload["document"]["pages"][0]["width"] = value

    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(json.dumps(payload).encode())

    assert _reason(raised.value) == "child_reply_invalid"


def test_decode_refuses_other_schema_version() -> None:
    reply = ChildDone(document=_document())
    payload = json.loads(encode_child_reply(reply))
    payload["document"]["schema_version"] = 999

    with pytest.raises(UnreadableFileError) as raised:
        decode_child_reply(json.dumps(payload).encode())

    assert _reason(raised.value) == "child_reply_invalid"


def test_no_pickle() -> None:
    source = SOURCE.read_text()

    assert "pickle" not in source
    assert "eval(" not in source
