"""Property tests of the link map (S3-M5-T2)."""

from hypothesis import given, settings

from clause_tracer.core import LinkMap, Span, fold_for_matching
from clause_tracer.links import map_links
from clause_tracer.links.sample_clauses import SampleInput
from clause_tracer.links.tests.strategies import link_cases


def _spans(link_map: LinkMap) -> list[Span]:
    return (
        [reference.source for reference in link_map.references]
        + [term.definition for term in link_map.terms]
        + [use for term in link_map.terms for use in term.uses]
        + [override.evidence for override in link_map.overrides]
        + [outside.evidence for outside in link_map.outside_documents]
        + list(link_map.undefined_terms)
    )


@given(link_cases())
@settings(deadline=None)
def test_spans_are_inside_the_text(case: SampleInput) -> None:
    link_map = map_links(case.document, case.clauses)
    text_length = len(case.document.text)

    for span in _spans(link_map):
        assert 0 <= span.start <= span.end <= text_length


@given(link_cases())
@settings(deadline=None)
def test_targets_are_known_or_none(case: SampleInput) -> None:
    link_map = map_links(case.document, case.clauses)
    known = {clause.id for clause in case.clauses}

    for reference in link_map.references:
        assert reference.target is None or reference.target in known
    for override in link_map.overrides:
        assert override.target is None or override.target in known


@given(link_cases())
@settings(deadline=None)
def test_result_is_sorted(case: SampleInput) -> None:
    link_map = map_links(case.document, case.clauses)

    reference_starts = [reference.source.start for reference in link_map.references]
    term_starts = [term.definition.start for term in link_map.terms]
    override_starts = [override.evidence.start for override in link_map.overrides]
    outside_starts = [outside.evidence.start for outside in link_map.outside_documents]
    undefined_starts = [span.start for span in link_map.undefined_terms]

    assert reference_starts == sorted(reference_starts)
    assert term_starts == sorted(term_starts)
    assert override_starts == sorted(override_starts)
    assert outside_starts == sorted(outside_starts)
    assert undefined_starts == sorted(undefined_starts)


@given(link_cases())
@settings(deadline=None)
def test_same_input_same_output(case: SampleInput) -> None:
    assert map_links(case.document, case.clauses) == map_links(case.document, case.clauses)


@given(link_cases())
@settings(deadline=None)
def test_term_uses_match_the_term(case: SampleInput) -> None:
    link_map = map_links(case.document, case.clauses)
    text = case.document.text

    for term in link_map.terms:
        for use in term.uses:
            assert fold_for_matching(text[use.start : use.end]).text == (
                fold_for_matching(term.term).text
            )
