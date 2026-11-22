"""The placeholder text and its segment map (S4-M4-T2 to T5).

The map holds spans, not copies of names (D3). Each entity span becomes one
token, each marker character of the contract becomes its own escape, and
every other run of characters is copied as it is (question 10).
"""

from collections.abc import Sequence

from clause_tracer.core import (
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
