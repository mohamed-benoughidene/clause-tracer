"""The privacy fixture against ingest and links (S4-M1-T4)."""

from collections.abc import Callable
from pathlib import Path

from clause_tracer.core import FakePiiDetector, FileKind, Party
from clause_tracer.ingest import read_text_file, split_clauses
from clause_tracer.links import map_links
from clause_tracer.privacy import (
    PrivacyInput,
    anonymise,
    dump_privacy_fixture,
    find_personal_data,
    group_entities,
    load_privacy_fixture,
    render_privacy_report,
    restore_text,
)
from clause_tracer.privacy._spans import overlaps

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
GOLDEN = (
    Path(__file__).parent.parent
    / "src"
    / "clause_tracer"
    / "privacy"
    / "tests"
    / "goldens"
    / "developer-agreement.privacy.txt"
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


def test_text_to_placeholder_text() -> None:
    document = read_text_file(
        SAMPLE_TEXT.read_bytes(), kind=FileKind.TEXT, name="developer-agreement.txt"
    )
    clauses = split_clauses(document)
    link_map = map_links(document, clauses)
    case = PrivacyInput(
        document=document,
        clauses=clauses,
        parties=PARTIES,
        terms=link_map.terms,
    )
    entities = group_entities(document, find_personal_data(case, FakePiiDetector({})))
    placeholder = anonymise(document, entities)

    assert restore_text(placeholder, document) == document.text

    entity_spans = [span for entity in entities for span in entity.spans]
    for term in link_map.terms:
        for use in term.uses:
            assert not any(overlaps(use, entity_span) for entity_span in entity_spans), term.term

    assert render_privacy_report(case, entities, placeholder) == GOLDEN.read_text(encoding="utf-8")
