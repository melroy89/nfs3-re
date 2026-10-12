# Detailed analysis notes

Historical function-level findings and runtime evidence for NFS III. Earlier names and counts may be superseded by later corrections. Current scope, tool setup, status and the Astra backlog are maintained in `SCRATCHPAD.md`; saved annotations live in the Ghidra project.

Target executable SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

## Contents

- [Project and runtime foundations](#project-and-runtime-foundations)
- [Police, pursuit and traffic](#police-pursuit-and-traffic)
- [Vehicle physics and AI](#vehicle-physics-and-ai)
- [Networking and multiplayer](#networking-and-multiplayer)
- [Cars, archives and resource loading](#cars-archives-and-resource-loading)
- [Frontend, profiles and dialogs](#frontend-profiles-and-dialogs)
- [Input and replay](#input-and-replay)
- [Rendering, cameras and track geometry](#rendering-cameras-and-track-geometry)
- [Audio and music](#audio-and-music)
- [Historical contract context](#historical-contract-context)
- [Review, reconciliation and handoff](#review-reconciliation-and-handoff)

## Reading these notes

Notes are grouped by subsystem. Each third-level heading identifies a finding or historical pass. The historical contract context is retained as an archival section, rather than split into hundreds of small headings. Entries retain their original evidence and caveats. Earlier entries may be superseded by later corrections within the same topic. Current statuses and remaining Astra tasks stay in `SCRATCHPAD.md`; this file preserves the analysis history.

Existing finding headings are retained so inbound evidence links remain valid.

## Project and runtime foundations

### Memory-map evidence

Repaired the truncated Ghidra `.bss` map by adding the uninitialised `.bss.recovered` range `0070d000–00a1efff` with read/write permissions. Verified segment boundaries and existing labels/comments, then saved the project; executable SHA-256 remained unchanged. Runtime variable values are not available in this static database.

### Historical note: Wine runtime check

Wine runtime check: launched the patched game with the specified prefix/runner and sampled process memory read-only during a single-player race. Captured 80 samples (24 race samples, no read errors); observed eight vehicles, advancing ticks, moving positions, populated callback lists, and inertia values matching the static formula. Live mappings cover the repaired `.bss` range. No collision, pursuit, audio or multiplayer behaviour was validated. Sampler stopped without issuing a game-termination command; the game process was no longer present at the final check. Evidence: `/tmp/nfs3-runtime-E2iKSk/{summary.json,samples.jsonl,maps-72022.txt,wine.log}`; key corroboration is also recorded in Ghidra comments. These temporary captures may disappear.

### Historical note: Broad static pass

Broad static pass: established the Ticketed/Busted banner-selection branch from assembly, including indexed localization IDs omitted by current pseudocode. Added pursuit, AI and audio documentation with explicit confidence/unknowns in the project. No further game testing or live-memory writes. Static analysis remains active; outstanding work includes remaining AI heuristics, track/resources, rendering and multiplayer.

### Historical note: Memory-helper follow-up

Memory-helper follow-up: named and documented five byte/dword fill and zeroing routines from assembly, including their custom register arguments. Names/comments and refreshed pseudocode verified; project saved and executable hash unchanged. Four track-query stack locals were re-bound to names visible in current pseudocode; obsolete HASH entries remain in the database and are excluded from the local-variable total. No Wine run needed for this pass.

### Historical note: Periodic-worker/cleanup follow-up

Periodic-worker/cleanup follow-up: added six function names and five globals/tables; recovered the explicitly registered worker entry. Established event-driven callback dispatch and wake/close helpers, plus the 32-slot cleanup registry. Refined two earlier lifecycle comments to identify the wake event. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Upstream wake frequency, full callback ABIs and cleanup traversal order remain unresolved; details are in Ghidra.

### Historical note: Thread/event follow-up

Thread/event follow-up: added nine function names and one 20-byte thread descriptor; recovered the explicitly registered native thread trampoline. Traced suspended creation/resume, priority-code mapping, event polling, manual-reset creation, waits and signal/close helpers. Verified names/comments/refreshed pseudocode and descriptor type/storage width; project saved, executable hash unchanged. No Wine run. Full thread lifecycle, descriptor field +0xc and renderer lock preconditions remain partial; detailed evidence is in Ghidra.

### Historical note: Multimedia-timer follow-up

Multimedia-timer follow-up: added four function names and eight globals/tables; recovered the explicitly registered timer worker. Traced fixed-point interval scheduling, one-shot rearming, worker callback dispatch and shutdown. Distinguished the EAX event-signalling entry from its existing EDX entry and refined related comments. Verified all new/refined names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Timer delivery, concurrent teardown and accumulated clock units remain unvalidated; detailed evidence is in Ghidra.

### Historical note: Text-colour/traversal follow-up

Text-colour/traversal follow-up: added three function names and ten globals/table fields covering colour-pair preparation, indexed font blending and text traversal. Assembly clarified distinct interpolation divisors, decoder ordinal input, glyph bearings and newline/tab/missing-glyph handling. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full drawing callback ABI and nonzero colour-mode/cache producers remain unresolved; detailed evidence is in Ghidra.

### Historical note: Mask/native-utility follow-up

Mask/native-utility follow-up: added eight function names, including three recovered registered mask writers. Covered remaining pixel widths, font draw-mode selection, working-directory/disk geometry wrappers, literal-path attributes and process ID. Verified names/comments/refreshed pseudocode; project saved, executable hash unchanged. No Wine run. Documented literal24-bit byte ordering and absent local search-handle cleanup without runtime defect claims; detailed evidence is in Ghidra.

### Historical note: File-enumeration/error follow-up

File-enumeration/error follow-up: added nine function names and three globals/table fields covering shared search lifecycle, native/runtime error translation, runtime state access, bounded append and decimal parsing. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full search-buffer capacities, runtime record ownership and append fallback decoding remain partial; detailed evidence is in Ghidra.

### Historical note: Stream/clock follow-up

Stream/clock follow-up: added nine function names and two globals covering buffered character/line input, device checks, optional directory allocation and library clock/delay helpers. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Refill internals, clock units and small-capacity input contracts remain partial; detailed evidence is in Ghidra.

### Historical note: Descriptor/runtime-heap follow-up

Descriptor/runtime-heap follow-up: added seven function names and four globals covering refill consumption, access/share masks, descriptor capacity/tokens and runtime heap allocation. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Heap maintenance/arena ownership and synthetic-token lifecycle remain partial; detailed evidence is in Ghidra.

### Historical note: Runtime-arena follow-up

Runtime-arena follow-up: added eight function names and five globals covering arena allocation, initialization, sizing, collection and release. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Lock nesting and complete allocator ownership remain partial; detailed evidence is in Ghidra.

### Historical note: Heap-free/console/stream follow-up

Heap-free/console/stream follow-up: added eight function names and four globals covering arena coalescing, console handles/key filtering and tracked-stream flushing. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Documented allocation-pointer assumptions and the separate all-stream/masked flush entries; detailed evidence is in Ghidra.

### Historical note: Calendar/address/environment follow-up

Calendar/address/environment follow-up: added seven function names and seven globals/tables covering timezone/DST parsing, calendar normalization, console reads, RAS/local-address lookup and environment search. Assembly corrected missing arithmetic and allocation-base tracking in pseudocode; verified names/comments/refreshed pseudocode and global types/storage widths, then saved. Executable hash unchanged; no Wine run. Calendar boundary assumptions, callback contracts and environment-vector ownership remain partial; detailed evidence is in Ghidra.

### Historical note: Character-conversion/echo follow-up

Character-conversion/echo follow-up: added four function names and one global covering wide-to-multibyte conversion, bounded string conversion and console echo/output. Verified names/comments/refreshed pseudocode and global type/storage width; project saved, executable hash unchanged. No Wine run. Documented termination/encoding limits and unchecked console-output results; detailed evidence is in Ghidra.

### Historical note: Timezone/DST-consumer follow-up

Timezone/DST-consumer follow-up: added five function names and ten globals/buffers/rule records covering settings refresh, transition ordering, year-day calculation, seasonal selection and time comparison. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Native fallback retains existing transition rules; exact boundary and concurrency behaviour remain partial. Detailed evidence is in Ghidra.

### Historical note: Extended-float helper follow-up

Extended-float helper follow-up: added six function names and one raw table covering digit accumulation,96-bit normalization/rounding, decimal scaling and x87 encoding classification. Decoded table values offline from program bytes. Verified names/comments/refreshed pseudocode and table type/storage width; project saved, executable hash unchanged. No Wine run. Full formatter/parser contracts, rounding equivalence and extreme-input behaviour remain partial; detailed evidence is in Ghidra.

### Historical note: Float-formatting follow-up

Float-formatting follow-up: added seven function names covering fixed-width digit writers, magnitude formatting, shared continuation flow and fixed/exponent segment builders. Verified names/comments/refreshed pseudocode; project saved, executable hash unchanged. No Wine run. Documented deferred zero padding and continuation stack requirements; full consumer format semantics and rounding equivalence remain partial. Detailed evidence is in Ghidra.

### Historical note: Math-exception follow-up

Math-exception follow-up: added eight function names and five globals/tables covering exception records/callbacks, default numeric results, diagnostic output and runtime error stores. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Kept runtime-record size separate from adjacent operation-name table; selector bounds and callback/error contracts remain partial. Detailed evidence is in Ghidra.

### Historical note: Thread-state/stream follow-up

Thread-state/stream follow-up: added seven function names and five globals/raw records covering standard streams, buffered string output, zeroed allocations, thread-state initialization/resize and stack-bound estimates. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Thread-list/size invariants, TLS publication failures and historical stack estimates remain partial; detailed evidence is in Ghidra.

### Historical note: Runtime-resize follow-up

Runtime-resize follow-up: added four function names covering payload capacity, in-place resizing and allocation/copy fallback. Verified names/comments/refreshed pseudocode; project saved, executable hash unchanged. No Wine run. Documented partial growth before failure and attempted capacity restoration; segment ABI, invalid-input and rollback guarantees remain partial. Detailed evidence is in Ghidra.

### Historical note: Startup/thread-lifecycle follow-up

Startup/thread-lifecycle follow-up: added ten function names and two callback globals/tables covering initializer ordering, exception registration, thread-node registration/removal, TLS publication and startup hooks. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Initializer table supplies explicit callback recovery seeds; callback bodies, SEH handlers and failure/lifetime contracts remain partial. Detailed evidence is in Ghidra.

### Historical note: Runtime-initializer follow-up

Runtime-initializer follow-up: recovered and named ten table-referenced functions and five globals covering stream tracking, argument/environment setup, floating-point status and callback installation. Verified names/comments/pseudocode and global types/storage widths; project saved, executable hash unchanged. Detailed evidence and remaining callback/ownership questions are in Ghidra; no Wine run.

### Historical note: Argument/environment/signal follow-up

Argument/environment/signal follow-up: added 25 function names and 13 globals/tables, including four recovered callbacks. Covered command-line and integer parsing, inherited descriptor metadata, environment updates, code-page lead-byte tables, x87 setup and signal lifecycle. Verified names/comments/refreshed pseudocode and global types/storage widths; refined three initializer comments and saved. Executable hash unchanged; no Wine run. Full signal delivery, wide-environment ownership and floating-parser grammar remain partial; detailed evidence is in Ghidra.

### Historical note: Exception/finalization follow-up

Exception/finalization follow-up: added 29 function names and 16 globals/tables, recovering three registered exception/console callbacks and all seven finalizer entries. Covered signal dispatch, diagnostics, debugger interception, exit ordering, stream/environment cleanup, critical sections and TLS. Verified names/comments/refreshed pseudocode and global types/storage widths; saved project and confirmed unchanged executable hash. Typed embedded debugger marker as data and disassembled its skipped continuation; pseudocode still models the trap indirectly. No Wine run; full exception retry, callback ABIs and shutdown concurrency remain partial. Detailed evidence is in Ghidra.

### Historical note: Bootstrap/string follow-up

Bootstrap/string follow-up: added eight function names and eight globals covering process setup, standard descriptors, module paths, command-line duplication and register-based string/copy helpers. Verified names/comments/refreshed pseudocode and global types/storage widths; saved project, executable hash unchanged. No Wine run; static wide-path buffer capacities and startup failure contracts remain partial. Namespace inventory currently contains imported libraries and generated switch scopes, with no recovered game class names. Structure layouts, enums and callback types remain useful next targets; detailed evidence belongs in Ghidra.

### Historical note: Structure/worker follow-up

Structure/worker follow-up: created eight recovered runtime structure types and applied them to eight existing tables/list pointers. Checked packed sizes, field offsets/names, pointer links, storage widths and representative pseudocode; unknown fields remain opaque. A Luna medium read-only pilot supplied a countdown helper analysis; parent checked assembly/callers and named two related functions. Saved project, executable hash unchanged; no Wine run. Parallel workers analyse bounded disjoint scopes read-only; parent reviews and performs all mutations/saves. Detailed evidence and partial-layout limits are in Ghidra.

### Historical note: Race pause/clock follow-up

Race pause/clock follow-up: named twelve functions and thirteen globals, including one recovered registered timer callback. Covered pause entry/menu controls, action-history edge suppression, network pause request scheduling, divided clock counters and callback registration/removal. Parent checked Luna findings against assembly, retaining exact signed gates, local/playback request passthrough, callee-dependent register stores and silent callback-table capacity behavior. Names/comments, refreshed pseudocode, global widths and tag count verified; project saved, executable hash unchanged and memory map stable. Complete network menu actions, synchronization lifecycle, timer concurrency and unknown paused override values remain deferred. No Wine run.

### Historical note: Broad short-function pass

Broad short-function pass: added thirty names/comments covering pursuit links/assignment dispatch, opponent speed helpers, traffic parameter scaling, race cleanup/slots, sound wrappers and a fixed-size resource arena. Parent reviewed three Luna reports and corrected slot-count and field-owner interpretations against assembly. Names/comments and refreshed pseudocode verified; project saved, executable hash and memory-map bounds/block count unchanged. No new runtime test.

### Historical note: Setup/race-settings pass

Setup/race-settings pass: named twenty-five functions and three globals covering config loading/defaults, frontend transitions, selected car colors, lap-selection conversion, menu constraints, network settings serialization and callback service. Refined three earlier roster/UI comments. Three Luna workers supplied read-only reviews; parent corrected Boolean polarity, DWORD widths, color versus control-profile meaning and signed/unsigned boundaries against assembly. Names/comments, refreshed pseudocode, global widths and tag count verified; project saved, executable hash and memory-map bounds/block count unchanged. No Wine run. Detailed contracts and unresolved capacities remain in Ghidra.

### Historical note: Coverage priority

Coverage priority: Melroy questioned progress after more than five hours. Prefer broad passes over short, clear unnamed functions across subsystems; keep necessary evidence checks and descriptive comments, but defer deeper codec/math reconstruction to Astra. Function-name coverage is a count, not a percentage of source reconstruction; recovered entries increase the denominator.

### Historical note: Race standings/completion follow-up

Race standings/completion follow-up: named nine functions and one shared count covering ranked-vehicle access, mode-specific completion, participant status updates and performance milestone timing. Parent verified assembly and corrected the table identity and network-state polarity from the read-only worker report. Names/comments, regenerated pseudocode, count type/width and tag total verified; project saved and executable hash unchanged. No game testing. Detailed contracts and remaining physical units/mode meanings remain in Ghidra.

### Historical note: Stored database/comparator follow-up

Stored database/comparator follow-up: recovered and named the explicitly registered record comparator; named nine functions in total and two globals/map arrays. Covered version-header loading/default allocation, record eligibility/count queries, marker clearing across three lap categories and eleven track indices, summary strings and progress storage reset. Names/comments, regenerated pseudocode, raw comparator dispatch table, array types/widths, recognized count and tag total verified; project saved and executable hash unchanged. No game testing. Record insertion, complete schemas and caller bounds remain partial; static work can continue without runtime testing.

### Historical note: Buffered stream-control follow-up

Buffered stream-control follow-up: named five functions covering control-size calculation, initialization, node selection, synchronous memory copying and asynchronous read completion/refill. Parent checked the Luna review against assembly and corrected byte-string interpretation, register preservation and memory-source copy length. Names/comments, refreshed pseudocode and tag total verified; project saved. Custom register prototypes, completion-result provenance and status/queue contracts remain partial; detailed evidence stays in Ghidra. No game testing or binary changes.

### Historical note: Stream callback/control follow-up

Stream callback/control follow-up: recovered two explicitly registered callbacks and named seven functions covering open/close completion, file-operation result/release, channel configuration, threshold/gate updates and one-based queue-record lookup. Assembly establishes scalar operation results with preserved EDX and resolves the earlier full-read XOR provenance; updated that prior Ghidra comment. Names/comments, refreshed pseudocode, raw operation dispatch table, recognized count and tag total verified; project saved. Custom prototypes and remaining queue/status semantics stay partial. No game testing or binary changes.

### Historical note: Stream queue/cancellation follow-up

Stream queue/cancellation follow-up: named five functions covering file and memory sources, per-token cancellation, full cancellation and shutdown. Confirmed packet stride/tag packing, different idle-start contexts, skip-marker rewriting and callback-servicing wait. Names/comments, refreshed pseudocode and tag total verified; project saved. Source-buffer lifetime, name termination, packet traversal and callback progress invariants remain partial; details stay in Ghidra. No game testing or binary changes.

### Historical note: Reader/event-queue pass

Reader/event-queue pass: named four shared helpers for file/memory reader creation, DWORD reads, release and vehicle event queue append. Added reusable12-byte `FileOrMemoryDataReader` and24-byte `VehicleEventQueueRecord` definitions (not yet applied to a full vehicle type or custom-register signatures). Start-file payload reads are now confirmed as raw DWORD triples. Recorded eight-entry queue/drop behavior, fixed-point conversion, borrowed memory ownership and reader error-path uncertainty. Name/comment, refreshed-pseudocode and structure layouts verified; project saved, executable hash unchanged. No Wine run.

### Historical note: Playback/effect-backend pass

Playback/effect-backend pass: named nine helpers covering listener engine/surface layers, environment gating, pitch-scaled dispatch, packed position sampling, effect-type callback initialization, level-update stub, grouped voice levels and backend parameter application. Typed/named the primary effect-bus latch. Verified custom register/stack inputs, random sample suppression, signed sequence arithmetic, mapped effect IDs and grouped-level carry-forward against assembly; name/comment and refreshed-pseudocode readbacks passed, project saved, executable hash unchanged. Remaining packed-buffer and grouped-effect contracts are in the Astra backlog. No Wine run.

### Historical note: Pending static integration

Pending static integration: review Luna findings for car-choice filtering (`0043a6e0`), frontend layout helpers (`004633d0`, `00450970`), result/progression and hidden-code consumers (`00450fe0`, `0044e820`, `004524e0`), integer-angle helper (`004ea570`), remaining wheel/profile and vehicle control/response helpers (`004a97cb`, `004a9bc4`, `004ad2e1`, `004ad7a3`). These findings are not counted until parent verification and saving. Three Luna workers receive successive read-only batches; parent verifies and applies mutations.

### Latest verified findings

These findings are static unless explicitly stated otherwise; no new Wine test or executable edit accompanied this pass. Addresses refer to the target fingerprint above.

- **AI motion response — `00407fa0`, `ComputeAIVehicleMotionResponse`:** assembly-reviewed descriptive name and evidence comments are saved. Coordinate conventions, physical units and the effects of individual tuning fields remain unresolved; the name does not establish a complete physics model.
- **AI skill selection — `006fd4f0`, `g_dwAISkillSelection`:** the frontend descriptor at `005565dc` associates the `ai` menu key with this storage. Mode 1/2 builders overwrite it with 1. Consumers distinguish zero/nonzero scaling from exact-1 response gates: `00406584` applies approximately 0.9 acceleration scaling when selection is zero and the signed vehicle field at +8 exceeds 100; `0040eea3` consumes track-profile scaling. Exact-1 gates at `00404a73` and `00404bae`, and selection-minus-one tuning at `004047c1`, must be preserved. This is not runtime proof of the Aggressive menu setting's complete behavior.
- **Police profile assignment — caller `00474ba6`, initializer evidence `0047389e` / `00473911`:** the caller supplies total roster ordinal as the profile offset. Model variation is selected independently, including an every-fourth-police variant rule except under special flag 0x20. Roster/profile selection must not be conflated with the escalation stop counter.
- **Frontend descriptor initialization — `0044ab40`, `InitializeFrontendMenuDescriptorAndEntries`:** entry flags are restored before per-menu initialization; selection sentinel 100 and callback return propagation are documented. The custom register ABI remains a typing limitation.
- **Race speech admission — `004c8f90`, `SubmitRaceSpeechWithChannelCooldown`, and `004c9010`, `TrySubmitRandomizedRaceSpeechWhenChannelReady`:** names and comments distinguish channel cooldown from randomized readiness admission. Exact spoken-line identities remain unverified.
- **Police radio hooks — `0040a940`, `PoliceRadioSequenceNoOpHook`, and `0040aea0`, `PoliceRadioTargetScalarNoOpHook`:** complete assembly establishes no-op bodies, rather than missing decompiler logic.
- **Point effects — `0041c9f0`, `RenderPointEffectsForIndexedSceneRecord`, and `00491190`, `QueueProjectedBlinkingPointEffectQuads`:** indexed records have 16-byte XYZ/style layout; the style index is masked to 0xf into a 12-byte-stride table. A tick/phase/shift bit test suppresses emission before projection and linked-quad construction. The visual identity of these effects remains unverified.
- **Gear update — `004a90a0`, `UpdateVehicleGearFromRPMThresholds`:** the added plate comment complements the existing evidence at `004a91c8`; complete tuning-table bounds and exceptional RPM behavior remain unresolved.

Names, comments and subsystem/AnalystNamed tags were read back from the persistent Ghidra project. The final inventory contained 3,916 function entries, including 1,322 `FUN_*` names. This is an inventory, not a percentage of behavior understood. The project was saved; the executable fingerprint remained unchanged.

### Callback lifecycle and capacity audit

[Direct lifecycle review](callback-list-lifecycle.md) confines resolved insertion/removal callers to initialization/teardown and bounds ordinary single-initialization list occupancy at114/50 for valid N<=16, versus144 capacity each. Normal shutdown follows race-loop return; abort shutdown precedes gameplay. Category and force-feedback predicate differences remain explicit, with indirect/concurrent mutation and abnormal reentry unresolved. No runtime mutation or gameplay defect is claimed.

### Secondary ownership and caller-bound refinements

INI direct integer/string reader names fit within26 bytes includingNUL;
see[INI environment contract](ini-environment-contract.md). Screenshot capture
and worker formulas/local lifetime are documented separately; no local GDI+
shutdown wait proves actual overlap, see[screenshot lifecycle](screenshot-lifecycle-contract.md).
Window-handler search004fb300 is generic, with fixed stride8 and bounded
observed registration IDs; first-use lock and external admissions remain open.
00508390 is named InitializeDirectDrawWindowSession with proof comments.
See[window handler contract](window-message-handler-contract.md).

### Race preparation and sound service worker

Recovered61-byte worker0048ec40 as RunSoundServiceEventWorker and named its
callback/handshake controller0048ec80 SetSoundServiceWorkerCallbackAndWait.
Sound stop waits for callback-loop retirement before backend stop; full worker
and handler lifetime remains partial. See[sound shutdown](sound-driver-shutdown-contract.md).
Race preparation helpers now named/commented:00410aa0
ReleaseOptionalMusicStreamBeforeRace,004bc8e0
PrepareRaceRenderStateAndTemporaryArena,00434a90 ApplyPackedSceneColorToRenderer.
Their local sequencing is established; partial-init cleanup/resource ownership
and abort-return paths remain open. Screenshot encoder initialization also
requires a positive count and adequate76-byte-record extent; parent assembly
verified its unguarded first iteration. See[screenshot lifecycle](screenshot-lifecycle-contract.md).

### Receiver open failure and zero-length state

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

### Dynamic-text caller excludes special car IDs

LookupDynamicText004d17b0 accepts car-label IDs0x7bd..0x7ee,
subtracts0x7bd intoEDX and forwards that value at004d180e to
display getter004d1810. Intervening predicate00439cc0 calls
00439a50/00439c10; both preserveEDX. Hence this specific caller
supplies0..49 and cannot enter special500..599 branch. It does not
establish registry presence: missing-model predicate returns0 and
still reaches display getter, whose node+10 calculation has no
NULL guard. Other callers and runtime registry/cache lifetime remain
open. Dynamic-text Ghidra proof comment saved.

### Participant readiness does not validate car identifiers

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

### First-entry direct-start flag source

File-backed DWORD0055b03c is1. Its decoded direct xrefs are three
reads in RunFrontendSetup and sole write00473269 clearing0 before
ordinary menu. Therefore initial direct-route enable does not require
a separate command-line flag setter. Nonempty endpoint selects that
first-entry route; network failure exits before clearing it. This
resolves the missing initial producer question, not bulk/indirect
mutations, reentry or full runtime startup. Prior notes listing the
initial flag producer as unknown are superseded by this byte check.
Ghidra frontend comment saved; binary unchanged.

### Prepared-model validator signed-count boundary

00478100 accepts matching magic with signed count+19d0<=0 by skipping
the model loop (0047811a/20). Positive counts drive0x6c-stride accesses;
this helper has no file-length or pose-sample count check. Ghidra comment
saved. This narrows the ghost-loader admission question without claiming
malformed-input reachability or downstream safety. See[pose contract](pose-ghost-contract.md#immediate-validator-boundary).

## Police, pursuit and traffic

### Historical note: Hot Pursuit traffic check

Hot Pursuit traffic check: user enabled traffic On (only On/Off available). Read-only capture: 709 samples, including 205 race samples, no read errors; 12 vehicles including four traffic records. Observed ten traffic deactivations and ten reactivations across those records, corroborating activation fields. Police pursuit/arrest fields and controlled collisions remain unvalidated. Key evidence saved in Ghidra comments; temporary captures at `/tmp/nfs3-traffic-runtime-r4yvbdu4/`. Sampler stopped and game remained running; executable hash unchanged.

### Historical note: Follow-up after Melroy reported an arrest

Follow-up after Melroy reported an arrest: a read-only live snapshot captured police-category AI states and linked targets, but the arrest transition was missed; the player status was already zero and the race continued. Evidence `/tmp/nfs3-traffic-runtime-r4yvbdu4/post-arrest-snapshot.json`; limitations recorded in Ghidra. No memory writes or system-protection changes.

### Historical note: Continuous Hot Pursuit arrest check

Continuous Hot Pursuit arrest check: 1,310 read-only samples, no read errors. Captured police state 5→6 linked to the player at tick 3104, matching the statically identified stop path; player gained the AI-control flag while finish status stayed zero. Renamed four stop-processing helpers and refined the police state-machine name; saved detailed evidence and sampling limitations in Ghidra. Sampler stopped with the game still running. Temporary evidence: `/tmp/nfs3-pursuit-runtime-qq97qo1a/{arrest-summary.json,samples.jsonl}`. No instruction trace, memory writes or executable changes.

### Historical note: Follow-up pursuit pass

Follow-up pursuit pass: named five player/opponent stop-state and police cleanup routines, explaining player AI takeover and recovery through static control flow. Names/comments and refreshed pseudocode verified; project saved. Ticket/arrest/busted HUD message selection was unresolved at this point; see the subsequent static pass below. No new runtime test or binary changes.

### Historical note: Police/setup/stream-helper pass

Police/setup/stream-helper pass: named thirty functions and four globals/tables. Covered vehicle activation gates, police slot links/proximity/voice cooldowns, pursuit group state and assignments, driving decisions, radio gating, track-relative lane scoring, language lookup, mirrored record tables and STRM stream queues/tokens. Three Luna workers supplied read-only reviews; parent checked instructions/raw data and corrected threshold values, comparison directions, output offsets and unsupported participant-table interpretations. Names/comments, regenerated pseudocode, global types/array extents and tag count verified; project saved, executable hash unchanged and memory map stable. Detailed contracts remain in Ghidra. No game execution.

### Historical note: Lane-profile/pursuit follow-up

Lane-profile/pursuit follow-up: named five functions covering preferred track lane scoring, closing-speed penalties, scalar target approach, nearby speeding accumulation and observed police-target admission. Verified assembly and raw double coefficients; preserved FISTP rounding, signed/raw float-bit thresholds and unordered branches in comments. Names/comments, refreshed pseudocode and tag total verified; project saved. Personality/UI mapping, lane-bound invariants, offset roles and pursuit ownership remain partial. No game testing or runtime samples required.

### Historical note: Opponent proximity/player-police list follow-up

Opponent proximity/player-police list follow-up: named two functions for timed-selector expiry and target/proximity events; named one signed list count. Registration assembly proves the window list contains combined player/police vehicles, so refined its existing predicate name. Verified full assembly, audio dispatch table, event initializer and reset-count preservation chain; names/comments, regenerated pseudocode, count width and tag total checked; project saved. List capacity, audio parameter roles and event identity remain partial. No game testing or binary changes.

### Historical note: Traffic event/speed and result-formatting pass

Traffic event/speed and result-formatting pass: named three functions and two float display multipliers. Verified full assembly, exact double thresholds/scales, x87 comparison/rounding paths and shared-neighbor consumers; documented timed-event/audio-record updates without claiming event identity or audible effects. Names/comments, float types/widths and refreshed pseudocode checked; project saved, executable hash unchanged. Totals: 2,305 AnalystNamed, 2,194 StaticReviewed, 878 globals/constants. Traffic units/producers and result scalar/unit-label identities remain partial; no game testing.

### Astra live police follow-up

Read-only Wine sampling now corroborates the distinction between selectable human police and AI police profiles, human-police/AI-racer stop completion, and spike-strip deployment/removal. The spike-strip control binding resolves the identity of six formerly generic timed-track-event functions; names and supporting comments are saved in Ghidra. Detailed evidence and remaining limits are in [police-torque-runtime.md](police-torque-runtime.md) and [spike-strip-runtime.md](spike-strip-runtime.md). A subsequent racer-side countdown capture confirms four AI501/0002 profiles with torque[21]=0.0 and AI callback004088f0; a reachable full-drivetrain path remains unproven; no spike-hit effect was confirmed.

Player-racer lifecycle follow-up: the same local limit3 run captured first/second ticket completion with racer state0 and the third stop with stops3/state4, matching Melroy’s Busted report. Reciprocal links and group counters clear; the temporary AI bit clears on both nonterminal and terminal completion while callback pointers stay unchanged. See [police-torque-runtime.md](police-torque-runtime.md) and its retained runtime snapshots. Post-terminal reacquisition and other limits remain unresolved.

### Pursuit-assist reset ordering and cadence

[Reset contract](pursuit-assist-reset-contract.md) records strict-minimum participant selection, forced-call semantics, pre-guard segment changes, phase rejection and default directional offsets. Cooldown32 decrements on the even-tick contact callback; a priority21 player reset can be decremented at priority50 in the same tick. Runtime accepted/rejected placement and reference/world consistency remain unresolved.

### RUSHHOUR cap versus roster

[Traffic contract](rushhour-traffic-contract.md) separates menu-entered override survival from roster allocation and reactivation: ordinary solo allocation is7/6/0 for opponent selectors0/1/2 with traffic enabled, versus override cap15. Delay modifiers and tick1920 gate remain; failed cap checks retry every third eligible invocation. Runtime population/counter and menu availability remain unresolved.

### Police reset cooldown runtime corroboration

[Two captured inputs22 ticks apart](runtime/police-reset-cooldown-rejection.json) distinguish accepted placement from the second cooldown-rejected reset: reference changes before rejection, horizontal position does not relocate, cooldown does not restart, and reference later recovers. User observed one reset with quick taps. See [bounded conclusions and remaining scope](pursuit-assist-reset-contract.md).

### Spike contact, roadblock assignment and late escalation

[Spike-strip analysis](spike-strip-runtime.md) now separates a hit followed by recovery without arrest from a hit followed by pursuit and arrest. The retained [recovery capture](runtime/spike-contact-and-recovery.json) and [arrest capture](runtime/spike-contact-and-arrest.json) support the officer-target ownership distinction. Static contact geometry, wheel-effect bits and feedback gates are documented separately from live observations; exact contact timing and some visual mappings remain open.

In the subsequent racer-side run, Melroy heard a roadblock request but saw no completed roadblock. [Assignment samples](runtime/ai-roadblock-assignment.json) show paired command4 records and states8/9, then pursuit diversion; no sampled state10/11 establishes completed placement. The [reconstruction](roadblock-assignment-reconstruction.json) reproduces midpoint258 from the sampled pair and corroborates the cancellation window. Function00403b20 is named AssignRoadblockPolicePairAheadOfPlayer; its successful return means assignments installed, not a visible obstacle completed. Comments at004032e0,00403b20,00403ed0 and00403180 retain these distinctions.

The reorientation helper00403180 requires every scanned racer to pass an approximate-distance threshold of240 position units. It uses an axis-ordered max-plus-quarter-min estimate, not established metres or Euclidean distance. Sampled proximity supplies context only: the observed officer was in state9, so execution of the state10 gate is not proven.

[Scheduler samples](runtime/police-tactic-scheduling.json) corroborate stored group ticks11880/12208/12536. Static code requires a signed tick difference greater than320, updates the group timestamp before selection, and suppresses both selectors when the caller matches the announcement marker. Otherwise strip selection precedes roadblock selection, then support recruitment. The observed328-tick spacing is not a universal cadence. The support comment at004043a0 corrects an older argument interpretation: helper00404340 assigns command3 with span8, not command8.

[Late-run evidence](runtime/ai-strip-request-no-deployment.json) records the strip-request bit first observed at20663, but no active strip or police strip-assignment bit across11482 samples spanning6942 unique ticks. At21490 all sampled free officers fail the raw forward-gap test; the race then finishes. This explains a bounded missed opportunity, not every scheduler decision or a general deployment defect. Sampling was non-atomic. AI strip placement and completed roadblock behaviour remain unresolved; a longer racer-side race is the next useful test, with the sampler verified before gameplay instructions.

These changes affect saved Ghidra analysis metadata and documentation only. The executable remains unchanged; SCRATCHPAD.md remains the concise status and backlog index.

### AI spike deployment and player ticket corroborated

The longer race captured AI command0/span3 assignment, state3->4 deployment and an active strip at segment703 with arming tick25326. Melroy saw it and deliberately crossed: player tyre mask0->3 coincides with reported damage to both front tyres. The previously unassigned deploying AI officer acquired the human racer, despite the original strip assignment targeting the other racer. First-ticket completion clears the mask/link and restores control, with reset cooldown31 briefly present; stop limit9, result state0. This closes the bounded normal-direction deployment/player-hit/nonterminal-recovery case. Left/right bit order, quantified handling effects, reverse/seam deployment and completed roadblock placement remain open. See [full evidence and limitations](spike-strip-runtime.md#ai-deployment-human-front-wheel-hit-and-nonterminal-recovery) and [retained samples](runtime/long-pursuit-ai-strip-deployment.json). Ghidra00403d30/00401650 comments are saved; the sampler is stopped.

Release-reset refinement: player state7 calls00429100 directly at004059f5 after the group stop phase ends, without a strip-flag test. This differs from conditional helper004056e0 and explains how reset can occur despite finalization clearing flag40. Samples show controller7->2, category07->05 and cooldown0->31 with input_bits0 around completion. Ghidra00405740 and the focused report preserve this evidence and its non-atomic timing limitation.

Assignment-pointer lifetime refinement: strip contact clears officer+711bit08 before attachment, while attachment requires that bit to clear the original auxiliary group's+58. The prior group's pointer remains through26537, after the other racer's ticket completes and officer+730 clears. A nonzero+58 blocks a later selector invocation, but permanent suppression or an actual failed repeat attempt is not established. See [ordering and scope](spike-strip-runtime.md#contact-bypasses-one-assignment-pointer-cleanup-path); comments saved at00401650/004018b0.

### Reverse roadblock and strip attempts

[Reverse roadblock reconstruction](reverse-roadblock-reconstruction.json) distinguishes the actual record-minima pair2/3 from nearest pair3/4. Signed pair delta-559 passes the one-sided400 check, and midpoint969 matches the assignments. Ghidra00403b20 records this runtime witness. No completed roadblock was visually reported.

Three reverse strip assignments were overridden by pursuit before any sampled deployment. The first two clear the old group pointer during ordinary acquisition, corroborating the cleanup distinction from strip contact. All three show increasing segment movement away from their nearby lower-index assignment intervals. The full direction/speed chain remains unresolved; this is not proof of a universal reverse bug. [Third-attempt evidence](runtime/reverse-third-strip-attempt.json) includes the full capture summary:13821 samples,10820 unique ticks406..35359, no active strip observed. The sampler is stopped. See [focused report](spike-strip-runtime.md#third-reverse-attempt-and-capture-endpoint).

Follow-up resolves the local sign chain:004028e0 sets directionbit10 from negative wrapped start-current delta;00401430 flips cruise-speed sign once for reverse and once for that bit. With both set, the flips cancel. [Retained witnesses](reverse-assignment-direction-evidence.json) show this flag combination and movement away from lower assignment intervals. Comments at both functions are saved. Subsequent speed adjustment0040bff0 and full dynamics remain outside this bounded proof; no universal reverse-deployment failure is claimed.

Reverse U-turn observation: Melroy reports no visible turn-around by oncoming
police. This remains separate from the assignment sign proof: pursuit
helper00402910 explicitly adjusts for reverse, and context producer00401780
uses target direction/category fields. [Evidence boundary and follow-up
fields](spike-strip-runtime.md#reported-absence-of-reverse-track-pursuit-u-turns)
are also recorded in its saved Ghidra comment. A later radio announcement
occurred after sampling stopped and supplies no additional memory evidence.

### Successful reverse strip deployment observed

A fresh capture establishes an active reverse-track strip at360/lane7, owned
by master4 in state4. Human approach at segment366 has tyre mask0 and the user
reports proximity. This resolves existence of reverse deployment, not the
missed assignment-to-activation transition. [Evidence](runtime/reverse-active-strip.json)
and [limits](spike-strip-runtime.md#active-reverse-strip-finally-captured) are
saved; Ghidra00403030 records the distinction from earlier failed attempts.

Reverse contact/recovery is now captured: user-reported front tyres match
mask0->3 at73463, deploying officer joins existing group1->2, third ticket
under limit9 clears mask/link at74022, controller2/category05 returns at74025
with reset cooldown30. [Contact](runtime/reverse-strip-contact.json) and
[recovery](runtime/reverse-strip-ticket-recovery.json) are preserved; Ghidra
comments saved. Sampler stopped at paused tick74061. Initial deployment
transition, seams and individual left/right identities remain unresolved.

Final handoff pass: named004b0900 `IsCarPhysicsValueLine` after assembly and
character-table verification (first digit or minus, no complete numeric
validation). Saved abort return-path comments at00401010/004ea290 and
expanded physics-parser-defaults.md. Current state and next steps are in
[model handoff](model-handoff.md).

Parser ownership follow-up: confirmed companion profile initialization is
separate from vehicle working-state clearing; empty parse does not implicitly
load defaults. Named shared cursor0055ed88, presence-array start0055ed8c and
default-image start0055f874 with data comments, preserving existing widths.
Two Luna workers are independently checking resource callback and abort-policy
restoration boundaries; their conclusions have not yet been applied.

Scheduler registration follow-up: inspected the16-record timed callback registrar
and its seven direct registration sites. Named `InitializeAsyncResourceIO`
004f0da0 from win_async.c/initasync diagnostics and queue/thread setup, and
`StartPathfinderSoundStream`004e6f0c from SNDpathstartstream diagnostics and
stream initialization. Ghidra comments retain register ABI caveats, unchecked
path-copy bounds and unresolved failure/readiness conditions. Registration
sites also include raster, sound-context and network-discovery services;
this inventory does not prove that scheduled callbacks cannot reenter loaders.
Project saved; no binary or runtime writes.

Preparation import refinement:004465e0 snapshots0x176c bytes beginning
006fbb4c plus two12-byte ranges, optional-loads a resource, resolves its
primary car references and only then copies0x20f0 bytes to006fbb40 before
restoring the snapshots. Resolver-failure branch frees the loaded buffer and
returns0 without success-path restoration; inspected resolver writes are to
that buffer, so this is not evidence of global corruption. No local loaded
length gate precedes header access or the fixed-size copy. Recorded exact
branches in Ghidra; malformed-file admission and upstream bounds remain open.

Optional-loader caller naming: named00446800
`LoadAndResolveTrnPreparationResource` and004465e0
`LoadAndResolveKotPreparationResource`, using caller extension construction
and verified resolver/copy operations. Named00488a80
`LoadLocalCarArchiveShapeMetrics`: local car.viv shape payload,12 hotspot
pairs and derived angles/distances are observed; exact HUD component semantics
remain qualified. Saved Ghidra comments and original ABI limitations.

TRN/KOT admission follow-up: read-only caller reconstruction locates menu
load action00446c50, registered for loadnow at004474f3. Nonempty selected
paths receive TRN/KOT suffixes and call the named importers without an
intervening length query. Generic loader rejects zero size, but the observed
chain does not establish a minimum length before resolver offset reads or
fixed0x20f0 copy. This closes the local absence-of-check question, not actual
malformed-file behavior or global file provenance. Network roster callback
and ownership boundaries are consolidated in network-roster-admission.md.

Frontend continuation pass: recovered registered button render/update callback
004607c0 and named reverse selection00449f30 plus cursor positioning00449ea0.
Separated offline initializer's persistent racenow disable from network-only
render refresh and temporary selection policy. Full record binding and later
retention remain open. Spike/force-feedback pass bounds direct mask writers
to0..15 and confirms creation-time period is not a dynamic floor; hardware
consequences remain unvalidated. Reports and Ghidra comments saved.

### Pursuit member removal caller refinement

RemovePoliceFromPursuitGroup00401a20 skips a NULL group link. Nonnull absent
membership still decrements the count. Attach004018b0 establishes link plus
member append on the inspected path; detach00401a80 trusts this invariant and
preserves both on the non-player phase2 refusal. ResetFlaggedPolicePursuitLinks
004042b0 has one direct caller00401f1a in BeginPoliceStop: group count>1,
player-police category, zero stop counter and another selected member. It
clears links after removal, excluding an immediate ordinary second removal
through that reset path. Actual membership is not revalidated, and aliased
or stale state remains open. Saved refinement in Ghidra00401a20; no runtime
occurrence or general membership-safety claim.

## Vehicle physics and AI

### Historical note: Roster/physics/editor pass

Roster/physics/editor pass: added 48 function names and 13 globals; recovered one explicitly referenced comparator callback. Covered participant categories and roster builders, balanced setup choices, model eligibility/groups, tuning-to-physics setup, editor change detection/navigation and TGA capture helpers. Refined the model flag 0x10 name to its confirmed police role and typed/documented the existing race-mode selector. Verified all 49 new/refined names/comments/pseudocode and 14 new/refined globals; project saved, executable hash unchanged. No Wine run or capture execution. Exact modes 1/2 UI labels, several physics fields and editor callback bodies remain unresolved; detailed evidence is in Ghidra.

### Historical note: Triangle material follow-up

Triangle material follow-up: named three functions for interleaved versus separate batch passes and inline clipped fan submission; typed/named two mutable driver-depth scale/bias globals. Parent verified Luna findings against assembly, preserving pass flag consumption, DWORD/BYTE outcode differences and the unconditional second fan call. Names/comments, refreshed pseudocode and global widths read back; project saved, executable hash unchanged. Exact driver/material meanings, clipping equivalence and call reachability remain in Astra backlog. No Wine run.

### Historical note: NPS callback/contact/startup pass

NPS callback/contact/startup pass: named seventeen functions and ten globals/constants, recovering one registered incoming-message callback entry. Covered NPS seven-argument send wrapper and endpoint dispatch, track-plane clearance/contact basis/corners, height/contact reset, projections and angular-rate clamping, startup asset/window/path helpers, exception names and loading-progress timing. Three Luna workers supplied read-only reviews; parent checked assembly, corrected projection direction/constant interpretations, and confirmed 1/65536 from raw bytes. Names/comments, refreshed pseudocode, global widths and tag count verified; project saved, executable hash and memory map unchanged. No Wine/network execution. Detailed contracts and uncertainty remain in Ghidra. Further static targets include vehicle orientation integration and contact dispatch; defer complex cross-system semantics below.

### Historical note: Opponent lane-scoring follow-up

Opponent lane-scoring follow-up: named six functions covering ahead-vehicle speed limiting, behind-player profile gating, nonzero score boosts, clearance penalties, opening-progress windows and target/debug flagging. Verified assembly, signed gap comparisons, three-lane loops, raw0.5 multiplier and debug strings. Names/comments, refreshed pseudocode and tag total verified; project saved. Profile/UI mapping, score categories and target/latch roles remain partial; no live memory samples or game testing required.

### Historical note: AI timed-control follow-up

AI timed-control follow-up: named five functions covering latch set/toggle, expiry, low-speed/vector gates and driving-default initialization. Names/comments, refreshed pseudocode, raw comparison constants and tag total verified; project saved. Exact manoeuvre meaning, custom register inputs and field units remain partial; detailed evidence stays in Ghidra. Current Hot Pursuit/Aggressive/two-ticket/final-lap conditions are user-reported only: read-only process-memory access was denied, so no new runtime samples were captured.

### Historical note: AI speed-control follow-up

AI speed-control follow-up: named three functions covering braking magnitude, speed-indexed acceleration and signed desired-speed integration. Assembly and raw constants verified; names/comments, refreshed pseudocode and tag total checked; project saved. Documented weather/distance multipliers, unchanged profile-dependent braking coefficient, raw-bit branch and missing preserved-register propagation. Physical units and complete configuration/ABI remain partial. User reported arrest during the current run; no new runtime samples captured.

### Historical note: AI steering-vector follow-up

AI steering-vector follow-up: named five functions covering target displacement, motion prediction, current-track-point recovery and offset lookahead. Verified assembly, subtraction order, signed coordinate decoding and raw constants; corrected five output-pointer returns, while EAX/ESI register binding remains partial. Names/comments, refreshed pseudocode, tag total and one typed/named prediction constant checked; project saved. Physical units, target ownership and track-specific exception rationale remain unresolved. No game testing or runtime samples; executable unchanged.

### Historical note: AI steering/recovery dispatcher follow-up

AI steering/recovery dispatcher follow-up: named three functions and three heading scratch globals. Covered lane-neighbor tolerance, target/prediction/lookahead dispatch, recovery counters and heading error in turns. Verified assembly, reset-helper register preservation and raw thresholds; corrected scalar/pointer returns. Names/comments, refreshed pseudocode, global float widths and tag total checked; project saved. One reset branch copies an uninitialized local vector on that path; reachability and caller invariants remain unresolved, with no reachable defect established. Custom register binding and atan2 fallback remain partial. No game testing or binary changes.

### Historical note: AI control integration follow-up

AI control integration follow-up: named three functions and three integration/scale globals. Covered local/world control transforms, repeated motion scaling, damping/rebuilding world vectors and low-speed steering/acceleration. Verified assembly, transpose/dot contracts, raw damping constants and integration initialization; names/comments, regenerated pseudocode, global types/widths and tag total checked; project saved. Custom register binding, physical units, status identities and exact floating equivalence remain partial. No game testing or binary changes.

### Historical note: AI gear/controller selection follow-up

AI gear/controller selection follow-up: named two functions and two threshold constants. Covered gear/RPM search, countdown, integer smoothing and controller routing through track/profile/heading gates. Verified full assembly, speed-limit helper preservation and exact constants; names/comments, refreshed pseudocode, global float widths and tag total checked; project saved. No-candidate RPM/gear state and configuration bounds remain unresolved; no reachable defect established. No game testing or binary changes.

### Historical note: Vehicle effect/lifetime pass

Vehicle effect/lifetime pass: named and documented three functions covering fixed-position vehicle batches, timed type combinations and viewport overlay lifetime/fade updates. Named/typed two verified vector-carry constants and the two viewport counters. Counters count entries visited active before expiry, not survivors. Renderer pseudocode was inspected to identify consumers; full renderer assembly review remains pending. Ghidra holds detailed evidence; executable unchanged.

### Historical note: Vehicle-effect/queue pass

Vehicle-effect/queue pass: named the type-3 vehicle effect batch emitter, scene effect queue wrapper and depth-bucket command queue. Documented randomized vectors/lifetimes, custom register preservation, destructive linked-list insertion and ordered/unordered depth comparisons. Full assembly, relevant helpers/constants and name/comment/pseudocode readbacks verified; project saved. Alternate queue implementation and emitter lifetime-divisor reachability remain unresolved in Ghidra comments. No Wine run or executable changes.

### Historical note: Vehicle wheel-strip pass

Vehicle wheel-strip pass: named intensity calculation, material selection, contact update and stop wrappers. Connected the spatial-strip channel state to wheel contact positions/normals and vehicle flags; documented gating and material fallback. Full assembly/helpers/constants, names/comments and refreshed pseudocode verified; project saved. Cross-checked ambiguous x87 listing against raw bytes and objdump: bridge text can show FST for a qword FSTP, so use raw opcodes when stack semantics matter. No Wine run or executable changes; detailed evidence stays in Ghidra.

### Historical note: Wheel dispatch/contact-query pass

Wheel dispatch/contact-query pass: named material-gated strip/type6 dispatch, four-corner track-query refresh, scaled integer-phase sine and surface/speed sine scaling. Typed/named phase and corner-prediction scale floats. Verified full assembly/constants/helper contracts, name/comment/type/storage-width readbacks and refreshed pseudocode; project saved. Numerical exceptions and unresolved field meanings documented in Ghidra. No Wine run or executable changes.

### Historical note: Vehicle oscillation/runtime PRNG pass

Vehicle oscillation/runtime PRNG pass: named three vehicle pair/reset helpers and runtime seed-address/random/seed-set helpers. Distinguished the15-bit linear congruential runtime PRNG from game-effect PRNG; documented random signs/phases, raw-bit and x87 gates, plus runtime-record validity assumptions. Full assembly/constants and name/comment/refreshed-pseudocode readbacks verified; project saved. Oscillation integration remains follow-up. No Wine run or executable changes.

### Historical note: Vehicle oscillation/effect integration pass

Vehicle oscillation/effect integration pass: named five functions covering oscillation feedback/noise, impact-position effect stages, wheel-strip/oscillation reset, effect dispatch and local motion adjustment; typed/named two float constants. Recorded assembly-only unordered branches that differ from pseudocode, noise added after output clamps, phase countdown and reset boundaries. Names/comments, refreshed pseudocode, constant widths and tag totals verified; project saved, executable hash unchanged. Intermediate wheel-effect stages remain static follow-up. No Wine run.

### Historical note: Wheel material/effect pass

Wheel material/effect pass: named four functions covering masked speed effects, material-configured effects, four-wheel strip/effect orchestration and wheel-pair event dispatch; typed/named the averaging constant. Verified effect thresholds, ordered/unordered gates, stage overwrite order, zero-extended selector bytes and asymmetric pair event selection. Assembly, constants, name/comment and refreshed-pseudocode readbacks verified; project saved, executable hash unchanged. Remaining intermediate stage `0042ac40` is a static follow-up. No Wine run.

### Historical note: Contact/start-placement pass

Contact/start-placement pass: named the contact-effect/oscillation dispatcher and two start-placement loader/fallback functions; typed/named three float constants. Recorded contact classes, force-feedback/replay/event dependencies, raw-bit and unordered gates, plus twelve-record file/fallback storage. Corrected an earlier shared track-getter comment against assembly (table displacement has no extra +8; getter uses the shared selector). Name/comment, refreshed-pseudocode and constant audits verified; project saved, executable hash unchanged. No Wine run.

### GOFAST startup lookup verified

Menu-entered GOFAST with Diablo SV automatic/default tuning produces final-gear index45, beyond torque[0..40], selecting the adjacent maximum-velocity field. Static calculation from retained live inputs exactly reproduces vehicle+58c. See [runtime evidence and limits](gofast-final-gear-runtime.md). This establishes the startup lookup, not its visible driving consequences.

### Bounded controller and gear contracts

[Controller quotient review](controller-quotient-contract.md) verifies integer division before conversion, finite-state clamping and positive denominators in all47 installed CARP profiles. [AI gear review](ai-gear-fallback.md) adds local shift-helper bound preservation and a candidate guarantee for94 untuned profile/transmission cases at finite speed magnitude0..600. These close bounded contracts; global reachable speed/gear validity, tuning and visible controller behavior remain unresolved. Parent-reviewed annotations are saved in Ghidra.

### Best-lane display identified

[Display evidence](lane-adherence-display.md) resolves English text IDs to "in best lane" and singular/plural cone hits, names renderer00489900, and traces gated lane samples through the even-tick contact callback. Runtime presentation and recovery outcomes remain open.

### Opponent response countdown scheduler and startup reload

Assembly00404840 and its sole resolved direct caller00409c83 establish a state1-only decrement path, after activation and profile-reduction gates. Controller registration0042c876 uses priority21 on the even-tick list, dispatched at004c4a7f. With unchanged registration and uninterrupted eligible state1, the positive countdown decrements once per two simulation ticks; other controller states skip this call. This is a static scheduling contract, not a measured duration in seconds.

The competing50000 producer at0040488e precedes the decrement. Its strict tick window1152<tick<1216 admits31 even-tick opportunities,1154..1214. Each qualifying call reloads50000 and then leaves49999 for categorybit08. With valid segment indices, its strict segment window selects the final two track segments. It reads the first master vehicle's byte+50d but assigns the first player pointer as target; those identities must not be conflated across arbitrary rosters. Player input bit04 writes+50d at004314e7, while physics has additional writers, so a nonzero byte alone does not prove a key press. Positive countdown blocks the profile-based reload at00404a43.

The parsed-instruction search returned one immediate0xc350 producer and eleven operands containing0x6e4; aliases and bulk writes remain outside that search. The complete refinement is saved in Ghidra's00404840 comment. Runtime activation, effects and broader AI-profile invariants remain open. The current longer Hot Pursuit test targets police deployment, not this startup condition.

### AI501 full-drivetrain candidate via GO18

Verified menu/loader/roster chain: GO18 selects18, loader adds483 to resolve
501/pursuit0002, and regular session0 preserves the override while Hot Pursuit
strips it. This supplies a built-in runtime candidate without changing the
executable. Actual human profile and full-drivetrain consumption remain open;
see [test contract](police-torque-runtime.md#go18-built-in-candidate-for-full-drivetrain-reachability).
The route and limitations are saved in Ghidra0042c950.

GO18 provenance refinement:0042c2a0 reads physics text from the same global
archive loaded by the override-aware loader, then parses into[vehicle+528].
The substitution covers physics input, not only appearance; basename
compatibility, tuning and live execution still require verification. See the
[resolved source chain](police-torque-runtime.md#override-archive-supplies-physics-text).

Drivetrain004aaed1 is now named `UpdateEngineRPMAndComputeDriveResponse` with
a saved evidence plate. [Torque consumption gates](police-torque-runtime.md#full-drivetrain-entry-versus-actual-torque-interpolation)
separate neutral/shift/state bypasses from current-RPM, redline and idle
interpolation. This tightens the pending GO18 test without claiming live use.

### Physics missing-field defaults

[Parser/defaulting evidence](physics-parser-defaults.md) distinguishes empty
input from incomplete nonempty input and preserves the all112-float AI reset.
A newly verified destination discrepancy makes missing external field79 write
the field11 destination+1b8 instead of+1bc. All47 installed profile headers
include79 and67..74, so no installed trigger is established. Ghidra004b0bb0
is saved; malformed-input reachability and wider safety remain unresolved.

Physics parser follow-up names004b1380/004b0940/004b09d0 and establishes
local synchronous caller ordering. Expanded installed inventory matches all80
header slots in47 files with maximum normalized line450 bytes; numeric
validity and global serialization remain open. See [coverage and ownership](physics-parser-defaults.md#installed-header-coverage-and-local-ownership).

### Inverse-angle stack and domain trace

Two previously unnamed helpers now have evidence comments and descriptive
names in Ghidra:004f9482 ComputeX87AcosWithDomainHandler and0051a1ba
SqrtX87OrDispatchDomainError. Ordinary-domain x87 stack flow, endpoint and
masked-unordered branches, and selector1 domain-handler delegation are
established. Compatibility approximation, error policy and caller invariants
remain partial. See[x87 inverse-angle contract](x87-inverse-angle-contract.md).

### Contact recovery scheduling

The alternate-tick registration and active-vehicle gate are now traced.
Countdown+8a0 subtracts0..12 units per invocation and can reload; it is
distinct from+524 input cooldown. See
[contact recovery countdown](contact-recovery-countdown-contract.md).
Ghidra00429260 includes the scheduling proof; collision/placement outcomes
remain open.

### Mirrored normalizer direct loading caller

00478bb0 has one decoded call004dbc3b in004dbbe0. Full caller assembly
places it after environment loading00478340 and helpers0041d960/004bc870,
with abort polls separating stages. Nonzero004dbc28 poll skips normalization;
004dbc40 polls afterward. This establishes the local loading route only.
Source schema,17th stack value provenance, destination consumers and actual
reachability remain Astra work; no car-slot capacity is inferred. Ghidra
normalizer comment refined and saved.

## Networking and multiplayer

### Historical note: Network/preparation/dialog pass

Network/preparation/dialog pass: added 20 function names and eight globals/tables covering peer lookup, synchronization, control sends, roster changes, session cleanup, version compatibility, prepared-race car identifiers and dialog layout. Verified names/comments/refreshed pseudocode and all global types/storage widths; project saved, executable hash unchanged. Network protocol text is "27, 2.0", separate from About-screen 1.6.2. No Wine run; full transport semantics, callback bodies and preparation-buffer validation remain partial. Detailed evidence is in Ghidra.

### Historical note: Packet/callback/queue pass

Packet/callback/queue pass: added 17 function names and two globals/tables; recovered two explicitly registered connection callbacks. Covered packet dispatch/version receipt, connection cleanup, segmented sends and shared linked-queue operations. Verified all names/comments/refreshed pseudocode and both global types/storage widths; project saved, executable hash unchanged. Documented local receiver termination/length dependencies and a queue null-target return limitation without claiming runtime defects. No Wine run. Remaining dispatch handlers and layer internals can be followed statically; detailed evidence is in Ghidra.

### Historical note: Registered network-message pass

Registered network-message pass: recovered and named the remaining 18 handlers in the 19-entry control table, plus five helpers; added eight globals/records. Covered roster/sync receipt, input and vehicle updates, transfer controls and staged car-resource data. Assembly corrected a mixed float/unsigned-integer decoder that pseudocode represented as two floats. Verified all 23 names/comments/refreshed pseudocode and eight global types/storage widths; project saved, executable hash unchanged. No Wine run. Full message formats, transfer stages and upstream validation remain partial; details are in Ghidra.

### Historical note: Network-text/replication pass

Network-text/replication pass: added 20 function names and five globals/buffers. Refined packet type 10 from generic race data to confirmed queued network text; traced queue lifecycle, wrapping/history and panel rendering. Documented pending/display replicated-update records and their mixed float/integer fields. Verified all 21 new/refined names/comments/pseudocode and five global types/storage widths; project saved, executable hash unchanged. No Wine run. Text-history internals, replicated-field gameplay meanings and remaining transport/layer internals remain partial; details are in Ghidra.

### Historical note: Vehicle-replication correction pass

Vehicle-replication correction pass: added ten function names and four globals/tables. Connected outgoing packed vehicle updates to correction consumers, 20-row AI history checks, motion scaling and reposition/reset paths. Assembly confirmed gain0.03 and a one-sided negative-delta reposition threshold; field units and some flags remain partial. Verified all names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Further static work remains in related placement and transport/layer routines; details are in Ghidra.

### Historical note: Packet-layer/service follow-up

Packet-layer/service follow-up: added nine function names and one initialization flag; recovered the explicitly registered shutdown callback. Traced packer-chain dispatch, flattened-send fallback, shared-lock queue setup and periodic-service callback registration/cleanup. Verified names/comments/refreshed pseudocode and flag type/storage width; project saved, executable hash unchanged. No Wine run. Full callback ABIs and worker scheduling remain partial; details are in Ghidra.

### Historical note: Network race/menu follow-up

Network race/menu follow-up: named seven additional functions and eleven globals/constants; refined the existing type-8 receiver and applied a 12-byte NetworkPauseControlPacket layout. Covered host/client menu resolution, setup transfer with local-field restoration, synchronization cleanup, loading abort gates and synchronizing overlay. Parent checked Luna findings against assembly and English resource text, preserving exact marker paths, packet sizes, signed gates and duplicate rendering passes. Names/comments, refreshed pseudocode, global widths, packet offsets and tag count verified; project saved, executable hash unchanged and memory map stable. Complete setup field identities, protocol validation, lock ordering and original register prototypes remain partial. No Wine run.

### Historical note: Network admission/profile pass

Network admission/profile pass: named twenty-seven functions and five globals, adding a packed 31-byte pending-request structure applied to six records. Covered participant profile send/apply/readiness, setup synchronization, host admission/connection cleanup, request-ring operations, RAS loading/enumeration and local network probes. Three Luna workers supplied read-only reviews; parent checked assembly and corrected byte-string, copy-direction, lock-allocation and readiness interpretations. Names/comments, refreshed pseudocode, global widths, structure offsets and tag count verified; project saved, executable hash and memory-map bounds/block count unchanged. No Wine or network execution. Transport identities, payload schema and cross-system bounds remain partial.

### Historical note: NPS networking pass

NPS networking pass: named nine functions and thirty-three DLL export pointers covering export loading, connection/channel setup and cleanup, connection callbacks, endpoint lookup, service lookup and client roster initialization. Read back names/comments and refreshed pseudocode; pointer types and four-byte widths verified. Project saved; executable hash unchanged and memory map remains eight blocks with the same bounds. No Wine or network execution. Export signatures, callback event meanings and full record schemas remain partial. Car-resource transfer and track/vehicle worker findings were reviewed and applied in the following pass.

### Historical note: Stream packet/query follow-up

Stream packet/query follow-up: named five functions covering packet dequeue/release, refill resumption, pending-byte count, idle/empty predicate and total payload capacity. Verified assembly distinguishes scalar EAX from preserved EDX, total capacity from free space, and tag clearing before packet release. Names/comments, refreshed pseudocode and tag total verified; project saved. Packet lifetime, traversal bounds and non-atomic queries remain partial; detailed contracts stay in Ghidra. No game testing or binary changes.

### Historical note: Participant/model, networking and traffic pass

Participant/model, networking and traffic pass: named27 more functions covering model identifier/colour/flag adapters, network service operations, formatted numeric input, shared vehicle-axis damping, traffic target balancing/spawn placement and traffic police/lane predicates. Recovered one previously unrecognised network game-discovery callback and its comparison wrapper; its20-entry browser-list cap is distinct from player capacity. Parent verified assembly, corrected worker offset/arithmetic/ABI interpretations, read back annotations and refreshed pseudocode; project saved, executable hash unchanged. Detailed field offsets and remaining contracts stay in Ghidra. Three Luna workers continue read-only batches; parent alone applies changes. No Wine run.

### Historical note: Networking and numeric physics pass

Networking and numeric physics pass: named11 functions and typed/named13 float constants. Covered service candidate initialization, sorted game discovery, join/roster waiting, participant-list rendering and mode/magnitude/control-gated vehicle scaling. Parent verified full assembly and constants, preserving raw signed float-bit thresholds, x87 unordered paths and unused clamp dataflow; corrected several worker simplifications. Names/comments/types and refreshed pseudocode verified; project saved after a transient transaction lock, executable hash unchanged. Physical units, backend identities and complex controls remain unresolved in Ghidra/Astra backlog. No game testing.

## Cars, archives and resource loading

### Historical note: Track/resource/rendering static pass

Track/resource/rendering static pass: documented nearest-segment and surface-quad queries, reset placement checks, opponent catch-up balancing, resource/container fallback and native encoded handles, plus bitmap-text/quad batching. Typed track pointers and three-lane neighbour arrays; verified all 71 new names/comments/pseudocode, 21 globals and 15 locals. Detailed evidence remains in Ghidra; no game testing, runtime-memory writes or executable changes. Container format, complete track/query structures and several calling conventions remain unresolved.

### Historical note: Car registry/profile/CRT pass

Car registry/profile/CRT pass: added 50 function names and six globals/tables; refined three generic list routines to confirmed car-model names. Covered directory/FEDATA loading, identifiers, grouped display-name sorting, metadata cleanup, persistent per-player car records and buffered file IO. Verified all 53 new/refined names/comments/refreshed pseudocode and six global names/types/widths/comments; project saved, executable hash unchanged. Car flag meanings, profile payload and complete formats/ABIs remain partial. No Wine run needed; detailed evidence remains in Ghidra.

### Historical note: Resource/block/calendar follow-up

Resource/block/calendar follow-up: added seven function names covering RGB565 block expansion, packed-resource relocation/allocation, caller-buffer reads and local calendar/timestamp helpers. Assembly confirmed 4x4 block layout, custom register inputs and half-second rounding. Verified names/comments/refreshed pseudocode; project saved, executable hash unchanged. No Wine run. Full codec validation, renderer use of zero colours and timezone/DST helper semantics remain partial; detailed evidence is in Ghidra.

### Historical note: Car transfer/track/NPS registry pass

Car transfer/track/NPS registry pass: named thirteen functions and six globals/constants. Documented archive-member transfer/chunking, host/client synchronization, tilt gating, fixed-point track query/transform, heading conversion, basis-plane height projection and registry-selected NPS loading. Parent checked worker reports against assembly and corrected scale values using raw bytes: world-to-fixed is 65536, inverse scales are 1/65536, heading is 1024 units/turn. Names/comments, refreshed pseudocode and global types/widths verified; project saved, executable hash unchanged and memory map stable. No game/network execution. Detailed contracts and uncertainties remain in Ghidra.

### Historical note: Frontend validation/hover/resource pass

Frontend validation/hover/resource pass: named twenty-four functions and six globals. Covered dialog backdrop/text rendering, packed-rectangle hit tests, hover/sound policy, minimal timeout/full-opacity/reset helpers, 640x480 mouse-coordinate scaling, cursor texture construction and text-policy dispatch. Three Luna workers supplied read-only reviews; parent checked assembly and raw tables, corrected cursor-tag formatting and preserved AL-only results and required X/Y pointers in the scaling path. Names/comments, regenerated pseudocode, global types/four-byte widths and tag count verified; project saved, executable hash unchanged. Callback identities, packed table capacities and custom signatures remain partial; detailed contracts stay in Ghidra. No game execution.

### Historical note: Car settings/resource and physics follow-up

Car settings/resource and physics follow-up: named20 functions covering FEC colour settings, QFS existence predicates, registry directory enumeration, nonrecursive deletion wrappers, wheel scratch/magnitude/ratio helpers, network candidate-key equality and connection dispatch. Recovered the registered network-service cleanup callback. Parent checked full assembly and corrected misleading short-read/write and missing-file interpretations; detailed limitations remain in Ghidra. Names/comments and refreshed pseudocode verified; project saved and executable hash unchanged. No game testing.

### Historical note: BIG archive and lap-selector pass

BIG archive and lap-selector pass: named nine functions for memory-format identification, directory bounds, entry lookup, car physics-text loading and frontend dropdown geometry/formatting. Named/typed encoded lap selection and decoded race lap count as separate four-byte integers; preserved overlapping unaligned accesses. Parent verified full assembly, corrected legacy magic bytes and parser pointer/formatter ABI interpretations, read back names/comments/types and regenerated pseudocode. Project saved; executable hash unchanged. Current totals: 2,292 AnalystNamed, 2,181 StaticReviewed, 876 globals/constants. Archive bounds/error invariants, generic widget schemas and complete lap/track UI limits remain unresolved; no game testing.

### Historical note: Archive path/matrix/result pass

Archive path/matrix/result pass: named ten functions covering model/override VIV path selection, two signed matrix-triple rotations, selected-track/lap result-progress writes, three literal stubs and three native indexed-resource count/tag/address accessors. Parent verified full assembly and callers, correcting negative-selector acceptance, lookup-key versus progression-slot distinctions and container identity assumptions. Names/comments and regenerated pseudocode checked; project saved, executable hash unchanged. Totals: 2,302 AnalystNamed and 2,191 StaticReviewed. Resource format identity, matrix coordinate conventions and comparison-flag semantics remain partial; no game testing.

### Installed FCE palette extents

ReadCarFcePaletteFromArchive0049c700 reads member+7fc/4 bytes,
+800/256 bytes and+28/12 bytes after only a nonzero-length check.
Its fixed access therefore requires member length>=0x900; read/seek
returns are ignored. All86 car.fce members found in BIGF VIV archives
under installed GAMEDATA and gamedata_org have valid in-file extents
and satisfy that requirement; minimum length28084 bytes. Original and
active trees are counted separately, not deduplicated as unique models.

[Inventory](installed-fce-palette-extents.json) records paths, hashes,
offsets and lengths. This closes the bounded asset-extent question,
not runtime full reads or malformed/custom archive admission. Ghidra
0049c700 includes the extent proof and limitation.

### Installed VIV directory and member extents

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
[Inventory](installed-viv-directory-extents.json) records every archive
hash/header and member offset/length. Ghidra opener comment saved.
No runtime or binary modification.

### Member lookup and basename termination

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

### Direct basename queries

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

### Validated registry language query bound

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

### Transfer read-unit correction and archive-close ownership

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

### Immediate transfer caller ignores failed-read status

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

### Transfer setup failure admission and installed physics members

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

### Car-transfer receiver stage boundary

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

### Paired car-transfer emission partition

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

### Registry target retention after transfer

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

### Temporary directory cleanup name predicate

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

### Temporary cleanup traversal and result propagation

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

### Archived car display-string content

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

### Current loose metadata override check

A recursive filesystem check, independent of rg ignore rules, found
no regular localized FEDATA files under either GAMEDATA or
gamedata_org. All114 archive SHA256 values still match the directory
inventory used for the274 display-string extraction. Evidence is
installed-car-display-source-check.json. This closes current loose
override presence for these two roots only; alternate configured
roots, later writes, special IDs500..599 and live/transformed strings
remain outside the content proof. No full network format-safety claim.

### Special display-name ID extent

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

### Transfer eligibility is not model-ID admission

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

### Local profile selected-model provenance

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

### Command-line car selector admission

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

### Car selector startup ordering

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

### Stored car-key installed presence

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

## Frontend, profiles and dialogs

### Historical note: Shared helpers/frontend/clipping pass

Shared helpers/frontend/clipping pass: named 72 more functions and typed/named 20 globals/constants. Covered PRNG and x87 truncation, string formatting/parsing, diagnostic text buffers, pooled critical sections, periodic callbacks, allocator internals, file-table setup, viewport projection/clipping and frontend text alignment. All 72 names/comments and refreshed pseudocode, plus 20 global names/types/storage widths/comments, were read back and verified; project saved and executable hash unchanged. Exact register signatures, complete formats and some renderer depth conventions remain unresolved. No new Wine run.

### Historical note: Profile/tuning/persistence pass

Profile/tuning/persistence pass: added 62 function names and eight globals; recovered seven editor callbacks from registered pointers, bringing recognized functions to 3,828. Identified the seven-float saved tuning payload through CE editor tokens; refined three earlier function comments and two record-table comments. Covered .spc profiles, tuning/sliders, car metadata accessors and file-write/finalization helpers. Verified all new names/comments/refreshed pseudocode and all ten new/refined global names/types/widths/comments; project saved, executable hash unchanged. Static importer final-record and writer short-write limitations are documented in Ghidra; no binary fixes or Wine run. Full physics effects, metadata flags and some ABIs remain unresolved.

### Historical note: Editor/frontend follow-up

Editor/frontend follow-up: added 20 function names and two globals; recovered ten explicitly referenced editor entries. Covered Done/Cancel snapshot handling, car switching, defaults confirmation, editor initialization and shared button/drop-down/list/dialog helpers. Verified names/comments/refreshed pseudocode and global types/widths; project saved, executable hash unchanged. No Wine run needed. Network/prepared-roster candidates have read-only static evidence for a later pass; detailed annotations remain in Ghidra.

### Historical note: Raster-window/display follow-up

Raster-window/display follow-up: added ten function names and nine globals covering active-window selection, fallback allocation, clip filling, field validation, display-surface locking/restoration and backing cleanup. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full display-context layout, fill callbacks and recovery lifecycle remain partial; detailed evidence is in Ghidra.

### Historical note: Screenshot/cone/lifecycle pass

Screenshot/cone/lifecycle pass: named fifteen additional functions and seventeen globals/constants; recovered the explicitly referenced screenshot thread entry and its single-argument stdcall prototype. Added partial TrackConeSegmentState and ScreenshotCaptureHeader structures. Covered screenshot format/directory handling, capture ownership, BMP conversion and GDI+ encoding/cleanup, cone allocation/reset/release and race subsystem initialization/cleanup. Names/comments, refreshed pseudocode, global widths, structure offsets and tag count verified; project saved, executable hash unchanged and memory-map bounds/block count stable. Several overlap warnings disappeared after confirmed storage typing. Full geometry, register ABIs and concurrent screenshot lifecycle remain partial. No Wine run; detailed evidence remains in Ghidra.

### Historical note: Dialog/cursor/render-batch pass

Dialog/cursor/render-batch pass: named sixteen functions and eleven globals, including the verified 256-byte dialog text buffer. Covered timed/choice dialog setup, input codes, cursor selection and source-resource lifetime, and indexed render-batch initialization/reservation/submission. Parent checked worker findings against assembly, preserving signed-count gaps, negative cursor selectors and exact vertex offsets. Names/comments, regenerated pseudocode, global types/widths and tag count verified; project saved, executable hash unchanged. Custom register signatures and caller bounds remain partial; detailed evidence stays in Ghidra. No game execution.

### Historical note: Toggle-menu/tooltip/callback pass

Toggle-menu/tooltip/callback pass: named twelve functions and twelve globals, recovering three explicitly registered text-validator entries. Covered mode4 menu initialization/layout/rendering/hover, input and frame dispatch, tooltip delay/fade/resource tags and string validation. Three Luna workers supplied read-only reviews; parent checked assembly/raw tables and corrected row advancement, AL-only results and callback-status propagation. Names/comments, regenerated pseudocode, global types/four-byte widths and tag count verified; project saved, executable hash unchanged. Menu count remains a separate one-byte field; attempted typing was rejected by bridge prefix validation without a write. Detailed contracts stay in Ghidra. No game execution.

### Historical note: Profile/display/menu-parser pass

Profile/display/menu-parser pass: named twenty-seven functions and five globals, recovering the explicitly registered display-mode enumeration callback. Covered profile selection/deletion/replay preparation, display-mode records and dynamic labels, menu template/string/integer/float parsing, session restrictions, one-shot callbacks and tooltip reset/rendering. Three Luna workers supplied read-only reviews; parent checked assembly and raw strings, correcting callback-address, table-offset and policy-branch interpretations. Names/comments, regenerated pseudocode, global types/four-byte widths and tag count verified; project saved, executable hash unchanged and memory map stable. Detailed contracts remain in Ghidra. No game execution or file deletion.

### Historical note: Race formatting/record gate follow-up

Race formatting/record gate follow-up: named eight functions and four globals covering speed/time display, standings initialization, screenshot repeat state, temporary sorted-record queries and a mode/network frontend gate. Verified assembly, exact float factors and missing per-mode tests in pseudocode; names/comments, regenerated pseudocode, global types/widths and tag total checked. Project saved; executable hash unchanged. No Wine run. Record schemas, query filters and some calling conventions remain unresolved.

### Historical note: Participant record-query follow-up

Participant record-query follow-up: named nine functions and two sort globals; recovered the explicitly referenced comparator entry, leaving its name pending full review. Covered filter masks, sixteen-entry sorted index maps, participant score/name/car text accessors and network-state predicate. Names/comments, regenerated pseudocode, global types/widths, function count and tag total verified; project saved and executable hash unchanged. No game testing. Inclusive index/count checks and unresolved callback layouts are documented in Ghidra; no safe capacity expansion or reachable defect established.

### Historical note: Results snapshot/comparator follow-up

Results snapshot/comparator follow-up: named seven functions and two shared arrays, including the previously recovered comparator. Verified its raw jump table, all branches, direction handling and ascending final tie-breaker. Covered full vehicle-record snapshots, category lookup, localized rank text and result/progression dispatch; typed the two category counts and two sixteen-entry signed index maps. Names/comments, regenerated pseudocode, array types/widths and tag total verified; project saved and executable hash unchanged. No game testing. Embedded-pointer lifetimes, progression schemas and capacity bounds remain partial.

### Historical note: Progression/stored-record follow-up

Progression/stored-record follow-up: named eight functions and three pointers covering series score awards, elimination ordering, final result ranks, database save/release, track/lap-category selection, stored-record sorting/lookup and progress flags. Confirmed separate0x9ac participant snapshots versus0x31c stored records and sixteen versus ten map slots. Names/comments, regenerated pseudocode, pointer types/widths and tag total verified; project saved and executable hash unchanged. No Wine run. Score table/caller capacities, record schemas and persistence error semantics remain partial.

### Historical note: Record insertion/frontend text follow-up

Record insertion/frontend text follow-up: named seven functions covering by-value stored-record insertion/replacement, summary writes/reset, mutable text truncation and clipped-string rendering. Assembly resolves the insertion stack source despite incomplete BADSPACEBASE pseudocode and confirms exact RET cleanup. Documented ellipsis replacement without final width measurement and unresolved caller bounds. Names/comments, regenerated pseudocode and tag count verified; project saved and executable hash unchanged. No Wine run. Full record type/ABI recovery and text capacity invariants remain partial.

### Historical note: Frontend dispatch/file-helper follow-up

Frontend dispatch/file-helper follow-up: named five functions covering editable-string backend dispatch, input/font reset, trailing backslash, buffered file copying and current Setup descriptor predicate. Verified assembly, source/destination order, raw mode/name strings, register contracts and return statuses. Names/comments, refreshed pseudocode and tag total verified; project saved. Partial-open cleanup, read/close failure handling and complete renderer/descriptor layouts remain unresolved; evidence stays in Ghidra. No game testing or file-copy execution; executable unchanged.

### Historical note: Frontend token/menu-history follow-up

Frontend token/menu-history follow-up: named six functions and typed/named the shared current-menu pointer. Covered token extraction with three-space tab expansion, ASCII uppercase normalization and encoded sequence matching, descriptor/name access and history pop/default fallback. Verified assembly, exact replacement bytes, original consumed length and twenty-entry shift leaving the last entry unchanged. Names/comments, refreshed pseudocode, pointer type/width and tag total verified; project saved. Full paragraph ABI, token capacities, sequence-state bounds and history producer invariants remain partial; detailed evidence stays in Ghidra. No game testing or binary changes.

### Historical note: Menu history/string follow-up

Menu history/string follow-up: named four functions and two globals/arrays covering in-place ASCII uppercase, descriptor lookup, history push and history restoration by names. Verified assembly establishes twenty pointers,36-byte descriptor stride and case-sensitive lookup. Corrected uppercase helper scalar return type; pseudocode now exposes conversion, while EAX parameter storage and preserved-register propagation remain partial. Names/comments and global widths verified; project saved. No game execution during this annotation pass.

### Historical note: Frontend name/exit callback follow-up

Frontend name/exit callback follow-up: recovered three explicitly registered callbacks and named four functions covering both player-name prompts, exit confirmation and pending display recovery. Verified event branches, localized fallback IDs250/251, close-byte writes, action codes and display-mode reset. Names/comments, refreshed pseudocode, recognized count and tag total verified; project saved. Event enums, capacity/callback contracts and recovery trigger remain partial; evidence stays in Ghidra. No game testing required for these annotations.

### Historical note: AI low-speed tuning/window follow-up

AI low-speed tuning/window follow-up: named nine tuning floats and two functions for the last-listed-vehicle track window and profile-gated desired-speed reduction. Verified assembly, wrapped interval/constant-one helpers and raw5/0.9 constants; corrected two scalar returns. Names/comments, refreshed helper/controller/initializer pseudocode, float widths and tag total checked; project saved. Last nonNULL result replaces prior matches rather than accumulating; list category/capacity and motion-field meaning remain unresolved. No game testing or binary changes.

### Historical note: Camera overlap/orientation pass

Camera overlap/orientation pass: named and documented six functions covering sequential vehicle ellipsoid adjustment, vehicle angle offsets, target-facing basis construction and three turn-angle matrix rotations. Named/typed three verified float factors and the default reference vector. Updated pose-extraction comments to point to the reviewed helpers. Detailed branch/aliasing/numeric evidence remains in Ghidra; executable unchanged.

### Historical note: Physics profile-scale pass

Physics profile-scale pass: named the mode/flag-dependent reciprocal-scale routine and all26 verified float coefficients. Parent checked full assembly, six coefficient branches, overwritten-input policy, unordered floor selection and reciprocal/multiplier rounding. Names/comments, rawvalues, four-byte types and regenerated pseudocode verified; project saved, executable hash unchanged. Totals: 2,306 AnalystNamed, 2,195 StaticReviewed, 904 globals/constants. Physical scale, mode classes and flag identity remain unresolved; detailed formulas stay in Ghidra. No game testing.

### Historical note: Wheel/profile and attenuated-response pass

Wheel/profile and attenuated-response pass: named three functions and a four-float observed material-coefficient span. Covered signed/raw-bit wheel/profile updates, one police speech-selector wrapper and attenuated response scalar. Parent verified full assembly/constants, preserving original signed motion, coefficient reload differences, store precision, negative-zero return and unchecked table indexing. Names/comments, table type/width and regenerated pseudocode checked; project saved, executable hash unchanged. Totals: 2,309 AnalystNamed, 2,198 StaticReviewed, 905 globals/constants. Full table capacity, physical coefficient/response axes and speech selector identity remain unresolved; no game testing.

### Series continuation and eliminated-human contracts

[Series menu analysis](series-terminal-menu-contract.md) binds the postgame resource to its button handler and distinguishes enabled-key lookup from selected-entry dispatch. Result filters at004cf000/004cef80 and their composition at004cf090 are documented in Ghidra: surviving human results exclude numeric state2, while the separate state1 query is not human-only. Neither query can re-enable a terminal-track gate. Loaded-state bounds and actual final-round continuation remain unresolved.

Mode2 generation produces seven ascending track entries with track8 last, matching the endpoint at006fd40a. Eliminated humans remain registered, receive the model selected by canonical asset ID0x21, and acquire category bit0x80; normalization assigns result state2 and excludes them from the surviving-human query. The installed KNOC asset identifies the substitution as Knockout. This does not establish spectator controls or camera behaviour. Function comments preserve the producer, registration and result-copy evidence; full details and addresses are in the linked report.

### Display initialization does not add screenshot dimension bounds

Named InitializeRasterDisplayModeAndSurfaces00517620, verified in
assembly. It stores selector004bedcc result into current-mode0055fec0
before driver selection009ef958. On explicit driver failure it returns0
without restoring that index in this body. On success it constructs
surface records, copies their dimensions/format into configuration,
then calls ApplyDriverDisplayMode004beeb0 with the stored same index.
The latter's equal-current-index path bypasses differing-index range
validation. Selector fallback1 is not a proof of an eligible record
when no eligible mode exists. No maximum dimension/area bound is
introduced here. Driver-provided extents and caller failure recovery
remain unresolved; no malformed driver result was observed.

This narrows the screenshot producer audit without claiming a reachable
overflow or adding checks to the binary. Ghidra name/comment saved.

### Direct screenshot request admission

The decoded direct caller set of004c4480 is frontend input00451969,
loading progress00495274 and race loop004c5481. Capture004c452c has
only004c4499 as decoded direct caller. Request007a2778 is a Boolean
latch: its direct writes are producer004cdc80/004cdcb0 setting1 and
consumer004c44ac clearing0. A processing invocation attempts at most
one launch and clears the latch on success or failure. It has no
atomic consume, lock or outstanding-worker completion gate.

This closes the bounded request representation/caller-routing question.
It does not prove universal main-thread ownership or exclude indirect
calls/reentry. Sequential requests may launch another encoder without
waiting for the previous worker; actual overlap and initialization
concurrency have not been captured. Producer004cdc50 also has unusual
repeated-zero request behaviour already documented in Ghidra; event
mapping is still partial, so it is not described as ordinary key-up.
Ghidra consumer comment saved.

### Worker output-format ownership

Capture header snapshots width/height/depth only. Worker004e31d0
passes shared extension007a2780 by pointer to filename formatting,
then004e31ef separately loads it to choose BMP or PNG/JPEG. Direct
writes found are INI loading004b56a7 and normalization004c44e2. Thus
a format snapshot is not part of the per-worker capture object.

PNG/JPEG branches select encoder CLSID pointer0054d7a0/7b0 and JPEG
parameters0054d7c0 before writer004e3014. The writer uses supplied
arguments, without another extension load. A mutation between filename
formatting and dispatch could disagree, but actual reload/concurrent
mutation is not proven. This is distinct from shared GDI+ export/token
lifetime, which remains unresolved. No mismatch was observed. Ghidra
worker comment saved; binary unchanged.

### BMP filename admission and write completion

Worker filename probe004f91ec tests GetFileAttributesA success and
non-directory bit, without reserving the path. The later BMP save
004eeae0 uses AcquireResourceWriteHandle004e2ae0 flags0x232.
OpenNativeFileHandle004e3620 translates these to write access
0x40000000, share0, disposition2 and attributes0x08000080. Disposition2
is CREATE_ALWAYS: an existing writable file is truncated, whereas
CREATE_NEW would fail if it already existed. Share0 only protects an
already-open handle lifetime. [Microsoft CreateFileA contract](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea).

This closes the bounded BMP open-policy question: the existence probe
is not an exclusive name reservation. Actual collision/overwrite is
not observed, and concurrent workers normally use distinct atomic
counter values until wrap/reset/external interference. Nonzero short
resource writes are not locally rejected by004eeae0; the screenshot
worker ignores its return and always exits0. PNG/JPEG uses its separate
GDI+ path; this CREATE_ALWAYS proof applies to the BMP branch only.
Ghidra write-helper comment saved; no executable changes.

### Filename counter initialization and wrapping

The only decoded direct counter reset006fd1e0 is004c451b: ordinary
MOV0 when directory setup succeeds and DirectoryContainsNonDotEntry
returns0. That includes empty enumeration and search failure; it does
not derive a maximum existing screenshot number. Cached-ready path
rechecks directory existence and skips reset on success. Worker
LOCK XADD then INC uses low32(old+1), with no wrap guard or lock
shared with reset. Actual concurrent reset/encoding is not captured.

File-backed prefix0053f7f4 is .\screenshots\ (14 characters);
format0053f804 is nfs3_%04d.%s. Width4 is a minimum: signed32 decimal
can occupy11 characters. With a stable normalized3-character extension,
the combined name requires at most35 bytes includingNUL, fitting the
worker260-byte local buffer. This conditional calculation does not
prove arbitrary aliased format/extension mutation safe. Existing-file
probe retries names but does not reserve them. Ghidra initializer
comment updated and saved; binary unchanged.

### Mouse handler retains a prior callback independently

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

### Mouse cleanup and conditional reinitialization chain

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

### Ordinary main-loop exit ordering

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

### Application wrapper invokes the game once

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

### Frontend lap normalization boundary

Parent verified004cf160/190 and sole decoded decoder caller0044c295.
Reconciliation readsDWORD006fd4ae, SAR16 extracts the lowWORD selector
at006fd4b0; decoder compares AX and yields2,4,8, then CWDE/store006fd4b4.
Thus this particular post-reconciliation write belongs to{2,4,8}, even for
invalid selector words. Mode1 first encodes literal2 when signed006fd3b0>1,
otherwise4; mode2 encodes EAX2 and stores selector0. Other modes retain the
selector before decoding. Ghidra comment saved. This local normalization
does not prove every lap-count writer, network admission or per-lap storage
capacity. Whole-path limits remain unresolved for Astra.

### Timed-dialog local admission refinement

Parent verified Luna review of InitializeFrontendTimedDialog00444a80:
count admission is nonzero-only, not positive, plus nonnull text pointer.
Rejected calls clear00558b0c/00558b38 but retain prior active/mode/context.
EAX is input count on rejection and forwarded00443a90 output on acceptance,
not a normalized boolean. Duration INT_MIN stays negative after NEG and
forces policy1 by the subsequent signed test. These local facts are saved
in Ghidra; caller count/duration reachability, clock units/wrap and context
ownership remain Astra questions.

### Choice-dialog admission and raw return

Parent verified Luna findings at00444c20: text count is nonzero-only;
signed-negative values are not locally rejected. Choice count likewise
accepts negatives under its nonzero/signed<10 test. The mode>=4 check
reads existing00558c5c, not incoming stack mode. Rejection jumps00444f40
without assigning EAX, retaining the original text count and prior
active/mode/context after clearing two fields. Accepted path forwards
00444570's cursor-position result. It is not a uniform status boolean.
Ghidra comments saved; caller admission, layout bounds and state ownership
remain Open in the frontend contract.

### Timed-dialog expiry callback veto

Parent verified00444b60 and frame service00445f50 against Luna findings.
Positive-duration expiry returns4; frame service forwards it to optional
00558b18 callback with EDX pointing to a local byte initialized1 each frame.
Callback may clear it to suppress00445f10 dialog clearing for that frame.
Without a callback or with nonzero byte, clearing proceeds. The veto itself
does not update the timer/start; later repeated expiry depends on callback
and global mutation. INT_MIN duration remains nonpositive after initializer
negation and does not enter the expiry gate. Local routing is resolved in
saved Ghidra comments; clock units/wrap guarantees, caller domains and
callback lifetime remain open for Astra.

### Fixed-duration localized notice caller

Named0044e170 ShowLocalizedNoticeWithFixedDuration after complete assembly
review. It looks up incoming EAX text ID, stores pointer006644a8, then calls
00444a80 with count1, array006644a8, duration0x400, policy1, context0.
This caller has fixed positive count/duration; clock units, text-ID admission
and shared-array ownership remain separate. Raw EAX is forwarded and has
no established uniform status meaning. Ghidra name/comment saved and read back.

### Timed-dialog nominal scheduling rate

Verified startup MOV EAX,0x80 at004b5cca before timer initialization004b5ccf:
requested128 pulses/second, interval0x7d000 (7.8125 ms). This closes only
the requested-rate question. Active worker iterations remain distinct from
wall-clock time; delivery and concurrency guarantees remain open for Astra.
See [frontend contract](frontend-dialog-contract.md#nominal-timer-rate-at-startup).

### Race completion latch publication order

Full assembly CheckRaceCompletion004ceae0 skips nonzero007d369c;
a successful predicate stores1 at004ceb24 before finalizer004ceb2a.
This prevents ordinary synchronous reentry through the same function while
the latch remains set. No concurrency/reset-lifetime guarantee is inferred.
Unsigned race modes>3 retain EAX0 and skip finalization locally. Existing
completion predicates retain their distinct exclusion/network/status gates;
performance categories, tick-wrap admission and persistence remain open.
Ghidra dispatcher comment refined, saved and read back.

### Race completion latch is shared exit state

Direct writer inventory for007d369c includes initialization clear004c460f,
pause-action stores1 at004c4c7e/004c4cbf/004c4d0e/004c4d57, and race-loop
writes004c5434/004c54e5, besides completion004ceb24. Assembly verifies
the initialization clear and pause stores. Thus nonzero is not exclusive
evidence of successful finishing; prior “completion latch” wording describes
its local use, not a universal status enum. Other write operands, full reset
ordering, indirect mutation and concurrent ownership remain open. Saved
qualification in Ghidra004ceae0.

### Alternate exit path publishes after finalization

004c54e0 finalizes with EAX1 before004c54e5 stores exit flag1. ESI1 is
preserved by finalizer PUSH/POP. Thus the completion dispatcher's prior
publication is not universal. Ghidra qualification saved; event007a22dc
identity and complete lifecycle remain open. See[race completion](race-completion-contract.md#alternate-finalization-order).

### Vehicle-result record updater named

Named00450fe0 UpdateStoredRecordsFromVehicleResult after complete assembly
review: conditional record insertion followed by independent best nonzero
lap-summary update, EAX result bits2/4 and1. No disk persistence occurs here.
Comment retains participant/model/lap/string admission and first stack DWORD
initialization questions for Astra. See[stored records](stored-records-contract.md#vehicle-result-updater-named).

### Record-result mask consumer cells

004512f0 maps mask1/4/2 to kind0/2/1 and slots0/1. Leaf0044e7f0 writes
00664440+8*kind+4*slot, so these six decoded calls target only six DWORDs
through00664454. ECX preservation verified; visible labels and global
ownership remain open. Ghidra comment refreshed and saved.

### Pending result notification consumer named

Named0044ea60 ConsumePendingResultAnnouncementFlags after complete
assembly/jump-table review. Recorded numeric mode priorities and post-audio
flag clearing without success check. Gate register and global lifetime
remain partial. Ghidra saved; see[stored records](stored-records-contract.md#notification-flag-consumer-named).

### Result notification gate register dependency resolved

Full assembly00500e20/004ffc9c/00500e7c explicitly saves/restores ECX
on normal returns, resolving0044ea60 scan-bound preservation through
004e8fd0. Configured1/2 slots survive the gate; nonlocal/concurrent
contracts remain open. Ghidra and focused report corrected.

### Record qualification does not establish capacity admission

0044f960 accepts signed count<10 immediately, otherwise may accept via
NULL sorted lookup or smaller signed time. Its gate at00451075 therefore
does not establish0..10 for insertion004511d6. Actual count producers and
loaded-file reachability remain open. Ghidra insertion comment saved.

### Installed record database extents verified

Read-only active/backup records.dat inventory matches0x4197c/header16.
Assembly-derived33 blocks per file fit with active counts0..2 and backup
0..8, all0..10. Retained hashes and every offset/count in
installed-records-database-extents.json. Added saved/read-back Ghidra
comments at loader0044f510 and selector0044f670. This closes installed-file
extents/counts only; selector admission, actual reads, strings, custom files
and mutation remain open. SCRATCHPAD bounded closure added.

### Installed records: occupied-string termination

Verified current hashes and independently recomputed all occupied-record
string bounds: active3 records, backup127, all four ranges terminated.
See [stored records evidence](stored-records-contract.md#installed-occupied-record-strings).
Enriched the existing installed-file closure; broader records contracts
remain Partial. Binary and runtime memory were not modified.

## Input and replay

### Historical note: Input-ring synchronization pass

Input-ring synchronization pass: added 16 function names and 11 globals/tables, refining one earlier target-sequence name. Established eight participant rows with 128 four-byte samples each, corresponding ready flags, producer/consumer counters, lead throttling/correction and previous-sample fallback. Connected six-byte and 33-byte type-6 messages to ring processing. Verified all 17 new/refined names/comments/pseudocode and 11 global types/storage widths; project saved, executable hash unchanged. No Wine run. Exact packed action bits, complete scheduling policy and remaining race-data helpers are unresolved; details remain in Ghidra.

### Historical note: Text-history/input follow-up

Text-history/input follow-up: added 16 function names and seven globals, covering history allocation/reset/character rings, keyboard editing, bounded name-message composition, packet sending, panel frame/cursor helpers and character policy. Confirmed allocation capacities and the keyboard length86 limit from assembly; mode callbacks remain partial. Verified all names/comments/pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full frontend lifecycle and remaining replication/transport internals remain available for static analysis; detailed evidence is in Ghidra.

### Historical note: Console-input/parser follow-up

Console-input/parser follow-up: added four function names and four globals covering key availability, repeat/extended-key handling, decimal cursor parsing and leap-year checks. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Console failure/concurrency contracts and calendar epoch remain partial; detailed evidence is in Ghidra.

### Historical note: Parallel pose/visual pass

Parallel pose/visual pass: added fourteen function names covering selected visual records, packed track-relative positions, pose recording/playback and fixed-point quaternion conversion/interpolation. Two Luna medium workers provided read-only findings; parent checked assembly/callers and corrected mathematical and stack-argument interpretations before applying changes. Names/comments and refreshed pose pseudocode verified; project saved, executable hash unchanged. No Wine run; full register prototypes, endpoint contracts and numerical equivalence remain partial. The visual-slot projection consumer was reviewed in the follow-up below.

### Historical note: Pose/ghost IO follow-up

Pose/ghost IO follow-up: added seven function names and six globals; created the 18-byte `PackedVehiclePoseSample` type and applied it to the first entry of each pose table, leaving total capacities untyped. Covered position encoding, visual-slot projection, optional replay pose IO, ghost saving and playback enable/reset. Parent checked Luna findings and corrected the replay writer's incoming seek-offset contract. Verified names/comments, global types/widths, packed layout and refreshed pseudocode; project saved, executable hash unchanged. No Wine run. File round trips, recording index/count semantics, loader bounds and full mode lifecycle remain partial; detailed evidence is in Ghidra.

### Historical note: Replay/ghost lifecycle follow-up

Replay/ghost lifecycle follow-up: added six function names and three serialized replay fields covering ghost loading, recording initialization, default replay save/load and primary car-identifier conversion. Checked Luna findings against assembly, names/comments/refreshed pseudocode and global types/widths. Buffer initialization and ghost-load clear sizes establish intended storage of 14,400 packed samples per table; expanded both existing pose-table types accordingly and verified 259,200-byte spans. Size/count validation and nontransactional failure paths remain partial; detailed limits are in Ghidra. Project saved; executable hash unchanged, no Wine run.

### Historical note: Replay/setup follow-up

Replay/setup follow-up: added nine function names and three mode/save-eligibility globals covering replay initialization/finalization, ghost setup restoration, config snapshots and persistent-record status. Parent checked Luna findings against assembly and retained unknown field/state meanings. Verified names/comments, global types/widths and regenerated pseudocode; project saved, executable hash unchanged. No Wine run. Partial state changes on load failure, record-string contracts and replay event/control semantics remain documented for further analysis in Ghidra.

### Historical note: Replay codec follow-up

Replay codec follow-up: added eight function names and six globals/buffers; recovered the registered vehicle replay callback. Covered four-channel input sampling, signed-token RLE, stream cursors and playback application. Parent verified Luna findings against assembly and corrected register-preservation details. Names/comments/types/widths and regenerated pseudocode checked; project saved, executable hash unchanged. An offline branch model round-tripped three constructed patterns and showed encoded expansion beyond the wrapper's 128-byte reservation; this was not original-binary execution or a demonstrated game defect. Advanced capacity, malformed-stream and state-transition questions are deferred below; no Wine run.

### Historical note: Replay event/selection follow-up

Replay event/selection follow-up: added eight function names, four globals and the 116-byte ReplaySelectionCycleState layout. Covered event priority windows, pending priorities, timed selection and availability cycling. Verified names/comments, global widths, structure layout and refreshed pseudocode; project saved, executable hash unchanged. Exact view modes, CCM selection and transition contracts remain deferred below. No Wine run.

### Historical note: Replay controls and viewport follow-up

Replay controls and viewport follow-up: added nine function names and nine globals covering keyboard edges, mouse activation, manual/automatic selection, playback-rate indexing, cursor positioning, integer text scanning and viewport stores. Parent checked Luna findings against assembly, including scanner NUL termination and mixed register/stack output contracts. Names/comments, refreshed pseudocode and global types/widths verified; project saved, executable hash unchanged. UI transition timing, text-input boundaries and viewport adjustment rationale remain unresolved in Ghidra/Astra backlog. No Wine run.

### Historical note: Force feedback follow-up

Force feedback follow-up: named nine functions and four globals covering device selection, signed effect indices, Stop/Download/Unload, gain broadcasts and selected-effect resets. Parent checked Luna findings against assembly and matched GUIDs, method slots and gain property against Wine DirectInput headers. Typed the 16x4 signed index table and 30-interface pointer table. Names/comments, refreshed pseudocode, global widths and tag counts verified; project saved, executable hash unchanged. Device flag identities, effect creation/release and gameplay routing remain incomplete. No controller or Wine testing.

### Historical note: DirectInput effect creation/control follow-up

DirectInput effect creation/control follow-up: named seven functions and three shared globals; added a partial 136-byte DirectInputEffectRecord applied to the 30-record pool. Covered creation, start, stop-all, cached status, cooperative level and acquisition groups. Parent checked worker findings against assembly and local Wine headers, preserving unchecked index assumptions and group-result behavior. Regenerated pseudocode now uses named fields; the creator overlap warning disappeared after typing. Names/comments, global widths, structure offsets and tag count verified; project saved, executable hash unchanged and memory map stable. Full ownership, release/count lifecycle, envelope contracts and register signatures remain incomplete. No Wine or controller testing.

### Historical note: Force-feedback update/policy follow-up

Force-feedback update/policy follow-up: named ten functions and the 16-device interface table. Covered parameter conversion/update flags, four-effect setup, actuator enable/disable, three equivalent selected-effect stop wrappers, vendor-specific policies and grouped unacquire. Parent corrected worker flag/slot interpretations against assembly and local Wine headers. A worker disassembly call created one missing entry during intended read-only review; parent validated its full body and retained it. Names/comments, regenerated pseudocode, table width and tag count verified; project saved, executable hash unchanged. Driver success, ownership, unusual substring-helper decoding and complete register prototypes remain unresolved. No Wine run. Workers must treat disassemble_bytes as a mutation, not a read-only inspection tool.

### Historical note: DirectInput lifecycle/state follow-up

DirectInput lifecycle/state follow-up: named twelve functions and six globals; added partial 136-byte DirectInputDeviceRecord and 132-byte ExtendedJoystickState layouts. Covered subsystem/mouse initialization and shutdown, joystick enumeration/capability caching, raw-to-derived input state, cursor bounds, axis percentages and force-feedback reset. Parent verified worker findings against assembly and local Wine headers; retained exact failure, mask and percentage behavior. Names/comments, regenerated pseudocode, table widths, structure offsets and tag count verified; project saved, executable hash unchanged and memory map stable. Enumeration capacity, error cleanup, original device classes and complete register prototypes remain partial. No Wine or controller testing.

### Historical note: Force-feedback routing/mapping follow-up

Force-feedback routing/mapping follow-up: named ten functions and eight globals/constants, including the recovered registered callback. Covered binding-based target selection, eligibility, callback scheduling, clamped scalar conversion, rate-limited slot0 updates and preset dispatch. Typed13/26 packed binding tables and verified float/double constants. Parent checked worker findings against assembly, distinguishing preset side effects from predicates. Names/comments, refreshed pseudocode, widths, callback body and tag count verified; project saved, executable hash unchanged and memory map stable. Physical field identities, complete callback ownership, packed actions and numeric boundary equivalence remain deferred. No Wine run.

### Historical note: Control-mapping preset follow-up

Control-mapping preset follow-up: named thirteen functions and nine globals/constants. Covered seven model-specific presets, shared copy/default reset, mode initialization and three generic type fallbacks; typed default tables and verified model-string bytes. Parent checked worker findings against assembly, preserving packed-code ordering, conditional writes and mode1 reset asymmetry. Names/comments, refreshed pseudocode, table/string widths and tag count verified; project saved, executable hash unchanged and memory map stable. Action identities, complete register prototypes and caller/reset invariants remain partial. No Wine or hardware testing.

### Historical note: Input binding consumer follow-up

Input binding consumer follow-up: named twelve additional functions, recovered three explicit evaluator-table entries, added five globals and a four-byte CollectedPlayerInputSample type. Typed joystick samples and runtime binding storage; corrected two earlier function names because the pending list contains device indices, not action indices. Parent verified worker findings against assembly, preserving the valid device-zero case, twelve-slot runtime player stride, exact axis thresholds and keyboard side effect. Names/comments, regenerated pseudocode, table widths, structure offsets and tag count verified; project saved, executable hash unchanged and memory map stable. Fixed-binding overlap warnings disappeared after typing. Complete action identities, custom evaluator ABI and unusual class/index behavior remain deferred. No Wine run.

### Historical note: Shifted-nibble constructor pass

Shifted-nibble constructor pass: named twenty-two functions (sixteen builders, four position getters and two float block generators), recovered thirty-six registered entries. Verified constructor writes/widths, callback mapping, mono/stereo output, float/WORD variants, return sizes and RET16 cleanup. Getter callbacks are cursor accessors, not destructors; queued builders preserve the scalar voice-slot result/custom ABI. Names/comments and regenerated pseudocode read back; project saved, executable hash and memory map unchanged. Three Luna workers supplied read-only reviews. Sixteen recovered reader bodies remain unnamed; full buffering, continuation/loop policy, header bounds, fixed-point arithmetic and reentrancy need further review. No Wine run.

### Historical note: Dialog input/profile-description pass

Dialog input/profile-description pass: named twelve functions and five globals, recovering four explicitly registered input handlers. Covered choice/timed/edit/toggle-menu input, choice/edit rendering, cursor feedback and replay/ghost/tournament/knockout description helpers. Corrected an existing initializer comment against assembly. Names/comments, regenerated pseudocode, global types/four-byte widths and tag count verified; project saved, executable hash unchanged. Three Luna workers supplied read-only reviews; parent checked raw bytes and instructions. Detailed contracts remain in Ghidra. No game execution.

### Historical note: Frontend input/scale follow-up

Frontend input/scale follow-up: named five functions covering limited input/scan-code conversion, empty polling fallback, free-disk-space threshold and backend-adjusted text scale. Verified assembly, raw0.6 comparison constant and geometry-record field order; documented unsigned overflow policy, unordered scale comparison and preserved-EDX scalar results. Names/comments, refreshed pseudocode and tag total verified; project saved. Full input polling, backend scale presets and directory-failure reachability remain partial; details stay in Ghidra. No game testing or binary changes.

### Historical note: Effect pose-reader pass

Effect pose-reader pass: reviewed and named six fixed/floating pose readers, timed interpolation and quaternion helpers in the saved Ghidra project. Documented output preservation on inactive/finished records, distinct integer/float basis rotation, signed timing arithmetic and direct component interpolation without normalization. Named and typed the verified matrix multiplier constant. Detailed addresses, register contracts and numeric caveats remain in Ghidra comments; executable hash unchanged.

### Historical note: Scene pose constraint pass

Scene pose constraint pass: reviewed and named eight functions covering pose extraction, track-query refresh, matrix row sign changes, paired normal-offset probes, finite surface refinement and numeric upper/lower Y clamps. Assembly establishes the ten-step refinement limit and correct probe endpoint order that pseudocode obscures. Documented exact constants, query reseeding, output side effects and unordered comparisons in Ghidra. Globals/local naming counts unchanged; executable hash unchanged.

### Replay RLE malformed-token count bound

DecodeRle32ByteBlock004bca80 checks output count only between
complete runs. Entry count0..31 plus signed8 token absolute count
(max128 for-128) bounds one decoded channel to159 output bytes.
Witness:31 prior bytes then128-literal token. Exhaustive8192
count/token combinations are recorded in replay-rle-token-bound.json.
Zero token consumes one source byte and emits none, so output-count
termination does not impose a finite source-read bound. Wrapper
004bcee0 copies first32 bytes per channel but advances compressed
cursor by full consumed count; that copy does not bound decoder
scratch writes. Actual scratch extent/input admission and malformed
replay reachability remain unresolved. Ghidra proof comment saved;
no original-binary execution or binary changes.

### Replay encoder paired-stream partition and expansion

Encoder004bc9b0 partitions exactly32 source bytes into nonzero
repeat/literal tokens; final singleton is ff,value. Its unmodified
complete output therefore makes the paired decoder stop exactly at32,
excluding malformed-token overshoot. This is conditional on stream
integrity and correct cursor, not arbitrary replay-file admission.

Segment-cost dynamic programming for32 source bytes yields maximum
44 encoded bytes. A block of k singleton bytes followed by repeat
r>=2 costs(k+1 if k>0 else0)+2; distinct trailing k>=2 costs k+2
because final singleton is separate. Witness[0,1,1]*10+[0,2]
attains44. Four independently worst-case channels total176 bytes,
so the wrapper128-byte reservation is not a compression upper bound.
Actual aggregate buffer capacity/remaining checks and reachable input
patterns remain unresolved. Ghidra encoder proof comment saved;
static/offline arithmetic only, no original-binary execution.

### Replay stream end aliases initialized table

Initializer004bcbb0..c6 clears exactly0x1e000 bytes beginning
007a5f48; exclusive end is007c3f48.004bcbf6 then initializes
16DWORDs at that exact address to0xb, followed by600-row stride64
table setup. Thus adjacent space is live initialized table storage,
not demonstrated padding. Append guard checks signed cursor+128<N
once, then copies all four encoded channels without another check.
For ordinary nonnegative cursor, largest admitted value isN-129;
176 bytes conditionally end atN+47, affecting first47 table bytes.
This is an arithmetic upper bound, not proof that the cursor and
four worst-case channel patterns co-occur during gameplay. Source
constraints, reachable cursor residue and actual runtime corruption
remain open. Ghidra append proof comment saved; binary unchanged.

### Replay sample filter does not exclude expansion witness

RecordParticipantReplayInputTick004bd000 gathers four bytes via
0048f6a0, writes separate32-byte channels and flushes at cursor32.
Copy helper004c6840 reads current sample007d36f0+4*participant.
First three bytes are unchanged; fourth output=x&~oldLatch, with
newLatch=x&0xf2. Offline enumeration of all256 initial latch bytes
shows[0,1,1]*10+[0,2] survives unchanged: first0 clears the latch,
and1 is outside0xf2. Hence this filter alone does not exclude the
44-byte fourth-channel witness. Actual sample producers and
simultaneous worst-case four-channel gameplay input remain open.
Ghidra gather comment saved; no runtime testing or binary changes.

### Replay input sequence source mapping

ConsumeParticipantInputSequence004c67a0 masks sequence to127.
Four-byte sample address is007d3714+participant*512+sequence*4;
current sample destination is007d36f0+participant*4. Replay gather
reads that destination through004c6840. Producer004c6530 copies
four supplied bytes into producer&127, sets ready and advances
producer; callers include collected-player and network input paths.

When006fd50c is nonzero, consumer refreshes only local row006fd4f4,
but clears sequence ready flags for every configured human row.
Nonlocal current samples therefore retain previous values in that
branch; this is not an all-row refresh. Selector006fd3a0>1 skips
refresh, clearing and sequence increment. Alternate remote-control
paths and recording/consume scheduling remain unresolved. Consumer
Ghidra comment expanded/saved; no runtime or binary changes.

### Replay recording controller cadence

Initializer0042c400 installs replay callback at vehicle+0x5fc and
player controller00431430 at+0x600; AI bit02 replaces controller
and clears replay callback. Player controller0043145c invokes
replay callback before applying gathered controls. Controller list
007d3690 executes on even simulation ticks004c4a6a..7f; race
input consumption also checks even outer ticks004c52e1..f1 and
uses sequence=tick>>1. Thus half-rate input refresh does not
automatically imply duplicate recorded sample pairs: recording is
controller-driven as well. Exact outer/simulation tick alignment,
alternate callbacks and pause/playback cadence remain unresolved.
State0/1 records, other replay states apply playback. Ghidra callback
comment expanded/saved; no runtime or binary changes.

### Collected replay controls producer

CollectBoundPlayerInputsAndActionHistory0048f550 builds the sample
at0079c338 through binding callbacks00554e34. Channel0 is low byte
of arithmetic-shifted(callback1-callback0)/2; channel1/2 are low
bytes of callbacks2/3. Channel3 packs eight boolean action results.
Session1 collects two rows; others one. Dispatch0048fa10 appends
both rows for session1, selected local row for session0, and submits
other sessions through networking. These establish axis/action
producer roles, but callback ranges and active bindings remain open.
No simultaneous input-pattern reachability claim. Ghidra producer
comment saved; binary unchanged.

### Binding evaluator output ranges

Digital joystick button004316c0, POV004316f0 and keyboard004317d0
evaluators return0 or255; class0 returns0. Axis00431740 uses byte
bounds but doubled interior distances, so exact branch range is
0..508, not a universal0..255 clamp. Collector truncates axis
channels1/2 to low byte; channel0 takes low byte of signed half
difference. These ranges alone do not constrain equality-run lengths:
RLE depends on equality only, and binary[0,255,255]*10+[0,255]
has the same44-byte expansion as the earlier witness. Actual
configured bindings and simultaneous channel timing remain open.
Ghidra axis comment saved; no runtime or binary changes.

### Player control byte application

Assembly at00431478 loads DWORD0079c4a5 and arithmetic-shifts it
by24, extracting signed byte0079c4a8 into vehicle DWORD+518.
The overlapping DWORD symbol therefore reflects an instruction
access across adjacent bytes; it does not establish a separate
four-byte control value. Bytes0079c4a9/aa go to vehicle+504/505.
The input callback+5fc executes before these field updates.

Action masks04/08/80 become booleans at+50d/+50e/+512;40 cycles
+660 modulo3;02 requests ordinary or leader-relative reset according
to vehicle+200 bit20. User key names are not inferred from masks.
Ghidra controller header reconciled with these exact operations.
Static assembly evidence only; binary and runtime memory unchanged.

### Current versus requested shift state

Parent-reviewed Luna evidence distinguishes vehicle current/applied
selector+50b from requested+506. Caller004314a6/be loads+50b,
helper return is stored at004314c9 to+506, and transition processing
004a9bc4 compares these fields before updating+50b and saving old
current into+50a. Action10 advances and20 lowers, with advance
precedence. Three-state down maps every value>1 to1; only up or
no input can preserve a value>2. This corrects an initial worker
claim before annotation. Multiple controller writers prevent a
global range conclusion. Ghidra controller header saved.

Binding-map review corroborates existing annotations: configuration
records stride52 bytes while runtime player rows stride48 bytes.
Source fields7/9 map into history slots46/45, not the player sample;
player action slot4 remains zero after ordinary table initialization.
Fixed keyboard actions occupy slots24..55 and map to history bits
slot-minus24; these are separate from the eight player sample bits.
Concrete key/action names and full timing invariants remain open.
Static analysis only; no executable or runtime changes.

### Fixed action consumers, corrected against assembly

RunRaceLoop maps fixed slots31/32 to held bits7/8 and calls
004be970 with+1/-1 for viewport geometry. Slots39/40 are BOTH
held bits15/16, calling0048eb60 with0/1 for view parameters.
Slot44 bit20 rising edge calls004187e0 stream-volume toggle;
slot42 bit18 calls00418840 vehicle-effect-volume toggle. Scene
cycle00423b80 instead uses bit22 and is not installed by the
fixed-binding routine. Parent assembly review corrected worker
misassociation of adjacent calls before saving the Ghidra comment.
This closes these local slot-to-consumer mappings, while human
key labels, view units and broad camera/input contracts stay open.

Viewport scale follow-up: named two helpers and verified binary32
steps+/-0.1, ordinary[1,4] preservation, two-local-view dispatch
and bounds-derived extent/centre updates. Bit15 increases while
bit16 decreases the setting. See[Camera contract](ccm-camera-contract.md#local-viewport-scale-controls).
Ghidra annotations saved; static only, executable unchanged.

Camera coordinate follow-up: CCM keys and placement/query vehicle
segment indices use the active geometry domain, while reverse
progress is derived separately. This narrows the historical
coordinate uncertainty; visible reverse camera and later writers
remain open. See[Camera contract](ccm-camera-contract.md#shared-geometry-indices-versus-reverse-progress).
Parent-reviewed Luna evidence saved in Ghidra.

Constructor/weather handoff: verified and saved initialized request17
eligibility for modes1..7,11..13; named viewport scene initializer.
Weather initialization consumes a zero-extended BYTE modulo3,
separate from the weather-enable flag. Complex runtime transition,
aggregate arena and atmospheric identity questions are explicitly
deferred in model-handoff.md for Astra, following user clarification.
No binary changes.

Viewport classification helpers named:00481f90 tests enabled
configured rectangle spans against0.5;0048ccf0 combines that
predicate with exact scale1 into numeric classes0/1/2. Full assembly
and constant checked. Negative/unordered spans are not rejected
as invalid. Conservative names/comments preserve unresolved UI
meaning and custom register ABI; Ghidra saved. No binary changes.

Small helper pass: six parent-reviewed Luna candidates received
assembly-backed names and comments: global render-chain append
004bbf40, route-option processing004bc060, explicit-depth processing
004bc0b0, base-scene vehicle getter00422ba0, scene float-or-one
004227e0 and fixed action-history bit0 reader0048f920. Queue
wrappers clear their pair after routing/processing; this is not
proof of storage retirement. Scene float fallback treats either
signed zero as absent; unknown field purpose stays qualified.
Names/comments read back and project saved. No binary changes.

Render arena reset boundary verified: viewport entry resets cursor
to raw base, separating successive views but not proving backend
retirement. World-effect payload maximum96000 and configured8MiB
allocation recorded in[Render arena contract](render-arena-contract.md).
Aggregate/lifetime work remains for Astra. Ghidra header saved.

Viewport membership helpers named00423ab0/00423ae0: fixed25-DWORD
list predicate and guarded indexed-setting write. Membership guard
does not validate destination index. Original register ABI and
numeric list meaning kept qualified; Ghidra saved.

Frame/successor helper pass: named004bc650 frame viewport-state
finalizer and004bc670 dialog/mouse refresh. Also named00423a20
nonzero configured-value iterator and00423a60 successor-map
initializer: four candidate values,25 defaults, fallback2, then
previous-to-next links. Iterator preservesEDX; it does not return
an index there. Candidate bounds/duplicate policy and scene labels
remain qualified. Ghidra saved. A Luna audit confirmed existing
SCRATCHPAD camera/arena resolved-versus-open wording; no broad
closure justified. No binary changes.

Weather evidence index added in[Weather mode contract](weather-mode-contract.md):
initialized0..2 range and enable distinction are resolved; names,
active-count admission and wider pool ownership remain open for
Astra. Luna ledger audit found no justified broad closure.

Camera setting data labels: named four verified menu-choice-index
globals006fbba8/ac/b0/b4 and added descriptor/mapping proof
comments. They are choice indices, not direct scene-mode IDs.
Mapper pseudocode refreshed; project saved.

### Ghost loader local read-status admission

Assembly00477b50 confirms an unsigned inclusive0..0x41574 byte-count
gate, no local minimum length, and no test of reader return before the
car-model validator. Nonzero validator result publishes success; failure
retains prior loaded flag. See[pose contract](pose-ghost-contract.md#local-ghost-loader-admission).
SCRATCHPAD also reconciles previously established static human-role count
boundaries and non-player phase2 detachment refusal, while preserving their
runtime ownership/reachability questions. No broad closure is asserted.

### Ghost save extent uses published current index

00477d81 publishes current recorded index;004777d0 emits0x20f4+18*index
without+1. For unchanged nonnegative index this excludes its just-written
sample from the byte span. Pointer helper004779e0 has signed upper check
14400 only; recorder requests predecessor index too. Intended endpoint and
negative-index conventions remain open; no defect claim. See[pose contract](pose-ghost-contract.md#writer-extent-and-direct-index-producer).

## Rendering, cameras and track geometry

### Historical note: Packed-data/shape follow-up

Packed-data/shape follow-up: added ten function names and six globals/tables covering codec dispatch, header size queries, literal/backreference and run-length decoding, byte-pair expansion, and shape hotspot/comment lookup. Documented codec-specific optional headers, transient stack-backed dictionary pointers and local validation limits. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Remaining codecs and complete resource format validation still need analysis; details are in Ghidra.

### Historical note: Shape-depth/conversion follow-up

Shape-depth/conversion follow-up: added nine function names and four globals/tables; refined the existing shape-property table to confirmed pixel depths. Covered row-stride calculation, type-to-converter indexing, two 8x8 callback matrices and five colour-packing helpers with distinct alpha/zero rules. Verified names/comments/refreshed pseudocode and all five new/refined global types/storage widths; project saved, executable hash unchanged. No Wine run. Full converter mode/callback ABIs and clipped blitter internals remain partial; details are in Ghidra.

### Historical note: Palette-preparation follow-up

Palette-preparation follow-up: added nine function names and three globals/buffers covering embedded/default/scratch palette selection, keyed555/565 expansion, explicit alpha storage and RGB6/RGB8 triplets. Confirmed DWORD565-plus-alpha storage and the special alpha rule for entry255. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full type0x23 format, conversion modes and shared-state concurrency remain partial; detailed evidence is in Ghidra.

### Historical note: Shape-conversion/blitting follow-up

Shape-conversion/blitting follow-up: added six function names and four globals/records; recovered two explicitly registered drawing callbacks. Traced intermediate-format allocation/sentinel checks, clipping, row conversion through stack scratch and indexed565 drawing with index255 skips. Documented local cleanup/allocation and alignment-sensitive limitations without runtime defect claims. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Complete draw-context lifecycle, callback contracts and edge cases remain partial; details are in Ghidra.

### Historical note: Raster-surface follow-up

Raster-surface follow-up: added eight function names and thirteen globals covering clipping, pixel reads/writes, ARGB compositing, surface updates and shared offset-table allocation/release. Assembly recovered blend logic omitted by pseudocode and clarified format/caller constraints. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full draw-context lifecycle and upstream colour preparation remain partial; detailed evidence is in Ghidra.

### Historical note: Raster-arena/backend follow-up

Raster-arena/backend follow-up: added seven function names and three globals; refined the raster constructor with register arguments, embedded shape layout and offset ownership. Covered depth/type mapping, arena initialization/shutdown, backend acquisition/release and readiness checks. Verified all new/refined names/comments/pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Full backend contracts and fill callbacks remain partial; detailed evidence is in Ghidra.

### Historical note: Raster-fill callback follow-up

Raster-fill callback follow-up: recovered and named six explicitly registered row callbacks; added three globals/table fields. Covered packed-nibble, byte, word, RGB24 and DWORD fills, documenting count/alignment and shared-pattern constraints. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Upstream edge handling and complete blitter callback contracts remain partial; detailed evidence is in Ghidra.

### Historical note: Glyph/raster-cleanup follow-up

Glyph/raster-cleanup follow-up: added ten function names and seven globals covering glyph search, kerning, bounded text measurement, cursor positioning, palette matching and raster/surface destruction. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Direct glyph-probe bounds, decoder contracts and full text-control layout remain partial; detailed evidence is in Ghidra.

### Historical note: Glyph-drawing follow-up

Glyph-drawing follow-up: recovered three explicitly registered glyph callbacks and named two drawing helpers; added four atlas/metric globals. Covered packed4-bit compositing/colour writes,1-bit clipping and indexed lookup application. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Odd-width/source alignment assumptions and complete optimized-path equivalence remain unvalidated; detailed evidence is in Ghidra.

### Historical note: Viewport geometry follow-up

Viewport geometry follow-up: added nine function names, fourteen globals and a 32-byte ViewportGeometryPair type applied to seven records. Covered profile initialization, resizing, border coordinates/drawing, register-based record access and render clipping. Parent checked Luna findings against assembly and corrected the adjusted-export comment to distinguish source dimensions from endpoint coordinates. Names/comments, regenerated pseudocode, global widths and structure layout verified; project saved, executable hash unchanged. Original classes, driver primitive semantics and invalid-size reachability remain unresolved. No Wine run.

### Historical note: Display mode and projection follow-up

Display mode and projection follow-up: added ten function names, four globals and a 40-byte DriverDisplayModeRecord type with unknown fields preserved. Covered eligibility, enumeration, closest-area choice, mode application/reset and geometry-to-projection/clipping wrappers. Confirmed driver +0x3c is the highest valid index and first/second geometry groups feed projection/clipping respectively. Parent verified Luna findings against assembly, including outgoing stack arguments, signed division details and FOV half-angle conversion. Names/comments, regenerated pseudocode, global widths and structure layout checked; project saved, executable hash unchanged. Driver capability/callback meanings and malformed-dimension reachability remain deferred. No Wine run.

### Historical note: View projection dispatch follow-up

View projection dispatch follow-up: added eight function names and fifteen globals covering FOV selection, view geometry dispatch, attributed vertex projection, reciprocal seeds and window client geometry. Parent verified Luna findings against assembly/constants; retained the scalar/delegated depth-guard difference and unknown view-object meanings. Names/comments, regenerated pseudocode and global types/widths checked; project saved, executable hash unchanged. Rendering boundary equivalence is deferred below. No Wine run.

### Historical note: Weather pipeline follow-up

Weather pipeline follow-up: added twelve function names and eleven globals covering initialization, effective mode, segment/time intensity, history resets, particle/overlay command dispatch and shared command-chain helpers. Names/comments, refreshed pseudocode and global types/storage widths read back; project saved and executable hash unchanged. Preserved register ABI caveats and strict wrapped-segment endpoint behavior. Exact weather mode identities, pool lifecycle and renderer details remain unresolved in Ghidra. No Wine run.

### Historical note: Weather renderer/lifecycle follow-up

Weather renderer/lifecycle follow-up: added five function names, seven globals and two partial state structures (12-byte screen history and 20-byte overlay records). Typed both slot pools and XYZ positions. Parent checked Luna findings against assembly: the near-particle helper spawns an overlay rather than testing obstruction; update moves the maximum pool but reseeds the caller active count. Preserved nonzero lifetime decrement and exact reseeding behavior. Names/comments, refreshed pseudocode, global widths and structure offsets verified; project saved, executable hash unchanged. No Wine run.

### Historical note: Render arena follow-up

Render arena follow-up: added ten function names and three globals covering heap wrappers, arena initialization/reset/release, aligned allocation, cursor peek and command-pair concatenation/append. Names/comments, refreshed pseudocode and global widths read back; project saved, executable hash unchanged. Peek does not reserve/check requested bytes; allocation checks capacity after advancing. Caller boundary/alignment invariants remain deferred. No Wine run.

### Historical note: Render dispatch follow-up

Render dispatch follow-up: added thirteen function names and ten globals covering numeric state caches, HUD/scene state transitions, winding selection, command-list consumption and viewport pre/post stages. Refined existing state-setter comments. Parent checked Luna findings against assembly, including returned-next-node dispatch and callee-cleaned command pairs. Names/comments, regenerated pseudocode and global widths read back; project saved, executable hash unchanged. Numeric driver meanings, handler bounds and view-object identities remain unresolved. No Wine run.

### Historical note: Registered render-handler follow-up

Registered render-handler follow-up: recovered thirteen explicit table targets and named fourteen functions including their initializer; typed the six-slot handler table. Covered driver-selected quad/triangle batching, line variants, inline attributes, material dispatch and numeric state commands. Parent checked Luna findings against assembly. Names/comments, refreshed pseudocode, table width and recovered function count verified; project saved, executable hash unchanged and memory map stable. Specialized material passes and exact driver feature meanings remain deferred. No Wine run.

### Historical note: Quad subdivision follow-up

Quad subdivision follow-up: added five function names, three double constants and the shared weather projection buffer; introduced a partial 32-byte ProjectedRenderVertex type with unknown bytes preserved. Documented direct-quad versus two-triangle submission, strict depth thresholds and recursive subdivision. Names/comments, refreshed pseudocode, constant bytes, buffer width and structure offsets verified; project saved, executable hash unchanged. Custom register ABI and exact interpolation/boundary equivalence remain deferred. No Wine run.

### Historical note: Quad command producer follow-up

Quad command producer follow-up: named eight functions covering inline colored quad initialization, uniform-color projection, packed color blending, chain setup/export/flush and two eight-quad producers; typed/named three blend globals/constants. Parent checked Luna findings against assembly and connected selector-5 payloads to the numeric-state consumer. Names/comments, regenerated pseudocode, global types/widths and tag counts verified; project saved, executable hash unchanged. Scene identity, index/table bounds and geometry interpolation remain deferred. No Wine run.

### Historical note: Scene envelope/geometry follow-up

Scene envelope/geometry follow-up: named seven functions and eight globals covering selected scene position, color/parameter lookup, vector-strip extension, viewport rectangle bounds and command-stage export; added a partial 36-byte SceneColorEnvelopeRecord with unknown bytes preserved. Confirmed profile blend clamp to 1..100 before scaling by 0.01. Parent verified Luna findings against assembly, including unconditional two-vector copies and always-zero fixed-depth quad result. Names/comments, refreshed pseudocode, global widths and structure layout verified; project saved, executable hash unchanged and memory map stable. Scene identities, interval/index contracts and exact geometry/interpolation remain deferred. No Wine run.

### Historical note: Environment render-state follow-up

Environment render-state follow-up: named six functions and two tracking globals for gated numeric states 14/15, signed percent inversion/scaling, pair application and reset/getter contracts. Parent verified Luna findings against assembly, preserving register argument order, overflow behavior and reset without a state-15 driver call. Names/comments, refreshed pseudocode and global widths verified; project saved, executable hash unchanged. Driver meanings remain deferred. No Wine run.

### Historical note: Cone/path/math follow-up

Cone/path/math follow-up: named twenty-one additional functions and six globals/constants. Covered cone seed placement/profile offsets, in-place smoothing/surface setup, directory/path checks, byte/wide and ASCII case conversion, vector distance/cross-product/matrix transforms, six-word random-state seeding and display restore notification. Three Luna workers provided bounded read-only reviews; parent checked assembly and applied changes. Refined screenshot directory state as a boolean rather than an enumeration count. Names/comments, refreshed pseudocode, global widths and tag count verified; project saved, executable hash unchanged and map bounds/block count stable. Exact cone smoothing order, x87 boundaries and broader runtime ownership remain partial. No Wine run; detailed evidence remains in Ghidra.

### Historical note: Cone motion/runtime follow-up

Cone motion/runtime follow-up: named fourteen additional functions and thirteen globals/constants; recovered an explicitly referenced window-message comparator. Covered cone contact, tick catch-up, respawn and nearby rendering, allocation/free adapters, sound-library unload/control storage, translated file deletion, INI environment overrides and callback-based binary search. Refined the 80-byte cone record with velocity and motion/respawn countdown fields. Three Luna workers provided read-only candidates; parent checked instructions and corrected address-versus-offset interpretation in the search helper. Names/comments, refreshed pseudocode, global widths, structure layout and tag count verified; project saved, executable hash unchanged and map bounds/block count stable. Full cone effects/render ABI, boundary behavior and concurrent runtime ownership remain partial. No Wine run; detailed evidence remains in Ghidra.

### Historical note: Orientation/matrix/startup/viewport pass

Orientation/matrix/startup/viewport pass: named fifteen functions and three constants/tables. Covered turn-angle X/Y/Z rotation builders, angular-rate integration, matrix add/subtract/scale and inverse-square-root correction, required-directory checks, deterministic byte-table range selection, frontend shape resources and screen-quad submission. Three Luna workers supplied read-only reviews; parent verified assembly and corrected parameter extents, multiplication order and shape-handle indexing. Confirmed all ten inverse-square-root coefficients against their recurrence. Names/comments, refreshed pseudocode, global array widths and tag count verified; project saved and executable hash unchanged. No game execution. Exact overlay purpose, cross-system mode semantics and numerical equivalence remain partial.

### Historical note: Opponent/track-AI follow-up

Opponent/track-AI follow-up: named four functions covering behavior-profile lookup, selected-track speed scale, neutral speed multiplier and scalar offset correction. Assembly corrected a hidden x87 return in track scaling; applying verified float return exposes the table lookup and improves desired-speed pseudocode. Names/comments, refreshed pseudocode, raw8.0 constant and tag total verified; project saved. Exact Aggressive UI mapping, offset-field roles and preserved-register caller propagation remain partial. No live memory samples or additional game testing.

### Historical note: AI track-motion follow-up

AI track-motion follow-up: named four functions covering vector composition, heading-limited lookahead, packed track-vector projection and two-component direction dot product. Verified assembly, raw0.7 threshold and signed-byte/128 decoding; names/comments, refreshed pseudocode and tag total checked; project saved. Corrected lookahead scalar return and exposed projection x87 return; register inputs, original floating precision and generated calling-convention labels remain partial. No runtime samples or binary changes.

### Historical note: AI projection-controller follow-up

AI projection-controller follow-up: named the full projection-based controller and twelve mutable tuning floats covering offset/heading targets, correction gains, limits and low-speed scaling. Verified full assembly, initializer defaults and raw speed-scaling constant; names/comments, regenerated controller/initializer/caller pseudocode, float widths and tag total checked; project saved. Documented direct signed bounds, acceleration penalty, excess outputs and unordered branches. Physical units, config+248 and exact numerical equivalence remain partial. No game testing or binary changes.

### Historical note: Start placement/timed-track-event follow-up

Start placement/timed-track-event follow-up: named six functions and two placement constants. Covered player-police starting offsets, indexed placement records, input-edge latching, timed record initialization/clearing and police-radio dispatch. Verified full assembly, raw placement dispatch table, names/comments, refreshed pseudocode, float widths and tag total; project saved and executable hash unchanged. Exact event identity, endpoint units, record capacity and custom register prototypes remain partial. No game testing or runtime samples; detailed evidence stays in Ghidra.

### Historical note: Timed-event contact/geometry follow-up

Timed-event contact/geometry follow-up: named six functions covering eight-record contact candidate scanning, vehicle contact dispatch, police passage cleanup/pursuit response, clamped lane offsets and endpoint calculation. Verified full assembly, exact conversion/box constants, names/comments, regenerated pseudocode and tag total; project saved and executable hash unchanged. Contact acceptance uses conservative common-plane rejection rather than exact intersection; documented unordered comparisons and caller pointer invariants. Event identity, four contact-point roles, allocation capacity and full surface-query ABI remain partial. No game testing; detailed evidence stays in Ghidra.

### Historical note: Track surface/basis follow-up

Track surface/basis follow-up: named eight functions covering selective query initialization, fallback refresh/change flags, cached-quad reuse, basis/origin construction, height/state copying and fixed-point transpose/transform/projection. Verified full assembly, names/comments, regenerated pseudocode and tag total; corrected two EAX return types while documenting placeholder prototypes and unresolved register/stack storage. Cached-quad acceptance clears change flags without copying the new position. Project saved and executable hash unchanged. Basis normalization, search fallback policy, complete query-state schema and numeric range invariants remain partial; no game testing.

### Historical note: Track-query fallback follow-up

Track-query fallback follow-up: named three functions and one three-entry signed search-step table. Covered linked-descriptor selection with 120-byte save/restore, boundary/nearest-segment recovery and quad binding/conversion wrapper. Corrected an earlier vertex-binding comment: all four packed indices are signed16-bit, with verified reordered mapping. Names/comments, regenerated pseudocode, table width/raw entries and tag total checked; project saved and executable hash unchanged. Distance sentinel/tie behavior, link capacities, fallback XZ-only local data and error policy remain partial. No game testing; evidence stays in Ghidra.

### Historical note: Track surface rescan follow-up

Track surface rescan follow-up: named the seven-segment sequential strip rescan and one signed seven-entry incremental step table. Refined four existing comments for forward/backward vertex reuse, exact65536 conversion with current x87 rounding, and caller fallback. Full assembly proves the rescan consumes only input X/Z; the caller unwritten local Y is not read on this path. Verified retry order, partial failure restoration, raw constants/table, names/comments, refreshed pseudocode, table width and tag total; project saved and executable hash unchanged. Topology, material identity and index/capacity invariants remain partial. No game testing.

### Historical note: Track attribute/float-placement follow-up

Track attribute/float-placement follow-up: named four functions covering float-to-fixed height placement/state copying, four-vertex packed colour averaging, full material-byte lookup/default and side-dependent nibble2 predicate. Verified full assembly, exact conversion constants, caller stack order/RET16, names/comments, regenerated pseudocode and tag total. Replaced bogus64-bit predicate return/register parameters with verified32-bit scalar and four stack parameters. Float placement quantizes X/Z too; colour forces high byteFF; material getter preserves full byte. Project saved and executable hash unchanged. Byte/nibble gameplay identities and related track override/viewport predicates remain partial. No game testing.

### Historical note: Viewport track-side/scene follow-up

Viewport track-side/scene follow-up: named five functions covering offset-segment side checking used by weather particles, paired vehicle/view counter updates, mode dispatch and full/selective scene snapshots. Verified full assembly, resolver preservation, exact conversion constant, names/comments, regenerated pseudocode and tag total. Corrected scalar predicate and void dispatcher returns; register argument prototypes remain documented placeholders. Dispatcher preserves all GPRs and accesses its scene table before mode validation; no reachable defect established. Snapshot copies are284 bytes/full and56 bytes/selected. Project saved and executable hash unchanged. Mode/field identities, pointer lifetimes and capacity invariants remain partial. No game testing.

### Historical note: Viewport mode-selection follow-up

Viewport mode-selection follow-up: named four functions covering vehicle/pause override selection, base and override scene setters, and stored base-mode refresh. Verified full assembly, dispatch preservation, raw24-entry handler table, names/comments, regenerated pseudocode and tag total; project saved and executable hash unchanged. Documented priority order, modes3..6 dispatch before pointer replacement, differing mode19 marker policies and mode24 exit handling. Mode0 table entry is not assumedNULL; slot/mode bounds and visual identities remain partial. No game testing; detailed evidence stays in Ghidra.

### Historical note: Viewport loop/callback recovery follow-up

Viewport loop/callback recovery follow-up: named four functions and recovered two missing code entries from verified scene dispatch pointers. Covered one/two-viewport updates, effect-record allocation, a single-RET mode handler and stored transition advancement/completion. Corrected allocator and existing clear-helper32-bit scalar returns, retaining documented register-ABI placeholders. Verified full assembly, raw dispatch entries, names/comments, regenerated pseudocode, recognized count and tag total; project saved and executable hash unchanged. Effect definitions, negative-index caller invariants and transition fields remain partial. No game testing.

### Historical note: Registered view-handler follow-up

Registered view-handler follow-up: recovered two missing callbacks from verified mode17/18 table pointers and named three functions including the indexed effect-active predicate. Covered CCM view position/orientation selection, effect/fallback pose application and multiplayer participant reselection on effect completion. Verified full handler assembly, raw conversion constants, names/comments, regenerated pseudocode, recognized count and tag total; corrected the predicate32-bit return. Project saved and executable hash unchanged. Helper output validity, record schemas and effect/participant lifecycle remain partial. No game testing.

### Historical note: Camera selection/transition helper pass

Camera selection/transition helper pass: named and documented six functions covering nearest CCM camera selection, viewport transition preparation, float quaternion sign alignment/conversion, matrix basis rotation and fixed sine/cosine lookup. Corrected the selector scalar return representation; named and typed the complete 257-entry quarter-wave lookup table and a half-factor constant. Recorded strict selection distance/tie rules and signed raw-bit rejection semantics in Ghidra. Detailed evidence stays in the saved project; no executable changes.

### Historical note: Surface geometry/math pass

Surface geometry/math pass: named and documented six functions covering normalized surface basis construction, turn-angle point rotation, integer/XZ approximate distance and fast vector normalization with its runtime seed initializer. Named/typed the 128-byte runtime seed table and a verified float weight. Refined the existing guarded normalizer comment and established stack-only rotation signature. Recorded identity fallback, unordered comparisons and seed entry64 override in Ghidra; no runtime sampling or executable changes.

### Historical note: Effect emission/math pass

Effect emission/math pass: named and documented four functions covering directed effect batches, selection from a600-record pool, piecewise planar length approximation and planar Euclidean length. Corrected x87 return/stack signatures and effect-slot pointer return. Recorded free-slot priority, signed minimum selection, tie handling and batch payload offsets in Ghidra. Detailed effect identity remains unresolved; globals/local counts unchanged and executable unchanged.

### Historical note: Configured effect pass

Configured effect pass: named and documented six functions covering the main record initializer, random rotation-sign emitter, primary/secondary pool clearing, driver-dependent configuration colours and day/night texture descriptor loading. Verified tick/settings gates, slot reuse without blanket clearing, pointer-return caveats and distinct reset scopes. Detailed field offsets and numeric semantics remain in saved Ghidra comments. Globals/local counts unchanged; executable unchanged.

### Historical note: Overlay-effect rendering pass

Overlay-effect rendering pass: named and documented the viewport quad-command builder and its output-pair wrapper. Verified camera-mode exclusions, per-vertex outcodes, colour modulation, custom register arguments and partial-chain handling on allocation failure against assembly and callees. Names/comments and refreshed pseudocode verified; project saved. Detailed evidence remains in Ghidra; no Wine run or executable changes.

### Historical note: World-effect rendering pass

World-effect rendering pass: named and documented the primary effect command builder, including projection/depth rejection, near-camera overlay transfer, rotated quads, per-viewport trail history and colour/outcode handling. Verified against full assembly and arena helpers; names/comments and refreshed pseudocode read back, project saved. Detailed evidence remains in Ghidra. No new game testing or executable changes.

### Historical note: Overlay-emission/history pass

Overlay-emission/history pass: named the configured overlay emitter, session-aware camera-mode query and camera-change history invalidator; typed/named the two-viewport history-mode cache. Established that overlay success includes probability/overlap suppression, while pool exhaustion can leave partial emission; updated the world-renderer comment accordingly. Verified full assembly, PRNG helpers, names/comments, refreshed pseudocode and cache storage width; project saved. Detailed evidence stays in Ghidra. No Wine run or executable changes.

### Historical note: Render-bucket lifecycle pass

Render-bucket lifecycle pass: named seven average-depth queue, reset and merge helpers. Distinguished the 2000 average-depth buckets, 800 sorted-depth buckets and adjacent auxiliary 800-bucket region; documented destructive list stitching, retained headers and mode gates. Full assembly, constants, names/comments and refreshed pseudocode verified; project saved. Detailed evidence stays in Ghidra; auxiliary producer identity remains unresolved. No Wine run or executable changes.

### Historical note: Render-command routing pass

Render-command routing pass: named the texture/opacity router and explicit-depth/deferred pair append wrappers; typed/named the queue-mode DWORD and depth-bias float. Verified flag priority, texture bucket indexing, primitive depth handling, null-descriptor assumption and helper contracts against assembly/constants. Names/comments/types/storage widths and refreshed pseudocode read back; project saved after a transient transaction-lock retry. No Wine run or executable changes; descriptor reachability and complete mode-bit meanings remain unresolved in Ghidra.

### Historical note: Adaptive-depth sorting pass

Adaptive-depth sorting pass: identified the auxiliary800-bucket producer and orchestration; named three functions and three verified float constants. Documented range/sentinel handling, approximate triangle averaging, unchecked index computation and opposite bucket/within-bucket ordering. Updated the existing merge comment to connect the producer. Full assembly, names/comments/types/storage widths and refreshed pseudocode verified; project saved. No Wine run or executable changes.

### Historical note: Render-queue consumer/setup pass

Render-queue consumer/setup pass: named texture/optional-depth merge, mode-specific depth-offset initialization and its refresh wrapper; typed/named the shared cone/effect depth offset and refined the bucket-bias initialization comment. Verified merge order, mode gates, register ABI, constant stores, all new names/comments/types/storage widths and refreshed pseudocode. Project saved; no Wine run or executable changes. Detailed evidence remains in Ghidra.

### Historical note: Spatial-quad batch pass

Spatial-quad batch pass: named allocation/release/reinitialization, ring append and nearby projection/queueing functions, plus storage pointer/current-index/used-count globals. Established64 batches of16 quads, vertex/variant/colour storage and partial-output allocation behaviour. Full assembly, relevant helper preservation/constants, name/comment/type/storage-width readbacks and refreshed pseudocode verified; project saved. Visual effect identity and initialization invariants remain explicitly unresolved in Ghidra. No Wine run or executable changes.

### Historical note: Spatial-strip geometry pass

Spatial-strip geometry pass: named recursive subdivision/append, indexed state-flag reset and cross-product edge-pair construction; typed/named quad vertical-offset and batch-anchor threshold floats. Verified depth-limited splitting, colour propagation, custom register arguments and degenerate geometry handling. Full assembly/constants/helper preservation, name/comment/type/storage-width readbacks and refreshed pseudocode checked; project saved. Strip-state updater and visual identity remain follow-up. No Wine run or executable changes.

### Historical note: Spatial-strip state pass

Spatial-strip state pass: named/documented the tick-gated channel updater, including start/continue/stop transitions, fixed-point conversion and colour quantization. Created verified52-byte SpatialStripChannelState with named fields and applied its64-entry array at008b7ba0 (3328 bytes). The table label remains generic because MCP naming validation rejects its suggested structure-array prefix; its type/comment are saved. Full assembly/constants, function name/comment, struct field offsets/storage size and refreshed pseudocode verified; project saved. No Wine run or executable changes.

### Historical note: Car palette/selection and physics-ramp pass

Car palette/selection and physics-ramp pass: named15 functions covering archive palette extraction, integer HSV conversion, packed1555 recolouring/resampling, model-identifier predicates and physics profile/ramp helpers. Parent verified assembly/constants, names/comments and refreshed pseudocode; corrected two stack-based floating-point signatures. Project saved; executable hash unchanged. Partial archive reads, opaque fourth colour components and register-ABI placeholders remain documented in Ghidra. Current tags: 2,283 AnalystNamed and 2,172 StaticReviewed; naming counts are not full semantic-completion percentages. No game testing.

### Palette distance unordered and precision boundary

0049d240 comparison uses extended candidate versus binary32 stored best,
and JNC accepts unordered as well as ordered smaller distance under masked
invalid. Ordinary equal finite distance retains earlier entry. Ghidra comment
saved; exceptional reachability remains open. See[personality selection](personality-selection-contract.md).

## Audio and music

### Historical note: Font/texture/audio/helper pass

Font/texture/audio/helper pass: named 51 additional functions and 10 globals/constants covering frontend token lookup and cursor tests, turn-based trigonometry/matrix maths, diagnostic ring records, tagged sound playback/voice allocation, and font/shape texture resources. All names/comments/refreshed pseudocode and global types/widths were verified; project saved, executable hash unchanged. Complete resource structures, sound tags and register ABIs remain partial. No new Wine run.

### Historical note: Controls/track-AI/radio/tile pass

Controls/track-AI/radio/tile pass: added 44 function names and seven new globals; refined/typed the existing traffic-settings table as shared track AI parameter records after cross-checking its traffic-limit/delay consumers. Covered shift/action inputs, track tuning initialization, sound-bank loading, police speech queue/location selection and tiled frontend rendering. All 44 names/comments/pseudocode and eight new/refined global names/types/storage widths verified; project saved, executable hash unchanged. No Wine run; full AI record, speech request and renderer ABIs remain partial.

### Historical note: Radio/archive follow-up

Radio/archive follow-up: added 22 function names covering police-radio dispatch/admission, speech queue and warning-voice updates, archive directories/member lookup, optional shape lookup, palettes and raster/font setup. All names/comments and refreshed pseudocode verified; project saved, executable hash unchanged. Spoken sample identities, complete resource formats and register ABIs remain partial. No Wine run needed; detailed evidence remains in Ghidra.

### Historical note: Font-decoder/workspace follow-up

Font-decoder/workspace follow-up: added six function names and eight globals; recovered two explicitly registered decoder entries. Covered byte/variable-width character decoding, printable mapping, alpha ramp preparation, workspace refresh and glyph callback selection. Verified names/comments/refreshed pseudocode and global types/storage widths; project saved, executable hash unchanged. No Wine run. Encoding identity, indexed blend builder and drawing callback internals remain partial; detailed evidence is in Ghidra.

### Historical note: Sound lifecycle/callback follow-up

Sound lifecycle/callback follow-up: named ten additional functions and seven globals; recovered six explicitly registered callback entries. Covered DLL/version/export loading, window-message start/stop, critical-section unwind, diagnostic/channel callbacks and sample-conversion dispatch. Confirmed the message callback has six stack arguments with stdcall cleanup; kept sample rate and adjacent control word as separate two-byte fields. Added comments to three still-unnamed callbacks where complete semantics remain uncertain. Three Luna workers supplied bounded read-only reviews; parent verified instructions, names/comments, regenerated pseudocode, globals/storage widths, signature and tag count. Project saved, executable hash unchanged and map bounds/block count stable. Complex sample conversion and asynchronous ownership remain in the Astra backlog; no Wine run.

### Historical note: Sound/cursor static follow-up

Sound/cursor static follow-up: named eighteen additional functions and ten globals/tables; recovered six explicitly referenced callbacks. Covered sound initialization/shutdown, capability/mode selection, locked activation/service, sample conversions and cursor clamping/snapshot hooks. Added a verified 32-byte cursor state structure with eight named fields. Confirmed signed-byte sample expansion uses a 256-float table at a scale of 256. Names/comments, regenerated pseudocode, global widths and structure offsets verified; project saved, executable hash unchanged and memory-map bounds/block count stable. Complete sound voice layouts, envelope invariants and asynchronous ownership remain in the Astra backlog. Three Luna workers supplied read-only reviews; no Wine run.

### Historical note: Modal/audio descriptor follow-up

Modal/audio descriptor follow-up: named forty-two additional functions and five globals/tables; recovered sixteen explicitly registered adapter entries. Covered yes/no and timed dialogs, raster/font state snapshots, linked voice pitch controls, pan/sign handling, pitch-ratio conversion and sound descriptor builders. Confirmed selector mechanics while leaving physical formats and backend identity unresolved. Added a no-argument HWND getter prototype; its previously named window global remains untyped because the bridge rejects the existing handle prefix/type combination. Names/comments, regenerated pseudocode, global widths, prototype and tag count verified; project saved, executable hash unchanged and memory-map bounds/block count stable. Three Luna workers supplied read-only reviews. Further static work can follow registered descriptor callbacks; pitch-domain and numerical limits remain in the Astra backlog. No Wine run.

### Historical note: Sound reader/layout pass

Sound reader/layout pass: named thirty-one additional functions, refined twenty-five earlier names/comments, and added four globals/tables while refining two existing globals. Recovered twenty-six registered reader/adapter entries. Added eight reader structures (16–32 bytes) and typed/named sixteen reader pointers in callbacks and constructors. Established finite, looping, refill and queued paths; signed8/signed16 and mono/stereo controls; float versus raw-copy output; and two shifted-nibble lookup tables. The shared backend selector also serves raster dispatch, so its name now reflects library-wide use. All fifty-six new/refined functions, global widths, structure offsets and local pointer types/names were read back and checked in regenerated pseudocode. Project saved, executable hash unchanged and memory-map bounds/block count stable. Three Luna workers supplied read-only reviews; no Wine run. Stream refill ownership, custom register ABIs and decoder identities remain partial.

### Historical note: Sound stream queue/decoder pass

Sound stream queue/decoder pass: named nineteen additional functions and fifteen globals/record tables, refined the refill callback global comment, and added two structures: a 12-byte buffer header and 16-byte timed callback record. Recovered fifteen registered entries, including six constructors still awaiting names. Documented queue retirement/signalling, terminal replay, initialization/shutdown, format-specific clearing and finite/refill/queued decoded output. Preserved exact masked 17-bit saturation, conditional tail clearing, signed versus unsigned WORD window counts and custom register arguments. All new names/comments, refreshed pseudocode, global widths and structure offsets verified; project saved, executable hash unchanged and memory-map bounds/block count stable. Three Luna workers supplied read-only reviews; parent corrected register-order and zero-fill interpretations against assembly. No Wine run. Next ordinary static work: six decoder-reader constructors and decoder initialization/block generation.

### Historical note: Packed sound decoder follow-up

Packed sound decoder follow-up: named ten additional functions and eight globals/constants, including the six previously recovered constructors. Added a 12-byte bit-reader prefix and typed/named its register-held pointer. Confirmed bit masks for widths 0–8, decoder initialization/reset ranges, alternating-sample interpolation and block-generation mechanics without assigning a codec identity. Parent assembly/byte checks corrected worker interpretations of bit widths, the initial scale (8.0), synthesis range and threshold branch. Names/comments, refreshed pseudocode, global widths, structure offsets and local type/name verified; project saved, executable hash and memory map unchanged. Three Luna workers supplied read-only reviews; no Wine run. Further static targets are decoder preparation-hook installation and transform helpers; exact codec/numerical equivalence remains in the Astra backlog.

### Historical note: Sound backend/packed transform follow-up

Sound backend/packed transform follow-up: named eleven additional functions and nine globals/tables, refined the preparation-hook comment, recovered two registered hooks, and added a 12-byte decode-code structure applied to 29 records. Typed/named the bit-skip state pointer. Established EMMS versus RET-only preparation, backend constructor selection, two-row packed transitions, coefficient-vector decoding, feedback filtering and stereo conversion helpers. Assembly corrected worker claims about output extent and bias application: the feedback filter covers +0x684..+0xd40 and adds bias to every output while retaining unbiased history. Names/comments, regenerated pseudocode, global widths, code-record layout and local pointer verified; project saved, executable hash and memory map unchanged. Three Luna workers supplied read-only reviews; no Wine run. Next ordinary static work: the sixteen registered shifted-nibble constructors selected by 00521fc0 and remaining mixing callbacks installed by 004ffd84.

### Historical note: AI/radio/network-role/geometry pass

AI/radio/network-role/geometry pass: named twenty-eight functions and seven globals. Covered police-radio command sequences, selective AI/pursuit resets, track placement and velocity setup, cruise speed, nearby-player segment lookup, clamped lane/segment helpers, indexed state records, geometry color/rotation state, network timing/role election and bounded record copying. Three Luna workers supplied read-only reviews; parent checked assembly/raw constants and corrected1/6 versus1/3, register preservation and packed-color difference meanings. Names/comments, regenerated pseudocode, global types/four-byte widths and tag count verified; project saved, executable hash unchanged and memory map stable. Detailed contracts remain in Ghidra. No game/network execution or file writes by analyzed routines.

### Historical note: Spatial audio/helper follow-up

Spatial audio/helper follow-up: named twelve functions and two globals covering voice reset/stop, approximate distance scoring, parameter updates, position history and transition records, plus a flags-only vehicle comparison and empty speech hook. Parent checked worker findings against assembly and raw constant bytes. Names/comments, regenerated pseudocode, global types/widths and tag count verified; project saved, executable hash unchanged. One parameter helper has incomplete pseudocode because the downstream register ABI is unresolved; its assembly contract is documented. No Wine run.

### Historical note: Music selection follow-up

Music selection follow-up: named nine functions and five globals covering configured/random track/style selection, weighted show sequence, stream storage setup, show6 override and music cleanup. Assembly and raw resource strings establish music-specific roles. Names/comments, regenerated pseudocode, global widths/types and tag total verified; project saved and executable hash unchanged. No Wine run. Stream allocation, playback state machine and callback ownership remain partial.

### Historical note: Vehicle event/audio consumer pass

Vehicle event/audio consumer pass: named five helpers for indexed sample selection, pitch-bend caching, indexed/one-shot routing, distance gating and an audio projection code. Consumer assembly excerpts now establish audio use of the vehicle event queue, including channel remapping and stop commands. Recorded signed fixed-point attenuation, low-byte cache behavior and auxiliary SAR4 strength scaling without assigning unverified audible sample identities. Names/comments and refreshed pseudocode verified; project saved, executable hash unchanged. Parent audio loops and remaining sample/voice routing helpers are static follow-ups. No Wine run.

### Historical note: Vehicle sample/voice routing pass

Vehicle sample/voice routing pass: named two functions and previous-sample global. Verified selector jump tables, random repeat variation, bank selection, voice replacement/update paths and spatial/pan handling. Downstream pitch setter confirms cached strength-derived value is pitch bend; corrected earlier helper name/comments and scratchpad wording. Volume instead follows distance attenuation and configured scaling. Names/comments, refreshed pseudocode, direct global xrefs and type audit verified; project saved, executable hash unchanged. Exact audible sample identities and voice-counter lifecycle remain unresolved. No Wine run.

### Historical note: Vehicle warning/engine audio pass

Vehicle warning/engine audio pass: named twelve functions covering sample-three voice control, warning active-state access, phase start/fade transitions, randomized alternating/continuous initialization, phase update and distance-scaled engine voice. Typed/named shared motion magnitude. Recorded sample IDs, timing ranges, exact-equality/wrap behavior, volume/pitch scaling and spatial/pan branches. Names/comments, refreshed pseudocode, global width/audit and tag totals verified; project saved, executable hash unchanged. Parent engine/audio loops remain follow-up; exact audible identities and timing units unresolved. No Wine run.

### Historical note: Audio environment/control pass

Audio environment/control pass: named eight functions covering pan/bearing conversion, master/stream restoration, effect-bus level wrappers, selected voice-range stopping, volume toggles and queued sample replay. Assembly and refreshed-pseudocode/name/comment checks completed; project saved, executable hash unchanged. Reactivated three Luna workers for separate read-only playback, effect-bus and stop/reset reviews; parent retains Ghidra writes and verification. No Wine run.

### Historical note: Audio listener/effect-bus pass

Audio listener/effect-bus pass: named eighteen functions covering race listener orchestration, slot initialization/reinitialization, scaled playback, stream loudness, effect-bus control, weather scheduling/playback, police alert/pursuit music, effect classification, signed bearing lookup and shell path opening. Typed/named weather countdown and active spatial-audio slot count. Verified assembly, raw bytes/constants, name/comment readbacks, refreshed pseudocode and tag totals; project saved, executable hash unchanged. Corrected slot reinitialization to preserve incoming active state. Bearing lookup quadrant tails are verified in raw bytes but omitted from the current Ghidra function body; body/jump-table recovery remains a static follow-up. Exact audible identities, timing units and backend contracts remain unresolved. No Wine run.

### Historical note: Spatial-audio caller pass

Spatial-audio caller pass: named five orchestration functions for listener transform copies, nearest track ambience, listener vehicle audio, tracked-source audio and nearest-source allocation. Caller data flow confirms slot+0 stores a vehicle/source pointer; refined initializer/reinitializer comments accordingly. Verified forward versus reverse24-byte queue traversal, nearest-candidate filtering/order/reuse and signed warning-state transitions against full assembly. Bearing tails are now disassembled with twelve feasible jump references, but function-body expansion remains pending and pseudocode is still incomplete. Names/comments and refreshed pseudocode checked; project saved, executable hash unchanged. No Wine run.

### Historical note: Race-audio lifecycle pass

Race-audio lifecycle pass: named seven reset, fade/release, persistent engine-layer creation, voice-record initialization and bank-adapter functions. Verified39 initialized handle/sample records, zero-volume layer startup, distinct master-volume ramps, repeated teardown delay and byte-versus-DWORD reset widths. Refined the existing bank-removal comment to distinguish assertions, validation and16 associated voice records from24 bank slots. Name/comment and refreshed-pseudocode readbacks passed; project saved, executable hash unchanged. Large track-specific ambient dispatcher00415210 remains a further static-analysis target; not counted as reviewed here. No Wine run.

### Historical note: Route-speech follow-up

Route-speech follow-up: named three functions covering route-cue interpretation, default speech requests and owned tutorial-buffer cleanup. Parent verified full assembly and read back names/comments; refreshed pseudocode and saved project. Route record headers, cue terminators, lap wrap and cursor ownership are documented in Ghidra; exact physical units, resource bounds and the unused request word remain unresolved. Executable hash unchanged; no Wine run.

### Multiplayer setup framing and music-list ownership

Setup sender004c5e80 sends exactly2192 bytes in ten208-byte and one112-byte
chunks, each prefixed with type5. Client restoration preserves only record
+14 when the saved signed value is0..49, and always+68, across sixteen
108-byte records. This is selective restoration, not transfer rollback.
Reader004f6640 admits only an exactly peeked complete frame under its
configured WORD length limit. The absent-index unpacker fallback reaches
004c6080 through004a6440; that append has no aggregate2192-byte check.
Configured frame bounds, indexed unpacker behavior, ordering and teardown
remain open. Ghidra004c6080 now links these contracts.

Music creators00410330/00410370 return through004e4790/004e45f0/004e4420;
the initializer publishes the returned object as both list head and tail,
with next+70 zero. Thus ordinary creation supports the head-equal branch
of004e4b50 when00410aa0 releases00552598. The non-head branch unlinks and
frees its target but also clears both global list pointers; remaining-list
preservation is not established. Caller EDX is the preserved zero gate
value used to clear00552598. Reentry, abort-return and indirect mutation
remain open; this does not resolve the reported music-stop hang.

Camera constructor increment evidence is recorded in
[CCM and camera contract](ccm-camera-contract.md#stored-transition-increment).
All findings are static; no runtime capture or binary change.

### Music fade service dependency

Voice ramp update/clamping and its active-record gates are assembly-verified
in00500c80. Duration in004e9420 divides a per-service update delta; no
millisecond interpretation is established. See
[menu wait investigation](runtime-menu-hang.md#static-fade-progress-dependency).
The historical hang remains unresolved.

### Music head writer audit

All176 decoded direct references to005645b8 were inspected. Its writes
are confined to initializer004e44a7 and teardown004e4b35/004e4bcf/004e4c3c.
Worker traversal updates tail rather than head. This strengthens the ordinary
creator-to-release head-equality contract documented above. Indirect aliases,
reentry and returning abort paths prevent a universal ownership claim.
Ghidra004e4b50 records this bounded negative search.

### Music worker exit notification

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

See [shutdown contract](sound-driver-shutdown-contract.md). Ghidra worker comment saved.

### Startup consumes the ordinary event notification

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

### Shared command and lifecycle notification event

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

### Music command pool admission

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

### Installed command capacity and admission checks

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

### Music ring acquisition and idle predicate

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

### Contiguous release frontier

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

### Consumer queue cleanup and tag dispatch

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

### Recovered timed stream callback and retained retired node

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

### Purge voice wait deadline

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

### Identification speech code index producer

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

### Separate speech-language index bound

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

### Sound pitch dispatch boundary refinement

Live Ghidra assembly at00522f50 confirms unsigned upper clamping: zero
passes unchanged; any DWORD above0x80000, including signed-negative bit
patterns, becomes0x80000. The record offset is index*0xde4 using 32-bit
shift/subtract arithmetic. The wrapper has no local index or callback-null
check. Its two stack arguments are record+0xd64 and the clamped value;
the caller removes both after the indirect call through record+0xdb0.
This bounded mapping is resolved and saved in the Ghidra plate comment.
Caller index admission, callback lifetime, source pitch bounds and numerical
equivalence remain open for Astra; the audio table item stays Open.

The only direct Ghidra xref to00522f50 is00502da5 in
ApplyPlatformSoundVoicePitch00502d30. Assembly confirms methods0..2
forward the original index without a local bounds check and zero-extend
two WORD rate operands before00522f10. No local nonzero-divisor check
exists. This route discards dispatch return with XOR EAX,EAX. Method3
uses the separate009ef64c callback and does not establish the same clamp.
Saved caller comments retain the unresolved upstream bounds and ownership;
this is not evidence of a reachable failure.

### Configured audio-rate producer

Ghidra xrefs to009ef614 identify five direct writes in
HandleSoundDriverWindowMessage004e225c. After009ef61c returns signed-positive,
flag precedence is0800→22050,0400→16000,1000→32000,2000→44100,0200→11025.
All recognized assignments are nonzero. Multiple flags select the first in
that order. An unrecognized flag combination stores status-8 without assigning
a new rate; query failure and the stop branch also leave the rate unchanged.
The conditional producer is resolved, with a saved Ghidra comment. Call ordering,
indirect/overlapping writes and pre-initialization consumers remain unresolved;
this does not prove every pitch-converter invocation has a nonzero divisor.

### Pitch converter final rounding

Assembly00522f37 calls TruncateX87ValueTowardZero004dfd56 immediately
before FISTP DWORD at00522f3c. The helper saves the control word, loads0x0c3f,
executes FRNDINT and restores the caller word. Thus finite values with a
signed32-representable truncated result convert toward zero at the final
store. This resolves the former unspecified final-conversion helper semantics
in00522f10; its Ghidra comment now records the bounded conclusion. Earlier
arithmetic still uses ambient control state. Intermediate precision, invalid
inputs, overflow, unmasked exceptions and numerical equivalence remain open.

### Pitch-factor zero and INT_MIN behavior

Parent assembly review and Luna read-only review agree:00522e90 initializes
a float1.0 accumulator. Zero returns it directly. INT_MIN negates modulo32
to itself at00522ecf; signed CMP against1/JL at00522ed7..d9 returns that
same1.0 without reading factors. This resolves the local INT_MIN question
in the historical audio prompt, not its caller reachability or intended meaning.
The saved Ghidra comment now distinguishes this result from unresolved input
bounds and signed shift-overflow behavior. Full-domain equivalence remains open.

### Playback method3 conversion differs from the mixer ratio path

StartPlatformSoundPlayback00522510 loads the pitch helper argument as a full
DWORD at00522896; this callsite supplies no narrowing or local bound. After
00522e90, it multiplies by a zero-extended descriptor WORD rate, truncates
through004dfd56, and FISTP-stores a QWORD at005228c6. Only the low DWORD is
then passed to009ef640. This is a signed64 conversion followed by low32-bit
selection, unlike00522f10's signed32 integer store. Finite signed64 values
outside signed32 therefore cannot be assumed to share the latter's conversion
behavior. Callback failure takes the fallback at00522900. Ghidra comments
are saved; caller range, exceptional behavior and backend ABI remain Open.

### Sample-converter admission and callback boundary

Assembly004e1afb..fe uses signed CMP/JG for channels>2; it establishes
no positive lower bound. The range branch004e1bac..c0 requires signed end>0,
then computes end-start+1 and advances the working pointer by start*8,
without local ordering/original-count checks. In particular end0 does not
select an inclusive one-frame range. VirtualFree's result is ignored before
return0. The only decoded xref is callback publication004e1e46 to an indirect
DLL export at004e1e6e, not a direct conversion caller. Argument admission must
therefore be traced through that DLL route; direct-call absence proves no
caller bounds. These refinements are saved in Ghidra. Allocation ownership,
callback range provenance and failure reachability remain for Astra.

### Result notification audio wrappers named

Named004c9990 StartIndexedResultAnnouncementSound and004c99f0
CheckResultAnnouncementVoiceExpired after full assembly/audio-callee review.
Shared handle007dd82c and result-flag consumer0044ea60 establish notification
routing; sample identity, consumption/failure policy and lifecycle remain open.
Clear helper0044e7d0 covers0x68 bytes including six record-result flags.
Ghidra saved; no runtime or binary changes.

## Historical contract context

### Analysis findings and runtime evidence

Chronological pass entries from this section are grouped by subsystem below. Original prose is retained; later corrections may supersede earlier findings.

### Historical unresolved contracts

Recent static follow-up priorities (detailed evidence is saved in the Ghidra project):

- Service discovery and payload ownership: `00512c80`, `00512d70`, unrecognized callback entry `00512ad0`, `004f5950`, `00512890`, `004f5a30`, `004f60b0`, `005125b0`. Recover and inspect the registered worker entry, trace flag/handle cleanup, validate short-packet and string-termination contracts, and resolve indexed unpacker ownership after queue lookup unlocks. Review statically first; later controlled network tests only where static evidence leaves a specific gap.

- Network connection setup and dispatch: `004c3f90`, `004f5130`, `00512660`. Resolve callback register contracts, lock-held waits, reference counting and allocation-failure status provenance. Establish reachable caller/allocator invariants before reporting faults. Begin statically; controlled connection/cancellation tests only if later required.
- Vehicle control and contact contracts: `004a97cb`, `004a9bc4`, `004a0580`, `004a1210`; larger surface/control routines `004a1610` (pending), `004a1ce0`, `004a83d3` (initial static pass saved). Resolve mode/channel identities, profile rate/count bounds, rounding-sensitive calculations and query geometry. Begin statically; isolated numerical checks before game scenarios.
- Pursuit placement and selection: `00401b50`, `00401c20`, `00402a00`, `00402cb0`, `00404ff0`. Resolve side/placement validity, avoidance-loop termination, detach refusal and candidate-report semantics. Existing Wine evidence does not validate these new paths. Include `00404a00` and its direct callsite `0042b9af`, which currently has no recognized containing function; establish enclosing dispatch and timer/target caller contracts.






| Investigation | Entry points | Evidence and remaining questions |
| --- | --- | --- |
| Medium: screenshot concurrency and image boundaries | Capture `004c452c`; thread `004e3078`; GDI+ init/cleanup `004e2eb0` / `004e2fac`; writer `004e3014` | Recover dimension/allocation invariants, encoder availability and concurrent worker/cleanup ownership. Preserve 15/16/24/32-bit conversion, bottom-up rows, RGB565 masks and DWORD padding. Atomic counter increment does not reserve a filename; shutter sound reports thread launch and thread exit ignores save status. Begin with static and isolated instruction-equivalent cases; later controlled screenshot tests across supported depths/formats and shutdown timing only if needed. No reachable defect established. |
| Medium: cone placement and cached geometry | Cone position initializer `00493640`; seed/profile helpers `004934c0` / `00493380`; geometry loader `00475240`; helper `00474db0`; cleanup `00475b10` | Complete cone state/matrix/surface/color semantics and smoothing boundaries. Four smoothing passes update in place; EDX carries previous/current segment between side iterations, so do not substitute a symmetric simultaneous filter. Preserve fixed-point IMUL/SHL/SHR/ADC and x87 FISTP rounding. Recover cached geometry format, extrusion/topology construction, adjacency cancellation and buffer ownership before applying full layouts. Begin with assembly and resource comparisons; later controlled track/cone scenes only if static evidence requires them. The former cone tail is now confirmed velocity; motion lasts 128 ticks, followed by a 512-tick respawn countdown. Include one-wrap segment assumptions, signed tick catch-up, bounce below reset Y without position clamping, vehicle effect/counter semantics and depth/resource-variant contracts. Later controlled cone strikes, waiting for respawn and track-boundary/view tests only if static evidence requires them. |
x87 inverse-angle follow-up: `004f9482`, quaternion callsite `004b725b`, helper `0051a1ba`. Ordinary stack flow, endpoints, masked-unordered handling, domain-handler delegation and the local finite-domain caller gate are resolved in [x87 inverse-angle contract](x87-inverse-angle-contract.md). Remaining Astra work is the compatibility approximation, exception policy/unmasked behavior and unit/output-normalization invariants. These residuals do not reopen the established bounded findings or imply libm numerical equivalence.

| Investigation | Entry points | Evidence and remaining questions |
| --- | --- | --- |
| Medium: INI environment and runtime ownership boundaries | Environment override `004fb734`; search `004fb300`; window handler lookup/comparator `004cc660` / `004cc650`; sound unload `004e217c` | Trace reachable section/key lengths before reporting overflow: uppercase copies may exhaust capacity, yet underscore insertion and remaining-count decrement are unconditional. Establish search stride/count/address and comparator subtraction-overflow invariants. Recover lazy critical-section creation and sound export/worker lifetime across shutdown. Start with static call/resource bounds and isolated cases; runtime scenarios only if needed. No reachable defect established. |

| Investigation | Entry points | Evidence and remaining questions |
| --- | --- | --- |
| High: sound conversion and asynchronous lifecycle | Sample converter `004e1ae4`; loader `004e1dd4`; message handler `004e225c`; start/stop `004e2450` / `004e253c`; lock unwind `004e1d1c` | Recover nine-argument conversion formats, channel/count/subrange invariants and temporary buffer ownership. Inclusive subrange advances the working pointer before VirtualFree; prove caller ranges and allocation-base behavior before reporting a defect. Loader caches the module before validating exports; caller ignores loader status and message waits have no local timeout. Trace callback registration/removal, partial initialization, critical-section thread ownership and shutdown ordering statically. Begin with isolated instruction-equivalent conversion/range cases; later precise audio enable/disable, restart, mode/rate changes and shutdown scenarios only if needed. No reachable defect or audio equivalence established. |

Additional sound targets for the Astra lifecycle item: host voice/envelope service `00500c80` and float-pair packer `00500910`. Recover the complete 96-byte voice records from all consumers, preserving signed bytes, unaligned DWORD reads, fixed-point ramps, zero-duration and callback-mutation invariants. Check the packer's exact bit-mask saturation, ambient x87 rounding, mutable source buffer and unsigned end-pointer arithmetic before claiming numerical equivalence or a defect. The byte expansion table and its signed-8-to-float scale are now confirmed. Include pitch-ratio helper `00522e90`, fixed-point converter `00522f10` and clamped dispatch `00522f50`: thirteen nonzero factors support cents-like scaling, but valid input bounds, following zero entries, signed shifting/INT_MIN and intermediate float rounding remain unresolved. Start with static evidence and isolated instruction-equivalent cases; controlled fading, pitch modulation, audio restart and shutdown scenes remain optional later tests.

Sound reader follow-up for Astra: finite readers advance by the full requested count even across the end; preserve inclusive loop bounds, zero-progress refill assumptions, WORD versus DWORD pending consumption and conditional zero-fill at empty queues. Review custom register signatures, including the misleading inferred 64-bit return for the EDX-preserving voice-slot lookup, before locking caller parameters. Begin with static caller invariants and isolated cases; controlled looping/streaming and audio shutdown tests only if needed. Refill callback `004e8328` and the selected decoder-reader constructors are now documented; continue remaining decoder/mixer handlers at `00521fc0` / `005220a0`.

Packed transform refinement: 0052d6d8 is now named ApplyPackedSoundFeedbackFilter and its helper0052d618 has a bounded coefficient-recurrence description. Bias mode adds12582912.0 to every float output; the rolling history remains unbiased. Downstream int16 readers mask biased sample bits, so float-store rounding is part of the contract. The hook00520a00 is EMMS;004ffd80 is RET-only. Continue exact recurrence, x87 rounding/exception behavior, malformed bitstreams, positive stride and unary termination assumptions, and end-pointer overflow checks in stereo conversion00522f90/00522fd4; no reachable defect or numerical equivalence established.

Packed decoder transform follow-up for Astra: `0052d428` / `0052d6d8`, called by `0052df80`. Synthesis writes 432 intermediate floats at +0x684..+0xd40; final transform receives the output mode and may change representation. History copy is +0x834..+0xd40 to +0x174..+0x680. Initial threshold comparison changes a flag and continues generation, rather than returning early. Preserve x87 order, interpolation padding, history aliasing and width/mode contracts. Decoder initializer reads widths 1,4,4,6, uses initial scale 8.0 and clears exact partial state ranges; do not expand resets to full descriptor memory. Begin with static/isolated numerical cases; no new live test currently required.

Additional Astra stream targets: refill `004e8328`, release marker `004e68a0`, setup `004e7750`, stop `004e7b28`, decoder initializer/block generator `0052de94` / `0052df80`. Resolve sentinel -1/-2 ownership, deferred retirement, terminal stages, twenty-item ring bounds, initialization without clearing the retired pointer, codec format/state and zero-progress/overflow preconditions. Timed registration `004e7520` skips free slots according to nesting depth; preserve that policy and resolve record +0xc through consumers. Decoder readers have different register conventions and signed/unsigned WORD window tests; do not infer conventional prototypes or codec identity from output widths. Begin statically; later controlled streamed-audio completion, interruption/restart and shutdown tests only where needed. No reachable defect established.

Race/network capacity follow-up for Astra: roster builders `00473bf0` / `00474640`, menu reconciliation `0044be60`, settings sender `0049aa80`, lap option helpers `004cf160` / `004cf190`. Trace UI selection codes through roster budgets, all participant/model/track arrays, per-lap timing storage, network send/receive widths and AI pursuit support before proposing any expansion. Existing eight-slot budgets vary by mode/session; network settings narrow several fields to bytes, and traffic toggle differs from activation density/delay. These observations do not prove safe maxima or a reachable defect. Begin statically; later multiplayer synchronization and controlled race/pursuit/traffic scenarios may be useful. Implementation and binary changes remain outside scope.

Network lifecycle follow-up for Astra: `0049e320`, `0049eae0`, `0049f6a0` / `0049f730`, `0049abd0`, `0049eed0` and RAS probes `0049f790` / `0049f880`. Resolve six-slot ring versus separate admission counter capped at seven, seven-slot close versus eight-slot admission scans, full-slot fallthrough, unchecked name lengths, twenty-byte payload provenance, callback synchronization and marker wait outcomes. RAS readiness checks buffer-size/count outputs rather than only API success; accepted enumeration status codes and output capacity require caller analysis. These are unresolved invariants, not established reachable defects. Begin statically; later controlled lobby join/leave, start synchronization, disconnect and shutdown tests only if needed.

Car-transfer/NPS follow-up for Astra: `0049b800` / `0049b9b0` / `0049bab0` and `004a5780` / `004a5880` / `004a59c0`. Recover full header/300-byte metadata schema, receive-side bounds, short-read behavior, error cleanup and marker outcomes; trace registry type/index/string bounds and nonzero-type loader -1 acceptance. These are static observations, not confirmed reachable defects. Begin with callers/receivers and isolated instruction-equivalent cases; later two-peer car compatibility and interrupted-transfer scenarios only if needed. Implementation remains outside scope.

Vehicle contact/projection follow-up for Astra: `004a0580`, `004a1210`, `004a1610`, `004a1ce0`, `004a2260`, `004a2690` and orientation integration `004a2cc0` / `004a2e20`. Recover contact/query record layouts, normal basis/flag meanings, support-point resolution and damping before claiming numerical equivalence. Projection at `004a2690` repeats the same packed DWORD+0x15 load for all three vector components; determine intended field/reachability rather than assuming a defect. Preserve 16.16 conversion, raw signed float-bit gates, x87 rounding/NaNs and custom register results. Begin statically; later controlled slopes, rollover/contact recovery and police/traffic vehicle comparisons only if needed. Implementation remains outside scope.

Orientation correction follow-up for Astra: `004a2cc0` / `004a2e20` and `004b7840`. Matrix correction forms E=transpose(M)*M-I and applies M*(I+sum coefficient[k]*E^k); ten stored coefficients match inverse-square-root expansion. Recover valid matrix-error bounds, caller term-count/divisor constraints, x87 exceptional cases, countdown rollover and exact rounding before claiming convergence or equivalence. Minimum terms10 does not enforce maximum; full-table bounds require caller analysis. Begin with static and isolated numerical cases; later sustained driving/slopes/rollover comparisons only if needed. No binary changes authorized by this research.

Dialog/cursor/render-batch follow-up for Astra: `00444a80` / `00444b60` / `00444c20`, `0049c0e0` / `0049c1c0`, and `0049bf40` / `0049bf60`. Resolve library-clock units/wrap, dialog context/mode types, caller guarantees for positive choice counts and nonzero row heights, negative cursor-selector consumer meanings, render-batch capacities and driver primitive identity. Preserve custom register conventions; inferred EDX:EAX results can include a preserved EDX rather than a real 64-bit result. Mouse resource cleanup clears via ECX preserved by the allocator, despite misleading extraout_ECX pseudocode. Begin statically; later menu/input/driver comparisons only if required. No reachable defect established.

Frontend validation/hover follow-up for Astra: dispatchers `00445e60` / `00445f50`, edit renderer `00444350`, choice renderer `00444000`, and text-policy callback table near `00558c7c`. Resolve callback record-index bounds, event status labels and close-byte mutation, mode4 menu schema, packed rectangle capacities and backend-specific hit margins. Coordinate rescaling uses wrapping 32-bit multiplication without viewport-origin subtraction or local zero-divisor checks; nonzero backend mode requires valid X/Y output pointers. Cursor tags are `c%02d%d`; missing shape tags preserve old slots. Validate assumptions through callers before claiming a reachable defect. Begin statically; later input/menu transitions only if needed.

Toggle-menu/tooltip follow-up for Astra: `00445750`, `00445e60`, `00445f50` and `00445ac0`. Mode4 menu count narrows to BYTE after nonzero/<6 signed tests, leaving negative-input caller invariants unresolved; layout builder writes only for counts1..5. Choice hover has priority over menu hover and mode4 hover returns0. Tooltip delay uses signed comparison against wrapping clock+100; fade changes by calls and fade-out may become negative. Verify source-class changes at equal indices, target initialization, text measurement and screen-edge bounds before claiming a reachable fault. Frame service returns callback result with2 mapped0, else0; callback close-byte mutation remains significant. AL-only validator return types remain inferred inaccurately by decompiler; the bridge component-renaming tool accepted return_type arguments but readback showed no prototype change. Begin statically; later menu transitions only if needed.

Dialog input/profile follow-up for Astra: `00444f50`, `00445520`, `004446d0`, `00446060`, `004461d0`, `004462e0`, `00446420` and larger helper `004465e0`. Recover loaded-file schema, pre-lookup selector bounds, selected-car indices, shared description capacities and failure-state ownership. Edit append writes no explicit NUL and depends on precleared tail/bounds. Enter in mode4 writes1 through the selected state pointer; it does not invert it. Choice initializer rejects zero counts/pointers and signed choice count>=10 but not negative counts; rejected input does not explicitly clear active/mode/callback. Preserve signed high-half WORD extraction at corrected offsets. Begin statically; later controlled dialog/profile transitions only if needed. No reachable defect established.

Profile/display/menu-parser follow-up for Astra: callback `00448210`, selector `00448394`, list builder `004475a0`, replay preparation `00446990`, parser helpers `00448f50` / `004491b0`, callback wrapper `00449990` and tooltip updater `00449aa0`. Resolve sorted insertion/duplicate policy, old-count100 insertion to101 and dynamic-ID range, empty-list fallback, file/list capacities and scanner negative-return initialization. String arena uses wrapping32-bit addition and rejects exact full capacity. Callback completion flag is written after invocation and depends on preserved EDX. Tooltip early return skips restoring scalar1.0; establish downstream state ownership before claiming a defect. Begin statically; later bounded menu/profile/display transitions only where needed. No reachable defect established.

Police/setup/stream follow-up for Astra: pursuit recruitment `00401650` / `00402cb0`, reorientation `00403180`, assignments `00403870`, mirror/normalization `00478bb0`, stream packet processor `004cf440` and queue/token helpers `004cf220`..`004cf3f0`. Resolve pursuit phases/ownership, radio flags set despite admission failure, physical speed/distance units, assignment count/divisor bounds and x87 exceptional cases. Normalizer reads17 stack entries after populating16 and writes destination slots1..17; establish provenance and consumers before claiming a reachable fault. Eight source records are not proven car slots. STRM operations use signed threshold/count comparisons, wrapping token generations and object locks around a global generation value; recover cross-object synchronization, packet lengths and selector contracts. Raw constants verified: warning threshold8.9406, track-relation speed threshold3.0, clearance240.0. Begin statically; later controlled pursuit/start/restart or stream scenarios only if needed. No reachable defect established.

AI/network-role/geometry follow-up for Astra: placement search `0040c160`, interpolation `0040f4b0`, provider list/start `0049e3d0` / `0049e800`, role exchange `004c4310`, spatial cache producer/consumer `004c6cb0` / `004c6f00`. Resolve placement-search termination and target validity, packed interpolation schema and custom ABI, service interface/descriptor counts, callback ownership and cleanup, role packet padding/name lengths and receiver validation. Role election uses signed clock then byte-string comparison; exact ties fail, wait has no local timeout. Cache payload remains unidentified. Raw interpolation constant00536814 is1/65536, not0.5; clamped speed-offset constant005367b4 is1/6. Render fade scales all four color byte lanes, lacks a negative clamp and clobbers EDX on scaled paths. Preserve x87 rounding and ordered/unordered comparisons. Begin statically; later two-peer/provider or controlled driving/render scenarios only if needed. No reachable defect established.

Melroy is willing to run the game and perform the required scenarios during the later Astra session. For each live test, give precise mode/settings/actions, the transition to capture, relevant function/field targets and a clear stop condition; do not omit useful scenarios merely because they require game interaction. These tests remain pending and are not required during the current static pass.

Future runtime work should use the Wine setup above, bounded read-only capture and explicit scenario instructions for Melroy when interaction is needed. Keep static inference, offline mathematical checks and observed game execution distinct. Parallel workers stay read-only on separate scopes; the parent reviews and performs Ghidra mutations and saves.

Performance timing follow-up for Astra: `004cdf10` and completion predicates `004ce840` / `004ce8e0` / `004ce960`. Resolve milestone units/categories, shared marker consumers, participant-state semantics and wrapped signed tick comparisons. Preserve raw signed float-bit speed gates and mode-specific exclusions; ranked pointer table starts at005612b0 while the HUD accessor indexes from005612a8. Begin statically; controlled acceleration/distance and multiplayer completion scenarios only if needed. No reachable defect established.

Spatial audio follow-up for Astra: `00411e60`, `004117a0`, `00410e30` and register callee `00417080`. Resolve entity/voice record layouts, selector/control meanings, fixed-point score overflow and spatial transition ownership. Current pseudocode for `00411cb0` omits register calculations because the callee ABI is incomplete; use assembly before applying prototypes. Distance score squares a truncated approximation, and position-history delta uses32.0 without proven physical units. Begin statically; controlled multi-vehicle/audio transitions only if needed.

Music state follow-up for Astra: `004103a0`, `004104f0`, allocator `004e45f0` and teardown `004109d0`. Trace rock/tech versus show resource schemas, selector bounds, stream storage ownership, fade/drain callback progress and interruption/restart semantics. Cleanup polls without a local timeout; setup overwrites the storage pointer without an existing-pointer guard. Establish caller lifecycle invariants before inferring defects. Begin statically; controlled music transitions/shutdown only if needed.

Record/performance follow-up for Astra: `00455c10` / `00455cd0`, query wrapper `00455dd0`, gate `004cf090` and lap-stat completion `004ce5a0`. Resolve category/filter semantics, sixteen-entry index maps versus record counts, sort-global lifetime and exact frontend action. Wrapper restores the map but leaves sort-selector globals changed; incomplete register ABIs hide calculations in pseudocode. Recover per-lap arrays and missing-time synthesis before defining expansion limits. Begin statically; controlled records/results or multiplayer menu scenarios only if needed.

Recovered comparator follow-up: `00455840`, explicitly installed by `00455c10`. Full body now available; static entry/dispatch/epilogue show eight sort selectors, primary-direction inversion and a separate ascending +0x238 tie-breaker. Verify remaining branches, float unordered handling, case-insensitive metadata-name pointers and score/status field identities before naming or applying layouts. Ordinary static review can continue here; difficult schema/capacity cases remain for Astra.

Result snapshot follow-up for Astra: `00455410`, `004552f0`, `00455070` / `00455140` and snapshot buffers006647b0/0066e270. Full0x9ac-byte copies preserve embedded runtime pointers; resolve their post-race ownership/lifetime before applying whole-record types. Comparator00455840 is now reviewed/named: direction reverses primary order only, final+0x238 tie-breaker stays ascending; unordered speed comparisons fall back to the tie-breaker. Trace progression/score writes and caller capacity invariants statically before any runtime scenario or expansion proposal.

Stored-record/progression follow-up for Astra: comparator `0044f6e0`, updates `0044f9b0` / `004512f0` / `0044e820`, save `0044f5f0`. Recover callback entry from explicit registration, full0x31c record/0x214 summary layouts, signed category modulo3 bounds, ten-slot map and inclusive lookup bounds. Trace series score and elimination indices through metadata before expansion proposals. Save frees database buffer without checking writer result; establish lifecycle/error reachability before claiming defects. Begin statically; controlled records/results persistence only if needed.

Stored record insertion follow-up: `0044fa10` has incomplete pseudocode with BADSPACEBASE around bulk copy; recover actual stack/register source and full-list replacement before naming. Comparator0044f6e0 is now reviewed/named, including text offsets+4/+0xf, signedWORD+0x318 and unordered speed tie handling. Database allocation/load accepts header0x10 without a local full-size check; validate loader and caller contracts before inferring defects. Continue statically; persistence/leaderboard scenarios only if needed.

Insertion/text ABI follow-up: insertion0044fa10 now named with verified by-value0x31c stack source, but pseudocode still needs a correct aggregate prototype. Trace all callers before applying it. Text wrapper00452120 copies into256byte stack storage; truncator00452090 substitutes dots after width testing without remeasurement. Recover source length/glyph width invariants before claiming reachable overflow or visual defects. Continue statically; leaderboard/text scenarios only if needed.

Timed track-event/placement follow-up for Astra: `00404e40`, `004c9dd0`, `004c9f50`, `0040b9c0`, `00404d30`, `0042bc70`; consumers `004ca160`, `004297d0`, `00403df0`; geometry helper `004c9bc0`. Resolve input byte+512 identity, 80-byte record capacity/ownership, endpoint geometry/units and radio command identities before assigning tactic names. Preserve signed deadline comparison, tick+192 wrap, reverse classification and no-match placement output behavior. Begin statically; controlled event input tests only if necessary.

Timed-event contact numeric/schema follow-up for Astra: reviewed/named `004ca160`, `004297d0`, `00403df0`, `00401650`, `004c9a80`, `004c9bc0`; surface chain `00420650`, `0041e940`, `0041f6e0`, `00420230`. Consumer scans eight records and four vehicle positions with 120-byte stride; establish allocation and police-index mapping independently. Preserve common-plane conservative rejection against +/-0.5, unordered negative-face outcodes, raw signed+6f0 gate and first-record mask policy. Surface helper mutates coordinate Y; recover complete fixed-point surface/height ABI and endpoint winding before stronger collision/tactic claims. Begin statically; runtime only if invariants remain unresolved.

Track surface/basis ABI follow-up for Astra: reviewed/named `0041e940`, `0041f650`, `0041f6e0`, `00420230`, `00420650`, `004969c0`, `004f44e0`, `004f4544`; remaining search `0041e990`, `0041f330`, `0041f500`. Recover full120-byte state and mixed EAX matrix/six-stack-int height ABI; current scalar/pointer return prototypes are documented placeholders. Distinguish rounded per-product cross/edge maths from transform summed64-bit products then SHRD16. Preserve cached-quad no-position-copy path, fallback basis sources and absence of normalization checks; establish basis invariants before exact plane-projection claims. Begin statically; controlled surface/height comparisons only if necessary.

Track linked-fallback follow-up for Astra: `0041f330`, `0041f500`, reviewed/named rescan `0041f090`; shared steps00552ea8 are incremental0,+1,-2. First/second descriptor links use unsigned distance scores with FFFFFFFF sentinel; ties choose second and only selected link is attempted before restoring120 bytes. Preserve signed distance threshold0x10000, boundary strip semantics, SAR5 XZ movement and local Y left unwritten in0041f500; full rescan assembly now proves it is not consumed on this path. Vertex binder0041e6a0 now confirms all four signedWORD indices and mapping2,0,6,4. Begin statically; caller/link validity and search failure policy need review before defect claims.

Surface rescan topology/numeric follow-up for Astra: `0041f090` now fully reviewed/named; steps00552e88 produce scanned offsets0,+1,-1,+2,-2,+3,-3, with final unscanned+7 movement then accumulated rollback. Failure restores segment and clears+14/+18, not full state. Preserve ordered edge acceptance/unordered rejection, inclusive strip bound and current-x87 FISTP rounding in0041e7c0. Verify descriptor counts, quad winding and exceptional numeric/control-state invariants before defect claims. Input Y concern for0041f500->0041f090 is closed statically; no runtime needed for that question.

Track attribute/side follow-up for Astra: reviewed/named `004205a0`, `004206f0`, `004207e0`, `00420bf0`; pending larger track override `00420840`, viewport side predicate `00420d60`, counter consumer `00426370`. Resolve track byte+0e nibble meanings, material byte+1 flags and colour channel ordering from producers/callers. Preserve dot positive-or-unordered primary-low-nibble choice, ordered<=0 primary-high, zero-primary fallback, full-byte material return and setter+74=-1. Float wrapper quantizes all coordinates through current-x87 FISTP. Predicate stack ABI and scalar return are now verified; remaining register-propagation pseudocode is partial. Begin statically; controlled material/track comparisons only if necessary.

Viewport side/scene follow-up for Astra: reviewed/named `00420d60`, `00426370`, `00426450`, `0042649c`, `004264c0`; pending mode selection `00426560`, handlers004263f0 and larger track override00420840. Resolve weather predicate nibble2 meaning, counter005e1014 stride8 and snapshot005e0dd8->00661220 schemas. Preserve original-segment side score with offset-segment byte lookup, zero-orientation +2 policy, single cyclic correction and current-x87 conversion. Dispatch reads00552ec8 before accepting modes1..24, with PUSHAD/POPAD preserving inputs. Establish mode/slot caller invariants before any bounds defect claim. Begin statically; controlled weather/view scenarios only if needed.

Viewport mode transition follow-up for Astra: reviewed/named `00426560`, `004238b0`, `00423960`, `00426310`; complex transition `00422610`, updater `00426680`, handler table004263f0. Recover mode0/19/23/24 meanings,00559264 pause bypass and vehicle flag priorities through producers. Preserve dispatch-before-pointer-store for modes3..6, base/override marker-policy difference, NULL base fallback and old-mode24/new0 restoration. Full scene types, slot/table bounds and interpolation helper ownership remain partial. Begin statically; controlled view/pause/contact scenarios only if necessary.

Viewport/effect callback follow-up for Astra: reviewed/named `00426680`, `0040f3b0`, recovered `00426290` and `004262a0`. Remaining explicit scene handler pointers include004251f0 and00425640; recover only from verified dispatch entries and review full bodies before names. Mode19 completion uses signed raw+110>3f800000 before float increment; allocation checks index<256 without lower bound and leaves record+8 unchanged. Establish definition/record lifecycle, state field schema and valid caller ranges before fault claims. Larger interpolation00422610 remains partial. Begin statically; targeted view/effect tests only if needed.

Recovered CCM/effect-view follow-up for Astra: `004251f0`, `00425640`; selection00423d90, pose readers0040f8d0/0040f940, quaternion/matrix helpers004b7590/004b79c0, transition00424fd0 and lookup004eac60. Full handlers are reviewed/named; resolve helper failure/output initialization contracts before uninitialized-data claims. CCM ratio uses extended comparison against float0.7, replacing below/unordered values. Effect completion may reselect eligible human participant and copy420-byte state backup; establish multiplayer ownership and restoration lifecycle. Begin statically; controlled CCM/effect/view scenarios only if necessary.

Effect pose follow-up for Astra: establish definition count and elapsed-tick invariants for the timed interpolation path, asset quaternion conventions and the numerical effect of unnormalized component blends. Preserve x87 precision/store order and distinguish mode-2 completion from invalid record input. Review viewport fallback and effect completion consumers before proposing any behavioural change; runtime testing is deferred.

Camera follow-up for Astra: validate CCM record coordinate/orientation conventions, zero displacement normalization, signed raw-bit direction rejection and why a rejected nearest candidate does not fall back to a second candidate. Trace scene pose extraction and transition interpolation consumers before changing camera behaviour. Preserve unordered x87 branch semantics in quaternion conversion/sign alignment; asset and caller validity remain unproven.

Scene pose follow-up for Astra: finish vehicle-overlap adjustment00421900, orientation adjustment00421730 and target-direction construction00422290, then trace mode-specific flag producers. Confirm material category meanings and physical vertical convention before interpreting upper/lower numeric clamps as ground/ceiling behaviour. Preserve ten-step endpoint/refinement state, x87 rounding and query reseeding; no new gameplay test required for remaining static investigation.

Camera overlap/orientation follow-up for Astra: trace vehicle eligibility bytes, extent/radius producers and scene flags; assess sequential adjustment order, zero extents, coincident targets and nearly parallel reference vectors before any behavioural changes. The three previously deferred pose helpers00421730/00421900/00422290 now have assembly-reviewed names/comments; remaining work concerns their producers and exceptional numerical behaviour. No additional game run needed for producer tracing.

Fast normalization follow-up for Astra: compare00497500 accuracy and exceptional-input behaviour against guarded004972f0 and unguarded004e01c0, preserving float spills, seed exponent construction and entry64 override. Trace source004cab60 and remaining geometry callers statically first; the runtime-generated seed storage has not been sampled. Surface basis00496a50 uses only three vertices and does not orthogonalize its edge vectors; confirm asset assumptions before changing projection behaviour.

Effect emission follow-up:004ca850 initializer and004cb469 caller of004cab60 need full schema/consumer tracing before naming effect identity. Pool selection004ca4b0 is assembly-reviewed and does not reserve its returned slot. Directed batch004cab60 skips zero vectors, uses fast normalization and shortens returned record lifetime-like DWORD; precise type/configuration roles remain open. Static initializer assembly was retrieved; no new runtime test is required to continue.

Configured effect follow-up:004ca850 is now assembly-reviewed and named; remaining work includes caller/consumer schemas. Trace004cac20/004caea0/004cb010/004cb220 emission callers and004cb750/004cbc90 update/render consumers to establish type identities and lifetime/vector fields. Configuration index/divisor validity, retained slot bytes and random rounding remain Astra candidates after ordinary static tracing.

Effect renderer follow-up:004cb750 secondary viewport-quad commands and004cbc90 primary world-effect projection/trails have pseudocode evidence only so far; do not count them as assembly-reviewed or named. Continue full assembly review, tracking per-viewport history flags, allocation failure and near-camera conversion004ca500.004cb010/004caea0/004cb220 are now reviewed/named; remaining ambiguity concerns effect identities, selector meanings and source validity.

- World-effect arena capacity contract: `BuildWorldTransientEffectCommandPair` writes before committing emitted bytes; its peek helper ignores the maximum requested size and the final commit result is ignored. Trace arena sizing/caller invariants before inferring an overflow. Optional later instrumentation should check cursor, capacity and emitted count under dense effects. Static evidence is in the Ghidra plate comment.

- Adaptive depth sort index contract: trace command producers and depth-range invariants for `BuildAdaptiveDepthSortedRenderCommandPair`; insertion has no bucket clamp and range measurement uses finite sentinels. Check nonfinite/extreme input reachability before classifying a bug. Static ordering and edge cases are documented in Ghidra.

Contact/start-placement follow-up for Astra: `0042ac40`, `0042ba00`, `0042bb80`, shared getter `0040eca0`. Establish contact class/subtype producers and table extents, event-helper register contract and force-feedback units. Preserve FISTP rounding, raw signed gates and extended sum comparison. Start loader always fills twelve records; reverse fallback uses configured racer total and can compute negative segments for unused indices. Trace producer/consumer validity before defect or capacity claims; the twelve-record loop is not proof of a universal racer limit. Begin statically; no new game test required for the current pass.

Reader/queue follow-up for Astra: `004dc1e0`, error helper `004f2a7d` and termination chain `004dfd04`; queue `004284e0`. Resolve error-helper nonreturn boundary before treating trailing decoded data as instructions or claiming the read failure returns an uninitialized value. Confirm resource-read return/count semantics. Trace vehicle event queue consumers before assigning command/channel/category enums or direct playback semantics; preserve signed count/drop gate and x87 fixed-point rounding. Current reader/queue structure definitions are reusable layouts only; custom ABI typing remains follow-up. Begin statically.

Buffered stream-control follow-up for Astra: `004cf5e0`, `004cf6b0`, `004cf810`, `004cfa40` / `004cfa80`, and upstream result helper `004fc600`. Full-read XOR provenance is now resolved by the completion helper preserving EDX. Continue packet-processor EDX:EAX contract, full operation/request layouts, source-transition API contracts and queue synchronization. Preserve byte-string names, signed free-space checks and memory copies that may exceed the asynchronous 0x2000 request size. Size calculator clobbers EBX/EDX; initializer returns the 16-byte record array rather than the backing base. Begin statically; runtime stream interruption/completion checks only if needed. No reachable defect established.

Stream cancellation follow-up for Astra: `004cfef0`, `004cffb0`, `004d0060`, `004d0220`, `004cfd30`; packet access/consumption `004d0300` / `004d03c0` and source close `004fd060`. Resolve source ownership and termination, length-zero packet-chain traversal, queue cursor bounds, pending-byte accounting, callback races and shutdown progress. Memory source scans until matching selector with no local bounds/zero-stride guard; file name copy need not terminate at0x103 bytes. Full cancellation early-returns when tail is NULL, and shutdown waits while state1 without local timeout. Establish caller invariants before fault claims; begin statically, runtime interruption/shutdown only if needed.

Frontend file/render follow-up for Astra: `00452a00`, `004529a0`, `004515e0`, `00452db0`. Trace copy callers and error handling: both opens occur before failure checks, partial success lacks local cleanup, zero read does not distinguish EOF/error and close results are ignored. Establish destination capacities and source aliasing before defect claims. Recover renderer register signatures and frontend descriptor+14 ownership. Begin statically; file-error or frontend scenarios only if needed.

Frontend token/history follow-up for Astra: `00451b50`, paragraph layout `00451cd0`, sequence matcher `00452420` and dispatcher `004524e0`, history pop `0044aec0`. Recover full layout register/stack ABI, local/destination token capacities and CR handling (copies following byte without checking LF). Tabs expand to three spaces while returned source length stays unchanged. Sequence match uppercases ASCII lowercase input then consumes full normalized input+9, resets only on mismatch and leaves completed index; establish caller state/reset bounds. History shifts19 pointers and leaves final entry duplicated; trace producers before fault claims. Begin statically; no runtime needed unless caller invariants remain unresolved.

Decompiler caution: `004eede0` is UppercaseAsciiCodeInEax; correcting its scalar int return now exposes verified comparisons/subtraction in pseudocode. EAX input is still unbound and unknown calling-convention/storage warnings remain. Sequence matcher uses uppercase-normalized input plus9; recover complete shared register signature before treating callers as complete.


Opponent scaling follow-up for Astra: `00404610`, `00408dc0`, `0040ee80`, `00409330`, scalar/vector chain `00406880` / `004068a0`. Resolve descriptor+30 profile index versus Aggressive UI setting,24-byte personality records and32-byte track tuning records. Track speed scale now returns verified float ST0; EAX/EBX/EDX preserved despite incomplete caller propagation. Scalar correction is(+7b4-+7b8)*8; establish producers/physical units before naming it speed or acceleration. Begin statically; controlled behavior-setting comparison only if needed and read-only memory access available.

Opponent lane follow-up for Astra: `004094d0`..`00409920` and progress gate `0040f050`. Resolve24-byte personality field+8 versus UI aggression, three-lane score groups24..38 and target flag+621bit80 ownership. Speed limiter gap<=1 copies ahead signed speed; gap2 applies half excess. Clearance penalty accepts signed negative gaps locally; establish nearest-vehicle producer invariants. Opening window uses vehicle+8+14*field+1fc against50/200/400 thresholds with optional-26. Preserve wrapping and unordered x87 branches; no physical units or reachable defect established. Begin statically; later behavior-setting comparisons only if needed.

Lane/pursuit numeric follow-up for Astra: `004096b0`, `00409920`, `00408870`, `004052e0`, `004053b0`. Preserve closing-score coefficients0.8,1/6,-0.5,-0.1,-1.3 and FISTP current-mode rounding; establish track nibble bounds before assuming target-adjustment loop terminates. Scalar approach assumes caller step policy and returns unchanged on unordered initial comparison. Pursuit gate compares signed raw excess bits against0x40000000; distinguish ordinary positive float2.0 from negative/NaN representations. Complete observed-target/group ownership statically before runtime pursuit scenarios.

AI timed-latch follow-up for Astra: `00405fd0`, `004060d0`, `00406120`, `00406160`, defaults `00405e60`. Resolve latch+7d4 gameplay role, offset+7c8 ownership and incoming EDX vector provenance. Preserve strict expiry versus toggle deadline comparisons, signed tick wrap, unordered x87 gates and nonzero raw motion-field tests. Complete custom register prototypes before relying on caller pseudocode. Begin statically; controlled low-speed/pursuit comparisons only if needed and read-only capture is available.

AI acceleration/braking follow-up for Astra: `004063e0`, `004064f0`, `004066c0`. Recover configuration+1cc/+1d8 and112-float table+2ec, byte+509 role and0056ec58 integration factor. Preserve FISTP rounding, raw signed error threshold and exact unordered min/max choices; profile getter locally converges on the same1.25 braking coefficient. Trace distance-scaling settings and participant gating before assigning catch-up/game-mode names. Begin statically; controlled comparisons only if needed.

AI track-motion follow-up for Astra: `004068a0`, `00406980`, `00406a80`, `0040ef70`. Resolve basis-vector physical roles and36-byte track-record packed fields. Heading scan has track0 segment0x225..0x235 bypass, one-step wrapping and no local iteration bound; establish valid-index/count invariants before fault claims. Projection x87 return is exposed, but original declared precision and EAX parameter storage remain unknown. Begin statically; runtime track/reverse-mode comparison only if needed.

AI steering/recovery follow-up for Astra: `00406b00`, `00406b60`, `00406c00`, `00406c90`, `00406d40`; dispatcher `00406e50` and predicate `0040f110`. Resolve output ESI/vehicle EAX signatures, target ownership/aliasing, predicted-motion0.4 units, desired-speed distance multiplier32 and track0 segment0x205..0x20f offset-10 exception. Trace reset counters, latch ownership and all dispatcher paths statically before assigning recovery/tactic semantics. Bridge naming validator currently rejects double prefixes; exact double constants remain documented in function comments rather than mistyped globals. Runtime recovery scenarios only if needed.

AI steering recovery/heading follow-up for Astra: `00406e50`, `0040f110`, `004070c0`; reset `00429100`; atan2 fallback `004ff624`. Predicate accepts current or adjacent valid lane inside track nibble interval. Trace +658 producer/counter>8, NULLtarget and speed<=10/unordered branch: local output vector is copied without initialization on that path, even when reset helper returns early. Establish reachability and consumer behavior before defect claims. Preserve incoming EDX0 through predicate/reset; +7d8 bit40 alternates recovery paths and signed>1000 resets. Heading positive scale0.00097656 differs from exact1/1024 nonpositive path; original heading range and fallback precision need review. Begin statically; specific recovery tests only if invariants cannot be resolved.

AI controller follow-up for Astra: larger controllers `004076b0`, `00407fa0` and selector `00408600`; reviewed integration `004071a0`, damping `00407380`, low-speed controller `00407c30`. Recover matrix/coordinate conventions, tuning schemas and shared control vector0056ec6c. Preserve raw signed gate+10c, sign-selected abs, unordered clamp paths, FSIN negative-error branch and float-store boundaries. Integration factor initialized0.03125 and repeat count1; scale skips signed zeros but acceptsNaN/inf. Low-speed desired magnitude caps16.4109; reverse/latch branch changes acceleration sign. Larger controllers include random/tick/profile effects and should receive full assembly review before tactic names or physical claims. Begin statically; controlled low-speed/reverse/weather comparisons only if needed.

AI gear/controller gates follow-up for Astra: `004061b0`, `00408600`; unnamed controllers `004076b0`, `00407fa0`. Establish config gear count+8 and table+94 extents; no accepted candidate leaves incoming EBX and uninitialized targetRPM. Countdown path bypasses idle floor, uses shared iteration count and truncates its own RPM target. Preserve target coefficients0.2/0.4/0.5/0.8, speed-limit+10 and magnitude+20 gates, wrapping arithmetic and SAR3 smoothing. Complete profile005523d8 schema and physical meaning of controller thresholds0.04/0.5/2.5/13.4109; infer status3/4 from producers before naming categories. Begin statically; controlled gear/low-speed scenarios only if invariants remain unresolved.

AI projection-controller numeric follow-up for Astra: `004076b0`, shared tuning0056ebd0..0056ebfc, projection helper `00406a80`. Full assembly now reviewed/named; resolve physical bases/units, config+248 override3.45/value and+5c0/+5c4 roles. Offset bound uses+b8*0.5 directly without abs; establish nonnegative-bound invariants. Gain/limit scale uses1+forward*float~0.0015 then+7bc on>1/unordered; preserve float stores and unordered clamps. Penalty requires forward>abs(side), positive/unordered acceleration and forward>44.703. Larger random/tick controller `00407fa0` still needs full review. Begin statically; numerical equivalence and targeted track scenarios only if needed.

AI list-window/profile gate follow-up for Astra: `00409a90`, `00404b90`, caller state machine `00409c00`; list005efc08/count00553078. Combined player/police registration flags now confirmed; recover list capacity and weather/006fd4c8/+660/+710bit10 distance policy. Last nonNULL interval result overwrites prior entries, with no short circuit; establish intended state1/2 transition before fault claims. Reduction requires+16c and raw signed+168 gate in setting1; ordered+168>5 truncates to trigger, profile0 adds tick phase, desired speed multiplies0.9. Motion-field physical meaning and register-preservation pseudocode remain partial. Low-speed tuning0056ec04..0056ec28 now typed/named; units unresolved. Begin statically; runtime behavior comparison only if necessary.

Opponent proximity/list follow-up for Astra: `00404840`, `0040deb0`, placement `00404d30`; player-police count00553078 and table005efc08. Combined descriptor flags1/8 producer is verified; capacity is not established. Preserve target update before opponent-flag gate, strict startup tick interval, signed gap<=1, unordered desired-speed threshold and audio dispatch register tuples. Selector expiry maps only1->0 and2->1 after strict deadline, leaving>=3 unchanged. Complete event/audio identity and primary-player pointer invariants statically before runtime scenarios.

List geometry and network-browser/speech pass: named three functions covering scrollable list geometry, discovered-game list rebuilding and police speech scalar thresholds. Full assembly checked; verified pointer-table ownership, record stride, empty-list fallback and ordered x87 gates. Names/comments and refreshed pseudocode checked; project saved. Totals: 2,312 AnalystNamed, 2,201 StaticReviewed, 905 globals/constants. Widget schemas, callback reachability and speech field units remain partial; detailed evidence stays in Ghidra. Three Luna workers have separate read-only follow-up batches; parent verifies and applies annotations. No game testing.

Police radio sequence follow-up: named one sequence wrapper after full assembly verification, preserving admission ordering, two independent random gates and shared selector updates. Name/comment and regenerated pseudocode verified; project saved. Totals: 2,313 AnalystNamed and 2,202 StaticReviewed. Specific speech/event identity remains unresolved. No game testing or binary changes.

Frontend geometry/police sequence pass: named two functions after full assembly review. Corrected the six-entry rectangle formula for partial AX writes; documented target-flag/admission gates and random speech paths. Names/comments and refreshed pseudocode verified; project saved. Totals: 2,315 AnalystNamed, 2,204 StaticReviewed. Exact widget schema and speech/event identities remain partial. No game testing or binary changes.

Result-progression dispatcher pass: named one function and documented all four mode branches after verifying assembly, helpers and raw jump-table order. Corrected worker mode mapping and recovered the omitted model/track branch. Names/comment and refreshed pseudocode verified; project saved. Totals: 2,316 AnalystNamed, 2,205 StaticReviewed. Flag-code labels, record statuses and complete progression semantics remain unresolved; detailed evidence stays in Ghidra. No game testing or binary changes.

Fixed-angle math pass: named angle interpolation and two integer arithmetic helpers. Verified full257-entry lookup table, quadrant dispatch, zero-input result and masked-shift/division assumptions; corrected the proven stack-based quotient prototype. Names/comments and refreshed pseudocode checked; project saved. Totals: 2,319 AnalystNamed, 2,208 StaticReviewed. Custom register ABI still limits angle pseudocode; caller axis conventions and exceptional integer inputs remain deferred in Ghidra. No game testing or binary changes.

Signed vehicle response pass: named one response-scaling function after full assembly/rawconstant review. Corrected negative-threshold branch assignments and absolute-magnitude taper interpretation; confirmed final candidate clamp stores do not feed the return. Name/comment and refreshed pseudocode verified; project saved. Totals: 2,320 AnalystNamed, 2,209 StaticReviewed. Physical axis/units and exceptional-value invariants remain unresolved; no game testing or binary changes.

Police segment/assignment pass: named three helpers covering encoded segment bounds, flagged pursuit-link cleanup and wrapped midpoint assignment. Parent checked full assembly and callees, correcting record stride and stack-argument-to-field order. Names/comments and regenerated pseudocode verified; project saved. Totals: 2,323 AnalystNamed, 2,212 StaticReviewed. Tactical code meanings and list/index invariants remain partial; no game testing or binary changes.

Vehicle projection/reset pass: named three helpers for profile-threshold mode limiting, two projected vector components and motion/response reset. Parent verified full assembly, integer profile loading, identical reset branches and contradictory gates around an unreachable response write. Names/comments and refreshed pseudocode checked; project saved. Totals: 2,326 AnalystNamed, 2,215 StaticReviewed. Mode/axis semantics remain partial. No game testing or binary changes.

Police radio builders pass: named three sequences covering target-status selection and two command-selector variants. Parent verified full assembly, staged admission gates, speaker-change calls and shared global updates. Names/comments and regenerated pseudocode checked; project saved. Totals: 2,329 AnalystNamed, 2,218 StaticReviewed. Specific voice-line meanings remain unresolved. No game testing or binary changes.

Quaternion interpolation pass: named spherical quaternion interpolation and matrix interpolation wrapper. Verified hemisphere alignment, linear fallback threshold, mixed register/stack arguments and output writes. Names/comments and refreshed pseudocode checked; project saved. Totals: 2,331 AnalystNamed, 2,220 StaticReviewed. Math-helper domain handling, coordinate conventions and input invariants remain partial; no game testing or binary changes.

Fixed-stride allocation helper: named and documented one cursor-based record-slice reserver, including exact preserved registers, wrapping arithmetic and output-write order. Full assembly and refreshed pseudocode verified; project saved. Totals: 2,332 AnalystNamed, 2,221 StaticReviewed. Caller capacity/alias assumptions remain partial. No game testing or binary changes.

Memory-pool summary pass: named summary collection and active block-head accessor. Verified full assembly, address-span accounting, flag priority, signed largest-block comparison and output-write order. Names/comments and refreshed pseudocode checked; project saved. Totals: 2,334 AnalystNamed, 2,223 StaticReviewed. Allocator overhead and alias/list invariants remain partial. No game testing or binary changes.

Memory diagnostic flags/sentinel pass: named fixed-width flag formatter and end-marker status checker. Parent verified full assembly, ten-byte nonterminated output and three distinct sentinel return statuses, correcting worker match-status interpretation. Names/comments and refreshed pseudocode checked; project saved. Totals: 2,336 AnalystNamed, 2,225 StaticReviewed. Flag-letter meanings and allocator integrity assumptions remain partial; no game testing or binary changes.

Network profile/settings dispatcher: named one function after full assembly and helper-contract review. Documented profile/cache comparisons, host settings sends, client setting copies, separate lap fields and flag-only lock scope. Name/comment and refreshed pseudocode checked; project saved. Totals: 2,337 AnalystNamed, 2,226 StaticReviewed. Protocol validity, concurrent snapshot and model-lookup invariants remain partial; no game testing or binary changes.

Vehicle contact-basis projection pass: named one routine after full assembly/rawconstant review. Documented profile gate, raw-bit threshold, basis transforms, unordered projection branch and two-component quadratic correction; preserved the absence of a zero-crossing clamp. Name/comment and refreshed pseudocode checked; project saved. Totals: 2,338 AnalystNamed, 2,227 StaticReviewed. Coordinate/contact-state and physical coefficient meanings remain partial; no game testing or binary changes.

Memory-report follow-up: named and documented the diagnostic report writer after full assembly and format-string verification. Project saved; totals 2,339 AnalystNamed and 2,228 StaticReviewed. Buffer, filename-exhaustion and allocator contracts remain qualified in Ghidra for later review. No game testing or binary changes.

Police-radio follow-up: named detached-assignment and support-recruitment sequence builders. Full assembly/caller checks corrected worker attribution of helper-internal selection logic. Names/comments verified and project saved; totals 2,341 AnalystNamed and 2,230 StaticReviewed. Detailed queue gates remain in Ghidra; no game testing or binary changes.

Pursuit-group radio pass: named the remaining action-sequence builder and verified admission, random selection and shared tail against assembly and caller. Project saved; totals 2,342 AnalystNamed and 2,231 StaticReviewed. No game testing or binary changes.

Network-address layout pass: named inverse record/payload conversions; verified copy direction, 14/12-byte layouts and separate address/data use in caller. Leading value six is documented as an address-record field, without claiming a gameplay opcode. Project saved; totals 2,344 AnalystNamed and 2,233 StaticReviewed. No game testing or binary changes.

Police assignment-window pass: named wrapped-distance reset helper; verified signed bounds, both flag clears and exact assignment record writes. Project saved; totals 2,345 AnalystNamed and 2,234 StaticReviewed. Caller invariants remain qualified in Ghidra; no game testing or binary changes.

Police track-event pass: named event initialization/counter helper and verified record stride, reverse-track selector mapping and saturated low-nibble update. Project saved; totals 2,346 AnalystNamed and 2,235 StaticReviewed. Specific gameplay event remains qualified; no game testing or binary changes.

Pursuit response-counter pass: named counter accumulator; verified branch priority, unsigned selector dispatch, double threshold and unordered comparisons. Project saved; totals 2,347 AnalystNamed and 2,236 StaticReviewed. Counter semantics and caller validity remain qualified; no game testing or binary changes.

Pursuit-target acquisition pass: named conditional acquisition/replacement helper; verified speed-ratio branch direction, target flags and callee refusal paths. Passing wrapper gates does not prove successful replacement. Project saved; totals 2,348 AnalystNamed and 2,237 StaticReviewed. No game testing or binary changes.

Police chase-speed pass: named speed/direction response helper; verified threshold branches, float sign-bit flips, 1.19 cruise multiplier and conditional 0.8 scaling. Project saved; totals 2,349 AnalystNamed and 2,238 StaticReviewed. Policy units remain qualified; no game testing or binary changes.

Connection-default pass: named type-six/type-three wrappers; verified zero-only field defaults, register forwarding and preservation, and delegated return. Project saved; totals 2,351 AnalystNamed and 2,240 StaticReviewed. Transport roles/default units remain partial; no game testing or binary changes.

Network connection-setup pass: named session connection initializer; verified role exchange, cancellation cleanup, retained result and lock-held nonhost wait. Project saved; totals 2,352 AnalystNamed and 2,241 StaticReviewed. Callback/locking invariants remain for Astra; no game testing or binary changes.

Player pursuit-candidate pass: named nearest-candidate scan; verified selection versus reporting eligibility, special participant exclusions, tie metric and report-kind overrides. Project saved; totals 2,353 AnalystNamed and 2,242 StaticReviewed. Report meanings remain partial; no game testing or binary changes.

Vehicle control-transition pass: named low-motion mode transition helper; verified transition priority, raw float-bit gates, control-byte swap and returned flag. Project saved; totals 2,354 AnalystNamed and 2,243 StaticReviewed. Mode meanings and threshold units remain for Astra; no game testing or binary changes.

Smoothed vehicle-control pass: named control/mode updater; verified forced reset path, byte smoothing, mode transitions, countdown and normalized outputs. Project saved; totals 2,355 AnalystNamed and 2,244 StaticReviewed. Profile/rate validity and mode semantics remain for Astra; no game testing or binary changes.

Vehicle/player separation pass: named separation/track-state updater; verified signed segment separation, maximum metric combination, threshold and reinitialization path. Corrected worker interpretation of count fallback and metric clamp. Project saved; totals 2,356 AnalystNamed and 2,245 StaticReviewed. No game testing or binary changes.

Eight-sample track-contact pass: named contact sample processor; verified all-sample iteration, query/material filters, fixed-point conversion and response-result latch. It can apply contact response. Project saved; totals 2,357 AnalystNamed and 2,246 StaticReviewed. Geometry/query contracts remain for Astra; no game testing or binary changes.

Police-stop transform pass: named participant offset transform; verified asymmetric heading constants, side-selected rotation/vector offsets and separate output position. Project saved; totals 2,358 AnalystNamed and 2,247 StaticReviewed. Side/units remain qualified; no game testing or binary changes.

Police-stop track-transform pass: named placement preparation; verified packed-byte extraction, side selection, query validity gates and unchecked alternate-side result. Project saved; totals 2,359 AnalystNamed and 2,248 StaticReviewed. Stop placement contracts remain partial; no game testing or binary changes.

Track-assignment vehicle initialization pass: named initializer; verified player avoidance loop, packed-track/random placement scalar, cruise speed, pursuit reset and bounded random counter. Project saved; totals 2,360 AnalystNamed and 2,249 StaticReviewed. Loop termination and policy units remain for Astra; no game testing or binary changes.

Connection dispatcher/queue pass: named callback dispatcher and queue allocation helper; verified register forwarding, reference counting and allocation-failure status provenance. Project saved; totals 2,362 AnalystNamed and 2,251 StaticReviewed. Callback/failure contracts remain for Astra; no game testing or binary changes.

Indexed AI tuning pass: named profile-class initializer; verified 20-byte tuning stride, 24-byte class lookup, raw jump-table mapping and setting adjustment. Project saved; totals 2,363 AnalystNamed and 2,252 StaticReviewed. Class/difficulty mapping remains qualified; no game testing or binary changes.

Vehicle surface-response pass: named response routine; verified conditional basis damping, common-tail checks and distinct linear/quadratic outputs. Project saved; totals 2,364 AnalystNamed and 2,253 StaticReviewed. Geometry/caller invariants remain for Astra; no game testing or binary changes.

Track-profile control pass: named controller; verified heading smoothing, rate limits, integer division before float conversion and byte output boundaries. Project saved; totals 2,365 AnalystNamed and 2,254 StaticReviewed. Channel meanings and profile/divisor invariants remain for Astra; no game testing or binary changes.

Recent static analysis: expanded pursuit/control, profile interpolation, socket transport, packet packer/unpacker dispatch and family-six service discovery/lifecycle coverage. Full assembly, selected raw constants and embedded diagnostics were checked; detailed names, ABI notes, data-flow evidence and unresolved contracts are in the saved Ghidra project. Live tag refresh confirms 2,404 AnalystNamed and 2,293 StaticReviewed; 1,448 FUN_ names remain. Naming coverage does not measure complete semantic understanding. No additional game testing or executable changes.

Pursuit timer follow-up: verified and named target/timer update; corrected integer-conversion order and branch multiplier from worker interpretation. Detailed evidence saved in Ghidra; target flags, bounds and timing units remain qualified. No additional game testing or executable changes.

Profile data follow-up: named and typed the verified four-byte interpolation index scale; audited saved name/type/comment. Current shared global/constant count:907. Detailed evidence remains in Ghidra; no executable changes or game testing.

Planar response and service-state follow-up: named one vehicle response routine and three DWORD service lifecycle globals. Full response assembly and initializer/shutdown accesses reviewed; saved annotations distinguish observed arithmetic from unresolved physical units and worker synchronization. Detailed evidence is in the Ghidra project. Shared global/constant count: 910. No game testing or executable changes.

Planar response limiter follow-up: named the adjacent limiter after full reachable-assembly review and raw coefficient checks. Documented prior-accumulator overwrite, repeated mutating profile-helper calls, tick-dependent branch, raw-bit comparisons and common override/cap tail in Ghidra. Physical interpretation and enclosing controller remain for Astra; no game testing or executable changes.

Runtime arithmetic follow-up: named three helpers covering DWORD population count, wrapped record-buffer size arithmetic and its zero-return callee. Verified complete bodies and saved annotations; schema and hook purpose remain qualified. No game testing or executable changes.

Resource-context helper follow-up: named four functions covering signed slot lookup, encoded-identifier record search, threshold forwarding and caller-buffer slot initialization. Verified complete bodies, stub effects, widths and error branches; detailed evidence saved in Ghidra. Exact resource domain and buffer ownership remain unresolved. No game testing or executable changes.

Sound request-status follow-up: embedded diagnostic establishes the identifier-search caller as sound-stream status reporting. Named status routine and full-width multiplication helper; documented output states, lock pairing, arithmetic and denominator limits. Updated earlier lookup comment with the new caller evidence. Project saved; exact lifecycle enums and numeric units remain qualified. No game testing or executable changes.

Sound context lifecycle follow-up: named three functions covering caller-memory creation, context counting and request reset. Saved assembly-backed comments include memory partitioning, external/internal handle branches and pending threshold-call ordering/identifier question. Astra follow-up: trace004f3fec ->00511ca0 before publication,0051181c cleanup, registered callbacks and failure ownership. All three Luna workers are completed; their reported helpers were incorporated after parent review. Analysis paused at user request; Ghidra project saved. No game testing or executable changes.

Resumed packet-playback pass: recovered live Ghidra access through the installed MCP stdio client while native Codex Ghidra tools were absent. Named packet-playback stop routine using its embedded diagnostic; documented lock/callback/invalidation sequence. Three Luna workers are reviewing separate cleanup, playback and network helpers read-only. Detailed annotations remain in the saved project; no game execution or executable changes.

Luna validation follow-up: parent verified and saved packet queue signed-range purge, resource slot clearing and masked network record lookup. Added count-underflow/shift-wrap and callback/queue invariants to Ghidra comments. Remaining Luna findings: context shutdown004f43c0 and serializer00513030 require parent review;00511 unnamed-helper search exhausted. No game testing or executable changes.

Sound context teardown follow-up: parent verified Luna report and named context shutdown, including last-context callback removal, resource unregistration and external-handle ownership branch. Existing timed callback removal annotation corroborated. Project saved; teardown concurrency remains qualified. Three workers assigned further bounded read-only reviews. No game testing or executable changes.

Runtime stack helper follow-up: named the verified stack-address minus runtime-record-base calculation; exact stack-depth meaning remains qualified. Registered sound callbacks004f3b44/004f3b60 have executable instructions but no recognized Ghidra function entries; callback recovery and shared-tail analysis remain pending. Serializer worker stack-offset interpretation requires correction before annotations. Project saved; no game testing or executable changes.

Network game-information builder follow-up: parent reconciled worker stack offsets and named the172-byte packet builder/dispatcher. Saved exact field mapping, token/custom ABI, stack lifetime and76 locally unwritten bytes. Astra backlog: resolve virtual transport callback and reserved-field handling before treating those bytes as a runtime defect. No game testing or executable changes.

Sound queue compaction follow-up: parent named identifier removal and documented unconditional one-count decrement despite scanning all matches. Astra backlog: establish unique/present identifier invariants for004f3ab8, recover callback004f3b60 shared-tail ABI and trace playback ownership. If static evidence remains insufficient, later controlled Wine tests should exercise queued stream completion, stop/reset, and last-context shutdown; observe queue count/current index and callback ordering without modifying executable. No runtime testing needed for current annotations. Project saved.

Sound request creation follow-up: named source-kind queueing; corrected stack/register mapping, verified signed byte capacity checks, generation-based identifiers and field initialization. Astra backlog: trace record+18/highWORD+2a initialization, automatic memory-source length traversal, and identifier wrap/lifetime invariants before any runtime fault claim. Project saved; no game testing or executable changes.

Sound API wrapper follow-up: named three wrappers for context memory sizing, external-handle context creation and existing-token request queueing. Verified all register/stack forwarding and wrapped size formula; project saved. Three Luna workers assigned further sound/network helper batches. No game testing or executable changes.

Packet release follow-up: named two helpers for post-release request-field update and current-index advancement. Parent verified full assembly; reentrancy/source-lifetime question added to Astra callback backlog. Live refresh before this pair:2430 AnalystNamed,2319 StaticReviewed; two names added afterward. Three new Luna reports await parent validation (linked sound controls, network free-slot insertion). Project saved; no game testing or executable changes.

Network slot insertion follow-up: named first-free player-record insertion; verified92-byte copy plus two metadata DWORDs, unsigned count-minus-one bound, shift-mask reuse and ambiguous zero return. Astra backlog: establish player-capacity/mask bounds and failure disambiguation in dispatcher005133a0; later controlled multiplayer join/full-slot testing only if static caller tracing leaves a specific gap. Project saved; no game testing or executable changes.

Runtime startup follow-up: parent named stack runtime-state initializer after complete assembly and immediate startup-wrapper review. Documented allocation rounding, size-field write and stack lifetime. Linked sound-control Luna report corroborates existing names/comments; no duplicate renames applied. Project saved; no game testing or executable changes.

Sound packet dispatch follow-up: named exact-tag dispatcher linking release helpers to header/data paths; verified fallback and return forwarding. Astra backlog:004f3d00/004f3ba4 and005114d4 descriptor/schema/ownership tracing, including callback lifetime and local descriptor initialization. Project saved; no game testing or executable changes.

Startup workspace follow-up: named stack-page probe and game-entry workspace wrapper after full assembly/callee checks. Saved comparison polarity, rounded/unrounded size distinction and optional allocation behavior. Deeper termination/workspace purpose remains qualified; no runtime testing or executable changes. Project saved.

Runtime exit follow-up: named finalizer/exit wrapper and hook-to-termination adapter. Verified saved hook pointers, priority split, BYTE-versus-DWORD mode guard and downstream ExitProcess contract. Startup wrapper terminal path now established; mutable hook ownership remains qualified. Project saved; no game testing or executable changes.

MMX/helper callback pass: named DWORD zeroing routine and callback installation helper after complete assembly review. Documented signed count, EMMS state effects and exact installation writes; callback domain remains qualified pending three Luna review batches. Project saved; no game testing or executable changes.

Callback and float-accumulation follow-up: saved three small callback-state helpers and eight selector/accumulation routines after parent assembly review of Luna findings. Comments document pointer-slot indirection, zero/unity fast paths, signed count handling, x87 arithmetic and preserved-register ABI; detailed evidence stays in Ghidra. No executable changes or runtime testing.

Astra backlog — accumulation callback contracts: trace the two gain-selector families through their installer/consumer to establish channel identity, scalar-versus-pair count units, buffer capacity/alias rules and callback state ownership. Prefer static caller tracing first. If runtime evidence is needed later, use controlled Wine audio playback with isolated mono/stereo sources, zero/full/asymmetric gain settings and stop/reset transitions; observe selected callback, source/destination bounds and state lifetime. Do not infer left/right names or a defect from arithmetic alone.

Float-pair accumulation follow-up: parent verified and saved seven sibling gain-selector/accumulator functions. Corrected Luna interpretations of x87 store ordering, pre-guard gain reads and the weighted tail source increment. Pair-count versus scalar-count distinction is documented in Ghidra; no executable changes or runtime testing.

Astra backlog — stepped sampling and interpolation: review005213ab,0052150c with consumers/installer, shared helper00527330 and sibling00521620. Resolve recovered stack ABI, fixed-point phase/carry, cached pair ownership and packed state fields before semantic structure naming. Static analysis first; optional later controlled Wine audio playback at differing source/output rates, repeated buffer boundaries and stop/reset would test continuity and cached-frame lifetime. No defect or exact channel format established.

Fixed-point callback follow-up: parent verified and saved two span calculators, one state-field setter and a stepped DWORD copy callback. Detailed Ghidra comments distinguish signed branches from logical shifts, wrapped arithmetic, source-address alignment, unity bypass and unbounded-by-output prefill. Astra backlog: establish positive-count, step/hold, alignment, destination-capacity and shared-scratch reentrancy invariants for0052125b and pair sibling005213ab before any fault claim. No runtime testing or executable changes. Three Luna workers assigned adjacent callback/interpolation batches.

Interpolation helper follow-up: parent verified and saved shared two-float interpolation/advance kernel. Raw constants establish an approximate fractional scale rather than exact1/65536; overlapping scratch DWORD access includes the following statically zero WORD. Documented do-while positive-count contract and verified caller guard. Astra backlog retains caller buffer headroom, cache transitions, scratch reentrancy and packed state layout; details in Ghidra. No game testing or executable changes.

Boundary interpolation wrapper follow-up: parent saved two-float history wrapper after full assembly/helper/constant review. Comments record up to16bytes input headroom, positive-count requirement, next-pair caching and unsigned phase-versus-step branch. Exact approximate scale retained. Caller buffer ownership and history flags remain in Astra backlog; no game testing or executable changes.

Scalar interpolation follow-up: parent verified and saved shared scalar kernel and two history/carry wrappers. Distinguished helper zero-count behavior, wrapper NONZERO versus signed-positive call guards, cached input headroom and final index overwrite from signed BYTE+16. Astra backlog: resolve this packed-byte policy and paired sibling before naming fields or asserting faults. Detailed arithmetic/ABI in Ghidra; no game testing or executable changes.

Runtime/property helper follow-up: parent saved physical-memory query, descriptor flush and tagged sound callback dispatch after full assembly review. Corrected preserved ESI, parser-failure dispatch path and callback stack cleanup interpretation. Astra backlog: establish tag92/93 ordering, writable cursor and callback registration/ownership for00522d08; parser failure alone does not suppress dispatch. Detailed evidence in Ghidra; no executable changes or game testing.

Audio table initialization follow-up: parent saved scaled-prime search and mapped-effect table initialization. Verified existing truncation helper, below-two candidate increment behavior, four buffer partitions and changing0.1-times0.7 scale sequence. Astra backlog: establish table capacity/input ranges and exact effect schema before field renaming; x87 power special cases remain pending caller/helper review. No game testing or executable changes.

Descriptor flags follow-up: parent saved lazy character-device flag lookup after full assembly review. Documented exclusive upper bound versus flush helper inclusive bound, probe-attempt caching and ambiguous zero result. Limit/table consistency and synchronization remain qualified in Ghidra; no game testing or executable changes.

Raster lifecycle follow-up: parent saved backend initialization/shutdown after full assembly review. Corrected worker interpretation of nonzero-input window setup: it changes the EBX flag but still calls initializer. Comments cover command callback stack cleanup, timed callback pairing and post-unregister register preservation. Astra backlog: backend command schema, external/window ownership and failure/reentrancy paths; later controlled window/fullscreen transitions only if static tracing leaves a gap. No game testing or executable changes.

Pool resize follow-up: parent saved within-span allocation resize after complete assembly and callee ABI review. Corrected generic payload-move interpretation: overlap-safe move relocates trailer bytes. Documented neighbouring free-block absorption, clamped capacity, split threshold and original-pointer return. Astra backlog: allocator sentinel/minimum size versus stored size, alignment, trailer and free-list invariants; static caller tracing first, runtime allocation stress only if needed later. No executable changes or game testing.

X87 power follow-up: parent saved unsigned16-bit integer-power helper after full assembly and raw opcode review. Resolved ambiguous one-operand Ghidra FMUL display using DC C9 encoding, confirming accumulator destination. Wrapper special cases and exception contracts remain for Astra; no game testing or executable changes.

Tagged sound format follow-up: parent saved platform-format resolver after full assembly and callback stack-offset review. Documented seven callback args, callee cleanup, tag defaults and unconditional output-pointer write before method selection. Astra backlog: parser schema/tag presence, callback registration and abort-return assumptions; static callers first, optional future controlled supported-format playback only for specific remaining gaps. Live prior refresh:2478 AnalystNamed,2367 StaticReviewed,1391 FUN_ names; list_functions3902 entries. One named/reviewed resolver added after refresh. Counts describe annotations, not semantic completion. No game testing or executable changes.

Pair copy/carry follow-up: parent saved remaining stepped pair-copy and carry interpolator after complete assembly review. Confirmed deliberate ESP use as a sample register with shared saved-stack pointer, source8-byte alignment, and packed BYTE+1e index overwrite. Astra backlog: asynchronous/reentrant safety of shared stack scratch, prefill bounds and packed-byte initializer/caller policy. Detailed evidence stays in Ghidra; no executable changes or runtime testing.

Runtime string follow-up: parent saved terminator classification, multibyte character advance and ASCII code-unit uppercase helpers after complete assembly review. Comments retain exact0/1/2 results, dangling lead-byte handling and low16-versus-full-register semantics. Detailed evidence in Ghidra; no executable changes or runtime testing.

Runtime signal follow-up: parent saved three signal4/7 wrappers after complete shared-tail/callee review. Distinguished supplied EDX sentinel from independently queried handler, exact0/1 return polarity and RET4 cleanup. Sentinel enums and exception caller contracts remain qualified in Ghidra; no executable changes or runtime testing.

Current analysis priorities: focus static effort on multiplayer/session/player capacity, race/lap limits, track/car slots, opponents, pursuit/police difficulty, traffic density and vehicle physics. Generic CRT, signal, x87 math and unrelated audio/MMX helpers deferred unless needed by relevant game paths. Three Luna workers redirected to networking, pursuit/traffic and race-configuration caller/callee batches. Broad goal remains active; no executable modifications or additional game testing. Complex contracts and specific future runtime scenarios belong in Astra backlog.

Focused traffic/lap pass: rechecked lap codec2/4/8 and traffic-limit accessor assembly; expanded traffic comment with32-byte stride, shared race selector and unproven per-mode table values. Static read of table neighbour failed; initialization/mapping must be traced before quoting concrete caps. Astra backlog: relate mode table initialization to on/off traffic selection and active-population comparison; optional later controlled mode/traffic runs only for unresolved observations. Generic no-op police stubs deferred. Current active goal is the focused game-system static analysis goal; unrelated runtime/audio helpers deferred. No executable changes or game testing.

Focused multiplayer roster pass: parent expanded three existing function annotations for fixed8-entry WORD identity lookup, readiness iteration and96-byte received profile records. Corrected receive local-ID extraction (WORD2278 from unaligned DWORD2276), distinguished identity/count/slot fields and exact packet-start copy. Astra backlog: trace upstream packet length/slot validation, participant-ID allocation and duplicate/occupancy invariants before any multiplayer capacity change or fault claim; optional later controlled join/leave/full-roster tests if static dispatch tracing leaves gaps. No executable changes or runtime tests.

Traffic tuning initialization pass: parent verified full initializer/setter assembly and raw mode jump table; saved precise per-row cap/delay initialization and override precedence in Ghidra. Modes0/3 supply nonzero caps,1/2 zero, configuration bit8 forces15 and zero delay; optional row3 override still passes through same setter. Astra backlog: assign user-facing mode/flag names, valid track selector range and later writes before translating these static caps into live density claims. No executable changes or runtime testing.

Traffic reactivation policy follow-up: parent saved exact1920-tick gate, countdown reset/decrement/retry behavior and signed active-population comparison. Delay getter adds200/400 configuration modifiers even when initialized base delay is0. Units/category invariants remain qualified; details in Ghidra. Car-record Luna evidence identifies50 saved per-player records, distinct from simultaneous race participants, pending parent validation. No game testing or executable changes.

Saved car-record capacity pass: parent expanded free-slot search and occupancy getter annotations after full assembly review. Established50 records per player at48-byte stride, AL-only occupancy result with nonzero upper EAX and invalid/full search=-1. These saved records are separate from simultaneous race and network slots. Astra backlog: reconcile profile serialization/model registry limits before any future car-capacity changes; no implementation in scope. No executable changes or game testing.

Opponent/police tuning pass: parent expanded profile lookup, police cap getter and cruise-speed setter after complete assembly/raw1.1 coefficient review. Documented mode-specific profile fallback, cap clipping (including unordered comparison), independent sign flips and distinct police/opponent tuning sources. Astra backlog: police flag/mode policy and speed units, with later controlled pursuit difficulty scenarios only if static tracing remains inconclusive. EXE SHA256 still matches recorded baseline2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb. No game testing or executable changes.

Multiplayer dispatch pass: parent expanded dispatcher, callback installer and packet-state initializer annotations after full assembly/raw handler-table review. Type3 routes to participant-state receive; callback read occurs before abort gate. Corrected connection stride to108bytes, distinct from96-byte participant profiles and8-entry identity map. Astra backlog: trace connection+20 invocation/framing and ECX setup/preservation before final capacity or packet-validation conclusions; optional later controlled multiplayer join/leave scenarios if needed. No game testing or executable changes.

Focused annotation precision pass: corrected police cap flag notation to bit0/mask0x01 and made profile/table dereferences explicit. Rechecked original00477170: already named countdown visual setter, outside current capacity/physics priorities. Three Luna workers assigned lap-count consumers, physics and connection initialization contracts. Project saved; no executable changes or runtime testing.

Lap-limit and boundary-physics pass: parent reviewed full assembly, renamed two relevant routines and saved detailed comments in the Ghidra project. Lap estimates use the configured lap count directly without a local clamp; array extents and upstream validation remain Astra backlog before future lap expansion. Boundary sampling has distinct inline-point and repeated segment-point paths; coordinate units, material policy and the vehicle state threshold remain unresolved for Astra and optional later runtime testing. No executable changes or game testing.

Boundary-normal follow-up: parent named and documented the fixed-point edge-normal builder after assembly and normalizer review, correcting the unsupported assumption that invalid selectors yield zero. Astra backlog includes caller selector invariants, normal orientation and physical units; details remain in Ghidra. Three Luna workers continue read-only lap-limit, multiplayer framing and physics investigations. Project saved; no executable changes or runtime tests.

Multiplayer initialization contract resolved: parent verified register preservation through helper paths, establishing seven callback records at108-byte stride and the separate844-byte zero-fill. This does not establish the player limit. Lap display helper named and documented separately from capacity logic. Remaining Astra work: transport framing/roster policy, upstream lap validation and per-lap allocation extents. Detailed evidence saved in Ghidra; no executable changes or runtime testing.

Car registry reconciliation pass: parent verified50-record scan, missing-model insertion, full-table skip and independent registry index ceiling; expanded existing Ghidra annotation. Saved car/profile capacity remains distinct from race participants. Astra backlog retains serialization compatibility, registry loading and tuning semantics. Worker multiplayer follow-up found receive framing with a configurable bound whose initialization needs tracing, plus short-consumption behavior; pending parent validation before stronger conclusions. Project saved; no executable changes or runtime tests.

Physics envelope and multiplayer framing pass: parent named the horizontal vehicle-object envelope check and verified projection/extent comparisons. Expanded receive-frame annotation with actual stack metadata offsets, correcting unsupported buffer-size inference. Astra backlog: physics basis normalization/units; transport state length initialization, zero-length handling, participant slot validation and short frame consumption. Three workers continue relevant read-only traces. Ghidra saved; no executable changes or runtime tests.

Multiplayer callback route verified through full descriptor/unpacker/fallback assembly and saved in Ghidra. Temporary fallback payload ownership is synchronous; configured frame bound, nonempty-payload invariant and indexed transformations remain Astra backlog. Multiple Ghidra instances are now running: bridge sessions must explicitly call connect_instance with project nfs3_decomp before NFS3 program tools. Lap-history worker located two additional direct array consumers, pending parent review. No executable changes or runtime tests.

Lap-history consumers reviewed and named: parent verified two popup renderers use configured lap count directly over per-lap time/float arrays without local clamping. Documented minimum seeding even at nonpositive count and float-highlight index lacking initialization when no positive metric exists. Astra backlog: upstream count validation, backing storage/serialization and missing-data display behavior; details in Ghidra. Project saved; no executable changes or runtime tests.

Vehicle box-contact pass: parent reviewed and named the signed-corner witness test, recording extent comparisons, acceptance/rejection side effects and candidate-position writes in Ghidra. Astra backlog: precomputed transform provenance, contact manifold use, units and shared scratch lifetime; witness testing alone is not full collision-response reconstruction. Project saved; no executable changes or runtime tests.

Police chase-speed pass: parent verified full arithmetic branches and decoded coefficients directly from program data, expanding existing Ghidra annotation. Documented mode/flag-dependent formulas, latch activation, sign flips and interpolation without a final local cap clamp. Astra backlog: gap/flag producers, target speed-field semantics, units and difficulty linkage; later controlled pursuit tests only if needed. Physics worker also mapped reverse box-corner witnesses and transform setup, pending parent validation. Project saved; no executable changes or runtime tests.

Reverse box-corner pass: parent named/reviewed the mirror contact helper, confirming first-box corner against second-box extents and shared candidate-position writes. Both directional helpers are documented in Ghidra; transform/classification wiring and downstream response remain for verification/Astra. Worker triage now targets the witness resolver rather than assuming these tests implement complete collision response. Project saved; no executable changes or runtime tests.

Pursuit-context provenance verified: relative gap is wrapped track-index subtraction with direction adjustment; its negative flag is derived from that gap, not demonstrated difficulty configuration. Parent saved producer/consumer contracts and stale-context null-target behavior in Ghidra. Astra backlog also includes SelectVehicleBoxContactNormal: relative-motion versus penetration selection, normal orientation and downstream response; optional controlled vehicle collisions/pursuit runs later. Multiplayer frame-limit initialization remains unresolved; candidate callback cap is not linked to the receiving state. No executable changes or runtime tests.

Track selector/resource pass: traced selector xrefs and named the track-stem filename builder after assembly/raw format review. Folder and filename encode the selector in hexadecimal with minimum widths, providing no capacity clamp. Astra backlog: selector validation, root setup, shared buffer extent and resource inventory before track expansion. Ghidra saved; no executable changes or runtime tests.

Traffic model-pool pass: parent verified track-selector jump table, seven counted pools, duplicate model entries and usage-balanced selection. This controls model variety separately from active population. Selector0..10 support differs from the nine-row cap initializer; special-track reachability/tuning, usage reset/wrap and model availability remain Astra backlog. Detailed pool mappings saved in Ghidra; no executable changes or runtime tests.

Traffic selection contract refined: parent verified deterministic generator always returns an unsigned byte, ensuring nonnegative pool remainder for reviewed positive counts. Signed-index uncertainty belongs inside the generator lookup, not traffic-pool indexing. Usage selection/wrap and1024-byte reset coverage documented in Ghidra; reset timing and generator input domain remain unresolved. Workers redirected to special-track tuning and opponent helpers. Project saved; no executable changes or runtime tests.

Traffic data labels added: seven verified counted model pools and their track dispatch table now have descriptive labels/comments in Ghidra; creation verified and project saved. Opponent helper triage found direct small steering/braking callees already named. Astra backlog adds FUN_00407fa0 (complex controller calculations called by SelectAIControllerAndIntegrateMotion); inspect control-field outputs and runtime steering/braking scenarios later if needed. No executable changes or runtime tests.

AI braking/acceleration review: existing detailed comments corroborated against full assembly. Added four verified braking coefficient/threshold data labels to aid cross-function work; profile-return branches converge on one multiplier here. Astra backlog retains control-byte semantics, acceleration-table units and catch-up policy producers. Ghidra saved; no executable changes or runtime tests.

Race-menu writer verified: enabled reconciliation decodes lap option to2/4/8; skip guard preserves prior values, and other roster/network writers still prevent a game-wide bound claim. Documented mode-specific lap/track writes and unaligned option extraction in Ghidra. No general track clamp in this writer. Astra backlog: alternate writers and normalization order before capacity changes. Project saved; no executable changes or runtime tests.

Multiplayer wire-layout pass: parent corroborated race-settings sender and created/verified reusable40-byte Nfs3RaceSettingsWirePacket datatype in Ghidra, retaining unknown/conditionally stale bytes. Documented low-byte truncation, separate lap-option/count fields and model-selector caller contract. Astra backlog: receiver validation/consistency, special-track reachability to traffic tuning and configured frame bound. Project saved; no executable changes or runtime tests.

Race-settings receive/application path verified: handler renamed to reflect type2 packet and40-byte datatype. Cached lap/track bytes are zero-extended by client application without local range or option/count consistency checks, unlike menu decoding. Astra backlog: upstream validation/host identity, reconciliation order, special-track reachability and flag-lock snapshot behavior. Details saved in Ghidra; no executable changes or runtime tests.

Saved-car datatype pass: reusable48-byte Nfs3SavedCarRecord created and layout verified, with unknown padding and opaque tuning payload retained; setter comment links storage contract. Separate occupancy setter and50-slot per-player validation are established, distinct from race slots. Three workers assigned per-lap storage, participant identity packets and profile producers. Ghidra saved; no executable changes or runtime tests.

Multiplayer roster review: corrected the saved handler comment to distinguish state indices 1 through 8 from index 0 and roster positions from compacted remote rows. Confirmed the fixed packet copy starts at the packet itself. Astra backlog retains upstream packet-length/sender checks, count normalization and first-receive synchronization. Track-dependent cop asset selection is now named/documented separately from police population and difficulty. Detailed evidence remains in Ghidra; project saved, no executable changes or runtime tests.

Participant snapshot storage corroborated: fixed record and category strides agree across copy and lookup routines; producers do not locally clamp qualifying counts to the category stride. This does not establish per-lap array capacity. Astra backlog retains source allocation, qualifying-count invariants and lap-array extent/initialization; detailed evidence saved in Ghidra. No executable changes or runtime tests.

Network participant-state review: connected snapshot eligibility to the eight-word state array. Found that the inactive-state updater accesses a connection slot before its later bounds check and copies broadcast state after unlocking. Astra backlog: caller index contracts, state semantics, sender validation and concurrent snapshot behavior. Exact ordering documented and saved in Ghidra; no executable changes or runtime tests.

Participant-state caller pass: connection-loss callback checks lookup failure, whereas two send-failure paths pass the lookup result directly to the updater. Synchronization iterates advertised roster count without a local literal slot cap. Astra backlog now explicitly includes connection membership/lifetime, failed lookup reachability and roster-count normalization. Saved call-site evidence in Ghidra; no executable changes or runtime tests.

Roster producer/layout pass: verified the local builder starts with one participant and scans seven remote rows, establishing its conditional 1..8 count bound. Created and verified a reusable 124-byte roster wire datatype with unknown bytes retained. This producer bound does not validate incoming rosters; name-slot termination/length and other count writers remain Astra backlog. Project saved; no executable changes or runtime tests.

Participant-state wire datatype added and verified against receive assembly: preserves the unknown header byte and eight state words. Receiver documentation links sender layout and unresolved validation/state semantics to the Astra backlog. Detailed layout saved in Ghidra; no executable changes or runtime tests.

Collision-normal selector reviewed in full assembly: established threshold, body ordering, finite-input tie rules and the distinction between relative-motion branch selection and single-body motion scoring. Saved detailed contract in Ghidra. Astra/runtime backlog retains basis/frame consistency, physical units and moving/moving versus stationary contact response. No executable changes or runtime tests.

Collision caller chain verified: corner classifications determine normal-selector body order; other contact families bypass that selector. Pair separation refreshes position projections between up to four calls and returns the last helper result. Astra backlog retains scratch-frame/sign consistency, sample-family normal production and convergence under controlled contacts. Detailed call-site evidence saved in Ghidra; no executable changes or runtime tests.

Mass-weighted separation verified through vector helpers: fixed positional correction follows center difference rather than selected contact normal; return value reports invocation, not convergence. Zero direction is not rejected. Astra/runtime backlog retains coincident centers, mass invariants, correction units and downstream normal use. Detailed contract saved in Ghidra; no executable changes or runtime tests.

Collision iteration wrapper verified: outer and inner loop bounds permit at most 132 positional correction calls before one impact-processing call. Impact receives shared contact point; direct normal consumption remains unproven in this path. Astra backlog includes witness lifetime after a final no-contact result, convergence and response/alias tracing. Saved in Ghidra; no executable changes or runtime tests.

Impact-response helper review: linear gating uses normalized contact offset and response vector; angular response has a separate offset-length gate. No shared contact-normal read appears in the reviewed helper body. Documented stack arguments and numeric return semantics in Ghidra. Astra backlog retains response weighting, inertia/units, angular clamp and aliased normal use elsewhere. Project saved; no executable changes or runtime tests.

Angular clamp reviewed: verified independent component clipping, initial numeric limit and unordered-input branch behavior. This can alter vector direction and is not a magnitude cap. Saved exact contract/data comment in Ghidra; units and indirect configuration writers remain Astra backlog. No executable changes or runtime tests.

Impact attenuation constants verified: response magnitude is compared with mass times a threshold and attenuated once, rather than capped. Numeric constants and rotational-response conversion hypothesis documented in Ghidra; physical units remain unresolved. Project saved; no executable changes or runtime tests.

Pair-impact event writes reviewed: distinguished response refresh, conditional partner/contact metadata and strict counter threshold. Prior metadata can remain when update branches are skipped. Astra backlog retains counter meaning/reset policy and controlled asymmetric-impact observations. Saved in Ghidra; no executable changes or runtime tests.

Traffic accessor documentation reconciled with recovered initializer/setter evidence, replacing the stale initialization-unknown note. Verified setter override and an unwritten record field; special-track domain and subsequent writers remain Astra backlog. Detailed contracts saved in Ghidra; no executable changes or runtime tests.

Scope audit follow-up: named/documented the default configuration initializer, grounding another track/lap writer and distinguishing direct defaults from helper register assumptions. Remaining static priorities: config load/reset ordering and roster-specific lap writers; multiplayer connection lifecycle/count normalization; special-track table reachability; car registry versus participant allocation; police profile/control producers. Complex physics/frame/unit and runtime cases remain Astra backlog. All requested subsystems have partial evidence, but coverage is not yet complete. Ghidra saved; no executable changes or runtime tests.

Mode-specific lap/track writers verified: roster builders override actual lap count independently of encoded menu option and derive tracks from separate series/progression tables. Documented signed extraction/stride and upstream index contracts in Ghidra. Astra backlog retains initialization order, option/count reconciliation and progression-domain validation. Project saved; no executable changes or runtime tests.

Transport-two session setup reviewed: supplied lap count remains literal while option encoding maps unrecognized counts to the first option; fallback endpoint bypasses supplied race-setting copies. No local track-domain clamp. Direct scalar xrefs did not identify the supplied-count producer, so bulk setup population/validation remains Astra backlog. Saved in Ghidra; no executable changes or runtime tests.

Supplied network setup producer identified: indexed command-line decimal parsing writes race/track/lap fields, explaining absent direct scalar write xrefs. Literal lap value flows to session setup; branch-local range checks are absent. Replaced producer-unknown call-site note in Ghidra. Astra retains whole-path argument acceptance and downstream normalization. Project saved; no executable changes or runtime tests.

Command-line final acceptance gate reviewed: required endpoint/name/setup-presence checks do not validate lap/track/race domains. Producer-to-session path now documented; whether downstream race reconciliation replaces supplied values remains unresolved. Added storage cross-reference in Ghidra for future tracing. Project saved; no executable changes or runtime tests.

Direct-network frontend handoff verified: supplied participant-number option selects client versus host startup, and success rejoins the normal frontend loop. Therefore unchanged command-line lap/track reachability is not yet established. Documented roster-wait gate and one-shot flag clearing; downstream menu transition order remains Astra backlog. Ghidra saved; no executable changes or runtime tests.

Track-resource predicate clarified: environment compatibility is not track-domain/resource-existence validation. Caller inspection also identified a separate signed sector-candidate index contract; broader resource batching semantics are deferred to Astra rather than guessed. Saved evidence in Ghidra; no executable changes or runtime tests.

Car-model index cache reviewed: verified upper bound, missing negative guard, null-miss behavior and exact clear size; identified discovery/sort invalidation callers. Distinguished model lookup limit from tuning slots and race participants. Astra retains registry storage and mutation/invalidation contracts. Ghidra saved; no executable changes or runtime tests.

Registry discovery/count chain reviewed: per-model allocation and linked-list append/recount do not locally enforce the lookup cache limit. Frontend consumers use recounted count with the bounded getter, so overall model capacity remains a cross-system contract. Saved precise evidence; directory/resource/helper bounds and frontend storage remain Astra backlog. Ghidra saved; no executable changes or runtime tests.

Car capacity follow-up: directory enumeration has no local count cap, while discovery immediately passes each accepted index to a resource loader using the bounded model getter without a null guard. Thus lookup capacity constrains discovery resource setup as well as frontend access. Saved call-chain evidence; overall over-limit reachability and dependent storage remain Astra backlog. Ghidra saved; no executable changes or runtime tests.

Car-settings capacity follow-up: verified that FEC loading retains an unchecked bounded-registry result while filename getters have separate fallback index domains. Version-one settings subsequently write through the retained model pointer; filename resolution does not prove model validity. Also documented unchecked payload read counts. Astra backlog retains discovery index reachability, static fallback table domains and malformed-file behaviour. Detailed call-site evidence saved in Ghidra; no executable changes or runtime tests.

Resource-ID domain pass: verified static fallback pointer/string samples for directory and archive getters. Their biased table addressing and broad branch ranges do not establish actual table capacity; object archive IDs are separate from dynamic car registry slots. Replaced dated getter comments with precise undated contracts in Ghidra. Astra retains intended ID sets, physical table extents and caller validation before capacity changes. Project saved; no executable changes or runtime tests.

Network cleanup dispatch verified: service descriptor supplies an indirect method and object, while the seven-slot cleanup loop forwards both the original argument in EDX and the scanned slot pointer in EBX. This corrects the earlier incomplete argument description. Documented service-record stride and unchecked lookup-failure dereference separately from participant indexing. Astra retains callback identity/ABI, selected-service membership and actual ownership/lifetime semantics. Ghidra saved; no executable changes or runtime tests.

Network shutdown chain reviewed: verified seven-record host cleanup, unchecked close results before connection-count decrement, and separate payload-buffer release. Direct wrappers do not establish active-field invalidation; indirect callback/lifetime and repeated-close invariants remain Astra backlog. Distinguished descriptor interface tables used for service operations and payload comparison. Detailed evidence saved in Ghidra; no executable changes or runtime tests.

Admission/count chain verified: reservation count is separate from pending depth and decremented by close/failure paths. Admission gates seven reservations while the pending request ring wraps six records; enqueue has no local full check, dequeue relies on its caller empty check. Reachable overfill is not established. Astra backlog: occupancy/callback sequencing, initial reservations and producer name bounds. Detailed evidence saved in Ghidra; no executable changes or runtime tests.

Admission producer/reset follow-up: transport-two initialization resets reservation and pending depth to zero; no local-player reservation explains the six-record/seven-reservation distinction there. Host NPS connection events feed admission without a queue-depth check, and the queued payload has only its first byte explicitly initialized locally. Astra retains callback scheduling/burst reachability and trailing-payload consumers. Detailed evidence saved in Ghidra; no executable changes or runtime tests.

Pending admission datatype created and layout verified:31-byte record with11-byte name storage and20-byte opaque endpoint payload; not applied to live memory/prototypes. Traced payload copy into endpoint and byte-ID lookup across eight records without active-record filtering. Astra retains full-ID versus byte-ID contract, stale identity handling and remaining payload consumers. Ghidra saved; no executable changes or runtime tests.

Race-loop state cleanup verified: state2 becomes1 after close wrapper returns even on early-out/failure, preventing repeats in that scanner while state remains1. This is distinct from endpoint-flag-based host cleanup and does not establish global idempotence. Configured participant count remains unclamped locally; state concurrency and retry policy are Astra backlog. Detailed contract saved in Ghidra; no executable changes or runtime tests.

Pursuit count provenance verified: cleanup participant count is human racers plus human police, distinct from total vehicles including AI and traffic. Network human classification loops over signed advertised roster count without a local eight-slot clamp. Connected this producer to cleanup/count-validation backlog; precise call-site evidence saved in Ghidra. Astra retains incoming count normalization and fixed-storage safety before future pursuit expansion. No executable changes or runtime tests.

Police role producer linked: discovery metadata sets the model police mask consumed by pursuit human-role classification. Distinguished this role flag from difficulty/profile tuning and documented adjacent flag mappings without guessing their meanings. Updated undated function contract and saved Ghidra; metadata validation/later writers remain Astra follow-up. No executable changes or runtime tests.

Network pursuit budgets recovered: racer-only, police-only and mixed-human branches allocate AI/traffic differently; police-only forces at least one AI opponent. Constructor calls corrected a reversed AI count-field description:520 is opponents,524 is police. Saved exact formulas and corrected total-count annotation in Ghidra. Astra retains abnormal human-count reachability and role/difficulty scenarios. No executable changes or runtime tests.

Native MCP resumption check: configured bridge connects to nfs3_decomp and reports analysis/comment/save tools loaded, but this Codex turn exposes only bridge management tools; invoking the analysis tool through the available tool registry fails. Do not launch duplicate Python/stdio bridges. Pending native tool exposure refresh; Luna workers perform read-only scratchpad/backlog and bridge-registration audits meanwhile. No new Ghidra annotations or runtime findings claimed in this pass.

Luna backlog consolidation (proposed tests, not executed): Astra should prioritize two-peer setup/first synchronization; lobby join/leave/disconnect and reservation/queue transitions; pursuit racer-only/police-only/mixed-role budgets with traffic; controlled vehicle/wall collisions; and slopes/rollover/contact recovery. Use the existing function contracts in nfs3_decomp and the subsystem backlog above. Multiplayer tests require suitable peers; burst-capacity testing requires a controlled multi-peer setup, not merely repeated sequential joins. Static tracing should precede runtime tests, and ordinary play does not by itself establish queue capacity or numerical physics units. Luna found no contradictory AI count mapping in the current scratchpad.

Native bridge exposure diagnosis: Luna reviewed installed bridge source. When no Ghidra instance is available at bridge startup, only eight management tools are initially registered; later connect registers analysis tools and sends tools/list_changed when request context is available. This session still exposes the initial management list despite successful connection. Existing no-lazy configuration is correct; installed CLI has no startup-wait option. Refresh/restart Codex with nfs3_decomp already open is the next recovery step. This is evidence of a tool-list refresh mismatch, not proof of a Codex update regression. No bridge/package/config changes made.

Native MCP recovery verified by actual disassembly, annotation readback and successful project save. Pursuit traffic construction gate reviewed: disabled setting clears traffic budget before total count; special local-role flag branches can force traffic enabled with a three-record budget. Distinguished enable policy, roster budget, active population cap and model variety. Detailed contracts saved in Ghidra; special-flag provenance remains Astra/static follow-up. Luna continues independent lap reconciliation tracing. No executable changes or runtime tests.

Pursuit override flag producer found: indexed command-line flags write the containing DWORD, explaining missing direct byte-write references. Parser table index21 maps to the traffic/AI override bit. Keyword identity/table initialization remains unresolved from static bytes; do not guess a cheat/mode name. Exact producer arithmetic saved in Ghidra; Astra retains initialization provenance if static tracing cannot resolve it. No executable changes or runtime tests.

Override flag reachability qualification: static command-line table maps most entries, including the relevant index, to one empty string. Ascending first-match scanning would select an earlier identical entry if bytes remain unchanged. Therefore recovered bit-setting arithmetic establishes a possible indexed producer, not a usable distinct option in this build. Saved table evidence in Ghidra; indirect mutation and flag provenance remain unresolved. No executable changes or runtime tests.

Lap-ordering parent verification corrected Luna interpretation: direct-network zero/failure returns before setup menu, whereas successful wrappers rejoin it. Menu guard compares incoming menu-name argument with postgame, not the proposed global string; setup invocation clears guard initially. Normal body reconciles after callback before checking its newly returned exit result. Saved verified ordering in Ghidra; later guard mutations and roster/network writers still prevent a whole-path lap-limit claim. No executable changes or runtime tests.

Lap reconciliation guard audit: direct xrefs identify only menu-prologue writes; setup initializes guard clear and postgame sets it. No separate direct scalar mutation found. Lap decoder has only the reconciliation direct call site, reinforcing that2/4/8 is this writer policy rather than universal capacity. Nested menus/indirect writes and later roster/network writers remain qualified. Evidence saved in Ghidra; no executable changes or runtime tests.

Pursuit stop-limit consumer verified: officer counter uses exact equality, target counter uses signed greater-or-equal, and target count indexes a separate16-byte-stride timing table even after terminal-state assignment. Future lap/pursuit expansion therefore needs timing-table extent and post-threshold caller validation, retained for Astra. Detailed evidence saved in Ghidra; no executable changes or runtime tests.

Pursuit timing-table chain linked: stop beginning reads a second row field using the pre-finalization count, while finalization reads the first field after increment. A separate officer flag chooses fixed timing instead. Neither local read validates index; raw sampled rows do not establish table extent. Saved data comment in Ghidra; count lifecycle/table extent and timing units remain Astra backlog. No executable changes or runtime tests.

Track reconciliation parent verification: mode1 menu copies the sequence first element (static zero), while later roster construction indexes that sequence by progression. Mode2 also writes zero; other modes retain selector. Recorded raw sequence samples without treating adjacent bytes as extra tracks or claiming whole-path bounds. Ghidra saved; special-track reachability and progression validation remain Astra/static backlog. No executable changes or runtime tests.

Series progression initialization verified: frontend setup clears the progression storage before choosing its setup route; mode1 track index starts zero on this path. This establishes initialization, not a bound on later progression or alternate profile loads. Verified zero-fill helper contract and saved call-site evidence in Ghidra. Luna continues index update/bound tracing. No executable changes or runtime tests.

Series update/reset boundary pass: verified wrapping progression increment and inclusive17-WORD initial rank reset, distinct from32-byte result clear. Last reset write reaches the adjacent points field; intent/schema remains unresolved rather than assumed defective. Saved exact loop evidence in Ghidra; terminal-series gate and rank/points layout retained for Astra/static tracing. No executable changes or runtime tests.

Series result ordering verified: qualifying scoring/increment occurs after snapshot normalization and before later result-query gates, without a surrounding terminal-series check. Gate helper performs its query before applying forced-zero flag; temporary index-map context is restored by wrapper. Saved call-chain evidence in Ghidra; next-race continuation policy remains the key progression bound question. No executable changes or runtime tests.

Series roster dispatcher verified against raw jump-table entries: mode1 reaches the indexed track builder without a local progression bound. Distinguished race-mode validation from series-index validation. Luna’s bounded next-race trace places the remaining terminal-policy question in postgame indirect menu callbacks; no count-eight guard established. Detailed dispatcher evidence saved in Ghidra; callback ownership and terminal behaviour remain Astra/static follow-up. No executable changes or runtime tests.

Postgame callback recovery: static descriptor points to previously undefined code. Created and named the menu-entry/action initializer in Ghidra; it installs race/session-dependent callbacks, providing concrete continuation targets. Descriptor loader mapping and series terminal policy still require tracing. Detailed descriptor evidence saved in project; no executable changes or runtime tests.

## Review, reconciliation and handoff

### Historical backlog reconciliation

The focused reports refine the older unresolved prompts above. The physics
full-copy default image is initialized and available before race loading;
source lifetime, aliased writes, malformed parsing and shared ownership remain
open in [physics parser defaults](physics-parser-defaults.md).

The recovered socket-select worker and type1 frame-limit producer are documented
in [network roster admission](network-roster-admission.md). They do not resolve
the separate service-discovery worker, lobby admission, queue capacity, sender
authority or concurrent teardown contracts. Local transfer read units and
receiver stages are established in [archive directory contract](archive-directory-contract.md);
peer outcomes, marker waits, cleanup and model admission remain open.

Six timed-event identities and normal/reverse spike-contact captures supersede
the early uncertainty about spike-strip identity and observed contact. The
bounded normal-direction local police reset/cooldown capture is also resolved.
[Spike-strip evidence](spike-strip-runtime.md) and
[reset contract](pursuit-assist-reset-contract.md) retain the distinct open
roadblock placement, reverse/seam, contact-role, capacity, handling and broader
reset questions. The SCRATCHPAD statuses remain bounded accordingly.

Audio conversion, voice-record ownership and numerical contracts remain a
separate Open table item; host shutdown findings do not close them. Complex
residuals remain assigned to Astra.

### Astra ledger evidence-link audit

The current ledger has 50 Closed, 36 Partial and 1 Open investigation rows.
Every Closed row has an evidence link; all linked local files and Markdown
heading anchors exist. The [audit inventory](astra-ledger-link-audit.json)
records the row titles and targets. This is structural verification only:
it does not prove the linked claims, close the remaining contracts or imply
a completion percentage. Complex unresolved work remains deferred to Astra
under the model boundary recorded in SCRATCHPAD.md.

### Backlog reconciliation: static rotation and recovery gates

Luna compared the current ledger with preserved original evidence. Corrected
two overly broad unresolved descriptions: byte7 selects quarter/three-quarter
turn rotation in00403180;00409b70 has strict384-tick attempt spacing after
startup tick1152, pursuit/network suppression and timestamp-before-reset.
These are preserved static findings from astra-backlog-context.md, not fresh
runtime validation. Observed placement, actual reset success, suppression
behavior and cadence questions remain open. Both parent rows remain Partial;
no additional Closed row was created.

### Focused ledger reconciliation: audio and frontend

Luna audited archive/resource/audio/music and frontend/input/window/screenshot
rows against their focused reports. Parent checked audio-conversion-contract.md
and the saved toggle-menu/tooltip evidence before narrowing stale residual
phrases. Audio packer/pitch local mechanics are established; numeric admission,
ambient state and ownership remain open. Frontend AL-only result behavior and
local mode4/tooltip mechanics are known; prototype typing, caller provenance,
layout consumption and the explicit tooltip boundary questions remain open.
No reviewed parent row qualifies for full closure, and no new Closed rows
were added. Live Ghidra comments corroborate the retained replay endpoint
and race-finalization boundaries. No executable/runtime changes were made.

### Gameplay and networking backlog reconciliation

Luna reviewed multiplayer, movement, car registry/transfer and series rows
against focused evidence reports. Parent checked the offline action-to-race
section: action6 reaches RunRaceSession locally, while concrete dispatch
of disabled racenow remains unproved. Corrected the ledger accordingly.
A separate Luna review covered physics, AI, personality, traffic, pursuit,
spikes, collision and reset. Parent checked the reset-placement and contact
geometry reports: static ten-pass fallback and candidate geometry are known;
dense placement correctness and runtime/exceptional geometry remain open.
Narrowed those residual descriptions without changing Partial statuses.
Also removed stale report-level unknowns for the already-proved default lap
source and local notification ordering/installed occupied-string termination.
Executable and sound-driver hashes still match the established baseline;
git diff --check passed. No runtime test or binary change occurred.


Rendering/history reconciliation: Luna found no status contradiction in
x87, arena/sort, camera/CCM, weather, ghost or replay RLE rows. Restored
explicit effect-pose count/time/blend/viewport questions, weather identity
and visible appearance, and cone wrap/catch-up/bounce/resource questions to
the ledger so broader wording does not obscure the preserved historical
scope. These remain unresolved for Astra; no closure was added.

### Backlog status-review completion boundary

Reviewed all36 remaining Partial rows and the Open historical-scope umbrella
using parent report/Ghidra checks and three Luna domain audits. Callback-list
ownership was checked directly against callback-list-lifecycle.md: direct
lifecycle/single-initialization capacity findings are established; indirect
mutation, predicate stability and teardown/reentry remain unresolved. The
[per-row dispositions](astra-backlog-review.json) retain each unresolved
investigation and evidence pointers. The status reconciliation is complete;
the unresolved research is explicitly not complete. Final ledger totals are
50 Closed,36 Partial,1 Open. No closure was inferred from a valid link alone.

### Session closing handoff

Commit `ee700d5` contains the saved Ghidra annotations, focused evidence
reports and backlog status reconciliation. The review ran as Sol6.1 with
Luna workers; it did not resolve the complex Astra investigations. Remaining
Astra work and runtime test planning stay in SCRATCHPAD.md, outside this
repository in the game installation. Do not duplicate that task list here.

Ghidra program `nfs3.exe` was saved successfully before the commit. No game
binary or asset changes were made during this review, and no new runtime
capture was started. Existing runtime reports describe earlier captured
scenarios; they must not be treated as fresh observations.
