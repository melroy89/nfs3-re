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

## DX8 fog-related vertex policy: partial historical evidence

The same pinned helper bodies provide a concrete change relevant to MP161-002. This is a **verified buffer transformation**, with its interpretation as successful API fog still incomplete. The audit additionally retains the newer table initializer and local state-writing envelopes, and asserts the two arithmetic constants. All addresses below are preferred DX8 DLL addresses; helper ranges end exclusively.

| Aspect | v1.6.0 | v1.6.1 |
|---|---|---|
| Vertex admission | Null pointer returns without writes | Coordinates are accessed immediately; no equivalent local null guard |
| Colour-disabled flag `6001c038 == 0` | Write `ffffffff` at vertex `+0x10`, then return | Write the same value, then continue to the separate mode test |
| Enabled state | Tests `6001edd0` after the colour gate | Tests `6001edd0` independently of that gate |
| Remaining mode policy | Several branches for mode values2/4/8 and table selection, then byte-wise colour blending written at `+0x10` | Mode `6001c08c == 0x10` computes a table index and writes `table[index] << 24` to `+0x14` |

In the newer mode0x10 path (`60002024..60002065`), the arithmetic is `(1 / vertex_float[+0x0c]) / 65535.0 * 255.0`, evaluated on x87, then converted by `FISTP` to a signed DWORD. That conversion uses ambient rounding and exception behavior. Signed comparisons clamp the converted integer to0..255; the selected byte from `600208a0` is shifted24 bits before the DWORD store. This overwrites all four bytes at `+0x14`, making its lower24 bits zero. It is not a direct translation to C casting, nor a proof of sensible results for zero, NaN, overflow or unmasked exceptions.

The startup envelope `600037a3..600037b8` fills256 bytes with `table[i] = 255 - i`. This is a default, not an immutable table: the state envelope `60006501..60006535` conditionally passes the same destination to `600076f0`, calls `60001b40` with pushed values0 and0x23, and stores mode0x10 at `6001c08c`. A separate envelope `60006486..60006498` forwards a value through that wrapper with selector0x1c and stores it at `6001edd0`. Those local writes connect the helper gates to actual state paths; their full dispatch admission, wrapper/API contracts and table-copy behavior still require inspection.

The older helper already contains fog-like depth, table and colour-blend calculations. Therefore this comparison does **not** establish that v1.6.0 had no fog-related code. It establishes a changed representation and gate structure in a corresponding helper with15 retained direct callers. Identifying `+0x14` as the API's specular/fog channel requires tracing vertex format, submission and render-state contracts; that interpretation remains inferred here. Successful visible fog, driver acceptance, every drawing route and original-retail behavior remain untested. MP161-002 receives partial support, not full acceptance.

Next static step: trace `60001b40`, the mode/table state dispatch and vertex submission format, preserving the distinction between buffer evidence and API interpretation. Runtime acceptance is a later, separately scoped comparison.

## DX8 API and vertex-format follow-up

The next inspection resolves the API labels and the selected format layout; full dispatch admission and rendered acceptance remain open. The audit above now retains the additional instruction envelopes and hashes primary [MinGW-w64 Direct3D8 interface](https://github.com/mingw-w64/mingw-w64/blob/master/mingw-w64-headers/include/d3d8.h) and [type](https://github.com/mingw-w64/mingw-w64/blob/master/mingw-w64-headers/include/d3d8types.h) header snapshots. These are ABI references, not source recovered from this driver. Their current upstream URLs may evolve; the evidence manifest pins the bytes actually inspected. Reproduce by acquiring those two URLs into the manifest's ignored snapshot paths and checking their recorded hashes before running the audit; differing upstream bytes require an explicit reference update.

| Instruction evidence in v1.6.1 | Resolved contract |
|---|---|
| Import `d3d8.dll!Direct3DCreate8` at IAT `600180b8`, thunk `60011244`, caller `60003749` with argument120, result stored `6001ed24` | Direct3D8 factory path; this is more than a DLL-name string |
| `60003d2a..60003d51` passes output address `6001ed28` to factory-object vtable `+0x3c` | Matches `IDirect3D8::CreateDevice` and its returned device pointer |
| Wrapper `60001b40..60001b68` forwards its two inputs to device vtable `+0xc8` after two preparation calls | `SetRenderState(state,value)`; returns1 only for exact zero result,0 otherwise, rather than testing HRESULT sign |
| `600061ec..6000627e` selects FVF0x1c4 with stride32 or FVF0x2c4 with stride40, stores format/stride at `6001c084`/`6001c080`, and calls device `+0x130` | `SetVertexShader` fixed-function format selection: XYZRHW, diffuse, specular, and one/two texture-coordinate sets |
| `60001f20..60001fc2` reapplies the format through `+0x130`, binds stream0/buffer `6001dabc`/selected stride through `+0x14c`, then submits batch entries through `+0x118` | `SetVertexShader`, `SetStreamSource`, then `DrawPrimitive` correspondence |

The header method-order check independently derives byte offsets0xc8/0x118/0x130/0x14c for32-bit interface pointers. FVF0x1c4 decomposes as0x4 (XYZRHW),0x40 (diffuse),0x80 (specular),0x100 (one texture set);0x2c4 changes only the texture-set count. Thus both selected layouts place diffuse at+0x10 and specular at+0x14 after four32-bit position components. The new helper's high-byte store therefore supplies specular alpha in these formats. Direct3D documents that channel as the fog-factor carrier; see [Microsoft's fog formulas](https://learn.microsoft.com/en-us/windows/win32/direct3d9/fog-formulas), whose stated device scope includes DirectX7 and later. That documentation explains the contract; it is not an observation of this game's rendering.

The state constants used by the observed wrapper match the Direct3D8 header:0x1c is FOGENABLE,0x23 FOGTABLEMODE,0x8c FOGVERTEXMODE, and0x22 FOGCOLOR. Consequently the local mode0x10 state path disables table-formula fog before setting the helper's software-table mode; the enable path also records its supplied value at `6001edd0`. The separately observed mode2/4/8 branches configure table/vertex formula state and parameters. These labels do not prove every dispatcher input reaches a successful device call. The helper leaves `+0x14` untouched when its enable/mode predicates fail, and the wrapper flushes queued geometry before changing state; those order and stale-field cases matter to later testing.

The table routine `600076f0..600077c0` is **not merely a memcpy**: it has two null guards, a64-iteration loop, multiple byte writes per iteration and x87 conversions via `60009806`. Treat it as a table transformation until its exact interpolation and input contract are reconstructed. Its destination aliases the256-byte default table, so using `255-i` for every session would be unjustified.

This follow-up closes the earlier format/channel ambiguity for the two inspected FVF modes and establishes the wrapper's API contract. MP161-002 remains partial: table transformation semantics, complete state-dispatch admission, all drawing paths, device success and actual visible fog still require separate evidence. No driver, game or target instruction was executed.
