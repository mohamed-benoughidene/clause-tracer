"""The output scans (S1-M5-T2 to S1-M5-T8, Spec 6.2)."""

import pytest

from clause_tracer.core import (
    ABBREVIATIONS,
    ADVICE_PHRASES,
    CONTACT_WORDS,
    EVALUATIVE_WORDS,
    FILLER_PHRASES,
    FIRST_PERSON_WORDS,
    INJECTION_PHRASES,
    LAW_WORDS,
    LENGTH_CAPS,
    ScanFinding,
    TextSlot,
    contains_phrase,
    mask_abbreviations,
    scan_style,
    scan_text,
)
from clause_tracer.core.tests.owner_tables import TABLES_DIR, load_table
from clause_tracer.core.tests.scan_cases import SCAN_CASE_KEYS, ScanCase, scan_cases
from clause_tracer.core.tests.shapes_for_tests import make_scan_context

SCANS_TABLE = TABLES_DIR / "scans.toml"

TEXT_FINDINGS: frozenset[ScanFinding] = frozenset(
    {
        ScanFinding.TOO_LONG,
        ScanFinding.LAW_WORD,
        ScanFinding.ADVICE,
        ScanFinding.INJECTION_TELL,
        ScanFinding.CONTACT_WORD,
        ScanFinding.WEB_ADDRESS,
        ScanFinding.EMAIL_ADDRESS,
        ScanFinding.WRONG_LABEL_WORD,
    }
)
WORD_STYLE_FINDINGS: frozenset[ScanFinding] = frozenset(
    {ScanFinding.FIRST_PERSON, ScanFinding.FILLER_PHRASE, ScanFinding.EVALUATIVE_WORD}
)

_CASES: tuple[ScanCase, ...] = scan_cases()
_CASE_IDS: list[str] = [case.id for case in _CASES]

_COPIED_LISTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("law_words", LAW_WORDS),
    ("advice_phrases", ADVICE_PHRASES),
    ("injection_phrases", INJECTION_PHRASES),
    ("contact_words", CONTACT_WORDS),
    ("first_person_words", FIRST_PERSON_WORDS),
    ("filler_phrases", FILLER_PHRASES),
    ("evaluative_words", EVALUATIVE_WORDS),
    ("abbreviations", ABBREVIATIONS),
)


def test_scan_rules_match_owner_table() -> None:
    table = load_table(
        SCANS_TABLE,
        case_keys=SCAN_CASE_KEYS,
        required=frozenset({"id"}),
        sections=frozenset({"lists", "caps"}),
    )
    for key, copied in _COPIED_LISTS:
        value = table.sections["lists"][key]
        assert isinstance(value, list)
        assert tuple(value) == copied, key
    caps = table.sections["caps"]
    assert set(LENGTH_CAPS) == set(TextSlot)
    for slot in TextSlot:
        value = caps[slot.value]
        assert isinstance(value, int) and not isinstance(value, bool)
        assert LENGTH_CAPS[slot] == value, slot


@pytest.mark.parametrize("case", _CASES, ids=_CASE_IDS)
def test_text_scans_table(case: ScanCase) -> None:
    assert set(scan_text(case.text, case.slot, case.context.label)) == (
        case.findings & TEXT_FINDINGS
    )


def test_scans_table_has_rows() -> None:
    assert len(_CASES) > 0


def test_every_law_word_fails_in_any_case() -> None:
    # Promise test: no AI text states what a law allows (Spec 11).
    for word in LAW_WORDS:
        for form in (word.lower(), word.upper(), word.title()):
            text = f"This is {form} here."
            assert ScanFinding.LAW_WORD in scan_text(text, TextSlot.READING, None)


def test_curly_apostrophe_is_folded() -> None:
    assert contains_phrase("don’t sign", "don't sign")


@pytest.mark.parametrize("case", _CASES, ids=_CASE_IDS)
def test_style_word_scans_table(case: ScanCase) -> None:
    assert set(scan_style(case.text, case.slot, case.context)) & WORD_STYLE_FINDINGS == (
        case.findings & WORD_STYLE_FINDINGS
    )


def test_mask_abbreviations_keeps_length() -> None:
    assert mask_abbreviations("Pay e.g. now.") == "Pay " + " " * 4 + " now."
    assert mask_abbreviations("See info.") == "See info."


def test_first_person_fails_outside_the_message() -> None:
    first_person_slots = {TextSlot.REASON, TextSlot.READING, TextSlot.REWRITE}
    for slot in TextSlot:
        holds = ScanFinding.FIRST_PERSON in scan_style("I'd flag this.", slot, make_scan_context())
        if slot in first_person_slots:
            assert holds, slot
        else:
            assert not holds, slot


def test_curly_contraction_is_first_person() -> None:
    holds = ScanFinding.FIRST_PERSON in scan_style(
        "We’ll check 5.4.", TextSlot.READING, make_scan_context()
    )
    assert holds


def test_abbreviation_is_not_first_person() -> None:
    holds = ScanFinding.FIRST_PERSON in scan_style(
        "The fee, i.e. the deposit, is due.", TextSlot.READING, make_scan_context()
    )
    assert not holds


def test_word_in_source_is_allowed() -> None:
    findings = scan_style(
        "We shall ensure that the work is fair.",
        TextSlot.REWRITE,
        make_scan_context(source_text="We shall ensure that the work is fair and on time."),
    )
    assert not (set(findings) & WORD_STYLE_FINDINGS)


def test_word_not_in_source_fails() -> None:
    holds = ScanFinding.FIRST_PERSON in scan_style(
        "We shall pay.",
        TextSlot.REWRITE,
        make_scan_context(source_text="The Client shall pay."),
    )
    assert holds


def test_exclamation_mark_is_filler() -> None:
    with_mark = scan_style("5.4 says 60 days!", TextSlot.READING, make_scan_context())
    without_mark = scan_style("5.4 says 60 days.", TextSlot.READING, make_scan_context())
    assert ScanFinding.FILLER_PHRASE in with_mark
    assert ScanFinding.FILLER_PHRASE not in without_mark


def test_evaluative_word_whole_word_only() -> None:
    whole = scan_style("Not fair.", TextSlot.READING, make_scan_context())
    part = scan_style("Fairly broad.", TextSlot.READING, make_scan_context())
    assert ScanFinding.EVALUATIVE_WORD in whole
    assert ScanFinding.EVALUATIVE_WORD not in part


def test_keep_strings_pass_style_scans() -> None:
    # The "Keep" strings of ux-copy 1.1, word for word, are models of the
    # voice: none of them may fail a style scan.
    keep_strings = (
        "This one is a walk-away. You'd wait 60 days to be paid; your limit is 30.",
        "“Reasonable” has no number, so it can't be checked against your limit.",
        "A late payer loses nothing by waiting.",
        "A search can miss a clause. This doesn't prove the contract has no non-compete.",
        "One label in it is wrong on purpose.",
        "The check can miss things.",
        "It doesn't mean it's safe to sign.",
    )
    for text in keep_strings:
        findings = scan_style(text, TextSlot.READING, make_scan_context())
        assert not (set(findings) & WORD_STYLE_FINDINGS), text


@pytest.mark.parametrize("case", _CASES, ids=_CASE_IDS)
def test_anchor_scans_table(case: ScanCase) -> None:
    assert set(scan_style(case.text, case.slot, case.context)) & {ScanFinding.NO_ANCHOR} == (
        case.findings & {ScanFinding.NO_ANCHOR}
    )


def test_clause_number_anchors_a_reason() -> None:
    findings = scan_style(
        "5.4 sets no deadline.",
        TextSlot.REASON,
        make_scan_context(clause_numbers=("5.4",)),
    )
    assert ScanFinding.NO_ANCHOR not in findings


def test_longer_number_is_not_an_anchor() -> None:
    for text in ("5.40 sets no deadline.", "15.4 sets no deadline."):
        findings = scan_style(text, TextSlot.REASON, make_scan_context(clause_numbers=("5.4",)))
        assert ScanFinding.NO_ANCHOR in findings, text


def test_number_at_sentence_end_anchors() -> None:
    findings = scan_style("Read 5.4.", TextSlot.REASON, make_scan_context(clause_numbers=("5.4",)))
    assert ScanFinding.NO_ANCHOR not in findings


def test_quoted_word_from_the_quote_anchors() -> None:
    findings = scan_style(
        "“Reasonable” has no number, so it can't be checked against your limit.",
        TextSlot.REASON,
        make_scan_context(quote="within a reasonable time"),
    )
    assert ScanFinding.NO_ANCHOR not in findings


def test_straight_quotes_also_count() -> None:
    findings = scan_style(
        '"Reasonable" has no number.',
        TextSlot.REASON,
        make_scan_context(quote="within a reasonable time"),
    )
    assert ScanFinding.NO_ANCHOR not in findings


def test_short_quoted_word_is_not_an_anchor() -> None:
    findings = scan_style(
        "“the” has no number.",
        TextSlot.REASON,
        make_scan_context(quote="the time"),
    )
    assert ScanFinding.NO_ANCHOR in findings


def test_quoted_word_not_in_the_quote_fails() -> None:
    findings = scan_style(
        "“prompt” payment is not defined.",
        TextSlot.REASON,
        make_scan_context(quote="within a reasonable time"),
    )
    assert ScanFinding.NO_ANCHOR in findings


def test_reason_without_quote_or_clause_fails() -> None:
    findings = scan_style('"Reasonable" has no number.', TextSlot.REASON, make_scan_context())
    assert ScanFinding.NO_ANCHOR in findings


def test_no_anchor_only_checks_reasons() -> None:
    other_slots = {TextSlot.READING, TextSlot.QUESTION, TextSlot.MESSAGE, TextSlot.REWRITE}
    for slot in other_slots:
        findings = scan_style("The wording is vague.", slot, make_scan_context())
        assert ScanFinding.NO_ANCHOR not in findings, slot
