"""Company names by suffix, with the words that lead them cut off (S4-M2-T5)."""

import re
from typing import Final

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy._patterns import COMPANY_RE
from clause_tracer.privacy._spans import unique_sorted

COMPANY_LEAD_WORDS: Final[tuple[str, ...]] = (
    "The",
    "This",
    "Each",
    "Any",
    "Such",
    "Our",
    "Your",
    "Its",
    "Their",
    "If",
    "Where",
    "Unless",
    "Pay",
    "Payment",
    "Notice",
    "Notices",
    "Invoice",
    "Deliver",
    "Send",
    "Contact",
    "Between",
    "Agreement",
    "Services",
    "Client",
    "Customer",
    "Please",
    "Notify",
    "Attention",
)
COMPANY_ROLE_WORDS: Final[frozenset[str]] = frozenset(
    {
        "agency",
        "developer",
        "client",
        "customer",
        "supplier",
        "contractor",
        "consultant",
        "company",
        "employer",
        "employee",
        "licensor",
        "licensee",
        "buyer",
        "seller",
        "landlord",
        "tenant",
        "party",
        "parties",
    }
)
_CONNECTORS: Final[frozenset[str]] = frozenset({"and", "&", "of"})


def find_companies(text: str) -> tuple[PiiSuggestion, ...]:
    """Find company names by their suffix.

    Input:   the contract text.
    Output:  one suggestion for each company, sorted, with no duplicate.
    Raises:  nothing.
    Effects: none (T1).
    """

    suggestions: list[PiiSuggestion] = []
    for match in COMPANY_RE.finditer(text):
        start, end = match.span()
        words = [
            (start + word.start(), word.group()) for word in re.finditer(r"\S+", text[start:end])
        ]
        first = 0
        for index in range(1, len(words) - 1):
            is_and_after_a_role = (
                words[index][1] == "and" and words[index - 1][1].casefold() in COMPANY_ROLE_WORDS
            )
            if is_and_after_a_role:
                first = index + 1
        while first < len(words) - 1 and (
            words[first][1] in COMPANY_LEAD_WORDS or words[first][1] in _CONNECTORS
        ):
            first += 1
        starts_with_a_lead_word = words[first][1] in COMPANY_LEAD_WORDS
        has_no_name_left = len(words) - first < 2
        if starts_with_a_lead_word or has_no_name_left:
            continue
        suggestions.append(
            PiiSuggestion(
                span=Span(start=words[first][0], end=end),
                kind=PlaceholderKind.COMPANY,
                source=PiiSource.RULE,
            )
        )
    return unique_sorted(suggestions)
