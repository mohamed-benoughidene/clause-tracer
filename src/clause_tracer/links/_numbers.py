"""Clause numbers: normalise, read Roman numbers, expand a range (S3-M2-T1).

A number is a dotted number with an optional bracketed tail, such as
`7.1(a)(i)`. The caller normalises a number once; `expand_range` trusts
that its arguments are normalised.
"""

from typing import Final

from clause_tracer.links._patterns import ROMAN_RE, WRITTEN_NUMBER_RE

MAX_RANGE: Final[int] = 50

_ROMAN_VALUES: Final[dict[str, int]] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


def normalise_number(written: str) -> str:
    """Drop leading zeros from each dotted part, and keep the tail as written.

    Raises ValueError when `written` is not a clause number at all.
    """

    if WRITTEN_NUMBER_RE.fullmatch(written) is None:
        raise ValueError(f"not a clause number: {written}")
    bracket = written.find("(")
    if bracket == -1:
        base, tail = written, ""
    else:
        base, tail = written[:bracket], written[bracket:]
    parts = [_strip_leading_zeros(part) for part in base.split(".")]
    return ".".join(parts) + tail


def roman_to_int(roman: str) -> int:
    """Return the value of a strict upper-case Roman number from 1 to 3999.

    Raises ValueError for anything else.
    """

    if roman == "" or ROMAN_RE.fullmatch(roman) is None:
        raise ValueError(f"not a Roman number: {roman}")
    total = 0
    for index, character in enumerate(roman):
        value = _ROMAN_VALUES[character]
        followed_by_larger = index + 1 < len(roman) and _ROMAN_VALUES[roman[index + 1]] > value
        if followed_by_larger:
            total -= value
        else:
            total += value
    return total


def expand_range(first: str, last: str) -> tuple[str, ...]:
    """Return every number from `first` to `last` when the range is plain.

    Input:   two normalised numbers.
    Output:  every number in the range, or `(first, last)` when the range
             cannot be expanded, or `(first,)` when both are equal.
    Effects: none.
    """

    first_base, first_tail = _split_tail(first)
    last_base, last_tail = _split_tail(last)
    first_parts = first_base.split(".")
    last_parts = last_base.split(".")
    same_prefix = first_parts[:-1] == last_parts[:-1]
    last_first = int(first_parts[-1])
    last_last = int(last_parts[-1])
    is_plain_range = (
        first_tail == ""
        and last_tail == ""
        and len(first_parts) == len(last_parts)
        and same_prefix
        and last_first < last_last
        and last_last - last_first + 1 <= MAX_RANGE
    )
    if not is_plain_range:
        return (first,) if first == last else (first, last)
    prefix = first_parts[:-1]
    return tuple(".".join([*prefix, str(value)]) for value in range(last_first, last_last + 1))


def _strip_leading_zeros(part: str) -> str:
    return part.lstrip("0") or "0"


def _split_tail(written: str) -> tuple[str, str]:
    bracket = written.find("(")
    if bracket == -1:
        return written, ""
    return written[:bracket], written[bracket:]
