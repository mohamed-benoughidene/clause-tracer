"""Placeholder tokens and escapes (S4-M4-T1).

A token is the form the scan of `core` reads as a known placeholder. Each
marker character of the contract is escaped, so it never reads as a token.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from clause_tracer.core import PLACEHOLDER_CLOSE, PLACEHOLDER_OPEN, PlaceholderKind

LABELS: Final[Mapping[PlaceholderKind, str]] = MappingProxyType(
    {
        PlaceholderKind.PERSON: "Person",
        PlaceholderKind.COMPANY: "Company",
        PlaceholderKind.ADDRESS: "Address",
        PlaceholderKind.EMAIL: "Email",
        PlaceholderKind.PHONE: "Phone",
        PlaceholderKind.ID: "ID",
        PlaceholderKind.BANK: "Bank",
    }
)

ESCAPES: Final[Mapping[str, str]] = MappingProxyType(
    {PLACEHOLDER_OPEN: "[", PLACEHOLDER_CLOSE: "]"}
)


def placeholder_token(kind: PlaceholderKind, number: int) -> str:
    """Return the token of one placeholder, such as `⟦Person 1⟧`.

    Input:   a placeholder kind and its number, from 1.
    Output:  the token, with the marker characters of `core`.
    Raises:  ValueError when the number is below 1.
    Effects: none (T1).
    """

    if number < 1:
        raise ValueError("privacy: a placeholder number starts at 1")
    return f"{PLACEHOLDER_OPEN}{LABELS[kind]} {number}{PLACEHOLDER_CLOSE}"
