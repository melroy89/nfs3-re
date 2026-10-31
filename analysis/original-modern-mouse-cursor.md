# Mouse cursor callback: conditional hiding and result-slot anomaly

## Scope and evidence

The original and official Modern callback starts at `00436930`. Compare the 79-byte envelope `00436930..0043697f` using [the reproducible audit](scripts/audit_mouse_cursor_callback.py) and [hash-pinned manifest](evidence/audits/mouse-cursor-callback.json). Original returns at `00436978` with `RET 24`; Modern returns at `0043697c` with the same stack cleanup. No cursor/window/game execution was performed.

Existing research already establishes the [six-argument callback contract and lifecycle limits](window-message-handler-contract.md#mouse-handler-retains-a-prior-callback-independently). This comparison adds the original counterpart rather than treating that Modern-only research as comparative proof.

## Retained registration and forwarding

The complete witness `004351a0..004351eb` is byte-identical. It sets ESI to message ID `20h`, looks up the existing callback through `004cc660`, saves that pointer to `00554ef4`, then registers `00436930` through `004cc6d0`. The [table contract](window-message-handler-contract.md) explains lookup and replacement; this is an internal callback, not a four-argument Windows procedure.

The first 45 callback bytes `00436930..0043695d` are identical. If `00554ef4` is nonzero, both forward all six arguments to it, then continue irrespective of its returned handled flag. The argument layout after the callback prologue is:

| Frame offset | Argument |
|---|---|
| `+14` | context |
| `+18` | HWND |
| `+1c` | message |
| `+20` | wParam |
| `+24` | lParam |
| `+28` | result pointer |

The previous callback can write through that pointer. Its result must not be assumed zero merely because its returned EAX is ignored.

## Verified changed tail

Original unconditionally calls `SetCursor(NULL)` at `0043695f`, then `ShowCursor(0)` at `00436968`, and returns handled flag 1. Modern instead initializes EBX=0 and compares the low WORD of lParam with 1 at `0043695f`. On inequality it returns handled flag 0. On equality it calls `SetCursor(NULL)` at `00436968`, sets EBX=1, writes DWORD 1 to `[EBP+28]`, then returns EBX. This removes the callback's unconditional display-count operation and restricts its explicit cursor-hiding call to that low-WORD case. It does not prove that ShowCursor is absent elsewhere.

The write at `0043696f` replaces the **incoming argument slot containing the result pointer**. It does not dereference that pointer or write a result into the window procedure's local storage. This distinction is verified by the instruction `c7 45 28 01 00 00 00`; reconstructing it as `*result = 1` would silently change the machine behavior.

## Consequence through the retained window procedure

The full dispatcher `004cd2d0..004cd348` (120 bytes) is byte-identical. As detailed in the [window-handling comparison](original-modern-window-handling.md#3-preserved-dispatcher-exposes-a-power-handler-anomaly), callback EAX controls whether ordinary default processing runs; the Windows return value comes from a separate local initialized to zero and passed by pointer.

Thus Modern's matching branch is handled, but its own stack-slot write does not make the Windows result 1. If no previous callback writes an output, the local remains zero. If the chained callback wrote one, that value remains available. The nonmatching branch returns zero and permits the dispatcher's default processing, even when the previous callback returned nonzero. Original always prevents that default processing after this callback. These are static control-flow consequences, not observed cursor defects or a claim about author intent.

## Reconstruction and remaining work

**Bounded comparison status: done; evidence confidence: verified static instructions.** Preserve the six-argument ABI, prior-callback invocation, version-specific handling policy and actual stack-slot write when reconstructing machine behavior. Do not automatically correct the apparent result-write anomaly.

Pending runtime/lifecycle questions are the saved callback's identity and output in each configuration, display-count balance across other callers, focus/nonclient behavior and actual host/Wine cursor effects. The earlier conditional self-chain/lifetime investigation remains explicitly bounded in the existing contract; this difference does not establish that sequence is reachable.
