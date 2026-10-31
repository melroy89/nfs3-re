# Graphics menu: snapshot, Cancel and mode-request transition

## Counterparts and evidence

The static registration row `00556068` retains init callback `00448440`, redirects runtime descriptor+0ch from original **`004484e0`** to Modern **`004484bc`**, and removes the original return-zero stub at descriptor+10h. The [registration comparison](original-modern-menu-callback-table.md) proves these relationships; the Modern callback is not paired with original code at its new address.

The [audit script](scripts/audit_graphics_menu_transition_difference.py) pins executable hashes and retains complete init/transition bodies and selected Modern dependencies. [Manifest](evidence/audits/original-modern-graphics-menu-transition.json). Ends are exclusive. No display, game, callback or instruction probes were run.

| Role | Original range | Modern range |
|---|---|---|
| Init callback | `00448440..004484d7` | `00448440..004484ba` |
| Transition callback | `004484e0..00448561` | `004484bc..00448553` |

## Shared snapshot and changed initialization

Both init bodies copy **16 DWORDs / 64 bytes** from `006fbc10` into shared backup `006627b0`. They look up `CARSHADE` and `CARSHADE_TEXT` and retain the renderer-mask-dependent flags at the inspected tail: byte flag 1 for the former, WORD mask `1001h` for the latter, when `[007a3a58] & 6` is nonzero and the entry exists.

Original first calls `004482c0`, then compares signed selected index `006fbc14` against `00559218`, resetting it to zero when not less. Modern instead calls `00448394` (request-to-mode selection), `00437614` (the separately audited Race Now policy) and `004377c4` before taking the snapshot. The fog-gate helper is mapped in the follow-up below. The old index field has changed meaning; its original clamp cannot simply be transplanted into Modern.

Original additionally looks up `credits` at `00538d7c` and disables the result when signed session mode `006fd3b0 > 1`. Modern repurposes those string bytes as `%s %s` and removes that local block from the shorter init body. Its earlier call to the separately audited Race Now policy can handle Credits flags in a broader conditional context; removal of this block alone does not prove that Credits becomes universally enabled.

## Original transition

The callback computes the selected item from the signed high words of descriptor fields read at +16h/+18h, using `00604ee0 + wrap32(index*bch)`. If it is type 5 (button), it tests the codelink against `CANCEL_GRAPHICS_OPTIONS` through `004429c0`.

- On a match, copy 64 bytes from `006627b0` back to `006fbc10` and return zero.
- Otherwise call `004482c0`, read the original selected row index `006fbc14`, and store that `114h`-stride row's DWORD+4 from the original mode table at `00661220` into `006fbc18`.

The original callback has no local call to Modern's request-based selector or dimension-update helper. Its stored DWORD is not assigned Modern's packed width/height meaning; see [resolution defaults](original-modern-resolution-defaults.md).

## Modern transition

Modern reads signed WORDs at descriptor+18h and +1ah, sums them and forms the same `bch`-stride item address. These WORDs correspond to the two high-word extractions in the original. It only tests the codelink when item type is 5, but the helper changes from `004429c0` to **`0043778c`**.

That Modern helper calls `004429c0` and preserves its result on the stack. On a match it copies `00664688 → 006fd1d8` and `00664684 → 006fd1d4`. On a nonmatch it copies the latter pair only if Modern effective fog-support flag `007a3a54` is zero. It then restores the comparison result to EAX. These extra global writes are observable code effects; their full producer/ownership contracts remain separate.

If the returned comparison result is nonzero, Modern restores the same 64-byte snapshot and calls **`00448394`** to reselect/reapply the restored request before returning zero.

Otherwise it performs the new request-construction path:

1. Set bit 0 of `006fbc14` using BTS, initially requesting the 32-bit-depth choice.
2. Get the selected menu row through `00448348` and the last row through `0044837c`. Selected-row helper resets an unsigned out-of-range selected index to zero; neither helper proves the list is nonempty.
3. If the selected pointer equals the last-row pointer, store packed sentinel **`7fff7fffh`** into `006fbc18`.
4. Otherwise compare selected and last row DWORD+0ch (depth in the established mode-record layout). If unequal, toggle bit 0 of `006fbc14`. Store low WORDs of selected row+4/+8 into `006fbc18`/+1ah (width/height request).
5. Pass the selected row to `00448400`, which copies width/height/depth into `006fd1e4..006fd1ec` and calls `00485680` if width or height changed. General registers are restored and EAX is zero on return.

The sentinel records the final-row choice in the persistent request while the selected actual row is still used for current dimensions. It is not a literal 32767×32767 render size. The nearest-area/default interpretation and arithmetic limits are covered by the existing [mode-selection](original-modern-mode-selection.md) and [requested-defaults](original-modern-resolution-defaults.md) reports.

## Reconstruction implications and remaining evidence

This is a changed transition implementation, not just a moved pointer. Preserve version-specific field meanings, the 64-byte snapshot, the comparison helper's hidden global writes, Cancel's reselection and the final-row/depth encoding. The backup is shared scratch storage: nesting or concurrent entry into this settings flow cannot be assumed safe without mapping all its writers and menu-stack ordering.

Nonempty mode lists, valid item/descriptor pointers, initialized snapshots and ordinary forward string-copy state remain preconditions rather than proven global invariants. Runtime display changes, settings serialization and failure behaviour are untested. Original and Modern enumerate/select through different helpers; similar selected rows do not prove equivalent outputs.

Next: trace snapshot/global producers and descriptor transition invocation ordering, then qualify mode-list boundary cases and settings persistence when runtime comparison is in scope. No historical release date or release-note fix is inferred solely from this final executable pair. Existing bytes, saved Ghidra state, reference exports and maintained C are preserved.

## Fog gating and saved-setting shadow pair

This follow-up reuses the existing [fog-gate research](detailed-analysis-notes.md#fog-option-gates-and-settings-copies-0043778c00437801) and retains its complete code spans against the pinned official executable:

| Range, end exclusive | Verified behaviour |
|---|---|
| `004377c4..00437801` | Input EAX is the menu descriptor/context. PUSHAD preserves general registers. Copy `006fd1d8 → 00664688` and `006fd1d4 → 00664684`. Load `007a3a54` into ECX; if zero, clear `006fd1d4`. Apply that gate to two named entries and POPAD/RET. Arithmetic flags are not preserved by PUSHAD. |
| `00437801..0043781d` | Use EBX as context, EAX as token and ECX as gate. Look up entry via `00442a40`; ignore a missing entry. For nonzero gate clear bit 0 of entry byte+4; otherwise set it, preserving the other bits. |
| `00538a20` / `00538a2c` | Exact tokens `GRAPH_FOG` and `GRAPH_FOG_CASCADE`. |

The renderer [configuration loader](original-modern-renderer-loading.md) normalizes `THRASH/FogSupport` into `007a3a54`; the later [renderer initialization query](original-modern-renderer-initialization.md) may clear it when the driver query returns zero. It is therefore an **effective fog-support gate in Modern**, not the original renderer selector merely because the address is reused. This corrects the earlier wording in this chapter. Actual driver fog rendering is not proven by the flag.

Together with restore helper `0043778c`, the new evidence closes the ordinary shadow-copy direction: gate application saves the pair before possibly clearing the live value; a matching Cancel token restores both. On a nonmatching token, the restore helper only restores `006fd1d4` when the gate is zero. Do not erase these writes during C reconstruction or silently assume the two settings' complete semantic types from the fog-token names alone.

Three direct calls to `004377c4` are now independently checked at `00448458`, `00448642` and `0044d2c0`. The latter two witnesses show a related init context and another settings snapshot context; they do not by themselves identify every enclosing menu or prove lifecycle ordering. The first graphics init applies the gate **before** the 64-byte snapshot. The `00448620..00448647` witness takes that snapshot **before** applying the gate. Those orders are observably different and should not be merged into one generic sequence without verifying caller contracts.

The saved pair and the 64-byte snapshot are separate shared storage. All writers, nested menu admission and reentrancy remain unenumerated. A bounded direct-call census from retained disassembly is not proof that indirect callers do not exist. No new target execution or Ghidra edits were made.

## Authored fog controls bind the verified selector

The expanded graphics audit verifies `fedata/menus/graphics.mnu` and `advgrph.mnu` against the pinned official archive. Graphics contains an authored `nextmenu=advgrph` route. Advanced Graphics contains these two controls:

| Section | `codelink` | `listname` | Other relevant authored fields |
|---|---|---|---|
| button | `GRAPH_FOG` | `fog` | `buttontype=arrowtab`, ypos1, priority9 |
| cascade | `GRAPH_FOG_CASCADE` | `fog` | ypos1, priority0, maxvisitem5 |

The two codelinks are exactly the entries processed by the support-gate helper documented above. The descriptor at `00556924` binds name `fog`, list pointer `005561be`, and selector DWORD `006fd1d4`; its list WORDs are `00e5,00e4,0000`. These are two nonzero list entries followed by zero, not five selectable values merely because the authored visible cap is5. Localized labels and input-to-ordinal writes remain separate contracts; no Off/On wording is invented from the numeric IDs here.

The [scene-admission comparison](original-modern-state14.md#modern-scene-entry-recomputes-fog-admission) establishes that `006fd1d4` participates in the bitwise admission computation `007a3a54 & 006fd1d4 & 00559234`. Thus this asset/descriptor/consumer chain connects the fog controls to the setting used by the inspected render path, beyond finding a label in strings. The support gate can disable the controls and clear the selector as already described; scene context and renderer behavior still matter.

For the comparison, local uppercase backup `fedata_org/menus/ADVGRPH.MNU` contains no item with `listname=fog`, while official Modern contains the two above. Both file hashes and selected fields are retained. This backup is **not authenticated as retail or paired to the supplied original executable**; its absence is bounded asset evidence, not proof that no original menu/configuration/command route could affect fog.

**MP150-008 now has partial static support:** a concrete menu route and bound fog-control mechanism are verified in final Modern, with a qualified backup contrast. Complete input dispatch, actual ordinal changes, renderer output and historical introduction remain unverified. No menu, driver, game or new instruction probe was executed, and the established Ghidra project is unchanged.
