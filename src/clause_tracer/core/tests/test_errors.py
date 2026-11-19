"""Tests for the error tree (system design 3.4, 6.4)."""

import re

from clause_tracer.core import (
    ConfigError,
    DuplicateRecordError,
    EmptyInputError,
    EncryptedPdfError,
    InputError,
    InputTooLargeError,
    InvalidApiKeyError,
    LocalError,
    ModelReplyInvalidError,
    ModelServiceError,
    ModelTimeoutError,
    NetworkUnavailableError,
    NoCreditError,
    NoPrivateModelError,
    NotTextError,
    NotUtf8Error,
    OldWordFileError,
    PlaybookFormatError,
    RateLimitedError,
    ReviewCancelled,
    ScannedPdfError,
    SchemaTooNewError,
    SecretStoreUnavailableError,
    StorageCorruptError,
    UnreadableFileError,
)

LEAVES: tuple[type[Exception], ...] = (
    UnreadableFileError,
    ScannedPdfError,
    OldWordFileError,
    InputTooLargeError,
    NotUtf8Error,
    EmptyInputError,
    NotTextError,
    EncryptedPdfError,
    PlaybookFormatError,
    NetworkUnavailableError,
    InvalidApiKeyError,
    NoCreditError,
    RateLimitedError,
    NoPrivateModelError,
    ModelTimeoutError,
    ModelReplyInvalidError,
    SecretStoreUnavailableError,
    StorageCorruptError,
    SchemaTooNewError,
    ConfigError,
    DuplicateRecordError,
    ReviewCancelled,
)

GROUPS: tuple[type[Exception], ...] = (
    InputError,
    ModelServiceError,
    LocalError,
    ReviewCancelled,
)

EXPECTED_CODES: dict[type[Exception], str] = {
    UnreadableFileError: "unreadable_file",
    ScannedPdfError: "scanned_pdf",
    OldWordFileError: "old_word_file",
    InputTooLargeError: "input_too_large",
    NotUtf8Error: "not_utf8",
    EmptyInputError: "empty_input",
    NotTextError: "not_text",
    EncryptedPdfError: "encrypted_pdf",
    PlaybookFormatError: "playbook_format",
    NetworkUnavailableError: "network_unavailable",
    InvalidApiKeyError: "invalid_api_key",
    NoCreditError: "no_credit",
    RateLimitedError: "rate_limited",
    NoPrivateModelError: "no_private_model",
    ModelTimeoutError: "model_timeout",
    ModelReplyInvalidError: "model_reply_invalid",
    SecretStoreUnavailableError: "secret_store_unavailable",
    StorageCorruptError: "storage_corrupt",
    SchemaTooNewError: "schema_too_new",
    ConfigError: "config",
    DuplicateRecordError: "duplicate_record",
    ReviewCancelled: "review_cancelled",
}


def test_every_leaf_is_in_exactly_one_group() -> None:
    for leaf in LEAVES:
        holders = [group for group in GROUPS if issubclass(leaf, group)]
        assert len(holders) == 1, f"{leaf.__name__} sits in {len(holders)} groups"


def test_codes_are_unique_lower_snake_case() -> None:
    pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    codes = [leaf.code for leaf in LEAVES]  # type: ignore[attr-defined]
    for code in codes:
        assert pattern.match(code), f"{code} is not lower snake case"
    assert len(set(codes)) == 22


def test_codes_match_system_design() -> None:
    for leaf, code in EXPECTED_CODES.items():
        assert leaf.code == code  # type: ignore[attr-defined]


def test_context_is_read_only() -> None:
    error = ModelTimeoutError({"step": "match"})
    try:
        error.context["step"] = "x"  # type: ignore[index]
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError")


def test_context_defaults_to_empty() -> None:
    assert ConfigError().context == {}


def test_message_is_the_code() -> None:
    assert str(NoCreditError()) == "no_credit"


def test_empty_input_error() -> None:
    error = EmptyInputError()

    assert error.code == "empty_input"
    assert isinstance(error, InputError)


def test_not_text_error() -> None:
    error = NotTextError({"char_offset": 3})

    assert error.code == "not_text"
    assert isinstance(error, InputError)


def test_rate_limited_carries_the_wait_time() -> None:
    error = RateLimitedError({"step": "match"}, retry_after_seconds=30)
    assert error.retry_after_seconds == 30
    assert error.context["retry_after_seconds"] == 30
    assert error.context["step"] == "match"
    zero = RateLimitedError(retry_after_seconds=0)
    assert zero.retry_after_seconds == 0
    assert zero.retry_after_seconds is not None


def test_rate_limited_without_wait_time() -> None:
    error = RateLimitedError()
    assert error.retry_after_seconds is None
    assert error.context == {}
    assert str(error) == "rate_limited"


def test_rate_limited_negative_wait_raises() -> None:
    try:
        RateLimitedError(retry_after_seconds=-1)
    except ValueError as raised:
        assert str(raised) == "retry_after_seconds must be 0 or more"
    else:
        raise AssertionError("expected ValueError")
