# Original versus Modern: localized stepped numeric scale

## Correspondence and evidence

**Verified static comparison; no UI or instruction execution.** Modern `00489ab0..00489bd9` corresponds to original `00489b30..00489c40`, not original `00489ab0`. The latter is a different formatting wrapper with `RET 18h`; the matched numeric-scale functions both consume seven stack DWORDs and return with `RET 1ch`. Shared localized IDs `15ah/15bh`, indexed numeric labels, color selections and three redirected callers establish correspondence.

Run `python3 analysis/scripts/audit_numeric_scale_difference.py` (pefile, GNU objdump). The [manifest](evidence/audits/original-modern-numeric-scale.json) retains baseline SHA-256 identities, complete paired function spans, helper witnesses and assertions that calls at `0045ae27`, `0045af5e`, `00483a62` target original `00489b30` versus Modern `00489ab0`. Ends are exclusive. Existing contracts are in [detailed notes](detailed-analysis-notes.md#localized-stepped-numeric-scale).

## Layout changes

Both functions receive count in EAX, selection indices in EDX/EBX, and seven stack DWORDs: scale, three colors, left/right endpoints and vertical anchor. The selected indices are adjusted by minus one for the interior label comparisons. This is a register/stack contract, not a standard compiler-inferred prototype.

| Operation | Original | Modern |
|---|---|---|
| Spacing | `(right - left) / (count + 2)`, rounded to binary32 local | Measures combined labels first; `(right - left - measuredAdvance) / (count + 1)`, rounded to binary32 local |
| Labels measured together | No such combined-measurement pass | Concatenates localized IDs `15ah`, `15bh` and decimal integers 1..count; passes combined string to `004d1430` |
| Small spacing | No local scale fallback loop | Converts binary32 spacing with FISTP; if signed result <2 and current scale differs from `00791b4c`, substitutes that scale and repeats measurement |
| Position advance | Adds spacing; discards each draw's returned advance | Adds each draw's returned advance plus spacing |
| Final endpoint | Drawn through ordinary `004d1000` at the incremented position | Uses separate `004d10e0` with the supplied right endpoint; existing text research identifies right anchoring |
| Integer label formatting | Local `sprintf`-style call using constant format | `004f93a8` signed decimal formatter, retained register contract and no capacity parameter |
| Text color | Direct writes to `00561b34` | Calls `004d1450`, whose implementation stores the same global |

The Modern formatting loop increments before its count comparison, so even zero/negative counts enter its premeasurement integer loop at least once. The main draw loop also uses signed comparisons. Neither routine supplies comprehensive local input validation. The table describes ordinary intended count ranges; it is not a guarantee for arbitrary signed values.

Modern retry sets the scale argument slot itself, then stops retrying once it equals fallback `00791b4c`, even if rounded spacing remains below 2. It does not keep shrinking indefinitely. Its placement update stores the accumulated float with FST, then converts the still-live x87 value with FISTP into the left-position argument slot. A replacement using only rounded float locals or truncating casts could change coordinates. Both current-rounding behavior and the original/Modern control-word differences matter; integer-coordinate equality has not been tested.

## Buffer, state and ABI boundaries

Modern concatenates with `004f93b8`, an unbounded NUL-terminated byte copy that leaves destination at the terminator for the next append. Its scratch begins at EBP-34h within a 34h-byte local frame; other locals and a separate decimal buffer share that frame. There is no capacity parameter or aggregate-length guard. Actual localized strings and admissible counts must be established before claiming the concatenation is safe. No overflow input was executed and no reachable defect is asserted.

Modern PUSHAD/POPAD restores all general registers, including EAX; original saves ECX/ESI/EDI/EBP but does not establish the same full preservation. Both modify rendering text state through scale/color setup. Modern also overwrites the caller-provided stack slots for scale and left position before popping the seven arguments; this matters to an exact assembly contract even though ordinary caller cleanup discards them. Neither routine restores the previous global text scale/color locally.

**Verified:** moved counterpart, three caller retargetings, formulas, text-helper changes, fallback branch and machine-rounding operations. **Inferred:** a layout change intended to account for label widths. **Unresolved:** exact screen/option identity for every caller, localized assets and length admission, helper return/anchoring contracts beyond existing research, invalid counts, rendered appearance and release introduction. No catalog claim is promoted solely from a similar UI description.

Next: inspect the three caller argument producers and packaged localized labels; compare render output only in a later authorized runtime phase. Executables, raw reference exports, reconstruction sources and Ghidra are unchanged.

## Caller follow-up: retained HUD inputs

The manifest now retains paired setup regions `0045adba..0045ae2c`, `0045aef0..0045af63` and `004839eb..00483a67` and asserts that **every differing byte is inside the corresponding CALL displacement**. This is stronger than the earlier target-only check: argument instructions in these inspected regions remain identical. It is not a whole-caller equality claim; incoming registers, earlier branches and producers can still differ outside the captured spans.

The first two calls belong to existing `RenderHudElementForView` research (`0045ab30`); the third belongs to `RenderRaceHUD` (`00482b00`). Thus this scale is used in HUD rendering, rather than established as a frontend options widget. Direct input observations are:

- EAX count comes from DWORD `[[vehicle + 0x528] + 8] - 2` in all three regions. Existing AI gear/controller research identifies profile `+8` as a gear count, but this does not prove every admissible profile count or array extent.
- EDX selection is zero-extended byte `[vehicle + 0x50b]`. Existing drive-state/gear research links this to the current selected drive state. Exact enumeration and exceptional values remain separate from that association.
- First and second inspected calls explicitly clear EBX, disabling the secondary selected-index match on the ordinary positive interior loop. The third region does not establish its incoming EBX, so it is not assigned the same value by analogy.
- All three push scale DWORD `00791b54`. Caller branches supply either fixed color values `ff707070` / `ffa0a0a0` and zero, or colors carried in registers; endpoints and vertical anchors come from per-view geometry and, on some branches, x87-to-integer coordinate conversion.

This supports a **gear/drive-state HUD scale** interpretation while preserving the raw field contracts. It does not authenticate localized endpoint text: IDs `15ah/15bh` still require actual language-table payload inspection. No rendered label or endpoint was observed in this phase.

The changed routine can therefore alter label spacing for the same retained argument-building instructions. Whether a particular race invokes one branch with the same arguments in both versions still depends on upstream state, assets, initialization and floating-point behavior. Those conditions are not supplied by a static CALL retargeting alone.
