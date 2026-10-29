# Car selector gameplay domain

## Scope and evidence

This read-only pass distinguishes the four pointer groups rebuilt for race setup from the player-car settings and selector masks used by the frontend. The active installed `nfs3.exe` SHA-256 is `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. REA evidence was collected from that binary; the owned REA session was closed. Installed-data counts come from the existing read-only [car selector inventory](evidence/inventories/installed-car-selector-categories.json), reproducible with [inventory_car_selector_categories.py](scripts/inventory_car_selector_categories.py). No executable, configuration, live process, or persistent Ghidra project was changed.

## Four pointer groups are one combined pool plus three category pools

`RebuildEligibleCarModelGroups` (`0043a580`, body `0043a580..0043a6a2`, evidence `ev_aac71dfc964cebef039c74e62a1eacbc839982c1a0e821928621fe87c6eb265b`) clears `0x320` bytes at `005552d8` and four DWORD counts at `005555f8`. The entries occupy four `0xc8`-byte regions, so each region holds 50 pointers:

| Group index | Pointer region | Appended candidates | Capacity |
|---:|---|---|---:|
| 0 | `005552d8` | Combined pool: every model accepted by the group eligibility check | 50 pointers |
| 1 | `005553a0` | FEDATA selector value 0 | 50 pointers |
| 2 | `00555468` | FEDATA selector value 1 | 50 pointers |
| 3 | `00555530` | FEDATA selector value 2 | 50 pointers |

For each accepted model, the builder reads the model’s selector at `+0x388`, adds one, appends the pointer to that category group, and separately appends the pointer to group 0 (`0043a5c8..a626`). Thus these are not four disjoint 50-model categories and do not provide 200 distinct model slots. Group 0 is the combined pool; each category pool contains a duplicate pointer subset. The maximum distinct model domain represented by these arrays is the combined-group count, subject to the builder’s scan and eligibility rules.

`GetEligibleCarModelIndexFromGroup` (`0043a6b0..a6de`, evidence `ev_6e9df38a0daf885ef2b8e5249008779ad75760e2459bfee4866dc5eae27f80c7`) computes `base + groupIndex*0xc8 + ordinal*4`, reads that group pointer, adds `0x31c` to reach its identifier, and resolves that identifier to a registry ordinal. This is the category-to-registry-index conversion, not a player-menu row conversion.

## Ordinary race setup uses the groups for opponent model choice

`RunRaceSession` (`004a3690`) calls `PrepareRaceSetupAndBuildRoster` (`00474ca0`) on the normal setup path (`004a36f3`). The setup helper rebuilds the groups at `00474cb3`, resets setup-use counters at `00474cb8`, then dispatches the selected roster builder by race mode (`00474cd4..cf5`). The direct caller evidence is `ev_91b44d82c462c291ceeb29784ae306cbf70a577b9e28b209faf13512ad16a99b` and `ev_415a979ffb3494b75503bdcb765baec8350ac93a8bcf50b9d8aea01cfeca2b22`.

`SelectOpponentCarModel` (`004734d0..3540`, evidence `ev_a92c2ddc40cce999027e8bee9ac1d332c3711e9dea7f173de837419c1eaef3c9`) uses `g_nOpponentCarSelection` (`006fd4d4`) to choose its source. Values 0–3 index the corresponding group count, select an ordinal within that group, and call `GetEligibleCarModelIndexFromGroup`; values at least 4 take the explicit-model path and return selector minus 4. The group paths update setup-option usage counters afterward. This establishes the four groups as opponent-roster pools, including the combined pool at selector 0.

The player-one and player-two settings instead hold direct model indices in `006fd2bc` and `006fd328`. The installed frontend view resolver `ResolveFrontendCarViewModelSelection` (`00453500`) maps `car1` and `car2` to those values directly; `InitializeHumanRaceParticipant` consumes the corresponding model index from the settings records. `ReconcileRaceSetupMenuConstraints` (`0044be60`) calls `ApplyCarSelectionEligibilityMask` (`0043a6e0`) to update separate WORD eligibility tables beginning at `0055500a` (models) and `0055519a` (opponents). These are distinct from the four pointer groups. Exact visible-menu selection event dispatch is not required to explain the opponent group lookup and remains outside this pass.

## Installed cars matching the direct group eligibility path

The loader maps FEDATA source words into the model record’s `+0x380` flag byte: source `+6` sets bit `0x01`, source `+8` low WORD sets `0x02`, source `+0x0e` sets `0x04`, source `+0x10` sets `0x10`, and source `+0x14` sets `0x40` (`DiscoverAndLoadCarModelRegistry`, `0043a0ea..a171`, evidence `ev_727a98977efd96d434c96b443076fb5784cd6e53cf81d8e31192cea6dea348b1`). The selector is the signed high WORD of source DWORD `+8`, stored at record `+0x388`.

`CheckCarModelOpponentEligibility` (`0043a4f0..a578`, evidence `ev_a5a45393d6031b5f554c1d3226fe67bfc3db32ea6a2ef68ceae4c6277f0f10b8`) has a direct accepted path in non-mode-3 operation when bit `0x10` and bit `0x04` are clear, `CheckBuiltinCarIdentifier` succeeds, bit `0x01` is clear, and bit `0x40` is set. The built-in check (`00439620..9653`, evidence `ev_460e16b36eb019ceeaf2de2a12960adfddbedac4614343ddaef7dfe93d1c6e5a`) requires identifier DWORD 0 to be below `0x32` and identifier bytes `+4..+0x0f` to be zero. Mode 3 has an additional rejection when record bit `0x20` is set.

Applying the non-mode-3 direct-path predicate to each installed model’s recognized-language FEDATA rows produces nine matching models, three per ordinary category:

| FEDATA selector | Group | Installed models matching the direct predicate | Count |
|---:|---:|---|---:|
| 0 | 1 | DIAB, FM50, SCIG | 3 |
| 1 | 2 | CORV, COUT, F355 | 3 |
| 2 | 3 | AMD7, JXK8, SL60 | 3 |
| — | 0 combined | All nine above | 9 |

The inventory covers 58 car archives, 139 recognized-language FEDATA members, and 24 model directories. The recognized rows agree across each model’s present languages. The remaining installed entries do not all fail the entire routine: after an earlier bit-`0x10` or mode-3 bit-`0x20` rejection, the routine returns false; other failures can reach the selected-human fallback. That fallback admits a model matching the current player-car index when the global selector state permits it (at most the player-one selection for state 0, either player selection for state 1, and neither for other positive states). Accordingly, nine is the static installed-data count matching the direct path, not a claim that every race has exactly nine current group entries.

The builder scans `GetCarModelCount() - DWORD[00554f50]` ordinals; the selected image initializes that DWORD to1 and the direct xref inventory contains two reads, with no direct writer. Under that unchanged adjustment it scans count-minus-one ordinals, and the installed directory inventory is not proof that all 24 records are successfully admitted or identifies the omitted final post-ordering ordinal. The exact runtime combined-group count can therefore be lower than nine if an otherwise matching model is the omitted ordinal or fails an earlier loader gate. The installed selector value 255 (KNOC) is outside ordinary selector values 0–2 and is not included in the counts above. No runtime group contents or visible menu state were observed.

## Capacity interpretation

For an ordinary loaded registry whose candidates all pass the static group check, each of the four regions has independent capacity 50, but group 0 is the aggregate ceiling on distinct accepted models. The three category counts are subsets and can overlap only through their duplicate representation in group 0. The installed-data direct-path set is nine models (three per category), well below 50; the selected-human fallback and exact final scanned ordinal make active counts state- and registry-dependent. This report does not treat the 200 pointer cells as 200 selectable cars or infer a runtime-loaded total from the asset inventory.
