"""Defined terms, their uses, and terms used but never defined (S3-M3-T1, T2, T4)."""

from collections.abc import Mapping

from clause_tracer.core import DefinedTerm, Sentence, Span, fold_for_matching
from clause_tracer.links._index import build_index
from clause_tracer.links._spans import build_span_set, trimmed
from clause_tracer.links.sample_clauses import SampleInput
from clause_tracer.links.terms import (
    Definition,
    find_definitions,
    find_terms,
    find_undefined_terms,
)
from clause_tracer.links.tests.case_builder import build_case, span_of


def _definitions(
    rows: list[Mapping[str, object]],
) -> tuple[str, tuple[Definition, ...]]:
    case = build_case(rows)
    index = build_index(case.clauses)
    return case.document.text, find_definitions(case.document.text, index)


def _in_one_clause(*sentences: str) -> tuple[str, tuple[Definition, ...]]:
    return _definitions([{"id": "1", "sentences": list(sentences)}])


def _sentence(sample: SampleInput, sentence_id: str) -> Sentence:
    for clause in sample.clauses:
        for sentence in clause.sentences:
            if str(sentence.id) == sentence_id:
                return sentence
    raise AssertionError(f"no sentence {sentence_id}")


def _trimmed_sentence(sample: SampleInput, sentence_id: str) -> Span:
    return trimmed(sample.document.text, _sentence(sample, sentence_id).span)


def test_means() -> None:
    text, definitions = _in_one_clause('"Charges" means the fees.')
    assert definitions == (
        Definition(
            term="Charges",
            quoted=span_of(text, "Charges"),
            definition=Span(start=0, end=len(text)),
        ),
    )


def test_shall_mean() -> None:
    _, definitions = _in_one_clause('"Charges" shall mean the fees.')
    assert [definition.term for definition in definitions] == ["Charges"]


def test_has_the_meaning() -> None:
    _, definitions = _in_one_clause('"Charges" has the meaning given below.')
    assert [definition.term for definition in definitions] == ["Charges"]


def test_curly_quotes() -> None:
    _, definitions = _in_one_clause("\u201cServices\u201d means work.")
    assert [definition.term for definition in definitions] == ["Services"]


def test_single_quotes() -> None:
    _, definitions = _in_one_clause("'Fee' means money.")
    assert [definition.term for definition in definitions] == ["Fee"]


def test_bracket_with_the_inside() -> None:
    text, definitions = _in_one_clause('Brightline Ltd ("the Agency").')
    assert [definition.term for definition in definitions] == ["Agency"]
    assert definitions[0].quoted == span_of(text, "Agency")


def test_bracket_with_the_outside() -> None:
    text, definitions = _in_one_clause('Brightline Ltd (the "Agency").')
    assert [definition.term for definition in definitions] == ["Agency"]
    assert definitions[0].quoted == span_of(text, "Agency")


def test_lower_case_is_not_a_term() -> None:
    _, definitions = _in_one_clause('"fees" means money.')
    assert definitions == ()


def test_means_without_quotes_is_not_a_term() -> None:
    _, definitions = _in_one_clause("Charges means the fees.")
    assert definitions == ()


def test_defined_twice() -> None:
    text, definitions = _in_one_clause('"Fee" means a.', '"Fee" means b.')
    assert [definition.term for definition in definitions] == ["Fee", "Fee"]
    assert definitions[0].quoted == span_of(text, "Fee", 1)
    assert definitions[1].quoted == span_of(text, "Fee", 2)


def test_multi_word_term() -> None:
    _, definitions = _in_one_clause('"Master Agreement" means the deal.')
    assert [definition.term for definition in definitions] == ["Master Agreement"]


def test_mid_sentence_means_is_not_a_definition() -> None:
    _, definitions = _in_one_clause('The word "Fee" means nothing.')
    assert definitions == ()


def test_each_a_party() -> None:
    _, definitions = _in_one_clause('Brightline Ltd (each a "Party").')
    assert [definition.term for definition in definitions] == ["Party"]


def test_together_the_parties() -> None:
    _, definitions = _in_one_clause('Brightline and Karim (together the "Parties") sign.')
    assert [definition.term for definition in definitions] == ["Parties"]


def test_means_with_the_inside_quotes() -> None:
    _, definitions = _in_one_clause('"the Buyer" means Brightline.')
    assert [definition.term for definition in definitions] == ["Buyer"]


def test_comma_lead_in() -> None:
    _, definitions = _in_one_clause('In this Agreement, "Business Day" means a day.')
    assert [definition.term for definition in definitions] == ["Business Day"]


def test_two_definitions_joined_by_and() -> None:
    text, definitions = _in_one_clause('"Fee" means money and "Tax" means tax.')
    whole_sentence = Span(start=0, end=len(text))
    assert definitions == (
        Definition(
            term="Fee",
            quoted=span_of(text, "Fee"),
            definition=whole_sentence,
        ),
        Definition(
            term="Tax",
            quoted=span_of(text, "Tax"),
            definition=whole_sentence,
        ),
    )


def test_three_definitions_joined_by_and() -> None:
    _, definitions = _in_one_clause('"Fee" means a and "Tax" means b and "Levy" means c.')
    assert [definition.term for definition in definitions] == ["Fee", "Tax", "Levy"]


def test_and_without_an_earlier_definition_is_not_a_definition() -> None:
    _, definitions = _in_one_clause('The word "Fee" and "Tax" means nothing.')
    assert definitions == ()


def test_and_after_a_rejected_definition_is_not_a_definition() -> None:
    _, definitions = _in_one_clause('The word "Fee" means money and "Tax" means tax.')
    assert definitions == ()


_DEFINED_ROWS: list[Mapping[str, object]] = [
    {
        "id": "1",
        "sentences": [
            '"Agency" means the buyer.',
            '"Master Agreement" means the deal.',
            '"Agreement" means the contract.',
        ],
    },
]


def _terms_for(
    sentences: list[str],
) -> tuple[SampleInput, tuple[DefinedTerm, ...]]:
    case = build_case([*_DEFINED_ROWS, {"id": "2", "sentences": sentences}])
    index = build_index(case.clauses)
    text = case.document.text
    definitions = find_definitions(text, index)
    terms = find_terms(text, fold_for_matching(text), definitions)
    return case, terms


def _uses_of(terms: tuple[DefinedTerm, ...], term: str) -> list[tuple[Span, ...]]:
    return [entry.uses for entry in terms if entry.term == term]


def test_uses_found() -> None:
    sample, terms = _terms_for(["2. The Agency starts."])
    assert _uses_of(terms, "Agency") == [(span_of(sample.document.text, "Agency", 2),)]


def test_definition_is_not_a_use() -> None:
    _, terms = _terms_for(["2. Nothing here."])
    assert all(entry.uses == () for entry in terms)


def test_possessive_is_a_use() -> None:
    sample, terms = _terms_for(["2. The Agency's request."])
    assert _uses_of(terms, "Agency") == [(span_of(sample.document.text, "Agency", 2),)]


def test_longer_word_is_not_a_use() -> None:
    _, terms = _terms_for(["2. Agencyship applies."])
    assert _uses_of(terms, "Agency") == [()]


def test_lower_case_is_not_a_use() -> None:
    _, terms = _terms_for(["2. An agency applies."])
    assert _uses_of(terms, "Agency") == [()]


def test_curly_apostrophe() -> None:
    sample, terms = _terms_for(["2. The Agency\u2019s request."])
    assert _uses_of(terms, "Agency") == [(span_of(sample.document.text, "Agency", 2),)]


def test_shorter_term_inside_longer_term() -> None:
    sample, terms = _terms_for(["2. The Master Agreement applies."])
    assert _uses_of(terms, "Master Agreement") == [
        (span_of(sample.document.text, "Master Agreement", 2),)
    ]
    assert _uses_of(terms, "Agreement") == [()]


def test_uses_sorted() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ['"Fee" means money.']},
            {"id": "2", "sentences": ["The Fee and the Fee."]},
        ]
    )
    index = build_index(case.clauses)
    text = case.document.text
    terms = find_terms(text, fold_for_matching(text), find_definitions(text, index))
    assert _uses_of(terms, "Fee") == [
        (span_of(text, "Fee", 2), span_of(text, "Fee", 3)),
    ]


def test_defined_twice_share_uses() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ['"Fee" means a.', '"Fee" means b.']},
            {"id": "2", "sentences": ["The Fee."]},
        ]
    )
    index = build_index(case.clauses)
    text = case.document.text
    terms = find_terms(text, fold_for_matching(text), find_definitions(text, index))
    assert [entry.term for entry in terms] == ["Fee", "Fee"]
    assert [entry.uses for entry in terms] == [
        (span_of(text, "Fee", 3),),
        (span_of(text, "Fee", 3),),
    ]


def test_shorter_term_inside_longer_quotes() -> None:
    case = build_case(
        [
            {
                "id": "1",
                "sentences": ['"Fee" means money.', '"Net Fee" means money after tax.'],
            }
        ]
    )
    index = build_index(case.clauses)
    text = case.document.text
    terms = find_terms(text, fold_for_matching(text), find_definitions(text, index))
    assert _uses_of(terms, "Fee") == [()]
    assert _uses_of(terms, "Net Fee") == [()]


def test_overlapping_terms() -> None:
    case = build_case(
        [
            {
                "id": "1",
                "sentences": ['"Net Fee" means a.', '"Fee Pool" means b.'],
            },
            {"id": "2", "sentences": ["The Net Fee Pool."]},
        ]
    )
    index = build_index(case.clauses)
    text = case.document.text
    terms = find_terms(text, fold_for_matching(text), find_definitions(text, index))
    assert _uses_of(terms, "Fee Pool") == [(span_of(text, "Fee Pool", 2),)]
    assert _uses_of(terms, "Net Fee") == [()]


def test_same_folded_text_shares_uses() -> None:
    case = build_case(
        [
            {"id": "1", "sentences": ['"Fee" means a.', '"FEE" means b.']},
            {"id": "2", "sentences": ["The Fee and the FEE."]},
        ]
    )
    index = build_index(case.clauses)
    text = case.document.text
    terms = find_terms(text, fold_for_matching(text), find_definitions(text, index))
    expected = (span_of(text, "Fee", 2), span_of(text, "FEE", 2))
    assert [entry.term for entry in terms] == ["Fee", "FEE"]
    assert [entry.uses for entry in terms] == [expected, expected]


def _undefined(
    sentence: str,
    *,
    excluded: tuple[Span, ...] = (),
) -> tuple[str, tuple[Span, ...]]:
    case = build_case([{"id": "1", "sentences": [sentence]}])
    index = build_index(case.clauses)
    text = case.document.text
    return text, find_undefined_terms(text, index, build_span_set(excluded))


def test_business_days() -> None:
    text, undefined = _undefined("6.1 Reply within 3 Business Days.")
    assert undefined == (span_of(text, "Business Days"),)


def test_sentence_start_is_skipped() -> None:
    _, undefined = _undefined("6.1 Business Days count.")
    assert undefined == ()


def test_after_bracket_marker() -> None:
    _, undefined = _undefined("(A) The Agency builds.")
    assert undefined == ()


def test_single_word_is_skipped() -> None:
    _, undefined = _undefined("6.1 Pay VAT and Tax.")
    assert undefined == ()


def test_defined_term_is_skipped() -> None:
    text, undefined = _undefined(
        "under the Master Agreement",
        excluded=(span_of("under the Master Agreement", "Master Agreement"),),
    )
    assert undefined == ()


def test_heading_sentence_is_skipped() -> None:
    case = build_case(
        [{"id": "5", "heading": "Charges And Payment", "sentences": ["5. Charges And Payment"]}]
    )
    index = build_index(case.clauses)
    assert find_undefined_terms(case.document.text, index, build_span_set(())) == ()


def test_table_row_is_skipped() -> None:
    _, with_tab = _undefined("6.1 x Aa Bb\tcc")
    text, without_tab = _undefined("6.1 x Aa Bb cc")
    assert with_tab == ()
    assert without_tab == (span_of(text, "Aa Bb"),)


def test_four_words_at_most() -> None:
    text, undefined = _undefined("x Aa Bb Cc Dd Ee y")
    assert undefined == (span_of(text, "Aa Bb Cc Dd"),)


def test_outside_document_is_skipped() -> None:
    text, undefined = _undefined(
        "6.1 Reply within 3 Business Days.",
        excluded=(span_of("6.1 Reply within 3 Business Days.", "Business Days"),),
    )
    assert undefined == ()
