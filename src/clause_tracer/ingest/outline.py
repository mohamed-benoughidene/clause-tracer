"""Render an outline of a document's clauses and sentences (S2-M4-T2).

The lines are tab-separated so a person can read them, and so a golden file
can hold them exactly. Not exported from `ingest`.
"""

from typing import Final

from clause_tracer.core import Clause, Document

PREVIEW_CHARACTERS: Final[int] = 60


def _preview(text: str, start: int, end: int) -> str:
    """The words of one span, cut to their first 60 characters."""

    words = " ".join(text[start:end].split())
    return words[:PREVIEW_CHARACTERS]


def render_outline(document: Document, clauses: tuple[Clause, ...]) -> str:
    """Return the document's source, numbering, warnings, clauses and sentences.

    Input:   one document and its clauses, in text order.
    Output:  one line per fact, ending with "\\n": three header lines, then a
             line for each clause and a line for each of its sentences.
    Effects: none.
    """

    lines = [
        "source",
        document.source.kind.value,
        str(document.source.size),
        document.source.sha256,
    ]
    outline = ["\t".join(lines)]
    numbering = clauses[0].numbering_source if clauses else "-"
    outline.append(f"numbering\t{numbering}")
    warning_codes = ",".join(warning.code for warning in document.warnings) or "-"
    outline.append(f"warnings\t{warning_codes}")
    for clause in clauses:
        outline.append(
            "\t".join(
                (
                    clause.id,
                    clause.number or "-",
                    f"level {clause.level}",
                    clause.parent_id or "-",
                    f"{clause.span.start}-{clause.span.end}",
                    clause.heading or "-",
                )
            )
        )
        for sentence in clause.sentences:
            outline.append(
                "\t".join(
                    (
                        f"  {sentence.id}",
                        f"{sentence.span.start}-{sentence.span.end}",
                        _preview(document.text, sentence.span.start, sentence.span.end),
                    )
                )
            )
    return "\n".join(outline) + "\n"
