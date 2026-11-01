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
