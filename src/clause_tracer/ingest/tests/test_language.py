"""The not-English warning (S2-M5-T4, ADR 0017)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core.tests.owner_tables import as_bool, as_str, load_table
from clause_tracer.ingest.language import looks_not_english

TABLE = Path(__file__).parent / "tables" / "not_english.toml"
CASE_KEYS: frozenset[str] = frozenset({"id", "text", "warned"})
REQUIRED: frozenset[str] = frozenset({"id", "text", "warned"})

_TABLE = load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED)
_ROWS: list[Mapping[str, object]] = list(_TABLE.cases)
_IDS = [str(row["id"]) for row in _ROWS]

PACKAGE = Path(__file__).parents[2]


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_not_english_table(row: Mapping[str, object]) -> None:
    text = as_str(row["text"], f"case {row['id']} text")
    warned = as_bool(row["warned"], f"case {row['id']} warned")

    assert looks_not_english(text) is warned


def test_not_english_table_has_rows() -> None:
    assert len(_ROWS) >= 8


def test_text_under_10_words_is_never_warned() -> None:
    assert looks_not_english("Le Client paie les frais.") is False


def test_only_this_file_imports_lingua() -> None:
    allowed = {
        PACKAGE / "ingest" / "language.py",
        *(PACKAGE / "ingest" / "tests").glob("*.py"),
    }

    for path in PACKAGE.rglob("*.py"):
        if path in allowed:
            continue
        assert "lingua" not in path.read_text(encoding="utf-8"), path
