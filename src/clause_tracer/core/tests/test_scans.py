"""The output scans (S1-M5-T2 to S1-M5-T8, Spec 6.2)."""

from collections.abc import Mapping

import pytest

from clause_tracer.core import (
    ABBREVIATIONS,
    ADVICE_PHRASES,
    CONTACT_WORDS,
    EVALUATIVE_WORDS,
    FILLER_PHRASES,
    FIRST_PERSON_WORDS,
    INJECTION_PHRASES,
    LAW_WORDS,
    LENGTH_CAPS,
    Level,
    ScanFinding,
    TextSlot,
    contains_phrase,
    scan_text,
)
from clause_tracer.core.tests.owner_tables import (
    TABLES_DIR,
    as_enum,
    as_enum_tuple,
    as_str,
    load_table,
)

SCANS_TABLE = TABLES_DIR / "scans.toml"

_CASE_KEYS: frozenset[str] = frozenset(
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

_TABLE = load_table(
    SCANS_TABLE,
    case_keys=_CASE_KEYS,
    required=_REQUIRED,
    sections=frozenset({"lists", "caps"}),
)
_ROWS: tuple[Mapping[str, object], ...] = _TABLE.cases
_IDS: list[str] = [str(row["id"]) for row in _ROWS]

TEXT_FINDINGS: frozenset[ScanFinding] = frozenset(
    {
        ScanFinding.TOO_LONG,
        ScanFinding.LAW_WORD,
        ScanFinding.ADVICE,
        ScanFinding.INJECTION_TELL,
        ScanFinding.CONTACT_WORD,
        ScanFinding.WEB_ADDRESS,
        ScanFinding.EMAIL_ADDRESS,
        ScanFinding.WRONG_LABEL_WORD,
    }
)

_COPIED_LISTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("law_words", LAW_WORDS),
    ("advice_phrases", ADVICE_PHRASES),
    ("injection_phrases", INJECTION_PHRASES),
    ("contact_words", CONTACT_WORDS),
    ("first_person_words", FIRST_PERSON_WORDS),
    ("filler_phrases", FILLER_PHRASES),
    ("evaluative_words", EVALUATIVE_WORDS),
    ("abbreviations", ABBREVIATIONS),
)


def _where(row: Mapping[str, object], key: str) -> str:
    return f"case {row['id']} {key}"


def _row_label(row: Mapping[str, object]) -> Level | None:
    if "label" not in row:
        return None
    return as_enum(Level, row["label"], _where(row, "label"))


def test_scan_rules_match_owner_table() -> None:
    for key, copied in _COPIED_LISTS:
        value = _TABLE.sections["lists"][key]
        assert isinstance(value, list)
        assert tuple(value) == copied, key
    caps = _TABLE.sections["caps"]
    assert set(LENGTH_CAPS) == set(TextSlot)
    for slot in TextSlot:
        value = caps[slot.value]
        assert isinstance(value, int) and not isinstance(value, bool)
        assert LENGTH_CAPS[slot] == value, slot


@pytest.mark.parametrize("row", _ROWS, ids=_IDS)
def test_text_scans_table(row: Mapping[str, object]) -> None:
    text = as_str(row["text"], _where(row, "text"))
    slot = as_enum(TextSlot, row["slot"], _where(row, "slot"))
    findings = frozenset(as_enum_tuple(ScanFinding, row["findings"], _where(row, "findings")))
    assert set(scan_text(text, slot, _row_label(row))) == findings & TEXT_FINDINGS


def test_scans_table_has_rows() -> None:
    assert len(_ROWS) > 0


def test_every_law_word_fails_in_any_case() -> None:
    # Promise test: no AI text states what a law allows (Spec 11).
    for word in LAW_WORDS:
        for form in (word.lower(), word.upper(), word.title()):
            text = f"This is {form} here."
            assert ScanFinding.LAW_WORD in scan_text(text, TextSlot.READING, None)


def test_curly_apostrophe_is_folded() -> None:
    assert contains_phrase("don’t sign", "don't sign")
