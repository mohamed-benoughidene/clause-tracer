"""The privacy fixture against ingest and links (S4-M1-T4)."""

from collections.abc import Callable
from pathlib import Path

from clause_tracer.core import FileKind, Party
from clause_tracer.ingest import read_text_file, split_clauses
from clause_tracer.links import map_links
from clause_tracer.privacy import (
    PrivacyInput,
    dump_privacy_fixture,
    load_privacy_fixture,
)

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
    / "privacy"
    / "samples"
    / "developer-agreement.privacy.json"
)

PARTIES: tuple[Party, ...] = (
    Party(
        name="Brightline Studio Ltd",
        address="14 Harbour Street, Leeds LS1 4AB",
        yours=False,
    ),
    Party(
        name="Karim Benali",
        address="27 Rue Didouche Mourad, Algiers 16000, Algeria",
        yours=True,
    ),
)


def test_fixture_matches_ingest_and_links(check_golden: Callable[[Path, str], None]) -> None:
    document = read_text_file(
        SAMPLE_TEXT.read_bytes(), kind=FileKind.TEXT, name="developer-agreement.txt"
    )
    clauses = split_clauses(document)
    terms = map_links(document, clauses).terms

    check_golden(
        FIXTURE,
        dump_privacy_fixture(
            PrivacyInput(document=document, clauses=clauses, parties=PARTIES, terms=terms)
        ),
    )


def test_fixture_loads() -> None:
    sample = load_privacy_fixture(FIXTURE.read_text(encoding="utf-8"))

    assert len(sample.clauses) == 65
    assert sample.clauses[-1].id == "S1.2"
    assert len(sample.parties) == 2
    assert len(sample.terms) == 7
    assert sample.terms[0].term == "Agency"
