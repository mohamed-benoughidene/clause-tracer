"""Span helpers (S3-M2-T1)."""

from clause_tracer.core import Span
from clause_tracer.links._spans import build_span_set, trimmed


def _span(start: int, end: int) -> Span:
    return Span(start=start, end=end)


def test_trimmed() -> None:
    assert trimmed("ab \n", _span(0, 4)) == _span(0, 2)
    assert trimmed("   ", _span(0, 3)) == _span(0, 0)


def test_overlap_inside() -> None:
    assert build_span_set([_span(2, 8)]).overlaps(_span(3, 4)) is True


def test_overlap_touching_is_not_overlap() -> None:
    span_set = build_span_set([_span(2, 4)])
    assert span_set.overlaps(_span(4, 6)) is False
    assert span_set.overlaps(_span(0, 2)) is False


def test_overlap_long_earlier_span() -> None:
    span_set = build_span_set([_span(0, 100), _span(10, 12)])
    assert span_set.overlaps(_span(50, 60)) is True


def test_empty_span_overlaps_nothing() -> None:
    assert build_span_set([_span(2, 8)]).overlaps(_span(3, 3)) is False


def test_empty_set() -> None:
    assert build_span_set(()).overlaps(_span(0, 5)) is False


def test_empty_span_in_the_set_overlaps_nothing() -> None:
    assert build_span_set([_span(5, 5)]).overlaps(_span(3, 8)) is False
    span_set = build_span_set([_span(5, 5), _span(10, 12)])
    assert span_set.overlaps(_span(3, 8)) is False
    assert span_set.overlaps(_span(11, 20)) is True
