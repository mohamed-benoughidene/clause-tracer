import tomllib
from pathlib import Path

import pytest

from clause_tracer.core.__main__ import main

OWNER_TABLE = Path(__file__).parent / "tables" / "spec_14_5.toml"


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_main_prints_one_line_per_position(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    lines = capsys.readouterr().out.splitlines()
    with OWNER_TABLE.open("rb") as file:
        rows = tomllib.load(file)["case"]
    assert len(lines) == 11
    assert len(rows) == 11
    for line, row in zip(lines, rows, strict=True):
        columns = line.split("\t")
        assert len(columns) == 5
        assert columns[0] == row["position"]
        assert columns[2] == row["level"]


def test_missing_input_returns_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "missing.toml"
    assert main(["--input", str(path)]) == 3
    assert f"clause_tracer.core: cannot read {path}" in capsys.readouterr().err


def test_bad_input_returns_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.toml"
    path.write_text("x = ", encoding="utf-8")
    assert main(["--input", str(path)]) == 3
    assert capsys.readouterr().err.startswith("clause_tracer.core: ")
