"""The ports of the engine (system design 3.1 and 3.4).

The five ports are typing.Protocol classes (P4). Adapters are passed in,
never imported (B3, T2). CancelCheck is a stage 1 shape (ADR 0005).
"""

from collections.abc import Callable

# Returns True once the user has cancelled.
CancelCheck = Callable[[], bool]
