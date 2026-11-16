"""The label-rule owner table as test cases. Not exported from core."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from clause_tracer.core import (
    LabelInput,
    Level,
    ReasonCode,
    UnreadableSpans,
    WrittenBy,
)
from clause_tracer.core.sample_input import parse_label_inputs, parse_sample
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_enum,
    as_enum_tuple,
    load_table,
)

SAMPLE = Path(__file__).parent.parent / "samples" / "spec-14-5.toml"

LABEL_CASE_KEYS = frozenset(
    {
        "id",
        "rule",
        "note",
        "position",
        "match",
        "values",
        "judged",
        "clauses_to_read",
        "outside_documents",
        "level",
        "reasons",
        "written_by",
    }
)
LABEL_CASE_REQUIRED = frozenset(
    {"id", "rule", "position", "match", "level", "reasons", "written_by"}
)


@dataclass(frozen=True, slots=True, kw_only=True)
class LabelCase:
    """One row of the owner's label-rule table, ready for label_position."""

    id: str
    rule: str
    label_input: LabelInput
    unreadable: UnreadableSpans
    level: Level
    reasons: frozenset[ReasonCode]
    written_by: WrittenBy


def label_rule_cases() -> tuple[LabelCase, ...]:
    """Every row of the owner's label-rule table, with its input built."""

    table = load_table(
        TABLES_DIR / "label_rules.toml",
        case_keys=LABEL_CASE_KEYS,
        required=LABEL_CASE_REQUIRED,
    )
    sample = parse_sample(tomllib.loads(SAMPLE.read_text(encoding="utf-8")))
    cases: list[LabelCase] = []
    for row in table.cases:
        where = f"case {row['id']}"
        # The input keys of the sample format, in file order.
        entry: dict[str, object] = {
            "position": row["position"],
            "match": row["match"],
        }
        for key in ("values", "judged", "clauses_to_read", "outside_documents"):
            if key in row:
                entry[key] = row[key]
        inputs, unreadable = parse_label_inputs([entry], sample.playbook)
        cases.append(
            LabelCase(
                id=str(row["id"]),
                rule=str(row["rule"]),
                label_input=inputs[0],
                unreadable=unreadable,
                level=as_enum(Level, row["level"], f"{where} level"),
                reasons=frozenset(as_enum_tuple(ReasonCode, row["reasons"], f"{where} reasons")),
                written_by=as_enum(WrittenBy, row["written_by"], f"{where} written_by"),
            )
        )
    return tuple(cases)
