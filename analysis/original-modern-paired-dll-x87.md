# Paired DLL x87 control-site comparison

## Scope and reproduction

This compares the four identified [author-reference/final DLL pairs](original-modern-original-reference-bundle.md): DX5, software, sound and Glide. The reference bundle is mixed and not authenticated pristine retail; in particular its Glide member differs from the previously studied local legacy candidate. Their exact identities and semantic findings remain in the [DX5](original-modern-dx5-reference-pair.md), [software](original-modern-software-reference-pair.md), [sound](original-modern-sound-reference-pair.md) and [Glide](original-modern-glide-reference-identity.md) reports.

Run `python3 analysis/scripts/audit_paired_dll_x87_sites.py`. The [script](scripts/audit_paired_dll_x87_sites.py) verifies both archive hashes and all eight DLL hashes before GNU objdump linear decoding. [Manifest](evidence/audits/paired-dll-x87-sites.json) records every matched VA, instruction encoding/operand text and a context hash covering32 bytes before and32 after the instruction. It uses temporary files only; no DLL or instruction is executed.

## Verified static result

| Pair | Primary control candidates per side | Environment-state candidates per side | Sites, encodings and short contexts |
|---|---:|---:|---|
| DX5 |31 |2 |Identical |
| Software |23 |1 |Identical |
| Sound |20 |2 |Identical |
| Hosted-reference Glide / final |28 |1 |Identical |
| **Total** | **102** | **6** | **Identical** |

Primary search mnemonics are FLDCW, FNSTCW/FSTCW and FNINIT/FINIT. The separate environment-state search also covers FLDENV, FNSTENV/FSTENV, FRSTOR, FNSAVE/FSAVE, FXRSTOR/FXSAVE and LDMXCSR/STMXCSR. Its six matches here are FSAVE/FRSTOR candidates; all are retained at the same addresses with identical short contexts. The manifest preserves those separately instead of pretending that restoring an entire FPU environment is merely a control-word load.

These are **linear-decoding candidates**, not102 executed transitions,102 functions, or a proof that every decoded byte lies on a valid path. The additional context comparison is stronger than matching an isolated opcode but weaker than whole-function/caller/dataflow analysis. Overlapping context windows are not independent coverage units.

## What this adds to the precision investigation

For these four pinned pairs, the selected control/environment instruction sites and nearby bytes do not supply a new Modern-only control-word implementation change. This narrows the earlier package-only inventory, which lacked distinct older-side candidates. The sound pair independently has identical entire existing raw code/data sections, a stronger implementation-byte result for that component.

It does **not** establish equal runtime control words. The [EXE precision comparison](og-modern-x87-precision.md) still establishes removal of selected original single-precision scopes and changed FINIT boundaries. Identical DLL code can inherit different incoming state from that EXE, save/restore different words, read changed runtime storage or invoke a different provider. The Glide pair also has initialized-data differences outside these short contexts; no equality of every loaded operand or later writer is inferred.

The separate [DX8 rounding contract](original-modern-packaged-x87.md#verified-dx8-pair-changes-rounding-bits-preserving-precision-bits) remains a separately scoped final-package analysis. Historical1.6.0/1.6.1 renderer comparisons also retain their own evidence boundaries. DX6/DX7/DX8, nGlide/dgVoodoo providers, packed components, system libraries and external threads are not silently added to these four pairs.

A global statement such as “every component uses one fixed80-bit policy” still exceeds the evidence. Precision-control bits, rounding-control bits, memory widths, extended temporaries, environment restoration and actual caller/provider selection are separate contracts. No replay/multiplayer equivalence or trajectory difference follows from these candidate counts.

## Acceptance and next gate

- **Done:** archive/member identity, full specified mnemonic inventory in each decoded pair, exact site/encoding equality, short-context equality and retained environment-state candidates.
- **Pending:** reachability/complete contracts for remaining candidates, live operand/control state, indirect/runtime components, exceptional/unbalanced restoration paths and numerical comparison in a stated scope.
- **Not run:** DLL loading, game/API calls, new instruction probes, reconstruction or compilation.

Two successful runs produced identical manifests. Existing EXEs, saved Ghidra database, maintained C and raw exports were preserved. This bounded comparison does not complete the overall original/Modern investigation.

## nGlide adapter page flip retains the same x87 boundary

The `drivers/nglide/voodoo2a.dll` members in the retained 1.5.3
and final archives export `_THRASH_pageflip@0` at `60002890`.
Their DLL SHA-256 values are
`a7f8831bb5e78fcab34714612722201a711868ffe4d2d45c11a86d677cdfcaeb`
and `f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b`.
The entire 65-byte span `60002890..600028d1` matches.

This export polls the provider through slot `600110c0` with
selector `14h`, compares the output with `6000fcd8` and has
a four-million-iteration countdown. It then calls provider
slot `60011034` once. The wrapper itself has no x87 instruction
and does not save or restore the control word around either provider
call. This narrows the precision question to the caller's incoming
state and the provider's behavior for this handoff. It does not
establish what the provider does or how long the poll takes.
See the [executable precision transition](og-modern-x87-precision.md).

The actual packaged nGlide provider, `drivers/nglide/glide3x.dll`,
and `drivers/nglide/thrash.ini` are each byte-identical across
1.5.3, 1.6.0, and 1.6.1. Extracting each member with `7z x -so`
gives SHA-256
`87842a85d1bfda4217e691a9d4412915c74905eed818c5a727e2f2d6b814edb6`
for the DLL and
`e2c4e128a3c9dd7fb6cddf10a83e29613f70c392e8b938eac0577a66ff98022c`
for the INI. The provider exports `_grGet@12` and
`_grBufferSwap@4` as direct jumps from `10001096` and
`100011c2` to `10008950` and `10009190`, respectively.

The 1.6.0 executable's x87 transition therefore has no matching
replacement of this packaged provider or its INI. The static
identities leave open the actual loaded DLL, provider-internal
control-word behavior, and differences in the state supplied by
each executable.

### nGlide swap arithmetic uses the current precision and scopes truncation

In that common provider, the swap path uses `FILD`, `FDIVR` and
`FIMUL` at `100091f5..10009203`, then calls conversion helper
`100c02d0`. No control-word load separates those arithmetic
instructions. The helper saves the current word at `100c02d6`,
sets rounding bits 10 and 11 through `OR AH,0ch`, converts through
`FISTP` to a 64-bit integer, and restores the saved word at
`100c02ec` on ordinary return. It leaves the precision bits
unchanged. The caller adds the low DWORD of the converted result
to its saved counter value at `10009219`.

This establishes an explicit temporary truncation scope inside
the provider even though the adapter page-flip wrapper has none.
The arithmetic before conversion uses the precision in effect
at that point. Earlier provider calls and later indirect calls
remain outside the trace, so this does not establish preservation
of the caller's control word across the entire swap. No timing
or floating-point state was observed at runtime.

The arithmetic feeds a conditional wait before the graphics call
at `1000926b`. The binary32 constant at `100fd034` is exactly
1000.0. The provider zero-extends the DWORD from `1f2972c4` into
the 64-bit operand for FILD, divides 1000.0 by it, multiplies by
the signed swap argument, and truncates. It adds the low DWORD
of that result to the saved counter, with a further increment on
the conditional path at `1000922e`.

At `10009248..1000925c`, the code compares the callback's current
counter with that target using signed comparisons. It polls while
the result is below the target and the gate at `13262148` equals 1.
Another branch can bypass the wait. The follow-up callback result
is stored at `1f00ec74` before the graphics call. A precision
difference that changes the truncated integer can therefore change
the wait target on this path. The counter's units, callback identity
and actual timing remain unverified. This trace establishes a
presentation wait and leaves its relationship to simulation timing open.

The provider's PE import table resolves the polling callback at
`1f9f0824` to **WINMM.timeGetTime**, also reached by thunk
`100c0080`. The target compared at `1000924a` and `10009258`
therefore uses millisecond clock readings. The signed comparisons
are visible in the instructions. They do not implement a separate
wrap-safe elapsed-time comparison in this loop.

The divisor is a saved value. At `1000355b..10003571` the provider
copies `1f01699c` to `1f2972c4` before replacing the former with
EDX. Swap reads the saved value for arithmetic and the live value
for the equality check at `1000922f`. A reconstruction should
preserve that distinction. Complete refresh-rate provenance and
the measured effect of this wait on game timing remain open.
