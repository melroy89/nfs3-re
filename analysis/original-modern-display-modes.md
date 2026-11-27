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

Original collector `00448210..004482b9` uses count `00559218`, fixed-stride **0x114** records at `00661220`, and dynamic-label IDs beginning at `0x7a8`. It appends in enumerated order, without a local duplicate search/sort, while signed count is below **20**. Its initializer `004482c0` resets the count and label table before enumerating.

Modern collector `00448210..0044831d` uses count `00a18260`, records at `00a18330`, and IDs beginning at `0x866`. It binary-searches the existing list ordered lexicographically by unsigned DWORD keys, inserts by shifting records with STD/REP MOVSD, clears the new record and restores CLD before normal continuation. It still uses stride 0x114. This is EXE-side sorting; driver-side sorting claims are separate.

Key comparison length depends on `Hide16bitModes` (`007a2798`):

- Zero: compare three DWORDs, **width/height/depth**, so equal dimensions at different depths remain separate keys.
- Nonzero: compare two DWORDs, **width/height**, so the depths compete for one key. At `004482db..004482e1`, an incoming lower depth is rejected; an equal or higher depth updates that record. With the eligibility gate permitting only 16/32, the retained depth for shared dimensions is therefore 32 whenever a 32-bit candidate is enumerated.

This explains the specific “hide 16-bit modes when corresponding 32-bit modes exist” mechanism. It does not globally discard every 16-bit mode or force a 32-bit driver mode when no matching candidate exists. The cached descriptor and list initialization (`00448320`) matter: it enumerates only while count is zero, rather than always rebuilding as original initializer `004482c0` does. Other count-reset paths are not excluded by this chapter.

In retained 1.4.0 the collector still uses the append path
with signed count rejection at 101. In 1.5.0 the sorted collector
tests `007a2798` at `00448221` to choose the key length, and the
settings code stores the integer reader's result at `004b564e`.
The named key and these operands are present in every retained
release from 1.5.0 onward. The complete 269-byte collector at
PE RVA `48210h` matches in all five releases from 1.5.0 through
1.6.0 (SHA-256
`2c6100e3605e3edeb50d30502df12c9ab50f1d532b989648940b07b87d8eeea9`).
The 1.6.1 collector is a different byte sequence and retains
the same key-length check. This dates the setting-to-collector
path independently of which mode rows a driver supplies.

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

## Field10 retains the Z-buffer indication while the label suffix disappears

The audit now links menu record+10h to its producer and named controls in both executables. Original enumerator004bee4c..004bee5c forms Boolean **signed driver-record+18h >=2** and pushes it to the callback. Original collector loads that stack value at00448246 and stores it at menu+10h through00448258. Modern computes the same normalized0/1 threshold directly at004482e8..004482f5. This closes the selected-field meaning gap without asserting that every provider's underlying+18h field has one fully reconstructed layout.

Both collectors format dimensions/depth with retained literal **`%d x %d x %d`**. Original then tests menu+10h and appends literal **` (z)`** when nonzero; Modern does not append that suffix. Its old string location00538d58 is now empty. This is a concrete label-construction difference, not evidence that Z-buffer indication or depth rendering was removed.

Graphics setup looks up exact tokens **`Z_BUFFER`** and **`Z_BUFFER_TEXT`** at00538e20/2c. If either item is missing, it skips the shown capability policy. Otherwise a zero field indication ORs item flags01h and1001h respectively; nonzero clears those bits usingFEh/EFFEh masks. Original reads the field from its copied local record, while Modern uses the [direct field accessor](#original-accessor-counterparts-and-the-race-init-handoff). The flag operations and token bindings identify the intended Z-buffer capability indication; actual menu rendering/interactions and successful provider depth-buffer operation are not tested.

Modern's deduplication is also relevant: an accepted equal/higher-depth candidate replaces the row's+10h indication with its own value. It does not aggregate an OR across merged depth candidates. Under Hide16bitModes grouping, capability therefore follows the retained candidate rather than “any mode at these dimensions supports it.” Which capabilities actual16/32-bit provider entries supply remains unverified.

**Verified:** shared threshold/field/consumer linkage and removed original `(z)` append. **Pending:** every provider field contract, all list/caller lifetimes, UI flag effects, actual labels/depth rendering and historical attribution. This is static evidence only; no target instructions, menus or driver records were executed.

## Historical EXE capacity expands from51 to101 local entries

**Confidence: verified static instructions and paired1.1.0/1.2.0 boundary. Work status: done for this local EXE producer/consumer chain; partial for the advertised limits.** The [historical audit](scripts/audit_mode_capacity_history.py) pins both author-hosted archives and EXE hashes and rechecks the supplied original guard. Its [manifest](evidence/audits/mode-capacity-history.json) retains complete collectors/initializers, dynamic-label routing, record-label accessors, raw bytes and hashes. No enumeration, target instructions or UI was executed.

| Property | Supplied original | Historical1.1.0 | Historical1.2.0 |
|---|---|---|---|
| Collector entry |`00448210` |`00448210` |`00448210` |
| Signed reject condition at`00448235` |count>=20 |count>=51 (`33h`) |count>=101 (`65h`) |
| Count storage |`00559218` |`00559218` |`00559218` |
| Record bank,114h-byte stride |`00661220` |`00a18400` |`00a18320` |
| Label WORD bank |`005591ec` |`00a18398` |`00a18254` |
| Initializer’s label clear | Existing paired audit |104 bytes =52 WORDs |204 bytes =102 WORDs |
| Dynamic mode-label IDs | Existing original evidence |`0866..0898` inclusive =51 |`0866..08ca` inclusive =101 |

For initialized counts starting at0 and ordinary serialized calls, the historical appenders admit indexes0..50 and0..100 respectively. They reject before writing another record when count reaches51/101. Neither historical collector sorts or deduplicates locally; the entire169-byte pair differs only in the record-bank operand, label-bank operand and capacity immediate. The later final sorted collector uses another branch form (`JA count>100`) but also admits101 unique records locally, as documented above. These are distinct implementations with the same resulting ordinary local count bound at1.2.0/final, not identical bodies across all releases.

The initializer `004482c0..004482e8` in both historical versions resets count to0, clears the label bank with an extra WORD beyond the admitted entries, and calls enumerator`004bed90` with callback`00448210`. This supports a terminating zero after a maximally appended list under the stated non-aliasing/lifetime assumptions; it does not imply that the record bank is file-backed or that runtime mapping was observed.

### Menu consumer expands with the producer

The historical20-byte descriptor at`005566b8` binds key`winsize`, the version’s label WORD bank and selected-index storage`006fbc14`. Each appended record publishes ID`0866+index` into that bank. The dynamic-string router at`004d17b0..004d17ca` admits that **inclusive** ID range and calls`00448400`. Its complete35-byte accessor subtracts`0866`, multiplies by114h, adds the matching record base and returns record+14h, the formatted label. It has no separate count check.

Thus the51st/101st entries are not excluded by these specific label-routing bounds. This is a matched producer→descriptor→string-consumer chain, stronger than finding a larger immediate alone. It still does not prove every cascade/input consumer, provider record, real enumeration result or selected display works at maximum capacity.

### Release-note conclusions and limits

- **MP100-009**, advertised 20→50: the original cap is 20 and the retained 1.0.0 and 1.1.0 builds both admit 51 entries locally. The collector, initializer, menu descriptor, label router and label accessor match byte for byte between those releases. Compare PE VAs `00448210` (169 bytes), `004482c0` (40), `005566b8` (20), `004d17b0` (26) and `00448400` (35) in their archived EXEs. Runtime capacity remains unverified.
- **MP120-008**, advertised100 EXE modes: the direct1.1.0→1.2.0 pair now verifies expansion51→101 and corresponding label/clear/accessor changes. The introducing historical boundary for this mechanism is established; the strict headline number is not the local bound.
- **MP120-017/024** concern renderer components in the release-note context. This EXE comparison cannot independently establish either DLL’s capacity or provider behaviour; retain their separate evidence status.

Provider ceilings can prevent the final admitted slot from ever being populated; no such ceiling is assumed here. Record-bank storage/protection, all reset paths and actual display support remain separate questions. Preserve the observed signed comparisons and inclusive label ranges in a version-faithful C reconstruction. Do not silently substitute advertised50/100 caps or infer a runtime fault merely from local admission arithmetic.

## Early Modern already bypasses the budget gate and has a broader depth test

**Verified static historical predicates; no display-mode execution.** The [admission-history audit](evidence/audits/mode-admission-history.json), reproduced with `python3 analysis/scripts/audit_mode_admission_history.py`, pins supplied original, author-hosted1.1.0 and official final EXEs. It retains complete original/early enumerator envelopes`004bed90..004bee72` and the complete67-byte final eligibility helper`004bee60..004beea3`.

| Local eligibility property | Supplied original |Modern1.1.0 |Final1.6.1 |
|---|---|---|---|
|Geometry |Exact wrapped3W=4H |Ordinary truncated100W/H in124..178 |Same ordinary ratio interval |
|Depth |15 or16 |**Signed depth>=16** |16 or32 |
|Original budget/size gate |Present |Bypassed |Absent from new helper |
|Descriptor source |Indirect about call |Retains indirect about call |Cached descriptor in enclosing enumerator |

Early mode enumeration replaces the original size/budget block with`JMP004bee32` at`004bee10`, then32 NOPs at`004bee12..004bee32`. The aspect arithmetic is already changed to IMUL100/IDIV and bounds124/178. Its depth test is`CMP ECX,10h; JL reject` at`004bedfe..004bee03`: it does not yet implement final's equality tests. A hypothetical24-bit record can therefore pass this early local predicate while final rejects it. This is **not** evidence that a bundled driver can enumerate or render24-bit modes.

For the following instruction-derived cases, assume ordinary positive fitting dimensions, flags bit0 set/bit1 clear, signed field+14h>=2, and the original8 MiB budget case. Each result covers only the local admission rules, not actual provider enumeration or mode selection:

| Candidate W×H×depth | Original,8 MiB |Early1.1.0 |Final1.6.1 |
|---|---|---|---|
|1920×1440×16 |Reject: size/budget |Admit locally |Admit locally |
|1024×768×24 |Reject: depth |Admit locally |Reject: depth |
|1024×768×32 |Reject: depth |Admit locally |Admit locally |
|320×240×16 |Admit locally |Admit locally |Admit locally |

The last case reinforces the existing limit: these EXE predicates alone do not enforce a640×480 minimum. Conversely, bypassing the old budget gate does not make all resolutions valid. Final still has ratio/depth/flag restrictions, driver enumeration/storage limits and machine-width arithmetic; providers, mode callbacks and allocations can impose additional limits.

**MP100-003 advances to partial historical support:** a concrete original size restriction is removed in early Modern, with useful larger local candidates admitted. “No unreasonable maximum limits” remains broader than this evidence.The restriction is already bypassed in 1.0.0. Actual mode menus and rendered operation remain unverified. The follow-up below now dates depth narrowing to1.4.0→1.5.0 and separates later descriptor caching. This also separates at least three edits—budget removal, aspect/depth policy and later descriptor-cache refactor—rather than silently assigning final's entire helper to the first release. No driver, game, instruction probe, Ghidra write or executable mutation occurred.

## Depth narrowing and descriptor caching occur in different releases

**Verified static release boundaries; no mode execution.** The [refactor-boundary audit](evidence/audits/mode-refactor-boundaries.json), reproduced with `python3 analysis/scripts/audit_mode_refactor_boundaries.py`, freshly pins1.4.0,1.5.0 and1.6.0 archives/EXEs plus official final1.6.1. It also checks1.4.0's enumerator against the prior hash-retained1.1.0 bytes, without claiming a fresh early extraction in this follow-up.

| Boundary | Verified selected-body change |
|---|---|
|1.0.0–1.4.0, all six retained releases |Complete 226-byte inline enumerator identical |
|1.4.0→1.5.0 |Inline signed depth>=16 predicate replaced by shared67-byte eligibility helper requiring16 or32; enumerator/search use that helper |
|1.5.0–1.6.0, all five retained releases |Complete enumerator, nearest-mode search and eligibility bodies identical |
|1.6.0→1.6.1 |Enumerator/search replace about-slot calls with cached-descriptor loads; eligibility body unchanged |

The 226-byte inline enumerator at PE RVA `bed90h` has SHA-256
`84a8ea1447b72f9083948d93858788cbc0a1bd79128b8f7771dff7980eed7f47`
in each of the six retained Modern archives through 1.4.0.
The corresponding hosted original span hashes to
`ff88ba280cea0606c66f86e484e3acb4fbc63cb59a8340c443f9ca39516fbb0d`.
This dates the budget bypass and the broader geometry and depth
checks to 1.0.0 in the EXE enumerator.

The complete 67-byte eligibility helper at `004bee60..004beea3`
also matches in all six retained releases from 1.5.0 through 1.6.1
(SHA-256 `caa1e8a8639b8e171f5884195237da48bad3748b0ba79e38e627df6a32daa860`).
The 1.4.0 inline depth threshold already admitted 32-bit rows if
the other checks passed. The 1.5.0 change retains 32 and 16 while
excluding other depths that could pass the earlier threshold, such
as 24. This is a statement about EXE eligibility, with actual
provider modes outside the comparison. Reproduce the equality checks
by extracting each retained `nfs3.exe` and hashing PE RVA `bee60h`
for 67 bytes, `bed90h` for 59 bytes, and `bedcch` for 147 bytes.
The latter two lengths apply to 1.5.0 through 1.6.0.

In1.6.0 both complete consumers call slot`009ef980`: enumerator`004bed90..004bedcb` at`004bed99`, and nearest-search`004bedcc..004bee5f` at`004beddd`. Final replaces both with`MOV EAX,[007a3a5c]` at those sites. Their following count/table reads use descriptor+3ch/+40h as before; the one-byte instruction shrink repacks later instructions and branch displacements. Final envelopes end at`004bedca` and`004bee5e`, respectively. Its nearest-search epilogue also moves the saved-EAX store ahead of restoring ESP. The complete captures retain those differences; this is not described as a sole same-length call patch or a full machine-state equivalence proof.

The [loader](original-modern-renderer-loading.md) and [descriptor lifecycle](original-modern-renderer-lifecycle.md) explain cache acceptance/refresh separately. Eliminating a provider query changes the point at which descriptor state/side effects can be observed; byte-identical eligibility does not prove equivalent mode lists when that source can change. Neither query-result validity, cache lifetime under all callers nor actual initialization/recovery is established by the local substitutions.

**Status: done for these selected release-boundary checks; confidence: verified static.** Budget removal, depth narrowing and descriptor caching must remain distinct changes in reconstruction planning. This does not date every texture-loading cache consumer, prove measured optimization, validate renderer callbacks, qualify arbitrary malformed records or complete the whole EXE comparison. No driver, game, new instruction probes, Ghidra or executable changes occurred.

## DX6 public mode count gains its leading slot in150

**Verified descriptor/callback/insertion linkage; complete consumer bounds and runtime mode visibility untested.** The [DX6 count audit](evidence/audits/dx6-mode-count-history.json), reproduced with `python3 analysis/scripts/audit_dx6_mode_count_history.py`, resolves the shared counter left opaque in the [historical DX6 code edit](original-modern-state14.md#dx6-has-a-separate-small-code-edit-at-the-same-boundary). It pins140/150 archives and exact driver hashes; the complete about, callback and insertion bodies are byte-identical across the pair.

| Storage/contract | Address/value |
|---|---|
|Descriptor returned by `_THRASH_about@0` |`6003bd00` |
|Count field |Descriptor+3c =`6003bd3c` |
|Published table pointer |Descriptor+40 stores`6003f000` |
|Inserted-record base |`6003f028` |
|Record stride |40 bytes (28h) |
|Explicit initialization clearing |4,000 bytes from`6003f028`, excluding the preceding40-byte slot |

The two table bases differ by **one record**. Callback`60001cd0..60001d90` filters incoming records, builds a40-byte temporary record and calls insertion helper`6000e500` at`60001d7c`. The complete157-byte insertion helper searches using the first three DWORDs as an unsigned comparison key. An equal key overwrites the40-byte record without increasing the count. A new key increments the count if it was below100, shifts subsequent records with backward DWORD copying, clears the vacated space and copies the new record. The inserted record addresses use`6003f028 + index×40`, while external clients receive the earlier base`6003f000`.

Initializer`60001c50` clears that insertion arena and the count, invokes the callback-bearing enumeration call, then returns in140. In150 its added INC increments the same public count after the call. For an ordinary fresh completed enumeration that inserted N distinct records, the reported count changes **N→N+1**, now accounting numerically for the leading public slot. Derived examples are0→1,3→4 and100→101. These are arithmetic consequences under the stated condition, not observed enumerations or a claim that the leading slot is a newly valid display mode.

The descriptor and both table bases lie in the `.data` section's virtual tail beyond its raw file bytes. They are loader-zero-filled storage initially, **not file-backed zero records obtained by reading PE offset0**. The explicit initializer clears only the inserted arena; this audit does not establish all later writes or contents of the leading slot. The about body also invokes a device-selection helper before returning the descriptor; that helper's complete side effects remain outside this focused review.

### Count convention and reconstruction limits

The [EXE search comparison](original-modern-mode-selection.md#modern-descriptor-lookup) already establishes that its inspected helper skips index0 and scans1 through count **inclusive**. Therefore adding a public leading slot must not be casually described as “restoring the last mode” for every consumer: exclusive-count and inclusive-count loops observe different extents. At the insertion limit100 the new reported count is101, and all subsequent record accesses/admission must be qualified independently. No out-of-bounds runtime event or valid catalog at that limit is asserted here.

The added INC is not guarded by a local enumeration-result check; the callback does not test insertion's return before continuing. Failures, provider callback ordering and complete external consumers remain unknown. The insertion helper uses ambient direction-flag assumptions for its forward comparisons/copy, uses STD for shifting and executes CLD before continuing; a C port must preserve the verified record movement and comparator rather than imitate those machine operations without their preconditions.

**The counter's structural purpose is now resolved:** it is the exported mode count, not a lighting or fog value. The edit remains separate from MP150-033's unverified taillight repair. Complete driver semantics, leading-slot policy, mode-menu visibility, device acceptance and all bounds remain later work. No DLL, enumerator, API, game, instruction probe, compiler or Ghidra write occurred.

## DX6 extra count slot reaches inclusive scans but can fail admission

**Verified selected consumer contracts; conditional zero-slot extent argument, not universal mode safety.** The [consumer audit](evidence/audits/dx6-count-consumers.json), reproduced with `python3 analysis/scripts/audit_dx6_count_consumers.py`, binds the preceding driver count/layout evidence to author-hosted140/150 EXE consumers.

Both140 inline enumeration and150 factored enumeration begin with public index1 and exit only when signed index>descriptor count. Therefore they include index=count; they do not use a conventional exclusive count bound.150's59-byte enumerator`004bed90..004bedcb` and147-byte nearest search`004bedcc..004bee5f` call the same67-byte eligibility helper`004bee60..004beea3` before collecting/scoring a record. That helper first tests record+10 bit0; a clear bit exits rejected **before** the height division and before callback dispatch.

Let N be the number of distinct inserted records after the checked fresh-clear/insertion-only driver lifecycle.150 reports N+1, and its last visited public row N+1 is at insertion-base`6003f028 + N×40`. The retained insertion helper writes only the occupied prefix; its ordinary sorted shifts and replacements do not populate the next unused record.

| N |150 reported count / final visited index |Extra record address |Inside the4,000-byte explicit clear? |
|---|---:|---|---|
|0 |1 |`6003f028` |Yes |
|3 |4 |`6003f0a0` |Yes |
|99 |100 |`6003ffa0` |Yes, last cleared record |
|100 |101 |`6003ffc8` |No |

Thus for **0≤N<100**, if no other/aliased writes modify that next record, it remains zero from initialization and150's enumeration/nearest admission rejects it before callback/scoring. This narrows the earlier count-convention uncertainty: adding the leading-slot contribution need not add a visible resolution in these consumers. It is not proof that the complete140/150 menus are equivalent; depth gates, callback ABI, collector ordering and other changes remain separately documented.

At N=100 the extra row lies beyond the explicit clearing extent. That does not prove it is outside mapped storage or contains nonzero data; it means this particular zero-row argument cannot establish its contents or admission. Initial loader zero-fill, later adjacent writes, other consumers and complete provider lifetime need separate evidence. No malformed catalog or fault was produced.

### Search rejection is not a direct-switch guard

150's nearest-search tail retains unconditional fallback index1 when no candidate wins (`004bee4e..004bee56`), without validating record1. In the N=0 derived case, rejecting the zero row therefore does not itself create a valid fallback mode.

150 application`004bef50` clamps incoming indices below1 to1 and forms its record offset. The same-current-index route branches away before the changed-index count gate. The changed-index gate`004befc2..004befdb` admits signed indices1..count **inclusive**; it is not the eligibility helper used by enumeration/nearest search. Follow-up driver calls, failure handling and actual selection must not be replaced by an assumption that “it was in range, so it was eligible.” The [mode-application report](original-modern-mode-selection.md) retains the later final implementation's independently qualified behaviour.

**Resolved:** selected inclusive visitation, zero-slot rejection ordering and a bounded N<100 clearing/insert-lifetime argument. **Remaining:** counter/record alias writes, capacity-edge contents, fallback/same-current/direct-switch outcomes, all external clients and device acceptance. These findings do not establish a universal missing-last-mode repair or a runtime bounds failure. No game, DLL, mode API, instruction probe, compiler or Ghidra write was used.


## DX8 early size filter and later16-bit admission

**Partial static provider evidence for MP110-007 and MP150-039; no display-mode execution.** The [three-build audit](evidence/audits/dx8-mode-admission-history.json), reproduced with `python3 analysis/scripts/audit_dx8_mode_admission_history.py`, pins110 `dx8.dll` and140/150 `drivers/dx8/dx8a.dll` from their exact author-hosted archives. The inspected component is distinct from the game EXE and the DX5/DX6 providers discussed above.

### Enumeration producer and published records

Imported `d3d8.dll!Direct3DCreate8` is reached through thunk `60011244` and its output is published at `6001ed24`. The mode builder `60004550..600047f2` uses that object's slots18h/1Ch. The pinned [MinGW-w64 interface header](https://raw.githubusercontent.com/mingw-w64/mingw-w64/master/mingw-w64-headers/include/d3d8.h) identifies these as GetAdapterModeCount/EnumAdapterModes; the [types header](https://raw.githubusercontent.com/mingw-w64/mingw-w64/master/mingw-w64-headers/include/d3d8types.h) defines the output as Width, Height, RefreshRate and Format. Cached header hashes and instruction captures are retained in the audit.

The builder clears256 forty-byte records at `600429a0`, publishes that table through `60042900`, and starts its count at2. `_THRASH_about@0` returns descriptor `600428c0`, whose+3Ch count is `600428fc` and+40h table pointer is `60042900`. Reserved/unpopulated rows and all EXE consumers are not fully qualified by this builder audit.

### Two separate policies

| Selected policy |110 |140 |150 |
|---|---|---|---|
|Minimum input dimensions |Unsigned width≥640 AND height≥480 |Same |Same |
|Depth admission after recognized format |Require32 |Require32 |Require nonzero reported depth;32-only check removed |
|Special slot1 |640×480 after32-only gate |Same |640×480 only when depth16 |

The complete674-byte110/140 builder bodies are identical. In the early body, `600045f3/600045ff` compare width/height against640/480; unsigned-below branches go to next-mode iteration before record writes. This verifies the lower-size filter is already present in110, not its exact introduction versus an unavailable100 baseline. It is not proof that every published slot contains a valid filtered mode: the function reserves entries and API/output lifetime remains conditional.

All140→150 builder differences are inside `600045de..60004623`; the earlier prefix and later suffix match. The old `CMP EAX,32 / JNE next-mode` disappears.150 retains the preceding nonzero classifier/depth tests and adds depth16 to the640×480 special-slot condition.

A concrete derived case is API format23, R5G6B5: both retained classifiers map it to internal token4 and depth16. With a valid640×480 enumeration output and the other local preconditions,140 rejects it at its32-only gate;150 can store width640, height480, depth16 and token4 at slot1. This explains a selected16-bit admission mechanism without asserting that arbitrary formats are limited to16/32 or that a device actually offers/accepts the mode.

### Limits and reconstruction implications

EnumAdapterModes' result is not checked locally before reading its output. Successful complete output is therefore a premise, not a guaranteed API outcome. Other format classifiers, record capacity/deduplication, reserved slots, EXE selection and device activation remain separate. The early32-only builder does not itself prove the advertised ugly-menu symptom was fixed, and source ancestry is not inferred from exported names.

MP110-007 and MP150-039 advance vendor-only→partial. Preserve unsigned size tests, local failure behaviour and the distinct slot1 policy in reconstruction. No DLL/API, game or target instructions were executed, no toolchain was installed and no executable or Ghidra database was changed.


### The mode builder accounts for the DX8 executable-byte changes in 1.5.0

The [hash-pinned 1.4.0 and 1.5.0 DX8 members](original-modern-renderer-loading.md#dx8-package-history) retain image base `60000000`, entry RVA `975e`, and the same 47 export names, ordinals, RVAs and forwarder fields. Match executable bytes by RVA because 1.5.0 merges the old executable `PACODE` section into `.text`. Comparing section names or ordinal positions overstates the code change.

Compare RVA `1000..12000` (old raw `.text`) and `12000..18000` (old raw `PACODE`) against the same ranges in the new `.text` using `pefile.PE.get_data`. The only differing positions are the 63 consecutive bytes `45de..461d`, in the mode-builder edit above. The entire old `PACODE` payload, including its raw padding, is identical at its original RVA. This scopes the DLL's executable-byte delta to mode enumeration. The PE section layout, resources and non-code state are outside that conclusion, and selecting a different display mode can still change rendering inputs.

### DX8 ordinary mode order is append order, with a special slot

The expanded [three-build audit](evidence/audits/dx8-mode-admission-history.json) records the builder's selected ordering contract. After initialization count2 reserves indices0/1. Ordinary accepted modes use the current count as their index, increment it, and write a40-byte record; the ordinary capacity guard rejects when count≥256. Under fresh initialization and no external/alias mutation, these ordinary records therefore occupy slots2 onward in accepted enumeration order, not a width/height sort.

Before append, the routine checks existing active ordinary rows. Its equality key is record offsets0/4/8/0Ch: width, height, depth and internal format token. The flags bit at+10h must be set for a row to match. A match skips the incoming record. RefreshRate from the API output is **not** included in this compared key. For otherwise admitted records, the first occurrence of a key supplies the ordinary slot; a later equal key does not move it.

The special640×480 case instead writes slot1 before reaching ordinary capacity/deduplication. Later admitted special records overwrite that slot without increasing the ordinary append count. Its depth condition differs by release as shown above. Thus even a late API640×480 entry can populate the earlier slot1, while ordinary1024×768 followed by800×600 entries can remain in that order at slots2/3. This is a derived conditional example, not an observed device catalog. An absent special entry can leave the reserved slot unpopulated despite the initial count2.

The248-byte region `6000462d..60004725` is entirely NOP in all three checked builders. That is a byte fact, not proof of the source or history of removed ordering code. The compared append/deduplication tail is retained140/150.

**MP110-008 remains vendor-only as a comparative claim:** the early DX8 ordering mechanism is now documented, but its precise advertised difference from an earlier provider/catalog is not established. No actual API mode order, final visible list, refresh selection, complete consumer bounds or runtime mutation was observed. Do not equate a documented current ordering algorithm with proof of every historical ordering change.


### The 1.1.0 DX8 provider and game store different startup depths

The archived 1.1.0 game EXE (SHA-256 `59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72`) still stores 640×480×16 at `004b6027..004b6052`, matching the original setup's three initial values. Its DX8 mode builder independently rejects ordinary enumerated modes of depth other than 32 and writes qualifying 640×480 rows into special slot 1. These are different variables in different components. The 16-bit EXE store therefore coexists with a provider record advertising 32 bits if a matching row is enumerated.

The checked legacy mode-selection branch at `00517692..005176aa` compares ECX with `0x140` and, on equality, calls the renderer's set-video-mode slot with stack arguments `(4, 2, 1)`. Thus this branch does not request slot 1 directly. In archived 1.1.0 `dx8.dll`, the export at `600038b0` treats the first argument as a row index. It retains row 4 if in range and active, and substitutes row 1 otherwise. It separately maps the third argument 1 to `0x10` in `6001eed0`, a field distinct from the catalog row depth. This identifies a conditional route to the reserved slot and gives a concrete reason to keep the EXE's mode ID, the catalog depth and the provider's separate depth-related setting distinct.

The archived 1.1.0 `dx8.dll` (SHA-256 `c58ffb6810ca335602766d9179f2fcd8ecf9c9127c98ffa43cd76c0f8fb91e62`) also matches the 1.4.0 and 1.5.0 DLLs over the complete set-video-mode export `600038b0..600039fe` and worker `60003b80..60004001`. Extract the exact DLL members and hash the end-exclusive VA spans for reproduction. Their SHA-256 values are `a5415010562bb8d87a9bac7b6ed154c30b0b864c5ed3a3ebd699e7ff2073be2a` and `dfe38c3603223c84d598f3663e59e823a96b43996afa159498a319e64bc9674c`. The worker already contains both format requests described below: adjusted depth 16 selects R5G6B5 and adjusted depth 32 selects X8R8G8B8. The 32-bit catalog filter therefore coexists with a 16-bit activation path from the first retained DX8 release.

The two colour-depth adjustment helpers and depth/stencil selection also match across 1.1.0, 1.4.0 and 1.5.0. Concatenating `60004010..6000413b`, `60004140..6000420b`, `600043e0..60004521` and the jump table `60004524..6000454c` in address order gives SHA-256 `0a478f721366b138c893ee31112ec3c6d71a962b27a1b9f64d310cdbe83958b4` in all three DLLs. The checked `(4, 2, 1)` game call selects the D16-first depth/stencil candidate order through its third argument, while the back-buffer colour depth follows the separate adjustment rules below. Where the windowed helper succeeds, it uses the GDI-reported colour depth. The other helper can fall back from an enumerated 32-bit colour row to 16-bit if its format checks require that fallback. Neither path establishes the format accepted by an actual device.

The worker chooses the first adjustment attempt at `60003be8`. A nonzero DWORD at `6001ed50` permits the GDI-based helper at `60003c04`. A zero flag or a zero helper return takes the format-selection helper at `60003c26`. If that helper also returns zero on this route, execution branches to `60003fdc` before building the presentation record. The 1.1.0 export `_THRASH_setstate@8` at `60005490` masks the state ID to its low 16 bits before dispatch. State `0x12` maps through byte table `600073f4` to index 15, and jump-table entry `60007370` targets `6000642d`. Its write at `60006431` copies the second argument to the gate, so zero disables the GDI attempt and a nonzero value enables it. The 1.1.0 game calls helper `005246a0` before its mode request when `00564364` is zero. With the startup bit at `00564390` set, `005177f6` passes EAX=0. With that bit clear, `0051766b` passes EAX=1. The helper saves EAX in ESI and, if its initialization gates permit, passes `(0x12, ESI)` to slot `009ef96c` at `00524716..0052471f`. Thus the checked startup branch with the initialized bit set can explicitly disable the desktop-depth attempt, while the alternate branch can enable it. This is conditional on reaching the state call and using the DX8 provider. Runtime gate values and subsequent state writes remain unverified.

The game-side state route predates DX8. The hosted original, 1.0.0 and 1.1.0 executables match over `00517655..0051767d` and `005177f6..005177fd`, which choose the argument, and over `005246a0..0052471f`, which includes the conditional state call. Reproduce by extracting each EXE and comparing those three end-exclusive VA spans. The 1.1.0 DX8 provider therefore interprets an existing game request. The [pinned original Direct3D provider](original-modern-dx5-reference-pair.md) also handles literal state `0x12`. Its export at `60002b58` takes the unsigned range between `0x11` and `0x13`, stores the second argument at `60010eac` via `60002bb4`, and returns 1. A checked consumer at `60001cc6` tests that DWORD and branches to `60001e73` when zero. This establishes the flag-setting contract on both providers, with different downstream implementations. The two original branches make different mode setup requests. The zero branch at `60001e73` sends the selected record's width and height and the prepared depth to vtable offset `0x54` on object `60010eb8`, with two trailing zero arguments. The prepared depth normalizes 15 to 16 at `60001cba..60001cc4`. The nonzero branch skips that call and first invokes offset `0x18` on the same object with a 108-byte surface descriptor and output pointer `60010ebc`. The interface identity is anchored by the query at `60001937..60001954`: vtable slot zero takes the IID at `60011970` and output address `60010eb8`. The stored IID is `b3a6f3e0-2b43-11cf-a2de-00aa00b93356`, which identifies `IDirectDraw2`. Its 32-bit vtable names the zero-branch call `SetDisplayMode` and the nonzero branch's first call `CreateSurface`. [Wine DirectDraw interface declarations](https://github.com/wine-mirror/wine/blob/master/include/ddraw.h). Actual desktop depth, surface format and successful rendering remain unverified.

On the original driver's nonzero-state path, the first `CreateSurface` call at `60001d17` sets `DDSURFACEDESC.dwSize=0x6c`, `dwFlags=1` and `ddsCaps.dwCaps=0x200`. These fields request a primary surface with `DDSD_CAPS` alone. The request supplies neither dimensions nor an explicit pixel format, so the prepared 15→16 depth does not constrain this first surface. The resulting surface properties and later render-target formats are separate. [DirectDraw structure and flag definitions](https://raw.githubusercontent.com/wine-mirror/wine/master/include/ddraw.h)

After a successful `SetDisplayMode` on the original driver's zero-state path, the surface request at `60001e95..60001ee9` instead sets `dwFlags=0x21` (caps and back-buffer count) and `dwCaps=0x2218` (primary, flipping, complex and 3D-capable). A nonzero `60012ba8` adds video-memory capability, producing `0x6218`. The initial back-buffer count is the routine's last stack argument minus one. If `CreateSurface` returns `0x8876017c` and the unsigned count exceeds one, the retry at `60001ef5..60001f28` decrements the count and tries again. The descriptor still omits an explicit pixel format. Thus the explicit colour depth on this path comes from the preceding display-mode request. The actual surface formats and memory placement remain unverified.

Final Modern DX5 retains both checked DirectDraw paths. Comparing the [pinned original and final DX5 pair](original-modern-dx5-reference-pair.md), the 91-byte state-test and primary-surface span `60001cc4..60001d1f` matches (SHA-256 `340fac759c60f6fa8747ec32fc5faa9e7688fab51bb839f3fb0c78dc45ff5b9c`), as does the 181-byte display-mode, flip-chain and retry span `60001e73..60001f28` (SHA-256 `7a6e3d46f115d836df95c19783269e222e7f2757d99f358b43b602a90a462423`). The 1.1.0 DX8 path is a separate provider implementation. These equal spans leave input selection and resulting formats dependent on the game and driver state.

This gives MP110-009 partial static support for a concrete provider mechanism. The record selected at menu startup, the final back-buffer format and the reported visual repair remain unverified. A 32-bit row in the provider catalog alone cannot settle those questions.

### DX8 activation already contains16-bit requests before150

The [activation audit](evidence/audits/dx8-mode-activation-history.json), reproduced with `python3 analysis/scripts/audit_dx8_mode_activation_history.py`, compares140/150 with the same pinned DLLs and header snapshots. The complete334-byte `_THRASH_setvideomode@12` at `600038b0..600039fe` and1,153-byte worker `60003b80..60004001` are byte-identical. This separates the preceding changed enumeration gate from retained activation code.

The export checks signed input index≥0 and<count, then row+10h bit0. Failure substitutes index1 at `600038d6` without rechecking that row locally. It can route through a posted message464h on its cross-thread path, or directly call the worker at `600039a7`; actual message delivery and synchronization are untested. This is not a universally validated-index interface.

The worker reads width/height/depth from an active record. An inactive record supplies fallback640×480×16 before adjustment. It then passes field pointers to helpers `60004010` or `60004140`; their selected adjustment policies are documented below, so selected catalog values are not assumed to survive unchanged.

After those adjustments, it clears52 bytes at `60020fa0` and builds the thirteen-field presentation record. The checked32-bit SDK layout identifies the first fields as BackBufferWidth/Height/Format:

|Adjusted depth |Format request at parameter+8 |
|---|---|
|16 |23 = R5G6B5 (`60003cc5`) |
|32 |22 = X8R8G8B8 (`60003cd6`) |

On selected branches, that parameter pointer reaches the previously traced Direct3D8 object/device chain: CreateDevice at vtable+3Ch (`60003d4c`, output object `6001ed28`) or Reset at+38h (`60003d5e`). Local result handling and dimension retries follow; no API acceptance was observed. Unsupported/other depth values do not gain an invented validated mapping here.

Thus the16-bit activation-request branch **already exists in140**;150's new catalog admission can expose it without changing these two bodies. Conversely, the older32-only enumeration gate never proved all activation paths requested32, because fallback/adjustment paths are separate. MP150-039 remains partial: catalog and selected activation requests are linked, while selector/flag and index/slot lifetime, errors, actual display depth and rendered output remain unverified. No DLL/API or target instructions were executed and no executable/Ghidra state was changed.


### DX8 adjustment can override the selected depth

The expanded [activation audit](evidence/audits/dx8-mode-activation-history.json) retains the complete299-byte helper `60004010..6000413b` and203-byte helper `60004140..6000420b`. Each body is identical in140/150. These are retained policies, not newly discovered150 changes.

| Path/helper | Selected policy | Consequence |
|---|---|---|
|Windowed adjustment `60004010` |Queries GetDC(0), then GetDeviceCaps indices8/10/12. Requires reported depth16 or32 and signed reported width≥640; clamps requested dimensions downward using signed comparisons. |Successful writeback uses the GDI-reported depth, regardless of incoming selected depth. There is no separate reported-height≥480 guard here. |
|Other adjustment `60004140` |For requested depth32, tries formats22 then23; for every other requested depth, tries23 then22. |First admitted candidate writes depth32 for format22 or16 for23. Null object or no admitted candidate returns0. |

The pinned `wingdi.h` snapshot maps those indices to HORZRES, VERTRES and BITSPIXEL; [Microsoft's API description](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-getdevicecaps) explains the reported dimensions/depth. These are values returned by GDI, not independently measured physical display properties. Header hashes and both complete disassemblies are retained in the audit.

Preserve one unusual branch exactly: windowed CheckDeviceFormat at `600040c5` returning **nonzero** skips CheckDeviceType and continues to helper `600043e0`. A zero first result instead calls CheckDeviceType at `600040e1`, whose result must be zero to continue. This is not a conventional requirement that both checks succeed. No failed API call or resulting symptom was observed, and reconstruction must not silently correct this control flow.

The other helper requires zero results from both CheckDeviceType (`6000419b`) and CheckDeviceFormat (`600041b9`) for each candidate. Both paths then require nonzero from `600043e0`, which receives the ancillary-format output pointer. Its selected search/write contract is documented below; no candidate is asserted actually available.

Consequently, admitting a16-bit catalog row does **not** guarantee16-bit output: windowed adjustment may replace it with reported32, and the other path can fall back from16 to32. Conversely, requesting32 can fall back to16. These statements describe conditional requests/writebacks, not rendered results. Follow-up priorities are selector/flag initialization and mutation, complete caller/device lifetime and runtime acceptance. No DLL/API/target instructions were executed, and no executable or saved Ghidra database changed.


### DX8 ancillary helper selects depth/stencil, with a success-without-write edge

The same [activation audit](evidence/audits/dx8-mode-activation-history.json) now retains helper `600043e0..60004521` (321 code bytes) and separately decodes its ten-entry jump table `60004524..6000454c` as data. Both code and table match140/150. SDK constants identify the previously opaque output as a depth/stencil format.

Its four stack arguments are adapter index, adapter format, render-target format and output pointer. It chooses a six-candidate list from the current DWORD at `6001eed0`; this is distinct storage from the incoming colour-depth pointer handled by the preceding helpers.

|Selector value |Candidate order, first to last |
|---|---|
|16 |D16(80), D32(71), D24S8(75), D24X8(77), D24X4S4(79), D15S1(73) |
|32 |D32(71), D24S8(75), D24X8(77), D24X4S4(79), D16(80), D15S1(73) |
|Anything else |Returns1 without a local write to the output pointer |

Each candidate must return zero from CheckDeviceFormat at `6000447c` (usage2, resource type1), then zero from CheckDepthStencilMatch at `60004495`. The pinned interface header establishes vtable slots28h/30h. The first candidate passing both checks is written to the output at `600044c1`; exhaustion writes0 and returns0. Actual device support is untested.

Selected D32/D24S8/D24X8/D24X4S4 writes selector32; D16 writes16. D15S1 writes16 and sets DWORD `6002022c` to1. This helper does not clear that flag on its other paths. Do not infer that it always describes the current selected format without checking initialization and later writes.

The unsupported-selector branch at `6000444c` reaches the success return `600044dc` without performing the search or writing the output. That is an instruction-level edge, not evidence that normal initialization reaches it. A C reconstruction must preserve or explicitly resolve the caller precondition rather than replace this with an invented failure/default.

**Resolved:** selected candidate order, API gate order, output writes and selector/flag effects. **Remaining:** the selector and flag's full initialization/mutation history, output contents on success-without-write, complete device/error lifecycle and rendered behaviour. This narrows the earlier ancillary-helper unknown; it does not establish runtime safety or introduce another140→150 change.

## Historical DX6 depth keys and sorting change at140

The [131/140 admission audit](evidence/audits/dx6-mode-admission-history.json), reproduced with `python3 analysis/scripts/audit_dx6_mode_admission_history.py`, pins `drivers/dx6/dx6.dll` SHA-256`81cc2b24972d37efca68ad277b714f5053672994df1ed266c529e1e24cd3420f` and140 `drivers/dx6/dx6a.dll` SHA-256`d32ee0f11361977ecaa01402b33a0a1ea4f4732b118355a5b98696768f8d25cb`. It retains both complete initializers and callbacks and the140 insertion body. These are historical provider changes, not newly identified EXE instructions.

|Selected policy |131 |140 |
|---|---|---|
|Initializer at60001c50 |Clears1,200 bytes through the published pointer; seeds640×480×16 and sets count2 |Clears4,000 bytes at6003f028, resets count0, omits fixed seed |
|Ordinary equal-width/height callback route |Stored depth greater than incoming, unsigned, rejects; otherwise overwrites that row |Builds a40-byte temporary record and calls6000e500 |
|Record key/order |Ordinary scan matches width/height; new unmatched records use encountered empty slots |Unsigned lexicographic width,height,stored-depth key; binary search and ordered insertion |
|Equal key |Depth selection can replace existing dimensions' row |Equal triple overwrites; different depth is a separate key |
|Classifier3 |Stores normalized depth15 after ordinary depth comparison |Normalizes to15 before insertion compares the complete key |

Under the ordinary131 branch, an existing800×600×32 row rejects a later800×600×16 input at60001d51; the reverse arrival order overwrites16 with32. In140, assuming both candidates pass classification/filtering, retain stored depths16 and32 after normalization and capacity is available,16 and32 are distinct keys and sort in that order. This is a static derivation from the captured comparisons, not a new instruction probe or observed device catalogue. The special640×480 route in131 separately tests its seeded slot and incoming depth16; the ordinary example must not be generalized to that branch.

Both callbacks retain minimum width640 and height480 gates and a classifier-result rejection. Neither locally requires every input depth to equal16. The claim therefore has a specific mechanism: lower-depth alternatives need no longer be lost solely because a higher-depth record shares their dimensions.131 already seeds a16-bit mode, so these findings do not establish that16-bit operation was previously absent.

The140 insertion helper's new-key limit is100. The131 scan's101 guard and1,200-byte clearing request are different facts, not a proved allocation bound or safe visible row count. Reuse the [later count/public-base analysis](#dx6-public-mode-count-gains-its-leading-slot-in150) and [consumer limits](#dx6-extra-count-slot-reaches-inclusive-scans-but-can-fail-admission) rather than equating insertion count with displayed modes. Ambient DF, malformed records, arithmetic/division failures, callback ordering and complete storage lifetimes remain separate contracts.

**MP140-038 advances vendor-only→partial:** the named historical pair proves sorted depth-aware insertion and seed-policy changes consistent with retaining16-bit alternatives. Actual enumeration, menu order, successful16-bit activation, provider/device acceptance and rendered output remain unverified. No DLL/API/target code executes and executable/database bytes remain unchanged.

## Early120 DX6 mode policies and the640 by480 caveat

The expanded [DX6 admission audit](evidence/audits/dx6-mode-admission-history.json) hash-pins120 `drivers/dx6/dx6.dll` and proves it **byte-identical to the131 driver** already captured above. Therefore those complete initializer/callback captures directly establish120 policy without assuming correspondence from reused addresses. The audit also captures its complete classifier600028e0..60002993. No unpatched NFS4 DX6 driver is available in the inspected reference/110 archives, so presence in120 is not proof of introduction there.

|Release claim |Local120 evidence |Qualification |
|---|---|---|
|MP120-017:100 resolutions |Seed count2; new-row guard compares with101; scan skips reserved index0 and starts at the640×480 seed |For ordinary fresh synchronous filling, indices1..100 permit100 nonreserved records; count can be101. Allocation/consumer safety and visible counts are separate |
|MP120-018:hide height below480 |Unsigned height comparison at60001d02 rejects below480 before record writes; width below640 is also rejected |Actual display offers and visible menu, all other providers and prepatch boundary unverified |
|MP120-019:always640×480×16 |Initializer seeds depth16 with record+10h=0; callback later prefers16 once the slot is occupied |The first accepted input can overwrite the unoccupied seed with another depth; universal16-bit forcing is not established |

The last distinction is a concrete conditional counterexample to **local callback** universality. A valid640×480 input with depth32 and RGB masks00ff0000/0000ff00/000000ff returns classifier6. At60001d26, seed flag+10h==0 branches directly to record writing, before the later `ECX==16` preference test. The depth remains32 because only classifier3 triggers conversion to15. With no later16-bit callback or other overwrite, this route leaves the selected record at32. These are instruction-derived conditions, not a new instruction probe, observed enumeration or proof of actual32-bit game/movie activation.

If a later accepted16-bit input arrives, the occupied-slot path admits it and can replace that32-bit row. Once occupied, non16 incoming depth takes the skip path. Enumeration order and the presence of a16-bit candidate therefore matter. Seed metadata alone must not be rewritten as a guaranteed post-enumeration depth, and the release-note rationale about intro-movie failure is not independently tested here.

**MP120-017/018 advance vendor-only→partial** for the bounded capacity arithmetic and height gate present120. **MP120-019 advances vendor-only→partial with a caveat:** the16-bit seed/preference is verified, but the absolute wording exceeds the local mechanism. Missing prepatch comparison, later state changes, provider ordering, mode-menu/activation and movie behavior remain open. Existing DLL/EXE bytes and Ghidra state are unchanged; no target or API executes.

### The original budget bypass is already present in 1.0.0

The recovered 1.0.0 EXE matches 1.1.0 across the complete 226-byte
enumerator at `004bed90..004bee72` (exclusive end). The shared span
SHA-256 is
`84a8ea1447b72f9083948d93858788cbc0a1bd79128b8f7771dff7980eed7f47`.
Extract `nfs3.exe` from the
[pinned 1.0.0 archive](original-modern-dll-candidates.md#recovered-100-package-separates-code-changes-from-renames)
and compare PE RVA `bed90` for `e2h` bytes.

Consequently the first retained Modern release already skips the
original size/budget block and applies the same wider aspect interval
and signed depth-at-least-16 predicate as 1.1.0. This dates the
mechanisms for MP100-001 and MP100-003 to the named release. Driver
enumeration, other eligibility checks and successful use of large
resolutions remain separate.

The 1.0.0 and 1.1.0 EXEs also match byte for byte across the complete
collector (`00448210`, 169 bytes), reset/enumeration initializer
(`004482c0`, 40 bytes), menu descriptor (`005566b8`, 20 bytes),
dynamic-label route (`004d17b0`, 26 bytes), and record-label accessor
(`00448400`, 35 bytes). This extends the matched producer-to-menu
chain for MP100-009 to 1.0.0. The ordinary zero-based collector allows
51 records in both builds, versus 20 in the supplied original. The
release note's wording of 50 and the actual number displayed at
runtime remain distinct from that local limit.
