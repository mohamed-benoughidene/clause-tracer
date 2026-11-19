"""Read text, Markdown and pasted text into a Document (Spec 6.1 step 1).

The decoded text is kept unchanged (D1): a byte-order mark, CRLF line ends
and Markdown symbols all stay. A document without glyphs has empty glyph
fields (system design 3.4).
"""

import hashlib
from typing import Final

from clause_tracer.core import (
    Document,
    EmptyInputError,
    FileKind,
    InputTooLargeError,
    NotUtf8Error,
    SourceFile,
)
from clause_tracer.ingest.limits import MAX_FILE_BYTES, MAX_WORDS, count_words

DOCUMENT_SCHEMA_VERSION: Final[int] = 1


def read_text_file(data: bytes, *, kind: FileKind, name: str) -> Document:
    """Read a text or Markdown file into a document.

    Input:   the file's bytes, its kind (TEXT or MARKDOWN) and its name.
    Output:  a Document whose text is the decoded bytes, character for character.
    Raises:  ValueError for any other kind (a caller bug); InputTooLargeError
             over 20 MB or 50,000 words; NotUtf8Error for bytes that are not
             strict UTF-8; EmptyInputError when the text has no visible character.
    Effects: none. Does not read or write files (I11).
    """

    if kind is not FileKind.TEXT and kind is not FileKind.MARKDOWN:
        raise ValueError("read_text_file reads text and Markdown files only")
    if len(data) > MAX_FILE_BYTES:
        raise InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise NotUtf8Error({"byte_offset": error.start}) from error
    return _build_document(data, text, kind=kind, name=name)


def read_pasted_text(text: str) -> Document:
    """Read pasted text into a document.

    Input:   the pasted text.
    Output:  a Document whose text is the input, character for character.
    Raises:  InputTooLargeError over 20 MB or 50,000 words; NotUtf8Error for a
             lone surrogate; EmptyInputError when the text has no visible character.
    Effects: none. Does not read or write files (I11).
    """

    try:
        data = text.encode("utf-8", errors="strict")
    except UnicodeEncodeError as error:
        raise NotUtf8Error({"char_offset": error.start}) from error
    return _build_document(data, text, kind=FileKind.PASTED, name="")


def _build_document(data: bytes, text: str, *, kind: FileKind, name: str) -> Document:
    """Run the shared checks, then build the document (steps 2, 4, 5 and 6)."""

    if len(data) > MAX_FILE_BYTES:
        raise InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})
    if text.strip() == "":
        raise EmptyInputError()
    words = count_words(text)
    if words > MAX_WORDS:
        raise InputTooLargeError({"words": words, "limit_words": MAX_WORDS})
    return Document(
        schema_version=DOCUMENT_SCHEMA_VERSION,
        source=SourceFile(
            name=name,
            kind=kind,
            sha256=hashlib.sha256(data).hexdigest(),
            size=len(data),
        ),
        text=text,
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )
