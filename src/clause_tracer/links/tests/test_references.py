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


_DEFINED = [
    {"id": "4", "sentences": ["4. Fees."]},
    {"id": "5", "sentences": ["5. Payment."]},
    {"id": "6", "sentences": ["6. Expenses."]},
]


def _run_in_9(sentence: str) -> tuple[str, tuple[CrossReference, ...]]:
    return _run([*_DEFINED, {"id": "9", "sentences": [sentence]}])


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


def test_range() -> None:
    text, references = _run_in_9("9. Clauses 4 to 6 apply.")
    source = span_of(text, "Clauses 4 to 6")
    assert references == (
        CrossReference(source=source, target=ClauseId("4")),
        CrossReference(source=source, target=ClauseId("5")),
        CrossReference(source=source, target=ClauseId("6")),
    )


def test_range_with_dash() -> None:
    _, references = _run_in_9("9. clauses 4-6")
    assert tuple(reference.target for reference in references) == (
        ClauseId("4"),
        ClauseId("5"),
        ClauseId("6"),
    )
    _, references = _run_in_9("9. clauses 4\u20136")
    assert tuple(reference.target for reference in references) == (
        ClauseId("4"),
        ClauseId("5"),
        ClauseId("6"),
    )


def test_range_keeps_missing_members() -> None:
    _, references = _run_in_9("9. clauses 5 to 7")
    assert tuple(reference.target for reference in references) == (
        ClauseId("5"),
        ClauseId("6"),
        None,
    )


def test_list() -> None:
    _, references = _run_in_9("9. clauses 4, 5 and 9")
    assert tuple(reference.target for reference in references) == (
        ClauseId("4"),
        ClauseId("5"),
        ClauseId("9"),
    )


def test_list_with_or() -> None:
    _, references = _run_in_9("9. clause 4 or 9")
    assert tuple(reference.target for reference in references) == (
        ClauseId("4"),
        ClauseId("9"),
    )


def test_range_then_list() -> None:
    _, references = _run_in_9("9. clauses 4 to 6 and 9")
    assert tuple(reference.target for reference in references) == (
        ClauseId("4"),
        ClauseId("5"),
        ClauseId("6"),
        ClauseId("9"),
    )


def test_and_followed_by_a_word_stops() -> None:
    text, references = _run(
        [
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Fees"]},
            {"id": "1", "sentences": ["1. Schedule 1 and the Agency."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "Schedule 1", 2), target=ClauseId("S1")),
    )


def test_over_long_range_keeps_its_ends() -> None:
    _, references = _run_in_9("9. clauses 1 to 99")
    assert tuple(reference.target for reference in references) == (None, None)


def test_repeated_key_once() -> None:
    _, references = _run_in_9("9. clauses 4 and 4")
    assert len(references) == 1


def test_list_stops_before_a_unit() -> None:
    text, references = _run_in_9("9. clause 4, 30 days")
    assert references == (CrossReference(source=span_of(text, "clause 4"), target=ClauseId("4")),)


def test_range_stops_before_a_month() -> None:
    text, references = _run(
        [
            {"id": "3", "sentences": ["3. Fees."]},
            {"id": "9", "sentences": ["9. clause 3 - 5 July"]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "clause 3"), target=ClauseId("3")),)


def test_number_with_unit_is_not_a_reference() -> None:
    _, references = _run([{"id": "9", "sentences": ["9. clause 4 days"]}])
    assert references == ()


def test_may_is_not_a_unit() -> None:
    text, references = _run(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. Clause 4 may apply."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "Clause 4"), target=ClauseId("4")),)


def test_decimal_before_a_unit_is_not_cut() -> None:
    _, references = _run(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. see clause 4.5 days"]},
        ]
    )
    assert references == ()


def test_range_with_bad_roman() -> None:
    text, references = _run(
        [
            {"id": "5", "sentences": ["5. Payment."]},
            {"id": "9", "sentences": ["9. Articles IIII to V"]},
        ]
    )
    source = span_of(text, "Articles IIII to V")
    assert references == (
        CrossReference(source=source, target=None),
        CrossReference(source=source, target=ClauseId("5")),
    )


def test_this_clause() -> None:
    text, references = _run([{"id": "5.1", "sentences": ["5.1 This Clause applies."]}])
    assert references == (
        CrossReference(source=span_of(text, "This Clause"), target=ClauseId("5.1")),
    )


def test_this_schedule() -> None:
    text, references = _run(
        [
            {"id": "S1", "number": "Schedule 1", "sentences": ["Schedule 1 · Fees"]},
            {"id": "S1.1", "parent": "S1", "sentences": ["1. This Schedule lists fees."]},
        ]
    )
    assert references == (
        CrossReference(source=span_of(text, "This Schedule"), target=ClauseId("S1")),
    )


def test_this_schedule_outside_a_schedule() -> None:
    text, references = _run([{"id": "3", "sentences": ["3. This Schedule lists fees."]}])
    assert references == (CrossReference(source=span_of(text, "This Schedule"), target=None),)


def test_this_clause_with_number_is_one_reference() -> None:
    text, references = _run(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. this Clause 4 applies."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "Clause 4"), target=ClauseId("4")),)


def test_this_agreement_is_not_a_reference() -> None:
    _, references = _run([{"id": "5.1", "sentences": ["5.1 This Agreement ends."]}])
    assert references == ()


def test_this_clause_in_paragraphs() -> None:
    text, references = _run(
        [
            {"id": "p1", "sentences": ["The Agency pays."]},
            {"id": "p2", "sentences": ["This Clause applies."]},
        ]
    )
    assert references == (CrossReference(source=span_of(text, "This Clause"), target=None),)
