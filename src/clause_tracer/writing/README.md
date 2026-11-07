# writing

## Purpose
Rewrite a clause on request, then hand it back for re-checking.

## Spec
`docs/spec.md` section 6.1, step 12.

## Input shape (planned)
A clause with placeholders, affected positions and an optional instruction.

## Output shape (planned)
New clause wording.

## Depends on
core only. The AI client is passed in by cli. To re-check a rewrite, cli passes the new wording to `checking` (ADR 0004).

## Run alone
`.venv/bin/uv run python -m clause_tracer.writing`
