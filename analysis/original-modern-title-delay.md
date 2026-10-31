# Original versus Modern: configured title-splash delay

## Evidence boundary

Static paired comparison of **`00472fc0`**, original end `0047300d`, Modern end `00473016`. Reproduce with `python3 analysis/scripts/audit_title_delay_difference.py`; the [manifest](evidence/audits/original-modern-title-delay.json) retains both bodies, draw/input/service witnesses and direct callers. Baselines follow the [main comparison](original-modern-differences.md). No title rendering, input, delay measurement, target instructions or Ghidra writes.

## Original accumulated library-clock threshold

Original conditionally calls title drawing `00472f20` only when `006fbb54 == 0`. It calls `004f0650` once, drains input through `00451940(EAX=0)`, initializes EDX=0, then loops over filtered input `00451960(EAX=1)`, service helper `004c9860`, and further clock-delta calls.

`004f0650` saves/restores EDX, reads old global timestamp `005651dc`, calls `004f0630`, replaces the timestamp and returns the wrapping difference. The wait accumulates these returned deltas in EDX and compares signed against **384 (`180h`)**. At exactly384, a final input poll occurs before the pre-service `JGE` exits. This chapter does not assign seconds to the underlying library clock or claim that this threshold equals a particular measured wall-clock duration.

## Modern configuration, clamp and elapsed milliseconds

The [settings-loader analysis](original-modern-startup-policy.md#3-current-settings-exact-defaults-and-immediate-effects) establishes **`IntroSplashTime`**, fallback0, stored raw at `007a279c`. The consumer now:

1. Loads the setting and clamps it with signed comparisons to **0..10**.
2. For zero, returns immediately: no draw, input drain or service loop in this helper.
3. For positive values, computes EDX=`seconds*1000`, reads start time from `004f2790` into EBX, draws through `00472f20`, and drains input with `00451940(EAX=0)`.
4. Polls filtered input with EAX=1; a nonzero result exits early.
5. Otherwise calls `004c9860`, reads the clock again, and repeats while **unsigned wrapping elapsed `< duration`**.

The [clock-source audit](original-modern-clock-source.md) verifies that Modern `004f2790` calls timeGetTime and preserves ECX/EDX, establishing milliseconds here. The maximum multiplication is10000, so the shown clamped duration does not overflow32 bits. Startup rendering and input draining occur after the initial clock read and count toward elapsed time. The loop may exceed the requested duration because it checks only after polling/service work; it does not promise precise scheduling or sleep for the full configured duration.

The helper uses EDX as the live duration across calls, with Watcom-style register preservation rather than an ordinary assumed C caller-clobber contract. The retained draw routine saves EDX; the input poller and clock preserve it, while the service wrapper delegates to further callees. Complete transitive preservation, callbacks and nonlocal exits remain separate reconstruction concerns; this chapter does not claim a full service ABI audit. EAX on return is path-dependent; no success-return interface is inferred.

## Call placement and scope of the claim

The retained Modern caller witness **`00473152..00473160`** checks `0055b03c != 0`, calls this helper at `0047315b`, then continues. Original direct calls are retained at `00473181` and subsystem setup `004b61a6`; the latter original caller belongs to the broader setup counterpart already compared elsewhere. Bounded direct-call locators do not prove all possible indirect entry paths or whole-startup equivalence.

Modern’s helper no longer contains original’s `006fbb54` draw suppression; it gates all its work on the configured duration instead. The [movie startup comparison](original-modern-idle-movie.md) separately handles title-movie availability. **A title-splash wait and movie admission are distinct policies**: zero delay here does not by itself prove the title movie is disabled.

**MP150-032:** partial static support for the configuration producer,0..10 consumer clamp, zero-skip behavior and millisecond elapsed loop. Actual display duration, title visibility, callback timing, input behavior and historical introduction remain unverified. No timing or instruction probes were run.
