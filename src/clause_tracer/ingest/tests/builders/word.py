"""Build Word packages from XML strings, so a test states what it relies on.

The same input always gives the same bytes: every member gets a fixed
timestamp (S5-M1-T7).
"""

import io
import zipfile
from collections.abc import Mapping
from typing import Final
from xml.sax.saxutils import escape

W_NS: Final[str] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS: Final[str] = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_REL_NS: Final[str] = "http://schemas.openxmlformats.org/package/2006/relationships"
_CT_NS: Final[str] = "http://schemas.openxmlformats.org/package/2006/content-types"
_REL_TYPE: Final[str] = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
_DATE: Final[str] = "2026-01-01T00:00:00Z"
_DOCUMENT_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
)
_STYLES_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"
)
_NUMBERING_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"
)
_COMMENTS_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
)
_FOOTNOTES_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"
)
_ENDNOTES_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml"
)
_SETTINGS_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"
)
_HEADER_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"
)
_FOOTER_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
)

_PART_ORDER: Final[tuple[tuple[str, str, str, str, str], ...]] = (
    ("styles", "styles.xml", "styles", _STYLES_TYPE, "styles"),
    ("numbering", "numbering.xml", "numbering", _NUMBERING_TYPE, "numbering"),
    ("comments", "comments.xml", "comments", _COMMENTS_TYPE, "comments"),
    ("footnotes", "footnotes.xml", "footnotes", _FOOTNOTES_TYPE, "footnotes"),
    ("endnotes", "endnotes.xml", "endnotes", _ENDNOTES_TYPE, "endnotes"),
    ("settings", "settings.xml", "settings", _SETTINGS_TYPE, "settings"),
)


def _attr(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def _xml(root: str, inner: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<w:{root} xmlns:w="{W_NS}" xmlns:r="{R_NS}">{inner}</w:{root}>'
    )


def _relationship(rel_id: str, kind: str, target: str) -> str:
    return f'<Relationship Id="{rel_id}" Type="{_REL_TYPE}{kind}" Target="{_attr(target)}"/>'


def _content_types(parts: tuple[tuple[str, str], ...]) -> str:
    overrides = "".join(
        f'<Override PartName="/{name}" ContentType="{content_type}"/>'
        for name, content_type in parts
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Types xmlns="{_CT_NS}">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'<Override PartName="/word/document.xml" ContentType="{_DOCUMENT_TYPE}"/>'
        f"{overrides}</Types>"
    )


def _package_rels() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Relationships xmlns="{_REL_NS}">'
        f"{_relationship('rId1', 'officeDocument', 'word/document.xml')}"
        "</Relationships>"
    )


def _document_rels(document_rels: tuple[str, ...], parts: tuple[tuple[str, str], ...]) -> str:
    built = "".join(
        _relationship(f"rId{index}", kind, target)
        for index, (kind, target) in enumerate(parts, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<Relationships xmlns="{_REL_NS}">{built}{"".join(document_rels)}</Relationships>'
    )


def build_docx(
    body: str,
    *,
    styles: str | None = None,
    numbering: str | None = None,
    comments: str | None = None,
    footnotes: str | None = None,
    endnotes: str | None = None,
    headers: Mapping[str, str] | None = None,
    footers: Mapping[str, str] | None = None,
    settings: str | None = None,
    document_rels: tuple[str, ...] = (),
    extra_parts: Mapping[str, bytes] | None = None,
) -> bytes:
    """Return a Word package with the given body and parts."""
    given = {
        "styles": styles,
        "numbering": numbering,
        "comments": comments,
        "footnotes": footnotes,
        "endnotes": endnotes,
        "settings": settings,
    }
    parts: list[tuple[str, str, str, str, str]] = []
    for key, file_name, root, content_type, kind in _PART_ORDER:
        inner = given[key]
        if inner is not None:
            parts.append((f"word/{file_name}", root, inner, content_type, kind))
    for name, inner in (headers or {}).items():
        parts.append((f"word/{name}", "hdr", inner, _HEADER_TYPE, "header"))
    for name, inner in (footers or {}).items():
        parts.append((f"word/{name}", "ftr", inner, _FOOTER_TYPE, "footer"))

    rels = tuple(
        (kind, name.removeprefix("word/")) for name, _root, _inner, _content_type, kind in parts
    )
    content_parts = tuple(
        (name, content_type) for name, _root, _inner, content_type, _kind in parts
    )

    members: list[tuple[str, bytes]] = [
        ("[Content_Types].xml", _content_types(content_parts).encode()),
        ("_rels/.rels", _package_rels().encode()),
        ("word/document.xml", _xml("document", f"<w:body>{body}</w:body>").encode()),
        (
            "word/_rels/document.xml.rels",
            _document_rels(document_rels, rels).encode(),
        ),
    ]
    for name, root, inner, _content_type, _kind in parts:
        members.append((name, _xml(root, inner).encode()))
    for name, data in (extra_parts or {}).items():
        members.append((name, data))

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, data)
    return buffer.getvalue()


def p(*runs: str, style: str | None = None, num: tuple[int, int] | None = None) -> str:
    """Return a paragraph. `num` is (num_id, level)."""
    properties = ""
    if style is not None:
        properties += f'<w:pStyle w:val="{_attr(style)}"/>'
    if num is not None:
        num_id, level = num
        properties += f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="{num_id}"/></w:numPr>'
    prefix = f"<w:pPr>{properties}</w:pPr>" if properties else ""
    return f"<w:p>{prefix}{''.join(runs)}</w:p>"


def r(
    text: str,
    *,
    hidden: bool = False,
    color: str | None = None,
    size_half_points: int | None = None,
    shading: str | None = None,
    style: str | None = None,
    bold: bool = False,
) -> str:
    """Return a run of text with the given formatting."""
    properties = ""
    if style is not None:
        properties += f'<w:rStyle w:val="{_attr(style)}"/>'
    if bold:
        properties += "<w:b/>"
    if color is not None:
        properties += f'<w:color w:val="{_attr(color)}"/>'
    if size_half_points is not None:
        properties += f'<w:sz w:val="{size_half_points}"/>'
    if shading is not None:
        properties += f'<w:shd w:fill="{_attr(shading)}"/>'
    if hidden:
        properties += "<w:vanish/>"
    prefix = f"<w:rPr>{properties}</w:rPr>" if properties else ""
    return f'<w:r>{prefix}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def tab() -> str:
    """Return a tab character."""
    return "<w:r><w:tab/></w:r>"


def br() -> str:
    """Return a line break."""
    return "<w:r><w:br/></w:r>"


def ins(author: str, *runs: str, id: int = 1) -> str:
    """Return a tracked insertion."""
    return f'<w:ins w:id="{id}" w:author="{_attr(author)}" w:date="{_DATE}">{"".join(runs)}</w:ins>'


def delete(author: str, text: str, id: int = 1) -> str:
    """Return a tracked deletion, whose words are never in the contract."""
    return (
        f'<w:del w:id="{id}" w:author="{_attr(author)}" w:date="{_DATE}">'
        f'<w:r><w:delText xml:space="preserve">{escape(text)}</w:delText></w:r></w:del>'
    )


def tbl(*rows: tuple[str, ...]) -> str:
    """Return a table, one paragraph in each cell."""
    body = "".join(
        "<w:tr>" + "".join(f"<w:tc><w:p>{cell}</w:p></w:tc>" for cell in row) + "</w:tr>"
        for row in rows
    )
    return f"<w:tbl>{body}</w:tbl>"


def comment_range(comment_id: int, *runs: str) -> str:
    """Return the range a comment points at."""
    return (
        f'<w:commentRangeStart w:id="{comment_id}"/>'
        f"{''.join(runs)}"
        f'<w:commentRangeEnd w:id="{comment_id}"/>'
        f'<w:r><w:commentReference w:id="{comment_id}"/></w:r>'
    )


def comment(comment_id: int, author: str, text: str) -> str:
    """Return one comment for the `comments` part."""
    return (
        f'<w:comment w:id="{comment_id}" w:author="{_attr(author)}">'
        f"<w:p>{r(text)}</w:p></w:comment>"
    )
