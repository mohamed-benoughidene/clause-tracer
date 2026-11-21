"""One Hypothesis profile for the whole repo (S3-M5-T15)."""

from hypothesis import settings


def test_deadline_is_off() -> None:
    assert settings().deadline is None
