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

The progression's normal track sequence is **0,1,2,3,8,0**, depending on its prior value. Invalid settings/states are not normalized by a general range check; the table above is deliberately scoped. Settings0..2 copy the selected circuit index rather than incrementing the playlist: these are the three track-default choices, not the Random modes13..15. The `tracks` descriptor at `005563fc` names selection storage `006fd4ac`; race initialization also passes this same value to track-scene loading.

Direct calls are retained at **`00410426`** and race-loading call `004a3489`. The latter demonstrates a loading-sequence update, not proof of exactly one advance per completed race. The selected-circuit descriptor and the fuller initialization/seed evidence below resolve that source’s role; all application-level caller cadence remains pending.

## Modern menu subset cycles

New helper `0040ffb4` reads menu setting `006fbbec`:

| Setting | Accepted track-ID mask | Set IDs |
|---:|---:|---|
| 0 | `00be` | 1,2,3,4,5,7 |
| 1 | `0034` | 2,4,5 |
| 2 | `008a` | 1,3,7 |
| ≥3, ordinary values | No cycle | Return setting−2 |

For modes 0..2, it reads cursor `005525fc`, resets unsigned cursor ≥6 to zero, reads ID from table **`[1,2,3,4,7,5]`**, increments the cursor and tests the selected mask. It repeats until an accepted ID is found, stores the next cursor and returns that ID. Each mask intersects the fixed table, so the shown normal masks have an accepted element. This is cyclic subset selection, not a fresh random draw on every call.

Seed helper `0040ff9c` calls `005177cc` with EAX=20, indexes a 20-byte mapping at `0040ff88` and writes the resulting cursor to `005525fc`. Direct call `004b5d30` establishes a seed-initialization site. The RNG helper’s bounded return rule is now retained below; seed quality and distribution are not established. Main music routine calls the cycle helper at `0041060b` before storing its result at `0055258c`.

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
- **MP153-005:** stored race progression is supported for modes 13..15, track-default modes use the selected circuit; update placement and seeding are verified below, while exactly one advance per race and complete advertised playlist behavior remain partial.
- **MP153-003:** the race list names three Random modes and matches the helper’s style rules; asset coverage and actual playback remain unverified.
- Volume fixes (**MP153-001**) and double-fade prevention (**MP153-006**) have separate partial static support in the [start/volume and audio-exit comparison](original-modern-music-start.md): removal of circuit-dependent level subtraction and Race/Exit suppression of an extra menu restart. These findings do not follow from selection bytes alone, and audible results remain untested.

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

## Modern playlist seeding and race-load update placement

New helper **`0040fed0..0040fefa`** initializes `005525f8` from `005177cc(5)`, remapping result4 to8, then initializes style `00552854` from `005177cc(2)`. Direct caller **`004b5d35`** follows menu-cursor seeding at `004b5d30`; the retained caller witness starts at instruction `004b5d21`. This establishes the two calls' local order, not the number of times the entire application reaches initialization.

The retained RNG chain **`0051778c..005177de`** establishes the bounded calls without executing them:

- `0051778c`: update unsigned state `007a32b4 = (old * 0x343fd + 0x269ec3) mod 2^32`, return the updated 32-bit value.
- `005177ac`: call that update, then return its upper16 bits by logical shift16.
- `005177cc`: preserve incoming ECX/EDX, save incoming EAX as divisor, call `005177ac`, unsigned DIV by the saved divisor, and return the remainder in EAX.

For positive divisors5,2,20 used here, return ranges are therefore0..4,0..1,0..19. Zero would fault rather than return a value. This is a range and state-transition contract; no claim of uniform independent samples or a particular startup seed follows. The game’s unsigned wrapping arithmetic must remain explicit in a C reconstruction.

The full Modern **`InitializeRaceSession` envelope `004a33f0..004a354b`** now replaces the earlier five-byte call-only witness. After a first abort poll at `004a3470` returns zero, the routine calls `004a3558`, emits a progress update and calls the selector **once at `004a3489` on this shown straight-line path**. It then polls again at `004a348e`. A nonzero result branches to the abort presentation at `004a3532`; a later nonzero track-scene loader result at `004a34c7` also branches there. The selected circuit is loaded from `006fd4ac` at `004a34bd` and passed to `004dbbe0` at `004a34c2`.

Consequently, Random modes13..15 advance before successful scene loading is known; a later abort/failure has no direct rollback of `005525f8` or `00552854` in this caller. The branch calls the [pending-overlay renderer](original-modern-pending-overlay.md), waits through `004df8e0` with EAX=200 and returns1; it is not itself session shutdown. A failed attempt that reaches the selector can therefore advance the state at that point; proving its persistent effect after outer shutdown requires the remaining callees. Fixed choices3..12 can also reach the selector through contextual routine `004103a0`, where they assign deterministic values rather than increment. This distinction explains why direct-call counts alone cannot establish one playlist advance per completed race. Remaining work is outer loading/retry cadence, cleanup effects and all indirect calls, followed by any separately authorized playback validation.

## Outer session comparison: removed style toggle and excluded rollback state

The audit now retains the complete shared address envelope **`004a3690..004a38bc`** in both executables. Its byte comparison finds exactly two changed regions:

| Region, end exclusive | Original | Modern |
|---|---|---|
| `004a36c6..004a36e1` | Test `00552854`; zero becomes1, nonzero becomes0 | `JMP 004a36e1`, followed by25 NOP bytes |
| `004a36f9..004a36fb` | Call displacement bytes for `004a3400` | Call displacement bytes for `004a33f0` |

All other bytes in this envelope match, including the settings snapshot, abort-result handling and failure restore. Original EDX is set to0 before `004e0dee`; that helper’s full body `004e0dee..004e0e2b` is byte-identical in both baselines and contains only EAX additions, six direct state stores and RET, preserving EDX. Thus the old block is a verified zero/nonzero toggle. Modern clearly bypasses the entire old toggle block. Combined with the new selector’s mode0/13 toggle, this identifies a relocation of style policy rather than two simultaneous outer/inner toggles.

At **`004a36a2..004a36c1`**, both versions copy **0x83c DWORDs = 0x20f0 bytes** from `006fbb40` to the stack. After the initializer, `CWDE` sign-extends AX at `004a36fd`, stores the result into abort flag `0055e88c`, and tests it. On nonzero, both versions call `004a35d0` with EAX=1 and then restore that same snapshot at `004a3721`. Its address interval is **`[006fbb40,006fdc30)`**: it includes the music-choice settings and selected circuit, but excludes playlist index **`005525f8`** and style **`00552854`**. The explicit rollback copy therefore cannot restore those two globals.

The full Modern shutdown body **`004a35d0..004a3681`** is retained as context. It uses PUSHAD/POPAD and invokes several graphics/scene/session helpers; it contains no direct store to either playlist global. That is a bounded direct-store observation, not proof of their preservation through every callee, callback or alias. Original shutdown has a different body and is not assumed semantically equivalent because its address matches. There is no need to finish every renderer shutdown investigation to retain the verified snapshot boundary.

There is one direct initializer call in the compared outer routine, at `004a36f8`. This proves one call on a path reaching that site, not one invocation per user-visible completed race: session entry/retry orchestration and indirect effects remain open. A reconstruction should preserve the original-versus-Modern toggle placement and snapshot exclusion as separate policy decisions, and must not silently add playlist rollback as a purported cleanup fix.

## Override wrappers follow the shifted fixed-choice index

The full same-address wrappers `00410460..004104a1` (65 bytes) and `004104b0..004104ee` (62 bytes), exclusive ends, each contain exactly one differing byte: `00410479` and `004104cf`, respectively. Both change the comparison against menu-setting DWORD `006fbbec` from **6 to 8**. Reproduce with [the wrapper audit](scripts/audit_small_wrapper_differences.py); its [manifest](evidence/audits/small-wrapper-differences.json) pins the executable identities and complete spans.

This preserves the fixed-choice exception for track ID 6, Monster: the documented original list has one random choice before its fixed titles, while Modern has three. The internal selected-track comparison at `0041047c` remains against `0055258c == 6`; that internal ID does not shift to 8.

The begin wrapper sets `00552594=1` before its checks. It skips its stop/start sequence when the menu setting is the exceptional value (old 6, Modern 8), or when selected internal track `0055258c` is 6. Otherwise it calls `004109d0`, then `004104f0` with EAX=24, EDX=`006fbbe8`, EBX=0. The end wrapper acts only when `00552594` is nonzero, clears that flag, and skips its sequence for the exceptional menu setting. Otherwise it calls the same stop helper and start routine with EAX=22, the same level source and EBX=0.

**Bounded work status: done; evidence: verified static instructions and list correspondence.** This is a setting-index adjustment, not evidence of a new audio backend or measured playback behavior. The saved names containing “ShowSix” must not be interpreted as meaning that the Modern menu index is still six. Original language-resource provenance retains the limitation stated above.

## Race-setup reconciliation stops rewriting a tune-dependent global

The complete same-address setup function `0044be60..0044c2ce` (1,134 bytes, exclusive end), saved as `ReconcileRaceSetupMenuConstraints`, differs only within `0044bea4..0044bec1`. [The focused audit](scripts/audit_race_setup_music_coupling.py) verifies both pinned executable hashes and exact original/Modern block bytes; [its manifest](evidence/audits/race-setup-music-coupling.json) records full hashes and disassembly locations.

Original computes and stores the Boolean:

`DWORD [006fbbd8] = (DWORD [006fbbe4] == 0 ? 1 : 0)`

It also loads EDI from `006fbc00` before continuing at `0044bec1`. Modern retains that EDI load at the block's beginning, jumps directly to `0044bec1`, and NOP-fills 21 bytes. The assignment to `006fbbd8` is absent from this local route; every other byte of the complete function is identical.

The race tune descriptor `tunenames` already establishes `006fbbe4` as its selector, as documented above. However, the full semantic role of destination `006fbbd8` is **not established by this assignment alone**. This finding should not be labelled “music mute removed” or “a specific option unlocked” without tracing that destination's readers and other writers. Nor does omission of this local store prove the destination retains its value through all later calls.

The Modern saved body union contains 1,113 bytes and five changed in-body bytes; it excludes the 21-byte NOP gap. This audit includes the removed original decision/store instructions. A reconstruction should keep this version-specific state coupling separate from generic menu constraints and preserve the chosen global's initialization/lifetime contract. Incidental EAX/flags also differ on reaching the common continuation; full machine-state equivalence is not assumed.

**Bounded work status: done for the complete function's byte differences; confidence: verified static assignment and existing source-selector evidence.** Required follow-up is destination-state semantics, all writer/consumer paths and actual menu/audio behavior. No game or instruction probes, Ghidra writes or maintained-C edits were performed.

## Direct RNG-call census: music separates from the retained shared generator

The [RNG callsite audit](scripts/audit_rng_callsite_difference.py) regenerates GNU objdump disassembly from both hash-pinned executable files, validates each selected direct CALL's E8 displacement against the PE bytes, and retains the [complete address lists](evidence/audits/rng-callsite-difference.json). This is a decoded direct-call census, not an invocation-frequency or whole-program reachability measurement.

The complete shared generator/seed envelope `004e0d88..004e0e2b` is byte-identical. Original has **194 decoded direct CALL sites** to `004e0d88`; Modern has **191**, all at addresses present in the original list. Exactly three original sites are absent from the Modern list:

| Original site | Original music use | Final-pair interpretation |
|---|---|---|
| `0041001a` | Selector `0040ffd0` calls shared generator and uses unsigned remainder modulo 5. | Modern's separately mapped selection/playlist policy replaces this original selector route. |
| `0041016f` | Setting 11 branch takes unsigned remainder modulo 100; residues 0..50 store style 1, 51..99 style 0. | The original exceptional randomized-style branch is absent from the rewritten loader; Modern fixed-setting parity policy is documented above. Residue counts are not a probability proof. |
| `0041058f` | Menu setting 0 takes remainder modulo 7, adds 1, remaps result 6 to 2, and stores the byte cursor. | The [music-start report](original-modern-music-start.md) maps Modern menu selection and startup; this old per-call draw is no longer a direct consumer of the shared generator. |

Modern's bounded LCG wrapper `005177cc` has three decoded direct callers: `0040fed7`, `0040feed` and `0040ffa1`, in the already documented race/style initialization and weighted menu-cursor initialization. Its state at `007a32b4` is distinct from the retained shared six-DWORD state `005644e0..005644f4`. This establishes an additional kind of change beyond track ranges: these inspected music routes no longer advance the old shared state through their original direct calls, while the old generator remains available to other subsystems.

The [vehicle-dispatch report](original-modern-vehicle-dispatch.md#7-shared-rng-algorithm-retained-consumption-can-change) independently establishes shared render consumers and retained initial bytes. Changed consumption can alter later shared values under matching seeds and differing call histories; the census does not identify a physical simulation dependency or demonstrate replay/multiplayer desynchronization. Other gates and indirect calls can change execution frequency even at the 191 unchanged direct sites. Linear disassembly can also miss alternate boundaries or decode embedded data; no target instruction was executed.

**Bounded status: done for complete decoded direct-call lists and generator/seed identity. Confidence: verified static within the declared decoding scope.** Original and Modern do not need a same-address counterpart for each new RNG wrapper: the evidence here is a changed music dependency on two distinct generators, not a claimed one-for-one replacement of every old RNG consumer. Complete seed order, synchronization, indirect consumers and observed random trajectories remain unresolved.

### Startup seed source is the clock result

The expanded [RNG audit](scripts/audit_rng_callsite_difference.py) verifies the only decoded direct caller of Modern seed setter `00517784`: application startup calls it at `004a3e02`, immediately after `CALL 004f2790` at `004a3dfd`. There are no intervening instructions. Clock helper `004f2790..004f279b` preserves ECX/EDX, calls IAT `00534664`, restores those registers and returns EAX. The manifest resolves that import as **WINMM.dll `timeGetTime`**. Setter `00517784..0051778a` writes EAX directly to DWORD `007a32b4` and returns.

Thus on this startup path the LCG seed is the clock API's raw 32-bit return, without local mixing, masking or an explicit fixed seed. The [clock-source comparison](original-modern-clock-source.md) explains the broader timer replacement; the seed provenance here follows the actual return-value flow rather than inferring it from a nearby timer call. Same captured clock value and same subsequent LCG call sequence yield the same LCG sequence mathematically; neither condition is guaranteed across launches.

**Status: startup seed source verified statically.** Actual seed values, invocation count, clock quality, indirect writes/reseeding and cross-thread ordering remain untested. This does not change the separate shared generator's state or establish gameplay/replay dependence on the music LCG. The earlier “no particular startup seed” limitation concerns the actual numeric seed and remains valid; its source is now identified.
