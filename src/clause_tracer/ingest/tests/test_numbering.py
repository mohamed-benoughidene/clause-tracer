"""Tests for the continuity rules and bracketed-token readings (S2-M3-T2)."""

import pytest

from clause_tracer.ingest._numbering import (
    ParenStyle,
    is_decimal_successor,
    paren_readings,
    roman_numeral_value,
)


@pytest.mark.parametrize(
    ("previous", "parts", "expected"),
    [
        ((5, 6), (5, 7), True),
        ((5, 6), (6,), True),
        ((5, 6), (6, 1), True),
        ((5, 6), (5, 6, 1), True),
        ((5,), (5, 1), True),
        ((1, 2), (2, 1), True),
        ((1, 2), (2, 1, 1), True),
        ((1, 2, 3), (1, 3), True),
        ((1, 2, 3), (2,), True),
        ((5, 6), (7,), False),
        ((5, 6), (2, 5), False),
        ((5, 6), (5, 6), False),
        ((5, 6), (5, 8), False),
        ((5,), (5, 2), False),
        ((5, 6), (5, 6, 2), False),
        ((5, 6), (4,), False),
    ],
)
def test_is_decimal_successor(
    previous: tuple[int, ...],
    parts: tuple[int, ...],
    expected: bool,
) -> None:
    assert is_decimal_successor(previous, parts) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("a", ((ParenStyle.LOWER, 1),)),
        ("h", ((ParenStyle.LOWER, 8),)),
        ("i", ((ParenStyle.LOWER, 9), (ParenStyle.ROMAN, 1))),
        ("v", ((ParenStyle.LOWER, 22), (ParenStyle.ROMAN, 5))),
        ("ii", ((ParenStyle.LOWER, 35), (ParenStyle.ROMAN, 2))),
        ("iv", ((ParenStyle.ROMAN, 4),)),
        ("xxxix", ((ParenStyle.ROMAN, 39),)),
        ("xl", ()),
        ("iiii", ()),
        ("aa", ((ParenStyle.LOWER, 27),)),
        ("ab", ()),
        ("A", ((ParenStyle.UPPER, 1),)),
        ("1", ((ParenStyle.DIGIT, 1),)),
        ("99", ((ParenStyle.DIGIT, 99),)),
        ("the", ()),
    ],
)
def test_paren_readings(
    token: str,
    expected: tuple[tuple[ParenStyle, int], ...],
) -> None:
    assert paren_readings(token) == expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("I", 1),
        ("IV", 4),
        ("XIV", 14),
        ("MCMXC", 1990),
        ("IIII", None),
        ("IC", None),
        ("", None),
        ("iv", None),
    ],
)
def test_roman_numeral_value(token: str, expected: int | None) -> None:
    assert roman_numeral_value(token) == expected
