# ADR-0007: Read PDFs with pypdfium2 alone and Word files with one hardened parser

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 6.1](../spec.md) step 1 reads PDF, Word, text and Markdown, and finds hidden text, comments and tracked changes. Step 2 splits clauses and step 14 builds the report PDF. Spec 8.4 says Word files are read with external links off. [ADR 0001](0001-show-contracts-as-original-pdf-pages.md) shows PDFs as their original pages, so every character needs a page box.

The [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) paired pdfplumber for geometry with pypdfium2 for page images. It called pypdfium2-alone "unverified". [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) checked the PDFium headers on 11 Nov 2026 and found the fields are there. It also found two pdfplumber bugs still open. Runtime dependencies must be MIT, BSD or Apache, and MPL-2.0 needs an explicit decision. Contracts are untrusted input (Spec 8.4).

## Decision
The project owner accepted the following on 12 Nov 2026.

- **PDF.** pypdfium2 as the single engine, through its raw API, for page images, per-character geometry and hidden-text fields.
- **Cross-check.** pdfplumber only in tests, never at runtime.
- **Hidden layers.** pikepdf (MPL-2.0). The owner allowed it on 12 Nov 2026 as a named exception to the MIT, BSD and Apache rule. As a working rule, not legal advice: use pikepdf unmodified as a dependency, and never copy its source files into this repo, because MPL-2.0 puts conditions on changed copies of its own files. Have a lawyer confirm this before a release that ships it.
- **Word.** Read the zip directly and parse every part with one explicit, hardened lxml parser. Reject any DOCTYPE. Cap sizes before reading.
- **Sentences.** NUPunkt, which returns character spans. Quote checks tolerate a missed split.
- **Report PDF.** ReportLab (BSD, pure Python, about 2 MB).
- **Hostile files.** Set limits before parsing, and parse in a resource-limited child process.

## Options Considered

### Option A: pypdfium2 alone, hardened lxml, NUPunkt, ReportLab (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: the raw PDFium API is low-level |
| Cost | pypdfium2 wheels are 3.6 to 4.5 MB on PyPI |
| Scalability | Single user, not a scale question |
| Team familiarity | Med: raw C-style calls wrapped in Python |

**Pros:** one coordinate system, so no join between two libraries. PDFium exposes per-character box, font size, fill colour with alpha, render mode (through the text object), and generated, hyphen and Unicode-error flags ([fpdf_text.h](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_text.h), [fpdf_edit.h](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_edit.h)).
**Cons:** the raw API is harder to read than pdfplumber's. Reading order on two-column contracts is not benchmarked.

### Option B: pdfplumber plus pypdfium2 at runtime
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med to High: one pure coordinate function joins two libraries |
| Cost | Two PDF packages in the bundle |
| Scalability | pdfplumber is slow (about 1.6 s for 15 pages in the earlier report) |
| Team familiarity | High: pdfplumber's API is friendly |

**Pros:** pdfplumber's colour and font fields are well known.
**Cons:** `dedupe_chars` is still quadratic ([issue #1419](https://github.com/jsvine/pdfplumber/issues/1419) is open, and 0.11.10 of 15 Jun 2026 predates it). Characters can vanish through a pdfminer.six bug ([issue #1415](https://github.com/jsvine/pdfplumber/issues/1415)). The earlier report wrongly said #1419 was fixed.

### Option C: python-docx or docx2python for Word
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low to start |
| Cost | One package |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** quick to start.
**Cons:** python-docx is for creating and editing. It has no list-number rendering, an issue open since 2018 ([python-docx #590](https://github.com/python-openxml/python-docx/issues/590)), and no tracked-change handling. docx2python returns nested string lists.

### Option D: Typst through typst-py for the report
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low: a restylable template |
| Cost | 30 to 37 MB |
| Scalability | Single user, not a scale question |
| Team familiarity | Med |

**Pros:** tagged, accessible PDFs. It wins if accessibility becomes a requirement.
**Cons:** much larger than ReportLab. The Typst compiler licence was not checked.

pySBD (last release 2021), syntok (2022) and spaCy's sentence splitter (ids tied to a model version) lost to NUPunkt. PyMuPDF is AGPL and fails the licence rule.

## Trade-off Analysis
The PDFium field list is verified against the headers. The single-engine choice is judgement. NUPunkt's current README gives 0.90 to 0.902 precision and 0.782 F1 on legal data ([nupunkt](https://github.com/alea-institute/nupunkt)). Recall is the weaker side, so about one boundary in five may be missed or wrong on hard text. That replaces the earlier report's "91.1%". Sentence ids must therefore tolerate a missed split. The earlier report's "8.8 MB" for pypdfium2 may be an installed size; that is unverified.

Hostile-file limits are judgement on verified library facts. Python's `zipfile` does not enforce member count, size or ratio limits ([zipfile docs](https://docs.python.org/3/library/zipfile.html)). Declared sizes are attacker-controlled, so the real read is capped too. The lxml parser uses `resolve_entities=False`, `no_network=True`, `load_dtd=False` and `huge_tree` off. The report judges `defusedxml` too stale (last release 2021). Its claim that the lxml wrapper is deprecated is from memory.

Gaps carried over: not verified that the bundled PDFium build includes every function; whether PDFium exposes optional-content visibility is unchecked; docx2python numbering and tracked-change support are unverified; ReportLab PDF/UA support is unchecked; no independent contract benchmark for NUPunkt exists.

## Consequences
- Easier: one coordinate system removes the most common source of highlight bugs.
- Easier: the child-process parse is also the production design, so hostile-file tests exercise real code.
- Harder: the Word reader rebuilds list numbers and resolves hidden runs itself.
- Revisit if the golden set shows poor reading order on two-column PDFs, or if accessibility becomes a requirement (then Typst).

## Action Items
1. [ ] Check that the pypdfium2 build pinned in `uv.lock` exposes every needed PDFium function, including optional-content visibility.
2. [x] Decide on pikepdf (MPL-2.0) or pypdf for hidden layers: pikepdf allowed, 12 Nov 2026. Add it to the licence check's allow-list by name, not MPL in general.
3. [ ] Set the limits (member count, expanded size, ratio, page count, time, memory) and test each one. Values are `[Assumption]` until measured.
4. [ ] Add the pdfplumber cross-check as a test-only dependency.
5. [x] Add the hidden-layer licence decision to Spec 13 (done 12 Nov 2026).
6. [ ] Update `src/clause_tracer/ingest/README.md` when `ingest` is built.
