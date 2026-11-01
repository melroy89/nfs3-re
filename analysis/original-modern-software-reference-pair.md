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

## Claim correspondence and remaining work

**MP100-067 receives partial static support:** final software callback filters raw input depth to16 and selected retained seeds use16. The reference/final comparison does not date this to1.0.0, authenticate pristine retail, validate all table writers or establish actual enumerated/rendered results.

The nine code intervals are retained in full. This increment interprets the mode-callback changes; the separate state-handler, lock/unlock/page-flip intervals still need their own control-flow comparison. Do not call the whole44-byte set semantically explained yet. Resource/overlay meaning, complete runtime state, ABI compatibility and actual display acceptance remain open.

Two successive successful runs produced identical evidence manifests. Existing EXEs, saved Ghidra state, raw reference exports and maintained C were preserved; no toolchain, compilation, driver loading or new instruction probes were used.
