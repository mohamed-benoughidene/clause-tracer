"""The list numbers of a Word body (S5-M3-T3)."""

import io
import time
import zipfile
from typing import Final

from clause_tracer.core import Span
from clause_tracer.ingest import (
    WARNING_WORD_SYMBOL_UNREAD,
    read_pasted_text,
    read_word_file,
    split_clauses,
)
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_model import BodyResult
from clause_tracer.ingest._word_numbering import Label, Numbering
from clause_tracer.ingest._word_styles import Styles
from clause_tracer.ingest._xml import W_NS, parse_part
from clause_tracer.ingest.tests.builders.word import build_docx, p, r

_NS: Final[str] = f'xmlns:w="{W_NS}"'


def _level(
    ilvl: int = 0,
    *,
    start: int = 1,
    fmt: str = "decimal",
    text: str = "%1.",
    restart: int | None = None,
    is_lgl: bool = False,
    pstyle: str | None = None,
    suff: str | None = None,
) -> str:
    parts = [
        f'<w:start w:val="{start}"/>',
        f'<w:numFmt w:val="{fmt}"/>',
        f'<w:lvlText w:val="{text}"/>',
    ]
    if restart is not None:
        parts.append(f'<w:lvlRestart w:val="{restart}"/>')
    if is_lgl:
        parts.append("<w:isLgl/>")
    if pstyle is not None:
        parts.append(f'<w:pStyle w:val="{pstyle}"/>')
    if suff is not None:
        parts.append(f'<w:suff w:val="{suff}"/>')
    return f'<w:lvl w:ilvl="{ilvl}">{"".join(parts)}</w:lvl>'


def _num(num_id: int, abstract_id: str = "0", *, overrides: str = "") -> str:
    return f'<w:num w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/>{overrides}</w:num>'


def numbering_xml(
    levels: list[str], nums: list[str], *, abstract_id: str = "0", link: str | None = None
) -> str:
    link_element = f'<w:numStyleLink w:val="{link}"/>' if link is not None else ""
    abstract = (
        f'<w:abstractNum w:abstractNumId="{abstract_id}">'
        f"{link_element}{''.join(levels)}</w:abstractNum>"
    )
    return abstract + "".join(nums)


def _numbering(numbering: str = "", styles: str | None = None) -> Numbering:
    styles_root = (
        parse_part(f"<w:styles {_NS}>{styles}</w:styles>".encode()) if styles is not None else None
    )
    root = parse_part(f"<w:numbering {_NS}>{numbering}</w:numbering>".encode())
    return Numbering.from_xml(root, Styles.from_xml(styles_root))


def _result(body: str, numbering: str = "", *, styles: str | None = None) -> BodyResult:
    data = build_docx(body, numbering=numbering, styles=styles)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
        numbering_root = parse_part(package.read("word/numbering.xml"))
        styles_root = parse_part(package.read("word/styles.xml")) if styles is not None else None
    styles_object = Styles.from_xml(styles_root)
    return build_body(
        root,
        styles=styles_object,
        numbering=Numbering.from_xml(numbering_root, styles_object),
    )


def test_decimal() -> None:
    numbering = numbering_xml([_level()], [_num(1)])
    body = p(r("A"), num=(1, 0)) + p(r("B"), num=(1, 0)) + p(r("C"), num=(1, 0))

    assert _result(body, numbering).text == "1. A\n2. B\n3. C\n"


def test_multilevel() -> None:
    numbering = numbering_xml([_level(0, text="%1."), _level(1, text="%1.%2")], [_num(1)])
    body = (
        p(r("A"), num=(1, 0))
        + p(r("B"), num=(1, 1))
        + p(r("C"), num=(1, 1))
        + p(r("D"), num=(1, 0))
        + p(r("E"), num=(1, 1))
    )

    assert _result(body, numbering).text == "1. A\n1.1 B\n1.2 C\n2. D\n2.1 E\n"


def test_letters_past_26() -> None:
    numbering = _numbering(numbering_xml([_level(fmt="lowerLetter", text="%1.")], [_num(1)]))

    labels = [numbering.label(num_id="1", ilvl=0).text for _ in range(28)]

    assert labels[0] == "a."
    assert labels[25] == "z."
    assert labels[26] == "aa."
    assert labels[27] == "bb."


def test_roman() -> None:
    upper = _numbering(numbering_xml([_level(fmt="upperRoman", text="%1.")], [_num(1)]))
    lower = _numbering(numbering_xml([_level(fmt="lowerRoman", text="%1.")], [_num(1)]))

    assert [upper.label(num_id="1", ilvl=0).text for _ in range(4)] == ["I.", "II.", "III.", "IV."]
    assert [lower.label(num_id="1", ilvl=0).text for _ in range(4)] == ["i.", "ii.", "iii.", "iv."]


def test_decimal_zero() -> None:
    numbering = _numbering(numbering_xml([_level(fmt="decimalZero", text="%1")], [_num(1)]))

    labels = [numbering.label(num_id="1", ilvl=0) for _ in range(10)]

    assert labels[0].text == "01"
    assert labels[8].text == "09"
    assert labels[9].text == "10"


def test_bullet_gives_no_number() -> None:
    numbering = _numbering(numbering_xml([_level(fmt="bullet", text="•")], [_num(1)]))

    label = numbering.label(num_id="1", ilvl=0)

    assert label == Label(text=None)
    assert label.unknown is False


def test_none_format() -> None:
    numbering = _numbering(numbering_xml([_level(fmt="none", text="")], [_num(1)]))

    assert numbering.label(num_id="1", ilvl=0) == Label(text=None)


def test_num_id_zero_is_no_list() -> None:
    numbering = numbering_xml([_level()], [_num(1)])

    assert _result(p(r("A"), num=(0, 0)), numbering).text == "A\n"


def test_suffix_is_always_one_space() -> None:
    for suff in ("tab", "space", "nothing"):
        numbering = numbering_xml([_level(suff=suff)], [_num(1)])

        assert _result(p(r("A"), num=(1, 0)), numbering).text == "1. A\n", suff


def test_start_override() -> None:
    override = '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="5"/></w:lvlOverride>'
    numbering = numbering_xml([_level()], [_num(1, overrides=override)])

    assert _result(p(r("A"), num=(1, 0)), numbering).text == "5. A\n"


def test_lvl_override() -> None:
    override = (
        '<w:lvlOverride w:ilvl="0"><w:lvl w:ilvl="0">'
        '<w:start w:val="1"/><w:numFmt w:val="upperLetter"/>'
        '<w:lvlText w:val="%1)"/></w:lvl></w:lvlOverride>'
    )
    numbering = numbering_xml([_level()], [_num(1, overrides=override)])

    assert _result(p(r("A"), num=(1, 0)), numbering).text == "A) A\n"


def test_continues_across_two_nums_of_one_abstract() -> None:
    numbering = numbering_xml([_level()], [_num(1), _num(2)])
    body = p(r("A"), num=(1, 0)) + p(r("B"), num=(1, 0)) + p(r("C"), num=(2, 0))

    assert _result(body, numbering).text == "1. A\n2. B\n3. C\n"


def test_start_override_restarts() -> None:
    override = '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride>'
    numbering = numbering_xml([_level()], [_num(1), _num(2, overrides=override)])
    body = p(r("A"), num=(1, 0)) + p(r("B"), num=(1, 0)) + p(r("C"), num=(2, 0))

    assert _result(body, numbering).text == "1. A\n2. B\n1. C\n"


def test_lvl_restart_zero_never_restarts() -> None:
    numbering = numbering_xml(
        [_level(0, text="%1."), _level(1, text="%1.%2", restart=0)], [_num(1)]
    )
    body = p(r("A"), num=(1, 1)) + p(r("B"), num=(1, 0)) + p(r("C"), num=(1, 1))

    assert _result(body, numbering).text == "1.1 A\n1. B\n1.2 C\n"


def test_is_lgl() -> None:
    numbering = numbering_xml(
        [
            _level(0, fmt="upperRoman", text="%1."),
            _level(1, text="%1.%2"),
            _level(2, text="%1.%2.%3", is_lgl=True),
        ],
        [_num(1)],
    )
    body = p(r("A"), num=(1, 0)) + p(r("B"), num=(1, 1)) + p(r("C"), num=(1, 2))

    assert _result(body, numbering).text == "I. A\nI.1 B\n1.1.1 C\n"


def test_style_numbering() -> None:
    styles = (
        '<w:style w:type="paragraph" w:styleId="Numbered">'
        '<w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr></w:style>'
    )
    numbering = numbering_xml([_level(pstyle="Numbered")], [_num(1)])

    assert _result(p(r("A"), style="Numbered"), numbering, styles=styles).text == "1. A\n"


def test_num_style_link() -> None:
    styles = (
        '<w:style w:type="paragraph" w:styleId="ListStyle">'
        '<w:pPr><w:numPr><w:numId w:val="2"/></w:numPr></w:pPr></w:style>'
    )
    linked = numbering_xml([_level()], [_num(2, "1")], abstract_id="1")
    numbering = numbering_xml([], [_num(1)], link="ListStyle") + linked

    assert _result(p(r("A"), num=(1, 0)), numbering, styles=styles).text == "1. A\n"


def test_num_style_link_loop_is_unknown() -> None:
    styles = (
        '<w:style w:type="paragraph" w:styleId="Loop">'
        '<w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr></w:style>'
    )
    numbering = numbering_xml([], [_num(1)], link="Loop")

    result = _result(p(r("A"), num=(1, 0)), numbering, styles=styles)

    assert result.text == "A\n"
    assert result.numbering_unknown is True


def test_unknown_format_gives_no_number_and_counts_on() -> None:
    ordinal = numbering_xml([_level(fmt="ordinal")], [_num(1)])
    decimal = numbering_xml([_level()], [_num(2, "1")], abstract_id="1")
    body = p(r("A"), num=(1, 0)) + p(r("B"), num=(2, 0)) + p(r("C"), num=(2, 0))

    result = _result(body, ordinal + decimal)

    assert result.text == "A\n1. B\n2. C\n"
    assert result.numbering_unknown is True


def test_missing_num_is_no_list() -> None:
    numbering = numbering_xml([_level()], [_num(1)])

    result = _result(p(r("A"), num=(9, 0)), numbering)

    assert result.text == "A\n"
    assert result.numbering_unknown is False


def test_huge_level_is_unknown() -> None:
    numbering = numbering_xml([_level()], [_num(1)])

    result = _result(p(r("A"), num=(1, 9)), numbering)

    assert result.text == "A\n"
    assert result.numbering_unknown is True


def test_huge_lvl_text_is_unknown() -> None:
    numbering = numbering_xml([_level(text="x" * 201)], [_num(1)])

    result = _result(p(r("A"), num=(1, 0)), numbering)

    assert result.text == "A\n"
    assert result.numbering_unknown is True


def test_deleted_paragraph_does_not_count() -> None:
    numbering = numbering_xml([_level()], [_num(1)])
    deleted = (
        '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
        '<w:rPr><w:del w:id="1" w:author="A"/></w:rPr></w:pPr>'
        '<w:del w:id="2" w:author="A"><w:r><w:delText>B</w:delText></w:r></w:del></w:p>'
    )
    body = p(r("A"), num=(1, 0)) + deleted + p(r("C"), num=(1, 0))

    assert _result(body, numbering).text == "1. A\n2. C\n"


def test_typed_number_stays() -> None:
    numbering = numbering_xml([_level()], [_num(1)])

    assert _result(p(r("1.1 Fees"), num=(1, 0)), numbering).text == "1. 1.1 Fees\n"


def _multilevel() -> str:
    return numbering_xml([_level(0, text="%1."), _level(1, text="%1.%2")], [_num(1)])


def test_number_in_a_table_cell() -> None:
    cell = f"<w:tbl><w:tr><w:tc>{p(r('In cell'), num=(1, 0))}</w:tc></w:tr></w:tbl>"
    body = p(r("One"), num=(1, 0)) + cell + p(r("Three"), num=(1, 0))

    assert _result(body, _multilevel()).text == "1. One\n2. In cell\n3. Three\n"


def test_numbers_in_two_cells() -> None:
    row = (
        "<w:tbl><w:tr>"
        f"<w:tc>{p(r('A'), num=(1, 0))}</w:tc>"
        f"<w:tc>{p(r('B'), num=(1, 0))}</w:tc>"
        "</w:tr></w:tbl>"
    )

    assert _result(row, _multilevel()).text == "1. A\t2. B\n"


def test_number_in_an_inserted_row_is_outside_the_change() -> None:
    row = (
        "<w:tbl><w:tr>"
        '<w:trPr><w:ins w:id="1" w:author="A"/></w:trPr>'
        f"<w:tc>{p(r('x'), num=(1, 0))}</w:tc>"
        "</w:tr></w:tbl>"
    )

    result = _result(row, _multilevel())

    assert result.text == "1. x\n"
    assert result.tracked_changes[0].new == "x"
    assert result.tracked_changes[0].span == Span(start=3, end=4)


def test_own_level_with_the_list_of_the_style() -> None:
    styles = (
        '<w:style w:type="paragraph" w:styleId="L1">'
        '<w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr></w:style>'
    )
    sub = (
        '<w:p><w:pPr><w:pStyle w:val="L1"/>'
        '<w:numPr><w:ilvl w:val="1"/></w:numPr></w:pPr>'
        f"{r('Sub')}</w:p>"
    )
    body = p(r("Top"), style="L1") + sub

    assert _result(body, _multilevel(), styles=styles).text == "1. Top\n1.1 Sub\n"


def test_child_style_sets_only_the_level() -> None:
    styles = (
        '<w:style w:type="paragraph" w:styleId="L1">'
        '<w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="L2"><w:basedOn w:val="L1"/>'
        '<w:pPr><w:numPr><w:ilvl w:val="1"/></w:numPr></w:pPr></w:style>'
    )
    body = p(r("Top"), style="L1") + p(r("Sub"), style="L2")

    assert _result(body, _multilevel(), styles=styles).text == "1. Top\n1.1 Sub\n"


def test_negative_level_is_unknown_and_fast() -> None:
    start = time.monotonic()

    result = _result(p(r("A"), num=(1, -40_000_000)), _multilevel())

    elapsed = time.monotonic() - start

    assert result.text == "A\n"
    assert result.numbering_unknown is True
    assert elapsed < 1


def test_start_over_the_bound_is_one() -> None:
    numbering = numbering_xml([_level(fmt="lowerLetter", start=26_000_000)], [_num(1)])

    assert _result(p(r("A"), num=(1, 0)), numbering).text == "a. A\n"


def test_letter_over_the_bound_is_unknown() -> None:
    over = numbering_xml([_level(fmt="lowerLetter", start=781)], [_num(1)])
    at = numbering_xml([_level(fmt="lowerLetter", start=780)], [_num(1)])

    result = _result(p(r("A"), num=(1, 0)), over)

    assert result.text == "A\n"
    assert result.numbering_unknown is True
    assert _result(p(r("A"), num=(1, 0)), at).text == "z" * 30 + ". A\n"


def test_values_that_are_not_numbers_raise_nothing() -> None:
    bad_start = (
        '<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0">'
        '<w:start w:val="x"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/>'
        "</w:lvl></w:abstractNum>" + _num(1)
    )
    bad_level = (
        '<w:abstractNum w:abstractNumId="0">'
        '<w:lvl w:ilvl="x"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
        '<w:lvlText w:val="%1."/></w:lvl>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
        '<w:lvlText w:val="%1."/></w:lvl>'
        "</w:abstractNum>" + _num(1)
    )
    bad_override = numbering_xml(
        [_level()],
        [
            _num(
                1,
                overrides=(
                    '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="x"/></w:lvlOverride>'
                ),
            )
        ],
    )
    bad_restart = (
        '<w:abstractNum w:abstractNumId="0">'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
        '<w:lvlText w:val="%1."/></w:lvl>'
        '<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
        '<w:lvlText w:val="%1.%2"/><w:lvlRestart w:val="x"/></w:lvl>'
        "</w:abstractNum>" + _num(1)
    )

    for numbering in (bad_start, bad_level, bad_override, bad_restart):
        document = read_word_file(
            build_docx(p(r("A"), num=(1, 0)), numbering=numbering), name="t.docx"
        )
        assert document.text == "1. A\n", numbering

    symbol = read_word_file(build_docx(p(r("A"), '<w:r><w:sym w:char="zz"/></w:r>')), name="t.docx")

    assert [warning.code for warning in symbol.warnings] == [WARNING_WORD_SYMBOL_UNREAD]


def _clause_numbers(text: str) -> list[str | None]:
    return [clause.number for clause in split_clauses(read_pasted_text(text))]


def test_known_splitter_limits() -> None:
    first = numbering_xml([_level(fmt="decimal", text="%1)")], [_num(1)])
    second = numbering_xml([_level(fmt="upperLetter", text="%1.")], [_num(2, "1")], abstract_id="1")
    third = numbering_xml([_level(fmt="upperRoman", text="%1.")], [_num(3, "2")], abstract_id="2")
    fourth = numbering_xml([_level(fmt="decimalZero", text="%1.")], [_num(4, "3")], abstract_id="3")
    numbering = first + second + third + fourth
    body = (
        p(r("A"), num=(1, 0))
        + p(r("B"), num=(2, 0))
        + p(r("C"), num=(3, 0))
        + p(r("D"), num=(4, 0))
    )

    text = _result(body, numbering).text

    assert text == "1) A\nA. B\nI. C\n01. D\n"
    assert set(_clause_numbers("1) A\n2) B\n")) == {None}
    assert set(_clause_numbers("A. C\nB. D\n")) == {None}
    assert set(_clause_numbers("I. E\nII. F\n")) == {None}
    clauses = split_clauses(read_pasted_text("01. G\n02. H\n"))
    assert [clause.number for clause in clauses] == ["01", "02"]
    assert [clause.id for clause in clauses] == ["1", "2"]
