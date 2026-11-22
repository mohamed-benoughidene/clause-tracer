"""Golden-file test for the privacy report (S4-M5-T3)."""

from collections.abc import Callable
from pathlib import Path

from clause_tracer.core import FakePiiDetector
from clause_tracer.privacy.__main__ import DEFAULT_INPUT
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.placeholder import anonymise
from clause_tracer.privacy.render import render_privacy_report
from clause_tracer.privacy.sample_input import load_privacy_fixture

GOLDENS = Path(__file__).parent / "goldens"


def test_report_matches_its_golden(check_golden: Callable[[Path, str], None]) -> None:
    case = load_privacy_fixture(DEFAULT_INPUT.read_text(encoding="utf-8"))
    suggestions = find_personal_data(case, FakePiiDetector({}))
    entities = group_entities(case.document, suggestions)
    placeholder = anonymise(case.document, entities)

    check_golden(
        GOLDENS / "developer-agreement.privacy.txt",
        render_privacy_report(case, entities, placeholder),
    )
