"""Build small link cases without `ingest` (S3-M1-T5).

Test code, not exported from `links`. Each clause row is one clause, and
the clause and sentence spans tile the text with no gap (S2, T3).
"""

import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, cast

from clause_tracer.core import (
    Clause,
    ClauseId,
    Document,
    FileKind,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
)
from clause_tracer.links.sample_clauses import SampleInput

_ALLOWED_KEYS: Final[frozenset[str]] = frozenset({"id", "sentences", "parent", "heading", "number"})


@dataclass(frozen=True, slots=True, kw_only=True)
class _Row:
    id: ClauseId
    sentences: tuple[str, ...]
    parent_id: ClauseId | None
    heading: str | None
    number: str | None
    level: int


def build_case(rows: Sequence[Mapping[str, object]]) -> SampleInput:
    """Build a document and its clauses from short rows.

    Input:   rows with `id` and `sentences`, and optional `parent`,
             `heading` and `number`.
    Output:  a pasted-text document and its clauses, with spans that tile it.
    Raises:  ValueError for an unknown key, a missing key, a wrong type, a
             repeated id, a line break in a sentence, or an unknown parent.
    Effects: none (T1).
    """

    parsed = _parse_rows(rows)
    clause_texts = [" ".join(row.sentences) for row in parsed]
    text = "\n".join(clause_texts)
    has_rows = bool(parsed)
    every_id_is_a_paragraph = all(_is_paragraph_id(str(row.id)) for row in parsed)
    numbering_source = "paragraphs" if has_rows and every_id_is_a_paragraph else "numbers"
    clauses = _build_clauses(parsed, numbering_source=numbering_source)
    document = Document(
        schema_version=1,
        source=SourceFile(
            name="case.txt",
            kind=FileKind.PASTED,
            sha256=hashlib.sha256(text.encode()).hexdigest(),
            size=len(text.encode()),
        ),
        text=text,
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )
    return SampleInput(document=document, clauses=clauses)


def span_of(text: str, needle: str, nth: int = 1) -> Span:
    """Return the span of the nth occurrence of `needle` in `text`."""

    start = -1
    for _ in range(nth):
        start = text.find(needle, start + 1)
        if start == -1:
            raise AssertionError(f"{needle!r} occurs fewer than {nth} times")
    return Span(start=start, end=start + len(needle))


def _parse_rows(rows: Sequence[Mapping[str, object]]) -> list[_Row]:
    parsed: list[_Row] = []
    levels: dict[ClauseId, int] = {}
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in _ALLOWED_KEYS:
                raise ValueError(f"unknown key {key}")
        if "id" not in row:
            raise ValueError("missing key id")
        if "sentences" not in row:
            raise ValueError("missing key sentences")
        clause_id = cast(str, _string(row, "id"))
        sentences = _sentences(row["sentences"])
        parent = _string(row, "parent")
        heading = _string(row, "heading")
        written_number = _string(row, "number")
        if clause_id in seen:
            raise ValueError(f"duplicate id {clause_id}")
        seen.add(clause_id)
        for sentence in sentences:
            if sentence == "" or "\n" in sentence or "\r" in sentence:
                raise ValueError("a sentence must be non-empty and hold no line break")

        parent_id = None if parent is None else ClauseId(parent)
        if parent_id is None:
            level = 1
        else:
            if parent_id not in levels:
                raise ValueError(f"unknown parent {parent}")
            level = levels[parent_id] + 1
        if _is_paragraph_id(clause_id):
            number = None
        elif written_number is not None:
            number = written_number
        else:
            number = clause_id
        parsed.append(
            _Row(
                id=ClauseId(clause_id),
                sentences=sentences,
                parent_id=parent_id,
                heading=heading,
                number=number,
                level=level,
            )
        )
        levels[ClauseId(clause_id)] = level
    return parsed


def _string(row: Mapping[str, object], key: str) -> str | None:
    if key not in row:
        return None
    value = row[key]
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _sentences(value: object) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(sentence, str) for sentence in value)
    ):
        raise ValueError("sentences must be a non-empty list of strings")
    return tuple(cast(list[str], value))


def _is_paragraph_id(clause_id: str) -> bool:
    return re.fullmatch(r"p[0-9]+(~[0-9]+)?", clause_id) is not None


def _build_clauses(rows: list[_Row], *, numbering_source: str) -> tuple[Clause, ...]:
    clauses: list[Clause] = []
    offset = 0
    last_clause = len(rows) - 1
    for clause_index, row in enumerate(rows):
        clause_start = offset
        sentences: list[Sentence] = []
        last_sentence = len(row.sentences) - 1
        for sentence_index, sentence_text in enumerate(row.sentences):
            sentence_start = offset
            is_last = clause_index == last_clause and sentence_index == last_sentence
            sentence_end = sentence_start + len(sentence_text) + (0 if is_last else 1)
            sentences.append(
                Sentence(
                    id=SentenceId(f"{row.id}.s{sentence_index + 1}"),
                    span=Span(start=sentence_start, end=sentence_end),
                )
            )
            offset = sentence_end
        clauses.append(
            Clause(
                id=row.id,
                number=row.number,
                heading=row.heading,
                level=row.level,
                parent_id=row.parent_id,
                span=Span(start=clause_start, end=offset),
                numbering_source=numbering_source,
                sentences=tuple(sentences),
            )
        )
    return tuple(clauses)
