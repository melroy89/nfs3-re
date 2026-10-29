# Lap choice gameplay domain

## Scope and selected build

Static, read-only trace against the selected installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This joins the Location menu control, normal frontend reconciliation, and race-mode roster dispatch. It does not execute the game or modify the executable or persistent Ghidra project.

## Menu binding and normal selector

The installed Location menu (`FEDATA/MENUS/location.mnu`) defines both a `[button]` and a `[cascade]` with `listname=laps`, `hostonly`, and codelinks `LOCATION_LAPS_BUTTON` / `LOCATION_LAPS_CASCADE`. Its English text resources provide “Laps” and “Select laps…” as the control labels. The file does not enumerate the choice rows themselves; `maxvisitem=2000` is a display cap, not evidence of the choice count.

The active20-byte data descriptor row begins at `00556424`: key pointer `00537e44` (`laps`), WORD-list pointer `005561fa` at+4, zero pointers at+8/+0x0c, and output selector pointer `006fd4b0` at+0x10 (`00556434`). The next row at `00556438` is `direction` (key `00537e4c`); its list pointers do not belong to laps. This binds the Location laps control to `006fd4b0`, the encoded selector. A bounded frontend block at `004487e0` looks up `LOCATION_LAPS_BUTTON` and `LOCATION_LAPS_CASCADE`; for selected race-mode values 1 or 2 it sets disabled-input bit `0x01` on both items, and otherwise clears that bit. This agrees with the normal menu behavior for Tournament and Knockout paths. The exact generic menu event that writes the pointed-to selector was not resolved to one instruction; the row binding and subsequent reconciliation establish the data path, not a particular keypress implementation.

`ReconcileRaceSetupMenuConstraints` (`0044be60`) is called from the ordinary setup menu loop before its input/action dispatch. Its lap section distinguishes the selector ordinal from the actual race lap total:

| Low-word selector ordinal | Decoder result in `006fd4b4` | Encoder result for the indicated total |
|---:|---:|---:|
| 0 | 2 laps | 2 laps → 0 |
| 1 | 4 laps | 4 laps → 1 |
| 2 | 8 laps | other input → 2 |

The decoder at `004cf190` explicitly returns 2 for `AX=0`, 4 for `AX=1`, and 8 for every other value. The reconciler reads the low WORD of `006fd4b0` via `MOV EAX,[006fd4ae]; SAR EAX,16`, decodes it, sign-extends the result, and stores the DWORD to `006fd4b4` (`0044c28d–0044c29b`). Therefore the ordinary menu's three expected ordinals represent actual totals 2, 4, and 8; they are not lap counts themselves. The implementation does not locally reject selector values above 2: those also decode as 8. The installed menu resource does not expose the generated option rows, so this establishes three decoded totals, not the actual generated UI row count.

The reconciler applies mode overrides before this decode. For mode 1 it encodes 4 laps when the session-mode DWORD at `006fd3b0` is signed `<=1`, otherwise 2 laps (`0044c24e–0044c269`). For mode 2 it encodes the current value 2 to ordinal 0 (`0044c27a–0044c282`). In other modes 0 and 3, it retains the current selector and decodes that choice. The broader frontend order and the separation from command-line/network writers are already recorded in [lap-count producer boundaries](lap-count-producers.md).

## From normalized settings to race roster

`RunRaceSession` reaches `PrepareRaceSetupAndBuildRoster` (`00474ca0`) on its normal setup path. The dispatcher switches on race-mode DWORD `006fd3b8`: mode 0 calls `BuildRegularRaceRoster` (`00473bf0`), mode 1 calls `BuildRaceModeOneRoster` (`00474310`), mode 2 calls `BuildRaceModeTwoRoster` (`00473ee0`), and mode 3 calls `BuildHotPursuitRoster` (`00474640`) (`00474cd4–00474cf5`). The installed race-type menu (`FEDATA/MENUS/RACETYPE.MNU`) names Single Race, Tournament, Knockout, Hot Pursuit, and Top Cop in that order. The four-way code-to-label correspondence follows menu order and the reviewed race-mode names; the fifth displayed Top Cop item is outside this four-case builder switch, so its distinct setup mapping is not resolved here.

The roster builder can replace the count normalized by the menu for the two series modes:

- Mode 1 writes 2 laps when the signed session-mode DWORD is `>1`, and 4 laps otherwise (`004743ad` / `004743b9`). The corresponding mode-1 menu control is disabled by the Location-menu state block.
- Mode 2 writes 2 laps unconditionally at `00474011`; the corresponding mode-2 menu control is also disabled.
- Mode 0 uses the ordinary menu-decoded total. Mode 3 has no direct write to `006fd4b4` in the audited direct-writer inventory, so the reviewed path leaves the reconciled total as its input; aliases or later writers are not excluded.

For the normal, menu-controlled path, the supported totals observed at roster entry are therefore 2, 4, or 8 for modes that retain the user selector; Tournament resolves to 2 or 4 by session mode, and Knockout resolves to 2. These are gameplay-setting values, not a capacity proof. For the ordinary totals, the per-lap consumers request indices 0–1, 0–3, or 0–7 respectively; the separate storage and live-index caveats remain in [lap-count admission and per-lap storage audit](lap-storage-capacity-audit.md).

## Boundary of this result

- The menu-to-global binding is direct in descriptor data, but the generic event code that mutates `006fd4b0` was not isolated to a specific keyboard/button instruction. The installed menu also does not list numeric choices as literal rows.
- The selector decoder is permissive: every low WORD other than 0 or 1 produces 8. No broader input-domain claim follows from the ordinary menu choices.
- The direct writer census includes other sources, including a full DWORD supplied by `-LAPS` and a zero-extended network byte. Those sources are not constrained by this menu's 2/4/8 map and are outside the ordinary menu domain.
- The roster builders run after frontend normalization, but other supplied, network, playback, alias, or later writers may change the value. The existing producer and storage reports retain those open ordering/admission limits.

Evidence anchors (all shipped-artifact observations are from the selected hash above): reconciler assembly `ev_285a099508860107d38925d9640e24127b50e756019ed23bc7c61fedcca79c56`; encoder/decoder assembly `ev_26f1a0d89fb2004889f96d186d2dc966f4969c92701d8abf36e8c802cf72a4de` / `ev_3221a837a52919551eb3965a14d1df1942a2be88967d71f583dba65782a9e0db`; selector xrefs `ev_0b499f1c9c5bec24bdcaf71c4a30bc2a4afb191ddef7a8c0fe5d7c85ee8b3d68`; descriptor bytes `ev_5b5033d719667a340dec5783c24ecdc24fe4edee0abcafc4333b5f6a49a88daf`; menu-mode availability bytes `ev_371c5ae0aa67b20332305fb21fba1897029cc9370d9b5aa852cc7e58fb8892ad`; roster dispatcher assembly `ev_de3e65f7d404ded9bd5dea65d0935cec7442a7750494e475b475aa8a05cb053b`; and mode-one/mode-two assembly `ev_a636938a7cf812e36ba270e973dfb1d389684b95755e262200ffd91204cd3655` / `ev_7a65a2310a93252c263168e82acdc670667aa3f6e212a7880036d215e116b074`. Direct lap-count writer references are corroborated by `ev_11ba71c6832c72392ee314652e47f16b03153c626440854635f331d01640c5a9` and summarized in [lap-count producer boundaries](lap-count-producers.md).
