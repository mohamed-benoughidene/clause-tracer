"""The owner's sample table (S3-M5-T8, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

from clause_tracer.core import ClauseId, LinkMap, Span
from clause_tracer.core.tests.owner_tables import (
    OwnerTableError,
    as_bool,
    as_str,
    load_table,
)
from clause_tracer.links import load_clause_fixture, map_links
from clause_tracer.links.__main__ import DEFAULT_INPUT
from clause_tracer.links._index import ClauseIndex, build_index

TABLE = Path(__file__).parent / "tables" / "sample.toml"
KEYS = ("terms", "outside", "overrides", "references", "undefined")
TABLE_DATA = load_table(
    TABLE,
    case_keys=frozenset(),
    required=frozenset(),
    sections=frozenset({"sample"}),
)


def _sample_section() -> Mapping[str, object]:
    if "sample" not in TABLE_DATA.sections:
        raise OwnerTableError("sample.toml: missing section sample")
    section = TABLE_DATA.sections["sample"]
    for key in KEYS:
        if key not in section:
            raise OwnerTableError(f"sample.toml: missing key {key}")
    for key in section:
        if key not in KEYS:
            raise OwnerTableError(f"sample.toml: unknown key {key}")
    return section


def _link_map() -> tuple[str, ClauseIndex, LinkMap]:
    sample = load_clause_fixture(DEFAULT_INPUT.read_text(encoding="utf-8"))
    return (
        sample.document.text,
        build_index(sample.clauses),
        map_links(sample.document, sample.clauses),
    )


def _clause(index: ClauseIndex, span: Span) -> str:
    clause = index.clause_at(span.start)
    assert clause is not None
    return str(clause.id)


def _target(target: ClauseId | None) -> str:
    return "" if target is None else str(target)


def _rows(value: object) -> list[Mapping[str, object]]:
    assert isinstance(value, list)
    rows: list[Mapping[str, object]] = []
    for row in value:
        assert isinstance(row, dict)
        rows.append(row)
    return rows


def test_sample_terms() -> None:
    section = _sample_section()
    expected = [as_str(term, "terms") for term in _list(section["terms"])]
    _, _, links = _link_map()

    assert [term.term for term in links.terms] == expected


def test_sample_outside() -> None:
    section = _sample_section()
    expected = [
        {"name": as_str(row["name"], "name"), "clause": as_str(row["clause"], "clause")}
        for row in _rows(section["outside"])
    ]
    _, index, links = _link_map()

    actual = [
        {"name": outside.name, "clause": _clause(index, outside.evidence)}
        for outside in links.outside_documents
    ]

    assert actual == expected


def test_sample_overrides() -> None:
    section = _sample_section()
    expected = [
        {
            "clause": as_str(row["clause"], "clause"),
            "target": as_str(row["target"], "target"),
            "overrides_target": as_bool(row["overrides_target"], "overrides_target"),
        }
        for row in _rows(section["overrides"])
    ]
    _, _, links = _link_map()

    actual = [
        {
            "clause": str(override.clause_id),
            "target": _target(override.target),
            "overrides_target": override.overrides_target,
        }
        for override in links.overrides
    ]

    assert actual == expected


def test_sample_references() -> None:
    section = _sample_section()
    expected = [
        {
            "clause": as_str(row["clause"], "clause"),
            "written": as_str(row["written"], "written"),
            "target": as_str(row["target"], "target"),
        }
        for row in _rows(section["references"])
    ]
    text, index, links = _link_map()

    actual = [
        {
            "clause": _clause(index, reference.source),
            "written": text[reference.source.start : reference.source.end],
            "target": _target(reference.target),
        }
        for reference in links.references
    ]

    assert actual == expected


def test_sample_undefined() -> None:
    section = _sample_section()
    expected = [as_str(term, "undefined") for term in _list(section["undefined"])]
    text, _, links = _link_map()

    assert [text[span.start : span.end] for span in links.undefined_terms] == expected


def _list(value: object) -> list[object]:
    assert isinstance(value, list)
    return value
