"""Smoke tests for the module command: python -m clause_tracer.ingest (S2-M4-T3)."""

from pathlib import Path

import pytest

from clause_tracer.core import FileKind
from clause_tracer.ingest import read_text_file, split_clauses
from clause_tracer.ingest.__main__ import DEFAULT_INPUT, main

SAMPLES = Path(__file__).parent.parent / "samples"


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_default_run_prints_the_sample(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0

    output = capsys.readouterr().out
    assert output.splitlines()[0].startswith("source\ttext\t")
    assert "numbering\tnumbers" in output.splitlines()


def test_markdown_input(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--input", str(SAMPLES / "plain-paragraphs.md")]) == 0

    assert "numbering\tparagraphs" in capsys.readouterr().out.splitlines()


def test_sample_has_65_clauses() -> None:
    document = read_text_file(
        DEFAULT_INPUT.read_bytes(), kind=FileKind.TEXT, name=DEFAULT_INPUT.name
    )

    assert len(split_clauses(document)) == 65


def test_missing_file_exits_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "missing.txt"

    assert main(["--input", str(missing)]) == 3

    captured = capsys.readouterr()
    assert "cannot read" in captured.err
    assert captured.out == ""


def test_not_utf8_exits_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "not-utf8.txt"
    path.write_bytes(b"caf\xe9")

    assert main(["--input", str(path)]) == 3

    assert capsys.readouterr().err == "clause_tracer.ingest: not_utf8\n"


def test_empty_file_exits_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")

    assert main(["--input", str(path)]) == 3

    assert capsys.readouterr().err == "clause_tracer.ingest: empty_input\n"
