"""Tests for splitting a document's text into lines (S2-M3-T1)."""

from hypothesis import given

from clause_tracer.core.tests.strategies import hazard_text
from clause_tracer.ingest._lines import Line, is_blank, split_lines


def test_three_kinds_of_break() -> None:
    lines = split_lines("a\nb\r\nc\rd")

    assert tuple(line.text for line in lines) == ("a", "b", "c", "d")
    assert tuple(line.start for line in lines) == (0, 2, 5, 7)


def test_empty_text_is_one_empty_line() -> None:
    assert split_lines("") == (Line(start=0, end=0, text=""),)


def test_trailing_break_gives_a_last_empty_line() -> None:
    lines = split_lines("a\n")

    assert len(lines) == 2
    assert lines[1] == Line(start=2, end=2, text="")


def test_blank_line() -> None:
    assert is_blank(Line(start=0, end=2, text=" \t"))
    assert not is_blank(Line(start=0, end=2, text=" a"))


def test_line_with_only_a_byte_order_mark_is_blank() -> None:
    assert is_blank(Line(start=0, end=1, text="﻿"))


@given(source=hazard_text())
def test_lines_point_into_the_text(source: str) -> None:
    for line in split_lines(source):
        assert line.text == source[line.start : line.end]
        assert "\n" not in line.text
        assert "\r" not in line.text
