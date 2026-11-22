# privacy

## Purpose
Find personal data in clauses and turn it into placeholder text.

## Spec
`docs/spec.md` sections 4.2 and 8, and section 6.1 steps 3–4.

## Input shape (planned)
Clauses and typed party details.

## Output shape (planned)
Suggested placeholders, then the user's confirmed placeholder text.

## Sample fixture
`sample_input.py` holds the input of `find_personal_data` for the sample: the
document, its clauses, the typed parties and the defined terms. `privacy` may not
import `ingest` or `links`, so the sample arrives as a committed JSON fixture and
a root test keeps it in step with both modules.

The format is `{"format": "clause-tracer-privacy-sample", "version": 1, ...}`
with these keys:

- `document`: `schema_version`, `source` (`name`, `kind`, `sha256`, `size`),
  `text` and `warnings` (`code`, `page`);
- `clauses`: `id`, `number`, `heading`, `level`, `parent_id`, `start`, `end`,
  `numbering_source` and `sentences` (`id`, `start`, `end`);
- `parties`: `name`, `address` and `yours`;
- `terms`: `term`, `definition` (`start`, `end`) and `uses` (`start`, `end`).

`dump_privacy_fixture` accepts text documents only: it refuses a document with
glyphs, pages or other non-text fields, and a source kind other than `text`,
`markdown` or `pasted`. `load_privacy_fixture` checks the JSON shape once at the
door. Both then run `_check_input`, which raises `ValueError` with the prefix
`privacy sample: ` on the first failure: a span outside the text, a level below
1, a duplicate clause or sentence id, a sentence outside its clause, a clause or
sentence out of order, or an empty party name.

The caller reads and writes the fixture. `privacy` code reads no file (T1).

`tests/goldens/` holds the expected report of the sample, written only by
`--update-goldens`.

## Depends on
core only. The Presidio detector is passed in by cli.

## Run alone
`.venv/bin/uv run python -m clause_tracer.privacy`
