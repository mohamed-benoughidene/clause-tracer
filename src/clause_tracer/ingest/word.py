"""The Word reader (S5-M3-T8).

`read_word_file` reads a Word package into the same `Document` that the
other readers return: the accepted text as Word draws it, the hidden
findings, the tracked changes, and the side text that sits apart from the
body. The body walk is in `_word_body.py`; the side parts are in
`_word_side.py`.
"""

from typing import Final

from clause_tracer.core import (
    Document,
    FileKind,
    HiddenReason,
    HiddenText,
    InputTooLargeError,
    InputWarning,
    SideText,
    SideTextKind,
)
from clause_tracer.ingest._kind import detect_kind
from clause_tracer.ingest._word_body import build_body
from clause_tracer.ingest._word_numbering import Numbering
from clause_tracer.ingest._word_side import (
    comment_hidden,
    hidden_comments,
    link_comments,
    note_comment_refs,
    read_comments,
    read_headers_and_footers,
    read_notes,
    read_relationships,
)
from clause_tracer.ingest._word_styles import Styles, is_on
from clause_tracer.ingest._xml import W_NS, Element, parse_part, qname
from clause_tracer.ingest._zip import WordPackage, open_package
from clause_tracer.ingest.limits import MAX_FILE_BYTES
from clause_tracer.ingest.reading import _build_document
from clause_tracer.ingest.warnings import (
    WARNING_WORD_NOTES,
    WARNING_WORD_NUMBERING_UNKNOWN,
    WARNING_WORD_SYMBOL_UNREAD,
)

_DOCUMENT_PART: Final[str] = "word/document.xml"
_STYLES_PART: Final[str] = "word/styles.xml"
_NUMBERING_PART: Final[str] = "word/numbering.xml"
_SETTINGS_PART: Final[str] = "word/settings.xml"
_COMMENTS_PART: Final[str] = "word/comments.xml"
_FOOTNOTES_PART: Final[str] = "word/footnotes.xml"
_ENDNOTES_PART: Final[str] = "word/endnotes.xml"
_RELS_PART: Final[str] = "word/_rels/document.xml.rels"

_EVEN_AND_ODD: Final[str] = qname(W_NS, "evenAndOddHeaders")


def _part(package: WordPackage, name: str) -> Element | None:
    if not package.has(name):
        return None
    return parse_part(package.read_part(name))


def _has_even_and_odd(root: Element | None) -> bool:
    if root is None:
        return False
    element = root.find(_EVEN_AND_ODD)
    return element is not None and is_on(element)


def _order_hidden(hidden: tuple[HiddenText, ...]) -> tuple[HiddenText, ...]:
    return tuple(
        sorted(
            hidden,
            key=lambda item: (item.span is None, item.span.start if item.span is not None else 0),
        )
    )


def read_word_file(data: bytes, *, name: str) -> Document:
    """Read a Word file into a document.

    Input:   the file's bytes and its name.
    Output:  a Document whose text is the accepted view as Word draws it,
             with the hidden runs, comments and never-shown parts, the
             tracked changes and the side text. A Word document has no
             glyphs or pages.
    Raises:  ValueError when the bytes are not a Word file (a caller bug);
             OldWordFileError for an OLE2 file; InputTooLargeError over
             20 MB or 50,000 words; EmptyInputError when no visible
             character is present; NotTextError for a NUL character;
             UnreadableFileError when a package or an XML part is refused,
             or a reached part is imported (`word_alt_chunk`).
    Effects: none. Does not read or write files (I11).
    """

    if len(data) > MAX_FILE_BYTES:
        raise InputTooLargeError({"size_bytes": len(data), "limit_bytes": MAX_FILE_BYTES})
    kind = detect_kind(data, name)
    if kind is not FileKind.WORD:
        raise ValueError("ingest: read_word_file reads Word files only")

    package = open_package(data)
    document_root = parse_part(package.read_part(_DOCUMENT_PART))
    styles = Styles.from_xml(_part(package, _STYLES_PART))
    numbering = Numbering.from_xml(_part(package, _NUMBERING_PART), styles)
    body = build_body(document_root, styles=styles, numbering=numbering)

    comments_root = _part(package, _COMMENTS_PART)
    comments = read_comments(comments_root, styles)
    linked_comments = link_comments(comments, body.comment_spans)
    footnotes_root = _part(package, _FOOTNOTES_PART)
    endnotes_root = _part(package, _ENDNOTES_PART)
    notes, notes_hidden = read_notes(
        footnotes_root,
        endnotes_root,
        body.note_refs,
        styles,
    )
    relationships = read_relationships(_part(package, _RELS_PART))
    headers_and_footers, parts_hidden = read_headers_and_footers(
        package,
        relationships,
        body.sections,
        _has_even_and_odd(_part(package, _SETTINGS_PART)),
        styles,
    )
    comment_hidden_texts = comment_hidden(
        body.comment_spans,
        comments,
        note_comment_refs(footnotes_root, endnotes_root, body.note_refs, styles),
    )
    comment_runs = tuple(
        HiddenText(span=None, reason=HiddenReason.WORD_HIDDEN_RUN, boxes=())
        for _ref in hidden_comments(comments_root, styles)
    )
    hidden = _order_hidden(
        (
            *body.hidden,
            *comment_hidden_texts,
            *comment_runs,
            *notes_hidden,
            *parts_hidden,
        )
    )

    extra_warnings: list[InputWarning] = []
    if body.numbering_unknown:
        extra_warnings.append(InputWarning(code=WARNING_WORD_NUMBERING_UNKNOWN, page=None))
    if body.symbol_unread:
        extra_warnings.append(InputWarning(code=WARNING_WORD_SYMBOL_UNREAD, page=None))
    has_notes = any(item.kind in (SideTextKind.FOOTNOTE, SideTextKind.ENDNOTE) for item in notes)
    if has_notes:
        extra_warnings.append(InputWarning(code=WARNING_WORD_NOTES, page=None))

    side_text: tuple[SideText, ...] = (*linked_comments, *notes, *headers_and_footers)
    return _build_document(
        data,
        body.text,
        kind=FileKind.WORD,
        name=name,
        hidden=hidden,
        tracked_changes=body.tracked_changes,
        side_text=side_text,
        extra_warnings=tuple(extra_warnings),
    )
