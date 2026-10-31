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

The context’s first DWORD is the viewport renderer’s incoming pass tag, as traced below. The option-binding follow-up below identifies Modern `006fd1d8` as Rear View Detail. **MP150-002** mentions headlights in the rear-view mirror, but the lighting gate alone does not identify that viewport or explain clouds/lightnings also bundled in the claim. No catalog promotion is made on that inference.

## Scratch sizing and preserved allocation limitation

Original forms **28*incoming EDX modulo2^32** through shifts/subtraction. Modern uses unsigned `MUL` by28, then copies the low product into EDX. Both pass a local output-pointer cell in EAX to **`004bbde0`**. Discarding the high product preserves the requested low32-bit size; this is not an added multiplication-overflow guard.

The complete arena helper **`004bbde0..004bbe3a`** is byte-identical. It writes the current cursor to the supplied output cell, advances and rounds the stored cursor to a32-byte boundary, then compares consumption against its capacity state. On the diagnostic/failure path it returns0 after updating those cells; this is not an ordinary allocator that leaves output null and state unchanged on failure.

The lighting caller subsequently tests the **output pointer**, not the helper’s Boolean EAX. That retained limitation must not silently become an invented checked-allocation contract in reconstructed C. Capacity, pointer validity, arena lifetime and out-of-range count behavior remain unresolved; no malformed input was executed.

## Calling boundary and result

The paired direct caller witness **`0041d04e..0041d06d`** pushes four stack values, supplies context in EAX, the sizing/count input in EDX, block/index input in EBX and another selector in ECX, then calls at `0041d068`. Callee ends with **RET16** and preserves ESI/EDI/EBP; other register preservation is not guessed from a normal platform ABI. Full pointer types and units require the existing caller/layout research to be completed.

The local accumulator starts0 and sums retained submission-helper results, returning it in EAX at `0041c9d9`. It is not established as a count of visible or successfully drawn primitives. Both rejection paths return0. Modern’s entry gate can therefore expose an existing body to additional contexts without proving correct output for those contexts.

Next: trace the optional pass’s camera construction, then compare any changed helper reached only by the newly admitted cases. Keep mirror attribution, x87/numeric behavior, allocation contracts and runtime visual acceptance separate.

## Modern option binding: Rear View Detail values0..2

The expanded manifest retains Modern20-byte descriptor **`00556564`**: name pointer `00537720` (`mirrorlevel`), WORD-list pointer **`0055623a`**, two zero fields and selector storage **`006fd1d8`**. The list is **187,186,185,0**. The hash-pinned official English resource decodes those IDs as **High, Medium, Low**, respectively; no labels are inferred from their numeric magnitude.

Official `graphics.mnu` binds both an arrow-tab control and a cascade to `listname=mirrorlevel`. Its title `str_1937` resolves to **Rear View Detail**. Official `psgraph.mnu` binds a list button to the same list and title. The [menu text-field analysis](original-modern-menu-text-fields.md) documents the Modern `str_` lookup mechanism; this audit retains the exact asset member hashes and matching fields.

The normal selected ordinal mapping is therefore **0=High,1=Medium,2=Low**, consistent with the shared generic selector mechanism documented in the [Frame Size analysis](original-modern-frame-setting.md). On those values, Modern’s context1 lighting gate admits **High/Medium**, rejects **Low**. The descriptor establishes the option’s meaning and storage; it does not establish what the context tag itself denotes, every later writer, persisted-state validity or rendered mirror output.

Original’s same-address row is a different descriptor, so it is not presented as an original `mirrorlevel` counterpart. The manifest retains that original row separately. This address difference does not prove absence of every original mirror-detail control or storage alias. Historical **MP150-002/003**, **MP151-001** and **MP152-001** require their own scoped attribution or intermediate-release evidence. The current binding is useful evidence for the final Modern mechanism without completing those bundled claims.

## Context producer: optional mirror-setting-gated pass

The expanded audit retains the register-forwarding chain directly from both hash-checked executables:

| Address | Observed data flow |
|---|---|
| `004bc767..004bc777` | Optional pass supplies EAX=1 and calls `004bc470` at `004bc772`. |
| `004bc475`, `004bc481` | Viewport renderer saves incoming EAX in ESI, then stores it at context DWORD0, `007a3d14`. |
| `004bc4fa` | Calls scene renderer `004bc160`; both track-render branches pass context pointer `007a3d14` to `0041b9b0` at `004bc245` or `004bc29d`. |
| `0041b9ba..0041babd` | Saves the incoming context in ESI and forwards that pointer in EAX to `0041cdc0`. |
| `0041cdc9`, `0041d066..0041d068` | Saves context in ESI and forwards it in EAX to the night-lighting helper. |

The full viewport wrapper **`004bc470..004bc529`** and optional-pass admission span **`004bc717..004bc777`** are byte-identical in this pair. The latter selects between two settings using vehicle byte `+0x200` bit`0x20`: storage **`006fbc5c`** or **`006fbe00`**, separated by `0x1a4`. Paired descriptors **`00556870`** and **`00556910`** identify those cells as **`mirror`** and **`mirrorcop`**. A nonzero selected setting additionally requires `00422aa0` to return nonzero; nonzero **`00559264`** can override those local gates. The replay-related role of this override is separately discussed in the [replay mirror analysis](original-modern-replay-mirror.md); its complete lifecycle is not established here. Earlier gating by `007a3d10` also remains part of admission.

The other two visible calls to `004bc470`, at **`004bc6d8`** and **`004bc712`**, supply EAX=0. In the session1 branch, the call shared at `004bc772` also receives EAX=0 and EDX=1, so **the call address alone is insufficient to identify a mirror pass**. Its incoming register values distinguish that route from the optional EAX=1 route.

This establishes tag1 as the **optional mirror-setting-gated render pass**, rather than an arbitrary guessed tag. Combined with the Rear View Detail binding, Modern admits the retained night-lighting body for that pass at High/Medium, whereas original rejects it. Full camera orientation, transitive context mutations, actual visible headlights and the claim’s clouds/lightnings remain unverified. No runtime or historical-release equivalence is claimed. The complete `0041b9b0` prefix differs elsewhere between versions; retaining both spans does not label it byte-identical.
