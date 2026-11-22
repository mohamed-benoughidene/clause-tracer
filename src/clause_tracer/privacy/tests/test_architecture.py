"""The module's public shape (S4-M5-T4)."""

from pathlib import Path

import clause_tracer.privacy

MODULE = Path(__file__).parent.parent


def test_public_names() -> None:
    assert set(clause_tracer.privacy.__all__) == {
        "PrivacyInput",
        "anonymise",
        "dump_privacy_fixture",
        "find_personal_data",
        "group_entities",
        "load_privacy_fixture",
        "map_to_original",
        "render_privacy_report",
        "restore_reply",
        "restore_text",
    }


def test_module_has_its_parts() -> None:
    for name in ("README.md", "tests", "samples", "__main__.py"):
        assert (MODULE / name).exists(), name


def test_readme_names_every_public_name() -> None:
    readme = (MODULE / "README.md").read_text(encoding="utf-8")

    for name in clause_tracer.privacy.__all__:
        assert name in readme, name
