"""Hidden runs, low contrast and tiny print in a Word body (S5-M3-T2)."""

import io
import zipfile

from clause_tracer.core import HiddenReason, HiddenText, Span
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_model import BodyResult
from clause_tracer.ingest._word_styles import Styles
from clause_tracer.ingest._xml import parse_part
from clause_tracer.ingest.tests.builders.word import build_docx, p, r


def _body(body: str, *, styles: str | None = None) -> BodyResult:
    data = build_docx(body, styles=styles)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
        styles_root = parse_part(package.read("word/styles.xml")) if styles is not None else None
    return build_body(root, styles=Styles.from_xml(styles_root))


def _hidden(start: int, end: int, reason: HiddenReason) -> HiddenText:
    return HiddenText(span=Span(start=start, end=end), reason=reason, boxes=())


def _run(text: str, properties: str) -> str:
    return f'<w:r><w:rPr>{properties}</w:rPr><w:t xml:space="preserve">{text}</w:t></w:r>'


def test_hidden_run_is_flagged_and_kept() -> None:
    result = _body(p(r("keep "), r("secret", hidden=True), r(" end")))

    assert result.text == "keep secret end\n"
    assert result.hidden == (_hidden(5, 11, HiddenReason.WORD_HIDDEN_RUN),)


def test_two_touching_hidden_runs_merge() -> None:
    result = _body(p(r("a", hidden=True), r("b", hidden=True)))

    assert result.hidden == (_hidden(0, 2, HiddenReason.WORD_HIDDEN_RUN),)


def test_hidden_by_style() -> None:
    styles = '<w:style w:type="paragraph" w:styleId="Hidden"><w:rPr><w:vanish/></w:rPr></w:style>'

    result = _body(p(r("secret"), style="Hidden"), styles=styles)

    assert result.hidden == (_hidden(0, 6, HiddenReason.WORD_HIDDEN_RUN),)


def test_white_on_white() -> None:
    result = _body(p(r("barely", color="FFFFFF")))

    assert result.hidden == (_hidden(0, 6, HiddenReason.LOW_CONTRAST),)


def test_white_on_dark_fill_is_not_flagged() -> None:
    result = _body(p(r("visible", color="FFFFFF", shading="000080")))

    assert result.hidden == ()


def test_same_colour_as_fill() -> None:
    result = _body(p(r("grey", color="808080", shading="808080")))

    assert result.hidden == (_hidden(0, 4, HiddenReason.LOW_CONTRAST),)


def test_white_on_yellow_highlight_is_not_flagged() -> None:
    result = _body(p(_run("yellow", '<w:color w:val="FFFFFF"/><w:highlight w:val="yellow"/>')))

    assert result.hidden == ()


def test_white_on_white_highlight_is_flagged() -> None:
    result = _body(p(_run("white", '<w:color w:val="FFFFFF"/><w:highlight w:val="white"/>')))

    assert result.hidden == (_hidden(0, 5, HiddenReason.LOW_CONTRAST),)


def test_paragraph_fill_counts() -> None:
    run = _run("black", '<w:color w:val="000000"/>')
    body = f'<w:p><w:pPr><w:shd w:fill="000000"/></w:pPr>{run}</w:p>'

    assert _body(body).hidden == (_hidden(0, 5, HiddenReason.LOW_CONTRAST),)


def test_tiny_run() -> None:
    two = _body(p(r("tiny", size_half_points=2)))
    three = _body(p(r("tiny", size_half_points=3)))
    four = _body(p(r("small", size_half_points=4)))

    assert two.hidden == (_hidden(0, 4, HiddenReason.TINY_FONT),)
    assert three.hidden == (_hidden(0, 4, HiddenReason.TINY_FONT),)
    assert four.hidden == ()


def test_small_print_is_not_flagged() -> None:
    assert _body(p(r("eight", size_half_points=16))).hidden == ()


def test_auto_colour_is_not_flagged() -> None:
    assert _body(p(_run("auto", '<w:color w:val="auto"/>'))).hidden == ()


def test_web_hidden_is_not_flagged() -> None:
    assert _body(p(_run("web", "<w:webHidden/>"))).hidden == ()


def test_space_only_run_is_not_flagged() -> None:
    assert _body(p(r("   ", hidden=True))).hidden == ()


def test_deleted_run_is_not_flagged() -> None:
    deleted = (
        '<w:del w:id="1" w:author="A">'
        "<w:r><w:rPr><w:vanish/></w:rPr><w:t>secret</w:t></w:r></w:del>"
    )

    result = _body(p(deleted, r("kept")))

    assert result.text == "kept\n"
    assert result.hidden == ()


def test_two_reasons_on_one_run() -> None:
    result = _body(p(r("both", hidden=True, color="FFFFFF")))

    assert result.hidden == (
        _hidden(0, 4, HiddenReason.LOW_CONTRAST),
        _hidden(0, 4, HiddenReason.WORD_HIDDEN_RUN),
    )


def test_hidden_paragraph_mark_is_not_flagged() -> None:
    body = f"<w:p><w:pPr><w:rPr><w:vanish/></w:rPr></w:pPr>{r('shown')}</w:p>"

    assert _body(body).hidden == ()


def test_symbol_font_run_sets_symbol_unread() -> None:
    result = _body(p(_run("þ", '<w:rFonts w:ascii="Wingdings"/>')))

    assert result.text == "þ\n"
    assert result.symbol_unread is True


def test_symbol_font_from_a_style() -> None:
    styles = (
        '<w:style w:type="character" w:styleId="SymbolChar">'
        '<w:rPr><w:rFonts w:ascii="Wingdings"/></w:rPr></w:style>'
    )
    body = p('<w:r><w:rPr><w:rStyle w:val="SymbolChar"/></w:rPr><w:t>þ</w:t></w:r>')

    result = _body(body, styles=styles)

    assert result.symbol_unread is True


def test_symbol_font_sym_in_range_sets_it() -> None:
    result = _body(p('<w:r><w:sym w:font="Wingdings" w:char="00FE"/></w:r>'))

    assert result.text == "þ\n"
    assert result.symbol_unread is True


def test_ordinary_font_does_not_warn() -> None:
    result = _body(p(_run("plain", '<w:rFonts w:ascii="Calibri"/>')))

    assert result.symbol_unread is False


def test_near_white_is_a_known_limit() -> None:
    assert _body(p(r("near", color="FEFEFE"))).hidden == ()


_DEFAULT_HIDDEN = (
    '<w:style w:type="paragraph" w:styleId="Normal" w:default="1">'
    '<w:rPr><w:color w:val="FFFFFF"/><w:vanish/></w:rPr></w:style>'
)


def test_default_paragraph_style_hides() -> None:
    result = _body(p(r("Secret term")), styles=_DEFAULT_HIDDEN)

    assert result.hidden == (
        _hidden(0, 11, HiddenReason.LOW_CONTRAST),
        _hidden(0, 11, HiddenReason.WORD_HIDDEN_RUN),
    )


def test_default_character_style_hides() -> None:
    styles = (
        '<w:style w:type="character" w:styleId="NormalChar" w:default="1">'
        "<w:rPr><w:vanish/></w:rPr></w:style>"
    )

    result = _body(p(r("secret")), styles=styles)

    assert result.hidden == (_hidden(0, 6, HiddenReason.WORD_HIDDEN_RUN),)


def test_named_style_does_not_take_the_default() -> None:
    styles = _DEFAULT_HIDDEN + '<w:style w:type="paragraph" w:styleId="Plain"/>'

    result = _body(p(r("shown"), style="Plain"), styles=styles)

    assert result.hidden == ()


def test_style_without_the_default_flag_is_not_applied() -> None:
    styles = '<w:style w:type="paragraph" w:styleId="Normal"><w:rPr><w:vanish/></w:rPr></w:style>'

    result = _body(p(r("shown")), styles=styles)

    assert result.hidden == ()


def test_missing_style_takes_the_default() -> None:
    result = _body(p(r("Secret term"), style="Nope"), styles=_DEFAULT_HIDDEN)

    assert result.hidden == (
        _hidden(0, 11, HiddenReason.LOW_CONTRAST),
        _hidden(0, 11, HiddenReason.WORD_HIDDEN_RUN),
    )
