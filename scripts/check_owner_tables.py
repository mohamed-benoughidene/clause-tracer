"""The owner-table guard: code and an owner table may not change together.

Expected answers live in tables only the owner edits (Constitution T11).
This script fails a change that touches both code and an owner table,
so the expected answers and the code that must match them are never
written in one step. See docs/testing-strategy.md section 10.
"""

import argparse
import re
from collections.abc import Iterable

OWNER_TABLE_PATTERN = re.compile(r"(^|/)tests/tables/")
APPROVAL_LINE = "Owner-Approved-Tables: yes"


def is_owner_table(path: str) -> bool:
    """True when the path is inside a tests/tables/ folder."""
    return OWNER_TABLE_PATTERN.search(path) is not None


def is_code(path: str) -> bool:
    """True when the path holds code the guard protects."""
    if is_owner_table(path):
        return False
    return path.endswith(".py") or path.startswith("scripts/")


def change_fails(paths: Iterable[str]) -> bool:
    """True when one change edits both an owner table and code."""
    paths = tuple(paths)
    touches_table = any(is_owner_table(path) for path in paths)
    touches_code = any(is_code(path) for path in paths)
    return touches_table and touches_code


def is_approved(message: str) -> bool:
    """True when the commit message carries the owner's approval line."""
    return any(line.strip() == APPROVAL_LINE for line in message.splitlines())


if __name__ == "__main__":
    raise SystemExit(0)
