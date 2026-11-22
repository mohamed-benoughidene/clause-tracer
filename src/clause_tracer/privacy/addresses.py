"""Addresses: street-anchored, and a chain built backwards from a postcode (S4-M2-T6).

The address runs from the house number, the unit word or the end of a cue
phrase to the last town, postcode or country. The chain looks back at most
5 comma segments and 120 characters, and never crosses a hard stop
(question 3). A chain that is too long keeps its nearest segments
(question 23, the owner's decision of 22 Nov 2026).
"""

from typing import Final

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy._patterns import (
    ABBREVIATION_END_RE,
    ADDRESS_RE,
    CA_POSTCODE_RE,
    CUE_RE,
    HARD_STOP_RE,
    START_TOKEN_RE,
    TAIL_RE,
    UK_POSTCODE_RE,
    US_ZIP_RE,
)
from clause_tracer.privacy._spans import unique_sorted

MAX_LENGTH: Final[int] = 120
MAX_SEGMENTS: Final[int] = 5


def _word_start(text: str, index: int) -> bool:
    """Say whether a word starts at `index`."""

    return index == 0 or not text[index - 1].isalnum()


def _chain_start(text: str, anchor_start: int, anchor_end: int) -> int | None:
    """The start of the address chain that ends at the anchor, or `None`."""

    budget = MAX_LENGTH - (anchor_end - anchor_start)
    low = max(0, anchor_start - max(budget, 0))
    window = text[low:anchor_start]
    cut = 0
    for stop in HARD_STOP_RE.finditer(window):
        if not ABBREVIATION_END_RE.search(window[: stop.start()]):
            cut = stop.end()
    base = low + cut
    segments: list[tuple[int, str]] = []
    position = 0
    for part in text[base:anchor_start].split(","):
        segments.append((base + position, part))
        position += len(part) + 1
    segments = segments[-MAX_SEGMENTS:]
    candidates: list[int] = []
    for index, (segment_start, segment) in enumerate(segments):
        found = [
            match
            for match in START_TOKEN_RE.finditer(segment)
            if _word_start(text, segment_start + match.start())
            and (segment_start + match.start() > low or low == 0 or not text[low - 1].isalnum())
        ]
        if found:
            match = found[-1] if index == 0 else found[0]
            candidates.append(segment_start + match.start())
            break
    first_start = segments[0][0] if segments else base
    cues = list(CUE_RE.finditer(text[first_start:anchor_start]))
    if cues:
        candidates.append(first_start + cues[-1].end())
    if candidates:
        return min(candidates)
    return _truncated_start(text, anchor_start, anchor_end)


def _truncated_start(text: str, anchor_start: int, anchor_end: int) -> int | None:
    """The earliest comma segment that keeps the chain within the limits."""

    base = 0
    for stop in HARD_STOP_RE.finditer(text, 0, anchor_start):
        if not ABBREVIATION_END_RE.search(text[max(0, stop.start() - 4) : stop.start()]):
            base = stop.end()
    region = text[base:anchor_start]
    has_start = CUE_RE.search(region) is not None or any(
        _word_start(text, base + match.start()) for match in START_TOKEN_RE.finditer(region)
    )
    if not has_start:
        return None
    starts: list[int] = []
    position = 0
    for part in region.split(","):
        starts.append(base + position + len(part) - len(part.lstrip(" \t")))
        position += len(part) + 1
    for start in starts[-MAX_SEGMENTS:]:
        if anchor_end - start <= MAX_LENGTH:
            return start
    return None


def find_addresses(text: str) -> tuple[PiiSuggestion, ...]:
    """Find street-anchored addresses and postcode chains.

    Input:   the contract text.
    Output:  one suggestion for each address, sorted, with no duplicate.
    Raises:  nothing.
    Effects: none (T1).
    """

    spans = [(match.start(), match.end()) for match in ADDRESS_RE.finditer(text)]
    for pattern in (UK_POSTCODE_RE, US_ZIP_RE, CA_POSTCODE_RE):
        for anchor in pattern.finditer(text):
            end = anchor.end()
            tail = TAIL_RE.match(text, end)
            if tail:
                end = tail.end()
            start = _chain_start(text, anchor.start(), end)
            spans.append((anchor.start() if start is None else start, end))
    spans.sort()
    merged: list[tuple[int, int]] = []
    for start, end in spans:
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return unique_sorted(
        PiiSuggestion(
            span=Span(start=start, end=end),
            kind=PlaceholderKind.ADDRESS,
            source=PiiSource.RULE,
        )
        for start, end in merged
    )
