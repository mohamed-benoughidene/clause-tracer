"""Placeholder tokens and escapes (S4-M4-T1)."""

import re

import pytest

from clause_tracer.core import PLACEHOLDER_CLOSE, PLACEHOLDER_OPEN, PlaceholderKind
from clause_tracer.privacy._tokens import ESCAPES, LABELS, placeholder_token


def test_person_token() -> None:
    assert placeholder_token(PlaceholderKind.PERSON, 1) == "⟦Person 1⟧"


def test_id_token() -> None:
    assert placeholder_token(PlaceholderKind.ID, 12) == "⟦ID 12⟧"


def test_number_zero_raises() -> None:
    with pytest.raises(ValueError, match="privacy: a placeholder number starts at 1"):
        placeholder_token(PlaceholderKind.PERSON, 0)


def test_every_kind_has_a_label() -> None:
    assert set(LABELS) == set(PlaceholderKind)


def test_token_is_one_marker_group() -> None:
    pattern = (
        re.escape(PLACEHOLDER_OPEN)
        + "[^"
        + re.escape(PLACEHOLDER_CLOSE)
        + "]*"
        + re.escape(PLACEHOLDER_CLOSE)
    )
    for kind in PlaceholderKind:
        assert re.fullmatch(pattern, placeholder_token(kind, 3))


def test_escapes() -> None:
    assert ESCAPES == {"⟦": "[", "⟧": "]"}
