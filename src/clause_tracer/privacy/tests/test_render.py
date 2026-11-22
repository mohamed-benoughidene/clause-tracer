"""The printed privacy report (S4-M5-T1)."""

import dataclasses

from clause_tracer.core import (
    PlaceholderEntity,
    PlaceholderKind,
    PlaceholderText,
    Span,
)
from clause_tracer.privacy.placeholder import anonymise
from clause_tracer.privacy.render import render_privacy_report
from clause_tracer.privacy.tests.case_builder import make_case


def _person(start: int, end: int) -> PlaceholderEntity:
    return PlaceholderEntity(
        id="person-1",
        kind=PlaceholderKind.PERSON,
        number=1,
        spans=(Span(start=start, end=end),),
    )


def test_report_lines() -> None:
    case = make_case(["Hi Sam."])
    entities = [_person(3, 6)]

    rendered = render_privacy_report(case, entities, anonymise(case.document, entities))

    assert rendered == (
        "source\tcase.txt\t7\n"
        "counts\tentities 1\tspans 1\tsegments 3\n"
        "entity\tperson-1\tPerson 1\tplaces 1\n"
        "span\tperson-1\t3-6\tSam\n"
        "text\tHi ⟦Person 1⟧.\n"
    )


def test_no_entities() -> None:
    case = make_case(["Hi."])

    rendered = render_privacy_report(case, [], anonymise(case.document, []))

    assert rendered == ("source\tcase.txt\t3\ncounts\tentities 0\tspans 0\tsegments 1\ntext\tHi.\n")


def test_tabs_are_replaced_in_free_text() -> None:
    case = make_case(["x"])
    case = dataclasses.replace(case, document=dataclasses.replace(case.document, text="a\tb"))
    entities = [_person(0, 3)]

    rendered = render_privacy_report(case, entities, anonymise(case.document, entities))

    assert "span\tperson-1\t0-3\ta b\n" in rendered


def test_a_line_break_in_the_sent_text_gives_two_text_lines() -> None:
    case = make_case(["x"])
    placeholder = PlaceholderText(text="a\nb", entities=(), segments=())

    rendered = render_privacy_report(case, [], placeholder)

    assert rendered.split("\n")[-3:-1] == ["text\ta", "text\tb"]


def test_report_ends_with_a_newline() -> None:
    case = make_case(["Hi."])

    rendered = render_privacy_report(case, [], anonymise(case.document, []))

    assert rendered.endswith("\n")
