"""The place named in the governing-law clause (S4-M3-T3).

Spec 4.2 keeps that place only when it is a country, a nation of the United
Kingdom, a US state, a Canadian province or an Australian state. The list is
the owner's (`_place_list.py`, S4-M2-T11); this file reads it and never edits it.
"""

import re
from collections.abc import Iterable
from typing import Final

from clause_tracer.core import Span
from clause_tracer.privacy._patterns import GOVERNING_LAW_CUE, PLACE_END
from clause_tracer.privacy._place_list import (
    AU_STATES,
    CA_PROVINCES,
    COUNTRIES,
    COUNTRIES_MULTI,
    UK_NATIONS,
    US_STATES,
)

US_STATE_BARE: Final[bool] = False
US_COMMONWEALTH: Final[bool] = False


def _alternation(names: Iterable[str]) -> str:
    return (
        "(?:" + "|".join(re.escape(n) for n in sorted(set(names), key=lambda n: (-len(n), n))) + ")"
    )


def _build_place_re() -> re.Pattern[str]:
    countries = COUNTRIES + COUNTRIES_MULTI
    us_prefix = r"(?:State|Commonwealth)" if US_COMMONWEALTH else "State"
    alternatives = [
        rf"(?:Republic|Kingdom)[ \t]+of[ \t]+{_alternation(countries)}",
        _alternation(countries + UK_NATIONS),
        rf"{us_prefix}[ \t]+of[ \t]+{_alternation(US_STATES)}",
        rf"(?:State[ \t]+of[ \t]+)?{_alternation(AU_STATES)}",
        rf"(?:Province[ \t]+of[ \t]+)?{_alternation(CA_PROVINCES)}",
    ]
    if US_STATE_BARE:
        alternatives.append(_alternation(US_STATES))
    return re.compile(GOVERNING_LAW_CUE + "(?P<p>(?:" + "|".join(alternatives) + "))" + PLACE_END)


PLACE_RE: Final[re.Pattern[str]] = _build_place_re()


def governing_law_places(text: str) -> tuple[Span, ...]:
    """The kept place of every governing-law phrase in `text`, in order."""

    return tuple(
        Span(start=match.start("p"), end=match.end("p")) for match in PLACE_RE.finditer(text)
    )
