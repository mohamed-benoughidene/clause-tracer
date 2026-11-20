"""The links clause fixture against ingest (S3-M1-T4)."""

from collections.abc import Callable
from pathlib import Path

from clause_tracer.core import FileKind
from clause_tracer.ingest import read_text_file, split_clauses
from clause_tracer.links import dump_clause_fixture, load_clause_fixture

SAMPLE_TEXT = (
    Path(__file__).parent.parent
    / "src"
    / "clause_tracer"
    / "ingest"
    / "samples"
    / "developer-agreement.txt"
)
FIXTURE = (
    Path(__file__).parent.parent
    / "src"
    / "clause_tracer"
    / "links"
    / "samples"
    / "developer-agreement.clauses.json"
)


def test_fixture_matches_ingest(check_golden: Callable[[Path, str], None]) -> None:
    data = SAMPLE_TEXT.read_bytes()
    document = read_text_file(data, kind=FileKind.TEXT, name="developer-agreement.txt")

    check_golden(FIXTURE, dump_clause_fixture(document, split_clauses(document)))


def test_fixture_loads_to_65_clauses() -> None:
    sample = load_clause_fixture(FIXTURE.read_text(encoding="utf-8"))

    assert len(sample.clauses) == 65
    assert sample.clauses[-1].id == "S1.2"
