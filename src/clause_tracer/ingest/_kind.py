"""The kind of a file comes from its bytes first, then its name (S5-M2-T2)."""

from typing import Final

from clause_tracer.core import FileKind, OldWordFileError

OLE2_SIGNATURE: Final[bytes] = bytes.fromhex("D0CF11E0A1B11AE1")
# An old .doc and a password-protected .docx share this signature (question 17).

PDF_SIGNATURE: Final[bytes] = b"%PDF-"
PDF_SCAN_BYTES: Final[int] = 1_024
# A PDF reader may allow leading bytes before the header (Spec 9).

ZIP_SIGNATURES: Final[tuple[bytes, ...]] = (b"PK\x03\x04", b"PK\x05\x06")
# A local header, or an empty archive's end-of-central-directory record.

MARKDOWN_SUFFIXES: Final[tuple[str, ...]] = (".md", ".markdown")


def detect_kind(data: bytes, name: str) -> FileKind:
    """Return the kind of a file from its first bytes, then its name.

    Input:   the file's bytes and its name.
    Output:  PDF, WORD, MARKDOWN or TEXT.
    Raises:  OldWordFileError for an OLE2 file: an old .doc, or a
             password-protected .docx. The name is not read for this rule.
    Effects: none.
    """

    is_ole2 = data[: len(OLE2_SIGNATURE)] == OLE2_SIGNATURE
    if is_ole2:
        raise OldWordFileError()

    is_pdf = PDF_SIGNATURE in data[:PDF_SCAN_BYTES]
    if is_pdf:
        return FileKind.PDF

    is_zip = data[:4] in ZIP_SIGNATURES
    if is_zip:
        return FileKind.WORD

    lower_name = name.lower()
    is_markdown = lower_name.endswith(MARKDOWN_SUFFIXES)
    return FileKind.MARKDOWN if is_markdown else FileKind.TEXT
