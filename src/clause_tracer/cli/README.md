# `cli`

Wires the modules together and is the only place that reads files, prints and starts processes (Spec 9).

## The child process

The parent never reads a contract in its own process. It starts a child, gives it the bytes and reads one reply, so that a hostile file cannot take the app down with it.

| File | What it does |
| --- | --- |
| `child_runner.py` | Starts the child, writes the bytes to its standard input, reads its reply inside a time limit and turns the outcome into a `Document` or a named error. |
| `_child.py` | The child: sets the memory limit, reads one file with `ingest.read_file` and writes one reply. |
| `_limits.py` | `apply_limits(memory_bytes)`: sets the memory limit on this system, or raises. It never catches its own error (fail closed). |
| `_limits_windows.py` | The Windows job object that limits committed memory. It is importable on every system. |
| `child_reply.py` | The reply codec, shared by both sides. |
| `child_limits.py` | `CHILD_TIMEOUT_S` (60 s) and `CHILD_MEMORY_BYTES` (1 GiB). Both are `[Assumption]` values, tuned in testing. |

### The reply protocol

The parent starts the child with a list of arguments, never a shell:

```
python -I -m clause_tracer.cli._child --memory-bytes <bytes> --name <name>
```

It writes the file bytes to the child's standard input in a daemon thread and closes it. The child reads at most `MAX_FILE_BYTES + 1` bytes. Its first action after parsing the arguments is `apply_limits`; only then does it import `core`, `child_reply` and `ingest`, so the memory that those libraries use counts against the limit.

The child writes one JSON reply to standard output and returns 0 for a document and for a named input error. A `MemoryError` becomes `ChildFailed` with reason `memory`. A reply that cannot be encoded becomes `ChildFailed` with reason `child_reply_unencodable`. Any other exception is not caught, and the process ends with exit code 1.

The parent reads at most `MAX_CHILD_REPLY_BYTES + 1` bytes. A longer reply is refused with reason `child_reply_too_large`, and the child is killed and waited for.

### The outcome table

| What happened | What the parent raises |
| --- | --- |
| The time limit fired | `UnreadableFileError`, reason `too_slow` |
| The child exited with a code other than 0 | `UnreadableFileError`, reason `child_crashed`, with `exit_code` |
| The reply is a `ChildDone` | No error: the document is returned |
| The reply is a `ChildFailed` | The `InputError` whose code it names |
| The reply is empty, has an extra key, holds a non-finite number or names another schema version | `UnreadableFileError`, reason `child_reply_invalid` |
| The reply is longer than `MAX_CHILD_REPLY_BYTES` | `UnreadableFileError`, reason `child_reply_too_large` |

The parent always waits for the child, so none is left running.

### Memory on Linux and Windows

On Linux, `apply_limits` sets `RLIMIT_AS`, which limits address space. On Windows, `_limits_windows` puts the process in a job object and limits committed memory. The same figure therefore means different things on the two systems. On any other system the child stops with `OSError`, because there is no limit it can set.

### Not a sandbox

The child is not a security sandbox. It sets a limit on itself, and a parser exploit can lift that limit. The limit protects the app from a file that is slow or greedy, not from an attacker who can run code.

### The frozen build

The frozen build does not dispatch `--read-child` yet. It answers that argument in stage 12; until then, `child_command` builds the command that stage 12 will serve.

## The reply of the child process

The child process reads one file and writes one JSON reply. Both sides of the reply live here, because `core` never imports Pydantic (ADR 0005, system design 15.5).

| Name | What it is |
| --- | --- |
| `ChildDone` | The child read the file: `kind` is `"done"` and `document` is the `Document` it built. |
| `ChildFailed` | The child named an input error: `kind` is `"failed"`, with the error's `code` and its `context`. |
| `encode_child_reply` | Turns a `ChildDone` or a `ChildFailed` into the bytes the child writes to its standard output. |
| `decode_child_reply` | Reads those bytes back. A reply over `MAX_CHILD_REPLY_BYTES` raises `UnreadableFileError` with reason `child_reply_too_large`; bytes that do not validate, or a document with another schema version, raise it with reason `child_reply_invalid`. |
| `input_error_for_code` | Rebuilds the `InputError` subclass whose `code` matches, with the given context. An unknown code raises `UnreadableFileError` with reason `child_error_code_unknown`. |
| `MAX_CHILD_REPLY_BYTES` | The largest reply the parent reads: 64 MiB ([Assumption], system design 15.5). |

The reply is JSON and the codec validates it in strict mode, with no extra key and no non-finite number. It never uses `pickle` and never evaluates the data. A validation message is never put into an error's context, because it can hold contract text.
