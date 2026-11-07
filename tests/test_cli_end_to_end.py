import subprocess
import sys

from clause_tracer import __version__


def test_cli_version_via_subprocess() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "clause_tracer.cli", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert __version__ in result.stdout
