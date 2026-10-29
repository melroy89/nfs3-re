# Series result tie, status and ordering policy

## Scope and conclusion

Static review of the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. This report covers ordinary valid snapshot rows in the result builder, comparator, filtered lookup and mode-specific normalizer. It does not establish an online tournament result or cross-peer deterministic ordering.

For score sort keys, equal scores are resolved first by snapshot category bit `+0x200 & 0x04`, then by signed `+0x238`. In normal direction, bit4 clear sorts before bit4 set; reversing the configured direction reverses that category preference. The final `+0x238` comparison remains ascending after that direction inversion. In ordinary mode1 point awarding, the ranking map is explicitly sorted by ascending `+0x238`, so lower values receive earlier award slots. Exact equality on the last key returns comparator equality: no identity-based final discriminator is present in this comparator.

The producer supports treating `+0x238` as a finish-time estimate/order scalar, not as a participant identity or series score. `InitializeRaceLapEstimates` (`004ce5a0`) computes it from clock-like `+0x228`, progress `+0x224`, track segment count `005dd940`, and configured lap count `006fd4b4`, then adds a correction for missing per-lap values. The formula's physical unit is unresolved. Knockout normalization (`004552f0`) later overwrites selected snapshot `+0x238` values as ordering buckets and assigns a separate sequential rank at `+0x2bc`.

## Comparator's score ties

`00455840` dispatches the selector in `00559618`; `0055961c == 1` reverses the comparator result before return. The switch table at `00455810` maps selectors 3 and 4 to score comparisons:

- Selector 3 performs an unaligned DWORD load from `006fd42c + 2*identity`, arithmetic-shifts it right 16, and therefore compares the signed WORD at `006fd42e + 2*identity`. Mode1 progression writes the round award from table `00454f10` into that WORD at `004550bd` and accumulates the score into WORD `006fd44e + 2*identity` at `004550d0`.
- Selector 4 performs the same unaligned DWORD load/shift on `006fd44c + 2*identity`, comparing signed WORD `006fd44e + 2*identity`.

When those WORD scores tie, the comparator checks each row's byte `+0x200` bit `0x04` (selector3 at `00455b05..00455b3b`, selector4 at `00455a3c..00455a72`). If exactly one row has bit4 set, the unset row compares earlier in normal direction. This is a category marker, not an explicit disconnect or abandoned-race test. The result filter used by `004cf000` also uses `+0x200` bit4 to select its human-category rows; that use does not assign broader semantics to the flag.

After the direction inversion at `00455bb5..00455bc0`, a zero comparison proceeds to the shared `+0x238` fallback at `00455bc4..00455bf8`. Its signed comparisons return negative when the first row's value is smaller, so smaller `+0x238` sorts first. Because the fallback executes after the direction inversion, reversing the primary score/category ordering does not reverse this final tie-break. Selector 1 itself uses `+0x238` as its primary key, so its direction does apply to that primary comparison. Float selector2 uses its own primary metric at `+0x2b8`; this report limits the tie policy to ordinary valid result rows.

The implementation therefore has a two-level score tie rule:

1. Score key (selector 3 per-round award or selector 4 cumulative score), then category bit4.
2. If those are equal, signed `+0x238` ascending, regardless of primary direction.

If all compared values are equal, the comparator returns zero. It does not compare participant identity afterward.

## Meaning and mode-specific rewriting of +0x238

The live result path gives `+0x238` a time/order role:

- The completion/progress routine stores global clock value `007d3684` into vehicle `+0x228` and initially copies it to `+0x238` (`004ce408..004ce435`, plus the alternate branch at `004ce50a..004ce51f`). One completion branch adjusts `+0x238` by subtracting `0x200` (`004ce4c7..004ce4cd`).
- For records that need lap estimates, `004ce5a0` checks `+0x224` and `+0x228`, then stores a quotient at `+0x238` (`004ce5ab..004ce5f1`): `((+0x228 - 0x200) * DWORD[005dd940] * DWORD[006fd4b4]) / +0x224`. Here `005dd940` is the track segment count. The callback sets completed progress `+0x224` to lap count times segment count in its finish branch (`004ce4b2..004ce4d3`), so the estimate reduces to an adjusted clock value for that completed-progress case. Other progress values produce an extrapolated ordering estimate. Missing per-lap values can adjust the estimate further (`004ce5f7..004ce6b3`).

These instructions use 32-bit signed `IMUL` results followed by signed `IDIV`; they support “adjusted finish-time estimate/order scalar” but do not establish ticks-per-second or wall-clock units. When a per-lap timing slot is missing, the correction at `004ce646..004ce69e` advances shared PRNG state at `00554f10/00554f18` and adds a pseudo-random increment to `+0x238` and the missing lap value. Nor do these instructions prove that every row's `+0x238` came from the same path before the snapshot copy.

The mode2-only prepass of `004552f0` changes category0 snapshots with `+0x200` bit `0x80` to state2 (`+0x2c4 = 2`). The common path beginning at `00455340`, also reached by other modes, then uses `00455cd0` and status filters to rewrite `+0x238` for state2 and state4 rows, based on an existing sorted value plus `0x3c`; it rebuilds the map and assigns sequential order values at `+0x2bc`. Thus the common normalizer turns `+0x238` into an ordering bucket for selected status rows; this rewrite is not exclusive to mode2. This bit80/state2 operation is distinct from comparator tie bit4.

`00455cd0` selects a valid row through the 16-slot category map, or scans that map for the requested matching index when a filter is nonzero. `004557b0` implements the status/category filters: filter `0x08` requires row bit4, `0x02` requires bit4 clear, `0x10` requires the specified `+0x2c4` state, and `0x20` requires a different state. These are row-selection predicates; they do not inspect transport connectivity.

## Ordinary score and incomplete-result gates

Mode1 updater `00455070` sets category0, selector1, and normal direction before traversing the sorted map. It applies per-round awards by sorted index and adds them to cumulative score WORDs, then rebuilds selector1 in reverse direction (descending `+0x238`) for its stored order words and increments the mode1 progression counter. The second map is not a cumulative-score sort: `004550f1` passes EDX=1, and EBX=1 supplies reversal at `004550f7`. Before doing so it calls `004cef80`; if that helper reports an unsuppressed state1 result, the updater returns without awards or progression. Existing state-producer notes show state1 can be written by pause/exit finalization and network-menu exit/synchronization paths. That evidence supports an unfinished/termination gate on this path, but it does not prove state1 means a dropped network connection or a user-abandoned race in every case.

Mode2 updater `00455140` does not use that early state1 gate. It uses the sorted category0 results, requires more than one row before the initial elimination, marks the selected row state2, then updates mode2 eligibility/order. The normalizer's explicit state2 source is bit80, and the elimination updater's state2 source is the selected row. Neither routine tests a socket/peer connection state.

Accordingly, the static result logic supports these bounded statements:

- Mode1 scoring/progression can be suppressed by the existing state1 query unless its suppression flag disables that query.
- Mode2 identifies selected/eliminated or bit80 rows through numeric state2 and adjusts their result ordering; no direct disconnection predicate is present in the comparator or normalizer.
- “Abandoned” and “disconnected” are not established meanings for these numeric states. A transport drop may influence other state producers, but that mapping was not proved here.

## Peer agreement limit

The result builder runs the state exchange before copying local snapshots. Type12 participant-state packets copy the vehicle range `+0x224..+0x2e3`, which includes `+0x238` and `+0x2c4`, but excludes the local participant/descriptor pointer at `+0x220` and does not directly carry the global cumulative-score arrays. A packet can therefore carry the already-populated `+0x238` value, including any prior correction, but this alone does not prove the same value was produced, sent, or consumed by every peer in the same order. The comparator indexes score WORDs by identity obtained through the local `+0x220` pointer. Matching row order across peers therefore cannot be inferred from the local comparator alone. The existing network result ownership audit also finds no host-only gate around progression and no transmitted authoritative final standings table. Cross-peer identity, clock agreement and complete-series synchronization remain unverified.

## Evidence and reproduction

Artifact: `/home/melroy/.local/share/winegui/prefixes/NFS3/dosdevices/c:/Program Files/Electronic Arts/Need For Speed III/nfs3.exe`, SHA-256 as above. The comparator bytes at `00455840` were inspected directly with objdump because the current ephemeral REA FunctionManager does not contain that entry; the prior detailed audit and parent review identify it as the installed comparator. Other REA evidence: mode2 normalizer `ev_29522d6b2d10b78162e8c36c00c486d9f57464f81adde968ba623c754f0867c6`; filtered lookup assembly `ev_0afc54d4560459ff6aa051d4b49c631303f6acd5acaaf48454dd1dde0a8e6656`; predicate `ev_c2759f84c0d40784b04f69ac23b2eb7002ec9d782b053afd7dbdc334c87212fc`; map builder `ev_ec1500510b65536446cd14510b53e7351d4cb9f6eece1ffcaf4d9f371f0dbf1d`; mode1 score updater `ev_7507651e05ed98cce79ccccdb5cef58f6e00d6e5747796a6c40f1320dbc10a46`; mode2 updater `ev_baebf150c69e0d049c9f8eee973fb545d2aa9542f92f07d25811657fa30ad8cd`; lap estimate initializer `ev_c048ae0d021a040550040d841e224f94ec0b55f22a126a6dd084a3c59d8be479`.

Bounded disassembly used:

```sh
objdump -d -M intel --start-address=0x00455810 --stop-address=0x00455c02 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x00455070 --stop-address=0x00455140 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004552f0 --stop-address=0x00455403 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004ce280 --stop-address=0x004ce596 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004ce5a0 --stop-address=0x004ce74c '<selected nfs3.exe>'
```

Static analysis only. No runtime result, network session or executable/configuration change was made. The REA session was closed.
