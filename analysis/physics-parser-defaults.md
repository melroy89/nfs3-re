# Physics parser missing-field behavior

Static analysis of004b1380 and004b0bb0, with read-only installed resource
inspection. No modified assets, parser execution or live-memory writes.

## Empty input and incomplete input differ

Parser004b1380 returns zero at004b13ba for null input or zero byte count,
before clearing global seen flags or applying defaults. With nonempty input,
it counts seen slots at004b2157..004b2174; count other than80 calls
004b0bb0 in missing-field mode. Caller0042c2a0 ignores the return count.
This is not general field-value validation. Missing archive entry handling
also depends on global abort policy0056440c; continuation is not proved here.

Missing-field defaults scan slots0..79. Any missing slot72..79 copies all112
AI acceleration floats, replacing even sections already parsed. Seen flags
are not marked by this fallback. Full-default mode instead copies0x4ac bytes.

## Field79 destination discrepancy

Descriptor table004af3b0 maps slot15 to external11 and slot16 to external79.
The normal parser writes them to+1b8 and+1bc at004b16bc/004b16e3.
Default jump-table entries004b0aa8/004b0aac select004b0d99/004b0dab, but
both default handlers write+1b8, at004b0d9f/004b0db1. Therefore missing79
can overwrite a parsed11 with default0055fa30 while leaving+1bc unchanged.
Preserve this behavior in a faithful reconstruction; do not silently correct it.

[Installed header inventory](physics-default-field-presence.json) covers47
CARP profiles. Every one contains field79 and all AI sections67..74. This
provides no installed missing-header trigger; it does not prove all values
are valid, every header is accepted by the binary parser, or custom input is
unreachable. Ghidra004b0bb0 records the discrepancy and evidence boundary.

Initial full-copy default availability is resolved below. Remaining: source
lifetime/aliased mutation, malformed entry bounds, global shared-parser
ownership and abort-policy reachability across callers.

## File-backed default image

The full-copy source0055f874..0055fd1f is1196 initialized bytes in the
executable's writable `.data` section, file offset1434228. All bytes match
the persistent Ghidra image. [Retained bytes and hashes](physics-default-profile-image.json)
establish availability before race loading. Baseline values include mass1000,
gear counts8/8, idle750/redline8000 and both field11/79 defaults4.0. The
missing classification handler separately uses0055f3c8, so not every
missing-field source is asserted to come from this full-copy image.

A program operand search for55f scanned341226 instructions and returned249
uncapped matches. Filtering address operands to this default image yields72
source reads/address loads, all in004b0bb0, with no direct destination write.
This bounded search does not exclude register-computed aliases, unknown
code or runtime changes in writable data. Initial default availability is
resolved; universal immutability and shared-parser serialization are not.
Executable SHA256 remains2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb.

## Installed header coverage and local ownership

[Expanded inventory](physics-header-coverage.json) matches all80 descriptor
slots exactly once in each of47 installed CARP files, using executable name
and numeric-ID substrings in first-match order. The maximum normalized line
is450 bytes against the2000-byte parser buffer. Files whose final byte is
neither LF nor NUL instead end in a literal space after CRLF; the reader's
final-byte omission therefore removes no numeric character in those files.
These bounds exclude neither numeric conversion anomalies nor custom inputs.

Resolved direct calls form the synchronous local chain0042c700 ->0042c350
->0042c2a0 ->004b1380 ->004b09d0. Only0042c2fe directly references the parser;
its enclosing vehicle loop does not overlap iterations itself. No local
locking protects shared cursor0055ed88 or seen array0055ed8c. Indirect
reentry and other thread entry paths remain unproved, so local ordering is
not a global serialization guarantee.

Named the parser `ParseCarPhysicsTextProfile`, header matcher
`MatchCarPhysicsHeaderToDescriptorSlot`, and line reader
`ReadNormalizedCarPhysicsLine`; retained original ABIs and interior evidence.

## Missing-entry abort versus continuation

Saved-image abort policy0056440c is1 and suppression callback00564414 isNULL.
00401010 nevertheless has real return paths: nonzero recursion guard returns
at0040120e; a suppression callback returning0 clears the guard and returns.
Otherwise normal cleanup reaches process termination. The handler preserves
ECX, so004ea290 retains its zero lookup result across returning abort paths.
Missing lookup clears output offset/length. Physics caller0042c2a0 ignores
lookup status; if allocation/copy return, size0 reaches the parser early exit
without defaults. Whether a suppressed failure is reachable during ordinary
race loading remains unproved. Comments saved at00401010 and004ea290.

Zero-length allocation refinement:004e1620 clamps working payload size0..7
to8 at004e165d, while negative requests take the invalid-size path. Original
size is retained for metadata. A zero request therefore need not fail. The
physics loader reloads the original zero byte count for copy/parser, so this
minimum allocation does not bypass the parser's empty-input early return.
Allocator capacity, copy backend and suppressed-error reachability remain
separate conditions. Ghidra004e1620 records the verified assembly contract.

Zero-byte copy is now verified across all three forward backends005033e5,
00503281 and0050356d. Alignment-prefix operations check count before payload
access; zero count traverses their size tails and returns without reading or
writing source/destination payload. The wrapper's overlap predicate cannot
select backward copying at count0. Together with minimum allocation and
parser early return, this resolves the local suppressed-missing-entry chain,
conditional on valid pool state and returning error handlers. Actual normal
race reachability of suppressed errors remains open. Ghidra004ea4f0 saved.

## Profile initialization before parsing

Race initializer0042c738..0042c741 zeros16 companion records at005eabe0
(stride0x4ac, total0x4ac0), and0042c79c/0042c7b0 selects the slot passed to
0042c350. The latter stores that pointer at vehicle+528 before parsing.
`ClearVehiclePhysicsWorkingState`004285f0 writes the vehicle's own+224..2e0
region; it does not copy the embedded profile defaults into the companion.
Thus empty parser input does not receive an implicit default profile from this
helper. Under stable valid-slot setup without aliased intervening mutation,
the destination starts zeroed. Suppressed missing-entry reachability and
subsequent tuning/dynamics on such input remain unresolved. Saved0042c350
comment records the local distinction.

## Temporary resource abort policy

Normal-return restoration is verified for the existence/open wrappers:
`CheckResourceFileExists`004e0e60 restores0056440c on both failed-open
(004e0e8e) and successful-close (004e0eae) branches.
`OpenResourceHandleWithAbortPolicy`004e2ab0 restores at004e2ac7 after its
004e28d0 call; its direct length-query caller resumes after restoration.

`LoadOptionalResourceFile`004e0fe0 saves at004e0fe4, clears at004e0fea,
delegates at004e0ff0 and restores at004e0ff5. Unlike a purely local flag
change, that dynamic extent includes audio top-up waits004e0edb/004e0f2e
and conditional post-load callback dispatch004e0f9d. The registered callback
00517f10..00518037 checks headers, pool size and CRC, resizes allocations,
and performs policy-gated error handling. Its inspected body/helpers contain
no direct physics-parser or nested resource-loader call. Startup setter
00518040 is now named `RegisterResourceFilePostLoadCallback`; static slot
references show registration and reads, without a reset/unregister write.

`SaveResourceFileWithoutAbort`004eebb0 similarly saves at004eebb4, clears
at004eebba, delegates004eeae0 at004eebc0 and restores at004eebc5. Its inspected
open/write/close chain contains no callback or audio wait. These findings
resolve ordinary wrapper restoration, but do not prove restoration following
nonlocal exits, serialization of the shared global, or absence of indirect
reentry through other paths. The normal physics loader uses mandatory004e0ec0
rather than optional004e0fe0; suppressed missing-entry race reachability
therefore remains open. Ghidra comments preserve these scope limits.

Audio-wait refinement: `WaitForAudioStreamTopUp`004ff7c0 includes a
main-thread wait loop calling `ServicePeriodicCallbacks`004e7630. That
scheduler dispatches due function pointers from16 records, guarded against
reentering each active record. Thus the optional-loader disabled-policy
window has a concrete indirect callback surface beyond the post-load hook.
This is a conditional static route, not evidence that a scheduled target
actually reparses physics or that the wait branch runs during race loading.
Known direct optional-loader caller paths do not connect to004b1380 in the
analyzed graph; unresolved indirect edges prevent a global non-reentry claim.

The wait also calls `RequestAudioStreamTopUp`004ff670, now named and
commented in Ghidra. This helper creates a completion event if absent,
clears completion and invokes009f6a50 under a thread-dependent critical
section; with no callback it marks completion and signals the event.
The observed installed audio-service path has another reader callback.
Additionally, timed async poller004f0d20 invokes a job-provided completion
pointer at004f0d77, and the wait uses alertable SleepEx. Consequently a
complete non-reentry proof requires job-target/APC provenance as well as
scheduler records. No active callback or APC target has been established
that reaches physics parsing; these surfaces remain conditional, not defects.

Async completion refinement: known type2 submitter004f1370 explicitly zeros
job+24. Type3 submitter004f1500 accepts ECX there, but its sole direct caller
004f15d0 clears ECX before delegation. Worker004f1820 routes zero-callback
jobs to status queue+38; only nonzero callbacks enter completion queue+54,
whose poller calls job+24. Thus these traced submissions do not demonstrate
completion-callback reentry. Arbitrary heap writers/alternate entries and
runtime queue state remain outside this bounded result. Named004f1370
`QueueAsyncFileSelection` and saved submission/wrapper comments in Ghidra.
