"""The memory limit the child sets on itself (S5-M2-T6)."""

import subprocess
import sys

import pytest

from clause_tracer.cli._limits import apply_limits

LINUX_ONLY = pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="RLIMIT_AS is on Linux"
)


def test_limits_unknown_system(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")

    with pytest.raises(OSError):
        apply_limits(1024)


@LINUX_ONLY
def test_limits_linux_sets_rlimit_as() -> None:
    code = (
        "import resource\n"
        "from clause_tracer.cli._limits import apply_limits\n"
        "apply_limits(1024 * 1024 * 1024)\n"
        "print(resource.getrlimit(resource.RLIMIT_AS))\n"
    )

    result = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "(1073741824, 1073741824)"
