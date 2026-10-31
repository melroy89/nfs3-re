# Original versus Modern: replay mirror/variant admission

## Evidence boundary

Static supplied-original/official-Modern comparison, with exact identities in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_replay_mirror_difference.py`. The [manifest](evidence/audits/original-modern-replay-mirror.json) retains toggle, eligibility, refresh-gate and input witnesses. No replay, keyboard or target instruction was executed.

The current saved analysis names `00484450` as the primary-view variant toggle. Its shared eligibility and HUD paths are relevant to **MP140-064**'s replay-mirror claim, but full input translation and rendered output remain outside the established scope.

## Original broad rejection becomes a stateful enable path

Original `00484450` returns when mode `006fd3b0==1`, and also when **`006fd3a0!=0`**. Otherwise it obtains primary view 0 through `00422bd0`, chooses one of two layout records using bit 0x20 of view byte `+0x200`, toggles the DWORD at `006fbc5c + variant*0x1a4`, and calls `004844c0` with EAX=0.

Modern keeps the first mode-1 rejection, but removes the second broad state rejection. It forms the same layout-field pointer in EDX, calls predicate `00422aa0` and saves its return in ECX. Then:

- If enable global **`00791b1c==0`** and playback state **`006fd3a0==2`**, set the enable global to 1. If the previously evaluated predicate was nonzero, also write DWORD 1 to the layout field. Call refresh regardless of that predicate result.
- Otherwise, only proceed when the predicate is nonzero. Toggle the field by comparing its full DWORD with zero and SETE-writing **only its low byte**, then refresh.

The low-byte write differs from original's complete DWORD 0/1 store. Ordinary Boolean producers make them agree; arbitrary nonzero upper bytes do not. Do not silently rewrite this as a universally equivalent Boolean DWORD assignment.

The predicate is evaluated **before** first-enable changes the global; it is not re-evaluated before the conditional field write. Refresh can therefore be significant even when that earlier predicate returned zero.

## Eligibility changes in the shared predicate

Both `00422aa0` entries first obtain a view/camera object and check multiple gates: a signed size threshold of 320 at `007d3684`, non-null object and absence of object byte `+0x200` mask 0x02, among others.

Original additionally rejects renderer mask bits **0x180** at `007a3a58`. Later it rejects playback state **2** unconditionally unless the earlier `00559264` override has already returned success.

Modern removes that renderer-mask rejection in this inspected predicate. It retains the override, then rejects state 2 **only while `00791b1c==0`**. After that it still checks per-view state `0079c4a0`, global `0055fe30`, camera/object fields and an accepted numeric range through `00423b00`. Enabling the global therefore does not guarantee visibility in every view or camera.

Its normal epilogue explicitly preserves EDX, which explains how the caller's layout pointer survives this predicate call. Early assumptions that EDX is an output here would misread the toggle's stores.

## Refresh gate also follows the enable global

Modern `004844c0`'s inspected prefix tests `00791b1c` before its state-2 early-out: when enabled, it proceeds to layout-building calls including `00480fc0` and `004812e0`; when disabled and state 2, it skips that route. This is a third coordinated gate, not just a changed hotkey branch. The complete refresh body and render consumers remain separate work.

## Input witness and remaining F7 question

Race-loop callsite **`004c5097..004c50ae`** requests action **11** with EDX=1 through `0048f7b0`, then calls `00484450` on success. That action reader compares current and prior ring-buffer bitmasks, establishing an edge-triggered request at this caller.

Fixed-binding initializer `0048f970` writes encoded value **0x4104** to `0079c3cc`. The vendor identifies the mirror shortcut as F7. However, this chapter has not completed the encoded-binding-to-action-11 translation chain; the binding value alone is not promoted to an independently verified F7 mapping. Remapping/provider input and actual key presses were not tested.

## Conclusion and further work

Static evidence supports coordinated replay-state admission changes in the toggle, eligibility predicate and refresh path. **MP140-064 remains partial** until the full shortcut chain and mirror-render consumer mapping are established. The removal of renderer-mask admission is an additional observed delta, not proof that all those renderers now support the feature.

Pending: all enable-global initialization/reset paths, layout-field role across profiles, complete camera eligibility, input mapping and rendered replay mirror behavior. This does not alter or validate replay trajectory/file compatibility; the audited changes concern presentation admission.
