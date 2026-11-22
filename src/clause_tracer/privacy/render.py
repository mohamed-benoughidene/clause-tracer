"""The printed privacy report: one tab-separated line for each field (S4-M5-T1)."""

from collections.abc import Sequence

from clause_tracer.core import PlaceholderEntity, PlaceholderText
from clause_tracer.privacy._tokens import LABELS
from clause_tracer.privacy.sample_input import PrivacyInput


def render_privacy_report(
    case: PrivacyInput,
    entities: Sequence[PlaceholderEntity],
    placeholder: PlaceholderText,
) -> str:
    """Render the entities and the placeholder text as tab-separated lines.

    Input:   the privacy input, its entities and its placeholder text.
    Output:  the lines, each ending in one newline, in the order source,
             counts, entity, span and text.
    Raises:  None.
    Effects: none (T1).
    """

    lines = [
        f"source\t{_text(case.document.source.name)}\t{len(case.document.text)}",
        "counts"
        f"\tentities {len(entities)}"
        f"\tspans {sum(len(entity.spans) for entity in entities)}"
        f"\tsegments {len(placeholder.segments)}",
    ]
    for entity in entities:
        lines.append(
            f"entity\t{entity.id}\t{LABELS[entity.kind]} {entity.number}"
            f"\tplaces {len(entity.spans)}"
        )
    for entity in entities:
        for span in sorted(entity.spans, key=lambda span: span.start):
            lines.append(
                f"span\t{entity.id}\t{span.start}-{span.end}"
                f"\t{_text(case.document.text[span.start : span.end])}"
            )
    for piece in placeholder.text.split("\n"):
        lines.append(f"text\t{_text(piece)}")
    return "\n".join(lines) + "\n"


def _text(field: str) -> str:
    return field.replace("\t", " ").replace("\r", " ").replace("\n", " ")
