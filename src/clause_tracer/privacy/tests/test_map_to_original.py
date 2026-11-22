"""`map_to_original`, a span in the sent text back to the contract (S4-M4-T5)."""

import pytest

from clause_tracer.core import PlaceholderEntity, PlaceholderKind, PlaceholderText, Span
from clause_tracer.privacy.placeholder import anonymise, map_to_original
from clause_tracer.privacy.tests.case_builder import make_case, span_of

TEXT = "Hi Sam, hi Sam."


def _placeholder() -> PlaceholderText:
    document = make_case([TEXT]).document
    entity = PlaceholderEntity(
        id="person-1",
        kind=PlaceholderKind.PERSON,
        number=1,
        spans=(span_of(TEXT, "Sam", 1), span_of(TEXT, "Sam", 2)),
    )
    return anonymise(document, [entity])


def test_a_copy_span_maps_by_a_shift() -> None:
    assert map_to_original(_placeholder(), Span(start=15, end=17)) == Span(start=8, end=10)


def test_a_start_inside_a_placeholder_snaps_out() -> None:
    assert map_to_original(_placeholder(), Span(start=5, end=15)) == Span(start=3, end=8)


def test_an_end_inside_a_placeholder_snaps_out() -> None:
    assert map_to_original(_placeholder(), Span(start=0, end=5)) == Span(start=0, end=6)


def test_a_span_over_a_placeholder_and_a_copy() -> None:
    assert map_to_original(_placeholder(), Span(start=2, end=14)) == Span(start=2, end=7)


def test_the_last_placeholder_to_the_end() -> None:
    assert map_to_original(_placeholder(), Span(start=18, end=29)) == Span(start=11, end=15)


def test_a_span_in_an_escape() -> None:
    document = make_case(["a ⟦b⟧ c"]).document

    assert map_to_original(anonymise(document, []), Span(start=2, end=3)) == Span(start=2, end=3)


def test_an_empty_span_raises() -> None:
    with pytest.raises(ValueError, match="privacy: an empty span has no place"):
        map_to_original(_placeholder(), Span(start=4, end=4))


def test_a_span_outside_the_text_raises() -> None:
    with pytest.raises(ValueError, match="privacy: span is outside the placeholder text"):
        map_to_original(_placeholder(), Span(start=0, end=30))
    with pytest.raises(ValueError, match="privacy: span is outside the placeholder text"):
        map_to_original(_placeholder(), Span(start=-1, end=2))
