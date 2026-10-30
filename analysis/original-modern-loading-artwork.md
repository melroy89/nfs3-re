# Original versus official Modern: loading artwork tiling and progress setup

## Scope and binaries

Static comparison of matched routine `00494cb0` in the supplied original and official Modern executable. The report records tile-grid arithmetic and progress-state writes. It does not establish final pixels or all behavior of downstream raster/text helpers.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.
- Existing paired function inventory records 748 bytes at this entry, with 480 differing bytes. The name `RenderTiledLoadingArtworkAndInitializeProgressBounds` comes from the maintained Modern database. Its same-VA comparison window is not a recovered original name or boundary: original autoanalysis body ends at `00494f9f` (752 bytes), Modern at `00494f9b` (748 bytes). The matched routines have materially different tile and progress calculations.

## Raster and tile grid

Both routines obtain four viewport bounds through `004beb20` and set `0079f288` to one (`00494cec`). The source rectangle record passed in EAX differs: original `007cdac0`, Modern `007a2740` (`00494cf6`). Modern uses the [centred 4:3 reference rectangle](original-modern-viewport-geometry.md); this is a destination/reference-space change, not evidence that the input image pointer itself differs.

| Property | Original | Official Modern |
|---|---|---|
| Scale factors | Bounds at `[EBP+0x4a]` and `[EBP+0x4e]` are multiplied by floats `0053bddc` and `0053bde0` (`00494d00–d2f`) | Same bounds multiplied by floats `0053bdcc` and `0053bdd0` (`00494d00–d2f`) |
| Live tile-allocation extent across `00431bc0` | `EDX=0x20`; `ECX=EBX=0x10` (`00494d1e–d32`) | `EDX=0x100`; `ECX=EBX=0x10` (`00494d1e–d32`) |
| Live grid-count values across raster selection `004eada0` | `ECX=0x14` (20), `EBX=0x0f` (15) (`00494d37–d4b`) | `ECX=3`, `EBX=2` (`00494d37–d4b`) |
| Per-tile source step | `ESI*32` and `EDI*32` (`00494dbb–dc5`) | `ESI*256` and `EDI*256` (`00494dbb–dc6`) |
| Last tile origin override | No special last-tile override; indices remain stepped by 32 | Last X-column origin is forced to `0x180` (384), last Y-row origin to `0xe0` (224) (`00494dc6–de9`) |

The Modern grid is explicitly three columns by two rows, with 256-unit steps and edge origins of 224 and 384. Those final origins make the last tile overlap the preceding tile in each axis when interpreted as tile origins. In the original, the 20-by-15 grid and 32-unit steps have no corresponding edge-origin override. This is an arithmetic difference; the renderer's coordinate orientation, source-resource dimensions and final crop are not fully established here, so it is not a universal claim about visible coverage.

`00431bc0` resets cached render state and preserves EDX; it is not a tile-size API. The following `MOV EAX,EDX` carries the chosen square tile extent to allocator `004ef190`. Likewise `004eada0` selects an active raster window; ECX/EBX are held grid counts, not arguments describing a grid to that helper. The source X origin is carried in EDX and Y in EBX to the tile/read and destination draw paths. This corroborates 20 X columns × 15 Y rows versus 3 X columns × 2 Y rows: **300 versus 6 tile iterations** on the ordinary loop path. It does not measure performance or successful allocation/rendering.

The inner loop calls `004f2cb0` to obtain per-tile data, then `004d4080` to prepare the tile. **Both versions** call floor helper `004f1c30` for positioned coordinates and ceiling helper `004f2d78` for scaled extents. Original uses a QWORD 32.0 step, spills the floor/ceil results through binary32 locals, then calls truncation helper `004dfd56` before integer stores. Modern uses its explicit selected origins/256 extent, spills products to double before floor/ceil, and converts those integral results directly with FISTP. Thus floor/ceiling is retained behavior, not an introduced replacement for simple truncation. For ordinary representable screen-size integers, the extra old truncation need not change the integral result; exceptional/large values and x87 status are not proven equivalent.

Both create a 640×480 staging raster: EDX is set to 480 at `00494d55`, retained across color-conversion helper `004ef760` and fill helper `004ef1b0`, then paired with EAX=640 at allocator call `00494d76`. `004ef760` converts an RGB value and saves/restores EDX; it does not set a raster height. The callsites/preservation establish requested dimensions, not allocation success or final screen size. Both paths fill/select staging storage, draw the source into it and later dispose of temporary objects; complete failure/ownership behavior remains separate.

## Progress and text bounds

The progress setup differs after raster cleanup:

- **Modern (`00494ea8–4f50`):** clears `00561b3c` and sets `00561b34` to `-1`, formats the ellipsis label through `00494c5c`, and computes a vertical bound as `[EBP+0x46] + FISTP([EBP+0x76] * 448.0)`, storing it at `0079f284` (`00494ec0–ed5`). It computes a horizontal coordinate as `[EBP+0x42] + FISTP([EBP+0x72] * 10.0)` and calls `004d1000` (`00494edb–ef0`). It then computes `[EBP+0x42] + [EBP+0x4a] * 0.015625`, stores the FIST-converted value at `0079f280`, and stores the unconverted x87 result at `0053bddc` (`00494ef5–f11`). The source bounds and scales used here were set earlier in the routine; this code establishes the arithmetic, not the semantics or visible placement of the progress UI.
- **Original (`00494ecc–4f79`):** draws localized text ID `0x18c` through `004d1850` and `004df690`, with scale-derived values at `0053bdf0` and `0053bdf4` passed through truncation helper `004dfd56`, then calls `004d1000` with the resulting registers and stack argument (`00494edb–f41`). It derives `0079f284` and `0079f280` from an x87 sequence involving DWORD `007cdac8`, float constants `0053bdfc` and `0053bdf8`, and the truncated text coordinates (`00494f42–f73`). It does not use Modern's explicit `448.0` and `10.0` bound expressions or its `[EBP+0x4a] * 1/64` write.

The old x87 stack sequence is preserved in the capture, but the complete meaning of its two progress globals depends on the unverified contract of `004d1000` and associated renderer state. Accordingly, this comparison does not translate these globals into a progress-bar width, fill direction, or screen location.

## Retained evidence

Run `python3 analysis/scripts/audit_loading_artwork_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-loading-artwork.json) records full matched initializer spans, helper preservation/rounding witnesses, binary identities and exact float constants. Raw assembly remains ignored under `analysis/captures/modern-differences/loading-artwork/`.

## Limits and evidence

The address spans above were checked in raw `objdump -d -Mintel` captures made from the two hash-pinned executables. The Modern-only prior notes at [detailed analysis](detailed-analysis-notes.md#tiled-loading-artwork-and-progress-bounds) report the same staging-raster size and Modern tile origins, but that earlier note describes a different installed Modern hash; the claims in this report are rechecked against the official archive binary named above.

The callers in the existing Ghidra notes invoke this routine from `LoadAndRenderRaceLoadingArtwork` at `0049512d` and `0049513e`; this report does not re-identify or validate their runtime reachability. Tile object layout, whether the helper inputs represent texels or another unit, the loaded image dimensions, clipping, renderer behavior, allocation failures and final display are unresolved. No game, graphics backend, probe, or test was run; no executable or Ghidra project was modified.
