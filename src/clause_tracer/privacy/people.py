"""People by honorific, signature and job title (S4-M2-T7).

Code alone can find a person who is not a typed party by three marks: an
honorific, a signature line, and a name before a job title. Each seed also
gives its variants everywhere in the text (question 1).
"""

import re
from typing import Final

from clause_tracer.core import (
    MatchKey,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
    fold_for_matching,
)
from clause_tracer.privacy._match import find_name_form
from clause_tracer.privacy._patterns import (
    ENDING_AFTER_RE,
    HONORIFIC_PERSON_CAPS_RE,
    HONORIFIC_PERSON_RE,
    NAME_BEFORE_TITLE_RE,
    SIGNED_BY_CAPS_RE,
    SIGNED_BY_RE,
)
from clause_tracer.privacy._spans import unique_sorted
from clause_tracer.privacy.companies import COMPANY_LEAD_WORDS, COMPANY_ROLE_WORDS
from clause_tracer.privacy.names import (
    COMMON_WORD_NAMES,
    NAME_STOP_WORDS,
    fold_text,
    is_company_seed,
    name_forms,
)

LEGAL_STOP_WORDS: Final[frozenset[str]] = COMPANY_ROLE_WORDS | frozenset(
    {
        "agreement",
        "annex",
        "appendix",
        "charges",
        "clause",
        "confidential",
        "date",
        "deliverables",
        "director",
        "effective",
        "exhibit",
        "fees",
        "force",
        "governing",
        "information",
        "intellectual",
        "law",
        "majeure",
        "manager",
        "milestone",
        "notice",
        "notices",
        "owner",
        "partner",
        "payment",
        "property",
        "schedule",
        "secretary",
        "section",
        "service",
        "services",
        "term",
        "termination",
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
    if not honorific and len(tokens) < 2:
        return None
    if is_company_seed(" ".join(token[2] for token in tokens)):
        return None
    first, last = tokens[0][0], tokens[-1][1]
    return (match.start() if honorific else first), last, match.string[first:last]


def find_people(text: str, *, key: MatchKey | None = None) -> tuple[PiiSuggestion, ...]:
    """Find people by honorific, signature and job title, with their variants.

    Input:   the contract text.
    Output:  one suggestion for each copy, sorted, with no duplicate.
    Raises:  nothing.
    Effects: none (T1).
    """

    key = fold_for_matching(text) if key is None else key
    suggestions: list[PiiSuggestion] = []
    seeds: list[tuple[str, PlaceholderKind]] = []
    seen: set[tuple[str, PlaceholderKind]] = set()
    for pattern, honorific in _SEEDS:
        for match in pattern.finditer(text):
            cleaned = _clean_seed(match, honorific)
            if cleaned is None:
                continue
            start, end, seed = cleaned
            has_a_company_ending = ENDING_AFTER_RE.match(text, end) is not None
            kind = PlaceholderKind.COMPANY if has_a_company_ending else PlaceholderKind.PERSON
            suggestions.append(_rule_suggestion(Span(start=start, end=end), kind))
            found = (fold_text(seed), kind)
            if found not in seen:
                seen.add(found)
                seeds.append(found)
    for folded, kind in seeds:
        for form in name_forms(folded, PlaceholderKind.PERSON):
            for span in find_name_form(text, key, form, NAME_STOP_WORDS, COMMON_WORD_NAMES):
                suggestions.append(_rule_suggestion(span, kind))
    person_spans = {item.span for item in suggestions if item.kind == PlaceholderKind.PERSON}
    return unique_sorted(
        item
        for item in suggestions
        if item.kind == PlaceholderKind.PERSON or item.span not in person_spans
    )


def _rule_suggestion(span: Span, kind: PlaceholderKind) -> PiiSuggestion:
    return PiiSuggestion(span=span, kind=kind, source=PiiSource.RULE)
