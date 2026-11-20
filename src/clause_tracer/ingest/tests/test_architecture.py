"""The module's public shape (S2-M5-T5)."""

from pathlib import Path

import clause_tracer.ingest

MODULE = Path(__file__).parent.parent


def test_public_names() -> None:
    assert set(clause_tracer.ingest.__all__) == {
        "DOCUMENT_SCHEMA_VERSION",
        "NUMBERING_NUMBERS",
        "NUMBERING_PARAGRAPHS",
        "WARNING_NOT_ENGLISH",
        "read_pasted_text",
        "read_text_file",
        "split_clauses",
    }


def test_readme_names_every_public_name() -> None:
    readme = (MODULE / "README.md").read_text(encoding="utf-8")

    for name in clause_tracer.ingest.__all__:
        assert name in readme, name


def test_module_has_its_parts() -> None:
    for name in ("README.md", "tests", "samples", "__main__.py"):
        assert (MODULE / name).exists(), name
