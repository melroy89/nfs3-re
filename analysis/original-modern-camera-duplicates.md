# Camera-choice cleanup: Done path extracted, non-Cancel exit path added

## Scope and identity

The [focused audit](scripts/audit_camera_duplicate_callers.py) checks both executable fingerprints, paired camera callback registrations, action-handler paths, complete transition callback `0045d9e0..0045daa4`, and the shared duplicate-comparison instructions. The [manifest](evidence/audits/camera-duplicate-callers.json) retains addresses, span hashes and disassembly paths. No menu, replay, race, file save or instruction probe was executed.

Registration rows `00555d50` (`pscamera`) and `00556008` (`camera`) are byte-identical in original and Modern. Both name initializer `0045d920`, transition callback `0045d9e0`, and final callback `0045d9a0`. This establishes the transition counterpart using named registration evidence rather than same-address assumptions. The broader [registration/layout research](original-modern-menu-callback-table.md) keeps callback fields and layouts version-specific.

## Existing action path: comparison instructions become a callable helper

Original handler `0045d770` examines its action input. Its action1 path marks the output byte1 and calls `004446c0`; a zero return at `0045d7a4` jumps to inline comparisons at `0045d7ae`. After those comparisons original loads EAX=3 at `0045d832` and unwinds the handler's frame.

Modern's corresponding action1 path calls the same helper, rejects unsigned results≥2, sets the output byte1 for accepted results, and when the result is zero calls extracted helper `0045d7ad` at `0045d798`. It then restores its PUSHAD frame and returns EAX=3. The result1 path exits with EAX=0 after marking the output byte. These are verified raw action/helper-result values; no general replacement with a Boolean contract is justified.

The 132 comparison bytes `0045d7ae..0045d832` are byte-identical between versions. Modern adds PUSHAD at `0045d7ad`, then POPAD/RET at `0045d832`; the original same address was a RET on a different handler path. The [small-entry comparison](original-modern-small-entry-followup.md#duplicate-choice-code-receives-a-callable-register-preserving-boundary) gives the complete six-check order. This is extraction of existing checks, not a newly invented algorithm.

## New cleanup on the registered transition path

Both transition callbacks derive a menu entry from the incoming context and inspect entry type5 plus token match against `CANCEL_CAMERA_OPTIONS`. The matching Cancel branch restores saved state and bypasses the normal continuation. Their restore implementations differ: original explicitly copies saved cells to camera globals, while Modern uses four MOVSD instructions and also restores `006fd1cc`. The follow-up below resolves exact snapshot pairings; complete semantic meaning, lifetime and caller register expectations remain unqualified.

On the other branch, original proceeds directly to retained call `00472300` at `0045da49`. Modern instead reaches newly inserted `CALL 0045d7ad` at `0045da44`, then falls through to that same call. The branch displacements at `0045da0c` and `0045da1d` are retargeted to include the new cleanup. The full tail `0045da49..0045daa4` (91 bytes) is byte-identical, including the existing update calls and return sequence.

This closes the missing local mechanism behind the bypass claim: normalization is no longer confined to the action-handler's inline completion path; it also runs on the registered camera transition's non-Cancel continuation. Exact routing of every named Race, Credits and Exit game button through this callback still requires the full dispatcher/lifecycle chain. Equal later call bytes do not establish equal persistence results or transitive callee behavior.

## What normalization guarantees

The helper checks the four DWORDs `006fbba8/ac/b0/b4` in priority order and clears later matching entries to zero. It does not exclude zero from comparisons and does not guarantee four distinct raw values. Its relevant established effect is removal of later repeated **nonzero** choices under the ordered comparisons; zeros may remain or be introduced repeatedly. Intended meaning of zero and every choice's localized label are separate data contracts.

**MP151-002: partial static support.** The original completion-path checks, extracted register-preserving helper and added non-Cancel transition call are verified. Universal duplicate-free saving, exact named-button reachability, runtime behavior and introduction in v1.5.1 are unverified. No camera selection was changed, and no executable, Ghidra, raw export or maintained C was modified.

## Complete initializer and paired Cancel snapshot layout

The expanded audit now records complete initializer counterparts **original`0045d920..0045d995`** (117 bytes), **Modern`0045d920..0045d965`** (69), exclusive ends, in addition to the already retained transition callback. Their live-to-shadow maps are:

| Live DWORD | Original shadow | Modern shadow |
|---|---|---|
| `006fbba8` | `006788fc` | `006788f0` |
| `006fbbac` | `006788f4` | `006788f4` |
| `006fbbb0` | `006788f8` | `006788f8` |
| `006fbbb4` | `006788f0` | `006788fc` |
| `006fd1cc` | No local snapshot here | `0066468c` |

Original Cancel restores each of its four values through explicit loads/stores. Modern initializes the contiguous four-DWORD shadow with MOVSD and Cancel copies that shadow back with four MOVSD instructions, then restores006fd1cc from0066468c. Under the expected clear direction flag, both versions’ own save/restore pairs preserve the four choice values; the changed shadow layout cannot be mixed across versions. Modern additionally rolls back006fd1cc on the matched Cancel path. No atomicity, reentrancy, saved-state lifetime or exclusion of intervening writers is proved by these local copies.

Modern initializer adds the Race Now policy call, retains the same binary32 argument bits3f19999ah (approximately0.6) to`00451530` and binds the same action callback`0045d840` to token`escape`, whose string location changes. It removes original’s separate`assists` lookup and language-ID196h text-pointer store in this initializer. This is a local setup change, not proof that every assists control disappears.

The Cancel MOVSD path has an additional register contract: it explicitly writes ESI/EDI and advances them to **ESI00678900 / EDI006fbbb8** after four forward copies. The transition callback saves only EBX/EDX/EBP, and its shared epilogue`0045da9e..0045daa4` clears EAX then restores those three registers; it does **not** restore ESI/EDI. The initializer’s PUSHAD/POPAD does restore its own general registers, so these two routines must not be assigned one generic preservation rule. Actual caller reliance on the Cancel outputs remains unresolved; no ABI defect or runtime failure is asserted.

This narrows the earlier snapshot-layout unknown and records a required reconstruction contract. Complete choice labels, generic lifecycle, remaining aliases and runtime Cancel/persistence behaviour remain unverified. No setting, callback or target instruction was executed.

### The paired camera rewrite lands in 1.5.1

The 1.5.0 initializer still saves the four camera choices individually in the older shadow order and updates the assists text using ID `0x196`. It calls the Race Now policy near its tail at `0045d991). Version 1.5.1 calls the policy before the other setup work at `0045d923`, uses the four forward copies to the new shadow layout, saves the additional `006fd1cc` value and drops the local assists text update. Its transition callback changes at the same boundary, so the paired save and Cancel restore stay in the same release.

Compare the 124-byte window at `0045d920` and the 196-byte callback at `0045d9e0`. Both are byte-identical from 1.5.1 through 1.6.1. The two 24-byte registrations named above also match from 1.4.0 through 1.6.1. This dates the callback changes without relying on a change to which initializer is registered. Runtime menu behavior remains unverified.

The same release adds the rear-view source control to both menu contexts. In 1.5.1, `camera.mnu` adds an arrow tab and a cascade named `rearcamera`; `pscamera.mnu` adds a `blist` button with the same list name and label ID 1938. Neither file uses that list in 1.5.0. The 1.5.1 executable row at `00556550` names `rearcamera`, points to WORD IDs `1939, 1940, 0` at `005563aa` and binds the selected index to `006fd1cc`, the extra value now covered by Cancel. That row and list match through 1.6.1, and each retained pause-menu asset still contains the binding.

Reproduce by diffing the two menu members across 1.5.0 and 1.5.1 and decoding the five DWORDs of the list descriptor and three WORDs at its list pointer. The [viewport trace](original-modern-viewport-pose.md) follows later consumers of the selector. These witnesses establish menu data, selection storage and the matching Cancel snapshot. They do not establish the rendered rear view.

### The rear-view selector is part of the saved configuration block

The live selector at `006fd1cc` occupies bytes `0x168c..0x1690` (end exclusive) of the configuration block starting at `006fbb40`. The [configuration load and save paths](original-modern-config-loading.md) copy the entire `0x20f0`-byte block. The selector can therefore be saved and loaded by the bulk copy even though no individual config read names its address. In final 1.6.1 the grouped-default route calls `00472298`, which stores 1 at `004722a6`. The accepted-header route bypasses that grouped reset. The checked local body of its helper at `00472230` does not write the rear-view selector.

A whole-file scan for the little-endian selector VA finds no literal in the hosted original or 1.5.0. It finds six in both 1.5.1 and 1.6.1: two viewport comparisons, the snapshot read, the Cancel write, the default store and the menu descriptor's selection pointer. The bulk configuration copy explains a persistence path outside that literal census. This establishes saved-block inclusion and a reset condition. No save-and-restart test or exhaustive startup-write trace was performed.

The inspected Wine installation's `FEDATA/CONFIG/config.dat` is 8,432 bytes, declares size 8,432 and version 6, and stores DWORD 1 at file offset `0x168c` (file SHA-256 `2f0b05ad7d0f86e396b61e7c07fad9b28a395952beb80ca1bfd2bd8b411947c7`). In the two-entry list, index 1 is **In Car Camera** (ID 1940); index 0 is **Active Camera** (ID 1939). The installed value agrees with the checked default in 1.5.1 (store at `00472266`) and 1.6.0–1.6.1 (store at `004722a6`). A version-5 settings block that reaches the 1.6.x [post-copy header gate](original-modern-config-loading.md#modern-header-decision-tree) takes grouped defaults, including that rear-view reset. The file read confirms this installation's saved value. It does not establish how that value was selected or what a running renderer displays.

### The 1.0.0 Camera menu gains the standard bottom controls

The hosted original `fedata/MENUS/CAMERA.MNU` and Modern Patch 1.0.0 `fedata/menus/camera.mnu` preserve the same authored items through the original ending. The 1.0.0 member appends three `mainonly=1` buttons and their `3btt` background image at `(281,434)`.

| Codelink | Button type | Authored text or route |
|---|---|---|
| `racenow` | `LR1of3` | `kMenuOPTIONSRACE001` |
| `credits` | `LR2of3` | `kMenuOPTIONSCredits001`, `nextmenu=credits` |
| `exitprogram` | `LR3of3` | `kMenuOPTIONSExitGame001` |

The same three codelinks and background image appear in the 1.0.0 Audio and Graphics menus. This verifies the authored addition for MP100-055. Visibility under different menu contexts, actual input dispatch and rendered position remain untested. Reproduce by extracting the named members from the retained `nfs3_orig.7z` and `nfs3_modern_patch_v1.0.0.7z`. The Camera menu SHA-256 values are `bdeeb5b38abb48858e27467eb3bb37d0ba78821bd0c0e755ed3251df1b059b04` and `164480687764236044e3c753de250869443e5c9df4c4bd7e58cc8cd5c5962b44`, respectively.

All 12 retained Modern packages keep exactly one Camera menu declaration for each of the three codelinks, plus one `image=3btt`. The 1.0.0 Player Settings Camera member `pscamera.mnu` shows a different change from its hosted original counterpart: the only textual difference is the `pstitle` Y coordinate moving from 14 to 9. It does not gain the bottom set at that boundary. The [Race Now policy comparison](original-modern-race-now.md) explains why the persistent Camera declarations alone do not guarantee that every control is visible in every context.
