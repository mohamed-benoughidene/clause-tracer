"""The committed privacy fixture for the sample (S4-M1-T3).

The import wall keeps `privacy` from calling `ingest` or `links`, so the
sample reaches this module as a committed fixture. The writer and the
loader validate the format once at the door (D4, I9).
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, cast

from clause_tracer.core import (
    Clause,
    ClauseId,
    DefinedTerm,
    Document,
    FileKind,
    InputWarning,
    Party,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
)

FIXTURE_FORMAT: Final[str] = "clause-tracer-privacy-sample"
FIXTURE_VERSION: Final[int] = 1
_TEXT_KINDS: Final[frozenset[FileKind]] = frozenset(
    {FileKind.TEXT, FileKind.MARKDOWN, FileKind.PASTED}
)
_TOP_KEYS: Final[tuple[str, ...]] = ("format", "version", "document", "clauses", "parties", "terms")
_DOCUMENT_KEYS: Final[tuple[str, ...]] = ("schema_version", "source", "text", "warnings")
_SOURCE_KEYS: Final[tuple[str, ...]] = ("name", "kind", "sha256", "size")
_WARNING_KEYS: Final[tuple[str, ...]] = ("code", "page")
_CLAUSE_KEYS: Final[tuple[str, ...]] = (
    "id",
    "number",
    "heading",
    "level",
    "parent_id",
    "start",
    "end",
    "numbering_source",
    "sentences",
)
_SENTENCE_KEYS: Final[tuple[str, ...]] = ("id", "start", "end")
_PARTY_KEYS: Final[tuple[str, ...]] = ("name", "address", "yours")
_TERM_KEYS: Final[tuple[str, ...]] = ("term", "definition", "uses")
_SPAN_KEYS: Final[tuple[str, ...]] = ("start", "end")


@dataclass(frozen=True, slots=True, kw_only=True)
class PrivacyInput:
    """The input of `find_personal_data`: the sample, its clauses and typed details."""

    document: Document
    clauses: tuple[Clause, ...]
    parties: tuple[Party, ...]
    terms: tuple[DefinedTerm, ...]


def dump_privacy_fixture(case: PrivacyInput) -> str:
    """Write a privacy fixture for a text document.

    Input:   a `PrivacyInput` whose document has no glyphs, pages or other
             non-text fields.
    Output:  the fixture text, ending in one newline.
    Raises:  ValueError when the document holds a non-text field, when its
             source kind is not a text kind, or when the input fails the
             structure checks (a caller bug).
    Effects: none (T1).
    """

    document = case.document
    if (
        document.char_map
        or document.glyphs
        or document.pages
        or document.furniture
        or document.hidden
        or document.undecodable
        or document.tracked_changes
    ):
        raise ValueError("privacy sample: text documents only")
    if document.source.kind not in _TEXT_KINDS:
        raise ValueError(f"privacy sample: kind {document.source.kind.value} is not a text kind")
    _check_input(case)
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
            for clause in case.clauses
        ],
        "parties": [
            {"name": party.name, "address": party.address, "yours": party.yours}
            for party in case.parties
        ],
        "terms": [
            {
                "term": term.term,
                "definition": {"start": term.definition.start, "end": term.definition.end},
                "uses": [{"start": use.start, "end": use.end} for use in term.uses],
            }
            for term in case.terms
        ],
    }
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def load_privacy_fixture(text: str) -> PrivacyInput:
    """Read a privacy fixture.

    Input:   fixture text written by `dump_privacy_fixture`.
    Output:  the document, its clauses, the typed parties and the defined terms.
    Raises:  ValueError with the prefix "privacy sample: " when the text is
             not a well-formed text fixture.
    Effects: none (T1).
    """

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("privacy sample: not JSON") from error
    if not isinstance(raw, dict):
        raise ValueError("privacy sample: top level is not an object")
    data = cast(dict[str, object], raw)
    if data.get("format") != FIXTURE_FORMAT:
        raise ValueError(f"privacy sample: format is not {FIXTURE_FORMAT}")
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != FIXTURE_VERSION:
        raise ValueError(f"privacy sample: version is not {FIXTURE_VERSION}")
    _validate_top(data)

    document_row = cast(dict[str, object], data["document"])
    source_row = cast(dict[str, object], document_row["source"])
    document = Document(
        schema_version=_int_field(document_row, "schema_version"),
        source=SourceFile(
            name=_string_field(source_row, "name"),
            kind=_text_kind(_string_field(source_row, "kind")),
            sha256=_string_field(source_row, "sha256"),
            size=_int_field(source_row, "size"),
        ),
        text=_string_field(document_row, "text"),
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=tuple(
            InputWarning(
                code=_string_field(cast(dict[str, object], row), "code"),
                page=_optional_int_field(cast(dict[str, object], row), "page"),
            )
            for row in cast(list[object], document_row["warnings"])
        ),
    )

    clauses: list[Clause] = []
    for row_value in cast(list[object], data["clauses"]):
        row = cast(dict[str, object], row_value)
        sentences: list[Sentence] = []
        for sentence_value in cast(list[object], row["sentences"]):
            sentence_row = cast(dict[str, object], sentence_value)
            sentences.append(
                Sentence(
                    id=SentenceId(_string_field(sentence_row, "id")),
                    span=_span(sentence_row),
                )
            )
        clauses.append(
            Clause(
                id=ClauseId(_string_field(row, "id")),
                number=_optional_string_field(row, "number"),
                heading=_optional_string_field(row, "heading"),
                level=_int_field(row, "level"),
                parent_id=_optional_clause_id_field(row, "parent_id"),
                span=_span(row),
                numbering_source=_string_field(row, "numbering_source"),
                sentences=tuple(sentences),
            )
        )

    parties = tuple(
        Party(
            name=_string_field(cast(dict[str, object], row), "name"),
            address=_optional_string_field(cast(dict[str, object], row), "address"),
            yours=_bool_field(cast(dict[str, object], row), "yours"),
        )
        for row in cast(list[object], data["parties"])
    )

    terms = tuple(
        DefinedTerm(
            term=_string_field(cast(dict[str, object], row), "term"),
            definition=_span(cast(dict[str, object], cast(dict[str, object], row)["definition"])),
            uses=tuple(
                _span(cast(dict[str, object], use))
                for use in cast(list[object], cast(dict[str, object], row)["uses"])
            ),
        )
        for row in cast(list[object], data["terms"])
    )

    case = PrivacyInput(
        document=document,
        clauses=tuple(clauses),
        parties=parties,
        terms=terms,
    )
    _check_input(case)
    return case


def _validate_top(data: Mapping[str, object]) -> None:
    _check_keys(data, _TOP_KEYS)
    _validate_document(data["document"])
    _validate_clauses(data["clauses"])
    _validate_parties(data["parties"])
    _validate_terms(data["terms"])


def _validate_document(value: object) -> None:
    data = _object(value, "document")
    _check_keys(data, _DOCUMENT_KEYS)
    _require_int(data["schema_version"], "schema_version")
    _require_string(data["text"], "text")
    _validate_source(data["source"])
    _validate_warnings(data["warnings"])


def _validate_source(value: object) -> None:
    data = _object(value, "source")
    _check_keys(data, _SOURCE_KEYS)
    _require_string(data["name"], "name")
    _require_string(data["kind"], "kind")
    _require_string(data["sha256"], "sha256")
    _require_int(data["size"], "size")


def _validate_warnings(value: object) -> None:
    for row in _list(value, "warnings"):
        data = _object(row, "warnings")
        _check_keys(data, _WARNING_KEYS)
        _require_string(data["code"], "code")
        _require_optional_int(data["page"], "page")


def _validate_clauses(value: object) -> None:
    for row in _list(value, "clauses"):
        data = _object(row, "clauses")
        _check_keys(data, _CLAUSE_KEYS)
        _require_string(data["id"], "id")
        _require_optional_string(data["number"], "number")
        _require_optional_string(data["heading"], "heading")
        _require_int(data["level"], "level")
        _require_optional_string(data["parent_id"], "parent_id")
        _require_int(data["start"], "start")
        _require_int(data["end"], "end")
        _require_string(data["numbering_source"], "numbering_source")
        _validate_sentences(data["sentences"])


def _validate_sentences(value: object) -> None:
    for row in _list(value, "sentences"):
        data = _object(row, "sentences")
        _check_keys(data, _SENTENCE_KEYS)
        _require_string(data["id"], "id")
        _require_int(data["start"], "start")
        _require_int(data["end"], "end")


def _validate_parties(value: object) -> None:
    for row in _list(value, "parties"):
        data = _object(row, "parties")
        _check_keys(data, _PARTY_KEYS)
        _require_string(data["name"], "name")
        _require_optional_string(data["address"], "address")
        _require_bool(data["yours"], "yours")


def _validate_terms(value: object) -> None:
    for row in _list(value, "terms"):
        data = _object(row, "terms")
        _check_keys(data, _TERM_KEYS)
        _require_string(data["term"], "term")
        _validate_span(data["definition"], "definition")
        _validate_spans(data["uses"], "uses")


def _validate_span(value: object, key: str) -> None:
    data = _object(value, key)
    _check_keys(data, _SPAN_KEYS)
    _require_int(data["start"], "start")
    _require_int(data["end"], "end")


def _validate_spans(value: object, key: str) -> None:
    for row in _list(value, key):
        _validate_span(row, key)


def _check_keys(data: Mapping[str, object], keys: tuple[str, ...]) -> None:
    for key in data:
        if key not in keys:
            raise ValueError(f"privacy sample: unknown key {key}")
    for key in keys:
        if key not in data:
            raise ValueError(f"privacy sample: missing key {key}")


def _object(value: object, key: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"privacy sample: {key} has the wrong type")
    return cast(dict[str, object], value)


def _list(value: object, key: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"privacy sample: {key} has the wrong type")
    return cast(list[object], value)


def _require_int(value: object, key: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"privacy sample: {key} has the wrong type")
    return value


def _require_string(value: object, key: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"privacy sample: {key} has the wrong type")
    return value


def _require_bool(value: object, key: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"privacy sample: {key} has the wrong type")
    return value


def _require_optional_int(value: object, key: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, key)


def _require_optional_string(value: object, key: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, key)


def _int_field(data: Mapping[str, object], key: str) -> int:
    return cast(int, data[key])


def _string_field(data: Mapping[str, object], key: str) -> str:
    return cast(str, data[key])


def _bool_field(data: Mapping[str, object], key: str) -> bool:
    return cast(bool, data[key])


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
        raise ValueError(f"privacy sample: kind {written} is not a text kind") from error
    if kind not in _TEXT_KINDS:
        raise ValueError(f"privacy sample: kind {written} is not a text kind")
    return kind


def _span(data: Mapping[str, object]) -> Span:
    return Span(start=_int_field(data, "start"), end=_int_field(data, "end"))


def _check_span(span: Span, text: str, item_id: str) -> None:
    if span.start < 0 or span.end < span.start or span.end > len(text):
        raise ValueError(f"privacy sample: span of {item_id} is outside the text")


def _check_input(case: PrivacyInput) -> None:
    """Check the spans and structure of the input, raising on the first failure."""

    text = case.document.text

    for clause in case.clauses:
        _check_span(clause.span, text, str(clause.id))
    for clause in case.clauses:
        for sentence in clause.sentences:
            _check_span(sentence.span, text, str(sentence.id))
    for term in case.terms:
        _check_span(term.definition, text, term.term)
        for use in term.uses:
            _check_span(use, text, term.term)

    for clause in case.clauses:
        if clause.level < 1:
            raise ValueError(f"privacy sample: level of {clause.id} is not 1 or more")

    seen_clauses: set[ClauseId] = set()
    for clause in case.clauses:
        if clause.id in seen_clauses:
            raise ValueError(f"privacy sample: duplicate clause id {clause.id}")
        seen_clauses.add(clause.id)

    seen_sentences: set[SentenceId] = set()
    for clause in case.clauses:
        for sentence in clause.sentences:
            if sentence.id in seen_sentences:
                raise ValueError(f"privacy sample: duplicate sentence id {sentence.id}")
            seen_sentences.add(sentence.id)

    for clause in case.clauses:
        for sentence in clause.sentences:
            if sentence.span.start < clause.span.start or sentence.span.end > clause.span.end:
                raise ValueError(f"privacy sample: span of {sentence.id} is outside its clause")

    previous_clause: Clause | None = None
    for clause in case.clauses:
        if previous_clause is not None and clause.span.start < previous_clause.span.end:
            raise ValueError(f"privacy sample: clause {clause.id} is out of order")
        previous_clause = clause

    for clause in case.clauses:
        previous_sentence: Sentence | None = None
        for sentence in clause.sentences:
            if previous_sentence is not None and sentence.span.start < previous_sentence.span.end:
                raise ValueError(f"privacy sample: sentence {sentence.id} is out of order")
            previous_sentence = sentence

    for party in case.parties:
        if not party.name.strip():
            raise ValueError("privacy sample: party name is empty")
