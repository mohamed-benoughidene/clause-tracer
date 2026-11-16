"""The Spec 14.5 sample, labelled end to end against the owner's table (S1-M3-T17)."""

import tomllib
from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import Level, ReasonCode, WrittenBy, label_all
from clause_tracer.core.sample_input import parse_sample
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_enum,
    as_enum_tuple,
    load_table,
)

SAMPLE = Path(__file__).parent.parent / "samples" / "spec-14-5.toml"
CASE_KEYS: frozenset[str] = frozenset({"id", "position", "level", "reasons", "written_by"})

_TABLE = load_table(TABLES_DIR / "spec_14_5.toml", case_keys=CASE_KEYS, required=CASE_KEYS)
_ROWS: list[Mapping[str, object]] = list(_TABLE.cases)
_IDS = [str(row["id"]) for row in _ROWS]


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_spec_14_5_sample(row: Mapping[str, object]) -> None:
    sample = parse_sample(tomllib.loads(SAMPLE.read_text(encoding="utf-8")))
    labels = label_all(sample.playbook, sample.inputs, sample.unreadable)
    where = f"case {row['id']}"
    label = next(label for label in labels if label.position_id == str(row["position"]))
    assert label.level is as_enum(Level, row["level"], f"{where} level"), where
    assert frozenset(label.reasons) == frozenset(
        as_enum_tuple(ReasonCode, row["reasons"], f"{where} reasons")
    ), where
    assert label.written_by is as_enum(WrittenBy, row["written_by"], f"{where} written_by"), where


def test_spec_14_5_table_covers_every_position() -> None:
    sample = parse_sample(tomllib.loads(SAMPLE.read_text(encoding="utf-8")))
    table_positions = {str(row["position"]) for row in _ROWS}
    sample_positions = {str(position.id) for position in sample.playbook.positions}
    assert table_positions == sample_positions
