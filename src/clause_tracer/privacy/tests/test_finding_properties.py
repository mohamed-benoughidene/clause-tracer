"""The properties of `find_personal_data` (S4-M3-T11)."""

from hypothesis import given

from clause_tracer.core import FakePiiDetector, PiiSuggestion
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.sample_input import dump_privacy_fixture
from clause_tracer.privacy.tests.strategies import SETTINGS, PlantedCase, planted_cases


def _output(planted: PlantedCase) -> tuple[str, tuple[PiiSuggestion, ...]]:
    text = planted.case.document.text
    return text, find_personal_data(planted.case, FakePiiDetector({text: planted.planted}))


def _sentence_starts(planted: PlantedCase) -> set[int]:
    return {sentence.span.start for clause in planted.case.clauses for sentence in clause.sentences}


@SETTINGS
@given(planted_cases())
def test_output_is_sorted_apart_and_inside_the_text(planted: PlantedCase) -> None:
    text, output = _output(planted)

    for item in output:
        assert 0 <= item.span.start < item.span.end <= len(text)
    for earlier, later in zip(output, output[1:], strict=False):
        assert earlier.span.start <= later.span.start
        assert earlier.span.end <= later.span.start


@SETTINGS
@given(planted_cases())
def test_no_span_holds_a_sentence_start(planted: PlantedCase) -> None:
    _, output = _output(planted)
    starts = _sentence_starts(planted)

    for item in output:
        assert not any(item.span.start < start < item.span.end for start in starts)


@SETTINGS
@given(planted_cases())
def test_every_flagged_letter_and_digit_is_covered(planted: PlantedCase) -> None:
    text, output = _output(planted)

    for planted_item in planted.planted:
        for index in range(planted_item.span.start, planted_item.span.end):
            if text[index].isalnum():
                assert any(item.span.start <= index < item.span.end for item in output), (
                    f"index {index} of {text!r} is not covered"
                )


@SETTINGS
@given(planted_cases())
def test_a_strategy_case_has_a_valid_input(planted: PlantedCase) -> None:
    dump_privacy_fixture(planted.case)
