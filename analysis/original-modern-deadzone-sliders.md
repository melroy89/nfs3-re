# Dead-zone sliders: rounding, row numbering and initializer cleanup

## Evidence and scope

[The static audit](scripts/audit_deadzone_sliders.py) verifies both pinned executable hashes, complete function envelopes, conversion constants and widget-name literals. [Its manifest](evidence/audits/deadzone-sliders.json) records full span hashes and retained disassembly. No controller, menu or instruction probes were executed.

| Saved Modern entry / label | Full envelope, exclusive end | Scope distinction |
|---|---|---|
| `00442dd0` ApplyDeadzoneAxisSliderValues | `00442dd0..00442e5a` (138 bytes) | Saved Modern union excludes six NOP bytes |
| `00443070` InitializeDeadzoneAxisSliders | `00443070..0044325c` (492 bytes) | Modern returns at `00443207`; old remaining tail is NOP-filled |

## Applying slider values removes explicit truncation

Original calls rounding helper `004dfd56` at `00442e03` and `00442e0d`; Modern replaces each five-byte CALL with a short jump and three NOPs. All other bytes in the 138-byte envelope are identical, including the two retained FISTP DWORD conversions at `00442e16` and `00442e1f` and `RET 16` stack cleanup.

The four stack arguments include two binary32 values and two DWORD indices. Both multiply the float inputs by the same file-backed 100.0 at `00538a10`, calculate an indexed pair at `006fc970 + 136*device_index + 72 + 8*axis_index`, compare converted values with its two DWORDs and write/call `00435b40` only for changed members. The two calls distinguish pair members using EBX=1 or EBX=0. This establishes caller-side propagation; full downstream device-property semantics are not qualified here.

As established by the [HUD rounding comparison](original-modern-hud-layout.md#pixel-conversion-removes-explicit-truncation-before-fistp), original's helper performs toward-zero FRNDINT and restores the incoming control word. Modern's removed calls leave final FISTP governed directly by that incoming word. For ordinary representable values, a product of 12.75 therefore becomes 12 in original and, **if round-to-nearest is active**, 13 in Modern. This is a conditional instruction-level derivation, not a tested controller value. Exception behavior and actual caller control state remain separate.

## Initializer changes register preservation and row layout

Original begins by saving EBX, ECX, ESI, EDI and EBP; Modern uses PUSHAD and ends with `MOV ESP,EBP; POPAD; RET`. Modern additionally restores incoming EAX/EDX. Neither version's eventual EAX should be casually annotated as the same useful C return value.

Original initializes ESI=0; Modern initializes ESI=1. The retained loop scans eight possible slider pointers at `00558a10 + 4*axis`. It checks device capability bits from the selected 136-byte device record, sets callbacks/flags, copies SI into slider WORD `+40`, and increments ESI only for an admitted axis. Thus enabled-row numbering changes from zero-based to one-based. In the layout branch gated by `00559234`, the same SI-derived index selects the WORD from `00559c94 + 4*row`; the starting row changes there as well.

That branch also changes the literal written to slider WORD `+6` from 242 to 220 at `004431da`. The table-derived WORD at `+8` and other shared instructions are retained. These are verified field/layout inputs, not a pixel-perfect rendering claim or proof of what every unknown widget field means.

The initializer still reads existing integer pair values, multiplies each by identical binary32 `0.009999999776482582` at `00538a40`, stores binary32 and passes it to `0046c950`. This retained approximate factor must not be confused with a new exact division algorithm. The pair storage/callback route is unchanged in this core.

## Removed named-widget tail

Original `00443204..00443254` finds four named widgets through `00442a40`, using file-backed strings `TEST`, `WHAT_R0`, `WHAT_R1`, `WHAT_R2`, and ORs byte flag `+5` with `10h` for each nonnull result. Modern returns at `00443204..00443208` instead and NOP-fills the rest of the old envelope. Original null-entry early exit targeted `00443254`; Modern targets its earlier epilogue.

This removes this routine's explicit flag-setting tail, not the widgets themselves or every writer of that flag. Their actual visibility/interactivity and initialization by other paths remain unverified. No controller detection, hardware compatibility or force-feedback improvement follows solely from these changes.

## Reconstruction and follow-up

**Bounded work status: done; evidence confidence: verified static code, constants and literals.** Preserve row-counter start, register contract, floating-point conversion policy, capability admission and callback order for the selected version. A C cast would impose truncation and would not generally match Modern's current-rounding-mode FISTP contract.

**Pending:** all caller rounding states, pair-field semantics and device property application, widget flag meaning across other producers, layout-table bounds/provenance and actual input/UI behavior under Windows or Wine. These affect interfaces, data layout and runtime validation. Executable bytes, saved Ghidra state and reconstruction sources are unchanged.

## Capability refresh reduces its scan from sixteen slots to fifteen

The expanded [input audit](scripts/audit_deadzone_sliders.py) verifies complete same-address `00472b60..00472d0d` (429 bytes), saved as `RefreshDirectInputDeviceCapabilityCache`. Only byte `00472c93` differs: `CMP DWORD [EBP-4],16` becomes comparison against 15. The following signed `JGE exit` and all other instructions are identical. [The manifest](evidence/audits/deadzone-sliders.json) records full hashes and disassembly.

The local index starts at zero, enters the body through `00472c96`, increments at `00472c8d`, then applies that bound. Thus original processes ordinals **0..15**, Modern **0..14**. This is not merely a changed display label or a decrement applied after sixteen iterations.

Both call `00435690` with the ordinal and map the frontend/config cache to `006fc970 + ordinal*88h`. Null query results clear `88h` bytes; changed capability/name records can copy 22 DWORDs; unchanged records can compare eight axis-value pairs and propagate changed members through `00435b40`. The new bound skips the entire ordinal-15 refresh route, including its clear/copy/compare operations and any per-slot counter contribution.

Existing [device-slot lifecycle evidence](controller-device-slot-lifecycle.md#result) establishes a separate primary 16-slot domain: normal registration can populate slot 15, initial capability query traverses all sixteen, and the race reader accepts slot 15. That evidence describes the selected Modern executable; it does not by itself prove every original interface path identical. Coupled with the direct paired refresh comparison, it shows why this edit should **not** be labelled a verified bounds fix: Modern omits refreshing a frontend slot that remains in its primary device domain.

**Bounded comparison status: done; confidence: verified full refresh bodies and previously qualified Modern slot lifecycle.** Actual sixteen-device availability and stale/unrefreshed frontend consequences are unobserved. Cache extent/other writers, every original device path and author intent remain separate. Preserve the version-specific bound in reconstruction rather than silently “correcting” it. No new hardware, game or instruction probes were run; executables/Ghidra/maintained C are unchanged.
