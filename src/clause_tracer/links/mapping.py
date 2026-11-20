"""The one public call: a document and its clauses give one link map (S3-M5-T1)."""

from clause_tracer.core import (
    Clause,
    Document,
    LinkMap,
    fold_for_matching,
)
from clause_tracer.links._index import build_index
from clause_tracer.links._spans import build_span_set
from clause_tracer.links.outside import find_outside_documents
from clause_tracer.links.overrides import find_overrides
from clause_tracer.links.references import find_references
from clause_tracer.links.terms import find_definitions, find_terms, find_undefined_terms


def map_links(document: Document, clauses: tuple[Clause, ...]) -> LinkMap:
    """Map every link the contract holds.

    Input:   a document and its clauses, as `ingest` returns them.
    Output:  the link map; every span points into `document.text`, and an
             unresolved target is `None`.
    Raises:  ValueError when a clause span lies outside the text, which is a
             bug in the caller, and when `build_index` refuses the clauses
             ("clauses are not in text order" or "clause {id} has a later
             parent").
    Effects: none (T1).
    """

    text = document.text
    for clause in clauses:
        if (
            clause.span.start < 0
            or clause.span.end < clause.span.start
            or clause.span.end > len(text)
        ):
            raise ValueError(f"clause {clause.id} lies outside the text")
    index = build_index(clauses)
    references = find_references(text, index)
    definitions = find_definitions(text, index)
    terms = find_terms(text, fold_for_matching(text), definitions)
    outside = find_outside_documents(text, index, definitions)
    overrides = find_overrides(text, index, references, outside)
    excluded = build_span_set(
        [use for term in terms for use in term.uses]
        + [definition.quoted for definition in definitions]
        + [document_outside.evidence for document_outside in outside]
    )
    undefined = find_undefined_terms(text, index, excluded)
    return LinkMap(
        references=references,
        terms=terms,
        overrides=overrides,
        outside_documents=outside,
        undefined_terms=undefined,
    )
