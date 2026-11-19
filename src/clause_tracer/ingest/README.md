# ingest

## Purpose
Read the contract file and split it into numbered clauses.

## Spec
`docs/spec.md` section 6.1, steps 1–2.

## Input shape

### `read_text_file`

`read_text_file(data: bytes, *, kind: FileKind, name: str) -> Document`

Reads a text or Markdown file. `kind` is `FileKind.TEXT` or `FileKind.MARKDOWN`;
another kind raises `ValueError`, which is a bug in the caller. Reads strict UTF-8.
Raises `InputTooLargeError` over 20 MB or 50,000 words, `NotUtf8Error` for bytes
that are not UTF-8, `NotTextError` for a NUL character, and `EmptyInputError`
when no character other than spaces, line breaks and byte-order marks is present.
No side effects.

### `read_pasted_text`

`read_pasted_text(text: str) -> Document`

Reads pasted text exactly like a text file. Raises `InputTooLargeError` over
20 MB or 50,000 words, `NotUtf8Error` for a lone surrogate, `NotTextError` for a
NUL character, and `EmptyInputError` when no character other than spaces, line
breaks and byte-order marks is present. The character count is checked before
the text is encoded. For a text with too many characters the error's context
holds `size_chars`; for one with too many bytes it holds `size_bytes`. Both hold
`limit_bytes`. No side effects.

## Splitting

### `split_clauses`

`split_clauses(document: Document) -> tuple[Clause, ...]`

Reads only `document.text`. Returns the clauses in text order, each with its
id, number, heading, level, parent, span and sentences. A blank text gives no
clauses. When no marker is accepted, the text is split by paragraph. No errors
and no side effects.

Clause ids come from the number and the order: `5.1`, `7.1(a)(i)`, `S1` and
`S1.2` inside a schedule, `p1` for a clause with no number, `5.1~2` when a
number appears twice, and `4` for `Article IV`.

`numbering_source` is `numbers` when a marker opens the clauses, and
`paragraphs` when no marker is accepted. The clauses cover the whole text:
each starts where the one before ends.

A clause that a marker starts has a heading when the rest of its line is short,
does not end like a sentence, and every later line in the clause is blank. An
unnumbered heading clause takes its own line as the heading. The clause of text
before the first clause has no heading.

## Output shape
A `Document` with no glyphs: `glyphs`, `char_map`, `pages`, `furniture`, `hidden`,
`undecodable` and `tracked_changes` are empty in stage 2.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.ingest`
