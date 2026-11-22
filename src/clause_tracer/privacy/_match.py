"""Find whole words and name forms through the match key (S4-M1-T6)."""

from typing import Final

from clause_tracer.core import MatchKey, Span
from clause_tracer.privacy._patterns import (
    CLAUSE_NUMBER_RE,
    HEADING_WORD_RE,
    HONORIFIC_BEFORE_RE,
    SENTENCE_MARK_RE,
)

_OPENERS: Final[str] = " \t\"“‘'("


def find_word(key: MatchKey, needle: str) -> tuple[Span, ...]:
    """Find every whole-word hit of `needle`, already folded, in `key.text`."""

    if not needle:
        return ()
    spans: list[Span] = []
    position = 0
    while True:
        index = key.text.find(needle, position)
        if index < 0:
            break
        end = index + len(needle)
        starts_a_word = index == 0 or not key.text[index - 1].isalnum()
        ends_a_word = end == len(key.text) or not key.text[end].isalnum()
        if starts_a_word and ends_a_word:
            spans.append(Span(start=key.to_canonical[index], end=key.to_canonical[end]))
            position = end
        else:
            position = index + 1
    return tuple(spans)


def find_name_form(
    text: str,
    key: MatchKey,
    form: str,
    stop_words: frozenset[str],
    ambiguous_words: frozenset[str],
) -> tuple[Span, ...]:
    """Find a folded form of a name, with the stop-word and layer 3 guards."""

    if " " in form:
        return find_word(key, form)
    if form in stop_words:
        return ()
    spans: list[Span] = []
    for span in find_word(key, form):
        if not text[span.start].isupper():
            continue
        if form in ambiguous_words and not _ambiguous_ok(text, span):
            continue
        spans.append(span)
    return tuple(spans)


def _line_bounds(text: str, index: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    return start, (len(text) if end < 0 else end)


def _is_heading(line: str) -> bool:
    if SENTENCE_MARK_RE.search(line):
        return False
    words = HEADING_WORD_RE.findall(line)
    return bool(words) and all(word[0].isupper() for word in words)


def _sentence_initial(text: str, index: int) -> bool:
    line_start, _ = _line_bounds(text, index)
    if CLAUSE_NUMBER_RE.match(text[line_start:index]):
        return True
    j = index
    while j > 0 and text[j - 1] in _OPENERS:
        j -= 1
    if j == 0:
        return True
    if text[j - 1] in ".!?":
        return True
    if text[j - 1] == "\n":
        before = text[: j - 1]
        return not before.strip() or before.rstrip(" \t").endswith((".", "!", "?"))
    return False


def _ambiguous_ok(text: str, span: Span) -> bool:
    if text[span.end : span.end + 2] in ("'s", "’s"):
        return True
    if HONORIFIC_BEFORE_RE.search(text[max(0, span.start - 8) : span.start]):
        return True
    if _sentence_initial(text, span.start):
        return False
    line_start, line_end = _line_bounds(text, span.start)
    return not _is_heading(text[line_start:line_end])
