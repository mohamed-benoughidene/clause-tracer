"""Typed party details and their variants (S4-M2-T4)."""

import pytest

from clause_tracer.core import (
    DefinedTerm,
    Party,
    PiiSource,
    PlaceholderKind,
    Span,
    fold_for_matching,
)
from clause_tracer.privacy.party import find_party_details

BRIGHTLINE = Party(name="Brightline Studio Ltd", address=None, yours=False)
NORTHWIND = Party(name="Northwind, Inc.", address=None, yours=False)
COMPANY = PlaceholderKind.COMPANY
PERSON = PlaceholderKind.PERSON
ADDRESS = PlaceholderKind.ADDRESS


def spans(
    text: str,
    parties: tuple[Party, ...] = (),
    terms: tuple[DefinedTerm, ...] = (),
) -> list[tuple[int, int]]:
    return [
        (suggestion.span.start, suggestion.span.end)
        for suggestion in find_party_details(text, parties, terms)
    ]


def test_finds_a_company_and_its_forms() -> None:
    assert spans("Brightline Studio Ltd and brightline studio limited.", (BRIGHTLINE,)) == [
        (0, 17),
        (0, 21),
        (26, 43),
        (26, 51),
    ]


def test_finds_a_company_typed_with_a_comma() -> None:
    assert spans("Northwind, Inc. signs. Northwind pays.", (NORTHWIND,)) == [
        (0, 9),
        (0, 14),
        (23, 32),
    ]


def test_a_comma_after_a_short_company_name_is_outside_the_span() -> None:
    assert spans("Ask Northwind, then pay.", (NORTHWIND,)) == [(4, 13)]


def test_a_name_split_by_a_line_break_is_found() -> None:
    assert spans("Brightline\nStudio Ltd", (BRIGHTLINE,)) == [(0, 17), (0, 21)]


def test_finds_a_person_and_their_forms() -> None:
    party = Party(name="Karim Benali", address=None, yours=True)
    text = "Signed by Karim Benali. Mr Benali agrees. Karim too."

    assert spans(text, (party,)) == [
        (10, 15),
        (10, 22),
        (16, 22),
        (24, 33),
        (27, 33),
        (42, 47),
    ]


def test_a_short_name_from_a_defined_term() -> None:
    text = 'Brightline Studio Ltd ("the Studio") and the Agency.'
    terms = (
        DefinedTerm(term="Studio", definition=Span(start=0, end=len(text)), uses=()),
        DefinedTerm(term="Agency", definition=Span(start=0, end=len(text)), uses=()),
    )

    assert spans(text, (BRIGHTLINE,), terms) == [(0, 17), (0, 21), (11, 17), (28, 34)]


def test_a_role_is_not_a_short_name() -> None:
    text = 'Brightline Studio Ltd ("the Studio") and the Agency.'
    terms = (DefinedTerm(term="Agency", definition=Span(start=0, end=len(text)), uses=()),)

    assert spans(text, (BRIGHTLINE,), terms) == [(0, 17), (0, 21)]


def test_address_and_its_first_line() -> None:
    party = Party(name="X Ltd", address="14 Harbour Street, Leeds LS1 4AB", yours=False)
    text = "at 14 Harbour Street, Leeds LS1 4AB; or 14 Harbour Street."
    results = [
        (suggestion.span.start, suggestion.span.end)
        for suggestion in find_party_details(text, (party,), ())
        if suggestion.kind is ADDRESS
    ]

    assert results == [(3, 20), (3, 35), (40, 57)]


def test_no_address_when_there_is_none() -> None:
    no_address = Party(name="X Ltd", address=None, yours=False)
    blank_address = Party(name="X Ltd", address="  ", yours=False)

    assert spans("at 14 Harbour Street.", (no_address,)) == []
    assert spans("x", (blank_address,)) == []


def test_empty_name_raises() -> None:
    party = Party(name=" ", address=None, yours=False)

    with pytest.raises(ValueError) as error:
        find_party_details("x", (party,), ())

    assert str(error.value) == "privacy: party name is empty"


def test_no_parties_gives_nothing() -> None:
    assert find_party_details("x", (), ()) == ()


def test_source_is_party_details() -> None:
    suggestions = find_party_details(
        "Brightline Studio Ltd and brightline studio limited.", (BRIGHTLINE,), ()
    )

    assert all(suggestion.source is PiiSource.PARTY_DETAILS for suggestion in suggestions)


def test_a_term_defined_in_another_sentence_is_not_a_short_name() -> None:
    text = 'Brightline Services Ltd pays. "Services" means the work.'
    party = Party(name="Brightline Services Ltd", address=None, yours=False)
    definition = Span(start=text.index('"Services"'), end=len(text))
    terms = (DefinedTerm(term="Services", definition=definition, uses=()),)

    assert spans(text, (party,), terms) == [(0, 19), (0, 23)]


def test_a_one_word_form_needs_a_capital() -> None:
    party = Party(name="Karim Benali", address=None, yours=True)

    assert spans("karim benali signs. karim signs. Karim signs.", (party,)) == [
        (0, 12),
        (33, 38),
    ]


def test_a_month_is_not_a_name() -> None:
    party = Party(name="May Lee", address=None, yours=False)

    assert spans("Lee signed on 1 May 2026. May Lee signs.", (party,)) == [
        (0, 3),
        (26, 33),
        (30, 33),
    ]


def test_a_common_word_is_not_a_name() -> None:
    party = Party(name="Will Price", address=None, yours=False)

    assert spans("Will pay. Will Price signs. Price is 5.", (party,)) == [(10, 20)]


def test_layer3_party_rose_hope() -> None:
    party = Party(name="Rose Hope", address=None, yours=False)

    assert spans("Rose Hope signs. Hope is not a term. Contact Hope.", (party,)) == [
        (0, 9),
        (5, 9),
        (45, 49),
    ]


def test_hard_list_unchanged_will_price() -> None:
    party = Party(name="Will Price", address=None, yours=False)

    assert spans("Will pay. Will Price signs. Price is 5. Contact Will.", (party,)) == [(10, 20)]


def test_a_company_name_that_is_only_a_suffix_gives_nothing() -> None:
    assert spans("Ltd pays.", (Party(name="Ltd", address=None, yours=False),)) == []


def test_a_given_key_gives_the_same_result() -> None:
    text = "Brightline Studio Ltd and brightline studio limited."

    assert find_party_details(
        text, (BRIGHTLINE,), (), key=fold_for_matching(text)
    ) == find_party_details(text, (BRIGHTLINE,), ())
