"""The error tree (system design 3.4 and 6.4; I5, I6, I7).

Every error the project raises on purpose is a subclass of ClauseTracerError.
A code names the cause; the edge turns codes into words. Context holds ids,
step names and counts only, never contract text.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import ClassVar


class ClauseTracerError(Exception):
    """Base of every error the project raises on purpose (I6)."""

    code: ClassVar[str] = ""

    def __init__(self, context: Mapping[str, str | int] | None = None) -> None:
        super().__init__(self.code)
        self.context: Mapping[str, str | int] = MappingProxyType(dict(context or {}))


class InputError(ClauseTracerError):
    """A contract or playbook the app cannot read."""

    code: ClassVar[str] = ""


class ModelServiceError(ClauseTracerError):
    """The AI service failed, was unreachable or gave an unusable reply."""

    code: ClassVar[str] = ""


class LocalError(ClauseTracerError):
    """Something on this computer failed: the store, secrets or settings."""

    code: ClassVar[str] = ""


class ReviewCancelled(ClauseTracerError):
    """The user cancelled the review."""

    code: ClassVar[str] = "review_cancelled"


class UnreadableFileError(InputError):
    code: ClassVar[str] = "unreadable_file"


class ScannedPdfError(InputError):
    code: ClassVar[str] = "scanned_pdf"


class OldWordFileError(InputError):
    code: ClassVar[str] = "old_word_file"


class InputTooLargeError(InputError):
    code: ClassVar[str] = "input_too_large"


class NotUtf8Error(InputError):
    code: ClassVar[str] = "not_utf8"


class EmptyInputError(InputError):
    code: ClassVar[str] = "empty_input"


class EncryptedPdfError(InputError):
    code: ClassVar[str] = "encrypted_pdf"


class PlaybookFormatError(InputError):
    code: ClassVar[str] = "playbook_format"


class NetworkUnavailableError(ModelServiceError):
    code: ClassVar[str] = "network_unavailable"


class InvalidApiKeyError(ModelServiceError):
    code: ClassVar[str] = "invalid_api_key"


class NoCreditError(ModelServiceError):
    code: ClassVar[str] = "no_credit"


class RateLimitedError(ModelServiceError):
    """The AI service asked the app to wait. Carries the wait, when given."""

    code: ClassVar[str] = "rate_limited"

    def __init__(
        self,
        context: Mapping[str, str | int] | None = None,
        *,
        retry_after_seconds: int | None = None,
    ) -> None:
        if retry_after_seconds is not None and retry_after_seconds < 0:
            raise ValueError("retry_after_seconds must be 0 or more")
        merged: dict[str, str | int] = dict(context or {})
        if retry_after_seconds is not None:
            merged["retry_after_seconds"] = retry_after_seconds
        super().__init__(merged)
        self.retry_after_seconds: int | None = retry_after_seconds


class NoPrivateModelError(ModelServiceError):
    code: ClassVar[str] = "no_private_model"


class ModelTimeoutError(ModelServiceError):
    code: ClassVar[str] = "model_timeout"


class ModelReplyInvalidError(ModelServiceError):
    code: ClassVar[str] = "model_reply_invalid"


class SecretStoreUnavailableError(LocalError):
    code: ClassVar[str] = "secret_store_unavailable"


class StorageCorruptError(LocalError):
    code: ClassVar[str] = "storage_corrupt"


class SchemaTooNewError(LocalError):
    code: ClassVar[str] = "schema_too_new"


class ConfigError(LocalError):
    code: ClassVar[str] = "config"


class DuplicateRecordError(LocalError):
    code: ClassVar[str] = "duplicate_record"
