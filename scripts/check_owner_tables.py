"""The owner-table guard: code and an owner table may not change together.

Expected answers live in tables only the owner edits (Constitution T11).
This script fails a change that touches both code and an owner table,
so the expected answers and the code that must match them are never
written in one step. See docs/testing-strategy.md section 10.
"""

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

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


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(("git", *args), cwd=repo, check=True, capture_output=True, text=True)
    return done.stdout


def working_tree_paths(repo: Path) -> tuple[str, ...]:
    """The paths the working tree changed, relative to the repo root."""
    changed = _git(repo, "diff", "--name-only", "HEAD")
    untracked = _git(repo, "ls-files", "--others", "--exclude-standard")
    return tuple(sorted(set(changed.split()) | set(untracked.split())))


def commit_paths(repo: Path, sha: str) -> tuple[str, ...]:
    """The paths one commit changed."""
    return tuple(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).split())


def commits_since(repo: Path, base: str) -> tuple[str, ...]:
    """The shas of the commits after base, oldest first, merges left out."""
    return tuple(_git(repo, "rev-list", "--no-merges", "--reverse", f"{base}..HEAD").split())


def commit_message(repo: Path, sha: str) -> str:
    """The full message of one commit."""
    return _git(repo, "log", "-1", "--format=%B", sha)


def main(argv: list[str] | None = None) -> int:
    """Run the guard on the working tree, or on every commit since a base."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--commits",
        metavar="BASE",
        help="check each commit since this base on its own",
    )
    args = parser.parse_args(argv)
    repo = Path.cwd()
    if args.commits is None:
        paths = working_tree_paths(repo)
        if change_fails(paths):
            tables = sorted(p for p in paths if is_owner_table(p))
            print(
                "owner-table guard: working tree edits code and an owner table: "
                f"{', '.join(tables)}",
                file=sys.stderr,
            )
            return 1
        return 0
    failed = False
    for sha in commits_since(repo, args.commits):
        if is_approved(commit_message(repo, sha)):
            continue
        paths = commit_paths(repo, sha)
        if change_fails(paths):
            tables = sorted(p for p in paths if is_owner_table(p))
            print(
                f"owner-table guard: {sha[:7]} edits code and an owner table: {', '.join(tables)}",
                file=sys.stderr,
            )
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
