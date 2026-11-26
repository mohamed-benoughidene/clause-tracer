"""The committed clause fixture for the sample (S3-M1-T3).

The import wall keeps `links` from calling `ingest`, so the sample reaches
this module as a committed clause fixture. The writer and loader validate
the format once at the door (D4, I9).
"""

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final, cast

from clause_tracer.core import (
    Clause,
    ClauseId,
    Document,
    FileKind,
    InputWarning,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
)

FIXTURE_FORMAT: Final[str] = "clause-tracer-links-sample"
FIXTURE_VERSION: Final[int] = 1
_TEXT_KINDS: Final[frozenset[FileKind]] = frozenset(
    {FileKind.TEXT, FileKind.MARKDOWN, FileKind.PASTED}
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SampleInput:
    """The sample contract's document and clauses, as `ingest` returns them."""

    document: Document
    clauses: tuple[Clause, ...]


def dump_clause_fixture(document: Document, clauses: tuple[Clause, ...]) -> str:
    """Write a clause fixture for a text document.

    Input:   a Document without glyphs, and its clauses.
    Output:  the fixture text, ending in one newline.
    Raises:  ValueError when the document holds glyphs, pages or other
             non-text fields, when its source kind is not a text kind, or
             when the clauses fail the structure checks (a caller bug).
    Effects: none (T1).
    """

    if (
        document.char_map
        or document.glyphs
        or document.pages
        or document.furniture
        or document.hidden
        or document.undecodable
        or document.tracked_changes
        or document.side_text
    ):
        raise ValueError("links sample: text documents only")
    if document.source.kind not in _TEXT_KINDS:
        raise ValueError(f"links sample: kind {document.source.kind.value} is not a text kind")
    _check_clauses(document.text, clauses)
    obj = {
        "format": FIXTURE_FORMAT,
        "version": FIXTURE_VERSION,
        "document": {
            "schema_version": document.schema_version,
            "source": {
                "name": document.source.name,
                "kind": document.source.kind.value,
                "sha256": document.source.sha256,
                "size": document.source.size,
            },
            "text": document.text,
            "warnings": [
                {"code": warning.code, "page": warning.page} for warning in document.warnings
            ],
        },
        "clauses": [
            {
                "id": str(clause.id),
                "number": clause.number,
                "heading": clause.heading,
                "level": clause.level,
                "parent_id": None if clause.parent_id is None else str(clause.parent_id),
                "start": clause.span.start,
                "end": clause.span.end,
                "numbering_source": clause.numbering_source,
                "sentences": [
                    {
                        "id": str(sentence.id),
                        "start": sentence.span.start,
                        "end": sentence.span.end,
                    }
                    for sentence in clause.sentences
                ],
            }
            for clause in clauses
        ],
    }
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def load_clause_fixture(text: str) -> SampleInput:
    """Read a clause fixture.

    Input:   fixture text written by `dump_clause_fixture`.
    Output:  the document and its clauses.
    Raises:  ValueError with the prefix "links sample: " when the text is
             not a well-formed text fixture.
    Effects: none (T1).
    """

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("links sample: not JSON") from error
    if not isinstance(raw, dict):
        raise ValueError("links sample: top level is not an object")
    data = cast(dict[str, object], raw)
    if data.get("format") != FIXTURE_FORMAT:
        raise ValueError(f"links sample: format is not {FIXTURE_FORMAT}")
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != FIXTURE_VERSION:
        raise ValueError(f"links sample: version is not {FIXTURE_VERSION}")
    _validate_mapping(
        data,
        "top level",
        {
            "format": _ignore,
            "version": _ignore,
            "document": _validate_document,
            "clauses": _validate_clauses,
        },
    )

    document_row = cast(dict[str, object], data["document"])
    source_row = cast(dict[str, object], document_row["source"])
    text_value = _string_field(document_row, "text")
    warnings = tuple(
        InputWarning(
            code=_string_field(cast(dict[str, object], row), "code"),
            page=_optional_int_field(cast(dict[str, object], row), "page"),
        )
        for row in cast(list[object], document_row["warnings"])
    )
    document = Document(
        schema_version=_int_field(document_row, "schema_version"),
        source=SourceFile(
            name=_string_field(source_row, "name"),
            kind=_text_kind(_string_field(source_row, "kind")),
            sha256=_string_field(source_row, "sha256"),
            size=_int_field(source_row, "size"),
        ),
        text=text_value,
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=warnings,
    )

    clauses: list[Clause] = []
    for row_value in cast(list[object], data["clauses"]):
        row = cast(dict[str, object], row_value)
        clause_id = ClauseId(_string_field(row, "id"))
        span = _span(row)
        sentences: list[Sentence] = []
        for sentence_value in cast(list[object], row["sentences"]):
            sentence_row = cast(dict[str, object], sentence_value)
            sentence_id = SentenceId(_string_field(sentence_row, "id"))
            sentence_span = _span(sentence_row)
            sentences.append(Sentence(id=sentence_id, span=sentence_span))
        clauses.append(
            Clause(
                id=clause_id,
                number=_optional_string_field(row, "number"),
                heading=_optional_string_field(row, "heading"),
                level=_int_field(row, "level"),
                parent_id=_optional_clause_id_field(row, "parent_id"),
                span=span,
                numbering_source=_string_field(row, "numbering_source"),
                sentences=tuple(sentences),
            )
        )

    _check_clauses(text_value, clauses)
    return SampleInput(document=document, clauses=tuple(clauses))


def _validate_mapping(
    value: object,
    key: str,
    validators: Mapping[str, Callable[[object], object]],
) -> None:
    """Check an object's keys and values in JSON order."""

    if not isinstance(value, dict):
        raise ValueError(f"links sample: {key} has the wrong type")
    data = cast(dict[str, object], value)
    for item_key, item_value in data.items():
        validator = validators.get(item_key)
        if validator is None:
            raise ValueError(f"links sample: unknown key {item_key}")
        validator(item_value)
    for required_key in validators:
        if required_key not in data:
            raise ValueError(f"links sample: missing key {required_key}")


def _ignore(value: object) -> None:
    """Accept a value that an earlier check has already validated."""


def _validate_document(value: object) -> None:
    _validate_mapping(
        value,
        "document",
        {
            "schema_version": lambda item: _require_int(item, "schema_version"),
            "source": _validate_source,
            "text": lambda item: _require_string(item, "text"),
            "warnings": _validate_warnings,
        },
    )


def _validate_source(value: object) -> None:
    _validate_mapping(
        value,
        "source",
        {
            "name": lambda item: _require_string(item, "name"),
            "kind": lambda item: _require_string(item, "kind"),
            "sha256": lambda item: _require_string(item, "sha256"),
            "size": lambda item: _require_int(item, "size"),
        },
    )


def _validate_warnings(value: object) -> None:
    for row in _require_list(value, "warnings"):
        _validate_mapping(
            row,
            "warnings",
            {
                "code": lambda item: _require_string(item, "code"),
                "page": lambda item: _require_optional_int(item, "page"),
            },
        )


def _validate_clauses(value: object) -> None:
    for row in _require_list(value, "clauses"):
        _validate_mapping(
            row,
            "clauses",
            {
                "id": lambda item: _require_string(item, "id"),
                "number": lambda item: _require_optional_string(item, "number"),
                "heading": lambda item: _require_optional_string(item, "heading"),
                "level": lambda item: _require_int(item, "level"),
                "parent_id": lambda item: _require_optional_string(item, "parent_id"),
                "start": lambda item: _require_int(item, "start"),
                "end": lambda item: _require_int(item, "end"),
                "numbering_source": lambda item: _require_string(item, "numbering_source"),
                "sentences": _validate_sentences,
            },
        )


def _validate_sentences(value: object) -> None:
    for row in _require_list(value, "sentences"):
        _validate_mapping(
            row,
            "sentences",
            {
                "id": lambda item: _require_string(item, "id"),
                "start": lambda item: _require_int(item, "start"),
                "end": lambda item: _require_int(item, "end"),
            },
        )


def _require_int(value: object, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"links sample: {key} has the wrong type")
    return value


def _require_string(value: object, key: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"links sample: {key} has the wrong type")
    return value


def _require_optional_int(value: object, key: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, key)


def _require_optional_string(value: object, key: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, key)


def _require_list(value: object, key: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"links sample: {key} has the wrong type")
    return cast(list[object], value)


def _int_field(data: Mapping[str, object], key: str) -> int:
    return cast(int, data[key])


def _string_field(data: Mapping[str, object], key: str) -> str:
    return cast(str, data[key])


def _optional_int_field(data: Mapping[str, object], key: str) -> int | None:
    value = data[key]
    return None if value is None else cast(int, value)


def _optional_string_field(data: Mapping[str, object], key: str) -> str | None:
    value = data[key]
    return None if value is None else cast(str, value)


def _optional_clause_id_field(data: Mapping[str, object], key: str) -> ClauseId | None:
    value = _optional_string_field(data, key)
    return None if value is None else ClauseId(value)


def _text_kind(written: str) -> FileKind:
    try:
        kind = FileKind(written)
    except ValueError as error:
        raise ValueError(f"links sample: kind {written} is not a text kind") from error
    if kind not in _TEXT_KINDS:
        raise ValueError(f"links sample: kind {written} is not a text kind")
    return kind


def _span(data: Mapping[str, object]) -> Span:
    return Span(start=_int_field(data, "start"), end=_int_field(data, "end"))


def _check_span(span: Span, text: str, item_id: ClauseId | SentenceId) -> None:
    if span.start < 0 or span.end < span.start or span.end > len(text):
        raise ValueError(f"links sample: span of {item_id} is outside the text")


def _check_clauses(text: str, clauses: Sequence[Clause]) -> None:
    """Check the spans and structure of every clause, raising on the first failure."""

    by_id: dict[ClauseId, Clause] = {}
    previous: Clause | None = None
    seen_sentences: set[SentenceId] = set()

    for clause in clauses:
        _check_span(clause.span, text, clause.id)
        for sentence in clause.sentences:
            _check_span(sentence.span, text, sentence.id)

        if clause.id in by_id:
            raise ValueError(f"links sample: duplicate clause id {clause.id}")

        parent = None if clause.parent_id is None else by_id.get(clause.parent_id)
        if clause.parent_id is not None and parent is None:
            raise ValueError(f"links sample: unknown parent {clause.parent_id}")

        for sentence in clause.sentences:
            if sentence.span.start < clause.span.start or sentence.span.end > clause.span.end:
                raise ValueError(f"links sample: span of {sentence.id} is outside its clause")

        if clause.level < 1:
            raise ValueError(f"links sample: level of {clause.id} is not 1 or more")
        if parent is None:
            if clause.level != 1:
                raise ValueError(f"links sample: level of {clause.id} does not fit its parent")
        elif clause.level != parent.level + 1:
            raise ValueError(f"links sample: level of {clause.id} does not fit its parent")

        if previous is not None and clause.span.start < previous.span.end:
            raise ValueError(f"links sample: span of {clause.id} overlaps an earlier clause")

        for sentence in clause.sentences:
            if sentence.id in seen_sentences:
                raise ValueError(f"links sample: duplicate sentence id {sentence.id}")
            seen_sentences.add(sentence.id)

        by_id[clause.id] = clause
        previous = clause
