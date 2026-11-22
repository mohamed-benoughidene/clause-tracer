"""Check and trim the suggestions (S4-M3-T1)."""

from typing import cast

import pytest

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy.resolve import trim_suggestions
from clause_tracer.privacy.tests.case_builder import suggestion

PERSON = PlaceholderKind.PERSON


def _raw(start: object, end: object) -> PiiSuggestion:
    return PiiSuggestion(
        span=Span(start=cast(int, start), end=cast(int, end)),
        kind=PERSON,
        source=PiiSource.NER,
    )


def test_trims_white_space() -> None:
    trimmed = trim_suggestions(" Sam ", (suggestion(" Sam ", " Sam ", PERSON, PiiSource.NER),))

    assert trimmed == (PiiSuggestion(span=Span(start=1, end=4), kind=PERSON, source=PiiSource.NER),)


def test_blank_span_is_dropped() -> None:
    item = PiiSuggestion(span=Span(start=1, end=4), kind=PERSON, source=PiiSource.NER)

    assert trim_suggestions("a   b", (item,)) == ()


def test_empty_span_is_dropped() -> None:
    item = PiiSuggestion(span=Span(start=2, end=2), kind=PERSON, source=PiiSource.NER)

    assert trim_suggestions("abc", (item,)) == ()


def test_outside_the_text_raises() -> None:
    item = PiiSuggestion(span=Span(start=1, end=9), kind=PERSON, source=PiiSource.NER)

    with pytest.raises(ValueError, match="privacy: suggestion span is outside the text"):
        trim_suggestions("abc", (item,))


def test_keeps_kind_source_and_order() -> None:
    later = suggestion("abc xyz", "xyz", PlaceholderKind.ADDRESS, PiiSource.RULE)
    first = suggestion("abc xyz", "abc", PERSON, PiiSource.NER)

    assert trim_suggestions("abc xyz", (later, first)) == (later, first)


def test_reversed_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span is reversed"):
        trim_suggestions("Short text here.", (_raw(5, 2),))


def test_start_past_text_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span is outside the text"):
        trim_suggestions("Short text here.", (_raw(20, 25),))


def test_start_past_the_text_and_reversed_raises_outside() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span is outside the text"):
        trim_suggestions("Short text here.", (_raw(25, 16),))


def test_negative_start_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span is outside the text"):
        trim_suggestions("Short text here.", (_raw(-1, 3),))


def test_bool_start_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span offsets must be integers"):
        trim_suggestions("Short text here.", (_raw(True, 3),))


def test_bool_end_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span offsets must be integers"):
        trim_suggestions("Short text here.", (_raw(0, True),))


def test_float_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span offsets must be integers"):
        trim_suggestions("Short text here.", (_raw(0.0, 3),))


def test_none_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span offsets must be integers"):
        trim_suggestions("Short text here.", (_raw(None, 3),))


def test_empty_span_at_len_is_dropped() -> None:
    assert trim_suggestions("Short text here.", (_raw(16, 16),)) == ()


def test_empty_span_is_dropped_silently() -> None:
    assert trim_suggestions("Short text here.", (_raw(3, 3),)) == ()


def test_a_valid_span_then_a_bad_one_still_raises() -> None:
    with pytest.raises(ValueError, match="privacy: suggestion span is reversed"):
        trim_suggestions("Short text here.", (_raw(0, 5), _raw(5, 2)))
