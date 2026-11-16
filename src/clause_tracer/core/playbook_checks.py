"""The playbook checks of Spec 4.1 (system design 15.1, ADR 0005 14 Nov 2026).

check_playbook is pure: it takes a playbook and returns its problems,
in playbook order, and within one position in PlaybookProblemCode
member order. Stages 6 and 12 share these checks.
"""

from clause_tracer.core.checks import PlaybookProblem
from clause_tracer.core.enums import (
    Direction,
    Level,
    PlaybookProblemCode,
    PositionType,
    Unit,
)
from clause_tracer.core.ids import PositionId
from clause_tracer.core.levels import is_better
from clause_tracer.core.playbook import NumberRule, Playbook, Position, WordsRule, YesNoRule


def _duplicate_problem(position: Position) -> PlaybookProblem:
    return PlaybookProblem(
        position_id=position.id,
        code=PlaybookProblemCode.DUPLICATE_POSITION_ID,
    )


def _mismatch_problem(position: Position) -> PlaybookProblem:
    return PlaybookProblem(
        position_id=position.id,
        code=PlaybookProblemCode.RULE_TYPE_MISMATCH,
    )


def _number_problems(position: Position, rule: NumberRule) -> list[PlaybookProblem]:
    negative = rule.preferred_limit < 0 or rule.acceptable_limit < 0
    over_100 = rule.unit is Unit.PERCENT and (
        rule.preferred_limit > 100 or rule.acceptable_limit > 100
    )
    if rule.direction is Direction.LOWER_IS_BETTER:
        stricter = rule.preferred_limit < rule.acceptable_limit
    else:
        stricter = rule.preferred_limit > rule.acceptable_limit
    problems: list[PlaybookProblem] = []
    if negative:
        problems.append(
            PlaybookProblem(position_id=position.id, code=PlaybookProblemCode.LIMIT_NEGATIVE)
        )
    if over_100:
        problems.append(
            PlaybookProblem(position_id=position.id, code=PlaybookProblemCode.PERCENT_OVER_100)
        )
    if not stricter:
        problems.append(
            PlaybookProblem(position_id=position.id, code=PlaybookProblemCode.LIMITS_NOT_STRICTER)
        )
    return problems


def _yes_no_problems(position: Position, rule: YesNoRule) -> list[PlaybookProblem]:
    a_level_is_unsure = rule.yes_level is Level.UNSURE or rule.no_level is Level.UNSURE
    missing_matches_no = position.missing_level == rule.no_level
    problems: list[PlaybookProblem] = []
    if a_level_is_unsure:
        problems.append(
            PlaybookProblem(position_id=position.id, code=PlaybookProblemCode.YES_NO_LEVEL_UNSURE)
        )
    elif not is_better(rule.yes_level, rule.no_level):
        problems.append(
            PlaybookProblem(position_id=position.id, code=PlaybookProblemCode.YES_NOT_BETTER)
        )
    if not missing_matches_no:
        problems.append(
            PlaybookProblem(
                position_id=position.id, code=PlaybookProblemCode.MISSING_LEVEL_NOT_NO_LEVEL
            )
        )
    return problems


def _words_problems(position: Position, rule: WordsRule) -> list[PlaybookProblem]:
    texts = (rule.preferred, rule.acceptable, rule.walk_away)
    a_text_is_empty = any(not text.strip() for text in texts)
    problems: list[PlaybookProblem] = []
    if a_text_is_empty:
        problems.append(
            PlaybookProblem(position_id=position.id, code=PlaybookProblemCode.LEVEL_TEXT_EMPTY)
        )
    return problems


def check_playbook(playbook: Playbook) -> tuple[PlaybookProblem, ...]:
    """The problems of one playbook; an empty result means it passes (Spec 4.1)."""

    problems: list[PlaybookProblem] = []
    seen_ids: set[PositionId] = set()
    for position in playbook.positions:
        if position.id in seen_ids:
            problems.append(_duplicate_problem(position))
        seen_ids.add(position.id)
        if position.type is PositionType.NUMBER:
            if not isinstance(position.rule, NumberRule):
                problems.append(_mismatch_problem(position))
                continue
            problems.extend(_number_problems(position, position.rule))
        elif position.type is PositionType.YES_NO:
            if not isinstance(position.rule, YesNoRule):
                problems.append(_mismatch_problem(position))
                continue
            problems.extend(_yes_no_problems(position, position.rule))
        else:
            if not isinstance(position.rule, WordsRule):
                problems.append(_mismatch_problem(position))
                continue
            problems.extend(_words_problems(position, position.rule))
    return tuple(problems)
