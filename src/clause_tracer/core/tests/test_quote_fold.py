"""The Spec 2 quote-check fold (S1-M5-T4, ADR 0012 14 Nov amendment)."""

from hypothesis import example, given
from hypothesis import strategies as st

from clause_tracer.core import fold_for_quote_check


def test_curly_quotes_become_straight() -> None:
    fold = fold_for_quote_check("“a” ‘b’")
    assert fold.text == "\"a\" 'b'"


def test_whitespace_runs_collapse() -> None:
    fold = fold_for_quote_check("a \n\t b")
    assert fold.text == "a b"
    assert fold.to_original == (0, 1, 5, 6)


def test_empty_text() -> None:
    fold = fold_for_quote_check("")
    assert fold.text == ""
    assert fold.to_original == (0,)


@given(text=st.text())
@example(text="  ")
def test_map_shape(text: str) -> None:
    fold = fold_for_quote_check(text)
    # One entry per folded character (whitespace runs collapse to one
    # entry) plus the last entry, which is the original length.
    assert len(fold.to_original) == len(fold.text) + 1
    assert all(a < b for a, b in zip(fold.to_original, fold.to_original[1:], strict=False))
    assert fold.to_original[-1] == len(text)


@given(text=st.text())
def test_fold_is_idempotent(text: str) -> None:
    folded = fold_for_quote_check(text)
    assert fold_for_quote_check(folded.text).text == folded.text
