# Original versus Modern: dropdown input shared sound tail

## Evidence boundary

Containing envelope **`00463ff0..0046455d`**, with saved Modern function ranges split by gaps. This span is retained for context, not presented as one contiguous instruction-only function. Reproduce with `python3 analysis/scripts/audit_dropdown_input_difference.py`; the [manifest](evidence/audits/original-modern-dropdown-input.json) binds both baselines and focused route/tail witnesses. See the [main comparison](original-modern-differences.md). Static only; no input/audio, executable changes or Ghidra writes.

## Selection routes gain a shared sound request

On the inspected closed-list route (WORD widget+`0x40` zero), left code`0x4b00` and right code`0x4d00` enter selection-update branches. Original completes their bound-selector stores and returns EDI directly at **`004640ed`** or **`00464163`**. Modern replaces those returns with jumps to **`004642db`**. That shared tail sets **EAX1**, calls **`004181d0`** at **`004642e0`**, then returns EDI through the shared epilogue. Right selection sets EDI2 in the retained local path; left selection likewise has its own preceding result setup. Full list-validity and skip rules remain separate work.

This adds a sound1 request on those inspected selection routes, rather than relying only on opening/closing requests elsewhere. Existing [frontend-sound analysis](original-modern-frontend-sound.md) describes the new helper’s own gates and interface; the tail supplies no old EDX127 multiplier. The helper restores EDI, so the sound request does not replace the selected action result in this local return flow.

## Close/update branches are consolidated

Original **`00464294..004642f3`** contains two sound1 sites with EDX127, separate result2 assignments and repeated calls to layout/update helper **`00464560`**. Modern’s first branch stores the selected value and jumps to shared **`004642c9`**. That tail clears widget WORD+`0x40`, invokes `00464560`, sets EDI2, and falls into the single sound1 tail.

Ordering therefore changes on these routes: Modern issues the common update before its common sound request, while original has sound calls before parts of the update/close work. The layout helper’s behavior is not established equivalent merely because its call address is retained; the [track-list alias analysis](original-modern-car-alias.md) already identifies related changes in that helper’s policy. Full callback/reentry effects and actual audible ordering require separate validation.

Modern also retargets some earlier branches to the new shared return locations, avoiding returns embedded in old instruction regions. The retained envelope permits reviewing those control-flow changes without interpreting NOP gaps as additional functionality. No assertion is made that every changed byte in this larger handler is explained by these sound-tail findings.

This supplies partial static support for consistent top-dropdown keyboard feedback. Remaining work includes full action/skip semantics, all other routes, caller result handling, callback effects and audible behavior. It is not proof that every keypress changes selection or emits exactly one sound.

## Enter opening route and retained cursor arithmetic

Closed-list Enter (`SI=0x0d`) enters **`0046417b`**. Paired bytes **`0046417b..00464209`** are identical: set WORD widget+`0x40` to1, copy the bound selected value into local widget fields, calculate the visible interval, call layout helper `00464560`, form cursor coordinates and call **`0049bfc0`** at `00464204`. The position arithmetic uses signed high-WORD components, truncation-corrected halving and a16-unit row step with8-unit offset. No new cursor offset is identified in this route.

Original then returns EDI at `00464209`. Modern replaces that epilogue with a jump to **`004642db`**, so opening now also requests sound1 before returning the retained EDI2. The Modern NOP region that follows is not a hidden handler. The layout-helper call is locally unchanged, but that helper’s separate alias/layout changes can still affect its outputs.

The audit now enumerates every differing byte in the complete containing envelope and checks that all fall within nine recorded region envelopes: earlier branch-target adjustments, the three replaced selection/opening epilogues, the consolidated close/sound tail, and the expanded-list navigation epilogue. This is byte-difference coverage, not proof of complete behavioral equivalence outside the changed bytes: helper behavior, globals and caller inputs can differ. The exact changed addresses remain in the manifest for future reconstruction review.

Together the left/right selection and Enter-opening routes give additional support for the top-dropdown keyboard-sound claim. Up/down/page selection in the expanded list, callback policy and exact audible effects remain separate. No input route was executed.

Expanded-list positioning ends with retained cursor call **`0046454e`**. Original’s tail at **`00464553`** returns EDI directly; Modern loads EAX0 and jumps to **`004642e0`**, reusing the same sound call while retaining sound identifier0 rather than the sound1 supplied by the other entry. EAX is then replaced by EDI in the common return sequence. This extra epilogue change is included in the ninth region; complete path admission and whether every movement changes the selected item remain unresolved.
