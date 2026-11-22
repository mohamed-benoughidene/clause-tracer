"""Run the privacy module alone (S4-M5-T2)."""

from pathlib import Path

import pytest

from clause_tracer.privacy.__main__ import main
from clause_tracer.privacy.sample_input import dump_privacy_fixture
from clause_tracer.privacy.tests.case_builder import make_case


def test_main_prints_the_sample_report(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0

    captured = capsys.readouterr()
    assert captured.out.startswith("source\tdeveloper-agreement.txt\t6204\n")
    assert captured.err == ""


def test_main_reads_another_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "case.json"
    path.write_text(dump_privacy_fixture(make_case(["Hi Sam."])), encoding="utf-8")

    assert main(["--input", str(path)]) == 0

    assert capsys.readouterr().out.startswith("source\tcase.txt\t7")


def test_a_missing_file_returns_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--input", str(tmp_path / "none.json")]) == 3

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("clause_tracer.privacy: cannot read")


def test_a_bad_fixture_returns_3(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{", encoding="utf-8")

    assert main(["--input", str(path)]) == 3

    assert capsys.readouterr().err == "clause_tracer.privacy: privacy sample: not JSON\n"


def test_a_file_that_is_not_utf8_returns_3(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "latin.json"
    path.write_bytes(b"\xff\xfe\x00")

    assert main(["--input", str(path)]) == 3

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("clause_tracer.privacy: cannot read")
