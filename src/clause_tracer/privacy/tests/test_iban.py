"""IBAN patterns and the mod-97 check (S4-M2-T3)."""

from clause_tracer.core import PlaceholderKind
from clause_tracer.privacy.patterns import find_patterns, iban_is_valid


def test_valid_iban() -> None:
    assert iban_is_valid("GB82 WEST 1234 5698 7654 32")


def test_compact_iban_is_valid() -> None:
    assert iban_is_valid("GB82WEST12345698765432")


def test_german_iban_is_valid() -> None:
    assert iban_is_valid("DE89 3704 0044 0532 0130 00")


def test_changed_digit_is_invalid() -> None:
    assert not iban_is_valid("GB83 WEST 1234 5698 7654 32")


def test_too_short_is_invalid() -> None:
    assert not iban_is_valid("GB82")


def test_find_patterns_keeps_only_valid_ibans() -> None:
    text = "Pay to GB82 WEST 1234 5698 7654 32 or GB83 WEST 1234 5698 7654 32."
    results = [
        (suggestion.span.start, suggestion.span.end, suggestion.kind)
        for suggestion in find_patterns(text)
    ]

    assert results == [(7, 34, PlaceholderKind.BANK)]
