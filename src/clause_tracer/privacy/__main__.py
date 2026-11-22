"""Run the privacy module alone: python -m clause_tracer.privacy.

Reads the sample privacy fixture, or another one given with --input, and
prints its entities and placeholder text. This is the only place in
`privacy` that reads a file (Constitution S1, S2).
"""

import argparse
import sys
from pathlib import Path

from clause_tracer.core import FakePiiDetector
from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.placeholder import anonymise
from clause_tracer.privacy.render import render_privacy_report
from clause_tracer.privacy.sample_input import load_privacy_fixture

DEFAULT_INPUT = Path(__file__).parent / "samples" / "developer-agreement.privacy.json"
EXIT_INPUT_FILE = 3  # "input file", system design 6.2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clause_tracer.privacy")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args(argv)
    path: Path = args.input

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        print(f"clause_tracer.privacy: cannot read {path}", file=sys.stderr)
        return EXIT_INPUT_FILE

    try:
        case = load_privacy_fixture(text)
    except ValueError as error:
        print(f"clause_tracer.privacy: {error}", file=sys.stderr)
        return EXIT_INPUT_FILE

    suggestions = find_personal_data(case, FakePiiDetector({}))
    entities = group_entities(case.document, suggestions)
    placeholder = anonymise(case.document, entities)
    print(render_privacy_report(case, entities, placeholder), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
