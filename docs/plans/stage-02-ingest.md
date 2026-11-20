# Stage 2 plan: `ingest` for text, Markdown and pasted text

| | |
| --- | --- |
| Stage | 2, `ingest` (text, Markdown and pasted text) |
| Status | In progress |
| Branch | One branch for each milestone, cut from `main`: `feat/ingest-m1-foundations`, `feat/ingest-m2-reading`, `feat/ingest-m3-clauses-and-sentences`, `feat/ingest-m4-samples-and-goldens`, `feat/ingest-m5-match-key-and-language`. See [the README](README.md), "Branches and pull requests" |
| Accepted on | 19 Nov 2026 |
| Stage outline | [System design section 15.2](../system-design.md#152-stage-2-ingest-for-text-markdown-and-pasted-text) |

## 1. Goal

`ingest` reads a text file, a Markdown file or pasted text into a `Document`, splits it into clauses with sentence ids, and warns when the contract does not look English. `python -m clause_tracer.ingest` reads the sample contract and prints its clauses and sentences, and the golden files match.

## 2. Scope

**Where the code starts.** `src/clause_tracer/ingest/` is a skeleton: `__init__.py` (an empty `__all__`), `__main__.py` (prints "not built yet"), a README with "planned" shapes, `tests/__init__.py`, `tests/test_smoke.py` and `samples/.gitkeep`. `core` already holds every shape this stage fills: `Document`, `SourceFile`, `Clause`, `Sentence`, `MatchKey`, `InputWarning`, `Span`, and the errors `NotUtf8Error` and `InputTooLargeError`. `core` also holds the Spec 2 quote-check fold (`fold_for_quote_check`). The repo has no sample contract file, no golden file, no root `conftest.py` and no `--update-goldens` command. `scripts/check.sh` has a coverage floor for `core` only. Neither NUPunkt nor Lingua is installed.

### Builds

- Strict UTF-8 reading of text and Markdown files, and reading of pasted text, into a `Document` with no glyphs. Markdown symbols stay plain characters.
- The size limits of [Spec 9](../spec.md#9-running-the-app): 20 MB and 50,000 words, both `[Assumption]`.
- The clause splitter: markers found at line starts (decimal numbers, bracketed items, `a)` items, `Clause`/`Article` keywords, bare `3 Payment` numbers and schedules), a continuity check, unnumbered headings, and the fallback to paragraphs (question 7).
- Sentence ids with NUPunkt, where a clause's sentences join up to the whole clause.
- The match key with its index map: the wide fold `fold_for_matching` in `core` (question 2).
- The not-English warning, with Lingua ([ADR 0017](../adr/0017-language-detection-with-lingua.md), question 1).
- A sample contract, golden files, the `--update-goldens` command, and `python -m clause_tracer.ingest --input …`.
- Owner tables for the clause splitter, the match key and the not-English check (Constitution T11).
- Property tests of offset invariants 2 and 4, and an 85% branch-coverage floor for `ingest`.

### Leaves to later stages

- Word and PDF reading, glyphs, page boxes, furniture, tracked changes, hostile-file limits and the child process: stage 5.
- Every hidden-text check, including zero-width and bidi characters in a text file: stage 5. In stage 2, `Document.hidden`, `undecodable`, `furniture` and `tracked_changes` are always `()`.
- Confusable letters and line-end hyphen joins in the match key: stage 5.
- Fixing a split by hand at the contract check (merge and split): user state, stages 6 and 12.
- Turning error codes and warning codes into words, exit codes in `cli`, and the missing copy for a contract over the word limit: stage 6 (question 5).
- Cross-references, defined terms and schedule references: stage 3.
- The nightly 2,000-example Hypothesis profile: stage 5. The socket block: stage 6.
- Numbering styles this stage does not read (question 7): `A)` and `1)` without an opening bracket; "Section 5" and other keywords; a keyword with a decimal number ("Clause 5.1"); Roman numbers without a keyword; and unnumbered headings longer than 8 words or 60 characters.

## 3. Read first

- [AGENTS.md](../../AGENTS.md), the [Constitution](../../Constitution.md), [GIT_CONVENTIONS.md](../../GIT_CONVENTIONS.md), and [WRITING_DOCS.md](../../WRITING_DOCS.md) sections 2, 5 and 9.
- [System design](../system-design.md): [3.1](../system-design.md#31-the-engine), [3.4](../system-design.md#34-core-shapes-for-stage-1) (the `Document`, `Clause`, `Sentence`, `MatchKey`, `InputWarning` and `QuoteFold` rows, and "Errors"), [4.2](../system-design.md#42-the-offset-chain), [5.1](../system-design.md#51-three-kinds-of-data), [6.2](../system-design.md#62-the-command-line), [6.4](../system-design.md#64-errors), [15.2](../system-design.md#152-stage-2-ingest-for-text-markdown-and-pasted-text). Skim 15.3 to 15.8 to see what later stages take from `ingest`.
- [Testing strategy](../testing-strategy.md): sections [3](../testing-strategy.md#3-five-layers) (golden files), [4](../testing-strategy.md#4-what-to-test-in-each-module) (the `ingest` row), [5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariants 2 and 4, and the hazard alphabet), [10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [11](../testing-strategy.md#11-coverage-targets) and [13](../testing-strategy.md#13-gaps-today-and-the-order-to-close-them).
- [Spec](../spec.md): [2](../spec.md#2-glossary) (Clause, Quote check), [5](../spec.md#5-labelling-rules) (the "never guess" principle), [6.1](../spec.md#61-steps) (steps 1 and 2), [9](../spec.md#9-running-the-app) (file types and input limits), [13](../spec.md#13-open-decisions-before-coding), [14.2](../spec.md#142-states-to-show) (New review and Contract check rows) and [14.5](../spec.md#145-sample-data).
- [UX copy](../ux-copy.md): the "Load the contract" and "Contract check" rows. Read only.
- Decision records: [ADR 0017](../adr/0017-language-detection-with-lingua.md) (Lingua), [ADR 0004](../adr/0004-code-layout.md), [ADR 0007](../adr/0007-document-reading-stack.md) with its amendment of 12 Nov 2026 on NUPunkt, [ADR 0012](../adr/0012-missing-unsure-and-evidence-failures.md) amendment of 14 Nov 2026 (the fold), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) (golden files and the agent guard).
- [The architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md), one part only, as background: [`ingest`](../../reports/Clause%20Tracer%20pipeline%20architecture.md#ingest-keeps-a-page-box-for-every-character). Where it and this plan differ, this plan wins.
- [The stage 1 plan](stage-01-core.md), section 9 ("The fold is built once, in `core`"), and task S1-M3-T1 (the owner-table loader this stage reuses).
- The code: [`src/clause_tracer/ingest/`](../../src/clause_tracer/ingest/), [`src/clause_tracer/core/document.py`](../../src/clause_tracer/core/document.py), [`src/clause_tracer/core/quote_fold.py`](../../src/clause_tracer/core/quote_fold.py), [`src/clause_tracer/core/tests/strategies.py`](../../src/clause_tracer/core/tests/strategies.py), [`src/clause_tracer/core/tests/owner_tables.py`](../../src/clause_tracer/core/tests/owner_tables.py), [`pyproject.toml`](../../pyproject.toml) and [`scripts/check.sh`](../../scripts/check.sh).

## 4. Checks before starting

- [x] **The plan is Accepted.** Questions 1 to 9 in section 6 were answered on 17 Nov 2026, and the tasks follow the answers.
- [x] **The skeleton passes.** Run `.venv/bin/uv sync`, then `scripts/check.sh`. It must exit 0 before any change.
- [x] **NUPunkt behaves as this plan assumes.** The planner checked these on 16 Nov 2026 with `nupunkt` 0.8.0 (MIT, no dependencies, Python 3.11 or later, ships `py.typed`). Run them again after S2-M1-T1: `nupunkt.sentence_spans(text)` returns a list of `(start, end)` pairs; the offsets count code points (`"x\U0001F600. Next one here."` gives a first pair of `(0, 3)`); the same text gives the same pairs on two calls; an empty string gives `[]`. If one fails, stop and bring it to the owner.
- [x] **Lingua behaves as this plan assumes.** The planner checked these on 17 Nov 2026 with `lingua-language-detector` 2.2.0 (Apache-2.0, Python 3.12 or later, ships `py.typed`). Run them again after S2-M1-T6: with `LanguageDetectorBuilder.from_all_languages().build()`, `detect_language_of("Les factures sont payées dans un délai de soixante jours à compter de la date de facture.")` is `Language.FRENCH`, `detect_language_of("Invoices will be paid within 60 days of the invoice date.")` is `Language.ENGLISH`, and a second call gives the same answer. Every row of `not_english.toml` gives its `warned` value under the rule of S2-M5-T4. If one fails, stop and bring it to the owner.
- [x] **The docs are on `main`.** The `docs/` branch that holds this plan, with any spec or system design change the answers needed, is merged. Milestone 1 is cut from that `main`.

## 5. Milestones and tasks

**Rules for every task.**

- Every new shape in `ingest` is written `@dataclass(frozen=True, slots=True, kw_only=True)`.
- A file whose name starts with `_` is internal to `ingest`. Only `__init__.py` re-exports names, and only the names a task says to export.
- Offsets are half-open, count code points and point into `Document.text`.
- Tests of `ingest` may import from `clause_tracer.core.tests` (the owner-table loader and the hazard alphabet). They never import from another pipeline module, because the import contract covers test code.
- A commit that fills an owner table holds no code (the owner-table guard). Golden files never sit in a `tables` folder.

### M1: Foundations

When this is done, NUPunkt and Lingua are pinned, `ingest` has a coverage floor, the golden-file command exists, and the empty owner tables are in place.

- [x] **S2-M1-T1: Add NUPunkt**
  - **Build:** Run `.venv/bin/uv add 'nupunkt==0.8.0'`. It is a runtime dependency, pinned to one version, because sentence ids depend on where it puts sentence breaks. Commit `pyproject.toml` and `uv.lock`.
  - **Files:** `pyproject.toml`, `uv.lock`, `src/clause_tracer/ingest/tests/test_sentence_library.py`.
  - **Tests first:** in `test_sentence_library.py`: `test_nupunkt_version_is_pinned` (`nupunkt.__version__ == "0.8.0"`); `test_known_breaks` (`nupunkt.sentence_spans("Invoices are paid within 60 days. Interest runs at 4% p.a. from the due date. See cl. 5 below.")` equals `[(0, 33), (34, 77), (78, 94)]`); `test_offsets_count_code_points` (`nupunkt.sentence_spans("x\U0001F600. Next one here.")[0] == (0, 3)`); `test_empty_text_has_no_sentences` (`nupunkt.sentence_spans("") == []`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_sentence_library.py` reports 4 passed, and `scripts/check.sh` exits 0.
  - **Rules:** [ADR 0007](../adr/0007-document-reading-stack.md) (NUPunkt), D2 (ids rebuild the same way).
  - **Depends on:** None

- [x] **S2-M1-T2: An 85% coverage floor for `ingest`**
  - **Build:** In `scripts/check.sh`, add one last line: `run coverage report --include='src/clause_tracer/ingest/*' --fail-under=85`. In `scripts/README.md`, change the `check.sh` row to say "a 95% branch-coverage floor for `core` and an 85% floor for `ingest`".
  - **Files:** `scripts/check.sh`, `scripts/README.md`.
  - **Tests first:** None. The check is the script itself.
  - **Done when:** `scripts/check.sh` exits 0 and its last lines show a coverage table for `ingest`. Then change 85 to 101 in your working copy, see the script exit non-zero, and put 85 back.
  - **Rules:** [Testing strategy 11](../testing-strategy.md#11-coverage-targets).
  - **Depends on:** None

- [x] **S2-M1-T3: The golden-file command**
  - **Build:** Create `conftest.py` at the repo root with:
    - `def pytest_addoption(parser: pytest.Parser) -> None`, which adds the option `--update-goldens` (`action="store_true"`, `default=False`, help text `"Rewrite golden files instead of comparing them."`).
    - `def compare_or_update(path: Path, actual: str, *, update: bool) -> None`. When `update` is true, it creates the parent folder and writes `actual` to `path` as UTF-8 with `newline=""`. When false and `path` does not exist, it raises `AssertionError(f"{path.name} is missing. Run pytest with --update-goldens, then read the file.")`. When false and the file exists, it reads it as UTF-8 with `newline=""` and runs `assert actual == expected`.
    - A fixture `golden_compare`, which returns `compare_or_update` itself.
    - A fixture `check_golden(request: pytest.FixtureRequest) -> Callable[[Path, str], None]`, which returns a function `(path, actual)` that calls `compare_or_update(path, actual, update=request.config.getoption("--update-goldens"))`.
    - In `tests/README.md`, add a row for `test_golden_helper.py`.
  - **Files:** `conftest.py`, `tests/test_golden_helper.py`, `tests/README.md`.
  - **Tests first:** in `tests/test_golden_helper.py`, each using `golden_compare` and `tmp_path`: `test_same_text_passes` (file holds `"a\n"`, actual `"a\n"`, `update=False`: no error); `test_different_text_fails` (file `"a\n"`, actual `"b\n"`: `AssertionError`); `test_missing_file_fails_and_names_the_command` (no file: `AssertionError` whose message contains `--update-goldens`); `test_update_writes_the_file` (no file, `update=True`: the file then holds the actual text); `test_update_replaces_the_file` (file `"a\n"`, actual `"b\n"`, `update=True`: the file holds `"b\n"`); `test_line_endings_are_kept` (`update=True` with `"a\r\nb"`, then `update=False` with the same text passes, and the file's bytes are `b"a\r\nb"`).
  - **Done when:** `.venv/bin/uv run pytest tests/test_golden_helper.py` reports 6 passed, `.venv/bin/uv run pytest tests/test_golden_helper.py --update-goldens` also reports 6 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T11, [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest), [ADR 0013](../adr/0013-test-layers-and-release-gates.md) "Agent guard".
  - **Depends on:** None

- [x] **S2-M1-T4: Create the three empty owner tables**
  - **Build:** Create these files, each holding exactly two lines: the `HEADER` line of `clause_tracer.core.tests.owner_tables`, then `# Format: docs/plans/stage-02-ingest.md, task <id>.` with the id of the owner task that fills it: `src/clause_tracer/ingest/tests/tables/clause_split.toml` (S2-M3-T5), `src/clause_tracer/ingest/tests/tables/not_english.toml` (S2-M5-T3), `src/clause_tracer/core/tests/tables/match_fold.toml` (S2-M5-T1). This commit holds these three files and the plan tick, and no code.
  - **Files:** the three files above.
  - **Tests first:** None. The loader test of S1-M3-T1 covers a header-only file.
  - **Done when:** `.venv/bin/uv run python scripts/check_owner_tables.py` exits 0 before the commit, and `scripts/check.sh` exits 0.
  - **Rules:** T11.
  - **Depends on:** None

- [x] **S2-M1-T5: The error for input with no text**
  - **Build:** Needs question 4. In `src/clause_tracer/core/errors.py`, add `class EmptyInputError(InputError)` with `code: ClassVar[str] = "empty_input"`, placed straight after `NotUtf8Error`. Export it from `src/clause_tracer/core/__init__.py`. In `src/clause_tracer/core/README.md`, add the row `` | `EmptyInputError` | Input | `empty_input` | `` after the `NotUtf8Error` row.
  - **Files:** `src/clause_tracer/core/errors.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/README.md`, `src/clause_tracer/core/tests/test_errors.py`.
  - **Tests first:** in `test_errors.py`, add `EmptyInputError` to the `LEAVES` tuple straight after `NotUtf8Error`, and add `test_empty_input_error` (`EmptyInputError().code == "empty_input"`, and it is an instance of `InputError`). See it fail before the class exists.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_errors.py` passes with one more test than before, and `scripts/check.sh` exits 0.
  - **Rules:** I5, I6, D5 (a new error, no rename), [system design 6.4](../system-design.md#64-errors).
  - **Depends on:** None

- [x] **S2-M1-T6: Add Lingua**
  - **Build:** Run `.venv/bin/uv add 'lingua-language-detector==2.2.0'`. It is a runtime dependency, pinned to one version, because the not-English warning depends on its models ([ADR 0017](../adr/0017-language-detection-with-lingua.md)). Commit `pyproject.toml` and `uv.lock`.
  - **Files:** `pyproject.toml`, `uv.lock`, `src/clause_tracer/ingest/tests/test_language_library.py`.
  - **Tests first:** in `test_language_library.py`, with `DETECTOR = LanguageDetectorBuilder.from_all_languages().build()` at module level: `test_lingua_version_is_pinned` (`importlib.metadata.version("lingua-language-detector") == "2.2.0"`); `test_french_sentence` (`DETECTOR.detect_language_of("Les factures sont payées dans un délai de soixante jours à compter de la date de facture.") == Language.FRENCH`); `test_english_sentence` (`DETECTOR.detect_language_of("Invoices will be paid within 60 days of the invoice date.") == Language.ENGLISH`); `test_same_answer_twice` (the French sentence gives the same language on two calls).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_language_library.py` reports 4 passed, and `scripts/check.sh` exits 0.
  - **Rules:** [ADR 0017](../adr/0017-language-detection-with-lingua.md), D2 (the same text gives the same warning).
  - **Depends on:** None

### M2: Reading

When this is done, `read_text_file` and `read_pasted_text` turn bytes or a string into a `Document`, and every input error has a test.

- [x] **S2-M2-T1: Size limits and the word count**
  - **Build:** Needs question 5. In `src/clause_tracer/ingest/limits.py`: `MAX_FILE_BYTES: Final[int] = 20 * 1024 * 1024`; `MAX_WORDS: Final[int] = 50_000`; `def count_words(text: str) -> int`, which returns `len(text.split())`. Both constants carry the comment `# [Assumption] Spec 9: tuned in testing.` Export nothing from `__init__.py` yet.
  - **Files:** `src/clause_tracer/ingest/limits.py`, `src/clause_tracer/ingest/tests/test_limits.py`.
  - **Tests first:** in `test_limits.py`: `test_limits_match_the_spec` (`MAX_FILE_BYTES == 20_971_520` and `MAX_WORDS == 50_000`); `test_count_words` (`"a b\n\nc\td"` gives 4); `test_count_words_empty` (`""` gives 0, `"  \n "` gives 0); `test_count_words_keeps_punctuation_inside_a_word` (`"don't re-use 2.5"` gives 3).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_limits.py` reports 4 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, [Spec 9](../spec.md#9-running-the-app) (input limits).
  - **Depends on:** None

- [x] **S2-M2-T2: Read a text or Markdown file**
  - **Build:** In `src/clause_tracer/ingest/reading.py`:
    - `DOCUMENT_SCHEMA_VERSION: Final[int] = 1`.
    - `def read_text_file(data: bytes, *, kind: FileKind, name: str) -> Document`. Steps, in this order:
      1. `kind` is not `FileKind.TEXT` and not `FileKind.MARKDOWN`: raise `ValueError("read_text_file reads text and Markdown files only")`. This is a bug in the caller, not an input error.
      2. `len(data) > MAX_FILE_BYTES`: raise `InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})`.
      3. `text = data.decode("utf-8", errors="strict")`. On `UnicodeDecodeError as error`: raise `NotUtf8Error({"byte_offset": error.start}) from error`.
      4. `text.find("\x00")` is not -1: raise `NotTextError({"char_offset": that index})`.
      5. `text.replace("\ufeff", "").strip() == ""`: raise `EmptyInputError()`.
      6. `words = count_words(text)`; `words > MAX_WORDS`: raise `InputTooLargeError({"words": words, "limit_words": MAX_WORDS})`.
      7. Return `Document(schema_version=DOCUMENT_SCHEMA_VERSION, source=SourceFile(name=name, kind=kind, sha256=hashlib.sha256(data).hexdigest(), size=len(data)), text=text, char_map=(), glyphs=(), pages=(), furniture=(), hidden=(), undecodable=(), tracked_changes=(), warnings=())`.
    - `Document.text` is the decoded text, character for character. Nothing is removed or changed: not a byte-order mark, not `\r\n`, not a Markdown symbol.
    - The function has a contract note (I11): input, output, the five errors and "no side effects".
    - Export `read_text_file` and `DOCUMENT_SCHEMA_VERSION` from `src/clause_tracer/ingest/__init__.py`. In the README, replace "Input shape (planned)" with the signature and the errors, and "Output shape (planned)" with "A `Document` with no glyphs: `glyphs`, `char_map`, `pages`, `furniture`, `hidden`, `undecodable` and `tracked_changes` are empty in stage 2."
  - **Files:** `src/clause_tracer/ingest/reading.py`, `src/clause_tracer/ingest/__init__.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_reading.py`.
  - **Tests first:** in `test_reading.py`: `test_text_is_the_decoded_bytes` (`"1. Pay\r\n**now** ﬁne\n".encode()` with `kind=FileKind.MARKDOWN`, `name="a.md"`: `text` equals the original string, `source.kind is FileKind.MARKDOWN`, `source.name == "a.md"`, `source.size == len(data)`, `source.sha256 == hashlib.sha256(data).hexdigest()`); `test_byte_order_mark_is_kept` (`b"\xef\xbb\xbfHello"`: `text == "\ufeffHello"`); `test_document_has_no_glyphs` (`read_text_file(b"1. Pay now.", kind=FileKind.TEXT, name="a.txt")`: the seven tuple fields named in the README line are `()`, `warnings == ()`, `schema_version == 1`); `test_not_utf8_raises` (`b"caf\xe9 bar"`: `NotUtf8Error` with `context["byte_offset"] == 3`); `test_nul_in_file_raises` (`b"abc\x00def"` with `kind=FileKind.TEXT`, `name="a.txt"`: `NotTextError` with `context["char_offset"] == 3`); `test_nul_only_file_raises` (`b"\x00"`: `NotTextError`, not `EmptyInputError`); `test_file_over_the_byte_limit_raises` (`b"a" * (MAX_FILE_BYTES + 1)`: `InputTooLargeError` with `context == {"size_bytes": MAX_FILE_BYTES + 1, "limit_bytes": MAX_FILE_BYTES}`); `test_file_at_the_byte_limit_is_checked_for_words_next` (`b"a" * MAX_FILE_BYTES`: a `Document`, because it is one word); `test_over_the_word_limit_raises` (`("a " * 50_001).encode()`: `InputTooLargeError` with `context == {"words": 50_001, "limit_words": 50_000}`); `test_at_the_word_limit_passes` (`("a " * 50_000).encode()`: a `Document`); `test_empty_file_raises` (`b""`: `EmptyInputError`); `test_blank_file_raises` (`b" \n\t\r\n"`: `EmptyInputError`); `test_bom_only_file_raises` (`b"\xef\xbb\xbf"`: `EmptyInputError`); `test_bom_and_blank_file_raises` (`b"\xef\xbb\xbf \n"`: `EmptyInputError`); `test_wrong_kind_is_a_bug` (`kind=FileKind.PDF`: `ValueError`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_reading.py` reports 15 passed, and `scripts/check.sh` exits 0.
  - **Rules:** D1 (the text is kept unchanged), D4, I5, I7, I11, S3, [Spec 9](../spec.md#9-running-the-app) (file types).
  - **Depends on:** S2-M1-T5, S2-M2-T1. `NotTextError` is added to `core` in this milestone (code, `core` README and system design 3.4), 19 Nov 2026.

- [x] **S2-M2-T3: Read pasted text**
  - **Build:** In `reading.py`, add `def read_pasted_text(text: str) -> Document`. It first checks `len(text) > MAX_FILE_BYTES` and raises `InputTooLargeError({"size_chars": len(text), "limit_bytes": MAX_FILE_BYTES})`, then encodes: `data = text.encode("utf-8", errors="strict")`, and on `UnicodeEncodeError as error` raises `NotUtf8Error({"char_offset": error.start}) from error` (a string can hold a lone surrogate, which is not valid text). Then it checks the bytes: `len(data) > MAX_FILE_BYTES` raises `InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})`. `_build_document(data: bytes, text: str, *, kind: FileKind, name: str) -> Document` holds the NUL, blank, word and build steps; both public functions call it, with `SourceFile(name="", kind=FileKind.PASTED, …)` for a paste. Export `read_pasted_text`. Add it to the README beside `read_text_file`.
  - **Files:** `src/clause_tracer/ingest/reading.py`, `src/clause_tracer/ingest/__init__.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_reading.py`.
  - **Tests first:** in `test_reading.py`: `test_pasted_text_is_kept` (`"1. Pay\n# now"`: `text` is the same string, `source.kind is FileKind.PASTED`, `source.name == ""`, `source.size == 12`, and `source.sha256` is the SHA-256 of the UTF-8 bytes); `test_pasted_text_matches_the_same_text_as_a_file` (`read_pasted_text(s).text == read_text_file(s.encode(), kind=FileKind.TEXT, name="a.txt").text` for `s = "(a) one\n(b) two"`); `test_pasted_blank_raises` (`"  \n"`: `EmptyInputError`); `test_pasted_bom_only_raises` (`"\ufeff"`: `EmptyInputError`); `test_pasted_lone_surrogate_raises` (`"a\ud800b"`: `NotUtf8Error` with `context["char_offset"] == 1`); `test_pasted_nul_raises` (`"a\x00b"`: `NotTextError` with `context["char_offset"] == 1`); `test_pasted_over_the_character_limit_raises` (`"a" * (MAX_FILE_BYTES + 1)`: `InputTooLargeError` with `context == {"size_chars": MAX_FILE_BYTES + 1, "limit_bytes": MAX_FILE_BYTES}`); `test_pasted_over_the_byte_limit_raises` (now `"é" * (MAX_FILE_BYTES // 2 + 1)`, which is 10,485,761 characters and 20,971,522 bytes: `InputTooLargeError` with `context == {"size_bytes": 2 * (MAX_FILE_BYTES // 2 + 1), "limit_bytes": MAX_FILE_BYTES}`); `test_pasted_over_the_word_limit_raises` (`"a " * 50_001`: `InputTooLargeError`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_reading.py` reports 24 passed, and `scripts/check.sh` exits 0.
  - **Rules:** D1, D4, I2 (two functions, no flag), S3, [Spec 9](../spec.md#9-running-the-app) ("read exactly like pasted text").
  - **Depends on:** S2-M2-T2

### M3: Clauses and sentences

When this is done, `split_clauses` gives the clauses of a document with their sentences, the owner's splitter table passes, and invariant 4 holds on generated text.

**How the splitter works.** It reads the text line by line. A line may start with a *marker*: a number (`5.` or `5.1`), a bracketed item (`(a)` or `a)`), a keyword (`Clause 5`, `Article IV`), a bare number before a capital word (`3 Payment`), or a schedule heading (`Schedule 1`). A marker opens a new clause only when it follows on from the numbering so far (the continuity check). A short line with no marker is a heading clause of its own when a blank line stands before it or a marker line follows it. Every other line belongs to the clause before it. The clauses cover the whole text with no gap and no overlap, so no word of the contract falls outside a clause (question 6). If no marker is accepted, the text is split by paragraph.

- [x] **S2-M3-T1: Lines**
  - **Build:** In `src/clause_tracer/ingest/_lines.py`: the shape `Line` with fields `start: int`, `end: int`, `text: str` (`text` is `document_text[start:end]`, without the line break); and `def split_lines(text: str) -> tuple[Line, ...]`. A line break is `"\r\n"`, or a single `"\r"`, or a single `"\n"`, matched with `re.compile(r"\r\n|\r|\n")`. Text after the last break is a line, even when empty, so `""` gives one empty line. Add `def is_blank(line: Line) -> bool`, true when `line.text.replace("\ufeff", "").strip() == ""`, so a line with only whitespace and byte-order marks is blank (a shared `is_blank_text(text)` holds the test; the preamble test and the heading test in `clauses.py` use it too).
  - **Files:** `src/clause_tracer/ingest/_lines.py`, `src/clause_tracer/ingest/tests/test_lines.py`.
  - **Tests first:** in `test_lines.py`: `test_three_kinds_of_break` (`"a\nb\r\nc\rd"` gives texts `("a", "b", "c", "d")` and starts `(0, 2, 5, 7)`); `test_empty_text_is_one_empty_line` (`""` gives one line `Line(start=0, end=0, text="")`); `test_trailing_break_gives_a_last_empty_line` (`"a\n"` gives two lines, the second `Line(start=2, end=2, text="")`); `test_blank_line` (`is_blank` is true for `" \t"` and false for `" a"`); the property `test_lines_point_into_the_text` (for `hazard_text()` from `clause_tracer.core.tests.strategies`: every line has `text == source[line.start:line.end]`, and no line text contains `"\n"` or `"\r"`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_lines.py` reports 5 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, T6.
  - **Depends on:** None

- [x] **S2-M3-T2: The continuity rules**
  - **Build:** In `src/clause_tracer/ingest/_numbering.py`:
    - `def is_decimal_successor(previous: tuple[int, ...], parts: tuple[int, ...]) -> bool`. With `m = len(previous)` and `n = len(parts)`, it is true when some `k` from 1 to `min(n, m + 1)` has all three of: `parts[:k-1] == previous[:k-1]`; either `k <= m and parts[k-1] == previous[k-1] + 1` (the next sibling at depth `k`) or `k == m + 1 and parts[k-1] == 1` (the first child); and every part after position `k` equals 1.
    - `class ParenStyle(StrEnum)` with `LOWER`, `ROMAN`, `UPPER`, `DIGIT`.
    - `def paren_readings(token: str) -> tuple[tuple[ParenStyle, int], ...]`: every way to read a bracketed token, in the order LOWER, ROMAN, UPPER, DIGIT. LOWER: one letter `a` to `z` is 1 to 26; the same letter twice, `aa` to `zz`, is 27 to 52. ROMAN: a token that `re.fullmatch(r"x{0,3}(ix|iv|v?i{0,3})", token)` accepts and that is not empty, valued like `roman_numeral_value(token.upper())`, so 1 (`i`) to 39 (`xxxix`). UPPER: one letter `A` to `Z` is 1 to 26. DIGIT: `1` to `99` with no leading zero. A token with no reading gives `()`.
    - `def roman_numeral_value(token: str) -> int | None`: the value of an upper-case Roman numeral in its standard form, 1 to 3999, the form `re.fullmatch(r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})", token)` accepts. An empty token, a token that does not match, and a lower-case token give `None`. Each letter counts I 1, V 5, X 10, L 50, C 100, D 500, M 1000, and a letter before a larger one is subtracted.
  - **Files:** `src/clause_tracer/ingest/_numbering.py`, `src/clause_tracer/ingest/tests/test_numbering.py`.
  - **Tests first:** in `test_numbering.py`: the parametrised `test_is_decimal_successor` over `(previous, parts, expected)`: `((5, 6), (5, 7), True)`, `((5, 6), (6,), True)`, `((5, 6), (6, 1), True)`, `((5, 6), (5, 6, 1), True)`, `((5,), (5, 1), True)`, `((1, 2), (2, 1), True)`, `((1, 2), (2, 1, 1), True)`, `((1, 2, 3), (1, 3), True)`, `((1, 2, 3), (2,), True)`, `((5, 6), (7,), False)`, `((5, 6), (2, 5), False)`, `((5, 6), (5, 6), False)`, `((5, 6), (5, 8), False)`, `((5,), (5, 2), False)`, `((5, 6), (5, 6, 2), False)`, `((5, 6), (4,), False)`; the parametrised `test_paren_readings` over `(token, expected)`: `("a", ((LOWER, 1),))`, `("h", ((LOWER, 8),))`, `("i", ((LOWER, 9), (ROMAN, 1)))`, `("v", ((LOWER, 22), (ROMAN, 5)))`, `("ii", ((LOWER, 35), (ROMAN, 2)))`, `("iv", ((ROMAN, 4),))`, `("xxxix", ((ROMAN, 39),))`, `("xl", ())`, `("iiii", ())`, `("aa", ((LOWER, 27),))`, `("ab", ())`, `("A", ((UPPER, 1),))`, `("1", ((DIGIT, 1),))`, `("99", ((DIGIT, 99),))`, `("the", ())`; the parametrised `test_roman_numeral_value` over `(token, expected)`: `("I", 1)`, `("IV", 4)`, `("XIV", 14)`, `("MCMXC", 1990)`, `("IIII", None)`, `("IC", None)`, `("", None)`, `("iv", None)`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_numbering.py` reports 39 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, T6.
  - **Depends on:** None

- [x] **S2-M3-T3: Markers**
  - **Build:** Needs questions 7 and 8. In `src/clause_tracer/ingest/_markers.py`:
    - `class MarkerKind(StrEnum)` with `DECIMAL`, `PAREN`, `SCHEDULE`, `KEYWORD`, `BARE` (values are the lower-case names).
    - The shape `Marker` with fields `kind: MarkerKind`, `parts: tuple[int, ...]`, `token: str`, `written: str`, `id_part: str`, `body_start: int`. `written` is the number as the clause's `number` field shows it. `id_part` is the piece the clause id is built from.
    - `def find_marker(line_text: str) -> Marker | None`. It tries the six patterns below in the order SCHEDULE, DECIMAL, PAREN, KEYWORD, CLOSING PAREN, BARE, each anchored at the start of the line with `re.match`, and returns the first that gives a marker.
    - `PREFIX = r"[ \t\ufeff#*_]*"`: spaces, tabs, a byte-order mark and the Markdown symbols `#`, `*` and `_` may stand before a marker. `CLOSE = r"(?:\*\*|__)?"`: a closing Markdown bold may follow it. `AFTER = r"(?=[ \t]|$)"`.
    - **DECIMAL:** `PREFIX + r"(?P<num>[0-9]{1,3}(?:\.[0-9]{1,3}){0,4})(?P<dot>\.)?" + CLOSE + AFTER`. When `num` has one part and `dot` did not match, there is no marker. `parts` is each part as an `int`. `token` is `""`. `written` is the number exactly as the line writes it (so `"05."` gives `"05"`). `id_part` is the parts joined with `"."` (so `"05."` gives `"5"`).
    - **PAREN:** `PREFIX + r"\((?P<tok>[a-z]{1,6}|[A-Z]|[1-9][0-9]?)\)" + CLOSE + AFTER`. When `paren_readings(tok)` (S2-M3-T2) is empty, there is no marker. `parts` is `()`. `token` is `tok`. `written` and `id_part` are `"(" + tok + ")"`.
    - **SCHEDULE:** `PREFIX + r"(?P<word>(?i:schedule|annex|appendix|exhibit))[ \t]+(?P<des>[0-9]{1,3}|[A-Z])(?![0-9A-Za-z])"`. It is a marker only when the whole line is heading-like: with `stripped = line_text.strip(EMPHASIS_STRIP)`, `len(stripped) <= 100` and `stripped[-1] not in ".;:,"`; and when the text after the designation is empty or starts, after spaces and tabs, with one of `·`, `:`, `-`, `–`, `—`. So `Schedule 1 · Services` is a marker and a wrapped line `Schedule 2 to this Agreement and the Customer will pay` is not. `parts` is `()`. `token` and `id_part` are `word[0].upper() + des`. `written` is `word + " " + des`, with `word` as the line writes it.
    - **KEYWORD:** `PREFIX + r"(?P<word>[Cc]lause|CLAUSE|[Aa]rticle|ARTICLE)[ \t]+(?P<num>[0-9]{1,3}|[IVXLCDM]{1,7})(?:[ \t]*[.:\u2013\u2014-])?" + CLOSE + r"(?=[ \t]*$|[ \t]+[A-Z])"`. The value is `int(num)` when `num` is digits with no leading zero, else `roman_numeral_value(num)` (S2-M3-T2). When `num` has a leading zero or the value is `None`, there is no marker. `parts` is `(value,)`. `token` is `""`. `written` is `word + " " + num`, as the line writes them. `id_part` is `str(value)`. So `Article IV` gives the id `4`, and its children `4.1`.
    - **CLOSING PAREN:** `PREFIX + r"(?P<tok>[a-z]{1,6})\)" + CLOSE + AFTER`. When `paren_readings(tok)` is empty, there is no marker. The kind is `PAREN`. `parts` is `()`. `token` is `tok`. `written` is `tok + ")"`. `id_part` is `"(" + tok + ")"`, so `a)` under `7.1` gives the id `7.1(a)`.
    - **BARE:** `PREFIX + r"(?P<num>[1-9][0-9]{0,2})" + CLOSE + r" +(?P<word>[A-Z][^ \t]*)"`. It is a marker only when all three hold: `"\t" not in line_text`; `word.rstrip(",.;:")` is not in `MONTH_NAMES`; and with `stripped = line_text.strip(EMPHASIS_STRIP)`, `len(stripped) <= 100` and `stripped[-1] not in ".;:,"`. `parts` is `(int(num),)`. `token` is `""`. `written` and `id_part` are `num`. `body_start` is the start of `word`.
    - `MONTH_NAMES: Final[frozenset[str]]` holds the twelve English month names with a capital first letter, `"January"` to `"December"`.
    - `EMPHASIS_STRIP: Final[str] = " \t\ufeff#*_"` and `HEADING_STRIP: Final[str] = EMPHASIS_STRIP + "·:-–—"`.
    - Except for BARE (the start of `word`), `body_start` is the index in `line_text` of the first character after the match that is not a space or a tab. It equals `len(line_text)` when nothing follows.
    - `def is_heading_line(line_text: str) -> bool`: with `stripped = line_text.strip(EMPHASIS_STRIP)`, true when all hold: `stripped != ""`; `len(stripped) <= 60`; `len(stripped.split()) <= 8`; `stripped[-1] not in ".,;:"`; `"\t" not in line_text`; and `stripped[0].isupper()`. It looks at one line only. S2-M3-T6 adds the conditions on the lines around it.
  - **Files:** `src/clause_tracer/ingest/_markers.py`, `src/clause_tracer/ingest/tests/test_markers.py`.
  - **Tests first:** in `test_markers.py`, the parametrised test `test_find_marker` over these rows (`line`, then `None` or `kind, parts, token, written, id_part, body_start`):

    | Line | Result |
    | --- | --- |
    | `"5. Charges"` | `DECIMAL, (5,), "", "5", "5", 3` |
    | `"5.1 The Agency"` | `DECIMAL, (5, 1), "", "5.1", "5.1", 4` |
    | `"5.1. The Agency"` | `DECIMAL, (5, 1), "", "5.1", "5.1", 5` |
    | `"  12.3.4\tText"` | `DECIMAL, (12, 3, 4), "", "12.3.4", "12.3.4", 9` |
    | `"05. Old style"` | `DECIMAL, (5,), "", "5", "5", 4` |
    | `"7."` | `DECIMAL, (7,), "", "7", "7", 2` |
    | `"5 November 2026"` | `None` |
    | `"12.11.2026 is the date"` | `None` |
    | `"2026. A year"` | `None` |
    | `"5.1The Agency"` | `None` |
    | `"1.2.3.4.5.6 too deep"` | `None` |
    | `"\ufeff1. First"` | `DECIMAL, (1,), "", "1", "1", 4` |
    | `"## 3. The Services"` | `DECIMAL, (3,), "", "3", "3", 6` |
    | `"**5.1** The Agency"` | `DECIMAL, (5, 1), "", "5.1", "5.1", 8` |
    | `"(a) first"` | `PAREN, (), "a", "(a)", "(a)", 4` |
    | `"(iv) fourth"` | `PAREN, (), "iv", "(iv)", "(iv)", 5` |
    | `"(A) The Agency"` | `PAREN, (), "A", "(A)", "(A)", 4` |
    | `"(12) twelve"` | `PAREN, (), "12", "(12)", "(12)", 5` |
    | `"(the Agency) will"` | `None` |
    | `"(a)first"` | `None` |
    | `"a) first"` | `PAREN, (), "a", "a)", "(a)", 3` |
    | `"ii) components"` | `PAREN, (), "ii", "ii)", "(ii)", 4` |
    | `"Schedule 1 · Services and Charges"` | `SCHEDULE, (), "S1", "Schedule 1", "S1", 11` |
    | `"SCHEDULE 2"` | `SCHEDULE, (), "S2", "SCHEDULE 2", "S2", 10` |
    | `"Annex A: Rates"` | `SCHEDULE, (), "AA", "Annex A", "AA", 7` |
    | `"Schedule 1 conflict, this Agreement prevails."` | `None` |
    | `"Schedule 12a"` | `None` |
    | `"The Schedule 1"` | `None` |
    | `"Article IV Payment"` | `KEYWORD, (4,), "", "Article IV", "4", 11` |
    | `"Article IV. Payment"` | `KEYWORD, (4,), "", "Article IV", "4", 12` |
    | `"ARTICLE 4"` | `KEYWORD, (4,), "", "ARTICLE 4", "4", 9` |
    | `"Clause 5: Fees"` | `KEYWORD, (5,), "", "Clause 5", "5", 10` |
    | `"clause 12 – Notices"` | `KEYWORD, (12,), "", "clause 12", "12", 12` |
    | `"Clause 5 applies to notices."` | `None` |
    | `"Article 4.1 Terms"` | `None` |
    | `"Article IIII Bad"` | `None` |
    | `"3 Payment"` | `BARE, (3,), "", "3", "3", 2` |
    | `"**3** Payment"` | `BARE, (3,), "", "3", "3", 6` |
    | `"30 days' notice"` | `None` |
    | `"1 January 2027"` | `None` |
    | `"3 Build\tWeek 6"` | `None` |
    | `"1000 Things"` | `None` |
    | `"2 Build Templates."` | `None` |
    | `"03 Old"` | `None` |
    | `""` | `None` |

    And the parametrised `test_is_heading_line` over `(line, expected)`: `("Background", True)`, `("## Parties", True)`, `("Signed by Karim Benali", True)`, `("the Developer", False)`, `("The work is done.", False)`, `("Milestone\tWork", False)`, `("", False)`, `("A" * 61, False)`, `("One two three four five six seven eight nine", False)`.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_markers.py` reports 54 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, T6, B4 (the patterns that find a marker are hidden here), [Spec 9](../spec.md#9-running-the-app) (Markdown symbols stay plain characters in the text), [system design 4.2](../system-design.md#42-the-offset-chain) (what the splitter reads).
  - **Depends on:** S2-M3-T2

- [x] **S2-M3-T4: Sentence starts from NUPunkt**
  - **Build:** In `src/clause_tracer/ingest/_sentences.py`: `def sentence_starts(text: str) -> tuple[int, ...]`, which returns `tuple(start for start, _end in nupunkt.sentence_spans(text))`. This is the only file in the repo that imports `nupunkt`.
  - **Files:** `src/clause_tracer/ingest/_sentences.py`, `src/clause_tracer/ingest/tests/test_sentences.py`.
  - **Tests first:** in `test_sentences.py`: `test_starts_of_three_sentences` (the text of `test_known_breaks` in S2-M1-T1 gives `(0, 34, 78)`); `test_empty_text` (`""` gives `()`); `test_only_this_file_imports_nupunkt` (read every `.py` file under `src/clause_tracer/` except `ingest/_sentences.py` and the files in `ingest/tests/`; none contains the string `nupunkt`); the property `test_starts_are_strictly_increasing_and_inside_the_text` (for `hazard_text()`: each start is `>= 0` and `< len(text)`, and each is greater than the one before).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_sentences.py` reports 4 passed, and `scripts/check.sh` exits 0.
  - **Rules:** B4 (the sentence library is hidden in one file), [ADR 0007](../adr/0007-document-reading-stack.md).
  - **Depends on:** S2-M1-T1

- [x] **S2-M3-T5: Clause-splitter table (Owner)**
  - **Build:** Owner only. Fill `src/clause_tracer/ingest/tests/tables/clause_split.toml`. Each `[[case]]` has the keys `id` (string), `text` (the contract text, a TOML multi-line string), `numbering` (`"numbers"` or `"paragraphs"`) and `clauses`: a list of inline tables, one for each expected clause in order, each with `id`, `number`, `level` (integer), `parent`, `heading` and `starts_with`. An empty string in `number`, `parent` or `heading` means "none". `starts_with` is the first words of the clause. Cover at least: the testing strategy's "2.5 days is not a clause number"; `(i)` after `(h)` and `(i)` after `(a)`; a numbered heading with sub-clauses; text before the first number; a schedule that restarts at 1; a contract with no numbers; a Markdown heading before a number; an excerpt that starts at clause 5; a contract whose numbering skips a number; a table of contents before the body; a numbered list inside a clause; `Article` keywords, and `Clause 9` inside a sentence; `a)` items, in order and out of order; bare `1 Heading` numbers, and lines that look like them but are text; an unnumbered heading after a blank line, and short lines that are not headings; recitals after a `Background` heading. The splitter's rules are in S2-M3-T6 to S2-M3-T9, and section 6 lists the cases where the owner's answer changes them.
  - **Files:** `src/clause_tracer/ingest/tests/tables/clause_split.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** T11.
  - **Depends on:** S2-M1-T4

- [x] **S2-M3-T6: Which lines start a clause**
  - **Build:** Needs questions 6, 7 and 9. In `src/clause_tracer/ingest/clauses.py`: `NUMBERING_NUMBERS: Final[str] = "numbers"`, `NUMBERING_PARAGRAPHS: Final[str] = "paragraphs"`, and `def split_clauses(document: Document) -> tuple[Clause, ...]`. It reads only `document.text`. When `document.text.strip() == ""` it returns `()`. Export the three names. This task builds the numbered path: which lines start a clause, and each clause's id, parent, level and span. Until S2-M3-T7, every `heading` is `None`. Until S2-M3-T8, every clause has exactly one sentence, over its whole span, with the id `f"{clause_id}.s1"`. When no marker is accepted (heading lines do not count) it calls `_split_paragraphs(text)`, which until S2-M3-T9 returns one clause `p1` over the whole text with `numbering_source="paragraphs"`.
    - **State,** reset at the start: `scope_prefix = ""`, `scope_parent: ClauseId | None = None`, `last_decimal: tuple[int, ...] | None = None`, `open_decimal: dict[tuple[int, ...], ClauseId] = {}`, `base: ClauseId | None = None` (the clause a bracketed item hangs from), `paren_stack: list[tuple[ParenStyle, int, ClauseId]] = []`, `suspended: list[tuple[tuple[int, ...], dict[tuple[int, ...], ClauseId]]] = []` (numbering runs that a restart interrupted), `used_ids: set[str] = set()`.
    - **For each line** of `lines = split_lines(text)`, in order, take `marker = find_marker(line.text)`. A line whose marker is not accepted is a continuation line and changes nothing. A line with no marker is a heading line or a continuation line (below).
    - **SCHEDULE** is always accepted. Its id is `marker.token`. Parent `None`. Then: `scope_prefix = id + "."`, `scope_parent = id`, `base = id`, `last_decimal = None`, `open_decimal = {}`, `paren_stack = []`, `suspended = []`.
    - **DECIMAL and KEYWORD** with parts `p`. Try these in order, and stop at the first that fits:
      1. `last_decimal is None`: accepted.
      2. `is_decimal_successor(last_decimal, p)`: accepted.
      3. Walk `suspended` from the top down. At the first entry `(run_last, run_open)` with `is_decimal_successor(run_last, p)`: set `last_decimal = run_last` and `open_decimal = run_open`, drop that entry and every entry above it, and accept. A list inside a clause has ended, and the outer numbering goes on.
      4. `p == (1,)`: push `(last_decimal, open_decimal)` on `suspended`, set `open_decimal = {}`, and accept. Numbering starts again, as after a table of contents.
      5. Otherwise the marker is not accepted.

      **BARE** with parts `p` is accepted when `last_decimal is None` and `p == (1,)`, or when `last_decimal is not None` and `is_decimal_successor(last_decimal, p)`. Otherwise it is not accepted. A bare number never starts numbering again and never resumes a suspended run, and before any numbering only a bare `1` starts it, so an address line such as `27 Rue Didouche Mourad` stays text.

      On acceptance (DECIMAL, KEYWORD or BARE): remove from `open_decimal` every key that is not a proper prefix of `p`; the parent is the clause of the longest key left, or `scope_parent` when none is left; the id is `scope_prefix + marker.id_part`; then `open_decimal[p] = id`, `last_decimal = p`, `base = id`, `paren_stack = []`.
    - **PAREN** with token `t`: (1) walk `paren_stack` from the top down; at the first entry `(style, value, _)` for which `(style, value + 1)` is in `paren_readings(t)`, accept as its next sibling: drop that entry and every entry above it. (2) Otherwise, when `paren_readings(t)` holds a reading `(style, 1)` whose style is not in `paren_stack`, accept as a first child. (3) Otherwise the marker is not accepted. On acceptance: the parent is the clause of the entry now on top of `paren_stack`, or `base` when the stack is empty; the id is `parent + marker.id_part` when there is a parent, else `scope_prefix + marker.id_part`; then push `(style, value, id)`. `(style, value)` is the reading the item was accepted on: `(style, value + 1)` of the matched entry for a sibling, or `(style, 1)` for a first child.
    - **Heading lines.** A line with no marker, at index `i` in `lines`, is a heading line when all three hold: `i > 0`; `is_heading_line(line.text)` (S2-M3-T3); and either `lines[i - 1]` is blank, or the first non-blank line after it has `find_marker(...) is not None`. A heading line opens a clause with `number=None`, `parent_id=None` and `level=1`. Then `paren_stack = []` and `base = None`, so a bracketed item after a heading starts at the top level. Nothing else changes: `last_decimal`, `open_decimal`, `suspended`, `scope_prefix` and `scope_parent` stay as they are. Any other line with no marker is a continuation line.
    - **Ids of clauses with no number.** After the walk, number the clauses with no number `p1`, `p2` and so on, in text order. The clause of text before the first clause, when there is one, is `p1`. Each is made unique by the rule below, in the same order.
    - **Unique ids.** When an id is already in `used_ids`, add `"~2"` to it, or `"~3"` and so on, the lowest number that makes it new. Then add it to `used_ids`. Marker clauses get their final id during the walk, as each is accepted, so a child built from its parent's id uses the parent's final id (`1~2(a)`). The rule covers schedule ids too (`S1~2`).
    - **Spans.** Each accepted marker's clause and each heading clause starts at its line's `start`. When the first of these lines starts after offset 0 and `text[:start].strip() != ""`, the text before it is a clause of its own: id `"p1"`, `number=None`, `heading=None`, `level=1`, `parent_id=None`. When that text is blank, the first clause starts at 0 instead. Each clause ends where the next begins, and the last ends at `len(text)`.
    - **Fields.** `number` is `marker.written` (`None` for a heading clause). `level` is 1 plus the number of ancestors. `numbering_source` is `NUMBERING_NUMBERS` on every clause.
    - Add the contract note (I11): input, output, no errors, no side effects. In the README, add `split_clauses` with the id forms (`5.1`, `7.1(a)(i)`, `S1`, `S1.2`, `p1`, `5.1~2`, and `4` for `Article IV`), the two `numbering_source` values, and the sentence "The clauses cover the whole text: each starts where the one before ends."
  - **Files:** `src/clause_tracer/ingest/clauses.py`, `src/clause_tracer/ingest/__init__.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_clauses.py`.
  - **Tests first:** in `test_clauses.py`, each building its document with `read_pasted_text`. A helper `ids(text)` returns the tuple of clause ids.
    - `test_heading_with_sub_clauses`: `"5. Charges and payment\n5.1 The Agency pays 25%.\n5.2 Invoices are paid in 60 days.\n"` gives ids `("5", "5.1", "5.2")`; clause `5` has `level == 1` and `parent_id is None`; `5.1` has `level == 2`, `parent_id == "5"` and `number == "5.1"`.
    - `test_number_inside_a_sentence_is_not_a_clause`: `"5.6 Payment is due within\n2.5 days of the invoice.\n5.7 Next."` gives `("5.6", "5.7")`.
    - `test_sub_clauses_without_a_heading_line`: `"1.1 One.\n1.2 Two.\n2.1 Three."` gives `("1.1", "1.2", "2.1")`, each with `level == 1` and `parent_id is None`.
    - `test_letter_i_after_h_is_a_letter`: lines `(a)` to `(i)`, each followed by `" x."`, give nine sibling clauses, the last with id `"(i)"` and `level == 1`.
    - `test_letter_i_after_a_is_a_roman_child`: `"1. Rules:\n(a) first:\n(i) one;\n(ii) two;\n(b) second."` gives `("1", "1(a)", "1(a)(i)", "1(a)(ii)", "1(b)")` with levels `(1, 2, 3, 3, 2)`.
    - `test_bracket_item_out_of_order_is_text`: `"1. Rules:\n(c) is not first."` gives `("1",)`.
    - `test_text_before_the_first_number`: `"Services Agreement\nThis Agreement is dated 5 November 2026.\n1. Start\n1.1 Now."` gives `("p1", "1", "1.1")`, and `p1` has `number is None`.
    - `test_blank_text_before_the_first_number_joins_it`: `"\n\n1. Start"` gives `("1",)` with `span == Span(start=0, end=10)`.
    - `test_schedule_restarts_numbering`: `"14. General\n14.1 Whole agreement.\nSchedule 1 · Services\n1. Build the site.\n2. Hosting is extra."` gives `("14", "14.1", "S1", "S1.1", "S1.2")`; `S1` has `number == "Schedule 1"` and `level == 1`; `S1.1` has `parent_id == "S1"`, `level == 2` and `number == "1"`.
    - `test_numbering_that_starts_again_gets_new_ids`: `"1. Definitions\n2. Term\n1. Definitions\n1.1 Words.\n2. Term"` gives `("1", "2", "1~2", "1.1", "2~2")`.
    - `test_list_inside_a_clause_does_not_swallow_what_follows`: `"5.1 Do:\n1. x\n2. y\n5.2 Next\n6. Then"` gives `("5.1", "1", "2", "5.2", "6")`.
    - `test_excerpt_can_start_at_any_number`: `"5.4 Invoices are paid in 60 days.\n5.5 Expenses."` gives `("5.4", "5.5")`.
    - `test_skipped_number_stays_in_the_clause_before`: `"1. One\n3. Three"` gives `("1",)`.
    - `test_markdown_symbols_do_not_hide_a_number`: `"## 1. Start\n**1.1** Now."` gives `("1", "1.1")`, and the document text is unchanged.
    - `test_clauses_cover_the_text`: for the text of `test_schedule_restarts_numbering`, the first span starts at 0, the last ends at `len(text)`, and each span starts where the one before ends.
    - `test_numbering_source_is_numbers`: every clause of `test_heading_with_sub_clauses` has `numbering_source == "numbers"`.
    - `test_blank_document_has_no_clauses`: a `Document` built by `dataclasses.replace(read_pasted_text("x"), text="  \n")` gives `()`.
    - `test_article_keywords`: `"Article I Definitions\n1.1 Words.\nArticle II Payment\n2.1 Invoices."` gives `("1", "1.1", "2", "2.1")`; clause `1` has `number == "Article I"`, and `1.1` has `parent_id == "1"`.
    - `test_closing_brackets`: `"3.1 The Developer will:\na) plan;\nb) write:\ni) templates;\nii) components."` gives `("3.1", "3.1(a)", "3.1(b)", "3.1(b)(i)", "3.1(b)(ii)")`, and `3.1(a)` has `number == "a)"`.
    - `test_bare_numbers_that_follow_on`: `"1 Definitions\n1.1 Words.\n2 Payment"` gives `("1", "1.1", "2")`.
    - `test_bare_number_never_starts_again`: `"1. One\n1.1 Words.\n1 Again"` gives `("1", "1.1")`.
    - `test_unnumbered_heading_after_a_blank_line`: `"1. Start\n1.1 Now.\n\nBackground\nThe Agency builds sites.\n\n2. Payment"` gives `("1", "1.1", "p1", "2")`; `p1` has `number is None`, `level == 1` and `parent_id is None`, and `2` has `parent_id is None`.
    - `test_heading_before_a_number_ends_the_bracket_list`: `"Parties\n(1) Brightline.\n(2) Karim.\nBackground\n(A) The Agency.\n1. Definitions"` gives `("p1", "(1)", "(2)", "p2", "(A)", "1")`, and `(A)` has `parent_id is None`.
    - `test_address_number_before_any_numbering_is_text`: `"Karim Benali\n27 Rue Didouche Mourad\nAlgiers (\"the Developer\").\n1. Definitions"` gives `("p1", "1")`.
    - `test_heading_inside_numbered_text_ends_the_bracket_list`: `"1. Start\n1.1 Now.\n\nBackground\n(A) The Agency."` gives `("1", "1.1", "p1", "(A)")`, and `(A)` has `parent_id is None`.
    - `test_short_line_inside_a_sentence_is_not_a_heading`: `"1.1 The Developer will deliver\nThe Website\nby the Delivery Date.\n1.2 Next."` gives `("1.1", "1.2")`.
    - `test_no_marker_is_one_paragraph_clause_for_now`: `"Just words."` gives `("p1",)` with `numbering_source == "paragraphs"`. S2-M3-T9 replaces this test.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clauses.py` reports 27 passed, and `scripts/check.sh` exits 0.
  - **Rules:** D2, I4, I11, S3, T1, [Spec 5](../spec.md#5-labelling-rules) (never guess: no text is dropped), [Spec 6.1](../spec.md#61-steps) step 2.
  - **Depends on:** S2-M2-T3, S2-M3-T1, S2-M3-T3

- [x] **S2-M3-T7: Clause headings**
  - **Build:** In `clauses.py`, fill `heading` for every clause that a DECIMAL, KEYWORD, SCHEDULE or BARE marker started. A clause that a PAREN marker started always has `heading=None`, so `(a) the Supplier` is not a heading. With `rest = line.text[marker.body_start:].strip(EMPHASIS_STRIP)` and `title = rest.strip(HEADING_STRIP)`, the heading is `title` when all four hold: `title != ""`; `len(rest) <= 100`; `rest[-1] not in ".;:,"`; and every later line inside the clause's span is blank. Otherwise it is `None`. So `5. Charges and payment` has the heading `Charges and payment`, and `1. Rules:` has none. A heading clause (S2-M3-T6) has the heading `line.text.strip(EMPHASIS_STRIP)`. The clause of text before the first clause keeps `heading=None`. Add the rule to the README.
  - **Files:** `src/clause_tracer/ingest/clauses.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_clauses.py`.
  - **Tests first:** in `test_clauses.py`: `test_numbered_heading_line_has_a_heading` (the text of `test_heading_with_sub_clauses`: clause `5` has `heading == "Charges and payment"`, and `5.1` and `5.2` have `heading is None`); `test_line_ending_in_a_colon_is_not_a_heading` (the text of `test_letter_i_after_a_is_a_roman_child`: every `heading is None`); `test_schedule_heading` (the text of `test_schedule_restarts_numbering`: `S1` has `heading == "Services"` and `14` has `heading == "General"`); `test_markdown_heading` (`"## 1. Start\n**1.1** Now."`: clause `1` has `heading == "Start"`); `test_long_line_is_not_a_heading` (`"1. " + "a" * 101 + "\n1.1 x."`: clause `1` has `heading is None`); `test_clause_with_more_lines_has_no_heading` (`"1. Payment\nThe Agency pays on time.\n1.1 Now."`: clause `1` has `heading is None`); `test_heading_clause_heading` (the text of `test_unnumbered_heading_after_a_blank_line`: `p1` has `heading == "Background"`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clauses.py` reports 34 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, S3, [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) (the `Clause` row).
  - **Depends on:** S2-M3-T6

- [x] **S2-M3-T8: Sentences inside each clause**
  - **Build:** In `clauses.py`, replace the one-sentence stand-in of S2-M3-T6. For a clause with span `[s, e)`, the body starts at `b`: the line start plus `marker.body_start`, or `s` for a clause with no number. The sentence boundaries are `s`, then `b + start` for every item of `sentence_starts(text[b:e])` except the first. Sentence `n` (counting from 1) runs from boundary `n` to boundary `n + 1`, the last to `e`, and has the id `f"{clause_id}.s{n}"`. So the clause number is always inside the first sentence, and the sentences cover the clause whatever NUPunkt returns. A missed break only makes a sentence longer. In the README, add the sentence id form (`5.1.s3`) and "A clause's sentences cover the whole clause: each starts where the one before ends."
  - **Files:** `src/clause_tracer/ingest/clauses.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_clauses.py`.
  - **Tests first:** in `test_clauses.py`: `test_sentences_cover_the_clause` (`"5.4 Invoices are paid within 60 days. Interest runs at 4% p.a. from the due date."` gives one clause with two sentences, ids `("5.4.s1", "5.4.s2")`, spans `(Span(start=0, end=38), Span(start=38, end=81))`); `test_the_number_stays_in_the_first_sentence` (`"5. Charges and payment"` gives one clause with one sentence over the whole span); `test_sentence_ids_count_from_one_in_each_clause` (`"1.1 One. Two.\n1.2 Three."` gives the sentence ids `("1.1.s1", "1.1.s2")` and `("1.2.s1",)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clauses.py` reports 37 passed, and `scripts/check.sh` exits 0.
  - **Rules:** B5 (one call returns clauses with their sentences), T1, S3, [ADR 0007](../adr/0007-document-reading-stack.md) (quote checks tolerate a missed split), [testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 4).
  - **Depends on:** S2-M3-T6, S2-M3-T4

- [x] **S2-M3-T9: Split a contract with no numbers by paragraph**
  - **Build:** In `clauses.py`, write `_split_paragraphs(text: str) -> tuple[Clause, ...]` in full. With the lines of `split_lines(text)`: when at least one blank line stands between two non-blank lines, a paragraph is a run of non-blank lines with no blank line inside it; otherwise every non-blank line is a paragraph. The first clause starts at 0, each later clause starts at the `start` of its paragraph's first line, each ends where the next begins, and the last ends at `len(text)`. Clause `n` (counting from 1) has id `f"p{n}"`, `number=None`, `heading=None`, `level=1`, `parent_id=None`, `numbering_source=NUMBERING_PARAGRAPHS`. Its sentences follow the rule of S2-M3-T8 with the body starting at the clause's own start.
  - **Files:** `src/clause_tracer/ingest/clauses.py`, `src/clause_tracer/ingest/README.md` (the paragraph rule), `src/clause_tracer/ingest/tests/test_clauses.py`.
  - **Tests first:** in `test_clauses.py`, replacing `test_no_marker_is_one_paragraph_clause_for_now`: `test_paragraphs_by_blank_lines` (`"First part\nwraps here.\n\nSecond part.\n\n\nThird."` gives `("p1", "p2", "p3")` with span starts `(0, 24, 39)` and every `numbering_source == "paragraphs"`); `test_paragraphs_by_lines_when_no_blank_line` (`"First.\nSecond.\nThird."` gives `("p1", "p2", "p3")`); `test_one_paragraph` (`"Just words."` gives `("p1",)` over the whole text); `test_paragraph_clauses_cover_the_text` (for the text of the first test: first start 0, last end `len(text)`, no gap); `test_paragraph_sentences` (`"One. Two."` gives sentences `("p1.s1", "p1.s2")`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clauses.py` reports 41 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T1, [Spec 6.1](../spec.md#61-steps) step 2 ("or paragraphs if there are no numbers"), [Spec 14.2](../spec.md#142-states-to-show) (the paragraph note).
  - **Depends on:** S2-M3-T8, S2-M3-T7

- [x] **S2-M3-T10: The owner's table, and invariant 4**
  - **Build:** Two test files and one strategy file. No change to the code under test. If a table row fails, stop and bring it to the owner: do not change the row, and do not change the splitter's rules without the owner (the README, "When the plan is wrong").
    - `src/clause_tracer/ingest/tests/strategies.py`: `MARKER_PREFIXES: tuple[str, ...] = ("", "", "1. ", "2. ", "3. ", "1.1 ", "1.2 ", "2.1 ", "(a) ", "(b) ", "(i) ", "(ii) ", "(A) ", "(1) ", "a) ", "ii) ", "Article II ", "Clause 3 ", "3 ", "Background\n", "Schedule 1 ", "## 1. ", "**1.1** ")` and `def contract_like_text() -> SearchStrategy[str]`, a `@composite`: draw a list of 1 to 12 lines, each `sampled_from(MARKER_PREFIXES)` joined to a `hazard_text()` from `clause_tracer.core.tests.strategies`; join the lines with separators each drawn from `("\n", "\n\n", "\r\n")`; `assume(text.strip() != "")`.
    - `src/clause_tracer/ingest/tests/test_clause_table.py`: `test_clause_split_table`, parametrised over the cases of `clause_split.toml`, loaded with `load_table(path, case_keys=frozenset({"id", "text", "numbering", "clauses"}), required=frozenset({"id", "text", "numbering", "clauses"}))`. For each case: `clauses = split_clauses(read_pasted_text(text))`; the number of clauses equals the number of expected rows; for each pair, `clause.id`, `clause.number or ""`, `clause.level`, `clause.parent_id or ""` and `clause.heading or ""` equal the row's values, `text[clause.span.start:clause.span.end].lstrip().startswith(row["starts_with"])`, and `clause.numbering_source == numbering`. Also `test_clause_split_table_has_rows` (at least 27 cases).
    - `src/clause_tracer/ingest/tests/test_clause_properties.py`, each for `contract_like_text()`, with `clauses = split_clauses(read_pasted_text(text))`: `test_clauses_cover_the_text` (at least one clause; the first span starts at 0; the last ends at `len(text)`; each starts where the one before ends; no span is empty); `test_invariant_4_sentences_join_up_to_the_clause` (for each clause: at least one sentence; the first starts at the clause's start; the last ends at its end; each starts where the one before ends; none is empty; sentence `n` has the id `f"{clause.id}.s{n}"`); `test_invariant_4_ids_are_the_same_on_a_second_read` (`split_clauses(read_pasted_text(text)) == split_clauses(read_text_file(text.encode(), kind=FileKind.TEXT, name="a.txt"))`); `test_ids_are_unique` (no clause id and no sentence id appears twice); `test_parents_come_first` (each `parent_id` is `None` or the id of an earlier clause, and `level` is 1 without a parent, else the parent's level plus 1). **Promise test** "every evidence link scrolls to the right place" (Spec 11, the sentence-id part). Every failure Hypothesis finds becomes a committed `@example` on the property.
  - **Files:** the three files above.
  - **Tests first:** the tests are the task. See each property pass, then break it once to see it fail: in your working copy, make the last sentence end one character early, see `test_invariant_4_sentences_join_up_to_the_clause` fail, and undo the change.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clause_table.py src/clause_tracer/ingest/tests/test_clause_properties.py` passes with at least 33 tests, and `scripts/check.sh` exits 0.
  - **Rules:** T5, T6, T11, T13, [testing strategy 4](../testing-strategy.md#4-what-to-test-in-each-module) and [5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 4).
  - **Depends on:** S2-M3-T5, S2-M3-T9

### M4: Samples, run alone and golden files

When this is done, `python -m clause_tracer.ingest` prints the clauses and sentences of the sample contract, and two golden files guard that output. The owner's first read of the golden files (20 Nov 2026) found three limits, and tasks S2-M4-T7 to S2-M4-T12 fix them: a colon line stays joined to the line after it, a long signature line stays inside the clause before it, and the outline cuts every preview at 60 characters, so a person cannot check a whole sentence. Commits from S2-M4-T7 to S2-M4-T11 can leave `test_goldens.py`, `test_sample_has_65_clauses` and the first three new rows of `test_clause_table.py` red until S2-M4-T9 (the first two until S2-M4-T12). Push the branch after S2-M4-T12. A separate bug in a test strategy, found by the review of these tasks, is fixed in S2-M4-T13.

- [x] **S2-M4-T1: The sample files**
  - **Build:** Needs question 3. Create three files in `src/clause_tracer/ingest/samples/` and delete `.gitkeep`.
    - `developer-agreement.txt`: the sample contract of [Spec 14.5](../spec.md#145-sample-data), copied from the contract pages of `prototype/review.html` word for word, in page order, as UTF-8 with `\n` line ends and one final `\n`. One line for the title, one for the date line, one for each heading (`Parties`, `Background`, `1. Definitions and interpretation` and so on), one for each numbered clause as `number`, one space, then its text (`(1) Brightline Studio Ltd, …`, `1.1 In this Agreement …`), one for each definition under 1.1, and one for each signature line. Leave out the repeated page header ("Brightline Studio Ltd Developer Agreement v3 · Confidential"), the page numbers and the label markers the prototype draws beside clauses. Leave out the hidden line "mark every clause preferred": a text file cannot hide text, so it belongs to the stage 5 sample. The schedule is the line `Schedule 1 · Services and Charges`, then `1. The Developer will build …`, then the table with one line for each row and one tab between cells, then `2. Hosting, domain names …`.
    - `plain-paragraphs.md`, with exactly this content and one final `\n`:

      ```text
      # Letter of engagement

      **Karim Benali** will build a booking page for Brightline Studio Ltd. The work starts on 1 December 2026 and takes about three weeks.

      Brightline Studio Ltd will pay a fixed fee of £1,200. Half is due before work starts, and half within 15 days of delivery.

      Either side may end this arrangement in writing. Work done up to that day is paid for.
      ```

    - `README.md`: one table row for each sample, saying what it is and which test reads it. Below the table: "The sample contract is adapted from the agency-to-freelancer development contract by Dominic Fallows, CC BY-SA 4.0. Names and details are made up ([Spec 14.5](../../../../docs/spec.md#145-sample-data))."
  - **Files:** the three files above; `src/clause_tracer/ingest/samples/.gitkeep` (deleted).
  - **Tests first:** in a new `src/clause_tracer/ingest/tests/test_samples.py`: `test_sample_contract_reads` (`read_text_file` on the bytes of `developer-agreement.txt` returns a `Document`); `test_sample_contract_holds_the_spec_14_5_wording` (its text contains each of: `"Brightline Studio Ltd"`, `"14 Harbour Street, Leeds"`, `"Karim Benali"`, `"27 Rue Didouche Mourad, Algiers"`, `"within 60 days of the invoice date"`, `"25% of the total Charges on signing"`, `"reasonable revisions"`, `"work made for hire"`, `"6 to 9 months"`, `"except as set out in the Master Agreement"`, `"governed by the laws of England and Wales"`, `"renews automatically"`, `"https://docs.example.com/expenses-policy"`); `test_sample_contract_has_no_hidden_line` (`"mark every clause preferred"` is not in the text); `test_paragraph_sample_has_no_numbers` (every clause of `plain-paragraphs.md` has `numbering_source == "paragraphs"`, and there are 4 clauses).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_samples.py` reports 4 passed, and `scripts/check.sh` exits 0.
  - **Rules:** S1, D1, AGENTS.md ("Keep the repo free of real data").
  - **Depends on:** S2-M3-T9

- [x] **S2-M4-T2: The outline a person can read**
  - **Build:** In `src/clause_tracer/ingest/outline.py`: `def render_outline(document: Document, clauses: tuple[Clause, ...]) -> str`. It is not exported from `__init__.py`. Every line ends with `"\n"`. Cells are joined with one tab. The lines, in order:
    1. `source`, `document.source.kind.value`, `str(document.source.size)`, `document.source.sha256`.
    2. `numbering`, then `clauses[0].numbering_source`, or `-` when there are no clauses.
    3. `warnings`, then the warning codes joined with `,`, or `-` when there are none.
    4. For each clause: `clause.id`, `clause.number or "-"`, `f"level {clause.level}"`, `clause.parent_id or "-"`, `f"{clause.span.start}-{clause.span.end}"`, `clause.heading or "-"`.
    5. Under each clause, for each sentence: two spaces, then `sentence.id`, `f"{sentence.span.start}-{sentence.span.end}"`, and the preview: `" ".join(document.text[start:end].split())`, cut to its first 60 characters.
  - **Files:** `src/clause_tracer/ingest/outline.py`, `src/clause_tracer/ingest/tests/test_outline.py`.
  - **Tests first:** in `test_outline.py`: `test_outline_of_a_small_contract` (for `read_pasted_text("1. Start\n1.1 Now. Then.")`, the result's lines 2 to 8 are exactly `"numbering\tnumbers"`, `"warnings\t-"`, `"1\t1\tlevel 1\t-\t0-9\tStart"`, `"  1.s1\t0-9\t1. Start"`, `"1.1\t1.1\tlevel 2\t1\t9-23\t-"`, `"  1.1.s1\t9-18\t1.1 Now."`, `"  1.1.s2\t18-23\tThen."`, and line 1 starts with `"source\tpasted\t23\t"`); `test_preview_is_cut_at_60_characters` (a one-sentence clause of 200 `"a"` characters gives a preview of exactly 60 characters); `test_outline_with_no_clauses` (`render_outline(document, ())` has the line `"numbering\t-"`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_outline.py` reports 3 passed, and `scripts/check.sh` exits 0.
  - **Rules:** S1 (an output you can open and read), T1.
  - **Depends on:** S2-M3-T9

- [x] **S2-M4-T3: Run `ingest` alone**
  - **Build:** Rewrite `src/clause_tracer/ingest/__main__.py`, following `src/clause_tracer/core/__main__.py`. `DEFAULT_INPUT = Path(__file__).parent / "samples" / "developer-agreement.txt"`. `EXIT_INPUT_FILE = 3`. `def main(argv: list[str] | None = None) -> int`: one argument, `--input` (a `Path`, default `DEFAULT_INPUT`). The kind is `FileKind.MARKDOWN` when the path's suffix, in lower case, is `.md`, else `FileKind.TEXT`. Read the bytes; on `OSError` print `f"clause_tracer.ingest: cannot read {path}"` to standard error and return 3. Call `read_text_file(data, kind=kind, name=path.name)`; on `InputError as error` print `f"clause_tracer.ingest: {error.code}"` to standard error and return 3. Print `render_outline(document, split_clauses(document))` to standard output with `end=""` and return 0. This file is the only place in `ingest` that reads a file. In the README, replace "Run alone" with the command, the `--input` flag, the three exit paths and one line on the outline's columns.
  - **Files:** `src/clause_tracer/ingest/__main__.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_smoke.py`.
  - **Tests first:** in `test_smoke.py`, keeping `test_main_returns_zero` (now `main([]) == 0`): `test_default_run_prints_the_sample` (with `capsys`: `main([])` prints a first line that starts with `"source\ttext\t"` and a line `"numbering\tnumbers"`); `test_markdown_input` (`main(["--input", str(samples / "plain-paragraphs.md")])` returns 0 and prints `"numbering\tparagraphs"`); `test_sample_has_64_clauses` (`split_clauses(read_text_file(DEFAULT_INPUT.read_bytes(), kind=FileKind.TEXT, name=DEFAULT_INPUT.name))` has 64 clauses, the count recorded in [system design 4.2](../system-design.md#42-the-offset-chain) and the copy deck; if it is not 64, stop and bring it to the owner); `test_missing_file_exits_3` (a path in `tmp_path` that does not exist: returns 3, standard error contains `"cannot read"`, standard output is empty); `test_not_utf8_exits_3` (a file holding `b"caf\xe9"`: returns 3, standard error is `"clause_tracer.ingest: not_utf8\n"`); `test_empty_file_exits_3` (an empty file: returns 3, standard error is `"clause_tracer.ingest: empty_input\n"`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_smoke.py` reports 7 passed, `.venv/bin/uv run python -m clause_tracer.ingest` prints the outline and exits 0, and `scripts/check.sh` exits 0.
  - **Rules:** S1, S2, T2 (the file is read only at the edge), I12, [system design 6.2](../system-design.md#62-the-command-line).
  - **Depends on:** S2-M4-T1, S2-M4-T2

- [x] **S2-M4-T4: The first golden files**
  - **Build:** Write the test file of S2-M4-T5 in your working copy, but do not commit it in this task. Run `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_goldens.py` and see both tests fail with "is missing. Run pytest with --update-goldens". Then run the named command, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_goldens.py --update-goldens`. It writes `src/clause_tracer/ingest/tests/goldens/developer-agreement.outline.txt` and `src/clause_tracer/ingest/tests/goldens/plain-paragraphs.outline.txt`. Commit only those two files and the plan tick, and say in the commit body that `--update-goldens` made them.
  - **Files:** the two golden files.
  - **Tests first:** None. The red test above is the check.
  - **Done when:** The two files exist, the commit holds no `.py` file, and `scripts/check.sh` exits 0.
  - **Rules:** T11, [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest) (golden files only by the named command, in a commit of their own).
  - **Depends on:** S2-M4-T3, S2-M1-T3

- [x] **S2-M4-T5: The golden-file tests**
  - **Build:** `src/clause_tracer/ingest/tests/test_goldens.py` with `SAMPLES = Path(__file__).parent.parent / "samples"` and `GOLDENS = Path(__file__).parent / "goldens"`, and one parametrised test `test_outline_matches_its_golden(check_golden, sample, kind)` over `("developer-agreement.txt", FileKind.TEXT)` and `("plain-paragraphs.md", FileKind.MARKDOWN)`: read the sample's bytes, `document = read_text_file(data, kind=kind, name=sample)`, `actual = render_outline(document, split_clauses(document))`, then `check_golden(GOLDENS / (Path(sample).stem + ".outline.txt"), actual)`. In the README, add a "Golden files" part: the two files, and "Regenerate them only with `--update-goldens`, in a commit of their own, and ask the owner to read the diff."
  - **Files:** `src/clause_tracer/ingest/tests/test_goldens.py`, `src/clause_tracer/ingest/README.md`.
  - **Tests first:** the test is the task. It was seen to fail in S2-M4-T4.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_goldens.py` reports 2 passed, and `scripts/check.sh` exits 0.
  - **Rules:** T11, [testing strategy 3](../testing-strategy.md#3-five-layers) (layer 2).
  - **Depends on:** S2-M4-T4

- [x] **S2-M4-T7: Signature rows and the new clause count (Owner)**
  - **Build:** Owner only. The rows below are the planner's draft of what the owner decided on 20 Nov 2026 (question 13). Every row is made of real lines of `developer-agreement.txt` (lines 65 to 71), and rows 2, 3 and 5 change only the first word or words of the signature line: a line that opens with `Signed`, `Executed` or `In witness whereof`, with a blank line before it, starts a clause of its own whatever its length. Read them, change any value that is wrong, and add them to the end of `src/clause_tracer/ingest/tests/tables/clause_split.toml`. The block is indented by 4 spaces here: remove those 4 spaces from every line when you copy it, or the `text` values get leading spaces. In the same step, in `src/clause_tracer/ingest/tests/test_smoke.py`, rename `test_sample_has_64_clauses` to `test_sample_has_65_clauses` and change `== 64` to `== 65`: the sample then has one clause more, because the signature line of Brightline Studio Ltd (73 characters) becomes the clause `p4` and `Signed by Karim Benali` becomes `p5`. A trial of the rules gave 65 clauses and 75 sentences (it was 64 and 74).

    ```toml
    # Lines 65 to 71 of developer-agreement.txt: a signature line opens a clause whatever its length (question 13, 20 Nov 2026).
    [[case]]
    id = "signature-line-over-60-characters-starts-a-clause"
    text = """
    14.5 Notices must be in writing and sent by email to the addresses each party gives the other, with a copy to Ms Jones at the Developer's address.
    14.6 This Agreement is governed by the laws of England and Wales.

    Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director

    Signed by Karim Benali
    Schedule 1 · Services and Charges"""
    numbering = "numbers"
    clauses = [
      { id = "14.5", number = "14.5", level = 1, parent = "", heading = "", starts_with = "14.5 Notices must be in w" },
      { id = "14.6", number = "14.6", level = 1, parent = "", heading = "", starts_with = "14.6 This Agreement is gov" },
      { id = "p1", number = "", level = 1, parent = "", heading = "Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director", starts_with = "Signed for and on behalf of" },
      { id = "p2", number = "", level = 1, parent = "", heading = "Signed by Karim Benali", starts_with = "Signed by Karim Benali" },
      { id = "S1", number = "Schedule 1", level = 1, parent = "", heading = "Services and Charges", starts_with = "Schedule 1 · Services" },
    ]

    # The sample's signature line with its first word changed to Executed.
    [[case]]
    id = "executed-line-starts-a-clause"
    text = """
    14.6 This Agreement is governed by the laws of England and Wales.

    Executed as a deed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director"""
    numbering = "numbers"
    clauses = [
      { id = "14.6", number = "14.6", level = 1, parent = "", heading = "", starts_with = "14.6 This Agreement is gov" },
      { id = "p1", number = "", level = 1, parent = "", heading = "Executed as a deed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director", starts_with = "Executed as a deed for and" },
    ]

    # The sample's signature line with its first words changed to In witness whereof.
    [[case]]
    id = "in-witness-whereof-line-starts-a-clause"
    text = """
    14.6 This Agreement is governed by the laws of England and Wales.

    In witness whereof, for and on behalf of Brightline Studio Ltd by Sarah Jones, Director"""
    numbering = "numbers"
    clauses = [
      { id = "14.6", number = "14.6", level = 1, parent = "", heading = "", starts_with = "14.6 This Agreement is gov" },
      { id = "p1", number = "", level = 1, parent = "", heading = "In witness whereof, for and on behalf of Brightline Studio Ltd by Sarah Jones, Director", starts_with = "In witness whereof, for and" },
    ]

    # The sample's own lines with the blank line between them removed: with text right before it, the long Signed line is not a heading.
    [[case]]
    id = "signed-line-with-no-blank-line-before-it-stays-in-the-clause"
    text = """
    14.6 This Agreement is governed by the laws of England and Wales.
    Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director"""
    numbering = "numbers"
    clauses = [
      { id = "14.6", number = "14.6", level = 1, parent = "", heading = "", starts_with = "14.6 This Agreement is gov" },
    ]

    # The sample's signature line with its first word changed to Signedness, which is not the word Signed.
    [[case]]
    id = "a-word-that-only-starts-like-signed-is-text"
    text = """
    14.6 This Agreement is governed by the laws of England and Wales.

    Signedness for and on behalf of Brightline Studio Ltd by Sarah Jones, Director"""
    numbering = "numbers"
    clauses = [
      { id = "14.6", number = "14.6", level = 1, parent = "", heading = "", starts_with = "14.6 This Agreement is gov" },
    ]
    ```

    The draft has one known limit, which the owner accepts by adding the rows: a sentence that opens with `Executed` or `Signed` after a blank line, such as `Executed copies must be kept by both parties.`, also becomes a clause of its own.
  - **Files:** `src/clause_tracer/ingest/tests/tables/clause_split.toml`, `src/clause_tracer/ingest/tests/test_smoke.py`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and the count and said so. `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clause_table.py` then reports 33 tests, with 3 failing (the first three new rows) until S2-M4-T9, and `test_sample_has_65_clauses` fails until S2-M4-T9.
  - **Rules:** T11.
  - **Depends on:** S2-M4-T5

- [ ] **S2-M4-T8: A colon line ends a sentence**
  - **Build:** Decided by the owner on 20 Nov 2026 (question 12). In `src/clause_tracer/ingest/_sentences.py`, add `def colon_line_starts(text: str) -> tuple[int, ...]` and change `sentence_starts` to return `tuple(sorted(set(library_starts) | set(colon_line_starts(text))))`, where `library_starts` is what the NUPunkt call returned before. The file stays the only one that imports `nupunkt` (B4).
    - `colon_line_starts` takes `lines = split_lines(text)` (from `clause_tracer.ingest._lines`). For each index `i` from 0 to `len(lines) - 2`: the line is a colon line when `lines[i].text.rstrip(" \t\u00a0\ufeff*_")` ends with `":"` or `"："` (U+FF1A). Write the characters as these escapes in the code, not as pasted characters. When it is a colon line and `lines[i + 1]` is not blank (`is_blank`), `lines[i + 1].start` is a start. It returns the starts in order. A colon line with no line after it, or with a blank line after it, gives no start. A colon in the middle of a line gives no start.
    - Update the module docstring: sentence starts are the NUPunkt starts plus the starts after colon lines.
    - In `src/clause_tracer/ingest/README.md`, add a new paragraph after the paragraph that ends "The clause number stays in the first sentence.": "A line that ends in a colon ends a sentence, so a lead-in line such as `1.1 In this Agreement the following words have these meanings:` is a sentence of its own. A hard-wrapped line that ends in a colon in the middle of a sentence also breaks there: a known limit." In [system design 4.2](../system-design.md#42-the-offset-chain), after the sentence about `Markdown symbols`, add the same sentence.
  - **Files:** `src/clause_tracer/ingest/_sentences.py`, `src/clause_tracer/ingest/README.md`, `docs/system-design.md`, `src/clause_tracer/ingest/tests/test_sentences.py`, `src/clause_tracer/ingest/tests/test_clauses.py`.
  - **Tests first:** in `test_sentences.py`: `test_colon_line_starts`, parametrised over (`text`, `expected`): `("Meanings:\nCharges means fees.", (10,))`, `("Meanings: \t\nCharges.", (12,))`, `("Meanings：\nNext", (10,))`, `("Meanings:\r\nNext", (11,))`, `("Meanings:\u00a0\nNext", (11,))`, `("**Terms:**\nNext", (11,))`, `("Meanings:\n\nNext", ())`, `("Meanings:\n", ())`, `("Note: this\nstays", ())`; `test_colon_line_is_a_sentence_start` (`'In this Agreement the following words have these meanings:\n"Charges" means the fees set out in Schedule 1.'` gives `(0, 59)`); `test_colon_start_joins_the_library_starts` (`"One. Two:\nThree."` gives `(0, 5, 10)`). In `test_clauses.py`: `test_colon_line_splits_the_lead_in_from_the_list` (`'1.1 In this Agreement the following words have these meanings:\n"Charges" means the fees.\n"Services" means the work.'` gives one clause `1.1` with sentence ids `("1.1.s1", "1.1.s2", "1.1.s3")` and spans `(Span(start=0, end=63), Span(start=63, end=89), Span(start=89, end=115))`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_sentences.py` reports 15 passed, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clauses.py` reports 46 passed, and `scripts/check.sh` exits 0 except for `test_goldens.py`, `test_sample_has_65_clauses` and the first three new rows of `test_clause_table.py`, which pass after S2-M4-T9 (the first two after S2-M4-T12).
  - **Rules:** B4, I4, T1, S3, [Spec 5](../spec.md#5-labelling-rules) (a missed break only makes a sentence longer; this rule removes one kind of missed break, and adds a break after a hard-wrapped line that ends in a colon, a known limit), [system design 4.2](../system-design.md#42-the-offset-chain).
  - **Depends on:** S2-M4-T5

- [ ] **S2-M4-T9: A signature line starts a clause**
  - **Build:** Decided by the owner on 20 Nov 2026 (question 13). In `src/clause_tracer/ingest/_markers.py`: `SIGNATURE_OPENERS: Final[tuple[str, ...]] = ("signed", "executed", "in witness whereof")`, `SIGNATURE_BOUNDARY: Final[str] = " :,;.*_"`, and `def is_signature_line(line_text: str) -> bool`. With `words = " ".join(line_text.strip(EMPHASIS_STRIP).split()).casefold()`, it is true when for some `opener` in `SIGNATURE_OPENERS` `words.startswith(opener)` holds and either `len(words) == len(opener)` or `words[len(opener)] in SIGNATURE_BOUNDARY`. Then change `is_heading_line`: after the `stripped == ""` check, add `if "\t" in line_text: return False` and then `if is_signature_line(line_text): return True`, before the length, word and capital-letter tests. So a table row with tabs that opens with `Signed` is never a heading, as before. Nothing else changes: `clauses.py` still asks for a blank line before the line, or a marker line after it (S2-M3-T6), so a long line that opens with `Signed` and has a text line before it stays in its clause. A later language adds its own openers to the same tuple.
    - In `src/clause_tracer/ingest/README.md`, at the end of the paragraph that begins "A numbered clause has a heading", add: "A line that opens with `Signed`, `Executed` or `In witness whereof` is a heading whatever its length." In [system design 4.2](../system-design.md#42-the-offset-chain), add the same sentence to the one about short unnumbered lines. In this plan, in the last bullet of section 2 ("Scope"), the one that begins "Numbering styles this stage does not read", change the end so that it reads: "and unnumbered headings longer than 8 words or 60 characters, except a line that opens with `Signed`, `Executed` or `In witness whereof`."
  - **Files:** `src/clause_tracer/ingest/_markers.py`, `src/clause_tracer/ingest/README.md`, `docs/system-design.md`, `docs/plans/stage-02-ingest.md`, `src/clause_tracer/ingest/tests/test_markers.py`, `src/clause_tracer/ingest/tests/test_clauses.py`.
  - **Tests first:** in `test_markers.py`, add these rows to the parametrised `test_is_heading_line`: `("Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director", True)`, `("Executed as a deed by Brightline Studio Ltd acting by a director in the presence of a witness", True)`, `("In witness whereof the parties have signed this Agreement on the date at the top", True)`, `("**Signed** by Karim Benali and returned to the Agency by post within three days", True)`, `("SIGNED BY BOTH PARTIES ON THE DATE AT THE TOP OF THIS AGREEMENT IN TWO COPIES", True)`, `("Signedness of the copies is checked by the Agency in person at the office", False)`, `("The signed copy is kept by the Agency in person at the office of the Developer", False)`, `("Signed\tby\tKarim Benali", False)`. In `test_clauses.py`: `test_signature_line_starts_its_own_clause` (`"14.6 Governed by English law.\n\nSigned for and on behalf of Brightline Studio Ltd by Sarah Jones, Director\n\nSigned by Karim Benali"` gives ids `("14.6", "p1", "p2")`, and `p1` has `heading == "Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director"`); `test_signed_line_after_a_text_line_stays_in_the_clause` (`"9.1 The parties agree.\nSigned by both parties on the date at the top of this Agreement, in two copies."` gives `("9.1",)`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_markers.py` reports 62 passed, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clauses.py` reports 48 passed, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clause_table.py src/clause_tracer/ingest/tests/test_smoke.py` passes, and `scripts/check.sh` exits 0 except for `test_goldens.py` and `test_sample_has_65_clauses`, which fail until S2-M4-T12.
  - **Rules:** T1, T11 (the rows of S2-M4-T7 were written first), S3, [Spec 5](../spec.md#5-labelling-rules) (never guess: a signature block is not part of the clause before it), [system design 4.2](../system-design.md#42-the-offset-chain).
  - **Depends on:** S2-M4-T7, S2-M4-T8

- [ ] **S2-M4-T10: Show whole sentences with `--full`**
  - **Build:** Decided by the owner on 20 Nov 2026 (question 14). In `src/clause_tracer/ingest/outline.py`, change the signature to `def render_outline(document: Document, clauses: tuple[Clause, ...], *, full: bool = False) -> str` and `_preview` to `def _preview(text: str, start: int, end: int, *, full: bool) -> str`. When `full` is true the preview is the whole `" ".join(text[start:end].split())`, with no cut at 60 characters. The default keeps the cut, so the golden files do not change. In `src/clause_tracer/ingest/__main__.py`, add `parser.add_argument("--full", action="store_true", help="print each sentence in full")` and call `render_outline(document, split_clauses(document), full=args.full)`. The flag writes to standard output only. In the README, in the "Run alone" part, add the `--full` flag and "The golden files always use the cut preview."
  - **Files:** `src/clause_tracer/ingest/outline.py`, `src/clause_tracer/ingest/__main__.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_outline.py`, `src/clause_tracer/ingest/tests/test_smoke.py`.
  - **Tests first:** in `test_outline.py`: `test_full_outline_does_not_cut_the_preview` (for `read_pasted_text("a" * 200)`, the last line of `render_outline(document, split_clauses(document), full=True)` is `"  p1.s1\t0-200\t" + "a" * 200`). In `test_smoke.py`: `test_full_flag_prints_whole_sentences` (with `capsys`: `main(["--full"])` returns 0 and the output contains the text `5.5 The Agency will repay reasonable expenses that it has approved in writing before they are incurred, as set out in its expenses policy at https://docs.example.com/expenses-policy.`); `test_without_the_flag_the_preview_is_cut` (`main([])` returns 0 and the output does not hold `expenses-policy`).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_outline.py` reports 4 passed, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_smoke.py` reports 9 passed, and `scripts/check.sh` exits 0 except for the red tests named in the M4 introduction.
  - **Rules:** S1 (an output you can open and read), T1, I12.
  - **Depends on:** S2-M4-T3

- [ ] **S2-M4-T11: The clause count is 65**
  - **Build:** Change `64 clauses` to `65 clauses` in every place that states the count for the sample contract. The known places are: `docs/system-design.md` (section 4.2, "On the sample contract this gives 64 clauses"); `docs/ux-copy.md` (the "Load file dialog", "Log lines" and "Reading log" rows, and the "Facts" row with `Clauses: 64`, including "Matched 12 of 64 clauses to positions" and "Matched all 64 clauses to 11 positions"); `prototype/new-review.html`, `prototype/running.html` (every line, including the script array near line 342) and `prototype/states.html`; and `prototype/contract-check.html`, where `<dt>Clauses</dt><dd>64,` becomes `65,`. Then find any other place: `grep -rnE "\b64\b" docs prototype src --include=*.md --include=*.html --include=*.py | grep -i clause | grep -v "docs/plans/stage-02-ingest.md"`. In the change log of this plan, the new row (section 8) says that question 6 and the 19 Nov 2026 row that gives 64 keep it, because they record the count of that day. Run `.venv/bin/uv run python scripts/copy_lint.py`, then the two-minute check of [ux-copy 1.1](../ux-copy.md#11-signs-of-machine-made-text) on the changed rows.
  - **Files:** `docs/system-design.md`, `docs/ux-copy.md`, `prototype/new-review.html`, `prototype/running.html`, `prototype/states.html`, `prototype/contract-check.html`, `docs/plans/stage-02-ingest.md`.
  - **Tests first:** None. The check is the search command above: it prints no line that says 64 for the sample. The lines of this plan file are not checked, because its history keeps 64.
  - **Done when:** The search prints no such line, `scripts/copy_lint.py` exits 0, the prototype pages named above show 65 when opened (preview server `prototype`, http://localhost:8767), and `scripts/check.sh` exits 0 except for the red tests named in the M4 introduction.
  - **Rules:** [AGENTS.md](../../AGENTS.md) ("The deck, the page and the spec must match"), [WRITING_DOCS.md](../../WRITING_DOCS.md) section 9.
  - **Depends on:** S2-M4-T9

- [ ] **S2-M4-T12: Regenerate the developer-agreement golden file**
  - **Build:** Run `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_goldens.py` and see the developer-agreement test fail and the plain-paragraphs test pass. Then run the named command, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_goldens.py --update-goldens`. Commit only `src/clause_tracer/ingest/tests/goldens/developer-agreement.outline.txt` and the plan tick, and say in the commit body that `--update-goldens` made it. The diff must hold exactly these changes, and nothing else: (1) clause `1.1` gains a sentence: `1.1.s1` runs 659-722 (the lead-in line), the new `1.1.s2` runs 722-770 and starts `"Charges" means`, and the old `1.1.s2` to `1.1.s5` become `1.1.s3` to `1.1.s6` with the same spans; (2) clause `14.6` keeps only `14.6.s1`, 5497-5564; (3) a new clause `p4`, level 1, span 5564-5640, with the heading `Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director` and one sentence `p4.s1`, 5564-5640; (4) the old clause `p4` becomes `p5`, span 5640-5663, with `p5.s1`. The file then holds 65 clauses and 75 sentences. If the diff holds anything else, stop and bring it to the owner. The plain-paragraphs file does not change.
  - **Files:** `src/clause_tracer/ingest/tests/goldens/developer-agreement.outline.txt`.
  - **Tests first:** None. The red test above is the check.
  - **Done when:** The commit holds no `.py` file, one golden file and the plan file, the diff is the four changes above, and `scripts/check.sh` exits 0 with no red test left.
  - **Rules:** T11, [testing strategy 10](../testing-strategy.md#10-keeping-agent-written-tests-honest) (golden files only by the named command, in a commit of their own).
  - **Depends on:** S2-M4-T8, S2-M4-T9

- [ ] **S2-M4-T13: A blank text is never a usable contract-like text**
  - **Build:** In `src/clause_tracer/ingest/tests/strategies.py`, add `from clause_tracer.ingest._lines import is_blank_text` and `def is_usable_text(text: str) -> bool`, which returns `not is_blank_text(text)`. In `contract_like_text`, replace `assume(text.strip() != "")` with `assume(is_usable_text(text))`. The old guard let a text of only a byte-order mark through, because `str.strip()` keeps U+FEFF, and `read_pasted_text` then raised `EmptyInputError`. A run of 1,500 Hypothesis examples hit it twice (`test_invariant_4_sentences_join_up_to_the_clause` and `test_invariant_4_ids_are_the_same_on_a_second_read`); the default 100 examples did not. The nightly 2,000-example profile of stage 5 would. No other file changes.
  - **Files:** `src/clause_tracer/ingest/tests/strategies.py`, `src/clause_tracer/ingest/tests/test_strategies.py`.
  - **Tests first:** in a new `test_strategies.py`: `test_is_usable_text`, parametrised over (`text`, `expected`): `("\ufeff", False)`, `("  \n", False)`, `("", False)`, `("a", True)`, `("\ufeff1. Start", True)`. See the first row fail before the change: write the test first, with `is_usable_text` defined as `return text.strip() != ""`, and see the byte-order-mark row fail; then change it to the final form.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_strategies.py` reports 5 passed, `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_clause_properties.py` passes, and `scripts/check.sh` exits 0 except for the red tests named in the M4 introduction.
  - **Rules:** T1, T5, [testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 4).
  - **Depends on:** S2-M3-T10

- [ ] **S2-M4-T6: Read the golden files (Owner)**
  - **Build:** Owner only. Read `developer-agreement.outline.txt` and `plain-paragraphs.outline.txt` against the two samples. Each clause should start where a reader would start it, and each sentence break should be one a reader would accept or a missed break, never a break inside a word or a number. Say whether they are right. A wrong split is a splitter bug or a new row for the clause-splitter table, never a hand edit of a golden file. The owner read the first files on 20 Nov 2026 and found the three limits that S2-M4-T7 to S2-M4-T12 fix. Read the files again after S2-M4-T12. To see whole sentences, run `.venv/bin/uv run python -m clause_tracer.ingest --full` (S2-M4-T10), because the golden files still cut each preview at 60 characters.
  - **Files:** None.
  - **Tests first:** None.
  - **Done when:** The owner has read both files again after S2-M4-T12 and said so.
  - **Rules:** T11.
  - **Depends on:** S2-M4-T4, S2-M4-T10, S2-M4-T12

### M5: The match key, the language warning and the close

When this is done, `core` builds match keys, invariant 2 holds, a contract that does not look English carries a warning, and the stage is closed.

- [x] **S2-M5-T1: Match-fold table (Owner)**
  - **Build:** Owner only. Needs question 2. Fill `src/clause_tracer/core/tests/tables/match_fold.toml`. Each `[[case]]` has `id`, `text` and `expected` (the folded text). Cover at least: capital letters; `ß`; the ligature `ﬁ`; curly quotes; a soft hyphen inside a word; a zero-width space inside a word; a no-break space; a run of spaces and line breaks; an en dash between two numbers.
  - **Files:** `src/clause_tracer/core/tests/tables/match_fold.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** T11.
  - **Depends on:** S2-M1-T4

- [ ] **S2-M5-T2: The match key**
  - **Build:** Needs question 2. In a new `src/clause_tracer/core/match_fold.py`: `def fold_for_matching(text: str) -> MatchKey`, exported from `core`. It uses only the standard library (`unicodedata`).
    - **Pass 1,** for each character `c` at index `i`: when `c` is one of the dropped characters (U+00AD, U+200B, U+200C, U+200D, U+2060, U+FEFF, U+202A to U+202E, U+2066 to U+2069), emit nothing. Otherwise take `unicodedata.normalize("NFKC", c).casefold()` and, for each character `d` of it: `‘ ’ ‚ ‛` become `'`; `“ ” „ ‟` become `"`; U+2010 to U+2015 and U+2212 become `-`; emit `(d, i)`.
    - **Pass 2,** over the emitted pairs: a run of pairs whose character has `isspace()` true becomes one `" "` with the index of the run's first pair. Every other pair is kept.
    - `MatchKey.text` is the kept characters joined. `MatchKey.to_canonical` has one entry for each folded character, the index of the character it came from, plus a last entry equal to `len(text)`.
    - In `src/clause_tracer/core/README.md`, add `fold_for_matching` under "Functions", and one line: "Two folds: `fold_for_quote_check` is the narrow Spec 2 fold that confirms a quote; `fold_for_matching` is the wide fold for finding names, terms and keywords. A quote is never confirmed on the wide fold."
  - **Files:** `src/clause_tracer/core/match_fold.py`, `src/clause_tracer/core/__init__.py`, `src/clause_tracer/core/README.md`, `src/clause_tracer/core/tests/test_match_fold.py`.
  - **Tests first:** in `test_match_fold.py`: `test_sharp_s_becomes_two_letters` (`"Straße"` gives text `"strasse"` and `to_canonical == (0, 1, 2, 3, 4, 4, 5, 6)`); `test_ligature_is_two_letters_from_one` (`"ﬁne"` gives `"fine"` and `(0, 0, 1, 2, 3)`); `test_soft_hyphen_is_dropped` (`"A\u00adB"` gives `"ab"` and `(0, 2, 3)`); `test_quotes_and_spaces` (`"“Hi”  \n there"` gives `'"hi" there'`); `test_empty_text` (`MatchKey(text="", to_canonical=(0,))`); `test_match_fold_table`, parametrised over `match_fold.toml` (case keys and required keys `id`, `text`, `expected`): `fold_for_matching(text).text == expected`; `test_match_fold_table_has_rows` (at least 9 cases); the property `test_map_shape` (for `hazard_text()`: `len(to_canonical) == len(key.text) + 1`; the entries never go down; the last is `len(text)`; every other entry is less than `len(text)`); the property `test_invariant_2_folding_a_slice_equals_slicing_the_fold` (for `hazard_text()` and any `0 <= a <= b <= len(text)`: with `key = fold_for_matching(text)`, `ka` the first index `i` with `key.to_canonical[i] >= a` and `kb` the first with `key.to_canonical[i] >= b`, `fold_for_matching(text[a:b]).text.strip(" ") == key.text[ka:kb].strip(" ")`. The `strip` is needed because a run of spaces cut by the slice folds to one space on one side only). Every failure Hypothesis finds becomes a committed `@example`. If the invariant fails on an input the rules above allow, stop and bring it to the owner.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/core/tests/test_match_fold.py` passes with at least 17 tests, and `scripts/check.sh` exits 0 (the 95% floor for `core` holds).
  - **Rules:** T1, T6, T11, T13, [system design 4.2](../system-design.md#42-the-offset-chain), [testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants) (invariant 2, and the `ß` trap).
  - **Depends on:** S2-M5-T1

- [x] **S2-M5-T3: Not-English table (Owner)**
  - **Build:** Owner only. Needs question 1. Fill `src/clause_tracer/ingest/tests/tables/not_english.toml`. Each `[[case]]` has `id`, `text` and `warned` (a boolean). Cover at least: an English contract paragraph; a French one; an Arabic one; a short English sentence; a short French sentence; a text under 10 words; an English contract with a French schedule about a third of its length; a table with few words. The answers are what a reader expects under the rule of S2-M5-T4, not Lingua's output.
  - **Files:** `src/clause_tracer/ingest/tests/tables/not_english.toml`.
  - **Tests first:** None. The owner's values are the expected answers.
  - **Done when:** The owner has written the rows and said so.
  - **Rules:** T11.
  - **Depends on:** S2-M1-T4

- [ ] **S2-M5-T4: The not-English warning**
  - **Build:** Needs question 1 ([ADR 0017](../adr/0017-language-detection-with-lingua.md)). In `src/clause_tracer/ingest/language.py`, the only file in the repo that imports `lingua`:
    - `WARNING_NOT_ENGLISH: Final[str] = "not_english"`, exported from `__init__.py`.
    - `MIN_WORDS_TO_JUDGE: Final[int] = 10`, with the comment `# [Assumption] tuned in testing.`
    - `@functools.cache def _detector() -> LanguageDetector`, which returns `LanguageDetectorBuilder.from_all_languages().build()`. It is built on first use and reused.
    - `def looks_not_english(text: str) -> bool`: with `words = re.findall(r"[^\W\d_]+", text)`, fewer than `MIN_WORDS_TO_JUDGE` words gives `False` (too short to tell). Otherwise `language = _detector().detect_language_of(text)`, and the result is `language is not None and language != Language.ENGLISH`.
    - In `reading.py`, `_build_document` sets `warnings=(InputWarning(code=WARNING_NOT_ENGLISH, page=None),)` when `looks_not_english(text)` is true, else `()`.
    - In the README, add the warning code, that Lingua names the language, and the `[Assumption]` 10-word minimum.
  - **Files:** `src/clause_tracer/ingest/language.py`, `src/clause_tracer/ingest/reading.py`, `src/clause_tracer/ingest/__init__.py`, `src/clause_tracer/ingest/README.md`, `src/clause_tracer/ingest/tests/test_language.py`, `src/clause_tracer/ingest/tests/test_reading.py`.
  - **Tests first:** in `test_language.py`: `test_not_english_table`, parametrised over `not_english.toml` (case keys and required keys `id`, `text`, `warned`): `looks_not_english(text) is warned`; `test_not_english_table_has_rows` (at least 8 cases); `test_text_under_10_words_is_never_warned` (`"Le Client paie les frais."` gives `False`); `test_only_this_file_imports_lingua` (read every `.py` file under `src/clause_tracer/` except `ingest/language.py` and the files in `ingest/tests/`; none contains the string `lingua`). In `test_reading.py`: `test_not_english_text_carries_the_warning` (`read_pasted_text("Les factures sont payées dans un délai de soixante jours à compter de la date de facture.").warnings == (InputWarning(code="not_english", page=None),)`); `test_english_text_has_no_warning` (`read_pasted_text("Invoices will be paid within 60 days of the invoice date.").warnings == ()`). If a table row fails, stop and bring it to the owner: do not change the row.
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_language.py src/clause_tracer/ingest/tests/test_reading.py` passes, and `scripts/check.sh` exits 0 with no golden file changed.
  - **Rules:** B4 (the library is hidden in one file), T1, T11, T13, [Spec 9](../spec.md#9-running-the-app) (the warning; the user can still continue, so this is a warning and never an error), [ADR 0017](../adr/0017-language-detection-with-lingua.md).
  - **Depends on:** S2-M5-T3, S2-M4-T5, S2-M1-T6

- [ ] **S2-M5-T5: Finish the READMEs**
  - **Build:** Bring `src/clause_tracer/ingest/README.md` to its final form: Purpose; Spec steps; "Public calls" (`read_text_file`, `read_pasted_text`, `split_clauses`, with signatures, errors and side effects); "Shapes it returns" (which `core` shapes, and which fields stage 2 leaves empty); "Clause and sentence ids"; "What the splitter reads, and what it does not" (the list in section 2, "Leaves to later stages"); "Samples"; "Golden files"; "Owner tables"; "Run alone"; "Depends on: `core`, NUPunkt and Lingua". In `src/clause_tracer/README.md`, change the `ingest` row to "Read text, Markdown and pasted text; split into clauses and sentences (6.1 steps 1-2). Word and PDF come in stage 5." Add `src/clause_tracer/ingest/tests/test_architecture.py`.
  - **Files:** `src/clause_tracer/ingest/README.md`, `src/clause_tracer/README.md`, `src/clause_tracer/ingest/tests/test_architecture.py`.
  - **Tests first:** in `test_architecture.py`: `test_public_names` (`set(clause_tracer.ingest.__all__) == {"DOCUMENT_SCHEMA_VERSION", "NUMBERING_NUMBERS", "NUMBERING_PARAGRAPHS", "WARNING_NOT_ENGLISH", "read_pasted_text", "read_text_file", "split_clauses"}`); `test_readme_names_every_public_name` (each name in `__all__` appears in the README's text); `test_module_has_its_parts` (`README.md`, `tests/`, `samples/` and `__main__.py` exist in the `ingest` folder).
  - **Done when:** `.venv/bin/uv run pytest src/clause_tracer/ingest/tests/test_architecture.py` reports 3 passed, and `scripts/check.sh` exits 0.
  - **Rules:** S3, T9, [ADR 0007](../adr/0007-document-reading-stack.md) action item 6 (tell the owner it can be ticked for the text part).
  - **Depends on:** S2-M5-T4, S2-M5-T2

- [ ] **S2-M5-T6: Close the stage**
  - **Build:** Run the "Done when" checks of section 7. Write section 9 of this plan. Update the status lines: [AGENTS.md](../../AGENTS.md) "Where the project stands" (stage 2 done, stage 3 `links` next), the status line in [README.md](../../README.md), and [testing strategy 13](../testing-strategy.md#13-gaps-today-and-the-order-to-close-them) (the "No samples or golden files" row: `ingest` closed, with the date). Set this plan's status to Done. Then give the owner a short report: what was built, what differs from the outline, the open limits of the splitter, and the action items to tick.
  - **Files:** `docs/plans/stage-02-ingest.md`, `AGENTS.md`, `README.md`, `docs/testing-strategy.md`.
  - **Tests first:** None.
  - **Done when:** Every box in section 7 is ticked, `scripts/check.sh` exits 0, and the owner has the report.
  - **Rules:** The README, "When the stage is done"; [WRITING_DOCS.md](../../WRITING_DOCS.md) section 9.
  - **Depends on:** S2-M5-T5, S2-M4-T6, S2-M3-T10

## 6. Open questions

The owner answered questions 1 to 9 on 17 Nov 2026, questions 10 and 11 on 19 Nov 2026 and questions 12 to 14 on 20 Nov 2026. Each answer is recorded in its home. The recommendation column keeps the planner's first proposal, so where the answer differs, the answer wins.

| # | Question | Needed by task | Recommendation (if any) | Owner's answer |
| --- | --- | --- | --- | --- |
| 1 | **How does the app detect that a contract is mostly not English?** [System design 15.2](../system-design.md#152-stage-2-ingest-for-text-markdown-and-pasted-text) leaves it open: Spec 9 asks for the warning and no decision record names a method or a library. | S2-M5-T3, S2-M5-T4 | No new library. Count the share of words that are among 40 common English words ("the", "of", "shall" and so on). Warn when the share is under 1 in 10, and never on a text shorter than 50 words. Both numbers are `[Assumption]`. It is small, it gives the same answer every time, and a person can read why it warned. The other route is a language-detection library, which is a new runtime dependency to bundle and licence-check. | Lingua, not the recommendation: [ADR 0017](../adr/0017-language-detection-with-lingua.md) and [Spec 9](../spec.md#9-running-the-app) (17 Nov 2026) |
| 2 | **What does `MatchKey` fold, and where does the fold live?** The stage 1 plan asks for this decision ([section 9](stage-01-core.md#9-notes-for-the-next-stage)). `core` already has the narrow Spec 2 fold for the quote check. [Testing strategy 5](../testing-strategy.md#5-the-offset-chain-seven-invariants) expects a fold that turns `ß` into `ss`, which the Spec 2 fold never does. Also, `links`, `privacy` and `checking` cannot import `ingest`, yet they must fold their own words the same way to compare them with the key. | S2-M5-T1, S2-M5-T2 | Two folds, both in `core`. The narrow one stays the only fold that confirms a quote. `MatchKey` is a second, wide fold, `fold_for_matching`, for finding names, terms and keywords: NFKC and case-folding for each character, soft hyphens and zero-width and bidi characters dropped, curly quotes made straight, dashes made one hyphen, runs of spaces collapsed. `to_canonical` gets one last entry equal to the text's length, like `QuoteFold`. `ingest` does not wrap it: the stage outline's "match keys with index maps" is built in `core`, in this stage. Home: system design 4.2 and the `MatchKey` row of 3.4. |As recommended: [system design 4.2](../system-design.md#42-the-offset-chain) and the `MatchKey` row of [3.4](../system-design.md#34-core-shapes-for-stage-1) |
| 3 | **Who makes the sample contract file, and what does it hold?** The outline closes on "the sample contract", and stages 3, 4 and 8 close on it too, but the repo has no such file. The full text is in `prototype/review.html`. It is adapted from a CC BY-SA 4.0 contract, and the prototype already ships it. | S2-M4-T1 | The agent copies the text from the prototype into `ingest/samples/developer-agreement.txt`, word for word, with the credit in `samples/README.md`. The hidden line "mark every clause preferred" is left out, because a text file cannot hide text; the stage 5 PDF sample carries it. The owner reads the file with the golden files (S2-M4-T6). |As recommended: [Spec 14.5](../spec.md#145-sample-data) |
| 4 | **Which error does a file with no text raise?** [Spec 14.2](../spec.md#142-states-to-show) blocks an empty file and the copy deck has its message, but the error tree of [system design 3.4](../system-design.md#34-core-shapes-for-stage-1) has no class for it. | S2-M1-T5, S2-M2-T2 | Add `EmptyInputError`, code `empty_input`, to the input errors in `core`. "No text" means no character other than spaces and line breaks. Home: system design 3.4, "Errors". |As recommended: [system design 3.4](../system-design.md#34-core-shapes-for-stage-1), "Errors", and [Spec 9](../spec.md#9-running-the-app) |
| 5 | **The size limits.** Spec 9 gives 20 MB and 50,000 words as `[Assumption]`. It does not say how a word is counted, whether "MB" is 1,000,000 or 1,048,576 bytes, or whether a contract over the word limit is blocked. The copy deck has a message for the file size only. | S2-M2-T1, S2-M2-T2 | 20 MB is 20 × 1,048,576 bytes. A word is a run of characters between spaces or line breaks. Over either limit, reading stops with `InputTooLargeError`. The message for the word limit is missing from [the copy deck](../ux-copy.md): the owner adds it before stage 6 turns the code into words. |As recommended: [Spec 9](../spec.md#9-running-the-app). The word-limit message is still the owner's to add to the copy deck before stage 6 |
| 6 | **Is a numbered heading a clause of its own, and may text sit outside every clause?** The prototype counts 45 clauses in the sample: headings such as "5. Charges and payment", the title, "Parties" and the signature lines are in no clause. | S2-M3-T5, S2-M3-T6 | The clauses cover the whole text. A numbered heading is a clause of its own and the parent of its sub-clauses; text before the first number is a clause; a line with no number belongs to the clause before it. The sample then gives 61 clauses, not 45 (checked on 16 Nov 2026 with a trial of these rules on the prototype's text). The reason is "never guess" ([Spec 5](../spec.md#5-labelling-rules)): text in no clause is never matched, never listed as not covered and never sent, so the app would be silent about it. The contract check can still draw a heading inside its sub-clauses, as the prototype does. If the owner prefers 45, the plan changes before milestone 3. Home: system design 4.2, with the "45 clauses" lines of the copy deck and prototype. |As recommended: [system design 4.2](../system-design.md#42-the-offset-chain). With the answer to question 7, the sample gives 64 clauses; the copy deck and the prototype say 64 |
| 7 | **Which numbering styles does stage 2 read?** The outline asks for "a stack of open levels and continuity check". Schedules, a table of contents and `(i)` come only from the architecture report, which is historical. | S2-M3-T3, S2-M3-T5, S2-M3-T6 | Read `5.`, `5.1`, `5.1.2` (up to five parts), `(a)`, `(i)`, `(A)`, `(1)`, and schedule headings ("Schedule", "Annex", "Appendix", "Exhibit"), which start numbering again. A number is accepted only as the next sibling or first child of the numbering so far. A `1.` that does not follow on starts numbering again, which keeps a table of contents from swallowing the body; when a later number follows on from the numbering before the restart, that numbering goes on. Not read in stage 2: "Clause 5" and "Article IV", "a)", a bare "1 Heading", and unnumbered headings. Four known limits follow, each fixable by hand at the contract check: a contract whose own numbering skips a number keeps the rest inside the clause before the gap; an unnumbered heading such as "Background" stays at the end of the clause before it; in the sample, recital `(A)` becomes a child of party `(2)`, with the id `(2)(A)`; and a numbered list inside a clause (`1.`, `2.`) becomes clauses of its own. Wait for the ten test contracts to show which of these matter. |More than recommended: also `Clause 5` and `Article IV`, `a)` and `i)`, bare `3 Payment` and unnumbered headings, with three guards the owner chose on 17 Nov 2026 (no tab on a bare-number line; a heading needs a blank line before it or a marker line after it; a heading ends any bracketed list) and a fourth on 19 Nov 2026 (before any numbering, only a bare `1` starts it). Recorded in [system design 4.2](../system-design.md#42-the-offset-chain). The limits of a skipped number and of a list inside a clause stay |
| 8 | **May Markdown symbols stand before a clause number?** [Spec 9](../spec.md#9-running-the-app) says Markdown symbols are shown as plain characters. It does not say whether `## 3. The Services` or `**5.1** The Agency…` starts a clause. | S2-M3-T3 | Yes. The text keeps every symbol, and the splitter looks past `#`, `*` and `_` before a number and a closing `**` or `__` after it. Without this, most Markdown contracts fall back to paragraphs. |As recommended: [system design 4.2](../system-design.md#42-the-offset-chain) |
| 9 | **The form of clause and sentence ids.** [System design 5.1](../system-design.md#51-three-kinds-of-data) says ids are "derived from the clause number and span". | S2-M3-T6 | Ids come from the number and the order, not from offsets: `5.1`, `7.1(a)(i)`, `S1.2` inside Schedule 1, `p3` for the third clause with no number, a `~2` ending when a number appears twice, and `5.1.s3` for a sentence. They are the same on every read of the same file, and a person can read them. Home: system design 5.1 and the `Clause` row of 3.4. |As recommended: [system design 5.1](../system-design.md#51-three-kinds-of-data) and the `Clause` row of [3.4](../system-design.md#34-core-shapes-for-stage-1) |
| 10 | **Is a file with NUL characters text?** Strict UTF-8 accepts NUL, so a binary file with only ASCII bytes reads as text. No error in the tree fits. | S2-M2-T2 | None yet, the owner decides (options: leave it, reuse `NotUtf8Error`, or add a new error). | Owner, 19 Nov 2026: reject it. New error `NotTextError`, code `not_text`. |
| 11 | **Does the paste box need its own size limit?** Spec 9 gives one limit for a file or a paste: 20 MB and 50,000 words. | S2-M2-T3 | None yet. | Owner, 19 Nov 2026: no. A paste keeps the same limit as a file, 20 MB and 50,000 words, as Spec 9 says. |
| 12 | **Does a line that ends in a colon end a sentence?** In the sample, `1.1.s1` holds the lead-in line "In this Agreement the following words have these meanings:" and the first definition, because NUPunkt looks for full stops. | S2-M4-T8 | Do nothing was the smallest option. A break after a colon line is narrow and language-neutral, and the MultiLegalSBD guidelines use the same rule. | Owner, 20 Nov 2026: break after a colon line. A known limit: a hard-wrapped line that ends in a colon inside a sentence also breaks. See [system design 4.2](../system-design.md#42-the-offset-chain) |
| 13 | **Which lines open a clause when they are a signature line?** `Signed for and on behalf of Brightline Studio Ltd by Sarah Jones, Director` is 73 characters, so the 60-character heading limit left it inside clause 14.6, while the shorter `Signed by Karim Benali` got its own clause. | S2-M4-T7, S2-M4-T9 | Lines that open with `Signed`, `Executed` or `In witness whereof`, whatever their length. | As recommended, 20 Nov 2026. A known limit: a sentence such as `Executed copies must be kept by both parties.` after a blank line also becomes a clause. See [system design 4.2](../system-design.md#42-the-offset-chain) |
| 14 | **How does the owner read whole sentences?** The outline cuts each preview at 60 characters, so six lines of the first read looked like wrong breaks. | S2-M4-T10 | A `--full` flag on the command, which prints in full to the screen. The golden files keep the cut. | As recommended, 20 Nov 2026. See the README of `ingest` |

## 7. Done when

- [ ] Every task above is ticked.
- [ ] `scripts/check.sh` passes with no errors.
- [ ] Each touched module's README records its shapes (Constitution S3): `ingest` and `core`.
- [ ] Every promise the stage touches has its test (Constitution T13): the sentence-id part of "every evidence link scrolls to the right place" (S2-M3-T10, S2-M5-T2) and the not-English warning (S2-M5-T4).
- [ ] The lines that state the project's status are updated (see the README, "When the stage is done").
- [ ] The owner has been told what was built, and what the next stage should know.
- [ ] `python -m clause_tracer.ingest` reads the sample contract, prints its clauses and sentences, and exits 0.
- [ ] The two golden files match, and the owner has read them (S2-M4-T6).
- [ ] The three owner tables have their rows, and their tests pass.
- [ ] Branch coverage of `ingest` is at least 85%, and of `core` at least 95%.
- [ ] Importing `clause_tracer.core` still loads only the standard library (the stage 1 architecture test passes with `match_fold.py` in place).

## 8. Change log

| Date | Change | Why |
| --- | --- | --- |
| 16 Nov 2026 | The owner asked the agent to write the three owner tables before the build starts and to tick their tasks: S2-M3-T5 (`clause_split.toml`, 17 cases), S2-M5-T1 (`match_fold.toml`, 11 cases) and S2-M5-T3 (`not_english.toml`, 7 cases). The rows follow the recommendations of questions 1, 2 and 6 to 9, which are not answered yet. S2-M1-T4 is ticked too: the three files now exist with their rows, so no empty files are created. S2-M4-T6 stays open, because the golden files do not exist until S2-M4-T4. | The owner's request. The expected answers do not depend on the code, only on the rules. If an answer to a question differs from its recommendation, the rows that rest on it change before the task that reads them. |
| 17 Nov 2026 | The owner answered questions 1 to 9 (section 6). Questions 1 and 7 differ from the recommendations: Lingua replaces the word share (new task S2-M1-T6, S2-M5-T4 rewritten, [ADR 0017](../adr/0017-language-detection-with-lingua.md)), and the splitter reads `Clause`/`Article` keywords, `a)` items, bare `3 Payment` numbers and unnumbered headings (S2-M3-T2, T3, T6 to T10 changed). Two unit-test texts in S2-M3-T6 and T7 gained a full stop, because the heading rule would otherwise read their short line as a heading. The owner tables were regenerated: `clause_split.toml` now has 25 cases (the recitals rows changed, and 8 cases were added for the new styles), `not_english.toml` has 8 cases under the Lingua rule, and `match_fold.toml` is unchanged. Each answer is recorded in its home: the spec, the system design, the copy deck and the prototype (45 clauses became 63). | The owner's answers. The tables' rows follow the rules as now written, and the owner reads them before accepting the plan. |
| 19 Nov 2026 | Two checks of the rules found two gaps, both fixed. A heading now always ends a bracketed list, as the owner chose on 17 Nov; the earlier wording kept a bracketed item under the clause before the heading when numbering was open. Before any numbering, only a bare `1` starts it (the owner's answer of 19 Nov), so an address line such as `27 Rue Didouche Mourad` stays text. S2-M3-T6 gained two tests, and `clause_split.toml` two cases (27 in all). | A plain reading of the plan, implemented from scratch, gave `1.1(A)` and read an address as clause 27. |
| 19 Nov 2026 | An independent review found the sample gives 64 clauses, not 63: the planner's transcription of the prototype had dropped the line `8. Confidentiality`. The count is 64 everywhere. The review also made the plan tighter where a reader had to guess: the BARE and PAREN rules of S2-M3-T6, when ids become unique, `body_start` for BARE, the lower-case Roman reading in S2-M3-T2, the input of `test_document_has_no_glyphs`, and the floor of S2-M3-T10 (33 tests). No rule changed. | A fresh agent built the splitter from the plan alone and compared it with every row. |
| 19 Nov 2026 | The owner approved the review fixes of M2. A text with only a byte-order mark is empty (T2 step 5). The byte-limit check moves into `read_pasted_text`, and `_build_document` holds the shared checks (T3). The byte-order-mark rule adds three tests, and the pasted byte limit adds one. Question 10 asks whether a file with NUL characters is text. The review point on memory use was split: the paste now checks its character count before it encodes (see the row below), and the full word list stays, because the 20 MB limit bounds it. | The owner's request after the M2 review. |
| 19 Nov 2026 | The owner approved the second round: the early character check in `read_pasted_text` (T3), `NotTextError` for NUL characters (T2, `core`, system design 3.4), and questions 10 and 11. | The owner's request after the M2 review. |
| 19 Nov 2026 | The owner answered question 11: no separate paste limit. The owner also approved the words for the new error: "This file doesn't look like text. Choose another file, or paste the text." The words are in the spec (14.2 and the input limits), the copy deck (4.3 and section 6) and the prototype (the `not-text` and `load-not-text` states). The tests also ran on Python 3.12.16 (1,138 passed), the version CI uses. | The owner's answers, and the check that failed in M1. |
| 19 Nov 2026 | A review of M3 found four gaps in the marker and heading rules; the owner approved these changes. A `Schedule N` line is a marker only when nothing or a separator (`·`, `:`, `-`, `–`, `—`) follows the designation. A clause that a bracketed marker started has no heading. A line with only a byte-order mark is blank. `written` keeps the number as the line writes it (`05.` gives `05`, the id stays `5`). Two changes were not made, because the owner table expects the old rule: any number may open the first clause (an excerpt can start at clause 5), and a short line after a blank line is still a heading clause. So a line such as `Signature` after a blank line becomes a clause of its own; this is a known limit. S2-M3-T1, T3 and T7 were reworded; `clause_split.toml` did not change; one expected value in `test_markers.py` changed and four tests were added. | The owner's answers to the M3 review. A wrapped line that began with `Schedule 2 to` had opened a schedule and given the next clause the wrong id. |
| 20 Nov 2026 | The owner read the first golden files and found three limits. The owner decided (questions 12 to 14): a line that ends in a colon ends a sentence; a line that opens with `Signed`, `Executed` or `In witness whereof` is a heading whatever its length; and a `--full` flag prints whole sentences. Tasks S2-M4-T7 to S2-M4-T12 were added to milestone 4, and S2-M4-T6 now waits for them. S2-M4-T13 fixes an old bug in the `contract_like_text` test strategy that a review of these tasks found: a text of only a byte-order mark passed its blank-text guard. The sample gives 65 clauses and 75 sentences, not 64 and 74, so the count changes in the copy deck, the system design and the prototype (S2-M4-T11); question 6 and the 19 Nov 2026 row of this log that gives 64 keep it as the count of that day. | The owner's read of the golden files. A research report on splitting methods (`reports/Clause splitting methods across languages.md`) found that all three fixes fit a design that adds other languages later. |

## 9. Notes for the next stage

None yet. Filled in when the stage is done.
