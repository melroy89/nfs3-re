# Standard menu controls: official assets versus local backups

**MP140-018 is partially supported by package evidence.** The official v1.6.1 menu definitions for Connect Players, Connect IPX and View Car Interior explicitly contain Options and Exit buttons absent from the corresponding uppercase local backups. This establishes an asset difference; actual runtime selection and introduction in v1.4.0 are not proven.

## Source identity and inventory

The [inventory script](scripts/inventory_official_menu_routes.py) checks the retained official archive SHA-256 `c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3`, inventories **52** extracted `.mnu` files, and compares each file hash to the corresponding archive member read directly with `7z x -so`. Every file has an uppercase counterpart in the local `fedata_org/menus` backup. **Zero of these 52 pairs are byte-identical.** That does not mean every button or semantic field differs: whitespace, ordering, comments and unrelated fields can change the file hash.

The [retained JSON inventory](evidence/inventories/official-menu-routes.json) records file paths, lengths, hashes, exact-match results, button section line numbers and selected routing fields for all 52 pairs. Uppercase backup names do not authenticate original retail provenance. These are neither original source files nor proof that every supplied-original installation used these assets.

## Three release-note targets

| Official menu | Added control definitions relative to selected backup | Relevant details |
|---|---|---|
| `connect.mnu` | Options `LR1of2`; Exit `LR2of2` | Options uses `text=kMenuMAINOptions001`, `nextmenu=options`, `codelink=escape`. Exit uses `text=kMenuSETUPExitGame001`, `codelink=exitprogram`. |
| `ipx.mnu` | Options `LR1of2`; Exit `LR2of2` | Same selected label/routing/type fields as the Connect pair. |
| `interior.mnu` | Race `LR1of3`; Options `LR2of3`; Exit `LR3of3` | Race uses `codelink=racenow`, `text=kMenuMAINRACE001`; Options uses `nextmenu=options`, `text=kMenuMAINOptions001`; Exit uses `codelink=exitprogram`, `text=kMenuMAINExitGame001`. |

The script asserts presence of Options and Exit in all three official files, and their absence in the three selected backups. It ignores commented-out lines and retains section boundaries. It is an inventory of the authored fields, not a full emulation of the game's menu parser; duplicate-key and lexical edge cases have not been qualified against the original parser.

## Code connection and reconstruction scope

The [setup-button comparison](original-modern-setup-website.md#generic-options-transition-retained-code-changed-asset-route) verifies the generic button handler and relevant transition ranges are byte-identical in original and Modern. A simple button with no overriding callback and a non-null `nextmenu` can return action 5; the loop then conditionally resolves a loaded descriptor. `exitprogram` and `racenow` are separate recognized commands with distinct action/state handling. The authored `escape` token is recorded here without claiming that its complete Escape-key admission/priority has been traced for these menus.

A reconstruction needs both the menu assets and generic routing machinery. The observed added controls do not themselves require three bespoke new C callback implementations. Entry initialization can still alter visibility, callbacks or selection; actual selected files, initialized fields, multiplayer state and rendered output remain untested.

Related release entries **MP140-019** (controls persist when Options opens from race results) and **MP140-020** (Race hidden when Options opens from the first screen) describe lifecycle policy, not merely these asset definitions. They remain separate from this finding. Reuse the [Race Now policy audit](original-modern-race-now.md), then map the entry contexts and global writers before promoting either claim. Do not infer these dynamic behaviours from the presence of the controls alone.

## Follow-up

1. Confirm actual runtime selection of these external files versus fallback/resource definitions.
2. Map menu initialization overrides and Escape routing for the three contexts.
3. Inspect historical v1.4.0 assets to verify release attribution; authenticate original assets if a universal original-versus-patch asset claim is needed.
4. Validate controls and return navigation in a suitable game session, separately from static comparison.

Reproduce: extract `fedata/menus/*` from the pinned retained archive into `analysis/captures/modern-differences/upstream/package`, then run `python3 analysis/scripts/inventory_official_menu_routes.py`. Target binaries, saved Ghidra state, raw exports and maintained reconstruction are unchanged. No game or instruction probes were run.

## Controller reset button: authored position7→8

The focused [controller-reset asset audit](evidence/audits/controller-reset-asset.json), reproduced by `python3 analysis/scripts/audit_controller_reset_asset.py`, reads `fedata/menus/control1.mnu` directly from the hash-pinned official archive and compares the uppercase local backup **`fedata_org/menus/CONTROL1.MNU`**. Each has one `[button]` with text token **`kMenuCONTROL1ResetToD001`**, `codelink=reset` and `buttontype=tab`.

The backup specifies **`ypos=7`**, official Modern **`ypos=8`**. Both retain x0/y0, priority11, listpos0/listoff0 and align0 for this control. The preceding Predefined control remains `ypos=6` and links `hardkeys` in the inspected files. The reset change is therefore authored tab-position metadata, not a change from literal screen y7 to y8 pixels.

This gives partial asset evidence for **MP140-027**, the reported one-position downward shift. It does not authenticate the backup as original retail, prove which asset is selected at runtime, establish parser defaults for omitted legacy fields or verify the rendered result. The text token and reset binding remain associated; full reset callback semantics and layout interpretation are separate investigations. No settings were reset and no menu was opened.
