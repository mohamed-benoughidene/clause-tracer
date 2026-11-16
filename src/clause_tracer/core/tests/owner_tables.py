"""The loader for the owner's expected-answer tables (Constitution T11).

The owner alone writes and edits the tables in tables/; tests read them
through this loader and never write to a table. Each table is a TOML
file whose first line is HEADER, holding optional named sections and
[[case]] rows. Every load error and every converter raises
OwnerTableError, so a broken table fails loudly instead of passing.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from fractions import Fraction
from pathlib import Path

HEADER = "# Expected answers. Only the owner edits this file. Constitution T11."
TABLES_DIR = Path(__file__).parent / "tables"


class OwnerTableError(ValueError):
    """A table is unreadable: wrong header, unknown key, or a bad cell."""


@dataclass(frozen=True, slots=True, kw_only=True)
class OwnerTable:
    """One loaded owner table: its named sections and its case rows."""

    sections: Mapping[str, Mapping[str, object]]
    cases: tuple[Mapping[str, object], ...]


def _case_id(row: Mapping[str, object]) -> str:
    """The row's id when it is a string, to name it in error messages."""

    value = row.get("id")
    return value if isinstance(value, str) else "<no id>"


def load_table(
    path: Path,
    *,
    case_keys: frozenset[str],
    required: frozenset[str],
    sections: frozenset[str] = frozenset(),
) -> OwnerTable:
    """Read one owner table; raise OwnerTableError when it is not well formed."""

    text = path.read_text(encoding="utf-8")
    first_line = text.split("\n", 1)[0]
    if first_line != HEADER:
        raise OwnerTableError(f"{path.name}: first line is not the owner-table header")
    data = tomllib.loads(text)
    for key in data:
        if key != "case" and key not in sections:
            raise OwnerTableError(f"{path.name}: unknown top-level key {key}")
    loaded_cases: list[Mapping[str, object]] = data.get("case", [])
    seen_ids: set[str] = set()
    cases: list[Mapping[str, object]] = []
    for row in loaded_cases:
        unknown = sorted(set(row) - case_keys)
        if unknown:
            raise OwnerTableError(f"{path.name}: case {_case_id(row)}: unknown key {unknown[0]}")
        missing = sorted(required - set(row))
        if missing:
            raise OwnerTableError(f"{path.name}: case {_case_id(row)}: missing key {missing[0]}")
        case_id = row.get("id")
        if not isinstance(case_id, str):
            raise OwnerTableError(f"{path.name}: case id must be a string")
        if case_id in seen_ids:
            raise OwnerTableError(f"{path.name}: case {case_id}: duplicate id")
        seen_ids.add(case_id)
        cases.append(row)
    loaded_sections: dict[str, Mapping[str, object]] = {
        key: value for key, value in data.items() if key != "case"
    }
    return OwnerTable(sections=loaded_sections, cases=tuple(cases))


def as_str(value: object, where: str) -> str:
    if not isinstance(value, str):
        raise OwnerTableError(f"{where}: expected a string, got {value!r}")
    return value


def as_bool(value: object, where: str) -> bool:
    if not isinstance(value, bool):
        raise OwnerTableError(f"{where}: expected a boolean, got {value!r}")
    return value


def as_int(value: object, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise OwnerTableError(f"{where}: expected an integer, got {value!r}")
    return value


def as_decimal(value: object, where: str) -> Decimal:
    if isinstance(value, bool):
        raise OwnerTableError(f"{where}: expected a decimal number, got {value!r}")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise OwnerTableError(f"{where}: expected a decimal number, got {value!r}") from error
    raise OwnerTableError(f"{where}: expected a decimal number, got {value!r}")


def as_fraction(value: object, where: str) -> Fraction:
    if isinstance(value, bool):
        raise OwnerTableError(f"{where}: expected a number, got {value!r}")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as error:
            raise OwnerTableError(f"{where}: expected a number, got {value!r}") from error
    raise OwnerTableError(f"{where}: expected a number, got {value!r}")


def as_datetime(value: object, where: str) -> datetime:
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value
    raise OwnerTableError(f"{where}: expected a timezone-aware datetime, got {value!r}")


def as_str_tuple(value: object, where: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise OwnerTableError(f"{where}: expected a list of strings, got {value!r}")
    return tuple(as_str(item, where) for item in value)


def as_enum[E: StrEnum](enum_type: type[E], value: object, where: str) -> E:
    if isinstance(value, str):
        for member in enum_type:
            if value == member.value:
                return member
    names = ", ".join(member.value for member in enum_type)
    raise OwnerTableError(f"{where}: expected one of {names}, got {value!r}")


def as_enum_tuple[E: StrEnum](enum_type: type[E], value: object, where: str) -> tuple[E, ...]:
    if not isinstance(value, list):
        raise OwnerTableError(f"{where}: expected a list, got {value!r}")
    return tuple(as_enum(enum_type, item, where) for item in value)
