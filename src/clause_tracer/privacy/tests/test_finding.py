"""`find_personal_data`, the step 3 call (S4-M3-T6)."""

from clause_tracer.core import (
    DefinedTerm,
    FakePiiDetector,
    Party,
    PiiSource,
    PiiSuggestion,
    PlaceholderEntity,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.tests.case_builder import make_case, span_of, suggestion

PERSON = PlaceholderKind.PERSON
COMPANY = PlaceholderKind.COMPANY
ADDRESS = PlaceholderKind.ADDRESS
EMAIL = PlaceholderKind.EMAIL
ID = PlaceholderKind.ID
NER = PiiSource.NER
RULE = PiiSource.RULE
PATTERN = PiiSource.PATTERN
PARTY_DETAILS = PiiSource.PARTY_DETAILS


class RecordingDetector:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def find(self, text: str) -> tuple[PiiSuggestion, ...]:
        self.calls.append(text)
        return ()


class FailingDetector:
    def find(self, text: str) -> tuple[PiiSuggestion, ...]:
        raise RuntimeError("detector failed")


def _read5(
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


def _read4(
    text: str, result: tuple[PiiSuggestion, ...]
) -> list[tuple[str, int, int, PlaceholderKind]]:
    return [
        (text[item.span.start : item.span.end], item.span.start, item.span.end, item.kind)
        for item in result
    ]


def _read3(text: str, result: tuple[PiiSuggestion, ...]) -> list[tuple[str, int, int]]:
    return [
        (text[item.span.start : item.span.end], item.span.start, item.span.end) for item in result
    ]


def test_code_finders_run_with_an_empty_detector() -> None:
    case = make_case(["Signed by Tom Jones, Director.", "Mail a@b.com."])

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Tom Jones", 10, 19, PERSON, RULE),
        ("a@b.com", 36, 43, EMAIL, PATTERN),
    ]


def test_the_detector_is_called_once_with_the_whole_text() -> None:
    case = make_case(["Signed by Tom Jones, Director."])
    detector = RecordingDetector()

    find_personal_data(case, detector)

    assert detector.calls == [case.document.text]


def test_a_detector_span_outside_the_text_raises() -> None:
    case = make_case(["Hi."])
    planted = (PiiSuggestion(span=Span(start=0, end=99), kind=PERSON, source=NER),)

    try:
        find_personal_data(case, FakePiiDetector({case.document.text: planted}))
    except ValueError:
        return
    raise AssertionError("a detector span outside the text must raise")


def test_a_detector_name_is_kept() -> None:
    case = make_case(["Zed paid."])
    planted = (suggestion(case.document.text, "Zed", PERSON, NER),)

    result = find_personal_data(case, FakePiiDetector({case.document.text: planted}))

    assert _read5(case.document.text, result) == [("Zed", 0, 3, PERSON, NER)]


def test_a_defined_term_is_not_replaced_when_the_detector_flags_it() -> None:
    case = make_case(
        ["Agency pays."],
        terms=(DefinedTerm(term="Agency", definition=Span(start=0, end=0), uses=()),),
    )
    planted = (suggestion(case.document.text, "Agency", COMPANY, NER),)

    result = find_personal_data(case, FakePiiDetector({case.document.text: planted}))

    assert result == ()


def test_a_party_short_name_is_replaced() -> None:
    case = make_case(
        ['Brightline Studio Ltd ("Brightline") pays.'],
        parties=(Party(name="Brightline Studio Ltd", address=None, yours=False),),
        terms=(DefinedTerm(term="Brightline", definition=Span(start=0, end=42), uses=()),),
    )

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Brightline Studio Ltd", 0, 21, COMPANY, PARTY_DETAILS),
        ("Brightline", 24, 34, COMPANY, PARTY_DETAILS),
    ]


def test_the_governing_law_place_is_kept() -> None:
    case = make_case(["This is governed by the laws of England and Wales."])
    planted = (suggestion(case.document.text, "England and Wales", ADDRESS, NER),)

    result = find_personal_data(case, FakePiiDetector({case.document.text: planted}))

    assert result == ()


def test_a_detector_span_across_a_sentence_is_split() -> None:
    case = make_case(["Pay Sam Lee.", "Then Kim."])
    planted = (suggestion(case.document.text, "Lee. Then", ADDRESS, NER),)

    result = find_personal_data(case, FakePiiDetector({case.document.text: planted}))

    assert _read5(case.document.text, result) == [
        ("Lee.", 8, 12, ADDRESS, NER),
        ("Then", 13, 17, ADDRESS, NER),
    ]


def test_a_detector_error_is_not_caught() -> None:
    case = make_case(["Hi."])

    try:
        find_personal_data(case, FailingDetector())
    except RuntimeError:
        return
    raise AssertionError("a detector error must not be caught")


def test_value_only_id_and_phone_on_the_same_digits_gives_id() -> None:
    case = make_case(["company number 07700900123"])

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [("07700900123", 15, 26, ID, PATTERN)]


def test_bare_mercury_from_the_detector_is_replaced_and_the_role_is_not() -> None:
    text = (
        'Mercury Logistics Ltd ("Mercury") will carry the goods. '
        'Mercury must pay on time. The "Agency" appoints the Agent.'
    )
    mercury_definition = span_of(text, 'Mercury Logistics Ltd ("Mercury") will carry the goods.')
    agency_definition = span_of(text, 'The "Agency" appoints the Agent.')
    case = make_case(
        [text],
        terms=(
            DefinedTerm(term="Mercury", definition=mercury_definition, uses=()),
            DefinedTerm(term="Agency", definition=agency_definition, uses=()),
        ),
    )
    planted = (
        suggestion(text, "Mercury", COMPANY, NER, 3),
        suggestion(text, "Agency", COMPANY, NER),
    )

    result = find_personal_data(case, FakePiiDetector({text: planted}))

    assert _read5(text, result) == [
        ("Mercury Logistics Ltd", 0, 21, COMPANY, RULE),
        ("Mercury", 24, 31, COMPANY, RULE),
        ("Mercury", 56, 63, COMPANY, RULE),
    ]


def test_detector_alone_cannot_decide() -> None:
    text = 'Mercury ("Mercury") will pay. Mercury must pay.'
    definition = span_of(text, 'Mercury ("Mercury") will pay.')
    case = make_case(
        [text],
        terms=(DefinedTerm(term="Mercury", definition=definition, uses=()),),
    )
    planted = (suggestion(text, "Mercury", COMPANY, NER, 3),)

    result = find_personal_data(case, FakePiiDetector({text: planted}))

    assert result == ()


def test_a_person_found_by_rule_makes_the_short_name_a_name() -> None:
    text = (
        'Jane Smith ("Jane") signed. Signed by Jane Smith. Jane pays. The "Company" is Apple Inc.'
    )
    jane_definition = span_of(text, 'Jane Smith ("Jane") signed.')
    company_definition = span_of(text, 'The "Company" is Apple Inc.')
    case = make_case(
        [text],
        terms=(
            DefinedTerm(term="Jane", definition=jane_definition, uses=()),
            DefinedTerm(term="Company", definition=company_definition, uses=()),
        ),
    )
    planted = (suggestion(text, "Company", COMPANY, NER),)

    result = find_personal_data(case, FakePiiDetector({text: planted}))

    assert _read4(text, result) == [
        ("Jane Smith", 0, 10, PERSON),
        ("Jane", 13, 17, PERSON),
        ("Jane Smith", 38, 48, PERSON),
        ("Jane", 50, 54, PERSON),
        ("Apple Inc", 78, 87, COMPANY),
    ]


def test_company_rule_touching_the_place_stays_whole() -> None:
    case = make_case(["governed by the laws of England Brightline Studio Ltd signs."])

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read3(case.document.text, result) == [
        ("England Brightline Studio Ltd", 24, 53),
    ]


def test_every_sarah_jones_is_hidden() -> None:
    case = make_case(
        [
            "This Agreement is governed by the laws of England Sarah Jones signs. "
            "Signed by Sarah Jones."
        ]
    )

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read4(case.document.text, result) == [
        ("Sarah Jones", 50, 61, PERSON),
        ("Sarah Jones", 79, 90, PERSON),
    ]


def test_a_leftover_ending_joins_a_typed_company() -> None:
    case = make_case(
        ["Beta Gadgets, Inc. signs.", "Pay Beta Gadgets now."],
        parties=(Party(name="Beta Gadgets Inc.", address=None, yours=False),),
    )

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Beta Gadgets, Inc", 0, 17, COMPANY, PARTY_DETAILS),
        ("Beta Gadgets", 30, 42, COMPANY, PARTY_DETAILS),
    ]
    assert group_entities(case.document, result) == (
        PlaceholderEntity(
            id="company-1",
            kind=COMPANY,
            number=1,
            spans=(Span(start=0, end=17), Span(start=30, end=42)),
        ),
    )


def test_a_leftover_ending_joins_a_company_typed_with_another_ending() -> None:
    case = make_case(
        ["Beta Gadgets, Inc. signs.", "Pay Beta Gadgets now."],
        parties=(Party(name="Beta Gadgets Ltd", address=None, yours=False),),
    )

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Beta Gadgets, Inc", 0, 17, COMPANY, PARTY_DETAILS),
        ("Beta Gadgets", 30, 42, COMPANY, PARTY_DETAILS),
    ]
    assert group_entities(case.document, result) == (
        PlaceholderEntity(
            id="company-1",
            kind=COMPANY,
            number=1,
            spans=(Span(start=0, end=17), Span(start=30, end=42)),
        ),
    )


def test_a_leftover_ending_joins_a_party_read_as_a_person() -> None:
    case = make_case(
        ["Beta Gadgets, Inc. signs.", "Pay Beta Gadgets now."],
        parties=(Party(name="Beta Gadgets", address=None, yours=False),),
    )

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Beta Gadgets, Inc", 0, 17, PERSON, PARTY_DETAILS),
        ("Beta Gadgets", 30, 42, PERSON, PARTY_DETAILS),
    ]
    assert group_entities(case.document, result) == (
        PlaceholderEntity(
            id="person-1",
            kind=PERSON,
            number=1,
            spans=(Span(start=0, end=17), Span(start=30, end=42)),
        ),
    )


def test_a_short_name_shares_the_company_placeholder() -> None:
    case = make_case(["Beta Gadgets, Inc. signs.", "Pay Beta Gadgets now."])

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Beta Gadgets, Inc", 0, 17, COMPANY, RULE),
        ("Beta Gadgets", 30, 42, COMPANY, RULE),
    ]
    assert [entity.id for entity in group_entities(case.document, result)] == ["company-1"]


def test_a_signed_company_has_one_placeholder() -> None:
    case = make_case(["Signed by Beta Gadgets, Inc.", "Beta Gadgets delivers."])

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Beta Gadgets, Inc", 10, 27, COMPANY, RULE),
        ("Beta Gadgets", 29, 41, COMPANY, RULE),
    ]
    assert [entity.id for entity in group_entities(case.document, result)] == ["company-1"]


def test_a_one_word_short_name_is_hidden() -> None:
    case = make_case(["Gizmotron, Inc. signs.", "Gizmotron pays."])

    result = find_personal_data(case, FakePiiDetector({}))

    assert _read5(case.document.text, result) == [
        ("Gizmotron, Inc", 0, 14, COMPANY, RULE),
        ("Gizmotron", 23, 32, COMPANY, RULE),
    ]
