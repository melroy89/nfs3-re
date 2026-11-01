# Historical lockwindow failure callbacks:1.5.0 to1.5.1

**Confidence: verified static paths. Work status: partial for MP151-004.** This compares retained author-hosted Modern Patch1.5.0 and1.5.1 archives, not authenticated original-retail drivers or a new EXE difference. The [reproducible audit](scripts/audit_historical_lockwindow_failure.py) verifies both archive hashes, six DLL hashes, export addresses, branch witnesses and adapters. Its [manifest](evidence/audits/historical-lockwindow-failure.json) retains complete selected lockwindow envelopes and disassembly hashes. Archive members are read into memory; no DLL or API was executed.

## Shared failure-path change

Each DLL exports `_THRASH_lockwindow@0`. The inspected path requests callback argument1 before a surface vtable+64h call. Existing [DX5 interface research](original-modern-dx5-reference-pair.md) supplies that driver's wider interface context; this historical comparison does not infer every object's interface identity solely from a shared offset.

| Driver / member | Lockwindow entry |1.5.0 nonzero-result route |1.5.1 nonzero-result route |
|---|---|---|---|
| `drivers/dx5/dx5a.dll` | `600011d4` | After storing result, branch at`60001234` to existing failure continuation`60001326` | At`6000122d`, EAX0→helper`60001880`, then jump to the same continuation |
| `drivers/dx6/dx6a.dll` | `60001240` | Result failure falls through to EAX0 and stack-restoring RET | At`600012ce`, EAX0→helper`60001d90`, then EAX0 and shared return tail`600013d6` |
| `drivers/softtri/softtria.dll` | `60003530` | Branch`6000362f` goes directly to failure continuation`60003550` | Same branch targets new tail`600036c1`: PUSH0, indirect callback, jump to`60003550` |

The local result predicate is **nonzero**, not a signed HRESULT-negative test. Preserve that distinction in reconstruction. These paths add a callback0 request after an attempted lock whose result takes the failure branch; the previous failure continuation remains. No actual failed lock or resulting state restoration was observed.

## Callback adapters and ABI

In1.5.0 DX5 reads optional callback slot`6001289c`, checks null, then pushes1 and calls it directly.1.5.1 replaces this with EAX1→`60001880`. DX6 similarly changes slot`6003bcd4`'s direct PUSH1 call to EAX1→`60001d90`.

Both new adapters are17-byte bodies with the same instruction shape: preserve EBX, save incoming EAX in EBX, load the callback pointer, skip it if null, otherwise PUSH EBX and CALL EAX, restore EBX and RET. They do not explicitly discard the pushed argument, so normal return requires the callback's compatible stack-cleanup contract. They are not demonstrated Boolean-return helpers. The new failure paths reuse them with EAX0.

SoftTri instead retains the existing callback slot`600400b4` and adds a direct PUSH0/CALL through it in the new tail. This local call has no newly added null check. The callback pointer's admission/lifetime and ordinary ABI remain separate requirements; do not silently add a guard and describe it as the original behaviour.

## Interpretation and limits

The static mechanism is consistent with balancing a callback1 request with callback0 when locking fails. **The follow-up below identifies the corresponding EXE callback as critical-section enter/leave.** This report still does not prove that it fixes a reproduced freeze or restores every surrounding state. Complete successful-lock/unlock lifetimes, reentrancy, callback mutation, surface-loss/retry handling and all other changed bytes in these DLLs are not qualified by the failure-path witnesses.

MP151-004 names DX5, DX6 and SoftTri lockwindow fixes. All three historical pairs now have concrete failure-path evidence, so the entry advances from vendor-only to **partial**. It is not fully verified until registration/lifetime contracts and the claimed bug's actual effect are established. No reconstruction, compilation, target execution or Ghidra change was performed.


## EXE callback table identifies critical-section enter and leave

The extended audit extracts `nfs3.exe` from **each same pinned archive**, verifies its hash and captures the registration witness and complete59-byte callback. Both historical EXEs contain the same eight-pointer block at **`0056afd0`**. Its sixth DWORD, at offset`14h`, is **`00524550`**. At `0052472d..0052473a`, the raster initializer pushes that block pointer and selector`13h`, then calls renderer slot`009ef96c` before the following initialization call. Registration must actually reach the selected driver for this static linkage to describe its installed callback.

The1.5.1 DLLs have direct eight-DWORD bulk-copy writers to these callback-bank destinations:

| Driver | Copy destination | Lock callback cell | Cell offset |
|---|---|---|---|
| DX5 | `60012888` | `6001289c` | `14h` |
| DX6 | `6003bcc0` | `6003bcd4` | `14h` |
| SoftTri | `600400a0` | `600400b4` | `14h` |

The [existing DX5 registration analysis](original-modern-dx5-reference-pair.md#lock-failure-now-notifies-the-callback) already establishes its selector13h route. The copy witnesses corroborate the other bank layouts; the follow-up below resolves the1.5.1 DX6/SoftTri selector13h dispatch/admission. Alternate writers and lifetime remain separate. Bulk-copy layout is not an observed registration session.

Complete callback **`00524550..0052458b`** is identical in both historical EXEs. It reads its stack argument. Nonzero passes pointer`[00564480]` to imported **EnterCriticalSection** (`005344b8`); zero passes that pointer to imported **LeaveCriticalSection** (`00534588`). After the API call, both branches publish the original raw argument at `00567180`, then execute **RET4**. This verifies the stack cleanup required by the driver calls; the nonzero branch also explicitly saves/restores EBX. It does not normalize arbitrary nonzero arguments or return a documented success Boolean.

**Conditional mechanism:** with this block installed, a stable/valid critical-section pointer and ordinary callback return, the pre-lock callback1 enters the section. The new failure callback0 leaves it before the prior failure return. The old inspected failure paths omitted that release request; ordinary unlock callbacks were a different route. This is concrete synchronization evidence, not merely an unnamed notification. Do not describe it as a generic kernel-mutex unlock or claim every possible recursive acquisition is balanced.

**Still pending at this checkpoint:** complete creation/destruction and aliases of `[00564480]` (selected setup paths are qualified below), callback-bank mutation, complete registration dispatch and admission, other lock/unlock/error paths, reentrancy and a real failed-lock/deadlock reproduction. The release note remains **partial** despite the stronger mechanism evidence. No critical section, driver callback, API or game instruction was executed.


## Critical-section setup narrows the pointer-lifetime prerequisite

The audit now captures complete **`004eb2e0..004eb333`** (83-byte pool helper), **`004df740..004df799`** (89-byte initialization entry) and raster admission **`005246d2..00524712`**. Each span is byte-identical in the same-archive1.5.0/1.5.1 EXEs; their hashes are asserted equal. This is retained setup context for the driver fix, not an additional historical change.

The pool helper checks initialization flag`009ef5b8`, calls setup if needed, and obtains a node through free-list head`00564a64`. If needed it calls replenisher`004eb260`. If the head remains null, it returns0. Otherwise it advances the free-list head from node+`18h`, requests zeroing of the first`18h` bytes through`004e070c`, calls imported **InitializeCriticalSection** at`004eb326` with that node pointer, and returns the node. The instruction sequence supplies a24-byte object; this is not a claim that every pool field or replenisher contract is reconstructed.

Two verified publication paths are:

| Caller | Observed publication / admission |
|---|---|
| `004df740` initialization entry | Sets its initialization flag1, calls producer at`004df78c`, stores returned EAX to`00564480` at`004df791` |
| Raster startup | At`005246d2`, existing nonnull pointer bypasses creation; null reaches call`00524706`, then store`0052470b`, and jumps back to`005246db` |

The raster path does **not** locally retest the returned pointer after publication. The callback likewise passes the global to Enter/Leave without a null check. Thus this setup trace narrows ownership evidence but does not justify assuming allocation/initialization always succeeds. The pool helper's failure return, initialization exceptions, concurrent first use, other publishers, object destruction and pointer mutation require their own qualification.

For the inspected valid initialized path, the added failure callback0 therefore has a real critical-section release consumer. It still does not prove the section is dedicated solely to renderer locking: the global has additional consumers outside these captured paths. Full shared-lock ordering, recursion and a live deadlock reproduction remain unresolved. No object was allocated, initialized, entered, left or deleted during this analysis.


## Correspondence with supplied original and official final EXEs

The audit now also verifies the supplied original and official final executable SHA-256 identities from the [baseline comparison](original-modern-differences.md). Their complete eight-pointer table at`0056afd0` is identical to both historical EXEs. The following selected spans are asserted byte-identical **across all four EXEs**:

| Span (end exclusive) | Bytes | Retained role |
|---|---:|---|
| `00524550..0052458b` | 59 | Enter/Leave callback, raw argument publication and RET4 |
| `004eb2e0..004eb333` | 83 | Pool-node critical-section initialization helper |
| `004df740..004df799` | 89 | General initialization/publication path |
| `0052471d..00524740` | 35 | Renderer setup and callback-table registration witness |

All four use matching inspected Initialize/Enter/LeaveCriticalSection import bindings. The audit retains separate hashes and disassembly for original/final instead of transferring historical labels by address alone. This establishes original/final **EXE-side correspondence within these ranges**, not byte equality of every driver, callback target, indirect export slot or surrounding startup path.

The [existing hosted-reference/final DX5 comparison](original-modern-dx5-reference-pair.md#lock-failure-now-notifies-the-callback) independently identifies the same failure-notification mechanism and registration offset in that driver pair. Its reference archive is not authenticated as every retail installation, and DX6/SoftTri's new evidence remains the explicitly dated historical pair. Do not describe all three as original-retail driver comparisons.

The combined interpretation is therefore a changed driver failure path using a **retained EXE critical-section callback**, with1.5.0→1.5.1 dating for the three selected drivers. EXE callback preservation is established; complete call admission, valid object lifetime and actual failure recovery remain pending. No executable/database bytes, driver state or critical-section objects were changed.


## DX6 and SoftTri selector13h registration routes

The extended audit now verifies the **1.5.1** registration dispatch, not just bank offsets. Its manifest retains the selected export-entry prefixes, DX6 table entry, copy blocks and instruction witnesses. These are static routes; successful invocation and callback lifetime remain conditional.

**DX6:** exported `_THRASH_setstate@8` begins at`60003310`. Its stack loads put selector in EDI and payload in EBX, with EBP zeroed. Selector19 (`13h`) passes the upper-bound checks and reaches indirect jump`6000333e` through table`60003f0c`. Entry19 is **`600036d1`**. That block compares payload EBX against EBP0: null jumps away to`60003cca`, while nonnull sets ESI=EBX, ECX8, EDI=`6003bcc0` and copies eight DWORDs. Callback cell`6003bcd4` therefore receives payload+`14h` on that admitted path.

**SoftTri:** exported `_THRASH_setstate@8` begins at`600030c0`, loading selector into EAX and payload into EDX. Ordered comparisons send19 past17, below104 and21, then above18 to`60003228`; equality against19 admits the eight-DWORD copy from EDX to`600400a0`. The branch returns1 with RET8 after restoring EDI/ESI. There is **no local null test of the payload pointer on this copy path**. Callback cell`600400b4` receives payload+`14h`, assuming accessible storage and ordinary clear DF for the REP MOVSD.

This closes the selected DX6/SoftTri1.5.1 selector-to-bank edges behind the critical-section callback interpretation. It does not make null input safe, prove all export slots were resolved successfully, exclude callback replacement, or establish thread/teardown ordering. Full historical registration equivalence, remaining setters/aliases and live failure behaviour remain pending. MP151-004 remains partial; no API or target instruction was executed.
