# Original versus Modern: pending localized overlay

## Evidence and retained path

**Static paired comparison; no UI/game/instruction execution.** Both versions enter at `00494bd0`, gate work on `0079f288 != 0`, clear that pending flag before drawing, select scale `00791b54`, use packed text color `ffe0e000`, localize ID `ebh`, format a temporary string, draw through `004d1000`, then call `004d1340` and driver slots `009ef950` / `009ef940`.

Run `python3 analysis/scripts/audit_pending_overlay_difference.py`. The [manifest](evidence/audits/original-modern-pending-overlay.json) retains both baseline fingerprints, complete overlay bodies (original exclusive end `00494ca6`, Modern `00494c5a`), selected producer spans and exact format strings. The producer witnesses are not complete-function comparisons.

## Changed formatting and coordinates

| Aspect | Original | Modern |
|---|---|---|
| Format at `0053bdc8` | `" ... %s"` | `" %s"` |
| Draw-time layout setup | Calls `004beb20` with descriptor `007cdac0` and local output pointers; derives a float local using constant `0053bdd0` | Removes that query/conversion setup from this function |
| Horizontal input | Loads `0079f280` with FLD, converts through `004dfd56` / FISTP | Loads raw DWORD `0079f280` into EDX |
| Vertical input | Computes from the local float and `0053bdd4`, converts through `004dfd56` / FISTP | Loads raw DWORD `0079f284` into EBX |
| General registers | Explicitly saves EBX/ECX/EDX/EBP | PUSHAD/POPAD preserves all general registers |

This is a changed data contract, not safe evidence for interpreting both versions' globals as the same C types. In particular, original `0079f284` is used as floating scratch by the inspected producer, rather than the Modern renderer's direct vertical coordinate.

Modern producer witness `00494ec0..00494f12` computes a vertical coordinate through FMUL/FISTP plus an integer local offset and stores it to `0079f284`. It computes the horizontal draw position, calls `004d1000`, combines that call's x87 advance with scaled/integer layout inputs, and stores FIST to `0079f280` while retaining ST0 for a separate binary32 store. Thus integer coordinate publication happens upstream, under current x87 rounding. A C cast that truncates or a premature binary32 rounding could change the result.

Original witness `00494f42..00494f79` instead writes `0079f284` with FSTP and uses it in floating additions, then writes/uses `0079f280` as a float. This establishes distinct storage operations at selected producers; complete upstream layout correspondence and every alias/write remain unresolved. Constants at reused addresses must not be transferred across versions by address alone.

## State and failure boundaries

Both use an `118h`-byte local frame containing the format destination and other locals, and the formatting call has no destination-size argument. Actual ID-ebh strings and maximum expansion are not bounded here. Clearing the pending flag before draw/driver calls means a later failure does not locally restore it. Neither routine establishes synchronization around shared pending/coordinate/text state or restores previous scale/color state locally.

The retained driver calls are pointers, not proof of successful display, frame presentation or identical backend behavior. The removed ellipsis is statically visible, but its exact user-facing message and historical release association require localized text and caller admission evidence.

**Verified:** paired pending/draw flow, changed format, draw-time integer inputs, selected producer storage changes and register preservation. **Unresolved:** complete message identity, coordinate units/producer equivalence, every writer, localized length admission, transitive helpers and rendered output. No precision, replay or multiplayer compatibility conclusion follows from this overlay rewrite.

## Loading-abort context and installed message identity

The Modern caller witness `004a3500..004a3544` connects this overlay to the loading-presentation loop. When `0055e88c` is zero, it repeats progress helper `00495230` until that helper returns nonzero, then calls `004c62a0`. When `0055e88c` is nonzero at the loop gate, it instead calls `00494bd0` at `004a3532`, calls `004df8e0` with EAX=200 and sets EAX=1 on that path. The wait-adapter follow-up below resolves this to an alertable200 ms request, while actual presentation duration remains unmeasured.

Artwork initializer `00494cb0` sets pending global `0079f288=1` at `00494cec` (EDX was loaded with 1 at `00494cde`). Thus the overlay's clear-and-draw gate is armed as part of loading artwork setup. See the existing [loading artwork](original-modern-loading-artwork.md) and [loading timing/cancellation](original-modern-loading-timing.md) comparisons for the broader input-poll path. This is a static chain, not a captured abort interaction or a universal explanation of every write to `0055e88c`.

The [installed overlay label inventory](evidence/inventories/installed-overlay-labels.json) hash-identifies all 18 installed/local backup language files and validates ID **ebh (235)** offset and NUL termination within each. The inspected installed English and uppercase backup English payloads both contain **“Aborted”**. Exact bytes for each translation are retained; the JSON's Latin-1 text is a byte-preserving display, not an independently established code page. Backup naming does not authenticate retail provenance or prove which file loads at runtime.

Combining that label with the paired format constants gives original English `" ... Aborted"` versus Modern `" Aborted"` for these payloads. This supports identification of the path as a loading-abort overlay while preserving the separate questions of rendering success, active language and precise trigger cause. No game was aborted for this investigation.

Reproduce the label evidence with `python3 analysis/scripts/inventory_overlay_labels.py --game-dir '<installed game directory>'`. The static audit script retains the arming and caller spans alongside the renderer evidence. Remaining work: full flag-writer provenance, complete coordinate-producer correspondence, message-expansion bounds and actual rendered output.

## Abort presentation requests an alertable 200 ms wait

The expanded overlay audit verifies complete helper `004df8e0..004df8ef` (15 bytes) is identical in original and Modern and resolves IAT `00534604` to `SleepEx`. It preserves ECX/EDX, pushes literal1 followed by incoming EAX, calls the API and returns its result. This reuses the same adapter already identified in the [asynchronous-wait comparison](original-modern-async-wait.md).

Modern's abort-presentation branch loads EAX=200 at `004a3537` and calls that helper at `004a353c`, immediately after calling the overlay routine at `004a3532`. It then returns1 through the caller's existing unwind. The overlay itself is conditional on its pending flag, so a wait request does not prove that a new message was drawn on every visit.

Microsoft's [SleepEx contract](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleepex) defines the first argument in milliseconds and the second as alertability. Accordingly, this is a verified **200 ms alertable wait request**. An I/O completion/APC can end an alertable wait early, and scheduling can delay resumption after timeout. Neither the wrapper nor this abort branch measures elapsed time and retries the remainder. Thus the instructions do not prove a display duration of exactly200 ms.

**MP160-011 has partial static support:** final Modern adds the explicit wait on this inspected abort path. Its wording about an `Aborted` message and an original duration around500 ms still requires a complete original presentation/timing trace and actual language/render evidence. The already captured original session-loading path does not supply that proof. No500→200 runtime measurement, universal abort coverage or historical introduction is claimed. No game or instruction probe was executed.
