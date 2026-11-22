"""Typed party details and their variants (S4-M2-T4).

A typed party is a company when its name ends in one of the 15 company
suffixes, and a person otherwise (question 2). A defined term is also a
short name of the party when all its words are the party's words and its
defining sentence holds the full name (question 4).
"""

from collections.abc import Sequence

from clause_tracer.core import (
    DefinedTerm,
    Party,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    fold_for_matching,
)
from clause_tracer.privacy._match import find_name_form
from clause_tracer.privacy._spans import unique_sorted
from clause_tracer.privacy.names import (
    COMMON_WORD_NAMES,
    NAME_STOP_WORDS,
    address_forms,
    fold_text,
    is_company_name,
    name_forms,
    strip_honorific,
)


def find_party_details(
    text: str,
    parties: Sequence[Party],
    terms: Sequence[DefinedTerm],
) -> tuple[PiiSuggestion, ...]:
    """Find every copy of each typed party's name, variants and address.

    Input:   the contract text, the typed parties and the defined terms.
    Output:  one suggestion for each copy, sorted, with no duplicate.
    Raises:  ValueError when a party name is empty.
    Effects: none (T1).
    """

    key = fold_for_matching(text)
    suggestions: list[PiiSuggestion] = []
    for party in parties:
        if not party.name.strip():
            raise ValueError("privacy: party name is empty")
        kind = PlaceholderKind.COMPANY if is_company_name(party.name) else PlaceholderKind.PERSON
        forms = list(name_forms(party.name, kind))
        forms.extend(_short_names(text, party, kind, forms, terms))
        for form in forms:
            for span in find_name_form(text, key, form, NAME_STOP_WORDS, COMMON_WORD_NAMES):
                suggestions.append(
                    PiiSuggestion(span=span, kind=kind, source=PiiSource.PARTY_DETAILS)
                )
        address = party.address
        if address is not None and address.strip():
            for address_form in address_forms(address):
                for span in find_name_form(
                    text, key, address_form, NAME_STOP_WORDS, COMMON_WORD_NAMES
                ):
                    suggestions.append(
                        PiiSuggestion(
                            span=span,
                            kind=PlaceholderKind.ADDRESS,
                            source=PiiSource.PARTY_DETAILS,
                        )
                    )
    return unique_sorted(suggestions)


def _short_names(
    text: str,
    party: Party,
    kind: PlaceholderKind,
    forms: Sequence[str],
    terms: Sequence[DefinedTerm],
) -> list[str]:
    """The defined terms that are also short names of this party (question 4)."""

    tokens = (
        party.name.split()[:-1]
        if kind is PlaceholderKind.COMPANY
        else list(strip_honorific(party.name.split()))
    )
    if not tokens:
        return []
    core_words = {fold_text(token).strip(".,;:") for token in tokens}
    core_words.discard("")
    full_forms = [form for form in forms if " " in form]
    short_names: list[str] = []
    for term in terms:
        words = {word.strip(".,;:") for word in fold_text(term.term).split()}
        words.discard("")
        folded_term = fold_text(term.term)
        defining_text = fold_text(text[term.definition.start : term.definition.end])
        if (
            words
            and words <= core_words
            and folded_term not in forms
            and any(form in defining_text for form in full_forms)
        ):
            short_names.append(folded_term)
    return short_names
