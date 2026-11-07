# adapters/keyring

## Purpose
Fit the system password store for the API key and encryption key to a port defined in `core`.

## Spec
`docs/spec.md` sections 8 and 9.

## Input shape (planned)
Calls shaped by the port in `core`.

## Output shape (planned)
Results shaped by the port in `core`.

## Depends on
core only.

## Run alone
Not yet. When it's built, add a `__main__.py` so it runs alone against a sample (Constitution S1): `.venv/bin/uv run python -m clause_tracer.adapters.keyring`. It must not need a real key or contract to do that.
