"""Command-line entry point: clause-tracer."""

import argparse
from collections.abc import Sequence

from clause_tracer import __version__


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clause-tracer", description="Local-first contract review."
    )
    parser.add_argument("--version", action="version", version=f"clause-tracer {__version__}")
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
