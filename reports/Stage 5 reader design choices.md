# Stage 5 reader design choices: what to change in the stage 5 plan

**Written 23 Nov 2026.** This report tests questions 1 to 5 of section 6 of `docs/plans/stage-05-ingest-word-pdf.md` against five sets of research notes (one for each question). The plan is a Draft and its owner answers are empty, so this report recommends and decides nothing.

**Scope.** Questions 6 to 21 of the plan are not covered. Where a note touches them (for example a new `HiddenReason` member), the report says so and leaves the question open. This report edits no plan, no table and no expected value (Constitution T11). It is not legal advice.

**Where the numbers live.** The folder `research_notes/` is git-ignored. The measurements below exist only in the notes and in this report. No contract text, party name or person name appears here. The test text in the notes is made up.

**Source grades.** The notes grade every claim. This report keeps the grades, in square brackets, as the notes use them:

| Grade | Meaning |
| --- | --- |
| primary | The researcher read the standard, the manual or the source code. |
| measured | The researcher ran it on one machine (Debian 13, Python 3.12 and 3.13, pypdfium2 5.15.2). Q1 and Q2 only. |
| local | The researcher ran the repo's own `read_pasted_text` and `split_clauses` on made-up text. Q5 only. |
| summary | A fetch tool summarised the page or the code. The quote is the tool's, not checked against the file. |
| search | Seen only in a web-search summary. |
| memory | The researcher's background knowledge, not re-checked. |
| uncited | The researcher's own knowledge, with no source fetched. Q1 and Q2 use this word. |
| inference | A conclusion drawn from the other grades. |

A claim with no grade in this report is a repo fact that the notes read in the repo (file path given) or a statement of the plan.

**Task IDs.** A task such as S5-M2-T5 is task 5 of milestone 2 of the stage 5 plan. The plan's question numbers (1 to 21) are the numbers of its section 6. For questions 1 to 5 the report number and the plan number are the same.

## Executive summary

The plan's direction holds on all five questions. Research changes the detail, and on three questions it contradicts a sentence of the plan. The most serious finding is on question 5: the plan's placement of footnotes and headers breaks the clause splitter, and comment text has no home in any current shape.

**Verdicts at a glance.**

| # | Question | Verdict | One-line reason |
| --- | --- | --- | --- |
| 1 | Who starts the child process | KEEP the owner (`cli`), CHANGE the mechanism | `subprocess` with `python -I -m` (or the app's own executable when frozen), not a process pool. The child sets its own limits. The reply is JSON checked by a `TypeAdapter`, never pickle. The Windows cap counts committed memory, not address space |
| 2 | Who renders for the contrast check | KEEP + 4 additions | `ingest` renders in the child. Time the glyph-record loop first: it costs about 10 times the render. Cap the pixels per page. The check takes bytes, width, height and stride |
| 3 | Do `links` and `privacy` skip hidden text | KEEP for `privacy`; KEEP for `links` in stage 5 with an open owner point | A blanket skip would also skip visible words under a Word `COMMENT` span. For `links`, Rule 9 covers values only, so an edge that rests on hidden text is unmarked |
| 4 | Where a rebuilt list number goes | KEEP option (a), CHANGE two rules | The number goes into `Document.text`. The plan's separator rule conflicts with the splitter's tab rule. The resolution rules in the plan are too short |
| 5 | Where notes, headers, footers and comments go | CHANGE | The tests of the real splitter contradict the plan: header lines become false clauses, footer and footnote text join the last clause. Comment text has no home in any shape |

**Where the notes disagree with the plan, in one place.**

1. Q1. The plan says "spawned process" and does not say who sets the limits. The notes say: start the child with `subprocess`, not a pool, and let the child set its own limits as its first action.
2. Q1. The plan gives one memory figure for both systems. The notes say that 1 GB means address space on Linux and committed memory on Windows.
3. Q2. The plan's bitmap call passes "bytes, width, height". The notes add the stride.
4. Q3. The plan calls "keep every edge" enough. The notes find an open owner point for `links`: Rule 9 covers values, not evidence-trail entries.
5. Q4. The plan follows the number with the `w:suff` separator. The splitter never accepts a bare number on a line with a tab.
6. Q5. The plan puts footnotes after the body and headers before it. The local tests show that both break the splitter. The plan's "comment text is not put into `Document.text`" is sound, but then nothing carries it to the screen.

**Owner decisions this report asks for.** Five open points need an owner answer before the planner can write the tasks: whether stage 5 adds one `cli` file before stage 6 (Q1), whether Rule 9 extends to evidence-trail entries (Q3), the separator after a Word list number (Q4), and where comment text and Word furniture live (Q5, two points). The last table of the report lists them.

## Q1. Which module starts the child process for parsing hostile files

**(a) Plan's current choice (S6 row 1).** "`ingest` stays pure: bytes in, `Document` out, with no process, file or clock. `cli` owns the child process. Stage 5 builds one small `cli` function, `read_file_in_child`, that runs the `ingest` call in a spawned process with a wall-clock limit (the parent kills the child) and a memory limit (an address-space limit on Linux; a job object on Windows), and turns a timeout, a memory failure or a crash into `UnreadableFileError`."

**(b) Verdict: KEEP the owner of the process, CHANGE the mechanism.** `cli` is the right owner. The plan leaves out how the child starts, who sets its limits, how it replies, and what the Windows limit means. The notes settle each of these.

**(c) Evidence.**

*Why `cli` and not `ingest`.*
- Constitution T2 pushes side effects to thin edge modules, and B4 says a module hides one decision. `pyproject.toml` lets only `cli` wire modules together, and pipeline modules never import `cli`. Starting a process, reading a pipe, reading the clock and killing a child are side effects. [repo facts; inference for the fit]
- System design 3.3 says parsing runs "in its own short-lived child process", and ADR 0007 says the child-process parse is also the production design, so hostile-file tests exercise real code. Neither names the owner. System design 15.5 leaves it open. [repo facts]
- If `ingest` started its own child, it would hold the interpreter path, the frozen-build flag, the pipe protocol and the Windows calls. Tests of `ingest` could no longer be bytes in, `Document` out. [inference]
- The notes found no fit for a neutral shared place under the current contracts. `core` must stay free of side effects (T1), and ADR 0004 names no such place. [inference; the researcher did not read ADR 0004 in full]

*Why not a process pool.*
- `ProcessPoolExecutor` has no supported way to kill a stuck worker on Python 3.12 and 3.13. A running future cannot be cancelled, and `future.result(timeout=)` raises `TimeoutError` but the docs do not say it stops the worker. `terminate_workers()` and `kill_workers()` exist only from 3.14. [primary: [concurrent.futures docs](https://docs.python.org/3/library/concurrent.futures.html)]
- A pool returns objects by pickle, and `Connection.recv()` unpickles data and "can be a security risk unless you can trust the process which sent the message". The reader child parses the hostile file, so it is the process least fit to be trusted. [primary: [multiprocessing docs](https://docs.python.org/3/library/multiprocessing.html)]
- `multiprocessing` spawn does work. It started in 81 ms against 15 ms for `subprocess` of `python -I -c pass`. It adds a resource-tracker process and needs `freeze_support()` in a frozen build. [measured for the times; primary for the rest]
- `fork` is unsafe. The desktop shell is multi-threaded. CPython moved the POSIX default away from `fork` in 3.14 "to avoid common multithreaded process incompatibilities", and `fork` in a multi-threaded process warns since 3.12. [primary: [multiprocessing docs](https://docs.python.org/3/library/multiprocessing.html)]
- PDFium is not thread-safe by the maintainers' own words, so `pypdfium2` must be called from one thread only, inside the child. [primary: [pypdfium2 API docs](https://pypdfium2.readthedocs.io/en/stable/python_api.html)] No source says whether PDFium is fork-safe. The notes mark that unknown, not safe. [primary by absence, search]
- `python -I` ignores `PYTHON*` variables and adds neither the current directory nor the user site-packages to `sys.path`. A child started with `-I -m clause_tracer.cli...` finds the package only if it is installed. A source checkout run without installation would fail. [primary: [command line docs](https://docs.python.org/3/using/cmdline.html); inference for the consequence]

*Start-up cost.* On Python 3.13 with a warm cache on Linux: `python -I -c pass` took 15 ms. `python -I -c "import pypdfium2, lxml.etree"` took 96 ms. Windows and a frozen build will cost more (uncited). A cost of about 0.1 s for each file is small against a read that can take seconds. [measured]

*Linux memory limit.*
- `RLIMIT_AS` is the address-space limit. When it is exceeded, `brk`, `mmap` and `mremap` fail with `ENOMEM`. [primary: [getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html)]
- Set before `import pypdfium2`, loading `libpdfium.so` failed at 24 MB on 3.13 and worked at 48 MB. Importing lxml, pypdfium2, pikepdf, zipfile and json together worked at 80 MB and above. The researcher did not test below 80 MB for the whole set. [measured] So PDFium does not reserve a huge range, unlike V8, which reserves a 4 GB cage. [search for V8; one blog for Chromium: [write-up](https://gnu.eecs.kth.se/~nt/computer/notes/2023-04-18__ulimit-caused_crash_of_chrome-based_browsers.txt)]
- With the cap at 512 MB after loading, rendering a 14,400 pt page raised a catchable Python `MemoryError`. At 1 GB a 30,000 pt page also ended as `MemoryError`. Python 3.12 and 3.13 behaved the same. [measured]
- `RLIMIT_DATA` at 100 MB did not stop a 500 MB shared anonymous `mmap`, but it stopped a 500 MB `bytearray`. It is unsafe as the only guard. [measured]
- `RLIMIT_CPU` counts CPU seconds, not wall-clock time. A process that sleeps or blocks never reaches it. [primary: [getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html)]
- A signal death gave `returncode == -11` under `subprocess`. An uncaught `MemoryError` gave exit 1. [measured]
- `preexec_fn` "is NOT SAFE to use in the presence of threads". So the limit must be set in the child's own start-up code, not through `preexec_fn`. [primary: [subprocess docs](https://docs.python.org/3/library/subprocess.html); inference for the rule]

*Windows memory limit.*
- `JOB_OBJECT_LIMIT_PROCESS_MEMORY` limits "the virtual memory that can be committed by a process". It counts committed memory, not reserved address space. So the same figure of 1 GB is more permissive on Windows than on Linux. [primary: [JOBOBJECT_EXTENDED_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information); inference for the comparison]
- "Memory operations performed by the process before it was associated with the job are not examined." A job assigned from the parent therefore leaves a window in which the child runs without a limit. Python cannot start a suspended process through `subprocess` (no `CREATE_SUSPENDED` constant). [primary: [AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject); [subprocess docs](https://docs.python.org/3/library/subprocess.html)]
- If the child puts itself in a job as its first action, the window closes and each platform has one code path inside the child. [inference]
- On Windows 8 and later, a process already in a job may join another, and the tighter limit wins. A failed assignment must be a hard error, never a silent skip. [primary: [Nested Jobs](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs); inference for the rule]
- The note holds a pure-`ctypes` sketch. It was not run: no Windows host was available. The struct sizes (144 bytes for the extended structure on x64) are the researcher's expectation. [uncited]
- PDFium's reaction to a failed commit on Windows has no source. The parent must treat any nonzero exit, including codes such as `0xC0000005` and `0xC0000409`, as a crash. [inference]

*The reply.*
- The project validates outside data once, at the edge, with a Pydantic `TypeAdapter` (Constitution D4 and I9; system design 3.4). The child's reply is outside data. So the parent should validate JSON with the `TypeAdapter` for `Document`. [repo facts; inference for the use]
- The notes did not test that Pydantic round-trips the project's `Document` (frozen, slotted dataclasses, `StrEnum`, tuples). They did not measure the reply size of a 1,000-page `Document`. `char_map` may be large. [gap]
- The parent should cap the reply bytes it reads, so a compromised child cannot flood it. [inference]

*A limit is not a sandbox.* A parser exploit that gets code execution can lift a limit that the process set on itself. The plan should say so. [uncited threat model]

**(d) Options and effects.**

| Option | Kill on timeout (3.12, 3.13) | Reply | Frozen build | Effect |
| --- | --- | --- | --- | --- |
| A. `subprocess` of `python -I -m` or the app's executable with a flag (recommended) | `Popen.kill()` | Bounded JSON on stdout, checked by `TypeAdapter` | Needs the app to dispatch on a flag | Fewest moving parts. No pickle on the trust boundary. 15 ms start |
| B. `multiprocessing` spawn `Process` with a pipe | `kill()` | Pickle by default, or bytes only | Needs `freeze_support()` | Works. Extra tracker process. Pickle on the boundary unless bytes only |
| C. `ProcessPoolExecutor` | None before 3.14 | Pickle only | Same as B | Rejected: a hung worker cannot be stopped |
| D. `fork` | Yes | Pickle | Not applicable | Rejected: copies the shell's threads and locks |
| E. `ingest` starts its own child | Same as A | Same as A | Same as A | Puts a process, a clock and Windows calls into a pipeline module. Breaks T2 |
| F. cgroups v2 `MemoryMax` | Not applicable | Not applicable | Not applicable | Limits real memory, but needs systemd delegation or root. Unsuitable as the default [uncited] |

Frozen build. ADR 0009 chose a one-dir PyInstaller build, and system design 3.3 says the engine starts "from the same frozen executable". PyInstaller says `multiprocessing` is its only supported multi-processing framework, and a frozen app's `sys.executable` is the app itself. A child started with `-m` does not exist there. So the child entry must be a flag on the app's own executable. [primary: [PyInstaller pitfalls](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)] The behaviour of a one-dir build under `subprocess` re-dispatch was not tested. [gap]

Stage order. `cli` is built in stage 6. Stage 5 would add exactly one `cli` module. That is a small early use of a stage 6 module and needs the owner's word. [inference]

Split that keeps the logic pure. The notes suggest three parts: a pure outcome table in `cli` (`classify_child_outcome`, which holds the decision table and the JSON check), an edge runner in `cli` (spawn, stdin, deadline, kill, bounded read), and an `apply_limits` function with one Linux body and one Windows body. [inference] Outcomes:

| Child result | Parent maps it to |
| --- | --- |
| Return code 0 and a well-formed reply | The `Document`, or the typed error the child caught (a `code` string) |
| Return code 0 and a malformed or oversize reply | `UnreadableFileError` |
| `MemoryError` caught in the child | `UnreadableFileError` (too large for memory), through a typed reply |
| Negative code (Linux), an NTSTATUS-looking code (Windows) or any nonzero code | `UnreadableFileError` (crashed) |
| No reply by the deadline | `kill()`, `wait()`, then `UnreadableFileError` (too slow) |

Tests. Unit tests of `ingest` may not import `cli`. So the real-child tests (S5-M2-T6) live in the root `tests/` folder, the outcome table is tested with a fake runner in `cli/tests/`, and the zip checks, limits and the hardened parser are tested in process in `ingest/tests/`. `lint-imports` sees only `import` statements, so a `-m` string passes it. [inference; the last point is a gap the notes did not check]

**(e) Recommendation.**
1. Keep `cli` as the owner. Say in the plan that stage 5 adds exactly one `cli` module and no other `cli` behaviour (needs the owner's word, see below).
2. Start the child with `subprocess.Popen`: a list of arguments, no shell, `python -I -m clause_tracer.cli.<child module>` when run from an installed environment, and the app's own executable plus a flag when frozen. Pass the file bytes on stdin. Read a bounded JSON reply on stdout. Validate it with the `Document` `TypeAdapter`. Never unpickle.
3. Let the child set its own limits as its first action: `resource.setrlimit(RLIMIT_AS)` on Linux and a self-assigned job object with `JOB_OBJECT_LIMIT_PROCESS_MEMORY` and `DIE_ON_UNHANDLED_EXCEPTION` on Windows. Fail closed if the call fails. The parent keeps the wall clock and calls `kill()`.
4. State in the plan that the Linux cap counts address space (measured floor about 80 MB) and the Windows cap counts committed memory, so "1 GB" differs. State that neither is a security sandbox.
5. Put one real over-limit child test for each system in root `tests/`. Add a Windows CI test for the `ctypes` struct size and a real over-limit allocation before the stage closes.
6. Add a test that `Document` round-trips through the `TypeAdapter`, and measure the reply size of a 1,000-page file.

**(f) What would change this recommendation.**
- If the owner will not accept any `cli` code before stage 6, the alternative is a neutral place that every module may import. The notes found no fit under the current contracts, so the owner would have to amend ADR 0004 or the contracts. The contracts must stay as they are (AGENTS.md).
- If the Windows test shows that PDFium aborts instead of failing a commit, the Windows limit could never turn a memory failure into a typed reply. The report would then rest on the crash path only.
- If a measured `Document` reply for a 1,000-page file is very large, JSON on stdout is the wrong channel and a temporary file in a private directory is the fallback.
- If the one-dir frozen build cannot dispatch the child from a flag, the choice falls to option B with bytes only on the pipe.
- If a threat model later needs a real sandbox (seccomp, AppContainer), these limits do not meet it. That is outside stage 5.

**Gaps.** No Windows host: the sketch and the struct sizes are unrun. No source for PDFium's reaction to a failed commit on Windows, or for fork safety. No test with many threads, Alpine or musl, or the final `ingest` imports. The floor of 80 MB must be re-measured when the imports are final. No source for how other document tools isolate parsers (uncited).

## Q2. Does `ingest` render pages itself for the contrast check

**(a) Plan's current choice (S6 row 2).** "`ingest` renders each page itself with `pypdfium2`, which it already uses, inside the same child process, at a fixed scale in greyscale. The contrast check is one pure function over a bitmap passed in (bytes, width, height), so tests pass small made-up bitmaps. No port is added."

**(b) Verdict: KEEP, with four additions.** The choice holds. The plan lacks a pixel cap, the stride, a skip rule for generated characters, and a timing check of the glyph-record loop before the 60-second limit is fixed.

**(c) Evidence.**

*Cost.* All figures: one run on a synthetic file, an Intel i7-5500U (2015 laptop CPU, 2 cores), Python 3.13.5, pypdfium2 5.15.2. The file has 1,000 A4 pages with 60 lines of Helvetica 10 pt, about 7,970 characters per page. Image-heavy and vector-heavy pages were not tested. [measured]

| Step | Result |
| --- | --- |
| Render one A4 page, greyscale, 72 dpi | About 6 ms per page. 1,000 pages: 6.0 s. Bitmap 596 x 842, 501,832 bytes |
| Render at 96 dpi | Also 6.0 s. Bitmap 794 x 1,123, 891,662 bytes. Equal times are one run each: read as "about the same" |
| Peak resident memory of the process | 26 MB (72 dpi) and 28 MB (96 dpi), with each bitmap and page closed in the loop |
| Text extraction only (`get_textpage`, `get_text_range`) | 3.1 s for 1,000 pages |
| Six per-character values through the raw API (fill colour, unicode, size, generated flag, unicode-error flag, box) | 62.5 ms per page (about 7.8 microseconds per character), measured on 20 pages |
| That loop, extrapolated to 1,000 pages | About 62 s at this density. Over the 60 s limit alone |
| One page with a 14,400 x 14,400 pt MediaBox at scale 1 | 0.06 s, a 207 MB bitmap, peak 219 MB |

The 62 s figure is the researcher's extrapolation. A real contract page holds fewer characters than the synthetic page, and the CPU is old. So the figure shows an order of magnitude, not a result. The 96 dpi size of the large page (about 368 MB) is arithmetic. [inference]

*Raw bytes, no Pillow or numpy.* `page.render(..., grayscale=True)` gives a `PdfBitmap` with a ctypes buffer. `bytes(bm.buffer)` or `memoryview(bm.buffer)` gives plain bytes. After `import pypdfium2`, neither `numpy` nor `PIL` was in `sys.modules`. The package declares no dependencies. [measured; primary for the attributes: [pypdfium2 PdfPage.render docs](https://pypdfium2.readthedocs.io/en/stable/python_api.html), [bitmap source](https://pypdfium2.readthedocs.io/en/stable/_modules/pypdfium2/_helpers/bitmap.html), read through a summariser]
- `stride` (bytes per row) may include padding, and the buffer size is `stride * height`. For the Gray format it equalled the width in the one case tested. [primary for the attribute; measured for the case]
- Pillow's licence is `MIT-CMU` and numpy's is `BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`. The researcher did not read numpy's bundled-library notices. ReportLab 5.1.0 pulls Pillow in when installed. [measured, from package metadata]

*What the open-source detector does.* `hidden-text-detector` renders each page once at 110 dpi in greyscale and takes max minus min of the pixels in each text span's box. Below 24 of 255 it reports the text as not visible. It runs after the cheaper checks (render mode 3, font under 2 pt, opacity under 0.1, off the page). It returns "not measurable" for an empty, off-page or zero-area box. [primary: [scan.py](https://raw.githubusercontent.com/wppoland/hidden-text-detector/main/scripts/scan.py) lines 212 to 490] Its README gives MIT as the licence (summary: [repository](https://github.com/wppoland/hidden-text-detector)). It uses PyMuPDF, which is AGPL-3.0 (uncited, "please verify"). The algorithm is an idea, not copied code. The researcher did not run the detector and did not confirm the architecture report's "tested" claim.

*Which hiding cases each method catches.* One hand-written one-page PDF with 13 cases, read with pypdfium2 5.15.2, a render at 96 dpi, and a flag when the spread is under 24. [measured]

| Case | PDFium fill colour | Spread | Fill-colour check | Render check |
| --- | --- | --- | --- | --- |
| A. Normal black text | 0,0,0,255 | 147 to 255 | not applicable | no (correct) |
| B. White on white | 255,255,255,255 | 0 | yes | yes |
| C. Black text on black rectangle | 0,0,0,255 | 0 | no | yes |
| D. White text on black rectangle (visible) | 255,255,255,255 | 227 to 255 | falsely yes | no (correct) |
| E. Black text, white rectangle drawn later | 0,0,0,255 | 0 | no | yes |
| F. Black text, black rectangle drawn later | 0,0,0,255 | 0 | no | yes |
| G. White text, Multiply blend, white page | 255,255,255,255 | 0 | yes | yes |
| H. Black text at alpha 0.05 | 0,0,0,13 | 0 | only with an alpha rule | yes |
| I. Black text clipped out by an empty clip path | 0,0,0,255 | 0 | no | yes |
| J. Black text under large black text | 0,0,0,255 | 235 to 255 | no | no (missed) |
| K. White text on pale yellow band | 255,255,255,255 | 2 to 3 | falsely no | yes |
| L. Grey 0.8 text on grey 0.9 band | 204,204,204,255 | 26 (96 dpi), 21 to 26 (72 dpi) | no | borderline at 24 |
| M. Render mode 3 | band colour | 0 | no (needs a render-mode read) | yes |

The cases that only a render catches are C, E, F, I and K. Neither method catches J. Not tested: a soft mask over text, a pattern or shading fill, stroke-only text, text under an image, an annotation cover and Optional Content layers. [measured; inference for the untested cases]

*What the flags mean for the check.* `FPDFText_IsGenerated` is true for a character that PDFium inserts. `FPDFText_HasUnicodeMapError` is true for an invalid Unicode mapping. [primary: [fpdf_text.h](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_text.h)] A generated space has no ink, so its spread is noise. A Unicode-map error means the extracted letter is wrong, not that the ink is hidden, so it belongs to the undecodable counter. [inference] The box of a generated character was not tested. [gap]

*Determinism.* Two renders on the same machine and the same flags gave the same SHA-256. `no_smoothtext=True` changed the bytes. Pixel equality across Linux and Windows was not tested by anyone the researcher found. The test PDFs used unembedded Helvetica, which PDFium substitutes, and the substitute can differ between systems. [measured; uncited for the substitution]

*The alternative.* The architecture report lists a `PageRenderer` port ("cleaner") or `cli` passing images in ("simpler"). [repo: architecture report] ADR 0005 accepts no `PageRenderer` port, and system design says parsers and the report renderer are not ports. [repo facts]
- If `cli` renders, it needs `pypdfium2`, which is PDF work in the wiring layer. The images (0.5 to 0.9 MB for each A4 page) must cross the process boundary. If `cli` renders in the parent, PDFium runs on a hostile file outside the limited child, which defeats the containment. [inference]
- A port in `core` needs an ADR amendment, a fake, an adapter and wiring. It buys nothing the pure function does not give, because tests pass made-up bitmaps. [inference]

**(d) Options and effects.**

| Option | Where PDFium runs on the hostile file | New parts | Effect |
| --- | --- | --- | --- |
| A. `ingest` renders in the child (plan) | Inside the child limits | None | One library, one decision. The pure check tests with made-up bitmaps |
| B. `cli` renders in the parent and passes images | Outside the child | `pypdfium2` in `cli`, an image channel | Defeats the child. Moves 500 to 900 MB across the boundary for 1,000 pages |
| C. `PageRenderer` port in `core` | Depends on the adapter | ADR 0005 amendment, fake, adapter, wiring | Gains only a swappable renderer, which the project does not plan |

Within option A, choose one of three checks:

| Check | Catches | Misses |
| --- | --- | --- |
| Fill colour, alpha and render mode only | B, G, H, M | C, E, F, I, K |
| Render spread only | B, C, E, F, G, H, I, K, M | J |
| Both (recommended): the cheap reads first, then the spread | B, C, E, F, G, H, I, K, M | J |

**(e) Recommendation.**
1. Keep the plan: `ingest` renders in the same child with `pypdfium2`, in greyscale at a fixed scale. No port. No Pillow or numpy at run time.
2. Make the pure check take `(pixels: bytes, width: int, height: int, stride: int)` and a box in pixels. Read whole rows by slicing (`min(buf[o:o+w])`) and not by single pixels. The slicing cost was not timed.
3. Cap the pixels per page. Skip the check on a page whose bitmap would exceed the cap, and raise a warning, never silence. Close each bitmap and page right after use. The cap value is a planner choice (the notes chose none).
4. Skip generated and white-space characters and characters with an empty box.
5. Keep the fill colour, alpha and render-mode reads as the cheap first checks. Use the render as the only detector of covered, clipped-out and same-colour-panel text.
6. Put the threshold (24) and the dpi in one constant each, both `[Assumption]`. Use fixtures far from the threshold (spread 0 against 240 to 255). Case L flips between 21 and 26 with the dpi.
7. Time the glyph-record loop (S5-M4-T2) on a dense page before S5-M2-T1 fixes the 60-second limit. The loop, not the render, is the budget risk.
8. Write the known miss (text under other text, under a photo or on a busy background; soft masks and images not tested) in the threat list.

**(f) What would change this recommendation.**
- If the timed loop on real contract pages is far below the synthetic figure, the 60 s limit stands. If it is near or above, the plan raises the limit or gives each page a share of it, and the render may then run only on pages that carry text.
- If a viewer in the app window later renders pages with a different engine (PDF.js is the researcher's example), a port could earn its place. No repo doc says it will.
- If the pure check run over a dense page in pure Python proves slow, a different spread method is needed (the notes did not time it).
- If the owner holds that opening a PDF twice in one module is two decisions, not one, the planner needs a B4 note. The researcher thinks ADR 0007 supports one decision, but asks the owner to confirm. [gap]
- If a fixture needs a font that differs across systems, the pixel tests stay Linux-only, and an embedded font fixes the rest.

**Gaps.** No Windows run, no image-heavy or vector-heavy page, no lower-spec machine. Case coverage for soft masks, patterns, images and annotation covers is untested. The researcher did not read the detector's tests. A frozen build's `memoryview` slicing was not tested.

## Q3. Do `links` and `privacy` skip text that `Document.hidden` flags

**(a) Plan's current choice (S6 row 3).** "Neither skips it. `links` keeps every edge, so a reference inside hidden text is still seen. `privacy` replaces names inside hidden text too, which is the safe direction. Whether hidden text and furniture go into the text sent to the AI is decided in stage 8... Stage 5 changes no code in `links` or `privacy`."

**(b) Verdict: KEEP for `privacy`. KEEP for `links` in stage 5, with an open owner decision that the plan does not name.** The plan's position is right for stage 5. Two of its reasons are weak. "The safe direction" is true for `privacy` only. For `links`, the researcher found no source that makes either direction clearly safer.

**(c) Evidence.**

*What the repo documents say.*
- Rule 9 (Spec 5): "A value whose quote includes hidden text becomes unsure, and doesn't count as readable for Rule 4 step 1." Spec 8.4: "Values resting on it become unsure." Both cover values only. `UnreadableSpans` is built "from every `HiddenText.span` that is not `None`", and nothing in the system design table connects it to `LinkMap`. [repo: `docs/spec.md` lines 216 and 335 to 337; `docs/system-design.md` line 220]
- The stage 3 plan leaves it to stage 5 whether `links` skips hidden spans, "so a planted hidden 'Notwithstanding anything in this Agreement' cannot join every trail". The same plan says Overrides that name nothing join every trail (Spec 4.5). [repo: `docs/plans/stage-03-links.md` lines 40 and 881; `docs/spec.md` 4.5]
- An override never changes a label by itself. The note names it (Spec 4.5). Rule 10 turns a label unsure when its trail has a reference to a document that is not loaded, unless Rule 4 step 1 already made it walk-away. [repo: `docs/spec.md` lines 204 and 218]
- Which module builds the evidence trail, and how far a trail entry reaches, are not decided (system design 15.8). The stage 3 plan says "Stage 8 matches Rule 10 on spans, never on whole clauses", as a note, not a rule. [repo: `docs/system-design.md` lines 748 to 750; `docs/plans/stage-03-links.md` line 885]
- `Override.evidence` is a `Span`. `HiddenText.span` is `Span | None` (None for a hidden layer that is not in the canonical text). So a later stage can test whether an edge's evidence overlaps a hidden span, but a `None` span can never be tested. [repo: `docs/system-design.md` lines 179 and 188]
- `links` emits no override when the same sentence names an unloaded document. [repo: `docs/plans/stage-03-links.md` line 886]

*What `privacy` does today.* The stage 4 plan says `privacy` reads all of `Document.text`, so a name inside hidden text is replaced as every other copy is. The privacy fixture writer refuses any document with a non-empty `hidden`, so no privacy test touches hidden text. [repo: `docs/plans/stage-04-privacy.md` lines 19 and 110]

*The comment point.* Under the plan's own answer to question 5, a Word comment is a `HiddenText` with `COMMENT` whose span covers the commented words of the body. Those words are visible contract text. A blanket "skip `Document.hidden` spans" rule would skip visible clauses. [repo: plan row 5; `docs/system-design.md` line 220] A skip would have to filter by `HiddenReason` (skip `LOW_CONTRAST` and `TINY_FONT`, not `COMMENT`). That is more design than the plan lets the implementer make. [inference]

*How other tools treat hidden text.*
- NSA's 2005 redaction guidance warns that Word files carry hidden information and says to rebuild from clean text. The 2012 Acrobat X paper lists removal of hidden data and obscured text. Seen through news coverage and a search summary, not the originals. [search: [UPI](https://www.upi.com/NSA-issues-guidance-on-redacting-Word-PDF/28841138030530/), [Nextgov](https://www.nextgov.com/people/2006/01/nsa-issues-redacting-guidelines/234046/), [Cryptome copy](https://cryptome.org/2012/06/nsa-pdf-redaction.pdf)]
- Redaction guides say hidden layers, comments and revision history leak even when the page is blacked out. These are vendor and blog sources. [search: [Adobe](https://www.adobe.com/acrobat/resources/how-to-redact-a-pdf.html), [Redactable](https://www.redactable.com/blog/adobe-redaction-risks)]
- The EDRM Processing Standards Guide defines a "Has Hidden Data" flag, and says the Extracted Text field "holds the hidden comments of MS Office files". [primary: [EDRM](https://edrm.net/resources/frameworks-and-standards/edrm-model/edrm-stages-standards/edrm-processing-standards-guide-version-1/), read through a summariser]
- The pattern is: extract, flag, show, and sanitise at output. It matches the plan for `privacy`. For `links` the researcher found no comparable source. [inference]

*Prompt injection with hidden text.* The OWASP cheat sheet says ingestion pipelines pass extracted text and discard how it renders. It advises to render each page, flag extracted text that does not appear on it, check all hidden text and not only text that reads like an instruction, and send a flagged document to human review or give the model only visible text, marked incomplete. In one resume dataset, more than 90% of hidden prompts had no explicit instruction. [primary, through the fetch tool's quotes: [OWASP cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)] PhantomLint, the preprints on peer-review attacks and the report of 18 arXiv manuscripts were seen as search summaries only, except the abstract of one. [search: [arXiv 2508.17884](https://arxiv.org/pdf/2508.17884), [2508.20863](https://arxiv.org/abs/2508.20863), [2507.06185](https://arxiv.org/pdf/2507.06185)] One ID (2605.28999) has a date after the researcher's training data and needs a check. No source covers prompt injection that targets rule-based link extraction. So the `links` risk is plausible, not measured. [inference]

*What a hidden edge can do.* From the repo's own rules: add a hidden clause to many or all trails (a target-less override), add a "These clauses disagree" note, and create an `OutsideDocument` entry. A hidden "subject to the Master Agreement" can turn a Missing label whose missing level is walk-away into unsure through Rule 10. So a planted mention can weaken a Missing walk-away warning, which is not "the safe direction". Skipping hidden spans would remove that effect and also a real risk signal. The spec does not choose. [inference]

**(d) Options and effects.** For `privacy`:

| Option | Effect |
| --- | --- |
| Replace everywhere (plan) | No leak from a hidden name, whatever stage 8 sends. The user may be asked to confirm a name that they cannot see. The hidden name may be a suggestion on an outline that they cannot read |
| Skip hidden spans | A hidden name stays literal in the placeholder text. If stage 8 sends hidden text, the name leaves the computer. The same name is replaced in one place and not in another, which breaks the "every copy" rule. A visible name under a `COMMENT` span stays unreplaced, which is a leak |

For `links`:

| Option | Effect | Cost |
| --- | --- | --- |
| 1. Skip hidden spans in `links` | Hidden override and reference edges vanish | `links` must read `Document.hidden`. A `None` span cannot be skipped. Cutting a span out of a sentence can change how `links` reads the rest. A hidden outside-document mention no longer reaches Rule 10, so the direction is not clearly safer. A `COMMENT` span covers visible words. The user sees no trace of what the hidden line tried to link |
| 2. Keep every edge and mark an edge whose evidence overlaps a hidden span | The edge stays in the trail with the hidden outline. Stage 8 or 12 can make the trail entry or note unsure | Needs a new field or a post-pass, which is a design change, not stage 5 code. `None` spans still escape |
| 3. Keep as is (plan) | `links` unchanged and D1 intact. The edge is real but unmarked. The user's only signal is the Read first row | Fits "never guess" only in part: the code reads a hidden reference as if the user could see it |

**(e) Recommendation.**
1. `privacy`: keep "replace everywhere". The evidence supports it from five sides: the leak, consistency, the `COMMENT` span, the redaction guidance (an indirect analogy), and the decoupling from stage 8, which can then choose freely.
2. `links`: keep option 3 for stage 5, as the plan says. Add to the stage 8 notes that an edge whose `evidence` span overlaps a `HiddenText.span` needs a decision (mark it, or make the dependent trail entry and note unsure). The data for that test is already in `core`.
3. Ask the owner whether Rule 9 should extend from values to evidence-trail entries. Nothing the researcher read states it.
4. Add a privacy test with a document that has hidden text. The stage 5 PDF sample and a root `tests/` test could close the gap that the fixture writer leaves.
5. Add to the stage 8 notes that hidden-layer text (`span=None`) must never be sent. No repo statement says so. Today it is safe only because that text is outside `Document.text`.

**(f) What would change this recommendation.**
- If the owner answers that Rule 9 extends to edges, option 2 becomes the answer. It still needs a `core` shape or a post-pass, so it moves to stage 8 or 12, not stage 5.
- If a `links` test on a PDF-like fixture with a hidden target-less override shows the edge reaching every trail and changing a Rule 10 outcome, the risk is measured, not plausible, and option 2 moves earlier.
- If the owner decides that stage 8 sends only visible text, the `privacy` choice does not change (it is already safe), but the hidden-name suggestion on the screen loses its reason, and stage 12 may hide it.
- If a source shows how contract-review tools treat a hidden reference in a clause-link map, the weak analogy for `links` improves.

**Gaps.** No repo text says Rule 9 extends to trail entries. The researcher grepped the ADR folder for "hidden" and did not read every ADR in full. `map_links` was not run on a hidden override. Most paper findings are search summaries. The researcher could not read the NSA originals. Presidio's handling of hidden text was not searched. No source on EDRM or Relativity treatment of hidden reference extraction.

## Q4. Where a rebuilt Word list number goes in the canonical text

**(a) Plan's current choice (S6 row 4).** "Put the rebuilt number into `Document.text` at the start of its paragraph, followed by the level's separator (a tab, a space or nothing, from `w:suff`). ... Number formats rebuilt: decimal, lower and upper letter, lower and upper Roman, and `w:lvlText` patterns such as `%1.%2`. A bullet gives no text. Another format gives no number and an `InputWarning` with the code `word_numbering_unknown`."

**(b) Verdict: KEEP option (a). CHANGE two rules.** The number goes into `Document.text`. The separator rule conflicts with the splitter. The list of formats and resolution rules is too short.

**(c) Evidence.**

*The number is never stored.* Word computes it from a lookup chain and a running counter. Microsoft's own sample says the list text "is not directly in the markup" and must be assembled. [primary, through the Microsoft article: [Eric White, Working with Numbered Lists](https://learn.microsoft.com/en-us/previous-versions/office/developer/office-2010/ee922775(v=office.14))] The researcher could not fetch the ECMA-376 PDF. The standard's text comes from docx4java's HTML copy, from MS-OI29500 and from that article. [primary, second hand]

*What a correct rebuild needs.* Each item below is [primary, second hand] unless marked.

| Item | Rule |
| --- | --- |
| Where the level comes from | The paragraph's own `numPr` first; else the style's `numPr` (and the `basedOn` chain), with the level from the `w:lvl` whose `w:pStyle` names the style. A `numId` of 0 means no list item |
| `lvlOverride` | A `w:lvl` inside the override replaces the abstract level. `w:startOverride` sets the start value |
| Counters | Keyed by (abstractNum, level), not by `numId`. Word continues one list across several `w:num` entries of one abstractNum unless a `startOverride` restarts it. Pandoc keys continuation on the abstract id (summary) |
| Deeper levels | Reset when a shallower level advances, unless `lvlRestart` says otherwise. The default restarts "each time the previous numbering level is used". A value of 0 means never restart. Word limits `lvlRestart` to 0 to 7 and ignores it under a level override (search) |
| `isLgl` | Converts every `%n` in that level's text to decimal. A level-3 `isLgl` gives "1.1.1" even if level 1 is upper Roman |
| `lvlText` | `%n` is one-based. A `%n` that names a deeper level than the current one is ignored. A missing `val` is an empty string |
| `numFmt` | About 60 values. English contracts meet decimal, `decimalZero`, upper and lower Roman, upper and lower letter, bullet, none, and sometimes `ordinal`, `cardinalText`, `ordinalText`. A bullet uses the literal `lvlText` and ignores `%x` (MS-OI29500) |
| `numStyleLink` and `styleLink` | An abstractNum with `w:numStyleLink` has no `w:lvl` children. Follow the link to the numbering style and its real levels |
| `w:suff` | The content between the number and the text. Default tab. The page shows tab and space. The value `nothing` is from the researcher's knowledge of the schema [uncited] |
| Letters past 26 | Word gives a to z, then aa, bb, cc (doubling, not aa, ab) [search: [Telerik report](https://feedback.telerik.com/document-processing/1691914-wordsprocessing-docxformatprovider-ordered-lists-with-the-start-attribute-are-exported-incorrectly-when-converting-html-to-docx)] |

*Other tools.* None of the tools the notes checked gives a vetted multi-level text rebuild.
- python-docx has no list-number API. Issue 590 is open with the label "numbering". One attempt "did not support multi-level numbers like 1.1 or 1.1.1". [primary: [python-docx #590](https://github.com/python-openxml/python-docx/issues/590)]
- Pandoc builds list structures and does not print Word's numbers. It handles `startOverride`, `lvlOverride`, style-level `numPr` and `numStyleLink`. The summary found no mention of `isLgl` or `suff`. A maintainer reply says pandoc "usually expects" the paragraph to carry its own `numPr`. [summary: [Parse.hs](https://raw.githubusercontent.com/jgm/pandoc/main/src/Text/Pandoc/Readers/Docx/Parse.hs); search: [discussion 10096](https://github.imc.re/jgm/pandoc/discussions/10096)]
- docx2python writes its own markers (`1)`, `a)`, `i)`). Its README does not mention legal-style "1.1.1", `isLgl` or restarts. [primary for the README: [docx2python](https://github.com/ShayHill/docx2python)]
- Mammoth lists "Lists" as supported and says nothing on formats or restarts. [primary for the README: [Mammoth](https://github.com/mwilliamson/python-mammoth)]
- LibreOffice Bugzilla 137363 reports style-linked list levels above level 1 dropped. The output of `soffice --convert-to txt` on lists was not tested. [search: [bug 137363](https://www.libreoffice.org/bugzilla/show_bug.cgi?id=137363)]
- No tool was run on a multi-level file. [gap] A small experiment of one fixture and four tools would settle this in minutes.

*Typed against automatic numbers.* No survey or measured share exists. Legal-tech guides recommend style-linked lists and warn that manual numbering breaks when clauses move. These are vendor sources with a commercial interest. [search: [Clio](https://www.clio.com/resources/ms-word-for-legal-drafting/microsoft-word-limits-legal-workflows/), [LawVu](https://lawvu.com/articles/mastering-microsoft-word-for-in-house-lawyers-advanced-skills-that-save-hours/)] Do not quote a percentage. [inference] A reader must expect both kinds in one file. A paragraph with an automatic number and a typed "1.1" shows both, as Word does, and the splitter's continuity check will reject the second. [inference]

*What the splitter accepts.* The `ingest` README lists the markers at the start of a line: `5.`, `5.1` to `5.1.2.3.4`, `(a)`, `(i)`, `(A)`, `(1)`, `a)`, `i)`, `Clause 5`, `Article IV`, and a bare `3 Payment`, "never on a line with a tab". `A)` and `1)` without an opening bracket, and Roman numbers without a keyword, are not accepted. A number counts only if it follows on from the numbering so far. [repo: `src/clause_tracer/ingest/README.md`]

*What the shapes allow.* A Word document has `glyphs == ()`, `char_map == ()` and `pages == ()`. Word files are shown as typeset pages laid out by the app from `Document.text` (ADR 0001). The architecture report says the rebuilt number is "a derived label kept apart from the run text, so offsets stay honest". [repo facts]

**(d) Options and effects.**

| | (a) Number in `Document.text` (plan) | (b) Separate field that the splitter reads | (c) New shape field that marks inserted characters |
| --- | --- | --- | --- |
| Offsets | One string, number included, for clauses, sentences, hidden spans, tracked changes and privacy spans | `text` has no number. Clause spans exclude it | Offsets include the number. A mask says which characters are inserted |
| Quote check | A quote that starts at `5.1` matches. A search of the Word file for "5.1 Payment" finds nothing, because Word has no such text | A quote that starts at the number cannot match | As (a), and the mask can tell the check |
| Typeset pages | Show the number, as Word does | Layout must merge the field back: two code paths | Layout can style inserted characters: more code |
| Splitter | No change, but a separator rule is needed | New input and new reading. Changes the README contract and a `core` shape | Splitter unchanged. `core` shape changes (AGENTS.md: ask first) |
| `core` change | None | A `Document` field | A `Document` field and `draw_check` rules |
| Typed numbers | Behave the same | Differ | Differ |

The raw file stays unchanged (D1), and the Word-reader text is derived data (D2), so option (a) does not touch raw data. The report's "apart from run text" is met inside the reader: compute the number apart, join it once. [inference]

*The separator conflict.* The default `suff` is tab, and most Word legal templates use tab. The splitter never accepts a bare number on a line with a tab. So `3<TAB>Payment` is rejected. The notes also say a `5.1<TAB>` line "may also be treated differently", which was not tested. A `suff` of `nothing` would glue the number to the text ("(a)text"). [inference from the README; the tab claim for dotted numbers is untested] The choices are (i) always write one space after the number, whatever `suff` says, or (ii) write a tab and accept the rejection. Table rows also use tabs between cells in the splitter's rule, so a tab after a number inside a cell adds a second use of the same character. [inference]

*Formats the splitter rejects even when rebuilt faithfully:* `1)` and `A)` without an opening bracket, `I.` and `iv.` with no keyword, `decimalZero` "01.", and `numberInDash`. Templates do use `1)`, `A.` and `I.` for article headings. The reader should rebuild faithfully and the splitter should decide. The reader should not rewrite numbers to suit the splitter. [inference]

*Unknown formats.* ST_NumberFormat has language-specific members (Chinese, Japanese, Korean, Hebrew, Arabic, Hindi, Thai, Russian, Vietnamese, full width). [primary, second hand: [ECMA-376 via docx4java](https://webapp.docx4java.org/OnlineDemo/ecma376/WordML/ST_NumberFormat.html)] The rule "never guess" gives no number and an `InputWarning`. If one level of a multi-level `lvlText` is unknown, give no number for that paragraph and keep counting that level, so that later numbers at other levels stay right. Guard against a `numStyleLink` loop, a missing `num`, a huge `ilvl` and a huge `lvlText`. [inference]

*Fixtures.* The note lists 16 fixtures (multi-level decimal, restart by a second `num`, `startOverride`, `lvlOverride`, `lvlRestart`, `isLgl`, style-linked list, `numStyleLink`, `suff` of tab, space and nothing, bullet and none, unknown formats, beyond 26 letters and `decimalZero`, typed numbers, hidden number, tracked-change interplay, hostile numbering). Word was not available, so no expected number was confirmed against Word. Items 2, 14 and 15 (continue across a second `num`, `w:vanish` on a paragraph mark, a deleted numbered paragraph and the counter) need a Word render before the owner writes the expected values. [inference; memory for the `w:vanish` claim]

**(e) Recommendation.**
1. Keep option (a). Build the number apart inside the reader and join it once. No change to `core`, `char_map` or the splitter contract.
2. Say plainly in the plan and the README that for Word, `Document.text` is the text as Word draws it. The number is part of `text` and of every offset, as a typed number already is.
3. Replace the plan's format sentence with the full rule set: `numId` 0, style-linked levels through the `basedOn` chain, `numStyleLink` and `styleLink`, `lvlOverride`, `startOverride`, `lvlRestart`, `isLgl`, counters keyed by (abstractNum, level), and the formats decimal, `decimalZero`, upper and lower letter (a rule past 26), upper and lower Roman, bullet and none.
4. Ask the owner for the separator. The least risky choice is one space after the number (option i). It is a design choice, so ask.
5. For an unknown or unresolvable format, give no number, raise `word_numbering_unknown` with the paragraph's position, keep the paragraph text and keep counting.
6. Ask the owner to record the shapes that the splitter rejects (`1)`, `A.`, `I.`, `01.`) as a known limit of the splitter.
7. Run one cross-check of pandoc, LibreOffice and docx2python on fixtures 1, 2, 6 and 7, test only, and record where they differ from Word. Add it to S5-M1-T5.

**(f) What would change this recommendation.**
- If the owner chooses to keep the number out of the text (option b or c), every reader of `text` must know the field or the mask, and a `core` shape changes. The notes advise against it. A new `Document` field needs an AGENTS.md question first.
- If a Word render shows that Word continues one list across two `num` entries differently from the pandoc rule, fixture 2 and the counter key change.
- If tests show that `5.1<TAB>` lines are accepted, the separator conflict shrinks to the bare number and the `suff` default could be kept for dotted numbers. This is untested.
- If a cheap English ordinal table (1 to 20) is wanted, `ordinal`, `cardinalText` and `ordinalText` move from the warning path to the supported set. It is an owner choice.
- If a hidden-number test (`w:vanish` on the paragraph mark) shows Word hides the number, a hidden rule is needed. It has no source today.

**Gaps.** The ECMA-376 PDF was not read, so the 17.3.1.19 text and the exact `ST_LevelSuffix` list are second hand. No source for hidden numbering. No source for how Word counts a skipped level. No tool was run. No survey of typed against automatic share. The ux-copy line for the warning was not checked, and the effect on `draw_check` and the privacy step was inferred from the README, not tested.

## Q5. Where Word comments, footnotes, endnotes, headers and footers go

**(a) Plan's current choice (S6 row 5).** "Comments: a `HiddenText` with `COMMENT` whose span covers the commented words of the body; the comment's own text is not put into `Document.text`, so it is never matched or sent, and the raw file keeps it (D1). Footnotes and endnotes: their text goes into `Document.text` after the body, in order, each opening with its number, because they can change a term. Headers and footers: the text of each distinct header and footer goes in once, before the body (headers) and after it (footers), and its span is in `Document.furniture`, as for a PDF."

**(b) Verdict: CHANGE.** The comment rule is sound as far as it goes, but it leaves the comment text with no home. The placement of footnotes, headers and footers is contradicted by tests of the repo's own splitter. This is the weakest row of the plan.

**(c) Evidence.**

*What the real splitter does with each placement.* The researcher ran `read_pasted_text` and `split_clauses` on a made-up contract of 3 clauses (1 to 3.1), read-only, with scratch scripts outside the repo. No `.docx` was read by any tool. [local]

| Placement | Clause splitter result | Sentence result | Effect on links, privacy and the quote check [inference] |
| --- | --- | --- | --- |
| Header lines before the body | Each line becomes an unnumbered heading clause (`p1`, `p2`). A line `CONFIDENTIAL` alone becomes `p1` | One sentence each | A header name enters entity grouping. The quote check works |
| Footer lines after the body (`Page 1 of 3`, `Confidential`) | Join the last clause (3.1) | The last clause gets an extra sentence | Footer text is attributed to the last clause. The AI may cite the extra sentence |
| Footnote after the body, long (`1 text`, `Footnote 1: text`) | Joins the last clause | Extra sentence in the last clause | A term-changing note is attributed to the wrong clause |
| Footnote after the body, short (`4 Fees cap`) | A false top-level clause `4` with heading "Fees cap" | One sentence | A false clause appears in the outline and can be labelled or marked Missing |
| Footnote inline at the reference (`[1: ... ]`) | No new clause | The sentence splits at the note's full stop | A quote that spans the break no longer matches the contract's words |
| Footnote as its own line after the host paragraph, long | Joins the host clause (1.1) | Extra sentence in 1.1 | Terms and cross-references stay with the host clause |
| Footnote as its own line after the host paragraph, short with no full stop (`Footnote 1: Capped`) | Its own unnumbered heading clause `p1` inside the numbered run, with or without blank lines | One sentence | A false clause |

A short note that ends in a full stop was not tested. The README of `ingest` already lists a short first line in title case, such as `CONFIDENTIAL` or `Page 1 of 5`, as a known limit of the splitter. The tests make that limit systematic for every Word file that has a header. [repo: `ingest` README; local]

*Furniture can only point into the text.* `Document.furniture` is a tuple of spans into `text`. So the plan's "span in `Document.furniture`" forces the furniture text into `Document.text`. The typeset pages of a Word file are laid out from `Document.text` (ADR 0001), so whatever is in the text is drawn as contract wording. A note at the end of the text appears at the end of the contract. The user never sees a page-foot layout. [repo facts; inference for the consequence]

*Footnotes and endnotes.*
- `footnoteReference` links a note by `w:id`. A `footnoteRef` inside the note is the auto-number mark and carries no text. [primary: [footnotereference](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.footnotereference?view=openxml-3.0.1), [footnotereferencemark](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.footnotereferencemark?view=openxml-3.0.1)]
- The `w:type` values are `normal`, `separator`, `continuationSeparator` and `continuationNotice`. [primary: [FootnoteEndnoteValues](https://raw.githubusercontent.com/OfficeDev/open-xml-docs-ref-dotnet/live/docs/xml/DocumentFormat.OpenXml.Wordprocessing/FootnoteEndnoteValues.xml)]
- `docx2python` skips notes whose type contains `separator`, and so reads `continuationNotice`. It writes `footnote<id>)` and the text, and uses the `w:id`, not a display number. [primary: [docx_text.py](https://raw.githubusercontent.com/ShayHill/docx2python/HEAD/src/docx2python/docx_text.py) lines 235 to 290]
- Pandoc stores notes by `w:id`, never reads `w:type`, and places the note at the reference. [summary: [Parse.hs](https://raw.githubusercontent.com/jgm/pandoc/main/src/Text/Pandoc/Readers/Docx/Parse.hs)] A pandoc changelog entry shows `sdt` elements occur inside notes. [search: [changelog](https://hackage.haskell.org/package/pandoc-2.14/src/changelog.md)]
- A LibreOffice text export did not write footnotes in a 2021 bug report. [search: [bug 139844](https://lists.freedesktop.org/archives/libreoffice-bugs/2021-January/353032.html)]
- `customMarkFollows` is described as "Suppress Footnote/Endnote Reference Mark" [primary]. Its full meaning (the custom mark follows as ordinary run text) is [memory]. The separator ids (-1 and 0, or 0 and 1) and whether Word shows an orphan note are [memory]. So skip by type, never by id.
- A display number is the count of references in body order, formatted by the note `numFmt`, and the id is not that number. A hostile file can have two references to one id, or a note with no reference. [inference]

*Headers and footers.*
- Each section has up to three header references (first, default, even). If `titlePg` is not set, no first-page header is shown. The same holds for `even` and `evenAndOddHeaders`, which is a document-wide setting. A missing reference is inherited from the previous section by rule. [primary: [headerreference](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.headerreference?view=openxml-3.0.1); [TitlePage](https://raw.githubusercontent.com/OfficeDev/open-xml-docs-ref-dotnet/live/docs/xml/DocumentFormat.OpenXml.Wordprocessing/TitlePage.xml)] The spec text has what reads as a typo ("even" for "odd" in the third inheritance bullet). [primary, the researcher's reading]
- `docx2python` reads every header and footer part with no regard to section, type or whether a section references it, and does no dedupe. [primary: [docx_output.py](https://raw.githubusercontent.com/ShayHill/docx2python/HEAD/src/docx2python/docx_output.py) lines 145 to 160 and 342] Pandoc has no code path for header or footer parts (by absence in Parse.hs). [primary by absence] LibreOffice behaviour: no source found.
- A referenced header that can never show, and a header part that no section references, are hidden from the normal view by the spec's rules. A naive reader such as `docx2python` reaches both. [primary for the rule; inference for the reach]
- The cached field result is the visible text. PAGE and NUMPAGES appear in simple and complex field form. `instrText` is not shown unless field codes are on. Word makes separate parts with identical text when "Link to previous" is off. [memory]
- Comments, tracked changes and `w:vanish` apply inside headers too, so the same run walker should be reused. [inference]

*Comments.*
- A comment is anchored by `commentRangeStart`, `commentRangeEnd` and a required `commentReference`. "The authoritative position of the comment is the required `w:commentReference` element." The start and end are optional. [primary: [python-docx comments analysis](https://python-docx.readthedocs.io/en/latest/dev/analysis/features/comments.html)]
- The marker can sit in many parents (body, paragraph, table cell, hyperlink, `ins`, `del`, `sdtContent`, footnote, endnote, `hdr`, `ftr`). So a flat event stream in document order builds the span better than the tree. [primary: [commentrangestart](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.commentrangestart?view=openxml-3.0.1); inference for the method]
- Threading is in `commentsExtended.xml` (`paraId`, `paraIdParent`, `done`). [search: [CommentEx](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.office2013.word.commentex)]
- `docx2python` returns comments as `(reference text, author, date, comment text)` and keeps them out of the main text. [primary: [README](https://raw.githubusercontent.com/ShayHill/docx2python/HEAD/README.md)] Pandoc reads comments only with `--track-changes=all`. [summary]
- Comment text, author and initials are untrusted text. A comment can contain tables, images and hidden or tiny runs. [inference; memory for "No Markup" view hiding comments]
- "Show me" can scroll to and outline a span that exists in the text. A comment's own text can never appear on the typeset page if it is not in `Document.text`. The hidden-text row in the copy says the text "may be trying to fool this review", and a user cannot judge that without reading it. [inference; repo: Spec 4.3]
- If the comment text is never in `Document.text`, it is never matched, never sent, and never read by `links` or `privacy`. No name can leak from it. [inference]

*Other carriers the walk must handle.* The notes add traps that touch the body walk (S5-M3-T1) as well. [Each one is the grade shown.]
- `mc:AlternateContent` wraps one piece of content in several versions. Word writes a `Choice Requires="wps"` and an older `Fallback` that both hold the same text box. A reader that walks all descendants reads the box twice. [summary: [OpenOffice wiki on MCE](https://wiki.openoffice.org/wiki/OOXML/Markup_Compatibility_and_Extensibility)]
- Pandoc reads the Fallback only. `docx2python` has no handler, so it probably reads both. Okapi reads both and duplicates text. [primary by grep for pandoc: Parse.hs lines 170 to 206; inference for `docx2python`; search for Okapi: [issue 166](https://bitbucket.org/okapiframework/okapi/issues/166/docx-file-with-alternatecontent-in)]
- Text that exists in only one branch is visible to one viewer and not to the other, so a difference between the branches is a hostile signal. [inference] The researcher did not read the normative ISO/IEC 29500-3 clause 10.2. [gap]
- `instrText` is not shown with field codes off, and a field's displayed text is its cached result, which can differ from the instruction. The reader should read results only and flag an unknown instruction. [inference; memory for the field forms]
- `delText` and `w:del` content is not in the accepted view (ADR 0012 amendment), in notes, headers and footers too. A deleted reference can leave an orphan note. [repo; inference]
- Drawing alt text (`descr`, `title`) is not in the page view. [inference]
- Three carriers have no `HiddenReason` member: a header or footer that can never show or that no section reaches, a note with no reference, a differing Choice and Fallback, an unknown `instrText`, and drawing alt text. The first three of these could reuse `INVISIBLE_TEXT`. D5 allows a new member. This is an owner choice that also touches question 6. [repo: system design 3.4 for the nine members; inference for the mapping]

**(d) Options and effects.** For where the comment text lives (the researcher's five options):

| Option | Change to `core` | Effect |
| --- | --- | --- |
| 1. Nowhere in the app | None | The screen shows the commented words only. The user opens Word to read the comment. The user cannot judge it in the app |
| 2. A text field on `HiddenText` | A shape change, a `schema_version` bump from 1, an update of system design 3.4 and the `core` README | Every consumer of `HiddenText` then carries text that must never be sent to the AI |
| 3. A separate `Document` field for comments (author, date, thread parent, text, anchor span) | A shape change and a version bump | `HiddenText` stays as it is. The one field can also carry notes, headers and footers (see below) |
| 4. Comment text in `Document.text` in a marked region | None | The text is matched, split, read by `links` and `privacy`, and sent unless stage 8 filters it. With Q3's "neither skips", hostile text goes to the model by default. Not recommended without an exclusion rule |
| 5. Re-read `comments.xml` from the stored raw file when the screen needs it (D1, stage 12) | None | A reader function outside `read_word_file` and a second parse of untrusted XML, inside the same limits |

For where footnotes and endnotes go:

| Option | Effect (from the table above) |
| --- | --- |
| A. After the body (plan) | A long note joins the last clause and is attributed to the wrong clause. A short note makes a false clause |
| B. Inline at the reference | The note's full stops split the host sentence. Quotes across the break fail |
| C. Own paragraph right after the host paragraph, with an opener | A long note joins the host clause, which is right. A short note makes a false heading clause. Safe only if the note reads as a sentence, which no reader can guarantee (a note may be `See clause 4`, `Ibid` or a citation) |
| D. Out of `Document.text` in a side field | No effect on the splitter. A note that changes a term is then not matched to its clause unless a later stage reads the side field |

For headers and footers:

| Option | Effect |
| --- | --- |
| A. Before and after the body, span in `furniture` (plan) | Header lines become false clauses and shift every clause count. Footer lines join the last clause |
| B. Out of `Document.text` in a side field | The splitter is untouched. `furniture` stays empty for Word. The text is shown only if a screen reads the side field |
| C. In the text, and stage 8 drops the furniture spans before sending | The splitter and `links` still read it, and the Word reading table (S5-M3-T9) must show the effect on the clause outline |

**(e) Recommendation.**
1. **Comments.** Keep the plan's rule: a `HiddenText(COMMENT)` with a span on the commented words, and the comment text not in `Document.text`. Build the span from a flat event stream of start, end and reference. A reference with no range is a point anchor. Flag a comment inside a note or header. Flag an orphan comment (no reference) with `span=None`. Treat the author and initials as untrusted text. Put the question "where does the comment text live" to the owner, and note that option 3 is the one the researcher's evidence supports best if the owner wants the user to read it. Option 1 or 5 is the answer if no `core` change is allowed.
2. **Footnotes and endnotes.** Skip `separator`, `continuationSeparator` and `continuationNotice` by type, never by id. Reach a note only through its reference, by `w:id`. Flag a note with no reference. Count references in body order for a display number, or do not claim one. Do not open a note line with a bare number. Replace the plan's "after the body" placement. The evidence rules out placement A. Placement C keeps meaning with the clause for a full-sentence note, but it fails for a short one, so the owner must decide the opener and the handling of a short note. Adding a full stop would change the contract's words, which the researcher doubts D1 allows.
3. **Headers and footers.** Resolve the effective header for each section by the spec's inheritance rules. Read only a header that can show (`titlePg`, `evenAndOddHeaders`). Dedupe by normalised text, with a token for the result of PAGE, NUMPAGES and SECTIONPAGES. Flag a header that can never show and a part that no section reaches. Both of the plan's placements break the splitter. So ask the owner whether Word furniture belongs in `Document.text` at all. The evidence favours option B (out of the text) with the owner's `core` choice from point 1, because `furniture` can only point into the text.
4. **Alternate content and the rest of the walk.** Take one branch by the MCE rule with a fixed set of supported namespaces, for the body and for text boxes alike. Read a text box once, right after its anchor paragraph. Compare the other branch and flag a difference. Read field results, never `instrText` or `delText`. Unwrap `sdt`, `smartTag`, `hyperlink` and `customXml`. Apply the same walker (hidden runs, tracked changes, comment markers) in notes, headers and footers.
5. **Fixtures (S5-M1-T5).** Both separator id schemes. A custom-mark footnote. An unreferenced note. A `first` header without `titlePg`. Two sections that share a header, and a duplicate header part. PAGE and NUMPAGES in both field forms. A Choice and Fallback pair that match and one that differ. A comment across two paragraphs, a point comment, a reply, an orphan, a comment in a deleted run and a comment on a footnote.

**(f) What would change this recommendation.**
- If the owner allows a `core` change, one new `Document` field for "side parts" (kind, author, date, text, anchor span) can carry comments, headers, footers and, if wanted, notes. That removes the false clauses and keeps the text out of the sent text by default. It needs a `schema_version` bump and a stage 1 note, and AGENTS.md says to ask first.
- If the owner allows no `core` change, comment text takes option 1 or 5, headers and footers stay out of the text with a `HiddenText(span=None)` and a warning, and footnotes take placement C with an owner-chosen opener.
- If a Word render of a real file shows that Word hides an orphan comment or note, or shows a `first` header without `titlePg`, the flags above change. These points are [memory].
- If the splitter is changed to ignore a short first line or a short note, placements A and C improve. That is a splitter change and a different stage, and it is outside this plan (Constitution T11 and S3 apply).
- If stage 8 sends only visible text and drops furniture spans, option C for headers and footers becomes safe for sending, but the clause outline problem remains.

**Gaps.** No primary page for the `ST_FtnEdn` values, the separator ids or `customMarkFollows`. officeopenxml.com could not be fetched. No source on `continuationNotice` content or orphan notes. No source for LibreOffice headers and footers, python-docx text boxes, or pandoc's header handling beyond its absence. The `paraIdParent` attribute was seen only in search summaries. The normative MCE text was not read. The effect on `draw_check` was not tested. No `.docx` was read by any tool; only the splitter was run, on made-up text. The notes list the items still at [memory]: the meaning of `customMarkFollows`, the separator ids by Word version, whether Word shows orphan notes and comments, the "No Markup" view, the `first` and `even` header behaviour in the Word interface, field forms, `sectPr` placement and Word's reply anchoring.

## Evidence quality and links between questions

**What is well supported.** The Linux limit and the `subprocess` choice rest on the Python manual, the Linux man page and the researcher's measurements on two Python versions. The cases of the contrast check rest on one hand-built PDF, so they show which method can catch which case, not how often. The splitter tests of Q5 are exact for the shapes tested but use made-up text.

**What is weak.** Everything about Windows is unrun. The Word number rules come second hand from a copy of the standard. All OOXML behaviour in Q5 comes from the spec text and from tool source, not from Word. The studies of hidden-text injection are mostly search summaries. No source covers rule-based link extraction.

**Links between the questions.**
- Q1 and Q2 share the same limits. The 60 s and 1 GB figures of S5-M2-T1 depend on the timed glyph-record loop (Q2) and on the two meanings of "1 GB" (Q1).
- Q3 and Q5 meet at the `COMMENT` span. The plan's Q3 answer holds only because a comment span covers visible words, and Q5's answer keeps that span.
- Q4 and Q5 meet at the tab. The splitter's tab rule rejects a bare number after a tab (Q4), and the table-cell rule uses tabs between cells (Q5, body walk).
- Q3 and Q5 meet at stage 8. If furniture or note text sits in `Document.text`, stage 8 must drop or mark it before sending. If hidden-layer text has `span=None`, stage 8 must never send it.
- Q5 touches Q6. New `HiddenReason` members for alternate content, field codes, unreferenced parts and alt text are an owner choice for the same decision as `TAG_CHARACTER`.

## Conclusion

The notes confirm the plan's shape on every question and correct its details. The two clearest corrections are mechanical: start the child with `subprocess` and let it limit itself, and give the contrast check the stride. The two corrections that matter most for the product are the separator after a Word list number and the home of Word side text. Both of these come from running the real splitter, not from reading about Word.

One finding runs against the plan's habit of keeping every artefact inside `Document.text`. Word furniture, note text and comment text are each a kind of text that the contract does not say in its own clauses. The tests show that the splitter cannot hold them safely in the text. The evidence leans toward one new place for such text, outside the text that the splitter, `links` and `privacy` read. That is a `core` change, and it is the owner's call.

## Answers and owner decisions needed

| Q | Recommended answer | Needs owner decision |
| --- | --- | --- |
| 1 | `cli` owns the child. Start it with `subprocess` (`python -I -m`, or the app's own executable with a flag when frozen), not a pool. The child sets its own limits first: `RLIMIT_AS` on Linux, a self-assigned job object on Windows. The reply is bounded JSON checked by a `TypeAdapter`, never pickle. State that 1 GB means address space on Linux and committed memory on Windows, and that neither is a sandbox | Yes, one point: may stage 5 add one `cli` module (the child entry and `read_file_in_child`) before stage 6 builds `cli`? If not, the owner must name another place, and the contracts must change |
| 2 | `ingest` renders in the child with `pypdfium2`, greyscale, fixed scale. The pure check takes bytes, width, height and stride. Cap the pixels per page and warn, skip generated and white-space characters, and time the glyph-record loop before the 60 s limit is fixed | No decision needed. Confirm only that one module opening a PDF for text and for render is one B4 decision. The pixel cap value is the planner's |
| 3 | `privacy` replaces names in hidden text too. `links` keeps every edge in stage 5. Record in the stage 8 notes that an edge whose evidence overlaps a hidden span needs a decision. Add a privacy test with hidden text. Stage 8 must never send `span=None` text | Yes, one point: should Rule 9 extend from values to evidence-trail entries (a `links` edge that rests on hidden text is marked, or its dependent entry and note become unsure)? |
| 4 | The rebuilt number goes into `Document.text` at the paragraph start, built apart and joined once. Rebuild with the full rule set (`numId` 0, style links, `lvlOverride`, `startOverride`, `lvlRestart`, `isLgl`, counters by abstractNum and level, `decimalZero`, none). Unknown format: no number and `word_numbering_unknown` | Yes, two points: (1) the separator after the number, one space (the least risky) or the `w:suff` value, which conflicts with the splitter's tab rule; (2) whether `1)`, `A.`, `I.` and `01.` are a known limit of the splitter |
| 5 | Comments: a `HiddenText(COMMENT)` on the commented words, text out of `Document.text`. Footnotes and endnotes: reach by `w:id`, skip separators by type, and do not append after the body or open a line with a bare number. Headers and footers: resolve the effective ones, dedupe, flag the never-shown ones, and keep them out of `Document.text`. Walk alternate content once and read field results only | Yes, three points: (1) where comment text and Word furniture live (a new `Document` field with a version bump, or nowhere, or a re-read of the raw file); (2) the footnote opener and the handling of a short note; (3) new `HiddenReason` members for the carriers that have none (D5) |

## Changes this report asks for in the stage 5 plan

The report does not edit the plan. These rows or tasks would change once the owner answers.

| Where in the plan | Change |
| --- | --- |
| Section 6, row 1 | Replace "a spawned process" with the `subprocess` mechanism. Add who sets the limits, the reply format and the two meanings of the memory figure. Add the frozen-build flag. Add a line that the limits are not a sandbox |
| S5-M2-T5 | Name the three parts: the pure outcome table, the edge runner and `apply_limits`. Name the child entry file. Add a bounded reply. Add the `TypeAdapter` round-trip test |
| S5-M2-T6 | Say where the tests live: real-child tests in root `tests/`, the outcome table in `cli/tests/`, the zip, limit and parser tests in `ingest/tests/` |
| S5-M2-T1 | Note that 1 GB differs by system. Fix the 60 s limit only after the timing of S5-M4-T2 |
| Section 4, checks before starting | Add a re-measure of the address-space floor with the final imports, and a Windows check of the `ctypes` struct size |
| S5-M6-T7 | Add the Windows over-limit allocation test and the struct size test to the Windows job |
| Section 2, "Builds" and "Leaves to later stages" | Add that stage 5 adds one `cli` module, if the owner agrees. Add the `span=None` rule to the stage 8 items |
| Section 6, row 2 | Add the stride to the bitmap call. Add the pixel cap, the skip rule for generated and white-space characters, the cheap-checks-first order and the threshold and dpi constants |
| S5-M4-T2 | Add a timing step for the glyph-record loop on a dense page |
| S5-M5-T1 and S5-M5-T2 | Split the checks: fill, alpha and render mode in T1, and the render spread in T2. Use fixtures far from the threshold. Write the known miss (text under other text or a photo) into the threat list |
| S5-M5-T5 | Add the cases C, E, F, I and K as hostile fixtures and J as a known miss |
| Section 6, row 3 | Keep the answer. Replace "which is the safe direction" with the reasons for `privacy` and say that for `links` it is not clearly safer. Name the open point on Rule 9. Add the privacy test with hidden text and the `span=None` note for stage 8 |
| Section 6, row 4 | Replace the separator sentence. Replace the format sentence with the full rule set. Add the owner point on shapes the splitter rejects |
| S5-M3-T3 | Name the rules of the table above, the partial-failure rule and the guards for a loop, a missing `num` and a huge `ilvl` |
| S5-M1-T5 | Add the 16 numbering fixtures, the note and header fixtures, and the alternate-content and comment fixtures. Add the one-off cross-check of pandoc, LibreOffice and docx2python |
| S5-M3-T9 | The owner writes the expected values, and items 2, 14 and 15 of the numbering fixtures need a Word render first |
| Section 6, row 5 | Replace the placement of footnotes, endnotes, headers and footers. Add the comment text decision, the flat event stream, the orphan rules and the effective-header rules |
| S5-M3-T1 | Add the one-branch rule for alternate content, field results only, and the unwrap of `sdt`, `smartTag`, `hyperlink` and `customXml`. Add a tab between table cells |
| S5-M3-T5 | Add the span rules (point anchor, orphan, comment in a note or header, comment in a deleted run) and the untrusted author text |
| S5-M3-T6 | Rewrite to the owner's answer on placement. Add the separator-type skip, the reference-by-id rule, the unreferenced-note flag and the header resolution |
| Section 6, row 6 and S5-M5-T4 | Add the owner choice on new `HiddenReason` members for the carriers in Q5 |
| Section 6, row 21 and S5-M3-T2 | No change asked. Note that the same run walker runs in notes, headers, footers and comments |
