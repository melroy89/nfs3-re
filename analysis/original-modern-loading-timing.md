# Original versus official Modern: loading timing

## Scope and binaries

This is a bounded static comparison of Modern loading-clock helpers `004a354c` and `004a3558`, their loading-sequence callers, and the `LoadingSplashTime` setting. It does not establish a visible minimum splash duration or the behavior of the timer worker.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.

The paired function inventory lists Modern helpers `004a354c` (11 bytes) and `004a3558` (77 bytes) as changed same-VA ranges, with the original entry not identified by autoanalysis. Disassembly confirms these addresses are not corresponding original helper functions: in original they fall inside a different routine's loading/presentation sequence.

## Modern reset and remaining-time calculation

Modern `004a354c` calls shared clock helper `004f2790` and stores its EAX result in `007a27a0` (`004a354c–3556`). The loading-sequence caller invokes it at `004a3417`, before the loading artwork and related setup work. The [clock-source comparison](original-modern-clock-source.md) establishes that this wrapper returns timeGetTime milliseconds in Modern.

Modern `004a3558` is called later at `004a347d`. Its observed arithmetic is:

1. Read current clock `now` through `004f2790`.
2. Compute elapsed as `now - [007a27a0]`.
3. Set `007a27a0` and `007a27a4` to `now`; clear accumulator `007a27a8`.
4. Compute low-32-bit `LoadingSplashTime * 1000 - elapsed` from `[007a27b0]`, interpret that result with signed comparisons and clamp it to `0..10000`, and store it at `007a27ac` (`004a3558–35a4`).

The settings loader reads `LoadingSplashTime` with code fallback `5` and writes the returned integer to `007a27b0` (`004b5624–5633`). This gives the timing helper a millisecond-scaled target and an explicit ten-second ceiling. No unit conversion is applied in the settings loader itself; the multiplication by 1000 is in `004a3558`.

After resetting this state, the Modern caller invokes `00495230` with zero at `004a3484`, followed by `0040fefc`. Other presentation steps pass fixed floating-point values to `00495230` (`004a349b–3527`). Within `00495230`, the timing path checks `0079f288`, invokes `004955a0`, then calls `00490134` with its caller-supplied value; a negative result exits that presentation step (`00495242–266`). `004955a0` can clear `007a27ac` after a nonzero input-poll result from `00451960` (`004955a0–5c3`). These links show the configured remaining-time state is consumed by the loading presentation path, with millisecond clock units; actual input state, scheduling and visible duration remain untested.

## Consumer and input cancellation

`00490134` reads the same clock at `0049013c`. Except for incoming float-bit value 100.0, it returns integer `-1` when no more than 50 ms has elapsed since the prior update (`00490143..00490159`). Otherwise it compares time since `007a27a0` with the remaining target at `007a27ac`, computes a percentage while inside that interval, and limits later stored progress through its prior-value-plus-5 path. The state is stored at `007a27a8` and last-update time at `007a27a4`. This is progress-estimate throttling; the helper contains no blocking sleep that by itself establishes a five-second screen duration.

`004955a0` calls input routine `00451960` with EAX=1 when the remaining target is nonzero. A nonzero result clears that target; it is not a worker-readiness test. It then calls `004a33d0`, which retains an existing abort latch or tests scan-code 1 through `004eb1c0` and sets `0055e88c` on success. This supports input-based skipping and the Escape abort route in the inspected path, without proving all input devices or presentation states.

For ordinary fitting settings, the configured multiplication represents seconds converted to milliseconds. With arbitrary large/negative INI integers, wrapping IMUL/SUB occur before the signed clamp; do not translate the formula into unbounded mathematical arithmetic and assume identical results.

## Original path at the corresponding addresses

The original bytes at `004a354c` are not a reset helper. At that address the loading sequence calls `004283d0`, tests its return, and may return early (`004a354c–3560`). The surrounding original caller includes fixed float arguments to `00495230`, including `5.0` at `004a3477–3481` and later values at `004a34a3–35bd`; it also uses `004f0240` after the initial presentation call (`004a3481`). Original contains no direct call to `004a354c` or `004a3558` as separate helpers in the inspected loading sequence, and does not use Modern's `007a27a0..007a27ac` state there.

The direct sequence comparison is therefore:

| Stage | Original | Official Modern |
|---|---|---|
| Establish timing baseline | No corresponding helper call in the loading sequence | `004a3417 -> 004a354c`, save clock at `007a27a0` |
| Refresh timing state | Fixed presentation arguments; no `004a3558` call | `004a347d -> 004a3558`, compute remaining configured time into `007a27ac` |
| First subsequent presentation argument | `5.0` (`004a3477–3481`) | `0` (`004a3484`) |
| Time configuration | No corresponding setting use in this sequence | `007a27b0` default 5 seconds; remaining target bounded to 0–10,000 ms |

This establishes a code-path change from fixed arguments and a distinct polling call to Modern's configured remaining-time state. It does not show that `LoadingSplashTime=5` means the screen remains visible for exactly five real seconds: earlier work contributes to elapsed time, the shared clock can wrap, and the worker/renderer synchronization has not been fully traced here.

## Retained evidence

Run `python3 analysis/scripts/audit_clock_source_difference.py` (Python `pefile`, GNU `objdump`). The [clock/loading manifest](evidence/audits/original-modern-clock-source.json) retains original loading sequence `004a3400..004a35ca`, Modern sequence/helpers and direct timing/input consumer spans. Raw captures stay ignored under `analysis/captures/modern-differences/clock-source/`.

## Limits

Static evidence comes from the two hash-pinned executables and the paired function inventory at `analysis/evidence/audits/original-modern-function-diff.json`; raw disassemblies are retained as ignored captures. The shared clock helper `004f2790`, Modern timer worker and broader timer API changes are intentionally not re-audited here. No game, probe, test or Ghidra operation was performed; no executable was modified.
