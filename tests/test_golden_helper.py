"""Tests for the golden-file helper in the root conftest.py."""

from collections.abc import Callable
from pathlib import Path

import pytest


def test_same_text_passes(golden_compare: Callable[..., None], tmp_path: Path) -> None:
    path = tmp_path / "same.txt"
    path.write_text("a\n", encoding="utf-8", newline="")

    golden_compare(path, "a\n", update=False)


def test_different_text_fails(golden_compare: Callable[..., None], tmp_path: Path) -> None:
    path = tmp_path / "different.txt"
    path.write_text("a\n", encoding="utf-8", newline="")

    with pytest.raises(AssertionError):
        golden_compare(path, "b\n", update=False)


def test_missing_file_fails_and_names_the_command(
    golden_compare: Callable[..., None], tmp_path: Path
) -> None:
    path = tmp_path / "missing.txt"

    with pytest.raises(AssertionError, match="--update-goldens"):
        golden_compare(path, "a\n", update=False)


def test_update_writes_the_file(golden_compare: Callable[..., None], tmp_path: Path) -> None:
    path = tmp_path / "new" / "written.txt"

    golden_compare(path, "a\n", update=True)

    assert path.read_bytes().decode("utf-8") == "a\n"


def test_update_replaces_the_file(golden_compare: Callable[..., None], tmp_path: Path) -> None:
    path = tmp_path / "replaced.txt"
    path.write_text("a\n", encoding="utf-8", newline="")

    golden_compare(path, "b\n", update=True)

    assert path.read_bytes().decode("utf-8") == "b\n"


def test_line_endings_are_kept(golden_compare: Callable[..., None], tmp_path: Path) -> None:
    path = tmp_path / "line-endings.txt"

    golden_compare(path, "a\r\nb", update=True)
    golden_compare(path, "a\r\nb", update=False)

    assert path.read_bytes() == b"a\r\nb"
