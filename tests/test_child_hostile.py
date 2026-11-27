"""Hostile files end as named input errors in a real child (S5-M2-T7)."""

import subprocess
import sys
from typing import Any, Literal

import pytest

from clause_tracer.cli.child_runner import ChildLimits, read_file_in_child
from clause_tracer.core import InputTooLargeError, OldWordFileError, UnreadableFileError
from clause_tracer.ingest.limits import MAX_XML_PART_BYTES, MAX_ZIP_MEMBERS
from clause_tracer.ingest.tests.builders.hostile import (
    big_xml_docx,
    deep_xml_docx,
    doctype_docx,
    entity_docx,
    huge_text_node_docx,
    lying_low_docx,
    many_members_docx,
    not_a_zip,
    ole2_bytes,
    zip_bomb_docx,
)

_MIB = 1024 * 1024


def _reason(error: UnreadableFileError) -> object:
    return error.context["reason"]


def _big_part() -> bytes:
    return big_xml_docx(MAX_XML_PART_BYTES - _MIB)


def test_ole2_is_old_word() -> None:
    with pytest.raises(OldWordFileError):
        read_file_in_child(ole2_bytes(), name="a.doc")


def test_not_a_zip() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(not_a_zip(), name="a.docx")

    assert _reason(raised.value) == "zip_invalid"


def test_too_many_members() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(many_members_docx(MAX_ZIP_MEMBERS + 1), name="a.docx")

    assert _reason(raised.value) == "too_many_members"


def test_zip_bomb_is_input_too_large() -> None:
    with pytest.raises(InputTooLargeError):
        read_file_in_child(zip_bomb_docx(100 * _MIB), name="a.docx")


def test_lying_low() -> None:
    with pytest.raises(UnreadableFileError):
        read_file_in_child(lying_low_docx(), name="a.docx")


def test_doctype() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(doctype_docx(), name="a.docx")

    assert _reason(raised.value) == "doctype"


@pytest.mark.parametrize("kind", ["internal", "external_file", "external_url", "parameter"])
def test_each_entity_kind(
    kind: Literal["internal", "external_file", "external_url", "parameter"],
) -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(entity_docx(kind), name="a.docx")

    assert _reason(raised.value) == "doctype"


def test_deep_xml() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(deep_xml_docx(255), name="a.docx")

    assert _reason(raised.value) == "xml_invalid"


def test_huge_text_node() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(huge_text_node_docx(11 * _MIB), name="a.docx")

    assert _reason(raised.value) == "xml_invalid"


def test_too_slow() -> None:
    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(_big_part(), name="a.docx", limits=ChildLimits(timeout_s=0.4))

    assert _reason(raised.value) == "too_slow"


@pytest.mark.skipif(
    sys.platform == "win32", reason="committed memory differs: S5-M6-T6 tests Windows"
)
def test_too_greedy() -> None:
    with pytest.raises(UnreadableFileError):
        read_file_in_child(_big_part(), name="a.docx", limits=ChildLimits(memory_bytes=600 * _MIB))


def test_no_child_left_running(monkeypatch: pytest.MonkeyPatch) -> None:
    started: list[subprocess.Popen[Any]] = []
    real_popen = subprocess.Popen

    def keep(*args: Any, **kwargs: Any) -> subprocess.Popen[Any]:
        process = real_popen(*args, **kwargs)
        started.append(process)
        return process

    monkeypatch.setattr(subprocess, "Popen", keep)

    with pytest.raises(UnreadableFileError) as raised:
        read_file_in_child(_big_part(), name="a.docx", limits=ChildLimits(timeout_s=0.4))

    assert _reason(raised.value) == "too_slow"
    assert started
    assert started[0].poll() is not None
