# Environment-strip setup normalizer (`00478bb0`)

## Scope and result

This read-only audit resolves the direct caller, ordinary setup route, input
record shape, output tables, and observed consumer of `00478bb0`. The exact
target is the repository asset `nfs3_decomp.rep/Electronic Arts/Need For
Speed III/nfs3.exe`, SHA-256
`2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

`00478bb0` runs from the selected-track scene-loading chain. It builds a
16-slot pointer selection from an eight-entry environment-strip pointer table,
with the second half reversed when the parsed environment-strip mirror-mode
DWORD at `0055d15c` is nonzero. It reads two WORDs from each selected record;
the second WORD is used as a scalar and divided by the maximum of the 16
second-WORD values (with the maximum initialized to at least one). It writes
17 floats to `007001e8..00700228`, plus the selected pointers to
`006ff95c..006ff998`. Those values feed the projected environment-strip quad
builder `00479b90`. The observed source shape and consumer are rendering/setup
data, not participant or vehicle records. No participant/car capacity follows
from the 16/17 loop sizes.

One final numerator is not explained by the routine’s local writes: the
normalizer reads local element 16 in its 17th iteration although its first
loop populates only elements 0 through 15. This establishes a normal-path
dataflow gap in the static body; the value and its eventual visual effect are
not established.

## Artifact and evidence method

REA/Ghidra inspected the exact repository asset read-only. Its SHA-256 matched
the installed executable hash above. The binary was not run, and no persistent
Ghidra edits were made. Relevant procedures and direct evidence:

- `00478bb0`: complete assembly and pseudo-code; one resolved direct caller,
  `004dbbe0`.
- `004dbbe0`: complete assembly and pseudo-code; sole caller `004a33f0`.
- `004a33f0` (`InitializeRaceSession`): calls `004dbbe0` after earlier setup
  and checks the loading poll around each phase.
- `00478340`: selected-track environment loading/parser; its positional
  integer read at `00478762` stores the value to `0055d15c`.
- `00479b90` (`QueueProjectedStripQuadCommands`): reads the selected pointer
  and normalized scalar.
- `0047a880` / `004782e0` / `004bc160`: observed downstream rendering call
  chain for the strip pass.

The relevant instructions can also be re-read from the exact file with:

```sh
EXE='nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe'
objdump -D -Mintel --start-address=0x478bb0 --stop-address=0x478c63 "$EXE"
objdump -D -Mintel --start-address=0x4dbbe0 --stop-address=0x4dbbff "$EXE"
objdump -D -Mintel --start-address=0x4dbc19 --stop-address=0x4dbc46 "$EXE"
objdump -D -Mintel --start-address=0x479b90 --stop-address=0x479ec9 "$EXE"
```

The setup and downstream identity claims are limited to these decoded
instructions and the existing track/environment and strip-renderer findings
in `analysis/detailed-analysis-notes.md`. No runtime values or visual result
are inferred.

## Ordinary setup path and gating

`004a3db0` dispatches application states 6 and 7 to `004a3690`. That routine
calls `004a33f0` for race-session initialization. `004a33f0` passes selected
track DWORD `006fd4ac` in `EAX` to `004dbbe0` after its preceding setup stages.
The track loader’s sequence relevant here is:

1. `0041dbc0` loads the selected-track shape container, followed by abort poll
   `004a33d0`.
2. `00478340` loads the selected-track environment/setup data, followed by
   abort poll `004a33d0`.
3. `0041d960` initializes and loads selected-track resource groups, followed by
   an abort poll.
4. `004bc870` initializes the scene preparation path, followed by an abort
   poll at `004dbc28`.
5. If that poll is zero, `004dbbe0` reaches `00478bb0` at `004dbc3b`; a further
   abort poll follows at `004dbc40`.

This is the ordinary selected-track setup route. The normalizer has no
participant-role, vehicle-category, or roster-count branch. Its call is
skipped when an earlier abort poll returns nonzero. The post-normalizer poll
does not gate entry into the normalizer; it reports/handles the later state in
the enclosing loader.

## Input and normalization operation

The environment parser stores a positional signed integer in
`g_nEnvironmentStripMirrorMode` (`0055d15c`) at `00478762`. The function
does not normalize that integer to a documented boolean range; its only use in
`00478bb0` is a zero/nonzero branch.

For each `ECX = 0..15`, the normalizer selects a source index as follows:

- If `0055d15c == 0`, source index is `ECX % 8`, producing `0..7, 0..7`.
- If `0055d15c != 0`, slots `0..7` use source `0..7`, while slots `8..15`
  use `15 - ECX`, producing source `7..0`.

The selected source pointer is read from
`0055d1d0 + 4 * source_index` and copied to output pointer slot
`006ff95c + 4 * ECX` (`00478be7..00478bee`). `00478320`, called once per
slot, reads a pair of zero-extended WORDs from that pointed record:

- `[record + 0]` is copied to the scratch DWORD at `EBP-8`.
- `[record + 2]` is copied to the local DWORD for slot `ECX`.

The scratch first WORD is overwritten on the next iteration and is not read by
the ratio loop. The second WORD values are compared as unsigned zero-extended
integers; `EDI` starts at 1 and is raised only when a slot value is greater.
Thus the divisor is `max(1, values[0..15])` for the observed 16 populated
slots.

The second pass executes for `ECX = 0..16` inclusive. Each iteration loads
`[EBP - 0x4c + 4 * ECX]`, converts it to x87 integer form, divides by `EDI`,
and stores the resulting binary32 value at
`007001e4 + 4 * (ECX + 1)`. It therefore writes slots 1 through 17, at
`007001e8..00700228`.

The first pass writes local source-value slots 0..15. The 17th ratio iteration
reads local slot 16 at `EBP-0xc`, for which there is no preceding store in
`00478bb0` or in the two-WORD helper `00478320`; `004a33d0` is a no-argument
abort-poll helper and does not receive that local pointer. The value used for
the final output slot is therefore not established by this routine. The
instruction sequence proves the read/write, not a particular runtime value or
whether downstream code consumes that final slot.

The PE image bytes at `0055d1d0..0055d1ef` are zero in the original file image.
The normalizer’s direct references to this address are indexed reads, and the
bounded direct disassembly found no direct store to that table. This does not
show the table is zero when the setup path runs: a write through an alias,
resource-loading mechanism, or another initialization route may supply the
runtime pointers. The table’s population path and the exact `.hrz` source
record labels remain unresolved. Accordingly, the two-WORD memory shape is
assembly-confirmed while its field semantics are not.

## Observed consumer and capacity relevance

`00479b90` is reached from `0047a880`, which calls it when the projected-strip
pass gate `0055d160` is nonzero. In its strip-quad loop:

- It reads `006ff95c + 4 * index` and stores the selected pointer into emitted
  command `+0x18` at `00479e79..00479e80`.
- It reads a normalized scalar from `007001e8 + 4 * index` at `00479c64` and
  passes it to helper `004e0050` during projected-strip construction.

The existing renderer audit documents `00479b90` as `QueueProjectedStripQuadCommands`:
it builds projected strip quad commands from scene geometry and attaches a
selected resource pointer. Its outer call path is `004bc160` → `004782e0` →
`0047a880` → `00479b90`; `004bc160` is a scene/render routine. This makes the
normalizer relevant to environment-strip setup/rendering. It is not a per-car
parameter normalizer:
the body contains no participant count `006fd510`, vehicle pointer table
`005efac8`, car-model ordinal, or role/category branch. Its fixed 8/16/17
iteration domains describe this rendering data only and impose no limit on
race participants or registered car models.

## Remaining limits

- The runtime producer for pointer entries at `0055d1d0` was not recovered;
  the image’s zero bytes are not runtime-state evidence.
- The two WORD meanings in the pointed source records are unknown; only the
  second WORD’s use as a normalization numerator is proven.
- The meaning/domain of parsed mirror-mode values beyond the observed
  zero/nonzero behavior remains unknown.
- The 17th numerator is read from local slot 16 without a local store. Its
  runtime value, the intended purpose of the seventeenth output, and whether
  the downstream renderer reads that output remain unverified.
- The loading wrapper’s abort checks establish a local route, not that every
  gameplay start completes this stage or that all required assets are
  present.
- No conclusion about vehicle/participant capacity, visual appearance, or
  runtime failure follows from this static normalizer audit.
