"""The auto-delete date rules (S1-M4-T6, Spec 9)."""

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import due_at, in_warning_window, is_due
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_bool,
    as_datetime,
    as_int,
    load_table,
)

TABLE = TABLES_DIR / "auto_delete.toml"
CASE_KEYS: frozenset[str] = frozenset(
    {"id", "last_change", "days", "now", "protected_until", "due_at", "due", "warning"}
)
REQUIRED: frozenset[str] = frozenset(
    {"id", "last_change", "days", "now", "due_at", "due", "warning"}
)

_TABLE = load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED)
_ROWS: list[dict[str, object]] = [dict(row) for row in _TABLE.cases]
_IDS = [str(row["id"]) for row in _ROWS]


def _read_row(row: dict[str, object]) -> tuple[datetime, int, datetime, datetime | None]:
    last_change = as_datetime(row["last_change"], f"case {row['id']} last_change")
    days = as_int(row["days"], f"case {row['id']} days")
    now = as_datetime(row["now"], f"case {row['id']} now")
    protected_until: datetime | None = None
    if "protected_until" in row:
        protected_until = as_datetime(row["protected_until"], f"case {row['id']} protected_until")
    return last_change, days, now, protected_until


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_auto_delete_table(row: dict[str, object]) -> None:
    last_change, days, now, protected_until = _read_row(row)
    where = f"case {row['id']}"
    expected_due_at = as_datetime(row["due_at"], f"{where} due_at")
    assert due_at(last_change, days, protected_until) == expected_due_at
    assert is_due(last_change, days, now, protected_until) == as_bool(row["due"], f"{where} due")
    assert in_warning_window(last_change, days, now, protected_until) == as_bool(
        row["warning"], f"{where} warning"
    )


def test_auto_delete_table_has_rows() -> None:
    assert len(_ROWS) > 0


@given(
    last_change=st.datetimes(timezones=st.just(UTC)),
    days=st.sampled_from([7, 30, 90]),
    now=st.datetimes(timezones=st.just(UTC)),
)
def test_due_exactly_when_now_reaches_the_due_date(
    last_change: datetime, days: int, now: datetime
) -> None:
    # Promise test: auto-delete runs on schedule (Spec 11, unit part).
    assert is_due(last_change, days, now) == (now >= last_change + timedelta(days=days))


@given(
    last_change=st.datetimes(timezones=st.just(UTC)),
    days=st.sampled_from([7, 30, 90]),
    now=st.datetimes(timezones=st.just(UTC)),
    protected=st.one_of(st.none(), st.datetimes(timezones=st.just(UTC))),
)
def test_never_due_before_the_rule_allows(
    last_change: datetime, days: int, now: datetime, protected: datetime | None
) -> None:
    before_rule = now < last_change + timedelta(days=days)
    before_grace = protected is not None and now < protected
    if before_rule or before_grace:
        assert not is_due(last_change, days, now, protected)


def test_naive_datetime_raises() -> None:
    aware = datetime(2026, 11, 16, 9, 0, 0, tzinfo=UTC)
    naive = datetime(2026, 11, 16, 9, 0, 0)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        due_at(naive, 30)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        is_due(aware, 30, naive)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        is_due(aware, 30, aware, protected_until=naive)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        in_warning_window(aware, 30, naive)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        due_at(aware, 30, naive)


def test_days_below_one_raises() -> None:
    aware = datetime(2026, 11, 16, 9, 0, 0, tzinfo=UTC)
    with pytest.raises(ValueError, match="days must be 1 or more"):
        due_at(aware, 0)
    with pytest.raises(ValueError, match="days must be 1 or more"):
        is_due(aware, -1, aware)
    with pytest.raises(ValueError, match="days must be 1 or more"):
        in_warning_window(aware, 0, aware)
