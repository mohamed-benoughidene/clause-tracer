"""The time and memory limits the child process sets on itself (S5-M2-T1)."""

from typing import Final

CHILD_TIMEOUT_S: Final[float] = 60.0
# [Assumption] system design 8.4: tuned in testing.

CHILD_MEMORY_BYTES: Final[int] = 1024 * 1024 * 1024
# [Assumption] system design 8.4: tuned in testing.
