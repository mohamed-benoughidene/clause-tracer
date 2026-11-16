"""The output scans of every AI step (Spec 6.2, system design 8.2).

The scans look for what must never reach the screen: law words, advice,
injection tells, contact words, addresses, and the style signs of
ux-copy 1.1. A listed word or phrase matches as a whole word or phrase,
in any letter case, with curly apostrophes made straight. An empty
result means the text passed. When a scan fails, the AI is asked once
more; if that fails too, the code template is used.
"""

import re
from collections.abc import Iterable, Mapping
from types import MappingProxyType

from clause_tracer.core.checks import ScanContext
from clause_tracer.core.enums import Level, ScanFinding, TextSlot
from clause_tracer.core.quote_fold import fold_for_quote_check
from clause_tracer.core.scan_rules import (
    ABBREVIATIONS,
    ADVICE_PHRASES,
    CONTACT_WORDS,
    EVALUATIVE_WORDS,
    FILLER_PHRASES,
    FIRST_PERSON_WORDS,
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

# The user speaks in the message and the question to ask, so the
# first-person scan leaves both out (question 18a).
FIRST_PERSON_SLOTS: frozenset[TextSlot] = frozenset(
    {TextSlot.REASON, TextSlot.READING, TextSlot.REWRITE}
)

# The style scans compare the text with what the AI was given: the
# template message or the clause for a rewrite, the quote for the rest
# (question 18b).
_SOURCE_SLOTS: frozenset[TextSlot] = frozenset({TextSlot.MESSAGE, TextSlot.REWRITE})

_ABBREVIATION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (abbreviation, re.compile(r"(?<![\w.])" + re.escape(abbreviation), re.IGNORECASE))
    for abbreviation in ABBREVIATIONS
)

# A reason needs an anchor: a clause number given to the step, or a
# quoted word of at least four letters that is in the quote (Spec 6.2).
MIN_ANCHOR_LETTERS = 4
QUOTED_RUN_PATTERN = re.compile(r'"([^"]+)"')

# One or more of ".", "?" and "!", then any closing quotes or brackets,
# then a space, a line break or the end of the text. "1.5" does not end
# a sentence, and the listed abbreviations are masked out first. The
# stage 2 splitter (NUPunkt) is not used here: core imports no other
# module, and both texts of a comparison are counted by this one rule.
SENTENCE_END_PATTERN = re.compile(r"[.?!]+[\"'’”)\]]*(?=\s|$)")


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


def mask_abbreviations(text: str) -> str:
    """Blank out every listed abbreviation with spaces, keeping the length.

    Both texts of a comparison are masked, so "i.e." is never read as
    the first-person "I". Anything the mask covers cannot match.
    """

    masked = text
    for abbreviation, pattern in _ABBREVIATION_PATTERNS:
        masked = pattern.sub(" " * len(abbreviation), masked)
    return masked


def _added_words(text: str, source: str | None, words: tuple[str, ...]) -> bool:
    """True when some listed word is in the text but not in its source.

    The scans look for words the AI added, so a word that is already in
    the text the AI was given passes (question 18b).
    """

    for word in words:
        in_text = contains_phrase(text, word)
        in_source = source is not None and contains_phrase(source, word)
        if in_text and not in_source:
            return True
    return False


def scan_style(text: str, slot: TextSlot, context: ScanContext) -> tuple[ScanFinding, ...]:
    """The style scans: signs of machine-made text (ux-copy 1.1).

    A listed word counts only when the AI added it, comparing the text
    with its quote, or with the message or clause a rewrite starts from.
    An exclamation mark counts as filler unless the source holds one.
    Findings in ScanFinding member order, no repeats.
    """

    source = context.source_text if slot in _SOURCE_SLOTS else context.quote
    findings: list[ScanFinding] = []
    if slot in FIRST_PERSON_SLOTS:
        masked_text = mask_abbreviations(text)
        masked_source = mask_abbreviations(source) if source is not None else None
        first_person_added = _added_words(masked_text, masked_source, FIRST_PERSON_WORDS)
        if first_person_added:
            findings.append(ScanFinding.FIRST_PERSON)
    filler_added = _added_words(text, source, FILLER_PHRASES)
    exclamation_added = "!" in text and (source is None or "!" not in source)
    if filler_added or exclamation_added:
        findings.append(ScanFinding.FILLER_PHRASE)
    if _added_words(text, source, EVALUATIVE_WORDS):
        findings.append(ScanFinding.EVALUATIVE_WORD)
    if slot is TextSlot.REASON:
        anchored = has_clause_number(text, context.clause_numbers) or has_quoted_word(
            text, context.quote
        )
        if not anchored:
            findings.append(ScanFinding.NO_ANCHOR)
    may_add_sentences = slot is TextSlot.MESSAGE or (
        slot is TextSlot.REWRITE and not context.instruction_given
    )
    if may_add_sentences:
        no_source = context.source_text is None
        more_than_source = context.source_text is not None and count_sentences(
            text
        ) > count_sentences(context.source_text)
        if no_source or more_than_source:
            findings.append(ScanFinding.ADDED_SENTENCE)
    return tuple(findings)


def count_sentences(text: str) -> int:
    """The number of sentences by the scans' own small rule.

    A sentence ends at ".", "?" or "!" followed by a space or the end of
    the text; "1.5" and the listed abbreviations do not end one, and
    text with no end mark is one sentence. Pieces with no letter or
    digit, such as the tail after a final mark, do not count.
    """

    pieces = SENTENCE_END_PATTERN.split(mask_abbreviations(text))
    return sum(1 for piece in pieces if any(character.isalnum() for character in piece))


def has_clause_number(text: str, clause_numbers: Iterable[str]) -> bool:
    """True when the text names one of the clause numbers the step was given.

    The whole number must appear alone: "5.4" is found in "Read 5.4."
    but not in "5.40" or "15.4".
    """

    for number in clause_numbers:
        stripped = number.strip()
        if stripped == "":
            continue
        pattern = r"(?<![\w.])" + re.escape(stripped) + r"(?!\w|\.\w)"
        if re.search(pattern, text, re.IGNORECASE) is not None:
            return True
    return False


def has_quoted_word(text: str, quote: str | None) -> bool:
    """True when the text quotes a word of at least four letters that is
    in the quote the reason rests on. Both texts are folded first, so
    curly double quotes count as straight ones."""

    if quote is None:
        return False
    folded = fold_for_quote_check(text).text
    folded_quote = fold_for_quote_check(quote).text
    for match in QUOTED_RUN_PATTERN.finditer(folded):
        run = match.group(1).strip(" .,;:!?")
        enough_letters = sum(character.isalpha() for character in run) >= MIN_ANCHOR_LETTERS
        if enough_letters and contains_phrase(folded_quote, run):
            return True
    return False
