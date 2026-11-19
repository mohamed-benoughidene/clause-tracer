"""Sentence starts from NUPunkt (S2-M3-T4).

The sentence library is hidden in this file (B4). Callers get only the
code-point offsets where sentences start; a missed break only makes one
sentence longer, and the quote checks tolerate that (ADR 0007).
"""

import nupunkt


def sentence_starts(text: str) -> tuple[int, ...]:
    """The start offset of every sentence NUPunkt finds.

    Input:   one text, usually a clause's body.
    Output:  the start of each sentence in order, as code-point offsets into
             the text. An empty text gives an empty tuple.
    Effects: none.
    """

    return tuple(start for start, _end in nupunkt.sentence_spans(text))
