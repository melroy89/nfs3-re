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

## Pixel conversion removes explicit truncation before FISTP

The complete helper `00480910..004809f7` (231 bytes, exclusive end), saved as `ScaleHudLayoutSlotToViewportPixels`, differs only at four five-byte calls: `00480999`, `004809a3`, `004809aa`, `004809b3`. Original calls `004dfd56` at each; Modern substitutes a short jump over three NOPs. [The audit](scripts/audit_hud_pixel_rounding.py) verifies the entire body, decoded call targets, replacement bytes and retained conversion instructions; [the manifest](evidence/audits/hud-pixel-rounding.json) retains both bodies and original/Modern rounding-helper witnesses.

Original `004dfd56` saves the control word, changes its temporary high byte to `1fh`, loads it, executes FRNDINT and restores the saved control word. The temporary rounding-control bits are `11`, toward zero. It leaves an integral floating-point value in ST0, rather than returning an integer in EAX. The original HUD caller applies this helper to each of its four calculated x87 values before the eventual integer stores.

Modern removes these four calls entirely. Both versions retain FISTP DWORD conversions at `004809bd`, `004809c5`, `004809d3`, `004809df`, followed by stores to the selected record based at `00749758`, `00749760`, `0074975c`, `00749764`. The source calculations, x87 exchanges, address arithmetic and stores are otherwise byte-identical. Modern's helper implementation at `004dfd56` still exists, but its revised temporary word `0c3fh` is irrelevant to these four removed calls: it is not invoked here.

For ordinary finite results representable in signed 32 bits, original first truncates toward zero, then converts the resulting integral value. Modern converts the untruncated value according to the **active** x87 rounding mode. Conditional mathematical example: with round-to-nearest active, 1.75 converts to 1 in the original sequence and 2 in Modern; −1.75 converts to −1 versus −2. These are consequences of the instruction contracts, not executed probes or measured HUD coordinates. If active rounding is already toward zero, that ordinary-value difference disappears. Exceptional values, precision exceptions, pending unmasked exceptions and status bits require separate treatment.

The 219-byte Modern saved body union excludes the twelve NOP bytes and reports eight changed in-body bytes. The full envelope includes all twenty changed bytes. Do not equate the saved-body count with complete coverage of removed rounding calls.

**Bounded work status: done; confidence: verified static instructions; conditional numerical consequences derived.** A C cast truncates toward zero and would not represent Modern's general current-rounding-mode conversion contract. Reconstruction must preserve or explicitly emulate the selected semantics and the four-value operation order. Caller control-word state, actual layout values, pixel comparisons and machine-state equivalence remain unverified. See the broader [x87 comparison](og-modern-x87-precision.md) for why this local conversion policy is distinct from arithmetic precision control.

## Additional consumers distinguish fitted and corrected overlay rectangles

The [reference-consumer audit](scripts/audit_hud_reference_consumers.py) now verifies five additional complete same-address functions. For each, replacing exactly the listed reads (plus one constant below) in original bytes reproduces the complete Modern envelope. The expanded [manifest](evidence/audits/hud-reference-consumers.json) records every new read's instruction address, old opcode/source and Modern source.

| Saved Modern entry / label | Complete envelope, exclusive end | Verified read changes |
|---|---|---|
| `004800a0` RefreshHudVisibleRectangleQuadsForView | `004800a0..004808af` (2,063 bytes) | `00480187`: signed FILD width `007cdac8`→`007a2748`; one additional quad constant below |
| `00487210` StoreAndInsetIndexedFloatRectangle | `00487210..0048733c` (300 bytes) | Four FILD reads at `00487238`, `00487251`, `00487284`, `004872b3`: `007cdac8`→`007a2748` |
| `004880b0` RenderVehicleDrivenRotatedQuads | `004880b0..00488470` (960 bytes) | `004880c7`: `007cdba0`→`007a2758`; `0048818d`/`0048832f`: `007cdb98`→`007a2750`; `004881a4`/`00488346`: `007cdb9c`→`007a2754`; all remain signed FILD |
| `0048a660` RenderPolicePursuitStatusList | `0048a660..0048aa3e` (990 bytes) | `0048a670`, `0048a714`: signed FILD width `007cdac8`→`007a2748` |
| `0048aa40` CalculateHUDStandingsColumnWidths | `0048aa40..0048ae69` (1,065 bytes) | Two width FLD→FILD changes, two width source-only FILD changes, one height FLD→FILD change |

For the column-width function, original `0048ab47` and `0048abfa` load binary32 `0055d6b8`; Modern loads signed integer reference width `007a2748`. Original `0048ac53` loads binary32 `0055d6bc`; Modern loads signed integer reference height `007a274c`. The other two reads at `0048ac06` and `0048ae0f` retain FILD but change width address. These type changes matter even when the intended mathematical dimensions are equal: float bits are not integer dimensions.

The rotated-quad function uses a **different group** from the fitted width/height consumers. Existing [overlay producer evidence](original-modern-viewport-geometry.md#overlay-rectangle-at-007a2750-separate-derived-extent-correction) establishes corrected `{x,y,width,height}` at `007a2750..007a275f`, separate from fitted group `007a2740..007a274f`. Its changed sources are therefore corrected overlay X, Y and width. Applying the fitted 4:3 formula indiscriminately to both groups would misrepresent these consumers. Initialization and later resize/update lifetime remain governed by their separately documented producers.

The visible-quad refresh function also changes the immediate store at `00480831`: DWORD record `+3c` receives bits `3f450000` instead of `3f440000`, i.e. binary32 0.76953125 instead of 0.765625. This exact +0.00390625 value change is independent of the width-source replacement. The field's draw-contract meaning is not established by this store alone; it is not labelled a depth/texture-coordinate fix without a corresponding consumer trace.

**Bounded work status: done for these five complete code comparisons; confidence: verified static reads, opcodes and constant bits.** Their unchanged instructions can still consume different metrics, buffers and x87 state. Remaining scope is consumer field semantics, source freshness, full alias/caller domains and rendered standings/pursuit/quad behavior. No game or instruction probes were executed, and executables/Ghidra/reconstruction sources remain unchanged.
