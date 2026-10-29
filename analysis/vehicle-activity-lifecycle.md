# Vehicle activity-byte lifecycle (`+0x88` / `+0x89`)

## Scope and finding

This is a bounded, read-only static audit of direct byte-width references to
offsets `+0x88` and `+0x89` in the installed NFS III executable. It focuses on
ordinary participant construction, activation/deactivation, remote network
participants, replay, collision-update admission, and rendering.

The ordinary participant builder initializes each constructed vehicle with
`+0x88 = 0` and `+0x89 = 1`. `+0x89` is directly cleared/set by a generic
vehicle transition path, but its caller chain does not identify network
disconnect or replay unload as the reason for a transition. `+0x88` is cleared
in several environment/query paths. Its sole direct nonzero store in the byte
census is in a frontend mouse-drag routine, not an identified live-vehicle
path. Both bytes gate work beyond collision admission, including rendering and
spatial/environment updates. The code supports describing their observed
effects, but not assigning either byte a complete lifecycle name.

The existing replay pose ghost remains a distinct rendering path: it consumes
packed pose samples and is not shown as a live vehicle record entering the
participant collision list. A remote network human is instead a normal
participant vehicle. Its control/dynamics callbacks may be replaced during
initialization, while the ordinary update callback at `+0x618` remains
installed. No direct `+0x88`/`+0x89` test distinguishes that remote role.

## Artifact and reproducible direct census

Target: installed `nfs3.exe`, SHA-256
`2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.
The analysis used REA/Ghidra against the exact original file plus GNU objdump
disassembly. No game execution, live-memory inspection, persistent Ghidra
annotation, or executable write was performed.

From a shell, with `EXE` set to that exact path, reproduce the direct byte
reference census with:

```sh
objdump -D -Mintel --section=.code "$EXE" \
  | rg 'BYTE PTR \[[^]]*\+0x8[89]\]'
```

This yields **53 direct byte-width instructions** in `.code`: **32** at
`+0x88` and **21** at `+0x89`. The address lists below are the complete output
addresses for this exact executable and pattern. This is a complete census of
that bounded instruction form, not a complete alias or whole-program dataflow
census: wider accesses, pointer aliases, data outside `.code`, and indirect
call effects are outside the count.

| Offset | Direct instruction addresses |
| --- | --- |
| `+0x88` (32) | `00408a56`, `0041ba83`, `0041c3a2`, `0041c6f4`, `00421939`, `00428b2c`, `0042b925`, `004311f2`, `00466815`, `0046681e`, `00466842`, `00466895`, `00466f23`, `00467627`, `0046774c`, `00467951`, `0049fec3`, `0049ffb8`, `004a0596`, `004a07c7`, `004a07ff`, `004a080e`, `004a0895`, `004a08a4`, `004a094b`, `004a0cce`, `004a0e0e`, `004a26ab`, `004a285a`, `004b9821`, `004bb603`, `004bbc51` |
| `+0x89` (21) | `00405d8a`, `00405dde`, `0040d047`, `004122b7`, `0041c3af`, `0041c701`, `0042192b`, `00428b39`, `0042b92e`, `0042ce8f`, `004311fb`, `0049ffab`, `004a08ca`, `004a0f08`, `004a269e`, `004a284d`, `004a2c63`, `004a2e2d`, `004b9814`, `004bb5ef`, `004bbc48` |

Several matching displacements are in generic resource/metadata records, not
demonstrated vehicle records. In particular, `0046774c` and `00467951` clear
`+0x88` in routines that initialize/reset records reached through the
`0044a660` lookup path; adjacent accesses initialize small IDs, flags, and
resource pointers. They are included in the mechanical census but excluded
from the live-vehicle writer conclusions below. Likewise, a byte census does
not interpret a `DWORD PTR [vehicle+0x88]` access as four independent byte
field uses: the DWORD overlaps later bytes and must be understood in its own
instruction context.

## Direct vehicle initialization and active-update registration

`0042c700` iterates participant slots up to global `006fd510`. For each slot it
loads a pointer from `005efac8`, calls setup `0042c350`, and later calls
`0042c400` to install that participant’s callbacks. The setup path calls
`004a0d20`; after clearing `0x1e4` bytes, that initializer explicitly writes
`+0x88 = 0` at `004a0e0e` and `+0x89 = 1` at `004a0f08` (it also initializes
`+0x174 = 0`). These are direct evidence of the normal constructed
participant’s initial byte values.

`0042c400` installs `004311d0` at vehicle `+0x618`. For a qualifying
nonlocal network participant, its callback setup changes the control/dynamics
callback slots; it does not replace `+0x618`. In `004311d0`, the object is
considered for collision-pair admission only if `+0x88 == 0`, `+0x89 != 0`,
and the post-decrement value of `+0x174` is zero. These are per-object state
tests; there is no direct network-role or replay-mode check in that admission
gate.

The same activity bytes gate other work. The reviewed `004311d0` path also
uses them around scene/contact calls. Readers in `004a08c0`/`004a0580` gate
environment/query refresh and resource updates; readers in `004a2690` gate
transformed basis/inertia updates. Rendering paths `004bb5d0` and `004bbba0`
check active `+0x89` and zero `+0x88` before drawing live vehicle records.
Vehicle scans in `0041b9b0`, `0041c310`, `0041c670`, and `004b97b0` also filter
one or both activity bytes. Thus changing these bytes would affect several
ordinary update/draw paths; the direct evidence does not support describing
them as collision-only switches.

## `+0x89`: directly observed activation state changes

The only direct byte stores to `+0x89` in the `.code` census are:

| Address | Procedure | Operation | Context |
| --- | --- | --- | --- |
| `00405d8a` | `00405d40` | store `0` | `00405d40` also computes a delay into `+0x650`, increments global `0056ebc0`, and sets bit `4` in byte `+0x620`. |
| `00405dde` | `00405dc0` | store `1` | `00405dc0` decrements `0056ebc0`, clears bit `4` in `+0x620`, and conditionally calls category helpers according to bits in `+0x200`. |
| `004a0f08` | `004a0d20` | store `1` | Ordinary vehicle construction, after whole-record initialization. |

REA’s direct caller result for both `00405d40` and `00405dc0` is only
`0040df10`. That transition helper is reached by several gameplay/state
paths, but its call alone does not show that a particular invocation means a
remote-human disconnect, replay teardown, or roster removal. The counter and
`+0x620` changes establish a shared inactive/active transition mechanism; the
full meaning and all transitive triggers are not proven by this byte audit.

The inspected normal transition machine is narrower than an unrestricted toggle: `0040df10` first requires `00401240` to return nonzero. Its state DWORD `+0x630 == 1` calls the reactivation predicate `00405e20`; success calls `00405dc0` and advances to state2. In state2 it calls `00405cd0`; success calls `00405d40` and returns to state1. Other incoming states are normalized to2, with a bit2-dependent placement/deactivation path that can enter state1. Predicate `00405e20` dispatches category bit0x10 to `0040c210` and bit0x20 to `00402c70`, otherwise returns0. These instructions connect activation to ordinary category-specific gameplay state; their transitive conditions and live ordering remain separate.

The ordinary remote-human setup in `0042c400` is an initialization-time
callback selection branch, not an observed `+0x89` transition. The replay
pose-render path processes replay samples separately from the live participant
list. No direct evidence here shows replay preparation or playback changing a
live vehicle’s `+0x89` byte. Conversely, no direct evidence proves that
network disconnect cleanup cannot later reach `0040df10` through an indirect
or unanalyzed route.

## `+0x88`: reset/clear paths and the unresolved setter

The ordinary vehicle initializer `004a0d20` writes `+0x88 = 0`. The other
vehicle-context clear operations found in the direct census are in
`004a0580`, called by `004a08c0`. This environment/query routine has multiple
branches that clear `+0x88`, including early/fallback paths and a common clear
after its proximity/query work. On one branch it clears the compared second
object’s byte as well. The routine does not set `+0x88` to one.

The only direct byte store of one at `+0x88` is `0046681e` in
`UpdateFrontendObjectHorizontalDragState` (`004667d0`). Its verified body
implements horizontal drag: it calls `0049c080`, which polls mouse state and
returns code `0x0d` for the relevant button event; on a nonzero start gate in
incoming `EDX`, clear byte `+0xb1`, and `+0x88 == 0`, it sets `+0x88 = 1`,
clears DWORD `+0x78`, stores the mouse-X low WORD at `+0x8a`, and sets flag bit
4 in byte `+0x5`. While `+0x88` remains nonzero, it computes a mouse-X delta
against `+0x8a`, updates float `+0x6c`, and writes drag-related values at
`+0x78`. The stop path clears `+0x88` and flag bit 4. This field use is the
frontend object's drag state, not evidence of a live vehicle's activity state.

The sole direct call to `004667d0` is at `00466e56`. It lies inside a raw
routine whose entry bytes at `00466cf4` begin `PUSH EBP; MOV EBP,ESP; SUB
ESP,0xd0`. That routine takes the incoming `EAX` pointer into `ECX`, saves
incoming `EDX` in a stack local, and passes the object through `0044a660`;
the latter checks global `00559234` and object flag bit 8 at `+0x5`, an
eligibility gate also used by the documented frontend wrapper at `004675b0`.
The drag call passes the object in `EAX` and saved `EDX` in `EDX`. Nearby
accesses include the frontend entry's mode WORD `+0x80`, color/flag fields,
resource pointer `+0xa8`, tick at `+0x90`, and presentation fields `+0x6c` and
`+0x78`. Together with the mouse poll and coordinate arithmetic, this
establishes the object as a frontend/UI object rather than a race vehicle.

The incoming pointer producer for raw entry `00466cf4` is still unknown.
REA reports no containing procedure or xrefs for that entry; its resolved
caller query is unavailable because Ghidra has no function at the address.
A full-image objdump search found no direct `CALL`/`JMP` target or literal
absolute pointer to `00466cf4`, and a bounded raw-byte search found no
little-endian pointer literal `f4 6c 46 00`. An indirect callback/table
dispatch, runtime construction, or dead/unreferenced entry cannot be
distinguished from this evidence. This unresolved incoming path does not
undermine the frontend identity of the object passed from this routine to
`004667d0`; it does limit identifying which UI entry owns it.

Consequently, the `+0x88 = 1` frontend setter is excluded from evidence about
live vehicle lifecycle. The direct census identifies the ordinary vehicle
initializer's clear and the vehicle environment/query clear paths, but does
not identify a live-vehicle path that sets `+0x88` to one. A wider store,
pointer alias, or other indirect vehicle path remains outside this bounded
byte census.

## Limits and practical conclusion

The direct-byte census is reproducible and complete for byte operands at
`[base+0x88]`/`[base+0x89]` in `.code`; it is not a proof of all possible writes
through wider stores, pointer aliases, or unanalyzed/indirect paths. The
ordinary constructor state and direct activation/deactivation stores are
supported. What remains unknown is the complete set of transitive callers
that deactivate or reactivate participant vehicles, whether any such calls
are specifically part of network disconnect/rejoin or replay setup/teardown,
and which frontend entry supplies the pointer to raw routine `00466cf4`.
Establishing those points would require broader caller/dataflow recovery and,
for observable effects, controlled runtime evidence; neither is claimed here.
