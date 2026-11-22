"""Group variants into numbered entities (S4-M3-T7)."""

from clause_tracer.core import (
    Document,
    PiiSource,
    PiiSuggestion,
    PlaceholderEntity,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.tests.case_builder import make_case, suggestion

PERSON = PlaceholderKind.PERSON
COMPANY = PlaceholderKind.COMPANY
ADDRESS = PlaceholderKind.ADDRESS
EMAIL = PlaceholderKind.EMAIL
PHONE = PlaceholderKind.PHONE
ID = PlaceholderKind.ID
RULE = PiiSource.RULE


def _read(
    document: Document, entities: tuple[PlaceholderEntity, ...]
) -> list[tuple[str, list[str]]]:
    return [
        (
            entity.id,
            [document.text[span.start : span.end] for span in entity.spans],
        )
        for entity in entities
    ]


def test_variants_share_one_entity() -> None:
    text = "Sarah Jones then Ms Jones and Mr Smith and Smith."
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "Sarah Jones", PERSON, RULE),
        suggestion(text, "Ms Jones", PERSON, RULE),
        suggestion(text, "Mr Smith", PERSON, RULE),
        suggestion(text, "Smith", PERSON, RULE, 2),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("person-1", ["Sarah Jones", "Ms Jones"]),
        ("person-2", ["Mr Smith", "Smith"]),
    ]


def test_a_short_form_of_two_names_gets_its_own_entity() -> None:
    text = "Ms Jones and Sarah Jones and Sarah and Tom Jones."
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "Ms Jones", PERSON, RULE),
        suggestion(text, "Sarah Jones", PERSON, RULE),
        suggestion(text, "Sarah", PERSON, RULE, 2),
        suggestion(text, "Tom Jones", PERSON, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("person-1", ["Ms Jones"]),
        ("person-2", ["Sarah Jones", "Sarah"]),
        ("person-3", ["Tom Jones"]),
    ]


def test_a_company_suffix_is_ignored() -> None:
    text = "Brightline Studio Ltd, Brightline Studio and Brightline Studio Limited."
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "Brightline Studio Ltd", COMPANY, RULE),
        suggestion(text, "Brightline Studio", COMPANY, RULE, 2),
        suggestion(text, "Brightline Studio Limited", COMPANY, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("company-1", ["Brightline Studio Ltd", "Brightline Studio", "Brightline Studio Limited"])
    ]


def test_emails_differ_only_by_case() -> None:
    text = "a@b.com and A@B.com"
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "a@b.com", EMAIL, RULE),
        suggestion(text, "A@B.com", EMAIL, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("email-1", ["a@b.com", "A@B.com"])
    ]


def test_phones_compare_by_digits() -> None:
    text = "020 7946 0958 and 0207946 0958"
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "020 7946 0958", PHONE, RULE),
        suggestion(text, "0207946 0958", PHONE, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("phone-1", ["020 7946 0958", "0207946 0958"])
    ]


def test_ids_compare_by_letters_and_digits() -> None:
    text = "ID 123-45 and id 12345"
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "ID 123-45", ID, RULE),
        suggestion(text, "id 12345", ID, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("id-1", ["ID 123-45", "id 12345"])
    ]


def test_an_address_line_joins_its_full_address() -> None:
    text = "14 Harbour Street and 14 Harbour Street, Leeds LS1 4AB"
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "14 Harbour Street", ADDRESS, RULE),
        suggestion(text, "14 Harbour Street, Leeds LS1 4AB", ADDRESS, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("address-1", ["14 Harbour Street", "14 Harbour Street, Leeds LS1 4AB"])
    ]


def test_numbers_run_by_kind_in_order_of_first_place() -> None:
    text = "Bob and Acme Ltd and Zed"
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "Bob", PERSON, RULE),
        suggestion(text, "Acme Ltd", COMPANY, RULE),
        suggestion(text, "Zed", PERSON, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("person-1", ["Bob"]),
        ("company-1", ["Acme Ltd"]),
        ("person-2", ["Zed"]),
    ]


def test_spans_are_sorted() -> None:
    text = "Sarah Jones then Ms Jones and Mr Smith and Smith."
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "Smith", PERSON, RULE, 2),
        suggestion(text, "Mr Smith", PERSON, RULE),
        suggestion(text, "Ms Jones", PERSON, RULE),
        suggestion(text, "Sarah Jones", PERSON, RULE),
    )

    assert _read(document, group_entities(document, suggestions)) == [
        ("person-1", ["Sarah Jones", "Ms Jones"]),
        ("person-2", ["Mr Smith", "Smith"]),
    ]


def test_overlapping_suggestions_raise() -> None:
    text = "abcdefghij"
    document = make_case([text]).document
    suggestions = (
        PiiSuggestion(span=Span(start=0, end=5), kind=PERSON, source=RULE),
        PiiSuggestion(span=Span(start=3, end=8), kind=PERSON, source=RULE),
    )

    try:
        group_entities(document, suggestions)
    except ValueError as error:
        assert str(error) == "privacy: suggestions overlap"
        return
    raise AssertionError("overlapping suggestions must raise")


def test_a_span_outside_the_text_raises() -> None:
    document = make_case(["abc"]).document
    past_end = PiiSuggestion(span=Span(start=0, end=99), kind=PERSON, source=RULE)
    before_start = PiiSuggestion(span=Span(start=-1, end=2), kind=PERSON, source=RULE)

    for bad in (past_end, before_start):
        try:
            group_entities(document, (bad,))
        except ValueError:
            continue
        raise AssertionError("a span outside the text must raise")


def test_no_suggestions() -> None:
    document = make_case(["abc"]).document

    assert group_entities(document, ()) == ()


def test_an_honorific_alone_groups_by_its_text() -> None:
    text = "Ms and Ms"
    document = make_case([text]).document
    suggestions = (
        suggestion(text, "Ms", PERSON, RULE),
        suggestion(text, "Ms", PERSON, RULE, 2),
    )

    assert _read(document, group_entities(document, suggestions)) == [("person-1", ["Ms", "Ms"])]
