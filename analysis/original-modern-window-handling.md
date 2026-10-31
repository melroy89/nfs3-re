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

This gives **partial static support for MP140-068**: the final setting exists and reaches a changed hook lifecycle, including a type `0x0d` attempt followed by the type 2 fallback. It does not establish the historical replacement of `KeyboardHook` between particular Modern releases, or successful prevention of minimization on Windows NT. The comparison has only original and final Modern baselines; MP120-011's intermediate setting and Windows-version claims remain vendor-only. Follow-up requires the relevant intermediate package for the rename and callback/OS behavior evidence for effectiveness. No such behavior was executed for this finding.

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

### Original mode-state producers: a bounded link

The extended focus audit also retains original producer witnesses. At `0050818a`, raster setup tests **bit0 of `00564390`** and writes a normalized byte to `009f3d2d`: bit set loads AL=1; bit clear branches to `00508265`, clears AL and jumps back to the common store at `0050819f`. This operation is downstream of a `005644fc` check; its missing-state diagnostic route is not asserted to be nonreturning. This is an exact bit-to-state link, not a complete enumeration of renderer flags.

At the original window-initializer call `0050844e`, BL is loaded from that state byte, with width/height from `009f38e4/e8` supplied in EAX/EDX. A separate original call at `005246ef` supplies EBX=1 explicitly. The initializer's publication at `004cd946` stores BL back to `009f3d2d`. Thus the retry gate has concrete setup producers, including an explicit-on route, rather than being an unexplained constant or file-backed default.

Do not infer a permanent invariant that `009f3d2d == (00564390 & 1)`: the separate installer caller can supply 1, and all intervening writes/lifetimes are not proven. Likewise, calling the byte universally “fullscreen” would exceed this evidence. The [geometry chapter](original-modern-window-geometry.md) documents the related context-byte style behavior independently; complete field/global aliasing and cross-thread transition ordering still require inspection. These original-only witnesses explain the removed mechanism's conditions, not equal setup semantics in Modern.

This adds a direct mechanism to **MP100-040** beyond the activation-hook refactor. It remains partial evidence for the whole release-note claim: initial foreground/active requests at `004cd55d` and `004cd571` survive in the identical prefix, and the existing [mode-publication path](original-modern-mode-selection.md) also retains a foreground request. Removal of this loop tail does not establish absence of every possible focus-restoration route. Runtime behavior and historical release introduction remain unverified.

## Release-note mapping and next evidence

The lifecycle changes are relevant to **MP100-040**, the claim that the game no longer repeatedly restores lost focus. They are not sufficient to verify that entire claim: activation consumers and any focus-restoration API paths still need tracing. No release-introduction date can be proven from only original and final Modern binaries.

Next: inspect any alternate callback/alias writers and all focus/foreground API use sites; trace the earlier module/class-name producers; trace style/context producers and replacement cursor/input setup; keep the power callback anomaly separate from confirmed runtime behavior. The original and maintained Modern Ghidra databases and both executables remain unchanged.
