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

## Output shape
A `Document` with no glyphs: `glyphs`, `char_map`, `pages`, `furniture`, `hidden`,
`undecodable` and `tracked_changes` are empty in stage 2.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.ingest`
