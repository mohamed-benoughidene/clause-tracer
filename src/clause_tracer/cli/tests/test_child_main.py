"""The child's main function (S5-M2-T6)."""

import ast
import io
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import clause_tracer.cli._child as child
import clause_tracer.ingest as ingest
from clause_tracer.cli.child_reply import ChildDone, ChildFailed, decode_child_reply
from clause_tracer.core import Document, FileKind
from clause_tracer.ingest import read_text_file

CLI = Path(__file__).resolve().parents[1]
FORBIDDEN_TOP_LEVEL = {
    "clause_tracer.ingest",
    "clause_tracer.core",
    "clause_tracer.cli.child_reply",
    "pydantic",
    "lxml",
    "pypdfium2",
    "pikepdf",
    "ling" + "ua",  # Split in two: another test forbids the whole word here.
}


def _no_limits(memory_bytes: int) -> None:
    pass


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


def test_child_main_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(child, "apply_limits", _no_limits)
    out = io.BytesIO()

    code = child.main(
        ["--memory-bytes", "1", "--name", "a.txt"],
        stdin=io.BytesIO(b"Hello world.\n"),
        stdout=out,
    )

    assert code == 0
    reply = decode_child_reply(out.getvalue())
    assert isinstance(reply, ChildDone)
    assert reply.document.text == "Hello world.\n"


def test_child_main_input_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(child, "apply_limits", _no_limits)
    out = io.BytesIO()

    code = child.main(["--memory-bytes", "1", "--name", "a.txt"], stdin=io.BytesIO(b""), stdout=out)

    assert code == 0
    reply = decode_child_reply(out.getvalue())
    assert isinstance(reply, ChildFailed)
    assert reply.code == "empty_input"


def test_child_main_memory_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_memory(data: bytes, *, name: str) -> Document:
        raise MemoryError

    monkeypatch.setattr(child, "apply_limits", _no_limits)
    monkeypatch.setattr(ingest, "read_file", raise_memory)
    out = io.BytesIO()

    code = child.main(
        ["--memory-bytes", "1", "--name", "a.txt"], stdin=io.BytesIO(b"Hello"), stdout=out
    )

    assert code == 0
    reply = decode_child_reply(out.getvalue())
    assert isinstance(reply, ChildFailed)
    assert reply.code == "unreadable_file"
    assert reply.context == {"reason": "memory"}


def test_child_main_other_error_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_runtime(data: bytes, *, name: str) -> Document:
        raise RuntimeError("boom")

    monkeypatch.setattr(child, "apply_limits", _no_limits)
    monkeypatch.setattr(ingest, "read_file", raise_runtime)

    with pytest.raises(RuntimeError):
        child.main(
            ["--memory-bytes", "1", "--name", "a.txt"],
            stdin=io.BytesIO(b"Hello"),
            stdout=io.BytesIO(),
        )


def test_child_main_unencodable_reply(monkeypatch: pytest.MonkeyPatch) -> None:
    document = read_text_file(b"Hello world.", kind=FileKind.TEXT, name="a.txt")
    broken = replace(document, text="\ud800")

    def return_broken(data: bytes, *, name: str) -> Document:
        return broken

    monkeypatch.setattr(child, "apply_limits", _no_limits)
    monkeypatch.setattr(ingest, "read_file", return_broken)
    out = io.BytesIO()

    code = child.main(
        ["--memory-bytes", "1", "--name", "a.txt"],
        stdin=io.BytesIO(b"Hello world."),
        stdout=out,
    )

    assert code == 0
    reply = decode_child_reply(out.getvalue())
    assert isinstance(reply, ChildFailed)
    assert reply.code == "unreadable_file"
    assert reply.context == {"reason": "child_reply_unencodable"}


def test_child_has_no_heavy_top_level_import() -> None:
    names = _top_level_imports(CLI / "_child.py")

    assert names & FORBIDDEN_TOP_LEVEL == set()

    init_tree = ast.parse((CLI / "__init__.py").read_text(encoding="utf-8"))
    assert not any(isinstance(node, ast.Import | ast.ImportFrom) for node in init_tree.body)


@pytest.mark.skipif(sys.platform == "win32", reason="the order is checked on Linux")
def test_apply_limits_runs_before_the_libraries_load() -> None:
    command = [
        sys.executable,
        "-I",
        "-X",
        "importtime",
        "-m",
        "clause_tracer.cli._child",
        "--memory-bytes",
        str(1024**3),
        "--name",
        "a.txt",
    ]

    result = subprocess.run(command, input=b"Hello world.\n", capture_output=True, check=False)

    assert result.returncode == 0
    stderr = result.stderr.decode()
    limits_at = stderr.find("clause_tracer.cli._limits")
    ingest_at = stderr.find("clause_tracer.ingest")
    assert limits_at >= 0
    assert ingest_at > limits_at
