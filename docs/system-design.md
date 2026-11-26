# System design: Clause Tracer version 1

11 Nov 2026 · status: **accepted** on 12 Nov 2026

This is the design of the whole of version 1: the Python engine, the desktop shell around it, storage, packaging and release. It says how the parts fit, what each one promises, and which choices are still open. Build stages 1 (`core`), 2 (`ingest`) and 3 (`links`) are built; the other modules are empty skeletons.

**How to read it.** [`spec.md`](spec.md) says what the app does, and wins if this file disagrees with it. Each choice below that is hard to undo has a decision record (ADR) with its runner-up. The project owner accepted them all on 12 Nov 2026 (section 13). The evidence is in [the v1 design decisions report](../reports/Clause%20Tracer%20v1%20design%20decisions.md). How to test all of it is in [`testing-strategy.md`](testing-strategy.md). The rules the code must follow are in the [Constitution](../Constitution.md), cited here by ID. The order in which it is built is section 15.

## 1. Requirements

### 1.1 What it does

Clause Tracer checks one contract against the user's own playbook and shows the evidence for every label. The full behaviour is Spec sections 3 to 7. The design rests on four promises from the Spec:

1. **Code decides wherever it can.** Code picks number and yes/no labels, checks every quote and number, and chooses what runs next (Spec 5, 6.1, 8.4).
2. **Only placeholder text leaves the computer**, and only to the AI provider the user chose (Spec 8.1).
3. **Everything saved is encrypted**, and reviews delete themselves on a schedule (Spec 8.3, 9).
4. **No telemetry, no accounts, no server run by the project** in version 1 (Spec 1, 8.1, 12).

### 1.2 Qualities it must have

| Quality | Target for version 1 | Source |
| --- | --- | --- |
| Privacy | No confirmed personal item, note or name in any outgoing request or log. Proven by test on every change | Spec 11 |
| Correct labels | Every planted walk-away found. At least 90% of numbers and labels correct on the test set | Spec 11 |
| Evidence | No quote reaches the screen unless code found it word for word in the contract | Spec 11 |
| Cost per review | `[Assumption]` by the formula of section 7, at $2.00 input, $0.20 cached input and $10.00 output per million tokens: $0.29 to $1.32 for a 10,000-word contract and $0.75 to $5.88 for 50,000 words on a Sonnet-class model; 1.5 to 7 cents for 10,000 words on Claude Haiku 5.5. The low end is every call hitting the cache, the high end none | [ADR 0010](adr/0010-starting-models.md), amendment of 16 Nov 2026 |
| Input size | `[Assumption]` files up to 20 MB and 50,000 words (about 95,000 tokens at the 1.9 tokens per word the 13 Nov 2026 probe measured, [ADR 0010](adr/0010-starting-models.md); about 2,500 sentences) | Spec 9 |
| Offline | Saved reviews open offline. A draft can be prepared offline. Only AI steps need the internet | Spec 9 |
| Systems | Linux (Ubuntu 24.04 and later, Mint 22 and later, Debian 13, Fedora by archive) and Windows 10/11. Mac later | Spec 9 |
| Download | As small as the personal-data model allows. `[Assumption]` roughly 150 to 250 MB installed with the medium model; not yet measured | [ADR 0008](adr/0008-personal-data-detection-bundle.md) |
| Resume | An interrupted review continues from the first unfinished step. Finished AI calls are never paid for twice | Spec 6.3 |
| Upkeep | One person can review every line that ships. That means Python, plus the HTML, CSS and JavaScript of the existing prototype | Constraint below |

There is no load or scaling target. The app serves one user on one computer, and runs one review at a time.

### 1.3 Constraints

- **One developer, who reviews Python.** AI agents write most code. Any Rust or TypeScript would ship unreviewed, so the design avoids both.
- **No Windows machine.** The developer works on Debian. Windows builds must be built and tested by CI.
- **Licence rule.** The project is source available under FSL-1.1-ALv2. Runtime dependencies must be MIT, BSD or Apache. No GPL or AGPL. Two named exceptions, both allowed on 12 Nov 2026: `pikepdf` (MPL-2.0) for reading hidden PDF layers ([ADR 0007](adr/0007-document-reading-stack.md)), and PyGObject (LGPL) on Linux, the bridge that lets Python open the window ([ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md)). The app shows a third-party licences page.
- **Tie-break.** When two good options conflict, the better experience for non-technical freelancers wins: a small download, a quick start and a smooth install.
- **Later, not now.** A future version may let the project itself become the AI provider, with optional accounts. Version 1 must not block that (section 11).

## 2. The system in one picture

```text
 ┌──────────────────────────── the user's computer ────────────────────────────┐
 │                                                                              │
 │  ┌─────────────── shell process (Python, pywebview) ───────────────┐         │
 │  │  system webview  ◄── js_api facade ──►  engine client           │         │
 │  │  (prototype HTML,     (narrow, typed)    (spawns and talks      │         │
 │  │   CSS, JS)                                to the engine)        │         │
 │  └─────────────────────────────────────────────┬──────────────────┘         │
 │                        newline-delimited JSON over stdin/stdout             │
 │  ┌──────────────────────────────────────────────▼─────────────────┐         │
 │  │ engine process: the same executable, `clause-tracer serve --stdio`       │
 │  │                                                                 │         │
 │  │   cli ── runner ──► ingest ► privacy ► links ► checking ► writing ► outputs
 │  │    │                    (pipeline modules import only core)     │         │
 │  │    └─ wires adapters:  storage · keyring · presidio · openrouter│         │
 │  └───────┬──────────────┬────────────────────────────┬─────────────┘         │
 │          ▼              ▼                            │                       │
 │   encrypted store   OS password store                │                       │
 │   (data folder)     (master key, API key)            │                       │
 └──────────────────────────────────────────────────────┼───────────────────────┘
                                                        ▼  HTTPS, placeholder text only
                                        OpenRouter ──► AI provider (zero retention asked)

   GitHub Releases: opened only when the user presses "Check for updates".
```

Two processes, one executable. The shell draws the interface. The engine does all the work and is the same program the command-line tool runs. Both are Python.

## 3. Components

### 3.1 The engine

The engine keeps the layout in [ADR 0004](adr/0004-code-layout.md): a pure `core`, six pipeline modules, adapters at the edge, and `cli` as the only place that wires them together. `lint-imports` enforces the import rules.

| Part | Job | Hides this decision (B4) |
| --- | --- | --- |
| `core` | Shapes, ports, labelling rules, output scans, error types. No files, network, clock or third-party imports (T1) | What a label is and how it is picked |
| `ingest` | Read the file, build the canonical text, find hidden text, split clauses and sentences | Which PDF and Word libraries read a file |
| `privacy` | Suggest personal data, number placeholders, keep the exact map between the two texts | How names become placeholders and back |
| `links` | Cross-references, defined terms, overrides, references to other documents | The patterns that find a link |
| `checking` | Match, extract, quote check, judge, explain, sort not-covered parts | Prompts, reply forms and their checks |
| `writing` | Rewrite a clause as small edits that code applies | The rewrite form and its rules |
| `outputs` | The message and the report | Templates and the PDF library |
| `adapters` | OpenRouter, Presidio, storage, the password store | Each outside tool |
| `cli` | Commands, the step runner, wiring, the stdio server | The order of steps and how resume works |

**Ports.** `core` defines five small `typing.Protocol` ports, and `cli` passes the real adapters in (P4, T2). [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) records why each is a port. Section 3.4 lists their methods and the shapes `core` defines in stage 1.

| Port | Real adapter | Fake used in tests |
| --- | --- | --- |
| `AiClient` | `adapters/openrouter` | Replay fake keyed by request hash |
| `PiiDetector` | `adapters/presidio` | Fake that returns planted suggestions |
| `ReviewStore` | `adapters/storage` | In-memory store |
| `SecretStore` | `adapters/keyring` | In-memory store |
| `Clock` | Standard library, in `cli` | Fixed clock |

PDF and Word parsers, the report renderer and JSON handling are **not** ports. Each is an internal choice of one module (the P4 trap: a port for something that will not change).

### 3.2 The shell

The shell is **pywebview** ([ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md)). It shows the pages of [`../prototype/`](../prototype/) in the system webview (WebView2 on Windows, WebKitGTK on Linux), and every line of shell code is Python. It will live in its own top-level folder, as ADR 0004 says.

- **The interface never talks to the engine directly.** JavaScript calls a narrow Python facade through `window.pywebview.api`. The facade checks its inputs and forwards typed requests to the engine.
- **Untrusted content stays inert.** PDF pages are pictures. Contract, playbook and AI text is set with `textContent`, never as HTML. A content security policy forbids remote content: `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'`. `'unsafe-eval'` is needed because pywebview injects its Python bridge with `eval` (ADR 0009, 13 Nov 2026). Links open in the system browser after the Spec 4.3 warning. Developer tools and the remote debugging port are off in release builds.
- **Pages load from files, with no local server** (decided 12 Nov 2026; confirmed in trial builds on 13 Nov 2026, ADR 0009 amendments). pywebview is always given a `file://` address with its built-in server off; a bare path starts a local server. The shell must refuse any navigation away from its own files. Browser storage is not relied on (it is missing on Linux in private mode), so theme and text size are saved by Python through the facade.
- **The shell waits for the window's own start-up events** (decided 13 Nov 2026, ADR 0009 amendment). Before the first pywebview call, the shell waits for the window's `shown` and `loaded` events with its own longer timeout, because pywebview's fixed 20-second limit is too short where the desktop portal stalls.

### 3.3 Why two processes

The engine runs as a child process of the shell, started from the same frozen executable.

- **One engine for both forms.** The command-line tool and the desktop app run the same code through the same protocol (Spec 9).
- **A heavy or stuck step cannot freeze the window.** Personal-data detection and PDF reading are slow and run outside the interface process.
- **No port is opened** between shell and engine. They talk over stdin and stdout.
- **Hostile files are contained.** File parsing runs in its own short-lived child process with time and memory limits (section 8.4).

### 3.4 Core shapes for stage 1

This is the list of shapes and ports `core` defines in build stage 1 (section 15.1). It replaces the sketch in [the architecture report](../reports/Clause%20Tracer%20pipeline%20architecture.md#core-holds-the-shapes-the-rules-and-only-the-ports-that-earn-them), which predates ADRs 0005 to 0016. The list stays at the level of names, fields and types. Each module's README records the exact shapes it takes and returns (S3).

**Rules for every shape** ([ADR 0005](adr/0005-engine-runner-shapes-and-ports.md)):

- Frozen, slotted standard-library dataclasses, with tuples instead of lists and no third-party imports (T1, B3). Every shape is written `@dataclass(frozen=True, slots=True, kw_only=True)`, so it is always built with keyword arguments (decided 14 Nov 2026).
- Fields come in the order the tables below list them. A field has no default unless the table shows one.
- Every enum is an `enum.StrEnum`. Each member's value is its name in lower case: `Level.WALK_AWAY == "walk_away"`.
- Outside data is validated once, at the edge, with Pydantic `TypeAdapter` (D4, I9). AI reply schemas are Pydantic models in the module that owns the step, never in `core`.
- Ids are opaque strings made at the edge. `core` never makes an id or reads the clock (T1).
- Offsets are half-open, count code points, and point into `Document.text` (section 4.2).
- Stored records carry a schema version (D6). Shapes grow by new fields, never renames (D5).
- Nothing provider-specific: no zero-retention flags, cost-field names or model lists ([ADR 0015](adr/0015-provider-ready-seam.md)).
- Every piece of wording the app stores is a `Wording`, so it cannot be stored without its written-by value ([ADR 0016](adr/0016-legal-positions-without-a-lawyer.md), Spec 6.2). Contract quotes are spans into the contract, not wording.

**Check first.** ADR 0005 action item 2 is still open: confirm that Pydantic `TypeAdapter` validates straight into frozen, slotted dataclasses on the pinned version. Do this at the start of stage 1, before the shapes are written. If it fails, bring it to the owner. Pydantic is a runtime dependency from stage 1, locked in `uv.lock`, so the check runs on the version that ships; `core` still never imports it (decided 14 Nov 2026, [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) amendment).

**Ids and enums**

The values column gives the exact member names.

| Shape | Values | Why |
| --- | --- | --- |
| `ReviewId`, `PlaybookId`, `CustomerId`, `PositionId`, `ClauseId`, `SentenceId`, `RecordId` | `NewType` over `str` | Opaque ids. Clause and sentence ids come from the clause number and span, so they survive a re-read (section 5.1) |
| `Level` | `PREFERRED`, `ACCEPTABLE`, `WALK_AWAY`, `UNSURE` | The four labels, and the missing level (Spec 2) |
| `PositionType` | `NUMBER`, `YES_NO`, `WORDS` | Decides whether code or AI picks the label (Spec 5) |
| `Direction` | `LOWER_IS_BETTER`, `HIGHER_IS_BETTER` | Number positions (Spec 4.1) |
| `Unit` | `DAYS`, `PERCENT`, `MONTHS`, `ROUNDS` | Playbook units (Spec 4.1). Units as written in the contract stay text until Rule 6 converts them |
| `Answer` | `YES`, `CONDITIONAL_YES`, `NO`, `UNCLEAR`, `MISSING` | Yes/no extraction (Spec 6.1 step 6b) |
| `ReasonCode` | `QUOTE_NOT_CONFIRMED`, `NUMBER_NOT_IN_QUOTE`, `VAGUE_WORDING`, `OTHER_START_POINT`, `UNKNOWN_FIGURES`, `BUSINESS_DAYS`, `UNIT_UNKNOWN`, `AMOUNT_WITHOUT_TOTAL`, `AMOUNT_PERCENT_DISAGREE`, `CONDITIONAL_YES`, `RANGE`, `CLAUSES_DISAGREE`, `HIDDEN_TEXT`, `UNDECODABLE_TEXT`, `UNLOADED_DOCUMENT`, `REPLY_BROKEN_TWICE`, `MATCH_UNCONFIRMED`, `NO_VALUE`, `JUDGED_UNSURE`, `UNLIMITED_UNCLEAR`, in this order | Rules return codes, never prose. Templates turn codes into words ([ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md), I7). One code per cause in Spec 5. `NO_VALUE`, `JUDGED_UNSURE` and `UNLIMITED_UNCLEAR` cover inputs Spec 5 did not name at first (the stage 1 plan, section 6). `UNLIMITED_UNCLEAR` is "unlimited" on a position where higher is better (Rule 1). Reason tuples are sorted in this order |
| `UNSURE_REASONS` | A `frozenset[ReasonCode]` constant: every code except `RANGE`, `CLAUSES_DISAGREE` and `AMOUNT_PERCENT_DISAGREE` | A value that carries one of these is unsure. The three left out are notes shown beside a label |
| `WrittenBy` | `CODE`, `AI`, `USER` | ADR 0016 |
| `ReviewStatus` | `DRAFT`, `RUNNING`, `INTERRUPTED`, `FAILED`, `READY_TO_CHECK`, `DONE` | Spec 6.3 |
| `PrivacyMode` | `ON`, `OFF` | Neutral. The adapter maps it to the provider's settings (ADR 0015) |
| `FileKind` | `PDF`, `WORD`, `TEXT`, `MARKDOWN`, `PASTED` | Spec 9 file types |
| `PlaceholderKind` | `PERSON`, `COMPANY`, `ADDRESS`, `EMAIL`, `PHONE`, `ID`, `BANK` | Spec 4.2 |
| `SegmentKind` | `COPY`, `ENTITY`, `ESCAPE` | The placeholder map (section 4.2) |
| `HiddenReason` | `LOW_CONTRAST`, `TINY_FONT`, `OFF_PAGE`, `INVISIBLE_TEXT`, `HIDDEN_LAYER`, `WORD_HIDDEN_RUN`, `COMMENT`, `ZERO_WIDTH`, `BIDI_CONTROL` | Each finding names its cause. Stage 5 adds a member for any new check (D5) |
| `PiiSource` | `PARTY_DETAILS`, `PATTERN`, `RULE`, `NER`, `USER` | Overlaps resolve by source ([ADR 0008](adr/0008-personal-data-detection-bundle.md)) |
| `TextSlot` | `REASON`, `READING`, `QUESTION`, `MESSAGE`, `REWRITE` | The kinds of text the AI may write. Each has its own length cap (Spec 6.2). `REASON` is the reason of a words label the AI judged; `READING` and `QUESTION` are one of the two readings and the question to ask, for that label or for a value unsure because of vague wording; `MESSAGE` is "Rewrite with AI"; `REWRITE` is a clause rewrite (step 12). Code writes every other sentence in a label's panel, so it has no slot (decided 14 Nov 2026, Spec 6.1 step 10) |
| `ScanFinding` | `TOO_LONG`, `LAW_WORD`, `ADVICE`, `INJECTION_TELL`, `CONTACT_WORD`, `WEB_ADDRESS`, `EMAIL_ADDRESS`, `WRONG_LABEL_WORD`, `ACCEPTABLE_LIMIT`, `NUMBER_NOT_ALLOWED`, `UNKNOWN_PLACEHOLDER`, `PERSONAL_DATA`, `FIRST_PERSON`, `FILLER_PHRASE`, `EVALUATIVE_WORD`, `NO_ANCHOR`, `ADDED_SENTENCE`, in this order | What an output scan found. An empty tuple means the text passed (section 8.2). The last five are the style scans of Spec 6.2 (added 14 Nov 2026) |
| `DrawFailure` | `CLAUSE_MISMATCH`, `SENTENCE_UNKNOWN`, `EMPTY_QUOTE`, `SPAN_OUTSIDE_SENTENCES`, `QUOTE_NOT_FOUND`, `QUOTE_NOT_UNIQUE`, `SPAN_MISMATCH`, `CHAR_MAP_LENGTH`, `GLYPH_MISSING`, `PAGE_UNKNOWN`, `PAGE_MISMATCH`, `BOX_OUTSIDE_PAGE` | Why the last check before drawing refused (section 4.2) |
| `PlaybookProblemCode` | `DUPLICATE_POSITION_ID`, `RULE_TYPE_MISMATCH`, `LIMIT_NEGATIVE`, `PERCENT_OVER_100`, `LIMITS_NOT_STRICTER`, `YES_NO_LEVEL_UNSURE`, `YES_NOT_BETTER`, `MISSING_LEVEL_NOT_NO_LEVEL`, `LEVEL_TEXT_EMPTY` | The playbook checks of Spec 4.1, shared by stage 6 (reading files) and stage 12 (the editor) |
| `PLACEHOLDER_OPEN`, `PLACEHOLDER_CLOSE` | `str` constants `"⟦"` and `"⟧"` | The placeholder marker of Spec 4.2, as the testing strategy writes it (`⟦Person 1⟧`). The scans and `privacy` use the same constants |

**Shapes**

| Shape | Fields | Why |
| --- | --- | --- |
| `Wording` | `text: str, written_by: WrittenBy` | Every stored label reason, Missing text, question, message, rewrite and note (ADR 0016) |
| `Span` | `start: int, end: int` | A place in the canonical text |
| `PageBox` | `page: int, x0: float, top: float, x1: float, bottom: float` | PDF points, top-left origin, one coordinate system ([ADR 0007](adr/0007-document-reading-stack.md)) |
| `Page` | `number: int, width: float, height: float` | Lets the last check before drawing test that a box is inside its page. Pages are numbered from 1 |
| `Glyph` | `page: int, box: PageBox` | One drawn character. `page` is a `Page.number` and equals `box.page` |
| `SourceFile` | `name: str, kind: FileKind, sha256: str, size: int` | Points at the raw bytes, which the store keeps unchanged (D1) |
| `HiddenText` | `span: Span \| None, reason: HiddenReason, boxes: tuple[PageBox, ...]` | Flagged, never removed (D1). No span when the text is not in the canonical text, such as a hidden layer |
| `TrackedChange` | `earlier: str, new: str, author: str, span: Span \| None` | Listed at the contract check. The accepted view is the contract (ADR 0012) |
| `InputWarning` | `code: str, page: int \| None` | Undecodable pages, scanned pages in a mixed file, not English (Spec 9) |
| `Document` | `schema_version: int, source: SourceFile, text: str, char_map: tuple[int \| None, ...], glyphs: tuple[Glyph, ...], pages: tuple[Page, ...], furniture: tuple[Span, ...], hidden: tuple[HiddenText, ...], undecodable: tuple[Span, ...], tracked_changes: tuple[TrackedChange, ...], warnings: tuple[InputWarning, ...]` | The one canonical text. When the document has glyphs (a PDF), `char_map` has one entry per character of `text`: the index of its glyph in `glyphs`, or `None` for a character the app inserted. A document without glyphs (text, Markdown, pasted text, Word) has `glyphs == ()`, `char_map == ()` and `pages == ()` (decided 14 Nov 2026). Word comments are hidden text (Spec 2), so they sit in `hidden` |
| `MatchKey` | `text: str, to_canonical: tuple[int, ...]` | Folded copy with its index map (section 4.2). Built in `core` by the wide fold `fold_for_matching`; `to_canonical` has one last entry equal to the text's length |
| `Sentence` | `id: SentenceId, span: Span` | Stable ids such as `4.2.s3`, which the AI points at |
| `Clause` | `id: ClauseId, number: str \| None, heading: str \| None, level: int, parent_id: ClauseId \| None, span: Span, numbering_source: str, sentences: tuple[Sentence, ...]` | One clause, or one paragraph when the contract has no numbers (Spec 6.1 step 2). Ids come from the number and the order (section 5.1) |
| `CrossReference` | `source: Span, target: ClauseId \| None` | An unresolved target is kept, with no target |
| `DefinedTerm` | `term: str, definition: Span, uses: tuple[Span, ...]` | Evidence trail, and the privacy allow-list (section 4.1) |
| `Override` | `clause_id: ClauseId, target: ClauseId \| None, overrides_target: bool, evidence: Span` | Direction matters. No target means it joins every trail (Spec 4.5) |
| `OutsideDocument` | `name: str, evidence: Span` | Feeds the unloaded-document Read first row and Rule 10 |
| `LinkMap` | `references: tuple[CrossReference, ...], terms: tuple[DefinedTerm, ...], overrides: tuple[Override, ...], outside_documents: tuple[OutsideDocument, ...], undefined_terms: tuple[Span, ...]` | What `links` returns. `cli` passes `terms` into `privacy` |
| `Party` | `name: str, address: str \| None, yours: bool` | Typed party details: raw data, and the first privacy finder |
| `PiiSuggestion` | `span: Span, kind: PlaceholderKind, source: PiiSource` | What the `PiiDetector` port and the code finders return |
| `PlaceholderEntity` | `id: str, kind: PlaceholderKind, number: int, spans: tuple[Span, ...]` | One placeholder, such as Person 1, for every variant of one name |
| `Segment` | `kind: SegmentKind, sent: Span, original: Span, entity_id: str \| None` | Tiles both texts, so a quote maps back exactly |
| `PlaceholderText` | `text: str, entities: tuple[PlaceholderEntity, ...], segments: tuple[Segment, ...]` | The only contract text that leaves the computer |
| `NumberRule` | `unit: Unit, direction: Direction, preferred_limit: Decimal, acceptable_limit: Decimal` | Rule 1 |
| `YesNoRule` | `question: str, yes_level: Level, no_level: Level` | Rule 2. The missing level is always the "no" level |
| `WordsRule` | `preferred: str, acceptable: str, walk_away: str` | One sentence per level |
| `Position` | `id: PositionId, topic: str, type: PositionType, rule: NumberRule \| YesNoRule \| WordsRule, missing_level: Level, why_note: str \| None` | One playbook rule (Spec 4.1) |
| `Playbook` | `id: PlaybookId, schema_version: int, name: str, side: str, customer_id: CustomerId \| None, positions: tuple[Position, ...], starter: bool` | Starters are read-only |
| `PlaybookSnapshot` | `playbook: Playbook, taken_at: datetime, unedited_starter: bool` | Taken at "Send for review". Drives "by the example playbook" |
| `Evidence` | `clause_id: ClauseId, sentence_ids: tuple[SentenceId, ...], quote: Span, placed: bool` | A confirmed quote. `placed` is false when it could not be marked on the page; the label stays (ADR 0012) |
| `CheckedValue` | `position_id: PositionId, clause_id: ClauseId, evidence: Evidence \| None, raw_value: str \| None, number: Decimal \| None, range_high: Decimal \| None, unit_as_written: str \| None, start_point_as_written: str \| None, answer: Answer \| None, condition: Span \| None, vague: bool, amount: Decimal \| None, total: Decimal \| None, reasons: tuple[ReasonCode, ...], unlimited: bool = False` | One value after the quote check: the input of the number and yes/no label rules (Spec 6.1 step 6b). `unlimited` is true when the contract says the value has no limit, which Rule 1 makes the worst value. "None" reaches `core` as `number == 0`: the number parser of stage 8 turns it into 0 (decided 14 Nov 2026) |
| `JudgedLevel` | `position_id: PositionId, clause_id: ClauseId, evidence: Evidence \| None, level: Level` | One AI judgement for a words position (step 9) |
| `MatchFound`, `NothingFound`, `MatchUnconfirmed`, `CallFailed` | `position_id: PositionId, clause_ids: tuple[ClauseId, ...]`; `position_id: PositionId, searches: tuple[str, ...]`; `position_id: PositionId, clauses_to_read: tuple[ClauseId, ...]`; `code: str` | Four separate types, so a failed call can never pass as "nothing found" (I4). `searches` fills the "Where it was searched" panel. `MatchUnconfirmed` is the result when the searches disagree: the label is unsure with `MATCH_UNCONFIRMED`, and `clauses_to_read` names the clauses to read (ADR 0012; fourth type decided 14 Nov 2026). `MatchResult` is the type alias for the union of the four |
| `ToolLabel` | `position_id: PositionId, level: Level, reasons: tuple[ReasonCode, ...], evidence: tuple[Evidence, ...], written_by: WrittenBy` | `written_by` is AI only for words positions, which are drawn in pencil ([ADR 0002](adr/0002-label-look-split-stamp.md)) |
| `NotCoveredClause` | `clause_id: ClauseId, clause_type: str` | A type from the closed list, plus the clause's own first line ([ADR 0011](adr/0011-who-writes-the-words.md)). Replaces the sketch's `NotCoveredSummary` |
| `PromptMessage` | `role: str, text: str` | One rendered prompt part |
| `StepInputs` | No fields | The base class of every step's own input shape. Each step's input shape is a frozen, slotted, keyword-only dataclass that subclasses it. Stage 1 has only a test-only subclass; the real ones come with each step in stage 8 (decided 14 Nov 2026) |
| `AiRequest` | `step: str, prompt_id: str, prompt_version: int, inputs: StepInputs, messages: tuple[PromptMessage, ...], schema_id: str, json_schema: Mapping[str, object], model: str, privacy_mode: PrivacyMode, max_tokens: int` | The accepted form (section 6.3). It carries the structured inputs as well as the rendered prompt (ADR 0015). Its `__post_init__` replaces `json_schema` with a `MappingProxyType` copy, so the top level cannot be changed |
| `Usage` | `input_tokens: int, cached_input_tokens: int, output_tokens: int, cost_usd: Decimal \| None` | Cached tokens are read on every call ([ADR 0010](adr/0010-starting-models.md)). `cost_usd` is one neutral amount, filled in by the adapter from the provider's reply, or `None` when the provider reports none. It feeds the running cost, the spend ledger and the cost per review (decided 13 Nov 2026, [ADR 0015](adr/0015-provider-ready-seam.md) amendment) |
| `AiReply` | `raw_body: bytes, text: str, model_used: str, provider_used: str, usage: Usage, generation_id: str` | The exact reply, saved before it is parsed (D8) |
| `AiRecord` | `record_id: RecordId, schema_version: int, review_id: ReviewId, step: str, attempt: int, request_sha256: str, request: AiRequest, reply: AiReply \| None, error_code: str \| None, started_at: datetime, finished_at: datetime` | Raw and append-only, failed calls too (D1, D8). Its hash keys the cache and the replay fake. It carries its own `schema_version` (decided 14 Nov 2026). Every `datetime` in `core` is timezone-aware |
| `Settings` | `default_model: str, step_models: tuple[tuple[str, str], ...], private_mode_default: bool, send_why_notes: bool, auto_delete_days: int, data_dir: str, log_level: str` | Loaded once at start-up and passed in (I13). Spec 14.3 |

**Shapes for the stage 1 functions** (defined 14 Nov 2026 for the stage 1 plan; the owner approves them with the plan):

| Shape | Fields | Why |
| --- | --- | --- |
| `UnreadableSpans` | `hidden: tuple[Span, ...], undecodable: tuple[Span, ...]` | The Rule 9 input. `unreadable_spans(document)` builds it from every `HiddenText.span` that is not `None`, and from `Document.undecodable` |
| `LabelInput` | `position: Position, match: MatchResult, values: tuple[CheckedValue, ...], judged: tuple[JudgedLevel, ...], outside_documents: tuple[OutsideDocument, ...]` | Everything the label rules need for one position, in one bundle (I3). `values` serve number and yes/no positions, `judged` serves words positions. `outside_documents` are the documents not loaded that the label's evidence reaches (Rule 10) |
| `ValueVerdict` | `clause_id: ClauseId, level: Level, reasons: tuple[ReasonCode, ...], evidence: Evidence \| None, readable_value: str \| None` | One value after Rules 1 to 3, 5, 6 and 9, before Rule 4 combines them. `readable_value` is `None` exactly when `level` is `UNSURE`. Rule 4 compares it to find clauses that disagree |
| `ScanContext` | `label: Level \| None, allowed_numbers: tuple[Decimal, ...], acceptable_limits: tuple[Decimal, ...], known_placeholders: tuple[str, ...], defined_roles: tuple[str, ...], clause_numbers: tuple[str, ...], quote: str \| None, source_text: str \| None, instruction_given: bool` | What one output scan compares the AI text with. `label` is the code's label, or `None` for text with no label. The last four serve the style scans (14 Nov 2026): `clause_numbers` are the clause numbers given to the step, and `quote` is the confirmed quote the text rests on (`None` when there is none); a reason needs one of them as its anchor. `source_text` is the template message for `MESSAGE`, or the clause's own text for `REWRITE`; `instruction_given` is true when the user's rewrite instruction is not empty |
| `QuoteFold` | `text: str, to_original: tuple[int, ...]` | The Spec 2 quote-check fold of a text, with its index map. `to_original` has one entry per folded character plus a last entry equal to the length of the original text |
| `DrawAllowed`, `DrawRefused` | `evidence: Evidence`; `failure: DrawFailure` | The result of the last check before drawing. Two types, so a refusal cannot pass as an approval (I4) |
| `CallPrices` | `input_per_million: Decimal, cached_input_per_million: Decimal, output_per_million: Decimal` | US dollars per million tokens. The caller passes them in, so no price list enters `core` (ADR 0015) |
| `CostInputs` | `positions: int, words_positions: int, clauses: int, contract_tokens: int, prices: CallPrices` | The input of the pre-run estimate (section 7) |
| `CostRange` | `calls: int, low_usd: Decimal, high_usd: Decimal` | The estimate: the number of AI calls, and the cost if the cache hits on every call (low) or never hits (high) |
| `PlaybookProblem` | `position_id: PositionId \| None, code: PlaybookProblemCode` | One failed playbook check (Spec 4.1). `position_id` is `None` for a problem with the whole playbook |

**Errors.** `ClauseTracerError(code, context)` and its tree (section 6.4). The list in [the report's errors section](../reports/Clause%20Tracer%20pipeline%20architecture.md#errors-carry-codes-and-only-the-edge-turns-them-into-words) is the starting list. Stage 1 builds it exactly so (14 Nov 2026):

- `ClauseTracerError(Exception)` takes one argument, `context: Mapping[str, str | int] | None = None`, and keeps it as a read-only `MappingProxyType` in `self.context`. Each class has a class attribute `code: ClassVar[str]`. Context holds ids, step names and counts only, never contract text.
- Four groups, each a direct subclass of `ClauseTracerError`: `InputError`, `ModelServiceError`, `LocalError`, and `ReviewCancelled` (the cancellation group is this one class). The base and the three group classes have `code = ""`.
- Input errors, with their codes: `UnreadableFileError` `unreadable_file`, `ScannedPdfError` `scanned_pdf`, `OldWordFileError` `old_word_file`, `InputTooLargeError` `input_too_large`, `NotUtf8Error` `not_utf8`, `EmptyInputError` `empty_input` (a file or paste with no character other than spaces and line breaks, Spec 14.2; added 17 Nov 2026), `NotTextError` `not_text` (a file or paste that holds a NUL character; added 19 Nov 2026), `EncryptedPdfError` `encrypted_pdf`, `PlaybookFormatError` `playbook_format`.
- Model-service errors: `NetworkUnavailableError` `network_unavailable`, `InvalidApiKeyError` `invalid_api_key`, `NoCreditError` `no_credit`, `RateLimitedError` `rate_limited`, `NoPrivateModelError` `no_private_model`, `ModelTimeoutError` `model_timeout`, `ModelReplyInvalidError` `model_reply_invalid`. `RateLimitedError` is the one leaf with an extra argument: `retry_after_seconds: int | None = None`, the wait the AI service asked for. It is kept as `self.retry_after_seconds` and, when given, as `context["retry_after_seconds"]`. A negative value raises `ValueError` (added 14 Nov 2026).
- Local errors: `SecretStoreUnavailableError` `secret_store_unavailable`, `StorageCorruptError` `storage_corrupt`, `SchemaTooNewError` `schema_too_new`, `ConfigError` `config`, `DuplicateRecordError` `duplicate_record`.
- Cancellation: `ReviewCancelled` `review_cancelled`.

**Ports** (section 3.1). The method lists are drafted against the fakes in stage 1. Each real adapter must later pass the same contract suite ([`testing-strategy.md`](testing-strategy.md) section 3).

| Port | Methods | Notes |
| --- | --- | --- |
| `AiClient` | `complete(self, request: AiRequest) -> AiReply` | Raises model-service errors. Network retries live in the adapter; the one reask lives in the step (ADR 0005) |
| `PiiDetector` | `find(self, text: str) -> tuple[PiiSuggestion, ...]` | Behind the code finders (ADR 0008) |
| `ReviewStore` | `save_record(self, record: AiRecord) -> None`; `load_records(self, review_id: ReviewId) -> tuple[AiRecord, ...]`; `list_reviews(self) -> tuple[ReviewId, ...]`; `delete_review(self, review_id: ReviewId) -> None`; `purge_expired(self, now: datetime, auto_delete_days: int) -> tuple[ReviewId, ...]` | Hides the encrypted store ([ADR 0006](adr/0006-encrypted-storage-and-secrets.md)). Stage 1 has only these five methods (decided 14 Nov 2026). `save_record` raises `DuplicateRecordError` for a `record_id` already saved (append-only, D1). `load_records` returns records in the order saved, or `()`. `delete_review` is idempotent (I8). `purge_expired` deletes every review that is due under the auto-delete rules and returns their ids, sorted. Until stage 6 adds user state, a review's last change is the latest `finished_at` of its records. Stage 6 adds derived records by cache key and user state as new methods (D5) |
| `SecretStore` | `get_secret(self, provider_id: str) -> str \| None`; `put_secret(self, provider_id: str, secret: str) -> None`; `delete_secret(self, provider_id: str) -> None` | Each raises `SecretStoreUnavailableError` when the store cannot be reached. `get_secret` returns `None` when nothing is stored. `delete_secret` is idempotent (I8). Never plain text (ADR 0006, ADR 0015) |
| `Clock` | `now(self) -> datetime` | Returns a timezone-aware time. Auto-delete, timestamps and retry pauses stay testable (T2) |

**Fakes.** The fakes live in `clause_tracer.core.fakes`, use only the standard library, and are exported from `core`. Tests use them, and so does every module's run-alone command (decided 14 Nov 2026). They are `ReplayAiClient`, `FakePiiDetector`, `InMemoryReviewStore`, `InMemorySecretStore` and `FixedClock`. The replay fake is keyed by a hash of the exact request, raises `UnrecordedRequest` on a miss and reports `unused_keys()` ([ADR 0013](adr/0013-test-layers-and-release-gates.md), T12). The behaviour suite each fake passes lives in `tests/contracts/`, so stage 6 and later stages run the same suite against the real adapters ([`testing-strategy.md`](testing-strategy.md) section 3).

**Left to later stages.** These shapes are added to `core`, by new fields or new shapes (D5), in the stage that first needs them:

| Shape | Stage | Why then |
| --- | --- | --- |
| User state: your label, the decision, notes, ticks, tone; `Customer` | 6 | Stored apart from derived data and keyed by stable ids (section 5.1), so it is built with the store |
| Storage rows, the key table, migrations | 6 | Inside the storage adapter (ADR 0006) |
| `StepSpec`, the cache key, runner events, the cancel token behind `CancelCheck` | 6 | The runner lives in `cli` (ADR 0005). `CancelCheck` itself is a stage 1 shape |
| Explanation parts: the lead, the source line, "why it could be the other level", "What to check", Missing text, readings and the question | 8 | Their form follows the code templates and, for the two AI cases of Spec 6.1 step 10, the fenced slots built there. Every text field is a `Wording`, so each part carries its own written-by value; the readings and question of a vague value can be AI text on a label written by code |
| Keywords on `Position`, for the keyword search | 8 | Needed only by the match searches |
| The outbound message and its items | 8, then 11 | Templates in stage 8, "Rewrite with AI" in stage 11 (ADR 0011) |
| `Suggestion`; the report's contents | 11 | Built with `writing` and the report |
| AI reply schemas | 8, 9, 11 | Pydantic models in the owning module, never in `core` (ADR 0005) |
| Engine protocol requests and events; theme and text size | 12 | `cli` and the shell ([ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md)) |

**Decided for stage 1** (owner, 13 Nov 2026, [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) amendment):

- **Each step has its own input shape.** `AiRequest.inputs` holds that step's own frozen dataclass, defined in `core` beside the step's other shapes. It is never a free-form dictionary. `json_schema` is a read-only mapping, built from the step's reply schema by the module that owns the step.
- **Playbook text carries no written-by value.** Playbook names, topics and level text are always the user's own words or a starter's fixed text. `Wording` applies to review output, messages, rewrites and notes (ADR 0016, Spec 6.2).
- **`checking` is handed a cancel check.** `core` defines a small `CancelCheck` shape: a callable that returns true once the user has cancelled. The runner passes it in, and `checking` asks it between per-clause calls and raises the cancellation error (section 6.4). The per-clause calls stay inside `checking`.

**Decided for stage 1** (owner, 14 Nov 2026, [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) and [ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md) amendments). These answer the questions in the stage 1 plan, section 6:

- **Pydantic** is a runtime dependency from stage 1 (see "Check first").
- **The fakes** live in `clause_tracer.core.fakes` (see "Fakes").
- **`AiRecord` carries its own `schema_version`.** `AiRequest.inputs` is typed as the empty base class `StepInputs`.
- **`ReviewStore`** has five methods in stage 1 (see "Ports").
- **"Unlimited"** is the `CheckedValue.unlimited` field. "None" arrives as the number 0. Unlimited is walk-away when lower is better and unsure with `UNLIMITED_UNCLEAR` when higher is better (decided 14 Nov 2026, Spec 5 Rule 1).
- **"Other start point" (Rule 5).** In stage 1 the rule makes a value unsure when it already carries `OTHER_START_POINT`. How a start point is compared is not yet decided (section 15.8).
- **A fourth match result**, `MatchUnconfirmed`, holds the position and the clauses to read.
- **Rule 10.** In stage 1 the rule takes the documents not loaded that the label's evidence reaches (`LabelInput.outside_documents`). Which module builds the evidence trail is not yet decided (section 15.8).
- **The extra shapes** of stage 1 are the table "Shapes for the stage 1 functions" and the enums `TextSlot`, `ScanFinding`, `DrawFailure`, `PlaybookProblemCode`, with the reason codes above.
- **The last check before drawing.** The text half always runs, with the Spec 2 quote-check fold written in `core` (`QuoteFold`). The page-box half runs only when the document has glyphs.
- **The output scans** have one length cap per `TextSlot` (Spec 6.2). The word lists and caps are owned by the project owner: their values come from the owner's scan table, and a test checks that the code holds the same values.
- **The cost estimate** takes prices from the caller and the call count from section 7. Its range runs from "the cache hits on every call" to "the cache never hits" (Spec 9).
- **Auto-delete and a clock that jumped backwards.** A review whose last change is later than "now" is not due. Auto-delete never removes a review earlier than the rule allows (Spec 9).
- **The playbook checks** of Spec 4.1 are pure functions in `core`, built in stage 1 and shared by stage 6 and stage 12.
- **Who writes a label's words, and five style scans** (owner, 14 Nov 2026, [ADR 0011](adr/0011-who-writes-the-words.md) and [ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md) amendments). Code writes every panel sentence except the reason, readings and question of a words label the AI judged, and the readings and question of a value unsure because of vague wording (Spec 6.1 step 10), so `TextSlot` has five members. Each explanation part is a `Wording`: its `written_by` is AI only for those AI-written blocks, and CODE for everything else, including the fallback template. A label a rule made unsure stays written by code (`ToolLabel.written_by`), even when its readings are AI text. The scans gain `FIRST_PERSON`, `FILLER_PHRASE`, `EVALUATIVE_WORD`, `NO_ANCHOR` and `ADDED_SENTENCE`, built in stage 1, with their word lists in the owner's scan table (Spec 6.2). They count sentences with their own small rule, not with the stage 2 splitter, because `core` imports no other module. The exact functions are in the stage 1 plan, tasks S1-M5-T5 to S1-M5-T7.
- **Label and scan edge cases, and the rate limit** (owner, 14 Nov 2026). The behaviour is in Spec 5 (the "never guess" principle and the rules), Spec 6.2 (scans and retries) and Spec 6.3. The shapes are the reason code `UNLIMITED_UNCLEAR` and the error `RateLimitedError`, both in the lists above ([ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) and [ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md) amendments).

## 4. Data flow

### 4.1 The fixed pipeline

The order is fixed and code runs it (P3). The AI never chooses a step and has no tools (Spec 6.1).

| Stage | Spec steps | Module | AI? | Leaves the computer |
| --- | --- | --- | --- | --- |
| Read and split | 1–2 | `ingest` | No | Nothing |
| Map links | 5 | `links` | No | Nothing |
| Find personal data | 3 | `privacy` + Presidio | No | Nothing |
| Privacy check | 4 | The user | No | Nothing |
| Match, extract | 6a, 6b | `checking` | Yes | Placeholder text, position topics and types, with known names replaced |
| Quote check | 7 | `checking` (code) | No | Nothing (one retry call on a failed quote) |
| Pick labels | 8 | `core` | No | Nothing |
| Judge, explain, sort not-covered parts | 9–11 | `checking` | Yes | Placeholder text, level text (known names replaced), fixed labels |
| Rewrite (on request) | 12 | `writing`, then `checking` | Yes | One clause as placeholder text, and the instruction with known names replaced |
| Message | 13 | `outputs` | No, unless the user asks for a rewrite | Nothing by default ([ADR 0011](adr/0011-who-writes-the-words.md)) |
| Report | 14 | `outputs` | No | Nothing |

Known names are the confirmed personal items of the review and the typed party details. Code replaces them with their placeholders in position text and in rewrite instructions too, before anything is sent, and puts them back in what comes back (decided 13 Nov 2026, [ADR 0008](adr/0008-personal-data-detection-bundle.md)). The privacy canary test covers both fields ([`testing-strategy.md`](testing-strategy.md) section 8).

`links` runs before `privacy` so the privacy allow-list can reuse the defined terms ("the Contractor"). The Spec's step numbers do not change. `cli` passes `LinkMap.terms`, a `core` shape, into `privacy`.

### 4.2 The offset chain

Every position in the app points into **one canonical text**, built from the page's own characters. Nothing is found by searching a second copy.

```text
 glyphs on the page ──► canonical text ──► match key        (folded copy + index map)
        ▲                     │
        │                     ├──► sentences  4.2.s1, 4.2.s2 …  (stable ids)
   page boxes                 │
        ▲                     └──► placeholder text  (segments: copy · entity · escape)
        │                                   │
        └── exact maps back ◄── quote ◄── AI reply: sentence ids + short quote
```

**Two folds, both in `core`** (decided 17 Nov 2026). `fold_for_quote_check` is the narrow Spec 2 fold, and the only one that confirms a quote. `fold_for_matching` builds the `MatchKey`, which finds names, terms and keywords. It applies NFKC and case-folding to each character together with the combining marks after it, so `ß` becomes `ss` and a decomposed `e` with an accent matches `é`. It drops soft hyphens and zero-width and bidi characters, and from stage 5 the rest of the Default_Ignorable set too (tag characters, variation selectors, left-to-right and right-to-left marks and the like; decided 26 Nov 2026), makes curly quotes straight and every dash one hyphen, and collapses runs of spaces. `links`, `privacy` and `checking` fold their own words with the same function.

**Clauses cover the whole text** (decided 17 Nov 2026). No word of the contract falls outside a clause, because text in no clause would never be matched or sent (Spec 5, "never guess"). A numbered heading is a clause of its own and the parent of its sub-clauses. Text before the first number is a clause. A line that starts nothing belongs to the clause before it. On the sample contract this gives 65 clauses. The splitter reads, at the start of a line:
- `5.`, `5.1` to `5.1.2.3.4`;
- `(a)`, `(i)`, `(A)` and `(1)`, and also `a)` and `i)`;
- `Clause 5` and `Article IV`, with ids in Arabic numbers;
- a bare `3 Payment`, but never on a line with a tab, never with a month name, and before any numbering only a bare `1`;
- schedule headings, which start numbering again.

Markdown symbols before a number are looked past and kept in the text. A line that ends in a colon ends a sentence: a lead-in line such as `1.1 In this Agreement the following words have these meanings:` is a sentence of its own; a hard-wrapped line that ends in a colon in the middle of a sentence also breaks there, a known limit. A table row, a line with a tab between two cells, starts a sentence. A number counts only when it follows on from the numbering so far. A short unnumbered line is a heading of its own when it is the first line of the text and in title case (every word starts with a capital letter, except short joining words such as `of` and `and`), when a blank line stands before it, or when the next non-blank line starts with a marker (a number, a bracketed item, a keyword or a schedule heading), and it ends any open bracketed list. A line that opens with `Signed`, `Executed` or `In witness whereof` is a heading whatever its length. The line of a short unnumbered heading ends a sentence. The full rules are in the [stage 2 plan](plans/stage-02-ingest.md), milestone 3.

The AI answers with pointers: clause and sentence ids from a closed list, then a short quote. Code confirms the quote appears exactly once inside the cited sentences, maps it back through the segments to the real text, and from there to page boxes. The same rule runs again, by a different code path, right before a highlight is drawn. If that last check fails, nothing is drawn and the app says "Check [clause] yourself." The full reasoning is in [the seams report](../reports/Clause%20Tracer%20pipeline%20seams.md).

## 5. Data model and storage

### 5.1 Three kinds of data

| Kind | Examples | Rule |
| --- | --- | --- |
| **Raw** | Original file bytes, pasted text, typed party details, the confirmed placeholder map, the playbook snapshot, Presidio's findings, every AI request with its exact reply (failed ones too) | Append-only, never edited (D1, D8) |
| **Derived** | Canonical text, clauses, links, values, labels, explanations, the report | Rebuildable from raw; stored with `derived_by = step@version` and its cache key (D2) |
| **User state** | Checks, notes, ticks, tone, suggestions | Kept apart, keyed by stable position ids, so Re-run keeps it (Spec 6.3) |

Every stored record carries a schema version. Numbered migrations move derived data forward, after the encrypted file is copied to a numbered backup (D5, D6, D7). Ids are opaque strings made at the edge. Clause and sentence ids come from the clause number and the order, never from offsets, so they stay the same when the same file is read again: `5.1`, `7.1(a)(i)`, `S1.2` inside Schedule 1, `p3` for the third clause with no number, a `~2` ending when a number appears twice, and `5.1.s3` for a sentence (decided 17 Nov 2026).

### 5.2 Where it is stored

The design is a **hybrid** ([ADR 0006](adr/0006-encrypted-storage-and-secrets.md)). The passphrase fallback uses Argon2id or scrypt; that choice is still open (ADR 0006 action item 2).

```text
 OS password store ──► master key (32 random bytes) ──┬─► opens the encrypted SQLite file
   (or passphrase,                                    │     index, statuses, playbooks,
    Argon2id)                                         │     customers, user state, small records
                                                      │
                                                      └─► wraps one key per review
                                                              │
                                                              └─► AES-GCM blobs: contract bytes,
                                                                  placeholder map, AI replies
```

- **The encrypted file uses `sqlcipher3`** (decided 12 Nov 2026 after both candidates passed the same leak test on Linux; ADR 0006 amendment).
- **Deleting a review destroys its key.** The blobs cannot then be read, whatever the disk keeps. This matters because an app cannot overwrite a block on an SSD.
- **Blobs are bound to their place.** `review_id | record_id | schema_version` is passed as associated data, so a blob cannot be swapped for another.
- **Nothing readable is left in side files.** Temporary storage stays in memory, secure delete is on, and the write-ahead log is truncated after a delete and on close.
- **The honest claim.** "Encrypted at rest. Once its key is destroyed, a review is unreadable by this app." Not "securely erased". A backup made earlier still holds the old key, and the app says so.

### 5.3 What the password store does and does not protect

The master key and the API key sit in Windows Credential Manager or the Linux Secret Service. If Linux has no password store, the app asks for a passphrase and derives the key from it. It never writes a plain-text key.

This protects saved data from other people who use the computer and from someone who takes the disk. **It does not protect from malware running under the user's own account.** The OS stores are not built to do that, and no app-side trick closes the gap ([ADR 0014](adr/0014-protection-and-release-integrity.md)). The Help page should say this plainly.

## 6. Interfaces

### 6.1 The engine protocol

The shell and the engine exchange one JSON object per line. Every message carries `protocol_version`, so a shell and an engine that do not match fail at start-up with a clear error, not half-way through a review (I13).

| Request | Purpose |
| --- | --- |
| `hello` | Exchange protocol and app versions |
| `list_reviews`, `get_review` | Read saved reviews |
| `create_draft`, `update_draft` | Load a contract, pick a playbook and party, fix clause splits, confirm the privacy check |
| `estimate_cost` | The pre-run estimate, as a range |
| `start_review`, `resume_review`, `rerun_review` | Run the pipeline |
| `cancel` | Stop the running review; the engine answers with the cost so far |
| `set_label`, `set_note`, `mark_read` | User state |
| `rewrite_clause`, `build_message`, `build_report` | Writing and outputs |
| `delete_review`, `delete_all` | Deletion (idempotent, I8) |
| Playbook, customer and settings requests | The remaining screens |

The engine sends **events** on the same channel: `StepStarted`, `CallFinished(cost, tokens)`, `StepFinished`, `ReviewInterrupted`, `ReviewFailed(code)`. The command-line tool prints the same events to standard error.

Requests that change data are safe to repeat (I14's idempotency rule, applied to a local protocol). Errors come back as a code plus ids, never as contract text, because the user can copy error details (Spec 8.3).

### 6.2 The command line

```text
clause-tracer review --input contract.pdf --playbook freelancer.json --output report.pdf
clause-tracer resume --review <id>
clause-tracer serve --stdio
python -m clause_tracer.<module> --input samples/…        # any module alone (S1)
```

Exit codes are fixed in one place in `cli`: 0 success, 1 internal bug, 2 usage, 3 input file, 4 model service, 5 local storage or secrets, 6 interrupted and resumable (I12). Results go to standard output and errors to standard error.

### 6.3 The AI request

Every AI step uses one request shape and one frame for the prompt. The shape is deliberately **provider-neutral** (section 11).

```python
AiRequest(step, prompt_id, prompt_version,
          inputs,            # typed, structured inputs of the task
          messages,          # the prompt, rendered by the owning module
          schema_id, json_schema, model, privacy_mode, max_tokens)
AiReply(raw_body: bytes, text, model_used, provider_used, usage, generation_id)
```

The OpenRouter adapter sends `messages` with a strict JSON schema, `require_parameters`, and zero-retention routing when private mode is on. It never logs a body or a header. The module that owns the step validates the reply against its own Pydantic reply schema (D4, I16), and the exact reply bytes are saved before anything parses them (D8).

### 6.4 Errors

One base `ClauseTracerError(code, context)` in `core`, with a small tree of expected failures: input errors, model-service errors, local errors and cancellation (I5, I6). The runner maps model-service errors and cancellation to **Interrupted**, other project errors to **Failed** with their code, and anything else to Failed with code `internal` plus a local log entry. A rate limit (`RateLimitedError`) is a named case beside wrong key, no credit, no internet and no private-mode model: the review is Interrupted, and the message says the AI service is busy or the key's limit is reached and shows the wait time when there is one. Only the edge turns a code into words, using [`ux-copy.md`](ux-copy.md) (I7).

## 7. Caching, resume and cost

**The runner** is about 200 lines of plain Python in `cli`, with no orchestration framework ([ADR 0005](adr/0005-engine-runner-shapes-and-ports.md)). Each step is a `StepSpec(name, version, run)`. The runner computes a key from the step name and version, prompt hash, model, privacy mode and the hashes of the step's inputs. If the store holds a finished output for that key, it loads it. Otherwise the step runs and its output is saved under the key.

**Each AI step is split in two.** The *call* is cached as a raw reply, keyed by a hash of the exact request. The *parse* is a pure, separately versioned function of that raw reply. Three things follow from this one mechanism:

- **Resume is a cache lookup.** An interrupted step continues at the next unsent call.
- **A parser fix costs nothing.** Fixed code re-reads the saved replies with no new AI calls (D2).
- **Test fixtures come free.** Saved replies from a paid run become replay fixtures.

**Prompt caching.** Prompts put the byte-stable system text first, the contract block next, and the per-position task last, so the provider can reuse the prefix. The app reads the cached-token count on every call and warns when caching misses, because a miss raises the cost of a 50,000-word review from about $0.75 to about $5.88 on the recommended default model, by the formula below `[Assumption]`.

**Estimate.** `[Assumption]` A review of 11 positions over about 50 clauses makes roughly 30 to 35 AI calls: one forward match per position, a few reverse-match batches, a handful of pair checks, one extraction per number or yes/no position, one judge call and one explain call per words position, one more call per value that is unsure because of vague wording (for its readings and question), and the sort-not-covered calls. Code writes every other panel sentence, with no AI call (decided 14 Nov 2026, Spec 6.1 step 10). Before that decision the count was 35 to 40, with an explain call for every second position. The pre-run estimate is shown as a range and is calibrated from the `usage.cost` of real runs.

**How `core` computes the estimate** (decided 14 Nov 2026; every constant is `[Assumption]` until the first paid run). With P positions, W words positions, C clauses and T contract tokens, and `ceil` rounding up:

| Part | Calls |
| --- | --- |
| Forward match | P |
| Reverse-match batches | ceil(C / 25) |
| Pair checks | ceil(P / 4) |
| Extraction (number and yes/no positions) | P − W |
| Judge (words positions) | W |
| Explain (words positions only) | W |
| Sort not-covered parts | ceil(C / 25) |

This gives 30 calls for the starter playbook (P 11, W 1) over 50 clauses: 11 + 2 + 3 + 10 + 1 + 1 + 2. The explain row counts one call per words position, whether or not its label ends up unsure, so that row errs high. Vague values are not counted, because the pre-run estimate cannot know them: each adds one call (the Spec 14.5 sample has one, position 5, so 31 calls). The two errors partly cancel `[Assumption]`. Every call sends the contract block (T tokens), 1,000 more input tokens for the task, and gets 400 output tokens back. Prices are passed in by the caller, in US dollars per million tokens. The **low** end assumes the cache hits on every call: the contract block is priced at the cached input price. The **high** end assumes the cache never hits: the contract block is priced at the full input price. Task tokens and output tokens are priced the same at both ends. Both amounts are rounded half up to $0.0001.

## 8. Reliability and failure handling

### 8.1 Statuses

Review statuses and their moves are fixed by Spec 6.3. The runner writes the status row after each step, so a crash leaves the review Interrupted, never half-finished.

### 8.2 Calls to the AI service

| Failure | Handling |
| --- | --- |
| Network error or timeout | Retried 3 times with a pause and jitter, honouring `Retry-After`, then the review becomes Interrupted (I15) |
| Broken, empty or unknown reply | Retried once with a message saying what failed, then that value becomes unsure (Spec 6.2) |
| Quote not found, or number not in its quote | One retry, then unsure: "Couldn't confirm the wording" (Rule 3) |
| AI text fails a scan | One retry, then the slot falls back to its code template. The failed text is never shown |
| No private-mode endpoint, wrong key, no credit | Named error, review Interrupted with a plain fix |
| HTTP 429, a rate limit, after the 3 retries | `RateLimitedError`, carrying the wait in seconds from `Retry-After` when the service gave one. The review becomes Interrupted with its own message. Resume continues from the first unfinished step, and finished steps are not paid for again |

A broken or timed-out reply is **never** treated as "nothing found". The two have separate result types (I4).

### 8.3 Cancel, close and orphans

- **Cancel** is a message. The runner checks a cancel token between steps and between per-clause calls, then reports the cost so far.
- **Closing the app pauses the review.** The engine exits when its stdin reaches end-of-file, so it cannot outlive the shell. On Windows a Job Object with kill-on-close backs this up.
- **Retry records are written before the pause**, so Resume knows which calls were already paid for.

### 8.4 Hostile files

A contract is untrusted input (D4, Spec 8.4). Before parsing, code checks the member count, declared and real expanded size, the size of each XML part and the page count. The per-member compression ratio is not a check: it rejects legitimate Word files (decided 26 Nov 2026). XML is read with one hardened `lxml` parser: no entities, no network, no DTD. Relationships marked external are never followed. Each parse runs in a child process with a memory limit and a wall-clock limit, so a file built to exhaust the machine ends as `UnreadableFileError`, not a frozen app ([ADR 0007](adr/0007-document-reading-stack.md)).

## 9. Security and privacy

### 9.1 Trust boundaries

| Boundary | What crosses it | Guard |
| --- | --- | --- |
| File → engine | A contract or an imported playbook | Limits before parsing, child process, hidden-text checks, strict playbook format |
| Engine → AI provider | Placeholder text, position text | Privacy check, placeholder map, request builder tests, zero-retention routing |
| AI provider → engine | Filled-in forms | Closed schemas, Pydantic checks, quote check, output scans, code-picked labels |
| Engine → interface | Labels, quotes, AI wording | Plain text only, page pictures, no remote content |
| Engine → disk | Everything saved | Encrypted file, per-review keys, key in the OS store |
| Engine → logs | Events | Ids, codes, counts and costs only; never contract text |

### 9.2 What planted contract text can and cannot do

With code-picked labels, pointer answers, templates and output scans in place, text planted in a contract **cannot** change a number or yes/no label, show an invented number, name or phone number, tell the user to sign, or state law. It **can** still bias the reason given for a pencilled words label and an opt-in rewrite. Both sit under the real quote and carry the AI mark. This is a judgement, so the test set measures it with planted injections ([`testing-strategy.md`](testing-strategy.md) section 7).

### 9.3 Promises the app can prove, and ones it cannot

| Promise | Can a test prove it? | Wording to use |
| --- | --- | --- |
| No personal item in any request or log | Yes | Keep as written |
| No telemetry | Yes, for the engine. Not yet for the packaged shell | Keep; add a release-level network check |
| Private mode asks for zero retention | Yes: the request carries the fields | "asks for", as Spec 8.2 already says |
| Providers do not keep the contract | **No.** Nothing in the reply proves it | Keep Spec 8.2's careful wording; record the provider used per call and compare it with OpenRouter's zero-retention list |
| Saved data is unreadable without the key | Yes | Keep |
| A deleted review is gone | Partly | "unreadable once its key is destroyed", not "securely erased" |
| Safe from other software on the computer | **No** | Say what it protects from, and what it does not (section 5.3) |

Checking the provider against OpenRouter's zero-retention list is a new kind of request to OpenRouter. If the owner accepts it, Spec 8.1 must list it.

### 9.4 Copying, tampering and reverse engineering

The source is public, so nothing technical stops a copy, and hiding the shipped code would add antivirus warnings while protecting nothing. The design uses **no obfuscator** ([ADR 0014](adr/0014-protection-and-release-integrity.md)). Protection comes from elsewhere:

- **Copycats:** the licence. A registered trade mark on the name would be the stronger defence, but the owner ruled it out for now on cost (12 Nov 2026). Until then, keep dated public proof of first use of the name: signed Git tags and release dates.
- **Tampered builds:** make the real build easy to verify (section 10).
- **Secrets:** ship none. Prompts are public. The test set stays in a private repository used only by CI.

## 10. Packaging and release

| Step | Decision | Record |
| --- | --- | --- |
| Freeze the Python engine and shell | PyInstaller, one-folder build (one-file builds unpack on every start) | [ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md) |
| Windows installer | Inno Setup, scripted on GitHub's Windows runner, with the WebView2 bootstrapper | ADR 0009 |
| Linux package | A `.deb` on GitHub Releases, with WebKitGTK as a system dependency, plus a plain `tar.gz` for Fedora. A trial build confirmed it on 13 Nov 2026. One Linux build, made on Ubuntu 24.04, with one `Depends:` line (the `t64` names) | ADR 0009 |
| Personal-data model | Bundled in the installer, never downloaded on first run | [ADR 0008](adr/0008-personal-data-detection-bundle.md) |
| Signing | Unsigned at first, with published checksums. An individual certificate later | ADR 0009 |
| Integrity | Signed `SHA256SUMS`, GitHub build attestations, a reproducible Linux build | [ADR 0014](adr/0014-protection-and-release-integrity.md) |
| Updates | "Check for updates" opens the GitHub release page, only when pressed (Spec 8.1) | Spec |
| Windows testing | CI installs the build silently and drives the real window with Playwright for Python. A 90-day evaluation VM covers the manual look | ADR 0009 |

CI runs `scripts/check.sh` on Linux on every pull request. A Windows job, pinned to the `windows-2025` image, joins when the first code that touches files, paths or wheels lands, because the developer has no Windows machine to catch those problems by hand.

## 11. Room for a hosted option later

The owner may later let Clause Tracer itself be the AI provider, with optional accounts. **Version 1 does not change:** own key, no accounts, no server. The design only keeps the door open ([ADR 0015](adr/0015-provider-ready-seam.md)). `[Assumption]` Even then, contracts are handled on the user's computer by default.

| Seam | What version 1 does now |
| --- | --- |
| The AI call | One `AiClient` port. `AiRequest` carries structured inputs as well as the rendered prompt, so a hosted adapter could build prompts on a server |
| Core shapes | Nothing OpenRouter-specific in `core`. Routing flags and provider cost-field names live in the adapter; `core` carries only the neutral `cost_usd` amount (section 3.4) |
| Evidence guarantees | Quote checks, number checks and code-picked labels stay on the user's computer, whoever runs the model |
| Credentials | Stored under a provider id, so an account token could later use the same slot |
| Engine protocol | Transport-neutral requests and events; no screen logic in the engine |
| Paid features | No licence or feature gating in the app. It could be patched out, and would be a pattern to undo |
| Release channel | Signed and attested from the first release |

If a hosted option is ever added, these promises change and every copy must be updated in the same change ([WRITING_DOCS.md](../WRITING_DOCS.md) section 3): "no accounts, no sign-in, no server run by the project" and "uses your own OpenRouter key". A hosted service would also make the project a processor of users' contract text, which needs legal advice first.

## 12. Trade-offs, and what to revisit

| Choice | What it costs | Revisit when |
| --- | --- | --- |
| Hand-written runner, no framework | The project owns about 200 lines of resume and cache code | Steps stop being a fixed list |
| pywebview, not Tauri or Electron | No built-in updater, bundler or permission system; the Linux webview varies between distributions | A second developer who reviews Rust or TypeScript joins, or WebKitGTK problems pile up |
| One PDF engine through its low-level API | Harder C-style calls inside `ingest` | The bundled PDFium lacks a needed function, or reading order fails on two-column contracts |
| Hybrid storage | Two mechanisms to test instead of one | Never, unless per-review deletion is dropped |
| Medium personal-data model | Lower recall than larger models on some names | The planted-entity set shows a larger model's gain is real |
| Templates instead of AI wording | Stiffer tone in the message and explanations | Users ask for warmer text; the opt-in rewrite covers the first step |
| Four match searches instead of one | About two cents more per review `[Assumption]` | The test set shows a search adds nothing |
| No obfuscation | Shipped code is readable | Never for public code; a server is the place for anything secret |
| Unsigned Windows installer at first | A SmartScreen warning on install | Before wide promotion |

## 13. Decisions

The owner accepted ADRs 0005 to 0015 on 12 Nov 2026, ADR 0016 on 13 Nov 2026, and ADR 0017 on 17 Nov 2026.

| Decision | What was accepted | Record |
| --- | --- | --- |
| Step runner, core shapes, ports, HTTP client | Hand-written runner; frozen dataclasses; `Protocol` ports; `httpx2` with a small retry loop | [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md) |
| Storage and secrets | Hybrid encrypted store with a key per review; OS password store with a passphrase fallback | [ADR 0006](adr/0006-encrypted-storage-and-secrets.md) |
| Reading PDF and Word files; report PDF | `pypdfium2` reads PDFs at run time through its raw API only; `pikepdf` also ships, for hidden layers; hardened `lxml` for Word; NUPunkt; ReportLab | [ADR 0007](adr/0007-document-reading-stack.md) |
| Personal-data detection (Spec 13) | Presidio with a pinned config and the medium spaCy model, behind code-first finders | [ADR 0008](adr/0008-personal-data-detection-bundle.md) |
| Desktop shell, protocol, packaging (Spec 13) | pywebview; engine child process over stdio; PyInstaller one-folder; Inno Setup | [ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md) |
| Starting models and Jev (Spec 13) | Claude Sonnet 5.5 by default, two comparison models; Jev as an experiment only | [ADR 0010](adr/0010-starting-models.md) |
| Who writes the message, summaries and AI mark | Code templates by default; clause types from a closed list; one fixed line saying what was checked | [ADR 0011](adr/0011-who-writes-the-words.md) |
| Missing, unsure and failed evidence | A checkable "searched, nothing found" list; disagreeing searches become unsure; unplaceable quotes keep their label | [ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md) |
| Test layers and release gates | Five layers, a paid run on a budget, the project's own gates | [ADR 0013](adr/0013-test-layers-and-release-gates.md) |
| Protection and release integrity | No obfuscation; signed and attested releases; honest wording; trade mark deferred | [ADR 0014](adr/0014-protection-and-release-integrity.md) |
| Legal positions without a lawyer (not legal advice) | Cautious working positions: ship `pikepdf` unchanged with its licence and source; FSL enforcement by a polite message first, then a GitHub DMCA notice for a plain copy only; EU AI Act Article 50 handled as a working position, with a written-by value on each text and AI text marked in PDF metadata | [ADR 0016](adr/0016-legal-positions-without-a-lawyer.md) |
| Room for a hosted option | Keep the seams in section 11 open; change nothing users see | [ADR 0015](adr/0015-provider-ready-seam.md) |

**Still open after this work.** These were not researched well enough to recommend, or need a measurement or a lawyer:

- Final input limits and the real cost per review, from the first paid run (Spec 13). A small probe on 13 Nov 2026 supports the estimates (ADR 0010's last amendment). Other values wait for that run too: the cost estimate's constants (section 7) and the length caps of AI text, which testing tunes (Spec 6.2).
- Whether Jev beats an AI model on steps 6a and 9, and whether it can run under the same privacy rules. Version 1 isn't built on it (ADR 0010).
- Whether EU AI Act Article 50 puts a marking duty on this app. ADR 0016 (accepted 13 Nov 2026) takes a cautious working position: treat the project as a "provider", keep a written-by value on every text, mark AI text in PDF metadata, and accept the one known gap (a plain-text rewrite the user copies out can't carry a hidden mark). The provider question was sent to the EU's AI Act Service Desk on 13 Nov 2026 and has no reply yet. The docs must not say the rule does not apply.
- Real-world installer checks (13 Nov 2026, new ADR 0009 amendment). **Closed:** the real `apt`/`.deb` install on Ubuntu 22.04 and 24.04 (correct `Depends:` names for each, clean removal), the real `dnf`/tar.gz install on Fedora, and a real Windows installer (Inno Setup, silent install, run, silent uninstall, no admin rights needed). The Ubuntu window puzzle is closed: the window was slow to start, not missing, and the trial app now waits for its own start-up events (ADR 0009, 13 Nov 2026). Linux Mint 22 and 21.3 pass in containers. Ubuntu 26.04 passes too, and the trial app runs under a headless Wayland compositor on Ubuntu and Fedora (13 Nov 2026, same ADR amendment). **Still untried:** a real Ubuntu or Mint desktop session.
- Whether to register a trade mark later. How FSL would be enforced: no court has ruled on it, and the free routes do little (ADR 0014 amendment). ADR 0016 (accepted 13 Nov 2026) sets the working position: a polite message, then a GitHub DMCA notice for a plain copy only, never for a "competing use" dispute. Then stop.
- Presidio's speed on a real 60,000-character contract on an ordinary laptop.
- The running screen's first stage is labelled "Reading the pages (step 5)" (Spec 14.1 row 6), but step 5 (`links`) already ran before the privacy check (section 4.1). What that stage shows is not decided.
- How page pictures reach the window. The page policy has no `img-src data:`, pages cannot fetch files, and writing pictures to disk would break "everything saved is encrypted". Needed before build stage 12.
- How CI drives the Windows window. ADR 0009 plans Playwright over the debugging port, which release builds turn off. A separate test build or another driver is needed.
- The oldest supported Windows version. The oldest supported Linux is decided: Ubuntu 24.04 (13 Nov 2026, ADR 0009).
- The playbook file format, and which module reads it (section 15.6).
- The uninstall flow: Spec 8.3 says uninstall offers to remove all data and keys, and the flow has no design yet (settled at the shell stage; testing strategy section 1).
- The third-party licences page is not in the prototype yet ([ux-copy 4.18](ux-copy.md#418-third-party-licences-licenceshtml-not-built-yet)).
- A compact navigation for large text sizes. At 150% and 200% the sidebar stacks above the content and fills the first screen on Home, so a compact navigation is still to design (found 14 Nov 2026, [design-system](design-system.md) 3.10).
- The smaller build questions marked "Not yet decided" in section 15, for the stages after stage 1. The stage 1 label and scan edge cases were answered on 14 Nov 2026 (the stage 1 plan, section 6).

## 14. Changes this work made to earlier documents

The research found facts in the earlier architecture report that are out of date or wrong, and rules worth adding to the Constitution. Each edit, with its reason and source, is listed in [the edit record](../reports/Edits%20to%20source%20documents%202026-11-11.md).

## 15. Build stages

This section is the home of the build plan. Spec 9 sets its shape: a Python command-line tool first, then wrapped as a desktop app. The order follows [the architecture report](../reports/Clause%20Tracer%20pipeline%20architecture.md#twelve-build-stages-lead-from-skeleton-to-installer): pure parts first, then the encrypted spine, then AI steps over a fake, then real calls, then the shell. **The report's stage table is historical.** It predates ADRs 0005 to 0016, and where it differs from this section, this section wins.

The stage numbers and the module of each stage match the report's, so "build stage 12" in [ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md) and the gap table in [`testing-strategy.md`](testing-strategy.md) section 13 still point at the right stage.

The task plan of each stage is written in `docs/plans/` just before the stage is built. See [`plans/README.md`](plans/README.md).

**Every stage:**

- leaves `scripts/check.sh` passing;
- updates its module's README with the shapes it takes and returns, in the same change (S3);
- adds the tests that [`testing-strategy.md`](testing-strategy.md) asks for. The test pointers below name its sections and do not restate the tests;
- stops for the owner at each "Not yet decided" point, and before any paid run ([`testing-strategy.md`](testing-strategy.md) section 7.5).

| Stage | Module | In short |
| --- | --- | --- |
| 1 | `core` | Shapes, ports, errors, fakes, label rules, scans, the last check before drawing |
| 2 | `ingest` (text) | Text, Markdown and pasted text; clauses, sentences, match keys |
| 3 | `links` | Cross-references, defined terms, overrides, outside documents |
| 4 | `privacy` | Code finders, placeholders, the segment map |
| 5 | `ingest` (Word, PDF) | Word and PDF reading, hidden text, hostile-file limits |
| 6 | `adapters/storage`, `adapters/keyring`, `cli` | Encrypted store, secrets, the runner, the first commands |
| 7 | `adapters/presidio` | Presidio with its pinned config |
| 8 | `checking`, message templates in `outputs` | Every AI step over the replay fake |
| 9 | `adapters/openrouter` | The real AI client, the spend ledger, the first real run |
| 10 | The paid test set | Real runs on the test set; results to the owner |
| 11 | `writing`, `outputs` | Rewrites, "Rewrite with AI" for the message, the report |
| 12 | Engine protocol, shell, packaging | `serve --stdio`, the pywebview shell, installers, release checks |

### 15.1 Stage 1: `core`

- **Builds.** The ids, enums, shapes and five ports of section 3.4; the error tree (section 6.4); the fakes in `clause_tracer.core.fakes`, including the replay fake, with their behaviour suites in `tests/contracts/`; the label rules 1 to 10 as pure functions, with `MATCH_UNCONFIRMED`, the unplaceable-quote case and undecodable text under Rule 9; unit conversion (Rule 6); the playbook checks of Spec 4.1; the auto-delete date rules; the cost estimate; the output scans, with the five style scans of Spec 6.2 (decided 14 Nov 2026); the last check before drawing; a pure hash of the exact request. Tooling: Hypothesis, Pydantic (runtime, for the `TypeAdapter` check), branch-coverage measurement, and the guard that fails a change editing both code and an owner table ([`testing-strategy.md`](testing-strategy.md) sections 10 and 11).
- **Governed by.** [ADR 0004](adr/0004-code-layout.md), [ADR 0005](adr/0005-engine-runner-shapes-and-ports.md), [ADR 0012](adr/0012-missing-unsure-and-evidence-failures.md), [ADR 0013](adr/0013-test-layers-and-release-gates.md), [ADR 0015](adr/0015-provider-ready-seam.md), [ADR 0016](adr/0016-legal-positions-without-a-lawyer.md).
- **Start with** ADR 0005 action item 2 (section 3.4).
- **Done when** importing `core` loads only the standard library; the label-rule tables cover every row of the Spec 14.5 sample; no shape has a provider-specific field; `src/clause_tracer/core/README.md` records the shapes and ports (ADR 0005 action item 4); branch coverage of `core` is at least 95%; and the owner-table guard runs in `scripts/check.sh` and CI. The owner starts writing the ten test contracts now, because they take longest.
- **Tests, in the testing strategy.** Section 4 (the `core` row), section 5 (invariant 7), section 6.1, sections 10, 11 and 14.
- **Decided 13 and 14 Nov 2026:** the points at the end of section 3.4. The owner answered all 17 questions of [the stage 1 plan](plans/stage-01-core.md) on 14 Nov 2026, the label and scan edge cases under one principle (Spec 5). The same day the owner decided who writes a label's words and added the five style scans (section 3.4).
- **Decided 14 Nov 2026** (question 18 of the stage 1 plan): the first-person scan skips the message and the question to ask, where the user speaks; and a listed word that is already in the text the AI was given passes, because the scans look for words the AI added (Spec 6.2).

### 15.2 Stage 2: `ingest` for text, Markdown and pasted text

- **Builds.** Strict UTF-8 reading (`NotUtf8Error`); Markdown shown as plain characters; the size limits `[Assumption]` (Spec 9); the clause splitter with its stack of open levels and continuity check, falling back to paragraphs; sentence ids with NUPunkt, tolerant of missed breaks; match keys with index maps; the not-English warning (Spec 9).
- **Governed by.** ADR 0004, [ADR 0007](adr/0007-document-reading-stack.md) (NUPunkt), [ADR 0017](adr/0017-language-detection-with-lingua.md) (Lingua).
- **Done when** `python -m clause_tracer.ingest` reads the sample contract and prints its clauses and sentences, and the golden files match.
- **Tests, in the testing strategy.** Section 4 (the `ingest` row), section 5 (invariants 2 and 4), section 3 (golden files).
- **Decided 17 Nov 2026:** the not-English check uses Lingua ([ADR 0017](adr/0017-language-detection-with-lingua.md)). The task plan is [the stage 2 plan](plans/stage-02-ingest.md).

### 15.3 Stage 3: `links`

- **Builds.** Cross-references, including ranges and "this Clause"; defined terms and terms used but never defined; overrides with their direction; references to documents that are not loaded. Every edge carries its evidence span. Unresolved targets are kept.
- **Governed by.** ADR 0004. The run order puts `links` before `privacy` (section 4.1).
- **Done when** `LinkMap` for the sample shows the Master Agreement reference and the defined roles that `privacy` will keep.
- **Tests, in the testing strategy.** Section 4 (the `links` row).
- **Task plan.** The task plan is [the stage 3 plan](plans/stage-03-links.md).
- **Decided 20 Nov 2026** (questions 1 to 6 of [the stage 3 plan](plans/stage-03-links.md), all as recommended):
  - **Defined terms** (question 1). A term is stored without a leading "the" (`Agency`). A use is a whole word that starts with a capital letter in the contract: "the Agency's" counts, "an agency" does not.
  - **Terms used but never defined** (question 2). Runs of 2 to 4 capitalised words in the middle of a sentence that are not a defined term, a heading or a table row. Single words are not listed. Names and addresses also show up, so stage 8 decides how the list is used.
  - **Documents that are not loaded** (question 3). A capitalised name followed by Agreement, Contract, Deed, Addendum, Licence, License, Statement of Work, or Terms and Conditions. "This Agreement", the contract's own title, a term inside its own definition, headings, lower-case mentions and names in capitals are not read as one. On the sample this gives only the Master Agreement in 11.1, so Rule 10 stays on position 10.
  - **Overrides** (question 4). "Notwithstanding" before a clause reference: this clause overrides the target. "Subject to", "save as set out in" and "except as set out in" before a clause reference: the target qualifies this clause. A "prevails" sentence says who wins in the words before the verb. An override names nothing only in two narrow forms: "Notwithstanding anything in this Agreement", and "…, this Clause prevails." with nothing after the verb. Neither is given when the same sentence names a document that is not loaded. A carve-out ("Clause 8.1 does not apply to …") is a cross-reference only. A lower-case document name is not seen: a known limit.
  - **Unresolved targets** (question 5). An override whose clause does not exist is not kept, because an override with no target joins every trail. Its cross-reference is kept, with no target.
  - **References inside a schedule** (question 6). "Paragraph" points only into that schedule. Any other word points to the body clause or the schedule clause, whichever exists; when both exist, the target is left empty, never guessed.

### 15.4 Stage 4: `privacy`, code finders and placeholders

- **Builds.** The code layer that carries the promise: typed party details and their variants, checksum patterns, company-suffix and address rules; the allow-list from `LinkMap.terms`; placeholder numbering by kind (Spec 4.2); escaping; the segment map with `copy`, `entity` and `escape`; no entity across a sentence boundary; name variants sharing one placeholder; restore. Tested with the fake `PiiDetector`.
- **Governed by.** [ADR 0008](adr/0008-personal-data-detection-bundle.md), ADR 0004.
- **Done when** anonymise then restore gives the original text on the sample and on generated text, and every Spec 14.5 name and address is replaced by code alone.
- **Tests, in the testing strategy.** Section 4 (the `privacy` row), section 5 (invariant 3), section 14.
- **Task plan.** The task plan is [the stage 4 plan](plans/stage-04-privacy.md).
- **Decided 20 Nov 2026** (question 7 of [the stage 3 plan](plans/stage-03-links.md)): a defined term that the typed party details or a name finder also match is dropped from the allow-list, so a party's short name (`Brightline Studio Ltd ("Brightline")`) is always replaced.
- **Decided 21 and 22 Nov 2026** (questions 1 to 26 of [the stage 4 plan](plans/stage-04-privacy.md); the rules for the governing-law place are also in Spec 4.2):
  - **Finders** (questions 1 to 4, 15 to 17, 22 to 24, 26). A person who is not a typed party is found by an honorific, a signature phrase or a job title. A typed party is a company when its last word is on a list of 15 suffixes. An address is a street pattern or a chain built backwards from a postcode, at most 5 comma segments and 120 characters, and a longer chain keeps its last part. A one-word form counts only with a capital, and a common word needs evidence of a name. Patterns cover email, phone, keyword IDs and bank values, IBAN, and four bare identifiers (NINO, GB VAT number, UK company prefix, Luhn-checked card number, kind `BANK`).
  - **Value only** (question 5). An ID or bank span covers the value. The words "company number" stay in the text.
  - **Detector and overlaps** (questions 7 to 9, 11, 21). The detector runs once over the whole text, and its result is checked once. A span that crosses a sentence start is cut, never dropped. Overlaps resolve by source (`USER`, `PARTY_DETAILS`, `PATTERN`, `RULE`, `NER`), then length, and the lower span is cut. Only same-kind `NER` spans join. A detector match never removes a defined term from the allow-list.
  - **Governing-law place** (questions 14, 19, 20, 25). It is kept only when it is on the owner's closed list. A US state counts only as `State of X`. A `PERSON` or `COMPANY` span that touches the place stays whole, and every other kind is cut.
  - **Grouping** (questions 12, 13). A short form that fits two or more full names gets its own placeholder. Replacing known names in position text and in rewrite instructions is stage 8 work.
  - **Escape and restore** (questions 6, 10). The token form is `⟦Person 1⟧`. Each `⟦` and `⟧` of the contract is its own `escape` segment and is sent as `[` and `]`. Restore has three jobs: the whole text, the tokens of an AI reply, and a span of the sent text.
  - **Doubts** (decided 21 Nov 2026). Stage 4 produces none. Stage 6 and stage 12 build the code that fills the doubt list.

### 15.5 Stage 5: `ingest` for Word and PDF

- **Builds.** Word: the zip read directly, every part through one hardened `lxml` parser, size caps before reading, external relationships never followed, list numbers rebuilt, hidden runs, comments, and tracked changes read as accepted, each one listed with its earlier and new wording and author; `.doc` detected by its bytes. PDF: `pypdfium2` alone through its raw API, with the canonical text built from glyphs, furniture, scanned pages, the undecodable count and its 1-in-20 page warning `[Assumption]`, the hidden-text checks, hidden layers through `pikepdf`, and one coordinate function. Then the Unicode checks. Hostile-file limits, with parsing in a child process with time and memory limits (section 8.4).
- **Governed by.** ADR 0007 and its amendments, ADR 0012 and its amendment, [ADR 0001](adr/0001-show-contracts-as-original-pdf-pages.md).
- **Changed from the report.** No cross-check between two PDF libraries at run time: `pdfplumber` is a test-only dependency (ADR 0007).
- **Done when** the generated test PDFs and Word files give their known glyph positions and findings, every hostile fixture ends as a named input error inside its limits, and the highlight pictures match.
- **Tests, in the testing strategy.** Section 4 (the `ingest` row), section 5 (invariants 1 and 6), section 8 (hostile files, hidden text and Unicode tricks). The Windows CI job joins at this stage or stage 6 (section 13 there, and section 10 here).
- **Decided 23 Nov 2026** (questions 1 to 5 of [the stage 5 plan](plans/stage-05-ingest-word-pdf.md); the evidence is in [the stage 5 reader design choices report](../reports/Stage%205%20reader%20design%20choices.md)):
  - **The child process** (question 1). `cli` owns it, so `ingest` stays pure. Stage 5 adds one `cli` module and no other `cli` behaviour. The child starts with `subprocess.Popen`, a list of arguments and no shell: `python -I -m` from an installed environment, or the app's own executable with a flag when frozen. It never uses a process pool or `fork`. The file goes in on standard input. The reply is bounded JSON that `core` checks with a `TypeAdapter`, and it is never unpickled. The child sets its own memory limit as its first action and fails closed if it cannot (`RLIMIT_AS` on Linux; a job object it assigns to itself on Windows). The parent keeps the wall clock and kills the child. The Linux limit counts address space and the Windows limit counts committed memory, so the same figure differs by system. Neither is a security sandbox.
  - **Rendering** (question 2). `ingest` renders each page itself with `pypdfium2`, in the same child, in greyscale at a fixed scale. No port is added, and no Pillow or numpy runs at run time. The contrast check is a pure function over bytes, width, height and stride. The pixels per page are capped, and a page over the cap gives a warning.
  - **Hidden text** (question 3). `privacy` replaces names inside hidden text too. `links` keeps every edge in stage 5. Stage 8 decides what to do with an edge whose evidence lies on hidden text, and whether Rule 9 reaches it. Stage 8 must never send hidden-layer text that has no span.
  - **Word list numbers** (question 4). The rebuilt number goes into `Document.text` at the start of its paragraph, followed by one space. For Word, `Document.text` is the text as Word draws it. A format that cannot be rebuilt gives no number and the warning `word_numbering_unknown`. The splitter does not read `1)`, `A.`, `I.` and `01.`: a known limit.
  - **Word comments and notes** (question 5, in part). A comment is a `HiddenText` with `COMMENT` on the commented words, and its own text is not in `Document.text`. A note is reached through its reference by `w:id`, separator notes are skipped by type, and note text is not appended after the body. Header and footer text is not placed in `Document.text`. An alternate-content branch is read once.
- **Decided 23 Nov 2026** (question 5, the place of side text): the text of a Word comment and the text of a Word header or footer live in one new `Document` field, outside `Document.text`. The splitter, `links` and `privacy` never read it. This is a `core` change: a new field, a new `schema_version` and a row in section 3.4, written in a `core` task of the stage 5 plan (D5, D6).
- **Decided 23 Nov 2026** (question 5, footnotes and endnotes): their text goes into the same new `Document` field, outside `Document.text`, so the splitter never reads it and no false clause can appear. The reader raises a warning that gives the number of notes, and the contract check lists them. A term set only in a note is therefore not checked. The owner asked to look at this again when the app is tested with real contracts.
- **Not yet decided** (question 5, the rest): which new `HiddenReason` members stage 5 adds; the exact name, type and content of the new field; and the name of the warning code for notes.
- **Decided 26 Nov 2026** (questions 6 to 21 of [the stage 5 plan](plans/stage-05-ingest-word-pdf.md); the evidence is in [the stage 5 reader checks and limits report](../reports/Stage%205%20reader%20checks%20and%20limits.md)):
  - **Unicode checks** (question 6). The reader flags tag characters, bidi controls and a zero-width character that is not a byte-order mark at the start. It adds `TAG_CHARACTER` to `HiddenReason`. The wide fold drops the rest of the Default_Ignorable set too (tag characters, variation selectors, left-to-right and right-to-left marks and the like), so an invisible character cannot hide a keyword. That changes `core` and needs new cases in `match_fold.toml`, written by the owner. Confusables and the line-end hyphen join wait for stage 8.
  - **CI and tools** (questions 7 to 9). The Windows job joins in stage 5, at the milestone that builds the child process. It runs every test except the highlight pictures, uses `shell: bash`, and the repo gets a `.gitattributes` that marks the sample PDF as binary. The nightly job runs Hypothesis with a `nightly` profile that `conftest.py` registers. Atheris is optional, Linux x86_64 only, and its gap is recorded. ReportLab (with `invariant=1`) and `pikepdf` write the fixtures, a page is rotated with `pikepdf`, and Pillow is a direct dev dependency.
  - **Hidden-text thresholds** (question 10). Font size is the drawn size, with the matrix scale. Render mode comes from the page object. Each threshold is an `[Assumption]` constant. The contrast limit is open: it is set in the task, after the fixtures. Fixtures lie far from each limit.
  - **Hostile-file limits** (question 11). The reader stops at 50,000 words. A soft per-page budget in the child works inside the 60-second kill, which stays as the backstop. The per-member compression ratio is dropped, because it rejects legitimate Word files. Members are counted from the end record. A part of the XML is capped, and the lxml error is mapped to `UnreadableFileError`. A page count is a pre-check. The exact caps are `[Assumption]` values of the tasks.
  - **Scanned pages** (question 12). A page is scanned when it has fewer than 50 readable characters and holds an image. A character drawn in invisible render mode is not readable, so a scan with an invisible text layer counts as scanned and is not read (Spec 9, Spec 12). The image walk goes into form objects. A signature page with a scanned signature can be named scanned.
  - **Furniture and reading order** (questions 13 and 15). A repeated line is found by its text with each run of digits replaced, in the top or bottom 8% of the page, on at least half of the pages and on at least 3. A line is split at a wide gap. Tags are not read in stage 5. The reading order is PDFium's, with lines built from character baselines. Row-wise, reversed and rotated pages are known limits that fixtures record.
  - **Glyphs, encrypted PDFs and boxes** (questions 14, 18 and 20). The text is built for each character from `GetUnicode`. A character that PDFium generates has no glyph index in `char_map`. The Unicode-error flag is not trusted alone. A PDF that needs a password raises `EncryptedPdfError`, taken from the error code of the failed open. A PDF with an owner password only is read as normal. A box is converted from the page bounding box, not the crop box, with the rotation. No `core` shape changes.
  - **The sample PDF** (question 19). A committed script builds it with ReportLab, with an embedded Vera font and `invariant=1`. A test compares words, not bytes.
  - **Word changes and hidden text** (questions 16, 17 and 21). A tracked change is read as accepted, from the current properties only, and everything inside a deletion or a move-from is dropped. A deleted paragraph mark joins the two paragraphs with no separator, as Word shows them. A move is shown as one deletion and one insertion. A formatting change is not listed. Text is flagged when it is hidden after the style cascade, smaller than 2 points, or the same colour as its fill. Automatic colour, web-hidden text, a hidden paragraph mark and a run of white space are never flagged. Every OLE2 file, an old `.doc` and an encrypted `.docx` alike, gets one neutral message in version 1.
- **Decided 26 Nov 2026** (the open points of questions 5, 6, 10, 18 and 21; the owner approved the words of the three file messages the same day, and they are in Spec 9, ux-copy 4.3 and the prototype):
  - **Invisible marks** (question 6). A left-to-right or right-to-left mark or a variation selector is flagged as hidden text only when it sits between two letters, where it can hide a keyword. The wide fold ignores them everywhere.
  - **Look-alike letters** (question 6). A word that mixes two alphabets is not flagged in stage 5. The check is stage 8 work and is listed in 15.8 so it is not forgotten.
  - **Contrast** (question 10). Mistakes fall on the side of more false alarms. The limit of 24 is the start and stays an `[Assumption]` that the task tunes on the fixtures.
  - **Word colours** (question 21). The rule is simple: pure white on a white page, and text with exactly the colour of its own shading. Near-white, theme colours and table-style fills are known limits. Text of 2 to 8 points is never flagged.
  - **Parts that never show** (question 5). Besides `TAG_CHARACTER`, one new `HiddenReason` marks a Word part that never shows: a header or footer that no section uses or that can never appear, an unreferenced note, and an alternate-content branch that differs from the one read.
  - **A PDF that forbids copying** (question 18). It is read, with a notice.
- **Decided 27 Nov 2026** (two points of the stage 5 plan):
  - **The count of notes.** The warning for Word notes carries no count. The count is the number of footnote and endnote entries in the side text, referenced or not, and the warning is raised even when no note is referenced.
  - **Imported content.** A Word file with a `w:altChunk` that Word would show is not read: it raises `UnreadableFileError` with the reason `word_alt_chunk`. One inside deleted content or an unread alternate branch raises nothing. The words the user sees are open.
- **Not yet decided** (stage 5, the rest): the exact name, type and content of the new `Document` field; the names of the new warning codes and the new `HiddenReason`; the exact caps of question 11.

### 15.6 Stage 6: the encrypted store, secrets, the runner and the first commands

- **Builds.**
  - **Store:** `sqlcipher3` with a key per review, associated data, the pragmas, numbered migrations with a backup first, and raw, derived and user-state records. Every stored wording keeps its written-by value (ADR 0016).
  - **Secrets:** `keyring` with its backend pinned per system, a passphrase fallback, and credentials under a provider id (ADR 0015).
  - **Auto-delete:** runs at start-up and while the engine runs. "Delete all reviews" also clears temporary files and logs (Spec 8.3).
  - **Runner:** the hand-written runner in `cli`, with `StepSpec`, cache keys, the call and parse split, statuses, cancel and events.
  - **Commands:** settings loaded once, exit codes, logs that carry no contract text, and the `review` and `resume` commands (section 6.2).
  - **Playbooks:** reading the starter playbook and playbook files with a strict format and size limits, checked with the playbook checks that stage 1 builds in `core`, and exporting without the customer link or "why this matters" notes (Spec 4.1, 8.4).
  - **Store methods:** derived records by cache key and user state, added to `ReviewStore` as new methods (D5). A review's real last change then replaces the stage 1 stand-in (section 3.4, "Ports").
- **Governed by.** [ADR 0006](adr/0006-encrypted-storage-and-secrets.md) and its amendments, ADR 0005, ADR 0015, ADR 0016.
- **Changed from the report.** The storage choice is made: `sqlcipher3` in a hybrid design, not "after the A/B decision".
- **Done when** a review of the sample runs through the steps built so far, is saved encrypted, can be interrupted and resumed with no step run twice, and is deleted on schedule by a fixed clock.
- **Tests, in the testing strategy.** Section 4 (the `adapters` and `cli` rows), section 3 (the contract suite against each fake and real adapter), section 8 (encryption at rest, deleting a review, auto-delete, storage settings, leaks in logs).
- **Not yet decided:**
  - **Several reviews open at once.** The prototype's window tabs assume it (Spec 13). Say whether one engine runs one review or several, and what the runner, the store and the cancel token do when two reviews run.
  - **The playbook file format**, and which module reads it. Spec 8.4 asks only for a strict format with size limits, and ADR 0004 names no module for it.
  - **How the command-line tool does the privacy check.** Spec 6.1 step 4 needs the user to confirm before anything is sent, and the `review` command in section 6.2 has no step for it. Settle this before stage 9 sends anything.
  - **Argon2id or scrypt** for the passphrase, if the pinned `cryptography` lacks Argon2id (ADR 0006 action item 2).
  - **How a stored `AiRecord` is read back with its step's own input shape.** `AiRequest.inputs` is typed as the base class `StepInputs`, and Pydantic may not rebuild the subclass. The stage 1 `TypeAdapter` check records what happens.

### 15.7 Stage 7: the Presidio adapter

- **Builds.** Presidio with the adapter's own pinned config, `en_core_web_md` with ORGANIZATION on, loaded only in the step that needs it; a test of the loaded engine, model and recognisers; the planted-entity set.
- **Governed by.** ADR 0008.
- **The adapter contract** (decided 21 Nov 2026, [stage 4 plan](plans/stage-04-privacy.md) questions 7 and 8). `PiiDetector.find` gets the whole text in one call, and its offsets are code points of exactly that text. The adapter does any chunking and offset mapping itself: windows overlap and break at white space, duplicates are removed, and nothing is silently truncated. If the adapter cannot cover the text, it raises and returns nothing. It returns spans only, never copied text. A detector error stops the run, and `privacy` does not catch it. The docstring of `PiiDetector` in `core/ports.py` says "Raises: None", which conflicts with failing closed. Stage 7 changes it in a `core` task.
- **Changed from the report.** The bundle is decided: no recall race between bundling options. The medium model is measured on the planted-entity set, and a larger model or GLiNER comes in only under ADR 0008's switch rule.
- **Done when** Presidio plus the code finders catch every planted name, company and address, and its speed on a 60,000-character contract is measured (section 13).
- **Tests, in the testing strategy.** Section 1 (planted entities), section 4 (the `adapters` row).

### 15.8 Stage 8: `checking` and the message templates

- **Builds.** The quote check and number parser (pure). The parser turns "none" into the number 0 and sets `CheckedValue.unlimited` for "unlimited" (Rule 1). Then, over the replay fake: extraction with sentence-id forms; matching with the four searches, the pair check and `MATCH_UNCONFIRMED`; the "searched, nothing found" list; judging words positions; clause types from the closed list for not-covered clauses.
  - **A label's words** (decided 14 Nov 2026, Spec 6.1 step 10). Code templates, filled with checked values, write every panel sentence: the lead, the source line, "why it could be the other level", "What to check", the question to ask and Missing text. The AI writes, in fenced slots, in exactly two cases: the reason, two readings and question of a words label the AI judged; and the two readings and question of a value of any type that is unsure with `VAGUE_WORDING` (code still writes its lead). Every other unsure reason and every Missing label gets code words only. AI text passes the `core` scans (Spec 6.2); after one failed regeneration the code template is used, which for a vague value means no readings and a template question. Every piece of AI wording is stored as written by AI and shown with the fixed AI line; the label stays written by code when a rule made it unsure.
  - **Prompt rules.** The prompts carry the six signs of [ux-copy 1.1](ux-copy.md#11-signs-of-machine-made-text) ("Text the AI writes") as rules, and four good sample lines as examples. They carry no bad examples. Prompts are versioned files, never edited once released.
  - **Placeholders in prompts** (decided 21 Nov 2026, from a paid check on real Claude models). Every prompt that holds placeholder text also carries this rule: "Placeholders such as ⟦Person 1⟧ stand for hidden names. Write each placeholder exactly as it appears in the text, never change, translate or invent one." In the check, no reply changed a placeholder when the rule was given (0 of 152 replies), and 28 of the replies without it did. The reply scan of stage 1 still treats an unknown placeholder as a broken reply.
  - **Known names in free text.** The replacement of known names in position text and in rewrite instructions (Spec 4.2, ADR 0008) calls one function that `privacy` exports and `cli` passes in, because `checking` cannot import `privacy`. The function may live in `core` instead. Two copies of the matcher would drift and leak. One-word forms match here without regard to case, since the user types this text by hand. Restored text is never sent again without a fresh replacement pass.
  - **The message.** The code-built message from templates in `outputs`, moved here from stage 11 because it needs no AI.
  - **From stage 5: look-alike letters** (decided 26 Nov 2026, do not forget). Stage 5 does not flag a word that mixes two alphabets, such as a Cyrillic letter inside a Latin word. Stage 8 first uses the wide match key, so it adds the check there: the Unicode confusables data (a licence decision of the owner: Unicode License v3 is not MIT, BSD or Apache), a pinned Unicode version, new cases in `match_fold.toml`, and tests that `0` and `O`, and `l` and `1`, do not fold. A check with the standard library alone flags harmless Greek letters such as `μm`. See [the stage 5 reader checks and limits report](../reports/Stage%205%20reader%20checks%20and%20limits.md), question 6.
- **Governed by.** [ADR 0011](adr/0011-who-writes-the-words.md), ADR 0012, ADR 0005, ADR 0013, ADR 0016.
- **Changed from the report.** Not-covered clauses get a clause type, not an AI summary (ADR 0011).
- **Done when** the end-to-end replay test on the sample gives the Spec 14.5 labels.
- **Tests, in the testing strategy.** Section 4 (the `checking` and `outputs` rows), sections 6.2 and 6.3, section 3 (end-to-end replay).
- **Not yet decided** (from the stage 1 answers, 14 Nov 2026):
  - **How a start point is compared** for Rule 5 ("30 days after acceptance" against "from invoice date"). Stage 1 only acts on an `OTHER_START_POINT` reason already on the value.
  - **Which module builds a label's evidence trail** (cross-references, defined terms, overrides), and so fills `LabelInput.outside_documents` for Rule 10.
  - **Whether the quote check reuses `core`'s quote-check fold.** Section 4.2 asks the last check before drawing to be a different code path; sharing the fold would share one part of it.
- **Decided 20 Nov 2026** (question 8 of [the stage 3 plan](plans/stage-03-links.md)): an override that names a label's subject ("the payment terms prevail", Spec 4.5) is matched to labels here, in stage 8, which knows each position's topic. `links` reads only clause references, "this Agreement" and "this Clause".

### 15.9 Stage 9: the OpenRouter adapter and the first real run

- **Builds.**
  - **Requests:** the request builder with a strict `response_format` schema, `require_parameters`, and zero-retention routing in private mode. It never sends `temperature`, and Response Healing stays off.
  - **Calls:** `httpx2` with timeouts and three tries with jitter and `Retry-After`, and no body or header ever logged.
  - **Other calls:** the cached-token count on every call, with a warning when caching misses; the key check, credit balance and model list (Spec 8.1).
  - **Spend ledger:** a cap per run and a $10 total, built and tested with the replay client before any key is used.
- **Governed by.** ADR 0005 and its amendment, ADR 0010 and its amendments, ADR 0013 and its amendment, ADR 0015.
- **Changed from the report.** No local stub server. The adapter is tested against saved bodies through `httpx2.MockTransport`, not `respx` (ADR 0005 and ADR 0013 amendments).
- **Done when** the contract suite passes on saved bodies, and the first real run on the sample contract is made on the cheap model, only after the owner says go ([`testing-strategy.md`](testing-strategy.md) section 7.5, step 1).
- **Tests, in the testing strategy.** Section 6.4, section 8 (private mode, leaks in requests).
- **Not yet decided:** whether the app checks the provider used against OpenRouter's zero-retention list. It is a new kind of request, so Spec 8.1 must list it if the owner accepts it (section 9.3, ADR 0010 action item 3).

### 15.10 Stage 10: the paid test set

- **Builds.** The ten contracts and answer keys in a private repository; injected variants; built absence cases; the planted-entity set; the paid runner with the `paid` marker and a report script; the hard gates and reported rates.
- **Governed by.** ADR 0013 and its amendments, ADR 0010, [ADR 0014](adr/0014-protection-and-release-integrity.md).
- **Changed from the report.** The budget sets the model plan: paid testing runs on Claude Haiku 5.5, and the default Sonnet-class model gets one pass of the ten contracts at most ([`testing-strategy.md`](testing-strategy.md) section 7.5). Comparisons run only where the budget allows.
- **Done when** a first baseline is recorded and the results are brought to the owner: real cost per review, input limits (Spec 13), the unsure share, the undecodable-character level, clause-type accuracy and the disagreement rate.
- **Tests, in the testing strategy.** Section 7.
- **Check in this stage** (owner, 16 Nov 2026). The law-word scan flags "legal" in "legal fees" or "legal costs", so a sound reason that quotes such a clause falls back to the code's template. Nothing wrong reaches the user, but good AI text is lost. Count how often this happens in the paid runs, then decide: keep it, let a law word pass when it is in the quote, or change the list. Do not drop "legal" without a replacement, or "this is legal" gets through.

### 15.11 Stage 11: `writing` and the rest of `outputs`

- **Builds.**
  - **Rewrite:** `writing.rewrite_clause` with the `{old, new}` edit form, applied by code. Known names are replaced in the clause and in the instruction, and Presidio checks the new text (Spec 4.6). `cli` then passes it to `checking`, which re-checks every affected position (ADR 0004). One suggestion per clause.
  - **Message:** the optional "Rewrite with AI", shown before and after, with every quote, number and name re-checked (ADR 0011 and its amendment). Code fills in names.
  - **Report:** the PDF built with ReportLab, all text plain. When it contains AI wording, it carries the fixed AI line on those pages and the written-by mark in its metadata, using the IPTC "digital source type" terms (ADR 0016).
- **Governed by.** ADR 0004, ADR 0011, ADR 0007 (ReportLab), ADR 0016.
- **Done when** a rewrite of a sample clause is re-checked against every position it affects, and a report with AI wording carries the metadata mark.
- **Tests, in the testing strategy.** Section 4 (the `writing` and `outputs` rows). ADR 0016 action item 3 asks for a test of the written-by value and of the metadata mark.

### 15.12 Stage 12: the engine protocol, the shell and packaging

- **Do not forget (from stage 5).** The words for a refused Word file with imported content (reason `word_alt_chunk`) are open (Spec 13). Ask the owner before the screen is built.
- **Builds.**
  - **Engine protocol:** `serve --stdio` with `protocol_version` and every request and event of section 6.1.
  - **Shell:** the pywebview shell, in its own top-level folder, reusing the prototype pages. It also adds the screens the command line lacks, such as import preview, error details and the update check.
  - **Packaging:** PyInstaller one-folder, the Inno Setup installer, the `.deb` and the `tar.gz`.
  - **Licences:** the third-party licences page, a build test that `pikepdf` and PyGObject ship unchanged, and the `pikepdf` source archive on each release.
  - **Release chain:** signed `SHA256SUMS`, build attestations, an SBOM and a reproducible Linux build.
- **Shell rules from the trial builds** (ADR 0009, amendments of 12 and 13 Nov 2026):
  - Load pages from a `file://` address, never a bare path, with the built-in server off and `ALLOW_FILE_URLS` off. Load them from `_internal/`.
  - Refuse any navigation away from the app's own files, with a test (Spec 8.4).
  - Use the page policy `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'`. Pages get all data through the Python bridge.
  - Python saves theme and text size.
  - Before the first pywebview call, wait for the window's `shown` and `loaded` events with the app's own longer timeout.
  - Keep the whole GTK stack out of the bundle, and undo PyInstaller's environment in the app's first lines.
  - Turn off developer tools and the debugging port in release builds.
  - Pin the Windows runner to `windows-2025`. The installer asks for no admin rights.
  - Build the `.deb` on Ubuntu 24.04, with the one `Depends:` line (the `t64` names). Ubuntu 22.04 and Mint 21 are not supported (13 Nov 2026).
- **Governed by.** ADR 0009 and its amendments, ADR 0014, ADR 0016, ADR 0004.
- **Done when** a full review runs from the installer on Linux and Windows (Spec 11). The release checks run as well: the app with and without a session bus, under Wayland and under X11, and the package installed on Ubuntu 24.04 and on the newest Ubuntu.
- **Before the first public release:** the steps in Spec 10, including the reply from the AI Act Service Desk.
- **Tests, in the testing strategy.** Section 9, section 8 (the app window, no telemetry, dependencies), section 12 (before a release).
- **Playbook editor:** uses the playbook checks of `core` (stage 1) for its validation errors (Spec 4.1).
- **Not yet decided:** which reviews count as "affected" when the auto-delete setting is lowered (Spec 9 shows their count before the user confirms). Stage 1 builds only the date rules.
- **Decided 13 Nov 2026:** version 1 supports Ubuntu 24.04 and later, Linux Mint 22 and later, Debian 13, and Fedora through the plain archive. There is one Linux build ([ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md) amendment). The oldest supported Windows version is still open.
