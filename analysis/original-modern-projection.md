# Original versus Modern: automatic FOV and projection-angle interface

## Evidence boundary

Static supplied-original/official-Modern comparison; exact fingerprints are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_projection_difference.py`. The [manifest](evidence/audits/original-modern-projection.json) captures original/Modern angle helpers, three paired callers, Modern producer call, exact float constants and an asserted identical projection builder. No rendering, game or instruction probes were executed.

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

Three existing audits close a specific Modern input chain: [Frame Size labels/storage](original-modern-frame-setting.md), [covering-rectangle construction](original-modern-viewport-geometry.md#source-groups-covering-frame-versus-physicalfitted-rectangles), and [wide-angle caller](scripts/audit_projection_callers_followup.py). In the non-two-player branch, `004dbda0` supplies rectangle `007cdb88` to `004bed20` at `004dbdd6`. That helper passes the first four DWORDs as EAX/EDX/EBX/ECX to projection wrapper `004dbcc0` at `004bed34`; their FILD-to-float conversion reaches the retained centre builder above. The later +10h rectangle group is passed to a separate helper and must not be substituted for these projection inputs.

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
