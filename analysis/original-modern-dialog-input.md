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
