# Track CCM camera record contract

`LoadTrackCCMRecords`0041e180 optionally loads a track-relative CCM file,
reads signed count at+4, treats+8 as28-byte records, computes each record's
segment key+18, then bubble-sorts by that key. Selector00423d90 and view
updater004251f0 consume the resulting records. No local file-size comparison
precedes the header or record accesses.

Read-only inventory of all eight loose installed GAMEDATA/TRACKS CCM files
finds counts4..25 and exact sizes8+28*count, with no trailing bytes. Each
header's first DWORD is1. [Inventory and hashes](evidence/inventories/installed-ccm-extents.json)
preserve the file evidence. TRK002 has no loose CCM in this inventory; this
does not establish archive fallback or absence of a camera path.

Installed loose-file extent is closed. Complete runtime reads, replacement
or packed assets, malformed/negative counts, segment-query correctness,
selector seams/reverse direction and visible camera behavior remain open.
Ghidra loader comment records these boundaries. No executable/assets changed.

## Empty-count selector fallback

Selector00423d90 initializes result-1 and uses a signed count bound. Count<=0
skips every CCM record read and returns-1. Scene/vehicle access precedes this
check, so it does not guard an invalid scene. Caller004251f0 tests-1 at
00425208, invokes004238b0 and mode8 dispatch00426450, without CCM pose update.
This closes the local empty-count/fallback contract; valid-track occurrence,
reverse/seam behavior and full scene lifetime remain separate. Saved selector
comment in Ghidra.

## Cyclic distance and tie order

With N>0 and normalized current/key indices0..N-1, selector00423d90 computes
min(abs(current-key),N-abs(current-key)); only distances<30 compete. It scans
all records, without an early exit from sorted order. Stable ascending key
sort plus strict improvement means equal-distance ties keep the first record,
generally the lower numeric key; duplicate keys retain file order. At odd
N=9/current0, keys4 and5 tie and4 wins. Only that winner undergoes orientation
eligibility; rejection returns-1 without retrying another tied candidate.

No direct reverse-flag branch is present in this selector/preprocessing path.
It uses supplied vehicle segment+1c and computed camera keys. Separate reverse
progress/offset helpers do not prove these coordinate conventions. Invalid
indices can produce negative N-distance and are not sanitized here. The reviewed index producers are resolved below; actual reverse-camera
behavior and remaining writers remain open.

## Stored transition increment

Constructor00422cf0 case19 initializes scene+114 to binary32
0x3c23d70a (0.01), with+110/+118/+11c zero. Eligible
BeginViewportSceneModeTransition00422610 leaves+114 unchanged and initializes
transition progress/old/target fields. Updater004262a0 adds+114 to+110 once
per eligible callback, testing signed raw progress>0x3f800000 before adding.
This establishes the ordinary increment, not a duration in seconds.
Finish caller00426680 writes raw1/6 to the reloaded active scene+114;
direct fallback to mode17 gives that field different semantics. Actual
finish branch selection and callback cadence remain open.

## Local viewport scale controls

Named0048ea20 `AdjustViewportScaleSettingAndExtent` and0048eb60
`AdjustScaleSettingsForLocalViewports`. Held history bit15 selects0
(add binary32~0.1, upper bound4); bit16 selects1 (subtract~0.1,
lower bound1). The wrapper updates view0 and also view1 in session1.
The ordinary finite positive[1,4] domain is preserved; signed raw-bit
comparisons are not general exceptional-value normalization.

The setting address is006fbc60+0x348*(view+(sessionMode==1))
+0x1a4*policeFlag. Extent00792878[view] becomes half the smaller
viewport-bound span times scale. Exact scale1 also resets both
centres to the bounds midpoints. Constants and complete assembly
were checked, and Ghidra names/comments saved. This closes local
control mapping/arithmetic; user-facing feature identity, active
setting provenance and later rendering effects remain unresolved.

## Finish caller reload and conditional field aliases

00426680 requests mode17 when the attached vehicle has category bit1
and status3. Modes16/17 additionally require their+11c guard zero;
other modes use guard zero automatically and are not excluded.
After Begin returns,004266e9 reloads the active base pointer.
It writes+11c=1, disposes any existing+118 indexed effect, writes
raw+114=1 (normal) or6 (reverse), and replaces+118 with allocator
result. If retained mode19 is actually eligible, these replace its
target17 with1 and its old-mode field with an effect index; raw
1/6 are subnormal binary32 increments. These are conditional
alias consequences, not a runtime stall or proven reachable path.
Request17 transition eligibility from initialized scene tables is
the next static check. Parent corrected worker wording that had
incorrectly limited caller admission to modes16/17. Ghidra updated.

## Shared geometry indices versus reverse progress

Loader0041e180 computes CCM key+18 through world-XZ nearest-track
queries. Placement004a0aa0 initializes a query at vehicle+c using
0041e940; query index+10 is therefore vehicle+1c. Both use active
track geometry records005dd948. Separate0042ce10 derives progress
vehicle+8 as lap*N plus segment (normal) or N-segment (reverse),
without altering vehicle+1c. This resolves the reviewed producer
coordinate convention; it does not prove every later writer,
identical reverse asset ordering or visible camera correctness.
The orientation gate remains independent of cyclic distance.
Ghidra selector comment reconciled; static evidence only.

## Initialized request17 eligibility

Constructor00422cf0, now `InitializeRaceViewportSceneRecords`, clears
scene eligibility bytes+58..70. Its switch sets request17 byte+69
only for modes1..7 and11..13. Parent checked all ten stores and
switch-table bytes. Modes16/17 therefore take direct mode17
fallback under initialized eligibility; other admitted modes may
retain if scene/vehicle identity gates pass. This closes the
constructor-side gate, not runtime mutation or actual finish-path
occurrence. Conditional field aliases above remain relevant only
when retained mode19 is actually selected.

## Four camera setting sources

File-backed menu rows00556c1c/30/44/58 name camera1..4 and
point to indices006fbba8/ac/b0/b4. Mapper00472300 reads signed
WORDs0055629e+2*index. Verified indices0..6 map[0,1,4,3,2,5,6];
default indices[3,1,0,0] therefore produce[3,1,0,0]. Parent raw
byte review corrected a worker's one-element table shift. The
four values feed successor construction00423a60. This resolves
menu association/default mapping; accepted menu extent and later
mutation remain open for Astra. Ghidra mapper comment saved.
