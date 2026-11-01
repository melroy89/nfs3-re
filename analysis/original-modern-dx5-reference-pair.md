# DX5 reference/final pairing and changed-byte map

## Baselines and reproduction

This comparison uses `d3da.dll` from the [author-hosted reference bundle](original-modern-original-reference-bundle.md), and `drivers/dx5/dx5a.dll` from the pinned official final Modern archive. The reference DLL hash also matches the previously inventoried local root `D3DA.DLL`; it does not match the separate setup-directory candidate. Author hosting and local equality do not authenticate pristine retail provenance.

| Role | Bytes | SHA-256 |
|---|---:|---|
| Reference `d3da.dll` | 98,641 | `ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02` |
| Final `drivers/dx5/dx5a.dll` | 72,704 | `6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42` |

Run `python3 analysis/scripts/audit_dx5_reference_final.py`. The [script](scripts/audit_dx5_reference_final.py) verifies both archive hashes before extracting members into memory, verifies member hashes, compares exports and selected whole file-backed sections, and records bounded disassembly in the [manifest](evidence/audits/dx5-reference-final.json). It never loads either DLL. Two successive successful runs produced identical manifest bytes during this increment.

## What is verified

| Area | Finding | Meaning and boundary |
|---|---|---|
| Export surface | All 34 names, ordinals, RVAs and forwarder fields match | Strong interface correspondence; not proof of identical ABI contracts or all function bodies |
| Image base | Both `60000000` | Reported VAs are preferred-image addresses, not runtime mappings |
| Whole code section | 55,296 bytes at RVA `1000`; 710 differing bytes in 25 maximal contiguous differing-byte intervals | Complete raw inventory within this section, including padding/data if present; intervals are not function or feature counts |
| Import section | All 2,048 bytes match at RVA `f000` | File-backed section equality, not equality of resolved imports or dynamic calls |
| Data section | All 7,168 bytes match at RVA `10000` | File-backed initial data equality, not equality of subsequent writes |
| `THRASH_about` | Complete 180-byte body `60001020..600010d4` differs in two immediate bytes only | Exact descriptor publication change below |
| Selection helper and `THRASH_selectdisplay` | Complete combined span `60001618..60001734`, 284 bytes, is identical | Includes the helper called by `about`, plus exported selector at `60001654`; changed subordinate callees remain possible |

All end addresses above are exclusive. The manifest records every changed interval in the code section with both byte strings and addresses, so later work can start from the remaining changes rather than rediscover their locations. This does not inventory every byte difference in the entire files: headers, relocation/export/resource sections and appended file material have separate boundaries.

## Exact descriptor publication difference

Both `about` bodies populate a descriptor at `60012010`, call helper `60001618`, then return descriptor address in EAX. At `60001090`, the five-byte instruction changes as follows:

| Reference | Modern |
|---|---|
| `ba 90 20 01 60` — `MOV EDX,60012090` | `ba 00 9e 01 60` — `MOV EDX,60019e00` |

Only bytes at `60001091..60001093` differ. Both bodies then store EDX at `600010ba` to `60012050`, descriptor offset `+40h`. The verified finding is a changed published pointer. The descriptor also retains magic `44334435h` and `+8=68h`; the latter must not be called a structure size or API version merely from this literal. See the [loader analysis](original-modern-renderer-loading.md).

The callback and selected setup paths are now compared below. Exhaustive consumers and actual display acceptance remain separate. The previously analysed DX7 table policy does not establish the DX5 policy.

## Storage distinction

Every section in these two DLLs has `VirtualSize=0`. Their `.bss` headers have RVA `12000`, raw-data pointer zero and nonzero raw-size fields: reference `7e00h`, Modern `8e00h`. The reference descriptor pointer falls inside the reference declared extent; the new pointer `60019e00` is exactly the reference extent's end and falls inside the expanded Modern extent, using those nonzero size fields.

This establishes a declared uninitialized-storage expansion of `1000h`. It does not establish file-backed initial values or observed loader mapping. The script does not read file offset zero as BSS contents. Actual zero filling, subsequent initialization writes and ownership of the expanded region remain distinct questions.

## Mode callback and selected initialization paths

The extended manifest captures complete reference callback `600017bc..600018e3` and Modern callback `600017bc..6000187d`, plus setup tails in two callers and the complete retained pixel classifier `600025f0..600026b1`. These are static comparisons of the pinned DLLs, not calls to the graphics API.

Both callbacks receive a descriptor pointer as their first stack argument and a context/count pointer as their second, and return using `RET 8`. Input fields used as width, height and depth are respectively `+0ch`, `+08h` and `+54h`; pixel-format classification receives input `+48h`. The retained classifier examines RGB masks and depth and returns zero for unrecognized combinations. It recognizes 555/565/4444-style 16-bit layouts and RGB-mask-compatible 24/32-bit layouts; this is parser acceptance, not device support.

| Mechanism | Reference | Modern |
|---|---|---|
| Early admission | Rejects zero classifier; no general minimum-dimension filter | Rejects zero classifier, then unsigned width below640 or height below480 |
| Record size | `28h` bytes | `28h` bytes |
| Setup clear request | `4b0h` bytes in EBX at `60001b80` and `600021da` | `fa0h` bytes at the same sites, through retained helper `600052e8` |
| Seed entries in captured setup tails |640×480×16 at index1;800×600×16 at index2; count3 |640×480×16 at index1; count2; no fixed800×600 seed in these tails |
| Matching | Special fixed640/800 cases, then append using context index with unsigned limit30 | Scan from index1 until width zero or exact width/height/raw-depth match; new key allowed only if context count<100 |
| Placement | Fixed slots plus append order | First matching or empty slot; no sorting or shifting in this callback |
| Depth after classification | Classifier3 changes stored depth to15 | Same conversion, after raw-depth comparison |
| Buffer-related fields | Quotient and quotient−1 at record `+14h/+18h` | If quotient<=3, same; if quotient>3, both fields become3 |

The Modern quotient is unsigned `[60010eb4] / (width * height * bytes_per_pixel)` with 32-bit wrapping products. `bytes_per_pixel` is2 for stored depth<=15, otherwise depth shifted right3. The reference computes its denominator before the later classifier3-to-depth15 conversion. Ordinary supported dimensions/depths avoid a zero denominator; arbitrary wrapped products are not validated by this inspection. The cap is a code fact, not a proof of available surfaces or successful allocation. The identity of `[60010eb4]` requires its producer before calling this a complete memory-budget model.

The scan compares **incoming raw depth before conversion**. Consequently repeated 16-bit input classified as555 can miss a previously stored depth15 record. Do not describe this as normalized-key deduplication or silently repair it in reconstruction. Actual enumeration inputs/order and resulting duplicates were not observed.

The seed alone does **not** prove that every640×480 record is reported as16-bit. For example, the Modern callback has no dimension-specific depth coercion: a recognized640×480×32 input can pass the local guards and reach a different-depth slot, provided capacity remains. That is a conditional static path, not proof that the OS supplies that input or the game selects it. The retained 32-bit classifier also exists in the reference; its presence by itself cannot explain a new32-bit rendering claim.

The two setup tails push callback `600017bc` and context address `6001204c` before an indirect vtable call at offset20h. This connects the published descriptor's `+3ch` count cell and `+40h` table pointer to callback construction in those paths. Exact COM-object provenance, exhaustive setup/callback callers, executable consumers and failure paths remain follow-up. The fill helper's arguments are recorded as requests here; the complete transitive fill implementation is not claimed as independently audited by this increment.

### Release-note correspondence

- **MP100-062:** partial support for a concrete final-DX5 lower-height filter, alongside an additional lower-width filter; historical1.0.0 introduction and the actual displayed mode list remain unverified.
- **MP100-063:** partial support for retaining recognized32-bit entries in the larger callback table. The original classifier already accepts32-bit formats; actual mode selection/device/rendering paths are still required to establish the claimed change in operation.
- **MP100-064:** the fixed640×480×16 seed is verified, but the absolute word “always” is not established by this callback. Distinct-depth entries remain locally admissible. Runtime enumeration and consumers must settle the full claim.

## Actionable follow-up and acceptance

- **Done, verified:** artifact pairing, full export inventory, whole code-section byte map, import/data section equality, complete `about` comparison and retained selection span.
- **Done, verified:** complete callback comparison, selected setup seeds/count requests, raw-key scan policy, dimension filter and local quotient cap.
- **Pending, unresolved:** exhaustive initialization/consumers, actual32-bit operation and absolute640×480 reporting policy; classify remaining code intervals into mechanisms.
- **Later evidence:** authenticated retail provenance, historical introduction, full relocations/resources, runtime display enumeration and rendering acceptance.

No release-note item is promoted by this bounded pairing alone. The broader original/Modern investigation remains incomplete. Existing EXEs, saved Ghidra state, maintained C and raw exports were not edited; no target instructions, OS graphics calls or new probes were run.
