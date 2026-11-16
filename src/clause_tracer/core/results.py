"""The review result shapes (system design 3.4).

One value after the quote check is a CheckedValue; the label rules of
Spec 5 turn values into verdicts and labels. The four match results
are separate types, so a failed call can never pass as "nothing found"
(I4, ADR 0012).
"""

from dataclasses import dataclass
from decimal import Decimal

from clause_tracer.core.enums import Answer, Level, ReasonCode, WrittenBy
from clause_tracer.core.ids import ClauseId, PositionId, SentenceId
from clause_tracer.core.wording import Span


@dataclass(frozen=True, slots=True, kw_only=True)
class Evidence:
    """A confirmed quote; placed is false when it could not be marked on the page (ADR 0012)."""

    clause_id: ClauseId
    sentence_ids: tuple[SentenceId, ...]
    quote: Span
    placed: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CheckedValue:
    """One value after the quote check; the input of Rules 1, 2, 3, 5, 6 and 9.

    "None" reaches core as number == 0; "unlimited" is the unlimited field,
    which Rule 1 makes the worst value (decided 14 Nov 2026).
    """

    position_id: PositionId
    clause_id: ClauseId
    evidence: Evidence | None
    raw_value: str | None
    number: Decimal | None
    range_high: Decimal | None
    unit_as_written: str | None
    start_point_as_written: str | None
    answer: Answer | None
    condition: Span | None
    vague: bool
    amount: Decimal | None
    total: Decimal | None
    reasons: tuple[ReasonCode, ...]
    unlimited: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class JudgedLevel:
    """One AI judgement for a words position (Spec 6.1 step 9)."""

    position_id: PositionId
    clause_id: ClauseId
    evidence: Evidence | None
    level: Level


@dataclass(frozen=True, slots=True, kw_only=True)
class MatchFound:
    """The position was found in the clauses named."""

    position_id: PositionId
    clause_ids: tuple[ClauseId, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class NothingFound:
    """Nothing was found; searches fills the "Where it was searched" panel."""

    position_id: PositionId
    searches: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class MatchUnconfirmed:
    """The searches disagree; the label is unsure with MATCH_UNCONFIRMED (ADR 0012)."""

    position_id: PositionId
    clauses_to_read: tuple[ClauseId, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class CallFailed:
    """The call failed twice; its value becomes unsure (Spec 6.2)."""

    code: str


MatchResult = MatchFound | NothingFound | MatchUnconfirmed | CallFailed


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolLabel:
    """The label code picked for one position; written_by is AI only for words
    positions, which are drawn in pencil (ADR 0002)."""

    position_id: PositionId
    level: Level
    reasons: tuple[ReasonCode, ...]
    evidence: tuple[Evidence, ...]
    written_by: WrittenBy


@dataclass(frozen=True, slots=True, kw_only=True)
class NotCoveredClause:
    """A clause the playbook does not cover (ADR 0011)."""

    clause_id: ClauseId
    clause_type: str
