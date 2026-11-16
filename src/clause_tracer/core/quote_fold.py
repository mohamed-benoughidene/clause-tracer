"""The Spec 2 quote-check fold, with its index map (section 4.2).

One fold serves the quote check and the last check before drawing.
Curly quotes become straight, and a run of whitespace becomes one
space, so a quote matches however it was typed. The index map points
every folded character back at the character it came from, so the
confirmed span stays the span in the real text. Folding never changes
a character that the fold does not name: offsets count code points.
"""

from clause_tracer.core.checks import QuoteFold

_CURLY_SINGLES = "‘’‚‛"
_CURLY_DOUBLES = "“”„‟"


def fold_for_quote_check(text: str) -> QuoteFold:
    """Fold one text for the quote check, mapping every folded character
    back to where it came from. The map's last entry is len(text)."""

    folded: list[str] = []
    to_original: list[int] = []
    index = 0
    length = len(text)
    while index < length:
        character = text[index]
        in_whitespace_run = character.isspace()
        if in_whitespace_run:
            run_start = index
            while index < length and text[index].isspace():
                index += 1
            folded.append(" ")
            to_original.append(run_start)
            continue
        if character in _CURLY_SINGLES:
            folded.append("'")
        elif character in _CURLY_DOUBLES:
            folded.append('"')
        else:
            folded.append(character)
        to_original.append(index)
        index += 1
    to_original.append(length)
    return QuoteFold(text="".join(folded), to_original=tuple(to_original))
