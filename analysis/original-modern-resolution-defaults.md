# Original versus Modern: requested resolution defaults

## Evidence and scope

Static comparison using the supplied original/backup and official Modern v1.6.1 fingerprints in the [baseline](original-modern-differences.md). The [display-mode manifest](evidence/audits/original-modern-display-modes.json) retains the original/Modern default initializer `00472d10`, original menu selector `004483a0`, Modern selector `00448394`, and Modern desktop-metrics helper. Reproduce with `python3 analysis/scripts/audit_display_mode_difference.py`. No game/API/probe execution or executable/database mutation.

This follows the requested-mode producer missing from the [mode-selection report](original-modern-mode-selection.md). It is a bounded default-initialization path, not proof that it runs on every first launch or ignores every saved configuration.

## Original default path

Original `00472d10..00472f18` initializes multiple settings from local tables and a calculated tier. Near its end, renderer mask `[007a3a58] & 6` selects **320** or **640** in EAX (`00472eaa..00472ec8`). It calls `004bee80`, then selector `004483a0` at `00472ed2`.

Original `004483a0` takes an identifier in EAX, initializes/enumerates the list through `004482c0`, then scans the collected menu records at `00661220` with stride 0x114, and stores the matching row index at `006fbc14` and that row's DWORD `+4` at `006fbc18`. If no matching ID is found, it selects row zero. This differs from Modern's packed width/height request and nearest-area search; the same global addresses must not be assigned unchanged field semantics across versions.

The complete original tier computation and `004bee80` contract remain outside this chapter. The shown path establishes literal 320/640 selection, not an original desktop-resolution query.

## Modern default path

Modern `00472d10..00472e1c` loads `[005652a4]` into ECX, caps it to unsigned 5, and halves it when `[007a3a58] & 6` is nonzero. This ECX value indexes byte tables for several graphics settings. The [CPU tier comparison](original-modern-cpu-tier.md) now traces its feature/family score producer, distinct from original’s million-scaled estimate. Vendor/legacy branches and runtime interpretation remain bounded.

The requested size is then chosen as follows (`00472dbb..00472dce`):

| Condition | Stored DWORD at `006fbc18` | Width/height WORDs |
|---|---|---|
| Renderer mask has bit 1 or 2 set | `01e00280` | 640 × 480 |
| Neither bit set, adjusted tier < 4 | `01e00280` | 640 × 480 |
| Neither bit set, adjusted tier ≥ 4 | `7fff7fff` | 32767 × 32767 |

It stores `006fbc14=1` and calls `00448394` (`00472dde`). The default initializer itself contains no desktop API read.

The large request must not be described unconditionally as “highest resolution.” It feeds the same machine-width nearest-area calculation documented in the mode-selection chapter, with approximate eligibility and depth handling. For ordinary fitting candidate areas below the requested area it favours larger area; arbitrary driver dimensions or arithmetic wrap need not follow that intuitive model.

## Modern request-to-menu linkage

`00448394` first initializes/enumerates the menu list through `00448320`. It chooses requested depth **32** by default. If `Hide16bitModes` is zero and bit 0 of `006fbc14` is clear, it instead requests **16**. Thus the default initializer's explicit bit value requests 32 on this path.

It zero-extends height WORD `006fbc1a` and width WORD `006fbc18`, pushes depth/height/width, then invokes `004bedcc` at `004483c4`. It searches the menu list for the returned driver index; if absent, it uses row zero. It stores the menu-row index at `00a1825c` and invokes `00448400` on that row. The latter copies dimensions/depth into `006fd1e4..006fd1ec` and reacts to changed dimensions.

This connects default requests to actual selection code. It does not prove a nonempty list, a valid row-zero fallback, driver availability or rendered output. The sorted menu's deduplication and `Hide16bitModes` rules are documented in the [admission/menu report](original-modern-display-modes.md).

## Desktop helper and release-note claim

Modern also contains helper `004f9140..004f915d`: EAX points to two output DWORDs, populated by imported GetSystemMetrics with arguments 0 and 1. That is a concrete metric-read mechanism, not proof of its use by default initialization. The inspected `00472d10 -> 00448394 -> 004bedcc` route does not call it. A bounded search of the retained linear Modern disassembly found no direct `CALL 004f9140`; indirect calls and data-held function pointers are not excluded.

**MP100-011** says the first run tries a gameplay resolution nearest the Windows default. The retained releases establish a conditional desktop-based default in 1.0.0 through 1.3.0 and a different policy starting in 1.3.1. First-run reachability remains unverified.

### Packaged 1.0.0–1.3.0 defaults use desktop pixel area

In the retained 1.1.0 executable (SHA-256
`59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72`),
`004a6e3b` passes `007a3a2c` to `004f9140`. The latter calls
GetSystemMetrics with arguments 0 and 1 and stores the results in two
adjacent DWORDs. The default branch at `00472e36..00472e67` uses those
values only when renderer mask `007a3a58 & 6` is clear and the adjusted
tier in ECX is at least 4. At `00472e54` it computes the low 32 bits of
desktop width × height + 32 and passes that score in EAX to `004bee80`.
The returned driver index goes to `004483a0`. The
[historical score selector](original-modern-mode-selection.md#historical131-uses-a-different-scalar-sentinel)
compares scalar scores, so this is a desktop-area target with a depth
term. Aspect-ratio or per-dimension proximity is not established.

Both bypasses in 1.1.0–1.3.0 preserve EAX=`0004b010h`, loaded at
`00472e31`. That score is 640 × 480 + 16. A set renderer mask
branches around the desktop calculation, as does a signed tier
below 4. The selector receives a scalar target, so the literal
does not guarantee that the driver supplies or selects a
640 × 480 × 16 mode. Version 1.3.1 retains the same fallback and
uses the large sentinel on the qualifying path. Version 1.4.0
retains both literals, now at `00472e2c` and `00472e4f`. Compare
these with final's packed 640 × 480 request and separately chosen
32-bit requested depth above.

The same producer and consumer use `007a2760/007a2764` in 1.2.0 and 1.3.0.
The packaged 1.3.1 binary still calls the producer at `004a6e40`, but the
same qualifying defaults branch instead loads `7fffffffh` at
`00472e54`. This dates the removal of desktop dimensions from this
defaults branch independently of whether the metric helper still runs.
To reproduce, extract the retained archives with `7z x -so` and
disassemble `004a6e3b..004a6e45`, `004f9140..004f915e` and
`00472e36..00472e6e` using `objdump -d -Mintel`. Actual mode lists,
first-run admission and rendered output remain untested.

The [config-load comparison](original-modern-config-loading.md) now traces exact size/version-byte decisions at `00472aac..00472aea` before default setup (`00472ad7 -> 00472d10`). It remains a reset/default path rather than an unconditional first-run route; complete serialization and saved-setting validity remain unresolved.

## Menu startup depth: fixed original request versus optional Modern 32-bit

The expanded [renderer-selection manifest](evidence/audits/original-modern-renderer-selection.json), reproduced by `python3 analysis/scripts/audit_renderer_selection_difference.py`, retains complete original subsystem setup **`004b6020..004b6246`** and Modern **`004b5c00..004b5d83`**. The original setup’s connection through wrapper `004a3390` is independently documented in the [registry/selector call chain](original-modern-registry.md#original-selector-precedence-and-call-chain). These routines have corresponding subsystem roles; they are not paired by address.

Original **`004b6027..004b6052`** stores width640 at `00564384`, height480 at `00564388`, depth16 at `0056438c`, and state1 at `00564390`, without a conditional depth choice in that initialization block. Modern **`004b5c27..004b5c50`** stores the same width/height, then chooses the depth:

| `007a2794` setting value | Modern stored request depth |
|---|---:|
| Zero | 16 |
| Any nonzero 32-bit value | 32 |

The [settings-loader analysis](original-modern-startup-policy.md#3-current-settings-exact-defaults-and-immediate-effects) verifies key **`Use32bitModeInMenu`**, fallback0, and its write to `007a2794`. The test is nonzero, not equality with1. Modern’s state write at `00564390` separately derives zero/nonzero from `0067900c`; do not fold that unrelated flag into the depth choice.

The [renderer lifecycle comparison](original-modern-renderer-lifecycle.md#parameters-and-mode-selection-change) verifies the later mode path at `00517620`: call driver initialization, refresh its descriptor, push depth/height/width from these three globals and call `004bedcc` at `00517682`, then request the selected mode through `_THRASH_setvideomode@12`. The [selection report](original-modern-mode-selection.md#modern-descriptor-lookup) establishes fallback and depth-mismatch behavior, so this is a **requested depth**, not a guarantee of an accepted 32-bit mode or successful rendering. Full initialization ordering, driver failures and actual movie rendering in that mode remain separate evidence.

This gives **MP150-043** partial static support: Modern introduces the configuration-controlled16/32-bit menu request where the reviewed original setup requests16. It does not establish **MP120-019**’s stronger statement that640×480 is always reported as16-bit. A requested mode, a driver’s advertised record depth and a movie’s supported pixel formats are three distinct contracts. The [DX7 admission follow-up](original-modern-dx7-mode-admission.md) retains both16/32-bit candidate admission and the remaining exact-size reporting unknown. No additional driver, UI, movie or instruction execution was used.

## Frontend transitions stop forcing a temporary 16-bit depth

The complete same-address transition functions `00473020..0047307e` (94 bytes) and `00473080..004730c6` (70 bytes), exclusive ends, have a paired removal. [The frontend-depth audit](scripts/audit_frontend_depth_override.py) verifies both executable hashes, complete envelopes and exact removed instructions; [its manifest](evidence/audits/frontend-depth-override.json) records full hashes and disassembly locations.

Original entry at `00473041..00473056` reads current depth DWORD `0056438c`, stores it in shadow `00679008`, then writes 16 to `0056438c`. Original restore at `0047309b..004730a5` copies that shadow back to the depth field. Modern replaces those regions with jumps over 19 and eight NOPs, respectively. No other bytes differ in either complete envelope.

The complete changed spans retain their original bytes in the archived 1.1.0–1.4.0 executables. Both switch to the final jump-and-padding sequences in **1.5.0**, the first retained release where the entry and exit both leave the depth field alone. Compare `00473041..00473056` and `0047309b..004730a5` after extracting the executable from each archive. The same [transition archive and executable hashes](original-modern-state14.md#scene-paths-skip-original-placeholder-calls) apply.

This extends the startup-depth evidence above: the change is not only a different initial depth choice. Modern removes these local menu-transition save/force/restore operations, allowing the field's surrounding state to persist across this pair unless changed elsewhere. It does not prove that every menu uses an identical physical display mode or that no other depth write exists.

The separate state DWORD `00564390` still has its original transition protocol: entry saves it to `00679004` and ORs byte bit 2, while exit restores it. All other calls and their order in these functions remain byte-identical, including renderer/menu setup and teardown calls. Those calls can have their own version differences; equal caller bytes are not full transition equivalence.

Saved Modern body unions exclude the NOP gaps and list only 75/62 bytes, so their small in-body changed counts do not cover the removed stores. The audit includes the complete original operations. The old depth shadow is no longer read/written by this pair; global deadness or removal of the storage is not established.

**Bounded work status: done; confidence: verified static state writes, with depth meaning grounded in the existing startup/mode research.** Reconstruction must preserve the chosen version's depth lifetime and separate flag shadow. Removing these instructions also changes incidental EAX/EDX values at the next call boundary, so full register-contract equivalence is not assumed. Pending runtime scope includes selected-mode/reset propagation, actual frontend display depth and supported renderer transitions. Executables, Ghidra state and maintained C are unchanged.

## Tier tables occupy former original code; final load/store mismatch

The [table audit](scripts/audit_graphics_default_tables.py) and [manifest](evidence/audits/graphics-default-tables.json) retain both complete default-initializer body hashes and the exact file-backed arrays. The outside-function interval `00472e1d..00472f20` is not wholly NOP filling: Modern has three NOPs, **54 table bytes** at `00472e20..00472e56`, then 202 NOPs. Those table bytes replace part of the original initializer's instruction stream. They must be reconstructed as data rather than decompiled as arithmetic instructions.

The original tables contain five signed WORDs each; Modern uses six unsigned bytes per table. Entries below are ordered by each version's effective tier. Original and Modern tier producers differ, so equal ordinal is not an equal-CPU comparison.

| Destination DWORD | Original table / values for indices 0..4 | Modern table / values for indices 0..5 |
|---|---|---|
| `006fbc28` | `00472168`: 3,3,2,1,1 | `00472e20`: 3,2,1,1,0,0 |
| `006fbc2c` | `00472172`: 2,1,1,0,0 | `00472e26`: 2,1,1,0,0,0 |
| `006fbc1c` | `00472186`: 2,2,1,0,0 | `00472e2c`: 2,2,1,1,0,0 |
| `006fbc30` | `00472190`: 2,1,1,0,0 | `00472e32`: 2,1,1,0,0,0 |
| `006fbc20` | `0047219a`: 0,1,1,1,1 | `00472e38`: 0,1,1,1,1,1 |
| `006fbc24` | `004721a4`: 0,0,1,1,1 | `00472e3e`: 0,0,1,1,1,1 |
| `006fbc3c` | `004721ae`: 0,0,0,1,1 | `00472e44`: 0,0,0,1,1,1 |
| `00791b28` | `0047217c`: 0,0,1,1,1 | No write to this destination in the compared Modern initializer |
| `006fd1d8` | No write in this original initializer | `00472e4a`: 2,2,2,2,1,0 |

These are local table-derived writes, not unconditional final configuration values. Later branches in these bodies can override `006fbc3c`, and other initialization/configuration paths may write the same destinations. The [vehicle-dispatch comparison](original-modern-vehicle-dispatch.md) already maps consumers of `006fbc1c` and `006fd1d8`; the named-option follow-up below now binds the remaining table destinations through their actual descriptors and English label lists.

The ninth Modern table, `00472e50`, contains **0,0,0,1,1,1**, but the final sequence is:

```asm
00472e0f  MOVZX EDX,BYTE PTR [ECX+00472e50]
00472e16  MOV   DWORD PTR [006fd1d4],EAX
00472e1b  POPAD
00472e1c  RET
```

The store does **not** use the loaded EDX. In the local control flow EAX comes from the preceding call `00448368` at `00472de3`; TEST, conditional branches, immediate stores and MOVZX do not replace it. The [display-mode report](original-modern-display-modes.md) identifies `00448368` as returning the selected record's DWORD `+0x10`. The final write stores that raw EAX value, not a Boolean conversion and not a tier-table byte. POPAD then restores incoming general registers, discarding the new EDX value. Effective ECX indexing across the calls still depends on their register contracts.

**Status: done for static table/layout and load/store verification; confidence: verified.** Intent is unresolved: this could be a stale load, an incorrect destination register or a deliberate retained sequence. No bug fix is applied or claimed. The consumer follow-up below maps the immediate fog-selector consequence. Complete writer/caller ordering, actual startup values and visuals remain untested. Preserve the observed chosen-version behavior in reconstruction until an explicit policy decides otherwise.

### Consumer follow-up: the stored value feeds fog selection

The expanded table audit verifies the immediate producer-to-consumer chain, rather than treating `006fd1d4` as an unknown setting:

1. Menu-record writer `004482e8..004482f5` zeroes EAX, compares driver-record DWORD `+0x18` **signed** against 2, sets AL=1 when at least 2, and stores EAX into menu-record `+0x10`. Thus records populated by this path contain exactly 0 or 1 in that field. This menu offset must not be conflated with driver-record `+0x10`, which is a different flags field.
2. Getter `00448368` returns the selected menu record's `+0x10`, and the default initializer stores this EAX into `006fd1d4`. For a valid populated record, it therefore chooses the normalized result of **driver-record `+0x18 >= 2`**, rather than the unused tier-table byte. No additional normalization occurs at the final store.
3. File-backed descriptor `00556924` binds token `fog` to selector `006fd1d4`. The [state14 report](original-modern-state14.md#modern-scene-entry-recomputes-fog-admission) verifies helper `00431c1c`, which computes `007a3a54 & 006fd1d4 & 00559234` into admission DWORD `007a3a64`. The [graphics-menu transition report](original-modern-graphics-menu-transition.md) separately maps save/clear/restore writes to the selector.

This establishes a concrete consequence of the load/store sequence: **the default fog selector follows the selected mode's normalized driver-field threshold, with no direct tier-table choice at that store**. It does not establish the driver's semantic name for `+0x18` or prove a visible fog error. The effective tier can still influence mode selection, and later menu/configuration writes can replace this value. Empty-list fallback returns a record address without proving it was populated, so the 0/1 guarantee is conditional on successful record creation/selection. The unused table and chosen register remain an intent question; observed behavior is now mapped through its actual setting and admission consumer.

### DX5 producer qualifies the selected-mode fog default

The expanded [table audit](scripts/audit_graphics_default_tables.py) now pins
the official archive and DX5 member, captures producer `60001837..60001871`,
and retains instruction-derived boundary examples in
[its manifest](evidence/audits/graphics-default-tables.json). This connects the
EXE's field threshold to the independently compared
[DX5 mode callback](original-modern-dx5-reference-pair.md#mode-callback-and-selected-initialization-paths).
It does not assign that backend-specific producer to every driver.

For a candidate created by the captured final DX5 callback, let Q be the
unsigned quotient `[60010eb4] / wrap32(width*height*bytes_per_pixel)`, with
nonzero denominator. The callback writes record+18h as3 when Q>3; otherwise
it writes `wrap32(Q-1)`. Combining that with the EXE's **signed** field>=2 test:

| Q | Stored field+18h | EXE fog selector from that field |
|---:|---|---:|
|0 | `ffffffffh` (signed−1) |0 |
|1 |0 |0 |
|2 |1 |0 |
|3 |2 |1 |
| Greater than3 |3 |1 |

Thus the inspected callback-produced record satisfies **selector1 iff unsigned
Q>=3**. Q0's subtraction wraps to an unsigned all-ones bit pattern. Keep the quotient
unsigned and the later signed field interpretation explicit in C. The quotient
represents this producer's buffer-size arithmetic, not independently measured
available VRAM or proof of successful surface allocation. The [selected direct budget producer](original-modern-dx5-reference-pair.md#mode-budget-producer-retained-query-and-2-mib-fallback) is now identified as a query-derived sum or2 MiB fallback; all writers and lifetime paths remain unresolved.

This conclusion requires a valid selected record populated by that callback.
Fixed seed records, overwritten/aliased records, other driver implementations
and failed enumeration remain separate. Most importantly, the
[DX5 support trial](original-modern-dx5-reference-pair.md#exe-fog-trial-connects-to-the-rejected-dx5-selector)
rejects state21 and can clear the separate support flag. A default selector1
therefore does not establish enabled or rendered fog.

The same table audit also classifies outside-body interval
`00472155..004721f0`: only `00472155..004721b8` changes. Original has19 zero
bytes followed by80 bytes of eight signed-WORD default arrays; Modern replaces
those99 bytes with NOPs. The following56 bytes are unchanged. This is removed
embedded table storage, not an unrecognized99-byte original function. The
replacement byte arrays and changed initializer are documented above.

**Status:** done, verified static for the DX5-producer/EXE-threshold link and
old-table extent. The examples are arithmetic derivations, not target probes.
Full source lifetime, mode/record selection, other drivers and visible fog
remain unverified. No DLL, EXE, graphics API or instruction probe was executed;
executable and database bytes were preserved.

## Named graphics defaults and the limits of automatic High settings

**Confidence: verified static descriptor/label bindings and local default policy. Work status: done for this mapping, partial for MP100-010’s broad claim.** The expanded [table audit](scripts/audit_graphics_default_tables.py) pins the official package’s English resource, reads nine20-byte descriptors and their terminated WORD label lists, and connects the eight used byte tables to those options. The [manifest](evidence/audits/graphics-default-tables.json) retains addresses, raw descriptor DWORDs, label IDs, per-tier labels and two conditional examples. These are derived defaults, not observed settings on this machine.

The [CPU-tier investigation](original-modern-cpu-tier.md) establishes the ordinary standard-leaf feature/family score with maximum5. The default initializer interprets it as unsigned, caps it at5, then shifts right by1 when renderer mask`007a3a58 &6` is nonzero. It does not measure actual rendering speed. For incoming score5, the table writes are:

| Named option key | Selector DWORD | Mask6 clear: effective tier5 | Mask6 nonzero: effective tier2 |
|---|---|---|---|
|`viewlevel` |`006fbc28` |Full |Far |
|`hrzlevel` |`006fbc2c` |High |Low |
|`cardetail` |`006fbc1c` |High |Medium |
|`sfxlevel` |`006fbc30` |High |Low |
|`carlight` |`006fbc20` |On |On |
|`carchrome` |`006fbc24` |On |On |
|`projtex` |`006fbc3c` |Projected |Vertex |
|`mirrorlevel` |`006fd1d8` |High |Low |

These labels come from the descriptor-linked official English entries, not assumptions that larger numeric values mean better quality. In particular High/Full are ordinal0 for the corresponding lists; carlight/carchrome On and projtex Projected are ordinal1. The actual rendering meaning and effectiveness of each setting remain its consumer’s separate contract.

### ECX tier survives the two intervening mode calls

The later mirror byte read at`00472e02` occurs after calls to mode selector`00448394` and field10 accessor`00448368`. The expanded audit retains their exact bytes: the selector uses balanced PUSHAD/POPAD on its normal return; the accessor and its leaf`00448348` write EAX and the selected-index global, but not ECX. Thus the original effective tier survives these two calls under ordinary valid-stack/no-alias-mutation conditions. This closes the earlier specific callee-register question for the later table lookup, without certifying every mode helper or failure path.

### Mode-dependent overrides prevent an unconditional best-settings claim

The table is not the final authority for every destination. After selection, field10 of the selected menu record is read into EAX:

- Zero replaces`projtex` with0 (Vertex) and Z-buffer selector`006fbc34` with0.
- Nonzero sets the Z-buffer selector to1 while retaining the tier’s projtex choice.
- Fog selector`006fd1d4` receives that raw EAX value, despite the separate load of the ninth table into EDX. The previously documented load/store mismatch is preserved; do not describe fog as a ninth CPU-table-selected default.

For ordinary records from the audited collector, field10 is normalized0/1 from the provider-record threshold. Empty or invalid records, source lifetime and other writers retain the preceding caveats. Selector1 also does not prove actual fog support; the independent support trial still applies.

The initializer also requests either640×480 or the packed large-area sentinel according to tier/renderer conditions already documented above. That request is filtered through the actual mode list; it is not a promise that a desktop-sized or highest-quality display mode exists or succeeds.

**MP100-010 conclusion:** Modern changes CPU rating and its table consumers so a maximum ordinary feature score on the non-reduced renderer path requests the table’s High/Full choices. The renderer-reduced path and selected-mode overrides can choose lower labels. Persisted settings/default-reset admission are separate from this routine: the [configuration investigation](original-modern-config-loading.md) traces grouped defaults after a rejected version header, but this finding does not establish that every startup overwrites saved user choices. Exact1.0.0 introduction, every legacy CPU branch, active settings on particular PCs/VMs and visual quality remain unverified. No CPU detection, display API, instruction probe or game was run.

### 1.1.0 startup and missing-config entry paths

In the same pinned 1.1.0 executable, startup calls `004a6e10` at
`004a3a55`, which reaches the desktop metrics call at `004a6e40`.
The inspected startup sequence later calls graphics defaults at
`004a3dda` and then calls `004730d0` at `004a3e65`. The desktop
query is therefore part of startup before the inspected defaults
call. It is not gated locally on the existence of a config file.

There is also a missing-config route through `00472980`. It
initializes the local handle at `0047299d` and skips opening the
file when the path check at `004729d9` returns zero. If the handle
is still zero at `004729fd`, it sets `0067900c=1` and calls
`004723f0`. A later entry into `004730d0` can consume that marker
at `00473186` and call graphics defaults at `00473195`. This
requires `0055b03c != 0`, `0055e88c == 0`, and the marker to
survive to the test after `00472fc0`. The zero-handle branch can
also be reached without a missing file, such as when the earlier
flag test bypasses the open path.

Together these paths establish that 1.1.0 samples desktop dimensions
before a startup default-mode selection, and that missing settings
can request a later graphics reset. Actual first-run gate values,
subsequent overwrites, and the mode that ultimately renders remain
unverified. This evidence applies to 1.1.0. The 1.0.0 binary behavior
is still open.

### 1.5.0 requests 32-bit colour on the fallback branch

The [pinned 1.5.0 executable](original-modern-mode-selection.md#150-changes-the-stored-request-format-and-sentinel-trigger)
already writes the packed fallback `01e00280h` (640 × 480) and sets
`006fbc14=1` at `00472dd4`. Its call at `00472dde` reaches
`0044838e`. That helper starts with depth 32 at `00448396` and
allows depth 16 only if `007a2798` is zero and bit 0 of `006fbc14`
is clear. The default's bit is set, so the depth pushed at
`004483ad` is 32 on both the fallback and large-request branches.

The retained 1.5.1 through 1.6.0 executables keep those default writes.
Their call at `00472dde` instead reaches `00448398`, with the
equivalent depth-bit test at `004483ab` and selector call at
`004483c8`. The final build's corresponding path is documented above.
Reproduce by disassembling `00472dbb..00472de3` and
`0044838e..004483cd` in the retained builds.

This distinguishes the earlier scalar fallback `640 × 480 + 16`
from a packed 640 × 480 request with a separate depth of 32. In
1.5.0, the selector at `004bedcc` accepts an eligible exact size and
depth immediately. An eligible exact-size mode with mismatched depth
can still enter the ranking with zero area error. The selected mode
depends on the renderer's eligible records. No rendering was tested.

### Frontend restores the stored request through the same selector

At `00473279`, the original and retained 1.1.0–1.4.0 load the scalar score from `006fbc18`, call `004bee80`, and pass its result to `004483a0`. From 1.5.0 the frontend instead calls the dimension-based selector directly. Its target is `0044838e` in 1.5.0, `00448398` in retained 1.5.1–1.6.0, and `00448394` in final 1.6.1.

At each of those entry points the helper initializes the requested depth to 32, allowing depth 16 only when `007a2798` is zero and bit 0 of `006fbc14` is clear. It reads width and height as unsigned WORDs at `006fbc18` and `006fbc1a`. The historical address changes preserve that local policy. The frontend caller uses the current settings, so the default initializer's separate write of `006fbc14=1` does not establish a 32-bit request for every frontend entry. Requested depth and the chosen display mode remain distinct because the selector can consider eligible mismatched modes.

### Desktop-area defaults are already present in 1.0.0

The [recovered 1.0.0 EXE](original-modern-dll-candidates.md#recovered-100-package-separates-code-changes-from-renames)
matches 1.1.0 at the ten-byte startup call sequence at `004a6e3b`,
the metrics helper at `004f9140..004f915b`, and the default-score
branch at `00472e31..00472e67` (exclusive ends). Both PE import
tables resolve slot `00534750` to `USER32.GetSystemMetrics`.
Thus the qualifying branch already uses desktop width × height + 32
in 1.0.0. The alternate branches retain the 640×480×16 score.

This dates the target-score calculation in MP100-011. It does not
establish first-run reachability in every configuration, exact
dimension matching, or successful selection on a running machine.

The 1.0.0 branch calls the score selector at `00472e62` and passes
its result directly to the driver-index mapper at `00472e67`.
The complete selector (`004bee80..004bef4b`) and mapper
(`004483a0..004483dc`) match their 1.1.0 counterparts byte for byte.
The selector keeps the first eligible candidate on a score tie and
returns driver index 1 if it finds none. The mapper rebuilds the mode
list through `004482c0`, searches its stored driver indices, and
writes the corresponding menu index to `006fbc14`. A miss selects
menu index 0. These are separate fallbacks. They explain why a
desktop-derived score can still yield the first menu slot even when
the desktop dimensions are available to the game.

### The packed default request begins in 1.5.0

Version 1.4.0 still places the scalar fallback `0004b010h` and
qualifying sentinel `7fffffffh` at `00472e2c` and `00472e4f`.
In 1.5.0, the default producer instead selects packed `01e00280h`
(640×480) or `7fff7fffh` and stores it at `006fbc18` via
`00472dce`. The latter selection requires renderer mask bits 1 and 2
clear and an adjusted tier of at least 4.

The complete 25-byte choice and store at `00472dbb..00472dd4` match
byte for byte in all six retained releases from 1.5.0 through 1.6.1.
To reproduce, extract the root `nfs3.exe` from each archive and
compare PE RVA `72dbb` for `19h` bytes. This dates the default writer
independently of the menu's sentinel trigger and the reader's ranking
rules, which are traced in the [mode-selection comparison](original-modern-mode-selection.md#150-changes-the-stored-request-format-and-sentinel-trigger).

Across those six releases, the complete 268-byte defaults initializer
at `00472d10..00472e1c` differs at just two byte positions, both
inside relative-call operands. The adjacent 58-byte span at
`00472e1c..00472e56` also matches across all six.

| Release | Call at `00472dde` | Call at `00472de3` |
|---|---|---|
| 1.5.0 | `0044838e` | `00448367` |
| 1.5.1–1.6.0 | `00448398` | `0044836c` |
| 1.6.1 | `00448394` | `00448368` |

The local tier computation, table bytes and stores therefore stay
stable in the inspected span. Matching local bytes leaves changes in
the tier producer, the called routines and live user settings in scope
for the resulting graphics configuration.

### The area-plus-depth selector is present in Modern 1.0.0

The hosted original ranks eligible modes by distance from a
target **width**. Modern 1.0.0 already ranks them by distance
from a target **width × height + depth** score and applies
the broader aspect and depth checks described in the
[viewport history](original-modern-viewport-geometry.md#historical-mode-dimension-input).
This dates the selector rewrite independently of the two
callers that supply startup and frontend defaults.

Read 203 bytes at PE RVA `bee80h` from each retained
`nfs3.exe`. The complete selector window has SHA-256
`c7031dcbd776a438336e639cb722dafa48c4d53da1128a4539f0aa0630f67ec3`
in the hosted original and
`aaf49436bdda52b5d9c3bc4674baa6043490ae689e51a1aa581da53548fee1e9`
in each of the six retained Modern releases from 1.0.0
through 1.4.0. Starting in 1.5.0, the same address window
has different code. The packed-request path above documents
the later selection mechanism. The comparison establishes
the first observed release and the local algorithm, while
selected resolutions depend on the available mode rows.
