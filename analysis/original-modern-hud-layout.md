# Original versus Modern: HUD preset source and default records

## Scope and evidence

**Static initialization comparison; no rendered HUD validation.** Supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`; official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline](original-modern-differences.md).

Run `python3 analysis/scripts/audit_hud_layout_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-hud-layout.json) records input/span hashes, original filename/token formats and Modern embedded-preset provenance. Raw assembly remains ignored under `analysis/captures/modern-differences/hud-layout/`. No executable, Ghidra, game or instruction-probe changes.

The matched pair is preset initializer `00485680`, followed by default-header initializer `00485880`, which calls it in both binaries. Ghidra's Modern function boundary at `0048582c` is a shared-frame continuation, not a standalone callable ABI; capture includes its real return/unwind.

## 1. File-sourced presets become embedded data

The author-hosted 1.1.0 package already contains the embedded-preset path. Its `nfs3.exe` member hashes to `59456e52d7ec06fafcc170fd23ba1b1c241d849c66249b653013b33389f39a72`. At `00485694`, the paired initializer loads source `00540500` and consumes six profiles of 96 WORDs each. It zero-extends each WORD and calls `004f93ec`, which divides the integer by 1000 on x87 and stores binary32. The loop then enters dimension-dependent arithmetic at `004856c5`. This dates the selected embedded table and aspect computation to at least 1.1.0 and distinguishes its WORD conversion from the final preset format. The exact 1.0.0 implementation and visible placement remain unverified.

The six locale-prefixed presets in the [author-hosted reference archive](original-modern-original-reference-bundle.md) (`EDEF`, `FDEF`, `GDEF`, `IDEF`, `SDEF`, `WDEF`) each match both local copies byte for byte. This was checked by streaming each member from the hash-verified `nfs3_orig.7z` through `cmp` and comparing the installed and backup members with each other. The existing [coordinate comparison](original-modern-reference-assets-index.md#hud-coordinate-literal-comparison) therefore applies to all six local locale-prefixed files. The unprefixed `DEF.POS` is present locally and outside this archive comparison. This establishes input identity for the six pairs. Runtime parser output and retail-disc provenance remain unresolved.

Original `00485680`:

- Selects a character using `[006fbb4c]` and byte table `0047bbb8` (`egfsiw` plus NUL). The [original defaults-time language mapper](original-modern-language-table.md#removed-defaults-time-language-mapper-00472250) writes indices 0–5 for English, German, French, Spanish, Italian and Swedish, respectively. The local installer starts with `english`, so that path supplies `edef.pos` when the defaults mapper runs and its selection reaches this initializer.
- Formats `%s%cdef.pos` using prefix pointer `007a29b4` and that character, then calls loader `004e0ec0` at `004856cd`. Prefix and locale admission are not re-established here.
- If load returns null, branches directly to the common epilogue `0048586d`.
- This path has no retry with `DEF.POS`. Index 6 would supply a NUL byte to `%c`, terminating the visible C string after the directory prefix. The initializer has no local index bounds check. Other potential consumers of the unprefixed file remain outside this trace.
- Otherwise tokenizes using delimiter literal `: -(,)`, parses name/float tokens, and writes 23 rectangle slots per profile across three groups of two profiles. The nested bounds are visible at `004856ef/004857b2/004857bf`.
- Copies a separate four-DWORD slot from table `0055d454` into the last rectangle area of each profile (`004857d6..0048582a`), then enters the shared refresh tail.

Modern replaces that file/token route with a **file-backed embedded table** at `0053eb20`, consuming **0x900 bytes**: six profiles × 48 pairs of DWORDs. It swaps the two members of each pair into destination `+4/+0`, advances 8 bytes, then skips the next profile's 0x24-byte header. Each destination is at `006fbc50 + profile*0x1a4`.

The archive-matched 1.5.0 through 1.5.3 executables all retain the same 1,152-byte WORD table at `00540500` (SHA-256 `ff646b3a7fa754b60e7cee0c89509a32f69b49d2b1a1e07b6e18664ab06c8454`). The 1.6.0 copy loop at `00485694..004856b5` reads DWORD pairs directly from `0053eb20` and keeps the same pair swap. Its 2,304-byte table matches final 1.6.1 (SHA-256 `00e3c6b1e4b5f42e345e837845343a99c2798cb41686c8d6136a6c835bb2abbc`). Comparing in source order after converting each 1.5.3 unsigned WORD to nearest binary32 of `value / 1000` gives 143 differing scalars across 74 of 144 rectangles. The widening therefore also changes the preset data. This comparison uses nearest rounding and stops before the runtime layout arithmetic.

The local layout established by these writes is therefore **0x24 bytes of header plus 24 × 16-byte rectangle storage = 0x1a4 bytes**, six records. This does not establish semantic names for every header field or rectangle slot. It also does not prove which installed original `*def.pos` contents the embedded table was derived from. The [reference-asset comparison](original-modern-reference-assets-index.md#hud-coordinate-literal-comparison) now compares six author-hosted variants numerically; none matches the embedded table exactly. Authenticated installed-original provenance and runtime parser equivalence remain unverified.

No original preset-file read remains in this Modern initializer. This is a concrete source/initialization change, not proof that the whole game no longer reads external HUD/layout resources elsewhere.

The shared delimiter tokenizer survives the preset rewrite. Its 165-byte body at `004eff60..004f0005` matches in the paired disassembly. The direct `CALL` scan finds six original HUD call sites (`004856e2`, `0048571a`, `00485750`, `0048576b`, `0048578c`, `004857a8`), all absent in final. The seventh original site, `00442a07`, survives in the [menu token comparator](original-modern-race-now.md), which starts tokenization on a local copy and resumes with EAX zero after a nonmatching token. This establishes a retained consumer of the helper separately from the removed HUD parser route. The scan covers direct calls recovered by `objdump`; indirect references were outside its scope.

The [baseline executable pair](original-modern-differences.md) also differs at the literal level. A case-insensitive whole-file byte scan finds one ASCII `.pos` suffix in the original, at file offset `0x13a067`. It belongs to `%s%cdef.pos` at VA `0053b660`. The final executable contains no ASCII `.pos` suffix, and neither executable contains `DEF.POS` encoded as UTF-16LE. This rules out an independent literal `DEF.POS` in either scanned executable. Dynamically assembled filenames and references in external modules or assets remain outside the scan.

The [paired startup path audit](original-modern-startup-paths.md#original-installer-records-and-final-path-slots) resolves the original prefix for the inspected installation. Record eight in `install.win` supplies `.\GameData\DashHud\` at `007a29b4`. For the `e` table entry, the original initializer therefore passes `.\GameData\DashHud\edef.pos` to the file loader. Modern initializes the same directory path apart from case, but this initializer copies embedded data. A case-insensitive filename inventory and pairwise SHA-256 comparison show that all seven local `*DEF.POS` files (`DEF`, `EDEF`, `FDEF`, `GDEF`, `IDEF`, `SDEF`, and `WDEF`) match between the installed `GAMEDATA/DASHHUD` and backup `gamedata_org/DashHud` trees. Their presence and identity establish the local inputs available to the original file-based path. Actual file selection, retail-disc provenance and visual equivalence remain unverified.

## 2. Aspect adjustment and the retained shared-frame tail

Modern derives two x87 factors from DWORDs `006fd1e4/006fd1e8`. Producer `00448400` copies width and height from selected mode-record `+4/+8` to those addresses, and calls `00485680` if either changes. Let W/H denote those configured dimensions, C the binary32 literal `0x3faaaaab`:

- One retained factor is `0.75/(H/W)`.
- The other is `C/(W/H)`.
- Four calls to `00485718` at rectangle slots 1, 3, 6 and 8 (zero-based) adjust bounds at rectangle `+4/+0xc` using the second factor.
- One call to `0048573b` at slot 21 adjusts bounds at `+0/+8` using the first factor.

For the selected bounds, each helper forms extended delta `(hi-lo)*(1-factor)/2`, stores binary32 `lo+delta`, then binary32 `hi-delta`. The original hi remains available until its store; the extended delta is not reloaded from rounded float memory. Factors above one expand, rather than inset, the range. This is x87-sensitive arithmetic, not an instruction-equivalent replacement by a sequence of `float` operations.

Modern jumps at `00485713` into **unchanged bytes** at `0048582c..00485875`. That tail conditionally refreshes two views and 23 slots when `0055d440` is nonzero, then restores the parent frame and six saved registers. It is reached inside the initializer; exporting it as a normal isolated C function would invent an ABI. The previous [HUD helper contract](detailed-analysis-notes.md#internal-x87-hud-bounds-helpers-00485718-0048573b) already records the two required x87 inputs and preservation behavior.

The complete 501-byte span `00485680..00485875` and the 12-byte constants at `0053f420..0053f42c` match 1.6.0 and 1.6.1. The direct-call scan finds three sites in each build. Two remain at `0044de29` and `00485881`; the mode-publisher call moves from `00448422` to `0044841e`. In both publishers the selected path compares the two incoming dimensions with `006fd1e4/e8`, copies those dimensions and the following DWORD, and calls the initializer only if either dimension differs. This establishes continuity of the initializer, constants and selected refresh gate. It leaves other caller inputs and rendered output unverified.

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

The archived 1.4.0 initializer still writes `006fbbb8/bc` at `0048588b/91`. In 1.5.0 the writes are in separate helper `00472258`: it clears EAX, then sets AL to 3 before storing EAX at `00472272/77`. On the selected 1.5.0 defaults chain, `00472ad2` calls the HUD initializer and `00472ad7` immediately calls this helper. Indexed readers remain at `0042540e` and `00425421`. Thus the missing stores in the HUD routine do not imply that this defaults path stops setting the pair to 3. Other entry points and persisted overrides remain unverified.

In final 1.6.1 the separate helper still stores 3, now at `004722b7/bc`. The 1.5.0 and final fallback span `00425400..0042543c` is byte-identical. When the requested value is `-1`, it indexes the pair using context DWORD `+0x0c`, tests the saved value via the [membership predicate](detailed-analysis-notes.md), and forwards the saved value or fallback `005e1054` to `00422610`. This establishes a retained viewport-setting consumer of the pair. The default value's exact on-screen meaning and all runtime override paths remain unresolved.

The predicate `00423ab0` scans all 25 DWORDs at `005e103c`. On the reviewed rebuild path, `00423a20` enumerates four candidate DWORDs beginning at `006fbbc0`, immediately after the saved pair. The [table builder](original-modern-projection.md) fills all 25 entries with the first nonzero candidate (or 2 if none) before storing successors. If all four candidates are zero when that builder runs, the table contains only 2 and the predicate rejects both 1 and 3. Thus writing either saved default alone does not establish which value reaches the viewport. Actual candidate values and rebuild ordering in a live session remain unverified.

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

The retained 1.1.0 executable already sets all six speed-unit selectors to 3. At `00485974` it loads EBX with 3, then `00485979..0048599d` writes it to `006fbc68 + profile * 0x1a4` for all six profiles. This matches final's default selector policy and dates the removal of the original language-dependent default to at least 1.1.0. The same early initializer independently writes 3 to `006fbbb8/bc` at `00485891/97`, where the original writes 1 and final has no corresponding stores in this routine. Those two globals are distinct from the six speed-unit selectors. Their later writers and runtime values remain outside this comparison.

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

Accordingly **MP100-004 receives partial static support for the fitted-reference→scale→conditional-text route**. This review does not establish a universal height-based rule for all menu, atlas, bitmap and HUD fonts, nor that every widescreen label avoids excessive size. Other font-selection paths and visible output remain follow-up requirements. Preserve the chosen version’s scale sources and both gates in reconstruction; globally replacing width with height would alter retained behaviour that this comparison has not shown the patch changed.

### The fitted text-scale path is already present in 1.0.0

The retained 1.0.0 and official 1.6.1 EXEs match over the complete
scale initializer `00484b70..00484c10` (SHA-256
`3620c18726db32aba8b11237bb2fb4e855ca937e1ff4ee228bea61af2cc9338f`),
the text adapter and setter spans above, and the coefficient DWORD at
`0053b620` (file bytes `89 d2 de 3a`; hosted original `cd cc cc 3a`).

The 1.0.0 rectangle producer uses different addresses from final.
Its wide branch at `004be7e3` calculates `trunc(4*H/3)` for ordinary
positive dimensions and passes it in ECX to the rectangle writer
`004be898`. The call at `004be811` sets the writer destination to
`007a2740`, so ECX lands at `007a2748`, the width used by the
scale initializer. This establishes the early wide-branch route in code.
Reproduce by extracting the [retained 1.0.0 EXE](original-modern-dll-candidates.md#recovered-100-package-separates-code-changes-from-renames)
and comparing those file-backed spans and disassembly addresses.
Actual glyph sizes remain untested.

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

**MP100-007 advances to partial support:** there is a concrete mechanism for more compact police-list spacing in both row advance and panel layout. The advertised resemblance to the standard opponents list, actual speed fields/images, complete visual layout, and every caller remain unverified. The default-selection change in the preceding section is separate from these spacing coefficients. No game, renderer, font load, instruction probe or Ghidra write occurred.

The hosted original stores 20.0 at both coefficient sites.
All 12 retained Modern EXEs, starting with 1.0.0, store 12.414
at both. The six-byte x87 multiply instructions that reference
them are identical across the 13 EXEs. For reproduction, read
binary64 values at PE RVAs `13b598h` and `13b8cch`, and compare
instruction bytes at RVAs `81cbeh` and `8a70eh`. This dates
the spacing coefficient change to 1.0.0.

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

## 1.4.0 to 1.5.0 updates eight preset rectangles

The paired digital display branch at `004839eb..00483a36` is byte-identical across both archived builds. For selector 1 or 3, it multiplies the local index at `[ESI+4]` by `0x170`, then reads scaled slot 0 offsets `+0`, `+8` and `+0x0c` at `00483a0b`, `00483a11` and `00483a19`. This ties the slot 0 edits below to a retained geometry consumer. Whether the changed input values reach those fields after profile selection and scaling, and whether the display visibly moves, remain unverified.

Both releases retain scaler `00480910..004809f7` byte for byte. It writes rectangles at `00749758 + localIndex * 0x170 + slot * 0x10`. The paired 74-byte span `00483772..004837bc` forms the same local-index stride and reads `00749780` and `0074977c` plus that stride using `FILD`. These are slot 2 offsets `+8` and `+4`. Thus at least one downstream geometry path reads the scaled slot whose first two profiles have source edits below. The address match establishes the consumed slot and retained instructions. It does not establish which profile is active or whether the small input edits survive rounding in a selected display mode.

The two retained package members both use the WORD source table at `00540500..00540980`. A complete comparison finds 10 changed WORDs in eight of 144 rectangles. Indices are zero-based and values below are in source order before the pair swap and layout arithmetic.

| Profiles | Slot | 1.4.0 | 1.5.0 |
|---|---|---|---|
| 0, 1 | 0 | `(130, 2, 330, 58)` | `(130, 4, 330, 58)` |
| 0, 1 | 2 | `(655, 2, 850, 83)` | `(655, 4, 850, 85)` |
| 2, 3 | 0 | `(130, 0, 330, 56)` | `(130, 0, 330, 54)` |
| 4, 5 | 0 | `(130, 500, 330, 556)` | `(130, 500, 330, 554)` |

The 1.4.0 table SHA-256 is `4812d9a1657e3d90b83353e74e5598d76b2580e2c1c6c66461b7ebc9fa6a03a9`. The 1.5.0 table matches the later 1.5.x releases as recorded above. The comparison was made by streaming each archive's `nfs3.exe` to `pefile` and decoding six groups of 24 little-endian `4H` records. In the hash-matched reference `EDEF.POS`, slot 0 is named `DigitalSpeedometer` for all six profile prefixes, and slot 2 is named `DigitalTachometer` for the standalone Racer and Cop prefixes. The names come from records 1 and 3 of each 23-record file group, before the original initializer's extra rectangle. This identifies the corresponding authored slots by ordinal. On-screen geometry, runtime profile selection and release-note attribution remain unverified.

## Earlier120 to130 updates55 preset records

At the next boundary, 1.3.0→1.3.1 retains the complete 1,152-byte coordinate table at `00540500` (SHA-256 `191ab6e8206f777222ab65597531997c326eafd7d27cc755b153b123fd4fe922`) and the 69-byte copy prefix. The remaining 432-byte initializer span has exactly 24 changed bytes, all within eight operands that switch from `007a3920/24` back to `006fd1e4/e8`. The 1.3.1 defaults at `00472566` write 640×480 to that restored pair. On the reviewed mode-publisher path `004483f8..00448419`, the publisher compares the two incoming dimensions against the current pair, copies both dimensions and the following DWORD, and calls `00485680` only if either dimension changed. In 1.3.0 the reviewed rebuild gate instead uses the composite key described below. No runtime modes were exercised.

The preceding 1.1.0→1.2.0 release pair retains all 144 rectangles. A PE virtual-address read of `00540500..00540980` from each archive-matched EXE gives identical 1,152-byte tables, SHA-256 `c1061f11bfa9b79f76fcf49098c1e4b93486b02d3fc1d8cacfbe8046c22992fc`. The only differing bytes in the copy prefix `00485680..004856c5` are at `004856ab` and `004856b7`, redirecting the two calls from `004f93ec` to `004f9404`. Those 29-byte converters match, as do all 432 bytes in `004856c5..00485875`. This establishes table and selected initializer continuity through 1.2.0. The subsequent 1.2.0→1.3.0 changes below therefore start from the same embedded coordinates seen in 1.1.0. Caller inputs and runtime layout remain outside the byte comparison.

The [early HUD audit](evidence/audits/early-hud-preset-history.json), reproduced with `python3 analysis/scripts/audit_early_hud_preset_history.py`, pins120/130 author-hosted EXEs and compares the complete1,152-byte WORD table00540500..00540980. This is the same six-profile×24-slot×four-WORD layout documented for131/140, not final's differently sized DWORD table.

**55 of144 records change;89 remain identical.** There are118 changed WORDs and118 changed file-byte positions. Every changed record, address, before/after WORD quadruple and signed delta is retained in the manifest. This exhausts this paired table, not the vague release note's complete HUD scope.

|Profile |Changed rectangle records |
|---:|---:|
|0 |8 |
|1 |7 |
|2 |11 |
|3 |9 |
|4 |11 |
|5 |9 |

Examples in source order: profile0/slot0 changes130,4,330,60→130,2,330,58; profile2/slot1 changes250,0,344,125→251,0,343,123; profile4/slot3 changes656,500,750,625→657,500,749,623. These identify concrete coordinate/bound edits without assigning unverified live profile selection or a pixel interpretation.

Both versions retain byte-identical initializer prefix00485680..004856c5, complete29-byte conversion helper004f9404..004f9421 and complete231-byte scaler00480910..004809f7. The initializer reads this table, converts WORD/1000 to binary32 and swaps adjacent source members into rectangle storage. It is therefore incorrect to describe a two-unit source decrement as automatically two screen pixels or to transfer final's DWORD stride to these historical files. Equal code also does not establish equal inputs, x87 state, later writes or rendered results.

**MP130-004 advances vendor-only→partial:** the immediate120→130 pair supplies a concrete preset-data update consistent with “HUD was updated a little.” It does not establish all other HUD changes, rationale, visual quality or active-session placement. Reuse the separate131→140 inventory for later Name/Wrong Way/tutorial/tachometer evidence rather than attributing those later edits to130. No target instructions, UI, compiler or Ghidra changes occurred; executable/database bytes are unchanged.

## Earlier130 also changes the x87 aspect-adjustment block

The expanded [early HUD audit](evidence/audits/early-hud-preset-history.json) captures complete contiguous region004856c5..0048582c in120/130, including internal helpers and padding. **329 byte positions change.** The preceding69-byte copy prefix,29-byte WORD converter and231-byte downstream scaler remain identical as above; shared refresh/unwind tail0048582c..00485875 also matches. Prefix equality must not be generalized to the whole initializer.

|Selected operation |120 |130 |
|---|---|---|
|Dimension operands for ratio work |DWORDs006fd1e4/006fd1e8 |DWORDs007a3920/007a3924 |
|Small inverse-dimension term |`1/(2*Wold)` via FIDIV W then FIDIV2 |`k/Wnew` and additional `k/Hnew` |
|Coefficient k |No corresponding pushed coefficient for this term |Binary32 bits3efff2e5, value approximately0.4999000132083893 |
|Live x87 values discarded before shared tail |Five FSTP ST0 operations |Six iterations of FSTP ST0 |

These formulas are algebraic shorthand for the selected arithmetic with ordinary positive, nonzero dimension operands, not a guarantee of final rounded float equality.120 performs two successive divisions; do not reassociate them into a signed-C `2*Wold` expression that can overflow or change rounding. The new coefficient resembles a half-pixel adjustment, but its rendered purpose and physical/logical provenance are not established solely by these instructions. The two dimension pairs must retain distinct storage identities. The [selected publisher follow-up below](#historical-dimension-publisher-moves-with-the-hud-operands) now resolves their coordinated source, while full lifetimes remain unverified.

A concrete changed internal helper illustrates the hidden-register contract.120 helper0048579a..004857a9 loads `[EDI]`, adds its existing ST1 term and stores binary32.130 counterpart0048579b..004857ac adds the corresponding term **and ST4** before storing. At these calls, the newly built ST4 term after the temporary FLD is `k/Hnew`. Other bounding operations and helper addresses also change within the captured region; their full behavior is not replaced by this one example.

These helpers consume ambient x87 stack values established by the parent frame; a direct C export with no arguments would conceal their inputs. Arithmetic stays in the x87 stack until its FSTP stores, so a sequence of binary32 temporary variables could change rounding or exception/status behavior. Width/height zero, negative/corrupt fields, rounding mode, caller precision settings and floating-point exceptions remain separate reconstruction contracts. Do not silently drop the small terms or label329 differing bytes as329 features.

This strengthens MP130-004's partial support beyond changed presets: the same immediate release pair alters the selected aspect arithmetic and operand source. Actual HUD positions, visual improvements, all dimension producers and the full release-note scope remain unverified. This historical block also differs from the simpler final initializer described near the beginning; final helper addresses/stack contracts must not be copied backward. No target instructions, new probes, compilation, executable or Ghidra changes occurred.

### Historical dimension publisher moves with the HUD operands

The expanded [early HUD audit](evidence/audits/early-hud-preset-history.json) now captures selected-mode lookup/publisher004483a0..004483ff and defaults00472566..0047257a. The publisher's only changed instruction bytes are the destination immediate at004483e6: **006fd1e4→007a3920**. All other bytes match120/130 after substituting that pointer. Both default paths write640/480, redirected to the corresponding new pair in130.

The lookup scans records at00a18320 with stride114h, matches the incoming ID, and falls back to the first record on no match. Its helper discards the ID with LODSD, then copies source fields+4/+8/+0ch into three consecutive destination DWORDs. The130 HUD reads its ratios from that new destination, so the address changes are coordinated with the same selected-record publication. They do **not** prove different physical/effective dimensions at the moment of this copy. Empty/uninitialized record storage and complete lookup admission remain separate preconditions.

After copying, both versions compare **`wrap32(field4 * field8 + field0c)`** with006fbc18. A changed key is stored and calls preset initializer00485680; equal key skips that call even though the three fields were already copied. This is a composite-key gate, not an independent equality check on width and height. As a purely arithmetic example,800×600+16 equals1000×480+16, so different hypothetical records can share the key. Their actual availability/selection is not established, and no stale-HUD symptom was observed. A C reconstruction must preserve the low32-bit arithmetic instead of introducing signed multiplication overflow or silently replacing the key policy.

The gate also changes how the third copied DWORD affects a refresh. In 1.2.0–1.3.0, changing only record field `+0x0c` changes the composite key and requests a refresh, assuming the stored key represents the previous record. In 1.3.1 and 1.4.0, `0044840e` still copies that field but only the width and height comparisons increment ECX. Version 1.5.0 retains that rule at `00448410`, and final 1.6.1 retains it at `00448419`. Conversely, a width or height change with an unchanged composite key now requests a refresh. These are branch-level differences for hypothetical record transitions. The third field is the menu row's **colour depth**. The historical enumerator loads it from driver record `+0x08` into ECX at `004bedd4`, and the menu collector saves ECX at row `+0x0c` at `00448254`. The collector also passes it as the third number to the resolution label formatter. The separate row field at `+0x10` carries the [Z-buffer capability indication](original-modern-display-modes.md). The final row layout and publisher agree with the [later mode-selection trace](original-modern-mode-selection.md#hide16bitmodes-also-changes-the-depth-requested-on-replay). Whether the running game can select two rows with equal dimensions and different colour depths depends on the driver and menu filtering.

A depth-only transition was possible at the EXE menu-list level when the refresh rule changed in 1.3.1. Both 1.3.1 and 1.4.0 reject depths below 16 at `004bedfe`, then append otherwise eligible modes without merging equal dimensions. The collector at `00448210` rejects a new entry when the signed count reaches 101 and writes the depth at `00448254`. Thus, if a driver supplies otherwise eligible 800×600 rows at 16 and 32 bits before the cap, both can occupy distinct menu rows. This example describes the EXE paths. The [checked 1.4.0 DX8 builder](original-modern-display-modes.md#dx8-early-size-filter-and-later16-bit-admission) filters its enumerated inputs to 32 bits, so that builder cannot supply the hypothetical 16-bit input through that enumeration path. Starting in 1.5.0, [`Hide16bitModes` can merge equal-dimension rows](original-modern-display-modes.md#3-menu-list-append-becomes-sorted-insertiondeduplication) in the EXE itself.

This closes the selected publisher-to-HUD operand link. Other writes/aliases, actual record contents, effective viewport transformations and initialization timing remain unknown. The later final producer described earlier uses a different dimension-change guard; its implementation must not be substituted into120/130.

**MP100-005 advances vendor-only→partial:** the existing original/final comparison proves file-sourced presets become embedded aspect-adjusted initialization, and the selected historical publisher concretely requests a rebuild after a changed mode key. Exact100 introduction, every settings path, universal rebuilding, complete absence of other POS consumers and the advertised visual accuracy remain unverified. No resolution was changed in a running game and no target/API/instruction execution or Ghidra mutation occurred.

### Frontend writes the same selector to all six profiles

At `004517d4`, the original selects ECX=1 when the language field
`006fbb4c` is zero and ECX=3 otherwise. Modern selects 3
unconditionally. The shared tail at `004517e9..0045180d` writes the
value to `006fc154`, `006fc2f8`, `006fbe0c`, `006fbfb0`,
`006fc49c` and `006fbc68`. In ascending order those are precisely
the six profile selector cells at `006fbc68 + index*0x1a4`.

This particular write therefore changes all six cells from 1 to 3
when the original language field would be zero. The
[track length consumer](original-modern-track-length-text.md) places
1 and 3 on different unit-selection branches. Later profile edits,
entry-point reachability and visible units remain separate questions.

The ordinary defaults initializer `00485880` and this separate entry at
`004517d0` implement the same selector rule in each respective version.
This gives two matching static write policies. A scan of both pinned
executables found no near relative CALL to `004517d0` in their code sections
and no literal DWORD pointer to that entry in their file-backed sections.
Its activation remains unresolved. The ordinary defaults initializer is
the independent evidence for the changed default units policy.

The paired config traces identify the direct calls to the ordinary HUD
initializer. Original `00472807` calls it in the full defaults tail.
Modern `00472adc` calls it in the grouped reset branch, after header
refresh and display defaults. A loaded config with size `0x20f0`, zero
high version byte and low version byte at least 6 bypasses that Modern
branch. The unconditional selector 3 inside the initializer therefore
describes the reset default. Loading an accepted config does not itself
invoke this writer. See the [configuration comparison](original-modern-config-loading.md).

On the accepted Modern header branch, `00472ac6` calls the sound-mode
normalizer `00472230` and `00472acb` jumps to the common continuation at
`00472aeb`. The only direct setting write in the normalizer targets
`006fbc00` (audio mode), conditional on the capability result. Neither
this branch nor the normalizer directly writes any of the six HUD
selectors. This establishes local preservation through the header
decision and sound normalization. Provider callbacks and later
initialization remain separate from that result. See the
[audio capability evidence](original-modern-config-loading.md).

### 1.0.0 draws the selected-player HUD outlines in an earlier priority group

The hosted original `fedata/MENUS/HUD.MNU` and 1.0.0 `fedata/menus/hud.mnu` differ only in the two `priority=8` → `priority=10` edits on the `player1selected` and `player2selected` rectangle blocks. Both keep the same 320×120 size, thickness 4, Y positions 0 and 120, and corner colour `0xffffff00`. The paired member SHA-256 values are `1186648c5352fadfd94632cf2b43cc716e23d9c078863b563fa1602f3b14d60c` and `1c633422ecf718596dbbb44a887648848a22dcce8f6774f66a9f63667b9a1384`.

The four [priority draw-loop spans](original-modern-common-menu-buttons.md#location-and-opponents-dropdown-priority-changes-in150) at `0044a524..0044a536`, `0044a59c..0044a5a6`, `0044a5cb..0044a5e5` and `0044a634..0044a63a` match between the installed original and the archived 1.0.0 EXE. The loop visits higher groups first. The authored change therefore moves both outline callbacks earlier, allowing lower-priority controls to draw later. This supports MP100-054's layering mechanism. Actual compositing and overlap in rendered frames remain unverified.

In the 1.0.0 archive member, priority 9 contains six mirror cascades, covering the base, COP, and player-specific variants. Priority 8 contains six corresponding opponent-list cascades. The outlines therefore move from after the mirror group to before it, and from sharing the opponent-list group to preceding it. The two outlines join 33 image records at priority 10. Group order alone leaves their relative order within that group unresolved, and these counts include variants that need not be visible together. The counts can be reproduced by extracting the archived member with `7z x -so` and grouping its `priority=8`, `priority=9` and `priority=10` lines by section and `codelink`.
