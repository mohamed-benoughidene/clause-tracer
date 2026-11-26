# `cli`

Wires the modules together and is the only place that reads files, prints and starts processes (Spec 9).

## The reply of the child process

The child process reads one file and writes one JSON reply. Both sides of the reply live here, because `core` never imports Pydantic (ADR 0005, system design 15.5).

| Name | What it is |
| --- | --- |
| `ChildDone` | The child read the file: `kind` is `"done"` and `document` is the `Document` it built. |
| `ChildFailed` | The child named an input error: `kind` is `"failed"`, with the error's `code` and its `context`. |
| `encode_child_reply` | Turns a `ChildDone` or a `ChildFailed` into the bytes the child writes to its standard output. |
| `decode_child_reply` | Reads those bytes back. A reply over `MAX_CHILD_REPLY_BYTES` raises `UnreadableFileError` with reason `child_reply_too_large`; bytes that do not validate raise it with reason `child_reply_invalid`. |
| `input_error_for_code` | Rebuilds the `InputError` subclass whose `code` matches, with the given context. An unknown code raises `UnreadableFileError` with reason `child_error_code_unknown`. |
| `MAX_CHILD_REPLY_BYTES` | The largest reply the parent reads: 64 MiB ([Assumption], system design 15.5). |

The reply is JSON and the codec validates it in strict mode. It never uses `pickle` and never evaluates the data. A validation message is never put into an error's context, because it can hold contract text.
