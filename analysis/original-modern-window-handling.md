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

Both still build class style `0x0b`, procedure `004cd2d0`, zero extra bytes, icon/cursor/name fields and call RegisterClassA. On class-registration failure, original gets the last error, calls its diagnostic routine and returns zero (`004cd787..004cd79e`); Modern calls the fatal-error wrapper `004b570c` with a message (`004cd74b..004cd750`). The wrapper's known fatal-error behavior is existing research, not newly executed here. Window style/size selection in the thread callback and CreateWindow paths remains a separate comparison; this chapter does not establish all windowed/fullscreen changes.

## Release-note mapping and next evidence

The lifecycle changes are relevant to **MP100-040**, the claim that the game no longer repeatedly restores lost focus. They are not sufficient to verify that entire claim: hook callback bodies, activation consumers and any focus-restoration API paths still need tracing. No release-introduction date can be proven from only original and final Modern binaries.

Next: compare hook callbacks and all focus/foreground API use sites; trace the earlier module/class-name producers; compare actual window style/size creation; keep the power callback anomaly separate from confirmed runtime behavior. The original and maintained Modern Ghidra databases and both executables remain unchanged.
