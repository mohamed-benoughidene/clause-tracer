"""The pinned PDFium build has every function the stage uses (S5-M1-T10)."""

import ctypes
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Final

import pypdfium2.raw as raw
import pytest

from clause_tracer.ingest.tests.builders.pdf import (
    invisible_mode_page,
    tiny_text_page,
    white_text_page,
)

HIDDEN_TEXT_FUNCTIONS: Final[tuple[str, ...]] = (
    "FPDFText_GetUnicode",
    "FPDFText_GetCharBox",
    "FPDFText_GetFontSize",
    "FPDFText_GetFillColor",
    "FPDFText_GetMatrix",
    "FPDFText_IsGenerated",
    "FPDFText_IsHyphen",
    "FPDFText_HasUnicodeMapError",
    "FPDFTextObj_GetTextRenderMode",
)

FURTHER_FUNCTIONS: Final[tuple[str, ...]] = (
    "FPDFText_CountChars",
    "FPDFText_GetTextObject",
    "FPDFText_GetLooseCharBox",
    "FPDF_GetPageBoundingBox",
    "FPDFPage_GetRotation",
    "FPDFPage_CountObjects",
    "FPDFPageObj_GetType",
    "FPDFFormObj_CountObjects",
    "FPDF_GetLastError",
    "FPDF_GetDocPermissions",
    "FPDF_GetPageCount",
    "FPDF_LoadMemDocument64",
)


@contextmanager
def _textpage(data: bytes) -> Iterator[Any]:
    buffer = ctypes.create_string_buffer(data, len(data))
    document = raw.FPDF_LoadMemDocument64(buffer, len(data), None)
    assert document
    page = raw.FPDF_LoadPage(document, 0)
    textpage = raw.FPDFText_LoadPage(page)
    try:
        yield textpage
    finally:
        raw.FPDFText_ClosePage(textpage)
        raw.FPDF_ClosePage(page)
        raw.FPDF_CloseDocument(document)


def _fill_colour(textpage: Any, index: int) -> tuple[int, int, int, int] | None:
    red, green, blue, alpha = (ctypes.c_uint() for _ in range(4))
    loaded = raw.FPDFText_GetFillColor(
        textpage,
        index,
        ctypes.byref(red),
        ctypes.byref(green),
        ctypes.byref(blue),
        ctypes.byref(alpha),
    )
    if not loaded:
        return None
    return red.value, green.value, blue.value, alpha.value


@pytest.mark.parametrize("name", HIDDEN_TEXT_FUNCTIONS + FURTHER_FUNCTIONS)
def test_functions_exist(name: str) -> None:
    assert hasattr(raw, name)


def test_error_codes() -> None:
    assert raw.FPDF_ERR_PASSWORD == 4
    assert raw.FPDF_ERR_SECURITY == 5


def test_readings_tell_the_cases_apart() -> None:
    with _textpage(white_text_page().data) as textpage:
        white = [
            index
            for index in range(raw.FPDFText_CountChars(textpage))
            if _fill_colour(textpage, index) == (255, 255, 255, 255)
        ]
        assert white
        assert chr(raw.FPDFText_GetUnicode(textpage, white[0])) == "W"

    with _textpage(tiny_text_page().data) as textpage:
        assert chr(raw.FPDFText_GetUnicode(textpage, 0)) == "T"
        assert raw.FPDFText_GetFontSize(textpage, 0) == pytest.approx(1.0)

    with _textpage(invisible_mode_page().data) as textpage:
        text_object = raw.FPDFText_GetTextObject(textpage, 0)
        assert text_object
        assert raw.FPDFTextObj_GetTextRenderMode(text_object) == 3
