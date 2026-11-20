"""Golden-file tests for the outline (S2-M4-T5)."""

from collections.abc import Callable
from pathlib import Path

import pytest

from clause_tracer.core import FileKind
from clause_tracer.ingest import read_text_file, split_clauses
from clause_tracer.ingest.outline import render_outline

SAMPLES = Path(__file__).parent.parent / "samples"
GOLDENS = Path(__file__).parent / "goldens"


@pytest.mark.parametrize(
    ("sample", "kind"),
    [
        ("developer-agreement.txt", FileKind.TEXT),
        ("plain-paragraphs.md", FileKind.MARKDOWN),
    ],
)
def test_outline_matches_its_golden(
    check_golden: Callable[[Path, str], None], sample: str, kind: FileKind
) -> None:
    data = (SAMPLES / sample).read_bytes()
    document = read_text_file(data, kind=kind, name=sample)

    actual = render_outline(document, split_clauses(document))

    check_golden(GOLDENS / (Path(sample).stem + ".outline.txt"), actual)
