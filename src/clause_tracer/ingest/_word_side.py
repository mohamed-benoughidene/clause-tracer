"""Comments of a Word file (S5-M3-T5).

A comment is side text: its words are never in `Document.text`. The body
holds range marks instead, so a comment can point at the words it talks
about. This module reads the comments part, links each comment to its
range, and names the hidden findings that comments add.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Final

from clause_tracer.core import HiddenReason, HiddenText, SideText, SideTextKind, Span
from clause_tracer.ingest._word_body import _assemble, _Paragraph, _Walker
from clause_tracer.ingest._word_model import Text
from clause_tracer.ingest._word_styles import Styles
from clause_tracer.ingest._xml import W_NS, Element, qname

_COMMENT: Final[str] = qname(W_NS, "comment")
_ID: Final[str] = qname(W_NS, "id")
_AUTHOR: Final[str] = qname(W_NS, "author")


def _flow_text(element: Element, styles: Styles | None) -> str:
    walker = _Walker(styles=styles)
    paragraphs: list[_Paragraph] = []
    walker._walk_blocks(element, paragraphs)
    return _assemble(paragraphs)[0].removesuffix("\n")


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
