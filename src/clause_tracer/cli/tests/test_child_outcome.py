"""The outcome table of the child (S5-M2-T6)."""

import pytest

from clause_tracer.cli.child_reply import ChildDone, ChildFailed, encode_child_reply
from clause_tracer.cli.child_runner import classify_child_outcome
from clause_tracer.core import (
    Document,
    FileKind,
    ScannedPdfError,
    SourceFile,
    UnreadableFileError,
)
from clause_tracer.ingest import DOCUMENT_SCHEMA_VERSION


def _document() -> Document:
    return Document(
        schema_version=DOCUMENT_SCHEMA_VERSION,
        source=SourceFile(name="a.txt", kind=FileKind.TEXT, sha256="ab" * 32, size=12),
        text="Hello world.",
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )


def _reason(error: UnreadableFileError) -> object:
    return error.context["reason"]


def test_outcome_table() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        classify_child_outcome(returncode=0, stdout=b"", timed_out=True)
    assert _reason(raised.value) == "too_slow"

    with pytest.raises(UnreadableFileError) as raised:
        classify_child_outcome(returncode=1, stdout=b"", timed_out=False)
    assert _reason(raised.value) == "child_crashed"
    assert raised.value.context["exit_code"] == 1

    with pytest.raises(UnreadableFileError) as raised:
        classify_child_outcome(returncode=-11, stdout=b"", timed_out=False)
    assert _reason(raised.value) == "child_crashed"
    assert raised.value.context["exit_code"] == -11

    done = ChildDone(document=_document())
    assert (
        classify_child_outcome(returncode=0, stdout=encode_child_reply(done), timed_out=False)
        == done.document
    )

    failed = ChildFailed(code="scanned_pdf", context={"pages": 3})
    with pytest.raises(ScannedPdfError):
        classify_child_outcome(returncode=0, stdout=encode_child_reply(failed), timed_out=False)

    with pytest.raises(UnreadableFileError) as raised:
        classify_child_outcome(returncode=0, stdout=b"", timed_out=False)
    assert _reason(raised.value) == "child_reply_invalid"
