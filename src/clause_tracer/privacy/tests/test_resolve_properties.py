"""The properties of the resolve step (S4-M3-T11)."""

from random import Random
from typing import Final, cast

from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import (
    FakePiiDetector,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
)
from clause_tracer.privacy._spans import order_key, overlaps, trimmed_span
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.places import governing_law_places
from clause_tracer.privacy.resolve import (
    SOURCE_PRIORITY,
    resolve_overlaps,
    split_at_sentences,
    trim_suggestions,
)
from clause_tracer.privacy.tests.strategies import (
    OFFSETS,
    SETTINGS,
    TEXTS,
    PlantedCase,
    clean_input,
    law_cases,
    with_starts,
    with_suggestions,
)

OFFSET_ROWS: Final[st.SearchStrategy[list[tuple[object, object, PlaceholderKind, PiiSource]]]] = (
    st.lists(
        st.tuples(
            OFFSETS,
            OFFSETS,
            st.sampled_from(list(PlaceholderKind)),
            st.sampled_from(list(PiiSource)),
        ),
        max_size=6,
    )
)


def _cover(suggestions: tuple[PiiSuggestion, ...]) -> set[int]:
    return {
        index
        for suggestion in suggestions
        for index in range(suggestion.span.start, suggestion.span.end)
    }


def _alnum(text: str, indexes: set[int]) -> set[int]:
    return {index for index in indexes if text[index].isalnum()}


def _holds(span: Span, index: int) -> bool:
    return span.start <= index < span.end


def _is_bad(text: str, start: object, end: object) -> bool:
    if isinstance(start, bool) or not isinstance(start, int):
        return True
    if isinstance(end, bool) or not isinstance(end, int):
        return True
    return start < 0 or end < 0 or start > len(text) or end > len(text) or end < start


@SETTINGS
@given(with_suggestions())
def test_p1_output_is_disjoint_sorted_trimmed_and_inside(
    pair: tuple[str, tuple[PiiSuggestion, ...]],
) -> None:
    text, suggestions = pair
    result = resolve_overlaps(text, suggestions)

    for item in result:
        assert 0 <= item.span.start < item.span.end <= len(text)
        assert not text[item.span.start].isspace()
        assert not text[item.span.end - 1].isspace()
    for earlier, later in zip(result, result[1:], strict=False):
        assert earlier.span.start <= later.span.start
        assert earlier.span.end <= later.span.start


@SETTINGS
@given(with_suggestions())
def test_p2_no_letter_or_digit_is_uncovered(
    pair: tuple[str, tuple[PiiSuggestion, ...]],
) -> None:
    text, suggestions = pair

    assert _alnum(text, _cover(suggestions)) <= _cover(resolve_overlaps(text, suggestions))


@SETTINGS
@given(with_suggestions())
def test_p3_no_span_is_invented(pair: tuple[str, tuple[PiiSuggestion, ...]]) -> None:
    text, suggestions = pair

    for item in resolve_overlaps(text, suggestions):
        for index in range(item.span.start, item.span.end):
            assert any(
                other.kind == item.kind
                and other.source == item.source
                and _holds(other.span, index)
                for other in suggestions
            )


@SETTINGS
@given(with_suggestions())
def test_p4_source_priority_decides_each_character(
    pair: tuple[str, tuple[PiiSuggestion, ...]],
) -> None:
    text, suggestions = pair
    result = resolve_overlaps(text, suggestions)

    for index in _alnum(text, _cover(suggestions)):
        holders = [item for item in result if _holds(item.span, index)]
        assert len(holders) == 1
        best = min(SOURCE_PRIORITY[item.source] for item in suggestions if _holds(item.span, index))
        assert SOURCE_PRIORITY[holders[0].source] == best


@SETTINGS
@given(with_suggestions())
def test_p5_resolve_is_idempotent(pair: tuple[str, tuple[PiiSuggestion, ...]]) -> None:
    text, suggestions = pair
    once = resolve_overlaps(text, suggestions)

    assert resolve_overlaps(text, once) == once


@SETTINGS
@given(with_suggestions(), st.randoms(use_true_random=False))
def test_p6_resolve_ignores_input_order(
    pair: tuple[str, tuple[PiiSuggestion, ...]], randoms: Random
) -> None:
    text, suggestions = pair
    shuffled = list(suggestions)
    randoms.shuffle(shuffled)

    assert resolve_overlaps(text, shuffled) == resolve_overlaps(text, suggestions)


@SETTINGS
@given(with_suggestions(), st.data())
def test_p7_an_extra_suggestion_never_uncovers(
    pair: tuple[str, tuple[PiiSuggestion, ...]], data: st.DataObject
) -> None:
    text, suggestions = pair
    first = data.draw(st.integers(0, len(text)))
    second = data.draw(st.integers(0, len(text)))
    extra = PiiSuggestion(
        span=Span(start=min(first, second), end=max(first, second)),
        kind=data.draw(st.sampled_from(list(PlaceholderKind))),
        source=data.draw(st.sampled_from(list(PiiSource))),
    )
    before = _alnum(text, _cover(resolve_overlaps(text, suggestions)))
    after = _alnum(text, _cover(resolve_overlaps(text, (*suggestions, extra))))

    assert before <= after


@SETTINGS
@given(clean_input())
def test_p8_clean_input_is_unchanged(pair: tuple[str, tuple[PiiSuggestion, ...]]) -> None:
    text, suggestions = pair

    assert resolve_overlaps(text, suggestions) == tuple(
        sorted(suggestions, key=lambda item: (item.span.start, item.span.end))
    )


@SETTINGS
@given(with_starts())
def test_p9_split_keeps_cover_kind_and_source(
    case: tuple[str, tuple[PiiSuggestion, ...], list[int]],
) -> None:
    text, resolved, starts = case
    output = split_at_sentences(text, resolved, starts)

    for item in output:
        assert not any(item.span.start < start < item.span.end for start in starts)
        assert any(
            other.kind == item.kind
            and other.source == item.source
            and other.span.start <= item.span.start
            and item.span.end <= other.span.end
            for other in resolved
        )
    assert _alnum(text, _cover(resolved)) <= _cover(output)
    for item in resolved:
        if not any(item.span.start < start < item.span.end for start in starts):
            assert item in output
    assert split_at_sentences(text, output, starts) == output
    assert output == tuple(sorted(output, key=order_key))
    assert len(set(output)) == len(output)
    assert split_at_sentences(text, tuple(reversed(resolved)), starts) == output


@SETTINGS
@given(TEXTS, OFFSET_ROWS)
def test_p10_the_check_raises_exactly_for_bad_spans(
    text: str, rows: list[tuple[object, object, PlaceholderKind, PiiSource]]
) -> None:
    suggestions = [
        PiiSuggestion(
            span=Span(start=cast(int, start), end=cast(int, end)),
            kind=kind,
            source=source,
        )
        for start, end, kind, source in rows
    ]
    bad = [_is_bad(text, start, end) for start, end, _, _ in rows]

    try:
        result = trim_suggestions(text, suggestions)
    except ValueError as error:
        assert str(error).startswith("privacy: ")
        assert any(bad)
    else:
        assert not any(bad)
        kept: list[tuple[PlaceholderKind, PiiSource]] = []
        for start, end, kind, source in rows:
            span = trimmed_span(text, Span(start=cast(int, start), end=cast(int, end)))
            if span is not None:
                kept.append((kind, source))
        assert [(item.kind, item.source) for item in result] == kept


@SETTINGS
@given(law_cases())
def test_p11_the_composed_pipeline_cuts_at_the_place(planted: PlantedCase) -> None:
    text = planted.case.document.text
    output = find_personal_data(planted.case, FakePiiDetector({text: planted.planted}))
    places = governing_law_places(text)

    for item in planted.planted:
        for index in range(item.span.start, item.span.end):
            if not text[index].isalnum():
                continue
            if any(_holds(place, index) for place in places):
                continue
            assert any(_holds(result.span, index) for result in output)
    starts = {
        sentence.span.start for clause in planted.case.clauses for sentence in clause.sentences
    }
    for item in output:
        assert not any(item.span.start < start < item.span.end for start in starts)


@SETTINGS
@given(law_cases())
def test_p12_a_name_that_touches_the_place_is_hidden_whole(planted: PlantedCase) -> None:
    text = planted.case.document.text
    output = find_personal_data(planted.case, FakePiiDetector({text: planted.planted}))
    places = governing_law_places(text)

    for item in planted.planted:
        if item.kind not in (PlaceholderKind.PERSON, PlaceholderKind.COMPANY):
            continue
        if item.source == PiiSource.USER:
            continue
        if not any(overlaps(place, item.span) for place in places):
            continue
        for index in range(item.span.start, item.span.end):
            if text[index].isalnum():
                assert any(_holds(result.span, index) for result in output)
