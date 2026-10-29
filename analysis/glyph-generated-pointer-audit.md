# Generated glyph pointer arithmetic audit

## Finding

For the installed `TEST.GF`, the generated-path vertex-normal pointer discrepancy is **in-bounds but misbased**, rather than an out-of-allocation pointer. In `00475a1e`, the consolidation loop uses the final processed glyph's doubled vertex count for every glyph's vertex-normal pointer. For this asset that count is 20. The resulting `12*20` byte offset keeps every nonempty glyph's normal range inside that glyph's packed segment, but it does not select the intended vertex-normal array for 83 of 87 nonempty glyphs:

- 58 glyphs with `V > 20`: the pointer begins inside that glyph's position array.
- 25 glyphs with `0 < V < 20`: the requested range extends into that glyph's triangle/index-and-face-normal payload. Of these, 18 pointers begin inside the correct vertex-normal region; 7 begin after it.
- 4 glyphs with `V = 20`: the pointer is correct by coincidence.
- 3 empty glyphs: the generator's zero-count branch does not form a nonempty normal range.

This is a static pointer/layout finding. It does not establish that the generated branch runs for this installation, that its returned buffer is consumed, or that a visible rendering defect occurs.

## Scope and evidence

The target was the local shipped `nfs3.exe` at `nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. REA's owned analysis session for this target was closed after inspection. No executable, runtime process, or persistent Ghidra project was modified.

The primary instruction evidence is the full `00475240` procedure analysis `ev_58fcad83d9bf91a61cf537c8a5bb842a6d23690a08bcf64c8336ad656558151e` (body `00475240..00475b07`). Focused original-instruction observations include:

| Address | Instruction role | Evidence |
|---|---|---|
| `004753d0` | Doubles source vertex count into `V` | `ev_7f2fe84877e435e40fa3cd5488610b796ab30ca143eef9d387ccc9018db29f15` |
| `004753e1` | Saves current `V` at `[EBP+0x4a]` | `ev_2fa38191b53a81b836141adcef9a8bb6b617950d531f23842468563aa15a620c` |
| `00475404` | Calls allocator for per-glyph staging | `ev_74724c62519112acbce108ad8b836f739ce5c114da0e8f3136c36ac28902bc66` |
| `00475417` | Stores staging positions pointer in descriptor `+0x20` | `ev_8095b7e59d31d8db16bc062e14ccd2d38b0d9dc92d6ac73733b84158ddd7a612` |
| `00475426`, `0047543a` | Forms the `12*V` offset and staging vertex-normal pointer | `ev_e67af427241d4343a22f9aa976f005b0a94abe16db7129648a3685591892a1aa`, `ev_852859667c7fa5540a4bff85b70bbd1fc1cc34d5dde8ebd686aff5a12b7dd222` |
| `0047596a`, `00475977` | Loads total packed size and allocates final resource | `ev_435760751217e11f25248e21691fbb938879aaa0e59a49631f70a0478a32da8c`, `ev_934c9e3d9b96e0c87ce43f50421bca6f9730d81c4e3502173fbe174f00d2953` |
| `00475a1e` | Loads the saved final `V` during consolidation | `ev_f22119a06eb5921664e3f106545bb51b72c8e80b67a9ca2d60d79882f6cd5203` |
| `00475a30` | Stores current descriptor's positions pointer | `ev_75bf864e46643a1e9be2ede658273106e03c9f26548f75c2b107da68aeb2af92` |
| `00475a33`, `00475a38` | Adds `12*Vlast` to current cursor and stores descriptor `+0x28` | `ev_84453fb08248ce05d2d5ec90e581827329651986764254f9047e8953491437e7`, `ev_5ca5839bc014381ae0a4091fed4b05d9410e61fc5b8305077601c317b88361e9` |

The asset corroboration uses the retained static inventory [installed-glyph-geometry.json](evidence/inventories/installed-glyph-geometry.json), produced by [inventory_glyph_geometry.py](scripts/inventory_glyph_geometry.py), plus a sequential parse of the installed source `GAMEDATA/RENDER/PC/TEST.GF` using the source reads and count rules visible in `00475240`. The corresponding asset notes are in [detailed-analysis-notes.md](detailed-analysis-notes.md), under “Glyph cache-versus-generation pointer discrepancy” and “Glyph renderer: installed cached-geometry admission.”

Installed source identity: `TEST.GF`, 15,941 bytes, SHA-256 `30f154f35718eb648615ba043d445a4cdb5cbb2b6f02329bd24ded3828ffd36a`. Installed cache identity: `TEST.GFX`, 162,852 bytes, SHA-256 `b56f7d49ee6def17a9d8d67aef39292c3b535eeddfb5bc0c794e5ffd7c81e5c2`. The source record walk reaches exact EOF after 90 glyphs, codes 33–122; its source base-vertex and flat-triangle counts match the cached inventory. The final record is `z` (code 122), with 10 base vertices and `Vlast=20`. This matching inventory is not evidence that the on-disk cache is generated during the observed run or byte-for-byte equivalent to a live generated buffer.

## Producer and allocation constraints

The generator records source base vertex count `N` and flat triangle count from the current GF record. It doubles `N` into a byte-sized descriptor count `V` (`004753d0`, `004753e1`); installed records have `N <= 40`, so all installed `V=2N` values fit in one byte. The normal staging pointer is constructed at `staging + 12*V`; positions and vertex normals therefore occupy `12*V + 12*V = 24*V` bytes. The focused allocation sequence at `004753fa..00475404` computes this staging size before calling allocator `004e1620`.

Generated output also carries `T` triangle records. The final packed allocation size is assembled as `0x2010 + Σ(24*V_i + 15*T_i)`: `3*T` index bytes and `12*T` face-normal bytes account for the `15*T` term. The size is passed to allocator `004e1620` at `0047596a..00475977`. Consolidation copies the current glyph's `24*V_i` vertex bytes and advances the cursor by that current-glyph extent; the stale final-glyph count is used only for the `+0x28` pointer calculation. Triangle/index and face-normal pointers and cursor increments are formed from each entry's own triangle count in the same procedure.

The generator has no visible local allocation-result checks at these calls. Source parsing also does not establish general input safety: the static notes record no source-end bound, descriptor-range check, general byte-count admission, or per-source-triangle index validation. The conclusions below are bounded to the installed, fully parsed source and the counts observed in its matching installed inventory; they are not a proof for arbitrary or modified GF files.

## Exact pointer ranges for the installed geometry

The cached inventory reports 90 glyphs, 2,946 total packed vertices, 5,596 triangles, and exact payload end at byte 162,852. It also reports the three empty records: apostrophe (39), comma (44), and hyphen (45). For the installed asset:

| Quantity | Bytes |
|---|---:|
| Header and descriptor area | `0x2010` = 8,208 |
| Positions plus vertex normals, `Σ24*V` | 70,704 |
| Triangle indices plus face normals, `Σ15*T` | 83,940 |
| Final packed allocation | 162,852 (`0x27c24`) |

These values satisfy `8,208 + 70,704 + 83,940 = 162,852`, matching both the final allocation formula and the inventory's exact cache payload extent. Per-glyph segment boundaries were taken from the inventory's sequential packed layout; for each nonempty glyph `i`, let `S_i` be its segment start, `E_i=S_i+24*V_i+15*T_i`, and `Vlast=20`.

The generated path stores:

```text
positions_i       = S_i
vertex_normals_i  = S_i + 12*Vlast = S_i + 240
normal_range_i    = [S_i + 240, S_i + 240 + 12*V_i)
```

The correct per-glyph normal range would instead start at `S_i+12*V_i`. Exhaustive arithmetic over all 90 inventory records gives:

- **0 of 87 nonempty glyph normal ranges extend beyond `E_i`.** Thus none reaches a neighboring glyph segment or exceeds the final packed allocation for this installed geometry.
- For `V_i > 20`, the range ends at `S_i+240+12*V_i <= S_i+24*V_i`, so it lies within that glyph's position-plus-normal region, beginning too early in position data.
- For `V_i < 20`, the range end exceeds `S_i+24*V_i`, so it extends into that same glyph's triangle/index-and-face-normal region. Among these 25 glyphs, 18 range starts fall within their intended vertex-normal arrays and 7 start after those arrays. The minimum remaining margin to the glyph segment end is 36 bytes, for code 46 (`.`), with `V=8`, `T=12`.
- For `V_i=20`, `S_i+240` equals the intended normal start.

The “inside segment” result is a byte-extent proof only. It does not establish that these bytes are valid vertex normals or that downstream code interprets the overlapped payload as vectors safely.

## Cache reconstruction comparison

On the cache-hit path, `004752b4..004752cb` uses each current descriptor's own byte `+3` (`V_i`) to set its normal pointer to `cursor+12*V_i`; it then advances past `24*V_i`. This is the per-glyph layout implied by the staging allocation and used in the extent arithmetic above. The packed on-disk GFX file stores records and payload, not these process pointers. Its descriptor bytes cannot expose which formula was used to build a prior in-memory resource.

## Remaining runtime requirement

To establish live impact, a controlled run must force the cache-miss generation path with this exact installed `TEST.GF`, capture the returned resource base and allocation extent, and read back each nonempty descriptor's `+0x20`, `+0x28`, `+0x2c`, and `+0x24` pointer/count fields. Compare each address and accessed span against the current glyph segment and the `12*V_i` expected normal start; then establish that a real consumer reads the generated `+0x28` range before release. This would prove path selection and consumption, which static file identity and the cached loader do not. A visual claim would additionally require a controlled rendered result tied to that resource. No such runtime capture was made for this audit.
