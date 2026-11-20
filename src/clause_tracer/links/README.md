# links

## Purpose
Map cross-references, defined terms and override clauses between clauses.

## Spec
`docs/spec.md` section 6.1, step 5.

## Input shape (planned)
Clauses.

## Output shape (planned)
Cross-references, defined terms, override clauses and references to other documents.

## Sample clause fixture
`sample_clauses.py` writes and reads the clause fixture for the sample contract. The three names below are exported from `links`.

- `SampleInput`: frozen dataclass with two fields, `document: Document` and `clauses: tuple[Clause, ...]`.
- `dump_clause_fixture(document, clauses) -> str`
  - Input: a `Document` for a text file, and its clauses.
  - Output: the fixture as JSON text, ending in one newline.
  - Raises `ValueError` with the message `links sample: text documents only` when the document holds `char_map`, `glyphs`, `pages`, `furniture`, `hidden`, `undecodable` or `tracked_changes`.
- `load_clause_fixture(text) -> SampleInput`
  - Input: fixture text, as written by `dump_clause_fixture`.
  - Output: a `SampleInput`. The non-text fields of its `Document` are empty.
  - Raises `ValueError` with a message that starts `links sample: ` when the text fails one of these checks: it is not JSON; the top level is not an object; `format` or `version` is wrong; a key is unknown or missing; a value has the wrong type; a source kind is not a text kind; a span lies outside the text; a clause id is repeated; a parent id is unknown; a sentence span lies outside its clause.

Fixture format: `format` is `clause-tracer-links-sample` and `version` is `1`. The layout is:

```
format
version
document: schema_version, source {name, kind, sha256, size}, text, warnings [{code, page}]
clauses: [{id, number, heading, level, parent_id, start, end, numbering_source,
           sentences [{id, start, end}]}]
```

`samples/developer-agreement.clauses.json` is the sample fixture. It is the `ingest` output for the developer agreement sample. A root test keeps it in step with `ingest`.

`tests/case_builder.py` (`build_case`, `span_of`) is test code. It is not exported.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.links`
