# Incremental C reconstruction readiness

Status: **audit in progress**. This is a bounded documentation phase, not a claim that the game is ready to rebuild. No reference C exports, reconstruction sources or compilation are authorized in this phase. Existing scratchpad gaps need not all close before the first module.

## Baseline checkpoint

Inspected repository baseline: `a77ab226581481ea64e110b052b0f46f240f6b6f`.

- Executable: `nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe`, 1,699,840 bytes; SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
- PE machine: i386 (`0x14c`), image base `00400000`, entry `004f7fa0`.
- Saved project: `nfs3_decomp.gpr`; logical program `/Electronic Arts/Need For Speed III/nfs3.exe`.
- Saved program database: `nfs3_decomp.rep/idata/f9/~00000f9f.db/db.3141.gbf`, SHA-256 `ee64d4bae802146ef7f5957027fc7a7a48908029734f484aa11d5bdac85aa93e`.
- Installed Ghidra: 12.1.4 PUBLIC, revision `8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc`; Java 21.0.12.1.
- Language/compiler specification and current signatures: pending saved-database readback. No running GUI instance was discovered.

Confidence: **verified** for file hashes and installed version; work status: **done** for that checkpoint, **pending** for saved-program metadata.

## Proposed first module

Name: **line-boundary candidate leaf**. Include only `CalculateLineBoundaryIntersectionCandidate`, `00485c30..00485f1a` inclusive (747 bytes; end exclusive `00485f1b`). Function SHA-256: `3543671c1408e9124a8dd6dfc3166f296390b768b8ea8ab881517b3c041b237f` in the retained original-instruction probe. Do not describe this leaf as a complete segment clipper.

Existing evidence:

- [Detailed investigation](detailed-analysis-notes.md), sections “Geometry-intersection helper outer contract” and “Isolated execution of the line-boundary helper”.
- [Original-instruction probe](scripts/probe_line_boundary_helper.py) and [retained 40-case results](evidence/probes/line-boundary-helper-probe.json).
- [Probe scope and limitations](scripts/README.md).

Dependency map (static research; fresh instruction readback pending):

| Address | Role | Module-one boundary |
|---|---|---|
| `00485c30` | Candidate leaf; no calls in existing review | Include |
| `00791c08`, `00791c0c` | Two shared binary32 scratch components | Include original storage semantics in comparison model |
| `00485f20` | Segment clipper caller, policy 1 | Inspect contract; defer implementation |
| `004860b0` | Outside-fragment caller, mixed policies | Inspect contract; defer implementation |
| `004873e0`, `00487a30`, `0048d4c0` | HUD consumers | Defer implementation and rendering claims |
| `004b4919` | Unrelated dispatcher investigation | Exclude unless a dependency is established |

First future artifact: a standalone **test executable**, not a replacement game component. Proposed eventual target is 32-bit Windows i686 with explicit ABI adapters for the original register convention. Toolchain/flags and floating-point conformance remain audit items. The existing Linux i386 instruction harness is an oracle, not evidence that reconstructed Windows C builds or behaves correctly.

## Comparison plan

Freeze the 40 existing original-instruction cases (20 vectors, policies 0/1), including binary32 input rounding, seeded mask `0xa0` and x87 control word `0x037f`. A future comparison must execute the reconstructed C as well as the unchanged instruction oracle. Compare null/non-null return semantics, candidate raw bits, caller mask, all modified globals, preserved registers and relevant floating-point state. Pointer values must be normalized to storage identity where addresses differ.

No tolerance is currently justified: require bitwise agreement for the existing finite witnesses; retain separate NaN payload/status and signed-zero checks rather than numerical equality alone. Expand endpoint/corner ties, zero-length/parallel lines, infinities, NaNs, aliasing, and alternate rounding/exception modes before claiming those domains. Existing probes alone do not prove caller reachability, reentrancy, rendering correctness or C equivalence. No test stubs are needed for the leaf's existing original-instruction harness.

## Remaining audit checklist

All entries below are **pending**, unless explicitly stated otherwise above:

1. Saved language/compiler metadata, exporter configuration, address manifest and no-export repeatability blocker/procedure.
2. Register/storage contracts for `004abd9c`, `00518640`, selected leaf and relevant callers.
3. Fresh function-body/control-flow readback, indirect targets/shared tails where relevant.
4. Layout, initialized versus zero-filled storage, relocations, startup writes and PE resources.
5. x87, integer/aliasing/undefined-behavior, shared storage and synchronization treatment.
6. Explicit toolchain, ABI/build boundaries and confirmed dependency inventory.
7. Complete scoped comparison matrix and probe limitations.
8. Prioritized blockers by reference-export, compilation, linking and runtime-validation stage; saved Ghidra changes/readback or explicit no-change justification.
