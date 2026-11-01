# Original versus Modern: display-mode admission and menu list

## Scope and evidence

**Static EXE comparison, not a renderer or UI test.** Supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`; official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline](original-modern-differences.md).

Run `python3 analysis/scripts/audit_display_mode_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-display-modes.json) records identities and half-open instruction spans for the matched enumerator `004bed90` and its menu-list consumer `00448210`. Original and Modern initializer calls bind those two entries directly; this establishes correspondence beyond the shared addresses. Raw assembly remains ignored under `analysis/captures/modern-differences/display-modes/`. No executable/Ghidra edits or game/probe execution.

Both use driver records of stride **0x28**, with width/height/depth DWORDs at `+0/+4/+8`, flags at `+0x10`, and fields tested at `+0x14/+0x18`. Driver descriptor `+0x3c` supplies the enumeration count and `+0x40` its array. Fields not independently established remain offsets, not invented C member meanings.

## 1. Enumerator changes

Original `004bed90..004bee71` calls the driver's about slot `[009ef980]` on each enumeration. Modern uses cached descriptor `[007a3a5c]`, accepted by its [loader](original-modern-renderer-loading.md), and calls separate eligibility helper `004bee60` for each record. Both enumerate indices 1 through the descriptor count inclusive, skipping record zero.

| Gate | Original enumerator | Official Modern eligibility helper |
|---|---|---|
| Record `+0x14` | Signed value at least 2 | Same threshold |
| Geometry | Low-32-bit `3*width == 4*height` (`004bede6..004bedfc`) | Calculated aspect value in 124..178 (`004bee78..004bee8c`) |
| Depth | 15 or 16 (`004bedfe..004bee06`) | 16 or 32 (`004bee8e..004bee99`) |
| Flags `+0x10` | Bit 0 set, bit 1 clear | Same tests |
| Extra size/budget condition | Requires signed truncating half of `[0055fed0]` to be at least low-32-bit `2*width*height` (`004bee15..004bee30`) | No corresponding test in this helper |

For ordinary positive, nonoverflowing dimensions, Modern computes `trunc(100*width/height)` and accepts 124 through 178 inclusive. This is **not an exact rational 5:4..16:9 test**: 124 is below 125, and truncation can admit values above 178%. The vendor's stated aspect range describes intended/common modes; these instructions give the actual approximate admission. At valid normal sizes, 1280×1024, 1920×1080 and 1920×1200 meet the Modern ratio gate; all three fail the original exact-4:3 geometry test. These are arithmetic deductions, not actual advertised or selected driver modes.

The [producer linkage below](#original-budget-is-a-renderer-selection-constant) establishes renderer-selection constants for the old budget operand; it is not a demonstrated hardware-memory measurement. Removing this local gate does not prove the driver or later allocation accepts every larger mode. Neither helper alone establishes a 640×480 minimum; lower-resolution hiding may reside in drivers or other paths and is not verified by this comparison.

Machine caveat: Modern uses low-32-bit IMUL, clears EDX, then signed IDIV by height, without a local zero/overflow guard. The simple mathematical formula above assumes positive normal dimensions and a fitting product. Arbitrary malformed records can depart from that model or fault. Original multiplications/comparisons also use machine-width results. No malformed record was supplied or runtime fault observed.

## Original budget is a renderer-selection constant

The [renderer dispatch investigation](original-modern-renderer-initialization.md) already identifies the original producer branches. The focused `python3 analysis/scripts/audit_renderer_budget_field.py` now retains hash-pinned literal loads/stores and consumer004bee15..004bee32 in a [linkage manifest](evidence/audits/renderer-budget-field.json), rather than repeating the whole dispatch investigation.

| Original selector(s) | Store to0055fed0 | Local constant |
|---|---|---:|
|1,2 |004b5aa4 |4 MiB |
|3,4 |004b5bd5 |8 MiB |
|5 |004b5c68 |2 MiB |
|6 |004b5d57 |2 MiB |
|7,8 |004b5df6 |2 MiB |

These constants cross calls in EBX/ESI/EDI; the interpretation assumes ordinary/documented callee preservation and no intervening alias mutation. Selector0, invalid selectors, failures and alternate writers are not assigned a value by this table. The candidate DLL names and environment override remain qualified in the dispatch chapter. The local constants do not establish actual installed VRAM or a provider-reported capacity.

For positive dimensions with fitting products, the retained gate is equivalent to **budget >=4*width*height**. Thus2/4/8 MiB permit pixel products up to524,288/1,048,576/2,097,152 respectively. For example,1024×768 passes the4/8 MiB cases but fails2 MiB;1600×1200 passes8 MiB but fails2/4 MiB. These are derived outcomes of this one gate, not enumerated modes or instruction probes. Original's additional4:3/depth/flag/buffer-field gates still apply. Wrapped products, negative state and full provider admission retain the earlier machine caveats.

Modern removes this particular fixed-budget test and uses the same address0055fed0 for a different [border-thickness value](original-modern-border-geometry.md). Preserve separate version-specific meanings. This closes the specific producer-linkage omission in the earlier report; it does not establish every field writer, driver allocation success or visible resolution support.

## 2. Callback interface changes

Original enumeration invokes the callback with EAX=index, EDX=width, EBX=height, ECX=depth and one stack DWORD derived from `record+0x18 >= 2`. Original `00448210` consumes those values and ends with `RET 4`.

Modern invokes callback EAX=index and EDX=record pointer at `004bedbd..004bedc1`, with no pushed per-record argument. Modern `00448210` saves all general-purpose registers with PUSHAD/POPAD and returns with plain RET. Applying the original callback signature to Modern would lose the record pointer and misrepresent stack cleanup. This is an ABI change in an internal callback pair, not a changed Windows API signature.

## 3. Menu list: append becomes sorted insertion/deduplication

Original collector `00448210..004482b8` uses count `00559218`, fixed-stride **0x114** records at `00661220`, and dynamic-label IDs beginning at `0x7a8`. It appends in enumerated order, without a local duplicate search/sort, while signed count is below **20**. Its initializer `004482c0` resets the count and label table before enumerating.

Modern collector `00448210..0044831d` uses count `00a18260`, records at `00a18330`, and IDs beginning at `0x866`. It binary-searches the existing list ordered lexicographically by unsigned DWORD keys, inserts by shifting records with STD/REP MOVSD, clears the new record and restores CLD before normal continuation. It still uses stride 0x114. This is EXE-side sorting; driver-side sorting claims are separate.

Key comparison length depends on `Hide16bitModes` (`007a2798`):

- Zero: compare three DWORDs, **width/height/depth**, so equal dimensions at different depths remain separate keys.
- Nonzero: compare two DWORDs, **width/height**, so the depths compete for one key. At `004482db..004482e1`, an incoming lower depth is rejected; an equal or higher depth updates that record. With the eligibility gate permitting only 16/32, the retained depth for shared dimensions is therefore 32 whenever a 32-bit candidate is enumerated.

This explains the specific “hide 16-bit modes when corresponding 32-bit modes exist” mechanism. It does not globally discard every 16-bit mode or force a 32-bit driver mode when no matching candidate exists. The cached descriptor and list initialization (`00448320`) matter: it enumerates only while count is zero, rather than always rebuilding as original initializer `004482c0` does. Other count-reset paths are not excluded by this chapter.

## 4. Count boundary differs from the headline limit

At `00448263..0044826c`, Modern checks `count > 0x64` with unsigned **JA**, rather than `count >= 0x64`. A new unique candidate is admitted when count equals 100 and increments it to **101**. Duplicate/replacement processing occurs before that admission check. Original checks signed `count >= 20` before appending.

Therefore this callback alone does not prove a strict 100-entry maximum. Driver enumeration caps, available allocation/storage, all reset/admission paths and ordinary reachability must be reconciled before claiming a runtime overwrite or failure. No such failure was tested or observed. Do not silently change JA to JAE during reconstruction merely because the README says 100.

## Count caching and the declared storage boundary

The expanded display audit scans the complete official EXE for the exact little-endian count address00a18260. All seven occurrences are instruction operands at00448232/65/83,00448326/4f/7d/d4; their instruction contexts are already captured. The sole direct writer is **INC at00448281**. No direct literal zero-reset store was found. This excludes neither computed/bulk/alias writes nor external mutation; it is not proof that the count can never reset.

Initializer00448320 **tests** count==0; it does not zero the count. On that path it clears51 DWORDs of label storage `[00a18264,00a18330)` and enumerates. If enumeration leaves count0, a later call can enumerate again. If count remains positive, this initializer returns without rebuilding. This is a concrete empty-versus-populated cache distinction; complete invalidation/lifetime and every caller remain unresolved.

The effective101-entry admission boundary must also be kept separate from the PE layout:

| Quantity | Verified address/value |
|---|---|
| Record bank base/stride |00a18330 /114h bytes |
|100 records, end exclusive |00a1ef00 |
|101st record (index100) |00a1ef00..00a1f014 |
| BSS size-field extent |0056e000..00a1f000 |
| Following section |`.reloc` starts00a1f000 |

The BSS header has **VirtualSize0, raw-size4b1000h, raw pointer0**, characteristicsc0000080h. The following `.reloc` header has characteristics42000040h. These noncanonical metadata fields are retained exactly; no file-offset-zero bytes are interpreted as initialized BSS, and actual loader mapping/protection/discard behavior is not observed.

For the conditional **101st unique append** (pre-count100, insertion index100), the admitted path at0044828b sets destination to that record and REP STOSD clears69 DWORDs,276 bytes. Its calculated final20 bytes lie beyond the BSS size-field extent, in the following section's declared range. This narrows the storage question beyond the headline count alone. It does **not** establish that any provider supplies101 eligible unique keys, that this path executes, that memory is writable there or that an overwrite/fault occurs. Matching labels or a nominal100-mode claim is insufficient runtime evidence either way.

Preserve the original JA boundary when reproducing machine behavior; an intentional strict100-entry C policy would be a documented behavior change. Further evidence should establish provider/caller admission and actual mapping/lifetime, rather than repeat this address arithmetic. No driver records, instructions or memory writes were executed by this audit.

## Catalog mapping and remaining work

- **MP100-001:** EXE eligibility changes support broader aspect/depth modes, with the approximate ratio gate above. Complete projection/HUD correction and actual driver availability are independent.
- **MP150-040:** EXE-side sorted insertion is verified in the matched collector pair.
- **MP150-042:** current `Hide16bitModes` grouping/higher-depth retention is verified; final code fallback zero is in [startup settings](original-modern-startup-policy.md).
- **MP120-008/017/024:** notes about 100 modes can refer to different renderer components. This EXE's changed collector/boundary is documented, but individual DLL capacities and first-release dates are not thereby verified.
- **MP150-030:** the executable eligibility helper has no below-640×480 exclusion; the [DX7 driver follow-up](original-modern-dx7-mode-admission.md) locates unsigned minimum-size rejection in the official packaged DLL. Other renderers and runtime remain unverified.

The [mode-selection comparison](original-modern-mode-selection.md) follows the original ID tree and Modern search/application consumers. The fixed budget producers are now linked above. Remaining work includes all mode-list count resets/storage, complete driver admission and original/Modern projection/menu scaling. Reuse the existing paired driver reports rather than restarting enumeration inventories. The [screenshot dimension audit](screenshot-worker-admission-audit.md) already explains why eligibility and selector fallback are not a general buffer-size proof; do not duplicate or overstate that research.

The [DX7 driver follow-up](original-modern-dx7-mode-admission.md) separates its verified minimum-size checks from the still-unverified exact640×480 depth-forcing claim.

## Selected-record helpers normalize the index but do not reject an empty list

The expanded [display audit](scripts/audit_display_mode_difference.py) now verifies the complete Modern selector/accessor region `00448348..0044837c` (52 bytes including three NOPs), with exact instruction bytes and capture hashes in [the manifest](evidence/audits/original-modern-display-modes.json). These helpers use the **menu's 114h-byte records**, not the driver's 28h-byte records; equal field offsets in those two layouts must not be conflated.

Selector `00448348..00448368` reads selected index `00a1825c`, compares it **unsigned** with count `00a18260`, and when index≥count sets the index global to zero. It then returns `00a18330 + wrap32(index*114h)` in EAX. Only EAX and flags are changed by its local instructions.

Two complete accessors call it:

| Modern accessor | End, exclusive | Return |
|---|---|---|
| `00448368` GetSelectedDisplayModeField10 | `00448371` | DWORD `[selected_record+10h]` |
| `00448374` GetSelectedDisplayModeDriverIndex | `0044837c` | DWORD `[selected_record+0]` |

The second saved name reflects analysis metadata; the directly verified contract here is the offset-zero DWORD. Neither accessor checks the returned pointer or count. With count zero, selector resets index to zero and returns the first record address anyway. Thus “index normalized” does not prove “valid selected mode”: empty-list admission and first-record initialization must be established by callers/producers. A maintained C interface must preserve the index-global side effect or deliberately expose a documented behavior change.

For valid nonempty lists within storage capacity, the unsigned comparison rejects negative-looking/high-bit index values as out of range when they are ≥count. It is not a complete protection against malformed counts, arithmetic wrapping or invalid storage lifetime. No such malformed input was executed.

## Original accessor counterparts and the race-init handoff

The audit now captures complete original field-zero getter **004482f0..0044832c** (60 bytes) and verifies the paired caller handoff. Original call004a3418 targets004482f0; Modern call004a3408 targets00448374. Both then store EAX to0055fec4 and immediately call their respective mode-application routines004bef50/004beeb0 with that value still live. These are actual matched consumer paths, not correspondence inferred solely from return-field offsets.

Original getter first calls **004482c0 unconditionally**, which rebuilds its list. It then compares selected index006fbc14 with count00559218 using **signed JL**; if not below count it resets the index to0, then returns field0 from `00661220 + wrap32(index*114h)`. ECX/EDX/EBP are locally saved/restored. Modern's tiny getter instead calls cached selector00448348, whose **unsigned** comparison and side effect are documented above, and reads field0. It does not invoke the list initializer itself.

Consequently the original getter observes a newly rebuilt list on this path, while Modern depends on prior cached-list initialization/lifetime. A negative index can pass the original signed check against an ordinary positive count; Modern's unsigned check rejects it for ordinary small counts. Neither version's local normalization proves a nonempty list: count0 can still lead to a field0 read from record0. These are conditional machine contracts, not observed invalid accesses or proof that arbitrary indices are reachable.

For field10, the [existing graphics-menu dataflow](original-modern-graphics-menu-transition.md#mode-copy-field-correspondence-is-now-established) already maps original00448330's full276-byte record copy plus a caller+10h read to Modern00448368's direct field load. That helper is separately retained in this audit; it must not be confused with original004482f0 merely because nearby addresses overlap the new code.

**Work status: both local accessor counterpart mappings done; evidence: verified static callers/field contracts.** Complete source-record equality, all initialization/invalidation paths, register expectations of every caller and runtime mode behavior remain unresolved. No executable, Ghidra or reconstruction-source changes were made.
