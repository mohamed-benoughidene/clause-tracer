"""The output scans of every AI step (Spec 6.2, system design 8.2).

The scans look for what must never reach the screen: law words, advice,
injection tells, contact words, addresses, and the style signs of
ux-copy 1.1. A listed word or phrase matches as a whole word or phrase,
in any letter case, with curly apostrophes made straight. An empty
result means the text passed. When a scan fails, the AI is asked once
more; if that fails too, the code template is used.
"""

import re
from collections.abc import Mapping
from types import MappingProxyType

from clause_tracer.core.enums import Level, ScanFinding, TextSlot
from clause_tracer.core.scan_rules import (
    ADVICE_PHRASES,
    CONTACT_WORDS,
    INJECTION_PHRASES,
    LAW_WORDS,
    LENGTH_CAPS,
)

WEB_ADDRESS_PATTERN = re.compile(
    r"\bhttps?://\S+|\bwww\.\S+|\b(?:[a-z0-9-]+\.)+(?:com|org|net|io|co|uk|eu|info|biz|dev|app|me|ai)\b",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")

LABEL_WORDS: Mapping[Level, tuple[str, ...]] = MappingProxyType(
    {
        Level.PREFERRED: ("preferred",),
        Level.ACCEPTABLE: ("acceptable",),
        Level.WALK_AWAY: ("walk-away", "walk away"),
        Level.UNSURE: ("unsure",),
    }
)

_WORD_LIST_SCANS: tuple[tuple[ScanFinding, tuple[str, ...]], ...] = (
    (ScanFinding.LAW_WORD, LAW_WORDS),
    (ScanFinding.ADVICE, ADVICE_PHRASES),
    (ScanFinding.INJECTION_TELL, INJECTION_PHRASES),
    (ScanFinding.CONTACT_WORD, CONTACT_WORDS),
)


def contains_phrase(text: str, phrase: str) -> bool:
    """True when the phrase appears as a whole word or phrase, any case.

    Curly apostrophes in the text are made straight first, so a listed
    phrase written with straight ones matches (question 17a).
    """

    straight = text.replace("‘", "'").replace("’", "'")
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, straight, re.IGNORECASE) is not None


def scan_text(text: str, slot: TextSlot, label: Level | None) -> tuple[ScanFinding, ...]:
    """The word and pattern scans of one piece of AI text.

    TOO_LONG over the slot's cap; law words, advice, injection tells and
    contact words from the owner's lists; web and email addresses; and a
    label word of another level, which reads as ordinary English but is
    still flagged (question 17d). Findings in ScanFinding member order,
    no repeats.
    """

    findings: list[ScanFinding] = []
    too_long = len(text) > LENGTH_CAPS[slot]
    if too_long:
        findings.append(ScanFinding.TOO_LONG)
    for finding, words in _WORD_LIST_SCANS:
        found = any(contains_phrase(text, word) for word in words)
        if found:
            findings.append(finding)
    if WEB_ADDRESS_PATTERN.search(text) is not None:
        findings.append(ScanFinding.WEB_ADDRESS)
    if EMAIL_PATTERN.search(text) is not None:
        findings.append(ScanFinding.EMAIL_ADDRESS)
    other_label_word = label is not None and any(
        contains_phrase(text, word)
        for level, words in LABEL_WORDS.items()
        if level != label
        for word in words
    )
    if other_label_word:
        findings.append(ScanFinding.WRONG_LABEL_WORD)
    return tuple(findings)
