# Series terminal menu contract

## Verified resource-to-handler binding

Installed `FEDATA/MENUS/postgame.mnu` lines251..261 declare `[button]`,
`codelink=racenow`, RaceAgain localization, no selection-list or nextmenu key.
Binary registry record00557aa8 contains ID5, name pointer00538368 (`button`),
and template pointer00556e40. Template+30 at00556e70 points to
`HandleFrontendButtonInput`00461270; +58 and+64 default to0.

Loader00449510 passes a parsed bracket-command ID as EDX and the new slot
index as EAX to00449060 at004496f1. That helper copies0xbc template bytes
into00604ee0+slot*0xbc. This closes the default button type/handler binding
gap. It does not exclude later callback mutation or establish all selection
lifecycle invariants.

## Separate input gates

Named-key helper0044a24c is now `FindEnabledFrontendNamedKeyAction`.
EAX=menu, EDX=relative-index output, stack=token, RET4. It finds the first
matching type5 token entry with disabled bit0 clear and returns the entry
pointer; decompiler's void prototype omits that result. It continues scanning
to the sentinel after finding a match. No local table bound exists.

The direct selected-entry dispatcher0044a35d invokes callback+30 without a
local disabled-flag test. The simple Enter path0046128c likewise has no
entry+4 test: if action+64 is zero, `racenow` offline returns6; online uses
readiness/pending-start logic. Nonzero action+64 is invoked instead.
Therefore neither layer supplies a second disabled guard for stale selected
entries. This is a static conditional statement, not a demonstrated bypass.

Postgame initializer0044f2dc calls004cf090 and sets racenow bit0 on rejection.
Mode1's terminal condition compares current track with sequence entry0055d020,
not progression index006fd40c. Other record/network gates also apply. Menu
initialization sets selected/prior indices to sentinel100 before the postgame
callback; navigation/hover and modal exceptions remain decisive.

## Remaining evidence

Capture or fully prove final-round initial selection, disabled flags, modal
state, keyboard/mouse selection reconciliation, and actual next-race action.
Normal hover and named-key rejection must not be generalized to all paths.
Series-index/table bounds and mode2 continuation remain part of the broader
backlog. No game mutation or terminal-series runtime test was performed.


## Forward selection and modal routing

Renamed0044a0c0 to `SelectNextEligibleFrontendEntry` after full assembly review.
Fresh descriptor initialization sets current/prior selection to100 before
menu-specific disable flags. The first menu-loop initialization calls this
helper. With sentinel100 and no eligible previous selection, it scans to the
type0 terminator and picks the first effective flags without mask1301,
including disabled bit0. If none qualify, selection remains100. Thus ordinary
fresh initialization does not itself select a disabled racenow entry.

For a nonsentinel selection, the helper increments and wraps at the terminator
until a qualifying entry appears. There is no full-cycle exit; termination
requires at least one eligible entry under stable flags/policy. This is a
conditional invariant, not a demonstrated all-disabled menu hang. Before
any validation it returns unchanged if the current entry has flag0400.
The button template has0800, so template flags alone do not create that case.

Hover retention0044a6b0 can preserve current selection while a dialog is
active, but main loop0044b230 checks dialog state again before dispatch and
routes active-dialog input to00445e60 instead of0044a2d0. Therefore retained
selection during a dialog does not alone establish a disabled-entry bypass.
Flag mutations, dialog closure and0400 lifetime need further tracing. The
00559250 retention latch still has only a direct zero writer in the bounded
xref inventory; no nonzero reachable state is established.


## Button initialization and retention-flag producer audit

Recovered the previously undefined template callback00461900..00461a66 as
`InitializeFrontendButtonStyleAndShapes`. The type5 template+24 points here.
Full executable disassembly was checked before creating its Ghidra function.
It resolves style+44 into WORD+48, loads up to three shape handles, assigns
style-dependent coordinates, and handles `hostonly` tokens. The token branch
requires a nonnull entry+10, nonzero network marker `007a22e0`, and zero WORD
`007a22da`; an exact token match sets bit0 in the entry flags at+4. The
type5 named-key lookup treats bit0 as disabled, so this is an input-availability
gate, not proof that the control is hidden. `ServiceHostNetworkAdmissions`
(`0049eae0`) enters host admission only in network state3 with
`007a22da != 0`; zero dispatches to client service `004a69c0`. This confirms
the flag's host/client role and polarity, and shows that `hostonly` disables
the control for clients in an active network session. Network settings
synchronization agrees: the nonzero mismatch path builds a type2 message from
local settings, while the zero path adopts changed received settings. The
callback does not directly set0400 or rewrite button
input/action callbacks. Style-coordinate assembly uses scale4; the
decompiler's inferred indexing is not authoritative.

A parsed-instruction search for OR byte[register+5],4 found five frontend
sites:00456d14,0045a1dc,0045be21,00461d84,0046354c. There was also an unrelated
stack-byte OR40 substring match. This is not an exhaustive flag-writer proof:
register masks, wider stores, copies and aliases remain possible.

At0045a120, the decompiled mouse-drag handler sets high-byte bit4 on entering
an interaction and clears it when mouse input releases, also changing cursor
bounds. This supports input-capture/selection-retention semantics, but the
template provenance of all five sites is resolved below; this does not
exclude all possible postgame paths. No dynamic0400 state has been observed on racenow.


## Retention writers bound to control templates

The five direct byte-OR sites now have registry/template provenance:

| Writer | Enclosing callback and template slot | Registered control |
| --- | --- | --- |
| 00456d14 | 00456ce0, pointer005577fc = template005577d0+2c | ID0x12 `carclrselect` |
| 0045a1dc | 0045a120 called at0045bcbc by0045bcb0; pointer00557954 = template00557928+2c | ID0x1f `HudItem` |
| 0045be21 | 0045bd20, pointer00557958 = template00557928+30 | ID0x1f `HudItem` |
| 00461d84 | 00461d00, pointer00556ed4 = template00556ea8+2c | ID0x11 `cascade` |
| 0046354c | 004634d0, pointer00556f38 = template00556f0c+2c | ID0x1d `droplist` |

Registry00557a84 uses 12-byte ID/name/template records. String pointers
00538370/00538378/005383ec/00538444 identify the controls above. Native
Ghidra xrefs agree with the executable's template pointer bytes. These are
not the type5 button's default callbacks.

The colour selector tests WORD entry+58 before setting/clearing0400.
Cascade and droplist test WORD+42 and WORD+40 respectively after finding
their selection lists. HUD mouse interaction owns drag/cursor bounds;
the HUD keyboard callback also sets0400 through register read-modify-write
at0045bd86..0045bd92 and0045be02..0045be0e. Thus the initial direct-OR search
was demonstrably incomplete even within a known callback. Do not treat the
five matches as an exhaustive alias-aware producer inventory.

This closes the provenance question for those five known sites only.
A global absence of button flag mutation, final-round menu behavior and the
series continuation contract remain unproved. No runtime action was needed
for this static refinement.


## Result-filter contribution to terminal eligibility

Full assembly of004cf000/004cef80, query wrapper00455dd0, filtered lookup
00455cd0 and predicate004557b0 resolves the two previously opaque queries:

- `CountHumanResultRecordsOutsideStateTwo`004cf000 passes category0,
  successive requested indices, sort key/direction0, filter0x28 and state2.
  Filter0x08 requires record+200 bit4 (human category); filter0x20 requires
  DWORD record+2c4 not equal2. Each lookup selects the kth **matching** record
  from the 16-slot map, not the kth unfiltered record. Under stable valid
  map/count invariants, the result is the matching count capped by the outer
  signed count00677d30. It is not a prefix of the original race ordering.
- `HasStateOneResultUnlessSuppressed`004cef80 asks for the first category0
  record with DWORD+2c4 equal1 (filter0x10); there is no human/AI restriction.
  Byte0055eb2e bit40 then forces false. The query still executes first.

The gate004cf090 starts eligible and only clears it. For mode1/2 it requires
nonzero004cf000 and zero004cef80 in addition to a nonterminal selected track.
Mode1 endpoint is DWORD0055d020, value7 in installed sequence0..7. Mode2
compares selected track to signed WORD006fd40a. Sessions greater than1 also
require nonzero network state007a22e0 and zero WORD abort007a22dc. Other race
modes skip the record and endpoint clauses. A zero endpoint result cannot be
re-enabled by either query.

This closes the exact filter and gate-composition question, not the gameplay
meaning of numeric states1/2, record validity under all loading paths, or
reachability of a next race after the terminal menu. Both query wrappers
restore map bytes but leave sort-selector globals changed. The record lookup
has inclusive mapped<=count checks and a16-slot scan, so the counting statement
must retain its valid/stable-state qualification.


## Result-state producers and snapshot provenance

Category0 copier00455210 copies0x9ac bytes from selected live vehicle objects
into006647b0, including category+200 and state+2c4. Pipeline00455410 binds
that buffer/count, then normalizes and applies mode-specific progression
before later query gates. Thus the result filters inspect copied vehicle
states, with additional snapshot-only normalization.

State2 has an explicit elimination producer:00455140 chooses the first
non-state2 record in its descending key1 map, requires count>1, clears
WORD006fd3de[metadataIndex], and sets that snapshot's state2. Mode2
normalization004552f0 also sets state2 on category-bit80 snapshots. This
supports an eliminated/ineligible interpretation on these paths; it is not
proof of every producer or category-bit80's complete meaning.

State1 has unfinished/termination producers. In004ce750, player entries
without category bit80 retain only state3/4; any other value becomes1.
Bit80 players instead receive the caller's state unconditionally and do not
clear the local all-terminal flag. AI entries skipping category bit10 get
lap estimates when not state3; states3/4 are then preserved, otherwise3 is
assigned if that flag stayed set, or the caller's state if it cleared.
An empty player list also leaves the flag set. Therefore the flag must not
be described as proving every player literally has state3/4.

Pause actions3/4/5 call004ce750 with1 at004c4d1b/004c4ccc/004c4d64;
completion calls it with3 at004ceb2a. Network menu resolver004c5720 also
writes player state1 in several exit-action/synchronization branches.
Together these explain why the unsuppressed state1 query can reject an
unfinished/terminated result and why excluding state2 requires a surviving
human result. Exact UI labels, all other producers and end-to-end final-round
behavior remain separate validation tasks. No runtime was required here.


## Mode2 generated endpoint and participant retention

Generator00473ac0 starts with nine allowed IDs0..8, excludes two distinct
IDs from0..3 when006fd470 is nonzero or4..7 when zero, then writes seven
remaining IDs in ascending order as WORDs006fd3fe..006fd40a. ID8 is never
excluded, so the seventh and final generated entry is always8. Existing
Ghidra evidence covers termination for stable seed/configuration and the
inspected random lookup bytes, including signed-index behavior.

Roster00473ee0 generates this list only when progressionWORD006fd3bc is0.
Its final track load is signed list[J], where J is that signed WORD.
Gate004cf090 reads signed WORD006fd40a through an unaligned DWORD/SAR16:
this is exactly list[6], not a separate literal endpoint or index bound.
Consequently, for a freshly generated, unchanged list and valid J0..6,
selected-track equality detects exactly the seventh race. It does not prove
J can never become7 or that restored/network state has this generated list.

Zero eligibility is handled differently for humans and AI. Human branches
call004736c0 to substitute configured model006fdc30, set row+1c=1, refresh
three model fields/default tuning and clear row+68; they still increment
human count and roster cursor. AI zero-eligibility branches call their
initializer but do not advance cursor/count, allowing the next profile to
overwrite that row. The later reduction decrements AI count and cursor by
max(0,J-excludedTally), without an AI-count lower bound. These are setup
operations; the runtime role of the substituted human requires further
tracing before calling it a spectator or excluded vehicle.

The generated-list/terminal-field binding is closed. Global index bounds,
loaded-state contracts, substituted-human runtime roles and final-round
continuation remain open.


## Substituted-human result exclusion chain

Registry discovery0043a429..0043a43a resolves a built-in16-byte identifier
with first DWORD0x21 and remaining bytes zero, then stores its **registry
index** at006fdc30. Identifier helper00439660 delegates the canonical form
check to00439620. This is not a fixed registry slot33. The discovery loop
has no assignment at this site when no such model is found; fallback/default
identity under a missing installation remains unproved.

Substitution004736c0 writes that index to config+14 and leaves config role+18
unchanged. RegisterRaceVehicle00428700 performs its ordinary category/list
insertion, then00428937..00428951 sets vehicle+200 bit80 if config+14 equals
006fdc30 and race mode is2. Thus a substituted human retains normal human
registration plus the exclusion marker; it is not removed at registration.

Three consumers connect that marker to results:

- Mode2 completion004ce840 counts bit80 players as exclusions, skips their
  completion checks, and requires a positive remaining eligible count.
- The finish-assignment block004ce48f..004ce4d9 skips its state3/time/progress
  assignments when bit80 is set. This is a local block contract, not proof
  that no other routine can assign state3.
- Mode2 result normalization004552f0 sets bit80 snapshots to state2; the
  human/non-state2 continuation query therefore excludes those snapshots.

This closes the substituted-human registration-to-result-exclusion chain.
Driving controls, camera behavior, model absence and all alternative writers
remain open; do not label the participant a spectator solely from bit80.


## Installed substitution asset

Read-only BIGF directory/extent parsing of the installed top-level car
archives identifies builtin ID0x21 in GAMEDATA/CARMODEL/KNOC/CAR.VIV,
member fedata.eng at offset297428, size301. Bytes+18..+27 are
21000000000000000000000000000000; text includes `Knockout`.
This grounds the special model identity without assuming its registry slot.
Default controller00431430 has no local category80 input-suppression check;
callback initialization0042c400 selects player controls by default, with AI
and network ownership overrides. Full driving/camera behavior remains open.

## Cursor positioning after selection

Named00449ea0 `SetFrontendCursorToSelectedEntry` after full assembly review.
Sentinel100 returns without cursor changes. Otherwise it indexes signed
start+selection at stride0xbc and positions X at x+trunc(3*width/4), Y at
y+trunc(height/2), then calls the cursor setter. It does not check disabled
flags or policy. Therefore the navigation helper's final cursor update adds
no eligibility guard to the previously documented selection flow. Global
selection validity and final-round invocation remain unresolved.

## Per-frame button rendering and availability

Recovered registered callback004607c0..00461267 as
`RenderFrontendButtonAndUpdateAvailability`. Type5 template+2c points here;
template+30 remains input callback00461270. The menu update pass invokes+2c
before hover/key processing, subject to its entry/priority conditions.

The racenow branch updates bit0 only with nonzero network session, host role
and the applicable rendering path. It clears bit0 when
(00662968==0 OR gate004cf090 succeeds) AND readiness0049ab60 succeeds;
otherwise sets it. In particular00662968==0 skips the mode gate, not readiness.
Nonhost rendering draws the readiness indicator. This is a network-host
availability producer, not proof of offline terminal-series revalidation.
Retained selection/modal state and other disabled-bit producers remain open.
Ghidra comment records the corrected branch conditions and broader render role.

## Reverse navigation and policy scope

Named00449f30 `SelectPreviousEligibleFrontendEntry` after full assembly
review. Sentinel100/no valid prior selects the last eligible record; ordinary
reverse navigation decrements and wraps0 to the final record. Like forward
navigation,0400 retains the entry before eligibility checks, and the wrapped
scan has no full-cycle stop. Stable all-ineligible lists therefore require an
upstream invariant; no reachable postgame example is established.

Policy004499b0 is network-only: offline session0 returns1 without token
checking. Its callers add rejection bit0 to temporary flags, not persistent
entry storage. Thus this policy cannot supply offline terminal-series
revalidation. Actual postgame initialization/flag lifetime remains open.

## Offline stored availability producer

Initializer0044efd0 looks up racenow using00539494 and calls gate004cf090
at0044f2dc. False stores bit0 into entry+4 at0044f2e5. This establishes an
offline-capable persistent disable producer, separate from the network-only
policy's temporary flags and render callback's host-only refresh. Selection
ordering/retention and eventual next-race behavior remain open; initializer
comment saved in Ghidra.

## Registry-to-runtime postgame binding

Parent assembly review of00442b10 closes the missing binding: named
`BindFrontendMenuCallbacksByName`. It scans24-byte rows00555c48, compares
row name against runtime descriptor+14, and copies five DWORDs row+4..+14
to descriptor+0..+10. Postgame row00556038 names00537d94='postgame'; its
00556044 pointer0044efd0 therefore becomes descriptor+8, not a guessed
registry/runtime structure alias. Loader00449510 assigns descriptor name
before calling the binder. Adjacent control1 starts00556050.

For that normal bound descriptor, initialization0044ab40 resets selections
100, restores templates, invokes0044efd0 (including offline racenow disable),
then initializes/layouts entries; RunFrontendMenuLoop's first selection pass
follows. This closes normal initial ordering. Later transitions, mutated
callbacks/flags and retained selection still require lifecycle evidence.

## Postgame frame helper boundary

Per-frame0044eda0's explicit body does not re-evaluate the offline terminal
gate or write descriptor selection/prior fields. Its racenow write only
re-disables after a network-session loss in session modes above1. Result-tab
state/flags are distinct controls. Helper004c9860 is now named
`ProcessBackgroundSoundTasks`: it dispatches the periodic
scheduler then004c9380, named `UpdateSoundBankSequenceAndCleanup` from its
voice-expiration, next-patch and bank cleanup logic. Neither explicit body
adds terminal selection validation, but scheduled callbacks remain indirect
state-changing edges. Saved Ghidra comments; no global non-reentry claim.

## Selection retention reachability boundary

Navigation00449f30/0044a0c0 retains the current entry when flag0400 is set.
Hover0044a6b0 also retains it during a dialog or latch00559250. The main loop
rechecks dialog state before input dispatch, so modal retention alone does
not establish an action path. Known0400 writers belong to car-color, HUD,
cascade and droplist controls; the racenow type5 template has0800, and its
postgame initializer only adds disabled bit0. No concrete racenow0400
producer or retained disabled-racenow invocation was found. Direct latch
references show a read and clear, without a nonzero writer; aliased writes
remain outside this bounded inventory.

Fresh initialization resets selection to100 and applies the postgame disable
before the first scan, whose1301 exclusion mask includes bit0. That ordinary
path therefore skips disabled racenow. Later mutation/indirect callbacks and
actual action reachability remain open; conditional retention code alone is
not evidence of a bypass.

## Offline action-to-race route

Type5 template00556e40 binds entry+30 to00461270. Enter0d and racenow token
matching at0046128c..004612a8 take the simple offline action6 return when
007a22e0==0 (004612b1..004612bf). This handler does not inspect disabled bit0
or call terminal gate004cf090. Frontend loop0044b230 returns the action via
004732b0; application004a3db0 dispatches states6/7 to RunRaceSession004a3690.
The inspected race-start and mode1/mode2 roster routes consume progression
without calling004cf090. This closes the explicit action-route trace, not a
terminal bypass: no concrete disabled-racenow dispatch was established, and
race setup can fail for separate reasons. The observed terminal policy is
frontend availability/selection enforcement.
