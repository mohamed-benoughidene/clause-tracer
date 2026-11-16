"""The document shapes (system design 3.4 and 4.2).

Offsets are half-open, count code points, and point into Document.text.
The raw file bytes are kept unchanged (D1). A document without glyphs
(text, Markdown, pasted text, Word) has glyphs == (), char_map == ()
and pages == () (decided 14 Nov 2026).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class PageBox:
    """PDF points, top-left origin, one coordinate system (ADR 0007)."""

    page: int
    x0: float
    top: float
    x1: float
    bottom: float


@dataclass(frozen=True, slots=True, kw_only=True)
class Page:
    """One page of the document; pages are numbered from 1."""

    number: int
    width: float
    height: float


@dataclass(frozen=True, slots=True, kw_only=True)
class Glyph:
    """One drawn character; page is a Page.number and equals box.page."""

    page: int
    box: PageBox
