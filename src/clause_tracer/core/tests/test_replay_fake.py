"""The replay fake fails on a request it does not know (S1-M4-T3, T12)."""

import pytest

from clause_tracer.core import (
    AiClient,
    ModelTimeoutError,
    PromptMessage,
    UnrecordedRequest,
)
from clause_tracer.core.fakes import ReplayAiClient, assert_all_used
from clause_tracer.core.request_hash import request_sha256
from clause_tracer.core.tests.conftest import ReplayClientFactory
from clause_tracer.core.tests.shapes_for_tests import make_reply, make_request


def test_recorded_request_returns_its_reply(make_replay_client: ReplayClientFactory) -> None:
    reply = make_reply()
    client = make_replay_client({request_sha256(make_request()): reply})
    assert client.complete(make_request()) is reply


def test_one_character_change_raises() -> None:
    # T12: the fake knows one exact request; a different one is a test failure.
    client = ReplayAiClient({request_sha256(make_request()): make_reply()})
    changed = make_request(messages=(PromptMessage(role="user", text="Quote the clauses."),))
    with pytest.raises(UnrecordedRequest) as raised:
        client.complete(changed)
    message = str(raised.value)
    assert "step=echo" in message
    assert "sha256=" in message
    assert "Quote the clause" not in message


def test_unused_recording_is_reported() -> None:
    key = request_sha256(make_request())
    client = ReplayAiClient({key: make_reply()})
    assert client.unused_keys() == (key,)


def test_used_recording_is_not_unused() -> None:
    key = request_sha256(make_request())
    client = ReplayAiClient({key: make_reply()})
    client.complete(make_request())
    assert client.unused_keys() == ()


def test_assert_all_used_raises_on_unused() -> None:
    client = ReplayAiClient({request_sha256(make_request()): make_reply()})
    with pytest.raises(AssertionError, match="unused recordings"):
        assert_all_used(client)


def test_assert_all_used_passes_when_all_used() -> None:
    key = request_sha256(make_request())
    client = ReplayAiClient({key: make_reply()})
    client.complete(make_request())
    assert_all_used(client)


def test_fail_next_raises_once(make_replay_client: ReplayClientFactory) -> None:
    key = request_sha256(make_request())
    client = make_replay_client({key: make_reply()})
    client.fail_next(ModelTimeoutError)
    with pytest.raises(ModelTimeoutError) as raised:
        client.complete(make_request())
    assert raised.value.context["step"] == "echo"
    # The call after the failure returns the reply.
    client.complete(make_request())
    assert client.unused_keys() == ()


def test_fixture_client_works(make_replay_client: ReplayClientFactory) -> None:
    reply = make_reply("not json")
    client = make_replay_client({request_sha256(make_request()): reply})
    assert client.complete(make_request()).raw_body == b"not json"


def test_replay_fake_is_an_ai_client() -> None:
    # mypy strict checks this assignment against the port.
    client: AiClient = ReplayAiClient({})
    assert client is not None
