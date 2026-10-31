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

**MP100-011** says the first run tries a gameplay resolution nearest the Windows default. The final binary contains a nearest-area helper, but the directly traced default path supplies fixed/large sentinel requests instead of values from the metric helper. The historical claim therefore remains **unresolved/partial**, not confirmed and not universally disproven. Establishing the precise first-run path requires tracing the caller's saved-setting validity branch and all relevant indirect/configuration producers; dating behavior additionally needs the earlier release binary.

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

These are local table-derived writes, not unconditional final configuration values. Later branches in these bodies can override `006fbc3c`, and other initialization/configuration paths may write the same destinations. The [vehicle-dispatch comparison](original-modern-vehicle-dispatch.md) already maps consumers of `006fbc1c` and `006fd1d8`; remaining semantic setting names are not inferred from their positions in the table.

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
