# Renderer texel alignment: historical DX6 vertex correction

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

The DX7 and DX8 portions still need their own paired instruction/data traces. Their differing DLL hashes alone do not prove the same algorithm was applied. This finding also does not establish that original NFS III's driver used this exact older DX6 implementation. Keep EXE query-cache changes separate: this is code inside the packaged renderer, not evidence inferred from the EXE's graphics strings.
