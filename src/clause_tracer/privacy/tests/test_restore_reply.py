"""`restore_reply`, the tokens in an AI reply (S4-M4-T4)."""

import dataclasses

import pytest

from clause_tracer.core import Document, PlaceholderEntity, PlaceholderKind, PlaceholderText, Span
from clause_tracer.privacy.placeholder import anonymise, restore_reply
from clause_tracer.privacy.tests.case_builder import make_case, span_of

TEXT = "Sarah Jones then Ms Jones at Brightline Studio Ltd."


def _entities(spans: tuple[Span, ...] | None = None) -> list[PlaceholderEntity]:
    person_spans = spans or (
        span_of(TEXT, "Sarah Jones"),
        span_of(TEXT, "Ms Jones"),
    )
    return [
        PlaceholderEntity(
            id="person-1",
            kind=PlaceholderKind.PERSON,
            number=1,
            spans=person_spans,
        ),
        PlaceholderEntity(
            id="company-1",
            kind=PlaceholderKind.COMPANY,
            number=1,
            spans=(span_of(TEXT, "Brightline Studio Ltd"),),
        ),
    ]


def _placeholder(spans: tuple[Span, ...] | None = None) -> tuple[PlaceholderText, Document]:
    document = make_case([TEXT]).document
    return anonymise(document, _entities(spans)), document


def test_a_known_placeholder_comes_back() -> None:
    placeholder, document = _placeholder()

    assert restore_reply(placeholder, document, "Ask ⟦Person 1⟧ to pay.") == (
        "Ask Sarah Jones to pay."
    )


def test_the_first_place_gives_the_variant() -> None:
    placeholder, document = _placeholder((span_of(TEXT, "Ms Jones"), span_of(TEXT, "Sarah Jones")))

    assert restore_reply(placeholder, document, "Ask ⟦Person 1⟧ to pay.") == (
        "Ask Sarah Jones to pay."
    )


def test_several_placeholders() -> None:
    placeholder, document = _placeholder()

    assert restore_reply(placeholder, document, "⟦Person 1⟧ and ⟦Company 1⟧") == (
        "Sarah Jones and Brightline Studio Ltd"
    )


def test_an_unknown_placeholder_raises() -> None:
    placeholder, document = _placeholder()

    with pytest.raises(ValueError, match="privacy: unknown placeholder"):
        restore_reply(placeholder, document, "⟦Person 9⟧")


def test_text_without_placeholders_is_unchanged() -> None:
    placeholder, document = _placeholder()

    assert restore_reply(placeholder, document, "No names [Person 1] here") == (
        "No names [Person 1] here"
    )


def test_an_odd_marker_raises() -> None:
    placeholder, document = _placeholder()

    with pytest.raises(ValueError, match="privacy: unknown placeholder"):
        restore_reply(placeholder, document, "⟦ ⟧")


def test_a_lone_open_marker_is_left() -> None:
    placeholder, document = _placeholder()

    assert restore_reply(placeholder, document, "a ⟦ b") == "a ⟦ b"


def test_a_lone_open_marker_before_a_token_is_left() -> None:
    placeholder, document = _placeholder()

    assert restore_reply(placeholder, document, "a ⟦ b ⟦Person 1⟧ c") == ("a ⟦ b Sarah Jones c")


def test_an_entity_without_a_span_raises() -> None:
    placeholder, document = _placeholder()
    entity = PlaceholderEntity(
        id="person-1",
        kind=PlaceholderKind.PERSON,
        number=1,
        spans=(),
    )

    with pytest.raises(ValueError, match="privacy: entity has no span"):
        restore_reply(dataclasses.replace(placeholder, entities=(entity,)), document, "⟦Person 1⟧")


def test_an_entity_span_outside_the_text_raises() -> None:
    placeholder, document = _placeholder()
    entity = PlaceholderEntity(
        id="person-1",
        kind=PlaceholderKind.PERSON,
        number=1,
        spans=(Span(start=0, end=len(document.text) + 1),),
    )

    with pytest.raises(ValueError, match="privacy: entity span is outside the text"):
        restore_reply(dataclasses.replace(placeholder, entities=(entity,)), document, "⟦Person 1⟧")
