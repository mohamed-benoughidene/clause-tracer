"""The governing-law place is kept (S4-M3-T3)."""

from clause_tracer.core import PiiSource, PlaceholderKind
from clause_tracer.privacy.places import governing_law_places
from clause_tracer.privacy.resolve import cut_in_places
from clause_tracer.privacy.tests.case_builder import suggestion

PERSON = PlaceholderKind.PERSON
COMPANY = PlaceholderKind.COMPANY
ADDRESS = PlaceholderKind.ADDRESS
EMAIL = PlaceholderKind.EMAIL
PHONE = PlaceholderKind.PHONE
ID = PlaceholderKind.ID
BANK = PlaceholderKind.BANK
NER = PiiSource.NER
RULE = PiiSource.RULE
PATTERN = PiiSource.PATTERN
PARTY_DETAILS = PiiSource.PARTY_DETAILS
USER = PiiSource.USER

CUT_TEXT = "governed by the laws of England and Wales, Hall Road."


def _place_texts(text: str) -> tuple[str, ...]:
    return tuple(text[span.start : span.end] for span in governing_law_places(text))


def _cut(
    text: str, kind: PlaceholderKind, source: PiiSource
) -> tuple[tuple[str, int, int, PlaceholderKind, PiiSource], ...]:
    found = suggestion(text, "Wales, Hall Road", kind, source)
    places = governing_law_places(text)
    return tuple(
        (
            text[item.span.start : item.span.end],
            item.span.start,
            item.span.end,
            item.kind,
            item.source,
        )
        for item in cut_in_places(text, (found,), places)
    )


def test_finds_the_place() -> None:
    text = "This Agreement is governed by the laws of England and Wales."

    assert _place_texts(text) == ("England and Wales",)


def test_finds_the_other_wording() -> None:
    text = "governed by and construed in accordance with the law of Scotland."

    assert _place_texts(text) == ("Scotland",)


def test_no_place_without_the_phrase() -> None:
    assert _place_texts("Disputes go to Leeds.") == ()


def test_the_place_stops_at_a_full_stop() -> None:
    text = "governed by the laws of England and Wales. Next."

    assert _place_texts(text) == ("England and Wales",)


def test_cut_in_places_drops_a_detector_match() -> None:
    text = "governed by the laws of England and Wales. Fly to Leeds."
    england = suggestion(text, "England", ADDRESS, NER)
    leeds = suggestion(text, "Leeds", ADDRESS, NER)

    result = cut_in_places(text, (england, leeds), governing_law_places(text))

    assert tuple(text[item.span.start : item.span.end] for item in result) == ("Leeds",)


def test_cut_in_places_keeps_party_details_and_user() -> None:
    text = "governed by the laws of England and Wales. Fly to Leeds."
    party = suggestion(text, "England", ADDRESS, PARTY_DETAILS)
    user = suggestion(text, "England", ADDRESS, USER)

    result = cut_in_places(text, (party, user), governing_law_places(text))

    assert result == (party, user)


def test_state_of() -> None:
    text = "This Agreement is governed by the laws of the State of Delaware."

    assert _place_texts(text) == ("State of Delaware",)


def test_republic_of() -> None:
    assert _place_texts("governed by the laws of the Republic of Ireland.") == (
        "Republic of Ireland",
    )


def test_longest_match_england_and_wales() -> None:
    assert _place_texts("governed by the laws of England and Wales, Hall Road.") == (
        "England and Wales",
    )


def test_england_alone() -> None:
    assert _place_texts("governed by the laws of England.") == ("England",)


def test_wales_alone() -> None:
    assert _place_texts("governed by the laws of Wales.") == ("Wales",)


def test_scotland_alone() -> None:
    assert _place_texts("governed by the laws of Scotland.") == ("Scotland",)


def test_northern_ireland_alone() -> None:
    assert _place_texts("governed by the laws of Northern Ireland.") == ("Northern Ireland",)


def test_the_place_stops_at_england() -> None:
    text = "governed by the laws of England Sarah Jones signs. Signed by Sarah Jones."

    assert _place_texts(text) == ("England",)


def test_nothing_after_the_longest_match() -> None:
    text = "governed by the laws of Scotland and England and Wales"

    assert _place_texts(text) == ("Scotland",)


def test_us_state_bare_is_not_listed() -> None:
    assert _place_texts("governed by the laws of New York") == ()


def test_commonwealth_is_not_listed() -> None:
    assert _place_texts("governed by the laws of the Commonwealth of Virginia") == ()


def test_washington_dc_is_not_listed() -> None:
    assert _place_texts("governed by the laws of Washington, D.C.") == ()


def test_hong_kong_sar_is_not_listed() -> None:
    assert _place_texts("governed by the laws of Hong Kong SAR") == ()


def test_au_state_of_victoria() -> None:
    assert _place_texts("governed by the laws of the State of Victoria") == ("State of Victoria",)


def test_ca_province_of_ontario() -> None:
    assert _place_texts("governed by the laws of the Province of Ontario") == (
        "Province of Ontario",
    )


def test_kingdom_of_spain() -> None:
    assert _place_texts("governed by the laws of the Kingdom of Spain") == ("Kingdom of Spain",)


def test_state_of_new_york_usa() -> None:
    assert _place_texts("governed by the law of the State of New York, USA") == (
        "State of New York",
    )


def test_canadian_province() -> None:
    assert _place_texts("governed by the laws of Ontario") == ("Ontario",)


def test_australian_state() -> None:
    assert _place_texts("governed by the laws of New South Wales") == ("New South Wales",)


def test_outside_the_list_narnia() -> None:
    assert _place_texts("governed by the laws of Narnia") == ()


def test_jersey_is_not_listed() -> None:
    assert _place_texts("governed by the laws of Jersey") == ()


def test_guernsey_is_not_listed() -> None:
    assert _place_texts("governed by the laws of Guernsey") == ()


def test_isle_of_man_is_not_listed() -> None:
    assert _place_texts("governed by the laws of the Isle of Man") == ()


def test_hong_kong_is_not_listed() -> None:
    assert _place_texts("governed by the laws of Hong Kong") == ()


def test_dc_is_not_listed() -> None:
    assert _place_texts("governed by the laws of the District of Columbia") == ()


def test_courts_of_leeds_is_not_a_place() -> None:
    assert _place_texts("Disputes go to the courts of Leeds.") == ()


def test_cut_at_the_place_address_rule() -> None:
    assert _cut(CUT_TEXT, ADDRESS, RULE) == ((", Hall Road", 41, 52, ADDRESS, RULE),)


def test_person_stays_whole_at_the_place_ner() -> None:
    assert _cut(CUT_TEXT, PERSON, NER) == (("Wales, Hall Road", 36, 52, PERSON, NER),)


def test_company_stays_whole_at_the_place_rule() -> None:
    assert _cut(CUT_TEXT, COMPANY, RULE) == (("Wales, Hall Road", 36, 52, COMPANY, RULE),)


def test_person_stays_whole_at_the_place_rule() -> None:
    assert _cut(CUT_TEXT, PERSON, RULE) == (("Wales, Hall Road", 36, 52, PERSON, RULE),)


def test_company_stays_whole_at_the_place_ner() -> None:
    assert _cut(CUT_TEXT, COMPANY, NER) == (("Wales, Hall Road", 36, 52, COMPANY, NER),)


def test_cut_at_the_place_address_pattern() -> None:
    assert _cut(CUT_TEXT, ADDRESS, PATTERN) == ((", Hall Road", 41, 52, ADDRESS, PATTERN),)


def test_cut_at_the_place_address_ner() -> None:
    assert _cut(CUT_TEXT, ADDRESS, NER) == ((", Hall Road", 41, 52, ADDRESS, NER),)


def test_cut_at_the_place_email_ner() -> None:
    assert _cut(CUT_TEXT, EMAIL, NER) == ((", Hall Road", 41, 52, EMAIL, NER),)


def test_cut_at_the_place_phone_pattern() -> None:
    assert _cut(CUT_TEXT, PHONE, PATTERN) == ((", Hall Road", 41, 52, PHONE, PATTERN),)


def test_cut_at_the_place_id_pattern() -> None:
    assert _cut(CUT_TEXT, ID, PATTERN) == ((", Hall Road", 41, 52, ID, PATTERN),)


def test_cut_at_the_place_bank_pattern() -> None:
    assert _cut(CUT_TEXT, BANK, PATTERN) == ((", Hall Road", 41, 52, BANK, PATTERN),)


def test_a_span_inside_the_place_vanishes() -> None:
    found = suggestion(CUT_TEXT, "England and Wales", ADDRESS, NER)

    assert cut_in_places(CUT_TEXT, (found,), governing_law_places(CUT_TEXT)) == ()


def test_party_details_stays_whole_across_the_place() -> None:
    assert _cut(CUT_TEXT, ADDRESS, PARTY_DETAILS) == (
        ("Wales, Hall Road", 36, 52, ADDRESS, PARTY_DETAILS),
    )


def test_user_stays_whole_across_the_place() -> None:
    assert _cut(CUT_TEXT, ADDRESS, USER) == (("Wales, Hall Road", 36, 52, ADDRESS, USER),)
