"""Sentence starts from NUPunkt, colon lines and table rows (S2-M3-T4, S2-M4-T7,
S2-M4-T14).

The sentence library is hidden in this file (B4). Callers get only the
code-point offsets where sentences start; a missed break only makes one
sentence longer, and the quote checks tolerate that (ADR 0007).

The sentence starts are the NUPunkt starts plus the starts after colon lines
and at table rows.
"""

from typing import Final

import nupunkt

from clause_tracer.ingest._lines import is_blank, split_lines

_COLON_TRAILING: Final[str] = " \t\u00a0\ufeff*_"
_COLONS: Final[tuple[str, ...]] = (":", "\uff1a")
_ROW_EDGE: Final[str] = " \t\u00a0\ufeff"


def colon_line_starts(text: str) -> tuple[int, ...]:
    """The start of the line after each line that ends in a colon.

    Input:   one text, usually a clause's body.
    Output:  the start of each line that follows a non-blank line ending in a
             colon, in order, as code-point offsets. A colon in the middle of a
             line, and a colon line with a blank line or no line after it, give
             no start.
    Effects: none.
    """

    lines = split_lines(text)
    starts: list[int] = []
    for index in range(len(lines) - 1):
        line_text = lines[index].text.rstrip(_COLON_TRAILING)
        is_colon_line = line_text.endswith(_COLONS)
        if is_colon_line and not is_blank(lines[index + 1]):
            starts.append(lines[index + 1].start)
    return tuple(starts)


def tab_line_starts(text: str) -> tuple[int, ...]:
    """The start of each table row: a line with a tab between two cells.

    Input:   one text, usually a clause's body.
    Output:  the start of each line with a tab that is not only at its start or
             its end (spaces, no-break spaces and byte-order marks around it do
             not count), in order, as code-point offsets. The first line of the
             text gives no start, because a sentence already starts there.
    Effects: none.
    """

    starts: list[int] = []
    for index, line in enumerate(split_lines(text)):
        is_table_row = "\t" in line.text.strip(_ROW_EDGE)
        if index > 0 and is_table_row:
            starts.append(line.start)
    return tuple(starts)


def sentence_starts(text: str) -> tuple[int, ...]:
    """The start offset of every sentence, from NUPunkt, colon lines and rows.

    Input:   one text, usually a clause's body.
    Output:  the start of each sentence in order, as code-point offsets into
             the text. An empty text gives an empty tuple.
    Effects: none.
    """

    library_starts = tuple(start for start, _end in nupunkt.sentence_spans(text))
    line_starts = set(colon_line_starts(text)) | set(tab_line_starts(text))
    return tuple(sorted(set(library_starts) | line_starts))
