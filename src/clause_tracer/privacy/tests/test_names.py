"""Name and address forms, and the word lists (S4-M2-T1)."""

import pytest

from clause_tracer.core import PlaceholderKind
from clause_tracer.privacy.names import (
    COMMON_WORD_NAMES,
    HONORIFICS,
    NAME_STOP_WORDS,
    address_forms,
    is_company_name,
    is_company_seed,
    name_forms,
)


def honorific_forms(last: str) -> set[str]:
    """Every honorific form of one surname, with and without a full stop."""

    return {f"{h}{dot} {last}" for h in HONORIFICS for dot in ("", ".")}


def test_person_forms_of_two_words() -> None:
    forms = name_forms("Sarah Jones", PlaceholderKind.PERSON)

    assert set(forms) == {"sarah jones", "sarah", "jones"} | honorific_forms("jones")
    assert len(forms) == 15
    assert forms == tuple(sorted(forms, key=lambda form: (-len(form), form)))


def test_person_forms_of_three_words() -> None:
    assert set(name_forms("Ms. Anna Maria Smith", PlaceholderKind.PERSON)) == {
        "anna maria smith",
        "anna smith",
        "anna",
        "smith",
    } | honorific_forms("smith")


def test_person_of_one_short_word() -> None:
    assert set(name_forms("Li", PlaceholderKind.PERSON)) == {"li"} | honorific_forms("li")


def test_company_forms_swap_ltd_and_limited() -> None:
    assert name_forms("Brightline Studio Ltd", PlaceholderKind.COMPANY) == (
        "brightline studio limited",
        "brightline studio ltd",
        "brightline studio",
    )


def test_company_suffix_dot_is_dropped() -> None:
    assert name_forms("Smith & Sons Ltd.", PlaceholderKind.COMPANY) == (
        "smith & sons limited",
        "smith & sons ltd",
        "smith & sons",
    )


def test_company_other_suffix_has_no_swap() -> None:
    assert name_forms("Acme Co", PlaceholderKind.COMPANY) == ("acme co", "acme")


def test_company_without_suffix() -> None:
    assert name_forms("Acme", PlaceholderKind.COMPANY) == ("acme",)


def test_empty_forms() -> None:
    assert name_forms("", PlaceholderKind.PERSON) == ()
    assert name_forms("Ltd", PlaceholderKind.COMPANY) == ()
    assert name_forms("Ms", PlaceholderKind.PERSON) == ()


def test_forms_of_another_kind_raise() -> None:
    with pytest.raises(ValueError) as error:
        name_forms("a@b.com", PlaceholderKind.EMAIL)

    assert str(error.value) == "privacy: name forms need a person or a company"


def test_is_company_name() -> None:
    assert is_company_name("Acme Ltd.")
    assert is_company_name("Acme Co")
    assert not is_company_name("Karim Benali")
    assert not is_company_name("")


def test_address_forms() -> None:
    assert address_forms("14 Harbour Street, Leeds LS1 4AB") == (
        "14 harbour street, leeds ls1 4ab",
        "14 harbour street",
    )
    assert address_forms("Flat 2, 12 High Road, Leeds") == ("flat 2, 12 high road, leeds",)
    assert address_forms("12 High Road") == ("12 high road",)


def test_stop_words_hold_months_and_common_names() -> None:
    assert {"may", "april", "monday", "will", "price"} <= NAME_STOP_WORDS


def test_common_word_names_are_not_in_the_hard_list() -> None:
    assert COMMON_WORD_NAMES.isdisjoint(NAME_STOP_WORDS)


def test_is_company_seed() -> None:
    assert is_company_seed("Acme LP")
    assert is_company_seed("Acme Pte")
    assert is_company_seed("Acme Ltd.")
    assert not is_company_seed("Karim Benali")
    assert not is_company_seed("")
    assert not is_company_name("Acme LP")
