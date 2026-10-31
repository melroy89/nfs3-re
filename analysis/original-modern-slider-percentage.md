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
