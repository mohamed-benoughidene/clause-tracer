"""The link map shapes (system design 3.4).

What `links` returns. An unresolved target is kept, with no target.
`cli` passes `terms` into `privacy` for its allow-list (section 4.1).
"""

from dataclasses import dataclass

from clause_tracer.core.ids import ClauseId
from clause_tracer.core.wording import Span


@dataclass(frozen=True, slots=True, kw_only=True)
class CrossReference:
    """A reference from one clause to another; an unresolved target is kept."""

    source: Span
    target: ClauseId | None


@dataclass(frozen=True, slots=True, kw_only=True)
class DefinedTerm:
    """A defined term: evidence trail, and the privacy allow-list (section 4.1)."""

    term: str
    definition: Span
    uses: tuple[Span, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Override:
    """Direction matters; no target means it joins every trail (Spec 4.5)."""

    clause_id: ClauseId
    target: ClauseId | None
    overrides_target: bool
    evidence: Span


@dataclass(frozen=True, slots=True, kw_only=True)
class OutsideDocument:
    """A document not loaded that the label's evidence reaches (Rule 10)."""

    name: str
    evidence: Span


@dataclass(frozen=True, slots=True, kw_only=True)
class LinkMap:
    """What `links` returns; `cli` passes `terms` into `privacy`."""

    references: tuple[CrossReference, ...]
    terms: tuple[DefinedTerm, ...]
    overrides: tuple[Override, ...]
    outside_documents: tuple[OutsideDocument, ...]
    undefined_terms: tuple[Span, ...]
