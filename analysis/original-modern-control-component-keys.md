# Original versus Modern: InteriorBx key-control callback

## Evidence and function boundary

[The static audit](scripts/audit_control_component_key_difference.py) pins both EXEs and retains the full paired instruction envelopes **`004651e0..004652ed`** (269 bytes each), constants, changed addresses and shared callback binding **`00557a34 → 004651e0`**. See the [manifest](evidence/audits/control-component-key-difference.json). Shared binding, control flow and unchanged continuation establish correspondence beyond equal addresses.

Neither captured original nor local-Modern saved function inventory contains an entry/body covering this callback. Their paths, hashes and executable identities are recorded separately; absence from those inventories does not make the code padding. The outer [uncovered interval](original-modern-outside-function-index.md) is `00464fca..004654c0`,1270 bytes. Independently comparing it confirms **all52 changed bytes** lie inside this callback; other interval bytes match. No new function was created in Ghidra.

## Admission and shared state

The entry calls identical29-byte gate `0044a660..0044a67d`, which returns0 when global `00559234` is nonzero and entry byte+5 mask08h is clear, otherwise1. The gate does not change ECX, so the callback's preceding XOR ECX,ECX reliably initializes its two local binary32 deltas to0. It returns0 early if the gate rejects or global `00678950` is zero.

Admitted processing compares **BX**, not the full EBX, with three raw tokens. Component cells `00678954` and `00678958` have binary32 consumers/producers; the [existing component-setter research](detailed-analysis-notes.md) establishes the raw setter at `004654c0`. The follow-up below establishes the InteriorBx widget/menu binding. Physical axes and the event dispatcher's interpretation of return codes remain unresolved.

## Changed steps, cancellation and return code

| Raw BX token | Original admitted path | Modern admitted path |
|---|---|---|
| `4b00h` | Component0 delta+2.0; raw return2 | Component0 delta+1.0; raw return2 |
| `4d00h` | Component0 delta−2.0; raw return2 | Component0 delta−1.0; raw return2 |
| `0020h` | Sign-dependent adjustment of the already-zero local delta; component1 delta0; raw return2 | Load and negate both current components into local deltas; raw return0 |

For `0020h`, neither of the earlier mutually exclusive token comparisons assigned a nonzero delta. Original compares component0 with zero and applies retained binary64 coefficient0.4 to that zero local value. For ordinary finite state this leaves the deltas zero, so the shared addition does not recenter the pair (apart from its existing component0 clamp). Modern explicitly forms `delta0=-component0` and `delta1=-component1`; common additions at `0046527f/00465284` then cancel finite components to zero, with signed-zero details dependent on floating-point state.

The return change is independent of the arithmetic. Original sets ECX2 at `00465241`; Modern replaces that instruction with the new load/negate/store sequence and never sets ECX2 on the `0020h` path. Shared `MOV EAX,ECX` at `004652e6` therefore returns0. Do not silently change it to2 in reconstruction on the assumption that a state-changing event must report the same status as the step tokens. Whether this is intentional or affects event propagation requires the dispatcher consumer and runtime evidence.

## Retained continuation and machine limits

All bytes in **`00465271..004652ed`** are identical. They add the local deltas to the component pair, store binary32 values, and limit component0's magnitude to10 using fresh x87 comparisons and signed bound stores. Component1 has no corresponding clamp in this continuation. The binary64 coefficient0.4 and binary32 magnitude limit10 are equal in both files; the changes are instructions/immediates, not edited coefficient data.

Finite cancellation is not an arbitrary-input reset guarantee: infinities, NaNs, unmasked exceptions, pending state and signed zeros need their machine contracts. This callback contains no local precision-control reset. Removing the original sign comparison also changes local x87 status behavior; equality of the remaining tail is not full machine-state equivalence. ECX/EBP are explicitly restored on normal returns, while EAX is the raw callback code; broader ABI/flags/state and callers remain separate.

The removed original status-reader candidate `0046524c` is now explained by this replacement of the `0020h` branch. The meaningful code-level finding is **smaller step deltas plus finite component cancellation and a changed return code**, not proof of rendered behavior, a tested bug fix, or a historical release attribution. No key event, game, instruction probe, C compilation/export or Ghidra modification was performed.

## InteriorBx registry, packaged menus and shared update consumer

The expanded audit now establishes the widget context rather than relying on the component names. In **both EXEs**, registry row `00557bec` contains type33 (`21h`), token pointer `00538454` to **`InteriorBx`**, and template pointer `00557a04`. Template offset30h is the already verified key callback `004651e0`; offset2ch is updater `00464fd0`. These exact pointer/ID/string bytes link the changed callback to the named widget without guessing a physical axis.

The pinned official archive supplies matching **`[InteriorBx]`** sections in `fedata/menus/interior.mnu` and `fedata/menus/credits1.mnu`. The manifest retains member hashes and authored section properties. This proves packaged menu binding, not that either page was loaded or rendered during this audit. Other installed/user assets and earlier releases remain separate baselines.

Identical update prefix **`0046501a..0046505f`**,69 bytes, loads signed state DWORDs `0055a43c/0055a440` with FILD, adds component floats `00678954/00678958`, calls `004dfd56` twice, then writes integers back with FISTP. Thus the component pair supplies increments to the viewer's per-update state. Modern token0020h cancels the finite component pair, removing those explicit increments; the two step-token deltas are half their original magnitude. Actual scheduling, angle units/axes, input dispatch, conversion/exception edge cases and resulting frames remain untested.

The updater prefix is identical **only at the caller level**. Its callee `004dfd56` differs: the [existing rounding-helper comparison](original-modern-slider-percentage.md) records original temporary high byte `1fh` with inherited exception masks versus Modern literal control word `0c3fh`, plus waiting/nonwaiting instruction differences. Both request truncation toward zero, but exception handling and intermediate status are not equivalent by inspection. The helper restores the incoming control word before the updater's FISTP. Therefore identical updater bytes do not establish identical whole-path machine behaviour, even with the same component inputs; this remains a dependency for reconstruction and exceptional-state comparisons.

This gives **MP140-016 partial static support**: the source bullet explicitly describes stopping the car-interior view with Space and finer arrow-key speed changes, and the named InteriorBx callback/menu/dataflow now supplies the corresponding mechanism. Actual token-to-device event delivery, return0 propagation, rendered stop/smoothness and introduction in v1.4.0 remain unverified. It does not establish a racing-controller or simulation change. No target code, asset renderer, key event or new instruction probe was run.
