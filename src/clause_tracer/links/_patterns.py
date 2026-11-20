"""The patterns that `links` reads (stage 3).

Every pattern that a task gives as a string constant lives here. It is
compiled once, next to the constant. Offsets are half-open and point into
the canonical text.
"""

import re
from typing import Final

ITEM_NUMBER: Final[str] = r"[0-9]{1,3}(?:\.[0-9]{1,3}){0,4}(?:\([0-9A-Za-z]{1,4}\)){0,3}"
ITEM_ARTICLE: Final[str] = (
    r"(?:[0-9]{1,3}|[IVXLC]{1,7})(?:\.[0-9]{1,3}){0,4}(?:\([0-9A-Za-z]{1,4}\)){0,3}"
)
ITEM_SCHEDULE: Final[str] = (
    r"(?:[0-9]{1,3}|[A-Z])(?:\.[0-9]{1,3}){0,4}(?:\([0-9A-Za-z]{1,4}\)){0,3}"
)
WRITTEN_NUMBER_RE: Final[re.Pattern[str]] = re.compile(ITEM_NUMBER)
ROMAN_RE: Final[re.Pattern[str]] = re.compile(
    r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"
)

DOCUMENT_WORDS: Final[str] = r"(?:[A-Z][a-z]+(?:-[A-Z][a-z]+)?\s+){1,4}"
DOCUMENT_NOUN: Final[str] = (
    r"(?:Agreement|Contract|Deed|Addendum|Licence|License|"
    r"Statement\s+of\s+Work|Terms\s+and\s+Conditions)"
)
OF_DOCUMENT: Final[str] = (
    r"\s+(?i:of|in|under)\s+(?:(?i:the)\s+)?" + DOCUMENT_WORDS + DOCUMENT_NOUN + r"(?![A-Za-z])"
)
OF_DOCUMENT_RE: Final[re.Pattern[str]] = re.compile(OF_DOCUMENT)

SEPARATOR: Final[str] = (
    r"(?:\s*,\s*(?:(?:and|or)\s+)?|\s+(?:and|or)\s+|\s+to\s+|\s*[-\u2013\u2014]\s*)"
)
SEPARATOR_RE: Final[re.Pattern[str]] = re.compile(SEPARATOR)

UNIT_AFTER: Final[str] = (
    r"(?!\s*(?:%|(?i:per\s?cent|percent|days?|weeks?|months?|years?|hours?|"
    r"business|working|calendar)(?![A-Za-z])|"
    r"(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)(?![A-Za-z])))"
)


def _reference_pattern(keywords: str, item: str) -> re.Pattern[str]:
    """Build one reference pattern; the group `items` holds every item."""

    guarded_item = f"(?:{item}){UNIT_AFTER}"
    return re.compile(
        rf"(?<![A-Za-z])(?P<kw>(?i:{keywords}))\s+"
        rf"(?P<items>(?:{guarded_item})(?:{SEPARATOR}(?:{guarded_item}))*)"
        rf"(?![0-9A-Za-z]|\.[0-9])"
    )


NUMBER_REFERENCE: Final[re.Pattern[str]] = _reference_pattern(
    "clauses?|sections?|paragraphs?|sub-clauses?|subclauses?", ITEM_NUMBER
)
ARTICLE_REFERENCE: Final[re.Pattern[str]] = _reference_pattern("articles?", ITEM_ARTICLE)
SCHEDULE_REFERENCE: Final[re.Pattern[str]] = _reference_pattern(
    "schedules?|annex(?:es)?|appendix|appendices|exhibits?", ITEM_SCHEDULE
)
