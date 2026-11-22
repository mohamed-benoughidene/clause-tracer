"""Span helpers shared by every finder (S4-M1-T6)."""

from collections.abc import Iterable
from typing import Final

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span

KINDS: Final[tuple[PlaceholderKind, ...]] = tuple(PlaceholderKind)


def trimmed_span(text: str, span: Span) -> Span | None:
    """Move both ends of `span` over white space, or give `None` if none is left."""

    start = span.start
    end = span.end
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if start == end:
        return None
    return Span(start=start, end=end)


def overlaps(first: Span, second: Span) -> bool:
    """Say whether two non-empty spans share at least one character."""

    if first.start == first.end or second.start == second.end:
        return False
    return first.start < second.end and second.start < first.end


def order_key(suggestion: PiiSuggestion) -> tuple[int, int, int]:
    """Sort suggestions by start, then end, then the order of `PlaceholderKind`."""

    return (suggestion.span.start, suggestion.span.end, KINDS.index(suggestion.kind))


def unique_sorted(suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]:
    """Remove exact duplicates, then sort with a stable sort."""

    seen: set[tuple[Span, PlaceholderKind, PiiSource]] = set()
    unique: list[PiiSuggestion] = []
    for suggestion in suggestions:
        key = (suggestion.span, suggestion.kind, suggestion.source)
        if key in seen:
            continue
        seen.add(key)
        unique.append(suggestion)
    return tuple(sorted(unique, key=order_key))


def subtract_spans(span: Span, cuts: Iterable[Span]) -> tuple[Span, ...]:
    """Return the parts of `span` that no span of `cuts` covers, left to right."""

    pieces: list[Span] = []
    position = span.start
    for cut in sorted(cuts, key=lambda c: c.start):
        if cut.start > position:
            pieces.append(Span(start=position, end=min(cut.start, span.end)))
        position = max(position, cut.end)
    if position < span.end:
        pieces.append(Span(start=position, end=span.end))
    return tuple(piece for piece in pieces if piece.end > piece.start)
