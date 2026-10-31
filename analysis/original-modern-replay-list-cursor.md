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

## Drawing and hit-test follow-up: static row correspondence

The expanded audit retains and asserts byte equality for complete bodies **`00462d20..00462f84`** (list update/drawing), **`004633d0..004634c8`** (list geometry/scroll normalization), and **`0049c1c0..0049c1e5`** (mouse-row division). These unchanged consumers explain the corrected keyboard offset; no drawing or input was executed.

Geometry copies control WORD+08h to Y-origin field+1ah, WORD+06h to X-origin+1ch, and sets width WORD+1eh to200. It computes the last-visible WORD+56h from first-visible WORD+54h and the bounded visible-row count. This establishes the row/scroll role left provisional above; other fields and malformed states remain outside this layout summary.

The drawing loop starts its row coordinate at **Y-origin+57** (`00462e1f..00462e25`) and advances it by16 for each visible entry. Mouse selection uses the same origin+57 and row step16 before calling **`0049c1c0` at `0046309f`**. That helper takes base in EAX and row divisor in EDX:

- If signed mouse Y `< base`, return−1.
- Otherwise return signed quotient **`(mouseY−base−1)/divisor`**, truncating toward zero through IDIV.

For normal nonnegative visible-row offset `r = selection−first_visible`, within nonwrapping coordinates and divisor16, the Modern keyboard position gives:

`mouseY = Y-origin + 16*r + 68`

`mouseY−base−1 = 16*r + 10`, hence quotient **r**.

The original keyboard position instead gives `mouseY = Y-origin + 16*r + 8`. For r0..3 it is above base and returns−1; for r>=4, `(16*r−50)/16` truncates to **r−4**. This is a static consistency result between the inspected positioning and row-mapping contracts, not a live cursor test or an equivalence probe. It explains why adding60 aligns keyboard positioning with the retained list’s hit-test bands.

At exactly mouseY==base the helper computes−1/16, which truncates to0; replacing this routine with a generic floor-division formula would change that boundary. It also has no zero-divisor guard in the shown body. A reconstruction must preserve the machine-width arithmetic and deliberate−1 bias rather than silently cleaning up those details. Complete outer admission, valid list counts and observed platform cursor placement remain unverified.
