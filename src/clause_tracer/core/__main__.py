"""Run the core module alone: python -m clause_tracer.core.

Labels the Spec 14.5 sample, or another sample file given with --input,
and prints one tab-separated line per position. This is the only place in
core that reads a file (Constitution S1, S2).
"""

import argparse
import sys
import tomllib
from pathlib import Path

from clause_tracer.core.labels import label_all
from clause_tracer.core.sample_input import parse_sample

DEFAULT_INPUT = Path(__file__).parent / "samples" / "spec-14-5.toml"
EXIT_INPUT_FILE = 3  # "input file", system design 6.2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clause_tracer.core")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args(argv)
    path: Path = args.input

    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except OSError:
        print(f"clause_tracer.core: cannot read {path}", file=sys.stderr)
        return EXIT_INPUT_FILE
    except ValueError as error:  # TOMLDecodeError, or bytes that are not UTF-8
        print(f"clause_tracer.core: {error}", file=sys.stderr)
        return EXIT_INPUT_FILE

    try:
        sample = parse_sample(data)
        labels = label_all(sample.playbook, sample.inputs, sample.unreadable)
    except ValueError as error:
        print(f"clause_tracer.core: {error}", file=sys.stderr)
        return EXIT_INPUT_FILE

    topics = {position.id: position.topic for position in sample.playbook.positions}
    for label in labels:
        reasons = ",".join(reason.value for reason in label.reasons) or "-"
        columns = (
            label.position_id,
            topics[label.position_id],
            label.level.value,
            reasons,
            label.written_by.value,
        )
        print("\t".join(columns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
