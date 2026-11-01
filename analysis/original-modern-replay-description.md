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
`ff5abeff`, ECX18 and stack value3. Its exact localized wording and units are
not established here. Modern jumps directly to row iteration at `0044716e`
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

**Done, verified static:** complete callback and binding,90 changed-byte
localization, removed heading, initial row offsets, retained loop and narrowed
coordinate reads. **Unresolved:** record population and string validity,
actual component/resource selection, coordinate units, text-helper effects,
full callback lifecycle and rendered acceptance. Callback+54h is an observed
registration field; no generic ABI is inferred solely from that offset.

This is a menu-layout change. It is not evidence of replay-file format,
trajectory, physics or multiplayer compatibility changes. Those questions
remain governed by their separate evidence requirements.
