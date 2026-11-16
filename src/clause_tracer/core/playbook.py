"""The playbook shapes (system design 3.4, Spec 4.1).

Playbook text carries no written-by value: names, topics and level
text are always the user's own words or a starter's fixed text
(ADR 0005 amendment of 13 Nov 2026, ADR 0016).
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from clause_tracer.core.enums import Direction, Level, PositionType, Unit
from clause_tracer.core.ids import CustomerId, PlaybookId, PositionId


@dataclass(frozen=True, slots=True, kw_only=True)
class NumberRule:
    """Rule 1: a number with a preferred and an acceptable limit."""

    unit: Unit
    direction: Direction
    preferred_limit: Decimal
    acceptable_limit: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class YesNoRule:
    """Rule 2; the missing level is always the "no" level."""

    question: str
    yes_level: Level
    no_level: Level


@dataclass(frozen=True, slots=True, kw_only=True)
class WordsRule:
    """One sentence per level."""

    preferred: str
    acceptable: str
    walk_away: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Position:
    """One playbook rule (Spec 4.1)."""

    id: PositionId
    topic: str
    type: PositionType
    rule: NumberRule | YesNoRule | WordsRule
    missing_level: Level
    why_note: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Playbook:
    """A playbook; starters are read-only."""

    id: PlaybookId
    schema_version: int
    name: str
    side: str
    customer_id: CustomerId | None
    positions: tuple[Position, ...]
    starter: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PlaybookSnapshot:
    """Taken at "Send for review"; drives "by the example playbook"."""

    playbook: Playbook
    taken_at: datetime
    unedited_starter: bool
