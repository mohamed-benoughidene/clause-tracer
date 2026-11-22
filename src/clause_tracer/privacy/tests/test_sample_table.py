"""The owner's sample table (S4-M5-T6).

The table is the owner's expected answer (Constitution T11). A failing row
means the code or the row is wrong: bring it to the owner, and never edit
the table.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Final

from clause_tracer.core import (
    Document,
    FakePiiDetector,
    PlaceholderEntity,
    PlaceholderKind,
    PlaceholderText,
)
from clause_tracer.core.tests.owner_tables import (
    OwnerTable,
    OwnerTableError,
    as_int,
    as_str,
    load_table,
)
from clause_tracer.privacy.__main__ import DEFAULT_INPUT
from clause_tracer.privacy._spans import overlaps
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.placeholder import anonymise
from clause_tracer.privacy.sample_input import PrivacyInput, load_privacy_fixture
from clause_tracer.privacy.tests.case_builder import span_of

TABLES: Final[Path] = Path(__file__).parent / "tables"
SAMPLE_TABLE: Final[OwnerTable] = load_table(
    TABLES / "sample.toml",
    case_keys=frozenset({"id", "kind", "entity_kind", "number", "spans", "text", "nth"}),
    required=frozenset({"id", "kind"}),
)


def _rows(value: object, where: str) -> list[Mapping[str, object]]:
    """Read a list of TOML tables, or raise when the cell is not one."""

    if not isinstance(value, list):
        raise OwnerTableError(f"{where}: expected a list of tables")
    rows: list[Mapping[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            raise OwnerTableError(f"{where}: expected a list of tables")
        rows.append(item)
    return rows


def _pipeline() -> tuple[PrivacyInput, tuple[PlaceholderEntity, ...], PlaceholderText]:
    case = load_privacy_fixture(DEFAULT_INPUT.read_text(encoding="utf-8"))
    suggestions = find_personal_data(case, FakePiiDetector({}))
    entities = group_entities(case.document, suggestions)
    return case, entities, anonymise(case.document, entities)


def _entity(row: Mapping[str, object], document: Document) -> PlaceholderEntity:
    entity_kind = as_str(row["entity_kind"], "entity_kind")
    number = as_int(row["number"], "number")
    spans = tuple(
        span_of(
            document.text,
            as_str(span["text"], "text"),
            as_int(span.get("nth", 1), "nth"),
        )
        for span in _rows(row["spans"], "spans")
    )
    return PlaceholderEntity(
        id=f"{entity_kind}-{number}",
        kind=PlaceholderKind(entity_kind),
        number=number,
        spans=spans,
    )


def test_entities_match_the_table() -> None:
    case, entities, _ = _pipeline()
    rows = [row for row in SAMPLE_TABLE.cases if row["kind"] == "entity"]

    table = {as_str(row["id"], "id"): _entity(row, case.document) for row in rows}

    assert {entity.id: entity for entity in entities} == table
    assert len(entities) == len(rows)


def test_kept_rows() -> None:
    case, entities, placeholder = _pipeline()
    entity_spans = [span for entity in entities for span in entity.spans]

    for row in SAMPLE_TABLE.cases:
        if row["kind"] != "kept":
            continue
        text = as_str(row["text"], "text")
        assert text in placeholder.text, row["id"]
        span = span_of(case.document.text, text, as_int(row.get("nth", 1), "nth"))
        assert not any(overlaps(span, entity_span) for entity_span in entity_spans), row["id"]


def test_gone_rows() -> None:
    _, _, placeholder = _pipeline()
    sent = placeholder.text.casefold()

    for row in SAMPLE_TABLE.cases:
        if row["kind"] != "gone":
            continue
        assert as_str(row["text"], "text").casefold() not in sent, row["id"]


def test_sample_table_has_rows() -> None:
    kinds = [row["kind"] for row in SAMPLE_TABLE.cases]

    assert kinds.count("entity") >= 7
    assert kinds.count("gone") >= 12
    assert kinds.count("kept") >= 8
