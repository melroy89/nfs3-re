# Original versus Modern: startup error mode, affinity and settings

## Scope and evidence

**Verified static instructions; operating-system behavior not exercised.** Baselines: supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [provenance](original-modern-differences.md).

Run `python3 analysis/scripts/audit_startup_policy_difference.py` from the repository root (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-startup-policy.json) retains identities, instruction-span hashes, option strings and resolved static imports. Raw captures remain under ignored `analysis/captures/modern-differences/startup-policy/`. The old startup call span is compared as a removed region, not equated with the new settings function at a different address.

Modern's application startup calls `004b5580` at `004a3e4e`. That function reads section `NFS3`; [configuration precedence](original-modern-configuration.md) is INI value, then environment fallback, then the callsite's default. The defaults below are **code fallbacks**, not a claim about every installed INI/environment or prior release.

## 1. Error-reporting suppression becomes optional

Original has `PUSH 2; CALL [005345e4]` at `004a3ad9..004a3ae1` and again at `004a3b29..004a3b39`, without an INI-option condition at either callsite. The IAT entry is SetErrorMode. The entire original span `004a3ad9..004a3b39` is NOP bytes in official Modern, including these calls. This witnesses their removal, without reconstructing every original exception/startup path surrounding them.

Modern `004b5586..004b559d` reads `NoErrorReporting` with default **0**. Only a nonzero value performs SetErrorMode(2) at `004b5598`. It does not call SetErrorMode(0) for a false option, preserve/merge current flags before setting 2, or restore the previous mode locally. The API's previous-mode return value is ignored.

Literal 2 is `SEM_NOGPFAULTERRORBOX` (also verified in the installed MinGW header). Microsoft's [SetErrorMode documentation](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-seterrormode) describes the error-mode flag and parent-process inheritance. Therefore “suppression disabled by default” means this Modern option does not request it by default; it does **not** prove the effective inherited error mode is zero or that any particular crash dialog appears under Wine/Windows. No crash was induced.

This statically supports the default-policy portion of **MP100-025**. The binary pair alone cannot date the change to its first release.

## 2. Affinity is opt-in in the final Modern binary

Modern `004b559e..004b55cd` reads `SingleProcAffinity` with default **0**:

- False skips the whole resolution/call sequence; it does not widen or reset an inherited affinity mask.
- True passes module string `KERNEL32.DLL` and export string `SetProcessAffinityMask` to `004f1ebc`.
- Resolver `004f1ea0` first tries GetModuleHandleA, then LoadLibraryA if absent. Wrapper `004f1ebc` calls GetProcAddress when a module handle is available.
- Null resolved function pointer skips affinity setup. Otherwise GetCurrentProcess at `004b55c3` supplies the process handle; `PUSH 1`, `PUSH EAX`, `CALL EBX` at `004b55c9..004b55cc` invoke the export with literal mask **1**.
- The affinity API result is ignored; there is no local GetLastError, fallback mask selection or verification of the resulting affinity.

This is a proven dynamically resolved API use, unlike a DLL/export name merely present in strings. Microsoft's [SetProcessAffinityMask contract](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setprocessaffinitymask) defines mask bits as logical processors and permits failure. Thus the visible request is specifically bit 0, not an algorithm choosing an arbitrary available core; success on a constrained CPU set or under Wine is not established. The original-versus-final comparison here does not prove the original had no affinity operation anywhere else.

Release notes **MP100-021** describe an early automatic single-core policy, whereas the final package's code default is zero and its README's current option description agrees. **MP130-001** says multicore hangs were fixed. These are historical claims; observing the final optional branch does not prove the claimed hang fix or reproduce the early release's enabled default. No intermediate executable or multicore runtime comparison was inspected for this chapter.

## 3. Current settings: exact defaults and immediate effects

These values are recovered from the official settings loader. They describe the Modern mechanism and downstream writes, not a claim that every listed setting is entirely new versus original or that all consumers have been validated.

| Key | Code fallback | Immediate loader behavior |
|---|---:|---|
| `NoErrorReporting` | 0 | Nonzero calls SetErrorMode(2). |
| `SingleProcAffinity` | 0 | Nonzero attempts the resolved affinity call with mask 1. |
| `NoMovies` | 0 | Nonzero sets bit 11 of `0055eb2c`; zero does not locally clear an already set bit. |
| `OwnHeapLimitMb` | 32 | Signed clamp to 16..512, shift left 20, store byte count at `007a2760`. |
| `PreventMinimize` | 0 | Stores raw integer at `00561284`; [window hook lifecycle](original-modern-window-handling.md) consumes this state. |
| `LoadingSplashTime` | 5 | Stores raw integer at `007a27b0`; no local range clamp or time-unit conversion here. |
| `IntroSplashTime` | 0 | Stores raw integer at `007a279c`; consumer/time units are separate. |
| `Use32bitModeInMenu` | 0 | Stores at `007a2794`; subsystem setup chooses menu depth 16 for zero, 32 for nonzero (`004b5c3b..004b5c4b`). |
| `Hide16bitModes` | 0 | Stores raw integer at `007a2798`; complete mode-filter effects remain separate. |
| `ScreenshoterEnabled` | 1 | Stores at `00561288`, feeding the [screenshot hook/request path](original-modern-screenshots.md). Spelling follows the executable. |
| `ScreenshoterFormat` | `png` | Reads into an 8-byte temporary, copies a bounded three-character format to `007a2780`, and optionally parses `@` plus numeric quality; unsigned values 0..100 can replace `0054d7e0`. See screenshot format/encoder limitations. |
| `AllowHugeTextures` | 0 | Unsigned values 0..3 choose `256 << value` at `007a278c`; all other values use shift 0, therefore 256. No large/undefined shift from arbitrary INI input in this local path. |
| `WindowedMode` | 0 | Stores raw integer at `0067900c`; setup stores logical inverse as a normalized 0/1 at `00564390` (`004b5c50..004b5c5d`). Full window creation/backend support is separate. |

The integer/string readers do not normalize every boolean to 0/1. Some settings are tested as nonzero later; others are retained as raw integers. Reconstruction must preserve the actual comparisons and avoid silently replacing all settings with C booleans.

For `OwnHeapLimitMb`, negative inputs compare as signed values and clamp to 16; inputs above 512 clamp to 512. The chosen range makes the subsequent `SHL 20` fit in a positive 32-bit byte count (16,777,216..536,870,912). This checks arithmetic range, not allocator success. Startup also performs a separate capacity check; the [heap comparison](original-modern-heap-initialization.md) establishes the original fixed-size/null-backing-pointer path and retained adapter/allocator instructions.

## Limits and next evidence

- All stated options are from the final official binary; historical option names/default changes need intermediate releases for direct verification.
- Reading/writing a configuration global is not proof of every behavior named by the key. Time units, all movie paths, texture admission and full window creation need consumer traces.
- No API, process affinity, error mode, INI file or running game was changed. The maintained Ghidra project and executable bytes are unchanged.
- Next: allocator callback targets/lifetimes, earlier startup argument/config initialization, and consumer comparisons for the remaining settings. Preserve observed return-value handling and suspected original defects in any future reconstruction.

## Outside-body startup span ends in an application jump table

The [outside-body inventory](original-modern-outside-function-index.md) now classifies complete1002-byte interval **`004a39c6..004a3db0`** as **974 Modern NOP bytes** through`004a3d94`, then a **28-byte jump table** through`004a3db0`. The first part contains973 changed positions; the table contains27, totaling1000. The manifest asserts the NOP run and exact seven target DWORDs. Original bytes occupy longer startup/application control flow; this same-address split is not an original function definition.

Modern dispatcher`004a3eb7` subtracts6 from EAX, compares the result unsigned with6 and branches back to`004a3ea0` when above range; otherwise`004a3ebf` jumps through the table. Its mapping is:

| Raw state | Target |
|---:|---|
| 6,7 | `004a3ee8` |
| 8,9,10 | `004a3ea0` |
| 11 | `004a3ec6` |
| 12 | `004a3ed7` |

An earlier loop check at`004a3ea4` handles state10 before ordinary dispatch, so the presence of a table slot is not proof that every slot is reached. The [existing next-round handoff](network-series-next-round-state.md) already traces surviving frontend actions6/7 to`004a3ee8` and race preparation`004a3ef4`; it supplies the relevant semantic context without inventing a new function at the table. Complete original startup removal, all state producers/overrides and runtime progression remain unresolved on their existing boundaries. No application or new instruction probe was executed.


## Removed version-resource startup producer

The [configuration header producer audit](original-modern-config-loading.md#original-startup-populates-the-header-template-from-a-version-resource) identifies another removed startup operation: original `004a38f0` reads a FileVersion resource and startup `004a3a97` parses its string into the original header template. Final Modern removes this callsite and uses a file-backed version6 template elsewhere. The [scanner follow-up](original-modern-config-loading.md#scanner-width-and-conditional-version2-header) now verifies DWORD stores and a conditional version2 result; runtime source-file selection and later writes remain unresolved; the original zero-filled template must not be treated as a whole-lifetime version0 invariant.


The [failure/copy follow-up](original-modern-config-loading.md#version-reader-failure-gates-and-string-copy-boundary) also records the original zero-only scan-result check, bounded copy/padding semantics and final removal of the static `VERSION.dll` import descriptor. These are local startup/interface differences; malformed-resource runtime behavior remains untested.


## Removed optional floating-point error startup policy

Original [fpuerrors initialization](og-modern-x87-precision.md#removed-optional-startup-exception-unmasking) at `004a3d05..004a3d4a` conditionally clears five x87 exception-mask bits through a retained guarded helper. Final replaces all69 bytes with NOPs and empties the named switch. Precision and rounding bits are unaffected by those five original updates; later control-word resets remain separate.
