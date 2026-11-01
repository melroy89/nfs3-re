# Frame Size setting: two choices become four mode bits

## Verified UI-to-storage association

The [audit](scripts/audit_frame_setting_difference.py) connects official menu definitions and English label data to static list descriptor **`005567a8`**, key **`widescreen`** at `00538008`, and selection storage **`006fbc4c`**. [Evidence manifest](evidence/audits/original-modern-frame-setting.json). Both executable hashes and the official archive hash are checked; menu/language members are read directly from that archive, without running the game.

Official `advgrph.mnu` binds an arrow-tab button and cascade to `listname=widescreen`, with label `kMenuGRAPHICSWideScre001`. The paused graphics asset `psgraph.mnu` uses the same list and `kMenuPSGRAPHWideScre001`. The executable's symbolic-name table maps those labels to IDs1504 and1283; the official English file resolves both to **“Frame Size”**. Its cascade description ID1505 is “Frame Size is...”. The historical internal key therefore must not be mistaken for a direct name of an unrelated setting merely because it says widescreen.

The descriptor uses five DWORDs: name pointer, WORD-label-list pointer, optional eligibility pointer, another slot, and selection pointer. Both versions retain the name and selection address, with the two middle optional fields zero. The label list changes:

| Version | Label-list pointer | WORD IDs before zero sentinel |
|---|---|---|
| Supplied original | `005561be` | 229,228 |
| Official Modern | `005591f6` | 1951,1952,1953,1954 |

The official English data labels IDs229/228 “Off”/“On”; this is not authenticated original-retail language provenance. The two original option IDs and the four Modern IDs themselves are direct paired executable evidence.

## Modern ordinal meanings and consumers

The official English labels, also independently represented by the [embedded fallback table](original-modern-language-table.md), establish:

| Ordinal stored in `006fbc4c` | Official English choice | Bits0/1 |
|---:|---|---|
| 0 | Full, Centered | 00 |
| 1 | Full, Shifted | 01 |
| 2 | 2:1, Centered | 10 |
| 3 | 2:1, Shifted | 11 |

The [viewport constructor](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles) independently reads these low bits: bit1 changes the physical rectangle to a two-to-one extent, while bit0 changes the covering-frame vertical origin. The [resize wrapper](original-modern-frame-resize.md) and [overlay routine](original-modern-view-overlay.md) change their original whole-DWORD nonzero tests to bit1 tests. This now connects their fields to an actual labelled setting, rather than inferring association from adjacent code.

For normal admitted ordinals, bit0 distinguishes shifted versus centred choices and bit1 distinguishes Full versus2:1 choices. Do not treat the field as an invariant Boolean or assume arbitrary loaded/network values are confined to0..3 without producer validation. Session value1 also has separate constructor/resize overrides, documented in those reports.

## Generic list lookup and accepted selection write

Matched lookup-path witness `00442c80..00442cdc` scans20-byte rows from `005563e8`. On a name match it returns row+4 (the label-list pointer) and writes row+10h (the selector pointer) through the supplied output pointer.

The Modern cascade input witness `004624a0..004624df` reads item+60h, calls that lookup with output local−10h, and obtains count/eligibility through the existing helpers. The cascade template input pointer at `00556ed8` is `004624a0`. On the accepted path `00462633..00462663`, hit/eligibility checks lead to extraction of the signed selected ordinal from the high WORD of item+50h and **`MOV DWORD PTR [EDX],EAX` at `00462661`**. The selector store is32 bits; the fact that the ordinal came from a WORD does not make the write16 bits.

This corrects the width wording in the earlier [lap cascade follow-up](lap-choice-gameplay-domain.md#reviewed-list-and-actual-cascade-dispatch), which uses the same generic callback. The stored normal small ordinal is unchanged by that documentation correction, but layout and alias analysis depend on the full write width. No saved Ghidra metadata or executable bytes were changed.

These are partial-function instruction witnesses and the previously recovered template/parser linkage, not an exhaustive test of closed/open, mouse, keyboard or eligibility behaviour. Actual list creation and selected file/resource at runtime remain unobserved.

## Release-note and reconstruction boundary

**MP160-004 now has partial static support**: Frame Size expands from two choices to four, explicitly exposing shifted/centred and Full/2:1 modes, with concrete storage/bit consumers. The advertised visual restoration of camera shift, actual horizon position and introduction in v1.6.0 remain unverified. The [projection investigation](original-modern-projection.md) retains related unresolved camera/horizon evidence; these must not be collapsed into one proved render result.

The [covering-rectangle-to-centre chain](original-modern-projection.md#frame-size-covering-rectangle-reaches-the-projection-centre) now additionally traces one non-two-player wide-angle path into the actual projection centre stores, with concrete1920x1080 centered/shifted examples. It establishes data flow rather than merely adjacent code, while retaining the active-camera, resize and final rendered-output limits.

For C reconstruction, separate original two-choice policy from Modern four-choice bit semantics, preserve32-bit selector storage and version-specific gates, and map language-resource/fallback lifetime. Next qualify ordinary selections0..3, out-of-range loaded values, session overrides and viewport/horizon output in later runtime work. No game, input or instruction probes were run; executables, saved Ghidra state, exports and maintained C are preserved.


## Historical1.5.0 to1.5.1 first-choice translation index

The [historical descriptor/asset check](original-modern-localization-151.md#frame-size-first-choice-label-switches-to-the-new-full-entry) verifies the same key/selector descriptor but a two-choice WORD list changing184,1933→1932,1933. French/Spanish first-choice strings differ through that retargeting; German remains byte-identical. This dates a label-index change, not the final four-choice expansion or a framing arithmetic change. Exact historical words and six-language values are retained separately from final numbering.


## Direct1.5.3 to1.6.0 expansion boundary

The [historical audit](scripts/audit_frame_setting_history.py) verifies both retained archive hashes and their extracted EXE hashes against existing provenance manifests, then reads each matching packaged English text file. Its [evidence manifest](evidence/audits/frame-setting-history.json) records descriptor DWORDs, WORD lists, English labels and asset hashes. No archive member was installed or executed.

| Descriptor field |1.5.3 |1.6.0 |
|---|---|---|
| Row address | `005567a8` | Same |
| Key | `widescreen` at`00538008` | Same |
| Label-list pointer | `005562d2` | `005591f6` |
| WORD IDs before zero terminator |1932,1933 |1951,1952,1953,1954 |
| Two optional fields |0,0 |Same |
| Selection storage |`006fbc4c` |Same |

Matching English labels are **Full /2:1** in1.5.3, versus **Full, Centered / Full, Shifted /2:1, Centered /2:1, Shifted** in1.6.0. This directly dates the selected two-to-four option-table expansion to the immediate retained release pair, rather than guessing from original/final alone. It corroborates MP160-004's expanded setting mechanism; the separate final bit-consumer analysis above explains final ordinal interpretation.

**Boundary:** these historical descriptor/asset checks do not prove that every1.6.0 geometry consumer already matches final, that a camera visibly shifts correctly, that arbitrary old saved ordinals are migrated, or that every localized label is correct. The selector address staying equal is not proof that its ordinal semantics stay equal: historical ordinal1 is2:1, while final ordinal1 is Full, Shifted. Actual load/reset policies and consumer versioning remain separate.

**Work status:** selected historical expansion mechanism done, confidence verified static. Full MP160-004 outcome remains partial because runtime/complete consumer coverage is not established. No viewport, UI or instruction probe was run.


## Historical constructor changes Boolean policy to two independent bits

The extended [historical audit](evidence/audits/frame-setting-history.json) captures complete constructors **1.5.3 `004be5e0..004be850`** (624 bytes) and **1.6.0 `004be5e0..004be85a`** (634 bytes), plus their paired record setters. The complete1.6.0 constructor is asserted byte-identical to official final's same634 bytes, with both artifact hashes verified. This narrows the earlier consumer-date limitation for this constructor only.

In1.5.3, `004be620..004be635` sets ESI to normalized1 only when setting`006fbc4c` is nonzero and session`006fd3b0` is not1. Thus its rectangle choice treats all nonzero values alike. In1.6.0, `004be620..004be631` leaves ESI0 for session1; otherwise it reads the **raw DWORD setting** into ESI. The physical rectangle tests **bit1** at`004be640`, and covering-frame origin tests **bit0** at`004be65a`, with an additional bit1 adjustment inside the shifted branch.

Using the existing source-group interpretation and ordinary nonoverflowing dimensions, define `S=(3*W) arithmetic_shift_right2` and `D=(H-S) arithmetic_shift_right1`. Both versions write covering-frame heightS.1.5.3 unconditionally starts covering Y at **`D+(D arithmetic_shift_right1)`**, then applies its nonzero-mode correction.1.6.0 starts atD and applies that extra shift only when bit0 is set. Its physical-height2:1 choice depends on bit1, independently of shifting. Preserve arithmetic shifts/wrapping semantics for exceptional integer inputs rather than translating negative shifts into ordinary C division.

| Setting interpretation, excluding session1 |1.5.3 authored choice/policy |1.6.0 authored choice/policy |
|---|---|---|
| Ordinal0 | Full; covering-frame shifted formula | Full, Centered; no bit0 shift |
| Ordinal1 |2:1; nonzero-mode rectangle and shifted formula | Full, Shifted; bit0 set, bit1 clear |
| Ordinal2 | Not one of its two authored choices; normalizes nonzero |2:1, Centered |
| Ordinal3 | Not one of its two authored choices; normalizes nonzero |2:1, Shifted |

This demonstrates an actual local geometry-policy change alongside the expanded label table, not merely four renamed labels. Session1 still overrides the selector to0, but1.5.3's unconditional covering shift and1.6.0's bit-gated policy remain distinct. Do not extend the table into a claim about every camera or split-screen result.

Remaining: migration/reset of stored ordinals, all other1.6.0 frame consumers and helper/state lifetimes, malformed settings, mode dimensions and visible camera effects. Identical1.6.0/final constructor instructions do not prove equal transitive helper behaviour or runtime state. MP160-004 remains partial; no geometry or floating-point instruction was executed.


## Historical config version5 to6 selects reset rather than ordinal conversion

The extended [historical audit](evidence/audits/frame-setting-history.json) now captures both version-decision ranges, complete18-byte header-copy helpers and display-default envelopes. In1.5.3, file-backed template`0055e8a0` is DWORDs **`20f0,5,0`**. In1.6.0 it is **`20f0,6,0`**. These are configuration versions, not patch release numbers; earlier/later template writes and real saved-file provenance remain separate.

The complete decision range **`00472aac..00472aeb`** differs only at **`00472ac3`**, the threshold immediate5→6. Both first require loaded size`20f0`, load version WORD`006fbb44`, reject nonzero high byte, then compare the low byte unsigned with the threshold. Matching version5 is accepted by1.5.3 but **rejected by1.6.0**, entering `00472ad2`: header refresh, display defaults at`00472ad7`, then HUD and other grouped default helpers. This is a reset route, not a per-value migration table.

Within the captured1.6.0 display defaults, **`00472d92` clears EDX and`00472d94` stores0 at Frame Size`006fbc4c`**. The same local zero store is present in1.5.3. Consequently, if a version5 configuration reaches the1.6.0 header decision with the stated size, it does not simply preserve historical ordinal1 and reinterpret it as Full, Shifted: the inspected reset route explicitly writes ordinal0, corresponding to the new Full, Centered choice. Other grouped settings can also be reset; this is not an isolated Frame Size conversion or a promise that every loaded field is cleared.

Accepted version6+ headers with zero high byte instead bypass these grouped defaults in this local decision; arbitrary future versions are not rejected solely for being above6. Their existing Frame Size fields can retain loaded values absent other writes. Do not infer that every old file has version5, that a patched/mixed header is genuine, or that later initialization cannot change the result.

**Resolved locally:** version bump, changed acceptance threshold and direct Frame Size reset consumer. **Still pending:** actual save/read success and file provenance, all template/header writers, later settings overrides and visible camera behaviour. This supplies a concrete compatibility gate without claiming a tested upgrade migration. No config file was read by the game, saved, changed or executed during this analysis.
