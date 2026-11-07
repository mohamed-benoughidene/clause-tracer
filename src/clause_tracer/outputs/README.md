# outputs

## Purpose
Write the message to the other side and build the PDF report.

## Spec
`docs/spec.md` section 6.1, steps 13–14.

## Input shape (planned)
Ticked items, tone, quotes and preferred levels; the review data.

## Output shape (planned)
A message with [TO] and [FROM] markers; a PDF.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.outputs`
