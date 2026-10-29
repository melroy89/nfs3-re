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
objdump -D -Mintel --start-address=0x41daa0 --stop-address=0x41dae0 "$EXE"
objdump -D -Mintel --start-address=0x41d960 --stop-address=0x41da38 "$EXE"
objdump -D -Mintel --start-address=0x41dc60 --stop-address=0x41dcc0 "$EXE"
objdump -D -Mintel --start-address=0x478b70 --stop-address=0x478ba4 "$EXE"
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
The normal loading path does construct this table at runtime. `0041dae0`
allocates a resource-group buffer through `0041daa0`, which stores the
allocator result in `005dd858`. `0041d960` calls `0041dae0` before
`0041dc60`; the latter passes `[005dd858]` to `00478b70`. That helper is
the resolved writer of the eight table entries: for indices
`i=0..7`, it writes `[0055d1d0 + 4*i] = [005dd858] + 44*i`
(`00478b81..00478b96`; the stride is `(4*i-i)*4-i`, then `*4`). Thus the
eight pointers address byte offsets 0, 44, …, 308 in the allocated
resource-group buffer. The image's zero bytes describe its initial data, not
the post-loader table.

The payload producer is also traced. When resource-group source `005dd850` is nonzero, `0041dc60` calls `BuildIndexedShapeTexturesWithLoadingProgress` (`0041db10`) with destination `[005dd858]` before publishing the eight pointers. The builder advances its destination by44bytes after each successfully resolved shape (`0041db9d`). It selects `004d4080` when `007a3a58 & 2` is clear and `004d41a0` when that bit is set.

In `004d4080`, source-header WORDs at+4/+6 are copied to descriptor WORDs at+0/+2 (`004d409e..004d40af`), before texture creation and UV-field setup. Thus the normalizer's two WORDs are the texture descriptor's two stored extents, rather than participant parameters. The first extent is ignored by the normalizer; the second is divided by the maximum second extent across the16selected descriptors.

The alternate `004d41a0` initially copies the same source extents, then calls `004d4120` and replaces both descriptor WORDs with the same selected square side at `004d4230..004d4233`. `004d4120` takes the smaller signed input extent, returns256 for values at least256, otherwise the largest threshold from128/64/32/16/8/4/2 not exceeding it, and returns1 below2. This is a branch-specific texture-size policy, not a universal maximum for every renderer or all game textures. Therefore the normalizer can use the square output extent rather than the original second source extent on this branch.

This resolves the descriptor-content producer and the normalization input's structural meaning. It does not establish which branch ran in a particular race, the full source-asset schema, successful texture upload, renderer limits or the visible effect of the normalized ratio.

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

- The normal runtime construction of the eight pointer entries at
  `0055d1d0` is recovered as eight 44-byte-spaced addresses into the buffer
  held at `005dd858`. The descriptor extent producer is traced through `0041db10` and its two texture-construction branches; actual runtime contents remain unobserved.
- The two WORDs are stored texture extents; the selected backend branch and actual loaded values were not sampled, and successful upload/visual behavior remain unverified.
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
