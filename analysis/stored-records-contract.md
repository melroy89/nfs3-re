# Stored-record database evidence boundary

## Existing local schema and ownership findings

LoadOrInitializeRecordsDatabase0044f510 checks first DWORD0x10 after
loading, with no local loaded-length check in its saved assembly analysis.
Fallback allocation/zero size is0x4197c; summary starts+4 and selected
record block+16e0. Header identity alone does not prove complete schema
or allocation extent for a loaded file.

InsertOrReplaceStoredRecordAndRefreshRanks0044fa10 copies a0x31c-byte
stack-by-value record. Its count==10 branch replaces sorted index9; all
other counts take append-and-increment. Therefore its equality test is not
a universal capacity admission check. Qualification, loaded count and source
string bounds remain caller questions; no reachable corruption is claimed.

## Save-result handling verified in assembly

SaveRecordsDatabaseAndReleaseBuffer0044f5f0 formats records.dat under the
configured path into256 stack bytes, optionally changes permissions, then
passes EBX0x4197c to SaveResourceFileFromMemory at0044f64e. The next
instruction replaces EAX with the buffer pointer; no local save-result test
precedes free0044f65a and pointer-clear store0044f65f. Existing Ghidra
comments already capture this behavior; no duplicate annotation was added.

## Astra continuation

Sole decoded insertion caller004511d6 is inside00450fe0, now named UpdateStoredRecordsFromVehicleResult after full assembly review.
Start there for record qualification, stack snapshot/string bounds, lap
summary/count admission and result-mask consumers. Full schema, comparator
policy, loaded lengths, path bounds, save-failure recovery and lifetime
remain unresolved. Do not equate reaching save with successful persistence.
No record file was changed or runtime scenario performed.


## Vehicle-result updater named

00450fe0 constructs a qualified0x31c-byte record, calls insertion004511d6,
then independently scans signed lap count over vehicle+240 for the minimum
nonzero signed timing and conditionally updates the selected track summary.
Return bits distinguish the local insertion comparison (2/4) and summary
update (1); visible event names remain unassigned. It performs no disk save.
Participant/model/lap admission and NUL-copy bounds remain open. The first
stack record DWORD lacks an explicit local initialization before copying;
rank refresh later writes that field. No uninitialized-use consequence is
asserted without consumer/order proof. Ghidra name/comment saved.


## Result-mask consumer domain

Both decoded00450fe0 calls are in UpdateSelectedTrackLapResultProgressFlags
004512f0. Mask1/4/2 maps to kind0/2/1, primary slot0 and optional session1
second slot1. Setter0044e7f0 stores1 at00664440+8*kind+4*slot, leaving
ECX unchanged; these six calls therefore address only00664440..00664454
(six DWORD cells). Primary lookup key006fd4f4 is not the destination slot.
Exact visible labels, other producers and reset/lifetime remain open; no
UI meaning was guessed. Stale caller comment requesting helper review was
updated after full parent assembly review. Ghidra saved.


## Result notification audio route

The flags are read by0044ea60, which checks shared voice007dd82c via
004c99f0 before selecting a notification. Named the small wrappers
CheckResultAnnouncementVoiceExpired004c99f0 and
StartIndexedResultAnnouncementSound004c9990 after full assembly review.
The start wrapper selects one of two banks by signed selector<=4, forms
sample(slot<<4)+selector, starts volume-scaled audio and retains its handle
without a success check. Exact spoken text, broader concurrent/reentrant flag-consumption
ownership and failure/retry policy remain open. Local attempt-then-clear
ordering is established in the consumer section below. ClearResultProgressFlagStorage
0044e7d0 clears0x68 bytes from00664440, including the six record-result cells.
This establishes a notification route, not successful disk persistence.


## Notification flag consumer named

Named0044ea60 ConsumePendingResultAnnouncementFlags after full assembly
and five-entry jump-table review. Mode0 priority is paired kind1+0, paired
kind2+0, kind2, kind1, kind0, selecting numeric sounds3/4/1/0/2. Other
modes retain numeric selector mapping in Ghidra. Each selected path calls
audio then clears its flag(s) without testing playback success and returns.
Thus an attempted notification consumes flags locally; no successful
playback or disk-save guarantee follows.

Requested slot count1/2 is held in ECX across the voice-status helper.
Subsequent full assembly review resolved normal-return preservation, as below. Other callback/reentry/ownership
and spoken-identity questions remain Astra work; no runtime test performed.


## Voice-status gate preserves slot count

004e8fd0 calls lock00500e20, validator004ffc9c and unlock00500e7c;
each explicitly saves/restores ECX on every reviewed normal-return path.
Disabled audio bypasses those calls without changing ECX. Thus the
notification consumer retains its exact configured slot bound1/2 after
that gate. Validator rejects negative handle, low-five-bit index>=16,
inactive voice or generation mismatch. Nonlocal abort and concurrent state
mutation remain outside this local proof. Updated Ghidra consumer comment.


## Qualification does not bound record count

Immediate caller00451075 tests CheckStoredTimeQualifiesForRecordList
0044f960 before insertion004511d6. Full qualifier assembly returns1
for any signed count<10, including negative. For count>=10 it rebuilds
the map and queries count-1; NULL lookup returns1, otherwise a smaller
signed candidate time returns1. Equal time is rejected on that branch.
Thus qualification supplies no count-domain invariant0..10 to insertion.
Actual count initialization/load/producers and map capacity still require
Astra analysis. No malformed records.dat was loaded. Ghidra insertion
comment refined and saved.


## Installed database extents

Fresh read-only inventory found active FEDATA/STATS/records.dat and backup
fedata_org/stats/RECORDS.DAT. Both are268668 bytes (0x4197c), header16.
Selector0044f670 assembly uses+16e0+category*15634+track*1f1c; each
block1f1c equals4+10*31c, and three groups of11 exactly tile the remaining
file span. All33 candidate blocks per file fit; active signed counts0..2,
backup0..8, all within0..10. This closes the recorded installed-file extent
and count inventory, not actual track/category admission, complete loader
reads, later mutation or custom-file validation. Occupied record-string
termination is independently established below; source-copy bounds remain open. Hashes and
all offsets/counts retained in[JSON inventory](installed-records-database-extents.json).


## Installed occupied-record strings

Read-only verification of the same hashed active and backup files checked all
four assembly-derived string ranges in each occupied 0x31c-byte record:
offsets/capacities 4/11, 15/256, 271/256 and 527/257. All ranges contain a
NUL: 3 occupied active records and 127 backup records. Maximum bytes before
NUL are respectively 6/21/11/9 and 9/21/12/13. File hashes and independently
recomputed counts/maxima match the [string inventory](installed-records-string-bounds.json).

This closes occupied-string termination for these exact installed files. It
does not prove bounds of the updater's source copies, unused records, custom
files, later mutation, runtime loading or complete schema validity.
