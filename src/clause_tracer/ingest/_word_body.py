"""The body walk of the Word reader (S5-M3-T1, S5-M3-T2).

The walk reads `word/document.xml` as Word draws it: the accepted view of
the tracked changes, the cached result of a field, a table row as one line
and a text box after the paragraph that holds it. Content that Word does
not show is never read, and nothing is removed from the text it does show
(D1). A hidden run, low contrast and tiny print are flagged with a span
over their words.
"""

from dataclasses import replace
from typing import Final, Literal

from clause_tracer.core import (
    HiddenReason,
    HiddenText,
    InputTooLargeError,
    SideTextKind,
    Span,
    TrackedChange,
    UnreadableFileError,
)
from clause_tracer.ingest._thresholds import WORD_TINY_HALF_POINTS
from clause_tracer.ingest._word_model import BodyResult, Mark, SectionRefs, Text
from clause_tracer.ingest._word_numbering import Numbering
from clause_tracer.ingest._word_styles import RunProps, Styles
from clause_tracer.ingest._xml import W_NS, Element, qname
from clause_tracer.ingest.limits import MAX_WORDS

_MC_NS: Final[str] = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _tag(local: str) -> str:
    return qname(W_NS, local)


_BODY: Final[str] = _tag("body")
_P: Final[str] = _tag("p")
_PPR: Final[str] = _tag("pPr")
_NUMPR: Final[str] = _tag("numPr")
_NUMID: Final[str] = _tag("numId")
_ILVL: Final[str] = _tag("ilvl")
_VAL: Final[str] = qname(W_NS, "val")
_R: Final[str] = _tag("r")
_RPR: Final[str] = _tag("rPr")
_RSTYLE: Final[str] = _tag("rStyle")
_PSTYLE: Final[str] = _tag("pStyle")
_T: Final[str] = _tag("t")
_TAB: Final[str] = _tag("tab")
_PTAB: Final[str] = _tag("ptab")
_BR: Final[str] = _tag("br")
_CR: Final[str] = _tag("cr")
_NO_BREAK_HYPHEN: Final[str] = _tag("noBreakHyphen")
_SOFT_HYPHEN: Final[str] = _tag("softHyphen")
_SYM: Final[str] = _tag("sym")
_DEL: Final[str] = _tag("del")
_DEL_TEXT: Final[str] = _tag("delText")
_DEL_INSTR_TEXT: Final[str] = _tag("delInstrText")
_INSTR_TEXT: Final[str] = _tag("instrText")
_FLD_CHAR: Final[str] = _tag("fldChar")
_FLD_SIMPLE: Final[str] = _tag("fldSimple")
_INS: Final[str] = _tag("ins")
_MOVE_FROM: Final[str] = _tag("moveFrom")
_MOVE_TO: Final[str] = _tag("moveTo")
_SDT: Final[str] = _tag("sdt")
_SDT_CONTENT: Final[str] = _tag("sdtContent")
_HYPERLINK: Final[str] = _tag("hyperlink")
_SMART_TAG: Final[str] = _tag("smartTag")
_CUSTOM_XML: Final[str] = _tag("customXml")
_TBL: Final[str] = _tag("tbl")
_TBL_PR: Final[str] = _tag("tblPr")
_TBL_GRID: Final[str] = _tag("tblGrid")
_TR: Final[str] = _tag("tr")
_TR_PR: Final[str] = _tag("trPr")
_TC: Final[str] = _tag("tc")
_TC_PR: Final[str] = _tag("tcPr")
_V_MERGE: Final[str] = _tag("vMerge")
_TXBX_CONTENT: Final[str] = _tag("txbxContent")
_ALT_CHUNK: Final[str] = _tag("altChunk")
_SECT_PR: Final[str] = _tag("sectPr")
_LAST_RENDERED_PAGE_BREAK: Final[str] = _tag("lastRenderedPageBreak")
_PROOF_ERR: Final[str] = _tag("proofErr")
_BOOKMARK_START: Final[str] = _tag("bookmarkStart")
_BOOKMARK_END: Final[str] = _tag("bookmarkEnd")
_COMMENT_START: Final[str] = _tag("commentRangeStart")
_COMMENT_END: Final[str] = _tag("commentRangeEnd")
_COMMENT_REFERENCE: Final[str] = _tag("commentReference")
_ID: Final[str] = qname(W_NS, "id")
_TYPE: Final[str] = qname(W_NS, "type")
_R_NS: Final[str] = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_R_ID: Final[str] = qname(_R_NS, "id")
_FOOTNOTE_REFERENCE: Final[str] = _tag("footnoteReference")
_ENDNOTE_REFERENCE: Final[str] = _tag("endnoteReference")
_HEADER_REFERENCE: Final[str] = _tag("headerReference")
_FOOTER_REFERENCE: Final[str] = _tag("footerReference")
_TITLE_PG: Final[str] = _tag("titlePg")

_MC_ALTERNATE: Final[str] = qname(_MC_NS, "AlternateContent")
_MC_CHOICE: Final[str] = qname(_MC_NS, "Choice")
_MC_FALLBACK: Final[str] = qname(_MC_NS, "Fallback")

_DELETED_TAGS: Final[frozenset[str]] = frozenset({_DEL, _MOVE_FROM})
_CHANGE_TAGS: Final[frozenset[str]] = frozenset({_DEL, _MOVE_FROM, _INS, _MOVE_TO})
_WALK_TAGS: Final[frozenset[str]] = frozenset(
    {
        _SDT,
        _SDT_CONTENT,
        _HYPERLINK,
        _SMART_TAG,
        _CUSTOM_XML,
        _FLD_SIMPLE,
        _INS,
        _MOVE_TO,
    }
)
# Word shows what these hold, so the walk goes through them.

_IGNORED_TAGS: Final[frozenset[str]] = frozenset(
    {
        _BOOKMARK_START,
        _BOOKMARK_END,
        _PROOF_ERR,
        qname(W_NS, "permStart"),
        qname(W_NS, "permEnd"),
        _SECT_PR,
        _LAST_RENDERED_PAGE_BREAK,
    }
)

SYMBOL_FONTS: Final[frozenset[str]] = frozenset(
    {"symbol", "wingdings", "wingdings 2", "wingdings 3", "webdings"}
)

_REASON_ORDER: Final[dict[HiddenReason, int]] = {
    reason: index for index, reason in enumerate(HiddenReason)
}

_MAX_PARAGRAPHS: Final[int] = 200_000
# [Assumption] question 11: a hostile body ends early.


class _Paragraph:
    """One line before it is assembled, or one cell of a table row."""

    __slots__ = ("mark_deleted", "num_id", "num_level", "number", "pieces")

    def __init__(
        self,
        *,
        number: str | None,
        pieces: list[Text | Mark],
        mark_deleted: bool,
        num_id: str | None = None,
        num_level: int = 0,
    ) -> None:
        self.number = number
        self.pieces = pieces
        self.mark_deleted = mark_deleted
        self.num_id = num_id
        self.num_level = num_level


def _assemble(paragraphs: list[_Paragraph]) -> tuple[str, list[tuple[Text | Mark, int, int]]]:
    """Join the paragraphs into the text and the offsets of each piece."""

    parts: list[str] = []
    positions: list[tuple[Text | Mark, int, int]] = []
    offset = 0
    carried: list[Text | Mark] = []
    for paragraph in paragraphs:
        pieces = [*carried, *paragraph.pieces]
        if paragraph.mark_deleted:
            has_text = any(isinstance(piece, Text) and piece.text for piece in pieces)
            carried = pieces if has_text else []
            continue
        carried = []
        if paragraph.number is not None:
            parts.append(paragraph.number)
            offset += len(paragraph.number)
        for piece in pieces:
            text = piece.text if isinstance(piece, Text) else ""
            positions.append((piece, offset, offset + len(text)))
            parts.append(text)
            offset += len(text)
        parts.append("\n")
        offset += 1
    for piece in carried:
        text = piece.text if isinstance(piece, Text) else ""
        positions.append((piece, offset, offset + len(text)))
        parts.append(text)
        offset += len(text)
    if carried:
        parts.append("\n")
    return "".join(parts), positions


class _Walker:
    """Walk one part of a Word document, in the order Word draws it."""

    def __init__(
        self,
        *,
        styles: Styles | None = None,
        numbering: Numbering | None = None,
        quiet: bool = False,
    ) -> None:
        self.paragraphs: list[_Paragraph] = []
        self.hidden: list[HiddenText] = []
        self.changes: list[tuple[str, str, str]] = []
        self.comment_refs: list[str] = []
        self.note_refs: list[tuple[SideTextKind, str]] = []
        self.symbol_unread = False
        self._quiet = quiet
        self._styles = styles if styles is not None else Styles.from_xml(None)
        self._numbering = numbering
        self._paragraph_style: str | None = None
        self._paragraph_fill: str | None = None
        self._fields: list[str] = []
        self._word_count = 0
        self._in_word = False
        self._paragraph_count = 0
        self._boxes: list[_Paragraph] | None = None

    def walk(self, root: Element) -> None:
        """Walk the body of a parsed `word/document.xml`."""

        body = root.find(_BODY)
        if body is not None:
            self._walk_blocks(body, self.paragraphs)

    def _is_readable(self) -> bool:
        return all(state == "result" for state in self._fields)

    def _count_words(self, text: str) -> None:
        for char in text:
            if char.isspace():
                self._in_word = False
            elif not self._in_word:
                self._in_word = True
                self._word_count += 1
                if self._word_count > MAX_WORDS:
                    raise InputTooLargeError({"words": self._word_count, "limit_words": MAX_WORDS})

    def _text(self, text: str) -> Text:
        self._count_words(text)
        return Text(text=text)

    def _count_paragraph(self) -> None:
        self._paragraph_count += 1
        if self._paragraph_count > _MAX_PARAGRAPHS:
            raise InputTooLargeError(
                {"paragraphs": self._paragraph_count, "limit_paragraphs": _MAX_PARAGRAPHS}
            )

    def _child_for(self, element: Element, tag: str) -> Element | None:
        for child in element:
            if child.tag == tag:
                return child
        return None

    def _is_mark_deleted(self, paragraph: Element) -> bool:
        properties = self._child_for(paragraph, _PPR)
        if properties is None:
            return False
        run_properties = self._child_for(properties, _RPR)
        return run_properties is not None and self._child_for(run_properties, _DEL) is not None

    def _register(self, earlier: str, new: str, author: str) -> int | None:
        if earlier == "" and new == "":
            return None
        self.changes.append((earlier, new, author))
        return len(self.changes) - 1

    def _read_change_group(self, group: list[Element], pieces: list[Text | Mark]) -> None:
        segment: list[Element] = []
        author: str | None = None
        for child in group:
            if child.tag in _CHANGE_TAGS:
                child_author = _author(child)
                if author is not None and child_author != author:
                    self._emit_segment(segment, pieces)
                    segment = []
                author = child_author
            segment.append(child)
        self._emit_segment(segment, pieces)

    def _emit_segment(self, segment: list[Element], pieces: list[Text | Mark]) -> None:
        changes = [child for child in segment if child.tag in _CHANGE_TAGS]
        plan: dict[int, tuple[str, str]] = {}
        index = 0
        while index < len(changes):
            current = changes[index]
            following = changes[index + 1] if index + 1 < len(changes) else None
            is_pair = (
                following is not None
                and not _is_move(current)
                and not _is_move(following)
                and _kind(current) != _kind(following)
            )
            if is_pair and _kind(current) == "del":
                plan[id(current)] = ("skip", "")
                plan[id(following)] = ("replace", _deleted_text(current))
            elif is_pair:
                plan[id(current)] = ("insert", "")
                plan[id(following)] = ("delete", "")
            else:
                action = "delete" if _kind(current) == "del" else "insert"
                plan[id(current)] = (action, "")
            index += 2 if is_pair else 1
        for child in segment:
            if child.tag not in _CHANGE_TAGS:
                self._walk_inline(child, pieces)
                continue
            action, earlier = plan[id(child)]
            if action == "skip":
                continue
            if action == "delete":
                self._register(_deleted_text(child), "", _author(child))
            else:
                self._read_insertion(child, pieces, earlier=earlier)

    def _read_insertion(self, element: Element, pieces: list[Text | Mark], *, earlier: str) -> None:
        author = _author(element)
        local: list[Text | Mark] = []
        before = len(self.changes)
        for child in element:
            if child.tag in _DELETED_TAGS:
                self._register(_deleted_text(child), "", _author(child))
                continue
            self._walk_inline(child, local)
        new = "".join(piece.text for piece in local if isinstance(piece, Text))
        if new == "":
            if earlier != "":
                self.changes.insert(before, (earlier, "", author))
            pieces.extend(local)
            return
        self.changes.insert(before, (earlier, new, author))
        index = before
        for piece in local:
            pieces.append(replace(piece, change=index) if isinstance(piece, Text) else piece)

    def _walk_blocks(self, container: Element, out: list[_Paragraph]) -> None:
        for child in container:
            self._walk_block(child, out)

    def _walk_block(self, element: Element, out: list[_Paragraph]) -> None:
        tag = element.tag
        if tag == _P:
            self._read_paragraph(element, out)
        elif tag == _TBL:
            self._read_table(element, out)
        elif tag == _ALT_CHUNK:
            self._reach_alt_chunk()
        elif tag in _IGNORED_TAGS:
            return
        elif tag == _MC_ALTERNATE:
            self._read_alternate(element, out=out)
        else:
            self._walk_blocks(element, out)

    def _reach_alt_chunk(self) -> None:
        if not self._quiet:
            raise UnreadableFileError({"reason": "word_alt_chunk"})

    def _read_paragraph(self, element: Element, out: list[_Paragraph]) -> None:
        properties = self._child_for(element, _PPR)
        paragraph_style: str | None = None
        if properties is not None:
            style = self._child_for(properties, _PSTYLE)
            if style is not None:
                paragraph_style = style.get(qname(W_NS, "val"))
        num_id, num_level = self._numbering_of(properties, paragraph_style)
        paragraph = _Paragraph(
            number=None,
            pieces=[],
            mark_deleted=self._is_mark_deleted(element),
            num_id=num_id,
            num_level=num_level,
        )
        boxes: list[_Paragraph] = []
        saved = self._boxes
        saved_style = self._paragraph_style
        saved_fill = self._paragraph_fill
        self._boxes = boxes
        self._paragraph_style = paragraph_style
        self._paragraph_fill = self._styles.paragraph_fill(
            paragraph_style=paragraph_style, ppr=properties
        )
        children = [child for child in element if child.tag != _PPR]
        try:
            index = 0
            while index < len(children):
                child = children[index]
                if child.tag in _CHANGE_TAGS:
                    group: list[Element] = []
                    while index < len(children) and (
                        children[index].tag in _CHANGE_TAGS or _is_separator(children[index])
                    ):
                        group.append(children[index])
                        index += 1
                    self._read_change_group(group, paragraph.pieces)
                    continue
                self._walk_inline(child, paragraph.pieces)
                index += 1
        finally:
            self._boxes = saved
            self._paragraph_style = saved_style
            self._paragraph_fill = saved_fill
        self._count_words("\n")
        self._count_paragraph()
        out.append(paragraph)
        for box in boxes:
            self._count_paragraph()
            out.append(box)

    def _numbering_of(
        self, properties: Element | None, paragraph_style: str | None
    ) -> tuple[str | None, int]:
        num_pr = self._child_for(properties, _NUMPR) if properties is not None else None
        if num_pr is None:
            if self._numbering is None:
                return None, 0
            styled = self._styles.numbering(paragraph_style=paragraph_style)
            if styled is None:
                return None, 0
            num_id, ilvl_text, style_id = styled
            if ilvl_text is not None:
                return num_id, _level_of(ilvl_text)
            level = self._numbering.level_for_style(num_id=num_id, style_id=style_id)
            return num_id, level if level is not None else 0
        num_id_element = self._child_for(num_pr, _NUMID)
        direct_num_id = num_id_element.get(_VAL) if num_id_element is not None else None
        if direct_num_id is None:
            return None, 0
        ilvl_element = self._child_for(num_pr, _ILVL)
        ilvl = ilvl_element.get(_VAL) if ilvl_element is not None else None
        return direct_num_id, _level_of(ilvl)

    def _walk_inline(self, element: Element, pieces: list[Text | Mark]) -> None:
        tag = element.tag
        if tag == _R:
            self._read_run(element, pieces)
        elif tag in _DELETED_TAGS:
            return
        elif tag == _ALT_CHUNK:
            self._reach_alt_chunk()
        elif tag in _IGNORED_TAGS:
            return
        elif tag == _MC_ALTERNATE:
            self._read_alternate(element, pieces=pieces)
        elif tag == _TXBX_CONTENT:
            self._collect_text_box(element)
        elif tag in (_COMMENT_START, _COMMENT_END):
            ref = element.get(_ID)
            if ref is not None:
                kind: Literal["comment_start", "comment_end"] = (
                    "comment_start" if tag == _COMMENT_START else "comment_end"
                )
                pieces.append(Mark(kind=kind, ref=ref))
        elif tag == _COMMENT_REFERENCE:
            ref = element.get(_ID)
            if ref is not None:
                self.comment_refs.append(ref)
        elif tag in _WALK_TAGS:
            for child in element:
                self._walk_inline(child, pieces)
        else:
            for child in element:
                self._walk_inline(child, pieces)

    def _read_run(self, element: Element, pieces: list[Text | Mark]) -> None:
        local: list[Text | Mark] = []
        for child in element:
            tag = child.tag
            if tag == _FLD_CHAR:
                self._field_step(child)
            elif tag == _RPR or tag in (_INSTR_TEXT, _DEL_INSTR_TEXT, _DEL_TEXT):
                continue
            elif tag == _T:
                if self._is_readable() and child.text:
                    local.append(self._text(child.text))
            elif tag in (_TAB, _PTAB):
                if self._is_readable():
                    local.append(self._text("\t"))
            elif tag in (_BR, _CR):
                if self._is_readable():
                    local.append(self._text("\n"))
            elif tag == _NO_BREAK_HYPHEN:
                if self._is_readable():
                    local.append(self._text("\u2011"))
            elif tag == _SOFT_HYPHEN:
                continue
            elif tag in (_FOOTNOTE_REFERENCE, _ENDNOTE_REFERENCE):
                ref = child.get(_ID)
                if ref is not None:
                    kind = (
                        SideTextKind.FOOTNOTE
                        if tag == _FOOTNOTE_REFERENCE
                        else SideTextKind.ENDNOTE
                    )
                    self.note_refs.append((kind, ref))
            elif tag == _SYM:
                self._read_symbol(child, local)
            else:
                self._walk_inline(child, local)

        properties = self._child_for(element, _RPR)
        run_style: str | None = None
        if properties is not None:
            style = self._child_for(properties, _RSTYLE)
            if style is not None:
                run_style = style.get(qname(W_NS, "val"))
        props = self._styles.run_props(
            paragraph_style=self._paragraph_style, run_style=run_style, rpr=properties
        )
        run_text = "".join(piece.text for piece in local if isinstance(piece, Text))
        has_visible_text = run_text != "" and not run_text.isspace()
        hidden = _run_reasons(props, self._paragraph_fill) if has_visible_text else ()
        is_symbol_font = props.font is not None and props.font.lower() in SYMBOL_FONTS
        if has_visible_text and is_symbol_font:
            self.symbol_unread = True
        for piece in local:
            pieces.append(replace(piece, hidden=hidden) if isinstance(piece, Text) else piece)

    def _read_symbol(self, element: Element, pieces: list[Text | Mark]) -> None:
        font = element.get(qname(W_NS, "font"))
        if font is not None and font.lower() in SYMBOL_FONTS:
            self.symbol_unread = True
        value = element.get(qname(W_NS, "char"))
        code = int(value, 16) if value is not None else None
        if code is None or not 0x20 <= code <= 0xD7FF:
            self.symbol_unread = True
            return
        if self._is_readable():
            pieces.append(self._text(chr(code)))

    def _field_step(self, element: Element) -> None:
        kind = element.get(qname(W_NS, "fldCharType"))
        if kind == "begin":
            self._fields.append("instruction")
        elif kind == "separate" and self._fields:
            self._fields[-1] = "result"
        elif kind == "end" and self._fields:
            self._fields.pop()

    def _collect_text_box(self, element: Element) -> None:
        sink = self._boxes if self._boxes is not None else self.paragraphs
        self._walk_blocks(element, sink)

    def _read_alternate(
        self,
        element: Element,
        *,
        out: list[_Paragraph] | None = None,
        pieces: list[Text | Mark] | None = None,
    ) -> None:
        choice = self._child_for(element, _MC_CHOICE)
        fallback = self._child_for(element, _MC_FALLBACK)
        shown = choice if choice is not None else fallback
        other = fallback if choice is not None else choice
        if shown is None:
            return
        is_inline = pieces is not None
        if other is not None and self._branch_text(shown, inline=is_inline) != self._branch_text(
            other, inline=is_inline
        ):
            self.hidden.append(
                HiddenText(span=None, reason=HiddenReason.WORD_PART_NEVER_SHOWN, boxes=())
            )
        if pieces is not None:
            for child in shown:
                self._walk_inline(child, pieces)
        elif out is not None:
            self._walk_blocks(shown, out)

    def _branch_text(self, branch: Element, *, inline: bool) -> str:
        walker = _Walker(quiet=True)
        if inline:
            pieces: list[Text | Mark] = []
            boxes: list[_Paragraph] = []
            walker._boxes = boxes
            for child in branch:
                walker._walk_inline(child, pieces)
            text = "".join(piece.text for piece in pieces if isinstance(piece, Text))
            if boxes:
                text += _assemble(boxes)[0]
            return text.strip()
        out: list[_Paragraph] = []
        walker._walk_blocks(branch, out)
        return _assemble(out)[0].strip()

    def _read_table(self, element: Element, out: list[_Paragraph]) -> None:
        for child in element:
            if child.tag == _TR:
                self._read_row(child, out)
            elif child.tag in (_TBL_PR, _TBL_GRID):
                continue
            else:
                self._walk_table_rows(child, out)

    def _walk_table_rows(self, container: Element, out: list[_Paragraph]) -> None:
        for child in container:
            if child.tag == _TR:
                self._read_row(child, out)
            elif child.tag in (_SDT, _SDT_CONTENT, _CUSTOM_XML):
                self._walk_table_rows(child, out)

    def _row_deleted(self, row: Element) -> bool:
        properties = self._child_for(row, _TR_PR)
        return properties is not None and self._child_for(properties, _DEL) is not None

    def _read_row(self, row: Element, out: list[_Paragraph]) -> None:
        properties = self._child_for(row, _TR_PR)
        deletion = self._child_for(properties, _DEL) if properties is not None else None
        if deletion is not None:
            self._register(self._row_text(row), "", _author(deletion))
            return
        pieces: list[Text | Mark] = []
        is_first = True
        for cell in self._cells(row):
            if not is_first:
                pieces.append(self._text("\t"))
            is_first = False
            pieces.extend(self._cell_pieces(cell))
        insertion = self._child_for(properties, _INS) if properties is not None else None
        if insertion is not None:
            new = "".join(piece.text for piece in pieces if isinstance(piece, Text))
            index = self._register("", new, _author(insertion))
            if index is not None:
                pieces = [
                    replace(piece, change=index) if isinstance(piece, Text) else piece
                    for piece in pieces
                ]
        self._count_paragraph()
        out.append(_Paragraph(number=None, pieces=pieces, mark_deleted=False))

    def _row_text(self, row: Element) -> str:
        walker = _Walker(quiet=True, styles=self._styles)
        parts: list[str] = []
        for cell in self._cells(row):
            if parts:
                parts.append("\t")
            cell_pieces = walker._cell_pieces(cell)
            parts.append("".join(p.text for p in cell_pieces if isinstance(p, Text)))
        return "".join(parts)

    def _cells(self, row: Element) -> list[Element]:
        cells: list[Element] = []
        for child in row:
            if child.tag == _TC:
                cells.append(child)
            elif child.tag in (_SDT, _SDT_CONTENT):
                cells.extend(self._cells(child))
        return cells

    def _is_merged_continuation(self, cell: Element) -> bool:
        properties = self._child_for(cell, _TC_PR)
        if properties is None:
            return False
        merge = self._child_for(properties, _V_MERGE)
        if merge is None:
            return False
        value = merge.get(qname(W_NS, "val"))
        return value is None or value == "continue"

    def _cell_pieces(self, cell: Element) -> list[Text | Mark]:
        if self._is_merged_continuation(cell):
            return []
        blocks: list[_Paragraph] = []
        for child in cell:
            if child.tag == _TC_PR:
                continue
            if child.tag == _P:
                self._read_paragraph(child, blocks)
            elif child.tag == _TBL:
                self._read_table(child, blocks)
            else:
                self._walk_blocks(child, blocks)
        pieces: list[Text | Mark] = []
        carried: list[Text | Mark] = []
        for block in blocks:
            block_pieces = [*carried, *block.pieces]
            if block.mark_deleted:
                has_text = any(isinstance(piece, Text) and piece.text for piece in block_pieces)
                carried = block_pieces if has_text else []
                continue
            carried = []
            if pieces:
                pieces.append(self._text(" "))
            pieces.extend(block_pieces)
        pieces.extend(carried)
        return pieces


def _author(element: Element) -> str:
    return element.get(qname(W_NS, "author")) or ""


def _kind(element: Element) -> str:
    return "del" if element.tag in _DELETED_TAGS else "ins"


def _is_move(element: Element) -> bool:
    return element.tag in (_MOVE_FROM, _MOVE_TO)


def _run_text(element: Element) -> str:
    parts: list[str] = []
    for child in element:
        if child.tag == _T:
            parts.append(child.text or "")
        elif child.tag in (_TAB, _PTAB):
            parts.append("\t")
        elif child.tag in (_BR, _CR):
            parts.append("\n")
        elif child.tag == _NO_BREAK_HYPHEN:
            parts.append("\u2011")
    return "".join(parts)


def _is_separator(element: Element) -> bool:
    if element.tag in (_PROOF_ERR, _BOOKMARK_START, _BOOKMARK_END):
        return True
    if element.tag == _R:
        return _run_text(element).strip() == ""
    return False


def _deleted_text(element: Element) -> str:
    parts: list[str] = []

    def walk(node: Element) -> None:
        for child in node:
            tag = child.tag
            if tag in (_T, _DEL_TEXT):
                parts.append(child.text or "")
            elif tag in (_TAB, _PTAB):
                parts.append("\t")
            elif tag in (_INSTR_TEXT, _DEL_INSTR_TEXT):
                continue
            else:
                walk(child)

    walk(element)
    return "".join(parts)


def _level_of(value: str | None) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0


def _number_paragraphs(paragraphs: list[_Paragraph], numbering: Numbering) -> bool:
    """Write each kept paragraph's number and say whether any was unknown."""

    is_unknown = False
    for paragraph in paragraphs:
        if paragraph.mark_deleted or paragraph.num_id is None:
            continue
        label = numbering.label(num_id=paragraph.num_id, ilvl=paragraph.num_level)
        is_unknown = is_unknown or label.unknown
        if label.text is not None:
            paragraph.number = f"{label.text} "
    return is_unknown


def _run_reasons(props: RunProps, paragraph_fill: str | None) -> tuple[HiddenReason, ...]:
    """Return the hidden reasons of one run's words, each at most once."""

    reasons: list[HiddenReason] = []
    if props.vanish:
        reasons.append(HiddenReason.WORD_HIDDEN_RUN)
    is_tiny = props.size_half_points is not None and props.size_half_points < WORD_TINY_HALF_POINTS
    if is_tiny:
        reasons.append(HiddenReason.TINY_FONT)
    fill = props.highlight if props.highlight is not None else props.fill
    if fill is None:
        fill = paragraph_fill
    if props.color is not None:
        is_white_on_white = fill is None and props.color == "FFFFFF"
        is_same_colour = fill is not None and props.color == fill
        if is_white_on_white or is_same_colour:
            reasons.append(HiddenReason.LOW_CONTRAST)
    return tuple(reasons)


def _note_refs(
    refs: list[tuple[SideTextKind, str]],
) -> tuple[tuple[SideTextKind, str], ...]:
    seen: set[tuple[SideTextKind, str]] = set()
    result: list[tuple[SideTextKind, str]] = []
    for kind, ref in refs:
        if (kind, ref) in seen:
            continue
        seen.add((kind, ref))
        result.append((kind, ref))
    return tuple(result)


def _sections(root: Element) -> tuple[SectionRefs, ...]:
    sections: list[SectionRefs] = []
    for element in root.iter(_SECT_PR):
        headers: list[tuple[str, str]] = []
        footers: list[tuple[str, str]] = []
        for child in element:
            if child.tag == _HEADER_REFERENCE:
                headers.append((child.get(_TYPE) or "default", child.get(_R_ID) or ""))
            elif child.tag == _FOOTER_REFERENCE:
                footers.append((child.get(_TYPE) or "default", child.get(_R_ID) or ""))
        sections.append(
            SectionRefs(
                headers=tuple(headers),
                footers=tuple(footers),
                title_page=any(child.tag == _TITLE_PG for child in element),
            )
        )
    return tuple(sections)


def _comment_spans(
    positions: list[tuple[Text | Mark, int, int]], references: list[str]
) -> dict[str, Span | None]:
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    for piece, start, end in positions:
        if not isinstance(piece, Mark):
            continue
        if piece.kind == "comment_start":
            starts.setdefault(piece.ref, start)
        else:
            ends.setdefault(piece.ref, end)
    refs = [*starts, *(ref for ref in ends if ref not in starts)]
    refs.extend(ref for ref in references if ref not in refs)
    spans: dict[str, Span | None] = {}
    for ref in refs:
        first = starts.get(ref)
        last = ends.get(ref)
        if first is None or last is None or last <= first:
            spans[ref] = None
        else:
            spans[ref] = Span(start=first, end=last)
    return spans


def _tracked_changes(
    changes: list[tuple[str, str, str]],
    positions: list[tuple[Text | Mark, int, int]],
) -> tuple[TrackedChange, ...]:
    by_change: dict[int, list[tuple[int, int]]] = {}
    for piece, start, end in positions:
        if isinstance(piece, Text) and piece.change is not None:
            by_change.setdefault(piece.change, []).append((start, end))
    result: list[TrackedChange] = []
    for index, (earlier, new, author) in enumerate(changes):
        extents = by_change.get(index, [])
        span = None
        if new != "" and extents:
            span = Span(
                start=min(start for start, _ in extents), end=max(end for _, end in extents)
            )
        result.append(TrackedChange(earlier=earlier, new=new, author=author, span=span))
    return tuple(result)


def _hidden_from_positions(
    positions: list[tuple[Text | Mark, int, int]],
) -> tuple[HiddenText, ...]:
    """Merge touching spans of one reason, then order them by place."""

    by_reason: dict[HiddenReason, list[tuple[int, int]]] = {}
    for piece, start, end in positions:
        if not isinstance(piece, Text):
            continue
        for reason in piece.hidden:
            by_reason.setdefault(reason, []).append((start, end))
    entries: list[tuple[int, int, HiddenReason]] = []
    for reason, spans in by_reason.items():
        spans.sort()
        current_start, current_end = spans[0]
        for start, end in spans[1:]:
            if start == current_end:
                current_end = end
            else:
                entries.append((current_start, current_end, reason))
                current_start, current_end = start, end
        entries.append((current_start, current_end, reason))
    entries.sort(key=lambda entry: (entry[0], _REASON_ORDER[entry[2]]))
    return tuple(
        HiddenText(span=Span(start=start, end=end), reason=reason, boxes=())
        for start, end, reason in entries
    )


def build_body(
    root: Element,
    *,
    styles: Styles | None = None,
    numbering: Numbering | None = None,
) -> BodyResult:
    """Walk the body of a parsed `word/document.xml`.

    Input:   the parsed part (`root`), and the styles and numbering it uses.
    Output:  the accepted text, the hidden findings of the walk, the note
             references and the two flags of the walk. The text has one
             line for each paragraph and one line for each table row.
    Raises:  InputTooLargeError over 50,000 words or 200,000 paragraphs;
             UnreadableFileError with reason `word_alt_chunk` when the walk
             reaches an imported part.
    Effects: none.
    """

    walker = _Walker(styles=styles, numbering=numbering)
    walker.walk(root)
    numbering_unknown = (
        _number_paragraphs(walker.paragraphs, numbering) if numbering is not None else False
    )
    text, positions = _assemble(walker.paragraphs)
    return BodyResult(
        text=text,
        hidden=(*walker.hidden, *_hidden_from_positions(positions)),
        tracked_changes=_tracked_changes(walker.changes, positions),
        comment_spans=_comment_spans(positions, walker.comment_refs),
        note_refs=_note_refs(walker.note_refs),
        sections=_sections(root),
        numbering_unknown=numbering_unknown,
        symbol_unread=walker.symbol_unread,
    )
