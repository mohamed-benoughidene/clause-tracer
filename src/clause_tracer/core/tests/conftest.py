"""Shared fixtures for the core tests (S1-M4-T3)."""

from collections.abc import Callable, Iterator, Mapping

import pytest

from clause_tracer.core import AiReply
from clause_tracer.core.fakes import ReplayAiClient, assert_all_used

ReplayClientFactory = Callable[[Mapping[str, AiReply]], ReplayAiClient]


@pytest.fixture
def make_replay_client() -> Iterator[ReplayClientFactory]:
    """Make replay clients; each is checked for unused recordings after the test."""

    made: list[ReplayAiClient] = []

    def make(recordings: Mapping[str, AiReply]) -> ReplayAiClient:
        client = ReplayAiClient(recordings)
        made.append(client)
        return client

    yield make
    for client in made:
        assert_all_used(client)
