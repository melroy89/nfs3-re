# Original versus official Modern: RAM pool size configuration

## Scope and artifacts

Static comparison of the supplied original executable with the official archive Modern executable, limited to the startup RAM pool backing allocation and its size source. It does not measure process memory use or establish that allocation/pool creation succeeds at runtime.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.

## Modern size source and clamp

`LoadGameIniSettings` at `004b5580` reads integer setting key `OwnHeapLimitMb` from the constant at `0053f63c`, with caller default 32 (`EDX=0x20`) through `004fb6f0` (`004b55e6–004b55f5`). It clamps values below 16 to 16 (`004b55f5–004b55ff`) and values at or above 512 to 512 (`004b55ff–004b560b`), shifts the result left 20 bits, and stores the byte count at `007a2760` (`004b560b–004b560e`). The resulting configured range is 16–512 MiB, default 32 MiB. The existing configuration audit documents the INI/environment/caller-default precedence for this reader; here the evidence establishes the key's caller default and the resulting clamp.

Modern startup calls `InitializeRamPoolFromConfiguredByteCount` at `004f92d0` from `InitializeGameSubsystems` at `004b5c11`. The entry loads `007a2760` (`004f92d1`), clears EDX, and forwards the byte count to `004f92b0` (`004f92d6–004f92dd`). That adapter calls `AllocateRuntimeHeapBytes` at `004f7900`, publishes the returned pointer at `005644fc`, preserves the original count in EDX, and calls `InitializeRamMemoryPoolWithCallback` at `004f9270` (`004f92b0–004f92c5`). The pool initializer calls `CreateMemoryPool` at `004e1230` with EAX=0, EBX=buffer pointer, ECX=byte count, EDX=literal `RAM`, and stack arguments 8, 32, 16, 1, 1, 1, 1, and callback `004f9260` (`004f9270–004f92a3`). The meanings of these pool parameters beyond their passed values remain outside this comparison.

## Original fixed-size path

The original has the same allocation adapter at `004f92b0` and pool initializer at `004f9270`; the initializer passes literal name `RAM` from a different data address. But original entry `004f92d0` does not load a setting: it puts immediate `0x01000000` in EAX (16 MiB), clears EDX, and calls `004f92b0` (`004f92d0–004f92de`). The original caller at `004f8939..004f8945` tests backing pointer `005644fc` for zero and jumps to the allocation call at `004f8a73` when it is null; afterward it jumps back to `004f8946`. The nearby `00564364` checks control a different branch and must not be mistaken for the allocation guard. Modern's caller is instead `004b5c11` in `InitializeGameSubsystems`, after the resource/display check call at `004b5c0c`; the earlier application settings-loader call is `004a3e4e`.

Thus this path changes from a conditional fixed 16 MiB request in the original to the Modern INI/environment-derived, clamped 16–512 MiB request (32 MiB default). This identifies the local null-pointer guard, without proving every initialization/reinitialization sequence.

## Retained evidence and reproduction

Run `python3 analysis/scripts/audit_startup_policy_difference.py` (Python `pefile`, GNU `objdump`). The [startup/heap manifest](evidence/audits/original-modern-startup-policy.json) records input hashes, original caller and pool/allocator instruction spans, Modern configuration and startup callsites. Raw assembly remains under ignored `analysis/captures/modern-differences/startup-policy/`. Allocator body `004f7900..004f79ec` is compared byte-for-byte; unchanged instructions alone do not establish unchanged indirect callback targets.

## Allocator comparison and limits

The instruction sequence for `004f92b0` is the same in both inspected files: request a block from `004f7900`, save its pointer at `005644fc`, then pass pointer and byte count to `004f9270`. The body at `004f7900` is byte/instruction-identical across these baselines in the inspected range and uses the same indirect allocator callback slots; their stored targets and allocator state are not proven equivalent. Both then call the same `CreateMemoryPool` routine at `004e1230`. No direct allocator API substitution is visible in this RAM pool path; broader import-table changes are not attributed here to this allocation without a caller-level link.

The allocator adapter does not locally test the returned pointer before publishing it or initializing the pool. This report does not infer success, pool capacity, later RAM-pool use, practical safe maxima, or memory pressure from the configured range. No executable or Ghidra project was modified; no game or probe was run.

## Separate render scratch arena grows to8 MiB

The [arena audit](evidence/audits/render-arena-difference.json), reproduced by `python3 analysis/scripts/audit_render_arena_difference.py`, compares complete initializer **original`004bbd80..004bbdbc`**, **Modern`004bbd80..004bbda4`**, and free counterparts **original`004bbdc0..004bbdd9`**, **Modern`004bbda4..004bbdb6`**. This is a separate render arena from the RAM pool discussed above.

Original helper`004b56e0` writes requested size **`0c3400h` (799,744 bytes)** through its output pointer and calls pool allocator`004e1620`. The initializer publishes base`0055fe34`, rounds base+31 down to a32-byte boundary for cursor`0055fe38`, and subtracts100 from capacity`007a3d04`.

Modern requests **`800000h` (8,388,608 bytes /8 MiB)** through`004f1efc`, whose imported target is **HeapAlloc**, flags0 and heap handle from`009f3d40`. It publishes the same base/cursor cells, uses equivalent low-five-bit alignment, and explicitly sets capacity **`7fff9ch`**, i.e.8 MiB−100. The request is fixed here; it is not the configurable `OwnHeapLimitMb` RAM-pool size. No null-result guard precedes publication/alignment/capacity setup in either inspected initializer.

Original free conditionally calls`004e1890` through`004b5700`, then clears the base cell. Modern uses XCHG to set the base cell to0 first, tests the extracted pointer and calls the **HeapFree** adapter`004f1f30` when nonzero. That adapter uses flags0 and the same heap-handle cell. The XCHG changes clear/free ordering; it does not synchronize outstanding arena consumers or establish safe concurrent teardown.

The existing [scratch consumer analysis](original-modern-night-lighting.md#scratch-sizing-and-preserved-allocation-limitation) documents the retained bump helper and its update-before-failure limitation. This backing-size evidence narrows its former capacity unknown, without proving every caller's request fits or allocation succeeds. The retained reset`004bbd70` copies raw base to cursor, whereas initialization writes the aligned cursor; preserve that observed distinction instead of silently adding alignment to reset. Live allocator alignment, lifetime/reset ordering and actual utilization remain unverified. No allocator, arena reset or game code was executed.

The catalog claim **MP150-010** names a `Render_GetTm()` high-poly-car error. The arena growth above is related research, but this comparison has not connected that named error to this allocation or demonstrated its elimination. The catalog therefore retains vendor-only status; larger capacity alone is insufficient to verify the claimed fix.
