"""The licence check: the runtime group must be MIT, BSD or Apache.

A named package may use another licence when its text equals the stated
one, so a changed licence fails. See ADR 0007 action item 2 and
docs/testing-strategy.md section 8.
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
}

_SPLIT_PATTERN: Final[re.Pattern[str]] = re.compile(r",|;| OR | AND ")


def _normalise(name: str) -> str:
    """Return the name in the form the exceptions and the output use."""
    return name.lower().replace("_", "-")


def _keep_requirement(requirement: Requirement) -> bool:
    """True when the requirement applies here and is not an extra."""
    marker = requirement.marker
    if marker is None:
        return True
    if "extra ==" in str(marker):
        return False
    return marker.evaluate()


def runtime_packages(pyproject: Path) -> tuple[str, ...]:
    """Return the installed runtime packages, with their dependencies, sorted."""
    with pyproject.open("rb") as handle:
        project = tomllib.load(handle)["project"]
    pending = [Requirement(text).name for text in project["dependencies"]]
    found: set[str] = set()
    while pending:
        name = pending.pop()
        normalised = _normalise(name)
        if normalised in found:
            continue
        found.add(normalised)
        try:
            distribution = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            raise SystemExit(f"licences: {name} is not installed") from None
        for text in distribution.requires or ():
            requirement = Requirement(text)
            if _keep_requirement(requirement):
                pending.append(requirement.name)
    return tuple(sorted(found))


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
    return any(piece.strip() in ALLOWED for piece in _SPLIT_PATTERN.split(text))


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
