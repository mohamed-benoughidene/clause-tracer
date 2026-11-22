"""The privacy test-case builder (S4-M1-T5)."""

import pytest

from clause_tracer.core import (
    DefinedTerm,
    Party,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy.tests.case_builder import make_case, span_of, suggestion


def test_text_joins_sentences() -> None:
    assert make_case(["A b.", "C d."]).document.text == "A b. C d."


def test_sentence_spans_tile_the_text() -> None:
    case = make_case(["A b.", "C d."])
    clause = case.clauses[0]

    assert clause.sentences[0].span == Span(start=0, end=5)
    assert clause.sentences[1].span == Span(start=5, end=9)
    assert clause.span == Span(start=0, end=9)


def test_no_sentences() -> None:
    case = make_case([])

    assert case.document.text == ""
    assert case.clauses == ()


def test_empty_sentence_raises() -> None:
    with pytest.raises(ValueError):
        make_case([""])


def test_line_break_raises() -> None:
    with pytest.raises(ValueError):
        make_case(["a\nb"])


def test_parties_and_terms_pass_through() -> None:
    party = Party(name="Brightline Ltd", address=None, yours=False)
    term = DefinedTerm(term="Agency", definition=Span(start=0, end=3), uses=())

    case = make_case(["A b."], parties=[party], terms=[term])

    assert case.parties == (party,)
    assert case.terms == (term,)


def test_span_of_nth() -> None:
    assert span_of("a x a", "a", 2) == Span(start=4, end=5)


def test_span_of_missing_raises() -> None:
    with pytest.raises(AssertionError):
        span_of("abc", "z")


def test_suggestion_builds() -> None:
    assert suggestion("Hi Sam", "Sam", PlaceholderKind.PERSON, PiiSource.NER) == PiiSuggestion(
        span=Span(start=3, end=6), kind=PlaceholderKind.PERSON, source=PiiSource.NER
    )
