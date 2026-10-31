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

**Verified:** paired wrapper correspondence, equivalent slot/cache arithmetic, new fixed-descriptor admission, retained temporary restoration and identical finalizer. **Unresolved:** fixed-descriptor producers and meaning, full camera-index admission, extraction/blend helper differences, all callers, actual view output and historical release attribution. Next: compare `00422520` / `004223c0` and trace the fixed-descriptor producer chain; no runtime conclusion is claimed.
