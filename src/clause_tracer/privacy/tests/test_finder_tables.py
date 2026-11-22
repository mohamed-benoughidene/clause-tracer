"""The owner's finders and party details tables (S4-M2-T10).

The tables are the owner's expected answers (Constitution T11). A failing
row means the code or the row is wrong: bring it to the owner, and never
edit the table.
"""

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Final

import pytest

from clause_tracer.core import (
    DefinedTerm,
    Party,
    PiiSource,
    PiiSuggestion,
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
from clause_tracer.privacy.addresses import find_addresses
from clause_tracer.privacy.companies import find_companies
from clause_tracer.privacy.party import find_party_details
from clause_tracer.privacy.patterns import find_patterns
from clause_tracer.privacy.people import find_people
from clause_tracer.privacy.tests.case_builder import span_of

TABLES: Final[Path] = Path(__file__).parent / "tables"
FINDERS: Final[Mapping[str, Callable[[str], tuple[PiiSuggestion, ...]]]] = {
    "patterns": find_patterns,
    "companies": find_companies,
    "addresses": find_addresses,
    "people": find_people,
}
SOURCES: Final[Mapping[str, PiiSource]] = {
    "patterns": PiiSource.PATTERN,
    "companies": PiiSource.RULE,
    "addresses": PiiSource.RULE,
    "people": PiiSource.RULE,
}
FINDER_TABLE: Final[OwnerTable] = load_table(
    TABLES / "finders.toml",
    case_keys=frozenset({"id", "finder", "text", "found"}),
    required=frozenset({"id", "finder", "text", "found"}),
)
PARTY_TABLE: Final[OwnerTable] = load_table(
    TABLES / "party_details.toml",
    case_keys=frozenset({"id", "parties", "terms", "text", "found"}),
    required=frozenset({"id", "parties", "text", "found"}),
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


def _finder(name: str) -> Callable[[str], tuple[PiiSuggestion, ...]]:
    if name not in FINDERS:
        raise ValueError(f"unknown finder {name}")
    return FINDERS[name]


def _expected_rows(
    text: str,
    value: object,
    source: PiiSource,
) -> tuple[PiiSuggestion, ...]:
    expected: list[PiiSuggestion] = []
    for row in _rows(value, "found"):
        span = span_of(text, as_str(row["text"], "text"), as_int(row.get("nth", 1), "nth"))
        expected.append(
            PiiSuggestion(
                span=span,
                kind=as_enum(PlaceholderKind, row["kind"], "kind"),
                source=source,
            )
        )
    return tuple(expected)


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


@pytest.mark.parametrize(
    "row", FINDER_TABLE.cases, ids=[_case_id(row) for row in FINDER_TABLE.cases]
)
def test_finder_table(row: Mapping[str, object]) -> None:
    text = as_str(row["text"], "text")
    finder_name = as_str(row["finder"], "finder")
    finder = _finder(finder_name)

    assert finder(text) == _expected_rows(text, row["found"], SOURCES[finder_name])


def test_finder_table_has_rows() -> None:
    finder_names = [as_str(row["finder"], "finder") for row in FINDER_TABLE.cases]

    assert len(FINDER_TABLE.cases) >= 24
    for finder_name in FINDERS:
        assert finder_names.count(finder_name) >= 4


@pytest.mark.parametrize("row", PARTY_TABLE.cases, ids=[_case_id(row) for row in PARTY_TABLE.cases])
def test_party_table(row: Mapping[str, object]) -> None:
    text = as_str(row["text"], "text")
    parties: Sequence[Party] = _parties(row["parties"])
    terms: Sequence[DefinedTerm] = _terms(row.get("terms", []), text)

    assert find_party_details(text, parties, terms) == _expected_rows(
        text, row["found"], PiiSource.PARTY_DETAILS
    )


def test_party_table_has_rows() -> None:
    assert len(PARTY_TABLE.cases) >= 10
