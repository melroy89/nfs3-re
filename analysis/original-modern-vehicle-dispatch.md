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

Next: connect the admission globals to their actual configuration/mode producers and trace remaining tick-sensitive callers. The downstream dispatcher/randomizer comparison is now documented below. Preserve raw exports, executable bytes and saved Ghidra state.

## 5. Downstream comparison: global gate becomes per-object gate

The evidence script now retains and asserts byte identity of three complete bodies:

| Entry | Exclusive end | Existing research name |
|---|---|---|
| `004bb4c0` | `004bb5ce` | `DispatchVehicleFceRenderVariant` |
| `004bae00` | `004bb10f` | `RenderVehicleBodyAndUnmaskedWheelParts` |
| `004bb200` | `004bb495` | `ProcessVehicleFcePartsZeroThroughFour` |

The two four-entry jump tables at `004bb498..004bb4b8` are also identical. Existing [detailed notes](detailed-analysis-notes.md#vehicle-fce-render-variant-dispatch-004bb4c0) describe model-count downgrades and selector targets; the current comparison verifies that this dispatch code and table mapping remain, rather than attributing a same-address byte difference elsewhere to a changed dispatch algorithm.

Both render bodies call `004b90e0` twice: `004baf59` / `004bb01f` and `004bb330` / `004bb3c9`. Existing call-site research establishes zero/nonzero EDX choosing the two object float fields `+0x93c` / `+0x940`. The complete helper `004b90e0..004b913f` differs in **only four bytes**, `004b90e8..004b90eb`, changing the operand encoding of its first load:

| Version | Instruction at `004b90e7` | Equality gate at `004b90ed..004b90f3` |
|---|---|---|
| Original | `MOV EBX,[0055fe28]` | Global snapshot equals current `007d3684`: skip random generation and output write. |
| Modern | `MOV EBX,[EAX+000008c0]` | This object's saved tick equals current `007d3684`: skip random generation and output write. |

The rest of the helper is byte-identical. On an admitted call, it calls `004eb230`, multiplies the returned ST0 by binary32 object field `+0x930`, subtracts `object[+0x930] * 0.5`, and stores binary32 into the EDX-selected destination. It does not write `+0x8c0` or `0055fe28`. The numerical sequence and RNG call target are retained; identical instructions do not establish identical results under different x87 control state or RNG history. See the separate precision audit linked from the main index.

This clarifies the caller change in section 3. Original tests a shared snapshot, independent of the particular object's `+0x8c0`. Modern's object field is written **after** `004bb4c0` returns, allowing the render calls to see its earlier value. In the old ordering, that field was written before dispatch for nonzero `+0x174`; carrying that old ordering into a Modern reconstruction would alter the new helper's equality gate.

This is still not proof of exactly one random sample per object per tick. The helper never updates the gate field itself; the two calls inside a render body can both pass before the enclosing dispatcher writes it. Calls outside that enclosing path, objects skipped by its gates, tick changes and replay resets require separate tracing. Likewise this code-level difference can change RNG consumption when the two gates disagree, but does not establish that the RNG state affects physics, that network positions diverge, or that a particular release-note claim about wheel rotation is explained completely.

**Closed for this bounded follow-up:** downstream dispatch correspondence, two retained render bodies/tables, exact randomizer operand delta and its relationship to caller write ordering. **Still pending:** remaining callers, admission-global meanings, RNG-state sharing, visual validation and historical attribution.

## 6. Admission-global producers: defaults are not immutable settings

Modern default initializer `00472d10` supplies both globals used by the new selection-helper admission gate. The [CPU-tier comparison](original-modern-cpu-tier.md) establishes its index: unsigned score `005652a4` is capped at 5, then halved if renderer mask `007a3a58 & 6` is nonzero. The initializer reads byte tables and zero-extends each element:

| Effective tier index | `006fbc1c` from table `00472e2c` | `006fd1d8` from table `00472e4a` | Resulting admission to `004bbad0` under these values |
|---:|---:|---:|---|
| 0 | 2 | 2 | Always |
| 1 | 2 | 2 | Always |
| 2 | 1 | 2 | Always |
| 3 | 1 | 2 | Always |
| 4 | 0 | 1 | Only when context DWORD0 equals 1 |
| 5 | 0 | 0 | Never |

The writes occur at `00472d4d` and `00472e09`. This table evaluates the dispatcher's literal predicate using those defaults; it is not a claim that a user-selected configuration, race or renderer necessarily retains them. In particular, `006fd1d8` takes value 2 in the table, so replacing it with a boolean in maintained data would lose observed state even though this dispatcher only tests zero/nonzero.

A separate initialization block writes zero to `006fbc1c` at `00472672`. Existing config-load research also establishes bulk config restoration. Modern helper `0043778c` can restore `006fd1d8` from temporary `00664688` when token matcher `004429c0` returns nonzero. It also copies `00664684` to `006fd1d4`; on a matcher miss that second copy occurs only when fog gate `007a3a54` is zero. Adjacent menu code uses the literal tokens `GRAPH_FOG` and `GRAPH_FOG_CASCADE`, but those strings alone do not establish that `006fd1d8` is simply a named fog boolean or that context DWORD0 identifies a particular viewport. The whole option binding must be followed before assigning that semantic label.

**Verified:** two direct default producers, exact six-entry tables, zero initialization and conditional restore producer. **Still unresolved:** complete UI binding and context meaning, indirect/bulk writes beyond the existing config evidence, all original default counterparts and actual runtime values. This narrows the unknowns without converting a default table into a universal renderer policy. The script retains the Modern-specific producer spans; original bytes at those reused addresses are not presented as automatically corresponding functions.

## 7. Shared RNG: algorithm retained, consumption can change

The downstream fraction helper `004eb230..004eb257` calls the same generator `004e0d88`, masks EAX to 16 bits, zero-extends into a temporary 64-bit integer, loads it with FILD, and multiplies by binary64 constant `0054b734` = **1/65536**. Its result is ST0 in `[0, 65535/65536]`; EAX/EDX are saved/restored. This fraction construction uses exactly representable binary values, but later object scaling/subtraction still depends on floating-point state and operands.

The evidence script now verifies these complete bodies are identical in original and Modern:

| Entry | Exclusive end | Function |
|---|---|---|
| `004e0d88` | `004e0dee` | Shared six-word generator |
| `004e0dee` | `004e0e2b` | Seed-to-six-word initializer |
| `004eb230` | `004eb257` | Low-16-bit fraction wrapper |

The generator reads/writes shared DWORDs `005644e0..005644f4`, using an ADD/ADC chain and increment cascade, then stores/returns word0. The seed initializer takes incoming EAX, cumulatively adds literals `f22d0e56`, `96041893`, `3df3b646`, `40dde76d`, `97327ae1`, `d1a9fbe7`, and stores each intermediate DWORD to the corresponding state word. Arithmetic is modulo 2^32. It does not establish a particular generator family or mathematical quality.

Both files contain the same initial state bytes:

`560e2df2 e9263188 2fdd24c6 9cc40207 7d3f359e 643bdf6f`

These groups are **bytes in file order**, not printed numeric DWORD values. They match the initializer's cumulative additions from seed zero, but their presence does not prove the runtime seed is zero. Runtime seed calls can overwrite them; existing race/roster/configuration research records such callers. The binary64 fraction-scale bytes also match (`000000000000f03e`).

The render randomizer contains no private seed, snapshot or restore. Each admitted call reaches this shared generator once, so a difference in the gate can alter the next shared state even though the generator algorithm and initial file bytes are unchanged. Existing [music-selection comparison](original-modern-music-selection.md) establishes another consumer of `004e0d88`; the sky-grid/shared-RNG sections of [detailed notes](detailed-analysis-notes.md) establish additional use and seed-order limitations. The exact cross-subsystem call order, intervening reseeding, threading and dependency on simulation outcomes are not established here.

**Result:** shared-state ownership is confirmed; render-gate differences can change shared RNG consumption under inputs where the gates disagree. **Not established:** a particular replay divergence, multiplayer desynchronization, physical trajectory change or historical patch regression. Those claims require traced state consumers and controlled runtime comparisons, not just a changed random call count.
