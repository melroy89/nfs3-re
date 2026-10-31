# Original versus Modern: night vehicle lighting admission

## Evidence boundary

Paired full body **`0041c670..0041c9e4`**,884 bytes, identified in existing project research as `ApplyNightVehicleLightingToTrackBlockQuads`. Reproduce with `python3 analysis/scripts/audit_night_lighting_difference.py`; the [manifest](evidence/audits/original-modern-night-lighting.json) retains both counterparts, unchanged prefix/tail, caller and complete scratch-arena helper. Baselines follow the [main comparison](original-modern-differences.md). No night race, graphics, instruction probes or Ghidra writes.

## Context admission changes; downstream instructions remain

| Condition | Original | Modern |
|---|---|---|
| Context DWORD0==1 | Return0 immediately | Continue only if unsigned `006fd1d8 <= 1` |
| Context DWORD0!=1 | Continue | Continue |
| After context admission, `006fd4c8==0` | Return0 | Return0 |
| Otherwise | Request scratch storage, then process lighting | Same downstream body |

The changed Modern predicate is at **`0041c687..0041c699`**. The unsigned `JA` matters: values0/1 admit context1,2 and larger reject, and a bit pattern representing a negative signed integer also rejects. This global is demonstrably multi-valued in the [existing default-setting analysis](original-modern-vehicle-dispatch.md); do not reduce it to a Boolean.

All changed bytes are inside **`0041c684..0041c6cc`**. The complete tail **`0041c6cc..0041c9e4`** is byte-identical, so this is an expanded entry-admission policy, not an identified rewrite of the retained lighting arithmetic. The retained body includes vehicle/resource filtering, transforms and helper submissions already investigated in [detailed notes](detailed-analysis-notes.md#night-vehicle-lighting-over-track-block-quads). Equal local instructions do not establish equal floating-point state, global inputs, called helpers or rendered output.

The context’s first DWORD remains an unnamed tag. The option-binding follow-up below identifies Modern `006fd1d8` as Rear View Detail. **MP150-002** mentions headlights in the rear-view mirror, but this gate alone does not prove context1 is that viewport or explain clouds/lightnings also bundled in the claim. No catalog promotion is made on that inference.

## Scratch sizing and preserved allocation limitation

Original forms **28*incoming EDX modulo2^32** through shifts/subtraction. Modern uses unsigned `MUL` by28, then copies the low product into EDX. Both pass a local output-pointer cell in EAX to **`004bbde0`**. Discarding the high product preserves the requested low32-bit size; this is not an added multiplication-overflow guard.

The complete arena helper **`004bbde0..004bbe3a`** is byte-identical. It writes the current cursor to the supplied output cell, advances and rounds the stored cursor to a32-byte boundary, then compares consumption against its capacity state. On the diagnostic/failure path it returns0 after updating those cells; this is not an ordinary allocator that leaves output null and state unchanged on failure.

The lighting caller subsequently tests the **output pointer**, not the helper’s Boolean EAX. That retained limitation must not silently become an invented checked-allocation contract in reconstructed C. Capacity, pointer validity, arena lifetime and out-of-range count behavior remain unresolved; no malformed input was executed.

## Calling boundary and result

The paired direct caller witness **`0041d04e..0041d06d`** pushes four stack values, supplies context in EAX, the sizing/count input in EDX, block/index input in EBX and another selector in ECX, then calls at `0041d068`. Callee ends with **RET16** and preserves ESI/EDI/EBP; other register preservation is not guessed from a normal platform ABI. Full pointer types and units require the existing caller/layout research to be completed.

The local accumulator starts0 and sums retained submission-helper results, returning it in EAX at `0041c9d9`. It is not established as a count of visible or successfully drawn primitives. Both rejection paths return0. Modern’s entry gate can therefore expose an existing body to additional contexts without proving correct output for those contexts.

Next: trace context1 construction, then compare any changed helper reached only by the newly admitted cases. Keep mirror attribution, x87/numeric behavior, allocation contracts and runtime visual acceptance separate.

## Modern option binding: Rear View Detail values0..2

The expanded manifest retains Modern20-byte descriptor **`00556564`**: name pointer `00537720` (`mirrorlevel`), WORD-list pointer **`0055623a`**, two zero fields and selector storage **`006fd1d8`**. The list is **187,186,185,0**. The hash-pinned official English resource decodes those IDs as **High, Medium, Low**, respectively; no labels are inferred from their numeric magnitude.

Official `graphics.mnu` binds both an arrow-tab control and a cascade to `listname=mirrorlevel`. Its title `str_1937` resolves to **Rear View Detail**. Official `psgraph.mnu` binds a list button to the same list and title. The [menu text-field analysis](original-modern-menu-text-fields.md) documents the Modern `str_` lookup mechanism; this audit retains the exact asset member hashes and matching fields.

The normal selected ordinal mapping is therefore **0=High,1=Medium,2=Low**, consistent with the shared generic selector mechanism documented in the [Frame Size analysis](original-modern-frame-setting.md). On those values, Modern’s context1 lighting gate admits **High/Medium**, rejects **Low**. The descriptor establishes the option’s meaning and storage; it does not establish what the context tag itself denotes, every later writer, persisted-state validity or rendered mirror output.

Original’s same-address row is a different descriptor, so it is not presented as an original `mirrorlevel` counterpart. The manifest retains that original row separately. This address difference does not prove absence of every original mirror-detail control or storage alias. Historical **MP150-002/003**, **MP151-001** and **MP152-001** require their own scoped attribution or intermediate-release evidence. The current binding is useful evidence for the final Modern mechanism without completing those bundled claims.
