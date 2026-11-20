"""The owner's defined-terms table (S3-M3-T7, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import DefinedTerm, Span, fold_for_matching
from clause_tracer.core.tests.owner_tables import as_int, as_str, load_table
from clause_tracer.links._index import build_index
from clause_tracer.links._spans import build_span_set, trimmed
from clause_tracer.links.outside import find_outside_documents
from clause_tracer.links.sample_clauses import SampleInput
from clause_tracer.links.terms import find_definitions, find_terms, find_undefined_terms
from clause_tracer.links.tests.case_builder import build_case, span_of

TABLE = Path(__file__).parent / "tables" / "terms.toml"
CASE_KEYS = REQUIRED = frozenset({"id", "clauses", "terms", "undefined"})


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


def _clause_rows(case: Mapping[str, object]) -> list[Mapping[str, object]]:
    return _rows(case["clauses"])


def _trimmed_sentences(sample: SampleInput) -> dict[str, Span]:
    spans: dict[str, Span] = {}
    for clause in sample.clauses:
        for sentence in clause.sentences:
            spans[str(sentence.id)] = trimmed(sample.document.text, sentence.span)
    return spans


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["id"]))
def test_terms_table(case: Mapping[str, object]) -> None:
    sample = build_case(_clause_rows(case))
    index = build_index(sample.clauses)
    text = sample.document.text

    definitions = find_definitions(text, index)
    terms = find_terms(text, fold_for_matching(text), definitions)
    outside = find_outside_documents(text, index, definitions)
    excluded = build_span_set(
        [use for term in terms for use in term.uses]
        + [definition.quoted for definition in definitions]
        + [entry.evidence for entry in outside]
    )
    undefined = find_undefined_terms(text, index, excluded)

    sentence_spans = _trimmed_sentences(sample)
    expected_terms: list[DefinedTerm] = []
    for row in _rows(case["terms"]):
        term = as_str(row["term"], "term")
        definition_id = as_str(row["definition"], "definition")
        uses = tuple(
            span_of(text, as_str(use["text"], "text"), _nth(use)) for use in _rows(row["uses"])
        )
        expected_terms.append(
            DefinedTerm(term=term, definition=sentence_spans[definition_id], uses=uses)
        )
    expected_undefined = tuple(
        span_of(text, as_str(row["text"], "text"), _nth(row)) for row in _rows(case["undefined"])
    )

    assert terms == tuple(expected_terms)
    assert undefined == expected_undefined


def test_terms_table_has_rows() -> None:
    assert len(_cases()) >= 8
