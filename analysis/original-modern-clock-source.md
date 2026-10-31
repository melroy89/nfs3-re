# Original versus Modern: clock source and retained timer algorithms

## Scope and evidence

**Static comparison; no timing/performance measurement.** Baselines: supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [provenance](original-modern-differences.md).

Run `python3 analysis/scripts/audit_clock_source_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-clock-source.json) hash-checks both binaries, verifies 16 paired clock-call instructions and compares complete retained body ranges for three timer functions after replacing only their old clock-IAT operands. Raw assembly remains ignored under `analysis/captures/modern-differences/clock-source/`. No game/API execution, process scheduling changes or Ghidra/executable edits.

## 1. A real call-target change, not merely a new import

| Property | Original | Official Modern |
|---|---|---|
| Shared reader `004f2790` calls | KERNEL32.GetTickCount, IAT `00534568` | WINMM.timeGetTime, IAT `00534664` |
| Reader instructions | Explicit ECX/EDX saves; CS-prefixed indirect call; return at `004f279b` | Same explicit saves, unprefixed indirect call; return at `004f279a` |
| GetTickCount import | Present | Still present |
| GetTickCount import thunk `00533d18` | Present | Retained |
| timeGetTime import | Absent | Present |

The wrapper returns the API DWORD in EAX. Its one-byte shortening comes from removing the redundant CS prefix, not introducing a different time-unit conversion. Both original and Modern surrounding callers can use that retained wrapper, so unchanged caller bytes do not imply an unchanged time source.

## 2. Sixteen paired direct callsites

These instruction addresses are independently verified against both PE images. Each originally calls GetTickCount and now calls timeGetTime:

| Modern analysis context | Paired call addresses |
|---|---|
| Timer worker `0048eb90` | `0048eb97`, `0048ebe4` |
| Multimedia pulse callback `0048ed30` | `0048ed70`, `0048ed8e` |
| Timer initialization `0048eff0` | `0048f13d`, `0048f160`, `0048f17b` |
| Network/session code neighborhood | `0049faba`, `0049fad9` |
| Surface lock/unlock/relock family | `004ed169`, `004ed2ec`, `004ed366`, `004ed3a6` |
| Shared clock reader | `004f2792` |
| Connection-state initialization neighborhood | `004f6e9c`, `004f6ee3` |

Context labels come from the saved Modern analysis; this table does not fully re-audit the callers or transfer their names to every original function. A linear disassembly scan also found original call `004b56d5` in a region now reused by settings code; that region is not treated as a corresponding Modern clock call. Indirect calls, dynamically resolved clocks and arbitrary aliases remain outside this direct-site list. Retaining an unused-looking import/thunk does not prove it executes or is universally unreachable.

The clock switch is consequently broader than a single frame counter. This does **not** establish a changed race frame-rate cap, fixed simulation frequency, replay protocol or network synchronization algorithm.

## 3. Three timer bodies retain their surrounding instructions

For these complete saved function-body ranges, the evidence script substitutes `00534664` for `00534568` **only at the identified call operands in a temporary comparison buffer**. It then requires exact byte equality with Modern:

- `0048eb90..0048ec3c`: two call operands.
- `0048ed30..0048ee26`: two call operands.
- `0048eff0..0048f06f` plus `0048f075..0048f1e4`: three call operands.

No executable is patched. This proves that the other instructions in those ranges are retained, rather than inferring a scheduler rewrite from a changed function hash.

For example, worker `0048eb90` retains its elapsed-tick subtraction, low-32-bit multiplication by **1193**, accumulator/high-word update, stop checks and callback iteration. Pulse callback `0048ed30` retains its signed deadline tests, timer-event submission and shutdown/wake paths. Timer initialization retains its timeBeginPeriod call at `0048f0d7` and timeSetEvent setup; these APIs are not newly introduced by the clock switch. Their stored arguments, callback targets, system behavior and runtime state still require separate validation.

Byte equality after operand normalization does not prove equal scheduling, callback interleaving or runtime results: the input clock values are deliberately different and data/provider behavior can also differ.

## 4. “More accurate” is not a measured result

The API choice matches **MP153-012**. Microsoft's [GetTickCount documentation](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-gettickcount) describes a typical 10–16 ms resolution. Its [timeGetTime documentation](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timegettime) describes machine-dependent precision and the relationship with timeBeginPeriod. These support a possible resolution benefit, not a benchmark of this game or Wine.

Both APIs return **32-bit milliseconds since system start**, wrapping after approximately 49.71 days. Modern does not thereby become a 64-bit or floating-point high-resolution clock. Actual resolution, accuracy, jitter and frame pacing remain unmeasured here. Existing timeBeginPeriod requests and OS/Wine implementation must be considered before predicting improvement.

For reconstruction/native-port work, preserve the 32-bit arithmetic and each caller's signed/unsigned comparisons unless making an explicit behavioral change. Replacing timestamps with an unrestricted 64-bit monotonic duration, or interpreting the clock-source change as x87/physics equivalence, is not supported by this audit. No rollover test was run and no claim is made that every original/Modern caller handles wrap correctly.

## Next evidence

The separate [loading timing comparison](original-modern-loading-timing.md) follows a caller that changes beyond its clock source. Remaining work includes frame-pacing/simulation consumers, all indirect clock paths, actual timer resolution under the chosen OS/Wine, and controlled compatibility tests if required. Clock API agreement alone does not establish multiplayer or replay equivalence.
