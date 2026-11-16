"""The ports of the engine (system design 3.1 and 3.4).

The five ports are typing.Protocol classes (P4). Adapters are passed in,
never imported (B3, T2). CancelCheck is a stage 1 shape (ADR 0005).
"""

from collections.abc import Callable
from datetime import datetime
from typing import Protocol

from clause_tracer.core.ai import AiRecord, AiReply, AiRequest
from clause_tracer.core.ids import ReviewId
from clause_tracer.core.placeholders import PiiSuggestion

# Returns True once the user has cancelled.
CancelCheck = Callable[[], bool]


class AiClient(Protocol):
    """One call to the AI service, so no provider SDK reaches the rules."""

    def complete(self, request: AiRequest) -> AiReply:
        """Send one AI call and return its exact reply.

        Input: the AiRequest of one call, the accepted form (section 6.3).
        Output: the exact AiReply, saved before anything parses it (D8).
        Raises: a model-service error. Network retries live in the adapter; the one
            reask lives in the step (ADR 0005).
        Side effects: a paid AI call, recorded as an AiRecord by the caller.
        """
        ...


class PiiDetector(Protocol):
    """Finds personal data, behind the code finders (ADR 0008)."""

    def find(self, text: str) -> tuple[PiiSuggestion, ...]:
        """Find personal data in one text.

        Input: the text to scan.
        Output: every suggestion found, as a tuple of PiiSuggestion.
        Raises: None.
        Side effects: None. Sits behind the code finders (ADR 0008).
        """
        ...


class ReviewStore(Protocol):
    """The encrypted store of raw AI records (ADR 0006)."""

    def save_record(self, record: AiRecord) -> None:
        """Append one AI record.

        Input: one AiRecord, raw and append-only (D1).
        Output: None.
        Raises: DuplicateRecordError when a saved record already holds that
            record_id (append-only, D1).
        Side effects: the record is stored, encrypted (ADR 0006).
        """
        ...

    def load_records(self, review_id: ReviewId) -> tuple[AiRecord, ...]:
        """Load one review's records.

        Input: the review id.
        Output: the review's records in the order saved, or () when it holds none.
        Raises: None.
        Side effects: None. Hides the encrypted store (ADR 0006).
        """
        ...

    def list_reviews(self) -> tuple[ReviewId, ...]:
        """List the reviews that hold at least one record.

        Input: None.
        Output: the ids of those reviews, sorted.
        Raises: None.
        Side effects: None.
        """
        ...

    def delete_review(self, review_id: ReviewId) -> None:
        """Remove one review and its records.

        Input: the review id to remove.
        Output: None.
        Raises: None.
        Side effects: the review and its records are removed; a missing review
            does nothing (I8).
        """
        ...

    def purge_expired(self, now: datetime, auto_delete_days: int) -> tuple[ReviewId, ...]:
        """Delete every review that is due under the auto-delete rules.

        Input: the time now, and the auto-delete setting in days.
        Output: the ids of the reviews deleted, sorted.
        Raises: None.
        Side effects: the due reviews and their records are removed. Until stage 6
            adds user state, a review's last change is the latest finished_at of
            its records (system design 3.4).
        """
        ...


class SecretStore(Protocol):
    """Stores API keys, encrypted, under a provider id (ADR 0006, ADR 0015)."""

    def get_secret(self, provider_id: str) -> str | None:
        """Read one stored secret.

        Input: the provider id the secret is stored under (ADR 0015).
        Output: the secret, or None when nothing is stored.
        Raises: SecretStoreUnavailableError when the store cannot be reached.
        Side effects: None. The secret never sits in plain text (ADR 0006).
        """
        ...

    def put_secret(self, provider_id: str, secret: str) -> None:
        """Store one secret under a provider id.

        Input: the provider id, and the secret to store.
        Output: None.
        Raises: SecretStoreUnavailableError when the store cannot be reached.
        Side effects: the stored secret is replaced, encrypted (ADR 0006, ADR 0015).
        """
        ...

    def delete_secret(self, provider_id: str) -> None:
        """Remove one stored secret.

        Input: the provider id.
        Output: None.
        Raises: SecretStoreUnavailableError when the store cannot be reached.
        Side effects: the stored secret is removed; a missing id does nothing (I8).
        """
        ...


class Clock(Protocol):
    """The only source of the current time, so time stays testable (T2)."""

    def now(self) -> datetime:
        """Return the current time.

        Input: None.
        Output: a timezone-aware datetime.
        Raises: None.
        Side effects: None. Auto-delete, timestamps and retry pauses stay
            testable (T2).
        """
        ...
