"""Overrides, and the direction they take (S3-M4-T1, S3-M4-T2).

An override names a target clause, or names nothing. A target that does not
resolve gives no override: the reference stays visible with no target
(Spec 5, question 5).
"""

import re

from clause_tracer.core import (
    Clause,
    ClauseId,
    CrossReference,
    OutsideDocument,
    Override,
    Sentence,
    Span,
)
from clause_tracer.links._index import ClauseIndex
from clause_tracer.links._patterns import (
    GENERAL_OVERRIDE_RE,
    NOTWITHSTANDING_RE,
    OVERRIDE_GAP_RE,
    PREVAILS_RE,
    QUALIFIER_RE,
    SELF_NAME_RE,
    SENTENCE_LEAD_RE,
    SEPARATOR_RE,
    THIS_REFERENCE_RE,
    WINNER_LEFTOVER_RE,
)
from clause_tracer.links._spans import trimmed

_Group = tuple[Span, tuple[CrossReference, ...]]
_Phrase = tuple[re.Match[str], bool]


def find_overrides(
    text: str,
    index: ClauseIndex,
    references: tuple[CrossReference, ...],
    outside: tuple[OutsideDocument, ...],
) -> tuple[Override, ...]:
    """Find every override, with its direction.

    Input:   the canonical text, its clause index, the cross-references and
             the documents that are not loaded.
    Output:  one override for each target, sorted by evidence start and then
             by target; an identical override is kept once.
    Raises:  nothing.
    Effects: none (T1).
    """

    target_references = _without_self_references(text, references)
    directional = _directional_overrides(text, index, target_references, outside)
    overrides: list[Override] = list(directional)
    overrides.extend(_prevails_overrides(text, index, target_references, outside, directional))
    return _sorted_unique(overrides)


def _without_self_references(
    text: str,
    references: tuple[CrossReference, ...],
) -> tuple[CrossReference, ...]:
    return tuple(
        reference
        for reference in references
        if THIS_REFERENCE_RE.fullmatch(text[reference.source.start : reference.source.end]) is None
    )


def _directional_overrides(
    text: str,
    index: ClauseIndex,
    references: tuple[CrossReference, ...],
    outside: tuple[OutsideDocument, ...],
) -> tuple[Override, ...]:
    groups = _groups(references)
    phrases = [(match, True) for match in NOTWITHSTANDING_RE.finditer(text)]
    phrases.extend((match, False) for match in QUALIFIER_RE.finditer(text))
    phrases.sort(key=lambda phrase: phrase[0].start())
    overrides: list[Override] = []
    for phrase, is_notwithstanding in phrases:
        clause = index.clause_at(phrase.start())
        sentence = index.sentence_at(phrase.start())
        if clause is None or sentence is None:
            continue
        is_heading_sentence = clause.heading is not None and sentence == clause.sentences[0]
        if is_heading_sentence:
            continue
        taken = _taken_groups(text, phrase, sentence, groups, phrases)
        if taken:
            evidence_end = taken[-1][0].end
            for _, group_references in taken:
                for reference in group_references:
                    if reference.target is None:
                        continue
                    overrides.append(
                        Override(
                            clause_id=clause.id,
                            target=reference.target,
                            overrides_target=is_notwithstanding,
                            evidence=Span(start=phrase.start(), end=evidence_end),
                        )
                    )
            continue
        if not is_notwithstanding:
            continue
        general = GENERAL_OVERRIDE_RE.match(text, phrase.end())
        if general is None:
            continue
        if _sentence_holds_an_outside_document(sentence, outside):
            continue
        overrides.append(
            Override(
                clause_id=clause.id,
                target=None,
                overrides_target=True,
                evidence=Span(start=phrase.start(), end=general.end()),
            )
        )
    return tuple(overrides)


def _groups(references: tuple[CrossReference, ...]) -> tuple[_Group, ...]:
    by_source: dict[Span, list[CrossReference]] = {}
    for reference in references:
        by_source.setdefault(reference.source, []).append(reference)
    ordered = sorted(by_source.items(), key=lambda item: (item[0].start, item[0].end))
    return tuple((source, tuple(group_references)) for source, group_references in ordered)


def _taken_groups(
    text: str,
    phrase: re.Match[str],
    sentence: Sentence,
    groups: tuple[_Group, ...],
    phrases: list[_Phrase],
) -> list[_Group]:
    candidates = [group for group in groups if phrase.end() <= group[0].start < sentence.span.end]
    if not candidates:
        return []
    first = candidates[0]
    if _another_phrase_starts_before(phrases, phrase, first[0].start):
        return []
    if OVERRIDE_GAP_RE.fullmatch(text[phrase.end() : first[0].start]) is None:
        return []
    taken = [first]
    for group in candidates[1:]:
        gap = text[taken[-1][0].end : group[0].start]
        if SEPARATOR_RE.fullmatch(gap) is None:
            break
        taken.append(group)
    return taken


def _another_phrase_starts_before(
    phrases: list[_Phrase],
    phrase: re.Match[str],
    first_start: int,
) -> bool:
    return any(
        other is not phrase and phrase.end() < other.start() < first_start for other, _ in phrases
    )


def _sentence_holds_an_outside_document(
    sentence: Sentence,
    outside: tuple[OutsideDocument, ...],
) -> bool:
    return any(
        sentence.span.start <= document.evidence.start < sentence.span.end for document in outside
    )


def _prevails_overrides(
    text: str,
    index: ClauseIndex,
    references: tuple[CrossReference, ...],
    outside: tuple[OutsideDocument, ...],
    directional: tuple[Override, ...],
) -> tuple[Override, ...]:
    overrides: list[Override] = []
    for clause in index.clauses:
        for sentence in clause.sentences:
            found = _prevails_for_sentence(text, clause, sentence, references, outside, directional)
            overrides.extend(found)
    return tuple(overrides)


def _prevails_for_sentence(
    text: str,
    clause: Clause,
    sentence: Sentence,
    references: tuple[CrossReference, ...],
    outside: tuple[OutsideDocument, ...],
    directional: tuple[Override, ...],
) -> tuple[Override, ...]:
    verb = PREVAILS_RE.search(text, sentence.span.start, sentence.span.end)
    if verb is None:
        return ()
    is_heading_sentence = clause.heading is not None and sentence == clause.sentences[0]
    if is_heading_sentence:
        return ()
    sentence_references = tuple(
        reference
        for reference in references
        if sentence.span.start <= reference.source.start < sentence.span.end
    )
    sentence_outside = tuple(
        document
        for document in outside
        if sentence.span.start <= document.evidence.start < sentence.span.end
    )
    winner_start = _winner_start(text, sentence, verb.start(), sentence_references)
    winner_end = verb.start()
    self_names = tuple(SELF_NAME_RE.finditer(text, winner_start, winner_end))
    references_in_winner = tuple(
        reference
        for reference in sentence_references
        if _overlaps_winner(reference.source, winner_start, winner_end)
    )
    leftover = _winner_leftover(text, winner_start, winner_end, self_names, sentence_references)
    if WINNER_LEFTOVER_RE.fullmatch(leftover) is None:
        return ()
    evidence = trimmed(text, sentence.span)
    if self_names:
        if references_in_winner:
            return ()
        directional_targets = {
            override.target
            for override in directional
            if override.clause_id == clause.id
            and sentence.span.start <= override.evidence.start < sentence.span.end
        }
        losers = [
            reference
            for reference in sentence_references
            if not _overlaps_winner(reference.source, winner_start, winner_end)
            and reference.target is not None
            and reference.target not in directional_targets
        ]
        if losers:
            return tuple(
                Override(
                    clause_id=clause.id,
                    target=loser.target,
                    overrides_target=True,
                    evidence=evidence,
                )
                for loser in losers
            )
        names_nothing = _names_nothing(
            text,
            sentence,
            sentence_references,
            sentence_outside,
            self_names,
            verb,
            winner_start,
            winner_end,
        )
        if names_nothing:
            return (
                Override(
                    clause_id=clause.id,
                    target=None,
                    overrides_target=True,
                    evidence=evidence,
                ),
            )
        return ()
    winners = [
        reference
        for reference in sentence_references
        if winner_start <= reference.source.start < winner_end
    ]
    if not winners:
        return ()
    first_start = min(reference.source.start for reference in winners)
    return tuple(
        Override(
            clause_id=clause.id,
            target=reference.target,
            overrides_target=False,
            evidence=evidence,
        )
        for reference in winners
        if reference.source.start == first_start and reference.target is not None
    )


def _winner_start(
    text: str,
    sentence: Sentence,
    verb_start: int,
    sentence_references: tuple[CrossReference, ...],
) -> int:
    comma_end = sentence.span.start
    for position in range(sentence.span.start, verb_start):
        if text[position] != ",":
            continue
        inside_reference = any(
            reference.source.start <= position < reference.source.end
            for reference in sentence_references
        )
        if not inside_reference:
            comma_end = position + 1
    lead = SENTENCE_LEAD_RE.match(text, sentence.span.start, sentence.span.end)
    lead_end = sentence.span.start
    if lead is not None:
        reference_starts_in_lead = any(
            reference.source.start < lead.end() for reference in sentence_references
        )
        if not reference_starts_in_lead:
            lead_end = lead.end()
    return max(comma_end, lead_end)


def _overlaps_winner(source: Span, winner_start: int, winner_end: int) -> bool:
    return source.start < winner_end and source.end > winner_start


def _winner_leftover(
    text: str,
    winner_start: int,
    winner_end: int,
    self_names: tuple[re.Match[str], ...],
    sentence_references: tuple[CrossReference, ...],
) -> str:
    characters = list(text[winner_start:winner_end])
    for match in self_names:
        _blank(characters, winner_start, winner_end, match.start(), match.end())
    for reference in sentence_references:
        _blank(
            characters,
            winner_start,
            winner_end,
            reference.source.start,
            reference.source.end,
        )
    return "".join(characters)


def _blank(
    characters: list[str],
    winner_start: int,
    winner_end: int,
    start: int,
    end: int,
) -> None:
    left = max(start, winner_start) - winner_start
    right = min(end, winner_end) - winner_start
    for position in range(left, right):
        characters[position] = " "


def _names_nothing(
    text: str,
    sentence: Sentence,
    sentence_references: tuple[CrossReference, ...],
    sentence_outside: tuple[OutsideDocument, ...],
    self_names: tuple[re.Match[str], ...],
    verb: re.Match[str],
    winner_start: int,
    winner_end: int,
) -> bool:
    last_word = self_names[0].group(0).split()[-1].casefold()
    names_clause_or_section = last_word in ("clause", "section", "paragraph")
    no_reference_outside = all(
        _overlaps_winner(reference.source, winner_start, winner_end)
        for reference in sentence_references
    )
    no_outside_document = not sentence_outside
    closing = text[verb.end() : trimmed(text, sentence.span).end]
    only_closing = all(character.isspace() or character in ".;:" for character in closing)
    return names_clause_or_section and no_reference_outside and no_outside_document and only_closing


def _sorted_unique(overrides: list[Override]) -> tuple[Override, ...]:
    ordered = sorted(
        overrides,
        key=lambda override: (override.evidence.start, _target_key(override.target)),
    )
    kept: list[Override] = []
    seen: set[Override] = set()
    for override in ordered:
        if override in seen:
            continue
        seen.add(override)
        kept.append(override)
    return tuple(kept)


def _target_key(target: ClauseId | None) -> str:
    return "" if target is None else str(target)
