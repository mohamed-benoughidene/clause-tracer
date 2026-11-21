"""The printed link map (S3-M5-T3)."""

import pytest

from clause_tracer.links import map_links, render_link_map
from clause_tracer.links.tests.case_builder import build_case, span_of

_FIELD_COUNTS = {
    "source": 3,
    "counts": 6,
    "reference": 5,
    "term": 5,
    "override": 6,
    "outside": 4,
    "undefined": 4,
}


def _render(rows: list[dict[str, object]]) -> tuple[str, str]:
    case = build_case(rows)
    rendered = render_link_map(case.document, case.clauses, map_links(case.document, case.clauses))
    return rendered, case.document.text


def _lines(rendered: str) -> list[str]:
    assert rendered.endswith("\n")
    return rendered.split("\n")[:-1]


def test_empty_map() -> None:
    rendered, _ = _render([])

    assert rendered == (
        "source\tcase.txt\t0\ncounts\treferences 0\tterms 0\toverrides 0\toutside 0\tundefined 0\n"
    )


def test_reference_line() -> None:
    rendered, text = _render(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. See clause 4."]},
        ]
    )
    source = span_of(text, "clause 4")

    assert f"reference\t9\t{source.start}-{source.end}\t4\tclause 4" in _lines(rendered)


def test_unresolved_shows_dash() -> None:
    rendered, text = _render(
        [
            {"id": "9", "sentences": ["9. See clause 7."]},
        ]
    )
    source = span_of(text, "clause 7")

    assert f"reference\t9\t{source.start}-{source.end}\t-\tclause 7" in _lines(rendered)


def test_override_line() -> None:
    rendered, text = _render(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. Subject to Clause 4, fees are fixed."]},
        ]
    )
    evidence = span_of(text, "Subject to Clause 4")

    assert f"override\t9\t4\tqualified\t{evidence.start}-{evidence.end}\tSubject to Clause 4" in (
        _lines(rendered)
    )


def test_tab_in_text_is_a_space() -> None:
    rendered, _ = _render(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. See\tclause 4."]},
        ]
    )

    assert any(line.endswith("\tclause 4") for line in _lines(rendered))
    for line in _lines(rendered):
        kind = line.split("\t", 1)[0]
        assert len(line.split("\t")) == _FIELD_COUNTS[kind], line


def test_unordered_clauses_raise() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ["1. Pay."]},
            {"id": "2", "sentences": ["2. Fees."]},
        ]
    )
    link_map = map_links(case.document, case.clauses)

    with pytest.raises(ValueError, match="clauses are not in text order"):
        render_link_map(case.document, (case.clauses[1], case.clauses[0]), link_map)
