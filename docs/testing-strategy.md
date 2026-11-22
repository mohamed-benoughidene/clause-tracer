# Testing strategy: Clause Tracer version 1

11 Nov 2026 · status: **accepted** on 12 Nov 2026, with [ADR 0013](adr/0013-test-layers-and-release-gates.md)

This is the plan for testing version 1: which tests exist, what each must prove, which tools run them, when they run, and what must pass before a release. It covers the engine, the desktop shell and the installers.

**Where things stand.** Today the repo has one smoke test per module and one end-to-end test of `--version`. Everything below is planned, not built. The plan follows the [Constitution](../Constitution.md)'s fifth principle (rules T1 to T13), and its choices are recorded in [ADR 0013](adr/0013-test-layers-and-release-gates.md), which the owner accepted on 12 Nov 2026. The evidence is in [the v1 design decisions report](../reports/Clause%20Tracer%20v1%20design%20decisions.md). The system being tested is described in [`system-design.md`](system-design.md).

## 1. What the tests must prove

A test plan for this app starts from its promises. Each acceptance test in Spec section 11 needs a test that fails loudly when the promise breaks (T13).

| Promise (Spec 11) | Proven by | Layer |
| --- | --- | --- |
| Every planted walk-away gets the label walk-away | Label-rule tables; the paid test set, all three runs | Unit, paid |
| At least 90% of numbers and labels correct | The paid test set, with an exact interval | Paid |
| No made-up quote reaches the screen | Quote-check unit tests; the last check before drawing; replay tests with a wrong quote | Unit, replay |
| Every planted name, company and address is caught | Planted-entity contracts with computed offsets | Unit, integration |
| No confirmed item, note or name in any AI request, including position text and rewrite instructions | Canary scan of every request body | Integration |
| Every private-mode request asks for zero retention | Request-builder contract test | Unit |
| No acceptable limit reaches the message step | Prompt-render leak test; output scans | Unit |
| No AI text states what a law allows | Output-scan tests | Unit |
| Saved data is unreadable without the key | Byte scan of the data folder, with a positive control | Integration |
| Auto-delete runs on schedule | Fixed-clock tests of the date rules and the store | Unit, integration |
| Every evidence link scrolls to the right place | Offset invariants; highlight pictures | Unit, visual |
| Hidden text shows its Read first row; values on it are unsure | Hidden-text fixtures with innocent look-alikes | Unit, replay |
| A full review runs on Linux and Windows from the installer | Packaged-app smoke test in CI, plus one full review of the sample contract in the packaged build against saved replies (the replay fake), with no paid call. **To design at build stage 12:** how the packaged build is pointed at saved replies | Release |
| Every stored text keeps a written-by value (code, AI or user) | A schema test that no text can be saved without one; replay tests that AI, code and user text each get the right value (Spec 4.7 and 6.2, [ADR 0016](adr/0016-legal-positions-without-a-lawyer.md)) | Unit, replay |
| A PDF report with AI-written text carries a machine-readable AI mark in its metadata | Export the sample review, read the PDF's metadata back, and assert the mark is there. Assert it is absent from a report with no AI text (Spec 4.7, ADR 0016) | Integration |
| Uninstall offers to remove all data and keys (Spec 8.3) | An uninstall test on each system: choose removal, then scan the data folder and the password store for the review data and both keys. Choose keep, and assert both stay. **The uninstall flow has no design yet.** It is settled at the shell stage (build stage 12) | Release |
| Blind self-test: the owner catches a planted wrong label | Manual, with a script that plants the label | Manual |

## 2. Principles

1. **Test behaviour at the boundary** (T5, T6). Ask what someone rewriting the module would have to keep true. Test that.
2. **Fakes, not mocks** (T3). Every port has a simple working fake. No test checks how many times something was called.
3. **No network, no key, no cost** for everything except one opt-in suite (T7, T8). The whole free suite runs with sockets blocked.
4. **Only replay is repeatable.** The model endpoints chosen for version 1 accept no `temperature`, and output varies even at temperature 0. A test that calls a live model cannot gate a pull request.
5. **The case is the unit, not the run.** Three runs of one contract are not three trials. Rates are counted per case and compared with the last accepted baseline case by case.
6. **A person owns the expected answers** (T11). Agents write most tests here, and studies in 2025 and 2026 found AI-written tests catch fewer planted bugs than human ones. So expected values live in tables only the owner edits.
7. **When testing hurts, fix the design** (T10).

## 3. Five layers

| Layer | What it runs | Where it lives | Speed | Runs |
| --- | --- | --- | --- | --- |
| **1. Unit** | One module through its public call, with fakes. Label rules as tables. Property tests of pure invariants | `src/clause_tracer/<module>/tests/` | Milliseconds | Every change |
| **2. Golden-file** (free) | Each module's public call on its `samples/`, compared with a committed expected file | Beside each module | Fast | Every change |
| **3. Contract and integration** | One behaviour suite against each fake **and** its real adapter. Real encrypted storage in a temporary folder. The OpenRouter adapter against saved bodies | `tests/` | Seconds | Every change |
| **4. End-to-end replay** | The whole command-line tool on the sample contract with the replay AI client; asserts the Spec 14.5 labels | `tests/` | Seconds | Every change |
| **5. Paid test set** | The real API on the ten test contracts and the built cases | Private repository, opt-in | Minutes, costs money | By hand, before a prompt, model or labelling change merges |

Two more kinds of test sit across the layers: **architecture tests** (T9) and **release tests** of the packaged app (section 9).

This keeps the shape the Constitution asks for (T4): many unit tests, some integration tests with real storage, and very few end-to-end tests.

## 4. What to test in each module

| Module | Main promises to test | Example cases |
| --- | --- | --- |
| `core` | Label rules 1 to 10; unit conversion; playbook checks (Spec 4.1); auto-delete dates; cost estimate; output scans; the last check before drawing | One table row per rule and per row of the Spec 14.5 sample. "Unlimited" is walk-away when lower is better and unsure when higher is better. Business days never convert. A hidden-text value is not readable for Rule 4. A scan fails "Dear John", a web address, "safe to sign", an acceptable limit, a wrong label word. The style scans (Spec 6.2, 14 Nov 2026) fail "I", "Certainly!", "unfair", a reason with no clause number or quoted word, and a rewrite that adds a sentence. The "Keep" strings of [ux-copy 1.1](ux-copy.md#11-signs-of-machine-made-text) pass them. The starter playbook over 50 clauses makes 30 estimated calls |
| `ingest` | Canonical text built from glyphs; clause and sentence splitting; hidden-text checks; file limits | "2.5 days" is not a clause number. Ligature "ﬁ" is one glyph and two letters. A line-end hyphen is kept. White text, tiny fonts and zero-width characters are flagged, never removed. A `.doc` is detected by its bytes. A zip bomb ends as `UnreadableFileError` |
| `privacy` | Placeholders, the segment map, name variants; the code finders and the resolve step | Anonymise then restore gives the original. A `⟦` already in the contract is escaped. No entity crosses a sentence boundary. "Ms Jones" and "Sarah" share one placeholder, and a "Jones" that fits two people gets its own. Every pattern has true and false sample rows. An ID or bank span holds the value only. The governing-law place is kept only from a closed list, and a person or company span that touches it stays whole. Properties of the resolve step: every letter and digit that a suggestion covers is covered by exactly one span, in any input order, and resolving twice gives the same result. A bad offset raises `ValueError`, and a detector error is never caught |
| `links` | Cross-references, defined terms, override direction, outside documents | "Notwithstanding Clause 4" overrides its target; "Subject to Clause 4" is qualified by it. An unresolved target is kept, not dropped |
| `checking` | Reply validation, quote check, the four match searches, retries, fallbacks | A quote found twice inside the cited sentences fails. An unknown clause id is a broken reply. A timeout or a rate limit never becomes Missing. A keyword hit triggers the pair check. Two "no" answers give `MATCH_UNCONFIRMED`. A failed scan falls back to the template after one retry |
| `writing` | Edits applied by code; rewrite rules; re-check of every affected position | An `old` piece not in the clause is rejected. A new number not in the preferred level fails. Placeholders and defined terms survive |
| `outputs` | The message and the report | Every ticked topic appears. No acceptable limit appears. `[TO]` and `[FROM]` are filled by code. Report text is plain text |
| `adapters` | Each adapter behaves like its fake | The same suite runs against `FakeReviewStore` and the real store, and against the replay client and the real client fed saved bodies |
| `cli` | The runner, resume, cancel, exit codes, the stdio protocol | A cache key changes when any input changes. Resume makes no call that was already paid for. Each error code maps to its exit code. A protocol version mismatch fails at start-up |

Each module also keeps its smoke test, so it always runs alone (S1, S2).

## 5. The offset chain: seven invariants

The product is named after its evidence trail, so the chain from an AI quote to a highlight on the page gets one stated rule per link. Each is a property test.

1. **Glyphs to canonical text.** Every character points at a glyph or is marked generated.
2. **Canonical text to match key.** Folding a slice equals slicing the folded text.
3. **Canonical to placeholder text.** Segments tile both texts, restore undoes anonymise, and no entity crosses a sentence boundary.
4. **Sentence ids.** A clause's sentences join up to the whole clause, and ids stay the same when the file is read again.
5. **Quote to span.** Exactly one span inside the cited sentences, or a failure. Changing one character fails.
6. **Span to boxes.** Every non-generated character has a box inside its page.
7. **End to end.** The last check before drawing agrees, by a different code path.

**Tool: Hypothesis.** Use its built-in `ci` profile on every change, and a larger profile (2,000 examples) at night. The root `conftest.py` loads one profile, `clause_tracer`, on top of the profile Hypothesis has loaded (the `ci` profile in CI), with no deadline, so a slow first example fails neither a local run nor CI. The default text generator rarely produces the characters that break PDFs, so the tests use a custom "hazard" alphabet: ligatures, soft hyphens, curly quotes, zero-width characters, bidi controls and the `⟦` escape. Two traps to cover on purpose: folding can change a string's length (`ß` becomes `ss`), and offsets must count code points, not UTF-16 units. Every bug found becomes a committed `@example` (T6).

**Pictures too.** Number tests built on a wrong formula pass happily. So a script writes test PDFs with known glyph positions (ligatures, two columns, headers and footers, rotated and cropped pages, white text, duplicate glyphs), and a visual test renders each highlighted page and compares it with a saved picture. To keep this stable: pin the renderer in `uv.lock`, turn anti-aliasing off, render in greyscale at a fixed scale, and compare only a mask of highlight-coloured pixels. Run it on Linux only. A saved picture is never updated in the same change as coordinate code without a person looking at it.

## 6. Testing the AI steps without the AI

### 6.1 The replay fake

One fake serves every AI module: a pure, in-memory replay client, `ReplayAiClient` in `clause_tracer.core.fakes`, keyed by a hash of the exact request ([`system-design.md`](system-design.md) section 3.4, decided 14 Nov 2026). It has two checks built in:

- **Fail on an unrecorded request.** A changed prompt cannot silently fall through to "no answer".
- **Fail on an unused recording.** Stale fixtures cannot pile up, and a step that stopped making a call is noticed.

Each module's tests and `__main__` load their own sample replies and hand them to the fake, so `core` never touches a file (T1).

### 6.2 What replay tests cover

Everything around the model: parsing, validation, the one retry, the fallbacks and the error paths (T7). The fixtures include replies the model should never give but one day will: a quote that is not in the text, an unknown clause id, an invented placeholder, an empty body with `finish_reason: stop`, a number in a slot that bans digits, and a reply that obeyed a planted instruction. These prove the code checks hold whatever the model does. They check shape, not exact words.

### 6.3 Prompts

A fast test renders every prompt version with sample inputs and asserts the Spec 6.2 rules: no playbook names, no To or From names, no notes, and no acceptable limits in steps 10 and 13. A released prompt file is never edited; a change adds a new version. A second test checks that each reply schema uses only keywords that both the provider's strict mode and Pydantic enforce.

### 6.4 The real adapter, without a key

The OpenRouter adapter is tested against saved response bodies through `httpx2.MockTransport`, which is built into the HTTP client. A small handler refuses any request with no saved body and reports saved bodies nothing used. The same contract suite runs live inside the paid run.

Do not use `respx` here. It patches `httpx`, not `httpx2`: in a local test on 12 Nov 2026 its mock did not intercept, and the request reached the real network. That is the failure the suite-wide socket block (section 8) exists to catch.

### 6.5 Where fixtures come from

Every paid run saves its raw replies. The useful ones are promoted to replay fixtures, so the free suite grows each time money is spent. Before a fixture is committed, a redaction check confirms it holds no `Authorization` header, no key pattern and no restored personal data. Fixtures in this repo come only from the public sample contract with its invented names (Spec 14.5).

## 7. The paid test set

This is the only layer that calls a real model. It measures quality; the free layers prove the code.

### 7.1 Building it (nothing exists yet)

| Part | How it is made | Size |
| --- | --- | --- |
| **Ten contracts** (Spec 11) | Two written from the other side's view. Eight freelancer-friendly contracts edited into worse versions. Invented names only. Each needs a licence that allows editing and keeping | 10 |
| **Answer keys** | Written by the owner by hand, one answer per starter position per contract, including the missing ones. Stored as tables only the owner edits (section 10) | 10 × 11 |
| **Injected variants** | A script plants hidden and visible instructions in each contract | 10 |
| **Built absence cases** | A script edits clean contracts: the clause removed with numbering kept; reworded with none of its keywords; moved to a schedule; reached only by cross-reference; placed beside a planted denial line | 20 to 50 per kind |
| **Planted personal data** | Templates filled with generated names, companies and addresses, with offsets computed by code. Typos and awkward cases added on purpose | A few hundred |

The answer for every built case is computed by the script that builds it, never typed. Built cases are short excerpts, not full contracts: full-length variants would raise the cost of a run about fivefold.

The ten contracts and their answer keys live in a **private repository** that CI reads ([ADR 0014](adr/0014-protection-and-release-integrity.md)). Only the public sample contract and its fixtures live here.

### 7.2 Why ten contracts are not enough

With no failures seen in *n* independent cases, the true failure rate could still be about 3 ÷ *n* (95% upper limit): about 3.7% at 80 cases, 3.0% at 100 and 1.0% at 300. Positions inside one contract are not independent, so ten contracts are about ten data points. That is why the built cases exist. Each run reports the exact interval, never a bare percentage.

### 7.3 Relations that must hold

Three checks compare runs with each other, so they need no answer key:

1. **Injected equals clean.** A contract with a planted instruction gets the same labels as the clean one, or degrades only to unsure.
2. **A harmless edit changes nothing.** An innocent change of the same size keeps the labels. This measures false alarms.
3. **Worse never looks better.** Making a clause worse never improves its label.

### 7.4 Gates and reported rates

**Hard gates. Any failure blocks a release.**

- Every planted walk-away is labelled walk-away in all three runs.
- No made-up quote reaches the output, ever.
- No dangerous false-Missing on a built case: a clause that exists, reported missing, where the missing level is better than the right label.
- No personal item in any request. Every private-mode request asks for zero retention.
- No injected run turns a walk-away into anything but walk-away or unsure, and no injected text or web address reaches a visible field.

**Two rates that must also pass, because Spec 11 requires them.**

- Number accuracy at or above 90%, and label match at or above 90%, each reported with the exact interval.

**Reported rates with no pass mark, compared with the last accepted baseline case by case.**

- The overall false-Missing rate, with its upper limit.
- **Pass in all three runs**, shown beside per-run accuracy. A user gets one run, so a case that passes two times in three fails one user in three.
- The share of labels that are unsure, the first-try quote pass rate, the highlight fallback rate, what each match search found on its own, and cost per review.
- The owner's read-through of the AI text (section 7.5): the share marked "no" for each question.

These thresholds are the project's own. No regulator or bar has published an accuracy standard for this kind of tool, so the docs must never present them as an industry norm.

### 7.5 Budget

The owner set the budget on 12 Nov 2026: **about $10.76 in total** ($5.76 in hand, plus $5). The plan below fits inside what is left of it, with a small reserve.

**What a run costs.** Prices were fetched on 11 Nov 2026 and change weekly. All figures are estimates until the first paid run measures them. The first row comes from the stage 1 cost formula (system design 7, 16 Nov 2026); the rows below it assume the cache hits, and a run where it misses costs about four and a half times as much for 10,000 words, and about eight times for 50,000.

| Run | Cheap model (Claude Haiku 5.5) | Sonnet-class model |
| --- | --- | --- |
| One review of a 10,000-word contract | `[Assumption]` 1.5 cents, or 7 cents if no call hits the cache | about $0.29, or $1.32 if no call hits the cache |
| Ten contracts, one run each | `[Assumption]` 10 to 30 cents | about $2.80 |
| Ten contracts, ten injected variants and 100 built cases, three runs each | `[Assumption]` about $2 | about $34 |
| The same with 300 built cases | $3 to $4 | about $67 |

Claude Haiku 5.5 is the cheap model to use: on 12 Nov 2026 it cost $0.10 and $0.50 per million input and output tokens, with a zero-retention endpoint. DeepSeek V4.1 Flash is cheap only outside private mode; its zero-retention endpoints cost more than its list price.

So the earlier figures of $34 and $67 hold only for a Sonnet-class model. With $10.76, paid testing runs on a cheap model, and that is workable.

**First measurements (13 Nov 2026).** A small probe spent $0.07 of the budget on eight calls ([ADR 0010](adr/0010-starting-models.md), last amendment). On a 12,616-word invented contract, the first call cost $0.0030 on Claude Haiku 5.5 and $0.0602 on Claude Sonnet 5.5; each later call, read from the cache, cost $0.00027 and about $0.003. That puts a 40-call review near 1.5 cents and 18 cents, in line with the table above. Caching hit on the zero-retention route. The table stays an estimate until step 1 runs the real pipeline.

**Spent so far:** $0.07 (13 Nov 2026). About $10.69 is left, of which the plan below uses $9.90.

**The spending plan.**

| Step | What | Planned spend |
| --- | --- | --- |
| 1 | First real run on the sample contract, cheap model. It measures real cost per review and whether caching hits | under $0.25 |
| 2 | Ten contracts, one run, on Haiku 5.5 and one other cheap model, chosen at run time. Picks the model to carry forward | about $0.50 |
| 3 | The 100-case set, three runs, on the chosen cheap model. The first full baseline | about $2 |
| 4 | Two more 100-case runs after prompt fixes | about $4 |
| 5 | One pass of the ten contracts, one run, on the default Sonnet-class model | about $2.80 |
| Kept back | For price changes and mistakes | about $0.35 |

**Rules that protect the budget.**

- **A spend ledger comes first.** The paid runner sums the cost each reply reports and stops at a cap per run. A running total across runs stops at $10, counting the $0.07 already spent. The plan rows add up to $9.90, so the plan ends at $9.97. The rest of the $10.76 stays unspent unless the owner raises the stop. Build and test this with the replay client before any key is used.
- **Free tests do the daily work.** Prompt changes are tested on saved replies first. A paid run happens only when a change cannot be judged without the model.
- **Every paid reply is saved** and becomes a free replay fixture, so no call is paid for twice.
- **Three runs only where a hard gate needs them.** Other cases run once.
- **Stop and re-plan after step 1.** If a review costs more than 5 cents on the cheap model, or caching misses, redo this table before spending more.

**What this budget cannot do.** It cannot run the 300-case set on a Sonnet-class model, or compare three models at full size. It can show whether a cheap model passes the hard gates. That matters for users too: they pay per review with their own key, so a cheap model that passes is the better default. The owner accepted a Sonnet-class default on 12 Nov 2026 ([ADR 0010](adr/0010-starting-models.md)). With this budget that default gets one pass of the ten contracts at most, so step 5 is no longer optional: run it before a release, and say in the release notes how much testing the default model had.

**The owner's read-through** (decided 14 Nov 2026). The scans catch signs of machine-made text, not a fluent sentence that is wrong (Spec 6.2). So the report of every paid run lists each piece of AI text (reasons, readings, questions and rewrites) with a read-through column. The owner marks each one yes or no for each question that applies to it:

| Question | Applies to |
| --- | --- |
| True to the clause? | Every AI text |
| Are the two readings really different? | Readings |
| Is it a question a person would send? | Questions |
| Did the rewrite keep the meaning? | Message and clause rewrites |

The report script adds the empty column; the owner fills it in. The shares marked "no" are reported rates with no pass mark (section 7.4). Reading costs no money, so it never counts against the budget.

**Tooling.** A `@pytest.mark.paid` marker, left out of `scripts/check.sh` and CI, plus a small report script. No evaluation framework is needed yet. DeepEval and promptfoo are ruled out because both send telemetry by default. Inspect AI (MIT) is the upgrade path if many models are compared.

## 8. Privacy and security tests

| What | How it is tested |
| --- | --- |
| **Leaks in requests and logs** | Give every private field a unique canary token, including a known name typed into a playbook position and one typed into a rewrite instruction (both are replaced before sending, 13 Nov 2026, ADR 0008). Assert that no token, in any letter case or split form, appears in any request body captured at the transport, any log line, or the "Copy error details" text. Assert the positive too: the placeholder marker does appear |
| **No telemetry** | The whole free suite runs with sockets blocked (`pytest-socket`). A static test allows only two host strings in the package: OpenRouter and the GitHub release page. At release, the packaged app runs once in a network namespace |
| **Private mode** | A contract test over every step's request: private mode sends the zero-retention, no-data-collection and require-parameters fields, and no plugins or tools |
| **Encryption at rest** | After a full fixture review, scan every file in the data and temporary folders for the canaries in UTF-8, UTF-16 and case-folded forms. Run it after a clean close and after a simulated crash. **Positive control:** the same scan on a deliberately unencrypted store must find the canary, or the test proves nothing |
| **Deleting a review** | Copy a review's blob, delete the review, and assert the blob can no longer be decrypted and the key row is gone |
| **Auto-delete** | A fixed clock: the boundaries, a clock that jumps backwards, a laptop off for months, the "nothing sooner than 3 days" rule, and a crash between deleting the key and deleting the row |
| **Storage settings** | Read back the settings that keep side files clean: temporary storage in memory, secure delete on, the log truncated after delete and on close |
| **Hostile files** | Fixtures built in code: zip bombs, entity expansion, external relationships, huge page counts, deep nesting. Each must end as a named input error inside its time and memory limit. Hypothesis mutates files on every change; a heavier fuzzer (Atheris) runs at night |
| **Hidden text and Unicode tricks** | Paired fixtures: one hostile, one innocent look-alike. Every hostile one raises the Read first row and every look-alike does not |
| **The app window** | Added 13 Nov 2026, from the trial builds ([ADR 0009](adr/0009-desktop-shell-protocol-and-packaging.md)). The packaged app runs on Linux and Windows and checks itself: a link to a web address does not load inside the window, no socket is listening, and a page cannot read another local file. The trial script is the starting point. **Still to add:** the installed app starts both with and without a session bus on Ubuntu, which covers the slow desktop-portal case (ADR 0009, 13 Nov 2026). Also run the app once under Wayland and once under X11, and install the package on the newest Ubuntu as well as the oldest |
| **Bundled libraries are unchanged** | A build test compares the bundled `pikepdf` and PyGObject files with the hashes in each wheel's `RECORD` file. A changed file fails the build (Spec 8.4, ADR 0016) |
| **Dependencies** | The lockfile is installed locked. Known vulnerabilities are checked on every change and weekly. A licence check fails on anything outside MIT, BSD and Apache in the runtime group, except `pikepdf` (MPL-2.0) and PyGObject (LGPL), which are allowed by name ([ADR 0007](adr/0007-document-reading-stack.md), [ADR 0016](adr/0016-legal-positions-without-a-lawyer.md)). Secret scanning covers the whole history. GitHub Actions are pinned by commit |

Two honest limits. Sockets blocked in Python do not stop a native library, so the release-level network check matters. And no test can prove what an AI provider keeps, so that promise stays worded as "asks for" ([`system-design.md`](system-design.md) section 9.3).

## 9. The shell, the pages and the installers

The interface tests are written in Python, so the owner can review them.

| What | How |
| --- | --- |
| **Pages** | pytest with Playwright for Python against the static pages, with a fake `window.pywebview.api`, in Chromium and WebKit. Each state in `prototype/states.html` is a case |
| **Untrusted text stays inert** | Load a review whose quotes, summaries and playbook text contain markup and script. Assert nothing runs and nothing renders as HTML |
| **Engine protocol** | One contract suite for every request and event, run against a fake engine and the real one over stdio. A version mismatch must fail at start-up |
| **Process life cycle** | Kill the shell mid-review: the engine exits and the review is Interrupted. Cancel returns the cost so far |
| **Real app on Linux** | One smoke test of the real window under a virtual display. Version 1 supports Ubuntu 24.04 and later, so the installs are checked on 24.04 and the newest Ubuntu, not on 22.04 |
| **Windows** | CI builds the installer, installs it silently, drives the real window with Playwright, and uploads screenshots and video. A 90-day Windows evaluation machine covers the manual look at install warnings |
| **Accessibility** | Keyboard paths for every control (Spec 14.4). Automated checks are an open point. **Release check** (decided 14 Nov 2026): with text at 200%, every page fits a window 1366 px wide with no sideways scrolling, in version 1 |

Limits to state plainly: the CI Windows machine is a server edition, so it will not show the install warning a home user sees. Screen-reader behaviour has not been checked on either system.

## 10. Keeping agent-written tests honest

- **Acceptance tables have an owner.** Expected labels, values and quotes live in CSV or TOML tables. Agents may write the loader. A CI check fails any change that edits both code and those tables, unless the owner approves it. It arrives in build stage 1 (decided 14 Nov 2026, [ADR 0013](adr/0013-test-layers-and-release-gates.md) amendment) and works like this:
  - **An owner table** is any file in a folder named `tables` directly inside a `tests` folder: `src/clause_tracer/<module>/tests/tables/` or `tests/tables/`.
  - **Code** is any other file whose name ends in `.py`, and any file in `scripts/`.
  - **A change fails** when it holds at least one owner table and at least one code file.
  - **What counts as one change.** `scripts/check_owner_tables.py` checks the uncommitted work against the last commit, as one change, inside `scripts/check.sh`. In CI, on every pull request, it checks each commit of the pull request on its own. It does not run on pushes to `main`, because a squash-merged milestone joins commits that were separate.
  - **The owner's own change passes** when its commit touches owner tables and no code. When the owner must change both in one commit, the commit message carries the line `Owner-Approved-Tables: yes`, and the CI check lets that commit pass. Only the owner writes that line. An agent never does.
- **Golden files are regenerated only by a named command**, `--update-goldens`. "Golden files" means only the free layer 2 outputs; the paid layer is "the test set", marked `paid`. A change that alters both code and golden files needs a human read of the golden diff.
- **Red first.** A new test must be seen to fail for the right reason before the code that makes it pass.
- **Mutation testing as a report.** Before a release, run `mutmut` on `core` and the pure rule modules. It changes the code in small ways and checks that some test notices. Aim for no surviving change in the label picker and the quote check. It is a report, not a gate, and it runs on Linux only.
- **Coverage is a floor, not a goal.** Studies find coverage only weakly predicts whether tests catch real bugs.

## 11. Coverage targets

Branch coverage, set per package, because one global number lets a large well-tested module hide a weak one. Measurement arrives in build stage 1 with `coverage` (decided 14 Nov 2026): `scripts/check.sh` runs the tests under `coverage run --branch` and fails when `core` is under 95%. Each later package gets its floor in the stage that builds it.

| Package | Branch coverage |
| --- | --- |
| `core` | 95% |
| Pipeline modules | 85% |
| `adapters` | 70% |
| `cli` | 60% |
| Changed lines in any pull request | 90% |

These are the project's own targets, anchored on a common industry guide (60% acceptable, 75% commendable, 90% exemplary). Glue code with no logic is not worth chasing (T6).

## 12. When each test runs

| When | What |
| --- | --- |
| **Every pull request** (`scripts/check.sh`, Linux) | Lint, format, types, import rules, unit, golden-file, contract, integration and end-to-end replay tests, property tests on the `ci` profile, highlight pictures, fixture checks, architecture tests, dependency and licence checks, all with sockets blocked (from build stage 6). Also branch coverage per package and the owner-table guard (from stage 1). Also the copy lint for fixed copy: it fails on sure signs of machine-made text and warns on soft ones ([ux-copy 1.1](ux-copy.md#11-signs-of-machine-made-text), decided 14 Nov 2026; the script is `scripts/copy_lint.py`, built 14 Nov 2026) |
| **Every pull request, once files and paths are real** | The same suite on a Windows runner pinned to `windows-2025`, without the highlight pictures |
| **Nightly** (from build stage 5) | Property tests at 2,000 examples; file fuzzing |
| **Weekly** | Vulnerability check of the lockfile |
| **Before a release** | Mutation report; the largest paid run the budget allows (section 7.5); installer builds and packaged-app tests on both systems; the `.deb` installed on Ubuntu 24.04 and on the newest Ubuntu (the one Linux build, made on 24.04); the network check; signed checksums and build attestations; the blind self-test; text at 200% fits a 1366 px window with no sideways scrolling (section 9) |
| **By hand** | A paid run, when a prompt, model or labelling change cannot be judged on saved replies. Never on push, and always under the spend cap |

**Architecture tests** (T9) go beyond `lint-imports`: importing `core` loads only the standard library; importing `cli` does not load Presidio or spaCy; every module has a `README.md`, `tests/`, `samples/` and `__main__`.

## 13. Gaps today, and the order to close them

| Gap | Closed in build stage |
| --- | --- |
| No label-rule tables, no property tests | 1 (`core`): closed 16 Nov 2026 |
| No replay fake | 1: closed 16 Nov 2026 |
| No coverage measurement; no guard on owner tables | 1: closed 16 Nov 2026 |
| No suite-wide socket block (`pytest-socket`) | 6, with the first adapters |
| No nightly job (Hypothesis at 2,000 examples, file fuzzing) | 5, with the hostile-file fuzzing |
| No samples or golden files in any module | 2 to 5, with each module: `ingest` closed 20 Nov 2026, `links` closed 21 Nov 2026 |
| No hostile-file fixtures or test PDFs | 5 (`ingest`) |
| No storage, deletion or leak tests | 6 (storage and runner) |
| No planted-entity set | 7 (Presidio adapter) |
| No saved AI replies | 8 and 9 |
| No test set or answer keys | 10. Start writing the ten contracts during stage 1, because they take the longest |
| No interface, protocol or installer tests | 12 |
| CI runs on Linux only | Add Windows at stage 5 or 6 |

Each stage leaves `scripts/check.sh` passing, as the build plan already requires.

## 14. Example tests

A label-rule table, with rows the owner edits in `src/clause_tracer/core/tests/tables/label_rules.toml`. The test reads each row, builds the inputs, and compares the label (the stage 1 plan gives the full format):

```toml
[[case]]
id = "payment-days-60-is-walk-away"
rule = "rule1"
position = "1"                 # Spec 7 starter position
match = "found"
values = [{ clause = "c1", number = "60", unit = "days", quote = "confirmed", on = "visible" }]
level = "walk_away"
reasons = []
written_by = "code"
```

```python
@pytest.mark.parametrize("case", label_rule_cases(), ids=lambda case: case.id)
def test_label_rules_table(case: LabelCase) -> None:
    label = label_position(case.label_input, case.unreadable)
    assert label.level == case.level
    assert set(label.reasons) == set(case.reasons)
    assert label.written_by == case.written_by
```

A property test for invariant 3:

```python
@given(contract_text=hazard_text(), entities=planted_entities())
def test_restore_undoes_anonymise(contract_text, entities):
    placeholder = anonymise(contract_text, entities)
    assert restore(placeholder) == contract_text
    assert tiles_both_texts(placeholder.segments, contract_text, placeholder.text)
```

A replay test for a guard (a failed call is never "nothing found"):

```python
def test_timeout_never_gives_missing(replay_client, sample_review):
    replay_client.fail_next(ModelTimeoutError)
    result = match_positions(sample_review, ai=replay_client)
    assert not isinstance(result, NothingFound)
    assert replay_client.unused_keys() == []
```

A leak test:

```python
def test_no_canary_leaves_the_computer(run_review, captured_requests, log_lines):
    run_review(contract=contract_with_canaries(CANARIES))
    sent = b"".join(r.content for r in captured_requests)
    for canary in CANARIES.all_forms():
        assert canary not in sent
        assert all(canary.decode() not in line for line in log_lines)
    assert "⟦Person 1⟧".encode() in sent   # positive control
```

## 15. Open points

- **The first paid run redoes the budget.** It measures the cost of a built case, whether caching hits, and how often runs of the same case disagree.
- **Accessibility checks** in the page tests (an automated checker through Playwright) were not verified.
- **Vulnerability scanning command.** `uv`'s own audit command is new and its exact form was not confirmed; `pip-audit` on an exported lockfile is the checked route.
- **Public hostile-file collections** exist, but their licences were not confirmed. The plan generates fixtures in code instead.
- **The evidence on AI-written tests** is mostly from Java projects. No Python-specific study was found.
- **Screen readers** have not been tested with the chosen shell on either system.
