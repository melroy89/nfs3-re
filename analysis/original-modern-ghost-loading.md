# Original versus Modern: ghost loading and configuration restoration

## Evidence boundary

Static supplied-original/official-Modern comparison, with exact fingerprints and provenance limits in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_ghost_loading_difference.py`; the [manifest](evidence/audits/original-modern-ghost-loading.json) retains paired wrappers, save/header helpers and two byte-identical reader/resolver bodies. No ghost file, game or instruction probe was executed.

## The changed wrapper, not a new file reader

Matched entry `004466a0` takes a ghost resource/path argument in EAX. Both versions save current configuration, invoke `00472820`, pass the argument to `00477b50`, test its result and restore selected current state on success. Their order and byte coverage differ:

| Operation | Original | Official Modern |
|---|---|---|
| Snapshot order | Before calling `00472820` | After calling `00472820` |
| Main snapshot | `006fbb4c`, **0x176c** bytes | `006fbb40`, **0x20f0** bytes |
| Additional snapshot | Two separate 12-byte fields | Included in full block |
| Main successful restore | `006fbb4c`, 0x176c bytes | `006fbb40`, **0x1778** bytes |
| Restore `006fd2dc` / `006fd348` | 12 bytes each | 12 bytes each |
| Additional successful restores | No corresponding copies in this wrapper | Three 11-byte copies described below |

The old and new main restore ranges end at the same exclusive address **`006fd2b8`**. Modern adds the preceding **12-byte header**; it does not restore all 0x20f0 snapshot bytes. Ghost-specific fields outside the listed copies can remain loaded.

Modern uses PUSHAD/POPAD and writes the loader result/success into saved EAX before restoring registers; ordinary success returns 1, loader failure returns zero. Original uses a different explicit-save prologue. Do not infer identical preserved-register contracts from identical entry addresses.

## Header refresh is part of the fix mechanism

Modern `00472820` now calls `004723f0` immediately before its save-admission checks, replacing the original debug-flag check at that position. `004723f0` copies **three DWORDs** from file-backed prefix `0055e8a0` to `006fbb40`.

The wrapper then snapshots that refreshed header. After successful ghost loading, it restores the refreshed header along with the settings prefix. Original's wrapper snapshots only from `006fbb4c` and therefore excludes the first three DWORDs from its outer restoration.

This is concrete support for **MP152-003**'s config-reset fix mechanism: the current header is deliberately re-established and retained instead of leaving that prefix supplied by the ghost. Full header/version validation, every save failure path and actual cross-version reset behavior are not tested here. Restoring header bytes is not a proof that arbitrary ghost data is compatible.

## Player identity fields are explicitly restored

Modern's full snapshot provides these additional copies after a successful load:

| Snapshot offset from `006fbb40` | Destination | Bytes |
|---:|---|---:|
| `0x17bc` | `006fd2fc` | 11 |
| Same `0x17bc` bytes | `006fd560` | 11 |
| `0x1828` | `006fd368` | 11 |

At `004466fe..0044670b`, the first source pointer is restored between copies, so both first and second destinations receive the **same original 11 bytes**. The third uses its own snapshot source. They are raw fixed-length copies; this code does not search for or add a NUL terminator.

Existing [roster research](network-roster-admission.md) independently traces local player-name input from `006fd2fc` into the network name slot. Combined with the newly restored copies, this supports **MP152-004**'s player-name preservation mechanism. The other two fields' full UI/runtime roles and all long-name edge cases remain unresolved; they are not assigned guessed structure member names.

Both wrappers then pass the field at `006fd4ac` to `004cef00`, sign-extend AX and store its result to `006fd2b4` and `006fbb50`. Original obtains that same WORD through a signed shift of the overlapping DWORD at `006fd4aa`; Modern zero-extends the WORD directly. For values with its high bit set, the intermediate EAX differs, so equal ordinary IDs do not establish arbitrary-input equivalence.

## Retained reader and model resolver

The manifest asserts exact equality for complete functions:

- `00477b50..00477bf7`, **168 bytes**: snapshot a settings region, check existence/size, clear/read staging storage at `006ba5c4`, validate/resolve through `00478100`, then copy the 0x20f0-byte preparation block into globals and restore its own 0x176c-byte settings prefix on success.
- `00478100..004781a8`, **169 bytes**: require first DWORD `0x20f0`, iterate prepared car records and resolve/check model indices.

The reader's file-size comparison permits files no larger than `0x41574`; this alone is not complete file-format validation or proof that every read succeeded fully. Model lookup dependencies/data can also differ despite identical resolver bytes.

On failure, the outer wrapper skips its success-only restoration. The inner reader's shown failure paths occur before its global preparation-block copy, but `00472820` has already run. This is not an unconditional rollback transaction; all callee side effects are not reconstructed here.

## Remaining work

Verified: changed snapshot order, refreshed/restored header coverage, three additional identity copies and retained reader/resolver instructions. Pending: complete version/header format, all model/asset dependencies, name-field consumers, read/save failures and runtime ghost playback. Physics/x87 and trajectory compatibility remain separate from settings restoration. Historical release introduction requires older patch binaries; no compatible-replay claim follows from this chapter.
