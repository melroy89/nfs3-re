# Original versus Modern: colour-control mouse dispatch

## Scope

Static paired comparison of frontend colour handler **`0043ead0`**, original **232 bytes through `0043ebb8`**, Modern **181 bytes through `0043eb85`**. Reproduce with `python3 analysis/scripts/audit_colour_control_difference.py`; the [manifest](evidence/audits/original-modern-colour-control.json) retains both full bodies, shared prefix and five complete identical helpers. Exact executable identities follow the [baseline](original-modern-differences.md). No UI/audio/instruction execution or Ghidra edits.

The saved Modern name identifies an HSV colour control, not the HSV automobile marque mentioned in separate logo claims. **MP140-013** bundles colour dropdown sound consistency and padding; this chapter supports only the bounded sound-request/dispatch change.

## Retained state machine and shorter release actions

The shared prefix **`0043ead0..0043eb1c`** takes the control pointer in EAX and keeps it in ECX/EBX. WORD+8eh is the active region. When it is zero, hit tester `0043e8e0` supplies the hovered region into WORD+8ch. If hover is nonzero and input helper `0049c080` returns13, hover is copied into active. The numeric input code is retained literally here; no hardware mouse event was executed.

Once active, both implementations call `0043e7a0` while the input helper returns13. Otherwise they compare the current hit-test result with the signed active region, dispatch a matching release action and clear WORD+8eh. The release cases are:

| Active region | Action helper | Original preceding request | Modern |
|---:|---|---|---|
| 1 | `0043dd90` | `004181d0` with EAX=0, EDX=127 at `0043eb68` | Omitted; action at `0043eb60` |
| 2 | `0043dc90` | Same request at `0043eb7d` | Omitted; action at `0043eb69` |
| 5 | `0043ddd0` | Same request at `0043eb92` | Omitted; action at `0043eb72` |

The [frontend sound comparison](original-modern-frontend-sound.md) documents `004181d0` independently. Removing these direct requests does not prove silence: generic input feedback, called actions and other controls can still request sound.

Modern refactors the original unsigned comparison tree into three explicit equality tests and shares the final epilogue. It also replaces original DWORD read at control+8ch followed by arithmetic shift16 with **MOVSX from WORD+8eh**. In ordinary little-endian storage these select the same signed16-bit active value, but the read widths differ: the original also reads the neighbouring hover WORD. Layout, overlapping access and potential synchronization assumptions must remain explicit in reconstruction.

Hit tester `0043e8e0` saves/restores incoming EDX across every retained return path, so the post-call comparison against EDX uses the caller’s saved active value. A guessed decompiler prototype that treats EDX as an arbitrary scratch output would obscure that contract. The handler restores EBX/ECX/EDX/EBP but does not establish a uniform EAX return value on all paths; a normal success-return interface is not inferred.

## Identical helpers and evidence limits

The complete bodies of `0043e8e0` (hit region), `0043e7a0` (cursor-driven component updates), `0043dd90`, `0043dc90` and `0043ddd0` are byte-identical. Their saved names help navigation, while their equality establishes only local instructions. Globals, inputs and transitive helpers may differ. This chapter does not reconstruct all HSV mathematics or prove colour output equivalence.

The whole-function inventory’s101 changed bytes within the181-byte Modern range omits the old function’s additional51 bytes. The paired full bodies retained here are therefore the appropriate basis for explaining the removed sound setup and reorganized exits, rather than treating that inventory count as a complete semantic diff.

**MP140-013:** partial static support for removal of three bespoke release-action sound requests. Padding and consistency with every other control remain unverified; the hit tester itself has unchanged bytes. Next inspect its caller/registration and the authored colour-control layout before attributing a padding fix or an audible result. No executable bytes or saved database state were changed.
