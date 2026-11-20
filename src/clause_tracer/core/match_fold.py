"""The wide match fold, with its index map (system design 4.2; S2-M5-T2, S2-M5-T7).

`fold_for_quote_check` is the narrow Spec 2 fold, and the only one that
confirms a quote. This fold is the wide one that finds names, terms and
keywords: it normalises each character together with the combining marks
after it (NFKC), case-folds it, makes quotes straight and every dash one
hyphen, and drops the characters that could hide a word. Folding can change
the length (`ß` becomes `ss`), so a folded span is found through the map, never
by arithmetic on offsets.
"""

import unicodedata
from typing import Final

from clause_tracer.core.document import MatchKey

_DROPPED: Final[frozenset[str]] = frozenset(
    {
        "\u00ad",  # soft hyphen
        "\u200b",  # zero-width space
        "\u200c",  # zero-width non-joiner
        "\u200d",  # zero-width joiner
        "\u2060",  # word joiner
        "\ufeff",  # byte-order mark
        "\u202a",  # left-to-right embedding
        "\u202b",  # right-to-left embedding
        "\u202c",  # pop directional formatting
        "\u202d",  # left-to-right override
        "\u202e",  # right-to-left override
        "\u2066",  # left-to-right isolate
        "\u2067",  # right-to-left isolate
        "\u2068",  # first strong isolate
        "\u2069",  # pop directional isolate
    }
)

_SINGLE_QUOTES: Final[str] = "\u2018\u2019\u201a\u201b"
_DOUBLE_QUOTES: Final[str] = "\u201c\u201d\u201e\u201f"
_DASHES: Final[str] = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"


def _fold_one(cluster: str) -> str:
    """NFKC and case-fold one cluster, then make its quotes and dashes plain."""

    pieces: list[str] = []
    for folded in unicodedata.normalize("NFKC", cluster).casefold():
        if folded in _SINGLE_QUOTES:
            pieces.append("'")
        elif folded in _DOUBLE_QUOTES:
            pieces.append('"')
        elif folded in _DASHES:
            pieces.append("-")
        else:
            pieces.append(folded)
    return "".join(pieces)


def fold_for_matching(text: str) -> MatchKey:
    """Fold one text for finding names, terms and keywords.

    Input:   one text, usually a document's canonical text or a word to look
             for.
    Output:  the folded text and its index map: one entry per folded character,
             the index of the character it came from, plus a last entry equal
             to len(text). A combining mark maps to the index of the character
             it follows.
    Effects: none.
    """

    emitted: list[tuple[str, int]] = []
    index = 0
    while index < len(text):
        if text[index] in _DROPPED:
            index += 1
            continue
        cluster_end = index + 1
        while cluster_end < len(text):
            is_attached_mark = (
                text[cluster_end] not in _DROPPED and unicodedata.combining(text[cluster_end]) != 0
            )
            if not is_attached_mark:
                break
            cluster_end += 1
        for folded in _fold_one(text[index:cluster_end]):
            emitted.append((folded, index))
        index = cluster_end

    folded_characters: list[str] = []
    to_canonical: list[int] = []
    index = 0
    while index < len(emitted):
        character, source = emitted[index]
        is_space = character.isspace()
        if is_space:
            run_start = source
            while index < len(emitted) and emitted[index][0].isspace():
                index += 1
            folded_characters.append(" ")
            to_canonical.append(run_start)
            continue
        folded_characters.append(character)
        to_canonical.append(source)
        index += 1
    to_canonical.append(len(text))
    return MatchKey(text="".join(folded_characters), to_canonical=tuple(to_canonical))
