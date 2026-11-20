"""Clause numbers (S3-M2-T1)."""

import pytest

from clause_tracer.links._numbers import expand_range, normalise_number, roman_to_int


def test_normalise_drops_leading_zeros() -> None:
    assert normalise_number("05") == "5"
    assert normalise_number("01.02") == "1.2"
    assert normalise_number("0") == "0"
    assert normalise_number("10.0") == "10.0"


def test_normalise_keeps_the_tail() -> None:
    assert normalise_number("7.1(a)(i)") == "7.1(a)(i)"


def test_normalise_rejects_text() -> None:
    with pytest.raises(ValueError):
        normalise_number("a.1")


def test_roman() -> None:
    assert roman_to_int("IV") == 4
    assert roman_to_int("XII") == 12
    assert roman_to_int("MMMCMXCIX") == 3999


def test_roman_rejects() -> None:
    for written in ("IIII", "", "iv"):
        with pytest.raises(ValueError):
            roman_to_int(written)


def test_expand_whole_numbers() -> None:
    assert expand_range("4", "6") == ("4", "5", "6")


def test_expand_last_part() -> None:
    assert expand_range("4.1", "4.3") == ("4.1", "4.2", "4.3")


def test_expand_depth_differs() -> None:
    assert expand_range("4", "4.2") == ("4", "4.2")


def test_expand_backwards() -> None:
    assert expand_range("6", "4") == ("6", "4")


def test_expand_tail() -> None:
    assert expand_range("4.1(a)", "4.1(c)") == ("4.1(a)", "4.1(c)")


def test_expand_limit() -> None:
    assert len(expand_range("1", "50")) == 50
    assert expand_range("1", "51") == ("1", "51")


def test_expand_same() -> None:
    assert expand_range("4", "4") == ("4",)
