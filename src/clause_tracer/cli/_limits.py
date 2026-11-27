"""The memory limit the child sets on itself (S5-M2-T6).

A failure stops the child: the limit is never skipped (fail closed).
"""

import sys

from clause_tracer.cli import _limits_windows


def apply_limits(memory_bytes: int) -> None:
    """Set the child's memory limit on this system."""
    if sys.platform.startswith("linux"):
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        return

    if sys.platform == "win32":
        _limits_windows.limit_committed_memory(memory_bytes)
        return

    raise OSError("cli: no memory limit on this system")
