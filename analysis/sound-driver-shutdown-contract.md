# Sound-driver stop and unload

Host nfs3.exe StopSoundDriverThroughWindowMessage004e253c dispatches message
8200hex with nonzero parameter, waits for completion009ef607, then unloads
via004e217c. Handler004e225c calls iSNDdirectstop through009ef624 at004e2431,
does not test its result, writes result009ef60c=0 and completion=1. Therefore
acknowledgment orders the call before unload, but does not prove stop success.
Dispatch-failure/timeout behavior and backend worker retirement remain open.

REA independently opened the installed eacsnd.dll with immutable-source
Ghidra analysis. SHA256:
63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3.
Export iSNDdirectstop at0040207c conditionally calls object0040a8a8 vtable+48,
then releases object0040a89c through vtable+8. A nonzero release return logs
failure and returns-1 before clearing later backend globals; the host still
signals completion. External interface semantics and whether any work remains
active are not proven by this exported body. REA evidence ID:
ev_f2dae5e3f39cee492ec1015921784d74dbf87d61c340492e4c091a1c0339e07f.

Host unloader clears module handle but leaves resolved export pointer cells;
stop does not unregister message8200. Safe later invocation therefore requires
separate caller/backend lifetime evidence. No runtime failure, active worker
after unload or use-after-free is asserted. Backend directstop failure return
is a concrete branch, not a captured failure. No DLL/executable bytes changed.

## Host service-loop retirement and ordinary guards

Recovered worker0048ec40 RunSoundServiceEventWorker creates/publishes event
0079c168, calls callback0079c150 then waits, repeating until callbackNULL.
It closes the event and clears the published handle before its epilogue.
Setter0048ec80 SetSoundServiceWorkerCallbackAndWait clears the callback,
signals the event and waits for that handle to become zero. Sound stop calls
this before backend directstop, establishing callback-loop retirement for
ordinary successful handshake, not an OS-thread join or backend worker bound.
Creation failure/no timeout/concurrent publication remain open.

Ordinary top-level sound APIs check initialized00a09af4; shutdown clears it
after stop, and start reloads exports before sending message8200. The window
handler itself has no initialized guard and remains registered through later
window teardown. No queued/external post-unload invocation was captured; that
ownership case remains open rather than dismissed by top-level API guards.

## Separate music stream worker teardown

Named004e4a30 StopHeadMusicStreamWorkerAndReleaseHandles. It sets
head stream+24=8 and polls+28 while equal1, with no sleep/service call
in that loop. Timeout uses signed comparison of0079c1a4 against captured
counter+10000;0048eb90 increments that counter per active timer-worker
wake. No milliseconds conversion follows. Wrapping deadline and returning
abort handler also prevent treating this as an unconditional bounded wait.

After polling it signals worker wake event athead+8c+1c (=+a8), waits
completion handle+ a4, closes+a4/+8c and releases/clears criticalsection
+ac. Signal and waited handle are distinct. The+28 completion producer
and final wait termination remain open. This is separate from sampled
004109d0 fade polling; no slowdown cause is inferred. Ghidra name and
full-assembly comment saved.

## Music worker exit notification

Recovered and named RunMusicStreamStateWorker004e53c0. Assembly
004e53c9..53e2 publishes wake event+0xa8 and signals+0xa4 at startup.
Command+0x24=8 selects state+0x20=8. Shutdown004e5572..55b4 closes
nonzero file+0x1c, clears it, closes wake event+0xa8, signals+0xa4,
and returns. This establishes the normal exit notification producer
for the teardown event wait, not an OS-thread join. The same event is
also signaled at startup; startup consumption and event lifetime must
be reconciled before treating any signal as unique proof of retirement.

The recovered worker has no direct+0x28 operand. The earlier+0x28
poll producer remains unresolved. File-I/O retry004e629d..62c4 calls
005013b0 and alertable sleep without checking command+0x24 inside
that loop; therefore unconditional prompt shutdown is not established.
No historical slowdown cause or executable modification is inferred.

## Startup consumes the ordinary event notification

InitializeHeadMusicStreamAndStartWorker004e4420 creates event+0xa4
via004dfb00 at004e4556..455b (ESI is stream+0x8c). The wrapper calls
CreateEventA with manual-reset=false and initial-state=false. After a
nonzero worker-launch result,004e4581..4587 waits on+a4 before returning.
004dfb70 uses004df6f0 to wait indefinitely on one handle; the latter
calls WaitForMultipleObjectsEx. An ordinary successful auto-reset wait
consumes the startup notification, consuming that notification in the ordinary successful path. Other
command notifications also use this event, as qualified below.

The initializer ignores the wait return, including failure, so this
is not unconditional proof. A returning launch-failure diagnostic
also reaches the wait at004e45bf..45c5. The separate+0x28 producer,
concurrency and guaranteed worker termination remain unresolved.
Name/comment saved in Ghidra; no binary modification.

## Shared command and lifecycle notification event

Further assembly qualifies the startup finding: worker004e53c0 also
signals+a4 at004e5872 after selecting state2, and004e5998 after
selecting state7 from state20. This event is not exclusive to startup
and exit. ReplacePendingMusicStreamCommands004e4d70 waits on+a4 for
commands11,13,20 after waking+a8; it ignores the wait result. Pending
command notifications and call serialization remain to be reconciled
before a shutdown wait can uniquely establish retirement. Startup
consumption alone does not establish that broader claim.

Named QueueMusicStreamCommand004e4c60 and
ReplacePendingMusicStreamCommands004e4d70. Both manipulate the pending
node list+78/+7c under+ac lock, store node parameter+90/command+94,
and wake+a8. Replacement drains prior nodes, but does not locally test
the replacement pool-acquisition result before writing it. Reachability of
pool exhaustion/returning diagnostics remains unproven.

A full decoded instruction operand scan matched1392 occurrences of
0x28 without truncation; in004e4000..004e6fff only the two teardown
comparisons appear. This excludes only direct matching operands.
Initializer004e4502 writes stream+28=0 through rebased ESI-64, so
alias/rebased accesses still require analysis. No producer setting1
is established and no permanent-unused-field claim is made.

## Music command pool admission

AcquireMusicStreamCommandNode004e6b30 is a preallocated free-list pop,
not a heap allocator. Global head+74 is the free head; node+98 is the
next link. Empty pool with EAX policy0 unlocks and returnsNULL. With
nonzero policy it diagnoses NO_STREAM_BLOCK, then dereferences the
free head if the abort handler returns. QueueMusicStreamCommand checks
the returned node; ReplacePendingMusicStreamCommands does not. The
replacement path first recycles pending nodes, which may make a node
available, but an unconditional nonempty-pool invariant is not proven.

RecycleMusicStreamCommandNode004e6a20 prepends a node under head+ac
lock without a local membership/double-return check.
CheckMusicStreamFreeCommandNodeCount004e6a70 counts available nodes
under that lock and returns whether the requested count was reached;
it does not reserve them. Init004e45f0 allocates/zeros stream metadata
and command storage using0xc0+align16(0x9c*count), with arithmetic
masking/overflow details retained in assembly;004e4420 links nodes
from stream+c0 through004e69e0. Pool-count domain and exhaustion
reachability remain unresolved. Three helper names/comments saved.

## Installed command capacity and admission checks

File-backed DWORD005645a4 is8. Its five decoded direct xrefs are
reads in initialization/allocation; no decoded direct writer appears
in that xref set. This establishes the installed initial value, not
immutability against aliases or runtime mutation. Eight0x9c-byte nodes
require0x4e0 command bytes; metadata allocation is0x5a0 including0xc0
header. The initializer links the free list from stream+c0.

Named QueueSoundStreamWithCommandCapacityCheck004e78a0. Its active
path checks1 free node for mode0 at004e799b..79a0, or2 for the other
mode at004e79d1..79d6, and returns-13 if unavailable. It separately
checks byte queue-counter sum>18 under the sound lock, then releases
that lock before free-node checks. These checks do not reserve nodes
or hold the pool lock through subsequent enqueue; concurrency remains
unproven. Initial inactive paths bypass those capacity checks.

All three direct replacement wrappers pass fatal policy1:
004e4f20 command13 (waits),004e4fe0 command20 (waits), and004e4f60
command18 (does not wait). Draining pending nodes precedes acquisition,
but active/other owners and pool exhaustion are not fully reconciled.
No observed runtime failure is asserted. Name/comment saved in Ghidra.

## Music ring acquisition and idle predicate

Named AcquireMusicStreamRingChunk004e6740 and IsHeadMusicStreamIdle
004e68e0, verified against assembly. Acquisition returns0 for pending
commands11/13/20/23, states1/2 or unavailable data; state14 returns-2.
Under+ac lock it wraps header marker-1 to ring base+4, checks header
length against signed contiguous availability, advances read+14 and
moves length-8 between+b8/bc counters. Marker-3 returns-1 and signals
head+a8; it advances release+18 if equal to the marker location, or
rewrites marker-2 for later retirement. Ordinary return is a header
pointer. No local positive/minimum8-byte length guard appears; writer
invariants and owned-chunk release remain to be reconciled.

The idle predicate is unlocked: true for missing head, or state7 with
no pending+78 commands. It does not prove worker retirement or absence
of owned chunks. The decoded direct+28 operand scan also finds no
matches in004e7000..004e9fff; rebased aliases remain outside that proof.
Ghidra names/comments saved. No runtime or executable modification.

## Contiguous release frontier

Named ReclaimReleasedMusicStreamRingChunks004e6660. Under stream+ac
lock it stops when release+18 reaches read+14 or producer+10. Header
marker-2 subtracts length-8 from outstanding payload+bc and advances
release by length; marker-1 wraps release to base+4. Any ordinary
outstanding header stops reclamation, so a later released node cannot
be reclaimed past an earlier outstanding node.004e68a0, already named
MarkSoundStreamNodeReleasedAndSignal, writes-2 and signals+a8 without
heap deallocation. This connects release notification to delayed
contiguous reclamation, not immediate reusable ownership.

The reclaimer is called by worker state7 and the three free-space
helpers004e66e0/6710/6720. Header validity, duplicate release, pointer
membership and all consumer completion paths remain unproven. No
local length validation was added or inferred. Ghidra comment saved.

## Consumer queue cleanup and tag dispatch

Named ReleaseQueuedSoundStreamChunksAndClearPointers004e7ff8. Under
the sound-library lock it preserves next, releases each queued node
through tail, then releases nonNULL retired00564688. All three queue
pointers are cleared even when initial head00564680 isNULL; that
branch skips retired-node release. The invariant that a retired node
implies a nonNULL head has not been established. No list-cycle/tail
membership checks occur locally. This is a conditional ownership
question, not a demonstrated leak or runtime failure.

Purge004e7b28 first stops/waits for the voice and services periodic
callbacks, then invokes queue cleanup under the sound lock and resets
stream state/unregisters a timed callback. Abort-return and service
count deadline details still require assembly review.

Named DispatchSoundStreamChunkByTag004e7f30. Under the sound lock it
dispatches five tag values to004e8078/80cc/8258/82c4/82ec; unknown
tags are marked released immediately. Tag payload validation and
handler ownership remain open. Ghidra names/comments saved.

## Recovered timed stream callback and retained retired node

Recovered ServiceQueuedSoundStreamPlayback004e85a8, body921 bytes,
registered by004e8944. State4 (stream-state byte005646fd) calls
004e7df4 and tests signed stream+b8>5000.004e68c0, now named
GetMusicStreamQueuedPayloadBytes, reads+b8;5000 is a payload-byte
threshold here, not a duration. This branch drains pending consumer
queue, skips nonterminal node equal retired00564688, releases tail,
clears head/tail, preserves retired pointer, resets counters, and then
acquires/dispatches replacement chunks before selecting state2.

Therefore retired-implies-nonempty-head is not unconditional at
intermediate points. Whether the callback returns with empty head
and an outstanding retired node requires the refill/chunk sequence
and state4 reachability. No runtime leak or use-after-free is proven.
Refill004e8328 normally retires the previous node when advancing to a
new node, then records the just-consumed node at00564688. Initializer
004e8944 clears head/tail but also preserves that retired pointer.

State3 callback cleanup waits for voice expiration before queue
release/reinitialization; lifecycle/failure details remain partial.
Ghidra callback recovery, helper name and comments saved.

## Purge voice wait deadline

Named PurgeSoundStreamerAfterVoiceExpiration004e7b28. Assembly captures
DWORD00a09afc+200 with wrapping addition, then polls004e8fd0 until
any nonzero result. Unsigned deadline<current at004e7b6f..75 invokes
the abort diagnostic; if it returns, the code services periodic
callbacks and retries. The ordinary waiting path also services them.
00a09afc increments in00500c80 per sound-service invocation, so200
is not a proven millisecond deadline. Wrap/stalled service and
returning abort prevent claiming unconditional bounded termination.

CheckSoundVoiceHandleExpired004e8fd0 preserves caller EDX (deadline)
and returns0 while voice lookup004ffc9c is nonnegative,1 for negative
lookup, or-10 when sound is uninitialized. Purge accepts any nonzero
result, including that error. After wait it locks, cleans queue, resets
state, invokes004ff660 and unregisters timed callback004e85a8 if
flagged. Callers are shutdown004e784c and music stop004109d0. This
adds exact deadline/poll semantics without proving backend silence,
thread retirement, all owned-chunk release or historical hang cause.
Ghidra comment/name saved; executable unchanged.
