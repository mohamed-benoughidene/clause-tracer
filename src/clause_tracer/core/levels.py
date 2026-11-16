"""Level order, span overlap and reason order (Spec 5).

The label levels are ordered preferred, acceptable, walk-away; unsure
has no place in that order. Reasons are always returned as codes in
ReasonCode member order (I7), so a label's reasons never depend on the
order the values arrived in.
"""

from collections.abc import Iterable

from clause_tracer.core.document import Document
from clause_tracer.core.enums import Level, ReasonCode
from clause_tracer.core.results import UnreadableSpans
from clause_tracer.core.wording import Span

_RANKS: dict[Level, int] = {
    Level.PREFERRED: 0,
    Level.ACCEPTABLE: 1,
    Level.WALK_AWAY: 2,
}


def level_rank(level: Level) -> int:
    """The rank of a readable level; unsure has no rank."""

    if level is Level.UNSURE:
        raise ValueError("unsure has no rank")
    return _RANKS[level]


def is_better(a: Level, b: Level) -> bool:
    """True when level a is strictly better than level b."""

    return level_rank(a) < level_rank(b)


def worst_level(levels: Iterable[Level]) -> Level:
    """The worst readable level of a non-empty iterable."""

    found: Level | None = None
    for level in levels:
        if found is None or level_rank(level) > level_rank(found):
            found = level
    if found is None:
        raise ValueError("no levels to compare")
    return found


def spans_overlap(a: Span, b: Span) -> bool:
    """True when the half-open spans share at least one code point."""

    return max(a.start, b.start) < min(a.end, b.end)


def unreadable_spans(document: Document) -> UnreadableSpans:
    """The Rule 9 input: hidden spans that sit in the text, and undecodable spans."""

    hidden = tuple(hidden.span for hidden in document.hidden if hidden.span is not None)
    return UnreadableSpans(hidden=hidden, undecodable=document.undecodable)


def sort_reasons(reasons: Iterable[ReasonCode]) -> tuple[ReasonCode, ...]:
    """The reasons without repeats, in ReasonCode member order (I7)."""

    wanted = set(reasons)
    return tuple(code for code in ReasonCode if code in wanted)
