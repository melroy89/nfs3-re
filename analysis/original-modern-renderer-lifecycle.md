# Original versus Modern: renderer callback and video-mode lifecycle

## Evidence boundary

Static analysis of the supplied original/backup and official Modern v1.6.1. Exact executable hashes and provenance limitations are in the [loader report](original-modern-renderer-loading.md). The [selection/lifecycle manifest](evidence/audits/original-modern-renderer-selection.json) retains hash-pinned spans and asserts a shared tail is byte-identical. Reproduce with `python3 analysis/scripts/audit_renderer_selection_difference.py`. No game, driver or instruction probe was executed; no executable/database changed.

## Original indirection versus Modern direct entry

Original selector branches call `004f8830` and `004f8930` after loading, as mapped in the [initialization report](original-modern-renderer-initialization.md). `004f8830` tests about-export slot `009ef980`. When present, it installs five internal callbacks at `00567dc4`, `00567dcc`, `00567dd0`, `00567dd4` and **`00567dc8`**, the last pointing to **`00517610`** (`004f8844..004f887a`). A missing about export calls diagnostic helper `00401010` at `004f88a9`. If that call returns, the jump at `004f88b2` rejoins callback installation at `004f8844`.

`004f8930` first calls `004df740` with EAX=0 and allocates the backing pool through `004f92d0` if `005644fc` is null. When `00564364` is zero, it applies environment settings and calls `005089d0` with values from `00564384/88/8c`. That dispatcher loads callback slot `00567dc8` and, if nonzero, calls through it (`005089d8..00508a15`). Thus **original `00517610`**, not same-address `00517620`, is the relevant video-initialization counterpart.

Modern initializer instead calls **`00517620` directly at `004b5aa3`** and tests its return. This establishes removal of that particular indirection from the inspected startup path; it does not prove every old callback slot is unused throughout Modern.

## Parameters and mode selection change

Original `00517610` takes width in EAX, height in EDX and depth in EBX, copies width/height into ECX/ESI, checks the backing pool, and normalizes defaults. Width/height zero become 640/480; either -1 becomes 1024/768 respectively. Depth zero, -1 or 15 becomes 16. Those behaviors follow explicit branches, not a guessed C prototype.

It calls `005247c0` with the selected values, initializes the platform path if needed, and chooses hard-coded video-mode IDs through width/height comparisons before `_THRASH_setvideomode@12` at `005176a4`. The full ID-to-resolution table is not inferred here.

Modern `00517620` no longer reads those three input registers as requested dimensions. After its platform setup, it:

1. Calls `_THRASH_selectdisplay@4` (`009ef944`) with `[007a3a70]` at `00517665`.
2. Calls about-refresh helper `004f853c`, which stores a newly returned descriptor at `007a3a5c`.
3. Pushes `[0056438c]`, `[00564388]`, `[00564384]` and calls mode lookup `004bedcc`, storing its result at `0055fec0`.
4. Calls `_THRASH_setvideomode@12` (`009ef958`) with that mode result and literal arguments 2 and 1, then tests EAX at `0051769c`. Zero returns through the failure epilogue **before** the common tail.

The export identities are verified by the retained 34-name binding map. Original falls through after its corresponding setvideomode call without testing EAX there. Modern's mode lookup replaces the original local hard-coded selection branches, but mode enumeration/provider behavior and complete failure recovery remain outside this chapter.

## A retained tail with different entry conditions

Bytes **`005176aa..0051776b`** are exactly identical in the two executables; the manifest asserts this, rather than relying on visual similarity. This tail conditionally releases four stored objects through `00509b10`, clears their slots, handles `005643e0`, sets `00564364` to 1, calls `005179d0` for one or two records, then writes current width/height from `00565030/34`.

The common bytes do not imply identical lifecycle behavior: Modern can skip them on a failed setvideomode return, and its preceding display/mode selection differs. At the end, original calls imported ADVAPI32.RegFlushKey at `00534468` after pushing `0x80000000`; Modern instead calls `004beeb0` with `[0055fec0]`. The import identifies the original API, but its intended role/error handling and the complete effects of Modern’s descriptor-based mode helper remain unresolved here. Both success paths return EAX=1.

## Original hard-coded environment setup

Before its callback dispatch, original `004f8930` invokes environment helper `004f8b50` with:

| Names | Value | Replacement flag |
|---|---|---:|
| `SST_VIDEO_24BPP`, `FX_GLIDE_SHAMELESS_PLUG` | Empty string | 0 |
| `FX_GLIDE_NO_SPLASH`, `SST_DUALHEAD`, `SSTV2_DUALHEAD` | `1` | 1 |
| `SST_RGAMMA`, `SST_GGAMMA`, `SST_BGAMMA`, `SST_GAMMA` and four `SSTV2_` gamma names | `1.0` | 1 |

These values are read from the original PE and their call operands. Empty strings have special handling in the helper; do not equate the first row with unconditionally replacing an existing value. The earlier Voodoo selector also performs environment writes, documented separately; order matters.

Modern's smaller initializer does not contain this block. It instead has the configuration-driven `ENV` section path traced in the loader chapter. This supports a local hard-coded-to-configurable mechanism change, not proof that all environment manipulation disappeared or that each driver's shipped INI reproduces every original value.

## Further evidence required

The [mode-selection comparison](original-modern-mode-selection.md) now traces the original ID decision tree, Modern search rules and final record publication. Pending: complete resize/helper semantics, callback/storage users outside startup, platform helpers and actual driver acceptance/failure behavior. The original `004f8930` post-initialization path and Modern `004f8548` share several calls but differ in timer/input/callback setup; their full equivalence is not claimed. Historical release attribution and runtime compatibility remain separate questions.

## Final Glide init failure now connected to platform callers

The [paired driver follow-up](original-modern-glide-reference-identity.md#thrash-init-retries-provider-setup-and-has-a-separate-failure-channel) connects the final Glide init export to EXE slot009ef978 at0052473a. Its admitted path retries internal provider setup independently of the about cache; provider failure returns0. The EXE branches to cleanup, whose wrapper then returns current platform byte0056aff0. If that returns0,00517620 skips later display/mode work and startup reaches its existing init diagnostic. This is conditional static propagation, not observed recovery/termination or proof that every cleanup callback preserves zero.

## Gameplay exit skips frontend mode setup from150

**Verified shutdown admission change and selected action/state chain; OS display result untested.** The [exit-mode audit](evidence/audits/gameplay-exit-mode-history.json), reproduced with `python3 analysis/scripts/audit_gameplay_exit_mode_history.py`, pins original, author-hosted1.4.0/1.5.0 and official final EXEs. It captures complete shutdown bodies and retained route spans.

| Stage | Original/1.4.0 |1.5.0 |Final |
|---|---|---|---|
|Shutdown entry`004a35d0` |Always enters setup, saves incoming EAX in ESI |PUSHAD; TEST EAX,EAX; JE`004a365b` |Same zero-input gate, JE`004a3657` |
|Zero input |Performs frontend mode/viewport setup; skips later conditional`00495600` call |Skips setup and`00495600`, reaches cleanup |Same admission policy with changed cleanup |
|Nonzero input |Performs setup and conditional call |Performs setup and now-unconditional-on-that-path call |Same admission policy; mode/FOV/cleanup details differ |

Historical1.4.0/1.5.0 setup bytes`004a35d9..004a3652` are identical. The block loads configured frontend mode index`0055fec8` and calls original-role mode application`004bef50`; final uses`004beeb0`, as the [existing mode report](original-modern-mode-selection.md) qualifies. At`004a361d/004a3622`, retained instructions load ECX480 and EBX640 before calling viewport helper`004352d0`. Thus the skipped work contains both a frontend mode-application request and explicit640×480 viewport arguments. **The constants are not proof that the requested OS mode is always640×480:** mode application uses the configured index and driver descriptor, can fail, and has changed internals. Final also uses a different FOV argument representation and cleanup sequence; this is not whole-shutdown equivalence.

### Checked exit state reaches the zero-input branch

The audit retains the following chain, identical in all four builds within its explicit spans:

1. The confirmation callback`0044b0f0..0044b164` can publish byte`00559251=1` and return action10 for its accepted branch. Other selection/cancel paths remain distinct.
2. The in-race action mapping at`0044bcf6..0044bd3b` converts action10 to return5. The caller at`004c4c07` invokes in-race menu processing, then mediates the result through`004c5720`; **network mediation can change the result**, so the next step is conditional on accepted action5.
3. The accepted action5 arm`004c4d35..004c4d6f` performs cleanup, explicitly sets ECX1 and ultimately stores ECX into terminal state`007d36b4`. Its intervening finalizer`004ce750..004ce7ff` saves/restores ECX and is byte-identical in all four builds, supporting that published1 rather than assuming a register survives a call.
4. At`004a3829..004a3840`, the retained postrace caller maps terminal state1 to EAX0, other states to EAX1, then calls shutdown`004a35d0`.

The new zero-input gate therefore suppresses the inspected frontend mode/viewport transition on this accepted terminal-state1 route while retaining cleanup. The original's zero input only controlled the later conditional call, after setup had already happened. The complete captured shutdown envelopes end at`004a3684` (original/140), `004a3680` (150) and`004a3681` (final); the raw body identities and disassembly are retained separately.

**MP150-035 advances to partial static support:** the advertised140→150 boundary contains a concrete mechanism for avoiding the unnecessary frontend display transition on the checked gameplay-exit route. Actual desktop resolution, all exit paths, provider behaviour, callback admission, mediator outcomes and transitive cleanup remain unverified. Retained local code does not establish complete network or lifecycle equivalence. Reconstruction must preserve the conditional setup/cleanup split and register contract, rather than removing shutdown wholesale. No game, mode API, driver, new instruction probe, compiler or Ghidra write was used.

## The startup mode-result gate appears in 1.6.1

The supplied original, 1.1.0 and 1.2.0 share all 637 bytes of the callback at `00517610..0051788c` (span SHA-256 `3d0032952d268d72bea311fb9bb58aa4eb08faecf82ccd58e0e96a74b889ba8d`). If the driver's mode call returns normally with EAX zero at `005176a4`, execution still enters the common tail. That tail overwrites EAX with 1 at `00517721` and publishes it to `00564364` at `0051772d`. If the rest of initialization returns without clearing that state, the six earlier failure gates pass, including the gates with the new dialog in 1.2.0. The dialog addition and the later check for rejected startup modes are distinct changes. See the [six failure paths](original-modern-renderer-loading.md#renderer-initialization-failure-dialog-introduced-in-120).

In the retained 1.1.0–1.4.0 executables, startup's driver mode
request through `009ef958` is at `005176a4`. It falls directly into
the common tail at `005176aa`. In 1.5.0–1.6.0 the request moves to
`005176a1` and the unconditional jump at `005176a7` reaches the
same tail. Neither route branches on the driver's returned EAX.

The final 1.6.1 request at `00517696` adds a test at `0051769c`
and a zero branch to `0051777e`, which restores registers and
returns with EAX still zero. This skips the surface cleanup and
remaining success-path initialization described above. The requested
index has already been stored at `00517687`. This startup check is
a separate change from the failure check in the runtime mode
application, which the supplied original already has.

Reproduce by disassembling `00517620..00517900` with
`objdump -d -Mintel` on the retained historical executables and
official final package. For 1.4.0, extract the archive member
`nfs3.exe` with `7z x -so`. These instructions date the inspected
startup gate to the 1.6.0 → 1.6.1 package boundary. They leave
driver return behavior and observed startup recovery unverified.

### A rejected startup mode reaches the fatal renderer diagnostic

The 1.6.1 zero return at `0051777e` reaches the test at
`004b5aa8`. The caller supplies **Cannot init the thrash driver.**
from `0053d1e3` to `004b570c` at `004b5ab1`. The helper displays
the message through MessageBoxA and calls `004f2a7d` regardless of the
dialog result. That thunk supplies exit status zero to the
[shared termination chain](original-modern-startup-requirements.md#shared-termination-chain-reaches-exitprocess).
Under ordinary cleanup returns, startup terminates before reaching the
renderer-specific setup at `004b5ab6`.

The same diagnostic also receives earlier renderer-initialization
failures, as shown in the [Glide comparison](original-modern-glide-reference-identity.md#thrash-init-retries-provider-setup-and-has-a-separate-failure-channel).
The message alone therefore cannot distinguish failed driver setup
from a rejected startup mode. This is a static caller trace. No
failure, dialog, or process exit was observed.

### The startup caller switches from a state check to a return-value check

The retained 1.6.0 executable calls wrapper `004f8a50` at
`004b5a2d`. The wrapper uses `00564364` to decide whether to call
the video initializer at `00517630` and whether to run its own
continuation. At `004b5a32`, the startup caller tests that same
global. If zero, it passes **Cannot init thrash video driver.**
from `0053d147` to fatal helper `004b56f8`. That helper calls
the message-box slot and the common termination thunk.

Final 1.6.1 calls `00517620` directly from startup and tests EAX,
as documented above. The change from 1.6.0 is therefore removal of a
direct wrapper and a switch from the state check to the initializer's
return value. The original retail route through the indirect callback
is a separate baseline. A fatal renderer diagnostic already existed
in 1.6.0, but the startup mode request did not branch on the driver's
return. The two checks should not be treated as equivalent. No live
failure path was exercised.

### The old startup state check could pass after a rejected mode

In both 1.6.0 and 1.6.1, the common tail sets EAX to 1 at
`00517721` and writes it to `00564364` at `0051772d`, before
calling the record setup at `00517732`. In 1.6.0, control reaches
this store from the driver mode call even if the driver returns
zero. In 1.6.1, that zero result branches around the store and
returns to the startup diagnostic check.

Consequently, if the 1.6.0 initialization tail and its wrapper
return normally with that state intact, the startup check at
`004b5a32` passes even though the driver rejected the mode.
The store marks progress through the initializer. It does not
record the driver's result. Other code also compares this state
against 7, for example at `00503cf1` in 1.6.0, so a reconstruction
should retain its DWORD representation. The full state lifecycle
and live effects of rejection remain unverified.

### A nonzero renderer state takes different startup paths

In 1.6.0, an already nonzero `00564364` causes the startup wrapper
at `004f8a50` to bypass `00517630` entirely. If another caller
entered `00517630` directly with that state, its own branch at
`00517640` would instead call the display and mode slots using
the stored index `0055fec0`, skipping the mode lookup.

In 1.6.1, startup calls `00517620` directly. A nonzero state
branches at `0051762b` to `0051765f`, skipping the platform
initialization block. It still selects the display, refreshes the
renderer descriptor, looks up a mode from the three requested
dimensions/depth globals, and submits that index to the driver.
The same mode-result gate applies on this route.

This establishes the behavior for a nonzero state at the tested
entries. Whether repeated startup is reachable in normal gameplay,
and which other callers can supply that state, remain unverified.

### Display selection moves ahead of mode lookup in 1.6.1

On the zero-state startup path, the 1.6.0 and 1.6.1 executables
perform these operations in different orders:

| 1.6.0 | 1.6.1 |
|---|---|
| `00517681`: look up the mode through `004bedcc`, which queries the renderer descriptor | `00517665`: call `_THRASH_selectdisplay@4` |
| `00517686`: store the index at `0055fec0` | `0051766b`: refresh the cached descriptor through `004f853c` |
| `00517691`: call `_THRASH_selectdisplay@4` | `00517682`: look up the mode through `004bedcc` using that descriptor |
| `005176a1`: apply the stored index | `00517687`: store the index, then apply it at `00517696` |

Both display-selection calls pass `[007a3a70]`. Neither uses the
display-selection return value as a local gate. The later mode
result check in 1.6.1 is separate. If a driver changes its mode list
when the selected display changes, 1.6.0 can carry an index chosen
from the earlier list into the later display. Version 1.6.1 queries
in the opposite order. The [DX7 comparison](original-modern-dx7-mode-admission.md#display-selection-can-rebuild-the-dx7-mode-table)
verifies the table rebuild on a qualifying path in both releases.
Whether the rebuilt records differ on a particular adapter remains open.

The final package's DX6, DX7 and DX8 display selectors also clarify
what an out-of-range adapter request means before mode lookup. The
retained DLL hashes match the members under `drivers/dx6`,
`drivers/dx7` and `drivers/dx8` in the official archive.

| Driver export | Out-of-range selection policy |
|---|---|
| DX6 `60001880` | The signed range checks branch to `600018c7`, which loads the first adapter entry and stores index zero. |
| DX7 `600020c0` | The signed range checks branch to `60002132`, which loads the first adapter entry and stores index zero. |
| DX8 `60003800` | The first-selection path initializes the selected index to zero at `6000384a` and only overwrites it for an in-range index. A separate early return at `60003809` preserves the earlier selection once its flag is set. |

These are local adapter-index decisions. They do not establish
adapter availability, a successful selection, or the driver's
mode description after setup. The executable uses the later
mode-setting result for its startup failure gate.

The display selector entry spans match byte for byte between the
retained 1.6.0 and 1.6.1 DLLs for DX6
(`60001880..6000194a`), DX7 (`600020c0..600021e7`) and DX8
(`60003800..600038a7`). The spans end just after the return
instructions. Equal export bodies leave room for changed behavior in
their callees, as the DX7 rebuild shows.

In both DX8 builds the selection flag at `6001ed6c` starts in the
zero-filled tail of PE `.data`, beyond the file-backed bytes. The
selector tests it at entry and sets it to 1 at `6000389f` on the
first-selection path. A linear disassembly search found only those
two direct references to the absolute address in either build.
The early return is therefore present in 1.6.0 already. Indirect
writers, resets through bulk writes, and behavior across DLL reloads
were outside this check.

### The adapter index input is retained across the reorder

Both executables place `007a3a70` in the uninitialized `.bss`
section, so its loader-supplied value starts at zero. The renderer
name parser in 1.6.0 checks for an `@` followed by an ASCII digit
at `004b580b..004b581b`, calls the decimal converter `004f0430`,
and stores its result at `004b5822`. Final retains those checks,
converter and destination at `004b5823..004b583f`. Neither checked
suffix branch clears the field when the checks fail. See the
[command-line analysis](original-modern-command-line.md#duplicate-driver-options-name-and-suffix-are-separate-state)
for how a previously parsed suffix can survive a later name change.

A linear disassembly search found one direct store and one direct
read of `007a3a70` in each executable. The readers are the two
startup display calls above. The evidence thus ties the observed
reorder to the same adapter-index input, with no additional bounds
check on that input in the checked EXE routes. The selected DLL
interprets the index. Indirect writes and live adapter selection
remain outside this check.

### Retail uses a different adapter field and a fixed follow-up mode

In the supplied original executable, `004b5ce4..004b5cf1` passes
`0055fdbc` to the renderer display-selection slot. Two direct
writers are visible. The successful registry query for
[`D3D Device`](original-modern-registry.md) stores its result at
`004b6487`. The argument path at `004a5198..004a51f8` matches
`-D3D`, scans the following text using `%d`, and writes the
parsed DWORD at `004a51f3` when the scan succeeds.

On the same original branch, the display-selection call follows
video initialization and is followed by a separate driver mode
request with stack arguments `(1, 2, 1)` at `004b5cf7`. The
branch then calls `004b5940` without testing that request's return.
Final instead selects the adapter from the renderer-name suffix,
refreshes its descriptor, and submits the looked-up mode index
with a result check. This comparison covers the original branch
containing the direct display-selection call.

The original's `007a3a70` is a separate state cell. Its reads
at `004bc689` and `004bc7e8` gate x87 initialization sequences
and do not supply the adapter argument. Address-based annotations
must preserve the two versions' different meanings. No setup or
mode switch was executed.

### Early startup checks driver initialization separately from mode setting

The supplied original, 1.1.0 and 1.2.0 have identical code at `005246a0..005247b7` (span SHA-256 `2a6be886204a3c85bb6911453661da1f1950d6bbae1c3d9d0499077700f10025`). The platform initializer calls the driver's `_THRASH_init` slot at `0052473a` and tests EAX at `00524740`. Zero leads to cleanup at `0052479a`, followed by a zero-extended load of the post-cleanup byte `0056aff0` as the helper's return value.

On the zero-renderer-state entry path, the early mode callback tests that helper result at `00517675`. Zero branches to the epilogue at `00517782`, skipping both the mode request and the store of state 1. If the shared renderer state is still zero when control returns to the outer gate, 1.2.0 reaches the new dialog. Thus the early path already checks initialization failure, with propagation dependent on cleanup and shared state. The later 1.6.1 branch adds the distinct check on the result of the mode request itself. This comparison establishes static control flow; it does not establish which driver or cleanup outcomes occur on any particular machine.

The cleanup helper at `004cdaa0..004cdb0e` is byte-identical in the original, 1.1.0, 1.2.0 and installed 1.6.1 (span SHA-256 `fbb330d3c7a1fd17059ba0bcf2fb6da8c86f10dbc162c92165da6ce73e2c947c`). If window-session flag `009f3d24` is zero on entry, `004cdaae` jumps straight to the epilogue and leaves `0056aff0` untouched. If the window-session flag is nonzero, the helper sends the cleanup request at `004cdaeb` and polls that flag at `004cdaf0` while servicing calls at `004cdafb` and `004cdb02`. It contains no direct store to `0056aff0`. In the early initializer, `005246c9` ensures the platform byte is zero before taking the driver-init path. On the no-window cleanup path, the reload therefore returns zero provided the intervening calls left that byte untouched. The active-window branch requires separate tracing of its callees and callbacks to establish the resulting byte.

The active-window request `0x0466` uses the same pending-latch mechanism in the four inspected EXEs. In the original, 1.1.0 and 1.2.0, registration at `004cd849` installs `004cce60`, which sets DWORD `00561270` at `004cce69` when its first argument is nonzero. In installed 1.6.1 the corresponding registration, handler and store are `004cd8e7`, `004ccd98` and `004ccda1`. The inspected dispatch supplies the context pointer `009f38d0` as that argument, so a zero wParam still sets the latch. The window thread consumes the latch, optionally calls `004ecd50`, calls DestroyWindow at `004cd646`, then clears the shared HWND `009f3d24` at `004cd64f` in each build. That store explains how the cleanup wait can end. The consumer contains no direct store to platform status `0056aff0`. Effects through the optional callee or window callbacks, and runtime progress of the wait, remain unverified. See the [callback argument and pending latch evidence](detailed-analysis-notes.md#request-0x466-pending-latch-and-deferred-destruction).

### The 1.4.0 startup check uses the older initializer target

In retained 1.4.0, startup calls `004f8a50` at `004b5c35` and
tests `00564364` at `004b5c3a`. Zero calls the diagnostic with
the “Cannot init thrash video driver.” string. The wrapper tests the
same cell at `004f8a59` and `004f8a78`, just as in 1.6.0, but
its call at `004f8a73` targets `005089d0` in 1.4.0 and
`00517630` in 1.6.0.

The older target has multiple paths, including a call to
`00508390` at `00508a72`. A zero return from that call reaches the
store from EDI to `00564364` at `00508a7b`. An alternate branch
publishes EDX at `00508b12`. These witnesses separate the historical
initializer from the later common-tail store of 1. The shared caller
check alone does not establish identical failure coverage across
the two versions.

The wrapper's call at `004f8a73` changes from `005089d0` in
1.4.0 to `00517630` in 1.5.0. All five retained releases from
1.5.0 through 1.6.0 keep the latter target. The target can be
reproduced by adding the signed dword at PE RVA `f8a74` to
`004f8a78` after confirming the E8 opcode.
Earlier builds have a different call at the same address and
are outside this wrapper comparison. Final 1.6.1 instead calls
its revised initializer directly from startup. This dates the call
routing independently of whether the driver accepts a requested mode.

The startup-mode instructions from `00517630..0051776b` match in
1.5.0 through 1.5.3. They differ from 1.6.0 in only three bytes,
at `0051768d..0051768f`, which change the absolute device selector
source from `0055fdbc` to `007a3a70`. In all five releases, the
mode call through `009ef958` at `005176a1` is followed by an
unconditional jump to `005176aa`. The common tail publishes
`00564364=1` at `0051772d`. Thus the inspected startup route
can publish success state after a zero mode return starting
in 1.5.0, subject to the shared tail returning normally.
This byte comparison covers the named span, not earlier
initialization failures or live driver behavior.

The matching writer moves in the same 1.5.3→1.6.0 transition.
At `004b581b..004b5828`, both parsers pass ESI to the decimal parser
`004f0430` and store EAX at `004b5822`. The store's destination
changes from `0055fdbc` to `007a3a70`, matching the changed
startup read at `0051768b` before invocation of
`_THRASH_selectdisplay@4`. This verifies the paired writer and
reader relocation for a parsed device suffix. Earlier uses of
`007a3a70` include literal stores from renderer setup, so the
numeric device meaning cannot be carried backward by address.
Other callers and actual device selection remain unverified.

The address move preserves the initial zero by a different PE
mechanism. In 1.5.3 the device DWORD at `0055fdbc` is file-backed
`.data` with four zero bytes. In 1.6.0 and 1.6.1 its counterpart
`007a3a70` falls inside the declared `.bss` extent with a zero
raw-data pointer. A decoded direct-operand sweep finds the suffix
parser as the only direct `MOV` writer to the device DWORD in
1.5.3 and 1.6.0. With ordinary initial state and no intervening
writer, a name without a device suffix therefore leaves index
zero for initial selection. A later name without a suffix can
retain a previously parsed value. Indirect writes and live
device selection remain outside this comparison.

### The EXE moves the display-selection call in three releases

A direct-operand scan of the hosted original and all 12 retained
Modern `nfs3.exe` members finds one indirect call explicitly naming
`009ef944` in each. The call and argument bytes read from each PE
agree with the following sequence.

| Build | Argument setup | Call | Device DWORD |
|---|---|---|---|
| Hosted original and 1.0.0–1.3.1 | `004b5ce4`, load EDX then push | `004b5ceb` | `0055fdbc` |
| 1.4.0 | `004b5c4d`, push from memory | `004b5c53` | `0055fdbc` |
| 1.5.0–1.5.3 | `0051768b`, push from memory | `00517691` | `0055fdbc` |
| 1.6.0 | `0051768b`, push from memory | `00517691` | `007a3a70` |
| 1.6.1 | `0051765f`, push from memory | `00517665` | `007a3a70` |

The 1.4.0 change also replaces the immediate fixed mode request
seen after the 1.0.0 and 1.3.1 calls. At `004b5c59` it instead
scans for the lowest set bit in `007a3a58`, compares the resulting
index to 6 and branches or dispatches through the table at
`004b5be0`. The mask selects a renderer-type setup branch. The table and local
setup calls are decoded below.

For reproduction, linearly decode each retained EXE with
`objdump -d -Mintel` and search for calls naming `0x9ef944`.
Use the PE image base to read the argument setup through the
six-byte call ending in `ff 15 44 f9 9e 00`. Calls via a copied
pointer are outside this census. The corresponding [DX5 driver
selection code](original-modern-dx5-reference-pair.md#out-of-range-display-indices-fall-back-to-slot-zero)
retains its slot-zero fallback across these releases.

#### Version 1.4.0 renderer-type setup after display selection

In the retained 1.4.0 EXE (SHA-256
`7cfecaac5e78dcbd8de059ea4e25bee1922c37df867e4d794c9b05960984d80d`),
the parser at `004b5abe..004b5ae5` writes `007a3a58` from
the first byte of the normalized type string. Its outputs are
`0x40` for d, `0x10` for v, `0x02` for s and `0x01` otherwise.
Read seven little-endian DWORDs at `004b5be0` to recover the
dispatch destinations. State pairs below are selector and value
for slot `009ef96c`, in call order. The vertical bar marks the
intervening call through slot `009ef970`.

| Lowest bit | Target | Local setup |
|---|---|---|
| 0, 5 | `004b5d53` | Common return |
| 1, 2 | `004b5c70` | `(10,2), (3,0) \| (4,0), (6,0), (2,0)`, then calls `00431c50` |
| 3, 4 | `004b5d11` | Sets `007a3a68`, `007a3a60` and `007a3a70` to 1, then `(10,2) \| (4,1), (2,0)` |
| 6 | `004b5cb2` | Sets `007a3a68` and `007a3a60` to 1, requests mode arguments `(1,2,1)` at `004b5ccc`, calls `004b5940`, then `(10,2), (104,0) \| (4,1), (6,1), (2,0)` |

The fixed request survives in the d-type branch, after its flag
stores. The v-type store at `004b5d25` is a separate use of
`007a3a70` in 1.4.0. The display-selection call in this build
already received its adapter index from `0055fdbc`. The
normal type parser supplies nonzero masks, while BSF itself
leaves the destination undefined for a zero input. Runtime
renderer results and callee effects remain unverified.

#### Version 1.5.0 moves the D3D mode request and inlines the result loop

In retained 1.5.0 (EXE SHA-256
`d9db8ead63a9697c4c6c3933e720cd93565f67bd4b264e8bbc0d98d03c236dae`),
the type dispatch at `004b5a16` uses the seven DWORDs at
`004b59a0`. Bits 0/5 return at `004b5b29`, bits 1/2 run the
software path at `004b5a2d`, bits 3/4 run the Voodoo-like
path at `004b5ae7`, and bit 6 runs the D3D-like path at
`004b5a6f`. The software and Voodoo-like paths retain the
1.4.0 local state-call sequences and stores listed above.

The D3D-like path retains its two flag stores and subsequent
state-call sequence. It drops the local fixed mode request
and inlines the former `004b5940` loop over five selector/value pairs
at `0055fd94`: `(13,1), (13,0), (4,2), (206,1), (104,1)`.
At `004b5a97` it tests each state call's return and sets the
corresponding bit in EDI when EAX is nonzero. It stores the
resulting five-bit mask to `007a3a5c` at `004b5aa7`. Each bit
tracks the result of the call at that row index, including the
two distinct calls using selector 13. The table bytes match in
every retained release from 1.5.0 through 1.6.0. The mode
request itself is in the startup initializer through slot
`009ef958` at `005176a1`, as described above. These are static
call-site and data observations. The meaning of each return
and the live driver's response remain unverified.

The five calls and result mask already existed in the hosted
original. The complete helper at `004b5940..004b5994` (end
exclusive) matches the hosted original and all six retained
Modern EXEs from 1.0.0 through 1.4.0. Its SHA-256 is
`693dc34afe8a23442ef6cd9e09a33a3ef1796f3d04b7111de5de1fef31c3c9a4`.
It clears `007a3a5c`, then reads and updates it after each
call. The 1.5.0 loop accumulates in EDI and publishes once
after the fifth call. The source table at `0055fd94` matches
the hosted original and all retained Modern releases through
1.6.0.

A linear disassembly scan for explicit operands naming
`007a3a5c` finds only the mask store in 1.5.0 through 1.6.0,
at `004b5aa7`, `004b5acb`, `004b5adb`, `004b5adb` and
`004b5ad6` respectively. The hosted original and 1.0.0–1.4.0 have exactly
three decoded direct operands naming the cell, all within the
result helper: the clear at `004b594c`, accumulator read at
`004b597a`, and update at `004b5985`. The only decoded direct
call to the helper is at `004b5cfd` through 1.3.1 (including
the hosted original), and at `004b5cd2` in 1.4.0. No outside
reader was found by this scan. In 1.6.1 the same address instead
holds the [cached renderer descriptor pointer](original-modern-renderer-loading.md),
with direct stores at `004f84f5` and `004f8542`. The scan
cannot exclude reads through a computed address in the earlier builds.

#### Version 1.6.1 preserves the calls and drops the result mask

The final EXE's loop at `004b5b23..004b5b3e` (end exclusive)
calls the same state slot with all five pairs in the same
order. After the indirect call at `004b5b2f`, it advances the
table pointer and increments the loop counter without testing
EAX. The loop falls directly into the `(10,2)` setup call
sequence. Thus the 1.6.0-to-1.6.1 change removes result
accumulation and publication while preserving the five
requests. This explains how the descriptor can occupy the
former mask cell without a subsequent overwrite by this loop.

The 40 table bytes at PE RVA `15fd94h` match between the
retained 1.6.0 and 1.6.1 EXEs (SHA-256
`4340dc71acc29777ad540683833970e4878e6c84924132277ed777efb57da604`).
The final loop's 27 bytes have SHA-256
`fccba56e4bffed1a967aed3fd1e79c56c473ce5526b52ca9bdec5e3ba230c026`.
This comparison establishes argument and local control-flow
continuity. Driver effects remain dependent on the bound implementation.

#### Eight final EXE sites read the cached descriptor

The direct-operand scan finds eight descriptor reads in 1.6.1.
Seven replace a call through the about slot `009ef980` at the
corresponding site in 1.6.0. Texture-limit setup is the eighth
and uses a reorganized code window, as detailed in the
[texture-limit comparison](original-modern-texture-limits.md).

| 1.6.1 load | Corresponding 1.6.0 about call |
|---|---|
| `00488a8f` | `00488a8e` |
| `0049c5c6` | `0049c5c5` |
| `004b5bd6` | Reorganized texture-limit path |
| `004be582` | `004be581` |
| `004bed99` | `004bed99` |
| `004beddd` | `004beddd` |
| `004beec0` | `004beec0` |
| `004d37bf` | `004d37be` |

In the mode-dimension helper `004be570..004be5d1` (end
exclusive), only five bytes differ between the builds. The
six-byte about call at `004be581` becomes a NOP plus the
cached pointer load. The helper still compares the signed
input index against descriptor field `+0x3c`. It uses the
table at `+0x40` with 40-byte records to copy width and height,
or writes 640×480 when the index is greater than the field.
The comparison and fallback bytes are unchanged, including the
acceptance of equality in this local check. This is a
static comparison of direct references and does not establish
descriptor validity at runtime.

The full 97-byte mode-dimension helper matches the supplied original
in every retained Modern release from 1.0.0 through 1.6.0. Its SHA-256
is `bc69b769d28aa42f63bf08443a979053e8ce53ee43f564a81d45c9e152a3e129`.
Official 1.6.1 has span SHA-256
`6984e838709db38ff94856c46ada2bdb869b1e8ce7020c24bbfe7a08d5cce02b`.
Extract each archive's root EXE and hash 97 file-backed bytes at
PE RVA `be570h`. This dates the cached descriptor read to 1.6.1
for a helper shared by the old and new viewport initializers.
The matching earlier code does not establish identical descriptors
from different renderer DLLs.

#### Release history of the seven direct call replacements

Reading the six bytes at each old call address in the table above
establishes when that exact site used the indirect about call
(`ff 15 80 f9 9e 00`):

| Old call addresses | Retained builds with the call at those addresses |
|---|---|
| `00488a8e`, `0049c5c5`, `004be581`, `004d37be` | Hosted original and Modern 1.0.0–1.6.0 |
| `004bed99`, `004beddd` | Modern 1.5.0–1.6.0 |
| `004beec0` | Modern 1.5.2–1.6.0 |

At `004beec0`, 1.5.0 and 1.5.1 instead contain six NOPs.
All seven sites use the cached load in official 1.6.1. At the
first four sites the new load follows a NOP. At the last three
the load starts at the old call address. To reproduce, extract
the root EXE from each retained archive and inspect six
file-backed bytes at each listed VA. Earlier different bytes
establish only that the exact site did not contain the call.
The reorganized texture-limit path remains a separate comparison.
