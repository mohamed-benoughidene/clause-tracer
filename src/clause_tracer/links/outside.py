"""Documents that are not loaded, named in the contract (S3-M3-T3).

A name is one to four capitalised words followed by a document noun. The
contract's own name and title are not outside documents, and neither is a
term inside its own definition quotes (Spec 4.5, Rule 10).
"""

from clause_tracer.core import OutsideDocument, Span, fold_for_matching
from clause_tracer.links._index import ClauseIndex
from clause_tracer.links._patterns import (
    DROPPED_FIRST_WORDS,
    OUTSIDE_DOCUMENT_RE,
    OUTSIDE_NAME_RE,
    OWN_NAME_DEFINITION_RE,
    THIS_BEFORE_RE,
)
from clause_tracer.links._spans import build_span_set, trimmed
from clause_tracer.links.terms import Definition

_THIS_BEFORE_WINDOW: int = 10


def find_outside_documents(
    text: str,
    index: ClauseIndex,
    definitions: tuple[Definition, ...],
) -> tuple[OutsideDocument, ...]:
    """Find every mention of a document that is not loaded, in text order.

    Input:   the canonical text, its clause index and the definitions.
    Output:  one entry for each mention; each mention is kept.
    Raises:  nothing.
    Effects: none (T1).
    """

    quoted_set = build_span_set(definition.quoted for definition in definitions)
    own_terms = frozenset(
        fold_for_matching(definition.term).text
        for definition in definitions
        if OWN_NAME_DEFINITION_RE.search(
            text[definition.definition.start : definition.definition.end]
        )
    )
    own_title = _own_title(index)
    found: list[OutsideDocument] = []
    for clause in index.clauses:
        for sentence_index, sentence in enumerate(clause.sentences):
            if _is_heading_sentence(clause.heading, sentence_index):
                continue
            sentence_end = trimmed(text, sentence.span).end
            for match in OUTSIDE_DOCUMENT_RE.finditer(text, sentence.span.start, sentence_end):
                start = _start_after_dropped_words(text, match.start(), match.end())
                if start is None:
                    continue
                if OUTSIDE_NAME_RE.fullmatch(text, start, match.end()) is None:
                    continue
                if _follows_this(text, start):
                    continue
                evidence = Span(start=start, end=match.end())
                if quoted_set.overlaps(evidence):
                    continue
                folded = fold_for_matching(text[start : match.end()]).text
                if folded in own_terms or folded == own_title:
                    continue
                found.append(OutsideDocument(name=text[start : match.end()], evidence=evidence))
    return tuple(found)


def _start_after_dropped_words(text: str, start: int, end: int) -> int | None:
    """Move past leading words such as `The`; None when no word is left."""

    current = start
    while True:
        word_end = current
        while word_end < end and not text[word_end].isspace():
            word_end += 1
        if text[current:word_end] not in DROPPED_FIRST_WORDS:
            return current
        while word_end < end and text[word_end].isspace():
            word_end += 1
        if word_end >= end:
            return None
        current = word_end


def _follows_this(text: str, start: int) -> bool:
    before = text[max(0, start - _THIS_BEFORE_WINDOW) : start]
    return THIS_BEFORE_RE.search(before) is not None


def _own_title(index: ClauseIndex) -> str:
    for clause in index.clauses:
        if clause.heading is not None:
            return fold_for_matching(clause.heading).text
    return ""


def _is_heading_sentence(heading: str | None, sentence_index: int) -> bool:
    return heading is not None and sentence_index == 0
