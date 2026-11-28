"""The side text of a Word file (S5-M3-T5, S5-M3-T6).

A comment, a note, a header and a footer are side text: their words are
never in `Document.text`. The body holds range marks instead, so a
comment can point at the words it talks about. This module reads those
parts, links each comment to its range, and names the hidden findings
that side text adds.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Final

from clause_tracer.core import HiddenReason, HiddenText, SideText, SideTextKind, Span
from clause_tracer.ingest._word_body import _assemble, _Paragraph, _Walker
from clause_tracer.ingest._word_model import SectionRefs, Text
from clause_tracer.ingest._word_styles import Styles
from clause_tracer.ingest._xml import W_NS, Element, parse_part, qname
from clause_tracer.ingest._zip import WordPackage

_COMMENT: Final[str] = qname(W_NS, "comment")
_FOOTNOTE: Final[str] = qname(W_NS, "footnote")
_ENDNOTE: Final[str] = qname(W_NS, "endnote")
_ID: Final[str] = qname(W_NS, "id")
_AUTHOR: Final[str] = qname(W_NS, "author")
_TYPE: Final[str] = qname(W_NS, "type")

_HEADER_PREFIX: Final[str] = "word/header"
_FOOTER_PREFIX: Final[str] = "word/footer"
_PART_SUFFIX: Final[str] = ".xml"


def _flow(element: Element, styles: Styles | None) -> tuple[str, bool]:
    """Return a part's lines and whether it holds a hidden or tiny run."""

    walker = _Walker(styles=styles)
    paragraphs: list[_Paragraph] = []
    walker._walk_blocks(element, paragraphs)
    text, positions = _assemble(paragraphs)
    has_hidden_run = any(
        isinstance(piece, Text) and piece.hidden for piece, _start, _end in positions
    )
    return text.removesuffix("\n"), has_hidden_run


def _flow_text(element: Element, styles: Styles | None) -> str:
    return _flow(element, styles)[0]


def read_comments(root: Element | None, styles: Styles | None) -> tuple[SideText, ...]:
    """Read a parsed `word/comments.xml`; `None` gives no comments."""

    if root is None:
        return ()
    comments: list[SideText] = []
    for element in root:
        if element.tag != _COMMENT:
            continue
        comments.append(
            SideText(
                kind=SideTextKind.COMMENT,
                ref=element.get(_ID) or "",
                author=element.get(_AUTHOR) or "",
                text=_flow_text(element, styles),
            )
        )
    return tuple(comments)


def link_comments(
    comments: tuple[SideText, ...], spans: Mapping[str, Span | None]
) -> tuple[SideText, ...]:
    """Give each comment the span of the words it points at."""

    return tuple(replace(comment, span=spans.get(comment.ref)) for comment in comments)


def comment_hidden(
    spans: Mapping[str, Span | None], comments: tuple[SideText, ...]
) -> tuple[HiddenText, ...]:
    """Return the comment marks and the comments that never show."""

    hidden: list[HiddenText] = []
    for span in spans.values():
        if span is not None:
            hidden.append(HiddenText(span=span, reason=HiddenReason.COMMENT, boxes=()))
    for comment in comments:
        if comment.ref not in spans:
            hidden.append(
                HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=())
            )
    return tuple(hidden)


def hidden_comments(root: Element | None, styles: Styles | None) -> tuple[str, ...]:
    """Return the ids of the comments that hold a hidden or tiny run."""

    if root is None:
        return ()
    refs: list[str] = []
    for element in root:
        if element.tag != _COMMENT:
            continue
        walker = _Walker(styles=styles)
        paragraphs: list[_Paragraph] = []
        walker._walk_blocks(element, paragraphs)
        _, positions = _assemble(paragraphs)
        has_hidden_run = any(
            isinstance(piece, Text) and piece.hidden for piece, _start, _end in positions
        )
        if has_hidden_run:
            refs.append(element.get(_ID) or "")
    return tuple(refs)


def _read_note_part(
    root: Element | None, kind: SideTextKind, styles: Styles | None
) -> list[tuple[str, str]]:
    if root is None:
        return []
    tag = _FOOTNOTE if kind is SideTextKind.FOOTNOTE else _ENDNOTE
    notes: list[tuple[str, str]] = []
    for element in root:
        if element.tag != tag:
            continue
        if "separator" in (element.get(_TYPE) or ""):
            continue
        text = _flow_text(element, styles)
        if text == "":
            continue
        notes.append((element.get(_ID) or "", text))
    return notes


def read_notes(
    footnotes: Element | None,
    endnotes: Element | None,
    referenced: tuple[tuple[SideTextKind, str], ...],
    styles: Styles | None,
) -> tuple[tuple[SideText, ...], tuple[HiddenText, ...]]:
    """Read the notes, referenced ones first and then the others."""

    found: dict[tuple[SideTextKind, str], SideText] = {}
    file_order: dict[SideTextKind, list[str]] = {
        SideTextKind.FOOTNOTE: [],
        SideTextKind.ENDNOTE: [],
    }
    for kind, root in (
        (SideTextKind.FOOTNOTE, footnotes),
        (SideTextKind.ENDNOTE, endnotes),
    ):
        for ref, text in _read_note_part(root, kind, styles):
            found[(kind, ref)] = SideText(kind=kind, ref=ref, author="", text=text)
            file_order[kind].append(ref)

    side: list[SideText] = []
    hidden: list[HiddenText] = []
    seen: set[tuple[SideTextKind, str]] = set()
    for kind, ref in referenced:
        key = (kind, ref)
        if key in seen:
            continue
        seen.add(key)
        note = found.get(key)
        if note is not None:
            side.append(note)
    for kind in (SideTextKind.FOOTNOTE, SideTextKind.ENDNOTE):
        for ref in file_order[kind]:
            key = (kind, ref)
            if key in seen:
                continue
            seen.add(key)
            side.append(found[key])
            hidden.append(
                HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=())
            )
    return tuple(side), tuple(hidden)


def _is_shown(ref_type: str, section: SectionRefs, even_and_odd: bool) -> bool:
    if ref_type == "default":
        return True
    if ref_type == "first":
        return section.title_page
    if ref_type == "even":
        return even_and_odd
    return False


def read_headers_and_footers(
    package: WordPackage,
    rels: Mapping[str, str],
    sections: tuple[SectionRefs, ...],
    even_and_odd: bool,
    styles: Styles | None,
) -> tuple[tuple[SideText, ...], tuple[HiddenText, ...]]:
    """Read every header and footer part, shown ones first."""

    names = [
        name
        for name in package.names()
        if (name.startswith(_HEADER_PREFIX) or name.startswith(_FOOTER_PREFIX))
        and name.endswith(_PART_SUFFIX)
    ]
    shown: dict[str, list[str]] = {
        _HEADER_PREFIX: [],
        _FOOTER_PREFIX: [],
    }
    for section in sections:
        for prefix, references in (
            (_HEADER_PREFIX, section.headers),
            (_FOOTER_PREFIX, section.footers),
        ):
            for ref_type, rel_id in references:
                target = rels.get(rel_id)
                if not _is_shown(ref_type, section, even_and_odd):
                    continue
                if target is None or target not in names:
                    continue
                if target not in shown[prefix]:
                    shown[prefix].append(target)

    side: list[SideText] = []
    hidden: list[HiddenText] = []
    for prefix, kind in (
        (_HEADER_PREFIX, SideTextKind.HEADER),
        (_FOOTER_PREFIX, SideTextKind.FOOTER),
    ):
        seen_text: set[str] = set()
        for name in shown[prefix]:
            text, has_hidden_run = _flow(parse_part(package.read_part(name)), styles)
            if text == "" or text in seen_text:
                continue
            seen_text.add(text)
            side.append(SideText(kind=kind, ref=name, author="", text=text))
            if has_hidden_run:
                hidden.append(HiddenText(span=None, reason=HiddenReason.WORD_HIDDEN_RUN, boxes=()))
        for name in names:
            if not name.startswith(prefix) or name in shown[prefix]:
                continue
            text, has_hidden_run = _flow(parse_part(package.read_part(name)), styles)
            if text == "":
                continue
            side.append(SideText(kind=kind, ref=name, author="", text=text))
            hidden.append(
                HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=())
            )
            if has_hidden_run:
                hidden.append(HiddenText(span=None, reason=HiddenReason.WORD_HIDDEN_RUN, boxes=()))
    return tuple(side), tuple(hidden)
