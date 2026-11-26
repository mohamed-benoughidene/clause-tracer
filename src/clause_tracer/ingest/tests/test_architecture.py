"""The module's public shape (S2-M5-T5)."""

import ast
from pathlib import Path

import clause_tracer.ingest

MODULE = Path(__file__).parent.parent
SRC = MODULE.parent.parent
SCRIPTS = SRC.parent / "scripts"

RUNTIME_LIBRARY_FILES = {
    "pypdfium2": "ingest/_pdfium.py",
    "pikepdf": "ingest/_layers.py",
    "lxml": "ingest/_xml.py",
}
DEV_TOOLS = ("reportlab", "PIL", "pdfplumber")


def _imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module.split(".")[0])
    return names


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "tests" not in path.parts)


def test_runtime_libraries_have_one_importer() -> None:
    importers: dict[str, list[str]] = {name: [] for name in RUNTIME_LIBRARY_FILES}
    for path in _python_files(SRC):
        for name in _imported_names(path) & set(RUNTIME_LIBRARY_FILES):
            importers[name].append(path.relative_to(SRC).as_posix())

    for library, allowed_file in RUNTIME_LIBRARY_FILES.items():
        found = importers[library]
        assert found == [] or found == [allowed_file], (
            f"{library} is imported by {found}, not only {allowed_file}"
        )


def test_dev_tools_stay_in_tests() -> None:
    offenders: list[str] = []
    paths = sorted(SRC.rglob("*.py")) + sorted(SCRIPTS.rglob("*.py"))
    for path in paths:
        in_tests = "tests" in path.parts
        in_scripts = SCRIPTS in path.parents
        if in_tests or in_scripts:
            continue
        for name in _imported_names(path) & set(DEV_TOOLS):
            offenders.append(f"{path} imports {name}")

    assert offenders == []


def test_public_names() -> None:
    assert set(clause_tracer.ingest.__all__) == {
        "DOCUMENT_SCHEMA_VERSION",
        "NUMBERING_NUMBERS",
        "NUMBERING_PARAGRAPHS",
        "WARNING_NOT_ENGLISH",
        "read_pasted_text",
        "read_text_file",
        "split_clauses",
    }


def test_readme_names_every_public_name() -> None:
    readme = (MODULE / "README.md").read_text(encoding="utf-8")

    for name in clause_tracer.ingest.__all__:
        assert name in readme, name


def test_module_has_its_parts() -> None:
    for name in ("README.md", "tests", "samples", "__main__.py"):
        assert (MODULE / name).exists(), name
