"""The pattern finders: email, phone, ID and bank values (S4-M2-T2).

Each match covers the value only, never its keyword (question 5, the
owner's decision of 21 Nov 2026). A finder never removes an overlap: that
is the job of `resolve_overlaps` (S4-M3-T4).
"""

import re
from collections.abc import Callable
from typing import Final

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy._patterns import (
    ACCOUNT_NUMBER_RE,
    CARD_CUE_RE,
    CARD_CUE_WINDOW,
    CARD_FIRST_DIGITS,
    CARD_RE,
    COMPANY_PREFIX_RE,
    EMAIL_RE,
    GB_VAT_RE,
    GB_VAT_WEIGHTS,
    IBAN_RE,
    ID_KEYWORD_RE,
    NINO_RE,
    PHONE_RE,
    SORT_CODE_RE,
)
from clause_tracer.privacy._spans import unique_sorted

_PATTERNS: Final[tuple[tuple[re.Pattern[str], PlaceholderKind], ...]] = (
    (EMAIL_RE, PlaceholderKind.EMAIL),
    (PHONE_RE, PlaceholderKind.PHONE),
    (ID_KEYWORD_RE, PlaceholderKind.ID),
    (SORT_CODE_RE, PlaceholderKind.BANK),
    (ACCOUNT_NUMBER_RE, PlaceholderKind.BANK),
    (NINO_RE, PlaceholderKind.ID),
    (COMPANY_PREFIX_RE, PlaceholderKind.ID),
)


def _suggestion(start: int, end: int, kind: PlaceholderKind) -> PiiSuggestion:
    return PiiSuggestion(span=Span(start=start, end=end), kind=kind, source=PiiSource.PATTERN)


def iban_is_valid(candidate: str) -> bool:
    """Say whether an IBAN passes the mod-97 check.

    Input:   one candidate IBAN, with or without spaces.
    Output:  true only for 15 to 34 ASCII letters and digits that pass it.
    Raises:  nothing.
    Effects: none (T1).
    """

    compact = candidate.replace(" ", "")
    has_iban_length = 15 <= len(compact) <= 34
    has_iban_characters = compact.isascii() and compact.isalnum()
    starts_with_a_country = compact[:2].isalpha()
    if not (has_iban_length and has_iban_characters and starts_with_a_country):
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(int(character, 36)) for character in rearranged)
    return int(digits) % 97 == 1


def luhn_is_valid(digits: str) -> bool:
    """Say whether a string of digits passes the Luhn check."""

    if not digits or not digits.isdecimal():
        return False
    total = 0
    for index, character in enumerate(reversed(digits)):
        value = int(character)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def gb_vat_is_valid(candidate: str) -> bool:
    """Say whether a candidate GB VAT number passes its checksum."""

    digits = "".join(character for character in candidate if character.isdecimal())
    if len(digits) not in (9, 12):
        return False
    weighted = zip(GB_VAT_WEIGHTS, digits[:9], strict=True)
    remainder = sum(weight * int(digit) for weight, digit in weighted) % 97
    has_high_start = int(digits[:3]) >= 100
    return remainder == 0 or (has_high_start and remainder in (42, 55))


def has_card_cue(text: str, start: int) -> bool:
    """Say whether a card cue word lies in the 40 characters before `start`."""

    return CARD_CUE_RE.search(text, max(0, start - CARD_CUE_WINDOW), start) is not None


def card_is_valid(text: str, match: re.Match[str]) -> bool:
    """Say whether a card candidate passes the length, Luhn and gate rules."""

    digits = "".join(character for character in match.group() if character.isdecimal())
    has_card_length = 13 <= len(digits) <= 19
    has_issuer_digit = digits[0] in CARD_FIRST_DIGITS
    return (
        has_card_length
        and luhn_is_valid(digits)
        and (has_issuer_digit or has_card_cue(text, match.start()))
    )


_CHECKED: Final[
    tuple[tuple[re.Pattern[str], PlaceholderKind, Callable[[str, re.Match[str]], bool]], ...]
] = (
    (IBAN_RE, PlaceholderKind.BANK, lambda text, match: iban_is_valid(match.group())),
    (GB_VAT_RE, PlaceholderKind.ID, lambda text, match: gb_vat_is_valid(match.group())),
    (CARD_RE, PlaceholderKind.BANK, card_is_valid),
)


def find_patterns(text: str) -> tuple[PiiSuggestion, ...]:
    """Find emails, phones and keyword-gated ID and bank values.

    Input:   the contract text.
    Output:  one suggestion for each value, sorted, with no duplicate.
    Raises:  nothing.
    Effects: none (T1).
    """

    suggestions: list[PiiSuggestion] = []
    for pattern, kind in _PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span("v") if "v" in pattern.groupindex else match.span()
            suggestions.append(_suggestion(start, end, kind))
    for pattern, kind, is_valid in _CHECKED:
        for match in pattern.finditer(text):
            if is_valid(text, match):
                suggestions.append(_suggestion(match.start(), match.end(), kind))
    return unique_sorted(suggestions)
