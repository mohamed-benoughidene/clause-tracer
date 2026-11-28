"""Footnotes and endnotes of a Word file (S5-M3-T6)."""

import io
import zipfile

import pytest

from clause_tracer.core import (
    HiddenReason,
    HiddenText,
    SideText,
    SideTextKind,
    UnreadableFileError,
)
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_model import BodyResult
from clause_tracer.ingest._word_side import read_notes
from clause_tracer.ingest._xml import parse_part
from clause_tracer.ingest.tests.builders.word import build_docx, p, r


def _separator(kind: str, note_id: int) -> str:
    return f'<w:{kind} w:type="separator" w:id="{note_id}">{p()}</w:{kind}>'


def _note(kind: str, note_id: int, *paragraphs: str) -> str:
    return f'<w:{kind} w:id="{note_id}">{"".join(paragraphs)}</w:{kind}>'


def _reference(kind: str, note_id: int) -> str:
    return f'<w:r><w:{kind}Reference w:id="{note_id}"/></w:r>'


def _result(
    body: str, *, footnotes: str | None = None, endnotes: str | None = None
) -> tuple[BodyResult, tuple[SideText, ...], tuple[HiddenText, ...]]:
    data = build_docx(body, footnotes=footnotes, endnotes=endnotes)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
        notes_root = (
            parse_part(package.read("word/footnotes.xml")) if footnotes is not None else None
        )
        endnotes_root = (
            parse_part(package.read("word/endnotes.xml")) if endnotes is not None else None
        )
    result = build_body(root)
    side, hidden = read_notes(notes_root, endnotes_root, result.note_refs, None)
    return result, side, hidden


def test_footnote_is_side_text() -> None:
    footnotes = (
        _separator("footnote", -1)
        + _separator("footnote", 0)
        + _note("footnote", 2, p(r("See clause 4")))
    )
    body = p(r("Text"), _reference("footnote", 2))

    result, side, hidden = _result(body, footnotes=footnotes)

    assert result.text == "Text\n"
    assert result.note_refs == ((SideTextKind.FOOTNOTE, "2"),)
    assert side == (SideText(kind=SideTextKind.FOOTNOTE, ref="2", author="", text="See clause 4"),)
    assert hidden == ()


def test_separator_notes_are_skipped() -> None:
    footnotes = _separator("footnote", -1) + _separator("footnote", 0)

    result, side, hidden = _result(p(r("A")), footnotes=footnotes)

    assert result.note_refs == ()
    assert side == ()
    assert hidden == ()


def test_reference_order_beats_file_order() -> None:
    footnotes = _note("footnote", 2, p(r("Two"))) + _note("footnote", 1, p(r("One")))
    body = p(_reference("footnote", 1), _reference("footnote", 2))

    _, side, _ = _result(body, footnotes=footnotes)

    assert [item.text for item in side] == ["One", "Two"]


def test_endnote_kind() -> None:
    endnotes = _note("endnote", 1, p(r("Note")))
    body = p(_reference("endnote", 1))

    result, side, _ = _result(body, endnotes=endnotes)

    assert result.note_refs == ((SideTextKind.ENDNOTE, "1"),)
    assert side[0].kind is SideTextKind.ENDNOTE


def test_unreferenced_note_is_flagged() -> None:
    footnotes = _note("footnote", 3, p(r("Away")))

    _, side, hidden = _result(p(r("A")), footnotes=footnotes)

    assert [item.text for item in side] == ["Away"]
    assert hidden == (HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=()),)


def test_second_reference_to_one_id_counts_once() -> None:
    footnotes = _note("footnote", 2, p(r("Once")))
    body = p(_reference("footnote", 2), _reference("footnote", 2))

    result, side, _ = _result(body, footnotes=footnotes)

    assert result.note_refs == ((SideTextKind.FOOTNOTE, "2"),)
    assert len(side) == 1


def test_reference_in_deleted_text_is_not_a_reference() -> None:
    footnotes = _note("footnote", 2, p(r("Away")))
    deleted = '<w:del w:id="1" w:author="A"><w:r><w:footnoteReference w:id="2"/></w:r></w:del>'

    result, _, hidden = _result(p(deleted), footnotes=footnotes)

    assert result.note_refs == ()
    assert len(hidden) == 1


def test_empty_note_is_not_listed() -> None:
    footnotes = _note("footnote", 2, p())
    body = p(_reference("footnote", 2))

    _, side, hidden = _result(body, footnotes=footnotes)

    assert side == ()
    assert hidden == ()


def test_note_mark_adds_no_text() -> None:
    footnotes = f'<w:footnote w:id="2">{p("<w:r><w:footnoteRef/></w:r>", r("See"))}</w:footnote>'
    body = p(_reference("footnote", 2))

    _, side, _ = _result(body, footnotes=footnotes)

    assert side[0].text == "See"


def test_alt_chunk_in_a_note_raises() -> None:
    footnotes = '<w:footnote w:id="2">' + p('<w:altChunk r:id="rId9"/>') + "</w:footnote>"
    body = p(_reference("footnote", 2))

    with pytest.raises(UnreadableFileError) as raised:
        _result(body, footnotes=footnotes)

    assert raised.value.context["reason"] == "word_alt_chunk"


def test_short_note_cannot_become_a_clause() -> None:
    footnotes = _note("footnote", 2, p(r("4 Fees cap")))
    body = p(r("Body"), _reference("footnote", 2))

    result, side, _ = _result(body, footnotes=footnotes)

    assert side[0].text == "4 Fees cap"
    assert "Fees" not in result.text


def test_no_notes_parts() -> None:
    assert read_notes(None, None, (), None) == ((), ())
