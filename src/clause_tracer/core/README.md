# core

## Purpose
Pure rules and shapes: every shape, port, error and fake; label picking, playbook checks, output scans, the last check before drawing, auto-delete dates and the cost estimate. No files, network, clock or AI: only `__main__` reads a file (Constitution S1, S2).

## Spec
`docs/spec.md` sections 4.1 (playbook checks), 5 (labelling rules), 6.1 step 8 (pick labels), 6.2 (rules for every AI step) and 9 (cost and auto-delete).

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
| `SideTextKind` | `COMMENT`, `HEADER`, `FOOTER`, `FOOTNOTE`, `ENDNOTE` |
| `HiddenReason` | `LOW_CONTRAST`, `TINY_FONT`, `OFF_PAGE`, `INVISIBLE_TEXT`, `HIDDEN_LAYER`, `WORD_HIDDEN_RUN`, `COMMENT`, `ZERO_WIDTH`, `BIDI_CONTROL`, `TAG_CHARACTER`, `WORD_PART_NEVER_SHOWN` |
| `PiiSource` | `PARTY_DETAILS`, `PATTERN`, `RULE`, `NER`, `USER` |
| `DoubtCode` | `SHORT_NAME`, `NEAR_DUPLICATE`, `TWO_KINDS`, `SKIPPED_COMMON`, `NO_CUE_RUN` |
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
| `EmptyInputError` | Input | `empty_input` |
| `NotTextError` | Input | `not_text` |
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
| `SideText` | `kind: SideTextKind, ref: str, author: str, text: str, span: Span \| None` | Text that Word shows apart from the body (a comment, a header or footer, a footnote or endnote). Never in `Document.text`, so the splitter, `links` and `privacy` never read it. `ref` is the comment id, the note id, or the name of the header or footer part. `span` is the commented words for a `COMMENT`, and `None` for every other kind and for a comment with no range |
| `Document` | `schema_version: int, source: SourceFile, text: str, char_map: tuple[int \| None, ...], glyphs: tuple[Glyph, ...], pages: tuple[Page, ...], furniture: tuple[Span, ...], hidden: tuple[HiddenText, ...], undecodable: tuple[Span, ...], tracked_changes: tuple[TrackedChange, ...], warnings: tuple[InputWarning, ...], side_text: tuple[SideText, ...]` | The one canonical text (section 4.2). A document without glyphs has `glyphs == ()`, `char_map == ()` and `pages == ()`. A document without side text has `side_text == ()` |
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
| `Doubt` | `span: Span, code: DoubtCode` | A place where a finder could not be sure. It never changes what is replaced |
| `PlaceholderEntity` | `id: str, kind: PlaceholderKind, number: int, spans: tuple[Span, ...]` | One placeholder, such as Person 1, for every variant of one name |
| `Segment` | `kind: SegmentKind, sent: Span, original: Span, entity_id: str \| None` | Tiles both texts, so a quote maps back exactly |
| `PlaceholderText` | `text: str, entities: tuple[PlaceholderEntity, ...], segments: tuple[Segment, ...]` | The only contract text that leaves the computer |
| `NumberRule` | `unit: Unit, direction: Direction, preferred_limit: Decimal, acceptable_limit: Decimal` | Rule 1 |
| `YesNoRule` | `question: str, yes_level: Level, no_level: Level` | Rule 2; the missing level is always the "no" level |
| `WordsRule` | `preferred: str, acceptable: str, walk_away: str` | One sentence per level |
| `Position` | `id: PositionId, topic: str, type: PositionType, rule: NumberRule \| YesNoRule \| WordsRule, missing_level: Level, why_note: str \| None` | One playbook rule (Spec 4.1) |
| `Playbook` | `id: PlaybookId, schema_version: int, name: str, side: str, customer_id: CustomerId \| None, positions: tuple[Position, ...], starter: bool` | Starters are read-only |
| `PlaybookSnapshot` | `playbook: Playbook, taken_at: datetime, unedited_starter: bool` | Taken at "Send for review"; drives "by the example playbook" |
| `Settings` | `default_model: str, step_models: tuple[tuple[str, str], ...], private_mode_default: bool, send_why_notes: bool, auto_delete_days: int, data_dir: str, log_level: str` | Loaded once at start-up and passed in (I13, Spec 14.3) |
| `Evidence` | `clause_id: ClauseId, sentence_ids: tuple[SentenceId, ...], quote: Span, placed: bool` | A confirmed quote; `placed` is false when it could not be marked on the page; the label stays (ADR 0012) |
| `CheckedValue` | `position_id: PositionId, clause_id: ClauseId, evidence: Evidence \| None, raw_value: str \| None, number: Decimal \| None, range_high: Decimal \| None, unit_as_written: str \| None, start_point_as_written: str \| None, answer: Answer \| None, condition: Span \| None, vague: bool, amount: Decimal \| None, total: Decimal \| None, reasons: tuple[ReasonCode, ...], unlimited: bool = False` | One value after the quote check; the input of the number and yes/no label rules (Spec 6.1 step 6b). "None" arrives as `number == 0`; `unlimited` is true when the contract says the value has no limit |
| `JudgedLevel` | `position_id: PositionId, clause_id: ClauseId, evidence: Evidence \| None, level: Level` | One AI judgement for a words position (step 9) |
| `MatchFound` | `position_id: PositionId, clause_ids: tuple[ClauseId, ...]` | The position was found in the clauses named |
| `NothingFound` | `position_id: PositionId, searches: tuple[str, ...]` | Fills the "Where it was searched" panel |
| `MatchUnconfirmed` | `position_id: PositionId, clauses_to_read: tuple[ClauseId, ...]` | The searches disagree: unsure with `MATCH_UNCONFIRMED` (ADR 0012) |
| `CallFailed` | `code: str` | The call failed; a separate type, so it can never pass as "nothing found" (I4) |
| `MatchResult` | a type alias: the union of the four match types | The `match` field of `LabelInput` |
| `ToolLabel` | `position_id: PositionId, level: Level, reasons: tuple[ReasonCode, ...], evidence: tuple[Evidence, ...], written_by: WrittenBy` | The label code picked; `written_by` is AI only for words positions, which are drawn in pencil (ADR 0002) |
| `NotCoveredClause` | `clause_id: ClauseId, clause_type: str` | A type from the closed list, plus the clause's own first line (ADR 0011) |
| `StepInputs` | no fields | The base class of every step's own input shape; each step defines a frozen, slotted, keyword-only subclass (decided 14 Nov 2026) |
| `PromptMessage` | `role: str, text: str` | One rendered prompt part |
| `AiRequest` | `step: str, prompt_id: str, prompt_version: int, inputs: StepInputs, messages: tuple[PromptMessage, ...], schema_id: str, json_schema: Mapping[str, object], model: str, privacy_mode: PrivacyMode, max_tokens: int` | The accepted form of one AI call (section 6.3, ADR 0015). `__post_init__` replaces `json_schema` with a `MappingProxyType` copy, so the top level cannot be changed |
| `Usage` | `input_tokens: int, cached_input_tokens: int, output_tokens: int, cost_usd: Decimal \| None` | Cached tokens are read on every call (ADR 0010); one neutral cost amount, or `None` |
| `AiReply` | `raw_body: bytes, text: str, model_used: str, provider_used: str, usage: Usage, generation_id: str` | The exact reply, saved before it is parsed (D8) |
| `AiRecord` | `record_id: RecordId, schema_version: int, review_id: ReviewId, step: str, attempt: int, request_sha256: str, request: AiRequest, reply: AiReply \| None, error_code: str \| None, started_at: datetime, finished_at: datetime` | Raw and append-only, failed calls too (D1, D8); its hash keys the cache and the replay fake. Every datetime is timezone-aware |
| `UnreadableSpans` | `hidden: tuple[Span, ...], undecodable: tuple[Span, ...]` | The Rule 9 input; `unreadable_spans(document)` builds it |
| `LabelInput` | `position: Position, match: MatchResult, values: tuple[CheckedValue, ...], judged: tuple[JudgedLevel, ...], outside_documents: tuple[OutsideDocument, ...]` | Everything the label rules need for one position, in one bundle (I3) |
| `ValueVerdict` | `clause_id: ClauseId, level: Level, reasons: tuple[ReasonCode, ...], evidence: Evidence \| None, readable_value: str \| None` | One value after Rules 1 to 3, 5, 6 and 9, before Rule 4 combines them; `readable_value` is `None` exactly when `level` is `UNSURE` |
| `ScanContext` | `label: Level \| None, allowed_numbers: tuple[Decimal, ...], acceptable_limits: tuple[Decimal, ...], known_placeholders: tuple[str, ...], defined_roles: tuple[str, ...], clause_numbers: tuple[str, ...], quote: str \| None, source_text: str \| None, instruction_given: bool` | What one output scan compares the AI text with |
| `QuoteFold` | `text: str, to_original: tuple[int, ...]` | The Spec 2 quote-check fold, with its index map; one entry per folded character plus a last entry equal to the original length |
| `DrawAllowed` | `evidence: Evidence` | The last check before drawing approved this evidence |
| `DrawRefused` | `failure: DrawFailure` | The last check refused; a separate type, so a refusal cannot pass as an approval (I4) |
| `CallPrices` | `input_per_million: Decimal, cached_input_per_million: Decimal, output_per_million: Decimal` | US dollars per million tokens, passed in by the caller (ADR 0015) |
| `CostInputs` | `positions: int, words_positions: int, clauses: int, contract_tokens: int, prices: CallPrices` | The input of the pre-run estimate (section 7) |
| `CostRange` | `calls: int, low_usd: Decimal, high_usd: Decimal` | The estimate: the call count, and the cost from "cache hits on every call" (low) to "never hits" (high) |
| `PlaybookProblem` | `position_id: PositionId \| None, code: PlaybookProblemCode` | One failed playbook check (Spec 4.1); `position_id` is `None` for a whole-playbook problem |
| `CancelCheck` | a type alias: `Callable[[], bool]` | Returns True once the user has cancelled (ADR 0005) |
| `check_before_drawing(document: Document, clause: Clause, evidence: Evidence, quote_text: str) -> DrawAllowed \| DrawRefused` | approval with the evidence, or a refusal naming one `DrawFailure` | The last check before drawing (system design 4.2): clause, then cited sentences, then the quote span inside them, then the folded quote found exactly once in the cited region and mapped back to the exact span. With glyphs, every quoted character's box must sit on its known page (invariant 6); a document without glyphs skips the boxes (decided 14 Nov 2026). Two types, so a refusal cannot pass as an approval (I4). Shares only the fold with the stage 8 quote check (system design 15.8) |

## Ports
The five ports are `typing.Protocol` classes in `ports.py` (P4, B3). Adapters are passed in,
never imported. Each method's docstring holds `Input`, `Output`, `Raises` and `Side effects`.
Every real adapter must pass the same contract suite in `tests/contracts/` (T2, ADR 0005).

| Port | Methods | Notes |
| --- | --- | --- |
| `AiClient` | `complete(request: AiRequest) -> AiReply` | Raises model-service errors. Network retries live in the adapter; the one reask lives in the step (ADR 0005) |
| `PiiDetector` | `find(text: str) -> tuple[PiiSuggestion, ...]` | Behind the code finders (ADR 0008) |
| `ReviewStore` | `save_record(record: AiRecord) -> None`; `load_records(review_id: ReviewId) -> tuple[AiRecord, ...]`; `list_reviews() -> tuple[ReviewId, ...]`; `delete_review(review_id: ReviewId) -> None`; `purge_expired(now: datetime, auto_delete_days: int) -> tuple[ReviewId, ...]` | Hides the encrypted store (ADR 0006). `save_record` raises `DuplicateRecordError` for a saved `record_id` (append-only, D1); `load_records` returns records in the order saved, or `()`; `delete_review` is idempotent (I8); `purge_expired` deletes the reviews due under the auto-delete rules and returns their ids, sorted. Until stage 6, a review's last change is the latest `finished_at` of its records |
| `SecretStore` | `get_secret(provider_id: str) -> str \| None`; `put_secret(provider_id: str, secret: str) -> None`; `delete_secret(provider_id: str) -> None` | Each raises `SecretStoreUnavailableError` when the store cannot be reached; `get_secret` returns `None` when nothing is stored; `delete_secret` is idempotent (I8). Never plain text (ADR 0006, ADR 0015) |
| `Clock` | `now() -> datetime` | Returns a timezone-aware time (T2) |

## Fakes
The fakes live in `fakes.py`, use only the standard library and `core`, and are exported from
`clause_tracer.core`. Every real adapter must pass the same contract suite in `tests/contracts/`
(ADR 0013, T12).

| Fake | Port | Behaviour |
| --- | --- | --- |
| `ReplayAiClient(recordings)` | `AiClient` | Keys are `request_sha256` values; the client keeps a copy. `complete` returns the recorded reply and marks the key used; a miss raises `UnrecordedRequest` (an `AssertionError`, so a caught `ClauseTracerError` cannot swallow it) naming the step and the hash. A recording may be asked for more than once. `unused_keys()` returns the sorted keys never asked for; `fail_next(error_type)` makes the next call raise that model-service error, once. `assert_all_used(client)` raises `AssertionError("unused recordings: …")` when any key is unused |
| `FakePiiDetector(planted)` | `PiiDetector` | `find(text)` returns the suggestions planted for that exact text, or `()` for a text not planted |
| `InMemorySecretStore(available=True)` | `SecretStore` | Keeps secrets in a dict. `set_available(False)` makes each of the three `SecretStore` methods raise `SecretStoreUnavailableError({"provider_id": …})`. `delete_secret` of a missing id does nothing (I8) |
| `InMemoryReviewStore()` | `ReviewStore` | Keeps raw records in memory. `save_record` raises `DuplicateRecordError({"record_id": …})` for a record id any review already holds (append-only, D1); `load_records` returns the order saved, or `()`; `list_reviews` returns the sorted ids of reviews holding at least one record; `delete_review` is idempotent (I8); `purge_expired(now, days)` deletes each review whose latest `finished_at` is due under the auto-delete rules and returns their ids, sorted (the stage 1 stand-in for a review's last change) |
| `FixedClock(now)` | `Clock` | Returns the fixed time. `set(when)` sets it; `advance(delta)` moves it (a negative delta moves it back). A naive datetime raises `ValueError("datetime must be timezone-aware")` |
| `UnrecordedRequest` | — | The replay fake's miss, a test failure, not a project error |

## Functions

| Function | Returns | Notes |
| --- | --- | --- |
| `LAW_WORDS`, `ADVICE_PHRASES`, `INJECTION_PHRASES`, `CONTACT_WORDS`, `FIRST_PERSON_WORDS`, `FILLER_PHRASES`, `EVALUATIVE_WORDS`, `ABBREVIATIONS` | word lists, each a `tuple[str, ...]` | The output scans' word lists, copied from the owner's scan table (T11); a test checks the copy matches. The owner owns the values |
| `LENGTH_CAPS: Mapping[TextSlot, int]` | one maximum length in characters per kind of AI text | Read-only (`MappingProxyType`); values from the owner's scan table. Text over its cap fails the scan (Spec 6.2) |
| `contains_phrase(text: str, phrase: str) -> bool` | True when the phrase appears as a whole word or phrase, in any letter case | Curly apostrophes in the text are made straight first, so a phrase written with straight ones matches (question 17a) |
| `count_sentences(text: str) -> int` | the number of sentences by the scans' own small rule | A sentence ends at ".", "?" or "!" then a space or the end (`SENTENCE_END_PATTERN`); "1.5" and the listed abbreviations do not end one; text with no end mark is one sentence. The stage 2 splitter is not used: core imports no other module |
| `scan_text(text: str, slot: TextSlot, label: Level \| None) -> tuple[ScanFinding, ...]` | the word and pattern findings: `TOO_LONG`, law words, advice, injection tells, contact words, web and email addresses, `WRONG_LABEL_WORD` | In `ScanFinding` member order, no repeats; empty when the text passes. `WEB_ADDRESS_PATTERN` and `EMAIL_PATTERN` hold what counts as an address (question 17e); `LABEL_WORDS` holds each level's words, and any word of another level is flagged (question 17d) |
| `has_clause_number(text: str, clause_numbers: Iterable[str]) -> bool` | True when the text names one of the clause numbers the step was given | The whole number must appear alone: "5.4" is found in "Read 5.4." but not in "5.40" or "15.4" |
| `has_quoted_word(text: str, quote: str \| None) -> bool` | True when the text quotes a word of at least four letters that is in the quote | Both texts are folded first (`MIN_ANCHOR_LETTERS = 4`), so curly double quotes count as straight ones; `None` never anchors |
| `mask_abbreviations(text: str) -> str` | the text with every listed abbreviation blanked to spaces, same length | Both texts of a style comparison are masked, so "i.e." is never read as the first-person "I". An abbreviation in `NUMBER_ABBREVIATIONS` ("no.") is masked only when a digit follows, so "No. 5" does not end a sentence but "no." before a word does. `FIRST_PERSON_SLOTS` holds the slots the first-person scan checks (the message and question are the user's own voice, question 18a) |
| `scan_style(text: str, slot: TextSlot, context: ScanContext) -> tuple[ScanFinding, ...]` | the style findings: `FIRST_PERSON`, `FILLER_PHRASE` (a listed phrase or an added `!`), `EVALUATIVE_WORD`, `NO_ANCHOR`, `ADDED_SENTENCE` | Before the first-person scan, bracketed Roman-numeral list markers such as "(i)" are blanked (`LIST_MARKER_PATTERN`), so they are not the word "I". A listed word counts only when the AI added it: the comparison source is `source_text` for `MESSAGE` and `REWRITE`, the quote for the rest (question 18b). A reason with neither a clause number nor a quoted word from its quote fails (`NO_ANCHOR`). A message may not add a sentence over its template, nor a rewrite over its clause unless the user gave an instruction; with no source to compare, the scan fails closed (`ADDED_SENTENCE`). Findings in `ScanFinding` member order, no repeats |
| `scan_ai_text(text: str, slot: TextSlot, context: ScanContext, detector: PiiDetector) -> tuple[ScanFinding, ...]` | every finding of one piece of AI text: `scan_text` and `scan_style`, plus `UNKNOWN_PLACEHOLDER`, `ACCEPTABLE_LIMIT`, `NUMBER_NOT_ALLOWED` and `PERSONAL_DATA` | Numbers are digits only — with optional thousands separators and decimals; numbers written in words are not checked in stage 1 (question 17b). An acceptable limit fails in every slot, even when also allowed (17c, 17f). A number inside a placeholder is not the AI's; an unknown "⟦…⟧" fails. A detector finding passes only when it is a defined role (17d: `PiiDetector` is passed in, never imported). Findings in `ScanFinding` member order, no repeats |
| `level_rank(level: Level) -> int` | `PREFERRED` 0, `ACCEPTABLE` 1, `WALK_AWAY` 2 | `UNSURE` raises `ValueError("unsure has no rank")` |
| `is_better(a: Level, b: Level) -> bool` | `level_rank(a) < level_rank(b)` | Strictly better; unsure has no rank |
| `worst_level(levels: Iterable[Level]) -> Level` | the level with the highest rank | An empty input raises `ValueError` |
| `spans_overlap(a: Span, b: Span) -> bool` | `a.start < b.end and b.start < a.end` | Half-open spans (section 4.2) |
| `unreadable_spans(document: Document) -> UnreadableSpans` | every `HiddenText.span` that is not `None`, in order, as `hidden`; `document.undecodable` as `undecodable` | The Rule 9 input |
| `sort_reasons(reasons: Iterable[ReasonCode]) -> tuple[ReasonCode, ...]` | the reasons without repeats, in `ReasonCode` member order | Rules return codes in a fixed order (I7) |
| `check_playbook(playbook: Playbook) -> tuple[PlaybookProblem, ...]` | the playbook's problems, empty when it passes (Spec 4.1) | In playbook order; within one position, in `PlaybookProblemCode` member order. A `RULE_TYPE_MISMATCH` skips the position's other checks. Stages 6 and 12 share it (ADR 0005, 14 Nov 2026) |
| `convert_to_unit(number: Decimal, unit_as_written: str \| None, target: Unit) -> Fraction \| ReasonCode` | the number in the target unit, or `BUSINESS_DAYS` / `UNIT_UNKNOWN` (Rule 6) | `None` means already in the target unit (16a). Spelling normalised: lower case, stripped, space runs collapsed, one trailing `.` dropped. Week 7 days, month 30, year 365 or 12 months |
| `evidence_reasons(evidence: Evidence \| None, unreadable: UnreadableSpans) -> tuple[ReasonCode, ...]` | `QUOTE_NOT_CONFIRMED` when evidence is `None`; else `HIDDEN_TEXT` / `UNDECODABLE_TEXT` when the quote overlaps such a span | An unplaced quote keeps its label (Rule 3, ADR 0012) |
| `fold_for_quote_check(text: str) -> QuoteFold` | the folded text and its index map (Spec 2 quote check) | Curly quotes (‘ ’ ‚ ‛ and “ ” „ ‟) become straight; a run of whitespace becomes one `" "`, mapped to the run's first character; every other character is kept. `to_original` has one entry per folded character, plus a last entry equal to `len(text)`; folding never changes a character the fold does not name, so offsets count code points |
| `fold_for_matching(text: str) -> MatchKey` | the wide folded text and its index map, for finding names, terms and keywords (system design 4.2) | NFKC and case-folding for each character together with the combining marks after it, so `ß` becomes `ss`, `ﬁ` becomes `fi` and `e` with a combining accent becomes `é`, mapped to the index of the `e`; soft hyphens, zero-width and bidi characters dropped; curly quotes straight; U+2010 to U+2015 and U+2212 one hyphen; a run of whitespace becomes one `" "`, mapped to the run's first character. `to_canonical` has one entry per folded character, plus a last entry equal to `len(text)`. Folding can change the length, so a folded span is found through the map |
| `level_for_limits(rule: NumberRule, number: Fraction) -> Level` | preferred, acceptable or walk-away by the rule's limits (Rule 1) | Lower-is-better uses `<=`; higher-is-better `>=` |
| `number_verdicts(rule: NumberRule, value: CheckedValue, unreadable: UnreadableSpans) -> tuple[ValueVerdict, ...]` | the verdicts of one number value, before Rule 4 combines them | Unlimited: walk-away when lower is better, unsure with `UNLIMITED_UNCLEAR` when higher is better. Amount without total → `AMOUNT_WITHOUT_TOTAL`; amount and percent compared rounded half up to a whole percent. A range gives one verdict per end with `RANGE`; `RANGE` is added whenever `range_high` is given, even when the value is unsure, and the range end is the last number, not compared with the computed percentage. Any reason from `UNSURE_REASONS` → one unsure verdict |
| `yes_no_verdict(rule: YesNoRule, value: CheckedValue, unreadable: UnreadableSpans) -> ValueVerdict` | `YES` takes the rule's yes level; `NO`, `UNCLEAR` and `MISSING` take the no level (Rule 2) | A conditional yes is unsure with `CONDITIONAL_YES`; no answer → `NO_VALUE`; any unsure reason → unsure |
| `words_verdict(judged: JudgedLevel, unreadable: UnreadableSpans) -> ValueVerdict` | the judged level, kept as it is | An unsure judgement is unsure with `JUDGED_UNSURE`; hidden or undecodable text under it → unsure (Rule 9) |
| `combine_rule_4(verdicts: tuple[ValueVerdict, ...]) -> tuple[Level, tuple[ReasonCode, ...]]` | the Rule 4 level and the sorted reasons of every value | Walk-away if any readable value is walk-away, else unsure if any value is unsure, else the worst level. Readable values that differ between clauses add `CLAUSES_DISAGREE`. An empty tuple raises `ValueError` |
| `label_position(item: LabelInput, unreadable: UnreadableSpans) -> ToolLabel` | the label of one position (Rules 3, 4, 7 and 10) | Raises `ValueError` when any part names another position, the rule class does not match the type, or a words position holds values (or a number/yes-no one holds judged levels). A failed call, an unconfirmed match or a found match with no value is unsure. Missing takes the rule's no level for yes/no, else the position's missing level. An outside document makes the label unsure, except a walk-away Rule 4 step 1 gave. `written_by` is AI only for a words position the AI judged to a readable level (ADR 0002) |
| `label_all(playbook: Playbook, inputs: tuple[LabelInput, ...], unreadable: UnreadableSpans) -> tuple[ToolLabel, ...]` | one label per playbook position, in playbook order | Raises `ValueError` when a position has no input, two inputs name one position, or an input names a position not in the playbook |
| `to_plain(value: object) -> object` | the value as JSON-serialisable plain data | Checked in this order: `None`, `bool`, `int`, `float` stay; an `Enum` member becomes its value; a `str` stays; a `Decimal` becomes its `str`; a `datetime` becomes its `isoformat`; `bytes` become base64 ascii; a tuple or list becomes a list; a `Mapping` becomes a dict (a non-`str` key raises `TypeError`); a dataclass instance becomes `{"__type__": <qualname>, <field>: <plain>, ...}`. Anything else raises `TypeError(f"cannot hash {type(value).__name__}")` |
| `request_sha256(request: AiRequest) -> str` | the sha256 of the exact request | `hashlib.sha256(json.dumps(to_plain(request), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()`. Keys the cache, the resume and the replay fake (system design 7) |
| `due_at(last_change: datetime, days: int, protected_until: datetime \| None = None) -> datetime` | `last_change + timedelta(days=days)`, or `protected_until` when that is later | Pure; reads no clock. `ValueError("days must be 1 or more")` when `days < 1`; `ValueError("datetime must be timezone-aware")` for a naive datetime (Spec 9) |
| `estimate_calls(positions: int, words_positions: int, clauses: int) -> int` | the AI calls of a review, from the table in system design 7 | Forward match per position, reverse-match batches and sort calls per 25 clauses, pair checks per 4 positions, one extraction per number/yes-no position, a judge and an explain call per words position (explain counts for words positions only, per system design 7). `TASK_TOKENS_PER_CALL = 1000`, `OUTPUT_TOKENS_PER_CALL = 400`. Raises `ValueError` on a negative count or `words_positions > positions` |
| `estimate_cost(inputs: CostInputs) -> CostRange` | the call count, and the cost from "cache hits on every call" (low) to "never hits" (high) | Prices come from the caller (ADR 0015); both ends rounded half up to $0.0001. Raises `ValueError` on a negative count, `words_positions > positions`, or a negative price (Spec 9, system design 7) |
| `is_due(last_change: datetime, days: int, now: datetime, protected_until: datetime \| None = None) -> bool` | `now >= due_at(...)` | A clock behind `last_change` is never due, so a jump backwards deletes nothing (Spec 9, decided 14 Nov 2026) |
| `in_warning_window(last_change: datetime, days: int, now: datetime, protected_until: datetime \| None = None) -> bool` | `due_at(...) - WARNING_WINDOW <= now < due_at(...)` | The last three days before the due date; closed at the start, open at the end |
| `protected_until_after_lowering(lowered_at: datetime) -> datetime` | `lowered_at + LOWERING_GRACE` | The end of the three-day grace held after the setting was lowered. `WARNING_WINDOW` and `LOWERING_GRACE` are both `timedelta(days=3)` |

Two folds: `fold_for_quote_check` is the narrow Spec 2 fold that confirms a quote; `fold_for_matching` is the wide fold for finding names, terms and keywords. A quote is never confirmed on the wide fold.

## Owner tables
The expected answers of the acceptance tests live in `tests/tables/`. Only the owner edits them (Constitution T11): no commit may change code and an owner table together, and `scripts/check_owner_tables.py` checks this. Each file starts with the header line, then a `# Format:` line naming its owner task.

| File | Columns | Owner task |
| --- | --- | --- |
| `label_rules.toml` | `id`, `rule`, `note` (optional), one input in the sample format (`position`, `match`, optional `values`, `judged`, `clauses_to_read`, `outside_documents`), then the expected `level`, `reasons`, `written_by` | S1-M3-T6 |
| `units.toml` | `id`, `number`, `unit` (absent for none), `target`, `expected` (a fraction string or a reason code value) | S1-M3-T7 |
| `spec_14_5.toml` | `id`, `position`, `level`, `reasons`, `written_by`: one row per starter position | S1-M3-T8 |
| `playbook_checks.toml` | `id`, `positions` (position tables in the sample format), `problems` (`{ position, code }` tables, empty when the playbook passes) | S1-M3-T9 |
| `auto_delete.toml` | `id`, `last_change`, `now`, `days`, `protected_until` (optional), then the expected `due_at`, `due`, `warning` | S1-M4-T5 |
| `scans.toml` | `[lists]` (the eight word lists), `[caps]` (one length cap per `TextSlot`), and `[[case]]` rows: `id`, `text`, `slot`, `label`, `allowed_numbers`, `acceptable_limits`, `known_placeholders`, `defined_roles`, `personal_data`, `clause_numbers`, `quote`, `source_text`, `instruction_given`, then the expected `findings` | S1-M5-T1 |
| `cost_estimate.toml` | `id`, `positions`, `words_positions`, `clauses`, `contract_tokens`, `input_per_million`, `cached_input_per_million`, `output_per_million`, then the expected `calls`, `low_usd`, `high_usd` | S1-M5-T9 |
| `match_fold.toml` | `id`, `text`, `expected` (the folded text) | S2-M5-T1 |

## Depends on
Nothing. It imports no other clause_tracer module.

## Run alone
`.venv/bin/uv run python -m clause_tracer.core [--input <sample.toml>]`

Labels the Spec 14.5 sample (`samples/spec-14-5.toml`), or the sample file given with `--input`, and prints one line per position, in playbook order: position id, topic, level, the reasons joined by `,` (or `-` when none) and the written-by value, separated by tabs. It exits 0. A file that cannot be read, or is not a valid sample, prints `clause_tracer.core: …` to standard error and exits 3 ("input file", system design 6.2).
