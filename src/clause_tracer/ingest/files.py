"""Read a file of any kind into a Document (S5-M2-T5, S5-M3-T8).

The bytes decide the kind first (S5-M2-T2). A Word package goes to the
Word reader, which checks it before it opens it. The PDF reader is a stub
until stage 5 milestone 4.
"""

from clause_tracer.core import Document, FileKind, InputTooLargeError
from clause_tracer.ingest._kind import detect_kind
from clause_tracer.ingest.limits import MAX_FILE_BYTES
from clause_tracer.ingest.reading import read_text_file
from clause_tracer.ingest.word import read_word_file


def read_file(data: bytes, *, name: str) -> Document:
    """Read a contract file into a document.

    Input:   the file's bytes and its name.
    Output:  a Document for a text or Markdown file, or for a Word file.
    Raises:  InputTooLargeError over 20 MB; OldWordFileError for an OLE2
             file; UnreadableFileError when a Word package or an XML part
             is refused; NotImplementedError while the PDF reader is a
             stub.
    Effects: none. Does not read or write files (I11).
    """

    if len(data) > MAX_FILE_BYTES:
        raise InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})

    kind = detect_kind(data, name)

    if kind is FileKind.TEXT or kind is FileKind.MARKDOWN:
        return read_text_file(data, kind=kind, name=name)

    if kind is FileKind.WORD:
        return read_word_file(data, name=name)

    raise NotImplementedError("S5-M4")  # Temporary: removed by S5-M4-T8
