# Track-width lookup evidence boundary

## Saved installed-resource finding

The saved Ghidra comment for ConvertTrackOffsetToLaneIndex0040e2b0
retains a prior read-only inventory of nine installed COLL/version11 files:
12706 type15 segment records,36 bytes each, width bytes+17/+1b in0..30.
TRK006 contains83 zero-width fields. This pass read back that saved evidence;
it did not rerun the filesystem inventory or verify current asset hashes.

The helper's reviewed index formula2*width therefore gives0..60 for those
recorded files. Initializer0040e410 establishes cells0..79, including zero
at cell0. Output lane clamp0..13 follows the lookup and supplies no guard
for other width inputs. The saved finding resolves only that installed-file
input domain, not the complete table allocation or later record state.

## Remaining Astra work

- Prove active segment/count validity and lifetime across load/reload.
- Establish complete reads, block-relative offset/declared-size admission
  and allocator extents; current header/payload wrappers lack local proofs.
- Trace aliased record mutation and custom/transferred resource admission.
- Preserve x87 rounding, exceptional values and coordinate conventions.

Registry/cache/group/participant capacities belong to separate contracts.
The car/track capacity row remains Partial; no expansion or binary change
is authorized by these observations.
