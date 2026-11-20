"""Overrides, and the direction they take (S3-M4-T1).

An override names a target clause, or names nothing. A target that does not
resolve gives no override: the reference stays visible with no target
(Spec 5, question 5).
"""

import re

from clause_tracer.core import (
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
    QUALIFIER_RE,
    SEPARATOR_RE,
    THIS_REFERENCE_RE,
)

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
    overrides: list[Override] = []
    overrides.extend(_directional_overrides(text, index, target_references, outside))
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
