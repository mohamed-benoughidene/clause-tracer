"""The numbering continuity rules and bracketed-token readings (S2-M3-T2).

A number opens a clause only when it follows on from the numbering so far.
This file holds the pure rules: the next sibling or first child of a decimal
number, every way to read a bracketed token, and the value of a Roman numeral.
It reads no document text and has no side effects.
"""

import re
from enum import StrEnum, auto
from typing import Final


class ParenStyle(StrEnum):
    """The four ways to read a bracketed token."""

    LOWER = auto()
    ROMAN = auto()
    UPPER = auto()
    DIGIT = auto()


_LOWER_LETTERS: Final[str] = "abcdefghijklmnopqrstuvwxyz"
_UPPER_LETTERS: Final[str] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The lower-case Roman form the splitter reads inside brackets: i to xxxix.
_LOWER_ROMAN: Final[re.Pattern[str]] = re.compile(r"x{0,3}(ix|iv|v?i{0,3})")
_DIGITS: Final[re.Pattern[str]] = re.compile(r"[1-9][0-9]?")

_ROMAN_NUMERAL: Final[re.Pattern[str]] = re.compile(
    r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"
)
_ROMAN_VALUES: Final[dict[str, int]] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


def is_decimal_successor(previous: tuple[int, ...], parts: tuple[int, ...]) -> bool:
    """True when `parts` follows `previous` in the same numbering run.

    Input:   the last accepted number, and the number on the new line, split
             into their parts.
    Output:  true when the new number is the next sibling or the first child of
             the old one. Any deeper part must be a first child (1).
    Effects: none.
    """

    previous_depth = len(previous)
    for depth in range(1, min(len(parts), previous_depth + 1) + 1):
        same_parent = parts[: depth - 1] == previous[: depth - 1]
        next_sibling = depth <= previous_depth and parts[depth - 1] == previous[depth - 1] + 1
        first_child = depth == previous_depth + 1 and parts[depth - 1] == 1
        deeper_parts_are_first = all(part == 1 for part in parts[depth:])
        if same_parent and (next_sibling or first_child) and deeper_parts_are_first:
            return True
    return False


def roman_numeral_value(token: str) -> int | None:
    """The value of a standard upper-case Roman numeral, or None.

    Input:   one token.
    Output:  1 to 3999 for a standard numeral from I to MMMCMXCIX; None for an
             empty token, a token that is not a standard numeral, or a
             lower-case token.
    Effects: none.
    """

    if token == "" or _ROMAN_NUMERAL.fullmatch(token) is None:
        return None
    total = 0
    for index, letter in enumerate(token):
        value = _ROMAN_VALUES[letter]
        followed_by_larger = index + 1 < len(token) and value < _ROMAN_VALUES[token[index + 1]]
        total += -value if followed_by_larger else value
    return total


def paren_readings(token: str) -> tuple[tuple[ParenStyle, int], ...]:
    """Every way to read a bracketed token, in a fixed order.

    Input:   the token between the brackets, without the brackets.
    Output:  the readings in the order LOWER, ROMAN, UPPER, DIGIT. A token
             with no reading gives an empty tuple.
    Effects: none.
    """

    readings: list[tuple[ParenStyle, int]] = []
    if len(token) == 1 and token in _LOWER_LETTERS:
        readings.append((ParenStyle.LOWER, _LOWER_LETTERS.index(token) + 1))
    elif len(token) == 2 and token[0] == token[1] and token[0] in _LOWER_LETTERS:
        readings.append((ParenStyle.LOWER, 27 + _LOWER_LETTERS.index(token[0])))

    if token != "" and _LOWER_ROMAN.fullmatch(token) is not None:
        roman_value = roman_numeral_value(token.upper())
        if roman_value is not None:
            readings.append((ParenStyle.ROMAN, roman_value))

    if len(token) == 1 and token in _UPPER_LETTERS:
        readings.append((ParenStyle.UPPER, _UPPER_LETTERS.index(token) + 1))

    if _DIGITS.fullmatch(token) is not None:
        readings.append((ParenStyle.DIGIT, int(token)))

    return tuple(readings)
