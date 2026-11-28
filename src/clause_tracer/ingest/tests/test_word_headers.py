"""Headers and footers of a Word file (S5-M3-T6)."""

import io
import zipfile
from collections.abc import Mapping

from clause_tracer.core import HiddenReason, HiddenText, SideText, SideTextKind
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_model import BodyResult, SectionRefs
from clause_tracer.ingest._word_side import read_headers_and_footers
from clause_tracer.ingest._xml import parse_part
from clause_tracer.ingest._zip import open_package
from clause_tracer.ingest.tests.builders.word import build_docx, p, r


def _reference(kind: str, ref_type: str, rel_id: str) -> str:
    return f'<w:{kind}Reference w:type="{ref_type}" r:id="{rel_id}"/>'


def _section(*parts: str, title: bool = False) -> str:
    title_element = "<w:titlePg/>" if title else ""
    return f"<w:sectPr>{''.join(parts)}{title_element}</w:sectPr>"


def _read(
    body: str,
    *,
    headers: Mapping[str, str] | None = None,
    footers: Mapping[str, str] | None = None,
    rels: Mapping[str, str] | None = None,
    even_and_odd: bool = False,
) -> tuple[BodyResult, tuple[SideText, ...], tuple[HiddenText, ...]]:
    data = build_docx(body, headers=headers, footers=footers)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
    result = build_body(root)
    word_package = open_package(data)
    side, hidden = read_headers_and_footers(
        word_package, rels or {}, result.sections, even_and_odd, None
    )
    return result, side, hidden


def test_default_header_is_listed() -> None:
    body = p(r("A")) + _section(_reference("header", "default", "rId1"))

    _, side, hidden = _read(
        body,
        headers={"header1.xml": p(r("Head"))},
        rels={"rId1": "word/header1.xml"},
    )

    assert side == (
        SideText(kind=SideTextKind.HEADER, ref="word/header1.xml", author="", text="Head"),
    )
    assert hidden == ()


def test_first_header_needs_title_page() -> None:
    body = p(r("A")) + _section(_reference("header", "first", "rId1"))
    with_title = p(r("A")) + _section(_reference("header", "first", "rId1"), title=True)

    _, _, hidden_without = _read(
        body, headers={"header1.xml": p(r("Head"))}, rels={"rId1": "word/header1.xml"}
    )
    _, _, hidden_with = _read(
        with_title, headers={"header1.xml": p(r("Head"))}, rels={"rId1": "word/header1.xml"}
    )

    assert hidden_without == (
        HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=()),
    )
    assert hidden_with == ()


def test_even_header_needs_even_and_odd() -> None:
    body = p(r("A")) + _section(_reference("header", "even", "rId1"))

    _, _, hidden_without = _read(
        body, headers={"header1.xml": p(r("Head"))}, rels={"rId1": "word/header1.xml"}
    )
    _, side_with, hidden_with = _read(
        body,
        headers={"header1.xml": p(r("Head"))},
        rels={"rId1": "word/header1.xml"},
        even_and_odd=True,
    )

    assert hidden_without
    assert hidden_with == ()
    assert side_with[0].text == "Head"


def test_unreferenced_header_is_flagged() -> None:
    _, side, hidden = _read(
        p(r("A")), headers={"header1.xml": p(r("Head"))}, rels={"rId1": "word/header1.xml"}
    )

    assert [item.text for item in side] == ["Head"]
    assert hidden == (HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=()),)


def test_equal_headers_are_listed_once() -> None:
    first = _section(_reference("header", "default", "rId1"))
    body = p(r("A")) + f"<w:p><w:pPr>{first}</w:pPr></w:p>"
    body += _section(_reference("header", "default", "rId2"))

    _, side, _ = _read(
        body,
        headers={"header1.xml": p(r("Same")), "header2.xml": p(r("Same"))},
        rels={"rId1": "word/header1.xml", "rId2": "word/header2.xml"},
    )

    assert [item.text for item in side] == ["Same"]


def test_footer_kind() -> None:
    body = p(r("A")) + _section(_reference("footer", "default", "rId1"))

    _, side, _ = _read(
        body,
        footers={"footer1.xml": p(r("Foot"))},
        rels={"rId1": "word/footer1.xml"},
    )

    assert side[0].kind is SideTextKind.FOOTER
    assert side[0].ref == "word/footer1.xml"


def _page_field(result: str | None) -> str:
    parts = (
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        "<w:r><w:instrText> PAGE </w:instrText></w:r>"
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    )
    if result is not None:
        parts += r(result)
    return parts + '<w:r><w:fldChar w:fldCharType="end"/></w:r>'


def test_page_field_gives_no_text_and_no_entry() -> None:
    body = p(r("A")) + _section(_reference("footer", "default", "rId1"))

    _, side, _ = _read(
        body,
        footers={"footer1.xml": p(_page_field("3"))},
        rels={"rId1": "word/footer1.xml"},
    )
    _, empty, _ = _read(
        body,
        footers={"footer1.xml": p(_page_field(None))},
        rels={"rId1": "word/footer1.xml"},
    )

    assert side[0].text == "3"
    assert empty == ()


def test_header_text_is_not_in_the_body() -> None:
    body = p(r("Body")) + _section(_reference("header", "default", "rId1"))

    result, _, _ = _read(
        body, headers={"header1.xml": p(r("Head"))}, rels={"rId1": "word/header1.xml"}
    )

    assert result.text == "Body\n"


def test_inherited_section_adds_no_part() -> None:
    body = p(r("A")) + _section(_reference("header", "default", "rId1")) + _section()

    _, side, _ = _read(
        body, headers={"header1.xml": p(r("Head"))}, rels={"rId1": "word/header1.xml"}
    )

    assert [item.text for item in side] == ["Head"]


def test_missing_relationship_target_is_ignored() -> None:
    body = p(r("A")) + _section(_reference("header", "default", "rId9"))

    _, side, hidden = _read(body, rels={})

    assert side == ()
    assert hidden == ()


def test_hidden_run_in_header_is_flagged_once() -> None:
    body = p(r("A")) + _section(_reference("header", "default", "rId1"))

    _, _, hidden = _read(
        body,
        headers={"header1.xml": p(r("secret", hidden=True))},
        rels={"rId1": "word/header1.xml"},
    )

    assert hidden == (HiddenText(span=None, reason=HiddenReason.WORD_HIDDEN_RUN, boxes=()),)


def test_sections_are_read_in_document_order() -> None:
    first = f"<w:p><w:pPr>{_section(_reference('header', 'default', 'rId1'))}</w:pPr></w:p>"
    body = p(r("A")) + first + _section(_reference("footer", "default", "rId2"))

    result = _body(body)

    assert result.sections == (
        SectionRefs(headers=(("default", "rId1"),), footers=(), title_page=False),
        SectionRefs(headers=(), footers=(("default", "rId2"),), title_page=False),
    )


def _body(body: str) -> BodyResult:
    data = build_docx(body)
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        root = parse_part(package.read("word/document.xml"))
    return build_body(root)
