"""Build files that are small on disk and expensive to read (S5-M1-T9).

Every function returns bytes and touches no file. The cases come from
ADR 0007 action item 3 and testing strategy section 8.
"""

import io
import zipfile
import zlib
from typing import Final, Literal

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from clause_tracer.ingest.tests.builders.word import build_docx, p, r

_LOCAL = b"PK\x03\x04"
_CENTRAL = b"PK\x01\x02"
_REL_TYPE: Final[str] = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
_DOCUMENT = "word/document.xml"
_DATE_TIME: Final[tuple[int, int, int, int, int, int]] = (1980, 1, 1, 0, 0, 0)


def _rezip(members: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, data)
    return buffer.getvalue()


def _rewrite(data: bytes, name: str, replacement: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        members = [
            (member, replacement if member == name else package.read(member))
            for member in package.namelist()
        ]
    return _rezip(members)


def _document_xml(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        return package.read(_DOCUMENT).decode()


def _with_doctype(data: bytes, doctype: str) -> bytes:
    text = _document_xml(data)
    head, rest = text.split("?>\n", 1)
    return _rewrite(data, _DOCUMENT, f"{head}?>\n{doctype}{rest}".encode())


def _find(data: bytes, signature: bytes, name_start: int, length_start: int, name: str) -> int:
    encoded = name.encode()
    start = 0
    while True:
        index = data.find(signature, start)
        if index < 0:
            raise ValueError(f"ingest: {name} not found")
        length = int.from_bytes(data[index + length_start : index + length_start + 2], "little")
        if data[index + name_start : index + name_start + length] == encoded:
            return index
        start = index + 1


def _patch(data: bytes, offset: int, value: int) -> bytes:
    return data[:offset] + value.to_bytes(4, "little") + data[offset + 4 :]


def zip_bomb_docx(expanded_bytes: int) -> bytes:
    """A valid Word part of `expanded_bytes`, deflated."""
    unit = p(r("A" * 100))
    count = expanded_bytes // len(unit)
    body = unit * count
    leftover = expanded_bytes - len(body)
    overhead = len(p(r("")))
    if leftover > overhead:
        body += p(r("B" * (leftover - overhead)))
    return build_docx(body)


def many_members_docx(count: int) -> bytes:
    """A Word package with `count` members in all."""
    extra = {f"word/media/m{index}.bin": b"" for index in range(max(0, count - 4))}
    return build_docx(p(r("Hello")), extra_parts=extra)


def false_declared_size_docx(declared: int) -> bytes:
    """A package whose central directory overstates the part's size."""
    data = build_docx(p(r("Hello")))
    central = _find(data, _CENTRAL, 46, 28, _DOCUMENT)
    return _patch(data, central + 24, declared)


def entity_docx(kind: Literal["internal", "external_file", "external_url", "parameter"]) -> bytes:
    """A package whose DOCTYPE declares and uses one entity of that kind."""
    declarations = {
        "internal": '<!ENTITY e "EXPANDED">',
        "external_file": '<!ENTITY e SYSTEM "file:///etc/passwd">',
        "external_url": '<!ENTITY e SYSTEM "http://127.0.0.1:9/x">',
        "parameter": '<!ENTITY % e SYSTEM "http://127.0.0.1:9/x">%e;',
    }
    body = r("x") if kind == "parameter" else r("&e;")
    data = build_docx(p(body))
    return _with_doctype(data, f"<!DOCTYPE w:document [{declarations[kind]}]>")


def doctype_docx() -> bytes:
    """A package with a DOCTYPE and no entity."""
    return _with_doctype(build_docx(p(r("Hello"))), "<!DOCTYPE w:document>")


def external_rel_docx() -> bytes:
    """A package whose relationships point at the network, externally."""
    target = "http://127.0.0.1:9/x"
    relationships = tuple(
        f'<Relationship Id="{rel_id}" Type="{_REL_TYPE}{kind}" '
        f'Target="{target}" TargetMode="External"/>'
        for rel_id, kind in (
            ("rIdTemplate", "attachedTemplate"),
            ("rIdImage", "image"),
            ("rIdLink", "hyperlink"),
        )
    )
    return build_docx(p(r("Hello")), document_rels=relationships)


def deep_xml_docx(depth: int) -> bytes:
    """A body of `depth` nested w:sdt elements and no paragraph."""
    return build_docx("<w:sdt>" * depth + "</w:sdt>" * depth)


def huge_text_node_docx(size: int) -> bytes:
    """One text node of `size` characters."""
    return build_docx(p(r("a" * size)))


def big_xml_docx(size: int) -> bytes:
    """A legal part of about `size` bytes made of short paragraphs."""
    unit = p(r("A"))
    return build_docx(unit * (size // len(unit)))


def ole2_bytes() -> bytes:
    """The OLE2 signature, as an old Word file starts."""
    return bytes.fromhex("D0CF11E0A1B11AE1") + bytes(504)


def not_a_zip() -> bytes:
    """Bytes that start like a zip and are not one."""
    return b"PK\x03\x04" + bytes(range(96))


def lying_low_docx() -> bytes:
    """A package whose sizes say 10 bytes while the part is 1 MiB."""
    data = build_docx(p(r("a" * (1024 * 1024))))
    local = _find(data, _LOCAL, 30, 26, _DOCUMENT)
    central = _find(data, _CENTRAL, 46, 28, _DOCUMENT)
    data = _patch(data, local + 22, 10)
    return _patch(data, central + 24, 10)


def _flat_flate(pixels: int) -> bytes:
    """Deflate `pixels` zero bytes without holding them in memory."""
    compressor = zlib.compressobj(9)
    chunk = bytes(1 << 20)
    parts: list[bytes] = []
    remaining = pixels
    while remaining:
        take = min(remaining, len(chunk))
        parts.append(compressor.compress(chunk[:take]))
        remaining -= take
    parts.append(compressor.flush())
    return b"".join(parts)


def pdf_many_pages(count: int) -> bytes:
    """A PDF of `count` pages that share one page object."""
    pdf = pikepdf.new()
    page = pdf.add_blank_page(page_size=(612, 792))
    pages = pdf.Root.Pages
    pages.Kids = pikepdf.Array([page.obj] * count)
    pages.Count = count
    output = io.BytesIO()
    pdf.save(output, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    pdf.close()
    return output.getvalue()


def pdf_image_bomb(width: int, height: int, pages: int = 1) -> bytes:
    """A PDF whose pages draw one flat grey Flate image of width by height."""
    pdf = pikepdf.new()
    image = pdf.make_stream(_flat_flate(width * height))
    image.Type = pikepdf.Name.XObject
    image.Subtype = pikepdf.Name.Image
    image.Width = width
    image.Height = height
    image.ColorSpace = pikepdf.Name.DeviceGray
    image.BitsPerComponent = 8
    image.Filter = pikepdf.Name.FlateDecode
    for _ in range(pages):
        page = pdf.add_blank_page(page_size=(612, 792))
        page.Contents = pdf.make_stream(f"q {width} 0 0 {height} 0 0 cm /Im0 Do Q".encode())
        page.Resources = pikepdf.Dictionary(XObject=pikepdf.Dictionary(Im0=image))
    output = io.BytesIO()
    pdf.save(output, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    pdf.close()
    return output.getvalue()


def pdf_dense_text(pages: int, chars_per_page: int) -> bytes:
    """A PDF with `pages` pages of small characters."""
    lines = max(1, chars_per_page // 100)
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=(612, 792), invariant=1)
    canvas.setFont("Helvetica", 5)
    for _ in range(pages):
        for line in range(lines):
            canvas.drawString(10, 780 - 5 * line, "x" * 100)
        canvas.showPage()
    canvas.save()
    return buffer.getvalue()
