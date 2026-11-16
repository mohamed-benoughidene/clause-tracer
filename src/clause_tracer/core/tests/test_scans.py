"""The output scans (S1-M5-T2 to S1-M5-T8, Spec 6.2)."""

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
    TextSlot,
)
from clause_tracer.core.tests.owner_tables import TABLES_DIR, load_table

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


def test_scan_rules_match_owner_table() -> None:
    table = load_table(
        SCANS_TABLE,
        case_keys=_CASE_KEYS,
        required=frozenset({"id"}),
        sections=frozenset({"lists", "caps"}),
    )
    lists = table.sections["lists"]
    for key, copied in _COPIED_LISTS:
        value = lists[key]
        assert isinstance(value, list)
        assert tuple(value) == copied, key
    caps = table.sections["caps"]
    assert set(LENGTH_CAPS) == set(TextSlot)
    for slot in TextSlot:
        value = caps[slot.value]
        assert isinstance(value, int) and not isinstance(value, bool)
        assert LENGTH_CAPS[slot] == value, slot
