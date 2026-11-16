"""The label rules of Spec 5.

Code picks labels, the same way every time. The principle is never
guess: when code cannot be sure, the label is unsure, the reason is
named, and the user is shown the clause. A value that carries an
unsure reason never counts as readable for Rule 4.
"""

import math
from decimal import Decimal
from fractions import Fraction

from clause_tracer.core.enums import (
    UNSURE_REASONS,
    Answer,
    Direction,
    Level,
    PositionType,
    ReasonCode,
    Unit,
    WrittenBy,
)
from clause_tracer.core.ids import ClauseId, PositionId
from clause_tracer.core.levels import sort_reasons, spans_overlap, worst_level
from clause_tracer.core.playbook import NumberRule, Playbook, WordsRule, YesNoRule
from clause_tracer.core.results import (
    CallFailed,
    CheckedValue,
    Evidence,
    JudgedLevel,
    LabelInput,
    MatchFound,
    MatchUnconfirmed,
    NothingFound,
    ToolLabel,
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
    return _verdict_for(value.clause_id, value.evidence, level, reasons, readable_value)


def _verdict_for(
    clause_id: ClauseId,
    evidence: Evidence | None,
    level: Level,
    reasons: list[ReasonCode],
    readable_value: str | None,
) -> ValueVerdict:
    return ValueVerdict(
        clause_id=clause_id,
        level=level,
        reasons=sort_reasons(reasons),
        evidence=evidence,
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
        # A total of 0 counts as no total (Rule 6, question 16e). The
        # clause gave a range even so (decided 16 Nov 2026).
        if value.range_high is not None:
            reasons.append(ReasonCode.RANGE)
        reasons.append(ReasonCode.AMOUNT_WITHOUT_TOTAL)
        return []
    computed = Fraction(amount) / Fraction(total) * 100
    if value.number is None:
        if value.range_high is not None:
            reasons.append(ReasonCode.RANGE)
        return [computed]
    converted = _converted(value.number, value.unit_as_written, rule)
    if isinstance(converted, ReasonCode):
        reasons.append(converted)
        # The computed percentage still counts; the range says itself
        # even when the number did not convert (decided 16 Nov 2026).
        if value.range_high is not None:
            reasons.append(ReasonCode.RANGE)
        return [computed]
    if _half_up_to_whole(computed) != _half_up_to_whole(converted):
        reasons.append(ReasonCode.AMOUNT_PERCENT_DISAGREE)
        numbers = [computed, converted]
    else:
        numbers = [computed]
    if value.range_high is not None:
        reasons.append(ReasonCode.RANGE)
        # The range end is a last number, not compared with the
        # computed percentage; a failed conversion adds no reason.
        converted_high = _converted(value.range_high, value.unit_as_written, rule)
        if not isinstance(converted_high, ReasonCode):
            numbers.append(converted_high)
    return numbers


def _plain_numbers(
    rule: NumberRule, value: CheckedValue, reasons: list[ReasonCode], number: Decimal
) -> list[Fraction]:
    converted = _converted(number, value.unit_as_written, rule)
    if isinstance(converted, ReasonCode):
        reasons.append(converted)
        # The clause gave a range, so the reason says so, even when the
        # first number did not convert (decided 16 Nov 2026).
        if value.range_high is not None:
            reasons.append(ReasonCode.RANGE)
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


def yes_no_verdict(
    rule: YesNoRule, value: CheckedValue, unreadable: UnreadableSpans
) -> ValueVerdict:
    """The verdict of one yes/no value (Rule 2; the quote check, Rule 9)."""

    reasons = list(value.reasons) + list(evidence_reasons(value.evidence, unreadable))
    if value.answer is None:
        if not _has_unsure_reason(reasons):
            reasons.append(ReasonCode.NO_VALUE)
        # No answer is unsure either way.
        return _verdict(value, Level.UNSURE, reasons, None)
    if value.answer is Answer.CONDITIONAL_YES:
        reasons.append(ReasonCode.CONDITIONAL_YES)
    if _has_unsure_reason(reasons):
        return _verdict(value, Level.UNSURE, reasons, None)
    # "No" equals "missing" (and "unclear"): all three take the no level.
    level = rule.yes_level if value.answer is Answer.YES else rule.no_level
    return _verdict(value, level, reasons, value.answer.value)


def words_verdict(judged: JudgedLevel, unreadable: UnreadableSpans) -> ValueVerdict:
    """The verdict of one AI judgement for a words position (Rules 4 and 9)."""

    reasons = list(evidence_reasons(judged.evidence, unreadable))
    if judged.level is Level.UNSURE:
        # The AI could not judge it (question 16d).
        reasons.append(ReasonCode.JUDGED_UNSURE)
    if _has_unsure_reason(reasons):
        return _verdict_for(judged.clause_id, judged.evidence, Level.UNSURE, reasons, None)
    return _verdict_for(
        judged.clause_id, judged.evidence, judged.level, reasons, judged.level.value
    )


def combine_rule_4(verdicts: tuple[ValueVerdict, ...]) -> tuple[Level, tuple[ReasonCode, ...]]:
    """Rule 4: mixed values, in this order (Spec 5).

    The level is walk-away if any readable value gives walk-away, else
    unsure if any value is unsure, else the worst level. Clauses whose
    readable values differ add CLAUSES_DISAGREE. The reasons of every
    value are kept, at every level.
    """

    if not verdicts:
        raise ValueError("no values to combine")
    readable_by_clause: dict[ClauseId, set[str]] = {}
    for verdict in verdicts:
        if verdict.readable_value is not None:
            readable_by_clause.setdefault(verdict.clause_id, set()).add(verdict.readable_value)
    keys = {"|".join(sorted(values)) for values in readable_by_clause.values()}
    clauses_disagree = len(keys) >= 2
    levels = [verdict.level for verdict in verdicts]
    if Level.WALK_AWAY in levels:
        level = Level.WALK_AWAY
    elif Level.UNSURE in levels:
        level = Level.UNSURE
    else:
        level = worst_level(levels)
    reasons = [reason for verdict in verdicts for reason in verdict.reasons]
    if clauses_disagree:
        reasons.append(ReasonCode.CLAUSES_DISAGREE)
    return level, sort_reasons(reasons)


def _check_references(item: LabelInput) -> None:
    """Raise ValueError when a part of the input does not belong to its position."""

    position = item.position
    if not isinstance(item.match, CallFailed) and item.match.position_id != position.id:
        raise ValueError(f"match names another position, not {position.id}")
    for value in item.values:
        if value.position_id != position.id:
            raise ValueError(f"a value names another position, not {position.id}")
    for judged in item.judged:
        if judged.position_id != position.id:
            raise ValueError(f"a judged level names another position, not {position.id}")
    if position.type is PositionType.WORDS and item.values:
        raise ValueError(f"position {position.id} is a words position but holds values")
    if position.type is not PositionType.WORDS and item.judged:
        raise ValueError(f"position {position.id} takes values, not judged levels")


def label_position(item: LabelInput, unreadable: UnreadableSpans) -> ToolLabel:
    """The label of one position: Rules 3, 4, 7 and 10 (Spec 5)."""

    _check_references(item)
    position = item.position
    number_rule: NumberRule | None = None
    yes_no_rule: YesNoRule | None = None
    if position.type is PositionType.NUMBER:
        if not isinstance(position.rule, NumberRule):
            raise ValueError(f"position {position.id} is a number with another kind of rule")
        number_rule = position.rule
    elif position.type is PositionType.YES_NO:
        if not isinstance(position.rule, YesNoRule):
            raise ValueError(f"position {position.id} is a yes/no with another kind of rule")
        yes_no_rule = position.rule
    elif not isinstance(position.rule, WordsRule):
        raise ValueError(f"position {position.id} is a words position with another rule")
    match = item.match
    evidence: list[Evidence] = []
    if isinstance(match, CallFailed):
        # A failed call never passes as "nothing found" (I4, system design 8.2).
        level = Level.UNSURE
        reasons: list[ReasonCode] = [ReasonCode.REPLY_BROKEN_TWICE]
    elif isinstance(match, NothingFound):
        # Rule 7: a yes/no position goes to its no level (Spec 4.1).
        level = yes_no_rule.no_level if yes_no_rule is not None else position.missing_level
        reasons = []
    elif isinstance(match, MatchUnconfirmed):
        # The searches disagree: unsure, the clause to read is named (ADR 0012).
        level = Level.UNSURE
        reasons = [ReasonCode.MATCH_UNCONFIRMED]
    else:
        verdicts: list[ValueVerdict] = []
        if number_rule is not None:
            for value in item.values:
                verdicts.extend(number_verdicts(number_rule, value, unreadable))
        elif yes_no_rule is not None:
            for value in item.values:
                verdicts.append(yes_no_verdict(yes_no_rule, value, unreadable))
        else:
            for judged in item.judged:
                verdicts.append(words_verdict(judged, unreadable))
        if not verdicts:
            # A found clause with no value and no answer (question 16c).
            level = Level.UNSURE
            reasons = [ReasonCode.NO_VALUE]
        else:
            level, combined = combine_rule_4(tuple(verdicts))
            reasons = list(combined)
            for verdict in verdicts:
                if verdict.evidence is not None and verdict.evidence not in evidence:
                    evidence.append(verdict.evidence)
    # Rule 10: an unloaded document in the trail makes the label unsure,
    # except a walk-away Rule 4 step 1 already gave (question 16h).
    found_walk_away = isinstance(match, MatchFound) and level is Level.WALK_AWAY
    if item.outside_documents and not found_walk_away:
        level = Level.UNSURE
        reasons.append(ReasonCode.UNLOADED_DOCUMENT)
    # Only a level the AI actually judged is written by AI, and drawn in
    # pencil (ADR 0002, question 16i).
    if (
        position.type is PositionType.WORDS
        and isinstance(match, MatchFound)
        and level is not Level.UNSURE
    ):
        written_by = WrittenBy.AI
    else:
        written_by = WrittenBy.CODE
    return ToolLabel(
        position_id=position.id,
        level=level,
        reasons=sort_reasons(reasons),
        evidence=tuple(evidence),
        written_by=written_by,
    )


def label_all(
    playbook: Playbook,
    inputs: tuple[LabelInput, ...],
    unreadable: UnreadableSpans,
) -> tuple[ToolLabel, ...]:
    """Every position of the playbook, in playbook order (Spec 5, Rule 3).

    Raises ValueError when a position has no input, when two inputs name
    one position, or when an input names a position not in the playbook.
    """

    playbook_ids = {position.id for position in playbook.positions}
    by_position: dict[PositionId, LabelInput] = {}
    for item in inputs:
        if item.position.id in by_position:
            raise ValueError(f"two inputs name one position: {item.position.id}")
        if item.position.id not in playbook_ids:
            raise ValueError(f"input names a position not in the playbook: {item.position.id}")
        by_position[item.position.id] = item
    labels: list[ToolLabel] = []
    for position in playbook.positions:
        found = by_position.get(position.id)
        if found is None:
            raise ValueError(f"position {position.id} has no input")
        labels.append(label_position(found, unreadable))
    return tuple(labels)
