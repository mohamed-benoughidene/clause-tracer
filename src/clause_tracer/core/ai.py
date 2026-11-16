"""The AI request, reply and record shapes (system design 3.4, 6.3).

Provider-neutral: no zero-retention flags, cost-field names or model
lists (ADR 0015). The exact reply bytes are saved before anything
parses them (D8). Every datetime is timezone-aware.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

from clause_tracer.core.enums import PrivacyMode
from clause_tracer.core.ids import RecordId, ReviewId


@dataclass(frozen=True, slots=True, kw_only=True)
class StepInputs:
    """Base class of every step's own input shape."""


@dataclass(frozen=True, slots=True, kw_only=True)
class PromptMessage:
    """One rendered prompt part."""

    role: str
    text: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AiRequest:
    """The accepted form of one AI call (section 6.3, ADR 0015).

    Carries the structured inputs as well as the rendered prompt. Its
    json_schema becomes a read-only mapping copy, so the top level
    cannot be changed.
    """

    step: str
    prompt_id: str
    prompt_version: int
    inputs: StepInputs
    messages: tuple[PromptMessage, ...]
    schema_id: str
    json_schema: Mapping[str, object]
    model: str
    privacy_mode: PrivacyMode
    max_tokens: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "json_schema", MappingProxyType(dict(self.json_schema)))


@dataclass(frozen=True, slots=True, kw_only=True)
class Usage:
    """Token counts of one call; cached tokens are read on every call (ADR 0010)."""

    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    cost_usd: Decimal | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AiReply:
    """The exact reply, saved before it is parsed (D8)."""

    raw_body: bytes
    text: str
    model_used: str
    provider_used: str
    usage: Usage
    generation_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AiRecord:
    """Raw and append-only, failed calls too (D1, D8); its hash keys the cache."""

    record_id: RecordId
    schema_version: int
    review_id: ReviewId
    step: str
    attempt: int
    request_sha256: str
    request: AiRequest
    reply: AiReply | None
    error_code: str | None
    started_at: datetime
    finished_at: datetime
