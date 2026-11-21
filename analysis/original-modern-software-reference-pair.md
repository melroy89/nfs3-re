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

The reference has28,514 trailing bytes after its last raw section; Modern has none and adds a1,536-byte resource section. This accounts for the net26,978-byte file-size reduction arithmetically, not semantically. The later [non-code ledger](#softtri-non-code-ledger-equal-data-changed-relocations-and-debug-overlay) identifies the appended debug carrier and added version resource; full debug/resource semantics remain qualified. A large size reduction must not be equated with removal of that much executable code.

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

This accounts for all nine maximal differing-byte intervals in the original map. It establishes localization and bounded local control-flow explanations, not every transitive/runtime consequence. Identical instructions can still operate on changed data, API results or caller state. The non-code follow-up below inventories resources, normalized relocations and reference trailing material; complete headers and runtime interpretation remain outside this code accounting.

## Claim correspondence and remaining work

**MP100-067 receives partial static support:** final software callback filters raw input depth to16 and selected retained seeds use16. The reference/final comparison does not date this to1.0.0, authenticate pristine retail, validate all table writers or establish actual enumerated/rendered results.

The nine code intervals are retained in full and assigned to the four reviewed clusters above. Local byte/control-flow accounting is complete for this shared code extent. The follow-ups below identify the debug carrier and version resource; complete header/resource/debug interpretation, runtime consequences, callback/ABI contracts and display acceptance remain open. This does not complete the EXE comparison or authenticate a retail baseline.

Two successive successful runs produced identical evidence manifests. Existing EXEs, saved Ghidra state, raw reference exports and maintained C were preserved; no toolchain, compilation, driver loading or new instruction probes were used.


## Historical and debug follow-ups

The existing reference/final audit above remains the canonical44-byte code explanation. The newer [historical audit](evidence/audits/softtri-mode-fix-history.json) adds140/150 dating, allocation linkage and a non-code ledger. The separate [debug parser](evidence/audits/softtri-reference-debug.json) recovers bounded name records with export anchors. These complement the earlier work; they do not represent another set of44 newly discovered changes.

## Historical SoftTri fix initializes a mode-bound input

The [SoftTri audit](evidence/audits/softtri-mode-fix-history.json), reproduced with `python3 analysis/scripts/audit_softtri_mode_fix_history.py`, pins140/150 `drivers/softtri/softtria.dll` members and compares the entire245,760-byte file-backed code section. **Exactly19 bytes change**, all inside complete254-byte mode callback `60002480..6000257e`;245,741 code bytes match. This is code-section coverage, not equality of whole PE files or runtime behavior.

|Changed interval, exclusive end |140 |150 |
|---|---|---|
|`60002499..6000249e`,5 bytes |MOV ESI,16 |Jump over three NOPs; prior gate already requires incoming depth16 |
|`60002537..60002545`,14 bytes |Signed height≥480 filter, jump/padding |TEST EBP; zero exits; otherwise pass ESP to imported GetSystemInfo |

The retained continuation at `60002545` reads DWORD `[ESP+4]`, divides it unsigned by40, then compares that quotient with the context count before a new40-byte record is selected. The150 call binds IAT `6003d200` to **KERNEL32!GetSystemInfo**. [Microsoft's API contract](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsysteminfo) defines its output as SYSTEM_INFO; the [32-bit structure layout](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-system_info) places dwPageSize at+4. Therefore150 supplies a system-information-derived bound input where140's callback has no corresponding local buffer initialization. For a hypothetical reported4096-byte page, the quotient is102; this is arithmetic illustration, not an observed API value or a promise of102 visible modes.

The callback still requires depth16, a nonzero pixel classifier, and has special640×480/800×600 routes before this generic path. Classifier3 can store depth15. The changed generic path removes the old local height filter; do not silently preserve it in a150 translation. The first edit removes a locally redundant value assignment, not proof of all-state equivalence. Full classifier side effects/aliases, buffer allocation ownership, context lifetime and actual API/catalog values remain separate.

Packaged `thrash.ini` also drops LightBeams=0, retaining File=softtria.dll, Type=software and DirectDrawLagFix=1. This config edit is distinct from the19 code-byte changes. The DLL's BSS section has raw pointer0; apparent bytes obtained by treating file offset0 as BSS initial data are not used as runtime evidence.

**MP150-038 gains partial static support:** a concrete mode-bound initialization repair is localized, with every code-section difference assigned. The release note's unspecified bug symptom, complete capacity safety, device/display acceptance and visible output remain unverified. No DLL, graphics/system API, game or target instructions were executed, and no executable or saved Ghidra database changed.

### SoftTri bound matches its retained page-sized allocation request

The expanded [SoftTri audit](evidence/audits/softtri-mode-fix-history.json) retains setup span `600026e7..600027ac`, identical140/150. GetSystemInfo at `600026ef` fills stack SYSTEM_INFO; the following VirtualAlloc call at `60002707` requests its+4 page-size DWORD, with allocation flags3000h and protection4. The returned pointer is published at `60040050`. The setup seeds fixed640×480×16 and800×600×16 rows1/2, sets count `6004004c` to3, pushes callback `60002480` at `6000277a`, and passes count-address context to object vtable+20h at `600027a9`.

This establishes a local allocation-to-registration chain, not an assertion that allocation always succeeds or every object implements the assumed mode API. No successful provider/device call was observed.

For a successfully allocated P-byte table and a callback reporting the same page sizeP, its new quotient is `C=floor(P/40)`. With ordinary valid count n≥3, the generic insertion proceeds only when **n<C**, selects byte offset40n and increments the count. Hence the new record ends at `40(n+1)≤40C≤P`. The reserved rows1/2 additionally require enough allocated extent for those writes. This is a conditional extent argument, not a global lifetime/bounds proof.

The old callback reads the corresponding stack DWORD without this local GetSystemInfo initialization even though setup already used the API in its separate frame. Those are different stack buffers: setup's earlier query does not establish the callback-local value. The150 addition now obtains the same kind of bound source locally. Actual page-size consistency, allocation failure, corrupted/aliased context counts, classifier side effects, later mutations and non-generic paths remain separately qualified. Do not replace this with an unconditional “all SoftTri mode handling is safe” claim.

The concrete MP150-038 mechanism is now supported by allocation and callback-registration evidence as well as the complete19-byte code delta. The unspecified visible bug symptom still has no runtime reproduction. No target, allocator or graphics instructions were executed.

### SoftTri non-code ledger: equal data, changed relocations and debug overlay

The same expanded [SoftTri audit](evidence/audits/softtri-mode-fix-history.json) now records the following reference/final PE boundaries independently of the44-byte code delta:

|Area |Reference→final evidence |
|---|---|
|Import section |All2,048 bytes at RVA3d000h identical |
|File-backed data |All6,656 bytes at RVA3e000h identical |
|Export section |All1,536 bytes at RVA43000h identical, corroborating34 matched exports |
|Non-ABSOLUTE relocations |9,115→9,116 entries; remove HIGHLOW RVA37bfh, add HIGHLOW RVAs36c5h/37c2h |
|Version resource |Final adds1,536-byte section at RVA49000h; reference has no such section |
|Appended payload |Reference has28,514 bytes at file offset275,968; final has no overlay |

The relocation changes correspond to the new lock-failure callback operand and moved page-flip callback operand already assigned above. Raw relocation-section bytes differ more extensively; comparing normalized entries avoids mistaking repacking for thousands of semantic code edits. File-backed data equality does not prove equality of subsequent initialization or runtime globals.

The reference overlay begins ELF32 little-endian/i386 metadata, with type ET_EXEC and entry0. Its five-entry section-header table describes null plus `.debug_info` (22,480 bytes), `.debug_abbrev` (38), `.debug_aranges` (5,676) and `.shstrtab` (52). The audit retains offsets and hashes plus the final16 raw bytes. This establishes an appended DWARF carrier worth inspecting later; no source-code recovery, complete symbols/types or executable-purpose claim follows from its section names. It is not loaded as an ordinary PE section by this file layout.

Section names AUTO/DGROUP become `.code`/`.data`; final also adds `.rsrc`. The new version metadata identifies “SoftTri Thrash Driver Modern Patch”, FileVersion2016.10.25.0006 and ProductVersion1.0.0. Its “Based on…” comment is self-description, not independent authentication of source ancestry. Header-field interpretation, every resource node and debug-payload semantics remain pending. BSS has raw pointer0 in both files, so file-offset0 bytes are not treated as BSS initial values.

This ledger extends the reconstruction reference beyond C function bodies while preserving clear gaps. No ELF/PE payload, resource or target instruction was executed and no original/final bytes changed.

### Reference debug records recover names with34 export anchors

The [bounded debug audit](evidence/audits/softtri-reference-debug.json), reproduced with `python3 analysis/scripts/audit_softtri_reference_debug.py`, inspects the exact appended payload without modifying or executing it. GNU readelf2.42 exits1 with `.debug_abbrev section not zero terminated`: the38-byte section contains four complete abbreviation definitions but no terminating zero abbreviation entry. The audit records the stock reader's output/error evidence; it does not label that decoder successful.

A separate bounded parser accepts the exact declared abbreviation extent and only its observed forms1/8/12/16, enforcing compilation-unit lengths, address size4, version2 and string/field bounds. It consumes the complete22,480-byte info extent, yielding **173 units and1,034 named records**:

|Numeric tag |Records |What is retained |
|---|---:|---|
|11h |173 |Unit/source identifiers, including source-file paths and library unit names |
|0ah |510 |Address-bearing name records |
|34h |351 |Address-bearing name records |

The parser preserves numeric tags/attributes rather than inventing prototypes or structure definitions. Every extracted record and unit offset is retained in the JSON. This is a supported narrow extraction, not a general DWARF validator or proof of source/type completeness.

All34 PE exports match a debug name after replacing export prefix `_THRASH_` with `_SOFTTRI_`. For **every listed export**, stored debug address+1000h equals its PE RVA; the manifest enumerates all34 anchors. In particular, the mode callback's debug record `_SOFTTRI_modeenum@8` has stored1480h, corresponding to RVA2480h. These anchors corroborate the callback/export correspondence used in this comparison. Applying that adjustment to every unanchored address remains an inference requiring instruction/data validation.

The unit identifiers include `C:\nfs3\sdon\softtri\striasm.asm` and `striabout.c`; other records identify runtime/library units. Paths and symbols do not recover file contents, establish all function boundaries or justify final-version Ghidra signatures. Reference retail provenance remains qualified. No automatic labels/types were applied and no payload bytes were repaired, appended or executed. Use these records to guide later original/final inspection, preserving the raw address and artifact hash alongside any proposed mapping.

### Original-reference SoftTri already has the local system-info query

The reference callback already contains GetSystemInfo.140 replaces that local query with a height filter;150 restores it. The [historical audit](evidence/audits/softtri-mode-fix-history.json) therefore supports a local regression-and-repair interpretation relative to this author-hosted reference, without authenticating pristine retail provenance or dating the first introduction of the140 behavior.

Reference→150 has eight code-byte differences, and150→final has36 disjoint differences. Together these are the same44 bytes assigned by the [existing complete code map](#complete-shared-code-difference-accounting), including the [state21 return](#state21-now-rejects-instead-of-returning-no-op-success), [lock notification](#lock-failure-gains-callback0-notification) and [page-flip cleanup](#page-flip-failure-reaches-a-shared-notification-tail). These mechanisms need not be investigated again merely because they also appear in the newer historical manifest. MP100-066 has partial correspondence support; source ancestry, exact100 introduction, callback contracts and runtime effects remain qualified.
