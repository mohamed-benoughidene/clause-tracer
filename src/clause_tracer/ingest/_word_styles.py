"""The style cascade of the Word reader (S5-M3-T2).

A run's properties come from the document defaults, then the paragraph
style chain, then the character style chain, and the last explicit value
wins. Only the current properties are read: a change record is not a
property, so the values it holds are never read.
"""

from __future__ import annotations

import contextlib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Final

from clause_tracer.ingest._xml import W_NS, Element, qname

_VAL: Final[str] = qname(W_NS, "val")
_FILL: Final[str] = qname(W_NS, "fill")
_ASCII: Final[str] = qname(W_NS, "ascii")
_H_ANSI: Final[str] = qname(W_NS, "hAnsi")
_STYLE_ID: Final[str] = qname(W_NS, "styleId")

_VANISH: Final[str] = qname(W_NS, "vanish")
_COLOR: Final[str] = qname(W_NS, "color")
_SIZE: Final[str] = qname(W_NS, "sz")
_SHD: Final[str] = qname(W_NS, "shd")
_HIGHLIGHT: Final[str] = qname(W_NS, "highlight")
_RFONTS: Final[str] = qname(W_NS, "rFonts")
_RPR: Final[str] = qname(W_NS, "rPr")
_PPR: Final[str] = qname(W_NS, "pPr")
_BASED_ON: Final[str] = qname(W_NS, "basedOn")
_DOC_DEFAULTS: Final[str] = qname(W_NS, "docDefaults")
_RPR_DEFAULT: Final[str] = qname(W_NS, "rPrDefault")
_STYLE: Final[str] = qname(W_NS, "style")

_OFF_VALUES: Final[frozenset[str]] = frozenset({"false", "off", "0"})
_NONE_VALUES: Final[frozenset[str]] = frozenset({"auto", "none"})

_MAX_CHAIN_STEPS: Final[int] = 20

HIGHLIGHT_COLOURS: Final[Mapping[str, str]] = {
    "black": "000000",
    "blue": "0000FF",
    "cyan": "00FFFF",
    "green": "00FF00",
    "magenta": "FF00FF",
    "red": "FF0000",
    "yellow": "FFFF00",
    "white": "FFFFFF",
    "darkBlue": "000080",
    "darkCyan": "008080",
    "darkGreen": "008000",
    "darkMagenta": "800080",
    "darkRed": "800000",
    "darkYellow": "808000",
    "darkGray": "808080",
    "lightGray": "C0C0C0",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class RunProps:
    """The properties a run draws with, after the cascade."""

    vanish: bool = False
    color: str | None = None
    size_half_points: int | None = None
    fill: str | None = None
    highlight: str | None = None
    font: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class _Style:
    based_on: str | None
    rpr: Element | None
    ppr: Element | None


def _child(element: Element, local: str) -> Element | None:
    tag = qname(W_NS, local)
    for child in element:
        if child.tag == tag:
            return child
    return None


def _colour(value: str) -> str | None:
    if value in _NONE_VALUES:
        return None
    return value.upper()


def _is_on(element: Element) -> bool:
    value = element.get(_VAL)
    return value is None or value not in _OFF_VALUES


def _apply_rpr(props: RunProps, rpr: Element) -> RunProps:
    for child in rpr:
        tag = child.tag
        if tag == _VANISH:
            props = replace(props, vanish=_is_on(child))
        elif tag == _COLOR:
            value = child.get(_VAL)
            if value is not None:
                props = replace(props, color=_colour(value))
        elif tag == _SIZE:
            value = child.get(_VAL)
            if value is not None:
                with contextlib.suppress(ValueError):
                    props = replace(props, size_half_points=int(value))
        elif tag == _SHD:
            value = child.get(_FILL)
            if value is not None:
                props = replace(props, fill=_colour(value))
        elif tag == _HIGHLIGHT:
            value = child.get(_VAL)
            if value == "none":
                props = replace(props, highlight=None)
            elif value is not None and value in HIGHLIGHT_COLOURS:
                props = replace(props, highlight=HIGHLIGHT_COLOURS[value])
        elif tag == _RFONTS:
            font = child.get(_ASCII)
            if font is None:
                font = child.get(_H_ANSI)
            if font is not None:
                props = replace(props, font=font)
    return props


def _fill_of(ppr: Element, current: str | None) -> str | None:
    shading = _child(ppr, "shd")
    if shading is None:
        return current
    value = shading.get(_FILL)
    if value is None:
        return current
    return _colour(value)


class Styles:
    """The styles of one `word/styles.xml`, read once."""

    __slots__ = ("_default_rpr", "_styles")

    def __init__(
        self,
        *,
        default_rpr: Element | None = None,
        styles: Mapping[str, _Style] | None = None,
    ) -> None:
        self._default_rpr = default_rpr
        self._styles: Mapping[str, _Style] = styles or {}

    @classmethod
    def from_xml(cls, root: Element | None) -> Styles:
        """Read a parsed `word/styles.xml`; `None` gives empty styles."""

        if root is None:
            return cls()
        default_rpr: Element | None = None
        defaults = _child(root, "docDefaults")
        if defaults is not None:
            run_default = _child(defaults, "rPrDefault")
            if run_default is not None:
                default_rpr = _child(run_default, "rPr")
        styles: dict[str, _Style] = {}
        for element in root:
            if element.tag != _STYLE:
                continue
            style_id = element.get(_STYLE_ID)
            if style_id is None:
                continue
            based_on_element = _child(element, "basedOn")
            based_on = based_on_element.get(_VAL) if based_on_element is not None else None
            styles[style_id] = _Style(
                based_on=based_on,
                rpr=_child(element, "rPr"),
                ppr=_child(element, "pPr"),
            )
        return cls(default_rpr=default_rpr, styles=styles)

    def _chain_ids(self, style_id: str | None) -> list[str]:
        ids: list[str] = []
        seen: set[str] = set()
        current = style_id
        while current is not None and current not in seen and len(ids) < _MAX_CHAIN_STEPS:
            seen.add(current)
            if current not in self._styles:
                break
            ids.append(current)
            current = self._styles[current].based_on
        ids.reverse()
        return ids

    def numbering(self, *, paragraph_style: str | None) -> tuple[str, str | None, str] | None:
        """Return the list id, the level and the style that gave the list.

        The list and the level come from the nearest style that sets each,
        so a child style can set only one of them.
        """

        num_id: str | None = None
        ilvl: str | None = None
        num_style: str | None = None
        for style_id in reversed(self._chain_ids(paragraph_style)):
            style = self._styles[style_id]
            if style.ppr is None:
                continue
            num_pr = _child(style.ppr, "numPr")
            if num_pr is None:
                continue
            if num_id is None:
                num_id_element = _child(num_pr, "numId")
                value = num_id_element.get(_VAL) if num_id_element is not None else None
                if value is not None:
                    num_id = value
                    num_style = style_id
            if ilvl is None:
                ilvl_element = _child(num_pr, "ilvl")
                value = ilvl_element.get(_VAL) if ilvl_element is not None else None
                if value is not None:
                    ilvl = value
        if num_id is None or num_style is None:
            return None
        return num_id, ilvl, num_style

    def _chain(self, style_id: str | None) -> list[_Style]:
        chain: list[_Style] = []
        seen: set[str] = set()
        current = style_id
        while current is not None and current not in seen and len(chain) < _MAX_CHAIN_STEPS:
            seen.add(current)
            style = self._styles.get(current)
            if style is None:
                break
            chain.append(style)
            current = style.based_on
        chain.reverse()
        return chain

    def run_props(
        self,
        *,
        paragraph_style: str | None,
        run_style: str | None,
        rpr: Element | None,
    ) -> RunProps:
        """Return the properties of a run, after the whole cascade."""

        props = RunProps()
        if self._default_rpr is not None:
            props = _apply_rpr(props, self._default_rpr)
        for style in self._chain(paragraph_style):
            if style.rpr is not None:
                props = _apply_rpr(props, style.rpr)
        for style in self._chain(run_style):
            if style.rpr is not None:
                props = _apply_rpr(props, style.rpr)
        if rpr is not None:
            props = _apply_rpr(props, rpr)
        return props

    def paragraph_fill(self, *, paragraph_style: str | None, ppr: Element | None) -> str | None:
        """Return the fill of a paragraph, after its style chain."""

        fill: str | None = None
        for style in self._chain(paragraph_style):
            if style.ppr is not None:
                fill = _fill_of(style.ppr, fill)
        if ppr is not None:
            fill = _fill_of(ppr, fill)
        return fill
