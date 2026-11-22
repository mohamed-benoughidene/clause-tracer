"""People by honorific, signature and job title (S4-M2-T7).

Code alone can find a person who is not a typed party by three marks: an
honorific, a signature line, and a name before a job title. Each seed also
gives its variants everywhere in the text (question 1).
"""

import re
from typing import Final

from clause_tracer.core import (
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
    fold_for_matching,
)
from clause_tracer.privacy._match import find_name_form
from clause_tracer.privacy._patterns import (
    HONORIFIC_PERSON_CAPS_RE,
    HONORIFIC_PERSON_RE,
    NAME_BEFORE_TITLE_RE,
    SIGNED_BY_CAPS_RE,
    SIGNED_BY_RE,
)
from clause_tracer.privacy._spans import unique_sorted
from clause_tracer.privacy.companies import COMPANY_LEAD_WORDS
from clause_tracer.privacy.names import (
    COMMON_WORD_NAMES,
    NAME_STOP_WORDS,
    fold_text,
    is_company_seed,
    name_forms,
)

LEGAL_STOP_WORDS: Final[frozenset[str]] = frozenset(
    {
        "agreement",
        "party",
        "parties",
        "schedule",
        "clause",
        "section",
        "annex",
        "appendix",
        "exhibit",
        "services",
        "service",
        "client",
        "customer",
        "supplier",
        "contractor",
        "consultant",
        "developer",
        "agency",
        "company",
        "employer",
        "employee",
        "licensor",
        "licensee",
        "buyer",
        "seller",
        "landlord",
        "tenant",
        "charges",
        "deliverables",
        "milestone",
        "effective",
        "date",
        "term",
        "confidential",
        "information",
        "intellectual",
        "property",
        "governing",
        "law",
        "force",
        "majeure",
        "termination",
        "payment",
        "fees",
        "notice",
        "notices",
        "director",
        "manager",
        "partner",
        "owner",
        "secretary",
    }
)
TRAILING_TITLE_WORDS: Final[frozenset[str]] = frozenset(
    {
        "director",
        "manager",
        "partner",
        "owner",
        "secretary",
        "ceo",
        "cfo",
        "chairman",
        "president",
        "managing",
        "chief",
        "executive",
        "officer",
    }
)
LEAD_STOP_WORDS: Final[frozenset[str]] = frozenset(
    word.casefold() for word in COMPANY_LEAD_WORDS
) | frozenset({"by", "for", "and", "of"})

_SEEDS: Final[tuple[tuple[re.Pattern[str], bool], ...]] = (
    (HONORIFIC_PERSON_RE, True),
    (HONORIFIC_PERSON_CAPS_RE, True),
    (SIGNED_BY_RE, False),
    (SIGNED_BY_CAPS_RE, False),
    (NAME_BEFORE_TITLE_RE, False),
)


def _clean_seed(match: re.Match[str], honorific: bool) -> tuple[int, int, str] | None:
    """Cut a match down to a person's name, or give `None` when no name is left."""

    group_start = match.start(1)
    tokens = [
        (group_start + token.start(), group_start + token.end(), token.group())
        for token in re.finditer(r"\S+", match.group(1))
    ]

    def key(token: tuple[int, int, str]) -> str:
        return token[2].strip(".,;:").casefold()

    while tokens and key(tokens[0]) in LEAD_STOP_WORDS:
        tokens = tokens[1:]
    while tokens and (
        key(tokens[-1]) in TRAILING_TITLE_WORDS or key(tokens[-1]) in LEGAL_STOP_WORDS
    ):
        tokens = tokens[:-1]
    if not tokens:
        return None
    if all(key(token) in LEGAL_STOP_WORDS for token in tokens):
        return None
    if not honorific and len(tokens) < 2:
        return None
    if is_company_seed(" ".join(token[2] for token in tokens)):
        return None
    first, last = tokens[0][0], tokens[-1][1]
    return (match.start() if honorific else first), last, match.string[first:last]


def find_people(text: str) -> tuple[PiiSuggestion, ...]:
    """Find people by honorific, signature and job title, with their variants.

    Input:   the contract text.
    Output:  one suggestion for each copy, sorted, with no duplicate.
    Raises:  nothing.
    Effects: none (T1).
    """

    key = fold_for_matching(text)
    suggestions: list[PiiSuggestion] = []
    seeds: list[str] = []
    seen: set[str] = set()
    for pattern, honorific in _SEEDS:
        for match in pattern.finditer(text):
            cleaned = _clean_seed(match, honorific)
            if cleaned is None:
                continue
            start, end, seed = cleaned
            suggestions.append(
                PiiSuggestion(
                    span=Span(start=start, end=end),
                    kind=PlaceholderKind.PERSON,
                    source=PiiSource.RULE,
                )
            )
            folded = fold_text(seed)
            if folded not in seen:
                seen.add(folded)
                seeds.append(folded)
    for seed in seeds:
        for form in name_forms(seed, PlaceholderKind.PERSON):
            for span in find_name_form(text, key, form, NAME_STOP_WORDS, COMMON_WORD_NAMES):
                suggestions.append(
                    PiiSuggestion(
                        span=span,
                        kind=PlaceholderKind.PERSON,
                        source=PiiSource.RULE,
                    )
                )
    return unique_sorted(suggestions)
