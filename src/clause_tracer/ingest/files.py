"""Read a file of any kind into a Document (S5-M2-T5).

The bytes decide the kind first (S5-M2-T2). A Word package is checked
before it is opened, and every XML part is parsed with the hardened
parser (S5-M2-T3 and S5-M2-T4). The Word and PDF readers are stubs until
stage 5 milestones 3 and 4.
"""

from typing import Final

from clause_tracer.core import Document, FileKind, InputTooLargeError
from clause_tracer.ingest._kind import detect_kind
from clause_tracer.ingest._xml import parse_part
from clause_tracer.ingest._zip import open_package
from clause_tracer.ingest.limits import MAX_FILE_BYTES
from clause_tracer.ingest.reading import read_text_file

_XML_PART_SUFFIXES: Final[tuple[str, ...]] = (".xml", ".rels")


def read_file(data: bytes, *, name: str) -> Document:
    """Read a contract file into a document.

    Input:   the file's bytes and its name.
    Output:  a Document for a text or Markdown file; a Word package and a
             PDF are checked and then stop at a stub in this milestone.
    Raises:  InputTooLargeError over 20 MB; OldWordFileError for an OLE2
             file; UnreadableFileError when a Word package or an XML part
             is refused; NotImplementedError while the Word and PDF
             readers are stubs.
    Effects: none. Does not read or write files (I11).
    """

    if len(data) > MAX_FILE_BYTES:
        raise InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})

    kind = detect_kind(data, name)

    if kind is FileKind.TEXT or kind is FileKind.MARKDOWN:
        return read_text_file(data, kind=kind, name=name)

    if kind is FileKind.WORD:
        package = open_package(data)
        for member in package.names():
            if member.endswith(_XML_PART_SUFFIXES):
                parse_part(package.read_part(member))
        raise NotImplementedError("S5-M3")  # Temporary: removed by S5-M3-T8

    raise NotImplementedError("S5-M4")  # Temporary: removed by S5-M4-T8
