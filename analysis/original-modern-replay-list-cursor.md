# Original versus Modern: replay-list keyboard cursor offset

## Scope and association

Static paired comparison of selection-list input envelope **`00462fa0..004633cd`**, ending at its final RET. Reproduce with `python3 analysis/scripts/audit_replay_list_cursor_difference.py`; the [manifest](evidence/audits/original-modern-replay-list-cursor.json) retains both complete envelopes, matching ranges, template fields and the official menu record. Exact executable identities are in the [baseline](original-modern-differences.md). No keyboard, cursor, rendering or instruction probes; no Ghidra changes.

The official `fedata/menus/loadsave.mnu` contains **`[selectlist]`, `codelink=replays`, x183,y158,maxvis10**. The widget-name row at **`00557ad0`** maps `selectlist` to template **`00556ff8`**, whose+30h input slot points to **`00462fa0`** in both binaries. This directly supports the replay-control association, independently of guessed names for nearby routines. Full runtime menu instantiation remains untested.

## Corrected shared positioning tail

Most of the input handler is identical. Changed instructions are confined to the jump at **`0046326f`** and tail **`00463370..004633a7`**. The manifest separately asserts equality for the remaining prefix, middle and final callback/return regions.

On the branch for numeric input code **5000h**, the retained code increments selection DWORD control+4ch, constrains it and adjusts the two WORD fields at+54h/+56h when needed. Its cursor calculation then changes as follows, using signed16-bit field values:

| Value | Original | Modern |
|---|---|---|
| X | `s16(+1c) + trunc_zero(s16(+1e)/2)` | `s16(+1c) + arithmetic_shift_right(s16(+1e),1)` |
| Y | `s16(+1a) + 16*(selection−s16(+54)) + 8` | Same expression, final constant **68** |
| Cursor call | `0049bfc0` at `004633a2` | `0049bfc0` at `00463391` |

Both call the identical [cursor bridge](original-modern-cursor-position.md). The field+54h participates as the row/scroll origin in this calculation; its full producer/layout contract is not reconstructed here.

For ordinary nonnegative dimensions, the X calculations agree. Negative odd dimensions distinguish truncation toward zero from SAR’s downward rounding, so this arithmetic rewrite is not universal mathematical equivalence. Y gains **60 logical units**, with all arithmetic still operating at x86 widths; no scaling to physical screen pixels is established.

A separate existing navigation branch at **`0046326f`** formerly jumped to `0046339d`; Modern jumps to **`0046338c`**, joining the corrected base-plus-row-offset tail. Its already-prepared EDX/ESI roles still feed the ADD at the new target. This retargeting matters: a translation that copied only the main branch’s new constant would omit another path into the correction.

After cursor movement, Modern sets EAX=0 and calls sound helper **`004181d0` at `00463398`**, then jumps over NOP-filled storage to shared final handling at `004633a7`. Original falls directly from cursor movement to that final handling without the added sound request. Audible sample identity, request success and consistency remain untested.

## Catalog conclusion and remaining boundary

**MP140-014** now has partial static support: the replay-associated selection-list handler changes the keyboard cursor’s final Y offset from8 to68 and routes another navigation branch through that tail. It also adds a direct sound request. Other lists sharing the template may be affected; the change is not replay-exclusive.

This is independent of the generic corner-position Boolean helpers and wrappers described in the [cursor report](original-modern-cursor-position.md). Complete keyboard code translation, all selection/scroll producers, extreme inputs, actual list drawing and observed cursor placement remain unverified. No runtime correctness or whole-game readiness claim follows from this bounded comparison.
