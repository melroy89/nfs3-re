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

This corrects the width wording in the earlier [lap cascade follow-up](lap-choice-gameplay-domain.md#reviewed-list-and-generic-ordinal-writer-follow-up), which uses the same generic callback. The stored normal small ordinal is unchanged by that documentation correction, but layout and alias analysis depend on the full write width. No saved Ghidra metadata or executable bytes were changed.

These are partial-function instruction witnesses and the previously recovered template/parser linkage, not an exhaustive test of closed/open, mouse, keyboard or eligibility behaviour. Actual list creation and selected file/resource at runtime remain unobserved.

## Release-note and reconstruction boundary

**MP160-004 now has partial static support**: Frame Size expands from two choices to four, explicitly exposing shifted/centred and Full/2:1 modes, with concrete storage/bit consumers. The advertised visual restoration of camera shift, actual horizon position and introduction in v1.6.0 remain unverified. The [projection investigation](original-modern-projection.md) retains related unresolved camera/horizon evidence; these must not be collapsed into one proved render result.

For C reconstruction, separate original two-choice policy from Modern four-choice bit semantics, preserve32-bit selector storage and version-specific gates, and map language-resource/fallback lifetime. Next qualify ordinary selections0..3, out-of-range loaded values, session overrides and viewport/horizon output in later runtime work. No game, input or instruction probes were run; executables, saved Ghidra state, exports and maintained C are preserved.
