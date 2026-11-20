"""The module's public shape (S3-M5-T1)."""

from pathlib import Path

import clause_tracer.links

MODULE = Path(__file__).parent.parent


def test_public_names() -> None:
    assert set(clause_tracer.links.__all__) == {
        "SampleInput",
        "dump_clause_fixture",
        "load_clause_fixture",
        "map_links",
        "render_link_map",
    }


def test_module_has_its_parts() -> None:
    for name in ("README.md", "tests", "samples", "__main__.py"):
        assert (MODULE / name).exists(), name


def test_readme_names_every_public_name() -> None:
    readme = (MODULE / "README.md").read_text(encoding="utf-8")

    for name in clause_tracer.links.__all__:
        assert name in readme, name
