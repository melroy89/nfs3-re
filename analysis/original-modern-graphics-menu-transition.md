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

Original first calls `004482c0`, then compares signed selected index `006fbc14` against `00559218`, resetting it to zero when not less. Modern instead calls `00448394` (request-to-mode selection), `00437614` (the separately audited Race Now policy) and `004377c4` before taking the snapshot. The last helper's complete contract is not recovered here. The old index field has changed meaning; its original clamp cannot simply be transplanted into Modern.

Original additionally looks up `credits` at `00538d7c` and disables the result when signed session mode `006fd3b0 > 1`. Modern repurposes those string bytes as `%s %s` and removes that local block from the shorter init body. Its earlier call to the separately audited Race Now policy can handle Credits flags in a broader conditional context; removal of this block alone does not prove that Credits becomes universally enabled.

## Original transition

The callback computes the selected item from the signed high words of descriptor fields read at +16h/+18h, using `00604ee0 + wrap32(index*bch)`. If it is type 5 (button), it tests the codelink against `CANCEL_GRAPHICS_OPTIONS` through `004429c0`.

- On a match, copy 64 bytes from `006627b0` back to `006fbc10` and return zero.
- Otherwise call `004482c0`, read the original selected row index `006fbc14`, and store that `114h`-stride row's DWORD+4 from the original mode table at `00661220` into `006fbc18`.

The original callback has no local call to Modern's request-based selector or dimension-update helper. Its stored DWORD is not assigned Modern's packed width/height meaning; see [resolution defaults](original-modern-resolution-defaults.md).

## Modern transition

Modern reads signed WORDs at descriptor+18h and +1ah, sums them and forms the same `bch`-stride item address. These WORDs correspond to the two high-word extractions in the original. It only tests the codelink when item type is 5, but the helper changes from `004429c0` to **`0043778c`**.

That Modern helper calls `004429c0` and preserves its result on the stack. On a match it copies `00664688 → 006fd1d8` and `00664684 → 006fd1d4`. On a nonmatch it copies the latter pair only if renderer selector `007a3a54` is zero. It then restores the comparison result to EAX. These extra global writes are observable code effects; their full producer/ownership contracts remain separate.

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

Next: finish `004377c4`, trace snapshot/global producers and descriptor transition invocation ordering, then qualify mode-list boundary cases and settings persistence when runtime comparison is in scope. No historical release date or release-note fix is inferred solely from this final executable pair. Existing bytes, saved Ghidra state, reference exports and maintained C are preserved.
