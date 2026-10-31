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

The `menutunes` descriptor at **`00556bf4`** selects `006fbbec`. Original list pointer `0055633e` contains IDs466..473: Random followed by seven titles. Modern pointer `00556336` contains IDs1946,1944,1945 followed by467..473. Decoding the hash-pinned official English resource gives modes0 **Random (All)**,1 **Random (Fast)**,2 **Random (Slow)**. The names therefore come from resource/list correspondence, not an inference from mask bits. Original IDs are decoded with the Modern language resource; original language provenance remains unverified.

| Internal ID | Fixed-choice title | Modern subset membership |
|---:|---|---|
| 1 | Whacked | All, Slow |
| 2 | Romulus 3 | All, Fast |
| 3 | Minotaur | All, Slow |
| 4 | Pi | All, Fast |
| 5 | Triton | All, Fast |
| 6 | Monster | None |
| 7 | Whipped | All, Slow |

The table follows the Modern fixed-setting return rule `setting−2` and the list's title IDs467..473. In particular, the mode labelled “All” excludes ID6 from both its mask and cycle table, despite a fixed choice for Monster. This is a verified selector boundary, not proof that the omission is erroneous or that the track could otherwise be played in every context. Actual musical tempo and audible playback remain untested.

## Contextual policy now checks whether playback can continue

Original **`004103a0`** treats nonzero EDX as an unconditional route through `004109d0` and `004104f0` with operation EAX=22, level `[006fbbe8]`, EBX=0, then sets byte `00552591=1`. Its zero-EDX branch either keeps an existing flagged state or performs this route, except settings 3..12 take a separate race-specific selection route using the original helper.

Modern's nonzero-EDX branch first compares the configured menu selection with current ID `[0055258c]`. For subset modes 0..2 it uses the same masks above, rejects unsigned current IDs above 7 and tests membership. For a fixed setting it compares setting−2 directly with the current ID. A match reaches a continuation gate: if `[005525a0]` is nonzero and byte `[00552591]` is nonzero, return without the restart call sequence. A mismatch, or failed continuation gate, invokes the operation-22 route and marks that byte 1.

Its zero-EDX path retains the setting-range distinction. Values 3..12 call `004109d0`, then new selection helper `0040fefc`, then `004104f0` with EAX=0, level `[006fbbf0]`, EBX=1, and clear the state byte. Other values reach the continuation/restart gate.

These are observable call and state rules. The full meanings of the backend operations and state globals are not proved here; “continue” denotes skipping that restart sequence, not proof of uninterrupted audible playback. Modern uses PUSHAD/POPAD, so a decompiler must not infer an ordinary return value from intermediate EAX values.

## Catalog conclusions and unknowns

- **MP153-004:** subset masks, cycling and Fast/Slow list labels are statically supported; musical tempo and actual playback remain unverified.
- **MP153-005:** stored race progression is supported for modes 13..15, but other modes use `006fd4ac`; exactly one new track per race and complete advertised playlist behavior remain partial.
- **MP153-003:** the race list names three Random modes and matches the helper’s style rules; asset coverage and actual playback remain unverified.
- Volume fixes (**MP153-001**) and double-fade prevention (**MP153-006**) are not established by this selection analysis. They require backend/caller comparisons rather than assuming all audio claims follow from changed policy bytes.

The [start/volume comparison](original-modern-music-start.md) now traces original menu randomization removal and verifies retained stop/start/level/fade bodies; this narrows the unresolved volume claims. Further work: track assets/names, setting serialization/labels, progression producers, all call cadence and volume/fade helper semantics. Original `0040fefc` is inside unrelated code, so it must not be treated as the old version of Modern's new helper merely because addresses coincide.

## Original random range versus ten stem entries: bounded genre-path evidence

A separate Luna 6 read-only review identified a useful follow-up to **MP153-002**. The parent verified the original selector, downstream builder instructions and table bytes directly; the expanded audit now retains the original ten-entry stem table at **`005525a8`** and both style-token strings.

| Raw table indexes | Stem strings |
|---|---|
| 0..3 | `home`, `lost`, `atla`, `alpi` |
| 4..7 | `home`, `lost`, `atla`, `alpi` again |
| 8..9 | `empr`, `chuck` |

As established above, the original `0040ffd0` RNG branch returns only0..4, whereas its fixed-setting branch can return8. A raw RNG return cannot directly name table slots5..9, including the distinct final stems. But duplicate stems and the separately selected style mean a table slot cannot be equated with a genre or unique song from this observation alone.

The retained builder at `0041065a` compares its current operation/selection value signed against10. Its table-index source then depends on setting `006fbbe4`: either stored `005525f8` or the saved incoming EAX value at local+286h. Later `004106b8..004106cd` selects `tech` (`005368e0`) only when `00552854 == 1` and earlier restriction flags permit it; otherwise it uses `rock` (`005368d8`). Thus genre/style is a distinct control decision, not established as indexes0..4 versus5..9.

The race list now resolves the setting ambiguity. Its descriptor at **`00556be0`** is named `tunenames` and selects storage **`006fbbe4`**. Original list pointer **`00556320`** has 14 zero-terminated WORD IDs; Modern pointer **`00556314`** has 16. The audit retains every ID and decodes it with the hash-pinned official Modern English resource. This is not authentication of the original retail language file.

| Ordinal | Original label ID / official English decoding | Modern label ID / decoding |
|---:|---|---|
| 0 | 463 / Track default (Rock) | 465 / Track default (Rock or Techno) |
| 1 | 464 / Track default (Techno) | 463 / Track default (Rock) |
| 2 | 465 / Track default (Rock or Techno) | 464 / Track default (Techno) |
| 3..12 | IDs162..171, ten individual titles | Same IDs in the same order |
| 13 | 172 / Random | 1943 / Random (Rock or Techno) |
| 14 | Absent | 1941 / Random (Rock) |
| 15 | Absent | 1942 / Random (Techno) |

The complete original loader envelope **`00410030..00410329`** is now retained. Subject to its entry gates, settings >=3 reach the selector call at **`00410132`**, use its return directly to index `005525a8`, and store that index in `005525f8`. For setting13 the selector therefore supplies only0..4: `home`, `lost`, `atla`, `alpi`, or duplicate `home`; it cannot supply `empr` at8.

At **`00410163`**, however, the loader compares the setting with **11**, not13. Only11 calls the RNG for style selection: unsigned remainder modulo100 <=50 sets `00552854=1`, otherwise0. No probability claim follows without a verified RNG contract. Other settings use parity: odd sets0, even sets1. Setting13 thus sets0, and the later suffix gate **`004101a8..004101ec`** chooses **`rock.mus`** (`00536898`); style1 would choose **`tech.mus`** (`005368a4`). Restriction flags can force Rock, so they do not restore Techno on this path. Setting11's special branch also differs from the ordinary fixed-title parity rule; whether other callers overwrite that choice remains a separate question.

**Bounded conclusion:** on this original loader path, the list's Random setting excludes the distinct `empr` stem and selects no `tech.mus` suffix. This is code-level support for part of **MP153-002**, rather than merely a modulo/table-size inference. Modern's previously retained helper explicitly gives Random modes13..15 the five-stem progression0,1,2,3,8 and respective toggle/Rock/Techno state rules. The new list labels corroborate **MP153-003**'s three mode names. The statement that exactly the “last Rock” and every Techno song were ignored across all original playback routes still requires asset-to-title mapping and caller coverage; no audible result was tested.

Next: inspect actual track assets to associate stems/styles with the ten individual title IDs, follow all playback routes and progression producers, and establish caller cadence. Original UI ordinal serialization is not proven solely by the descriptor; the shared generic selector mechanism is documented in the [Frame Size setting analysis](original-modern-frame-setting.md), while this audit records the direct music-setting consumers. No new audio, RNG or instruction probes were executed; no Ghidra changes were made.

## Local asset availability and title correspondence

The read-only [asset inventory](evidence/inventories/local-music-assets.json), reproduced with `python3 analysis/scripts/inventory_music_assets.py`, records sizes, SHA256 hashes and first16 bytes for the supplied local `.MUS`, `.MAP` and `.LIN` files. Each of `home`, `lost`, `atla`, `alpi`, `empr` has both `rock` and `tech` triples present. These files have local-installation provenance only; this is not an original-versus-Modern asset delta or a playback/decode test.

The fixed original switch pairs settings3/4 with stem0 (`home`),5/6 with1 (`lost`),7/8 with2 (`atla`),9/10 with3 (`alpi`),11/12 with8 (`empr`). Together with the retained label IDs and ordinary style parity, this associates:

| Stem | Odd-setting title / Rock rule | Even-setting title / Techno rule |
|---|---|---|
| home | Little Sweaty Sow | Hydrus 606 |
| lost | Snorkeling Cactus Weasels | Cetus 808 |
| atla | Rear Flutterblast #19 | Aquilla 303 |
| alpi | Snow Bags | Knossos |
| empr | Flimsy | Warped |

This is a selector/list association, not identification by listening or embedded song metadata. Original setting11 has the exceptional randomized style branch documented above, so its loader route cannot simply be described as always selecting `EMPRROCK.MUS`. Modern's helper uses the ordinary parity rule for all fixed settings3..12. On the inspected original Random13 route, the missing distinct Rock stem is therefore the one associated with **Flimsy**, and all five available Techno filenames are excluded. Other callers, route reachability and actual playback still require qualification.
