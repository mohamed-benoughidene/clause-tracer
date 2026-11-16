"""The pure hash of the exact AI request (S1-M4-T2, system design 7)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from clause_tracer.core import (
    PrivacyMode,
    PromptMessage,
    request_sha256,
    to_plain,
)
from clause_tracer.core.ids import ClauseId
from clause_tracer.core.tests.shapes_for_tests import EchoInputs, make_request

CHANGES: list[tuple[str, object]] = [
    ("step", "echo2"),
    ("prompt_id", "echo2"),
    ("prompt_version", 2),
    ("inputs", EchoInputs(clause_id=ClauseId("4.2"), text="Pay in 31 days.")),
    ("messages", (PromptMessage(role="user", text="Quote it."),)),
    ("schema_id", "echo-reply-2"),
    ("json_schema", {"type": "array"}),
    ("model", "test-model-2"),
    ("privacy_mode", PrivacyMode.OFF),
    ("max_tokens", 201),
]


def test_same_request_same_hash() -> None:
    assert request_sha256(make_request()) == request_sha256(make_request())


def test_hash_is_64_lowercase_hex() -> None:
    digest = request_sha256(make_request())
    assert len(digest) == 64
    assert digest == digest.lower()
    assert all(c in "0123456789abcdef" for c in digest)


def test_hash_ignores_hash_seed(tmp_path: Path) -> None:
    in_process = request_sha256(make_request())
    code = (
        "from clause_tracer.core import request_sha256; "
        "from clause_tracer.core.tests.shapes_for_tests import make_request; "
        "print(request_sha256(make_request()))"
    )
    hashes = []
    for seed in ("0", "1"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            env=env,
            cwd=tmp_path,
            check=True,
        )
        hashes.append(result.stdout.strip())
    assert hashes == [in_process, in_process]


@pytest.mark.parametrize(("field", "changed"), CHANGES, ids=[field for field, _ in CHANGES])
def test_each_field_changes_the_hash(field: str, changed: object) -> None:
    base = request_sha256(make_request())
    other = request_sha256(make_request(**{field: changed}))
    assert other != base, f"changing {field} did not change the hash"


def test_json_schema_key_order_is_ignored() -> None:
    # sort_keys=True: two orders of the same schema hash the same.
    first = request_sha256(make_request(json_schema={"a": 1, "b": 2}))
    second = request_sha256(make_request(json_schema={"b": 2, "a": 1}))
    assert first == second


def test_unknown_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot hash set"):
        to_plain({1, 2})


@given(text=st.text())
def test_rebuilt_copy_has_the_same_hash(text: str) -> None:
    first = make_request(inputs=EchoInputs(clause_id=ClauseId("4.2"), text=text))
    second = make_request(inputs=EchoInputs(clause_id=ClauseId("4.2"), text=text))
    assert request_sha256(first) == request_sha256(second)
