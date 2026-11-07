# links

## Purpose
Map cross-references, defined terms and override clauses between clauses.

## Spec
`docs/spec.md` section 6.1, step 5.

## Input shape (planned)
Clauses.

## Output shape (planned)
Cross-references, defined terms, override clauses and references to other documents.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.links`
