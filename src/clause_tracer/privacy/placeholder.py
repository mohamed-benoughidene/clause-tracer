"""The placeholder text and its segment map (S4-M4-T2 to T5).

The map holds spans, not copies of names (D3). Each entity span becomes one
token, each marker character of the contract becomes its own escape, and
every other run of characters is copied as it is (question 10).
"""

import re
from bisect import bisect_right
from collections.abc import Sequence
from typing import Final

from clause_tracer.core import (
    PLACEHOLDER_CLOSE,
    PLACEHOLDER_OPEN,
    Document,
    PlaceholderEntity,
    PlaceholderKind,
    PlaceholderText,
    Segment,
    SegmentKind,
    Span,
)
from clause_tracer.privacy._spans import overlaps
from clause_tracer.privacy._tokens import ESCAPES, placeholder_token

TOKEN_RE: Final[re.Pattern[str]] = re.compile(
    re.escape(PLACEHOLDER_OPEN)
    + "[^"
    + re.escape(PLACEHOLDER_OPEN)
    + re.escape(PLACEHOLDER_CLOSE)
    + "]*"
    + re.escape(PLACEHOLDER_CLOSE)
)


def _check_entities(text: str, entities: Sequence[PlaceholderEntity]) -> None:
    """Raise on the first fault of the entities, in the order the plan gives."""

    seen_ids: set[str] = set()
    for entity in entities:
        if entity.id in seen_ids:
            raise ValueError("privacy: duplicate entity id")
        seen_ids.add(entity.id)

    seen_placeholders: set[tuple[PlaceholderKind, int]] = set()
    for entity in entities:
        placeholder = (entity.kind, entity.number)
        if placeholder in seen_placeholders:
            raise ValueError("privacy: duplicate placeholder")
        seen_placeholders.add(placeholder)

    for entity in entities:
        if not entity.spans:
            raise ValueError("privacy: entity has no span")

    for entity in entities:
        for span in entity.spans:
            if span.start < 0 or span.end > len(text):
                raise ValueError("privacy: entity span is outside the text")

    for entity in entities:
        for span in entity.spans:
            if span.start >= span.end:
                raise ValueError("privacy: entity span is empty")

    ordered = sorted(
        (span for entity in entities for span in entity.spans),
        key=lambda span: (span.start, span.end),
    )
    for earlier, later in zip(ordered, ordered[1:], strict=False):
        if overlaps(earlier, later):
            raise ValueError("privacy: entity spans overlap")

    for entity in entities:
        if entity.number < 1:
            raise ValueError("privacy: a placeholder number starts at 1")


def _copy_gap(text: str, start: int, end: int, sent_start: int) -> tuple[str, list[Segment], int]:
    """Copy one stretch with no entity, with an escape for each marker character."""

    pieces: list[str] = []
    segments: list[Segment] = []
    sent = sent_start
    index = start
    while index < end:
        character = text[index]
        if character in ESCAPES:
            piece = ESCAPES[character]
            pieces.append(piece)
            segments.append(
                Segment(
                    kind=SegmentKind.ESCAPE,
                    sent=Span(start=sent, end=sent + 1),
                    original=Span(start=index, end=index + 1),
                    entity_id=None,
                )
            )
            sent += 1
            index += 1
            continue
        run_end = index
        while run_end < end and text[run_end] not in ESCAPES:
            run_end += 1
        pieces.append(text[index:run_end])
        segments.append(
            Segment(
                kind=SegmentKind.COPY,
                sent=Span(start=sent, end=sent + (run_end - index)),
                original=Span(start=index, end=run_end),
                entity_id=None,
            )
        )
        sent += run_end - index
        index = run_end
    return "".join(pieces), segments, sent


def anonymise(document: Document, entities: Sequence[PlaceholderEntity]) -> PlaceholderText:
    """Build the placeholder text and the segment map of one document.

    Input:   the document and the entities to replace.
    Output:  the placeholder text, the entities as given, and the segments.
    Raises:  ValueError on a duplicate id or placeholder, a missing, empty,
             outside or overlapping span, or a number below 1.
    Effects: none (T1).
    """

    text = document.text
    _check_entities(text, entities)

    ordered = sorted(
        ((span, entity) for entity in entities for span in entity.spans),
        key=lambda pair: pair[0].start,
    )
    pieces: list[str] = []
    segments: list[Segment] = []
    sent = 0
    original = 0
    for span, entity in ordered:
        gap_text, gap_segments, sent = _copy_gap(text, original, span.start, sent)
        pieces.append(gap_text)
        segments.extend(gap_segments)
        token = placeholder_token(entity.kind, entity.number)
        segments.append(
            Segment(
                kind=SegmentKind.ENTITY,
                sent=Span(start=sent, end=sent + len(token)),
                original=span,
                entity_id=entity.id,
            )
        )
        pieces.append(token)
        sent += len(token)
        original = span.end
    tail_text, tail_segments, sent = _copy_gap(text, original, len(text), sent)
    pieces.append(tail_text)
    segments.extend(tail_segments)
    return PlaceholderText(text="".join(pieces), entities=tuple(entities), segments=tuple(segments))


def _segments_run_on(placeholder: PlaceholderText, document: Document) -> bool:
    """Say whether the spans run on from 0 to the end of each text."""

    sent = 0
    original = 0
    for segment in placeholder.segments:
        if segment.sent.start != sent or segment.original.start != original:
            return False
        if segment.sent.end < segment.sent.start or segment.original.end < segment.original.start:
            return False
        sent = segment.sent.end
        original = segment.original.end
    return sent == len(placeholder.text) and original == len(document.text)


def _lengths_fit(segment: Segment) -> bool:
    """Say whether the two lengths of one segment suit its kind."""

    sent_length = segment.sent.end - segment.sent.start
    original_length = segment.original.end - segment.original.start
    if segment.kind is SegmentKind.COPY:
        return sent_length == original_length
    if segment.kind is SegmentKind.ESCAPE:
        return sent_length == 1 and original_length == 1
    if segment.kind is SegmentKind.ENTITY:
        return original_length >= 1
    return False


def _check_segments(placeholder: PlaceholderText, document: Document) -> None:
    """Raise unless the segments tile both texts and each kind has its lengths."""

    segments_run_on = _segments_run_on(placeholder, document)
    lengths_fit = all(_lengths_fit(segment) for segment in placeholder.segments)
    if not segments_run_on or not lengths_fit:
        raise ValueError("privacy: segments do not tile the texts")


def restore_text(placeholder: PlaceholderText, document: Document) -> str:
    """Rebuild the whole contract text from the placeholder text and the document.

    Input:   the placeholder text and the document that it came from.
    Output:  the contract text, with each copied part taken from the sent text.
    Raises:  ValueError when the segments do not tile both texts.
    Effects: none (T1).
    """

    _check_segments(placeholder, document)
    pieces: list[str] = []
    for segment in placeholder.segments:
        if segment.kind is SegmentKind.COPY:
            pieces.append(placeholder.text[segment.sent.start : segment.sent.end])
        else:
            pieces.append(document.text[segment.original.start : segment.original.end])
    return "".join(pieces)


def restore_reply(placeholder: PlaceholderText, document: Document, reply: str) -> str:
    """Put the names back into the tokens of one AI reply.

    Input:   the placeholder text, the document, and the reply to restore.
    Output:  the reply with each token replaced by the entity's first place.
    Raises:  ValueError for an entity with no span, a span outside the text,
             or a token that no entity of the placeholder text has.
    Effects: none (T1).
    """

    for entity in placeholder.entities:
        if not entity.spans:
            raise ValueError("privacy: entity has no span")
    for entity in placeholder.entities:
        for span in entity.spans:
            if span.start < 0 or span.end > len(document.text):
                raise ValueError("privacy: entity span is outside the text")

    first_text: dict[str, str] = {}
    for entity in placeholder.entities:
        first = min(entity.spans, key=lambda span: span.start)
        token = placeholder_token(entity.kind, entity.number)
        first_text[token] = document.text[first.start : first.end]

    def put_back(match: re.Match[str]) -> str:
        token = match.group(0)
        if token not in first_text:
            raise ValueError("privacy: unknown placeholder")
        return first_text[token]

    return TOKEN_RE.sub(put_back, reply)


def map_to_original(placeholder: PlaceholderText, span: Span) -> Span:
    """Map one span of the sent text back to a span of the contract text.

    Input:   the placeholder text and a non-empty span of its sent text.
    Output:  the matching span of the contract, with an edge inside a
             placeholder snapped out to the whole name.
    Raises:  ValueError for a span outside the text or an empty span.
    Effects: none (T1).
    """

    if span.start < 0 or span.end > len(placeholder.text):
        raise ValueError("privacy: span is outside the placeholder text")
    if span.start >= span.end:
        raise ValueError("privacy: an empty span has no place")

    sent_starts = [segment.sent.start for segment in placeholder.segments]
    first = placeholder.segments[bisect_right(sent_starts, span.start) - 1]
    last = placeholder.segments[bisect_right(sent_starts, span.end - 1) - 1]
    if first.kind is SegmentKind.ENTITY:
        original_start = first.original.start
    else:
        original_start = first.original.start + (span.start - first.sent.start)
    if last.kind is SegmentKind.ENTITY:
        original_end = last.original.end
    else:
        original_end = last.original.start + (span.end - last.sent.start)
    return Span(start=original_start, end=original_end)
