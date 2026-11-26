"""The hostile fixtures promise what their names say (S5-M1-T9).

These tests never read an entity file with a parser: they only look at
the bytes, as the reading tests of M2 and M4 will do the reading.
"""

import io
import zipfile
from typing import Literal

import pikepdf
import pypdfium2
import pytest

from clause_tracer.ingest.tests.builders.hostile import (
    big_xml_docx,
    deep_xml_docx,
    doctype_docx,
    entity_docx,
    external_rel_docx,
    false_declared_size_docx,
    huge_text_node_docx,
    lying_low_docx,
    many_members_docx,
    not_a_zip,
    ole2_bytes,
    pdf_dense_text,
    pdf_image_bomb,
    pdf_many_pages,
    zip_bomb_docx,
)


def _member(data: bytes, name: str) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        return package.read(name)


def test_zip_bomb_is_small_and_large() -> None:
    expanded = 20_000_000
    data = zip_bomb_docx(expanded)

    assert len(data) < expanded / 100
    assert abs(len(_member(data, "word/document.xml")) - expanded) <= 1024


def test_many_members_count() -> None:
    with zipfile.ZipFile(io.BytesIO(many_members_docx(50))) as package:
        assert len(package.namelist()) == 50


def test_false_size_lies() -> None:
    declared = 10_000_000
    data = false_declared_size_docx(declared)

    with zipfile.ZipFile(io.BytesIO(data)) as package:
        info = package.getinfo("word/document.xml")
        assert info.file_size == declared
        assert len(package.read("word/document.xml")) < declared


@pytest.mark.parametrize("kind", ["internal", "external_file", "external_url", "parameter"])
def test_entity_kinds_have_a_doctype(
    kind: Literal["internal", "external_file", "external_url", "parameter"],
) -> None:
    text = _member(entity_docx(kind), "word/document.xml").decode()

    assert "<!DOCTYPE" in text
    assert "<!ENTITY" in text


def test_doctype_only() -> None:
    text = _member(doctype_docx(), "word/document.xml").decode()

    assert "<!DOCTYPE" in text
    assert "<!ENTITY" not in text


def test_external_rel_targets() -> None:
    text = _member(external_rel_docx(), "word/_rels/document.xml.rels").decode()

    assert text.count('TargetMode="External"') == 3
    assert text.count('Target="http://127.0.0.1:9/x"') == 3


def test_deep_xml_depth() -> None:
    depth = 100
    text = _member(deep_xml_docx(depth), "word/document.xml").decode()

    assert text.count("<w:sdt>") == depth


def test_huge_text_node() -> None:
    size = 1000
    text = _member(huge_text_node_docx(size), "word/document.xml").decode()

    assert "a" * size in text


def test_big_xml_size() -> None:
    size = 1_000_000
    text = _member(big_xml_docx(size), "word/document.xml")

    assert abs(len(text) - size) <= 1024


def test_ole2_signature() -> None:
    data = ole2_bytes()

    assert data.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
    assert len(data) == 512


def test_not_a_zip_starts_with_pk_zip_header() -> None:
    data = not_a_zip()

    assert data.startswith(b"PK\x03\x04")
    assert zipfile.is_zipfile(io.BytesIO(data)) is False


def test_lying_low_sizes() -> None:
    data = lying_low_docx()

    with zipfile.ZipFile(io.BytesIO(data)) as package:
        info = package.getinfo("word/document.xml")
        assert info.file_size == 10
        if info.file_size == 10:
            try:
                content = package.read("word/document.xml")
            except zipfile.BadZipFile:
                return
            assert len(content) > 10


def test_pdf_many_pages_count() -> None:
    pdf = pikepdf.open(io.BytesIO(pdf_many_pages(1000)))
    try:
        assert len(pdf.pages) == 1000
    finally:
        pdf.close()


def test_image_bomb_is_small() -> None:
    data = pdf_image_bomb(20_000, 20_000)

    assert len(data) < 1_000_000


def test_dense_text_pages() -> None:
    pages, chars_per_page = 3, 5_000
    data = pdf_dense_text(pages, chars_per_page)
    document = pypdfium2.PdfDocument(data)
    try:
        assert len(document) == pages
        text = document[0].get_textpage().get_text_range()
    finally:
        document.close()

    assert len(text.replace("\r\n", "")) >= chars_per_page
