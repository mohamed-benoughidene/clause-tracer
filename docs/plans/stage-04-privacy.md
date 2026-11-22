# Stage 4 plan: `privacy`

| | |
| --- | --- |
| Stage | 4, `privacy` |
| Status | In progress |
| Branch | One branch for each milestone, cut from `main`: `feat/privacy-m1-foundations`, `feat/privacy-m2-code-finders`, `feat/privacy-m3-resolve-and-group`, `feat/privacy-m4-placeholder-text`, `feat/privacy-m5-public-calls-and-sample`, and `docs/close-stage-4-privacy` for the close of the stage. See [the README](README.md), "Branches and pull requests" |
| Accepted on | 22 Nov 2026 |
| Stage outline | [System design section 15.4](../system-design.md#154-stage-4-privacy-code-finders-and-placeholders) |

## 1. Goal

`privacy` reads a `Document`, its clauses, the typed party details and the defined terms. It finds personal data with code finders and with the `PiiDetector` port, resolves overlaps, groups name variants under one placeholder, numbers placeholders by kind, and builds the `PlaceholderText` with its segment map. Restore undoes it. `python -m clause_tracer.privacy` prints the entities and the placeholder text of the sample contract, with an empty detector, and every Spec 14.5 name and address is replaced by code alone.

## 2. Scope

**Where the code starts.** `src/clause_tracer/privacy/` is a skeleton: `__init__.py` (an empty `__all__`), `__main__.py` (prints "not built yet"), a README with "planned" shapes, `tests/__init__.py`, `tests/test_smoke.py` (calls `main()` with no arguments and expects 0) and no `samples/` folder. `core` already holds every shape this stage uses, exactly as in [system design 3.4](../system-design.md#34-core-shapes-for-stage-1): `Party`, `PiiSuggestion`, `PlaceholderEntity`, `Segment` and `PlaceholderText` in [`core/placeholders.py`](../../src/clause_tracer/core/placeholders.py); `PlaceholderKind`, `PiiSource`, `SegmentKind`, `PLACEHOLDER_OPEN` and `PLACEHOLDER_CLOSE` in [`core/enums.py`](../../src/clause_tracer/core/enums.py); `DefinedTerm`; `Clause` and `Sentence`; the `PiiDetector` port and `FakePiiDetector`; and `fold_for_matching` with `MatchKey` ([`core/match_fold.py`](../../src/clause_tracer/core/match_fold.py)). `core` also holds the owner-table loader ([`core/tests/owner_tables.py`](../../src/clause_tracer/core/tests/owner_tables.py)) and the hazard alphabet ([`core/tests/strategies.py`](../../src/clause_tracer/core/tests/strategies.py)). The root `conftest.py` holds the `check_golden` fixture and the `--update-goldens` option. `scripts/check.sh` has coverage floors for `core`, `ingest` and `links` only.

**The import wall.** `privacy` may import only `core`, and the contract covers its tests and its `__main__` too ([`pyproject.toml`](../../pyproject.toml), "pipeline modules are independent"). So `privacy` can never call `split_clauses` or `map_links`. The sample reaches `privacy` as a committed fixture (S4-M1-T4), which a test in the root `tests/` folder rebuilds from `ingest` and `links` and compares. The root `tests/` folder is outside the package, so it may import all three modules. `privacy` does not copy `links` internals: it has its own small span helpers (S4-M1-T6). **Hidden text.** `privacy` reads all of `Document.text`, so a name inside text that stage 5 flags as hidden is replaced too, as every other copy of the name is.

### Builds

- The fixture of the sample: `PrivacyInput` (document, clauses, parties, defined terms), its writer and its loader, a committed sample fixture, and a drift test against `ingest` and `links` (S4-M1-T3, T4).
- Code finders, each returning `PiiSuggestion`s: typed party details and their variants, including a party's short name taken from a defined term (S4-M2-T4); email, phone (international, national, bracketed and 11 unseparated digits), ID by keyword and bank by keyword (the value only, not the keyword), and IBAN with the mod-97 check (S4-M2-T2, T3); four bare identifiers with no keyword: a UK National Insurance number, a GB VAT number with its checksum, a UK company number with a prefix, and a card number with the Luhn check (S4-M2-T12); company names by suffix (S4-M2-T5); addresses, built from the street or backwards from a postcode (S4-M2-T6); person names by honorific, signature and job title, with their variants, and a guard for common-word names (layer 3, S4-M1-T6) (S4-M2-T7).
- The owner's closed list of governing-law places (S4-M2-T11, an owner task).
- The resolve step: validation of every offset (D4: a bad, reversed or non-integer span raises), the allow-list from `LinkMap.terms` with the question 11 drop rule and the Mercury rule, the cut at the governing-law place that Spec 4.2 keeps (a closed list; a person or company span that touches the place stays whole), overlap resolution by source with the `NER` union and a rank for ties, and splitting at sentence boundaries (S4-M3-T1 to T6).
- Grouping name variants into `PlaceholderEntity`s numbered by kind in order of first appearance (S4-M3-T7).
- The placeholder text: tokens, escaping, the segment map, `anonymise`, and the three restore calls (S4-M4).
- `python -m clause_tracer.privacy` with `--input`, a golden file of its output, and an end-to-end test from the sample text through `ingest` and `links` to `privacy` (S4-M5).
- Owner tables (Constitution T11) for the finders, the party details, the resolve pipeline, the grouping and the sample.
- Property tests of invariant 3 (testing strategy section 5), eleven properties of the resolve step and of the composed pipeline (S4-M3-T11), and an 85% branch-coverage floor for `privacy`.

### Leaves to later stages

- The Presidio adapter, its pinned config, the Faker planted-entity set and its scoring: stage 7 ([system design 15.7](../system-design.md#157-stage-7-the-presidio-adapter)). This stage tests with `FakePiiDetector`.
- Replacing known names in position text and in rewrite instructions (ADR 0008, amendment of 13 Nov 2026): stage 8, which builds the position text. Stage 8 reads `PlaceholderEntity.spans` and `Document.text` to get each name, and calls `restore_reply` on what comes back.
- The user's controls: select text to replace, untick a false alarm, split or merge variants ("Same person", "Different person"). Stage 12 builds the screen. `anonymise` takes entities, so a later stage passes user-built entities without a change here.
- Passing `LinkMap.terms` from `cli` into `privacy`, storing the entities as a derived record with a cache key, and the "Send for review" lock: stage 6.
- Checking, before any request, that no known name is left in what is sent (the privacy canary test over request bodies): stage 6 and stage 9 (testing strategy section 8).
- Person names that no rule or typed detail names. Only the detector finds them, from stage 7 on.
- National ID numbers other than the UK National Insurance number, and non-UK bank formats: stage 7 (question 15). The NINO, Luhn-checked card numbers, bare GB VAT numbers and UK company prefixes are built in this stage (S4-M2-T12; the owner's answer to question 24).
- The doubt list (the codes that mark an unsure suggestion): not stage 4. The shape exists in `core` (S1-M6-T8); the code that fills it is built where the user first sees suggestions (stage 6 and stage 12). Stage 4 produces no doubts.

## 3. Read first

- [AGENTS.md](../../AGENTS.md), the [Constitution](../../Constitution.md), [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md), and [WRITING_DOCS.md](../../WRITING_DOCS.md) sections 2, 5 and 9.
- [System design](../system-design.md): [3.4](../system-design.md#34-core-shapes-for-stage-1) (the `Party`, `PiiSuggestion`, `PlaceholderEntity`, `Segment`, `PlaceholderText`, `DefinedTerm`, `Clause` and `Sentence` rows, the `PiiDetector` port and the fakes), [4.1](../system-design.md#41-the-fixed-pipeline) (known names, and `links` before `privacy`), [4.2](../system-design.md#42-the-offset-chain) (the two folds), [15.4](../system-design.md#154-stage-4-privacy-code-finders-and-placeholders). Skim 15.7 and 15.8 to see what later stages take from `privacy`.
- [Testing strategy](../testing-strategy.md): sections [3](../testing-strategy.md#3-five-layers) (golden files), [4](../testing-strategy.md#4-what-to-test-in-each-module) (the `privacy` row), [5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 3 and the hazard alphabet), [8](../testing-strategy.md#8-privacy-and-security-tests) (leaks), [10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [11](../testing-strategy.md#11-coverage-targets), [13](../testing-strategy.md#13-gaps-today-and-the-order-to-close-them) and [14](../testing-strategy.md#14-example-tests) (the `restore_undoes_anonymise` property).
- [Spec](../spec.md): [4.2](../spec.md#42-privacy-check) (what is replaced and kept, placeholder types, variants, escaping), [6.1](../spec.md#61-steps) (steps 3 and 4), [6.2](../spec.md#62-rules-for-every-ai-step) (known names, unknown placeholders), [8.4](../spec.md#84-security) (hostile input), [13](../spec.md#13-open-decisions-before-coding) and [14.5](../spec.md#145-sample-data) (the sample).
- Decision records: [ADR 0004](../adr/0004-code-layout.md) (the layout and import rules), [ADR 0008](../adr/0008-personal-data-detection-bundle.md) (code first, Presidio behind it, and the amendment on known names), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) (golden files and the agent guard).
- The prototype, as evidence of the owner's intent: [`prototype/privacy-check.html`](../../prototype/privacy-check.html) (the list of replacements, their numbering and the "Same person" prompt) and the privacy-check rows of [ux-copy.md](../ux-copy.md).
- [The architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md), one part only: ["`privacy` layers deterministic finders before NER"](../../reports/Clause%20Tracer%20pipeline%20architecture.md#privacy-layers-deterministic-finders-before-ner). [The seams report](../../reports/Clause%20Tracer%20pipeline%20seams.md), the part "Placeholders keep an exact map instead of matching lengths". Where they and this plan differ, this plan wins.
- [The privacy finder design choices report](../../reports/Privacy%20finder%20design%20choices.md): the owner decisions of 21 Nov 2026 and the measured fixes that this plan carries (Group A). Where it and this plan differ, this plan wins.
- [The stage 3 plan](stage-03-links.md), section 9, "For stage 4 (`privacy`)": the allow-list, the terms of the sample and the undefined terms.
- The code: [`src/clause_tracer/privacy/`](../../src/clause_tracer/privacy/), [`core/placeholders.py`](../../src/clause_tracer/core/placeholders.py), [`core/fakes.py`](../../src/clause_tracer/core/fakes.py) (`FakePiiDetector`), [`core/match_fold.py`](../../src/clause_tracer/core/match_fold.py), [`links/sample_clauses.py`](../../src/clause_tracer/links/sample_clauses.py) and [`links/__main__.py`](../../src/clause_tracer/links/__main__.py) (patterns to copy, not to import), [`links/tests/case_builder.py`](../../src/clause_tracer/links/tests/case_builder.py), the root [`conftest.py`](../../conftest.py), [`pyproject.toml`](../../pyproject.toml) and [`scripts/check.sh`](../../scripts/check.sh).

## 4. Checks before starting

- [ ] **The plan is Accepted.** Questions 1 to 26 in section 6 are answered, and the tasks follow the answers. If an answer differs from the recommendation, the planner rewrites the tasks that need it before they start, and records the change in section 8.
- [ ] **The skeleton passes.** Run `.venv/bin/uv sync`, then `scripts/check.sh`. It must exit 0 before any change.
- [ ] **The sample outline is as this plan assumes.** Run `.venv/bin/uv run python -m clause_tracer.ingest --full`. It must print 65 clauses. Sentence `(1).s1` (span 80 to 258) holds "Brightline Studio Ltd", "company number 09876543" and "14 Harbour Street, Leeds LS1 4AB". Sentence `(2).s1` (258 to 344) holds "Karim Benali" and "27 Rue Didouche Mourad, Algiers 16000, Algeria". Sentence `5.3.s1` holds "accounts@brightline.example". Sentence `14.5.s1` holds "Ms Jones". Sentence `p4.s1` (5564 to 5640) holds "Brightline Studio Ltd" and "Sarah Jones". Sentence `p5.s1` holds "Karim Benali". So no Spec 14.5 name or address crosses a sentence boundary. The planner checked this on 21 Nov 2026. If one fails, stop and bring it to the owner.
- [ ] **The link map is as this plan assumes.** Run `.venv/bin/uv run python -m clause_tracer.links`. Its `term` lines must be `Agency`, `Developer`, `Charges`, `Deliverables`, `Master Agreement`, `Milestone` and `Services`, in that order.
- [ ] **The owner has confirmed the planner's values.** Every test value marked "owner to confirm" is the planner's value from the reference code (Constitution T11). The owner also writes the place list (S4-M2-T11) and the other word lists with this plan (question 16).
- [ ] **The docs are on `main`.** The `docs/` branch that holds this plan, with any spec or system design change the answers need, is merged. Milestone 1 is cut from that `main`.

## 5. Milestones and tasks

**Rules for every task.**

- Every new shape in `privacy` is written `@dataclass(frozen=True, slots=True, kw_only=True)`.
- A file whose name starts with `_` is internal to `privacy`. Only `__init__.py` re-exports names, and only the names a task says to export (S4-M5-T3).
- Offsets are half-open, count code points and point into `Document.text`. Words, names and addresses typed by the user are found on the match key with `find_word` (S4-M1-T6), so case, curly quotes, soft hyphens and line breaks do not hide a name. The rule finders (patterns, companies, addresses, people) run their regular expressions on `Document.text` itself.
- Each pattern this plan gives as a string constant `NAME` lives in `src/clause_tracer/privacy/_patterns.py` as `NAME: Final[str]`, and is compiled there once as `NAME_RE: Final[re.Pattern[str]] = re.compile(NAME)`. A fragment (`H`, `WORD`, `SUFFIX_WORDS`, `SUFFIX`, `CONNECTOR`, `CAP`, `STREET_PLAIN`, `STREET_AMBIG`, `LEAD_WORD`, `POST`, `PART`, `MONTHS`, `PARTICLE`, `TOK`, `INIT`, `NAME_RUN`, `ONE_OR_TWO`, `CAPS_TOK`, `CAPS_RUN`, `CAPS_ONE_OR_TWO`, `TITLE_WORDS`, `GOVERNING_LAW_CUE`, `PLACE_END`) is a string only and has no `_RE`. `GOVERNING_LAW_CUE` and `PLACE_END` are defined in S4-M3-T3. A task adds its own constants to the file and keeps the order of the plan. A rule that a task gives in words ("the first word") is written as code in the file the task names.
- Every finder is a pure function that returns `tuple[PiiSuggestion, ...]` through `unique_sorted` (S4-M1-T6), so its result has no exact duplicate and is sorted by start, end and then the order of `PlaceholderKind`. A finder never removes an overlap: that is the job of `resolve_overlaps` (S4-M3-T4).
- Each finder sets one `PiiSource` for all its results: `PARTY_DETAILS` for `find_party_details`; `PATTERN` for `find_patterns`; `RULE` for `find_companies`, `find_addresses` and `find_people`. No code finder uses `NER` or `USER`.
- While an owner task blocks a milestone, go on with the tasks of that milestone that do not depend on it. Do not start the next milestone's branch before the owner merges this one (README, "Branches and pull requests"). An owner task of a later milestone may be filled by the owner at any time.
- `privacy` code is pure (T1): no file, clock, network or print, except in `__main__.py`.
- Tests of `privacy` may import from `clause_tracer.core.tests` (the owner-table loader and the hazard alphabet). They never import another pipeline module.
- A commit that fills an owner table holds no code (the owner-table guard). Golden files and the sample fixture never sit in a `tables` folder.
- **Values to confirm.** A test value marked "owner to confirm" is the planner's value from the reference code that the planner ran on 21 Nov 2026 (Constitution T11). The implementer never changes it. If a test fails, the code or the value is wrong: bring it to the owner. Word lists and tables are the owner's (question 16): the lists in the tasks are the planner's proposal, and the closed place list is an owner task (S4-M2-T11) that the agent does not write or change.
- **Short test cases.** A test that gives only sentences builds its case with `make_case` (S4-M1-T5): one clause `1` that holds the sentences. Expected spans come from `span_of(text, needle, nth)`. A test that gives a text and no sentences passes the text as one sentence.
- **Error messages.** Every `ValueError` of `privacy` code starts with `privacy: `, except the fixture loader and writer, whose messages start with `privacy sample: `. Test helpers are exempt. A message never holds contract text; the one exception is the name of a defined term in a fixture message.
- **Spans in tests.** `Span` takes keyword arguments only. In a test description, `Span(0, 3)` is short for `Span(start=0, end=3)`.
- **The sample.** "The sample" means `src/clause_tracer/ingest/samples/developer-agreement.txt`. "The party details of the sample" are the two parties in S4-M1-T4.

### M1: Foundations

When this is done, `privacy` has a coverage floor, five empty owner tables, a committed fixture of the sample that a root test keeps in step with `ingest` and `links`, a test helper that builds small cases without `ingest`, and the span and word helpers that every finder uses.

- [x] **S4-M1-T1: An 85% coverage floor for `privacy`**
  - **Build:** In `scripts/check.sh`, add one last line: `run coverage report --include='src/clause_tracer/privacy/*' --fail-under=85`. In `scripts/README.md`, change the `check.sh` row to say "a 95% branch-coverage floor for `core` and an 85% floor for `ingest`, `links` and `privacy`". In `docs/testing-strategy.md` section 11, change nothing: the table already holds the 85% target for pipeline modules.
  - **Files:** `scripts/check.sh`, `scripts/README.md`.
  - **Tests first:** None. The check is the script itself.
  - **Done when:** `scripts/check.sh` exits 0 and its last lines show a coverage table for `privacy`. Then change 85 to 100 in your working copy, see the script exit non-zero with the line `Coverage failure: total of 96 is less than fail-under=100` (the total may differ, and must be below 100), and put 85 back. Do not use 101: `coverage` refuses a floor above 100 as invalid before it compares any total, so that run proves nothing about coverage (found in the M1 build).
  - **Rules:** [Testing strategy 11](../testing-strategy.md#11-coverage-targets).
  - **Depends on:** None

- [x] **S4-M1-T2: Create the five empty owner tables**
  - **Build:** The five owner tables were committed, filled, together with this plan (commit `5bbc2b4`). When a file already exists, do not create or edit it: tick this task only, in a commit that holds the plan tick and no table file. (Built that way in M1.) The five committed tables lacked the `HEADER` line, so `load_table` refused them; the owner added it as line 1 of each, in commit `99a76f0` (22 Nov 2026), a commit of the five tables and no code. Otherwise create these files, each holding exactly two lines: the `HEADER` line of `clause_tracer.core.tests.owner_tables`, then `# Format: docs/plans/stage-04-privacy.md, task <id>.` with the id of the owner task that fills it: `src/clause_tracer/privacy/tests/tables/finders.toml` (S4-M2-T8), `src/clause_tracer/privacy/tests/tables/party_details.toml` (S4-M2-T9), `src/clause_tracer/privacy/tests/tables/pipeline.toml` (S4-M3-T8), `src/clause_tracer/privacy/tests/tables/entities.toml` (S4-M3-T9), `src/clause_tracer/privacy/tests/tables/sample.toml` (S4-M5-T5). This commit holds these five files and the plan tick, and no code.
  - **Files:** the five files above.
  - **Tests first:** None. The loader test of S1-M3-T1 covers a header-only file.
  - **Done when:** `.venv/bin/uv run python scripts/check_owner_tables.py` exits 0 before the commit, and `scripts/check.sh` exits 0.
  - **Rules:** T11.
  - **Depends on:** None

- [x] **S4-M1-T3: The privacy fixture format, its writer and its loader**
  - **Build:** In `src/clause_tracer/privacy/sample_input.py`:
    - `FIXTURE_FORMAT: Final[str] = "clause-tracer-privacy-sample"` and `FIXTURE_VERSION: Final[int] = 1`.
    - `@dataclass(frozen=True, slots=True, kw_only=True) class PrivacyInput` with exactly four fields in this order: `document: Document`, `clauses: tuple[Clause, ...]`, `parties: tuple[Party, ...]`, `terms: tuple[DefinedTerm, ...]`. It is the input of `find_personal_data` (S4-M3-T6). Add no method.
    - `def dump_privacy_fixture(case: PrivacyInput) -> str`. It raises `ValueError("privacy sample: text documents only")` when any of `document.char_map`, `glyphs`, `pages`, `furniture`, `hidden`, `undecodable` or `tracked_changes` is not empty, and `ValueError(f"privacy sample: kind {kind} is not a text kind")` when `document.source.kind` is not `TEXT`, `MARKDOWN` or `PASTED` (`kind` is the `FileKind` value). It then calls `_check_input(case)` (below). It returns `json.dumps(obj, ensure_ascii=False, indent=2) + "\n"`, where `obj` is this dict, with keys in this order:
      ```text
      {"format": FIXTURE_FORMAT, "version": FIXTURE_VERSION,
       "document": {"schema_version": int, "source": {"name": str, "kind": str (the FileKind value), "sha256": str, "size": int},
                    "text": str, "warnings": [{"code": str, "page": int | null}, ...]},
       "clauses": [{"id": str, "number": str | null, "heading": str | null, "level": int, "parent_id": str | null,
                    "start": int, "end": int, "numbering_source": str,
                    "sentences": [{"id": str, "start": int, "end": int}, ...]}, ...],
       "parties": [{"name": str, "address": str | null, "yours": bool}, ...],
       "terms": [{"term": str, "definition": {"start": int, "end": int},
                  "uses": [{"start": int, "end": int}, ...]}, ...]}
      ```
    - `def load_privacy_fixture(text: str) -> PrivacyInput`. It parses `text` with `json.loads` and builds the `Document` (with `char_map`, `glyphs`, `pages`, `furniture`, `hidden`, `undecodable` and `tracked_changes` all `()`), the clauses, the parties and the terms. It turns `kind` into `FileKind`, each warning into `InputWarning`, every JSON list into a tuple, and every id into `ClauseId` or `SentenceId`. It raises `ValueError` with a message that starts `privacy sample: ` in each of these cases, and no other error. The checks run in this order, and the first error is raised:
      - the text is not JSON (`privacy sample: not JSON`);
      - the top level is not an object (`privacy sample: top level is not an object`);
      - `format` is not the value above (`privacy sample: format is not clause-tracer-privacy-sample`);
      - `version` is not 1 (`privacy sample: version is not 1`);
      - an object has a key not listed in the format, or lacks one (`privacy sample: unknown key <key>` / `privacy sample: missing key <key>`);
      - a field has the wrong JSON type. Every field's JSON type is checked against the format, and `null` is allowed only where the format says `| null`. The message names the leaf key: `privacy sample: <key> has the wrong type`. A JSON `true` is not an `int`;
      - `kind` is not `text`, `markdown` or `pasted` (`privacy sample: kind <kind> is not a text kind`);
      - then `_check_input(case)` on the built input.
    - `def _check_input(case: PrivacyInput) -> None`, which raises `ValueError` with the prefix `privacy sample: ` on the first failure, and runs these checks in order. Checks (1) to (8) are passes over the whole input, in the order listed: pass (1) runs over all clauses, then all sentences, then all terms, before pass (2) starts, and so on; the first failing pass in list order raises. (1) A span outside the text: a clause, a sentence, a term definition or a term use with `start < 0`, `end < start` or `end > len(text)` (`privacy sample: span of <id> is outside the text`, where `<id>` is the clause id, the sentence id, or the term). (2) `level < 1` on a clause (`privacy sample: level of <id> is not 1 or more`). (3) A clause id that an earlier clause has (`privacy sample: duplicate clause id <id>`). (4) A sentence id that an earlier sentence in the document has (`privacy sample: duplicate sentence id <id>`). (5) A sentence span that is not inside its clause span (`privacy sample: span of <id> is outside its clause`). (6) A clause that starts before the end of the clause before it (`privacy sample: clause <id> is out of order`). (7) A sentence that starts before the end of the sentence before it in its clause (`privacy sample: sentence <id> is out of order`). (8) A party whose `name` is empty or only spaces (`privacy sample: party name is empty`).
    - Do not export anything from `__init__.py` yet.
  - **Files:** `src/clause_tracer/privacy/sample_input.py`, `src/clause_tracer/privacy/tests/test_sample_input.py`, `src/clause_tracer/privacy/README.md` (add a "Sample fixture" section: the format above, the checks, and that the fixture is read and written only by the caller, because `privacy` code reads no file).
  - **Tests first:** in `test_sample_input.py`, with a helper `_case() -> PrivacyInput` over the text `"1. Pay Brightline Ltd.\n"` (23 characters). The document has source `SourceFile(name="t.txt", kind=FileKind.TEXT, sha256="0" * 64, size=len(text.encode()))` (23 for this text; the helper that builds a `Document` takes the text, so another text, such as `"£5 due.\n"` with 9 UTF-8 bytes, gets its own size), `schema_version=1`, every tuple `()`. One clause `1` (span 0 to 23, number `"1"`, heading `None`, level 1, no parent, `numbering_source="numbers"`, one sentence `1.s1` from 0 to 23). One party `Party(name="Brightline Ltd", address=None, yours=False)`. One term `DefinedTerm(term="Agency", definition=Span(start=0, end=23), uses=(Span(start=3, end=6),))`. A test that needs invalid JSON takes `json.loads(dump_privacy_fixture(_case()))`, changes the dict, and passes `json.dumps` of it to `load_privacy_fixture`; this holds for every loader test, including the duplicate-id, out-of-order and level tests, which start from the valid dump and edit the dict, because the writer refuses invalid input. The load checks run object by object, outermost first, in document order: for each object, every unknown-key check, then every missing-key check, then every wrong-type check of THAT object's own fields, in document order; only then the checks of the objects it holds, in document order. A wrong-typed element of a list that is not an object names the list's key (`parties`); a wrong-typed field inside an object element names that field. An object's child objects are checked after all of its own scalar fields (so `document.schema_version` and `document.text` come before `document.source`). `format` and `version` are checked first, so a missing `format` gives `privacy sample: format is not clause-tracer-privacy-sample`. Only `test_not_json` passes the literal `"{"`:
    - `test_round_trip` (`load_privacy_fixture(dump_privacy_fixture(case))` equals `case`);
    - `test_dump_ends_with_one_newline` (the string ends with `"}\n"`);
    - `test_dump_keeps_non_ascii` (a case with the text `"£5 due.\n"`, one clause and one sentence over its 8 characters, and a party named `"Brightline £"` dumps the character `£` itself, not an escape sequence for it);
    - `test_warning_round_trips` (a document with `warnings=(InputWarning(code="not_english", page=None),)` round-trips);
    - `test_dump_refuses_glyphs` (a document with `pages=(Page(number=1, width=1.0, height=1.0),)` raises `ValueError`);
    - `test_dump_refuses_a_pdf_kind` (a document whose source kind is `FileKind.PDF`, with no glyphs, raises `privacy sample: kind pdf is not a text kind`);
    - `test_not_json` (`"{"` raises `ValueError` whose message starts `privacy sample: `);
    - `test_wrong_format` (`format` set to `"other"` raises);
    - `test_wrong_version` (`"version": 2` raises);
    - `test_unknown_key` (an extra key `"x"` in a party raises, and the message names `x`);
    - `test_missing_key` (a term without `uses` raises, and the message names `uses`);
    - `test_bool_is_not_int` (`"level": true` raises);
    - `test_unknown_kind` (`"kind": "word"` raises, and the message is `privacy sample: kind word is not a text kind`);
    - `test_span_outside_text` (a clause `end` of `999` raises `privacy sample: span of 1 is outside the text`);
    - `test_term_use_outside_text` (a use `end` of `999` raises `privacy sample: span of Agency is outside the text`);
    - `test_level_below_one` (`"level": 0` raises `privacy sample: level of 1 is not 1 or more`);
    - `test_duplicate_clause_id` (a second clause with the id `1`, span 23 to 23 and one sentence `1.s2` from 23 to 23, raises `privacy sample: duplicate clause id 1`);
    - `test_duplicate_sentence_id` (a second clause `2`, span 23 to 23, whose one sentence has the id `1.s1` and span 23 to 23, raises `privacy sample: duplicate sentence id 1.s1`);
    - `test_sentence_outside_its_clause` (the `end` of clause `1` set to `10`, the sentence `1.s1` left at 0 to 23, raises `privacy sample: span of 1.s1 is outside its clause`);
    - `test_clause_out_of_order` (a second clause `2` that starts at 10 raises `privacy sample: clause 2 is out of order`; clause 2 ends at 23, and its sentence `2.s1` is 10 to 23);
    - `test_sentence_out_of_order` (the clause `1` given two sentences, `1.s1` from 10 to 23 and `1.s2` from 5 to 23, raises `privacy sample: sentence 1.s2 is out of order`);
    - `test_empty_party_name` (a party `name` of `"  "` raises `privacy sample: party name is empty`);
    - `test_dump_refuses_what_load_refuses` (a case whose clause has `level=0` makes `dump_privacy_fixture` raise `privacy sample: level of 1 is not 1 or more`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_sample_input.py` reports 23 passed, and `scripts/check.sh` exits 0.
  - **Rules:** D4 and I9 (validated once at the door), T1 (pure: the caller reads the file), S1, S3.
  - **Depends on:** None

- [x] **S4-M1-T4: The sample fixture and its drift test**
  - **Build:** In `src/clause_tracer/privacy/__init__.py`, export `PrivacyInput`, `dump_privacy_fixture` and `load_privacy_fixture`. Create `tests/test_privacy_sample.py` with `SAMPLE_TEXT` (the path of `src/clause_tracer/ingest/samples/developer-agreement.txt`, built as in `tests/test_links_sample.py`) and `FIXTURE` (the path of `src/clause_tracer/privacy/samples/developer-agreement.privacy.json`). Add the constant `PARTIES: tuple[Party, ...] = (Party(name="Brightline Studio Ltd", address="14 Harbour Street, Leeds LS1 4AB", yours=False), Party(name="Karim Benali", address="27 Rue Didouche Mourad, Algiers 16000, Algeria", yours=True))`. These are the party details of Spec 14.5. Generate the fixture with `.venv/bin/uv run pytest tests/test_privacy_sample.py --update-goldens`, then read it. Add a row for `test_privacy_sample.py` to `tests/README.md`: "The `privacy` fixture against `ingest` and `links`, and the sample from text to placeholder text". Add `src/clause_tracer/privacy/samples/README.md`, which says the fixture is the `ingest` output, the `links` terms and the typed party details for `src/clause_tracer/ingest/samples/developer-agreement.txt`, written only by `pytest tests/test_privacy_sample.py --update-goldens`, and never edited by hand.
  - **Files:** `src/clause_tracer/privacy/__init__.py`, `tests/test_privacy_sample.py`, `tests/README.md`, `src/clause_tracer/privacy/samples/developer-agreement.privacy.json`, `src/clause_tracer/privacy/samples/README.md`.
  - **Tests first:** in `tests/test_privacy_sample.py`: `test_fixture_matches_ingest_and_links(check_golden)` (`document = read_text_file(SAMPLE_TEXT.read_bytes(), kind=FileKind.TEXT, name="developer-agreement.txt")`, `clauses = split_clauses(document)`, `terms = map_links(document, clauses).terms`, then `check_golden(FIXTURE, dump_privacy_fixture(PrivacyInput(document=document, clauses=clauses, parties=PARTIES, terms=terms)))`); `test_fixture_loads` (`load_privacy_fixture(FIXTURE.read_text(encoding="utf-8"))` has 65 clauses, the last with id `S1.2`, 2 parties and 7 terms, the first term `Agency`).
  - **Done when:** `.venv/bin/uv run pytest tests/test_privacy_sample.py` reports 2 passed without `--update-goldens`, and `scripts/check.sh` exits 0.
  - **Rules:** T11 (regenerated only by the named command), S1, the import contracts ([ADR 0004](../adr/0004-code-layout.md)).
  - **Depends on:** S4-M1-T3

- [x] **S4-M1-T5: The test-case builder**
  - **Build:** In `src/clause_tracer/privacy/tests/case_builder.py` (test code, not exported):
    - `def make_case(sentences: Sequence[str], *, parties: Sequence[Party] = (), terms: Sequence[DefinedTerm] = ()) -> PrivacyInput`. The text is the sentences joined by one space. Each sentence span covers its text and the one space that follows it, except the last sentence, which ends at the end of the text. A sentence that is empty or holds `"\n"` or `"\r"` raises `ValueError("a sentence must be non-empty and hold no line break")`. With no sentences the text is `""` and `clauses` is `()`. Otherwise there is one clause: `id=ClauseId("1")`, `number="1"`, `heading=None`, `level=1`, `parent_id=None`, `span` over the whole text, `numbering_source="numbers"`, and sentences with the ids `1.s1`, `1.s2` and so on. The document has `schema_version=1`, `source=SourceFile(name="case.txt", kind=FileKind.PASTED, sha256=hashlib.sha256(text.encode()).hexdigest(), size=len(text.encode()))`, and every tuple `()`. The result holds `tuple(parties)` and `tuple(terms)`.
    - `def span_of(text: str, needle: str, nth: int = 1) -> Span`, the span of the `nth` occurrence of `needle` in `text`. Occurrences are counted from 1 with `str.find`, and each search starts one character after the start of the occurrence before it, so occurrences may overlap. It raises `AssertionError(f"{needle!r} occurs fewer than {nth} times")`, and `AssertionError("nth must be 1 or more")` when `nth < 1`.
    - `def suggestion(text: str, needle: str, kind: PlaceholderKind, source: PiiSource, nth: int = 1) -> PiiSuggestion`, which returns `PiiSuggestion(span=span_of(text, needle, nth), kind=kind, source=source)`.
  - **Files:** `src/clause_tracer/privacy/tests/case_builder.py`, `src/clause_tracer/privacy/tests/test_case_builder.py`.
  - **Tests first:** in `test_case_builder.py`: `test_text_joins_sentences` (`make_case(["A b.", "C d."]).document.text == "A b. C d."`); `test_sentence_spans_tile_the_text` (for the same call: `1.s1` is 0 to 5 and `1.s2` is 5 to 9, and the clause is 0 to 9); `test_no_sentences` (`make_case([])` has the text `""` and no clauses); `test_empty_sentence_raises` (`make_case([""])` raises `ValueError`); `test_line_break_raises` (`make_case(["a\nb"])` raises `ValueError`); `test_parties_and_terms_pass_through` (a `Party` and a `DefinedTerm` given to `make_case` come back as one-item tuples); `test_span_of_nth` (`span_of("a x a", "a", 2) == Span(start=4, end=5)`); `test_span_of_missing_raises` (`span_of("abc", "z")` raises `AssertionError`); `test_suggestion_builds` (`suggestion("Hi Sam", "Sam", PlaceholderKind.PERSON, PiiSource.NER)` equals `PiiSuggestion(span=Span(start=3, end=6), kind=PlaceholderKind.PERSON, source=PiiSource.NER)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_case_builder.py` reports 9 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T3 (a simple working stand-in for `ingest`), S2 (the tests run without other modules).
  - **Depends on:** S4-M1-T3

- [x] **S4-M1-T6: Span helpers and the whole-word search**
  - **Build:** Three files.
    - `src/clause_tracer/privacy/_spans.py`:
      - `KINDS: Final[tuple[PlaceholderKind, ...]] = tuple(PlaceholderKind)`.
      - `def trimmed_span(text: str, span: Span) -> Span | None`: move `start` forward over every character for which `str.isspace()` is true, and `end` back over the same, and return `None` when nothing is left. A span with `start == end` gives `None`.
      - `def overlaps(first: Span, second: Span) -> bool`: `False` when either span has `start == end`; otherwise `first.start < second.end and second.start < first.end`.
      - `def order_key(suggestion: PiiSuggestion) -> tuple[int, int, int]`: `(span.start, span.end, KINDS.index(kind))`.
      - `def unique_sorted(suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]`: the suggestions with every exact duplicate removed (two `PiiSuggestion`s are duplicates only when span, kind and source are all equal; the first one seen is kept), then sorted by `order_key` with a stable sort, so suggestions with an equal `order_key` but a different source keep their input order.
      - `def subtract_spans(span: Span, cuts: Iterable[Span]) -> tuple[Span, ...]`, the parts of `span` that no span of `cuts` covers, left to right. It is used by `cut_in_places` (S4-M3-T3) and `resolve_overlaps` (S4-M3-T4). Write it exactly:
        ```python
        def subtract_spans(span: Span, cuts: Iterable[Span]) -> tuple[Span, ...]:
            pieces: list[Span] = []
            position = span.start
            for cut in sorted(cuts, key=lambda c: c.start):
                if cut.start > position:
                    pieces.append(Span(start=position, end=min(cut.start, span.end)))
                position = max(position, cut.end)
            if position < span.end:
                pieces.append(Span(start=position, end=span.end))
            return tuple(piece for piece in pieces if piece.end > piece.start)
        ```
    - `src/clause_tracer/privacy/_patterns.py` (created here; later tasks add to it in the order of this plan). Four constants, each `Final[str]` with its `_RE` compiled as the rules say, for the layer 3 rule below:
      ```python
      HONORIFIC_BEFORE = r"\b(?:Mr|Mrs|Ms|Miss|Mx|Dr)\.?[ \t]+$"
      CLAUSE_NUMBER = r"^[ \t]*(?:\(?[0-9A-Za-z]{1,3}[.)]|\d+(?:\.\d+)*\.?)[ \t]+$"
      SENTENCE_MARK = r"[.!?]"
      HEADING_WORD = r"[^\W\d_][\w'’-]*"
      ```
    - `src/clause_tracer/privacy/_match.py`: `def find_word(key: MatchKey, needle: str) -> tuple[Span, ...]`. `needle` is already folded (the `.text` of `fold_for_matching`). It returns `()` when `needle` is empty. Otherwise it scans `key.text` from position 0 with `str.find`. A hit at folded index `i` with `j = i + len(needle)` counts as a whole word when `i == 0 or not key.text[i - 1].isalnum()` and `j == len(key.text) or not key.text[j].isalnum()`. A hit that counts gives `Span(start=key.to_canonical[i], end=key.to_canonical[j])` and the scan goes on from `j`; a hit that does not count goes on from `i + 1`. The spans come left to right and never overlap.
      Also in `_match.py`: `def find_name_form(text: str, key: MatchKey, form: str, stop_words: frozenset[str], ambiguous_words: frozenset[str]) -> tuple[Span, ...]`, for a form of a name. `text` is the canonical text that `key` was folded from, and `form` is already folded (it comes from `name_forms`, defined in S4-M2-T1). A form that holds a space gives `find_word(key, form)`. A form of one word gives `()` when it is in `stop_words` (layer 2). Otherwise it gives the spans of `find_word(key, form)` for which both of these hold: `text[span.start].isupper()` is true (a one-word form counts only where its first letter is a capital in the contract, as a use of a defined term does: question 17), and it is not the case that `form in ambiguous_words and not _ambiguous_ok(text, span)` (layer 3, below). Layer 4 (a repeat count that lifts the layer 3 skip) is not built.
      **Layer 3 (question 17).** A one-word form that is also a common word ("Hope", "Rose", "Brown") counts only where the contract gives evidence that it is a name: it is not at the start of a sentence and not in a heading line, unless it is followed by `'s` or `’s`, or it follows an honorific. Write the helpers exactly, in `_match.py`:
      ```python
      _OPENERS: Final[str] = " \t\"“‘'("

      def _line_bounds(text: str, index: int) -> tuple[int, int]:
          start = text.rfind("\n", 0, index) + 1
          end = text.find("\n", index)
          return start, (len(text) if end < 0 else end)

      def _is_heading(line: str) -> bool:
          if SENTENCE_MARK_RE.search(line):
              return False
          words = HEADING_WORD_RE.findall(line)
          return bool(words) and all(word[0].isupper() for word in words)

      def _sentence_initial(text: str, index: int) -> bool:
          line_start, _ = _line_bounds(text, index)
          if CLAUSE_NUMBER_RE.match(text[line_start:index]):
              return True
          j = index
          while j > 0 and text[j - 1] in _OPENERS:
              j -= 1
          if j == 0:
              return True
          if text[j - 1] in ".!?":
              return True
          if text[j - 1] == "\n":
              before = text[: j - 1]
              return not before.strip() or before.rstrip(" \t").endswith((".", "!", "?"))
          return False

      def _ambiguous_ok(text: str, span: Span) -> bool:
          if text[span.end : span.end + 2] in ("'s", "’s"):
              return True
          if HONORIFIC_BEFORE_RE.search(text[max(0, span.start - 8) : span.start]):
              return True
          if _sentence_initial(text, span.start):
              return False
          line_start, line_end = _line_bounds(text, span.start)
          return not _is_heading(text[line_start:line_end])
      ```
      Layer 3 leaks by design: `Ms Brown signs. Brown shall pay.` leaves the sentence-initial `Brown` readable (the trade is the owner's to accept: report, open question 3).
  - **Files:** `src/clause_tracer/privacy/_spans.py`, `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/_match.py`, `src/clause_tracer/privacy/tests/test_spans.py`, `src/clause_tracer/privacy/tests/test_match.py`.
  - **Tests first:** in `test_spans.py`: `test_trimmed_span_moves_both_ends` (`trimmed_span("  ab  ", Span(start=0, end=6)) == Span(start=2, end=4)`); `test_trimmed_span_all_space_is_none` (`trimmed_span("   ", Span(start=0, end=3)) is None`); `test_trimmed_span_empty_is_none` (`Span(start=1, end=1)` on `"abc"` gives `None`); `test_overlaps_true` (`Span(0, 3)` and `Span(2, 5)`); `test_overlaps_touching_is_false` (`Span(0, 3)` and `Span(3, 5)`); `test_overlaps_empty_is_false` (`Span(2, 2)` and `Span(0, 5)`); `test_order_key_uses_kind_order` (two suggestions with the same span, `ADDRESS` and `PERSON`: `order_key` of the `PERSON` one is smaller); `test_unique_sorted_removes_duplicates_and_sorts` (the suggestions `B`, `A`, `B` with `A` before `B` in span order give `(A, B)`); `test_subtract_spans_cuts_the_middle` (`Span(0, 10)` minus `(Span(3, 5),)` gives `(Span(0, 3), Span(5, 10))`); `test_subtract_spans_cuts_an_edge` (`Span(0, 10)` minus `(Span(0, 4),)` gives `(Span(4, 10),)`); `test_subtract_spans_joins_overlapping_cuts` (`Span(0, 10)` minus `(Span(3, 6), Span(2, 4))` gives `(Span(0, 2), Span(6, 10))`); `test_subtract_spans_nothing_left` (`Span(2, 5)` minus `(Span(0, 10),)` gives `()`); `test_subtract_spans_no_cuts` (`Span(0, 10)` minus `()` gives `(Span(0, 10),)`). In `test_match.py`, each `find_word` case folds the text with `fold_for_matching` and passes `fold_for_matching(needle).text` as needle, and each `find_name_form` case passes `fold_for_matching(text)` as `key`, `stop_words=frozenset()` and `ambiguous_words=frozenset()` unless the test says otherwise: `test_finds_whole_words_only` (text `"Ms Jones and Jonesy, jones."`, needle `Jones`: spans `(3, 8)` and `(21, 26)`); `test_soft_hyphen_does_not_hide_a_word` (text `"Jo­nes here"`, needle `jones`: `(0, 6)`); `test_line_break_matches_a_space` (text `"Brightline\nStudio Ltd"`, needle `brightline studio ltd`: `(0, 21)`); `test_sharp_s_folds_to_ss` (text `"Strauß"`, needle `strauss`: `(0, 6)`; needle `stras` gives `()`); `test_hits_do_not_overlap` (text `"aa aa aa"`, needle `aa aa`: `((0, 5),)`); `test_empty_needle_gives_nothing` (needle `""` gives `()`); `test_punctuation_ends_a_word` (text `"(Jones)"`, needle `jones`: `(1, 6)`); `test_a_form_of_two_words_ignores_case` (text `"karim benali signs"`, form `karim benali`: `((0, 12),)`); `test_a_one_word_form_needs_a_capital` (text `"karim signs. Karim signs."`, form `karim`: `((13, 18),)`); `test_a_stop_word_is_skipped` (text `"Will pay."`, form `will`, `stop_words=frozenset({"will"})`: `()`). Layer 3 (all with form `hope` and `ambiguous_words=frozenset({"hope"})`, except the last, which says its form; the spans are `(start, end)` pairs; these values are the planner's, owner to confirm):
    - `test_layer3_sentence_initial_ambiguous_word_is_left` (`"Rose Hope signs. Hope is not a term. Contact Hope."` gives `(5, 9)` and `(45, 49)`);
    - `test_layer3_possessive_counts_at_a_sentence_start` (`"Hope's car. Hope cars."` gives `(0, 4)`);
    - `test_layer3_honorific_counts` (`"Ms Hope signs. Mr Hope signs."` gives `(3, 7)` and `(18, 22)`);
    - `test_layer3_heading_line_is_left` (`"Price and Payment\nHope\nContact Hope's team."` gives `(31, 35)`);
    - `test_layer3_clause_number_is_a_sentence_start` (`"1. Hope signs.\n2.1 Hope pays. Ask Hope."` gives `(34, 38)`);
    - `test_layer3_unambiguous_word_needs_no_evidence` (form `jones` with the same `ambiguous_words`, `"Jones shall pay. Jones signs."` gives `(0, 5)` and `(17, 22)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_spans.py src/clause_tracer/privacy/tests/test_match.py` reports 29 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, B2 (own helpers; no import from `links`), system design 4.2 (the span is found through the map).
  - **Depends on:** None

- [x] **S4-M1-T7: Close the error-path test gaps of the fixture loader (added after the M1 review)**
  - **Why:** The M1 code review found eight lines of `sample_input.py` with no test (the wrong-type paths and the unknown file kind), an unused test helper, and a test import from `clause_tracer.core.link_map` where every other core name comes from `clause_tracer.core`. The owner chose on 22 Nov 2026 to clean up. This task changes no behaviour and no message of `sample_input.py`.
  - **Build:** In `test_sample_input.py` only: delete the unused helper `_sentence_rows`, and import `DefinedTerm` from `clause_tracer.core`. Do not edit `sample_input.py`.
  - **Files:** `src/clause_tracer/privacy/tests/test_sample_input.py`.
  - **Tests first:** The 23 tests of T3 stay as they are and must still pass without any edit. Add these 7 tests to `test_sample_input.py`. Each starts from `json.loads(dump_privacy_fixture(_case()))`, edits the dict, passes `json.dumps` of it to `load_privacy_fixture`, and checks the message with `pytest.raises(ValueError, match=...)`: a top level that is a JSON array, given as the literal text `"[]"` (`privacy sample: top level is not an object`); `document` set to `[]` (`privacy sample: document has the wrong type`); `clauses` set to `"x"` (`privacy sample: clauses has the wrong type`); the first clause `id` set to `5` (`privacy sample: id has the wrong type`); the first party `yours` set to `"yes"` (`privacy sample: yours has the wrong type`); for the warning test, first set `document["warnings"]` to `[{"code": "not_english", "page": None}]`, then set that `page` to `"1"` (`privacy sample: page has the wrong type`); `source.kind` set to `"bogus"` (`privacy sample: kind bogus is not a text kind`). The planner checked all seven messages against the code on 22 Nov 2026.
  - **Done when:** the 23 old tests and the 7 new tests pass, `scripts/check.sh` exits 0, and the missing lines of `sample_input.py` that these tests reach are covered.
  - **Rules:** I9, D4.
  - **Depends on:** S4-M1-T3

**Draft for the owner, not a task yet: names with an apostrophe or a hyphen.** `find_word` treats `'` and `-` as the end of a word. The form `neil` matches the `Neil` in `O'Neil`, and `anne` matches the `Anne` in `Anne-Marie`, so a hit can cover part of a name and leave the rest readable. The owner chose on 22 Nov 2026 to try a code fix first, and to write the known limit in the README only if the fix fails or is not enough. Nothing here is built, and a cheap implementer must not build it. It becomes a task, with an id, when the owner accepts one rule and its values.

- **B1 (the rule the owner first agreed to try):** `'` and `-` between letters do not end a word. A hit that touches a letter through `'` or `-` is dropped, so `neil` finds nothing in `O'Neil`. The planner does not recommend it: when no other finder finds the name, the whole name stays readable, which is worse than a partial hit.
- **B2 (the planner's proposal):** a hit that touches a letter through `'` or `-` grows to cover the whole attached word. `Neil` in `O'Neil` gives the span of `O'Neil`, and `Anne` in `Anne-Marie` gives the span of `Anne-Marie`. A `'s` or `’s` after a hit is not part of the name (`Hope's` still gives `Hope`). The planner recommends B2.
- **Reach of B2:** it changes `find_word`, which every caller uses, so it also grows typed party and company hits (a company `Acme` in `Acme-branded` would hide `Acme-branded`; a surname `Benali` in `Benali-Smith` would hide `Benali-Smith`). It also meets the capital test of `find_name_form`: after growth, `text[span.start].isupper()` reads the prefix, so a name written `d'Arcy` or `de-Souza` would be dropped. The owner decides these cases before any build.
- **Values to confirm if B2 is accepted (planner's proposal):** `O'Neil signs` with form `neil` gives `(0, 6)`; `Anne-Marie signs` with form `anne` gives `(0, 10)`; `Hope's car` with form `hope` gives `(0, 4)`; `test_punctuation_ends_a_word` keeps `(1, 6)`.
- **When the question is closed:** the owner accepts the rule and the values, the tests pass and `scripts/check.sh` exits 0, and the typed-party check on the CUAD contracts (`research_notes/Privacy finder tests/B3-run.py`, run on the finished stage 4) shows no name part left readable next to a hit. The owner confirms this check, or names another one. Until then the question is open, and the known limit is not written.

### M2: Code finders

When this is done, `privacy` finds typed party details with their variants, emails, phones, IDs, bank details, the four bare identifiers (NINO, GB VAT, company prefix, card number), companies, addresses and people by code alone, the owner's tables fix what each finder returns, and the owner's list of governing-law places is in place.

- [x] **S4-M2-T1: Name and address forms**
  - **Build:** In `src/clause_tracer/privacy/names.py`:
    - `HONORIFICS: Final[tuple[str, ...]] = ("mr", "mrs", "ms", "miss", "mx", "dr")`.
    - `COMPANY_SUFFIXES: Final[frozenset[str]] = frozenset({"ltd", "limited", "llc", "llp", "plc", "inc", "corp", "gmbh", "ag", "sarl", "sas", "bv", "nv", "pty", "co"})`.
    - `SUFFIX_SWAPS: Final[Mapping[str, str]] = MappingProxyType({"ltd": "limited", "limited": "ltd"})`.
    - `NAME_STOP_WORDS: Final[frozenset[str]] = frozenset({"january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "will", "mark", "grant", "bill", "page", "price"})`. A one-word form in this set is never searched for (question 17, layer 2). Will, Mark, Grant and Bill stay in this hard list: layer 4 is off.
    - `COMMON_WORD_NAMES: Final[frozenset[str]]`, the words of layer 3 (S4-M1-T6). A one-word form in this set is searched for only where the contract gives evidence of a name. No word is in both sets. It holds exactly: `rose hope frank art bob pat ray rob jack sue dawn joy faith grace summer ruby amber daisy lily violet brown green white black king hall young long cook baker wood stone hill field bell ward lane mills bush rice fox bird major miller carter porter taylor parker hunter fisher mason cooper`. It is a word list: the owner reads it with the plan and may change it (Constitution T11; question 16).
    - `EXTENDED_COMPANY_SUFFIXES: Final[frozenset[str]] = COMPANY_SUFFIXES | frozenset({"lp", "corporation", "incorporated", "srl", "spa", "oy", "kg", "ug", "pte"})`. It is used to read a company name that a rule found (S4-M2-T7, S4-M3-T2). A typed party is still a company by `COMPANY_SUFFIXES` only (question 2).
    - `def fold_text(text: str) -> str`, which returns `fold_for_matching(text).text`.
    - `def strip_honorific(tokens: Sequence[str]) -> tuple[str, ...]`: the tokens without the first one, when `tokens[0].rstrip(".").casefold()` is in `HONORIFICS`; otherwise the tokens unchanged. An empty list gives `()`.
    - `def company_suffix(name: str) -> str | None`: the last token of `name.split()`, with `.` and `,` stripped from its right end and case-folded, when it is in `COMPANY_SUFFIXES`; otherwise `None`. A name with no tokens gives `None`.
    - `def is_company_name(name: str) -> bool`: `company_suffix(name) is not None`.
    - `def is_company_seed(name: str) -> bool`: the last token of `name.split()`, with `.` and `,` stripped from its right end and case-folded, is in `EXTENDED_COMPANY_SUFFIXES`. A name with no tokens gives `False`.
    - `def name_forms(name: str, kind: PlaceholderKind) -> tuple[str, ...]`. It raises `ValueError("privacy: name forms need a person or a company")` when `kind` is not `PERSON` or `COMPANY`. The result holds folded strings (through `fold_text`), with no duplicate, sorted by `(-len(form), form)`. For `PERSON`, with `tokens = strip_honorific(name.split())` and `last = tokens[-1]`: no tokens gives `()`. Otherwise the forms are: the tokens joined by one space; when there are 3 or more tokens, `tokens[0] + " " + last`; when there are 2 or more tokens and `len(tokens[0]) >= 3`, `tokens[0]`; when there are 2 or more tokens and `len(last) >= 3`, `last`; and for each `h` in `HONORIFICS`, `f"{h} {last}"` and `f"{h}. {last}"`. For `COMPANY`, with `tokens = name.split()`: no tokens gives `()`. When `company_suffix(name)` is not `None`, `core = tokens[:-1]`, and no core gives `()`; the forms are the core joined by one space, and the core plus each spelling in `[suffix, SUFFIX_SWAPS[suffix]]` (the second only when the suffix has a swap) joined by one space. Otherwise the only form is all tokens joined by one space.
    - `def address_forms(address: str) -> tuple[str, ...]`: folded, no duplicate, sorted by `(-len(form), form)`. The address is stripped of spaces at both ends first (`str.strip()`: all whitespace at both ends). The forms are the whole address, and the part before the first comma (stripped) when the address has a comma, that part starts with a digit and it has 2 or more words.
  - **Files:** `src/clause_tracer/privacy/names.py`, `src/clause_tracer/privacy/tests/test_names.py`.
  - **Tests first:** in `test_names.py`, with `honorific_forms(last: str) -> set[str]` as `{f"{h}{dot} {last}" for h in HONORIFICS for dot in ("", ".")}`:
    - `test_person_forms_of_two_words` (`name_forms("Sarah Jones", PERSON)` as a set equals `{"sarah jones", "sarah", "jones"} | honorific_forms("jones")`, it has 15 items, and it equals itself sorted by `(-len(form), form)`);
    - `test_person_forms_of_three_words` (`"Ms. Anna Maria Smith"` gives the set `{"anna maria smith", "anna smith", "anna", "smith"} | honorific_forms("smith")`);
    - `test_person_of_one_short_word` (`"Li"` gives `{"li"} | honorific_forms("li")`);
    - `test_company_forms_swap_ltd_and_limited` (`name_forms("Brightline Studio Ltd", COMPANY) == ("brightline studio limited", "brightline studio ltd", "brightline studio")`);
    - `test_company_suffix_dot_is_dropped` (`"Smith & Sons Ltd."` gives `("smith & sons limited", "smith & sons ltd", "smith & sons")`);
    - `test_company_other_suffix_has_no_swap` (`"Acme Co"` gives `("acme co", "acme")`);
    - `test_company_without_suffix` (`"Acme"` gives `("acme",)`);
    - `test_empty_forms` (`name_forms("", PERSON) == ()`, `name_forms("Ltd", COMPANY) == ()` and `name_forms("Ms", PERSON) == ()`);
    - `test_forms_of_another_kind_raise` (`name_forms("a@b.com", PlaceholderKind.EMAIL)` raises `ValueError` with the message `privacy: name forms need a person or a company`);
    - `test_is_company_name` (`"Acme Ltd."` and `"Acme Co"` are companies; `"Karim Benali"` and `""` are not);
    - `test_address_forms` (`"14 Harbour Street, Leeds LS1 4AB"` gives `("14 harbour street, leeds ls1 4ab", "14 harbour street")`; `"Flat 2, 12 High Road, Leeds"` gives `("flat 2, 12 high road, leeds",)`; `"12 High Road"` gives `("12 high road",)`);
    - `test_stop_words_hold_months_and_common_names` (`{"may", "april", "monday", "will", "price"} <= NAME_STOP_WORDS`);
    - `test_common_word_names_are_not_in_the_hard_list` (`COMMON_WORD_NAMES & NAME_STOP_WORDS == frozenset()`; owner to confirm);
    - `test_is_company_seed` (`"Acme LP"`, `"Acme Pte"` and `"Acme Ltd."` are seeds; `"Karim Benali"` and `""` are not; and `is_company_name("Acme LP")` is false; owner to confirm).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_names.py` reports 14 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, system design 4.2 (the folds), Spec 4.2 (name variants).
  - **Depends on:** None

- [x] **S4-M2-T2: Patterns for email, phone, ID and bank details**
  - **Build:** In `src/clause_tracer/privacy/_patterns.py`, add these constants (each as `Final[str]`, with its `_RE` compiled as the rules say):
    ```python
    EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
    PHONE = (r"(?<![\w+])(?:\+\d{1,3}[ -]?(?:\(0\))?\d[\d -]{6,14}\d"
             r"|0\d{2,4}[ -]\d{3,4}[ -]?\d{3,4}"
             r"|\(0\d{2,4}\)[ -]?\d{3,4}[ -]?\d{3,4}"
             r"|0\d{10})(?!\w)")
    ID_KEYWORD = (r"(?i:company (?:registration )?(?:number|no\.?)|registered (?:number|no\.?)|registration (?:number|no\.?)"
                  r"|vat (?:registration )?(?:number|no\.?)|tax id)[ \t]*(?:is|:|of)?[ \t]*(?P<v>(?:GB[ ]?)?[A-Z]{0,2}\d[\d ]{3,12}\d)")
    SORT_CODE = r"(?i:sort[ ]code)[ \t]*:?[ \t]*(?P<v>\d{2}-?\d{2}-?\d{2})(?!\d)"
    ACCOUNT_NUMBER = r"(?i:account[ ](?:number|no\.?))[ \t]*:?[ \t]*(?P<v>\d{8})(?!\d)"
    ```
    The phone has four forms: international (`+44 20 7946 0958`, `+44 (0)20 7946 0958`), UK national with spaces or dashes (`020 7946 0958`), UK national with a bracketed area code (`(020) 7946 0958`) and 11 unseparated digits that start with 0 (`07700900123`). None has a cue gate: a gate on spaced national numbers leaks every bare number (report, track A1). The price is a known limit: a reference such as `ref 0123 456 7890` is also replaced (`test_a_reference_that_looks_like_a_phone_still_matches`). A keyword-gated ID or bank value and a bare phone shape can cover the same digits; `resolve_overlaps` ranks the ID or BANK first (`TIE_RANK`, defined in S4-M3-T4).
    In `src/clause_tracer/privacy/patterns.py`, add `def find_patterns(text: str) -> tuple[PiiSuggestion, ...]`. For each pair `(EMAIL_RE, EMAIL)`, `(PHONE_RE, PHONE)`, `(ID_KEYWORD_RE, ID)`, `(SORT_CODE_RE, BANK)` and `(ACCOUNT_NUMBER_RE, BANK)` (kinds are `PlaceholderKind` members), each `finditer` match gives `PiiSuggestion(span=Span(start=a, end=b), kind=kind, source=PiiSource.PATTERN)`, where `(a, b)` is `match.span("v")` for `ID_KEYWORD_RE`, `SORT_CODE_RE` and `ACCOUNT_NUMBER_RE` (the named group `v`) and `match.span()` for the other two. Return them through `unique_sorted`. An ID or a bank number covers its value only: the span of "company number 09876543" starts at "09876543", and the words "company number" stay in the text (question 5, decided by the owner on 21 Nov 2026).
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/patterns.py`, `src/clause_tracer/privacy/tests/test_patterns.py`.
  - **Tests first:** in `test_patterns.py`, each result is read as `(text[span.start:span.end], kind)`:
    - `test_finds_emails` (`"Mail a@b.com or c.d@e.org."` gives `("a@b.com", EMAIL)` at 5 to 12 and `("c.d@e.org", EMAIL)` at 16 to 25, so the final full stop is left out);
    - `test_finds_phones` (`"Call +44 20 7946 0958 or 020 7946 0958."` gives two `PHONE` spans, 5 to 21 and 25 to 38);
    - `test_finds_ids_by_keyword` (`"Our VAT number: GB123456789 and company no. 1234567."` gives two `ID` spans, 16 to 27 and 44 to 51; the plan had 4 to 27 and 32 to 51 before the value-only decision; owner to confirm);
    - `test_an_id_stops_before_a_word` (`"company number 09876543 Agency"` gives one `ID` span, 15 to 23; the plan had 0 to 23; owner to confirm);
    - `test_finds_bank_details_by_keyword` (`"sort code 12-34-56 and account number 12345678."` gives two `BANK` spans, 10 to 18 and 38 to 46; the plan had 0 to 18 and 23 to 46; owner to confirm);
    - `test_plain_numbers_are_kept` (`"Pay 5 days, £1,600 on 5 November 2026."` gives `()`, and so does `"ref 1234 5678"`);
    - `test_result_is_sorted_and_from_patterns` (`"b@x.com +44 20 7946 0958"`: two results, the email first, and every `source` is `PiiSource.PATTERN`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm):
    - `test_id_value_only_registered_number` (`"registered number SC123456"` gives `("SC123456", 18, 26, ID)`);
    - `test_bracketed_national_phone` (`"Tel: (0121) 496 0123."` gives `("(0121) 496 0123", 5, 20, PHONE)`);
    - `test_bracketed_national_phone_2` (`"Call (020) 7946 0958 now"` gives `("(020) 7946 0958", 5, 20, PHONE)`);
    - `test_unseparated_national_phone` (`"Mobile: 07700900123."` gives `("07700900123", 8, 19, PHONE)`);
    - `test_unseparated_phone_without_a_cue` (`"Use 07700900456 for support."` gives `("07700900456", 4, 15, PHONE)`);
    - `test_phone_international_with_trunk_zero` (`"Call +44 (0)20 7946 0958"` gives `("+44 (0)20 7946 0958", 5, 24, PHONE)`);
    - `test_a_reference_that_looks_like_a_phone_still_matches` (`"Quote ref 0123 456 7890 on the invoice."` gives `("0123 456 7890", 10, 23, PHONE)` (a known limit: there is no cue gate));
    - `test_not_a_phone_dates_and_clauses` (`"Clause 12.3.4 and 2026-11-21"` gives nothing);
    - `test_not_a_phone_amounts` (`"£1,600,000 and 1 234 567 8901"` gives nothing);
    - `test_not_a_phone_day_month_year` (`"due 01-02-2026"` gives nothing);
    - `test_not_a_phone_11_digits_with_a_word` (`"Order 12345678901 shipped"` gives nothing);
    - `test_keyword_values_are_not_phones` (`"sort code 12-34-56 and company number 09876543"` gives `("12-34-56", 10, 18, BANK)` and `("09876543", 38, 46, ID)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_patterns.py` reports 19 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008 (pattern recognisers sit in the code layer), Spec 4.2.
  - **Depends on:** S4-M1-T6
  - **Changed later:** S4-M2-T14 replaces the `EMAIL` line (letters and digits of any script). S4-M2-T16 changes the body of `find_patterns` (a table of checked patterns; NINO and company prefix join `_PATTERNS`).

- [x] **S4-M2-T3: IBAN with the mod-97 check**
  - **Build:** In `_patterns.py`, add `IBAN = r"(?<![A-Za-z0-9])[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,3})?(?![A-Za-z0-9])"`. In `patterns.py`, add `def iban_is_valid(candidate: str) -> bool`: remove the spaces; return `False` unless the result has 15 to 34 characters, all `str.isalnum()` and ASCII, and its first two characters are letters; move the first four characters to the end; replace each character with `str(int(character, 36))`; return `int("".join(...)) % 97 == 1`. Change `find_patterns` so that it also adds, for each `IBAN_RE` match for which `iban_is_valid(match.group())` is true, a `PiiSuggestion` of kind `BANK` and source `PATTERN`. A match that fails the check gives nothing.
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/patterns.py`, `src/clause_tracer/privacy/tests/test_iban.py`.
  - **Tests first:** in `test_iban.py`: `test_valid_iban` (`iban_is_valid("GB82 WEST 1234 5698 7654 32")` is true); `test_compact_iban_is_valid` (`"GB82WEST12345698765432"`); `test_german_iban_is_valid` (`"DE89 3704 0044 0532 0130 00"`); `test_changed_digit_is_invalid` (`"GB83 WEST 1234 5698 7654 32"` is false); `test_too_short_is_invalid` (`"GB82"` is false); `test_find_patterns_keeps_only_valid_ibans` (`"Pay to GB82 WEST 1234 5698 7654 32 or GB83 WEST 1234 5698 7654 32."` gives one `BANK` span, 7 to 34).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_iban.py src/clause_tracer/privacy/tests/test_patterns.py` reports 25 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008 (checksum patterns for bank numbers).
  - **Depends on:** S4-M2-T2

- [x] **S4-M2-T4: Typed party details and their variants**
  - **Build:** In `src/clause_tracer/privacy/party.py`: `def find_party_details(text: str, parties: Sequence[Party], terms: Sequence[DefinedTerm]) -> tuple[PiiSuggestion, ...]`. It folds `text` once (`fold_for_matching`) and, for each party in order:
    - A party whose `name.strip()` is empty raises `ValueError("privacy: party name is empty")`.
    - `kind` is `COMPANY` when `is_company_name(party.name)`, else `PERSON`. `forms` is `list(name_forms(party.name, kind))`.
    - **Short names (question 4).** `tokens` is `party.name.split()` for a company with its last token removed, and `strip_honorific(party.name.split())` for a person. A party whose name has no token left once its company suffix is removed gets no short names and raises no error. `core_words` is the set of `fold_text(token).strip(".,;:")` of the tokens, without the empty string. `full_forms` is the forms of `name_forms(party.name, kind)` that hold a space. For each `term` in `terms`, in order: `words` is `fold_text(term.term).split()` with `.,;:` stripped from each word and empty words dropped; when `words` is not empty, `set(words) <= core_words`, `fold_text(term.term)` is not already in `forms`, and some form of `full_forms` occurs as a substring of `fold_text(text[term.definition.start:term.definition.end])` (the term is defined in a sentence that also holds the party's full name), append `fold_text(term.term)` to `forms`. A term such as `Services` that is defined in a sentence without the party's name is therefore never a short name.
    - Each form gives a `PiiSuggestion(span=span, kind=kind, source=PiiSource.PARTY_DETAILS)` for each span of `find_name_form(text, key, form, NAME_STOP_WORDS, COMMON_WORD_NAMES)`.
    - When `party.address` is not `None` and `party.address.strip()` is not empty, each form of `address_forms(party.address)` gives a suggestion of kind `ADDRESS` and the same source: each form goes through `find_name_form` with the same stop words and ambiguous words as the name forms (`NAME_STOP_WORDS` and `COMMON_WORD_NAMES`).
    Return everything through `unique_sorted`.
  - **Files:** `src/clause_tracer/privacy/party.py`, `src/clause_tracer/privacy/tests/test_party.py`.
  - **Tests first:** in `test_party.py`, each result is read as `(text[span.start:span.end], kind)`, and `BRIGHTLINE = Party(name="Brightline Studio Ltd", address=None, yours=False)`:
    - `test_finds_a_company_and_its_forms` (`"Brightline Studio Ltd and brightline studio limited."` with `BRIGHTLINE`: the `COMPANY` spans `0-17`, `0-21`, `26-43`, `26-51`);
    - `test_a_name_split_by_a_line_break_is_found` (`"Brightline\nStudio Ltd"`: `COMPANY` spans `0-17` and `0-21`);
    - `test_finds_a_person_and_their_forms` (`Party(name="Karim Benali", address=None, yours=True)` over `"Signed by Karim Benali. Mr Benali agrees. Karim too."`: `PERSON` spans `10-15`, `10-22`, `16-22`, `24-33`, `27-33`, `42-47`);
    - `test_a_short_name_from_a_defined_term` (`BRIGHTLINE`, text `'Brightline Studio Ltd ("the Studio") and the Agency.'`, the terms `DefinedTerm(term="Studio", ...)` and `DefinedTerm(term="Agency", ...)`, each with `definition=Span(start=0, end=len(text))` and `uses=()`: `COMPANY` spans `0-17`, `0-21`, `11-17`, `28-34`, and nothing for `Agency`);
    - `test_a_role_is_not_a_short_name` (the same text with only the term `Agency`: only `0-17` and `0-21`);
    - `test_address_and_its_first_line` (the `ADDRESS` results only; `Party(name="X Ltd", address="14 Harbour Street, Leeds LS1 4AB", yours=False)` over `"at 14 Harbour Street, Leeds LS1 4AB; or 14 Harbour Street."`: `ADDRESS` spans `3-20`, `3-35`, `40-57`);
    - `test_no_address_when_there_is_none` (`Party(name="X Ltd", address=None, yours=False)` over `"at 14 Harbour Street."` gives `()`; a party `Party(name="X Ltd", address="  ", yours=False)` over `"x"` gives `()`);
    - `test_empty_name_raises` (`Party(name=" ", address=None, yours=False)` raises `ValueError("privacy: party name is empty")`);
    - `test_no_parties_gives_nothing` (`find_party_details("x", (), ())` is `()`);
    - `test_source_is_party_details` (every result of the first test has `source == PiiSource.PARTY_DETAILS`);
    - `test_a_term_defined_in_another_sentence_is_not_a_short_name` (`Party(name="Brightline Services Ltd", address=None, yours=False)`, text `'Brightline Services Ltd pays. "Services" means the work.'`, the term `Services` with `definition` over the text from `"Services"` to the end: `COMPANY` spans `0-19` and `0-23` only);
    - `test_a_one_word_form_needs_a_capital` (`Party(name="Karim Benali", address=None, yours=True)`, text `"karim benali signs. karim signs. Karim signs."`: `PERSON` spans `0-12` and `33-38`);
    - `test_a_month_is_not_a_name` (`Party(name="May Lee", address=None, yours=False)`, text `"Lee signed on 1 May 2026. May Lee signs."`: `PERSON` spans `0-3`, `26-33`, `30-33`);
    - `test_a_common_word_is_not_a_name` (`Party(name="Will Price", address=None, yours=False)`, text `"Will pay. Will Price signs. Price is 5."`: one `PERSON` span, `10-20`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm):
    - `test_layer3_party_rose_hope` (`Party(name="Rose Hope", address=None, yours=False)`, text `"Rose Hope signs. Hope is not a term. Contact Hope."`: `PERSON` spans `0-9`, `5-9` and `45-49`; the sentence-initial `Hope` at 17 to 21 is left, layer 3);
    - `test_hard_list_unchanged_will_price` (`Party(name="Will Price", address=None, yours=False)`, text `"Will pay. Will Price signs. Price is 5. Contact Will."`: one `PERSON` span, `10-20`; `will` and `price` stay in the hard stop list, so a bare `Contact Will` is left readable).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_party.py` reports 16 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008 (typed party details come first), Spec 4.2 (every copy of a party's name and address), [system design 15.4](../system-design.md#154-stage-4-privacy-code-finders-and-placeholders) (the 20 Nov decision on short names), questions 4 and 17 (layers 2 and 3).
  - **Depends on:** S4-M1-T6, S4-M2-T1
  - **Changed later:** S4-M2-T16 names the three parts of the short-name condition and adds the keyword-only parameter `key` to `find_party_details`.

- [x] **S4-M2-T5: Company names by suffix**
  - **Build:** In `_patterns.py`, add these constants (`H`, `WORD`, `SUFFIX_WORDS`, `SUFFIX` and `CONNECTOR` are fragments, with no `_RE`; `COMPANY` is compiled as the rules say):
    ```python
    H = r"[ \t]"
    WORD = r"[A-Z][A-Za-z0-9'’&-]*"
    SUFFIX_WORDS = r"(?:Ltd|Plc|PLC|LLC|LLP|LP|Inc|Corp|Corporation|Incorporated|GmbH|AG|SARL|SAS|BV|NV|Pty|SRL|SpA|Oy|KG|UG|Pte|Co)"
    SUFFIX = (r"(?:S\.A\.R\.L\.|L\.L\.C\.|L\.L\.P\.|P\.L\.C\.|S\.A\.|N\.V\.|B\.V\."
              rf"|Co\.?{H}+KG(?![-\w])|Pte{H}+Ltd(?![-\w])"
              rf"|Limited(?![-\w])(?!{H}+(?:Liability|Warranty|Partnership|Licen[cs]e))"
              rf"|{SUFFIX_WORDS}(?![-\w]))")
    CONNECTOR = rf"(?:GmbH(?={H}+&{H}+Co\b)|(?!(?:{SUFFIX_WORDS}|Limited)(?![-\w])){WORD}|&|of|and)"
    COMPANY = rf"(?<![\w]){WORD}(?:{H}+{CONNECTOR}){{0,5}}{H}+{SUFFIX}"
    ```
    `SUFFIX_WORDS` and `SUFFIX` are the words that end a company name. A suffix word is never a connector, so `Acme Ltd and Foo Ltd` stays two names. `Limited` is a suffix unless `Liability`, `Warranty`, `Partnership` or a licence word follows it (`Provider Limited Warranty` is no company), and a suffix that is followed by `-` or a letter is no suffix (`Co-operative`). In `src/clause_tracer/privacy/companies.py`:
    - `COMPANY_LEAD_WORDS: Final[tuple[str, ...]] = ("The", "This", "Each", "Any", "Such", "Our", "Your", "Its", "Their", "If", "Where", "Unless", "Pay", "Payment", "Notice", "Notices", "Invoice", "Deliver", "Send", "Contact", "Between", "Agreement", "Services", "Client", "Customer", "Please", "Notify", "Attention")`.
    - `COMPANY_ROLE_WORDS: Final[frozenset[str]] = frozenset({"agency", "developer", "client", "customer", "supplier", "contractor", "consultant", "company", "employer", "employee", "licensor", "licensee", "buyer", "seller", "landlord", "tenant", "party", "parties"})`.
    - `def find_companies(text: str) -> tuple[PiiSuggestion, ...]`. For each `COMPANY_RE.finditer(text)` match, `start` and `end` are the match's. `words` is the list of `(offset, word)` for each `re.finditer(r"\S+", text[start:end])` match, where `offset` is `start + match.start()`. Let `first = 0`. For `j` from 1 to `len(words) - 2`: when `words[j]` is `and` and `words[j - 1]` case-folded is in `COMPANY_ROLE_WORDS`, set `first = j + 1` (a defined role is never glued to the next name). While `first < len(words) - 1` and the word at `first` is in `COMPANY_LEAD_WORDS` or is one of `and`, `&` or `of`, add 1 to `first`. When the word at `first` is in `COMPANY_LEAD_WORDS`, or `len(words) - first < 2`, skip the match. Each kept match gives `PiiSuggestion(span=Span(start=words[first][0], end=end), kind=PlaceholderKind.COMPANY, source=PiiSource.RULE)`. Return through `unique_sorted`.
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/companies.py`, `src/clause_tracer/privacy/tests/test_companies.py`.
  - **Tests first:** in `test_companies.py`, each result is read as `(text[span.start:span.end], span.start, span.end)`:
    - `test_finds_a_company_by_its_suffix` (`"The Agency and Brightline Studio Ltd will pay Smith & Sons Ltd."` gives `("Brightline Studio Ltd", 15, 36)` and `("Smith & Sons Ltd", 46, 62)`);
    - `test_a_leading_the_is_dropped` (`"The Acme Limited pays."` gives `("Acme Limited", 4, 16)`);
    - `test_lower_case_words_before_a_name_are_left` (`"See the Acme Limited, and Bank of Wales Plc."` gives `("Acme Limited", 8, 20)` and `("Bank of Wales Plc", 26, 43)`);
    - `test_other_suffixes` (`"Acme Co. and Foo AG"` gives `("Acme Co", 0, 7)` and `("Foo AG", 13, 19)`);
    - `test_a_role_is_not_a_company` (`"The Developer pays."` gives `()`);
    - `test_a_lead_word_and_a_suffix_is_not_a_company` (`"The Ltd pays."` gives `()`);
    - `test_a_line_break_ends_the_name` (`"Brightline\nStudio Ltd"` gives `("Studio Ltd", 11, 21)`, a known limit);
    - `test_kind_and_source` (every result of the first test has kind `COMPANY` and source `RULE`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm):
    - `test_limited_warranty_is_no_company` (`"Provider Limited Warranty applies."` gives nothing);
    - `test_hyphen_word_is_no_company` (`"The Co-operative Bank Co-operation applies."` gives nothing);
    - `test_a_leading_verb_is_not_in_the_span` (`"Pay Acme Ltd now."` gives `("Acme Ltd", 4, 12)`);
    - `test_and_is_a_connector` (`"Smith and Sons Ltd"` gives `("Smith and Sons Ltd", 0, 18)`);
    - `test_dotted_forms_and_gmbh_co_kg_whole` (`"Acme Holdings Inc. and Foo S.A. and Bar GmbH & Co. KG"` gives `("Acme Holdings Inc", 0, 17)`, `("Foo S.A.", 23, 31)` and `("Bar GmbH & Co. KG", 36, 53)`);
    - `test_two_companies_joined_by_and_stay_two` (`"Acme Ltd and Foo Ltd pay"` gives `("Acme Ltd", 0, 8)` and `("Foo Ltd", 13, 20)`);
    - `test_role_and_name_are_not_glued` (`"The Agency and Brightline Studio Ltd will pay"` gives `("Brightline Studio Ltd", 15, 36)`);
    - `test_extended_suffixes_lp` (`"The Company and Acme LP sign"` gives `("Acme LP", 16, 23)`);
    - `test_extended_suffixes_corporation_incorporated` (`"Acme Corporation and Foo Incorporated"` gives `("Acme Corporation", 0, 16)` and `("Foo Incorporated", 21, 37)`);
    - `test_extended_suffixes_srl_spa_oy_ug` (`"Foo SRL, Bar SpA, Baz Oy, Qux UG"` gives `("Foo SRL", 0, 7)`, `("Bar SpA", 9, 16)`, `("Baz Oy", 18, 24)` and `("Qux UG", 26, 32)`);
    - `test_pte_ltd_whole` (`"Acme Pte Ltd pays"` gives `("Acme Pte Ltd", 0, 12)`);
    - `test_company_group_holdings_are_not_suffixes` (`"Acme Group pays Beta Holdings and Gamma Company"` gives nothing);
    - `test_comma_after_limited` (`"Acme Limited, a company, signs."` gives `("Acme Limited", 0, 12)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_companies.py` reports 21 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008 ("company-suffix rules").
  - **Depends on:** S4-M1-T6
  - **Changed later:** S4-M2-T13 replaced the `WORD` line, and S4-M2-T16 replaced it again with `rf"[{UPPER}][\w'’&-]*"`; the block above shows the first version.

- [x] **S4-M2-T6: Addresses**
  - **Build:** In `_patterns.py`, add these constants (`CAP`, `STREET_PLAIN`, `STREET_AMBIG`, `LEAD_WORD`, `POST`, `PART` and `MONTHS` are fragments, with no `_RE`; the others are compiled as the rules say). The address has two parts: a street-anchored pattern, and a chain that is built backwards from a postcode.
    ```python
    CAP = r"(?:[A-Z][a-z'’-]+|UK|USA|UAE)"
    STREET_PLAIN = r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Terrace|Gardens|Boulevard)"
    STREET_AMBIG = r"(?:Way|Place|Court|Row|Hill|Close|Drive|Square)"
    LEAD_WORD = r"(?:Rue|Avenue|Boulevard|Via|Calle|Strasse|Chemin|Allée)"
    POST = r"(?:[A-Z]{1,2}\d[A-Z\d]?[ ]?\d[A-Z]{2}|\d{4,6})"
    PART = rf",{H}*{CAP}(?:{H}+{CAP}){{0,2}}(?:{H}+{POST})?"
    ADDRESS = (
        rf"\b\d+[A-Za-z]?{H}+(?:{CAP}{H}+){{0,3}}{STREET_PLAIN}\b(?:{PART}){{0,3}}"
        rf"|\b\d+[A-Za-z]?{H}+(?:{CAP}{H}+){{1,3}}{STREET_AMBIG}\b(?:{PART}){{0,3}}"
        rf"|\b\d+[A-Za-z]?{H}+{LEAD_WORD}{H}+{CAP}(?:{H}+{CAP}){{0,3}}(?:{PART}){{0,3}}"
    )
    UK_POSTCODE = (
        r"\b(?:GIR ?0AA|[A-PR-UWYZ](?:[0-9]{1,2}|[A-HK-Y][0-9]{1,2}"
        r"|[0-9][A-HJKPSTUW]|[A-HK-Y][0-9][ABEHMNPRV-Y])[ ]?[0-9][ABD-HJLNP-UW-Z]{2})\b"
    )
    US_ZIP = (
        r"\b(?:A[LKZR]|C[AOT]|DE|FL|GA|HI|I[DLNA]|K[SY]|LA|M[EDAINSOT]|N[EVHJMYCD]"
        r"|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])"
        r"[ ]\d{5}(?:-\d{4})?\b"
    )
    CA_POSTCODE = r"\b[A-Z]\d[A-Z][ ]?\d[A-Z]\d\b"
    MONTHS = (
        r"(?:January|February|March|April|May|June"
        r"|July|August|September|October|November|December)"
    )
    START_TOKEN = (
        r"(?:Flat|Unit|Suite|Floor|Room|Building)[ ]+\w+|PO Box[ ]+\d+"
        rf"|\d+[A-Za-z]?(?:-\d+)?(?=[ ]+(?!{MONTHS}\b)[A-Z][a-z])"
    )
    CUE = (
        r"(?i:registered office (?:is )?at|registered address (?:is )?at"
        r"|address is|located at|whose address is|whose address)[ \t]+"
    )
    TAIL = (
        rf",?{H}*(?:United Kingdom|UK|England|Scotland|Wales|Northern Ireland"
        r"|USA|United States|Canada)\b"
    )
    HARD_STOP = r"[;:()\[\]\"“”\n]|[.!?](?=\s+[A-Z0-9])"
    ABBREVIATION_END = r"\b(?:St|Rd|Ave|Dr|Ln|Ct|Sq|Mt)$"
    ```
    `US_ZIP` needs a state code before the five digits, and has no DC. A bare `Way`, `Court`, `Place`, `Row`, `Hill`, `Close`, `Drive` or `Square` is a street word only after at least one capitalised word (`5 Way of life` and `2 Court days` are no address). In `src/clause_tracer/privacy/addresses.py`: `MAX_LENGTH: Final[int] = 120` and `MAX_SEGMENTS: Final[int] = 5`, and `def find_addresses(text: str) -> tuple[PiiSuggestion, ...]`. Write the functions exactly (the chain is built backwards from a UK postcode, a US ZIP or a Canadian postcode; when no start token lies before the anchor, the anchor alone is the span; when a start token lies further back than the limits, the span is a truncated chain, see `_truncated_start`):
    ```python
    def _word_start(text: str, index: int) -> bool:
        return index == 0 or not text[index - 1].isalnum()


    def _chain_start(text: str, anchor_start: int, anchor_end: int) -> int | None:
        budget = MAX_LENGTH - (anchor_end - anchor_start)
        low = max(0, anchor_start - max(budget, 0))
        window = text[low:anchor_start]
        cut = 0
        for stop in HARD_STOP_RE.finditer(window):
            if not ABBREVIATION_END_RE.search(window[: stop.start()]):
                cut = stop.end()
        base = low + cut
        segments: list[tuple[int, str]] = []
        position = 0
        for part in text[base:anchor_start].split(","):
            segments.append((base + position, part))
            position += len(part) + 1
        segments = segments[-MAX_SEGMENTS:]
        candidates: list[int] = []
        for index, (segment_start, segment) in enumerate(segments):
            found = [
                m
                for m in START_TOKEN_RE.finditer(segment)
                if _word_start(text, segment_start + m.start())
                and (segment_start + m.start() > low or low == 0 or not text[low - 1].isalnum())
            ]
            if found:
                match = found[-1] if index == 0 else found[0]
                candidates.append(segment_start + match.start())
                break
        first_start = segments[0][0] if segments else base
        cues = list(CUE_RE.finditer(text[first_start:anchor_start]))
        if cues:
            candidates.append(first_start + cues[-1].end())
        if candidates:
            return min(candidates)
        return _truncated_start(text, anchor_start, anchor_end)


    def _truncated_start(text: str, anchor_start: int, anchor_end: int) -> int | None:
        base = 0
        for stop in HARD_STOP_RE.finditer(text, 0, anchor_start):
            if not ABBREVIATION_END_RE.search(text[max(0, stop.start() - 4) : stop.start()]):
                base = stop.end()
        region = text[base:anchor_start]
        has_start = CUE_RE.search(region) is not None or any(
            _word_start(text, base + m.start()) for m in START_TOKEN_RE.finditer(region)
        )
        if not has_start:
            return None
        starts: list[int] = []
        position = 0
        for part in region.split(","):
            starts.append(base + position + len(part) - len(part.lstrip(" \t")))
            position += len(part) + 1
        for start in starts[-MAX_SEGMENTS:]:
            if anchor_end - start <= MAX_LENGTH:
                return start
        return None


    def find_addresses(text: str) -> tuple[PiiSuggestion, ...]:
        spans = [(m.start(), m.end()) for m in ADDRESS_RE.finditer(text)]
        for pattern in (UK_POSTCODE_RE, US_ZIP_RE, CA_POSTCODE_RE):
            for anchor in pattern.finditer(text):
                end = anchor.end()
                tail = TAIL_RE.match(text, end)
                if tail:
                    end = tail.end()
                start = _chain_start(text, anchor.start(), end)
                spans.append((anchor.start() if start is None else start, end))
        spans.sort()
        merged: list[tuple[int, int]] = []
        for start, end in spans:
            if merged and start < merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return unique_sorted(
            PiiSuggestion(
                span=Span(start=s, end=e), kind=PlaceholderKind.ADDRESS, source=PiiSource.RULE
            )
            for s, e in merged
        )
    ```
    The address runs from the house number, the unit word, or the end of a cue phrase, to the last town, postcode or country joined by commas (question 3). If the start token or the cue lies more than 5 comma segments or more than 120 characters before the postcode (but after the last hard stop), the span is a truncated chain (owner, 22 Nov 2026, question 23): `_truncated_start` returns the start of the earliest comma segment, with its leading blanks skipped, that keeps the chain within 5 segments and 120 characters up to the end of the span (the span includes an optional trailing country; the count of segments is the one of `_chain_start`, so the segment of the town before a postcode that follows a comma counts). The nearest part of the address before the postcode is hidden and the earlier part stays readable. A truncated chain never crosses a hard stop. If no start token and no cue lies before the postcode, or if not even the nearest segment fits in 120 characters, the postcode alone is the span.
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/addresses.py`, `src/clause_tracer/privacy/tests/test_addresses.py`.
  - **Tests first:** in `test_addresses.py`, each result is read as `(span.start, span.end)`:
    - `test_uk_address` (`"Send it to 221B Baker Street, London NW1 6XE."` gives `((11, 44),)`);
    - `test_street_with_and_without_a_town` (`"at 5 High Road and 10 Downing Street, London, UK."` gives `((3, 14), (19, 48))`);
    - `test_us_style_address` (`"1 Main St, Springfield 12345, USA"` gives `((0, 33),)`);
    - `test_street_word_first_address` (`"27 Rue Didouche Mourad, Algiers 16000, Algeria"` gives `((0, 46),)`);
    - `test_amounts_and_durations_are_kept` (`"in 12 months, Leeds"` gives `()`, and so does `"Week 2 £1,600"`);
    - `test_a_bracket_ends_the_address` (`'14 Harbour Street, Leeds LS1 4AB ("the Agency")'` gives `((0, 32),)`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm; each result is read as the text of each span):
    - `test_postcode_after_a_comma` (`"Send it to 12 High Road, Leeds, LS1 4AB today."` gives `"12 High Road, Leeds, LS1 4AB"`);
    - `test_bare_way_is_no_address` (`"Keep 5 Way clear."` gives nothing);
    - `test_bare_court_is_no_address` (`"Keep 2 Court clear."` gives nothing);
    - `test_way_of_life` (`"at 5 Way of life"` gives nothing);
    - `test_court_days` (`"within 2 Court days"` gives nothing);
    - `test_us_suite_whole` (`"Deliver to Suite 400, 1 Main Street, Austin, TX 78701 by June."` gives `"Suite 400, 1 Main Street, Austin, TX 78701"`);
    - `test_flat_chain_with_country` (`"Flat 2, 12 High Road, Leeds, LS1 4AB, United Kingdom"` gives `"Flat 2, 12 High Road, Leeds, LS1 4AB, United Kingdom"`);
    - `test_unit_without_a_street_word` (`"Unit 4, Alpha Park, Leeds, LS1 4AB"` gives `"Unit 4, Alpha Park, Leeds, LS1 4AB"`);
    - `test_us_state_zip_usa` (`"Suite 400, 1 Main St, Springfield, IL 62704, USA"` gives `"Suite 400, 1 Main St, Springfield, IL 62704, USA"`);
    - `test_a_date_is_no_house_number_postcode_alone` (`"Within 30 days of 1 May 2026, ship to LS1 4AB"` gives `"LS1 4AB"`);
    - `test_previous_sentence_is_cut_off` (`"Pay 5 apples to Bob. He lives at 5 High St, Leeds LS1 4AB"` gives `"5 High St, Leeds LS1 4AB"`);
    - `test_canadian_postcode` (`"Ship to 100 King Street, Toronto, ON M5V 3L9, Canada"` gives `"100 King Street, Toronto, ON M5V 3L9, Canada"`);
    - `test_po_box` (`"PO Box 12, Leeds LS1 4AB"` gives `"PO Box 12, Leeds LS1 4AB"`);
    - `test_no_start_token_postcode_alone` (`"Alpha Park, Leeds LS1 4AB"` gives `"LS1 4AB"`);
    - `test_cue_phrase_starts_the_address` (`"whose address is Alpha House, 4 Mill Lane, Leeds LS1 4AB"` gives `"Alpha House, 4 Mill Lane, Leeds LS1 4AB"`);
    - `test_semicolon_ends_the_chain` (`"Pay Bob; 5 High St, Leeds LS1 4AB"` gives `"5 High St, Leeds LS1 4AB"`);
    - `test_address_chain_with_7_segments_keeps_the_last_5_segments` (`"Mail 1 Aaaa, Bbbb, Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB"` gives `"Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB"`; the plan of 21 Nov 2026 had `"LS1 4AB"`, owner decision of 22 Nov 2026, question 23);
    - `test_address_chain_with_exactly_5_segments_is_whole` (`"Mail 1 Aaaa, Bbbb, Cccc, Dddd, Leeds LS1 4AB"` gives `"1 Aaaa, Bbbb, Cccc, Dddd, Leeds LS1 4AB"`);
    - `test_address_chain_over_120_characters_keeps_the_nearest_segments` (`"Mail 1 Aaaa, " + "B" * 100 + ", Cccc, Leeds LS1 4AB"` gives `"Cccc, Leeds LS1 4AB"`; the chain from the `B` segment would be 121 characters);
    - `test_nearest_segment_over_120_characters_gives_the_postcode_alone` (`"Mail 1 Aaaa, " + "Bbbb " * 25 + "Leeds LS1 4AB"` gives `"LS1 4AB"`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_addresses.py` reports 26 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008 ("address rules").
  - **Depends on:** S4-M2-T5
  - **Changed later:** S4-M2-T14 replaces the `CAP` line (Latin-1 capitals and letters). `US_ZIP` is unchanged by the owner's decision of 22 Nov 2026: a state code that is also a word, such as `ID 12345`, is still read as a ZIP.

- [x] **S4-M2-T7: People by honorific, signature and job title**
  - **Build:** In `_patterns.py`, add these constants (`PARTICLE`, `TOK`, `INIT`, `NAME_RUN`, `ONE_OR_TWO`, `CAPS_TOK`, `CAPS_RUN`, `CAPS_ONE_OR_TWO` and `TITLE_WORDS` are fragments, with no `_RE`; the other five are compiled as the rules say). `TOK` is one name token: it keeps `O'Brien`, `McDonald`, `Smith-Jones` and `al-Rahman` whole. `NAME_RUN` is 2 to 4 tokens, with initials (`J.`) and particles (`de`, `ben`) allowed between them.
    ```python
    PARTICLE = r"(?:van|von|der|den|de|la|le|da|di|del|bin|ibn|bint|ben|ould|dos|du|al|el)"
    TOK = r"(?:[A-Z](?:['’][A-Z])?[a-z]+(?:[A-Z][a-z]+)*(?:-[A-Z]?[a-z]+)*|(?:al|el)-[A-Z][a-z]+)"
    INIT = r"(?:[A-Z]\.)"
    NAME_RUN = rf"{TOK}(?:{H}+(?:{INIT}{H}+|{PARTICLE}{H}+)*{TOK}){{1,3}}"
    ONE_OR_TWO = rf"{TOK}(?:{H}+(?:{INIT}{H}+|{PARTICLE}{H}+)*{TOK})?"
    CAPS_TOK = r"[A-Z]{2,}(?:['’-][A-Z]+)*"
    CAPS_RUN = rf"{CAPS_TOK}(?:{H}+{CAPS_TOK}){{1,2}}"
    CAPS_ONE_OR_TWO = rf"{CAPS_TOK}(?:{H}+{CAPS_TOK})?"
    TITLE_WORDS = r"(?:Managing Director|Director|Manager|Partner|Owner|Secretary|Chief Executive Officer|CEO|CFO|Chairman|President)"
    HONORIFIC_PERSON = rf"\b(?:Mr|Mrs|Ms|Miss|Mx|Dr)\.?{H}+({ONE_OR_TWO})"
    HONORIFIC_PERSON_CAPS = rf"\b(?:MR|MRS|MS|MISS|MX|DR)\.?{H}+({CAPS_ONE_OR_TWO})"
    SIGNED_BY = rf"\b(?:Signed|Executed)\b[^.\n]*?\bby{H}+({NAME_RUN})"
    SIGNED_BY_CAPS = rf"(?i:signed|executed)\b[^.\n]*?\b(?i:by){H}+({CAPS_RUN})"
    NAME_BEFORE_TITLE = rf"({NAME_RUN}){H}*,{H}*{TITLE_WORDS}\b"
    ```
    In `src/clause_tracer/privacy/people.py`, three word lists (the owner reads them with the plan: question 16):
    - `LEGAL_STOP_WORDS: Final[frozenset[str]] = frozenset({"agreement", "party", "parties", "schedule", "clause", "section", "annex", "appendix", "exhibit", "services", "service", "client", "customer", "supplier", "contractor", "consultant", "developer", "agency", "company", "employer", "employee", "licensor", "licensee", "buyer", "seller", "landlord", "tenant", "charges", "deliverables", "milestone", "effective", "date", "term", "confidential", "information", "intellectual", "property", "governing", "law", "force", "majeure", "termination", "payment", "fees", "notice", "notices", "director", "manager", "partner", "owner", "secretary"})`.
    - `TRAILING_TITLE_WORDS: Final[frozenset[str]] = frozenset({"director", "manager", "partner", "owner", "secretary", "ceo", "cfo", "chairman", "president", "managing", "chief", "executive", "officer"})`.
    - `LEAD_STOP_WORDS: Final[frozenset[str]] = frozenset(word.casefold() for word in COMPANY_LEAD_WORDS) | frozenset({"by", "for", "and", "of"})` (`COMPANY_LEAD_WORDS` is imported from `companies.py`, S4-M2-T5).
    Then `def find_people(text: str) -> tuple[PiiSuggestion, ...]`, with `key = fold_for_matching(text)`.
    - **Step 1, seeds.** The five pairs `(HONORIFIC_PERSON_RE, True)`, `(HONORIFIC_PERSON_CAPS_RE, True)`, `(SIGNED_BY_RE, False)`, `(SIGNED_BY_CAPS_RE, False)` and `(NAME_BEFORE_TITLE_RE, False)` run in that order, each over `finditer`. The second item of a pair says whether the match starts at an honorific. For each match, `_clean_seed(match, honorific)` (below) gives `(start, end, seed)` or `None`; a `None` gives nothing, no suggestion and no seed. A kept result gives the span `Span(start=start, end=end)` and the seed `seed`. Every kept span is added as a suggestion of kind `PERSON` and source `RULE`. For an honorific match the span starts at the honorific, and the seed text starts at the name.
    - **Step 2, variants.** For each distinct `fold_text(seed)` (kept in the order found), and each form of `name_forms(<that folded seed>, PlaceholderKind.PERSON)`, each span of `find_name_form(text, key, form, NAME_STOP_WORDS, COMMON_WORD_NAMES)` is a suggestion too.
    Every suggestion has kind `PERSON` and source `RULE`. Return through `unique_sorted`. The finder is the only way code alone finds a person who is not a typed party (question 1). Write `_clean_seed` exactly:
    ```python
    def _clean_seed(match: re.Match[str], honorific: bool) -> tuple[int, int, str] | None:
        group_start = match.start(1)
        tokens = [(group_start + t.start(), group_start + t.end(), t.group()) for t in re.finditer(r"\S+", match.group(1))]

        def key(token: tuple[int, int, str]) -> str:
            return token[2].strip(".,;:").casefold()

        while tokens and key(tokens[0]) in LEAD_STOP_WORDS:
            tokens = tokens[1:]
        while tokens and (key(tokens[-1]) in TRAILING_TITLE_WORDS or key(tokens[-1]) in LEGAL_STOP_WORDS):
            tokens = tokens[:-1]
        if not tokens:
            return None
        if all(key(token) in LEGAL_STOP_WORDS for token in tokens):
            return None
        if not honorific and len(tokens) < 2:
            return None
        if is_company_seed(" ".join(token[2] for token in tokens)):
            return None
        first, last = tokens[0][0], tokens[-1][1]
        return (match.start() if honorific else first), last, match.string[first:last]
    ```
    A seed that is a company (`Signed by Acme Holdings Limited`) gives no person: `find_companies` finds it. A seed made only of legal words (`Signed by Party Schedule`) gives nothing. A trailing job title or legal word is cut off (`Pat Kelly Director`, `Ms Jones Agreement`).
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/people.py`, `src/clause_tracer/privacy/tests/test_people.py`.
  - **Tests first:** in `test_people.py`, each result is read as `(text[span.start:span.end], span.start, span.end)`:
    - `test_honorific_and_surname` (`"Ms Jones at home. Jones left."` gives `("Ms Jones", 0, 8)`, `("Jones", 3, 8)`, `("Jones", 18, 23)`);
    - `test_signature_line` (`"Executed as a deed by Anna Lee Smith"` gives `("Anna", 22, 26)`, `("Anna Lee Smith", 22, 36)`, `("Smith", 31, 36)`);
    - `test_name_before_a_job_title` (`"Signed by Pat Kelly, Managing Director."` gives `("Pat", 10, 13)`, `("Pat Kelly", 10, 19)`, `("Kelly", 14, 19)`; the plan's first sentence, `"Pat Kelly, Managing Director, signed."`, gives only `("Pat Kelly", 0, 9)` and `("Kelly", 4, 9)` now, because `pat` is a layer 3 word at the start of the text);
    - `test_variants_are_found_elsewhere` (`"Signed by Sarah Jones. Hi Sarah, see Ms Jones."` gives `("Sarah", 10, 15)`, `("Sarah Jones", 10, 21)`, `("Jones", 16, 21)`, `("Sarah", 26, 31)`, `("Ms Jones", 37, 45)`, `("Jones", 40, 45)`);
    - `test_the_first_by_names_the_signer` (`"Signed for Acme Ltd by Tom Jones, Director"` gives `("Tom", 23, 26)`, `("Tom Jones", 23, 32)`, `("Jones", 27, 32)`);
    - `test_lower_case_words_are_not_names` (`"signed by the board"` gives `()`);
    - `test_kind_and_source` (every result of the first test has kind `PERSON` and source `RULE`);
    - `test_a_company_signature_is_not_a_person` (`"Signed by Acme Holdings Limited"` gives `()`);
    - `test_a_month_after_an_honorific_leaves_dates_alone` (`"Ms May signs on 1 May 2026."` gives only `("Ms May", 0, 6)`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm):
    - `test_o_brien` (`"Signed by Sean O'Brien."` gives `("Sean", 10, 14)`, `("Sean O'Brien", 10, 22)` and `("O'Brien", 15, 22)`);
    - `test_o_brien_curly` (`"Signed by Sean O’Brien."` gives `("Sean", 10, 14)`, `("Sean O’Brien", 10, 22)` and `("O’Brien", 15, 22)`);
    - `test_mc_donald` (`"Signed by Ann McDonald."` gives `("Ann", 10, 13)`, `("Ann McDonald", 10, 22)` and `("McDonald", 14, 22)`);
    - `test_hyphen_surname` (`"Signed by Ana Smith-Jones."` gives `("Ana", 10, 13)`, `("Ana Smith-Jones", 10, 25)` and `("Smith-Jones", 14, 25)`);
    - `test_capitals_signature` (`"SIGNED BY SARAH JONES."` gives `("SARAH", 10, 15)`, `("SARAH JONES", 10, 21)` and `("JONES", 16, 21)`);
    - `test_initial` (`"Signed by Sarah J. Jones."` gives `("Sarah", 10, 15)`, `("Sarah J. Jones", 10, 24)` and `("Jones", 19, 24)`);
    - `test_particles` (`"Signed by Maria de la Cruz."` gives `("Maria", 10, 15)`, `("Maria de la Cruz", 10, 26)` and `("Cruz", 22, 26)`);
    - `test_ben_ali` (`"Signed by Mohamed ben Ali."` gives `("Mohamed", 10, 17)`, `("Mohamed ben Ali", 10, 25)` and `("Ali", 22, 25)`);
    - `test_al_rahman` (`"Signed by Abd al-Rahman Saidi."` gives `("Abd", 10, 13)`, `("Abd al-Rahman Saidi", 10, 29)` and `("Saidi", 24, 29)`);
    - `test_trailing_title_without_comma` (`"Signed by Pat Kelly Director"` gives `("Pat", 10, 13)`, `("Pat Kelly", 10, 19)` and `("Kelly", 14, 19)`);
    - `test_capitals_honorific` (`"MS JONES signs."` gives `("MS JONES", 0, 8)` and `("JONES", 3, 8)`);
    - `test_legal_words_are_no_name` (`"Signed by Party Schedule."` gives nothing);
    - `test_capitals_legal_words_are_no_name` (`"SIGNED BY AGREEMENT PARTY"` gives nothing);
    - `test_trailing_legal_word_is_trimmed` (`"Ms Jones Agreement"` gives `("Ms Jones", 0, 8)` and `("Jones", 3, 8)`);
    - `test_layer3_pat_at_a_sentence_start_is_left` (`"Pat Kelly, Managing Director, signed."` gives `("Pat Kelly", 0, 9)` and `("Kelly", 4, 9)`);
    - `test_layer3_unambiguous_surname_replaced_at_a_sentence_start` (`"Signed by Sarah Jones. Jones shall pay."` gives `("Sarah", 10, 15)`, `("Sarah Jones", 10, 21)`, `("Jones", 16, 21)` and `("Jones", 23, 28)`);
    - `test_layer4_is_off` (`"Signed by Tim Brown. Contact Brown. The brown fox."` gives `("Tim", 10, 13)`, `("Tim Brown", 10, 19)`, `("Brown", 14, 19)` and `("Brown", 29, 34)`: the later capitalised `Brown` stays a name, and the lower-case `brown` stays readable).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_people.py` reports 26 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008, Spec 4.2 ("Ms. Jones" and "Sarah" are variants), questions 1 and 17.
  - **Depends on:** S4-M1-T6, S4-M2-T1, S4-M2-T5
  - **Changed later:** S4-M2-T14 replaces `TOK`, `INIT` and `CAPS_TOK` (Latin-1 capitals and letters). S4-M2-T16 builds `LEGAL_STOP_WORDS` from `COMPANY_ROLE_WORDS` (same 51 words), removes the all-legal-words check of `_clean_seed` (it can never run), and adds the keyword-only parameter `key` to `find_people`.

- [x] **S4-M2-T8: The finders table (Owner)**
  - **Build:** Owner only. The owner fills `src/clause_tracer/privacy/tests/tables/finders.toml` with rows in this format (the agent does not write or change them, Constitution T11):
    ```toml
    [[case]]
    id = "email-before-a-full-stop"
    finder = "patterns"          # one of: patterns, companies, addresses, people
    text = "Mail a@b.com."
    found = [
      { text = "a@b.com", kind = "email" },     # nth is optional and defaults to 1
    ]
    ```
    `found` lists, in order of start, every result the finder must return: the text, the `kind` (a `PlaceholderKind` value), and `nth` (the number of the occurrence of that text, from 1) when the text occurs twice. An empty list means the finder returns nothing. The table needs at least 24 rows and at least 4 rows for each of the four finders. The owner should cover: each `patterns` kind, a phone-like date, a number inside a word, a company with and without a suffix, a role that looks like a name, an address with and without a postcode, a street-word address, a person by honorific, by signature and by job title, and a name split by a line break.
  - **Files:** `src/clause_tracer/privacy/tests/tables/finders.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** Constitution T11, testing strategy 10.
  - **Depends on:** None

- [x] **S4-M2-T9: The party details table (Owner)**
  - **Build:** Owner only. The owner fills `src/clause_tracer/privacy/tests/tables/party_details.toml`, in this format:
    ```toml
    [[case]]
    id = "company-and-its-short-name"
    parties = [ { name = "Brightline Studio Ltd", yours = false } ]   # address is optional
    terms = [ "Studio" ]   # optional; a string is a term whose definition is the whole text, a table gives the text of the defining sentence
    text = 'Brightline Studio Ltd pays.'
    found = [ { text = "Brightline Studio", kind = "company" }, { text = "Brightline Studio Ltd", kind = "company" }, { text = "Studio", kind = "company" } ]   # as in finders.toml; every result has source party_details
    ```
    The example row proves that a defined term made of the company's own words (`Studio`) is found as a short name, next to the full name and the core name.
    The table needs at least 10 rows. The owner should cover: a company and its other-suffix spelling, a month or a common word as a name, a term defined in another sentence, a person and their honorific form, a one-word name, a short name from a defined term, a role that is not a short name, an address and its first line, a party with no address, and a name that wraps over a line break.
  - **Files:** `src/clause_tracer/privacy/tests/tables/party_details.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** Constitution T11.
  - **Depends on:** None

- [x] **S4-M2-T10: Table tests for the finders and the party details**
  - **Build:** In `src/clause_tracer/privacy/tests/test_finder_tables.py`, read `finders.toml` and `party_details.toml` with `load_table` (allowed and required keys for `finders.toml`: `id`, `finder`, `text`, `found`; for `party_details.toml`, allowed `id`, `parties`, `terms`, `text`, `found` and required `id`, `parties`, `text`, `found`). The module-level maps are `FINDERS: Final[Mapping[str, Callable[[str], tuple[PiiSuggestion, ...]]]] = {"patterns": find_patterns, "companies": find_companies, "addresses": find_addresses, "people": find_people}` and `SOURCES = {"patterns": PiiSource.PATTERN, "companies": PiiSource.RULE, "addresses": PiiSource.RULE, "people": PiiSource.RULE}`. An expected row `{text, kind, nth}` becomes `PiiSuggestion(span=span_of(case_text, text, nth), kind=as_enum(PlaceholderKind, kind, "kind"), source=<the source>)`. A `finder` name that is not a key of `FINDERS` raises `ValueError`.
  - **Files:** `src/clause_tracer/privacy/tests/test_finder_tables.py`.
  - **Tests first:** `test_finder_table` (parametrised over the rows of `finders.toml`, by `id`: the finder's result equals the expected tuple); `test_finder_table_has_rows` (at least 24 rows, and at least 4 for each of the four finder names); `test_party_table` (parametrised over `party_details.toml`: `find_party_details(text, parties, terms)` equals the expected tuple with source `PARTY_DETAILS`; each party is built as `Party(name=..., address=... or None, yours=...)`, and each term row as `DefinedTerm(term=row, definition=Span(start=0, end=len(text)), uses=())` when it is a string, or `DefinedTerm(term=row["term"], definition=span_of(text, row["definition"]), uses=())` when it is a table); `test_party_table_has_rows` (at least 10 rows).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_finder_tables.py` shows no failed test and the two has-rows tests pass, and `scripts/check.sh` exits 0. With zero rows, the has-rows tests fail and the parametrised tests skip, so this task is done only when the owner tables of S4-M2-T8 and S4-M2-T9 hold rows; until then it waits (plans README rule: continue with tasks that do not depend on it). If a row fails, the code or the row is wrong: bring it to the owner, and never edit the table. The row `company-with-a-foreign-suffix` passes after S4-M2-T13; build T13 before you commit or tick this task.
  - **Rules:** Constitution T11, testing strategy 10.
  - **Depends on:** S4-M1-T5, S4-M2-T3, S4-M2-T4, S4-M2-T5, S4-M2-T6, S4-M2-T7, S4-M2-T8, S4-M2-T9

- [x] **S4-M2-T11: The governing-law place list (Owner)**
  - **Build:** Owner only (Constitution T11, question 16: a word list is the owner's). The owner writes `src/clause_tracer/privacy/_place_list.py`, holding exactly these six constants, each `Final[tuple[str, ...]]`, and nothing else but the imports `from typing import Final` and a module docstring. The agent does not write or change this file, and does not add a name to it. The list is closed (owner decision of 21 Nov 2026, [report](../../reports/Privacy%20finder%20design%20choices.md#owner-decisions-of-21-and-22-nov-2026), decision 1; [Spec 4.2](../spec.md#42-privacy-check)): a place is kept only when it is a country, a nation of the United Kingdom ("England and Wales" is one entry), a US state, a Canadian province or an Australian state.
    - `COUNTRIES`: countries named by one word, and `COUNTRIES_MULTI`: countries and short forms named by more than one word, or by an abbreviation (`UK`, `USA`, `UAE`).
    - `UK_NATIONS`: `England and Wales`, `England & Wales`, `England`, `Wales`, `Scotland`, `Northern Ireland`.
    - `US_STATES`, `CA_PROVINCES` (and territories) and `AU_STATES` (and territories).
    **Proposal for the owner, not code to copy.** The planner took the lists below from the reference code that computed the expected values of S4-M3-T3. The country lists (131 one-word names and 20 other names and short forms: 151 in all) are the planner's draft and the owner must review them (open question 20); the other four follow the owner's five categories. Jersey, Guernsey, the Isle of Man, Hong Kong, the District of Columbia and `Washington, D.C.` are not in it (open question 20). The owner may take, change or reject any name. A change to a name changes the tests of S4-M3-T3 that name it, in a commit of its own (Constitution T11).
    ```python
    COUNTRIES: Final[tuple[str, ...]] = (
        "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia",
        "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
        "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia", "Botswana", "Brazil", "Brunei", "Bulgaria",
        "Cambodia", "Cameroon", "Canada", "Chile", "China", "Colombia", "Croatia", "Cuba", "Cyprus",
        "Czechia", "Denmark", "Ecuador", "Egypt", "Estonia", "Ethiopia", "Fiji", "Finland", "France",
        "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Guatemala", "Guyana", "Haiti", "Honduras",
        "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
        "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Latvia", "Lebanon", "Liberia",
        "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
        "Maldives", "Mali", "Malta", "Mauritius", "Mexico", "Moldova", "Monaco", "Mongolia",
        "Montenegro", "Morocco", "Mozambique", "Namibia", "Nepal", "Netherlands", "Nicaragua",
        "Nigeria", "Norway", "Oman", "Pakistan", "Panama", "Paraguay", "Peru", "Philippines", "Poland",
        "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Senegal", "Serbia", "Singapore",
        "Slovakia", "Slovenia", "Somalia", "Spain", "Sudan", "Sweden", "Switzerland", "Syria",
        "Taiwan", "Tanzania", "Thailand", "Tunisia", "Turkey", "Uganda", "Ukraine", "Uruguay",
        "Uzbekistan", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe",
    )
    COUNTRIES_MULTI: Final[tuple[str, ...]] = (
        "Costa Rica", "Dominican Republic", "El Salvador", "New Zealand", "Saudi Arabia",
        "South Africa", "South Korea", "North Korea", "Sri Lanka", "United Arab Emirates",
        "United Kingdom", "United States of America", "United States", "Papua New Guinea",
        "Trinidad and Tobago", "Czech Republic", "North Macedonia", "UAE", "UK", "USA",
    )
    UK_NATIONS: Final[tuple[str, ...]] = (
        "England and Wales", "England & Wales", "England", "Wales", "Scotland", "Northern Ireland",
    )
    US_STATES: Final[tuple[str, ...]] = (
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
        "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
        "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
        "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
        "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
    )
    CA_PROVINCES: Final[tuple[str, ...]] = (
        "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
        "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan",
        "Northwest Territories", "Nunavut", "Yukon",
    )
    AU_STATES: Final[tuple[str, ...]] = (
        "New South Wales", "Victoria", "Queensland", "South Australia", "Western Australia",
        "Tasmania", "Australian Capital Territory", "Northern Territory",
    )
    ```
  - **Files:** `src/clause_tracer/privacy/_place_list.py`.
  - **Tests first:** None. The owner's list is the expected answer.
  - **Done when:** The owner has written the file and said so. `scripts/check.sh` exits 0 with the file in place.
  - **Rules:** Constitution T11, Spec 4.2 (the kept place), question 14.
  - **Depends on:** None

- [x] **S4-M2-T12: Bare identifiers: NINO, card, GB VAT, company prefix**
  - **Build:** The owner decided on 22 Nov 2026 (question 24) that stage 4 also finds four identifiers that need no keyword. Each covers the whole match (there is no keyword to leave out, so the whole identifier is the value), has the source `PATTERN`, and is added to `find_patterns` before `unique_sorted`. A UK National Insurance number (NINO), a GB VAT number and a UK company number with a prefix give kind `ID`. A card number gives kind `BANK` (Spec 4.2, "bank numbers"; question 26 asks the owner to confirm it). A pattern that a checksum or a fixed prefix already makes strong has no cue gate (owner decision of 22 Nov 2026). Only the card number has a gate (below).
    In `src/clause_tracer/privacy/_patterns.py`, after `IBAN`, add these constants. `NINO`, `GB_VAT`, `COMPANY_PREFIX`, `CARD` and `CARD_CUE` are patterns: each also gets a `_RE` compiled as the rules say. `CARD_CUE_WINDOW`, `CARD_FIRST_DIGITS` and `GB_VAT_WEIGHTS` are plain values and get none:
    ```python
    NINO: Final[str] = (
        r"\b(?!BG|GB|NK|KN|NT|TN|ZZ)[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]"
        r"(?:[ ]?\d{2}){3}[ ]?[A-D]\b"
    )
    GB_VAT: Final[str] = r"(?<![A-Za-z0-9])GB[ ]?\d{3}[ ]?\d{4}[ ]?\d{2}(?:[ ]?\d{3})?(?![A-Za-z0-9])"
    COMPANY_PREFIX: Final[str] = (
        r"(?<![A-Za-z0-9])(?:SC|NI|OC|SO|NC|LP|SL|NL|FC|R0|IP|SP|RS|CE|NP)\d{6}(?![A-Za-z0-9])"
    )
    CARD: Final[str] = r"(?<![\d-])\d{4}(?:[ -]?\d{4}){2}[ -]?\d{1,7}(?![\d-])"
    CARD_CUE: Final[str] = r"(?i:\b(?:card|visa|mastercard|amex)\b)"
    CARD_CUE_WINDOW: Final[int] = 40
    CARD_FIRST_DIGITS: Final[str] = "3456"
    GB_VAT_WEIGHTS: Final[tuple[int, ...]] = (8, 7, 6, 5, 4, 3, 2, 10, 1)
    ```
    - `NINO` follows the HMRC prefix rules as the report gives them (Q15 and the notes): no prefix `BG`, `GB`, `NK`, `KN`, `NT`, `TN` or `ZZ`; a first letter that is not `D`, `F`, `I`, `Q`, `U` or `V`; a second letter that is not `D`, `F`, `I`, `O`, `Q`, `U` or `V`; three pairs of digits with an optional space before each pair; an optional space; a suffix letter `A` to `D`; and a word boundary on both sides. It is upper case only.
    - `GB_VAT` is `GB`, then 3, 4 and 2 digits with an optional space before each group, then an optional group of 3 digits (the branch), and no letter or digit on either side.
    - `COMPANY_PREFIX` is one of the 15 prefixes of report Q15 (`SC`, `NI`, `OC`, `SO`, `NC`, `LP`, `SL`, `NL`, `FC`, `R0`, `IP`, `SP`, `RS`, `CE`, `NP`) and exactly 6 digits, with no letter or digit on either side. `BR` and `OE` (the notes' line 13) are not built. A bare 8-digit number has no prefix and still needs a keyword (`ID_KEYWORD`).
    - `CARD` is 13 to 19 digits in groups of 4 (the last group holds 1 to 7 digits), with an optional space or hyphen between groups, and no digit or hyphen on either side. A card in 4-6-5 spacing (`3782 822463 10005`) is not found; the same card with no spaces is.
    In `src/clause_tracer/privacy/patterns.py`, add these four functions (the checksum helpers sit beside `iban_is_valid`, which S4-M2-T3 puts in this file):
    ```python
    def luhn_is_valid(digits: str) -> bool:
        if not digits or not digits.isdecimal():
            return False
        total = 0
        for index, character in enumerate(reversed(digits)):
            value = int(character)
            if index % 2 == 1:
                value *= 2
                if value > 9:
                    value -= 9
            total += value
        return total % 10 == 0


    def gb_vat_is_valid(candidate: str) -> bool:
        digits = "".join(character for character in candidate if character.isdecimal())
        if len(digits) not in (9, 12):
            return False
        weighted = zip(GB_VAT_WEIGHTS, digits[:9], strict=True)
        remainder = sum(weight * int(digit) for weight, digit in weighted) % 97
        has_high_start = int(digits[:3]) >= 100
        return remainder == 0 or (has_high_start and remainder in (42, 55))


    def has_card_cue(text: str, start: int) -> bool:
        return CARD_CUE_RE.search(text, max(0, start - CARD_CUE_WINDOW), start) is not None


    def card_is_valid(text: str, match: re.Match[str]) -> bool:
        digits = "".join(character for character in match.group() if character.isdecimal())
        has_card_length = 13 <= len(digits) <= 19
        has_issuer_digit = digits[0] in CARD_FIRST_DIGITS
        return (
            has_card_length
            and luhn_is_valid(digits)
            and (has_issuer_digit or has_card_cue(text, match.start()))
        )
    ```
    - `luhn_is_valid(digits)`: from the right, double every second digit, subtract 9 from a doubled value above 9, and add all. It is true when the sum is a multiple of 10. It is false for an empty string and for any string that is not all `str.isdecimal()` characters.
    - `gb_vat_is_valid(candidate)`: keep the `str.isdecimal()` characters of `candidate` (so the `GB` and the spaces fall away). It is false unless 9 or 12 digits remain. Multiply the first 9 digits by the weights `8, 7, 6, 5, 4, 3, 2, 10, 1` and add. The number is valid when the sum modulo 97 is 0, or when the first three digits are 100 or more and the sum modulo 97 is 42 or 55 (the python-stdnum rule, restated here; the library is LGPL, so no file is copied).
    - `has_card_cue(text, start)`: true when a whole word of `CARD_CUE` (`card`, `visa`, `mastercard`, `amex`, in any letter case) lies in the 40 characters before `start`. `credit`, `debit` and `maestro` are not cue words (the report's list in Q15 has four; question 26).
    - `card_is_valid(text, match)`: `digits` is the `str.isdecimal()` characters of `match.group()`. It is true when there are 13 to 19 digits (the pattern already holds this; the check is kept so the rule is stated in code), `luhn_is_valid(digits)` is true, and either `digits[0]` is in `CARD_FIRST_DIGITS` or `has_card_cue(text, match.start())` is true. This is the rule of report Q15 (d): a card needs the Luhn check and 13 to 19 digits, and a cue word or an issuer first digit. A card with a first digit of 1, 2, 7, 8, 9 or 0 needs the cue word.
    Change `find_patterns` so that, after the IBAN step, it also adds a `PiiSuggestion` with `span=Span(start=match.start(), end=match.end())` and source `PATTERN` for: each `NINO_RE` match (kind `ID`); each `COMPANY_PREFIX_RE` match (kind `ID`); each `GB_VAT_RE` match for which `gb_vat_is_valid(match.group())` is true (kind `ID`); and each `CARD_RE` match for which `card_is_valid(text, match)` is true (kind `BANK`). The result still goes through `unique_sorted`, so a NINO or a company prefix that follows a keyword and that `ID_KEYWORD` also finds, with the same span, comes back once (`registered number SC123456`).
    **Overlaps.** A finder never removes an overlap, so `find_patterns` can return two spans that cover the same digits. The planner ran these cases through the reference code, steps (1) to (6) of `find_personal_data`, on 22 Nov 2026: a card number holds a phone shape inside it (`Card 4000 0566 5566 5556`: `BANK` 5 to 24 and `PHONE` 10 to 24), a NINO after a keyword is one character longer than the keyword value (`registered number AB123456C`: `ID` 18 to 26 and `ID` 18 to 27), and a 12-digit GB VAT number is one character longer than the longest keyword value with a `GB ` prefix (`VAT number GB 333 2894 54 000`: `ID` 11 to 28 and `ID` 11 to 29). `resolve_overlaps` (S4-M3-T4) keeps the longer span of the same source and cuts the shorter one to nothing, so the result is one span in each case: `BANK` 5 to 24, `ID` 18 to 27 and `ID` 11 to 29. `TIE_RANK` is not needed here (the spans differ in length). The rank table puts `BANK` and `ID` before `PHONE`, as before.
    **Known limits (for the README, S4-M5-T4).** A cue-less number that passes the Luhn check and starts with 3, 4, 5 or 6 is replaced as a card, so a reference such as `Order 5123 4567 8901 2346` is over-masked (`test_issuer_digits_3_to_6_are_enough_known_limit`). A card in 4-6-5 spacing and a card written after a hyphen are not found. A GB VAT number is found bare only with the `GB` prefix (not `XI`, `GD` or `HA`). A NINO or a company prefix in lower case is not found. About 1 in 10 random digit strings of 13 to 19 digits passes the Luhn check, which is why the issuer digit or the cue word is required; a cue-word-only gate, as the nearby-fields table of the report proposes, is stricter (question 26).
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/patterns.py`, `src/clause_tracer/privacy/tests/test_bare_ids.py`.
  - **Tests first:** in `test_bare_ids.py`, with `found(text: str) -> list[tuple[str, int, int, PlaceholderKind]]` (each result of `find_patterns(text)` as `(text[span.start:span.end], span.start, span.end, kind)`), the names `ID`, `BANK` and `PHONE` for the `PlaceholderKind` members, and `PREFIXES`, the 15 prefixes of `COMPANY_PREFIX` in its order. The values are the planner's, computed by the reference code on 22 Nov 2026 (owner to confirm). A near miss is a text that must give nothing:
    - `test_every_result_comes_from_patterns` (`"Card 4111 1111 1111 1111 and AB123456C"` gives two results, and every `source` is `PiiSource.PATTERN`);
    UK National Insurance number (7 tests):
    - `test_nino_compact` (`"NI number AB123456C."` gives `("AB123456C", 10, 19, ID)`);
    - `test_nino_with_spaces` (`"NI number AB 12 34 56 C."` gives `("AB 12 34 56 C", 10, 23, ID)`; `"JG 10 38 17 D"` gives `("JG 10 38 17 D", 0, 13, ID)`);
    - `test_nino_after_a_bracket_or_a_colon` (`"(AB123456C)"` gives `("AB123456C", 1, 10, ID)`; `"NINO:AB123456C."` gives `("AB123456C", 5, 14, ID)`);
    - `test_nino_banned_prefixes_are_not_found` (`"BG123456C GB123456C NK123456C KN123456C NT123456C TN123456C ZZ123456C"` gives nothing);
    - `test_nino_banned_first_letters_are_not_found` (`"DA123456A FA123456A IA123456A QA123456A UA123456A VA123456A"` gives nothing);
    - `test_nino_banned_second_letters_are_not_found` (`"AD123456A AF123456A AI123456A AO123456A AQ123456A AU123456A AV123456A"` gives nothing);
    - `test_nino_wrong_shape_is_not_found` (`"AB123456E"` gives nothing; `"AB12345C"` gives nothing; `"AB1234567C"` gives nothing; `"ab123456c"` gives nothing; `"XAB123456C"` gives nothing; `"AB123456CD"` gives nothing);
    GB VAT number (7 tests, then the helper test below):
    - `test_gb_vat_bare_with_a_valid_checksum` (`"Registered for VAT as GB 333289454."` gives `("GB 333289454", 22, 34, ID)`);
    - `test_gb_vat_other_spacings` (`"GB333289454"` gives `("GB333289454", 0, 11, ID)`; `"GB 980 7806 84"` gives `("GB 980 7806 84", 0, 14, ID)`; `"GB 333 2894 54"` gives `("GB 333 2894 54", 0, 14, ID)`);
    - `test_gb_vat_with_a_branch_part` (`"GB 333 2894 54 000"` gives `("GB 333 2894 54 000", 0, 18, ID)`);
    - `test_gb_vat_wrong_checksum_is_not_found` (`"GB123456789"` gives nothing; `"GB 123 4567 89"` gives nothing);
    - `test_gb_vat_remainders_42_and_55` (`"GB 100 0000 34"` gives `("GB 100 0000 34", 0, 14, ID)`; `"GB 100 0000 47"` gives `("GB 100 0000 47", 0, 14, ID)`; `"GB 001 0000 36"` gives nothing; `"GB 001 0000 49"` gives nothing);
    - `test_gb_vat_needs_gb_and_a_whole_word` (`"333289454"` gives nothing; `"XGB333289454"` gives nothing; `"GB3332894541234"` gives nothing; `"GB 33328945"` gives nothing);
    - `test_gb_vat_after_a_keyword_needs_no_checksum` (`"VAT number GB123456789"` gives `("GB123456789", 11, 22, ID)`);
    - `test_gb_vat_is_valid` (`gb_vat_is_valid` is true for `"GB 333289454"`, `"333289454"`, `"GB 333 2894 54 000"` and `"GB 100 0000 34"`, and false for `"GB 001 0000 36"`, `"GB123456789"` and `"33328945"`);
    UK company number prefix (7 tests):
    - `test_company_prefix_found` (`"Brightline Studio Ltd (SC123456) signs."` gives `("SC123456", 23, 31, ID)`; `"NI012345"` gives `("NI012345", 0, 8, ID)`; `"LP123456"` gives `("LP123456", 0, 8, ID)`);
    - `test_every_listed_prefix_is_found` (the 15 prefixes of `COMPANY_PREFIX`, in its order (`PREFIXES` in the test file), each followed by `123456` and all joined by one space, give 15 `ID` spans, from `("SC123456", 0, 8, ID)` to `("NP123456", 126, 134, ID)`, the span of the `i`-th (from 0) being `9 * i` to `9 * i + 8`);
    - `test_company_prefix_wrong_digit_count_is_not_found` (`"FC12345"` gives nothing; `"SC1234567"` gives nothing; `"SC12345"` gives nothing);
    - `test_company_prefix_in_a_longer_word_is_not_found` (`"XSC123456"` gives nothing; `"SC123456AB"` gives nothing; `"sc123456"` gives nothing);
    - `test_unlisted_prefixes_are_not_found` (`"BR123456 OE123456 AB123456"` gives nothing);
    - `test_eight_digits_still_need_a_keyword` (`"09876543"` gives nothing; `"company number 09876543"` gives `("09876543", 15, 23, ID)`);
    - `test_company_prefix_after_a_keyword_gives_one_span` (`"registered number SC123456"` gives `("SC123456", 18, 26, ID)`);
    Card number (8 tests, then the helper test below):
    - `test_card_with_a_cue` (`"Card 4111 1111 1111 1111 expires"` gives `("4111 1111 1111 1111", 5, 24, BANK)`);
    - `test_card_formats_and_lengths` (`"visa 4111-1111-1111-1111"` gives `("4111-1111-1111-1111", 5, 24, BANK)`; `"Pay by Mastercard 5500005555555559."` gives `("5500005555555559", 18, 34, BANK)`; `"Amex 378282246310005"` gives `("378282246310005", 5, 20, BANK)`; `"card 4222222222222"` gives `("4222222222222", 5, 18, BANK)`; `"card 6304000000000000000"` gives `("6304000000000000000", 5, 24, BANK)`);
    - `test_card_that_fails_luhn_or_has_the_wrong_length_is_not_found` (`"Card 4111 1111 1111 1112"` gives nothing; `"Card 1234 5678 9012 3456"` gives nothing; `"card 411111111117"` gives nothing; `"card 41111111111111111111"` gives nothing);
    - `test_issuer_digits_3_to_6_are_enough_known_limit` (`"Order 3111 1111 1111 1113"` gives `("3111 1111 1111 1113", 6, 25, BANK)`; `"Order 4111 1111 1111 1111"` gives `("4111 1111 1111 1111", 6, 25, BANK)`; `"Order 5123 4567 8901 2346"` gives `("5123 4567 8901 2346", 6, 25, BANK)`; `"Order 6111 1111 1111 1116"` gives `("6111 1111 1111 1116", 6, 25, BANK)`);
    - `test_order_numbers_dates_and_clauses_are_kept` (`"Order 4929 1234 5678 9012"` gives nothing; `"Order 1234567890123456"` gives nothing; `"Clause 1.2.3.4 on 2026-11-21 at 12.30"` gives nothing);
    - `test_a_cue_is_needed_outside_the_digits_3_to_6` (`"Order 2221 1111 1111 1112"` gives nothing; `"Visa 2221 1111 1111 1112"` gives `("2221 1111 1111 1112", 5, 24, BANK)`; `"Order 1234 5678 1234 5670"` gives nothing);
    - `test_the_cue_must_be_within_40_characters` (`"card" + " " * 36 + "2221 1111 1111 1112"` gives `("2221 1111 1111 1112", 40, 59, BANK)`; `"card" + " " * 37 + "2221 1111 1111 1112"` gives nothing);
    - `test_the_cue_ignores_case_and_needs_a_whole_word` (`"VISA 2221 1111 1111 1112"` gives `("2221 1111 1111 1112", 5, 24, BANK)`; `"discard 2221 1111 1111 1112"` gives nothing; `"cards 2221 1111 1111 1112"` gives nothing);
    - `test_luhn_is_valid` (`luhn_is_valid` is true for `"4111111111111111"` and `"378282246310005"`, and false for `"4111111111111112"`, `""` and `"41a1"`);
    Overlaps (the finder keeps both spans and the resolve step of S4-M3-T4 keeps the longer one, see the Build; 3 tests):
    - `test_card_and_phone_overlap_both_come_back` (`"Card 4000 0566 5566 5556"` gives `("4000 0566 5566 5556", 5, 24, BANK)` and `("0566 5566 5556", 10, 24, PHONE)`);
    - `test_nino_and_keyword_id_overlap_both_come_back` (`"registered number AB123456C"` gives `("AB123456", 18, 26, ID)` and `("AB123456C", 18, 27, ID)`);
    - `test_long_vat_and_keyword_id_overlap_both_come_back` (`"VAT number GB 333 2894 54 000"` gives `("GB 333 2894 54 00", 11, 28, ID)` and `("GB 333 2894 54 000", 11, 29, ID)`);
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_bare_ids.py` reports 35 passed. The same command on `test_bare_ids.py`, `test_patterns.py` and `test_iban.py` together reports 60 passed (the 19 tests of S4-M2-T2 and the 6 of S4-M2-T3 do not change, and none of their values changes), and `scripts/check.sh` exits 0. The reference run of the sample (7 entities, 10 spans, and `id-1` at 169 to 177) needs `find_personal_data`, so it is checked in S4-M5-T7, not here.
  - **Rules:** T1 (pure functions), T11 (the values are the planner's, to confirm), ADR 0008 (checksum and prefix patterns sit in the code layer), the [report](../../reports/Privacy%20finder%20design%20choices.md), Q15 (d) and the row "Card and phone vetoes with checksums" of "Ideas from nearby fields", Spec 4.2, questions 24 and 26.
  - **Depends on:** S4-M2-T3

- [x] **S4-M2-T13: Company names with non-ASCII letters**
  - **Build:** The owner chose on 22 Nov 2026 to fix the company pattern now: the row `company-with-a-foreign-suffix` of `finders.toml` (`Müller GmbH delivers.` gives `Müller GmbH`) failed because `WORD` reads only `A` to `Z`. In `src/clause_tracer/privacy/_patterns.py`, replace the `WORD` line of S4-M2-T5 with this line, and change nothing else in the file:
    ```python
    WORD: Final[str] = r"[A-ZÀ-ÖØ-Þ](?:[^\W_]|['’&-])*"
    ```
    The first letter is `A` to `Z` or a Latin-1 capital (`À` to `Ö`, `Ø` to `Þ`; the signs `×` and `÷` are not in the ranges). The rest of the word is any letter or digit (`[^\W_]`, which excludes the underscore) or one of `'`, `’`, `&`, `-`, as before. `WORD` is used only in `COMPANY` and `CONNECTOR`. `companies.py` does not change. A capital outside Latin-1 (for example `Ł`, `Ś`, a Greek or a Cyrillic capital) is still not found: this is a known limit (see S4-M5-T4). Do not edit any table: the owner's row is the expected answer.
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/tests/test_companies.py`.
  - **Tests first:** Add these 6 tests to `test_companies.py`, with the `found` helper of the file. The planner ran each case on 22 Nov 2026. The 21 tests of S4-M2-T5 stay as they are, and none of their values changes:
    - `test_non_ascii_capital_first_letter` (`"Müller GmbH delivers."` gives `[("Müller GmbH", 0, 11)]`);
    - `test_non_ascii_capital_in_a_later_word` (`"Élan Studio Ltd signs"` gives `[("Élan Studio Ltd", 0, 15)]`);
    - `test_non_ascii_letters_inside_words` (`"Zoë Café Limited pays"` gives `[("Zoë Café Limited", 0, 16)]`);
    - `test_connector_with_a_non_ascii_word` (`"The Müller & Söhne GmbH pays."` gives `[("Müller & Söhne GmbH", 4, 23)]`);
    - `test_lower_case_non_ascii_start_is_not_a_name` (`"élan Ltd"` gives `[]`, and `"× Ltd"` gives `[]`);
    - `test_capital_outside_latin_1_is_a_known_limit` (`"Łukasz Ltd"` gives `[]`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_companies.py` reports 27 passed, `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_finder_tables.py` shows no failed test, and `scripts/check.sh` exits 0. The planner checked that the company spans of the sample contract (`ingest/samples/developer-agreement.txt`, source length 6204: 84 to 105 and 5592 to 5613) do not change.
  - **Rules:** T1 (pure functions), T11 (the owner's row is not edited; the six values are the planner's, to confirm).
  - **Depends on:** S4-M2-T5

- [x] **S4-M2-T14: Non-ASCII letters in person names, street words and emails**
  - **Build:** The M2 code review of 22 Nov 2026 found three places that still read only ASCII letters, the same cause as S4-M2-T13: `Mrs Zoë Smith signs.` gave the span `Mrs Zo` (cut mid-word, so `ë Smith` stayed readable), `Mr Müller signs.` gave nothing, `5 Müller Street, Köln` gave no address, and `bob@exämple.com` gave nothing. In `src/clause_tracer/privacy/_patterns.py` make exactly these five changes and no other:
    1. Replace the `EMAIL` line with:
       ```python
       EMAIL: Final[str] = r"[\w.%+-]+@[\w-]+(?:\.[\w-]+)+"
       ```
    2. Directly after the `H` line, add:
       ```python
       UPPER: Final[str] = "A-ZÀ-ÖØ-Þ"
       LOWER: Final[str] = "a-zß-öø-ÿ"
       ```
       (the Latin-1 capitals and lower-case letters; `×` and `÷` are in neither range).
    3. Replace the `CAP` line with:
       ```python
       CAP: Final[str] = rf"(?:[{UPPER}][{LOWER}'’-]+|UK|USA|UAE)"
       ```
    4. Replace the `TOK` and `INIT` lines with:
       ```python
       TOK: Final[str] = (
           rf"(?:[{UPPER}](?:['’][{UPPER}])?[{LOWER}]+(?:[{UPPER}][{LOWER}]+)*(?:-[{UPPER}]?[{LOWER}]+)*"
           rf"|(?:al|el)-[{UPPER}][{LOWER}]+)"
       )
       INIT: Final[str] = rf"(?:[{UPPER}]\.)"
       ```
    5. Replace the `CAPS_TOK` line with:
       ```python
       CAPS_TOK: Final[str] = rf"[{UPPER}]{{2,}}(?:['’-][{UPPER}]+)*"
       ```
    A capital outside Latin-1 (`Ł`, a Greek or a Cyrillic capital) is still not read: a known limit (S4-M5-T4). `US_ZIP` does not change: the owner chose on 22 Nov 2026 to keep a state code such as `ID` or `OK` read as a ZIP, because a missed address is worse than a hidden number. Do not edit any table.
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/tests/test_people.py`, `src/clause_tracer/privacy/tests/test_addresses.py`, `src/clause_tracer/privacy/tests/test_patterns.py`.
  - **Tests first:** Add these 6 tests, each with the `found` or `spans` helper of its file. The planner ran each case on 22 Nov 2026. The tests of S4-M2-T2, T6 and T7 stay as they are, and none of their values changes:
    - `test_people.py`: `test_non_ascii_surname_after_an_honorific` (`"Mr Müller signs."` gives `[("Mr Müller", 0, 9), ("Müller", 3, 9)]`); `test_non_ascii_name_in_a_signature` (`"Signed by Élodie Dupont for the Client."` gives `[("Élodie", 10, 16), ("Élodie Dupont", 10, 23), ("Dupont", 17, 23)]`); `test_non_ascii_letter_does_not_cut_a_name` (`"Mrs Zoë Smith signs."` gives `[("Mrs Zoë Smith", 0, 13), ("Zoë", 4, 7), ("Zoë Smith", 4, 13), ("Smith", 8, 13)]`);
    - `test_addresses.py`: `test_non_ascii_capital_in_a_street` (`spans("5 Müller Street, Köln")` is `[(0, 21)]`);
    - `test_patterns.py`: `test_email_with_non_ascii_letters` (`"Contact bob@exämple.com now"` gives `[("bob@exämple.com", 8, 23, EMAIL)]`); `test_email_with_an_underscore` (`"Mail john_smith@acme.com."` gives `[("john_smith@acme.com", 5, 24, EMAIL)]`; it already passes before the change, because the old pattern read `_`, and it pins that).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_people.py` reports 29 passed, the same command on `test_addresses.py` reports 27 passed and on `test_patterns.py` 21 passed, and `scripts/check.sh` exits 0. The planner checked that `find_companies`, `find_addresses`, `find_people`, `find_patterns` and `find_party_details` give the same results on the sample contract (`ingest/samples/developer-agreement.txt`, with the fixture's parties and terms) before and after this change.
  - **Rules:** T1 (pure functions), T11 (the six values are the planner's, to confirm).
  - **Depends on:** S4-M2-T13

- [x] **S4-M2-T15: Tests for three untested paths (tests only)**
  - **Build:** None. This task adds tests and changes no code. The M2 code review found three paths that no test ran: the hard-stop rule of a truncated address chain (`addresses.py`, lines 79 and 80), the rule that a one-word name before a job title is not a name (`people.py`, line 144), and the early return of `_short_names` for a company name that is only a suffix (`party.py`, line 89).
  - **Files:** `src/clause_tracer/privacy/tests/test_addresses.py`, `src/clause_tracer/privacy/tests/test_people.py`, `src/clause_tracer/privacy/tests/test_party.py`.
  - **Tests first:** Add these 4 tests. The planner ran each case on 22 Nov 2026 against the code of S4-M2-T14. All four must pass with no code change:
    - `test_addresses.py`: `test_truncated_chain_stops_at_a_hard_stop` (`spans("Done; Mail 1 Aaaa, Bbbb, Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB")` is `[(25, 62)]`); `test_hard_stop_between_the_start_and_the_postcode_gives_the_postcode_alone` (`spans("Mail 1 Aaaa, Bbbb; Cccc, Dddd, Eeee, Ffff, Gggg, Leeds LS1 4AB")` is `[(55, 62)]`);
    - `test_people.py`: `test_one_word_before_a_title_is_not_a_name` (`found("Signed by Smith Director today.")` is `[]`);
    - `test_party.py`: `test_a_company_name_that_is_only_a_suffix_gives_nothing` (`spans("Ltd pays.", (Party(name="Ltd", address=None, yours=False),))` is `[]`).
  - **Done when:** `test_addresses.py` reports 29 passed, `test_people.py` 30 passed and `test_party.py` 17 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T11 (the values are the planner's, to confirm).
  - **Depends on:** S4-M2-T14

- [x] **S4-M2-T16: Clean-up of the finders (the behaviour does not change, except for one underscore)**
  - **Build:** The M2 code review of 22 Nov 2026 found six places that are harder to read than they need to be. Make exactly these changes. Every test that exists before this task must pass with no edit.
    1. `party.py`, `_short_names`: replace the `if (...)` condition with named booleans:
       ```python
       words_belong_to_party = bool(words) and words <= core_words
       is_a_new_form = folded_term not in forms
       defining_sentence_names_party = any(form in defining_text for form in full_forms)
       if words_belong_to_party and is_a_new_form and defining_sentence_names_party:
           short_names.append(folded_term)
       ```
    2. `patterns.py`, `find_patterns`: add `from collections.abc import Callable`. Add `(NINO_RE, PlaceholderKind.ID)` and `(COMPANY_PREFIX_RE, PlaceholderKind.ID)` at the end of `_PATTERNS` (neither pattern has a `v` group, so the loop already covers them). Add this helper after `_PATTERNS`:
       ```python
       def _suggestion(start: int, end: int, kind: PlaceholderKind) -> PiiSuggestion:
           return PiiSuggestion(span=Span(start=start, end=end), kind=kind, source=PiiSource.PATTERN)
       ```
       Add this table directly before `find_patterns`:
       ```python
       _CHECKED: Final[
           tuple[tuple[re.Pattern[str], PlaceholderKind, Callable[[str, re.Match[str]], bool]], ...]
       ] = (
           (IBAN_RE, PlaceholderKind.BANK, lambda text, match: iban_is_valid(match.group())),
           (GB_VAT_RE, PlaceholderKind.ID, lambda text, match: gb_vat_is_valid(match.group())),
           (CARD_RE, PlaceholderKind.BANK, card_is_valid),
       )
       ```
       Then the body of `find_patterns` is the `_PATTERNS` loop, which appends `_suggestion(start, end, kind)`, then this loop, then `return unique_sorted(suggestions)`:
       ```python
       for pattern, kind, is_valid in _CHECKED:
           for match in pattern.finditer(text):
               if is_valid(text, match):
                   suggestions.append(_suggestion(match.start(), match.end(), kind))
       ```
       Delete the five separate loops for the IBAN, the NINO, the company prefix, the GB VAT number and the card.
    3. `people.py`: change the import to `from clause_tracer.privacy.companies import COMPANY_LEAD_WORDS, COMPANY_ROLE_WORDS` and define the legal words from the role words. The role words are the 18 words of `COMPANY_ROLE_WORDS`; the 33 other words stay in the literal, so the set keeps its 51 words and the owner's list does not change:
       ```python
       LEGAL_STOP_WORDS: Final[frozenset[str]] = COMPANY_ROLE_WORDS | frozenset(
           {
               "agreement", "annex", "appendix", "charges", "clause", "confidential", "date",
               "deliverables", "director", "effective", "exhibit", "fees", "force", "governing",
               "information", "intellectual", "law", "majeure", "manager", "milestone", "notice",
               "notices", "owner", "partner", "payment", "property", "schedule", "secretary",
               "section", "service", "services", "term", "termination",
           }
       )
       ```
       (Write one word on each line, as `ruff format` does.) The job-title lists `TITLE_WORDS` and `TRAILING_TITLE_WORDS` stay as they are: one is a pattern and one is a set of different words.
    4. `people.py`, `_clean_seed`: delete the check `if all(key(token) in LEGAL_STOP_WORDS for token in tokens): return None`. It can never run: the loop before it removes legal words from the end, so the last token is never a legal word. A seed made only of legal words still gives nothing, through `if not tokens`.
    5. Fold once. In `party.py`, add `MatchKey` to the import from `clause_tracer.core`, add the keyword-only parameter `*, key: MatchKey | None = None` after `terms`, and replace `key = fold_for_matching(text)` with `key = fold_for_matching(text) if key is None else key`. In `people.py` do the same: `def find_people(text: str, *, key: MatchKey | None = None)`. S4-M3-T6 folds once and passes `key=key` to both.
    6. `_patterns.py`: replace the `WORD` line with `WORD: Final[str] = rf"[{UPPER}][\w'’&-]*"`. This is the one change of behaviour: an underscore inside a word is now allowed (`Foo_Bar Ltd`).
  - **Files:** `src/clause_tracer/privacy/party.py`, `src/clause_tracer/privacy/patterns.py`, `src/clause_tracer/privacy/people.py`, `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/tests/test_companies.py`, `src/clause_tracer/privacy/tests/test_people.py`, `src/clause_tracer/privacy/tests/test_party.py`.
  - **Tests first:** Add these 4 tests. The planner ran each case on 22 Nov 2026. In `test_people.py` add the imports `fold_for_matching` (from `clause_tracer.core`), `COMPANY_ROLE_WORDS` (from `clause_tracer.privacy.companies`) and `LEGAL_STOP_WORDS` (from `clause_tracer.privacy.people`); in `test_party.py` add `fold_for_matching` to the import from `clause_tracer.core`:
    - `test_companies.py`: `test_underscore_inside_a_word` (`found("Foo_Bar Ltd pays.")` is `[("Foo_Bar Ltd", 0, 11)]`; fails before step 6);
    - `test_people.py`: `test_a_given_key_gives_the_same_result` (with `text = "Ms Jones at home. Jones left."`, `find_people(text, key=fold_for_matching(text)) == find_people(text)`); `test_legal_stop_words_hold_every_role_word` (`COMPANY_ROLE_WORDS <= LEGAL_STOP_WORDS` and `len(LEGAL_STOP_WORDS) == 51`);
    - `test_party.py`: `test_a_given_key_gives_the_same_result` (with `text = "Brightline Studio Ltd and brightline studio limited."`, `find_party_details(text, (BRIGHTLINE,), (), key=fold_for_matching(text)) == find_party_details(text, (BRIGHTLINE,), ())`).
  - **Done when:** `test_companies.py` reports 28 passed, `test_people.py` 32 passed, `test_party.py` 18 passed, `test_addresses.py` 29 passed and `test_patterns.py` 21 passed. `scripts/check.sh` exits 0 with 2058 tests passed in all. No test that exists before this task is edited. The planner ran steps 1 to 6 on 22 Nov 2026 with these results.
  - **Rules:** T1 (pure functions), S3 (the shapes do not change), T11 (the four values are the planner's, to confirm).
  - **Depends on:** S4-M2-T15

### M3: Resolve and group

When this is done, `find_personal_data` turns a `PrivacyInput` and a detector into a clean list of suggestions (checked, allow-listed, free of overlaps, never across a sentence start), and `group_entities` turns them into numbered `PlaceholderEntity`s.

- [x] **S4-M3-T1: Check and trim the suggestions**
  - **Build:** In `src/clause_tracer/privacy/resolve.py`: `def trim_suggestions(text: str, suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]`. First it takes `suggestions` as a tuple and checks every span, before any is trimmed, so that one bad span raises and no partial result exists. For each span, in this order: when `start` or `end` is not an `int`, or is a `bool`, raise `ValueError("privacy: suggestion span offsets must be integers")`; otherwise, when `start < 0`, `end < 0`, `start > len(text)` or `end > len(text)`, raise `ValueError("privacy: suggestion span is outside the text")`; otherwise, when `end < start`, raise `ValueError("privacy: suggestion span is reversed")`. Then, for each suggestion in order, apply `trimmed_span(text, span)`; a `None` result (an empty or blank span) drops the suggestion silently; otherwise the suggestion is kept with the trimmed span and the same `kind` and `source`. The order of the input is kept. This is the one check of the detector's output (D4, question 7), and it runs on the output of every finder too.
  - **Files:** `src/clause_tracer/privacy/resolve.py`, `src/clause_tracer/privacy/tests/test_trim.py`.
  - **Tests first:** in `test_trim.py`, with `suggestion` of `case_builder`: `test_trims_white_space` (`" Sam "` and a `PERSON` `NER` span 0 to 5 gives the span 1 to 4); `test_blank_span_is_dropped` (`"a   b"`, span 1 to 4, gives `()`); `test_empty_span_is_dropped` (span 2 to 2 gives `()`); `test_outside_the_text_raises` (`"abc"`, span 1 to 9, raises `ValueError` with the message `privacy: suggestion span is outside the text`); `test_keeps_kind_source_and_order` (two suggestions of different kind and source, the later one first in the input, come back in that order with the same kind and source).
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm; the suggestion is built with `PiiSuggestion(span=Span(start=a, end=b), kind=PlaceholderKind.PERSON, source=PiiSource.NER)`, and a value that is not an `int` is passed through `cast(int, ...)`):
    - `test_reversed_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(5, 2)`: raises `ValueError` with the message `privacy: suggestion span is reversed`);
    - `test_start_past_text_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(20, 25)`: raises `ValueError` with the message `privacy: suggestion span is outside the text`);
    - `test_start_past_the_text_and_reversed_raises_outside` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(25, 16)`: raises `ValueError` with the message `privacy: suggestion span is outside the text`);
    - `test_negative_start_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(-1, 3)`: raises `ValueError` with the message `privacy: suggestion span is outside the text`);
    - `test_bool_start_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(True, 3)`: raises `ValueError` with the message `privacy: suggestion span offsets must be integers`);
    - `test_bool_end_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(0, True)`: raises `ValueError` with the message `privacy: suggestion span offsets must be integers`);
    - `test_float_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(0.0, 3)`: raises `ValueError` with the message `privacy: suggestion span offsets must be integers`);
    - `test_none_raises` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(None, 3)`: raises `ValueError` with the message `privacy: suggestion span offsets must be integers`);
    - `test_empty_span_at_len_is_dropped` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(16, 16)`: gives `()`);
    - `test_empty_span_is_dropped_silently` (`"Short text here."`, a `PERSON` `NER` suggestion with the span `(3, 3)`: gives `()`);
    - `test_a_valid_span_then_a_bad_one_still_raises` (`"Short text here."`, two `PERSON` `NER` suggestions, `(0, 5)` then `(5, 2)`: raises `ValueError` with the message `privacy: suggestion span is reversed`, and gives no result).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_trim.py` reports 16 passed, and `scripts/check.sh` exits 0.
  - **Rules:** D4 and I9 (the detector's output is validated once, where it enters), I7.
  - **Depends on:** S4-M1-T5, S4-M1-T6

- [x] **S4-M3-T2: The allow-list from the defined terms**
  - **Build:** In `resolve.py`:
    - `def normalised_text(text: str) -> str`: `fold_text(text).strip()`; when the result starts with `"the "`, remove those four characters; when it then ends with `"'s"`, remove those two; strip again.
    - `def allowed_term_texts(text: str, terms: Sequence[DefinedTerm], suggestions: Sequence[PiiSuggestion]) -> frozenset[str]`. `names` is the set of `normalised_text(text[s.span.start:s.span.end])` over the suggestions `s` whose source is `PARTY_DETAILS`, or whose source is `RULE` and whose kind is `PERSON` or `COMPANY`. A term is allowed (its `normalised_text(term.term)` is in the result) when that value is not empty, is not in `names` (question 11: a detector match never removes a term), and the term is not a name by the subset rule (the Mercury rule, below). **The Mercury rule.** A defined term for a name that no typed party carries (`Mercury Logistics Ltd ("Mercury")`) is a short form of that name, not a role. With `words` the set of the words of `normalised_text(term.term)` (split on white space, `.,;:` stripped from each word, empty words dropped), the term is a name when `words` is not empty and some suggestion `s` of the `names` set, of kind `PERSON` or `COMPANY` (this kind test applies to every suggestion of the set, including one whose source is `PARTY_DETAILS`, so an `ADDRESS` suggestion never makes a term a name), lies inside `term.definition` (`definition.start <= s.span.start` and `s.span.end <= definition.end`) and `words <= core_words(text[s.span.start:s.span.end])` (`core_words` is defined at the end of this bullet). `def core_words(span_text: str) -> frozenset[str]`: `fold_text(span_text)` split on white space, `.,;:` stripped from each word, empty words dropped; the first word is dropped first, when it is in `HONORIFICS`; then the last word is dropped when more than one word remains and it is in `EXTENDED_COMPANY_SUFFIXES` (the count is of the words that remain after the honorific is dropped). So `Mr Ltd` gives `{"ltd"}`. A detector (`NER`) suggestion never makes a term a name by this rule (a short form that no finder reaches stays readable: a known limit). A role with no word in common with the name (`Agency`, `Company`) stays allowed.
    - `def drop_allowed(text: str, suggestions: Sequence[PiiSuggestion], allowed: frozenset[str]) -> tuple[PiiSuggestion, ...]`: keeps every suggestion whose source is `USER` or `PARTY_DETAILS`; keeps any other suggestion whose `normalised_text` of its span is not in `allowed`; drops the rest. The order is kept.
  - **Files:** `src/clause_tracer/privacy/resolve.py`, `src/clause_tracer/privacy/tests/test_allow_list.py`.
  - **Tests first:** in `test_allow_list.py`, with the helper `_term(name: str) -> DefinedTerm` that returns `DefinedTerm(term=name, definition=Span(start=0, end=0), uses=())` (an empty definition, so only the equal-text rule applies), and `normalised_text` of a term as the member of the result:
    - `test_a_term_is_allowed_by_default` (`allowed_term_texts("x", [_term("Agency")], ())` is `frozenset({"agency"})`);
    - `test_a_term_that_a_party_finder_matches_is_not_allowed` (text `"Brightline x"`, a `PARTY_DETAILS` `COMPANY` suggestion over `Brightline`, terms `[_term("Brightline"), _term("Agency")]`: `frozenset({"agency"})`);
    - `test_a_term_that_a_name_rule_matches_is_not_allowed` (text `"Jones x"`, a `RULE` `PERSON` suggestion over `Jones`, terms `[_term("Jones")]`: `frozenset()`);
    - `test_a_detector_match_does_not_drop_a_term` (the same with source `NER`: `frozenset({"jones"})`);
    - `test_an_address_rule_does_not_drop_a_term` (the same with source `RULE` and kind `ADDRESS`: `frozenset({"jones"})`);
    - `test_drop_allowed_drops_a_role` (text `"Pay the Agency. The Agency's rules apply to Karim."`, `NER` suggestions `COMPANY` over the first `Agency` and `PERSON` over `Karim`, allowed `{"agency"}`: only the `Karim` suggestion remains);
    - `test_drop_allowed_reads_the_and_a_possessive` (text `"Pay Agency. Next The Agency's rules."`, a `NER` `COMPANY` suggestion over `The Agency's`, allowed `{"agency"}`: `()`);
    - `test_drop_allowed_keeps_party_details_and_user` (text `"Agency Agency"`, a `PARTY_DETAILS` suggestion over the first word and a `USER` suggestion over the second, allowed `{"agency"}`: both remain);
    - `test_normalised_text` (`"The Agency’s"` gives `"agency"`; `"  THE agency "` gives `"agency"`; `"theatre"` gives `"theatre"`; `"the"` gives `"the"`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm). Each of the first four uses the text `'Mercury Logistics Ltd ("x") is the party.'`, one `RULE` `COMPANY` suggestion over `Mercury Logistics Ltd`, and one term whose `definition` is `Span(start=0, end=len(text))`; the result is read as whether `normalised_text(term)` is in the allowed set:
    - `test_mercury_is_a_name_not_a_role` (the term `Mercury`: not allowed);
    - `test_a_core_word_is_a_name` (the term `Logistics`: not allowed);
    - `test_a_role_with_no_word_in_common_stays_allowed` (the term `Agency`: allowed);
    - `test_company_and_effective_date_stay_allowed` (the term `Company`, and in a second call the term `Effective Date`: both allowed);
    - `test_a_ner_suggestion_does_not_make_a_term_a_name` (the same text, a `NER` `COMPANY` suggestion over `Mercury Logistics Ltd`, the term `Mercury`: allowed).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_allow_list.py` reports 14 passed, and `scripts/check.sh` exits 0.
  - **Rules:** Spec 4.2 (roles the contract defines are kept), [system design 15.4](../system-design.md#154-stage-4-privacy-code-finders-and-placeholders) (the 20 Nov decision), question 11.
  - **Depends on:** S4-M3-T1, S4-M2-T1

- [x] **S4-M3-T3: The governing-law place is kept**
  - **Build:** Spec 4.2 keeps the place named in the governing-law clause only when it is a country, a nation of the United Kingdom ("England and Wales" counts as one), a US state, a Canadian province or an Australian state (owner decision of 21 Nov 2026). Any other place is not kept: a finder's flag on it stays, and the text is replaced. Code cannot be unsure here, so there is no "unsure" mark in stage 4.
    - In `_patterns.py`, add two strings (fragments, with no `_RE`):
      ```python
      GOVERNING_LAW_CUE: Final[str] = (
          r"(?i:governed by,?(?: and construed in accordance with,?)? the laws? of)[ \t]+"
          r"(?:the[ \t]+)?"
      )
      PLACE_END: Final[str] = r"(?![A-Za-z])"
      ```
    - In `src/clause_tracer/privacy/places.py`, import the six lists of `_place_list.py` (S4-M2-T11, the owner's file) and add two switches, both off (open question 19). Write the switches and the pattern builder exactly:
      ```python
      US_STATE_BARE: Final[bool] = False
      US_COMMONWEALTH: Final[bool] = False


      def _alternation(names: Iterable[str]) -> str:
          return (
              "(?:" + "|".join(re.escape(n) for n in sorted(set(names), key=lambda n: (-len(n), n))) + ")"
          )


      def _build_place_re() -> re.Pattern[str]:
          countries = COUNTRIES + COUNTRIES_MULTI
          us_prefix = r"(?:State|Commonwealth)" if US_COMMONWEALTH else "State"
          alternatives = [
              rf"(?:Republic|Kingdom)[ \t]+of[ \t]+{_alternation(countries)}",
              _alternation(countries + UK_NATIONS),
              rf"{us_prefix}[ \t]+of[ \t]+{_alternation(US_STATES)}",
              rf"(?:State[ \t]+of[ \t]+)?{_alternation(AU_STATES)}",
              rf"(?:Province[ \t]+of[ \t]+)?{_alternation(CA_PROVINCES)}",
          ]
          if US_STATE_BARE:
              alternatives.append(_alternation(US_STATES))
          return re.compile(GOVERNING_LAW_CUE + "(?P<p>(?:" + "|".join(alternatives) + "))" + PLACE_END)


      PLACE_RE: Final[re.Pattern[str]] = _build_place_re()
      ```
      Then `def governing_law_places(text: str) -> tuple[Span, ...]`: the span of the group `p` of each `PLACE_RE.finditer(text)` match, in order. The group holds the place and the words `State of`, `Republic of`, `Kingdom of` or `Province of` when the text has them; the word `the` before it is outside. The longest listed name wins (`England and Wales`, not `England`). A US state counts only as `State of X` (`laws of New York` is not kept; `Commonwealth of Virginia` is not kept) unless a switch is on. Washington, D.C., the District of Columbia, Jersey, Guernsey, the Isle of Man and Hong Kong are not in the list, so they are not kept.
    - In `resolve.py`, `def cut_in_places(text: str, suggestions: Sequence[PiiSuggestion], places: Sequence[Span]) -> tuple[PiiSuggestion, ...]`. It keeps every suggestion whose source is `USER` or `PARTY_DETAILS`. For every other suggestion, `hits` is the spans of `places` that overlap its span. With no hit, it keeps the suggestion. If the suggestion's kind is `PERSON` or `COMPANY`, it keeps the suggestion whole, so the place word is hidden with the name (the owner's hybrid decision of 21 Nov 2026, question 25). Otherwise it takes each piece of `subtract_spans(suggestion.span, hits)` (S4-M1-T6), applies `trimmed_span(text, piece)`, skips a piece that gives `None` or whose text has no character with `str.isalnum()` true, and keeps the others with the suggestion's `kind` and `source`. The order is kept. A span of any other kind that runs into the place is cut, never dropped whole, so the part outside the place stays flagged (question 9; report, property P11 (defined in S4-M3-T11)). The place itself is never replaced, except when a person or company span holds it (question 25, property P12 (defined in S4-M3-T11)).
  - **Files:** `src/clause_tracer/privacy/_patterns.py`, `src/clause_tracer/privacy/places.py`, `src/clause_tracer/privacy/resolve.py`, `src/clause_tracer/privacy/tests/test_places.py`.
  - **Tests first:** in `test_places.py`. The tests that name a place assume the owner's list of S4-M2-T11 holds that name; if the owner changes the list, the test changes in a commit of its own (T11). `test_finds_the_place` (`"This Agreement is governed by the laws of England and Wales."` gives one span whose text is `England and Wales`); `test_finds_the_other_wording` (`"governed by and construed in accordance with the law of Scotland."` gives one span whose text is `Scotland`); `test_no_place_without_the_phrase` (`"Disputes go to Leeds."` gives `()`); `test_the_place_stops_at_a_full_stop` (`"governed by the laws of England and Wales. Next."` gives the text `England and Wales`); `test_cut_in_places_drops_a_detector_match` (text `"governed by the laws of England and Wales. Fly to Leeds."`, `NER` `ADDRESS` suggestions over `England` and `Leeds`, places `governing_law_places(text)`: only `Leeds` remains); `test_cut_in_places_keeps_party_details_and_user` (the same text, a `PARTY_DETAILS` and a `USER` suggestion over `England`: both remain). Each place test below reads the result of `governing_law_places` as the text of each span:
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm):
    - `test_state_of` (`"This Agreement is governed by the laws of the State of Delaware."` gives `"State of Delaware"`);
    - `test_republic_of` (`"governed by the laws of the Republic of Ireland."` gives `"Republic of Ireland"`);
    - `test_longest_match_england_and_wales` (`"governed by the laws of England and Wales, Hall Road."` gives `"England and Wales"`);
    - `test_england_alone` (`"governed by the laws of England."` gives `"England"`);
    - `test_wales_alone` (`"governed by the laws of Wales."` gives `"Wales"`);
    - `test_scotland_alone` (`"governed by the laws of Scotland."` gives `"Scotland"`);
    - `test_northern_ireland_alone` (`"governed by the laws of Northern Ireland."` gives `"Northern Ireland"`);
    - `test_the_place_stops_at_england` (`"governed by the laws of England Sarah Jones signs. Signed by Sarah Jones."` gives `"England"`);
    - `test_nothing_after_the_longest_match` (`"governed by the laws of Scotland and England and Wales"` gives `"Scotland"`);
    - `test_us_state_bare_is_not_listed` (`"governed by the laws of New York"` gives nothing);
    - `test_commonwealth_is_not_listed` (`"governed by the laws of the Commonwealth of Virginia"` gives nothing);
    - `test_washington_dc_is_not_listed` (`"governed by the laws of Washington, D.C."` gives nothing);
    - `test_hong_kong_sar_is_not_listed` (`"governed by the laws of Hong Kong SAR"` gives nothing);
    - `test_au_state_of_victoria` (`"governed by the laws of the State of Victoria"` gives `"State of Victoria"`);
    - `test_ca_province_of_ontario` (`"governed by the laws of the Province of Ontario"` gives `"Province of Ontario"`);
    - `test_kingdom_of_spain` (`"governed by the laws of the Kingdom of Spain"` gives `"Kingdom of Spain"`);
    - `test_state_of_new_york_usa` (`"governed by the law of the State of New York, USA"` gives `"State of New York"`);
    - `test_canadian_province` (`"governed by the laws of Ontario"` gives `"Ontario"`);
    - `test_australian_state` (`"governed by the laws of New South Wales"` gives `"New South Wales"`);
    - `test_outside_the_list_narnia` (`"governed by the laws of Narnia"` gives nothing);
    - `test_jersey_is_not_listed` (`"governed by the laws of Jersey"` gives nothing);
    - `test_guernsey_is_not_listed` (`"governed by the laws of Guernsey"` gives nothing);
    - `test_isle_of_man_is_not_listed` (`"governed by the laws of the Isle of Man"` gives nothing);
    - `test_hong_kong_is_not_listed` (`"governed by the laws of Hong Kong"` gives nothing);
    - `test_dc_is_not_listed` (`"governed by the laws of the District of Columbia"` gives nothing);
    - `test_courts_of_leeds_is_not_a_place` (`"Disputes go to the courts of Leeds."` gives nothing);
    - The cut and whole tests use the text `"governed by the laws of England and Wales, Hall Road."` (the place is 24 to 41), one suggestion over `Wales, Hall Road` (36 to 52), and `cut_in_places(text, (suggestion,), governing_law_places(text))`, read as `(text[span.start:span.end], span.start, span.end, kind, source)`:
    - `test_cut_at_the_place_address_rule` (kind `ADDRESS`, source `RULE`: `(", Hall Road", 41, 52, ADDRESS, RULE)`);
    - `test_person_stays_whole_at_the_place_ner` (kind `PERSON`, source `NER`: `("Wales, Hall Road", 36, 52, PERSON, NER)`);
    - `test_company_stays_whole_at_the_place_rule` (kind `COMPANY`, source `RULE`: `("Wales, Hall Road", 36, 52, COMPANY, RULE)`);
    - `test_person_stays_whole_at_the_place_rule` (kind `PERSON`, source `RULE`: `("Wales, Hall Road", 36, 52, PERSON, RULE)`);
    - `test_company_stays_whole_at_the_place_ner` (kind `COMPANY`, source `NER`: `("Wales, Hall Road", 36, 52, COMPANY, NER)`);
    - `test_cut_at_the_place_address_pattern` (kind `ADDRESS`, source `PATTERN`: `(", Hall Road", 41, 52, ADDRESS, PATTERN)`);
    - `test_cut_at_the_place_address_ner` (kind `ADDRESS`, source `NER`: `(", Hall Road", 41, 52, ADDRESS, NER)`);
    - `test_cut_at_the_place_email_ner` (kind `EMAIL`, source `NER`: `(", Hall Road", 41, 52, EMAIL, NER)`);
    - `test_cut_at_the_place_phone_pattern` (kind `PHONE`, source `PATTERN`: `(", Hall Road", 41, 52, PHONE, PATTERN)`);
    - `test_cut_at_the_place_id_pattern` (kind `ID`, source `PATTERN`: `(", Hall Road", 41, 52, ID, PATTERN)`);
    - `test_cut_at_the_place_bank_pattern` (kind `BANK`, source `PATTERN`: `(", Hall Road", 41, 52, BANK, PATTERN)`);
    - `test_a_span_inside_the_place_vanishes` (a `NER` `ADDRESS` suggestion over `England and Wales`, 24 to 41: nothing);
    - `test_party_details_stays_whole_across_the_place` (kind `ADDRESS`, source `PARTY_DETAILS`: `("Wales, Hall Road", 36, 52, ADDRESS, PARTY_DETAILS)`);
    - `test_user_stays_whole_across_the_place` (kind `ADDRESS`, source `USER`: `("Wales, Hall Road", 36, 52, ADDRESS, USER)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_places.py` reports 46 passed, and `scripts/check.sh` exits 0. The two composed cases (a company rule that touches the place, and every `Sarah Jones` beside it) are in S4-M3-T6.
  - **Rules:** Spec 4.2 ("the place named in the governing-law clause" is kept, closed list), Constitution T11 (the list is the owner's) and T13 (a promise has a test), question 14.
  - **Depends on:** S4-M3-T1, S4-M2-T11, S4-M1-T6

- [ ] **S4-M3-T4: Resolve overlaps by source**
  - **Build:** In `resolve.py`:
    - `SOURCE_PRIORITY: Final[Mapping[PiiSource, int]] = MappingProxyType({PiiSource.USER: 0, PiiSource.PARTY_DETAILS: 1, PiiSource.PATTERN: 2, PiiSource.RULE: 3, PiiSource.NER: 4})`.
    - `TIE_RANK: Final[Mapping[PlaceholderKind, int]] = MappingProxyType({PlaceholderKind.BANK: 0, PlaceholderKind.ID: 1, PlaceholderKind.PERSON: 2, PlaceholderKind.COMPANY: 3, PlaceholderKind.ADDRESS: 4, PlaceholderKind.EMAIL: 5, PlaceholderKind.PHONE: 6})`. It breaks a tie between two suggestions of the same source, the same length and the same start. Why it is here and not in `core`: with value-only spans (question 5), a keyword-gated ID or BANK value and a bare phone shape can cover exactly the same digits (`company number 07700900123`), and `PlaceholderKind` puts `PHONE` before `ID` and `BANK`, so the phone would win. A keyword gate or a checksum is stronger evidence than a bare shape, so `BANK` and then `ID` rank first. The other five kinds keep their relative order, so `test_equal_spans_keep_the_first_kind` still holds. `PlaceholderKind` in `core` is not reordered (an accepted shape).
    - `def union_ner(suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]`, the NER union (owner decision of 21 Nov 2026). Suggestions whose source is not `NER` pass through unchanged. For each kind in `KINDS`, the `NER` suggestions of that kind, sorted by `(start, end)`, are joined: a suggestion joins the run before it when `start < run_end and run_start < end` (a strict overlap; touching spans stay apart), and the run becomes `(run_start, max(run_end, end))`; each run is one `NER` suggestion of that kind. There is no union for `RULE`, `PATTERN`, `PARTY_DETAILS` or `USER` (open question 21). It fixes a detector that returns `Sarah Jo` and `ah Jones` for `Sarah Jones` (without it a fragment can stay).
    - `def resolve_overlaps(text: str, suggestions: Iterable[PiiSuggestion]) -> tuple[PiiSuggestion, ...]`. First apply `union_ner`. Sort the result by `(SOURCE_PRIORITY[source], -(span.end - span.start), span.start, TIE_RANK[kind])`. Keep a list `kept` of non-overlapping suggestions. For each suggestion in that order: let `hit` be the suggestions of `kept` that overlap its span, sorted by start. With no `hit`, its pieces are its whole span. Otherwise its pieces are `subtract_spans(span, [hit spans])` (S4-M1-T6). For each piece, apply `trimmed_span(text, piece)`; skip a piece that gives `None`; when `hit` is not empty, also skip a piece whose text has no character with `str.isalnum()` true; add the others to `kept` with the suggestion's `kind` and `source`. Return `kept` sorted by `(span.start, span.end)`. A lower-priority span is therefore cut, and never dropped whole: the part outside every kept span stays flagged (question 9). `kept` is always sorted by start and never holds two overlapping suggestions, because each piece added lies outside every suggestion already in it. Find the `hit` suggestions with `bisect` on the starts of `kept`, so no task compares every pair.
  - **Files:** `src/clause_tracer/privacy/resolve.py`, `src/clause_tracer/privacy/tests/test_overlaps.py`.
  - **Tests first:** in `test_overlaps.py`, each result is read as `(text[span.start:span.end], span.start, span.end, kind, source)`:
    - `test_a_contained_lower_span_vanishes` (text `"Brightline Studio Ltd"`, `PARTY_DETAILS` `COMPANY` over all of it, `NER` `PERSON` over `Studio`: only `("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS)`);
    - `test_a_lower_span_that_sticks_out_is_cut` (text `"Brightline Studio Ltd, Leeds"`, `PARTY_DETAILS` `COMPANY` over `Brightline Studio Ltd`, `NER` `ADDRESS` over `Studio Ltd, Leeds`: the party span, and `(", Leeds", 21, 28, ADDRESS, NER)`);
    - `test_a_punctuation_only_piece_is_dropped` (text `"Brightline Studio Ltd,"`, the same party span, `NER` `ADDRESS` over `Studio Ltd,`: only the party span);
    - `test_a_span_is_cut_on_both_sides` (text `"Sarah Jones Smith"`, `RULE` `PERSON` over `Jones`, `NER` `PERSON` over all: `("Sarah", 0, 5, PERSON, NER)`, `("Jones", 6, 11, PERSON, RULE)`, `("Smith", 12, 17, PERSON, NER)`);
    - `test_longer_wins_within_a_source` (text `"Brightline Studio Ltd"`, two `PARTY_DETAILS` `COMPANY` spans, `Brightline Studio` and the whole text: only the whole text);
    - `test_user_beats_party_details` (text `"Sarah Jones"`, `USER` `PERSON` over `Jones`, `PARTY_DETAILS` `PERSON` over all: `("Sarah", 0, 5, PERSON, PARTY_DETAILS)` and `("Jones", 6, 11, PERSON, USER)`);
    - `test_touching_spans_stay_apart` (text `"SamLee"`, `NER` `PERSON` over `Sam` and over `Lee`: both remain);
    - `test_equal_spans_keep_the_first_kind` (text `"Sam"`, `NER` `ADDRESS` and `NER` `PERSON` over all of it: only the `PERSON` one);
    - `test_result_is_sorted_by_start` (text `"aa bb cc"`, `NER` `PERSON` over `cc` then over `aa`: `aa` first);
    - `test_no_suggestions` (`resolve_overlaps("x", ())` is `()`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm; each result is read as `(text[span.start:span.end], span.start, span.end, kind, source)`):
    - `test_ner_union_sarah_jo_and_ah_jones` (text `"Sarah Jones"`, `NER` `PERSON` spans 0 to 8 and 3 to 11: `("Sarah Jones", 0, 11, PERSON, NER)`);
    - `test_ner_union_chain_of_three` (text `"abcdefghij"`, `NER` `PERSON` spans 0 to 4, 3 to 7 and 6 to 10: `("abcdefghij", 0, 10, PERSON, NER)`);
    - `test_ner_union_needs_the_same_kind` (text `"Sarah Jones"`, `NER` `PERSON` 0 to 8 and `NER` `ADDRESS` 3 to 11: `("Sarah Jo", 0, 8, PERSON, NER)` and `("nes", 8, 11, ADDRESS, NER)`);
    - `test_no_union_for_rule` (text `"Sarah Jones"`, `RULE` `PERSON` spans 0 to 8 and 3 to 11: `("Sarah Jo", 0, 8, PERSON, RULE)` and `("nes", 8, 11, PERSON, RULE)`);
    - `test_no_union_for_pattern` (the same with `PATTERN`: `("Sarah Jo", 0, 8, PERSON, PATTERN)` and `("nes", 8, 11, PERSON, PATTERN)`);
    - `test_no_union_for_party_details` (the same with `PARTY_DETAILS`: `("Sarah Jo", 0, 8, PERSON, PARTY_DETAILS)` and `("nes", 8, 11, PERSON, PARTY_DETAILS)`);
    - `test_no_union_for_user` (the same with `USER`: `("Sarah Jo", 0, 8, PERSON, USER)` and `("nes", 8, 11, PERSON, USER)`);
    - `test_tie_id_beats_phone` (text `"12-34-56"`, `PATTERN` `PHONE` and `PATTERN` `ID` over all of it: `("12-34-56", 0, 8, ID, PATTERN)`);
    - `test_tie_bank_beats_id_and_phone` (the same with a `PATTERN` `BANK` as well: `("12-34-56", 0, 8, BANK, PATTERN)`);
    - `test_tie_kind_order_otherwise_unchanged` (text `"12-34-56"`, `PATTERN` `ADDRESS` and `PATTERN` `PERSON` over all of it: `("12-34-56", 0, 8, PERSON, PATTERN)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_overlaps.py` reports 20 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, ADR 0008 (code first), the architecture report ("overlaps resolve by source priority, then length"), Spec 5 (when code cannot be sure it keeps the flag), questions 5 and 9.
  - **Depends on:** S4-M3-T1, S4-M1-T6

- [ ] **S4-M3-T5: Split suggestions at sentence starts**
  - **Build:** In `resolve.py`: `def sentence_starts(clauses: Sequence[Clause]) -> tuple[int, ...]`: the sorted, distinct `sentence.span.start` of every sentence of every clause. `def split_at_sentences(text: str, suggestions: Iterable[PiiSuggestion], starts: Sequence[int]) -> tuple[PiiSuggestion, ...]`: `starts` is sorted. For each suggestion, the cut points are its `span.start`, each value `c` of `starts` with `span.start < c < span.end` (found with `bisect`), and its `span.end`. Each pair of neighbouring cut points is a piece; apply `trimmed_span(text, piece)`; skip a `None`; keep the others with the same `kind` and `source`. Return through `unique_sorted`. No piece holds a sentence start inside it, so no entity crosses a sentence boundary (question 8).
  - **Files:** `src/clause_tracer/privacy/resolve.py`, `src/clause_tracer/privacy/tests/test_split.py`.
  - **Tests first:** in `test_split.py`: `test_a_span_inside_a_sentence_is_kept` (text `"Pay Sam. Then Kim."`, starts `(0, 9)`, a `NER` `PERSON` suggestion over `Sam`: unchanged); `test_a_span_across_a_sentence_start_is_cut` (text `"Pay Sam Lee. Then Kim."`, starts `(0, 13)`, a `NER` `ADDRESS` suggestion over `Lee. Then`: the pieces `Lee.` (8 to 12) and `Then` (13 to 17)); `test_a_piece_of_only_white_space_is_dropped` (text `"ab cd"`, starts `(0, 3)`, a `NER` `PERSON` suggestion with span 2 to 4: one suggestion, `c` at 3 to 4); `test_several_starts_give_several_pieces` (text `"aa bb cc dd"`, starts `(0, 3, 6, 9)`, a `NER` `ADDRESS` span 0 to 11: four pieces, `aa`, `bb`, `cc`, `dd`); `test_sentence_starts` (`sentence_starts(make_case(["A b.", "C d.", "E f."]).clauses) == (0, 5, 10)`); `test_kind_and_source_are_kept` (the pieces of the second test are `ADDRESS` and `NER`).
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm; each result is read as `(span.start, span.end)`):
    - `test_pieces_are_sorted_and_unique` (text `"aa bb"`, three `NER` `PERSON` suggestions with the spans 3 to 5, 0 to 2 and 0 to 2 again, starts `()`: `((0, 2), (3, 5))`);
    - `test_split_is_idempotent` (text `"Pay Sam Lee. Then Kim."`, a `NER` `ADDRESS` suggestion over `Lee. Then`, starts `(0, 13)`: splitting the result a second time with the same starts gives the same tuple).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_split.py` reports 8 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, Spec 5 ("never guess": a span is cut, never dropped), the seams report ("no name ever crosses a sentence boundary"), system design 4.2.
  - **Depends on:** S4-M3-T1, S4-M1-T5

- [ ] **S4-M3-T6: `find_personal_data`, the step 3 call**
  - **Build:** In `src/clause_tracer/privacy/finding.py`: `def find_personal_data(case: PrivacyInput, detector: PiiDetector) -> tuple[PiiSuggestion, ...]`. With `text = case.document.text` and `key = fold_for_matching(text)` (folded once), it runs these steps in order. (1) `raw` is `find_party_details(text, case.parties, case.terms, key=key)`, `find_patterns(text)`, `find_companies(text)`, `find_addresses(text)`, `find_people(text, key=key)` and `detector.find(text)`, joined in that order (the detector is called once, on the whole text: question 7). (2) `checked = trim_suggestions(text, raw)`. (3) `allowed = allowed_term_texts(text, case.terms, checked)`, then `kept = drop_allowed(text, checked, allowed)`. (4) `kept = cut_in_places(text, kept, governing_law_places(text))`. (5) `resolved = resolve_overlaps(text, kept)` (the `NER` union runs first inside it). (6) Return `split_at_sentences(text, resolved, sentence_starts(case.clauses))`. It raises `ValueError` only as its parts do. It reads no file and keeps no state. It never catches an error from `detector.find`: the port's docstring says "Raises: None", but a detector that fails must stop the run, so that a failure is never read as "nothing found" (fail closed; the stage 7 adapter gives a named error type, section 9).
  - **Files:** `src/clause_tracer/privacy/finding.py`, `src/clause_tracer/privacy/tests/test_finding.py`.
  - **Tests first:** in `test_finding.py`, with `make_case` and `FakePiiDetector({text: planted})` (the fake is keyed by the exact text), and results read as `(text[span.start:span.end], span.start, span.end, kind, source)`:
    - `test_code_finders_run_with_an_empty_detector` (sentences `["Signed by Tom Jones, Director.", "Mail a@b.com."]`, no parties, `FakePiiDetector({})`: `("Tom Jones", 10, 19, PERSON, RULE)` and `("a@b.com", 36, 43, EMAIL, PATTERN)`);
    - `test_the_detector_is_called_once_with_the_whole_text` (a class `RecordingDetector` in the test file, with `calls: list[str]` and `find` that appends its argument and returns `()`: after one call `calls == [case.document.text]`);
    - `test_a_detector_span_outside_the_text_raises` (a case with the sentence `["Hi."]`, and a planted `NER` `PERSON` span 0 to 99: `ValueError`);
    - `test_a_detector_name_is_kept` (sentence `["Zed paid."]`, a planted `NER` `PERSON` span over `Zed`: `("Zed", 0, 3, PERSON, NER)`);
    - `test_a_defined_term_is_not_replaced_when_the_detector_flags_it` (sentence `["Agency pays."]`, a term `DefinedTerm(term="Agency", definition=Span(start=0, end=0), uses=())`, a planted `NER` `COMPANY` span over `Agency`: `()`);
    - `test_a_party_short_name_is_replaced` (sentence `['Brightline Studio Ltd ("Brightline") pays.']`, party `Party(name="Brightline Studio Ltd", address=None, yours=False)`, the term `DefinedTerm(term="Brightline", definition=Span(start=0, end=42), uses=())` (the sentence is 42 characters long): `("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS)` and `("Brightline", 24, 34, COMPANY, PARTY_DETAILS)`);
    - `test_the_governing_law_place_is_kept` (sentence `["This is governed by the laws of England and Wales."]`, a planted `NER` `ADDRESS` span over `England and Wales`: `()`);
    - `test_a_detector_span_across_a_sentence_is_split` (sentences `["Pay Sam Lee.", "Then Kim."]`, a planted `NER` `ADDRESS` span over `Lee. Then`: `("Lee.", 8, 12, ADDRESS, NER)` and `("Then", 13, 17, ADDRESS, NER)`);
    - Added on 21 Nov 2026 (the planner's values from the reference code, owner to confirm; each result is read as `(text[span.start:span.end], span.start, span.end, kind, source)` unless the test says otherwise):
    - `test_a_detector_error_is_not_caught` (a class `FailingDetector` in the test file, whose `find` raises `RuntimeError("detector failed")`, over `make_case(["Hi."])`: `find_personal_data` raises `RuntimeError`);
    - `test_value_only_id_and_phone_on_the_same_digits_gives_id` (sentence `["company number 07700900123"]`, an empty detector: `("07700900123", 15, 26, ID, PATTERN)`);
    - `test_bare_mercury_from_the_detector_is_replaced_and_the_role_is_not` (the sentence `'Mercury Logistics Ltd ("Mercury") will carry the goods. Mercury must pay on time. The "Agency" appoints the Agent.'` as one sentence, terms `DefinedTerm(term="Mercury", ...)` with `definition` over `Mercury Logistics Ltd ("Mercury") will carry the goods.` and `DefinedTerm(term="Agency", ...)` with `definition` over `The "Agency" appoints the Agent.`, planted `NER` `COMPANY` spans over the third `Mercury` and over `Agency`: `("Mercury Logistics Ltd", 0, 21, COMPANY, RULE)` and `("Mercury", 56, 63, COMPANY, NER)`);
    - `test_detector_alone_cannot_decide` (a known limit, report residual risk (c): the sentence `'Mercury ("Mercury") will pay. Mercury must pay.'`, the term `Mercury` with `definition` over `Mercury ("Mercury") will pay.`, a planted `NER` `COMPANY` span over the third `Mercury`: `()`, because no finder finds a full name, so the term stays allowed and the detector's flag is dropped);
    - `test_a_person_found_by_rule_makes_the_short_name_a_name` (the sentence `'Jane Smith ("Jane") signed. Signed by Jane Smith. Jane pays. The "Company" is Apple Inc.'` as one sentence, terms `Jane` with `definition` over `Jane Smith ("Jane") signed.` and `Company` with `definition` over `The "Company" is Apple Inc.`, a planted `NER` `COMPANY` span over `Company`, read as `(text, start, end, kind)`: `("Jane Smith", 0, 10, PERSON)`, `("Jane", 13, 17, PERSON)`, `("Jane Smith", 38, 48, PERSON)`, `("Jane", 50, 54, PERSON)` and `("Apple Inc", 78, 87, COMPANY)`: the role `Company` is dropped, and `Jane` is replaced);
    - `test_company_rule_touching_the_place_stays_whole` (sentence `["governed by the laws of England Brightline Studio Ltd signs."]`, an empty detector, read as `(text, start, end)`: `("England Brightline Studio Ltd", 24, 53)`; the place word `England` is hidden with the name (hybrid, question 25));
    - `test_every_sarah_jones_is_hidden` (sentence `["This Agreement is governed by the laws of England Sarah Jones signs. Signed by Sarah Jones."]`, an empty detector, read as `(text, start, end, kind)`: `("Sarah Jones", 50, 61, PERSON)` and `("Sarah Jones", 79, 90, PERSON)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_finding.py` reports 15 passed, and `scripts/check.sh` exits 0.
  - **Rules:** I3 (one input object), I11 (the contract note is written in S4-M5-T4), P3 (a fixed series of steps), T2 (the detector is passed in), fail closed (the `PiiDetector` docstring "Raises: None" does not license catching an error).
  - **Depends on:** S4-M1-T3, S4-M1-T5, S4-M2-T3, S4-M2-T4, S4-M2-T5, S4-M2-T6, S4-M2-T7, S4-M2-T12, S4-M3-T2, S4-M3-T3, S4-M3-T4, S4-M3-T5

- [ ] **S4-M3-T7: Group variants into numbered entities**
  - **Build:** In `src/clause_tracer/privacy/entities.py`: `def group_entities(document: Document, suggestions: Sequence[PiiSuggestion]) -> tuple[PlaceholderEntity, ...]`.
    - Sort the suggestions by `(span.start, span.end)`. Then, for each suggestion in that order: a span with `start < 0` or an `end` after `len(document.text)` raises `ValueError("privacy: suggestion span is outside the text")`, and then a span that overlaps the one before it (`overlaps` of `_spans`) raises `ValueError("privacy: suggestions overlap")`.
    - `_word_set(kind: PlaceholderKind, text: str) -> frozenset[str]`: `folded = fold_text(text).strip()`. `PERSON`: `words = strip_honorific(folded.split())`. `COMPANY`: `words = folded.split()`, and when `len(words) > 1` and `words[-1].strip(".,")` is in `COMPANY_SUFFIXES`, drop the last word. `ADDRESS`: the non-empty parts of `re.split(r"[\s,]+", folded)`. `PHONE`: one word, the digits of `folded`. `ID` and `BANK`: one word, the characters of `folded` for which `str.isalnum()` is true. `EMAIL`: one word, `folded`. Then strip `".,;:"` from each word and drop empty words. When no word is left, the set is `frozenset({"\0" + folded})`.
    - Work on one kind at a time, in the order of `PlaceholderKind`. The distinct word sets of the kind come in order of first appearance. A set `S` has a bigger set when another distinct set strictly contains it. A set with no bigger set is a head. The cluster of a head is itself. The cluster of a set that has bigger sets is the one head that contains it, and when two or more heads contain it, the set is its own cluster (question 12). A suggestion belongs to the cluster of its word set.
    - Number the clusters of a kind 1, 2, … in the order of the earliest span start in each. An entity has `id=f"{kind.value}-{number}"`, `kind`, `number`, and `spans` sorted by start. Return all entities of all kinds sorted by the start of their first span.
  - **Files:** `src/clause_tracer/privacy/entities.py`, `src/clause_tracer/privacy/tests/test_entities.py`.
  - **Tests first:** in `test_entities.py`, each case builds the text with `make_case([text]).document`, the suggestions with `suggestion(text, needle, kind, PiiSource.RULE, nth)`, and reads each entity as `(id, [text of each span])`:
    - `test_variants_share_one_entity` (text `"Sarah Jones then Ms Jones and Mr Smith and Smith."`, `PERSON` suggestions over `Sarah Jones`, `Ms Jones`, `Mr Smith` and the second `Smith`: `("person-1", ["Sarah Jones", "Ms Jones"])` and `("person-2", ["Mr Smith", "Smith"])`);
    - `test_a_short_form_of_two_names_gets_its_own_entity` (text `"Ms Jones and Sarah Jones and Sarah and Tom Jones."`, `PERSON` suggestions over `Ms Jones`, `Sarah Jones`, the second `Sarah`, `Tom Jones`: `("person-1", ["Ms Jones"])`, `("person-2", ["Sarah Jones", "Sarah"])`, `("person-3", ["Tom Jones"])`);
    - `test_a_company_suffix_is_ignored` (text `"Brightline Studio Ltd, Brightline Studio and Brightline Studio Limited."`, `COMPANY` suggestions over `Brightline Studio Ltd`, the second `Brightline Studio` and `Brightline Studio Limited`: one entity `company-1` with the three spans);
    - `test_emails_differ_only_by_case` (text `"a@b.com and A@B.com"`, two `EMAIL` suggestions: one entity `email-1`);
    - `test_phones_compare_by_digits` (text `"020 7946 0958 and 0207946 0958"`, two `PHONE` suggestions: one entity `phone-1`);
    - `test_ids_compare_by_letters_and_digits` (text `"ID 123-45 and id 12345"`, two `ID` suggestions: one entity `id-1`);
    - `test_an_address_line_joins_its_full_address` (text `"14 Harbour Street and 14 Harbour Street, Leeds LS1 4AB"`, two `ADDRESS` suggestions, `14 Harbour Street` and `14 Harbour Street, Leeds LS1 4AB`: one entity `address-1`);
    - `test_numbers_run_by_kind_in_order_of_first_place` (text `"Bob and Acme Ltd and Zed"`, `PERSON` over `Bob` and `Zed`, `COMPANY` over `Acme Ltd`: `person-1` (`Bob`), `company-1` (`Acme Ltd`), `person-2` (`Zed`), in that order);
    - `test_spans_are_sorted` (the suggestions of the first test given in reverse: the same result);
    - `test_overlapping_suggestions_raise` (`PERSON` spans 0 to 5 and 3 to 8 over `"abcdefghij"`: `ValueError("privacy: suggestions overlap")`);
    - `test_a_span_outside_the_text_raises` (a span ending at 99 over `"abc"`, and a span with `start=-1`: `ValueError` each);
    - `test_no_suggestions` (`group_entities(document, ())` is `()`);
    - `test_an_honorific_alone_groups_by_its_text` (text `"Ms and Ms"`, two `PERSON` suggestions over `Ms`: one entity `person-1` with two spans).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_entities.py` reports 13 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, Spec 4.2 (numbering by kind, variants share one placeholder), system design 3.4 (`PlaceholderEntity`), D2 (the order and the ids are the same on every run).
  - **Depends on:** S4-M1-T5, S4-M1-T6, S4-M2-T1

- [x] **S4-M3-T8: The pipeline table (Owner)**
  - **Build:** Owner only. The owner fills `src/clause_tracer/privacy/tests/tables/pipeline.toml`, in this format:
    ```toml
    [[case]]
    id = "longer-code-span-cuts-a-detector-span"
    sentences = [ "Brightline Studio Ltd, Leeds is here." ]   # joined by one space to make the text
    parties = [ { name = "Brightline Studio Ltd", yours = false } ]   # optional
    terms = [ "Agency" ]                                            # optional; a string, or { term, definition } as in party_details.toml
    detector = [ { text = "Studio Ltd, Leeds", kind = "address", source = "ner" } ]   # optional; nth is optional
    found = [
      { text = "Brightline Studio Ltd", kind = "company", source = "party_details" },
      { text = ", Leeds", kind = "address", source = "ner" },
    ]
    ```
    `detector` lists the suggestions the fake detector returns for the text. `found` lists, in order of start, everything `find_personal_data` must return, with `source` a `PiiSource` value. The table needs at least 16 rows. The owner should cover: each source beating a lower one, equal spans, a longer span beating a shorter one, a span cut on both sides, a role dropped by the allow-list, a role that is also a party short name, the governing-law place, a span across two sentences and across three, and a detector span that only holds white space.
  - **Files:** `src/clause_tracer/privacy/tests/tables/pipeline.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** Constitution T11.
  - **Depends on:** None

- [x] **S4-M3-T9: The entities table (Owner)**
  - **Build:** Owner only. The owner fills `src/clause_tracer/privacy/tests/tables/entities.toml`, in this format:
    ```toml
    [[case]]
    id = "ms-jones-joins-sarah-jones"
    text = "Sarah Jones then Ms Jones."
    suggestions = [
      { text = "Sarah Jones", kind = "person" },
      { text = "Ms Jones", kind = "person" },
    ]
    entities = [
      { id = "person-1", spans = [ { text = "Sarah Jones" }, { text = "Ms Jones" } ] },
    ]
    ```
    `nth` is optional in a suggestion and in a span, and defaults to 1. `entities` lists every entity `group_entities` must return, in order, and each entity's spans in order of start. The table needs at least 12 rows. The owner should cover: Spec 4.2 ("Ms. Jones", "Sarah" and "Sarah Jones" share one placeholder), a surname shared by two people, a company with Ltd and Limited, a company name without its suffix, an address and its first line, an email in two cases, a phone in two layouts, numbering when kinds are mixed, and a name that occurs in three places.
  - **Files:** `src/clause_tracer/privacy/tests/tables/entities.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** Constitution T11.
  - **Depends on:** None

- [ ] **S4-M3-T10: Table tests for the pipeline and the entities**
  - **Build:** In `src/clause_tracer/privacy/tests/test_pipeline_tables.py`, read `pipeline.toml` (allowed keys `id`, `sentences`, `parties`, `terms`, `detector`, `found`; required `id`, `sentences`, `found`) and `entities.toml` (allowed and required `id`, `text`, `suggestions`, `entities`) with `load_table`. For `pipeline.toml`: `case = make_case(sentences, parties=..., terms=...)`, with each party as `Party(name=..., address=... or None, yours=...)` and each term row as in S4-M2-T10 (a string gives a definition over the whole text); the detector is `FakePiiDetector({case.document.text: planted})`; a row `{text, kind, source, nth}` becomes `suggestion(case.document.text, text, as_enum(PlaceholderKind, kind, "kind"), as_enum(PiiSource, source, "source"), nth)`; the test asserts `find_personal_data(case, detector)` equals the expected tuple. For `entities.toml`: the document is `make_case([text]).document`; each suggestion row becomes a suggestion with source `RULE`; each expected entity `{id, spans}` becomes `PlaceholderEntity(id=id, kind=PlaceholderKind(id.rsplit("-", 1)[0]), number=int(id.rsplit("-", 1)[1]), spans=...)` with spans from `span_of`; the test asserts `group_entities(document, suggestions)` equals the expected tuple.
  - **Files:** `src/clause_tracer/privacy/tests/test_pipeline_tables.py`.
  - **Tests first:** `test_pipeline_table` (parametrised over the rows of `pipeline.toml`, by `id`); `test_pipeline_table_has_rows` (at least 16 rows); `test_entities_table` (parametrised over `entities.toml`); `test_entities_table_has_rows` (at least 12 rows).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_pipeline_tables.py` shows no failed test and the two has-rows tests pass, and `scripts/check.sh` exits 0. If a row fails, the code or the row is wrong: bring it to the owner, and never edit the table.
  - **Rules:** Constitution T11, testing strategy 10.
  - **Depends on:** S4-M3-T6, S4-M3-T7, S4-M3-T8, S4-M3-T9

- [ ] **S4-M3-T11: The planted-case strategy and the properties of the resolve step and of `find_personal_data`**
  - **Build:** In `src/clause_tracer/privacy/tests/strategies.py` (test code, not exported):
    - The file starts with these imports. The four kind names are aliases of `PlaceholderKind` members, so that the pool below runs as written:
      ```python
      from dataclasses import dataclass
      from typing import Final

      from hypothesis import HealthCheck, settings
      from hypothesis import strategies as st
      from hypothesis.strategies import DrawFn, SearchStrategy, composite

      from clause_tracer.core.enums import PiiSource, PlaceholderKind
      from clause_tracer.core.placeholders import PiiSuggestion
      from clause_tracer.core.tests.strategies import HAZARD_ALPHABET
      from clause_tracer.core.wording import Span
      from clause_tracer.privacy._spans import trimmed_span
      from clause_tracer.privacy.resolve import resolve_overlaps, trim_suggestions
      from clause_tracer.privacy.sample_input import PrivacyInput
      from clause_tracer.privacy.tests.case_builder import make_case

      PERSON: Final = PlaceholderKind.PERSON
      COMPANY: Final = PlaceholderKind.COMPANY
      ADDRESS: Final = PlaceholderKind.ADDRESS
      EMAIL: Final = PlaceholderKind.EMAIL
      ```
    - The pool of planted names:
      ```python
      POOL: Final[tuple[tuple[str, PlaceholderKind], ...]] = (
          ("Sarah Jones", PERSON),
          ("Ms Jones", PERSON),
          ("Sarah", PERSON),
          ("Zoë Brown", PERSON),
          ("Zed Corp", COMPANY),
          ("Brightline Studio", COMPANY),
          ("14 Harbour Street, Leeds LS1 4AB", ADDRESS),
          ("a@b.com", EMAIL),
      )
      ```
    - `PLAIN_ALPHABET: Final[tuple[str, ...]]`: the characters of `HAZARD_ALPHABET` (from `clause_tracer.core.tests.strategies`) for which `str.isspace()` is false.
    - `@dataclass(frozen=True, slots=True, kw_only=True) class PlantedCase` with `case: PrivacyInput`, `planted: tuple[PiiSuggestion, ...]` and `names: tuple[str, ...]`.
    - `@composite def planted_cases(draw) -> PlantedCase`. It draws 1 to 4 sentences. Each sentence is 1 to 5 pieces joined by one space. A piece is either a name from `POOL` or a plain text of 1 to 6 characters of `PLAIN_ALPHABET`. It draws a boolean first to choose which: when the boolean is true, the piece is a name from `POOL`; when it is false, the piece is a plain text. The case is `make_case(sentences)`. Each name piece gives one `NER` suggestion with its kind, over the exact place where the piece sits in the text (computed while the text is built, and `names` holds the name texts). When there are 2 or more sentences and `draw(st.booleans())` is true, it adds one more `NER` `ADDRESS` suggestion over the last character of one sentence, the space after it and the first character of the next sentence, for a sentence index it draws.
    - For the properties of the resolve step (the planner ran each at 5,000 examples with no failure on the reference code; the tests run `max_examples=1000`):
      ```python
      ALPHABET: Final[tuple[str, ...]] = tuple(HAZARD_ALPHABET) + (".", ",", "(", ")", " ", "A", "b")
      LAW_PLAIN_ALPHABET: Final[tuple[str, ...]] = tuple(c for c in ALPHABET if not c.isspace())
      LAW_POOL: Final[tuple[tuple[str, PlaceholderKind], ...]] = POOL + (
          ("England and Wales", ADDRESS),
          ("Wales", ADDRESS),
          ("Sam", PERSON),
      )
      LAW_SENTENCE: Final[str] = "This is governed by the laws of England and Wales."
      SETTINGS: Final[settings] = settings(
          max_examples=1000, deadline=None, suppress_health_check=list(HealthCheck), database=None
      )
      TEXTS: Final[SearchStrategy[str]] = st.text(alphabet=ALPHABET, max_size=40)
      OFFSETS: Final[SearchStrategy[object]] = st.one_of(
          st.integers(-3, 25),
          st.booleans(),
          st.floats(allow_nan=False, allow_infinity=False, min_value=-3, max_value=25),
          st.none(),
      )


      @composite
      def with_suggestions(draw: DrawFn) -> tuple[str, tuple[PiiSuggestion, ...]]:
          text = draw(TEXTS)
          raw: list[PiiSuggestion] = []
          for _ in range(draw(st.integers(0, 12))):
              a = draw(st.integers(0, len(text)))
              b = draw(st.integers(0, len(text)))
              raw.append(
                  PiiSuggestion(
                      span=Span(start=min(a, b), end=max(a, b)),
                      kind=draw(st.sampled_from(list(PlaceholderKind))),
                      source=draw(st.sampled_from(list(PiiSource))),
                  )
              )
          return text, trim_suggestions(text, raw)


      @composite
      def clean_input(draw: DrawFn) -> tuple[str, tuple[PiiSuggestion, ...]]:
          text = draw(TEXTS)
          cuts = sorted(draw(st.lists(st.integers(0, len(text)), max_size=8)))
          kept: list[PiiSuggestion] = []
          for a, b in zip(cuts[::2], cuts[1::2], strict=False):
              span = trimmed_span(text, Span(start=a, end=b))
              if (
                  span
                  and any(c.isalnum() for c in text[span.start : span.end])
                  and (not kept or kept[-1].span.end <= span.start)
              ):
                  kept.append(
                      PiiSuggestion(
                          span=span,
                          kind=draw(st.sampled_from(list(PlaceholderKind))),
                          source=draw(st.sampled_from(list(PiiSource))),
                      )
                  )
          return text, tuple(kept)


      @composite
      def with_starts(draw: DrawFn) -> tuple[str, tuple[PiiSuggestion, ...], list[int]]:
          text, suggestions = draw(with_suggestions())
          starts = sorted(set(draw(st.lists(st.integers(0, len(text)), max_size=8))))
          return text, resolve_overlaps(text, suggestions), starts
      ```
    - `@composite def law_cases(draw) -> PlantedCase`, the case of property P11. It draws `count` from 1 to 4 sentences. For each sentence it records its start, and when `draw(st.booleans())` is true and then `draw(st.integers(0, 3)) == 0` the sentence is the one piece `LAW_SENTENCE`; otherwise it is 1 to 5 pieces, each (by `draw(st.booleans())`) a name drawn from `LAW_POOL` or a plain text of 1 to 6 characters of `LAW_PLAIN_ALPHABET`. Pieces are joined by one space and sentences by one space, as `make_case` does. Each name piece gives one `NER` suggestion with its kind over its exact place. When a sentence is `LAW_SENTENCE` and `draw(st.booleans())` is true, it adds one suggestion that runs from the start of `laws` to the end of `Wales`, the character before the final full stop (so it runs into the place), with a kind drawn from all kinds and a source drawn from `NER`, `RULE` and `PATTERN`. When `count >= 2` and `draw(st.booleans())` is true, it adds one `NER` `ADDRESS` suggestion from `e - 2` to `e + 1`, where `e` is the start of the sentence with the index `i + 1` and `i = draw(st.integers(0, count - 2))`. It drops every suggestion that ends after the text. The case is `make_case(sentences)`.
  - **Files:** `src/clause_tracer/privacy/tests/strategies.py`, `src/clause_tracer/privacy/tests/test_finding_properties.py`, `src/clause_tracer/privacy/tests/test_resolve_properties.py`.
  - **Tests first:** in `test_finding_properties.py`, each property has `@SETTINGS` on the line above `@given(planted_cases())`, so that it runs with the `SETTINGS` object (`max_examples=1000`), and runs `find_personal_data(planted.case, FakePiiDetector({text: planted.planted}))`:
    - `test_output_is_sorted_apart_and_inside_the_text` (every span satisfies `0 <= start < end <= len(text)`, the list is sorted by start, and each span ends at or before the start of the next);
    - `test_no_span_holds_a_sentence_start` (no span has a sentence start `c` with `start < c < end`);
    - `test_every_flagged_letter_and_digit_is_covered` (for every planted suggestion and every index `i` in its span for which `text[i].isalnum()`, some result span holds `i`: the stage's rule that a span is cut and never dropped, question 9);
    - `test_a_strategy_case_has_a_valid_input` (`dump_privacy_fixture(planted.case)` does not raise; this runs no finder).
    In `test_resolve_properties.py`, each property has `@SETTINGS` on the line above `@given(...)`, so that it runs with the `SETTINGS` object (`max_examples=1000`). `cover(suggestions)` is the set of indexes held by any span; `alnum(text, indexes)` is the indexes with `text[i].isalnum()`; `R(text, suggestions)` is `resolve_overlaps(text, suggestions)`. P1 to P9 use `with_suggestions()` unless said otherwise. Added on 21 Nov 2026 (the properties of the report, track A3; owner to confirm):
    - `test_p1_output_is_disjoint_sorted_trimmed_and_inside` (every result span satisfies `0 <= start < end <= len(text)` and neither end is white space; neighbouring results are sorted by start and the earlier ends at or before the start of the later);
    - `test_p2_no_letter_or_digit_is_uncovered` (`alnum(text, cover(suggestions)) <= cover(R(text, suggestions))`);
    - `test_p3_no_span_is_invented` (every index of every result has an input suggestion with the same kind and source that holds it);
    - `test_p4_source_priority_decides_each_character` (for every index in `alnum(text, cover(suggestions))`, the result spans that hold it are exactly one, and its source has the smallest `SOURCE_PRIORITY` among the input suggestions that hold the index);
    - `test_p5_resolve_is_idempotent` (`R(text, R(text, suggestions)) == R(text, suggestions)`);
    - `test_p6_resolve_ignores_input_order` (a shuffle of the suggestions, drawn with `st.randoms(use_true_random=False)`, gives the same result);
    - `test_p7_an_extra_suggestion_never_uncovers` (with one more suggestion drawn with `st.data()`, `alnum(text, cover(R(text, suggestions)))` is a subset of the same set for the list with the extra one);
    - `test_p8_clean_input_is_unchanged` (over `clean_input()`: `R(text, suggestions)` equals the suggestions sorted by `(start, end)`);
    - `test_p9_split_keeps_cover_kind_and_source` (over `with_starts()`, `out = split_at_sentences(text, resolved, starts)`: no result span holds a start strictly inside it; each result lies inside a `resolved` suggestion of the same kind and source; `alnum(text, cover(resolved)) <= cover(out)`; each `resolved` suggestion with no start strictly inside it is in `out`; splitting `out` again gives `out`; `out` equals itself sorted by `order_key` and has no duplicate; and the reversed `resolved` gives the same `out`);
    - `test_p10_the_check_raises_exactly_for_bad_spans` (over `TEXTS` and a list of up to 6 rows of `(OFFSETS, OFFSETS, kind, source)`, each built as `PiiSuggestion(span=Span(start=cast(int, a), end=cast(int, b)), ...)`: a span is bad when an offset is not an `int` or is a `bool`, or `a < 0`, `b < 0`, `a > len(text)`, `b > len(text)` or `b < a`. When `trim_suggestions(text, rows)` raises, it is a `ValueError` whose message starts `privacy: ` and some span is bad; otherwise no span is bad and the kinds and sources of the result equal those of the input rows whose text is not blank);
    - `test_p11_the_composed_pipeline_cuts_at_the_place` (over `law_cases()`: `out = find_personal_data(planted.case, FakePiiDetector({text: planted.planted}))`; `places = governing_law_places(text)`; every index `i` with `text[i].isalnum()` that some planted suggestion holds and that lies in no place span is held by some result span; and no result span holds a sentence start strictly inside it);
    - `test_p12_a_name_that_touches_the_place_is_hidden_whole` (over `law_cases()`, the same `out` and `places`: for every planted suggestion of kind `PERSON` or `COMPANY` whose source is not `USER` and whose span overlaps a place span, every index of its span with `text[i].isalnum()` is held by some result span, the place indexes included).
    A mutant of `resolve_overlaps` that drops the lower span whole fails P2, P4 and P11; a mutant of `cut_in_places` that drops the whole span fails P11; a mutant that cuts a `PERSON` or `COMPANY` span at the place instead of keeping it whole fails P12 and passes P11. The rank table `TIE_RANK` is not covered by a property (a plain kind order passes P6): it is covered by the three tie tests of S4-M3-T4.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_finding_properties.py src/clause_tracer/privacy/tests/test_resolve_properties.py` reports 16 passed, and `scripts/check.sh` exits 0. Every bug that a property finds becomes a committed `@example` (Constitution T6).
  - **Rules:** Testing strategy 5 (the hazard alphabet) and 14, Constitution T6.
  - **Depends on:** S4-M3-T6, S4-M1-T5, S4-M3-T1, S4-M3-T3, S4-M3-T4, S4-M3-T5

### M4: Placeholder text

When this is done, `anonymise` builds the `PlaceholderText` with its segment map, and the three restore calls work on it: the whole text, the tokens in an AI reply, and a span in the sent text.

- [ ] **S4-M4-T1: Placeholder tokens and escapes**
  - **Build:** In `src/clause_tracer/privacy/_tokens.py`: `LABELS: Final[Mapping[PlaceholderKind, str]] = MappingProxyType({PERSON: "Person", COMPANY: "Company", ADDRESS: "Address", EMAIL: "Email", PHONE: "Phone", ID: "ID", BANK: "Bank"})`; `ESCAPES: Final[Mapping[str, str]] = MappingProxyType({PLACEHOLDER_OPEN: "[", PLACEHOLDER_CLOSE: "]"})`; and `def placeholder_token(kind: PlaceholderKind, number: int) -> str`, which returns `f"{PLACEHOLDER_OPEN}{LABELS[kind]} {number}{PLACEHOLDER_CLOSE}"` and raises `ValueError("privacy: a placeholder number starts at 1")` when `number < 1`. The token has the form that the scan of `core` reads (`PLACEHOLDER_PATTERN` in `core/scans.py`), so `⟦Person 1⟧` is a known placeholder there.
  - **Files:** `src/clause_tracer/privacy/_tokens.py`, `src/clause_tracer/privacy/tests/test_tokens.py`.
  - **Tests first:** in `test_tokens.py`: `test_person_token` (`placeholder_token(PlaceholderKind.PERSON, 1) == "⟦Person 1⟧"`); `test_id_token` (`placeholder_token(PlaceholderKind.ID, 12) == "⟦ID 12⟧"`); `test_number_zero_raises` (`ValueError`); `test_every_kind_has_a_label` (`set(LABELS) == set(PlaceholderKind)`); `test_token_is_one_marker_group` (one test with a loop over every kind: `re.fullmatch("⟦[^⟧]*⟧", placeholder_token(kind, 3))` matches); `test_escapes` (`ESCAPES == {"⟦": "[", "⟧": "]"}`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_tokens.py` reports 6 passed, and `scripts/check.sh` exits 0.
  - **Rules:** Spec 4.2 (placeholder types, a marker that contract text cannot contain), testing strategy 8 (the marker `⟦Person 1⟧`), question 10.
  - **Depends on:** None

- [ ] **S4-M4-T2: `anonymise` and the segment map**
  - **Build:** In `src/clause_tracer/privacy/placeholder.py`: `def anonymise(document: Document, entities: Sequence[PlaceholderEntity]) -> PlaceholderText`. The checks run in this order, and the first failure raises `ValueError` with this message: an entity id that an earlier entity has (`privacy: duplicate entity id`); a `(kind, number)` that an earlier entity has (`privacy: duplicate placeholder`); an entity with no span (`privacy: entity has no span`); a span with `start < 0` or `end > len(document.text)` (`privacy: entity span is outside the text`), and then a span with `start >= end` (`privacy: entity span is empty`), each check over all spans before the next. `Span` itself checks nothing, so these checks are the only guard; two spans, in one entity or in two, that overlap (`privacy: entity spans overlap`); a number below 1 (`privacy: a placeholder number starts at 1`, from `placeholder_token`). Each check runs over all entities before the next check starts, in the order listed, and a placeholder number below 1 is checked in its own pass after the overlap check. Then walk the text from left to right over all spans sorted by start. A stretch of the original with no entity (a gap) is cut into segments: each character `⟦` or `⟧` is its own `ESCAPE` segment and is written to the sent text as `ESCAPES[character]`; each run of other characters is one `COPY` segment, written as it is. Each entity span is one `ENTITY` segment: the sent text gets `placeholder_token(entity.kind, entity.number)`. `Segment(kind, sent, original, entity_id)` has `sent` the span in the sent text and `original` the span in `document.text`; `entity_id` is the entity's id for `ENTITY` and `None` otherwise. A gap of zero length makes no segment. The result is `PlaceholderText(text=sent_text, entities=tuple(entities), segments=tuple(segments))`. The sent spans tile `[0, len(sent_text))` and the original spans tile `[0, len(document.text))` with no gap and no overlap.
  - **Files:** `src/clause_tracer/privacy/placeholder.py`, `src/clause_tracer/privacy/tests/test_anonymise.py`.
  - **Tests first:** in `test_anonymise.py`, with `entity(id, kind, number, *spans)` and `document(text)` helpers (`document(text)` is `make_case([text]).document`, and `document("")` is `make_case([]).document`):
    - `test_entities_become_tokens` (text `"Hi Sam, hi Sam."`, entity `person-1` (`PERSON`, 1) over 3 to 6 and 11 to 14: the sent text is `"Hi ⟦Person 1⟧, hi ⟦Person 1⟧."`, and the segments are `(COPY, sent 0-3, original 0-3, None)`, `(ENTITY, 3-13, 3-6, "person-1")`, `(COPY, 13-18, 6-11, None)`, `(ENTITY, 18-28, 11-14, "person-1")`, `(COPY, 28-29, 14-15, None)`);
    - `test_marker_characters_are_escaped` (text `"a ⟦b⟧ c"`, no entities: the sent text is `"a [b] c"`, and the segments are `(COPY, 0-2, 0-2)`, `(ESCAPE, 2-3, 2-3)`, `(COPY, 3-4, 3-4)`, `(ESCAPE, 4-5, 4-5)`, `(COPY, 5-7, 5-7)`, each with `entity_id` `None`);
    - `test_an_escape_next_to_an_entity` (text `"⟦Sam"`, entity `person-1` over 1 to 4: the sent text is `"[⟦Person 1⟧"`, and the segments are `(ESCAPE, 0-1, 0-1)` and `(ENTITY, 1-11, 1-4, "person-1")`);
    - `test_an_entity_over_a_marker_is_replaced_whole` (text `"x⟦y"`, entity over 1 to 3: the sent text is `"x⟦Person 1⟧"`, with segments `(COPY, 0-1, 0-1)` and `(ENTITY, 1-11, 1-3, ...)`);
    - `test_no_entities_copies_the_text` (`document("abc")` gives the sent text `"abc"` and one `COPY` segment 0-3; the text `""` gives no segment);
    - `test_entities_are_kept_as_given` (`result.entities == tuple(entities)` for two entities);
    - `test_two_kinds_have_their_own_tokens` (an `ADDRESS` entity number 2 gives the token `⟦Address 2⟧`);
    - `test_duplicate_entity_id_raises`; `test_duplicate_placeholder_raises` (two ids, the same kind and number); `test_entity_without_a_span_raises`; `test_empty_span_raises`; `test_span_outside_the_text_raises` (an end past the text, and a span with `start=-1`); `test_overlapping_spans_raise` (two entities with spans 0-3 and 2-5); `test_number_below_one_raises` (each raises `ValueError` with the message given above).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_anonymise.py` reports 14 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, Spec 4.2 (escaping), the seams report ("escaped characters get their own segment kind"), question 10, D3 (the map holds spans, not copies of names).
  - **Depends on:** S4-M4-T1, S4-M1-T5

- [ ] **S4-M4-T3: `restore_text`, the whole text back**
  - **Build:** In `placeholder.py`: `def restore_text(placeholder: PlaceholderText, document: Document) -> str`. It first checks the segments, and raises `ValueError("privacy: segments do not tile the texts")` when any of these is false: the sent spans run one after another from 0 to `len(placeholder.text)`; the original spans run one after another from 0 to `len(document.text)`; a `COPY` segment has equal lengths on both sides; an `ESCAPE` segment has length 1 on both sides; an `ENTITY` segment has an original span of length 1 or more. Then it joins, in order, `placeholder.text[sent]` for each `COPY` segment, and `document.text[original]` for each `ESCAPE` and `ENTITY` segment. The text that a `COPY` segment contributes comes from the placeholder text, so a change in the sent text shows in the result.
  - **Files:** `src/clause_tracer/privacy/placeholder.py`, `src/clause_tracer/privacy/tests/test_restore_text.py`.
  - **Tests first:** in `test_restore_text.py`, with `anonymise` over the cases of S4-M4-T2: `test_restore_gives_the_original` (the text `"Hi Sam, hi Sam."` with its entity); `test_restore_gives_the_original_with_escapes` (the text `"a ⟦b⟧ ⟦Sam⟧"` with an entity over `Sam`); `test_restore_of_an_empty_text` (`""` gives `""`); `test_a_copy_comes_from_the_sent_text` (`dataclasses.replace(placeholder, text=...)` with one character of a `COPY` segment changed gives a result with that character changed); `test_a_gap_in_the_segments_raises` (a `PlaceholderText` whose second segment starts one character late raises `ValueError("privacy: segments do not tile the texts")`); `test_a_wrong_length_raises` (the document `"abcd"`, the placeholder text `"abc"` with `entities=()`, and the segments `(COPY, sent 0-2, original 0-3)` and `(COPY, sent 2-3, original 3-4)`: the sent spans and the original spans each tile their text, but the first `COPY` has unequal lengths, so it raises the same error); `test_an_empty_entity_original_raises` (the document `"ab"`, the placeholder text `"⟦Person 1⟧ab"` with `entities=()`, and the segments `(ENTITY, sent 0-10, original 0-0)` and `(COPY, sent 10-12, original 0-2)`: it raises the same error).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_restore_text.py` reports 7 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, system design 4.2, testing strategy 5 (invariant 3: restore undoes anonymise), question 6.
  - **Depends on:** S4-M4-T2

- [ ] **S4-M4-T4: `restore_reply`, the tokens in an AI reply**
  - **Build:** In `placeholder.py`: `def restore_reply(placeholder: PlaceholderText, document: Document, reply: str) -> str`. Build a map from each entity's token (`placeholder_token(entity.kind, entity.number)`) to `document.text[span]`, where `span` is the entity's span with the smallest `start`. With `TOKEN_RE = re.compile(re.escape(PLACEHOLDER_OPEN) + "[^" + re.escape(PLACEHOLDER_CLOSE) + "]*" + re.escape(PLACEHOLDER_CLOSE))`, replace each match in `reply` by its value in the map. A match that is not in the map raises `ValueError("privacy: unknown placeholder")` (Spec 8.4: an unknown placeholder counts as a broken reply). Text outside a match, including a lone `⟦` and a `[` or `]`, is left as it is. The first variant of a name is the one that comes back (question 6).
  - **Files:** `src/clause_tracer/privacy/placeholder.py`, `src/clause_tracer/privacy/tests/test_restore_reply.py`.
  - **Tests first:** in `test_restore_reply.py`, over the text `"Sarah Jones then Ms Jones at Brightline Studio Ltd."` with the entities `person-1` (spans over `Sarah Jones` and `Ms Jones`) and `company-1` (over `Brightline Studio Ltd`), anonymised: `test_a_known_placeholder_comes_back` (`"Ask ⟦Person 1⟧ to pay."` gives `"Ask Sarah Jones to pay."`); `test_the_first_place_gives_the_variant` (the same entity with its spans given in the order `Ms Jones`, `Sarah Jones` still gives `Sarah Jones`, because that span starts first); `test_several_placeholders` (`"⟦Person 1⟧ and ⟦Company 1⟧"` gives `"Sarah Jones and Brightline Studio Ltd"`); `test_an_unknown_placeholder_raises` (`"⟦Person 9⟧"` raises `ValueError` whose message is `privacy: unknown placeholder`); `test_text_without_placeholders_is_unchanged` (`"No names [Person 1] here"` is returned as it is); `test_an_odd_marker_raises` (`"⟦ ⟧"` raises `ValueError`); `test_a_lone_open_marker_is_left` (`"a ⟦ b"` is returned as it is).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_restore_reply.py` reports 7 passed, and `scripts/check.sh` exits 0.
  - **Rules:** Spec 6.1 (placeholders are put back in what comes back), Spec 8.4, ADR 0008 (amendment), I7.
  - **Depends on:** S4-M4-T2

- [ ] **S4-M4-T5: `map_to_original`, a span in the sent text back to the contract**
  - **Build:** In `placeholder.py`: `def map_to_original(placeholder: PlaceholderText, span: Span) -> Span`. It first raises `ValueError("privacy: span is outside the placeholder text")` when `span.start < 0` or `span.end > len(placeholder.text)`, and then `ValueError("privacy: an empty span has no place")` when `span.start >= span.end`. Let `first` be the segment whose `sent` holds the index `span.start` and `last` the segment whose `sent` holds the index `span.end - 1` (find both with `bisect` on the sent starts of the segments). The original start is `first.original.start` when `first.kind` is `ENTITY`, else `first.original.start + (span.start - first.sent.start)`. The original end is `last.original.end` when `last.kind` is `ENTITY`, else `last.original.start + (span.end - last.sent.start)`. An edge that falls inside a placeholder snaps out to the whole name (the seams report).
  - **Files:** `src/clause_tracer/privacy/placeholder.py`, `src/clause_tracer/privacy/tests/test_map_to_original.py`.
  - **Tests first:** in `test_map_to_original.py`, over `anonymise` of `"Hi Sam, hi Sam."` with entity `person-1` over 3 to 6 and 11 to 14 (the sent text `"Hi ⟦Person 1⟧, hi ⟦Person 1⟧."`): `test_a_copy_span_maps_by_a_shift` (`Span(15, 17)` gives `Span(8, 10)`); `test_a_start_inside_a_placeholder_snaps_out` (`Span(5, 15)` gives `Span(3, 8)`); `test_an_end_inside_a_placeholder_snaps_out` (`Span(0, 5)` gives `Span(0, 6)`); `test_a_span_over_a_placeholder_and_a_copy` (`Span(2, 14)` gives `Span(2, 7)`); `test_the_last_placeholder_to_the_end` (`Span(18, 29)` gives `Span(11, 15)`); `test_a_span_in_an_escape` (over `anonymise` of `"a ⟦b⟧ c"`, `Span(2, 3)` gives `Span(2, 3)`); `test_an_empty_span_raises` (`Span(4, 4)`); `test_a_span_outside_the_text_raises` (`Span(0, 30)`, and `Span(-1, 2)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_map_to_original.py` reports 8 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, system design 4.2 (the offset chain), testing strategy 5 (invariant 3).
  - **Depends on:** S4-M4-T2

- [ ] **S4-M4-T6: Properties of invariant 3**
  - **Build:** In `src/clause_tracer/privacy/tests/test_placeholder_properties.py`, with `planted_cases()` of S4-M3-T11. A helper `pipeline(planted: PlantedCase) -> tuple[PlaceholderText, tuple[PlaceholderEntity, ...]]` runs `find_personal_data` with `FakePiiDetector({text: planted.planted})`, then `group_entities`, then `anonymise`. Each property has `@SETTINGS` (the object of S4-M3-T11, `max_examples=1000`) on the line above `@given(planted_cases())`.
  - **Files:** `src/clause_tracer/privacy/tests/test_placeholder_properties.py`.
  - **Tests first:** `test_restore_undoes_anonymise` (`restore_text(placeholder, document) == document.text`); `test_segments_tile_both_texts` (the sent spans run one after another from 0 to `len(placeholder.text)`, the original spans from 0 to `len(document.text)`, and `COPY` and `ESCAPE` segments have equal lengths); `test_no_entity_crosses_a_sentence_start` (no span of any entity holds a sentence start strictly inside it); `test_markers_only_in_entities` (the count of `⟦` in `placeholder.text` and the count of `⟧` each equal the number of `ENTITY` segments, and the text of each `ENTITY` segment is the token of its entity); `test_copy_spans_map_back_exactly` (for each `COPY` segment with at least 2 characters, the span from its second character to its end maps to a span of the original whose text equals `placeholder.text[start:end]`); `test_tokens_in_a_reply_come_back` (a reply made of every entity's token joined by `" | "` is restored to the first-span texts joined by `" | "`); `test_no_planted_name_is_left_in_the_sent_text` (no name of `planted.names`, folded with `casefold()`, is a substring of `placeholder.text.casefold()`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_placeholder_properties.py` reports 7 passed, and `scripts/check.sh` exits 0. Every bug that a property finds becomes a committed `@example` (Constitution T6).
  - **Rules:** Testing strategy 5 (invariant 3), 8 and 14, Constitution T6 and T13.
  - **Depends on:** S4-M3-T6, S4-M3-T7, S4-M3-T11, S4-M4-T3, S4-M4-T4, S4-M4-T5

### M5: Public calls and the sample

When this is done, `python -m clause_tracer.privacy` prints the entities and the placeholder text of the sample, a golden file and the owner's sample table pin the result, and the module's README states every contract.

- [ ] **S4-M5-T1: The printed report**
  - **Build:** In `src/clause_tracer/privacy/render.py`: `def render_privacy_report(case: PrivacyInput, entities: Sequence[PlaceholderEntity], placeholder: PlaceholderText) -> str`. Every line ends with `"\n"`, and fields are separated by one tab. In a free-text field, each tab, carriage return and line break is replaced by one space. The lines, in this order: (1) `source`, `case.document.source.name`, `len(case.document.text)`. (2) `counts`, `entities N`, `spans N`, `segments N` (the number of entities, of spans over all entities, and of segments of `placeholder`). (3) One `entity` line for each entity in the order given: `entity`, the id, `f"{LABELS[kind]} {number}"`, `places N` (the number of spans). (4) For each entity in that order, one `span` line for each span sorted by start: `span`, the entity id, `start-end`, the original text of the span (free text). (5) One `text` line for each piece of `placeholder.text.split("\n")`: `text`, the piece (free text). It reads no file and prints nothing.
  - **Files:** `src/clause_tracer/privacy/render.py`, `src/clause_tracer/privacy/tests/test_render.py`.
  - **Tests first:** in `test_render.py`: `test_report_lines` (`make_case(["Hi Sam."])`, entity `person-1` over 3 to 6, anonymised: `"source\tcase.txt\t7\ncounts\tentities 1\tspans 1\tsegments 3\nentity\tperson-1\tPerson 1\tplaces 1\nspan\tperson-1\t3-6\tSam\ntext\tHi ⟦Person 1⟧.\n"`); `test_no_entities` (`make_case(["Hi."])` with no entities gives `"source\tcase.txt\t3\ncounts\tentities 0\tspans 0\tsegments 1\ntext\tHi.\n"`); `test_tabs_are_replaced_in_free_text` (the test starts from `case = make_case(["x"])` and builds `dataclasses.replace(case, document=dataclasses.replace(case.document, text="a\tb"))`; the entity `person-1` is over 0 to 3; the span line is `"span\tperson-1\t0-3\ta b\n"`); `test_a_line_break_in_the_sent_text_gives_two_text_lines` (a `PlaceholderText` with `text="a\nb"` and no segments: the last two lines are `text\ta` and `text\tb`); `test_report_ends_with_a_newline`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_render.py` reports 5 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1 (the function returns a string; only `__main__` prints), S1.
  - **Depends on:** S4-M4-T2

- [ ] **S4-M5-T2: Run `privacy` alone**
  - **Build:** Replace `src/clause_tracer/privacy/__main__.py` with the pattern of [`links/__main__.py`](../../src/clause_tracer/links/__main__.py): `DEFAULT_INPUT = Path(__file__).parent / "samples" / "developer-agreement.privacy.json"`, `EXIT_INPUT_FILE = 3`, and `def main(argv: list[str] | None = None) -> int` with `argparse.ArgumentParser(prog="python -m clause_tracer.privacy")` and `--input` (a `Path`, default `DEFAULT_INPUT`). It reads the file as UTF-8 (an `OSError` prints `clause_tracer.privacy: cannot read <path>` to standard error and returns 3; unlike `links`, a `ValueError` from the read, which is a file that is not UTF-8, prints the same `cannot read <path>` line and returns 3), loads it with `load_privacy_fixture` (a `ValueError` prints `clause_tracer.privacy: <message>` to standard error and returns 3), then computes `suggestions = find_personal_data(case, FakePiiDetector({}))`, `entities = group_entities(case.document, suggestions)` and `placeholder = anonymise(case.document, entities)`, prints `render_privacy_report(case, entities, placeholder)` with `end=""` and returns 0. The detector is the empty fake, so the run shows what code alone finds. Change `tests/test_smoke.py` to call `main([])`.
  - **Files:** `src/clause_tracer/privacy/__main__.py`, `src/clause_tracer/privacy/tests/test_smoke.py`, `src/clause_tracer/privacy/tests/test_main.py`.
  - **Tests first:** in `test_main.py`, with `capsys`: `test_main_prints_the_sample_report` (`main([])` returns 0, and the standard output starts with `"source\tdeveloper-agreement.txt\t6204\n"`); `test_main_reads_another_input` (a fixture written to `tmp_path` with `dump_privacy_fixture(make_case(["Hi Sam."]))` and given with `--input` prints a report that starts `source\tcase.txt\t7`); `test_a_missing_file_returns_3` (`main(["--input", str(tmp_path / "none.json")])` returns 3, standard output is empty, and standard error starts `clause_tracer.privacy: cannot read`); `test_a_bad_fixture_returns_3` (a file that holds `{` returns 3, and standard error is `clause_tracer.privacy: privacy sample: not JSON\n`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_main.py src/clause_tracer/privacy/tests/test_smoke.py` reports 5 passed, and `.venv/bin/uv run python -m clause_tracer.privacy` prints the report and exits 0, and `scripts/check.sh` exits 0.
  - **Rules:** S1 and S2 (a module runs alone), I12 (clear flag names, exit codes, errors to standard error), system design 6.2 (exit code 3, "input file").
  - **Depends on:** S4-M5-T1, S4-M1-T4, S4-M3-T6, S4-M3-T7

- [ ] **S4-M5-T3: The golden file**
  - **Build:** Create `src/clause_tracer/privacy/tests/test_goldens.py`: `GOLDENS = Path(__file__).parent / "goldens"` and `test_report_matches_its_golden(check_golden)`, which loads `DEFAULT_INPUT` with `load_privacy_fixture`, runs the same three calls as `main`, and calls `check_golden(GOLDENS / "developer-agreement.privacy.txt", render_privacy_report(...))`. Generate the golden with `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_goldens.py --update-goldens` in one commit that holds the test and the golden file and no other file, and read it against the sample by hand (Constitution T11): the report must show the seven entities and the ten spans named below. The owner reads it in S4-M5-T7. Add `goldens/` to the module's README as "written only by `--update-goldens`".
  - **Files:** `src/clause_tracer/privacy/tests/test_goldens.py`, `src/clause_tracer/privacy/tests/goldens/developer-agreement.privacy.txt`.
  - **Tests first:** `test_report_matches_its_golden`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_goldens.py` reports 1 passed without `--update-goldens`, and `scripts/check.sh` exits 0. The golden has 7 `entity` lines (`company-1`, `id-1`, `address-1`, `person-1`, `address-2`, `email-1`, `person-2`, in that order) and 10 `span` lines, as the planner computed on 21 Nov 2026; if the count differs, stop and bring it to the owner. The `id-1` span line is `span<TAB>id-1<TAB>169-177<TAB>09876543` (the value only, owner decision of 21 Nov 2026; before it the span was 154 to 177 and held `company number 09876543`), and the `text` lines read `company number ⟦ID 1⟧`. The source length is 6204. No other entity or span changes. The figures are the planner's (owner to confirm in S4-M5-T7).
  - **Rules:** T11, ADR 0013 (golden files), testing strategy 3.
  - **Depends on:** S4-M5-T2

- [ ] **S4-M5-T4: Public names, contract notes and the README**
  - **Build:** In `src/clause_tracer/privacy/__init__.py`, set `__all__` to exactly these ten names, imported from their files: `PrivacyInput`, `anonymise`, `dump_privacy_fixture`, `find_personal_data`, `group_entities`, `load_privacy_fixture`, `map_to_original`, `render_privacy_report`, `restore_reply`, `restore_text`. Create `src/clause_tracer/privacy/tests/test_architecture.py` with the three tests of [`links/tests/test_architecture.py`](../../src/clause_tracer/links/tests/test_architecture.py) for `privacy`: `test_public_names`, `test_module_has_its_parts` (`README.md`, `tests`, `samples`, `__main__.py`) and `test_readme_names_every_public_name`. Rewrite `src/clause_tracer/privacy/README.md` with these parts, in this order: **Purpose** (one sentence); **Spec** (sections 4.2, 6.1 steps 3 and 4, 8); **Input shape** (`PrivacyInput`, and the detector port); **Output shape** (`PiiSuggestion`, `PlaceholderEntity`, `PlaceholderText` with its three segment kinds); **Public calls**, with a contract note for each of the ten names (input, output, errors raised with their messages, side effects: none; Constitution I11); **Rules** (the source priority and the cut rule, the allow-list and the question 11 reading, the governing-law place, the sentence cut, variant grouping and the ambiguous short form, token form and numbering, the escape form, which variant `restore_reply` returns, how `map_to_original` snaps an edge, and that the entities and the map hold real names, so they must stay out of logs); **The printed report** (a table with the columns `Line` and `Fields after the first word`, one row for each of `source`, `counts`, `entity`, `span`, `text`, in order, and the sentence "Every free-text field has each tab, carriage return and line break replaced by one space."); **Sample fixture** (kept from S4-M1-T3); **Known limits** (see below); **Depends on** (core only; the detector is passed in by `cli`); **Run alone** (the command and `--input`). The known limits are: a person who is not a typed party and has no honorific, signature or job title is found only by the detector; a name or an address that wraps over a line break is found by the typed party finder only; a lower-priority suggestion is cut, so the part outside a kept span may be a fragment; punctuation-only fragments are dropped; an NER match does not remove a defined term from the allow-list; only `Ltd` and `Limited` swap; the address rule reads UK, US, Canadian and street-word styles, and an address chain longer than 5 comma segments or 120 characters keeps its last part hidden (the nearest segments before the postcode, at most 5 and at most 120 characters) and its earlier part readable, and a chain whose nearest segment alone passes 120 characters gives the postcode alone; IBAN length per country is not checked; a company name, a person name or a street word that starts with a capital outside Latin-1, such as `Łukasz` or a Greek or Cyrillic name, is not found (the patterns read A to Z and the Latin-1 capitals, S4-M2-T13 and S4-M2-T14); a US state code that is also a word (`ID`, `OK`, `OR`, `IN`, `ME`, `HI`, `LA`, `DE`) before five digits is replaced as a ZIP, so `Employee ID 12345` becomes an address (owner decision of 22 Nov 2026); an honorific before a company name stays inside the company span (`Mr Brightline Studio Ltd`); non-UK bank formats and national ID numbers other than the NINO are left to the detector; a bare 8-digit company number needs a keyword, and only the 15 prefixes of `COMPANY_PREFIX` are found; a GB VAT number is found bare only with the `GB` prefix; a cue-less number that passes the Luhn check and starts with 3, 4, 5 or 6 is replaced as a card, and a card in 4-6-5 spacing is not found; a NINO in lower case is not found; the governing-law rule keeps only the places of a closed list that the owner writes, and two wordings of the clause; a phone shape with no cue gate also replaces a reference such as `ref 0123 456 7890`; a keyword ID value can run into a following number (`1234567 5`); a common-word name (layer 3) at the start of a sentence stays readable when no honorific, `'s` or earlier use shows it is a name; a defined term that only the detector flags, with no finder naming the full name, stays readable (it is allowed); only `NER` spans are joined when they overlap.
  - **Files:** `src/clause_tracer/privacy/__init__.py`, `src/clause_tracer/privacy/README.md`, `src/clause_tracer/privacy/tests/test_architecture.py`.
  - **Tests first:** `test_public_names` (the set equals the ten names), `test_module_has_its_parts`, `test_readme_names_every_public_name`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_architecture.py` reports 3 passed, `.venv/bin/uv run python scripts/copy_lint.py` exits 0, and `scripts/check.sh` exits 0. Every line kind of the golden file matches a row of the report table.
  - **Rules:** Constitution S3 (shapes in the README) and I11 (a contract note on each public call), B2.
  - **Depends on:** S4-M5-T3, S4-M4-T3, S4-M4-T4, S4-M4-T5

- [x] **S4-M5-T5: The sample table (Owner)**
  - **Build:** Owner only. The owner fills `src/clause_tracer/privacy/tests/tables/sample.toml`, in this format:
    ```toml
    [[case]]
    id = "company-1"
    kind = "entity"
    entity_kind = "company"
    number = 1
    spans = [ { text = "Brightline Studio Ltd", nth = 1 }, { text = "Brightline Studio Ltd", nth = 2 } ]

    [[case]]
    id = "kept-england-and-wales"
    kind = "kept"        # the text must stay in the placeholder text, and no entity may overlap it
    text = "England and Wales"
    nth = 2

    [[case]]
    id = "gone-harbour-street"
    kind = "gone"        # the text must not occur in the placeholder text, in any letter case
    text = "Harbour Street"
    ```
    The rows of kind `entity` list every entity code alone must find on the sample, with its `entity_kind` (a `PlaceholderKind` value), its `number` and all its spans (the text, and `nth` when the text occurs more than once in `Document.text`). A `kept` or `gone` row has `text`, and `nth` for a `kept` row (default 1). The owner covers every entity of Spec 14.5, every name and address of it as a `gone` row (including each word of "Sarah Jones", "Karim Benali", the two addresses, the email and the number `09876543`; the words `company number` stay), and, as `kept` rows, the amounts, dates, durations, defined roles and places that Spec 4.2 keeps: for example `£9,600`, `5 November 2026`, `60 days`, `12 months`, `the Agency`, `the Developer`, `Business Days`, `England and Wales`, and the web address in 5.5.
  - **Files:** `src/clause_tracer/privacy/tests/tables/sample.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** Constitution T11, Spec 14.5, Spec 4.2.
  - **Depends on:** None

- [ ] **S4-M5-T6: Sample tests: the table, the leak check and the kept roles**
  - **Build:** Two test files.
    - `src/clause_tracer/privacy/tests/test_sample_table.py`: load `sample.toml` with `load_table` (allowed keys `id`, `kind`, `entity_kind`, `number`, `spans`, `text`, `nth`; required `id`, `kind`). With `case = load_privacy_fixture(DEFAULT_INPUT.read_text(encoding="utf-8"))` and the three calls of `main`, check: `test_entities_match_the_table` (the entities equal the `entity` rows: for each row, `PlaceholderEntity(id=f"{entity_kind}-{number}", kind=..., number=..., spans=...)` with spans from `span_of(document.text, text, nth)`; and the number of entities equals the number of `entity` rows); `test_kept_rows` (each `kept` row's text occurs in `placeholder.text`, and its span in `document.text` overlaps no entity span); `test_gone_rows` (no `gone` text occurs in `placeholder.text.casefold()`, compared as `text.casefold()`); `test_sample_table_has_rows` (at least 7 `entity` rows, 12 `gone` rows and 8 `kept` rows).
    - In `tests/test_privacy_sample.py` (the root file of S4-M1-T4), add `test_text_to_placeholder_text`: read the sample as the drift test does, run `find_personal_data(PrivacyInput(...), FakePiiDetector({}))`, `group_entities`, `anonymise`, and assert `restore_text(placeholder, document) == document.text`; assert that every use span of every `DefinedTerm` of `map_links(document, clauses).terms` overlaps no entity span (the defined roles are kept, Spec 4.2); and assert that the report of `render_privacy_report` for this run equals the golden file `src/clause_tracer/privacy/tests/goldens/developer-agreement.privacy.txt` (so the committed fixture, the pipeline and the golden agree).
  - **Files:** `src/clause_tracer/privacy/tests/test_sample_table.py`, `tests/test_privacy_sample.py`.
  - **Tests first:** the tests named above. The has-rows counts are fixed by this task so that an empty table cannot pass.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/privacy/tests/test_sample_table.py tests/test_privacy_sample.py` shows no failed test, and `scripts/check.sh` exits 0. If a row fails, the code or the row is wrong: bring it to the owner, and never edit the table.
  - **Rules:** Constitution T11 and T13 (the promises of Spec 4.2 have tests), testing strategy 8 (positive and negative controls), Spec 14.5.
  - **Depends on:** S4-M5-T2, S4-M5-T4, S4-M5-T5, S4-M1-T4

- [ ] **S4-M5-T7: Read the golden files (Owner)**
  - **Build:** Owner only. Read `src/clause_tracer/privacy/tests/goldens/developer-agreement.privacy.txt` and `src/clause_tracer/privacy/samples/developer-agreement.privacy.json` against the sample contract, and say whether they are right. The `text` lines of the golden file are the contract as the AI would see it: read them for a name or an address that is still there.
  - **Files:** None.
  - **Tests first:** None.
  - **Done when:** The owner says the golden files are right. If not, the agent fixes the code, regenerates the files with `--update-goldens` in a commit of their own, and asks again.
  - **Rules:** T11.
  - **Depends on:** S4-M5-T3

### M6: Close the stage

- [ ] **S4-M6-T1: Notes for the next stage and the status lines**
  - **Build:** Ask the owner first about the open items that section 9 lists under "Open cleanup" (the loader cleanup, and names with an apostrophe or a hyphen), and record each answer in section 8. Then ask whether the close goes on the branch `docs/close-stage-4-privacy`, as stage 3 did, or on the branch of milestone 5 (the owner's rule of 16 Nov 2026 is that docs changes that come out of milestone work stay on the milestone branch). Then, on that branch: fill section 9 of this plan; set the status of this plan to Done and tick the "Done when" checks; update the lines that state the project's status: [AGENTS.md](../../AGENTS.md) "Where the project stands" (stage 4 done, `privacy` described in one sentence, stage 5 next), the status line in [README.md](../../README.md), and [testing strategy](../testing-strategy.md) section 13 (the row "No samples or golden files in any module" gets "`privacy` closed" with the date, and "No planted-entity set" stays open for stage 7); change the status of the stage 4 row in this folder's [README](README.md) only if it lists one; record the owner's answers to questions 1 to 26 in their homes (system design 15.4, with the 21 Nov decisions, and the spec where it states a rule) if the planner has not yet done so. Then tell the owner what was built and what stage 5 and stage 7 should know.
  - **Files:** `docs/plans/stage-04-privacy.md`, `AGENTS.md`, `README.md`, `docs/testing-strategy.md`, `docs/system-design.md`.
  - **Tests first:** None.
  - **Done when:** `.venv/bin/uv run python scripts/copy_lint.py` exits 0, and `scripts/check.sh` exits 0.
  - **Rules:** The README of this folder, "When the stage is done"; WRITING_DOCS.md section 9.
  - **Depends on:** S4-M5-T6, S4-M5-T7

## 6. Open questions

The docs do not settle these points. Each needs the owner's answer before the tasks that need it. The tasks are written to the recommendation. If the answer differs, the planner rewrites those tasks before they start, and records the change in section 8. When the owner answers, the planner records each answer in its home (system design 15.4, the spec, or an amendment to ADR 0008) on the `docs/` branch that carries this plan, before milestone 1. Section 15.4 of the system design lists no "Not yet decided" point for this stage, and Spec 13 has no open item that it touches, so questions 1 to 17 come from the planner's reading of the docs and the code. Questions 18 to 24 were added on 21 Nov 2026 from [the report](../../reports/Privacy%20finder%20design%20choices.md) and the reference code that computed the expected values. The owner answered every question on 21 and 22 Nov 2026: 5, 9, 10, 14, 18, 25 and 26 one by one, questions 1, 4, 12 and 17 in a batch, and the rest "as recommended", which is the plan as written. Question 24 is the one change: the owner chose the report's version, so stage 4 builds the four extra patterns (S4-M2-T12).

| # | Question | Needed by task | Recommendation (if any) | Owner's answer |
| --- | --- | --- | --- | --- |
| 1 | **How does code alone find a person who is not a typed party?** Spec 14.5 names "contact Sarah Jones", but `Party` has no contact field and the party card in ux-copy has only Name and Address. System design 15.4 asks that every Spec 14.5 name is replaced "by code alone". | S4-M2-T7 | Three rules find a person who is not a typed party: an honorific (Mr, Mrs, Ms, Miss, Mx, Dr, also in capitals) with one or two capitalised words; a name of two to four words after "by" in a "Signed" or "Executed" phrase (initials and particles such as "de" or "ben" are allowed inside it); and a name of two to four words before a comma and a job title (Director, Managing Director, Manager, Partner, Owner, Secretary, CEO, CFO, Chairman, President). Lead words, trailing job titles and legal words are cut off, a company (`Signed by Acme Holdings Limited`) gives no person, and each name found also gives its variants everywhere in the text. Example: `Signed by Sarah Jones. Hi Sarah, see Ms Jones.` finds `Sarah Jones` with `Sarah` and `Jones` at the signature, then `Sarah` and `Ms Jones` (with `Jones`) in the later words. Limits: a person with none of the three marks is found only by the detector (stage 7 on), and a common-word name at the start of a sentence, such as `Pat Kelly, Managing Director, signed.`, is found only as `Pat Kelly` and `Kelly`, not as `Pat` alone. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 2 | **How does code know that a `Party` is a company or a person?** `Party` has no kind field, and a new field would change system design 3.4. | S4-M2-T1, S4-M2-T4 | A typed party is a company when the last word of its name, without a final full stop or comma, is one of these 15 (case-folded): `ltd`, `limited`, `llc`, `llp`, `plc`, `inc`, `corp`, `gmbh`, `ag`, `sarl`, `sas`, `bv`, `nv`, `pty`, `co`; every other party is a person. A longer list, which adds `lp`, `corporation`, `incorporated`, `srl`, `spa`, `oy`, `kg`, `ug` and `pte`, is used only to read a company name that a rule found, not to type a party. Example: `Acme Ltd.` and `Acme Co` are companies, `Karim Benali` is not, and `Acme LP` is not a typed company (it is only a rule seed). | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 3 | **How far does an address run?** The Spec 14.5 strings stop at "Leeds" and "Algiers", but the contract goes on: "LS1 4AB", "16000, Algeria". The prototype's list shows "14 Harbour Street, Leeds LS1 4AB" and "27 Rue Didouche Mourad, Algiers 16000, Algeria" as one replacement each. | S4-M2-T6 | An address is found in two ways: from a street pattern (a house number, up to three capitalised words and a street word, with up to three more comma parts), and by building a chain backwards from a postcode or ZIP (UK, US state with five digits, or Canadian), which also takes a country at the end. The chain starts at the house number, the unit word (Flat, Unit, Suite, PO Box) or the end of a cue phrase such as "whose address is", looks back at most 5 comma segments and 120 characters, and stops at a hard stop such as a semicolon, a bracket or the end of the last sentence. Example: `Send it to 221B Baker Street, London NW1 6XE.` gives the whole `221B Baker Street, London NW1 6XE`. Limit: with more than 5 segments or 120 characters between the start token and the postcode, the span is a truncated chain that holds the last 5 segments at most, so the earlier part of the address stays readable (question 23); the typed address also gives its first line (`14 Harbour Street`) as a variant (S4-M2-T1). | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 4 | **What are the exact variants of a name?** Spec 4.2 gives three examples for a person. Nothing lists the forms, and nothing says how a company's short name is found. | S4-M2-T1, S4-M2-T4 | A person has these forms: the full name without its honorific; first and last name when there are three or more words; the first name alone and the last name alone when each has 3 or more letters; and an honorific (mr, mrs, ms, miss, mx, dr), with or without a full stop, before the last name. A company has the name with `Ltd`, with `Limited` and without its suffix (another suffix, such as `Co`, has no swap), and a defined term is a short name of a party only when its words are all in the party's name and its defining sentence also holds the full name. Example: for the party `Brightline Studio Ltd`, the text `Brightline Studio Ltd ("the Studio") and the Agency.` with the terms `Studio` and `Agency` gives the company spans `Brightline Studio` (0 to 17), `Brightline Studio Ltd` (0 to 21) and `Studio` twice (11 to 17 and 28 to 34), and nothing for `Agency`. Case, curly quotes, soft hyphens and line breaks do not matter, and a one-word form follows the rules of question 17. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 5 | **Does the span of an ID or a bank number include its keyword?** The prototype lists "company number 09876543" as one replacement ("ID 1"). | S4-M2-T2 | Yes, as the prototype shows. The text then reads "with ⟦ID 1⟧" and the AI never sees the words "company number". |  Value only, decided by the owner on 21 Nov 2026. Home: task S4-M2-T2 (the span covers the value and the words "company number" stay in the text) and the rank table in S4-M3-T4; see also the [report](../../reports/Privacy%20finder%20design%20choices.md#owner-decisions-of-21-and-22-nov-2026), decision 4. The prototype file [`prototype/privacy-check.html`](../../prototype/privacy-check.html) still lists "company number 09876543" as one replacement, and changing it is a follow-up outside this plan. |
| 6 | **What does "restore" mean?** `PlaceholderText` holds no original text, so restore needs the document. There are three jobs: the whole text (the invariant of testing strategy 5), the tokens in an AI reply, and a span in the sent text (the quote check). | S4-M4-T3, S4-M4-T4, S4-M4-T5 | Build all three. `restore_text` rebuilds the whole text and reads the copy parts from the sent text, so the test is not circular, and it raises when the segments do not tile both texts. `restore_reply` puts back each token as the text of the entity's first place, and an unknown token raises, because Spec 8.4 makes it a broken reply. `map_to_original` maps a span of the sent text to the contract, and an edge inside a placeholder snaps out to the whole name. Example: for `Sarah Jones then Ms Jones at Brightline Studio Ltd.`, the reply `Ask ⟦Person 1⟧ to pay.` gives `Ask Sarah Jones to pay.`, and `⟦Person 9⟧` raises `privacy: unknown placeholder`. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 7 | **How is the detector called?** `FakePiiDetector` is keyed on the exact text, and stage 7 builds the real adapter to the same contract. | S4-M3-T6 | One call with the whole `Document.text`. The adapter chooses how it works through long text. The result is checked once (S4-M3-T1): a span outside the text, reversed or not an integer raises, and an empty or blank span is dropped. An error from the detector is never caught, so a failed run is never read as "nothing found". Example: for the sentence `Hi.`, a detector span of 0 to 99 raises a `ValueError`, and a recording detector sees exactly one call with the whole text. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 8 | **What happens to a detector span that crosses a sentence start?** The seams report says "no name ever crosses a sentence boundary" and gives no remedy. | S4-M3-T5 | Cut it at the sentence start and keep each piece, because a dropped span would leak. A piece that is only white space is dropped. Example: for the sentences `Pay Sam Lee.` and `Then Kim.`, a detector `ADDRESS` span over `Lee. Then` gives two pieces, `Lee.` (8 to 12) and `Then` (13 to 17). | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 9 | **Which suggestion wins an overlap, and what happens to the part that sticks out?** ADR 0008 says "overlaps resolve by source", and the report says "source priority, then length". Neither gives the order of the five sources, and neither says what happens to the part of a lower-priority span that lies outside the winner. | S4-M3-T4 | The order is `USER`, `PARTY_DETAILS`, `PATTERN`, `RULE`, `NER`, then the longer span, then the earlier start. A lower span is cut to the parts outside every kept span, and a part with no letter or digit is dropped. Example of the harm of the other way: "Ms Jones" found by a rule would drop a detector's "Sarah Jones" whole and leave "Sarah" in the text. The other way is to drop the lower span whole, which is simpler and leaves such a fragment. |  Source priority, then the cut, as recommended, plus a union of overlapping same-kind `NER` spans only, decided by the owner on 21 Nov 2026. Home: task S4-M3-T4; see also the [report](../../reports/Privacy%20finder%20design%20choices.md#owner-decisions-of-21-and-22-nov-2026), decision 5. A union for `RULE` and `PATTERN` spans is not built (question 21). |
| 10 | **What is the escape form?** Spec 4.2 says text that looks like a placeholder "is escaped first". The seams report gives the `escape` segment kind and no form. | S4-M4-T1, S4-M4-T2 | Each `⟦` and each `⟧` of the contract is its own `escape` segment and is sent as `[` and `]`. Then `⟦` and `⟧` occur in the sent text only inside real placeholders, so the scan of `core` cannot mistake an escaped marker for a placeholder, and offsets do not move. |  Keep the token form `⟦ ⟧` with its escape, and no ADR, decided by the owner on 21 Nov 2026. Home: the `PLACEHOLDER_OPEN` and `PLACEHOLDER_CLOSE` row of [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), with the tasks S4-M4-T1 and S4-M4-T2; see also the [report](../../reports/Privacy%20finder%20design%20choices.md#owner-decisions-of-21-and-22-nov-2026), decision 2. The stage 6 prompt rule "write each placeholder exactly as it appears" is not stage 4 work (section 9). |
| 11 | **Which matches remove a defined term from the allow-list?** The 20 Nov decision says "a typed-party finder or a name finder". A detector match on "Agency" would remove a role, which Spec 4.2 keeps, but it is also a name finder. | S4-M3-T2 | A term is dropped from the allow-list when a `PARTY_DETAILS` suggestion, or a `RULE` suggestion of kind `PERSON` or `COMPANY`, has the same text (without "the" and "'s"), or when it is a short form of such a name (the Mercury rule: all its words are among the name's words, and the name lies inside the term's definition). A detector match never drops a term, because the allow-list exists to overrule the detector's guesses at roles. Example: with the text `Mercury Logistics Ltd ("x") is the party.` and a rule company over `Mercury Logistics Ltd`, the term `Mercury` is no longer allowed, but a role such as `Agency` stays allowed. Limit: a short form that no finder reaches (only the detector) stays readable. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 12 | **What if a short name could belong to two people?** "Jones" fits "Sarah Jones" and "Tom Jones". The prototype lets the user say "Same person" or "Different person" for "Ms Jones". | S4-M3-T7 | A short form that fits one full name joins it, so `Sarah Jones` and `Ms Jones` share Person 1 by default, as Spec 4.2 says. A short form that fits two or more full names gets a placeholder of its own, because code never guesses. Example: in `Ms Jones and Sarah Jones and Sarah and Tom Jones.`, `Ms Jones` is `person-1`, `Sarah Jones` with `Sarah` is `person-2` and `Tom Jones` is `person-3`. The user's split and merge are built in stage 12 and pass entities to `anonymise`. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 13 | **Which stage replaces known names in position text and in rewrite instructions?** ADR 0008 (13 Nov 2026) asks for it. Section 15.4 does not list it, and stage 8 builds the position text. | None (a scope question) | Stage 8. Stage 4 builds no replacement in position text or in rewrite instructions. It leaves `PlaceholderEntity.spans` and `restore_reply` ready (S4-M4-T4), so stage 8 can read each name from `Document.text` and put back a token, for example `Ask ⟦Person 1⟧ to pay.` back to `Ask Sarah Jones to pay.`. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 14 | **Does stage 4 build the rule that keeps the governing-law place?** Spec 4.2 keeps "the place named in the governing-law clause". The match step that finds the clause is stage 8, but privacy runs before it, so the detector's flag on "England and Wales" must be dropped here. | S4-M3-T3 | Yes, as a small rule: the words after "governed by (and construed in accordance with) the law(s) of" are a kept place, and no detector or rule suggestion may overlap it. |  Yes, with a closed list: a country, a nation of the United Kingdom, a US state, a Canadian province or an Australian state, decided by the owner on 21 Nov 2026. Home: [Spec 4.2](../spec.md#42-privacy-check) (it already says so) and the tasks S4-M2-T11 (the owner's list) and S4-M3-T3; see also the [report](../../reports/Privacy%20finder%20design%20choices.md#owner-decisions-of-21-and-22-nov-2026), decision 1. A place outside the list is not kept. |
| 15 | **Which patterns does stage 4 build?** Spec 4.2 names emails, phone numbers, ID numbers and bank numbers. The architecture report lists more (UK sort code and account, postcode, VAT and company numbers). | S4-M2-T2, S4-M2-T3, S4-M2-T12 | Stage 4 builds these patterns, and each covers the value only: email; phone (international, UK national with spaces or dashes, UK national with a bracketed area code, and 11 unseparated digits that start with 0); an ID value after a keyword (company, registered or registration number, VAT number, tax id); a bank value after "sort code" or "account number" (8 digits); and IBAN with the mod-97 check. Since the owner's answer to question 24 (22 Nov 2026) it also builds four bare identifiers: a NINO, a GB VAT number with its checksum, a UK company number with a prefix, and a card number with the Luhn check (S4-M2-T12). Everything else (other national ID numbers and non-UK bank formats) is left to stage 7, and a bare reference such as `0123 456 7890` is also replaced as a phone (a known limit, as there is no cue gate). Example: `Our VAT number: GB123456789 and company no. 1234567.` gives two `ID` spans, `GB123456789` and `1234567`. | As recommended (owner, 21 Nov 2026), and extended on 22 Nov 2026 by question 24. Home: the tasks named in the third column. |
| 16 | **Who owns the word lists?** The finders hold lists of honorifics, company suffixes, job titles, street words and lead words. Stage 1 gave the scan word lists to the owner's table. | S4-M2-T1, S4-M2-T5, S4-M2-T6, S4-M2-T7 | The lists are code constants in this plan, and the owner reads them with the plan: honorifics, company suffixes, the stop words and common-word names of question 17, the company lead and role words, the street words, the job titles and legal words of the people finder, and the place list, which the owner writes (S4-M2-T11). The finders table (S4-M2-T8) fixes their effect. A change to a list is a change to code and to the table, in two commits (Constitution T11). Example: a test pins that `may`, `april`, `monday`, `will` and `price` are in the stop list. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. The owner writes the lists (owner tasks); the planner's drafts are proposals only. |
| 17 | **Which one-word forms may match, so that dates and common words are safe?** A one-word form (a first name alone, a last name alone, a short name) matches any word. A party "May Lee" or "April Jones" would then turn every "May" in a date into a name, which Spec 4.2 keeps. A party "Will Price" would turn every "will" and "price" into Person 1. Replacing too much is safe for privacy but it breaks checking. | S4-M1-T6, S4-M2-T1, S4-M2-T4, S4-M2-T7 | A one-word form counts only where its first letter is a capital in the contract. It is never searched when it is a month, a day or one of `will`, `mark`, `grant`, `bill`, `page` and `price` (layer 2). A one-word form that is also a common word (`Hope`, `Rose`, `Brown` and about 50 more) counts only with evidence of a name: not at the start of a sentence and not in a heading line, unless it is followed by `'s` or follows an honorific (layer 3). Example: for the party `May Lee`, the text `Lee signed on 1 May 2026. May Lee signs.` replaces `Lee` (0 to 3), `May Lee` (26 to 33) and `Lee` (30 to 33), and leaves the month `May` readable. Limits: `Ms Brown signs. Brown shall pay.` leaves the sentence-initial `Brown` readable, and a bare `Contact Will` is left for the same reason as `will` in the stop list; the owner may change the lists. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 18 | **Does `pat` stay in the layer 3 word list, given the plan's own test?** `test_name_before_a_job_title` used `"Pat Kelly, Managing Director, signed."`. `pat` is in `COMMON_WORD_NAMES` and the name starts the text, so layer 3 leaves `Pat` readable, and the reference code finds only `Pat Kelly` and `Kelly`. The planner changed the sentence of that test to `"Signed by Pat Kelly, Managing Director."`, where the reference code gives the original three values at shifted offsets, and kept the original sentence as `test_layer3_pat_at_a_sentence_start_is_left`. | S4-M2-T1, S4-M2-T7 | Keep `pat` in the list and keep both tests. The other way is to take `pat` out of the list; then the original sentence gives its three original values again and the second test changes. | Keep `pat` in the list and keep both tests (decided by the owner on 21 Nov 2026). Home: tasks S4-M2-T1 (`COMMON_WORD_NAMES`) and S4-M2-T7 (`test_name_before_a_job_title` and `test_layer3_pat_at_a_sentence_start_is_left`). |
| 19 | **Do two more readings of "US state" count in the governing-law clause?** The tasks keep a US state only as `State of X`. Two switches in `places.py`, both off, change it: `US_STATE_BARE` (`laws of New York`) and `US_COMMONWEALTH` (`Commonwealth of Virginia`). | S4-M3-T3 | Leave both off, as the owner's list of five categories reads: a US state is kept only as `State of X`. Turn one on only if the owner wants it; each is a one-line change in `places.py` and a change to the tests `test_us_state_bare_is_not_listed` and `test_commonwealth_is_not_listed`. Example: `governed by the laws of the State of Delaware.` keeps `State of Delaware`, and `governed by the laws of New York` keeps nothing. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 20 | **Is the draft place list right?** The planner's draft holds 151 country names and short forms, the UK nations, 50 US states, the Canadian provinces and territories, and the Australian states and territories. It leaves out Jersey, Guernsey, the Isle of Man, Hong Kong, the District of Columbia and `Washington, D.C.` A place outside the list is replaced if a finder flags it. | S4-M2-T11 | The owner reviews the draft and writes the file, and the agent does not write or change it. The draft holds 151 country names and short forms, the UK nations, 50 US states, the Canadian provinces and territories, and the Australian states and territories. Example: `governed by the laws of Ontario` keeps `Ontario`, while `governed by the laws of Jersey` and `governed by the laws of Narnia` keep nothing, so a finder's flag on those places stays. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. The owner writes the lists (owner tasks); the planner's drafts are proposals only. |
| 21 | **Should overlapping `RULE` and `PATTERN` spans also be joined, as `NER` spans are?** The reference code found 3 more changed cases in 5,000 with it. | S4-M3-T4 | No, not in stage 4: the union stays `NER` only, and the stage looks again only if the address chain leaves a split span. Example: for `Sarah Jones`, two detector (`NER`) spans, 0 to 8 and 3 to 11, join into `Sarah Jones`, but two `RULE` spans with the same offsets stay apart as `Sarah Jo` (0 to 8) and `nes` (8 to 11). | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 22 | **Is the run-on of a keyword ID value a limit to accept?** `company no. 1234567 5 days notice` gives the ID span `1234567 5`, because the value pattern `\d[\d ]{3,12}\d` runs across a space into the next number. | S4-M2-T2 | Accept it as a known limit in stage 4: it replaces slightly too much, which is the safe direction. For example, `company no. 1234567 5 days notice` gives the ID span `1234567 5`, because the value pattern runs across a space into the next number, while `company number 09876543 Agency` stops before the word. The owner may give a stricter value pattern. | As recommended (owner, 21 Nov 2026). Home: the tasks named in the third column. |
| 23 | **What does the address finder do when the chain is too long?** A start token (house number, unit word, PO Box) or a cue phrase lies more than 5 comma segments or 120 characters before the postcode. The first reference code replaced only the postcode, so the street and town stayed readable and leaked (`Mail 1 Aaaa, Bbbb, Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB` gave `LS1 4AB`). | S4-M2-T6 | Keep a truncated chain, as the report recommends (it leaks less than the postcode alone). The span starts at the earliest comma segment that keeps the chain within 5 segments and 120 characters, ends as before (the postcode and an optional country), and never crosses a hard stop. Example: `Mail 1 Aaaa, Bbbb, Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB` gives `Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB`, while `Mail 1 Aaaa, Bbbb, Cccc, Dddd, Leeds LS1 4AB` (exactly 5 segments) gives the whole `1 Aaaa, Bbbb, Cccc, Dddd, Leeds LS1 4AB`. With no start token at all (`Alpha Park, Leeds LS1 4AB`), or when the nearest segment alone is longer than 120 characters, the postcode alone is the span. The segments before the truncation stay readable (a known limit). | Keep a truncated chain, as in the report (owner, 22 Nov 2026). Home: S4-M2-T6. |
| 24 | **May stage 4 also find NINO, Luhn-checked card numbers, bare GB VAT numbers and UK company prefixes?** Question 15 keeps them for stage 7. The report's evidence is that bare IDs leak (5 of 5 missed). | S4-M2-T12 | The report recommends yes for all four, and the owner agreed on 22 Nov 2026: S4-M2-T12 builds them. A NINO, a GB VAT number and a UK company prefix give kind `ID`, with no cue gate, because a checksum or a fixed prefix already makes each one strong. A card number gives kind `BANK` and needs the Luhn check, 13 to 19 digits, and a cue word or an issuer first digit (question 26). Example: `AB 12 34 56 C` gives one `ID` span, `BG123456C` gives none (an excluded prefix), and `Pay 5 days, £1,600 on 5 November 2026.` still gives none. | Add the four to stage 4, as the report recommended (owner, 22 Nov 2026). Home: S4-M2-T12. |
| 25 | **What happens to a person or company span that touches the kept governing-law place?** Example: `governed by the laws of England Brightline Studio Ltd signs.` The company finder marks `England Brightline Studio Ltd`, and the place `England` touches it. Cutting would leave `England` readable and leak one word if it belongs to the name. Keeping the span whole hides the place word and the AI cannot read the governing law in that clause; the label turns unsure and the user sees the clause. The reference code found 0 touches of a finder span and a kept place in 510 real contracts. | S4-M3-T3 | Keep a `PERSON` or `COMPANY` span whole and cut every other kind (the report's question 10 and the owner's choice). | Hybrid, decided by the owner on 21 Nov 2026: a `PERSON` or `COMPANY` span that touches the place stays whole; every other kind is cut. Home: [Spec 4.2](../spec.md#42-privacy-check) (it holds the clause) and task S4-M3-T3 (`cut_in_places`); see also the [report](../../reports/Privacy%20finder%20design%20choices.md#owner-decisions-of-21-and-22-nov-2026). |
| 26 | **Which placeholder kind does a card number get?** `PlaceholderKind` has no card kind, and Spec 4.2 lists "bank numbers". The same question has a second part: what gates a card number, because about 1 in 10 random digit strings of 13 to 19 digits passes the Luhn check. Report Q15 (d) gives the gate as a cue word within 40 characters before, or a first digit of 3, 4, 5 or 6, on top of the Luhn check and 13 to 19 digits. The report's nearby-fields table gives a stricter one: a cue word, or else only a 4-4-4-4 grouping that starts with 4 or 5. | S4-M2-T12 | Kind `BANK`. Gate: the rule of Q15 (d), which the task builds: Luhn check, 13 to 19 digits, and a cue word (`card`, `visa`, `mastercard` or `amex`, within 40 characters before) or a first digit of 3, 4, 5 or 6. Example: `Card 4111 1111 1111 1111 expires` gives one `BANK` span, `4111 1111 1111 1111`. The other options: kind `ID` (a card is then numbered with the company numbers, and the list shows `ID 3`); a stricter gate that needs the cue word, which would stop `Order 5123 4567 8901 2346` from being replaced as a card but would leak a card written with no cue word (a change to `card_is_valid` and two tests of S4-M2-T12); and a longer cue list that adds `credit`, `debit` and `maestro`. | As recommended (owner, 22 Nov 2026): a card number gets the kind `BANK`, and the gate is the Luhn check, 13 to 19 digits, and a cue word within 40 characters before or a first digit of 3, 4, 5 or 6. Home: S4-M2-T12. |

## 7. Done when

- [ ] Every task above is ticked.
- [ ] `scripts/check.sh` passes with no errors.
- [ ] Each touched module's README records its shapes (Constitution S3).
- [ ] Every promise the stage touches has its test (Constitution T13): anonymise then restore gives the original (S4-M4-T6, S4-M5-T6); no entity crosses a sentence boundary (S4-M3-T11, S4-M4-T6); a flagged name is cut and never dropped, also at the governing-law place, where a person or company span stays whole (S4-M3-T11, properties P2, P11 and P12); a bad, reversed or non-integer offset raises (S4-M3-T1, property P10); a detector error is not caught (S4-M3-T6); no planted name is left in the sent text (S4-M4-T6); the roles, amounts, dates, durations and the governing-law place of Spec 4.2 are kept (S4-M5-T5, S4-M5-T6); a bare NINO, GB VAT number, company prefix and card number is found, and its near misses are kept (S4-M2-T12); every Spec 14.5 name and address is gone from the sent text (S4-M5-T5, S4-M5-T6).
- [ ] The lines that state the project's status are updated (see the README, "When the stage is done").
- [ ] The owner has been told what was built, and what the next stage should know.
- [ ] `python -m clause_tracer.privacy` reads the sample fixture and prints its entities and placeholder text, and the golden file matches (outline "Done when").
- [ ] Anonymise then restore gives the original text on the sample and on generated text (outline "Done when").
- [ ] Every Spec 14.5 name and address is replaced by code alone, with an empty detector (outline "Done when").
- [ ] The five owner tables and the place list (S4-M2-T11) hold the owner's values, the owner has confirmed the values marked "owner to confirm", and the owner has read the golden file (S4-M5-T7).
- [ ] Branch coverage of `privacy` is at least 85%.

## 8. Change log

| Date | Change | Why |
| --- | --- | --- |
| 21 Nov 2026 | Plan written as a Draft. | Stage 3 is done. |
| 21 Nov 2026 | Plan verified by the planner. Checks: backward and forward analysis against section 15.4 and the testing strategy; a script for task ids, dependencies, define-and-use order, test counts and links; five haiku simulations that built the tasks from the text alone (about 370 tests in six folders, and the sample end to end: 7 entities, 10 spans, an exact restore, no Spec 14.5 name left in the placeholder text); 33,000 Hypothesis cases with no failure. The planner repaired the defects found, as exact string edits, and a haiku pass re-validated them (97 tests passed). The status stays Draft: only the owner accepts. | Section 15.4 asks for a plan that leaves the implementer no design choice. |
| 21 Nov 2026 | Doubts come later. The shape exists in core (S1-M6-T8). The code that fills it is built where the user first sees suggestions: stage 6 settles how the command-line tool does the privacy check (system design 15.6), and stage 12 builds the screen. Owner chose B on 21 Nov 2026. Stage 4 produces no doubts, and no stage 4 task builds the doubt list. | The owner's answer to the doubt-list question (option B), given in chat on 21 Nov 2026. |
| 21 Nov 2026 | Revised to carry the owner's decisions of 21 Nov 2026 and the measured fixes of [the privacy finder design choices report](../../reports/Privacy%20finder%20design%20choices.md), with every changed or added value taken from the reference code (of the 245 tests of the Draft, 4 values changed and 2 tests were renamed; 155 tests were added, 11 of them Hypothesis properties). Owner decisions carried: a closed governing-law place list (an owner task, S4-M2-T11, and the cut at the place in S4-M3-T3); the token form `⟦ ⟧` stays; value-only ID and bank spans; a union for `NER` spans only; no doubt list in stage 4. Tasks changed: S4-M1-T6 (`find_name_form` takes `ambiguous_words`, layer 3, `subtract_spans`, `_patterns.py` created), S4-M2-T1 (`COMMON_WORD_NAMES`, `EXTENDED_COMPANY_SUFFIXES`, `is_company_seed`), S4-M2-T2 (phones, value-only spans), S4-M2-T3 (count), S4-M2-T4 (layer 3), S4-M2-T5 (company rule), S4-M2-T6 (address chain), S4-M2-T7 (name fragments, trims, capitals, legal-word veto), S4-M3-T1 (offset checks), S4-M3-T2 (`allowed_term_texts` takes `DefinedTerm`s, Mercury rule), S4-M3-T3 (closed list, `cut_in_places` takes the text), S4-M3-T4 (`NER` union, `TIE_RANK`), S4-M3-T5 (two tests), S4-M3-T6 (steps 3 and 4, fail closed, composed cases), S4-M3-T11 (11 properties and the law strategy), S4-M5-T3, T4, T5 (the `id-1` span, known limits, `gone` row). Task added: S4-M2-T11 (Owner, the place list). Questions added: 18 to 24. Questions answered: 5, 9, 10, 14. Status stays Draft. | Plans README ("When the plan is wrong"; the Draft is revised before it is accepted) and the owner's decisions of 21 Nov 2026. |
| 21 Nov 2026 | Hybrid rule at the governing-law place (owner, question 25): `cut_in_places` keeps a `PERSON` or `COMPANY` span whole when it touches the place and cuts every other kind. S4-M3-T3 gains 6 tests (40 to 46); one test of S4-M3-T6 changes its expected span to `("England Brightline Studio Ltd", 24, 53)`; S4-M3-T11 gains property P12 (15 to 16). Values come from the reference code. | Plans README ("When the plan is wrong"), owner decision of 21 Nov 2026 |
| 21 Nov 2026 | Question 18 answered by the owner: `pat` stays in the layer 3 word list, and both `test_name_before_a_job_title` and `test_layer3_pat_at_a_sentence_start_is_left` stay. The tests no longer wait on an answer. The owner also kept `max_examples=1000` for the properties of S4-M3-T11. | The owner's answers in chat, 21 Nov 2026. |
| 21 Nov 2026 | Simulation of M1 and M2 by a cheap implementer: 190 tests built and passing, one plan defect (the T9 example) and a dozen ambiguities closed (S4-M1-T3, T6; S4-M2-T1, T4, T7, T9, T10, T11); Georgia added to the proposal block of S4-M2-T11. | Plans README (When the plan is wrong) |
| 21 Nov 2026 | Simulation of the changed M3 tasks by a cheap implementer: 135 tests built and passing; plan code blocks made ruff-clean (line length, zip strict, Final annotations); properties all use the 1000-example settings; four ambiguities closed (S4-M3-T1, T2, T11). | Plans README (When the plan is wrong) |
| 21 Nov 2026 | S4-M4-T6: the properties use the `SETTINGS` object of S4-M3-T11 (1,000 examples) in place of `@settings(deadline=None)`, so every property of the stage runs the same number of examples. M3 T7 to T10, M4 and M5 were not simulated by a cheap implementer (owner's choice). | The owner's answers in chat, 21 Nov 2026 |
| 21 Nov 2026 | The owner answered the open questions of section 6 (1 to 4, 6 to 8, 11 to 13, 15 to 17, 19 to 24) as recommended, which is the plan as written. Question 24 was first recorded as staying in stage 7; the owner reversed it on 22 Nov 2026 (next rows). No task changed on 21 Nov. | The owner's answers in chat, 21 Nov 2026 |
| 22 Nov 2026 | Question 24 reversed by the owner: stage 4 also finds a NINO, a GB VAT number with its checksum, a UK company number with a prefix, and a Luhn-checked card number. Task added: S4-M2-T12 (35 tests; values from the reference code). Changed: Scope (Builds, Leaves to later stages), the M2 introduction, the Depends on of S4-M3-T6, the known limits of S4-M5-T4, questions 15 and 24 in section 6, section 7, and the count of questions in section 4 and S4-M6-T1 (1 to 26). Question added: 26 (the kind and the gate of a card number; open, with a recommendation). Card rule used: report Q15 (d), a cue word or an issuer first digit. Status stays Draft. | The owner's decision in chat, 22 Nov 2026 |
| 22 Nov 2026 | Question 26 answered by the owner as recommended: a card number gets the kind `BANK`, and the card gate stays as built in S4-M2-T12. No task changed. All 26 questions of section 6 now carry an answer. | The owner's answers in chat, 22 Nov 2026 |
| 22 Nov 2026 | Question 23 answered by the owner the other way: an address chain longer than 5 comma segments or 120 characters keeps a truncated chain (the last part before the postcode, at most 5 segments and 120 characters) in place of the postcode alone. Changed: S4-M2-T6 (Build text, the code block with the new `_truncated_start`, and the tests: `test_address_chain_with_7_segments_gives_the_postcode_alone` is renamed `test_address_chain_with_7_segments_keeps_the_last_5_segments` and now gives `Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB`; two tests added, 24 to 26), question 3 (the limit), question 23 (the answer), and the known limits of S4-M5-T4. The task count stays 43. Values taken from `ref4.py` of the reference folder. Status stays Draft. | The owner's decision in chat, 22 Nov 2026 |
| 22 Nov 2026 | Recorded where the milestone 1 build differs from the plan text, and fixed the plan text. (1) S4-M1-T2: the five owner tables were already on `main` and filled, so the task is a tick only, and the T2 commit holds only the plan tick. (2) S4-M1-T1: the negative check used 101, which `coverage` rejects as invalid before it compares a total; the text now says 100. (3) S4-M1-T3: the `SourceFile.size` of the test document is `len(text.encode())` (23 for the plan's text), and the text now says how child objects and list elements are ordered and named. (4) The build order was T3, T2, T4, T5, T6, T1, because the privacy total was 50% before the new code and the T1 floor would have failed; the final checks match the plan. (5) Helpers and constants the plan does not name: the `_validate_*`, `_require_*` and `_*_field` helpers and the key tuples in `sample_input.py`; `_word`, `_form`, `_spans` in `test_match.py`; `_suggestion` in `test_spans.py`. (6) Docstrings and a longer `privacy/samples/README.md` and README section than the plan lists. (7) Four small fixes after the first write: three tests failed with `DID NOT RAISE` because the helper `_clause_rows` returned a copy (the helper was fixed, no loader change), two import orders and two formatting changes for ruff, and the type of the `seen` set in `unique_sorted`. (8) `test_sample_input.py` has an unused helper `_sentence_rows` and imports `DefinedTerm` from `clause_tracer.core.link_map`; S4-M1-T7 removes both | The agent reported these after building, and the planner checked the commit list, the T2 commit, the 101 run, the unused helper and the document size in the code. No expected value, name, signature or message changed |
| 22 Nov 2026 | Code review of milestone 1 (five findings). Added S4-M1-T7 (seven error-path tests, and the unused helper and the import fixed; tests only). Added a draft for the owner, with no task id, for names with an apostrophe or a hyphen (the owner chose to try a code fix first, and the known limit is written only if it fails). The owner asked also for the cleanup of the double check in `sample_input.py`; it is not a task yet, because `links/sample_clauses.py` has the same two-pass shape and the stage 3 plan told its loader task not to rewrite those validators, so a one-sided rewrite would make `privacy` differ from `links`. The owner decides whether to rewrite both or neither. Skipped, as the owner accepted: the loader does not check `sha256` and `size` against the text or that `parent_id` names a clause (the T3 plan lists exactly eight checks, and the drift test catches an old fixture), and the unused pattern strings in `_patterns.py` (harmless; later finders may use them) | The owner's answers in chat, 22 Nov 2026 |
| 22 Nov 2026 | Milestone 2 build record. (1) The five owner tables had no `HEADER` line, so S4-M2-T10 could not load them; the owner added it in `99a76f0` and S4-M1-T2 now says so. (2) S4-M2-T12: the check of the sample reference run moved to S4-M5-T7, because it needs `find_personal_data`. (3) S4-M2-T10: the known failing row `company-with-a-foreign-suffix` is named in Done when, and the implementer stops there. (4) Status set to In progress. Build differences with the same behaviour, accepted: S4-M2-T1 uses `isdisjoint` (ruff SIM300) and a private `_last_token` helper; S4-M2-T2, T3 and T12 hold the keyword patterns in a `_PATTERNS` tuple; S4-M2-T4 has a private `_short_names`; S4-M2-T5 has a module `_CONNECTORS` set; the unknown-finder message in T10 is `unknown finder <name>`. | The implementer's report and the owner's decision in chat, 22 Nov 2026 |
| 22 Nov 2026 | Owner chose to fix the company pattern for the row `company-with-a-foreign-suffix`, not to mark it as an expected failure. Task added: S4-M2-T13 (`WORD` reads a Latin-1 capital and Unicode letters; 6 tests, values run on 22 Nov 2026; the 287 privacy tests and `scripts/check.sh` pass with the change). Changed: S4-M2-T10 (the known-failing-row text removed), the known-limits text in S4-M5-T4 (a capital outside Latin-1 stays a limit). | The owner's decision in chat, 22 Nov 2026 |
| 22 Nov 2026 | M2 code review (ten findings). Tasks added: S4-M2-T14 (Latin-1 letters in `TOK`, `INIT`, `CAPS_TOK`, `CAP`, and `EMAIL` with any letter; 6 tests), S4-M2-T15 (4 tests of paths no test ran), S4-M2-T16 (named booleans, a table in `find_patterns`, shared role words, one unreachable check removed, `key` parameter, simpler `WORD`; 4 tests). Total 2058 tests pass with all three in a trial run. Finding 2 skipped by the owner. Changed: pointers in S4-M2-T2, T4, T5, T6, T7, S4-M3-T6 (folds once and passes `key`), the known limits in S4-M5-T4, section 9. The five finders give the same results on the sample before and after. | The owner's decision in chat, 22 Nov 2026 |

## 9. Notes for the next stage

Not yet written. The planner fills this in when the stage is done.

Known already:

- M2 code review (22 Nov 2026, ten findings): findings 1 and 3 (non-ASCII names, street words and emails), 4 to 7, 9 and 10 are built in S4-M2-T14 to T16. Finding 2 (`ID 12345` read as an address) was skipped by the owner, because a missed address is worse than a hidden number; it is in the known limits. The job-title half of finding 8 was not changed: `TITLE_WORDS` (a pattern) and `TRAILING_TITLE_WORDS` (a set) hold different words.
- Open cleanup, to decide before stage 4 closes (S4-M6-T1): the loaders `privacy/sample_input.py` and `links/sample_clauses.py` check every JSON value twice (a `_validate_*` pass, then `_*_field` casts). The M1 review (22 Nov 2026) found it; the owner wanted it cleaned up, but a rewrite of one module makes the two differ, and the stage 3 plan told its loader task not to rewrite those validators. Decide: rewrite both in one task, or neither. The planner recommends neither unless a later change to the fixture format makes the double check cost real work. Also open: names with an apostrophe or a hyphen (the draft after M1), closed only by the real-contract check.
- Doubts come later. The shape exists in core (S1-M6-T8). The code that fills it is built where the user first sees suggestions: stage 6 settles how the command-line tool does the privacy check (system design 15.6), and stage 12 builds the screen. Owner chose B on 21 Nov 2026.
- Stage 8 prompt rule ([system design 15.8](../system-design.md#158-stage-8-checking-and-the-message-templates), the prompt rules; not stage 4 work): every prompt that carries placeholders tells the model to write each placeholder exactly as it appears in the text, and never to change, translate or invent one (owner decision 2 of 21 Nov 2026; report, questions 6 and 10).
- Stage 7 adapter contract. The `PiiDetector` adapter takes the whole text and returns spans in whole-text offsets counted in code points. Any chunking and the mapping of offsets back happen inside the adapter, with overlapping windows broken at white space and duplicates removed. It never truncates the text silently, and it fails closed: when it cannot cover the whole text, it raises a named error. It returns spans only, never copied text, and an error message holds no contract text. The port's docstring ("Raises: None", system design 3.4) conflicts with failing closed, so `find_personal_data` must not catch a detector error (S4-M3-T6 has the test `test_a_detector_error_is_not_caught`). Stage 7 changes the docstring with the owner's agreement, because the port is an accepted shape.
- Stage 8 free-text replacer and the import wall. Stage 8 cannot import `privacy`, so the replacer of known names in position text and in rewrite instructions must be a call that `privacy` exports and `cli` wires in, or live in `core`; a second copy of the matcher would drift. One-word forms in free text match without regard to case (the stage 4 rule needs a capital, so the two rules differ and the stage 8 plan states which one wins). A restored text is never re-sent without a fresh replacement pass.
