"""Tests for the licence check script (ADR 0007 action item 2)."""

import importlib.util
import sys
from email.message import Message
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_licences.py"

_spec = importlib.util.spec_from_file_location("check_licences", SCRIPT)
assert _spec is not None and _spec.loader is not None
licences = importlib.util.module_from_spec(_spec)
sys.modules["check_licences"] = licences
_spec.loader.exec_module(licences)


@pytest.mark.parametrize(
    ("name", "text", "expected"),
    [
        ("a", "MIT", True),
        ("a", "BSD-3-Clause", True),
        ("a", "Apache-2.0", True),
        ("a", "Apache-2.0 OR BSD-2-Clause", True),
        ("a", "BSD-3-Clause, Apache-2.0, dependency licenses", True),
        ("a", "GPL-3.0-only", False),
        ("a", "MPL-2.0", False),
        ("a", "unknown", False),
        ("a", "", False),
        ("pikepdf", "MPL-2.0", True),
        ("pikepdf", "GPL-3.0-only", False),
        ("pillow", "MIT-CMU", True),
        ("pillow", "MIT", False),
        ("typing-extensions", "PSF-2.0", True),
    ],
)
def test_is_allowed(name: str, text: str, expected: bool) -> None:
    assert licences.is_allowed(name, text) is expected


def test_licence_text_reads_a_classifier(monkeypatch: pytest.MonkeyPatch) -> None:
    metadata = Message()
    metadata["Classifier"] = "License :: OSI Approved :: MIT License"

    class FakeDistribution:
        def __init__(self, message: Message) -> None:
            self.metadata = message

    monkeypatch.setattr(
        licences.importlib.metadata,
        "distribution",
        lambda _name: FakeDistribution(metadata),
    )

    assert licences.licence_text("a") == "MIT License"


def test_main_fails_on_an_offender(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(licences, "runtime_packages", lambda _pyproject: ("a", "b"))
    monkeypatch.setattr(
        licences, "licence_text", lambda name: "MIT" if name == "a" else "GPL-3.0-only"
    )

    assert licences.main() == 1
    assert capsys.readouterr().out == "b GPL-3.0-only\n"
