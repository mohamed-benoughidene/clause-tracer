"""The hardened XML parser (S5-M2-T4).

This is the only file of `src/` that imports lxml (B4). Before lxml sees a
part, the standard library's expat reads the prolog: a DOCTYPE is refused
there, and so is an encoding label other than UTF-8 or UTF-16 (ADR 0007
amendment, 27 Nov 2026). One lxml parser is then built once and shared; it
resolves no entity, loads no DTD, opens no network and never uses the
huge-tree mode. A part with a DOCTYPE is refused a second time after the
parse, when lxml can still show one.
"""

from typing import Final
from xml.parsers import expat

from lxml import etree

from clause_tracer.core import UnreadableFileError

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


class _RootReached(Exception):
    """The prolog ended: the first element started."""


def _on_xml_decl(version: str, encoding: str | None, standalone: int) -> None:
    is_other_encoding = encoding is not None and encoding.upper() not in _ALLOWED_ENCODINGS
    if is_other_encoding:
        raise ValueError("ingest: unsupported XML encoding")


def _on_doctype(name: str, sysid: str | None, pubid: str | None, has_internal_subset: int) -> None:
    raise UnreadableFileError({"reason": "doctype"})


def _on_start_element(name: str, attrs: dict[str, str]) -> None:
    raise _RootReached


def _check_prolog(data: bytes) -> None:
    """Refuse a DOCTYPE and a foreign encoding label before lxml reads the part."""

    reader = expat.ParserCreate()
    reader.XmlDeclHandler = _on_xml_decl
    reader.StartDoctypeDeclHandler = _on_doctype
    reader.StartElementHandler = _on_start_element

    try:
        reader.Parse(data, True)
    except _RootReached:
        return
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
             DOCTYPE, or `xml_invalid` when the part cannot be read. A
             MemoryError is not caught.
    Effects: none.
    """

    _check_prolog(data)

    try:
        root = etree.fromstring(data, parser=_PARSER)
    except etree.LxmlError:
        raise UnreadableFileError({"reason": "xml_invalid"}) from None

    has_doctype = root.getroottree().docinfo.doctype != ""
    if has_doctype:
        raise UnreadableFileError({"reason": "doctype"})

    return root
