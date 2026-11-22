"""Email, phone, ID and bank patterns (S4-M2-T2)."""

from clause_tracer.core import PiiSource, PlaceholderKind
from clause_tracer.privacy.patterns import find_patterns

EMAIL = PlaceholderKind.EMAIL
PHONE = PlaceholderKind.PHONE
ID = PlaceholderKind.ID
BANK = PlaceholderKind.BANK


def found(text: str) -> list[tuple[str, int, int, PlaceholderKind]]:
    results: list[tuple[str, int, int, PlaceholderKind]] = []
    for suggestion in find_patterns(text):
        span = suggestion.span
        results.append((text[span.start : span.end], span.start, span.end, suggestion.kind))
    return results


def test_finds_emails() -> None:
    assert found("Mail a@b.com or c.d@e.org.") == [
        ("a@b.com", 5, 12, EMAIL),
        ("c.d@e.org", 16, 25, EMAIL),
    ]


def test_finds_phones() -> None:
    assert found("Call +44 20 7946 0958 or 020 7946 0958.") == [
        ("+44 20 7946 0958", 5, 21, PHONE),
        ("020 7946 0958", 25, 38, PHONE),
    ]


def test_finds_ids_by_keyword() -> None:
    assert found("Our VAT number: GB123456789 and company no. 1234567.") == [
        ("GB123456789", 16, 27, ID),
        ("1234567", 44, 51, ID),
    ]


def test_an_id_stops_before_a_word() -> None:
    assert found("company number 09876543 Agency") == [("09876543", 15, 23, ID)]


def test_finds_bank_details_by_keyword() -> None:
    assert found("sort code 12-34-56 and account number 12345678.") == [
        ("12-34-56", 10, 18, BANK),
        ("12345678", 38, 46, BANK),
    ]


def test_plain_numbers_are_kept() -> None:
    assert found("Pay 5 days, £1,600 on 5 November 2026.") == []
    assert found("ref 1234 5678") == []


def test_result_is_sorted_and_from_patterns() -> None:
    suggestions = find_patterns("b@x.com +44 20 7946 0958")

    assert len(suggestions) == 2
    assert suggestions[0].kind is EMAIL
    assert all(suggestion.source is PiiSource.PATTERN for suggestion in suggestions)


def test_id_value_only_registered_number() -> None:
    assert found("registered number SC123456") == [("SC123456", 18, 26, ID)]


def test_bracketed_national_phone() -> None:
    assert found("Tel: (0121) 496 0123.") == [("(0121) 496 0123", 5, 20, PHONE)]


def test_bracketed_national_phone_2() -> None:
    assert found("Call (020) 7946 0958 now") == [("(020) 7946 0958", 5, 20, PHONE)]


def test_unseparated_national_phone() -> None:
    assert found("Mobile: 07700900123.") == [("07700900123", 8, 19, PHONE)]


def test_unseparated_phone_without_a_cue() -> None:
    assert found("Use 07700900456 for support.") == [("07700900456", 4, 15, PHONE)]


def test_phone_international_with_trunk_zero() -> None:
    assert found("Call +44 (0)20 7946 0958") == [("+44 (0)20 7946 0958", 5, 24, PHONE)]


def test_a_reference_that_looks_like_a_phone_still_matches() -> None:
    assert found("Quote ref 0123 456 7890 on the invoice.") == [("0123 456 7890", 10, 23, PHONE)]


def test_not_a_phone_dates_and_clauses() -> None:
    assert found("Clause 12.3.4 and 2026-11-21") == []


def test_not_a_phone_amounts() -> None:
    assert found("£1,600,000 and 1 234 567 8901") == []


def test_not_a_phone_day_month_year() -> None:
    assert found("due 01-02-2026") == []


def test_not_a_phone_11_digits_with_a_word() -> None:
    assert found("Order 12345678901 shipped") == []


def test_keyword_values_are_not_phones() -> None:
    assert found("sort code 12-34-56 and company number 09876543") == [
        ("12-34-56", 10, 18, BANK),
        ("09876543", 38, 46, ID),
    ]


def test_email_with_non_ascii_letters() -> None:
    assert found("Contact bob@exämple.com now") == [("bob@exämple.com", 8, 23, EMAIL)]


def test_email_with_an_underscore() -> None:
    assert found("Mail john_smith@acme.com.") == [("john_smith@acme.com", 5, 24, EMAIL)]
