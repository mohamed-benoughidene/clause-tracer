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

## Functions

| Function | Returns | Notes |
| --- | --- | --- |
| `level_rank(level: Level) -> int` | `PREFERRED` 0, `ACCEPTABLE` 1, `WALK_AWAY` 2 | `UNSURE` raises `ValueError("unsure has no rank")` |
| `is_better(a: Level, b: Level) -> bool` | `level_rank(a) < level_rank(b)` | Strictly better; unsure has no rank |
| `worst_level(levels: Iterable[Level]) -> Level` | the level with the highest rank | An empty input raises `ValueError` |
| `spans_overlap(a: Span, b: Span) -> bool` | `a.start < b.end and b.start < a.end` | Half-open spans (section 4.2) |
| `unreadable_spans(document: Document) -> UnreadableSpans` | every `HiddenText.span` that is not `None`, in order, as `hidden`; `document.undecodable` as `undecodable` | The Rule 9 input |
| `sort_reasons(reasons: Iterable[ReasonCode]) -> tuple[ReasonCode, ...]` | the reasons without repeats, in `ReasonCode` member order | Rules return codes in a fixed order (I7) |
| `check_playbook(playbook: Playbook) -> tuple[PlaybookProblem, ...]` | the playbook's problems, empty when it passes (Spec 4.1) | In playbook order; within one position, in `PlaybookProblemCode` member order. A `RULE_TYPE_MISMATCH` skips the position's other checks. Stages 6 and 12 share it (ADR 0005, 14 Nov 2026) |
| `convert_to_unit(number: Decimal, unit_as_written: str \| None, target: Unit) -> Fraction \| ReasonCode` | the number in the target unit, or `BUSINESS_DAYS` / `UNIT_UNKNOWN` (Rule 6) | `None` means already in the target unit (16a). Spelling normalised: lower case, stripped, space runs collapsed, one trailing `.` dropped. Week 7 days, month 30, year 365 or 12 months |
| `evidence_reasons(evidence: Evidence \| None, unreadable: UnreadableSpans) -> tuple[ReasonCode, ...]` | `QUOTE_NOT_CONFIRMED` when evidence is `None`; else `HIDDEN_TEXT` / `UNDECODABLE_TEXT` when the quote overlaps such a span | An unplaced quote keeps its label (Rule 3, ADR 0012) |
| `level_for_limits(rule: NumberRule, number: Fraction) -> Level` | preferred, acceptable or walk-away by the rule's limits (Rule 1) | Lower-is-better uses `<=`; higher-is-better `>=` |
| `number_verdicts(rule: NumberRule, value: CheckedValue, unreadable: UnreadableSpans) -> tuple[ValueVerdict, ...]` | the verdicts of one number value, before Rule 4 combines them | Unlimited: walk-away when lower is better, unsure with `UNLIMITED_UNCLEAR` when higher is better. Amount without total → `AMOUNT_WITHOUT_TOTAL`; amount and percent compared rounded half up to a whole percent. A range gives one verdict per end with `RANGE`; `RANGE` is added whenever `range_high` is given, even when the value is unsure, and the range end is the last number, not compared with the computed percentage. Any reason from `UNSURE_REASONS` → one unsure verdict |
| `yes_no_verdict(rule: YesNoRule, value: CheckedValue, unreadable: UnreadableSpans) -> ValueVerdict` | `YES` takes the rule's yes level; `NO`, `UNCLEAR` and `MISSING` take the no level (Rule 2) | A conditional yes is unsure with `CONDITIONAL_YES`; no answer → `NO_VALUE`; any unsure reason → unsure |
| `words_verdict(judged: JudgedLevel, unreadable: UnreadableSpans) -> ValueVerdict` | the judged level, kept as it is | An unsure judgement is unsure with `JUDGED_UNSURE`; hidden or undecodable text under it → unsure (Rule 9) |
| `combine_rule_4(verdicts: tuple[ValueVerdict, ...]) -> tuple[Level, tuple[ReasonCode, ...]]` | the Rule 4 level and the sorted reasons of every value | Walk-away if any readable value is walk-away, else unsure if any value is unsure, else the worst level. Readable values that differ between clauses add `CLAUSES_DISAGREE`. An empty tuple raises `ValueError` |
| `label_position(item: LabelInput, unreadable: UnreadableSpans) -> ToolLabel` | the label of one position (Rules 3, 4, 7 and 10) | Raises `ValueError` when any part names another position, the rule class does not match the type, or a words position holds values (or a number/yes-no one holds judged levels). A failed call, an unconfirmed match or a found match with no value is unsure. Missing takes the rule's no level for yes/no, else the position's missing level. An outside document makes the label unsure, except a walk-away Rule 4 step 1 gave. `written_by` is AI only for a words position the AI judged to a readable level (ADR 0002) |
| `label_all(playbook: Playbook, inputs: tuple[LabelInput, ...], unreadable: UnreadableSpans) -> tuple[ToolLabel, ...]` | one label per playbook position, in playbook order | Raises `ValueError` when a position has no input, two inputs name one position, or an input names a position not in the playbook |
| `to_plain(value: object) -> object` | the value as JSON-serialisable plain data | Checked in this order: `None`, `bool`, `int`, `float` stay; an `Enum` member becomes its value; a `str` stays; a `Decimal` becomes its `str`; a `datetime` becomes its `isoformat`; `bytes` become base64 ascii; a tuple or list becomes a list; a `Mapping` becomes a dict (a non-`str` key raises `TypeError`); a dataclass instance becomes `{"__type__": <qualname>, <field>: <plain>, ...}`. Anything else raises `TypeError(f"cannot hash {type(value).__name__}")` |
| `request_sha256(request: AiRequest) -> str` | the sha256 of the exact request | `hashlib.sha256(json.dumps(to_plain(request), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()`. Keys the cache, the resume and the replay fake (system design 7) |

## Depends on
Nothing. It imports no other clause_tracer module.

## Run alone
`.venv/bin/uv run python -m clause_tracer.core`
