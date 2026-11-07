# ingest

## Purpose
Read the contract file and split it into numbered clauses.

## Spec
`docs/spec.md` section 6.1, steps 1–2.

## Input shape (planned)
PDF, .docx, .txt, .md or pasted text.

## Output shape (planned)
Plain text with hidden text marked, then clauses with numbers and locations.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.ingest`
