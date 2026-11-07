# core

## Purpose
Pure rules: playbook and review models and label picking, with no files, network, clock or AI.

## Spec
`docs/spec.md` section 5, and section 6.1 step 8 (pick labels).

## Input shape (planned)
Plain typed values: the playbook snapshot, positions and extracted values.

## Output shape (planned)
Frozen dataclasses, and a label for each position.

## Depends on
Nothing. It imports no other clause_tracer module.

## Run alone
`.venv/bin/uv run python -m clause_tracer.core`
