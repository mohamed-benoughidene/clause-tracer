"""Read positions, playbooks and label inputs from the sample format.

The Spec 14.5 sample file and the label-rule owner table hold inputs,
not expected labels. This module parses data a caller has already read
(T1: pure; only __main__ and the tests read files). Every error is a
ValueError whose message names the offending key, so a wrong sample
fails loudly instead of being guessed at.

Quote spans: the k-th value or judged table of one parse_label_inputs
call takes Span(start=k * 100, end=k * 100 + 10), in file order, so the
tests get stable evidence spans without a document.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from clause_tracer.core.enums import Answer, Direction, Level, PositionType, ReasonCode, Unit
from clause_tracer.core.ids import ClauseId, PlaybookId, PositionId, SentenceId
from clause_tracer.core.link_map import OutsideDocument
from clause_tracer.core.playbook import (
    NumberRule,
    Playbook,
    Position,
    WordsRule,
    YesNoRule,
)
from clause_tracer.core.results import (
    CallFailed,
    CheckedValue,
    Evidence,
    JudgedLevel,
    LabelInput,
    MatchFound,
    MatchResult,
    MatchUnconfirmed,
    NothingFound,
    UnreadableSpans,
)
from clause_tracer.core.wording import Span

_MATCH_KINDS = ("found", "nothing", "unconfirmed", "failed")
_QUOTE_CHOICES = ("confirmed", "unplaced", "none")
_ON_CHOICES = ("visible", "hidden", "undecodable")


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


def _enum_value[E: StrEnum](enum_type: type[E], value: object, key: str, where: str) -> E:
    if isinstance(value, str):
        for member in enum_type:
            if value == member.value:
                return member
    names = ", ".join(member.value for member in enum_type)
    raise ValueError(f"{where}: {key} must be one of {names}")


def _enum_field[E: StrEnum](
    enum_type: type[E], data: Mapping[str, object], key: str, where: str
) -> E:
    return _enum_value(enum_type, _get(data, key, where), key, where)


def _enum_list_field[E: StrEnum](
    enum_type: type[E], data: Mapping[str, object], key: str, where: str
) -> tuple[E, ...]:
    if key not in data:
        return ()
    value = _get(data, key, where)
    if not isinstance(value, list):
        raise ValueError(f"{where}: {key} must be a list")
    return tuple(_enum_value(enum_type, item, key, where) for item in value)


def _optional_bool_field(
    data: Mapping[str, object], key: str, where: str, default: bool = False
) -> bool:
    if key not in data:
        return default
    return _bool_field(data, key, where)


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


def _int_field(data: Mapping[str, object], key: str, where: str) -> int:
    value = _get(data, key, where)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{where}: {key} must be an integer")
    return value


def _optional_str_field(data: Mapping[str, object], key: str, where: str) -> str | None:
    if key not in data:
        return None
    return _str_field(data, key, where)


def _optional_decimal_field(data: Mapping[str, object], key: str, where: str) -> Decimal | None:
    if key not in data:
        return None
    return _decimal_field(data, key, where)


def _optional_enum_field[E: StrEnum](
    enum_type: type[E], data: Mapping[str, object], key: str, where: str
) -> E | None:
    if key not in data:
        return None
    return _enum_field(enum_type, data, key, where)


def _choice(value: object, choices: tuple[str, ...], key: str, where: str) -> str:
    if isinstance(value, str) and value in choices:
        return value
    names = ", ".join(choices)
    raise ValueError(f"{where}: {key} must be one of {names}")


def _table_list(data: Mapping[str, object], key: str, where: str) -> list[Mapping[str, object]]:
    value = _get(data, key, where)
    if not isinstance(value, list):
        raise ValueError(f"{where}: {key} must be a list of tables")
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"{where}: {key} must be a list of tables")
    return value


def _optional_table_list(
    data: Mapping[str, object], key: str, where: str
) -> list[Mapping[str, object]]:
    if key not in data:
        return []
    return _table_list(data, key, where)


def _optional_str_list(data: Mapping[str, object], key: str, where: str) -> list[str]:
    if key not in data:
        return []
    return _str_list_field(data, key, where)


def _evidence_for(
    clause: str,
    quote: str,
    on: str,
    number: int,
    hidden: list[Span],
    undecodable: list[Span],
) -> Evidence | None:
    """Build the evidence of one value or judged table, and file its span."""

    span = Span(start=number * 100, end=number * 100 + 10)
    if on == "hidden":
        hidden.append(span)
    elif on == "undecodable":
        undecodable.append(span)
    if quote == "none":
        return None
    return Evidence(
        clause_id=ClauseId(clause),
        sentence_ids=(SentenceId(f"{clause}.s1"),),
        quote=span,
        placed=quote == "confirmed",
    )


def _parse_value(
    data: Mapping[str, object],
    where: str,
    position_id: PositionId,
    quote_number: int,
    hidden: list[Span],
    undecodable: list[Span],
) -> CheckedValue:
    allowed = {
        "clause",
        "raw",
        "number",
        "range_high",
        "unit",
        "start_point",
        "answer",
        "vague",
        "amount",
        "total",
        "reasons",
        "unlimited",
        "quote",
        "on",
    }
    for key in data:
        if key not in allowed:
            raise ValueError(f"{where}: unknown key {key}")
    clause = _str_field(data, "clause", where)
    quote = _choice(data.get("quote", "confirmed"), _QUOTE_CHOICES, "quote", where)
    on = _choice(data.get("on", "visible"), _ON_CHOICES, "on", where)
    return CheckedValue(
        position_id=position_id,
        clause_id=ClauseId(clause),
        evidence=_evidence_for(clause, quote, on, quote_number, hidden, undecodable),
        raw_value=_optional_str_field(data, "raw", where),
        number=_optional_decimal_field(data, "number", where),
        range_high=_optional_decimal_field(data, "range_high", where),
        unit_as_written=_optional_str_field(data, "unit", where),
        start_point_as_written=_optional_str_field(data, "start_point", where),
        answer=_optional_enum_field(Answer, data, "answer", where),
        condition=None,
        vague=_optional_bool_field(data, "vague", where),
        amount=_optional_decimal_field(data, "amount", where),
        total=_optional_decimal_field(data, "total", where),
        reasons=_enum_list_field(ReasonCode, data, "reasons", where),
        unlimited=_optional_bool_field(data, "unlimited", where),
    )


def _parse_judged(
    data: Mapping[str, object],
    where: str,
    position_id: PositionId,
    quote_number: int,
    hidden: list[Span],
    undecodable: list[Span],
) -> JudgedLevel:
    allowed = {"clause", "level", "quote", "on"}
    for key in data:
        if key not in allowed:
            raise ValueError(f"{where}: unknown key {key}")
    clause = _str_field(data, "clause", where)
    quote = _choice(data.get("quote", "confirmed"), _QUOTE_CHOICES, "quote", where)
    on = _choice(data.get("on", "visible"), _ON_CHOICES, "on", where)
    return JudgedLevel(
        position_id=position_id,
        clause_id=ClauseId(clause),
        evidence=_evidence_for(clause, quote, on, quote_number, hidden, undecodable),
        level=_enum_field(Level, data, "level", where),
    )


def parse_label_inputs(
    entries: Sequence[Mapping[str, object]], playbook: Playbook
) -> tuple[tuple[LabelInput, ...], UnreadableSpans]:
    """Read the [[input]] entries of the sample format for one playbook."""

    positions = {position.id: position for position in playbook.positions}
    hidden: list[Span] = []
    undecodable: list[Span] = []
    inputs: list[LabelInput] = []
    quote_number = 0
    allowed = {"position", "match", "values", "judged", "clauses_to_read", "outside_documents"}
    for index, entry in enumerate(entries):
        where = f"input {index}"
        for key in entry:
            if key not in allowed:
                raise ValueError(f"{where}: unknown key {key}")
        position_name = _str_field(entry, "position", where)
        position_id = PositionId(position_name)
        if position_id not in positions:
            raise ValueError(f"{where}: unknown position {position_name}")
        position = positions[position_id]
        match_kind = _choice(_get(entry, "match", where), _MATCH_KINDS, "match", where)
        values = [
            _parse_value(
                value_data,
                f"{where} value {value_index}",
                position.id,
                quote_number + value_index,
                hidden,
                undecodable,
            )
            for value_index, value_data in enumerate(_optional_table_list(entry, "values", where))
        ]
        quote_number += len(values)
        judged = [
            _parse_judged(
                judged_data,
                f"{where} judged {judged_index}",
                position.id,
                quote_number + judged_index,
                hidden,
                undecodable,
            )
            for judged_index, judged_data in enumerate(_optional_table_list(entry, "judged", where))
        ]
        quote_number += len(judged)
        clauses_to_read = _optional_str_list(entry, "clauses_to_read", where)
        match: MatchResult
        if match_kind == "found":
            clause_ids: list[ClauseId] = []
            for value in values:
                if value.clause_id not in clause_ids:
                    clause_ids.append(value.clause_id)
            for level in judged:
                if level.clause_id not in clause_ids:
                    clause_ids.append(level.clause_id)
            match = MatchFound(position_id=position.id, clause_ids=tuple(clause_ids))
        elif match_kind == "nothing":
            match = NothingFound(position_id=position.id, searches=())
        elif match_kind == "unconfirmed":
            match = MatchUnconfirmed(
                position_id=position.id,
                clauses_to_read=tuple(ClauseId(name) for name in clauses_to_read),
            )
        else:
            match = CallFailed(code="model_reply_invalid")
        outside_documents = tuple(
            OutsideDocument(name=name, evidence=Span(start=0, end=0))
            for name in _optional_str_list(entry, "outside_documents", where)
        )
        inputs.append(
            LabelInput(
                position=position,
                match=match,
                values=tuple(values),
                judged=tuple(judged),
                outside_documents=outside_documents,
            )
        )
    return tuple(inputs), UnreadableSpans(hidden=tuple(hidden), undecodable=tuple(undecodable))


@dataclass(frozen=True, slots=True, kw_only=True)
class Sample:
    """The parsed Spec 14.5 sample: its playbook and its label inputs."""

    playbook: Playbook
    inputs: tuple[LabelInput, ...]
    unreadable: UnreadableSpans


def parse_sample(data: Mapping[str, object]) -> Sample:
    """Read a whole sample file: schema_version, [playbook] and [[input]]."""

    where = "sample"
    allowed = {"schema_version", "playbook", "input"}
    for key in data:
        if key not in allowed:
            raise ValueError(f"{where}: unknown key {key}")
    schema_version = _int_field(data, "schema_version", where)
    playbook_data = _get(data, "playbook", where)
    if not isinstance(playbook_data, dict):
        raise ValueError(f"{where}: playbook must be a table")
    playbook = parse_playbook(playbook_data, schema_version=schema_version)
    entries = _table_list(data, "input", where)
    inputs, unreadable = parse_label_inputs(entries, playbook)
    return Sample(playbook=playbook, inputs=inputs, unreadable=unreadable)
