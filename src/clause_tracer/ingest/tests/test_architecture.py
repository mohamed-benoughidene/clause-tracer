"""The module's public shape (S2-M5-T5)."""

import ast
import shutil
from pathlib import Path

import clause_tracer.ingest

MODULE = Path(__file__).parent.parent
PACKAGE = MODULE.parent
SRC = MODULE.parent.parent
REPO = SRC.parent
SCRIPTS = REPO / "scripts"

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
    """Return the files outside a `tests` folder, judged below `root` only."""
    return sorted(
        path for path in root.rglob("*.py") if "tests" not in path.relative_to(root).parts
    )


def _runtime_importers(package: Path) -> dict[str, list[str]]:
    """Return, for each runtime library, the files of the package that import it."""
    importers: dict[str, list[str]] = {name: [] for name in RUNTIME_LIBRARY_FILES}
    for path in _python_files(package):
        for name in _imported_names(path) & set(RUNTIME_LIBRARY_FILES):
            importers[name].append(path.relative_to(package).as_posix())
    return importers


def test_importers_allow_the_stated_files(tmp_path: Path) -> None:
    # The copy sits under a folder named `tests`, so only a `tests` folder
    # inside the package may count.
    package = tmp_path / "tests" / "clause_tracer"
    shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
    imports = {"pypdfium2": "pypdfium2", "pikepdf": "pikepdf", "lxml": "lxml.etree"}
    for library, file in RUNTIME_LIBRARY_FILES.items():
        (package / file).write_text(f"import {imports[library]}\n", encoding="utf-8")
    in_tests = "".join(f"import {module}\n" for module in imports.values())
    (package / "ingest" / "tests" / "imports_all.py").write_text(in_tests, encoding="utf-8")

    assert _runtime_importers(package) == {
        library: [file] for library, file in RUNTIME_LIBRARY_FILES.items()
    }


def test_runtime_libraries_have_one_importer() -> None:
    importers = _runtime_importers(PACKAGE)

    for library, allowed_file in RUNTIME_LIBRARY_FILES.items():
        found = importers[library]
        assert found == [] or found == [allowed_file], (
            f"{library} is imported by {found}, not only {allowed_file}"
        )


def test_dev_tools_stay_in_tests() -> None:
    offenders: list[str] = []
    paths = sorted(SRC.rglob("*.py")) + sorted(SCRIPTS.rglob("*.py"))
    for path in paths:
        relative = path.relative_to(REPO)
        in_tests = "tests" in relative.parts
        in_scripts = relative.parts[0] == SCRIPTS.name
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
        "read_file",
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
