"""The test-only tools build and read the files the tests need (S5-M1-T4)."""

import io

import pdfplumber
import pypdfium2
from PIL import Image
from reportlab.pdfgen.canvas import Canvas


def _pdf_bytes() -> bytes:
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=(200, 200), invariant=1)
    canvas.setFont("Helvetica", 12)
    canvas.drawString(20, 100, "Hello")
    canvas.showPage()
    canvas.save()
    return buffer.getvalue()


def test_reportlab_pdf_is_readable() -> None:
    data = _pdf_bytes()
    document = pypdfium2.PdfDocument(data)
    try:
        text = document[0].get_textpage().get_text_range()
    finally:
        document.close()

    assert "Hello" in text


def test_pdfplumber_reads_it() -> None:
    with pdfplumber.open(io.BytesIO(_pdf_bytes())) as pdf:
        text = pdf.pages[0].extract_text()

    assert text is not None
    assert "Hello" in text


def test_pillow_writes_a_png() -> None:
    image = Image.new("L", (4, 4), 255)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    with Image.open(buffer) as loaded:
        assert loaded.size == (4, 4)
        assert loaded.getpixel((0, 0)) == 255
