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

## Derived original-versus-Modern integer examples

The same audit now records **64 static formula evaluations**: selectors0..3, both `006fd4c8` branches, both mode branches, and auxiliary representatives0..3. These are mathematical evaluations of retained code/table bytes, **not instruction probes or runtime tests**. Auxiliary values above3 give no further source-offset class for these selectors because the positive limit `3-selector` is at most3. Original fields without local writes are represented as unknown/untouched, never as zero.

**48 of64 evaluations differ in at least one field written by both versions.** The other16 only match those compared fields; they do not establish whole-record, float-output or machine-state equivalence. The count includes repeated auxiliary cases where the mode ignores that input and is not a percentage of game changes.

For `006fd4c8 == 0`, mode !=1, and auxiliary0, the first record gives the following raw DWORDs. Each tuple lists **+28h, +38h, +3ch**, before the x87 conversion loop:

| Selector | Original raw DWORDs | Modern raw DWORDs |
|---:|---|---|
| 0 | 32768000, 32768000, 32768000 | Same three values |
| 1 | 32768000, 7208960, 9830400 | Same three values |
| 2 | 18022000, 3964840, 5406600 | 18022400, 3997696, 5439488 |
| 3 | 13107000, 2883540, 3932100 | 13107200, 2883584, 3932160 |

This demonstrates a substantive value change before floating-point precision enters the calculation: original fractional fixed-point factors can leave low16 bits in these values, whereas Modern constructs every selected table WORD as `word << 16`. Modern also supplies +24h and second-record fields the original leaves unchanged in this mode. Thus even matching first-record tuples for selectors0/1 do not establish equivalent record state.

All formulas require valid accessible records, source reads and direction flag as documented above. The evaluated selectors are table-index examples, not a proof that every combination occurs in a race. Caller/global invariants and physical meanings remain the next evidence needed before attributing these differences to a specific gameplay effect.

## Retained selector setter, cycling and direct caller witnesses

The expanded preset audit now compares complete setter `0041d610..0041d61a`, complete advance helper `0041d870..0041d89d`, and callsite neighborhoods around `0041aaf6` and `0041da01`. All these retained spans are byte-identical between original and official Modern. Each of the three CALL operands is checked against target `0041d620`; these are confirmed direct callers, not proof of exhaustive indirect-call coverage.

- **Setter `0041d610`:** writes incoming EAX to `006fbc28`, restores its frame and returns. There is no normalization or apply call. Thus a valid cycle does not make every selector producer safe.
- **Advance caller `0041d894`:** loads the selector, increments with32-bit wrapping, publishes that incremented value, performs signed division by4, publishes the signed remainder, then applies the preset. Values0..3 cycle0→1→2→3→0. Arbitrary inputs can produce negative remainders; do not replace the routine with unsigned masking without qualifying its input domain. There are two stores, so the incremented intermediate value exists before the remainder store; no cross-thread observation or synchronization is established.
- **Object-position update caller `0041aaf6`:** saves its incoming EAX object pointer in ECX, applies presets, then supplies EDX as the record selector to `0041d310` before continuing with object+4. Its reliance on ECX/EDX surviving the apply call is supported by both versions' saved-register contracts. The [existing object/bucket analysis](detailed-analysis-notes.md) supplies the later consumer context; this new capture is deliberately only the entry/call prefix.
- **Initialization caller `0041da01`:** calls `0041d310` with EAX=0 immediately before applying, then invokes `00419b60`. The retained neighborhood establishes ordering, not a complete initialization/lifetime proof for every record field.

The original/Modern difference therefore sits inside an apply routine reached from retained initialization, preset advancement and object-update routes. That is stronger than treating the changed table as orphaned data, but still does not assign physical meanings to its fields or prove every enumerated input occurs. The [graphics-default table comparison](original-modern-resolution-defaults.md#tier-tables-occupy-former-original-code-final-loadstore-mismatch) is a further selector producer with version-specific tier values. Existing scene republishing only writes the same selector back through the setter; it is not an implicit bounds check.

## Record count: retained reset and unchecked append

The audit now includes complete original/Modern reset `0041deb0..0041def9` (73 bytes) and record insertion `0041df10..0041e069` (345 bytes). Both bodies are byte-identical. This supplies the missing local producers of count `005dd0dc`; it does not remove the changed apply-loop contract.

Reset writes count0 at `0041dec3` before its loop's external calls. It also publishes marker `1234h` at `005dd0d8`; its loop addresses record starts at `005dd0e0 + 84*index` and marks them `ffffffffh`. The local loop intends indexes0..3, but calls `004a33d0` on each pass with EDX live; its transitive register effects and count aliases are not newly audited here. Therefore the early count0 write is established, while atomic initialization or immunity to callback/global mutation is not.

Insertion reads the current count, forms the next destination as `005dd0e0 + wrap32(84*count)`, writes the record, then stores `wrap32(count+1)` at `0041e05f`. It has **no local count-capacity check** before accessing the destination. Its unsigned selector check against3 controls which record template branch is used, not whether count is within the array. Unsupported template selectors can still reach the conversion/increment tail with some fields left as prior storage. Record-pointer validity and template admission remain required preconditions.

Under a separately established sequential reset followed by a bounded number of insertions without alternate writers, the count stays nonnegative. These routines alone do not prove that lifecycle, a maximum live count, or negative-count reachability. Accordingly, Modern's negative-count LOOP behavior remains a **conditional contract difference**, not an observed failure: original's apply conversion skips negative counts; Modern treats every nonzero count as a decrementing32-bit loop. The unchanged count producers do not justify silently adding a clamp or declaring the problematic domain reachable. No record insertion/reset or target code was executed.

## Initialization-qualified values of previously untouched fields

The audit additionally verifies the four-target insertion jump table at `0041defc` and the initializer neighborhood `0041d9a3..0041da06`, all byte-identical across versions. That neighborhood resets records, then inserts **types1 and2 when mode==1**, or **types0 and3 otherwise**, before selecting record0 and applying presets. The table maps types1/2 to the same template. The four fixed-point template values at +24h/+28h/+38h/+3ch are:

| Template type | Values before shifting left16 |
|---|---|
| 0 | 500,500,110,150 |
| 1 or2 | 400,440,60,92 |
| 3 | 150,100,40,80 |

These are established producer values under the explicit sequential premise that reset establishes count0, the two insertions occupy records0/1, mode remains stable and no alias changes the compared fields before apply. They do **not** replace the earlier arbitrary-entry contract: original's apply still leaves those fields untouched locally. The manifest retains both views instead of assigning unconditional defaults to all calls.

With that initialization premise, the original mode!=1 second record remains `{150,100,40,80} << 16` after apply, while original first-record +24h stays `500 << 16`. Mode1 leaves +24h=`400 << 16` in both records and applies its three scaled values. Modern can either restate or change these known values depending on the selected table/source advance. For example, selector1, flag0, mode!=1, auxiliary0 retains the same first-record four fields but replaces the second record with `{500,333,133,266} << 16`; selector0 in mode1 changes both +24h values from400 to500.

Thus “Modern adds a write” is not itself proof that the live value changes. The new initialization-qualified formula evaluations distinguish matching stores from changed values without claiming the setup premise or every evaluated input was observed at runtime. Physical meanings, all alternate lifecycles and floating output remain separate.
