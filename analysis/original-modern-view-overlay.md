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

The [rectangle-producer follow-up](original-modern-viewport-geometry.md#overlay-rectangle-at-007a2750-separate-derived-extent-correction) now maps the new group to a derived extent correction and two checked update calls. Next: complete the source-group/profile and update-order contracts, qualify the 44-byte descriptor capacity and selected index, resolve the active indirect submission slot, and compare ordinary/nonzero-origin/boundary rectangles visually when runtime work is in scope. No release-note ID or visual fix is assigned solely from this static mechanism. Executable bytes, saved Ghidra state, raw exports and maintained C remain unchanged; no target instructions were executed.
