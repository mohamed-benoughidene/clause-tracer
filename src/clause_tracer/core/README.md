# core

## Purpose
Pure rules: playbook and review models and label picking, with no files, network, clock or AI.

## Spec
`docs/spec.md` section 5, and section 6.1 step 8 (pick labels).

## Ids and enums
Imported from `clause_tracer.core`, never from a file inside the package (B2).

**Ids.** Each is `NewType` over `str`, made at the edge, opaque to `core` (system design 3.4):
`ReviewId`, `PlaybookId`, `CustomerId`, `PositionId`, `ClauseId`, `SentenceId`, `RecordId`.

**Enums.** Each is a `StrEnum`; every member's value is its member name in lower case
(for example `Level.WALK_AWAY == "walk_away"`). Members, in order:

| Enum | Members |
| --- | --- |
| `Level` | `PREFERRED`, `ACCEPTABLE`, `WALK_AWAY`, `UNSURE` |
| `PositionType` | `NUMBER`, `YES_NO`, `WORDS` |
| `Direction` | `LOWER_IS_BETTER`, `HIGHER_IS_BETTER` |
| `Unit` | `DAYS`, `PERCENT`, `MONTHS`, `ROUNDS` |
| `Answer` | `YES`, `CONDITIONAL_YES`, `NO`, `UNCLEAR`, `MISSING` |
| `ReasonCode` | `QUOTE_NOT_CONFIRMED`, `NUMBER_NOT_IN_QUOTE`, `VAGUE_WORDING`, `OTHER_START_POINT`, `UNKNOWN_FIGURES`, `BUSINESS_DAYS`, `UNIT_UNKNOWN`, `AMOUNT_WITHOUT_TOTAL`, `AMOUNT_PERCENT_DISAGREE`, `CONDITIONAL_YES`, `RANGE`, `CLAUSES_DISAGREE`, `HIDDEN_TEXT`, `UNDECODABLE_TEXT`, `UNLOADED_DOCUMENT`, `REPLY_BROKEN_TWICE`, `MATCH_UNCONFIRMED`, `NO_VALUE`, `JUDGED_UNSURE`, `UNLIMITED_UNCLEAR` |
| `WrittenBy` | `CODE`, `AI`, `USER` |
| `ReviewStatus` | `DRAFT`, `RUNNING`, `INTERRUPTED`, `FAILED`, `READY_TO_CHECK`, `DONE` |
| `PrivacyMode` | `ON`, `OFF` |
| `FileKind` | `PDF`, `WORD`, `TEXT`, `MARKDOWN`, `PASTED` |
| `PlaceholderKind` | `PERSON`, `COMPANY`, `ADDRESS`, `EMAIL`, `PHONE`, `ID`, `BANK` |
| `SegmentKind` | `COPY`, `ENTITY`, `ESCAPE` |
| `HiddenReason` | `LOW_CONTRAST`, `TINY_FONT`, `OFF_PAGE`, `INVISIBLE_TEXT`, `HIDDEN_LAYER`, `WORD_HIDDEN_RUN`, `COMMENT`, `ZERO_WIDTH`, `BIDI_CONTROL` |
| `PiiSource` | `PARTY_DETAILS`, `PATTERN`, `RULE`, `NER`, `USER` |
| `TextSlot` | `REASON`, `READING`, `QUESTION`, `MESSAGE`, `REWRITE` |
| `ScanFinding` | `TOO_LONG`, `LAW_WORD`, `ADVICE`, `INJECTION_TELL`, `CONTACT_WORD`, `WEB_ADDRESS`, `EMAIL_ADDRESS`, `WRONG_LABEL_WORD`, `ACCEPTABLE_LIMIT`, `NUMBER_NOT_ALLOWED`, `UNKNOWN_PLACEHOLDER`, `PERSONAL_DATA`, `FIRST_PERSON`, `FILLER_PHRASE`, `EVALUATIVE_WORD`, `NO_ANCHOR`, `ADDED_SENTENCE` |
| `DrawFailure` | `CLAUSE_MISMATCH`, `SENTENCE_UNKNOWN`, `EMPTY_QUOTE`, `SPAN_OUTSIDE_SENTENCES`, `QUOTE_NOT_FOUND`, `QUOTE_NOT_UNIQUE`, `SPAN_MISMATCH`, `CHAR_MAP_LENGTH`, `GLYPH_MISSING`, `PAGE_UNKNOWN`, `PAGE_MISMATCH`, `BOX_OUTSIDE_PAGE` |
| `PlaybookProblemCode` | `DUPLICATE_POSITION_ID`, `RULE_TYPE_MISMATCH`, `LIMIT_NEGATIVE`, `PERCENT_OVER_100`, `LIMITS_NOT_STRICTER`, `YES_NO_LEVEL_UNSURE`, `YES_NOT_BETTER`, `MISSING_LEVEL_NOT_NO_LEVEL`, `LEVEL_TEXT_EMPTY` |

**Constants.**

- `UNSURE_REASONS`: a `frozenset[ReasonCode]`, every code except `RANGE`, `CLAUSES_DISAGREE` and `AMOUNT_PERCENT_DISAGREE` (17 codes). A value that carries one of these is unsure; the three left out are notes shown beside a label.
- `PLACEHOLDER_OPEN` = `"⟦"`, `PLACEHOLDER_CLOSE` = `"⟧"`: the placeholder marker of Spec 4.2.

## Errors
Every error the project raises on purpose subclasses `ClauseTracerError` (I6). Its constructor
takes `context: Mapping[str, str | int] | None = None`, kept as a read-only `MappingProxyType`
in `.context`; the message is the code; context holds ids, step names and counts only.

| Class | Group | Code |
| --- | --- | --- |
| `ClauseTracerError` | — (base) | `""` |
| `InputError` | base | `""` |
| `ModelServiceError` | base | `""` |
| `LocalError` | base | `""` |
| `ReviewCancelled` | base (and leaf) | `review_cancelled` |
| `UnreadableFileError` | Input | `unreadable_file` |
| `ScannedPdfError` | Input | `scanned_pdf` |
| `OldWordFileError` | Input | `old_word_file` |
| `InputTooLargeError` | Input | `input_too_large` |
| `NotUtf8Error` | Input | `not_utf8` |
| `EncryptedPdfError` | Input | `encrypted_pdf` |
| `PlaybookFormatError` | Input | `playbook_format` |
| `NetworkUnavailableError` | Model service | `network_unavailable` |
| `InvalidApiKeyError` | Model service | `invalid_api_key` |
| `NoCreditError` | Model service | `no_credit` |
| `RateLimitedError` | Model service | `rate_limited` |
| `NoPrivateModelError` | Model service | `no_private_model` |
| `ModelTimeoutError` | Model service | `model_timeout` |
| `ModelReplyInvalidError` | Model service | `model_reply_invalid` |
| `SecretStoreUnavailableError` | Local | `secret_store_unavailable` |
| `StorageCorruptError` | Local | `storage_corrupt` |
| `SchemaTooNewError` | Local | `schema_too_new` |
| `ConfigError` | Local | `config` |
| `DuplicateRecordError` | Local | `duplicate_record` |

`RateLimitedError` is the one leaf with an extra keyword argument,
`retry_after_seconds: int | None = None`: the wait the AI service asked for. It is kept as
`.retry_after_seconds` and, when given, in `context["retry_after_seconds"]`; a negative value
raises `ValueError`.

## Shapes
Every shape is `@dataclass(frozen=True, slots=True, kw_only=True)`, built with keyword
arguments, with exactly the fields of system design 3.4 in that order (ADR 0005).

| Shape | Fields | Why |
| --- | --- | --- |
| `Wording` | `text: str, written_by: WrittenBy` | Every stored label reason, Missing text, question, message, rewrite and note (ADR 0016) |
| `Span` | `start: int, end: int` | A place in the canonical text; half-open, counts code points (section 4.2) |
| `PageBox` | `page: int, x0: float, top: float, x1: float, bottom: float` | PDF points, top-left origin, one coordinate system (ADR 0007) |
| `Page` | `number: int, width: float, height: float` | Pages are numbered from 1 |
| `Glyph` | `page: int, box: PageBox` | One drawn character; `page` is a `Page.number` and equals `box.page` |
| `SourceFile` | `name: str, kind: FileKind, sha256: str, size: int` | Points at the raw bytes, which the store keeps unchanged (D1) |
| `HiddenText` | `span: Span \| None, reason: HiddenReason, boxes: tuple[PageBox, ...]` | Flagged, never removed (D1); no span when the text is not in the canonical text |
| `TrackedChange` | `earlier: str, new: str, author: str, span: Span \| None` | Listed at the contract check; the accepted view is the contract (ADR 0012) |
| `InputWarning` | `code: str, page: int \| None` | Undecodable pages, scanned pages in a mixed file, not English (Spec 9) |
| `Document` | `schema_version: int, source: SourceFile, text: str, char_map: tuple[int \| None, ...], glyphs: tuple[Glyph, ...], pages: tuple[Page, ...], furniture: tuple[Span, ...], hidden: tuple[HiddenText, ...], undecodable: tuple[Span, ...], tracked_changes: tuple[TrackedChange, ...], warnings: tuple[InputWarning, ...]` | The one canonical text (section 4.2). A document without glyphs has `glyphs == ()`, `char_map == ()` and `pages == ()` |
| `MatchKey` | `text: str, to_canonical: tuple[int, ...]` | Folded copy with its index map (section 4.2) |
| `Sentence` | `id: SentenceId, span: Span` | Stable ids such as `4.2.s3`, which the AI points at |
| `Clause` | `id: ClauseId, number: str \| None, heading: str \| None, level: int, parent_id: ClauseId \| None, span: Span, numbering_source: str, sentences: tuple[Sentence, ...]` | One clause, or one paragraph when the contract has no numbers (Spec 6.1 step 2) |
| `CrossReference` | `source: Span, target: ClauseId \| None` | An unresolved target is kept, with no target |
| `DefinedTerm` | `term: str, definition: Span, uses: tuple[Span, ...]` | Evidence trail, and the privacy allow-list (section 4.1) |
| `Override` | `clause_id: ClauseId, target: ClauseId \| None, overrides_target: bool, evidence: Span` | Direction matters; no target means it joins every trail (Spec 4.5) |
| `OutsideDocument` | `name: str, evidence: Span` | A document not loaded that the label's evidence reaches (Rule 10) |
| `LinkMap` | `references: tuple[CrossReference, ...], terms: tuple[DefinedTerm, ...], overrides: tuple[Override, ...], outside_documents: tuple[OutsideDocument, ...], undefined_terms: tuple[Span, ...]` | What `links` returns; `cli` passes `terms` into `privacy` |
| `Party` | `name: str, address: str \| None, yours: bool` | Typed party details: raw data, and the first privacy finder |
| `PiiSuggestion` | `span: Span, kind: PlaceholderKind, source: PiiSource` | What the `PiiDetector` port and the code finders return (ADR 0008) |
| `PlaceholderEntity` | `id: str, kind: PlaceholderKind, number: int, spans: tuple[Span, ...]` | One placeholder, such as Person 1, for every variant of one name |
| `Segment` | `kind: SegmentKind, sent: Span, original: Span, entity_id: str \| None` | Tiles both texts, so a quote maps back exactly |
| `PlaceholderText` | `text: str, entities: tuple[PlaceholderEntity, ...], segments: tuple[Segment, ...]` | The only contract text that leaves the computer |
| `CancelCheck` | a type alias: `Callable[[], bool]` | Returns True once the user has cancelled (ADR 0005) |

## Depends on
Nothing. It imports no other clause_tracer module.

## Run alone
`.venv/bin/uv run python -m clause_tracer.core`
