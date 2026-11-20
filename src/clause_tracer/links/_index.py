"""The clause index: find the clause at an offset, and resolve a number (S3-M2-T1)."""

import bisect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from clause_tracer.core import Clause, ClauseId, Sentence

_SCHEDULE_WORDS: Final[tuple[str, ...]] = (
    "schedule",
    "annex",
    "appendix",
    "exhibit",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ClauseIndex:
    """The clauses in text order, with the lookups `links` needs."""

    clauses: tuple[Clause, ...]
    starts: tuple[int, ...]
    by_id: Mapping[ClauseId, Clause]
    resolvable: frozenset[str]

    def clause_at(self, offset: int) -> Clause | None:
        """Return the clause whose span holds `offset`, or None."""

        index = bisect.bisect_right(self.starts, offset) - 1
        if index < 0:
            return None
        clause = self.clauses[index]
        if offset >= clause.span.end:
            return None
        return clause

    def sentence_at(self, offset: int) -> Sentence | None:
        """Return the sentence whose span holds `offset`, or None."""

        clause = self.clause_at(offset)
        if clause is None:
            return None
        for sentence in clause.sentences:
            if sentence.span.start <= offset < sentence.span.end:
                return sentence
        return None

    def resolve(self, key: str) -> ClauseId | None:
        """Return the clause id for `key`, or None when it is not unique."""

        if key in self.resolvable:
            return ClauseId(key)
        return None

    def top_ancestor(self, clause: Clause) -> Clause:
        """Follow the parents until a clause with no parent, and return it."""

        current = clause
        while current.parent_id is not None:
            parent = self.by_id.get(current.parent_id)
            if parent is None:
                return current
            current = parent
        return current

    def in_schedule(self, clause: Clause) -> Clause | None:
        """Return the schedule that holds `clause`, or None."""

        top = self.top_ancestor(clause)
        if top.number is None:
            return None
        folded = top.number.casefold()
        if any(folded.startswith(word) for word in _SCHEDULE_WORDS):
            return top
        return None


def build_index(clauses: tuple[Clause, ...]) -> ClauseIndex:
    """Build the index, refusing clauses that are out of order (a caller bug)."""

    previous_start = -1
    previous_end = -1
    for clause in clauses:
        if clause.span.start <= previous_start or clause.span.start < previous_end:
            raise ValueError("clauses are not in text order")
        previous_start = clause.span.start
        previous_end = clause.span.end

    positions: dict[ClauseId, int] = {}
    for position, clause in enumerate(clauses):
        positions.setdefault(clause.id, position)
    for position, clause in enumerate(clauses):
        if clause.parent_id is None:
            continue
        parent_position = positions.get(clause.parent_id)
        if parent_position is not None and parent_position >= position:
            raise ValueError(f"clause {clause.id} has a later parent")

    by_id: dict[ClauseId, Clause] = {}
    counts: dict[str, int] = {}
    blocked: set[str] = set()
    for clause in clauses:
        by_id.setdefault(clause.id, clause)
        name = str(clause.id)
        counts[name] = counts.get(name, 0) + 1
        marker = name.find("~")
        while marker != -1:
            blocked.add(name[:marker])
            marker = name.find("~", marker + 1)

    resolvable = frozenset(
        name for name, count in counts.items() if count == 1 and name not in blocked
    )
    return ClauseIndex(
        clauses=clauses,
        starts=tuple(clause.span.start for clause in clauses),
        by_id=by_id,
        resolvable=resolvable,
    )
