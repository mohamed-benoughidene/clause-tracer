"""The owner's clause-splitter table (S2-M3-T10, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core.tests.owner_tables import as_int, as_str, load_table
from clause_tracer.ingest import read_pasted_text, split_clauses

TABLE = Path(__file__).parent / "tables" / "clause_split.toml"
CASE_KEYS = frozenset({"id", "text", "numbering", "clauses"})
REQUIRED = frozenset({"id", "text", "numbering", "clauses"})


def _cases() -> tuple[Mapping[str, object], ...]:
    return load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED).cases


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["id"]))
def test_clause_split_table(case: Mapping[str, object]) -> None:
    text = as_str(case["text"], "text")
    numbering = as_str(case["numbering"], "numbering")
    expected_clauses = case["clauses"]
    assert isinstance(expected_clauses, list)

    clauses = split_clauses(read_pasted_text(text))

    assert len(clauses) == len(expected_clauses)
    for clause, row in zip(clauses, expected_clauses, strict=True):
        assert isinstance(row, dict)
        assert str(clause.id) == as_str(row["id"], "id")
        assert (clause.number or "") == as_str(row["number"], "number")
        assert clause.level == as_int(row["level"], "level")
        assert (clause.parent_id or "") == as_str(row["parent"], "parent")
        assert (clause.heading or "") == as_str(row["heading"], "heading")
        assert (
            text[clause.span.start : clause.span.end]
            .lstrip()
            .startswith(as_str(row["starts_with"], "starts_with"))
        )
        assert clause.numbering_source == numbering


def test_clause_split_table_has_rows() -> None:
    assert len(_cases()) >= 27
