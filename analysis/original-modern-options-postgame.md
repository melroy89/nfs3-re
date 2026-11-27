# Options after race results: mainonly asset restriction

## Finding and scope

**MP140-019 is partially supported by a concrete asset-to-code mechanism.** The official final Options asset removes `mainonly=1` from the Race, Credits and Exit controls present in a selected uppercase local backup. Both executable versions use the same generic mainonly/postgame filtering instructions and zero-valued button defaults. Thus these official entries avoid that specific postgame suppression path, assuming normal template creation/parsing and no later overrides.

The [audit script](scripts/audit_options_postgame_difference.py) pins both executable hashes, verifies identical relevant code/data, and hash-checks the official asset directly against the retained patch archive. [Manifest](evidence/audits/original-modern-options-postgame.json). No menu rendering, input or target instructions were executed. Backup provenance is not authenticated retail provenance; the final original/Modern pair cannot date the change to v1.4.0.

## Authored fields and defaults

| Options control codelink | Local uppercase backup | Official v1.6.1 asset |
|---|---|---|
| `racenow` | `mainonly=1`, `postonly=0` | Both fields absent |
| `credits` | `mainonly=1`, `postonly=0` | Both fields absent |
| `exitprogram` | `mainonly=1`, `postonly=0` | Both fields absent |

Their official button types remain `LR1of3`, `LR2of3`, `LR3of3`, with their Race/Credits/Exit label tokens. Absence of a field is interpreted through the observed template/parser route, not assumed to mean false universally.

The button template at `00556e40` has zero WORDs at item+14h/+16h in both images and a nonzero creation callback at +24h. Existing [template installation and field-storage research](original-modern-slider-percentage.md) establishes the `bch`-byte template copy and instance-relative destination calculation. Identical 16-byte field descriptors map:

- `00557c60`: `postonly`, numeric conversion type1, destination `00604ee0 + 14h`.
- `00557c70`: `mainonly`, numeric conversion type1, destination `00604ee0 + 16h`.

The unchanged numeric writer branch stores a WORD for conversion type1. Normal omitted fields therefore retain zero; the selected backup's explicit1 overwrites the mainonly WORD. Later writers and alternate file-loading paths remain unenumerated.

## Postgame-context producer and suppression consumer

The original/Modern prefix `0044b24e..0044b271` is byte-identical. At entry to the outer frontend loop it compares the supplied context name to literal **`postgame`** at `00539048`, and stores **1** to `00662968` on equality, **0** otherwise. This describes the loop's initial context flag, not the name of every subsequently active nested menu. A nested Options descriptor can therefore still be processed under an outer postgame context. Actual entry and nesting in a particular session were not observed here.

Complete generic initializer **`0044a960..0044a9db`** is also byte-identical. It scans entries until the type-zero sentinel. When item creation callback+24h is nonnull, it invokes that callback, then applies:

| Item field / context | Flag effect |
|---|---|
| `postonly != 0`, `00662968 == 0` | OR WORD item+4 with `1001h` |
| `mainonly != 0`, `00662968 != 0` | OR WORD item+4 with `1001h` |

The code does not locally clear this mask when conditions are false. Fresh template state, preceding callbacks and other writers matter. The [flag-consumer audit](original-modern-race-now.md) separately maps bit0 to a navigation exclusion and bit1000h to suppression of the inspected entry draw callback. Those consumers support the relevance of this mask without treating it as a universal visibility invariant.

For the selected original-like asset, ordinary postgame initialization therefore applies this suppression to the three mainonly buttons. In the official asset with ordinary zero defaults, this **particular** filter does not apply it. Other policy paths can still disable or suppress a control; this is not a proof that every control is always visible/enabled.

## Separate policy and reconstruction requirements

Modern Options initializer `00442aa0` calls shared policy helper `00437614`, replacing its older local Credits gate; the [Race Now report](original-modern-race-now.md) documents that branch map. That policy is separate from generic mainonly filtering. In particular, **MP140-020** (Race hidden when Options opens from the first screen) still requires its lifecycle-state interpretation and entry-path proof; removal of mainonly fields does not prove it.

For C reconstruction, preserve the outer-context flag, zero template defaults, WORD field layout, creation-callback ordering and OR-only suppression semantics. A port that uses the current nested menu name alone to decide postgame state, or restores `mainonly=1` while adopting Modern assets, can change control behaviour even with an otherwise faithful button renderer.

Next: reuse the conditional postgame-to-Options admission/return witnesses below, qualify later flag writers, compare actual selected assets in a suitable runtime session, and obtain intermediate packages if historical attribution is required. Do not silently turn this bounded mechanism into whole-postgame UI equivalence. Executables, saved Ghidra state, raw exports and maintained C remain preserved.

## First-screen Options policy: a new setup-state producer

**MP140-020 now has partial static support from the setup-to-Options chain**, in addition to the already mapped policy helper. The expanded audit captures the complete setup initializer in both images:

| Original | Modern |
|---|---|
| `00452f80..004530bb` | `00452f80..004530c0` |

The Modern body is exactly the original body with **five bytes inserted at `004530b4`**, `a3 6c 27 7a 00` (`MOV [007a276c],EAX`). The preceding `XOR EAX,EAX` is retained, so this new store clears the global. The audit asserts byte-identical prefixes and byte-identical shifted epilogues. This is a complete counterpart comparison, not only an isolated store witness.

Static registration row `00555f60` identifies this as `setup`'s initializer. The official [setup asset](original-modern-setup-website.md) supplies `nextmenu=options`, and the [generic transition trace](original-modern-setup-website.md#generic-options-transition-retained-code-changed-asset-route) resolves such a target to the loaded Options descriptor under its stated admission conditions. The unchanged Options row `00555c48` supplies init callback `00442aa0`.

Modern Options initializer now calls **`00437614`** at `00442ae3`, replacing the original local Credits-only gate. Its earlier two local entry checks remain. The [complete policy helper](original-modern-race-now.md#modern-helpers-exact-branches) proves that when `007a276c == 0` and an entry named `2btt` exists, it:

- ORs `1001h` into found `racenow` and `3btt` entry flags.
- Clears those same bits on the found `2btt` entry.
- Returns without the nonzero-state Credits/postgame Race branch.

The official Options asset has both `3btt` and `2btt` image entries alongside `racenow`, so the authored target set exists. The corresponding flag consumers suppress the inspected draw callback and exclude ordinary navigation candidates. These are entry effects, not proof of the final pixels or complete input rejection.

The helper also has an early return when its non-null context is paired with `00559234 != 0`. The outer frontend loop's retained prefix `0044b271..0044b28a` explicitly clears this latter global during ordinary initialization; later writes and pause/modal admission remain separate. Similarly, the setup initializer's clear of `007a276c` establishes a state producer, not an immutable invariant through arbitrary nested menu events. Known mode-menu writers can set the state to1; the [producer census](original-modern-race-now.md#branch-selector-producer-witnesses) remains relevant.

This supports the release claim for an ordinary sequence that initializes setup, takes its authored Options transition, and reaches the policy without intervening state overrides. It does not establish every user-visible first-screen route or the v1.4.0 introduction date. Original does not have this inserted state store or call the shared Modern policy from Options; its final visible result still depends on original assets, generic flags and rendering.

For C reconstruction, retain the new setup write as well as the policy consumer. Translating only the shared helper while leaving lifecycle producers at their original behaviour would miss the mechanism. Keep this mutable state separate from the postgame context flag `00662968` and pause/context flag `00559234`; they control different branches.

## Postgame-to-Options transition and return witnesses

The [expanded audit](scripts/audit_options_postgame_difference.py) now reads `POSTGAME.MNU` directly from both pinned archives. Each contains exactly one button labelled `kMenuPOSTGAMEOptions001`, with `nextmenu=options`, type `LR2of3` and no authored codelink. It also verifies that the author-reference `OPTIONS.MNU` hash matches the selected local backup used above. This improves source identity without authenticating pristine retail.

The already compared [generic nextmenu route](original-modern-setup-website.md#generic-options-transition-retained-code-changed-asset-route) applies conditionally to this button as well: its ordinary button template has zero specialized-callback fields at+58h/+64h, the input handler can return action5, and descriptor-name lookup can find Options. Later field writers, loaded-descriptor presence and selection/default-entry checks remain admission conditions. An authored string alone is not a successfully observed transition.

New complete or explicitly bounded original/Modern comparisons establish the rest of this local control flow; all listed bytes are identical across the supplied original and official final EXEs:

| Range, exclusive end | Verified role |
|---|---|
| `0044b7ec..0044b8d3` | Action5 lookup: on a found target, calls history helper `0044af10`, processes the outgoing descriptor through `0044aa30`, publishes the new active descriptor at `00559230`, and branches through `0044b6f6` rather than restarting the outer context-name prefix |
| `0044af10..0044af4a` | Complete history helper: shifts stored descriptor pointers and writes the current active descriptor to `00662800` |
| `0044b30b..0044b326` | Loop entry calls `0044ab40` with the active descriptor and stores its returned action |
| `0044ab40..0044ac7c` | Complete descriptor initializer: after conditional preparation, calls descriptor callback+08h if nonnull, then calls generic entry initialization `0044a960`, then `0044a860` |
| `0044b8f7..0044b90b` | Existing return branch processes the outgoing descriptor, calls `0044aec0`, then resumes the descriptor loop at `0044b30b` |
| `0044aec0..0044af05` | Complete restore helper: obtains the saved descriptor from `00662800`, shifts the history, substitutes base descriptor `006040d0` if saved pointer is null, and writes active descriptor `00559230` |

Static registration callback offsets and runtime descriptor offsets are different layouts; do not copy the Options static registration's+0ch field blindly into runtime+0ch. The runtime initializer's observed callback is+08h. The loader's complete registration-to-runtime mapping is not newly proved by these spans.

These witnesses explain a conditional nested Postgame→Options route and a separate history-based return route without requiring a new frontend invocation with context name `options`. They support the earlier mainonly mechanism: removing three authored restrictions can matter while the outer postgame flag is still set. **They do not prove the flag is preserved through every subordinate callback**, that the return branch is reached by every key/button, or that the history is valid at arbitrary depth. The outgoing callback, preparation helpers, actual loaded assets and later flag writers retain their separate obligations.

The relevant difference remains the authored restrictions and Modern Options policy already described above. This follow-up establishes retained linkage; it does not invent a new changed algorithm, prove the1.4.0 introduction date or establish rendered visibility. Next work should reuse this route and qualify particular callbacks/state writers or runtime cases, rather than re-investigate whether the authored Postgame Options target exists.

## 1.2.0 game-mode return claim

The [display-helper trace below](#the-display-helper-stops-overwriting-the-history-pointer-in-120) explains how Modern 1.0.0–1.1.0 can lose the selected Setup history pointer and how 1.2.0 preserves it. Live menu selection remains unverified.

MP120-009 describes a fix for returning to Setup instead of the menu for the current game mode. The retained 1.1.0 and 1.2.0 archives contain the same 52 `.mnu` paths after case normalization, and every matched member is byte-identical. Reproduce with `7z l -slt` to enumerate menu paths and `7z x -so` with each exact member name to compare payload hashes. This rules out a change to those shipped menu definitions between the two releases. Other asset inputs and actual post-race selection remain outside this comparison.

The hosted original and Modern 1.0.0, 1.1.0 and 1.2.0 have the same postgame wrapper `004732b0..0047333d`. Each clears EDX at `00473311` and calls the menu loop at `0047331a` with the Postgame name. The first `0x700` bytes of the loop at `0044b230` and the `0x1e0`-byte window at `004730d0` also match across those four images. The application-loop window `004a3db0..004a40b0` differs between the hosted original and 1.0.0, then stays byte-identical through 1.2.0. These fixed PE VA windows place the app-loop change before the 1.2.0 repair.

The equal-length first code sections of 1.1.0 and 1.2.0 have 2,531 differing byte positions when compared at the same RVA. One menu-related edit in that set is at `00452cf1`: 1.2.0 replaces the direct race-mode load with a call that swaps stored modes 1 and 3 for dialog preselection. The `racetype` descriptor at `00556528` is unchanged. The [race-dialog trace](original-modern-race-dialog.md) follows the converted value into the dialog constructor. Its verified effect is which row the dialog initially selects. This evidence applies to dialog preselection. The Setup trace below follows a separate history pointer.

The full saved menu-loop range `0044b230..0044b941`, the 24-byte Postgame registration at `00556038`, and the initializer `0044efd0..0044f4f2` also match across the hosted original and Modern 1.0.0–1.2.0. This extends the earlier prefix check through the loop's return and covers the registered initializer. The [descriptor-binding trace](series-terminal-menu-contract.md#registry-to-runtime-postgame-binding) identifies how the record supplies that initializer. These three ranges contain no release-specific byte change to account for MP120-009. A differing caller, dynamic menu history or a change in a callee remains possible.

The earlier race-session span `004a3690..004a38bc`, generic button handler `00461270..004613db` and menu input dispatcher `0044a2d0..0044a439` are also byte-identical across the hosted original and Modern 1.0.0–1.2.0. In the previously checked application-loop window `004a3db0..004a40b0`, the only original-to-1.0.0 differences are the five bytes at `004a3f35`: the original call to `0040fed0` becomes a short jump to `004a3f3a` followed by three NOPs. That replacement is present before the reported 1.2.0 fix. These additional comparisons cover race-session return and input handling at the named addresses. State written by their callees and alternate return routes remain open.

The menu-history helpers are also unchanged in all four early images. Compare the descriptor lookup window `0044ae60..0044aec0`, the restore helper `0044aec0..0044af05`, the push helper `0044af10..0044af4a`, the name-list restore entry `0044af50..0044af8a` and the descriptor initializer `0044ab40..0044ac7c`. The name-list entry resolves each non-null name and stores each successful result into the corresponding history slot at `00662800 + 4*index`, then calls the same restore helper. This narrows the remaining question to the inputs supplied to those helpers and other state changes. Identical history instructions can still choose different menus when the saved names or descriptor pointers differ.

Linear disassembly of 1.1.0 and 1.2.0 finds one decoded direct call to name-list restore, at `0044b2fa`. The menu loop saves incoming EDX in ESI at `0044b23c`, clears its history slots and calls restore only if ESI is nonzero. Both EXEs have the same two decoded direct callers of the loop: Setup at `0047328d` and Postgame at `0047331a`. Postgame explicitly supplies EDX zero in both, so it bypasses name-list restore on entry. The Setup path calls other helpers before entering the menu loop, so its effective EDX value needs a separate register trace. This direct-call census leaves indirect entry paths outside its scope.

The Setup wrapper does prepare candidate history inputs in both 1.1.0 and 1.2.0. The three 12-byte tables at `004721c0`, `004721cc` and `004721d8` resolve to `{main, setup, NULL}`, `{mainsplt, setup, NULL}` and `{mainmult, setup, NULL}`, respectively, in both builds. The wrapper copies them to its frame at `004730db..00473103`. With `0055b03c` zero, the branches at `004731e7` and `004731ef` select the split-screen and single-player lists in EDX according to `006fd3b0`. Both jump past the separate EDX-clear entry at `00473265`. This establishes identical authored histories and local selection branches. On that same `0055b03c == 0` route, values of `006fd3b0` other than 0 or 1 reach `004731f7`. The code selects the multiplayer list at `0047320e` only if DWORD `007a22e0` is nonzero and WORD `007a22dc` is zero. Otherwise it clears EDX at `0047320a`. Both branches call `0049ede0` before joining the shared display path at `00473267`. The branch window `004731d0..00473218` matches across 1.1.0 and 1.2.0. The complete helper span `0049ede0..0049ee50` also matches in 1.0.0–1.2.0. It saves EDX at entry and restores it at `0049ee4e` on the common return, even when the body reuses EDX at `0049ee21`. Thus the shared display path receives the multiplayer history pointer whenever the local checks selected it and the helper returns normally. In 1.1.0 the same display multiply can then clobber it; in 1.2.0 it survives to the menu loop. This traces the register on that Setup branch. Session state and the menu reached in a live multiplayer run remain unverified.

### The display helper stops overwriting the history pointer in 1.2.0

The Setup wrapper calls `004483a0` at `00473283` immediately before loading the menu name and entering the menu loop. The selected-mode helper at `004483dc` changes its multiply at this release boundary:

| Release | Mode product instruction | Effect on EDX |
|---|---|---|
| 1.1.0 | `MUL DWORD PTR [ESI+8]` at `004483df` | Replaces EDX with the high DWORD of the unsigned product. For ordinary display dimensions the high DWORD is zero. |
| 1.2.0 | `IMUL EAX,DWORD PTR [ESI+4]` at `004483df` | Writes only the low product in EAX and leaves EDX intact. |

The preceding Setup helpers at `004b56d0` and `004bee80` save and restore EDX, as does the mode preparation entry `004482c0`. If the mode comparison requires HUD recalculation, both builds call `00485680` at `004483f9`. The callee saves EDX at `00485682` and restores it at `00485872` before returning at `00485875`. It therefore preserves the value supplied **after** the multiply. The branch that skips recalculation goes directly to the return at `004483fe`.

Both paths can pass zero in 1.1.0 even when Setup selected a game-mode history list. In 1.2.0 both pass the selected pointer through to the menu loop on normal return, allowing the name-list restore to run. This supplies a static mechanism for MP120-009. Actual history resolution and live menu behaviour remain unverified.

To reproduce, use the 1.1.0 and 1.2.0 executable hashes pinned in the [historical mode audit](scripts/audit_mode_capacity_history.py) and disassemble `004483dc..004483ff` and `00485680..00485876` with `objdump -d -Mintel`.

The regression is already present in the checked first Modern release. The original display helper at `004483a0` saves EDX at `004483a1`, uses it as the mode-search index and restores it on both the match return (`004483e1`) and the fallback return (`004483fb`). It copies a stored mode value to `006fbc18` on both routes. Modern 1.0.0 instead uses ECX for the search and calls the new mode-product helper at `004483d3` on both routes, with no outer EDX save. The whole `004483a0..004483ff` window matches 1.1.0, including the EDX-clobbering multiply. This dates the register-contract change to the original-to-1.0.0 boundary in the checked builds and the repair to 1.2.0.

The original executable SHA-256 is `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`. The extracted 1.0.0 executable SHA-256 is `988fbf599af256d1486bef967959893c6b26c9fa8ed21b76310bbb7798b4d9df`. Compare the window from `004483a0` to `004483ff` (end exclusive).

With the history pointer intact, the first name controls the first descriptor. The loop clears the history slots, then `0044af50` resolves each name and stores it at its original index. The restore helper reads slot zero at `0044aec5`, shifts slot one into slot zero, and publishes the saved descriptor to `00559230` at `0044aefb`. The loop passes that descriptor to the initializer at `0044b31e`. Thus successful lookup picks `main`, `mainsplt` or `mainmult` as the first active descriptor, with `setup` left in history. A failed first lookup leaves slot zero empty and uses the base descriptor `006040d0`, even if the second name resolves. A zero history pointer uses the same base descriptor directly at `0044b301` without looking up either name. The helper instructions match in 1.1.0 and 1.2.0. Loaded descriptors and the menu rendered in a running game remain unverified.

The Setup caller still passes the literal `setup` from `0053afb8` in EAX. The menu loop saves that name separately and passes it to its loader at `0044b2cc` before it resolves the history. The later initializer call at `0044b31e` instead takes the active descriptor from `00559230`. The initializer keeps that argument in ECX, reads its name at `+0x14`, and, if present, calls that same descriptor's initializer callback at `+0x08` with the descriptor in EAX. The subsequent first-entry call at `0044b331` reloads the active descriptor from the global. This establishes the handoff from the restored descriptor to its initialization and first-entry code. Callback side effects, asset-load success and which menu is ultimately rendered remain outside the static trace.

Later retained releases keep the repair at the Setup-to-display call boundary:

| Modern release | Display helper called from Setup | Register-preservation mechanism |
|---|---|---|
| 1.2.0–1.3.0 | `004483a0` | Two-operand `IMUL` at `004483df` leaves EDX intact. |
| 1.3.1–1.4.0 | `004483a0` | The multiply reads a different field displacement at `004483df` and still writes only EAX. The HUD update moves to a helper at `004483f8`, which can call `00485680` at `00448413`. |
| 1.5.0 | `0044838e` | `PUSHAD` at entry and `POPAD` at `004483f5` preserve incoming EDX. |
| 1.5.1–1.6.0 | `00448398` | The same save and restore pair ends at `004483ff`. |
| 1.6.1 | `00448394` | The same save and restore pair ends at `004483fb`. |

In 1.5.0 and later, Setup calls the new wrapper at `00473279` and still enters the menu loop at `0047328d`. The final wrapper's inner HUD updater at `00448400` compares the two incoming DWORDs separately at `0044840c` and `00448413`, counts changes in ECX and calls the recalculator only when that count is nonzero. The outer register restoration therefore covers either HUD path. Reproduce by extracting `nfs3.exe` from the retained release archives and disassembling the Setup call site and the corresponding display helper from the listed entry. This comparison addresses preservation across that call. It does not establish how all callers select or populate menu history.
