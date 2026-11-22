"""`anonymise` and its segment map (S4-M4-T2)."""

import pytest

from clause_tracer.core import (
    Document,
    PlaceholderEntity,
    PlaceholderKind,
    Segment,
    SegmentKind,
    Span,
)
from clause_tracer.privacy.placeholder import anonymise
from clause_tracer.privacy.tests.case_builder import make_case


def entity(
    entity_id: str,
    kind: PlaceholderKind,
    number: int,
    *spans: Span,
) -> PlaceholderEntity:
    return PlaceholderEntity(id=entity_id, kind=kind, number=number, spans=spans)


def document(text: str) -> Document:
    return make_case([text]).document if text else make_case([]).document


def test_entities_become_tokens() -> None:
    result = anonymise(
        document("Hi Sam, hi Sam."),
        [
            entity(
                "person-1", PlaceholderKind.PERSON, 1, Span(start=3, end=6), Span(start=11, end=14)
            )
        ],
    )

    assert result.text == "Hi ⟦Person 1⟧, hi ⟦Person 1⟧."
    assert result.segments == (
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=0, end=3),
            original=Span(start=0, end=3),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.ENTITY,
            sent=Span(start=3, end=13),
            original=Span(start=3, end=6),
            entity_id="person-1",
        ),
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=13, end=18),
            original=Span(start=6, end=11),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.ENTITY,
            sent=Span(start=18, end=28),
            original=Span(start=11, end=14),
            entity_id="person-1",
        ),
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=28, end=29),
            original=Span(start=14, end=15),
            entity_id=None,
        ),
    )


def test_marker_characters_are_escaped() -> None:
    result = anonymise(document("a ⟦b⟧ c"), [])

    assert result.text == "a [b] c"
    assert result.segments == (
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=0, end=2),
            original=Span(start=0, end=2),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.ESCAPE,
            sent=Span(start=2, end=3),
            original=Span(start=2, end=3),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=3, end=4),
            original=Span(start=3, end=4),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.ESCAPE,
            sent=Span(start=4, end=5),
            original=Span(start=4, end=5),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=5, end=7),
            original=Span(start=5, end=7),
            entity_id=None,
        ),
    )


def test_an_escape_next_to_an_entity() -> None:
    result = anonymise(
        document("⟦Sam"),
        [entity("person-1", PlaceholderKind.PERSON, 1, Span(start=1, end=4))],
    )

    assert result.text == "[⟦Person 1⟧"
    assert result.segments == (
        Segment(
            kind=SegmentKind.ESCAPE,
            sent=Span(start=0, end=1),
            original=Span(start=0, end=1),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.ENTITY,
            sent=Span(start=1, end=11),
            original=Span(start=1, end=4),
            entity_id="person-1",
        ),
    )


def test_an_entity_over_a_marker_is_replaced_whole() -> None:
    result = anonymise(
        document("x⟦y"),
        [entity("person-1", PlaceholderKind.PERSON, 1, Span(start=1, end=3))],
    )

    assert result.text == "x⟦Person 1⟧"
    assert result.segments == (
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=0, end=1),
            original=Span(start=0, end=1),
            entity_id=None,
        ),
        Segment(
            kind=SegmentKind.ENTITY,
            sent=Span(start=1, end=11),
            original=Span(start=1, end=3),
            entity_id="person-1",
        ),
    )


def test_no_entities_copies_the_text() -> None:
    result = anonymise(document("abc"), [])

    assert result.text == "abc"
    assert result.segments == (
        Segment(
            kind=SegmentKind.COPY,
            sent=Span(start=0, end=3),
            original=Span(start=0, end=3),
            entity_id=None,
        ),
    )
    assert anonymise(document(""), []).segments == ()


def test_entities_are_kept_as_given() -> None:
    entities = [
        entity("person-1", PlaceholderKind.PERSON, 1, Span(start=3, end=6)),
        entity("company-1", PlaceholderKind.COMPANY, 1, Span(start=8, end=11)),
    ]

    assert anonymise(document("Hi Sam, Ac."), entities).entities == tuple(entities)


def test_two_kinds_have_their_own_tokens() -> None:
    result = anonymise(
        document("at Home"),
        [entity("address-2", PlaceholderKind.ADDRESS, 2, Span(start=3, end=7))],
    )

    assert result.text == "at ⟦Address 2⟧"


def test_duplicate_entity_id_raises() -> None:
    with pytest.raises(ValueError, match="privacy: duplicate entity id"):
        anonymise(
            document("ab"),
            [
                entity("person-1", PlaceholderKind.PERSON, 1, Span(start=0, end=1)),
                entity("person-1", PlaceholderKind.PERSON, 2, Span(start=1, end=2)),
            ],
        )


def test_duplicate_placeholder_raises() -> None:
    with pytest.raises(ValueError, match="privacy: duplicate placeholder"):
        anonymise(
            document("ab"),
            [
                entity("person-1", PlaceholderKind.PERSON, 1, Span(start=0, end=1)),
                entity("person-2", PlaceholderKind.PERSON, 1, Span(start=1, end=2)),
            ],
        )


def test_entity_without_a_span_raises() -> None:
    with pytest.raises(ValueError, match="privacy: entity has no span"):
        anonymise(document("ab"), [entity("person-1", PlaceholderKind.PERSON, 1)])


def test_empty_span_raises() -> None:
    with pytest.raises(ValueError, match="privacy: entity span is empty"):
        anonymise(
            document("ab"),
            [entity("person-1", PlaceholderKind.PERSON, 1, Span(start=1, end=1))],
        )


def test_span_outside_the_text_raises() -> None:
    with pytest.raises(ValueError, match="privacy: entity span is outside the text"):
        anonymise(
            document("ab"),
            [entity("person-1", PlaceholderKind.PERSON, 1, Span(start=0, end=3))],
        )
    with pytest.raises(ValueError, match="privacy: entity span is outside the text"):
        anonymise(
            document("ab"),
            [entity("person-1", PlaceholderKind.PERSON, 1, Span(start=-1, end=2))],
        )


def test_overlapping_spans_raise() -> None:
    with pytest.raises(ValueError, match="privacy: entity spans overlap"):
        anonymise(
            document("abcd"),
            [
                entity("person-1", PlaceholderKind.PERSON, 1, Span(start=0, end=3)),
                entity("company-1", PlaceholderKind.COMPANY, 1, Span(start=2, end=4)),
            ],
        )


def test_number_below_one_raises() -> None:
    with pytest.raises(ValueError, match="privacy: a placeholder number starts at 1"):
        anonymise(
            document("ab"),
            [entity("person-0", PlaceholderKind.PERSON, 0, Span(start=0, end=1))],
        )
