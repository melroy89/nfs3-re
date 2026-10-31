# Original versus Modern: indexed-texture loading progress

## Evidence boundary

Complete paired routine **`0041db10..0041dbb4`**, known in the saved analysis as `BuildIndexedShapeTexturesWithLoadingProgress`. Reproduce with `python3 analysis/scripts/audit_texture_progress_difference.py`; the [manifest](evidence/audits/original-modern-texture-progress.json) retains executable identities, both bodies, collection helpers and decoded constants. Baselines follow the [main comparison](original-modern-differences.md). Static only; no game, instruction probe or Ghidra write.

## Progress is redistributed

| Value | Original | Modern |
|---|---:|---:|
| Initial accumulator, immediate at `0041db27` | 43.0 | 14.0 |
| Fallback increment, immediate at `0041db20` | 15.0 | 81.0 |
| Budget constant at `00536d1c` | 15.0 | 81.0 |
| Nominal endpoint with N successful iterations, ignoring rounding | 58.0 | 95.0 |

Both first read collection count N through **`004ea654`**, which returns DWORD collection+8. If N is nonzero, the routine converts that signed32-bit count through `FILD`, computes budget/N using `FDIVR`, then stores the increment as binary32. With N=0, the fallback increment remains, but the loop’s signed count comparison normally exits before any progress update. A negative count also exits that comparison; this is not a validated collection invariant.

Each admitted texture route adds the increment to a binary32 accumulator, stores it back as binary32, and passes its bit pattern as one stack argument to **`00495230`**. The [loading-timing analysis](original-modern-loading-timing.md) explains Modern’s downstream throttling and estimation; the caller’s nominal progress is not proof of the displayed value or elapsed duration. Even with exactly N iterations, repeated binary32 rounding need not produce the ideal endpoint exactly.

The loop fetches each indexed entry with **`004ea658`**. That helper uses an unsigned index/count bound and adds the entry’s relative offset to the collection base; it returns0 when out of bounds. The caller’s zero-result branch skips texture creation, the accumulator update and the destination advance. A nonzero result takes one of the two texture preparation routes, then advances destination EDI by **`0x2c`**. The routine does not test those preparation helpers’ return value before advancing progress. Consequently “successful iteration” here means reaching this local update, not proven successful GPU upload.

After each update, nonzero **`0055e88c`** exits the loop. The per-iteration call to **`004a33d0`** also services the retained abort latch, but the caller does not immediately branch on it before entry lookup and texture processing. A zero-entry route jumps directly to the next index and bypasses this local post-update abort check. No additional validation, monotonicity guarantee or complete cancellation contract is inferred.

## Other changes and retained scope

The same function replaces original EBX=128 with the configured extent from **`007a278c`** before `004d4080`; this is already covered by the [texture-limit comparison](original-modern-texture-limits.md). Bit1 of `007a3a58` still selects alternate helper `004d41a0`. Its call route is retained, so configured extent does not govern every branch.

The progress loop is otherwise structurally retained. Modern uses a direct memory comparison for the post-update abort test, where original loads the flag into ECX first; incidental register outputs are therefore not assumed identical. ESI/EDI/EBP are restored by the routine. Complete transitive register contracts and renderer helper equivalence remain unresolved.

This establishes a local progress-allocation change alongside the known texture-limit change. It does not establish faster loading, a particular visible bar trajectory, successful allocation, or a unique release-note attribution. Follow-up should inspect the full loading-stage sequence before assigning meanings to the intervals43..58 and14..95.
