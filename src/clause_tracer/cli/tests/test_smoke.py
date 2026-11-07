import pytest

from clause_tracer import __version__
from clause_tracer.cli.__main__ import main


def test_no_arguments_prints_help_and_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage: clause-tracer" in capsys.readouterr().out


def test_version_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out
