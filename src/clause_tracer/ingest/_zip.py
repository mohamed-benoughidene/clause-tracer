"""The zip checks of the Word reader (S5-M2-T3, S5-M2-T11).

This file imports only the standard library. It refuses a package before
`zipfile` opens it when the count in the end record is too high. That count
can be false, so the names are counted again after the open. A member that
is not stored or deflated is refused, and media is never read. A part's
declared size is checked before the part is inflated.
"""

import copy
import io
import warnings
import zipfile
import zlib
from typing import Final

from clause_tracer.core import InputTooLargeError, UnreadableFileError
from clause_tracer.ingest.limits import (
    MAX_PARSED_TOTAL_BYTES,
    MAX_XML_PART_BYTES,
    MAX_ZIP_MEMBERS,
)

_EOCD_SIGNATURE: Final[bytes] = b"PK\x05\x06"
_EOCD_SEARCH_BYTES: Final[int] = 65_557
# The end record is 22 bytes, followed by a comment of up to 65,535 bytes.

_EOCD_ENTRIES_OFFSET: Final[int] = 10
_ZIP64_ENTRIES: Final[int] = 65_535
_ENCRYPTED_FLAG: Final[int] = 0x1

_ALLOWED_COMPRESSION: Final[frozenset[int]] = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})
# Word writes only these two. With any other, one read step is not bounded by the declared size.

_ZIP_ERRORS: Final[tuple[type[Exception], ...]] = (
    zipfile.BadZipFile,
    zlib.error,
    EOFError,
    NotImplementedError,
    OSError,
    ValueError,
)
# What zipfile raises for a damaged or hostile package. MemoryError is never in this list.

_REQUIRED_PARTS: Final[tuple[str, ...]] = (
    "[Content_Types].xml",
    "word/document.xml",
)


class WordPackage:
    """The members of a Word package, opened once and read part by part."""

    __slots__ = ("_zip", "_infos", "_parsed_bytes")

    def __init__(self, *, package: zipfile.ZipFile, infos: dict[str, zipfile.ZipInfo]) -> None:
        self._zip = package
        self._infos = infos
        self._parsed_bytes = 0

    def names(self) -> tuple[str, ...]:
        """Return the member names in file order."""
        return tuple(self._zip.namelist())

    def has(self, name: str) -> bool:
        """Return whether the package holds this member."""
        return name in self._infos

    def read_part(self, name: str) -> bytes:
        """Return one member's bytes, inside the size caps.

        Input:   a member name.
        Output:  the member's bytes.
        Raises:  ValueError when the member does not exist (a caller bug);
                 InputTooLargeError when the part or the running total is
                 over its cap; UnreadableFileError when the member is
                 corrupt, overlaps another member, or its real size differs
                 from the declared size.
        Effects: none.
        """

        info = self._infos.get(name)
        if info is None:
            raise ValueError("ingest: no such part")

        is_part_over_cap = info.file_size > MAX_XML_PART_BYTES
        if is_part_over_cap:
            raise InputTooLargeError(
                {"part": name, "size_bytes": info.file_size, "limit_bytes": MAX_XML_PART_BYTES}
            )

        is_total_over_cap = self._parsed_bytes + info.file_size > MAX_PARSED_TOTAL_BYTES
        if is_total_over_cap:
            raise InputTooLargeError({"part": name, "limit_bytes": MAX_PARSED_TOTAL_BYTES})

        # zipfile stops at the declared size: one extra byte lets a longer part show.
        probe = copy.copy(info)
        probe.file_size = info.file_size + 1

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            try:
                with self._zip.open(probe) as stream:
                    data = stream.read(info.file_size + 1)
            except _ZIP_ERRORS:
                raise UnreadableFileError({"reason": "zip_invalid"}) from None
            except UserWarning:
                raise UnreadableFileError({"reason": "zip_overlap", "part": name}) from None

        is_size_mismatch = len(data) != info.file_size
        if is_size_mismatch:
            raise UnreadableFileError({"reason": "size_mismatch", "part": name})

        self._parsed_bytes += len(data)
        return data


def open_package(data: bytes) -> WordPackage:
    """Open a Word package after checking its member count and names.

    Input:   the bytes of a .docx file.
    Output:  a WordPackage.
    Raises:  UnreadableFileError with a reason: zip_invalid, zip64,
             too_many_members, duplicate_member, zip_encrypted or
             not_a_word_file.
    Effects: none.
    """

    entries = _central_directory_entries(data)

    is_zip64 = entries == _ZIP64_ENTRIES
    if is_zip64:
        raise UnreadableFileError({"reason": "zip64"})

    is_too_many = entries > MAX_ZIP_MEMBERS
    if is_too_many:
        raise UnreadableFileError(
            {"reason": "too_many_members", "members": entries, "limit": MAX_ZIP_MEMBERS}
        )

    try:
        package = zipfile.ZipFile(io.BytesIO(data))
    except _ZIP_ERRORS:
        raise UnreadableFileError({"reason": "zip_invalid"}) from None

    names = package.namelist()
    has_too_many_names = len(names) > MAX_ZIP_MEMBERS
    if has_too_many_names:
        raise UnreadableFileError(
            {"reason": "too_many_members", "members": len(names), "limit": MAX_ZIP_MEMBERS}
        )

    has_duplicate = len(names) != len(set(names))
    if has_duplicate:
        raise UnreadableFileError({"reason": "duplicate_member"})

    infos: dict[str, zipfile.ZipInfo] = {}
    for info in package.infolist():
        is_encrypted = bool(info.flag_bits & _ENCRYPTED_FLAG)
        if is_encrypted:
            raise UnreadableFileError({"reason": "zip_encrypted"})
        is_other_compression = info.compress_type not in _ALLOWED_COMPRESSION
        if is_other_compression:
            raise UnreadableFileError({"reason": "zip_invalid"})
        infos[info.filename] = info

    has_required_parts = all(part in infos for part in _REQUIRED_PARTS)
    if not has_required_parts:
        raise UnreadableFileError({"reason": "not_a_word_file"})

    return WordPackage(package=package, infos=infos)


def _central_directory_entries(data: bytes) -> int:
    """Return the member count from the end-of-central-directory record."""

    tail = data[-_EOCD_SEARCH_BYTES:]
    index = tail.rfind(_EOCD_SIGNATURE)
    if index < 0:
        raise UnreadableFileError({"reason": "zip_invalid"})

    start = index + _EOCD_ENTRIES_OFFSET
    return int.from_bytes(tail[start : start + 2], "little")
