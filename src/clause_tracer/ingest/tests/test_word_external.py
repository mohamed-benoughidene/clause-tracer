"""External relationships of a Word file (S5-M3-T7)."""

import socket
from collections.abc import Mapping

import pytest

from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_side import read_headers_and_footers, read_relationships
from clause_tracer.ingest._xml import Element, parse_part
from clause_tracer.ingest._zip import open_package
from clause_tracer.ingest.tests.builders.hostile import external_rel_docx
from clause_tracer.ingest.tests.builders.word import build_docx, p, r

_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"


def _relationships(*targets: tuple[str, str]) -> Element:
    inner = "".join(
        f'<Relationship Id="{rel_id}" Type="{_TYPE}" Target="{target}"/>'
        for rel_id, target in targets
    )
    return parse_part(f'<Relationships xmlns="{_REL_NS}">{inner}</Relationships>'.encode())


def _map(data: bytes) -> Mapping[str, str]:
    package = open_package(data)
    root = parse_part(package.read_part("word/_rels/document.xml.rels"))
    return read_relationships(root)


def test_external_targets_are_left_out() -> None:
    relationships = _map(external_rel_docx())

    assert "rIdTemplate" not in relationships
    assert "rIdImage" not in relationships
    assert "rIdLink" not in relationships


def test_relative_target_is_kept() -> None:
    data = build_docx(p(r("A")), headers={"header1.xml": p(r("Head"))})

    assert _map(data) == {"rId1": "word/header1.xml"}


def test_dotdot_and_scheme_are_left_out() -> None:
    root = _relationships(
        ("a", "../x.xml"),
        ("b", "http://x"),
        ("c", "/x"),
        ("d", "file:///x"),
        ("e", "header1.xml"),
    )

    assert dict(read_relationships(root)) == {"e": "word/header1.xml"}


def test_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("a connection was opened")

    monkeypatch.setattr(socket.socket, "connect", fail)

    assert _map(external_rel_docx()) == {}


def test_hyperlink_text_is_read() -> None:
    link = '<w:hyperlink r:id="rIdLink"><w:r><w:t>Link</w:t></w:r></w:hyperlink>'
    external = (
        '<Relationship Id="rIdLink" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
        'Target="http://127.0.0.1:9/x" TargetMode="External"/>'
    )
    data = build_docx(p(link), document_rels=(external,))
    package = open_package(data)
    root = parse_part(package.read_part("word/document.xml"))

    assert build_body(root).text == "Link\n"


def test_attached_template_is_ignored() -> None:
    relationships = _map(external_rel_docx())

    assert "rIdTemplate" not in relationships
    package = open_package(external_rel_docx())
    root = parse_part(package.read_part("word/document.xml"))
    sections = build_body(root).sections

    assert read_headers_and_footers(package, relationships, sections, False, None) == ((), ())
