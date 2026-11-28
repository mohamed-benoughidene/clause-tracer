"""The codec for the reply the child process writes (system design 15.5).

Both sides of the reply live in `cli`, because `core` never imports
Pydantic (ADR 0005). The reply is JSON; nothing deserialises it into
running code.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated, Final, Literal

from pydantic import ConfigDict, Field, TypeAdapter, ValidationError

from clause_tracer.core import (
    Document,
    EmptyInputError,
    EncryptedPdfError,
    InputError,
    InputTooLargeError,
    NotTextError,
    NotUtf8Error,
    OldWordFileError,
    PlaybookFormatError,
    ScannedPdfError,
    UnreadableFileError,
)
from clause_tracer.ingest import DOCUMENT_SCHEMA_VERSION

MAX_CHILD_REPLY_BYTES: Final[int] = 64 * 1024 * 1024
# [Assumption] system design 15.5: tuned in testing.

_INPUT_ERRORS: Final[Mapping[str, type[InputError]]] = {
    "unreadable_file": UnreadableFileError,
    "scanned_pdf": ScannedPdfError,
    "old_word_file": OldWordFileError,
    "input_too_large": InputTooLargeError,
    "not_utf8": NotUtf8Error,
    "empty_input": EmptyInputError,
    "not_text": NotTextError,
    "encrypted_pdf": EncryptedPdfError,
    "playbook_format": PlaybookFormatError,
}


@dataclass(frozen=True, slots=True, kw_only=True)
class ChildDone:
    """The child read the file: the document it built."""

    kind: Literal["done"] = "done"
    document: Document


@dataclass(frozen=True, slots=True, kw_only=True)
class ChildFailed:
    """The child named an input error: its code and its context."""

    kind: Literal["failed"] = "failed"
    code: str
    context: dict[str, str | int]


ChildReply = Annotated[ChildDone | ChildFailed, Field(discriminator="kind")]
_ADAPTER: Final[TypeAdapter[ChildReply]] = TypeAdapter(
    ChildReply, config=ConfigDict(extra="forbid", allow_inf_nan=False)
)


def encode_child_reply(reply: ChildDone | ChildFailed) -> bytes:
    """Return the bytes the child writes to its standard output."""
    return _ADAPTER.dump_json(reply)


def decode_child_reply(data: bytes) -> ChildDone | ChildFailed:
    """Return the reply, or raise `UnreadableFileError` with a reason.

    The validation message is never put into the context: it can hold
    contract text.
    """
    if len(data) > MAX_CHILD_REPLY_BYTES:
        raise UnreadableFileError({"reason": "child_reply_too_large"})
    try:
        reply = _ADAPTER.validate_json(data, strict=True)
    except ValidationError:
        raise UnreadableFileError({"reason": "child_reply_invalid"}) from None

    is_other_schema = (
        isinstance(reply, ChildDone) and reply.document.schema_version != DOCUMENT_SCHEMA_VERSION
    )
    if is_other_schema:
        raise UnreadableFileError({"reason": "child_reply_invalid"})

    return reply


def input_error_for_code(code: str, context: Mapping[str, str | int]) -> InputError:
    """Rebuild the named input error the child reported."""
    error_class = _INPUT_ERRORS.get(code)
    if error_class is None:
        return UnreadableFileError({"reason": "child_error_code_unknown"})
    return error_class(context)
