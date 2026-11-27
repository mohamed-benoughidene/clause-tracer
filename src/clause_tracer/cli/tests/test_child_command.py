"""The command line of the child and the runner's source (S5-M2-T6)."""

import sys
from pathlib import Path

from clause_tracer.cli.child_runner import child_command

SOURCE = Path(__file__).resolve().parents[1] / "child_runner.py"


def test_child_command_installed() -> None:
    assert child_command(name="a.docx", memory_bytes=5, frozen=False) == [
        sys.executable,
        "-I",
        "-m",
        "clause_tracer.cli._child",
        "--memory-bytes",
        "5",
        "--name",
        "a.docx",
    ]


def test_child_command_frozen() -> None:
    assert child_command(name="a.docx", memory_bytes=5, frozen=True) == [
        sys.executable,
        "--read-child",
        "--memory-bytes",
        "5",
        "--name",
        "a.docx",
    ]


def test_no_pickle_no_shell() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert "pickle" not in source
    assert "shell=True" not in source
    assert "ProcessPoolExecutor" not in source
    assert "os.fork" not in source
