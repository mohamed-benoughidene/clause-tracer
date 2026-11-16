"""The detector, secret store and clock fakes (S1-M4-T4)."""

from datetime import UTC, datetime, timedelta

import pytest

from clause_tracer.core import Clock, FixedClock, InMemorySecretStore, PiiDetector, SecretStore
from clause_tracer.core.enums import PiiSource, PlaceholderKind
from clause_tracer.core.fakes import FakePiiDetector
from clause_tracer.core.placeholders import PiiSuggestion
from clause_tracer.core.wording import Span

NOW = datetime(2026, 11, 16, 9, 0, 0, tzinfo=UTC)


def _suggestion() -> PiiSuggestion:
    return PiiSuggestion(
        span=Span(start=5, end=9),
        kind=PlaceholderKind.PERSON,
        source=PiiSource.NER,
    )


def test_detector_returns_planted_suggestions() -> None:
    planted = _suggestion()
    detector = FakePiiDetector({"John Smith signs here.": (planted,)})
    assert detector.find("John Smith signs here.") == (planted,)


def test_detector_returns_nothing_for_other_text() -> None:
    detector = FakePiiDetector({"John Smith signs here.": (_suggestion(),)})
    assert detector.find("Nothing planted here.") == ()


def test_clock_returns_its_time() -> None:
    clock = FixedClock(NOW)
    assert clock.now() == NOW


def test_clock_moves_forward_and_back() -> None:
    clock = FixedClock(NOW)
    clock.advance(timedelta(days=3))
    assert clock.now() == datetime(2026, 11, 19, 9, 0, 0, tzinfo=UTC)
    clock.advance(timedelta(hours=-6))
    assert clock.now() == datetime(2026, 11, 19, 3, 0, 0, tzinfo=UTC)
    clock.set(NOW)
    assert clock.now() == NOW


def test_clock_rejects_naive_datetime() -> None:
    naive = datetime(2026, 11, 16, 9, 0, 0)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        FixedClock(naive)
    clock = FixedClock(NOW)
    with pytest.raises(ValueError, match="datetime must be timezone-aware"):
        clock.set(naive)


def test_fakes_satisfy_their_ports() -> None:
    # mypy strict checks these assignments against the ports.
    detector: PiiDetector = FakePiiDetector({})
    secrets: SecretStore = InMemorySecretStore()
    clock: Clock = FixedClock(NOW)
    assert detector is not None
    assert secrets is not None
    assert clock is not None
