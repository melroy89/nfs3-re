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

## Police list row and panel spacing use smaller data coefficients

**Verified static constants and direct consumers; rendered table untested.** The [police-spacing audit](evidence/audits/police-list-spacing.json), reproduced with `python3 analysis/scripts/audit_police_list_spacing.py`, pins supplied original/official final EXEs, both complete990-byte police-list renderer envelopes and selected layout/metric bodies. This extends the earlier width-source comparison with data changes that instruction-only diffing misses.

| Binary64 address | Original | Final Modern | Consumer |
|---|---:|---:|---|
|`0053b598` |20.0 |12.414 |Panel-layout metric at`00481cbe` |
|`0053b8cc` |20.0 |12.414 |Police-list row metric at`0048a70e` |
|`0053b5a0`, `0053b8d4` |Stored1/13 approximation |Identical |Following metric multiplier |

The panel route calls retained metric helpers `004d14f0` and `004d1540` with character code30h, adds their integer results, multiplies that sum by the first coefficient and1/13, then calls truncation helper`004dfd56` before FISTP. Its integer spacing is multiplied by the counted admitted entries at`00481cd5`; the later layout block consumes the resulting total. This is a panel-layout contribution, not a measured total panel height.

The renderer computes the corresponding metric through the second coefficient, stores the truncated integer at local`EBP-20h`, and at`0048a8c2..0048a8cd` adds it to the row coordinate in EDI after a text draw. The full renderer has only the six previously mapped changed bytes, in its two width-source operands; the metric multiplier instructions themselves are retained. Complete panel-metric span`00481ca0..00481cd8` and the65/67-byte font-metric bodies are identical between versions. The font helpers still read loaded bank tables and effective scale`0084018c`, so their code equality does not establish equal numeric metrics.

For equal ordinary positive input metrics, the **unrounded coefficient ratio is12.414/20 =0.6207**. This is not a guaranteed37.93% reduction in integer row spacing or displayed panel height: truncation, font bank/scale, actual entries, width-derived padding, clipping and x87 state remain dependencies. Integer count multiplication wraps at32 bits; translating it as overflowing signed C arithmetic would not preserve the machine contract.

**MP100-007 advances to partial support:** there is a concrete mechanism for more compact police-list spacing in both row advance and panel layout. The advertised resemblance to the standard opponents list, actual speed fields/images, complete visual layout, every caller and1.0.0 introduction remain unverified. The default-selection change in the preceding section is separate from these spacing coefficients. No game, renderer, font load, instruction probe or Ghidra write occurred.

## SoftTri list-bevel claim: checked renderer gates are retained

**Historical checkpoint:** the later [actual list-border branch comparison](#historical-list-bevel-fix-retargets-the-software-branch) supplies positive static evidence. The vendor-only assessment below records the earlier negative lead.

**Bounded negative evidence; advertised fix unresolved.** The [software-gate audit](evidence/audits/hud-software-gate-boundary.json), reproduced with `python3 analysis/scripts/audit_hud_software_gate_boundary.py`, pins supplied original, author-hosted1.4.0/1.5.0 and official final EXEs. This follows the opponent/police list research above without assuming a nearby changed field owns the bevel feature.

| Selected branch/fall-through span | Retained test | Retained skip target |
|---|---|---|
|`00482051..004820ac`,91 bytes |TEST byte`007a3a58`,2; JNE |`004820ac` |
|`0048213e..00482173`,53 bytes |Same TEST/JNE predicate |`00482173` |

Each whole captured span is byte-identical across all four inputs, including the1.4.0→1.5.0 release boundary. They therefore do not supply a newly removed software-renderer gate for MP150-017. These are bounded branch spans, not claims to complete enclosing-function boundaries or all software/rendering routes. Final's [type parser](original-modern-renderer-loading.md#5-driver-specific-configuration-before-loading) independently maps s-type to bit2; no universal flag meaning in every historical producer is inferred here.

The preceding audits separately establish width/reference substitutions, border coefficients, named Name/List defaults and compact police-row spacing. Those are real changes, but none alone identifies the advertised SoftTri-specific frame admission/drawing route. Similarly, equal branch bytes do not prove equal output: shared records, texture assets, other dispatch paths and provider code can differ.

**MP150-017 remains vendor-only/unverified.** The next required evidence is the actual opponent/pursuit frame-resource and submission linkage, including the software driver's handling of that submission and its changed inputs, followed by rendered validation if necessary. This check rules out one simple local-gate explanation; it neither disproves the vendor claim nor establishes a replacement explanation. Do not repeat this same span comparison as unresolved work, or label these unassigned branches as the exact claimed bevel without further linkage. No HUD, driver, callback, new instruction probe, Ghidra or executable modification occurred.

## Historical list bevel fix retargets the software branch

**Verified historical branch and queue mechanism; visual result remains untested.** The [list-bevel audit](evidence/audits/hud-list-bevel-history.json), reproduced with `python3 analysis/scripts/audit_hud_list_bevel_history.py`, supplies the missing positive evidence after the preceding negative gate check. It pins original, author-hosted1.4.0/1.5.0 and official final EXEs. MP150-017 now has **partial static support**, superseding the earlier vendor-only assessment. The other two unchanged gates remain valid negative evidence.

| Instruction | Original and1.4.0 |1.5.0 and final | Effect when renderer bit2 is set |
|---|---|---|---|
|`004847bc` JNE after TEST byte`007a3a58`,2 |Target`00484941` |Target`004847e5` |Now reaches border enqueue instead of skipping it |
|`004847e0` CALL`0049bd30` |Retained |Retained |Separate background quad still bypassed |
|`004847f2` CALL`0047fbe0` |Retained |Retained |Eight border quads now enqueued on this admitted software path |

The captured admission span`0048479e..0048483e` is160 bytes. It differs by exactly two bytes, at`004847be/004847bf`, between original/1.4.0 and1.5.0/final. Before the renderer test it checks profile List storage at`006fbc58` plus computed offsets; the enabled-list route also requires signed participant count`005efda0>1` or nonzero role-local ECX. Disabled/non-admitted paths reach the retained removal route at`004847fc`. Thus the change does not force every list to appear. Final bit2's software association follows the existing [renderer parser evidence](original-modern-renderer-loading.md#5-driver-specific-configuration-before-loading); historical flag production has not independently been requalified in this audit.

The frame resources are now distinguished by their actual allocation and consumption, rather than nearby global addresses:

| Resource | Vertex pointer | Index-base storage | Batch | Allocation |
|---|---|---|---|---|
|Eight-quad border bank |`00791b18` |`00791ad8` |`00749a38` |64 vertices at`0047cbb6..0047cbf3` |
|Separate background bank |`00791ad4` |`00791adc` |`00725748` |8 vertices at`0047cbf3..0047cc37` |

Allocator`0049bd10` returns the current batch+08 vertex count through ECX's output pointer, returns batch+10 plus count×32 through EBX's output pointer, then adds EDX to that count. Layout at`00481ede..00481ef3` selects border pointer`00791b18 + view×1024` and calls the existing eight-quad builder`0047f650`. Admission selects index base`00791ad8 + view×32` and calls`0047fbe0`. Its eight decoded calls enqueue consecutive groups of four indices through`0049bd30` into batch`00749a38`. Background admission uses`00791adc + view×4` and the other batch. The allocation span, selected layout span, both198-byte eight-group helpers and466-byte queue-helper span are byte-identical across all four builds. Changed border geometry elsewhere remains a separate mechanism.

Queue helper`0049bd30` appends four DWORD indices and increments batch+0c by four; when its signed first index is below batch+04 it first requests removal of the matching group. `0049bdc0` scans groups of four at batch+20010, removes the **first** exact match using overlap mover`004ea4f0`, and subtracts four from batch+0c. Consequently`0047fcb0`, which calls it eight times, is an eight-quad **removal** helper, not a draw or enqueue function. The nearby bank`00791ac8` removed at`00482dc8` is distinct from the border bank`00791ad8`; conflating them would misidentify the list-frame route. Flush`0049be40` passes count/4, vertices and indices to`004d5840` and`004c1e20`, then performs transient-group removal; those downstream consumers and provider behaviour have not been qualified here.

**Remaining:** this establishes the advertised release boundary and a concrete software-path bevel admission mechanism. The exact visible “standard bevel”, the advertised Speeds List identity, every caller/profile, software-provider rendering and stale-queue behaviour across transitions remain separate follow-ups. MP150-017 is partial, not fully verified. Reconstruction must preserve the conditional background/border distinction and queue lifecycle rather than merely drawing an unconditional rectangle. No game, driver, instruction probe, compiler or Ghidra write was used.


## Map-marker smoothing has an asset-level candidate

**MP150-014: partial code/asset linkage; not a rendered smoothing result.** The [HUD shape audit](evidence/audits/map-marker-shape-history.json), reproduced with `python3 analysis/scripts/audit_map_marker_shape_history.py`, pins140/150 archives/EXEs and a separately hashed local HUD backup.

The selected map renderer `0048d4c0..0048e76d`, marker helper `0048cc60..0048cce8`, HUD loader `0047f590..0047f645` and batch initializer `00484070..00484211` are byte-identical140/150. The loader requests FSH tag `1555` into descriptor `00791a94`; batch initialization reads its+4 cell `00791a98` for batch `0076da48`, and the centered marker helper submits that batch. This ties the selected map drawing route to an actual shape resource instead of assuming every HUD change is an EXE edit. Complete upload, ownership and all caller-role admission remain qualified by [existing HUD research](detailed-analysis-notes.md).

The140 archive has no `hud98.fsh` member;150 adds `gamedata/dashhud/hud98.fsh`. That is patch-package scope: an earlier game installation can already supply the file. Compared with local `gamedata_org/DashHud/HUD98.FSH`, the150 file has the same1,021,576-byte length and25-entry SHPI directory. **All1,050 differing bytes are inside the32×32 type7Dh `1555` pixel payload** at file offsets40120h..41120h; every other file byte matches.

| Highest byte in each of1,024 pixel DWORDs |Local backup |150 asset |
|---|---:|---:|
|0 |181 |260 |
|255 |843 |648 |
|Intermediate1..254 |0 |116 |

This is consistent with replacing binary transparency edges with intermediate alpha coverage, while retaining the center pixel and changing the border. The audit records highest-byte statistics explicitly; it does not independently validate the complete decoder, colour ordering, texture conversion or final blend policy. It must not be promoted into proof of visible antialiasing on every renderer.

The backup's **retail provenance is unverified**, and it is not demonstrated to be the installed140 asset. Consequently this is a concrete local-backup/150 payload difference and a package-boundary candidate, not a fully authenticated140→150 pixel comparison. Original retail identity, exact loaded file, police/player-specific coverage, successful upload and rendered edges remain follow-up work. MP150-014 advances vendor-only→partial. No game pixels are republished, no target instructions executed and no executable/Ghidra changes made.


### Game-side pixel format corroborates the alpha interpretation

The expanded shape audit checks additional retained140/150 code and data instead of relying solely on a file-format convention. `GetShapePixelDepth` at `00499e90` masks the format code with7Fh and indexes byte table `00566d54`; entry7Dh is32. Built-in hue-shape producer `0043db20` writes format7Dh and DWORD pixels from `0043de20`. That packer places three low-eight-bit channels at bit positions16/8/0 and ORs `ff000000`.

Separately, the checked raster compositor at `0052379f` extracts the packed input's highest byte. In its ordinary branch, zero returns without drawing,255 takes the opaque arm, and intermediate values enter a channel-blending arm. The retained prefix at `0052387e` separates the three colour channels and derives a complementary weight using `65536-(highByte<<8)` before reading the destination colour. The audit compares these selected bodies across140/150 and finds them unchanged.

Together these are code-level corroboration that the changed highest-byte values represent alpha-style coverage rather than an added colour channel. They do **not** prove this map texture traverses that raster compositor: conversion/upload, selected driver texture format and final blending remain separate links. The asset difference remains a partial smoothing candidate with unverified backup provenance and rendered output; no runtime or database changes were made.


## Opponent Name settings coordinates do not establish the gameplay move

The [131/140 asset audit](evidence/audits/opponent-name-menu-history.json), reproduced with `python3 analysis/scripts/audit_opponent_name_menu_history.py`, matches all12 `opponentNameButton*`/`opponentNameCascade*` controls in the pinned `fedata/menus/hud.mnu` members. Their x/y, listname and symbolic text fields are identical. The button position is9,313 and cascade position135,314 across all six profile variants. Other asset fields are outside this selected comparison.

These are settings-menu controls, not the gameplay name overlay. Their unchanged coordinates neither prove nor disprove MP140-071's advertised move beneath the rear-view mirror. The claim remains vendor-only. Next trace the profile+04 Name consumer (distinct from the already-qualified profile+08 List consumers), its gameplay rectangle/default producer and draw submission across131/140; then compare the resulting coordinates with the mirror layout. Do not substitute settings-menu geometry or List defaults for that missing linkage. No target execution or executable/Ghidra changes occurred.


### Gameplay Name consumer now linked; producer remains open

The expanded [Name audit](evidence/audits/opponent-name-menu-history.json) also pins the131/140 EXEs. Descriptor `00556848` names `opponentName` and binds storage `006fbc54`, profile header+04. Complete branch span `00483e49..00483ec8` (127 bytes) is byte-identical between these versions.

At `00483e57` it tests `006fbc54 + group×348h + role×1a4h`; zero skips to `00483ec8`. On the admitted path it additionally checks the selected object's+220h pointer and prepares text at pointer+34h. Before calling `004897f0` at `00483ec3`, it reads geometry DWORDs at `0074981c`, `00749820` and `00749818`, each indexed by the local `[ESI+4]` value×170h. The Name-to-call linkage is therefore established, independently of List's+08 gate. Pointer lifetimes, full callee ABI and the local index's complete production remain unqualified.

This closes the previous missing Name-consumer link without verifying the move. Next identify writes to these computed geometry cells and trace their profile rectangle sources across131/140, then inspect the callee's coordinate interpretation and mirror placement. A raw literal census alone misses base-plus-offset/alias writes and cannot establish the producer. Unchanged consumer instructions do not imply unchanged geometry or pixels. MP140-071 remains vendor-only until that linkage supports its specific relocation claim.


### Slot12 source presets change at131 to140

The same expanded [Name audit](evidence/audits/opponent-name-menu-history.json) now links the geometry storage to scaler `00480910..004809f7` (231 bytes, identical131/140). The scaler writes four DWORDs at `00749758 + localIndex×170h + slot×10h`. Therefore the Name consumer's `00749818/1c/20` reads belong to **slot12**, not an assumed settings-menu control.

Initializer prefix `00485680..004856c5` reads six profiles of96 WORDs at `00540500`, converting each WORD to binary32(value/1000) and swapping each pair into the profile rectangle. The conversion helper moves from `004f9404` to `004f9418`; its complete29-byte body is identical. The two corresponding call displacements account for the copy prefix's changed bytes. This historical WORD table differs from the final DWORD table described earlier; do not apply the final stride to these historical files.

|Profile index |131 slot12 source WORDs |140 slot12 source WORDs |
|---|---|---|
|0 |400,953,600,993 |400,156,600,196 |
|1 |0,0,0,0 |Same |
|2 |400,453,600,493 |400,121,600,161 |
|3 |0,0,0,0 |Same |
|4 |400,953,600,993 |400,621,600,661 |
|5 |0,0,0,0 |Same |

The source order is preserved above; adjacent pairs are swapped during initialization, so these numbers must not be quoted as final pixel coordinates. The changed second/fourth source bounds preserve extent40 while reducing their positions in profiles0/2/4; first/third remain400/600. The scaler reads the corresponding profile rectangle at header+24h+slot×10h and writes the indexed integer geometry. This is a concrete source-and-consumer mechanism consistent with the advertised relocation.

**MP140-071 advances to partial:** slot12 preset changes and the named Name consumer are linked. Remaining: full call-site admission selecting slot12, intervening layout/attachment writes, the drawing callee's full coordinate ABI and actual mirror-relative pixels. Do not claim the exact “just under the mirror” result solely from these source bounds. No target instructions or Ghidra/executable writes occurred.


### Complete131 to140 preset-table difference inventory

The expanded [historical HUD audit](evidence/audits/opponent-name-menu-history.json) records both complete1,152-byte tables at `00540500..00540980`, including hashes and raw hexadecimal bytes. The initializer's six profiles×24 slots×four WORDs account for the entire extent. **14 of144 rectangle records change, containing26 changed WORDs;130 records are identical.** This is exhaustive for these tables, not for all HUD state or either executable.

|Profile indices |Slot |131 source WORDs |140 source WORDs |
|---|---:|---|---|
|0,1 |6 |463,197,538,297 |463,235,538,335 |
|0 |12 |400,953,600,993 |400,156,600,196 |
|0 |15 |388,400,612,440 |388,350,612,400 |
|2,3 |3 |656,0,749,123 |657,0,749,123 |
|2,3 |6 |463,187,538,287 |463,190,538,290 |
|2 |12 |400,453,600,493 |400,121,600,161 |
|2 |15 |388,145,612,185 |388,190,612,240 |
|4,5 |6 |463,687,538,787 |463,690,538,790 |
|4 |12 |400,953,600,993 |400,621,600,661 |
|4 |15 |388,645,612,685 |388,690,612,740 |

Indices are zero-based. Grouped profile rows represent separate equal changes; the machine-readable manifest enumerates all14 individually. Slot12 has the Name consumer linkage above. Slots3/6/15 remain identified by layout position rather than guessed widget names. Their changed bounds are available for later reconstruction decisions without requiring another table discovery pass. Complete scaler-call admission, all attachment/override writes and visible effects remain unverified.

Historical address note: `004f9404`/`004f9418` here name conversion helpers in the pinned131/140 EXEs. The saved final database assigns different functions to these addresses. Address-index cross-links are navigation aids, not proof of cross-version function identity; use each capture's version/hash before applying a label or annotation.


### Local initialization loop explicitly scales slot12

The [historical audit](evidence/audits/opponent-name-menu-history.json) now captures `00484c10..00484c5d` (77 bytes), identical131/140. It loads dimensions from `007cdac8/007cdacc`, initializes local index0 and slot0, and calls `00480910` at `00484c43`. The loop visits slots0 through22 for local indices0 and1, so **slot12 is explicitly included**. This establishes the selected local call path, not entry into the initializer in every session or absence of subsequent writes.

The complete text adapter `004897f0..004898a4` (180 bytes) is also identical131/140. It accepts the Name text pointer through EAX and six stack values, eventually returning with RET18h; it branches on an alignment value and uses lower text helpers including `004d1390`, `004d1480`, `004d10e0` and `004d1000`. The earlier consumer passes the selected geometry values into this adapter. Its retained body does not prove equal output when the supplied geometry changes, or establish the lower text ABI/transitive rendering behaviour.

This supersedes the earlier local scaler-call gap. The still-required evidence is full initializer admission/timing, geometry edits after scaling, mirror rectangle linkage and lower text coordinate interpretation/rendering. The exact “just under the mirror” claim remains partial; no live HUD was observed.


### Slot15 supplies the WRONG WAY text branch

The expanded [historical HUD audit](evidence/audits/opponent-name-menu-history.json) identifies another changed preset without inventing a release-note attribution. Complete branch `0045b787..0045b7dc` (85 bytes) is identical131/140. It reads slot15 geometry at `0074984c/50/48 + localIndex×170h`, supplies lookup ID`0151h` at `0045b7be`, calls language lookup `004d1850` at `0045b7c9`, then text adapter `004897f0` at `0045b7ce`.

The pinned140 `fedata/text/text.eng` table's zero-based entry337 (`0151h`) contains **WRONG WAY**. Its asset hash, entry offset and exact label are retained in the audit; no131 packaged English table is asserted. This links slot15 to the selected WRONG WAY drawing branch. Its profiles0/2/4 have the source-bound changes listed in the complete inventory above, so the HUD table changes extend beyond Opponent Name.

This is an independently identified layout change, not a new count of vendor release-note entries. Full warning admission, selected language/font, later geometry writes and final placement remain unverified. Slots3/6 remain unnamed pending stronger consumer evidence. No game, text renderer or target instructions were executed.


### Slot6 connects to the Tutorial Icon quad path

The expanded [historical HUD audit](evidence/audits/opponent-name-menu-history.json) verifies complete builder `004818b0..00481aa0` (496 bytes) and editor arm `0045b8d0..0045b91a` (74 bytes), both identical131/140. It also checks jump-table slot6 at `0045aae8` targets `0045b8d0`. The [existing POS/editor classification](original-modern-hud-settings-policy.md#registered-editor-draw-chain-retains-both-widget-cases) names this slot **Tutorial Icon**; this is reused evidence, not a widget name inferred from coordinates.

The builder reads geometry `007497b8..007497c4 + localIndex×170h`, exactly scaler slot6, and builds thirteen quads in `[00791a58]+localIndex×680h`. Its full layout contract is already documented under [thirteen-quad scaling](detailed-analysis-notes.md#thirteen-quad-hud-rectangle-scaling). The checked editor case calls selection helper `00482030` at `0045b8e1`; its renderer-bit2 fallback calls submission helper `00482190` at `0045b900`. Those helpers' existing [buffer/selection analysis](detailed-analysis-notes.md#hud-quad-pair-selection-and-color-update) links the same vertex storage and records the extra-view colour-offset limitation.

This connects the slot6 source-bound changes in all six profiles to the Tutorial Icon geometry/editor path. Full live selection, texture identity, every gameplay consumer, later writes and rendered movement are not established. In particular, the retained unusual colour-address calculation must not be silently normalized during reconstruction. Slot3 remains the only changed table slot without a named-widget linkage in this historical audit. No new target execution or Ghidra changes occurred.


### Slot3 has a qualified Analog Tachometer identity

The expanded [historical HUD audit](evidence/audits/opponent-name-menu-history.json) reuses the pinned [reference-asset inventory](original-modern-reference-assets-index.md). It verifies the reference archive/member hashes, reads all138 ordered records from `gamedata/dashhud/edef.pos` and records slot3's six names: RacerAnalogTachometer, CopAnalogTachometer, Player1RacerAnalogTachometer, Player1CopAnalogTachometer, Player2RacerAnalogTachometer and Player2CopAnalogTachometer.

Historical builder prefix `004812e0..004813d0` (240 bytes) is identical131/140. It reads `00749788/8c/90/94 + localIndex×170h`, exactly scaler slot3, applies inset calculations and calls border builder `0047f650` at `004813cb`. This supplies geometry-path corroboration; it does not establish every subsequent tachometer draw or final pixel coordinates. The reference preset's names establish an ordinal semantic association, not a claim that its numeric coordinates equal either embedded historical table.

The only slot3 source-table change in131→140 is first WORD **656→657** for profiles2/3; the other three WORDs and other slot3 profiles match. Call it a one-unit preset adjustment, not automatically a one-pixel movement: initialization divides by1000, scaling/rounding and insets follow.

**Changed-slot identity map:** slot3 Analog Tachometer (qualified reference ordinal plus geometry linkage); slot6 Tutorial Icon (reference/editor and shared quad linkage); slot12 Opponent Name (named setting and consumer); slot15 WRONG WAY (version-bound text lookup and drawing branch). Every changed table slot now has an explicit identity basis and limitation. Authenticated original provenance, runtime loading/lifetime and complete rendered effects remain open. No executable, saved database or target instructions were changed/executed.
