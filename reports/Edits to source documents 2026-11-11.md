# Edits to source documents, 11 Nov 2026

This is the record of every change made to existing documents while the version 1 system design, testing strategy and decision records were written. The project owner asked that source documents be edited where the research supported it, and that each edit be recorded here.

**Summary.** Seven existing files were edited and sixteen new files were added. No promise to users was changed, and no open decision was settled: every new decision record has the status *proposed*. The largest edits are seven factual corrections to the architecture report and three new rules in the Constitution. The evidence for each is in [the v1 design decisions report](Clause%20Tracer%20v1%20design%20decisions.md).

This summary describes the state on 11 Nov 2026. Later the owner accepted ADRs 0005 to 0016 and settled many open decisions; sections 8 and 9 record what happened after 11 Nov.

To see the exact text of any edit, compare the branch `docs/v1-design-and-testing` with `main`.

## 1. Corrections to the architecture report

File: [Clause Tracer pipeline architecture.md](Clause%20Tracer%20pipeline%20architecture.md). Each fix is made in place and marked "(corrected 11 Nov 2026)". A note under the opening summary points here.

| # | Where | It said | It now says | Why |
| --- | --- | --- | --- | --- |
| 1 | `ingest`, PDF libraries | `pypdfium2` is 8.8 MB | Wheels are 3.6 to 4.5 MB | The package index lists wheels of that size. The 8.8 figure may have been an installed size, which was not verified |
| 2 | `ingest`, PDF pitfalls | pdfplumber's `dedupe_chars` "was quadratic until a recent fix" | It is still quadratic; the issue is open with no released fix | [Issue #1419](https://github.com/jsvine/pdfplumber/issues/1419) was open on 11 Nov 2026, and the latest release is older than the issue |
| 3 | `ingest`, sentence splitting | NUPunkt has "91.1% precision" | About 0.90 precision, but only 0.782 F1 on legal text | The project's own README gives these figures now. F1 below precision means missed sentence breaks, so sentence ids must tolerate them |
| 4 | `privacy`, Presidio | Since April 2026 the default configuration uses a slim spaCy engine plus GLiNER | That configuration was merged but is opt-in. The packaged default still names `en_core_web_lg` and ignores the ORGANIZATION label | The packaged `default.yaml` on the main branch says so. The conclusion (pin the configuration) is unchanged |
| 5 | AI request shape | The adapter uses `httpx` | The adapter uses `httpx2` | Plain `httpx` has had no release since December 2024. Who maintains `httpx2` was not verified and should be checked before it is adopted |
| 6 | Decision table, storage | SQLCipher "relies on a community wheel fork for Windows" | The original `sqlcipher3` now ships its own Windows and Linux wheels, and SQLite3 Multiple Ciphers is a third option the row missed | `sqlcipher3` has shipped self-contained wheels since 0.6.2. `apsw-sqlite3mc` is MIT-licensed |
| 7 | Decision table, PDF geometry | Whether `pypdfium2` exposes the fields the hidden-text checks need "is unverified" | Verified: PDFium exposes per-character box, font size, fill colour and render mode, through `pypdfium2`'s raw API | Checked against PDFium's public headers. One check remains: that the bundled build includes every function |

**Not changed.** The report's recommendations, its decision table options and its build stages are left as written. Where the new research recommends something different (one PDF engine instead of two, hybrid storage, `respx` instead of a local stub server), the new recommendation is in the decision records, not edited into the old report. The seams report was not edited.

## 2. New rules in the Constitution

File: [Constitution.md](../Constitution.md), fifth principle (Testability). Three rules were added after T10. No existing rule was changed or removed.

| Rule | Text, in short | Why |
| --- | --- | --- |
| **T11** | Expected answers have a human owner. Keep them in tables a person edits. Regenerate saved expected output only with a named command, and have a person read the difference | AI agents write most of the code and tests. Studies in 2025 and 2026 found AI-written tests catch fewer planted bugs than human ones, and an agent can "fix" a failing test by rewriting its expected output |
| **T12** | Only if the project uses AI: a replay fake fails on a request with no saved reply, and on a saved reply nothing used. Count cases, not repeated runs | Without the first check a changed prompt silently gets no answer. Without the second, stale fixtures pile up. Repeated runs of one case are not independent evidence |
| **T13** | Every promise made to users has a test that fails when the promise breaks. If no test can prove a promise, reword the promise | The research found three promises no test can prove: that providers keep nothing, that deleted data is erased from an SSD, and that saved data is safe from other software on the computer |

These follow the Constitution's own style: a short rule with an ID. The longer explanation under the rules was not extended.

## 3. The spec

File: [docs/spec.md](../docs/spec.md), section 13 only (Open decisions before coding).

- Added a short paragraph saying each open item now has a recommendation in a proposed decision record, and that none is settled until accepted.
- Added the recommendation and a link to its record after four items: the desktop shell, Presidio bundling, starting models and Jev.
- Added one new item listing the design decisions that would change the spec's own text if accepted (who writes the message and summaries, Rule 7 and related cases, and the release gates).

**Not changed.** Every checkbox is still unticked. Sections 1 to 12 and 14 are untouched, so what the app does, says and promises is exactly as before. The spec will need real edits only when the owner accepts a record; each record lists those edits under "Action Items".

## 4. The doc guides and folder lists

| File | Change | Why |
| --- | --- | --- |
| [WRITING_DOCS.md](../WRITING_DOCS.md) section 1 | Two rows: `docs/system-design.md` is the home of how the parts fit together; `docs/testing-strategy.md` is the home of how the app is tested | Every fact needs one home |
| WRITING_DOCS.md section 2 | Two rows saying which file to update when the system's structure or its tests change | So the new docs are kept up to date |
| WRITING_DOCS.md section 6 | ADRs from 0005 on use a longer format (context, decision, options with a small table, trade-offs, consequences, action items). ADRs 0001 to 0004 keep the short format. A proposed ADR is a recommendation that only the owner accepts | The owner chose the longer format on 11 Nov 2026 |
| [docs/README.md](../docs/README.md) | Rows for the two new docs, a table of the eleven proposed ADRs, and a new instruction for starting an ADR | Every new file is listed in its folder's README |
| [reports/README.md](README.md) | Rows for the new research report and for this file | The same rule |
| [AGENTS.md](../AGENTS.md) | Points agents at the two design docs and says they and ADRs 0005 to 0015 are proposed, so an agent must ask before building on one. Adds one line: leave expected answers to the user (T11) | So agents do not treat a recommendation as a decision |

## 5. New files

| File | What it is |
| --- | --- |
| [Clause Tracer v1 design decisions.md](Clause%20Tracer%20v1%20design%20decisions.md) | The research report behind every recommendation |
| [docs/system-design.md](../docs/system-design.md) | The design of the whole of version 1 |
| [docs/testing-strategy.md](../docs/testing-strategy.md) | The test plan, release gates and paid-run budget |
| [docs/adr/0005](../docs/adr/0005-engine-runner-shapes-and-ports.md) to [0015](../docs/adr/0015-provider-ready-seam.md) | Eleven proposed decision records |
| This file | The record of edits |

## 6. Things deliberately left alone

- **User promises.** "No accounts, no sign-in, no server run by the project", "no telemetry" and the others in WRITING_DOCS.md section 3 are unchanged. The system design lists which would change if a hosted option were ever added.
- **The import rules** in `pyproject.toml`, and ADR 0004.
- **The copy deck, the prototype and the README.** Several proposed records would change them if accepted. None is changed now.
- **Code.** No code, test or dependency was touched.

## 7. Known weak points in this work

- Most product-decision evidence (who writes the message, Rule 7, the AI mark, tracked changes) rests on search summaries that were not opened. The records mark these as judgement.
- Prices, model lists and package versions were fetched on 11 Nov 2026 and change often. Re-check them at decision time.
- Several checks were not done and are listed as action items: who maintains `httpx2`, the licence file of pywebview, whether the bundled PDFium build has every needed function, and Presidio's speed on a real contract.
- Legal questions (EU AI Act Article 50, trade mark classes, enforcing the licence) are flagged for a lawyer. Nothing in these documents is legal advice.

## 8. Later the same work: decisions, an audit and follow-up checks (12 Nov 2026)

This file's sections 1 to 7 describe the first day. On 12 Nov 2026 the project owner ruled on the eleven decision records, and the documents were changed to match. Compare the branch with `main` for the exact text.

| What happened | What changed |
| --- | --- |
| The owner accepted ADRs 0005 to 0015 | Each record's status. The trade mark was removed from ADR 0014 as too costly for now |
| The owner set about $10.76 for paid AI testing | Testing strategy section 7.5 and ADR 0013: cheap models, a spend cap, a six-step plan |
| The accepted decisions were written into the spec | Sections 2, 4.3, 4.7, 5 (Rules 3, 7, 8, 9), 6.1, 6.2, 8.3, 8.4, 9, 11, 12, 13 and 14.1 to 14.3 |
| The copy deck and prototype were brought into line | New states and words for the not-covered list, "Searched, nothing found", disagreeing searches, a quote not marked on the page, "Rewrite with AI", tracked changes, unreadable text and "What's protected". `ux-copy.md` section 6.8 lists the clashes fixed |
| Two reviewers audited the eleven records against the research | No wrong fact. Overstatements, dropped gaps and stale wording were fixed in place the same day |
| Open points were tested and re-read from primary sources | Dated amendments on ADRs 0005 to 0007 and 0009 to 0014, and a new closing section in the v1 design decisions report |
| The owner decided the remaining technical points | `sqlcipher3`; a `.deb` for Linux; pages loaded from files; PyGObject allowed by name; the two missing parts of ADR 0012 |

**Still open at the end of that day:** whether version 1 ships "Rewrite with AI" for the message; a trial build of the Linux package; the Windows checks in CI; and the legal questions, which need a lawyer. Section 9 below says how each was closed the next day.

## 9. Closing the last open items (12 and 13 Nov 2026)

The owner said a lawyer is not an option, and asked to work on the four items left open. Where this stands:

| Item | State |
| --- | --- |
| Legal questions | **Done, 13 Nov 2026.** [ADR 0016](../docs/adr/0016-legal-positions-without-a-lawyer.md) accepted by the owner. The spec, system design and ADRs 0007, 0011 and 0014 were updated to match |
| Linux trial build | **Done, 13 Nov 2026.** It works, with two conditions. Run without root in a throwaway sandbox; nothing was installed. Results are in an amendment of ADR 0009, and the full results file is on the local branch `spike/local-archive` |
| Windows checks | **Done, 13 Nov 2026.** The owner agreed to push the branch `spike/windows-checks`, which holds only the trial scripts. All checks passed on two Windows runners. Results are in amendments of ADRs 0006, 0007 and 0009 |
| Real installs (Ubuntu, Fedora, Windows) | **Done, 13 Nov 2026.** Real `apt`, `dnf` and Windows (Inno Setup) installs all work on GitHub's own CI runners, which have real root, and the Windows installer needs no admin rights. The Ubuntu window was slow to start, not missing: the app now waits for the window's own start-up events, and it starts on Ubuntu 22.04 and 24.04. Linux Mint 22 and 21.3 pass in containers. Ubuntu 26.04 passes too, and the app runs under a headless Wayland compositor on Ubuntu and Fedora (13 Nov 2026). **Still untried:** a real Ubuntu or Mint desktop session. Results are in the latest amendments of ADR 0009 |
| First paid run | The real first run still needs the pipeline. On 13 Nov 2026 a small probe spent $0.07 and measured cost, caching and strict forms on one form; the numbers are in the last amendment of ADR 0010 and in testing strategy 7.5 |

**Draft question for the EU's AI Act Service Desk** (the owner sent it on 13 Nov 2026, at <https://ai-act-service-desk.ec.europa.eu/en/form/helpdesk>):

> I am an individual developer outside a company. I plan to release a free desktop application under my own name. It runs on the user's computer and reviews a contract. For some steps it sends text to a general-purpose AI model through a third-party API, using an API key that the user obtains and pays for. The application shows short AI-written reasons, and can rewrite a clause or a message on request. A fixed visible line says the wording was written by AI.
>
> 1. Am I the "provider" of an AI system under Article 3(3) for the purposes of Article 50, or is that the model's provider?
> 2. If I am, does Article 50(2) apply to (a) reasons of one or two sentences and (b) a rewritten message that the user copies out as plain text? Plain text cannot carry metadata, and I cannot watermark the output of a model I do not run. Is relying on the model provider's marking, plus a metadata mark on exported PDF files, enough?
> 3. Does a free download from a public code-hosting site count as placing the system on the Union market?

### Design review and owner decisions (13 Nov 2026)

A full review of the docs was done on 13 Nov 2026. Its findings were fixed the same day: the build plan and the core shapes moved into system design sections 15 and 3.4, test names were corrected, missing test rows and the licence check were added, and stale text was fixed. The remaining open points are in the "Still open" list of [the system design](../docs/system-design.md) and in the "Not yet decided" points of its sections 3.4 and 15.

The owner then decided three things the same day:

| Decision | What changed |
| --- | --- |
| Known names are replaced in position text and in rewrite instructions too, not only in notes | Spec 4.2, 4.6, 6.1, 6.2, 11 and 13; system design section 4.1; testing strategy sections 1 and 8 (the canary test covers both fields); an amendment to [ADR 0008](../docs/adr/0008-personal-data-detection-bundle.md); the Help "What gets sent" text and `ux-copy.md` section 6.9 |
| "Check for updates" only opens the GitHub release page. The app never asks GitHub itself in version 1 | Spec 8.1 (already said so), 12, 13, 14.2 and 14.3; `ux-copy.md` About row; the prototype's Settings About card and `states.html` (the two update states are gone); the system design "Still open" list. Asking GitHub or a backend is listed in Spec 12 as a later idea |
| Version 1 supports Ubuntu 24.04 and later, Mint 22 and later, Debian 13, and Fedora by archive. Ubuntu 22.04 and Mint 21 are not supported | An amendment to [ADR 0009](../docs/adr/0009-desktop-shell-protocol-and-packaging.md), with pointers in its earlier amendments; Spec 9 and 13; system design 1.2, 10, 13 and 15 (stage 12); testing strategy sections 9 and 12. The 22.04 and Mint 21.3 trial results stay as history. The oldest supported Windows version is still open |

### Task plans (14 Nov 2026)

The owner asked for a `docs/plans/` folder with a README, a template and the first task plan: stage 1, `core`. The plan is Draft and not yet accepted. On 14 Nov 2026 the owner answered the plan's 15 open questions. Each answer is recorded in its home: Spec 6.2, 9 and 13; system design sections 3.4, 7, 13 and 15; the testing strategy sections 6.1, 10 to 13; and dated amendments to ADRs 0005, 0012 and 0013. The owner also set a rule for every plan: a strong model writes it, a cheaper model implements it, and no task leaves the implementer a design choice (a name, a field, a type, a signature or a test case). The plans README and template now say so, and the stage 1 plan was rewritten to that standard. Later that day the owner answered questions 16 and 17, the label and scan edge cases, under one principle: when the checker cannot be sure, the label is unsure, the reason is named and the user is shown the clause. The owner also added the rate-limit case: after the retries the review becomes Interrupted with a message of its own, recorded in Spec 6.2, 6.3, 9 and 14.2, the copy deck, the prototype, the system design and the plan's error-tree task.

### Review for friction and machine-made text (14 Nov 2026)

A review of the design system, the copy deck and the prototype looked for friction and for text that reads as machine-made. Its findings were fixed the same day. The owner then made eleven decisions:

1. Code writes a label's panel words; the AI writes only for words labels it judged and for values unsure because of vague wording (Spec 6.1 step 10, [ADR 0011](../docs/adr/0011-who-writes-the-words.md) amendment).
2. Five new scans on AI text, built in stage 1 (Spec 6.2, [ADR 0012](../docs/adr/0012-missing-unsure-and-evidence-failures.md) amendment, the stage 1 plan).
3. A lint for fixed copy in the project check (testing strategy section 12).
4. The source line moves under "More".
5. Read banners shrink to chips.
6. A first review preselects a copy of the starter.
7. "Show on the page" keeps the panel open.
8. Two stray controls are removed: "Test this rule" and "Replay tips".
9. One rewrite button is removed: the rewrite dialog keeps "Use as suggestion" only.
10. Text at 200% must fit a 1366 px window (testing strategy section 9).
11. No praise, including in the practice review.

The spec, the system design, the testing strategy, the copy deck, the design system, the prototype and the stage 1 plan were updated to match. Two details of the new scans were open as question 18 of the stage 1 plan, and the owner decided them the same day (Spec 6.2). The lint script, `scripts/copy_lint.py`, was then built and wired into `scripts/check.sh`, and the layout at 150% and 200% text was fixed so that no page scrolls sideways in a 1366 px window.
