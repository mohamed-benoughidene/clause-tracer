"""`restore_text`, the whole text back (S4-M4-T3)."""

import dataclasses

import pytest

from clause_tracer.core import (
    Document,
    PlaceholderEntity,
    PlaceholderKind,
    PlaceholderText,
    Segment,
    SegmentKind,
    Span,
)
from clause_tracer.privacy.placeholder import anonymise, restore_text
from clause_tracer.privacy.tests.case_builder import make_case, span_of


def _document(text: str) -> Document:
    return make_case([text]).document if text else make_case([]).document


def _entity(
    text: str, needle: str, kind: PlaceholderKind = PlaceholderKind.PERSON
) -> PlaceholderEntity:
    return PlaceholderEntity(
        id="person-1",
        kind=kind,
        number=1,
        spans=(span_of(text, needle),),
    )


def test_restore_gives_the_original() -> None:
    text = "Hi Sam, hi Sam."
    document = _document(text)
    entity = PlaceholderEntity(
        id="person-1",
        kind=PlaceholderKind.PERSON,
        number=1,
        spans=(span_of(text, "Sam", 1), span_of(text, "Sam", 2)),
    )

    assert restore_text(anonymise(document, [entity]), document) == text


def test_restore_gives_the_original_with_escapes() -> None:
    text = "a ⟦b⟧ ⟦Sam⟧"
    document = _document(text)
    entity = _entity(text, "Sam")

    assert restore_text(anonymise(document, [entity]), document) == text


def test_restore_of_an_empty_text() -> None:
    document = _document("")

    assert restore_text(anonymise(document, []), document) == ""


def test_a_copy_comes_from_the_sent_text() -> None:
    text = "Hi Sam, hi Sam."
    document = _document(text)
    entity = PlaceholderEntity(
        id="person-1",
        kind=PlaceholderKind.PERSON,
        number=1,
        spans=(span_of(text, "Sam", 1), span_of(text, "Sam", 2)),
    )
    placeholder = anonymise(document, [entity])
    last = len(placeholder.text) - 1
    changed = dataclasses.replace(
        placeholder,
        text=placeholder.text[:last] + "!" + placeholder.text[last + 1 :],
    )

    assert restore_text(changed, document) == "Hi Sam, hi Sam!"


def test_a_gap_in_the_segments_raises() -> None:
    placeholder = PlaceholderText(
        text="abc",
        entities=(),
        segments=(
            Segment(
                kind=SegmentKind.COPY,
                sent=Span(start=0, end=1),
                original=Span(start=0, end=1),
                entity_id=None,
            ),
            Segment(
                kind=SegmentKind.COPY,
                sent=Span(start=2, end=3),
                original=Span(start=1, end=3),
                entity_id=None,
            ),
        ),
    )

    with pytest.raises(ValueError, match="privacy: segments do not tile the texts"):
        restore_text(placeholder, _document("abc"))


def test_a_wrong_length_raises() -> None:
    placeholder = PlaceholderText(
        text="abc",
        entities=(),
        segments=(
            Segment(
                kind=SegmentKind.COPY,
                sent=Span(start=0, end=2),
                original=Span(start=0, end=3),
                entity_id=None,
            ),
            Segment(
                kind=SegmentKind.COPY,
                sent=Span(start=2, end=3),
                original=Span(start=3, end=4),
                entity_id=None,
            ),
        ),
    )

    with pytest.raises(ValueError, match="privacy: segments do not tile the texts"):
        restore_text(placeholder, _document("abcd"))


def test_an_empty_entity_original_raises() -> None:
    placeholder = PlaceholderText(
        text="⟦Person 1⟧ab",
        entities=(),
        segments=(
            Segment(
                kind=SegmentKind.ENTITY,
                sent=Span(start=0, end=10),
                original=Span(start=0, end=0),
                entity_id="person-1",
            ),
            Segment(
                kind=SegmentKind.COPY,
                sent=Span(start=10, end=12),
                original=Span(start=0, end=2),
                entity_id=None,
            ),
        ),
    )

    with pytest.raises(ValueError, match="privacy: segments do not tile the texts"):
        restore_text(placeholder, _document("ab"))
