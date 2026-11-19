"""Tests for sentence starts from NUPunkt (S2-M3-T4)."""

from pathlib import Path

from hypothesis import given

from clause_tracer.core.tests.strategies import hazard_text
from clause_tracer.ingest._sentences import sentence_starts

PACKAGE = Path(__file__).parents[2]


def test_starts_of_three_sentences() -> None:
    text = (
        "Invoices are paid within 60 days. Interest runs at 4% p.a. "
        "from the due date. See cl. 5 below."
    )

    assert sentence_starts(text) == (0, 34, 78)


def test_empty_text() -> None:
    assert sentence_starts("") == ()


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
