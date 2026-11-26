# Stage 5 reader checks and limits: what to change in the stage 5 plan

**Written 26 Nov 2026.** This report tests questions 6 to 21 of section 6 of `docs/plans/stage-05-ingest-word-pdf.md` against six sets of research notes. The plan is a Draft and its owner answers for these rows are empty. The report recommends. It decides nothing and edits no plan, no table and no expected value (Constitution T11). It is not legal advice.

**Scope.** Questions 1 to 5 are decided (system design 15.5) and are not reopened. They are used as background only: the memory floor and the 60 s limit (Q1), the render cost and the glyph-loop timing (Q2), the hidden-text rule for `links` and `privacy` (Q3), the rebuilt list number in `Document.text` (Q4), and the splitter tests on side text (Q5).

**How each question is laid out.** Each section opens with one plain sentence and one small example. Then it gives (a) the plan's choice, (b) a verdict, (c) graded evidence, (d) options with effects, (e) a recommendation, (f) what would change it, and the gaps. Verdicts are KEEP (the plan's choice holds), CHANGE (the notes contradict or extend it), or NEEDS OWNER DECISION (the notes found a point that is the owner's call). A section can carry two verdicts. Points that the notes call "a question for the owner" or "a design choice for the planner" are marked **[OWNER]** or **[PLANNER]** and are not decided here.

**Where the numbers live.** The folder `research_notes/` is git-ignored. The measurements exist only in the notes and in this report. No contract text, party name or person name appears here. All test text in the notes is made up.

**Source grades.** The notes grade every claim. This report keeps the grades in square brackets:

| Grade | Meaning |
| --- | --- |
| primary | The researcher read the standard, the manual, the source file or the vendor page. |
| measured | The researcher ran it on one machine: Debian 13, x86_64, Python 3.13.5, pypdfium2 5.15.2 (PDFium 159.0.8149.0), pikepdf 10.18.2, ReportLab 5.1.0, lxml 6.1. Linux only. |
| repo | The researcher read it in this repo. |
| search summary | Seen only in a web-search summary. The page was not read. |
| memory | The researcher's own knowledge, not re-checked. |
| inference | A conclusion drawn from the other grades. |

A claim with no grade is a repo fact or a statement of the plan. Where the notes give a URL, it is linked. A claim with no URL in the notes carries its grade only.

**What the notes did not do.** Nothing was run on Windows. Nothing was run on Python 3.12 (only wheel lists were read for 3.12). No real contract file, no Word-saved `.docx`, no scanner PDF and no PDF from Word, LibreOffice or Acrobat was measured. Word and LibreOffice were not installed. Every test file is synthetic. Where a figure comes from one run, the notes say so.

## Executive summary

The plan's direction holds on most of the sixteen questions. Research changes the detail on all of them, and on seven it contradicts a sentence or a number of the plan. The plan's own numbers for hostile-file limits (Q11), the hidden-text thresholds (Q10) and the digit rule for furniture (Q13) need the most change. The largest open choices for the owner are the Unicode policy and licence (Q6), how an OCR text layer is treated (Q10, Q12), the hostile-file budget (Q11), the paragraph-join rule and the shape of moves (Q16), the words for an encrypted Word file (Q17), and what to do with a PDF that forbids copying (Q18).

**Verdicts at a glance.**

| # | Question | Verdict | One-line reason |
| --- | --- | --- | --- |
| 6 | Unicode checks and the match key | CHANGE, NEEDS OWNER DECISION | The planner's option leaves tag characters, variation selectors and LRM/RLM in the match key. `confusables.txt` is under the Unicode License v3, not MIT, BSD or Apache |
| 7 | Windows CI | CHANGE | Stage 5 is right. The job should start at M2, not M6-T7. The repo has no `.gitattributes` |
| 8 | Nightly job and fuzzing | KEEP, CHANGE detail | Atheris installs on Linux x86_64 only and does not see native code. A `conftest` must register the nightly profile |
| 9 | Test-only tools | KEEP, CHANGE detail | ReportLab writes every hiding case. Rotate with pikepdf. Pillow arrives anyway. The grey-mask design is open |
| 10 | Hidden-text thresholds | CHANGE, NEEDS OWNER DECISION | One small source, no independent check. Spread 24 is 1.24 to 1. Mode 3 flags every OCR scan. Font size must be drawn size |
| 11 | Hostile-file limits | CHANGE, NEEDS OWNER DECISION | 100 to 1 per member rejects real files. The page cap does not protect the 60 s limit. 200 MB of XML cannot be parsed in 1 GB |
| 12 | Scanned page | CHANGE, NEEDS OWNER DECISION | Right on 10 of 12 fixtures. A signature page is named scanned. An OCR scan is not scanned and is all mode 3 |
| 13 | Furniture | CHANGE | Replace each run of digits, not each digit. The band and half-of-pages rule have false positives |
| 14 | Generated flag and `None` | KEEP, add rules | Only space, CR and LF are generated. Build per character. An unmapped font gives wrong letters |
| 15 | Reading order | KEEP, CHANGE wording | PDFium follows the stream. Geometric breaks do not fix row-wise columns |
| 16 | Tracked changes | CHANGE, NEEDS OWNER DECISION | A deleted paragraph mark merges two paragraphs. The shape cannot show a move |
| 17 | Encrypted `.docx` | CHANGE, NEEDS OWNER DECISION | The "old Word file" line is wrong for an encrypted `.docx`. A directory check separates three cases |
| 18 | Owner-password PDF | KEEP, NEEDS OWNER DECISION | PDFium opens it and reads all text. A no-copy flag is reported, not enforced |
| 19 | The PDF sample | KEEP, CHANGE detail | Vera is embedded and licensed. `invariant=1` is stable. Mark the PDF binary in `.gitattributes` |
| 20 | `PageBox` on rotated or cropped pages | KEEP, add rules | The notes give the exact conversion. Off-page characters need a rule |
| 21 | White or tiny text in Word | CHANGE, NEEDS OWNER DECISION | `FFFFFF` only misses near-white, same-colour and theme colours. Never flag five listed cases |

**Where the notes disagree with the plan, in one place.**

1. Q6. The plan leaves both match-key changes to stage 8. The notes show `fold_for_matching` drops only 15 characters, so a hidden `non<tag>compete` is flagged but still missed by keyword matching until stage 8.
2. Q7. The plan puts the Windows job at S5-M6-T7. The child memory limit lands at S5-M2-T5, so the first Windows test of that limit comes at the end of the stage.
3. Q9. The plan says Pillow's licence is HPND. The notes read the installed metadata as MIT-CMU. Both are permissive. The name should be checked before it is written down.
4. Q10. The plan uses the five values "tuned on the test set". The notes show the text API gives the nominal font size, not the drawn size, and has no render mode.
5. Q11. The plan's 100 to 1 ratio rejects a legitimate 157 to 1 and 208 to 1. Its 200 MB total cannot be tree-parsed inside 1 GB. Its 1,000-page cap does not protect the 60 s limit.
6. Q12. The plan's rule names a signature page as scanned, and it says nothing about an invisible OCR layer.
7. Q13. The plan says "with digits replaced". Replacing each digit breaks the rule at page 10.
8. Q15. The plan says line breaks come "from the glyph geometry". That does not fix columns drawn row by row.
9. Q16. The plan says a deletion and an insertion by one author are one change and lists moves. It does not say how two paragraphs join when a paragraph mark is deleted, and the shape cannot mark a move.
10. Q17. The plan's "known limit" sends the user to "save as .docx" for a file that already is `.docx`.
11. Q20. The plan does not say what the reader does with characters outside the page.
12. Q21. The plan's rule is `FFFFFF` and no shading. The notes list the cases it misses and the cases it must never flag.

**Owner decisions this report asks for.** Eleven points need an owner answer before the planner writes the tasks. The table at the end lists them with the exact open point.

## Q6. Which Unicode checks stage 5 builds, and whether the match key changes

**What this is about.** Some characters are invisible or look like another letter, and they can hide a word from a search or a reader. **Example:** a contract says "non" then an invisible character then "compete". A person sees "noncompete". A keyword search for "noncompete" finds nothing.

**(a) Plan's choice.** Build zero-width, bidi and tag-character checks now. Add `TAG_CHARACTER` to `HiddenReason`. Leave confusables and both match-key changes to stage 8. Record the line-end hyphen as a known limit.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.** The planner's licence point is right. The planner's choice leaves a gap that is cheap to close.

**(c) Evidence.**

*Licence of `confusables.txt`.*
- The file is a Unicode "Data File" under the Unicode License v3, SPDX `Unicode-3.0`. The file header points to the Terms of Use. [primary: [confusables.txt](https://www.unicode.org/Public/security/latest/confusables.txt), [Terms of Use](https://www.unicode.org/copyright.html)]
- The licence grants use, copy, modify, distribute and sell "without restriction" if the copyright and permission notice travel with copies or documentation. It adds a no-endorsement clause. It is the shape of MIT plus a BSD-3 clause. [primary: [license.txt](https://www.unicode.org/license.txt)]
- OSI approved it on 17 November 2023 as a "Special Purpose" licence. [search summary: [SPDX](https://spdx.org/licenses/Unicode-3.0), [Unicode FAQ](https://www.unicode.org/faq/unicode_license)]
- The two PyPI packages are poor sources. `confusable-homoglyphs` 3.3.1 is MIT on PyPI, archived on GitHub since January 2024, and its MIT file does not carry the Unicode notice. `confusables` 1.2.0 is from 2021 and has an empty licence field. [primary: [PyPI](https://pypi.org/pypi/confusable-homoglyphs/json), [PyPI](https://pypi.org/pypi/confusables/json)]
- Any derived table is still Unicode data, so the notice must travel with it. Whether a short hand-typed list of about 20 lookalikes is free of the licence is unsettled. [inference]
- Size of the 18.0 file: 763 KB, 6,712 mappings, 2,148 with an ASCII target, 93 of them Cyrillic or Greek letters. Accented Latin letters such as `é`, `ü` and `ñ` have no entry. [measured]

*What `fold_for_matching` does today.*
- `core/match_fold.py` `_DROPPED` holds 15 characters: 00AD, 200B to 200D, 2060, FEFF, 202A to 202E, 2066 to 2069. `fold_for_quote_check` drops nothing. [repo]
- Run on "non" plus one character plus "compete": U+00AD is dropped. U+E0020 (a tag space), U+FE0F, U+034F, U+2062, U+180E, U+061C, U+200E, U+200F and U+206A are **not** dropped. U+3164 folds to U+1160 and stays. A Cyrillic `а` in "аgency" stays Cyrillic. [measured]
- `match_fold.toml` has cases for soft hyphen, zero-width space and a bidi control. It has none for tags, variation selectors or LRM/RLM. Only the owner edits it (T11). [repo]

*What is hidden, and by which channel.*
- All the sets named are Default_Ignorable_Code_Point. [primary: [DerivedCoreProperties.txt 17.0.0](https://www.unicode.org/Public/17.0.0/ucd/DerivedCoreProperties.txt)]
- Variation selectors are category `Mn`, not `Cf`. The Hangul fillers are letters (`Lo`). So a "category Cf" test misses both. [measured, stdlib Unicode 15.1]
- Trojan Source (CVE-2021-42574) uses bidi controls. The advice is to warn on bidi controls and mixed-script identifiers. [primary: [trojansource.codes](https://trojansource.codes/)]
- Tag characters mirror ASCII, render invisible, and a model still reads them. The stated mitigation is to filter tag code points. [primary, read through a summariser: [Embrace The Red](https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/)]
- Variation selectors can carry a hidden payload, one byte per selector. The strongest source is the arXiv paper. [search summary: [arXiv 2510.05025](https://arxiv.org/abs/2510.05025)]
- UTS #39 builds its skeleton by NFD, removing Default_Ignorable, mapping to a prototype, NFD. It warns that both detections "will flag many legitimate strings". [primary, read through a summariser: [UTS #39](https://www.unicode.org/reports/tr39/)]
- Legitimate uses in English text: a BOM at file start, a soft hyphen from Word or PDF, a ZWSP after a slash, LRM/RLM from web copy or Hebrew and Arabic names, ZWNJ/ZWJ in emoji and Persian text, U+FE0F after an emoji. [memory for all but the BOM and soft hyphen, which are repo facts]
- Tags have no use in English contract text. Their one supported use is an emoji flag sequence. [memory]

*Mixed-script check with the standard library.*
- There is no `unicodedata.script()`. The usual trick reads the first word of the character name. [measured]
- "Müller", "Café", "Ångström", "Łódź" and "İstanbul" are single-script and raise no alarm. A Cyrillic-lookalike "раураl" and a Greek-Alpha "Αpple" are flagged. "μm", "Ωmega" and "Σtrategy" are also flagged, and are legitimate in a technical contract ("5 μg", "10 Ω"). [measured]
- Misses: `ı` (starts with LATIN), `ℓ` (starts with SCRIPT), and a word written wholly in Cyrillic lookalikes. [measured; the whole-script limit is an inference from the definition]

*The line-end hyphen.*
- Tools join a line-end hyphen only with a dictionary or word-frequency list, and keep compounds such as "high-quality". [search summary: [Freiburg thesis](https://ad-publications.informatik.uni-freiburg.de/theses/Bachelor_Mari_Hernaes_2019.pdf), [pypdf docs](https://pypdf.readthedocs.io/en/6.18.0/user/post-processing-in-text-extraction.html), [pdf_oxide](https://docs.rs/crate/pdf_oxide/0.3.30/source/src/text/hyphenation.rs)]
- The testing strategy says for `ingest`: "A line-end hyphen is kept." [repo] A reader that joined would change the canonical text.
- A real "-" at a line end followed by a line break folds to "non- compete", so keyword "noncompete" misses in a PDF. [inference]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| A. The plan: flag zero-width, bidi, tags. No fold change, no confusables | No new owner decision except the tier policy. One enum member. Leaves hidden-character evasion in the match key and leaves confusables neither flagged nor matched |
| A+. Option A plus a stdlib mixed-script flag | Detects Latin plus Cyrillic always, Greek only when lookalike-prone. Needs no data file. Needs a new member (or reuse). Misses whole-script and `ı`-type lookalikes. Accents never trigger |
| A with the cheap fold fix | Add the other Default_Ignorable characters to `_DROPPED`. A `core` change, new owner-table cases written by the owner (T11). No licence issue. Makes the key agree with the UTS #39 step |
| B. Confusables now | Needs a licence decision, a subset choice (6,712, about 2,150 or about 95 rows), a vendoring and version policy (stdlib is Unicode 15.1, the file is 18.0), a `core` fold change, owner-table cases, a licence-page entry and a generation script. Risk: the table is tuned for identifiers, not prose |
| Hyphen join | A stage 8 `core` change with a "try both forms" key, or a recorded known limit. No licence issue |

**(e) Recommendation.**
1. Keep the plan's first step and extend it. Flag by a per-character policy with three tiers: never flag (BOM at index 0 only, soft hyphen); always flag (all tag characters, 202A to 202E, 2066 to 2069, and ZWSP, ZWNJ, ZWJ, WJ and BOM not at the start); judgement tier (LRM, RLM, ALM, variation selectors). A run of two or more variation selectors, or one after an ASCII letter or digit, is not a legitimate use. **[OWNER]** or **[PLANNER]**: which tier each character takes. The notes call this their own inference. A false alarm costs a Read first row (Rule 9).
2. Add `TAG_CHARACTER` and, for variation selectors, either `VARIATION_SELECTOR` or reuse of `ZERO_WIDTH` (D5 allows a member). All checks are pure functions over `Document.text` in `ingest`. The "unreadable spans" input of Rule 9 picks up every `HiddenText.span` for free.
3. Close the fold gap in stage 5 by extending `_DROPPED`. It is small, needs no data file and no licence decision. **[OWNER]**: it edits `core` and the owner table. The cost of not doing it is that stage 5 flags a hostile `non<tag>compete` and keyword matching still misses it until stage 8. The notes could not check how stage 8 uses the fold, and did not check who else calls `fold_for_matching` (privacy, links).
4. Leave confusables folding to stage 8. **[OWNER]**: accept `Unicode-3.0` for a shipped data file, by a fourth named exception in Spec 13 and an ADR amendment, or read it as equal to BSD. Say "Unicode License v3" in the record, not "Terms of Use". The two PyPI packages are not suitable sources. Vendor the file directly if wanted.
5. Offer the stdlib mixed-script flag (Option A+) as an extra, with a short Greek exception list. **[OWNER]** or **[PLANNER]**: accept the false-alarm rule.
6. Keep the line-end hyphen as a known limit for stage 8, with the "match either form" idea.
7. Paired fixtures: hostile (a tag string spelling an instruction, an RLO reversing a number, a ZWSP inside "non-compete", a Cyrillic `а` in "terminаtion"); innocent (a BOM at index 0, a soft hyphen, a Hebrew name with an RLM, an emoji with U+FE0F, "Müller", "Ångström", "5 μg"). A ZWSP in a URL can be hostile or innocent by policy. **[OWNER]**.

**(f) What would change this.** A Word or PDF measurement showing how often real exports contain ZWSP or LRM would move characters between tiers. A decision that stage 8 builds the match key with its own sanitiser would make point 3 less urgent. A legal reading that a short hand-typed lookalike list is free of the licence would remove the licence blocker for a small table.

**Gaps.** No standards body says which sets to flag in plain text (UTS #39 covers identifiers). UTR #36 and the AWS article body were not read. Character frequency in real contracts is unmeasured. `regex` Script_Extensions support and licence were not checked. The OSI and SPDX pages were read only as summaries. False alarms were counted on hand-made tokens only. All work sizes are estimates.

## Q7. Does the Windows CI job join in stage 5 or stage 6

**What this is about.** The app must run on Windows as well as Linux, and a Windows test machine finds problems that Linux cannot. **Example:** a test passes on Linux but fails on Windows because Windows has no `resource` module to cap a child's memory.

**(a) Plan's choice.** Stage 5. The job runs `scripts/check.sh` on `windows-2025` without the highlight pictures. It lands at S5-M6-T7.

**(b) Verdict: CHANGE.** Stage 5 is right. The timing and the scope need detail.

**(c) Evidence.**
- `windows-2025` is a GitHub-hosted label, generally available since April 2025. `windows-latest` moved to Server 2025 in September 2025. [primary for existence: [runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [changelog Apr 2025](https://github.blog/changelog/2025-04-10-github-actions-macos-15-and-windows-2025-images-are-now-generally-available)] A later move to Visual Studio 2026 is announced. [search summary: [changelog May 2026](https://github.blog/changelog/2026-05-14-github-actions-upcoming-image-migrations)]
- Wheels exist for win_amd64 on cp312 and cp313 for pikepdf 10.18.2, lxml 6.1.3 and lingua 2.2.0. pypdfium2 5.15.2 has one `py3-none-win_amd64` wheel. nupunkt and reportlab are pure Python. Installing on Windows was not tested. [primary: [pikepdf](https://pypi.org/pypi/pikepdf/json), [pypdfium2](https://pypi.org/pypi/pypdfium2/json), [lxml](https://pypi.org/pypi/lxml/json), [lingua](https://pypi.org/pypi/lingua-language-detector/json)]
- The current workflow has one Linux job on Python 3.12. `scripts/check.sh` is bash, and prefers `.venv/bin/uv`, which does not exist on Windows. [repo]
- The repo has no `.gitattributes`. [repo, measured]
- The plan requires the child limit "on Linux and Windows" at S5-M2-T5. [repo]
- Cost: Windows 2-core is $0.010 a minute against $0.006 for Linux, about 1.67 times. Standard runners in public repos are free. Private repos have a monetary allowance. Whether the repo is public was not checked. [primary: [billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)]
- Hypothesis's built-in `ci` profile is derandomised, so Windows runs the same examples as Linux. [primary and measured: [Hypothesis docs](https://hypothesis.readthedocs.io/en/latest/reference/api.html)]
- Likely breakages, none observed: the `check.sh` shell path; no `RLIMIT_AS` on Windows (the most likely failure); CRLF conversion of goldens and samples by `actions/checkout`; path and open-file-lock behaviour; spawn instead of fork for child tests; console encoding under cp1252. [inference and memory]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| A. Job at M6-T7 (plan) | The Windows memory method is first tested at the end. A breakage there costs rework in M2 |
| B. Job at M2, with the child process | Finds the Windows limit and path problems at the same price. Needs the shell step and `.gitattributes` early |
| C. Run commands directly on Windows, not `check.sh` | Avoids the bash issue. Two command lists to keep in step |

**(e) Recommendation.** Keep stage 5. Bring the job forward to the milestone that adds the child process (M2), and add a new task for `.gitattributes`. **[PLANNER]**: the exact milestone. Use `shell: bash` for `check.sh` and make sure the `uv` on PATH branch works. Add `.gitattributes` with `* text=auto eol=lf`, or `eol=lf` for samples and goldens, and `binary` for the committed PDF sample. Run all tests except the highlight pictures. Add a Windows over-limit allocation test (Q1 background). Keep the pinned `windows-2025` label.

**(f) What would change this.** If the repo is private and the Windows run is slow, the job could run on pull requests to `main` only. If a first Windows run shows the child limit needs a larger rewrite, an earlier job is worth more, not less.

**Gaps.** Run time on `windows-2025` is unknown. Whether the repo is public is unknown. Git Bash finding `uv` after `setup-uv` was not verified. Python 3.12 and 3.13 on `windows-2025` was not verified. Nothing was run on Windows or on 3.12.

## Q8. What the nightly job runs, and which fuzzing tool

**What this is about.** A nightly job runs heavy tests while nobody is working, including tests that feed damaged files to the reader. **Example:** the job flips one byte in a sample PDF 2,000 times and checks that the reader always gives a `Document` or a named error, never a crash.

**(a) Plan's choice.** Nightly: property tests at 2,000 examples and the Hypothesis file mutation test at a larger count. Add Atheris only after a check shows it installs on the CI Python. Otherwise record a known gap.

**(b) Verdict: KEEP, CHANGE detail.**

**(c) Evidence.**
- PyPI lists three files for atheris 3.1.0: cp312, cp313 and cp314 `manylinux2014_x86_64` wheels. There is no Windows, macOS, aarch64 or source file. [primary: [PyPI](https://pypi.org/pypi/atheris/json)]
- `pip install atheris` on 3.13.5 worked from the wheel with no compiler. A harness ran 2,000 runs and printed "no interesting inputs were found so far. Is the code instrumented for coverage?" because nothing was instrumented. The 3.12 wheel exists but was not run. [measured]
- libFuzzer is inside the wheel. [measured]
- Native extensions (pdfium, libqpdf, libxml2) are not instrumented in wheels. [memory]
- Hypothesis can mutate a saved file's bytes with a custom strategy. 300 single-byte edits of a ReportLab PDF through pypdfium2 ran in about 1 s with no crash. `test.hypothesis.fuzz_one_input(bytes)` drives a `@given` test from an external fuzzer. There is no ready "mutate this file" strategy in `hypothesis.extra`. [measured]
- Hypothesis has no profile environment variable of its own. Profiles are registered and loaded in code. The built-in `ci` profile uses `derandomize=True`, so a nightly run with only `CI=true` repeats the same examples every night. [primary: [Hypothesis docs](https://hypothesis.readthedocs.io/en/latest/reference/api.html), partly read; measured]
- A scheduled workflow runs only on the default branch, and GitHub disables schedules after 60 days of inactivity on public repos. [memory]
- The Atheris wheel has an empty licence field. A LICENSE file is inside, not read. [primary]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| A. Hypothesis only | Works on both systems. No new dependency. Guided by Python code only |
| B. Add Atheris on the Linux nightly | A dev dependency with a platform marker. Python coverage guidance only. No Windows |
| C. Atheris drives the Hypothesis test through `fuzz_one_input` | Extra glue. Same native-code blind spot |
| D. python-afl or pythonfuzz | Not researched |

**(e) Recommendation.** Keep Hypothesis as the nightly tool. Add a `conftest` that registers a `nightly` profile (2,000 examples, `derandomize=False`, a cached or no database) chosen by an environment variable the workflow sets. Add a byte-mutation strategy built in-repo. Treat Atheris as optional: if added, mark it Linux x86_64 only and record the known gap "no native-code guidance and no Windows fuzzing". The plan's wording "install check" is now answered for Linux 3.13 (measured) and 3.12 (wheel listed). **[OWNER]**: accept the Atheris gap, which the plan already allows. Add `workflow_dispatch` beside the schedule.

**(f) What would change this.** A native-code crash found by a different tool would justify an instrumented build. If the repo goes private and quiet, the 60-day schedule rule matters more.

**Gaps.** Atheris on 3.12 was not run. Its README on instrumentation was not fetched. python-afl and pythonfuzz were not researched. The schedule rules are from memory. The Hypothesis page was read only in part (100,000 of 132,655 characters).

## Q9. Which test-only tools write the fixture PDFs and compare the pictures

**What this is about.** The tests need PDF files with known contents, and pictures to compare. Some tool has to write them. **Example:** a test PDF with one line of white text at a known position, and a saved picture to show where a highlight box lands.

**(a) Plan's choice.** ReportLab as a dev dependency to write fixture PDFs. `pikepdf` adds the switched-off layer. `pypdfium2` renders to a raw buffer. Pillow as a dev dependency to read and write PNG pictures.

**(b) Verdict: KEEP, CHANGE detail.**

**(c) Evidence.**
- ReportLab 5.1.0 wrote white text, 1.5 pt text, render mode 3, fill alpha 0, clipped-out text, a crop box and a page rotation. pypdfium2 returned the text of every one. [measured]
- `setPageRotation(90)` swapped the MediaBox to `[0 0 841.89 595.28]` with `/Rotate 90`. Text at y=700 then fell off the page and the render was blank. Rotating with pikepdf (`pg.Rotate = 90`) kept the box and rendered normally. [measured]
- `Canvas(..., invariant=1)` gave byte-identical files in two builds, also with an embedded Vera font. With `invariant=0` they differed. One environment only. [measured]
- pikepdf wrote an optional-content group switched off. PDFium still extracted its text. Whether PDFium hides the layer in a render was not tested. [measured]
- `page.render(scale=1.0, grayscale=True, no_smoothtext=True, ...)` gave a 1-byte-per-pixel bitmap with only grey levels 255 and 0 on text, and the same hash on two renders. [measured]
- A standard-library PNG writer (about 10 lines, `zlib` and `struct`) produced a file that Pillow opened. [measured]
- Licences: reportlab BSD, pypdfium2 BSD-3-Clause or Apache-2.0, lxml BSD-3-Clause, pikepdf MPL-2.0, Pillow MIT-CMU. [primary: PyPI metadata; measured for Pillow]
- Pillow is installed in any case as a dependency of pikepdf and ReportLab. Avoiding a direct import saves nothing in the lock. [measured, `pip show`]
- uv supports dependency groups (PEP 735). `--group dev` is already used in CI. [primary: [uv docs](https://docs.astral.sh/uv/concepts/projects/sync/)]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| Pillow as a direct dev dependency | Easy PNG read and write. The owner can open the files. No extra lock cost |
| Standard-library PNG writer | About 10 lines. Reading needs filter handling. Saves a direct import only |
| Raw buffers or text masks | Smallest. The owner cannot open the files in a viewer |

**(e) Recommendation.** Keep ReportLab and pikepdf as dev tools. Write fixtures with ReportLab, and rotate with pikepdf, not `setPageRotation`. Build fixtures with `invariant=1` and place text with the swapped box in mind. Keep Pillow as a direct dev dependency, because it arrives anyway. Correct the plan's licence word: the notes read MIT-CMU, and the plan says HPND. Both are permissive, and the licence rule covers the runtime group only. **[PLANNER]**: the pixel-mask design. A greyscale render has one channel, so a "highlight colour" cannot be seen. The mask needs either the highlight drawn at a distinct grey level or a separate overlay. The notes did not test either. Add a rule that no dev tool is imported under `src/`; `import-linter` does not check it.

**(f) What would change this.** If mypy strict on `scripts` rejects the ReportLab, pikepdf or pypdfium2 stubs, fixture builders move to `tests/` or get `ignore_missing_imports`. If a later ReportLab version breaks `invariant=1` stability, a "rebuild and compare bytes" test would fail, so the plan's word-level test is the safer one.

**Gaps.** Whether PDFium hides an OFF layer in a render is untested. `invariant=1` was measured in one environment only. mypy behaviour was not tested. The Atheris LICENSE was not read.

## Q10. Are the hidden-text thresholds right

**What this is about.** The reader flags text a person cannot see. It needs numbers for "too faint", "too small" and "almost invisible". **Example:** a "DRAFT" watermark in pale silver is normal, but white text on a white page is a hiding trick. A single number must tell them apart.

**(a) Plan's choice.** Contrast spread under 24 of 255, font under 2 points, opacity under 0.1, a box off the page, render mode 3. Each `[Assumption]`, tuned on the test set. Six-point small print and light watermarks stay unflagged.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.**

**(c) Evidence.**

*Where the numbers come from.*
- They match one small detector: MIT licence, one contributor, 11 stars, a regression set of 14 documents (7 hide text, 7 look-alikes). It leaves unflagged white text on a coloured banner or an image, OCR layers (reported as information), light watermarks and 6 pt small print. [primary, README: [hidden-text-detector](https://github.com/wppoland/hidden-text-detector)] The earlier report found its "tested" claim unconfirmed. [repo]
- A second scanner flags near-white fill and text under 2 pt, and stopped flagging white text over a dark shape after a false alarm. [primary: [pdf-injection-scanner](https://github.com/Andy8647/pdf-injection-scanner)]
- PhantomLint uses no thresholds. It renders, runs OCR and compares with the extracted text. On 3,257 papers it gave 3 false alarms (about 0.092 percent). The detector README says it takes about a minute a document. [primary, paper section 5.2: [arXiv 2508.17884](https://arxiv.org/html/2508.17884v1)]
- New York CPLR 4544 voids consumer-contract print under 8 points (5.5 for capitals). Small print of 6 to 8 pt is real in contracts. [search summary: [nysenate.gov](https://www.nysenate.gov/legislation/laws/CVP/4544)]
- WCAG 2.2 asks 4.5 to 1 for normal text and 3 to 1 for large text. Text "not visible to anyone" has no requirement. [primary: [SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)]

*Measured contrast.*
- A spread of 24 grey levels is a ratio of 1.24 to 1 against white. A spread of 137 is 4.5 to 1. Spread 12 is 1.1 to 1, 45 is 1.5, 72 is 2.0, 107 is 3.0. [measured]
- Flagged at under 24: grey #F0F0F0, #FAFAFA, #FFFFFF 10 pt (15, 5, 0); white on #F2F2F2 (12); black on black (0); black 10 pt at alpha 0.3, 0.2, 0.1, 0.05 (22, 10, 2, 0); "DRAFT" 80 pt silver #C0C0C0 at alpha 0.25 (16, a false alarm for a watermark). [measured]
- Not flagged: grey #E6E6E6 10 pt (25, one level over); "DRAFT" silver at alpha 0.5 (32, eight levels of margin); white on light grey #D9D9D9 (37, a ratio of about 1.4 to 1, barely visible, a miss). Black 1 pt has spread 75, so the size check must catch it. [measured]
- A watermark text box: one dark pixel in the box (a border, an underline, neighbouring text) makes max minus min large and hides white text next to it. [inference, not tested]
- At 72 and 144 dpi the spreads moved by 0 to 25 levels for faint grey, and thin small text gets lighter at low scale (black 1 pt: 75 at 72 dpi, 150 at 144 dpi). The threshold is tied to the scale. [measured]

*Measured API limits (pypdfium2 5.15.2 raw).*
- `FPDFText_GetFontSize` returns the nominal `Tf` size. Text set with `1 Tf` and a 10 times matrix reports 1.0 pt but draws 10 pt. The matrix is in `FPDFText_GetMatrix`. The drawn size is the font size times the matrix scale. `Tz` is not in the size. [measured]
- Fill alpha is in `FPDFText_GetFillColor`. Alpha 0.1 reads 26 of 255, so "under 0.1" (25.5) does not flag an alpha of exactly 0.1. [measured]
- The text-page API has no render mode. `FPDFTextObj_GetTextRenderMode` on the page object gives 3 for mode 3. Scanning every text object of a dense page took 0.26 ms. The object-to-character link was not tested. PDFium returns mode-3 text through normal extraction, with colour black and alpha 255, so the text API shows no sign of invisibility. [measured]
- Render mode 3 is "neither fill nor outline", is not specific to OCR, and OCR software uses it for its invisible layer. [search summary: [Apryse](https://apryse.com/blog/pdf-hidden-text-layer-ocr-visible), [ocrmypdf man page](https://manpages.debian.org/testing/ocrmypdf/ocrmypdf.1.en.html)]
- PDFium drops a duplicate text object and keeps the first drawn. A white copy drawn under a black one is read with the white fill. (Q14 note.) [measured]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| 1. Keep the five values | The first OCR scan and the first low-alpha silver watermark give false hidden-text banners |
| 2. Separate OCR layers: most glyphs of a page in mode 3 plus a large image gives a notice, not a finding; isolated mode-3 spans stay findings | Removes the largest false alarm. Adds a rule and a fixture. A hostile layer inside a real OCR page is missed |
| 3. Lower the spread (about 12) or measure on glyph pixels only | Fewer watermark false alarms. More misses |
| 4. Raise the spread (about 40) | Catches white on #D9D9D9 (37) and silver at alpha 0.5 (32). Flags light watermarks the report says to leave alone |
| 5. Use drawn size | Needed for correct results. One matrix read per glyph |
| 6. Read render mode per text object | 0.26 ms a dense page. Needs an object-to-character link, untested |
| 7. Drop the opacity check | Little lost on text over white. One constant fewer |
| 8. Keep each constant in one place marked `[Assumption]`, with a fixture pair for each | Matches the plan's tuning approach |

**(e) Recommendation.**
1. Font under 2 pt on the **drawn** size (font size times matrix scale). Never use the nominal size. This is needed, not optional. It flags nothing legitimate, because real small print is 6 to 8 pt.
2. Read render mode through the page-object call. Link objects to characters, and test that link first. **[PLANNER]**.
3. Read opacity as fill alpha under 26 of 255 if the check stays. It overlaps the contrast check on white, so dropping it is also fine.
4. Contrast: keep the check but treat 24 as a weak starting value. On the table, a threshold between 12 and 16 would stop flagging the alpha 0.25 watermark (16) and still flag white on white. The #F2F2F2 case has spread 12, so a rule "under 12" would miss it. The rule would have to read "at most 12", with no margin. This is the notes' reading of the table, not a validated value. **[OWNER]**: which side to err on, because the faint band between 1.24 and 3 to 1 is unreadable but unflagged either way.
5. Render mode 3 is safe only if whole-page OCR layers are separated first (Option 2). **[OWNER]**: this is one decision with Q12 and Rule 9 (see Cross-cutting findings).
6. Write the fixtures far from each threshold, so the tests do not depend on a one-level difference. Pairs: silver watermark at alpha 0.25 and 0.5, 6 pt and 7 pt footnote, white on navy, white on #F2F2F2, an OCR page.
7. Write into the threat list: text under other text or a photo is a known miss.

**(f) What would change this.** A real contract set would show how often watermarks, "DRAFT" stamps, grey footers and white-on-dark headings occur. The final render scale (Q2) moves the spreads. If the owner wants no thresholds, PhantomLint's render-and-OCR approach exists, at about a minute a document and with an OCR dependency that Spec 12 excludes.

**Gaps.** No real contract set. Word's default watermark and how Word's PDF export writes it were not confirmed. Off-page text threshold form (whole box or partly, any margin) was not researched. Word-side thresholds were not tested here. The detector's code was not read for this question. Anti-aliasing at the final render scale is not fixed.

## Q11. What are the hostile-file limits

**What this is about.** A damaged or hostile file can be tiny on disk and huge when opened. The reader needs limits that stop such a file without stopping real files. **Example:** a 20 MB `.docx` that expands to 20 GB when unzipped.

**(a) Plan's choice.** At most 2,000 zip members; 200 MB expanded in all; a ratio of at most 100 to 1 for each member; XML nesting at most 256; 1,000 PDF pages; 60 seconds; 1 GB for the child. All `[Assumption]`.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.**

**(c) Evidence.**

*Zip and Word.*
- Apache POI defaults: minimum inflate ratio 0.01 (100 to 1), 4 GB per entry, 1,000 files, a 100 KiB grace size below which the ratio check is skipped, 10 MiB of text. It checks while reading, not from declared sizes, and rejects duplicate names. [primary: [ZipSecureFile.java](https://raw.githubusercontent.com/apache/poi/trunk/poi-ooxml/src/main/java/org/apache/poi/openxml4j/util/ZipSecureFile.java), [javadoc](https://poi.apache.org/apidocs/dev/org/apache/poi/openxml4j/util/ZipSecureFile.html)] The plan's 100 to 1 equals POI's default. POI's count is half the plan's.
- CPython `zipfile` was patched against quoted-overlap bombs (CVE-2024-0450). [search summary: [Openwall](https://www.openwall.com/lists/oss-security/2024/03/20/5), [CVE record](https://www.cve.org/CVERecord?id=CVE-2024-0450)]
- OWASP says to apply the size limit after decompression and count bytes while streaming. [search summary: [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)]
- Real-shaped `.docx` files from python-docx (not Word-saved): 50,000 words 92 KB (document.xml 369 KB, 6.6 to 1); plus ten JPEGs 9.7 MB (1.1 to 1); three flat 3000x2000 BMP screenshots 123 KB for 18.8 MB expanded, the BMP member **208 to 1**, total **155 to 1**; a table-heavy repetitive file, document.xml **157 to 1**, total 42 to 1. A legitimate file can exceed 100 to 1 on one member. [measured] Word-saved XML is usually larger than python-docx output. [memory]
- Deflate cannot exceed about 1,030 to 1 (1 GiB of zeros gave 1,043,638 bytes). Inflating 1 GiB took 2.4 s. [measured]
- A central directory that lies low is caught by "Bad CRC-32"; the real expansion is bounded by the declared size, so a declared-size check before reading is sound. Duplicate names give a warning and `read()` returns the last. Two entries on one local header give only a `UserWarning` for the first. 230,000 empty members fit in 19.5 MB and took about 1 s and 141 MB to open. [measured]
- lxml with `huge_tree` off, entities off, no network: depth 256 parses and 257 fails; a single text node of 9 MB parses and 11 MB fails; entities are not expanded. A 51 MB XML took 1.4 s and about 680 MB more (about 13 times). Under a 1 GB address-space limit a 50 MB tree worked (778 MB) and 75 MB failed, as `XMLSyntaxError` "unknown error", not `MemoryError`. `iterparse` with clearing used 116 MB for 50 MB and 417 MB for 200 MB, at about three times the time. [measured]

*PDF page count, time and memory.*
- Time follows characters, not pages. At about 9 µs a character through the raw API: 100 pages of 500 words 3.0 s; 1,000 pages of 500 words 32 s; 1,000 dense pages (8.7 million characters) **83 s**. The Spec 9 limit of 50,000 words is about 3 s. [measured] The Q2 background figure was about 62 s for 1,000 dense pages (62.5 ms a page). The two sets of runs differ, per-character cost varies by about 10 percent between runs, and one cold run was twice as slow.
- A dense page costs about 100 ms in all (records 83, render 4.4, contrast 16). Peak memory stayed at 23 to 27 MB. [measured]
- A 12000x17000 JPEG page rendered in 155 ms. A Flate 20000x20000 grey image (381 MB raw, 390 KB in the file) took 1.26 s and 436 MB. The same image on 20 pages took 25 s. On 1,000 pages (658 KB file) it was still running after 70 s. A 40000x40000 image was skipped by PDFium. [measured]
- The Q1 background floor is about 80 MB for the imports. [repo, from the earlier report]

**(d) Options and effects** (from the notes; effects only).

| # | Option | Effect |
| --- | --- | --- |
| 1 | Keep 60 s and 1,000 pages | Legitimate files (3 to 10 s) pass. A 1,000-page dense text file and an image bomb both end as a timeout, so the error cannot say "too many words" |
| 2 | Stop reading when the running word count passes 50,000 | Text PDFs cost at most about 3 to 6 s. Right error early. No help for image pages |
| 3 | Lower the page cap (for example 500) | Rejects without a read. 50,000 words at 100 words a page is 500 pages, so do not go lower. No help against image bombs |
| 4 | Time limit as a function of pages | More time for big files, and a render bomb gets more time too (the 20-page bomb took 25 s) |
| 5 | A soft per-page budget in the child, with the parent's kill as the backstop | Names the failing page. The worst legitimate page was about 0.1 s and the bomb page 1.26 s, on this machine only |
| 6 | Cap each tree-parsed part near 32 to 40 MB, or use `iterparse` for large parts | Keeps inside 1 GB. A 200 MB cap with a tree dies at about 75 MB with an unhelpful error that must be mapped to a named memory error |
| 7 | Apply the ratio only to parsed parts above a grace size (POI: 100 KiB), or drop it and cap each declared size | No false alarm on BMP or TIFF media |
| 8 | Convert zip overlap warnings to errors | The overlap fix exists from 3.8.19, 3.9.19, 3.10.14. The app ships its own Python |

**(e) Recommendation.** **[OWNER]**: the relation between pages, time and memory. The notes list effects and do not choose. On the evidence, a combination of Options 2, 5, 6 and 7 fits best:
- Keep the 60 s hard kill. Stop reading text when the running word count passes 50,000, so a long text PDF ends with the right error in seconds.
- Add a soft per-page budget in the child (value on this machine between 0.1 s and 1.26 s, so a few seconds; it moves with the machine), with the hard kill kept as the backstop. This is the only guard that names an image bomb.
- Keep 1,000 pages as a cheap pre-check, not as the time guard. Do not go below 500.
- Replace the 200 MB total with a per-part cap on **parsed** parts (document, numbering, styles, notes, comments, headers, footers, rels) near 32 to 40 MB. Media never needs inflating. Map the lxml "unknown error" to a named memory error.
- Apply the ratio only to parsed parts above a grace size, or drop it. 2,000 members is twice POI's 1,000, and far above the 17 to 27 measured. Read the member count from the end-of-central-directory record before `ZipFile()` opens it. The exact member figure matters little.
- Check the declared size before reading, count real bytes while reading, and turn overlap warnings into errors. Decide duplicate member names (POI rejects them; Word's own choice was not found).
- The 1 GB figure means address space on Linux and committed memory on Windows (Q1 background). A single hostile page can reach the limit.

**(f) What would change this.** Real Word-saved files with large parts would move the per-part cap. A slower target machine moves the per-page budget and the 60 s. A decision to render pages for contrast on every page (Q2) raises the per-page cost. If the owner prefers one simple number, Option 1 is acceptable, with a timeout as the only message.

**Gaps.** No real Word-saved file was measured. No corpus of contracts. Windows commit behaviour and the job object were not tested. How Word treats duplicate names and overlaps was not found. No source for PDF object-count limits (Azure's 2,000 pages and 500 MB is a search summary about a hosted service). The contrast cost for a normal page and the pikepdf layer cost were not measured. A decompression bomb in a non-image filter (JBIG2, CCITT, object streams) was not tested. The scratch scripts were lost; the numbers are the record and should be re-run before relying on the last digit.

## Q12. What counts as a scanned page

**What this is about.** A scanned page is a picture of a page, with no real text in it. The reader must tell it from a page that is simply short. **Example:** a page that says only "This page is intentionally left blank" has few letters but is not a scan.

**(a) Plan's choice.** A page is scanned when it has fewer than 50 readable characters (not white space, not undecodable) **and** at least one image. A short page with no image is read as it is. A PDF with no readable page raises `ScannedPdfError`.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.**

**(c) Evidence.** All fixtures are synthetic, one page each. [measured]
- Raw object types: 1 text, 2 path, 3 image, 4 shading, 5 form. A form's children come from `FPDFFormObj_CountObjects` and `FPDFFormObj_GetObject`. `page.get_objects(max_depth=5)` recurses into forms. `PdfImage` has `get_bounds()`. [measured]
- Results against the plan's rule:

| Fixture | Readable chars | Plan's rule |
| --- | --- | --- |
| Plain text, 10 lines | 740 (908 counted by `CountChars`: 18 generated line breaks, 150 spaces) | not scanned, correct |
| Image only, area 100% | 0 | scanned, correct |
| Scan plus invisible OCR layer, all text objects mode 3 | 740 | not scanned (all text is invisible) |
| Vector drawing only | 0 | not scanned: an empty page |
| Image inside a form XObject, area 8% | 0 | scanned only if the walk recurses; a top-level count says no image |
| Inline image | 0 | scanned |
| Blank page | 0 | not scanned |
| "This page is intentionally left blank." | 33 | not scanned, correct |
| Signature page: 2 lines plus a 120x40 pt scanned signature, area 1% | 33 | **scanned**, probably unwanted |
| Letterhead: logo (0.3%) plus 2 sentences | 132 | not scanned |
| White text on white | 198 | not scanned (the hidden-text check must catch it) |
| A line of 70 spaces | 0 | not scanned |

- `FPDFText_CountChars` counts generated characters and real spaces. A readable count must skip them. [measured]
- A font with no `/ToUnicode` can give wrong-looking letters with the Unicode-error flag set on every character. Counting them as readable would pass a scanned-page test while the text is wrong. (Q14 note.) [measured]
- Scanners and OCR tools usually add an invisible mode-3 text layer. [memory]
- Annotations such as stamps and signature widgets are not page objects, so `FPDFPage_CountObjects` does not count them. [inference, not tested]
- A PDF of outlined text has no characters and no image. The rule reads it as empty, not scanned, and `ScannedPdfError` would name it wrongly. [inference from the vector and blank fixtures]

**(d) Options and effects.**
- Signature page: (a) accept it; (b) require the image to cover a share of the page (100% for scans, 8% form image, 1% signature, 0.3% logo; any threshold such as 50% is untested and an `[Assumption]`); (c) accept it and word the warning as "has little text".
- OCR-layered scan: (a) leave it. It is "not scanned" by Spec 9, and under a mode-3 hidden-text check every word is flagged and every value is unsure (Rule 9). (b) Count invisible characters as not readable. The page is then "scanned" and has no text for the AI, which matches Spec 12 (no OCR) and throws away usable OCR text. (c) Treat it as a notice, not a finding (Q10 Option 2).
- No-image arm: raise on no readable page regardless of images (as the plan does), and use the image test only to choose which pages to name in a mixed file.

**(e) Recommendation.**
1. Keep the plan's two-part rule. Count readable characters per page as: not white space, not generated, not `umerr`, not in {U+0000, U+FFFD, U+FFFE, controls}. This links to Q14.
2. The image walk must recurse into form XObjects. Its cost was not timed.
3. Raise `ScannedPdfError` on no readable page, and use the image test to name pages in a mixed file. The error name is slightly wrong for a vector-only or all-blank PDF. **[PLANNER]**: whether to add a separate message.
4. **[OWNER]**: the OCR-layer treatment. This is one decision across Q10, Q12, S5-M5 and Rule 9. The leaning of the notes is that leaving it makes the whole file unsure and that separating OCR layers (Q10 Option 2) removes the largest false alarm. The owner decides.
5. **[OWNER]** or **[PLANNER]**: signature-page handling, and whether to add an image-area share. The 50% idea is untested.

**(f) What would change this.** Real scanner PDFs (tiled strips, masked images, clipped images) would change the image rule. A decision to read OCR layers in version 1 would reverse Spec 12.

**Gaps.** No real scanner or Word/LibreOffice PDFs. No multi-image or tiled scans, masked images, clipped images or pages with very many objects. No fixture with Unicode-map errors. The 50-character figure and the 50% area idea have no source. Spec 9 says "tuned in testing".

## Q13. How furniture is found

**What this is about.** Some PDFs repeat a line at the top or bottom of every page, such as "ACME Services Agreement" or "Page 3 of 12". The reader has to decide which lines are that kind of repeated line. **Example:** "Page 3 of 12" on every page is furniture. A clause that happens to appear twice is not.

**(a) Plan's choice.** A line in the top or bottom 8% of the page height whose folded text, with digits replaced, repeats on at least half of the pages and at least 3 pages. A document of 1 or 2 pages has no furniture. Values `[Assumption]`.

**(b) Verdict: CHANGE.**

**(c) Evidence.**

*The tag.*
- Through the raw API, `FPDFPageObj_GetMark` and `FPDFPageObjMark_GetName` return `Artifact` for text inside `/Artifact << /Type /Pagination /Subtype /Header >> BDC`. The keys `Type` and `Subtype` are readable. Their name values (`/Pagination`, `/Header`) cannot be read with `FPDFPageObjMark_GetParamStringValue`: it returned false. The same value written as a text string `(Header)` did read. The structure tree does not list artifacts. [measured; artifact-outside-tree rule: [search summary: W3C PDF14](https://www.w3.org/TR/WCAG20-TECHS/PDF14.html), [WTPDF 1.0](https://pdfa.org/wp-content/uploads/2024/02/Well-Tagged-PDF-WTPDF-1.0.pdf)]
- pikepdf `parse_content_stream` gives the full operand dictionary (`/Type /Pagination`, `/Subtype /Header`), and a stack pairs each `Tj` with its open `BDC`s. [measured]
- The standard allows running headers and footers to be marked as Pagination artifacts. [search summary: [W3C PDF14](https://www.w3.org/TR/WCAG20-TECHS/PDF14.html), [Beacon](https://beaconaccessibility.com/docs/pdf/checkpoints/18-headers-footers/)] ISO 32000 was not read.
- In one author's sample of 60 datasheets, about 25 declared Header or Footer artifacts and 4 more had `/Pagination` without a subtype (about 29 of 60). The same project uses 60% of pages for constant text and 50% for varying text. [primary page, small and unrepresentative: [pdf_oxide issue 2285](https://github.com/yfedoseev/pdf_oxide/issues/2285)]
- Docling uses a layout model, not repetition. [search summary: [docling-models](https://huggingface.co/docling-project/docling-models)]

*The repetition rule on 12-page Letter fixtures.* A line is built from character origins, split at a baseline change. [measured]

| Case | Result |
| --- | --- |
| Header with page number, none on page 1 | found on 11 of 12, correct |
| Footer "Page 3 of 12" | found on 12 of 12, correct |
| Replace each digit, not each digit run | "Page # of ##" on 9 pages, header on 8: pages 10 to 12 become "##". A 20-page file would drop the footer after page 9 |
| Header changes by chapter (3 chapters of 4 pages) | each on 4 of 12: missed. A 30% rule finds them |
| Odd and even pages with different headers | each on 6 of 12: found, because "half" is inclusive |
| Contract line repeated in the body at mid-page | outside the band, correct |
| Same line in the top band (tight 36 pt margins) | found on 12 of 12: a **false positive** |
| Footer with a changing figure "Fee: GBP 1,037" | digits to `#`, found 12 of 12: a **false positive** |
| Header plus right-aligned roman page number on one baseline | lines merged by baseline: missed. Splitting a line at a gap over 3 times the glyph height gave the title and the number separately |
| Band 5% against 8% | matters little on a 1-inch margin |
| Band 12% | body lines at 9% from top enter the band: a numbered first body line becomes furniture on all 12 pages |
| 3 of 5 pages; 3 of 6 pages | found. A 2-page file has none by design |

- "Half the pages" is a common choice in other projects. "8%" and "3 pages" have no source found. [search summary: [rag-vs-agent-bench PR 29](https://github.com/Swayam-Ch/rag-vs-agent-bench/pull/29), [arXiv 2506.18027](https://arxiv.org/pdf/2506.18027), [arXiv 2508.13833](https://arxiv.org/pdf/2508.13833)]
- A share-of-height band is about 67 pt on A4 and 63 pt on Letter. [inference]
- No source was found for GROBID, pdfminer, pdfplumber or `pdftotext` header rules. [search summary and memory]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| 1. Repetition only (plan) | No new code path. False positives on repeated band lines. Misses chapter headers and 1 to 2 page files |
| 2. Tag first through pikepdf, repetition for untagged pages | Catches chapter headers and short files when tagged. Adds a content-stream parse of every page (cost not timed) and another place for hostile input |
| 3. Tag only | No body-text false positives. Misses about half of real files |
| 4. Repetition plus a gap split of lines | Fixes header plus roman number. Adds line-split code |

**(e) Recommendation.**
1. Replace each **run of digits** (`\d+`) with one marker, not each digit. This changes the plan row's wording.
2. Keep the band at 8% and the half-of-pages rule with the 3-page floor as `[Assumption]`s. Do not widen the band. Chapter-changing headers are a known limit.
3. Digit folding makes data lines in the band repeat ("Fee: GBP #"). **[PLANNER]**: either fold digits only for a candidate that also matches a page-number shape ("Page # of #", "- # -", a bare number), or accept the false positives. The cost of a false positive is real: a line marked furniture is not sent to the AI. Furniture is only marked, never removed (D1), and stage 8 decides what is sent (Q3 background).
4. Split a line at a wide horizontal gap (over about 3 times the glyph height) before the repetition test. **[PLANNER]**.
5. The tag can support the rule but not replace it. **[OWNER]**: whether to read tags through pikepdf, at the cost of a content-stream parse of every page. The notes did not time it and did not show which producers write the tag.
6. Fixtures: a header on 11 of 12 pages, odd and even headers, a body line repeated mid-page, a repeated band line with tight margins (false positive), a data line in the footer, and a header with a roman page number.

**(f) What would change this.** Real Word, LibreOffice and law-firm PDFs would show how often headers are tagged and how often chapter headers occur. A measured false-positive rate on real contracts would move the band and the digit rule. If stage 8 sends furniture to the AI anyway, a false positive costs less.

**Gaps.** No real PDF with headers, no facing-page layout, no two-line headers, no footnotes in the bottom band, no table rows in the bottom band. No source for how Word or LibreOffice mark headers in PDF output. ISO 32000 was not read. Whether the string-value failure is PDFium or pypdfium2 behaviour was not checked. Only build 5.15.2 was tested.

## Q14. Do PDFium's glyph flags decide a `char_map` entry of `None`

**What this is about.** PDFium adds spaces and line breaks of its own and marks them. The app must say which characters of the text have a real glyph on the page. **Example:** a line ends and PDFium adds a line break. That break has no ink, so it points to no glyph.

**(a) Plan's choice.** A character PDFium marks as generated gets `None` in `char_map`. Only characters with a real glyph get a glyph index.

**(b) Verdict: KEEP, add rules.**

**(c) Evidence.**
- `FPDFText_IsGenerated` is true only for a space inserted between text objects and for CR and LF. No letter, digit or hyphen was ever generated. [primary: [cpdf_textpage.cpp](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/core/fpdftext/cpdf_textpage.cpp), [fpdf_text.cpp](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/fpdfsdk/fpdf_text.cpp); measured on three fixtures] The source read is `main`, not the exact tag of build 159.0.8149.0.
- A generated character has a zero-size box at the line end, at the previous character's origin plus advance. It can fall outside a cropped page. A real space has a box of height 0.01. [measured; primary for `GenerateCharInfo`]
- Line-end hyphen: when the line ends in U+002D or U+00AD, the character before is alphabetic and the next object starts alphanumeric, PDFium retypes that character as a hyphen, sets `GetUnicode` to 0x2, writes U+FFFE into the text buffer, and drops the CR/LF after it. PDFium cannot tell a wrap hyphen from a real one ("self-" flagged the same). [primary and measured]
- Unicode-error flag: set when a font gives no Unicode for a non-zero code. A Type0 Identity-H TrueType font with no `/ToUnicode` gave "7HUPIHH" for "Term fee" with the flag set on every character, because the glyph id was used as the code point. The letters look plausible. `pdfplumber` read the same file correctly. [measured]
- A `/ToUnicode` entry mapping to U+FFFD gives flag 0 and stays U+FFFD. An entry to U+0000 gives flag 0 and U+FFFE in the text. An entry to U+FFFE gives flag 0 and the character is left out. So "undecodable" must also count U+FFFD, U+FFFE, U+0000 and controls. [measured]
- The char list and the text can differ in length. `FPDFText_GetText` leaves out 0x2, 0x3, 0x93, 0x94, 0x96 to 0x98 and U+FFFE (except a hyphen). 104 chars gave 101 text characters on one fixture, and 8 gave 7 on another. An astral character came as two UTF-16 halves with one box, but one Python character in `get_text_range`. [primary and measured] On Linux only; Windows `wchar_t` is 16 bits, untested.
- Ligatures: PDFium expands one glyph into one character per letter, all with the same box (`fi` gives `f`, `i`; `/ffi` gives three). All have `gen=0`. [primary and measured]
- Duplicate glyphs: PDFium drops a second copy at object level (same codes, same size, overlap, start within 0.9 of the first character width, within 1/8 of the box height) and per character. Offsets up to 5 pt gave one copy; 10, 16 and 24 pt kept both. The first copy drawn stays, with its own fill. A white copy drawn under black stays white. [primary and measured]
- `(cid:N)` is a pdfminer artefact. PDFium uses the code or glyph id with the error flag. [measured]

**(d) Options and effects.**

| Case | Option | Effect |
| --- | --- | --- |
| Ligature | A. One `Glyph` per PDFium char | Two glyphs with identical boxes. A highlight draws the box twice |
| | B. Merge chars with the same object, code and box into one `Glyph`; point both `char_map` entries at it | One glyph per drawn glyph. The glyph count is below `CountChars`. Needs a rule to tell a ligature from a repeat (PDFium removes stacked copies first) |
| | C. First letter gets the glyph, later letters `None` | A quote starting on the second letter has no box |
| Line-end hyphen | A. Write "-" into the text with the hyphen's real glyph index | Reads "contract-ual". Matches the plan |
| | B. Remove it | Breaks the kept-original rule |
| Unmapped chars | 1. Count only `umerr=0` and not in the bad set | `q14_cid`-type files are not counted readable |
| | 2. Also count `umerr=1` as readable | Wrong-looking letters pass a scanned test |

**(e) Recommendation.** Keep the plan's rule. It holds as written. Add these rules **[PLANNER]**:
1. Build the canonical text character by character from `FPDFText_GetUnicode` with the char index kept, not from `get_text_range`. Otherwise length and index drift.
2. Say how each case is mapped: ligature (B is the most consistent with "one entry per character of text", but is a **[PLANNER]** choice), line-end hyphen (A), generated space, CR and LF (`None`), PDFium-dropped characters.
3. Use Option 1 for unmapped characters. The "undecodable" test must not trust the flag alone.
4. The app has to insert its own line break after a flagged hyphen if it wants one (as a `None` entry).
5. Fixtures: an embedded Identity-H font without `/ToUnicode`, a `/ToUnicode` to U+FFFD, a ligature, a line-end hyphen, a stacked duplicate, an astral character.

**(f) What would change this.** A Windows run (16-bit `wchar_t`) could change surrogate handling. A real Word PDF could change ligature behaviour. A fixture with a hidden duplicate (white under black) would show only the first copy, which the hidden-text check must account for.

**Gaps.** Not measured on Windows. No real Word PDF with real ligatures. No 32-bit cmap font for astral characters. No vertical or right-to-left text, no text in Form XObjects, no ActualText. Why a real space has height 0.01 was not traced. The 50-character count was reasoned, not run.

## Q15. Which reading order the canonical text uses

**What this is about.** A PDF is a list of drawing instructions. The reader has to put the text in the order a person reads it. **Example:** a two-column page. If the PDF draws left and right columns row by row, the text comes out as left line, right line, left line, right line.

**(a) Plan's choice.** The order of PDFium's text page, with line breaks inserted from the glyph geometry. No column detection. A two-column fixture records what happens as a known limit until the golden set shows a need.

**(b) Verdict: KEEP, CHANGE wording.**

**(c) Evidence.** One-page synthetic fixtures. [measured]
- Character index order equals the content-stream order, and `FPDFText_GetCharBox` follows that index. PDFium adds a line break only when the next text object starts on a new baseline.
- Column-wise streams read correctly. Right column drawn first: right column first. Row by row: both columns merged on one line per row. Lines drawn bottom to top, or 3, 1, 4, 2: read in that order. A table drawn column by column glued "10" and "3" into "103". A superscript "1" after "full" produced a line break mid-sentence.
- Short objects of 1 to 2 characters glued to the previous line (`103`, `abc`, `125`, `403`, `1037`), even at 84 pt vertical distance. No generated break marks the join. The cause was not found. The pattern fits "the second object has fewer characters than the first and is at most 2 long" (inference).
- A page with `/Rotate 90` returned three lines drawn 1, 2, 3 as 3, 2, 1. `/Rotate` 0, 180 and 270 returned 1, 2, 3. Char boxes stay in unrotated space. The cause was not found.
- The splitter on text built in each order: column order gave clauses 1.1, 1.2, 2.1, 2.2; row order merged lines and lost clauses 2.1 and 2.2 inside 1.1 and 1.2 (a number mid-line is not a clause start); reversed order made one clause "2.2" with 5 sentences.
- A wrong order does not break the quote check or the highlights, because both use `char_map`. A quote across a column break can point at two disjoint boxes. [inference; the highlight part was not tested]
- ADR 0007 says two-column reading order is not benchmarked, and sets the golden set as the trigger. [repo]
- Alternatives: pdfminer.six layout analysis (second PDF library; ADR 0007 rules out run-time cross-checks); pdfplumber `use_text_flow` (follows the stream); poppler `pdftotext` (GPL, which the runtime licence rule excludes); Docling (heavy, already rejected in the architecture report). XY-cut libraries were not surveyed. [search summary for pdfminer, pdfplumber and poppler: [pdfminer docs](https://pdfminersix.readthedocs.io/en/latest/reference/composable.html), [pdfplumber issue 982](https://github.com/jsvine/pdfplumber/issues/982), [pdftotext man page](https://manpages.debian.org/testing/poppler-utils/pdftotext.1.en.html); memory for licences]
- A tension to resolve: the Q19 note says white and invisible lines drawn at different y came back "y-sorted, not stream-ordered". The Q15 fixtures were built to test order and show stream order. The Q19 remark was incidental and is unverified. [measured, both]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| 1. PDFium order as is | No code. Row-wise columns and glued objects enter the text |
| 2. PDFium order plus geometric line breaks | Small code. Fixes gluing and merged cells when a break is warranted. Does **not** fix columns drawn row by row |
| 3. Sort glyphs by lines then blocks (XY-cut) | Fixes shuffled, reversed and row-wise columns. A few hundred lines (estimate). Risk of a wrong guess on tables, sidebars, footnotes and rotated text. Text order then differs from PDFium's, but `char_map` stays valid |
| 4. pdfminer layout | Adds a runtime library. Against ADR 0007's direction |

**(e) Recommendation.** Keep the plan's choice as a known limit, and change its wording: line breaks from geometry fix gluing and superscript cuts, but they do not fix row-wise streams. Build the lines from character baselines (the notes' line builder used origin y in 3 pt steps and had no gluing failures on these fixtures), which costs one pass the glyph loop already makes. **[PLANNER]**: the line builder. Keep the two-column fixture and add a reversed-stream fixture and a `/Rotate 90` fixture to record the limits. A row-wise column fixture shows clauses lost to the splitter, so say that in the stage notes. **[OWNER]**: if the owner wants a user-facing warning when two glyph lines share a baseline with a wide gap, the notes could not say how often that false-alarms on tables.

**(f) What would change this.** The golden set showing real contracts with row-wise or shuffled streams is the trigger ADR 0007 names. Real Word and LibreOffice PDFs are said to draw columns column-wise [memory], which would make the plan's choice enough.

**Gaps.** Nothing run on Windows. No real two-column contract or real producer. No right-to-left, vertical text or real table borders. The cause of the gluing and the `/Rotate 90` reversal was not found. No source on how often contract PDFs use each stream order. pdfminer, pdfplumber and poppler come from search summaries and memory. XY-cut libraries were not surveyed.

## Q16. Which Word changes are tracked changes, and how they are grouped

**What this is about.** Word records edits as tracked changes: text added, text removed, text moved. The reader must show what the contract says after all changes are accepted, and list the changes. **Example:** "30 days" is crossed out and "60 days" is inserted. The accepted text says "60 days" and the list shows one change.

**(a) Plan's choice.** List insertions, deletions and moves. A deletion next to an insertion by the same author is one change (`earlier` and `new` both set). A formatting-only change is not listed. `span` covers the new wording and is `None` for a pure deletion.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.**

**(c) Evidence.**
- `w:del` marks content as deleted. Its text is in `w:delText`. It can sit in the body, paragraphs, hyperlinks, content controls, table cells, rows, comments, footnotes, endnotes, headers and footers, and it can nest with `w:ins`, `w:moveFrom`, `w:moveTo`. [primary: [Learn: DeletedRun](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.deletedrun)]
- A deleted paragraph mark (`w:pPr/w:rPr/w:del`): the paragraph's contents "are combined with the following paragraph". [primary: [Learn: Deleted](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.deleted)] The published text of the inserted-mark entry says the same merge, which looks like a copy-paste error and must not be read as a merge. [primary, with the error noted: [Learn: Inserted](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.inserted)]
- A deleted row does not mark its cells' text as deleted. The cells are revision-marked independently. `w:cellDel`, `w:cellIns` and `w:cellMerge` exist. [primary: [Deleted](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.deleted), [CellDeletion](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.celldeletion)]
- `w:numberingChange` applies only to a `LISTNUM` field. [primary: [Learn](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.numberingchange)]
- Run, paragraph, section and table property changes hold the **previous** properties inside the `*PrChange` child. The current properties are the siblings. [memory, checked indirectly: every library showed the current state]
- `w:moveFrom` and `w:moveTo` wrap source and destination. The `w:name` on the range markers pairs them. [primary for the element list, memory for the pairing]
- Measured on a 10-case file:

| Case | pandoc accept | mammoth | docx2python | python-docx `paragraph.text` |
| --- | --- | --- | --- | --- |
| `30` deleted, `60` inserted | correct | correct | correct | "due in  days." (inserted text missing) |
| Deleted paragraph mark | merged, one space added | merged, no separator | two paragraphs | two paragraphs |
| `moveFrom` / `moveTo` | correct | correct | source kept, sentence twice | source dropped, destination lost |
| `rPrChange` | current | current | current | n/a |
| Paragraph and its mark deleted | gone | gone | blank lines | blank paragraphs |
| Inserted paragraph | kept | kept | kept | missing |
| Inserted row / deleted row | kept / dropped | kept / dropped | kept / blank cell | both missing |

  `--track-changes=all` keeps both wordings with no separation ("3060"). python-docx has no tracked-change handling and loses every inserted word, which matches ADR 0007 option C. [measured]
- pandoc maps `ins` and `moveTo` to insertion and `del` and `moveFrom` to deletion, and has no clause for `rPrChange` or `pPrChange`. [search summary of source: [pandoc Parse.hs](https://raw.githubusercontent.com/jgm/pandoc/main/src/Text/Pandoc/Readers/Docx/Parse.hs)]
- LibreOffice fixed several bugs in move and paragraph-mark import (tdf#145718, tdf#149711, tdf#151954). [search summary: [bug 149711](https://www.libreoffice.org/bugzilla/show_bug.cgi?id=149711)] It shows that paragraph marks in moves are where readers go wrong.
- The `TrackedChange` shape (earlier, new, author, span) fits `ins`, `del` alone, `del` next to `ins`, and row and cell changes if the reader collects the row text itself. It cannot show a move as a move, a paragraph join, or an insert-then-delete by two people. [inference from `core` and ADR 0012]
- A hostile file can put `w:t` inside `w:del`. Word shows it as deleted. [spec text and tests]

**(d) Options for the paragraph-mark join** (effects):

| Option | Effect |
| --- | --- |
| A. Join with no separator (mammoth) | The accepted view as Word shows it. "text.Clause" has no sentence break for the splitter |
| B. Join with one space (pandoc) | Protects sentence splitting. Adds a character not in the file. The Word `Document` has no `char_map`, so nothing marks it. There is precedent: the rebuilt list number (Q4, decided) is also a character put into the Word text |
| C. Keep the break and note the merge | Not the accepted view. Conflicts with ADR 0012 |

Edge cases need a rule: the deleted mark is the last paragraph of a cell or body, the next block is a table, the next paragraph is wholly deleted, a chain of deleted marks. Only the simple case was measured.

**(d) Options for moves:** show as plain delete plus insert (the user cannot tell it is a move), pair by the range name and add a field (a `core` change), or leave as plain with a note.

**(e) Recommendation.**
1. Accept the plan's grouping and its decision not to list formatting changes (consistent with ADR 0012, which speaks of earlier and new wording).
2. Read the current `w:rPr`, `w:pPr` and `w:numPr` directly. Never search descendants. The old values sit inside `*PrChange`. (Cross-cutting.)
3. Drop all content of a `w:del` or `w:moveFrom`, whatever the child tag (`w:t`, `w:delText`, `w:instrText`, `w:delInstrText`). Ignore `w:delText` outside `w:del`.
4. The accepted view needs a block-level pass for paragraph marks and moves, not a run-level pass. None of the five libraries replaces the own reader.
5. **[OWNER]**: the join rule (A, B or C). The notes give effects and do not choose. The evidence shows that A and B each have a cost on the splitter or on the "no invented characters" side.
6. **[OWNER]**: how a move is told apart from a delete plus an insert. The shape has no field. The plan says "list moves", and the shape cannot show them as such.
7. **[PLANNER]**: insert-then-delete by two authors (one change with the deleter as author, two changes, or leave out); a missing `w:author` (what to show); `del` next to `ins` needs a "next to" rule (Word writes `del` then `ins` with proof marks, bookmarks or empty runs between, and dates can differ).
8. **[PLANNER]**: tracked changes in comments, notes, headers, footers and text boxes. By the decided design, side text is outside `Document.text`. Text boxes are read once (decided), so their changes must be counted once, or the "N changes" notice doubles.
9. Fixtures: replacement by one author, deleted paragraph mark, move across paragraphs, `rPrChange`, deleted row, `w:t` inside `w:del`, nested ins and del by two authors, and a change in a text box.

**(f) What would change this.** Word's own accepted result for the merged paragraph (which `pPr` and which list number survive) is unchecked. A Word or LibreOffice render may show different paragraph properties. If the owner accepts a `core` field for "moved", moves become faithful.

**Gaps.** Word's accept result and the surviving list number were not checked. LibreOffice was not run. Exact ISO wording for the property changes and the move range elements was not retrieved. No tests for changes in footnotes, comments, headers, text boxes or nested changes. MS-OI29500 notes were not read. Which splitter number survives a merge is memory at best.

## Q17. What about an encrypted `.docx`

**What this is about.** A Word file with a password has the same outer format as an old `.doc`. A simple check calls both "old". **Example:** the user loads a password-protected `.docx` and is told "save it as .docx", which it already is.

**(a) Plan's choice.** Version 1: every OLE2 file raises `OldWordFileError`, and an encrypted `.docx` is a known limit. The other way adds an `EncryptedWordFileError` to `core`, a new copy line and a reader for the OLE2 directory.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.**

**(c) Evidence.**
- An encrypted OOXML file is a compound file with `EncryptedPackage`, `EncryptionInfo` and a `\x06DataSpaces` storage. [primary: [MS-OFFCRYPTO 2.3.4.4](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-offcrypto/b60c8b35-2db2-4409-8710-59d88a793f83), via a search summary]
- A `.docx` encrypted with msoffcrypto-tool 6.1.0 begins `d0cf11e0a1b11ae1` and shows exactly those streams. The same file unencrypted begins `504b0304`. [measured]
- An old `.doc` has a `WordDocument` stream plus `0Table` or `1Table`. A password-protected `.doc` stays a `.doc` with `fEncrypted` set, so it shows `WordDocument`. It is a third case. [primary via search summary: [MS-DOC 2.1.2](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/44f62054-d911-4989-946c-a42100c26a15), [MS-DOC 2.2.6.2](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/3e9a4e92-bdfe-4379-8144-74d033892ede)] No real `.doc` was available, so the names were not seen in a measured listing.
- A directory-only reader (header, DIFAT chain, FAT, directory walk) is 28 lines and printed the full name set for the encrypted file. It has no bounds checks. A hardened version is probably 35 to 50 lines plus tests. [measured on one positive case]
- CFB header and directory layout. [primary: [MS-CFB 2.2](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/05060311-bfce-4b12-874d-71fd4ce63aea)] The directory entry layout used came from memory and one working test.
- `olefile` 0.47 is BSD (Dec 2023). `msoffcrypto-tool` 6.1.0 is MIT, needs `cryptography>=39.0` and `olefile>=0.46`, and reads encrypted `.docx` and RC4 `.doc`. Decrypting needs a password prompt, which is out of the spec. [primary: [olefile](https://pypi.org/pypi/olefile/json), [msoffcrypto-tool](https://pypi.org/pypi/msoffcrypto-tool/json), [README](https://github.com/nolze/msoffcrypto-tool)]
- The repo says only "an old Word file (.doc)" blocks Continue. The copy line is "This is an old Word file. Open it in Word, save it as .docx, then load that." There is no encrypted Word error and no ux-copy line for an encrypted PDF. [repo: `docs/spec.md`, `docs/ux-copy.md`, `core/errors.py`]
- An encrypted `.xlsx` or `.pptx` renamed to `.docx` has the same streams. Only the extension differs. [measured stream set; inference]

| File | What the user sees today | What would be correct |
| --- | --- | --- |
| Old `.doc` | "old Word file, save as .docx" | Correct |
| Encrypted `.doc` | same | Half right (saving needs the password they have) |
| Encrypted `.docx` | same | **Wrong.** It already is `.docx`. The user must remove the password, save, load again |

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| 1. Plan v1: every OLE2 file is an old Word file | Zero code. Wrong advice for an encrypted `.docx`. The user can loop |
| 2. Own directory check plus a new `core` error plus one copy line | Right message. No new dependency. Changes `core` (errors, system design 3.4, README) and ux-copy |
| 3. As 2, with `olefile` | Fewer own lines. One more runtime dependency that parses hostile input. Last release December 2023 |
| 4. One neutral message for every OLE2 file | Right for both, less specific. A copy change only |

**(e) Recommendation.** Option 1 is wrong for the user, so change it. The least costly correct answer is Option 4 for version 1, for example "This Word file is old or has a password. In Word, remove the password and save it as .docx, then load that." It needs no new error and no code. Option 2 gives a precise message for the cost of a `core` error and about 35 to 50 lines. **[OWNER]**: the words, because the copy deck belongs to the owner and must meet the ux-copy rules (third person, no filler), and the choice between Option 4 and Option 2. If Option 2 or 3 is chosen, the directory check runs inside the child (Q1), the missing bounds checks must be added, and `olefile` is allowed by the BSD rule. Decrypting stays out of scope. Add a fixture of an encrypted `.docx` and an encrypted `.doc`.

**(f) What would change this.** A real `.doc` listing could change the names. A decision to decrypt would add `msoffcrypto-tool`, `cryptography` and a password prompt, and reopen the spec.

**Gaps.** No real `.doc`. Directory entry offsets were not re-read in the spec. The `olefile` licence text was not opened. `cryptography`'s licence was not re-checked. Nothing was run on Windows.

## Q18. What about a PDF with an owner password only

**What this is about.** A PDF can have two passwords: one to open it and one to change its rules. A file with only the second one opens without a password. **Example:** a PDF that anyone can open, but whose author has switched off "copying text".

**(a) Plan's choice.** Read it as a normal PDF. `EncryptedPdfError` only when a password is needed to open it.

**(b) Verdict: KEEP, NEEDS OWNER DECISION.**

**(c) Evidence.** [measured, pypdfium2 5.15.2; PDFium codes from [primary: fpdfview.h](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdfview.h)]
- `FPDF_GetLastError` codes: 0 success, 1 unknown, 2 file, 3 format, 4 password, 5 security (unsupported scheme), 6 page.
- Owner password only (user empty), in AES-256, AES-128, RC4-128 and RC4-40: opens with no password and the text reads. Security revisions read 6, 4, 4, 2.
- A user password set: `PdfiumError` with `err_code` 4 for no password and for a wrong password. The two cannot be told apart.
- Permission bit "extract" cleared, user password empty: opens and reads in full. `FPDF_GetDocPermissions` shows the extract bit as 0. Opening with the owner password reads all allowed.
- An unknown security handler gives code 5. Garbage, empty or truncated bytes give code 3.
- After a successful open, `FPDF_GetLastError()` can still hold a stale 4 from an earlier failed open. Use the exception's `err_code`.
- pikepdf opens owner-only files and reports `is_encrypted`, `encryption.R` and `allow.extract`. It raises `PasswordError` for a user-password file. `pdfplumber` read the owner-only and no-copy files and raised `PDFPasswordIncorrect` for the user-password file.
- PDFium reports the copy bit and `pypdfium2` does not enforce it. No PDFium source file was read to confirm it is deliberate.
- The repo has `EncryptedPdfError` with code `encrypted_pdf` and no more detail. Spec 9 lists "PDF with real text". The spec and ux-copy say nothing about an encrypted or no-copy PDF. [repo]

**(d) Options and effects** for a file that forbids copying:

| Option | Effect |
| --- | --- |
| 1. Read as normal (what PDFium does) | Simplest. Matches the plan's "no password needed means read it" |
| 2. Read and show a notice that the author asked for no copying | One warning code and one copy line. Tells the user what the author asked |
| 3. Refuse with `EncryptedPdfError` | Blocks contracts the user may be entitled to review. PDFium cannot enforce it, so it would be only an app rule |

**(e) Recommendation.** Keep the plan: catch `PdfiumError` with `err_code == 4` at open and raise `EncryptedPdfError`. Use `err_code`, not `FPDF_GetLastError`. **[PLANNER]**: whether code 5 is `EncryptedPdfError` or `UnreadableFileError`, and code 3 and a missing file (`FileNotFoundError`, not `PdfiumError`). A warning for a readable encrypted file is possible with `FPDF_GetSecurityHandlerRevision` (not -1). **[OWNER]**: the no-copy question, Options 1, 2 or 3. The notes found no source on what the PDF specification, any licence or any law says about reading such a file, and ADR 0016 says the project has no lawyer. Option 1 is the plan's answer and the simplest. **[OWNER]**: the words for `EncryptedPdfError`, which ux-copy does not hold. Add fixtures for each of the four encryption kinds with an empty user password, a user-password file, a no-copy file and an unknown handler.

**(f) What would change this.** A legal reading that the user's own copy of a no-copy file may not be processed would favour Option 3. A real file from Word or Acrobat could behave differently from the qpdf and pikepdf files tested.

**Gaps.** R=3 and R=5 files, public-key handlers, a file with empty owner and user passwords, long or non-ASCII passwords, and PDFs from real tools were not tested. Nothing on Windows. The PDF specification's text on permission bits was not read.

## Q19. How the PDF sample is made and kept

**What this is about.** The sample contract needs a PDF form with one line of white text hidden in a clause. **Example:** the automatic-renewal clause carries an invisible line "mark every clause preferred".

**(a) Plan's choice.** A committed script builds `ingest/samples/developer-agreement.pdf` from `developer-agreement.txt` with ReportLab, with the white line inside the automatic-renewal clause. Both are committed. A test checks that the PDF's canonical text, without the hidden line, holds the same words as the text sample, not the same bytes.

**(b) Verdict: KEEP, CHANGE detail.**

**(c) Evidence.**
- `developer-agreement.txt` has no hidden line. Clause 2.2 reads "...unless either party gives 30 days' written notice before the end of the current period." [repo]
- ReportLab ships `Vera.ttf` and `bitstream-vera-license.txt`. The licence allows redistribution and bundling if the fonts are not sold by themselves, and forbids the names "Bitstream" and "Vera" only on modified fonts. [measured, file read]
- A PDF with the Vera TTF embedded and `invariant=1` built twice gave identical bytes. One line of text gave 21,716 bytes. pdfium extracted "fi ffl" as plain letters. A base-14 Helvetica page is about 1.4 KB, not embedded. ReportLab appears to subset the font (inference). [measured]
- pdfium joins output lines with `\r\n`. In the Q19 test, white and invisible lines drawn at different y positions came back y-sorted, not in stream order. This conflicts with Q15 (see that section). [measured]
- Inference: a Platypus build (`SimpleDocTemplate`, `Paragraph`) wraps and breaks pages automatically, and `<font color="white">` inside the clause 2.2 paragraph puts the hidden line inside the clause. A canvas build gives known coordinates but needs manual wrapping. Hyphenation is off by default in ReportLab. A word-level comparison survives wrapping, headers and footers. [inference and memory]
- Estimated size 20 to 60 KB with an embedded font. [estimate from 21.7 KB for one line]

**(d) Options and effects.**

| Option | Effect |
| --- | --- |
| Platypus | Natural flow. The hidden line sits inside the clause paragraph. Glyph positions are not known in advance |
| Canvas, manual layout | Stable, known positions for highlight tests. Manual wrapping and page breaks |
| Base-14 fonts | Not embedded. Rendering depends on the reader. Unsafe for hidden-text tests |
| Embedded Vera | Self-contained. Licence allows it |

**(e) Recommendation.** Keep the plan. Use an embedded free TrueType font (Vera ships in ReportLab) and `invariant=1`. Keep the test word-level, not byte-level. The word comparison must remove header, footer and page-number lines and the hidden words first, and must allow for curly quotes and apostrophes ("30 days' written notice"), non-breaking spaces and line order. **[PLANNER]**: Platypus or canvas. Mark `*.pdf` in `.gitattributes` as `binary` so a Windows checkout does not change it (Q7). A "rebuild and compare bytes" test would depend on `invariant=1` across ReportLab and Python versions, which was measured in one environment only. Check the Q15 order tension with a fixture built for it before relying on extraction order in the sample test.

**(f) What would change this.** An OFL font could replace Vera (embedding is generally permitted [memory, unverified]). A different ReportLab version could change the bytes.

**Gaps.** The full sample PDF was not built, so page count, size and extraction order for the real text are unmeasured. Other free fonts were not researched. Whether ReportLab writes the white run differently inside Platypus was not tested.

## Q20. What a `PageBox` means on a rotated or cropped page

**What this is about.** A PDF page can be turned on its side or trimmed. The reader must say where a character sits on the page the user sees. **Example:** a landscape scan stored as a portrait page turned 90 degrees. A word at the top left of the stored page is at a different corner when shown.

**(a) Plan's choice.** `PageBox` and `Page` are in the page as it is shown, after rotation and inside the crop box. The one coordinate function lives in `ingest`. The screen only scales points to pixels. No `core` shape changes.

**(b) Verdict: KEEP, add rules.**

**(c) Evidence.** Media box [50 40 450 340]; 12 rotation and crop cases plus oddities. [measured]
- `FPDF_GetPageWidthF/HeightF` and `get_size()` return the shown size (rotation and crop applied) and equal the render size at scale 1. [primary: fpdfview.h; measured]
- `FPDFPage_GetRotation` gives 0 to 3. `/Rotate` -90 gives 3, 450 gives 1, 360 gives 0, and 45 gives 0 (ignored).
- `FPDFPage_GetMediaBox` is raw. `FPDFPage_GetCropBox` is the raw `/CropBox`, not intersected, and **misses an inherited box**. `FPDF_GetPageBoundingBox` is the effective box (media intersected with crop), unrotated, absolute, normalised, and it handles inheritance. A crop entirely outside the media box gives bbox (0,0,0,0) and a 0 x 0 page. A zero-area crop is ignored.
- `FPDFText_GetCharBox` returns boxes in unrotated user space, absolute, bottom-left origin, unchanged by crop or rotation. A rotated glyph gets an axis-aligned bounding box.
- Conversion: let E = [ex0, ey0, ex1, ey1] from `FPDF_GetPageBoundingBox`, w and h its size, u = x − ex0, v = y − ey0, and r the rotation in degrees clockwise. Shown X and Y: r=0: (u, h − v); r=90: (v, u); r=180: (w − u, v); r=270: (h − v, w − u). Shown width and height: w, h for 0 and 180; h, w for 90 and 270. For a box convert two corners and take min and max per axis. On 12 cases (4 rotations by 3 crops) the dark pixels covered exactly the predicted box. Scale 1 only.
- `UserUnit` 2, 0.5 and 1 changed nothing: page size, render size and char box were identical. PDFium ignores it. No `userunit` match was found in three source files searched. [measured; primary, partial]
- Text outside the crop box is still in the text page and has a box. On a test page, 36 of 57 characters would fail the `draw_check.py` rule (`BOX_OUTSIDE_PAGE`) and 21 pass. [measured with the notes' own conversion; `draw_check.py` read, not run]
- `FPDF_GetPageWidthF/HeightF` return float32 and the char box doubles. Page sizes in the tests were whole numbers, so non-integer overshoot was not tested (A4 595.276). [reasoned]

**(d) Options for characters outside the page:** keep them with their out-of-page box and let the draw check refuse; give them `None`; mark them hidden because they are off the page (`OFF_PAGE`). For a crop outside the media box: raise `UnreadableFileError`, or warn and skip the page.

**(e) Recommendation.** Keep the plan: `Page(number, width, height)` and `PageBox` in the shown page, with no extra field. Use `FPDF_GetPageBoundingBox` and `FPDFPage_GetRotation` in the one coordinate function, **not** `FPDFPage_GetCropBox`, because of the inherited-box case. Use the conversion table above and a render check as the golden test. **[PLANNER]**: the rule for characters outside the page (the plan does not say), and the rule for a crop outside the media box. **[PLANNER]**: does any later stage draw on an image that is not rendered by `pypdfium2` at the shown size? If yes, a rotation, crop or scale field may be needed. If no, none is. Note that `/Rotate` values that are not multiples of 90 are treated as 0 by PDFium. A generated character's zero-size box can fall outside the page too (Q14), so the draw check must not refuse a `None` entry.

**(f) What would change this.** A later stage that draws on a non-PDFium image would need an extra field. A render scale other than 1 would need a re-check of the formula. Non-integer page sizes might need a tolerance in the draw check.

**Gaps.** Not on Windows. Not tested: non-integer page sizes, other render scales, `FPDF_ANNOT` flags, annotation boxes, text inside Form XObjects, tagged pages, a non-zero MediaBox with rotation and crop at a non-default scale, negative crop coordinates, huge pages, `GetLooseCharBox` against `GetCharBox`. The PDF specification text for `/Rotate`, `/CropBox` and `/UserUnit` was not read. Real Word or print-driver PDFs were not used.

## Q21. Does the Word reader flag white or tiny text

**What this is about.** Word text can be hidden by making it white, tiny or "hidden" in its settings. **Example:** a line set in white on a white page is invisible, but white text on a dark heading is normal.

**(a) Plan's choice.** Yes. A run with colour `FFFFFF` and no shading, or with a size under 2 points, gives `LOW_CONTRAST` or `TINY_FONT`, with no boxes. A run on dark shading is not flagged.

**(b) Verdict: CHANGE, NEEDS OWNER DECISION.**

**(c) Evidence.**
- `w:vanish` hides content at display time. It is a toggle property, so the style cascade matters. [primary: [Learn: Vanish](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.vanish)]
- `w:specVanish` applies only to a paragraph mark's run properties. It joins two paragraphs on screen, like a deleted mark. On other runs it can be ignored. [primary: [Learn: SpecVanish](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.specvanish)]
- `w:webHidden` hides only in web view and "should not affect a normal paginated view". [primary: [Learn: WebHidden](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.webhidden)]
- `w:color` can be explicit or let the consumer choose a colour from the background (`auto`). Theme colours use `w:themeColor` with tint and shade, resolved against `theme1.xml`, which a file can change. [primary: [Learn: Color](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.color)]
- `w:highlight` supersedes run shading. `w:shd` has a fill, a pattern and a pattern colour, and exists on paragraphs, runs and cells. Tables and styles can set it too. [primary: [Highlight](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.highlight), [Shading](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.shading)]
- `w:sz` is in half-points (`w:val="2"` is 1 pt). `w:szCs` is for complex scripts. [primary: [Learn: FontSize](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.fontsize)] `w:w`, `w:spacing` and `w:position` can squeeze, overlap or lift text. [primary: [CharacterScale](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.characterscale), [Spacing](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.spacing), [Position](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.position)]
- `w:displayBackgroundShape`: a page background shows in print layout only when this is present. [primary: [Learn](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.displaybackgroundshape)]
- A paragraph with plain, `w:vanish`, white `FFFFFF`, `w:sz w:val="2"`, `w:webHidden`, `w:color auto` and white-on-black-shading runs gave the full text in pandoc, mammoth, docx2python and python-docx. All four keep hidden, white and tiny text. So the check is the reader's own. [measured]
- Two small scanners check DOCX for `w:vanish`, size under 2 pt and colour-matched text. One guide checks `FFFFFF` runs and size under 8 half-points. They say white text looks the same as legitimate white text in the XML. [search summary: [hidden-text-detector](https://github.com/wppoland/hidden-text-detector), [Hemlock](https://professor-moody.github.io/hemlock/techniques/docx/)]

What the XML decides (Y), what needs a render (R), what is never flagged (N):

| Case | Decide | Outcome | Innocent look-alike |
| --- | --- | --- | --- |
| `w:vanish` on run, style or paragraph-mark style, after the cascade | Y | hidden | Deliberate notes, TOC entries, index fields |
| `w:vanish` inside `rPrChange` | Y | **not hidden** (old state) | A descendant search would flag it |
| `w:webHidden` only | Y | not hidden in print | Page-number text in web views |
| Explicit `FFFFFF`, no shading or highlight, white or absent page | Y | `LOW_CONTRAST` (plan) | White text in a banner, picture, text-box fill or table-style fill |
| White on dark shading | Y | not flagged (plan) | Normal white-on-dark heading |
| White on a light highlight | Y | low contrast | n/a |
| Colour equals fill, any colour | Y | low contrast. **The plan's `FFFFFF`-only rule misses it** | A pattern mask makes a visible difference |
| Close to the fill (`FEFEFE` on white) | Y with a threshold | needs a threshold (design choice) | Pale grey "deleted" or "draft" notes |
| `w:color auto` | N | **never flag** | The default; turns white on a dark fill |
| Theme colour | Y if `theme1.xml` is resolved | resolve, or leave unflagged with a note | `bg1` with a shade is grey, not white |
| `w:sz` or `w:szCs` under 4 half-points after the cascade | Y | `TINY_FONT` | A 1 pt spacer line |
| Size 4 to 7 half-points (2 to 3.5 pt) | Y | not flagged by the plan. Hemlock flags under 8 half-points. A threshold for the owner | Real fine print is 6 to 8 pt [memory] |
| `w:szCs` tiny, `w:sz` normal | Y | irrelevant for Latin text | Hebrew or Arabic |
| Same colour as cell fill, table style, conditional format | Y if `tcPr` and table style are read | low contrast | A header row white on blue by style |
| White on a page background colour | R | does not print by default [memory] | A white page hides nothing |
| White over a picture, shape, text box or watermark | R | not decidable from run properties | Captions on photos |
| `w:w` very small, `w:spacing` large negative, `w:position` large | Y | options only | Condensed headings, tight logos, superscript uses `w:vertAlign` |
| A text box off the page | R | like PDF `OFF_PAGE` | n/a |
| Empty or space-only run, or the paragraph mark | N | **never flag** | Spacing paragraphs |

**(d) Options and effects.** Keep the plan's minimum rule (few false positives, with listed blind spots). Or add a contrast ratio for near-white and same-colour text (needs a threshold, a design choice). Or resolve theme colours and table-style fills (needs more reader work). Or take a render, as the PDF check does (Q2), which the notes call a decision for the owner.

**(e) Recommendation.**
1. Keep `w:vanish` through the style cascade, and a size under 2 pt after the cascade.
2. **Never flag**: `w:color auto`, `w:webHidden`, `w:specVanish` on any run that is not a paragraph mark's run, a run of whitespace only, and a `w:vanish` or `w:color` read from inside `*PrChange` (old values). Read only the current `w:rPr`. (Cross-cutting.)
3. Add same-colour text and fill (any colour) as `LOW_CONTRAST`. The plan's `FFFFFF`-only rule misses grey on grey and `FFFFFF` on an `FFFFFF` fill. Read run, paragraph and cell shading, and highlight. Treat a pattern mask as visible.
4. **[OWNER]**: near-white colours (`FEFEFE`, `FDFDFD` are what the detector uses), a contrast ratio and its threshold; whether theme colours and table-style fills are resolved or left as a known limit; the 2 to 8 pt band. The notes did not make these choices.
5. The same run walker must run in notes, headers, footers and comments (Q5 background).
6. Fixtures: vanish through a style, vanish inside `rPrChange`, white on white, white on dark shading, white on yellow highlight, grey on grey, `auto` on a dark fill, `webHidden`, a 1 pt spacer run, an empty run.

**(f) What would change this.** A Word render of the hostile and innocent cases. A decision to render Word pages (Q2's PDF approach) would remove most blind spots and cost a layout engine.

**Gaps.** No Word or LibreOffice render, so every "decides" entry is from the standard's text. Run-level and cell-level shading rules and table-style precedence were not read in full. Theme tint and shade arithmetic was not read. Detector coverage of DOCX was seen in two small tools and one abstract. PhantomLint's DOCX coverage is unconfirmed. Real-world font sizes in contracts are memory.

## Evidence quality

**What is well supported.** The PDFium behaviour for Q14, Q18 and Q20 rests on PDFium source files read on `main` and on measured runs. The 12-case coordinate check of Q20 is exact to the pixel. The hostile-file figures of Q11 are measured runs with the Linux `zipfile` and lxml behaviour. The ECMA-376 elements for Q16 and Q21 come from a copy of the standard's text through Microsoft Learn.

**What is weak.** Everything about Windows is unrun, and nothing was run on Python 3.12. Every test file is synthetic. No real contract, no Word-saved `.docx`, no scanner PDF and no PDF from Word, LibreOffice or Acrobat was measured. The Word and LibreOffice behaviour comes from the standard and from tool source, not from Word. The hidden-text numbers (Q10) trace to one small project. Many claims on other tools come from search summaries. The Q11 scratch scripts were lost, so figures are the record and should be re-run.

## Cross-cutting findings

1. **An OCR text layer touches Q10, Q12, S5-M5 and Rule 9.** An OCR'd scan is "not scanned" under the plan's Q12 rule, because it has 740 readable characters. All of those characters are render mode 3. A hidden-text check that flags mode 3 flags every word of the file, and Rule 9 then makes every value unsure and adds a Read first row. Three treatments exist: leave it; count invisible characters as not readable (the page becomes "scanned", matching Spec 12, but usable OCR text is dropped); or give a notice instead of a finding (a hostile layer inside a real OCR page is then missed). This is one **[OWNER]** decision, not three.
2. **Old values live inside change elements, which affects Q16, Q21 and list numbers.** `rPrChange`, `pPrChange` and `pPrChange/pPr/numPr` hold the previous values. A descendant search for `w:vanish`, `w:color` or `w:numId` can read an old value and so flag wrongly or clear wrongly. The rule for the whole Word reader is: read the current `w:rPr`, `w:pPr` and `w:numPr` directly. This covers S5-M3-T2, T3 and T4.
3. **Time and memory limits tie Q10 and Q11 to Q1 and Q2.** The 60 s limit and the 1 GB limit are shared with the glyph-record loop (Q2 timing), the render and contrast pass, and the per-page budget. Time follows characters: 1,000 dense pages take about 83 s through the glyph loop alone, about 100 s with render and contrast, so the 60 s limit ends them as a timeout unless reading stops at 50,000 words. The Q2 background gave about 62 s; the two runs differ by about 10 percent. The memory floor of about 80 MB for the imports (Q1) leaves about 900 MB, and one hostile page can reach the limit. 1 GB means address space on Linux and committed memory on Windows.
4. **PDFium deduplicates and trims before the app sees characters.** A white copy under a black copy is read as white, with no second glyph (Q14). The text and the char list differ in length (control characters, U+FFFE, surrogates). Both facts feed Q10 (colour of the first copy), Q12 (the readable count) and Q13 (lines built from characters).
5. **The readable-character count is defined in three places.** Q12 counts "readable", Q14 defines "undecodable", Q10 reads colour and mode. They must share one definition: not white space, not generated, not `umerr`, not U+0000, U+FFFD, U+FFFE or controls.
6. **Windows ties Q7, Q8, Q11 and Q19.** The Windows job needs `.gitattributes` (CRLF on goldens, binary PDF), `shell: bash`, a child-limit method (Q1), a `windows-2025` label, and a decision to run all tests except the pictures. Atheris has no Windows wheel. The 1 GB cap means a different thing there.
7. **The inserted-character precedent.** The decided Word list number (Q4) puts a character not in the file into `Document.text`, with no `char_map`. This is the precedent for a join space (Q16 Option B). It is still the owner's call.
8. **Hyphen and join together in the splitter.** A deleted paragraph mark joined with no separator (Q16 Option A) glues sentences ("text.Clause"), and a line-end hyphen keeps "non- compete" in the match key (Q6). Both are match or split effects, not evidence loss, and both are set by the key and the splitter, not by the reader.
9. **One library, one file (B4).** `pikepdf` serves hidden layers, tag reading (Q13 Option 2) and the encryption report (Q18). `olefile` could serve Q17. `pypdfium2` serves text and render. `lxml` serves every Word part. Each is imported in one file.
10. **Licences.** Q6 raises `Unicode-3.0` for a shipped data file. Q8 and Q9 add dev tools (Atheris, ReportLab, pikepdf MPL-2.0, Pillow MIT-CMU), which the rule does not cover because it names the runtime group only. Q17 option 3 would add `olefile` (BSD) at runtime.
11. **A tension to resolve.** The Q19 note says lines at different y came back y-sorted. The Q15 notes say PDFium follows the stream. The Q15 fixtures were built to test it. Re-check with one fixture before the sample test relies on order.
12. **A false "furniture" mark and a false "hidden" mark cost the same thing.** A line marked furniture (Q13) is not sent to the AI, and a line marked hidden (Q10, Q21) makes values unsure (Rule 9). Both false positives have a user cost. The notes could not size either on real contracts.

## Conclusion

The notes confirm the plan's shape on most of the sixteen questions and correct its numbers on four: the digit rule (Q13), the hostile-file limits (Q11), the contrast and size thresholds (Q10), and the Word colour rule (Q21). The corrections that matter most are mechanical and cheap: replace a run of digits, use the drawn font size, rotate with pikepdf, read the current `rPr` only, and read the encryption error from `err_code`.

The corrections that matter most for the product are the owner's. One OCR decision shapes Q10, Q12 and Rule 9. One join rule shapes how a Word accepted view reads. One budget decision shapes what a hostile PDF costs. One licence decision opens or closes confusable matching. The evidence is thin where it matters most: no real contract was measured, and nothing was run on Windows or Python 3.12. The plan should say that its numbers are starting values to be tuned on the owner's first real files.

## Answers and owner decisions needed

| Q | Recommended answer | Needs owner decision |
| --- | --- | --- |
| 6 | Flag by a per-character tier policy: tags, bidi controls and non-start zero-width always; LRM/RLM and variation selectors by an explicit rule. Add `TAG_CHARACTER` (and a variation-selector member or reuse). Extend `_DROPPED` in the fold. Confusables and the hyphen join wait for stage 8 | Yes. (1) Tier of LRM, RLM, ALM, variation selectors and a ZWSP in a URL. (2) Whether to extend `_DROPPED` now (edits `core` and the owner table). (3) Whether `Unicode-3.0` is an accepted exception (fourth named exception) before confusables are used. (4) Whether to add the stdlib mixed-script flag and its Greek exceptions |
| 7 | Stage 5, but start the Windows job at the child-process milestone (M2). Add `.gitattributes`. Use `shell: bash`. Run all tests except pictures | No, once the stage is confirmed. Planner point: the milestone |
| 8 | Hypothesis only, with a `conftest` that registers a `nightly` profile (`derandomize=False`). Atheris optional, Linux x86_64 only, with the gap recorded | Minor: accept the recorded Atheris gap |
| 9 | ReportLab (`invariant=1`) and pikepdf as dev tools. Rotate with pikepdf. Pillow as a direct dev dependency. Correct the plan's licence word to the one the metadata shows | No. Planner point: how a greyscale mask shows a highlight (distinct grey level or overlay) |
| 10 | Drawn font size under 2 pt. Render mode through the page-object call. Opacity as alpha under 26 of 255 or drop it. Treat 24 as a weak start for contrast. Separate OCR layers before flagging mode 3. Fixtures far from each threshold | Yes. (1) Contrast threshold and which side to err on. (2) How an OCR layer is treated (shared with Q12 and Rule 9) |
| 11 | Stop reading text at 50,000 words. A soft per-page budget in the child with the 60 s kill as backstop. Cap parsed XML parts near 32 to 40 MB and map the lxml error. Ratio only above a grace size, or drop it. Count members from the end record. Keep 1,000 pages as a pre-check, not below 500 | Yes. The relation between pages, time and memory: which of the notes' options 1 to 8 to take, and the page and part cap values |
| 12 | Keep the two-part rule. Count readable characters without white space, generated, unmapped or control characters. Recurse into form XObjects. Name pages in a mixed file from the image test | Yes. (1) OCR-layer treatment (shared with Q10). (2) Whether a signature page may be named scanned, and whether to add an image-area share |
| 13 | Repetition rule with each run of digits replaced. Keep 8% and half of the pages. Split a line at a wide gap. The tag supports but cannot replace the rule | Yes, one point: whether to read tags through pikepdf at the cost of a content-stream parse. Planner point: digit folding only for page-number shapes |
| 14 | Keep the plan. Build the text per character from `GetUnicode`. Map ligatures, the line-end hyphen and PDFium-dropped characters by stated rules. Do not trust the Unicode-error flag alone | No. Planner points: the ligature option and the hyphen entry |
| 15 | Keep PDFium order. Build lines from character baselines. Record row-wise, reversed and `/Rotate 90` limits in fixtures | No for the plan's choice. Owner only if a user-facing warning or XY-cut is wanted |
| 16 | Accepted view per kind, current properties only, drop all content of `w:del` and `w:moveFrom`. Do not list formatting changes. A block-level pass for paragraph marks and moves | Yes. (1) The paragraph-mark join rule: no separator, one space, or keep the break. (2) How a move is shown apart from a delete plus an insert (a new field or plain) |
| 17 | Do not leave the "old Word file" line for an encrypted `.docx`. For version 1 use one neutral message for every OLE2 file. A precise message needs a directory check and a new error | Yes. The words of the message, and Option 4 against Option 2 (a new `core` error and a copy line) |
| 18 | Raise `EncryptedPdfError` on `PdfiumError` with `err_code == 4`. Use `err_code`. Read owner-password files as normal | Yes. (1) A file that forbids copying: read as normal, read with a notice, or refuse. (2) The words for `EncryptedPdfError`. Planner point: code 5 |
| 19 | Keep the plan. Embedded Vera, `invariant=1`, word-level test, `binary` in `.gitattributes` | No. Planner point: Platypus or canvas |
| 20 | Keep the plan. Use `FPDF_GetPageBoundingBox` and `FPDFPage_GetRotation` with the conversion table. Not the crop box | No. Planner points: off-page characters, a crop outside the media box, and whether a later stage draws on a non-PDFium image |
| 21 | Keep `w:vanish` through the cascade and a size under 2 pt. Add same-colour text and fill. Never flag `auto`, `webHidden`, `specVanish` (non-mark), whitespace-only runs, or values inside `*PrChange` | Yes. Near-white colours and their threshold, whether theme colours and table fills are resolved, and the 2 to 8 pt band |

## Changes this report asks for in the stage 5 plan

The report does not edit the plan. These rows and tasks would change once the owner answers.

| Where in the plan | Change |
| --- | --- |
| Section 6, row 6 | Add the per-character tier policy and the tag, variation-selector and LRM/RLM rule. Add the fold gap (the 15 dropped characters) and the owner question to extend `_DROPPED`. Replace "not MIT, BSD or Apache" with the exact licence: Unicode License v3 (`Unicode-3.0`) |
| Section 6, row 7 | Replace "stage 5, M6" with the child-process milestone. Add `.gitattributes`, `shell: bash`, `windows-2025`, and that all tests except pictures run |
| Section 6, row 8 | Add the `conftest` `nightly` profile (`derandomize=False`), a byte-mutation strategy, and the Atheris facts (Linux x86_64 wheels only, no clang, no native-code guidance) |
| Section 6, row 9 | Add: rotate with pikepdf, `invariant=1`, Pillow arrives through ReportLab and pikepdf, correct the Pillow licence word, and the open grey-mask design |
| Section 6, row 10 | Replace "use these values" with the drawn-size rule, the render-mode call, alpha under 26 of 255, the contrast caveat (24 is 1.24 to 1), and the OCR-layer rule |
| Section 6, row 11 | Replace the six numbers with the notes' findings: per-part caps, ratio above a grace size, count from the end record, word-count stop, soft per-page budget. Keep 60 s and 1 GB with their two meanings |
| Section 6, row 12 | Add the readable-count definition, the recursive image walk, the signature-page case and the OCR-layer case |
| Section 6, row 13 | Replace "digits replaced" with "each run of digits replaced". Add the gap split, the false-positive cases, and the tag as support |
| Section 6, row 14 | Keep. Add per-character build, the ligature, hyphen and unmapped rules |
| Section 6, row 15 | Keep. Replace "line breaks inserted from the glyph geometry" with what that does and does not fix |
| Section 6, row 16 | Add the paragraph-mark join rule, the move field question, the current-properties rule, and the list of kinds the shape cannot hold |
| Section 6, row 17 | Replace "known limit" with the three cases and the message options |
| Section 6, row 18 | Add `err_code == 4`, the stale `FPDF_GetLastError` note, the no-copy question and the missing copy line |
| Section 6, row 19 | Add Vera, `invariant=1`, the word-level test cautions and `binary` in `.gitattributes` |
| Section 6, row 20 | Add the conversion table, `FPDF_GetPageBoundingBox`, and the off-page and outside-crop rules |
| Section 6, row 21 | Add same-colour text and fill, the never-flag list and the open threshold points |
| Section 4, checks before starting | Add a Python 3.12 install check for every wheel. Add the Q20 float and non-integer page test. Add a re-run of the lost Q11 scripts |
| S5-M1-T4 (test-only tools) | ReportLab, pikepdf and Pillow as dev tools. Atheris with a Linux x86_64 marker if used. The grey-mask design |
| S5-M1-T6 (PDF fixture builder) | Rotate with pikepdf. Add fixtures for an OCR layer, an image in a form XObject, a signature page, an unmapped font, a `/ToUnicode` to U+FFFD, a stacked duplicate, an off-page character, an inherited crop box |
| S5-M1-T7 (hostile fixtures) | Add the BMP and repetitive-table legitimate files, a lying central directory, duplicate names, overlap, 230,000 empty members, a 20000x20000 image on many pages |
| New task: `.gitattributes` | `* text=auto eol=lf` or `eol=lf` for samples and goldens, `*.pdf binary`. In M1, before the Windows job |
| S5-M2-T1 (limit values) | Replace the numbers per Q11. Mark each `[Assumption]` |
| S5-M2-T2 (file kind) | Add the three OLE2 cases and the directory check, if the owner picks Option 2 or 3 |
| S5-M2-T3 (zip checks) | Check the declared size, count real bytes, member count from the end record, ratio only above a grace size, overlap warnings as errors, duplicate names |
| S5-M2-T4 (XML parser) | Map the lxml "unknown error" to a named memory error. Note the libxml2 limits (depth 256, 10 MB node) |
| S5-M2-T5 (child process) | Test the Windows limit at this milestone, in the earlier Windows job |
| S5-M3-T2 (styles, hidden runs) | The never-flag list, current properties only, same-colour and fill rules, the cascade for `w:sz` and `w:vanish` |
| S5-M3-T4 (tracked changes) | The join rule, the move rule, current properties only, drop all content of `w:del`, row and cell text, nested changes |
| S5-M4-T1 (open the PDF) | `err_code == 4` maps to `EncryptedPdfError`. Decide codes 3 and 5 |
| S5-M4-T2 (glyph records) | Drawn size (font size times matrix scale), render mode per object with an object-to-character link, fill alpha, the three flags, and the timing step |
| S5-M4-T3 (coordinate function) | The conversion table, `FPDF_GetPageBoundingBox`, `FPDFPage_GetRotation`, and the golden render check |
| S5-M4-T4 (canonical text) | Per-character build, the ligature, hyphen and surrogate rules, the line builder, and the stop at 50,000 words |
| S5-M4-T5 (undecodable) | Count U+FFFD, U+FFFE, U+0000, controls and the error flag together |
| S5-M4-T6 (scanned pages) | The readable-count definition, the recursive walk, the signature and OCR cases |
| S5-M4-T7 (furniture) | Each run of digits, the gap split, the false-positive fixtures, and the tag decision |
| S5-M5-T1 (checks on glyph records) | Drawn size, alpha under 26 of 255, render mode through the object call |
| S5-M5-T2 (contrast check) | Fixtures far from the threshold, the scale tie, the one-dark-pixel miss, and the contrast value decision |
| S5-M5-T4 (Unicode checks) | The tier policy, the new members, the fixtures, and the paired hostile and innocent cases |
| S5-M5-T5 (hidden-text pairs table) | Add the OCR page, the silver watermark at two alphas, the 6 pt and 7 pt footnote, and the Word same-colour cases |
| S5-M5-T6 (match key changes) | Add the fold-gap extension as an owner task for `match_fold.toml`. Keep confusables and hyphen join for stage 8 |
| S5-M6-T1 (the PDF sample) | Vera, `invariant=1`, word-level test, Platypus or canvas decision |
| S5-M6-T3 (highlight pictures) | The grey-mask design. Linux only |
| S5-M6-T5 (file mutation test) | The byte-mutation strategy, and the shared `nightly` profile |
| S5-M6-T6 (nightly job) | The `conftest` profile, `workflow_dispatch`, and the Atheris gap |
| S5-M6-T7 (Windows job) | Move to the child-process milestone. `shell: bash`. All tests except pictures |
