"""Tests for the core ids, enums and constants (system design 3.4)."""

import enum

import clause_tracer.core as core
from clause_tracer.core import (
    Answer,
    Direction,
    DoubtCode,
    DrawFailure,
    FileKind,
    HiddenReason,
    Level,
    PiiSource,
    PlaceholderKind,
    PlaybookProblemCode,
    PositionType,
    PrivacyMode,
    ReasonCode,
    ReviewStatus,
    ScanFinding,
    SegmentKind,
    TextSlot,
    Unit,
    WrittenBy,
)

EXPECTED_MEMBERS: dict[type[enum.StrEnum], tuple[str, ...]] = {
    Level: ("PREFERRED", "ACCEPTABLE", "WALK_AWAY", "UNSURE"),
    PositionType: ("NUMBER", "YES_NO", "WORDS"),
    Direction: ("LOWER_IS_BETTER", "HIGHER_IS_BETTER"),
    Unit: ("DAYS", "PERCENT", "MONTHS", "ROUNDS"),
    Answer: ("YES", "CONDITIONAL_YES", "NO", "UNCLEAR", "MISSING"),
    ReasonCode: (
        "QUOTE_NOT_CONFIRMED",
        "NUMBER_NOT_IN_QUOTE",
        "VAGUE_WORDING",
        "OTHER_START_POINT",
        "UNKNOWN_FIGURES",
        "BUSINESS_DAYS",
        "UNIT_UNKNOWN",
        "AMOUNT_WITHOUT_TOTAL",
        "AMOUNT_PERCENT_DISAGREE",
        "CONDITIONAL_YES",
        "RANGE",
        "CLAUSES_DISAGREE",
        "HIDDEN_TEXT",
        "UNDECODABLE_TEXT",
        "UNLOADED_DOCUMENT",
        "REPLY_BROKEN_TWICE",
        "MATCH_UNCONFIRMED",
        "NO_VALUE",
        "JUDGED_UNSURE",
        "UNLIMITED_UNCLEAR",
    ),
    WrittenBy: ("CODE", "AI", "USER"),
    ReviewStatus: ("DRAFT", "RUNNING", "INTERRUPTED", "FAILED", "READY_TO_CHECK", "DONE"),
    PrivacyMode: ("ON", "OFF"),
    FileKind: ("PDF", "WORD", "TEXT", "MARKDOWN", "PASTED"),
    PlaceholderKind: ("PERSON", "COMPANY", "ADDRESS", "EMAIL", "PHONE", "ID", "BANK"),
    SegmentKind: ("COPY", "ENTITY", "ESCAPE"),
    HiddenReason: (
        "LOW_CONTRAST",
        "TINY_FONT",
        "OFF_PAGE",
        "INVISIBLE_TEXT",
        "HIDDEN_LAYER",
        "WORD_HIDDEN_RUN",
        "COMMENT",
        "ZERO_WIDTH",
        "BIDI_CONTROL",
    ),
    PiiSource: ("PARTY_DETAILS", "PATTERN", "RULE", "NER", "USER"),
    DoubtCode: ("SHORT_NAME", "NEAR_DUPLICATE", "TWO_KINDS", "SKIPPED_COMMON", "NO_CUE_RUN"),
    TextSlot: ("REASON", "READING", "QUESTION", "MESSAGE", "REWRITE"),
    ScanFinding: (
        "TOO_LONG",
        "LAW_WORD",
        "ADVICE",
        "INJECTION_TELL",
        "CONTACT_WORD",
        "WEB_ADDRESS",
        "EMAIL_ADDRESS",
        "WRONG_LABEL_WORD",
        "ACCEPTABLE_LIMIT",
        "NUMBER_NOT_ALLOWED",
        "UNKNOWN_PLACEHOLDER",
        "PERSONAL_DATA",
        "FIRST_PERSON",
        "FILLER_PHRASE",
        "EVALUATIVE_WORD",
        "NO_ANCHOR",
        "ADDED_SENTENCE",
    ),
    DrawFailure: (
        "CLAUSE_MISMATCH",
        "SENTENCE_UNKNOWN",
        "EMPTY_QUOTE",
        "SPAN_OUTSIDE_SENTENCES",
        "QUOTE_NOT_FOUND",
        "QUOTE_NOT_UNIQUE",
        "SPAN_MISMATCH",
        "CHAR_MAP_LENGTH",
        "GLYPH_MISSING",
        "PAGE_UNKNOWN",
        "PAGE_MISMATCH",
        "BOX_OUTSIDE_PAGE",
    ),
    PlaybookProblemCode: (
        "DUPLICATE_POSITION_ID",
        "RULE_TYPE_MISMATCH",
        "LIMIT_NEGATIVE",
        "PERCENT_OVER_100",
        "LIMITS_NOT_STRICTER",
        "YES_NO_LEVEL_UNSURE",
        "YES_NOT_BETTER",
        "MISSING_LEVEL_NOT_NO_LEVEL",
        "LEVEL_TEXT_EMPTY",
    ),
}


def test_enum_members_match_system_design() -> None:
    for enum_type, names in EXPECTED_MEMBERS.items():
        assert tuple(member.name for member in enum_type) == names, (
            f"{enum_type.__name__} members differ from system design 3.4"
        )


def test_unsure_reasons() -> None:
    assert len(ReasonCode) == 20
    assert len(core.UNSURE_REASONS) == 17
    assert list(ReasonCode)[-1] is ReasonCode.UNLIMITED_UNCLEAR
    assert ReasonCode.UNLIMITED_UNCLEAR in core.UNSURE_REASONS
    assert ReasonCode.RANGE not in core.UNSURE_REASONS
    assert ReasonCode.CLAUSES_DISAGREE not in core.UNSURE_REASONS
    assert ReasonCode.AMOUNT_PERCENT_DISAGREE not in core.UNSURE_REASONS


def test_ids_are_plain_str_at_run_time() -> None:
    assert type(core.PositionId("1")) is str
    assert type(core.ClauseId("4.2")) is str


def test_placeholder_markers() -> None:
    assert core.PLACEHOLDER_OPEN == "⟦"
    assert core.PLACEHOLDER_CLOSE == "⟧"
