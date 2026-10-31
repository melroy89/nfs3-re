# Original versus Modern: dialog input dispatch

## Evidence boundary

Complete paired **`00445e60..00445efa`**,154 bytes. Reproduce with `python3 analysis/scripts/audit_dialog_input_difference.py`; the [manifest](evidence/audits/original-modern-dialog-input.json) retains baseline hashes, both bodies, dispatch tables and Modern Shift-query helper. See the [main comparison](original-modern-differences.md). Static only; no game/input/audio or Ghidra writes.

## Tab normalization and direct handler table

Both derive a dispatch ordinal from **`00558b14-1`**, accepting unsigned0..3. Original table **`00445e48`** points to four local wrappers, each sign-extending DX and calling a handler: `00444910`, `00444b20`, `00444f50`, `00445520`. Modern changes the table entries to those handler addresses directly and invokes them with an indirect CALL, replacing the original indirect JMP to wrappers.

Before dispatch, Modern treats low WORD input **9** as Tab: it sets DX=`0x4d00`, calls **`004f1fcc`**, and changes DX to`0x4b00` when the helper leaves ZF clear. It then sign-extends DX into EAX for the handler. Non-Tab inputs retain the existing sign-extension route.

The complete Modern helper **`004f1fcc..004f1ff0`** queries **`GetAsyncKeyState(0x10)`** through the actual import at **`00534738`**. It tests the returned signed WORD, normalizes a negative result to EAX1, and ends with TEST EAX,EAX before restoring EDX/ECX. Thus the caller’s branch consumes a real flag output: Shift held selects left code`0x4b00`, otherwise right code`0x4d00`. EDX preservation keeps the prepared DX value alive. A conventional C declaration omitting the flag result would obscure this interface.

## Handler result3 requests sound while preserving the result

Modern compares the selected handler’s EAX with3. On equality, it pushes that result, calls **`004181d0`** with EAX still3, and pops EAX afterward. Other results bypass the request. This adds a local sound request without converting the handler result into the sound helper’s return. Original has no corresponding request in this central dispatch block. Existing [frontend-sound analysis](original-modern-frontend-sound.md) establishes the changed sound-helper interface and its own gates; a call does not prove audible output.

Paired prefix **`00445e60..00445e9a`** and complete tail **`00445ec7..00445efa`** are byte-identical. The retained tail calls optional callback `00558b18` for nonzero handler results, passing a local byte pointer in EDX; that byte controls the later close-helper call. Callback result2 is normalized to0 for the outer return. The initial scene/global admission checks also remain in the equal prefix.

Handler result3’s action identity, full per-dialog navigation behavior, callback preservation and audible consistency remain unresolved. The finding gives partial support for the mini-dialog keyboard-sound claim, but is not complete validation of every dialog or every navigation action. No keyboard layout, held-key timing or UI state was tested.

## First handler: Escape versus navigation feedback

The expanded audit retains complete paired first handler **`00444910..004449c6`**. Exactly four byte positions differ, all within the two relative CALL operands at **`0044496b`** and **`0044498d`**. Original calls dialog cursor-position helper **`00444570`**; Modern calls wrapper **`0043eb88`**. Existing [cursor-position analysis](original-modern-cursor-position.md) verifies that wrapper requests sound0 only when cursor positioning reports a valid item. No other local instruction changes occur in this handler.

Both handlers map low-WORD **`0x1b` (Escape)** to EDX3 and return it in EAX, whereas **`0x0d` (Enter)** returns1. Left/up codes `0x4b00`/`0x4800` decrement the selected index with wrap; right/down `0x4d00`/`0x5000` increment it with wrap. The cursor-call wrapper preserves EDX, so the navigation route keeps its initial result0. Unrecognized inputs also return that initial0. Count/index validity remains a separate invariant; this is not proof of safe empty-dialog navigation.

Thus the new central result3 sound is concretely an Escape/cancel-associated request for this first handler. Navigation can instead request sound0 through the newly retargeted cursor wrapper, then returns0 and bypasses the central callback/close route. Enter’s result1 follows the retained callback handling without this central sound3 request. The conclusion is scoped to the inspected first handler; the other three handler contracts and all dialog callback meanings remain separate work.

This connects the added sound request to an actual input value and separates it from navigation feedback. Audible volume, throttling and device behavior still depend on the changed sound helper and runtime state. No dialog key was pressed during this audit.

## Remaining handler coverage

The audit now retains complete paired timed **`00444b20..00444b60`**, edit **`00444f50..004450bd`** and toggle-menu **`00445520..0044567b`** handlers. The timed body is byte-identical; edit/toggle differences are confined to the cursor CALL operands listed below.

| Call address | Original target | Modern target |
|---|---|---|
| `00444fd5`, `00444ffb` | `00444570` dialog position | `0043eb88` dialog position/sound wrapper |
| `004455a1`, `004455fd` | `00445160` menu position | `0043eba0` menu position/sound wrapper |
| `004455cb`, `00445627` | `00444570` dialog position | `0043eb88` dialog position/sound wrapper |

Timed input first tests byte **`00558b4c`**: when zero it returns0; when nonzero Escape returns3, Enter1 and Space2. Edit input maps Escape to ESI3 at `00444fa6`; toggle input maps it to EDX3 at `0044566d`, and their epilogues return that value in EAX. Together with the first handler, this establishes an Escape-associated result3 route for all four dispatch targets, subject to their own gates. The added central sound3 request is therefore not limited to one handler.

The paired local changes and previously verified wrapper contracts support a partial mini-dialog keyboard-sound mechanism: cursor feedback through position-validity wrappers, plus central Escape feedback. This does not prove all actions emit one sound, that callbacks do not add requests, or that audible timing/volume is consistent. The timed handler’s enable state, full edit mutation rules, toggle semantics and runtime audio remain beyond this focused comparison.

## Localized notice wrapper: moved counterpart and constructor inputs

The [notice audit](evidence/audits/localized-notice-difference.json), reproduced by `python3 analysis/scripts/audit_localized_notice_difference.py`, pairs original **`00444be0..00444c0d`** with Modern **`0043fda0..0043fdcc`** through caller **`0043fe09`**. The paired caller prefix`0043fdd0..0043fe0e` changes only its CALL displacement. Original code at the Modern entry address is an unrelated preceding routine’s tail; the saved same-address difference is not a semantic function pair.

Original resolves the incoming localized ID through`004d1850`, stores one pointer at`00661090`, then calls`00444a80` with EAX1, EDX pointing at that array, EBX`226h`, ECX1 and one zero stack argument. Modern resolves the incoming ID plus fixed ID11, stores two pointers at`00661090/+4`, and calls the same constructor with EAX2, EBX/ECX0 and a zero stack argument. Its EDX points to the shared array through the preserved setup; full localization-helper preservation remains an interface dependency.

Complete constructor **`00444a80..00444b1d` (157 bytes)** is byte-identical. It stores EAX as line count`00558b1c`, EDX as pointer-array address`00558b20`, timestamp`0079c1a4` into`00558b44`, and the absolute value of EBX into`00558b48`. Zero EBX sets byte`00558b4c` to1; positive EBX copies CL there. The wrapper therefore changes line count and configured timer/state inputs without rewriting this constructor. Visible wording, elapsed-time behaviour and dismissal still require their own localization/event-loop evidence.

Modern’s PUSHAD/POPAD preserves incoming general registers, including EAX, while original restores its narrower saved set and leaves a constructor-derived EAX. Neither saves flags or x87 state. Both use shared pointer storage, so a maintained C interface must preserve its lifetime/overlap requirements rather than assume stack-local text arrays. Reentrancy and all notice callers remain unresolved. No dialog or instruction probes were run.

## Initial edit state stops requesting first-character replacement

The complete dialog initializer `00444c20..00444f48` (808 bytes, exclusive end) differs only inside `00444c90..00444ca6`. Original sets byte `00558b10` to 1, sets DWORD `00558b2c` to 1, then loads the same stack-supplied selection into EAX. Modern still sets the byte to 1, but zeros `00558b2c` before loading that selection. The common store to `00558b3c` at `00444ca6` and the rest of the initializer remain byte-identical. It is the DWORD's value, not a newly different initial selected index, that changes here.

[The expanded dialog audit](scripts/audit_choice_dialog_followup.py) verifies pinned executable identities, this complete initializer, renderer and full edit-handler witness; [its manifest](evidence/audits/choice-dialog-followup.json) records hashes and exact float arguments. The insertion tail `0044504f..004450bd` is byte-identical. The full handler also contains the separately investigated cursor-call retargeting earlier in this chapter; it is **not** entirely byte-identical.

That retained insertion tail supplies a concrete consumer of the changed DWORD. At `0044505d`, nonzero `00558b2c` can allow the path even when the current length has reached its limit. After character-admission helper `00443810` accepts the input, nonzero flag at `00445079` triggers:

- Clear the flag.
- Clear the 256-byte buffer at `00558b58` through `004e0640`.
- Set current length `00558b50` to zero.
- Continue to the ordinary append/increment sequence.

With flag zero, the clear/reset block is skipped and the retained append sequence uses the current length. For an otherwise valid prefilled edit dialog, original's initial flag therefore requests replacement on the first accepted character; Modern's zero requests normal append behavior instead. This is conditional on reaching this edit path, character acceptance and buffer/length state. Other keys have their own branches, and all dialog-type admission/initial-buffer producers are not proven by this local chain.

## Four renderer float arguments receive small adjustments

The complete renderer `00444000..00444350` (848 bytes) differs only in four PUSH-immediate arguments:

| PUSH address | Original binary32 bits / value | Modern binary32 bits / value |
|---|---|---|
| `004440d8`, `0044410d` | `3f0d0000` / 0.55078125 | `3f0d4ccd` / 0.551953136920929 |
| `00444220`, `00444255` | `3ef80000` / 0.484375 | `3ef8999a` / 0.48554688692092896 |

Both pairs increase by approximately 0.001171887. The respective sequences still reach draw helper `004db000` at `0044412e` and `00444275`; the surrounding pushes, x87 arithmetic, calls and branches are byte-identical. The audit establishes exact changed argument bits, not the final visible texture sample or a texel-alignment fix. Assigning texture-coordinate/depth semantics requires the draw helper's complete argument mapping and resource evidence; a nearby rendering call alone is insufficient.

**Bounded work status: done; confidence: verified static initializer/consumer relationship and renderer constants.** Actual text-entry behavior, input limits/aliases, dialog-type coverage, draw-argument interpretation and rendered output remain untested. No target execution, Ghidra writes or reconstruction edits were performed. Preserve the original's replace-first policy or Modern's append policy as appropriate rather than silently choosing a preferred UX.

## Network-service callback changes only its notice wrapper

The expanded [localized-notice audit](scripts/audit_localized_notice_difference.py) verifies complete same-address service-selection callback `0043f680..0043f75a` (218 bytes). Its only two differing bytes lie in the CALL at `0043f6f3`: original invokes `00444be0`, Modern invokes `0043fda0`, both with EAX=12. [The manifest](evidence/audits/localized-notice-difference.json) retains full-span hashes and the callsite evidence.

The call is conditional on incoming action 1, a zero result from `004446c0`, and nonzero result from service helper `0049ea70`. Its caller first copies the selected string to `006fbb7e`, marks the output byte 1, requests the notice, then enters the retained local refresh loop and later service call `0049e800`. Those instructions and all other callback branches are byte-identical. API/helper success semantics and actual connection state are not established by their local nonzero tests alone.

The [moved notice comparison](#localized-notice-wrapper-moved-counterpart-and-constructor-inputs) already verifies the wrapper difference: original supplies one localized string and fixed constructor arguments; Modern supplies the requested string plus localized ID 11, with revised constructor arguments. This callback is another concrete consumer of that change, rather than evidence of a rewritten network protocol.

**Bounded status: done; confidence: verified static full callback and linked wrapper contract.** Actual notice text/timing, service availability and multiplayer behavior remain untested. The callback's retained calls can still reach other version differences, so whole network equivalence is not claimed. Executables, Ghidra and maintained C are unchanged.
