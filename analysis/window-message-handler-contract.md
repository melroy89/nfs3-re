# Window message-handler table

004fb300 is a generic strided binary search, not an INI section search. Its
two direct callers004cc660/004cc6d0 use stride8, base007f7060 and count00561268
with subtracting integer comparator004cc650. Empty count returnsNULL; a match
returns a record address. Generic duplicate preference is unspecified.

Setter004cc6d0 searches while holding the shared critical section, updates an
existing handler, or adds only absent/nonNULL handlers below capacity128.
Removal writes tombstone7fffffff, sorts and decrements active count. Observed
direct registration IDs from window/input/sound/DirectDraw initialization
range1..8200hex; difference81ff cannot overflow signed32 subtraction, and
the tombstone sorts last within that domain. With only these admissions and
valid state, fixed stride/count/unique-key ordering are established. Generic
DWORD admission is not validated; setter data reference0056afd8 also leaves
indirect/external callers outside the direct-site bound.

Lookup004cc660 copies handler+4 under lock, then unlocks and returns that
value. It does not return the movable table record; callback/module lifetime
remains separate. Both paths lazily create the critical section without an
atomic once guard. InitializeDirectDrawWindowSession00508390 (new descriptive
name) registers464/465 before InitializeGameWindow; observed startup flow is
synchronous before the later window worker. This does not establish global
first-use serialization across sound/input/indirect callers.

Actual concurrent first use, external registration domains, alias writers,
allocation failure and callback-module shutdown remain unresolved. No runtime
race or malformed-input occurrence is claimed. Saved names/comments in Ghidra.

## Mouse handler retains a prior callback independently

Recovered HandleMouseSetCursorAndChainPreviousHandler00436930,79
bytes. Mouse init saves lookup(message0x20) into00554ef4 at004351e1
and registers this handler. It forwards six stack slots to the saved
callback when nonNULL, ignores its return, then checks lowWORD fifth
argument==1. On that condition it calls SetCursor(NULL), writes1 to
the incoming sixth stack slot, and returns1; otherwise returns0. The
custom six-argument/RET24 ABI is not a direct four-argument WNDPROC.
The stack-slot write is not a pointed-to result write.

The prior callback pointer survives separately from table membership;
removing its table entry alone cannot invalidate this saved reference.
The decoded00554ef4 xref set shows only initialization write and two
handler reads. Cleanup restoration, reinitialization and pointed-to
module lifetime remain unresolved. No stale invocation was captured.
Ghidra recovery/name/comment saved; executable unchanged.

## Mouse cleanup and conditional reinitialization chain

Assembly00434fd0 closes the mouse event, unacquires/releases device,
clears mouse/context, but does not restore/unregister message0x20 or
clear saved prior00554ef4. Sole decoded direct shutdown caller is
ShutdownGameSubsystems004b5da2. Mouse initialization's sole decoded
direct caller is InitializeDirectInputSubsystem00434fb6; subsystem
initialization also has lazy input-device entry paths.

If shutdown were followed by successful mouse reinitialization while
00436930 remained registered, lookup would save that same handler as
its own previous callback.00436930 has no self-pointer guard, so a
later chain call would recurse. This is a conditional static consequence,
not a proven reachable sequence or observed failure. Window table
replacement/destruction and terminal lifecycle must be reconciled
before asserting it. Ghidra handler comment updated and saved.

## Ordinary main-loop exit ordering

Sole decoded direct ShutdownGameSubsystems caller004a3f48 follows
RunGameApplication's action10 exit. Ordinary continuation004a3f4d..
3f7c unwinds runtime cleanup and returns; it does not branch back to
the action loop or directly reinitialize input. The application's sole
decoded direct caller is005242de in RunGameWithOptionalStackWorkspace.
Thus the conditional mouse self-chain is not explained by ordinary
menu/race transitions in this loop. Indirect finalizer callbacks,
abnormal reentry and another application invocation are not excluded.
This narrows reachability while leaving the broad lifecycle item partial.
Ghidra shutdown comment updated; executable unchanged.

## Application wrapper invokes the game once

Full assembly00524290..5242ec calls RunGameApplication once at
005242de, then immediately calls FinalizeRuntimeAndExitApplication
004dfd04. If finalization unexpectedly returns, it restores the frame
and returns; there is no local retry/reinvocation. Sole decoded direct
wrapper caller is005158e5 in stack-runtime startup. Combined with
action10 terminal ordering, this closes the bounded ordinary local
shutdown-to-reinitialization question: neither inspected loop nor
wrapper supplies that sequence. Mutable hooks/indirect reentry and
delegated exit remain separate, so universal callback lifetime is
still partial. Ghidra wrapper comment saved.
