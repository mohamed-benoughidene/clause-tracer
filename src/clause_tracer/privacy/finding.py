"""`find_personal_data`, the step 3 call (S4-M3-T6).

A fixed series of steps (P3): the code finders and the detector, the check,
the allow-list, the governing-law place, the overlap resolve, the join of a
left-over company ending and the sentence split. The detector is passed in
(T2) and its error is never caught.
"""

from clause_tracer.core import (
    PiiDetector,
    PiiSuggestion,
    fold_for_matching,
)
from clause_tracer.privacy.addresses import find_addresses
from clause_tracer.privacy.companies import find_companies
from clause_tracer.privacy.party import find_party_details
from clause_tracer.privacy.patterns import find_patterns
from clause_tracer.privacy.people import find_people
from clause_tracer.privacy.places import governing_law_places
from clause_tracer.privacy.resolve import (
    allowed_term_texts,
    cut_in_places,
    drop_allowed,
    join_left_endings,
    resolve_overlaps,
    sentence_starts,
    split_at_sentences,
    trim_suggestions,
)
from clause_tracer.privacy.sample_input import PrivacyInput


def find_personal_data(case: PrivacyInput, detector: PiiDetector) -> tuple[PiiSuggestion, ...]:
    """Find every suggestion of personal data in one privacy input.

    Input:   the privacy input and the detector to run once over the whole text.
    Output:  the kept suggestions, sorted and with no overlap.
    Raises:  ValueError from a part, and any error from the detector.
    Effects: none (T1).
    """

    text = case.document.text
    key = fold_for_matching(text)
    raw = (
        *find_party_details(text, case.parties, case.terms, key=key),
        *find_patterns(text),
        *find_companies(text),
        *find_addresses(text),
        *find_people(text, key=key),
        *detector.find(text),
    )
    checked = trim_suggestions(text, raw)
    allowed = allowed_term_texts(text, case.terms, checked)
    kept = drop_allowed(text, checked, allowed)
    kept = cut_in_places(text, kept, governing_law_places(text))
    resolved = resolve_overlaps(text, kept)
    joined = join_left_endings(text, resolved)
    return split_at_sentences(text, joined, sentence_starts(case.clauses))
