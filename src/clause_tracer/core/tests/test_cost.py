"""The pre-run cost estimate (S1-M5-T10, system design 7, Spec 9)."""

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import CallPrices, CostInputs, estimate_calls, estimate_cost
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_decimal,
    as_int,
    load_table,
)

TABLE = TABLES_DIR / "cost_estimate.toml"
CASE_KEYS: frozenset[str] = frozenset(
    {
        "id",
        "positions",
        "words_positions",
        "clauses",
        "contract_tokens",
        "input_per_million",
        "cached_input_per_million",
        "output_per_million",
        "calls",
        "low_usd",
        "high_usd",
    }
)

_TABLE = load_table(TABLE, case_keys=CASE_KEYS, required=CASE_KEYS)
_ROWS: list[dict[str, object]] = [dict(row) for row in _TABLE.cases]
_IDS = [str(row["id"]) for row in _ROWS]

_CHEAP_PRICES = CallPrices(
    input_per_million=Decimal("1"),
    cached_input_per_million=Decimal("1"),
    output_per_million=Decimal("1"),
)


def _read_row(row: dict[str, object]) -> tuple[CostInputs, int, object, object]:
    where = f"case {row['id']}"
    prices = CallPrices(
        input_per_million=as_decimal(row["input_per_million"], f"{where} input_per_million"),
        cached_input_per_million=as_decimal(
            row["cached_input_per_million"], f"{where} cached_input_per_million"
        ),
        output_per_million=as_decimal(row["output_per_million"], f"{where} output_per_million"),
    )
    inputs = CostInputs(
        positions=as_int(row["positions"], f"{where} positions"),
        words_positions=as_int(row["words_positions"], f"{where} words_positions"),
        clauses=as_int(row["clauses"], f"{where} clauses"),
        contract_tokens=as_int(row["contract_tokens"], f"{where} contract_tokens"),
        prices=prices,
    )
    return inputs, as_int(row["calls"], f"{where} calls"), row["low_usd"], row["high_usd"]


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_cost_table(row: dict[str, object]) -> None:
    inputs, calls, low, high = _read_row(row)
    where = f"case {row['id']}"
    estimate = estimate_cost(inputs)
    assert estimate.calls == calls
    assert estimate.low_usd == as_decimal(low, f"{where} low_usd")
    assert estimate.high_usd == as_decimal(high, f"{where} high_usd")


def test_cost_table_has_rows() -> None:
    assert len(_ROWS) > 0


def test_starter_makes_30_calls() -> None:
    assert estimate_calls(11, 1, 50) == 30


@given(
    positions=st.integers(0, 200),
    words=st.integers(0, 200),
    clauses=st.integers(0, 200),
    tokens=st.integers(0, 200_000),
    cached=st.decimals(0, 100, places=2),
    full=st.decimals(0, 100, places=2),
    output=st.decimals(0, 100, places=2),
)
def test_low_never_above_high(
    positions: int,
    words: int,
    clauses: int,
    tokens: int,
    cached: Decimal,
    full: Decimal,
    output: Decimal,
) -> None:
    cached_price, full_price = sorted([cached, full])
    inputs = CostInputs(
        positions=positions,
        words_positions=min(words, positions),
        clauses=clauses,
        contract_tokens=tokens,
        prices=CallPrices(
            input_per_million=full_price,
            cached_input_per_million=cached_price,
            output_per_million=output,
        ),
    )
    estimate = estimate_cost(inputs)
    assert 0 <= estimate.low_usd <= estimate.high_usd


def test_negative_count_raises() -> None:
    with pytest.raises(ValueError):
        estimate_calls(-1, 0, 0)
    with pytest.raises(ValueError):
        estimate_calls(0, 0, -1)
    with pytest.raises(ValueError):
        estimate_calls(1, 2, 0)
    with pytest.raises(ValueError):
        estimate_cost(
            CostInputs(
                positions=-1,
                words_positions=0,
                clauses=0,
                contract_tokens=0,
                prices=_CHEAP_PRICES,
            )
        )
    negative_price = CallPrices(
        input_per_million=Decimal("-1"),
        cached_input_per_million=Decimal("1"),
        output_per_million=Decimal("1"),
    )
    with pytest.raises(ValueError):
        estimate_cost(
            CostInputs(
                positions=1,
                words_positions=0,
                clauses=0,
                contract_tokens=0,
                prices=negative_price,
            )
        )
