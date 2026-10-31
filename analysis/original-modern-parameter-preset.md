# Original versus Modern: parameter preset application

## Evidence and layout

**Static comparison, no game/instruction probes.** Paired entry `0041d620` has corresponding selector globals and writes to the same 84-byte record array. Original complete body ends at exclusive `0041d863`; Modern ends at `0041d6e4`, immediately followed by data. Treating the following Modern bytes as instructions would incorrectly disassemble the preset table.

Run `python3 analysis/scripts/audit_parameter_preset_difference.py`. The [manifest](evidence/audits/original-modern-parameter-preset.json) retains baseline identities, complete disassembly/body hashes, original scale-table bytes, all 256 Modern table bytes decoded as unsigned WORDs, and the shared conversion constant. Existing field/selector research is in [detailed notes](detailed-analysis-notes.md), under preset selection and initialized 84-byte records.

## Original: adjusted selector and scaled constants

Original loads `006fbc28`, subtracts one, and clamps a signed-negative result to zero. It uses that adjusted index at DWORD stride four into a three-element local table copied from `0041a8b0` or `0041a8bc`, selected by whether `006fd4c8` is nonzero. This lower clamp is not an upper-bound check.

Branches also test `006fd3b0 == 1`. They multiply fixed-point literal constants by the selected table factor using signed IMUL followed by SHL/SHR/ADC extraction, then write record fields at the first and sometimes second 84-byte record. For example, the inspected nonzero-`006fd4c8`, mode-1 path uses constants `01b80000`, `003c0000`, `005c0000`; its other mode path uses `01f40000`, `006e0000`, `00960000`. These describe raw fixed-point operations, not inferred physical distances or field names.

If the unadjusted selector is zero, original copies first-record +28h to +38h/+3ch; for mode 1 it does the corresponding second-record copies as well. It then iterates with signed `index < [005dd0dc]`, converting five signed DWORD fields per initialized record to floats.

## Exact original integer arithmetic and write map

The expanded audit asserts all **12** original `IMUL; SHL EDX,16; SHR EAX,16; ADC EAX,EDX` sequences and their literal loads. Every literal is `N << 16`, with N from `{440,60,92,500,110,150}`. For any signed32 factor F, the signed64 product therefore has low16 bits zero. The last SHR's carry is original product bit15, hence **zero**. The final EAX is exactly **`wrap32(N * F)`**. This simplifies this particular sequence; it does not justify discarding ADC or rounding in unrelated fixed-point routines.

For the admitted local indexes0..2, the nonzero-`006fd4c8` branch uses factors **49152,26869,19660** from `0041a8b0`; its zero branch uses **65536,36044,26214** from `0041a8bc`. Both branches then use the same mode-dependent write map. Let R0=`005dd0e0`, R1=R0+54h, and `M(N)=wrap32(N*F)`:

| Mode condition | R0+28h | R0+38h | R0+3ch | R1+28h | R1+38h | R1+3ch |
|---|---|---|---|---|---|---|
| `006fd3b0 == 1` | M(440) | M(60) | M(92) | M(440) | M(60) | M(92) |
| Other | M(500) | M(110) | M(150) | No local write | No local write | No local write |

When the **unadjusted** selector is zero, the later override copies R0+28h to R0+38h/+3ch; mode1 additionally copies R1+28h to R1+38h/+3ch. Otherwise the table above stands. Original does not write record+24h in this preset-store portion, unlike Modern's four-field writes to each record. A later conversion reads pre-existing +20h/+24h as well; untouched fields are dependencies, not zero defaults.

These are complete local integer-store branches, without invented physical field names. Index formation is `signed32(wrap32(selector-1))`, replaced with0 if negative; it still has no upper bound. In particular, a C implementation must not use undefined signed overflow for the decrement or products. The three known scale factors only establish in-table cases; arbitrary selectors can read beyond the copied local table. Clear direction flag is also an implicit precondition for the original MOVSD table copies. No target instructions were executed to derive this formula.

## Modern: explicit table and two-record writes

Modern does not subtract one or locally clamp `006fbc28`. Initial source address is:

`0041d6e4 + wrap32(selector << 6) + (006fd4c8 != 0 ? 32 : 0) + (006fd3b0 == 1 ? 16 : 0)`.

It loads four WORDs for each of two records and shifts each left 16, storing DWORD fields +24h, +28h, +38h, +3ch. The source WORD occupies the high half regardless of prior EAX contents; this is raw fixed-point construction, not floating conversion. The first destination is `005dd0e0`, the second is +54h.

Between the two records, when mode is not 1, it computes signed wrapped `limit = 3 - selector`. If limit is positive, it advances the source by `min_unsigned([006fd1d8], limit) * 64`; otherwise it uses the next four WORDs in sequence. For mode 1 it always uses the next four WORDs. Thus the second record is not universally a copy of the first or the adjacent table block.

The retained table covers four selector blocks of 64 bytes, each containing four 16-byte subblocks. Selector 0 consists entirely of WORD value 500. For selector 1, zero `006fd4c8`, mode !=1, its first subblock is `{500,500,110,150, 500,333,133,266}`. The first four values feed record zero; the second four feed record one only when the extra source advance is zero. Exact values for every block are in the manifest. Arbitrary selector or auxiliary-state values are not validated merely because four blocks exist.

## Conversion and machine contracts

Both versions convert record signed DWORD +20h/+24h/+28h/+38h/+3ch to binary32 +2ch/+30h/+34h/+40h/+44h, using the same binary64 constant at `00536ce4` = **1/65536**. Modern keeps that constant in x87 across the loop and stores each result immediately; original uses a different x87 stack schedule and reloads per record. Shared scale and destination mapping do not establish floating-point equality under different control words or arbitrary inputs.

The count loop changes materially. Original starts index zero, compares signed-less-than count, and therefore skips a negative count. Modern loads ECX=count, uses JECXZ to skip **only zero**, then x86 LOOP decrements until ECX becomes zero. A negative count would produce a very large unsigned iteration count and accesses beyond an ordinarily bounded array. Existing producer research records reset/insertion roles but does not establish negative count reachability; this is a conditional contract difference, not an observed fault.

Both versions apply preset writes to the first/second record before the conversion-count gate, even if count is zero. Modern PUSHAD/POPAD preserves all general registers; original saves the six non-EAX general registers and does not establish the same EAX output. Neither routine claims a scalar C return.

**Verified:** paired bodies, changed selector/table construction, two-record stores, conversion field map/constant, exact original integer-store branches and count-loop boundary difference. **Unresolved:** selector/auxiliary-state invariants, semantic record labels, every caller, runtime effects and release attribution. No whole-game precision, replay or multiplayer conclusion follows from these parameter writes.
