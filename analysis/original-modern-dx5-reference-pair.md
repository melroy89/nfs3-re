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

## Removed numeric state-selector15h route

The audit now compares the complete `THRASH_setstate` body `60002b58..600034d1` (2,425 bytes). Only two maximal differing-byte intervals occur in that body: `60002e47..60002e78` and `6000341c..60003498`. These are subsets of the existing whole-code map, not additional byte differences.

The entry reads its selector from the first stack argument and value from the second, initializing EBX=1. The retained comparison tree sends selector15h to `60002e47`. In Modern, that address is an unconditional jump to `60002b8e`, which clears EBX and returns EAX=0 through the normal `RET 8` epilogue. The remaining44 bytes before the next retained block are NOPs. The reference instead checks selector15h and dispatches by value:

| Value for selector15h | Reference local path | Modern local path |
|---|---|---|
|2 or8 | Stores value at `600129f0`, returns1 | Returns0; removed store |
|4 | Calls retained generator `60002994` with destination `600129b0`, EDX=`600128b0` and a pushed DWORD from `60010f0c`; then calls expander `60002a50` with EAX=`600129b0`; returns1 | Returns0; this invocation route removed |
|0 | Calls adapter `60004f64` for numeric device states `1ch=0`, then `23h=0`; returns1 | Returns0; calls removed |
|1 | Calls the same adapter for `1ch=1`, then `23h=0`; returns1 | Returns0; calls removed |
|Other values | Returns1 without these stores/calls | Returns0 |

Reference tails `6000341c..60003498`, containing the value4 and value0/1 routes, are entirely replaced by124 NOP bytes in Modern. Other parts of the state-handler body are byte-identical, including the distinct selector14h route's rejection. This is an export-level dispatch change, not just deletion of unused-looking bytes.

The generator, expander and numeric state adapter remain byte-identical in their separately captured complete bodies. The generator uses x87 operations to emit64 byte values; the expander has a256-iteration output loop. This supports a table-related interpretation. A fog-related role was initially inferred from this mechanism; the EXE FogSupport trial linkage below now establishes a game-facing fog-admission consumer. This does not establish API enumeration names or a visible effect merely from numeric constants. A precise mathematical reconstruction and floating-point edge-case audit of those helpers is outside this comparison.

The adapter prepares an object if needed, optionally calls a pending-work helper, and invokes object `[60010f48]` vtable offset5ch with the numeric state/value. It returns1 only when that indirect call returns zero, otherwise0. The reference selector15h tails discard this result and return their own1. Therefore the original exported success return does not by itself prove device acceptance. The complete object/interface provenance and subordinate helper contracts remain open.

This removes **one caller route** to retained table helpers and state writes. It does not prove all such calls, table consumers, fog effects or other rendering paths disappeared. Caller use, side effects through aliases and actual rendering remain untested. No release-note claim is promoted solely from this numeric-selector finding.

## Lock failure now notifies the callback

The complete `THRASH_lockwindow` body `600011d4..60001366` has62 differing bytes; its suffix from `6000123a` onward is identical. The complete unlock body `60001368..600013d0` is also identical. The change is concentrated around the surface operation and its failure branch:

| Step | Reference | Modern |
|---|---|---|
| Before indirect surface call | If callback `[6001289c]` is nonnull, calls it with stack argument1 | Calls new adapter `60001880` with EAX=1; adapter conditionally invokes the same callback with argument1 |
| Surface operation | Object from `[60010ee4]`, vtable offset64h; stores returned status at `60010ea4` | Same operation/arguments, moved nine bytes earlier |
| Returned status zero | Continues to shared success suffix | Same suffix |
| Returned status nonzero | Returns EAX=0 without a corresponding callback0 in this path | Calls adapter with EAX=0, then reaches the same zero-return tail |
| Later ordinary unlock | Clears lock state/pointer and conditionally calls callback0 | Byte-identical |

The new17-byte adapter `60001880..60001891` copies its EAX input into EBX, reads the callback pointer, invokes it with one pushed argument if nonnull, restores EBX and returns. Its callback contract requires the callee to remove that argument, as the old direct-call path already did; a malformed callback is not made safe by this wrapper. The wrapper does not specify a useful return value, preserve all caller registers or synchronize pointer changes.

The retained state handler's selector13h accepts a nonnull pointer and copies eight DWORDs to `60012888`; callback cell `6001289c` is offset14h in that copied block. This identifies one registration route, not the final callback target or all possible writes. The retained unlock callback still uses a direct indirect call rather than this new adapter.

The bounded finding is an added failure notification, plausibly balancing the preceding notification. It is not a claim of general lock recovery: both versions still store the surface pointer before the call; this changed failure path does not clear it, and the separate lock flag is set only by the success suffix. Callback behaviour, concurrent mutation, surface-object provenance, actual lock failures and observable recovery remain untested. There is no retry in this new local failure branch.

## Changed-code accounting and stopping boundary

The script now asserts that every differing byte in the shared55,296-byte code-section extent belongs to exactly one of these disjoint reviewed clusters:

| Cluster | Differing bytes |
|---|---:|
| Descriptor pointer publication |2 |
| Lock callback notification |62 |
| Enumeration callback and new notification adapter |283 |
| First mode-setup tail |91 |
| Second mode-setup tail |99 |
| Removed state-selector route |173 |
| **Total** | **710** |

There are zero unassigned differing bytes **within that code section**. This is localization coverage supported by bounded explanations above, not whole-DLL semantic equivalence, proof that every runtime consequence is understood, or completion of the EXE investigation. Changed PE headers, relocation/resource/export sections, appended material, runtime initialization and unchanged dependencies remain separate. The script retains the original25 maximal differing-byte intervals, so grouping has not discarded raw differences.

## EXE fog trial connects to the rejected DX5 selector

The extended audit now pins the official EXE and extracts `drivers/dx5/thrash.ini` from the same pinned final archive. The config names `File=dx5a.dll` and `Type=d3d`, and has **no FogSupport key**. The [EXE state analysis](original-modern-state14.md#support-producer-configuration-opt-in-followed-by-mode-trial) already establishes the opt-in/trial mechanism; these captures connect it to this particular DX5 handler instead of leaving the removed selector's game-facing role unnamed.

| EXE location | Verified local operation | Consequence for the inspected DX5 path |
|---|---|---|
| `004b597b..004b599e` | `GetPrivateProfileIntA("THRASH","FogSupport",0,path)` via verified import slot00534670; normalize nonzero to1 and store007a3a54 | Reading the bundled config without an overriding key requests default0; this is conditional on the actual path/API result |
| `004b5bb0..004b5bd6` | If007a3a54 is nonzero, invoke bound THRASH state slot009ef96c with `(21,4)`; return0 clears the flag; then issue `(21,0)` regardless | Modern DX5's selector15h rejection returns0 for both requests. On this trial route even a prior nonzero opt-in is cleared |
| `00431c1c..00431c33` | Complete recomputation writes007a3a64 =007a3a54 AND006fd1d4 AND00559234 | If the support flag is zero when this function runs, admission becomes zero regardless of the other two inputs |

**Decimal21 and hexadecimal15h are the same selector.** They are not decimal state15. The [export-binding analysis](original-modern-renderer-loading.md) identifies slot009ef96c as `_THRASH_setstate@8`; this DLL's export inventory and complete dispatcher comparison establish its rejecting target.

The driver’s changed return therefore has a concrete game consumer: it feeds the support gate, not merely an ignored status in an isolated table helper. The name association is supported by the EXE's FogSupport key and trial, without requiring a guessed Direct3D enum name. This also explains why a disabled default and a rejecting probe can coexist: the default avoids the trial, while the trial rejects an explicit opt-in if that common route is used.

This is a conditional static chain. It does not prove which INI/DLL was selected in a live session, that every initialization path performs the trial, that later writers preserve zero, or that every kind of visual fog is absent. The [initialization report](original-modern-renderer-initialization.md) distinguishes the common software/d/v route from the generic route that skips this trial. It is not a new claim of universal backend equivalence, a historical introduction date or successful rendering. Existing EXE and database bytes remain unchanged.

## Actionable follow-up and acceptance

- **Done, verified:** artifact pairing, full export inventory, whole code-section byte map, import/data section equality, complete `about` comparison and retained selection span.
- **Done, verified:** complete callback comparison, selected setup seeds/count requests, raw-key scan policy, dimension filter and local quotient cap.
- **Done, verified:** selector15h now rejects requests; removed table/state tail blocks and unchanged helper bodies are documented.
- **Done, verified:** lock failure gains callback0 notification; all710 differing code-section bytes are assigned to reviewed clusters.
- **Done, verified:** the EXE FogSupport trial consumes selector15h rejection on its common route; zero support forces zero on the captured admission recomputation.
- **Pending, unresolved:** exhaustive initialization/consumers, actual32-bit operation, absolute640×480 reporting policy and remaining selector15h callers/effects; qualify runtime consequences and PE/non-code differences.
- **Later evidence:** authenticated retail provenance, historical introduction, full relocations/resources, runtime display enumeration and rendering acceptance.

No release-note item is promoted by this bounded pairing alone. The broader original/Modern investigation remains incomplete. Existing EXEs, saved Ghidra state, maintained C and raw exports were not edited; no target instructions, OS graphics calls or new probes were run.
