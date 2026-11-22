"""The span helpers (S4-M1-T6)."""

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy._spans import (
    order_key,
    overlaps,
    subtract_spans,
    trimmed_span,
    unique_sorted,
)


def _suggestion(
    start: int,
    end: int,
    kind: PlaceholderKind = PlaceholderKind.PERSON,
    source: PiiSource = PiiSource.RULE,
) -> PiiSuggestion:
    return PiiSuggestion(span=Span(start=start, end=end), kind=kind, source=source)


def test_trimmed_span_moves_both_ends() -> None:
    assert trimmed_span("  ab  ", Span(start=0, end=6)) == Span(start=2, end=4)


def test_trimmed_span_all_space_is_none() -> None:
    assert trimmed_span("   ", Span(start=0, end=3)) is None


def test_trimmed_span_empty_is_none() -> None:
    assert trimmed_span("abc", Span(start=1, end=1)) is None


def test_overlaps_true() -> None:
    assert overlaps(Span(start=0, end=3), Span(start=2, end=5))


def test_overlaps_touching_is_false() -> None:
    assert not overlaps(Span(start=0, end=3), Span(start=3, end=5))


def test_overlaps_empty_is_false() -> None:
    assert not overlaps(Span(start=2, end=2), Span(start=0, end=5))


def test_order_key_uses_kind_order() -> None:
    address = _suggestion(0, 5, PlaceholderKind.ADDRESS)
    person = _suggestion(0, 5, PlaceholderKind.PERSON)

    assert order_key(person) < order_key(address)


def test_unique_sorted_removes_duplicates_and_sorts() -> None:
    first = _suggestion(0, 1)
    second = _suggestion(5, 6)

    assert unique_sorted([second, first, second]) == (first, second)


def test_subtract_spans_cuts_the_middle() -> None:
    assert subtract_spans(Span(start=0, end=10), (Span(start=3, end=5),)) == (
        Span(start=0, end=3),
        Span(start=5, end=10),
    )


def test_subtract_spans_cuts_an_edge() -> None:
    assert subtract_spans(Span(start=0, end=10), (Span(start=0, end=4),)) == (
        Span(start=4, end=10),
    )


def test_subtract_spans_joins_overlapping_cuts() -> None:
    assert subtract_spans(Span(start=0, end=10), (Span(start=3, end=6), Span(start=2, end=4))) == (
        Span(start=0, end=2),
        Span(start=6, end=10),
    )


def test_subtract_spans_nothing_left() -> None:
    assert subtract_spans(Span(start=2, end=5), (Span(start=0, end=10),)) == ()


def test_subtract_spans_no_cuts() -> None:
    assert subtract_spans(Span(start=0, end=10), ()) == (Span(start=0, end=10),)
