"""Shared pytest options and the golden-file helper."""

from collections.abc import Callable
from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-goldens",
        action="store_true",
        default=False,
        help="Rewrite golden files instead of comparing them.",
    )


def compare_or_update(path: Path, actual: str, *, update: bool) -> None:
    """Compare actual text with a golden file, or rewrite the file."""

    if update:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual, encoding="utf-8", newline="")
        return
    if not path.exists():
        raise AssertionError(
            f"{path.name} is missing. Run pytest with --update-goldens, then read the file."
        )
    with path.open(encoding="utf-8", newline="") as handle:
        expected = handle.read()
    assert actual == expected


@pytest.fixture
def golden_compare() -> Callable[..., None]:
    """The helper itself, for tests that choose the update flag."""

    return compare_or_update


@pytest.fixture
def check_golden(request: pytest.FixtureRequest) -> Callable[[Path, str], None]:
    """A checker that follows the command line's --update-goldens flag."""

    def check(path: Path, actual: str) -> None:
        compare_or_update(
            path,
            actual,
            update=request.config.getoption("--update-goldens"),
        )

    return check
