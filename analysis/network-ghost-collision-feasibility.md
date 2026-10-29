# Network ghost collision feasibility

## Scope and result

This is a read-only static comparison of the installed replay-pose ghost path
with the ordinary vehicle-pair collision path, including the callback setup
used for network participants. It does not implement a mode or establish a
runtime result.

**Finding:** the existing replay ghost is rendered from packed pose samples
through a separate renderer and is not shown entering the live vehicle
collision-pair list. Ordinary and remote-human participants, by contrast,
receive the same per-vehicle update callback that can append active vehicles
to that list. The observed append gate is vehicle activity/timer state, not a
network-role or category test. No dedicated collision-only ghost flag was
identified in this bounded path. Thus replay ghosts already appear
architecturally separate from collision, while selectively making a remote
human car noncolliding is not established as a supported option.

## Artifact and reproducibility

Target: installed `nfs3.exe`, SHA-256
`2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
REA/Ghidra inspection used the original executable read-only; no game or
network session was run and no persistent Ghidra edits were made. The REA
session was closed after inspection.

Key instruction ranges can be re-read from that exact artifact with:

```sh
objdump -D -Mintel --start-address=0x4310c0 --stop-address=0x431250 nfs3.exe
objdump -D -Mintel --start-address=0x430c80 --stop-address=0x430cd0 nfs3.exe
```

The collision updater’s callback address and branch details are in the first
range; `00430c80` dispatches the pair geometry/collision helpers in the
second. In REA, the relevant inspected procedures were `0042c400`,
`004bbba0`, `004bc160`, `00430c80`, `0042fee0`, and `0042f280`.

## Existing replay ghost

The established pose contract in [pose-ghost-contract.md](pose-ghost-contract.md)
identifies replay samples as 18-byte records from the separate ghost/replay
buffer. The playback control path `004bc160` calls `004bbba0` for its
recorded-pose updates. At the end of `004bbba0`, playback rendering is
conditionally submitted through `004b9df0` (the pose renderer), followed by
another replay/render helper. Inside `004bbba0`, the participant iteration
reads vehicle pointers from `005efac8` and processes their live vehicle
fields; the pose renderer call is a distinct later step. No call from the
pose interpolation/render path into the collision updater or pair resolver
was found in the reviewed path.

This supports a narrow architectural conclusion: the replay ghost visual is
not shown as a live vehicle object in the collision list. It does not mean a
remote network human is equivalent to that replay ghost; remote humans have
normal vehicle records and motion/control callbacks.

## Live vehicle pair admission and collision checks

`InitializeVehicleUpdateCallbacks` (`0042c400`) installs `004311d0` in the
vehicle callback slot at `+0x618`. The same initializer sets the other vehicle
callbacks, and its network-human branch can replace the control/dynamics
callbacks while leaving `+0x618` unchanged. Its branch for qualifying
nonlocal network humans is gated by network/session/master-index conditions;
it does not select a collision-specific callback.

The callback at `004311d0` first decrements a positive vehicle `+0x174`
counter. It considers the object for collision-pair admission only when
vehicle byte `+0x88` is zero, byte `+0x89` is nonzero, and the post-decrement
DWORD at `+0x174` equals zero. When those conditions hold, it calls
`004310c0`.

`004310c0` keeps the candidate pointers in the global array beginning at
`005efe10`, with count at `005537bc`. For each existing entry it performs
axis-aligned extent-overlap comparisons from vehicle fields around `+0x98`
and `+0x120`; only overlapping candidates reach `00430c80`. That routine
tries the pair geometry helper `0042fee0` (up to 33 calls when all returns remain nonzero: EBX starts at32 and
the loop stops after decrementing to-1) and conditionally calls the response/contact helper `0042f280`.
There is no test here of network identity, remote-human role, replay mode,
vehicle category bit `+0x200`, or a separate ghost/collision opt-out flag.

The same `004311d0` body also uses these gates for other work. Nonzero `+0x88` or zero `+0x89` skips its later scene/contact calls too, including `004304b0` and `004a0140`. A nonzero post-decrement `+0x174` suppresses pair admission and the conditional `00430da0` call, while the `+0x188 & 0x80` boundary-contact branch and `004a0140` remain reachable. Rendering also reads these fields: `004bbba0` rejects live-vehicle drawing on inactive `+0x89` or nonzero `+0x88`, while a nonzero `+0x174` participates in the alternating `+0x8bc` branch that can skip `004bb4c0` (`004bbc48..004bbca8`). These fields therefore cannot be assumed to be collision-only controls.

## `+0x174` initialization and temporary suppression lifecycle

The ordinary participant construction loop is `0042c700`: it iterates to
`006fd510`, prepares each vehicle through `0042c350`, and that setup calls
`0042bcb0` followed by `004a0d20`. The latter clears a `0x1e4`-byte vehicle
record, then explicitly initializes `+0x88=0`, `+0x174=0`, and `+0x89=1`
(`004a0e0e`, `004a0ec5`, `004a0f08`). This gives the normal constructed
participant the active-state values accepted by `004311d0`, subject to other
race gates. `0042c400` subsequently installs the callback at `+0x618` for
each object; its qualifying network-human override does not replace that
slot.

The other direct `+0x174` writes in the executable’s `.code` section are:

| Address | Operation and surrounding path | Supported interpretation |
| --- | --- | --- |
| `00428a82` | `00428970` stores global `005efdc8` to vehicle `+0x174`; `0042c600` is the sole direct writer found for that global and initializes it to zero. | Common vehicle reset clears the field on the reviewed initialization state. |
| `0040bf27` | `0040bd80`, reached from `00408f10` after its track/motion correction gates, calls `00428970`, then stores `64` at `+0x174` and `32` at `+0x524`. | A correction/reset path starts a finite suppression interval. Exact gameplay label is not established. |
| `004290e0` | `00428f90`, reached from recovery helper `00429260`, calls `00428970`, then stores `64` at `+0x174`. | Contact/recovery path starts the interval. |
| `00429240` | `00429100`, called by stop/reset state paths, calls `00428970`, then stores `64` at `+0x174` and `32` at `+0x524`. | Pursuit/reset path starts the interval. |
| `004311ec` | The per-vehicle callback decrements the field when positive. | The interval advances by callback invocations, not a verified wall-clock unit. |
| `004a0ec5` | `004a0d20` clears the constructed vehicle record and stores zero. | Normal vehicle initialization starts with no interval active. |

The `+0x174` gate in `004311d0` tests the value **after** its positive-value
decrement. Thus a reset-written `64` keeps the vehicle out of pair admission
until the callback has counted it down to zero; the same nonzero value also
suppresses the `00430da0` branch. The rendering code uses the field to select
an alternating update/draw path, so these reset-produced intervals also
affect the car’s visible blink/refresh behavior. This is a temporary
post-correction/recovery state with more than one observed consumer, not
evidence of an independent collision preference. The exact visual effect
and the elapsed time corresponding to 64 callback invocations have not been
runtime-verified.

The code census was bounded to direct immediate-offset references in the
exact executable’s `.code` disassembly. It establishes the direct stores
listed above; pointer-based aliases or writes outside that segment are not
excluded. For the specific vehicle constructor chain and timer global,
REA/Ghidra references resolve `004a0d20` to caller `0042bcb0`,
`0042c600` as the direct writer of `005efdc8`, and `00428970` callers to
`0040bd80`, `00428f90`, and `00429100`.

## Per-tick pair-list reset and callback schedule

`004c48d0` is the simulation-step helper used by `RunRaceLoop` (`004c4e40`;
direct calls include `004c5358`, `004c536c`, `004c5376`, and `004c53e1`).
All its ordinary control-flow branches converge on `004c4a65`, which calls
`00430cd0`; that helper sets candidate count `005537bc` to zero. `004c48d0`
then tests the low bit of simulation counter `007d3684`. If it is clear, it
dispatches the vehicle update list `007d3690` through `004be3a0`. The counter
is incremented once at `004c4a9c`, after this dispatch. Therefore, the
candidate-pointer array at `005efe10` is not cleared byte-for-byte, but its
count is reset on every call to the simulation-step helper before any
collision callback dispatch. Old pointers beyond the zero count are not
considered in the next step.

Setup helper `0042c830` loops the configured vehicle records at
`005efac8..` through count `006fd510`, and enqueues each record's `+0x618`
function into list `007d3690` with priority `0x28` (`0042c8d0..0042c8e2`).
The initializer `0042c400` stores `004311d0` in that slot, including before
its qualifying network-human callback overrides. Thus, on each
`004c48d0` invocation whose simulation counter is even, the normal registered
vehicle callback list includes the `+0x618` collision updater for each
vehicle whose callback remains installed. This is simulation-counter
scheduling evidence, not a wall-clock frequency claim.

For an uninterrupted timer value of64, `004311d0` decrements once per such
vehicle callback invocation. The invocation that changes1 to0 passes the
timer equality gate and may append the vehicle; the previous63 invocations
with values63..1 do not. This bounds the timer in callback invocations, not
seconds. If a reset path writes64 after that vehicle's callback has already
run in a step, that vehicle may already have been considered in the current
fresh pair-list build; the direct evidence does not establish writer order
for every reset caller. Regardless, the next simulation-step helper resets
the pair-list count before the next collision callback pass, so a previously
appended pointer cannot persist into a later step solely because the timer
became nonzero.

Reproducible byte windows for this lifecycle are `0042c830..0042c94d`
(callback registration), `00430cd0..00430cde` (candidate-count clear), and
`004c48d0..004c4abb` (reset, conditional dispatch, and tick increment). The
same exact executable and SHA-256 listed above were used.

Consequently, a remote-human vehicle is not specifically removed from
pairwise collision by its network role in this path. If it has the same
active/timer field values required by `004311d0`, its pointer can be admitted
alongside other active vehicles. This is a conditional static statement:
the direct constructor state and `+0x174` timer transitions are now traced,
while complete lifecycle meanings of `+0x88` and `+0x89` and runtime behavior
remain open.

## Feasibility boundary

- **Replay ghost:** already follows a separate pose-render route; no live
  vehicle-pair registration was established for it.
- **Remote-human vehicle:** uses the vehicle callback setup and is subject to
  the same active/timer admission conditions as other live vehicles. The
  pair filter has no observed network-role or category exclusion.
- **Selective noncolliding network option:** unsupported by the inspected
  gates alone. The existing `+0x88` and `+0x89` conditions affect admission
  to this callback’s collision list, but their broader lifecycle effects and
  intended meanings are not established. Changing them cannot yet be
  described as a collision-only toggle.

To establish an implementation path would require a distinct collision-only
gate, or a verified change to existing pair registration that preserves the
other consumers of `+0x88`, `+0x89`, and `+0x174`, followed by a controlled
ordinary multiplayer check of remote motion, rendering, input, and race
progress. No such option or effect is claimed by this report.

Parent review independently checked full instruction bodies for callback initializer `0042c400`, pair append/broad phase `004310c0`, pair driver `00430c80`, separator `0042fee0`, impulse/event response `0042f280`, and updater `004311d0`. The driver call limit is33, correcting the worker's initial32 wording. No network-role/category exclusion appears in those inspected bodies; transitive helper behavior and runtime effects remain qualified.
