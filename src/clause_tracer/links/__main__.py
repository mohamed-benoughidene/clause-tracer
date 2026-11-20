"""Run the links module alone: python -m clause_tracer.links.

Reads the sample clause fixture, or another one given with --input, and
prints its link map. This is the only place in `links` that reads a file
(Constitution S1, S2).
"""

import argparse
import sys
from pathlib import Path

from clause_tracer.links.mapping import map_links
from clause_tracer.links.render import render_link_map
from clause_tracer.links.sample_clauses import SampleInput, load_clause_fixture

DEFAULT_INPUT = Path(__file__).parent / "samples" / "developer-agreement.clauses.json"
EXIT_INPUT_FILE = 3  # "input file", system design 6.2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clause_tracer.links")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args(argv)
    path: Path = args.input

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        print(f"clause_tracer.links: cannot read {path}", file=sys.stderr)
        return EXIT_INPUT_FILE
    except ValueError as error:
        print(f"clause_tracer.links: {error}", file=sys.stderr)
        return EXIT_INPUT_FILE

    try:
        sample: SampleInput = load_clause_fixture(text)
    except ValueError as error:
        print(f"clause_tracer.links: {error}", file=sys.stderr)
        return EXIT_INPUT_FILE

    print(
        render_link_map(
            sample.document,
            sample.clauses,
            map_links(sample.document, sample.clauses),
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
