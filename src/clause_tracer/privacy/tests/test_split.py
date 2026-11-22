"""Split suggestions at sentence starts (S4-M3-T5)."""

from clause_tracer.core import PiiSource, PiiSuggestion, PlaceholderKind, Span
from clause_tracer.privacy.resolve import sentence_starts, split_at_sentences
from clause_tracer.privacy.tests.case_builder import make_case, suggestion

PERSON = PlaceholderKind.PERSON
ADDRESS = PlaceholderKind.ADDRESS
NER = PiiSource.NER


def _read(
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


def test_a_span_inside_a_sentence_is_kept() -> None:
    text = "Pay Sam. Then Kim."
    item = suggestion(text, "Sam", PERSON, NER)

    assert split_at_sentences(text, (item,), (0, 9)) == (item,)


def test_a_span_across_a_sentence_start_is_cut() -> None:
    text = "Pay Sam Lee. Then Kim."
    item = suggestion(text, "Lee. Then", ADDRESS, NER)

    assert split_at_sentences(text, (item,), (0, 13)) == (
        PiiSuggestion(span=Span(start=8, end=12), kind=ADDRESS, source=NER),
        PiiSuggestion(span=Span(start=13, end=17), kind=ADDRESS, source=NER),
    )


def test_a_piece_of_only_white_space_is_dropped() -> None:
    text = "ab cd"
    item = PiiSuggestion(span=Span(start=2, end=4), kind=PERSON, source=NER)

    assert split_at_sentences(text, (item,), (0, 3)) == (
        PiiSuggestion(span=Span(start=3, end=4), kind=PERSON, source=NER),
    )


def test_several_starts_give_several_pieces() -> None:
    text = "aa bb cc dd"
    item = PiiSuggestion(span=Span(start=0, end=11), kind=ADDRESS, source=NER)

    assert _read(text, split_at_sentences(text, (item,), (0, 3, 6, 9))) == [
        ("aa", 0, 2, ADDRESS, NER),
        ("bb", 3, 5, ADDRESS, NER),
        ("cc", 6, 8, ADDRESS, NER),
        ("dd", 9, 11, ADDRESS, NER),
    ]


def test_sentence_starts() -> None:
    case = make_case(["A b.", "C d.", "E f."])

    assert sentence_starts(case.clauses) == (0, 5, 10)


def test_kind_and_source_are_kept() -> None:
    text = "Pay Sam Lee. Then Kim."
    item = suggestion(text, "Lee. Then", ADDRESS, NER)

    assert {piece.kind for piece in split_at_sentences(text, (item,), (0, 13))} == {ADDRESS}
    assert {piece.source for piece in split_at_sentences(text, (item,), (0, 13))} == {NER}


def test_pieces_are_sorted_and_unique() -> None:
    text = "aa bb"
    later = PiiSuggestion(span=Span(start=3, end=5), kind=PERSON, source=NER)
    earlier = PiiSuggestion(span=Span(start=0, end=2), kind=PERSON, source=NER)

    result = split_at_sentences(text, (later, earlier, earlier), ())

    assert tuple((item.span.start, item.span.end) for item in result) == ((0, 2), (3, 5))


def test_split_is_idempotent() -> None:
    text = "Pay Sam Lee. Then Kim."
    item = suggestion(text, "Lee. Then", ADDRESS, NER)
    once = split_at_sentences(text, (item,), (0, 13))

    assert split_at_sentences(text, once, (0, 13)) == once
