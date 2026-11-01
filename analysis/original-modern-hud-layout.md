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

The local layout established by these writes is therefore **0x24 bytes of header plus 24 × 16-byte rectangle storage = 0x1a4 bytes**, six records. This does not establish semantic names for every header field or rectangle slot. It also does not prove which installed original `*def.pos` contents the embedded table was derived from. The [reference-asset comparison](original-modern-reference-assets-index.md#hud-coordinate-literal-comparison) now compares six author-hosted variants numerically; none matches the embedded table exactly. Authenticated installed-original provenance and runtime parser equivalence remain unverified.

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

The later [map-scale consumer comparison](original-modern-map-marker-scaling.md#profile-scale-defaults-reach-map-zoom-independently-of-marker-extents) now establishes the +10h field's map-zoom use and cop/racer variant linkage. It narrows that earlier field-identity limitation without proving persisted-state or rendered coverage.

## Catalog traceability and remaining work

This chapter supplies concrete evidence relevant to **MP140-071/072/073** and **MP100-030/032/033**, whose notes discuss HUD positions, reset behavior, map zoom and units. It does not fully verify them: remaining consumer-to-field mappings, authenticated original preset provenance, first-install/reset admission and persistence overrides still need inspection. Those entries remain vendor-claimed or only partially supported as appropriate.

Next: reuse the [ordered reference-asset/table comparison](original-modern-reference-assets-index.md#hud-coordinate-literal-comparison), qualify target parser and extra-slot behavior, map the nine header fields and rectangle slot consumers, and trace migration/reset triggers before claiming that an existing player's HUD is automatically reset. Preserve the shared-frame and x87 contracts during future reconstruction.

## Reference-dimension consumers in scale, standings and layout updates

Three further complete same-address function comparisons are now reproduced by [the HUD reference-consumer audit](scripts/audit_hud_reference_consumers.py), with pinned executable identities, full span hashes and disassembly locations in [its manifest](evidence/audits/hud-reference-consumers.json). Each envelope is byte-identical except the reads listed below.

| Saved Modern entry / label | Complete envelope, exclusive end | Changed reads |
|---|---|---|
| `00484b70` InitializeHudScaleFactors | `00484b70..00484c10` (160 bytes) | `00484b7a`: MOV EAX source `007cdac8`→`007a2748` |
| `0048ae70` RenderRaceStandingsList | `0048ae70..0048b29f` (1,071 bytes) | `0048ae87`, `0048aea0`: FILD source `007cdac8`→`007a2748`; `0048aecb`: FLD binary32 `0055d6bc`→FILD signed DWORD `007a274c` |
| `0048d110` UpdateHudLayoutGeometryForView | `0048d110..0048d4b3` (931 bytes) | `0048d40a`: FILD source `007cdac8`→`007a2748` |

The [viewport geometry comparison](original-modern-viewport-geometry.md#2-new-centred-43-reference-rectangle) already verifies Modern's `{x,y,width,height}` record at `007a2740`: `007a2748/+4` are its integer reference width/height. For ordinary 1920×1080 dimensions that producer yields reference width 1440 and height 1080. This is a static formula example, not a captured HUD result. These consumers therefore do not simply switch to the full configured display width.

The scale initializer retains its signed comparison against 640 and the two existing branches. Below the threshold it writes the fixed binary32 scale values through `00791b3c`, `00791b54`, `00791b4c`, `00791b50`; at/above it computes scales using the chosen width and existing instructions. Changing the width source can change both branch admission and arithmetic inputs without changing that code.

### Scale initializer also reads a changed base coefficient

The extended reference-consumer audit records16 bytes at `0053b620`. Original's first binary32 is **0.0015625000232830644** (the binary32 approximation to1/640); Modern's is **0.0017000000225380063**. The following three values, approximately0.8, approximately0.6 and exactly0.5, are unchanged. The width-at-least640 branch of `00484b70` uses the changed coefficient, so the code's retained arithmetic has both a changed width source and a changed file-backed constant as dependencies.

For equal ordinary input width, this coefficient alone raises the unrounded base by approximately8.8 percent. That is an arithmetic comparison, not an observed font-size change: Modern's reference width can differ from original's source width, individual binary32 stores round, and later state can override the initialized scales. The below640 branch instead uses its fixed constants. The [gear-label analysis](original-modern-numeric-scale.md#gear-label-release-claims-bounded-alignment-and-smaller-scale-evidence) connects primary/fallback scale destinations to a concrete consumer.

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

## Variant transition changes one profile-header float from 4 to 3

The expanded [HUD audit](scripts/audit_hud_reference_consumers.py) now also compares the complete same-address helper `0048e790..0048e91b` (395 bytes), saved as `CycleHudVariantViewportModeForView`. Its sole differing byte is at `0048e8e3`, inside the immediate DWORD store at `0048e8da`: original bits `40800000` (binary32 4.0) become Modern `40400000` (3.0). The [manifest](evidence/audits/hud-reference-consumers.json) records the complete spans and qualifies this separate constant change.

Both derive a group from incoming view index plus one when session `006fd3b0 == 1`, and a variant from object byte `+200` bit `20h`, obtained through `00422bd0`. The selected profile is based at `006fbc50 + group*348h + variant*1a4h`; this uses the same 1a4-byte profile layout documented earlier. They select rectangle slot 17 or 22 according to that variant. Nonzero incoming view indices bypass transition work unless session equals 1.

The changed store occurs only in the retained branch where profile DWORD `+20` equals 1, the selected rectangle's `+4` binary32 bit pattern is either signed zero (`TEST ... ,7fffffffh`), and its `+0c` bits equal positive 1.0. The branch writes profile state `+20=2`, restores the rectangle's four DWORDs from the saved rectangle area, then stores the changed float into profile header `+10`. Thus the change is **4.0→3.0 in one header field during this branch**, not a new integer state value or a universally changed default.

Other branches remain byte-identical: the initial zero-state path creates a rectangle and stores 1.0 into the same header field; a non-1 state becomes 1; failing the stated rectangle tests can set state zero. The subsequent calls `00481f90`, `004853c0`, `004844c0`, `0048ccf0` and the indexed store at `007925d0` retain their order and operands. Their transitive effects are not proven equivalent merely by these retained calls.

**Bounded work status: done; confidence: verified static complete body and conditional value change.** The semantic role of profile `+10`, every field producer and the visible transition remain unresolved. Reconstruction should preserve the float bits, signed-zero test and branch conditions rather than infer a scale/animation interpretation from the constant alone. No game, instruction probes, Ghidra writes or C edits were performed.

## Initialized-data reuse: old rectangle table cleared, new presets occupy old strings

The expanded HUD audit verifies the entire original auxiliary rectangle table `0055d454..0055d694` (**576 file-backed bytes**) and records its original/Modern hashes and file offsets. Modern contains **576 zero bytes** at this location. This is explicit initialized-file content, not a claim about loader-zero-filled BSS or the value after startup. The [initialized-data inventory](original-modern-initialized-data-index.md) identifies it as the largest contiguous changed run in that section.

Original's rectangle-copy path uses this table through the LEA operand at `00485810` (instruction starts `0048580e`). A full executable-file search finds exactly that one literal encoding of base `0055d454` in original and none in Modern. This corroborates removal of the direct table-base reference alongside the initializer rewrite; computed/interior references and later writes remain outside that bounded search. The former storage is not declared globally dead or safe to repurpose by a future port.

Modern's replacement preset table `0053eb20..0053f420` instead overlaps storage used for original renderer names and diagnostic messages. As a concrete identity witness, original `0053ebb8` contains `nulla.dll`, while the same address lies inside the Modern numeric preset table whose producer/consumer was traced above. The old text and new numeric data are version-specific objects, not aliases of one reconstructed structure. Finding different values at these addresses must not be interpreted as a simple update to the same field.

**Status: file-backed storage change and direct-base reference search done; confidence: verified static.** This addition explains data ownership at the two table locations, not derivation of every embedded coordinate from original `*def.pos` assets, complete runtime initialization, or visual equivalence. No game, probe, executable or Ghidra modification was performed.

## Default speed units: header selector reaches the digital KPH path

Run `python3 analysis/scripts/audit_speed_unit_default_difference.py` alongside the HUD initializer audit. The [speed-unit evidence](evidence/audits/speed-unit-default-difference.json) pins paired consumer `0048384a..0048395a` and complete formatter `00489d70..00489df7`; both spans are byte-identical between original and official Modern. This adds consumer evidence to header offset `+18`, rather than guessing its meaning from defaults alone.

The consumer indexes `006fbc68` with `348h*bank + 1a4h*profile` (two profile strides per bank). Selector values2 or4 enter another display branch. Values1 or3 enter the inspected digital-formatting branch. There, the selected profile value1 or2 produces an argument1 to formatter `00489d70`; other values produce0. Consequently, admitted digital selector1 takes the nonzero formatter path, while admitted digital selector3 takes the zero path. Input bank/profile validity remains an external precondition.

The nonzero formatter path obtains language ID`156h` and multiplies input speed by binary32 **2.2369000911712646** from `0053b83c`; the zero path obtains ID`157h` and multiplies by binary32 **3.5999999046325684** from `0053b840`. The pinned official English language member identifies those IDs as **MPH** and **KPH**, respectively. Both paths call `004dfd56` before FISTP; identical caller instructions do not establish equal rounding or floating-point state because that helper differs between versions, as covered by the [precision comparison](og-modern-x87-precision.md). No numeric output equivalence is implied.

Combined with the independently audited defaults above, Modern's **all3** header initialization selects the digital **KPH** branch on this route. Original initializes all six headers to **1 when `006fbb4c == 0`, otherwise3**: its zero-selector default takes MPH, and its nonzero-selector default already takes KPH. Modern therefore removes that dependency at default initialization; this is not a newly implemented speed-conversion formula in the inspected formatter. Official English labels are evidence of the named branches, not proof which language member is loaded at runtime.

**MP100-030: partial static support.** The default-to-digital-consumer chain is established. Saved settings, later edits, active profile selection, the alternative selector2/4 display branch, actual rendered output and historical introduction remain unverified. Do not generalize this bounded result to every speedometer or overwrite user preferences during reconstruction.

### Alternative selector2/4 branch: geometry is retained, calibration remains separate

The extended speed-unit audit now compares complete geometry helper **`0048a220..0048a317`**,247 bytes, and its five file-backed scale/offset constants at `0053b87c..0053b890`. The helper and constants are byte-identical in original and official Modern. The already paired caller admits selectors2/4 to this helper at `00483895`, supplying view index in EAX, a binary32 speed-magnitude argument and raw payload `ffffffffh`. Selectors1/3 instead enter the digital branch described above.

The alternative helper does not receive the unit selector. It forms a binary32 angle from `value * float[0053b87c] + float[0053b880]`, then calls trig/geometry helpers and writes the indexed geometry. It does not call the localized MPH/KPH formatter or apply its `2.2369`/`3.6` conversions locally. The same input magnitude is used for selector2 and selector4 at this callsite. Therefore the numeric pointer geometry alone cannot distinguish their unit calibration; the separate dial texture/label setup and subsequent draw consumers must be established before naming a complete analog-unit enum. Identical helper bytes also do not prove unchanged indirect state, trig dependencies or FPU precision.

This reuses the prior [indicator contract and bounded live sample](detailed-analysis-notes.md#per-view-hud-indicator-geometry-update), adding the missing original/official static comparison. That older sample concerned one existing analysis build and is **not** an original-versus-Modern equivalence test. It does not validate the claimed default behavior, complete dial calibration or high-speed rendering in both versions. No new runtime probe was performed.

## Author-reference HUD assets compared numerically

The [asset audit](scripts/audit_reference_asset_pairs.py) pins both archive hashes and the Modern EXE, parses all138 ordered records in each of six reference POS files and compares23 rectangles per profile against the embedded24-rectangle profile layout. Names/order agree across the six files. English has91 changed rectangles and352 differing binary32 coordinate fields; the other language variants have91–95 changed rectangles and352–365 differing fields. None supplies an exact numerical match.

This narrows the earlier asset-acquisition gap without authenticating pristine retail or identifying the author’s source. Comparison uses ordered coordinate literals and host decimal-to-binary32 conversion; it does not execute the original tokenizer/parser or prove final destination state after pair swapping, extra-slot initialization and aspect adjustment. The extra24th rectangle, header settings, persistence and rendered effects are excluded. Full per-profile changed-name lists are retained in [the manifest](evidence/audits/reference-asset-pairs.json).

## Fitted reference scales reach a conditional text path

**Confidence: verified static producer/consumer linkage; examples are derived. Work status: done for this bounded path, partial for MP100-004’s general font-size claim.** The expanded [reference-consumer audit](scripts/audit_hud_reference_consumers.py) now retains twelve complete paired bodies and verifies three more are identical: adapter`00451530..00451585` (85 bytes), bitmap scale setter`004d1390..004d13f3` (99), and bitmap font loader`004d0d50..004d0ff9` (681). The [manifest](evidence/audits/hud-reference-consumers.json) records exact gates, source addresses, threshold bits and ordinary reference-width examples. No fonts or target instructions were rendered/executed.

The existing paired initializer`00484b70` changes its scale input from actual width`007cdac8` to fitted reference width`007a2748`; the independent coefficient change at`0053b620` also remains relevant. This pass closes a specific downstream use of those scales:

| Adapter condition / ordinary ordered requested scale | Source forwarded to bitmap scale setter |
|---|---|
|`00559234==0` | Incoming scale argument unchanged |
| Nonzero gate, request>=1 |`00791b50` |
| Nonzero gate, request<1 but at least retained binary64 threshold0.6 |`00791b54` |
| Nonzero gate, request below that threshold |`00791b4c` |

These three globals are written by the audited scale initializer. The retained text adapter pushes the chosen scale, calls`004d1390` at`00451578`, and discards that setter’s old-value ST0 result. Thus the changed dimension/coefficient inputs can reach a concrete text-scale consumer; this is not merely a numeric change in unused data. The helper uses x87 comparisons and branches: on a nontrapping unordered first comparison it selects`00791b50`, not the ordinary below-threshold arm. Requested NaNs/exceptions and ambient precision remain distinct from the ordinary table above.

### Why height matters on the wide branch

The [reference-rectangle producer](original-modern-viewport-geometry.md#2-new-centred-43-reference-rectangle) gives the width source its meaning. For ordinary positive dimensions on the wide branch, reference width is`trunc(4*height/3)`. On the narrow/tall branch it remains actual width. It is therefore a **fitted4:3 reference policy**, not an unconditional replacement of every width read with height.

For the width>=640 arithmetic branch, the initializer’s base scale is input width times its version’s binary32 coefficient. The unrounded examples are:

| Display | Original input width | Modern reference width | Original unrounded base | Modern unrounded base, approximate |
|---|---:|---:|---:|---:|
|1920×1080 |1920 |1440 |3.0 |2.448 |
|2560×1080 |2560 |1440 |4.0 |2.448 |
|1280×1024 |1280 |1280 |2.0 |2.176 |

The equal-height wide examples keep Modern’s input/base equal while original grows with width. The tall example also shows why this must not be described as universally smaller fonts: the retained width branch and changed coefficient can increase the base. Individual binary32 stores, selected multiplier, font state, caller scale, mode/reference freshness and rendering determine actual glyph size. These are arithmetic examples, not pixel measurements or instruction-equivalence tests.

### Retained width-based bitmap behaviour limits the headline

The separate [bitmap-font investigation](original-modern-car-alias.md#scale-initialization-and-setter-are-retained) remains valid: when font flag`00840188==0`, the setter accepts the supplied scale; when nonzero, it selects a font variant and computes scale from **actual width`007cdac8` times the retained approximately1/320 coefficient**, rather than the supplied scale itself. The complete loader also still chooses its FFN file set using signed actual width>=640. Both bodies are identical in original and final.

Accordingly **MP100-004 receives partial static support for the fitted-reference→scale→conditional-text route**. This review does not establish a universal height-based rule for all menu, atlas, bitmap and HUD fonts, nor that every widescreen label avoids excessive size. Other font-selection paths, historical1.0.0 introduction and visible output remain follow-up requirements. Preserve the chosen version’s scale sources and both gates in reconstruction; globally replacing width with height would alter retained behaviour that this comparison has not shown the patch changed.

## Opponent Name and List have distinct profile defaults

**Verified named bindings, static defaults and selected conditional consumers; rendered visibility untested.** The [opponent-default audit](evidence/audits/opponent-hud-defaults.json), reproduced with `python3 analysis/scripts/audit_opponent_hud_defaults.py`, retains both complete default initializers and two paired consumer spans. It resolves previously offset-only fields+04/+08 by12 named20-byte descriptors, shared in both EXEs:

- `opponentName`, `opponentNamecop`, `opponentName1`, `opponentNamecop1`, `opponentName2`, `opponentNamecop2` bind header+04.
- The corresponding `opponentList*` descriptors bind header+08.
- All use the same two-entry choice-ID list at`005561be`; Name and List are distinct settings, not alternative names for one storage cell.

| Profile suffix | Original Name/List defaults | Final Modern Name/List defaults |
|---|---|---|
|`1` racer |1 /0 |0 /1 |
|`2` racer |1 /0 |0 /1 |
|`cop1`, `cop2` |0 /0 |0 /0 |

These match the six-profile header table above. Original writes the racer Name fields at`004858c5/004858cb` from retained literal1 in EDX, then zeroes EDX at`004858e0` and writes their List fields at`004858fa/00485900`. Modern zeroes ECX/EDX and increments EDX at`00485886..0048588b`, writes Name fields from ECX at`004858bb/004858c7`, and List fields from EDX at`004858df/004858eb`. Original helper preservation supporting the literal1 is already established in the earlier default-header analysis.

The complete bounded consumers `00482dcd..00482e6f` (162 bytes) and `00483614..004836c4` (176 bytes) are byte-identical between versions. They read selected header+08, skip their list branches when zero, and otherwise separate a nonzero role-local route to`0048a660` from a zero-role route that additionally requires signed`005efda0>1` before calling standings renderer`0048ae70`. This establishes an admission effect, not unconditional display. Full profile/session index production, all caller paths and other drawing gates remain separate. These are complete captured branch spans, not claims to complete parent-function boundaries.

**MP100-033 advances to partial support:** the named racer profiles change from Name enabled/List disabled to Name disabled/List enabled, consistent with the split-screen-default claim. The cop profiles do not receive the same default swap. Suffix-to-live-view/session admission, saved preferences, actual rendered layout and1.0.0 introduction remain unverified. Do not expand the release note into every role/context or infer that either renderer was removed. The separate standings/font/reference-dimension changes above still affect output after admission. No game, HUD draw, instruction probe or Ghidra write was performed.
