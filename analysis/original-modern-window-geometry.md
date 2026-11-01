# Original versus Modern: window creation and retained sizing helpers

## Evidence and scope

Static supplied-original/official-Modern comparison, with exact hashes in the [window lifecycle report](original-modern-window-handling.md). Reproduce with `python3 analysis/scripts/audit_window_initialization_difference.py`. The [manifest](evidence/audits/original-modern-window-initialization.json) retains both complete creation bodies and asserts four identical ranges. No game/window/API execution, executable edits or Ghidra changes.

## Creation policy is retained through the API call

The **293 bytes `004cd350..004cd474`** are identical, including the CreateWindowExA call at `004cd46e`. The routine takes its context pointer in EAX and loads base style from `0056128c`.

| Context/flag condition | Retained construction policy |
|---|---|
| Byte `context+0x45d` nonzero | Position fields `+0x464/+0x468` set to zero; size from GetSystemMetrics arguments 0/1; OR style with `80000000`; extended style 8 |
| Byte zero | OR style with `00ca0000`; extended style initially `00040000` |
| Byte zero, `[00564390] & 0x20` nonzero | Also OR style with `00050000` |
| Byte zero, that flag clear | Also OR style with `00800000`; extended style becomes `00040100` |

In the byte-zero path, `context+0x454` selects either stored coordinates or local coordinates `-8192,-8192`. Dimensions from `context+0x14/+0x18` form the requested client rectangle; AdjustWindowRect is called with the resulting style and menu=false. Adjusted coordinates/sizes are passed to CreateWindowExA along with existing class/title/module fields.

These are observed constants/offsets; neither identical instructions nor the names “windowed/fullscreen” prove identical context values or driver display state. The base style producer and complete context initialization are not re-audited here. AdjustWindowRect computes the surrounding window extent from a requested client rectangle; it does not itself change display mode. [Microsoft documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-adjustwindowrect)

## Modern shortens post-creation setup

The creation routines diverge immediately after CreateWindowExA:

- Original saves the returned handle in ESI and, only when nonzero, calls SetCursor(NULL), conditionally ShowCursor(FALSE) when `context+0x45d` is nonzero, clears `00564814`, and conditionally calls `004fb710` for indices 0,1,2 with EDX=0 when `00561298` is zero. It returns the saved handle at `004cd4c6..004cd4d0`.
- Modern unconditionally clears `00564814` and returns directly (`004cd475..004cd487`). MOV does not alter EAX, so the API handle/failure result remains the return value. The original local cursor and three-call setup block is absent.

This proves removal from this routine, not removal of every cursor or input-state operation elsewhere. Moving lifecycle responsibility cannot be fully explained without those other callers. Modern also clears `00564814` on creation failure, unlike original's success-only block; the global's complete contract remains unresolved.

## Three complete sizing helpers are unchanged

The manifest asserts exact equality for:

| Entry/range, inclusive | Bytes | Retained behavior |
|---|---:|---|
| `004cdb10..004cdbcc` | 189 | Adjust and apply a client rectangle; publish actual client origin/size |
| `004cdbd0..004cdc13` | 68 | Calculate centred coordinates from two screen metrics and requested dimensions, then call the first helper |
| `004cdc20..004cdc4b` | 44 | Request origin zero and the two screen-metric dimensions through the first helper |

`004cdb10` accepts EAX=x, EDX=y, EBX=width and ECX=height. It builds a RECT using low-32-bit additions, reads GetWindowLongA(handle,-16), calls AdjustWindowRect with menu=false, and calls SetWindowPos with flags **0x14**. Those flags combine NOACTIVATE and NOZORDER, according to [Microsoft's SetWindowPos contract](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos). It then gets the client rectangle and maps both corners through ClientToScreen, storing origin at `009f3d34/38` and dimensions at `009f38e4/e8`. API return values are not locally checked.

`004cdbd0` takes width in EAX and height in EDX. It computes each screen-minus-requested difference and signed division by two rounded toward zero using SAR/sign correction, then invokes `004cdb10`. This is not a per-monitor working-area calculation in this body: it passes literal metric indices 0 and 1 and contains no monitor-selection call. Actual OS/Wine metrics remain untested.

Modern's renderer path calls this retained centring helper before a mode request and during publication, as traced in the [mode-selection report](original-modern-mode-selection.md). Changed callers/data can therefore produce changed window behavior even with identical helper bytes. Do not attribute these sizing formulas themselves to a Modern rewrite.

## Remaining comparison work

Verified: retained style/size construction through CreateWindowExA, changed post-creation setup and exact sizing-helper equality. Pending: base-style/context producers, meaning and other users of `00564814`, replacement cursor/input setup, all foreground/focus paths, DPI/multiple-monitor behavior and actual windowed/fullscreen operation. No broad runtime improvement or historical release date follows from this static chapter alone.

## Removed startup reset of keyboard toggles

The [expanded window audit](scripts/audit_window_initialization_difference.py) now retains the complete original helper `004fb710..004fb78f` and its two adjacent Num Lock wrappers, in addition to the complete paired creation routines. The [manifest](evidence/audits/original-modern-window-initialization.json) identifies actual imports `GetKeyState` at `00534744` and `keybd_event` at `005347ac` in both binaries. No keyboard event was generated during inspection.

The helper consumes EAX as an index and EDX as the desired toggle state. It reads GetKeyState's low bit, compares the resulting0/1 with the requested value, and does nothing when equal. Otherwise it calls keybd_event twice with extra-info0:

| Index | Virtual key / scan byte | Down flags / up flags |
|---:|---|---|
|0 | Caps Lock:0x14 /0x3a |0 /2 |
|1 | Num Lock:0x90 /0x45 |1 /3 |
|2 | Scroll Lock:0x91 /0x46 |0 /2 |

Other index values return without this pair. Flags1 and2 are EXTENDEDKEY and KEYUP respectively; the API describes synthesized key transitions and demonstrates Num Lock toggling. See [Microsoft keybd_event](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-keybd_event) and [GetKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate). These API contracts explain the call shape; they do not demonstrate Windows/Wine accepted events or changed physical LEDs.

The original creation caller supplies desired EDX0 for indices0/1/2 at `004cd4a9`, `004cd4b5` and `004cd4c1`. It reaches these calls only after successful CreateWindowExA and when `00561298 == 0`. Thus the observed original policy is conditional clearing of toggle state at this creation boundary, not unconditional clearing on every conceivable startup path. Adjacent original wrappers at `004fb6f0`/`004fb700` request Num Lock1/0, but their own caller reachability is not established here.

Modern returns directly after its shared-state store at `004cd475..004cd488`, omitting the original reset calls. The old helper's address range is reused by the [INI/environment implementation](original-modern-configuration.md), so same-address Modern bytes are not a corresponding keyboard helper. Both imports and the keybd_event thunk remain; their presence must not be reported as proof that startup still resets toggles, or as newly added functionality.

MP100-038 has **bounded static support** for removal of this original startup operation. All alternate/indirect callers, device/OS effects, toggle state observed at launch and v1.0.0 introduction remain unverified. The separate [Num Lock keypad translation change](original-modern-window-key.md) concerns handling later input and must not be conflated with this removed reset.
