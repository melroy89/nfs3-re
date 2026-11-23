# Original versus Modern: replay description layout

## Evidence and scope

The [static audit](scripts/audit_replay_description_layout.py) compares complete
paired callback `004470e0..0044718f` (175 bytes) and its registration in
[the retained manifest](evidence/audits/replay-description-layout.json).
Both original and final register that address at component+54h after looking
up literal `DESCRIPTION_BOX` (`0044748f..004474a6`); adjacent component token
is `replays`. Baseline EXE hashes are asserted before inspection. No game,
menu, renderer, instruction probe or saved database write occurred.

All90 changed bytes in outside-function interval `00446fed..004471a0` lie
in this callback. The old/new body lengths happen to match because Modern
leaves NOPs before the retained row loop. Other code and the trailing table
in the larger interval are not newly interpreted as changed behaviour.

The retained release archives date the rewrite to 1.4.0. The full 175-byte
callback hashes match the original from 1.1.0 through 1.3.1 and match final
1.6.1 from 1.4.0 through 1.6.0. The 23-byte registration span
`0044748f..004474a6` matches in every inspected build. Thus 1.4.0 changes the
registered callback body while preserving its binding. Rendered output
remains untested.

At the same boundary, the packaged `fedata/menus/loadsave.mnu` moves
the `DESCRIPTION_BOX` rectangle from `(400, 176)` to `(395, 205)`
and keeps width 180 and height 115. The adjacent `replays` list moves
from `(185, 176)` to `(183, 158)`, retaining its codelink. The callback's
five-unit reduction in the first detail row offset is relative to the
description box. If the authored Y reaches the callback unchanged, the
combined first-row Y is 201 in 1.3.1 and 225 in 1.4.0. Actual anchoring,
scaling and pixel placement remain unverified.

The packaged positions follow the same history as the callback. All four
retained packages from 1.1.0 through 1.3.1 use the earlier coordinates. All
seven from 1.4.0 through 1.6.1 use the later coordinates. The description
box is 180×115 throughout. The check reads the blocks named by their exact
`codelink` values in each package's own `fedata/menus/loadsave.mnu`. It
establishes continuity of these fields, while other menu properties may vary.

The author-hosted `fedata/MENUS/LOADSAVE.MNU` matches the uppercase
local backup `fedata_org/menus/LOADSAVE.MNU` byte for byte (SHA-256
`6308194657d28f1205fca6fafb598c248fb6736e6bf4f827da778f9ce189b968`).
Both have the same two positions and box dimensions as pre-1.4.0 Modern.
The lowercase backup `fedata_org/menus/loadsave.mnu` instead matches the
installed `FEDATA/MENUS/loadsave.mnu` (SHA-256
`ac14717b7a8a4bfe2c3cbf5267212ff2d164edf1da6ad75a315e576bf00cf329`)
and uses the later positions. The two local backup files coexist under
case-distinct names. Their identities establish the comparison inputs.
The runtime path and case resolution remain unobserved.

## Heading removed, details begin earlier

| Property | Original | Final Modern |
|---|---|---|
| Local stack allocation |260 bytes |4 bytes |
| Separate heading | Lookup language ID480, format `%s...`, call text helper `00452190` | Removed |
| First detail row X | Context signed X+20 | Same |
| First detail row Y | Context signed Y+25 | Context signed Y+20 |
| Subsequent row spacing |20 coordinate units | Same |
| Row text source | `00558d0c + i*120`, i0..9 | Same |
| Empty record | Skip drawing, still advance row | Same |

The original heading is supplied with X+10 and the original Y, colour bits
`ff5abeff`, ECX18 and stack value3. At `004470f9` it calls `004d1850` with
EAX=`0x1e0`. For that ID the lookup reads the little-endian DWORD at language
base plus `480 * 4` and returns base plus the stored offset. In local backup
`fedata_org/text/TEXT.ENG` (SHA-256
`fb27fe75c9f8f6ee3d65058db0b2732ed14e1dd7aef9f1c5e5481d4078a74bcc`),
that entry points to `Loading`. The installed `FEDATA/TEXT/text.eng` also
contains `Loading` at index 480. With either English table, the callback's
format yields `Loading...`. Actual loaded table and font placement remain
unverified. Modern jumps directly to row iteration at `0044716e`
and NOP-fills `00447100..00447144` (68 bytes). Complete row-loop/tail
`00447144..0044718f` (75 bytes) is byte-identical, including draw colour
`ff649dfd`, ECX18, stack value3, increment, ten-record bound and epilogue.
The first row's five-unit shift follows the shown arithmetic under normal
helper register preservation; it is not a measured pixel displacement.

## Same signed coordinates, narrower reads

Original loads DWORDs at context+4/+6 then arithmetic-shifts each right16,
extracting signed WORD values at +6/+8. Modern loads those WORDs directly
with MOVSX. Under ordinary readable little-endian context storage, the signed
coordinate values are equal; the original performs wider reads, including an
unaligned DWORD at+6. A maintained C translation should distinguish value
reproduction from the original access footprint and use explicit packed-byte
access when alignment/aliasing is not established. It should also preserve
32-bit wrapping additions rather than assume arbitrary signed C arithmetic
cannot overflow.

## Status and follow-up

The menu selection path supplies the detail rows through a retained producer.
The original and final match across `00447190..0044734e`, including the
four-entry dispatch table. The handler clears the 1,200-byte row area at
`00558d0c`, reads the selected list entry, and builds a path using prefix
`007a2f34`. Dispatch case 0 appends `rp3` on the selected-file route and
calls `00446060`. That routine formats a string into the first row via
the destination argument at `00446151`. The other menu modes share the
row area. Complete row population and actual selected-file inputs remain
outside this trace.

For the selected `.rp3` route, the complete writer and jump table
`00446050..004461c4` are byte-identical in the original and final. After
its file and metadata checks succeed, it writes four consecutive rows.
Row 0 looks up ID `102 + header[0x196c]`, which selects Hometown through
Empire City for accepted indices 0–8 in the inspected English backup.
Row 1 formats the DWORD at header `+0x1974` with ID 5 (`Laps`). Row 2
maps the DWORD at `+0x1878` to IDs 213, 214, 215 or 220 (`Single Race`,
`Tournament`, `Knockout`, `Hot Pursuit`). Row 3 displays the car model
name. At `00446123..00446143` the writer reads the saved index at header
`+0x19b4`, uses its `0x6c` record stride and reads the model ID at header
`+0x1a00 + index * 0x6c`. The identical name helper at `00439250..00439287`
returns the model record's `+0x10` name on its ordinary registry path.
The six other row slots are untouched by this writer. The loaded registry
and file determine the actual names. Replay playback compatibility remains open.

All 11 retained Modern packages from 1.1.0 through 1.6.1 match in the
372-byte metadata writer, the 446-byte selection and dispatch span
`00447190..0044734e`, and the 55-byte car-name helper. The check reads these
virtual-address spans from each archive's own `nfs3.exe`. This confirms
that the 1.4.0 description layout change leaves these three routines
unchanged. Other replay readers, validation callees and runtime inputs
remain outside this comparison.

**Done, verified static:** complete callback and binding,90 changed-byte
localization, removed heading, initial row offsets, retained loop and narrowed
coordinate reads and the selected replay row producer. **Unresolved:**
other menu-mode producers and runtime string contents,
actual component/resource selection, coordinate units, text-helper effects,
full callback lifecycle and rendered acceptance. Callback+54h is an observed
registration field; no generic ABI is inferred solely from that offset.

This is a menu-layout change. It is not evidence of replay-file format,
trajectory, physics or multiplayer compatibility changes. Those questions
remain governed by their separate evidence requirements.
