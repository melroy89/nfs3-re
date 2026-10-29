# Network series interruption and progression gates

## Scope and target

Static review of the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This follows `RunRaceSession`, its result-builder call gate, the mode-one incomplete-result predicate, and direct numeric exit-state producers. It does not assign gameplay labels to unknown status words or claim a live disconnect/abandonment outcome. No game, network, executable, configuration, live-memory, or persistent Ghidra changes were made; the owned REA session was closed.

## Result-builder admission

`RunRaceSession` (`004a3690`) reaches the result stage only after the race loop and its synchronization/cleanup calls. At `004a3852..004a385f`, the exact call predicate is:

```text
saved context [EBP-4] == 0
AND DWORD[007d36b4] == 0
```

If either condition fails, it skips `BuildRaceResultSnapshotsAndUpdateProgression` (`00455410`). That builder has another outer gate: it returns immediately when playback selector `006fd3a0 != 0` (`00455416..0045541d`). With playback zero it snapshots and ranks local results, then calls the selected series updater: mode 1 invokes `00455070`, mode 2 invokes `00455140`. Neither call has a host/client role check.

The saved-context comparison at `004a3852` is after helper `00410370`, which receives that saved value in ECX. Parent-reviewed assembly confirms that this helper preserves ECX on the inspected normal-return path (including its optional `004e4790` branch, which saves/restores ECX around `004e45f0`). Thus the post-call test compares the saved context value on that path; this does not cover exceptional or nonreturning helper behavior.

Mode 1 has a further result-state gate. `HasStateOneResultUnlessSuppressed` (`004cef80`) asks for a category-0 snapshot whose DWORD at `+0x2c4` equals 1, then returns false when byte `0055eb2e & 0x40` is set. Mode-one updater `00455070` returns before scoring and incrementing `006fd40c` when this helper returns nonzero (`00455078..0045507f`). Mode 2 updater `00455140` has no matching `004cef80` check. Both modes are still subject to the outer `RunRaceSession` exit-state-zero gate.

## Network-state promotion at race exit

At `004a37ea..004a3815`, the race loop may change the numeric DWORD `007d36b4` to 2. The full condition is:

```text
DWORD[007d36b4] != 1
AND saved context [EBP-4] == 0
AND session mode DWORD[006fd3b0] > 1
AND (WORD[007a22dc] != 0 OR DWORD[007a22e0] == 0)
```

Only when all terms hold does `004a3815` store 2. In particular, state 1 branches around this promotion. I leave `007a22dc` and `007a22e0` unnamed here; their local values participate in this branch, but the branch alone does not say “disconnected” or “abandoned.”

The numeric return handling is at `004a386f..004a38b4`: exit state 0 returns application action `0x0c` (the post-race route identified in the normal-series lifecycle report); state 1 returns `0x0a`; state 2 branches to `004a3763`, which returns `0x0b`; values above 2 also return `0x0b` (the main-menu route). State 2 therefore returns to the outer application loop rather than restarting this race session. These are code paths and numeric actions, not proof that a particular lost connection or user choice selects one of them.

## Direct exit/status producers

The direct xref list for `007d36b4` in the active Ghidra import is bounded to references at `004a3776`, `004a377d`, `004a37ea`, `004a3815`, `004a3829`, `004a3856`, `004a386f`, `004c4cde`, `004c4d29`, `004c4d69`, `004c5401`, `004c558f`, and `004ceb39` (`ev_27a3784b7be4ec54067a00c6e5d5a3db173b340f08f20fefe94ce4cc61d119cb`). These include reads as well as writes; they do not prove the absence of indirect updates.

The established write paths are:

- `RunRaceSession` initializes/branches through numeric values 0 and 2 (`004a3776..004a377d`) and applies the network promotion above (`004a3815`).
- Network menu/event handler `004c4be0` sets 2 at `004c4cde` in one branch; another branch stores the value returned in ECX at `004c4d29`; and a separate branch stores 1 at `004c4d69`. These branches follow event ordinals returned by `004c5720` and finalizer calls. Continue and Restart are mapped to candidate resolver inputs 1 and 2 below; Quit event ordinals 3–5 are mapped below; any connection-loss cause remains unresolved.
- `CheckRaceCompletion` (`004ceae0`) can store 0 at `004ceb39` after its normal completion/finalization path and only when playback selector `006fd3a0` is zero. The shared finalizer `004ce750` also writes participant `+0x2c4` states; pause/action branches call it with 1, while the completion dispatcher calls it with 3. As documented in [race completion and shared exit state](race-completion-contract.md), the shared exit flag is not exclusive to a successful finish.

The menu resolver `004c5720` has network-session-mode gates and several event branches that mark participant records with state 1; one path also sets `WORD[007a22dc]` to 1 (`004c59a0`). The installed pause Continue and Restart links are connected to resolver inputs 1 and 2, and the Quit confirmation flow is connected to resolver events 3–5 below. This still does not establish that a transport loss invokes this route. The separate `004a6390` reset clears `WORD[007a22dc]` and `DWORD[007a22e0]`; `0049eed0` requests endpoint/provider cleanup only when `DWORD[007a22e0] == 3` and `DWORD[007a22e4] != 2`. Those are local reset/cleanup gates, not a provider-side disconnect-to-race-outcome mapping. Cleanup requests do not themselves establish a transport-loss-to-race-outcome mapping.

## Pause-menu choices and numeric event handoff

The installed `FEDATA/MENUS/pause.mnu` declares three simple buttons at lines 16–44. Their `codelink`/`text` keys are `PSE_CONTINUE` / `kMenuPAUSEContinue002`, `PSE_RESTART` / `kMenuPAUSERestart001`, and `PSE_QUITBUTTON` / `kMenuPAUSEQuit001`. The English text pack contains standalone strings “Continue”, “Restart”, and “Quit”; this review did not decode their indices back to these menu keys, so it does not claim the exact rendered labels were independently verified at runtime.

The menu-input coordinator `ProcessFrontendMenuInputAndTransitions` (`0044bac0`) directly recognizes the selected entry’s `PSE_CONTINUE` and `PSE_RESTART` codelinks at `0044bd68..bd8c` and `0044bd8d..bdad`, returning numeric values 1 and 2 respectively. In the in-race loop, `004c4be0` calls this coordinator at `004c4c07` and immediately passes its EAX result into `004c5720` at `004c4c0c`. The resolver saves that value in ESI (`004c572b`); after its network/session processing, the `ESI-1` switch at `004c5870..587c` routes a retained value 1 to the return-1 block (`004c5883..58c1`) and a retained value 2 to the return-2 block (`004c58c2..58e3`). The receiving loop then dispatches those resolver returns at `004c4c11..c14` and `004c4c64..c67`. This statically links the pause-menu Continue and Restart codelinks to candidate resolver inputs 1 and 2 and links retained resolver results 1 and 2 to their handler branches. It is conditional: the resolver has preceding session/status branches that can replace ESI (for example `004c57d1`, `004c5804`, and `004c598c`), so this is not a proof that every selected button always yields that final resolver result.

These event ordinals are **not** the race-exit DWORD states 1 and 2. The resolver value 1 takes `004c4be0`'s first event branch (`004c4c16..c5f`), which resets local menu/session values and returns without writing `007d36b4`. Value 2 takes the second branch (`004c4c69..c9e`), updating other session globals and returning without writing `007d36b4`. Thus this chain does not establish an in-race Continue or Restart as a write of exit-state 1/2, nor does static code alone prove the full visible effect of either action.

The Quit button has a menu-specific callback path. The static menu-descriptor table starts at `00555c48`; its `pause` row at `00555cf0` has name key pointer `00537c54`; descriptor initialization (`00442b10`) copies that row’s callbacks to offsets +8/+c/+10, yielding initializer `0044cab0`, transition hook `0044cf60`, and no menu action callback at +10. The type-5 button template at `00556e40` sets input handler +0x30 to `00461270`; its +0x40 and +0x64 fields start at zero. The menu parser’s `codelink` property record writes the token to item +0x10 (`00557c50` row, target offset `0x10`), so the Quit token alone does not populate those optional callback fields.

During pause-menu initialization, `0044cab0` looks up the entry by `PSE_QUITBUTTON` (`005392cc`, bytes decode to that token). If feature byte `0055eb2e & 0x20` is clear, it stores `0044c7b0` at the entry’s +0x64 callback (`0044cde7..cdf8`). The generic button handler (`00461270`, `00461325..d0`) calls a nonzero +0x64 callback on Enter and returns its value. The callback `0044c7b0` constructs a modal through `004446d0`, registering response callback `0044c730`; it returns 2. The selected-entry dispatcher (`0044a2d0`, `0044a428..434`) normalizes callback result 2 to zero before returning to `0044bac0`. Therefore the supported bit-clear Quit path opens a confirmation dialog and does not directly produce resolver event 3, 4, or 5 or write `007d36b4`.

The dialog labels are verified from the installed English `FEDATA/TEXT/text.eng` indexed table (SHA-256 `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`). IDs `0xfc`–`0xff` are “Quit Need For Speed III?”, “Quit Race?”, “Quit Tournament?”, and “Quit Knockout?”; `0xc4`/`0xc5`/`0xc6` are “Yes”/“No”/“Cancel”. IDs `0x1db`, `0x1dc`, `0x1dd`, `0x1df`, and `0x1ef` are “Quit to:”, “Race Results”, “Main Menu”, “Game Setup”, and “System”.

For the ordinary local branch (`006fd3a0 < 2` and not the special network-setup condition `006fd3b0 > 1 && WORD[007a22da] == 0`), the first dialog presents Main Menu (text ID `0x1dd`, action 11), Race Results (`0x1dc`, action 12), System (`0x1ef`, action 10), and Cancel (`0xc6`, action 2). The first two destinations use the mode-selected confirmation ID `0xfd`/`0xfe`/`0xff` (Race/Tournament/Knockout); System uses `0xfc` (Quit Need For Speed III?). The action and text associations are the paired assignments in `0044c93d..c9f6`.
The callback has other selector/network-setup branches (including selector `006fd3a0 >= 2` and the `Game Setup` path); this option-to-event mapping is limited to the ordinary branch stated above.

For a non-Cancel selection, initial-dialog callback `0044c730` calls the Yes/No dialog builder `0044c6d0`, which saves the selected action at `00559268` and installs response callback `0044c610`. An accepted first choice (`004446c0` returns index 0) makes `0044c610` return that saved action 10, 11, or 12. A rejected/dismissed choice returns 2. While the dialog is active, `0044bac0` routes input to modal processor `00445e60` (`0044bb4e..bb6e`); the processor calls the active response callback and returns its action to the coordinator’s ECX. It normalizes response 2 to zero. The coordinator maps action 12 to event 3 (`0044bd0b`), 11 to event 4 (`0044bd1b`), and 10 to event 5 (`0044bd2b`). In the local session gate, `004c5720` returns those incoming event values unchanged; other network-state branches can override them.

The normal receiver outcomes narrow the earlier exit-state gap. Event 3 (`Race Results`) runs finalizer state 1 and stores ECX to `007d36b4`. The receiving function entered with ECX zero and the menu coordinator/resolver preserve it, but this branch also calls `004186a0` and `00470fc0` before the store; their transitive ECX preservation is not yet established. Therefore the stored exit value is unresolved on this path, and reaching the result-builder gate requires it to be zero. If the builder does run, the finalizer/resolver set participant result state 1; mode 1's unsuppressed state-1 predicate blocks progression, while mode 2 has no matching updater predicate. Event 4 (`Main Menu`) runs finalizer state 1 and stores exit state 2; event 5 (`System`) runs finalizer state 1 and stores exit state 1. Those nonzero exit states skip result building, returning application actions `0x0b` and `0x0a` respectively. These are supported static menu paths and branch effects, not observed runtime results or proof of peer agreement.

When `0055eb2e & 0x20` is set, the initializer instead stores marker pointer `005392dc` at item +0x40 and skips installing the +0x64 dialog callback (`0044cdc8..cde5`). The generic handler then returns action 5 via its +0x40 test. That special-config branch is not mapped through the menu coordinator here. No pause-menu item explicitly labeled Return/Exit is present; other resolver inputs outside this Quit branch remain unnamed.

## What can be concluded about interruption

- If a race exits with `007d36b4 != 0`, the ordinary result builder and both series progression updaters are skipped. State 1 returns `0x0a`; state 2 and values above 2 return `0x0b`. State 2 does not restart the race session.
- If the exit DWORD is zero and saved context is zero, the result builder runs when playback is off. Mode 1 still awards no points and advances no progression when an unsuppressed state-1 snapshot is found. Mode 2 does not test that state-1 predicate in its updater; its outer admission still requires exit DWORD zero.
- A specific dropped connection has not been mapped to a write of a given `007d36b4` value, `007a22dc/e0` combination, or participant `+0x2c4` value in the bounded evidence. Likewise, no visible “abandon” label has been connected to one of those numeric paths. Therefore this report cannot say that every ordinary lost or abandoned race skips progression, restarts, or returns to the main menu; it states the exact conditional behavior once the corresponding numeric states are present.
- The type-12 exchange and next-round type-5 block may synchronize participant result data and series globals under their observed gates, but the prior reports do not prove packet completion or define disconnect recovery. No cross-peer progression agreement is claimed.

## Evidence and boundaries

- Active `RunRaceSession` instructions: `ev_116a11c466dcac7e68ace55d8d4198ef4af15f14bb0b3f551be05a7e1b3edda1`.
- Result builder instructions: `ev_951d8fdb1ad73acecd269ba9e29cbf88a27b2b962ed7b3dc43e37e8e9b078acd`.
- State-1 predicate helper `004cef80`: `ev_86fa871d02765821f9b3ca989a31d284072afb94889366d638b06fc3f2e88328`.
- Shared finalizer `004ce750`: `ev_7ce7a3f6bc2ed716f573c213e82410eae7d626716b2e9b349ce51c36b0b1d7b8`.
- Network menu/event resolver `004c5720`: `ev_f73c38264727550634ae299f5b79db62b06e8d031207c80e5f4c35acc2dbd570`.
- Frontend menu input/transition coordinator `0044bac0`: `ev_396a9a5511adba4c147078d314ecf400ebac76be9fb4fea18d90f591d025efc9`.
- In-race menu/event receiver `004c4be0`: `ev_3d0397581d79a3d4509cb33a02fd1aa92e7704ebe50a28daeac4a5d8cefa7364`.
- Button input handler `00461270`: `ev_43cf5cdd53b19239edfb4af641ab87d3fa0db206ebce783f905a3d00a40ed1e4`; selected-entry dispatcher `0044a2d0`: `ev_57001755ad7f029a3f3af9bf5b2775b2606a12eac65aac7a4489295d248e3dc9`.
- Pause-menu descriptor initializer and callback bytes: `ev_b6b293d85b6b39353eff22debea376e1f65fd423ca3d414487730b59ad0f0927` (`0044cab0` region), `ev_0f36d71d1318331140bdd193d328b6e28ac9f3e9ab681d911b716f2924a9f065` (`0044c7b0` region), and `ev_09d03b25b4b508e8559b1c91930ce2e95781a7650543b397775fbec2c06b6e72` (pause descriptor table bytes).
- Pause button template and indexed menu-property bytes: `ev_a646b5e728d4c2f0f599183ef365571f918f1068c728cbcb5e38c5e1fdcaae92` (`00556e40`), `ev_45018041c1b0df7cdead39208c724bd607f76dad4e9df27bddf3c9f8b92938d6` (`00557c10`). The Quit token string is `ev_5d8a9d9fb234fc7df6dee47ede3e0261b76788e2af9ecbf7357e2cde7385d0b0`; its bytes are in `ev_4d4742ba904a094b0adb78fe07d3fac6e38661e1f8e937edbfe988e93b2f71df`.
- Pause dialog callback/response bytes and indexed English strings: `ev_0f36d71d1318331140bdd193d328b6e28ac9f3e9ab681d911b716f2924a9f065`, `ev_76fd55e0d9d788da34c4169d6212b9795ff6b5426fa330c7c1221b41f87ba942`. The English strings were resolved from `FEDATA/TEXT/text.eng` by its indexed offset table; file SHA-256 is `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`.
- Modal processor `00445e60`: `ev_dc8d12cd668f6efc252fd473fa31a95e97dc447fdfad233df72e7a0cf9382ded`; resolver jump-table bytes for event values 1–5: `ev_9ebe7ce132af2bb5c0502c8d61ec2e87c7556f2056ab7bee716d4d498248cf0f`.
- Direct xrefs to numeric exit DWORD `007d36b4`: `ev_27a3784b7be4ec54067a00c6e5d5a3db173b340f08f20fefe94ce4cc61d119cb`.
- Existing complementary evidence: [network series result ownership](network-series-result-ownership.md), [network next-round state](network-series-next-round-state.md), [series result tie and status policy](series-result-tie-policy.md), and [race completion contract](race-completion-contract.md).

Static review only. The remaining gap is a normal supported online run with an actual remote disconnect and a deliberate in-race return/abandon action, observing the event selection, state writes, returned application action, and the next series state on each peer.
