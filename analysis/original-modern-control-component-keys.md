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

## Adjacent template data: separate Compass change

The audit compares the 64-byte InteriorBx template prefix at `00557a04..00557a44`: **all bytes match**, including its callback pointers. The next 64-byte prefix belongs to **Compass**, independently bound by registry row `00557bf8` (type34, token `00538460`, template `00557a44`). Its DWORD at template offset04h, address **`00557a48`**, changes from0 to`0200h`; the other63 bytes match (only byte `00557a49` differs).

This is a separate initialized-data change, not an InteriorBx key-handler option. The manifest retains both 64-byte prefixes and the Compass registry witness. The meaning of bit9, its consumers and any visible effect remain unresolved; determining them is a static dataflow follow-up before attributing a Compass feature or using this field in reconstruction. No claim of runtime activation or historical introduction follows from the bit alone.

The next inspection bounds the code side of this flag change: five Compass callback bodies are byte-identical across the pinned EXEs—`00457460..004575a0` (320 bytes), `004575a0..00457616` (118), `00457620..0045762a` (10), `00457630..0045766d` (61), and `00457670..00457675` (5), with exclusive ends. The manifest retains all **514 bytes** and per-body hashes. This excludes a local rewrite of those five bodies as the explanation for the changed template value; it does not establish unchanged callees, dispatcher behaviour or initializer `00457680`.

The retained key callback `004575a0` checks raw BX tokens `4b00h`, `4d00h`, `0020h` and `000dh`. On the admitted first three paths it sets raw return code2; the `000dh` path instead selects calls through `00457270/00457340` or `004572d0`, potentially passing two zero DWORDs to InteriorBx component setter `004654c0`. This supplies a static cross-widget connection, but neither the physical key mapping nor the external consumers of return2 are established. The five inspected bodies contain no explicit test of template mask`0200h`; the next useful trace is template copying and generic event selection, rather than assuming the Compass callback implements the bit itself.

## Runtime template copying: verified field destination

Identical complete helper **`00449060..004490d8`** (120 bytes, exclusive end) searches the registry at `00557a84` in 12-byte rows, comparing input EDX with each row’s type DWORD. For a match it loads the source pointer from row+8 and copies **`0xbch` (188) bytes** to `00604ee0 + 188*incoming_EAX`. It preserves EBX/ECX/ESI/EDI/EBP; the successful path leaves EAX as the copy count188, while no-match EAX is search arithmetic rather than a normalized status. The manifest retains the paired body. Admission, valid indices, clear direction flag and accessible buffers remain caller requirements.

For type34, the previously verified Compass registry row supplies source `00557a44`. Thus its changed DWORD at source+4 enters runtime entry+4 through this copy path; bit9 lies in runtime byte+5 mask02h. This establishes initialization dataflow, not the flag’s interpretation or persistence after parsing. It also corrects the earlier boundary terminology: adjacent templates begin64 bytes apart, but this helper reads188 bytes. The retained64-byte comparisons describe prefixes, **not verified complete template object sizes**. The additional copied bytes overlap subsequent file-backed records; their intended schema, later overwrites and final active-entry values require further inspection. No out-of-bounds runtime fault or original bug is inferred merely from that layout.

The generic flag consumer is still unresolved. The precise next trace is writes and reads of runtime entry+4/+5 after `00449060`, including parsed field overrides and event selection. The callback-body equality and this copy path alone do not explain the visible effect of Compass bit9.

## Full copied regions overlap the changed source byte

Comparing the actual188-byte source windows, rather than only their64-byte prefixes, reveals **one changed byte in each window**, the same file-backed byte `00557a49` (`00h → 02h`). In the InteriorBx source window `00557a04..00557ac0` it is offset**45h**; in the Compass window `00557a44..00557b00` it is offset**05h**. The audit pins both complete source windows and asserts that these are their only differences.

Consequently the initialization copy can place the change into **two runtime locations**: InteriorBx entry+45h and Compass entry+05h. The earlier type-specific description identifies ownership of the compact source prefix, but does **not** establish that only Compass runtime data changes. Interpreting InteriorBx+44h/+45h, subsequent parser writes and either destination’s consumers remains necessary before assigning a behavioural effect. This is a concrete reconstruction layout dependency: a replacement initializer must reproduce the observed188-byte copy, or explicitly validate a cleaner per-type initialization scheme, rather than silently copying only64 bytes. No claim is made that either changed destination survives to active dispatch or produces a visible difference.

### Initializer does not locally resolve the overlapping field

InteriorBx template+24h points to initializer **`00465370..004654b4`**,324 bytes. The complete initializer matches in both EXEs and is now retained in the audit. After its prologue, `0046537e` replaces incoming EAX with global `00664798`; it does not keep the incoming entry pointer in a working register for a direct entry+45h store. Its visible writes initialize viewer globals including `00678940`, `0055a438/3c/40` and `00678954/58`, with helper calls for paths/assets and setup.

This rules out a newly rewritten initializer body as the explanation for the overlapping source-byte difference. It **does not prove the field survives initialization**: helpers, global aliases, generic parser writes and the caller’s setup ordering remain unqualified. No default value is inferred merely from ECX or EBX across those helper calls. The remaining static target is therefore the generic loader/parser’s entry+44h/+45h writes and consumers, rather than treating the visible initializer as a proven reset.
