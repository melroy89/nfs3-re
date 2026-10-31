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

## Original polling call is an input drain, not a timed delay

The expanded clock audit asserts original CALL `004a3481 ->004f0240` and the complete10-byte helper `004f0240..004f024a`, identical in both executables. It repeatedly calls `004cc970`, tests the full EAX result and loops while nonzero. On ordinary exit EAX is zero. There is no timer read or sleep in this wrapper. Existing [queued-input contracts](detailed-analysis-notes.md#queued-input-result-wrappers-004f00d0-004f0240) establish its dequeue source; source locking/translation and concurrent producers remain separate concerns, so this is not an atomic flush guarantee.

Consequently removing this call from a loading sequence must not be described as removing a fixed sleep or establishing the “super quick gameplay loading” claim MP140-060. Its cost depends on queued input and source behavior. The already documented clock/progress restructuring, removed descriptor queries and display timing are concrete code differences, but no end-to-end loading benchmark has established that release-note claim. It remains vendor-only in the catalog. This clarification prevents a plausible timing label from replacing the actual instructions; no input or game code was executed.

## Paired progress-entry admission before renderer preparation

The clock audit now retains paired entry prefixes: original `00495230..0049527f`, Modern `00495230..00495279`. Both first call `004e7630` with EAX0 and require active DWORD `0079f288` nonzero. Original then immediately calls renderer slots `009ef948` with stack argument0 and `009ef938` with2, executes FINIT/FLDCW from `0079f3f4`, and begins float progress work. These callbacks and FPU changes precede that original prefix's percentage calculation; no equivalent early time-admission test appears in the captured original prefix.

Modern instead calls input/abort helper `004955a0`, rejects a nonzero abort latch, then calls timing estimator `00490134` with the incoming float bits. A signed-negative EAX result takes `00495268`, sets EAX0 and jumps to the exit at `00495594`, before preparation calls `00434b20`/`004c4480` at `0049526f/74`. The estimator's previously established <=50-ms sentinel can therefore suppress entry into that preparation/rendering continuation. It does not suppress the earlier common `004e7630` call or input/abort handling.

This adds a concrete caller consequence to the timer formula: Modern can skip a progress-update continuation before renderer preparation, whereas original's inspected prefix proceeds directly to renderer callbacks once active. The evidence is bounded to these prefixes and linked estimator; it does not prove the entire original body has no later throttle, characterize all callback side effects, or measure faster asset loading. Neither successful frames nor the broad MP140-060 claim are established. No renderer callback or floating-point instruction was executed.

## Complete progress envelopes expose an additional return contract

The retained captures now cover both complete progress routines: original `00495230..004955fb`, Modern `00495230..0049559f` (exclusive ends after RET4). This expands the prior prefix evidence; it does not by itself qualify every drawing helper or indirect renderer callback. No whole-program absence of blocking work is claimed.

Modern's admitted tail at `00495589..00495594` clears EAX, loads the estimator result bits from local`-10h`, compares that DWORD with incoming stack DWORD`+1ch`, and SETE writes AL. It returns1 for **exact bit equality**, otherwise0. Earlier inactive/abort/negative-estimator gates return0. Treating this as floating numeric equality would change such cases as positive versus negative zero and NaN bit patterns. Those cases are interface consequences of integer CMP, not tested estimator outputs.

Original's tail instead performs FINIT, saves/changes the x87 control word through `0079f3ec/0079f3f4`, then restores its saved general registers and returns with RET4. It has no corresponding local SETE normalization. Its operation-dependent EAX must not be assigned Modern's completion-Boolean interface without checking callers. The original's control-state sequence is also part of its behavior; removing it as apparently redundant is not a bit-equivalent reconstruction.

The earlier throttle finding therefore has a second caller-visible difference: Modern reports whether its estimated output exactly matches the requested bits. Callers' dependence on that return, the purpose of the100%-specific repeated submission near `0049556f`, complete transitive timing and renderer effects remain separate questions. These are the appropriate next checks before attributing the whole loading-speed claim or proposing a replacement function.

## Terminal caller uses the new completion Boolean

The new return is consumed in the main loading sequence. Original `004a35b8` pushes100.0, calls progress at `004a35bd` once, then clears EAX and returns. Modern instead checks abort latch `0055e88c` at `004a3514`, pushes100.0 at `004a351d`, calls progress at `004a3522`, and repeats from the abort check when EAX is zero (`004a3527/29`). Thus this interface delta has a verified control-flow consumer, not merely an incidental changed return register. The audit asserts both call/return-use sequences.

For exact input bits100.0, estimator `00490143` bypasses the ordinary50-ms admission gate. It still applies the remaining-target and progress-smoothing calculation. The terminal loop can therefore keep requesting updates until the estimated float bits equal100.0 or the abort route wins. Earlier presentation calls with other percentages must not be assigned this same retry policy merely because they call the same function.

There is no explicit sleep, retry cap or independent timeout in this local loop. That does not establish a hang or a CPU-usage measurement: clock/input/renderer callees and state changes determine actual behavior. Likewise, a configured remaining target does not prove an exact wall-clock splash duration. Reachability with active flag0 or failed renderer preparation, transitive waits, cadence and visible completion remain runtime/interface follow-up questions. The bounded code difference is original's one-shot final update versus Modern's abort-aware completion retry.

## The inner100% resubmission is distinct from the outer retry

The audit now asserts Modern `0049556f..00495589` in full. When the estimated output bits equal100.0 and ESI is nonzero, this branch clears ESI, calls renderer slot `009ef948` with0, then jumps from `00495587` to `0049551d`. That target repeats the optional state changes, quad submission `004c12e0` and renderer-slot calls `009ef950/009ef940`. It does not repeat the timing estimator, input polling or preceding geometry construction. Original's tail has no corresponding backedge before its x87-control sequence.

This is separate from the outer `004a3529 ->004a3514` completion retry, which invokes the whole progress routine again. Locally, clearing ESI makes the inner tail repeat at most once **provided the intervening callees preserve ESI**; callback conformance remains an explicit interface requirement, not a proven property of every supplied driver. The earlier geometry stage uses ESI as a nonzero record pointer, rather than declaring an independent C Boolean loop variable. Calling this a guaranteed double-buffer refresh or exactly two displayed frames would infer a renderer purpose that has not been established. Preserve the two loop levels and register contract separately in reconstruction. No draw callback was executed.
