# Original versus Modern: HUD preset source and default records

## Scope and evidence

**Static initialization comparison; no rendered HUD validation.** Supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`; official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline](original-modern-differences.md).

Run `python3 analysis/scripts/audit_hud_layout_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-hud-layout.json) records input/span hashes, original filename/token formats and Modern embedded-preset provenance. Raw assembly remains ignored under `analysis/captures/modern-differences/hud-layout/`. No executable, Ghidra, game or instruction-probe changes.

The matched pair is preset initializer `00485680`, followed by default-header initializer `00485880`, which calls it in both binaries. Ghidra's Modern function boundary at `0048582c` is a shared-frame continuation, not a standalone callable ABI; capture includes its real return/unwind.

## 1. File-sourced presets become embedded data

Original `00485680`:

- Selects a character using `[006fbb4c]` and byte table `0047bbb8` (`egfsiw` plus NUL).
- Formats `%s%cdef.pos` using prefix pointer `007a29b4` and that character, then calls loader `004e0ec0` at `004856cd`. Prefix and locale admission are not re-established here.
- If load returns null, branches directly to the common epilogue `0048586d`.
- Otherwise tokenizes using delimiter literal `: -(,)`, parses name/float tokens, and writes 23 rectangle slots per profile across three groups of two profiles. The nested bounds are visible at `004856ef/004857b2/004857bf`.
- Copies a separate four-DWORD slot from table `0055d454` into the last rectangle area of each profile (`004857d6..0048582a`), then enters the shared refresh tail.

Modern replaces that file/token route with a **file-backed embedded table** at `0053eb20`, consuming **0x900 bytes**: six profiles × 48 pairs of DWORDs. It swaps the two members of each pair into destination `+4/+0`, advances 8 bytes, then skips the next profile's 0x24-byte header. Each destination is at `006fbc50 + profile*0x1a4`.

The local layout established by these writes is therefore **0x24 bytes of header plus 24 × 16-byte rectangle storage = 0x1a4 bytes**, six records. This does not establish semantic names for every header field or rectangle slot. It also does not prove which installed original `*def.pos` contents the embedded table was derived from; an asset-to-table comparison remains pending.

No original preset-file read remains in this Modern initializer. This is a concrete source/initialization change, not proof that the whole game no longer reads external HUD/layout resources elsewhere.

## 2. Aspect adjustment and the retained shared-frame tail

Modern derives two x87 factors from DWORDs `006fd1e4/006fd1e8`. Producer `00448400` copies width and height from selected mode-record `+4/+8` to those addresses, and calls `00485680` if either changes. Let W/H denote those configured dimensions, C the binary32 literal `0x3faaaaab`:

- One retained factor is `0.75/(H/W)`.
- The other is `C/(W/H)`.
- Four calls to `00485718` at rectangle slots 1, 3, 6 and 8 (zero-based) adjust bounds at rectangle `+4/+0xc` using the second factor.
- One call to `0048573b` at slot 21 adjusts bounds at `+0/+8` using the first factor.

For the selected bounds, each helper forms extended delta `(hi-lo)*(1-factor)/2`, stores binary32 `lo+delta`, then binary32 `hi-delta`. The original hi remains available until its store; the extended delta is not reloaded from rounded float memory. Factors above one expand, rather than inset, the range. This is x87-sensitive arithmetic, not an instruction-equivalent replacement by a sequence of `float` operations.

Modern jumps at `00485713` into **unchanged bytes** at `0048582c..00485875`. That tail conditionally refreshes two views and 23 slots when `0055d440` is nonzero, then restores the parent frame and six saved registers. It is reached inside the initializer; exporting it as a normal isolated C function would invent an ABI. The previous [HUD helper contract](detailed-analysis-notes.md#internal-x87-hud-bounds-helpers-00485718-0048573b) already records the two required x87 inputs and preservation behavior.

Zero dimensions, exceptional x87 inputs and all saved-configuration producers are not validated by this path. No new runtime bounds or aspect test was performed.

## 3. Header default changes: preserve offsets, not guessed widget names

For records `P0..P5` at `006fbc50 + i*0x1a4`, the following DWORD stores are directly compared in `00485880`. Let **B** mean original renderer byte `007a3a58` bit 1 is set; let **L** mean original selector `006fbb4c` is nonzero. These symbols describe exact branch inputs, not a new classification of renderer or language behavior.

| Offset | Original P0..P5 | Modern P0..P5 |
|---|---|---|
| `+00` | `1,1,1,1,1,1` | Same |
| `+04` | `B?1:0, 0, 1, 0, 1, 0` | `0,0,0,0,0,0` |
| `+08` | `B?0:1, B?0:1, 0,0,0,0` | `1,1,1,0,1,0` |
| `+0c` | `B?0:1, B?0:1, 0,0,0,0` | First two are 0 if byte `007a3a58 & 6` is nonzero, otherwise 1; remaining four are 0 |
| `+10`, float bits | `4.0,1.0,4.0,1.0,4.0,1.0` | `3.0` in all six |
| `+14` | `3,3,3,3,3,3` | `3,0,3,0,3,0` |
| `+18` | All `L?3:1` | All 3 |
| `+1c` | All 1 | Same |
| `+20` | `1,2,1,2,1,2` | All 1 |

Original also sets `006fbbb8/006fbbbc` to 1 in this body; Modern has no corresponding local stores. Other initialization/persistence writers must be traced before inferring final values of those globals. The old preset helper preserves EDX, supporting original default initializer's retained literal 1 across its call; Modern initializes its zero/one registers after the helper returns.

These defaults can later be replaced by saved settings or user edits. The table is not a claim that all six profiles are always active, or that raw header offsets correspond to a named minimap/unit/widget field without consumer evidence. In particular, a modern value of 3.0 alone does not verify the vendor's complete minimap-zoom claim.

## Catalog traceability and remaining work

This chapter supplies concrete evidence relevant to **MP140-071/072/073** and **MP100-030/032/033**, whose notes discuss HUD positions, reset behavior, map zoom and units. It does not fully verify them: consumer-to-field mapping, actual original preset assets, first-install/reset admission and persistence overrides still need inspection. Those entries remain vendor-claimed or only partially supported as appropriate.

Next: compare original `*def.pos` assets to the embedded table; map the nine header fields and rectangle slot consumers; trace migration/reset triggers before claiming that an existing player's HUD is automatically reset. Preserve the shared-frame and x87 contracts during future reconstruction.

## Reference-dimension consumers in scale, standings and layout updates

Three further complete same-address function comparisons are now reproduced by [the HUD reference-consumer audit](scripts/audit_hud_reference_consumers.py), with pinned executable identities, full span hashes and disassembly locations in [its manifest](evidence/audits/hud-reference-consumers.json). Each envelope is byte-identical except the reads listed below.

| Saved Modern entry / label | Complete envelope, exclusive end | Changed reads |
|---|---|---|
| `00484b70` InitializeHudScaleFactors | `00484b70..00484c10` (160 bytes) | `00484b7a`: MOV EAX source `007cdac8`→`007a2748` |
| `0048ae70` RenderRaceStandingsList | `0048ae70..0048b29f` (1,071 bytes) | `0048ae87`, `0048aea0`: FILD source `007cdac8`→`007a2748`; `0048aecb`: FLD binary32 `0055d6bc`→FILD signed DWORD `007a274c` |
| `0048d110` UpdateHudLayoutGeometryForView | `0048d110..0048d4b3` (931 bytes) | `0048d40a`: FILD source `007cdac8`→`007a2748` |

The [viewport geometry comparison](original-modern-viewport-geometry.md#2-new-centred-43-reference-rectangle) already verifies Modern's `{x,y,width,height}` record at `007a2740`: `007a2748/+4` are its integer reference width/height. For ordinary 1920×1080 dimensions that producer yields reference width 1440 and height 1080. This is a static formula example, not a captured HUD result. These consumers therefore do not simply switch to the full configured display width.

The scale initializer retains its signed comparison against 640 and the two existing branches. Below the threshold it writes the fixed binary32 scale values through `00791b3c`, `00791b54`, `00791b4c`, `00791b50`; at/above it computes scales using the chosen width and existing instructions. Changing the width source can change both branch admission and arithmetic inputs without changing that code.

The standings prefix retains two signed-integer width conversions and its integer spacing conversions via FISTP. Its later dimension read is a **type/interface change**, not only a relocated global: original FLD interprets `0055d6bc` as binary32; Modern FILD interprets `007a274c` as signed 32-bit integer. A reconstructed global type or load helper copied from the original would misread Modern's height bits. The rest of this standings body remains byte-identical, including the call to font-scale helper `004d1390`; equal code does not establish equal font state, line spacing or pixel output.

The layout updater likewise retains the arithmetic following its one changed FILD. This audit verifies complete code differences, not every constant/data producer consumed by unchanged arithmetic. Existing width-source and reference-record research should be reused rather than assigning an unverified semantic name to every original global.

**Bounded work status: done; confidence: verified static reads and complete body differences.** Outstanding runtime scope is reference-record freshness after display changes, all callers, original height-state production, exact x87 rounding/exception behavior and rendered HUD comparisons. These changes support reference-rectangle integration at specific consumers; they do not prove all widescreen HUD layout is correct. No executable bytes, Ghidra database or maintained reconstruction sources were changed.
