# Opponent-model menu domain

## Scope and target

This read-only audit follows the ordinary `opponent.mnu` car droplist, its list descriptor, the registry-built label/eligibility arrays, and the downstream opponent selector. The inspected active executable is `nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. The installed menu file is `FEDATA/MENUS/opponent.mnu`, SHA-256 `83aad629e611f452f64067dde3834738a4a4bc0e615a6a5a754520c71b344626`. Installed `FEDATA/TEXT/text.eng` and `fedata_org/text/text.eng` are byte-identical, SHA-256 `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`.

REA used an ephemeral Ghidra session on the active executable; that session was closed. No executable, configuration, runtime, or persistent Ghidra state was changed. This report does not treat installed car directories as the loaded registry.

## The visible droplist is `opcars`

The installed `opponent.mnu` declares a `[droplist]` at `(101,69)` with `listname=opcars`, `maxvisitem=10`, `invert=0`, and `flip=0`. `maxvisitem=10` is the visible-window setting; it is not the total option count. The separate `oppnumber` list controls opponent count (`None`, `One`, `Full Grid`) and is not this model/class selector.

The executable descriptor at `00556514` contains, in order:

| Field | Address/value | Meaning supported by code |
|---|---|---|
| `+0x00` | pointer `00537eac` → `"opcars"` | list-name key |
| `+0x04` | pointer `00555130` | WORD label-ID array; populated by the car registry loader |
| `+0x08` | pointer `0055519a` | WORD eligibility array; populated by the loader and later car-selection reconciliation |
| `+0x0c` | pointer `00555204` | per-row color/style DWORD array; loader writes its default and disabled sentinel |
| `+0x10` | pointer `006fd4d4` | `g_nOpponentCarSelection`, the selected value associated with this list |

Raw descriptor-byte evidence is `ev_0dcc9ed3a1dbe1f39ac3a7471eea299740de8c740ba1cf1e34116f379065e005`. The exact descriptor pointer fields are data, so the ordinary list framework's indirect lookup is not represented by a direct xref to each field.

## Fixed rows and registry-derived rows

At the end of `DiscoverAndLoadCarModelRegistry` (`00439d90`), instructions `0043a34f..a394` seed the first four label IDs and their default colors:

| List index / selector value | Text ID | Installed English text |
|---:|---:|---|
| 0 | `0xc1` | `None` |
| 1 | `0xbe` | `Class A` |
| 2 | `0xbf` | `Class B` |
| 3 | `0xc0` | `Class C` |

These are the four group selectors, not four specific car models. `SelectOpponentCarModel` (`004734d0..3540`, existing evidence `ev_a92c2ddc40cce999027e8bee9ac1d332c3711e9dea7f173de837419c1eaef3c9`) dispatches selector values `0..3` to the corresponding pool; group 0 is the combined pool, and groups 1..3 are category pools. The English text `None` therefore labels the no-category/combined selector row in this menu; it does not mean “zero opponents.”

The same loader obtains the full linked-registry count `C` and scans model ordinals from zero (`0043a399..a405`). Let `P` be the first ordinal in `[0,C)` whose record flag byte at `+0x380` has bit `0x10` set; if none does, let `P=C`. The branch at `0043a3b4..a3b6` jumps directly to `0043a407` on the first set bit, so this is a **prefix scan**, not a sparse scan that resumes after flagged models. For every ordinal `i` with `0<=i<P`, it:

1. writes label ID `0x7bd+i` at `00555138+2*i`;
2. seeds its eligibility WORD to 1 at `005551a2+2*i` (the first four WORDs precede this at `0055519a`);
3. seeds its style DWORD at `00555214+4*i` to `0xff649dfd`;
4. calls `00439c10` on the record; if that predicate returns nonzero, clears the eligibility WORD and writes disabled sentinel `0x908080` to the style cell.

At the first bit-`0x10` model the loader exits label generation immediately; it does not label that model or inspect later ordinals in this pass. It writes a zero WORD label terminator at `00555138+2*P` (`0043a407..a410`). Thus the model-label array produced by this pass contains exactly the contiguous registry prefix `0..P-1`, followed by its terminator. Exact instructions are in `ev_727a98977efd96d434c96b443076fb5784cd6e53cf81d8e31192cea6dea348b1`; the full loader dossier is `ev_4431190816e1db03f35cb301a915c529fc86eed7b990db0366cbf730de6085cb`.

Consequently model ordinal `i` in the scanned prefix maps to list index/selector `i+4`, without compacting or renumbering registry indices. The producer's label array contains `4+P` rows (four fixed rows plus ordinals `0..P-1`), then the zero terminator. The number enabled at a particular frontend state can be lower because the eligibility table is also affected by `00439c10` and later `ApplyCarSelectionEligibilityMask` reconciliation. The selected installation inventory has 24 model directories, but this is not evidence that all 24 were admitted or that they form the loaded `C`.

The registry reorder evidence summarized in the [car selector domain report](car-selector-gameplay-domain.md) places ordinary records with bit `0x10` clear in an earlier partition than records with bit `0x10` set. That ordering is consistent with this prefix termination defining the ordinary model-list boundary. Exact `P` still depends on the records actually admitted and their final order; the directory inventory alone does not establish it.

This loader seeds and terminates the label array, but the reviewed body does not clear the entire label, eligibility, or style arrays before rebuilding the prefix. Cells beyond the newly written terminator can therefore retain prior contents after a shorter subsequent build. Whether the frontend list reader stops at the new zero terminator, and whether any other normal refresh rewrites the trailing eligibility/style cells, was not established here; this report does not treat stale tail cells as visible choices.

The model label IDs are dynamically resolved by `004d17b0` (`ev_ee467523fccb1faf52eba3649f57bc617e80625ce89fef66a43eb161a16b550e`). IDs `0x7bd..0x7ee` map back to model ordinals `0..49`. The resolver consults the registry and returns the model-record `+0x10` string in its ordinary branch; its special branch can select localized IDs `0x1e3` (“(Bonus Pursuit)”) or `0x1e4` (“(Bonus)”). The record lookup behavior used by that path is in `00439250` (`ev_fbd2619ecbdbc47f39648e61b84fa7eec3fe931ee8c30d1bfd3d2bc7408e7f57`). Thus the model rows are tied to registry ordinals and metadata-backed labels; they are not the pool selector labels.

## Selector meaning and bounds

The menu descriptor associates the list with `g_nOpponentCarSelection` at `006fd4d4`. The frontend helper `ResolveFrontendCarViewModelSelection` (`00453500`) treats a selection greater than 3 as explicit and computes `selection-4` for the preview model; values at or below 3 use the first player-car selection. `SelectOpponentCarModel` has the corresponding grouped/explicit split: 0..3 selects a group, while values at least 4 produce model ordinal `selection-4`.

At the menu producer level, each populated prefix row `i` corresponds to explicit selector `i+4`; the generated model-selector interval is therefore `4..P+3` when `P>0` (empty model suffix when `P=0`). The actual selectable explicit set can be smaller because `00439c10` and later reconciliation may clear rows. The installed menu's ten-row viewport does not further cap total list cardinality.

The prefix boundary is separate from race setup's group/eligibility arithmetic. The existing [car selector domain report](car-selector-gameplay-domain.md) establishes that group rebuilding and the opponent eligibility mask use `N=C-1`. If a bit-`0x10` record occurs before ordinal `C-1`, the menu label prefix stops before that record; if no such record occurs, this label producer reaches `P=C`, one model ordinal beyond the `N` model rows in that separate logical mask domain. This pass establishes the menu producer's prefix formula and the ordinary keyboard selection writer, but does **not** establish the active registry order or exact `P`. The mouse commit path remains unresolved, so this report does not claim every generated row can be committed by every ordinary input method.

## Ordinary droplist dispatch and selected-value write

The menu item type table at `00557a84` associates type key `29` with the `"droplist"` type string at `00538378` and the `0xbc`-byte item template at `00556f0c`. `00449060` selects a template by that type key and copies its 47 DWORDs into the menu item's record at `00604ee0 + index*0xbc`. In the droplist template, the callback slots are populated as follows: `+0x30 = 00463ff0`, `+0x34 = 00464560`, and `+0x2c = 004634d0`. This identifies the class-specific droplist handlers; it is distinct from the generic type-5 button handler `00461270`.

The droplist keyboard/event callback `00463ff0` reads the list name from entry `+0x64`, then calls `00442c80` and `00442bf0`. The first supplies the descriptor's options array (`descriptor+4`) and selected-value pointer (`descriptor+0x10`); the second supplies eligibility (`descriptor+8`). On ordinary left/right key events (`BX=0x4b00` / `0x4d00`), it advances or decrements the selected index, wraps over the option range, skips rows whose eligibility WORD is zero, and stores the resulting index through the selected-value pointer. Enter (`BX=0x0d`) opens a closed list and seeds its selection; an accepted Enter while open validates the selected row and writes the index through that pointer (`00464294..0046429d`). Thus the installed droplist class has a concrete ordinary keyboard route to the descriptor's selected global, including the `opcars` descriptor and `006fd4d4`.

## Remaining mouse-input boundary

The generic coordinate-row helper `SelectFrontendListRowFromCoordinate` (`00465ca0`) writes a row WORD at its incoming record+0x40 and conditionally invokes that record+0x44. This does not by itself identify the record as the `opcars` droplist. The droplist template has `004634d0` at+0x2c, while its+0x44 field is initially zero. Matching the helper's+0x44 to the template's+0x2c would require an additional rebasing or initialization proof, which is absent. The exact mouse-release store therefore remains open; the keyboard route above does not depend on that assumption.

The downstream race selector uses `g_nOpponentCarSelection` as a group-or-explicit selector but does not locally clamp the explicit branch. This report is limited to normal menu assets and static producer semantics; it does not test malformed data, arbitrary global values, runtime menu interaction, or peer-supplied settings.
