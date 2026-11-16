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


def _make_repo(repo: Path) -> str:
    """A fresh git repo with one committed README.md; returns the base sha."""
    import subprocess

    def run(*args: str) -> str:
        return subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True).stdout

    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    run("git", "config", "user.name", "Test")
    run("git", "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("test repo\n", encoding="utf-8")
    run("git", "add", "README.md")
    run("git", "commit", "-q", "-m", "base")
    return run("git", "rev-parse", "HEAD").strip()


def test_working_tree_mixed_change_fails(tmp_path: Path, monkeypatch: object) -> None:
    _make_repo(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    tables = tmp_path / "pkg" / "tests" / "tables"
    tables.mkdir(parents=True)
    (tables / "t.toml").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert guard.main([]) == 1


def test_working_tree_tables_only_passes(tmp_path: Path, monkeypatch: object) -> None:
    _make_repo(tmp_path)
    tables = tmp_path / "pkg" / "tests" / "tables"
    tables.mkdir(parents=True)
    (tables / "t.toml").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert guard.main([]) == 0


def test_commits_checked_one_by_one(tmp_path: Path, monkeypatch: object) -> None:
    import subprocess

    base = _make_repo(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "src/a.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "code only"], cwd=tmp_path, check=True)
    tables = tmp_path / "pkg" / "tests" / "tables"
    tables.mkdir(parents=True)
    (tables / "t.toml").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "pkg"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "table only"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    assert guard.main(["--commits", base]) == 0


def test_mixed_commit_fails(tmp_path: Path, monkeypatch: object) -> None:
    import subprocess

    base = _make_repo(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    tables = tmp_path / "pkg" / "tests" / "tables"
    tables.mkdir(parents=True)
    (tables / "t.toml").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "both in one"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    assert guard.main(["--commits", base]) == 1


def test_approved_mixed_commit_passes(tmp_path: Path, monkeypatch: object) -> None:
    import subprocess

    base = _make_repo(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    tables = tmp_path / "pkg" / "tests" / "tables"
    tables.mkdir(parents=True)
    (tables / "t.toml").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-q",
            "-m",
            "both in one\n\nOwner-Approved-Tables: yes",
        ],
        cwd=tmp_path,
        check=True,
    )
    monkeypatch.chdir(tmp_path)
    assert guard.main(["--commits", base]) == 0
