"""The label rules of Spec 5.

Code picks labels, the same way every time. The principle is never
guess: when code cannot be sure, the label is unsure, the reason is
named, and the user is shown the clause. A value that carries an
unsure reason never counts as readable for Rule 4.
"""

import math
from decimal import Decimal
from fractions import Fraction

from clause_tracer.core.enums import UNSURE_REASONS, Direction, Level, ReasonCode, Unit
from clause_tracer.core.levels import sort_reasons, spans_overlap
from clause_tracer.core.playbook import NumberRule
from clause_tracer.core.results import (
    CheckedValue,
    Evidence,
    UnreadableSpans,
    ValueVerdict,
)
from clause_tracer.core.units import convert_to_unit


def evidence_reasons(
    evidence: Evidence | None, unreadable: UnreadableSpans
) -> tuple[ReasonCode, ...]:
    """The reasons the evidence itself gives; an unplaced quote keeps its label."""

    if evidence is None:
        # A found clause with no confirmed quote (Rule 3, question 16b).
        return (ReasonCode.QUOTE_NOT_CONFIRMED,)
    reasons: list[ReasonCode] = []
    if any(spans_overlap(evidence.quote, hidden) for hidden in unreadable.hidden):
        reasons.append(ReasonCode.HIDDEN_TEXT)
    if any(spans_overlap(evidence.quote, span) for span in unreadable.undecodable):
        reasons.append(ReasonCode.UNDECODABLE_TEXT)
    return tuple(reasons)


def level_for_limits(rule: NumberRule, number: Fraction) -> Level:
    """Rule 1: limits, not ranges. Unsure has no place here."""

    if rule.direction is Direction.LOWER_IS_BETTER:
        at_preferred = number <= rule.preferred_limit
        at_acceptable = number <= rule.acceptable_limit
    else:
        at_preferred = number >= rule.preferred_limit
        at_acceptable = number >= rule.acceptable_limit
    if at_preferred:
        return Level.PREFERRED
    if at_acceptable:
        return Level.ACCEPTABLE
    return Level.WALK_AWAY


def _half_up_to_whole(number: Fraction) -> int:
    """Round half up to a whole number (question 16e)."""

    return math.floor(number + Fraction(1, 2))


def _verdict(
    value: CheckedValue, level: Level, reasons: list[ReasonCode], readable_value: str | None
) -> ValueVerdict:
    return ValueVerdict(
        clause_id=value.clause_id,
        level=level,
        reasons=sort_reasons(reasons),
        evidence=value.evidence,
        readable_value=readable_value,
    )


def _has_unsure_reason(reasons: list[ReasonCode]) -> bool:
    return any(reason in UNSURE_REASONS for reason in reasons)


def _converted(
    number: Decimal, unit_as_written: str | None, rule: NumberRule
) -> Fraction | ReasonCode:
    return convert_to_unit(number, unit_as_written, rule.unit)


def _numbers_for(
    rule: NumberRule, value: CheckedValue, reasons: list[ReasonCode]
) -> list[Fraction]:
    """The numbers one value stands for, in order; fills reasons as a side effect."""

    if value.unlimited:
        if rule.direction is Direction.HIGHER_IS_BETTER:
            # Unlimited when higher is better is unclear (Rule 1, 16k).
            reasons.append(ReasonCode.UNLIMITED_UNCLEAR)
        return []
    if rule.unit is Unit.PERCENT and value.amount is not None:
        return _percent_amount_numbers(rule, value, reasons, value.amount, value.total)
    if value.number is not None:
        return _plain_numbers(rule, value, reasons, value.number)
    if not _has_unsure_reason(reasons):
        # No number and no answer (question 16c).
        reasons.append(ReasonCode.NO_VALUE)
    return []


def _percent_amount_numbers(
    rule: NumberRule,
    value: CheckedValue,
    reasons: list[ReasonCode],
    amount: Decimal,
    total: Decimal | None,
) -> list[Fraction]:
    if total is None or total <= 0:
        # A total of 0 counts as no total (Rule 6, question 16e).
        reasons.append(ReasonCode.AMOUNT_WITHOUT_TOTAL)
        return []
    computed = Fraction(amount) / Fraction(total) * 100
    if value.number is None:
        return [computed]
    converted = _converted(value.number, value.unit_as_written, rule)
    if isinstance(converted, ReasonCode):
        reasons.append(converted)
        return [computed]
    if _half_up_to_whole(computed) != _half_up_to_whole(converted):
        reasons.append(ReasonCode.AMOUNT_PERCENT_DISAGREE)
        return [computed, converted]
    return [computed]


def _plain_numbers(
    rule: NumberRule, value: CheckedValue, reasons: list[ReasonCode], number: Decimal
) -> list[Fraction]:
    converted = _converted(number, value.unit_as_written, rule)
    if isinstance(converted, ReasonCode):
        reasons.append(converted)
        return []
    numbers = [converted]
    if value.range_high is not None:
        converted_high = _converted(value.range_high, value.unit_as_written, rule)
        if not isinstance(converted_high, ReasonCode):
            numbers.append(converted_high)
        reasons.append(ReasonCode.RANGE)
    return numbers


def number_verdicts(
    rule: NumberRule, value: CheckedValue, unreadable: UnreadableSpans
) -> tuple[ValueVerdict, ...]:
    """The verdicts of one number value, before Rule 4 combines them (Spec 5)."""

    reasons = list(value.reasons) + list(evidence_reasons(value.evidence, unreadable))
    if value.vague:
        reasons.append(ReasonCode.VAGUE_WORDING)
    numbers = _numbers_for(rule, value, reasons)
    if _has_unsure_reason(reasons):
        return (_verdict(value, Level.UNSURE, reasons, None),)
    if value.unlimited:
        # Unlimited is the worst value when lower is better (Rule 1);
        # the higher-is-better case left in the unsure step above.
        return (_verdict(value, Level.WALK_AWAY, reasons, "unlimited"),)
    return tuple(
        _verdict(value, level_for_limits(rule, number), reasons, str(number)) for number in numbers
    )
