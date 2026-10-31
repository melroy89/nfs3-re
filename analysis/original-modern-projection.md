# Original versus Modern: automatic FOV and projection-angle interface

## Evidence boundary

Static supplied-original/official-Modern comparison; exact fingerprints are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_projection_difference.py`. The [manifest](evidence/audits/original-modern-projection.json) captures original/Modern angle helpers, three paired callers, Modern producer call, exact float constants and an asserted identical projection builder. No rendering, game or instruction probes were executed.

## Automatic angle producer and selection

Modern helper **`004dbc48`** loads signed DWORD width/height from `006fd1e4/006fd1e8`, divides width by height on x87, multiplies by file-backed float 0.75, applies FPATAN with 1, doubles and multiplies by float `57.295780181884766`. Ordered comparisons clamp the result to file-backed float limits **90** and **107**, then store binary32 at **`0055fecc`**.

For ordinary positive dimensions and finite arithmetic, its mathematical summary is:

`automatic_degrees = clamp(2 * atan(0.75 * width / height) * radians_to_degrees, 90, 107)`

This yields approximately 90 degrees at 4:3 and 106.26 at 16:9, before accounting for exact x87 rounding. These are formula illustrations, not rendered/probed results. Zero height, NaNs, unordered comparisons and arbitrary malformed settings require machine-level treatment; the summary is not a substitute for those contracts.

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

**MP160-003**, horizon/camera shift: the removed integer-state setup is traced above, but it is not a verified explanation of the entire advertised fix. Remaining origin/camera/renderer consumers must be compared first. **MP140-033**'s setting rename likewise needs UI/string mapping.

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
