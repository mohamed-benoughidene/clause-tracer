"""The owner's cross-references table (S3-M2-T6, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import ClauseId, CrossReference
from clause_tracer.core.tests.owner_tables import as_int, as_str, load_table
from clause_tracer.links._index import build_index
from clause_tracer.links.references import find_references
from clause_tracer.links.tests.case_builder import build_case, span_of

TABLE = Path(__file__).parent / "tables" / "references.toml"
CASE_KEYS = REQUIRED = frozenset({"id", "clauses", "references"})


def _cases() -> tuple[Mapping[str, object], ...]:
    return load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED).cases


def _nth(row: Mapping[str, object]) -> int:
    return as_int(row["nth"], "nth") if "nth" in row else 1


def _clause_rows(case: Mapping[str, object]) -> list[Mapping[str, object]]:
    raw_rows = case["clauses"]
    assert isinstance(raw_rows, list)
    rows: list[Mapping[str, object]] = []
    for row in raw_rows:
        assert isinstance(row, dict)
        rows.append(row)
    return rows


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["id"]))
def test_reference_table(case: Mapping[str, object]) -> None:
    sample = build_case(_clause_rows(case))
    index = build_index(sample.clauses)
    actual = find_references(sample.document.text, index)

    raw_expected = case["references"]
    assert isinstance(raw_expected, list)
    expected: list[CrossReference] = []
    for row in raw_expected:
        assert isinstance(row, dict)
        source = span_of(
            sample.document.text,
            as_str(row["source"], "source"),
            _nth(row),
        )
        target_text = as_str(row["target"], "target")
        target = None if target_text == "" else ClauseId(target_text)
        expected.append(CrossReference(source=source, target=target))

    assert actual == tuple(expected)


def test_reference_table_has_rows() -> None:
    assert len(_cases()) >= 10
