"""Test-only shapes and builders for the core tests. Not exported from core."""

import dataclasses
from datetime import datetime, timedelta

from clause_tracer.core.ai import AiRecord, AiReply, AiRequest, PromptMessage, StepInputs, Usage
from clause_tracer.core.enums import PrivacyMode
from clause_tracer.core.ids import ClauseId, RecordId, ReviewId
from clause_tracer.core.request_hash import request_sha256


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class EchoInputs(StepInputs):
    """A test-only step input shape (system design 3.4, S1-M2-T6)."""

    clause_id: ClauseId
    text: str


def make_request(**changes: object) -> AiRequest:
    """One fixed AiRequest, with any field replaced by name."""

    request = AiRequest(
        step="echo",
        prompt_id="echo",
        prompt_version=1,
        inputs=EchoInputs(clause_id=ClauseId("4.2"), text="Pay in 30 days."),
        messages=(PromptMessage(role="user", text="Quote the clause."),),
        schema_id="echo-reply",
        json_schema={"type": "object"},
        model="test-model",
        privacy_mode=PrivacyMode.ON,
        max_tokens=200,
    )
    # The plan fixes this signature as **changes: object, a deliberate bag of
    # replacements. dataclasses.replace is typed per-field, so mypy cannot
    # verify the values through the bag; the call is checked at the AiRequest
    # constructor itself (recorded in the plan's change log, 16 Nov 2026).
    return dataclasses.replace(request, **changes)  # type: ignore[arg-type]


def make_reply(text: str = "{}") -> AiReply:
    """One fixed AiReply, with the body text replaced by name."""

    return AiReply(
        raw_body=text.encode(),
        text=text,
        model_used="test-model",
        provider_used="test-provider",
        usage=Usage(input_tokens=10, cached_input_tokens=0, output_tokens=5, cost_usd=None),
        generation_id="gen-1",
    )


def make_record(record_id: str, review_id: str, finished_at: datetime) -> AiRecord:
    """One fixed AiRecord of the echo step, finished at the given time."""

    request = make_request()
    return AiRecord(
        record_id=RecordId(record_id),
        schema_version=1,
        review_id=ReviewId(review_id),
        step="echo",
        attempt=1,
        request_sha256=request_sha256(request),
        request=request,
        reply=make_reply(),
        error_code=None,
        started_at=finished_at - timedelta(seconds=1),
        finished_at=finished_at,
    )
