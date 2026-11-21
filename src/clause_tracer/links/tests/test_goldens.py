"""Golden-file test for the link map (S3-M5-T5)."""

from collections.abc import Callable
from pathlib import Path

from clause_tracer.links import load_clause_fixture, map_links, render_link_map
from clause_tracer.links.__main__ import DEFAULT_INPUT

GOLDENS = Path(__file__).parent / "goldens"


def test_link_map_matches_its_golden(check_golden: Callable[[Path, str], None]) -> None:
    sample = load_clause_fixture(DEFAULT_INPUT.read_text(encoding="utf-8"))

    actual = render_link_map(
        sample.document,
        sample.clauses,
        map_links(sample.document, sample.clauses),
    )

    check_golden(GOLDENS / "developer-agreement.links.txt", actual)
