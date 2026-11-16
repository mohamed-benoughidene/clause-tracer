"""The placeholder map shapes (system design 3.4, ADR 0008).

PlaceholderText is the only contract text that leaves the computer.
Segments tile both texts, so a quote maps back exactly (section 4.2).
"""

from dataclasses import dataclass

from clause_tracer.core.enums import PiiSource, PlaceholderKind, SegmentKind
from clause_tracer.core.wording import Span


@dataclass(frozen=True, slots=True, kw_only=True)
class Party:
    """Typed party details: raw data, and the first privacy finder."""

    name: str
    address: str | None
    yours: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PiiSuggestion:
    """What the PiiDetector port and the code finders return."""

    span: Span
    kind: PlaceholderKind
    source: PiiSource


@dataclass(frozen=True, slots=True, kw_only=True)
class PlaceholderEntity:
    """One placeholder, such as Person 1, for every variant of one name."""

    id: str
    kind: PlaceholderKind
    number: int
    spans: tuple[Span, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Segment:
    """Tiles both texts, so a quote maps back exactly (section 4.2)."""

    kind: SegmentKind
    sent: Span
    original: Span
    entity_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class PlaceholderText:
    """The only contract text that leaves the computer."""

    text: str
    entities: tuple[PlaceholderEntity, ...]
    segments: tuple[Segment, ...]
