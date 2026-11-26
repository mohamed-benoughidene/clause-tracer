# ingest

## Purpose
Read a text file, a Markdown file or pasted text, and split it into clauses
with sentence ids.

## Spec
`docs/spec.md` section 6.1, steps 1–2.

## Public calls

### `read_text_file`

`read_text_file(data: bytes, *, kind: FileKind, name: str) -> Document`

Reads a text or Markdown file. `kind` is `FileKind.TEXT` or `FileKind.MARKDOWN`;
another kind raises `ValueError`, which is a bug in the caller. Reads strict UTF-8.
Raises `InputTooLargeError` over 20 MB or 50,000 words, `NotUtf8Error` for bytes
that are not UTF-8, `NotTextError` for a NUL character, and `EmptyInputError`
when no character other than spaces, line breaks and byte-order marks is present.
No side effects. `DOCUMENT_SCHEMA_VERSION` is the version it writes (2).

### `read_pasted_text`

`read_pasted_text(text: str) -> Document`

Reads pasted text exactly like a text file. Raises `InputTooLargeError` over
20 MB or 50,000 words, `NotUtf8Error` for a lone surrogate, `NotTextError` for a
NUL character, and `EmptyInputError` when no character other than spaces, line
breaks and byte-order marks is present. The character count is checked before
the text is encoded. For a text with too many characters the error's context
holds `size_chars`; for one with too many bytes it holds `size_bytes`. Both hold
`limit_bytes`. No side effects.

### `split_clauses`

`split_clauses(document: Document) -> tuple[Clause, ...]`

Reads only `document.text`. Returns the clauses in text order, each with its
id, number, heading, level, parent, span and sentences. A blank text gives no
clauses. When no marker is accepted, the text is split by paragraph. No errors
and no side effects.

## Shapes it returns
A `Document` (from `core`) with no glyphs: `glyphs`, `char_map`, `pages`,
`furniture`, `hidden`, `undecodable` and `tracked_changes` are empty in stage 2.
Its `warnings` hold `not_english` when the text does not look English.

`split_clauses` returns `Clause` shapes, each with `Sentence` shapes in
`sentences`. `numbering_source` is `NUMBERING_NUMBERS` (`"numbers"`) when a
marker opens the clauses, and `NUMBERING_PARAGRAPHS` (`"paragraphs"`) when no
marker is accepted.

A text that does not look English carries the warning `not_english`
(`WARNING_NOT_ENGLISH`). Lingua names the language of the text, and the warning
is set when that language is not English. A text of fewer than 10 words is
never warned about, because it is too short to tell (`[Assumption]`, tuned in
testing). The warning never stops the read: the user can go on with the
contract.

## Clause and sentence ids
Clause ids come from the number and the order: `5.1`, `7.1(a)(i)`, `S1` and
`S1.2` inside a schedule, `p1` for a clause with no number, `5.1~2` when a
number appears twice, and `4` for `Article IV`. `number` keeps the digits as
the text writes them: `01.2` gives `01.2`, and its id is `1.2`.

Sentence ids add `.s1`, `.s2` and so on to the clause id (`5.1.s3`). A clause's
sentences cover the whole clause: each starts where the one before ends. The
clause number stays in the first sentence.

A line that ends in a colon ends a sentence, so a lead-in line such as
`1.1 In this Agreement the following words have these meanings:` is a sentence
of its own. A hard-wrapped line that ends in a colon in the middle of a sentence
also breaks there: a known limit.

A line with a tab between two cells, such as a row of a table, starts a
sentence. A tab only at the start or the end of a line does not, so a hanging
indent stays one sentence. A sentence of only spaces, tabs and line breaks joins
the sentence after it. A line of prose right after a table joins the last row,
and a Markdown table, which uses `|` and not tabs, stays one sentence: known
limits.

## What the splitter reads, and what it does not
At the start of a line it reads:

- decimal numbers, `5.` and `5.1` to `5.1.2.3.4`;
- bracketed items, `(a)`, `(i)`, `(A)`, `(1)` and `a)` and `i)`;
- the keywords `Clause 5` and `Article IV`, with ids in Arabic numbers;
- a bare `3 Payment`, but never on a line with a tab, never with a month name,
  and before any numbering only a bare `1`;
- schedule headings (`Schedule`, `Annex`, `Appendix`, `Exhibit`), which start
  numbering again.

A schedule marker opens a clause only when nothing follows the designation, or
a separator follows it: `·`, `:`, `-`, `–` or `—`. A line such as
`Schedule 2 to this Agreement ...` is body text.

A number counts only when it follows on from the numbering so far. Markdown
symbols before a number are looked past and stay in the text.

A numbered clause has a heading when its marker is a decimal number, a keyword,
a schedule or a bare number, the rest of its line is short, does not end like a
sentence, and every later line in the clause is blank. A bracketed item such as
`(a)` never has a heading. An unnumbered heading clause takes its own line as
the heading, and only when a marker follows it, the line comes after a blank
line, or it is the first line of the text and in title case: every word starts
with a capital letter, except the joining words a, an, and, by, for, in, of,
on, or, the, to and with after the first word. So a first line such as
`This Agreement is made on`, wrapped in the middle of a sentence, is not a
heading. A line that opens with `Signed`, `Executed` or `In witness whereof` is
a heading whatever its length. The clause of text before the first clause has
no heading.

The line of a short unnumbered heading ends a sentence: the next sentence starts
at the next non-blank line. A long signature line does not end a sentence. A
short first line in title case that is not a title also becomes a heading,
such as a name at the top of an address, a label such as `CONFIDENTIAL` or
`Page 1 of 5`, or the first line of a title wrapped over two lines: a known
limit.

In the paragraph case, a blank line between two non-blank lines starts a new
paragraph; when the text has no such blank line, every non-blank line is a
paragraph. A line holding only spaces, tabs and byte-order marks counts as
blank. The first clause starts at 0 and the last ends at the end of the text.
The clauses cover the whole text: each starts where the one before ends.

It does not read, in this stage:

- Word and PDF files, glyphs, page boxes, furniture, tracked changes, the
  hostile-file limits and the child process: stage 5.
- Any hidden text, including zero-width and bidi characters in a text file:
  stage 5.
- Confusable letters and line-end hyphen joins in the match key: stage 5.
- Cross-references, defined terms and schedule references: stage 3.
- `A)` and `1)` without an opening bracket; "Section 5" and other keywords; a
  keyword with a decimal number ("Clause 5.1"); Roman numbers without a
  keyword; and unnumbered headings longer than 8 words or 60 characters, except
  a line that opens with `Signed`, `Executed` or `In witness whereof`.
- A number that skips a value: the text that follows stays in the clause
  before the gap. A numbered list inside a clause becomes clauses of its own.
  A split can be fixed by hand at the contract check (stages 6 and 12).

## Samples
`samples/developer-agreement.txt` is the sample contract of Spec 14.5.
`samples/plain-paragraphs.md` is a short Markdown letter with no numbers.
[The samples README](samples/README.md) says what each file is, which tests read
it, and the credit for the adapted contract. Samples are test data, never real
contracts.

## Golden files
`tests/goldens/developer-agreement.outline.txt` and
`tests/goldens/plain-paragraphs.outline.txt` hold the outline of each sample.
Regenerate them only with `--update-goldens`, in a commit of their own, and ask
the owner to read the diff.

## Owner tables
Only the owner edits these tables (Constitution T11):

| File | Columns | Owner task |
| --- | --- | --- |
| `tests/tables/clause_split.toml` | `id`, `text`, `numbering`, then the expected `clauses` | S2-M3-T5 |
| `tests/tables/not_english.toml` | `id`, `text`, `warned` | S2-M5-T3 |

The wide match fold's table lives in `core`: `core/tests/tables/match_fold.toml`
(owner task S2-M5-T1).

## Run alone
`.venv/bin/uv run python -m clause_tracer.ingest` reads
`samples/developer-agreement.txt`.

`.venv/bin/uv run python -m clause_tracer.ingest --input samples/plain-paragraphs.md`
reads another text or Markdown file. A `.md` or `.markdown` suffix, in any
case, is read as Markdown; every other suffix is read as text.

`.venv/bin/uv run python -m clause_tracer.ingest --full` prints each sentence in
full instead of its first 60 characters. The flag writes to standard output only.
The golden files always use the cut preview.

Exit 0 prints the outline and ends. Exit 3 means the file could not be read, or
it failed an input check; the message names the error code (`not_utf8`, for
example). The outline has one line for the source, the numbering and the
warnings, then one line for each clause and one for each of its sentences.
Cells are joined with one tab.

## Depends on
`core`, NUPunkt (sentence starts) and Lingua (the not-English warning). Each
library is imported in one file only.

Runtime libraries (stage 5), each imported in one file of `ingest` only (B4):

- `pypdfium2` 5.15.2 (PDFium 159.0.8149): `_pdfium.py`.
- `pikepdf` 10.18.2: `_layers.py`.
- `lxml` 6.1.3: `_xml.py`.

Test-only tools (stage 5), imported only in a `tests/` folder or in `scripts/`:

- `reportlab` 5.1.2: builds the PDF fixtures.
- `pillow` 13.0.0: writes the images inside those fixtures. It also ships with the app, because `pikepdf` requires it.
- `pdfplumber` 0.11.11: the cross-check of the PDF reader (ADR 0007 action item 4).
