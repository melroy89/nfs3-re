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

## Retained table expansion and changed selection

The next paired inspection verifies the complete208-byte routine `600076f0..600077c0` is **byte-identical in1.6.0 and1.6.1**, as are its two binary32 coefficients at `60018230`/`60018234`: approximately−0.6700000167 and−0.3300000131. Both helper calls at `60009806` use an import thunk for `MSVCRT.dll!_ftol` at IAT `6001806c`. The audit asserts these identities, retains both complete bodies and their local caller envelopes, and finds one direct CALL candidate per release: older `60006551`, newer `60006517`.

For valid, non-overlapping source/destination buffers, the dataflow expands64 source bytes into256 destination bytes. Iteration `i=0..63` reads `A=source[i]`, `B=source[min(i+1,63)]`, forms signed difference `B-A`, and writes four output bytes. The first is A and the fourth B. The middle bytes subtract the low-byte results of imported conversions of `(B-A)*coefficient` from A, using the−0.33 coefficient first and−0.67 second. Subtraction/stores use byte arithmetic; the positions are `destination[4*i+0..3]`. The final iteration repeats source[63] as both endpoints. This is interpolation-like expansion with quantized conversion, not simply four copies or exact one-third/two-thirds arithmetic.

The routine returns without writes when either pointer is null. It does not receive lengths or check buffer sizes. Its pointer-difference addressing and forward writes do not establish arbitrary overlap safety. The mathematical description assumes the imported helper follows its expected x87 conversion/stack contract; this audit identifies the import but does not pin or execute the installed CRT implementation. Exact exceptional behavior and machine-state equivalence remain outside this static derivation.

The historical difference is in selection and consumption:

| Release | Caller and consumer evidence |
|---|---|
|1.6.0 | Local caller `60006543..6000656d` optionally expands a supplied table, then writes1 to `6001edd4`. The old vertex helper tests that selector and uses its table branch before colour blending at `+0x10`. |
|1.6.1 | Local caller `60006501..60006535` optionally expands the table, then sets API FOGTABLEMODE to0 and local mode `6001c08c` to0x10. The new helper uses its gated reciprocal-depth index to write the table-derived specular alpha at `+0x14`. |

Thus the renderer reuses the existing expansion algorithm while changing the state route and output channel. This also strengthens the warning against reading the release note as “there was no fog-related implementation before1.6.1.” Whether the new route fixes visible fog on a particular device still requires observation. Remaining static work is complete dispatcher admission/default-state tracing and other submission paths; retained helper conversion semantics require a separately identified CRT if exactness becomes necessary. MP161-002 remains partial.

## Exported state dispatch: selected fog routes

Both DLLs export `_THRASH_setstate@8` at `60005490`. Its inspected prologue masks the selector to16 bits, indexes the byte table `600073f4`, then the target table `60007334` for these selectors. The audit now resolves and asserts each route below from the actual tables, retaining both prologues, case envelopes and return tails. This closes the selected route-address gap; it is not a recovery of every case in the much larger dispatcher.

| Low16 selector | v1.6.0 case entry | v1.6.1 case entry | Paired meaning |
|---|---|---|---|
|0x14 and0x69 | `60006543` | `60006501` | Shared table-expansion route; newer route selects mode0x10 and disables API table-formula fog |
|0x15 | `6000645d` | `6000645d` | Enable/formula selection; same entry address, changed body |
|0x0f | `6000656d` | `60006537` | Mask colour to24 bits; newer route additionally forwards FOGCOLOR to API |
|0x0e | `60006502` | `60006550` | Older stores raw parameter at `6001eddc`; newer applies its integer-or-bit-pattern rule below and forwards FOGDENSITY |
|0x16 /0x17 | `60006518` / `6000652e` | `60006579` / `60006593` | Older stores raw parameters; newer converts signed integers through FILD/binary32 stores and forwards FOGSTART/FOGEND |
|0x4b /0x4c | `60006589` / `6000659f` | `60007328` / `60007328` | Older raw writes to start/end storage; newer direct return0 with the prologue's EDI still zero |

In1.6.1 the mode and table entries first require `600201ec == 0`; failure reaches `60006789` and returns0 without applying those local writes. The physical meaning and lifecycle of this guard remain unresolved. For selector0x15, values0/1 forward API FOGENABLE0/1 and store that value at `6001edd0`. Values2/4/8 select API formula values3/1/2 respectively, configure relevant parameters and table/vertex formula states, and store the requested mode at `6001c08c`; other values return0. Formula selection does not itself write the local enable cell, so it must not be modelled as equivalent to enabling fog. The older value1 path instead stores local enable1 while forwarding API FOGENABLE0, consistent with its software colour-blending route.

For newer selector0x0e, raw values1..4095 become a binary32 reciprocal of the signed integer; zero or values with any bit in `0xfffff000` set retain their original bits. The result is stored at `6001c094` and forwarded as FOGDENSITY. This mixed representation is verified from instructions, not a proposed cleaned-up type. Selectors0x16/0x17 convert signed integer inputs to binary32 at `6001c098`/`6001c09c`; this differs from the older raw-bit stores and from the now-unaccepted0x4b/0x4c aliases.

These newer colour/parameter routes converge on `600065ab`, which sets EDI1; the table route reaches it as well. The mode route likewise reaches this success path after its wrapper calls. They discard `60001b40`'s Boolean result. The common tail `6000731a` notifies `600031c0` with the full original selector and payload, then returns EDI, under its normal callee-preservation contract. Therefore local return1 indicates the case was accepted, **not** that Direct3D accepted each state. Calls can also flush queued geometry before applying a state. Callback/cache side effects, guard initialization, other cases and actual device results remain separate investigation boundaries.

This is a concrete historical API/state-policy difference, beyond the helper's changed output channel. It supports the intended implementation of MP161-002 while leaving rendered fog unverified. No original-retail driver correspondence is asserted from this1.6.0/1.6.1 pair.

## Guard provenance, initial storage and stopping point

The complete capability mapper `60008140..600083fd` is identical in both historical DLLs. It first clears53 DWORDs at `6001edf0` and49 DWORDs at `600201c0`, then calls device vtable+0x1c (`GetDeviceCaps`) with the first buffer. This explicitly clears guard `600201ec` on entry. A nonzero API result returns0 before the later population. On the successful path EBX is1; the mapper tests bit0x00100000 of `6001ee14` and writes1 to the guard when that bit is set. The pinned [Direct3D8 capability header](https://github.com/mingw-w64/mingw-w64/blob/master/mingw-w64-headers/include/d3d8caps.h) places RasterCaps at buffer+0x24 and labels the bit `D3DPRASTERCAPS_WFOG`. The audit now retains/hash-pins this third header as well; the same snapshot acquisition procedure applies.

The mapper then calls `60008400`, which queries an adapter identifier and applies device-specific branches. Inspected retained envelopes include explicit zero stores at `60008630`, `6000865a` and `60008727` with ESI zeroed on entry; those can override the capability-derived guard. The startup capability mapper has a direct CALL witness at `60003f4b`, and its quirk call is at `60008358`. This establishes provenance and local overwrite order, not an exhaustive writer search or the complete lifecycle across resets/external callbacks. The guard's important observed polarity is: **new mode/table cases reject nonzero**, even though the capability mapper can set it from an advertised W-fog bit. Do not invert that condition or silently repair it in a reconstruction. Whether that policy is deliberate or problematic on a specific device remains unknown.

The DLL's `.data` section starts at RVA0x1c000, has raw size0x2000 and virtual size0x2a000. Mode `6001c08c` is file-backed with initial DWORD2. Enable `6001edd0` and guard `600201ec` lie beyond the raw bytes, within the section's virtual tail: loader-zero initialization is expected from this layout, **not a captured runtime value**. A missing result from `pefile.get_data` there must not be interpreted as file-backed zeros. Later mode/enable writes and the explicit capability reset are separate from these initial-storage facts.

The complete notification routine `600031c0..6000326c` and range lookup `60003170..600031b8` are also identical between releases. The notifier masks selector/stage fields, conditionally stores the payload into cache `6001dae8`, then invokes an optional callback from `6001eef8`. It saves/restores EDI locally, so the setstate tail's EDI success value is retained under the normal callback ABI. Its callee can still have side effects; identical notifier bytes do not establish identical callback targets, cache contents or recursive behaviour.

This closes the local guard-producer and notifier-body questions without claiming a complete fog subsystem. The historical comparison now explains coordinate correction, table expansion, output layout, selected exported state admission and capability-derived gating. Remaining requirements for broader acceptance are other submission routes, complete reset/callback lifecycle, exact external CRT edge behaviour where relevant, and device/rendered observations. MP161-002 remains partial. No game/DLL execution, target-byte changes or Ghidra writes were used.
