# Original versus Modern: automatic FOV and projection-angle interface

## Evidence boundary

Static supplied-original/official-Modern comparison; exact fingerprints are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_projection_difference.py`. The [manifest](evidence/audits/original-modern-projection.json) captures original/Modern angle helpers, three paired callers, Modern producer call, exact float constants and an asserted identical projection builder. No rendering, game or instruction probes were executed.

The later sections require their named companion audits as well: `audit_projection_callers_followup.py` covers temporary/ordinary caller dispatch; `audit_projection_centre_references.py` covers the complete literal-centre inventory; `audit_viewport_geometry_difference.py` generates the original/Modern rectangle examples; and `audit_frame_setting_difference.py` establishes option labels and selection storage. Run each with `python3 analysis/scripts/<name>` from the repository root. The first script alone does not reproduce the whole expanded chapter.

## Automatic angle producer and selection

Modern helper **`004dbc48`** loads signed DWORD width/height from `006fd1e4/006fd1e8`, divides width by height on x87, multiplies by file-backed float 0.75, applies FPATAN with 1, doubles and multiplies by float `57.295780181884766`. Ordered comparisons clamp the result to file-backed float limits **90** and **107**, then store binary32 at **`0055fecc`**.

For ordinary positive dimensions and finite arithmetic, its mathematical summary is:

`automatic_degrees = clamp(2 * atan(0.75 * width / height) * radians_to_degrees, 90, 107)`

This yields approximately 90 degrees at 4:3 and 106.26 at 16:9, before accounting for exact x87 rounding. These are formula illustrations, not rendered/probed results. Zero height, trapping exceptions and arbitrary malformed settings still require machine-level treatment. The conditional unordered clamp path is now traced below; the mathematical summary is not a substitute for that contract.

The selected-dimension producer is traced in the [HUD](original-modern-hud-layout.md) and [resolution-default](original-modern-resolution-defaults.md) reports. A direct call at `004be748` computes the cached automatic angle in the viewport-initialization neighborhood. Later dimension changes must reach an appropriate update path for that cache to remain current; this chapter does not establish every reset/caller.

Modern chooser **`004dbc94`** returns binary32 bits in EAX according to `[006fbc40]`: 1→75.0, 2→90.0, 3→105.0, zero or other values→cached automatic value. Original chooser **`004dbcc0`** instead returns an integer: setting 1→75, every other value→90. These are corresponding choice roles at different addresses, not matching same-address bodies.

## Projection wrapper moves and changes its argument representation

Original projection wrapper **`004dbce0`** corresponds to Modern **`004dbcc0`**. Three paired calls change target accordingly: **`004becf7`, `004bed34`, `004bed61`**. These callers obtain four integer rectangle fields and push two additional arguments. Their direct linkage establishes the moved-wrapper correspondence; disassembling original at Modern's entry would instead find the old chooser.

Both wrappers convert incoming EAX/EDX/EBX/ECX rectangle values with signed FILD and pass them as floats to **`004bf260`**, along with two angles and the second stack argument. Both finish with `RET 8`. However, their first stack argument changes:

| Property | Original `004dbce0` | Modern `004dbcc0` |
|---|---|---|
| Incoming angle | Signed integer | Binary32 bit pattern |
| Horizontal half-angle | Signed truncation toward zero of input/2 | Input × float 0.5; stored binary32 |
| Vertical half-angle | Signed truncation of 13×horizontal-half/16, for ordinary fitting integers | `atan(tan(horizontal-half * degree_constant) * 0.75) * radian_constant`, stored binary32 |
| Extra local setup | Calls `004fd280` and `004fd3f0` before builder | No corresponding calls in this wrapper |

Modern's exact constants are retained: 0.5, degree factor **0.017453279346227646**, inverse factor **57.295780181884766**, and 0.75. The conversion factors are stored binary32 approximations, not exact π/180 and 180/π. The vertical calculation uses the extended x87 horizontal intermediate before its tangent operation, even though FST also writes a binary32 local. Reloading only that local prematurely can change low bits.

The 0.75 relationship is a reference aspect factor; this wrapper itself does not load live width/height to compute the vertical angle. Actual projection depends on the dimensions passed to the builder and other camera/state consumers. Do not claim that this one helper proves every widescreen effect is correct.

## The downstream builder is retained

Complete **`004bf260..004bf36f`**, 272 bytes, is byte-identical in both executables. Its seven stack inputs include four rectangle floats, horizontal/vertical half-angles and a final field. It uses the same degree constant and FPTAN-based projection arithmetic, storing globals near `0056009c`.

Equal body bytes do not imply equal results: the angle producers, argument representation, control word and source dimensions differ. Conversely, the changed wrapper is not evidence that this complete builder was rewritten.

## Removed integer projection-state implementation

The two calls absent from Modern's wrapper have concrete side effects in original:

- **`004fd280..004fd2a7`**, 40 bytes: EAX/EDX become origin DWORDs `0056442c/30`. Adding existing half-extents `00564424/28` produces centre values `00564434/38`. ECX is explicitly preserved; EAX/EDX are modified.
- **`004fd3f0..004fd41f`**, 48 bytes: converts EAX and EDX from degree-like units to low-32-bit `value*1024/360`, with signed division, then calls `004fd2b0`.
- **`004fd2b0..004fd3ea`**, 315 bytes: stores those angle inputs at `00564448/4c`, arithmetic-shifts EBX/ECX right by one into `00564424/28`, updates centre values from the stored origin, then derives scales at `0056443c/40` using signed arithmetic and lookup table `005672ac`. Its zero-second-angle path uses `00564450` and helper `004e8f28`. Complete lookup-table interpretation remains outside this chapter.

The evidence script verifies that **every byte of all three ranges is NOP (`90`) in Modern**, rather than treating them as still-callable retained functions. This establishes removal of these implementations at those addresses and their calls from the matched wrapper. It does not exclude reimplemented behavior elsewhere.

Original's wrapper supplies integer half-angles to these helpers before calling the separate float builder. Modern omits those integer-state updates and uses the float route. A port must not preserve obsolete address-based calls simply because original used them, or silently assume the old global block still has active projection semantics.

The shared float builder itself computes centre coordinates from rectangle origin plus half width/height in both binaries. That retained formula does not locate every horizon/camera shift: all origin producers, downstream consumers and renderer behavior still matter. This narrows **MP160-003** without claiming its complete explanation or a visual test.

## Reconstruction and catalog limits

**MP160-001**, automatic FOV/H+ mode: the dimension-based producer, clamp, cached selection and changed projection route provide static support for the mechanism. Exact v1.6.0 introduction requires prior-release binaries; UI labels and rendered horizontal coverage remain untested.

**MP160-002**, more accurate vertical angle: the paired wrapper replaces the original truncated integer approximation with the tangent/arctangent calculation above. For an ordinary90-degree horizontal input, original computes half-angle45 then truncates `13*45/16` to36; Modern's reference-aspect formula gives approximately36.87 degrees before its binary32 store. This concrete calculation change supports the claim partially. It is not a visual or whole-camera accuracy measurement: reference/live aspect, exact constants, downstream dimensions and x87 execution remain dependencies. The catalog therefore records partial support rather than leaving this mechanism vendor-only or declaring complete accuracy verified.

**MP160-003**, horizon/camera shift: the removed integer-state setup is traced above, but it is not a verified explanation of the entire advertised fix. Remaining origin/camera/renderer consumers must be compared first. **MP140-033**'s setting rename likewise needs UI/string mapping.

## Legacy centre references and removed integer point projector

The extended projection audit inventories every overlapping four-byte little-endian occurrence of `00564434` and `00564438` in each complete pinned executable. Original has four occurrences per address: viewport-finalizer stores, origin-helper stores, angle/extent-helper stores, and loads in `004fd420`. Modern has **zero occurrences** of either literal. The manifest records file offsets and mapped operand addresses, not fabricated instruction entries. This rules out retained direct absolute references using those literal encodings in the final EXE; computed addresses, aliases, external modules and generated code remain outside that search.

The audit additionally captures complete original **`004fd420..004fd482`**,98 bytes, and verifies every byte of that span is NOP in Modern. Original takes ESI pointing to three signed DWORD components and EDI to two output DWORDs. For component2 greater than0, it computes each output as a signed division of the wrapped32-bit product of component0/1 and scale `0056443c/40`, then adds centre `00564434/38` with32-bit wrapping. The product is truncated to32 bits before sign extension and IDIV; it is not a64-bit product divided before truncation. EBX/ECX/EBP are preserved locally; EAX/EDX are working state.

For component2 less/equal0, it writes `80000000h` to both outputs and ORs bit0 into byte `00564444`. A successful projection does not clear that byte here. This is an integer point-projection/status contract with unchecked input/output pointers, not an established universal camera or renderer ABI. Its complete caller reachability is not newly proven.

These results narrow the horizon investigation: following the old centre literals through retained Modern direct instructions is no longer a useful next step. Follow Modern's float rectangle-origin/centre producers and their renderer consumers instead. Removal of this legacy projector and its direct address literals does not by itself explain the advertised horizon position or prove every alternate projection path disappeared. No projection, renderer or game code was executed.

## Retained float centre producer reaches a retained projection consumer

The audit now includes complete paired geometry-consumer envelope **`0041bc90..0041bf26`**,662 bytes, and verifies exact equality. Combined with the already identical272-byte builder `004bf260..004bf370`, it establishes a concrete retained float-centre chain in both executables.

The builder's first four stack floats are rectangle originX/originY/width/height. It multiplies width/height by the same binary32 constant **0.5** at `005401c0`, stores half-extents at `005600ac/b0`, then stores **originX+halfWidth** to `005600a4` and **originY+halfHeight** to `005600a8`. The instruction order matters: halfWidth is reloaded from its binary32 store before addition; halfHeight is FST-stored but remains live in x87 for addition. These are shared original/Modern instructions, not a newly introduced Modern centre formula.

Within the consumer, **`0041be02..0041be39`** uses float scales `0056009c/a0`, a binary32 inverse-Z value and input component0/1, adds centre `005600a4/a8`, and writes the two projected coordinates. It also copies input component2 and the inverse-Z bits into the output record. Earlier processing/validation and later clipping remain part of the enclosing helper; this local expression is not a complete standalone projection ABI.

This establishes that the new analysis should focus on changed rectangle/camera inputs and other centre writers, rather than attributing the horizon claim to a changed centre-addition or this unchanged downstream projection body. The existing viewport-finalizer path is another writer of these float globals, so the builder is not a proven sole owner. Data/state, x87 precision, output ordering and actual camera/horizon remain unverified across runs; **MP160-003 stays unresolved**.

## Frame Size covering rectangle reaches the projection centre

Three existing audits close a specific Modern input chain: [Frame Size labels/storage](original-modern-frame-setting.md), [covering-rectangle construction](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles), and [wide-angle caller](scripts/audit_projection_callers_followup.py). This caller is used by the weather command builders, as established below; it is not by itself the ordinary scene-camera route. In the non-two-player branch, `004dbda0` supplies rectangle `007cdb88` to `004bed20` at `004dbdd6`. That helper passes the first four DWORDs as EAX/EDX/EBX/ECX to projection wrapper `004dbcc0` at `004bed34`; their FILD-to-float conversion reaches the retained centre builder above. The later +10h rectangle group is passed to a separate helper and must not be substituted for these projection inputs.

For ordinary nonoverflowing positive dimensions with Frame Size bit1 clear, constructor height is `S=(3*W)>>2` and base origin is `D=(H-S)>>1`. Full/Centered uses Y=D; Full/Shifted (bit0 set) uses Y=D+(D>>1). Session1 overrides the constructor flags to0 and the wide-angle wrapper chooses a different per-view rectangle, so this derivation deliberately excludes that branch.

For **1920x1080**, the resulting static input/centre examples are:

| Frame Size | Rectangle Y / height | Derived centreY stored at `005600a8` |
|---|---|---:|
| Full, Centered | -180 /1440 | 540 |
| Full, Shifted | -270 /1440 | 450 |

These are exact arithmetic illustrations for this initialization route, not captured frames or a proof that this wide-angle caller is the active path in every camera. Odd dimensions retain arithmetic-shift rounding; later resize/finalizer writes can change the inputs/state. The path establishes how the labelled setting can change the projection centre independently of changing the centre-addition formula. It supports the existing partial MP160-004 mechanism, while camera orientation, final horizon location and MP160-003's universal visible claim remain unresolved. No game or instruction probe was executed.

## Original rectangle counterpart: numeric setting values are not interchangeable

The viewport audit now retains explicit mathematical examples from both initializers/setters. In original's non-two-player branch, setting0 gives the first rectangle the physical height H and originY0. Nonzero setting instead computes letterbox offset `L=truncate((H-truncate(W/2))/2)` and uses first-group originY=`truncate(-L/2)` with height H; its second group uses originY=L and height `truncate(W/2)`. These signed truncations must not be replaced by Modern's arithmetic shifts for arbitrary negative intermediates.

The verified setters `004beb00` and `004beb40` write the first and second groups respectively. Thus, for **1920x1080**, the initial covering-group centre values are:

| Version / setting | OriginY / covering height | Derived centreY |
|---|---|---:|
| Original0 | 0 /1080 | 540 |
| Original1 | -30 /1080 | 510 |
| Modern0, Full Centered | -180 /1440 | 540 |
| Modern1, Full Shifted | -270 /1440 | 450 |
| Modern2, 2:1 Centered | -180 /1440 | 540 |
| Modern3, 2:1 Shifted | -300 /1440 | 420 |

The source dimensions, physical/fitted group and projection angles differ as well; matching centre540 is not matching projection. Reusing original ordinal1 as Modern ordinal1 also does not preserve its old framing. At640x480, original1 and Modern3 both derive centre200, but that equality is a scoped arithmetic example, not a general migration rule. The [Frame Size report](original-modern-frame-setting.md) retains the paired option IDs and official-label provenance limits.

These before/after values narrow the camera-shift investigation without claiming a complete horizon explanation. The examples assume the inspected initial non-two-player route, ordinary fitting dimensions and no intervening rectangle writes. They were generated from static formulas in the viewport audit, not by running either game.

## Wide-angle caller scope: temporary weather projection

The caller follow-up audit now retains complete paired envelopes `004dece0..004dedea` and `004dedf0..004dee71`, both byte-identical across versions. Existing analysis labels them weather-particle and weather-overlay command builders. Their explicit wide-angle calls are **`004ded7a`** and **`004dee36`**; each reaches `004dbda0` with its context pointer. The audit scans every E8/rel32 target candidate in each first code section and finds only these two, corroborated in the retained caller instructions. This is bounded direct-call coverage, not exclusion of indirect callers or jumps.

Both builders later call `004dbde0` with context, at `004dedd2` and `004dee58`, after their command-building work. That routine reselects a projection based on context/session and the configured-angle chooser. The temporary weather setup therefore must not be described as the universal active camera or proof of the scene's final horizon. Its shared wrapper still requires the verified original integer120 versus Modern binary32-120 ABI adjustment.

The following section compares the context-dependent ordinary selector at `004dbde0`. The temporary-path examples do not establish global projection ownership or rendered output.

## Ordinary projection selector: retained dispatch with changed angle ABI

The caller audit now includes complete paired **`004dbde0..004dbee6`**,262 bytes. Exactly three bytes differ, at `004dbe00`, `004dbe25`, `004dbe42`: the three CALL displacements retarget original integer-angle chooser `004dbcc0` to Modern float-bit chooser `004dbc94`. All remaining body bytes are identical. Both retain this rectangle dispatch:

| Condition | Rectangle supplied to `004bed20` |
|---|---|
| Context DWORD0==1 | `007cdb48`, the separately initialized mirror rectangle |
| Other context, session `006fd3b0==1` | `007cda80 + wrap32(context[+4] << 5)` |
| Other context, other session | `007cdb88`, the covering rectangle |

The mirror branch chooses EBX as the logical inverse of nonzero `006fd4c4`; the other branches forward that global directly. Each obtains its angle through the version-specific chooser, moves its EAX result into EDX and calls the retained rectangle/projection adapter. The caller's source instructions match, but angle representation and downstream wrapper differ as already documented.

On the non-mirror path, the tail resolves a per-view pointer through `005e10b8`, falling back to `005e10b0`, and tests object DWORD+54h with mask`7fffffffh`. A nonzero magnitude replaces **scale** `0056009c` with halfWidth times that binary32 field and scale `005600a0` with negative halfHeight times the field times retained binary64 **1.34834** at `0054972c`. A nonzero `006fd4c4` then toggles the horizontal scale sign bit. This tail does **not** write centre `005600a4/a8`. Pointer/index validity, field identity and complete writers remain unresolved; signed zero skips the override while NaN bit patterns can enter it if execution proceeds.

This closes the ordinary non-two-player covering-rectangle input link, independently of the temporary weather path. The earlier Frame Size centre examples therefore also apply to this selector's covering-rectangle branch under the same initialization/state premises. The selector preserves EBX/ECX/EDX/ESI/EBP and has no stack arguments; EAX is working state, not an asserted status result.

The static difference here is changed angle selection/interface, not a rewritten context dispatch or an added centre-offset formula. Other centre writers and camera orientation still prevent a complete MP160-003 horizon claim. No projection, camera or instruction probe was executed.

## Complete literal-reference inventory of the float centres

Run `python3 analysis/scripts/audit_projection_centre_references.py`. The [manifest](evidence/audits/projection-centre-references.json) binds both executable hashes, searches every overlapping four-byte encoding of `005600a4/a8` across each complete file, and corroborates each containing six-byte instruction in fresh `objdump` output. All matches are absolute x87 memory operands; no unmatched literal was silently dropped. This is linear-disassembly/literal coverage, not control-flow reachability or general alias recovery.

Each binary contains **40 references per centre**, including **two stores per centre**. The horizontal centre has25 FLD,9 FADD and4 FSUB reads; the vertical centre has29 FLD,5 FADD and4 FSUB reads. The four stores are:

| Writer | Original centreX / centreY stores | Modern centreX / centreY stores |
|---|---|---|
| Rectangle/angle builder `004bf260` | `004bf2a0` / `004bf2a6` | Same |
| Conditional viewport finalizer `004213b0` | `00421415` / `00421425` | `004213e6` / `004213f2` |

Both writer contracts are already paired above: the builder computes origin plus half extent; the finalizer conditionally copies selected cached float values, with changed load/store scheduling. No additional direct literal centre writer was found. Matching reference counts do not establish equal execution, inputs or results.

The horizon investigation can now stop searching for an unidentified direct absolute centre store in these EXEs. Remaining ownership questions concern which of these two writers executes last, cached-value producers, computed aliases/external code and camera orientation. The catalogue's unresolved horizon claim is retained; this audit provides no rendering or runtime-order proof.

## Conditional finalizer sources: storage known, producers unresolved

The projection audit now records the storage boundary and complete literal occurrences for `005e1020`, `005e102c`, `005e1030` and `005e1038`, copied by the type8 finalizer path. All lie within the declared `.bss` extent in both executables. Its header has uninitialized-data attributes `c0000080`, raw offset0 and noncanonical size fields (VirtualSize0 with the declared extent in SizeOfRawData). There are no established file-backed initial values for these cells. As already qualified in the [readiness audit](recompilation-readiness.md), loader zero-fill is an **inferred expected contract**, not a measured Windows/Wine initialization result; file offset0 must not be read as these floats.

For `005e1020`, `005e102c` and `005e1030`, each full executable contains only the one literal address operand in that finalizer. The literal search therefore reveals no direct absolute producer for those three source cells. `005e1038` additionally occurs in two indexed stores at instructions `00423a7c` and `00423a89`; their effective destination depends on EAX, so these do not establish unconditional initialization of this exact cell. That fourth source feeds the vertical scale, not the centre pair. Bulk copies, computed addresses and aliases remain possible and have not been excluded.

Accordingly, earlier references to these values as “cached” describe their conditional restoration role only; a capture/cache writer has **not** been recovered. The precise follow-up is to find a bulk/alias producer, or establish that the type8 path is inactive in the relevant camera configuration, then qualify its ordering against the ordinary builder. Do not assume zero source centres, successful capture or permanent ownership from the section attributes alone. This is a genuine bounded unknown, not a reason to defer unrelated executable comparisons. No loader, camera or game code was run.

The indexed-store candidate is now narrowed further by the hash-pinned projection audit. The complete `00423a60..00423aab` body is identical in both baselines. On normal entry, `00423a79` clears EAX and `00423a7b` increments it before the first store. The loop fills indices1 through25, hence DWORD addresses `005e103c..005e109c` inclusive. Neither of the two literal `005e1038` indexed stores initializes that base cell, nor either centre source, on this path. This removes that initial fill as a candidate producer; it does **not** establish that the source cells have no writers. A subsequent store at `00423a9d` uses `005e103c+4*EDX`, with EDX derived from `00423a20` results; its admissible indices and alternate interior entries remain unqualified. The next producer search must follow those results or bulk/computed aliases rather than treating the literal base address as a write to index0.

The follow-up pins the complete retained iterator `00423a20..00423a5e`, also byte-identical. Nonzero input EAX resets its cursor; it returns successive nonzero DWORDs from `006fbbc0..006fbbcc`, or0 at exhaustion, saving the cursor at `005e10c0`. The inspected initializer calls this reset first, so the four-cell scan is bounded absent intervening mutation. Crucially, the iterator bounds the **number of table entries**, not the numeric values returned. Those values become the later store's EDX index (with fallback2 if the first result is0). A producer/value invariant for the table is therefore still required before excluding writes outside the intended array.

With wrapped 32-bit x86 address arithmetic, reaching `005e1038` from `005e103c+4*EDX` requires EDX congruent to `3fffffff` modulo `40000000`; the corresponding residues for source cells `005e1020`, `005e102c` and `005e1030` are `3ffffff9`, `3ffffffc` and `3ffffffd`. The audit records all four 32-bit representatives for each. These are conditional alias calculations, **not observed table values or evidence of corruption**. Assuming small positive identifiers would exclude these aliases, but that assumption has not yet been established. No original/Modern difference was found in either of these complete bodies.

Existing [camera-contract research](ccm-camera-contract.md#four-camera-setting-sources) supplies the relevant producer, now rechecked against both hash-pinned executables: `00472300..00472355` is identical and publishes the four table values from settings `006fbba8..006fbbb4`. Each is a signed WORD lookup at `0055629e+2*index`, implemented by a DWORD load at `0055629c+2*index` followed by arithmetic shift16. The seven verified indices0..6 yield `[0,1,4,3,2,5,6]` in both versions. Thus **for that index domain, after this producer and without intervening mutation**, the successor construction cannot write any of the four projection source cells. This closes the suspected path under an explicit configuration invariant, not globally: the mapper has no local index validation, and accepted menu extent, alternate writes and call order remain separate questions. Following this retained camera-successor mechanism further is not needed merely to explain a Modern-only projection change; the actual type8 capture/alias producer remains the next relevant projection gap.

A native translation must preserve the integer-versus-float ABI change, binary32 spills, x87 transcendental operations/control-word assumptions, wrapping integer intermediates and exceptional-input behavior. Ordinary C `double` plus libm is not proven bit-equivalent. No runtime FOV, replay or multiplayer claim is made here.

## Viewport finalizer drops legacy projection updates

The audit now retains complete paired envelope **`004213b0..00421441` (145 bytes)**, exclusive end. All changes lie in **`004213d4..00421430`**. Modern’s saved body union excludes the42-byte NOP gap`00421406..00421430`, so its103-byte saved-function size is not the complete paired envelope size. The unchanged prefix calls`004dbde0`, indexes the pointer table`005e10b0` using context DWORD+4, and enters the changed block only when the pointer is nonzero and its first DWORD equals8. The shared suffix clears the corresponding DWORD in table`00552ff4` and returns. Index bounds and the initial callee’s contract remain dependencies.

Both versions retain these binary32 FLD/FSTP mappings:

| Source | Destination |
|---|---|
| `005e1020` | `0056009c` |
| `005e102c` | `005600a4` |
| `005e1030` | `005600a8` |
| `005e1038` | `005600a0` |

Original additionally performs direct DWORD copies **`005e10a0→0056443c`**, **`005e1034→00564440`**, **`005e1024→00564434`**, **`005e1028→00564438`**. Modern removes all four on this path. The earlier legacy projection analysis identifies these destinations as scale/centre cells used by the old helper family; their other writers/users and live values are not fully inventoried here. This is a concrete removal of updates, not proof that the cells never change elsewhere.

Original loads all four floats before storing, with FXCH-based ordering and temporary x87 depth4. Modern pairs each load/store at depth1, stores in a different order, then jumps over NOPs to the shared suffix. For ordinary accessible finite inputs the destination mapping matches; x87 overflow, signaling NaNs, unmasked exceptions, interrupted/shared data and status bits can distinguish the sequences. Do not replace them with an assumed full machine-state-equivalent memory copy or treat this as a new80-bit storage format.

The bounded difference is removal of legacy projection-cell updates plus changed x87 sequencing under the type8 condition. Full viewport type meaning, renderer visual effect and historical release attribution remain unresolved. No viewport or floating-point instructions were executed.

## Fixed wide-angle caller follows the new angle representation

The complete same-address wrapper `004dbda0..004dbddf` (63 bytes, exclusive end), saved as `ApplyWideAngleViewGeometry`, differs in only six bytes. The two immediate EDX assignments at `004dbdb1` and `004dbdc6` change from DWORD `00000078` (integer 120) to `42f00000` (binary32 120.0). The selected branch still depends on `006fd3b0 == 1`, selects either `007cda80 + 32 * incoming_object[+4]` or fixed record `007cdb88`, loads EBX from `006fd4c4`, then calls `004bed20` at `004dbdd6`.

As established above, `004bed20` pushes EDX as an angle stack argument before calling original `004dbce0` or Modern `004dbcc0`. This wrapper's changed immediate is therefore an interface adaptation, **not a change from 120 degrees to a different numeric angle**. The changed downstream half-angle calculation can still change projection output. Reconstructing Modern's immediate as integer 120 would supply the wrong floating-point bit pattern.

## Four-point scaling constants move without changing their values

The full `00495190..00495223` helper (147 bytes), saved as `ScaleFourFloat2PointsByViewportFactors`, differs in only four bytes, all in two FMUL address operands:

| Instruction | Original constant address | Modern constant address | Identical little-endian bytes | Binary32 value |
|---|---|---|---|---:|
| `004951c2` | `0053be28` | `0053bdd4` | `cdcccc3a` | 0.0015625000232830644 |
| `004951d5` | `0053be2c` | `0053bdd8` | `8988083b` | 0.0020833334419876337 |

These are binary32 approximations to 1/640 and 1/480. The source signed DWORDs are obtained through retained call `004beb20` on record `007cdac0`, converted with FILD and multiplied by the respective constants. The helper scales four incoming float pairs supplied through EAX/EDX/EBX/ECX, using the retained x87 sequence and binary32 output stores. It does not establish that every caller supplies disjoint writable pairs or that the selected viewport record is identical at runtime.

The byte comparison proves that this helper's changed operands are constant relocation with **no changed numeric constant**. It does not prove all x87 machine state or rendered results are identical under different inputs/control words. Aliased destination pairs can also make operation order significant, so a reconstruction should preserve access order until caller aliasing is qualified.

Both follow-ups are reproduced by [the projection-caller audit](scripts/audit_projection_callers_followup.py), with full body hashes, retained disassembly locations and exact constant bytes in [its manifest](evidence/audits/projection-callers-followup.json). **Bounded work status: done; confidence: verified static evidence.** No rendering, instruction probes or Ghidra writes were performed. All broader projection and runtime limitations above remain applicable.

## Automatic FOV unordered clamp and machine outputs

The expanded projection audit checks the exact FCOM/FNSTSW/SAHF/branch/FXCH/FSTP sequences at `004dbc6e..004dbc8a`, both stored bound constants and the final binary32 store. This closes a local unordered-branch gap in the earlier finite-value summary. It is a **symbolic instruction/stack trace**, not a new NaN, zero-height or game probe.

Immediately before the lower comparison, ST0=90 and ST1=candidate. For a comparison reporting unordered, C0/C2/C3 are1; FNSTSW AX / SAHF makes CF=ZF=1. The lower **JBE** at `004dbc73` is taken, so FSTP ST0 discards90 and leaves the unordered candidate. The upper pass loads107; its **JAE** at `004dbc84` is not taken with CF1, so FXCH followed by FSTP discards the candidate and retains107. The final store at `004dbc8a` therefore writes exact binary32 **107.0** if both comparisons report unordered and execution continues without trapping.

| Candidate classification at clamp entry | Normal local outcome |
|---|---|
| Ordered below90 | 90 |
| Ordered90..107 | Candidate, with final binary32 store |
| Ordered above107 | 107 |
| Both comparisons unordered, non-trapping continuation | 107 |

Do not replace this with a generic NaN-preserving clamp or assume a different bound is chosen for unordered input. This analysis does not establish which malformed dimension combinations reach that state, how unmasked exceptions are delivered, or a safe contract for every width/height. The helper contains no local FINIT/FLDCW; ambient precision/rounding/exception state remains material.

Its useful output is the store to **`0055fecc`**. No ordinary scalar return is constructed: FNSTSW writes AX twice, and the second snapshot remains in low16 EAX while high16 EAX retains the entry value. SAHF also changes integer flags. Later floating instructions can alter x87 status, so that captured AX is not asserted equal to the final status word. A C interface must not treat this residue as a reliable angle or success Boolean, nor silently claim full register/flag/state equivalence from a matching stored float.

The two Modern-only observer-index sites `004dbc70/004dbc81` are therefore explained by this existing automatic-FOV mechanism, rather than two independent patch features. Same-address original code belongs to a different function envelope; the earlier paired producer/chooser/projection evidence supplies the version context. Caller EAX/flag liveness, actual cache-update frequency, rendering and historical introduction remain unverified. Executable bytes, Ghidra, raw exports and maintained C are unchanged.

## View Angle option list and release-note correspondence

The projection audit now pins descriptor `00556758`: both versions name `viewangle` and store its ordinal at `006fbc40`, the exact cell consumed by the paired choosers. Original points to the terminated WORD list at `005561e8`, IDs274/275; final Modern points to `005591ec`, IDs1947..1950. Official final-package English decodes these as follows; original retail text provenance is not established.

| Build | Ordinal | Label from official final English | Verified chooser result |
|---|---:|---|---|
| Original | 0 | Wide | integer90 |
| Original | 1 | Narrow | integer75 |
| Final Modern | 0 | Automatic | cached binary32 angle |
| Final Modern | 1 | Narrow (75°) | binary32 75 |
| Final Modern | 2 | Normal (90°) | binary32 90 |
| Final Modern | 3 | Wide (105°) | binary32 105 |

This provides partial static support for MP140-063: the retained narrow angle is75, original's90-degree option corresponds numerically to final Normal, and final Wide supplies105. The source bullet describes an intermediate three-option list; the inspected final build has four entries including Automatic, consistent with its later automatic-angle mechanism. Original-versus-final cannot verify the exact v1.4.0 list or introduction date. Persisted ordinal0 also changes meaning from fixed90 to automatic; equivalence of configuration files requires explicit migration policy rather than copying indices and assuming identical behavior. Actual accepted UI writes, saved-setting migration, all camera callers and rendered output remain separate; descriptor/chooser linkage alone does not prove those paths.

### Default/reset path explicitly selects Automatic

The paired graphics-default envelopes retained in the [display-mode report](original-modern-display-modes.md) resolve a concrete producer beyond the option descriptor. Modern `00472d92` clears EDX, then `00472d9a` writes that zero into `006fbc40`, selecting Automatic through the verified chooser. The projection audit asserts the14-byte sequence and hashes the complete original `00472d10..00472f18` and Modern `00472d10..00472e1c` envelopes. The complete original envelope contains no literal operand for this selector, so the Modern direct reset write is additional within this bounded comparison; computed or transitive original writes are not excluded.

The [configuration-load report](original-modern-config-loading.md) identifies the invalid-size/version route into this default routine. Consequently this is an explicit reset/default policy, not evidence that every startup discards a saved View Angle. Full serialization/migration and later menu writes remain unresolved. In a reconstruction, keep that reset policy distinct from merely interpreting a loaded ordinal: both can select0, but their causes and compatibility implications differ. No settings file or running game was changed.

## Indexed viewport-slot initialization is another bounded non-producer

The source search now checks a computed-address candidate that a literal-cell scan alone misses. Paired initializer witnesses `00422cf0..00422d9b` and loop tail `00423845..0042386b` are byte-identical and retained by the projection audit. EBX starts0; the saved upper bound is1 when session `006fd3b0==1`, otherwise0. The normal loop increments EBX at `00423865`. Its two clear stores at `00422d78/00422d86` target `005e1010+8*EBX` and `005e1014+8*EBX`.

For that ordinary index domain, those stores cover only DWORD cells `005e1010..005e101c`; they do not initialize the type8 sources `005e1020/2c/30/38`. This exclusion assumes intervening callees preserve the loop state; it does not establish a whole-program bound for other indexed writers using the same bases. In particular, merely noticing that index2 would numerically reach `005e1020` is not evidence that this initializer runs index2.

The separately recovered [Modern scene snapshot helpers](original-modern-viewport-pose.md#extractionblend-identity-and-fixed-descriptor-producers) write the disjoint fixed descriptor at `00661220`, so that established copy is not itself a write to these source cells either. The actual type8 producer/admission and ordering remain unresolved. The useful remaining search is other bulk/computed writers or the type8 selection route, rather than repeating direct-cell scans or treating unrelated scene snapshots as the missing cache capture. No scene initialization or projection code was run.

## Type8 cannot be dismissed as an absent descriptor

The paired file-backed mode-table row at `00552f08` (`00552ec8+8*8`) contains two nonzero pointers, `005de578` and `005de6ac`, in both executables. The expanded initializer witnesses include the common type store `00422dd8` and mode-loop tail `0042383f..0042386b`: ordinary iteration visits modes1..24 and stores the current mode number at descriptor+0. Slot initialization is0, or0/1 for session1, under the previously stated loop-state/callee assumptions.

Consequently, a null row or absence of ordinary mode8 initialization cannot establish that the finalizer's type8 branch is dormant. The table's descriptor addresses are also distinct from projection source cells `005e1020/2c/30/38`; table existence supplies no missing capture writer. Actual publication into primary table `005e10b0`, selection gates and call order must still be followed before claiming that the finalizer executes with those descriptors. This closes an exclusion hypothesis, not runtime reachability or source initialization. The remaining horizon claim therefore stays unresolved. No constructor or camera code was executed.

## Retained CCM fallback can publish the type8 descriptor

The audit now compares complete selection helper `004238b0..00423959` and caller prefix `004251f0..00425232`, both byte-identical in original and official Modern. The caller invokes CCM selector `00423d90` with the context's slot at+0ch. On result`ffffffff`, it requests mode8 through `004238b0` at `00425218`, then dispatches mode8 at `00425228`. Existing [CCM fallback research](ccm-camera-contract.md#empty-count-selector-fallback) establishes one selector-failure condition; actual track/session occurrence remains unmeasured.

For requested mode8, the selector helper bypasses its special callback cases3/4/5/6, indexes `00552ec8+8*8+4*slot`, and publishes the resulting pointer into `005e10b0[slot]` at `0042394d`. With ordinary initialized slot0/1 state and no intervening table mutation, this is the type8 descriptor established above. Thus there is a concrete conditional publication path into the same primary table read by finalizer `004213b0`; its branch cannot be dismissed solely as an unused static descriptor.

This narrows admission but does not establish finalizer call order after that fallback, pointer stability, or projection source initialization. The fallback itself does not directly capture the four source cells. The next decisive static question is the intervening update/finalization chain or another computed producer; runtime observation would be a separate acceptance layer. The publication mechanism is retained between binaries, while the type8 finalizer's changed stores/sequencing remain the already documented difference. No selector, camera or game code was executed.

## Finalizer is stage2 after the scene-render call

The audit now pins complete paired stage dispatcher `00421450..00421471`, preparation wrapper `00421380..004213a1` and viewport wrapper `004bc470..004bc529`; all are byte-identical. The viewport wrapper uses shared context `007a3d14`, publishing incoming viewport tag and slot before calling the dispatcher with EDX0 at `004bc4a4`. That stage runs the pose wrapper `004228e0`, then ordinary projection selection `004dbde0`.

For admitted viewport tags0/1, the wrapper next calls `0041bb50` at `004bc4f3` and scene renderer `004bc160` at `004bc4fa`, then calls the dispatcher again with EDX2 at `004bc509`. Stage2 invokes finalizer `004213b0`; the finalizer first recomputes ordinary projection through `004dbde0`, then tests the primary descriptor and conditionally restores the type8 source cells. Other dispatcher values do not imply that finalizer call.

This establishes local order and narrows the source search to state established before or during those stages, including the intervening callees. It does not prove that the descriptor published by a prior CCM fallback survives unchanged until stage2, or that the source cells were captured. Nor should a post-scene-call centre restoration be presented as proof of the earlier scene's rendered horizon: command buffering, later consumers and transitive rendering effects require their own evidence. The [night-lighting viewport context](original-modern-night-lighting.md) independently establishes tag/slot roles and optional-pass admission. No stage or renderer code was run.

## Scene pointer layout places the unresolved cells beyond the regular pairs

The projection manifest now retains all24 two-pointer rows for modes1..24 at `00552ec8`, verified identical in both executables. Their slot0-to-slot1 spacings vary from`110h` to`13ch`; type8 uses`134h`, while type1 uses`11ch`. The placement is incompatible with treating the observed pairs as consecutive elements of one common-stride array. It does not by itself prove every complete C structure size or exclude a shared base type with mode-specific extensions.

A useful packing model follows from those pointers: if each pair's spacing is used as its individual record extent, the24 pair blocks form an exactly contiguous range `005dda10..005e1010`, with no gaps or overlaps. **Verified:** the pointers, differing spacings and arithmetic adjacency. **Inferred:** that each spacing is the complete allocated structure size; field access/alias evidence is still required to establish that as a layout contract. The known type1 snapshot's11ch-byte copy independently matches one spacing, not every mode's schema.

In that model, projection source cells `005e1020/2c/30/38` lie beyond the regular scene pairs, following indexed viewport state beginning `005e1010`. This rejects the unsupported shortcut of treating the source cells as ordinary fields of the fixed type1 snapshot. It does not rule out out-of-domain indexed writes, a larger trailing object, bulk capture or other aliases. The actual source producer remains unresolved, and no memory allocation or structure boundary was observed at runtime. For reconstruction, keep verified pointer placement, inferred extents and unknown fields explicitly distinct.

## Nearby literal-base search finds no hidden data-held capture pointer

The projection audit now searches both complete executable files for all16 DWORD-aligned address values `005e1000..005e103c`, retaining every overlapping literal match and file offset. All matches map into the code-address range; no initialized-data-held literal of these exact values was found. In particular, nearby values `005e1018/1c` do not reveal an otherwise missed immediate or data pointer to the projection-source neighborhood. Original-only `005e1024/28/34` matches belong to the legacy finalizer loads removed in Modern; they are not producers.

This is a broader but still bounded negative search. It excludes a direct literal/data-pointer lead within that16-value domain, not arithmetic derivation from another base, unaligned address values, byte-offset aliases, encoded pointers or external code. It therefore leaves the actual writer unresolved and changes the next search toward computed stores or source-capture lifetime rather than repeating exact-address scans. No source-cell values or writes were observed at runtime.

## Complete type8 update handler is retained

The resumed audit pins all399 bytes of handler `00425060..004251ef`, through RET at `004251ee`, and asserts original/official-Modern equality. The [paired dispatcher mapping](original-modern-view-offset.md#complete-24-selector-dispatch-mapping) identifies this as selector8's target. Thus the inspected local update body is retained while the finalizer's legacy projection stores and sequencing differ. This is stronger than comparing a few call sites, but not whole-camera equivalence: the handler uses mutable context, other helpers and ambient floating-point state. Its mode label must not be treated as evidence that it captures the four projection-source cells. Required follow-up remains computed/bulk writer and capture-lifetime analysis, followed by finalizer ordering under actual state. No target code was executed.

## Interstage viewport flag helper is not the capture writer

Complete `004349a0..004349c1` (33 bytes) is now pinned and byte-identical in both EXEs. The viewport wrapper calls it at `004bc4ae`, between stage0 and the scene calls. It computes `(context DWORD0 == 1 ? 1 : 0) XOR raw DWORD[006fd4c4]`, stores that result at `00554e4c`, restores EDX/EBP and returns. This is a raw bitwise XOR, not a general Boolean normalization of arbitrary configuration values.

The exact body contains no calls and only this one data store. It therefore cannot capture the missing projection-source values on its ordinary path. This eliminates one concrete intervening callee from the writer search; it does not exclude the larger scene callees or establish every use of the resulting flag. The helper's retained instructions also cannot alone explain a Modern-only mirror-orientation change: input producers and downstream consumers remain relevant. No function was executed.

## Camera dispatch wrapper changes around the retained type8 handler

Following another indexed state-setting route exposes a distinct paired mechanism, without recovering the missing projection-source writer. The [camera-dispatch audit](scripts/audit_camera_dispatch_wrapper.py), run with `python3 analysis/scripts/audit_camera_dispatch_wrapper.py`, pins both complete wrappers at `00426450`, resolves24 table routes and retains the preparer/type8 bodies in [its manifest](evidence/audits/camera-dispatch-wrapper.json). Original ends exclusively at `0042655a` (266 bytes), Modern at `0042649a` (74 bytes); table data at `004263f0..00426450` is separate from either body.

Both take mode in EAX and slot in EDX, index descriptor table `00552ec8 + mode*8 + slot*4`, then call preparer `00426370`. The complete127-byte preparer is identical. Importantly, this lookup and preparer run **before** the unsigned `mode-1 <= 23` handler-range check. The later check therefore does not establish safe handling of arbitrary modes, slots or null descriptors.

Original uses a jump table whose targets are local stubs: each supplies EAX=descriptor, calls its handler and returns through the wrapper epilogue. Modern's table holds handler addresses directly; it supplies EAX=descriptor and EDX0 and performs an indirect CALL. Resolving old stub CALL operands establishes22 routes lead to the same handler addresses in both binaries. Modes15/22 instead change from direct wrapper return to the one-byte RET stub `00426290`. This is a representation/control-flow change, not24 new camera features.

| Selected mode | Original table target and handler | Modern target |
|---|---|---|
|8 | Stub `004264be`, CALL at `004264c0` to `00425060` | Direct `00425060` |
|15 /22 | Return epilogue `00426555` | RET stub `00426290` |
|20 | Stub `0042652a`, CALL to `00426290` | Direct `00426290` |

The399-byte type8 body is identical, but its wrapper contracts differ. Original explicitly saves EBX/ECX/ESI/EBP and supplies EDX=mode−1 at handler entry; Modern uses PUSHAD/POPAD and supplies EDX0. Thus Modern restores entry EAX and all general registers on ordinary return, while the original does not provide the same preservation contract. Neither should be invented as a common scalar-returning C interface without checking caller liveness and each handler's inputs.

After an admitted Modern handler returns, a new block tests `006fd3b0 != 1` and `006fd1cc != 0`. When both hold, it calls `004240c0` with EAX=`00661220` and EDX1 before restoring registers. That fixed descriptor is the same storage followed in the [viewport-pose report](original-modern-viewport-pose.md#extractionblend-identity-and-fixed-descriptor-producers). Original's stubs return without this post-handler block. The new block also follows the RET-stub modes; it does not run after an out-of-range mode takes the wrapper epilogue.

This supplies a concrete changed caller around the retained type8 code and another use of the fixed descriptor. It does **not** establish that `004240c0` captures projection cells `005e1020/2c/30/38`, that the descriptor aliases those cells, or that the horizon moves correctly. The projection source capture/lifetime and visible result remain unresolved. Next work on this branch must trace the fixed-descriptor handler's actual fields/callees or establish a producer alias; repeating literal-cell searches or treating handler-byte equality as whole-wrapper equivalence would miss the observed difference. No game, instruction, callback or Ghidra execution was used.

## Fixed-descriptor handler: changed control input and bounded write set

The camera-dispatch audit now retains complete paired handler `004240c0..00424252` (402 bytes), complete vector-add helper `004dffb0..004dfff3` (67 bytes), and complete orientation helper `00421570..004215b7` (71 bytes). Both callees are identical between original and Modern. Handler changes are confined to `00424101..0042416b`; its prefix and suffix outside that envelope are identical. This resolves the specific next step above for the fixed661220 call.

Original overwrites EDX with global `007922fc` at `00424101` before using it in the local branch. Modern first tests **incoming EDX** at `00424104` and later `0042413c`, and reads that global through EAX instead. Consequently the new dispatcher’s EDX1 is a meaningful added control input, not merely a redundant zero/nonzero convention inferred from the wrapper.

The handler begins with a three-DWORD local offset from descriptor+110h and a base vector from `[descriptor+4]+98h..a0h`. In the ordinary EDX0 path, zero global `007922fc` selects descriptor+50h=`3ca3d70a` (approximately0.02), first local component0, and a scaled object+11ch value for the third local component. Other paths set descriptor+50h=0. Under Modern EDX1, the first local component is also forced0 and the old availability/state-dependent branch is bypassed. In the EDX0/nonzero-global path, object+9a8h states0/1 select raw binary32−0.4/+0.4, while other states select0 in Modern; original specifically zeroes state2 and otherwise can retain the copied component. State-domain invariants and physical meanings remain unverified; preserve the machine branches rather than assuming all inputs fall in0..2.

The common suffix scales the second local component through `[descriptor+8]+10ch`, conditionally flips the third component's sign bit using the indexed flag at `0079c4a0`, transforms the vector with the object matrix at+0c0h, and adds it to the base vector via `004dffb0` with count1 and destination descriptor+14h. It then writes nine orientation DWORDs at descriptor+2ch, using either a forward36-byte copy or `00421570`. The latter negates binary32 elements0/1/2/6/7/8 with x87 FCHS and copies elements3/4/5 as DWORDs. Its floating stores are not a universal bit-preserving sign-XOR promise for exceptional values.

For the actual new wrapper arguments EAX=`00661220`, EDX1, the ordinary write set is:

| Destination | Mechanism |
|---|---|
| `00661270` | Descriptor+50h zero store |
| `00661234..00661240` | Three position DWORDs via vector-add helper |
| `0066124c..00661270` | Nine orientation DWORDs via copy/sign helper |

Ranges in this table have exclusive ends. Remaining writes are to stack locals. With valid source pointers, the verified helper contracts and forward string direction, these destinations do not alias the unresolved projection source cells `005e1020/2c/30/38`. There are no additional indirect/callback calls inside this handler. Thus this **specific fixed-descriptor branch is excluded as their capture writer**; no such exclusion is claimed for arbitrary descriptor pointers or other handlers.

The result still matters to the original/Modern comparison: an added caller uses a changed control input to update shared position/orientation data. It does not recover the projection-cache producer or establish a visible horizon correction. Those remain open, while this branch’s local effects no longer need to be guessed.
