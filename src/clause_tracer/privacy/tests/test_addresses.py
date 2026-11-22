"""Addresses: street-anchored and built backwards from a postcode (S4-M2-T6)."""

from clause_tracer.privacy.addresses import find_addresses


def spans(text: str) -> list[tuple[int, int]]:
    return [(suggestion.span.start, suggestion.span.end) for suggestion in find_addresses(text)]


def texts(text: str) -> list[str]:
    return [
        text[suggestion.span.start : suggestion.span.end] for suggestion in find_addresses(text)
    ]


def test_uk_address() -> None:
    assert spans("Send it to 221B Baker Street, London NW1 6XE.") == [(11, 44)]


def test_street_with_and_without_a_town() -> None:
    assert spans("at 5 High Road and 10 Downing Street, London, UK.") == [(3, 14), (19, 48)]


def test_us_style_address() -> None:
    assert spans("1 Main St, Springfield 12345, USA") == [(0, 33)]


def test_street_word_first_address() -> None:
    assert spans("27 Rue Didouche Mourad, Algiers 16000, Algeria") == [(0, 46)]


def test_amounts_and_durations_are_kept() -> None:
    assert spans("in 12 months, Leeds") == []
    assert spans("Week 2 £1,600") == []


def test_a_bracket_ends_the_address() -> None:
    assert spans('14 Harbour Street, Leeds LS1 4AB ("the Agency")') == [(0, 32)]


def test_postcode_after_a_comma() -> None:
    assert texts("Send it to 12 High Road, Leeds, LS1 4AB today.") == [
        "12 High Road, Leeds, LS1 4AB"
    ]


def test_bare_way_is_no_address() -> None:
    assert texts("Keep 5 Way clear.") == []


def test_bare_court_is_no_address() -> None:
    assert texts("Keep 2 Court clear.") == []


def test_way_of_life() -> None:
    assert texts("at 5 Way of life") == []


def test_court_days() -> None:
    assert texts("within 2 Court days") == []


def test_us_suite_whole() -> None:
    assert texts("Deliver to Suite 400, 1 Main Street, Austin, TX 78701 by June.") == [
        "Suite 400, 1 Main Street, Austin, TX 78701"
    ]


def test_flat_chain_with_country() -> None:
    assert texts("Flat 2, 12 High Road, Leeds, LS1 4AB, United Kingdom") == [
        "Flat 2, 12 High Road, Leeds, LS1 4AB, United Kingdom"
    ]


def test_unit_without_a_street_word() -> None:
    assert texts("Unit 4, Alpha Park, Leeds, LS1 4AB") == ["Unit 4, Alpha Park, Leeds, LS1 4AB"]


def test_us_state_zip_usa() -> None:
    assert texts("Suite 400, 1 Main St, Springfield, IL 62704, USA") == [
        "Suite 400, 1 Main St, Springfield, IL 62704, USA"
    ]


def test_a_date_is_no_house_number_postcode_alone() -> None:
    assert texts("Within 30 days of 1 May 2026, ship to LS1 4AB") == ["LS1 4AB"]


def test_previous_sentence_is_cut_off() -> None:
    assert texts("Pay 5 apples to Bob. He lives at 5 High St, Leeds LS1 4AB") == [
        "5 High St, Leeds LS1 4AB"
    ]


def test_canadian_postcode() -> None:
    assert texts("Ship to 100 King Street, Toronto, ON M5V 3L9, Canada") == [
        "100 King Street, Toronto, ON M5V 3L9, Canada"
    ]


def test_po_box() -> None:
    assert texts("PO Box 12, Leeds LS1 4AB") == ["PO Box 12, Leeds LS1 4AB"]


def test_no_start_token_postcode_alone() -> None:
    assert texts("Alpha Park, Leeds LS1 4AB") == ["LS1 4AB"]


def test_cue_phrase_starts_the_address() -> None:
    assert texts("whose address is Alpha House, 4 Mill Lane, Leeds LS1 4AB") == [
        "Alpha House, 4 Mill Lane, Leeds LS1 4AB"
    ]


def test_semicolon_ends_the_chain() -> None:
    assert texts("Pay Bob; 5 High St, Leeds LS1 4AB") == ["5 High St, Leeds LS1 4AB"]


def test_address_chain_with_7_segments_keeps_the_last_5_segments() -> None:
    assert texts("Mail 1 Aaaa, Bbbb, Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB") == [
        "Cccc, Dddd, Eeee, Ffff, Leeds LS1 4AB"
    ]


def test_address_chain_with_exactly_5_segments_is_whole() -> None:
    assert texts("Mail 1 Aaaa, Bbbb, Cccc, Dddd, Leeds LS1 4AB") == [
        "1 Aaaa, Bbbb, Cccc, Dddd, Leeds LS1 4AB"
    ]


def test_address_chain_over_120_characters_keeps_the_nearest_segments() -> None:
    assert texts("Mail 1 Aaaa, " + "B" * 100 + ", Cccc, Leeds LS1 4AB") == ["Cccc, Leeds LS1 4AB"]


def test_nearest_segment_over_120_characters_gives_the_postcode_alone() -> None:
    assert texts("Mail 1 Aaaa, " + "Bbbb " * 25 + "Leeds LS1 4AB") == ["LS1 4AB"]


def test_non_ascii_capital_in_a_street() -> None:
    assert spans("5 Müller Street, Köln") == [(0, 21)]
