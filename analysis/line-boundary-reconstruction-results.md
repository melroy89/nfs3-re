# First line-boundary C module: bounded results

**Implemented and functionally tested:** only `00485c30`, using a standalone Windows i686 test executable plus a native Linux i386 differential harness. This is not a reconstructed game or a qualified live replacement. [Maintained source and run commands](../reconstruction/README.md), [curated evidence](evidence/audits/line-boundary-reconstruction.json), [prior reference exports](reference-export-results.md).

## Scope and implementation

`reconstruction/line_boundary.c/.h` defines an ordinary C test function and one shared eight-byte binary32 result pair corresponding to `00791c08/00791c0c`. It preserves policy-zero returns, BYTE-mask OR behavior, write-before-rejection and shared scratch lifetime. It does not add validation, thread-local storage, locking or canonical geometry fixes.

The translation follows the saved instruction contract rather than compiling the raw decompiler output: explicit binary32 difference/slope/intercept stores; extended live x87 intermediates; first lower-bound comparisons consuming the unrounded FST-retained value, followed by upper-bound comparisons reloading binary32 scratch; branch-specific unordered predicates. No generic `ABS()` macro, undefined scratch type or raw exported alias identifier was retained.

The selected implementation/build contract is GCC x87, O0, CW `037f`, valid aligned nonaliasing synthetic buffers and serialized calls. Static assertions require 8-bit bytes, 32-bit policy, IEEE binary32 and 64-significand-bit x87 extended `long double`. Other compilers, optimizations, control words and overlapping buffers are not qualified.

## Build and differential evidence

| Layer | Cases and observations | Outcome |
|---|---|---|
| Native Linux i386 | Original 40 ordered fixture rows, eight directed noninteger rows and 256 fixed-seed finite rows; original unmodified instructions at their original VAs versus compiled maintained C | **304/304 exact functional matches** |
| Windows i686 under Wine 9.0 | Standalone MinGW PE and original register adapter; same 40 retained fixture rows, independent scratch sequences | **40/40 exact functional matches** |
| Return/storage and data | Null versus expected shared pointer identity, both scratch raw words, BYTE mask; candidate/line/bounds checked unchanged; canaries intact | **Passed in the stated harness scopes** |
| FPU control word | Both implementations reset with FNINIT then load `037f` per call | **0 CW differences** in either suite |
| x87 status word | Raw SW sampled after calls | **Not equal:** 252/304 native and 32/40 Windows rows differ |
| Original oracle crosscheck | Both new original runners compared to all 40 retained original records, including scratch, mask, CW and SW | **Exact matches** |

Observed SW XORs are only `0100`, `4000`, or `4500` (condition-code bits C0/C2/C3); sampled exception bits and TOP show zero differences. This narrows the discrepancy for these cases, but is not proof that complete FPU tags/registers, unmasked exceptions or all future calls agree. No status mismatch was hidden or treated as full machine equivalence.

The native harness records individual input words and checks them after both implementations. Windows checks its input array snapshot and surrounding canaries; native also guards the BYTE-mask neighborhood. Neither suite admits arbitrary pointer overlap or measures actual caller scheduling/lifetime.

The Windows compiler is the user-local Ubuntu MinGW i686 POSIX build (`13-posix`, package `13.2.0-6ubuntu1+26.1`); MinGW headers are 11.0.1 and binutils 2.41.90. The executable runs under Wine 9.0 in a dedicated ignored prefix, not the NFS3 game prefix. C11/O0, x87, no fast math, contraction off, rounding-math and standard excess-precision flags are recorded with full commands/artifact hashes. No native Windows machine was tested. The maintained object has no unresolved library symbols; CRT/Windows imports belong to the standalone test harness.

## Windows oracle relocation

Fixed mappings at `00480000`/`00790000` failed under Wine with error 487. The test instead allocates private code/scratch mappings, verifies all 29 original scratch operands, and relocates only those operands. Their offsets exactly match the selected function's PE HIGHLOW relocation entries. Relative control flow is unchanged; the on-disk executable and original 747-byte artifact retain their original hashes. The adapter uses EAX candidate, EDX line, EBX bounds, ECX policy and a pushed mask pointer, accounts for RET4, and preserves its CRT caller's callee-saved registers.

This relocation is a test-environment adaptation, not an executable patch or proof of the original Windows loader behavior. Private code is finalized read/execute and the instruction cache is flushed before the call. The original instruction artifact SHA-256 remains `3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f`.

## Ghidra documentation and type updates

The user-opened `nfs3_decomp` session was used to type `00791c08` and `00791c0c` as four-byte floats, based on their verified FLD/FST/FSTP accesses, without changing storage or bytes. Existing global names were retained; the plugin's naming-prefix check needed a per-call override for those legacy names. Refreshed pseudocode no longer has the overlapping-smaller-symbol warning; the unknown-custom-convention warning correctly remains.

The `00485c30` plate records test scope/results, extended/reloaded comparison behavior and the outstanding machine-state/integration gates. Save and live comment readback matched. The program was closed after saving to produce a consistent checkpoint; the program was initially reopened after validation. The latest follow-up checkpoint (`db.3146.gbf`) was then saved with Ghidra closed normally, independently reopened read-only, and committed; Ghidra is left closed to keep that checkpoint stable. Saved-database identity and isolated readback are recorded in the curated evidence. No other functions, game configuration or executable bytes were changed.

## Acceptance and next work

- **Done:** one maintained C leaf and address-to-symbol map, separate from generated references.
- **Done:** MinGW i686 standalone compilation/linking and Wine execution; native i386 differential testing.
- **Done:** exact functional comparison over the stated cases, input/canary checks, CW checks and explicit SW discrepancy records.
- **Done:** Ghidra scratch types/comments, save/readback and unchanged original executable.
- **Later — machine-state/runtime validation:** resolve which x87 condition bits/flags/tags callers require; reproduce them or justify a narrower interface before any game-facing replacement.
- **Later — expanded runtime scope:** alternate control words/exception modes, other optimizations/compilers, aliases/reentrancy and actual caller integration need their own evidence. Native Windows and a production Linux port remain untested.

No other reference sample or unrelated scratchpad investigation was reconstructed. The standalone functional slice is complete; full ABI/machine equivalence and integration remain separate gates.


## Static caller-dependence follow-up

A subsequent [read-only caller audit](line-boundary-x87-callers.md) found no direct C0/C2/C3 consumption at the six known helper callsites. Multiple returns propagate those bits, and bounded HUD ancestor paths reach unreviewed render/transform callees or outer returns. This narrows the limitation but does not clear it globally or qualify a game-facing replacement. The follow-up inspected saved instructions and retained results; it did not rerun these tests or change the maintained C, raw exports, executable or Ghidra database.
