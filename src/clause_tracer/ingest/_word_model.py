"""The shapes the Word reader shares (S5-M3-T1)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from clause_tracer.core import HiddenReason, HiddenText, SideTextKind, Span, TrackedChange


@dataclass(frozen=True, slots=True, kw_only=True)
class Text:
    """One run of text, with what the later tasks find in it."""

    text: str
    hidden: tuple[HiddenReason, ...] = ()
    change: int | None = None
    is_number: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class Mark:
    """A comment range mark, which holds no text."""

    kind: Literal["comment_start", "comment_end"]
    ref: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SectionRefs:
    """The headers and footers one section references."""

    headers: tuple[tuple[str, str], ...]
    footers: tuple[tuple[str, str], ...]
    title_page: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class BodyResult:
    """Everything the body walk finds, before it becomes a Document."""

    text: str
    hidden: tuple[HiddenText, ...] = ()
    tracked_changes: tuple[TrackedChange, ...] = ()
    comment_spans: Mapping[str, Span | None] = field(default_factory=dict)
    note_refs: tuple[tuple[SideTextKind, str], ...] = ()
    sections: tuple[SectionRefs, ...] = ()
    numbering_unknown: bool = False
    symbol_unread: bool = False
