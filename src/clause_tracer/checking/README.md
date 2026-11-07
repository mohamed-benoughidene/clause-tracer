# checking

## Purpose
Match, extract, quote-check, label, judge, explain and summarise clauses against a playbook.

## Spec
`docs/spec.md` section 6.1 (steps 6a–7 and 9–11) and section 6.2. Labels are picked by `core` (step 8, section 5).

## Input shape (planned)
Placeholder text, positions and a playbook snapshot.

## Output shape (planned)
Matched clauses, checked quotes and values, labels, levels, explanations and not-covered summaries.

## Depends on
core only. The AI client is passed in by cli.

## Run alone
`.venv/bin/uv run python -m clause_tracer.checking`
