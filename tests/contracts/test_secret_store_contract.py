"""The SecretStore behaviour suite (S1-M4-T4, T2, ADR 0006).

Run against each fake now, and against the real adapter from stage 6.
"""

import pytest

from clause_tracer.core import InMemorySecretStore, SecretStore, SecretStoreUnavailableError


@pytest.fixture(params=["in_memory"])
def secret_store(request: pytest.FixtureRequest) -> SecretStore:
    if request.param == "in_memory":
        return InMemorySecretStore()
    raise AssertionError(f"unknown secret store param {request.param}")


@pytest.fixture(params=["in_memory"])
def unavailable_secret_store(request: pytest.FixtureRequest) -> SecretStore:
    if request.param == "in_memory":
        return InMemorySecretStore(available=False)
    raise AssertionError(f"unknown secret store param {request.param}")


PROVIDER_ID = "openrouter"


def test_put_then_get(secret_store: SecretStore) -> None:
    secret_store.put_secret(PROVIDER_ID, "sk-test")
    assert secret_store.get_secret(PROVIDER_ID) == "sk-test"


def test_get_missing_is_none(secret_store: SecretStore) -> None:
    assert secret_store.get_secret(PROVIDER_ID) is None


def test_put_twice_keeps_the_last(secret_store: SecretStore) -> None:
    secret_store.put_secret(PROVIDER_ID, "first")
    secret_store.put_secret(PROVIDER_ID, "second")
    assert secret_store.get_secret(PROVIDER_ID) == "second"


def test_delete_missing_succeeds(secret_store: SecretStore) -> None:
    # I8: deleting a missing id does nothing.
    secret_store.delete_secret(PROVIDER_ID)


def test_delete_then_get_is_none(secret_store: SecretStore) -> None:
    secret_store.put_secret(PROVIDER_ID, "sk-test")
    secret_store.delete_secret(PROVIDER_ID)
    assert secret_store.get_secret(PROVIDER_ID) is None


def test_unavailable_store_raises(unavailable_secret_store: SecretStore) -> None:
    with pytest.raises(SecretStoreUnavailableError) as raised:
        unavailable_secret_store.get_secret(PROVIDER_ID)
    assert raised.value.context["provider_id"] == PROVIDER_ID
    with pytest.raises(SecretStoreUnavailableError):
        unavailable_secret_store.put_secret(PROVIDER_ID, "sk-test")
    with pytest.raises(SecretStoreUnavailableError):
        unavailable_secret_store.delete_secret(PROVIDER_ID)
