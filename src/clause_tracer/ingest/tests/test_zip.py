"""The zip checks of the Word reader (S5-M2-T3)."""

import io
import time
import warnings
import zipfile

import pytest

from clause_tracer.core import InputTooLargeError, UnreadableFileError
from clause_tracer.ingest._zip import open_package
from clause_tracer.ingest.limits import (
    MAX_PARSED_TOTAL_BYTES,
    MAX_XML_PART_BYTES,
    MAX_ZIP_MEMBERS,
)
from clause_tracer.ingest.tests.builders.hostile import (
    false_declared_size_docx,
    lying_low_docx,
    many_members_docx,
    not_a_zip,
    zip_bomb_docx,
)
from clause_tracer.ingest.tests.builders.word import build_docx, p, r

_DOCUMENT = "word/document.xml"
_MIB = 1024 * 1024


def _reason(error: UnreadableFileError) -> str:
    return str(error.context["reason"])


def _zip_of(members: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        for name, data in members:
            package.writestr(name, data)
    return buffer.getvalue()


def test_opens_a_word_package() -> None:
    data = build_docx(p(r("Hello")))

    package = open_package(data)

    assert package.names()[0] == "[Content_Types].xml"
    assert package.has(_DOCUMENT)
    with zipfile.ZipFile(io.BytesIO(data)) as original:
        assert package.read_part(_DOCUMENT) == original.read(_DOCUMENT)


def test_not_a_zip() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        open_package(not_a_zip())

    assert _reason(raised.value) == "zip_invalid"


def test_too_many_members() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        open_package(many_members_docx(MAX_ZIP_MEMBERS + 1))

    assert _reason(raised.value) == "too_many_members"
    assert raised.value.context["members"] == MAX_ZIP_MEMBERS + 1
    assert raised.value.context["limit"] == MAX_ZIP_MEMBERS

    assert len(open_package(many_members_docx(MAX_ZIP_MEMBERS)).names()) == MAX_ZIP_MEMBERS


def test_declared_size_over_cap() -> None:
    package = open_package(false_declared_size_docx(MAX_XML_PART_BYTES + 1))

    with pytest.raises(InputTooLargeError) as raised:
        package.read_part(_DOCUMENT)

    assert raised.value.context["part"] == _DOCUMENT
    assert raised.value.context["limit_bytes"] == MAX_XML_PART_BYTES


def test_zip_bomb_is_refused_before_inflating() -> None:
    package = open_package(zip_bomb_docx(100 * _MIB))

    started = time.monotonic()
    with pytest.raises(InputTooLargeError) as raised:
        package.read_part(_DOCUMENT)
    elapsed = time.monotonic() - started

    assert raised.value.context["part"] == _DOCUMENT
    assert raised.value.context["limit_bytes"] == MAX_XML_PART_BYTES
    assert elapsed < 1.0


def test_lying_low_is_refused() -> None:
    package = open_package(lying_low_docx())

    with pytest.raises(UnreadableFileError) as raised:
        package.read_part(_DOCUMENT)

    assert _reason(raised.value) in {"size_mismatch", "zip_invalid"}


def test_duplicate_member() -> None:
    buffer = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with zipfile.ZipFile(buffer, "w") as package:
            package.writestr("[Content_Types].xml", b"<Types/>")
            package.writestr(_DOCUMENT, b"<w:document/>")
            package.writestr(_DOCUMENT, b"<w:document/>")

    with pytest.raises(UnreadableFileError) as raised:
        open_package(buffer.getvalue())

    assert _reason(raised.value) == "duplicate_member"


def test_missing_document_part() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        open_package(_zip_of([("a.txt", b"Hello")]))

    assert _reason(raised.value) == "not_a_word_file"


def test_total_cap() -> None:
    part = b"a" * (30 * _MIB)
    package = open_package(
        _zip_of(
            [
                ("[Content_Types].xml", b"<Types/>"),
                (_DOCUMENT, part),
                ("word/other.xml", part),
            ]
        )
    )

    assert len(package.read_part(_DOCUMENT)) == 30 * _MIB

    with pytest.raises(InputTooLargeError) as raised:
        package.read_part("word/other.xml")

    assert raised.value.context["limit_bytes"] == MAX_PARSED_TOTAL_BYTES


def _overlapping_zip() -> bytes:
    """Two central entries that point at the same local header."""
    data = bytearray(_zip_of([("[Content_Types].xml", b"<Types/>"), (_DOCUMENT, b"<w:document/>")]))
    local = data.find(b"PK\x03\x04")
    first_central = data.find(b"PK\x01\x02")
    second_central = data.find(b"PK\x01\x02", first_central + 4)
    offset = second_central + 42
    data[offset : offset + 4] = local.to_bytes(4, "little")
    return bytes(data)


def test_overlap_is_an_error() -> None:
    try:
        open_package(_overlapping_zip())
    except UnreadableFileError as error:
        assert _reason(error) == "zip_overlap"
    else:
        pytest.skip("this CPython does not warn about overlapping members")


def test_read_part_unknown_name_raises_value_error() -> None:
    package = open_package(build_docx(p(r("Hello"))))

    with pytest.raises(ValueError):
        package.read_part("word/missing.xml")


def test_zip64_is_refused() -> None:
    data = bytearray(build_docx(p(r("Hello"))))
    end = data.rfind(b"PK\x05\x06")
    data[end + 10 : end + 12] = (65_535).to_bytes(2, "little")

    with pytest.raises(UnreadableFileError) as raised:
        open_package(bytes(data))

    assert _reason(raised.value) == "zip64"


def test_encrypted_member_is_refused() -> None:
    data = bytearray(build_docx(p(r("Hello"))))
    start = 0
    while (central := data.find(b"PK\x01\x02", start)) >= 0:
        data[central + 8] |= 0x1
        start = central + 4

    with pytest.raises(UnreadableFileError) as raised:
        open_package(bytes(data))

    assert _reason(raised.value) == "zip_encrypted"


def test_corrupt_central_directory_is_refused() -> None:
    data = (
        b"PK\x05\x06" + bytes(6) + (1).to_bytes(2, "little") + (1).to_bytes(2, "little") + bytes(8)
    )

    with pytest.raises(UnreadableFileError) as raised:
        open_package(data)

    assert _reason(raised.value) == "zip_invalid"
