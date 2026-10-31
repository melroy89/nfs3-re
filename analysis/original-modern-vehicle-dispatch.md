# Original versus Modern: race-vehicle render dispatch

## Evidence and correspondence

**Static comparison; no game, instruction or rendering tests.** The supplied original and official Modern v1.6.1 fingerprints are retained by [the manifest](evidence/audits/original-modern-vehicle-dispatch.json). Reproduce using `python3 analysis/scripts/audit_vehicle_dispatch_difference.py` (pefile and GNU objdump). Complete dispatcher spans are original `004bbba0..004bbcb4` and Modern `004bbba0..004bbce3`, with exclusive ends. Their shared participant arrays, field accesses, ordered callees and tail establish correspondence beyond merely occupying the same address.

Existing research names this routine `UpdateAndDispatchRaceVehicleRenderStates`; see [detailed notes](detailed-analysis-notes.md), including `SnapshotRaceSimulationTick` and `RandomizeSelectedVehicleOffsetUnlessTickMatches`. The current audit compares the paired instructions; existing names do not establish the complete structures or all render effects.

## 1. Retained two-pass organization

Both versions iterate signed count `005efd9c` over pointers at `005efac8 + 4*i`. The first pass clears object DWORD `+0x8b8`, passes its address in EBX, the object in EDX and incoming context in EAX to `004bb5d0`, and stores EAX at object `+0x8b4`.

The second pass skips objects whose signed `+0x8b4 <= -1`. If both `+0x8e4` and `+0x8e8` are nonzero, it calls `004b9bc0`. Further processing requires byte `+0x89 != 0` and byte `+0x88 == 0`. Eligible objects may then reach `004bb4c0`, with object in EAX and the incoming context in EDX. Field labels remain opaque where their full producers and consumers are not established.

The tails retain the `0055d000 == 1` gate and call `004b9df0` with the indexed pointer from `005efa48 + 4*[006fd4f4]`, then call `004c9f70` with the context. Existing research identifies playback-pose and spike-strip rendering, respectively; this audit does not establish their complete internals or visible output.

## 2. An unconditional selection helper becomes conditional

Original always calls `004bbad0` between the two passes (`004bbbdf`). Modern calls it at `004bbc04` only if:

`([context + 0] == 1 AND [006fd1d8] != 0) OR [006fbc1c] != 0`.

This is the exact branch condition; assigning the unnamed context/global combination a complete gameplay mode is unresolved. Both binaries' complete helper body `004bbad0..004bbb94` is byte-identical (196 bytes). The helper reads `006fbc1c`, calls `004bba10` / `004bba50`, and can rewrite participant `+0x8b4`. Thus the change is an admission policy around retained selection work, not evidence that the selection helper itself was rewritten. Whether any particular object is rendered differently requires its input state and the downstream paths.

## 3. Tick snapshot and parity bookkeeping change

Existing simulation research identifies `007d3684` as the race tick and `0055fe28` as its snapshot. At entry Modern saves both DWORDs to locals, using those saved values for the following per-object comparisons. Original rereads the live race-tick global within the object loop.

Original, after the byte gates above:

- Only when object `+0x174 != 0`, compare current tick with object `+0x8c0`; increment DWORD `+0x8bc` if unequal.
- Write current tick to `+0x8c0` before the optional dispatch.
- If the low bit of `+0x8bc` is set and `007d36a0 == 0`, skip `004bb4c0`; otherwise call it. When `+0x174 == 0`, bypass this bookkeeping and call directly.
- At the end of the whole routine, copy live `007d3684` to snapshot `0055fe28` (`004bbca3..004bbca8`).

Modern, after the same byte gates:

- Compute wrapped 32-bit `snapshot - object[+0x8c0]`, then the x86 signed-magnitude sequence `CDQ; XOR; SUB`. Compare that result **unsigned** against 16. If greater, reset `+0x8c0` to the entry snapshot (`004bbc5a..004bbc72`). This normalization runs even when `+0x174 == 0`.
- If `+0x174 != 0`, compare the saved current tick to the possibly reset field and increment `+0x8bc` if unequal. Retain the same low-bit / `007d36a0` dispatch gate.
- Whether the parity gate dispatches or skips, write the saved current tick to `+0x8c0` afterward (`004bbcad..004bbcb0`). Objects excluded by the earlier eligibility/byte gates bypass this write.
- Remove the original tail's write to global snapshot `0055fe28`. This does not prove the snapshot stops updating: existing research records other writers, including the dedicated snapshot helper.

The point of the `+0x8c0` write matters to callees that inspect it. Original updates it before `004bb4c0` for nonzero `+0x174`; Modern updates it after that call and also for zero `+0x174`. Existing `RandomizeSelectedVehicleOffsetUnlessTickMatches` research is a reason to trace those downstream dependencies, not sufficient evidence of the resulting visual effect. Full callee reachability and ordering remain pending.

The magnitude sequence must not be casually translated to C `abs(int)` or signed subtraction: x86 wraps, and input difference `80000000` remains that bit pattern after negation, so the unsigned `>16` branch is taken. C signed overflow and `abs(INT_MIN)` do not provide that contract. DWORD counter increment also wraps; only its low bit is tested locally.

## 4. Register contract and limits

Original's final `MOV EAX,[007d3684]` leaves that value in EAX while restoring EBX/ECX/EDX/ESI/EDI/EBP. Modern uses PUSHAD/POPAD and restores incoming EAX as well as the other general registers. This is a concrete machine-state difference, not proof that callers consume a scalar return. Flags are not preserved by either prologue/epilogue scheme; no flags-output contract is established here.

**Verified:** paired loop correspondence, conditional helper admission, identical helper bytes, tick/parity writes and general-register difference. **Inferred:** these changes alter render-state scheduling rather than physical integration; no physics-equivalence claim follows. **Unresolved:** mode/global meanings, all callees and callers, visual effects, original bug intent, exact historical release attribution and runtime behavior. No release-note row is promoted to verified based solely on a similar description of wheels or detail settings.

Next: trace `004bb4c0` and its tick-sensitive callees against the original, then connect the admission globals to their actual configuration/mode producers. Preserve raw exports, executable bytes and saved Ghidra state.
