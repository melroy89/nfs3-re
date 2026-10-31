# Original versus Modern: renderer state14 setter policy

## Evidence boundary

Paired setter **`00470ad0`**, original ending at exclusive`00470b1e`, Modern at`00470afa`; retained helpers **`00470b20..00470b6a`** and **`00470b90..00470bb8`**. Reproduce with `python3 analysis/scripts/audit_state14_difference.py`; the [manifest](evidence/audits/original-modern-state14.json) binds both executable identities, complete bodies and helper equality. See the [baseline](original-modern-differences.md). No target instructions, driver calls or Ghidra writes.

## Enabled input zero changes meaning

Both use DWORD **`007a3a64`** as an admission flag and cache the incoming EAX at **`00678b40`** when enabled. Original treats input0 specially: it passes EDX0 with EAX14 to state setter `00431900`. For nonzero input it forms signed32-bit `100-input`, clamps that signed result to1..100 and multiplies by5 before passing it in EDX.

Modern delegates to the existing scaled helper **`00470b20`**, setting incoming EDX=1. That helper performs the same complement/clamp/multiply policy but has **no input-zero exception**. Thus ordinary examples are:

| Input EAX | Original state14 value | Modern state14 value |
|---:|---:|---:|
| 0 | 0 | 500 |
| 1 | 495 | 495 |
| 50 | 250 | 250 |
| 100 | 5 | 5 |
| 101 | 5 | 5 |
| −1 | 500 | 500 |

These are instruction-derived examples, not executed probes. Arbitrary values require the actual wrapping SUB and signed comparisons; an unbounded mathematical clamp is not a complete C contract. The scaled helper additionally multiplies by its caller-supplied factor modulo32 bits, but this Modern wrapper supplies exactly1.

## Disabled path can now clear stale cached state

Original returns without a state call or cache reset when `007a3a64==0`. Modern instead checks **`00678b40`**: if it is−1, return; otherwise call reset helper **`00470b90`**. That helper is byte-identical in this pair: it writes−1 to `00678b40`, zero to **`00678b44`**, and invokes `00431900` with EAX14/EDX0.

The change therefore combines removal of a zero-input exception with conditional cleanup on disabled admission. It does not prove the feature’s high-level name, the backend interpretation of value500 versus0, or that every driver accepts this state. The [renderer initialization comparison](original-modern-renderer-initialization.md) already warns that enable/global roles and initialization stores can differ across versions; this local flag use must not be mistaken for equivalent whole-game initialization.

Original saves/restores EDX/EBP directly. Modern explicitly saves EDX around its enabled helper call; the reset helper saves ECX/EDX/EBP. Full transitive ABI, state-cache behavior inside `00431900`, all callers and enable-flag writers remain follow-up work. No normalized EAX status return is assigned to this setter.

## Retained setter cache qualifies driver dispatch

The expanded audit verifies complete **`00431900..00431a99`** is byte-identical in both baselines. For selector14 it compares incoming EDX with cache **`00554e68`** at `004319b0`. Equal values skip the renderer callback and return the initially selected EAX result1. Unequal values update that cache **before** calling slot **`009ef96c`** with stack pair `(14,value)`. Existing [renderer export binding](original-modern-renderer-loading.md) identifies that slot as `_THRASH_setstate@8`; this is a proven binding, not a name found only in strings.

After the state14 callback, it saves that result in EBX and reads **`00554e5c`**. If that value is signed nonnegative, it calls the same slot again with `(21,cachedValue)`. It ultimately returns the first callback’s result rather than the reapplication result. A signed-negative cache skips the second call. Complete meaning and writers of state21’s cache remain outside this finding.

Consequently the earlier0-versus500 difference is a **requested state-value** difference. Whether a driver call occurs also depends on prior cached state. The cache update is not rolled back on a failing callback in this local body; a later equal request can take the return1 fast path without retrying. No actual renderer failure is asserted, and the callback’s complete status conventions remain unresolved.

Disabled-state cleanup likewise requests state14 value0 through this cache, so it need not invoke the driver when0 is already cached. Separate local cells `00678b40/44` are still reset by `00470b90`. This distinction matters for reconstruction: local cached-input cleanup, state-cache equality and renderer acceptance are three different events.
