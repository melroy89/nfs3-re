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
