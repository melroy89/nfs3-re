# Car and track source/metadata admission audit

## Scope and target

This pass consolidates the remaining source-admission boundaries relevant to car and track capacity. Static executable evidence is for the selected `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, analyzed with an ephemeral REA/Ghidra session. No executable, live process, or persistent Ghidra project was modified. Installed-data observations use the inventory scope and scripts cited below; they do not establish successful runtime loading.

## Car source admission

`DiscoverAndLoadCarModelRegistry` (`00439d90`) walks the installed car-model directory source and attempts each candidate independently. Its observed gates include directory/file discovery, duplicate-name rejection, FEDATA path construction or `car.VIV` fallback, successful opening of the required source/metadata handles, and a metadata type check. Candidates that fail these gates are skipped; later flag and mode predicates further restrict ordinary record admission. An accepted record is appended to the linked registry. The recount has no local 50-record cap, and the loader's later initialization loops use the full recount. The 50-entry bound belongs to the indexed model cache/getter, not this source admission path.

The analyzed body is non-contiguous (`00439d90..0043a20f`, `0043a25c..0043a4c1`). Its path construction and metadata-copy logic do not establish a metadata-file length or per-field extent check before the indexed metadata reads. The source accessors also use signed upper-bound-only ordinal checks; negative metadata ordinals are locally admissible, although this pass did not establish a reachable negative ordinal. These omissions do not prove malformed metadata is accepted: upstream file/container behavior and the required metadata type/field gates still determine admission. Fresh dossier: `ev_9b867458e70bf4fdacc9d68b3033a35c03ed974e226ae30d72c7ddbf894ef460`; prior complete loader dossier: `ev_d839de47b9f466a5fb4d8c17222972c3b5d2871735a13217dd6a704ff23d590c`.

### Installed category metadata

The reproducible installed-data inventory is [inventory_car_selector_categories.py](scripts/inventory_car_selector_categories.py), with retained output [installed-car-selector-categories.json](evidence/inventories/installed-car-selector-categories.json). It covers 58 `GAMEDATA/CARMODEL` VIV archives, 139 FEDATA members in the seven language suffixes recognized by the executable, and 24 model directories. Those are distinct bounds: 24 is the directory count in this selected installation, 139 includes language variants, and neither count is a runtime registry count.

FEDATA DWORD `+8` is arithmetic-shifted right 16 and stored as a signed category at model-record `+0x388` (`0043a171`). The ordinary group consumers use categories 0, 1, and 2; the group builder adds one for the category-specific array and separately appends to the combined group. The installed selector counts are 9, 7, and 7 for categories 0, 1, and 2, with one exceptional `KNOC` value of 255. Its category would become array index 256 if it reaches that builder. The executable applies eligibility predicates, and the built-in `KNOC` route fails its ordinary flag-40 test in the installed metadata; a selected-human fallback can still admit it under additional session/mode/role conditions. Thus 0..2 is the supported installed category domain for ordinary grouped selection, not a universal parser clamp or a proof that 255 is unreachable.

Even if a candidate passes source and metadata gates, registry append/recount remain uncapped locally. The subsequent 50-pointer getter/cache and four adjacent 50-pointer selector groups impose different storage constraints. The installed population does not prove that the loader must accept exactly 24 records, that custom/loose sources are excluded, or that a >50 list is reachable. Record, category-array, index-cache, selector-group, and saved-car capacities must remain separate.

## Track source and selector admission

There is no universal track selector range established by the inspected producers:

| Producer/source path | Observed admission behavior | Bound and remaining gap |
|---|---|---|
| Mode-one `.TRN` profile description | `PopulateTrnProfileDescription` extracts the signed high WORD from the DWORD at file offset `+0x18ca`, indexes the eight-DWORD map, then checks whether the mapped track ID is 0..7. Its caller validates the profile-browser row only. | The sufficient embedded ordinal domain is 0..7. It is not enforced before indexing. No `.trn` specimen exists in the active prefix, and loaded-block extent and lower-level validation are unverified. |
| Mode-one race roster | `BuildRaceModeOneRoster` indexes the eight-entry map using the high WORD of `006fd40a`; no local progression bound is present. | Eight mapped IDs (0..7) are the established table extent. Setup/progression admission upstream remains unresolved. |
| Mode-two track generator | The generator excludes two distinct IDs from0..7 and emits seven survivors from0..8 in ascending order; the seventh output (zero-based index6) is8. The later progression index is valid only for0..6. | Completed output IDs are within 0..8. The generation preconditions and downstream resource availability are separate. |
| Track menu | The ninth ordinal starts disabled with a placeholder; postgame/EMPIRE unlock replaces its token with `0x6e` and enables ordinal 8. | This enables a menu ordinal; it does not expand the separate eight-entry mode-one map. |
| Network setup | The supplied track DWORD/byte is copied into the shared selector without a local range normalization in the inspected initializer/handler. | No accepted selector domain is established by those copies. Packet unpacker admission and later resource/index checks remain open. |

The `.TRN` caller reconstruction and eight-entry map evidence are recorded in [detailed-analysis-notes.md](detailed-analysis-notes.md#shared-track-selector-and-eight-entry-series-map); the active-prefix search found no `.trn` samples, so no source-record extent or valid embedded ordinal can be confirmed from installed profiles. This is a bounded negative observation for that prefix, not proof that alternate profiles cannot be loaded.

Track geometry introduces another independent metadata boundary. The type-15 COLL initializer (`0041e370`) reads a WORD segment count at block `+6` and binds the records at `+8` without a local minimum-count or file-length check. The nine installed uppercase COLL files in the inventory all declare exact `8 + 36*N` block lengths within their respective files, with N from 959 to 1723. This establishes well-formed static extents for those files only. It does not validate custom or truncated files or demonstrate live loading. See [installed-track-map-segments.json](evidence/inventories/installed-track-map-segments.json) and [inventory_track_map_segments.py](scripts/inventory_track_map_segments.py).

## Findings and open gates

- **Supported static domains:** ordinary installed car category metadata 0..2; mode-one track map IDs 0..7; completed mode-two output IDs 0..8; installed COLL type-15 segment extents match their declared file sizes.
- **Observed missing local checks:** no 50-record cap at car registry append/recount; metadata accessors lack a negative-ordinal lower check; `.TRN` embedded ordinal is used before the mapped-ID check; the COLL initializer binds count/data without checking source extent; supplied network track selectors are copied without normalization at the inspected stores.
- **Not established:** actual acceptance of malformed FEDATA or `.TRN` metadata; custom/alternate source reachability; a maximum effective registry count; all array backing extents and lifecycle invariants; universal network selector admission; and live loader success.

These gates narrow the valid-domain questions but do not support a single car-capacity or track-capacity number. Any such number must name the specific source, consumer, and admission path.
