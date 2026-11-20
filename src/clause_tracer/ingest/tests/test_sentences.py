"""Tests for sentence starts from NUPunkt and colon lines (S2-M3-T4, S2-M4-T7)."""

from pathlib import Path

import pytest
from hypothesis import given

from clause_tracer.core.tests.strategies import hazard_text
from clause_tracer.ingest._sentences import colon_line_starts, sentence_starts, tab_line_starts

PACKAGE = Path(__file__).parents[2]


def test_starts_of_three_sentences() -> None:
    text = (
        "Invoices are paid within 60 days. Interest runs at 4% p.a. "
        "from the due date. See cl. 5 below."
    )

    assert sentence_starts(text) == (0, 34, 78)


def test_empty_text() -> None:
    assert sentence_starts("") == ()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Meanings:\nCharges means fees.", (10,)),
        ("Meanings: \t\nCharges.", (12,)),
        ("Meanings\uff1a\nNext", (10,)),
        ("Meanings:\r\nNext", (11,)),
        ("Meanings:\u00a0\nNext", (11,)),
        ("**Terms:**\nNext", (11,)),
        ("Meanings:\n\nNext", ()),
        ("Meanings:\n", ()),
        ("Note: this\nstays", ()),
    ],
)
def test_colon_line_starts(text: str, expected: tuple[int, ...]) -> None:
    assert colon_line_starts(text) == expected


def test_colon_line_is_a_sentence_start() -> None:
    text = (
        "In this Agreement the following words have these meanings:\n"
        '"Charges" means the fees set out in Schedule 1.'
    )

    assert sentence_starts(text) == (0, 59)


def test_colon_start_joins_the_library_starts() -> None:
    assert sentence_starts("One. Two:\nThree.") == (0, 5, 10)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Intro.\nA\tB\nC\tD\nAfter", (7, 11)),
        ("A\tB\nC", ()),
        ("A\tB\n\nC", ()),
        ("No tabs\nhere", ()),
        ("A\tB", ()),
        ("Intro.\n\tTotal\t£9,600", (7,)),
        ("Intro\n\tindented line", ()),
        ("Intro\ntrailing\t", ()),
    ],
)
def test_tab_line_starts(text: str, expected: tuple[int, ...]) -> None:
    assert tab_line_starts(text) == expected


def test_tab_lines_join_the_other_starts() -> None:
    text = (
        "The Developer will build the site.\n"
        "Milestone\tWork\tCharges\n"
        "1 Discovery\tReview designs\t£1,600"
    )

    assert sentence_starts(text) == (0, 35, 58)


def test_only_this_file_imports_nupunkt() -> None:
    allowed = {
        PACKAGE / "ingest" / "_sentences.py",
        *(PACKAGE / "ingest" / "tests").glob("*.py"),
    }

    for path in PACKAGE.rglob("*.py"):
        if path in allowed:
            continue
        assert "nupunkt" not in path.read_text(encoding="utf-8"), path


@given(text=hazard_text())
def test_starts_are_strictly_increasing_and_inside_the_text(text: str) -> None:
    starts = sentence_starts(text)

    for start in starts:
        assert 0 <= start < len(text)
    for earlier, later in zip(starts, starts[1:], strict=False):
        assert earlier < later
