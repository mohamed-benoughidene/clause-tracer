"""Tests for reading text, Markdown and pasted text into a Document."""

import hashlib

import pytest

from clause_tracer.core import (
    Document,
    EmptyInputError,
    FileKind,
    InputTooLargeError,
    NotUtf8Error,
)
from clause_tracer.ingest import read_text_file
from clause_tracer.ingest.limits import MAX_FILE_BYTES


def test_text_is_the_decoded_bytes() -> None:
    text = "1. Pay\r\n**now** ﬁne\n"
    data = text.encode()

    document = read_text_file(data, kind=FileKind.MARKDOWN, name="a.md")

    assert document.text == text
    assert document.source.kind is FileKind.MARKDOWN
    assert document.source.name == "a.md"
    assert document.source.size == len(data)
    assert document.source.sha256 == hashlib.sha256(data).hexdigest()


def test_byte_order_mark_is_kept() -> None:
    document = read_text_file(b"\xef\xbb\xbfHello", kind=FileKind.TEXT, name="a.txt")

    assert document.text == "\ufeffHello"


def test_document_has_no_glyphs() -> None:
    document = read_text_file(b"1. Pay now.", kind=FileKind.TEXT, name="a.txt")

    assert document.glyphs == ()
    assert document.char_map == ()
    assert document.pages == ()
    assert document.furniture == ()
    assert document.hidden == ()
    assert document.undecodable == ()
    assert document.tracked_changes == ()
    assert document.warnings == ()
    assert document.schema_version == 1


def test_not_utf8_raises() -> None:
    with pytest.raises(NotUtf8Error) as raised:
        read_text_file(b"caf\xe9 bar", kind=FileKind.TEXT, name="a.txt")

    assert raised.value.context["byte_offset"] == 3


def test_file_over_the_byte_limit_raises() -> None:
    data = b"a" * (MAX_FILE_BYTES + 1)

    with pytest.raises(InputTooLargeError) as raised:
        read_text_file(data, kind=FileKind.TEXT, name="a.txt")

    assert raised.value.context == {
        "size_bytes": MAX_FILE_BYTES + 1,
        "limit_bytes": MAX_FILE_BYTES,
    }


def test_file_at_the_byte_limit_is_checked_for_words_next() -> None:
    document = read_text_file(b"a" * MAX_FILE_BYTES, kind=FileKind.TEXT, name="a.txt")

    assert isinstance(document, Document)


def test_over_the_word_limit_raises() -> None:
    data = ("a " * 50_001).encode()

    with pytest.raises(InputTooLargeError) as raised:
        read_text_file(data, kind=FileKind.TEXT, name="a.txt")

    assert raised.value.context == {"words": 50_001, "limit_words": 50_000}


def test_at_the_word_limit_passes() -> None:
    document = read_text_file(("a " * 50_000).encode(), kind=FileKind.TEXT, name="a.txt")

    assert isinstance(document, Document)


def test_empty_file_raises() -> None:
    with pytest.raises(EmptyInputError):
        read_text_file(b"", kind=FileKind.TEXT, name="a.txt")


def test_blank_file_raises() -> None:
    with pytest.raises(EmptyInputError):
        read_text_file(b" \n\t\r\n", kind=FileKind.TEXT, name="a.txt")


def test_wrong_kind_is_a_bug() -> None:
    with pytest.raises(ValueError):
        read_text_file(b"1. Pay now.", kind=FileKind.PDF, name="a.pdf")
