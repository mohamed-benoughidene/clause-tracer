"""The properties of invariant 3 (S4-M4-T6).

Anonymise then restore gives the original, the map tiles both texts, and no
planted name is left in the sent text.
"""

from hypothesis import given

from clause_tracer.core import (
    PLACEHOLDER_CLOSE,
    PLACEHOLDER_OPEN,
    Document,
    FakePiiDetector,
    PlaceholderEntity,
    PlaceholderText,
    SegmentKind,
    Span,
)
from clause_tracer.privacy._tokens import placeholder_token
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.placeholder import (
    anonymise,
    map_to_original,
    restore_reply,
    restore_text,
)
from clause_tracer.privacy.tests.strategies import SETTINGS, PlantedCase, planted_cases


def pipeline(planted: PlantedCase) -> tuple[PlaceholderText, tuple[PlaceholderEntity, ...]]:
    """Run the pipeline over one planted case and give the placeholder text."""

    document = planted.case.document
    suggestions = find_personal_data(
        planted.case, FakePiiDetector({document.text: planted.planted})
    )
    entities = group_entities(document, suggestions)
    return anonymise(document, entities), entities


def _sentence_starts(planted: PlantedCase) -> set[int]:
    return {sentence.span.start for clause in planted.case.clauses for sentence in clause.sentences}


def _first_text(document: Document, entity: PlaceholderEntity) -> str:
    first = min(entity.spans, key=lambda span: span.start)
    return document.text[first.start : first.end]


@SETTINGS
@given(planted_cases())
def test_restore_undoes_anonymise(planted: PlantedCase) -> None:
    placeholder, _ = pipeline(planted)

    assert restore_text(placeholder, planted.case.document) == planted.case.document.text


@SETTINGS
@given(planted_cases())
def test_segments_tile_both_texts(planted: PlantedCase) -> None:
    placeholder, _ = pipeline(planted)
    document = planted.case.document
    sent = 0
    original = 0
    for segment in placeholder.segments:
        assert segment.sent.start == sent
        assert segment.original.start == original
        sent = segment.sent.end
        original = segment.original.end
    assert sent == len(placeholder.text)
    assert original == len(document.text)
    for segment in placeholder.segments:
        sent_length = segment.sent.end - segment.sent.start
        original_length = segment.original.end - segment.original.start
        if segment.kind in (SegmentKind.COPY, SegmentKind.ESCAPE):
            assert sent_length == original_length


@SETTINGS
@given(planted_cases())
def test_no_entity_crosses_a_sentence_start(planted: PlantedCase) -> None:
    _, entities = pipeline(planted)
    starts = _sentence_starts(planted)

    for entity in entities:
        for span in entity.spans:
            assert not any(span.start < start < span.end for start in starts)


@SETTINGS
@given(planted_cases())
def test_markers_only_in_entities(planted: PlantedCase) -> None:
    placeholder, entities = pipeline(planted)
    tokens = {entity.id: placeholder_token(entity.kind, entity.number) for entity in entities}
    entity_segments = [
        segment for segment in placeholder.segments if segment.kind is SegmentKind.ENTITY
    ]

    assert placeholder.text.count(PLACEHOLDER_OPEN) == len(entity_segments)
    assert placeholder.text.count(PLACEHOLDER_CLOSE) == len(entity_segments)
    for segment in entity_segments:
        assert segment.entity_id is not None
        assert placeholder.text[segment.sent.start : segment.sent.end] == tokens[segment.entity_id]


@SETTINGS
@given(planted_cases())
def test_copy_spans_map_back_exactly(planted: PlantedCase) -> None:
    placeholder, _ = pipeline(planted)
    document = planted.case.document

    for segment in placeholder.segments:
        if segment.kind is not SegmentKind.COPY:
            continue
        if segment.sent.end - segment.sent.start < 2:
            continue
        start = segment.sent.start + 1
        end = segment.sent.end
        original = map_to_original(placeholder, Span(start=start, end=end))
        assert document.text[original.start : original.end] == placeholder.text[start:end]


@SETTINGS
@given(planted_cases())
def test_tokens_in_a_reply_come_back(planted: PlantedCase) -> None:
    placeholder, entities = pipeline(planted)
    document = planted.case.document
    reply = " | ".join(placeholder_token(entity.kind, entity.number) for entity in entities)
    expected = " | ".join(_first_text(document, entity) for entity in entities)

    assert restore_reply(placeholder, document, reply) == expected


@SETTINGS
@given(planted_cases())
def test_no_planted_name_is_left_in_the_sent_text(planted: PlantedCase) -> None:
    placeholder, _ = pipeline(planted)

    for name in planted.names:
        assert name.casefold() not in placeholder.text.casefold()
