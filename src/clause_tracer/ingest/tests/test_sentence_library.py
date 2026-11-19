"""Checks on NUPunkt itself, whose sentence breaks become sentence ids."""

import nupunkt


def test_nupunkt_version_is_pinned() -> None:
    assert nupunkt.__version__ == "0.8.0"


def test_known_breaks() -> None:
    text = (
        "Invoices are paid within 60 days. "
        "Interest runs at 4% p.a. from the due date. "
        "See cl. 5 below."
    )

    assert nupunkt.sentence_spans(text) == [(0, 33), (34, 77), (78, 94)]


def test_offsets_count_code_points() -> None:
    assert nupunkt.sentence_spans("x\U0001f600. Next one here.")[0] == (0, 3)


def test_empty_text_has_no_sentences() -> None:
    assert nupunkt.sentence_spans("") == []
