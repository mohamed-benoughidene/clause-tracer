"""Cross-references between clauses (S3-M2-T2 to S3-M2-T4).

A reference keeps its evidence span in the canonical text. An unresolved
target is kept with no target, so a miss stays visible (Spec 5).
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Final

from clause_tracer.core import Clause, ClauseId, CrossReference, Span
from clause_tracer.links._index import ClauseIndex
from clause_tracer.links._numbers import expand_range, normalise_number, roman_to_int
from clause_tracer.links._patterns import (
    ARTICLE_REFERENCE,
    NUMBER_REFERENCE,
    OF_DOCUMENT_RE,
    SCHEDULE_REFERENCE,
    SEPARATOR_SPLIT_RE,
    THIS_REFERENCE_RE,
)

_ARTICLE_BASE_RE: Final[re.Pattern[str]] = re.compile(r"[0-9]{1,3}|[IVXLC]{1,7}")
_SCHEDULE_BASE_RE: Final[re.Pattern[str]] = re.compile(r"[0-9]{1,3}|[A-Z]")
_OWN_NUMBER_CHARS: Final[frozenset[str]] = frozenset({" ", "\t", "#", "*", ">", "-", "_"})
_RANGE_MARKERS: Final[frozenset[str]] = frozenset({"to", "-", "\u2013", "\u2014"})


class _Family(Enum):
    NUMBER = "number"
    ARTICLE = "article"
    SCHEDULE = "schedule"


@dataclass(frozen=True, slots=True, kw_only=True)
class _Key:
    """One item of a reference: the list key, and the key used to resolve."""

    written: str
    resolution: str | None
    schedule_letter: str | None = None
    schedule_digits: str | None = None


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
    found.extend(_this_references(text, index))
    found.sort(key=lambda reference: reference.source.start)
    return tuple(found)


def _this_references(text: str, index: ClauseIndex) -> tuple[CrossReference, ...]:
    references: list[CrossReference] = []
    for match in THIS_REFERENCE_RE.finditer(text):
        clause = index.clause_at(match.start())
        target = _this_target(index, match, clause)
        references.append(
            CrossReference(
                source=Span(start=match.start(), end=match.end()),
                target=target,
            )
        )
    return tuple(references)


def _this_target(
    index: ClauseIndex,
    match: re.Match[str],
    clause: Clause | None,
) -> ClauseId | None:
    if clause is None or clause.number is None or clause.numbering_source == "paragraphs":
        return None
    keyword = match.group("kw").casefold()
    if keyword in ("clause", "section", "paragraph", "sub-clause", "subclause"):
        return clause.id
    schedule = index.in_schedule(clause)
    return None if schedule is None else schedule.id


def _references_for_match(
    text: str,
    index: ClauseIndex,
    match: re.Match[str],
    family: _Family,
) -> tuple[CrossReference, ...]:
    items, separators = _split_items(match.group("items"))
    keyword = match.group("kw")
    parsed = [_parse_item(item, family, keyword) for item in items]
    keys = _expand_keys(parsed, separators, family)
    source = Span(start=match.start(), end=match.end())
    references: list[CrossReference] = []
    for key in keys:
        target = _target(text, index, match, keyword, key)
        if _is_own_number(text, index, match, items, key, target):
            continue
        references.append(CrossReference(source=source, target=target))
    return tuple(references)


def _split_items(raw: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    parts = SEPARATOR_SPLIT_RE.split(raw)
    return tuple(parts[0::2]), tuple(parts[1::2])


def _expand_keys(
    parsed: list[_Key],
    separators: tuple[str, ...],
    family: _Family,
) -> tuple[_Key, ...]:
    expanded: list[_Key] = [parsed[0]]
    for index, separator in enumerate(separators, start=1):
        if _is_range_separator(separator):
            expanded.extend(_expand_pair(expanded[-1], parsed[index], family))
        else:
            expanded.append(parsed[index])
    return _dedupe(expanded)


def _is_range_separator(separator: str) -> bool:
    return separator.strip() in _RANGE_MARKERS


def _expand_pair(first: _Key, second: _Key, family: _Family) -> tuple[_Key, ...]:
    if family is _Family.SCHEDULE:
        return _expand_schedule(first, second)
    if first.resolution is None or second.resolution is None:
        return (second,)
    expanded = expand_range(first.written, second.written)
    return tuple(_Key(written=key, resolution=key) for key in expanded[1:])


def _expand_schedule(first: _Key, second: _Key) -> tuple[_Key, ...]:
    if first.schedule_digits is None or second.schedule_digits is None:
        return (second,)
    letter = first.schedule_letter or ""
    expanded = expand_range(first.schedule_digits, second.schedule_digits)
    return tuple(
        _Key(
            written=letter + digits,
            resolution=letter + digits,
            schedule_letter=letter,
            schedule_digits=digits if _is_plain_digits(digits) else None,
        )
        for digits in expanded[1:]
    )


def _is_plain_digits(written: str) -> bool:
    return written.isdigit() and (len(written) == 1 or not written.startswith("0"))


def _dedupe(keys: list[_Key]) -> tuple[_Key, ...]:
    seen: set[str] = set()
    kept: list[_Key] = []
    for key in keys:
        if key.written in seen:
            continue
        seen.add(key.written)
        kept.append(key)
    return tuple(kept)


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
    letter = keyword[0].upper()
    match = _SCHEDULE_BASE_RE.match(item)
    if match is None:
        return _Key(written=letter + item, resolution=None, schedule_letter=letter)
    base = match.group(0)
    tail = item[len(base) :]
    key = letter + item
    if tail:
        return _Key(written=key, resolution=None, schedule_letter=letter)
    return _Key(
        written=key,
        resolution=key,
        schedule_letter=letter,
        schedule_digits=item if _is_plain_digits(item) else None,
    )


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
    key: _Key,
    target: ClauseId | None,
) -> bool:
    resolution = key.resolution
    if len(items) != 1 or resolution is None:
        return False
    clause = index.clause_at(match.start())
    if clause is None:
        return False
    before = text[clause.span.start : match.start()]
    only_markup_before = all(character in _OWN_NUMBER_CHARS for character in before)
    if not only_markup_before:
        return False
    same_clause = target == clause.id
    if same_clause:
        return True
    if target is not None:
        return False
    base = str(clause.id).split("~", 1)[0]
    schedule = index.in_schedule(clause)
    candidates = {resolution}
    if schedule is not None:
        candidates.add(schedule.id + "." + resolution)
    return base in candidates
