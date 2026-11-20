"""The owner's outside-documents table (S3-M3-T8, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import OutsideDocument
from clause_tracer.core.tests.owner_tables import as_int, as_str, load_table
from clause_tracer.links._index import build_index
from clause_tracer.links.outside import find_outside_documents
from clause_tracer.links.terms import find_definitions
from clause_tracer.links.tests.case_builder import build_case, span_of

TABLE = Path(__file__).parent / "tables" / "outside_documents.toml"
CASE_KEYS = REQUIRED = frozenset({"id", "clauses", "outside"})


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


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["id"]))
def test_outside_table(case: Mapping[str, object]) -> None:
    sample = build_case(_rows(case["clauses"]))
    index = build_index(sample.clauses)
    text = sample.document.text

    outside = find_outside_documents(text, index, find_definitions(text, index))
    expected = tuple(
        OutsideDocument(
            name=as_str(row["name"], "name"),
            evidence=span_of(text, as_str(row["name"], "name"), _nth(row)),
        )
        for row in _rows(case["outside"])
    )

    assert outside == expected


def test_outside_table_has_rows() -> None:
    assert len(_cases()) >= 6
