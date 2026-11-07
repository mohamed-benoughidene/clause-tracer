# adapters

## Purpose
Fit real outside tools (OpenRouter, Presidio, storage, keyring) to the ports defined in core.

## Spec
`docs/spec.md` sections 8 and 9.

## Input shape (planned)
Calls from cli, shaped by ports in core.

## Output shape (planned)
Results shaped by ports in core.

## Depends on
core only.

## Run alone
`.venv/bin/uv run python -m clause_tracer.adapters`
