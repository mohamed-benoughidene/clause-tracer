"""The owner's overrides table (S3-M4-T4, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import ClauseId, Override
from clause_tracer.core.tests.owner_tables import as_bool, as_int, as_str, load_table
from clause_tracer.links._index import build_index
from clause_tracer.links.outside import find_outside_documents
from clause_tracer.links.overrides import find_overrides
from clause_tracer.links.references import find_references
from clause_tracer.links.terms import find_definitions
from clause_tracer.links.tests.case_builder import build_case, span_of

TABLE = Path(__file__).parent / "tables" / "overrides.toml"
CASE_KEYS = REQUIRED = frozenset({"id", "clauses", "overrides"})


def _cases() -> tuple[Mapping[str, object], ...]:
    return load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED).cases


def _nth(row: Mapping[str, object]) -> int:
    return as_int(row["nth"], "nth") if "nth" in row else 1


def _rows(value: object) -> list[Mapping[str, object]]:
    assert isinstance(value, list)
    rows: list[Mapping[str, object]] = []
    for row in value:
        assert isinstance(row, dict)
        rows.append(row)
    return rows


def _target(row: Mapping[str, object]) -> ClauseId | None:
    written = as_str(row["target"], "target")
    return None if written == "" else ClauseId(written)


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["id"]))
def test_override_table(case: Mapping[str, object]) -> None:
    sample = build_case(_rows(case["clauses"]))
    index = build_index(sample.clauses)
    text = sample.document.text

    references = find_references(text, index)
    outside = find_outside_documents(text, index, find_definitions(text, index))
    overrides = find_overrides(text, index, references, outside)
    expected = tuple(
        Override(
            clause_id=ClauseId(as_str(row["clause"], "clause")),
            target=_target(row),
            overrides_target=as_bool(row["overrides_target"], "overrides_target"),
            evidence=span_of(text, as_str(row["evidence"], "evidence"), _nth(row)),
        )
        for row in _rows(case["overrides"])
    )

    assert overrides == expected


def test_override_table_has_rows() -> None:
    assert len(_cases()) >= 8
