"""The entry function read_file (S5-M2-T5)."""

from collections.abc import Callable

import pytest

from clause_tracer.core import (
    FileKind,
    InputError,
    InputTooLargeError,
    OldWordFileError,
    UnreadableFileError,
)
from clause_tracer.ingest import read_file, read_text_file
from clause_tracer.ingest.limits import MAX_FILE_BYTES, MAX_ZIP_MEMBERS
from clause_tracer.ingest.tests.builders.hostile import (
    deep_xml_docx,
    doctype_docx,
    many_members_docx,
    ole2_bytes,
    zip_bomb_docx,
)
from clause_tracer.ingest.tests.builders.word import build_docx, p, r

_MIB = 1024 * 1024


def test_text_goes_to_the_text_reader() -> None:
    data = b"Hello world.\n"

    assert read_file(data, name="a.txt") == read_text_file(data, kind=FileKind.TEXT, name="a.txt")


def test_markdown_by_name() -> None:
    data = b"Hello world.\n"

    assert read_file(data, name="a.md") == read_text_file(data, kind=FileKind.MARKDOWN, name="a.md")


def test_ole2_raises_old_word() -> None:
    with pytest.raises(OldWordFileError):
        read_file(ole2_bytes(), name="a.doc")


def test_word_package_stops_at_the_stub() -> None:
    with pytest.raises(NotImplementedError):
        read_file(build_docx(p(r("Hello"))), name="a.docx")


def test_pdf_stops_at_the_stub() -> None:
    with pytest.raises(NotImplementedError):
        read_file(b"%PDF-1.7\n%%EOF\n", name="a.pdf")


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
        pytest.param(
            lambda: zip_bomb_docx(100 * _MIB),
            InputTooLargeError,
            None,
            id="zip-bomb",
        ),
    ],
)
def test_hostile_word_files_raise_named_errors(
    build: Callable[[], bytes], error_type: type[InputError], reason: str | None
) -> None:
    with pytest.raises(error_type) as raised:
        read_file(build(), name="a.docx")

    if reason is not None:
        assert raised.value.context["reason"] == reason


def test_too_large_file() -> None:
    with pytest.raises(InputTooLargeError) as raised:
        read_file(b"a" * (MAX_FILE_BYTES + 1), name="a.txt")

    assert raised.value.context == {
        "size_bytes": MAX_FILE_BYTES + 1,
        "limit_bytes": MAX_FILE_BYTES,
    }
