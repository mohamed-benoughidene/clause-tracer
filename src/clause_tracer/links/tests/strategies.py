"""Hypothesis strategies for the link-map property tests (S3-M5-T2).

Not exported from `links`. Each case is drawn from the fragments `links`
reads, mixed with the hazard alphabet, so a property test meets the same
odd characters that `ingest` meets.
"""

from typing import Final

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy, composite

from clause_tracer.core.tests.strategies import HAZARD_ALPHABET
from clause_tracer.links.sample_clauses import SampleInput
from clause_tracer.links.tests.case_builder import build_case

FRAGMENTS: tuple[str, ...] = (
    "see clause 1",
    "clauses 1 to 3",
    "Subject to Clause 2",
    "Notwithstanding clause 9",
    '"Fee" means money',
    'Brightline ("the Buyer")',
    "the Master Agreement",
    "this Clause",
    "Business Days",
    "2.5 days",
    "Schedule 1",
    "this Agreement prevails",
)

SENTENCE_HAZARDS: tuple[str, ...] = tuple(
    character for character in HAZARD_ALPHABET if character != "\n"
)

_ITEMS: Final[SearchStrategy[str]] = st.one_of(
    st.sampled_from(FRAGMENTS),
    st.text(alphabet=st.sampled_from(SENTENCE_HAZARDS), min_size=1, max_size=8),
)


@composite
def link_cases(draw: st.DrawFn) -> SampleInput:
    """Draw a small case of 1 to 6 clauses, each with 1 to 3 sentences."""

    clause_count = draw(st.integers(min_value=1, max_value=6))
    rows: list[dict[str, object]] = []
    for number in range(1, clause_count + 1):
        sentence_count = draw(st.integers(min_value=1, max_value=3))
        sentences: list[str] = []
        for _ in range(sentence_count):
            item_count = draw(st.integers(min_value=1, max_value=4))
            items = [draw(_ITEMS) for _ in range(item_count)]
            sentences.append(" ".join(items))
        rows.append({"id": str(number), "sentences": sentences})
    return build_case(rows)
