# Original versus Modern Patch: x87 precision

**Verdict:** the local binaries confirm a real precision-policy change. The original/backup executable explicitly selects single precision at six identified control blocks; Modern Patch removes those blocks and uses extended-precision initialization at the inspected application/race-render boundaries. The claim is substantially correct about that change, but its “only menu/HUD”, “80-bit everywhere”, and automatic incompatibility wording is too absolute.

This is read-only static investigation of the two supplied files, not new game, network, replay or ARM64 execution. [Byte witnesses and fingerprints](evidence/audits/og-modern-x87-precision.json) retain the actual differences. Existing Modern Patch reconstruction and raw exports were not changed.

## Exact targets

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Supplied original/backup | `nfs3_org.exe` | 1,589,248 | `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` |
| Local Modern Patch-based target | `nfs3.exe` | 1,699,840 | `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb` |

Both use image base `00400000`, entry `004f7fa0`. The Wine-prefix original supplied by the user matches the project-local ignored original copy byte-for-byte. “Original” here identifies that supplied artifact; its exact retail provenance/version has not been independently authenticated. Modern Patch provenance remains as recorded in [TARGET](../docs/TARGET.md).

The saved Ghidra database still targets Modern Patch. Its function names helped identify the current application, frontend and race-render paths. Original-code conclusions below come from original PE bytes, not from assuming every Modern Patch function boundary/address transfers unchanged to the original.

## What the instructions establish

Intel specifies that FINIT/FNINIT initializes CW to `037f`: exceptions masked, nearest rounding, PC=`11` (64-bit significand in the 80-bit format). PC=`00` selects a 24-bit significand. This controls arithmetic precision, not the size of every value in memory. [Intel architecture manual](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366521.pdf)

At original `00495159..0049517f`:

```text
00495159 FINIT                         ; CW = 037f
0049515c FSTCW [0079f3ec]
00495165 MOV EAX,[0079f3ec]
0049516a MOV [0079f3f4],EAX             ; retain reset/extended CW
0049516f AND EAX,fffff0ff              ; low word 037f -> 007f
00495174 MOV [0079f3ec],EAX
00495179 FLDCW [0079f3ec]              ; PC=00, RC=00
```

The mask clears precision bits 8–9 and rounding bits 10–11, so the resulting low word is **`007f` (single precision, nearest)**, not binary64/double precision. The same reset/save/clear/load sequence appears at original AND sites `004955df`, `004a3e83`, `004a3ec9`, `004b622f`, `004bc807`. No corresponding decoded `AND EAX,fffff0ff` site remains in Modern Patch. These are static instruction witnesses, not observations of every runtime path.

| Boundary | Original executable | Modern Patch executable |
|---|---|---|
| Frontend/application dispatch | `004a3e5a..64` restores saved extended CW before frontend setup; `004a3e6d..93` resets/saves/reselects single after it returns. The second frontend branch repeats this at `004a3e9b..004a3ed9`. | Loop at `004a3ea0` performs FINIT. Frontend calls at `004a3ec6`/`004a3ed7` return to that loop without the original single-precision reset blocks. |
| Loading-artwork path | Original control block above reselects single after rendering. | Current `LoadAndRenderRaceLoadingArtwork` ends at `00495165`; the old reset area is removed/NOP-padded. |
| Race-frame rendering | When flag `[007a3a70]==0`, `004bc692..9c` restores saved extended CW on entry; `004bc7f1..817` reselects single before returning. | `RenderRaceFrame` starts with FINIT at `004bc687`; the old restore/return-to-single code is removed. |

The race-frame witness is important: the original uses extended precision around race rendering as well as frontend work. Therefore “80-bit **only** in menu and HUD” is not an exact description of the inspected control flow. A more accurate summary is **single-precision game-side context with extended-precision frontend/render regions, versus Modern Patch's extended baseline at these boundaries**. Fully labeling every physics, online, replay or worker-thread interval still requires its own call/control-word trace.

The patch's bundled `readme_en.txt`, under v1.6.0 (2016-09-22), line 174, independently documents the intended change: “FPU always uses extended precision for all calculations.” That is patch-author documentation corroborated by the byte changes above, not a blanket runtime measurement.

## Why “80-bit everywhere” is shorthand

Local FPU-control helpers still exist. For example, Modern Patch's `004dfd56..004dfd6c` pushes CW `0c3f`, saves the incoming CW separately, loads the temporary word, executes FRNDINT, then restores the saved word. The temporary word has PC=`00`, but FRNDINT is not one of the arithmetic instructions controlled by PC. This is a scoped conversion/rounding helper, not evidence that normal patched race arithmetic reverts to single precision.

Thus it would be wrong to claim the control word is always `037f`, or that every result is stored in 80 bits. In fact the 747 bytes of the first reconstructed helper `00485c30` are **identical in both executables**, SHA-256 `3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f`. Both retain its binary32 memory accesses. A change in surrounding arithmetic mode can matter without converting all data structures to double or extended storage.

## Assessment of the other user's claims

| Claim | Assessment |
|---|---|
| Modern Patch changes OG's single-precision arithmetic policy toward extended precision. | **Confirmed statically for the inspected controls**, with corroborating patch documentation. |
| OG uses 32-bit precision in all race/online/replay execution and extended only in menus/HUD. | **Overgeneralized.** Single-precision switches are real; race-frame rendering has a conditional extended region too. Every online/replay/worker path has not been traced. |
| Modern Patch uses binary64 `double` everywhere. | **Incorrect description:** the verified baseline is x87 extended (64-bit significand), not binary64 (53-bit significand), and binary32 memory storage remains. |
| A float-everywhere ARM64 port runs without issues. | **Not verified here:** that port's source/binary, test cases and results were not supplied. Running without a crash is also a narrower observation than deterministic equivalence. |
| That port connects but desynchronizes positions/replay trajectories. | **Not verified here.** Numerically plausible, but needs the specific port and a controlled comparison; the inspected binaries alone cannot establish those reported outcomes or their cause. |
| Using native float necessarily makes a port incompatible with both versions. | **Not established.** Native float alone does not reproduce every x87 rule, but compatibility depends on observable arithmetic, timing, serialization and protocol behavior. Neither guaranteed compatibility nor inevitable incompatibility follows solely from the type choice. |

For replay trajectories and simulation-based multiplayer, a useful decisive test is identical recorded inputs against the chosen original binary, comparing state at matched simulation ticks, then testing actual replay/network exchange. For authoritative state exchange, protocol/state reconciliation details also matter. We have not established a universal NFS3 synchronization model or cross-version compatibility from this precision inspection.

## Scope and continuation

No executable, saved Ghidra database, maintained C or raw reference export was changed, and no tests were rerun. The conclusion is the verified **precision-policy difference between these exact two files**, not complete knowledge of Modern Patch or a guarantee about any ARM64 port.

A broader Modern-versus-original audit should remain version-bound and address-mapped: precision/control-word policy first; then separately documented simulation changes, replay/network formats and other patch behavior. Import/analyze the original in a distinct Ghidra program/project if deeper original cross-references are needed; do not replace or reinterpret the current Modern Patch database as original analysis. GUI launch is not required for these headless saved-project inspections.
