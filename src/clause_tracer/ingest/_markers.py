"""Find a clause marker at the start of a line (S2-M3-T3).

A marker is the number, bracket, schedule heading or keyword that opens a
clause. The patterns stay hidden here (B4): the splitter asks one question and
gets the marker, its written number, the part its id is built from, and where
its body starts. The text itself is never changed (D1); Markdown symbols and a
byte-order mark stay in the text and the patterns look past them.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Final

from clause_tracer.ingest._numbering import paren_readings, roman_numeral_value


class MarkerKind(StrEnum):
    """The five kinds of marker that can open a clause: DECIMAL (1.2),
    PAREN ((a)), SCHEDULE (Schedule 1), KEYWORD (Article 5) and BARE (3 Term)."""

    DECIMAL = auto()
    PAREN = auto()
    SCHEDULE = auto()
    KEYWORD = auto()
    BARE = auto()


@dataclass(frozen=True, slots=True, kw_only=True)
class Marker:
    """One marker found at the start of a line."""

    kind: MarkerKind
    parts: tuple[int, ...]
    token: str
    written: str
    id_part: str
    body_start: int


PREFIX: Final[str] = r"[ \t\ufeff#*_]*"
CLOSE: Final[str] = r"(?:\*\*|__)?"
AFTER: Final[str] = r"(?=[ \t]|$)"

EMPHASIS_STRIP: Final[str] = " \t\ufeff#*_"
SCHEDULE_SEPARATORS: Final[str] = "\u00b7:-\u2013\u2014"
HEADING_STRIP: Final[str] = EMPHASIS_STRIP + "·:-–—"

SIGNATURE_OPENERS: Final[tuple[str, ...]] = ("signed", "executed", "in witness whereof")
SIGNATURE_BOUNDARY: Final[str] = " :,;.*_"

MONTH_NAMES: Final[frozenset[str]] = frozenset(
    {
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    }
)

_SCHEDULE: Final[re.Pattern[str]] = re.compile(
    PREFIX
    + r"(?P<word>(?i:schedule|annex|appendix|exhibit))[ \t]+"
    + r"(?P<des>[0-9]{1,3}|[A-Z])(?![0-9A-Za-z])"
)
_DECIMAL: Final[re.Pattern[str]] = re.compile(
    PREFIX + r"(?P<num>[0-9]{1,3}(?:\.[0-9]{1,3}){0,4})(?P<dot>\.)?" + CLOSE + AFTER
)
_PAREN: Final[re.Pattern[str]] = re.compile(
    PREFIX + r"\((?P<tok>[a-z]{1,6}|[A-Z]|[1-9][0-9]?)\)" + CLOSE + AFTER
)
_KEYWORD: Final[re.Pattern[str]] = re.compile(
    PREFIX
    + r"(?P<word>[Cc]lause|CLAUSE|[Aa]rticle|ARTICLE)[ \t]+"
    + r"(?P<num>[0-9]{1,3}|[IVXLCDM]{1,7})(?:[ \t]*[.:\u2013\u2014-])?"
    + CLOSE
    + r"(?=[ \t]*$|[ \t]+[A-Z])"
)
_CLOSING_PAREN: Final[re.Pattern[str]] = re.compile(
    PREFIX + r"(?P<tok>[a-z]{1,6})\)" + CLOSE + AFTER
)
_BARE: Final[re.Pattern[str]] = re.compile(
    PREFIX + r"(?P<num>[1-9][0-9]{0,2})" + CLOSE + r" +(?P<word>[A-Z][^ \t]*)"
)


def _body_start(line_text: str, match_end: int) -> int:
    """The first index after the match that is not a space or a tab."""

    index = match_end
    while index < len(line_text) and line_text[index] in " \t":
        index += 1
    return index


def _is_heading_like(line_text: str) -> bool:
    """True when a numbered line is short and does not end like a sentence."""

    stripped = line_text.strip(EMPHASIS_STRIP)
    return len(stripped) <= 100 and stripped[-1] not in ".;:,"


def _has_schedule_separator(line_text: str, designation_end: int) -> bool:
    """True when nothing follows the designation, or a separator does."""

    rest = line_text[designation_end:].lstrip(" \t")
    return rest == "" or rest[0] in SCHEDULE_SEPARATORS


def _find_schedule(line_text: str) -> Marker | None:
    match = _SCHEDULE.match(line_text)
    if match is None:
        return None
    if not _is_heading_like(line_text):
        return None
    if not _has_schedule_separator(line_text, match.end()):
        return None
    word = match.group("word")
    designation = match.group("des")
    id_part = word[0].upper() + designation
    return Marker(
        kind=MarkerKind.SCHEDULE,
        parts=(),
        token=id_part,
        written=f"{word} {designation}",
        id_part=id_part,
        body_start=_body_start(line_text, match.end()),
    )


def _find_decimal(line_text: str) -> Marker | None:
    match = _DECIMAL.match(line_text)
    if match is None:
        return None
    if match.group("dot") is None and "." not in match.group("num"):
        return None
    written = match.group("num")
    parts = tuple(int(part) for part in written.split("."))
    id_part = ".".join(str(part) for part in parts)
    return Marker(
        kind=MarkerKind.DECIMAL,
        parts=parts,
        token="",
        written=written,
        id_part=id_part,
        body_start=_body_start(line_text, match.end()),
    )


def _find_paren(line_text: str) -> Marker | None:
    match = _PAREN.match(line_text)
    if match is None:
        return None
    token = match.group("tok")
    if not paren_readings(token):
        return None
    return Marker(
        kind=MarkerKind.PAREN,
        parts=(),
        token=token,
        written=f"({token})",
        id_part=f"({token})",
        body_start=_body_start(line_text, match.end()),
    )


def _find_keyword(line_text: str) -> Marker | None:
    match = _KEYWORD.match(line_text)
    if match is None:
        return None
    word = match.group("word")
    num = match.group("num")
    if num.isdigit():
        if num.startswith("0"):
            return None
        value: int | None = int(num)
    else:
        value = roman_numeral_value(num)
    if value is None:
        return None
    return Marker(
        kind=MarkerKind.KEYWORD,
        parts=(value,),
        token="",
        written=f"{word} {num}",
        id_part=str(value),
        body_start=_body_start(line_text, match.end()),
    )


def _find_closing_paren(line_text: str) -> Marker | None:
    match = _CLOSING_PAREN.match(line_text)
    if match is None:
        return None
    token = match.group("tok")
    if not paren_readings(token):
        return None
    return Marker(
        kind=MarkerKind.PAREN,
        parts=(),
        token=token,
        written=f"{token})",
        id_part=f"({token})",
        body_start=_body_start(line_text, match.end()),
    )


def _find_bare(line_text: str) -> Marker | None:
    match = _BARE.match(line_text)
    if match is None:
        return None
    word = match.group("word")
    has_no_tab = "\t" not in line_text
    is_not_a_month = word.rstrip(",.;:") not in MONTH_NAMES
    is_heading_like = _is_heading_like(line_text)
    if not (has_no_tab and is_not_a_month and is_heading_like):
        return None
    num = match.group("num")
    return Marker(
        kind=MarkerKind.BARE,
        parts=(int(num),),
        token="",
        written=num,
        id_part=num,
        body_start=match.start("word"),
    )


_FINDERS: Final[tuple[Callable[[str], Marker | None], ...]] = (
    _find_schedule,
    _find_decimal,
    _find_paren,
    _find_keyword,
    _find_closing_paren,
    _find_bare,
)


def find_marker(line_text: str) -> Marker | None:
    """Find the first clause marker at the start of one line.

    Input:   one line of the document text, without its line break.
    Output:  the marker of the first pattern that accepts the line, or None.
             The patterns run in the order SCHEDULE, DECIMAL, PAREN, KEYWORD,
             CLOSING PAREN, BARE.
    Effects: none.
    """

    for finder in _FINDERS:
        found = finder(line_text)
        if found is not None:
            return found
    return None


def is_signature_line(line_text: str) -> bool:
    """True when a line opens a signature block.

    Input:   one line of the document text, without its line break.
    Output:  true when the line opens with "signed", "executed" or
             "in witness whereof", as a word of its own. A later language adds
             its own openers to the same tuple.
    Effects: none.
    """

    words = " ".join(line_text.strip(EMPHASIS_STRIP).split()).casefold()
    return any(
        words.startswith(opener)
        and (len(words) == len(opener) or words[len(opener)] in SIGNATURE_BOUNDARY)
        for opener in SIGNATURE_OPENERS
    )


def is_short_heading_line(line_text: str) -> bool:
    """True when one line passes the short-line heading test.

    Input:   one line of the document text, without its line break.
    Output:  true for a line of at most 60 characters and 8 words, with no tab,
             that starts with a capital letter and does not end like a
             sentence.
    Effects: none.
    """

    stripped = line_text.strip(EMPHASIS_STRIP)
    if stripped == "" or "\t" in line_text:
        return False
    return (
        len(stripped) <= 60
        and len(stripped.split()) <= 8
        and stripped[-1] not in ".,;:"
        and stripped[0].isupper()
    )


def is_heading_line(line_text: str) -> bool:
    """True when one line looks like an unnumbered heading on its own.

    Input:   one line of the document text, without its line break.
    Output:  true for a short, capitalised line that does not end like a
             sentence, and for a line that opens a signature block whatever its
             length. The lines around it are S2-M3-T6's concern.
    Effects: none.
    """

    stripped = line_text.strip(EMPHASIS_STRIP)
    if stripped == "" or "\t" in line_text:
        return False
    return is_signature_line(line_text) or is_short_heading_line(line_text)
