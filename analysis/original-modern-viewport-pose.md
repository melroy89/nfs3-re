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

Both 284-byte spans lie in loader-zeroed `.bss` in the supplied original, 1.5.0, 1.5.1 and final EXEs. In this PE layout `.bss` starts at VA `0056e000` and has a zero raw-data pointer. The header's size field is `0x4aa400` in the original and `0x4b1000` in the three Modern builds. The 1.5.1 base relocation directory has no nonzero-type entries targeting either span. Thus `00661220` is runtime storage for the snapshot introduced in 1.5.1. The file contains no initial descriptor template at that address. The earlier builds' allocation alone does not establish the same use for that address. Source field writes and ordering at runtime remain open.

A second helper `004264c0..004264ec` also skips session 1. Its mixed CMPSD/MOVSD sequence deliberately advances across some fields without writing them. Assuming the forward string direction used by these routines, it copies source DWORD indices **1, 2, 5, 6, 7 and 11..19**, corresponding to offsets **4, 8, 14h, 18h, 1ch and 2ch..4ch**. Other traversed fields remain unchanged in this helper. CMPSD updates flags, but there is no conditional branch consuming those comparison results in this body; replacing it with a whole-descriptor memcpy would change storage effects.

The admission global `006fd1cc` is initialized to 1 by `00472298` at store `004722a6`, after XOR EAX,EAX and MOV AL,1. Another inspected producer at `0045da2d..0045da37` restores it from DWORD `0066468c`. These witnesses establish a nonzero default and a later restore path, not a permanent value. The menu-binding follow-up below identifies the user-facing selector; configuration/bulk writes and complete lifecycle remain separate.

**Closed:** extraction/blend body comparison, fixed descriptor's full snapshot origin, selected partial-update fields and two admission-global producers. **Still pending:** source descriptor initialization, snapshot call order/lifetime, all alternate global writes, transitive helper changes, actual camera selection and rendered pose; the menu binding is verified below. No historical release attribution or runtime equivalence is inferred.

## Snapshot scheduling: added calls in matched setup paths

Paired caller spans now establish two specific additions, with relative CALL targets asserted against the official executable:

| Matched context | Original at the insertion point | Modern |
|---|---|---|
| `InitializeRaceViewportSceneRecords` (`00422cf0`), after stores through `00553018` | Epilogue starts at `0042389a`; returns without a snapshot call there. | `0042389a` calls full snapshot helper `0042649c`, then enters its epilogue. |
| `BindViewportSceneDescriptorsToRaceVehicle` (`004215c0`), after its binding loop | `00421718` sets EDX=3, then EAX=EBX and calls `004238b0`. | `00421718` first calls partial snapshot updater `004264c0`, then sets EDX=3 through XOR/MOV DL and continues. |

These two points connect the fixed descriptor to scene initialization and vehicle binding, respectively. The full snapshot helper copies the complete 11ch-byte source on non-session-1 paths; the partial updater refreshes only the documented fields. Thus Modern adds scheduling for retained state at `00661220`, rather than merely selecting an otherwise unexplained constant address in the pose wrapper.

The copied source `005e0dd8` is already present as the mode-1, local-index-0 pointer at `00552ed0` in both the supplied original and 1.5.1. The 200-byte table and the indexed lookup at `00423845..00423865` match. When that entry is visited, the retained initializer at `00422da2..00422de5` writes the selected object pointer at descriptor offsets `+4/+8`, clears `+0x10`, publishes mode and local index at `+0/+0x0c`, and copies 30 DWORDs from the prepared stack record to `+0x74`. This links the added snapshot to concrete writes in the original scene setup. Other fields and live values remain unverified.

The prepared record starts with 120 file-backed zero bytes at `004212dc..00421354`, identical in the original, 1.5.1 and 1.6.1. The retained instructions at `00422d0c..00422d1e` copy them to `[EBP-0x7c]`, supplying the source for the 30-DWORD transfer above. This is an explicit initialization of descriptor offsets `+0x74..+0xeb` when that table entry is visited, separate from loader zero-fill. The following 1.5.1 instruction at `00422de5` initializes `+0xec` to `0xffffffff`. Subsequent writes can alter the record before the snapshot.

The next initializer span, `00422def..00422e62`, also matches in all three builds. It reads the object pointer from descriptor `+4`, copies nine DWORDs from object `+0xc0` to descriptor `+0x2c`, and moves three binary32 values from object `+0x98/+0x9c/+0xa0` into descriptor `+0x14/+0x18/+0x1c` using x87 loads and stores. Those position and nine-word regions also fall within the partial updater's write set. Both initialization and refresh therefore have concrete pose-field sources, while live object values and intervening writes remain unresolved.

The same producer chain is present in the retained 1.5.1 EXE. The scene and vehicle paths issue direct calls at `0042389a` and `00421718`, respectively. The helper bodies reference the same source and destination at `004264a9/ae` and `004264cd/d2`. The corresponding 1.5.0 disassembly has neither direct call nor a decoded immediate operand naming `00661220`. This dates the selected snapshot scheduling to the release that also adds the rear-camera selector and its consumers. The direct-reference scan leaves computed accesses and live call ordering unresolved.

The corresponding original bytes at `0042649c..004264ec` contain parts of other mode-handler call/return sequences. They are retained as raw original-region witnesses, **not named as original counterparts of the two Modern snapshot helpers**. Recovering the complete displaced handler correspondence is separate work; their differing bytes alone do not prove removal of the original camera modes.

This proves local call order at the two insertion points. It does not prove global ordering between scene initialization, every rebind, snapshot consumption, descriptor mutation and menu/config updates. Session 1 causes both snapshot helpers to return without copying, and the wrapper's new fixed-descriptor branch also excludes session 1; those local gates are consistent, but do not establish all runtime lifecycle invariants.

**Next:** trace callers of the matched setup functions and remaining descriptor writes, then map the reused original mode-handler region if needed. Runtime camera behavior and release introduction remain unverified.

## Rear-camera menu binding identifies the fixed-path selector

The expanded pose audit now verifies official `fedata/menus/camera.mnu` against the pinned Modern archive. It contains both an arrowtab button and a cascade with `listname=rearcamera`, ypos6; the cascade's `maxvisitem` is5. Local uppercase backup `fedata_org/menus/CAMERA.MNU` has no `rearcamera` item. Both hashes and parsed fields are retained. The backup remains unauthenticated as retail and is not established as the supplied original executable's paired asset.

Executable descriptor `00556550` binds exact name `rearcamera`, list pointer `005563aa`, and selection DWORD **`006fd1cc`**. The list contains WORDs **1939,1940,0**. The embedded language fallback table gives the authored meanings:

| ID | Verified fallback text | Position in the list |
|---|---|---|
| 1938 | Rear View From | Menu label (`text=str_1938` on the button) |
| 1939 | Active Camera | First choice |
| 1940 | In Car Camera | Second choice |

These are actual executable fallback strings, not proof of the selected external language file or a rendered label. The visible cap5 does not imply five choices. Descriptor binding establishes that these controls use the same selector already tested by the changed pose wrapper.

Under the wrapper's previously verified conditions—nonzero control mode, session `006fd3b0 != 1`, selector nonzero—Modern chooses fixed descriptor `00661220` instead of the normal primary/alternate route. Original has no corresponding branch. The authored choice names and selector binding therefore support the association of the new fixed route with the in-car rear-camera option. The default initializer writes1, but actual ordinal changes from input, malformed values, source-descriptor lifetime and visible camera geometry remain untested. The branch admits any nonzero selector, not only literal1.

**MP151-001: partial static support.** Official controls, two choice labels, selector identity, nonzero default and changed descriptor-selection mechanism are verified. Universal “locked in car” output, visibility/blind-spot improvement, all runtime callers and introduction in v1.5.1 require further evidence. No game, camera input, new instruction probe or Ghidra mutation was performed.


## Historical camera-menu addition is now dated directly

### Earlier mirror-direction claim

The 1.4.0 and 1.5.0 archive members match across the selected scene initializer `00422cf0..004238a8`, pose wrapper `004228e0..00422a30`, extractor `00422520..00422604`, blend helper `004223c0..00422512`, and finalizer `00422850..004228df`. The projection caller `004dbde0..004dbee6` also matches, including its mirror rectangle selection. The adapter at `004bed20` matches through its return at `004bed8b`; the first difference in the wider window is at the next routine, `004bed90`. These checks narrow the search for MP150-006 to inputs, other consumers or downstream behavior. The reported horizon change remains unverified. The later 1.5.1 selector below has separate evidence.

One input does change at that boundary. The mirror rectangle producer moves its literal `007cdb48` reference from `004be786` to `004be74b`, while the projection caller still passes that address at `004dbe06`. In 1.5.0 the producer calls `004be880` to store the physical rectangle into the second group. It then calculates a new logical height and stores the logical Y as the physical Y plus `(physical_height - logical_height) >> 1`, using arithmetic shift at `004be784`. The setter `004be874` places these values at record offsets `+4` and `+0x0c`. This is direct evidence of changed projection geometry with retained camera-pose instructions. It leaves open whether this is the mechanism behind the stated horizon correction and whether the rendered horizon is centered.

For positive dimensions without integer overflow, the 1.5.0 height instructions at `004be761..004be77d` compute `ceil((floor(1000 * H / 533) + floor(10 * W / 16)) / 2)`, with physical width `W` and height `H`. The subsequent arithmetic shift places the logical and physical rectangle midpoints within half a coordinate unit of each other. In 1.4.0, the two setters at `004be796/7a7` instead use logical Y equal to physical Y minus the quotient calculated at `004be770`, and store the independently prepared logical height popped at `004be78d`. The old geometry therefore has a different centering rule. This calculation concerns the rectangle passed to projection. It does not measure the horizon or identify a camera pitch change.

The 1.4.0 and 1.5.0 projection wrapper `004dbce0..004dbd97`, centre builder `004bf260..004bf370`, and binary32 half constant `005401c0` are byte-identical. The mirror selector passes the first rectangle group through `004bed20`; loads at `004bed28` and `004bed2f` take logical height and Y. The wrapper calls the [centre builder](original-modern-projection.md#retained-float-centre-producer-reaches-a-retained-projection-consumer) at `004dbd8a`, which stores Y plus half height at `005600a8`. This links the 1.5.0 centering math to the actual projection centre calculation. This provides partial static support for MP150-006. Camera pitch, any later projection writes and the visible horizon remain unverified.

In 1.4.0 both logical height and the Y offset come from display height `D` at `[EBP-0x1c]`. The signed division-by-four sequence at `004be72b..004be738` supplies `truncate(D / 4)` through the saved EAX value. The multiply/divide at `004be75d..004be772` supplies `truncate(5 * D / 60)` to subtract from physical Y. For example, holding the physical mirror rectangle fixed at width 160 and height 60 on a display of height 480, 1.4.0 stores logical height 120 and Y minus 40, yielding a projection centre 20 units below physical Y. The 1.5.0 formula gives height 106 and Y minus 23, yielding a centre 30 units below physical Y, equal to the physical midpoint in that example. These are derived values for fixed illustrative inputs, without assuming either executable produces those exact physical dimensions in a live session.

The [1.5.0→1.5.1 menu/translation pair](original-modern-localization-151.md#historical-menu-assets-bind-two-new-labels) verifies the exact15-line insertion adding the rear-camera button/cascade and `lang1938` label, with every old camera-menu line retained. This narrows the historical introduction gap for that authored control; it does not date every EXE camera mechanism or prove runtime availability/selection. The same comparison finds the separate mirrorlevel label replacement, which is not a new-control introduction.

The same release boundary adds executable consumers. In 1.5.1, the pose branch at `00422922` tests `006fd1cc` before choosing fixed descriptor `00661220` at `0042292b`. The selected branch also requires a nonzero incoming control mode and `006fd3b0 != 1`. The dispatch route at `00426482` tests that selector after the ordinary indirect handler, then calls `004240c0` with EAX=`00661220` and EDX=1 if both global gates admit it. The corresponding 1.5.0 paths lack both selector tests. A direct-operand scan also finds the 1.5.1 snapshot, restore and default stores at `0045d957`, `0045da32` and `00472266`. This dates the selected menu, initialization and camera paths together. Runtime rendering remains unverified.

The 1.5.1, 1.5.2, 1.5.3, 1.6.0 and final 1.6.1 EXEs match byte for byte in the pose gate `00422913..00422932`, the dispatch and post-call gate `00426472..0042649a`, the dispatch table `004263f0..00426450`, and the snapshot/restore spans `0045d957..0045d961` and `0045da2d..0045da37`. The 20-byte menu descriptor at `00556550` and its six-byte choice list at `005563aa` also match. This establishes continuity of those selected branches and bindings. The comparison leaves the fixed descriptor's runtime contents, handler internals and rendered mirror view open.

## Default camera slots change without removing the choice table

**Verified static defaults and named bindings; runtime cycling untested.** The [camera-default audit](evidence/audits/camera-defaults-difference.json), reproduced with `python3 analysis/scripts/audit_camera_defaults_difference.py`, compares the hash-pinned supplied original and official final Modern EXEs. Four identical20-byte descriptors at `00556c1c/30/44/58` bind `camera1..camera4` to settings `006fbba8/ac/b0/b4`. Their shared label list `0055628e` is unchanged, as is its separate mode-ID table `0055629e`.

| Slot | Original default ordinal / label / mode | Final Modern default ordinal / label / mode |
|---|---|---|
|Camera1 |1 / In Car /1 |3 / Heli Cam /3 |
|Camera2 |2 / Roof Cam /4 |1 / In Car /1 |
|Camera3 |3 / Heli Cam /3 |0 / None /0 |
|Camera4 |0 / None /0 |0 / None /0 |

Original's initializer sets EBX=3 at`0047241a`, EDX=1 at`00472425`, stores Camera1/3 at`00472454/0047245a`, then sets ESI=0/ECX=2 and stores Camera4/2 at`0047246c/00472475`. Between the first constants and stores it calls `004b56d0..004b56e0`, a complete16-byte GetTickCount wrapper that explicitly saves EDX/ECX/EBP. EBX retention assumes the normal32-bit Windows API callee-preserved contract; this is not an execution or arbitrary-hook proof.

Modern instead uses complete47-byte default helper `00472298..004722c7`: zero Camera3/4, load AL=1 for Camera2 and rear-camera selector, then AL=3 for Camera1 and two other fields. EAX starts zero and there are no intervening calls before these stores, so the low-byte loads establish full DWORD constants. The helper then calls retained converter `00472300`.

The complete85-byte converter `00472300..00472355` is byte-identical in the pair. It maps each ordinal through `0055629e`, publishing mode IDs at `006fbbc0/c4/c8/cc`. It uses overlapping DWORD reads at `0055629c + 2*ordinal`, then arithmetic-shifts16; reproducing only its selected WORD value does not establish identical memory-read footprint. No local ordinal bounds check exists in this converter; the table-derived interpretation above assumes the inspected valid defaults.

The retained 1.1.0 executable already has the final slot order. Its original-shaped defaults block loads EBX=3 and EDX=1 at `0047241a/25`, stores Camera2/1 from EDX/EBX at `00472454/5a`, and clears Camera3/4 at `0047246f/75`. The ordinary call at `00472488` converts these ordinals with the same mode values at `0055629e`, yielding `3, 1, 0, 0`. Thus the Heli Cam and In Car ordering predates relocation to final's separate helper. The exact 1.0.0 implementation and runtime selection remain unverified.

The archive members show that the relocation occurs from 1.4.0 to 1.5.0. The 1.4.0 span `0047241a..0047248d` matches 1.1.0. The separate 1.5.0 helper at `00472258..00472282` writes the same four ordinals and calls `00472300`. In 1.5.1, that helper adds a single five-byte store of ordinal 1 to `006fd1cc` at `00472266`, using the same value it writes to Camera2. Its converter call displacement changes to reach the same target. This dates initialization of the rear-camera selector in the reviewed helper to the same release that adds the authored control. Other writers and actual rear-camera behavior remain unverified.

If those defaults reach the [viewport membership rebuild](original-modern-hud-layout.md), the ordered nonzero candidates are `1, 4, 3` in the original and `3, 1` in final. The shared builder at `00423a60` fills all 25 entries with the first candidate and writes each later candidate at its predecessor's index. The original table therefore has `table[1] = 4`, `table[4] = 3`, and 1 everywhere else. Final has `table[3] = 1` and 3 everywhere else. The complete iterator, builder and membership span `00423a20..00423ad9` and the fallback span `00425400..0042543c` match across the pair. With the respective saved defaults intact, both default values pass their own rebuilt table. The selected `-1` fallback path thus forwards mode 1 (In Car) in the original and mode 3 (Heli Cam) in final under these premises. Actual rebuild timing, later setting writes and rendered views remain unverified.

The unchanged choices decode as None, In Car, Roof Cam, Heli Cam, Bumper Cam, High Cam and Low Cam using the hash-pinned official final English table. The packaged final `camera.mnu` still names all four lists. This supports configurable slots remaining available, rather than removal of the other camera implementations. Actual restoration of the original arrangement through the UI, input cycling, user-file overrides and every later writer remain untested. Original language provenance and1.0.0 introduction are also unverified.

**MP100-031 advances to partial support:** final defaults have two non-None slots, Heli Cam and In Car, while original has three. “None” is the verified list label/mode0; its complete runtime admission semantics are not established by the default writes alone. The separate [dispatch-wrapper comparison](evidence/audits/camera-dispatch-wrapper.json) already maps retained handler targets and changed register/post-processing contracts; this default change does not establish camera geometry, projection equivalence or removal of handlers. No game, camera input, instruction probe or Ghidra write occurred.
