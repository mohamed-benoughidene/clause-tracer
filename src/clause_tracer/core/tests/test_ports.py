"""The ports match system design 3.4 exactly, and stubs satisfy them (S1-M4-T1)."""

from datetime import datetime

from clause_tracer.core import (
    AiClient,
    AiRecord,
    AiReply,
    AiRequest,
    Clock,
    PiiDetector,
    PiiSuggestion,
    ReviewStore,
    SecretStore,
)
from clause_tracer.core.ids import ReviewId

PORT_METHODS: dict[type, frozenset[str]] = {
    AiClient: frozenset({"complete"}),
    PiiDetector: frozenset({"find"}),
    ReviewStore: frozenset(
        {"save_record", "load_records", "list_reviews", "delete_review", "purge_expired"}
    ),
    SecretStore: frozenset({"get_secret", "put_secret", "delete_secret"}),
    Clock: frozenset({"now"}),
}


def test_ports_have_exactly_the_system_design_methods() -> None:
    for port, expected in PORT_METHODS.items():
        names = {name for name in port.__dict__ if not name.startswith("_")}
        assert names == expected, f"{port.__name__} holds {sorted(names)}"


class _StubAiClient:
    def complete(self, request: AiRequest) -> AiReply:
        raise NotImplementedError


class _StubPiiDetector:
    def find(self, text: str) -> tuple[PiiSuggestion, ...]:
        raise NotImplementedError


class _StubReviewStore:
    def save_record(self, record: AiRecord) -> None:
        raise NotImplementedError

    def load_records(self, review_id: ReviewId) -> tuple[AiRecord, ...]:
        raise NotImplementedError

    def list_reviews(self) -> tuple[ReviewId, ...]:
        raise NotImplementedError

    def delete_review(self, review_id: ReviewId) -> None:
        raise NotImplementedError

    def purge_expired(self, now: datetime, auto_delete_days: int) -> tuple[ReviewId, ...]:
        raise NotImplementedError


class _StubSecretStore:
    def get_secret(self, provider_id: str) -> str | None:
        raise NotImplementedError

    def put_secret(self, provider_id: str, secret: str) -> None:
        raise NotImplementedError

    def delete_secret(self, provider_id: str) -> None:
        raise NotImplementedError


class _StubClock:
    def now(self) -> datetime:
        raise NotImplementedError


def test_stubs_satisfy_the_ports() -> None:
    # mypy strict checks these assignments against the port types.
    client: AiClient = _StubAiClient()
    detector: PiiDetector = _StubPiiDetector()
    store: ReviewStore = _StubReviewStore()
    secrets: SecretStore = _StubSecretStore()
    clock: Clock = _StubClock()
    assert client is not None
    assert detector is not None
    assert store is not None
    assert secrets is not None
    assert clock is not None
