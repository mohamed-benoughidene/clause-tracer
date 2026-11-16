"""Tests for the playbook checks of Spec 4.1 (S1-M3-T11)."""

import tomllib
from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import (
    Level,
    Playbook,
    PlaybookId,
    PlaybookProblem,
    PlaybookProblemCode,
    Position,
    PositionId,
    PositionType,
    WordsRule,
    check_playbook,
)
from clause_tracer.core.sample_input import parse_position, parse_sample
from clause_tracer.core.tests.owner_tables import TABLES_DIR, load_table

TABLE = TABLES_DIR / "playbook_checks.toml"
SAMPLE = Path(__file__).parent.parent / "samples" / "spec-14-5.toml"
CASE_KEYS: frozenset[str] = frozenset({"id", "positions", "problems"})
REQUIRED: frozenset[str] = frozenset({"id", "positions", "problems"})

_TABLE = load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED)
_ROWS: list[Mapping[str, object]] = list(_TABLE.cases)
_IDS = [str(row["id"]) for row in _ROWS]


def _expected_problems(row: Mapping[str, object]) -> set[PlaybookProblem]:
    problems: set[PlaybookProblem] = set()
    raw_problems: list[Mapping[str, object]] = row["problems"]  # type: ignore[assignment]
    for problem in raw_problems:
        raw_position = problem.get("position")
        position_id = PositionId(str(raw_position)) if raw_position is not None else None
        problems.add(
            PlaybookProblem(
                position_id=position_id,
                code=PlaybookProblemCode(str(problem["code"])),
            )
        )
    return problems


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_playbook_checks_table(row: Mapping[str, object]) -> None:
    raw_positions: list[Mapping[str, object]] = row["positions"]  # type: ignore[assignment]
    positions = tuple(
        parse_position(position, f"position {index}")
        for index, position in enumerate(raw_positions)
    )
    playbook = Playbook(
        id=PlaybookId("test"),
        schema_version=1,
        name="Test",
        side="test",
        customer_id=None,
        positions=positions,
        starter=False,
    )
    assert set(check_playbook(playbook)) == _expected_problems(row)


def test_playbook_checks_table_has_rows() -> None:
    assert len(_ROWS) > 0


def test_starter_playbook_passes() -> None:
    # The starter playbook of Spec 7 has no problems (Spec 4.1).
    sample = parse_sample(tomllib.loads(SAMPLE.read_text(encoding="utf-8")))
    assert check_playbook(sample.playbook) == ()


def test_rule_type_mismatch() -> None:
    # A NUMBER position holding a WordsRule gives exactly one problem,
    # and its other checks are skipped (S1-M3-T11).
    position = Position(
        id=PositionId("1"),
        topic="t",
        type=PositionType.NUMBER,
        rule=WordsRule(preferred="p", acceptable="a", walk_away="w"),
        missing_level=Level.UNSURE,
        why_note=None,
    )
    playbook = Playbook(
        id=PlaybookId("test"),
        schema_version=1,
        name="Test",
        side="test",
        customer_id=None,
        positions=(position,),
        starter=False,
    )
    assert check_playbook(playbook) == (
        PlaybookProblem(
            position_id=PositionId("1"),
            code=PlaybookProblemCode.RULE_TYPE_MISMATCH,
        ),
    )
