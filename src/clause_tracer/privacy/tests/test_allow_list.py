"""The allow-list from the defined terms (S4-M3-T2)."""

from clause_tracer.core import (
    DefinedTerm,
    PiiSource,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy.resolve import (
    allowed_term_texts,
    drop_allowed,
    normalised_text,
)
from clause_tracer.privacy.tests.case_builder import suggestion

COMPANY = PlaceholderKind.COMPANY
PERSON = PlaceholderKind.PERSON
ADDRESS = PlaceholderKind.ADDRESS
NER = PiiSource.NER
RULE = PiiSource.RULE
PARTY_DETAILS = PiiSource.PARTY_DETAILS
USER = PiiSource.USER

MERCURY_TEXT = 'Mercury Logistics Ltd ("x") is the party.'


def _term(name: str) -> DefinedTerm:
    return DefinedTerm(term=name, definition=Span(start=0, end=0), uses=())


def _mercury_term(name: str) -> DefinedTerm:
    return DefinedTerm(term=name, definition=Span(start=0, end=len(MERCURY_TEXT)), uses=())


def _mercury_allowed(
    name: str, *, kind: PlaceholderKind = COMPANY, source: PiiSource = RULE
) -> bool:
    found = suggestion(MERCURY_TEXT, "Mercury Logistics Ltd", kind, source)
    allowed = allowed_term_texts(MERCURY_TEXT, (_mercury_term(name),), (found,))
    return normalised_text(name) in allowed


def test_a_term_is_allowed_by_default() -> None:
    assert allowed_term_texts("x", [_term("Agency")], ()) == frozenset({"agency"})


def test_a_term_that_a_party_finder_matches_is_not_allowed() -> None:
    text = "Brightline x"
    found = suggestion(text, "Brightline", COMPANY, PARTY_DETAILS)

    result = allowed_term_texts(text, [_term("Brightline"), _term("Agency")], (found,))

    assert result == frozenset({"agency"})


def test_a_term_that_a_name_rule_matches_is_not_allowed() -> None:
    text = "Jones x"
    found = suggestion(text, "Jones", PERSON, RULE)

    assert allowed_term_texts(text, [_term("Jones")], (found,)) == frozenset()


def test_a_detector_match_does_not_drop_a_term() -> None:
    text = "Jones x"
    found = suggestion(text, "Jones", PERSON, NER)

    assert allowed_term_texts(text, [_term("Jones")], (found,)) == frozenset({"jones"})


def test_an_address_rule_does_not_drop_a_term() -> None:
    text = "Jones x"
    found = suggestion(text, "Jones", ADDRESS, RULE)

    assert allowed_term_texts(text, [_term("Jones")], (found,)) == frozenset({"jones"})


def test_drop_allowed_drops_a_role() -> None:
    text = "Pay the Agency. The Agency's rules apply to Karim."
    agency = suggestion(text, "Agency", COMPANY, NER)
    karim = suggestion(text, "Karim", PERSON, NER)

    assert drop_allowed(text, (agency, karim), frozenset({"agency"})) == (karim,)


def test_drop_allowed_reads_the_and_a_possessive() -> None:
    text = "Pay Agency. Next The Agency's rules."
    agency = suggestion(text, "The Agency's", COMPANY, NER)

    assert drop_allowed(text, (agency,), frozenset({"agency"})) == ()


def test_drop_allowed_keeps_party_details_and_user() -> None:
    text = "Agency Agency"
    party = suggestion(text, "Agency", COMPANY, PARTY_DETAILS)
    user = suggestion(text, "Agency", COMPANY, USER, 2)

    assert drop_allowed(text, (party, user), frozenset({"agency"})) == (party, user)


def test_normalised_text() -> None:
    assert normalised_text("The Agency’s") == "agency"
    assert normalised_text("  THE agency ") == "agency"
    assert normalised_text("theatre") == "theatre"
    assert normalised_text("the") == "the"


def test_mercury_is_a_name_not_a_role() -> None:
    assert not _mercury_allowed("Mercury")


def test_a_core_word_is_a_name() -> None:
    assert not _mercury_allowed("Logistics")


def test_a_role_with_no_word_in_common_stays_allowed() -> None:
    assert _mercury_allowed("Agency")


def test_company_and_effective_date_stay_allowed() -> None:
    assert _mercury_allowed("Company")
    assert _mercury_allowed("Effective Date")


def test_a_ner_suggestion_does_not_make_a_term_a_name() -> None:
    assert _mercury_allowed("Mercury", source=NER)
