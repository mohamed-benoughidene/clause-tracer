"""Resolve suggestions before grouping (S4-M3-T1).

The detector's output is checked once, where it enters (D4, I9). Every later
step keeps the rule that a flagged span is cut and never dropped whole.
"""

from collections.abc import Iterable, Sequence

from clause_tracer.core import (
    DefinedTerm,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy._spans import overlaps, subtract_spans, trimmed_span
from clause_tracer.privacy.names import (
    EXTENDED_COMPANY_SUFFIXES,
    HONORIFICS,
    fold_text,
)


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


def normalised_text(text: str) -> str:
    """Fold a text and drop a leading "the " and a trailing "'s"."""

    folded = fold_text(text).strip()
    if folded.startswith("the "):
        folded = folded[4:]
    if folded.endswith("'s"):
        folded = folded[:-2]
    return folded.strip()


def core_words(span_text: str) -> frozenset[str]:
    """The words of a name, without an honorific or an extended company suffix."""

    words = [word.strip(".,;:") for word in fold_text(span_text).split()]
    words = [word for word in words if word]
    if words and words[0] in HONORIFICS:
        words = words[1:]
    if len(words) > 1 and words[-1] in EXTENDED_COMPANY_SUFFIXES:
        words = words[:-1]
    return frozenset(words)


def _is_name_suggestion(suggestion: PiiSuggestion) -> bool:
    """Say whether a suggestion can make a defined term a name (question 11)."""

    is_party_details = suggestion.source == PiiSource.PARTY_DETAILS
    is_named_rule = suggestion.source == PiiSource.RULE and suggestion.kind in (
        PlaceholderKind.PERSON,
        PlaceholderKind.COMPANY,
    )
    return is_party_details or is_named_rule


def _term_is_a_name(
    text: str,
    term: DefinedTerm,
    value: str,
    suggestions: Sequence[PiiSuggestion],
) -> bool:
    """The Mercury rule: a term whose words all belong to a name inside its definition."""

    words = {word.strip(".,;:") for word in value.split()}
    words.discard("")
    if not words:
        return False
    for suggestion in suggestions:
        if suggestion.kind not in (PlaceholderKind.PERSON, PlaceholderKind.COMPANY):
            continue
        starts_inside = term.definition.start <= suggestion.span.start
        ends_inside = suggestion.span.end <= term.definition.end
        if not (starts_inside and ends_inside):
            continue
        span_text = text[suggestion.span.start : suggestion.span.end]
        if words <= core_words(span_text):
            return True
    return False


def allowed_term_texts(
    text: str,
    terms: Sequence[DefinedTerm],
    suggestions: Sequence[PiiSuggestion],
) -> frozenset[str]:
    """The defined terms that must not be replaced (Spec 4.2, question 11)."""

    name_suggestions = [s for s in suggestions if _is_name_suggestion(s)]
    name_texts = {normalised_text(text[s.span.start : s.span.end]) for s in name_suggestions}
    allowed: set[str] = set()
    for term in terms:
        value = normalised_text(term.term)
        if not value or value in name_texts:
            continue
        if _term_is_a_name(text, term, value, name_suggestions):
            continue
        allowed.add(value)
    return frozenset(allowed)


def drop_allowed(
    text: str,
    suggestions: Sequence[PiiSuggestion],
    allowed: frozenset[str],
) -> tuple[PiiSuggestion, ...]:
    """Drop the suggestions whose text is an allowed defined term."""

    kept: list[PiiSuggestion] = []
    for suggestion in suggestions:
        if suggestion.source in (PiiSource.USER, PiiSource.PARTY_DETAILS):
            kept.append(suggestion)
            continue
        span_text = text[suggestion.span.start : suggestion.span.end]
        if normalised_text(span_text) not in allowed:
            kept.append(suggestion)
    return tuple(kept)


def cut_in_places(
    text: str,
    suggestions: Sequence[PiiSuggestion],
    places: Sequence[Span],
) -> tuple[PiiSuggestion, ...]:
    """Keep the governing-law place, cutting every span that runs into it."""

    kept: list[PiiSuggestion] = []
    for suggestion in suggestions:
        if suggestion.source in (PiiSource.USER, PiiSource.PARTY_DETAILS):
            kept.append(suggestion)
            continue
        hits = [place for place in places if overlaps(place, suggestion.span)]
        if not hits:
            kept.append(suggestion)
            continue
        if suggestion.kind in (PlaceholderKind.PERSON, PlaceholderKind.COMPANY):
            kept.append(suggestion)
            continue
        for piece in subtract_spans(suggestion.span, hits):
            trimmed = trimmed_span(text, piece)
            if trimmed is None:
                continue
            if not any(character.isalnum() for character in text[trimmed.start : trimmed.end]):
                continue
            kept.append(PiiSuggestion(span=trimmed, kind=suggestion.kind, source=suggestion.source))
    return tuple(kept)
