"""Fakes of the five ports (system design 3.4, decided 14 Nov 2026).

Standard library and core only, exported from core. Tests use them, and
so does every module's run-alone command. Every real adapter must later
pass the same contract suite in tests/contracts/ (ADR 0013, T12).
"""

from collections.abc import Mapping
from datetime import datetime, timedelta

from clause_tracer.core.ai import AiRecord, AiReply, AiRequest
from clause_tracer.core.auto_delete import is_due
from clause_tracer.core.errors import (
    DuplicateRecordError,
    ModelServiceError,
    SecretStoreUnavailableError,
)
from clause_tracer.core.ids import RecordId, ReviewId
from clause_tracer.core.placeholders import PiiSuggestion
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


class FakePiiDetector:
    """A PiiDetector fake that returns planted suggestions, keyed by text."""

    def __init__(self, planted: Mapping[str, tuple[PiiSuggestion, ...]]) -> None:
        self._planted: dict[str, tuple[PiiSuggestion, ...]] = dict(planted)

    def find(self, text: str) -> tuple[PiiSuggestion, ...]:
        """Return the suggestions planted for this text, or ()."""

        return self._planted.get(text, ())


class InMemorySecretStore:
    """A SecretStore fake that keeps secrets in a dict."""

    def __init__(self, *, available: bool = True) -> None:
        self._available = available
        self._secrets: dict[str, str] = {}

    def set_available(self, available: bool) -> None:
        """Make the store available or unavailable, to test the error path."""

        self._available = available

    def get_secret(self, provider_id: str) -> str | None:
        """Return the stored secret, or None when nothing is stored."""

        self._raise_when_unavailable(provider_id)
        return self._secrets.get(provider_id)

    def put_secret(self, provider_id: str, secret: str) -> None:
        """Store the secret under the provider id, replacing any stored one."""

        self._raise_when_unavailable(provider_id)
        self._secrets[provider_id] = secret

    def delete_secret(self, provider_id: str) -> None:
        """Remove the stored secret; a missing id does nothing (I8)."""

        self._raise_when_unavailable(provider_id)
        self._secrets.pop(provider_id, None)

    def _raise_when_unavailable(self, provider_id: str) -> None:
        if not self._available:
            raise SecretStoreUnavailableError({"provider_id": provider_id})


class InMemoryReviewStore:
    """A ReviewStore fake that keeps raw AI records in memory (stage 1 stand-in)."""

    def __init__(self) -> None:
        self._records: dict[ReviewId, list[AiRecord]] = {}
        self._record_ids: set[RecordId] = set()

    def save_record(self, record: AiRecord) -> None:
        """Append one AI record; the record id is taken across every review (D1)."""

        if record.record_id in self._record_ids:
            raise DuplicateRecordError({"record_id": record.record_id})
        self._record_ids.add(record.record_id)
        self._records.setdefault(record.review_id, []).append(record)

    def load_records(self, review_id: ReviewId) -> tuple[AiRecord, ...]:
        """Return the review's records in the order saved, or ()."""

        return tuple(self._records.get(review_id, ()))

    def list_reviews(self) -> tuple[ReviewId, ...]:
        """Return the sorted ids of reviews that hold at least one record."""

        return tuple(sorted(review for review, records in self._records.items() if records))

    def delete_review(self, review_id: ReviewId) -> None:
        """Remove the review and its records; a missing review does nothing (I8)."""

        for record in self._records.pop(review_id, []):
            self._record_ids.discard(record.record_id)

    def purge_expired(self, now: datetime, auto_delete_days: int) -> tuple[ReviewId, ...]:
        """Delete every review due under the auto-delete rules; return their ids, sorted.

        A review's last change is the latest finished_at of its records, the
        stage 1 stand-in (system design 3.4); stage 6 adds user state.
        """

        due = [
            review
            for review, records in self._records.items()
            if records
            and is_due(max(record.finished_at for record in records), auto_delete_days, now)
        ]
        for review in due:
            self.delete_review(review)
        return tuple(sorted(due))


class FixedClock:
    """A Clock fake that stands still until the test moves it."""

    def __init__(self, now: datetime) -> None:
        if now.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        self._now = now

    def now(self) -> datetime:
        """Return the fixed time."""

        return self._now

    def set(self, when: datetime) -> None:
        """Set the fixed time."""

        if when.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        self._now = when

    def advance(self, delta: timedelta) -> None:
        """Move the fixed time by delta; a negative delta moves it back."""

        self._now += delta
