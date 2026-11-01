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
