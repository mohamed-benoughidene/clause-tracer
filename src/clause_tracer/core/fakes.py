"""Fakes of the five ports (system design 3.4, decided 14 Nov 2026).

Standard library and core only, exported from core. Tests use them, and
so does every module's run-alone command. Every real adapter must later
pass the same contract suite in tests/contracts/ (ADR 0013, T12).
"""

from collections.abc import Mapping

from clause_tracer.core.ai import AiReply, AiRequest
from clause_tracer.core.errors import ModelServiceError
from clause_tracer.core.request_hash import request_sha256


class UnrecordedRequest(AssertionError):
    """The replay fake was asked for a request it does not know.

    It is a test failure, not a project error, so code under test that
    catches ClauseTracerError cannot swallow it.
    """


class ReplayAiClient:
    """An AiClient fake that replays recorded replies, keyed by request hash."""

    def __init__(self, recordings: Mapping[str, AiReply]) -> None:
        self._recordings: dict[str, AiReply] = dict(recordings)
        self._used: set[str] = set()
        self._pending_failure: type[ModelServiceError] | None = None

    def complete(self, request: AiRequest) -> AiReply:
        """Return the recorded reply for this exact request."""

        if self._pending_failure is not None:
            error_type = self._pending_failure
            self._pending_failure = None
            raise error_type({"step": request.step})
        key = request_sha256(request)
        if key not in self._recordings:
            raise UnrecordedRequest(f"unrecorded request: step={request.step} sha256={key}")
        self._used.add(key)
        return self._recordings[key]

    def unused_keys(self) -> tuple[str, ...]:
        """Return the sorted keys never asked for."""

        return tuple(sorted(set(self._recordings) - self._used))

    def fail_next(self, error_type: type[ModelServiceError]) -> None:
        """Make the next complete call raise this model-service error, once."""

        self._pending_failure = error_type


def assert_all_used(client: ReplayAiClient) -> None:
    """Fail the test when any recording was never asked for."""

    unused = client.unused_keys()
    if unused:
        raise AssertionError(f"unused recordings: {unused}")
