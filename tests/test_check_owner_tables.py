"""Tests for the owner-table guard script (T11)."""

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_owner_tables.py"

_spec = importlib.util.spec_from_file_location("check_owner_tables", SCRIPT)
assert _spec is not None and _spec.loader is not None
guard = importlib.util.module_from_spec(_spec)
sys.modules["check_owner_tables"] = guard
_spec.loader.exec_module(guard)


def test_owner_table_paths() -> None:
    assert guard.is_owner_table("src/clause_tracer/core/tests/tables/label_rules.toml")
    assert guard.is_owner_table("tests/tables/x.csv")
    assert not guard.is_owner_table("src/clause_tracer/core/tests/test_labels.py")
    assert not guard.is_owner_table("src/clause_tracer/core/samples/spec-14-5.toml")
    assert not guard.is_owner_table("docs/tables/x.toml")


def test_code_paths() -> None:
    assert guard.is_code("src/clause_tracer/core/labels.py")
    assert guard.is_code("scripts/check.sh")
    assert not guard.is_code("docs/plans/stage-01-core.md")
    assert not guard.is_code("uv.lock")
    assert not guard.is_code("src/clause_tracer/core/tests/tables/label_rules.toml")


def test_change_fails_only_when_both() -> None:
    assert guard.change_fails(["a/tests/tables/t.toml", "src/x.py"])
    assert not guard.change_fails(["a/tests/tables/t.toml", "docs/plans/p.md"])
    assert not guard.change_fails(["src/x.py", "README.md"])
    assert not guard.change_fails([])


def test_approval_line() -> None:
    assert guard.is_approved("fix\n\nOwner-Approved-Tables: yes\n")
    assert not guard.is_approved("Owner-Approved-Tables: no")
    assert not guard.is_approved("owner-approved-tables: yes")
