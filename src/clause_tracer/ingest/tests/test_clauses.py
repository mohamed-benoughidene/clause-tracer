"""Tests for splitting a document into clauses (S2-M3-T6)."""

from dataclasses import replace

from clause_tracer.core import Clause, Span
from clause_tracer.ingest import read_pasted_text, split_clauses


def clauses_of(text: str) -> tuple[Clause, ...]:
    return split_clauses(read_pasted_text(text))


def ids(text: str) -> tuple[str, ...]:
    return tuple(str(clause.id) for clause in clauses_of(text))


def test_heading_with_sub_clauses() -> None:
    clauses = clauses_of(
        "5. Charges and payment\n5.1 The Agency pays 25%.\n5.2 Invoices are paid in 60 days.\n"
    )

    assert tuple(str(clause.id) for clause in clauses) == ("5", "5.1", "5.2")
    first, sub1, _sub2 = clauses
    assert first.level == 1
    assert first.parent_id is None
    assert sub1.level == 2
    assert sub1.parent_id == "5"
    assert sub1.number == "5.1"


def test_number_inside_a_sentence_is_not_a_clause() -> None:
    text = "5.6 Payment is due within\n2.5 days of the invoice.\n5.7 Next."

    assert ids(text) == ("5.6", "5.7")


def test_sub_clauses_without_a_heading_line() -> None:
    clauses = clauses_of("1.1 One.\n1.2 Two.\n2.1 Three.")

    assert tuple(str(clause.id) for clause in clauses) == ("1.1", "1.2", "2.1")
    for clause in clauses:
        assert clause.level == 1
        assert clause.parent_id is None


def test_letter_i_after_h_is_a_letter() -> None:
    text = "".join(f"({letter}) x.\n" for letter in "abcdefghi")

    clauses = clauses_of(text)

    assert len(clauses) == 9
    assert tuple(str(clause.id) for clause in clauses)[-1] == "(i)"
    assert clauses[-1].level == 1


def test_letter_i_after_a_is_a_roman_child() -> None:
    text = "1. Rules:\n(a) first:\n(i) one;\n(ii) two;\n(b) second."

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == (
        "1",
        "1(a)",
        "1(a)(i)",
        "1(a)(ii)",
        "1(b)",
    )
    assert tuple(clause.level for clause in clauses) == (1, 2, 3, 3, 2)


def test_bracket_item_out_of_order_is_text() -> None:
    assert ids("1. Rules:\n(c) is not first.") == ("1",)


def test_text_before_the_first_number() -> None:
    text = "Services Agreement\nThis Agreement is dated 5 November 2026.\n1. Start\n1.1 Now."

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == ("p1", "1", "1.1")
    assert clauses[0].number is None


def test_blank_text_before_the_first_number_joins_it() -> None:
    clauses = clauses_of("\n\n1. Start")

    assert tuple(str(clause.id) for clause in clauses) == ("1",)
    assert clauses[0].span == Span(start=0, end=10)


def test_schedule_restarts_numbering() -> None:
    text = (
        "14. General\n14.1 Whole agreement.\nSchedule 1 · Services\n"
        "1. Build the site.\n2. Hosting is extra."
    )

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == (
        "14",
        "14.1",
        "S1",
        "S1.1",
        "S1.2",
    )
    schedule = clauses[2]
    assert schedule.number == "Schedule 1"
    assert schedule.level == 1
    first_schedule_clause = clauses[3]
    assert first_schedule_clause.parent_id == "S1"
    assert first_schedule_clause.level == 2
    assert first_schedule_clause.number == "1"


def test_numbering_that_starts_again_gets_new_ids() -> None:
    text = "1. Definitions\n2. Term\n1. Definitions\n1.1 Words.\n2. Term"

    assert ids(text) == ("1", "2", "1~2", "1.1", "2~2")


def test_list_inside_a_clause_does_not_swallow_what_follows() -> None:
    text = "5.1 Do:\n1. x\n2. y\n5.2 Next\n6. Then"

    assert ids(text) == ("5.1", "1", "2", "5.2", "6")


def test_excerpt_can_start_at_any_number() -> None:
    text = "5.4 Invoices are paid in 60 days.\n5.5 Expenses."

    assert ids(text) == ("5.4", "5.5")


def test_skipped_number_stays_in_the_clause_before() -> None:
    assert ids("1. One\n3. Three") == ("1",)


def test_markdown_symbols_do_not_hide_a_number() -> None:
    text = "## 1. Start\n**1.1** Now."

    document = read_pasted_text(text)
    clauses = split_clauses(document)

    assert tuple(str(clause.id) for clause in clauses) == ("1", "1.1")
    assert document.text == text


def test_clauses_cover_the_text() -> None:
    text = (
        "14. General\n14.1 Whole agreement.\nSchedule 1 · Services\n"
        "1. Build the site.\n2. Hosting is extra."
    )

    clauses = clauses_of(text)

    assert clauses[0].span.start == 0
    assert clauses[-1].span.end == len(text)
    for earlier, later in zip(clauses, clauses[1:], strict=False):
        assert earlier.span.end == later.span.start


def test_numbering_source_is_numbers() -> None:
    text = "5. Charges and payment\n5.1 The Agency pays 25%.\n5.2 Invoices are paid in 60 days.\n"

    for clause in clauses_of(text):
        assert clause.numbering_source == "numbers"


def test_blank_document_has_no_clauses() -> None:
    document = replace(read_pasted_text("x"), text="  \n")

    assert split_clauses(document) == ()


def test_article_keywords() -> None:
    text = "Article I Definitions\n1.1 Words.\nArticle II Payment\n2.1 Invoices."

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == ("1", "1.1", "2", "2.1")
    assert clauses[0].number == "Article I"
    assert clauses[1].parent_id == "1"


def test_closing_brackets() -> None:
    text = "3.1 The Developer will:\na) plan;\nb) write:\ni) templates;\nii) components."

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == (
        "3.1",
        "3.1(a)",
        "3.1(b)",
        "3.1(b)(i)",
        "3.1(b)(ii)",
    )
    assert clauses[1].number == "a)"


def test_bare_numbers_that_follow_on() -> None:
    assert ids("1 Definitions\n1.1 Words.\n2 Payment") == ("1", "1.1", "2")


def test_bare_number_never_starts_again() -> None:
    assert ids("1. One\n1.1 Words.\n1 Again") == ("1", "1.1")


def test_unnumbered_heading_after_a_blank_line() -> None:
    text = "1. Start\n1.1 Now.\n\nBackground\nThe Agency builds sites.\n\n2. Payment"

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == ("1", "1.1", "p1", "2")
    heading_clause = clauses[2]
    assert heading_clause.number is None
    assert heading_clause.level == 1
    assert heading_clause.parent_id is None
    assert clauses[3].parent_id is None


def test_heading_before_a_number_ends_the_bracket_list() -> None:
    text = "Parties\n(1) Brightline.\n(2) Karim.\nBackground\n(A) The Agency.\n1. Definitions"

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == (
        "p1",
        "(1)",
        "(2)",
        "p2",
        "(A)",
        "1",
    )
    assert clauses[4].parent_id is None


def test_address_number_before_any_numbering_is_text() -> None:
    text = 'Karim Benali\n27 Rue Didouche Mourad\nAlgiers ("the Developer").\n1. Definitions'

    assert ids(text) == ("p1", "1")


def test_heading_inside_numbered_text_ends_the_bracket_list() -> None:
    text = "1. Start\n1.1 Now.\n\nBackground\n(A) The Agency."

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == ("1", "1.1", "p1", "(A)")
    assert clauses[3].parent_id is None


def test_short_line_inside_a_sentence_is_not_a_heading() -> None:
    text = "1.1 The Developer will deliver\nThe Website\nby the Delivery Date.\n1.2 Next."

    assert ids(text) == ("1.1", "1.2")


def test_paragraphs_by_blank_lines() -> None:
    text = "First part\nwraps here.\n\nSecond part.\n\n\nThird."

    clauses = clauses_of(text)

    assert tuple(str(clause.id) for clause in clauses) == ("p1", "p2", "p3")
    assert tuple(clause.span.start for clause in clauses) == (0, 24, 39)
    for clause in clauses:
        assert clause.numbering_source == "paragraphs"


def test_paragraphs_by_lines_when_no_blank_line() -> None:
    clauses = clauses_of("First.\nSecond.\nThird.")

    assert tuple(str(clause.id) for clause in clauses) == ("p1", "p2", "p3")


def test_one_paragraph() -> None:
    clauses = clauses_of("Just words.")

    assert tuple(str(clause.id) for clause in clauses) == ("p1",)
    assert clauses[0].span.start == 0
    assert clauses[0].span.end == len("Just words.")


def test_paragraph_clauses_cover_the_text() -> None:
    text = "First part\nwraps here.\n\nSecond part.\n\n\nThird."

    clauses = clauses_of(text)

    assert clauses[0].span.start == 0
    assert clauses[-1].span.end == len(text)
    for earlier, later in zip(clauses, clauses[1:], strict=False):
        assert earlier.span.end == later.span.start


def test_paragraph_sentences() -> None:
    clauses = clauses_of("One. Two.")

    assert tuple(str(sentence.id) for sentence in clauses[0].sentences) == (
        "p1.s1",
        "p1.s2",
    )


def test_numbered_heading_line_has_a_heading() -> None:
    clauses = clauses_of(
        "5. Charges and payment\n5.1 The Agency pays 25%.\n5.2 Invoices are paid in 60 days.\n"
    )

    assert clauses[0].heading == "Charges and payment"
    assert clauses[1].heading is None
    assert clauses[2].heading is None


def test_line_ending_in_a_colon_is_not_a_heading() -> None:
    clauses = clauses_of("1. Rules:\n(a) first:\n(i) one;\n(ii) two;\n(b) second.")

    for clause in clauses:
        assert clause.heading is None


def test_schedule_heading() -> None:
    text = (
        "14. General\n14.1 Whole agreement.\nSchedule 1 · Services\n"
        "1. Build the site.\n2. Hosting is extra."
    )

    clauses = clauses_of(text)

    assert clauses[2].heading == "Services"
    assert clauses[0].heading == "General"


def test_markdown_heading() -> None:
    clauses = clauses_of("## 1. Start\n**1.1** Now.")

    assert clauses[0].heading == "Start"


def test_long_line_is_not_a_heading() -> None:
    clauses = clauses_of("1. " + "a" * 101 + "\n1.1 x.")

    assert clauses[0].heading is None


def test_clause_with_more_lines_has_no_heading() -> None:
    clauses = clauses_of("1. Payment\nThe Agency pays on time.\n1.1 Now.")

    assert clauses[0].heading is None


def test_heading_clause_heading() -> None:
    text = "1. Start\n1.1 Now.\n\nBackground\nThe Agency builds sites.\n\n2. Payment"

    clauses = clauses_of(text)

    assert clauses[2].heading == "Background"


def test_sentences_cover_the_clause() -> None:
    text = "5.4 Invoices are paid within 60 days. Interest runs at 4% p.a. from the due date."

    clauses = clauses_of(text)

    assert len(clauses) == 1
    sentences = clauses[0].sentences
    assert tuple(str(sentence.id) for sentence in sentences) == ("5.4.s1", "5.4.s2")
    assert tuple(sentence.span for sentence in sentences) == (
        Span(start=0, end=38),
        Span(start=38, end=81),
    )


def test_the_number_stays_in_the_first_sentence() -> None:
    clauses = clauses_of("5. Charges and payment")

    assert len(clauses) == 1
    assert len(clauses[0].sentences) == 1
    assert clauses[0].sentences[0].span == clauses[0].span


def test_sentence_ids_count_from_one_in_each_clause() -> None:
    clauses = clauses_of("1.1 One. Two.\n1.2 Three.")

    assert tuple(str(sentence.id) for sentence in clauses[0].sentences) == (
        "1.1.s1",
        "1.1.s2",
    )
    assert tuple(str(sentence.id) for sentence in clauses[1].sentences) == ("1.2.s1",)


def test_wrapped_schedule_words_mid_clause_are_text() -> None:
    text = (
        "1. Payment\n"
        "The Supplier must pay the fee.\n"
        "Schedule 2 to this Agreement and the Customer will pay\n"
        "1.1 Later."
    )

    assert ids(text) == ("1", "1.1")


def test_paren_items_have_no_heading_and_bare_numbers_keep_theirs() -> None:
    clauses = clauses_of("1. Lists\n(a) the Supplier\n(b) the Customer")

    assert clauses[0].heading == "Lists"
    assert clauses[1].heading is None
    assert clauses[2].heading is None
    assert clauses_of("1 Definitions\n2 Terms")[0].heading == "Definitions"


def test_text_that_starts_with_a_byte_order_mark_and_blank_line_has_no_preamble() -> None:
    clauses = clauses_of("﻿\n\n1. Foo\nbar")

    assert len(clauses) == 1
    assert clauses[0].number == "1"


def test_number_keeps_its_written_digits_and_id_is_normalised() -> None:
    clause = clauses_of("01.2 Text")[0]

    assert clause.number == "01.2"
    assert clause.id == "1.2"
