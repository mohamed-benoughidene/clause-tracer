"""Resolve overlaps by source (S4-M3-T4)."""

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy.resolve import resolve_overlaps
from clause_tracer.privacy.tests.case_builder import suggestion

PERSON = PlaceholderKind.PERSON
COMPANY = PlaceholderKind.COMPANY
ADDRESS = PlaceholderKind.ADDRESS
PHONE = PlaceholderKind.PHONE
ID = PlaceholderKind.ID
BANK = PlaceholderKind.BANK
NER = PiiSource.NER
RULE = PiiSource.RULE
PATTERN = PiiSource.PATTERN
PARTY_DETAILS = PiiSource.PARTY_DETAILS
USER = PiiSource.USER


def _read(
    text: str, result: tuple[PiiSuggestion, ...]
) -> list[tuple[str, int, int, PlaceholderKind, PiiSource]]:
    return [
        (
            text[item.span.start : item.span.end],
            item.span.start,
            item.span.end,
            item.kind,
            item.source,
        )
        for item in result
    ]


def _double(
    text: str, kind: PlaceholderKind, source: PiiSource
) -> tuple[PiiSuggestion, PiiSuggestion]:
    first = PiiSuggestion(span=Span(start=0, end=8), kind=kind, source=source)
    second = PiiSuggestion(span=Span(start=3, end=11), kind=kind, source=source)
    return first, second


def test_a_contained_lower_span_vanishes() -> None:
    text = "Brightline Studio Ltd"
    party = suggestion(text, text, COMPANY, PARTY_DETAILS)
    studio = suggestion(text, "Studio", PERSON, NER)

    assert _read(text, resolve_overlaps(text, (party, studio))) == [
        ("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS)
    ]


def test_a_lower_span_that_sticks_out_is_cut() -> None:
    text = "Brightline Studio Ltd, Leeds"
    party = suggestion(text, "Brightline Studio Ltd", COMPANY, PARTY_DETAILS)
    address = suggestion(text, "Studio Ltd, Leeds", ADDRESS, NER)

    assert _read(text, resolve_overlaps(text, (party, address))) == [
        ("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS),
        (", Leeds", 21, 28, ADDRESS, NER),
    ]


def test_a_punctuation_only_piece_is_dropped() -> None:
    text = "Brightline Studio Ltd,"
    party = suggestion(text, "Brightline Studio Ltd", COMPANY, PARTY_DETAILS)
    address = suggestion(text, "Studio Ltd,", ADDRESS, NER)

    assert _read(text, resolve_overlaps(text, (party, address))) == [
        ("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS)
    ]


def test_a_span_is_cut_on_both_sides() -> None:
    text = "Sarah Jones Smith"
    jones = suggestion(text, "Jones", PERSON, RULE)
    whole = suggestion(text, text, PERSON, NER)

    assert _read(text, resolve_overlaps(text, (jones, whole))) == [
        ("Sarah", 0, 5, PERSON, NER),
        ("Jones", 6, 11, PERSON, RULE),
        ("Smith", 12, 17, PERSON, NER),
    ]


def test_longer_wins_within_a_source() -> None:
    text = "Brightline Studio Ltd"
    short = suggestion(text, "Brightline Studio", COMPANY, PARTY_DETAILS)
    whole = suggestion(text, text, COMPANY, PARTY_DETAILS)

    assert _read(text, resolve_overlaps(text, (short, whole))) == [
        ("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS)
    ]


def test_user_beats_party_details() -> None:
    text = "Sarah Jones"
    user = suggestion(text, "Jones", PERSON, USER)
    party = suggestion(text, text, PERSON, PARTY_DETAILS)

    assert _read(text, resolve_overlaps(text, (user, party))) == [
        ("Sarah", 0, 5, PERSON, PARTY_DETAILS),
        ("Jones", 6, 11, PERSON, USER),
    ]


def test_touching_spans_stay_apart() -> None:
    text = "SamLee"
    sam = suggestion(text, "Sam", PERSON, NER)
    lee = suggestion(text, "Lee", PERSON, NER)

    assert _read(text, resolve_overlaps(text, (sam, lee))) == [
        ("Sam", 0, 3, PERSON, NER),
        ("Lee", 3, 6, PERSON, NER),
    ]


def test_equal_spans_keep_the_first_kind() -> None:
    text = "Sam"
    address = suggestion(text, text, ADDRESS, NER)
    person = suggestion(text, text, PERSON, NER)

    assert _read(text, resolve_overlaps(text, (address, person))) == [("Sam", 0, 3, PERSON, NER)]


def test_result_is_sorted_by_start() -> None:
    text = "aa bb cc"
    cc = suggestion(text, "cc", PERSON, NER)
    aa = suggestion(text, "aa", PERSON, NER)

    assert _read(text, resolve_overlaps(text, (cc, aa))) == [
        ("aa", 0, 2, PERSON, NER),
        ("cc", 6, 8, PERSON, NER),
    ]


def test_no_suggestions() -> None:
    assert resolve_overlaps("x", ()) == ()


def test_ner_union_sarah_jo_and_ah_jones() -> None:
    text = "Sarah Jones"
    first = suggestion(text, "Sarah Jo", PERSON, NER)
    second = suggestion(text, "ah Jones", PERSON, NER)

    assert _read(text, resolve_overlaps(text, (first, second))) == [
        ("Sarah Jones", 0, 11, PERSON, NER)
    ]


def test_ner_union_chain_of_three() -> None:
    text = "abcdefghij"
    first = PiiSuggestion(span=Span(start=0, end=4), kind=PERSON, source=NER)
    second = PiiSuggestion(span=Span(start=3, end=7), kind=PERSON, source=NER)
    third = PiiSuggestion(span=Span(start=6, end=10), kind=PERSON, source=NER)

    assert _read(text, resolve_overlaps(text, (first, second, third))) == [
        ("abcdefghij", 0, 10, PERSON, NER)
    ]


def test_ner_union_needs_the_same_kind() -> None:
    text = "Sarah Jones"
    person = suggestion(text, "Sarah Jo", PERSON, NER)
    address = suggestion(text, "ah Jones", ADDRESS, NER)

    assert _read(text, resolve_overlaps(text, (person, address))) == [
        ("Sarah Jo", 0, 8, PERSON, NER),
        ("nes", 8, 11, ADDRESS, NER),
    ]


def test_no_union_for_rule() -> None:
    text = "Sarah Jones"

    assert _read(text, resolve_overlaps(text, _double(text, PERSON, RULE))) == [
        ("Sarah Jo", 0, 8, PERSON, RULE),
        ("nes", 8, 11, PERSON, RULE),
    ]


def test_no_union_for_pattern() -> None:
    text = "Sarah Jones"

    assert _read(text, resolve_overlaps(text, _double(text, PERSON, PATTERN))) == [
        ("Sarah Jo", 0, 8, PERSON, PATTERN),
        ("nes", 8, 11, PERSON, PATTERN),
    ]


def test_no_union_for_party_details() -> None:
    text = "Sarah Jones"

    assert _read(text, resolve_overlaps(text, _double(text, PERSON, PARTY_DETAILS))) == [
        ("Sarah Jo", 0, 8, PERSON, PARTY_DETAILS),
        ("nes", 8, 11, PERSON, PARTY_DETAILS),
    ]


def test_no_union_for_user() -> None:
    text = "Sarah Jones"

    assert _read(text, resolve_overlaps(text, _double(text, PERSON, USER))) == [
        ("Sarah Jo", 0, 8, PERSON, USER),
        ("nes", 8, 11, PERSON, USER),
    ]


def test_tie_id_beats_phone() -> None:
    text = "12-34-56"
    phone = suggestion(text, text, PHONE, PATTERN)
    identity = suggestion(text, text, ID, PATTERN)

    assert _read(text, resolve_overlaps(text, (phone, identity))) == [
        ("12-34-56", 0, 8, ID, PATTERN)
    ]


def test_tie_bank_beats_id_and_phone() -> None:
    text = "12-34-56"
    phone = suggestion(text, text, PHONE, PATTERN)
    identity = suggestion(text, text, ID, PATTERN)
    bank = suggestion(text, text, BANK, PATTERN)

    assert _read(text, resolve_overlaps(text, (phone, identity, bank))) == [
        ("12-34-56", 0, 8, BANK, PATTERN)
    ]


def test_tie_kind_order_otherwise_unchanged() -> None:
    text = "12-34-56"
    address = suggestion(text, text, ADDRESS, PATTERN)
    person = suggestion(text, text, PERSON, PATTERN)

    assert _read(text, resolve_overlaps(text, (address, person))) == [
        ("12-34-56", 0, 8, PERSON, PATTERN)
    ]
