"""The kind of a file comes from its bytes first, then its name (S5-M2-T2)."""

import pytest

from clause_tracer.core import FileKind, OldWordFileError
from clause_tracer.ingest._kind import detect_kind
from clause_tracer.ingest.tests.builders.hostile import ole2_bytes
from clause_tracer.ingest.tests.builders.word import build_docx, p, r


@pytest.mark.parametrize("name", ["a.doc", "a.docx", "a.pdf"])
def test_ole2_raises_old_word(name: str) -> None:
    with pytest.raises(OldWordFileError):
        detect_kind(ole2_bytes(), name)


def test_pdf_signature() -> None:
    assert detect_kind(b"%PDF-1.7\n...", "a.txt") is FileKind.PDF
    assert detect_kind(b"x" * 1000 + b"%PDF-", "a.txt") is FileKind.PDF
    assert detect_kind(b"x" * 1100 + b"%PDF-", "a.pdf") is FileKind.TEXT


def test_zip_is_word() -> None:
    assert detect_kind(build_docx(p(r("Hello"))), "a.txt") is FileKind.WORD
    assert detect_kind(b"PK\x05\x06" + bytes(18), "a.md") is FileKind.WORD


def test_text_and_markdown_by_name() -> None:
    assert detect_kind(b"Hello", "a.md") is FileKind.MARKDOWN
    assert detect_kind(b"Hello", "A.MARKDOWN") is FileKind.MARKDOWN
    assert detect_kind(b"Hello", "a.txt") is FileKind.TEXT
    assert detect_kind(b"Hello", "") is FileKind.TEXT
    assert detect_kind(b"Hello", "a.docx") is FileKind.TEXT


def test_empty_is_text() -> None:
    assert detect_kind(b"", "a.md") is FileKind.MARKDOWN
    assert detect_kind(b"", "a.txt") is FileKind.TEXT
