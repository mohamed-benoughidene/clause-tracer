"""The printed link map: one tab-separated line for each link (S3-M5-T3)."""

from clause_tracer.core import Clause, ClauseId, Document, LinkMap, Span
from clause_tracer.links._index import ClauseIndex, build_index

_EMPTY_CLAUSE = "-"


def render_link_map(document: Document, clauses: tuple[Clause, ...], link_map: LinkMap) -> str:
    """Render a link map as tab-separated lines.

    Input:   the document, its clauses and the link map of that document.
    Output:  the lines, joined by one newline and ending in one newline.
    Raises:  ValueError when `build_index` refuses the clauses ("clauses are
             not in text order" or "clause {id} has a later parent"), as
             `map_links` does.
    Effects: none (T1).
    """

    index = build_index(clauses)
    lines = [
        f"source\t{_text(document.source.name)}\t{len(document.text)}",
        "counts"
        f"\treferences {len(link_map.references)}"
        f"\tterms {len(link_map.terms)}"
        f"\toverrides {len(link_map.overrides)}"
        f"\toutside {len(link_map.outside_documents)}"
        f"\tundefined {len(link_map.undefined_terms)}",
    ]
    for reference in link_map.references:
        lines.append(
            "reference"
            f"\t{_clause_at(index, reference.source)}"
            f"\t{_span(reference.source)}"
            f"\t{_target(reference.target)}"
            f"\t{_text(document.text[reference.source.start : reference.source.end])}"
        )
    for term in link_map.terms:
        lines.append(
            "term"
            f"\t{_text(term.term)}"
            f"\t{_clause_at(index, term.definition)}"
            f"\t{_span(term.definition)}"
            f"\tuses {len(term.uses)}"
        )
    for override in link_map.overrides:
        direction = "overrides" if override.overrides_target else "qualified"
        lines.append(
            "override"
            f"\t{override.clause_id}"
            f"\t{_target(override.target)}"
            f"\t{direction}"
            f"\t{_span(override.evidence)}"
            f"\t{_text(document.text[override.evidence.start : override.evidence.end])}"
        )
    for outside in link_map.outside_documents:
        lines.append(
            "outside"
            f"\t{_text(outside.name)}"
            f"\t{_clause_at(index, outside.evidence)}"
            f"\t{_span(outside.evidence)}"
        )
    for undefined in link_map.undefined_terms:
        lines.append(
            "undefined"
            f"\t{_clause_at(index, undefined)}"
            f"\t{_span(undefined)}"
            f"\t{_text(document.text[undefined.start : undefined.end])}"
        )
    return "\n".join(lines) + "\n"


def _text(field: str) -> str:
    return field.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _span(span: Span) -> str:
    return f"{span.start}-{span.end}"


def _target(target: ClauseId | None) -> str:
    return _EMPTY_CLAUSE if target is None else str(target)


def _clause_at(index: ClauseIndex, span: Span) -> str:
    clause = index.clause_at(span.start)
    return _EMPTY_CLAUSE if clause is None else str(clause.id)
