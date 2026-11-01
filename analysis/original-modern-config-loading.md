# Original versus Modern: config.dat load acceptance and reset paths

## Evidence boundary

Static supplied-original/official-Modern comparison; exact executable identities are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_config_loading_difference.py`. The [manifest](evidence/audits/original-modern-config-loading.json) retains matched `00472980` bodies, original timestamp helpers, Modern header/sound-mode helpers, imported API identities and file-backed header bytes. No configuration file/API/game/instruction probes were executed.

This extends [resolution defaults](original-modern-resolution-defaults.md) and [ghost restoration](original-modern-ghost-loading.md). Configuration-header acceptance does not establish complete format compatibility.

## Retained file-load prefix, removed timestamp comparison

Both routines form a path with file-backed **`%sconfig.dat`** and prefix buffer `007a3034`, check the flag at `0055eb2e & 0x20`, check existence and request resource opening. They retain a local handle test and an exact **0x20f0-byte size comparison**. The flag is a load bypass in this path; its other producers/semantics are not inferred from an old command-line name.

Original additionally calls **`00472940`** when the size matches. It obtains time values for the config path and executable path (the latter from GetModuleFileNameA), then calls imported **CompareFileTime** with those two values. A return of -1 becomes helper result 1, which sends the caller to close/delete/reset; result zero allows the read path. The call, not a guessed function label, establishes this time-comparison gate.

Its time reader `004728e0` uses `_lopen`, GetFileTime's last-write output and `_lclose`, with a local zero-handle test and default time bytes. Complete failure semantics are not re-established here. In particular, do not promote this gate to a robust timestamp-validation mechanism without checking the legacy open/error contract.

Modern replaces the size-match timestamp call block with EAX=0 and a jump to the allocation/read path (`00472a22..00472a24`); mismatch still closes/deletes and goes to defaults. There is **no corresponding file-time check in this inspected Modern load path**. The old IAT address `0053448c` now names GetProcessHeap in Modern, so importing old API labels by address would be wrong.

Both allocate/read/copy/free in the remaining sequence. Their local caller does not branch on the read helper's return before copying; full allocation/read failure behavior and complete file-content validation remain outside this chapter.

## Modern header decision tree

After loading, Modern tests globals at `00472aac..00472aea`:

| Condition | Modern action |
|---|---|
| DWORD `006fbb40` differs from **0x20f0** | Call full defaults `00472404`, then header refresh and grouped default helpers |
| Size matches, byte `006fbb45` nonzero | Keep the existing block initially, then refresh header and grouped defaults |
| Size matches, high byte zero, byte `006fbb44` < **6** | Same grouped reset route |
| Size matches, high byte zero, low byte ≥ **6** | Call `00472230`, skip grouped defaults |

Grouped reset route calls header refresh `004723f0`, display defaults `00472d10`, HUD defaults `00485880`, `00472298` and `00472248`. Some fields outside these helpers may remain loaded on the version-only reset route. It is not automatically equivalent to a complete configuration reset.

The accepted version check is a **WORD interpreted as separate bytes**, not an exact DWORD equality against 6. Ordinary values 6..255 with zero high byte follow the accepted route; the code does not reject all unknown future versions. Higher header fields are not validated by these tests.

`00472230` only checks sound mode `006fbc00==3`; if capability helper `0040faf0` returns zero, it writes zero there. This is a narrow normalization step, not a full migration/validation of every serialized setting.

## Header producer and original reset behavior

Modern file-backed prefix `0055e8a0` contains bytes **`f0200000 06000000 00000000`**. `004723f0` copies those three DWORDs into `006fbb40`; effective values depend on any earlier source writes, which are not excluded here. This establishes the ordinary header template as size 0x20f0, next DWORD 6, then zero. **6 is not the Modern Patch release version.**

Original `004723f0` is a much larger defaults routine, not the same 18-byte header helper. Its file-backed bytes at `0055e8a0` are zero, so those source bytes must not be treated as a matching original template. Original load paths use the larger routine when no file opens or a size/time check fails, also set `0067900c`, and later compare loaded size and renderer type against current `007a3a58`. Modern replaces that sequence with the explicit size/version branching above.

This explains why the ghost wrapper's restored header matters: a ghost-supplied size/version prefix could otherwise route subsequent config loading into default initialization. It does not prove the exact contents or behavior of every original/patch-release ghost file.

## Remaining work

Verified: removed timestamp gate, retained size gate, Modern version-byte decisions and default-helper routing, and the header template/producer. Pending: all field layouts/packing, complete original default implementation, save-file semantics, read/open failures, source-template writes and cross-release compatibility. The [CPU](original-modern-cpu-tier.md), [HUD](original-modern-hud-layout.md) and resolution chapters explain selected reset consumers; they do not make this a complete serialization specification.

## View Angle reset versus accepted-header path

The [View Angle comparison](original-modern-projection.md#view-angle-option-list-and-release-note-correspondence) establishes that selector `006fbc40` changes meaning:0 selects fixed90 in original but Automatic in final Modern. It lies at offset`100h` from the inspected loaded-block destination `006fbb40`. This identifies a field location within the observed memory block, not a complete save-file layout or a proof that every read/copy succeeded.

The config audit now asserts the header decision bytes and direct display-default call. For matching size and version WORD`0006..00ff`, the header route calls the narrow sound normalizer `00472230` and jumps past grouped defaults. Neither that local decision nor the complete normalizer remaps View Angle. Rejected header versions enter grouped defaults; Modern `00472d9a` then explicitly writes selector0, as separately asserted by the projection audit. Size mismatch additionally invokes full defaults before those grouped helpers.

Thus the verified local policy is **accepted-header bypass versus explicit reset**, not an unconditional conversion of old Wide to new Normal. If a successfully copied block supplies ordinal0 and it survives later writes, final Modern interprets it as Automatic; ordinal1 retains the75-degree choice. This conditional consequence does not prove that an arbitrary original file reaches the accepted route, that no other helper migrates fields, or that a real user's setting changed. Full read/copy contracts, original header production, saved-format versions and later writers remain required before claiming cross-version configuration compatibility. No config file or game execution was used.

## Original header initialization narrows the migration example

The original prefix `004723f0..0047242c` sets up a zero-fill of the configuration block, then stores size`20f0` at `006fbb40`. Before the fill, EDI is set to `006fbb44` and ESI to `0055e8b8`. The captured fill adapter `004e0640..004e0658` and its complete nested fill code `004ff4c0..004ff563` do not modify ESI/EDI. Two MOVSD instructions at `0047242a/2b` then copy the eight template bytes into header+4/+8, assuming ordinary clear DF. The audit verifies that this original file-backed template is all zero. This is a different template location from final Modern's `0055e8a0`; treating the two as matching version6 producers would be incorrect.

With that template unmodified, this prefix therefore initializes version0. If such a header survives subsequent original initialization, saving and loading intact, Modern's verified decision tree takes the grouped-reset route, which explicitly selects Automatic FOV. It does **not** take the accepted-header bypass considered in the preceding conditional example. This materially limits that example: an original ordinal0 is not evidence of silent accepted-header reinterpretation unless its header also qualifies. The exact reset mechanism can still lead to Automatic, but for a different reason.

The prefix establishes neither every later original header write nor the contents of an actual saved file. Full original defaults, template mutation, save/read contracts and file provenance remain open. This finding is static instruction/data analysis; no config was created, loaded or modified and no new instruction probe was run.

## Save-entry policy: removed flag gate, added header refresh

The audit now compares complete `00472820..004728d3` (179 bytes) in both executables. All differences are confined to the13-byte region `0047282e..0047283b`; the initial14 bytes and remaining152 bytes are identical. Original tests byte `0055eb2e` against mask20h and skips to epilogue `004728ca` when set. Modern replaces that test/conditional jump with a call to its header refresh `004723f0` and eight NOPs.

This is a real policy difference: the inspected Modern save entry no longer honors that local flag as a bypass, and refreshes the three header DWORDs before its remaining admission checks. Those retained checks include nonzero `006fd3a0`, a disk-space request of`20f0` bytes, and nonzero `0055e88c`. They can still prevent writing. The header refresh nevertheless happens before them, so it can mutate memory even on a later no-save return. This is not an unconditional-save claim or proof that all callers ignore the flag.

The identical suffix copies the configuration block to a temporary buffer, clears temporary offset`1860h`, formats `%sconfig.dat`, requests writing through `004eeae0`, then frees the buffer. Equality of this sequence does not establish allocation/read/write success, external helper purity or complete serialized-field validation. In particular, Modern's earlier header refresh means equal copy instructions can copy different header contents. The ordinary template is size`20f0`, version6, third DWORD0; earlier template writes remain unexcluded. No save routine or file API was executed.

This narrows the migration story further: Modern actively stamps its header on this save entry, rather than relying solely on a first-load reset. The remainder of the original defaults routine and actual saved-file history remain separate unknowns; the prefix evidence above must not be promoted into a whole-lifetime version invariant.

## Removed save gate belongs to the original -msdemo flag

The [command-line audit](original-modern-command-line.md#table-contents-change-while-layout-remains) establishes that switch index21 sets bit21 of DWORD `0055eb2c`, equivalent to mask20h of byte `0055eb2e`. The config audit now independently pins slot21 at `0055eb88`: original points to literal `-msdemo`; final Modern points to an empty string. Thus the original save bypass described above has a concrete named-switch producer. Calling it a universal “disable saves” option would overstate its contract: the same bit has multiple consumers, and the name's intended demo-mode semantics are not inferred from its spelling.

The corresponding config-load prefix still checks this byte/mask in both executables. Final Modern therefore removes the named table switch and the inspected save-side gate while retaining a load-side bit consumer. These are three separate facts; the retained check is not proof that an ordinary named Modern command-line argument can set it, and the empty slot does not prove the bit is permanently zero. Alternate writes, empty-argument matching, external mutation and transitive policy remain outside the reviewed path. This distinction matters when reproducing the actual version's behavior rather than simply deleting all code associated with a removed switch.

## Sound-mode identity: D3D/EAX falls back to Stereo

The narrow normalizer now has a verified setting identity. Both descriptors at `00556c08` name `audiomode`, reference the same terminated choice list `00556364`, and store the ordinal at `006fbc00`. IDs155..158 decode in official final English as Stereo, Mono, Dolby Surround, D3D/EAX. Thus Modern `00472230` changes **D3D/EAX (3) to Stereo (0)** when `0040faf0` returns0; it leaves other mode ordinals alone in this body.

Complete capability helper `0040faf0..0040fb0f` is byte-identical between original and final Modern. It supplies EAX`ffffffff` to `004e21b0`, tests returned mask`20000h`, and returns normalized0/1. The audited mechanism is therefore a changed configuration consumer using a retained capability predicate, not evidence that the underlying audio provider itself was replaced. Backend flag production, refresh timing and actual device availability transitions remain unverified.

This supplies partial static support for MP153-010, whose wording describes a previously selected EAX mode becoming unavailable. The accepted-header route demonstrably reaches this normalizer; it is not merely an unused helper or a string match. The exact v1.5.3 introduction, all other callers, provider/device behavior, audible fallback and original retail label provenance remain open. No audio backend, device or game instructions were run.

### Capability predicate dispatches rather than returning a cached flag

The expanded audit compares complete `004e21b0..004e2221` (113 bytes), identical in both baselines. It lazily installs service pointer `00500c80` at `00a09b08` when zero, calls `004e1dd4`, obtains a value through `004eba70`, and pushes that value to indirect callback `009ef61c`. A zero value from `004eba70` first takes a diagnostic path; whether that diagnostic returns is not assumed universally. The callback result is ORed with`10000h` only when signed-positive, then returned through EAX; ECX/EDX are restored on ordinary return. The existing [capability preservation notes](detailed-analysis-notes.md#audio-capability-query-preservation-refinement) corroborate the register contract.

There is no cached capability-result return in this body: each normal invocation reaches the driver callback. That resolves the immediate cache question but does not prove the provider itself refreshes hardware state or that a device change is detected at a particular time. The service-pointer initialization and diagnostics also prevent treating this query as a proven pure function.

The outer `0040faf0` tests bit`20000h` without separately rejecting negative results. Since the query forwards nonpositive values unchanged, a hypothetical negative callback value containing that bit would satisfy the capability predicate. This is a conditional bit-contract limitation, not evidence that the driver returns such an error or that EAX is misdetected. Required follow-up is the resolved callback's result domain/lifecycle; actual provider testing remains separate. Preserve the bit test rather than silently replacing it with a signed-positive-success test during reconstruction.

## Executable-update deletion: config and both player specifications

The expanded audit now retains complete paired loader `004dc940..004dca4e` (270 bytes), filename builder `004dc800..004dc8af` (175 bytes), and deletion adapter `004e28a0..004e28bb`. This supplies a second caller of the original timestamp helper `00472940`, alongside the config caller already described. No settings file was read, deleted or rewritten during this inspection.

The player loader selects `player1` for input EAX0 and `player2` for EAX1 using file-backed strings `00549784`/`0054978c`; other values leave the local selection null and return. Other early checks remain before file handling. It builds the path, obtains the executable name with `GetModuleFileNameA`, and checks the target's existence through `004e0e60`.

| Existing-file path | Supplied original | Official Modern |
|---|---|---|
| Timestamp admission | `004dc9d5` calls `00472940` with specification/executable paths | Replaced by branch directly to read path `004dc9eb` |
| Timestamp helper returns nonzero | `004dc9e0` calls `004e28a0`, then enters default/rewrite route `004dca37` | This local deletion route is bypassed;30 NOP bytes occupy `004dc9cd..004dc9eb` |
| Other load/default/validation work | Surrounding paths retained | Same bytes outside changed envelope `004dc9c7..004dc9eb` in the complete loader |

The deletion adapter calls imported `KERNEL32.dll!DeleteFileA` through IAT `005344b0` in both binaries; this is API identity evidence rather than a guessed function name. Combined with the config load comparison, this gives bounded static support for MP100-045: the inspected timestamp-to-executable deletion gates are removed for config.dat and both selected player specifications. It does **not** promise files are never deleted or rewritten: missing-file handling, config size rejection, validation/default routes and I/O failures still exist. Actual update scenarios, file permissions, helper error contracts and precise first-release introduction remain untested.

The player filename builder changes independently. Original copies prefix `007a2fb4`, appends literal `carspecs\`, the selected player name, then `.spc`, into shared buffer `00564188`. Modern copies prefix `007a30b4`, skips the `carspecs\` append with `JMP 004dc85c` and37 NOPs, then appends name/extension. The audit verifies all other builder bytes identical. These buffers and unbounded string-copy loops imply shared scratch/length dependencies; reentrancy and arbitrary path safety are not established.

The final prefix producers are not traced here, so this builder change alone does not prove a root-directory location. Likewise, both config routines using `%sconfig.dat` with prefix `007a3034` does not establish what initializes that prefix. MP100-044's complete config relocation and MP100-046's driver-change reset policy therefore remain separate questions; neither is silently accepted from the timestamp finding.

The subsequent [versioned prefix audit](original-modern-startup-paths.md#config-path-history-root-relative-then-restored) now establishes final default prefixes and the1.1.0→1.2.0 config relocation reversal. This narrows the prefix limitation above for ordinary initialization; later mutation and actual I/O remain unverified.

## Renderer-type mismatch no longer requests the original startup reset

The audit now retains paired startup prefixes `004730d0..0047319a` and original saved-type producer `00472e70..00472e88`, alongside the complete config-load bodies. These tie an already observed loader comparison to a concrete graphics-defaults consumer.

Original defaults copy current DWORD `007a3a58` to saved configuration field `006fbc10` at `00472e72`/`00472e83`. On config loading, `00472ad1..00472ae9` compares those DWORDs and writes1 to `0067900c` when they differ. This is a renderer-type mask comparison, not a string comparison of DLL filenames or a complete graphics-device identity check. Same-type DLL changes need not differ under this predicate.

Later original startup performs this conditional chain at `0047316e..0047319a`: require `0055b03c != 0` and `0055e88c == 0`, call `00472fc0`, then test `0067900c`. A nonzero flag causes a store of the current EDX to that cell and a call to graphics defaults `00472d10`. The existing [default-initialization report](original-modern-resolution-defaults.md#original-default-path) documents resulting setting writes and resolution selection. The complete77-byte helper `00472fc0..0047300d` is now retained: it pushes EDX on entry and pops it before its ordinary RET. The caller loaded EDX from `0055e88c` and passed only its zero branch, so the later store clears the flag on ordinary return. Other config-failure paths also set the flag, so it is not exclusively a renderer-change indicator.

Modern's complete load body instead uses the size/version decisions documented above, without that saved/current renderer-type comparison. Its startup path calls `00472fc0` at `0047315b` under its own outer gate, then unconditionally jumps from `00473160` to `0047319a`; `00473162..0047319a` contains56 NOP bytes. It bypasses the original flag test/default call. This is control-flow evidence in the relevant caller, not merely noticing old bytes were overwritten.

Modern also repurposes `0067900c` as the INI `WindowedMode` setting, independently traced in [startup policy](original-modern-startup-policy.md#3-current-settings-exact-defaults-and-immediate-effects). Carrying the original reset-flag name or semantics onto that address would be incorrect. Its final graphics settings can still change through header/version reset, default initialization, mode selection and other paths; this comparison does not promise universal persistence.

MP100-046 gains **partial static support**: the specific original type-mismatch-to-startup-defaults route is removed. All renderer/device changes, later default callers, actual settings survival and v1.0.0 introduction remain unverified. No renderer was switched, no config was written and no target instructions were executed for this audit.

## Removed inline defaults at 00472566: replacement initialization matters

The [bounded default-block audit](scripts/audit_removed_default_block.py) pins
[complete removed bytes and the Modern sound helper](evidence/audits/removed-default-block.json).
It classifies the previously unrouted197-byte outside-function interval
`00472566..0047262b`. Every Modern byte there is NOP. Immediately before it,
original `00472561` calls `00472250`, whereas Modern jumps to `0047262b`.
That call is removed too; it is not part of the197-byte NOP interval.

| Original subrange | Inspected operation | Modern disposition |
|---|---|---|
| `00472566..004725be` | Conditional writes to six profile-header+18h cells, using EBX or literal1 according to `006fbb4c` | Old stores skipped; [HUD defaults](original-modern-hud-layout.md#3-header-default-changes-preserve-offsets-not-guessed-widget-names) separately initialize the headers |
| `004725be..00472611` | Inline audio default constants/selectors | Grouped reset calls sound helper `00472248..00472295` |
| `00472611..0047262b` | Calls `0040faf0`, stores sound mode3 on nonzero or0 otherwise | Modern sound helper retains this capability-dependent choice |

The complete retained capability predicate returns normalized0/1. This matters
because Modern subsequently writes small constants using MOV AL: here the
upper EAX bytes are known zero, rather than implicitly assumed so.

| Destination | Original inline default | Modern sound-helper default |
|---|---:|---:|
| `006fbbe8`, `006fbbf0`, `006fbbf4`, `006fbbf8` |100 |95 |
| `006fbbfc` |127 |108 |
| `006fbbe4` |2 |0 |
| `006fbbe0` |1 |1 |
| `006fbbec`, `006fbbdc` |0 |0 |
| `006fbc00` (audio mode) | Capability ?3:0 | Capability ?3:0 |
| `006fbbd8` |1 | No direct store in this helper |
| `006fd1d0` | No direct store in this block |83 |

These numbers are stored integers, not measured loudness or percentages.
The [frontend-sound comparison](original-modern-frontend-sound.md) establishes
`006fd1d0`'s new slider route; the [music policy](original-modern-music-start.md)
qualifies selection consumers. Missing stores in one block do not prove missing
initialization elsewhere. Modern's grouped reset route is documented above;
this local comparison is not a proof that every caller initializes all fields
or that saved settings are always reset.

**Status:** done for this removed interval's instruction roles, replacement
control transfer and compared sound defaults; verified static evidence.
The [original language mapper `00472250`](original-modern-language-table.md#removed-defaults-time-language-mapper-00472250) is now fully captured and its local contract verified. Full initializer register/data provenance, all
field identities, persistence and audible results remain separate follow-ups.
No game, audio API or instruction probe was executed; executable and saved
Ghidra bytes were preserved.

## Changed audio defaults have named slider bindings

The expanded [default-block evidence](evidence/audits/removed-default-block.json)
retains complete paired audio-menu initializer `00437e00..0043806b` and its
embedded tokens. The five binding regions below are byte-identical between
original and final; the initializer's only changed29-byte region is
`00437e42..00437e5f`, the separate [frontend-sound setup](original-modern-frontend-sound.md).
Thus these names come from code-bound controls, rather than guessing from
neighboring globals or preview sounds.

| Control token | Setting address | Original default | Modern default | Approximate normalized slider position, old→new |
|---|---|---:|---:|---|
| `ASLD_MENUMUSIC` | `006fbbe8` |100 |95 |78.7%→74.8% |
| `ASLD_RACEMUSIC` | `006fbbf0` |100 |95 |78.7%→74.8% |
| `ASLD_SOUNDFX` | `006fbbf4` |100 |95 |78.7%→74.8% |
| `ASLD_ENGINEVOLUME` | `006fbbf8` |100 |95 |78.7%→74.8% |
| `ASLD_SPEECHVOLUME` | `006fbbfc` |127 |108 |100%→85.0% |

The initializer obtains these controls by their tokens, loads their signed
integer settings with FILD, multiplies by binary64 constant `00537600`
(approximately1/127), and supplies the value to slider initialization.
For the sound-effects/engine controls, `00559234` selects between configured
values and separate live values `00552920/24`; the table describes the
configured-default branch. Fractions are arithmetic illustrations rounded to
one decimal, not rendered or executed slider observations. Existing
[slider callback evidence](original-modern-music-start.md#five-audio-slider-callbacks-remove-explicit-truncation)
separately establishes reverse conversion and changed rounding.

The selector change `006fbbe4:2→0` belongs to the independently verified
[`tunenames` race-music list](original-modern-music-selection.md#local-asset-availability-and-title-correspondence),
not an audio-volume field. Keep selector meaning and volume scaling separate.
No loudness, decibels, backend mixing law, successful audio output or universal
configuration-reset behavior is inferred from these stored defaults.
