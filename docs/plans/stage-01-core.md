# Stage 1 plan: `core`

| | |
| --- | --- |
| Stage | 1, `core` |
| Status | Draft |
| Branch | One branch for each milestone, cut from `main`: `feat/core-m1-foundations`, `feat/core-m2-shapes`, `feat/core-m3-label-rules`, `feat/core-m4-ports-and-fakes`, `feat/core-m5-scans-and-last-check`, `feat/core-m6-run-alone`. See [the README](README.md), "Branches and pull requests" |
| Accepted on | Not yet |
| Stage outline | [System design section 15.1](../system-design.md#151-stage-1-core) |

## 1. Goal

`core` holds every shape, port, error, fake and pure rule that system design section 15.1 lists, with table-driven and property tests. Importing `core` loads only the standard library, and `python -m clause_tracer.core` prints the labels of the Spec 14.5 sample.

## 2. Scope

**Where the code starts.** The skeleton is empty. `src/clause_tracer/core/` holds only `__init__.py` (an empty `__all__`), `__main__.py` (prints "not built yet"), a README with "planned" shapes, `tests/test_smoke.py` and `samples/.gitkeep`. `pyproject.toml` has no runtime dependencies. Its dev group has `pytest`, `ruff`, `mypy`, `import-linter` and `uv`, but no Hypothesis, no Pydantic and no coverage tool. There is no `conftest.py` anywhere. The five import contracts in `pyproject.toml` already cover `core` and stay as they are.

### Builds

- The ids, enums and shapes of [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), including the three points "Decided for stage 1" (step input shapes, no written-by value on playbook text, `CancelCheck`).
- The error tree of [system design 6.4](../system-design.md#64-errors).
- The five ports as `typing.Protocol` classes, and their fakes: the replay fake, a fake personal-data detector, in-memory review and secret stores, and a fixed clock.
- A pure hash of the exact AI request.
- Label rules 1 to 10 as pure functions, with `MATCH_UNCONFIRMED`, the unplaceable-quote case, and undecodable text under Rule 9. Unit conversion (Rule 6).
- The auto-delete date rules, the cost estimate, the output scans, and the last check before drawing.
- Owner-owned expected-answer tables for the label rules, the Spec 14.5 sample, auto-delete dates, scans and the cost estimate (Constitution T11).
- Architecture tests: importing `core` loads only the standard library; no shape has a provider-specific field.
- Property tests with Hypothesis, including offset invariant 7.
- `python -m clause_tracer.core --input …` on a sample (S1), and the module README with every shape, port and function (S3).

### Leaves to later stages

- Golden files and the `--update-goldens` command: stage 2, the first module with golden files ([testing strategy 13](../testing-strategy.md#13-gaps-today-and-the-order-to-close-them)).
- Building match keys and the fold for them, and offset invariants 2 and 4: stage 2. The placeholder map and invariant 3: stage 4. Glyphs, page boxes and invariants 1, 5 (in `checking`) and 6: stages 5 and 8.
- User state and `Customer`; storage rows, the key table and migrations; `StepSpec`, the cache key, runner events and the cancel token: stage 6 ([system design 3.4, "Left to later stages"](../system-design.md#34-core-shapes-for-stage-1)).
- Mapping errors to review statuses and exit codes, loading and validating `Settings`, reading playbook files: stage 6.
- The contract suite run against real adapters: stage 6 (store, secrets), 7 (Presidio), 9 (OpenRouter).
- The number parser and the quote check; the "searched, nothing found" list; explanation parts; keywords on `Position`; the step input shapes of each AI step; the template fallback after a failed scan: stage 8.
- AI reply schemas (Pydantic, in the owning module): stages 8, 9 and 11.
- The spend ledger: stage 9. The `paid` marker and the report script: stage 10.
- `Suggestion` and the report's contents: stage 11. Engine protocol shapes, theme and text size: stage 12.
- The Windows CI job: stage 5 or 6. The mutation report: before a release.

## 3. Read first

- [AGENTS.md](../../AGENTS.md), the [Constitution](../../Constitution.md), [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md), and [WRITING_DOCS.md](../../WRITING_DOCS.md) sections 2 and 9.
- [System design](../system-design.md): [3.1](../system-design.md#31-the-engine) (parts and ports), [3.4](../system-design.md#34-core-shapes-for-stage-1) (all of it), [4.2](../system-design.md#42-the-offset-chain), [5.1](../system-design.md#51-three-kinds-of-data), [6.3](../system-design.md#63-the-ai-request), [6.4](../system-design.md#64-errors), [7](../system-design.md#7-caching-resume-and-cost), [8.2](../system-design.md#82-calls-to-the-ai-service), [15](../system-design.md#15-build-stages) and [15.1](../system-design.md#151-stage-1-core). Skim 15.2 to 15.12 to see what later stages take from `core`.
- [Testing strategy](../testing-strategy.md): sections [1](../testing-strategy.md#1-what-the-tests-must-prove), [2](../testing-strategy.md#2-principles), [3](../testing-strategy.md#3-five-layers), [4](../testing-strategy.md#4-what-to-test-in-each-module) (the `core` row), [5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 7 and the hazard alphabet), [6.1](../testing-strategy.md#61-the-replay-fake), [10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [11](../testing-strategy.md#11-coverage-targets), [12](../testing-strategy.md#12-when-each-test-runs) (architecture tests), [14](../testing-strategy.md#14-example-tests).
- [Spec](../spec.md): [2](../spec.md#2-glossary) (glossary), [4.1](../spec.md#41-playbooks), [5](../spec.md#5-labelling-rules) (every rule), [6.1](../spec.md#61-steps) (steps 6a to 8), [6.2](../spec.md#62-rules-for-every-ai-step), [6.3](../spec.md#63-review-statuses), [7](../spec.md#7-starter-playbook), [8.3](../spec.md#83-stored-data), [9](../spec.md#9-running-the-app) (cost and auto-delete), [11](../spec.md#11-acceptance-tests), [14.5](../spec.md#145-sample-data).
- Decision records: [ADR 0002](../adr/0002-label-look-split-stamp.md) (pencilled labels), [ADR 0004](../adr/0004-code-layout.md), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) with both amendments, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) with its amendment, [ADR 0013](../adr/0013-test-layers-and-release-gates.md) with its amendments, [ADR 0015](../adr/0015-provider-ready-seam.md) with its amendment, [ADR 0016](../adr/0016-legal-positions-without-a-lawyer.md) (section 3 and action item 3).
- [The architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md), three parts only: [errors](../../reports/Clause%20Tracer%20pipeline%20architecture.md#errors-carry-codes-and-only-the-edge-turns-them-into-words) (the starting list of error classes), [labels](../../reports/Clause%20Tracer%20pipeline%20architecture.md#labels-8-are-pure-functions-and-unsure-is-the-abstention-channel), and [scans](../../reports/Clause%20Tracer%20pipeline%20architecture.md#judge-9-explain-10-and-summarise-11-templates-first-fenced-slots-for-the-rest) ("Plain-code scans are the gate"). Where the report and the system design differ, the system design wins.
- The current code: [`src/clause_tracer/README.md`](../../src/clause_tracer/README.md), everything in [`src/clause_tracer/core/`](../../src/clause_tracer/core/), [`pyproject.toml`](../../pyproject.toml) and [`scripts/check.sh`](../../scripts/check.sh).

## 4. Checks before starting

- [ ] **The plan is Accepted**, and the owner has answered every open question in section 6 whose "Needed by" task is in M1 or M2.
- [ ] **The skeleton passes.** Run `.venv/bin/uv sync`, then `scripts/check.sh`. It must pass with no errors before any change. Confirm that `core` holds only the files listed in section 2.
- [ ] **Pydantic `TypeAdapter` builds frozen, slotted dataclasses** ([ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) action item 2, [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) "Check first"). Run it after S1-M1-T2, and before any shape or enum is written (S1-M1-T4 onwards). How:
  1. Write a throwaway test file in your scratch folder, outside the repo. Never commit it.
  2. In it, define frozen, slotted standard-library dataclasses that use every kind of field the shapes need: `int`, `str`, `bytes`, `Decimal`, `datetime`, a `NewType` over `str`, an `Enum`, `X | None`, `tuple[X, ...]`, `tuple[int | None, ...]`, a nested dataclass, a `Mapping[str, object]` field, and a field typed as a union of three dataclasses (like `Position.rule`).
  3. Run `.venv/bin/uv run pytest <that file>`. Assert, for `TypeAdapter(...).validate_python(...)` and `validate_json(...)`: the result is an instance of the dataclass itself (not a Pydantic copy); assigning a field raises `FrozenInstanceError`; the instance has no `__dict__`; a JSON list becomes a tuple; a wrong type raises `ValidationError`; the union field becomes the right one of the three dataclasses for each input; and note what type the `Mapping` field comes back as.
  4. Pass: write the Pydantic and Python versions and the result in this plan's change log, and tell the owner. Ticking the ADR's action item is the owner's call.
  5. Fail, or any surprise (for example the union picks the wrong class): **stop**. Bring it to the owner before any shape is written.
- [ ] **Remind the owner** to start writing the ten test contracts now, because they take longest ([system design 15.1](../system-design.md#151-stage-1-core)).

## 5. Milestones and tasks

Notes for every task:

- File names are suggestions. Keep them unless there is a reason, and record the real names in the core README.
- Other modules import only from `clause_tracer.core` (its `__all__`), never from a file inside it (B2).
- Every shape task updates `src/clause_tracer/core/README.md` in the same commit (S3).
- If a shape must differ from system design 3.4, stop and ask the owner. An approved change also updates section 3.4 in the same commit ([WRITING_DOCS](../../WRITING_DOCS.md) section 2).
- Shapes get no third-party imports and no validation beyond the type (D4, I9: outside data is checked at the edge).

### M1: Foundations

The stage's dependencies are locked, the architecture tests guard `core`, and `from clause_tracer.core import Level, ClauseTracerError` works.

- [ ] **S1-M1-T1: Add Hypothesis**
  - **Build:** Run `.venv/bin/uv add --dev hypothesis`. Commit `pyproject.toml` and `uv.lock` together, as `build(deps): add hypothesis for property tests`.
  - **Files:** `pyproject.toml`, `uv.lock`.
  - **Tests first:** None. This task adds a tool.
  - **Done when:** `.venv/bin/uv sync --locked` and `scripts/check.sh` pass.
  - **Rules:** [Testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (Hypothesis), [ADR 0013](../adr/0013-test-layers-and-release-gates.md); AGENTS.md (commit `uv.lock`).
  - **Depends on:** None.

- [ ] **S1-M1-T2: Pin Pydantic for the TypeAdapter check**
  - **Build:** Only if question 1 is answered "add it now": run `.venv/bin/uv add pydantic` and commit `pyproject.toml` and `uv.lock` as `build(deps): add pydantic for edge validation`. Nothing in `core` imports it. Otherwise skip this task and run the check with `.venv/bin/uv run --with pydantic`.
  - **Files:** `pyproject.toml`, `uv.lock`.
  - **Tests first:** None. The check in section 4 runs right after this task.
  - **Done when:** `scripts/check.sh` passes, and the TypeAdapter check result is in the change log.
  - **Rules:** [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) (Pydantic at the edges, action item 2), D4, I9.
  - **Depends on:** S1-M1-T1, question 1.

- [ ] **S1-M1-T3: Architecture tests for `core`**
  - **Build:** Tests that guard the rules of `core` itself. They pass on the empty skeleton and keep passing as code is added.
  - **Files:** `src/clause_tracer/core/tests/test_architecture.py`.
  - **Tests first:** (1) In a fresh subprocess, `import clause_tracer.core` loads no module outside `clause_tracer` and `sys.stdlib_module_names`. (2) Every public dataclass in `core` is frozen and slotted, and no field is typed `list`, `dict` or `set`. (3) No field name of any public `core` dataclass contains a provider-specific word (`openrouter`, `zdr`, `data_collection`, `require_parameters`, `response_format`, and similar). Show each test failing once by a temporary bad change (for example `import pydantic` in `core/__init__.py`), then remove that change before the commit.
  - **Done when:** `scripts/check.sh` passes, and each test was seen to fail for the right reason.
  - **Rules:** T9, T1, B3, [ADR 0015](../adr/0015-provider-ready-seam.md) action item 2, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md), [system design 15.1](../system-design.md#151-stage-1-core) "Done when", [testing strategy 12](../testing-strategy.md#12-when-each-test-runs).
  - **Depends on:** None.

- [ ] **S1-M1-T4: Ids and enums**
  - **Build:** The seven `NewType` ids and the fourteen enums of system design 3.4 ("Ids and enums"). `ReasonCode` has one code per cause in that row, including `MATCH_UNCONFIRMED`. Add a code for each other cause Spec 5 names (for example a deposit amount with no total) and list them in the README for the owner.
  - **Files:** `src/clause_tracer/core/ids.py`, `src/clause_tracer/core/enums.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_enums.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Each enum has exactly the members that 3.4 lists, no more and no fewer. `ReasonCode` has `MATCH_UNCONFIRMED` and a code for every cause in 3.4. Each id is a plain `str` at run time.
  - **Done when:** `scripts/check.sh` passes, and the README lists every enum and its values.
  - **Rules:** [System design 3.4](../system-design.md#34-core-shapes-for-stage-1), [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) action item 1, I7 (rules return codes, never prose), T1.
  - **Depends on:** S1-M1-T3, the TypeAdapter check.

- [ ] **S1-M1-T5: The error tree**
  - **Build:** One base `ClauseTracerError(code, context)` and four groups: input errors, model-service errors, local errors, and cancellation. Start from the error classes in the architecture report's errors section. `context` holds ids, step names and counts only, never contract text.
  - **Files:** `src/clause_tracer/core/errors.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_errors.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Every error class is a `ClauseTracerError` and sits in exactly one of the four groups. Every class has its own fixed, unique `code`. `context` cannot be changed after the error is made. `SecretStoreUnavailableError`, `ModelTimeoutError` and `ReviewCancelled` exist (later tasks and stages use them).
  - **Done when:** `scripts/check.sh` passes, and the README lists each error, its group and its code.
  - **Rules:** I5, I6, I7, [system design 6.4](../system-design.md#64-errors), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md).
  - **Depends on:** S1-M1-T4.

### M2: Shapes

Every shape in system design 3.4 exists as a frozen, slotted dataclass, is exported from `clause_tracer.core`, and is listed in the core README.

- [ ] **S1-M2-T1: Wording and page-location shapes**
  - **Build:** `Wording`, `Span`, `PageBox`, `Page` and `Glyph`, with the fields of 3.4, and the `CancelCheck` type: a callable that returns true once the user has cancelled.
  - **Files:** `src/clause_tracer/core/wording.py`, `src/clause_tracer/core/document.py`, `src/clause_tracer/core/ports.py` (for `CancelCheck`), `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** A shared test checks each shape's field names against the list in 3.4 (it grows with each task). **Promise test** "every stored text keeps a written-by value" (Spec 4.7 and 6.2): a `Wording` cannot be made without `written_by`, which has no default.
  - **Done when:** `scripts/check.sh` passes, and the architecture tests cover the new shapes.
  - **Rules:** [ADR 0016](../adr/0016-legal-positions-without-a-lawyer.md), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) and its 13 Nov amendment, T13, T1, S3.
  - **Depends on:** S1-M1-T4.

- [ ] **S1-M2-T2: Document shapes**
  - **Build:** `SourceFile`, `HiddenText`, `TrackedChange`, `InputWarning`, `Document`, `MatchKey`, `Sentence` and `Clause`, with the fields of 3.4. Offsets are half-open and count code points.
  - **Files:** `src/clause_tracer/core/document.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Field names match 3.4. `Document` carries `schema_version`. A `Span` over a string with an astral character (such as an emoji) slices the right code points.
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** [System design 3.4 and 4.2](../system-design.md#42-the-offset-chain), D1, D6, S3.
  - **Depends on:** S1-M2-T1.

- [ ] **S1-M2-T3: Link and placeholder shapes**
  - **Build:** `CrossReference`, `DefinedTerm`, `Override`, `OutsideDocument`, `LinkMap`, `Party`, `PiiSuggestion`, `PlaceholderEntity`, `Segment` and `PlaceholderText`, with the fields of 3.4.
  - **Files:** `src/clause_tracer/core/link_map.py`, `src/clause_tracer/core/placeholders.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Field names match 3.4. An unresolved `CrossReference` and an `Override` with no target can be made (the target is `None`, never dropped).
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** [System design 3.4](../system-design.md#34-core-shapes-for-stage-1), [ADR 0008](../adr/0008-personal-data-detection-bundle.md), S3.
  - **Depends on:** S1-M2-T2.

- [ ] **S1-M2-T4: Playbook and settings shapes**
  - **Build:** `NumberRule`, `YesNoRule`, `WordsRule`, `Position`, `Playbook`, `PlaybookSnapshot` and `Settings`, with the fields of 3.4. Limits are `Decimal`.
  - **Files:** `src/clause_tracer/core/playbook.py`, `src/clause_tracer/core/settings.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Field names match 3.4. `Playbook` carries `schema_version`. Playbook names, topics and level text are plain `str`, not `Wording` (decided 13 Nov 2026).
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 13 Nov amendment, [Spec 4.1](../spec.md#41-playbooks), I13 (settings passed in), D6, S3.
  - **Depends on:** S1-M2-T1, question 15.

- [ ] **S1-M2-T5: Review result shapes**
  - **Build:** `Evidence`, `CheckedValue`, `JudgedLevel`, `MatchFound`, `NothingFound`, `CallFailed`, `ToolLabel` and `NotCoveredClause`, with the fields of 3.4, plus whatever questions 6 and 8 add.
  - **Files:** `src/clause_tracer/core/results.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Field names match 3.4. `MatchFound`, `NothingFound` and `CallFailed` are three unrelated types: a `CallFailed` is never an instance of `NothingFound`, and the reverse. `reasons` fields hold `ReasonCode` values, never strings.
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** I4, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md), [ADR 0002](../adr/0002-label-look-split-stamp.md), S3.
  - **Depends on:** S1-M2-T2, S1-M2-T4, questions 6 and 8.

- [ ] **S1-M2-T6: AI request and record shapes**
  - **Build:** `PromptMessage`, `AiRequest`, `Usage`, `AiReply` and `AiRecord`, with the fields of 3.4. `AiRequest.inputs` holds a frozen dataclass, typed as question 4 settles. `json_schema` is a read-only mapping. `Usage.cost_usd` is `Decimal | None`.
  - **Files:** `src/clause_tracer/core/ai.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Field names match 3.4. Changing an item of `json_schema` raises `TypeError`. Passing a plain `dict` as `inputs` fails mypy (check this once by hand, and do not commit the failing file). The architecture test finds no provider-specific field.
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** [ADR 0015](../adr/0015-provider-ready-seam.md) and its amendment, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 13 Nov amendment, [system design 6.3](../system-design.md#63-the-ai-request), D8, S3.
  - **Depends on:** S1-M2-T1, questions 4 and 10.

### M3: Label rules

Table-driven tests over the owner's tables pass for Rules 1 to 10 and for every row of the Spec 14.5 sample.

- [ ] **S1-M3-T1: Owner table format and loader**
  - **Build:** A small loader that reads the owner's TOML tables with the standard library's `tomllib` (typed values such as `Decimal` and enum names read cleanly from TOML). Create each table file with a header comment ("Expected answers. Only the owner edits this file. Constitution T11.") and no rows.
  - **Files:** `src/clause_tracer/core/tests/owner_tables.py`, `src/clause_tracer/core/tests/test_owner_tables.py`, `src/clause_tracer/core/tests/tables/label_rules.toml`, `src/clause_tracer/core/tests/tables/spec_14_5.toml`, `src/clause_tracer/core/tests/tables/auto_delete.toml`, `src/clause_tracer/core/tests/tables/scans.toml`, `src/clause_tracer/core/tests/tables/cost_estimate.toml`.
  - **Tests first:** On a small test-only table (not an owner file), the loader reads `Decimal`, `Level` and `ReasonCode` values, and rejects an unknown column or an unknown enum name with a clear error.
  - **Done when:** `scripts/check.sh` passes, and the table files hold only their header.
  - **Rules:** T11, [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) "Agent guard".
  - **Depends on:** S1-M1-T4.

- [ ] **S1-M3-T2: Spec 14.5 sample inputs**
  - **Build:** A sample file with the starter playbook of Spec 7 and, for each position, the values Spec 14.5 describes (`CheckedValue`, `JudgedLevel` or a match result). These are inputs, not expected labels. `__main__` and the sample test both read this file.
  - **Files:** `src/clause_tracer/core/samples/spec-14-5.toml`, `src/clause_tracer/core/samples/.gitkeep` (removed).
  - **Tests first:** The loader turns every entry into the shapes of M2 without error.
  - **Done when:** `scripts/check.sh` passes, and the file has one entry for each of the 11 starter positions.
  - **Rules:** S1 (a sample input), D1, AGENTS.md (sample names from Spec 14.5 only).
  - **Depends on:** S1-M2-T5, S1-M3-T1.

- [ ] **S1-M3-T3: Label-rule table (Owner)**
  - **Build:** Owner only. The rows of `label_rules.toml`: one row per case, giving the inputs and the expected level and reason codes. It must cover Rule 1 in both directions (the limit itself counts; "none" counts as 0; "unlimited" is the worst value), Rule 2 (including conditional yes), Rule 3 (quote not confirmed, number not in quote; a quote that is confirmed but not placed keeps its label), Rule 4's order, every Rule 5 cause, Rule 6 (week, month and year in both directions; business days never convert; a range; a deposit amount with and without a total; an amount and a percentage that disagree), the unit spellings Rule 6 accepts, Rule 7 (including an unsure missing level, `MATCH_UNCONFIRMED`, and a failed call that never gives the missing level), Rule 9 (hidden and undecodable text), and Rule 10. The AI agent does not write or change it (T11). It may list, in chat, which Spec lines still have no row.
  - **Files:** `src/clause_tracer/core/tests/tables/label_rules.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` passes.
  - **Rules:** T11, [Spec 5](../spec.md#5-labelling-rules), [testing strategy 4 and 14](../testing-strategy.md#14-example-tests).
  - **Depends on:** S1-M3-T1, questions 6, 7, 8 and 9.

- [ ] **S1-M3-T4: Spec 14.5 label table (Owner)**
  - **Build:** Owner only. One row per starter position in `spec_14_5.toml`: the expected level, the reason codes, and who wrote the label (code or AI). The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/spec_14_5.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the 11 rows and said so. `scripts/check.sh` passes.
  - **Rules:** T11, [Spec 14.5](../spec.md#145-sample-data), [system design 15.1](../system-design.md#151-stage-1-core) "Done when".
  - **Depends on:** S1-M3-T2.

- [ ] **S1-M3-T5: Level order and Rule 4**
  - **Build:** The order of levels (preferred, then acceptable, then walk-away) and a pure function that combines several values by Rule 4: a readable walk-away wins, then any unsure, then the worst level. It also adds the "clauses disagree" reason when the values differ.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/tests/conftest.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 4 rows of the owner table. Hypothesis properties: the order of the values never changes the result; a set with one readable walk-away always gives walk-away (**promise test**, part of "every planted walk-away gets walk-away", Spec 11); an unsure result always carries at least one reason (glossary: unsure "always explains why"). Register a `nightly` Hypothesis profile with 2,000 examples in `conftest.py`.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 4, T1, T11, T13, I4, [testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants).
  - **Depends on:** S1-M3-T3.

- [ ] **S1-M3-T6: Unit conversion (Rule 6)**
  - **Build:** A pure function that converts a number from the unit as written into the playbook's `Unit`, or says why it cannot (business days, an unknown unit). Also the deposit rule: an amount becomes a percentage when the total is known, otherwise it is unsure.
  - **Files:** `src/clause_tracer/core/units.py`, `src/clause_tracer/core/tests/test_units.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 6 rows and the unit-spelling rows of the owner table. A property: converting there and back gives the same number for weeks, months and years.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 6, T1, T11.
  - **Depends on:** S1-M3-T3.

- [ ] **S1-M3-T7: Unreadable text under a quote (Rule 9)**
  - **Build:** A pure check that says whether a value's quote overlaps hidden text or undecodable text in the `Document`. Such a value is unsure and does not count as readable for Rule 4 step 1.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 9 rows of the owner table. **Promise test** "values resting on hidden text are unsure" (Spec 11): a walk-away value on hidden text gives unsure, not walk-away. Edge cases: a quote that touches a hidden span only at its end offset (half-open, so no overlap); hidden text with no span.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 9, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) and its amendment, T13, T11.
  - **Depends on:** S1-M3-T5.

- [ ] **S1-M3-T8: Number labels**
  - **Build:** `label_number`: from a number position and its checked values to one `ToolLabel` written by code. It applies Rule 1 limits, Rule 6 through S1-M3-T6, Rule 5 (vague wording, another start point, business days), Rule 3 (failed quote), the unplaceable-quote case (label kept), Rule 9, then Rule 4. Bundle inputs into one small shape if more than four are needed (I3).
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 1, 3, 5 and 6 rows of the owner table, run through `label_number`.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rules 1, 3, 5, 6; I3, I4, T1, T11.
  - **Depends on:** S1-M3-T6, S1-M3-T7.

- [ ] **S1-M3-T9: Yes/no labels**
  - **Build:** `label_yes_no`: yes gives the yes level; no, unclear and missing give the no level; a conditional yes gives unsure with the conditional-yes reason. Rules 3, 9 and 4 apply as for numbers. The label is written by code.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 2 rows of the owner table, and the Rule 3, 4 and 9 rows that use yes/no positions.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 2, T1, T11.
  - **Depends on:** S1-M3-T7.

- [ ] **S1-M3-T10: Words labels**
  - **Build:** A function that combines the AI's judged levels for a words position by Rule 4, with Rule 9 applied. The label is written by AI, so it is drawn in pencil.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The words rows of the owner table. Every words label has `written_by` AI, and every number and yes/no label has `written_by` code.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) (who picks the label), [ADR 0002](../adr/0002-label-look-split-stamp.md), [ADR 0016](../adr/0016-legal-positions-without-a-lawyer.md), T11.
  - **Depends on:** S1-M3-T7.

- [ ] **S1-M3-T11: Missing, unconfirmed and failed matches (Rule 7)**
  - **Build:** A function from a match result to a label: nothing found gives the missing level; an unconfirmed match gives unsure with `MATCH_UNCONFIRMED` and the clause to read; a failed call gives unsure with the "reply broken twice" reason and never the missing level.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 7 rows of the owner table. A property over every position and every `CallFailed`: the label is unsure, so it never takes a missing level of preferred, acceptable or walk-away (system design 8.2: a broken reply is never "nothing found").
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 7, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md), I4, [system design 8.2](../system-design.md#82-calls-to-the-ai-service), T11.
  - **Depends on:** S1-M3-T5, question 8.

- [ ] **S1-M3-T12: Unloaded documents (Rule 10)**
  - **Build:** An overlay that makes a label unsure when its evidence trail reaches a document that is not loaded, unless Rule 4 step 1 already made it walk-away. Its input is what question 9 settles.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The Rule 10 rows of the owner table: a walk-away stays walk-away; any other level becomes unsure with the unloaded-document reason.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 10, T11.
  - **Depends on:** S1-M3-T5, question 9.

- [ ] **S1-M3-T13: The Spec 14.5 sample and "no position dropped"**
  - **Build:** One entry function that labels every position of a playbook snapshot, by calling the functions above. It returns one `ToolLabel` per position, in playbook order.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/tests/test_spec_14_5.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The sample inputs of S1-M3-T2 give exactly the owner's `spec_14_5.toml` rows. A property: every position of any generated snapshot gets exactly one label (Rule 3: "A position is never dropped silently").
  - **Done when:** `scripts/check.sh` passes, every Spec 14.5 row passes, and the owner tables are unchanged in the commit.
  - **Rules:** [Spec 5 and 14.5](../spec.md#145-sample-data), [system design 15.1](../system-design.md#151-stage-1-core) "Done when", T11, T13, B5.
  - **Depends on:** S1-M3-T4, S1-M3-T8, S1-M3-T9, S1-M3-T10, S1-M3-T11, S1-M3-T12.

### M4: Ports, the request hash, fakes and auto-delete

Any later module can be tested against a fake of each port, with the replay fake failing on a request it does not know, and a fixed clock driving auto-delete.

- [ ] **S1-M4-T1: The five ports**
  - **Build:** `AiClient`, `PiiDetector`, `ReviewStore`, `SecretStore` and `Clock` as `typing.Protocol` classes, with the methods of system design 3.4. `ReviewStore` gets the methods question 5 settles. Each method has a short contract note: input, output, errors raised, side effects.
  - **Files:** `src/clause_tracer/core/ports.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_ports.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** A tiny stub class for each port type-checks as that port under mypy strict, and a stub with a wrong method signature does not (check the failing case once by hand).
  - **Done when:** `scripts/check.sh` passes, and the README lists each port with its methods.
  - **Rules:** P4, T2, B3, I11, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md), [ADR 0015](../adr/0015-provider-ready-seam.md), [system design 3.1](../system-design.md#31-the-engine).
  - **Depends on:** S1-M1-T5, S1-M2-T3, S1-M2-T6, question 5.

- [ ] **S1-M4-T2: Pure hash of the exact request**
  - **Build:** A pure function from an `AiRequest` to a SHA-256 hex string. It covers every field, including `inputs` and `json_schema`, through a fixed, documented encoding.
  - **Files:** `src/clause_tracer/core/request_hash.py`, `src/clause_tracer/core/tests/test_request_hash.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The same request gives the same hash, also in two subprocesses with different `PYTHONHASHSEED` values. Changing any single field changes the hash (one case per field). The key order of `json_schema` does not change the hash. A Hypothesis property: a rebuilt copy of a request has the same hash.
  - **Done when:** `scripts/check.sh` passes, and the README states the encoding.
  - **Rules:** T1, D8, [ADR 0013](../adr/0013-test-layers-and-release-gates.md) 13 Nov amendment, [system design 7](../system-design.md#7-caching-resume-and-cost).
  - **Depends on:** S1-M2-T6.

- [ ] **S1-M4-T3: The replay fake**
  - **Build:** An in-memory `AiClient` fake keyed by the request hash, in the place question 3 settles. It is given its recordings by the caller and never reads a file. It raises `UnrecordedRequest` on a miss, reports `unused_keys()`, and can be told to raise a model-service error for the next call (`fail_next`). Add a pytest fixture that hands out a replay fake and asserts `unused_keys() == []` at the end of the test.
  - **Files:** `src/clause_tracer/core/fakes.py`, `src/clause_tracer/core/tests/test_replay_fake.py`, `src/clause_tracer/core/tests/conftest.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** A recorded request returns its exact `AiReply`. A request that differs by one character raises `UnrecordedRequest`, whose message names the step and the hash, not the prompt. A recording never asked for appears in `unused_keys()`, and the fixture fails the test. `fail_next(ModelTimeoutError)` raises that error once, then replies normally.
  - **Done when:** `scripts/check.sh` passes, and the fake type-checks as an `AiClient`.
  - **Rules:** T3, T7, T12, T1, [ADR 0013](../adr/0013-test-layers-and-release-gates.md) action item 1 and amendments, [testing strategy 6.1](../testing-strategy.md#61-the-replay-fake).
  - **Depends on:** S1-M4-T1, S1-M4-T2, question 3.

- [ ] **S1-M4-T4: Fake detector, secret store and clock**
  - **Build:** A fake `PiiDetector` that returns the suggestions it was given for a text; an in-memory `SecretStore` keyed by provider id that can be switched to "unavailable"; and a fixed `Clock` that can be moved forward and back. Write the behaviour tests as functions that take the implementation as a fixture, so stage 6 can run them against the real adapters.
  - **Files:** `src/clause_tracer/core/fakes.py`, `src/clause_tracer/core/tests/test_fakes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The detector returns the planted suggestions and nothing else. The secret store gets back what was put; deleting a missing secret succeeds (I8); when unavailable, every call raises `SecretStoreUnavailableError`. The clock returns exactly the time it was set to.
  - **Done when:** `scripts/check.sh` passes, and each fake type-checks as its port.
  - **Rules:** T3, T2, I8, [ADR 0006](../adr/0006-encrypted-storage-and-secrets.md), [ADR 0015](../adr/0015-provider-ready-seam.md) (credentials under a provider id), [testing strategy 3](../testing-strategy.md#3-five-layers).
  - **Depends on:** S1-M4-T1.

- [ ] **S1-M4-T5: Auto-delete table (Owner)**
  - **Build:** Owner only. The rows of `auto_delete.toml`: last change, setting (7, 30 or 90 days), "now", and the expected due date, "due now" and "warning shown" answers. Cover the exact boundaries, "Keep it", the 3-day warning, lowering the setting (nothing sooner than 3 days later), a laptop off for months, and a clock that jumps backwards. The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/auto_delete.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` passes.
  - **Rules:** T11, [Spec 9](../spec.md#9-running-the-app) (auto-delete), [testing strategy 8](../testing-strategy.md#8-privacy-and-security-tests) (auto-delete row).
  - **Depends on:** S1-M3-T1, question 14.

- [ ] **S1-M4-T6: Auto-delete date rules**
  - **Build:** Pure functions, given times as inputs and never reading a clock: a review's due date from its last change and the setting; whether it is due at "now"; whether it is in the 3-day warning window; the due date after the setting is lowered.
  - **Files:** `src/clause_tracer/core/auto_delete.py`, `src/clause_tracer/core/tests/test_auto_delete.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Every row of the owner table. **Promise test** "auto-delete runs on schedule" (Spec 11, unit part): a Hypothesis property that a review is due exactly when "now" reaches its due date, and that lowering the setting never makes a review due sooner than 3 days after the change.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** T1, T2, T13, T11, [Spec 9](../spec.md#9-running-the-app).
  - **Depends on:** S1-M4-T5.

- [ ] **S1-M4-T7: In-memory review store**
  - **Build:** An in-memory `ReviewStore` fake with the methods of S1-M4-T1. Its purge uses the date rules of S1-M4-T6 with the "now" it is given. Write its tests as behaviour tests that take the store as a fixture, for reuse in stage 6.
  - **Files:** `src/clause_tracer/core/fakes.py`, `src/clause_tracer/core/tests/test_fakes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** A saved `AiRecord` loads back equal. Records are append-only: saving the same record id twice is refused. Deleting a review twice succeeds (I8). Purge with a fixed "now" removes due reviews only, and returns the same type when nothing is due (I4).
  - **Done when:** `scripts/check.sh` passes, and the fake type-checks as a `ReviewStore`.
  - **Rules:** T3, I4, I8, D1, D8, [ADR 0006](../adr/0006-encrypted-storage-and-secrets.md).
  - **Depends on:** S1-M4-T1, S1-M4-T6.

### M5: Scans, the cost estimate and the last check before drawing

The output scans catch every case in the owner's table, the cost estimate gives the owner's ranges, and the last check before drawing passes invariant 7.

- [ ] **S1-M5-T1: Scan table (Owner)**
  - **Build:** Owner only. In `scans.toml`: the word lists the scans use (law words, advice such as "safe to sign", injection tells such as "ignore" or "mark every", "call" and "visit"), and the cases with their expected result. Cases must include "Dear John", a web address, "safe to sign", an acceptable limit, a wrong label word, an invented number, an unknown placeholder and text over the length cap, plus innocent look-alikes that must pass. The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/scans.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the lists and cases and said so. `scripts/check.sh` passes.
  - **Rules:** T11, [Spec 6.2](../spec.md#62-rules-for-every-ai-step), [testing strategy 4](../testing-strategy.md#4-what-to-test-in-each-module) (`core` row).
  - **Depends on:** S1-M3-T1, question 12.

- [ ] **S1-M5-T2: Word and pattern scans**
  - **Build:** A pure scan of one AI text that returns a tuple of finding codes, empty when the text passes. This task covers law words, advice, injection tells, web addresses, "call" and "visit", a label word that differs from the code's label, and the length cap.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The matching rows of the owner table. **Promise test** "no AI text states what a law allows" (Spec 11): every law word in the owner's list fails, in any letter case.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** T1, T13, T11, I4, [Spec 6.2](../spec.md#62-rules-for-every-ai-step), [system design 8.2](../system-design.md#82-calls-to-the-ai-service).
  - **Depends on:** S1-M5-T1, question 10.

- [ ] **S1-M5-T3: Value and name scans**
  - **Build:** The rest of the scan, given the allowed numbers, the acceptable limits, the known placeholders and defined roles, and a `PiiDetector` passed in. It fails any number not allowed, any acceptable limit, any unknown placeholder, and any name, email, phone or address the detector finds that is not a known placeholder or role.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** The matching rows of the owner table, with the fake detector. **Promise test** "no acceptable limit reaches the message step" (Spec 11, scan part): an acceptable limit fails in every written form the owner's table lists.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** P4 (detector passed in), T2, T13, T11, [Spec 6.2](../spec.md#62-rules-for-every-ai-step).
  - **Depends on:** S1-M5-T2, S1-M4-T4.

- [ ] **S1-M5-T4: Cost estimate table (Owner)**
  - **Build:** Owner only. The rows of `cost_estimate.toml`: inputs in the form question 13 settles, and the expected low and high amounts. The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/cost_estimate.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` passes.
  - **Rules:** T11, [Spec 9](../spec.md#9-running-the-app) (cost), [system design 7](../system-design.md#7-caching-resume-and-cost) (estimate).
  - **Depends on:** S1-M3-T1, question 13.

- [ ] **S1-M5-T5: Cost estimate**
  - **Build:** A pure function that gives the pre-run estimate as a range in US dollars, from the inputs question 13 settles. Prices are passed in; nothing provider-specific enters `core`.
  - **Files:** `src/clause_tracer/core/cost.py`, `src/clause_tracer/core/tests/test_cost.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Every row of the owner table. A property: the low end is never above the high end, and neither is negative.
  - **Done when:** `scripts/check.sh` passes, and the owner table is unchanged in the commit.
  - **Rules:** T1, T11, [ADR 0015](../adr/0015-provider-ready-seam.md), [ADR 0010](../adr/0010-starting-models.md).
  - **Depends on:** S1-M5-T4.

- [ ] **S1-M5-T6: Last check before drawing: the text**
  - **Build:** The first half of the last check. Given the document, the clause, the evidence and the quote, it confirms that the folded quote appears exactly once inside the cited sentences, at the evidence's span. It is written fresh, not shared with `checking`'s quote check (a different code path). It returns a result, and fails closed.
  - **Files:** `src/clause_tracer/core/draw_check.py`, `src/clause_tracer/core/tests/test_draw_check.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** Example cases: an exact quote passes; curly against straight quotes and runs of spaces pass (the fold of question 11); a quote found twice in the cited sentences fails; a quote outside the cited sentences fails; one changed character fails. **Promise test** "no made-up quote reaches the screen" (Spec 11, unit part).
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** T1, T13, I5, I4, [system design 4.2](../system-design.md#42-the-offset-chain), [Spec 2](../spec.md#2-glossary) (quote check).
  - **Depends on:** S1-M2-T5, question 11.

- [ ] **S1-M5-T7: Last check before drawing: page boxes**
  - **Build:** The second half: every character of the span that the app did not insert has a glyph whose box lies inside its page. Documents without glyphs follow question 11.
  - **Files:** `src/clause_tracer/core/draw_check.py`, `src/clause_tracer/core/tests/test_draw_check.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** A box inside its page passes. A box past the page edge fails. A character with no glyph that the app did not insert fails. Characters the app inserted (`None` in `char_map`) need no box. A ligature (one glyph, two letters) passes.
  - **Done when:** `scripts/check.sh` passes.
  - **Rules:** T1, I5, [ADR 0007](../adr/0007-document-reading-stack.md) (one coordinate system), [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) (unplaceable quote).
  - **Depends on:** S1-M5-T6.

- [ ] **S1-M5-T8: Invariant 7 with the hazard alphabet**
  - **Build:** A Hypothesis strategy for "hazard" text (ligatures, soft hyphens, curly quotes, zero-width characters, bidi controls, `ß`, astral characters and the `⟦` escape), and a property test of invariant 7 on generated documents. Later stages reuse the strategy.
  - **Files:** `src/clause_tracer/core/tests/strategies.py`, `src/clause_tracer/core/tests/test_draw_check.py`.
  - **Tests first:** For any generated document and any span inside one sentence, the last check passes; changing one character of the quote makes it fail. Offsets count code points, not UTF-16 units. Every failure Hypothesis finds becomes a committed `@example`. **Promise test** "every evidence link scrolls to the right place" (Spec 11, unit part).
  - **Done when:** `scripts/check.sh` passes, and the property runs with the `nightly` profile too (`--hypothesis-profile=nightly`) without failure.
  - **Rules:** T6, T13, [testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants), [ADR 0013](../adr/0013-test-layers-and-release-gates.md).
  - **Depends on:** S1-M5-T7.

### M6: Run alone and close the stage

`python -m clause_tracer.core` prints the Spec 14.5 labels, the README records everything `core` offers, and the owner has the stage report.

- [ ] **S1-M6-T1: Run `core` alone on the sample**
  - **Build:** `python -m clause_tracer.core --input <file>` reads a sample (default: `samples/spec-14-5.toml`) and prints one line per position: topic, label, reason codes, and who wrote it. Only `__main__` reads a file; nothing else in `core` does.
  - **Files:** `src/clause_tracer/core/__main__.py`, `src/clause_tracer/core/tests/test_smoke.py`.
  - **Tests first:** `main()` returns 0 on the sample and prints 11 lines that agree with the owner's `spec_14_5.toml`. A missing input file returns a non-zero exit code and writes to standard error.
  - **Done when:** `.venv/bin/uv run python -m clause_tracer.core` prints the 11 labels, and `scripts/check.sh` passes.
  - **Rules:** S1, S2, I12, T1, [system design 6.2](../system-design.md#62-the-command-line).
  - **Depends on:** S1-M3-T13.

- [ ] **S1-M6-T2: Finish the module README and the module map**
  - **Build:** Make `src/clause_tracer/core/README.md` complete: purpose, input and output shapes, the five ports with their methods, the fakes, every public function with its contract note, the errors, the owner tables and who edits them, and how to run it alone. Update the `core` row in `src/clause_tracer/README.md`, and the docstring in `core/__init__.py` ("labelling", British spelling).
  - **Files:** `src/clause_tracer/core/README.md`, `src/clause_tracer/README.md`, `src/clause_tracer/core/__init__.py`.
  - **Tests first:** None. Check: every name in `clause_tracer.core.__all__` appears in the README (a short test in `test_architecture.py` that reads the README text).
  - **Done when:** `scripts/check.sh` passes, and the README has no "planned" sections left.
  - **Rules:** S3, I11, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) action item 4, [WRITING_DOCS](../../WRITING_DOCS.md) sections 2 and 9.
  - **Depends on:** S1-M6-T1, S1-M5-T8, S1-M4-T7, S1-M5-T5, S1-M5-T3.

- [ ] **S1-M6-T3: Stage report to the owner**
  - **Build:** Run every check in section 7, set this plan to Done, and write the report described there.
  - **Files:** `docs/plans/stage-01-core.md`.
  - **Tests first:** None. Check: section 7 is fully ticked.
  - **Done when:** The owner has the report.
  - **Rules:** [Plans README](README.md) ("When the stage is done").
  - **Depends on:** S1-M6-T2.

## 6. Open questions

System design 15.1 says nothing in stage 1 is left open apart from the `TypeAdapter` check. Planning found the points below, which the docs do not settle.

| # | Question | Needed by task | Recommendation (if any) | Owner's answer |
| --- | --- | --- | --- | --- |
| 1 | The TypeAdapter check must run "on the pinned version", but Pydantic is not in `pyproject.toml` and `core` never imports it. Add Pydantic as a runtime dependency now, or run the check with `uv run --with pydantic` and pin it in stage 6? | S1-M1-T2, the TypeAdapter check | Recommendation: add it now. ADR 0005 accepts it, Presidio brings it anyway, and the check then proves the version that ships. | |
| 2 | Which test tooling arrives in stage 1? (a) Branch-coverage measurement for the 95% `core` target (no tool is installed). (b) The CI guard that fails a change editing both code and owner tables (ADR 0013 action item 2; no stage is named, and the way the owner approves is not designed). (c) The suite-wide socket block (`pytest-socket`). (d) A nightly job for the 2,000-example Hypothesis profile. A "yes" adds tasks to this plan through the change log. | S1-M1-T1, S1-M3-T1 | Recommendation: (a) and (b) in stage 1, because the owner tables first appear here; (c) and (d) later, since `core` makes no network calls. | |
| 3 | Where do the fakes live? System design 3.4 says "`core`'s test support", but testing strategy 6.1 has each module's `__main__` hand sample replies to the replay fake, and `__main__` is shipped code. | S1-M4-T3 | Recommendation: `clause_tracer.core.fakes`, standard library only, exported from `core`. | |
| 4 | What is the type of `AiRequest.inputs` in stage 1, before any step's input shape exists (they come with each step in stage 8)? Also, `AiRecord` has no `schema_version`, though 3.4 says stored records carry one. | S1-M2-T6 | Recommendation: a small marker base class or `Protocol` for step input shapes, with a test-only shape in stage 1. Add `schema_version` to `AiRecord` only if the owner wants it on the record rather than on the storage row. | |
| 5 | Which `ReviewStore` methods does stage 1 draft? Derived records need the cache key, and user state needs shapes, and both come in stage 6. | S1-M4-T1, S1-M4-T7 | Recommendation: raw records (`AiRecord`), list reviews, delete a review, purge given "now" in stage 1; derived and user-state methods added in stage 6 as new methods (D5). | |
| 6 | How do "unlimited" and "none" (Rule 1) reach `core`? `CheckedValue` has no field for "unlimited", and the number parser is built in stage 8. | S1-M2-T5, S1-M3-T3 | Recommendation: the stage 8 parser turns "none" into 0; add one optional field for "unlimited" to `CheckedValue` now (D5). | |
| 7 | How does code know a start point is "other than the invoice date" (Rule 5)? `NumberRule` has no start-point field, and positions are the user's own. | S1-M3-T3, S1-M3-T8 | Recommendation: in stage 1, `core` turns an "other start point" reason already on the value into unsure. How the start point is compared is settled before stage 8. | |
| 8 | Which match result carries `MATCH_UNCONFIRMED` and the clause to read? `MatchFound`, `NothingFound` and `CallFailed` have no field for it. | S1-M2-T5, S1-M3-T11 | Recommendation: a fourth result type, such as `MatchUnconfirmed(position_id, clause_ids)`. | |
| 9 | What does the Rule 10 overlay take as input? Building a label's evidence trail (cross-references, terms, overrides) is not assigned to any module. | S1-M3-T3, S1-M3-T12 | Recommendation: in stage 1 it takes the outside documents the trail reaches; who builds the trail is settled before stage 8. | |
| 10 | Stage 1 functions need shapes that 3.4 does not list: scan finding codes, the last check's result, the cost range, an input bundle for the label functions (I3), and any extra reason codes. May these be added in `core`, with 3.4 updated in the same commit? | S1-M2-T6, S1-M3-T8, S1-M5-T2 | Recommendation: yes; the owner approves the list once, at the end of M2. | |
| 11 | The last check before drawing: (a) which fold does it use? Match-key folding is built in stage 2 and the quote check in stage 8. (b) Text, Markdown, pasted and Word documents have no glyphs, so the box half cannot apply as written. | S1-M5-T6, S1-M5-T7 | Recommendation: (a) the Spec 2 quote-check fold (curly quotes made straight, runs of spaces and line breaks collapsed), written fresh in `core`; (b) the box half runs only when the document has glyphs. | |
| 12 | The scans' length cap: what is it, and is it one number or one per slot? | S1-M5-T1, S1-M5-T2 | None. | |
| 13 | The cost estimate: what goes in (positions, clauses, contract tokens, prices per token, the cache-hit share?) and how is the range formed? Spec 9 and system design 7 give only the call count and "a range". | S1-M5-T4, S1-M5-T5 | Recommendation: prices passed in by the caller, call counts from the system design 7 estimate, and the range from "caching hits" to "caching misses". | |
| 14 | Auto-delete: what happens when the clock jumps backwards, so a review's last change is later than "now"? Spec 9 does not say. | S1-M4-T5 | Recommendation: never delete earlier than the rule allows; treat the review as not due. | |
| 15 | The Spec 4.1 playbook checks (limits, at most 100%, preferred stricter than acceptable, yes better than no) are not in 15.1. Do they belong in `core` now, as a pure function that stage 6 import and stage 12 editor share? | S1-M2-T4 | Recommendation: leave them to stage 6, where playbook files are read, unless the owner wants them now. | |

## 7. Done when

- [ ] Every task above is ticked.
- [ ] `scripts/check.sh` passes with no errors: ruff, format, mypy strict, `lint-imports` and pytest.
- [ ] The five import contracts in `pyproject.toml` are unchanged and pass.
- [ ] The architecture test passes: importing `core` loads only the standard library.
- [ ] The architecture test passes: no `core` shape has a provider-specific field (ADR 0015 action item 2).
- [ ] The label-rule tests cover every row of the Spec 14.5 sample, against the owner's table.
- [ ] No commit changed code and an owner table together (T11).
- [ ] Every promise the stage touches has its test (T13): every planted walk-away gets walk-away (rules part); no made-up quote reaches the screen (last check); every evidence link scrolls to the right place (invariant 7); values on hidden text are unsure; no acceptable limit reaches the message step (scan part); no AI text states what a law allows (scan part); auto-delete runs on schedule (date rules); every stored text keeps a written-by value (`Wording`).
- [ ] `src/clause_tracer/core/README.md` records the shapes, ports, fakes and functions (S3, ADR 0005 action item 4), and `src/clause_tracer/README.md` matches it.
- [ ] `.venv/bin/uv run python -m clause_tracer.core` runs alone on the sample (S1).
- [ ] The TypeAdapter check result is in the change log.
- [ ] The owner has been told what was built, and what stage 2 should know:
  - the shapes `ingest` will fill (`Document`, `SourceFile`, `Clause`, `Sentence`, `MatchKey`, `InputWarning`, `Span`) and any change from 3.4;
  - the answers to the open questions, and any shape added under question 10;
  - the decision-record action items this stage closes, for the owner to tick: ADR 0005 items 2 and 4, ADR 0012 item 1, ADR 0013 item 1, ADR 0015 items 1 and 2;
  - a reminder about the ten test contracts;
  - that `cli` has no `README.md` or `samples/` yet, which the planned "every module has a README" architecture test will need.

## 8. Change log

| Date | Change | Why |
| --- | --- | --- |
| None | | |

## 9. Notes for the next stage

None yet. Filled in when the stage is done: what was built, what differs from the outline, and what stage 2 should know.
