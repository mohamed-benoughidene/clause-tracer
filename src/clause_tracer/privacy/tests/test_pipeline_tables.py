"""The owner's pipeline and entities tables (S4-M3-T10).

The tables are the owner's expected answers (Constitution T11). A failing
row means the code or the row is wrong: bring it to the owner, and never
edit the table.
"""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final

import pytest

from clause_tracer.core import (
    DefinedTerm,
    Document,
    FakePiiDetector,
    Party,
    PiiSource,
    PiiSuggestion,
    PlaceholderEntity,
    PlaceholderKind,
    Span,
)
from clause_tracer.core.tests.owner_tables import (
    OwnerTable,
    OwnerTableError,
    as_bool,
    as_enum,
    as_int,
    as_str,
    load_table,
)
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.tests.case_builder import make_case, span_of, suggestion

TABLES: Final[Path] = Path(__file__).parent / "tables"
PIPELINE_TABLE: Final[OwnerTable] = load_table(
    TABLES / "pipeline.toml",
    case_keys=frozenset({"id", "sentences", "parties", "terms", "detector", "found"}),
    required=frozenset({"id", "sentences", "found"}),
)
ENTITIES_TABLE: Final[OwnerTable] = load_table(
    TABLES / "entities.toml",
    case_keys=frozenset({"id", "text", "suggestions", "entities"}),
    required=frozenset({"id", "text", "suggestions", "entities"}),
)


def _case_id(row: Mapping[str, object]) -> str:
    return as_str(row["id"], "id")


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


def _sentences(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise OwnerTableError("sentences: expected a list of strings")
    return tuple(as_str(item, "sentences") for item in value)


def _parties(value: object) -> tuple[Party, ...]:
    parties: list[Party] = []
    for row in _rows(value, "parties"):
        address = as_str(row["address"], "address") if "address" in row else ""
        parties.append(
            Party(
                name=as_str(row["name"], "name"),
                address=address or None,
                yours=as_bool(row["yours"], "yours"),
            )
        )
    return tuple(parties)


def _terms(value: object, text: str) -> tuple[DefinedTerm, ...]:
    terms: list[DefinedTerm] = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, str):
            terms.append(DefinedTerm(term=item, definition=Span(start=0, end=len(text)), uses=()))
            continue
        if not isinstance(item, dict):
            raise OwnerTableError("terms: expected a string or a table")
        terms.append(
            DefinedTerm(
                term=as_str(item["term"], "term"),
                definition=span_of(text, as_str(item["definition"], "definition")),
                uses=(),
            )
        )
    return tuple(terms)


def _detector_rows(text: str, value: object) -> tuple[PiiSuggestion, ...]:
    planted: list[PiiSuggestion] = []
    for row in _rows(value, "detector"):
        planted.append(
            suggestion(
                text,
                as_str(row["text"], "text"),
                as_enum(PlaceholderKind, row["kind"], "kind"),
                as_enum(PiiSource, row["source"], "source"),
                as_int(row.get("nth", 1), "nth"),
            )
        )
    return tuple(planted)


def _pipeline_found(text: str, value: object) -> tuple[PiiSuggestion, ...]:
    found: list[PiiSuggestion] = []
    for row in _rows(value, "found"):
        found.append(
            suggestion(
                text,
                as_str(row["text"], "text"),
                as_enum(PlaceholderKind, row["kind"], "kind"),
                as_enum(PiiSource, row["source"], "source"),
                as_int(row.get("nth", 1), "nth"),
            )
        )
    return tuple(found)


def _entity_rows(text: str, value: object) -> tuple[PlaceholderEntity, ...]:
    entities: list[PlaceholderEntity] = []
    for row in _rows(value, "entities"):
        entity_id = as_str(row["id"], "id")
        kind_name, number_text = entity_id.rsplit("-", 1)
        spans: list[Span] = []
        for span_row in _rows(row["spans"], "spans"):
            spans.append(
                span_of(
                    text,
                    as_str(span_row["text"], "text"),
                    as_int(span_row.get("nth", 1), "nth"),
                )
            )
        entities.append(
            PlaceholderEntity(
                id=entity_id,
                kind=PlaceholderKind(kind_name),
                number=int(number_text),
                spans=tuple(spans),
            )
        )
    return tuple(entities)


@pytest.mark.parametrize(
    "row", PIPELINE_TABLE.cases, ids=[_case_id(row) for row in PIPELINE_TABLE.cases]
)
def test_pipeline_table(row: Mapping[str, object]) -> None:
    sentences = _sentences(row["sentences"])
    case = make_case(
        sentences,
        parties=_parties(row.get("parties", [])),
        terms=_terms(row.get("terms", []), " ".join(sentences)),
    )
    text = case.document.text
    detector = FakePiiDetector({text: _detector_rows(text, row.get("detector", []))})

    assert find_personal_data(case, detector) == _pipeline_found(text, row["found"])


def test_pipeline_table_has_rows() -> None:
    assert len(PIPELINE_TABLE.cases) >= 16


@pytest.mark.parametrize(
    "row", ENTITIES_TABLE.cases, ids=[_case_id(row) for row in ENTITIES_TABLE.cases]
)
def test_entities_table(row: Mapping[str, object]) -> None:
    text = as_str(row["text"], "text")
    document: Document = make_case([text]).document
    suggestions: Sequence[PiiSuggestion] = tuple(
        suggestion(
            text,
            as_str(item["text"], "text"),
            as_enum(PlaceholderKind, item["kind"], "kind"),
            PiiSource.RULE,
            as_int(item.get("nth", 1), "nth"),
        )
        for item in _rows(row["suggestions"], "suggestions")
    )

    assert group_entities(document, suggestions) == _entity_rows(text, row["entities"])


def test_entities_table_has_rows() -> None:
    assert len(ENTITIES_TABLE.cases) >= 12
