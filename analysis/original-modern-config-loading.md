# Original versus Modern: config.dat load acceptance and reset paths

## Evidence boundary

Static supplied-original/official-Modern comparison; exact executable identities are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_config_loading_difference.py`. The [manifest](evidence/audits/original-modern-config-loading.json) retains matched `00472980` bodies, original timestamp helpers, Modern header/sound-mode helpers, imported API identities and file-backed header bytes. No configuration file/API/game/instruction probes were executed.

This extends [resolution defaults](original-modern-resolution-defaults.md) and [ghost restoration](original-modern-ghost-loading.md). Configuration-header acceptance does not establish complete format compatibility.

## Retained file-load prefix, removed timestamp comparison

Both routines form a path with file-backed **`%sconfig.dat`** and prefix buffer `007a3034`, check the flag at `0055eb2e & 0x20`, check existence and request resource opening. They retain a local handle test and an exact **0x20f0-byte size comparison**. The flag is a load bypass in this path; its other producers/semantics are not inferred from an old command-line name.

Original additionally calls **`00472940`** when the size matches. It obtains time values for the config path and executable path (the latter from GetModuleFileNameA), then calls imported **CompareFileTime** with those two values. A return of -1 becomes helper result 1, which sends the caller to close/delete/reset; result zero allows the read path. The call, not a guessed function label, establishes this time-comparison gate.

Its time reader `004728e0` uses `_lopen`, GetFileTime's last-write output and `_lclose`, with a local zero-handle test and default time bytes. Complete failure semantics are not re-established here. In particular, do not promote this gate to a robust timestamp-validation mechanism without checking the legacy open/error contract.

Modern replaces the size-match timestamp call block with EAX=0 and a jump to the allocation/read path (`00472a22..00472a24`); mismatch still closes/deletes and goes to defaults. There is **no corresponding file-time check in this inspected Modern load path**. The old IAT address `0053448c` now names GetProcessHeap in Modern, so importing old API labels by address would be wrong.

Both allocate/read/copy/free in the remaining sequence. Their local caller does not branch on the read helper's return before copying; full allocation/read failure behavior and complete file-content validation remain outside this chapter.

## Modern header decision tree

After loading, Modern tests globals at `00472aac..00472aea`:

| Condition | Modern action |
|---|---|
| DWORD `006fbb40` differs from **0x20f0** | Call full defaults `00472404`, then header refresh and grouped default helpers |
| Size matches, byte `006fbb45` nonzero | Keep the existing block initially, then refresh header and grouped defaults |
| Size matches, high byte zero, byte `006fbb44` < **6** | Same grouped reset route |
| Size matches, high byte zero, low byte ≥ **6** | Call `00472230`, skip grouped defaults |

Grouped reset route calls header refresh `004723f0`, display defaults `00472d10`, HUD defaults `00485880`, `00472298` and `00472248`. Some fields outside these helpers may remain loaded on the version-only reset route. It is not automatically equivalent to a complete configuration reset.

The accepted version check is a **WORD interpreted as separate bytes**, not an exact DWORD equality against 6. Ordinary values 6..255 with zero high byte follow the accepted route; the code does not reject all unknown future versions. Higher header fields are not validated by these tests.

`00472230` only checks sound mode `006fbc00==3`; if capability helper `0040faf0` returns zero, it writes zero there. This is a narrow normalization step, not a full migration/validation of every serialized setting.

## Header producer and original reset behavior

Modern file-backed prefix `0055e8a0` contains bytes **`f0200000 06000000 00000000`**. `004723f0` copies those three DWORDs into `006fbb40`; effective values depend on any earlier source writes, which are not excluded here. This establishes the ordinary header template as size 0x20f0, next DWORD 6, then zero. **6 is not the Modern Patch release version.**

Original `004723f0` is a much larger defaults routine, not the same 18-byte header helper. Its file-backed bytes at `0055e8a0` are zero, so those source bytes must not be treated as a matching original template. Original load paths use the larger routine when no file opens or a size/time check fails, also set `0067900c`, and later compare loaded size and renderer type against current `007a3a58`. Modern replaces that sequence with the explicit size/version branching above.

This explains why the ghost wrapper's restored header matters: a ghost-supplied size/version prefix could otherwise route subsequent config loading into default initialization. It does not prove the exact contents or behavior of every original/patch-release ghost file.

## Remaining work

Verified: removed timestamp gate, retained size gate, Modern version-byte decisions and default-helper routing, and the header template/producer. Pending: all field layouts/packing, complete original default implementation, save-file semantics, read/open failures, source-template writes and cross-release compatibility. The [CPU](original-modern-cpu-tier.md), [HUD](original-modern-hud-layout.md) and resolution chapters explain selected reset consumers; they do not make this a complete serialization specification.
