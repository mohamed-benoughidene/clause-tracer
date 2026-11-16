"""Unit conversion, Rule 6 (Spec 5).

A fixed list of spellings is accepted for each unit; a unit not on the
list is unsure. Business days and working days never convert. One week
is 7 days, one month 30 days, one year 12 months or 365 days, in
either direction.
"""

import re
from decimal import Decimal
from fractions import Fraction

from clause_tracer.core.enums import ReasonCode, Unit

# The fixed spelling lists of Rule 6; the owner checks them (Spec 5).
_DAYS = ("day", "days", "calendar day", "calendar days")
_WEEKS = ("week", "weeks")
_MONTHS = ("month", "months")
_YEARS = ("year", "years")
_PERCENT = ("%", "percent", "per cent")
_ROUNDS = (
    "round",
    "rounds",
    "revision",
    "revisions",
    "round of revisions",
    "rounds of revisions",
)
_BUSINESS_DAYS = ("business day", "business days", "working day", "working days")

_FACTORS: dict[tuple[str, Unit], Fraction] = {
    ("days", Unit.DAYS): Fraction(1),
    ("weeks", Unit.DAYS): Fraction(7),
    ("months", Unit.DAYS): Fraction(30),
    ("years", Unit.DAYS): Fraction(365),
    ("days", Unit.MONTHS): Fraction(1, 30),
    ("weeks", Unit.MONTHS): Fraction(7, 30),
    ("months", Unit.MONTHS): Fraction(1),
    ("years", Unit.MONTHS): Fraction(12),
    ("percent", Unit.PERCENT): Fraction(1),
    ("rounds", Unit.ROUNDS): Fraction(1),
}

_SPACE_RUN = re.compile(r" +")


def _normalise(unit_as_written: str) -> str:
    """Lower case, strip, collapse space runs, drop one trailing dot."""

    spelling = _SPACE_RUN.sub(" ", unit_as_written.lower().strip())
    if spelling.endswith("."):
        spelling = spelling[:-1]
    return spelling


def _spelling_kind(spelling: str) -> str | ReasonCode:
    if spelling in _DAYS:
        return "days"
    if spelling in _WEEKS:
        return "weeks"
    if spelling in _MONTHS:
        return "months"
    if spelling in _YEARS:
        return "years"
    if spelling in _PERCENT:
        return "percent"
    if spelling in _ROUNDS:
        return "rounds"
    if spelling in _BUSINESS_DAYS:
        return ReasonCode.BUSINESS_DAYS
    return ReasonCode.UNIT_UNKNOWN


def convert_to_unit(
    number: Decimal, unit_as_written: str | None, target: Unit
) -> Fraction | ReasonCode:
    """The number in the target unit, or the reason it could not convert (Rule 6)."""

    if unit_as_written is None:
        # No unit as written: the number is already in the target unit
        # (question 16a).
        return Fraction(number)
    kind = _spelling_kind(_normalise(unit_as_written))
    if isinstance(kind, ReasonCode):
        return kind
    factor = _FACTORS.get((kind, target))
    if factor is None:
        return ReasonCode.UNIT_UNKNOWN
    return Fraction(number) * factor
