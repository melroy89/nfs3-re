# Original versus Modern: video-mode selection and publication

## Scope and evidence

This extends [mode admission](original-modern-display-modes.md) and [renderer lifecycle](original-modern-renderer-lifecycle.md), using the same hash-pinned supplied original/backup and official Modern v1.6.1. The [display manifest](evidence/audits/original-modern-display-modes.json) retains original `00517610..0051788c`, Modern lookup/filter/product helpers `004bedcc..004beeaf`, and application body `004beeb0..004bef9c`. Reproduce with `python3 analysis/scripts/audit_display_mode_difference.py`. No target, driver or instruction-probe execution.

Existing [screenshot admission research](screenshot-worker-admission-audit.md) already traces the live mode record and its downstream capture use. This report reuses that finding and adds the original/Modern selection comparison; it does not establish general buffer-size safety or actual advertised driver modes.

## Original hard-coded mode IDs

Original `00517610` normalizes its width/height/depth inputs as documented in the lifecycle chapter. Before calling `_THRASH_setvideomode@12`, it selects the following first argument through ordered comparisons:

| Condition, in priority order | Mode ID |
|---|---:|
| Width = 320 | 4 |
| Width = 512 | 6 |
| Width = 800 | 2 |
| Width = 960 | 10 |
| Width = 856 | 11 |
| Width = 1024 | 13 |
| Otherwise height = 502 | 17 |
| Otherwise height = 822 | 18 |
| Otherwise | 1 |

Width 320 is tested at `00517692`; remaining comparisons and branches are at `005177fd..0051788c`. These are literal width/height tests, **not complete resolution-pair matches**. In particular, do not silently replace heights 502/822 with more familiar values. The remaining two stack arguments are 2 and 1. Driver-specific ID meanings are not derived merely from these constants.

## Modern descriptor lookup

Modern `004bedcc` receives three stack DWORDs: requested width, height and depth; it restores registers through POPAD, returns its result in EAX and ends with `RET 12`. It reads descriptor `[007a3a5c]`, count at `+0x3c`, and record base at `+0x40`. Records have stride 0x28. Index zero is skipped: the scan visits indices **1 through count inclusive**, using a signed count comparison.

Only records accepted by `004bee60` are considered; the [admission report](original-modern-display-modes.md) explains that gate and its arithmetic limits. For normal positive fitting dimensions, selection is:

1. Compute requested pixel area using helper `004beea4`, which returns the low 32 bits of unsigned width × height.
2. An exact width/height/depth match ends the scan immediately with that index.
3. Equal width/height but different depth **immediately replaces the current best** with area distance zero and a depth-mismatch flag of 1, bypassing the ordinary distance/tie comparison (`004bee1f..004bee21 -> 004bee41`).
4. Otherwise calculate the signed absolute difference between the candidate and requested low-32-bit pixel areas.
5. For candidates reaching the ordinary comparison, prefer smaller area distance. For equal distance, prefer a depth match (flag 0) over mismatch (flag 1). If both are tied, retain the earlier candidate. The equal-dimensions special case above can override that preference.
6. If no candidate was selected, return **1**, without validating that record 1 exists or passes the gate.

Thus this is area-distance selection with special handling for equal dimensions and an ordinary depth tie-break, **not** nearest width/height distance or aspect-ratio distance. Eligible 1280×720 and 1152×800 have equal area; for a request of 1280×720 at the same depth, an exact 1280×720 record wins, but without that exact match, area alone cannot distinguish equal-area shapes. This is an arithmetic illustration, not a driver/probe result.

Machine limits matter: MUL discards the high product; SUB/NEG operate on 32 bits and comparisons are signed. NEG of `0x80000000` remains negative, so this is not a general mathematical absolute-distance function for arbitrary malformed/overflowing dimensions. No such input was executed. The no-candidate fallback must not be documented as a proven valid or safe mode.

## Modern application and live record

`004beeb0` takes the requested index in EAX, clamps signed values below 1 to 1, and forms `record_base + index*0x28` using low-32-bit arithmetic. Its branches are materially different:

- **Same current index** (`0055fec0`): jump directly to `004bef47`, skipping the count check and driver mode call.
- **Different index**: require signed index within `1..count`, call `_THRASH_flushwindow@0` and `_THRASH_pageflip@0`, then preparation helper `004bef9d`. Read record `+0x14`, cap it to unsigned 2, and derive another argument from a signed comparison with record `+0x18`. Resize/setup through `004cdbd0` before requesting `_THRASH_setvideomode@12` at `004bef24`.
- **Driver returns zero**: branch to final preparation helper; skip current-index update and live-record publication. This local path does not undo the earlier resize/setup call; complete recovery elsewhere remains unverified.
- **Driver succeeds**: update `0055fec0` and `007a3a68`, invoke `00431900`, then join the same-current path.

The shared publication path refreshes the about descriptor, calls `004cdbd0` with record width/height, requests SetForegroundWindow for `[009f3d24]`, copies ten DWORDs into **`007cdae0`**, updates rectangle state through `004bebb0`, and copies eight DWORDs from `007cda60` to `007cdac0`.

The record pointer was formed **before** descriptor refresh at `004bef47` and is then reused; there is no local recomputation from the refreshed descriptor. Pointer stability across the driver's about call is therefore a dependency, not something this function verifies. The same-current path likewise depends on the current index and driver catalog remaining coherent.

PUSHAD/POPAD preserve the caller's general registers; there is no independent Boolean success result written to saved EAX in this function. A C reconstruction must not invent one because the internal driver call has such a return.

## What this resolves and what remains

Verified: original's literal mode-ID decision tree, Modern's descriptor search and tie rules, fallback index, application branch order and live-record publication. This explains how Modern handles a dynamic list beyond original's hard-coded startup selection.

The [default-request comparison](original-modern-resolution-defaults.md) now traces the fixed/large requests supplied by the inspected default-settings path. That path does not establish a desktop-metrics producer. Still unresolved: complete first-run/saved-setting routing (**MP100-011**), all driver catalog invariants, exact renderer argument meanings, descriptor/pointer lifetime, recovery after a failed switch and runtime visual/compatibility behavior. The vendor's “nearest Windows default resolution” claim is not fully verified merely by finding a general nearest-area helper.

## Pending-display recovery retargets the mode-application call

The expanded [display-mode audit](scripts/audit_display_mode_difference.py) now verifies complete same-address callback `0044b1a0..0044b206` (102 bytes, exclusive end) in both binaries. Its only two differing bytes are in the relative CALL at `0044b1e5`, selecting original `004bef50` versus Modern `004beeb0`. The [manifest](evidence/audits/original-modern-display-modes.json) also now retains original application body `004bef50..004bf10f` (447 bytes), alongside the previously captured 237-byte Modern application body. These are corresponding caller roles, not evidence that same-address original bytes at Modern's moved entry implement the same function.

The callback checks pending global `00559444`; when zero it returns 0. Otherwise it writes 13 through incoming EDX, repeatedly calls `004f0710` with EAX=0 and `004c9860`, and polls the pending global until it becomes zero. No local timeout is present in this loop. It then calls renderer slot `009ef918` (the retained `_THRASH_treset@0` binding), sets EAX=1, writes zero to current-index cell `0055fec0`, and makes the version-specific mode-application call.

Both versions subsequently invoke the optional callback at incoming context `+0c`, refresh through `0044a9e0`, and return EAX=1. The mode application's returned EAX is not used as an admission check before those operations. In Modern the application routine restores general registers with PUSHAD/POPAD, as established above. Therefore **callback result 1 is not proof of a successful renderer mode change**. Likewise the initial renderer reset request is not proof that every driver resource was released.

Original's application body also clamps a requested signed index below 1 to 1 and uses descriptor records of stride `28h`; it obtains the about descriptor through `009ef980`. This follow-up retains that complete original body for further comparison but does not claim that all its renderer calls, failure handling or publication paths are equivalent to Modern's previously analysed routine.

**Bounded work status: done for the complete recovery callback and callsite correspondence. Confidence: verified static instructions and existing export evidence.** Required follow-up is the producers/clearing protocol of `00559444`, full original/Modern application failure-path comparison, callback lifetime and actual recovery observation. A C reconstruction must retain the pending-loop and return semantics until those contracts are qualified. No target execution, Ghidra writes or maintained-C edits were performed.

## Original application failure gate and preparation sequence are now paired

The expanded audit now directly checks original application's driver-result gate `004bf060` and Modern's `004bef2a`. **Both test EAX after `_THRASH_setvideomode@12` and skip current-index/live-record publication on zero.** Failure gating is therefore retained behavior, not a new check introduced by Modern. Original failure reaches its post-request surface sequence at `004bf0d7`; Modern reaches its preparation-helper call at `004bef94`.

Original duplicates a 47-byte preparation sequence at `004bf022..004bf051` and `004bf0d7..004bf106`. Modern factors it into `004bef9d..004befcd` (48 bytes, including RET). The audit verifies equality of all 47 instruction bytes after normalizing the single direct CALL displacement. The sequence passes 2 through renderer slot `009ef938`, calls state wrapper `00431900` with EAX=3/EDX=`ff000000`, then calls renderer slots `009ef970`, `009ef940`, `009ef970`, `009ef940` in that order. Slot bindings remain those of the pinned renderer-loader evidence; this comparison does not execute the driver operations.

Both different-index paths retain a flush/pageflip pair before that sequence and a second sequence after the mode request. Thus much of the apparent application-size reduction is factoring duplicated instructions, not removal of every preparation operation. Their transitive effects still depend on the renderer.

A separate interface change precedes the request: original caps record DWORD `+14` using a **signed** comparison against 2; Modern uses an **unsigned** comparison. Ordinary nonnegative values 0..2 pass through and larger positive values cap to 2 in both. Values with the high bit set can differ: original treats them as signed negative and retains them, Modern caps them to 2. Both derive the subsequent Boolean from a signed comparison with record `+18`. The enumerator's ordinary record-admission evidence is not a universal proof that every application caller/driver supplies only those ordinary values.

The timing of local setup/publication also differs:

| Step | Original `004bef50` | Modern `004beeb0` |
|---|---|---|
| Initial descriptor source | Fresh about-export call | Cached descriptor |
| Same-current-index route | Copies ten record DWORDs and updates/copies rectangle state | Joins descriptor-refresh/window/publication route |
| Window resize/setup before driver request | No `004cdbd0` call in this complete body | Calls `004cdbd0` before requesting mode |
| Successful request | Publishes current index/record and retained state/rectangle updates | Publishes index/state, then refreshes descriptor, resize/setup and foreground request before record/rectangle publication |
| Zero driver result | Skips publication; still executes post sequence | Skips publication; still executes preparation helper |

Modern therefore can have performed local resize/setup even when the later driver request fails; this local body supplies no explicit rollback of that earlier operation. Original's absence of that call in its complete body does not exclude equivalent work inside the driver or other callers. The retained recovery callback discussed above still does not turn either local result into a verified successful switch.

**Follow-up status: done for failure-branch correspondence, exact preparation factoring and argument signedness. Confidence: verified static bodies.** Remaining scope is full `004cdbd0` side effects/rollback, descriptor stability, all caller/record invariants, driver implementations and observed recovery. Do not claim mode-application equivalence or a newly added failure check from this refactoring alone. No executable, Ghidra or runtime state was changed.
