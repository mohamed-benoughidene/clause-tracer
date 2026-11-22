"""People by honorific, signature and job title (S4-M2-T7)."""

from clause_tracer.core import PiiSource, PlaceholderKind
from clause_tracer.privacy.people import find_people


def found(text: str) -> list[tuple[str, int, int]]:
    return [
        (
            text[suggestion.span.start : suggestion.span.end],
            suggestion.span.start,
            suggestion.span.end,
        )
        for suggestion in find_people(text)
    ]


def test_honorific_and_surname() -> None:
    assert found("Ms Jones at home. Jones left.") == [
        ("Ms Jones", 0, 8),
        ("Jones", 3, 8),
        ("Jones", 18, 23),
    ]


def test_signature_line() -> None:
    assert found("Executed as a deed by Anna Lee Smith") == [
        ("Anna", 22, 26),
        ("Anna Lee Smith", 22, 36),
        ("Smith", 31, 36),
    ]


def test_name_before_a_job_title() -> None:
    assert found("Signed by Pat Kelly, Managing Director.") == [
        ("Pat", 10, 13),
        ("Pat Kelly", 10, 19),
        ("Kelly", 14, 19),
    ]


def test_variants_are_found_elsewhere() -> None:
    assert found("Signed by Sarah Jones. Hi Sarah, see Ms Jones.") == [
        ("Sarah", 10, 15),
        ("Sarah Jones", 10, 21),
        ("Jones", 16, 21),
        ("Sarah", 26, 31),
        ("Ms Jones", 37, 45),
        ("Jones", 40, 45),
    ]


def test_the_first_by_names_the_signer() -> None:
    assert found("Signed for Acme Ltd by Tom Jones, Director") == [
        ("Tom", 23, 26),
        ("Tom Jones", 23, 32),
        ("Jones", 27, 32),
    ]


def test_lower_case_words_are_not_names() -> None:
    assert found("signed by the board") == []


def test_kind_and_source() -> None:
    suggestions = find_people("Ms Jones at home. Jones left.")

    assert all(suggestion.kind is PlaceholderKind.PERSON for suggestion in suggestions)
    assert all(suggestion.source is PiiSource.RULE for suggestion in suggestions)


def test_a_company_signature_is_not_a_person() -> None:
    assert found("Signed by Acme Holdings Limited") == []


def test_a_month_after_an_honorific_leaves_dates_alone() -> None:
    assert found("Ms May signs on 1 May 2026.") == [("Ms May", 0, 6)]


def test_o_brien() -> None:
    assert found("Signed by Sean O'Brien.") == [
        ("Sean", 10, 14),
        ("Sean O'Brien", 10, 22),
        ("O'Brien", 15, 22),
    ]


def test_o_brien_curly() -> None:
    assert found("Signed by Sean O’Brien.") == [
        ("Sean", 10, 14),
        ("Sean O’Brien", 10, 22),
        ("O’Brien", 15, 22),
    ]


def test_mc_donald() -> None:
    assert found("Signed by Ann McDonald.") == [
        ("Ann", 10, 13),
        ("Ann McDonald", 10, 22),
        ("McDonald", 14, 22),
    ]


def test_hyphen_surname() -> None:
    assert found("Signed by Ana Smith-Jones.") == [
        ("Ana", 10, 13),
        ("Ana Smith-Jones", 10, 25),
        ("Smith-Jones", 14, 25),
    ]


def test_capitals_signature() -> None:
    assert found("SIGNED BY SARAH JONES.") == [
        ("SARAH", 10, 15),
        ("SARAH JONES", 10, 21),
        ("JONES", 16, 21),
    ]


def test_initial() -> None:
    assert found("Signed by Sarah J. Jones.") == [
        ("Sarah", 10, 15),
        ("Sarah J. Jones", 10, 24),
        ("Jones", 19, 24),
    ]


def test_particles() -> None:
    assert found("Signed by Maria de la Cruz.") == [
        ("Maria", 10, 15),
        ("Maria de la Cruz", 10, 26),
        ("Cruz", 22, 26),
    ]


def test_ben_ali() -> None:
    assert found("Signed by Mohamed ben Ali.") == [
        ("Mohamed", 10, 17),
        ("Mohamed ben Ali", 10, 25),
        ("Ali", 22, 25),
    ]


def test_al_rahman() -> None:
    assert found("Signed by Abd al-Rahman Saidi.") == [
        ("Abd", 10, 13),
        ("Abd al-Rahman Saidi", 10, 29),
        ("Saidi", 24, 29),
    ]


def test_trailing_title_without_comma() -> None:
    assert found("Signed by Pat Kelly Director") == [
        ("Pat", 10, 13),
        ("Pat Kelly", 10, 19),
        ("Kelly", 14, 19),
    ]


def test_capitals_honorific() -> None:
    assert found("MS JONES signs.") == [
        ("MS JONES", 0, 8),
        ("JONES", 3, 8),
    ]


def test_legal_words_are_no_name() -> None:
    assert found("Signed by Party Schedule.") == []


def test_capitals_legal_words_are_no_name() -> None:
    assert found("SIGNED BY AGREEMENT PARTY") == []


def test_trailing_legal_word_is_trimmed() -> None:
    assert found("Ms Jones Agreement") == [
        ("Ms Jones", 0, 8),
        ("Jones", 3, 8),
    ]


def test_layer3_pat_at_a_sentence_start_is_left() -> None:
    assert found("Pat Kelly, Managing Director, signed.") == [
        ("Pat Kelly", 0, 9),
        ("Kelly", 4, 9),
    ]


def test_layer3_unambiguous_surname_replaced_at_a_sentence_start() -> None:
    assert found("Signed by Sarah Jones. Jones shall pay.") == [
        ("Sarah", 10, 15),
        ("Sarah Jones", 10, 21),
        ("Jones", 16, 21),
        ("Jones", 23, 28),
    ]


def test_layer4_is_off() -> None:
    assert found("Signed by Tim Brown. Contact Brown. The brown fox.") == [
        ("Tim", 10, 13),
        ("Tim Brown", 10, 19),
        ("Brown", 14, 19),
        ("Brown", 29, 34),
    ]
