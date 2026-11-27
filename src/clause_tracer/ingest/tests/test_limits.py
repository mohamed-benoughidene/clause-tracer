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


def test_stage_5_limits() -> None:
    from clause_tracer.ingest import limits

    assert limits.MAX_ZIP_MEMBERS == 2_000
    assert limits.MAX_XML_PART_BYTES == 33_554_432
    assert limits.MAX_PARSED_TOTAL_BYTES == 50_331_648
    assert limits.MAX_XML_DEPTH == 256
    assert limits.MAX_PDF_PAGES == 1_000
