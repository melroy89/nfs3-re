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
