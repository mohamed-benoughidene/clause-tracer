#!/usr/bin/env bash
# The one command agents run before finishing: lint, format, types, import rules, copy and look, tests.
# Stops at the first failure. Uses the repo's own uv (.venv/bin/uv) first, then a uv on PATH (CI).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -x .venv/bin/uv ]; then
  run() { .venv/bin/uv run "$@"; }
elif command -v uv >/dev/null 2>&1; then
  run() { uv run "$@"; }
else
  echo "No uv found. Set up first: python3 -m venv .venv && .venv/bin/pip install --no-cache-dir uv && .venv/bin/uv sync" >&2
  exit 1
fi

run ruff check
run ruff format --check
run mypy
run lint-imports
run python scripts/copy_lint.py
run coverage run -m pytest -q
run coverage report --include='src/clause_tracer/core/*' --fail-under=95
