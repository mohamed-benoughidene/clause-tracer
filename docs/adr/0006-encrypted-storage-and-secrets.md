# ADR-0006: Store reviews in an encrypted SQLite file plus per-review keys

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 8.3](../spec.md) says everything saved is encrypted. The encryption key and the API key live in the system's password store. If Linux has no password store, the app asks for a passphrase and never saves plain text. Spec 9 adds auto-delete after 7, 30 or 90 days, and Spec 11 requires that saved data is unreadable without the key.

The [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) left two designs open: one SQLCipher database, or plain SQLite with per-record AES-GCM blobs. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) corrected it on 11 Nov 2026. `sqlcipher3` no longer relies on a community wheel fork. SQLite3 Multiple Ciphers (`apsw-sqlite3mc`) was missing from the comparison. The runner in [ADR 0005](0005-engine-runner-shapes-and-ports.md) keeps its state in this store. D1 (keep raw data unchanged) and D8 (save the AI's exact reply) mean the store holds contract bytes and raw replies.

## Decision
The project owner accepted a hybrid on 12 Nov 2026. One choice inside it is still open: which of the two SQLite encryption packages to use (action item 6). *Superseded: see the amendment of 12 Nov 2026, which chose `sqlcipher3`.*

- **One encrypted SQLite file** holds the index and small records. The research prefers `apsw-sqlite3mc`, whose Python API differs from the standard `sqlite3` module. `sqlcipher3` is the fallback. The owner has not yet chosen between them.
- **A per-review AES-GCM key** encrypts raw contract bytes and AI replies. A random master key wraps each review key. Deleting a review destroys its key.
- **Associated data.** Each ciphertext passes `review_id|record_id|schema_version` as associated data, so blobs cannot be swapped between records.
- **Pragmas.** `temp_store=2`, `secure_delete` on, `wal_checkpoint(TRUNCATE)` after a delete and on close, and `journal_size_limit=0`. A test reads them back.
- **Secrets.** `keyring` with the backend pinned per OS. It stores only a random 32-byte master key. The fallback is an Argon2id passphrase. Never use a `keyrings.alt` plaintext backend.
- **The claim.** "Encrypted at rest; once its key is destroyed, unreadable by this app." Never "securely erased" or "forensically unrecoverable".

## Options Considered

### Option A: Hybrid, apsw-sqlite3mc plus per-review AES-GCM keys (chosen)
*Superseded: the package is `sqlcipher3`, chosen in the amendment of 12 Nov 2026. The hybrid itself stands.*
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: two layers of encryption and a key table |
| Cost | One SQLite package plus `cryptography`; sizes not measured |
| Scalability | Single user, not a scale question |
| Team familiarity | Med: apsw's API differs from the standard `sqlite3` module |

**Pros:** metadata such as review counts and dates stays encrypted. Deleting a review is real crypto-shredding. The apsw wheel is built with secure delete on and memory temp storage ([apsw-sqlite3mc](https://github.com/utelle/apsw-sqlite3mc)).
**Cons:** a non-standard database API. Its licence file inside the wheel was not read.

### Option B: Hybrid on sqlcipher3
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med |
| Cost | Self-contained wheels since 0.6.2; 0.6.5 appeared on 5 Nov 2026 ([sqlcipher3](https://github.com/coleifer/sqlcipher3)) |
| Scalability | Single user, not a scale question |
| Team familiarity | High: the standard `sqlite3` API |

**Pros:** familiar API and a well-known cipher.
**Cons:** needs a manual `temp_store=MEMORY` setting. Its BSD licence needs an About-screen credit.

### Option C: One SQLCipher database alone
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | One package |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** simplest. Everything, metadata included, is encrypted.
**Cons:** no per-review shredding. Deleted rows leave old pages until VACUUM, and on SSDs VACUUM does not guarantee physical erasure ([Wei and others, FAST 2011](https://www.usenix.org/legacy/event/fast11/tech/full_papers/Wei.pdf)).

### Option D: Plain SQLite index plus per-blob AES-GCM alone
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: careful nonce handling |
| Cost | Only `cryptography` |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** mainstream library and natural per-review keys.
**Cons:** leaks metadata such as review counts and timestamps.

For the passphrase, scrypt from `cryptography` avoids a dependency. The research recommends Argon2id and names scrypt as a close runner-up; its wording on which one lost is unclear, so treat the two as near-equal until action item 2 is done.

## Trade-off Analysis
The package and design facts are verified. The hybrid is judgement. It fixes the weakness of each single design: Option C cannot shred one review, and Option D leaks metadata. With a key per review, random 96-bit nonces stay far below the 2^32 limit in [NIST SP 800-38D](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-38d.pdf). Nonce reuse is still fatal, so tests must cover it. Keyring behaviour is verified; the rest of the secrets design is judgement.

Gaps carried over: the `sqlcipher3` wheel's compile-time temp setting was not checked; per-page authentication in SQLite3MC's default cipher is unverified; whether `secure_delete` acts on WAL frames is untested; whether `cryptography` 50.x ships Argon2id, and its key-wrap API, were not re-fetched; PyInstaller hook support for keyring and Windows size limits were not fetched; the text of NIST SP 800-88 Rev. 2 could not be read.

The honest claim is smaller than "erased", because an app cannot overwrite an SSD block. A backup made earlier still holds the old key, and the docs must say so. Users should keep full-disk encryption on.

## Consequences
- Easier: deleting a review is one key deletion plus a checkpoint, and auto-delete becomes simple and testable with an injected `Clock`.
- Easier: a byte scan with planted canaries can prove the promise ([ADR 0013](0013-test-layers-and-release-gates.md)).
- Harder: two encryption layers, a key table and associated-data rules to keep right.
- Revisit if the canary scan finds plain text in `-wal` or `-journal` files after a simulated crash, or if the chosen wheel lacks the expected temp setting.

## Action Items
1. [ ] Read the licence file inside the `apsw-sqlite3mc` wheel and check SQLite3MC's per-page authentication.
2. [ ] Check whether the pinned `cryptography` ships Argon2id and AES key wrap. If not, decide between `argon2-cffi` and scrypt.
3. [ ] Confirm `keyring` works under PyInstaller on Windows and Linux, and check Credential Manager size limits.
4. [ ] Write tests: pragma read-back, canary byte scan with a positive control, crypto-shredding, and a crash between key deletion and row deletion.
5. [x] Update Spec 8.3 with the honest claim and the backup note, and add matching lines to `docs/ux-copy.md` (done 12 Nov 2026).
6. [ ] Try both `apsw-sqlite3mc` and `sqlcipher3` on Linux and in Windows CI, then bring the choice to the owner.

## Amendment (12 Nov 2026): the SQLite encryption package is `sqlcipher3`

The owner chose **`sqlcipher3`** on 12 Nov 2026. This closes action item 6 for Linux.

Both packages were run through the same test on Debian 13 with Python 3.13 that day (`sqlcipher3` 0.6.5 and `apsw-sqlite3mc` 3.54.0.0). A marker string was written to an encrypted database in write-ahead-log mode, and every file on disk was searched for it.

| Check | `sqlcipher3` | `apsw-sqlite3mc` |
| --- | --- | --- |
| Marker found in the database or log files | No | No |
| Wrong key, or no key | Refused | Refused |
| Temporary storage compiled to memory (`TEMP_STORE=2`) | Yes | Yes |
| Secure delete on | Yes | Yes |
| Positive control: plain SQLite shows the marker | Yes, so the scan works | |

The research preferred `apsw-sqlite3mc` because it keeps temporary data in memory and has secure delete on. The test shows `sqlcipher3` does both too, so that reason no longer separates them. `sqlcipher3` wins because its interface matches Python's standard `sqlite3` module, which the developer and the agents already know.

Still to do: run the same test in Windows CI; add the SQLCipher credit to the About screen; note that a wrong key makes SQLCipher print errors to standard error, which must not reach the log with any contract text (it carries none in the test). `apsw-sqlite3mc` stays the fallback. If it is ever used, set its cipher explicitly: its default (ChaCha20-Poly1305) checks each page, but the AES-CBC option in its README does not.

## Amendment (13 Nov 2026): the store checks pass on Windows

The leak test from 12 Nov was run on GitHub's Windows Server 2025 and 2022 runners with `sqlcipher3` (SQLCipher 4.20.0). A marker string written to the encrypted file was found nowhere on disk, while open or after closing, including the write-ahead files. A wrong key and no key were both refused. A round trip through the Windows key store (`keyring`, WinVault backend) worked. The same script passes on Debian 13 with the Secret Service backend. Not tested: a real user desktop, and the passphrase fallback.
