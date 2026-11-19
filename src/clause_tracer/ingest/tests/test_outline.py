"""Tests for the outline a person can read (S2-M4-T2)."""

from clause_tracer.ingest import read_pasted_text, split_clauses
from clause_tracer.ingest.outline import render_outline


def test_outline_of_a_small_contract() -> None:
    document = read_pasted_text("1. Start\n1.1 Now. Then.")
    outline = render_outline(document, split_clauses(document))

    assert outline.splitlines()[1:8] == [
        "numbering\tnumbers",
        "warnings\t-",
        "1\t1\tlevel 1\t-\t0-9\tStart",
        "  1.s1\t0-9\t1. Start",
        "1.1\t1.1\tlevel 2\t1\t9-23\t-",
        "  1.1.s1\t9-18\t1.1 Now.",
        "  1.1.s2\t18-23\tThen.",
    ]
    assert outline.splitlines()[0].startswith("source\tpasted\t23\t")


def test_preview_is_cut_at_60_characters() -> None:
    document = read_pasted_text("1. " + "a" * 200)
    outline = render_outline(document, split_clauses(document))

    preview = outline.splitlines()[4].split("\t")[2]

    assert len(preview) == 60


def test_outline_with_no_clauses() -> None:
    document = read_pasted_text("x")

    assert "numbering\t-" in render_outline(document, ()).splitlines()
