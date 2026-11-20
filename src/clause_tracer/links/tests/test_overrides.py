"""Overrides and their direction (S3-M4-T1, S3-M4-T2)."""

from collections.abc import Mapping

from clause_tracer.core import ClauseId, CrossReference, Override
from clause_tracer.links._index import build_index
from clause_tracer.links.outside import find_outside_documents
from clause_tracer.links.overrides import find_overrides
from clause_tracer.links.references import find_references
from clause_tracer.links.terms import find_definitions
from clause_tracer.links.tests.case_builder import build_case, span_of

_DEFINED = [{"id": "4", "sentences": ["4. Fees."]}]


def _run(
    rows: list[Mapping[str, object]],
) -> tuple[str, tuple[CrossReference, ...], tuple[Override, ...]]:
    case = build_case(rows)
    text = case.document.text
    index = build_index(case.clauses)
    references = find_references(text, index)
    outside = find_outside_documents(text, index, find_definitions(text, index))
    return text, references, find_overrides(text, index, references, outside)


def _run_in_9(sentence: str) -> tuple[str, tuple[Override, ...]]:
    return _overrides([*_DEFINED, {"id": "9", "sentences": [sentence]}])


def _overrides(rows: list[Mapping[str, object]]) -> tuple[str, tuple[Override, ...]]:
    text, _, overrides = _run(rows)
    return text, overrides


def test_notwithstanding_overrides_its_target() -> None:
    text, overrides = _run_in_9("9. Notwithstanding Clause 4, fees are fixed.")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=True,
            evidence=span_of(text, "Notwithstanding Clause 4"),
        ),
    )


def test_subject_to_is_qualified() -> None:
    text, overrides = _run_in_9("9. Subject to Clause 4, fees are fixed.")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Subject to Clause 4"),
        ),
    )


def test_save_as_set_out_in() -> None:
    text, overrides = _run_in_9("9. Fees are fixed, save as set out in clause 4.")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "save as set out in clause 4"),
        ),
    )


def test_unresolved_target_gives_no_override() -> None:
    text, references, overrides = _run([{"id": "9", "sentences": ["9. Subject to clause 7."]}])
    assert references == (CrossReference(source=span_of(text, "clause 7"), target=None),)
    assert overrides == ()


def test_range_gives_one_override_per_target() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "5", "sentences": ["5. Payment."]},
            {"id": "9", "sentences": ["9. Subject to clauses 4 to 5."]},
        ]
    )
    evidence = span_of(text, "Subject to clauses 4 to 5")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=evidence,
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("5"),
            overrides_target=False,
            evidence=evidence,
        ),
    )


def test_reference_too_far_away() -> None:
    _, overrides = _run_in_9(
        "9. Subject to the terms and the conditions set out at length in clause 4."
    )
    assert overrides == ()


def test_gap_with_other_words() -> None:
    _, overrides = _run_in_9("9. Subject to approval under clause 4.")
    assert overrides == ()


def test_gap_the_provisions_of() -> None:
    text, overrides = _run_in_9("9. Subject to the provisions of clause 4.")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Subject to the provisions of clause 4"),
        ),
    )


def test_reference_in_next_sentence() -> None:
    _, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["Subject to agreement.", "See clause 4."]},
        ]
    )
    assert overrides == ()


def test_except_master_agreement_is_no_override() -> None:
    _, overrides = _overrides(
        [
            {
                "id": "11.1",
                "sentences": [
                    "11.1 Capped at the fees, except as set out in the Master Agreement."
                ],
            }
        ]
    )
    assert overrides == ()


def test_general_notwithstanding() -> None:
    text, overrides = _overrides(
        [
            {
                "id": "9",
                "sentences": [
                    "9. Notwithstanding anything to the contrary in this Agreement, fees are fixed."
                ],
            }
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=None,
            overrides_target=True,
            evidence=span_of(text, "Notwithstanding anything to the contrary in this Agreement"),
        ),
    )


def test_plain_notwithstanding_without_target() -> None:
    _, overrides = _overrides([{"id": "9", "sentences": ["9. Notwithstanding the delay, pay."]}])
    assert overrides == ()


def test_two_phrases_take_the_nearest() -> None:
    text, overrides = _run_in_9(
        "9. Notwithstanding the foregoing and subject to clause 4, fees are fixed."
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "subject to clause 4"),
        ),
    )


def test_and_clause_joins() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "5", "sentences": ["5. Payment."]},
            {"id": "9", "sentences": ["9. Notwithstanding clause 4 and clause 5, fees are fixed."]},
        ]
    )
    evidence = span_of(text, "Notwithstanding clause 4 and clause 5")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=True,
            evidence=evidence,
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("5"),
            overrides_target=True,
            evidence=evidence,
        ),
    )


def test_list_then_range_group() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "5", "sentences": ["5. Payment."]},
            {"id": "6", "sentences": ["6. Expenses."]},
            {"id": "9", "sentences": ["9. Subject to clause 4 and clauses 5 to 6."]},
        ]
    )
    evidence = span_of(text, "Subject to clause 4 and clauses 5 to 6")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=evidence,
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("5"),
            overrides_target=False,
            evidence=evidence,
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("6"),
            overrides_target=False,
            evidence=evidence,
        ),
    )


def test_general_any_other_provision_in() -> None:
    text, overrides = _overrides(
        [
            {
                "id": "9",
                "sentences": ["9. Notwithstanding any other provision in this Agreement, pay."],
            }
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=None,
            overrides_target=True,
            evidence=span_of(text, "Notwithstanding any other provision in this Agreement"),
        ),
    )


def test_general_with_outside_document() -> None:
    _, overrides = _overrides(
        [
            {
                "id": "9",
                "sentences": [
                    "9. Notwithstanding anything to the contrary in this Agreement or the Master "
                    "Agreement, fees are fixed."
                ],
            }
        ]
    )
    assert overrides == ()


def test_agreement_prevails_over_schedule() -> None:
    text, overrides = _overrides(
        [
            {
                "id": "14.2",
                "sentences": [
                    "14.2 If this Agreement and Schedule 1 conflict, this Agreement prevails."
                ],
            },
            {
                "id": "S1",
                "number": "Schedule 1",
                "heading": "Fees",
                "sentences": ["Schedule 1 · Fees"],
            },
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("14.2"),
            target=ClauseId("S1"),
            overrides_target=True,
            evidence=span_of(
                text, "14.2 If this Agreement and Schedule 1 conflict, this Agreement prevails."
            ),
        ),
    )


def test_schedule_prevails() -> None:
    text, overrides = _overrides(
        [
            {
                "id": "14.2",
                "sentences": [
                    "14.2 If this Agreement and Schedule 1 conflict, Schedule 1 prevails."
                ],
            },
            {
                "id": "S1",
                "number": "Schedule 1",
                "heading": "Fees",
                "sentences": ["Schedule 1 · Fees"],
            },
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("14.2"),
            target=ClauseId("S1"),
            overrides_target=False,
            evidence=span_of(
                text, "14.2 If this Agreement and Schedule 1 conflict, Schedule 1 prevails."
            ),
        ),
    )


def test_this_clause_prevails_over_named_clause() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["9. This Clause prevails over clause 4."]},
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=True,
            evidence=span_of(text, "9. This Clause prevails over clause 4."),
        ),
    )


def test_conflict_naming_nothing() -> None:
    text, overrides = _overrides(
        [{"id": "9", "sentences": ["9. In case of conflict, this Section prevails."]}]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=None,
            overrides_target=True,
            evidence=span_of(text, "9. In case of conflict, this Section prevails."),
        ),
    )


def test_takes_precedence() -> None:
    text, overrides = _overrides(
        [
            {
                "id": "S1",
                "number": "Schedule 1",
                "heading": "Fees",
                "sentences": ["Schedule 1 · Fees"],
            },
            {"id": "14.2", "sentences": ["14.2 this Agreement takes precedence over Schedule 1"]},
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("14.2"),
            target=ClauseId("S1"),
            overrides_target=True,
            evidence=span_of(text, "14.2 this Agreement takes precedence over Schedule 1"),
        ),
    )


def test_prevails_with_no_winner() -> None:
    _, overrides = _overrides([{"id": "9", "sentences": ["9. The higher figure prevails."]}])
    assert overrides == ()


def test_prevails_in_ordinary_sentence() -> None:
    _, overrides = _overrides(
        [{"id": "9", "sentences": ["9. The law that governs this Agreement prevails."]}]
    )
    assert overrides == ()


def test_take_precedence_over_set_off() -> None:
    _, overrides = _overrides(
        [
            {
                "id": "9",
                "sentences": [
                    "9. Amounts due under this Agreement take precedence over any set-off."
                ],
            }
        ]
    )
    assert overrides == ()


def test_unresolved_loser_is_no_override() -> None:
    _, overrides = _overrides(
        [{"id": "9", "sentences": ["9. this Agreement prevails over clause 99"]}]
    )
    assert overrides == ()


def test_subject_to_then_prevails() -> None:
    text, overrides = _overrides(
        [
            {"id": "3", "sentences": ["3. Fees."]},
            {
                "id": "S1",
                "number": "Schedule 1",
                "heading": "Fees",
                "sentences": ["Schedule 1 · Fees"],
            },
            {
                "id": "9",
                "sentences": ["9. Subject to clause 3, this Agreement prevails over Schedule 1."],
            },
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("S1"),
            overrides_target=True,
            evidence=span_of(
                text, "9. Subject to clause 3, this Agreement prevails over Schedule 1."
            ),
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("3"),
            overrides_target=False,
            evidence=span_of(text, "Subject to clause 3"),
        ),
    )


def test_self_and_reference_in_winner() -> None:
    _, overrides = _overrides(
        [
            {
                "id": "S1",
                "number": "Schedule 1",
                "heading": "Fees",
                "sentences": ["Schedule 1 · Fees"],
            },
            {"id": "14.2", "sentences": ["14.2 Schedule 1 and this Agreement prevails."]},
        ]
    )
    assert overrides == ()


def test_agreement_prevails_naming_nothing_is_nothing() -> None:
    _, overrides = _overrides(
        [{"id": "9", "sentences": ["9. For the avoidance of doubt, this Agreement prevails."]}]
    )
    assert overrides == ()


def test_prevails_over_outside_document() -> None:
    _, overrides = _overrides(
        [
            {
                "id": "9",
                "sentences": [
                    "9. If there is a conflict between this Agreement and the Master Agreement, "
                    "this Agreement prevails."
                ],
            }
        ]
    )
    assert overrides == ()


def test_clause_prevails_over_any_terms() -> None:
    _, overrides = _overrides(
        [{"id": "9", "sentences": ["9. This Clause prevails over any other terms."]}]
    )
    assert overrides == ()


def test_conflict_this_clause_prevails() -> None:
    text, overrides = _overrides(
        [{"id": "9", "sentences": ["9. If any term conflicts, then this Clause prevails."]}]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=None,
            overrides_target=True,
            evidence=span_of(text, "9. If any term conflicts, then this Clause prevails."),
        ),
    )


def test_sorted_by_evidence() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "9", "sentences": ["Subject to clause 4.", "Subject to clause 4."]},
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Subject to clause 4", 1),
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Subject to clause 4", 2),
        ),
    )


def test_sentence_without_a_number_prefix() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "5", "sentences": ["5. Payment."]},
            {"id": "9", "sentences": ["9. Fees.", "Clause 4 prevails over clause 5."]},
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Clause 4 prevails over clause 5."),
        ),
    )


def test_comma_inside_a_list_winner() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "5", "sentences": ["5. Payment."]},
            {"id": "6", "sentences": ["6. Expenses."]},
            {"id": "9", "sentences": ["9. Clauses 4, 5 prevail over clause 6."]},
        ]
    )
    evidence = span_of(text, "9. Clauses 4, 5 prevail over clause 6.")
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=evidence,
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("5"),
            overrides_target=False,
            evidence=evidence,
        ),
    )


def test_directional_override_in_another_sentence_hides_no_loser() -> None:
    text, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {
                "id": "9",
                "sentences": ["9. Subject to clause 4.", "This Clause prevails over clause 4."],
            },
        ]
    )
    assert overrides == (
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=False,
            evidence=span_of(text, "Subject to clause 4"),
        ),
        Override(
            clause_id=ClauseId("9"),
            target=ClauseId("4"),
            overrides_target=True,
            evidence=span_of(text, "This Clause prevails over clause 4."),
        ),
    )


def test_heading_sentence_gives_no_directional_override() -> None:
    _, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {
                "id": "9",
                "heading": "Subject to Clause 4",
                "sentences": ["Subject to Clause 4", "9. Pay."],
            },
        ]
    )
    assert overrides == ()


def test_heading_sentence_gives_no_prevails_override() -> None:
    _, overrides = _overrides(
        [
            {"id": "4", "sentences": ["4. Fees."]},
            {"id": "5", "sentences": ["5. Payment."]},
            {
                "id": "9",
                "heading": "Clause 4 prevails over clause 5",
                "sentences": ["Clause 4 prevails over clause 5", "9. Pay."],
            },
        ]
    )
    assert overrides == ()
