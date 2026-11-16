"""Hypothesis strategies for the core tests. Not exported from core."""

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy, composite

from clause_tracer.core import (
    UNSURE_REASONS,
    ClauseId,
    Level,
    ReasonCode,
    Span,
    ValueVerdict,
)


def spans() -> SearchStrategy[Span]:
    """Spans over the canonical text: a start and a length."""

    return st.builds(
        lambda start, length: Span(start=start, end=start + length),
        start=st.integers(0, 200),
        length=st.integers(0, 50),
    )


@composite
def value_verdicts(draw: st.DrawFn) -> ValueVerdict:
    """Value verdicts for Rule 4: unsure ones with unsure reasons, and
    readable ones with note reasons and a readable value."""

    clause_id = draw(st.sampled_from(["c1", "c2", "c3"]))
    level = draw(st.sampled_from(Level))
    if level is Level.UNSURE:
        reasons: list[ReasonCode] = draw(
            st.lists(st.sampled_from(sorted(UNSURE_REASONS)), min_size=1, max_size=3)
        )
        readable: str | None = None
    else:
        reasons = draw(
            st.lists(
                st.sampled_from([ReasonCode.RANGE, ReasonCode.CLAUSES_DISAGREE]),
                min_size=0,
                max_size=2,
            )
        )
        readable = draw(st.sampled_from(["5", "10", "30"]))
    return ValueVerdict(
        clause_id=ClauseId(clause_id),
        level=level,
        reasons=tuple(reasons),
        evidence=None,
        readable_value=readable,
    )
