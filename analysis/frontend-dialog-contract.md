# Frontend dialog contracts

Bounded static assembly findings, persistent Ghidra nfs3.exe. Parent verified
Luna's caller reviews against complete setup instructions and localization
fast-path preservation. No runtime or binary modification.

## Verified timed-dialog callers

| Callsite | Count | Array | Duration (active worker iterations) | Policy | Context |
| --- | --- | --- | --- | --- | --- |
|00444c03 localized notice|1|00661090|550|1|NULL|
|00446c2a profile operation|2|006611a0|1024|1|NULL|
|004c4005 network connection|2|007d3664|333|1|NULL|
|0044eded postgame notice|1|006644c0|512|1|NULL|
|0044e193 fixed-duration notice|1|006644a8|1024|1|NULL|

These caller counts and durations are fixed positive; their pointer-array
addresses are nonnull and the corresponding slots are assigned immediately
before the initializer. Localization IDs for profile are0x41/0x1c7, network
12/11, and postgame0x114. Their <=0x7a2 LookupLocalizedText route explicitly
saves/restores EDX and leaves EBX/ECX untouched, preserving the prepared
arguments. The two one-line wrappers set arguments after localization.
This proves no actual text-content or dynamic shared-array ownership contract.
The five additional decoded callsites0043cf6e,00447989,004478a3,0043fdc5,
0044e6fa are reconciled below under direct-call setup; their local counts
are also established. This table retains the five named positive-duration cases.

## Established local behavior and remaining questions

Timed initializer00444a80 admits nonzero counts, not positive counts. It
returns path-dependent raw EAX and retains old active/mode/context on rejection
after clearing two fields. Duration INT_MIN remains negative and does not
auto-expire under poller00444b60's positive-duration test.

Expiry status4 reaches an optional callback with per-frame close BYTE1;
callback may clear it to veto closing. The veto alone does not reset time.
Choice initializer00444c20 also admits negative text/choice counts locally;
its mode>=4 admission test reads existing global state, not incoming mode.

Astra residuals: alternate-entry/indirect caller admission, policy identity,
actual clock delivery/wrap, callback and shared-array lifetime, dialog context schema,
layout/cursor bounds, and profile/list failure ownership. The broad frontend
item remains Open; the verified subset does not establish universal admission.


## Additional caller boundaries

Full assembly0043ce80..0043cf76 shows the0043cf6e notice path supplies
count3, array005f3dac, duration1000, policy1 and null context. Three
localized IDs0x1f0/1f1/1f2 populate its slots; their direct lookup path
preserves prepared registers. The containing function's UI purpose is not
yet named here; caller admission into that notice path remains separate.

Full assembly0043fda0..0043fdcb shows0043fdc5 supplies count2, duration0,
policy0 and null context. EDX is set00661090 before an incoming-ID lookup,
then an ID11 lookup. Follow-up assembly review of dynamic004d17b0 shows explicit EDX save/restore
at every normal return. Together with the low-ID path, this establishes
EDX00661090 preservation through both lookups, regardless of the first ID
route on normal return. The function is now named
ShowLocalizedTwoLineUntimedNotice in Ghidra with full contract comments. Zero duration forces initializer policy1 and does not
enter automatic positive-duration expiry; broader completion is unresolved.

Ghidra get_function_by_address reports no containing function for decoded
call instructions00447989,004478a3 and0044e6fa. This is an analysis-boundary
gap, not evidence the instructions are absent or unreachable. Recover their
enclosing control flow before treating raw nearby setup as a full caller proof.

PUSHAD/POPAD in0043fda0 preserves all incoming GPRs, including EAX;
the notice wrapper therefore has no intentional scalar result. This
argument/preservation question is resolved locally. Shared text-array
ownership, dynamic text validity and completion lifecycle remain open.


## Unassigned caller regions: bounded byte evidence

Persistent Ghidra read_memory bytes corroborated with local objdump decoding
without creating instructions/functions:

-00447873..a8 prepares two slots006611b8/bc, count2, duration256, policy1,
 context0; first slot is005591d4 and second is localized ID0x43.
-00447950..8e invokes005591cc indirectly, selects text ID0x42/43, then
 prepares array006611c0/c4, count2, duration256 and context0. Second pointer
 comes from EDI; CL policy is not established by this bounded region and
 the indirect call is a separate register/state boundary.
-0044e6c0..708 has a prologue and balanced return sequence; localized
 IDs0x1cd/1ce populate006644b8/bc. It passes count2, duration1024, policy1,
 context0 and subsequently returns literal2. Ghidra currently assigns no
 containing function, so no new function/type/name was created in this pass.

All three count setups are positive literals. Enclosing dispatch/provenance,
text-pointer validity and shared ownership remain open. The raw decoded
regions do not prove all incoming paths or function boundaries.


## Direct-call setup reconciliation

All ten decoded xrefs to00444a80 now have reviewed local count setups:
1 at00444c03/0044eded/0044e193;2 at004c4005/00446c2a/00447989/
004478a3/0043fdc5/0044e6fa;3 at0043cf6e. Counts are literal1..3 along
those setup paths. The earlier “outside verified subset” list is now
covered by the additional sections above. This resolves local setup count
values, not alternate entries, indirect calls, text-array validity or lifecycle.
EOL evidence comments at the three unassigned call instructions are saved
and read back without changing function boundaries.


## Operation-name dialog callback publication

Named00447a30 OpenOperationNameChoiceDialog after full assembly/table review.
Unsigned selectors0..3 publish005591cc/005591d0 callback pairs:
0→00446550/00446510,1→004468c0/00446950,2→00446a10/00446a90,
3→00446780/00446740. Larger unsigned selectors retain prior pair/prompt.
It copies source006fd2fc into005591d4 through NUL without local bound,
then calls choice initializer with textcount1, choicecount2, selection0,
initial text005591d4, limit10, mode0, context004478c0. The input limit10
does not bound the preceding copy. Ghidra name/comment saved.

The four005591cc targets have no recognized Ghidra function entries, so
the policy-register question at00447989 remains unresolved. This producer
map gives Astra exact targets and retained-state admission to investigate;
no operation identity, caller bound or runtime fault is asserted.


## Operation selector direct callers

All five decoded call references reviewed:0044e465 passes0,0044e488
passes1,0044e4a8 passes3,0044e6a8 passes2. The fifth0044781c reloads
005591e8; its sole decoded direct writer is00447a38 at dialog entry.
These wrapper setup paths select valid callback pairs, and retry reuses
the prior selector. Persistent Ghidra bytes corroborate the raw wrapper
regions; the recognized selector-one wrapper provides the same pattern.
Ghidra producer comment saved.

This narrows the invalid-selector concern to indirect/alternate admissions,
alias writes and initialization ordering. It does not establish a universal
selector invariant or callback lifecycle. The broader frontend item stays Open.


## Dialog clock producer

RunMultimediaTimerWorker0048eb90 waits on0079c17c, tests active0079c19c,
then INCs0079c1a4 once at0048ebd8 per serviced active iteration.
The timeGetTime delta is separately multiplied by1193 and accumulated into
0079c16c; that is not the counter read by the timed dialog. Thus duration
operational units are active worker iterations, not directly milliseconds.
The earlier unspecified-clock-unit wording means real-time conversion and
delivery cadence remain unproven. No fixed seconds value is inferred for
550/1024/333/512/256. Poller Ghidra comment saved after direct writer review.


## Nominal timer rate at startup

Assembly at004b5cca loads EAX=0x80 immediately before the startup call
004b5ccf to InitializeMultimediaTimerService0048eff0. Its interval formula
therefore requests128 pulses/second and sets16.16 interval0x7d000, exactly
7.8125 ms. This resolves the configured nominal rate, not actual delivery.
The worker-count clock can only be converted using that rate conditionally;
scheduling, suppressed wakes, shutdown and concurrent servicing remain Astra
validation work. Ghidra initializer comment saved with this distinction.
