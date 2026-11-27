"""A clean text file round-trips through a real child (S5-M2-T7)."""

import time
from pathlib import Path

from clause_tracer.cli.child_runner import read_file_in_child
from clause_tracer.ingest import read_file

SAMPLE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "clause_tracer"
    / "ingest"
    / "samples"
    / "developer-agreement.txt"
)


def test_a_clean_text_file_round_trips() -> None:
    data = SAMPLE.read_bytes()

    assert read_file_in_child(data, name="a.txt") == read_file(data, name="a.txt")


def test_child_start_up_is_fast_enough() -> None:
    data = SAMPLE.read_bytes()

    started = time.monotonic()
    read_file_in_child(data, name="a.txt")
    elapsed = time.monotonic() - started

    assert elapsed < 10.0
