"""Split a document's text into clauses (Spec 6.1 step 2; S2-M3-T6 to T9).

The splitter reads the text line by line. A marker opens a clause only when
its number follows on from the numbering so far; every other line belongs to
the clause before it. The clauses cover the whole text, so no word of the
contract falls outside a clause (Spec 5, never guess).
"""

from dataclasses import dataclass, field, replace
from typing import Final

from clause_tracer.core import Clause, ClauseId, Document, Sentence, SentenceId, Span
from clause_tracer.ingest._lines import Line, is_blank, is_blank_text, split_lines
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
    kind: MarkerKind | None


HEADED_KINDS: Final[frozenset[MarkerKind]] = frozenset(
    {MarkerKind.DECIMAL, MarkerKind.KEYWORD, MarkerKind.SCHEDULE, MarkerKind.BARE}
)


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
        kind=marker.kind,
    )


def _heading_for(record: _ClauseStart, text: str, span_end: int) -> str | None:
    """The heading of one clause, or None when its line is not a heading."""

    if record.heading_source is None:
        return None
    if record.number is None:
        return record.heading_source.strip(EMPHASIS_STRIP)
    if record.kind not in HEADED_KINDS:
        return None
    rest = record.heading_source.strip(EMPHASIS_STRIP)
    title = rest.strip(HEADING_STRIP)
    later_lines_are_blank = is_blank_text(text[record.line_end : span_end])
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


@dataclass(slots=True)
class _WalkState:
    """The walk's mutable state, in one object (B6). Private to this file.

    The walk reads and changes these fields. Each step takes the state and only
    the inputs that are not walk state.
    """

    used_ids: set[str] = field(default_factory=set)
    levels: dict[str, int] = field(default_factory=dict)
    scope_prefix: str = ""
    scope_parent: str | None = None
    last_decimal: tuple[int, ...] | None = None
    open_decimal: dict[tuple[int, ...], str] = field(default_factory=dict)
    base: str | None = None
    paren_stack: list[tuple[ParenStyle, int, str]] = field(default_factory=list)
    suspended: list[tuple[tuple[int, ...], dict[tuple[int, ...], str]]] = field(
        default_factory=list
    )


def _open_numbered_clause(state: _WalkState, marker: Marker, line: Line) -> _ClauseStart:
    """Build the clause a decimal, keyword or bare number starts, under its open parent.

    Updates the walk state: the open numbers, the last number, the bracket stack
    and the base. The caller has already decided the number is accepted.
    """

    parts = marker.parts
    open_parents = {
        key: value for key, value in state.open_decimal.items() if _is_proper_prefix(key, parts)
    }
    parent_id = (
        max(open_parents.items(), key=lambda item: len(item[0]))[1]
        if open_parents
        else state.scope_parent
    )
    level = 1 if parent_id is None else state.levels[parent_id] + 1
    clause_id = _unique(state.scope_prefix + marker.id_part, state.used_ids)
    state.levels[clause_id] = level
    open_parents[parts] = clause_id
    record = _marker_clause_start(marker, line, clause_id, parent_id, level)
    state.open_decimal = open_parents
    state.last_decimal = parts
    state.base = record.id
    state.paren_stack = []
    return record


def _accept_decimal(state: _WalkState, parts: tuple[int, ...]) -> bool:
    """True when a decimal or keyword number is accepted. A number that continues a
    suspended run restores that run's state; no other state changes."""

    previous = state.last_decimal
    if previous is None or is_decimal_successor(previous, parts):
        return True
    for suspended_index in range(len(state.suspended) - 1, -1, -1):
        run_last, run_open = state.suspended[suspended_index]
        if is_decimal_successor(run_last, parts):
            state.last_decimal = run_last
            state.open_decimal = run_open
            del state.suspended[suspended_index:]
            return True
    if parts == (1,):
        state.suspended.append((previous, state.open_decimal))
        state.open_decimal = {}
        return True
    return False


def _accept_bare(state: _WalkState, parts: tuple[int, ...]) -> bool:
    """True when a bare number follows on from the numbering so far."""

    previous = state.last_decimal
    if previous is None:
        return parts == (1,)
    return is_decimal_successor(previous, parts)


def _open_schedule(state: _WalkState, marker: Marker, line: Line) -> _ClauseStart:
    """Build the clause a schedule heading starts, and reset the walk for its body."""

    clause_id = _unique(marker.token, state.used_ids)
    state.levels[clause_id] = 1
    state.scope_prefix = f"{clause_id}."
    state.scope_parent = clause_id
    state.base = clause_id
    state.last_decimal = None
    state.open_decimal = {}
    state.paren_stack = []
    state.suspended = []
    return _marker_clause_start(marker, line, clause_id, None, 1)


def _open_unnumbered_heading(state: _WalkState, line: Line) -> _ClauseStart:
    """Build the clause an unnumbered heading line starts, and end the bracket run."""

    state.paren_stack = []
    state.base = None
    return _ClauseStart(
        id=None,
        number=None,
        parent_id=None,
        level=1,
        start=line.start,
        body_start=line.start,
        line_end=line.end,
        heading_source=line.text,
        numbering_source=NUMBERING_NUMBERS,
        kind=None,
    )


def _open_paren_clause(state: _WalkState, marker: Marker, line: Line) -> _ClauseStart | None:
    """Build the clause a bracketed marker starts, or None when it is not the next one."""

    readings = paren_readings(marker.token)
    chosen: tuple[ParenStyle, int] | None = None
    for stack_index in range(len(state.paren_stack) - 1, -1, -1):
        style, value, _open_clause = state.paren_stack[stack_index]
        if (style, value + 1) in readings:
            del state.paren_stack[stack_index:]
            chosen = (style, value + 1)
            break
    if chosen is None:
        for style, value in readings:
            style_already_open = any(
                open_style == style for open_style, _open_value, _open_clause in state.paren_stack
            )
            if value == 1 and not style_already_open:
                chosen = (style, value)
                break
    if chosen is None:
        return None
    parent_id = state.paren_stack[-1][2] if state.paren_stack else state.base
    id_prefix = parent_id if parent_id is not None else state.scope_prefix
    clause_id = _unique(id_prefix + marker.id_part, state.used_ids)
    level = 1 if parent_id is None else state.levels[parent_id] + 1
    state.levels[clause_id] = level
    record = _marker_clause_start(marker, line, clause_id, parent_id, level)
    state.paren_stack.append((chosen[0], chosen[1], clause_id))
    return record


def _find_clause_starts(lines: tuple[Line, ...]) -> list[_ClauseStart]:
    """Walk the lines and return the clauses a marker or heading starts."""

    starts: list[_ClauseStart] = []
    markers = [find_marker(line.text) for line in lines]
    state = _WalkState()

    for index, line in enumerate(lines):
        marker = markers[index]
        if marker is None:
            if _is_heading_at(lines, markers, index):
                starts.append(_open_unnumbered_heading(state, line))
            continue
        if marker.kind is MarkerKind.SCHEDULE:
            starts.append(_open_schedule(state, marker, line))
        elif marker.kind is MarkerKind.DECIMAL or marker.kind is MarkerKind.KEYWORD:
            if _accept_decimal(state, marker.parts):
                starts.append(_open_numbered_clause(state, marker, line))
        elif marker.kind is MarkerKind.BARE:
            if _accept_bare(state, marker.parts):
                starts.append(_open_numbered_clause(state, marker, line))
        else:
            record = _open_paren_clause(state, marker, line)
            if record is not None:
                starts.append(record)
    return starts


def _build_clauses(text: str, starts: list[_ClauseStart]) -> tuple[Clause, ...]:
    """Add the text before the first clause, number unnumbered clauses, and
    give every clause its span and its sentence."""

    records = list(starts)
    first = records[0]
    if first.start > 0:
        text_before = text[: first.start]
        if not is_blank_text(text_before):
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
                    kind=None,
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
    if is_blank_text(text):
        return ()

    lines = split_lines(text)
    starts = _find_clause_starts(lines)
    if not any(start.id is not None for start in starts):
        return _split_paragraphs(text)
    return _build_clauses(text, starts)
