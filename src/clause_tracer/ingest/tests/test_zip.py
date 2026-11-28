"""The zip checks of the Word reader (S5-M2-T3, S5-M2-T11)."""

import io
import random
import time
import tracemalloc
import warnings
import zipfile
import zlib

import pytest

from clause_tracer.core import InputError, InputTooLargeError, UnreadableFileError
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
    package = open_package(_overlapping_zip())

    with pytest.raises(UnreadableFileError) as raised:
        package.read_part("[Content_Types].xml")

    assert _reason(raised.value) == "zip_overlap"
    assert raised.value.context["part"] == "[Content_Types].xml"


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


def _two_part_zip(document: bytes, method: int = zipfile.ZIP_DEFLATED) -> bytearray:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", b"<Types/>")
        package.writestr(_DOCUMENT, document, compress_type=method)
    return bytearray(buffer.getvalue())


def _second_central(data: bytearray) -> int:
    first = data.find(b"PK\x01\x02")
    return data.find(b"PK\x01\x02", first + 4)


def _declare(data: bytearray, *, size: int, crc: int) -> bytes:
    """Change the declared size and CRC of the second member."""
    central = _second_central(data)
    data[central + 16 : central + 20] = crc.to_bytes(4, "little")
    data[central + 24 : central + 28] = size.to_bytes(4, "little")
    return bytes(data)


@pytest.mark.parametrize("method", [zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA])
def test_other_compression_is_refused(method: int) -> None:
    with pytest.raises(UnreadableFileError) as raised:
        open_package(bytes(_two_part_zip(b"<a/>", method)))

    assert _reason(raised.value) == "zip_invalid"


def test_too_many_members_when_the_count_lies() -> None:
    data = bytearray(many_members_docx(MAX_ZIP_MEMBERS + 1))
    end = data.rfind(b"PK\x05\x06")
    data[end + 8 : end + 12] = (3).to_bytes(2, "little") * 2

    with pytest.raises(UnreadableFileError) as raised:
        open_package(bytes(data))

    assert raised.value.context == {
        "reason": "too_many_members",
        "members": MAX_ZIP_MEMBERS + 1,
        "limit": MAX_ZIP_MEMBERS,
    }


@pytest.mark.parametrize(
    "patches",
    [
        pytest.param([(6, 99)], id="extract-version"),
        pytest.param([(10, 99)], id="compression-method"),
        pytest.param([(9, 0x08), (46, 0xFF)], id="bad-utf8-name"),
    ],
)
def test_raw_zipfile_errors_are_zip_invalid(patches: list[tuple[int, int]]) -> None:
    data = bytearray(build_docx(p(r("Hello"))))
    central = data.find(b"PK\x01\x02")
    for offset, value in patches:
        data[central + offset] = value

    with pytest.raises(UnreadableFileError) as raised:
        open_package(bytes(data))

    assert _reason(raised.value) == "zip_invalid"


@pytest.mark.parametrize(("covered", "reason"), [(4, "zip_invalid"), (5, "size_mismatch")])
def test_a_cut_part_is_refused(covered: int, reason: str) -> None:
    real = b"<a/>" + b" " * 10 + b"<hidden-rest/>"
    data = _declare(_two_part_zip(real), size=4, crc=zlib.crc32(real[:covered]))
    package = open_package(data)

    with pytest.raises(UnreadableFileError) as raised:
        package.read_part(_DOCUMENT)

    assert _reason(raised.value) == reason


def test_a_declared_size_longer_than_the_data_is_refused() -> None:
    data = _declare(_two_part_zip(b"<a/>"), size=40, crc=zlib.crc32(b"<a/>"))
    package = open_package(data)

    with pytest.raises(UnreadableFileError) as raised:
        package.read_part(_DOCUMENT)

    assert _reason(raised.value) == "size_mismatch"


def test_a_deflate_bomb_stays_small() -> None:
    data = _declare(_two_part_zip(bytes(100 * _MIB)), size=100, crc=0)
    package = open_package(data)

    tracemalloc.start()
    with pytest.raises(UnreadableFileError):
        package.read_part(_DOCUMENT)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    assert peak < _MIB


def _stored_copy(data: bytes) -> bytes:
    buffer = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(data)) as source,
        zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as target,
    ):
        for name in source.namelist():
            target.writestr(name, source.read(name))
    return buffer.getvalue()


def _mutated(base: bytes, rng: random.Random) -> bytes:
    """Change one to four bytes, mostly inside the zip records."""
    data = bytearray(base)
    signatures = (b"PK\x01\x02", b"PK\x03\x04", b"PK\x05\x06")
    records = [index for index in range(len(base)) if base.startswith(signatures, index)]
    for _ in range(rng.randint(1, 4)):
        if rng.random() < 0.7:
            position = rng.choice(records) + rng.randrange(4, 46)
        else:
            position = rng.randrange(len(base))
        if position < len(data):
            data[position] = rng.randrange(256)
    return bytes(data)


def test_mutated_packages_raise_only_input_errors() -> None:
    rng = random.Random(1)
    deflated = build_docx(p(r("Hello " * 50)))
    bases = (deflated, _stored_copy(deflated))

    for index in range(4_000):
        data = _mutated(bases[index % 2], rng)
        try:
            package = open_package(data)
            for name in package.names():
                package.read_part(name)
        except InputError:
            pass
