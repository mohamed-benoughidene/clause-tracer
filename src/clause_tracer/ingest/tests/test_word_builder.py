"""The Word fixture builder writes a package a test can state exactly (S5-M1-T7)."""

import io
import xml.etree.ElementTree as ET
import zipfile

from clause_tracer.ingest.tests.builders.word import (
    br,
    build_docx,
    comment,
    comment_range,
    delete,
    ins,
    p,
    r,
    tab,
    tbl,
)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _texts(data: bytes) -> dict[str, str]:
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        return {name: package.read(name).decode() for name in package.namelist()}


def test_builds_a_zip() -> None:
    data = build_docx(p(r("Hello")))

    with zipfile.ZipFile(io.BytesIO(data)) as package:
        names = package.namelist()

    assert names[:4] == [
        "[Content_Types].xml",
        "_rels/.rels",
        "word/document.xml",
        "word/_rels/document.xml.rels",
    ]


def test_same_bytes_twice() -> None:
    assert build_docx(p(r("Hello"))) == build_docx(p(r("Hello")))


def test_body_is_wrapped() -> None:
    text = _texts(build_docx(p(r("Hello"))))["word/document.xml"]

    assert text.startswith("<?xml")
    assert W_NS in text
    assert "<w:body><w:p><w:r>" in text


def test_optional_parts_are_absent_by_default() -> None:
    names = _texts(build_docx(p(r("Hello"))))

    assert "word/comments.xml" not in names
    assert "word/styles.xml" not in names


def test_every_part_parses() -> None:
    data = build_docx(
        p(r("Hello")),
        styles="<w:style w:type='paragraph' w:styleId='Normal'/>",
        numbering='<w:abstractNum w:abstractNumId="0"/>',
        comments=comment(0, "A", "Note"),
        footnotes='<w:footnote w:id="1"><w:p/></w:footnote>',
        endnotes='<w:endnote w:id="1"><w:p/></w:endnote>',
        headers={"header1.xml": p(r("Head"))},
        footers={"footer1.xml": p(r("Foot"))},
        settings="",
    )

    texts = _texts(data)
    optional_parts = {
        f"word/{part}.xml"
        for part in (
            "styles",
            "numbering",
            "comments",
            "footnotes",
            "endnotes",
            "settings",
            "header1",
            "footer1",
        )
    }
    assert optional_parts <= set(texts)
    for name, text in texts.items():
        if name.endswith(".xml") or name.endswith(".rels"):
            ET.fromstring(text)


def test_external_relationship() -> None:
    relationship = (
        '<Relationship Id="rId9" Type="http://x/template" '
        'Target="http://127.0.0.1:9/x" TargetMode="External"/>'
    )
    text = _texts(build_docx(p(r("Hello")), document_rels=(relationship,)))[
        "word/_rels/document.xml.rels"
    ]

    assert relationship in text


def test_helpers() -> None:
    assert p(r("Hello")) == '<w:p><w:r><w:t xml:space="preserve">Hello</w:t></w:r></w:p>'
    assert p(style="Heading1", num=(2, 1)) == (
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/>'
        '<w:numPr><w:ilvl w:val="1"/><w:numId w:val="2"/></w:numPr></w:pPr></w:p>'
    )
    assert r("A") == '<w:r><w:t xml:space="preserve">A</w:t></w:r>'
    assert r(
        "A",
        hidden=True,
        color="FF0000",
        size_half_points=12,
        shading="FFFF00",
        style="Strong",
        bold=True,
    ) == (
        '<w:r><w:rPr><w:rStyle w:val="Strong"/><w:b/><w:color w:val="FF0000"/>'
        '<w:sz w:val="12"/><w:shd w:fill="FFFF00"/><w:vanish/></w:rPr>'
        '<w:t xml:space="preserve">A</w:t></w:r>'
    )
    assert r("<&>") == '<w:r><w:t xml:space="preserve">&lt;&amp;&gt;</w:t></w:r>'
    assert tab() == "<w:r><w:tab/></w:r>"
    assert br() == "<w:r><w:br/></w:r>"
    assert ins("A", r("B")) == (
        '<w:ins w:id="1" w:author="A" w:date="2026-01-01T00:00:00Z">'
        '<w:r><w:t xml:space="preserve">B</w:t></w:r></w:ins>'
    )
    assert delete("A", "B") == (
        '<w:del w:id="1" w:author="A" w:date="2026-01-01T00:00:00Z">'
        '<w:r><w:delText xml:space="preserve">B</w:delText></w:r></w:del>'
    )
    assert tbl((r("A"),), (r("B"),)) == (
        '<w:tbl><w:tr><w:tc><w:p><w:r><w:t xml:space="preserve">A</w:t></w:r></w:p></w:tc></w:tr>'
        '<w:tr><w:tc><w:p><w:r><w:t xml:space="preserve">B</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
    )
    assert comment_range(0, r("A")) == (
        '<w:commentRangeStart w:id="0"/><w:r><w:t xml:space="preserve">A</w:t></w:r>'
        '<w:commentRangeEnd w:id="0"/>'
        '<w:r><w:commentReference w:id="0"/></w:r>'
    )
    assert comment(0, "A", "x") == (
        '<w:comment w:id="0" w:author="A">'
        '<w:p><w:r><w:t xml:space="preserve">x</w:t></w:r></w:p></w:comment>'
    )
