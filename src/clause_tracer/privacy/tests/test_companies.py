"""Company names by their suffix (S4-M2-T5)."""

from clause_tracer.core import PiiSource, PlaceholderKind
from clause_tracer.privacy.companies import find_companies


def found(text: str) -> list[tuple[str, int, int]]:
    return [
        (
            text[suggestion.span.start : suggestion.span.end],
            suggestion.span.start,
            suggestion.span.end,
        )
        for suggestion in find_companies(text)
    ]


def test_finds_a_company_by_its_suffix() -> None:
    assert found("The Agency and Brightline Studio Ltd will pay Smith & Sons Ltd.") == [
        ("Brightline Studio Ltd", 15, 36),
        ("Smith & Sons Ltd", 46, 62),
    ]


def test_a_leading_the_is_dropped() -> None:
    assert found("The Acme Limited pays.") == [("Acme Limited", 4, 16)]


def test_lower_case_words_before_a_name_are_left() -> None:
    assert found("See the Acme Limited, and Bank of Wales Plc.") == [
        ("Acme Limited", 8, 20),
        ("Bank of Wales Plc", 26, 43),
    ]


def test_other_suffixes() -> None:
    assert found("Acme Co. and Foo AG") == [
        ("Acme Co", 0, 7),
        ("Foo AG", 13, 19),
    ]


def test_a_role_is_not_a_company() -> None:
    assert found("The Developer pays.") == []


def test_a_lead_word_and_a_suffix_is_not_a_company() -> None:
    assert found("The Ltd pays.") == []


def test_a_line_break_ends_the_name() -> None:
    assert found("Brightline\nStudio Ltd") == [("Studio Ltd", 11, 21)]


def test_kind_and_source() -> None:
    suggestions = find_companies("The Agency and Brightline Studio Ltd will pay Smith & Sons Ltd.")

    assert all(suggestion.kind is PlaceholderKind.COMPANY for suggestion in suggestions)
    assert all(suggestion.source is PiiSource.RULE for suggestion in suggestions)


def test_limited_warranty_is_no_company() -> None:
    assert found("Provider Limited Warranty applies.") == []


def test_hyphen_word_is_no_company() -> None:
    assert found("The Co-operative Bank Co-operation applies.") == []


def test_a_leading_verb_is_not_in_the_span() -> None:
    assert found("Pay Acme Ltd now.") == [("Acme Ltd", 4, 12)]


def test_and_is_a_connector() -> None:
    assert found("Smith and Sons Ltd") == [("Smith and Sons Ltd", 0, 18)]


def test_dotted_forms_and_gmbh_co_kg_whole() -> None:
    assert found("Acme Holdings Inc. and Foo S.A. and Bar GmbH & Co. KG") == [
        ("Acme Holdings Inc", 0, 17),
        ("Foo S.A.", 23, 31),
        ("Bar GmbH & Co. KG", 36, 53),
    ]


def test_two_companies_joined_by_and_stay_two() -> None:
    assert found("Acme Ltd and Foo Ltd pay") == [
        ("Acme Ltd", 0, 8),
        ("Foo Ltd", 13, 20),
    ]


def test_role_and_name_are_not_glued() -> None:
    assert found("The Agency and Brightline Studio Ltd will pay") == [
        ("Brightline Studio Ltd", 15, 36)
    ]


def test_extended_suffixes_lp() -> None:
    assert found("The Company and Acme LP sign") == [("Acme LP", 16, 23)]


def test_extended_suffixes_corporation_incorporated() -> None:
    assert found("Acme Corporation and Foo Incorporated") == [
        ("Acme Corporation", 0, 16),
        ("Foo Incorporated", 21, 37),
    ]


def test_extended_suffixes_srl_spa_oy_ug() -> None:
    assert found("Foo SRL, Bar SpA, Baz Oy, Qux UG") == [
        ("Foo SRL", 0, 7),
        ("Bar SpA", 9, 16),
        ("Baz Oy", 18, 24),
        ("Qux UG", 26, 32),
    ]


def test_pte_ltd_whole() -> None:
    assert found("Acme Pte Ltd pays") == [("Acme Pte Ltd", 0, 12)]


def test_company_group_holdings_are_not_suffixes() -> None:
    assert found("Acme Group pays Beta Holdings and Gamma Company") == []


def test_comma_after_limited() -> None:
    assert found("Acme Limited, a company, signs.") == [("Acme Limited", 0, 12)]
