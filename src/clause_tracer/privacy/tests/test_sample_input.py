"""The privacy fixture format, its writer and its loader (S4-M1-T3)."""

import json
from dataclasses import replace
from typing import cast

import pytest

from clause_tracer.core import (
    Clause,
    ClauseId,
    DefinedTerm,
    Document,
    FileKind,
    InputWarning,
    Page,
    Party,
    Sentence,
    SentenceId,
    SideText,
    SideTextKind,
    SourceFile,
    Span,
)
from clause_tracer.privacy.sample_input import (
    PrivacyInput,
    dump_privacy_fixture,
    load_privacy_fixture,
)

TEXT = "1. Pay Brightline Ltd.\n"


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


def _case() -> PrivacyInput:
    return PrivacyInput(
        document=_document(TEXT),
        clauses=(
            Clause(
                id=ClauseId("1"),
                number="1",
                heading=None,
                level=1,
                parent_id=None,
                span=Span(start=0, end=23),
                numbering_source="numbers",
                sentences=(Sentence(id=SentenceId("1.s1"), span=Span(start=0, end=23)),),
            ),
        ),
        parties=(Party(name="Brightline Ltd", address=None, yours=False),),
        terms=(
            DefinedTerm(
                term="Agency",
                definition=Span(start=0, end=23),
                uses=(Span(start=3, end=6),),
            ),
        ),
    )


def _fixture() -> dict[str, object]:
    data = json.loads(dump_privacy_fixture(_case()))
    assert isinstance(data, dict)
    return data


def _load(data: object) -> PrivacyInput:
    return load_privacy_fixture(json.dumps(data))


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
    for row in clauses:
        assert isinstance(row, dict)
    return cast(list[dict[str, object]], clauses)


def _party_rows(data: dict[str, object]) -> list[dict[str, object]]:
    parties = data["parties"]
    assert isinstance(parties, list)
    rows: list[dict[str, object]] = []
    for row in parties:
        assert isinstance(row, dict)
        rows.append(row)
    return rows


def _term_rows(data: dict[str, object]) -> list[dict[str, object]]:
    terms = data["terms"]
    assert isinstance(terms, list)
    rows: list[dict[str, object]] = []
    for row in terms:
        assert isinstance(row, dict)
        rows.append(row)
    return rows


def _use_rows(row: dict[str, object]) -> list[dict[str, object]]:
    uses = row["uses"]
    assert isinstance(uses, list)
    rows: list[dict[str, object]] = []
    for use in uses:
        assert isinstance(use, dict)
        rows.append(use)
    return rows


def _message(error: pytest.ExceptionInfo[ValueError]) -> str:
    return str(error.value)


def test_round_trip() -> None:
    assert load_privacy_fixture(dump_privacy_fixture(_case())) == _case()


def test_dump_ends_with_one_newline() -> None:
    assert dump_privacy_fixture(_case()).endswith("}\n")


def test_dump_keeps_non_ascii() -> None:
    text = "£5 due.\n"
    case = PrivacyInput(
        document=_document(text),
        clauses=(
            Clause(
                id=ClauseId("1"),
                number="1",
                heading=None,
                level=1,
                parent_id=None,
                span=Span(start=0, end=8),
                numbering_source="numbers",
                sentences=(Sentence(id=SentenceId("1.s1"), span=Span(start=0, end=8)),),
            ),
        ),
        parties=(Party(name="Brightline £", address=None, yours=False),),
        terms=(),
    )

    dumped = dump_privacy_fixture(case)

    assert "£" in dumped
    assert "\\u00a3" not in dumped


def test_warning_round_trips() -> None:
    case = _case()
    document = replace(
        case.document,
        warnings=(InputWarning(code="not_english", page=None),),
    )
    warned = replace(case, document=document)

    assert load_privacy_fixture(dump_privacy_fixture(warned)) == warned


def test_dump_refuses_glyphs() -> None:
    case = _case()
    document = replace(
        case.document,
        pages=(Page(number=1, width=1.0, height=1.0),),
    )

    with pytest.raises(ValueError):
        dump_privacy_fixture(replace(case, document=document))


def test_dump_refuses_side_text() -> None:
    case = _case()
    document = replace(
        case.document,
        side_text=(SideText(kind=SideTextKind.COMMENT, ref="0", author="A", text="x"),),
    )

    with pytest.raises(ValueError):
        dump_privacy_fixture(replace(case, document=document))


def test_dump_refuses_a_pdf_kind() -> None:
    case = _case()
    document = replace(
        case.document,
        source=SourceFile(
            name="t.pdf",
            kind=FileKind.PDF,
            sha256="0" * 64,
            size=len(TEXT.encode()),
        ),
    )

    with pytest.raises(ValueError) as error:
        dump_privacy_fixture(replace(case, document=document))

    assert _message(error) == "privacy sample: kind pdf is not a text kind"


def test_not_json() -> None:
    with pytest.raises(ValueError) as error:
        load_privacy_fixture("{")

    assert _message(error).startswith("privacy sample: ")


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
    _party_rows(data)[0]["x"] = 1

    with pytest.raises(ValueError) as error:
        _load(data)

    assert "x" in _message(error)


def test_missing_key() -> None:
    data = _fixture()
    del _term_rows(data)[0]["uses"]

    with pytest.raises(ValueError) as error:
        _load(data)

    assert "uses" in _message(error)


def test_bool_is_not_int() -> None:
    data = _fixture()
    _clause_rows(data)[0]["level"] = True

    with pytest.raises(ValueError):
        _load(data)


def test_unknown_kind() -> None:
    data = _fixture()
    _source_row(data)["kind"] = "word"

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: kind word is not a text kind"


def test_span_outside_text() -> None:
    data = _fixture()
    _clause_rows(data)[0]["end"] = 999

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: span of 1 is outside the text"


def test_term_use_outside_text() -> None:
    data = _fixture()
    _use_rows(_term_rows(data)[0])[0]["end"] = 999

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: span of Agency is outside the text"


def test_level_below_one() -> None:
    data = _fixture()
    _clause_rows(data)[0]["level"] = 0

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: level of 1 is not 1 or more"


def test_duplicate_clause_id() -> None:
    data = _fixture()
    _clause_rows(data).append(
        {
            "id": "1",
            "number": "2",
            "heading": None,
            "level": 1,
            "parent_id": None,
            "start": 23,
            "end": 23,
            "numbering_source": "numbers",
            "sentences": [{"id": "1.s2", "start": 23, "end": 23}],
        }
    )

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: duplicate clause id 1"


def test_duplicate_sentence_id() -> None:
    data = _fixture()
    _clause_rows(data).append(
        {
            "id": "2",
            "number": "2",
            "heading": None,
            "level": 1,
            "parent_id": None,
            "start": 23,
            "end": 23,
            "numbering_source": "numbers",
            "sentences": [{"id": "1.s1", "start": 23, "end": 23}],
        }
    )

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: duplicate sentence id 1.s1"


def test_sentence_outside_its_clause() -> None:
    data = _fixture()
    _clause_rows(data)[0]["end"] = 10

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: span of 1.s1 is outside its clause"


def test_clause_out_of_order() -> None:
    data = _fixture()
    _clause_rows(data).append(
        {
            "id": "2",
            "number": "2",
            "heading": None,
            "level": 1,
            "parent_id": None,
            "start": 10,
            "end": 23,
            "numbering_source": "numbers",
            "sentences": [{"id": "2.s1", "start": 10, "end": 23}],
        }
    )

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: clause 2 is out of order"


def test_sentence_out_of_order() -> None:
    data = _fixture()
    _clause_rows(data)[0]["sentences"] = [
        {"id": "1.s1", "start": 10, "end": 23},
        {"id": "1.s2", "start": 5, "end": 23},
    ]

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: sentence 1.s2 is out of order"


def test_empty_party_name() -> None:
    data = _fixture()
    _party_rows(data)[0]["name"] = "  "

    with pytest.raises(ValueError) as error:
        _load(data)

    assert _message(error) == "privacy sample: party name is empty"


def test_dump_refuses_what_load_refuses() -> None:
    case = _case()
    bad = replace(case.clauses[0], level=0)

    with pytest.raises(ValueError) as error:
        dump_privacy_fixture(replace(case, clauses=(bad,)))

    assert _message(error) == "privacy sample: level of 1 is not 1 or more"


def test_top_level_is_not_an_object() -> None:
    with pytest.raises(ValueError, match="privacy sample: top level is not an object"):
        load_privacy_fixture("[]")


def test_document_is_not_an_object() -> None:
    data = cast(dict[str, object], json.loads(dump_privacy_fixture(_case())))
    data["document"] = []

    with pytest.raises(ValueError, match="privacy sample: document has the wrong type"):
        load_privacy_fixture(json.dumps(data))


def test_clauses_is_not_a_list() -> None:
    data = cast(dict[str, object], json.loads(dump_privacy_fixture(_case())))
    data["clauses"] = "x"

    with pytest.raises(ValueError, match="privacy sample: clauses has the wrong type"):
        load_privacy_fixture(json.dumps(data))


def test_clause_id_has_the_wrong_type() -> None:
    data = cast(dict[str, object], json.loads(dump_privacy_fixture(_case())))
    _clause_rows(data)[0]["id"] = 5

    with pytest.raises(ValueError, match="privacy sample: id has the wrong type"):
        load_privacy_fixture(json.dumps(data))


def test_party_yours_has_the_wrong_type() -> None:
    data = cast(dict[str, object], json.loads(dump_privacy_fixture(_case())))
    _party_rows(data)[0]["yours"] = "yes"

    with pytest.raises(ValueError, match="privacy sample: yours has the wrong type"):
        load_privacy_fixture(json.dumps(data))


def test_warning_page_has_the_wrong_type() -> None:
    data = cast(dict[str, object], json.loads(dump_privacy_fixture(_case())))
    document = _document_row(data)
    document["warnings"] = [{"code": "not_english", "page": None}]
    warnings = document["warnings"]
    assert isinstance(warnings, list)
    warning = warnings[0]
    assert isinstance(warning, dict)
    warning["page"] = "1"

    with pytest.raises(ValueError, match="privacy sample: page has the wrong type"):
        load_privacy_fixture(json.dumps(data))


def test_source_kind_is_unknown() -> None:
    data = cast(dict[str, object], json.loads(dump_privacy_fixture(_case())))
    _source_row(data)["kind"] = "bogus"

    with pytest.raises(ValueError, match="privacy sample: kind bogus is not a text kind"):
        load_privacy_fixture(json.dumps(data))
