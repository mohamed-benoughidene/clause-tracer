"""Tests for unit conversion, Rule 6 (S1-M3-T12)."""

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import ReasonCode, Unit, convert_to_unit
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_decimal,
    as_enum,
    as_fraction,
    load_table,
)

TABLE = TABLES_DIR / "units.toml"
CASE_KEYS: frozenset[str] = frozenset({"id", "number", "unit", "target", "expected"})
REQUIRED: frozenset[str] = frozenset({"id", "number", "target", "expected"})

_TABLE = load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED)
_ROWS: list[Mapping[str, object]] = list(_TABLE.cases)
_IDS = [str(row["id"]) for row in _ROWS]

_REASON_VALUES = {member.value for member in ReasonCode}


def _expected(row: Mapping[str, object]) -> Fraction | ReasonCode:
    raw = str(row["expected"])
    if raw in _REASON_VALUES:
        return ReasonCode(raw)
    return as_fraction(raw, f"case {row['id']} expected")


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_units_table(row: Mapping[str, object]) -> None:
    number = as_decimal(row["number"], f"case {row['id']} number")
    target = as_enum(Unit, row["target"], f"case {row['id']} target")
    unit: str | None = None
    if "unit" in row:
        unit = str(row["unit"])
    assert convert_to_unit(number, unit, target) == _expected(row)


def test_units_table_has_rows() -> None:
    assert len(_ROWS) > 0


@given(n=st.decimals(min_value=0, max_value=10_000, places=2))
def test_days_and_months_round_trip(n: Decimal) -> None:
    assert convert_to_unit(n, "months", Unit.DAYS) == Fraction(n) * 30
    assert convert_to_unit(n, "days", Unit.MONTHS) * 30 == Fraction(n)
