# Pose and ghost analysis status

This reconciles existing saved analysis, rather than claiming a fresh runtime
validation. Source: [pose and replay history](detailed-analysis-notes.md).

Established storage: PackedVehiclePoseSample is18 bytes. Initializer and
ghost-load clear extents establish intended tables of14400 entries, each
259200 bytes. Selected position encoding, visual-slot projection, optional
replay pose I/O, ghost save/load and setup restoration helpers have reviewed
names/comments. These dimensions do not validate a loaded count or index.

Remaining original questions:

- Recording index/count semantics, loader count/size admission, file round
  trips and nontransactional failure-state ownership.
- Complete mode lifecycle, setup restoration and replay event/control meaning.
- Packed pose register/stack ABI, interpolation endpoints and numerical
  equivalence; coordinate and quaternion asset conventions.
- Timed effect definition count/elapsed-tick admission, unnormalized blends,
  completion versus invalid records, viewport fallback and multiplayer
  completion/restoration ownership.

[Camera findings](ccm-camera-contract.md) resolve bounded selector and geometry
producer questions, not these complete pose contracts. Replay input RLE has
its separate Partial SCRATCHPAD item and retained token-bound evidence;
intact RLE round trips do not establish ghost-file count or mode admission.

For Astra: start at saved loader/writer/recording comments in Ghidra, trace
count/index producers and failure paths, then select a precise isolated or
read-only runtime test. A successful ordinary replay alone cannot close
malformed input, full lifecycle or exceptional interpolation behavior.


## Saved type readback

Live Ghidra readback confirms alignment1 and18-byte size:

| Offset | Storage | Existing field |
| --- | --- | --- |
|0|ushort|wMetadata|
|2|short|nTrackSegmentIndex|
|4|short[3]|aSegmentRelativePosition|
|10|short[4]|aOrientationQuaternion|

The existing PackedVehiclePoseSample[14400] type reports259200 bytes.
This verifies saved type dimensions, not a runtime loaded-count check or
full quaternion interpretation. The broader item remains Partial.


## Local ghost loader admission

LoadGhostRecordingResource00477b50 compares byte count unsigned against
0x41574 at00477b82/87; zero through that inclusive ceiling pass this local
gate. It clears the fixed destination span, then calls reader004f22e0 at
00477ba3 and overwrites its result without testing. Validator00478100 at
00477bad is accepted for any nonzero EAX; zero returns0, success publishes
loaded flag1 and returns1. Failure does not clear the previous loaded flag.
Existing Ghidra comment refined and saved after full assembly review.

This establishes local behavior only. Minimum valid file schema, complete
read, embedded sample count, downstream index and lifecycle ownership remain
Astra work; the broad Partial row is unchanged.


## Immediate validator boundary

ResolvePreparedRaceCarModelIndices00478100 checks magic0x20f0, then
compares signed zero-based ECX against buffer DWORD+19d0 at0047811a/20.
A nonpositive count skips the entire model-resolution loop and returns1
if magic matches. Positive counts drive0x6c-stride identifier/model accesses.
No file-length argument or pose-sample count check appears in this helper.
Its existing name describes model resolution; calling it does not establish
a complete ghost-file schema check. Parent verified full assembly and saved
the signed-count refinement in Ghidra.

This closes the local question of whether the immediate validator supplies
a positive-count gate: it does not. It does not establish malformed-file
reachability, downstream safety or a valid loaded pose-count invariant. Those
remain open for Astra. No artificial file was loaded or game state changed.


## Writer extent and direct index producer

SaveGhostRecordingIfAllowed004777d0 reads0067b140 and computes
0x20f4+18*value with ordinary32-bit arithmetic; it adds no extra sample.
The sole decoded direct scalar writer00477d81 publishes the current index
after recording at that index in00477c20. For nonnegative tick007d3684,
this index is floor(tick/8). Therefore an unchanged saved value excludes
the just-written index from the emitted sample span. This is a local
extent fact, not proof of an off-by-one defect or the intended end convention.

Pointer helper004779e0 rejects signed index>=14400, but has no negative
index check. Recorder also requests index-1 for quaternion continuity;
negative-index meaning and initial-tick reachability remain Astra questions.
Header0x20f4 plus14400*18 equals loader ceiling0x41574 exactly.
Full producer invariants, initialization timing, skipped updates, sample
interpolation semantics and actual file round trips remain open. Ghidra
writer comment saved after direct xref and full assembly review.


## Conditional playback endpoint pointers

GetPlaybackPoseSamplePointer00477a10 independently substitutes N-2
whenever signed requested index>=N-1. InterpolatePlaybackVehiclePose
00477d90 calls it for i and i+1 at00477dc0/ca. With stable N in2..14400,
nonnegative indices and no increment overflow, returned indices lie0..N-2.
At i>=N-2 both pointers equal sample N-2; stored sample N-1 is never
selected under these assumptions. This is pointer-selection evidence only,
not proof that interpolator output is identical or endpoint intent is wrong.

The accessor has no local lower-index or N>=2 guard. Actual count/tick
admission, concurrent changes, quaternion interpolation equivalence and
file round trips remain open. Ghidra accessor comment saved and verified.


## Ledger review against saved Ghidra annotations

Live plate-comment readback of00477a10 confirms the conditional endpoint
proof and explicitly retains count/index admission and interpolation intent.
The current Partial ledger row matches this boundary; no status upgrade is
supported. Race dispatcher004ceae0 likewise retains shared exit-state and
alternate finalization ordering qualifications, matching the separate race
completion report. This review does not add runtime evidence.
