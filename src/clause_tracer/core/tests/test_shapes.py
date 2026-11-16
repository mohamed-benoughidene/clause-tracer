"""Every shape matches system design 3.4: names, fields, order (S3)."""

import dataclasses

import pytest

from clause_tracer.core import (
    Clause,
    ClauseId,
    CrossReference,
    DefinedTerm,
    Document,
    FileKind,
    Glyph,
    HiddenText,
    InputWarning,
    LinkMap,
    MatchKey,
    OutsideDocument,
    Override,
    Page,
    PageBox,
    Party,
    PiiSuggestion,
    PlaceholderEntity,
    PlaceholderText,
    Segment,
    Sentence,
    SourceFile,
    Span,
    TrackedChange,
    Wording,
)

EXPECTED_FIELDS: dict[type, tuple[str, ...]] = {
    Wording: ("text", "written_by"),
    Span: ("start", "end"),
    PageBox: ("page", "x0", "top", "x1", "bottom"),
    Page: ("number", "width", "height"),
    Glyph: ("page", "box"),
    SourceFile: ("name", "kind", "sha256", "size"),
    HiddenText: ("span", "reason", "boxes"),
    TrackedChange: ("earlier", "new", "author", "span"),
    InputWarning: ("code", "page"),
    Document: (
        "schema_version",
        "source",
        "text",
        "char_map",
        "glyphs",
        "pages",
        "furniture",
        "hidden",
        "undecodable",
        "tracked_changes",
        "warnings",
    ),
    MatchKey: ("text", "to_canonical"),
    Sentence: ("id", "span"),
    Clause: (
        "id",
        "number",
        "heading",
        "level",
        "parent_id",
        "span",
        "numbering_source",
        "sentences",
    ),
    CrossReference: ("source", "target"),
    DefinedTerm: ("term", "definition", "uses"),
    Override: ("clause_id", "target", "overrides_target", "evidence"),
    OutsideDocument: ("name", "evidence"),
    LinkMap: (
        "references",
        "terms",
        "overrides",
        "outside_documents",
        "undefined_terms",
    ),
    Party: ("name", "address", "yours"),
    PiiSuggestion: ("span", "kind", "source"),
    PlaceholderEntity: ("id", "kind", "number", "spans"),
    Segment: ("kind", "sent", "original", "entity_id"),
    PlaceholderText: ("text", "entities", "segments"),
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


def test_document_without_glyphs() -> None:
    # A document without glyphs has empty glyphs, char_map and pages
    # (decided 14 Nov 2026, system design 3.4).
    document = Document(
        schema_version=1,
        source=SourceFile(name="contract.pdf", kind=FileKind.PDF, sha256="ab", size=3),
        text="Pay in 30 days.",
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )
    assert document.glyphs == ()
    assert document.char_map == ()
    assert document.pages == ()


def test_span_counts_code_points() -> None:
    # Offsets count code points (section 4.2): the emoji is one code point.
    text = "\U0001f600 fee"
    span = Span(start=2, end=5)
    assert text[span.start : span.end] == "fee"


def test_unresolved_targets_are_kept() -> None:
    # An unresolved target is kept, with no target (system design 3.4).
    reference = CrossReference(source=Span(start=0, end=4), target=None)
    assert reference.target is None
    override = Override(
        clause_id=ClauseId("4"),
        target=None,
        overrides_target=True,
        evidence=Span(start=0, end=4),
    )
    assert override.target is None
