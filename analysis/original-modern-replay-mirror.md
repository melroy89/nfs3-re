# Original versus Modern: replay mirror/variant admission

## Evidence boundary

Static supplied-original/official-Modern comparison, with exact identities in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_replay_mirror_difference.py`. The [manifest](evidence/audits/original-modern-replay-mirror.json) retains toggle, eligibility, refresh-gate and input witnesses, plus hash-pinned checks of the 1.3.1 and 1.4.0 archive members. No replay, keyboard or target instruction was executed.

The current saved analysis names `00484450` as the primary-view variant toggle. Its shared eligibility and HUD paths are relevant to **MP140-064**'s replay-mirror claim, and its default F7 input chain is now traced below; rendered output remains untested.

The retained 1.3.1 and 1.4.0 archive members date both local changes to the reported release boundary. The 112-byte toggle span `00484450..004844c0` and 304-byte eligibility span `00422aa0..00422bd0` in 1.3.1 match the supplied original byte for byte. Both spans in 1.4.0 match final 1.6.1 byte for byte, including the checks of `00791b1c`. This dates the switch from rejecting replay state to a stateful opt-in at the two selected entry points. The renderer outcome and full replay lifecycle remain untested.

## Original broad rejection becomes a stateful enable path

Original `00484450` returns when mode `006fd3b0==1`, and also when **`006fd3a0!=0`**. Otherwise it obtains primary view 0 through `00422bd0`, chooses one of two layout records using bit 0x20 of view byte `+0x200`, toggles the DWORD at `006fbc5c + variant*0x1a4`, and calls `004844c0` with EAX=0.

Modern keeps the first mode-1 rejection, but removes the second broad state rejection. It forms the same layout-field pointer in EDX, calls predicate `00422aa0` and saves its return in ECX. Then:

- If enable global **`00791b1c==0`** and playback state **`006fd3a0==2`**, set the enable global to 1. If the previously evaluated predicate was nonzero, also write DWORD 1 to the layout field. Call refresh regardless of that predicate result.
- Otherwise, only proceed when the predicate is nonzero. Toggle the field by comparing its full DWORD with zero and SETE-writing **only its low byte**, then refresh.

The low-byte write differs from original's complete DWORD 0/1 store. Ordinary Boolean producers make them agree; arbitrary nonzero upper bytes do not. Do not silently rewrite this as a universally equivalent Boolean DWORD assignment.

The predicate is evaluated **before** first-enable changes the global; it is not re-evaluated before the conditional field write. Refresh can therefore be significant even when that earlier predicate returned zero.

## Eligibility changes in the shared predicate

The enable flag already has producers in the supplied original. The HUD batch/layout initializer at `00484070` clears EDX at `0048407d` and stores zero to `00791b1c` at `0048409c`. A separate replay-state branch at `004842a8..004842de` sets both the selected layout master DWORD and `00791b1c` to 1 when the flag is clear and state `006fd3a0` is 2. Both spans match byte for byte in the original, archived 1.3.1 and 1.4.0, and final 1.6.1. The 1.4.0 change therefore adds use of this existing flag in the mirror toggle and eligibility helper. The separate branch's full input route and reset coverage across replay transitions remain unresolved.

Both `00422aa0` entries first obtain a view/camera object and check multiple gates: a signed threshold of 320 on global `007d3684` (identified as the race tick in existing simulation research, not a screen-size field), non-null object and absence of object byte `+0x200` mask 0x02, among others.

Original additionally rejects renderer mask bits **0x180** at `007a3a58`. Later it rejects playback state **2** unconditionally unless the earlier `00559264` override has already returned success.

Modern removes that renderer-mask rejection in this inspected predicate. It retains the override, then rejects state 2 **only while `00791b1c==0`**. After that it still checks per-view state `0079c4a0`, global `0055fe30`, camera/object fields and an accepted numeric range through `00423b00`. Enabling the global therefore does not guarantee visibility in every view or camera.

Its normal epilogue explicitly preserves EDX, which explains how the caller's layout pointer survives this predicate call. Early assumptions that EDX is an output here would misread the toggle's stores.

## Refresh gate also follows the enable global

The refresh prefix `004844c0..00484599` tests `00791b1c` before its state-2 early-out. When the HUD master field allows refresh and the flag is set, the prefix reaches the layout-building calls `00480fc0` and `004812e0`. Byte comparison shows that this 217-byte prefix matches in the original, 1.3.1, 1.4.0 and final. The two HUD presentation gates at `00482d6b..00482d8e` and `00482f5b..00482f7f` also match across those four builds and already test the flag. Thus 1.4.0's revised F7 toggle and eligibility helper feed existing refresh and presentation gates. The complete render chain and output remain unverified.

## Default F7 binding to action 11: complete static chain

Fixed-binding initializer `0048f970` writes encoded value **0x4104** to **`0079c3cc`**. The evidence script asserts that exact immediate instruction in both executables. The mask builder **`0048f550..0048f699`** is also byte-identical, asserted by the script.

The builder starts at binding base `0079c340`. Each participant uses twelve DWORD slots (0x30 bytes): four axis-like entries followed by eight button entries. For one-participant mode it skips a further 0x30 bytes; for two-participant mode it consumes a second twelve-slot block. Both ordinary routes therefore reach **`0079c3a0`** before the shared 32-action loop (`0048f645`).

`0079c3cc = 0079c3a0 + 4*11`, so this binding feeds shared **action 11**. The loop examines the signed low byte of each encoded DWORD and calls `00431800` for a nonzero type. For `0x4104`, that helper recognizes type **4**, extracts `(encoded << 8) >> 16 = 0x41`, and reads keyboard state byte **`00564818 + 0x41`**. A nonzero byte returns 255. Other fallback branches apply when the byte is zero; those do not change the direct default binding's index.

The builder shifts the accumulating mask right once per shared entry and sets bit 31 on active input. After all 32 entries, the value contributed at index 11 occupies bit 11. It stores that mask in ring `0079c2b8`, indexed by an incremented counter masked with 31. The action reader `0048f7b0` uses the consumer-selected current/prior ring positions; it does not itself advance the producer.

Race-loop callsite **`004c5097..004c50ae`** requests action 11 with EDX=1. `0048f7b0` then tests `current & ~previous & (1<<11)` and calls `00484450` on success. This supplies the previously missing binding → key state → mask bit → edge → toggle linkage.

Microsoft's Scan 1 table maps scan index **0x41** to **F7**. This is a scan-code interpretation, not virtual-key `0x41` (A). [Keyboard Input Overview](https://learn.microsoft.com/en-us/windows/win32/inputdev/about-keyboard-input)

The static default chain is therefore established. Actual OS/Wine keyboard delivery, remapping, ring scheduling and pressing F7 during replay remain untested. Unchanged binding/mask code also shows that this default key was not newly invented by the replay-admission change.

The historical audit verifies that the binding initializer, keyboard decoder witness, mask builder, action reader and selected race-loop callsite match in 1.3.1 and 1.4.0 as well as the original and final. The toggle and eligibility spans differ. This isolates the verified release change after the input dispatch, with no inference about live keyboard delivery.

The original also exposes the separate HUD-enable branch through action 12. Binding initializer `0048f9be` loads `0x3f04` and `0048f9dd` stores it to `0079c3d0`, the next slot after action 11. This selects keyboard scan index `0x3f` through the same binding decoder. At `004c5017..004c5031`, the race loop requests action 12 with EDX=1 and calls `00484260` with EAX=0 when the edge is detected. For view 0 this reaches the branch that sets `00791b1c` in replay state 2 if the flag is clear. The binding prefix, action callsite and selected toggle prefix match in the original, 1.5.0 and final. This identifies an input route to the original flag producer. The original mirror-specific toggle still has its separate playback rejection.

## Conclusion and further work

Static evidence supports changes in the F7 toggle and eligibility predicate that feed retained refresh and presentation gates. **MP140-064 remains partial** because the final mirror render chain and output are unverified. The removal of renderer-mask admission is a separate observed change. Actual support across renderers remains untested.

Pending: all enable-global initialization/reset paths, layout-field role across profiles, complete camera eligibility, nondefault input/remapping and rendered replay mirror behavior. This does not alter or validate replay trajectory/file compatibility; the audited changes concern presentation admission.
