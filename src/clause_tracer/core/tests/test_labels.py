"""Tests for the label rules of Spec 5 (S1-M3-T13 onwards)."""

import dataclasses
from decimal import Decimal

from clause_tracer.core import (
    CheckedValue,
    ClauseId,
    Direction,
    Evidence,
    Level,
    NumberRule,
    PositionId,
    ReasonCode,
    SentenceId,
    Span,
    Unit,
    UnreadableSpans,
    number_verdicts,
)

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
