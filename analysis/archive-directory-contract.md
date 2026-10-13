# Archive directory extent contract

## Installed VIV directory and member extents

Inventoried all114 .viv files under GAMEDATA and gamedata_org, counting
active/original trees separately. All are BIGF, declared file sizes
match actual bytes, directory headers and NUL-terminated names fit
the declared directory, and all1169 member payload spans are within
the file and begin at/after directory end. The extra48 bytes read by
OpenArchiveDirectory0043b830 also fit in every inspected file.

Assembly confirms allocation and read length both use directory_end
+0x30, with wrapping32-bit arithmetic, and seek/read returns are
ignored. Zero-fill before read does not prove complete I/O. This
closes installed artifact extents only; custom/malformed archives,
short reads, parser traversal and ownership remain open.
[Inventory](evidence/inventories/installed-viv-directory-extents.json) records every archive
hash/header and member offset/length. Ghidra opener comment saved.
No runtime or binary modification.

## Member lookup and basename termination

FindArchiveMemberByName004679f0 uses unsigned header count+8,
starts records+10, returns first ASCII-case-insensitive match, and
scans NUL names on misses. It does not consult directory end+0xc or
buffer length. EBX/ECX are offset/length output pointers; miss zeros
both. A zero-length member cannot be distinguished from miss by
length alone. Installed inventory names are at most12 bytes and have
no ASCII-casefold duplicates within any of114 archives.

FindArchiveMemberByBasename0043b9d0 finds the last backslash, then
copies29 bytes through004e0e30 into a32-byte local area without an
explicit terminator. The copy helper pads remaining bytes only; an
input basename>=29 bytes need not terminate before lookup. Installed
member-name lengths do not prove requested caller basename lengths.
Long-query reachability, short reads and arbitrary header/count/name
validity remain open. Ghidra comments refined and saved.

## Direct basename queries

Seven decoded callsites occur in registry discovery, palette reading,
car transfer, vehicle sound and identification speech. Fixed vehicle
sound queries scar.bnk/car.bnk/ocard.bnk/ocardd.bnk are at most10
characters; palette uses car.fce (7), transfer constructs final
carp.txt (8). Identification uses IPNCspch.bnk (12) or IP%sspch.bnk
with twelve file-backed two-character codes at00412920: RD,GR,BL,YL,
WT,BK,OR,PU,SV,BR,DK,LT. A valid index therefore also yields12.
These fit the29-byte copy with zero-padding.

Registry query fedata.%s still depends on language-code provenance;
identification index bounds, full path construction and non-direct
callers remain open. This is a conditional caller-domain refinement,
not proof that every possible lookup request terminates safely.
Ghidra basename-helper comment saved; binary unchanged.

## Validated registry language query bound

Registry00439e71 passes language index007a3a50 to004782b0. Sole
decoded direct writer004a6eb9 stores0..5 after a six-string language
match, or0 after fallback. RunGameApplication invokes validation
004a6e68 before subsystem initialization004b5c00. Getter table0055d12c
contains seven verified NUL codes eng/ger/fre/spa/ita/swe/jap at
0053b21c; ordinary selected first six are each3 characters.

Consequently validated registry basename fedata.<code> is10 characters
and fits29-byte copying with termination. This closes that ordinary
query-bound question. Getter itself has no index check; arbitrary
inputs, aliased mutation, full path assembly and identification speech
index provenance remain open. Ghidra getter comment saved.

## Identification speech code index producer

Named ClassifyRgbForRacerIdentificationSpeech00431280 and
ComputeRgbSquaredDistanceLow3200431250. Classifier selects among359
fixed16-byte RGB/class records at005537c4, seeding row0 and keeping
strictly smaller signed wrapped squared distance; an improved zero
ends scan. All359 file-backed output classes are0..11 (class10 absent).
Thus every selected row supplies a valid12-entry speech index while
the table is unchanged, irrespective of exceptional distance ordering.
Ordinary byte RGB distance is at most195075 and does not wrap.

Sole speech-loader caller0040a010 supplies this class or replaces it
with99 for custom identity.00413750 tests99 before table indexing;
its random generic-name branch also bypasses indexing. This closes
the ordinary file-backed identification query index/name-length
contract, not mutable table aliases, all RGB semantics, path bounds,
bank slot capacity or complete runtime reads. Names/comments saved.

## Separate speech-language index bound

InitializeGameDataPaths004a6ec4 loads validated007a3a50 intoECX at
004a6ee5. Its path/string helpers leaveECX unchanged; attributes
wrapper004f915e explicitly saves/restores it. Localized-directory
success retains the index; failure004a6f24 sets0 before sole decoded
direct speech-index write004a6f26 to007a2764. Thus ordinary validated
0..5 remains0..5, fitting the separate seven-entry language arrays in
0040a010 and00413750. This is independent of the twelve-entry color
classification table. The fallback changes speech language locally,
without proving every requested bank exists or complete reads succeed.
Aliased mutation and full path bounds remain open. Ghidra path
initializer comment updated/saved; executable unchanged.

## Transfer read-unit correction and archive-close ownership

SendCarArchiveDataChunks0049b9b0 passes EDX=positive chunk size<=208
and EBX=1 to ReadBufferedFileElements004e9200. Full assembly reader
004e9404..08 divides accumulated bytes by saved element size. Nonzero
therefore confirms one completed requested element; partial EOF
returns0 and sender exits-1 before sending that chunk. The previous
Ghidra statement that a nonzero short byte count could be sent was
incorrect and has been replaced. This closes the local read-unit
question, not reader hooks/invalid state or network delivery.

CloseArchiveDirectory0043b9b0 frees EAX directory, closes stream at
[EDX], then clears that stream slot. It cannot clear caller directory
pointer passed by value. Transfer normal completion passes its local
stream slot and global0079f978 directory value; the global remains
unchanged after free. Its decoded writes occur only in Prepare at
0049b920. Zero-read sender path exits before cleanup. Normal repeated
Prepare overwrites the global, but error caller cleanup/reentry and
metadata lifetime still need tracing. No double-free/leak observed.
Ghidra sender comment corrected/saved; executable unchanged.

## Immediate transfer caller ignores failed-read status

Both SendCarArchiveDataChunks callsites in TransferParticipantCarResources
0049bab0 immediately overwrite EAX with0x3c at0049bb7b/0049bc33
and invoke marker wait004a6a10. Neither checks-1 nor performs archive
cleanup there. Thus sender rejection of a partial element does not
propagate as an immediate caller failure, and its pre-close exit is
not locally repaired. The caller's sole decoded entry is0049acdb in
network profile setup. Marker timeout/abort policy is independent and
does not prove file cleanup. Actual failed read, resource retention,
peer result and broader teardown/reentry remain unresolved. Ghidra
caller comment saved; executable unchanged.

## Transfer setup failure admission and installed physics members

PrepareCarArchiveTransfer stores OpenArchiveDirectory return0079f978
at0049b920 and unconditionally passes it to basename lookup0049b943.
No directory/stream success guard intervenes; null directory reaches
lookup's header+8 access. Member miss zeros offset/length, but setup
still seeks, writes length0 into control header and sends28 bytes.
Seek result is ignored. These are conditional failure paths, not
captured runtime defects.

All86 installed/original car.viv entries in the hashed VIV inventory
contain nonempty carp.txt. This closes bounded member presence, not
registry-path correctness or open/allocation/complete-read success.
Ghidra setup comment refined/saved; executable unchanged.

## Car-transfer receiver stage boundary

Assembly confirms offer0049b45c supplies packet+0x18 as expected
file length to InitializeCarResourceTransfer, with no local check of
its return. Append0049b66c..67f adds the complete incoming length
modulo32 bits and checks exact equality only after copy/write. File
completion0049b693..6a9 switches the same state0055e5bc to a fixed
300-byte memory stage at0079f97c. Type16 wrapper0049b508 decrements
incoming length and advances payload without a local minimum check.
No local excess-chunk splitting/clamping or immediate zero-length
completion exists. This establishes the receiver's two-stage boundary;
upstream frame minimum, ordering, legitimate sender pairing, overlap
and cleanup remain unresolved. No runtime defect demonstrated.
Ghidra append comment saved; executable unchanged.

## Paired car-transfer emission partition

Prepare0049b95b advertises member length at header+0x18. Callers
0049bb6b/0049bc28 load the same field into sender EBX, pairing
types15/16 and17/18. For positive signed length and complete reads,
each payload is min(remaining,208); subtraction reaches zero without
crossing the declared file boundary. Metadata is a separate300-byte
loop emitting208 then92, matching the receiver's fixed memory stage.
This closes local chunk partition arithmetic, conditional on ordered,
complete delivery, successful initialization and unchanged shared state.
Zero/nonpositive lengths skip file chunks and do not establish the
receiver's file-to-memory transition.

Dispatcher004a6440 checks abort/type range but no EBX minimum before
indirect callback004a645e. Both data wrappers decrement EBX then
advance payload; both setup handlers read+0x14/+0x18 without local
length checks. Fallback flattening00512470 supplies aggregate length,
but dispatcher does not validate it. Provider admission, framing,
ordering, overlapping sessions and cleanup remain open; no malformed
packet or runtime defect demonstrated. Ghidra comments saved.

## Receiver open failure and zero-length state

Initialize0049b54c/553 clears offset/status before attempting file open,
stores expected length at+4, but file branch leaves destination+8
untouched. Failed open stores0 at+0x10 and returns-1 without restoring
stopped status; both setup handlers ignore that return. Append chooses
memory versus file solely from+0x10, so a subsequent payload after
failed open uses retained destination+8. Initial file-backed20-byte
state0055e5bc decodes as{1,0,0,0,0}; destination initially0, or can
retain0079f97c after a prior metadata stage. This is a conditional
state-confusion path, not a captured runtime failure or exploitability
claim. Actual open-failure reachability, provider delivery and lifecycle
remain unresolved.

Expected length0 has no immediate transition in initializer. Sender
skips file payloads for nonpositive signed length and sends metadata;
positive cumulative metadata lengths208/300 do not equal0. Thus the
ordinary zero-length emission sequence cannot itself trigger the
receiver file-to-memory transition. Installed86 car.viv archives have
nonempty carp.txt; missing/custom members and failed I/O remain open.
Ghidra initializer proof comment saved; binary unchanged.

## Registry target retention after transfer

Discovery entry00439d9e invokes cache reset004399f0, which clears
50 pointer cells005f3c00 only. It does not reset last-discovered
00554f74, initially0 in file-backed bytes. Its sole decoded direct
writer0043a328 follows successful append. Allocation failure00439fef,
metadata-view failure0043a270 and no-new-model scans retain the old
value. Getter0043bbf0 merely loads it. All four transfer setters
0043bc00/40/70/90 test nonzero, without generation or membership
validation; transfer0049b7c7 ignores discovery result before them.
Thus their null guards cannot establish the intended fresh transfer
target. Actual stale-target mutation, indirect aliases and lifetime
remain unresolved. Existing display setter interpretation is confirmed:
0x100 is a variadic argument, not a capacity bound; received text is
the format. No runtime defect demonstrated. Discovery proof comment
saved in Ghidra; binary unchanged.

## Temporary directory cleanup name predicate

Recovered/named0043bcf0 RemoveCarDirectoriesWithThreeDigitPPrefix.
It requires uppercase P followed by three characters whose ctype
bit0x20 is set; inspected file-backed00564ef0 identifies decimal
digits. There is no name[4]==NUL check, so this matches a prefix,
not an exact four-character name. It builds a300-byte local path
without a local length bound and invokes004389d0 without checking
its result. Flag08 removal calls this before rediscovery, whereas
full registry teardown calls per-node resource-path cleanup0043b2a0.
Neither reviewed cleanup body directly clears last-discovered pointer.
Name predicate is established; deletion success, runtime directory
contents, path limits and stale-target lifetime remain unresolved.
Ghidra name/comment saved; game assets unchanged.

## Temporary cleanup traversal and result propagation

DeleteFilesThenRemoveDirectory004389d0 deletes only non-directory
entries, then attempts removal of the parent. Nested directories
are skipped, not recursively removed. Per-file permission/delete
results are ignored; EAX reports only final removal-wrapper status.
Caller0043bcf0 ignores that status too, so local transfer cleanup
does not propagate deletion failure. Empty enumeration and search
failure both lead to the final parent-removal attempt.

For uninterrupted traversal, first/next enumeration exhaustion
calls FindClose and clears shared00554f7c. First-search failure
clears the slot. Only these two routines have decoded direct refs
to it. FindFirst overwrites an existing handle without preclosing,
so reentry/early-exit callers require separate proof. The ordinary
cleanup loop does drain to exhaustion; no handle leak is established
for that local sequence. Names/comments already existed; expanded
cleanup proof saved. Filesystem results/concurrency/path bounds
remain unresolved. No actual deletions or binary changes performed.

## Archived car display-string content

Parsed274 localized FEDATA members in active/original VIV trees,
excluding fedata.fsh image assets. Metadata view00439bd0 supplies
count at+0x2d and buffer-relative offsets at+0x2f; getter00439af0
selects third string with offset at+0x37. All274 third strings have
valid in-member NUL-terminated spans, maximum22 bytes and no percent
characters. Hashed member/archive evidence is stored in
installed-car-display-strings.json.

This closes only archived source-text content. Sender00439250 may
use model+0x10 or alternate ID-based tables; loose localized files,
runtime modifications, peer content and complete reads are outside
this inventory. Display setter still treats received text as format
with no capacity argument. Ghidra setter comment updated/saved.
No game assets changed.

## Current loose metadata override check

A recursive filesystem check, independent of rg ignore rules, found
no regular localized FEDATA files under either GAMEDATA or
gamedata_org. All114 archive SHA256 values still match the directory
inventory used for the274 display-string extraction. Evidence is
installed-car-display-source-check.json. This closes current loose
override presence for these two roots only; alternate configured
roots, later writes, special IDs500..599 and live/transformed strings
remain outside the content proof. No full network format-safety claim.

## Special display-name ID extent

GetCarModelDisplayName00439250 admits500..599 and loads
[0055c944+4*ID]. The effective base for500 is0055d114.
Inspected400-byte file-backed span contains six actual strings for
500..505: cvic/eagl/falc/rovr/vett/diab. IDs506..512 alias
neighboring seven language-code pointers0055d12c;513..515 yield
DWORD100, and516..599 yield0. The accepted range therefore does
not establish100 valid display pointers. No100-element array was
created across these adjacent objects. Upstream special-ID admission,
runtime table changes and car-transfer reachability remain unresolved;
no invalid-ID access observed at runtime. Getter proof comment saved.

## Dynamic-text caller excludes special car IDs

LookupDynamicText004d17b0 accepts car-label IDs0x7bd..0x7ee,
subtracts0x7bd intoEDX and forwards that value at004d180e to
display getter004d1810. Intervening predicate00439cc0 calls
00439a50/00439c10; both preserveEDX. Hence this specific caller
supplies0..49 and cannot enter special500..599 branch. It does not
establish registry presence: missing-model predicate returns0 and
still reaches display getter, whose node+10 calculation has no
NULL guard. Other callers and runtime registry/cache lifetime remain
open. Dynamic-text Ghidra proof comment saved.

## Transfer eligibility is not model-ID admission

CheckCarIdentifierFlags41Clear00439530 resolves a sixteen-byte ID
through00439990, an uncapped linked-list scan returning first ordinal
or-1. It immediately calls flag40 accessor00439570, then flag01
accessor00439680 if needed. Both call getter00439a50 and dereference
model+0x380 without NULL checks. Getter rejects signed indices>49,
but lacks negative-index rejection before cache indexing. Thus the
boolean predicate used at0049bb52/0049bc00 cannot establish a valid
ordinary/special model domain or successful identifier lookup. A
stable valid registry of at most50 entries is an independent
precondition, not a result of this flag test. Upstream registry count,
model ID and peer profile admission remain open. Ghidra predicate
comment expanded/saved; no runtime or binary changes.

## Participant readiness does not validate car identifiers

ReceiveNetworkParticipantStateBlock0049b310 copies96 wire bytes
to slot*96 without model validation. Readiness0049ab60 requires
connection state, participant count>=2, mapped slots and nonzero
profile ready byte+8. It never resolves a car identifier. Later
ApplyNetworkProfilesToRaceParticipantSetup0049ad69 resolves the
identifier and0049ad6e stores EAX into setup model field without
checking-1. Therefore readiness and profile presence do not establish
model admission or successful post-transfer discovery. Legitimate
profile producers, sender authority and registry lifetime remain open.
Ghidra readiness proof comment saved; binary unchanged.

## Local profile selected-model provenance

Sender0049a93e loads selected DWORD006fd2bc and obtains identifier
via00439520, which calls model getter then adds0x31c without
NULL guard. Local-slot validity only gates profile sending; selected
model/flags/defaults remain unchecked here. Stored-key resolver
00439a10 writes identifier lookup result at00439a2f without checking
-1. Cheat producer004528fc likewise stores lookup result, gated by
ECX policy rather than lookup success. These establish additional
unvalidated producers, not a reachable runtime failure: missing-ID
configuration/cheat circumstances, menu indirect writes and cache
lifetime remain unresolved. Sender proof comment saved in Ghidra.

## Command-line car selector admission

Option index7 at0055ec6c points0053d65c '-CAR='. Generic%d
parse004a52b0 computes destination007a2008 without a local numeric
domain check. When endpoint is nonempty, transport-two session
0049e1ba loads that DWORD and0049e1c1 calls stored-key resolver.
Resolver00439a14 immediately reads[00554f84+4*EAX] without bounds,
builds a zero-padded16-byte key, resolves it and stores index without
checking-1. Final parser gate validates neither car index nor this
table extent. Thus this startup chain does not establish valid
selected-model admission. Full startup reachability, table domain
and downstream reconciliation remain open; no malformed launch was
executed. Resolver Ghidra proof comment saved.

## Car selector startup ordering

RunFrontendSetup direct-network branch requires0055b03c!=0 and
nonempty endpoint. PNUM>1 calls client wrapper0049e220, otherwise
host wrapper0049e2e0; both call0049e080 before result handling or
client roster wait. The unchecked car-key resolver0049e1c1 executes
before backend initialization004a5b00 at0049e1d8. Successful routes
rejoin frontend menu at00473267, so subsequent menu reconciliation
cannot protect the earlier key-table read. This closes the ordering
question only; initial flag source is resolved below (file-backed1).
Supported key-table extent and full startup/runtime reachability remain open. Resolver comment
expanded/saved in Ghidra.

## First-entry direct-start flag source

File-backed DWORD0055b03c is1. Its decoded direct xrefs are three
reads in RunFrontendSetup and sole write00473269 clearing0 before
ordinary menu. Therefore initial direct-route enable does not require
a separate command-line flag setter. Nonempty endpoint selects that
first-entry route; network failure exits before clearing it. This
resolves the missing initial producer question, not bulk/indirect
mutations, reentry or full runtime startup. Prior notes listing the
initial flag producer as unknown are superseded by this byte check.
Ghidra frontend comment saved; binary unchanged.

## Stored car-key installed presence

First nine nonzero file-backed DWORDs at00554f84 are
23,19,2,31,30,24,15,16,21. Their zero-padded16-byte identifiers
exactly match FEDATA.ENG records in both active/original trees:
AMD7,CORV,F355,FM50,SCIG,JXK8,COUT,DIAB,SL60 respectively.
Evidence: installed-stored-car-key-matches.json, referencing the
hashed VIV directory inventory. Following inspected DWORDs are0;
this is not proof of a declared nine-entry table or supported input
bound. Installed key presence is resolved for these nine values;
discovery filters/allocation/reads, runtime membership and arbitrary
selectors remain unresolved. Resolver Ghidra comment saved.
