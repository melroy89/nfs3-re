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

## Original clock follow-up: shared counter and requested rate

The expanded audit retains original reader **`004f0630..004f0636`**, reset **`004f0670..004f068a`**, worker **`0048eb90..0048ec3d`**, timer-initialization prefix **`0048eff0..0048f109`**, and startup witness **`004b6155..004b6165`**. These are original-only producer witnesses, not claims of whole timer-subsystem equivalence with Modern.

`004f0630` is simply **`MOV EAX,[0079c1a4]; RET`**. Reset clears that shared counter and copies its value to delta-history/deadline globals `005651dc/d8`. The title delta helper therefore measures changes in the same counter used by the [idle movie controller](original-modern-idle-movie.md), rather than directly reading a millisecond API on each call.

At `004b6155`, original subsystem startup supplies **EAX=128** to `0048eff0` at `004b6160`. The initializer accepts signed positive inputs1..10000, otherwise substitutes100; computes **`(1000<<16)/rate`** into `0079c170`; clears the shared counter; and begins timer/worker setup. This establishes a requested rate and a fixed-point period calculation. The retained prefix includes multiple failure branches that clear active/rate state, so a supplied128 must not be described as unconditional successful128-Hz operation.

Worker `0048eb90` creates/stores an event-like wait object through `004dfb00`, waits through `004dfb70`, then—while state `0079c19c` remains nonzero—increments **`0079c1a4` once** at `0048ebd8`. It also updates another counter, samples GetTickCount and services up to eight registered callbacks before waiting again. When the state clears it closes/releases its wait object through a separate helper and returns. This is a logical worker-step counter; elapsed milliseconds are sampled separately.

**Inference, explicitly conditional:** if the requested128 rate is realized as128 counter increments per second,384 ticks correspond nominally to3 seconds, and5120 ticks to40 seconds. This is not an established wall-clock guarantee: complete event production/coalescing, failure handling, reinitialization (including renderer-side calls), scheduler delays, resets and all counter writers remain to be qualified. The earlier decision not to label the original threshold as a measured three-second wait therefore stands.

For reconstruction, keep this logical counter distinct from Modern’s direct millisecond duration. Substituting the same integer384 into a millisecond timeout would not preserve the demonstrated clock contract. No timer, event, sleep, game or instruction probe was executed.
