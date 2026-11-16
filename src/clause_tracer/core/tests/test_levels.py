"""Tests for level order, span overlap and reason order (Spec 5)."""

import pytest
from hypothesis import given

from clause_tracer.core import (
    Document,
    FileKind,
    HiddenReason,
    HiddenText,
    Level,
    ReasonCode,
    SourceFile,
    Span,
    UnreadableSpans,
    is_better,
    level_rank,
    sort_reasons,
    spans_overlap,
    unreadable_spans,
    worst_level,
)
from clause_tracer.core.tests.strategies import spans


def test_level_rank() -> None:
    assert level_rank(Level.PREFERRED) == 0
    assert level_rank(Level.ACCEPTABLE) == 1
    assert level_rank(Level.WALK_AWAY) == 2


def test_unsure_has_no_rank() -> None:
    with pytest.raises(ValueError, match="unsure has no rank"):
        level_rank(Level.UNSURE)


def test_is_better() -> None:
    assert is_better(Level.PREFERRED, Level.ACCEPTABLE)
    assert is_better(Level.ACCEPTABLE, Level.WALK_AWAY)
    assert not is_better(Level.WALK_AWAY, Level.ACCEPTABLE)
    assert not is_better(Level.PREFERRED, Level.PREFERRED)


def test_worst_level() -> None:
    assert worst_level([Level.PREFERRED, Level.ACCEPTABLE]) is Level.ACCEPTABLE
    assert worst_level([Level.WALK_AWAY, Level.PREFERRED]) is Level.WALK_AWAY
    with pytest.raises(ValueError):
        worst_level([])


def test_spans_overlap_examples() -> None:
    # Half-open spans: they share no character when one ends where the
    # next starts, and an empty span overlaps nothing.
    assert not spans_overlap(Span(start=0, end=5), Span(start=5, end=9))
    assert spans_overlap(Span(start=0, end=5), Span(start=4, end=9))
    assert not spans_overlap(Span(start=3, end=3), Span(start=0, end=9))


def test_unreadable_spans_skips_hidden_without_span() -> None:
    # Hidden text not in the canonical text has no span; it cannot make
    # a value unreadable.
    document = Document(
        schema_version=1,
        source=SourceFile(name="c.pdf", kind=FileKind.PDF, sha256="ab", size=3),
        text="t",
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(
            HiddenText(span=None, reason=HiddenReason.COMMENT, boxes=()),
            HiddenText(span=Span(start=0, end=5), reason=HiddenReason.LOW_CONTRAST, boxes=()),
        ),
        undecodable=(Span(start=7, end=9),),
        tracked_changes=(),
        warnings=(),
    )
    assert unreadable_spans(document) == UnreadableSpans(
        hidden=(Span(start=0, end=5),),
        undecodable=(Span(start=7, end=9),),
    )


def test_sort_reasons() -> None:
    # No repeats, in ReasonCode member order (I7).
    assert sort_reasons([ReasonCode.RANGE, ReasonCode.HIDDEN_TEXT, ReasonCode.RANGE]) == (
        ReasonCode.RANGE,
        ReasonCode.HIDDEN_TEXT,
    )
    assert sort_reasons([]) == ()


@given(a=spans(), b=spans())
def test_spans_overlap_is_symmetric(a: Span, b: Span) -> None:
    assert spans_overlap(a, b) == spans_overlap(b, a)
