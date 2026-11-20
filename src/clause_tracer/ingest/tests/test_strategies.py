"""Tests for the ingest test strategies (S2-M3-T11)."""

import pytest

from clause_tracer.ingest.tests.strategies import is_usable_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("\ufeff", False),
        ("  \n", False),
        ("", False),
        ("a", True),
        ("\ufeff1. Start", True),
    ],
)
def test_is_usable_text(text: str, expected: bool) -> None:
    assert is_usable_text(text) is expected
