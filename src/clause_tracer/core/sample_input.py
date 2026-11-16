"""Read positions, playbooks and label inputs from the sample format.

The Spec 14.5 sample file and the label-rule owner table hold inputs,
not expected labels. This module parses data a caller has already read
(T1: pure; only __main__ and the tests read files). Every error is a
ValueError whose message names the offending key, so a wrong sample
fails loudly instead of being guessed at.
"""

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from clause_tracer.core.enums import Direction, Level, PositionType, Unit
from clause_tracer.core.ids import PlaybookId, PositionId
from clause_tracer.core.playbook import (
    NumberRule,
    Playbook,
    Position,
    WordsRule,
    YesNoRule,
)


def _get(data: Mapping[str, object], key: str, where: str) -> object:
    if key not in data:
        raise ValueError(f"{where}: missing key {key}")
    return data[key]


def _str_field(data: Mapping[str, object], key: str, where: str) -> str:
    value = _get(data, key, where)
    if not isinstance(value, str):
        raise ValueError(f"{where}: {key} must be a string")
    return value


def _bool_field(data: Mapping[str, object], key: str, where: str) -> bool:
    value = _get(data, key, where)
    if not isinstance(value, bool):
        raise ValueError(f"{where}: {key} must be a boolean")
    return value


def _enum_field[E: StrEnum](
    enum_type: type[E], data: Mapping[str, object], key: str, where: str
) -> E:
    value = _get(data, key, where)
    if isinstance(value, str):
        for member in enum_type:
            if value == member.value:
                return member
    names = ", ".join(member.value for member in enum_type)
    raise ValueError(f"{where}: {key} must be one of {names}")


def _decimal_field(data: Mapping[str, object], key: str, where: str) -> Decimal:
    value = _get(data, key, where)
    if isinstance(value, bool):
        raise ValueError(f"{where}: {key} must be a decimal number")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise ValueError(f"{where}: {key} must be a decimal number") from error
    raise ValueError(f"{where}: {key} must be a decimal number")


def _str_list_field(data: Mapping[str, object], key: str, where: str) -> list[str]:
    value = _get(data, key, where)
    if not isinstance(value, list):
        raise ValueError(f"{where}: {key} must be a list")
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{where}: {key} must be a list of strings")
    return value


def parse_position(data: Mapping[str, object], where: str) -> Position:
    """Read one position table of the sample format; a float limit raises."""

    position_id = PositionId(_str_field(data, "id", where))
    topic = _str_field(data, "topic", where)
    position_type = _enum_field(PositionType, data, "type", where)
    common = {"id", "topic", "type", "why_note"}
    if position_type is PositionType.NUMBER:
        allowed = common | {
            "unit",
            "direction",
            "preferred_limit",
            "acceptable_limit",
            "missing_level",
        }
        rule: NumberRule | YesNoRule | WordsRule = NumberRule(
            unit=_enum_field(Unit, data, "unit", where),
            direction=_enum_field(Direction, data, "direction", where),
            preferred_limit=_decimal_field(data, "preferred_limit", where),
            acceptable_limit=_decimal_field(data, "acceptable_limit", where),
        )
        missing_level = _enum_field(Level, data, "missing_level", where)
    elif position_type is PositionType.YES_NO:
        allowed = common | {"question", "yes_level", "no_level", "missing_level"}
        no_level = _enum_field(Level, data, "no_level", where)
        rule = YesNoRule(
            question=_str_field(data, "question", where),
            yes_level=_enum_field(Level, data, "yes_level", where),
            no_level=no_level,
        )
        if "missing_level" in data:
            missing_level = _enum_field(Level, data, "missing_level", where)
        else:
            missing_level = no_level
    else:
        allowed = common | {"preferred", "acceptable", "walk_away", "missing_level"}
        rule = WordsRule(
            preferred=_str_field(data, "preferred", where),
            acceptable=_str_field(data, "acceptable", where),
            walk_away=_str_field(data, "walk_away", where),
        )
        missing_level = _enum_field(Level, data, "missing_level", where)
    for key in data:
        if key not in allowed:
            raise ValueError(f"{where}: unknown key {key}")
    why_note: str | None = None
    if "why_note" in data:
        why_note = _str_field(data, "why_note", where)
    return Position(
        id=position_id,
        topic=topic,
        type=position_type,
        rule=rule,
        missing_level=missing_level,
        why_note=why_note,
    )


def parse_playbook(data: Mapping[str, object], *, schema_version: int) -> Playbook:
    """Read the [playbook] table of the sample format; customer_id stays None."""

    where = "playbook"
    allowed = {"id", "name", "side", "starter", "positions"}
    for key in data:
        if key not in allowed:
            raise ValueError(f"{where}: unknown key {key}")
    raw_positions = _get(data, "positions", where)
    if not isinstance(raw_positions, list):
        raise ValueError(f"{where}: positions must be a list of tables")
    positions = tuple(
        parse_position(entry, f"position {index}") for index, entry in enumerate(raw_positions)
    )
    return Playbook(
        id=PlaybookId(_str_field(data, "id", where)),
        schema_version=schema_version,
        name=_str_field(data, "name", where),
        side=_str_field(data, "side", where),
        customer_id=None,
        positions=positions,
        starter=_bool_field(data, "starter", where),
    )
