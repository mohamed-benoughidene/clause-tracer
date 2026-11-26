"""The licence check: the runtime group must be MIT, BSD or Apache.

A named package may use another licence when its text equals the stated
one, so a changed licence fails. In any other text one choice of an `OR`
is enough, and every piece of an `AND` or of a list must be allowed. See
ADR 0007 action item 2 and its amendments, and docs/testing-strategy.md
section 8.
"""

import importlib.metadata
import re
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from packaging.requirements import Requirement

ALLOWED: Final[frozenset[str]] = frozenset(
    {
        "MIT",
        "MIT License",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "BSD License",
        "Apache-2.0",
        "Apache Software License",
    }
)

NAMED_EXCEPTIONS: Final[Mapping[str, str]] = {
    "pikepdf": "MPL-2.0",
    "pillow": "MIT-CMU",
    "typing-extensions": "PSF-2.0",
    "pypdfium2": "BSD-3-Clause, Apache-2.0, dependency licenses",
}

_LIST_PATTERN: Final[re.Pattern[str]] = re.compile(r"[,;]")


def _normalise(name: str) -> str:
    """Return the name in the form the exceptions and the output use."""
    return name.lower().replace("_", "-")


def _applies(requirement: Requirement, extras: frozenset[str]) -> bool:
    """True when the requirement applies on this system.

    `extras` holds the extras that the parent requirement asked for.
    """
    marker = requirement.marker
    if marker is None:
        return True
    return any(marker.evaluate({"extra": extra}) for extra in ("", *extras))


def runtime_packages(pyproject: Path) -> tuple[str, ...]:
    """Return the installed runtime packages, with their dependencies, sorted."""
    with pyproject.open("rb") as handle:
        project = tomllib.load(handle)["project"]
    direct = [Requirement(text) for text in project["dependencies"]]
    pending = [requirement for requirement in direct if _applies(requirement, frozenset())]
    walked: set[tuple[str, frozenset[str]]] = set()
    while pending:
        requirement = pending.pop()
        extras = frozenset(requirement.extras)
        key = (_normalise(requirement.name), extras)
        if key in walked:
            continue
        walked.add(key)
        try:
            distribution = importlib.metadata.distribution(requirement.name)
        except importlib.metadata.PackageNotFoundError:
            raise SystemExit(f"licences: {requirement.name} is not installed") from None
        for text in distribution.requires or ():
            child = Requirement(text)
            if _applies(child, extras):
                pending.append(child)
    return tuple(sorted({name for name, _extras in walked}))


def licence_text(name: str) -> str:
    """Return the licence the installed package declares."""
    metadata = importlib.metadata.distribution(name).metadata
    expression = metadata.get("License-Expression")
    if expression:
        return expression
    declared = metadata.get("License")
    if declared and len(declared) <= 200:
        return declared
    prefix = "License :: OSI Approved :: "
    classifiers = [
        value.removeprefix(prefix)
        for value in metadata.get_all("Classifier") or ()
        if value.startswith("License ::")
    ]
    if classifiers:
        return ", ".join(classifiers)
    return "unknown"


def is_allowed(name: str, text: str) -> bool:
    """True when the package may ship with the app."""
    stated = NAMED_EXCEPTIONS.get(name)
    if stated is not None:
        return text == stated
    if "(" in text or ")" in text:
        return False
    return all(_part_is_allowed(part) for part in _LIST_PATTERN.split(text))


def _part_is_allowed(part: str) -> bool:
    """True when at least one `OR` choice has only allowed `AND` pieces."""
    return any(
        all(piece.strip() in ALLOWED for piece in choice.split(" AND "))
        for choice in part.split(" OR ")
    )


def main() -> int:
    """Check every runtime package and return the exit code."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    names = runtime_packages(pyproject)
    offenders = 0
    for name in names:
        text = licence_text(name)
        if not is_allowed(name, text):
            print(f"{name} {text}")
            offenders += 1
    if offenders:
        return 1
    print(f"licences: ok ({len(names)} packages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
