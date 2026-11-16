"""Tests for the owner-table loader (T11, testing strategy 10).

The owner alone writes and edits the tables; these tests only read
them, through the loader, and check that a broken table fails loudly.
"""

from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

from clause_tracer.core.enums import Level
from clause_tracer.core.tests.owner_tables import (
    OwnerTableError,
    as_bool,
    as_datetime,
    as_decimal,
    as_enum,
    as_fraction,
    as_int,
    as_str,
    as_str_tuple,
    load_table,
)

FIXTURE = Path(__file__).parent / "fixtures" / "owner_table_example.toml"
CASE_KEYS: frozenset[str] = frozenset({"id", "level", "limit"})
REQUIRED: frozenset[str] = frozenset({"id", "level", "limit"})


def test_reads_cases() -> None:
    table = load_table(FIXTURE, case_keys=CASE_KEYS, required=REQUIRED)
    assert [case["id"] for case in table.cases] == ["a", "b"]


def test_missing_header_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text('# Not the header.\n\n[[case]]\nid = "a"\n', encoding="utf-8")
    with pytest.raises(OwnerTableError):
        load_table(path, case_keys=CASE_KEYS, required=REQUIRED)


def test_unknown_top_level_key_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        '# Expected answers. Only the owner edits this file. Constitution T11.\n[nope]\nx = "1"\n',
        encoding="utf-8",
    )
    with pytest.raises(OwnerTableError):
        load_table(path, case_keys=CASE_KEYS, required=REQUIRED, sections=frozenset())


def test_unknown_case_key_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        "# Expected answers. Only the owner edits this file. Constitution T11.\n"
        '[[case]]\nid = "a"\nlevel = "walk_away"\nlimit = "15"\nextra = "1"\n',
        encoding="utf-8",
    )
    with pytest.raises(OwnerTableError):
        load_table(path, case_keys=CASE_KEYS, required=REQUIRED)


def test_missing_required_key_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        "# Expected answers. Only the owner edits this file. Constitution T11.\n"
        '[[case]]\nid = "a"\n',
        encoding="utf-8",
    )
    with pytest.raises(OwnerTableError):
        load_table(path, case_keys=CASE_KEYS, required=REQUIRED)


def test_duplicate_id_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        "# Expected answers. Only the owner edits this file. Constitution T11.\n"
        '[[case]]\nid = "a"\nlevel = "walk_away"\nlimit = "15"\n'
        '[[case]]\nid = "a"\nlevel = "walk_away"\nlimit = "15"\n',
        encoding="utf-8",
    )
    with pytest.raises(OwnerTableError):
        load_table(path, case_keys=CASE_KEYS, required=REQUIRED)


def test_header_only_file_has_no_cases(tmp_path: Path) -> None:
    path = tmp_path / "empty.toml"
    path.write_text(
        "# Expected answers. Only the owner edits this file. Constitution T11.\n",
        encoding="utf-8",
    )
    table = load_table(path, case_keys=CASE_KEYS, required=REQUIRED)
    assert table.cases == ()


def test_as_decimal() -> None:
    assert as_decimal("1.5", "where") == Decimal("1.5")
    assert as_decimal(15, "where") == Decimal(15)
    with pytest.raises(OwnerTableError):
        as_decimal(1.5, "where")
    with pytest.raises(OwnerTableError):
        as_decimal(True, "where")


def test_as_fraction() -> None:
    assert as_fraction("7/30", "where") == Fraction(7, 30)


def test_as_enum() -> None:
    assert as_enum(Level, "walk_away", "where") is Level.WALK_AWAY
    with pytest.raises(OwnerTableError):
        as_enum(Level, "walk-away", "where")


def test_as_datetime_rejects_naive() -> None:
    assert as_datetime(datetime(2026, 1, 1, tzinfo=UTC), "where") == datetime(
        2026, 1, 1, tzinfo=UTC
    )
    with pytest.raises(OwnerTableError):
        as_datetime(datetime(2026, 1, 1), "where")


def test_other_converters() -> None:
    # The plan names as_str, as_bool, as_int and as_str_tuple without
    # dedicated cases; this check keeps them covered.
    assert as_str("x", "where") == "x"
    assert as_bool(True, "where") is True
    assert as_int(3, "where") == 3
    assert as_str_tuple(["a", "b"], "where") == ("a", "b")
    for converter, bad in (
        (as_str, 1),
        (as_bool, "yes"),
        (as_int, True),
        (as_int, "1"),
        (as_str_tuple, ("a",)),
        (as_str_tuple, [1]),
        (as_datetime, "2026-01-01"),
    ):
        with pytest.raises(OwnerTableError):
            converter(bad, "where")
