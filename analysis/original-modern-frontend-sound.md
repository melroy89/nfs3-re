# Original versus Modern: frontend sound volume and request throttling

## Evidence boundary

Static comparison of the supplied original/backup and official Modern v1.6.1, with exact hashes in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_frontend_sound_difference.py`. The [manifest](evidence/audits/original-modern-frontend-sound.json) retains paired sound routines, the unchanged record initializer and Modern slider/restore witnesses. No game, audio or instruction probes were executed.

## Changed caller contract at 004181d0

The retained archives date the dedicated volume source to 1.5.0. The
1.4.0 body calculates the request byte from EDX and `006fbbf4`.
All retained packages from 1.5.0 through 1.6.1 instead load `006fd1d0`
and mask AL with `0x7f` at `0041821c..00418223`. Between 1.5.1 and 1.5.2
the later request-mode checks are reorganized at `0041822a`: both
`006fbc00 == 2` and `005525a4 != 0` still reach the same mode-1
record writes, but 1.5.2 shares that block. The volume instructions match
across this rewrite. The [replay-list sound call](original-modern-replay-list-cursor.md#corrected-shared-positioning-tail)
bypasses its former EDX-setting wrapper starting in 1.5.0. Actual sound
levels and backend success remain unverified.

The same 1.5.0 boundary redirects four frontend calls: the dropdown shared tail at `004642e0`, the two cursor wrappers at `0043eb95` and `0043ebad`, and dialog Escape feedback at `00445ebf`. In 1.4.0 each calls `004181c4`, which saves EDX, sets it to 127, calls `004181d0`, and restores EDX. From 1.5.0 all four call `004181d0` directly. The handler address is unchanged. The call-site change removes the forced multiplier as the handler switches to the dedicated volume field.

A linear disassembly of 1.4.0 finds eight decoded direct callers of the multiplier wrapper. The four additional sites are `0043ef6e`, `0044a423`, `004626aa` and `00463398`. Resolving each of the eight five-byte CALLs in every retained release from 1.4.0 through 1.6.1 confirms that all eight retarget in 1.5.0 and retain the direct destination afterward. A final disassembly scan finds no decoded direct call to the old wrapper. Indirect entry use is outside that scan.

Comparing the union of both direct-call lists in each retained release from 1.4.0 through 1.6.1 shows 71 decoded call sites per build. At 1.5.0 the eight wrapper clients stay at their old addresses and switch destinations. Separately, the wrapper's internal call at `004181c9` drops out of the list and the new slider preview call at `0043777d` enters it. In 1.5.3 that preview call moves to `00437779`. These are the only changes to the address set found by the scan. The equal total counts call instructions, including the old forwarding call, and does not measure requests during play.

Extending the same scan back to the hosted original finds an identical set of 77 call addresses through 1.3.1. At 1.4.0, fifteen addresses drop out and nine enter, leaving 71. The nine additions are the eight wrapper clients listed above and the wrapper's forwarding call. The dropped addresses are `0043eb68`, `0043eb7d`, `0043eb92`, `0043ecea`, `0043ef48`, `0043ef67`, `0044a3c4`, `0044a407`, `0044a41c`, `00462520`, `00462662`, `004626a0`, `00464176`, `0046429e` and `004642d8`. Reproduce by extracting each EXE, filtering `objdump -d -Mintel` for CALL destinations `004181c4` and `004181d0`, then comparing instruction addresses. The address changes include shared-tail rewrites. They do not represent a count of user actions lost or added.

The 176-byte window at `004181d0..00418280` includes the full original handler and the padding after the shorter final handler. Its release groups line up with three edits: the 1.4.0 request gates, the 1.5.0 volume-source change and the 1.5.2 mode-branch consolidation. Read RVA `0x181d0` for `0xb0` bytes to reproduce.

| Executables | Window SHA-256 |
|---|---|
| Hosted original and 1.0.0–1.3.1 | `8fc43b899ec0430ed01370922b08b92c1d18791e77c25f7986172b66401c0f52` |
| 1.4.0 | `63e1247d8ef8b9a2fe92a1259eda037197503a88a8c259bfb4a101dd721ca487` |
| 1.5.0–1.5.1 | `3e28255037b020a816f5a7b1f20ba02275c7817582b5eab0c6cae9183ebe893e` |
| 1.5.2–1.6.1 | `07d4aa7e8efae706cbcab3b8499650e9e583096ce23df354f7877446e876a5ff` |

Original `004181d0..0041827f` consumes EAX as the sound identifier and EDX as a caller-supplied volume multiplier. It preserves that multiplier in EBX, checks globals `00559234` (must be zero) and `0055290c` (must be nonzero), then builds a 16-byte request record. There is no local ID-range or per-ID elapsed-counter gate in this routine.

For record byte `+8`, original computes the low-32-bit product of **55 × `[006fbbf4]` × caller multiplier**, arithmetic-shifts it right by **14**, and stores its low byte (`00418204..0041822e`). The intermediate multiplications wrap at machine width; this is not unrestricted real-number multiplication. Different caller multipliers can therefore produce different requested levels even with the same shared setting.

Modern `004181d0..00418261` keeps the two global admission checks, but also rejects unsigned EAX IDs **≥8**. It no longer reads EDX as a multiplier. It sets byte `+8` from the low byte of separate DWORD **`006fd1d0`**, masked with **0x7f** (`0041821c..00418223`). This is a bit mask, not saturating clamping: arbitrary invalid values need not map to the nearest endpoint.

Modern uses PUSHAD/POPAD on its admitted path. Its EDX input is unused and restored rather than supplying volume; neither branch establishes a meaningful playback-result return. Register/flag contracts must be reconstructed per version, not copied from the old pseudocode.

## Per-ID timing gate

Modern uses one timestamp DWORD per ID at `00664750 + 4*ID`. It subtracts that entry from shared counter `[0079c1a4]`, and returns when the unsigned low-32-bit difference is **less than 5**. An admitted request stores the current counter **before** constructing/submitting the sound record (`004181f2..00418207`).

The package history dates both this elapsed-counter check and the unsigned
ID limit to 1.4.0. In the retained 1.1.0–1.3.1 members, the request-builder
span has neither the ID-8 comparison nor the two counter operands. In
1.4.0, `004181e2` rejects IDs at or above 8 and `004181f2..00418207` reads
the per-ID timestamp, checks the five-count threshold, and stores the new
timestamp. The five-count value is present in every retained later build.
This predates the separate 1.5.0 volume-source change. Counter units and
audible timing remain outside the static comparison.

This gates repeated requests for the same ID independently. The [timer worker trace](frontend-dialog-contract.md#dialog-clock-producer) identifies `0048ebd8` as one increment of `0079c1a4` per serviced active iteration. The same increment is present in the inspected 1.3.1, 1.5.0 and 1.6.0 members. The [timer startup trace](sound-stream-notification-units.md) records a requested rate of 128 pulses per second. Five serviced iterations are nominally about 39 ms if the worker services every requested pulse at that rate. The check observes the counter, and actual cadence, initial timestamps and audio playback remain unverified. The read/update sequence is non-atomic in the inspected instructions. Original's inspected routine has no corresponding local gate.

In 1.6.0 the eight timestamp DWORDs at `00664750..00664770` lie in the
uninitialized `.bss` section, which has no backing file offset. The loader
initializes them to zero. A direct-address disassembly scan finds the
indexed writer through EDI in the request builder and a separate reader
in the caller at `0043776d`. The latter checks the last timestamp for
sound ID 1 against a threshold of `0x30` before calling `004181d0`.
The same local caller sequence is present in 1.5.0 and absent at that
location in 1.4.0. This is a stricter precheck on that caller path. The
generic request builder still checks five serviced iterations. Later
computed writes and runtime request frequency remain unverified.

The sound-slider preview callback adds a stricter outer check: with nonzero action/context input it tries ID 1 only when unsigned counter difference from ID 1's timestamp is **at least 0x30 (48)** (`00437758..0043777b`). It then delegates slider handling to `0046cae0`. The outer check and inner five-unit gate are distinct; do not collapse them into a guessed repeat duration.

## Record fields and retained initialization

Both call record initializer `004e9b20`; its normal-path **61 bytes** are identical, asserted by the evidence script. It initializes a 16-byte record with sentinel/default fields. Both callers then supply the ID at `+0`, byte `[00571124]` at `+4`, requested level at `+8`, and literal 0x40 at `+9`.

Both versions choose the same observed branch policy: if `[006fbc00]==2` or `[005525a4]!=0`, set byte `+11=1` and WORD `+12=0`; otherwise set byte `+7=0x40` and byte `+11=0`. They call `004e9ba0` and increment `00552928`. That counter is incremented without establishing successful audible output; do not label it a count of successfully played sounds.

Across the hosted original and all twelve retained Modern releases, the handler reads the same byte at `00571124` for request field `+4`. A retained producer at `00410c1e` writes a load result into the corresponding 12-byte bank record, at `00571124 + 12*index`. The frontend handler uses the first record and passes its incoming sound ID separately in request field `+0`. The 1.4.0 range check therefore changes admission while the checked bank selector and ID fields retain their roles. This does not identify the installed sample for each ID or establish unchanged sound-bank contents.

Other field/backend semantics remain opaque. Equal initializer bytes do not prove all submission/provider behavior is unchanged.

## Separate slider and restore path

Modern `004376fc` reads integer `006fd1d0`, converts it to floating point and multiplies by a retained double approximating **1/127** before initializing a slider through `0046c950`. It installs update callback `00437740` and preview/action callback `00437758`.

The 1.5.0–1.5.2 constructors store preview target `0043775c` at
`0043772b` and the same update target `00437740` at `00437732`.
The early preview tests the incoming EDX, applies the 48-count check
to sound ID 1, and forwards the action to `0046cae0`. In 1.5.3 the
constructor changes the preview pointer to `00437758`, retaining
these instructions and their two call targets at the new location.
This verifies that the stricter gate belongs to the menu sound slider
by 1.5.0 and survives the later callback move. Input delivery and
audible feedback remain untested.

Update callback `00437740` obtains the slider value through `0046c9b0`, multiplies by exact double **127**, and FISTP-stores to `006fd1d0`. The conversion therefore depends on current x87 rounding; it is not a proven truncating integer cast. The helper's allowed slider range and all setting-load validation remain separate.

The 1.5.0–1.5.2 defaults entry at `00472230` clears EAX, loads
AL=`0x53`, then stores the full DWORD to `006fd1d0`. From 1.5.3 onward,
the store moves to `00472272`. On normal entry, the intervening call at
`00472260` returns either 0 or 1 from the [capability predicate](original-modern-config-loading.md).
The caller leaves zero or changes AL to 3 for the audio-mode default,
then replaces AL with `0x53`. Both paths therefore write the same
full DWORD value 83 to the frontend volume default. The nominal slider
fraction before user changes is `83/127`. The cancel path at `004381b7`
restores the saved value from `00664680`. These are defaults and one
restore witness. Persisted values and audible loudness remain unverified.

On the final [config.dat load and save paths](original-modern-config-loading.md),
`006fd1d0` is at offset `0x1690` from block base `006fbb40`, within the
`0x20f0`-byte payload. The save path selects that base at `00472870` and
copies the block to its write buffer. The load path copies the payload
back to that base at `00472a7f..00472aa3`. For an accepted version-6
configuration, the reviewed post-copy helper checks audio mode without
overwriting the menu volume. The grouped reset path can instead restore
83. This establishes the field's serialized position and the selected
load policy. It does not establish successful persistence under a live
save and restart or validation of every stored value.

A read-only check of the installed `FEDATA/CONFIG/config.dat` found an
8,432-byte payload, header size `0x20f0`, version 6, and DWORD 83 at
offset `0x1690`. It also contains 95 at offset `0xb4`, corresponding to
`006fbbf4`, the volume operand used by the original request builder at
`00418204`. The two fields coexist in the inspected save. A direct
operand scan finds no `006fd1d0` reference in the original disassembly.
That scan does not resolve indirect access to the corresponding bytes
or imply that the original accepts the current file. No file was changed
or loaded by the game for this check.

These producer/consumer links statically support **MP150-009**'s separate menu-sound setting. The removed per-call multiplier supports the mechanism relevant to **MP140-010**'s consistent-volume claim; sample loudness, backend mixing and audible equality are not established.

## Remaining work

Pending: any later timestamp resets, all ID callers and their original multipliers, backend sample assets and mixing, complete saved-setting serialization and range checks, and runtime slider and cancel behavior. The 1.4.0 request gate and 1.5.0 volume and slider paths are dated above. Music volume, other dialog sounds, and race effects have separate paths.

## Five hover-call immediates change, but Modern ignores that argument

The [hover-call audit](scripts/audit_frontend_hover_sound_calls.py) verifies four complete same-address original/Modern envelopes, five isolated changed bytes and direct call targets. [Its manifest](evidence/audits/frontend-hover-sound-calls.json) retains pinned executable hashes, complete-body hashes and disassembly locations.

| Saved Modern entry / label | Complete envelope, exclusive end | MOV EDX sites |
|---|---|---|
| `004449d0` UpdateFrontendChoiceDialogHoverAndRender | `004449d0..00444a52` (130 bytes) | `004449fe` |
| `004450c0` UpdateFrontendTextEntryDialogScene | `004450c0..0044514c` (140 bytes) | `004450ee` |
| `00445680` UpdateFrontendToggleMenuHover | `00445680..0044574f` (207 bytes) | `004456ae`, `004456e4` |
| `0044a6b0` FindHoveredMenuEntryOrRetainSelection | `0044a6b0..0044a860` (432 bytes) | `0044a81c` |

At every listed site, original sets EDX=45 and Modern sets EDX=127. Both then execute `XOR EAX,EAX` and call `004181d0`, selecting sound ID 0. All other bytes in these four envelopes are identical, including admission branches and subsequent hover-state writes. The different caller immediates do not demonstrate a changed hover algorithm.

As established by the complete callee comparison at the start of this chapter, **original uses EDX as its multiplier, Modern does not**. Modern reads configured volume `006fd1d0` instead and applies its own ID/timing admission rules. Reading these five edits alone as an increase from volume 45 to volume 127 would therefore misrepresent the active call contract. The callee's ignored argument can still be present in reconstructed assembly without representing a meaningful maintained-C parameter.

The four caller comparisons do not prove identical audio behavior: original's multiplier differs from Modern's configured source, and Modern's callee gating is different. Likewise the immediate edit does not establish that effects are audibly louder, that a sound is actually emitted, or that hover movement behaves identically with different surrounding state.

**Bounded work status: done; confidence: verified static callers, interpreted using the separately verified callee.** Runtime volume, sound assets, admission timing and complete UI paths remain unverified. No audio, UI or instruction probes were run; executable bytes, Ghidra state and maintained reconstruction sources are unchanged.

## Audio Cancel restores the block without the original cache overwrite

**Confidence: verified paired snapshot and Cancel instructions; work status: done for the local state change, partial for MP100-027’s audible bug claim.** The [Cancel audit](scripts/audit_audio_cancel_difference.py) pins supplied-original and official-final hashes and retains complete audio initializer`00437e00..0043806b` and exit envelope`00438070..0043825c`. The [manifest](evidence/audits/audio-cancel-difference.json) records callback rows, snapshot bytes, exact post-copy changes and field-offset arithmetic. No input, audio or target instructions were executed.

Both menu descriptors`00555d20` (`psaudio`) and`00556128` (`audio`) bind initializer`00437e00` and exit`00438070`. The exit’s Cancel path requires a selected item of type5 whose token matches`CANCEL_AUDIO_OPTIONS` (`00537608`); the separate Race/Exit music policy is already documented in the [music-start chapter](original-modern-music-start.md).

### Two kinds of saved values must remain distinct

Both versions’ identical snapshot sequence at`0043803c..00438061` copies16 DWORDs from`006fbbd0..006fbc10` into`005f3920..005f3960`, and separately saves two cache DWORDs. The existing [named audio controls](original-modern-config-loading.md#changed-audio-defaults-have-named-slider-bindings) identify the corresponding configured settings:

| Control | Configured DWORD | Location in saved64-byte block | Separate cache | Separately saved cache |
|---|---|---|---|---|
|`ASLD_SOUNDFX` |`006fbbf4` |`005f3944` |`00552920` |`005f3960` |
|`ASLD_ENGINEVOLUME` |`006fbbf8` |`005f3948` |`00552924` |`005f396c` |

The initializer can use configured values or these separate cache values for slider display according to`00559234`. Their distinction is established by instructions, not a claim that each cache always equals the physical mixer state. The cache saves are outside the64-byte block, so the sources can hold different values.

### Original can overwrite an already restored volume

On admitted Cancel, both versions restore the separately saved cache values to`00552920/24` and copy the64-byte block back to`006fbbd0`. Original then performs another policy step:

| Version | Instructions after the block copy |
|---|---|
| Original | Tests BYTE`00552909`, previously loaded into BL; if nonzero, writes`00552920` to`006fbbf4` and`00552924` to`006fbbf8` at`004381a7..004381bb` |
| Official final | Has no corresponding extra sound-effects/engine stores; after the copy at`004381a7`, gates the separate menu-sound restore using`00559234` |

Consequently, with stable saved storage and clear DF, let **S** be the configured Engine Volume saved in the block and **C** the separately saved engine cache. Original’s local result is **C** when`00552909!=0`, otherwise **S**. Modern’s local result remains **S**. Sound Effects has the same source-selection change. For example S=95/C=127/flag1 produces original127 versus Modern95 at this local boundary. This is a derived conditional example; no test established127 as the actual or universal saved cache value.

Final also restores its added menu-sound setting`006fd1d0` from`00664680` only when`00559234==0`. This is separate from the two configured volume fields and does not reintroduce their cache overwrite. The subsequent music-preview stop/restart paths can have further effects; this finding does not assert unchanged backend calls or immediate audible state.

**MP100-027 conclusion:** removal of the conditional cache-to-configured-volume overwrite gives concrete partial support for the advertised Cancel fix affecting Engine Volume and Sound Effects. The shared snapshot was not removed, and Modern does not simply stop restoring audio state. Still unverified: the flag/cache lifecycle for an actual affected session, all UI transition admission, later audio application and audible maximum-volume behavior. The release comparison below dates removal of the local overwrite to 1.0.0. A faithful reconstruction must preserve the chosen version’s two saved-value sources and post-copy order rather than merging their globals or silently fixing the original path.

### Modern 1.0.0 already removes the Cancel overwrite

The original's two cache-to-settings stores occupy the
20-byte window at PE RVA `381a7h`. That window is all
NOPs in every retained Modern EXE from 1.0.0 through 1.4.0.
The branch at `004381a3` in 1.0.0 skips it and resumes
at `004381bb`. The 37-byte snapshot sequence at PE RVA
`3803ch` matches the hosted original in all 12 retained
Modern EXEs. Later Modern builds reuse the removed-store
window for other restore instructions. Its NOP count is
therefore evidence for the early implementation only.

Across 1.0.0–1.4.0, the 24 bytes starting at `004381a3` are
`eb 16` followed by 22 NOPs. The hosted original instead starts
with `84 db 74 14` (test BL and skip the two stores when zero).
Reproduce by extracting `nfs3.exe` from the retained release
archives and disassembling at `004381a3`. The checked 1.0.0
member has SHA-256
`988fbf599af256d1486bef967959893c6b26c9fa8ed21b76310bbb7798b4d9df`.
This dates the local removal behind MP100-027 to 1.0.0.
The saved cache values, active mixer behavior and audible
result remain unverified.

The reused window begins restoring a separate setting in
1.5.0. After the 64-byte block copy, the zero-status path
loads `00664680` and writes it to menu-sound volume
`006fd1d0`. The 1.5.0–1.5.2 store is at `004381b1`;
in 1.5.3–1.6.1 it moves to `004381b7`. Both compare
`00559234` with zero before the restore and skip it
when nonzero. This dates a distinct Cancel behavior
associated with the added menu-sound setting. Both
versions leave the restored Engine Volume and Sound
Effects DWORDs alone on the inspected continuation.

In all six retained releases from 1.5.0 through 1.6.1, the
audio initializer snapshots volume at `00437e50..00437e5a`
after calling the menu-sound slider setup at `00437e4b`.
The snapshot copies `006fd1d0` to `00664680`. The preceding
status gate at `00437e39` skips the snapshot when
`00559234` is nonzero. These instructions match in all
six builds. The initializer and Cancel independently
test that status, so the local logic does not establish
freshness if the flag changes between entry and exit.

The snapshot DWORD at `00664680` is in uninitialized
`.bss` in all six retained releases from 1.5.0 through
1.6.1. The section starts at RVA `16e000h`, has a declared
size of `4b1000h` in the section's size field used by
objdump, and has a zero raw-data pointer. Its initial value
is loader zero-fill. A linear disassembly scan of operands
naming any of the four byte addresses finds the snapshot
store at `00437e55` and the corresponding Cancel load in
each build. If no snapshot has run and no alias has written
the cell, an admitted restore therefore reads zero.
Indirect writes and the runtime status transition needed
to take that path remain unverified.

The shared flag `00559234` also gates frontend paths outside
audio. A linear disassembly scan for direct MOV destinations
finds the same four writes in all retained 1.5.0–1.6.1 EXEs.
The normal frontend path clears it at `0044b278`. Two
other menu entries set it to 1 at `0044b964` and `0044ba47`,
including the pause-menu setup. A further path clears it at
`004a35e2` before the display-mode call. The hosted original
has those four direct MOV sites plus `0044be26`. The extra
reset survives through Modern 1.4.0. [Modern 1.5.0 bypasses
the reset wrapper](original-modern-vehicle-dispatch.md#frame-finalization-adds-a-snapshot-call-dialog-cleanup-bypasses-one-reset)
on the dialog cleanup route. This context field is separate
from the [`RemoteOnly` media gate](original-modern-config-loading.md#mediaaudio-gate-snapshots-the-original-remote-prefix-classification).

These writers establish that the snapshot and restore tests
read shared menu context state. Whether a writer can intervene
between the two callbacks for a single Audio Cancel interaction
remains unverified.

### Bank slot zero can be repopulated during gameplay

The hosted original and final 1.6.1 match over the loader `00410b50..00410c2b` and the caller branch `00413c32..00413cd9`. On that branch, the caller selects one of the stems `strex`, `scrate`, `struck` or `slimo`, combines it with path slot `007a2ab4`, and passes EDX zero at `00413cd4`. The loader appends the retained `.bnk` suffix and stores its bank-load result into record zero at `00571124` when it reaches the publication path. The frontend request's read of that slot therefore does not by itself identify a fixed bank filename across game states.

The official final patch archive lists no loose `.bnk` members. The installed frontend bank and its initializer are identified below. Individual sample names remain unresolved.

### Frontend setup loads FESFX.BNK into slot zero

The frontend setup call at `0047306c` targets `004136e0` in both the hosted original and final 1.6.1. The complete 111-byte helper is byte-identical. It copies path slot `007a2ab4`, appends the `fesfx` stem from `00536a20`, and calls `00410b50` at `00413741` with EDX zero and EBX `0x10`. The loader appends `.bnk` and publishes to slot zero if it reaches the bank-result store. Final initializes this path slot to `.\gamedata\audio\sfx\`.

The installed `GAMEDATA/AUDIO/SFX/FESFX.BNK` and its local `gamedata_org/Audio/SFX/FESFX.BNK` counterpart both hash to `0a6a947b64801b0034e7d42c882893dfa1904d88afa314316f2fa687bd2199a9`. This verifies the installed file and expected frontend load route. It leaves successful loading, the live bank handle and per-ID sample decoding unverified.

The setup call and all 111 helper bytes also match in every retained Modern EXE. The original reads the directory from processed installer record index 9, which contains `.\GameData\Audio\SFX\` in the inspected local installer file. Modern 1.0.0–1.3.1 initializes the same slot to that spelling from string index 6 at `0053ec2c`. In 1.4.0–1.5.3 the table moves to `0053eb20` and the string becomes `.\gamedata\audio\sfx\`. In 1.6.0–1.6.1 the table moves to `0053f42c` with the same lowercase string. To reproduce, compare the call at `0047306c` and the helper at `004136e0`, then read the seventh NUL-terminated string in the indicated initializer table. The directory source changed in 1.0.0 while the checked bank-loading instructions stayed the same.

The installed 261,608-byte bank starts with `BNKl`, the magic checked by the loader at `004e8d30`. Its little-endian WORD at `+0x06` is 8. Taking eight little-endian DWORDs starting at `+0x0c` as displacements relative to each DWORD's own file offset yields eight distinct `PT\0\0` headers at `0x2c, 0x4c, 0x6c, 0x88, 0xa0, 0xbc, 0xd8, 0xf4` in order. This structural result is consistent with the handler's eight-ID limit. It leaves the middleware's ID-to-entry lookup and the contents of the samples unverified.

The original and final bank processors match over `00502620..0050273f`. They confirm the directory interpretation above. The type-2 branch reads the unsigned WORD count at `0050267a`, takes the DWORD at `bank + 0x0c + 4*index` at `005026d9`, and adds its own address to the nonzero displacement at `00502736..0050273a`. The shared path passes the rebased pointer to the patch processor at `0050270b`. This verifies that the game traverses the same eight headers in order during bank preparation. The playback request reads the rebased directory as follows.

### Playback uses the sound ID as a zero-based directory index

The original and final share the 105-byte lookup at `004e9bf8..004e9c61` (SHA-256 `afeb08ce7e144bfb65f6e5ed8fbf3d0fae6d2953ba240295658a75949d2aa78b`). It extracts the signed bank selector from request byte `+4`, validates it through `00502570`, and loads the bank pointer from the corresponding 12-byte handle record. It rejects a negative request ID and any ID at or above the bank's WORD count at `+6`. For the type-2 frontend bank, `004e9c53` loads the rebased pointer at `bank + 0x0c + 4*ID` and forwards it to `00501de8` at `004e9c59`.

With FESFX loaded, IDs 0 through 7 therefore select the eight headers in the order listed above. The shared middleware already bounds-checks the loaded bank in the original. Modern 1.4.0 adds a separate check earlier in the frontend request builder. This maps IDs to bank entries. Their audible content and playback success remain unverified.

The hosted original and all twelve retained Modern executables match byte for byte over the following ranges. Extract `nfs3.exe` from each archive and hash the listed half-open PE VA ranges to reproduce.

| Range | Checked operation | SHA-256 |
|---|---|---|
| `00410b50..00410c2b` | Bank filename construction and handle publication | `7dd5d81b51c08bd1065c755aebe36a6e3d7d400934c1b440ccfed106ba4f9eae` |
| `00502620..0050273f` | Bank type, entry count and directory rebasing | `0ec696a7ef5773ad58c081e7b000f16e6e03b993000a49f52a6ee2ab8bc616d7` |
| `004e9bf8..004e9c61` | Bounded request ID lookup and patch dispatch | `afeb08ce7e144bfb65f6e5ed8fbf3d0fae6d2953ba240295658a75949d2aa78b` |
| `005021ac..005022ce` | Tagged patch preparation | `35ae373afd85f50da8e84ff01eb2620ecd201b035358b7d253a2511d8a3a43c1` |
| `00501de8..005021ab` | Tagged patch playback interpreter | `798afbc6b090e340c85b9124bf478a5a34fd7b7e3160c05987ccfeb5ee4f70b9` |

The dated frontend request changes therefore enter a retained bank lookup. The compared ranges now extend through the tagged patch preparation and playback interpreter bodies. They establish local code identity. Active bank data, backend callees and audible output remain separate.

### The 1.5.0 Audio menu adds the matching slider

The retained 1.5.0 `fedata/menus/audio.mnu` adds a slider with `codelink=ASLD_MENUSOUND`, `ypos=1`, and `text=lang1934`. The same release's English text member resolves ID 1934 to **Menu Sounds**. The 1.4.0 Audio menu has no matching codelink, and the shipped `psaudio.mnu` matches across this release boundary. The Audio menu asset hashes are `abd8b8f918fa9a3385b5338e049d931cddf87391b65a030b164971a98a4178ea` (1.4.0) and `8f15f73685ef8421a9e886db28d99a369c7515f1adde926bd55167fa3b05339e` (1.5.0).

In 1.5.0, the setup path at `00437e4b` calls the constructor at `004376fc`. Its lookup at `00437707` passes the literal `ASLD_MENUSOUND` at `00538f84`; successful lookup initializes the slider from `006fd1d0` before installing the update and preview callbacks. This binds the shipped menu element to the separate volume field at its introduction. Audio output and live menu interaction remain untested.
