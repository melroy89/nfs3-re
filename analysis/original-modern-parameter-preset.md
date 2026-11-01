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

## Confirmed downstream meaning: track-chain distance selection

The [track-chain detail comparison](original-modern-track-detail.md) supplies the downstream link for three preset fields. Its independently reproducible audit, `python3 analysis/scripts/audit_track_detail_difference.py`, pins complete paired builders/classifiers and their lookup table. The present preset audit supplies the upstream record writes and conversion mapping. Reusing those two sources establishes this chain without treating the numeric differences as an unidentified physics change:

| Preset fixed field | Converted binary32 field | Confirmed track-chain use |
|---|---|---|
| +28h | +34h | Builder at `0041ce55..0041ce6a` squares it and compares with X/Z squared displacement; below/unordered threshold result takes the rejection branch |
| +38h | +40h | Classifier's second threshold square separates return1 from return2 after the outer threshold passed |
| +3ch | +44h | Classifier's first threshold square separates return0 from the inner comparison |

Selected-record helper `0041d310` publishes `005dd0e0 + wrap32(index*84)` through `005dd830`; the [existing pointer contract](detailed-analysis-notes.md#indexed-84-byte-record-selection-0041d310) documents this mapping. The track-chain consumer reads exactly that selected pointer. Original/Modern classifier entry `0041aa60` differs: original first rejects context DWORD0==1; Modern moves mirror-quality handling to the caller. Do not model the same thresholds as identical whole-classifier behavior across versions.

For ordered finite values, the classifier compares `(+44h)^2` to its stack value, returning0 when below it; if that threshold passes, `(+40h)^2` below the input returns1, otherwise2. Equality passes each gate. Those selections index the track-detail table used for block-count and geometry-submission selectors. The compared builder derives the input from X/Z squared displacement. This supports describing these fields as **track-chain distance thresholds**; world-coordinate units, complete geometry submission and visible quality remain unverified. It does not establish a complete physical distance model for every record consumer.

The auxiliary `006fd1d8` used in Modern's second-record source advance is independently bound to **Rear View Detail** in the [track-chain/mirror policy](original-modern-track-detail.md#mirror-quality-moves-into-the-caller). Thus the table's extra source advance and the caller's classification adjustment share a verified setting. The consequences of both mechanisms together still depend on the active record, tag, current setting and floating-point state; one mechanism must not be substituted for the other.

Remaining field-semantic work includes other consumers, full selector/lifetime invariants and rendered effects. The following section further resolves +24h/+30h. No replay/multiplayer desynchronization or vehicle-dynamics change follows merely from these rendering-consumer links. No new runtime or instruction probe was used.

## Fourth preset field: retained geometry cutoff consumers

The preset audit now also compares selected-record publisher `0041d310..0041d349` and retained geometry envelopes `0041ae90..0041b2f4` and `0041b300..0041b63c`. All three are byte-identical between original and official Modern; the geometry envelopes total1,952 bytes. This proves retained consumer instructions, not identical generated geometry when preset data changes.

At `0041af7a..0041af93`, the first path loads selected pointer `005dd830`, loads the component at `ECX+8`, and compares it with selected-record binary32 **+30h**, the converted preset **+24h**. Ordered greater advances the item cursor by14 bytes and jumps to the loop continuation. Less/equal or unordered takes the JBE continuation, subject to ambient x87 exception behavior. The second path at `0041b3bf..0041b3d7` compares `ESI+8` against the same threshold, advancing ECX by14 bytes on ordered greater before skipping further processing. The audit asserts both local instruction sequences and their branch targets.

This establishes **a direct per-component geometry cutoff**, distinct from the squared-distance gates using +28h/+34h and +38h/+40h/+3ch/+44h. No squaring or unit conversion occurs in these local comparisons. Complete transformation/coordinate semantics are not newly proven here, so a physical view-depth or world-distance label remains qualified. Unlike the earlier squared-distance rejection, unordered values take the JBE continuation here; preserve the actual comparison policy in C.

The [track-chain builder](original-modern-track-detail.md#mirror-quality-moves-into-the-caller) submits through `0041b300`, establishing a surrounding render route. All four fields explicitly written by Modern's preset application now have confirmed rendering consumers. +20h/+2ch remains a pre-existing converted field with its wider role unresolved. Visible output, complete clipping, all caller domains and vehicle-physics effects remain unverified.

## User-facing binding: View Distance and the Full preset

The preset audit now retains the identical20-byte descriptor at **`00556730`** in both executables: name `viewlevel` at `00537fc8`, WORD-list pointer `00556252`, two zero fields and destination `006fbc28`. Its list is **184,183,182,181,0**. The hash-pinned official English member resolves those IDs to **Full, Far, Medium, Close**. Official `graphics.mnu` and `psgraph.mnu` bind controls to `listname=viewlevel`; the graphics title token is `kMenuADVGRPHViewDist001`. Archive/member hashes and matching lines are retained in the manifest.

Using the established [generic ordinal-list mechanism](original-modern-frame-setting.md), this maps the shared selector to **0=Full,1=Far,2=Medium,3=Close**. The executable descriptor is unchanged; it is the application mechanism and table values that change. The official menu evidence does not authenticate original retail asset files or prove active runtime language/menu selection.

For **Full (selector0)**, the original override makes the first record's +28h/+38h/+3ch equal. Their values after the exact1/65536 scale are:

| `006fd4c8` | `006fd3b0 == 1` | Original three thresholds | Modern three thresholds |
|---|---|---:|---:|
| Zero | No | 500 | 500 |
| Nonzero | No | 375 | 500 |
| Zero | Yes | 440 | 500 |
| Nonzero | Yes | 330 | 500 |

These particular integer thresholds are exactly representable as binary32. The table states the preset source/conversion values, not a runtime capture or proof of equal later squared arithmetic under different x87 precision. The previously established geometry/distance consumers give these changes a concrete render-selection role.

This provides **partial static support for MP100-013**, the improved Full view-distance claim. The adjective “better” and actual farther visible rendering require output validation. The following evidence additionally maps the night/two-player inputs relevant to MP100-014. Historical introduction is not dated by the original/final pair. No game, menu, asset code or instruction probe was executed.

## Night and two-player branch identities

The expanded audit resolves both raw branch inputs using retained descriptor/producer evidence in **both** executable baselines:

- **`006fd4c8`: Night setting.** Identical descriptor `00556460` names `night`, points to WORD choices229/228/0 and stores the ordinal at `006fd4c8`. The official English resource labels229 **Off**,228 **On**. Ordinary choices are0=Off and1=On. The apply routine tests nonzero; the descriptor does not prove every writer normalizes the value.
- **`006fd3b0 == 1`: two-player setup route.** Official `setup.mnu` binds `SETUP_TWOPLAYERBUTTON` to `nextmenu=mainsplt`. The identical first16 bytes of row `00555ee8` name `mainsplt` and reference callback `0045d360` through `00555ef4`. Its retained prefix stores1 to `006fd3b0` at `0045d36a`. The [descriptor layout](original-modern-menu-callback-table.md) distinguishes this slot from changed transition/finalization fields. The existing [two-player input route](original-modern-input-worker.md) independently shows value1 collects two player buffers. This establishes the authored route, not exclusion of alternate writers or an observed splitscreen race.

Together these identities and the Full table provide **partial static support for MP100-014**: original day/non-two-player supplies500; day/two-player440; night/non-two-player375; night/two-player330. Modern supplies500 in all four branches for the inspected first-record thresholds. This is the concrete source-value equalization mechanism across those named conditions; the rendering consumers are mapped above.

Farther rendered scenery, second-view selection, all active state/lifetimes, historical introduction and runtime compatibility remain unverified. Equal source thresholds do not establish identical images or floating-point machine state.

## Full/Far rear-view source values

The [paired mirror-record selection](original-modern-track-detail.md#mirror-tag-selects-the-second-preset-record) now confirms tag1 selects record1 after applying presets. For the non-two-player mode branch, the Modern source formula yields the following record1 values, listed as **+24h,+28h,+38h,+3ch before shifting left16**:

| Main View Distance | Rear View Detail | Day | Night |
|---|---|---|---|
| Full | High | 500,500,500,500 | Same |
| Full | Medium | 500,333,133,266 | 375,250,100,200 |
| Full | Low | 150,100,40,80 | Same |
| Far | High | 500,333,133,266 | 375,250,100,200 |
| Far | Medium or Low | 150,100,40,80 | Same |

These are existing manifest formula cases, with confirmed option labels applied. Under the earlier initialization premise, original's non-two-player apply leaves record1 at template3 values **150,100,40,80**. Modern therefore changes mirror-route source thresholds for Full at High/Medium and Far at High, while retaining those values for Full at Low and Far at Medium/Low. This gives further partial static support to **MP100-013**, whose full source bullet explicitly mentions rear view in Far/Full.

The table is not a statement of final visible distance: tag1 classification also applies the separate Rear View Detail adjustment, geometry cutoffs use other fields, and active record/lifetime, x87 state and rendering remain unobserved. In the two-player branch, the source advance is skipped and record1 has a different role-dependent context; the table deliberately states its non-two-player scope.

## Pre-existing +20h field: retained initialized value

The fifth converted field is distinct from the four Modern preset-table writes. For valid constructor template kinds0..3, both versions' identical insertion body stores **`fffb0000h`**, signed **-327680**, at record+20h through `0041dfc6` or `0041e00d`. Both constructor scale `00536d6c` and apply scale `00536ce4` are independently asserted as exact binary64 **1/65536**. Therefore the initialized stored binary32 value at +2ch is exactly **-5.0**, subject to the stated initialization/count and ordinary x87 execution premises.

Neither version's apply preset-store portion replaces +20h. Its subsequent conversion carries the existing signed value into +2ch; under this initialized value the arithmetic is exact at the supported x87 precision settings. Different instruction scheduling, status flags, exceptions and unrelated data remain separate equivalence questions. Unsupported constructor kinds can retain prior +20h storage, so -5.0 must not become an unconditional default for arbitrary records or entries.

This narrows the data reconstruction requirement: retain the existing +20h input and its constructor initialization, instead of treating all five converted fields as supplied by Modern's table. Its complete physical/consumer role remains unresolved; the verified value alone does not justify naming it a clipping plane or applying a corrective normalization. No target instruction or runtime probe was executed.

The selector also has a separate [retained world-effect scale consumer](original-modern-effect-renderer-masks.md#retained-view-distance-scale-in-the-world-effect-builder), with factors1.0/1.0/approximately0.85/0.7. The track-record rewrite must not be generalized to every use of View Distance; that other table and comparison remain unchanged.

## Shared field offset is not a consumer identity

A focused consumer check eliminates a plausible false match for the unresolved+2ch role. The audit now retains paired `0041ab40..0041ab6d`. Its read at `0041ab6a` uses base `00571370 + wrap32(EBX*1472) + wrap32(ECX*4)`, then offset2ch. That base is a different indexed record family, not a demonstrated alias of selected preset pointer `005dd830`. The common offset alone therefore does not identify a preset+2ch consumer or justify naming the initialized−5 value a clipping plane.

The practical reconstruction boundary remains clear: +20h signed fixed input, +2ch binary32 output and the initialized−5 value are verified; the physical field meaning remains opaque. Preserve that layout/value without inventing a role. This check is not an exhaustive read-absence proof, and copied/aliased uses remain possible. Resolving the role is not a prerequisite for explaining unrelated Modern preset-table differences. No target instructions or new probes were executed.
