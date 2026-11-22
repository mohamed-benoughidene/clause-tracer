"""Group variants into numbered entities (S4-M3-T7).

Variants of one name share one placeholder by default (Spec 4.2). A short form
that fits two or more full names gets its own placeholder, because code never
guesses (question 12). Numbers run by kind in order of first appearance (D2).
"""

import re
from collections.abc import Sequence

from clause_tracer.core import (
    Document,
    PiiSuggestion,
    PlaceholderEntity,
    PlaceholderKind,
)
from clause_tracer.privacy._spans import overlaps
from clause_tracer.privacy.names import EXTENDED_COMPANY_SUFFIXES, fold_text, strip_honorific


def _word_set(kind: PlaceholderKind, text: str) -> frozenset[str]:
    """The words that decide whether two texts are variants of one entity."""

    folded = fold_text(text).strip()
    words: list[str]
    if kind == PlaceholderKind.PERSON:
        words = list(strip_honorific(folded.split()))
    elif kind == PlaceholderKind.COMPANY:
        words = folded.split()
        if len(words) > 1 and words[-1].strip(".,") in EXTENDED_COMPANY_SUFFIXES:
            words = words[:-1]
    elif kind == PlaceholderKind.ADDRESS:
        words = [part for part in re.split(r"[\s,]+", folded) if part]
    elif kind == PlaceholderKind.PHONE:
        words = ["".join(character for character in folded if character.isdigit())]
    elif kind in (PlaceholderKind.ID, PlaceholderKind.BANK):
        words = ["".join(character for character in folded if character.isalnum())]
    else:
        words = [folded]
    cleaned = [word.strip(".,;:") for word in words]
    cleaned = [word for word in cleaned if word]
    if not cleaned:
        return frozenset({"\0" + folded})
    return frozenset(cleaned)


def group_entities(
    document: Document, suggestions: Sequence[PiiSuggestion]
) -> tuple[PlaceholderEntity, ...]:
    """Group suggestions into one numbered entity per name, in first-place order."""

    ordered = sorted(suggestions, key=lambda item: (item.span.start, item.span.end))
    previous = None
    for item in ordered:
        if item.span.start < 0 or item.span.end > len(document.text):
            raise ValueError("privacy: suggestion span is outside the text")
        if previous is not None and overlaps(previous, item.span):
            raise ValueError("privacy: suggestions overlap")
        previous = item.span

    entities: list[PlaceholderEntity] = []
    for kind in PlaceholderKind:
        of_kind = [item for item in ordered if item.kind == kind]
        if not of_kind:
            continue
        word_sets: list[frozenset[str]] = []
        for item in of_kind:
            text = document.text[item.span.start : item.span.end]
            found = _word_set(kind, text)
            if found not in word_sets:
                word_sets.append(found)
        heads = [
            word_set for word_set in word_sets if not any(word_set < other for other in word_sets)
        ]
        cluster_of: dict[frozenset[str], frozenset[str]] = {}
        for word_set in word_sets:
            bigger = [other for other in word_sets if word_set < other]
            if not bigger:
                cluster_of[word_set] = word_set
                continue
            containers = [head for head in heads if word_set < head]
            cluster_of[word_set] = containers[0] if len(containers) == 1 else word_set
        clusters: dict[frozenset[str], list[int]] = {}
        for index, item in enumerate(of_kind):
            text = document.text[item.span.start : item.span.end]
            cluster = cluster_of[_word_set(kind, text)]
            clusters.setdefault(cluster, []).append(index)
        for number, indexes in enumerate(clusters.values(), start=1):
            spans = tuple(sorted((of_kind[index].span for index in indexes), key=lambda s: s.start))
            entities.append(
                PlaceholderEntity(
                    id=f"{kind.value}-{number}",
                    kind=kind,
                    number=number,
                    spans=spans,
                )
            )
    return tuple(sorted(entities, key=lambda entity: entity.spans[0].start))
