# Original versus Modern: frontend slider percentage tail

## Evidence

Static paired function `00469680`, named `RenderFrontendSingleSliderWidget` in current analysis. Original complete body ends at exclusive `0046a5ea`; Modern at `0046a5af`. The first **3,755 bytes**, `00469680..0046a52b`, are byte-identical. The inspected code change is concentrated in the percentage-display tail rather than a rewrite of the entire slider.

Run `python3 analysis/scripts/audit_slider_percentage_difference.py`. The [manifest](evidence/audits/original-modern-slider-percentage.json) retains baseline fingerprints, complete body/disassembly hashes, exact common-prefix hash, format and raw constants. No slider/UI execution or numeric input probes.

## Changed admission and numeric mapping

Both first test a local gate at EBP+32h; nonzero skips the percentage tail. Original then accepts only entry byte **+3ch ==1**. Modern skips only **+3ch ==0**, so additional nonzero types enter; it treats type2 specially.

Both call `004693c0` with entry DWORD+54h and binary32 immediate `3c23d70ah` (approximately0.01). Calling that a particular sound/dead-zone setting requires its entry producers and helper semantics, not this field alone. Let its returned ST0 be `v`:

- Original admitted type1 computes `(v - 0.5) * 2 * 100` using FSUBR followed by FCHS and multiplications. It stores a binary32 intermediate, compares against zero and chooses a sign-dependent bias constant, stores again, then calls `004dfd56` before FISTP to integer.
- Modern type2 computes `(v - 0.5) * 2 * 100` with FSUB/FMUL. Other admitted nonzero types compute `v * 100`. It directly applies **FISTP** to the live x87 result, without the original intermediate binary32 stores, sign-branch or conversion-helper call in this tail.

The constants0.5,2 and100 are read from `0053ae70/74/78`. Algebraic correspondence does not establish bitwise results: removed stores change rounding points, direct FISTP uses the current x87 rounding mode, and signed zero/nonfinite/overflow inputs need separate treatment. The helper's valid output range and runtime control word are not proved by these instructions. A generic C cast would not preserve this machine contract.

## Formatting and draw

Both format through constant **`%d%c`**, supplying integer percentage and character `25h` (`%`), then call `00452190` with selector18. Modern moves the shared position calculation after formatting and subtracts an additional1 from the vertical-position arithmetic relative to the original sequence. Other coordinates combine the same two saved local fields plus10; full field units and actual visible alignment remain unresolved.

Both return EAX0 and restore EBX/ECX/ESI/EDI/EBP. The format destination starts at a local frame buffer with no capacity parameter on the formatting call; admissible integer formatting bounds and surrounding local overlap should be established before a reconstruction safety claim. Prior slider animation, color and value-state instructions belong to the verified common prefix, but their transitive callees/data may still differ.

## Catalog interpretation and next work

The final Modern mechanism is consistent with expanded percentage display and changed rounding. **MP150-021** (volume/alpha percentage display) and **MP153-011** (sound/dead-zone rounding) receive only partial static support: type admission and arithmetic are traced, but exact slider-type bindings, ordinary/boundary output cases, historical release introduction and rendered values are not verified.

Next: map entry+3ch type producers and `004693c0`'s output contract, inspect `004dfd56`, then define bounded numeric comparisons if runtime work is authorized. No gameplay, executable bytes or Ghidra changes were made.

## Quantizer identity and conversion-helper control words

The paired audit now retains complete `004693c0..00469479` and asserts its bytes are identical. Existing [quantizer analysis](detailed-analysis-notes.md#normalized-float-step-quantization) establishes its two stack binary32 inputs (step, value), ST0 result and RET8. For ordinary finite nonnegative values it quantizes toward the nearest step using a 0.5 fractional threshold, preserving exact integer-step values, then clamps toward [0,1]. Raw-bit comparisons, mixed quotient/floor rounding and exceptional inputs prevent presenting that shorthand as a universal mathematical contract.

Both percentage tails supply approximately0.01 as step and entry+54h as value. Thus the code change is after a retained quantization stage; it is not evidence of changing this helper's step algorithm. The ordinary [0,1] result interpretation requires the stated input assumptions, and does not assign each slider type a UI meaning.

Original bias constants `0053ae7c/80` are binary32 **approximately−0.005/+0.005**. The tail selects them according to its x87 zero comparison, stores a rounded binary32 result and calls `004dfd56`. Modern no longer uses those bias locations in its percentage tail; the same addresses contain zero bytes in the inspected final binary. Their address reuse must not be mistaken for the original constants still participating in the new path.

The conversion helper itself is also different:

| `004dfd56` implementation | Temporary control word | Conversion and restore |
|---|---|---|
| Supplied original (`..004dfd73`) | Save current word, preserve its low byte, replace high byte with **1fh** | FSTCW/FWAIT, FLDCW, FRNDINT, restore saved word, FWAIT |
| Modern (`..004dfd6d`) | Literal **0c3fh**; save prior word in the other half of the temporary DWORD | FNSTCW, FLDCW, FRNDINT, restore saved word |

Both words request RC=11 (toward zero). Original's forced high byte also sets PC=11; Modern's literal sets PC=00 and masks all six floating exceptions in the low six bits. Original instead inherits those low-byte masks. This describes installed control bits, not a claim that precision-control bits alter FRNDINT in the same way as every arithmetic instruction. Waiting/nonwaiting save sequences and exception handling also differ; those are machine-state contracts outside a plain integer return.

The original percentage tail invokes its original conversion helper before FISTP; Modern's changed tail invokes neither implementation and uses direct ambient-rounding FISTP. Consequently “both executables contain a truncation helper” would not establish identical slider rounding. Ordinary/boundary numeric comparisons and exact active control words remain untested in this phase.

## Installed percent-type definitions and parser descriptor

The [selected menu inventory](evidence/inventories/installed-slider-percent-types.json) records nine case-distinct installed/local backup files named `audio.mnu`, `advgrph.mnu` or `cedbasic.mnu`, including source hashes, section lines, codelinks and raw `percenttype`/`slidertype` values. It is a bounded text inventory, not a full parser emulation or proof of runtime file choice.

Installed `FEDATA/MENUS` definitions establish:

| File | Codelinks | percenttype |
|---|---|---:|
| `audio.mnu` | `ASLD_MENUMUSIC`, `ASLD_MENUSOUND`, `ASLD_RACEMUSIC`, `ASLD_SOUNDFX`, `ASLD_ENGINEVOLUME`, `ASLD_SPEECHVOLUME` | 1 |
| `advgrph.mnu` | `SFX_INTENSITY` | 1 |
| `cedbasic.mnu` | `CE_ENGINETUNE`, `CE_BRAKEBAL`, `CE_STEERINGSPD`, `CE_BGRRATS`, `CE_SUSPENSION`, `CE_AERODYN`, `CE_TIRES` | 2 |

This supplies concrete audio/effect-intensity and car-editing candidates for the two percentage mappings. It does not by itself establish callback semantics for every codelink or map the dead-zone controls to this single-slider tail. In particular, type2 is not automatically a dead-zone label: these inspected installed declarations use it for car-editing controls.

The executable evidence now retains the 16-byte descriptor at `00558224`: keyword pointer to literal **`percenttype`** at `005386b4`, a default/value word, destination pointer **`00604f1c`**, and a type/dispatch word. `00604f1c - 00604ee0 = 3ch`, matching the renderer's field offset in the frontend entry template. This is an exact descriptor/offset link; parsing dispatch, write width, template instantiation and all default overrides still need direct code tracing before declaring the full asset-to-live-instance contract verified.

Reproduce the asset side with `python3 analysis/scripts/inventory_slider_percent_types.py --game-dir '<installed game directory>'`; the executable audit records descriptor bytes for both baselines. Installed/backup naming does not authenticate retail or official-package provenance. No slider was moved, setting changed or numeric output measured.

## Coordinated definition changes and duplicate backup boundary

The selected inventory now matches blocks by exact codelink between installed files and case-distinct uppercase backups, without treating their directory names as authenticated provenance:

| Codelink group | Uppercase local backup percenttype | Installed percenttype | Paired renderer implication |
|---|---:|---:|---|
| Five shared audio controls | 0 | 1 | Original tail skips type0; Modern type1 admits direct `v*100`. |
| `SFX_INTENSITY` | 0 | 1 | Same transition from no percentage tail to direct percentage mapping. |
| Seven shared `CE_*` car-editing controls | 1 | 2 | Original type1 and Modern type2 both select the bipolar `(v-0.5)*2*100` mapping, with different rounding sequences already documented. |

Installed `audio.mnu` additionally contains `ASLD_MENUSOUND`, absent from the selected uppercase `AUDIO.MNU`. Its separate volume consumer is traced in the [frontend sound comparison](original-modern-frontend-sound.md). This is a matching-codelink/data comparison, not proof that the two file sets were paired with the executables historically or selected at runtime.

For all three selected filenames, lowercase `fedata_org/menus/*.mnu` copies are **byte-identical** to installed `FEDATA/MENUS/*.mnu`; the inventory records this explicitly. They are not independent original evidence merely because they sit in a backup folder. Uppercase files have different hashes and preserve the older declaration pattern in this bounded set; retail/package provenance remains unverified.

This explains the cooperation between a changed binary type gate and changed menu declarations: applying only one side would not reproduce the observed mappings for these files. It strengthens the mechanism behind the volume/alpha percentage catalog claim while leaving complete parser binding, historical introduction, dead-zone behavior and actual formatted outputs pending. No setting or asset was changed.

## Separate two-axis percentage renderer: bounded counterexample

The same audit now captures complete `RenderFrontendSliderWithPercentagePair` at `0046b3a0..0046c2e6` and compares every body byte. It differs at **only `0046c1f0`**, changing the immediate in `SUB EDX,10` to `SUB EDX,20` on one caption-coordinate branch. This is a layout delta, not a rewrite of that body's percentage arithmetic.

Both bodies quantize entry floats +54h/+58h through `004693c0` with approximately0.01 step, multiply by100, store binary32 intermediates, add sign-selected approximately−0.005/+0.005, store again, and call `004dfd56` before FISTP. The constants at `0053aea8..0053aeb4` are byte-identical. Format `(%02d%c, %02d%c)` is also retained; existing argument-order research places the +58h percentage before +54h in the output. EAX returns0. The routine's type-2 widget dispatch is distinct from the single-slider's **percenttype2** field; identical numeric labels must not be conflated across these two selectors.

This path still depends on the changed `004dfd56` implementation documented above. Consequently unchanged caller instructions/constants do not prove identical exception handling or every numeric result. Conversely, the final original/Modern pair does not support describing the two-axis percentage body as having adopted the single-slider's direct-FISTP rewrite. No such local rewrite exists here.

Existing [controller property setup research](controller-axis-property-setup.md) connects axis widgets to cached percentage pairs and device-property setters. That supports further investigation of controller-related controls, not universal proof that the catalog's historical dead-zone rounding change is represented by this one-byte layout delta. Intermediate releases, complete type/resource binding and controlled ordinary/boundary comparisons remain required for that stronger claim.

**Closed:** two-axis body/constant comparison and distinction from the single-slider tail. **Still unresolved:** historical rounding attribution, active control-word/exception state, full widget binding and numeric output equivalence. No controller properties or settings were changed.

## Five-percent step claim: declared fallback versus selected step

The asset inventory now retains `snap` and `r0_step/r1_step/r2_step` values. The selected installed audio and effect-intensity blocks declare **`r0_step=0.050000`**, compared with **0.010000** in the matched uppercase backups. They also retain **`snap=0.010000`** in the inspected installed blocks. These are distinct fields and must not be collapsed into a single advertised step.

Executable descriptors connect literal `snap` to template destination `00604f24` (entry+44h), and `r0_step` to `00604f28` (entry+48h), at descriptor addresses `00558324` / `00558334`. The audit retains their raw words for both binaries. Complete parser write/instance creation still remains outside this bounded descriptor observation.

Complete `HandleSingleSliderStepInput`, `0046a860..0046a97c`, is **byte-identical** between executables. Its ordinary finite-input selection uses +44h whenever `0 < value <= 1`; otherwise it falls back to +48h. Event codes `4b00h` / `4d00h` subtract/add that selected value, with clamping and subsequent update/quantization described in existing analysis. Return status2 indicates a handled path, not proof of a changed value at a limit.

Consequently, **if** these declarations become the instance fields without intervening overrides, this retained handler selects **0.01**, not the declared fallback0.05. That is a conditional static implication, not a measured keypress, complete asset-to-runtime binding or universal refutation of every release's behavior. Other event paths, menu callbacks, parser/template interpretation and runtime writes must be checked before saying the installed slider actually moves by1% or5%.

Catalog **MP152-005** now records partial evidence: the0.05 declaration exists and changed in selected local files, but a competing0.01 primary field and retained preference rule prevent treating the full5% behavior as verified. This distinction is also why percentage display rounding and input step size remain separate claims. No input or setting was changed.

## Immediate step-event dispatcher does not override step values

The paired audit now captures complete `0046cb80..0046cbbc` and its six-target table at `0046cb64`; both are byte-identical. It receives the widget in EAX and an event in low WORD EBX, saves the event through ECX, reads widget WORD+42h as its type selector, then dispatches:

| Widget type | Action |
|---:|---|
| 0 | Sign-extend event WORD and call single-slider step handler `0046a860`. |
| 1 | Skip adjustment, return0. |
| 2 | Sign-extend event WORD and call pair-slider handler `0046c4a0`. |
| 3, 4, 5 | Call single-slider step handler. |
| Unsigned WORD >5 | Call single-slider step handler via default branch. |

This selector is `slidertype`/widget behavior state, distinct from the percentage-display byte+3ch. The code does not write widget+44h or+48h, replace the widget pointer, or add a Modern-only step override before `0046a860`. Its EAX result forwards the selected handler's status; preserving other dispatch registers does not imply preservation by every downstream callback.

For the installed audio blocks declaring `slidertype=0`, this supplies the immediate dispatch route **if** their parsed instance field+42h has that value. It does not close the complete menu-parser/template contract or prove an actual event reached the dispatcher. No resolved direct CALL appeared in the retained disassembly search; callback/table-based invocation remains to trace rather than assuming inactivity.

The 5% claim's remaining static gap is therefore upstream field instantiation/mutation and alternative event paths, not an uninspected override inside this immediate dispatcher. Runtime step behavior and historical attribution remain unverified. No game input was sent.

## File-backed slider callback row

The manifest now retains and asserts byte identity of the 80-byte prefix capture at **`00557718`** (the full template is established below). Its first DWORD is **0fh**, second DWORD **800h**, and the callback-shaped slots are:

| Row offset | Function pointer |
|---:|---|
| +24h | `0046cc50` |
| +28h | `0046cc10` |
| +2ch | `0046cae0` — known slider render/type dispatcher |
| +30h | `0046cb80` — step-event dispatcher inspected above |
| +34h | `0046cbe0` |

Remaining DWORDs in this captured prefix are zero; that prefix length did not establish the full template size. This is a concrete static callback-registration candidate, shared between original and Modern, rather than treating the lack of direct CALLs as evidence the dispatcher is unused. The +2ch/+30h positions correspond to the entry callback fields examined elsewhere in frontend rendering/input analysis, but the row-to-entry copy/installation code must still be traced before asserting that exact runtime relationship for every slider.

The row contains no new Modern-only step override: its bytes are identical and point to the same retained step dispatcher. This further localizes the5% ambiguity to instance construction/mutation, other input paths or historical releases. Pointer presence does not prove execution, valid widget lifetime or user input delivery. No callback was invoked during this audit.

Next: locate the table walker/template installer and establish how row ID0fh and the parsed slider record are combined. The documented conditional snap-field preference remains conditional until those links or live values establish the actual input state.

## Verified template-to-entry installation

Complete installer `00449060..004490d8` is now captured and byte-identical between original and Modern. Incoming EAX is the destination entry index; EDX is the requested type. It scans a sentinel-terminated registry at `00557a84` with **12-byte stride**, matching type DWORD0 and loading the template pointer at +8. A missing type returns without the copy.

The exact registry item at **`00557b44`** is `{0fh, 005383e4, 00557718}`; the middle pointer names literal **`slider`**. For this type, the installer therefore copies **bch (188) bytes** from `00557718` into `00604ee0 + wrap32(index * bch)`. The manifest now retains the complete source template and registry item and asserts both identical across baselines. There is no local destination-index capacity check.

This establishes installation of the template's +2ch render dispatcher and +30h step-event dispatcher into corresponding entry fields. The prior 80-byte callback capture was a **prefix**, not proof of row extent; the bch-byte copy determines the installed template extent used here. Copying raw pointers is not equivalent to invoking them, and does not validate the lifecycle of the destination entry.

The callback-registration gap is closed for a type0fh install through this helper. Remaining links for the5% question are the text parser's numeric stores/default overrides into the template/instance, later field mutation, and actual event delivery. The helper itself does not introduce a Modern-only snap/step override: its body and complete slider template are retained unchanged.

## Descriptor numeric writes reach instance fields

The audit now retains complete descriptor writer `00449240..004493aa` and float parser `004491b0..00449215` for both baselines. Their captured hashes describe each body independently; they are not asserted wholly identical merely because the relevant numeric branch is shared in the inspected code.

The writer takes an entry index in EBX and descriptor index in EDX. It forms the destination as:

`00604ee0 + wrap32(entryIndex * bch) + (descriptor.destination - 00604ee0)`.

Descriptor rows are16 bytes, indexed relative to the table fields at `00557c18/1c`: the numeric type and destination pointer respectively. Type6 dispatches through table `00449218` to **`00449383`**, calls `004491b0`, stores its ST0 result as binary32, then copies **four bytes** to the computed destination at `00449393..004493a2`.

Together with the retained `snap`/`r0_step` descriptors, this establishes direct entry-field destinations +44h/+48h on that descriptor route. It is not a store into a separate global template followed by an unexplained copy. The earlier template installer initializes entries; this writer addresses the selected instance using the same bch stride.

The float parser calls the runtime formatted scanner with the retained format at `00538f70`, then performs its own character checks and returns a binary32 value through ST0. Malformed-input/scan-failure behavior and every scanner contract remain outside this ordinary-decimal input review. The inspected menu spellings `0.010000` / `0.050000` match the expected decimal-value path; no parser instruction was executed.

**Closed:** numeric descriptor write width and instance-address calculation. **Still pending:** key-to-descriptor selection and overall file parse order, subsequent initialization/callback overrides, event delivery and actual step values. Thus the conditional1%-versus5% observation remains a bounded static result rather than a measured contradiction of the release claim.

## Resumed checkpoint: key-selection evidence retained

Final read-only inspection traced lookup `00448f00..00448f4d`: it scans 16-byte descriptors, compares the input keyword through `004ee310`, and accepts a matching descriptor when its applicability type equals the current entry type or is generic type1. The loader witness `004496a8..00449737` reads the current entry type, calls that lookup, then forwards the returned descriptor index, current entry index and value buffer to `00449240`.

The complete descriptor rows are `00558320 = {0fh,00538738,6,00604f24}` for `snap` and `00558330 = {0fh,00538740,6,00604f28}` for `r0_step`. Their fields are applicability type, keyword pointer, numeric conversion type and destination. Earlier keyword-first captures omit the preceding applicability DWORD and must not be read as complete row boundaries.

After resumption, the audit script retains both spans and complete descriptor rows for both hash-pinned baselines. Readback verifies the keyword/type checks, loader arguments and full row boundaries; the key lookup body and selected loader span are byte-identical across baselines. Two runs reproduce the expanded JSON unchanged. The loader span is a witness inside a larger routine, not a complete loader-body comparison. Later field overrides, lexical parsing edge cases, actual event delivery and runtime step size remain unresolved; the broader comparison is not complete.

## Single-slider initializer changes geometry and index signedness

The audit now retains complete paired **`0046ab10..0046abac`**, exclusive end, **156 bytes**. All differences lie in`0046ab1f..0046ab49`; the99-byte tail from`0046ab49` is identical. The envelope includes five Modern NOP bytes excluded from its saved body union, so it must not be confused with the151-byte saved-function size.

When widget byte+`0x3d` is nonzero, original obtains the signed WORD at+`0x40` via DWORD+`0x3e` shifted16; Modern zero-extends WORD+`0x40` directly. Both use it as a four-byte-stride table index. Original stores WORD+6 from table`00559c6c` plus148; Modern uses plus151. Original stores WORD+8 from table`00559c94` unchanged; Modern subtracts1 before that WORD store. For equal ordinary indices/table values, these are **+3 and−1 internal coordinate arguments**, with16-bit wrapping. Physical-pixel effects and the flag’s full meaning remain unverified.

For indices whose high bit is set, original negative indexing and Modern positive indexing differ; no local range guard is added here. This is a signedness/operand-width change, not proof that either arbitrary-input path is safe. When the byte flag is0, both skip the changed block.

The retained tail calls`0046a980`, passes DWORD+`0x48` through`00469530` and DWORD+`0x54` through`00469480`, saves WORD+`0x0a` to+`0xb2`, and performs renderer-state-gated geometry updates. Its calls/globals remain dependencies; identical tail bytes alone do not establish identical initialized values or outputs. No slider, key input or initializer was executed, and no historical alignment claim is promoted from these offsets.
