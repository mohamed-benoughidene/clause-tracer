# privacy

## Purpose
Find personal data in clauses and turn it into placeholder text.

## Spec
`docs/spec.md` sections 4.2 and 8, and section 6.1 steps 3–4.

## Input shape (planned)
Clauses and typed party details.

## Output shape (planned)
Suggested placeholders, then the user's confirmed placeholder text.

## Depends on
core only. The Presidio detector is passed in by cli.

## Run alone
`.venv/bin/uv run python -m clause_tracer.privacy`
