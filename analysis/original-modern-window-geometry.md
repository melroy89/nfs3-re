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
