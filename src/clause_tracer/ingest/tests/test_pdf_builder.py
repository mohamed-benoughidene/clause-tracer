"""The PDF fixture builder places what it says it places (S5-M1-T8)."""

import io

import pdfplumber
import pikepdf
import pypdfium2
import pytest
from reportlab.pdfbase import pdfmetrics

from clause_tracer.ingest.tests.builders.pdf import (
    PageSpec,
    build_pdf,
    cropped_page,
    hidden_layer_page,
    many_pages,
    plain_page,
    rotated_page,
)


def _words(data: bytes) -> str:
    document = pypdfium2.PdfDocument(data)
    try:
        text = document[0].get_textpage().get_text_range()
    finally:
        document.close()
    return " ".join(text.split())


def test_same_text_twice() -> None:
    lines = ["Hello world", "Second line"]

    assert _words(plain_page(lines).data) == _words(plain_page(lines).data)


def test_placed_matches_text() -> None:
    built = plain_page(["Hello"])

    assert "".join(placed.char for placed in built.placed) == "Hello"


def test_placed_positions_follow_the_font() -> None:
    built = plain_page(["Hello"])
    first, second = built.placed[0], built.placed[1]

    assert second.x - first.x == pytest.approx(pdfmetrics.stringWidth("H", "Vera", 10.0))


def test_rotate_keeps_the_box() -> None:
    rotated = pikepdf.open(io.BytesIO(rotated_page(90).data))
    plain = pikepdf.open(io.BytesIO(plain_page(["Hello"]).data))
    try:
        assert rotated.pages[0].obj.Rotate == 90
        assert [float(value) for value in rotated.pages[0].mediabox] == [
            float(value) for value in plain.pages[0].mediabox
        ]
    finally:
        rotated.close()
        plain.close()


def test_crop_box_is_set() -> None:
    pdf = pikepdf.open(io.BytesIO(cropped_page().data))
    try:
        assert [float(value) for value in pdf.pages[0].cropbox] == [0.0, 0.0, 400.0, 600.0]
    finally:
        pdf.close()


def test_hidden_layer_is_off() -> None:
    pdf = pikepdf.open(io.BytesIO(hidden_layer_page().data))
    try:
        properties = pdf.Root.OptionalContentProperties
        groups = list(properties.OCGs)
        default = properties.D
        on = list(default.get("/ON", []))
        off = list(default.OFF)
    finally:
        pdf.close()

    assert len(groups) == 2
    assert [str(group.Name) for group in on] == ["Visible"]
    assert [str(group.Name) for group in off] == ["Hidden"]


def test_copy_off_flag() -> None:
    pdf = pikepdf.open(io.BytesIO(build_pdf([PageSpec()], copy_off=True).data))
    try:
        assert pdf.allow.extract is False
    finally:
        pdf.close()


def test_user_password_needs_it() -> None:
    data = build_pdf([PageSpec()], user_password="secret").data

    with pytest.raises(pikepdf.PasswordError):
        pikepdf.open(io.BytesIO(data))


def test_many_pages() -> None:
    built = many_pages(1000)
    pdf = pikepdf.open(io.BytesIO(built.data))
    try:
        assert len(pdf.pages) == 1000
    finally:
        pdf.close()

    assert len(built.data) < 200_000


def test_pdfplumber_agrees_on_plain_text() -> None:
    data = plain_page(["Hello world"]).data
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        text = pdf.pages[0].extract_text()

    assert text is not None
    assert " ".join(text.split()) == _words(data)
