"""The body walk of the Word reader (S5-M3-T1, S5-M3-T2).

The walk reads `word/document.xml` as Word draws it: the accepted view of
the tracked changes, the cached result of a field, a table row as one line
and a text box after the paragraph that holds it. Content that Word does
not show is never read, and nothing is removed from the text it does show
(D1). A hidden run, low contrast and tiny print are flagged with a span
over their words.
"""

from dataclasses import replace
from typing import Final

from clause_tracer.core import (
    HiddenReason,
    HiddenText,
    InputTooLargeError,
    Span,
    UnreadableFileError,
)
from clause_tracer.ingest._thresholds import WORD_TINY_HALF_POINTS
from clause_tracer.ingest._word_model import BodyResult, Mark, Text
from clause_tracer.ingest._word_styles import RunProps, Styles
from clause_tracer.ingest._xml import W_NS, Element, qname
from clause_tracer.ingest.limits import MAX_WORDS

_MC_NS: Final[str] = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _tag(local: str) -> str:
    return qname(W_NS, local)


_BODY: Final[str] = _tag("body")
_P: Final[str] = _tag("p")
_PPR: Final[str] = _tag("pPr")
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

_MC_ALTERNATE: Final[str] = qname(_MC_NS, "AlternateContent")
_MC_CHOICE: Final[str] = qname(_MC_NS, "Choice")
_MC_FALLBACK: Final[str] = qname(_MC_NS, "Fallback")

_DELETED_TAGS: Final[frozenset[str]] = frozenset({_DEL, _MOVE_FROM})
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
        qname(W_NS, "bookmarkStart"),
        qname(W_NS, "bookmarkEnd"),
        qname(W_NS, "proofErr"),
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

    __slots__ = ("mark_deleted", "number", "pieces")

    def __init__(
        self, *, number: str | None, pieces: list[Text | Mark], mark_deleted: bool
    ) -> None:
        self.number = number
        self.pieces = pieces
        self.mark_deleted = mark_deleted


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

    def __init__(self, *, styles: Styles | None = None, quiet: bool = False) -> None:
        self.paragraphs: list[_Paragraph] = []
        self.hidden: list[HiddenText] = []
        self.symbol_unread = False
        self._quiet = quiet
        self._styles = styles if styles is not None else Styles.from_xml(None)
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
        paragraph = _Paragraph(number=None, pieces=[], mark_deleted=self._is_mark_deleted(element))
        properties = self._child_for(element, _PPR)
        paragraph_style: str | None = None
        if properties is not None:
            style = self._child_for(properties, _PSTYLE)
            if style is not None:
                paragraph_style = style.get(qname(W_NS, "val"))
        boxes: list[_Paragraph] = []
        saved = self._boxes
        saved_style = self._paragraph_style
        saved_fill = self._paragraph_fill
        self._boxes = boxes
        self._paragraph_style = paragraph_style
        self._paragraph_fill = self._styles.paragraph_fill(
            paragraph_style=paragraph_style, ppr=properties
        )
        try:
            for child in element:
                if child.tag == _PPR:
                    continue
                self._walk_inline(child, paragraph.pieces)
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
        if self._row_deleted(row):
            return
        pieces: list[Text | Mark] = []
        is_first = True
        for cell in self._cells(row):
            if not is_first:
                pieces.append(self._text("\t"))
            is_first = False
            pieces.extend(self._cell_pieces(cell))
        self._count_paragraph()
        out.append(_Paragraph(number=None, pieces=pieces, mark_deleted=False))

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
    numbering: object | None = None,
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

    walker = _Walker(styles=styles)
    walker.walk(root)
    text, positions = _assemble(walker.paragraphs)
    return BodyResult(
        text=text,
        hidden=(*walker.hidden, *_hidden_from_positions(positions)),
        symbol_unread=walker.symbol_unread,
    )
