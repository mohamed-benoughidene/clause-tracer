# Stage 1 plan: `core`

| | |
| --- | --- |
| Stage | 1, `core` |
| Status | In progress |
| Branch | One branch for each milestone, cut from `main`: `feat/core-m1-foundations`, `feat/core-m2-shapes`, `feat/core-m3-label-rules`, `feat/core-m4-ports-and-fakes`, `feat/core-m5-scans-and-last-check`, `feat/core-m6-run-alone`. See [the README](README.md), "Branches and pull requests" |
| Accepted on | 16 Nov 2026 |
| Stage outline | [System design section 15.1](../system-design.md#151-stage-1-core) |

## 1. Goal

`core` holds every shape, port, error, fake and pure rule that system design section 15.1 lists, with table-driven and property tests. Importing `core` loads only the standard library, branch coverage of `core` is at least 95%, and `python -m clause_tracer.core` prints the labels of the Spec 14.5 sample.

## 2. Scope

**Where the code starts.** The skeleton is empty. `src/clause_tracer/core/` holds only `__init__.py` (an empty `__all__`), `__main__.py` (prints "not built yet"), a README with "planned" shapes, `tests/__init__.py`, `tests/test_smoke.py` and `samples/.gitkeep`. `pyproject.toml` has no runtime dependencies. Its dev group has `pytest`, `ruff`, `mypy`, `import-linter` and `uv`, but no Hypothesis, no Pydantic and no coverage tool. There is no `conftest.py` anywhere. The five import contracts in `pyproject.toml` already cover `core` and stay as they are. `mypy` checks `src/` in strict mode, so every test in `src/` needs type annotations.

### Builds

- The ids, enums, shapes, ports and fakes of [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), including both "Decided for stage 1" lists (13 and 14 Nov 2026) and the table "Shapes for the stage 1 functions".
- The error tree of [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) ("Errors") and [6.4](../system-design.md#64-errors).
- The five ports as `typing.Protocol` classes, and their fakes in `clause_tracer.core.fakes`, with behaviour suites in `tests/contracts/`.
- A pure hash of the exact AI request.
- Label rules 1 to 10 as pure functions, with `MATCH_UNCONFIRMED`, the unplaceable-quote case, and undecodable text under Rule 9. Unit conversion (Rule 6).
- The playbook checks of Spec 4.1.
- The auto-delete date rules, the cost estimate, the output scans, the quote-check fold and the last check before drawing. The output scans include the five style scans of [Spec 6.2](../spec.md#62-rules-for-every-ai-step) (first-person words, filler, evaluative words, a reason with no anchor, added sentences), decided 14 Nov 2026, and the cost estimate counts explain calls for words positions only ([system design 7](../system-design.md#7-caching-resume-and-cost)).
- Owner-owned expected-answer tables (Constitution T11): label rules, units, the Spec 14.5 sample, playbook checks, auto-delete dates, scans and the cost estimate.
- Tooling: Hypothesis, Pydantic, branch-coverage measurement with a 95% floor for `core`, and the owner-table guard ([testing strategy 10 and 11](../testing-strategy.md#10-keeping-agent-written-tests-honest)).
- Architecture tests: importing `core` loads only the standard library; no shape has a provider-specific field; every shape is frozen, slotted and keyword-only.
- Property tests with Hypothesis, including offset invariant 7.
- `python -m clause_tracer.core --input …` on a sample (S1), and the module README with every shape, port and function (S3).

### Leaves to later stages

- Golden files and the `--update-goldens` command: stage 2, the first module with golden files ([testing strategy 13](../testing-strategy.md#13-gaps-today-and-the-order-to-close-them)).
- Building match keys and the fold for them, and offset invariants 2 and 4: stage 2. The placeholder map and invariant 3: stage 4. Glyphs, page boxes and invariants 1, 5 (in `checking`) and 6: stages 5 and 8.
- The nightly job with the 2,000-example Hypothesis profile: stage 5. The suite-wide socket block: stage 6 ([testing strategy 13](../testing-strategy.md#13-gaps-today-and-the-order-to-close-them)).
- User state and `Customer`; storage rows, the key table and migrations; derived records and user state in `ReviewStore`; `StepSpec`, the cache key, runner events and the cancel token: stage 6 ([system design 3.4, "Left to later stages"](../system-design.md#34-core-shapes-for-stage-1)).
- Mapping errors to review statuses and exit codes (including the message for a rate limit), loading and validating `Settings`, reading playbook files: stage 6. Raising `RateLimitedError` from a real HTTP 429: stage 9.
- The contract suites run against real adapters: stage 6 (store, secrets), 7 (Presidio), 9 (OpenRouter).
- The number parser and the quote check; how a start point is compared; who builds the evidence trail; the "searched, nothing found" list; explanation parts; keywords on `Position`; the step input shapes of each AI step; the code templates for a label's panel words; the template fallback after a failed scan; the prompt rules for AI text: stage 8 ([system design 15.8](../system-design.md#158-stage-8-checking-and-the-message-templates)).
- The lint script for fixed copy: already built (`scripts/copy_lint.py`, run by `scripts/check.sh`); this plan leaves it as it is ([testing strategy 12](../testing-strategy.md#12-when-each-test-runs)).
- AI reply schemas (Pydantic, in the owning module): stages 8, 9 and 11.
- The spend ledger: stage 9. The `paid` marker and the report script: stage 10.
- `Suggestion` and the report's contents: stage 11. Engine protocol shapes, theme and text size, and the count of reviews affected when auto-delete is lowered: stage 12.
- Coverage floors for the other packages: the stage that builds each one. The Windows CI job: stage 5 or 6. The mutation report: before a release.

## 3. Read first

- [AGENTS.md](../../AGENTS.md), the [Constitution](../../Constitution.md), [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md), and [WRITING_DOCS.md](../../WRITING_DOCS.md) sections 2 and 9.
- [System design](../system-design.md): [3.1](../system-design.md#31-the-engine) (parts and ports), [3.4](../system-design.md#34-core-shapes-for-stage-1) (all of it: it holds the exact shapes), [4.2](../system-design.md#42-the-offset-chain), [5.1](../system-design.md#51-three-kinds-of-data), [6.3](../system-design.md#63-the-ai-request), [6.4](../system-design.md#64-errors), [7](../system-design.md#7-caching-resume-and-cost) (with the estimate formula), [8.2](../system-design.md#82-calls-to-the-ai-service), [15](../system-design.md#15-build-stages) and [15.1](../system-design.md#151-stage-1-core). Skim 15.2 to 15.12 to see what later stages take from `core`.
- [Testing strategy](../testing-strategy.md): sections [1](../testing-strategy.md#1-what-the-tests-must-prove), [2](../testing-strategy.md#2-principles), [3](../testing-strategy.md#3-five-layers), [4](../testing-strategy.md#4-what-to-test-in-each-module) (the `core` row), [5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 7 and the hazard alphabet), [6.1](../testing-strategy.md#61-the-replay-fake), [10](../testing-strategy.md#10-keeping-agent-written-tests-honest) (with the owner-table guard), [11](../testing-strategy.md#11-coverage-targets), [12](../testing-strategy.md#12-when-each-test-runs) (architecture tests), [14](../testing-strategy.md#14-example-tests).
- [Spec](../spec.md): [2](../spec.md#2-glossary) (glossary, and the quote check), [4.1](../spec.md#41-playbooks), [5](../spec.md#5-labelling-rules) (every rule), [6.1](../spec.md#61-steps) (steps 6a to 8, and step 10), [6.2](../spec.md#62-rules-for-every-ai-step) (with the length caps), [6.3](../spec.md#63-review-statuses), [7](../spec.md#7-starter-playbook), [8.3](../spec.md#83-stored-data), [9](../spec.md#9-running-the-app) (cost and auto-delete), [11](../spec.md#11-acceptance-tests), [14.5](../spec.md#145-sample-data).
- [UX copy 1.1](../ux-copy.md#11-signs-of-machine-made-text) (signs of machine-made text, and the "Keep" strings the style scans must pass). Read only.
- Decision records: [ADR 0002](../adr/0002-label-look-split-stamp.md) (pencilled labels), [ADR 0004](../adr/0004-code-layout.md), [ADR 0011](../adr/0011-who-writes-the-words.md) with its amendment of 14 Nov 2026 (who writes a label's words), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) with all three amendments, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) with both amendments, [ADR 0013](../adr/0013-test-layers-and-release-gates.md) with all three amendments, [ADR 0015](../adr/0015-provider-ready-seam.md) with its amendment, [ADR 0016](../adr/0016-legal-positions-without-a-lawyer.md) (section 3 and action item 3).
- [The architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md), three parts only, as background: [errors](../../reports/Clause%20Tracer%20pipeline%20architecture.md#errors-carry-codes-and-only-the-edge-turns-them-into-words), [labels](../../reports/Clause%20Tracer%20pipeline%20architecture.md#labels-8-are-pure-functions-and-unsure-is-the-abstention-channel), and [scans](../../reports/Clause%20Tracer%20pipeline%20architecture.md#judge-9-explain-10-and-summarise-11-templates-first-fenced-slots-for-the-rest). Where the report and the system design or this plan differ, the system design and this plan win.
- The current code: [`src/clause_tracer/README.md`](../../src/clause_tracer/README.md), everything in [`src/clause_tracer/core/`](../../src/clause_tracer/core/), [`pyproject.toml`](../../pyproject.toml), [`scripts/check.sh`](../../scripts/check.sh) and [`.github/workflows/check.yml`](../../.github/workflows/check.yml).

## 4. Checks before starting

- [x] **The plan is Accepted.** Questions 1 to 18 in section 6 are answered (all on 14 Nov 2026). No task waits on an open question.
- [x] **The skeleton passes.** Run `.venv/bin/uv sync`, then `scripts/check.sh`. It must exit 0 before any change. Confirm that `core` holds only the files listed in section 2.
- [x] **Pydantic `TypeAdapter` builds frozen, slotted, keyword-only dataclasses** ([ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) action item 2, [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) "Check first"). Run it after S1-M1-T2 (Pydantic installed) and before S1-M1-T7 (the first enum). How:
  1. Write a throwaway test file in your scratch folder, outside the repo. Never commit it.
  2. In it, define `@dataclass(frozen=True, slots=True, kw_only=True)` classes that use every kind of field the shapes need: `int`, `str`, `bytes`, `bool`, `float`, `Decimal`, `datetime` (aware), a `NewType` over `str`, a `StrEnum`, `X | None`, `tuple[X, ...]`, `tuple[int | None, ...]`, a nested dataclass, a field with a default (`unlimited: bool = False`), a `Mapping[str, object]` field that `__post_init__` wraps in `MappingProxyType`, a field typed as a union of three dataclasses (like `Position.rule`), and a field typed as an empty base dataclass given a subclass instance (like `AiRequest.inputs: StepInputs`).
  3. Run `.venv/bin/uv run pytest <that file>`. Assert, for `TypeAdapter(...).validate_python(...)` and `validate_json(...)`: the result is an instance of the dataclass itself (not a Pydantic copy); assigning a field raises `FrozenInstanceError`; the instance has no `__dict__`; a JSON list becomes a tuple; a wrong type raises `ValidationError`; the union field becomes the right one of the three dataclasses for each input; `__post_init__` ran (the mapping is a `MappingProxyType`). Note what type comes back for the base-class field given a subclass, and for a JSON-loaded `Decimal` and `datetime`.
  4. Pass: write the Pydantic and Python versions and the result, including the base-class note, in this plan's change log, and tell the owner. Ticking the ADR's action item is the owner's call. The base-class note feeds the stage 6 question in [system design 15.6](../system-design.md#156-stage-6-the-encrypted-store-secrets-the-runner-and-the-first-commands).
  5. Fail, or any other surprise: **stop**. Bring it to the owner before any shape is written. A base-class field that comes back as the base class is not a failure: write it down.
- [x] **The docs are on `main`.** The `docs/` branch that holds this plan, the spec and the system design has been merged by its own pull request ([the README](README.md), "Branches and pull requests"). Milestone 1 is cut from that `main`.
- [x] **Remind the owner** to start writing the ten test contracts now, because they take longest ([system design 15.1](../system-design.md#151-stage-1-core)).

## 5. Milestones and tasks

Rules for every task:

- File names, class names, function names and signatures are fixed by this plan. Do not rename anything. If a name seems wrong, stop and ask the owner.
- Every shape is `@dataclass(frozen=True, slots=True, kw_only=True)` with exactly the fields of [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), in that order, and no more. Every enum is an `enum.StrEnum` whose member values are the member names in lower case. Shapes get no validation beyond the type (D4, I9). The one exception is `AiRequest.__post_init__` (S1-M2-T6).
- "Export" means: import the name in `src/clause_tracer/core/__init__.py` and add it to `__all__`, which stays sorted alphabetically. Other modules import only from `clause_tracer.core`, never from a file inside it (B2).
- Every task that adds a public name adds it to `src/clause_tracer/core/README.md` in the same commit, under the heading the task names (S3). The README headings are: "Ids and enums", "Errors", "Shapes", "Ports", "Fakes", "Functions", "Owner tables", "Run alone".
- Every datetime in `core` is timezone-aware. A function that takes a datetime raises `ValueError("datetime must be timezone-aware")` when given a naive one.
- Tests in `src/clause_tracer/core/tests/` have full type annotations (mypy strict). Use `-> None` on every test function.
- A task that reads an owner table never writes to that table. The owner-table guard (S1-M1-T5) fails a commit that changes code and an owner table together.
- "Done when" always includes: `scripts/check.sh` exits 0.

### M1: Foundations

The stage's tools are locked, coverage and the owner-table guard run in `scripts/check.sh`, the architecture tests guard `core`, and `from clause_tracer.core import Level, ClauseTracerError` works.

- [x] **S1-M1-T1: Add Hypothesis**
  - **Build:** Run `.venv/bin/uv add --dev hypothesis`. Commit `pyproject.toml` and `uv.lock` together, with the message `build(deps): add hypothesis for property tests`.
  - **Files:** `pyproject.toml`, `uv.lock`.
  - **Tests first:** None. This task adds a tool.
  - **Done when:** `.venv/bin/uv sync --locked` exits 0, `.venv/bin/uv run python -c "import hypothesis"` exits 0, and `scripts/check.sh` exits 0.
  - **Rules:** [Testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants), [ADR 0013](../adr/0013-test-layers-and-release-gates.md); AGENTS.md (commit `uv.lock`).
  - **Depends on:** None.

- [x] **S1-M1-T2: Add Pydantic as a runtime dependency**
  - **Build:** Run `.venv/bin/uv add pydantic`. It goes into `[project] dependencies`. Commit `pyproject.toml` and `uv.lock` together, with the message `build(deps): add pydantic for edge validation`. Nothing in `core` imports it. Then run the TypeAdapter check of section 4 and write its result in the change log (section 8) in the same commit.
  - **Files:** `pyproject.toml`, `uv.lock`, `docs/plans/stage-01-core.md` (change log).
  - **Tests first:** None. The check in section 4 runs right after the install.
  - **Done when:** `.venv/bin/uv sync --locked` exits 0, the TypeAdapter check result is in the change log, and `scripts/check.sh` exits 0.
  - **Rules:** [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) (amendment of 14 Nov 2026, action item 2), D4, I9.
  - **Depends on:** S1-M1-T1.

- [x] **S1-M1-T3: Measure branch coverage, with a 95% floor for `core`**
  - **Build:**
    1. Run `.venv/bin/uv add --dev coverage`.
    2. In `pyproject.toml` add:
       ```toml
       [tool.coverage.run]
       branch = true
       source = ["clause_tracer"]

       [tool.coverage.report]
       exclude_also = ["if __name__ == .__main__.:"]
       show_missing = true
       ```
    3. In `scripts/check.sh`, replace the line `run pytest -q` with two lines:
       ```bash
       run coverage run -m pytest -q
       run coverage report --include='src/clause_tracer/core/*' --fail-under=95
       ```
    4. Add `.coverage` to `.gitignore`.
  - **Files:** `pyproject.toml`, `uv.lock`, `scripts/check.sh`, `.gitignore`.
  - **Tests first:** None. Check by hand once: add a function with an untested `if` branch to a scratch copy of `core/__main__.py`, run `scripts/check.sh`, see the coverage step fail, then remove the change before the commit.
  - **Done when:** `scripts/check.sh` exits 0 and prints a coverage table with a `TOTAL` line for `core`; `git status` shows no `.coverage` file.
  - **Rules:** [Testing strategy 11](../testing-strategy.md#11-coverage-targets), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) amendment of 14 Nov 2026.
  - **Depends on:** S1-M1-T1.

- [x] **S1-M1-T4: The owner-table guard: its rules**
  - **Build:** A new script `scripts/check_owner_tables.py`, standard library only, with these functions. This task writes the pure part; S1-M1-T5 adds the git part.
    - `OWNER_TABLE_PATTERN = re.compile(r"(^|/)tests/tables/")` and `APPROVAL_LINE = "Owner-Approved-Tables: yes"`.
    - `def is_owner_table(path: str) -> bool`: true when `OWNER_TABLE_PATTERN.search(path)` matches. Paths use `/` and are relative to the repo root.
    - `def is_code(path: str) -> bool`: false when `is_owner_table(path)`; otherwise true when `path.endswith(".py")` or `path.startswith("scripts/")`.
    - `def change_fails(paths: Iterable[str]) -> bool`: true when at least one path is an owner table and at least one path is code.
    - `def is_approved(message: str) -> bool`: true when any line of `message`, stripped of spaces at both ends, equals `APPROVAL_LINE`.
  - **Files:** `scripts/check_owner_tables.py`, `tests/test_check_owner_tables.py`.
  - **Tests first:** in `tests/test_check_owner_tables.py`, which loads the script with `importlib.util.spec_from_file_location`:
    - `test_owner_table_paths`: `is_owner_table` is true for `src/clause_tracer/core/tests/tables/label_rules.toml` and `tests/tables/x.csv`; false for `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/samples/spec-14-5.toml` and `docs/tables/x.toml`.
    - `test_code_paths`: `is_code` is true for `src/clause_tracer/core/labels.py` and `scripts/check.sh`; false for `docs/plans/stage-01-core.md`, `uv.lock` and `src/clause_tracer/core/tests/tables/label_rules.toml`.
    - `test_change_fails_only_when_both`: `["a/tests/tables/t.toml", "src/x.py"]` fails; `["a/tests/tables/t.toml", "docs/plans/p.md"]` passes; `["src/x.py", "README.md"]` passes; `[]` passes.
    - `test_approval_line`: `"fix\n\nOwner-Approved-Tables: yes\n"` is approved; `"Owner-Approved-Tables: no"` and `"owner-approved-tables: yes"` are not.
  - **Done when:** `.venv/bin/uv run pytest tests/test_check_owner_tables.py` reports 4 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T11, [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) action item 2 and amendment of 14 Nov 2026.
  - **Depends on:** None.

- [x] **S1-M1-T5: The owner-table guard in `check.sh` and CI**
  - **Build:** In `scripts/check_owner_tables.py` add:
    - `def working_tree_paths(repo: Path) -> tuple[str, ...]`: the sorted, unique paths from `git diff --name-only HEAD` plus `git ls-files --others --exclude-standard`, run with `subprocess.run(..., cwd=repo, check=True, capture_output=True, text=True)`.
    - `def commit_paths(repo: Path, sha: str) -> tuple[str, ...]`: from `git diff-tree --no-commit-id --name-only -r <sha>`.
    - `def commits_since(repo: Path, base: str) -> tuple[str, ...]`: from `git rev-list --no-merges --reverse <base>..HEAD`.
    - `def commit_message(repo: Path, sha: str) -> str`: from `git log -1 --format=%B <sha>`.
    - `def main(argv: list[str] | None = None) -> int`: parses `--commits BASE` with `argparse`. With no argument it checks `working_tree_paths(Path.cwd())` as one change, and an approval line does not apply. With `--commits BASE` it checks each commit of `commits_since` on its own and skips a commit whose message `is_approved`. For each failing change it prints `owner-table guard: <change> edits code and an owner table: <table paths>` to standard error, where `<change>` is `working tree` or the short commit hash. It returns 1 if any change fails, else 0. End the file with `if __name__ == "__main__": raise SystemExit(main())`.
    - In `scripts/check.sh`, add `run python scripts/check_owner_tables.py` as the first `run` line, before `run ruff check`.
    - In `.github/workflows/check.yml`, set `fetch-depth: 0` on `actions/checkout@v7`, and add a last step:
      ```yaml
      - if: github.event_name == 'pull_request'
        run: uv run python scripts/check_owner_tables.py --commits origin/${{ github.base_ref }}
      ```
  - **Files:** `scripts/check_owner_tables.py`, `scripts/check.sh`, `.github/workflows/check.yml`, `tests/test_check_owner_tables.py`.
  - **Tests first:** in `tests/test_check_owner_tables.py`, each test makes a fresh repo in `tmp_path` with `git init`, sets `user.name` and `user.email` locally, and commits one file `README.md` as the base commit:
    - `test_working_tree_mixed_change_fails`: write `src/a.py` and `pkg/tests/tables/t.toml`, uncommitted; `main([])` run with that repo as the working directory returns 1.
    - `test_working_tree_tables_only_passes`: only `pkg/tests/tables/t.toml` changed; `main([])` returns 0.
    - `test_commits_checked_one_by_one`: commit `src/a.py` alone, then `pkg/tests/tables/t.toml` alone; `main(["--commits", <base sha>])` returns 0.
    - `test_mixed_commit_fails`: one commit with both files; `main(["--commits", <base sha>])` returns 1.
    - `test_approved_mixed_commit_passes`: the same commit with `Owner-Approved-Tables: yes` as the last line of its message; returns 0.
    Use `monkeypatch.chdir(repo)` to set the working directory.
  - **Done when:** `.venv/bin/uv run pytest tests/test_check_owner_tables.py` reports 9 passed; `scripts/check.sh` exits 0 on a clean tree; and, by hand once, `scripts/check.sh` exits 1 with a scratch change to both `src/clause_tracer/core/__main__.py` and a new `src/clause_tracer/core/tests/tables/x.toml` (remove both before the commit).
  - **Rules:** T11, I12 (exit codes), [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest).
  - **Depends on:** S1-M1-T4.

- [x] **S1-M1-T6: Architecture tests for `core`**
  - **Build:** Tests that guard the rules of `core` itself. They pass on the empty skeleton and keep passing as code is added.
  - **Files:** `src/clause_tracer/core/tests/test_architecture.py`.
  - **Tests first:**
    - `test_import_core_loads_only_stdlib`: runs `[sys.executable, "-c", "import sys, clause_tracer.core; print('\\n'.join(sorted(sys.modules)))"]` with `subprocess.run`, then asserts every printed module's top-level name (the part before the first `.`) is `clause_tracer` or is in `sys.stdlib_module_names`, or starts with `_`.
    - `test_public_dataclasses_are_frozen_slotted_keyword_only`: for every name in `clause_tracer.core.__all__` that is a dataclass class: `__dataclass_params__.frozen` is true, `"__slots__"` is in its `__dict__`, and every field has `kw_only` true.
    - `test_no_mutable_container_fields`: for those dataclasses, no field's type annotation string contains `list[`, `dict[` or `set[`.
    - `test_no_provider_specific_field_names`: for those dataclasses, no field name contains any of `openrouter`, `zdr`, `data_collection`, `require_parameters`, `response_format`, `provider_order`, `usage_cost`, `anthropic`, `openai`.
    - `test_enums_are_str_enums`: every `enum.Enum` subclass in `__all__` is a `StrEnum`, and each member's value equals `member.name.lower()`.
    Show each test failing once by a temporary bad change, exported from `core/__init__.py`: a line `import pydantic` (first test); a dataclass with `frozen=False` (second); a field typed `list[int]` (third); a field named `zdr` (fourth); a plain `Enum` (fifth). Remove every bad change before the commit.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_architecture.py` reports 5 passed, each was seen to fail for the right reason, and `scripts/check.sh` exits 0.
  - **Rules:** T9, T1, B3, [ADR 0015](../adr/0015-provider-ready-seam.md) action item 2, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md), [testing strategy 12](../testing-strategy.md#12-when-each-test-runs).
  - **Depends on:** None.

- [x] **S1-M1-T7: Ids, enums and constants**
  - **Build:**
    - `src/clause_tracer/core/ids.py`: the seven ids of system design 3.4, each `X = NewType("X", str)`.
    - `src/clause_tracer/core/enums.py`: the enums `Level`, `PositionType`, `Direction`, `Unit`, `Answer`, `ReasonCode`, `WrittenBy`, `ReviewStatus`, `PrivacyMode`, `FileKind`, `PlaceholderKind`, `SegmentKind`, `HiddenReason`, `PiiSource`, `TextSlot`, `ScanFinding`, `DrawFailure` and `PlaybookProblemCode`, with exactly the members of system design 3.4 in the listed order. Then `UNSURE_REASONS: frozenset[ReasonCode] = frozenset(ReasonCode) - {ReasonCode.RANGE, ReasonCode.CLAUSES_DISAGREE, ReasonCode.AMOUNT_PERCENT_DISAGREE}`, and `PLACEHOLDER_OPEN = "⟦"`, `PLACEHOLDER_CLOSE = "⟧"`.
    - Export every name.
  - **Files:** `src/clause_tracer/core/ids.py`, `src/clause_tracer/core/enums.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_enums.py`, `src/clause_tracer/core/README.md` ("Ids and enums").
  - **Tests first:** in `test_enums.py`:
    - `test_enum_members_match_system_design`: a dict in the test maps each enum to the tuple of member names copied from system design 3.4; `tuple(m.name for m in enum) ==` that tuple for every enum.
    - `test_unsure_reasons`: `ReasonCode` has 20 members, `UNSURE_REASONS` has 17 members, `UNLIMITED_UNCLEAR` is the last member of `ReasonCode` and is in `UNSURE_REASONS`, and `UNSURE_REASONS` holds neither `RANGE`, `CLAUSES_DISAGREE` nor `AMOUNT_PERCENT_DISAGREE`.
    - `test_ids_are_plain_str_at_run_time`: `type(PositionId("1")) is str`.
    - `test_placeholder_markers`: `PLACEHOLDER_OPEN == "⟦"` and `PLACEHOLDER_CLOSE == "⟧"`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_enums.py` reports 4 passed, `from clause_tracer.core import Level` works, and `scripts/check.sh` exits 0.
  - **Rules:** [System design 3.4](../system-design.md#34-core-shapes-for-stage-1), [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) action item 1, I7 (rules return codes, never prose), T1.
  - **Depends on:** S1-M1-T6, the TypeAdapter check.

- [x] **S1-M1-T8: The error tree**
  - **Build:** In `src/clause_tracer/core/errors.py`, the classes of [system design 3.4, "Errors"](../system-design.md#34-core-shapes-for-stage-1), exactly: the base, the four groups and the 20 leaf classes with their codes. The base:
    ```python
    class ClauseTracerError(Exception):
        code: ClassVar[str] = ""

        def __init__(self, context: Mapping[str, str | int] | None = None) -> None:
            super().__init__(self.code)
            self.context: Mapping[str, str | int] = MappingProxyType(dict(context or {}))
    ```
    Each leaf class sets only `code`, except `RateLimitedError`, which also carries the wait the AI service asked for:
    ```python
    class RateLimitedError(ModelServiceError):
        code: ClassVar[str] = "rate_limited"

        def __init__(
            self,
            context: Mapping[str, str | int] | None = None,
            *,
            retry_after_seconds: int | None = None,
        ) -> None:
            if retry_after_seconds is not None and retry_after_seconds < 0:
                raise ValueError("retry_after_seconds must be 0 or more")
            merged: dict[str, str | int] = dict(context or {})
            if retry_after_seconds is not None:
                merged["retry_after_seconds"] = retry_after_seconds
            super().__init__(merged)
            self.retry_after_seconds: int | None = retry_after_seconds
    ```
    Export every class.
  - **Files:** `src/clause_tracer/core/errors.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_errors.py`, `src/clause_tracer/core/README.md` ("Errors": a table of class, group, code, with a line on `retry_after_seconds`).
  - **Tests first:** in `test_errors.py`, with `LEAVES` a tuple of the 20 leaf classes written out in the test:
    - `test_every_leaf_is_in_exactly_one_group`: for each leaf, exactly one of `InputError`, `ModelServiceError`, `LocalError`, `ReviewCancelled` is a superclass (a class counts as its own superclass).
    - `test_codes_are_unique_lower_snake_case`: every leaf code matches `^[a-z][a-z0-9_]*$`, and the 20 codes are unique.
    - `test_codes_match_system_design`: a dict in the test copies each class's code from system design 3.4; each class's `code` equals it.
    - `test_context_is_read_only`: `ModelTimeoutError({"step": "match"}).context["step"] = "x"` raises `TypeError`.
    - `test_context_defaults_to_empty`: `ConfigError().context == {}`.
    - `test_message_is_the_code`: `str(NoCreditError()) == "no_credit"`.
    - `test_rate_limited_carries_the_wait_time`: `RateLimitedError({"step": "match"}, retry_after_seconds=30)` has `retry_after_seconds == 30`, `context["retry_after_seconds"] == 30` and `context["step"] == "match"`; with `retry_after_seconds=0` the wait is `0`, not `None`.
    - `test_rate_limited_without_wait_time`: `RateLimitedError()` has `retry_after_seconds is None` and `context == {}`; `str(RateLimitedError()) == "rate_limited"`.
    - `test_rate_limited_negative_wait_raises`: `RateLimitedError(retry_after_seconds=-1)` raises `ValueError` whose message is `retry_after_seconds must be 0 or more`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_errors.py` reports 9 passed, and `scripts/check.sh` exits 0.
  - **Rules:** I5, I6, I7, [system design 6.4](../system-design.md#64-errors), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md).
  - **Depends on:** S1-M1-T7.

- [x] **S1-M1-T9: The coverage floor omits `core`'s tests (temporary)**
  - **Build:** Done 16 Nov 2026, on the owner's decision in the working session. The line in `scripts/check.sh` that S1-M1-T3 added,
    `run coverage report --include='src/clause_tracer/core/*' --fail-under=95`,
    became
    `run coverage report --include='src/clause_tracer/core/*' --omit='src/clause_tracer/core/tests/*' --fail-under=95`,
    so the 95% floor measures `core`'s shipped code and not its test files. Reason: the architecture tests of S1-M1-T6 cannot fully execute their loops until the first shapes of S1-M2-T1 exist, so the floor as written failed although every test passed. The change is recorded in the change log (16 Nov 2026).
  - **Files:** `scripts/check.sh`, `docs/plans/stage-01-core.md` (change log).
  - **Tests first:** none. This task changes a check, not code.
  - **Done when:** `scripts/check.sh` exits 0. Met: commit `4fcc949`.
  - **Rules:** [Testing strategy 11](../testing-strategy.md#11-coverage-targets) (the floor is per package); plans README ("When the plan is wrong").
  - **Depends on:** S1-M1-T6.

### M2: Shapes

Every shape in system design 3.4 exists as a frozen, slotted, keyword-only dataclass, is exported from `clause_tracer.core`, and is listed in the core README.

Every task in M2 extends one shared test, `test_fields_match_system_design` in `src/clause_tracer/core/tests/test_shapes.py`. It holds a dict `EXPECTED_FIELDS: dict[type, tuple[str, ...]]` that maps each shape to its field names, copied in order from system design 3.4, and asserts `tuple(f.name for f in dataclasses.fields(shape)) == EXPECTED_FIELDS[shape]` for each entry (one `pytest.mark.parametrize` case per shape). Each task adds its shapes to the dict. Each task also adds its shapes to the README under "Shapes".

- [x] **S1-M2-T1: Wording and page-location shapes**
  - **Build:** In `src/clause_tracer/core/wording.py`: `Wording` and `Span`. In `src/clause_tracer/core/document.py`: `PageBox`, `Page` and `Glyph`. Each exactly as in system design 3.4, no more fields. In `src/clause_tracer/core/ports.py`: `CancelCheck = Callable[[], bool]` (a type alias, with a one-line docstring comment above it: `# Returns True once the user has cancelled.`). Export all six names.
  - **Files:** `src/clause_tracer/core/wording.py`, `src/clause_tracer/core/document.py`, `src/clause_tracer/core/ports.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** in `test_shapes.py`: `test_fields_match_system_design` (the five shapes); `test_wording_needs_written_by` (**promise test**, "every stored text keeps a written-by value", Spec 4.7 and 6.2): `Wording(text="x")` raises `TypeError`, and `dataclasses.fields(Wording)` shows `written_by` with no default; `test_shapes_need_keywords`: `Span(1, 2)` raises `TypeError`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, the architecture tests cover the new shapes, and `scripts/check.sh` exits 0.
  - **Rules:** [ADR 0016](../adr/0016-legal-positions-without-a-lawyer.md), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) and its 13 Nov amendment, T13, T1, S3.
  - **Depends on:** S1-M1-T7.

- [x] **S1-M2-T2: Document shapes**
  - **Build:** In `src/clause_tracer/core/document.py`: `SourceFile`, `HiddenText`, `TrackedChange`, `InputWarning`, `Document`, `MatchKey`, `Sentence` and `Clause`, each exactly as in system design 3.4, no more fields. Export all eight.
  - **Files:** `src/clause_tracer/core/document.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** `test_fields_match_system_design` (the eight shapes); `test_document_without_glyphs`: a `Document` with `text="Pay in 30 days."`, `char_map=()`, `glyphs=()`, `pages=()` builds; `test_span_counts_code_points`: for `text = "\U0001F600 fee"`, `text[Span(start=2, end=5).start:Span(start=2, end=5).end] == "fee"`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, and `scripts/check.sh` exits 0.
  - **Rules:** [System design 3.4 and 4.2](../system-design.md#42-the-offset-chain), D1, D6, S3.
  - **Depends on:** S1-M2-T1.

- [x] **S1-M2-T3: Link and placeholder shapes**
  - **Build:** In `src/clause_tracer/core/link_map.py`: `CrossReference`, `DefinedTerm`, `Override`, `OutsideDocument` and `LinkMap`. In `src/clause_tracer/core/placeholders.py`: `Party`, `PiiSuggestion`, `PlaceholderEntity`, `Segment` and `PlaceholderText`. Each exactly as in system design 3.4, no more fields. Export all ten.
  - **Files:** `src/clause_tracer/core/link_map.py`, `src/clause_tracer/core/placeholders.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** `test_fields_match_system_design` (the ten shapes); `test_unresolved_targets_are_kept`: `CrossReference(source=Span(start=0, end=4), target=None)` and `Override(clause_id=ClauseId("4"), target=None, overrides_target=True, evidence=Span(start=0, end=4))` build, and their `target` is `None`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, and `scripts/check.sh` exits 0.
  - **Rules:** [System design 3.4](../system-design.md#34-core-shapes-for-stage-1), [ADR 0008](../adr/0008-personal-data-detection-bundle.md), S3.
  - **Depends on:** S1-M2-T2.

- [x] **S1-M2-T4: Playbook and settings shapes**
  - **Build:** In `src/clause_tracer/core/playbook.py`: `NumberRule`, `YesNoRule`, `WordsRule`, `Position`, `Playbook` and `PlaybookSnapshot`. In `src/clause_tracer/core/settings.py`: `Settings`. Each exactly as in system design 3.4, no more fields. Export all seven.
  - **Files:** `src/clause_tracer/core/playbook.py`, `src/clause_tracer/core/settings.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** `test_fields_match_system_design` (the seven shapes); `test_playbook_text_is_plain_str`: the type hints (`typing.get_type_hints`) of `Playbook.name`, `Position.topic`, `YesNoRule.question` and the three `WordsRule` fields are `str`, not `Wording` (decided 13 Nov 2026).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, and `scripts/check.sh` exits 0.
  - **Rules:** [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 13 Nov amendment, [Spec 4.1](../spec.md#41-playbooks), I13, D6, S3.
  - **Depends on:** S1-M2-T1.

- [x] **S1-M2-T5: Review result shapes**
  - **Build:** In `src/clause_tracer/core/results.py`: `Evidence`, `CheckedValue` (with `unlimited: bool = False` as its last field), `JudgedLevel`, `MatchFound`, `NothingFound`, `MatchUnconfirmed`, `CallFailed`, `ToolLabel` and `NotCoveredClause`, each exactly as in system design 3.4, no more fields. Then the alias `MatchResult = MatchFound | NothingFound | MatchUnconfirmed | CallFailed`. Export all ten names.
  - **Files:** `src/clause_tracer/core/results.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** `test_fields_match_system_design` (the nine shapes); `test_match_results_are_unrelated`: for each ordered pair of the four match types, neither is a subclass of the other; `test_unlimited_defaults_to_false`: a `CheckedValue` built without `unlimited` has `unlimited is False`; `test_reason_fields_hold_reason_codes`: the type hint of `CheckedValue.reasons` and `ToolLabel.reasons` is `tuple[ReasonCode, ...]`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, and `scripts/check.sh` exits 0.
  - **Rules:** I4, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) and its 14 Nov amendment, [ADR 0002](../adr/0002-label-look-split-stamp.md), D5, S3.
  - **Depends on:** S1-M2-T2, S1-M2-T4.

- [x] **S1-M2-T6: AI request and record shapes**
  - **Build:** In `src/clause_tracer/core/ai.py`: `StepInputs` (no fields, docstring `"""Base class of every step's own input shape."""`), `PromptMessage`, `AiRequest`, `Usage`, `AiReply` and `AiRecord`, each exactly as in system design 3.4, no more fields. `AiRequest` gets:
    ```python
    def __post_init__(self) -> None:
        object.__setattr__(self, "json_schema", MappingProxyType(dict(self.json_schema)))
    ```
    Export all six. In `src/clause_tracer/core/tests/shapes_for_tests.py` (not exported), add the test-only step input shape `EchoInputs(StepInputs)` with fields `clause_id: ClauseId, text: str`, and a function `def make_request(**changes: object) -> AiRequest` that builds one fixed `AiRequest` (step `"echo"`, prompt id `"echo"`, prompt version 1, `EchoInputs(clause_id=ClauseId("4.2"), text="Pay in 30 days.")`, one `PromptMessage(role="user", text="Quote the clause.")`, schema id `"echo-reply"`, json schema `{"type": "object"}`, model `"test-model"`, `PrivacyMode.ON`, max tokens 200) and applies `dataclasses.replace(request, **changes)`.
  - **Files:** `src/clause_tracer/core/ai.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/shapes_for_tests.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** `test_fields_match_system_design` (the six shapes); `test_json_schema_is_read_only`: `make_request().json_schema["type"] = "array"` raises `TypeError`; `test_json_schema_is_copied`: a dict passed in and then changed leaves the request's `json_schema` unchanged; `test_record_has_schema_version`: `"schema_version"` is the second field of `AiRecord`. Check by hand once that `make_request(inputs={"a": 1})` written in a scratch file fails mypy, and do not commit that file.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, the architecture test finds no provider-specific field, and `scripts/check.sh` exits 0.
  - **Rules:** [ADR 0015](../adr/0015-provider-ready-seam.md) and its amendment, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 13 and 14 Nov amendments, [system design 6.3](../system-design.md#63-the-ai-request), D6, D8, S3.
  - **Depends on:** S1-M2-T1.

- [x] **S1-M2-T7: Shapes for the stage 1 functions**
  - **Build:** In `src/clause_tracer/core/results.py`: `UnreadableSpans`, `LabelInput` and `ValueVerdict`. In `src/clause_tracer/core/checks.py`: `ScanContext`, `QuoteFold`, `DrawAllowed`, `DrawRefused`, `CallPrices`, `CostInputs`, `CostRange` and `PlaybookProblem`. Each exactly as in the system design 3.4 table "Shapes for the stage 1 functions", no more fields. Export all eleven.
  - **Files:** `src/clause_tracer/core/results.py`, `src/clause_tracer/core/checks.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_shapes.py`, `src/clause_tracer/core/README.md`.
  - **Tests first:** `test_fields_match_system_design` (the eleven shapes); `test_draw_results_are_unrelated`: neither `DrawAllowed` nor `DrawRefused` is a subclass of the other.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_shapes.py` passes, and `scripts/check.sh` exits 0.
  - **Rules:** [System design 3.4](../system-design.md#34-core-shapes-for-stage-1) (14 Nov 2026), I3, I4, S3.
  - **Depends on:** S1-M2-T5.

- [x] **S1-M2-T8: Remove the coverage omit again**
  - **Build:** In `scripts/check.sh`, change the coverage report line back to what S1-M1-T3 wrote, so the 95% floor covers the test files of `core` again as the plan first had it:
    `run coverage report --include='src/clause_tracer/core/*' --fail-under=95`.
    This undoes S1-M1-T9, as the owner asked on 16 Nov 2026. Run it only once the shapes of S1-M2-T1 to S1-M2-T7 exist and every file in `src/clause_tracer/core/tests/` is fully executed by its own run, so the floor holds with the tests measured too. If the floor then still fails, stop and tell the owner; do not lower the floor, do not re-add the omit on your own.
  - **Files:** `scripts/check.sh`, `docs/plans/stage-01-core.md` (change log: a dated line saying the omit is gone).
  - **Tests first:** none. This task changes a check, not code.
  - **Done when:** `scripts/check.sh` exits 0 with no `--omit` in the coverage line, and `git grep -n "omit" scripts/check.sh` finds nothing.
  - **Rules:** [Testing strategy 11](../testing-strategy.md#11-coverage-targets); plans README ("When the plan is wrong").
  - **Depends on:** S1-M2-T7.

### M3: Playbook checks and label rules

Table-driven tests over the owner's tables pass for the playbook checks, for unit conversion, for Rules 1 to 10, and for every row of the Spec 14.5 sample.

**Owner tables.** They live in `src/clause_tracer/core/tests/tables/`. Each is a TOML file whose first line is exactly `# Expected answers. Only the owner edits this file. Constitution T11.` Each row is a `[[case]]` table with a unique string `id`. Numbers are written as TOML strings (`"15"`, `"7/30"` where a fraction is allowed) or integers, never as TOML floats. Enum values are written as their lower-case values (`"walk_away"`). A table-driven test reads its table through the loader of S1-M3-T1, builds the inputs, calls the function, and compares the result with the row. Each table also gets a test that fails when the table has no rows, so an empty table can never pass.

**Sample format.** The Spec 14.5 sample file (S1-M3-T5) and the label-rule table use one format for positions and inputs, read by `clause_tracer.core.sample_input` (S1-M3-T3 and T4).

- [x] **S1-M3-T1: The owner-table loader**
  - **Build:** In `src/clause_tracer/core/tests/owner_tables.py`:
    - `HEADER = "# Expected answers. Only the owner edits this file. Constitution T11."` and `TABLES_DIR = Path(__file__).parent / "tables"`.
    - `class OwnerTableError(ValueError)`.
    - `@dataclass(frozen=True, slots=True, kw_only=True) class OwnerTable` with fields `sections: Mapping[str, Mapping[str, object]]` and `cases: tuple[Mapping[str, object], ...]`.
    - `def load_table(path: Path, *, case_keys: frozenset[str], required: frozenset[str], sections: frozenset[str] = frozenset()) -> OwnerTable`. It raises `OwnerTableError` when: the first line is not `HEADER`; a top-level key is neither `case` nor in `sections`; a case has a key outside `case_keys`; a case lacks a key in `required`; a case's `id` is not a string; two cases share an `id`. A file with no `case` key has `cases == ()`. Every message starts with `f"{path.name}: "` and names the case id and key.
    - Converters, each `(value: object, where: str) -> X`, raising `OwnerTableError(f"{where}: …")`: `as_str` (a `str`), `as_bool` (a `bool`), `as_int` (an `int` that is not a `bool`), `as_decimal` (an `int`, or a `str` that `Decimal` parses; a `float` or `bool` raises), `as_fraction` (an `int`, or a `str` that `fractions.Fraction` parses), `as_datetime` (a `datetime` whose `tzinfo` is not `None`), `as_str_tuple` (a list of `str`), `as_enum(enum_type: type[E], value: object, where: str) -> E` (a `str` equal to a member's value), and `as_enum_tuple(enum_type, value, where) -> tuple[E, ...]`.
  - **Files:** `src/clause_tracer/core/tests/owner_tables.py`, `src/clause_tracer/core/tests/test_owner_tables.py`, `src/clause_tracer/core/tests/fixtures/owner_table_example.toml` (a test-only table with the header and two cases, `id = "a"` and `id = "b"`, each with `level = "walk_away"` and `limit = "15"`).
  - **Tests first:** in `test_owner_tables.py`: `test_reads_cases` (the fixture gives two cases with ids `a` and `b`); `test_missing_header_raises`; `test_unknown_top_level_key_raises`; `test_unknown_case_key_raises`; `test_missing_required_key_raises`; `test_duplicate_id_raises`; `test_header_only_file_has_no_cases`; `test_as_decimal` (`"1.5"` gives `Decimal("1.5")`, `15` gives `Decimal(15)`, `1.5` raises, `True` raises); `test_as_fraction` (`"7/30"` gives `Fraction(7, 30)`); `test_as_enum` (`"walk_away"` gives `Level.WALK_AWAY`, `"walk-away"` raises); `test_as_datetime_rejects_naive` (a naive `datetime` raises). Tests that need a bad file write it to `tmp_path`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_owner_tables.py` reports 11 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T11, [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) "Agent guard".
  - **Depends on:** S1-M1-T7.

- [x] **S1-M3-T2: Create the seven empty owner tables**
  - **Build:** Create these files, each holding exactly two lines: the `HEADER` line, then `# Format: docs/plans/stage-01-core.md, task <id>.` with the id of the owner task that fills it: `label_rules.toml` (S1-M3-T6), `units.toml` (S1-M3-T7), `spec_14_5.toml` (S1-M3-T8), `playbook_checks.toml` (S1-M3-T9), `auto_delete.toml` (S1-M4-T5), `scans.toml` (S1-M5-T1), `cost_estimate.toml` (S1-M5-T9). This commit holds these seven files and the plan tick, and no code, so the owner-table guard passes.
  - **Files:** the seven files in `src/clause_tracer/core/tests/tables/`.
  - **Tests first:** None. The loader test of S1-M3-T1 already covers a header-only file.
  - **Done when:** `.venv/bin/uv run python scripts/check_owner_tables.py` exits 0 before the commit, and `scripts/check.sh` exits 0.
  - **Rules:** T11.
  - **Depends on:** S1-M3-T1, S1-M1-T5.

- [x] **S1-M3-T3: Read positions and playbooks from the sample format**
  - **Build:** In `src/clause_tracer/core/sample_input.py` (not exported; only `__main__` and tests use it). Every error is `ValueError(f"{where}: …")` naming the key.
    - `def parse_position(data: Mapping[str, object], where: str) -> Position`. Keys: `id` (str, required), `topic` (str, required), `type` (`"number"`, `"yes_no"` or `"words"`, required), `why_note` (str, optional, default `None`). For `number`: `unit` (a `Unit` value), `direction` (a `Direction` value), `preferred_limit` and `acceptable_limit` (a TOML integer or a string `Decimal` parses), `missing_level` (a `Level` value), all required. For `yes_no`: `question`, `yes_level`, `no_level` required; `missing_level` optional, defaulting to the `no_level`. For `words`: `preferred`, `acceptable`, `walk_away` (str) and `missing_level`, all required. Any other key raises. A TOML float raises.
    - `def parse_playbook(data: Mapping[str, object], *, schema_version: int) -> Playbook`. Keys: `id`, `name`, `side` (str), `starter` (bool), `positions` (a list of position tables, read with `parse_position(..., where=f"position {i}")`). `customer_id` is `None`.
  - **Files:** `src/clause_tracer/core/sample_input.py`, `src/clause_tracer/core/tests/test_sample_input.py`.
  - **Tests first:** in `test_sample_input.py`, each test parses an inline TOML string with `tomllib.loads`: `test_number_position` (all fields map, limits are `Decimal`); `test_yes_no_missing_level_defaults_to_no_level`; `test_yes_no_missing_level_given_is_kept`; `test_words_position`; `test_unknown_key_raises` (the message contains the key); `test_float_limit_raises`; `test_playbook_fields` (id, name, side, starter, two positions in order, `customer_id is None`, `schema_version` as passed).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_sample_input.py` reports 7 passed, and `scripts/check.sh` exits 0.
  - **Rules:** S1 (sample input), D4, T1 (pure: it parses data already read; only `__main__` reads files).
  - **Depends on:** S1-M2-T4.

- [x] **S1-M3-T4: Read label inputs from the sample format**
  - **Build:** In `src/clause_tracer/core/sample_input.py`:
    - `def parse_label_inputs(entries: Sequence[Mapping[str, object]], playbook: Playbook) -> tuple[tuple[LabelInput, ...], UnreadableSpans]`. Each entry has keys `position` (str, required: a position id of `playbook`, or `ValueError`), `match` (`"found"`, `"nothing"`, `"unconfirmed"` or `"failed"`, required), `values` (list, default empty), `judged` (list, default empty), `clauses_to_read` (list of str, default empty), `outside_documents` (list of str, default empty).
    - A value table has keys `clause` (str, required), `raw`, `number`, `range_high`, `unit`, `start_point`, `answer` (an `Answer` value), `vague` (bool, default false), `amount`, `total`, `reasons` (list of `ReasonCode` values, default empty), `unlimited` (bool, default false), `quote` (`"confirmed"`, `"unplaced"` or `"none"`, default `"confirmed"`), `on` (`"visible"`, `"hidden"` or `"undecodable"`, default `"visible"`). It becomes a `CheckedValue` with `raw_value=raw`, `unit_as_written=unit`, `start_point_as_written=start_point`, `condition=None`, and the other fields by name.
    - A judged table has keys `clause` and `level` (required), `quote` and `on` (as above). It becomes a `JudgedLevel`.
    - Quote spans: a counter `k` starts at 0 for each call and goes up by 1 for each value and each judged table, in file order. The span is `Span(start=k * 100, end=k * 100 + 10)`. `quote = "none"` gives `evidence=None`; otherwise `Evidence(clause_id=clause, sentence_ids=(SentenceId(f"{clause}.s1"),), quote=span, placed=(quote == "confirmed"))`. `on = "hidden"` adds the span to `UnreadableSpans.hidden`; `on = "undecodable"` adds it to `UnreadableSpans.undecodable`.
    - The match: `found` gives `MatchFound(position_id, clause_ids=<the clause ids of values and judged, first-seen order, no repeats>)`; `nothing` gives `NothingFound(position_id, searches=())`; `unconfirmed` gives `MatchUnconfirmed(position_id, clauses_to_read=<clauses_to_read>)`; `failed` gives `CallFailed(code="model_reply_invalid")`.
    - Each outside document name becomes `OutsideDocument(name=name, evidence=Span(start=0, end=0))`.
    - `@dataclass(frozen=True, slots=True, kw_only=True) class Sample` with fields `playbook: Playbook, inputs: tuple[LabelInput, ...], unreadable: UnreadableSpans`, and `def parse_sample(data: Mapping[str, object]) -> Sample`, whose top-level keys are `schema_version` (int), `playbook` (table) and `input` (list of entries).
  - **Files:** `src/clause_tracer/core/sample_input.py`, `src/clause_tracer/core/tests/test_sample_input.py`.
  - **Tests first:** `test_found_value_builds_checked_value_and_evidence` (span `0..10`, sentence id `c1.s1`, `placed` true); `test_quote_none_has_no_evidence`; `test_unplaced_quote_has_placed_false`; `test_spans_count_across_entries` (the third value gets span `200..210`); `test_hidden_and_undecodable_spans_collected`; `test_match_kinds` (one entry of each of the four kinds gives the four types); `test_unknown_position_raises`; `test_judged_level`; `test_parse_sample_top_level`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_sample_input.py` reports 16 passed, and `scripts/check.sh` exits 0.
  - **Rules:** S1, D4, T1, I3.
  - **Depends on:** S1-M3-T3, S1-M2-T7.

- [x] **S1-M3-T5: The Spec 14.5 sample input file**
  - **Build:** `src/clause_tracer/core/samples/spec-14-5.toml`, with `schema_version = 1`. These are inputs, not expected labels.
    - `[playbook]`: `id = "starter-freelancer"`, `name = "Freelancer receiving a service agreement from the other side"`, `side = "service provider"`, `starter = true`, and one `[[playbook.positions]]` per row of Spec 7, in Spec 7 order, with `id` the row number (`"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"6"`, `"7a"`, `"7b"`, `"8"`, `"9"`, `"10"`) and `topic` the "Position" text of Spec 7 word for word. Yes/no positions use the topic as `question`. Number positions: 1 is days, lower is better, 15 and 30, missing `unsure`; 2 is percent, higher is better, 50 and 25, missing `walk_away`; 5 is rounds, lower is better, 2 and 3, missing `walk_away`; 9 is months, lower is better, 0 and 6, missing `preferred`. Yes/no positions: 3, 7b and 8 have yes `preferred`, no `acceptable`; 4, 6 and 7a have yes `preferred`, no `walk_away`. Position 10 is words, with the three level texts of Spec 7 word for word, missing `walk_away`. No `why_note` (Spec 7 does not give their text).
    - One `[[input]]` per position, in the same order: 1 `found`, value `clause = "c1"`, `number = "60"`, `unit = "days"`; 2 `found`, value `c2`, `"25"`, `unit = "%"`; 3 `nothing`; 4 `found`, value `c4`, `answer = "no"`, `quote = "none"`, `reasons = ["quote_not_confirmed"]`; 5 `found`, value `c5`, `raw = "reasonable revisions"`, `vague = true`; 6 `found`, value `c6`, `answer = "yes"`; 7a `found`, value `c7`, `answer = "no"`; 7b `nothing`; 8 `nothing`; 9 `found`, values `c9a` with `"12"` `months`, and `c9b` with `number = "6"`, `range_high = "9"`, `unit = "months"`; 10 `found`, judged `c10` with `level = "preferred"`, and `outside_documents = ["Master Agreement"]`.
    - Delete `src/clause_tracer/core/samples/.gitkeep`.
  - **Files:** `src/clause_tracer/core/samples/spec-14-5.toml`, `src/clause_tracer/core/samples/.gitkeep` (deleted), `src/clause_tracer/core/tests/test_sample_input.py`.
  - **Tests first:** `test_spec_14_5_sample_parses`: `parse_sample(tomllib.loads(<the file>))` gives 11 positions with the ids above in order, 11 inputs in the same order, and empty `UnreadableSpans`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_sample_input.py` reports 17 passed, and `scripts/check.sh` exits 0.
  - **Rules:** S1 (a sample input), D1, AGENTS.md (sample names from Spec 14.5 only), [Spec 7 and 14.5](../spec.md#145-sample-data).
  - **Depends on:** S1-M3-T4.

- [ ] **S1-M3-T6: Label-rule table (Owner)**
  - **Build:** Owner only. The rows of `label_rules.toml`. Columns: `id` (str), `rule` (one of `"rule1"`, `"rule2"`, `"rule3"`, `"rule4"`, `"rule5"`, `"rule6"`, `"rule7"`, `"rule9"`, `"rule10"`, `"edge"`; Rule 8 gives no label), `note` (str, optional), then one input in the sample format of S1-M3-T4 (`position` is a Spec 7 position id from the sample file; `match`; optional `values`, `judged`, `clauses_to_read`, `outside_documents`), then the expected answer: `level` (a `Level` value), `reasons` (a list of `ReasonCode` values; order does not matter), `written_by` (`"code"` or `"ai"`). Cases to cover, proposed, owner to check: Rule 1 at each limit and just past it, in both directions (positions 1 and 2), "none" as 0 (position 9), "unlimited" when lower is better (position 5: walk-away) and when higher is better (position 2: unsure, `unlimited_unclear`); Rule 2 yes, no, unclear, missing and conditional yes; Rule 3 quote not confirmed, number not in quote, and a confirmed quote that is not placed (label kept); Rule 4 a readable walk-away beside an unsure value, unsure beside acceptable, worst of preferred and acceptable, clauses that disagree; Rule 5 vague wording, another start point, unknown figures, business days; Rule 6 weeks, months and years each way, a range, a deposit amount with and without a total, an amount and a percentage that disagree; Rule 7 nothing found for each missing level, `MATCH_UNCONFIRMED`, and a failed call for a position whose missing level is preferred; Rule 9 hidden and undecodable text under a walk-away value; Rule 10 a walk-away that stays walk-away and an acceptable that becomes unsure; `edge` one row per item of question 16. The AI agent does not write or change it (T11). It may list, in chat, which Spec lines still have no row.
  - **Files:** `src/clause_tracer/core/tests/tables/label_rules.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 5](../spec.md#5-labelling-rules), [testing strategy 4 and 14](../testing-strategy.md#14-example-tests).
  - **Depends on:** S1-M3-T2, S1-M3-T5.

- [ ] **S1-M3-T7: Unit table (Owner)**
  - **Build:** Owner only. The rows of `units.toml`. Columns: `id` (str), `number` (a decimal string), `unit` (the unit as written, or absent for none), `target` (a `Unit` value), `expected` (a number as a string that `fractions.Fraction` reads, for example `"14"` or `"7/30"`, or the reason code value `"business_days"` or `"unit_unknown"`). Cases to cover, proposed, owner to check: every spelling in the list of S1-M3-T12 to each target it converts to; a week, a month and a year to days and to months; business days and working days; an unknown word; days to percent (no conversion); no unit (question 16a). The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/units.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 5](../spec.md#5-labelling-rules) Rule 6.
  - **Depends on:** S1-M3-T2.

- [ ] **S1-M3-T8: Spec 14.5 label table (Owner)**
  - **Build:** Owner only. One row per starter position in `spec_14_5.toml`. Columns: `id` (str), `position` (a Spec 7 position id), `level`, `reasons` (a list of `ReasonCode` values), `written_by` (`"code"` or `"ai"`). The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/spec_14_5.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the 11 rows and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 14.5](../spec.md#145-sample-data), [system design 15.1](../system-design.md#151-stage-1-core) "Done when".
  - **Depends on:** S1-M3-T5.

- [ ] **S1-M3-T9: Playbook-check table (Owner)**
  - **Build:** Owner only. The rows of `playbook_checks.toml`. Columns: `id` (str), `positions` (a list of position tables in the format of S1-M3-T3), `problems` (a list of inline tables `{ position = "<id>", code = "<PlaybookProblemCode value>" }`, empty when the playbook passes). Cases to cover, proposed, owner to check: a negative limit; a percentage over 100; equal limits and reversed limits, in both directions; yes level not better than no level; a yes/no level of unsure; a yes/no missing level that is not the no level; an empty words level text (`"   "`); two positions with one id; a playbook with no problem. The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/playbook_checks.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 4.1](../spec.md#41-playbooks).
  - **Depends on:** S1-M3-T2.

- [x] **S1-M3-T10: Level order, span overlap and reason order**
  - **Build:** In `src/clause_tracer/core/levels.py`, export each:
    - `def level_rank(level: Level) -> int`: `PREFERRED` 0, `ACCEPTABLE` 1, `WALK_AWAY` 2. `UNSURE` raises `ValueError("unsure has no rank")`.
    - `def is_better(a: Level, b: Level) -> bool`: `level_rank(a) < level_rank(b)`.
    - `def worst_level(levels: Iterable[Level]) -> Level`: the level with the highest rank; an empty input raises `ValueError`.
    - `def spans_overlap(a: Span, b: Span) -> bool`: `max(a.start, b.start) < min(a.end, b.end)` (true only when the spans share at least one code point; an empty span overlaps nothing).
    - `def unreadable_spans(document: Document) -> UnreadableSpans`: `hidden` is every `HiddenText.span` that is not `None`, in order; `undecodable` is `document.undecodable`.
    - `def sort_reasons(reasons: Iterable[ReasonCode]) -> tuple[ReasonCode, ...]`: no repeats, in `ReasonCode` member order.
  - **Files:** `src/clause_tracer/core/levels.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_levels.py`, `src/clause_tracer/core/tests/strategies.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_levels.py`: `test_level_rank`; `test_unsure_has_no_rank`; `test_is_better` (preferred over acceptable, acceptable over walk-away, not the reverse, not equal); `test_worst_level` (`[PREFERRED, ACCEPTABLE]` gives `ACCEPTABLE`; empty raises); `test_spans_overlap_examples` (`0..5` and `5..9` false; `0..5` and `4..9` true; `3..3` and `0..9` false); `test_unreadable_spans_skips_hidden_without_span`; `test_sort_reasons` (`[RANGE, HIDDEN_TEXT, RANGE]` gives `(RANGE, HIDDEN_TEXT)`); the property `test_spans_overlap_is_symmetric`, over `spans()` pairs. In `strategies.py`, add `def spans() -> SearchStrategy[Span]`: `start` from `integers(0, 200)`, length from `integers(0, 50)`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_levels.py` reports 8 passed, and `scripts/check.sh` exits 0.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 4, T1, T6.
  - **Depends on:** S1-M2-T7.

- [x] **S1-M3-T11: Playbook checks**
  - **Build:** In `src/clause_tracer/core/playbook_checks.py`, export `def check_playbook(playbook: Playbook) -> tuple[PlaybookProblem, ...]`. Problems come in playbook order; within one position, in `PlaybookProblemCode` member order. For each position:
    - `DUPLICATE_POSITION_ID` when an earlier position has the same id.
    - `RULE_TYPE_MISMATCH` when the rule's class does not match the type (`NUMBER` with `NumberRule`, `YES_NO` with `YesNoRule`, `WORDS` with `WordsRule`). Then skip the other checks for that position.
    - Number: `LIMIT_NEGATIVE` when either limit is below 0; `PERCENT_OVER_100` when the unit is `PERCENT` and either limit is above 100; `LIMITS_NOT_STRICTER` when, for `LOWER_IS_BETTER`, the preferred limit is not below the acceptable limit, or, for `HIGHER_IS_BETTER`, it is not above it.
    - Yes/no: `YES_NO_LEVEL_UNSURE` when either level is `UNSURE` (then skip `YES_NOT_BETTER`); `YES_NOT_BETTER` when `not is_better(yes_level, no_level)`; `MISSING_LEVEL_NOT_NO_LEVEL` when `missing_level != no_level`.
    - Words: `LEVEL_TEXT_EMPTY` when any of the three texts is empty after `strip()`.
  - **Files:** `src/clause_tracer/core/playbook_checks.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_playbook_checks.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_playbook_checks.py`: `test_playbook_checks_table`, one case per row of `playbook_checks.toml` (load with `load_table`, case keys `{"id", "positions", "problems"}`, all required; build the positions with `parse_position`; build `Playbook(id=PlaybookId("test"), schema_version=1, name="Test", side="test", customer_id=None, positions=…, starter=False)`; compare `set(check_playbook(playbook))` with the set of expected `PlaybookProblem`s); `test_playbook_checks_table_has_rows`; `test_starter_playbook_passes` (the playbook of the Spec 14.5 sample gives `()`); `test_rule_type_mismatch` (a `NUMBER` position holding a `WordsRule` gives exactly one problem, `RULE_TYPE_MISMATCH`).
  - **Done when:** every row passes, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 4.1](../spec.md#41-playbooks), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 14 Nov amendment, T1, T11, I4.
  - **Depends on:** S1-M3-T9, S1-M3-T10.

- [x] **S1-M3-T12: Unit conversion (Rule 6)**
  - **Build:** In `src/clause_tracer/core/units.py`, export `def convert_to_unit(number: Decimal, unit_as_written: str | None, target: Unit) -> Fraction | ReasonCode`.
    - `None` means the number is already in the target unit: return `Fraction(number)` (question 16a).
    - Otherwise normalise the spelling: lower case, strip spaces at both ends, collapse runs of spaces to one, drop one trailing `.`. Then look it up:
      - `day`, `days`, `calendar day`, `calendar days`: days. `week`, `weeks`: weeks. `month`, `months`: months. `year`, `years`: years.
      - `%`, `percent`, `per cent`: percent. `round`, `rounds`, `revision`, `revisions`, `round of revisions`, `rounds of revisions`: rounds.
      - `business day`, `business days`, `working day`, `working days`: return `ReasonCode.BUSINESS_DAYS`.
      - Anything else: return `ReasonCode.UNIT_UNKNOWN`.
    - Factors, applied as `Fraction(number) * factor`: to `DAYS`, a day is 1, a week 7, a month 30, a year 365. To `MONTHS`, a month is 1, a year 12, a day `Fraction(1, 30)`, a week `Fraction(7, 30)`. To `PERCENT`, percent is 1. To `ROUNDS`, rounds is 1. Any other pair returns `ReasonCode.UNIT_UNKNOWN`.
  - **Files:** `src/clause_tracer/core/units.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_units.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_units.py`: `test_units_table`, one case per row of `units.toml` (case keys `{"id", "number", "unit", "target", "expected"}`, required all but `unit`; `expected` is a `ReasonCode` value or else read with `as_fraction`; compare for equality); `test_units_table_has_rows`; the property `test_days_and_months_round_trip`: for any `Decimal` from `decimals(min_value=0, max_value=10_000, places=2)`, `convert_to_unit(n, "months", Unit.DAYS) == Fraction(n) * 30` and `convert_to_unit(n, "days", Unit.MONTHS) * 30 == Fraction(n)`.
  - **Done when:** every row passes, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 6, T1, T6, T11.
  - **Depends on:** S1-M3-T7.

- [x] **S1-M3-T13: Number values (Rules 1, 3, 5, 6 and 9)**
  - **Build:** In `src/clause_tracer/core/labels.py`, export:
    - `def evidence_reasons(evidence: Evidence | None, unreadable: UnreadableSpans) -> tuple[ReasonCode, ...]`: `QUOTE_NOT_CONFIRMED` when `evidence` is `None` (question 16b); otherwise `HIDDEN_TEXT` when `evidence.quote` overlaps any hidden span, and `UNDECODABLE_TEXT` when it overlaps any undecodable span. Sorted with `sort_reasons`. `evidence.placed` never matters (Rule 3: an unplaced quote keeps its label).
    - `def level_for_limits(rule: NumberRule, number: Fraction) -> Level`: for `LOWER_IS_BETTER`, `PREFERRED` when `number <= preferred_limit`, else `ACCEPTABLE` when `number <= acceptable_limit`, else `WALK_AWAY`; for `HIGHER_IS_BETTER` the same with `>=`.
    - `def number_verdicts(rule: NumberRule, value: CheckedValue, unreadable: UnreadableSpans) -> tuple[ValueVerdict, ...]`, in this order:
      1. `reasons` = `value.reasons` plus `evidence_reasons(value.evidence, unreadable)`. Add `VAGUE_WORDING` when `value.vague`.
      2. Numbers: take the first case that fits.
         - `value.unlimited`: when `rule.direction` is `HIGHER_IS_BETTER`, add `UNLIMITED_UNCLEAR` (Rule 1, decided 14 Nov 2026). The value has no numbers.
         - `rule.unit` is `PERCENT` and `value.amount` is not `None`: when `value.total` is `None` or not above 0, add `AMOUNT_WITHOUT_TOTAL`, and the value has no numbers. Otherwise the computed percentage is `Fraction(amount) / Fraction(total) * 100`. When `value.number` is `None`, the computed percentage is the one number. When `value.number` is given, convert it with `convert_to_unit(value.number, value.unit_as_written, rule.unit)`. A `ReasonCode` result is added to `reasons`, and the computed percentage is the one number. Otherwise, when the converted value and the computed percentage, each rounded half up to a whole number (`math.floor(x + Fraction(1, 2))`), differ, add `AMOUNT_PERCENT_DISAGREE`, and the numbers are the computed percentage then the converted value. When they match, the computed percentage is the one number (question 16e).
         - `value.number` is not `None`: convert it with `convert_to_unit(value.number, value.unit_as_written, rule.unit)`; a `ReasonCode` result is added to `reasons` and the value has no numbers, otherwise it is the first number. If `value.range_high` is not `None`, convert it the same way, add it as a second number when it converted, and add `RANGE`.
         - Otherwise: add `NO_VALUE` when `reasons` holds nothing from `UNSURE_REASONS` yet (question 16c).
      3. If `reasons` holds anything from `UNSURE_REASONS`: return one verdict with `level=UNSURE`, `readable_value=None`.
      4. If `value.unlimited` (so `rule.direction` is `LOWER_IS_BETTER`, because step 3 caught the other direction): return one verdict with `level=WALK_AWAY`, `readable_value="unlimited"` (Rule 1: unlimited is the worst value when lower is better).
      5. Otherwise one verdict per number, in order: `level=level_for_limits(rule, n)`, `readable_value=str(n)`.
      Every verdict has `clause_id=value.clause_id`, `evidence=value.evidence`, `reasons=sort_reasons(reasons)`.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_labels.py`, with `PAYMENT_DAYS = NumberRule(unit=DAYS, direction=LOWER_IS_BETTER, preferred_limit=Decimal(15), acceptable_limit=Decimal(30))`, `DEPOSIT_PERCENT = NumberRule(unit=PERCENT, direction=HIGHER_IS_BETTER, preferred_limit=Decimal(50), acceptable_limit=Decimal(25))` and a helper `def value(**changes: object) -> CheckedValue` that builds a confirmed 60-day value on clause `c1` with quote `Span(start=0, end=10)`:
    - `test_hidden_quote_makes_value_unsure` (**promise test**, "values resting on hidden text are unsure", Spec 11): with hidden span `5..8`, one verdict, `UNSURE`, reasons `(HIDDEN_TEXT,)`, `readable_value is None`.
    - `test_undecodable_quote_makes_value_unsure`.
    - `test_quote_touching_hidden_at_its_end_is_readable`: hidden span `10..12` gives a verdict that is not `UNSURE`.
    - `test_unplaced_quote_keeps_its_level`: `placed=False` gives the same level as `placed=True`.
    - `test_missing_quote_is_unsure`: `evidence=None` gives `UNSURE` with `QUOTE_NOT_CONFIRMED`.
    - `test_reason_on_value_makes_it_unsure`: `reasons=(OTHER_START_POINT,)` gives `UNSURE` (Rule 5, decided 14 Nov 2026).
    - `test_range_gives_two_verdicts`: `number=6, range_high=9` gives two verdicts, both with `RANGE`.
    - `test_unlimited_is_walk_away_when_lower_is_better`: with `PAYMENT_DAYS`, `unlimited=True` gives one verdict, `WALK_AWAY`, `readable_value == "unlimited"`, `reasons == ()`.
    - `test_unlimited_is_unsure_when_higher_is_better`: with `DEPOSIT_PERCENT`, `unlimited=True` gives one verdict, `UNSURE`, `readable_value is None`, `reasons == (UNLIMITED_UNCLEAR,)`.
    - `test_business_days_are_unsure`: `unit_as_written="business days"` gives `UNSURE` with `BUSINESS_DAYS`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_labels.py` reports 10 passed, and `scripts/check.sh` exits 0.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) (the "never guess" principle, Rules 1, 3, 5, 6, 9); I3, I4, T1, T13.
  - **Depends on:** S1-M3-T10, S1-M3-T12.

- [x] **S1-M3-T14: Yes/no and words values (Rules 2 and 9)**
  - **Build:** In `src/clause_tracer/core/labels.py`, export:
    - `def yes_no_verdict(rule: YesNoRule, value: CheckedValue, unreadable: UnreadableSpans) -> ValueVerdict`: `reasons` = `value.reasons` plus `evidence_reasons(...)`. When `value.answer` is `None`, add `NO_VALUE` if `reasons` holds nothing from `UNSURE_REASONS`. When it is `CONDITIONAL_YES`, add `CONDITIONAL_YES`. If `reasons` holds anything from `UNSURE_REASONS`: `level=UNSURE`, `readable_value=None`. Else `YES` gives `rule.yes_level`, and `NO`, `UNCLEAR` and `MISSING` give `rule.no_level`; `readable_value=value.answer.value`.
    - `def words_verdict(judged: JudgedLevel, unreadable: UnreadableSpans) -> ValueVerdict`: `reasons = evidence_reasons(judged.evidence, unreadable)`; add `JUDGED_UNSURE` when `judged.level` is `UNSURE` (question 16d). If `reasons` holds anything from `UNSURE_REASONS`: `level=UNSURE`, `readable_value=None`. Else `level=judged.level`, `readable_value=judged.level.value`.
    Both set `clause_id` and `evidence` from their input, and `reasons=sort_reasons(reasons)`.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** with `PAID_IF_CANCELLED = YesNoRule(question="Paid if cancelled", yes_level=PREFERRED, no_level=WALK_AWAY)`: `test_yes_gives_yes_level`; `test_no_unclear_and_missing_give_no_level` (all three give `WALK_AWAY`); `test_conditional_yes_is_unsure` (reasons hold `CONDITIONAL_YES`); `test_hidden_yes_is_unsure`; `test_judged_level_is_kept`; `test_judged_unsure_has_a_reason`; `test_hidden_judged_level_is_unsure`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_labels.py` reports 17 passed, and `scripts/check.sh` exits 0.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rules 2 and 9, T1.
  - **Depends on:** S1-M3-T13.

- [x] **S1-M3-T15: Combining values (Rule 4)**
  - **Build:** In `src/clause_tracer/core/labels.py`, export `def combine_rule_4(verdicts: tuple[ValueVerdict, ...]) -> tuple[Level, tuple[ReasonCode, ...]]`:
    - An empty tuple raises `ValueError("no values to combine")`.
    - Level: `WALK_AWAY` if any verdict is `WALK_AWAY` (a verdict that is not `UNSURE` is readable); else `UNSURE` if any verdict is `UNSURE`; else `worst_level` of all.
    - Disagreement (question 16f): for each clause id, take its verdicts whose `readable_value` is not `None`, and make the key `"|".join(sorted(set(<their readable values>)))`. Clauses with no readable verdict have no key. When there are two or more different keys, add `CLAUSES_DISAGREE`.
    - Reasons: `sort_reasons` of every verdict's reasons, plus `CLAUSES_DISAGREE` when added (question 16g: reasons of every value are kept at every level).
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/tests/strategies.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `strategies.py` add `def value_verdicts() -> SearchStrategy[ValueVerdict]`: `clause_id` from `sampled_from(["c1", "c2", "c3"])`; `level` from `sampled_from(Level)`; for `UNSURE`, `reasons` is a list of 1 to 3 codes from `sorted(UNSURE_REASONS)` and `readable_value` is `None`; otherwise `reasons` is a list of 0 to 2 codes from `[RANGE, CLAUSES_DISAGREE]` and `readable_value` from `sampled_from(["5", "10", "30"])`; `evidence` is `None`. In `test_labels.py`: the property `test_order_never_changes_the_result` (a list of 1 to 6 verdicts and any permutation of it give the same result); the property `test_readable_walk_away_wins` (**promise test**, part of "every planted walk-away gets walk-away", Spec 11: any list holding a `WALK_AWAY` verdict gives `WALK_AWAY`); the property `test_unsure_always_has_a_reason` (an `UNSURE` result has at least one code from `UNSURE_REASONS`); `test_empty_raises`; `test_clauses_that_disagree` (`c1` "12" and `c2` "6", "9" give `CLAUSES_DISAGREE`); `test_same_value_in_two_clauses_agrees` (`c1` "30" and `c2` "30"); `test_range_in_one_clause_agrees` (`c1` "6" and `c1` "9" only).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_labels.py` reports 24 passed, and `scripts/check.sh` exits 0.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rule 4, T1, T6, T13, I4.
  - **Depends on:** S1-M3-T14.

- [ ] **S1-M3-T16: One label per position (Rules 7 and 10)**
  - **Build:** In `src/clause_tracer/core/labels.py`, export `def label_position(item: LabelInput, unreadable: UnreadableSpans) -> ToolLabel`:
    1. Raise `ValueError` when: the match is not a `CallFailed` and its `position_id` differs from `item.position.id`; any value or judged level has another `position_id`; the rule's class does not match the position type; a `WORDS` position has `values`; a `NUMBER` or `YES_NO` position has `judged`.
    2. `CallFailed`: `level=UNSURE`, `reasons=(REPLY_BROKEN_TWICE,)`, `evidence=()`, `written_by=CODE`.
    3. `NothingFound`: `level` is `rule.no_level` for `YES_NO` (Spec 4.1) and `position.missing_level` otherwise; `reasons=()`, `evidence=()`, `written_by=CODE`.
    4. `MatchUnconfirmed`: `level=UNSURE`, `reasons=(MATCH_UNCONFIRMED,)`, `evidence=()`, `written_by=CODE`.
    5. `MatchFound`: the verdicts are `number_verdicts` of each value (joined in order), `yes_no_verdict` of each value, or `words_verdict` of each judged level. No verdict: `level=UNSURE`, `reasons=(NO_VALUE,)`, `written_by=CODE`. Otherwise `level, reasons = combine_rule_4(verdicts)`; `written_by` is set in step 7. `evidence` is every verdict's evidence that is not `None`, in order, without repeats.
    6. Rule 10: when `item.outside_documents` is not empty, the level becomes `UNSURE` and `UNLOADED_DOCUMENT` joins the reasons, unless the level came from step 5 and is `WALK_AWAY` (Rule 4 step 1). That walk-away keeps its level and its reasons unchanged. A `NothingFound` label whose missing level is `WALK_AWAY` came from step 3, so it does become `UNSURE` (question 16h).
    7. `written_by`: `AI` only when all three hold: the position type is `WORDS`, the match is a `MatchFound`, and the final level after step 6 is `PREFERRED`, `ACCEPTABLE` or `WALK_AWAY`. In every other case it is `CODE`. So a words label that a rule turned `UNSURE` (the AI answered unsure, a quote failed, hidden text, an unloaded document) is written by code, and only a level the AI actually judged is drawn in pencil (question 16i, ADR 0002).
    `position_id=item.position.id`; reasons always pass through `sort_reasons`.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/tests/label_cases.py`, `src/clause_tracer/core/tests/strategies.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:**
    - In `label_cases.py`: `@dataclass(frozen=True, slots=True, kw_only=True) class LabelCase` with `id: str, rule: str, label_input: LabelInput, unreadable: UnreadableSpans, level: Level, reasons: frozenset[ReasonCode], written_by: WrittenBy`, and `def label_rule_cases() -> tuple[LabelCase, ...]`: loads `label_rules.toml` with `load_table` (case keys `id, rule, note, position, match, values, judged, clauses_to_read, outside_documents, level, reasons, written_by`; required `id, rule, position, match, level, reasons, written_by`), reads the starter playbook from `samples/spec-14-5.toml` with `parse_sample`, and builds each case's input with `parse_label_inputs([<the case's input keys>], playbook)`.
    - In `strategies.py`: `def positions() -> SearchStrategy[Position]`: id `"p"` plus `integers(0, 99)`; type from `sampled_from(PositionType)`; a `NumberRule` with unit from `sampled_from(Unit)`, direction from `sampled_from(Direction)` and two limits from `decimals(0, 100, places=0)` ordered so the preferred limit is stricter; a `YesNoRule` with question `"q"`, yes and no levels from `[PREFERRED, ACCEPTABLE, WALK_AWAY]`; a `WordsRule` with texts `"a"`, `"b"`, `"c"`; `missing_level` from `sampled_from(Level)`; topic `"t"`; `why_note=None`.
    - In `test_labels.py`: `test_label_rules_table`, one case per `label_rule_cases()` row (compare `level`, `frozenset(reasons)`, `written_by`); `test_every_rule_has_rows` (each of `rule1`, `rule2`, `rule3`, `rule4`, `rule5`, `rule6`, `rule7`, `rule9`, `rule10` has a row); the property `test_failed_call_never_gives_a_missing_level` (any `positions()` with `CallFailed` gives `UNSURE`: system design 8.2); `test_words_label_is_written_by_ai`; `test_missing_words_label_is_written_by_code`; `test_rule_10_keeps_a_walk_away` (a found walk-away value plus one outside document: level `WALK_AWAY`, no `UNLOADED_DOCUMENT`); `test_rule_10_makes_a_missing_walk_away_unsure`; `test_words_label_turned_unsure_is_written_by_code` (a `WORDS` position with one judged level and one outside document gives `UNSURE` with `written_by=CODE`); `test_judged_words_label_is_written_by_ai` (the same position with no outside document and a judged `ACCEPTABLE` gives `written_by=AI`) (`NothingFound` on a position whose missing level is `WALK_AWAY`, plus one outside document: level `UNSURE`, reasons `(UNLOADED_DOCUMENT,)`); `test_position_mismatch_raises`.
  - **Done when:** every row of `label_rules.toml` passes, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** [Spec 5](../spec.md#5-labelling-rules) Rules 3, 4, 7 and 10, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) and its 14 Nov amendment, [ADR 0002](../adr/0002-label-look-split-stamp.md), I4, [system design 8.2](../system-design.md#82-calls-to-the-ai-service), T11.
  - **Depends on:** S1-M3-T6, S1-M3-T14, S1-M3-T15.

- [ ] **S1-M3-T17: Every position of a playbook, and the Spec 14.5 sample**
  - **Build:** In `src/clause_tracer/core/labels.py`, export `def label_all(playbook: Playbook, inputs: tuple[LabelInput, ...], unreadable: UnreadableSpans) -> tuple[ToolLabel, ...]`. It raises `ValueError` when a position has no input, when two inputs name one position, or when an input names a position not in the playbook. It returns `label_position` of each position's input, in playbook order.
  - **Files:** `src/clause_tracer/core/labels.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_spec_14_5.py`, `src/clause_tracer/core/tests/test_labels.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_spec_14_5.py`: `test_spec_14_5_sample`, one case per row of `spec_14_5.toml` (case keys `id, position, level, reasons, written_by`, all required): the label of that position from `label_all` on the sample file matches `level`, `frozenset(reasons)` and `written_by`; `test_spec_14_5_table_covers_every_position` (the table's positions are exactly the 11 sample ids). In `test_labels.py`: the property `test_no_position_is_dropped` (Spec 5 Rule 3: for a list of 1 to 6 `positions()` with unique ids, each given a `NothingFound` input, `label_all` returns one label per position, with the ids in playbook order); `test_missing_input_raises`; `test_duplicate_input_raises`.
  - **Done when:** every Spec 14.5 row passes, `scripts/check.sh` exits 0, and the owner tables are unchanged in the commit.
  - **Rules:** [Spec 5 and 14.5](../spec.md#145-sample-data), [system design 15.1](../system-design.md#151-stage-1-core) "Done when", T11, T13, B5.
  - **Depends on:** S1-M3-T8, S1-M3-T16.

### M4: Ports, the request hash, fakes and auto-delete

Any later module can be tested against a fake of each port. The replay fake fails on a request it does not know, the contract suites in `tests/contracts/` pass against each fake, and a fixed clock drives auto-delete.

- [ ] **S1-M4-T1: The five ports**
  - **Build:** In `src/clause_tracer/core/ports.py`, beside `CancelCheck`: `AiClient`, `PiiDetector`, `ReviewStore`, `SecretStore` and `Clock` as `typing.Protocol` classes, with exactly the method signatures of system design 3.4 ("Ports"), each method body `...`. Each method has a docstring of four lines: `Input: …`, `Output: …`, `Raises: …`, `Side effects: …`, filled from the "Notes" column of that table (write `None.` where a line does not apply). Export all five.
  - **Files:** `src/clause_tracer/core/ports.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_ports.py`, `src/clause_tracer/core/README.md` ("Ports").
  - **Tests first:** in `test_ports.py`: `test_ports_have_exactly_the_system_design_methods` (for each port, the set of names in its `__dict__` that do not start with `_` equals the method names of 3.4); `test_stubs_satisfy_the_ports`: one small stub class per port with the right methods, each assigned to a variable annotated with the port type (`client: AiClient = _StubAiClient()`), so mypy strict checks them. Check by hand once that a stub whose `complete` takes `str` fails mypy, and do not commit it.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_ports.py` reports 2 passed, and `scripts/check.sh` exits 0.
  - **Rules:** P4, T2, B3, I11, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 14 Nov amendment, [ADR 0015](../adr/0015-provider-ready-seam.md), [system design 3.1](../system-design.md#31-the-engine).
  - **Depends on:** S1-M1-T8, S1-M2-T3, S1-M2-T6.

- [ ] **S1-M4-T2: Pure hash of the exact request**
  - **Build:** In `src/clause_tracer/core/request_hash.py`, export:
    - `def to_plain(value: object) -> object`, checked in this order: `None`, `bool`, `int`, `float` stay as they are; an `Enum` member becomes its `value`; a `str` stays; a `Decimal` becomes `str(value)`; a `datetime` becomes `value.isoformat()`; `bytes` become `base64.b64encode(value).decode("ascii")`; a `tuple` or `list` becomes a list of `to_plain` of each item; a `Mapping` becomes a dict of `to_plain` of each value (a key that is not a `str` raises `TypeError`); a dataclass instance becomes `{"__type__": type(value).__qualname__, <field name>: to_plain(<field value>) for each field}`; anything else raises `TypeError(f"cannot hash {type(value).__name__}")`.
    - `def request_sha256(request: AiRequest) -> str`: `hashlib.sha256(json.dumps(to_plain(request), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()`.
  - **Files:** `src/clause_tracer/core/request_hash.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_request_hash.py`, `src/clause_tracer/core/README.md` ("Functions", with the encoding written out).
  - **Tests first:** in `test_request_hash.py`, using `make_request` from `shapes_for_tests.py`: `test_same_request_same_hash`; `test_hash_is_64_lowercase_hex`; `test_hash_ignores_hash_seed` (run `python -c` printing `request_sha256(make_request())` in two subprocesses with `PYTHONHASHSEED` `0` and `1`; both equal the in-process hash); `test_each_field_changes_the_hash`, one case per field with these changes: `step="echo2"`, `prompt_id="echo2"`, `prompt_version=2`, `inputs=EchoInputs(clause_id=ClauseId("4.2"), text="Pay in 31 days.")`, `messages=(PromptMessage(role="user", text="Quote it."),)`, `schema_id="echo-reply-2"`, `json_schema={"type": "array"}`, `model="test-model-2"`, `privacy_mode=PrivacyMode.OFF`, `max_tokens=201`; `test_json_schema_key_order_is_ignored` (`{"a": 1, "b": 2}` and `{"b": 2, "a": 1}`); `test_unknown_type_raises` (`to_plain({1, 2})` raises `TypeError`); the property `test_rebuilt_copy_has_the_same_hash` (for any `text()` used as the inputs' text, two requests built separately from it hash the same).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_request_hash.py` reports 16 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, D8, [ADR 0013](../adr/0013-test-layers-and-release-gates.md) 13 Nov amendment, [system design 7](../system-design.md#7-caching-resume-and-cost).
  - **Depends on:** S1-M2-T6.

- [ ] **S1-M4-T3: The replay fake**
  - **Build:** In `src/clause_tracer/core/fakes.py` (standard library and `core` only), export:
    - `class UnrecordedRequest(AssertionError)`. It is a test failure, not a project error, so code under test that catches `ClauseTracerError` cannot swallow it.
    - `class ReplayAiClient` with `def __init__(self, recordings: Mapping[str, AiReply]) -> None` (keys are `request_sha256` values; the client keeps a copy); `def complete(self, request: AiRequest) -> AiReply`; `def unused_keys(self) -> tuple[str, ...]` (sorted keys never asked for); `def fail_next(self, error_type: type[ModelServiceError]) -> None`. `complete` first checks a pending failure: if one is set, it clears it and raises `error_type({"step": request.step})`. Then it hashes the request; a miss raises `UnrecordedRequest(f"unrecorded request: step={request.step} sha256={key}")`; a hit marks the key used and returns the reply. A recording may be asked for more than once.
    - `def assert_all_used(client: ReplayAiClient) -> None`: raises `AssertionError(f"unused recordings: {client.unused_keys()}")` when any key is unused.
    In `src/clause_tracer/core/tests/conftest.py`, add the fixture `make_replay_client`: it yields a function `(recordings: Mapping[str, AiReply]) -> ReplayAiClient` and, after the test, calls `assert_all_used` on every client it made.
  - **Files:** `src/clause_tracer/core/fakes.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/conftest.py`, `src/clause_tracer/core/tests/test_replay_fake.py`, `src/clause_tracer/core/tests/shapes_for_tests.py` (add `def make_reply(text: str = "{}") -> AiReply` with `raw_body=text.encode()`, `model_used="test-model"`, `provider_used="test-provider"`, `Usage(input_tokens=10, cached_input_tokens=0, output_tokens=5, cost_usd=None)`, `generation_id="gen-1"`), `src/clause_tracer/core/README.md` ("Fakes").
  - **Tests first:** in `test_replay_fake.py`: `test_recorded_request_returns_its_reply`; `test_one_character_change_raises` (a request whose message text differs by one character raises `UnrecordedRequest`; the message contains `step=echo` and the hash, and not `Quote the clause`); `test_unused_recording_is_reported`; `test_assert_all_used_raises_on_unused`; `test_fail_next_raises_once` (`fail_next(ModelTimeoutError)`: the next call raises `ModelTimeoutError` with `context["step"] == "echo"`, the call after returns the reply); `test_fixture_client_works` (uses `make_replay_client` with one recording that the test asks for); `test_replay_fake_is_an_ai_client` (`client: AiClient = ReplayAiClient({})`, checked by mypy).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_replay_fake.py` reports 7 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T3, T7, T12, T1, [ADR 0013](../adr/0013-test-layers-and-release-gates.md) action item 1 and amendments, [testing strategy 6.1](../testing-strategy.md#61-the-replay-fake).
  - **Depends on:** S1-M4-T1, S1-M4-T2.

- [ ] **S1-M4-T4: Fake detector, secret store and clock, with the first contract suite**
  - **Build:** In `src/clause_tracer/core/fakes.py`, export:
    - `class FakePiiDetector` with `def __init__(self, planted: Mapping[str, tuple[PiiSuggestion, ...]]) -> None` and `def find(self, text: str) -> tuple[PiiSuggestion, ...]`, which returns `planted[text]`, or `()` for a text not planted.
    - `class InMemorySecretStore` with `def __init__(self, *, available: bool = True) -> None`, `def set_available(self, available: bool) -> None`, and the three `SecretStore` methods. When not available, each of the three raises `SecretStoreUnavailableError({"provider_id": provider_id})`. `delete_secret` of a missing id does nothing (I8).
    - `class FixedClock` with `def __init__(self, now: datetime) -> None`, `def now(self) -> datetime`, `def set(self, when: datetime) -> None` and `def advance(self, delta: timedelta) -> None` (a negative `delta` moves it back). A naive datetime raises `ValueError("datetime must be timezone-aware")`.
    Create `tests/contracts/__init__.py` (empty) and `tests/contracts/test_secret_store_contract.py` with a fixture `secret_store` (`params=["in_memory"]`, returning `InMemorySecretStore()`) and a fixture `unavailable_secret_store` (`params=["in_memory"]`, returning `InMemorySecretStore(available=False)`), so stage 6 adds the real adapter as a new param.
  - **Files:** `src/clause_tracer/core/fakes.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_fakes.py`, `tests/contracts/__init__.py`, `tests/contracts/test_secret_store_contract.py`, `tests/README.md` (add: "`contracts/`: one behaviour suite per port, run against each fake now and each real adapter from stage 6"), `src/clause_tracer/core/README.md` ("Fakes").
  - **Tests first:** in `test_secret_store_contract.py`: `test_put_then_get`; `test_get_missing_is_none`; `test_put_twice_keeps_the_last`; `test_delete_missing_succeeds`; `test_delete_then_get_is_none`; `test_unavailable_store_raises` (each of the three methods raises `SecretStoreUnavailableError`). In `test_fakes.py`: `test_detector_returns_planted_suggestions`; `test_detector_returns_nothing_for_other_text`; `test_clock_returns_its_time`; `test_clock_moves_forward_and_back`; `test_clock_rejects_naive_datetime`; `test_fakes_satisfy_their_ports` (each assigned to a variable annotated with its port, checked by mypy).
  - **Done when:** `.venv/bin/uv run pytest tests/contracts src/clause_tracer/core/tests/test_fakes.py` reports 12 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T3, T2, I8, [ADR 0006](../adr/0006-encrypted-storage-and-secrets.md), [ADR 0015](../adr/0015-provider-ready-seam.md) (credentials under a provider id), [testing strategy 3](../testing-strategy.md#3-five-layers).
  - **Depends on:** S1-M4-T1.

- [ ] **S1-M4-T5: Auto-delete table (Owner)**
  - **Build:** Owner only. The rows of `auto_delete.toml`. Columns: `id` (str); `last_change`, `now` (TOML offset datetimes, written like `2026-11-01T09:00:00Z`); `days` (7, 30 or 90); `protected_until` (an offset datetime, optional: the end of the 3-day grace after the setting was lowered); and the expected answers `due_at` (offset datetime), `due` (bool), `warning` (bool). Cases to cover, proposed, owner to check: "now" exactly at the due date, and one second before it; each of 7, 30 and 90 days; "Keep it" (a later `last_change`); the warning at exactly 3 days before, and one second more than 3 days before; a lowered setting whose new date falls inside the grace; a laptop off for months; a clock that jumped backwards, so "now" is before `last_change` (Spec 9: not due). The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/auto_delete.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 9](../spec.md#9-running-the-app) (auto-delete), [testing strategy 8](../testing-strategy.md#8-privacy-and-security-tests) (auto-delete row).
  - **Depends on:** S1-M3-T2.

- [ ] **S1-M4-T6: Auto-delete date rules**
  - **Build:** In `src/clause_tracer/core/auto_delete.py`, export `WARNING_WINDOW = timedelta(days=3)`, `LOWERING_GRACE = timedelta(days=3)` and these pure functions. None reads a clock. Each raises `ValueError("datetime must be timezone-aware")` for a naive datetime and `ValueError("days must be 1 or more")` when `days < 1`.
    - `def due_at(last_change: datetime, days: int, protected_until: datetime | None = None) -> datetime`: `last_change + timedelta(days=days)`, or `protected_until` when that is later.
    - `def is_due(last_change: datetime, days: int, now: datetime, protected_until: datetime | None = None) -> bool`: `now >= due_at(...)`. A clock behind `last_change` is therefore never due (Spec 9, decided 14 Nov 2026).
    - `def in_warning_window(last_change: datetime, days: int, now: datetime, protected_until: datetime | None = None) -> bool`: `due_at(...) - WARNING_WINDOW <= now < due_at(...)`.
    - `def protected_until_after_lowering(lowered_at: datetime) -> datetime`: `lowered_at + LOWERING_GRACE`.
  - **Files:** `src/clause_tracer/core/auto_delete.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_auto_delete.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_auto_delete.py`: `test_auto_delete_table`, one case per row (case keys `id, last_change, days, now, protected_until, due_at, due, warning`; all required but `protected_until`; compare `due_at`, `is_due` and `in_warning_window` with the row); `test_auto_delete_table_has_rows`; the property `test_due_exactly_when_now_reaches_the_due_date` (**promise test**, "auto-delete runs on schedule", Spec 11, unit part; aware datetimes from `datetimes(timezones=just(timezone.utc))`, days from `sampled_from([7, 30, 90])`); the property `test_never_due_before_the_rule_allows` (`is_due` is false whenever `now < last_change + timedelta(days=days)` or `now < protected_until`); `test_naive_datetime_raises`; `test_days_below_one_raises`.
  - **Done when:** every row passes, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T1, T2, T13, T11, [Spec 9](../spec.md#9-running-the-app).
  - **Depends on:** S1-M4-T5.

- [ ] **S1-M4-T7: In-memory review store, with its contract suite**
  - **Build:** In `src/clause_tracer/core/fakes.py`, export `class InMemoryReviewStore` with `def __init__(self) -> None` and the five `ReviewStore` methods of system design 3.4:
    - `save_record` raises `DuplicateRecordError({"record_id": record.record_id})` when any review already holds that `record_id`.
    - `load_records` returns the review's records in the order saved, or `()`.
    - `list_reviews` returns the sorted ids of reviews that hold at least one record.
    - `delete_review` removes the review and its records; a missing review does nothing (I8).
    - `purge_expired(now, auto_delete_days)`: for each review, its last change is the latest `finished_at` of its records (the stage 1 stand-in, system design 3.4); it deletes each review for which `is_due(last_change, auto_delete_days, now)` is true, and returns their ids, sorted.
    Create `tests/contracts/test_review_store_contract.py` with a fixture `review_store` (`params=["in_memory"]`, returning `InMemoryReviewStore()`). In `src/clause_tracer/core/tests/shapes_for_tests.py` add `def make_record(record_id: str, review_id: str, finished_at: datetime) -> AiRecord` (`schema_version=1`, step `"echo"`, attempt 1, the hash and request of `make_request()`, `reply=make_reply()`, `error_code=None`, `started_at=finished_at - timedelta(seconds=1)`).
  - **Files:** `src/clause_tracer/core/fakes.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/shapes_for_tests.py`, `tests/contracts/test_review_store_contract.py`, `src/clause_tracer/core/README.md` ("Fakes").
  - **Tests first:** in `test_review_store_contract.py`: `test_saved_record_loads_back_equal`; `test_records_load_in_save_order`; `test_duplicate_record_id_raises`; `test_unknown_review_has_no_records`; `test_list_reviews_is_sorted`; `test_delete_review_twice_succeeds`; `test_delete_removes_the_records`; `test_purge_removes_only_due_reviews` (two reviews, last changes 31 and 29 days before "now", setting 30: only the first goes); `test_purge_with_nothing_due_returns_empty`; `test_purge_with_clock_behind_removes_nothing` ("now" before every `finished_at`).
  - **Done when:** `.venv/bin/uv run pytest tests/contracts/test_review_store_contract.py` reports 10 passed, `review: ReviewStore = InMemoryReviewStore()` type-checks, and `scripts/check.sh` exits 0.
  - **Rules:** T3, I4, I8, D1, D8, [ADR 0006](../adr/0006-encrypted-storage-and-secrets.md), [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) 14 Nov amendment.
  - **Depends on:** S1-M4-T3, S1-M4-T6.

### M5: Scans, the cost estimate and the last check before drawing

The output scans give the owner's findings for every case in the scan table, the cost estimate gives the owner's ranges, and the last check before drawing passes invariant 7.

- [ ] **S1-M5-T1: Scan table (Owner)**
  - **Build:** Owner only. `scans.toml` holds two sections and the cases.
    - `[lists]`: `law_words`, `advice_phrases`, `injection_phrases`, `contact_words`, `first_person_words`, `filler_phrases`, `evaluative_words`, `abbreviations`, each a list of strings. Proposed starting values, owner to check: law words `"legal"`, `"illegal"`, `"lawful"`, `"unlawful"`, `"enforceable"`, `"unenforceable"`, `"the law"`; advice `"safe to sign"`, `"you should sign"`, `"do not sign"`, `"don't sign"`, `"we recommend"`; injection tells `"ignore"`, `"disregard"`, `"mark every"`, `"system prompt"`; contact words `"call"`, `"visit"`; first-person words `"I"`, `"I'm"`, `"I'd"`, `"I'll"`, `"I've"`, `"we"`, `"we're"`, `"we'd"`, `"we'll"`, `"we've"`, `"my"`, `"our"`; filler phrases `"certainly"`, `"here is"`, `"here's"`, `"I hope"`, `"it's important to note"`, `"please note"`, `"overall"`, `"in summary"`, `"as an AI"`, `"feel free"`, `"rest assured"`, `"crucial"`, `"ensure that"`; evaluative words `"fair"`, `"unfair"`, `"concerning"`, `"problematic"`, `"favourable"`, `"standard"`, `"typical"`, `"risky"`; abbreviations (each ends in `.`) `"e.g."`, `"i.e."`, `"etc."`, `"approx."`, `"no."`, `"cl."`, `"mr."`, `"mrs."`, `"ms."`, `"dr."`, `"vs."`. Write apostrophes straight: the scans make curly ones straight before they match.
    - `[caps]`: one integer per `TextSlot` value (`reason`, `reading`, `question`, `message`, `rewrite`), the maximum length in characters. Proposed starting values, owner to check: reason 280, reading 200, question 200, message 3000, rewrite 2000.
    - `[[case]]` columns: `id`, `text`, `slot` (a `TextSlot` value), `label` (a `Level` value, optional), `allowed_numbers`, `acceptable_limits` (lists of decimal strings, default empty), `known_placeholders`, `defined_roles` (lists of strings, default empty), `personal_data` (a list of substrings of `text` that the fake detector reports as a person, default empty), `clause_numbers` (a list of strings, default empty), `quote` (a string, optional: the quote the text rests on), `source_text` (a string, optional: the template message or the clause a rewrite starts from), `instruction_given` (a bool, default false), and the expected `findings` (a list of `ScanFinding` values, empty when the text passes). Each row lists every finding the full scan gives, so a row with digits lists them in `allowed_numbers` unless it expects `number_not_allowed`, and a `message` or `rewrite` row gives a `source_text` unless it expects `added_sentence`.
    Cases to cover, proposed, owner to check: "Dear John" (with `John` as personal data); a web address, with and without `https://`; an email address; "safe to sign"; "call" and "visit"; each law word, and an innocent look-alike ("legally" if it is not listed, "the lawn"); an acceptable limit, also when the same number is allowed; a wrong label word; an invented number; a number inside a known placeholder (passes); an unknown placeholder; a defined role ("the Contractor") reported by the detector (passes); text one character over each cap, and text exactly at the cap; the items of question 17.
    The style scans of [Spec 6.2](../spec.md#62-rules-for-every-ai-step) (decided 14 Nov 2026), proposed rows, owner to check, at least one passing and one failing case each:
      - `first_person`. Fails: `reason` "I think 5.4 is vague." (clause numbers `5.4`); `rewrite` "We’ll pay within 30 days." from source "The Client pays within 30 days." (a curly apostrophe). Passes: `message` "Before I sign, could we look at a few points?" with that same sentence as source (the user speaks); `question` "Can we agree that 2 rounds of revisions are included?" (the user sends it, question 18a); `rewrite` "We pay within 15 days." from source "We pay within 30 days." (the word is in the source, question 18b); `reading` "The fee, i.e. the deposit, is due on signing." (an abbreviation, not "I").
      - `filler_phrase`. Fails: `reason` "Certainly! 5.4 says 60 days." (clause numbers `5.4`: the phrase and the exclamation mark give one finding); `reading` "Overall, 5.4 favours the other side.". Passes: `reading` "5.4 says 60 days."; `rewrite` "The Contractor shall ensure that work is delivered on time." from source "The Contractor shall ensure that work is delivered." (question 18b).
      - `evaluative_word`. Fails: `reason` "Clause 5.4 is unfair." (clause numbers `5.4`); `reading` "This is a standard clause.". Passes: `reason` "“Fair price” has no number." with quote "at a fair price" (question 18b); `reading` "5.4 is worded fairly broadly." (whole words only).
      - `no_anchor`. Fails: `reason` "The wording is vague." (quote "within a reasonable time", clause numbers `5.4`); `reason` "“the” has no number." (fewer than four letters); `reason` "“prompt” payment is not defined." (not in the quote); `reason` "5.40 sets no deadline." (clause numbers `5.4`); `reason` "“Reasonable” has no number." with no quote and no clause numbers. Passes: `reason` "5.4 sets no deadline." (clause numbers `5.4`); `reason` "Read 5.4." (clause numbers `5.4`); `reading` "The wording is vague." (only reasons are checked).
      - `added_sentence`. Fails: `message` "Thanks for sending the agreement. Before I sign, could we look at a few points? That would help me plan the work." from source "Thanks for sending the agreement. Before I sign, could we look at a few points?"; `rewrite` "The Client pays within 30 days. Late payment carries interest." from source "The Client pays within 30 days." with no instruction; a `message` with no source. Passes: the same `rewrite` with `instruction_given = true`; a `message` with fewer sentences than its source; a `message` "Thanks, e.g. for the draft. Could we talk?" from a two-sentence source (an abbreviation does not end a sentence).
      - The "Keep" strings of [ux-copy 1.1](../ux-copy.md#11-signs-of-machine-made-text), word for word: "“Reasonable” has no number, so it can't be checked against your limit." in `reason` with quote "within a reasonable time"; the other six in `reading`, with `label = "walk_away"` and allowed numbers `60` and `30` for "This one is a walk-away. You'd wait 60 days to be paid; your limit is 30." Each gives none of the five style findings. "It doesn't mean it's safe to sign." still gives `advice` from the advice list.
    The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/scans.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the lists, caps and cases and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 6.2](../spec.md#62-rules-for-every-ai-step) (with the length caps and the style scans), [testing strategy 4](../testing-strategy.md#4-what-to-test-in-each-module) (`core` row), question 18.
  - **Depends on:** S1-M3-T2.

- [ ] **S1-M5-T2: The scan lists and caps in code**
  - **Build:** In `src/clause_tracer/core/scan_rules.py`, export `LAW_WORDS`, `ADVICE_PHRASES`, `INJECTION_PHRASES`, `CONTACT_WORDS`, `FIRST_PERSON_WORDS`, `FILLER_PHRASES`, `EVALUATIVE_WORDS`, `ABBREVIATIONS` (each `tuple[str, ...]`, from the lists `law_words` to `abbreviations` in that order) and `LENGTH_CAPS: Mapping[TextSlot, int]` (a `MappingProxyType`), with the values copied from the owner's `scans.toml` in the same order. The owner owns the values; the code holds a copy.
  - **Files:** `src/clause_tracer/core/scan_rules.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_scans.py`: `test_scan_rules_match_owner_table` (load `scans.toml` with `sections=frozenset({"lists", "caps"})`; each list equals its tuple; the caps equal `LENGTH_CAPS`, with one entry per `TextSlot`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_scans.py` reports 1 passed, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T11, [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) (decided 14 Nov 2026: the owner's table holds the values).
  - **Depends on:** S1-M5-T1, S1-M1-T7.

- [ ] **S1-M5-T3: Word and pattern scans**
  - **Build:** In `src/clause_tracer/core/scans.py`, export:
    - `WEB_ADDRESS_PATTERN = re.compile(r"\bhttps?://\S+|\bwww\.\S+|\b(?:[a-z0-9-]+\.)+(?:com|org|net|io|co|uk|eu|info|biz|dev|app|me|ai)\b", re.IGNORECASE)` and `EMAIL_PATTERN = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")`.
    - `LABEL_WORDS: Mapping[Level, tuple[str, ...]]`: `PREFERRED` `("preferred",)`, `ACCEPTABLE` `("acceptable",)`, `WALK_AWAY` `("walk-away", "walk away")`, `UNSURE` `("unsure",)`.
    - `def contains_phrase(text: str, phrase: str) -> bool`: first replace `‘` and `’` in `text` with `'`; then `re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE) is not None` (question 17a).
    - `def scan_text(text: str, slot: TextSlot, label: Level | None) -> tuple[ScanFinding, ...]`: `TOO_LONG` when `len(text) > LENGTH_CAPS[slot]`; `LAW_WORD`, `ADVICE`, `INJECTION_TELL`, `CONTACT_WORD` when `contains_phrase` is true for any item of the matching list; `WEB_ADDRESS` when `WEB_ADDRESS_PATTERN` finds a match; `EMAIL_ADDRESS` when `EMAIL_PATTERN` finds a match; `WRONG_LABEL_WORD` when `label` is not `None` and any word of another level in `LABEL_WORDS` is present by `contains_phrase` (question 17d). Findings in `ScanFinding` member order, no repeats.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_scans.py`, with `TEXT_FINDINGS = frozenset({TOO_LONG, LAW_WORD, ADVICE, INJECTION_TELL, CONTACT_WORD, WEB_ADDRESS, EMAIL_ADDRESS, WRONG_LABEL_WORD})`: `test_text_scans_table`, one case per row of `scans.toml` (case keys as in S1-M5-T1; required `id, text, slot, findings`): `set(scan_text(text, slot, label)) == set(findings) & TEXT_FINDINGS`; `test_scans_table_has_rows`; `test_every_law_word_fails_in_any_case` (**promise test**, "no AI text states what a law allows", Spec 11: one test function that loops over each item of `LAW_WORDS`, in lower case, upper case and title case, inside `"This is {word} here."`; each gives `LAW_WORD`); `test_curly_apostrophe_is_folded` (`"don’t sign"` matches `"don't sign"`).
  - **Done when:** every row of `scans.toml` passes `test_text_scans_table`, `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_scans.py -k "not scans_table"` reports 3 passed, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T1, T13, T11, I4, [Spec 6.2](../spec.md#62-rules-for-every-ai-step), [system design 8.2](../system-design.md#82-calls-to-the-ai-service).
  - **Depends on:** S1-M5-T2.

- [ ] **S1-M5-T4: The quote-check fold**
  - **Build:** In `src/clause_tracer/core/quote_fold.py`, export `def fold_for_quote_check(text: str) -> QuoteFold`, the fold of Spec 2. Walk the text once: `‘ ’ ‚ ‛` (`‘ ’ ‚ ‛`) become `'`; `“ ” „ ‟` (`“ ” „ ‟`) become `"`; a run of characters for which `str.isspace()` is true becomes one `" "`, mapped to the run's first character; every other character is kept. `to_original[i]` is the index in `text` of folded character `i`, and the last entry is `len(text)`.
  - **Files:** `src/clause_tracer/core/quote_fold.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_quote_fold.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_quote_fold.py`: `test_curly_quotes_become_straight` (`"“a” ‘b’"` folds to `"\"a\" 'b'"`); `test_whitespace_runs_collapse` (`"a \n\t b"` folds to `"a b"` with `to_original == (0, 1, 5, 6)`); `test_empty_text` (`QuoteFold(text="", to_original=(0,))`); the property `test_map_shape` (for `text()`: `len(to_original) == len(text) + 1`, it is strictly increasing, and its last entry is the original length); the property `test_fold_is_idempotent` (folding the folded text gives the same text).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_quote_fold.py` reports 5 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, T6, [Spec 2](../spec.md#2-glossary) (quote check), [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) 14 Nov amendment.
  - **Depends on:** S1-M2-T7.

- [ ] **S1-M5-T5: Style scans: first-person, filler and evaluative words**
  - **Build:** In `src/clause_tracer/core/scans.py`, export:
    - `FIRST_PERSON_SLOTS: frozenset[TextSlot] = frozenset({TextSlot.REASON, TextSlot.READING, TextSlot.REWRITE})`. The message and the question to ask are left out, because the user speaks in them (question 18a).
    - `def mask_abbreviations(text: str) -> str`: for each item `a` of `ABBREVIATIONS`, replace every match of `re.compile(r"(?<![\w.])" + re.escape(a), re.IGNORECASE)` in `text` with `" " * len(a)`. The result has the same length as `text`.
    - `def scan_style(text: str, slot: TextSlot, context: ScanContext) -> tuple[ScanFinding, ...]`. Let `source` be `context.source_text` when `slot` is `MESSAGE` or `REWRITE`, and `context.quote` for every other slot. A listed item `w` is *added* when `contains_phrase(text, w)` is true and it is not the case that `source` is not `None` and `contains_phrase(source, w)` is true (question 18b). Then:
      - `FIRST_PERSON` when `slot` is in `FIRST_PERSON_SLOTS` and an item of `FIRST_PERSON_WORDS` is added, with both `text` and `source` passed through `mask_abbreviations` first (so "i.e." is not "I").
      - `FILLER_PHRASE` when an item of `FILLER_PHRASES` is added, or when `"!"` is in `text` and `source` is `None` or does not hold `"!"`.
      - `EVALUATIVE_WORD` when an item of `EVALUATIVE_WORDS` is added.
      Findings in `ScanFinding` member order, no repeats. S1-M5-T6 and S1-M5-T7 add `NO_ANCHOR` and `ADDED_SENTENCE` to this function.
    - In `src/clause_tracer/core/tests/shapes_for_tests.py`, add `def make_scan_context(**changes: object) -> ScanContext`: `ScanContext(label=None, allowed_numbers=(), acceptable_limits=(), known_placeholders=(), defined_roles=(), clause_numbers=(), quote=None, source_text=None, instruction_given=False)` with `dataclasses.replace(context, **changes)`.
    - In `src/clause_tracer/core/tests/scan_cases.py` (not exported): `@dataclass(frozen=True, slots=True, kw_only=True) class ScanCase` with `id: str, text: str, slot: TextSlot, context: ScanContext, personal_data: tuple[str, ...], findings: frozenset[ScanFinding]`; `SCAN_CASE_KEYS = frozenset({"id", "text", "slot", "label", "allowed_numbers", "acceptable_limits", "known_placeholders", "defined_roles", "personal_data", "clause_numbers", "quote", "source_text", "instruction_given", "findings"})`; and `def scan_cases() -> tuple[ScanCase, ...]`, which loads `scans.toml` with `load_table(TABLES_DIR / "scans.toml", case_keys=SCAN_CASE_KEYS, required=frozenset({"id", "text", "slot", "findings"}), sections=frozenset({"lists", "caps"}))` and builds each case: `slot` and `label` with `as_enum` (`label` `None` when absent); `allowed_numbers` and `acceptable_limits` as `tuple(as_decimal(v, where) for v in as_str_tuple(value, where))`; the other lists with `as_str_tuple`; `quote` and `source_text` with `as_str`, `None` when absent; `instruction_given` with `as_bool`, `False` when absent; `findings` as `frozenset(as_enum_tuple(ScanFinding, value, where))`. Absent lists are `()`.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/tests/scan_cases.py`, `src/clause_tracer/core/tests/shapes_for_tests.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_scans.py`, with `WORD_STYLE_FINDINGS = frozenset({FIRST_PERSON, FILLER_PHRASE, EVALUATIVE_WORD})` and `make_scan_context()` unless a change is named:
    - `test_style_word_scans_table`, one case per `scan_cases()` row: `set(scan_style(case.text, case.slot, case.context)) & WORD_STYLE_FINDINGS == case.findings & WORD_STYLE_FINDINGS`.
    - `test_mask_abbreviations_keeps_length`: `mask_abbreviations("Pay e.g. now.") == "Pay " + " " * 4 + " now."`; `mask_abbreviations("See info.") == "See info."`.
    - `test_first_person_fails_outside_the_message`: one test function that loops over the slots. `"I'd flag this."` gives a result holding `FIRST_PERSON` in `REASON`, `READING` and `REWRITE`, and not holding it in `MESSAGE` and `QUESTION`.
    - `test_curly_contraction_is_first_person`: `"We’ll check 5.4."` in `READING` holds `FIRST_PERSON`.
    - `test_abbreviation_is_not_first_person`: `"The fee, i.e. the deposit, is due."` in `READING` does not hold `FIRST_PERSON`.
    - `test_word_in_source_is_allowed`: `"We shall ensure that the work is fair."` in `REWRITE` with `source_text="We shall ensure that the work is fair and on time."` holds nothing from `WORD_STYLE_FINDINGS`.
    - `test_word_not_in_source_fails`: `"We shall pay."` in `REWRITE` with `source_text="The Client shall pay."` holds `FIRST_PERSON`.
    - `test_exclamation_mark_is_filler`: in `READING`, `"5.4 says 60 days!"` holds `FILLER_PHRASE` and `"5.4 says 60 days."` does not.
    - `test_evaluative_word_whole_word_only`: in `READING`, `"Not fair."` holds `EVALUATIVE_WORD` and `"Fairly broad."` does not.
    - `test_keep_strings_pass_style_scans`: the seven "Keep" strings of [ux-copy 1.1](../ux-copy.md#11-signs-of-machine-made-text), copied word for word into a tuple in the test, each in `READING`, give a result holding nothing from `WORD_STYLE_FINDINGS`.
  - **Done when:** every row of `scans.toml` passes `test_style_word_scans_table`, `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_scans.py -k "not scans_table"` reports 12 passed, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T1, T11, I4, [Spec 6.2](../spec.md#62-rules-for-every-ai-step) (style scans, and how the scans match), [ux-copy 1.1](../ux-copy.md#11-signs-of-machine-made-text), question 18.
  - **Depends on:** S1-M5-T3.

- [ ] **S1-M5-T6: Style scans: a reason with no anchor**
  - **Build:** In `src/clause_tracer/core/scans.py`, export:
    - `MIN_ANCHOR_LETTERS = 4` and `QUOTED_RUN_PATTERN = re.compile(r'"([^"]+)"')`.
    - `def has_clause_number(text: str, clause_numbers: Iterable[str]) -> bool`: true when some `n` in `clause_numbers` with `n.strip() != ""` has `re.search(r"(?<![\w.])" + re.escape(n.strip()) + r"(?!\w|\.\w)", text, re.IGNORECASE)`. So `5.4` is found in "Read 5.4." but not in "5.40" or "15.4".
    - `def has_quoted_word(text: str, quote: str | None) -> bool`: false when `quote` is `None`. Otherwise, with `folded = fold_for_quote_check(text).text` and `folded_quote = fold_for_quote_check(quote).text` (the fold makes curly double quotes straight), true when some `QUOTED_RUN_PATTERN` match in `folded` gives `run = match.group(1).strip(" .,;:!?")` with `sum(c.isalpha() for c in run) >= MIN_ANCHOR_LETTERS` and `contains_phrase(folded_quote, run)`.
    - In `scan_style`, add `NO_ANCHOR` when `slot` is `REASON`, `has_clause_number(text, context.clause_numbers)` is false and `has_quoted_word(text, context.quote)` is false. A reason with no quote and no clause numbers therefore always fails, and the template is used.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_scans.py`, each in `REASON` with `make_scan_context()` unless a change is named:
    - `test_anchor_scans_table`, one case per `scan_cases()` row: `set(scan_style(case.text, case.slot, case.context)) & {NO_ANCHOR} == case.findings & {NO_ANCHOR}`.
    - `test_clause_number_anchors_a_reason`: `"5.4 sets no deadline."` with `clause_numbers=("5.4",)` does not hold `NO_ANCHOR`.
    - `test_longer_number_is_not_an_anchor`: with `clause_numbers=("5.4",)`, `"5.40 sets no deadline."` and `"15.4 sets no deadline."` each hold `NO_ANCHOR`.
    - `test_number_at_sentence_end_anchors`: `"Read 5.4."` with `clause_numbers=("5.4",)` does not hold `NO_ANCHOR`.
    - `test_quoted_word_from_the_quote_anchors`: `"“Reasonable” has no number, so it can't be checked against your limit."` with `quote="within a reasonable time"` does not hold `NO_ANCHOR`.
    - `test_straight_quotes_also_count`: `'"Reasonable" has no number.'` with `quote="within a reasonable time"` does not hold `NO_ANCHOR`.
    - `test_short_quoted_word_is_not_an_anchor`: `"“the” has no number."` with `quote="the time"` holds `NO_ANCHOR`.
    - `test_quoted_word_not_in_the_quote_fails`: `"“prompt” payment is not defined."` with `quote="within a reasonable time"` holds `NO_ANCHOR`.
    - `test_reason_without_quote_or_clause_fails`: `'"Reasonable" has no number.'` holds `NO_ANCHOR`.
    - `test_no_anchor_only_checks_reasons`: one test function that loops over the slots. `"The wording is vague."` in `READING`, `QUESTION`, `MESSAGE` and `REWRITE` does not hold `NO_ANCHOR`.
  - **Done when:** every row of `scans.toml` passes `test_anchor_scans_table`, `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_scans.py -k "not scans_table"` reports 21 passed, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T1, T11, I4, [Spec 6.2](../spec.md#62-rules-for-every-ai-step) (style scans), [Spec 2](../spec.md#2-glossary) (the quote-check fold).
  - **Depends on:** S1-M5-T5, S1-M5-T4.

- [ ] **S1-M5-T7: Style scans: added sentences**
  - **Build:** In `src/clause_tracer/core/scans.py`, export:
    - `SENTENCE_END_PATTERN = re.compile(r"[.?!]+[\"'’”)\]]*(?=\s|$)")`: one or more of `.`, `?` and `!`, then any closing quotes or brackets, then a space, a line break or the end of the text.
    - `def count_sentences(text: str) -> int`: split `mask_abbreviations(text)` with `SENTENCE_END_PATTERN.split`, and count the pieces that hold at least one character for which `str.isalnum()` is true. So "1.5" does not end a sentence, an abbreviation in `ABBREVIATIONS` does not end one, and text with no end mark is one sentence. The sentence splitter of stage 2 (`ingest`, NUPunkt) is not used: `core` imports no other module, and stage 2 is built later. Both texts of a comparison are counted by this one rule.
    - In `scan_style`, add `ADDED_SENTENCE` when `slot` is `MESSAGE` and (`context.source_text` is `None` or `count_sentences(text) > count_sentences(context.source_text)`); or when `slot` is `REWRITE`, `context.instruction_given` is false, and (`context.source_text` is `None` or `count_sentences(text) > count_sentences(context.source_text)`). With no source to compare, the scan fails closed and the template is used. A new number needs no rule here: the number scan already fails it.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_scans.py`, with `make_scan_context()` unless a change is named:
    - `test_sentence_scans_table`, one case per `scan_cases()` row: `set(scan_style(case.text, case.slot, case.context)) & {ADDED_SENTENCE} == case.findings & {ADDED_SENTENCE}`.
    - `test_count_sentences_examples`: one test function. `""` gives 0; `"   "` gives 0; `"Pay in 30 days."` gives 1; `"Pay. Now!"` gives 2; `"Is it 1.5 days? Yes."` gives 2; `"See e.g. clause 4."` gives 1; `"No end mark"` gives 1; `"The fee is “reasonable.” Ask."` gives 2.
    - `test_message_may_not_add_a_sentence`: in `MESSAGE`, `"Thanks for sending the agreement. Could we look at a few points? That would help me plan the work."` with `source_text="Thanks for sending the agreement. Could we look at a few points?"` holds `ADDED_SENTENCE`.
    - `test_message_may_drop_a_sentence`: in `MESSAGE`, `"Could we look at a few points?"` with the same source does not hold `ADDED_SENTENCE`.
    - `test_clause_rewrite_may_not_add_a_sentence`: in `REWRITE`, `"The Client pays within 30 days. Late payment carries interest."` with `source_text="The Client pays within 30 days."` holds `ADDED_SENTENCE`.
    - `test_instruction_allows_more_sentences`: the same with `instruction_given=True` does not hold `ADDED_SENTENCE`.
    - `test_missing_source_fails_closed`: `"Pay now."` holds `ADDED_SENTENCE` in `MESSAGE`, and in `REWRITE` with `instruction_given=False`; it does not hold it in `REWRITE` with `instruction_given=True`.
    - `test_added_sentence_only_checks_rewrites`: `"5.4 says 60 days. 5.5 says 30 days."` in `REASON` does not hold `ADDED_SENTENCE`.
  - **Done when:** every row of `scans.toml` passes `test_sentence_scans_table`, `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_scans.py -k "not scans_table"` reports 28 passed, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T1, T11, I4, the import rules in AGENTS.md (`core` imports no other module), [Spec 6.2](../spec.md#62-rules-for-every-ai-step) (style scans).
  - **Depends on:** S1-M5-T6.

- [ ] **S1-M5-T8: Value and name scans**
  - **Build:** In `src/clause_tracer/core/scans.py`, export:
    - `NUMBER_PATTERN = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")` and `PLACEHOLDER_PATTERN = re.compile(re.escape(PLACEHOLDER_OPEN) + "[^" + re.escape(PLACEHOLDER_CLOSE) + "]*" + re.escape(PLACEHOLDER_CLOSE))`.
    - `def scan_ai_text(text: str, slot: TextSlot, context: ScanContext, detector: PiiDetector) -> tuple[ScanFinding, ...]`. It starts from `scan_text(text, slot, context.label)`, adds `scan_style(text, slot, context)`, and adds:
      - `UNKNOWN_PLACEHOLDER` for any `PLACEHOLDER_PATTERN` match not in `context.known_placeholders`.
      - For each `NUMBER_PATTERN` match that does not lie inside a placeholder match: `n = Decimal(match.replace(",", ""))`. `ACCEPTABLE_LIMIT` when `n` equals any item of `context.acceptable_limits`, in every slot, even when `n` is also allowed (question 17c and 17f); otherwise `NUMBER_NOT_ALLOWED` when `n` equals no item of `context.allowed_numbers`. Numbers written in words are not checked in stage 1 (question 17b); the README entry for `scan_ai_text` says so.
      - `PERSONAL_DATA` for any suggestion from `detector.find(text)` whose span is not inside a placeholder match and whose text (`text[span.start:span.end]`), case-folded, is not a case-folded item of `context.defined_roles`.
      Findings in `ScanFinding` member order, no repeats.
  - **Files:** `src/clause_tracer/core/scans.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_scans.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_scans.py`, with `make_scan_context()` unless a change is named: `test_full_scans_table`, one case per `scan_cases()` row: build a `FakePiiDetector` that maps the row's `text` to one `PiiSuggestion(span=Span(start=i, end=i + len(s)), kind=PlaceholderKind.PERSON, source=PiiSource.NER)` per `personal_data` substring `s`, where `i = text.index(s)`; `set(scan_ai_text(case.text, case.slot, case.context, detector)) == case.findings`; `test_acceptable_limit_fails_in_every_form` (**promise test**, "no acceptable limit reaches the message step", Spec 11, scan part: with acceptable limit `30` and allowed numbers `30`, the texts `"30"`, `"30 days"` and `"30.00"` in slot `MESSAGE` each give a result holding `ACCEPTABLE_LIMIT`); `test_number_inside_known_placeholder_passes` (`"Ask ⟦Person 1⟧."` in `READING` with `known_placeholders=("⟦Person 1⟧",)` gives no finding); `test_invented_name_fails` (`"Dear John,"` in `READING` with `John` planted gives `(PERSONAL_DATA,)`); `test_number_in_words_is_not_checked` (`"Pay within thirty days."` in `READING` with no allowed numbers gives no finding: the stage 1 limit, question 17b); `test_full_scan_includes_style_scans` (`"I hope this helps!"` in `READING` with `FakePiiDetector({})` gives a result holding `FIRST_PERSON` and `FILLER_PHRASE`).
  - **Done when:** every row of `scans.toml` passes `test_full_scans_table`, `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_scans.py -k "not scans_table"` reports 33 passed, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** P4 (detector passed in), T2, T13, T11, [Spec 6.2](../spec.md#62-rules-for-every-ai-step).
  - **Depends on:** S1-M5-T7, S1-M4-T4.

- [ ] **S1-M5-T9: Cost estimate table (Owner)**
  - **Build:** Owner only. The rows of `cost_estimate.toml`. Columns: `id`; `positions`, `words_positions`, `clauses`, `contract_tokens` (integers); `input_per_million`, `cached_input_per_million`, `output_per_million` (decimal strings, US dollars); the expected `calls` (integer), `low_usd` and `high_usd` (decimal strings with at most four decimal places), worked out by the formula of [system design 7](../system-design.md#7-caching-resume-and-cost). Cases to cover, proposed, owner to check: the starter playbook (11 positions, 1 words position) over 50 clauses with a 10,000-word contract (19,000 tokens), at a cheap and at a Sonnet-class price; a 50,000-word contract (95,000 tokens); one position over one clause; zero clauses; a case whose amounts round at the fourth decimal place. The AI agent does not write or change it (T11).
  - **Files:** `src/clause_tracer/core/tests/tables/cost_estimate.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so. `scripts/check.sh` exits 0.
  - **Rules:** T11, [Spec 9](../spec.md#9-running-the-app) (cost), [system design 7](../system-design.md#7-caching-resume-and-cost) (estimate).
  - **Depends on:** S1-M3-T2.

- [ ] **S1-M5-T10: Cost estimate**
  - **Build:** In `src/clause_tracer/core/cost.py`, export `TASK_TOKENS_PER_CALL = 1000`, `OUTPUT_TOKENS_PER_CALL = 400` and:
    - `def estimate_calls(positions: int, words_positions: int, clauses: int) -> int`: the sum of the table in system design 7, with `math.ceil`.
    - `def estimate_cost(inputs: CostInputs) -> CostRange`: `calls = estimate_calls(...)`. Per call, in `Decimal`: `low_call = (T * cached + TASK * input + OUTPUT * output) / 1_000_000` and `high_call = ((T + TASK) * input + OUTPUT * output) / 1_000_000`, where `T` is `contract_tokens`. `low_usd` and `high_usd` are `calls` times each, then `.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)`.
    Both raise `ValueError` when a count is negative or `words_positions > positions`; `estimate_cost` also when a price is negative.
  - **Files:** `src/clause_tracer/core/cost.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_cost.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_cost.py`: `test_cost_table`, one case per row (all columns required; compare `calls`, `low_usd`, `high_usd`); `test_cost_table_has_rows`; `test_starter_makes_30_calls` (`estimate_calls(11, 1, 50) == 30`, the figure in system design 7); the property `test_low_never_above_high` (counts from `integers(0, 200)` with `words_positions <= positions`, tokens from `integers(0, 200_000)`, prices from `decimals(0, 100, places=2)` with `cached <= input`: `0 <= low_usd <= high_usd`); `test_negative_count_raises`.
  - **Done when:** every row passes, `scripts/check.sh` exits 0, and the owner table is unchanged in the commit.
  - **Rules:** T1, T11, [ADR 0015](../adr/0015-provider-ready-seam.md), [ADR 0010](../adr/0010-starting-models.md), [Spec 9](../spec.md#9-running-the-app).
  - **Depends on:** S1-M5-T9, S1-M2-T7.

- [ ] **S1-M5-T11: Last check before drawing: the text**
  - **Build:** In `src/clause_tracer/core/draw_check.py`, export `def check_before_drawing(document: Document, clause: Clause, evidence: Evidence, quote_text: str) -> DrawAllowed | DrawRefused`. It stops at the first failure and returns `DrawRefused(failure=…)`:
    1. `evidence.clause_id != clause.id`: `CLAUSE_MISMATCH`.
    2. `evidence.sentence_ids` is empty, or holds an id that is not a sentence of `clause`: `SENTENCE_UNKNOWN`.
    3. The region is `Span(start=<smallest start of the cited sentences>, end=<largest end>)`. `evidence.quote` not inside it: `SPAN_OUTSIDE_SENTENCES`.
    4. `q = fold_for_quote_check(quote_text).text.strip(" ")`. Empty: `EMPTY_QUOTE`.
    5. `f = fold_for_quote_check(document.text[region.start:region.end])`. Count every place `q` starts in `f.text` (overlapping places count). None: `QUOTE_NOT_FOUND`. More than one: `QUOTE_NOT_UNIQUE`.
    6. With `i` the one place: `start = region.start + f.to_original[i]` and `end = region.start + f.to_original[i + len(q) - 1] + 1`. `Span(start=start, end=end) != evidence.quote`: `SPAN_MISMATCH`.
    7. Otherwise `DrawAllowed(evidence=evidence)`. (S1-M5-T12 adds the page-box half before this step.)
    It is written apart from the stage 8 quote check: it shares only the fold (system design 15.8).
  - **Files:** `src/clause_tracer/core/draw_check.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_draw_check.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_draw_check.py`, with a helper that builds a `Document` without glyphs for the text `"1. Payment. The Client pays within 60 days. Late fees apply. The Client pays within 60 days."` and one clause `c1` over the whole text with four sentences (`c1.s1` to `c1.s4`, split after each `". "`): `test_exact_quote_passes` (`"Late fees apply."` citing `c1.s3`); `test_curly_quotes_and_spaces_pass` (a document sentence with `"fees"` in curly quotes and two spaces, quoted with straight quotes and one space); `test_quote_twice_in_cited_sentences_fails` (`"The Client pays within 60 days."` citing `c1.s2` to `c1.s4`: `QUOTE_NOT_UNIQUE`); `test_quote_outside_cited_sentences_fails` (`"Late fees apply."` citing `c1.s2`: `QUOTE_NOT_FOUND`, with the evidence span inside `c1.s2`); `test_one_changed_character_fails` (**promise test**, "no made-up quote reaches the screen", Spec 11, unit part: `"Late fees apply!"` is refused); `test_wrong_span_fails` (`SPAN_MISMATCH`); `test_unknown_sentence_fails`; `test_other_clause_fails`; `test_empty_quote_fails` (`"  "`); `test_offsets_count_code_points` (a text starting with `"\U0001F600 "` passes with the span counted in code points).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_draw_check.py` reports 10 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, T13, I5, I4, [system design 4.2](../system-design.md#42-the-offset-chain), [Spec 2](../spec.md#2-glossary) (quote check).
  - **Depends on:** S1-M5-T4, S1-M2-T5.

- [ ] **S1-M5-T12: Last check before drawing: page boxes**
  - **Build:** In `check_before_drawing`, between step 6 and step 7, and only when `document.glyphs` is not empty (decided 14 Nov 2026):
    1. `len(document.char_map) != len(document.text)`: `CHAR_MAP_LENGTH`.
    2. For each index `k` from `evidence.quote.start` to `evidence.quote.end - 1`: `g = document.char_map[k]`. `None` (a character the app inserted) needs no box. `g < 0` or `g >= len(document.glyphs)`: `GLYPH_MISSING`. With `glyph = document.glyphs[g]`: `glyph.page != glyph.box.page`: `PAGE_MISMATCH`; no page in `document.pages` has `number == glyph.page`: `PAGE_UNKNOWN`; unless `0 <= box.x0 <= box.x1 <= page.width` and `0 <= box.top <= box.bottom <= page.height`: `BOX_OUTSIDE_PAGE`.
  - **Files:** `src/clause_tracer/core/draw_check.py`, `src/clause_tracer/core/tests/test_draw_check.py`, `src/clause_tracer/core/README.md` ("Functions").
  - **Tests first:** in `test_draw_check.py`, with a helper that adds one glyph per character on page 1 (`Page(number=1, width=600.0, height=800.0)`, boxes `0, 0, 5, 10`): `test_box_inside_page_passes`; `test_box_past_page_edge_fails` (`x1 = 601`); `test_character_without_glyph_fails` (a `char_map` index past the glyphs: `GLYPH_MISSING`); `test_inserted_characters_need_no_box` (`None` in `char_map` inside the quote passes); `test_ligature_passes` (two characters pointing at one glyph); `test_unknown_page_fails`; `test_page_mismatch_fails`; `test_char_map_length_fails`; `test_document_without_glyphs_skips_boxes`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_draw_check.py` reports 19 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, I5, [ADR 0007](../adr/0007-document-reading-stack.md) (one coordinate system), [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) (unplaceable quote, and the 14 Nov amendment).
  - **Depends on:** S1-M5-T11.

- [ ] **S1-M5-T13: Invariant 7 with the hazard alphabet**
  - **Build:** In `src/clause_tracer/core/tests/strategies.py`, add:
    - `HAZARD_ALPHABET: tuple[str, ...]`: the characters of `"abcXYZ019"`, space, `"\n"`, `" "`, the ligatures `"ﬁ"` and `"ﬂ"`, the soft hyphen `"­"`, `"'"`, `'"'`, `"‘"`, `"’"`, `"“"`, `"”"`, the zero-width characters `"​"`, `"‌"`, `"‍"`, `"﻿"`, the bidi controls `"‪"` to `"‮"` and `"⁦"` to `"⁩"`, `"ß"`, the astral characters `"\U0001F600"` and `"\U0001D400"`, and `"⟦"`, `"⟧"`.
    - `def hazard_text() -> SearchStrategy[str]`: `text(alphabet=sampled_from(HAZARD_ALPHABET), min_size=1, max_size=80)`.
    - `def documents_with_quote() -> SearchStrategy[tuple[Document, Clause, Evidence, str]]`, a `@composite`: draw a hazard text, a `bool` for glyphs, and `0 <= start < end <= len(text)`. Move `start` forward and `end` back past characters for which `isspace()` is true; `assume(start < end)`. The quote is `text[start:end]`; `assume` that its folded form occurs exactly once in the folded text. The document has one clause `c1` over the whole text with one sentence `c1.s1` over the whole text; with glyphs, one glyph per character on page 1 (boxes `0, 0, 1, 1`), `char_map = tuple(range(len(text)))` and `pages = (Page(number=1, width=600.0, height=800.0),)`; without, all three empty. `evidence = Evidence(clause_id=ClauseId("c1"), sentence_ids=(SentenceId("c1.s1"),), quote=Span(start=start, end=end), placed=True)`.
  - **Files:** `src/clause_tracer/core/tests/strategies.py`, `src/clause_tracer/core/tests/test_draw_check.py`.
  - **Tests first:** in `test_draw_check.py`: the property `test_invariant_7_last_check_agrees` (for any `documents_with_quote()`, the result is `DrawAllowed`); the property `test_invariant_7_changed_character_fails` (pick an index of the quote whose character is not whitespace and not one of `' " ‘ ’ “ ”`, `assume` there is one; replace it with `"X"`, or `"Y"` when it already is `"X"`; the result is `DrawRefused`). **Promise test** "every evidence link scrolls to the right place" (Spec 11, unit part). Every failure Hypothesis finds becomes a committed `@example` on the property.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_draw_check.py` reports 21 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T6, T13, [testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants), [ADR 0013](../adr/0013-test-layers-and-release-gates.md).
  - **Depends on:** S1-M5-T12.

### M6: Run alone and close the stage

`python -m clause_tracer.core` prints the Spec 14.5 labels, the README records everything `core` offers, and the owner has the stage report.

- [ ] **S1-M6-T1: Run `core` alone on the sample**
  - **Build:** Rewrite `src/clause_tracer/core/__main__.py`: `def main(argv: list[str] | None = None) -> int`. It parses `--input` with `argparse` (a `Path`, default `Path(__file__).parent / "samples" / "spec-14-5.toml"`), reads the file with `tomllib.load` in binary mode, and calls `parse_sample` and `label_all`. For each label it prints one line: position id, topic, level value, the reason values joined by `,` (or `-` when none), and the written-by value, separated by tabs. It returns 0. A file that cannot be opened prints `clause_tracer.core: cannot read <path>` to standard error and returns 3; a `tomllib.TOMLDecodeError` or `ValueError` prints `clause_tracer.core: <message>` to standard error and returns 3 (exit code 3 is "input file", system design 6.2). Only `__main__` reads a file; nothing else in `core` does.
  - **Files:** `src/clause_tracer/core/__main__.py`, `src/clause_tracer/core/tests/test_smoke.py`.
  - **Tests first:** in `test_smoke.py`: `test_main_returns_zero` (`main([]) == 0`); `test_main_prints_one_line_per_position` (11 lines, whose first and third columns match the position and `level` of each row of the owner's `spec_14_5.toml`); `test_missing_input_returns_3` (standard error names the path); `test_bad_input_returns_3` (a file in `tmp_path` holding `x = `).
  - **Done when:** `.venv/bin/uv run python -m clause_tracer.core` prints 11 lines and exits 0, and `scripts/check.sh` exits 0.
  - **Rules:** S1, S2, I12, T1, [system design 6.2](../system-design.md#62-the-command-line).
  - **Depends on:** S1-M3-T17.

- [ ] **S1-M6-T2: Finish the module README and the module map**
  - **Build:** Make `src/clause_tracer/core/README.md` complete, with these headings in order: "Purpose", "Spec", "Ids and enums", "Errors", "Shapes", "Ports", "Fakes", "Functions" (each public function with its signature and one line on what it returns and raises), "Owner tables" (each file, its columns, its owner task, and "only the owner edits it"), "Depends on", "Run alone". Update the `core` row of `src/clause_tracer/README.md` to: "Pure rules and shapes: every shape, port, error and fake; label picking, playbook checks, output scans, the last check before drawing, auto-delete dates and the cost estimate (Spec 4.1, 5, 6.1 step 8, 6.2, 9)." Change the docstring of `core/__init__.py` to: `"""Pure rules and shapes: labelling, checks and fakes, with no files, network, clock or AI. Implements Spec section 5 (labelling rules); T1 of the Constitution."""`.
  - **Files:** `src/clause_tracer/core/README.md`, `src/clause_tracer/README.md`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/tests/test_architecture.py`.
  - **Tests first:** `test_every_public_name_is_in_the_readme` in `test_architecture.py`: every name in `clause_tracer.core.__all__` appears in the README text inside backticks.
  - **Done when:** the test passes, the README has no "planned" left (`grep -c planned src/clause_tracer/core/README.md` prints 0), and `scripts/check.sh` exits 0.
  - **Rules:** S3, I11, [ADR 0005](../adr/0005-engine-runner-shapes-and-ports.md) action item 4, [WRITING_DOCS](../../WRITING_DOCS.md) sections 2 and 9.
  - **Depends on:** S1-M6-T1, S1-M5-T13, S1-M5-T10, S1-M5-T8, S1-M4-T7, S1-M3-T11.

- [ ] **S1-M6-T3: Stage report to the owner**
  - **Build:** Run every check in section 7. Write "Notes for the next stage" (section 9). Update the status lines the README names under "When the stage is done". Set this plan's status to Done, then send the owner the report that section 7 describes.
  - **Files:** `docs/plans/stage-01-core.md`, `AGENTS.md` ("Where the project stands"), `README.md` (status line), `docs/testing-strategy.md` (section 13).
  - **Tests first:** None. Check: every box in section 7 is ticked.
  - **Done when:** the owner has the report and confirms the stage is Done.
  - **Rules:** [Plans README](README.md) ("When the stage is done").
  - **Depends on:** S1-M6-T2.

## 6. Open questions

Planning found questions 1 to 17. The owner answered all of them on 14 Nov 2026; each answer is recorded in its home. Questions 16 and 17 are the label and scan edge cases. They were answered under one principle, stated once in [Spec 5](../spec.md#5-labelling-rules): when code cannot be sure, the label is unsure, the reason is named, and the user is shown the clause. It never guesses in either direction. The same day the owner added the rate-limit case, which is in the error-tree task S1-M1-T8 and in [Spec 6.2 and 6.3](../spec.md#62-rules-for-every-ai-step). Later that day the owner decided who writes a label's panel words and added five style scans ([Spec 6.1 step 10 and 6.2](../spec.md#62-rules-for-every-ai-step)). Planning those scans found question 18, which the owner answered the same day, as recommended; tasks S1-M5-T1 and S1-M5-T5 follow that answer.

| # | Question | Needed by task | Recommendation (if any) | Owner's answer |
| --- | --- | --- | --- | --- |
| 1 | Add Pydantic as a runtime dependency now, or run the TypeAdapter check with `uv run --with pydantic`? | S1-M1-T2, the TypeAdapter check | Add it now. | Add it now, through `.venv/bin/uv add pydantic`, with `uv.lock` committed: [ADR 0005, amendment of 14 Nov 2026](../adr/0005-engine-runner-shapes-and-ports.md), [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) "Check first" |
| 2 | Which test tooling arrives in stage 1: (a) coverage, (b) the owner-table guard, (c) the socket block, (d) a nightly Hypothesis job? | S1-M1-T3, S1-M1-T4 | (a) and (b) now; (c) and (d) later. | (a) and (b) in stage 1; (c) in stage 6, (d) in stage 5: [ADR 0013, amendment of 14 Nov 2026](../adr/0013-test-layers-and-release-gates.md), [testing strategy 10, 11 and 13](../testing-strategy.md#10-keeping-agent-written-tests-honest) |
| 3 | Where do the fakes live? | S1-M4-T3 | `clause_tracer.core.fakes`. | `clause_tracer.core.fakes`, standard library only, exported from `core`: [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) "Fakes" |
| 4 | The type of `AiRequest.inputs` in stage 1; and does `AiRecord` carry a `schema_version`? | S1-M2-T6 | A marker base class with a test-only shape; `schema_version` on the record if wanted. | `AiRecord.schema_version`; `inputs: StepInputs` (an empty base class), with a test-only subclass: [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), [ADR 0005, amendment of 14 Nov 2026](../adr/0005-engine-runner-shapes-and-ports.md) |
| 5 | Which `ReviewStore` methods does stage 1 draft? | S1-M4-T1, S1-M4-T7 | Raw records, list, delete, purge. | Those four kinds only; stage 6 adds the rest: [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) "Ports" |
| 6 | How do "unlimited" and "none" reach `core`? | S1-M2-T5, S1-M3-T6 | An optional field for "unlimited"; the parser turns "none" into 0. | `CheckedValue.unlimited: bool = False`; "none" becomes 0 in stage 8: [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), [15.8](../system-design.md#158-stage-8-checking-and-the-message-templates) |
| 7 | How does code know a start point is "other than the invoice date" (Rule 5)? | S1-M3-T6, S1-M3-T13 | Act on a reason already on the value; settle the comparison before stage 8. | As recommended; the comparison is "Not yet decided" in [system design 15.8](../system-design.md#158-stage-8-checking-and-the-message-templates); [ADR 0012, amendment of 14 Nov 2026](../adr/0012-missing-unsure-and-evidence-failures.md) |
| 8 | Which match result carries `MATCH_UNCONFIRMED` and the clause to read? | S1-M2-T5, S1-M3-T16 | A fourth result type. | `MatchUnconfirmed(position_id, clauses_to_read)`: [ADR 0012, amendment of 14 Nov 2026](../adr/0012-missing-unsure-and-evidence-failures.md), [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) |
| 9 | What does the Rule 10 overlay take as input? | S1-M3-T6, S1-M3-T16 | The outside documents the trail reaches; who builds the trail is settled before stage 8. | As recommended (`LabelInput.outside_documents`); the trail's builder is "Not yet decided" in [system design 15.8](../system-design.md#158-stage-8-checking-and-the-message-templates) |
| 10 | May stage 1 add the shapes 3.4 does not list? | S1-M2-T7 | Yes. | The planner defines them exactly, in [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) ("Shapes for the stage 1 functions" and the enums); the owner approves them with this plan |
| 11 | The last check before drawing: which fold, and what of documents without glyphs? | S1-M5-T4, S1-M5-T11, S1-M5-T12 | The Spec 2 fold in `core`; boxes only with glyphs. | As recommended: [ADR 0012, amendment of 14 Nov 2026](../adr/0012-missing-unsure-and-evidence-failures.md), [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) (`Document`, `QuoteFold`) |
| 12 | The scans' length cap: one number, or one per slot? | S1-M5-T1, S1-M5-T3 | None. | One cap per kind of AI text (`TextSlot`); the numbers live in the owner's scan table: [Spec 6.2](../spec.md#62-rules-for-every-ai-step) "Length caps", [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) |
| 13 | The cost estimate: what goes in, and how is the range formed? | S1-M5-T9, S1-M5-T10 | Prices passed in, calls from system design 7, cache hits to cache misses. | As recommended: [Spec 9](../spec.md#9-running-the-app) "Cost", [system design 7](../system-design.md#7-caching-resume-and-cost) (the formula) |
| 14 | Auto-delete when the clock jumps backwards? | S1-M4-T5, S1-M4-T6 | Not due; never earlier than the rule allows. | As recommended: [Spec 9](../spec.md#9-running-the-app) "Auto-delete" |
| 15 | Do the Spec 4.1 playbook checks belong in `core` now? | S1-M3-T9, S1-M3-T11 | Leave them to stage 6. | Build them in `core` in stage 1, shared by stages 6 and 12: [ADR 0005, amendment of 14 Nov 2026](../adr/0005-engine-runner-shapes-and-ports.md), [system design 15.1, 15.6 and 15.12](../system-design.md#151-stage-1-core) |
| 16 | **Label edge cases that Spec 5 does not define.** (a) A value with no unit as written. (b) A value with no confirmed quote and no reason code. (c) A value with no number or no answer, and a found match with no value. (d) The judge answers "unsure" for a words position. (e) A deposit amount and a percentage in one clause: when do they "disagree", and what counts? A total of 0. (f) What "clauses give different values" means for Rule 4. (g) A walk-away label: are the reasons of its other values kept? (h) Rule 10 for a Missing label whose missing level is walk-away; and does a walk-away get the unloaded-document reason? (i) Who wrote a words label that the AI never judged? (j) The unit spellings Rule 6 accepts. (k) "Unlimited" when higher is better. | S1-M3-T6, S1-M3-T12 to S1-M3-T16 | (a) The number is in the playbook's unit. (b) Unsure, `QUOTE_NOT_CONFIRMED`. (c) Unsure, `NO_VALUE`. (d) Unsure, `JUDGED_UNSURE`. (e) Compare both rounded half up to a whole percent; when they differ, keep both values with `AMOUNT_PERCENT_DISAGREE`, and Rule 4 combines them; a total of 0 is `AMOUNT_WITHOUT_TOTAL`. (f) Compare readable values clause by clause (converted numbers, yes/no answers, words levels); unsure values are not compared; a range inside one clause is not a disagreement. (g) Yes, every value's reasons are kept. (h) The overlay applies to every label except a walk-away from Rule 4 step 1, so a Missing walk-away becomes unsure; a walk-away gets no extra reason. (i) Code; only a judged words label is written by AI (ADR 0002). (j) The list in S1-M3-T12. (k) Walk-away in both directions. | Items (a) to (j) as recommended. (k) differs: unlimited is walk-away when lower is better and unsure with the new reason `UNLIMITED_UNCLEAR` when higher is better. [Spec 5](../spec.md#5-labelling-rules) (the principle and Rules 1, 3, 4, 6 and 10), [ADR 0012, amendment of 14 Nov 2026](../adr/0012-missing-unsure-and-evidence-failures.md), [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) |
| 17 | **Scan edge cases that Spec 6.2 does not define.** (a) How a listed word matches. (b) Numbers written in words ("thirty"). (c) A number that is both an acceptable limit and an allowed number (the contract itself says 30). (d) Label words used as ordinary English ("an acceptable rate"). (e) What counts as a web address. (f) Which kinds of AI text the acceptable-limit scan covers. | S1-M5-T1, S1-M5-T3, S1-M5-T8 | (a) Whole words or phrases, any letter case, curly apostrophes made straight. (b) Not checked in stage 1; digits only. (c) Flag it as an acceptable limit (fail closed, so the template is used). (d) Flag it: any label word other than the code's label fails. (e) `http://`, `https://`, `www.`, or a bare name ending in a listed domain (`WEB_ADDRESS_PATTERN` in S1-M5-T3). (f) Every kind. | All six as recommended. [Spec 6.2](../spec.md#62-rules-for-every-ai-step) ("How the scans match" and "Acceptable levels"), [ADR 0012, amendment of 14 Nov 2026](../adr/0012-missing-unsure-and-evidence-failures.md) |
| 18 | **Style scans: where the user speaks, and words the AI was given.** (a) The owner's rule exempts only the message rewrite from `FIRST_PERSON`. But the copy deck defines the question to ask as "a polite question the user can send", with the example "Can we agree consent won't be refused without a good reason?" ([ux-copy 3](../ux-copy.md#3-patterns), Spec 5 Rule 2). Is the question exempt too? (b) A first-person, filler or evaluative word that is already in the text the AI was given: its quote (for a reason, reading or question), or the clause or template message a rewrite starts from. Does it fail? Without an exception, a clause written in the first person ("We shall pay…") or one that says "ensure that" or "fair" can never be rewritten, and a reason cannot quote "fair price". | S1-M5-T1, S1-M5-T5 | (a) Yes: `FIRST_PERSON` checks the reason, the readings and the clause rewrite, not the message or the question. (b) No, it passes: the scans look for words the AI added, so an item that also matches in that source text is not flagged. An exclamation mark is treated the same way. | Answered 14 Nov 2026, as recommended: (a) the question to ask is left out of the first-person scan, because the user speaks in it; (b) a listed word that is already in the text the AI was given passes. Home: [Spec 6.2](../spec.md#62-rules-for-every-ai-step). |

## 7. Done when

- [ ] Every task above is ticked.
- [ ] `scripts/check.sh` exits 0: the owner-table guard, ruff, format, mypy strict, `lint-imports`, the copy lint, pytest under coverage, and the coverage floor.
- [ ] Branch coverage of `src/clause_tracer/core/` is at least 95% (`coverage report --include='src/clause_tracer/core/*'`).
- [ ] The five import contracts in `pyproject.toml` are unchanged and pass.
- [ ] The architecture test passes: importing `core` loads only the standard library.
- [ ] The architecture test passes: no `core` shape has a provider-specific field (ADR 0015 action item 2).
- [ ] The label-rule tests cover every row of the Spec 14.5 sample, against the owner's table.
- [ ] No commit changed code and an owner table together (T11): `.venv/bin/uv run python scripts/check_owner_tables.py --commits main` exits 0 on each milestone branch before its pull request.
- [ ] Every promise the stage touches has its test (T13): every planted walk-away gets walk-away (`test_readable_walk_away_wins`); no made-up quote reaches the screen (`test_one_changed_character_fails` in `test_draw_check.py`); every evidence link scrolls to the right place (`test_invariant_7_*`); values on hidden text are unsure (`test_hidden_quote_makes_value_unsure`); no acceptable limit reaches the message step (`test_acceptable_limit_fails_in_every_form`); no AI text states what a law allows (`test_every_law_word_fails_in_any_case`); auto-delete runs on schedule (`test_due_exactly_when_now_reaches_the_due_date`); every stored text keeps a written-by value (`test_wording_needs_written_by`).
- [ ] The five style scans of Spec 6.2 give the owner's findings for every row of `scans.toml` (`test_full_scans_table`), and the "Keep" strings of ux-copy 1.1 pass them (`test_keep_strings_pass_style_scans`).
- [ ] The cost estimate gives 30 calls for the starter playbook over 50 clauses (`test_starter_makes_30_calls`).
- [ ] `src/clause_tracer/core/README.md` records the shapes, ports, fakes, functions and owner tables (S3, ADR 0005 action item 4), and `src/clause_tracer/README.md` matches it.
- [ ] `.venv/bin/uv run python -m clause_tracer.core` runs alone on the sample (S1) and exits 0.
- [ ] The TypeAdapter check result is in the change log.
- [ ] The owner has been told what was built, and what stage 2 should know:
  - the shapes `ingest` will fill (`Document`, `SourceFile`, `Clause`, `Sentence`, `MatchKey`, `InputWarning`, `Span`), and that a document without glyphs has empty `glyphs`, `char_map` and `pages`;
  - the answers to questions 16 to 18, and the "never guess" principle behind 16 and 17;
  - for stage 8: which `ScanContext` fields each AI text needs (the clause numbers and quote for a reason, the source and the instruction for a rewrite), and that the scans catch signs, not a fluent sentence that is wrong (Spec 6.2);
  - that `RateLimitedError` exists: stage 6 maps it to Interrupted with its own message, and stage 9 raises it from an HTTP 429 after the retries;
  - the decision-record action items this stage closes, for the owner to tick: ADR 0005 items 2 and 4, ADR 0012 item 1, ADR 0013 items 1 and 2 (the guard part), ADR 0015 items 1 and 2;
  - a reminder about the ten test contracts;
  - that `cli` has no `README.md` or `samples/` yet, which the planned "every module has a README" architecture test will need.

## 8. Change log

| Date | Change | Why |
| --- | --- | --- |
| 16 Nov 2026 | Accepted (owner, in the working session). Status set to Accepted on `feat/core-m1-foundations`. | Plans README, "Status" |
| 16 Nov 2026 | TypeAdapter check (section 4) passed: Pydantic 2.14.3 (pydantic-core 2.50.4), Python 3.12. `TypeAdapter(...).validate_python(...)` and `validate_json(...)` on `@dataclass(frozen=True, slots=True, kw_only=True)` classes return the dataclass itself, not a Pydantic copy; fields raise `FrozenInstanceError`; the instance has no `__dict__`; a JSON list becomes a tuple; a wrong type raises `ValidationError`; a union of three dataclasses picks the right member; `__post_init__` runs and the mapping becomes a `MappingProxyType`. A JSON-loaded `Decimal` and an aware `datetime` come back as those types. **Base-class note:** a field typed as an empty base dataclass, given a subclass instance, comes back as the base class, not the subclass (the subclass identity is lost). This feeds the stage 6 question in system design 15.6. | S1-M1-T2, ADR 0005 action item 2 |
| 16 Nov 2026 | `test_import_core_loads_only_stdlib` changed from comparing against `sys.stdlib_module_names` alone to a baseline comparison: the same subprocess runs once without importing `clause_tracer.core`, and importing it may add only `clause_tracer` and standard-library names. Reason: the OS loads a system-wide `sitecustomize` (the apport hook) in every Python process, so the original wording failed before `core` was imported. The owner chose this on 16 Nov 2026. The goal of testing strategy 12 ("importing core loads only the standard library") is still enforced: any non-stdlib import `core` causes still fails. | S1-M1-T6, testing strategy 12 |
| 16 Nov 2026 | The coverage floor in `scripts/check.sh` gained `--omit='src/clause_tracer/core/tests/*'`, so the 95% floor measures `core`'s shipped code, not its test files. Reason: the floor as written also measured the test files, and the architecture tests of S1-M1-T6 cannot fully execute until the first shapes of S1-M2-T1 exist, so `check.sh` failed although every test passed. The owner chose this on 16 Nov 2026 and asked to remove the omit again once milestone 2 is implemented, so the floor covers the test files as the plan first wrote it. To do after S1-M2-T1's shapes make the tests fully covered. | S1-M1-T6, testing strategy 11 |
| 16 Nov 2026 | Milestone 1 ticked (tasks S1-M1-T1 to S1-M1-T8, plus section 4's checks), and the status set to In progress. Added two tasks the owner asked for: S1-M1-T9 records that the coverage omit was made, and S1-M2-T8 removes it again once milestone 2's shapes exist. | Plans README ("Status", "When the plan is wrong": add a task) |
| 16 Nov 2026 | S1-M2-T6 hand check: `make_request(inputs={"a": 1})` does **not** fail mypy, as the plan expected. The plan's own signature `make_request(**changes: object)` routes every value through untyped keyword arguments, so the call site is not checked. The type seam itself holds: constructing `AiRequest(...)` directly with `inputs={"a": 1}` does fail mypy (`arg-type`). Strict mypy does flag the `dataclasses.replace(request, **changes)` inside the helper (`arg-type`, six errors), so that line carries one `# type: ignore[arg-type]` with a comment. No code change beyond that; the scratch file was not committed. | S1-M2-T6, plans README ("When the plan is wrong") |
| 16 Nov 2026 | The coverage omit is gone: S1-M2-T8 changed the coverage report line in `scripts/check.sh` back to `run coverage report --include='src/clause_tracer/core/*' --fail-under=95`, as S1-M1-T9 promised once milestone 2's shapes existed. The 95% floor now covers the test files of `core` again, as the plan first had it; `core` measures 99% with them included. | S1-M2-T8 |
| 16 Nov 2026 | Added the fold-sharing note to section 9 before the stage closes, so it cannot be lost. The milestone 2 review (standards axis) flagged that `MatchKey` and `QuoteFold` share a silhouette; both are mandated by system design 3.4, and the decision on one shared fold implementation belongs to stage 2's plan. The note decides nothing; it hands the question to stage 2. | Plans README ("Notes for the next stage", "When the plan is wrong": add a note) |
| 16 Nov 2026 | S1-M3-T10. The `spans_overlap` formula returned true for an empty span inside another span (`3..3` and `0..9`), against the planned test. The owner chose the test's meaning: spans overlap only when they share a code point. Formula changed to `max(a.start, b.start) < min(a.end, b.end)`. | Plans README ("When the plan is wrong"), owner decision of 16 Nov 2026 |

## 9. Notes for the next stage

Filled in when the stage is done: what was built, what differs from the outline, and what stage 2 should know. One note is already recorded, added on 16 Nov 2026 before the stage closes so it cannot be lost:

**The fold is built once, in `core`.** Stage 1 built the Spec 2 quote-check fold as `fold_for_quote_check` (S1-M5-T4), returning `QuoteFold` (`text`, `to_original`), and the last check before drawing uses it (S1-M5-T11). System design 3.4 also defines `MatchKey` (`text`, `to_canonical`) — the folded copy and index map of section 4.2, which stage 2 builds with "the fold for them". The two index maps are not the same thing: `to_canonical` maps the folded text into `Document.text` for matching; `to_original` maps a folded character back to the text the fold came from. The folding rules themselves (quotes made straight, whitespace runs collapsed) are one set of rules in the Spec. When planning stage 2, decide whether one shared fold implementation in `core` serves both shapes, and record the decision in its home (system design 4.2 or a short ADR). Do not build a second fold without saying so.
