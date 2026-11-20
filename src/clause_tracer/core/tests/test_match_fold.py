"""The wide match fold, with its index map (S2-M5-T2, question 2)."""

from collections.abc import Mapping

import pytest
from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import MatchKey, fold_for_matching
from clause_tracer.core.tests.owner_tables import TABLES_DIR, as_str, load_table
from clause_tracer.core.tests.strategies import hazard_text

TABLE = TABLES_DIR / "match_fold.toml"
CASE_KEYS: frozenset[str] = frozenset({"id", "text", "expected"})
REQUIRED: frozenset[str] = frozenset({"id", "text", "expected"})

_TABLE = load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED)
_ROWS: list[Mapping[str, object]] = list(_TABLE.cases)
_IDS = [str(row["id"]) for row in _ROWS]


def test_sharp_s_becomes_two_letters() -> None:
    key = fold_for_matching("Straße")

    assert key.text == "strasse"
    assert key.to_canonical == (0, 1, 2, 3, 4, 4, 5, 6)


def test_ligature_is_two_letters_from_one() -> None:
    key = fold_for_matching("ﬁne")

    assert key.text == "fine"
    assert key.to_canonical == (0, 0, 1, 2, 3)


def test_soft_hyphen_is_dropped() -> None:
    key = fold_for_matching("A\u00adB")

    assert key.text == "ab"
    assert key.to_canonical == (0, 2, 3)


def test_quotes_and_spaces() -> None:
    assert fold_for_matching("“Hi”  \n there").text == '"hi" there'


def test_empty_text() -> None:
    assert fold_for_matching("") == MatchKey(text="", to_canonical=(0,))


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_match_fold_table(row: Mapping[str, object]) -> None:
    text = as_str(row["text"], f"case {row['id']} text")
    expected = as_str(row["expected"], f"case {row['id']} expected")

    assert fold_for_matching(text).text == expected


def test_match_fold_table_has_rows() -> None:
    assert len(_ROWS) >= 9


@given(text=hazard_text())
def test_map_shape(text: str) -> None:
    key = fold_for_matching(text)

    assert len(key.to_canonical) == len(key.text) + 1
    assert all(
        earlier <= later
        for earlier, later in zip(key.to_canonical, key.to_canonical[1:], strict=False)
    )
    assert key.to_canonical[-1] == len(text)
    assert all(index < len(text) for index in key.to_canonical[:-1])


def _first_at_or_after(to_canonical: tuple[int, ...], index: int) -> int:
    """The first folded position whose source index is at or after `index`."""

    for position, source in enumerate(to_canonical):
        if source >= index:
            return position
    return len(to_canonical) - 1


@given(
    text=hazard_text(),
    first=st.integers(min_value=0, max_value=1000),
    second=st.integers(min_value=0, max_value=1000),
)
def test_invariant_2_folding_a_slice_equals_slicing_the_fold(
    text: str,
    first: int,
    second: int,
) -> None:
    start = first % (len(text) + 1)
    end = second % (len(text) + 1)
    if start > end:
        start, end = end, start

    key = fold_for_matching(text)
    start_folded = _first_at_or_after(key.to_canonical, start)
    end_folded = _first_at_or_after(key.to_canonical, end)

    assert fold_for_matching(text[start:end]).text.strip(" ") == (
        key.text[start_folded:end_folded].strip(" ")
    )
