"""The owner's scan-table rows, built for the scan tests. Not exported from core.

Each row of scans.toml is one case: the AI text, the slot it would be
shown in, the context the scans compare it with, and the findings the
full scan must give. The owner owns the table (T11); tests only read it.
"""

from dataclasses import dataclass
from decimal import Decimal

from clause_tracer.core.checks import ScanContext
from clause_tracer.core.enums import Level, ScanFinding, TextSlot
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_bool,
    as_decimal,
    as_enum,
    as_enum_tuple,
    as_str,
    as_str_tuple,
    load_table,
)

SCAN_CASE_KEYS: frozenset[str] = frozenset(
    {
        "id",
        "text",
        "slot",
        "label",
        "allowed_numbers",
        "acceptable_limits",
        "known_placeholders",
        "defined_roles",
        "personal_data",
        "clause_numbers",
        "quote",
        "source_text",
        "instruction_given",
        "findings",
    }
)
_REQUIRED: frozenset[str] = frozenset({"id", "text", "slot", "findings"})


@dataclass(frozen=True, slots=True, kw_only=True)
class ScanCase:
    """One row of the owner's scan table, ready to run the scans on."""

    id: str
    text: str
    slot: TextSlot
    context: ScanContext
    personal_data: tuple[str, ...]
    findings: frozenset[ScanFinding]


def _optional_str(row: dict[str, object], key: str, where: str) -> str | None:
    if key not in row:
        return None
    return as_str(row[key], f"{where} {key}")


def _str_list(row: dict[str, object], key: str, where: str) -> tuple[str, ...]:
    if key not in row:
        return ()
    return as_str_tuple(row[key], f"{where} {key}")


def _decimal_list(row: dict[str, object], key: str, where: str) -> tuple[Decimal, ...]:
    if key not in row:
        return ()
    items = as_str_tuple(row[key], f"{where} {key}")
    return tuple(as_decimal(item, f"{where} {key}") for item in items)


def scan_cases() -> tuple[ScanCase, ...]:
    """Every row of the owner's scan table, in file order."""

    table = load_table(
        TABLES_DIR / "scans.toml",
        case_keys=SCAN_CASE_KEYS,
        required=_REQUIRED,
        sections=frozenset({"lists", "caps"}),
    )
    cases: list[ScanCase] = []
    for row in table.cases:
        entry = dict(row)
        case_id = as_str(entry["id"], "case id")
        where = f"case {case_id}"
        label: Level | None = None
        if "label" in entry:
            label = as_enum(Level, entry["label"], f"{where} label")
        instruction_given = False
        if "instruction_given" in entry:
            instruction_given = as_bool(entry["instruction_given"], f"{where} instruction_given")
        context = ScanContext(
            label=label,
            allowed_numbers=_decimal_list(entry, "allowed_numbers", where),
            acceptable_limits=_decimal_list(entry, "acceptable_limits", where),
            known_placeholders=_str_list(entry, "known_placeholders", where),
            defined_roles=_str_list(entry, "defined_roles", where),
            clause_numbers=_str_list(entry, "clause_numbers", where),
            quote=_optional_str(entry, "quote", where),
            source_text=_optional_str(entry, "source_text", where),
            instruction_given=instruction_given,
        )
        cases.append(
            ScanCase(
                id=case_id,
                text=as_str(entry["text"], f"{where} text"),
                slot=as_enum(TextSlot, entry["slot"], f"{where} slot"),
                context=context,
                personal_data=_str_list(entry, "personal_data", where),
                findings=frozenset(
                    as_enum_tuple(ScanFinding, entry["findings"], f"{where} findings")
                ),
            )
        )
    return tuple(cases)
