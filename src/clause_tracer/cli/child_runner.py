"""Start the child, give it the bytes and read its reply (S5-M2-T6).

The child is not a security sandbox: a parser exploit can lift a limit
that the process set on itself. It always bounds its time and its memory,
and it never uses a process pool, a fork or a shell.
"""

import subprocess
import sys
import threading
from dataclasses import dataclass

from clause_tracer.cli.child_limits import CHILD_MEMORY_BYTES, CHILD_TIMEOUT_S
from clause_tracer.cli.child_reply import (
    MAX_CHILD_REPLY_BYTES,
    ChildDone,
    decode_child_reply,
    input_error_for_code,
)
from clause_tracer.core import Document, UnreadableFileError


@dataclass(frozen=True, slots=True, kw_only=True)
class ChildLimits:
    """The time and memory the parent allows the child."""

    timeout_s: float = CHILD_TIMEOUT_S
    memory_bytes: int = CHILD_MEMORY_BYTES


def child_command(*, name: str, memory_bytes: int, frozen: bool | None = None) -> list[str]:
    """Return the command that starts the child."""
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))

    if frozen:
        return [
            sys.executable,
            "--read-child",
            "--memory-bytes",
            str(memory_bytes),
            f"--name={name}",
        ]

    return [
        sys.executable,
        "-I",
        "-m",
        "clause_tracer.cli._child",
        "--memory-bytes",
        str(memory_bytes),
        f"--name={name}",
    ]


def classify_child_outcome(*, returncode: int, stdout: bytes, timed_out: bool) -> Document:
    """Turn how the child ended into a document or a named error."""
    if timed_out:
        raise UnreadableFileError({"reason": "too_slow"})

    if returncode != 0:
        raise UnreadableFileError({"reason": "child_crashed", "exit_code": returncode})

    reply = decode_child_reply(stdout)
    if isinstance(reply, ChildDone):
        return reply.document

    raise input_error_for_code(reply.code, reply.context)


def read_file_in_child(data: bytes, *, name: str, limits: ChildLimits | None = None) -> Document:
    """Read one file in a child process with a time and a memory limit."""
    limits = limits or ChildLimits()
    command = child_command(name=name, memory_bytes=limits.memory_bytes)
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    def feed() -> None:
        assert process.stdin is not None
        try:
            process.stdin.write(data)
            process.stdin.close()
        except OSError:
            # The child ended early. Windows reports this as EINVAL, not BrokenPipeError.
            pass

    thread = threading.Thread(target=feed, daemon=True)
    thread.start()

    timer_fired = False

    def kill() -> None:
        nonlocal timer_fired
        timer_fired = True
        is_still_running = process.poll() is None
        if is_still_running:
            process.kill()

    timer = threading.Timer(limits.timeout_s, kill)
    timer.start()

    is_too_large = False
    try:
        assert process.stdout is not None
        reply = process.stdout.read(MAX_CHILD_REPLY_BYTES + 1)
        is_too_large = len(reply) > MAX_CHILD_REPLY_BYTES
        if is_too_large:
            process.kill()
        process.wait()
    finally:
        timer.cancel()
        is_left_running = process.poll() is None
        if is_left_running:
            process.kill()
            process.wait()

    if is_too_large:
        raise UnreadableFileError({"reason": "child_reply_too_large"})

    returncode = process.returncode
    assert returncode is not None
    # A timer that fired after the child ended well does not discard its reply.
    timed_out = timer_fired and returncode != 0
    return classify_child_outcome(returncode=returncode, stdout=reply, timed_out=timed_out)
