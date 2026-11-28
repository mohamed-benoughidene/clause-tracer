"""The hardened XML parser (S5-M2-T4, S5-M2-T9).

This is the only file of `src/` that imports lxml (B4). Before lxml sees a
part, the standard library's expat reads all of it: a DOCTYPE is refused,
and so is an encoding label other than UTF-8 or UTF-16, nesting deeper
than `MAX_XML_DEPTH`, and more than `MAX_XML_TEXT_BYTES` in one run of
text, one comment, one processing instruction or the attributes of one
tag. Those limits belong to the product because the limits of lxml differ
between systems (ADR 0007 amendments, 27 and 28 Nov 2026). One lxml parser
is then built once and shared; it resolves no entity, loads no DTD, opens
no network and never uses the huge-tree mode. A part with a DOCTYPE is
refused a second time after the parse, when lxml can still show one.
"""

from typing import Final
from xml.parsers import expat

from lxml import etree

from clause_tracer.core import UnreadableFileError
from clause_tracer.ingest.limits import MAX_XML_DEPTH, MAX_XML_TEXT_BYTES

W_NS: Final[str] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

_ALLOWED_ENCODINGS: Final[frozenset[str]] = frozenset({"UTF-8", "UTF-16"})

_PARSER: Final[etree.XMLParser] = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    load_dtd=False,
    dtd_validation=False,
    huge_tree=False,
    remove_comments=True,
    remove_pis=True,
    collect_ids=False,
)
# The parser is shared and must not be modified (T4).


def _utf8_size(text: str) -> int:
    """Return the bytes of a text in UTF-8."""
    return len(text.encode("utf-8"))


def _check_size(size: int) -> None:
    is_too_long = size > MAX_XML_TEXT_BYTES
    if is_too_long:
        raise UnreadableFileError({"reason": "xml_invalid"})


class _PartScan:
    """Count the nesting and the length of each run of content."""

    __slots__ = ("_depth", "_run_bytes")

    def __init__(self) -> None:
        self._depth = 0
        self._run_bytes = 0

    def start_element(self, name: str, attrs: dict[str, str]) -> None:
        self._depth += 1
        self._run_bytes = 0
        is_too_deep = self._depth > MAX_XML_DEPTH
        if is_too_deep:
            raise UnreadableFileError({"reason": "xml_invalid"})
        if attrs:
            _check_size(sum(_utf8_size(key) + _utf8_size(value) for key, value in attrs.items()))

    def end_element(self, name: str) -> None:
        self._depth -= 1
        self._run_bytes = 0

    def characters(self, data: str) -> None:
        self._run_bytes += _utf8_size(data)
        _check_size(self._run_bytes)


def _on_xml_decl(version: str, encoding: str | None, standalone: int) -> None:
    is_other_encoding = encoding is not None and encoding.upper() not in _ALLOWED_ENCODINGS
    if is_other_encoding:
        raise ValueError("ingest: unsupported XML encoding")


def _on_doctype(name: str, sysid: str | None, pubid: str | None, has_internal_subset: int) -> None:
    raise UnreadableFileError({"reason": "doctype"})


def _on_comment(data: str) -> None:
    _check_size(_utf8_size(data))


def _on_processing_instruction(target: str, data: str) -> None:
    _check_size(_utf8_size(target) + _utf8_size(data))


def _check_part(data: bytes) -> None:
    """Refuse a part that the product does not accept, before lxml reads it."""

    scan = _PartScan()
    reader = expat.ParserCreate()
    reader.buffer_text = True
    reader.XmlDeclHandler = _on_xml_decl
    reader.StartDoctypeDeclHandler = _on_doctype
    reader.StartElementHandler = scan.start_element
    reader.EndElementHandler = scan.end_element
    reader.CharacterDataHandler = scan.characters
    reader.CommentHandler = _on_comment
    reader.ProcessingInstructionHandler = _on_processing_instruction

    try:
        reader.Parse(data, True)
    except (expat.ExpatError, ValueError, LookupError):
        raise UnreadableFileError({"reason": "xml_invalid"}) from None


def qname(namespace: str, local: str) -> str:
    """Return the Clark name of a namespace and a local name."""
    return f"{{{namespace}}}{local}"


def parse_part(data: bytes) -> etree._Element:
    """Parse one XML part of a Word package.

    Input:   the part's bytes.
    Output:  the root element, without comments or processing instructions.
    Raises:  UnreadableFileError with reason `doctype` when the part has a
             DOCTYPE, or `xml_invalid` when the part is not accepted. A
             MemoryError is not caught.
    Effects: none.
    """

    _check_part(data)

    try:
        root = etree.fromstring(data, parser=_PARSER)
    except etree.LxmlError:
        raise UnreadableFileError({"reason": "xml_invalid"}) from None

    has_doctype = root.getroottree().docinfo.doctype != ""
    if has_doctype:
        raise UnreadableFileError({"reason": "doctype"})

    return root
