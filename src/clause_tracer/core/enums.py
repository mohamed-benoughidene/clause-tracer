"""The enums and constants of the app, exactly as system design 3.4 lists them.

Every enum is a StrEnum whose member value is the member name in lower case.
Reason tuples are sorted in ReasonCode member order (I7: rules return codes,
never prose).
"""

from enum import StrEnum


class Level(StrEnum):
    """The four labels, and the missing level (Spec 2)."""

    PREFERRED = "preferred"
    ACCEPTABLE = "acceptable"
    WALK_AWAY = "walk_away"
    UNSURE = "unsure"


class PositionType(StrEnum):
    """Decides whether code or AI picks the label (Spec 5)."""

    NUMBER = "number"
    YES_NO = "yes_no"
    WORDS = "words"


class Direction(StrEnum):
    """Number positions (Spec 4.1)."""

    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class Unit(StrEnum):
    """Playbook units (Spec 4.1)."""

    DAYS = "days"
    PERCENT = "percent"
    MONTHS = "months"
    ROUNDS = "rounds"


class Answer(StrEnum):
    """Yes/no extraction (Spec 6.1 step 6b)."""

    YES = "yes"
    CONDITIONAL_YES = "conditional_yes"
    NO = "no"
    UNCLEAR = "unclear"
    MISSING = "missing"


class ReasonCode(StrEnum):
    """One code per cause in Spec 5. Templates turn codes into words (ADR 0012)."""

    QUOTE_NOT_CONFIRMED = "quote_not_confirmed"
    NUMBER_NOT_IN_QUOTE = "number_not_in_quote"
    VAGUE_WORDING = "vague_wording"
    OTHER_START_POINT = "other_start_point"
    UNKNOWN_FIGURES = "unknown_figures"
    BUSINESS_DAYS = "business_days"
    UNIT_UNKNOWN = "unit_unknown"
    AMOUNT_WITHOUT_TOTAL = "amount_without_total"
    AMOUNT_PERCENT_DISAGREE = "amount_percent_disagree"
    CONDITIONAL_YES = "conditional_yes"
    RANGE = "range"
    CLAUSES_DISAGREE = "clauses_disagree"
    HIDDEN_TEXT = "hidden_text"
    UNDECODABLE_TEXT = "undecodable_text"
    UNLOADED_DOCUMENT = "unloaded_document"
    REPLY_BROKEN_TWICE = "reply_broken_twice"
    MATCH_UNCONFIRMED = "match_unconfirmed"
    NO_VALUE = "no_value"
    JUDGED_UNSURE = "judged_unsure"
    UNLIMITED_UNCLEAR = "unlimited_unclear"


class WrittenBy(StrEnum):
    """Who wrote a stored text (ADR 0016)."""

    CODE = "code"
    AI = "ai"
    USER = "user"


class ReviewStatus(StrEnum):
    """Spec 6.3."""

    DRAFT = "draft"
    RUNNING = "running"
    INTERRUPTED = "interrupted"
    FAILED = "failed"
    READY_TO_CHECK = "ready_to_check"
    DONE = "done"


class PrivacyMode(StrEnum):
    """Neutral. The adapter maps it to the provider's settings (ADR 0015)."""

    ON = "on"
    OFF = "off"


class FileKind(StrEnum):
    """Spec 9 file types."""

    PDF = "pdf"
    WORD = "word"
    TEXT = "text"
    MARKDOWN = "markdown"
    PASTED = "pasted"


class PlaceholderKind(StrEnum):
    """Spec 4.2."""

    PERSON = "person"
    COMPANY = "company"
    ADDRESS = "address"
    EMAIL = "email"
    PHONE = "phone"
    ID = "id"
    BANK = "bank"


class SegmentKind(StrEnum):
    """The placeholder map (system design 4.2)."""

    COPY = "copy"
    ENTITY = "entity"
    ESCAPE = "escape"


class SideTextKind(StrEnum):
    """Text that sits apart from the body (system design 3.4)."""

    COMMENT = "comment"
    HEADER = "header"
    FOOTER = "footer"
    FOOTNOTE = "footnote"
    ENDNOTE = "endnote"


class HiddenReason(StrEnum):
    """Each finding names its cause. Stage 5 adds a member for any new check (D5)."""

    LOW_CONTRAST = "low_contrast"
    TINY_FONT = "tiny_font"
    OFF_PAGE = "off_page"
    INVISIBLE_TEXT = "invisible_text"
    HIDDEN_LAYER = "hidden_layer"
    WORD_HIDDEN_RUN = "word_hidden_run"
    COMMENT = "comment"
    ZERO_WIDTH = "zero_width"
    BIDI_CONTROL = "bidi_control"
    TAG_CHARACTER = "tag_character"
    WORD_PART_NEVER_SHOWN = "word_part_never_shown"


class PiiSource(StrEnum):
    """Overlaps resolve by source (ADR 0008)."""

    PARTY_DETAILS = "party_details"
    PATTERN = "pattern"
    RULE = "rule"
    NER = "ner"
    USER = "user"


class DoubtCode(StrEnum):
    """Why a finder was not sure. A doubt never changes what is replaced."""

    SHORT_NAME = "short_name"
    NEAR_DUPLICATE = "near_duplicate"
    TWO_KINDS = "two_kinds"
    SKIPPED_COMMON = "skipped_common"
    NO_CUE_RUN = "no_cue_run"


class TextSlot(StrEnum):
    """The kinds of text the AI may write; each has its own length cap (Spec 6.2)."""

    REASON = "reason"
    READING = "reading"
    QUESTION = "question"
    MESSAGE = "message"
    REWRITE = "rewrite"


class ScanFinding(StrEnum):
    """What an output scan found. An empty tuple means the text passed."""

    TOO_LONG = "too_long"
    LAW_WORD = "law_word"
    ADVICE = "advice"
    INJECTION_TELL = "injection_tell"
    CONTACT_WORD = "contact_word"
    WEB_ADDRESS = "web_address"
    EMAIL_ADDRESS = "email_address"
    WRONG_LABEL_WORD = "wrong_label_word"
    ACCEPTABLE_LIMIT = "acceptable_limit"
    NUMBER_NOT_ALLOWED = "number_not_allowed"
    UNKNOWN_PLACEHOLDER = "unknown_placeholder"
    PERSONAL_DATA = "personal_data"
    FIRST_PERSON = "first_person"
    FILLER_PHRASE = "filler_phrase"
    EVALUATIVE_WORD = "evaluative_word"
    NO_ANCHOR = "no_anchor"
    ADDED_SENTENCE = "added_sentence"


class DrawFailure(StrEnum):
    """Why the last check before drawing refused (system design 4.2)."""

    CLAUSE_MISMATCH = "clause_mismatch"
    SENTENCE_UNKNOWN = "sentence_unknown"
    EMPTY_QUOTE = "empty_quote"
    SPAN_OUTSIDE_SENTENCES = "span_outside_sentences"
    QUOTE_NOT_FOUND = "quote_not_found"
    QUOTE_NOT_UNIQUE = "quote_not_unique"
    SPAN_MISMATCH = "span_mismatch"
    CHAR_MAP_LENGTH = "char_map_length"
    GLYPH_MISSING = "glyph_missing"
    PAGE_UNKNOWN = "page_unknown"
    PAGE_MISMATCH = "page_mismatch"
    BOX_OUTSIDE_PAGE = "box_outside_page"


class PlaybookProblemCode(StrEnum):
    """The playbook checks of Spec 4.1."""

    DUPLICATE_POSITION_ID = "duplicate_position_id"
    RULE_TYPE_MISMATCH = "rule_type_mismatch"
    LIMIT_NEGATIVE = "limit_negative"
    PERCENT_OVER_100 = "percent_over_100"
    LIMITS_NOT_STRICTER = "limits_not_stricter"
    YES_NO_LEVEL_UNSURE = "yes_no_level_unsure"
    YES_NOT_BETTER = "yes_not_better"
    MISSING_LEVEL_NOT_NO_LEVEL = "missing_level_not_no_level"
    LEVEL_TEXT_EMPTY = "level_text_empty"


UNSURE_REASONS: frozenset[ReasonCode] = frozenset(ReasonCode) - {
    ReasonCode.RANGE,
    ReasonCode.CLAUSES_DISAGREE,
    ReasonCode.AMOUNT_PERCENT_DISAGREE,
}

PLACEHOLDER_OPEN = "⟦"
PLACEHOLDER_CLOSE = "⟧"
