"""Run `links` alone (S3-M5-T4)."""

from pathlib import Path

import pytest

from clause_tracer.links import dump_clause_fixture
from clause_tracer.links.__main__ import main
from clause_tracer.links.tests.case_builder import build_case


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_default_run_prints_the_sample(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0

    lines = capsys.readouterr().out.split("\n")
    assert lines[0].startswith("source\tdeveloper-agreement.txt\t")
    assert any(line.startswith("outside\tMaster Agreement\t11.1\t") for line in lines)


def test_missing_file_exits_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "missing.json"

    assert main(["--input", str(missing)]) == 3

    captured = capsys.readouterr()
    assert "cannot read" in captured.err
    assert captured.out == ""


def test_bad_fixture_exits_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")

    assert main(["--input", str(broken)]) == 3

    assert capsys.readouterr().err == "clause_tracer.links: links sample: not JSON\n"


def test_not_utf8_exits_3(tmp_path: Path) -> None:
    not_utf8 = tmp_path / "not-utf8.json"
    not_utf8.write_bytes(b"caf\xe9")

    assert main(["--input", str(not_utf8)]) == 3


def test_input_option(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    case = build_case([{"id": "1", "sentences": ["1. Paid."]}])
    fixture = tmp_path / "case.json"
    fixture.write_text(
        dump_clause_fixture(case.document, case.clauses),
        encoding="utf-8",
    )

    assert main(["--input", str(fixture)]) == 0

    lines = capsys.readouterr().out.split("\n")
    assert lines[0] == f"source\tcase.txt\t{len(case.document.text)}"
