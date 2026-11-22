"""Resolve suggestions before grouping (S4-M3-T1).

The detector's output is checked once, where it enters (D4, I9). Every later
step keeps the rule that a flagged span is cut and never dropped whole.
"""

from bisect import bisect_left, bisect_right
from collections.abc import Iterable, Mapping, Sequence
from types import MappingProxyType
from typing import Final

from clause_tracer.core import (
    Clause,
    DefinedTerm,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy._spans import (
    KINDS,
    overlaps,
    subtract_spans,
    trimmed_span,
    unique_sorted,
)
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
    """Keep the governing-law place. Cut every span that runs into it, except a
    PERSON or COMPANY span, which stays whole (question 25)."""

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


SOURCE_PRIORITY: Final[Mapping[PiiSource, int]] = MappingProxyType(
    {
        PiiSource.USER: 0,
        PiiSource.PARTY_DETAILS: 1,
        PiiSource.PATTERN: 2,
        PiiSource.RULE: 3,
        PiiSource.NER: 4,
    }
)
TIE_RANK: Final[Mapping[PlaceholderKind, int]] = MappingProxyType(
    {
        PlaceholderKind.BANK: 0,
        PlaceholderKind.ID: 1,
        PlaceholderKind.PERSON: 2,
        PlaceholderKind.COMPANY: 3,
        PlaceholderKind.ADDRESS: 4,
        PlaceholderKind.EMAIL: 5,
        PlaceholderKind.PHONE: 6,
    }
)


def union_ner(suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]:
    """Join overlapping detector spans of one kind (owner decision, 21 Nov 2026)."""

    items = tuple(suggestions)
    joined: list[PiiSuggestion] = []
    for kind in KINDS:
        same_kind = sorted(
            (item for item in items if item.source == PiiSource.NER and item.kind == kind),
            key=lambda item: (item.span.start, item.span.end),
        )
        if not same_kind:
            continue
        run_start = same_kind[0].span.start
        run_end = same_kind[0].span.end
        for item in same_kind[1:]:
            if item.span.start < run_end and run_start < item.span.end:
                run_end = max(run_end, item.span.end)
                continue
            joined.append(
                PiiSuggestion(
                    span=Span(start=run_start, end=run_end),
                    kind=kind,
                    source=PiiSource.NER,
                )
            )
            run_start = item.span.start
            run_end = item.span.end
        joined.append(
            PiiSuggestion(span=Span(start=run_start, end=run_end), kind=kind, source=PiiSource.NER)
        )
    others = [item for item in items if item.source != PiiSource.NER]
    return (*others, *joined)


def resolve_overlaps(text: str, suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]:
    """Resolve overlaps by source, then length, then start, then kind."""

    ordered = sorted(
        union_ner(suggestions),
        key=lambda item: (
            SOURCE_PRIORITY[item.source],
            -(item.span.end - item.span.start),
            item.span.start,
            TIE_RANK[item.kind],
        ),
    )
    kept: list[PiiSuggestion] = []
    starts: list[int] = []
    for suggestion in ordered:
        left = bisect_left(starts, suggestion.span.start)
        if left > 0 and kept[left - 1].span.end > suggestion.span.start:
            left -= 1
        hits: list[PiiSuggestion] = []
        index = left
        while index < len(kept) and kept[index].span.start < suggestion.span.end:
            if kept[index].span.end > suggestion.span.start:
                hits.append(kept[index])
            index += 1
        if hits:
            pieces = subtract_spans(suggestion.span, (hit.span for hit in hits))
        else:
            pieces = (suggestion.span,)
        for piece in pieces:
            trimmed = trimmed_span(text, piece)
            if trimmed is None:
                continue
            if hits and not any(
                character.isalnum() for character in text[trimmed.start : trimmed.end]
            ):
                continue
            added = PiiSuggestion(span=trimmed, kind=suggestion.kind, source=suggestion.source)
            position = bisect_left(starts, trimmed.start)
            kept.insert(position, added)
            starts.insert(position, trimmed.start)
    return tuple(sorted(kept, key=lambda item: (item.span.start, item.span.end)))


def sentence_starts(clauses: Sequence[Clause]) -> tuple[int, ...]:
    """The sorted, distinct start of every sentence in every clause."""

    return tuple(
        sorted({sentence.span.start for clause in clauses for sentence in clause.sentences})
    )


def split_at_sentences(
    text: str,
    suggestions: Iterable[PiiSuggestion],
    starts: Sequence[int],
) -> tuple[PiiSuggestion, ...]:
    """Cut every suggestion at each sentence start strictly inside its span."""

    pieces: list[PiiSuggestion] = []
    for suggestion in suggestions:
        span = suggestion.span
        index = bisect_right(starts, span.start)
        cuts = [span.start]
        while index < len(starts) and starts[index] < span.end:
            cuts.append(starts[index])
            index += 1
        cuts.append(span.end)
        for start, end in zip(cuts, cuts[1:], strict=False):
            trimmed = trimmed_span(text, Span(start=start, end=end))
            if trimmed is None:
                continue
            pieces.append(
                PiiSuggestion(span=trimmed, kind=suggestion.kind, source=suggestion.source)
            )
    return unique_sorted(pieces)
