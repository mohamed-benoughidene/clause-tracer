"""Short names of the companies that the rule finder found (S4-M2-T5).

A company nobody typed is found where its ending is written. This finder hides
the same name without the ending, and a nickname that the contract defines.
"""

from collections.abc import Sequence
from typing import Final

from clause_tracer.core import (
    DefinedTerm,
    MatchKey,
    Party,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Span,
    fold_for_matching,
)
from clause_tracer.privacy import _place_list
from clause_tracer.privacy._match import find_name_form, find_word
from clause_tracer.privacy._patterns import LAST_ENDING_RE
from clause_tracer.privacy._spans import unique_sorted
from clause_tracer.privacy.names import (
    COMMON_WORD_NAMES,
    EXTENDED_COMPANY_SUFFIXES,
    NAME_STOP_WORDS,
    fold_text,
    is_company_name,
)
from clause_tracer.privacy.people import LEGAL_STOP_WORDS

JOINING_WORDS: Final[frozenset[str]] = frozenset({"the", "and", "of", "&"})
_LISTED_PLACES: Final[frozenset[str]] = frozenset(
    fold_text(name)
    for group in (
        _place_list.COUNTRIES,
        _place_list.COUNTRIES_MULTI,
        _place_list.UK_NATIONS,
        _place_list.US_STATES,
        _place_list.CA_PROVINCES,
        _place_list.AU_STATES,
    )
    for name in group
)
_ADDRESS_MARKS: Final[tuple[str, ...]] = ("@", "/", "-", "_")


def find_short_names(
    text: str,
    companies: Sequence[PiiSuggestion],
    parties: Sequence[Party],
    terms: Sequence[DefinedTerm],
    *,
    key: MatchKey | None = None,
) -> tuple[PiiSuggestion, ...]:
    """Find each found company's name without its ending, and its nicknames.

    Input:   the contract text, the results of `find_companies` over it, the
             typed parties and the defined terms.
    Output:  one `RULE` `COMPANY` suggestion for each copy, sorted, no duplicate.
    Raises:  nothing.
    Effects: none (T1).
    """

    key = fold_for_matching(text) if key is None else key
    person_words = [
        _words(fold_text(party.name)) for party in parties if not is_company_name(party.name)
    ]
    suggestions: list[PiiSuggestion] = []
    for company in companies:
        found = text[company.span.start : company.span.end]
        full = fold_text(found).strip()
        short = fold_text(LAST_ENDING_RE.sub("", found).strip(" ,")).strip()
        has_no_ending_to_remove = not short or short == full
        if (
            has_no_ending_to_remove
            or _is_never_a_name(short)
            or _is_typed_person(short, person_words)
        ):
            continue
        is_one_word = " " not in short
        if not (is_one_word and _is_written_in_small_letters(text, key, short)):
            suggestions.extend(_copies(text, key, short))
        full_forms = [full, short] if " " in short else [full]
        for term in terms:
            nickname = fold_text(term.term)
            words = _words(nickname)
            is_made_of_the_name = bool(words) and words <= _words(short)
            if not is_made_of_the_name:
                continue
            if _is_never_a_name(nickname) or _is_typed_person(nickname, person_words):
                continue
            definition = fold_text(text[term.definition.start : term.definition.end])
            if any(form in definition for form in full_forms):
                suggestions.extend(_copies(text, key, nickname))
    return unique_sorted(suggestions)


def _words(folded: str) -> frozenset[str]:
    return frozenset(word.strip(".,;:") for word in folded.split()) - {""}


def _is_never_a_name(folded: str) -> bool:
    """A role or legal word, a company ending, or a place on the owner's list."""

    is_role_or_legal = _words(folded) <= LEGAL_STOP_WORDS | JOINING_WORDS
    is_only_endings = _words(folded) <= EXTENDED_COMPANY_SUFFIXES | JOINING_WORDS
    return is_role_or_legal or is_only_endings or folded.removeprefix("the ") in _LISTED_PLACES


def _is_typed_person(folded: str, person_words: Sequence[frozenset[str]]) -> bool:
    return any(_words(folded) <= words for words in person_words)


def _is_written_in_small_letters(text: str, key: MatchKey, word: str) -> bool:
    """True when the word is written in small letters outside a web or mail address."""

    return any(_is_plain_small_use(text, span) for span in find_word(key, word))


def _is_plain_small_use(text: str, span: Span) -> bool:
    found = text[span.start : span.end]
    before = text[span.start - 1 : span.start]
    after = text[span.end : span.end + 1]
    is_small = found == found.lower()
    follows_an_address = before in (".", *_ADDRESS_MARKS)
    starts_an_address = after in _ADDRESS_MARKS or (
        after == "." and text[span.end + 1 : span.end + 2].isalnum()
    )
    return is_small and not follows_an_address and not starts_an_address


def _copies(text: str, key: MatchKey, form: str) -> list[PiiSuggestion]:
    """The copies of a form that start with a capital letter."""

    return [
        PiiSuggestion(span=span, kind=PlaceholderKind.COMPANY, source=PiiSource.RULE)
        for span in find_name_form(text, key, form, NAME_STOP_WORDS, COMMON_WORD_NAMES)
        if text[span.start].isupper()
    ]
