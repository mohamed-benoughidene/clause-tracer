"""The clause fixture format, its writer and its loader (S3-M1-T3)."""

import json
from dataclasses import replace

import pytest

from clause_tracer.core import (
    Clause,
    ClauseId,
    Document,
    FileKind,
    InputWarning,
    Page,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
)
from clause_tracer.links.sample_clauses import (
    SampleInput,
    dump_clause_fixture,
    load_clause_fixture,
)

TEXT = "1. Payment\n1.1 Paid.\n"


def _document(text: str) -> Document:
    return Document(
        schema_version=1,
        source=SourceFile(
            name="t.txt",
            kind=FileKind.TEXT,
            sha256="0" * 64,
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


def _clauses() -> tuple[Clause, ...]:
    return (
        Clause(
            id=ClauseId("1"),
            number="1",
            heading="Payment",
            level=1,
            parent_id=None,
            span=Span(start=0, end=11),
            numbering_source="numbers",
            sentences=(Sentence(id=SentenceId("1.s1"), span=Span(start=0, end=11)),),
        ),
        Clause(
            id=ClauseId("1.1"),
            number="1.1",
            heading=None,
            level=2,
            parent_id=ClauseId("1"),
            span=Span(start=11, end=21),
            numbering_source="numbers",
            sentences=(Sentence(id=SentenceId("1.1.s1"), span=Span(start=11, end=21)),),
        ),
    )


def _fixture() -> dict[str, object]:
    data = json.loads(dump_clause_fixture(_document(TEXT), _clauses()))
    assert isinstance(data, dict)
    return data


def _load(data: object) -> SampleInput:
    return load_clause_fixture(json.dumps(data))


def _document_row(data: dict[str, object]) -> dict[str, object]:
    document = data["document"]
    assert isinstance(document, dict)
    return document


def _source_row(data: dict[str, object]) -> dict[str, object]:
    source = _document_row(data)["source"]
    assert isinstance(source, dict)
    return source


def _clause_rows(data: dict[str, object]) -> list[dict[str, object]]:
    clauses = data["clauses"]
    assert isinstance(clauses, list)
    rows: list[dict[str, object]] = []
    for row in clauses:
        assert isinstance(row, dict)
        rows.append(row)
    return rows


def _sentence_rows(row: dict[str, object]) -> list[dict[str, object]]:
    sentences = row["sentences"]
    assert isinstance(sentences, list)
    rows: list[dict[str, object]] = []
    for sentence in sentences:
        assert isinstance(sentence, dict)
        rows.append(sentence)
    return rows


def _message(error: pytest.ExceptionInfo[ValueError]) -> str:
    return str(error.value)


def test_round_trip() -> None:
    document = _document(TEXT)
    clauses = _clauses()

    assert load_clause_fixture(dump_clause_fixture(document, clauses)) == SampleInput(
        document=document, clauses=clauses
    )


def test_dump_ends_with_one_newline() -> None:
    assert dump_clause_fixture(_document(TEXT), _clauses()).endswith("}\n")


def test_dump_keeps_non_ascii() -> None:
    dumped = dump_clause_fixture(_document("£"), ())

    assert "£" in dumped
    assert "\\u00a3" not in dumped


def test_warning_round_trips() -> None:
    document = replace(
        _document(TEXT),
        warnings=(InputWarning(code="not_english", page=None),),
    )

    assert load_clause_fixture(dump_clause_fixture(document, _clauses())) == SampleInput(
        document=document, clauses=_clauses()
    )


def test_dump_refuses_glyphs() -> None:
    document = replace(
        _document(TEXT),
        pages=(Page(number=1, width=1.0, height=1.0),),
    )

    with pytest.raises(ValueError):
        dump_clause_fixture(document, _clauses())


def test_not_json() -> None:
    with pytest.raises(ValueError) as error:
        load_clause_fixture("{")

    assert _message(error).startswith("links sample: ")


def test_wrong_format() -> None:
    data = _fixture()
    data["format"] = "other"

    with pytest.raises(ValueError):
        _load(data)


def test_wrong_version() -> None:
    data = _fixture()
    data["version"] = 2

    with pytest.raises(ValueError):
        _load(data)


def test_unknown_key() -> None:
    data = _fixture()
    _clause_rows(data)[0]["x"] = 1

    with pytest.raises(ValueError) as error:
        _load(data)

    assert "x" in _message(error)


def test_missing_key() -> None:
    data = _fixture()
    del _clause_rows(data)[0]["sentences"]

    with pytest.raises(ValueError) as error:
        _load(data)

    assert "sentences" in _message(error)


def test_bool_is_not_int() -> None:
    data = _fixture()
    _clause_rows(data)[0]["level"] = True

    with pytest.raises(ValueError):
        _load(data)


def test_span_outside_text() -> None:
    data = _fixture()
    _clause_rows(data)[0]["end"] = 999

    with pytest.raises(ValueError):
        _load(data)


def test_unknown_kind() -> None:
    data = _fixture()
    _source_row(data)["kind"] = "fax"

    with pytest.raises(ValueError):
        _load(data)


def test_word_kind_is_refused() -> None:
    data = _fixture()
    _source_row(data)["kind"] = "word"

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "links sample: kind word is not a text kind"


def test_duplicate_clause_id() -> None:
    data = _fixture()
    _clause_rows(data)[1]["id"] = "1"

    with pytest.raises(ValueError):
        _load(data)


def test_unknown_parent() -> None:
    data = _fixture()
    _clause_rows(data)[1]["parent_id"] = "9"

    with pytest.raises(ValueError):
        _load(data)


def test_sentence_outside_its_clause() -> None:
    data = _fixture()
    _sentence_rows(_clause_rows(data)[0])[0]["end"] = 15

    with pytest.raises(ValueError):
        _load(data)


def test_level_below_one() -> None:
    data = _fixture()
    _clause_rows(data)[0]["level"] = 0

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "links sample: level of 1 is not 1 or more"


def test_level_does_not_fit_parent() -> None:
    data = _fixture()
    _clause_rows(data)[1]["level"] = 3

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "links sample: level of 1.1 does not fit its parent"


def test_root_level_must_be_one() -> None:
    data = _fixture()
    _clause_rows(data)[0]["level"] = 2

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "links sample: level of 1 does not fit its parent"


def test_clause_overlap() -> None:
    data = _fixture()
    _clause_rows(data)[1]["start"] = 5
    _sentence_rows(_clause_rows(data)[1])[0]["start"] = 5

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "links sample: span of 1.1 overlaps an earlier clause"


def test_duplicate_sentence_id() -> None:
    data = _fixture()
    _sentence_rows(_clause_rows(data)[1])[0]["id"] = "1.s1"

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "links sample: duplicate sentence id 1.s1"


def test_dump_refuses_a_pdf_kind() -> None:
    document = replace(
        _document(TEXT),
        source=SourceFile(
            name="t.pdf",
            kind=FileKind.PDF,
            sha256="0" * 64,
            size=len(TEXT.encode()),
        ),
    )

    with pytest.raises(ValueError) as error:
        dump_clause_fixture(document, _clauses())

    assert _message(error) == "links sample: kind pdf is not a text kind"


def test_dump_refuses_a_span_outside_the_text() -> None:
    first, second = _clauses()
    bad = replace(first, span=Span(start=0, end=999))

    with pytest.raises(ValueError) as error:
        dump_clause_fixture(_document(TEXT), (bad, second))

    assert _message(error) == "links sample: span of 1 is outside the text"


def test_dump_refuses_a_duplicate_clause_id() -> None:
    first, second = _clauses()
    duplicate = replace(second, id=ClauseId("1"))

    with pytest.raises(ValueError) as error:
        dump_clause_fixture(_document(TEXT), (first, duplicate))

    assert _message(error) == "links sample: duplicate clause id 1"
