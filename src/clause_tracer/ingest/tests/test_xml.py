"""The hardened XML parser (S5-M2-T4)."""

import socket
import time
from pathlib import Path
from typing import Literal

import pytest

from clause_tracer.core import UnreadableFileError
from clause_tracer.ingest import _xml
from clause_tracer.ingest._xml import W_NS, _check_part, parse_part, qname
from clause_tracer.ingest._zip import open_package
from clause_tracer.ingest.limits import MAX_XML_DEPTH, MAX_XML_TEXT_BYTES
from clause_tracer.ingest.tests.builders.hostile import (
    deep_xml_docx,
    doctype_docx,
    entity_docx,
    huge_text_node_docx,
)
from clause_tracer.ingest.tests.builders.word import build_docx, p, r

_DOCUMENT = "word/document.xml"
_MIB = 1024 * 1024
CAP = MAX_XML_TEXT_BYTES


def _document(data: bytes) -> bytes:
    return open_package(data).read_part(_DOCUMENT)


def _reason(error: UnreadableFileError) -> str:
    return str(error.context["reason"])


def test_parses_a_plain_part() -> None:
    root = parse_part(_document(build_docx(p(r("Hello")))))

    assert root.tag == qname(W_NS, "document")
    assert qname(W_NS, "body") == f"{{{W_NS}}}body"


def test_doctype_is_refused() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        parse_part(_document(doctype_docx()))

    assert _reason(raised.value) == "doctype"


def test_every_entity_kind_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_connect(*args: object, **kwargs: object) -> None:
        raise AssertionError("a socket opened")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    kinds: tuple[Literal["internal", "external_file", "external_url", "parameter"], ...] = (
        "internal",
        "external_file",
        "external_url",
        "parameter",
    )

    for kind in kinds:
        with pytest.raises(UnreadableFileError) as raised:
            parse_part(_document(entity_docx(kind)))
        assert _reason(raised.value) == "doctype"


def _billion_laughs() -> bytes:
    entities = ['<!ENTITY e0 "lol">']
    for index in range(1, 10):
        reference = f"&e{index - 1};" * 10
        entities.append(f'<!ENTITY e{index} "{reference}">')
    return (
        '<?xml version="1.0"?>'
        f"<!DOCTYPE w:document [{''.join(entities)}]>"
        f'<w:document xmlns:w="{W_NS}"><w:body><w:p><w:r><w:t>&e9;</w:t></w:r></w:p>'
        "</w:body></w:document>"
    ).encode()


def test_billion_laughs_is_refused_fast() -> None:
    started = time.monotonic()
    with pytest.raises(UnreadableFileError) as raised:
        parse_part(_billion_laughs())
    elapsed = time.monotonic() - started

    assert _reason(raised.value) == "doctype"
    assert elapsed < 1.0


def test_depth_256_parses_and_257_fails() -> None:
    assert parse_part(_document(deep_xml_docx(254))) is not None

    with pytest.raises(UnreadableFileError) as raised:
        parse_part(_document(deep_xml_docx(255)))

    assert _reason(raised.value) == "xml_invalid"
    assert MAX_XML_DEPTH == 256


def test_huge_text_node() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        parse_part(_document(huge_text_node_docx(11 * _MIB)))

    assert _reason(raised.value) == "xml_invalid"
    assert parse_part(_document(huge_text_node_docx(5 * _MIB))) is not None


def test_bad_xml() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        parse_part(b"<a>")

    assert _reason(raised.value) == "xml_invalid"


def test_comments_and_pis_are_dropped() -> None:
    xml = (
        '<?xml version="1.0"?>'
        f'<w:document xmlns:w="{W_NS}"><!-- note -->'
        "<w:body><?target data?><w:p/></w:body></w:document>"
    ).encode()

    root = parse_part(xml)

    tags = [node.tag for node in root.iter()]
    assert all(isinstance(tag, str) for tag in tags)


def test_only_utf8_and_utf16_labels() -> None:
    assert parse_part('<?xml version="1.0" encoding="UTF-16"?><a/>'.encode("utf-16")) is not None

    with pytest.raises(UnreadableFileError) as raised:
        parse_part(b'<?xml version="1.0" encoding="ISO-8859-1"?><a/>')

    assert _reason(raised.value) == "xml_invalid"


def test_a_named_dtd_file_is_not_read(tmp_path: Path) -> None:
    dtd = tmp_path / "outside.dtd"
    dtd.write_text("not a DTD <<<", encoding="utf-8")
    part = f'<!DOCTYPE w:document SYSTEM "{dtd.as_uri()}"><w:document xmlns:w="{W_NS}"/>'

    with pytest.raises(UnreadableFileError) as raised:
        parse_part(part.encode())

    assert _reason(raised.value) == "doctype"


def _assert_refused(data: bytes) -> None:
    with pytest.raises(UnreadableFileError) as raised:
        parse_part(data)

    assert _reason(raised.value) == "xml_invalid"


def test_own_check_refuses_depth_257() -> None:
    _check_part(_document(deep_xml_docx(254)))

    with pytest.raises(UnreadableFileError) as raised:
        _check_part(_document(deep_xml_docx(255)))

    assert _reason(raised.value) == "xml_invalid"


def test_long_text_is_refused() -> None:
    assert parse_part(b"<a>" + b"x" * CAP + b"</a>") is not None

    _assert_refused(b"<a>" + b"x" * (CAP + 1) + b"</a>")


def test_text_limit_counts_utf8_bytes() -> None:
    assert parse_part(("<a>" + "\u00e9" * 4_500_000 + "</a>").encode()) is not None

    _assert_refused(("<a>" + "\u00e9" * 4_500_001 + "</a>").encode())


def test_long_cdata_is_refused() -> None:
    assert parse_part(b"<a><![CDATA[" + b"x" * CAP + b"]]></a>") is not None

    _assert_refused(b"<a><![CDATA[" + b"x" * (CAP + 1) + b"]]></a>")


def test_long_comment_is_refused() -> None:
    assert parse_part(b"<a><!--" + b"x" * CAP + b"--></a>") is not None

    _assert_refused(b"<a><!--" + b"x" * (CAP + 1) + b"--></a>")


def test_long_processing_instruction_is_refused() -> None:
    assert parse_part(b"<a><?t " + b"x" * (CAP - 1) + b"?></a>") is not None

    _assert_refused(b"<a><?t " + b"x" * CAP + b"?></a>")


def test_long_attributes_are_refused() -> None:
    one = b"x" * (CAP - 1)
    half = b"x" * (CAP // 2 - 1)

    assert parse_part(b'<a b="' + one + b'"/>') is not None
    assert parse_part(b'<a b="' + half + b'" c="' + half + b'"/>') is not None

    _assert_refused(b'<a b="' + one + b'x"/>')
    _assert_refused(b'<a b="' + half + b'" c="' + half + b'x"/>')


def test_only_a_tag_restarts_the_text_count() -> None:
    first = b"x" * (CAP // 2)
    second = b"x" * (CAP // 2 + 1)

    assert parse_part(b"<a>" + first + b"<b/>" + second + b"</a>") is not None

    _assert_refused(b"<a>" + first + b"<!--c-->" + second + b"</a>")


@pytest.mark.parametrize(("code", "error_type"), [(2, MemoryError), (4, UnreadableFileError)])
def test_lxml_out_of_memory_is_a_memory_error(
    monkeypatch: pytest.MonkeyPatch, code: int, error_type: type[BaseException]
) -> None:
    etree = vars(_xml)["etree"]  # No test imports lxml: _xml.py is its one importer.

    def fail(*args: object, **kwargs: object) -> None:
        raise etree.XMLSyntaxError("unknown error", code, 0, 0)

    monkeypatch.setattr(etree, "fromstring", fail)

    with pytest.raises(error_type):
        parse_part(b"<a/>")
