"""Run the ingest module alone: python -m clause_tracer.ingest.

Reads the sample contract, or another file given with --input, and prints its
clauses and sentences as a tab-separated outline. This is the only place in
`ingest` that reads a file (Constitution S1, S2).
"""

import argparse
import sys
from pathlib import Path

from clause_tracer.core import FileKind, InputError
from clause_tracer.ingest.clauses import split_clauses
from clause_tracer.ingest.outline import render_outline
from clause_tracer.ingest.reading import read_text_file

DEFAULT_INPUT = Path(__file__).parent / "samples" / "developer-agreement.txt"
EXIT_INPUT_FILE = 3  # "input file", system design 6.2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clause_tracer.ingest")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args(argv)
    path: Path = args.input

    kind = FileKind.MARKDOWN if path.suffix.lower() == ".md" else FileKind.TEXT
    try:
        data = path.read_bytes()
    except OSError:
        print(f"clause_tracer.ingest: cannot read {path}", file=sys.stderr)
        return EXIT_INPUT_FILE

    try:
        document = read_text_file(data, kind=kind, name=path.name)
    except InputError as error:
        print(f"clause_tracer.ingest: {error.code}", file=sys.stderr)
        return EXIT_INPUT_FILE

    print(render_outline(document, split_clauses(document)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
