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

The follow-ups below inspect three caller setup regions, installed labels and profile counts. Next: complete upstream branch/state admission and compare render output in a later authorized runtime phase. Executables, raw reference exports, reconstruction sources and Ghidra are unchanged.

## Caller follow-up: retained HUD inputs

The manifest now retains paired setup regions `0045adba..0045ae2c`, `0045aef0..0045af63` and `004839eb..00483a67` and asserts that **every differing byte is inside the corresponding CALL displacement**. This is stronger than the earlier target-only check: argument instructions in these inspected regions remain identical. It is not a whole-caller equality claim; incoming registers, earlier branches and producers can still differ outside the captured spans.

The first two calls belong to existing `RenderHudElementForView` research (`0045ab30`); the third belongs to `RenderRaceHUD` (`00482b00`). Thus this scale is used in HUD rendering, rather than established as a frontend options widget. Direct input observations are:

- EAX count comes from DWORD `[[vehicle + 0x528] + 8] - 2` in all three regions. Existing AI gear/controller research identifies profile `+8` as a gear count, but this does not prove every admissible profile count or array extent.
- EDX selection is zero-extended byte `[vehicle + 0x50b]`. Existing drive-state/gear research links this to the current selected drive state. Exact enumeration and exceptional values remain separate from that association.
- First and second inspected calls explicitly clear EBX, disabling the secondary selected-index match on the ordinary positive interior loop. The third region does not establish its incoming EBX, so it is not assigned the same value by analogy.
- All three push scale DWORD `00791b54`. Caller branches supply either fixed color values `ff707070` / `ffa0a0a0` and zero, or colors carried in registers; endpoints and vertical anchors come from per-view geometry and, on some branches, x87-to-integer coordinate conversion.

This supports a **gear/drive-state HUD scale** interpretation while preserving the raw field contracts. It does not authenticate localized endpoint text: the installed language-table payload follow-up below now records IDs `15ah/15bh`, with provenance and runtime-selection limits. No rendered label or endpoint was observed in this phase.

The changed routine can therefore alter label spacing for the same retained argument-building instructions. Whether a particular race invokes one branch with the same arguments in both versions still depends on upstream state, assets, initialization and floating-point behavior. Those conditions are not supplied by a static CALL retargeting alone.

## Installed label inventory and bounded scratch overlap

The [installed label inventory](evidence/inventories/installed-numeric-scale-labels.json) hash-identifies all 18 selected language files: six under `FEDATA/TEXT` and twelve case-distinct files under `fedata_org/text`. Each ID offset is within its file and reaches a NUL before EOF. These are installed/local backup artifacts, **not authenticated original retail files or independently attributed official-patch assets**; the backup directory name does not establish provenance. No file was selected through a running game.

| Languages / IDs | `15ah` | `15bh` | Payload bytes each |
|---|---|---|---:|
| English, French, German, Spanish, Swedish | N | R | 1 |
| Italian | F | R | 1 |

The English neutral/reverse interpretation agrees with the gear/drive-state caller evidence. The table records actual bytes, without imposing that English expansion on Italian's `F`. The case-distinct backup files have differing full-file sizes/contents while retaining these labels; do not collapse them into one authenticated baseline.

For these one-byte endpoint labels and an ordinary positive count `n`, the concatenated measurement text requires **`3 + sum(decimal_digit_count(i), i=1..n)` bytes including the final NUL**. There are no added separators. This requires 12 bytes at count 9, 14 at 10, 16 at 11 and 18 at 12.

Modern's destination begins at EBP-34h. Stored pointer local EBP-24h (the second endpoint pointer used later) begins **16 bytes** after that destination. Consequently counts 1..11 with these inspected labels fit before that neighboring local, whereas count 12 would overwrite its first two bytes through the unbounded append loop. This is a conditional storage-overlap calculation, **not a demonstrated reachable defect**: count comes from profile count minus two, and no installed profile admission of count 12 has been established here. It also does not prove the rest of the function safe for every count 1..11, arbitrary assets or external state.

Reproduce with `python3 analysis/scripts/inventory_numeric_scale_labels.py --game-dir '<installed game directory>'`. The script reads only the two named folders, records selected string offsets/lengths and full-file hashes, and performs no game/probe execution. The profile-count follow-up below now bounds this installed data set; actual language selection and visual validation remain pending.

## Installed profile follow-up: conditional count-12 case is outside this inventory

The label inventory script now reuses `inventory_car_physics.py` to reread all installed `GAMEDATA/CARMODEL/*.viv` resources recursively and requires the recomputed result to equal the retained [47-profile inventory](evidence/inventories/controller-profile-inventory.json). It records that inventory's SHA-256 and derived counts in its own evidence. This validates the current assets rather than relying only on an older summary. The source scope excludes `gamedata_org`; installed files are not assumed to be pristine retail or official-patch assets.

| Profile gear count | Manual profiles | Automatic profiles | Derived HUD count (minus 2) | Concatenated bytes, inspected labels |
|---:|---:|---:|---:|---:|
| 5 | 0 | 1 | 3 | 6 |
| 6 | 8 | 19 | 4 | 7 |
| 7 | 22 | 16 | 5 | 8 |
| 8 | 17 | 11 | 6 | 9 |

Counts come from CARP fields 3 and 75, respectively, as parsed by the existing inventory. Their use as the active profile count follows the existing gear/profile research; the caller itself directly establishes only the read from profile DWORD+8. No runtime loading or mode-selection proof is added by this resource inventory.

Under the bounded combination of these profile counts, the inspected one-byte language endpoints, normal decimal formatting and unchanged profile data, maximum measurement concatenation is **9 bytes including NUL**. Therefore this data set does not supply the earlier count-12 local-overlap case. This closes the installed-data question for these two named inventories, not arbitrary modified assets, dynamically changed profile counts, different localized strings, denominator failures elsewhere or the complete function's safety.

**Next evidence:** remaining caller register/branch inputs, active profile/language selection and visible layout comparison. The conditional assembly overlap remains documented for larger inputs; it is not promoted to an observed defect.

## Right-anchor helper changes its x87 return contract

The audit now retains complete paired **`004d10e0`** bodies: original through exclusive`004d1116` (**54 bytes**), Modern through exclusive`004d1114` (**52 bytes**). Their prefix through exclusive`004d110f` is byte-identical. It calls`004d1480` for the string’s adjusted extent, subtracts that extent from the signed incoming EDX anchor through x87, calls`004dfd56`, FISTP-stores the resulting starting coordinate, and calls`004d1000` with that coordinate in EDX. The right-anchor relationship is therefore supported by direct instructions, not merely the function’s inferred name.

After the draw call, **original executes`FSTP ST(0)` at`004d110f`**, discarding the returned advance. **Modern omits that instruction** and returns with the draw result still in x87. The Modern numeric-scale caller pairs it with an explicit **`FSTP ST(0)` at`00489bd1`** after its call at`00489bcc`. The audit pins both disposal sites and both RET boundaries. This establishes a caller/callee x87 stack-effect change; it does not prove all other callers satisfy the Modern contract.

The helper saves/restores ECX and EBP but does not establish a standard C calling convention from that fact alone. Its incoming EAX string pointer, EDX anchor and EBX vertical input, plus x87 result ownership, must be reflected in the chosen reconstruction interface. Omitting the caller pop or retaining the original callee pop while also adding the Modern caller pop would change x87 stack state.

Byte-identical anchoring arithmetic is not equivalent output evidence: the [measurement dependency](original-modern-car-alias.md#width-dependency-removes-an-intermediate-integer-conversion) changed, and the shared-address rounding helper has distinct control-word/wait sequences. For ordinary finite in-range values both temporary rounding settings select toward-zero, but full floating-point state/exception equivalence remains unresolved. Actual endpoint placement still requires initialized metrics, scale and input comparison. This pass executed no rendering or instruction probes.
