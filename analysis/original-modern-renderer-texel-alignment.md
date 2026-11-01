# Renderer texel alignment: historical DX6/DX7/DX8 coordinate correction

## Evidence and scope

The [paired static audit](scripts/audit_dx6_160_161_alignment.py), run with `python3 analysis/scripts/audit_dx6_160_161_alignment.py`, verifies author-hosted v1.6.0/v1.6.1 archives and DX6 members against the [historical baseline](evidence/audits/official-160-161-baseline.json). Its [manifest](evidence/audits/dx6-160-161-alignment.json) retains hashes, all eight patch sites, disassembly captures and the complete new55-byte adapter. This is a renderer-release comparison, not an original-retail-DLL pairing. No DLL or graphics API was executed.

## Eight sites replace a pushed constant with an adjustment call

At `60005712`, `60006329`, `600063ed`, `600064d7`, `60006583`, `60006633`, `6000670d` and `600067b3`, v1.6.0 executes five-byte `PUSH 1c4h`. V1.6.1 replaces each with a five-byte CALL to `6000e514`. The continuation remains at the same address. For example, the site at `60006329` precedes an indirect drawing call through vtable+74h.

The new helper takes the already-pushed vertex pointer/count and modifies the supplied buffer:

| Property | Verified behavior |
|---|---|
| Inputs | Entry stack+4 pointer; stack+8 DWORD count |
| Vertex stride | 32 bytes |
| Changed fields | Float+0 and float+4 each become original minus0.5 |
| Other per-vertex fields | No stores to them in this helper |
| Zero count | Skips loading the correction constant and all vertex arithmetic |
| Preserved working registers | ECX/EDI saved and restored; other general registers not explicitly modified |
| x87 behavior | Loads binary32 constant0.5 at `6000f158`; stores each corrected component as binary32; pops its retained constant on ordinary completion |

The constant is0.5 in both DLLs; the change is its new use, not a changed numeric literal. Count controls an x86 LOOP; valid buffer/count and ordinary nontrapping x87 execution are caller requirements. No general malformed-input safety claim follows.

## The adapter preserves the pushed-argument shape

After restoring ECX/EDI, the helper duplicates its return address, writes `1c4h` into the next stack slot, and RETs. The caller resumes after the patched instruction with stack shape `[1c4h, vertex_pointer, count, ...]`, matching the original PUSH's net argument layout. A normal C function replacement that merely subtracts0.5 and returns would omit this assembly-specific stack effect.

The helper does not preserve arithmetic flags or x87 status. Its coordinate writes are in place, so reusing the same buffer for another patched submission without reinitialization can apply the correction again. Actual caller buffer ownership/reuse and every exported draw path remain unqualified.

## Release-note support and limits

This supplies partial static support for MP161-001's DX6 portion: a real half-unit X/Y vertex-origin correction appears between author-hosted1.6.0 and1.6.1 at eight verified sites. It is not a direct modification of texture U/V fields. Interpreting its intended purpose as texel alignment is consistent with the release note and draw-call placement, while physical pixel coverage, texture sharpness and all driver modes require rendered evidence.

The following paired investigation establishes DX7/DX8 coordinate corrections independently. Their differing DLL hashes alone were not used as proof of a shared algorithm. This finding also does not establish that original NFS III's driver used this exact older DX6 implementation. Keep EXE query-cache changes separate: this is code inside the packaged renderer, not evidence inferred from the EXE's graphics strings.


## DX7 and DX8 historical instruction traces

The [second audit](scripts/audit_dx7_dx8_160_161_alignment.py), run with `python3 analysis/scripts/audit_dx7_dx8_160_161_alignment.py`, pins both release members for each driver, retains complete relevant helper envelopes and direct-call witnesses, and writes [its manifest](evidence/audits/dx7-dx8-160-161-alignment.json). The exact subtract/store sequence is present once in each newer DLL and absent in that byte form from its older pair; this pattern search corroborates inspected helpers, not an exhaustive semantic absence proof.

| Driver | Verified newer mechanism | Caller boundary |
|---|---|---|
| DX6 |55-byte counted32-byte-stride helper at `6000e514`; subtract0.5 from X/Y and reproduce replaced PUSH1c4h stack effect | Eight exact PUSH-to-CALL patches |
| DX7 |44-byte counted32-byte-stride helper at `6000d580`; same X/Y subtraction, ECX/EDI saved/restored, plain RET | Three direct CALL candidates `60006f5e`, `600082ca`, `600087ee`; no direct call to that target in the older DLL |
| DX8 |New prefix at `60001ff0` subtracts0.5 from one supplied vertex's X/Y, then continues into reworked colour/fog handling | Fifteen identical direct CALL-site addresses target this helper in both releases |

DX7 loads0.5 from `6001544c`; DX8 loads0.5 from `60018220`. DX7 has a count0 guard like DX6, while the DX8 correction prefix operates on its supplied pointer immediately. The DX8 old/new helper bodies are retained in full (`60001ff0..600021f7` versus `60001ff0..60002067`); this report does not declare the other colour/fog changes equivalent or fully explain them. Its15 retained direct calls corroborate helper correspondence more strongly than same-address equality alone.

The DX7 adapter does **not** emulate the DX6 PUSH. Copying one driver's wrapper into another would change the stack contract. All three corrections mutate coordinates in place and perform binary32 stores, with ambient x87 rounding/status/exception behavior still relevant. Repeated buffer reuse, malformed pointer/count inputs, all exported drawing routes and actual screen-space pixel coverage remain outside this static finding.

MP161-001 now has bounded static support for all three named components in an actual1.6.0/1.6.1 pair. The intended alignment explanation is supported by the coordinate adjustments and drawing-call context; no sharper image, universal sampling correctness or original-retail compatibility was observed. The DX8 fog changes are a separate investigation rather than automatically accepted because they share this helper.
