"""Wording and span shapes (system design 3.4).

Every piece of wording the app stores is a Wording, so it cannot be
stored without its written-by value (ADR 0016, Spec 6.2). Contract
quotes are spans into the contract, not wording.
"""

from dataclasses import dataclass

from clause_tracer.core.enums import WrittenBy


@dataclass(frozen=True, slots=True, kw_only=True)
class Wording:
    """Every stored label reason, question, message, rewrite and note (ADR 0016)."""

    text: str
    written_by: WrittenBy


@dataclass(frozen=True, slots=True, kw_only=True)
class Span:
    """A place in the canonical text; half-open, counts code points (section 4.2)."""

    start: int
    end: int
