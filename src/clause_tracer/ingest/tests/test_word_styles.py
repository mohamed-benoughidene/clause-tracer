"""The style cascade of the Word reader (S5-M3-T2)."""

import pytest

from clause_tracer.ingest._word_styles import HIGHLIGHT_COLOURS, RunProps, Styles
from clause_tracer.ingest._xml import W_NS, Element, parse_part


def _styles(inner: str) -> Styles:
    part = f'<w:styles xmlns:w="{W_NS}">{inner}</w:styles>'.encode()
    return Styles.from_xml(parse_part(part))


def _rpr(inner: str) -> Element:
    return parse_part(f'<w:rPr xmlns:w="{W_NS}">{inner}</w:rPr>'.encode())


def _props(
    styles: Styles,
    *,
    paragraph_style: str | None = None,
    run_style: str | None = None,
    rpr: Element | None = None,
) -> RunProps:
    return styles.run_props(paragraph_style=paragraph_style, run_style=run_style, rpr=rpr)


def test_direct_vanish() -> None:
    assert _props(_styles(""), rpr=_rpr("<w:vanish/>")).vanish is True


def test_vanish_val_false() -> None:
    assert _props(_styles(""), rpr=_rpr('<w:vanish w:val="0"/>')).vanish is False


def test_vanish_from_paragraph_style() -> None:
    styles = _styles(
        '<w:style w:type="paragraph" w:styleId="Hidden"><w:rPr><w:vanish/></w:rPr></w:style>'
    )

    assert _props(styles, paragraph_style="Hidden").vanish is True


def test_vanish_from_character_style() -> None:
    styles = _styles(
        '<w:style w:type="character" w:styleId="HiddenRun"><w:rPr><w:vanish/></w:rPr></w:style>'
    )

    assert _props(styles, run_style="HiddenRun").vanish is True


def test_based_on_chain() -> None:
    styles = _styles(
        '<w:style w:type="paragraph" w:styleId="Hidden"><w:rPr><w:vanish/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Based"><w:basedOn w:val="Hidden"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Shown">'
        '<w:basedOn w:val="Hidden"/><w:rPr><w:vanish w:val="0"/></w:rPr></w:style>'
    )

    assert _props(styles, paragraph_style="Based").vanish is True
    assert _props(styles, paragraph_style="Shown").vanish is False


def test_basedon_loop_stops() -> None:
    styles = _styles(
        '<w:style w:styleId="A"><w:basedOn w:val="B"/><w:rPr><w:vanish/></w:rPr></w:style>'
        '<w:style w:styleId="B"><w:basedOn w:val="A"/></w:style>'
    )

    assert _props(styles, paragraph_style="A").vanish is True


def test_doc_defaults() -> None:
    styles = _styles(
        "<w:docDefaults><w:rPrDefault><w:rPr><w:vanish/></w:rPr></w:rPrDefault></w:docDefaults>"
    )

    assert _props(styles).vanish is True


def test_old_values_are_not_read() -> None:
    rpr = _rpr('<w:rPrChange w:id="1" w:author="A"><w:rPr><w:vanish/></w:rPr></w:rPrChange>')

    assert _props(_styles(""), rpr=rpr).vanish is False


def test_color_auto_is_none() -> None:
    assert _props(_styles(""), rpr=_rpr('<w:color w:val="auto"/>')).color is None


def test_size_is_half_points() -> None:
    assert _props(_styles(""), rpr=_rpr('<w:sz w:val="24"/>')).size_half_points == 24


@pytest.mark.parametrize(("name", "value"), sorted(HIGHLIGHT_COLOURS.items()))
def test_highlight_names(name: str, value: str) -> None:
    props = _props(_styles(""), rpr=_rpr(f'<w:highlight w:val="{name}"/>'))

    assert props.highlight == value
