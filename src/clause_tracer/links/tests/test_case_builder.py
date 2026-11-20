"""The test-case builder (S3-M1-T5)."""

import pytest

from clause_tracer.core import ClauseId, Span
from clause_tracer.links.tests.case_builder import build_case, span_of


def test_text_joins_sentences_and_clauses() -> None:
    sample = build_case(
        [
            {"id": "1", "sentences": ["A b.", "C d."]},
            {"id": "2", "sentences": ["E."]},
        ]
    )

    assert sample.document.text == "A b. C d.\nE."


def test_spans_tile_the_text() -> None:
    sample = build_case(
        [
            {"id": "1", "sentences": ["A b.", "C d."]},
            {"id": "2", "sentences": ["E."]},
        ]
    )

    first, second = sample.clauses
    assert (first.span.start, first.span.end) == (0, 10)
    assert (second.span.start, second.span.end) == (10, 12)
    assert (first.sentences[0].span.start, first.sentences[0].span.end) == (0, 5)
    assert (first.sentences[1].span.start, first.sentences[1].span.end) == (5, 10)


def test_parent_sets_level() -> None:
    sample = build_case(
        [
            {"id": "1", "sentences": ["1. Fees."]},
            {"id": "1.1", "parent": "1", "sentences": ["1.1 Paid."]},
        ]
    )

    child = sample.clauses[1]
    assert child.level == 2
    assert child.parent_id == ClauseId("1")


def test_unknown_parent_raises() -> None:
    with pytest.raises(ValueError, match="unknown parent 1"):
        build_case([{"id": "1.1", "parent": "1", "sentences": ["x."]}])


def test_unknown_key_raises() -> None:
    with pytest.raises(ValueError, match="unknown key colour"):
        build_case([{"id": "1", "sentences": ["x."], "colour": "red"}])


def test_paragraph_ids() -> None:
    sample = build_case(
        [
            {"id": "p1", "sentences": ["First."]},
            {"id": "p2", "sentences": ["Second."]},
        ]
    )

    for clause in sample.clauses:
        assert clause.numbering_source == "paragraphs"
        assert clause.number is None


def test_paragraph_id_with_number_raises() -> None:
    with pytest.raises(ValueError, match="paragraph id p1 cannot have a number"):
        build_case([{"id": "p1", "number": "1", "sentences": ["x."]}])


def test_number_key() -> None:
    sample = build_case([{"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Fees"]}])

    assert sample.clauses[0].number == "Schedule 1"


def test_empty_rows() -> None:
    sample = build_case([])

    assert sample.document.text == ""
    assert sample.clauses == ()


def test_duplicate_id_raises() -> None:
    with pytest.raises(ValueError, match="duplicate id 1"):
        build_case(
            [
                {"id": "1", "sentences": ["x."]},
                {"id": "1", "sentences": ["y."]},
            ]
        )


def test_missing_key_raises() -> None:
    with pytest.raises(ValueError, match="missing key sentences"):
        build_case([{"id": "1"}])
    with pytest.raises(ValueError, match="missing key id"):
        build_case([{"sentences": ["x."]}])


def test_wrong_type_id_still_reports_missing_sentences() -> None:
    with pytest.raises(ValueError, match="missing key sentences"):
        build_case([{"id": 3}])


def test_sentence_spaces_are_kept() -> None:
    sample = build_case([{"id": "1", "sentences": [" a "]}])

    assert sample.document.text == " a "
    assert (sample.clauses[0].sentences[0].span.start, sample.clauses[0].sentences[0].span.end) == (
        0,
        3,
    )


def test_word_starting_with_p_is_not_a_paragraph() -> None:
    sample = build_case([{"id": "payment", "sentences": ["x."]}])

    assert sample.clauses[0].numbering_source == "numbers"
    assert sample.clauses[0].number == "payment"


def test_mixed_ids_are_numbers() -> None:
    sample = build_case(
        [
            {"id": "p1", "sentences": ["x."]},
            {"id": "1", "sentences": ["y."]},
        ]
    )

    assert sample.clauses[0].numbering_source == "numbers"
    assert sample.clauses[1].numbering_source == "numbers"
    assert sample.clauses[0].number is None


def test_carriage_return_raises() -> None:
    with pytest.raises(ValueError, match="a sentence must be non-empty and hold no line break"):
        build_case([{"id": "1", "sentences": ["a\rb"]}])


def test_heading_must_be_a_string() -> None:
    with pytest.raises(ValueError, match="heading must be a string"):
        build_case([{"id": "1", "heading": 3, "sentences": ["x."]}])


def test_span_of_nth() -> None:
    assert span_of("a x a", "a", 2) == Span(start=4, end=5)


def test_span_of_missing_raises() -> None:
    with pytest.raises(AssertionError):
        span_of("abc", "z")
