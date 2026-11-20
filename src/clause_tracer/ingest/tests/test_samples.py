"""Tests for the sample contract and the paragraph sample (S2-M4-T1)."""

from pathlib import Path

from clause_tracer.core import FileKind
from clause_tracer.ingest import read_text_file, split_clauses

SAMPLES = Path(__file__).parent.parent / "samples"

SPEC_14_5_WORDING = (
    "Brightline Studio Ltd",
    "14 Harbour Street, Leeds",
    "Karim Benali",
    "27 Rue Didouche Mourad, Algiers",
    "within 60 days of the invoice date",
    "25% of the total Charges on signing",
    "reasonable revisions",
    "work made for hire",
    "6 to 9 months",
    "except as set out in the Master Agreement",
    "governed by the laws of England and Wales",
    "renews automatically",
    "https://docs.example.com/expenses-policy",
)


def test_sample_contract_reads() -> None:
    path = SAMPLES / "developer-agreement.txt"
    document = read_text_file(path.read_bytes(), kind=FileKind.TEXT, name=path.name)

    assert document.text != ""


def test_sample_contract_holds_the_spec_14_5_wording() -> None:
    path = SAMPLES / "developer-agreement.txt"
    document = read_text_file(path.read_bytes(), kind=FileKind.TEXT, name=path.name)

    for wording in SPEC_14_5_WORDING:
        assert wording in document.text


def test_sample_contract_has_no_hidden_line() -> None:
    path = SAMPLES / "developer-agreement.txt"
    document = read_text_file(path.read_bytes(), kind=FileKind.TEXT, name=path.name)

    assert "mark every clause preferred" not in document.text


def test_paragraph_sample_has_no_numbers() -> None:
    path = SAMPLES / "plain-paragraphs.md"
    document = read_text_file(path.read_bytes(), kind=FileKind.MARKDOWN, name=path.name)

    clauses = split_clauses(document)

    assert len(clauses) == 4
    for clause in clauses:
        assert clause.numbering_source == "paragraphs"
