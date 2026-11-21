"""The public call: one link map from a document and its clauses (S3-M5-T1)."""

import dataclasses
from pathlib import Path

import pytest

from clause_tracer.core import (
    ClauseId,
    CrossReference,
    DefinedTerm,
    LinkMap,
    OutsideDocument,
    Override,
    Span,
)
from clause_tracer.links import map_links
from clause_tracer.links._spans import trimmed
from clause_tracer.links.sample_clauses import load_clause_fixture
from clause_tracer.links.tests.case_builder import build_case, span_of

FIXTURE = Path(__file__).parent.parent / "samples" / "developer-agreement.clauses.json"


def _sample_map() -> LinkMap:
    sample = load_clause_fixture(FIXTURE.read_text(encoding="utf-8"))
    return map_links(sample.document, sample.clauses)


def test_empty_document() -> None:
    case = build_case([])

    link_map = map_links(case.document, case.clauses)

    assert link_map.references == ()
    assert link_map.terms == ()
    assert link_map.overrides == ()
    assert link_map.outside_documents == ()
    assert link_map.undefined_terms == ()


def test_all_parts_together() -> None:
    case = build_case(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {
                "id": "9",
                "sentences": [
                    '9. "Fee" means the price.',
                    "Subject to Clause 4, the Master Agreement applies within 3 Business Days.",
                ],
            },
        ]
    )
    text = case.document.text
    definition = trimmed(text, case.clauses[1].sentences[0].span)

    link_map = map_links(case.document, case.clauses)

    assert link_map.references == (
        CrossReference(source=span_of(text, "Clause 4"), target=ClauseId("4")),
    )
    assert link_map.terms == (DefinedTerm(term="Fee", definition=definition, uses=()),)
    assert link_map.overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Subject to Clause 4"),
        ),
    )
    assert link_map.outside_documents == (
        OutsideDocument(name="Master Agreement", evidence=span_of(text, "Master Agreement")),
    )
    assert link_map.undefined_terms == (span_of(text, "Business Days"),)


def test_span_outside_text_raises() -> None:
    case = build_case([{"id": "1", "sentences": ["0123456789"]}])
    clause = dataclasses.replace(case.clauses[0], span=Span(start=0, end=99))

    with pytest.raises(ValueError, match="clause 1 lies outside the text"):
        map_links(case.document, (clause,))


def test_sentence_outside_its_clause_raises() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ["1. Pay."]},
            {"id": "2", "sentences": ["2. Fees."]},
        ]
    )
    sentence = dataclasses.replace(case.clauses[0].sentences[0], span=Span(start=0, end=99))
    clause = dataclasses.replace(case.clauses[0], sentences=(sentence,))

    with pytest.raises(ValueError, match="sentence 1.s1 lies outside clause 1"):
        map_links(case.document, (clause, case.clauses[1]))


def test_same_input_same_output() -> None:
    case = build_case(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {
                "id": "9",
                "sentences": [
                    '9. "Fee" means the price.',
                    "Subject to Clause 4, the Master Agreement applies within 3 Business Days.",
                ],
            },
        ]
    )

    first = map_links(case.document, case.clauses)
    second = map_links(case.document, case.clauses)

    assert first == second


def test_sample_has_no_override_without_target() -> None:
    link_map = _sample_map()

    assert [override for override in link_map.overrides if override.target is None] == []


def test_sample_has_one_outside_document() -> None:
    link_map = _sample_map()

    assert len(link_map.outside_documents) == 1
