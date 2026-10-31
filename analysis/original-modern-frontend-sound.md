# Original versus Modern: frontend sound volume and request throttling

## Evidence boundary

Static comparison of the supplied original/backup and official Modern v1.6.1, with exact hashes in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_frontend_sound_difference.py`. The [manifest](evidence/audits/original-modern-frontend-sound.json) retains paired sound routines, the unchanged record initializer and Modern slider/restore witnesses. No game, audio or instruction probes were executed.

## Changed caller contract at 004181d0

Original `004181d0..0041827f` consumes EAX as the sound identifier and EDX as a caller-supplied volume multiplier. It preserves that multiplier in EBX, checks globals `00559234` (must be zero) and `0055290c` (must be nonzero), then builds a 16-byte request record. There is no local ID-range or per-ID elapsed-counter gate in this routine.

For record byte `+8`, original computes the low-32-bit product of **55 × `[006fbbf4]` × caller multiplier**, arithmetic-shifts it right by **14**, and stores its low byte (`00418204..0041822e`). The intermediate multiplications wrap at machine width; this is not unrestricted real-number multiplication. Different caller multipliers can therefore produce different requested levels even with the same shared setting.

Modern `004181d0..00418261` keeps the two global admission checks, but also rejects unsigned EAX IDs **≥8**. It no longer reads EDX as a multiplier. It sets byte `+8` from the low byte of separate DWORD **`006fd1d0`**, masked with **0x7f** (`0041821c..00418223`). This is a bit mask, not saturating clamping: arbitrary invalid values need not map to the nearest endpoint.

Modern uses PUSHAD/POPAD on its admitted path. Its EDX input is unused and restored rather than supplying volume; neither branch establishes a meaningful playback-result return. Register/flag contracts must be reconstructed per version, not copied from the old pseudocode.

## Per-ID timing gate

Modern uses one timestamp DWORD per ID at `00664750 + 4*ID`. It subtracts that entry from shared counter `[0079c1a4]`, and returns when the unsigned low-32-bit difference is **less than 5**. An admitted request stores the current counter **before** constructing/submitting the sound record (`004181f2..00418207`).

This gates repeated requests for the same ID independently. It does not prove backend playback succeeded, establish elapsed milliseconds, or prevent all concurrent access: no atomic read/update sequence appears here. The counter's producer/unit and timestamp initialization are not established in this chapter. Original's inspected routine has no corresponding local gate.

The sound-slider preview callback adds a stricter outer check: with nonzero action/context input it tries ID 1 only when unsigned counter difference from ID 1's timestamp is **at least 0x30 (48)** (`00437758..0043777b`). It then delegates slider handling to `0046cae0`. The outer check and inner five-unit gate are distinct; do not collapse them into a guessed repeat duration.

## Record fields and retained initialization

Both call record initializer `004e9b20`; its normal-path **61 bytes** are identical, asserted by the evidence script. It initializes a 16-byte record with sentinel/default fields. Both callers then supply the ID at `+0`, byte `[00571124]` at `+4`, requested level at `+8`, and literal 0x40 at `+9`.

Both versions choose the same observed branch policy: if `[006fbc00]==2` or `[005525a4]!=0`, set byte `+11=1` and WORD `+12=0`; otherwise set byte `+7=0x40` and byte `+11=0`. They call `004e9ba0` and increment `00552928`. That counter is incremented without establishing successful audible output; do not label it a count of successfully played sounds.

Other field/backend semantics remain opaque. Equal initializer bytes do not prove all submission/provider behavior is unchanged.

## Separate slider and restore path

Modern `004376fc` reads integer `006fd1d0`, converts it to floating point and multiplies by a retained double approximating **1/127** before initializing a slider through `0046c950`. It installs update callback `00437740` and preview/action callback `00437758`.

Update callback `00437740` obtains the slider value through `0046c9b0`, multiplies by exact double **127**, and FISTP-stores to `006fd1d0`. The conversion therefore depends on current x87 rounding; it is not a proven truncating integer cast. The helper's allowed slider range and all setting-load validation remain separate.

Defaults path `00472270` writes AL=`0x53` before storing full EAX to `006fd1d0`; that instruction alone does not prove all upper bytes are zero on every caller state. A cancel/restore neighborhood copies `[00664680]` back to this field at `004381b7`, providing a concrete restore path but not a complete settings transaction audit.

These producer/consumer links statically support **MP150-009**'s separate menu-sound setting. The removed per-call multiplier supports the mechanism relevant to **MP140-010**'s consistent-volume claim; sample loudness, backend mixing and audible equality are not established.

## Remaining work

Pending: counter unit/initialization, all ID callers and removed-multiplier meanings, backend sample assets/mixing, complete saved-setting serialization/range checks and runtime slider/cancel behavior. Historical introduction dates require earlier patch releases. This chapter does not establish music-volume fixes, all dialog sound choices or race-effect behavior.

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
