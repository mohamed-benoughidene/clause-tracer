"""The list numbers of a Word body (S5-M3-T3).

Word stores the shape of a list once and the number of each paragraph in
the body. This module rebuilds the number Word shows, from the abstract
list, the list the paragraph uses, its level overrides and the counters
of one read. The labels are built in text order, one call for each
numbered paragraph.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from clause_tracer.ingest._thresholds import WORD_MAX_LETTER_REPEATS, WORD_MAX_LIST_START
from clause_tracer.ingest._word_styles import Styles, is_on
from clause_tracer.ingest._xml import W_NS, Element, qname

_VAL: Final[str] = qname(W_NS, "val")
_ILVL: Final[str] = qname(W_NS, "ilvl")

_ABSTRACT: Final[str] = qname(W_NS, "abstractNum")
_ABSTRACT_ID: Final[str] = qname(W_NS, "abstractNumId")
_NUM: Final[str] = qname(W_NS, "num")
_NUM_ID: Final[str] = qname(W_NS, "numId")
_LVL: Final[str] = qname(W_NS, "lvl")
_LVL_OVERRIDE: Final[str] = qname(W_NS, "lvlOverride")
_START_OVERRIDE: Final[str] = qname(W_NS, "startOverride")
_NUM_STYLE_LINK: Final[str] = qname(W_NS, "numStyleLink")

_REFERENCE: Final[re.Pattern[str]] = re.compile(r"%([1-9])")

_MAX_LVL_TEXT: Final[int] = 200
_MAX_LINK_STEPS: Final[int] = 10
_MAX_LEVEL: Final[int] = 8

_BULLET_FORMATS: Final[frozenset[str]] = frozenset({"bullet", "none"})


@dataclass(frozen=True, slots=True, kw_only=True)
class Label:
    """The number of one paragraph, and whether its format is known."""

    text: str | None
    unknown: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class _Level:
    start: int
    num_fmt: str
    lvl_text: str
    restart: int | None
    is_lgl: bool
    pstyle: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class _Abstract:
    style_link: str | None
    levels: Mapping[int, _Level]


@dataclass(frozen=True, slots=True, kw_only=True)
class _Num:
    abstract_id: str
    levels: Mapping[int, _Level]
    starts: Mapping[int, int]


def _child(element: Element, local: str) -> Element | None:
    tag = qname(W_NS, local)
    for child in element:
        if child.tag == tag:
            return child
    return None


def _value(element: Element | None) -> str | None:
    return element.get(_VAL) if element is not None else None


def _read_level(element: Element) -> tuple[int, _Level] | None:
    ilvl_value = element.get(_ILVL)
    ilvl = _whole(ilvl_value, 0, _MAX_LEVEL) if ilvl_value is not None else 0
    if ilvl is None:
        return None
    start = _whole(_value(_child(element, "start")), 0, WORD_MAX_LIST_START)
    restart = _whole(_value(_child(element, "lvlRestart")), 0, 9)
    is_lgl_element = _child(element, "isLgl")
    level = _Level(
        start=start if start is not None else 1,
        num_fmt=_value(_child(element, "numFmt")) or "decimal",
        lvl_text=_value(_child(element, "lvlText")) or "",
        restart=restart,
        is_lgl=is_lgl_element is not None and is_on(is_lgl_element),
        pstyle=_value(_child(element, "pStyle")),
    )
    return ilvl, level


def _whole(value: str | None, low: int, high: int) -> int | None:
    """Return a whole number inside the bounds, or `None` when it is not one."""

    if value is None:
        return None
    try:
        number = int(value)
    except ValueError:
        return None
    if low <= number <= high:
        return number
    return None


def _format(value: int, number_format: str) -> tuple[str | None, bool]:
    """Format one counter value; the second result says whether it is known."""

    if number_format == "decimal":
        return str(value), False
    if number_format == "decimalZero":
        return f"{value:02d}", False
    if number_format in ("upperLetter", "lowerLetter"):
        if value < 1 or value > 26 * WORD_MAX_LETTER_REPEATS:
            return None, True
        letter = chr(ord("a") + (value - 1) % 26)
        if number_format == "upperLetter":
            letter = letter.upper()
        return letter * ((value - 1) // 26 + 1), False
    if number_format in ("upperRoman", "lowerRoman"):
        if value < 1 or value > 3999:
            return None, True
        text = _roman(value)
        if number_format == "lowerRoman":
            text = text.lower()
        return text, False
    if number_format in _BULLET_FORMATS:
        return None, False
    return None, True


def _roman(value: int) -> str:
    numerals = (
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    )
    parts: list[str] = []
    remaining = value
    for amount, numeral in numerals:
        count, remaining = divmod(remaining, amount)
        parts.append(numeral * count)
    return "".join(parts)


def _restarts(level: _Level | None, used_level: int) -> bool:
    if level is None:
        return True
    if level.restart is None:
        return True
    if level.restart == 0:
        return False
    return used_level < level.restart


class Numbering:
    """The lists of one `word/numbering.xml`, with their counters."""

    __slots__ = ("_abstracts", "_counters", "_last_num", "_nums", "_styles")

    def __init__(
        self,
        *,
        abstracts: Mapping[str, _Abstract],
        nums: Mapping[str, _Num],
        styles: Styles,
    ) -> None:
        self._abstracts = abstracts
        self._nums = nums
        self._styles = styles
        self._counters: dict[tuple[str, int], int] = {}
        self._last_num: dict[str, str] = {}

    @classmethod
    def from_xml(cls, root: Element | None, styles: Styles) -> Numbering:
        """Read a parsed `word/numbering.xml`; `None` gives no lists."""

        abstracts: dict[str, _Abstract] = {}
        nums: dict[str, _Num] = {}
        if root is not None:
            for element in root:
                if element.tag == _ABSTRACT:
                    abstract_id = element.get(_ABSTRACT_ID)
                    if abstract_id is None:
                        continue
                    levels: dict[int, _Level] = {}
                    for child in element:
                        if child.tag == _LVL:
                            read = _read_level(child)
                            if read is not None:
                                levels[read[0]] = read[1]
                    abstracts[abstract_id] = _Abstract(
                        style_link=_value(_child(element, "numStyleLink")),
                        levels=levels,
                    )
                elif element.tag == _NUM:
                    num_id = element.get(_NUM_ID)
                    abstract_id = _value(_child(element, "abstractNumId"))
                    if num_id is None or abstract_id is None:
                        continue
                    levels = {}
                    starts = {}
                    for child in element:
                        if child.tag != _LVL_OVERRIDE:
                            continue
                        ilvl_value = child.get(_ILVL)
                        ilvl = _whole(ilvl_value, 0, _MAX_LEVEL) if ilvl_value is not None else 0
                        if ilvl is None:
                            continue
                        override = _child(child, "lvl")
                        if override is not None:
                            read = _read_level(override)
                            if read is not None:
                                levels[ilvl] = read[1]
                        start = _whole(
                            _value(_child(child, "startOverride")), 0, WORD_MAX_LIST_START
                        )
                        if start is not None:
                            starts[ilvl] = start
                    nums[num_id] = _Num(abstract_id=abstract_id, levels=levels, starts=starts)
        return cls(abstracts=abstracts, nums=nums, styles=styles)

    def _resolve(self, num: _Num) -> tuple[str, _Abstract, _Num] | None:
        abstract_id = num.abstract_id
        seen: set[str] = set()
        for _ in range(_MAX_LINK_STEPS + 1):
            abstract = self._abstracts.get(abstract_id)
            if abstract is None:
                return None
            if abstract.style_link is None:
                return abstract_id, abstract, num
            if abstract.style_link in seen:
                return None
            seen.add(abstract.style_link)
            style_numbers = self._styles.numbering(paragraph_style=abstract.style_link)
            if style_numbers is None:
                return None
            linked = self._nums.get(style_numbers[0])
            if linked is None:
                return None
            num = linked
            abstract_id = linked.abstract_id
        return None

    def level_for_style(self, *, num_id: str, style_id: str) -> int | None:
        """Return the level whose `w:pStyle` names the style, if any."""

        num = self._nums.get(num_id)
        if num is None:
            return None
        resolved = self._resolve(num)
        if resolved is None:
            return None
        _, abstract, _ = resolved
        for ilvl, level in abstract.levels.items():
            if level.pstyle == style_id:
                return ilvl
        return None

    def _enter_num(self, abstract_id: str, num_id: str, num: _Num) -> None:
        if self._last_num.get(abstract_id) == num_id:
            return
        self._last_num[abstract_id] = num_id
        for ilvl, start in num.starts.items():
            self._counters[(abstract_id, ilvl)] = start - 1

    def _advance(self, abstract_id: str, abstract: _Abstract, num: _Num, ilvl: int) -> None:
        for deeper in range(ilvl + 1, _MAX_LEVEL + 1):
            level = num.levels.get(deeper, abstract.levels.get(deeper))
            if _restarts(level, ilvl):
                self._counters.pop((abstract_id, deeper), None)
        key = (abstract_id, ilvl)
        if key in self._counters:
            self._counters[key] += 1
            return
        level = num.levels.get(ilvl, abstract.levels.get(ilvl))
        start = num.starts.get(ilvl)
        if start is None:
            start = level.start if level is not None else 1
        self._counters[key] = start

    def _value_of(self, abstract_id: str, abstract: _Abstract, num: _Num, ilvl: int) -> int:
        key = (abstract_id, ilvl)
        if key in self._counters:
            return self._counters[key]
        level = num.levels.get(ilvl, abstract.levels.get(ilvl))
        start = num.starts.get(ilvl)
        if start is not None:
            return start
        return level.start if level is not None else 1

    def _resolve_text(
        self,
        abstract_id: str,
        abstract: _Abstract,
        num: _Num,
        ilvl: int,
        level: _Level,
    ) -> tuple[str, bool]:
        is_unknown = False

        def replace(match: re.Match[str]) -> str:
            nonlocal is_unknown
            target = int(match.group(1)) - 1
            if target > ilvl:
                return ""
            value = self._value_of(abstract_id, abstract, num, target)
            if level.is_lgl:
                return str(value)
            target_level = num.levels.get(target, abstract.levels.get(target))
            if target_level is None:
                is_unknown = True
                return ""
            text, unknown = _format(value, target_level.num_fmt)
            if unknown:
                is_unknown = True
                return ""
            return text or ""

        return _REFERENCE.sub(replace, level.lvl_text), is_unknown

    def label(self, *, num_id: str, ilvl: int) -> Label:
        """Return the number of one paragraph and advance its counter."""

        if num_id == "0":
            return Label(text=None)
        num = self._nums.get(num_id)
        if num is None:
            return Label(text=None)
        resolved = self._resolve(num)
        if resolved is None:
            return Label(text=None, unknown=True)
        abstract_id, abstract, num = resolved
        self._enter_num(abstract_id, num_id, num)
        if ilvl < 0 or ilvl > _MAX_LEVEL:
            return Label(text=None, unknown=True)
        self._advance(abstract_id, abstract, num, ilvl)
        level = num.levels.get(ilvl, abstract.levels.get(ilvl))
        if level is None:
            return Label(text=None, unknown=True)
        if level.num_fmt in _BULLET_FORMATS:
            return Label(text=None)
        if len(level.lvl_text) > _MAX_LVL_TEXT:
            return Label(text=None, unknown=True)
        text, is_unknown = self._resolve_text(abstract_id, abstract, num, ilvl, level)
        if is_unknown:
            return Label(text=None, unknown=True)
        if len(text) > _MAX_LVL_TEXT:
            return Label(text=None, unknown=True)
        if text == "":
            return Label(text=None)
        return Label(text=text)
