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
