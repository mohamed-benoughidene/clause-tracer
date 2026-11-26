"""Every shape matches system design 3.4: names, fields, order (S3)."""

import dataclasses
from typing import get_type_hints

import pytest

from clause_tracer.core import (
    AiRecord,
    AiReply,
    AiRequest,
    CallFailed,
    CallPrices,
    CheckedValue,
    Clause,
    ClauseId,
    CostInputs,
    CostRange,
    CrossReference,
    DefinedTerm,
    Document,
    Doubt,
    DoubtCode,
    DrawAllowed,
    DrawRefused,
    Evidence,
    FileKind,
    Glyph,
    HiddenText,
    InputWarning,
    JudgedLevel,
    LabelInput,
    LinkMap,
    MatchFound,
    MatchKey,
    MatchUnconfirmed,
    NotCoveredClause,
    NothingFound,
    NumberRule,
    OutsideDocument,
    Override,
    Page,
    PageBox,
    Party,
    PiiSuggestion,
    PlaceholderEntity,
    PlaceholderText,
    Playbook,
    PlaybookProblem,
    PlaybookSnapshot,
    Position,
    PromptMessage,
    QuoteFold,
    ReasonCode,
    ScanContext,
    Segment,
    Sentence,
    Settings,
    SideText,
    SideTextKind,
    SourceFile,
    Span,
    StepInputs,
    ToolLabel,
    TrackedChange,
    UnreadableSpans,
    Usage,
    ValueVerdict,
    Wording,
    WordsRule,
    YesNoRule,
)
from clause_tracer.core.tests.shapes_for_tests import make_request

EXPECTED_FIELDS: dict[type, tuple[str, ...]] = {
    Wording: ("text", "written_by"),
    Span: ("start", "end"),
    Evidence: ("clause_id", "sentence_ids", "quote", "placed"),
    CheckedValue: (
        "position_id",
        "clause_id",
        "evidence",
        "raw_value",
        "number",
        "range_high",
        "unit_as_written",
        "start_point_as_written",
        "answer",
        "condition",
        "vague",
        "amount",
        "total",
        "reasons",
        "unlimited",
    ),
    JudgedLevel: ("position_id", "clause_id", "evidence", "level"),
    MatchFound: ("position_id", "clause_ids"),
    NothingFound: ("position_id", "searches"),
    MatchUnconfirmed: ("position_id", "clauses_to_read"),
    CallFailed: ("code",),
    ToolLabel: ("position_id", "level", "reasons", "evidence", "written_by"),
    NotCoveredClause: ("clause_id", "clause_type"),
    StepInputs: (),
    PromptMessage: ("role", "text"),
    AiRequest: (
        "step",
        "prompt_id",
        "prompt_version",
        "inputs",
        "messages",
        "schema_id",
        "json_schema",
        "model",
        "privacy_mode",
        "max_tokens",
    ),
    Usage: ("input_tokens", "cached_input_tokens", "output_tokens", "cost_usd"),
    AiReply: (
        "raw_body",
        "text",
        "model_used",
        "provider_used",
        "usage",
        "generation_id",
    ),
    AiRecord: (
        "record_id",
        "schema_version",
        "review_id",
        "step",
        "attempt",
        "request_sha256",
        "request",
        "reply",
        "error_code",
        "started_at",
        "finished_at",
    ),
    UnreadableSpans: ("hidden", "undecodable"),
    LabelInput: (
        "position",
        "match",
        "values",
        "judged",
        "outside_documents",
    ),
    ValueVerdict: ("clause_id", "level", "reasons", "evidence", "readable_value"),
    ScanContext: (
        "label",
        "allowed_numbers",
        "acceptable_limits",
        "known_placeholders",
        "defined_roles",
        "clause_numbers",
        "quote",
        "source_text",
        "instruction_given",
    ),
    QuoteFold: ("text", "to_original"),
    DrawAllowed: ("evidence",),
    DrawRefused: ("failure",),
    CallPrices: (
        "input_per_million",
        "cached_input_per_million",
        "output_per_million",
    ),
    CostInputs: (
        "positions",
        "words_positions",
        "clauses",
        "contract_tokens",
        "prices",
    ),
    CostRange: ("calls", "low_usd", "high_usd"),
    PlaybookProblem: ("position_id", "code"),
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
        "side_text",
    ),
    SideText: ("kind", "ref", "author", "text", "span"),
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
    Doubt: ("span", "code"),
    PlaceholderEntity: ("id", "kind", "number", "spans"),
    Segment: ("kind", "sent", "original", "entity_id"),
    PlaceholderText: ("text", "entities", "segments"),
    NumberRule: ("unit", "direction", "preferred_limit", "acceptable_limit"),
    YesNoRule: ("question", "yes_level", "no_level"),
    WordsRule: ("preferred", "acceptable", "walk_away"),
    Position: ("id", "topic", "type", "rule", "missing_level", "why_note"),
    Playbook: (
        "id",
        "schema_version",
        "name",
        "side",
        "customer_id",
        "positions",
        "starter",
    ),
    PlaybookSnapshot: ("playbook", "taken_at", "unedited_starter"),
    Settings: (
        "default_model",
        "step_models",
        "private_mode_default",
        "send_why_notes",
        "auto_delete_days",
        "data_dir",
        "log_level",
    ),
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


def test_playbook_text_is_plain_str() -> None:
    # Playbook text carries no written-by value (decided 13 Nov 2026,
    # ADR 0005 amendment): the hints are str, not Wording.
    hints = get_type_hints(Playbook)
    assert hints["name"] is str
    assert get_type_hints(Position)["topic"] is str
    assert get_type_hints(YesNoRule)["question"] is str
    words_hints = get_type_hints(WordsRule)
    assert words_hints["preferred"] is str
    assert words_hints["acceptable"] is str
    assert words_hints["walk_away"] is str


def test_match_results_are_unrelated() -> None:
    # Four separate types, so a failed call can never pass as "nothing
    # found" (I4, system design 3.4).
    match_types = (MatchFound, NothingFound, MatchUnconfirmed, CallFailed)
    for a in match_types:
        for b in match_types:
            if a is not b:
                assert not issubclass(a, b), f"{a.__name__} subclasses {b.__name__}"


def test_unlimited_defaults_to_false() -> None:
    # "Unlimited" is CheckedValue.unlimited (decided 14 Nov 2026).
    fields = {f.name: f for f in dataclasses.fields(CheckedValue)}
    assert fields["unlimited"].default is False


def test_reason_fields_hold_reason_codes() -> None:
    # Rules return codes, never prose (I7).
    assert get_type_hints(CheckedValue)["reasons"] == tuple[ReasonCode, ...]
    assert get_type_hints(ToolLabel)["reasons"] == tuple[ReasonCode, ...]


def test_json_schema_is_read_only() -> None:
    # The top level of json_schema cannot be changed (system design 3.4, 6.3).
    with pytest.raises(TypeError):
        make_request().json_schema["type"] = "array"  # type: ignore[index]


def test_json_schema_is_copied() -> None:
    # A dict passed in and then changed leaves the request's json_schema unchanged.
    schema: dict[str, object] = {"type": "object"}
    request = make_request(json_schema=schema)
    schema["type"] = "array"
    assert request.json_schema["type"] == "object"


def test_record_has_schema_version() -> None:
    # AiRecord carries its own schema_version (decided 14 Nov 2026).
    assert dataclasses.fields(AiRecord)[1].name == "schema_version"


def test_draw_results_are_unrelated() -> None:
    # Two types, so a refusal cannot pass as an approval (I4).
    assert not issubclass(DrawAllowed, DrawRefused)
    assert not issubclass(DrawRefused, DrawAllowed)


def test_doubt_needs_keywords() -> None:
    with pytest.raises(TypeError):
        Doubt(Span(start=0, end=1), DoubtCode.SHORT_NAME)  # type: ignore[call-arg]


def test_doubt_holds_a_span_and_a_code() -> None:
    doubt = Doubt(span=Span(start=0, end=4), code=DoubtCode.NO_CUE_RUN)
    assert doubt.span.end == 4
    assert doubt.code is DoubtCode.NO_CUE_RUN


def _text_document(*, side_text: tuple[SideText, ...] = ()) -> Document:
    return Document(
        schema_version=1,
        source=SourceFile(name="contract.txt", kind=FileKind.TEXT, sha256="ab", size=3),
        text="Pay in 30 days.",
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
        side_text=side_text,
    )


def test_side_text_default_is_empty() -> None:
    assert _text_document().side_text == ()


def test_side_text_is_frozen() -> None:
    side_text = SideText(kind=SideTextKind.COMMENT, ref="0", author="A", text="x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        side_text.text = "y"  # type: ignore[misc]


def test_document_with_side_text() -> None:
    side_text = SideText(kind=SideTextKind.COMMENT, ref="0", author="A", text="x")
    document = _text_document(side_text=(side_text,))
    assert document.side_text == (side_text,)
