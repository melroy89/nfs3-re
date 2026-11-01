# Software renderer: reference/final pairing and mode-depth admission

## Identity and reproduction

This pairs `softtria.dll` from the [author-hosted reference bundle](original-modern-original-reference-bundle.md) with `drivers/softtri/softtria.dll` from the pinned final Modern archive. Hosting does not authenticate a pristine retail DLL or establish a historical introduction date.

| Role | Bytes | SHA-256 |
|---|---:|---|
| Reference | 304,482 | `8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02` |
| Final Modern | 277,504 | `9479203471f4dd615788769bac365043d903505af370c48df69e5d6a1e6f8732` |

Run `python3 analysis/scripts/audit_software_reference_final.py`. The [script](scripts/audit_software_reference_final.py) verifies both archive/member hashes and retains exports, section metadata, all shared-code changed-byte intervals and selected disassembly in [the manifest](evidence/audits/software-reference-final.json). No DLL or target instructions are executed.

## What the file comparison establishes

Both image bases are `60000000`. All34 named export entries match in name, ordinal, RVA and forwarder field. The complete shared245,760-byte code-section extent has **44 differing bytes in nine maximal intervals**. These are an address-based investigation map, not nine feature changes. File-backed import/data sections are entirely identical:2,048 and6,656 bytes respectively.

The reference has28,514 trailing bytes after its last raw section; Modern has none and adds a1,536-byte resource section. This accounts for the net26,978-byte file-size reduction arithmetically, not semantically. The trailing material's purpose and resource contents are not decoded here. A large size reduction must not be equated with removal of that much executable code.

Every listed section has `VirtualSize=0`; the unchanged BSS header has RVA40000h, raw-size field2800h and raw-data pointer0. The audit does not treat file offset zero as BSS initial data or observe loader zero filling. Headers, relocations, exports/resources and trailing material remain separate from the shared-code interpretation.

## Exact mode-callback change

Complete callback `60002480..60002580` is256 bytes in both images. Its first stack argument is the incoming descriptor, its second a context/count pointer; return uses `RET 8`. The width/height/depth inputs are read at descriptor+0ch/+08h/+54h. At `60002494`:

| Reference | Modern |
|---|---|
| Compare depth with15; if equal replace it with16; otherwise continue | Compare depth with16; if unequal branch directly to the callback's continuation return1 |

Thus Modern rejects non16 **raw input depth** before calling the retained pixel classifier. The reference lets other raw depths reach that classifier and treats raw15 specially. “Reject” here means omit this input from table construction while returning1 to continue enumeration; it is not an exported error return.

The complete classifier `60002e80..60002f41` (193 bytes) is byte-identical. It recognizes selected16-bit mask layouts as well as RGB-mask-compatible24/32-bit inputs. Those latter branches remain present in Modern, but this callback's new raw-depth guard prevents its non16 descriptors from reaching them.

The retained callback still changes the **stored depth to15 when classifier result is3**, corresponding to its recognized RGB555 mask pattern. This is why the evidence supports16-bit input-format restriction without claiming every published depth DWORD equals16. Recognized RGB565 and RGB4444 masks follow their existing classifier paths; no new pixel-format conversion is introduced by the guard.

The callback's other changed branch is at `60002539`: when EBP is zero, reference jumps to the record-write block at `600024d6`, Modern to continuation return `60002506`. The earlier classifier-zero branch already exits at `600024aa`, and the intervening local instructions do not overwrite EBP. Under that ordinary local control flow this later zero branch is redundant; no reachable original null-write defect is asserted from the changed displacement.

## Registration and retained seeds

The bounded setup span `600026f6..600027ac` is identical across both DLLs. It publishes an allocated table pointer at `60040050`, prepares fixed640×480×16 and800×600×16 records at indices1/2, sets context/count `6004004c` to3, and passes callback `60002480` plus that context to an indirect vtable+20h call. Allocation/fill helpers and all failure paths are not independently audited by this span.

The callback's special640/800 handling, table stride28h and capacity calculation remain in the captured body. Other producers/consumers, allocation success, callback order and later changes to records are not exhaustively established. Complete `THRASH_about` body `60002330..60002412` (226 bytes) is also identical; its equality does not imply identical initialized mode data.

## State21 now rejects instead of returning no-op success

The complete `THRASH_setstate` body `600030c0..600033ef` is815 bytes. Its sole changed interval is the six bytes at `600031ac..600031b2`. The retained comparison tree reaches this branch with selector>=15h and preserved flags from `CMP EAX,15h`; the JBE therefore selects equality only, decimal state21.

Reference branches to `600030eb`, returning1 without applying this state. Modern branches to `60003180`, returning0. The remaining four bytes are NOPs. Higher selector handling is retained. This is an observable exported return-value change even though the old equality case performed no state write.

The EXE's [fog-support trial](original-modern-state14.md#support-producer-configuration-opt-in-followed-by-mode-trial) calls state21/value4 and clears its support flag on return0. Thus, **if this software DLL is bound and the common trial route runs**, Modern's changed return can reject that opt-in rather than report no-op success. This is a conditional consumer consequence, not proof of actual driver/configuration selection or blanket absence of visual fog. Do not confuse decimal21 with decimal15: the machine comparison literal is15h.

## Lock failure gains callback0 notification

The paired lock envelope `60003530..600036d0` is416 bytes. Its reference body ends at `600036c1`; Modern reuses the following original alignment bytes for a new failure tail. The byte accounting explicitly includes this reused padding rather than inventing a larger original function body.

In the inspected surface path, both versions invoke callback `[600400b4]` with stack argument1 at `600035fe..60003606`, perform the same indirect vtable+64h operation and store its status at `6003e04c`. For nonzero status:

- Reference jumps directly to `60003550`, which clears EAX and returns.
- Modern jumps to `600036c1`, invokes the same callback with argument0, then jumps back to that zero-return path.

Other lock paths and the success suffix are retained. No null-pointer check is introduced around the callback. The callback must return with its one stack argument removed, as the preexisting call sites already require. The failure tail does not clear every remembered surface pointer or establish general resource recovery; actual callback effects, registration, reentrancy and surface failure behaviour remain unobserved.

The complete unlock body `600036d0..6000374e` (126 bytes) is byte-identical. Its existing callback0 after successful unlock is not a new change.

## Page-flip failure reaches a shared notification tail

The complete page-flip envelope `60003750..60003890` is320 bytes, including the internal copy-loop path that jumps back to the earlier epilogue. Both versions send callback1 before their vtable+64h surface operation. On failure, both call the verified import `KERNEL32!OutputDebugStringA` at IAT `6003d21c` with `lock failed on writebuffer\n`. The diagnostic call is not a fatal-exit function.

Reference failure then jumps directly to frame cleanup at `600037c6`, omitting callback0. Modern changes that jump to `600037be`, sending callback0 before frame cleanup. To share this tail safely with the success path, Modern moves POP EBX/ESI/EDI to `600037bb..600037be`, before callback0. Those three registers are pushed only after successful lock; the failure path therefore bypasses these POPs and enters at `600037be` directly. The local stack accounting remains distinct for the two paths.

The callback now sees restored EBX/ESI/EDI on the successful path, whereas the reference callback was invoked before those POPs. Full machine-state equivalence is not claimed: callback register assumptions, incidental EAX/flags and transitive clobbers require their own contract. The successful drawing/copy instructions and subsequent frame cleanup remain byte-identical. No retry or guaranteed visible recovery is introduced by this local edit.

## Complete shared-code difference accounting

The script asserts that all44 differing bytes in the shared code-section extent belong to exactly one reviewed cluster, with no unassigned bytes or overlaps:

| Cluster | Differing bytes |
|---|---:|
| Raw-depth filter and later callback branch |8 |
| State21 return-value change |6 |
| Lock-failure callback tail |18 |
| Page-flip tail/order and failure jump |12 |
| **Total** | **44** |

This accounts for all nine maximal differing-byte intervals in the original map. It establishes localization and bounded local control-flow explanations, not every transitive/runtime consequence. Identical instructions can still operate on changed data, API results or caller state. PE resources, headers, relocation data and reference trailing material remain outside semantic coverage.

## Claim correspondence and remaining work

**MP100-067 receives partial static support:** final software callback filters raw input depth to16 and selected retained seeds use16. The reference/final comparison does not date this to1.0.0, authenticate pristine retail, validate all table writers or establish actual enumerated/rendered results.

The nine code intervals are retained in full and assigned to the four reviewed clusters above. Local byte/control-flow accounting is complete for this shared code extent. Resource/overlay meaning, complete runtime consequences, callback/ABI contracts and actual display acceptance remain open. This does not complete the EXE comparison or authenticate a retail baseline.

Two successive successful runs produced identical evidence manifests. Existing EXEs, saved Ghidra state, raw reference exports and maintained C were preserved; no toolchain, compilation, driver loading or new instruction probes were used.
