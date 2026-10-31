# Original versus Modern: temporary viewport camera selection

## Evidence and interface

**Static comparison; no camera/game execution.** Paired `004228e0` bodies have corresponding slot selection, shared camera tables and extraction/restoration calls. Original exclusive end is `004229bb`; Modern is `004229b9`. Reproduce with `python3 analysis/scripts/audit_viewport_pose_difference.py`. The [manifest](evidence/audits/original-modern-viewport-pose.json) retains baseline fingerprints, complete wrapper spans and a byte-identical finalizer witness.

Existing [detailed notes](detailed-analysis-notes.md) name the wrapper `BuildViewportPoseWithTemporaryCameraSelection`: EAX requested viewport, EDX 96-byte destination, EBX control mode, no stack arguments. The current comparison checks instructions rather than relying on the decompiler's inferred prototype.

## Retained slot selection and override precedence

Both select `slot = viewport & 1` when global `006fd3b0 == 1`, otherwise slot zero. Original's `XOR EDI,EAX` zeroes the slot because EDI still equals incoming EAX; Modern uses `XOR EDI,EDI`. These are equivalent on this path, not different viewport policies.

Normal camera selection starts with primary pointer `005e10b0[slot]`. If non-null and descriptor DWORD0 equals `13h`, both temporarily replace that slot with:

`[00552ec8 + 4*slot + 8*[ [00552f60 + 4*slot] + 11ch ]]`.

The formula describes raw pointer/index accesses, not validated table extents. Both then prefer non-null alternate pointer `005e10b8[slot]` over the primary/replacement for extraction through `00422520`. A type-13 replacement still triggers later blending/restoration even when the alternate pointer supplies extraction.

Original records a boolean replacement flag plus saved primary pointer. Modern initializes only the saved-pointer local to zero and uses its nonzero value as the flag. Because the replacement branch first requires a non-null primary, those representations are equivalent under the inspected straight-line conditions. Neither adds a bounds or pointer-lifetime guarantee.

## New fixed-descriptor path

Modern inserts a branch before type-13 handling. If **incoming control mode !=0**, **`006fd3b0 !=1`** and **`006fd1cc !=0`**, it extracts from fixed descriptor address **`00661220`**. This bypasses both the type-13 temporary replacement and the alternate-pointer preference. The primary slot is loaded before the branch but not dereferenced on this fixed path.

Original has no corresponding branch in this wrapper and always follows its normal primary/alternate handling. Existing camera research associates `00661220` with scene/override snapshots, but complete producer schema and the user-visible mode are not established by this wrapper alone. Do not call it a particular cinematic or replay camera solely from that association.

## Restoration, finalization and output cache

When a temporary replacement occurred, both call `004223c0` with destination position/rotation, slot and original control mode, then restore the saved primary pointer to `005e10b0[slot]`. Restoration happens on the normal path after that call. No exception cleanup, concurrent access protection or reentrancy guard is present in the inspected wrapper; a plain C local-pointer rewrite could lose this shared-state timing.

Both call `00422850` to build the transposed rotation and negative translation. Its complete body `00422850..004228df` is **byte-identical**. Original reloads EBX with incoming control mode before calling; Modern omits that reload, but the finalizer saves EBX and overwrites it with a destination-field address before its first operational use. Incoming EBX is not an input to that finalizer. This removed reload alone is not evidence of a changed mathematical result.

After finalization, original tests the reloaded control mode in EBX; Modern tests its saved stack local. For mode zero, both copy **24 DWORDs (96 bytes)** from the destination to `005dd950 + 60h*slot`. Original forms the offset with shifts/subtraction, Modern uses IMUL by 60h; the selected slot is 0 or 1, so these produce the same offset. Nonzero mode skips the cache copy in both.

The finalizer uses x87 and binary32 stores. Byte identity does not establish equal output under different x87 control words or different selected descriptors. Both wrappers preserve ECX/ESI/EDI/EBP, while EAX/EDX/EBX are not presented as preserved scalar outputs. Valid destination and descriptor storage are preconditions; no full pose schema or orthonormal rotation invariant is proved here.

**Verified:** paired wrapper correspondence, equivalent slot/cache arithmetic, new fixed-descriptor admission, retained temporary restoration and identical finalizer. **Unresolved:** fixed-descriptor producers and meaning, full camera-index admission, extraction/blend helper differences, all callers, actual view output and historical release attribution. The follow-up below verifies `00422520` / `004223c0` and selected fixed-descriptor producers. Next: trace source initialization and call order; no runtime conclusion is claimed.

## Extraction/blend identity and fixed-descriptor producers

The manifest now retains and asserts byte identity of both complete direct callees:

| Entry | Exclusive end | Existing analysis name |
|---|---|---|
| `004223c0` | `00422512` | `BlendViewportPoseWithStoredCameraTransform` |
| `00422520` | `00422604` | `ExtractScenePoseWithPositionConstraints` |

Along with the identical finalizer, this localizes the inspected change to wrapper selection/control flow rather than edits inside these three bodies. It does not prove their complete transitive call graphs, data inputs or floating-point state are identical. The extractor copies descriptor position at +14h and selects its rotation source using the supplied control mode, with additional descriptor-controlled calls; a different descriptor can therefore change output through retained instructions.

Modern producer `0042649c..004264be` returns immediately in session 1; otherwise it copies **71 DWORDs = 284 bytes (11ch)** from scene descriptor `005e0dd8` to fixed descriptor `00661220`. It preserves ECX/ESI/EDI. This is a concrete snapshot origin for the fixed descriptor, not proof of the source's full schema, initialization or every caller's ordering.

A second helper `004264c0..004264ec` also skips session 1. Its mixed CMPSD/MOVSD sequence deliberately advances across some fields without writing them. Assuming the forward string direction used by these routines, it copies source DWORD indices **1, 2, 5, 6, 7 and 11..19**, corresponding to offsets **4, 8, 14h, 18h, 1ch and 2ch..4ch**. Other traversed fields remain unchanged in this helper. CMPSD updates flags, but there is no conditional branch consuming those comparison results in this body; replacing it with a whole-descriptor memcpy would change storage effects.

The admission global `006fd1cc` is initialized to 1 by `00472298` at store `004722a6`, after XOR EAX,EAX and MOV AL,1. Another inspected producer at `0045da2d..0045da37` restores it from DWORD `0066468c`. These witnesses establish a nonzero default and a later restore path, not a permanent value or a particular user-facing option. Configuration loading/bulk writes and complete menu binding remain separate.

**Closed:** extraction/blend body comparison, fixed descriptor's full snapshot origin, selected partial-update fields and two admission-global producers. **Still pending:** source descriptor initialization, snapshot call order/lifetime, full global binding and alternate writes, transitive helper changes, actual camera selection and rendered pose. No historical release attribution or runtime equivalence is inferred.

## Snapshot scheduling: added calls in matched setup paths

Paired caller spans now establish two specific additions, with relative CALL targets asserted against the official executable:

| Matched context | Original at the insertion point | Modern |
|---|---|---|
| `InitializeRaceViewportSceneRecords` (`00422cf0`), after stores through `00553018` | Epilogue starts at `0042389a`; returns without a snapshot call there. | `0042389a` calls full snapshot helper `0042649c`, then enters its epilogue. |
| `BindViewportSceneDescriptorsToRaceVehicle` (`004215c0`), after its binding loop | `00421718` sets EDX=3, then EAX=EBX and calls `004238b0`. | `00421718` first calls partial snapshot updater `004264c0`, then sets EDX=3 through XOR/MOV DL and continues. |

These two points connect the fixed descriptor to scene initialization and vehicle binding, respectively. The full snapshot helper copies the complete 11ch-byte source on non-session-1 paths; the partial updater refreshes only the documented fields. Thus Modern adds scheduling for retained state at `00661220`, rather than merely selecting an otherwise unexplained constant address in the pose wrapper.

The corresponding original bytes at `0042649c..004264ec` contain parts of other mode-handler call/return sequences. They are retained as raw original-region witnesses, **not named as original counterparts of the two Modern snapshot helpers**. Recovering the complete displaced handler correspondence is separate work; their differing bytes alone do not prove removal of the original camera modes.

This proves local call order at the two insertion points. It does not prove global ordering between scene initialization, every rebind, snapshot consumption, descriptor mutation and menu/config updates. Session 1 causes both snapshot helpers to return without copying, and the wrapper's new fixed-descriptor branch also excludes session 1; those local gates are consistent, but do not establish all runtime lifecycle invariants.

**Next:** trace callers of the matched setup functions and remaining descriptor writes, then map the reused original mode-handler region if needed. Runtime camera behavior and release introduction remain unverified.
