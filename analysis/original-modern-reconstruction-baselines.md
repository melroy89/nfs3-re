# Reconstruction samples: what can be reused across executable baselines

## Three-way byte identity

The [sample audit](scripts/audit_reconstruction_baseline_samples.py) checks the current supplied original, official Modern and local analysis executable against their pinned full-file hashes. It then independently reads the three selected reference functions. The [manifest](evidence/audits/reconstruction-baseline-samples.json) records every address, half-open extent and digest.

| Entry | Existing analysis name | End exclusive | Bytes | Result across all three files |
|---|---|---|---:|---|
| `00485c30` | CalculateLineBoundaryIntersectionCandidate | `00485f1b` | 747 | Identical |
| `004abd9c` | ComputeTyreTuningWeatherResponseScale | `004ac027` | 651 | Identical |
| `00518640` | MoveBytesWithOverlapAndSegmentSetup | `0051868d` | 77 | Identical |

These are matched instruction bodies at the original sample addresses, with original entries independently present in the earlier autoanalysis inventory. Names and custom Ghidra signatures remain maintained analysis metadata. Equal bytes do not prove that every original caller supplies the same values or expects the same incidental outputs.

## Relocations, constant storage and retained oracle

For `00485c30`, all **29 HIGHLOW relocation operand sites** within its body are present at the same addresses in all three files. The retained `analysis/captures/line-boundary-windows/original_00485c30.bin` is exactly the same747 bytes as every baseline's function body, SHA-256 `3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f`. The check reads this artifact; it does not regenerate, relocate or execute it.

For the tyre sample, all **104 file-backed bytes** at `0053dd4c..0053ddb4` match across the three files. This half-open envelope includes the final DWORD read at `0053ddb0`; writing an ambiguous endpoint at that last operand address would omit its four bytes. This establishes the selected table's file identity, not immutability after startup or complete vehicle/global data equivalence.

The byte helpers' preserved segment/DF behavior and the leaf's shared scratch still require the [readiness contracts](recompilation-readiness.md). The leaf has no file-backed constant table; its scratch at `00791c08/0c` is runtime storage. Matching relocation sites do not establish identical loader/startup contents there.

## Scope of research reuse

The existing [two-run reference exports](reference-export-results.md), [register contracts](recompilation-readiness.md#2-interfaces-and-register-contracts) and [line-boundary reconstruction results](line-boundary-reconstruction-results.md) remain useful when selecting an original or Modern baseline. In particular, the retained instruction oracle is no longer merely assumed to represent the same original function: its code bytes are directly matched to both versions.

Under identical harness input bytes, scratch initialization, mapping/relocation and machine state, those equal instruction bytes define the same oracle program. The existing harness comparisons can therefore be reused for that deliberately controlled program. They are **not new tests of either complete game**, and this audit has not rerun them. Their historical scope resets CW to `037f`; the documented x87 status-condition mismatch with maintained C remains unresolved and cannot be erased by cross-version byte identity.

The [precision comparison](og-modern-x87-precision.md) explains why context matters: unchanged x87 instructions can execute under different surrounding precision control and initialization. The tyre sample also reads mutable game state and caller-provided vehicle/tuning data; the byte mover depends on valid ranges, overlap, DF and segment assumptions. Baseline selection for a larger C module must consequently include callers, data layout/initialization and ambient machine contracts, rather than selecting a version solely by this table.

**Bounded status: done; confidence: verified file/code/relocation identity.** Whole-game equivalence, expanded floating-point/input scope and game-facing integration remain unverified. No reference C export, maintained C edit, compiler/linker invocation, new instruction probe, game execution or Ghidra write occurred.
