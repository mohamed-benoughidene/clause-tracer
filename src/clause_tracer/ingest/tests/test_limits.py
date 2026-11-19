"""Tests for the input size limits and the word count (Spec 9)."""

from clause_tracer.ingest.limits import MAX_FILE_BYTES, MAX_WORDS, count_words


def test_limits_match_the_spec() -> None:
    assert MAX_FILE_BYTES == 20_971_520
    assert MAX_WORDS == 50_000


def test_count_words() -> None:
    assert count_words("a b\n\nc\td") == 4


def test_count_words_empty() -> None:
    assert count_words("") == 0
    assert count_words("  \n ") == 0


def test_count_words_keeps_punctuation_inside_a_word() -> None:
    assert count_words("don't re-use 2.5") == 3
