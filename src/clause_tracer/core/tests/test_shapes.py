"""Every shape matches system design 3.4: names, fields, order (S3)."""

import dataclasses

import pytest

from clause_tracer.core import Glyph, Page, PageBox, Span, Wording

EXPECTED_FIELDS: dict[type, tuple[str, ...]] = {
    Wording: ("text", "written_by"),
    Span: ("start", "end"),
    PageBox: ("page", "x0", "top", "x1", "bottom"),
    Page: ("number", "width", "height"),
    Glyph: ("page", "box"),
}


def _by_name(item: tuple[type, tuple[str, ...]]) -> str:
    return item[0].__name__


_ORDERED_SHAPES: list[tuple[type, tuple[str, ...]]] = sorted(EXPECTED_FIELDS.items(), key=_by_name)


@pytest.mark.parametrize(("shape", "expected"), _ORDERED_SHAPES)
def test_fields_match_system_design(shape: type, expected: tuple[str, ...]) -> None:
    assert tuple(f.name for f in dataclasses.fields(shape)) == expected


def test_wording_needs_written_by() -> None:
    # Promise test: every stored text keeps a written-by value (Spec 4.7, 6.2).
    with pytest.raises(TypeError):
        Wording(text="x")  # type: ignore[call-arg]
    fields = {f.name: f for f in dataclasses.fields(Wording)}
    assert "written_by" in fields
    assert fields["written_by"].default is dataclasses.MISSING
    assert fields["written_by"].default_factory is dataclasses.MISSING


def test_shapes_need_keywords() -> None:
    with pytest.raises(TypeError):
        Span(1, 2)  # type: ignore[call-arg]
