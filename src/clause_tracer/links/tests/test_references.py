"""Cross-references between clauses (S3-M2-T2 to S3-M2-T4)."""

from collections.abc import Mapping

from clause_tracer.core import ClauseId, CrossReference
from clause_tracer.links._index import build_index
from clause_tracer.links.references import find_references
from clause_tracer.links.tests.case_builder import build_case, span_of


def _run(
    rows: list[Mapping[str, object]],
) -> tuple[str, tuple[CrossReference, ...]]:
    case = build_case(rows)
    index = build_index(case.clauses)
    return case.document.text, find_references(case.document.text, index)


def test_clause_reference() -> None:
    text, references = _run(
        [
            {"id": "12", "sentences": ["12. Ending."]},
            {"id": "2", "sentences": ["2. It ends under clause 12."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 12"), target=ClauseId("12")),)


def test_keyword_case_is_ignored() -> None:
    text, references = _run(
        [
            {"id": "12", "sentences": ["12. Ending."]},
            {"id": "2", "sentences": ["2. See CLAUSE 12."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "CLAUSE 12"), target=ClauseId("12")),)


def test_section_reference_resolves_to_a_number() -> None:
    text, references = _run(
        [
            {"id": "14.2", "sentences": ["14.2 The cap."]},
            {"id": "2", "sentences": ["2. See Section 14.2."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "Section 14.2"), target=ClauseId("14.2")),
    )


def test_unresolved_is_kept() -> None:
    text, references = _run([{"id": "1", "sentences": ["1. See clause 9."]}])
    assert references == (CrossReference(source=span_of(text, "clause 9"), target=None),)


def test_two_point_five_days_after_a_reference() -> None:
    text, references = _run(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "1", "sentences": ["1. See clause 4 within 2.5 days."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 4"), target=ClauseId("4")),)


def test_bracketed_tail() -> None:
    text, references = _run(
        [
            {"id": "7.1(a)", "sentences": ["7.1(a) The fees."]},
            {"id": "1", "sentences": ["1. See clause 7.1(a)."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "clause 7.1(a)"), target=ClauseId("7.1(a)")),
    )


def test_leading_zero() -> None:
    text, references = _run(
        [
            {"id": "5", "sentences": ["5. Fees."]},
            {"id": "1", "sentences": ["1. See clause 05."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 05"), target=ClauseId("5")),)


def test_article_roman() -> None:
    text, references = _run(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "1", "sentences": ["1. See Article IV."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "Article IV"), target=ClauseId("4")),)


def test_article_bad_roman() -> None:
    text, references = _run([{"id": "1", "sentences": ["1. See Article IIII."]}])
    assert references == (CrossReference(source=span_of(text, "Article IIII"), target=None),)


def test_article_with_tail_is_unresolved() -> None:
    text, references = _run(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "1", "sentences": ["1. See Article 4.1."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "Article 4.1"), target=None),)


def test_schedule_reference() -> None:
    text, references = _run(
        [
            {"id": "1", "sentences": ["1. The fees are in Schedule 1."]},
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Fees"]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "Schedule 1"), target=ClauseId("S1")),
    )


def test_annex_letter() -> None:
    text, references = _run(
        [
            {"id": "AA", "number": "Annex A", "sentences": ["Annex A · Fees"]},
            {"id": "1", "sentences": ["1. See Annex A."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "Annex A", 2), target=ClauseId("AA")),
    )


def test_schedule_with_tail_is_unresolved() -> None:
    text, references = _run(
        [
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Fees"]},
            {"id": "1", "sentences": ["1. See Schedule 1.2."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "Schedule 1.2"), target=None),)


def test_schedule_heading_is_not_a_reference() -> None:
    _, references = _run(
        [
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Services"]},
        ]
    )
    assert references == ()


def test_reference_to_own_number_in_text_is_kept() -> None:
    text, references = _run([{"id": "8.2", "sentences": ["8.2 Clause 8.2 is new."]}])
    assert references == (
        CrossReference(source=span_of(text, "Clause 8.2"), target=ClauseId("8.2")),
    )


def test_duplicate_number_is_unresolved() -> None:
    text, references = _run(
        [
            {"id": "5", "sentences": ["5. Fees."]},
            {"id": "5~2", "sentences": ["5. Again."]},
            {"id": "9", "sentences": ["9. See clause 5."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 5"), target=None),)


def test_word_before_keyword() -> None:
    text, references = _run(
        [
            {"id": "3", "sentences": ["3. Fees."]},
            {"id": "1", "sentences": ["1. See subclause 3 and Xclause 3."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "subclause 3"), target=ClauseId("3")),
    )


def test_reference_into_another_document() -> None:
    text, references = _run(
        [
            {"id": "3", "sentences": ["3. Fees."]},
            {"id": "1", "sentences": ["1. under Section 3 of the Master Agreement"]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "Section 3"), target=None),)


def test_paragraph_in_schedule() -> None:
    text, references = _run(
        [
            {"id": "2", "sentences": ["2. Hosting is extra."]},
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Services"]},
            {"id": "S1.2", "parent": "S1", "sentences": ["2. See paragraph 2."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "paragraph 2"), target=ClauseId("S1.2")),
    )


def test_clause_in_schedule_ambiguous() -> None:
    text, references = _run(
        [
            {"id": "1", "sentences": ["1. Fees."]},
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Services"]},
            {"id": "S1.1", "parent": "S1", "sentences": ["See clause 1."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 1"), target=None),)


def test_clause_in_schedule_body_only() -> None:
    text, references = _run(
        [
            {"id": "12", "sentences": ["12. Ending."]},
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Services"]},
            {"id": "S1.1", "parent": "S1", "sentences": ["See clause 12."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 12"), target=ClauseId("12")),)
