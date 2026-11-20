"""Cross-references between clauses (S3-M2-T2 to S3-M2-T4).

A reference keeps its evidence span in the canonical text. An unresolved
target is kept with no target, so a miss stays visible (Spec 5).
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Final

from clause_tracer.core import ClauseId, CrossReference, Span
from clause_tracer.links._index import ClauseIndex
from clause_tracer.links._numbers import normalise_number, roman_to_int
from clause_tracer.links._patterns import (
    ARTICLE_REFERENCE,
    NUMBER_REFERENCE,
    OF_DOCUMENT_RE,
    SCHEDULE_REFERENCE,
    SEPARATOR,
)

_ARTICLE_BASE_RE: Final[re.Pattern[str]] = re.compile(r"[0-9]{1,3}|[IVXLC]{1,7}")
_SCHEDULE_BASE_RE: Final[re.Pattern[str]] = re.compile(r"[0-9]{1,3}|[A-Z]")
_OWN_NUMBER_CHARS: Final[frozenset[str]] = frozenset({" ", "\t", "#", "*", ">", "-", "_"})


class _Family(Enum):
    NUMBER = "number"
    ARTICLE = "article"
    SCHEDULE = "schedule"


@dataclass(frozen=True, slots=True, kw_only=True)
class _Key:
    """One item of a reference: the list key, and the key used to resolve."""

    written: str
    resolution: str | None


def find_references(text: str, index: ClauseIndex) -> tuple[CrossReference, ...]:
    """Find every cross-reference, in text order.

    Input:   the canonical text and its clause index.
    Output:  one reference for each target, with its evidence span; an
             unresolved target is None.
    Raises:  nothing.
    Effects: none (T1).
    """

    found: list[CrossReference] = []
    for pattern, family in (
        (NUMBER_REFERENCE, _Family.NUMBER),
        (ARTICLE_REFERENCE, _Family.ARTICLE),
        (SCHEDULE_REFERENCE, _Family.SCHEDULE),
    ):
        for match in pattern.finditer(text):
            found.extend(_references_for_match(text, index, match, family))
    found.sort(key=lambda reference: reference.source.start)
    return tuple(found)


def _references_for_match(
    text: str,
    index: ClauseIndex,
    match: re.Match[str],
    family: _Family,
) -> tuple[CrossReference, ...]:
    items = _split_items(match.group("items"))
    keyword = match.group("kw")
    first = _parse_item(items[0], family, keyword)
    target = _target(text, index, match, keyword, first)
    if _is_own_number(text, index, match, items, target):
        return ()
    return (CrossReference(source=Span(start=match.start(), end=match.end()), target=target),)


def _split_items(raw: str) -> tuple[str, ...]:
    parts = re.split(f"({SEPARATOR})", raw)
    return tuple(parts[0::2])


def _parse_item(item: str, family: _Family, keyword: str) -> _Key:
    if family is _Family.NUMBER:
        key = normalise_number(item)
        return _Key(written=key, resolution=key)
    if family is _Family.ARTICLE:
        return _article_key(item)
    return _schedule_key(item, keyword)


def _article_key(item: str) -> _Key:
    match = _ARTICLE_BASE_RE.match(item)
    if match is None:
        return _Key(written=item, resolution=None)
    base = match.group(0)
    tail = item[len(base) :]
    if tail:
        return _Key(written=item, resolution=None)
    if base[0].isdigit():
        key = normalise_number(base)
        return _Key(written=key, resolution=key)
    try:
        key = str(roman_to_int(base))
    except ValueError:
        return _Key(written=item, resolution=None)
    return _Key(written=key, resolution=key)


def _schedule_key(item: str, keyword: str) -> _Key:
    match = _SCHEDULE_BASE_RE.match(item)
    if match is None:
        return _Key(written=keyword[0].upper() + item, resolution=None)
    base = match.group(0)
    tail = item[len(base) :]
    key = keyword[0].upper() + item
    if tail:
        return _Key(written=key, resolution=None)
    return _Key(written=key, resolution=key)


def _target(
    text: str,
    index: ClauseIndex,
    match: re.Match[str],
    keyword: str,
    key: _Key,
) -> ClauseId | None:
    if key.resolution is None:
        return None
    if OF_DOCUMENT_RE.match(text, match.end()) is not None:
        return None
    clause = index.clause_at(match.start())
    schedule = None if clause is None else index.in_schedule(clause)
    if schedule is None:
        return index.resolve(key.resolution)
    keyword_lower = keyword.casefold()
    if keyword_lower in ("paragraph", "paragraphs"):
        return index.resolve(schedule.id + "." + key.resolution)
    inside = index.resolve(schedule.id + "." + key.resolution)
    body = index.resolve(key.resolution)
    if inside is not None and body is not None:
        return None
    return inside if inside is not None else body


def _is_own_number(
    text: str,
    index: ClauseIndex,
    match: re.Match[str],
    items: tuple[str, ...],
    target: ClauseId | None,
) -> bool:
    if len(items) != 1 or target is None:
        return False
    clause = index.clause_at(match.start())
    if clause is None or target != clause.id:
        return False
    before = text[clause.span.start : match.start()]
    return all(character in _OWN_NUMBER_CHARS for character in before)
