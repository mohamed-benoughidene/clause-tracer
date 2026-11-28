"""The runner when a name, a child or a read is unusual (S5-M2-T12)."""

import errno
import subprocess
import threading
from collections.abc import Callable
from typing import Any

import pytest

from clause_tracer.cli.child_runner import read_file_in_child
from clause_tracer.core import InputError

_TEXT = b"Hello world.\n"


def _keep(
    monkeypatch: pytest.MonkeyPatch, tweak: Callable[[subprocess.Popen[Any]], None]
) -> list[subprocess.Popen[Any]]:
    """Keep each child the runner starts, after `tweak` has changed it."""
    started: list[subprocess.Popen[Any]] = []
    real_popen = subprocess.Popen

    def start(*args: Any, **kwargs: Any) -> subprocess.Popen[Any]:
        process = real_popen(*args, **kwargs)
        tweak(process)
        started.append(process)
        return process

    monkeypatch.setattr(subprocess, "Popen", start)
    return started


@pytest.mark.parametrize("name", ["-draft.txt", "--x.txt", ""])
def test_any_file_name_reaches_the_child(name: str) -> None:
    assert read_file_in_child(_TEXT, name=name).source.name == name


def test_child_is_killed_when_the_read_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def break_read(process: subprocess.Popen[Any]) -> None:
        def read(*args: object) -> bytes:
            raise RuntimeError("read failed")

        monkeypatch.setattr(process.stdout, "read", read)

    started = _keep(monkeypatch, break_read)

    with pytest.raises(RuntimeError):
        read_file_in_child(_TEXT, name="a.txt")

    assert started[0].poll() is not None


def test_closed_pipe_error_of_windows_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    def break_write(process: subprocess.Popen[Any]) -> None:
        assert process.stdin is not None
        close = process.stdin.close

        def write(data: bytes) -> int:
            close()
            raise OSError(errno.EINVAL, "closed pipe")

        monkeypatch.setattr(process.stdin, "write", write)

    _keep(monkeypatch, break_write)
    uncaught: list[object] = []
    monkeypatch.setattr(threading, "excepthook", uncaught.append)
    before = set(threading.enumerate())

    with pytest.raises(InputError) as raised:
        read_file_in_child(_TEXT, name="a.txt")
    for thread in set(threading.enumerate()) - before:
        thread.join(timeout=5)

    assert raised.value.code == "empty_input"
    assert uncaught == []


def test_a_timer_that_fires_late_keeps_the_result(monkeypatch: pytest.MonkeyPatch) -> None:
    class LateTimer:
        def __init__(self, interval: float, function: Callable[[], None]) -> None:
            self._function = function

        def start(self) -> None:
            pass

        def cancel(self) -> None:
            self._function()

    monkeypatch.setattr(threading, "Timer", LateTimer)

    assert read_file_in_child(_TEXT, name="a.txt").text == "Hello world.\n"
