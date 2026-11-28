"""The limits the child process sets on itself (S5-M2-T1)."""

from clause_tracer.cli.child_limits import CHILD_MEMORY_BYTES, CHILD_TIMEOUT_S


def test_child_limits() -> None:
    assert CHILD_TIMEOUT_S == 60.0
    assert CHILD_MEMORY_BYTES == 1_073_741_824
