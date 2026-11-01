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

The static mechanism is consistent with balancing a callback1 request with callback0 when locking fails. **The callback's identity and the meaning of1/0 remain unresolved here**; this report does not prove that it unlocks a mutex, re-enables rendering or fixes a reproduced freeze. Complete successful-lock/unlock lifetimes, reentrancy, callback mutation, surface-loss/retry handling and all other changed bytes in these DLLs are not qualified by the failure-path witnesses.

MP151-004 names DX5, DX6 and SoftTri lockwindow fixes. All three historical pairs now have concrete failure-path evidence, so the entry advances from vendor-only to **partial**. It is not fully verified until callback ownership/contracts and the claimed bug's actual effect are established. No reconstruction, compilation, target execution or Ghidra change was performed.
