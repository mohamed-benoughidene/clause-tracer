"""Whole-word and name-form searches through the match key (S4-M1-T6)."""

from collections.abc import Iterable

from clause_tracer.core import Span, fold_for_matching
from clause_tracer.privacy._match import find_name_form, find_word


def _word(text: str, needle: str) -> tuple[Span, ...]:
    return find_word(fold_for_matching(text), fold_for_matching(needle).text)


def _form(
    text: str,
    form: str,
    *,
    stop_words: Iterable[str] = (),
    ambiguous_words: Iterable[str] = (),
) -> tuple[Span, ...]:
    return find_name_form(
        text,
        fold_for_matching(text),
        fold_for_matching(form).text,
        frozenset(stop_words),
        frozenset(ambiguous_words),
    )


def _spans(spans: tuple[Span, ...]) -> tuple[tuple[int, int], ...]:
    return tuple((span.start, span.end) for span in spans)


def test_finds_whole_words_only() -> None:
    assert _word("Ms Jones and Jonesy, jones.", "Jones") == (
        Span(start=3, end=8),
        Span(start=21, end=26),
    )


def test_soft_hyphen_does_not_hide_a_word() -> None:
    assert _word("Jo\u00adnes here", "jones") == (Span(start=0, end=6),)


def test_line_break_matches_a_space() -> None:
    assert _word("Brightline\nStudio Ltd", "brightline studio ltd") == (Span(start=0, end=21),)


def test_sharp_s_folds_to_ss() -> None:
    assert _word("Strauß", "strauss") == (Span(start=0, end=6),)
    assert _word("Strauß", "stras") == ()


def test_hits_do_not_overlap() -> None:
    assert _word("aa aa aa", "aa aa") == (Span(start=0, end=5),)


def test_empty_needle_gives_nothing() -> None:
    assert _word("abc", "") == ()


def test_punctuation_ends_a_word() -> None:
    assert _word("(Jones)", "jones") == (Span(start=1, end=6),)


def test_a_form_of_two_words_ignores_case() -> None:
    assert _form("karim benali signs", "karim benali") == (Span(start=0, end=12),)


def test_a_one_word_form_needs_a_capital() -> None:
    assert _form("karim signs. Karim signs.", "karim") == (Span(start=13, end=18),)


def test_a_stop_word_is_skipped() -> None:
    assert _form("Will pay.", "will", stop_words={"will"}) == ()


def test_layer3_sentence_initial_ambiguous_word_is_left() -> None:
    spans = _form(
        "Rose Hope signs. Hope is not a term. Contact Hope.",
        "hope",
        ambiguous_words={"hope"},
    )

    assert _spans(spans) == ((5, 9), (45, 49))


def test_layer3_possessive_counts_at_a_sentence_start() -> None:
    assert _form("Hope's car. Hope cars.", "hope", ambiguous_words={"hope"}) == (
        Span(start=0, end=4),
    )


def test_layer3_honorific_counts() -> None:
    spans = _form(
        "Ms Hope signs. Mr Hope signs.",
        "hope",
        ambiguous_words={"hope"},
    )

    assert _spans(spans) == ((3, 7), (18, 22))


def test_layer3_heading_line_is_left() -> None:
    spans = _form(
        "Price and Payment\nHope\nContact Hope's team.",
        "hope",
        ambiguous_words={"hope"},
    )

    assert _spans(spans) == ((31, 35),)


def test_layer3_clause_number_is_a_sentence_start() -> None:
    spans = _form(
        "1. Hope signs.\n2.1 Hope pays. Ask Hope.",
        "hope",
        ambiguous_words={"hope"},
    )

    assert _spans(spans) == ((34, 38),)


def test_layer3_unambiguous_word_needs_no_evidence() -> None:
    spans = _form(
        "Jones shall pay. Jones signs.",
        "jones",
        ambiguous_words={"hope"},
    )

    assert _spans(spans) == ((0, 5), (17, 22))
