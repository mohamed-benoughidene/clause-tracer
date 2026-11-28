"""The owner's Word reading table (S5-M3-T9, Constitution T11)."""

from collections.abc import Mapping
from pathlib import Path

import pytest

from clause_tracer.core import (
    HiddenReason,
    HiddenText,
    SideText,
    SideTextKind,
    Span,
    TrackedChange,
)
from clause_tracer.core.tests.owner_tables import (
    OwnerTableError,
    as_enum,
    as_int,
    as_str,
    as_str_tuple,
    load_table,
)
from clause_tracer.ingest import read_word_file
from clause_tracer.ingest.tests.builders.word import build_docx

TABLE = Path(__file__).parent / "tables" / "word_reading.toml"
CASE_KEYS = frozenset(
    {
        "id",
        "body",
        "styles",
        "numbering",
        "comments",
        "footnotes",
        "endnotes",
        "headers",
        "footers",
        "settings",
        "text",
        "hidden",
        "tracked_changes",
        "side_text",
        "warnings",
    }
)
REQUIRED = frozenset({"id", "body", "text", "hidden", "tracked_changes", "side_text", "warnings"})


def _cases() -> tuple[Mapping[str, object], ...]:
    return load_table(TABLE, case_keys=CASE_KEYS, required=REQUIRED).cases


def _optional_str(case: Mapping[str, object], key: str) -> str | None:
    return None if key not in case else as_str(case[key], key)


def _parts(value: object, where: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise OwnerTableError(f"{where}: expected a table of strings, got {value!r}")
    return {as_str(name, where): as_str(part, where) for name, part in value.items()}


def _span(row: Mapping[str, object], where: str) -> Span | None:
    has_start = "start" in row
    has_end = "end" in row
    if has_start != has_end:
        raise OwnerTableError(f"{where}: start and end must be given together")
    if not has_start:
        return None
    return Span(start=as_int(row["start"], where), end=as_int(row["end"], where))


def _rows(value: object, where: str) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, list):
        raise OwnerTableError(f"{where}: expected a list, got {value!r}")
    rows: list[Mapping[str, object]] = []
    for row in value:
        if not isinstance(row, dict):
            raise OwnerTableError(f"{where}: expected a table, got {row!r}")
        rows.append(row)
    return tuple(rows)


def _hidden(value: object, where: str) -> tuple[HiddenText, ...]:
    return tuple(
        HiddenText(
            span=_span(row, where),
            reason=as_enum(HiddenReason, row["reason"], where),
            boxes=(),
        )
        for row in _rows(value, where)
    )


def _tracked_changes(value: object, where: str) -> tuple[TrackedChange, ...]:
    return tuple(
        TrackedChange(
            earlier=as_str(row["earlier"], where),
            new=as_str(row["new"], where),
            author=as_str(row["author"], where),
            span=_span(row, where),
        )
        for row in _rows(value, where)
    )


def _side_text(value: object, where: str) -> tuple[SideText, ...]:
    return tuple(
        SideText(
            kind=as_enum(SideTextKind, row["kind"], where),
            ref=as_str(row["ref"], where),
            author=as_str(row["author"], where),
            text=as_str(row["text"], where),
            span=_span(row, where),
        )
        for row in _rows(value, where)
    )


def test_word_reading_table_has_rows() -> None:
    assert _cases()


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["id"]))
def test_word_reading_table(case: Mapping[str, object]) -> None:
    data = build_docx(
        as_str(case["body"], "body"),
        styles=_optional_str(case, "styles"),
        numbering=_optional_str(case, "numbering"),
        comments=_optional_str(case, "comments"),
        footnotes=_optional_str(case, "footnotes"),
        endnotes=_optional_str(case, "endnotes"),
        headers=None if "headers" not in case else _parts(case["headers"], "headers"),
        footers=None if "footers" not in case else _parts(case["footers"], "footers"),
        settings=_optional_str(case, "settings"),
    )

    document = read_word_file(data, name="t.docx")

    assert document.text == as_str(case["text"], "text")
    assert document.hidden == _hidden(case["hidden"], "hidden")
    assert document.tracked_changes == _tracked_changes(case["tracked_changes"], "tracked_changes")
    assert document.side_text == _side_text(case["side_text"], "side_text")
    assert [warning.code for warning in document.warnings] == list(
        as_str_tuple(case["warnings"], "warnings")
    )
