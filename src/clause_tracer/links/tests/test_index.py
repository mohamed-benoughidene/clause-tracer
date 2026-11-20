"""The clause index (S3-M2-T1)."""

import dataclasses
from collections.abc import Mapping

import pytest

from clause_tracer.core import Clause, ClauseId
from clause_tracer.links._index import build_index
from clause_tracer.links.tests.case_builder import build_case, span_of

_ROWS: list[Mapping[str, object]] = [
    {"id": "1", "sentences": ["1. Pay."]},
    {
        "id": "1.1",
        "parent": "1",
        "sentences": ["1.1 Paid in 30 days.", "Late fees apply."],
    },
    {"id": "2", "sentences": ["2. End."]},
    {"id": "2~2", "sentences": ["2. Again."]},
]


def _sample() -> tuple[str, tuple[Clause, ...]]:
    case = build_case(_ROWS)
    return case.document.text, case.clauses


def test_clause_at_start_and_end() -> None:
    text, clauses = _sample()
    index = build_index(clauses)
    first = index.clause_at(0)
    assert first is not None
    assert first.id == ClauseId("1")
    last = index.clause_at(clauses[1].span.end - 1)
    assert last is not None
    assert last.id == ClauseId("1.1")
    assert index.clause_at(len(text)) is None


def test_sentence_at() -> None:
    text, clauses = _sample()
    index = build_index(clauses)
    sentence = index.sentence_at(span_of(text, "Late").start)
    assert sentence is not None
    assert str(sentence.id) == "1.1.s2"


def test_resolve_unique() -> None:
    _, clauses = _sample()
    index = build_index(clauses)
    assert index.resolve("1.1") == ClauseId("1.1")


def test_resolve_unknown() -> None:
    _, clauses = _sample()
    index = build_index(clauses)
    assert index.resolve("9") is None


def test_resolve_duplicate_is_none() -> None:
    _, clauses = _sample()
    index = build_index(clauses)
    assert index.resolve("2") is None


def test_top_ancestor() -> None:
    _, clauses = _sample()
    index = build_index(clauses)
    assert index.top_ancestor(clauses[1]).id == ClauseId("1")


def test_clause_at_before_first() -> None:
    case = build_case([{"id": "1", "sentences": ["1. Pay."]}])
    index = build_index(case.clauses)
    assert index.clause_at(-1) is None


def test_build_index_refuses_disorder() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ["1. Pay."]},
            {"id": "2", "sentences": ["2. End."]},
        ]
    )
    with pytest.raises(ValueError, match="clauses are not in text order"):
        build_index(tuple(reversed(case.clauses)))


def test_build_index_refuses_later_parent() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ["1. Pay."]},
            {"id": "2", "sentences": ["2. End."]},
        ]
    )
    clauses = (
        dataclasses.replace(case.clauses[0], parent_id=ClauseId("2")),
        case.clauses[1],
    )
    with pytest.raises(ValueError, match="clause 1 has a later parent"):
        build_index(clauses)


def test_build_index_allows_unknown_parent() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ["1. Pay."]},
            {"id": "2", "sentences": ["2. End."]},
        ]
    )
    clauses = (
        case.clauses[0],
        dataclasses.replace(case.clauses[1], parent_id=ClauseId("9")),
    )
    index = build_index(clauses)
    assert index.top_ancestor(clauses[1]).id == ClauseId("2")
