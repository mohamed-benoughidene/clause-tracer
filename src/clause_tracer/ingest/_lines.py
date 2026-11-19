"""Split a document's text into lines (S2-M3-T1).

The clause splitter reads the text one line at a time. A line keeps the
half-open span it came from, so every later clause and sentence span points
back into `Document.text`. A line break is CRLF, CR or LF, and the text after
the last break is a line even when it is empty.
"""

import re
from dataclasses import dataclass
from typing import Final

_LINE_BREAK: Final[re.Pattern[str]] = re.compile(r"\r\n|\r|\n")


@dataclass(frozen=True, slots=True, kw_only=True)
class Line:
    """One line of the text: its half-open span and its text, without the break."""

    start: int
    end: int
    text: str


def split_lines(text: str) -> tuple[Line, ...]:
    """Split text at CRLF, CR and LF line breaks.

    Input:   the document text.
    Output:  every line in order. The text after the last break is a line even
             when it is empty, so an empty text gives one empty line.
    Effects: none.
    """

    lines: list[Line] = []
    start = 0
    for break_match in _LINE_BREAK.finditer(text):
        end = break_match.start()
        lines.append(Line(start=start, end=end, text=text[start:end]))
        start = break_match.end()
    lines.append(Line(start=start, end=len(text), text=text[start:]))
    return tuple(lines)


def is_blank(line: Line) -> bool:
    """True when the line holds only spaces and tabs."""

    return line.text.strip() == ""
