"""Tracked changes of a Word body (S5-M3-T4)."""

import io
import zipfile

import pytest

from clause_tracer.core import Span, TrackedChange
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_model import BodyResult
from clause_tracer.ingest._xml import parse_part
from clause_tracer.ingest.tests.builders.word import build_docx, delete, ins, p, r


def _body(body: str, *, comments: str | None = None) -> BodyResult:
    data = build_docx(body, comments=comments)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
    return build_body(root)


def _marked_deleted(*runs: str) -> str:
    return f'<w:p><w:pPr><w:rPr><w:del w:id="9" w:author="A"/></w:rPr></w:pPr>{"".join(runs)}</w:p>'


def _move_from(author: str, text: str) -> str:
    return (
        f'<w:moveFrom w:id="1" w:author="{author}" w:date="2026-01-01T00:00:00Z">'
        f'<w:r><w:delText xml:space="preserve">{text}</w:delText></w:r></w:moveFrom>'
    )


def _move_to(author: str, *runs: str) -> str:
    return (
        f'<w:moveTo w:id="2" w:author="{author}" w:date="2026-01-01T00:00:00Z">'
        f"{''.join(runs)}</w:moveTo>"
    )


def test_replacement() -> None:
    body = p(r("due in "), delete("A", "30"), ins("A", r("60")), r(" days"))

    result = _body(body)

    assert result.text == "due in 60 days\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="30", new="60", author="A", span=Span(start=7, end=9)),
    )


def test_insertion_alone() -> None:
    result = _body(p(r("a "), ins("A", r("b"))))

    assert result.text == "a b\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="", new="b", author="A", span=Span(start=2, end=3)),
    )


def test_deletion_alone() -> None:
    result = _body(p(r("a "), delete("A", "b"), r(" c")))

    assert result.text == "a  c\n"
    assert result.tracked_changes == (TrackedChange(earlier="b", new="", author="A", span=None),)


def test_insertion_then_deletion_is_two_changes() -> None:
    result = _body(p(ins("A", r("x")), delete("A", "y")))

    assert result.text == "x\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="", new="x", author="A", span=Span(start=0, end=1)),
        TrackedChange(earlier="y", new="", author="A", span=None),
    )


def test_two_authors_are_two_changes() -> None:
    result = _body(p(delete("A", "x"), ins("B", r("y"))))

    assert result.tracked_changes == (
        TrackedChange(earlier="x", new="", author="A", span=None),
        TrackedChange(earlier="", new="y", author="B", span=Span(start=0, end=1)),
    )


def test_proof_marks_between_do_not_split() -> None:
    proof = '<w:proofErr w:type="spellStart"/>'
    body = p(delete("A", "30"), proof, ins("A", r("60")))

    assert _body(body).tracked_changes == (
        TrackedChange(earlier="30", new="60", author="A", span=Span(start=0, end=2)),
    )


def test_text_between_splits() -> None:
    body = p(delete("A", "x"), r(" and "), ins("A", r("y")))

    assert _body(body).tracked_changes == (
        TrackedChange(earlier="x", new="", author="A", span=None),
        TrackedChange(earlier="", new="y", author="A", span=Span(start=5, end=6)),
    )


def test_no_removed_word_in_text() -> None:
    words = [f"removed{i}" for i in range(10)]

    text = _body(p(*(delete("A", word) for word in words), r("kept"))).text

    assert text == "kept\n"
    assert all(word not in text for word in words)


def test_w_t_inside_del_is_deleted() -> None:
    body = p(
        '<w:del w:id="1" w:author="A"><w:r><w:t>gone</w:t></w:r></w:del>',
        r("kept"),
    )

    result = _body(body)

    assert result.text == "kept\n"
    assert result.tracked_changes == (TrackedChange(earlier="gone", new="", author="A", span=None),)


def test_deleted_paragraph_mark_joins() -> None:
    body = _marked_deleted(r("text.")) + p(r("Clause"))

    assert _body(body).text == "text.Clause\n"


def test_deleted_paragraph_is_gone() -> None:
    body = p(r("a")) + _marked_deleted(delete("A", "b")) + p(r("c"))

    assert _body(body).text == "a\nc\n"


def test_move_is_two_changes() -> None:
    body = p(_move_from("A", "old"), _move_to("A", r("new")))

    result = _body(body)

    assert result.text == "new\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="old", new="", author="A", span=None),
        TrackedChange(earlier="", new="new", author="A", span=Span(start=0, end=3)),
    )


def test_nested_ins_del() -> None:
    body = p(
        '<w:ins w:id="1" w:author="A"><w:r><w:t>new</w:t></w:r>'
        '<w:del w:id="2" w:author="B"><w:r><w:delText>old</w:delText></w:r></w:del>'
        "</w:ins>"
    )

    result = _body(body)

    assert result.text == "new\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="", new="new", author="A", span=Span(start=0, end=3)),
        TrackedChange(earlier="old", new="", author="B", span=None),
    )


_WRAPPERS = {
    "sdt": "<w:sdt><w:sdtPr/><w:sdtContent>{}</w:sdtContent></w:sdt>",
    "hyperlink": '<w:hyperlink r:id="rId9">{}</w:hyperlink>',
    "smartTag": "<w:smartTag>{}</w:smartTag>",
    "customXml": "<w:customXml>{}</w:customXml>",
    "fldSimple": '<w:fldSimple w:instr=" PAGE ">{}</w:fldSimple>',
    "dir": '<w:dir w:val="ltr">{}</w:dir>',
    "unknown": "<w:foo>{}</w:foo>",
}


@pytest.mark.parametrize("wrapper", sorted(_WRAPPERS))
def test_changes_in_each_wrapper(wrapper: str) -> None:
    inner = delete("B", "not ") + ins("B", r("never "))
    body = p(r("We "), _WRAPPERS[wrapper].format(inner), r("pay"))

    result = _body(body)

    assert result.text == "We never pay\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="not ", new="never ", author="B", span=Span(start=3, end=9)),
    )


def test_deletion_inside_a_wrapper_inside_an_insertion_is_listed() -> None:
    inner = '<w:hyperlink r:id="rId9">' + r("a") + delete("B", "b", id=2) + "</w:hyperlink>"
    body = p(ins("A", inner))

    result = _body(body)

    assert result.text == "a\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="", new="a", author="A", span=Span(start=0, end=1)),
        TrackedChange(earlier="b", new="", author="B", span=None),
    )


def test_nested_insertion_in_a_wrapper_is_listed_once() -> None:
    inner = '<w:hyperlink r:id="rId9">' + ins("B", r("x"), id=2) + "</w:hyperlink>"
    body = p(ins("A", inner))

    result = _body(body)

    assert result.text == "x\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="", new="x", author="A", span=Span(start=0, end=1)),
    )


def test_deleted_row_is_dropped_and_listed() -> None:
    row = (
        "<w:tbl><w:tr>"
        '<w:trPr><w:del w:id="1" w:author="A"/></w:trPr>'
        f"<w:tc>{p(r('A'))}</w:tc><w:tc>{p(r('B'))}</w:tc>"
        "</w:tr></w:tbl>"
    )

    result = _body(row + p(r("kept")))

    assert result.text == "kept\n"
    assert result.tracked_changes == (TrackedChange(earlier="A\tB", new="", author="A", span=None),)


def test_inserted_row_is_kept_and_listed() -> None:
    row = (
        "<w:tbl><w:tr>"
        '<w:trPr><w:ins w:id="1" w:author="A"/></w:trPr>'
        f"<w:tc>{p(r('A'))}</w:tc><w:tc>{p(r('B'))}</w:tc>"
        "</w:tr></w:tbl>"
    )

    result = _body(row)

    assert result.text == "A\tB\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="", new="A\tB", author="A", span=Span(start=0, end=3)),
    )


def test_formatting_change_is_not_listed() -> None:
    run = (
        "<w:r><w:rPr><w:b/>"
        '<w:rPrChange w:id="1" w:author="A"><w:rPr/></w:rPrChange>'
        "</w:rPr><w:t>plain</w:t></w:r>"
    )

    result = _body(p(run))

    assert result.text == "plain\n"
    assert result.tracked_changes == ()


def test_missing_author_is_empty_string() -> None:
    body = p('<w:del w:id="1"><w:r><w:delText>gone</w:delText></w:r></w:del>')

    assert _body(body).tracked_changes == (
        TrackedChange(earlier="gone", new="", author="", span=None),
    )


def test_change_in_comment_is_not_listed() -> None:
    comments = f'<w:comment w:id="0" w:author="B">{p(ins("B", r("hidden")))}</w:comment>'

    result = _body(p(ins("A", r("visible"))), comments=comments)

    assert [change.author for change in result.tracked_changes] == ["A"]


def test_changes_in_document_order() -> None:
    body = p(ins("A", r("one"))) + p(ins("B", r("two")))

    assert [change.author for change in _body(body).tracked_changes] == ["A", "B"]


_MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def test_changes_in_alternate_content_are_listed() -> None:
    alternate = (
        f'<mc:AlternateContent xmlns:mc="{_MC_NS}">'
        f'<mc:Choice Requires="wps">{delete("B", "not ")}{ins("B", r("never "))}'
        "</mc:Choice></mc:AlternateContent>"
    )
    body = p(r("We "), alternate, r("pay"))

    result = _body(body)

    assert result.text == "We never pay\n"
    assert result.tracked_changes == (
        TrackedChange(earlier="not ", new="never ", author="B", span=Span(start=3, end=9)),
    )


def test_deletion_held_by_a_run_is_listed() -> None:
    run = (
        '<w:r><w:del w:id="1" w:author="B" w:date="2026-01-01T00:00:00Z">'
        '<w:delText xml:space="preserve">gone</w:delText></w:del>'
        '<w:t xml:space="preserve">kept</w:t></w:r>'
    )

    result = _body(p(run))

    assert result.text == "kept\n"
    assert result.tracked_changes == (TrackedChange(earlier="gone", new="", author="B", span=None),)
