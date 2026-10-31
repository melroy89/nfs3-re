# Original versus Modern: colour-control mouse dispatch

## Scope

Static paired comparison of frontend colour handler **`0043ead0`**, original **232 bytes through `0043ebb8`**, Modern **181 bytes through `0043eb85`**. Reproduce with `python3 analysis/scripts/audit_colour_control_difference.py`; the [manifest](evidence/audits/original-modern-colour-control.json) retains both full bodies, shared prefix and five complete identical helpers. Exact executable identities follow the [baseline](original-modern-differences.md). No UI/audio/instruction execution or Ghidra edits.

The saved Modern name identifies an HSV colour control, not the HSV automobile marque mentioned in separate logo claims. **MP140-013** bundles colour dropdown sound consistency and padding; the registration follow-up below now separates the HSV wheel handler from the dropdown’s own render/input callbacks.

## Retained state machine and shorter release actions

The shared prefix **`0043ead0..0043eb1c`** takes the control pointer in EAX and keeps it in ECX/EBX. WORD+8eh is the active region. When it is zero, hit tester `0043e8e0` supplies the hovered region into WORD+8ch. If hover is nonzero and input helper `0049c080` returns13, hover is copied into active. The numeric input code is retained literally here; no hardware mouse event was executed.

Once active, both implementations call `0043e7a0` while the input helper returns13. Otherwise they compare the current hit-test result with the signed active region, dispatch a matching release action and clear WORD+8eh. The release cases are:

| Active region | Action helper | Original preceding request | Modern |
|---:|---|---|---|
| 1 | `0043dd90` | `004181d0` with EAX=0, EDX=127 at `0043eb68` | Omitted; action at `0043eb60` |
| 2 | `0043dc90` | Same request at `0043eb7d` | Omitted; action at `0043eb69` |
| 5 | `0043ddd0` | Same request at `0043eb92` | Omitted; action at `0043eb72` |

The [frontend sound comparison](original-modern-frontend-sound.md) documents `004181d0` independently. Removing these direct requests does not prove silence: generic input feedback, called actions and other controls can still request sound.

Modern refactors the original unsigned comparison tree into three explicit equality tests and shares the final epilogue. It also replaces original DWORD read at control+8ch followed by arithmetic shift16 with **MOVSX from WORD+8eh**. In ordinary little-endian storage these select the same signed16-bit active value, but the read widths differ: the original also reads the neighbouring hover WORD. Layout, overlapping access and potential synchronization assumptions must remain explicit in reconstruction.

Hit tester `0043e8e0` saves/restores incoming EDX across every retained return path, so the post-call comparison against EDX uses the caller’s saved active value. A guessed decompiler prototype that treats EDX as an arbitrary scratch output would obscure that contract. The handler restores EBX/ECX/EDX/EBP but does not establish a uniform EAX return value on all paths; a normal success-return interface is not inferred.

## Identical helpers and evidence limits

The complete bodies of `0043e8e0` (hit region), `0043e7a0` (cursor-driven component updates), `0043dd90`, `0043dc90` and `0043ddd0` are byte-identical. Their saved names help navigation, while their equality establishes only local instructions. Globals, inputs and transitive helpers may differ. This chapter does not reconstruct all HSV mathematics or prove colour output equivalence.

The whole-function inventory’s101 changed bytes within the181-byte Modern range omits the old function’s additional51 bytes. The paired full bodies retained here are therefore the appropriate basis for explaining the removed sound setup and reorganized exits, rather than treating that inventory count as a complete semantic diff.

**MP140-013:** the three removed HSV-handler sound requests are related wheel evidence, not dropdown attribution. The registration follow-up below now verifies the dropdown’s own inset and sound-operand changes; rendered and audible consistency remain untested. The hit tester itself has unchanged bytes. Next inspect its caller/registration and the authored colour-control layout before attributing a padding fix or an audible result. No executable bytes or saved database state were changed.

## Asset follow-up: dropdown and wheel are distinct controls

The [asset manifest](evidence/inventories/colour-control-assets.json), reproduced with `python3 analysis/scripts/inventory_colour_control_assets.py`, compares two selected records in official `fedata/menus/car1.mnu` with the local uppercase backup. The official member is checked directly against the hash-pinned release archive; the backup is not authenticated retail media.

| Widget section / codelink | Backup | Official final asset |
|---|---|---|
| `[carclrselect]` / `CAR_COLOR_SELECT_P1` | x128,y208 | x126,y220 |
| `[colorwheel]` / `COLOR_EDIT` | x163,y209,w155,h210 | Same |

For the wheel, **all shared fields** match, including HSV subrectangles and Accept/Preview coordinates. For the dropdown, the only changed shared fields are x/y; title, priority2 and player0 match. Both official records omit legacy `postonly`, `mainonly`, `EnableForDemo` and `EnableForE3Demo` fields present in the backup. Their defaults are not inferred from omission.

The dropdown therefore has a verified authored left2/down12 coordinate change. It is not yet a verified internal padding change or a measured pixel result. The asset distinction also corrects the earlier premature association of the HSV release-handler changes with the release note’s **dropdown** sound claim. There is a direct call to `0043ead0` at `0043ebd9` in the retained disassembly locator, and the registration follow-up below now associates that caller with the wheel template. Do not merge these widget contracts merely because both edit car colour.

For **MP140-013**, the asset evidence alone remains partial. The follow-up below adds the actual dropdown callback changes; visual/audible consistency remains unverified. The complete HSV code comparison remains useful independent evidence for reconstruction, without claiming it proves that bundled release-note item.

## Registration follow-up: actual dropdown inset and sound operands

The expanded executable audit retains these paired12-byte widget records and100-byte templates:

| Widget row | Name | Template | Template+2ch | Template+30h |
|---|---|---|---|---|
| `00557b54` | `carclrselect` | `005577d0` | `00456ce0` | `00457030` |
| `00557b60` | `colorwheel` | `00557834` | `0043ebc0` | `0043ec40` |

Both baselines contain the shown bindings. The wheel callback witness **`0043ebc0..0043ebec`** calls HSV handler `0043ead0` at `0043ebd9`, then other wheel helpers. This closes the widget distinction; it does not turn the wheel’s removed sounds into dropdown changes.

The dropdown’s render/update counterpart **`00456ce0..00456e98`** differs at exactly three byte addresses: **`00456db2`, `00456e2a`, `00456e2b`**. Complete surrounding instructions establish:

- At `00456dad..00456db1`, a coordinate WORD is loaded from control+1ch and offset by **15 originally,5 in Modern**, then stored as a WORD in the row-drawing local rectangle. The adjacent control+1ah coordinate already uses+5 in both. The patch therefore equalizes these two local insets; the eventual rendered pixel interpretation is not tested.
- Original **`00456e29`** computes `EBX=ECX−1` through `LEA EBX,[ECX−1]`. Modern uses `LEA EBX,[ECX]` plus a NOP to retain the three-byte footprint. This register feeds the subsequent drawing call; exact baseline/pixel coverage is not inferred solely from the one-unit operand change.

The dropdown input counterpart **`00457030..004571d1`** differs at exactly two bytes, **`00457107`** and **`00457142`**. These change **`MOV EAX,1` to `MOV EAX,0`** before direct sound helper calls `004181d0` at `0045710b` and `00457146`. The adjacent branches decrement/increment and constrain the selected entry before refreshing it through `00456f10`. All other bytes in that input envelope match; this is a changed sound-request ID, not removal of the call or proof of a different audio sample heard.

**Updated MP140-013 conclusion:** the named dropdown has a direct verified code change to a15→5 inset and two1→0 sound operands, alongside the separately verified authored position shift. Padding intent now has stronger instruction-level support; “consistent sounds,” exact rendering, driver behavior and historical introduction still lack runtime/intermediate-release evidence. The HSV-wheel changes remain independently documented. No input, render, sound or instruction probes were executed; no saved Ghidra metadata changed.

## Additional frame/title and metadata-layout changes

Three complete same-address original/Modern functions contain only four changed immediate bytes. [The focused audit](scripts/audit_colour_layout_followup.py) verifies pinned executable identities and all surrounding bytes; [its manifest](evidence/audits/colour-layout-followup.json) records complete hashes and disassembly locations. No colour widget, text or instruction probes were executed.

| Saved Modern entry / label | Complete envelope, exclusive end | Verified change |
|---|---|---|
| `0043dfb0` DrawFrontendHsvControlFrameAndTitle | `0043dfb0..0043e033` (131 bytes) | `0043e017`: LEA EDX from signed WORD widget `+6` plus 12→plus 8 |
| `004569a0` CalculateColorSelectorMetadataTextExtent | `004569a0..00456a1f` (127 bytes) | `00456a12`: final WORD `+1e` padding 45→38 |
| `004571e0` UpdateFrontendColorSelectorLayout | `004571e0..0045724e` (110 bytes) | `0045720a`: count-based extent padding 5→8; `00457217`: origin offset 48→28 |

The title path still supplies the text pointer from widget `+9c`, EDX as the adjusted coordinate argument, EBX as signed WORD widget `+8` minus 1, ECX=18, and retained stack arguments to text call `00452190` at `0043e027`. Its preceding frame/image calls remain byte-identical. This establishes a −4 coordinate-argument adjustment, not an observed physical-pixel shift under every scale.

The extent helper retains its localized label lookup, formatting, text measurement and per-entry measurement loop. Only its final WORD padding decreases by 7, modulo 65536. The text-width helper itself reaches separately changed font-measurement behavior described in the [car-alias/text-width report](original-modern-car-alias.md); unchanged measurement call instructions do not establish identical measured widths.

When the layout helper's admission call `0044a660` succeeds and widget WORD `+58` is nonzero, it calls the extent helper and writes:

| Destination WORD | Original formula | Modern formula |
|---|---|---|
| `+20` | `16 * low16(widget[+4c]) + 5` | `16 * low16(widget[+4c]) + 8` |
| `+1c` | `low16(widget[+6]) + 48` | `low16(widget[+6]) + 28` |
| `+1a` | `low16(widget[+8]) + 17` | Retained |

Each stored result is its low 16 bits. The machine sometimes loads only AX before DWORD shifts/adds, leaving inherited high bits; the low-WORD formulas above remain valid, but full EAX/flags must not be assumed equivalent to a freshly zero-extended C expression. When WORD `+58` is zero, the collapsed branch's fixed dimensions and `+6−10` origin remain byte-identical.

**Bounded work status: done; confidence: verified static field/argument changes.** Full field semantics, caller aliasing, font state, rendered geometry and interaction bounds remain unverified. Do not silently repair suspected original layout arithmetic or claim a visual fix from these offsets alone. Executable bytes, Ghidra state and maintained C remain unchanged.
