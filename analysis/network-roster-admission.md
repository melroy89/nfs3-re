# Network roster admission boundary

Status: partial static contract; transport framing and sender authorization
remain unresolved. No runtime packet testing or executable changes.

## Established callback chain

`InstallNetworkConnectionCallbacks`004a6410 stores control dispatcher004a6440
at connection+20. Its type1 table entry0055ecc0 is roster receiver004a68d0.
The dispatcher reads the packet type before checking the abort flag, accepts
types below19 and forwards the original packet pointer. It does not consume
a packet-length argument to gate type1 processing.

`ReceiveNetworkParticipantRoster` copies0x7c bytes from the packet start to
007a2214. It clears eight WORDs at007a22ca..007a22d8, leaving index0 of the
base007a22c8 untouched, and sets roster-changed007a2296. Transport2 scans
eight roster positions, compacting nonlocal entries into remote rows; this
fixed scan is distinct from the advertised count and overall gameplay limit.
Its first invocation bypasses lock0055ecb4 under007a2210==0.

## Buffer ownership versus validation

Fallback00512470 sums segment lengths, allocates a temporary flat buffer,
copies segments, calls connection+20 with EBX total length and frees the
buffer synchronously afterward. The control dispatcher and roster receiver
do not establish a0x7c minimum despite this available length. Nonpositive
segment counts still reach the callback with total0. This is a conditional
local contract, not proof that a provider admits empty/short control packets.

The indexed unpacker dispatcher uses entry+8 instead of flattening when
an index resolves; its collection lookup lock ends before callback dispatch.
Thus fallback temporary ownership cannot establish indexed-handler ownership
or universal transport validation. The next boundary is the registered
unpacker/provider chain that admits segment lengths, packet origin and type.

## Join and notification semantics

Join0049e800 waits for roster-changed with callback/abort servicing and checks
version after readiness. The notification flag is set by roster reception
and also disconnect/inactive/connection-loss paths, so observing the flag
alone does not prove receipt of a complete new roster. Consume004a69c0 checks
before taking the lock, then clears under lock: it is a coalescing flag,
not a counted event stream or a proven atomic read-and-clear operation.
Further lifecycle ordering, first-receive lock invariants, sender authority,
packet minimum sizes and concurrent teardown remain open.

## Service registry ownership

Service initialization004f4d10 searches registry009f25f0 by the incoming
object pointer, invoking teardown only for that existing object. It clears0xac bytes and
reuses the object across candidate attempts. Only a nonzero backend result
permits registry insertion. Caller0049e3d0 clears the active key before
initialization and commits the requested key only after success. This is
pointer ownership and success-gated registration, not eviction by service key.
Backend partial-state cleanup after zero return and candidate table validity
remain unresolved; no multi-peer runtime admission test was performed.

Parent assembly refinement:004f4d10 zeros the service only once before its
candidate loop, so failed candidates can leave fields for the next attempt
unless backend code clears them. At0049e3d0 the same-key branch0049e412
bypasses reinitialization. The requested key is committed before enumeration
004f4eb0; enumeration failure does not locally clear it. Therefore the key
represents initialized service selection, not successful enumeration or
participant admission. Saved both function comments in Ghidra.

Teardown qualification:004f4e60 searches by object identity, dispatches backend
kill method+0xc, then passes the post-call EDX value to queue removal. Correct
removal therefore also depends on backend register preservation/return ABI;
exact-pointer lookup does not by itself prove successful removal. This backend
contract remains open.

## Candidate loop boundary

The inspected count00566de4 has only two direct references, both loop reads,
and its saved DWORD is zero. No separate capacity comparison occurs before
indexed candidate table loads009f25b0/009f25d0. Static reads of those recovered
BSS tables fail in the current database; this is not evidence of unmapped
runtime memory. Concrete candidate initializers and population writes remain
unresolved, including aliased/external writers. Zero initializer result
continues or exits without an outer rollback call; backend self-cleanup is
unknown. The service object is not re-zeroed between failed candidates.

## Recovered socket select worker provenance

Recovered898-byte registered entry004f68c0 as
RunSocketConnectionSelectWorker; registration reference004f7521. Assembly
004f69c0..cc invokes queue iterator0050e9b0 with queue009f2628, collector
004f6570 and local scratch. The resulting connection pointer table feeds
reader004f6640 at004f6b00. Service singleton009f37f0 field+38 is a
separate pending connection, not the enumerated list itself. This corrects
the earlier worker inference before persistence.

Writable entries call004f67b0, exceptional entries004f6860; combined
nonzero status reaches removal004f6870. Running/stop bytes are+47/+46.
Per-connection+10/state+4 frame-limit producer is recovered below; select
set cap64 does not establish frame-size or participant-capacity bounds. The
runtime provider word and later state mutation remain unresolved.
Queue collector provenance, state allocation and concurrent lifetime remain
open. Static evidence only; Ghidra entry and proof comment saved.

## Select collector and distinct capacity checks

Recovered199-byte CollectSocketConnectionSelectSets004f6570. Include
only context[connection+4] DWORD0==1, valid socket+48, and connection
different from service+38. The collector first appends connection to
scratch+314 and increments count+310 without a local cap (004f6596..ad).
Subsequent read/exception fd-set additions each require count<64; send
set also requires WORD[state+6]>0, state=connection+10. It always returns1.
Therefore fd-set caps do not bound the preceding pointer append. Actual
queue admission/cardinality and scratch-capacity invariant remain open;
no runtime overflow or exploitability is claimed.

Immediate-operand search for009f2628 finds additional queue sites in
0051bdc0 and0051c2d2/0051c4d6/0051c6ba/0051cca8/0051d610/0051d7c9/
0051da0b. Earlier networking-region searches ending00510000 did not
cover these. These sites are the next producer/admission trace targets.
Ghidra collector name/comment saved; no binary change.

## Provider-wrapper teardown ordering

Assembly-verified0051bdc0 and0051cc80 remove wrapper[0] connection from
009f2628 first. Failed removal returns after optional diagnostics, without
callbacks or destination-queue push. Successful removal clears connection+24, invokes
wrapper context+4 callback withEAXconnection, invokes connection+18 with
EAX=EDXconnection, thenPushLinkedQueueNode0050de50 on009f260c. The wrappers differ in
diagnostic identity byte offsets+0e/+0d and associated strings.

This establishes local unlink-before-callback ordering. It does not establish
retirement from worker scratch snapshots, callback non-reentry/reinsertion
or destination-queue reuse/lifetime. Both Ghidra comments preserve these limits.

## Destination queue push, not memory release

0050de50 is now named PushLinkedQueueNode after full assembly verification.
Under queue+18 lock, a nonnull node links to old head+8, becomes head,
increments count+0, sets tail+0c if previously empty, and sets flagbit1
at+4. Null input only locks/unlocks. No allocation/free or local capacity
check exists. Thus provider teardown recycles the connection into009f260c
after callbacks; prior generic release wording was corrected. Actual node
reuse and stale worker snapshots still require caller/lifecycle evidence.

## Packet-layer state is not the socket-reader state

Recovered1037-byte0051c100 as OpenUnreliablePacketLayerConnection. It
allocates/reuses connection+10 state, stores descriptor pointer at state+4
and adjusted requested size at+8. Size is raised to descriptor byte+1e
when necessary; that byte is a minimum, not an upper cap.

Raw callback table0056ac10 has DWORD type5, with0051c100 at+4.
004f5130 stores the chosen context at connection+4. Collector004f6570
requires context DWORD type1, so ordinary type5 records are excluded from
the socket reader despite sharing queue009f2628. Queue membership alone
does not prove reader reachability. An apparent pointer-versus-length field
mismatch was rejected after this provider-type check. The type1
state+4 producer is recovered below; runtime value, later mutation and
context reentry remain open.
Ghidra constructor name/comment preserve this distinction.

## Type1 socket frame-limit initialization

Context00566e8c raw DWORD is1; its open callback+4 is004f6c50.
Wrapper004f7380 selects this context through004f5130. Recovered names:
OpenSocketProviderConnectionLayer and InitializeSocketConnectionState.
Constructor instructions004f6c89..b2 initialize state+4 to1024 when
WORD009f37e8 is zero; otherwise store low16(zeroextended provider WORD-2).
State+6/+8 are cleared and connection+10 is published at004f6ccb.

The default permits at most1026-byte framed peek, preceding reader live
metadata at offset0x404 (1028). This closes the zero-word default extent
calculation, not arbitrary provider-output safety or aggregate setup bounds.
Actual nonzero provider value/range and subsequent state writers remain
open. The entry definition was rebuilt to a980-byte body; frame-limit setup
was assembly-checked, while error and lifetime paths remain unaudited. No runtime observation or binary
modification.

## Socket limit source: startup output

InitializeSocketProviderLibrary004f73a0 calls Winsock ordinal115
(WSAStartup) with requested version0x101 and output009f3660. Limit word
009f37e8 lies at output+0x188, consistent with legacy32-bit WSADATA
iMaxUdpDg. This is provider output, not an established user setting.
[Microsoft WSADATA reference](https://learn.microsoft.com/en-us/windows/win32/api/winsock/ns-winsock-wsadata)
identifies that compatibility field as maximum datagram message size.

Assembly004f73d4..fa returns1024 for zero or values whose subtract-two
result exceeds1024, otherwise subtract-two. The connection constructor
004f6c50 lacks this upper clamp before its state+4 store. Therefore the
initializer's reported capacity alone does not prove a1024 reader maximum.
Raw1 also gives signed-1 before low16 storage in the constructor; actual
provider outputs, caller constraints and aliases remain unvalidated.
Ghidra initializer name/comment saved.

## Socket constructor metadata recovery

After decoding the entry, rebuilt the initial one-byte function definition
at004f6c50; Ghidra now reports a980-byte body. Preserved the descriptive
name and proof comment. This corrects metadata coverage, not source bytes.
Full error/lifetime paths remain unaudited. SCRATCHPAD multiplayer/admission
rows now reflect the discovered provider-output limit source.

## Type1 socket close ownership

Recovered126-byte CloseSocketConnectionAndRecycleRecord004f71a0
(context00566e8c+10). Successful removal from active009f2628 precedes
shutdown(socket,2), sleephelper1, closesocket, socket=-1/status=0 and
push to009f260c. It then independently removes from009f260c. Only when
that succeeds does it inspect connection+10 state; nonzero state DWORD0
causes state free and pointer clear. The connection node itself is not freed
here. Return1 follows successful second removal, otherwise0.

This ties constructor state ownership flag to conditional cleanup. No
null-state check or worker snapshot-retirement wait is shown in this body.
Actual concurrent lifetime, aliases and node reuse remain unresolved. Name,
full assembly proof comment and project saved; no runtime or binary change.

## Socket send acceptance and partial transmission

Recovered354-byte SendLengthPrefixedSocketPayload004f7030, type1
context00566e8c+8. Pending nonzero returns0. It stores a big-endian
16-bit prefix and synchronously copies payload into state+0e, sets pending
WORD to low16(length+2), then attempts send under00564480 lock.
Positive partial writes reduce pending and advance pointer;004f67b0 later
flushes remaining bytes. Initial retryable errors2747/2733 clear pending
and return0; other errors or zero/positive send return1. Thus1 is not
proof of full transmission, and caller retry semantics remain open.

Oversize length invokes an abort diagnostic but continues if that handler
returns. Pending check precedes locking. State allocation extent, provider
limit, abnormal abort-return, concurrent send and caller retry remain open.
Also recovered158-byte InitializeConnectionEndpointSession004f7280;
its descriptor callbacks/ownership remain partial. Ghidra names/comments
saved, no runtime or binary changes.

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
