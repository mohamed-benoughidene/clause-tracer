"""The document shapes (system design 3.4 and 4.2).

Offsets are half-open, count code points, and point into Document.text.
The raw file bytes are kept unchanged (D1). A document without glyphs
(text, Markdown, pasted text, Word) has glyphs == (), char_map == ()
and pages == () (decided 14 Nov 2026).
"""

from dataclasses import dataclass

from clause_tracer.core.enums import FileKind, HiddenReason
from clause_tracer.core.ids import ClauseId, SentenceId
from clause_tracer.core.wording import Span


@dataclass(frozen=True, slots=True, kw_only=True)
class PageBox:
    """PDF points, top-left origin, one coordinate system (ADR 0007)."""

    page: int
    x0: float
    top: float
    x1: float
    bottom: float


@dataclass(frozen=True, slots=True, kw_only=True)
class Page:
    """One page of the document; pages are numbered from 1."""

    number: int
    width: float
    height: float


@dataclass(frozen=True, slots=True, kw_only=True)
class Glyph:
    """One drawn character; page is a Page.number and equals box.page."""

    page: int
    box: PageBox


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceFile:
    """Points at the raw bytes, which the store keeps unchanged (D1)."""

    name: str
    kind: FileKind
    sha256: str
    size: int


@dataclass(frozen=True, slots=True, kw_only=True)
class HiddenText:
    """Flagged, never removed (D1); no span when the text is not in the canonical text."""

    span: Span | None
    reason: HiddenReason
    boxes: tuple[PageBox, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class TrackedChange:
    """Listed at the contract check; the accepted view is the contract (ADR 0012)."""

    earlier: str
    new: str
    author: str
    span: Span | None


@dataclass(frozen=True, slots=True, kw_only=True)
class InputWarning:
    """Undecodable pages, scanned pages in a mixed file, not English (Spec 9)."""

    code: str
    page: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Document:
    """The one canonical text; offsets point into text (section 4.2)."""

    schema_version: int
    source: SourceFile
    text: str
    char_map: tuple[int | None, ...]
    glyphs: tuple[Glyph, ...]
    pages: tuple[Page, ...]
    furniture: tuple[Span, ...]
    hidden: tuple[HiddenText, ...]
    undecodable: tuple[Span, ...]
    tracked_changes: tuple[TrackedChange, ...]
    warnings: tuple[InputWarning, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class MatchKey:
    """Folded copy with its index map (section 4.2)."""

    text: str
    to_canonical: tuple[int, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Sentence:
    """Stable ids such as 4.2.s3, which the AI points at."""

    id: SentenceId
    span: Span


@dataclass(frozen=True, slots=True, kw_only=True)
class Clause:
    """One clause, or one paragraph when the contract has no numbers (Spec 6.1 step 2)."""

    id: ClauseId
    number: str | None
    heading: str | None
    level: int
    parent_id: ClauseId | None
    span: Span
    numbering_source: str
    sentences: tuple[Sentence, ...]
