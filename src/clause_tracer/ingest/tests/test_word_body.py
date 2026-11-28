"""The body walk of the Word reader (S5-M3-T1)."""

import io
import time
import zipfile

import pytest

from clause_tracer.core import HiddenReason, HiddenText, InputTooLargeError, UnreadableFileError
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_model import BodyResult
from clause_tracer.ingest._xml import parse_part
from clause_tracer.ingest.tests.builders.word import br, build_docx, p, r, tab, tbl

_MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
_WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"


def _body(body: str) -> BodyResult:
    data = build_docx(body)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
    return build_body(root)


def _reason(error: UnreadableFileError) -> str:
    return str(error.context["reason"])


def _text_box(text: str) -> str:
    return (
        f'<w:drawing><wps:txbx xmlns:wps="{_WPS_NS}">'
        f"<w:txbxContent>{p(r(text))}</w:txbxContent>"
        "</wps:txbx></w:drawing>"
    )


def _alternate(*, choice: str, fallback: str) -> str:
    return (
        f'<mc:AlternateContent xmlns:mc="{_MC_NS}" xmlns:wps="{_WPS_NS}">'
        f'<mc:Choice Requires="wps">{choice}</mc:Choice>'
        f"<mc:Fallback>{fallback}</mc:Fallback>"
        "</mc:AlternateContent>"
    )


def _field_char(kind: str) -> str:
    return f'<w:r><w:fldChar w:fldCharType="{kind}"/></w:r>'


def test_two_paragraphs() -> None:
    assert _body(p(r("Hello")) + p(r("World"))).text == "Hello\nWorld\n"


def test_runs_join() -> None:
    assert _body(p(r("He"), r("llo"))).text == "Hello\n"


def test_space_is_kept() -> None:
    assert _body(p(r("a "), r(" b"))).text == "a  b\n"


def test_tab_and_break() -> None:
    assert _body(p(r("a"), tab(), r("b"), br(), r("c"))).text == "a\tb\nc\n"


def test_empty_paragraph() -> None:
    assert _body(p(r("a")) + p() + p(r("b"))).text == "a\n\nb\n"


def test_table_row_is_one_line() -> None:
    assert _body(tbl((r("A"), r("B")), (r("C"), r("D")))).text == "A\tB\nC\tD\n"


def test_cell_with_two_paragraphs() -> None:
    body = f"<w:tbl><w:tr><w:tc>{p(r('x'))}{p(r('y'))}</w:tc></w:tr></w:tbl>"

    assert _body(body).text == "x y\n"


def test_nested_table_is_flattened() -> None:
    body = f"<w:tbl><w:tr><w:tc>{tbl((r('A'), r('B')), (r('C'), r('D')))}</w:tc></w:tr></w:tbl>"

    assert _body(body).text == "A\tB C\tD\n"


def test_merged_cells_are_one_cell() -> None:
    body = (
        "<w:tbl>"
        f'<w:tr><w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr>{p(r("A"))}</w:tc>'
        f"<w:tc>{p(r('B'))}</w:tc></w:tr>"
        f"<w:tr><w:tc><w:tcPr><w:vMerge/></w:tcPr>{p()}</w:tc>"
        f"<w:tc>{p(r('D'))}</w:tc></w:tr>"
        "</w:tbl>"
    )

    assert _body(body).text == "A\tB\n\tD\n"


def test_content_control_is_read() -> None:
    block = f"<w:sdt><w:sdtPr/><w:sdtContent>{p(r('Body'))}</w:sdtContent></w:sdt>"
    run = "<w:sdt><w:sdtPr/><w:sdtContent><w:r><w:t>Text</w:t></w:r></w:sdtContent></w:sdt>"

    assert _body(block + p(run)).text == "Body\nText\n"


def test_hyperlink_and_simple_field() -> None:
    link = '<w:hyperlink r:id="rId9"><w:r><w:t>Link</w:t></w:r></w:hyperlink>'
    simple = '<w:fldSimple w:instr=" PAGE "><w:r><w:t>Result</w:t></w:r></w:fldSimple>'
    instruction = "<w:r><w:instrText> PAGE </w:instrText></w:r>"

    assert _body(p(link, simple, instruction, r("!"))).text == "LinkResult!\n"


def test_complex_field_result_only() -> None:
    body = p(
        _field_char("begin"),
        "<w:r><w:instrText> PAGE </w:instrText></w:r>",
        _field_char("separate"),
        r("3"),
        _field_char("end"),
    )

    assert _body(body).text == "3\n"


def test_symbols() -> None:
    in_range = _body(p('<w:r><w:sym w:char="00A9"/></w:r>'))
    private = _body(p('<w:r><w:sym w:char="F0FC"/></w:r>'))

    assert in_range.text == "©\n"
    assert in_range.symbol_unread is False
    assert private.text == "\n"
    assert private.symbol_unread is True


def test_deleted_symbol_does_not_warn() -> None:
    deleted = (
        '<w:del w:id="1" w:author="A"><w:r><w:sym w:font="Wingdings" w:char="F0FC"/></w:r></w:del>'
    )

    result = _body(p(deleted, r("kept")))

    assert result.text == "kept\n"
    assert result.symbol_unread is False


def test_hyphens() -> None:
    assert _body(p("<w:r><w:noBreakHyphen/><w:softHyphen/></w:r>")).text == "‑\n"


def test_alternate_content_is_read_once() -> None:
    body = p(
        r("Host"),
        f"<w:r>{_alternate(choice=_text_box('Box'), fallback=_text_box('Box'))}</w:r>",
    )

    assert _body(body).text == "Host\nBox\n"


def test_alternate_content_difference_is_flagged() -> None:
    body = p(
        r("Host"),
        f"<w:r>{_alternate(choice=_text_box('Box'), fallback=_text_box('Other'))}</w:r>",
    )

    result = _body(body)

    assert result.text == "Host\nBox\n"
    assert result.hidden == (
        HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=()),
    )


def test_text_box_follows_its_paragraph() -> None:
    body = p(r("Before"), _text_box("Box")) + p(r("After"))

    assert _body(body).text == "Before\nBox\nAfter\n"


def test_alt_chunk_raises() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        _body('<w:altChunk r:id="rId9"/>')

    assert _reason(raised.value) == "word_alt_chunk"


def test_deleted_alt_chunk_is_read_normally() -> None:
    deleted_row = (
        "<w:tbl><w:tr>"
        '<w:trPr><w:del w:id="1" w:author="A"/></w:trPr>'
        '<w:tc><w:altChunk r:id="rId9"/></w:tc>'
        "</w:tr></w:tbl>"
    )
    alternate = _alternate(choice=p(r("Shown")), fallback='<w:altChunk r:id="rId9"/>')

    result = _body(deleted_row + p(r("Kept")) + alternate)

    assert result.text == "Kept\nShown\n"


def test_unknown_element_is_not_read_as_text() -> None:
    body = p(r("A")) + "<w:foo><w:bar>not text</w:bar></w:foo>"

    assert _body(body).text == "A\n"


def test_word_limit_stops_early() -> None:
    body = p(r("word")) * 50_001

    start = time.monotonic()
    with pytest.raises(InputTooLargeError) as raised:
        _body(body)
    elapsed = time.monotonic() - start

    assert raised.value.context["limit_words"] == 50_000
    assert elapsed < 5
