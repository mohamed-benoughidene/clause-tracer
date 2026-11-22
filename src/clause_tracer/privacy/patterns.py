"""The pattern finders: email, phone, ID and bank values (S4-M2-T2).

Each match covers the value only, never its keyword (question 5, the
owner's decision of 21 Nov 2026). A finder never removes an overlap: that
is the job of `resolve_overlaps` (S4-M3-T4).
"""

import re
from typing import Final

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy._patterns import (
    ACCOUNT_NUMBER_RE,
    EMAIL_RE,
    ID_KEYWORD_RE,
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
            suggestions.append(
                PiiSuggestion(
                    span=Span(start=start, end=end),
                    kind=kind,
                    source=PiiSource.PATTERN,
                )
            )
    return unique_sorted(suggestions)
