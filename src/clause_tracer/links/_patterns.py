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
SEPARATOR_SPLIT_RE: Final[re.Pattern[str]] = re.compile(f"({SEPARATOR})")

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

THIS_REFERENCE: Final[str] = (
    r"(?<![A-Za-z])(?i:this)\s+"
    r"(?P<kw>(?i:clause|section|paragraph|sub-clause|subclause|schedule|annex|"
    r"appendix|exhibit))"
    r"(?![A-Za-z])(?!\s*[0-9])(?!\s+[IVXLC]+(?![A-Za-z]))(?!\s+[A-Z](?![A-Za-z]))"
)
THIS_REFERENCE_RE: Final[re.Pattern[str]] = re.compile(THIS_REFERENCE)

QUOTE_OPEN: Final[str] = "[\"\u201c\u2018']"
QUOTE_CLOSE: Final[str] = "[\"\u201d\u2019']"
TERM: Final[str] = r"[A-Z][A-Za-z0-9]*(?:[ \-][A-Za-z0-9]+){0,5}"

MEANS_DEFINITION: Final[str] = (
    QUOTE_OPEN
    + r"(?:(?i:the)\s+)?(?P<term>"
    + TERM
    + ")"
    + QUOTE_CLOSE
    + r"\s+(?:means|shall\s+mean|has\s+the\s+meaning)\b"
)
MEANS_DEFINITION_RE: Final[re.Pattern[str]] = re.compile(MEANS_DEFINITION)

BRACKET_DEFINITION: Final[str] = (
    r"\(\s*(?:(?i:each|together|collectively)\s+)?(?:(?i:the|a|an)\s+)?"
    + QUOTE_OPEN
    + r"(?:(?i:the)\s+)?(?P<term>"
    + TERM
    + ")"
    + QUOTE_CLOSE
    + r"\s*\)"
)
BRACKET_DEFINITION_RE: Final[re.Pattern[str]] = re.compile(BRACKET_DEFINITION)

SENTENCE_LEAD: Final[str] = (
    r"[\s#*>\-_]*(?:(?:\([0-9A-Za-z]{1,4}\)|[0-9]{1,3}(?:\.[0-9]{1,3}){0,4}\.?|"
    r"[A-Za-z]\)|[ivx]{1,4}\)|(?i:clause|article|schedule|annex|appendix|exhibit)"
    r"[ \t]+[0-9A-Z]{1,5}\.?)[ \t]+)?"
)
SENTENCE_LEAD_RE: Final[re.Pattern[str]] = re.compile(SENTENCE_LEAD)
LIST_LEAD_END: Final[str] = r"[:;,]\s*$"
LIST_LEAD_END_RE: Final[re.Pattern[str]] = re.compile(LIST_LEAD_END)
AND_LEAD_END: Final[str] = r"\s(?i:and|or)\s+$"
AND_LEAD_END_RE: Final[re.Pattern[str]] = re.compile(AND_LEAD_END)

OUTSIDE_DOCUMENT: Final[str] = (
    r"(?<![A-Za-z])" + DOCUMENT_WORDS + DOCUMENT_NOUN + r"(?![A-Za-z])(?!\s+[A-Z][a-z])"
)
OUTSIDE_DOCUMENT_RE: Final[re.Pattern[str]] = re.compile(OUTSIDE_DOCUMENT)
OUTSIDE_NAME_RE: Final[re.Pattern[str]] = re.compile(DOCUMENT_WORDS + DOCUMENT_NOUN)
DROPPED_FIRST_WORDS: Final[frozenset[str]] = frozenset(
    {
        "The",
        "This",
        "That",
        "These",
        "Those",
        "Each",
        "Any",
        "Such",
        "Our",
        "Your",
        "Its",
        "Their",
        "Under",
        "As",
        "In",
        "Of",
        "For",
        "By",
        "With",
        "See",
        "If",
        "Where",
        "Unless",
        "Subject",
    }
)
THIS_BEFORE: Final[str] = r"(?i:\bthis)\s+$"
THIS_BEFORE_RE: Final[re.Pattern[str]] = re.compile(THIS_BEFORE)
OWN_NAME_MEANS: Final[str] = (
    QUOTE_CLOSE
    + r"\s+(?:means|shall\s+mean|has\s+the\s+meaning)\s+(?i:this\s+(?:agreement|contract|deed))"
    + r"(?![A-Za-z])"
)
OWN_NAME_MEANS_RE: Final[re.Pattern[str]] = re.compile(OWN_NAME_MEANS)
OWN_NAME_BRACKET: Final[str] = (
    r"(?i:\bthis\s+(?:[A-Za-z]+\s+){0,3}(?:agreement|contract|deed))"
    + r"\s*\(\s*(?:(?i:each|together|collectively)\s+)?(?:(?i:the|a|an)\s+)?"
    + QUOTE_OPEN
    + r"(?:(?i:the)\s+)?$"
)
OWN_NAME_BRACKET_RE: Final[re.Pattern[str]] = re.compile(OWN_NAME_BRACKET)

UNDEFINED_RUN: Final[str] = r"(?<![A-Za-z])[A-Z][a-z]+(?: [A-Z][a-z]+){1,3}(?![A-Za-z])"
UNDEFINED_RUN_RE: Final[re.Pattern[str]] = re.compile(UNDEFINED_RUN)
