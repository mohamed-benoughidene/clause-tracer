"""Defined terms, their uses, and terms used but never defined (S3-M3-T1, T2, T4).

A definition keeps its term as the quotes hold it, the span of the term
inside the quotes, and the trimmed span of the sentence that defines it.
The uses of a term are found on the wide match fold and mapped back, so a
folded span is never confirmed by arithmetic on offsets (system design 4.2).
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass

from clause_tracer.core import (
    DefinedTerm,
    MatchKey,
    Sentence,
    Span,
    fold_for_matching,
)
from clause_tracer.links._index import ClauseIndex
from clause_tracer.links._patterns import (
    AND_LEAD_END_RE,
    BRACKET_DEFINITION_RE,
    LIST_LEAD_END_RE,
    MEANS_DEFINITION_RE,
    SENTENCE_LEAD_RE,
    UNDEFINED_RUN_RE,
)
from clause_tracer.links._spans import SpanSet, build_span_set, trimmed


@dataclass(frozen=True, slots=True, kw_only=True)
class Definition:
    """One definition the text gives, with the term's span inside the quotes."""

    term: str
    quoted: Span
    definition: Span


def find_definitions(text: str, index: ClauseIndex) -> tuple[Definition, ...]:
    """Find every definition, in text order by the term's span.

    Input:   the canonical text and its clause index.
    Output:  one definition for each quoted term the text defines.
    Raises:  nothing.
    Effects: none (T1).
    """

    found: list[Definition] = []
    previous: re.Match[str] | None = None
    for match in MEANS_DEFINITION_RE.finditer(text):
        sentence = index.sentence_at(match.start())
        follows_lead_in = _starts_its_sentence_or_follows_a_lead_in(text, index, match.start())
        has_earlier_accepted_match = (
            previous is not None
            and sentence is not None
            and index.sentence_at(previous.start()) == sentence
        )
        joins_previous = False
        if has_earlier_accepted_match and previous is not None:
            gap = text[previous.end() : match.start()]
            joins_previous = AND_LEAD_END_RE.search(gap) is not None
        if follows_lead_in or joins_previous:
            definition = _definition_from(text, index, match)
            if definition is not None:
                found.append(definition)
                previous = match
    for match in BRACKET_DEFINITION_RE.finditer(text):
        definition = _definition_from(text, index, match)
        if definition is not None:
            found.append(definition)
    found.sort(key=lambda definition: definition.quoted.start)
    return tuple(found)


def _definition_from(
    text: str,
    index: ClauseIndex,
    match: re.Match[str],
) -> Definition | None:
    sentence = index.sentence_at(match.start())
    if sentence is None:
        return None
    return Definition(
        term=match.group("term"),
        quoted=Span(start=match.start("term"), end=match.end("term")),
        definition=trimmed(text, sentence.span),
    )


def _starts_its_sentence_or_follows_a_lead_in(
    text: str,
    index: ClauseIndex,
    offset: int,
) -> bool:
    sentence = index.sentence_at(offset)
    if sentence is None:
        return False
    starts_its_sentence = offset == _first_word_offset(text, sentence)
    if starts_its_sentence:
        return True
    return LIST_LEAD_END_RE.search(text[sentence.span.start : offset]) is not None


def _first_word_offset(text: str, sentence: Sentence) -> int:
    sentence_text = text[sentence.span.start : sentence.span.end]
    lead = SENTENCE_LEAD_RE.match(sentence_text)
    lead_end = 0 if lead is None else lead.end()
    return sentence.span.start + lead_end


def find_terms(
    text: str,
    key: MatchKey,
    definitions: tuple[Definition, ...],
) -> tuple[DefinedTerm, ...]:
    """Find the uses of every defined term, on the match key.

    Input:   the canonical text, its match key (built once by the caller) and
             the definitions.
    Output:  one entry for each definition, in definition order, with the uses
             of every term that folds to the same text.
    Raises:  nothing.
    Effects: none (T1).
    """

    quoted_set = build_span_set(definition.quoted for definition in definitions)
    groups = _groups(definitions)
    uses_by_folded: dict[str, tuple[Span, ...]] = {}
    kept_uses: list[Span] = []
    for folded in sorted(groups, key=lambda folded: (-len(folded), folded)):
        kept_set = build_span_set(kept_uses)
        uses = _find_uses(text, key, folded, quoted_set, kept_set)
        uses_by_folded[folded] = uses
        kept_uses.extend(uses)
    return tuple(
        DefinedTerm(
            term=definition.term,
            definition=definition.definition,
            uses=uses_by_folded[fold_for_matching(definition.term).text],
        )
        for definition in definitions
    )


def _groups(definitions: Iterable[Definition]) -> dict[str, list[Definition]]:
    groups: dict[str, list[Definition]] = {}
    for definition in definitions:
        folded = fold_for_matching(definition.term).text
        groups.setdefault(folded, []).append(definition)
    return groups


def _find_uses(
    text: str,
    key: MatchKey,
    folded: str,
    quoted_set: SpanSet,
    kept_set: SpanSet,
) -> tuple[Span, ...]:
    uses: list[Span] = []
    position = key.text.find(folded)
    while position != -1:
        after = position + len(folded)
        is_whole_word = _is_whole_word(key.text, position, after)
        if is_whole_word:
            span = Span(start=key.to_canonical[position], end=key.to_canonical[after])
            if (
                text[span.start].isupper()
                and not quoted_set.overlaps(span)
                and not kept_set.overlaps(span)
            ):
                uses.append(span)
        position = key.text.find(folded, position + 1)
    uses.sort(key=lambda span: span.start)
    return tuple(uses)


def _is_whole_word(folded_text: str, start: int, end: int) -> bool:
    before_is_free = start == 0 or not folded_text[start - 1].isalnum()
    after_is_free = end >= len(folded_text) or not folded_text[end].isalnum()
    return before_is_free and after_is_free


def find_undefined_terms(
    text: str,
    index: ClauseIndex,
    excluded: SpanSet,
) -> tuple[Span, ...]:
    """Find capitalised runs used but never defined, in text order.

    Input:   the canonical text, its clause index, and the spans that are not
             runs used but never defined (uses, quoted terms, outside names).
    Output:  one span for each run, sorted by start.
    Raises:  nothing.
    Effects: none (T1).
    """

    found: list[Span] = []
    for clause in index.clauses:
        for sentence_index, sentence in enumerate(clause.sentences):
            if _is_heading_sentence(clause.heading, sentence_index):
                continue
            sentence_text = text[sentence.span.start : sentence.span.end]
            if "\t" in sentence_text:
                continue
            first_word = _first_word_offset(text, sentence)
            sentence_end = trimmed(text, sentence.span).end
            for match in UNDEFINED_RUN_RE.finditer(text, sentence.span.start, sentence_end):
                span = Span(start=match.start(), end=match.end())
                if span.start == first_word:
                    continue
                if excluded.overlaps(span):
                    continue
                found.append(span)
    found.sort(key=lambda span: span.start)
    return tuple(found)


def _is_heading_sentence(heading: str | None, sentence_index: int) -> bool:
    return heading is not None and sentence_index == 0
