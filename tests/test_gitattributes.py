"""The line-ending rules of the repository (S5-M2-T8)."""

from pathlib import Path

GITATTRIBUTES = Path(__file__).resolve().parents[1] / ".gitattributes"


def test_gitattributes() -> None:
    lines = GITATTRIBUTES.read_text(encoding="utf-8").splitlines()

    assert "* -text" in lines
    assert "*.pdf binary" in lines
