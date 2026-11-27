"""The forms of a name and of an address, and the word lists (S4-M2-T1).

A form is folded through `fold_for_matching`, so a finder can search it on
the match key. The lists are code constants; the owner reads them with the
plan (question 16, Constitution T11).
"""

from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Final

from clause_tracer.core import PlaceholderKind, fold_for_matching

HONORIFICS: Final[tuple[str, ...]] = ("mr", "mrs", "ms", "miss", "mx", "dr")
COMPANY_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        "ltd",
        "limited",
        "llc",
        "llp",
        "plc",
        "inc",
        "corp",
        "gmbh",
        "ag",
        "sarl",
        "sas",
        "bv",
        "nv",
        "pty",
        "co",
    }
)
SUFFIX_SWAPS: Final[Mapping[str, str]] = MappingProxyType({"ltd": "limited", "limited": "ltd"})
# A one-word form in this set is never searched for (question 17, layer 2).
NAME_STOP_WORDS: Final[frozenset[str]] = frozenset(
    {
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "will",
        "mark",
        "grant",
        "bill",
        "page",
        "price",
    }
)
# A one-word form in this set counts only where the contract shows a name (layer 3).
COMMON_WORD_NAMES: Final[frozenset[str]] = frozenset(
    {
        "rose",
        "hope",
        "frank",
        "art",
        "bob",
        "pat",
        "ray",
        "rob",
        "jack",
        "sue",
        "dawn",
        "joy",
        "faith",
        "grace",
        "summer",
        "ruby",
        "amber",
        "daisy",
        "lily",
        "violet",
        "brown",
        "green",
        "white",
        "black",
        "king",
        "hall",
        "young",
        "long",
        "cook",
        "baker",
        "wood",
        "stone",
        "hill",
        "field",
        "bell",
        "ward",
        "lane",
        "mills",
        "bush",
        "rice",
        "fox",
        "bird",
        "major",
        "miller",
        "carter",
        "porter",
        "taylor",
        "parker",
        "hunter",
        "fisher",
        "mason",
        "cooper",
    }
)
EXTENDED_COMPANY_SUFFIXES: Final[frozenset[str]] = COMPANY_SUFFIXES | frozenset(
    {"lp", "corporation", "incorporated", "srl", "spa", "oy", "kg", "ug", "pte"}
)


def fold_text(text: str) -> str:
    """Fold a text through the wide match fold."""

    return fold_for_matching(text).text


def strip_honorific(tokens: Sequence[str]) -> tuple[str, ...]:
    """Drop the first token when it is an honorific."""

    if tokens and tokens[0].rstrip(".").casefold() in HONORIFICS:
        return tuple(tokens[1:])
    return tuple(tokens)


def _last_token(name: str) -> str | None:
    """The last token of a name, without a final full stop or comma, folded."""

    tokens = name.split()
    if not tokens:
        return None
    return tokens[-1].rstrip(".,").casefold()


def company_suffix(name: str) -> str | None:
    """The company suffix that ends `name`, or `None`."""

    last = _last_token(name)
    if last is not None and last in COMPANY_SUFFIXES:
        return last
    return None


def is_company_name(name: str) -> bool:
    """Say whether a typed party name ends in a company suffix (question 2)."""

    return company_suffix(name) is not None


def is_company_seed(name: str) -> bool:
    """Say whether a rule-found name ends in an extended company suffix."""

    last = _last_token(name)
    return last is not None and last in EXTENDED_COMPANY_SUFFIXES


def name_forms(name: str, kind: PlaceholderKind) -> tuple[str, ...]:
    """Every folded form of a person's or a company's name.

    Input:   the typed or found name, and its placeholder kind.
    Output:  the folded forms, with no duplicate, longest first.
    Raises:  ValueError for a kind other than a person or a company.
    Effects: none (T1).
    """

    if kind not in (PlaceholderKind.PERSON, PlaceholderKind.COMPANY):
        raise ValueError("privacy: name forms need a person or a company")

    raw: list[str] = []
    if kind is PlaceholderKind.PERSON:
        person_tokens = strip_honorific(name.split())
        if person_tokens:
            last = person_tokens[-1]
            raw.append(" ".join(person_tokens))
            if len(person_tokens) >= 3:
                raw.append(person_tokens[0] + " " + last)
            if len(person_tokens) >= 2 and len(person_tokens[0]) >= 3:
                raw.append(person_tokens[0])
            if len(person_tokens) >= 2 and len(last) >= 3:
                raw.append(last)
            for honorific in HONORIFICS:
                raw.append(f"{honorific} {last}")
                raw.append(f"{honorific}. {last}")
    else:
        company_tokens = name.split()
        suffix = company_suffix(name)
        if company_tokens and suffix is None:
            raw.append(" ".join(company_tokens))
        elif company_tokens and suffix is not None:
            joined = " ".join(company_tokens[:-1])
            short_core = joined.rstrip(", ")
            core_is_left = bool(short_core)
            if core_is_left:
                raw.append(short_core)
                swap = SUFFIX_SWAPS.get(suffix)
                for core in (joined, short_core):
                    raw.append(core + " " + suffix)
                    if swap is not None:
                        raw.append(core + " " + swap)

    forms = {fold_text(form) for form in raw}
    return tuple(sorted(forms, key=lambda form: (-len(form), form)))


def address_forms(address: str) -> tuple[str, ...]:
    """Every folded form of a typed address: the whole, and its first line."""

    stripped = address.strip()
    raw = [stripped]
    if "," in stripped:
        first_line = stripped.split(",")[0].strip()
        if first_line[:1].isdigit() and len(first_line.split()) >= 2:
            raw.append(first_line)
    forms = {fold_text(form) for form in raw}
    return tuple(sorted(forms, key=lambda form: (-len(form), form)))
