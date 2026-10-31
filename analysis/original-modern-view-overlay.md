# Viewport tiles and vehicle-overlay orchestration

## Complete comparison and a range-accounting limitation

The complete paired address envelope **`00489240..0048962d`** contains **143 changed bytes**. The retained Modern function inventory includes `00489240..00489614` and `00489619..0048962d`, omitting five padding bytes. Its same-address comparison therefore reports only **138** changed bytes. In original, bytes `00489614..00489619` are part of the six-byte indirect CALL beginning at `00489613`; they are not original padding.

The [audit](scripts/audit_view_overlay_difference.py) retains the full envelope, both counts, exact change addresses, retained subranges and the new Modern helper. [Manifest](evidence/audits/original-modern-view-overlay.json). Baseline hashes are checked before disassembly; ends are exclusive. This illustrates why Modern function ranges alone cannot define original function boundaries or complete instruction differences.

## Entry gate changes from zero test to one bit

The shared entry first requires raw `007922fc != 0`, `007a3d10 == 0`, helper `00423b00(EAX=0)` returning1 and indexed flag `0079c4a0[0] == 0`. Pointer/state semantics beyond those established in existing research are not inferred here.

At `0048928c`:

| Original | Modern |
|---|---|
| Require DWORD `006fbc4c == 0` | Require bit1 of byte `006fbc4c` clear (`TEST byte,2`) |

Modern can therefore admit nonzero values with bit1 clear that original rejects. Other entry gates still apply; this does not prove those values occur in a game session. Do not translate the new test into a generic nonzero Boolean check.

## Rectangle sources move

The x87 scaling and loop setup now read these corresponding source addresses:

| Observed role in this routine | Original | Modern |
|---|---|---|
| Horizontal origin | `007cdb98` | `007a2750` |
| Vertical origin | `007cdb9c` | `007a2754` |
| Horizontal extent | `007cdba0` | `007a2758` |
| Vertical extent | `007cdba4` | `007a275c` |

Both primary tile setup and optional overlay size calculations use the new extents. The [viewport reference geometry report](original-modern-viewport-geometry.md) establishes related Modern rectangle construction; this chapter does not assume every group/producer is interchangeable or prove live values. Merely comparing multipliers would miss this source change.

The [source-group follow-up](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles) resolves the ordinary linkage: original reads the physical/fitted record's +10h group, whereas Modern reads an expanded derivative of the covering +0 group. For zero flags at1920×1080, the Modern initializer produces covering `{0,-180,1920,1440}`, then correction yields `{0,-180,1922,1441}`. Thus describing this as only a two-pixel horizontal expansion would omit the changed source height and origin. These are static initial tuples, not lifetime invariants or observed cabin pixels; later resize updates and clipping still matter.

The retained middle tile/draw orchestration `004892dd..004894f8` is byte-identical. Its descriptor/loop/resource bounds and transitive draw implementations remain separate; the prior [function notes](detailed-analysis-notes.md#viewport-tile-and-overlay-orchestration-named) describe its bounded mechanical role.

## Descriptor-read rewrite and additional fixed-colour quads

Optional overlay construction still uses the selected byte from the object at +50bh to compute a **44-byte record** at `00791c10 + index*44`. Original reads each attribute through an absolute indexed operand; Modern first forms ESI as the record base, then reads offsets +8/+10h/+18h/+20h and +0ch/+14h/+1ch/+24h, followed by state DWORD+4. These map to the same source addresses for the same valid index. That address correspondence is not full register/flags or callback equivalence.

Modern moves the state call and four-vertex indirect submission earlier. Original's optional gate at `004894f8` skips directly to the final helper when false; Modern instead skips to **`004895fc`**, where the new fixed-colour path is evaluated. Consequently the added path is not conditional on the optional overlay being enabled.

At `004895fc`, Modern calls **`004900c8`** when `007cdb9c != 0`, or when it is zero and signed `007cdb8c > 0`. Otherwise it skips the call. The shared final path at `00489619` still passes the object to `00488470`.

Helper `004900c8..00490134` submits two axis-aligned shapes through `004900b0`. Using source DWORD names rather than unverified global labels, its derived corners are:

- First: `(0,0)` to `(value[007cda68], max_signed(value[007cdb9c], value[007cdb8c]))`.
- Second: `(0, min_signed(wrap32(value[007cdb8c]+value[007cdb94]), wrap32(value[007cdb9c]+value[007cdba4])))` to `(value[007cda68], value[007cda6c])`.

Signed integer values are converted to binary32 bit patterns by `004f9390` (`FILD` then `FSTP` through the stack). Wrapper **`004900b0..004900c5`** forms four rectangle corners and calls `0047d1d0` with fill argument1 and literal colour DWORD **`ff000000h`**. The [existing coloured-shape contract](detailed-analysis-notes.md#coloured-coordinate-drawing-helpers-0048b4a0-0047d1d0) explains its ten stack arguments and consumption. Colour channel interpretation, actual clipping, negative/reversed extents and visible bars remain untested. These bytes do not prove every backend interprets that colour identically.

## Reconstruction implications and next evidence

Separate the revised bit gate, rectangle-source selection, address-equivalent descriptor reads and genuinely new draw submission. Preserve wrapped additions, signed comparisons, unaligned stack/vertex layout, x87 integer-to-float conversion and callback/state ordering. Do not claim unchanged drawing because the middle loop is identical, or claim 138 is a complete original instruction-difference count.

The [rectangle-producer follow-up](original-modern-viewport-geometry.md#overlay-rectangle-at-007a2750-separate-derived-extent-correction) now maps the new group to a derived extent correction and two checked update calls. The [source-group follow-up](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles) also maps the physical versus width-based 4:3 groups and ordinary initialization examples. Next: complete profile/flag admission and update-order contracts, qualify the 44-byte descriptor capacity and selected index, resolve the active indirect submission slot, and compare ordinary/nonzero-origin/boundary rectangles visually when runtime work is in scope. No release-note ID or visual fix is assigned solely from this static mechanism. Executable bytes, saved Ghidra state, raw exports and maintained C remain unchanged; no target instructions were executed.

## Optional indexed overlay has gear-labelled shape producers

The expanded overlay audit now retains paired setup `00488c6e..00488d41` (211 bytes), identical in both executables. Eight calls to `004d4080` receive consecutive destinations beginning `00791c10` with44-byte stride and shape names at `0053b70c+8*index`: `geaR`, `geaN`, `gea1`, `gea2`, `gea3`, `gea4`, `gea5`, `gea6`. The manifest pins all eight destination/name bindings. These are the same records indexed by vehicle byte`+50bh` at consumer `0048954f/004895a2`.

The names and R/N/1..6 ordering support a **gear-display association**, consistent with the independent [gear-label rendering research](original-modern-numeric-scale.md), but the actual shape images and complete allowed index domain have not been validated here. This producer-to-consumer binding narrows the earlier opaque optional-overlay role; it does not identify the primary viewport tile imagery or prove the cabin-edge claim MP160-008. Those optional records alone do not support that claim; the following primary-tile investigation supplies a separate dashboard binding, while exact source-to-pixel coverage remains unresolved. Do not infer that all drawing in this function depicts the cabin merely because it runs in a vehicle viewport. The paired optional shape setup is retained; Modern's changed extent source and orchestration remain the differences described above. No asset was rendered or game code run.

## Primary tile binding supports a bounded cabin-widening association

The paired setup `00488b8c..00488c33` (167 bytes), now pinned by the overlay audit, is identical. It looks up named resource `dash.qfs`, passes shape strings `0000`/`0001` and destination `00791d70` to `004d4ae0`, then publishes its return into primary drawing gate `007922fc`. The tile consumer reads indexed fields from the same44-byte record base at `00489447..0048948f`. Together these give a **dashboard/cabin association inferred from the asset name and concrete record linkage**, rather than confusing the separate gear-labelled records with the primary tiles. Actual images, loader success and all accepted indices remain unvalidated.

Combined with the [expanded rectangle producer](original-modern-viewport-geometry.md#overlay-rectangle-at-007a2750-separate-derived-extent-correction), this provides partial static support for MP160-008. For X=0 and ordinary positive, nonoverflowing source width W, the width correction is `floor((W-1)/640)`:0 at640,1 at1280,2 at1920,3 at2560. These are instruction-derived extent deltas, not observed pixel measurements. It is **not** a global three-unit cap: at3840 the same expression yields5. The routine also changes height, and Modern's upstream covering rectangle can differ from original's physical/fitted source, so this local correction alone does not describe every displayed cabin boundary.

The catalog records this as partial: named dashboard-resource linkage and the width-dependent mechanism are established, while exact screen-pixel coverage, seam removal, all flags/resolutions, historical introduction and final rendering remain unresolved. The earlier one-pixel claim MP100-018 cannot be dated or isolated from this final pair and remains separate. No image, game or renderer code was executed.

## Rectangle units reach tiled vertex coordinates, not proven pixels

The overlay audit now decodes and asserts the retained binary64 constants `0053b76c=256`, `0053b774=1/640` and `0053b77c=1/480` in both executables. The ordinary mathematical tile steps are `256*extentW/640` horizontally and `256*extentH/480` vertically. Actual x87 operation order and binary32 spills at locals`+46h/+52h` remain part of the contract; these formulas are not unrestricted floating-point equivalence claims.

The retained loop starts from the supplied origin, computes candidate right/bottom coordinates, clamps them against origin+extent, and submits four vertices through slot `009ef94c` at `004894af`. The outer progression is horizontal, inner progression vertical; the44-byte descriptor index advances for each inner submission. For typical finite, fitting positive examples the ratios imply three columns and two rows, but full range/rounding/descriptor-capacity invariants are not established by that illustration. There is no separately established per-submit table-capacity check.

This closes a mechanical step for the dashboard claim: changed rectangle values affect actual submitted coordinate bounds, not merely an unused global. It still does not turn extent correction N into an exact N-pixel visual expansion. Renderer transformation, edge rules, texture coordinates, clipping and viewport origin can affect coverage. The algorithm and constants are retained between versions; the primary difference here is their input rectangle/source, together with the surrounding policy changes already documented. A useful later acceptance test would compare the submitted vertices and resulting cabin boundary under the same dimensions/flags, separately from whether a seam is visible. No vertices were submitted during this audit.
