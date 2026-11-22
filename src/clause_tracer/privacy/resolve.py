"""Resolve suggestions before grouping (S4-M3-T1).

The detector's output is checked once, where it enters (D4, I9). Every later
step keeps the rule that a flagged span is cut and never dropped whole.
"""

from collections.abc import Iterable

from clause_tracer.core import PiiSuggestion
from clause_tracer.privacy._spans import trimmed_span


def trim_suggestions(text: str, suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]:
    """Check every span, then trim white space and drop empty suggestions.

    Input:   the contract text and the suggestions to check.
    Output:  the kept suggestions, in input order, with trimmed spans.
    Raises:  ValueError when a span is bad, before any result exists.
    Effects: none (T1).
    """

    items = tuple(suggestions)
    for suggestion in items:
        start = suggestion.span.start
        end = suggestion.span.end
        if isinstance(start, bool) or not isinstance(start, int):
            raise ValueError("privacy: suggestion span offsets must be integers")
        if isinstance(end, bool) or not isinstance(end, int):
            raise ValueError("privacy: suggestion span offsets must be integers")
        if start < 0 or end < 0 or start > len(text) or end > len(text):
            raise ValueError("privacy: suggestion span is outside the text")
        if end < start:
            raise ValueError("privacy: suggestion span is reversed")

    kept: list[PiiSuggestion] = []
    for suggestion in items:
        span = trimmed_span(text, suggestion.span)
        if span is None:
            continue
        kept.append(PiiSuggestion(span=span, kind=suggestion.kind, source=suggestion.source))
    return tuple(kept)
