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
        ("a", "BSD-3-Clause, Apache-2.0, dependency licenses", False),
        ("pypdfium2", "BSD-3-Clause, Apache-2.0, dependency licenses", True),
        ("pypdfium2", "GPL-3.0-only", False),
        ("a", "MIT AND Apache-2.0", True),
        ("a", "GPL-3.0-only OR MIT", True),
        ("a", "MIT AND GPL-3.0-only", False),
        ("a", "GPL-3.0-only AND MIT", False),
        ("a", "BSD-3-Clause, GPL-3.0-only", False),
        ("a", "MIT; AGPL-3.0", False),
        ("a", "GPL-3.0-only AND (BSD-3-Clause OR MIT OR Apache-2.0)", False),
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


class _FakeInstalled:
    def __init__(self, requires: list[str]) -> None:
        self.requires = requires


def _write_pyproject(folder: Path, *dependencies: str) -> Path:
    listed = ", ".join(f"'{dependency}'" for dependency in dependencies)
    pyproject = folder / "pyproject.toml"
    pyproject.write_text(f"[project]\ndependencies = [{listed}]\n", encoding="utf-8")
    return pyproject


def test_runtime_packages_follows_dependencies_and_extras(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    requires = {
        "a": ["b"],
        "b": ["z"],
        "z": ['c; extra == "fast"', 'd; extra == "slow"'],
    }
    monkeypatch.setattr(
        licences.importlib.metadata,
        "distribution",
        lambda name: _FakeInstalled(requires.get(name, [])),
    )
    pyproject = _write_pyproject(tmp_path, "z[fast]", "a", 'old; python_version < "3"')

    assert licences.runtime_packages(pyproject) == ("a", "b", "c", "z")


def test_runtime_packages_names_a_missing_package(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def missing(name: str) -> _FakeInstalled:
        raise licences.importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(licences.importlib.metadata, "distribution", missing)
    pyproject = _write_pyproject(tmp_path, "a")

    with pytest.raises(SystemExit) as raised:
        licences.runtime_packages(pyproject)

    assert str(raised.value) == "licences: a is not installed"
