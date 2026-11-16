"""Shapes for the stage 1 functions (system design 3.4, 14 Nov 2026).

What the playbook checks, the output scans, the quote-check fold, the
cost estimate and the last check before drawing take and return.
"""

from dataclasses import dataclass
from decimal import Decimal

from clause_tracer.core.enums import DrawFailure, Level, PlaybookProblemCode
from clause_tracer.core.ids import PositionId
from clause_tracer.core.results import Evidence


@dataclass(frozen=True, slots=True, kw_only=True)
class ScanContext:
    """What one output scan compares the AI text with."""

    label: Level | None
    allowed_numbers: tuple[Decimal, ...]
    acceptable_limits: tuple[Decimal, ...]
    known_placeholders: tuple[str, ...]
    defined_roles: tuple[str, ...]
    clause_numbers: tuple[str, ...]
    quote: str | None
    source_text: str | None
    instruction_given: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class QuoteFold:
    """The Spec 2 quote-check fold of a text, with its index map.

    to_original has one entry per folded character plus a last entry
    equal to the length of the original text.
    """

    text: str
    to_original: tuple[int, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class DrawAllowed:
    """The last check before drawing approved this evidence."""

    evidence: Evidence


@dataclass(frozen=True, slots=True, kw_only=True)
class DrawRefused:
    """The last check before drawing refused; nothing is drawn (section 4.2)."""

    failure: DrawFailure


@dataclass(frozen=True, slots=True, kw_only=True)
class CallPrices:
    """US dollars per million tokens, passed in by the caller (ADR 0015)."""

    input_per_million: Decimal
    cached_input_per_million: Decimal
    output_per_million: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class CostInputs:
    """The input of the pre-run estimate (section 7)."""

    positions: int
    words_positions: int
    clauses: int
    contract_tokens: int
    prices: CallPrices


@dataclass(frozen=True, slots=True, kw_only=True)
class CostRange:
    """The estimate: the call count, and the cost from cache hit to no hit."""

    calls: int
    low_usd: Decimal
    high_usd: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class PlaybookProblem:
    """One failed playbook check (Spec 4.1); position_id is None for a whole-playbook problem."""

    position_id: PositionId | None
    code: PlaybookProblemCode
