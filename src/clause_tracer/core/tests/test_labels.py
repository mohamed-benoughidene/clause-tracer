"""Tests for the label rules of Spec 5 (S1-M3-T13 onwards)."""

import dataclasses
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import (
    UNSURE_REASONS,
    Answer,
    CallFailed,
    CheckedValue,
    ClauseId,
    Direction,
    Evidence,
    JudgedLevel,
    LabelInput,
    Level,
    MatchFound,
    MatchResult,
    NothingFound,
    NumberRule,
    OutsideDocument,
    Position,
    PositionId,
    PositionType,
    ReasonCode,
    SentenceId,
    Span,
    Unit,
    UnreadableSpans,
    ValueVerdict,
    WordsRule,
    WrittenBy,
    YesNoRule,
    combine_rule_4,
    label_position,
    number_verdicts,
    words_verdict,
    yes_no_verdict,
)
from clause_tracer.core.tests.label_cases import LabelCase, label_rule_cases
from clause_tracer.core.tests.strategies import positions, value_verdicts

PAYMENT_DAYS = NumberRule(
    unit=Unit.DAYS,
    direction=Direction.LOWER_IS_BETTER,
    preferred_limit=Decimal(15),
    acceptable_limit=Decimal(30),
)
DEPOSIT_PERCENT = NumberRule(
    unit=Unit.PERCENT,
    direction=Direction.HIGHER_IS_BETTER,
    preferred_limit=Decimal(50),
    acceptable_limit=Decimal(25),
)
PAID_IF_CANCELLED = YesNoRule(
    question="Paid if cancelled",
    yes_level=Level.PREFERRED,
    no_level=Level.WALK_AWAY,
)

NO_HIDDEN = UnreadableSpans(hidden=(), undecodable=())


def value(**changes: object) -> CheckedValue:
    """A confirmed 60-day value on clause c1, with any field replaced."""

    base = CheckedValue(
        position_id=PositionId("1"),
        clause_id=ClauseId("c1"),
        evidence=Evidence(
            clause_id=ClauseId("c1"),
            sentence_ids=(SentenceId("c1.s1"),),
            quote=Span(start=0, end=10),
            placed=True,
        ),
        raw_value="60 days",
        number=Decimal(60),
        range_high=None,
        unit_as_written="days",
        start_point_as_written=None,
        answer=None,
        condition=None,
        vague=False,
        amount=None,
        total=None,
        reasons=(),
    )
    # The plan fixes this signature as **changes: object, a deliberate bag
    # of replacements (see shapes_for_tests.make_request, S1-M2-T6).
    return dataclasses.replace(base, **changes)  # type: ignore[arg-type]


def test_hidden_quote_makes_value_unsure() -> None:
    # Promise test: values resting on hidden text are unsure (Spec 11).
    unreadable = UnreadableSpans(hidden=(Span(start=5, end=8),), undecodable=())
    verdicts = number_verdicts(PAYMENT_DAYS, value(), unreadable)
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.UNSURE
    assert verdicts[0].reasons == (ReasonCode.HIDDEN_TEXT,)
    assert verdicts[0].readable_value is None


def test_undecodable_quote_makes_value_unsure() -> None:
    unreadable = UnreadableSpans(hidden=(), undecodable=(Span(start=5, end=8),))
    verdicts = number_verdicts(PAYMENT_DAYS, value(), unreadable)
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.UNSURE
    assert verdicts[0].reasons == (ReasonCode.UNDECODABLE_TEXT,)


def test_quote_touching_hidden_at_its_end_is_readable() -> None:
    # Half-open spans: 0..10 and 10..12 share no code point.
    unreadable = UnreadableSpans(hidden=(Span(start=10, end=12),), undecodable=())
    verdicts = number_verdicts(PAYMENT_DAYS, value(), unreadable)
    assert verdicts[0].level is not Level.UNSURE


def test_unplaced_quote_keeps_its_level() -> None:
    # An unplaced quote keeps its label (Rule 3, ADR 0012).
    base_verdicts = number_verdicts(PAYMENT_DAYS, value(), NO_HIDDEN)
    unplaced_evidence = Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId("c1.s1"),),
        quote=Span(start=0, end=10),
        placed=False,
    )
    unplaced = number_verdicts(PAYMENT_DAYS, value(evidence=unplaced_evidence), NO_HIDDEN)
    assert unplaced[0].level is base_verdicts[0].level
    assert unplaced[0].reasons == base_verdicts[0].reasons


def test_missing_quote_is_unsure() -> None:
    # A found clause with no confirmed quote and no other reason is
    # unsure with quote_not_confirmed (Rule 3, question 16b).
    verdicts = number_verdicts(PAYMENT_DAYS, value(evidence=None), NO_HIDDEN)
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.UNSURE
    assert verdicts[0].reasons == (ReasonCode.QUOTE_NOT_CONFIRMED,)


def test_reason_on_value_makes_it_unsure() -> None:
    # Rule 5 decided 14 Nov 2026: a reason the checker cannot resolve
    # makes the value unsure.
    verdicts = number_verdicts(
        PAYMENT_DAYS,
        value(reasons=(ReasonCode.OTHER_START_POINT,)),
        NO_HIDDEN,
    )
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.UNSURE


def test_range_gives_two_verdicts() -> None:
    # A range counts as two values, so Rule 4 applies (Rule 6).
    verdicts = number_verdicts(
        PAYMENT_DAYS, value(number=Decimal(6), range_high=Decimal(9)), NO_HIDDEN
    )
    assert len(verdicts) == 2
    assert all(verdict.reasons == (ReasonCode.RANGE,) for verdict in verdicts)
    assert [verdict.readable_value for verdict in verdicts] == ["6", "9"]


def test_unlimited_is_walk_away_when_lower_is_better() -> None:
    # Unlimited is the worst value when lower is better (Rule 1).
    verdicts = number_verdicts(PAYMENT_DAYS, value(unlimited=True), NO_HIDDEN)
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.WALK_AWAY
    assert verdicts[0].readable_value == "unlimited"
    assert verdicts[0].reasons == ()


def test_unlimited_is_unsure_when_higher_is_better() -> None:
    # Unlimited when higher is better is unclear, not walk-away (16k).
    verdicts = number_verdicts(DEPOSIT_PERCENT, value(unlimited=True), NO_HIDDEN)
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.UNSURE
    assert verdicts[0].readable_value is None
    assert verdicts[0].reasons == (ReasonCode.UNLIMITED_UNCLEAR,)


def test_business_days_are_unsure() -> None:
    # Business days never convert (Rule 6).
    verdicts = number_verdicts(PAYMENT_DAYS, value(unit_as_written="business days"), NO_HIDDEN)
    assert len(verdicts) == 1
    assert verdicts[0].level is Level.UNSURE
    assert verdicts[0].reasons == (ReasonCode.BUSINESS_DAYS,)


def judged(**changes: object) -> JudgedLevel:
    """A judged acceptable level on clause c10, with any field replaced."""

    base = JudgedLevel(
        position_id=PositionId("10"),
        clause_id=ClauseId("c10"),
        evidence=Evidence(
            clause_id=ClauseId("c10"),
            sentence_ids=(SentenceId("c10.s1"),),
            quote=Span(start=0, end=10),
            placed=True,
        ),
        level=Level.ACCEPTABLE,
    )
    # The plan fixes this signature as **changes: object, a deliberate bag
    # of replacements (see shapes_for_tests.make_request, S1-M2-T6).
    return dataclasses.replace(base, **changes)  # type: ignore[arg-type]


def test_yes_gives_yes_level() -> None:
    verdict = yes_no_verdict(PAID_IF_CANCELLED, value(answer=Answer.YES), NO_HIDDEN)
    assert verdict.level is Level.PREFERRED
    assert verdict.readable_value == "yes"
    assert verdict.reasons == ()


def test_no_unclear_and_missing_give_no_level() -> None:
    # Rule 2: "No" equals "missing" (and "unclear").
    for answer in (Answer.NO, Answer.UNCLEAR, Answer.MISSING):
        verdict = yes_no_verdict(PAID_IF_CANCELLED, value(answer=answer), NO_HIDDEN)
        assert verdict.level is Level.WALK_AWAY, answer
        assert verdict.readable_value == answer.value


def test_conditional_yes_is_unsure() -> None:
    # A conditional yes gives unsure, with the condition quoted (Rule 2).
    verdict = yes_no_verdict(PAID_IF_CANCELLED, value(answer=Answer.CONDITIONAL_YES), NO_HIDDEN)
    assert verdict.level is Level.UNSURE
    assert verdict.reasons == (ReasonCode.CONDITIONAL_YES,)
    assert verdict.readable_value is None


def test_hidden_yes_is_unsure() -> None:
    # Rule 9: a value whose quote includes hidden text becomes unsure.
    unreadable = UnreadableSpans(hidden=(Span(start=5, end=8),), undecodable=())
    verdict = yes_no_verdict(PAID_IF_CANCELLED, value(answer=Answer.YES), unreadable)
    assert verdict.level is Level.UNSURE
    assert verdict.reasons == (ReasonCode.HIDDEN_TEXT,)


def test_judged_level_is_kept() -> None:
    verdict = words_verdict(judged(), NO_HIDDEN)
    assert verdict.level is Level.ACCEPTABLE
    assert verdict.readable_value == "acceptable"
    assert verdict.reasons == ()


def test_judged_unsure_has_a_reason() -> None:
    # The AI answering unsure is unsure with judged_unsure (16d).
    verdict = words_verdict(judged(level=Level.UNSURE), NO_HIDDEN)
    assert verdict.level is Level.UNSURE
    assert verdict.reasons == (ReasonCode.JUDGED_UNSURE,)
    assert verdict.readable_value is None


def test_hidden_judged_level_is_unsure() -> None:
    unreadable = UnreadableSpans(hidden=(Span(start=5, end=8),), undecodable=())
    verdict = words_verdict(judged(), unreadable)
    assert verdict.level is Level.UNSURE
    assert verdict.reasons == (ReasonCode.HIDDEN_TEXT,)


def test_empty_raises() -> None:
    with pytest.raises(ValueError, match="no values to combine"):
        combine_rule_4(())


def _readable(clause: str, readable: str, level: Level) -> ValueVerdict:
    return ValueVerdict(
        clause_id=ClauseId(clause),
        level=level,
        reasons=(),
        evidence=None,
        readable_value=readable,
    )


def test_clauses_that_disagree() -> None:
    # Clauses that give different values: every one appears with
    # "These clauses disagree" (Rule 4, question 16f).
    verdicts = (
        _readable("c1", "12", Level.PREFERRED),
        _readable("c2", "6", Level.PREFERRED),
        _readable("c2", "9", Level.ACCEPTABLE),
    )
    level, reasons = combine_rule_4(verdicts)
    assert level is Level.ACCEPTABLE
    assert ReasonCode.CLAUSES_DISAGREE in reasons


def test_same_value_in_two_clauses_agrees() -> None:
    verdicts = (
        _readable("c1", "30", Level.ACCEPTABLE),
        _readable("c2", "30", Level.ACCEPTABLE),
    )
    level, reasons = combine_rule_4(verdicts)
    assert level is Level.ACCEPTABLE
    assert ReasonCode.CLAUSES_DISAGREE not in reasons


def test_range_in_one_clause_agrees() -> None:
    # A range inside one clause is not a disagreement (Rule 4, 16f).
    verdicts = (
        _readable("c1", "6", Level.PREFERRED),
        _readable("c1", "9", Level.ACCEPTABLE),
    )
    level, reasons = combine_rule_4(verdicts)
    assert level is Level.ACCEPTABLE
    assert ReasonCode.CLAUSES_DISAGREE not in reasons


@given(verdict_list=st.lists(value_verdicts(), min_size=1, max_size=6), data=st.data())
def test_order_never_changes_the_result(
    verdict_list: list[ValueVerdict], data: st.DataObject
) -> None:
    shuffled = data.draw(st.permutations(verdict_list))
    assert combine_rule_4(tuple(shuffled)) == combine_rule_4(tuple(verdict_list))


@given(
    verdict_list=st.lists(value_verdicts(), min_size=0, max_size=5),
    walk_away=value_verdicts().filter(lambda verdict: verdict.level is Level.WALK_AWAY),
)
def test_readable_walk_away_wins(verdict_list: list[ValueVerdict], walk_away: ValueVerdict) -> None:
    # Promise test: every planted walk-away gets walk-away (Spec 11).
    level, _ = combine_rule_4((*verdict_list, walk_away))
    assert level is Level.WALK_AWAY


@given(verdict_list=st.lists(value_verdicts(), min_size=1, max_size=6))
def test_unsure_always_has_a_reason(verdict_list: list[ValueVerdict]) -> None:
    # Never guess: an unsure label names a reason (Spec 5).
    level, reasons = combine_rule_4(tuple(verdict_list))
    if level is Level.UNSURE:
        assert any(reason in UNSURE_REASONS for reason in reasons)


def _input(
    position: Position,
    match: MatchResult,
    **changes: object,
) -> LabelInput:
    fields: dict[str, object] = {
        "position": position,
        "match": match,
        "values": (),
        "judged": (),
        "outside_documents": (),
    }
    fields.update(changes)
    return LabelInput(**fields)  # type: ignore[arg-type]


DAYS_POSITION = Position(
    id=PositionId("1"),
    topic="Days until I'm paid, from invoice date",
    type=PositionType.NUMBER,
    rule=PAYMENT_DAYS,
    missing_level=Level.UNSURE,
    why_note=None,
)
DEPOSIT_POSITION = Position(
    id=PositionId("2"),
    topic="Upfront deposit",
    type=PositionType.NUMBER,
    rule=DEPOSIT_PERCENT,
    missing_level=Level.WALK_AWAY,
    why_note=None,
)
WORDS_POSITION = Position(
    id=PositionId("10"),
    topic="My liability is capped",
    type=PositionType.WORDS,
    rule=WordsRule(
        preferred="At most the fees paid",
        acceptable="Above the fees, up to 2x fees",
        walk_away="Above 2x fees, a fixed sum, or uncapped",
    ),
    missing_level=Level.WALK_AWAY,
    why_note=None,
)

_TABLE_ROWS = label_rule_cases()
_TABLE_IDS = [case.id for case in _TABLE_ROWS]


@pytest.mark.parametrize("case", _TABLE_ROWS, ids=_TABLE_IDS)
def test_label_rules_table(case: LabelCase) -> None:
    label = label_position(case.label_input, case.unreadable)
    assert label.level is case.level, case.id
    assert frozenset(label.reasons) == case.reasons, case.id
    assert label.written_by is case.written_by, case.id


def test_every_rule_has_rows() -> None:
    rules = {case.rule for case in _TABLE_ROWS}
    for rule in (
        "rule1",
        "rule2",
        "rule3",
        "rule4",
        "rule5",
        "rule6",
        "rule7",
        "rule9",
        "rule10",
    ):
        assert rule in rules


@given(position=positions())
def test_failed_call_never_gives_a_missing_level(position: Position) -> None:
    # A failed call gives unsure, never the missing level (system design 8.2).
    label = label_position(_input(position, CallFailed(code="model_reply_invalid")), NO_HIDDEN)
    assert label.level is Level.UNSURE
    assert label.reasons == (ReasonCode.REPLY_BROKEN_TWICE,)


def test_words_label_is_written_by_ai() -> None:
    label = label_position(
        _input(
            WORDS_POSITION,
            MatchFound(position_id=PositionId("10"), clause_ids=(ClauseId("c10"),)),
            judged=(judged(),),
        ),
        NO_HIDDEN,
    )
    assert label.written_by is WrittenBy.AI
    assert label.level is Level.ACCEPTABLE


def test_missing_words_label_is_written_by_code() -> None:
    # A label a rule produced on a words position is written by code.
    label = label_position(
        _input(
            WORDS_POSITION,
            NothingFound(position_id=PositionId("10"), searches=()),
        ),
        NO_HIDDEN,
    )
    assert label.written_by is WrittenBy.CODE
    assert label.level is Level.WALK_AWAY


def test_rule_10_keeps_a_walk_away() -> None:
    # A walk-away the app found in a clause stays walk-away and gets no
    # extra reason (Rule 10).
    label = label_position(
        _input(
            DAYS_POSITION,
            MatchFound(position_id=PositionId("1"), clause_ids=(ClauseId("c1"),)),
            values=(value(),),
            outside_documents=(
                OutsideDocument(name="Master Agreement", evidence=Span(start=0, end=0)),
            ),
        ),
        NO_HIDDEN,
    )
    assert label.level is Level.WALK_AWAY
    assert label.reasons == ()


def test_rule_10_makes_a_missing_walk_away_unsure() -> None:
    # A Missing label whose missing level is walk-away becomes unsure (16h).
    label = label_position(
        _input(
            DEPOSIT_POSITION,
            NothingFound(position_id=PositionId("2"), searches=()),
            outside_documents=(
                OutsideDocument(name="Master Agreement", evidence=Span(start=0, end=0)),
            ),
        ),
        NO_HIDDEN,
    )
    assert label.level is Level.UNSURE
    assert label.reasons == (ReasonCode.UNLOADED_DOCUMENT,)


def test_words_label_turned_unsure_is_written_by_code() -> None:
    # A words label a rule turned unsure is written by code (16i).
    label = label_position(
        _input(
            WORDS_POSITION,
            MatchFound(position_id=PositionId("10"), clause_ids=(ClauseId("c10"),)),
            judged=(judged(),),
            outside_documents=(
                OutsideDocument(name="Master Agreement", evidence=Span(start=0, end=0)),
            ),
        ),
        NO_HIDDEN,
    )
    assert label.level is Level.UNSURE
    assert label.reasons == (ReasonCode.UNLOADED_DOCUMENT,)
    assert label.written_by is WrittenBy.CODE


def test_judged_words_label_is_written_by_ai() -> None:
    label = label_position(
        _input(
            WORDS_POSITION,
            MatchFound(position_id=PositionId("10"), clause_ids=(ClauseId("c10"),)),
            judged=(judged(),),
        ),
        NO_HIDDEN,
    )
    assert label.written_by is WrittenBy.AI


def test_position_mismatch_raises() -> None:
    with pytest.raises(ValueError, match="another position"):
        label_position(
            _input(
                DAYS_POSITION,
                MatchFound(position_id=PositionId("2"), clause_ids=()),
            ),
            NO_HIDDEN,
        )
