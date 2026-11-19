"""Split a document's text into clauses (Spec 6.1 step 2; S2-M3-T6 to T9).

The splitter reads the text line by line. A marker opens a clause only when
its number follows on from the numbering so far; every other line belongs to
the clause before it. The clauses cover the whole text, so no word of the
contract falls outside a clause (Spec 5, never guess).
"""

from dataclasses import dataclass, replace
from typing import Final

from clause_tracer.core import Clause, ClauseId, Document, Sentence, SentenceId, Span
from clause_tracer.ingest._lines import Line, is_blank, split_lines
from clause_tracer.ingest._markers import (
    Marker,
    MarkerKind,
    find_marker,
    is_heading_line,
)
from clause_tracer.ingest._numbering import (
    ParenStyle,
    is_decimal_successor,
    paren_readings,
)

NUMBERING_NUMBERS: Final[str] = "numbers"
NUMBERING_PARAGRAPHS: Final[str] = "paragraphs"


@dataclass(frozen=True, slots=True, kw_only=True)
class _ClauseStart:
    """A clause found during the walk, before its span end is known."""

    id: str | None
    number: str | None
    heading: str | None
    parent_id: str | None
    level: int
    start: int
    body_start: int
    numbering_source: str


def _is_proper_prefix(prefix: tuple[int, ...], parts: tuple[int, ...]) -> bool:
    return len(prefix) < len(parts) and parts[: len(prefix)] == prefix


def _unique(base: str, used: set[str]) -> str:
    """Make an id new by adding ~2, ~3 and so on when it is already used."""

    if base not in used:
        used.add(base)
        return base
    suffix = 2
    while f"{base}~{suffix}" in used:
        suffix += 1
    unique = f"{base}~{suffix}"
    used.add(unique)
    return unique


def _has_marker_after(lines: tuple[Line, ...], index: int) -> bool:
    for later in lines[index + 1 :]:
        if is_blank(later):
            continue
        return find_marker(later.text) is not None
    return False


def _is_heading_at(lines: tuple[Line, ...], index: int) -> bool:
    if index == 0:
        return False
    line = lines[index]
    if not is_heading_line(line.text):
        return False
    return is_blank(lines[index - 1]) or _has_marker_after(lines, index)


def _marker_clause_start(
    marker: Marker,
    line: Line,
    clause_id: str,
    parent_id: str | None,
    level: int,
) -> _ClauseStart:
    return _ClauseStart(
        id=clause_id,
        number=marker.written,
        heading=None,
        parent_id=parent_id,
        level=level,
        start=line.start,
        body_start=line.start + marker.body_start,
        numbering_source=NUMBERING_NUMBERS,
    )


def _find_clause_starts(lines: tuple[Line, ...]) -> list[_ClauseStart]:
    """Walk the lines and return the clauses a marker or heading starts."""

    starts: list[_ClauseStart] = []
    used_ids: set[str] = set()
    levels: dict[str, int] = {}

    scope_prefix = ""
    scope_parent: str | None = None
    last_decimal: tuple[int, ...] | None = None
    open_decimal: dict[tuple[int, ...], str] = {}
    base: str | None = None
    paren_stack: list[tuple[ParenStyle, int, str]] = []
    suspended: list[tuple[tuple[int, ...], dict[tuple[int, ...], str]]] = []

    for index, line in enumerate(lines):
        marker = find_marker(line.text)
        if marker is None:
            if _is_heading_at(lines, index):
                starts.append(
                    _ClauseStart(
                        id=None,
                        number=None,
                        heading=None,
                        parent_id=None,
                        level=1,
                        start=line.start,
                        body_start=line.start,
                        numbering_source=NUMBERING_NUMBERS,
                    )
                )
                paren_stack = []
                base = None
            continue

        if marker.kind is MarkerKind.SCHEDULE:
            clause_id = _unique(marker.token, used_ids)
            levels[clause_id] = 1
            starts.append(_marker_clause_start(marker, line, clause_id, None, 1))
            scope_prefix = f"{clause_id}."
            scope_parent = clause_id
            base = clause_id
            last_decimal = None
            open_decimal = {}
            paren_stack = []
            suspended = []
            continue

        if marker.kind is MarkerKind.DECIMAL or marker.kind is MarkerKind.KEYWORD:
            parts = marker.parts
            accepted = False
            if last_decimal is None or is_decimal_successor(last_decimal, parts):
                accepted = True
            else:
                for suspended_index in range(len(suspended) - 1, -1, -1):
                    run_last, run_open = suspended[suspended_index]
                    if is_decimal_successor(run_last, parts):
                        last_decimal = run_last
                        open_decimal = run_open
                        del suspended[suspended_index:]
                        accepted = True
                        break
                if not accepted and parts == (1,):
                    suspended.append((last_decimal, open_decimal))
                    open_decimal = {}
                    accepted = True
            if not accepted:
                continue
            open_decimal = {
                key: value for key, value in open_decimal.items() if _is_proper_prefix(key, parts)
            }
            parent_id = (
                max(open_decimal.items(), key=lambda item: len(item[0]))[1]
                if open_decimal
                else scope_parent
            )
            level = 1 if parent_id is None else levels[parent_id] + 1
            clause_id = _unique(scope_prefix + marker.id_part, used_ids)
            levels[clause_id] = level
            starts.append(_marker_clause_start(marker, line, clause_id, parent_id, level))
            open_decimal[parts] = clause_id
            last_decimal = parts
            base = clause_id
            paren_stack = []
            continue

        if marker.kind is MarkerKind.BARE:
            parts = marker.parts
            accepted = (last_decimal is None and parts == (1,)) or (
                last_decimal is not None and is_decimal_successor(last_decimal, parts)
            )
            if not accepted:
                continue
            open_decimal = {
                key: value for key, value in open_decimal.items() if _is_proper_prefix(key, parts)
            }
            parent_id = (
                max(open_decimal.items(), key=lambda item: len(item[0]))[1]
                if open_decimal
                else scope_parent
            )
            level = 1 if parent_id is None else levels[parent_id] + 1
            clause_id = _unique(scope_prefix + marker.id_part, used_ids)
            levels[clause_id] = level
            starts.append(_marker_clause_start(marker, line, clause_id, parent_id, level))
            open_decimal[parts] = clause_id
            last_decimal = parts
            base = clause_id
            paren_stack = []
            continue

        readings = paren_readings(marker.token)
        chosen: tuple[ParenStyle, int] | None = None
        for stack_index in range(len(paren_stack) - 1, -1, -1):
            style, value, _open_clause = paren_stack[stack_index]
            if (style, value + 1) in readings:
                del paren_stack[stack_index:]
                chosen = (style, value + 1)
                break
        if chosen is None:
            for style, value in readings:
                style_already_open = any(
                    open_style == style for open_style, _open_value, _open_clause in paren_stack
                )
                if value == 1 and not style_already_open:
                    chosen = (style, value)
                    break
        if chosen is None:
            continue
        parent_id = paren_stack[-1][2] if paren_stack else base
        id_prefix = parent_id if parent_id is not None else scope_prefix
        clause_id = _unique(id_prefix + marker.id_part, used_ids)
        level = 1 if parent_id is None else levels[parent_id] + 1
        levels[clause_id] = level
        starts.append(_marker_clause_start(marker, line, clause_id, parent_id, level))
        paren_stack.append((chosen[0], chosen[1], clause_id))

    return starts


def _build_clauses(text: str, starts: list[_ClauseStart]) -> tuple[Clause, ...]:
    """Add the text before the first clause, number unnumbered clauses, and
    give every clause its span and its sentence."""

    records = list(starts)
    first = records[0]
    if first.start > 0:
        text_before = text[: first.start]
        if text_before.strip() != "":
            records.insert(
                0,
                _ClauseStart(
                    id=None,
                    number=None,
                    heading=None,
                    parent_id=None,
                    level=1,
                    start=0,
                    body_start=0,
                    numbering_source=NUMBERING_NUMBERS,
                ),
            )
        else:
            records[0] = replace(first, start=0)

    used_ids: set[str] = set()
    for record in records:
        if record.id is not None:
            used_ids.add(record.id)

    numbered: list[_ClauseStart] = []
    next_paragraph = 1
    for record in records:
        if record.id is None:
            clause_id = _unique(f"p{next_paragraph}", used_ids)
            next_paragraph += 1
            record = replace(record, id=clause_id)
        numbered.append(record)

    clauses: list[Clause] = []
    for index, record in enumerate(numbered):
        end = numbered[index + 1].start if index + 1 < len(numbered) else len(text)
        assert record.id is not None
        span = Span(start=record.start, end=end)
        clauses.append(
            Clause(
                id=ClauseId(record.id),
                number=record.number,
                heading=record.heading,
                level=record.level,
                parent_id=(ClauseId(record.parent_id) if record.parent_id is not None else None),
                span=span,
                numbering_source=record.numbering_source,
                sentences=(Sentence(id=SentenceId(f"{record.id}.s1"), span=span),),
            )
        )
    return tuple(clauses)


def _split_paragraphs(text: str) -> tuple[Clause, ...]:
    """One paragraph clause over the whole text (S2-M3-T9 fills this in)."""

    span = Span(start=0, end=len(text))
    return (
        Clause(
            id=ClauseId("p1"),
            number=None,
            heading=None,
            level=1,
            parent_id=None,
            span=span,
            numbering_source=NUMBERING_PARAGRAPHS,
            sentences=(Sentence(id=SentenceId("p1.s1"), span=span),),
        ),
    )


def split_clauses(document: Document) -> tuple[Clause, ...]:
    """Split a document into clauses, with a sentence id for every sentence.

    Input:   one document. Only `document.text` is read.
    Output:  the clauses in text order, each with its id, number, heading,
             level, parent, span and sentences. A blank text gives no clauses.
             When no marker is accepted, the text is split by paragraph.
    Raises:  nothing. A document that `ingest` built is always valid here.
    Effects: none (I11).
    """

    text = document.text
    if text.strip() == "":
        return ()

    lines = split_lines(text)
    starts = _find_clause_starts(lines)
    if not any(start.id is not None for start in starts):
        return _split_paragraphs(text)
    return _build_clauses(text, starts)
