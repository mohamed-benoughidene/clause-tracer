"""The child process: read one file under limits (S5-M2-T6).

Only the standard library and `_limits` are imported at the top. The
libraries that `ingest` loads are imported inside `main`, after
`apply_limits` has run, so their memory counts against the limit (system
design 15.5: the limit is the child's first action).
"""

import argparse
import sys
from collections.abc import Sequence
from typing import BinaryIO

from clause_tracer.cli._limits import apply_limits


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | None = None,
) -> int:
    """Read one file and write one reply."""
    parser = argparse.ArgumentParser(prog="clause-tracer-child")
    parser.add_argument("--memory-bytes", type=int, required=True)
    parser.add_argument("--name", type=str, required=True)
    args = parser.parse_args(argv)

    apply_limits(args.memory_bytes)

    from clause_tracer.cli.child_reply import ChildDone, ChildFailed, encode_child_reply
    from clause_tracer.core import InputError
    from clause_tracer.ingest import read_file
    from clause_tracer.ingest.limits import MAX_FILE_BYTES

    source = stdin if stdin is not None else sys.stdin.buffer
    target = stdout if stdout is not None else sys.stdout.buffer
    data = source.read(MAX_FILE_BYTES + 1)

    try:
        document = read_file(data, name=args.name)
    except InputError as error:
        target.write(encode_child_reply(ChildFailed(code=error.code, context=dict(error.context))))
        return 0
    except MemoryError:
        target.write(
            encode_child_reply(ChildFailed(code="unreadable_file", context={"reason": "memory"}))
        )
        return 0

    try:
        reply = encode_child_reply(ChildDone(document=document))
    except ValueError:
        target.write(
            encode_child_reply(
                ChildFailed(
                    code="unreadable_file",
                    context={"reason": "child_reply_unencodable"},
                )
            )
        )
        return 0

    target.write(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
