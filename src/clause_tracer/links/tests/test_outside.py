"""Documents that are not loaded (S3-M3-T3)."""

from collections.abc import Mapping

from clause_tracer.core import OutsideDocument
from clause_tracer.links._index import build_index
from clause_tracer.links.outside import find_outside_documents
from clause_tracer.links.terms import find_definitions
from clause_tracer.links.tests.case_builder import build_case, span_of


def _outside(
    rows: list[Mapping[str, object]],
) -> tuple[str, tuple[OutsideDocument, ...]]:
    case = build_case(rows)
    index = build_index(case.clauses)
    text = case.document.text
    return text, find_outside_documents(text, index, find_definitions(text, index))


def test_master_agreement() -> None:
    text, outside = _outside(
        [
            {
                "id": "11.1",
                "sentences": ["11.1 Capped, except as set out in the Master Agreement."],
            }
        ]
    )
    assert outside == (
        OutsideDocument(name="Master Agreement", evidence=span_of(text, "Master Agreement")),
    )


def test_this_agreement_is_not_outside() -> None:
    _, outside = _outside(
        [
            {
                "id": "1",
                "sentences": [
                    "1. This Agreement starts today.",
                    "It runs under this Agreement until ended.",
                ],
            }
        ]
    )
    assert outside == ()


def test_this_named_agreement_is_not_outside() -> None:
    _, outside = _outside(
        [{"id": "1", "sentences": ["1. The deal runs under this Services Agreement."]}]
    )
    assert outside == ()


def test_defined_term_in_its_quotes_is_skipped() -> None:
    _, outside = _outside([{"id": "1", "sentences": ['1. "Master Agreement" means the deal.']}])
    assert outside == ()


def test_lower_case_policy_is_not_outside() -> None:
    _, outside = _outside(
        [
            {
                "id": "5.5",
                "sentences": [
                    "5.5 Expenses follow its expenses policy at "
                    "https://docs.example.com/expenses-policy."
                ],
            }
        ]
    )
    assert outside == ()


def test_the_is_dropped() -> None:
    text, outside = _outside([{"id": "1", "sentences": ["The Supply Contract applies."]}])
    assert outside == (
        OutsideDocument(name="Supply Contract", evidence=span_of(text, "Supply Contract")),
    )


def test_heading_is_skipped() -> None:
    _, outside = _outside(
        [
            {
                "id": "p1",
                "heading": "Development Services Agreement",
                "sentences": ["Development Services Agreement"],
            },
            {"id": "p2", "sentences": ["This Agreement is dated 5 November 2026."]},
        ]
    )
    assert outside == ()


def test_statement_of_work() -> None:
    text, outside = _outside(
        [
            {
                "id": "7",
                "sentences": ["7. Work follows the Project Statement of Work."],
            }
        ]
    )
    assert outside == (
        OutsideDocument(
            name="Project Statement of Work",
            evidence=span_of(text, "Project Statement of Work"),
        ),
    )


def test_each_mention_counts() -> None:
    text, outside = _outside(
        [
            {"id": "11.1", "sentences": ["11.1 Liability follows the Master Agreement."]},
            {"id": "11.2", "sentences": ["11.2 The Master Agreement also caps losses."]},
        ]
    )
    assert outside == (
        OutsideDocument(name="Master Agreement", evidence=span_of(text, "Master Agreement", 1)),
        OutsideDocument(name="Master Agreement", evidence=span_of(text, "Master Agreement", 2)),
    )


def test_payment_terms_is_not_outside() -> None:
    _, outside = _outside([{"id": "1", "sentences": ["1. The Payment Terms apply."]}])
    assert outside == ()


def test_hyphenated_name() -> None:
    text, outside = _outside(
        [{"id": "7", "sentences": ["7. Signed under the Non-Disclosure Agreement."]}]
    )
    assert outside == (
        OutsideDocument(
            name="Non-Disclosure Agreement",
            evidence=span_of(text, "Non-Disclosure Agreement"),
        ),
    )


def test_dropped_words_repeat() -> None:
    text, outside = _outside([{"id": "1", "sentences": ["Under Services Agreement terms apply."]}])
    assert outside == (
        OutsideDocument(name="Services Agreement", evidence=span_of(text, "Services Agreement")),
    )


def test_terms_and_conditions() -> None:
    text, outside = _outside(
        [{"id": "1", "sentences": ["1. The Standard Terms and Conditions apply."]}]
    )
    assert outside == (
        OutsideDocument(
            name="Standard Terms and Conditions",
            evidence=span_of(text, "Standard Terms and Conditions"),
        ),
    )


def test_name_across_a_no_break_space() -> None:
    text, outside = _outside([{"id": "1", "sentences": ["1. See the Master\u00a0Agreement."]}])
    assert outside == (
        OutsideDocument(
            name="Master\u00a0Agreement",
            evidence=span_of(text, "Master\u00a0Agreement"),
        ),
    )


def test_own_name_is_not_outside() -> None:
    _, outside = _outside(
        [
            {"id": "1", "sentences": ['1. "Services Agreement" means this agreement.']},
            {"id": "2", "sentences": ["2. Work under the Services Agreement continues."]},
        ]
    )
    assert outside == ()


def test_noun_before_a_capital_word() -> None:
    _, outside = _outside([{"id": "1", "sentences": ["1. The Software Licence Fee is due."]}])
    assert outside == ()


def test_own_title_is_not_outside() -> None:
    _, outside = _outside(
        [
            {
                "id": "p1",
                "heading": "Development Services Agreement",
                "sentences": ["Development Services Agreement"],
            },
            {
                "id": "1",
                "sentences": ["1. The Development Services Agreement is the whole deal."],
            },
        ]
    )
    assert outside == ()
