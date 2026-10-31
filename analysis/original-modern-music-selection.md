# Original versus Modern: music selection state and continuation

## Evidence boundary

Static comparison of the supplied original/backup and official Modern v1.6.1, whose fingerprints are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_music_selection_difference.py`. The [manifest](evidence/audits/original-modern-music-selection.json) retains matched contextual policy, original race selector, new Modern race/menu helpers, menu tables and direct caller witnesses. No game/audio/RNG/instruction probes were executed.

## Original race choice versus Modern stored progression

Original `0040ffd0` reads setting `006fbbe4`. Values 3..12 dispatch through a table to fixed results 0,1,2,3 or 8. Outside that range it calls random helper `004e0d88`, divides by 5 and returns the unsigned remainder (`00410013..00410026`). This is a per-call random-source path; no distribution, seed quality or complete no-repeat behavior is established here.

Modern replaces that caller's selection work with helper **`0040fefc`**, which updates stored track `005525f8` and style `00552854`. For ordinary settings 0..15:

| Setting | Track-state update | Style-state update |
|---|---|---|
| 0 | Copy `006fd4ac` directly | Toggle zero/nonzero via SETE |
| 1 | Copy `006fd4ac` directly | Set 0 |
| 2 | Copy `006fd4ac` directly | Set 1 |
| 3..12 | `(setting-3)>>1`, with result 4 remapped to 8 | Set 1 for even setting, 0 for odd |
| 13 | Increment stored track; unsigned values >4 become 0; result 4 becomes 8 | Toggle |
| 14 | Same increment/remap | Set 0 |
| 15 | Same increment/remap | Set 1 |

The progression's normal track sequence is **0,1,2,3,8,0**, depending on its prior value. Invalid settings/states are not normalized by a general range check; the table above is deliberately scoped. Settings 0..2 copy another global rather than incrementing here, so this helper alone does not explain every advertised random race mode.

Direct calls are retained at **`00410426`** and race-loading call `004a3489`. The latter demonstrates a loading-sequence update, not proof of exactly one advance per completed race. Source/initialization of `006fd4ac` and all caller cadence remain pending.

## Modern menu subset cycles

New helper `0040ffb4` reads menu setting `006fbbec`:

| Setting | Accepted track-ID mask | Set IDs |
|---:|---:|---|
| 0 | `00be` | 1,2,3,4,5,7 |
| 1 | `0034` | 2,4,5 |
| 2 | `008a` | 1,3,7 |
| ≥3, ordinary values | No cycle | Return setting−2 |

For modes 0..2, it reads cursor `005525fc`, resets unsigned cursor ≥6 to zero, reads ID from table **`[1,2,3,4,7,5]`**, increments the cursor and tests the selected mask. It repeats until an accepted ID is found, stores the next cursor and returns that ID. Each mask intersects the fixed table, so the shown normal masks have an accepted element. This is cyclic subset selection, not a fresh random draw on every call.

Seed helper `0040ff9c` calls `005177cc` with EAX=20, indexes a 20-byte mapping at `0040ff88` and writes the resulting cursor to `005525fc`. Direct call `004b5d30` establishes a seed-initialization site; the RNG helper's full range/distribution contract is not reconstructed here. Main music routine calls the cycle helper at `0041060b` before storing its result at `0055258c`.

The two subsets support the mechanism behind **MP153-004**'s additional menu modes. Track names, tempo labels and menu-label-to-setting mapping still require assets/string consumers. Do not assign “Fast” and “Slow” to a numeric mask from the bit pattern alone.

## Contextual policy now checks whether playback can continue

Original **`004103a0`** treats nonzero EDX as an unconditional route through `004109d0` and `004104f0` with operation EAX=22, level `[006fbbe8]`, EBX=0, then sets byte `00552591=1`. Its zero-EDX branch either keeps an existing flagged state or performs this route, except settings 3..12 take a separate race-specific selection route using the original helper.

Modern's nonzero-EDX branch first compares the configured menu selection with current ID `[0055258c]`. For subset modes 0..2 it uses the same masks above, rejects unsigned current IDs above 7 and tests membership. For a fixed setting it compares setting−2 directly with the current ID. A match reaches a continuation gate: if `[005525a0]` is nonzero and byte `[00552591]` is nonzero, return without the restart call sequence. A mismatch, or failed continuation gate, invokes the operation-22 route and marks that byte 1.

Its zero-EDX path retains the setting-range distinction. Values 3..12 call `004109d0`, then new selection helper `0040fefc`, then `004104f0` with EAX=0, level `[006fbbf0]`, EBX=1, and clear the state byte. Other values reach the continuation/restart gate.

These are observable call and state rules. The full meanings of the backend operations and state globals are not proved here; “continue” denotes skipping that restart sequence, not proof of uninterrupted audible playback. Modern uses PUSHAD/POPAD, so a decompiler must not infer an ordinary return value from intermediate EAX values.

## Catalog conclusions and unknowns

- **MP153-004:** subset masks and cycling are statically supported; menu labels, asset tempo and actual playback remain unverified.
- **MP153-005:** stored race progression is supported for modes 13..15, but other modes use `006fd4ac`; exactly one new track per race and complete advertised playlist behavior remain partial.
- **MP153-003:** added numeric selection/style handling exists, but Rock/Techno asset and UI mapping remain unresolved.
- Volume fixes (**MP153-001**) and double-fade prevention (**MP153-006**) are not established by this selection analysis. They require backend/caller comparisons rather than assuming all audio claims follow from changed policy bytes.

The [start/volume comparison](original-modern-music-start.md) now traces original menu randomization removal and verifies retained stop/start/level/fade bodies; this narrows the unresolved volume claims. Further work: track assets/names, setting serialization/labels, progression producers, all call cadence and volume/fade helper semantics. Original `0040fefc` is inside unrelated code, so it must not be treated as the old version of Modern's new helper merely because addresses coincide.

## Original random range versus ten stem entries: genre claim still unresolved

A separate Luna 6 read-only review identified a useful follow-up to **MP153-002**. The parent verified the original selector, downstream builder instructions and table bytes directly; the expanded audit now retains the original ten-entry stem table at **`005525a8`** and both style-token strings.

| Raw table indexes | Stem strings |
|---|---|
| 0..3 | `home`, `lost`, `atla`, `alpi` |
| 4..7 | `home`, `lost`, `atla`, `alpi` again |
| 8..9 | `empr`, `chuck` |

As established above, the original `0040ffd0` RNG branch returns only0..4, whereas its fixed-setting branch can return8. A raw RNG return cannot directly name table slots5..9, including the distinct final stems. But duplicate stems and the separately selected style mean a table slot cannot be equated with a genre or unique song from this observation alone.

The retained builder at `0041065a` compares its current operation/selection value signed against10. Its table-index source then depends on setting `006fbbe4`: either stored `005525f8` or the saved incoming EAX value at local+286h. Later `004106b8..004106cd` selects `tech` (`005368e0`) only when `00552854 == 1` and earlier restriction flags permit it; otherwise it uses `rock` (`005368d8`). Thus genre/style is a distinct control decision, not established as indexes0..4 versus5..9.

The selector's return range is proven; **a complete random-mode-to-table/style path and the vendor's specific “last Rock and all Techno” explanation are not**. In particular, the existence of a ten-entry table and a modulo-five helper does not by itself prove a defect, its reachability or the advertised fix. The catalog claim is left vendor-claimed with this related evidence linked rather than promoted on that inference.

Next: follow the two original direct selector callers (`00410132`, `0041042f`), map the race-music list's ordinary settings to their labels, establish all style-state producers and resulting filenames, and compare the corresponding Modern paths. Then inspect actual assets before assigning individual stems to song/genre names. No new audio, RNG or instruction probes were executed; no Ghidra changes were made.
