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
    EMPHASIS_STRIP,
    HEADING_STRIP,
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
from clause_tracer.ingest._sentences import sentence_starts

NUMBERING_NUMBERS: Final[str] = "numbers"
NUMBERING_PARAGRAPHS: Final[str] = "paragraphs"


@dataclass(frozen=True, slots=True, kw_only=True)
class _ClauseStart:
    """A clause found during the walk, before its span end is known."""

    id: str | None
    number: str | None
    parent_id: str | None
    level: int
    start: int
    body_start: int
    line_end: int
    heading_source: str | None
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


def _has_marker_after(
    lines: tuple[Line, ...],
    markers: list[Marker | None],
    index: int,
) -> bool:
    for later_index in range(index + 1, len(lines)):
        if is_blank(lines[later_index]):
            continue
        return markers[later_index] is not None
    return False


def _is_heading_at(
    lines: tuple[Line, ...],
    markers: list[Marker | None],
    index: int,
) -> bool:
    if index == 0:
        return False
    line = lines[index]
    if not is_heading_line(line.text):
        return False
    return is_blank(lines[index - 1]) or _has_marker_after(lines, markers, index)


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
        parent_id=parent_id,
        level=level,
        start=line.start,
        body_start=line.start + marker.body_start,
        line_end=line.end,
        heading_source=line.text[marker.body_start :],
        numbering_source=NUMBERING_NUMBERS,
    )


def _heading_for(record: _ClauseStart, text: str, span_end: int) -> str | None:
    """The heading of one clause, or None when its line is not a heading."""

    if record.heading_source is None:
        return None
    if record.number is None:
        return record.heading_source.strip(EMPHASIS_STRIP)
    rest = record.heading_source.strip(EMPHASIS_STRIP)
    title = rest.strip(HEADING_STRIP)
    later_lines_are_blank = text[record.line_end : span_end].strip() == ""
    if title == "" or len(rest) > 100 or rest[-1] in ".;:,":
        return None
    if not later_lines_are_blank:
        return None
    return title


def _sentences_for(
    clause_id: str,
    span: Span,
    body_start: int,
    text: str,
) -> tuple[Sentence, ...]:
    """Split one clause into sentences, with the number in the first one."""

    boundaries = [span.start]
    starts = sentence_starts(text[body_start : span.end])
    boundaries.extend(body_start + start for start in starts[1:])

    sentences: list[Sentence] = []
    for index, boundary in enumerate(boundaries):
        end = boundaries[index + 1] if index + 1 < len(boundaries) else span.end
        sentences.append(
            Sentence(
                id=SentenceId(f"{clause_id}.s{index + 1}"),
                span=Span(start=boundary, end=end),
            )
        )
    return tuple(sentences)


def _open_numbered_clause(
    *,
    marker: Marker,
    line: Line,
    parts: tuple[int, ...],
    open_decimal: dict[tuple[int, ...], str],
    scope_prefix: str,
    scope_parent: str | None,
    levels: dict[str, int],
    used_ids: set[str],
) -> tuple[_ClauseStart, dict[tuple[int, ...], str]]:
    """Build the clause a decimal or bare number starts, under its open parent.

    Returns the clause and the open decimal numbers with this clause added.
    The caller decides whether the number is accepted.
    """

    open_parents = {
        key: value for key, value in open_decimal.items() if _is_proper_prefix(key, parts)
    }
    parent_id = (
        max(open_parents.items(), key=lambda item: len(item[0]))[1]
        if open_parents
        else scope_parent
    )
    level = 1 if parent_id is None else levels[parent_id] + 1
    clause_id = _unique(scope_prefix + marker.id_part, used_ids)
    levels[clause_id] = level
    open_parents[parts] = clause_id
    record = _marker_clause_start(marker, line, clause_id, parent_id, level)
    return record, open_parents


def _find_clause_starts(lines: tuple[Line, ...]) -> list[_ClauseStart]:
    """Walk the lines and return the clauses a marker or heading starts."""

    starts: list[_ClauseStart] = []
    used_ids: set[str] = set()
    levels: dict[str, int] = {}
    markers = [find_marker(line.text) for line in lines]

    scope_prefix = ""
    scope_parent: str | None = None
    last_decimal: tuple[int, ...] | None = None
    open_decimal: dict[tuple[int, ...], str] = {}
    base: str | None = None
    paren_stack: list[tuple[ParenStyle, int, str]] = []
    suspended: list[tuple[tuple[int, ...], dict[tuple[int, ...], str]]] = []

    for index, line in enumerate(lines):
        marker = markers[index]
        if marker is None:
            if _is_heading_at(lines, markers, index):
                starts.append(
                    _ClauseStart(
                        id=None,
                        number=None,
                        parent_id=None,
                        level=1,
                        start=line.start,
                        body_start=line.start,
                        line_end=line.end,
                        heading_source=line.text,
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
            record, open_decimal = _open_numbered_clause(
                marker=marker,
                line=line,
                parts=parts,
                open_decimal=open_decimal,
                scope_prefix=scope_prefix,
                scope_parent=scope_parent,
                levels=levels,
                used_ids=used_ids,
            )
            starts.append(record)
            last_decimal = parts
            base = record.id
            paren_stack = []
            continue

        if marker.kind is MarkerKind.BARE:
            parts = marker.parts
            accepted = (last_decimal is None and parts == (1,)) or (
                last_decimal is not None and is_decimal_successor(last_decimal, parts)
            )
            if not accepted:
                continue
            record, open_decimal = _open_numbered_clause(
                marker=marker,
                line=line,
                parts=parts,
                open_decimal=open_decimal,
                scope_prefix=scope_prefix,
                scope_parent=scope_parent,
                levels=levels,
                used_ids=used_ids,
            )
            starts.append(record)
            last_decimal = parts
            base = record.id
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
                    parent_id=None,
                    level=1,
                    start=0,
                    body_start=0,
                    line_end=0,
                    heading_source=None,
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
        body_start = record.body_start if record.number is not None else span.start
        clauses.append(
            Clause(
                id=ClauseId(record.id),
                number=record.number,
                heading=_heading_for(record, text, end),
                level=record.level,
                parent_id=(ClauseId(record.parent_id) if record.parent_id is not None else None),
                span=span,
                numbering_source=record.numbering_source,
                sentences=_sentences_for(record.id, span, body_start, text),
            )
        )
    return tuple(clauses)


def _has_blank_line_between(lines: tuple[Line, ...]) -> bool:
    """True when a blank line stands between two non-blank lines."""

    seen_non_blank = False
    seen_blank_after_non_blank = False
    for line in lines:
        if is_blank(line):
            if seen_non_blank:
                seen_blank_after_non_blank = True
        else:
            if seen_blank_after_non_blank:
                return True
            seen_non_blank = True
    return False


def _paragraph_line_groups(lines: tuple[Line, ...]) -> list[list[Line]]:
    """Group lines into paragraphs, by blank lines when the text has them."""

    if not _has_blank_line_between(lines):
        return [[line] for line in lines if not is_blank(line)]

    groups: list[list[Line]] = []
    current: list[Line] = []
    for line in lines:
        if is_blank(line):
            if current:
                groups.append(current)
                current = []
        else:
            current.append(line)
    if current:
        groups.append(current)
    return groups


def _split_paragraphs(text: str) -> tuple[Clause, ...]:
    """Split a text with no accepted marker into paragraph clauses."""

    groups = _paragraph_line_groups(split_lines(text))
    clauses: list[Clause] = []
    for index, group in enumerate(groups):
        is_first = index == 0
        start = 0 if is_first else group[0].start
        is_last = index + 1 == len(groups)
        end = len(text) if is_last else groups[index + 1][0].start
        clause_id = f"p{index + 1}"
        span = Span(start=start, end=end)
        clauses.append(
            Clause(
                id=ClauseId(clause_id),
                number=None,
                heading=None,
                level=1,
                parent_id=None,
                span=span,
                numbering_source=NUMBERING_PARAGRAPHS,
                sentences=_sentences_for(clause_id, span, span.start, text),
            )
        )
    return tuple(clauses)


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
