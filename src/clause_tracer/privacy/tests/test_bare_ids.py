"""Bare identifiers: NINO, GB VAT, company prefix and card number (S4-M2-T12)."""

from clause_tracer.core import PiiSource, PlaceholderKind
from clause_tracer.privacy.patterns import (
    find_patterns,
    gb_vat_is_valid,
    luhn_is_valid,
)

ID = PlaceholderKind.ID
BANK = PlaceholderKind.BANK
PHONE = PlaceholderKind.PHONE
PREFIXES = (
    "SC",
    "NI",
    "OC",
    "SO",
    "NC",
    "LP",
    "SL",
    "NL",
    "FC",
    "R0",
    "IP",
    "SP",
    "RS",
    "CE",
    "NP",
)


def found(text: str) -> list[tuple[str, int, int, PlaceholderKind]]:
    results: list[tuple[str, int, int, PlaceholderKind]] = []
    for suggestion in find_patterns(text):
        span = suggestion.span
        results.append((text[span.start : span.end], span.start, span.end, suggestion.kind))
    return results


def test_every_result_comes_from_patterns() -> None:
    suggestions = find_patterns("Card 4111 1111 1111 1111 and AB123456C")

    assert len(suggestions) == 2
    assert all(suggestion.source is PiiSource.PATTERN for suggestion in suggestions)


def test_nino_compact() -> None:
    assert found("NI number AB123456C.") == [("AB123456C", 10, 19, ID)]


def test_nino_with_spaces() -> None:
    assert found("NI number AB 12 34 56 C.") == [("AB 12 34 56 C", 10, 23, ID)]
    assert found("JG 10 38 17 D") == [("JG 10 38 17 D", 0, 13, ID)]


def test_nino_after_a_bracket_or_a_colon() -> None:
    assert found("(AB123456C)") == [("AB123456C", 1, 10, ID)]
    assert found("NINO:AB123456C.") == [("AB123456C", 5, 14, ID)]


def test_nino_banned_prefixes_are_not_found() -> None:
    assert found("BG123456C GB123456C NK123456C KN123456C NT123456C TN123456C ZZ123456C") == []


def test_nino_banned_first_letters_are_not_found() -> None:
    assert found("DA123456A FA123456A IA123456A QA123456A UA123456A VA123456A") == []


def test_nino_banned_second_letters_are_not_found() -> None:
    assert found("AD123456A AF123456A AI123456A AO123456A AQ123456A AU123456A AV123456A") == []


def test_nino_wrong_shape_is_not_found() -> None:
    assert found("AB123456E") == []
    assert found("AB12345C") == []
    assert found("AB1234567C") == []
    assert found("ab123456c") == []
    assert found("XAB123456C") == []
    assert found("AB123456CD") == []


def test_gb_vat_bare_with_a_valid_checksum() -> None:
    assert found("Registered for VAT as GB 333289454.") == [("GB 333289454", 22, 34, ID)]


def test_gb_vat_other_spacings() -> None:
    assert found("GB333289454") == [("GB333289454", 0, 11, ID)]
    assert found("GB 980 7806 84") == [("GB 980 7806 84", 0, 14, ID)]
    assert found("GB 333 2894 54") == [("GB 333 2894 54", 0, 14, ID)]


def test_gb_vat_with_a_branch_part() -> None:
    assert found("GB 333 2894 54 000") == [("GB 333 2894 54 000", 0, 18, ID)]


def test_gb_vat_wrong_checksum_is_not_found() -> None:
    assert found("GB123456789") == []
    assert found("GB 123 4567 89") == []


def test_gb_vat_remainders_42_and_55() -> None:
    assert found("GB 100 0000 34") == [("GB 100 0000 34", 0, 14, ID)]
    assert found("GB 100 0000 47") == [("GB 100 0000 47", 0, 14, ID)]
    assert found("GB 001 0000 36") == []
    assert found("GB 001 0000 49") == []


def test_gb_vat_needs_gb_and_a_whole_word() -> None:
    assert found("333289454") == []
    assert found("XGB333289454") == []
    assert found("GB3332894541234") == []
    assert found("GB 33328945") == []


def test_gb_vat_after_a_keyword_needs_no_checksum() -> None:
    assert found("VAT number GB123456789") == [("GB123456789", 11, 22, ID)]


def test_gb_vat_is_valid() -> None:
    assert gb_vat_is_valid("GB 333289454")
    assert gb_vat_is_valid("333289454")
    assert gb_vat_is_valid("GB 333 2894 54 000")
    assert gb_vat_is_valid("GB 100 0000 34")
    assert not gb_vat_is_valid("GB 001 0000 36")
    assert not gb_vat_is_valid("GB123456789")
    assert not gb_vat_is_valid("33328945")


def test_company_prefix_found() -> None:
    assert found("Brightline Studio Ltd (SC123456) signs.") == [("SC123456", 23, 31, ID)]
    assert found("NI012345") == [("NI012345", 0, 8, ID)]
    assert found("LP123456") == [("LP123456", 0, 8, ID)]


def test_every_listed_prefix_is_found() -> None:
    text = " ".join(f"{prefix}123456" for prefix in PREFIXES)
    results = found(text)

    assert len(results) == 15
    assert results[0] == ("SC123456", 0, 8, ID)
    assert results[-1] == ("NP123456", 126, 134, ID)
    assert results == [
        (f"{prefix}123456", 9 * index, 9 * index + 8, ID) for index, prefix in enumerate(PREFIXES)
    ]


def test_company_prefix_wrong_digit_count_is_not_found() -> None:
    assert found("FC12345") == []
    assert found("SC1234567") == []
    assert found("SC12345") == []


def test_company_prefix_in_a_longer_word_is_not_found() -> None:
    assert found("XSC123456") == []
    assert found("SC123456AB") == []
    assert found("sc123456") == []


def test_unlisted_prefixes_are_not_found() -> None:
    assert found("BR123456 OE123456 AB123456") == []


def test_eight_digits_still_need_a_keyword() -> None:
    assert found("09876543") == []
    assert found("company number 09876543") == [("09876543", 15, 23, ID)]


def test_company_prefix_after_a_keyword_gives_one_span() -> None:
    assert found("registered number SC123456") == [("SC123456", 18, 26, ID)]


def test_card_with_a_cue() -> None:
    assert found("Card 4111 1111 1111 1111 expires") == [("4111 1111 1111 1111", 5, 24, BANK)]


def test_card_formats_and_lengths() -> None:
    assert found("visa 4111-1111-1111-1111") == [("4111-1111-1111-1111", 5, 24, BANK)]
    assert found("Pay by Mastercard 5500005555555559.") == [("5500005555555559", 18, 34, BANK)]
    assert found("Amex 378282246310005") == [("378282246310005", 5, 20, BANK)]
    assert found("card 4222222222222") == [("4222222222222", 5, 18, BANK)]
    assert found("card 6304000000000000000") == [("6304000000000000000", 5, 24, BANK)]


def test_card_that_fails_luhn_or_has_the_wrong_length_is_not_found() -> None:
    assert found("Card 4111 1111 1111 1112") == []
    assert found("Card 1234 5678 9012 3456") == []
    assert found("card 411111111117") == []
    assert found("card 41111111111111111111") == []


def test_issuer_digits_3_to_6_are_enough_known_limit() -> None:
    assert found("Order 3111 1111 1111 1113") == [("3111 1111 1111 1113", 6, 25, BANK)]
    assert found("Order 4111 1111 1111 1111") == [("4111 1111 1111 1111", 6, 25, BANK)]
    assert found("Order 5123 4567 8901 2346") == [("5123 4567 8901 2346", 6, 25, BANK)]
    assert found("Order 6111 1111 1111 1116") == [("6111 1111 1111 1116", 6, 25, BANK)]


def test_order_numbers_dates_and_clauses_are_kept() -> None:
    assert found("Order 4929 1234 5678 9012") == []
    assert found("Order 1234567890123456") == []
    assert found("Clause 1.2.3.4 on 2026-11-21 at 12.30") == []


def test_a_cue_is_needed_outside_the_digits_3_to_6() -> None:
    assert found("Order 2221 1111 1111 1112") == []
    assert found("Visa 2221 1111 1111 1112") == [("2221 1111 1111 1112", 5, 24, BANK)]
    assert found("Order 1234 5678 1234 5670") == []


def test_the_cue_must_be_within_40_characters() -> None:
    near = "card" + " " * 36 + "2221 1111 1111 1112"
    far = "card" + " " * 37 + "2221 1111 1111 1112"

    assert found(near) == [("2221 1111 1111 1112", 40, 59, BANK)]
    assert found(far) == []


def test_the_cue_ignores_case_and_needs_a_whole_word() -> None:
    assert found("VISA 2221 1111 1111 1112") == [("2221 1111 1111 1112", 5, 24, BANK)]
    assert found("discard 2221 1111 1111 1112") == []
    assert found("cards 2221 1111 1111 1112") == []


def test_luhn_is_valid() -> None:
    assert luhn_is_valid("4111111111111111")
    assert luhn_is_valid("378282246310005")
    assert not luhn_is_valid("4111111111111112")
    assert not luhn_is_valid("")
    assert not luhn_is_valid("41a1")


def test_card_and_phone_overlap_both_come_back() -> None:
    assert found("Card 4000 0566 5566 5556") == [
        ("4000 0566 5566 5556", 5, 24, BANK),
        ("0566 5566 5556", 10, 24, PHONE),
    ]


def test_nino_and_keyword_id_overlap_both_come_back() -> None:
    assert found("registered number AB123456C") == [
        ("AB123456", 18, 26, ID),
        ("AB123456C", 18, 27, ID),
    ]


def test_long_vat_and_keyword_id_overlap_both_come_back() -> None:
    assert found("VAT number GB 333 2894 54 000") == [
        ("GB 333 2894 54 00", 11, 28, ID),
        ("GB 333 2894 54 000", 11, 29, ID),
    ]
