# Original versus Modern: window initialization and callbacks

## Scope and repeatable evidence

**Verified static differences; no window/game execution.** Baselines are the supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [provenance](original-modern-differences.md).

Run `python3 analysis/scripts/audit_window_initialization_difference.py` from the repository root (Python `pefile`, GNU `objdump`). The [curated evidence](evidence/audits/original-modern-window-initialization.json) retains instruction-span hashes, original/Modern registration lists, removed/added message IDs and changed callback addresses. Raw assembly remains under ignored `analysis/captures/modern-differences/window/`. The script checks both input hashes; it extracts immediate message/handler pushes to `004cc6d0`, allowing intervening non-stack setup instructions. This covers this initializer, not every registration made by other subsystems.

## 1. Registration changes at the matched initializer

Both executables enter the initializer at `004cd6c0`; common setup and thread-launch/continuation neighborhoods establish a stronger correspondence than address equality alone. The direct registration calls change from **26 original to 27 Modern**:

| Message | Original callback | Modern callback | Observed change |
|---|---|---|---|
| `0001` WM_CREATE | No registration here | `004cccc4` | Added |
| `0002` WM_DESTROY | `004cce80` | `004ccce4` | Replaced no-op callback with state/hook teardown |
| `0007` WM_SETFOCUS | `004ccd60` | No registration here | Removed |
| `0008` WM_KILLFOCUS | `004ccdd0` | No registration here | Removed |
| `001c` WM_ACTIVATEAPP | No registration here | `004ccd04` | Added active-state transition callback |
| `0010` WM_CLOSE | `004cce40` | `004ccd5c` | Moved equivalent PostQuitMessage behavior |
| `0218` WM_POWERBROADCAST | No registration here | `004ccd78` | Added, with ABI/result anomaly described below |
| `0466` private request | `004cce60` | `004ccd98` | Moved same pending-latch behavior |

The other 21 registrations retain their message/handler-address pairs; this does not by itself prove those callbacks retain their implementation. Original close and private-request callbacks are separately inspected as moved behavior, rather than classifying address movement as new functionality. Setter `004cc6d0` takes stack arguments message then handler, cleans 8 bytes, and does not invoke the callback; see the existing [table contract](window-message-handler-contract.md).

Message names/IDs were checked against the installed MinGW `winuser.h`, not inferred from current Ghidra names. The registration sets are observable facts even on hosts where these Windows messages behave differently.

The retained release sequence dates the focus-to-activation switch
to 1.4.0 and the power-message registration to 1.5.0.

| Checked builds | Focus or activation registrations | Power registration |
|---|---|---|
| Hosted original and Modern 1.0.0–1.3.1 | `0007 → 004ccd60`, `0008 → 004ccdd0` | Absent |
| Modern 1.4.0 | `001c → 004ccdf0` | Absent |
| Modern 1.5.0–1.6.1 | `001c → 004ccd04` | `0218 → 004ccd78` |

Reproduce by disassembling `004cd6c0..004cd939` in the retained
root EXEs and reading the message and handler pushes before each
direct call to `004cc6d0`. This covers registrations in the
matched initializer. It leaves other writers and OS delivery
outside the comparison.

The same registration scan gives the close and private-request
timeline:

| Checked builds | Close handler | Private request handler |
|---|---|---|
| Hosted original and Modern 1.0.0–1.3.1 | `004cce40` | `004cce60` |
| Modern 1.4.0 | `004cce48` | `004cce64` |
| Modern 1.5.0–1.6.1 | `004ccd5c` | `004ccd98` |

The private handler's 27-byte body matches across all 13 EXEs.
With a nonnull context it sets `00561270` to 1. The close
handler keeps its nonnull-context check and `PostQuitMessage(0)`
call. Version 1.4.0 drops the redundant CS prefix on that call
and shortens the preceding jump by one byte. The resulting
25-byte body matches through 1.6.1. Both handlers return 1
and pop the same 24 bytes of arguments. This comparison verifies
local behavior despite relocation. Actual window destruction and
consumption of the private request are separate paths.

## 2. Focus handling becomes application activation handling

Original WM_SETFOCUS callback `004ccd60..004ccdc7`:

- Requires nonzero context and matching HWND.
- Writes 1 to active flag `009f3d4c`.
- When `00561280` is nonzero and `0056127c` is zero, installs a thread hook through SetWindowsHookExA using type 2, callback `004ccc70` and zero module/thread arguments; stores the returned handle at `0056127c`.
- Invokes optional callback `[007f7484]` with EAX=1.

Original WM_KILLFOCUS `004ccdd0..004cce3b` checks HWND, writes active flag zero, conditionally unhooks `[0056127c]` and clears it, calls optional `[007f7484]` with EAX=0, calls ShowCursor(1), and invokes `004e070c` with `00564818` and length `0x80`.

Modern `004ccd04..004ccd5b` instead handles WM_ACTIVATEAPP. It requires nonzero context and matching HWND, compares wParam with the active flag, and does nothing if unchanged. On change it stores wParam, calls hook helper `004ccc40` for nonzero or unhook helper `004ccca4` for zero, performs the same `004e070c` call on deactivation, then notifies `[007f7484]` with EAX=wParam. It returns zero, allowing ordinary DefWindowProc processing through the dispatcher.

Modern helper `004ccc40..004ccca3` checks the sum of `[00561284]` and `[00561288]` and whether `[00561280]` is already nonzero. If requested and not installed, it first tries SetWindowsHookExA type `0x0d` with module `[009f3d48]`, callback `004ccb84`, thread zero. On failure it sets `[0056127c]=1` and retries type 2 on GetCurrentThreadId(), module zero. The accepted handle is stored in `00561280`. Helper `004ccca4..004cccc0` unhooks and clears that handle. These globals have **different roles across versions**; matching their addresses does not establish retained meanings.

Modern WM_CREATE calls the install helper and sets active flag 1; WM_DESTROY sets active flag zero and calls teardown. The original destroy callback merely returns zero. This is a concrete lifecycle change beyond moving code. Whether OS/Wine focus behavior improves in a particular setup requires runtime observation; no such run was made here.

### Original installer tail becomes screenshot code and padding

The original installer begins at `004cdc90` and returns at `004cdccb`. The final Modern keyboard repeat handler occupies part of that address range and returns at `004cdcba`. All 21 bytes at `004cdcbb..004cdcd0` become NOPs. They cover the last three bytes of the original `MOV ECX,1` at `004cdcb9`, the stores of the returned handle to `0056127c` and request flag to `00561280`, the epilogue and the alignment before the next entry. Modern's hook setup at `004ccc40` instead puts the handle in `00561280` and uses `0056127c` as the fallback marker.

Comparing this exact 21-byte slice of the [retained release executables](original-modern-differences.md#5-confirmed-menu-routing-difference), 1.0.0–1.3.1 match the original. Versions 1.4.0–1.5.2 have a RET at `004cdcbb` followed by 20 NOPs. The all-NOP slice first appears in the retained 1.5.3 and persists through final 1.6.1. Reproduce by extracting each `nfs3.exe` and reading the slice with `objdump -s --start-address=0x4cdcbb --stop-address=0x4cdcd0`. This dates the bytes at the old site. Hook installation success remains a runtime question.

## 3. Preserved dispatcher exposes a power-handler anomaly

The complete window procedure `004cd2d0..004cd347` is **120 identical bytes** in both baselines (SHA-256 `228975aac39547ab0e69a25a4278a63078e98b73d11471747e30cd5ea6c8f5a6`). It initializes a local Windows result to zero and calls the selected callback with six stack arguments:

`context, HWND, message, wParam, lParam, result_pointer`

A callback's EAX is only a handled/not-handled flag. If nonzero, the window procedure returns the local value written through `result_pointer`; otherwise it calls DefWindowProcA. The callback's EAX is **not** automatically forwarded as the Windows result (`004cd320..004cd33c`).

New callback `004ccd78..004ccd94` reads `[ESP+0x14]`, which is **lParam** under that six-argument contract. If the value is 0 or 1 it returns EAX=`0x424d5144`; otherwise it returns EAX=1. It never reads wParam and never writes through the sixth argument. Therefore all paths are handled and, through this unchanged dispatcher, return the unchanged local result **zero**. The magic EAX constant is not the Windows result.

Microsoft documents the event selector in **wParam** for [WM_POWERBROADCAST](https://learn.microsoft.com/en-us/windows/win32/power/wm-powerbroadcast). Its older [PBT_APMQUERYSUSPEND contract](https://learn.microsoft.com/en-us/windows/win32/power/pbt-apmquerysuspend) uses a Windows return value to grant or deny suspension and notes that this event ceased being supported in Vista. Against that documented interface, the argument/result handling above is anomalous. This is a static machine-level consequence, **not an observed suspend failure or a proven statement of author intent**. No speculative correction is applied. Other execution-state or power-management paths have not been excluded.

## 4. Class registration and failure handling

The original initializer calls GetModuleHandleA(NULL) at `004cd6f1` and stores it at `009f3d48`; Modern reads an already stored handle there at `004cd6ef`. Original also supplies a fallback class-name pointer when `[005612a4]` is null (`004cd6f8..004cd723`); Modern's shown initializer uses the existing value without this local fallback. This moves responsibility to earlier setup; that producer must be traced before asserting invalid or missing initialization.

Both still build class style `0x0b`, procedure `004cd2d0`, zero extra bytes, icon/cursor/name fields and call RegisterClassA. On class-registration failure, original gets the last error, calls its diagnostic routine and returns zero (`004cd787..004cd79e`); Modern calls the fatal-error wrapper `004b570c` with a message (`004cd74b..004cd750`). The wrapper's known fatal-error behavior is existing research, not newly executed here. The [geometry comparison](original-modern-window-geometry.md) now verifies retained creation policy through CreateWindowExA, shortened post-creation setup and three identical sizing helpers; context producers and all windowed/fullscreen effects remain unresolved.

## PreventMinimize: final mechanism versus historical claim

The [startup settings audit](original-modern-startup-policy.md#3-current-settings-exact-defaults-and-immediate-effects) establishes the final Modern parser-to-storage link: `PreventMinimize`, default 0, is stored as an unnormalized integer at `00561284`. The hook installation helper above consumes it together with `ScreenshoterEnabled` at `00561288` (default 1). Consequently, an installed hook alone does **not** establish that PreventMinimize is enabled: screenshot support can also request installation. The two settings share infrastructure; they are not interchangeable feature switches.

This gives **partial static support for MP140-068**: the final setting exists and reaches a changed hook lifecycle, including a type `0x0d` attempt followed by the type 2 fallback. The [historical startup trace](#the-120-keyboardhook-setting-gates-the-original-style-installer) below verifies the 1.2.0 gate and its replacement in 1.4.0. Actual Windows shortcut suppression and minimization remain untested.

## Hook filter comparison: selected keys and callback contracts

The additional repeatable audit is `python3 analysis/scripts/audit_keyboard_hook_filter_difference.py`; its [hash-pinned full filter spans](evidence/audits/keyboard-hook-filter-difference.json) cover original `004ccc70..004ccd5a`, Modern `004ccb84..004ccc3f`, Modern installation and the modifier wrappers. Ends are exclusive. This supplements the initializer audit; it does not execute hook events.

Both filters forward when hook code is not zero or active state `009f3d4c` is zero. Original takes the virtual key from the full wParam DWORD. Modern decodes only its low byte: in the type `0x0d` mode (`0056127c == 0`) it reads the first byte through lParam and marks down for message `0100h` or `0104h`; in fallback mode it reads the low wParam byte and derives down as the inverse of lParam bit31. The derived down/up value gates screenshot handling downstream, **not** the PreventMinimize key comparisons. Thus matching filter returns are not restricted locally to key-down events.

| Selected event | Original filter | Final Modern filter |
|---|---|---|
| Alt+Tab / Alt+Esc | Requires original `00561284 != 0` and lParam bit29; selects scan pairs `38h/0fh` or `38h/01h` | Requires PreventMinimize nonzero and Alt wrapper nonzero; returns 1 |
| Control+Esc | On original non-Alt path, signed GetAsyncKeyState(11h) negative selects `1dh/01h` | Requires PreventMinimize nonzero and Control wrapper nonzero; returns 1 |
| Keys `5bh`, `5ch`, `5dh` | On the original no-Alt/no-Control path, selects scan pair `0/key` | Requires PreventMinimize nonzero; returns 1 without modifier exclusion |
| Key `2ch` | On that same original no-Alt/no-Control path, selects scan pair `0/2ch` | Requires ScreenshoterEnabled nonzero, calls `004cdc50` with decoded down/up, then returns 1 |

“Selects” is deliberately distinct from “blocks”: original calls the optional function pointer at `00561288` with EAX=first scan component and EDX=second when a candidate was selected. A null pointer leaves the selection nonzero and returns 1; a present callback's return replaces the selection, so zero forwards through CallNextHookEx instead. The Alt+Tab arm additionally stores 1 at `00559448`. The callback implementation/later effects of that store are outside this bounded comparison. Original modifier branches are ordered: a taken Alt or Control path does not fall through to the unconditional key list when its key comparison misses.

Modern has no corresponding optional-callback veto on these selected blocking branches: `004ccc31` supplies literal EAX=1. Modifier helpers `004f1fd0` and `004f1fd4` use virtual keys `11h` and `12h`, returning a normalized value and ZF derived from signed AX after GetAsyncKeyState; the hook branches consume those flags. See the existing [modifier-wrapper comparison](original-modern-menu-input.md). This is a register-and-flags interface, not just a C return-value dependency.

The original startup route now resolves the ordinary callback question: `004b6165..004b617d` sets EDX=0 and EAX=1 before calling installer `004cdc90`. The installer stores EDX to callback slot `00561288` and EAX to `00561284`, then attempts the original type 2 hook if its handle is zero. Thus this inspected startup **requests the hook with Alt filtering enabled and no optional veto callback**. On that initialized path, selected events return 1 directly. The installer sets request flag `00561280` to 1 even if SetWindowsHookExA returns zero; a requested hook is not evidence of successful installation.

A bounded search of the original disassembly found one direct call to `004cdc90` (at `004b6178`) and one direct absolute store to `00561288` (inside that installer). This does not exclude indirect calls, aliased writes or later memory corruption. It establishes the shown startup producer, not a whole-program immutability proof. The separate `00559448` Alt+Tab side effect remains unresolved.

One reconstruction edge case follows from the raw setting values: the installer tests the **wrapping 32-bit sum** of `00561284` and `00561288`, rather than logical OR. Opposite nonzero values can therefore suppress installation (for example -1 and 1); two nonzero `80000000h` values also sum to zero. This is a static arithmetic consequence, not a tested user configuration. Preserve the sum or explicitly document a deliberate compatibility change; signed C addition must not introduce undefined overflow.

These mechanisms explain the final filtering changes but do not prove Windows/Wine hook acceptance, modifier timing, system minimization behavior or the vendor's Windows NT compatibility claim.

## Removed recurring foreground-restoration tail

Run `python3 analysis/scripts/audit_focus_restoration_difference.py`; the [retained comparison](evidence/audits/focus-restoration-difference.json) pins complete window-thread bodies, original `004cd4e0..004cd6b7` and Modern `004cd4e0..004cd663`. The prefix through `004cd655` is byte-identical except for the exit branch displacement at `004cd588`, retargeted from old epilogue `004cd6ae` to Modern `004cd65a`. The nine-byte epilogue is retained at that new location.

The original recurring loop tail at `004cd655` checks byte `009f3d2d`. If zero it returns to loop head `004cd582`. Otherwise it calls predicate `004f9120`: a nonzero result selects a second predicate `004f9070`, and if that returns zero it calls ShowCursor(0), then loops. The zero-result branch from the first predicate checks IsIconic on game HWND `009f3d24`; when that API returns zero, it calls SetForegroundWindow on that HWND before looping. This is a concrete **repeated foreground request route**, conditional on the shown state/predicate results, not evidence that Windows necessarily grants focus.

The predicate bodies now narrow those conditions without guessed names. Original `004f9120..004f9140` returns 1 exactly when **both** active flag `009f3d4c` and HWND `009f3d24` are nonzero; otherwise it branches to shared `XOR EAX,EAX; RET` at `004f9088`. Original `004f9070..004f908b` returns 1 when either DWORD `009f3d0c` or `00567180` is nonzero, else zero. The audit retains and asserts both complete spans, including that shared return.

Consequently, with outer byte `009f3d2d != 0`, the recurring foreground route is selected when **active flag is zero or HWND is zero**, then additionally requires IsIconic(HWND)==0. The null-HWND possibility is present in the instructions, but the loop's broader lifetime guards may prevent it in ordinary execution; no invalid-window behavior was observed. On the active/non-null-HWND branch, ShowCursor(0) is requested only when both other DWORDs are zero. Their semantic roles and all writer lifetimes remain unresolved. This separates the retry condition from the independent cursor branch instead of treating both as generic lost-focus handling.

Modern replaces that entire tail with a direct jump at `004cd655` back to `004cd582`, moves the epilogue and fills `004cd663..004cd6b7` with NOPs. The local IsIconic test, conditional foreground request and ShowCursor(0) request are removed together. The complete producers of these predicate inputs and `009f3d2d` are not reconstructed here, so this should not be simplified to “every lost-focus event always forces restoration” in the original.

The separate startup calls survive across the hosted original and
all 12 retained Modern EXEs. The 27-byte span `004cd55d..004cd578`
matches exactly. In each PE import table, `00534788` resolves to
`SetForegroundWindow` and `0053477c` resolves to
`SetActiveWindow`. The window thread calls them in that order,
with writes to the shared origin fields in between. This
distinguishes the retained startup requests from the removed
recurring request. OS acceptance of the calls remains untested.

### The foreground and cursor branches disappear at different points

Retained 1.0.0–1.3.1 match over the 88-byte window `004cd655..004cd6ad`. They retain the test of `009f3d2d`, both predicate calls, and the conditional ShowCursor(0) call. However, their jump at `004cd669` targets the back edge at `004cd680`, bypassing the original IsIconic / SetForegroundWindow branch. That original branch at `004cd685..004cd6ad` is entirely NOP-filled in these five releases. The `nfs3.exe` member from the retained 1.4.0 archive (SHA-256 `7cfecaac5e78dcbd8de059ea4e25bee1922c37df867e4d794c9b05960984d80d`) instead jumps directly to `004cd582` and places the epilogue at `004cd65a`, as in 1.5.0 and installed 1.6.1. The handle-clear instruction at `004cd64f` remains in place. To check the boundary, stream the 1.4.0 member with `7z x -so` and use `objdump -d -Mintel --start-address=0x4cd64d --stop-address=0x4cd665` on it and the retained 1.3.1 EXE.

Across the full 472-byte window-thread span `004cd4e0..004cd6b7`, 1.4.0 and installed 1.6.1 are byte-identical (span SHA-256 `0094e35550f96e19a93badbbebba0bd604843c574aa4eddc36e5c44fc9e3fd61`). Compared with 1.3.1, only the exit-branch displacement bytes at `004cd58a..004cd58b` differ before `004cd655`. The branch now targets the relocated epilogue, and all bytes from `004cd663` through the old end are NOPs. This also pins the pending-request consumer and handle-clear sequence as preserved locally across the transition. Called helpers and Windows callback effects remain outside the span.

The two predicate bodies at `004f9070..004f908a` and `004f9120..004f913f` match byte for byte in the original, 1.3.1, 1.4.0 and installed 1.6.1. An `objdump -d -Mintel` sweep across 1.3.1 and 1.4.0 finds one removed direct call to each: `004cd66b` to `004f9070` (10 → 9 sites) and `004cd662` to `004f9120` (6 → 5 sites). Every other decoded direct call to either predicate stays at the same address. The sweep covers decoded direct calls only. Both predicates still have callers and remain relevant when reconstructing the rest of the window code.

The recurring foreground request is therefore already absent in retained 1.0.0, consistent with MP100-040. The residual cursor branch survives through 1.3.1 and disappears at the 1.3.1 → 1.4.0 boundary.

### Direct foreground requests across builds

A linear `objdump -d -Mintel` sweep for calls through the SetForegroundWindow import slot `00534788` identifies nine addresses in every checked build: `004cd21f`, `004cd55d`, `004cda6b`, `004eb7ed`, `004ece12`, `0050558e`, `00507b9b`, `00507e20` and `0050846c`. The remaining sites distinguish the builds:

| Executable | Additional direct call sites |
|---|---|
| Original | `004cd6a2` (recurring loop), `004f9231` |
| 1.1.0 and 1.3.1 | `004f9231` |
| 1.4.0 and 1.5.0 | None |
| 1.6.0 | `004bef4e` |
| Installed 1.6.1 | `004bef5c` |

Thus the 1.3.1 → 1.4.0 comparison also loses the separate site at `004f9231`. The 1.6.0 and 1.6.1 additions both occur in runtime display-mode application at `004beeb0`. Each calls SetForegroundWindow on the game HWND after publishing the selected record dimensions through `004cdbd0`. The same-index path reaches publication without calling the driver, while a different index reaches it only on the admitted, nonzero driver-result path. A zero driver result skips the foreground request. See the [mode application comparison](original-modern-mode-selection.md). The removed site at `004f9231` belonged to [duplicate-instance recovery](original-modern-startup-requirements.md#separate-original-mutextitle-recovery-and-repurposed-handle-storage). In 1.3.1, startup still calls `004f91d0` at `004b6058`. That helper requests foreground focus only after the named mutex reports an existing instance and the title lookup finds a window. In 1.4.0 the old helper span contains different code and the decoded direct startup call is gone. The separate class-based FindWindowA call at `004a38ce` survives. Indirect calls and OS focus outcomes remain open.

### Original mode-state producers: a bounded link

The extended focus audit also retains original producer witnesses. At `0050818a`, raster setup tests **bit0 of `00564390`** and writes a normalized byte to `009f3d2d`: bit set loads AL=1; bit clear branches to `00508265`, clears AL and jumps back to the common store at `0050819f`. This operation is downstream of a `005644fc` check; its missing-state diagnostic route is not asserted to be nonreturning. This is an exact bit-to-state link, not a complete enumeration of renderer flags.

At the original window-initializer call `0050844e`, BL is loaded from that state byte, with width/height from `009f38e4/e8` supplied in EAX/EDX. A separate original call at `005246ef` supplies EBX=1 explicitly. The initializer's publication at `004cd946` stores BL back to `009f3d2d`. Thus the retry gate has concrete setup producers, including an explicit-on route, rather than being an unexplained constant or file-backed default.

The producer instructions also survive in the historical binaries. The original, retained 1.1.0–1.3.1, archive 1.4.0 and installed 1.6.1 have identical bytes at the bit test and store `0050818a..005081a3`, the BL store `004cd946..004cd94b`, and the call-site spans around `0050844e` and `005246ef`. A direct-store sweep in 1.1.0–1.3.1 finds the same two visible writes to `009f3d2d`. This establishes that 1.4.0 removes the focus-loop use while retaining the inspected producers. It leaves changes in caller reachability, indirect writes and the earlier 1.0.0 claim open.

Do not infer a permanent invariant that `009f3d2d == (00564390 & 1)`: the separate installer caller can supply 1, and all intervening writes/lifetimes are not proven. Likewise, calling the byte universally “fullscreen” would exceed this evidence. The [geometry chapter](original-modern-window-geometry.md) documents the related context-byte style behavior independently; complete field/global aliasing and cross-thread transition ordering still require inspection. These witnesses establish the local setup instructions. Their input values and reachability can differ across builds.

A separate original [named-mutex/title recovery helper](original-modern-startup-requirements.md#separate-original-mutextitle-recovery-and-repurposed-handle-storage) also requests foreground focus during startup. Its duplicate-instance handling is distinct from this recurring loop and must not be counted as the same mechanism.

This adds a direct mechanism to **MP100-040** beyond the activation-hook refactor. It remains partial evidence for the whole release-note claim: initial foreground/active requests at `004cd55d` and `004cd571` survive in the identical prefix, and the existing [mode-publication path](original-modern-mode-selection.md) also retains a foreground request. Removal of this loop tail does not establish absence of every possible focus-restoration route. The retained 1.0.0 executable verifies removal from this loop. Actual focus behavior remains unverified.

## Release-note mapping and next evidence

The lifecycle changes are relevant to **MP100-040**, the claim that the game no longer repeatedly restores lost focus. They are not sufficient to verify that entire claim: activation consumers and any focus-restoration API paths still need tracing. The retained builds date the loop change to 1.0.0 and the activation refactor to 1.4.0.

Next: inspect any alternate callback/alias writers and all focus/foreground API use sites; trace the earlier module/class-name producers; trace style/context producers and replacement cursor/input setup; keep the power callback anomaly separate from confirmed runtime behavior. The original and maintained Modern Ghidra databases and both executables remain unchanged.

## Mouse registrations move, callback bodies stay identical

The expanded [window audit](scripts/audit_window_initialization_difference.py)
asserts all ten message/handler pairs and complete callback-byte equality in
[the existing manifest](evidence/audits/original-modern-window-initialization.json).
It also classifies outside-body interval `004cd8f8..004cd939`: Modern fills65
bytes with NOPs,61 of which differ. Original registrations in that tail were
moved earlier in the rewritten initializer; they were not simply deleted.
The interval starts at an original CALL instruction within the sequence.

| Messages | Retained handler | Complete identical body |
|---|---|---|
| `0201,0203,0204,0206,0207,0209` (left/right/middle down and double-click) | `004cd130` |87 bytes, end exclusive`004cd187` |
| `0200,0202,0205,0208` (move and left/right/middle up) | `004cd190` |84 bytes, end exclusive`004cd1e4` |

The retained 1.4.0 initializer already registers all ten messages
with these same handlers at `004cd842..004cd8d8`. The old 65-byte
tail matches the hosted original through 1.3.1 and is entirely
NOPs from 1.4.0 through 1.6.1. Both complete handler bodies match
the hosted original in all 12 retained releases. Reproduce by
comparing the file-backed spans above and disassembling the new
registration calls in the 1.4.0 archive member. This dates the
registration move to the release that also changed the hook lifecycle.

Both callbacks first require nonzero context, using the six-argument callback
layout already verified through the retained dispatcher. They map wParam
bits0,1,4 to EBXbits0,1,2, extract packed lParam coordinates and call
`004fb470` with EAX=X, EDX=Y and ECX1 (down/double-click) or ECX0 (up/move).
Both return EAX0 with `RET18h`, leave the result-pointer value untouched and
therefore permit the outer window procedure's DefWindowProcA route.

Coordinate extraction is **zero extension** of both16-bit halves. For example,
packed component`ffffh` becomes65535 at this callback-to-helper boundary, not
−1. This behaviour is retained in both versions; the capture does not prove
how the downstream helper ultimately interprets/clamps it or whether such
coordinates reach it in an actual window. Do not silently replace extraction
with signed16-bit conversion while claiming exact original behaviour.

The shared coordinate helper also matches across the hosted original
and all 12 retained Modern EXEs. Compare its main span
`004fb470..004fb564` and the separate branch targets
`004fb6a0..004fb6e8`, with exclusive ends. The helper saves the
incoming ECX notification flag and EBX button mask separately.
On the notification path it tests the saved ECX after releasing the
lock, then passes the saved EBX in EAX to the callback at `0056446c`.
Thus the registration move preserves the inspected coordinate helper
and the distinction between down/double-click notification and up/move.
The installed callback and live clipping and capture state can differ.

The frontend notification target is also retained. In the hosted
original and all 12 retained Modern EXEs, the 21-byte setup at
`004730f9..0047310e` loads `0049bfb0` into EDX and publishes it
to `0056446c` after the EDX-preserving call to `0043b390`.
The complete 11-byte target at `0049bfb0` matches in all those
builds and ORs incoming EAX into `0055e5ec`. Reproduce by comparing
both file-backed spans in each root EXE. The verified setup and
target cover this frontend notification path. Other pointer writers
and accumulator clearing can still affect runtime behavior.

Both frontend polling bodies, `0049c000..0049c075` and
`0049c080..0049c0d1`, also match across the hosted original and all
12 retained Modern EXEs. In the first path, when polling is enabled,
pending bits 8–11 select the clear-and-return branch. Bit 8 produces
`0x0d`; the other bits alone produce zero. The second poll instead
tests the low nibble of the freshly polled button output at
`0055e5f4`. If nonzero, it clears the same accumulator and returns
`0x0d` for bit 0 or `0x1b` otherwise. Compare those half-open
file-backed spans in the extracted EXEs. This establishes continuity
of these two local consumers. Race and list consumers, event ordering,
and actual input behavior remain outside this check.

The frontend mouse-state wrapper and both coordinate scalers
also match the hosted original in every retained Modern EXE.
Compare the 173-byte window `00451480..0045152d` and the 48-byte
viewport-read window at `004beb80`. The wrapper first calls
`00435310` to read mouse state, then scales only the two coordinate
outputs when `00559234` is nonzero. Button and wheel outputs
bypass these conversions. This verifies the scaling instructions
and their gate. Live device state, viewport values and
the [release-specific context writers](original-modern-frontend-sound.md)
can still affect the result.

The lower buffered mouse reader also matches in the hosted original
and all 12 retained Modern EXEs. The 768-byte window
`00435310..00435610` includes its final RET at `004355fd` and the
start of the next routine. Compare PE RVA `35310h` for `300h`
bytes (SHA-256
`b60c4d0f711faa4d29c82eb79bd6c7db0e3a82f2d4b2055d740e339c73d77edc`).
The release notification path masks EAX with `0xf00` before calling
the same callback slot as the window mouse path. This confirms
continuity of the EXE-side reader and that bit domain. Device setup,
buffered events supplied by DirectInput, and runtime ordering remain
separate from the byte match.

The mouse-device setup window `004350c0..004351f0` also has
the same bytes in the hosted original and all 12 retained Modern
EXEs. It passes `00554ee8` as the output pointer at `00435111`,
then uses that slot for the device's format call at `0043512f`
and for the buffered reader. Compare 304 bytes at PE RVA
`350c0h` in the extracted executables. This verifies reuse of
the local creation and setup sequence.

The referenced mouse format data also match across all 13 EXEs.
The 24-byte descriptor at `0052f020` declares seven 16-byte object
records at `0052efb0` and a 16-byte state layout. The object
offsets are `0, 4, 8, 12, 13, 14, 15`. Concatenate the descriptor,
the 112-byte object table, and the four 16-byte GUIDs at
`0056b908`, `0056b948`, `0056b958`, and `0056b968` in that order
to reproduce SHA-256
`b2cfa9c31756bf30a724875b17c62be4f60b78dc19eda423162368fae6cbc80a`.
The first GUID is passed to device creation, and the other three
are referenced by the object table. This covers the local format
parameters. Indirect device methods and runtime results remain
separate.

**Status:** done, verified static for ten retained registrations, both complete
callback bodies, register forwarding and the61 changed-byte tail. Full
`004fb470` state/clip/capture processing, external message delivery, mouse
capture/focus interaction, Wine/VM behaviour and actual user input remain
unverified. This is evidence against interpreting the NOP tail as removed
mouse support, not proof of identical end-to-end mouse behaviour.

### The 1.2.0 KeyboardHook setting gates the original-style installer

Retained 1.2.0 startup calls `004b562c` at `004b616f`. The helper passes section `NFS3`, key `KeyboardHook` and fallback zero to the integer reader `004fb6f0`. A zero result skips installation. A nonzero result calls `004cdc90` with EAX=1 and EDX=0 at `004b564a`, the same installer arguments observed on the original startup route. The literal key is absent from retained 1.1.0. This verifies the 1.2.0 setting's startup gate. Actual key suppression and hook acceptance remain untested.

The retained archives give the following shipped defaults and installer call sites. In 1.3.1 the gate moved, but it still uses a zero fallback and skips the installer when the resulting value is zero.

| Release | Shipped INI | Original-style installer call |
|---|---|---|
| 1.0.0–1.1.0 | No `KeyboardHook` setting | Startup calls `004cdc90` directly at `004b6178`. |
| 1.2.0–1.3.0 | `KeyboardHook=0` | Gated call at `004b564a`. |
| 1.3.1 | `KeyboardHook=0` | Gated call at `004b55d2`. |
| 1.4.0 | `PreventMinimize=0` replaces `KeyboardHook`. | No decoded direct call to `004cdc90`. The final replacement lifecycle is documented above. |

The 1.0.0 call passes EAX=1 and EDX=0. The 64-byte installer
window at `004cdc90..004cdcd0`, including its trailing padding,
matches the hosted original and 1.1.0 (SHA-256
`bc6b3886ec41a22ff52abc872880bd7e2fe15d799c7cb68c10f4fc364b164c36`).
Neither `KeyboardHook` nor `PreventMinimize` appears in the shipped
1.0.0 INI or as an exact ASCII string in its executable.

Extract both `nfs3.ini` and `nfs3.exe` from the matching archive when comparing these defaults. The shipped value and executable fallback agree in the three retained builds with the old key. A user's effective value or OS hook behavior requires separate evidence.

In retained 1.4.0, the integer reader stores `PreventMinimize` with fallback zero to `00561284` at `004b5615` and `ScreenshoterEnabled` with fallback one to `00561288` at `004b563b`. Installer `004ccd2c` adds the two DWORDs and attempts installation only if the wrapping sum is nonzero and the handle at `00561280` is zero. It tries hook type `0x0d` first, then type 2 with the current thread ID on failure. Both attempts take callback `004ccc70`. Thus with ordinary values 0 and 1, disabling minimization prevention alone still permits installation for screenshots. These addresses are specific to 1.4.0. Actual hook installation remains untested.

The create/activate/destroy lifecycle is already present in retained 1.4.0. Window initialization registers `0001 → 004ccdb0`, `0002 → 004ccdd0` and `001c → 004ccdf0` at `004cd77c..004cd7a0`. The create callback's installation call is at `004ccdb9`, the destroy cleanup call at `004ccde3`, and the activation handler calls install or cleanup at `004cce18` and `004cce1f`. This places the new lifecycle in the same retained release as the setting rename. The corresponding helper and call sites have moved to their final addresses by retained 1.5.0. The static registration does not establish the order in which a particular Windows or Wine session delivers those messages.

The full 100-byte installer matches between 1.4.0 at `004ccd2c`
and 1.5.0 at `004ccc40` except for four bytes in the two immediate
callback addresses. Both hook attempts switch from `004ccc70` to
`004ccb84`. All six retained installers from 1.5.0 through 1.6.1
match at the latter installer address, including the final RET.
Compare the 100 file-backed bytes in the extracted EXEs to reproduce.
This dates the final install policy to 1.4.0 and the callback
redirection at those call sites to 1.5.0. Callback behavior and OS
hook acceptance are separate from the installer comparison.

The 29-byte teardown body also matches from 1.4.0 through 1.6.1.
It moves from `004ccd90` to `004ccca4` in 1.5.0. All seven EXEs
bind `005347a8` to `UnhookWindowsHookEx`. For a nonzero stored
handle, the helper calls the API and clears `00561280` on its
ordinary return, regardless of the API result. For a zero handle,
it returns without calling the API. The same helper services the
shared shortcut and screenshot hook. This comparison establishes
the executable's teardown policy. It does not establish that the
OS accepted the removal or what callbacks remained in flight.

The complete 88-byte `WM_ACTIVATEAPP` handler moves from
`004ccdf0` in 1.4.0 to `004ccd04` in 1.5.0. Only two bytes
differ, both in the displacement of the call to `004e070c`.
The installer and unhook calls retain their relative offsets
because their targets move by the same amount. The handler
stays byte-identical from 1.5.0 through 1.6.1. Thus the same
context, HWND and active-state checks gate hook changes throughout
these releases. Deactivation still unhooks before clearing the
128-byte keyboard state and calling the optional notification.
Actual message delivery and hook acceptance remain untested.

The complete 30-byte callbacks for `WM_CREATE` and `WM_DESTROY`
also match across the seven retained builds from 1.4.0 through
1.6.1. Their entries move from `004ccdb0` and `004ccdd0` to
`004cccc4` and `004ccce4` in 1.5.0. With a nonnull context,
creation calls the installer before marking the app active.
Destruction marks the app inactive before calling teardown.
Both skip their state changes on a null context and return zero.
This verifies the order at these callbacks. Delivery and OS hook
results remain runtime questions.

### Deferred window destruction keeps its local request consumer

The 67 bytes at `004cd612..004cd655` match the hosted original
in all 12 retained Modern executables. This window tests and clears
the private-request latch, optionally calls `004ecd50`, calls
`DestroyWindow` with the stored HWND, and clears the stored handle
on ordinary return. The instructions immediately after that block
do change. In 1.3.1, `004cd655` tests byte `009f3d2d` before the
next loop iteration. In 1.4.0 and final 1.6.1, the bytes at that
address begin a direct jump to `004cd582`. The pending-request
consumer is retained while the surrounding message pump changes.
See the [renderer cleanup trace](original-modern-renderer-lifecycle.md)
for the corresponding waiting path. Runtime teardown and wait
completion remain untested.

### Later initializer changes are confined to the registration-failure diagnostic

The 633-byte address window `004cd6c0..004cd939` matches the
hosted original through retained 1.3.1. After the 1.4.0 and 1.5.0
registration rewrites, only two byte positions in that same
window vary from 1.5.0 through 1.6.1:

| Release | Diagnostic string operand at `004cd74b` | Call target at `004cd750` |
|---|---|---|
| 1.5.0 | `00540468` | `004b56c4` |
| 1.5.1 | `00540468` | `004b56e8` |
| 1.5.2–1.5.3 | `00540468` | `004b56f8` |
| 1.6.0 | `0054046c` | `004b56f8` |
| 1.6.1 | `0054046c` | `004b570c` |

The old and new pointers resolve to the same RegisterClass
failure text in the checked 1.5.2 and 1.6.1 EXEs. Reproduce by
comparing PE RVA `cd6c0h` for `279h` bytes and decoding the two
operands. This confines the changes within the initializer after
1.5.0 to the diagnostic operands. The called routines and runtime
registration results require separate evidence.

Following the diagnostic call in all six retained 1.5.0–1.6.1
EXEs leads to a 25-byte body. The bodies match after excluding
the displacement of the call at offset `+0x13`. That call always
targets the termination thunk at `004f2a7d`. Each helper calls
`MessageBoxA` via import slot `00534764`, with the initializer's
text, the same title pointer and flags `0x51010`. It calls the
termination thunk on return from the dialog without testing
the dialog result. This verifies the local diagnostic policy
despite relocation. Actual dialog and shutdown outcomes remain
untested.
