"""The public Word call (S5-M3-T8)."""

import io
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import clause_tracer.ingest
from clause_tracer.core import (
    Document,
    EmptyInputError,
    FileKind,
    HiddenReason,
    HiddenText,
    InputError,
    InputTooLargeError,
    OldWordFileError,
    SideText,
    SideTextKind,
    Span,
    TrackedChange,
    UnreadableFileError,
)
from clause_tracer.ingest import (
    WARNING_NOT_ENGLISH,
    WARNING_WORD_NOTES,
    WARNING_WORD_NUMBERING_UNKNOWN,
    WARNING_WORD_SYMBOL_UNREAD,
    read_file,
    read_text_file,
    read_word_file,
    split_clauses,
)
from clause_tracer.ingest.limits import MAX_ZIP_MEMBERS
from clause_tracer.ingest.tests.builders.hostile import (
    deep_xml_docx,
    doctype_docx,
    many_members_docx,
    ole2_bytes,
    zip_bomb_docx,
)
from clause_tracer.ingest.tests.builders.word import (
    build_docx,
    comment,
    comment_range,
    ins,
    p,
    r,
)

_MIB = 1024 * 1024

_DECIMAL = (
    '<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0">'
    '<w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/>'
    '</w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
)
_ORDINAL = _DECIMAL.replace('w:numFmt w:val="decimal"', 'w:numFmt w:val="ordinal"')
_FRENCH = (
    "Le contrat est conclu entre les parties et il prend effet le premier jour "
    "du mois qui suit la signature des deux parties."
)
_SEPARATOR = '<w:footnote w:type="separator" w:id="-1">' + p() + "</w:footnote>"


def _read(body: str = "", **parts: Any) -> Document:
    data = build_docx(body, **parts)
    return read_word_file(data, name="t.docx")


def _codes(document: Document) -> list[str]:
    return [warning.code for warning in document.warnings]


def _without_member(data: bytes, name: str) -> bytes:
    buffer = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(data)) as source,
        zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as target,
    ):
        for info in source.infolist():
            if info.filename != name:
                target.writestr(info, source.read(info.filename))
    return buffer.getvalue()


def test_reads_a_simple_file() -> None:
    document = _read(p(r("Hello world.")))

    assert document.text == "Hello world.\n"
    assert document.source.kind is FileKind.WORD
    assert document.char_map == ()
    assert document.warnings == ()


def test_every_shape_field() -> None:
    footnotes = _SEPARATOR + f'<w:footnote w:id="1">{p(r("Note"))}</w:footnote>'
    body = p(
        r("Keep "),
        r("hidden", hidden=True),
        comment_range(0, r("this")),
        ins("A", r("new")),
        '<w:r><w:footnoteReference w:id="1"/></w:r>',
    )
    data = build_docx(
        body,
        comments=comment(0, "Ann", "check"),
        footnotes=footnotes,
        headers={"header1.xml": p(r("Head"))},
    )

    document = read_word_file(data, name="t.docx")

    assert document.text == "Keep hiddenthisnew\n"
    assert document.hidden == (
        HiddenText(span=Span(start=5, end=11), reason=HiddenReason.WORD_HIDDEN_RUN, boxes=()),
        HiddenText(span=Span(start=11, end=15), reason=HiddenReason.COMMENT, boxes=()),
        HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=()),
    )
    assert document.side_text == (
        SideText(
            kind=SideTextKind.COMMENT,
            ref="0",
            author="Ann",
            text="check",
            span=Span(start=11, end=15),
        ),
        SideText(kind=SideTextKind.FOOTNOTE, ref="1", author="", text="Note"),
        SideText(kind=SideTextKind.HEADER, ref="word/header1.xml", author="", text="Head"),
    )
    assert document.tracked_changes == (
        TrackedChange(earlier="", new="new", author="A", span=Span(start=15, end=18)),
    )
    assert document.char_map == ()
    assert document.glyphs == ()
    assert document.pages == ()
    assert document.furniture == ()
    assert document.undecodable == ()
    assert document.source.size == len(data)
    assert document.source.sha256
    assert _codes(document) == [WARNING_WORD_NOTES]


def test_hidden_order() -> None:
    body = p(r("A"), comment_range(0, r("x")), r("B"), r("y", hidden=True))

    document = _read(body, headers={"header1.xml": p(r("Head"))})

    assert [item.reason for item in document.hidden] == [
        HiddenReason.COMMENT,
        HiddenReason.WORD_HIDDEN_RUN,
        HiddenReason.WORD_PART_NEVER_SHOWN,
    ]
    assert document.hidden[0].span == Span(start=1, end=2)
    assert document.hidden[1].span == Span(start=3, end=4)
    assert document.hidden[2].span is None


def test_warning_order() -> None:
    footnotes = _SEPARATOR + f'<w:footnote w:id="1">{p(r("Note"))}</w:footnote>'
    body = p(
        r(_FRENCH),
        '<w:r><w:sym w:char="F0FC"/></w:r>',
        '<w:r><w:footnoteReference w:id="1"/></w:r>',
        num=(1, 0),
    )

    document = _read(body, numbering=_ORDINAL, footnotes=footnotes)

    assert _codes(document) == [
        WARNING_WORD_NUMBERING_UNKNOWN,
        WARNING_WORD_SYMBOL_UNREAD,
        WARNING_WORD_NOTES,
        WARNING_NOT_ENGLISH,
    ]


def test_symbol_warning() -> None:
    body = p(
        '<w:r><w:sym w:char="F0FC"/></w:r><w:r><w:sym w:char="F0FD"/></w:r>',
        r("A"),
    )

    assert _codes(_read(body)) == [WARNING_WORD_SYMBOL_UNREAD]


def test_old_word_file() -> None:
    with pytest.raises(OldWordFileError):
        read_word_file(ole2_bytes(), name="a.doc")


def test_wrong_kind_is_a_caller_bug() -> None:
    with pytest.raises(ValueError, match="read_word_file reads Word files only"):
        read_word_file(b"%PDF-1.7\n%%EOF\n", name="a.pdf")


def test_empty_body_raises_empty_input() -> None:
    with pytest.raises(EmptyInputError):
        _read("")


def test_word_limit() -> None:
    with pytest.raises(InputTooLargeError):
        _read(p(r("word")) * 50_001)


def test_not_english_warning() -> None:
    assert _codes(_read(p(r(_FRENCH)))) == [WARNING_NOT_ENGLISH]


@pytest.mark.parametrize(
    ("build", "error_type", "reason"),
    [
        pytest.param(
            lambda: many_members_docx(MAX_ZIP_MEMBERS + 1),
            UnreadableFileError,
            "too_many_members",
            id="many-members",
        ),
        pytest.param(doctype_docx, UnreadableFileError, "doctype", id="doctype"),
        pytest.param(lambda: deep_xml_docx(255), UnreadableFileError, "xml_invalid", id="deep"),
        pytest.param(lambda: zip_bomb_docx(100 * _MIB), InputTooLargeError, None, id="zip-bomb"),
    ],
)
def test_hostile_files_keep_their_errors(
    build: Callable[[], bytes], error_type: type[InputError], reason: str | None
) -> None:
    with pytest.raises(error_type) as raised:
        read_word_file(build(), name="a.docx")

    if reason is not None:
        assert raised.value.context["reason"] == reason


def test_only_unreferenced_notes_still_warn() -> None:
    footnotes = f'<w:footnote w:id="1">{p(r("Away"))}</w:footnote>'

    document = _read(p(r("A")), footnotes=footnotes)

    assert _codes(document) == [WARNING_WORD_NOTES]
    assert [item.text for item in document.side_text] == ["Away"]


def test_missing_document_part() -> None:
    data = _without_member(build_docx(p(r("A"))), "word/document.xml")

    with pytest.raises(UnreadableFileError) as raised:
        read_word_file(data, name="a.docx")

    assert raised.value.context["reason"] == "not_a_word_file"


def test_read_file_dispatches_word() -> None:
    data = build_docx(p(r("Hello")))

    assert read_file(data, name="a.docx") == read_word_file(data, name="a.docx")


def test_splitter_reads_a_numbered_word_file() -> None:
    body = p(r("One"), num=(1, 0)) + p(r("Two"), num=(1, 0)) + p(r("Three"), num=(1, 0))

    document = _read(body, numbering=_DECIMAL)

    assert document.text == "1. One\n2. Two\n3. Three\n"
    assert [clause.number for clause in split_clauses(document)] == ["1", "2", "3"]


def test_text_files_unchanged() -> None:
    document = read_text_file(b"Hello world.\n", kind=FileKind.TEXT, name="a.txt")

    assert document.text == "Hello world.\n"
    assert document.hidden == ()
    assert document.side_text == ()


def test_public_names_and_readme() -> None:
    for name in ("read_word_file", "WARNING_WORD_NOTES", "WARNING_WORD_NUMBERING_UNKNOWN"):
        assert name in clause_tracer.ingest.__all__

    readme = Path(clause_tracer.ingest.__file__ or "").parent / "README.md"
    text = readme.read_text(encoding="utf-8")
    for name in (
        "read_word_file",
        "WARNING_WORD_NOTES",
        "WARNING_WORD_NUMBERING_UNKNOWN",
        "WARNING_WORD_SYMBOL_UNREAD",
    ):
        assert name in text
