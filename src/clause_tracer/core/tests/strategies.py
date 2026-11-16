"""Hypothesis strategies for the core tests. Not exported from core."""

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy, composite

from clause_tracer.core import (
    UNSURE_REASONS,
    ClauseId,
    Direction,
    Level,
    NumberRule,
    Position,
    PositionId,
    PositionType,
    ReasonCode,
    Span,
    Unit,
    ValueVerdict,
    WordsRule,
    YesNoRule,
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


@composite
def positions(draw: st.DrawFn) -> Position:
    """Playbook positions of any type, with limits ordered so the
    preferred limit is the stricter one."""

    number = draw(st.integers(0, 99))
    position_type = draw(st.sampled_from(PositionType))
    unit = draw(st.sampled_from(Unit))
    direction = draw(st.sampled_from(Direction))
    first = draw(st.decimals(0, 100, places=0))
    second = draw(st.decimals(0, 100, places=0))
    if direction is Direction.LOWER_IS_BETTER:
        rule: NumberRule | YesNoRule | WordsRule = NumberRule(
            unit=unit,
            direction=direction,
            preferred_limit=min(first, second),
            acceptable_limit=max(first, second),
        )
    else:
        rule = NumberRule(
            unit=unit,
            direction=direction,
            preferred_limit=max(first, second),
            acceptable_limit=min(first, second),
        )
    if position_type is PositionType.YES_NO:
        rule = YesNoRule(
            question="q",
            yes_level=draw(st.sampled_from([Level.PREFERRED, Level.ACCEPTABLE, Level.WALK_AWAY])),
            no_level=draw(st.sampled_from([Level.PREFERRED, Level.ACCEPTABLE, Level.WALK_AWAY])),
        )
    elif position_type is PositionType.WORDS:
        rule = WordsRule(preferred="a", acceptable="b", walk_away="c")
    return Position(
        id=PositionId(f"p{number}"),
        topic="t",
        type=position_type,
        rule=rule,
        missing_level=draw(st.sampled_from(Level)),
        why_note=None,
    )
