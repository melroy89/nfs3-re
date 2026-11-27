# Packaged DLL x87-control dependencies: bounded static scan

## Scope and artifacts

This is a contextual check of the **11 DLL members in the pinned official Modern archive**, not an original-versus-Modern DLL comparison. It extends the [executable precision comparison](og-modern-x87-precision.md) by identifying places where external components need their own control-state contracts. No DLL was loaded, unpacked into running code or executed.

Run [the static inventory](scripts/inventory_packaged_x87_controls.py). The [manifest](evidence/audits/packaged-x87-control-candidates.json) records archive/member SHA-256, image base, section names and every matching disassembly candidate. New reference copies reside only under ignored `analysis/captures/modern-differences/driver-fpu-members/`; existing files must match archive bytes before reuse.

## Candidate inventory is not reachable-code coverage

GNU objdump executable-section decoding was searched for `FLDCW`, `FNSTCW`, `FSTCW`, `FNINIT` and `FINIT`:

| Archive member | Linear-decoded candidates |
|---|---:|
| `drivers/dgvoodoo/glide3x.dll` | 27 |
| `drivers/dgvoodoo/voodoo2a.dll` | 28 |
| `drivers/dx5/dx5a.dll` | 31 |
| `drivers/dx6/dx6a.dll` | 6 |
| `drivers/dx7/dx7a.dll` | 0 |
| `drivers/dx8/dx8a.dll` | 6 |
| `drivers/glide3x/voodoo2a.dll` | 28 |
| `drivers/nglide/glide3x.dll` | 208 |
| `drivers/nglide/voodoo2a.dll` | 28 |
| `drivers/softtri/softtria.dll` | 23 |
| `eacsnd.dll` | 20 |

The dgVoodoo Glide member has `.MPRESS1`/`.MPRESS2` sections. Its linear hits are **not validated instructions in unpacked execution code** and must not be interpreted as27 executed state changes. Packing, embedded data and alternate boundaries can likewise invalidate other linear candidates. Zero DX7 candidates under this scan does not prove that every runtime dependency preserves the FPU state.

The three `voodoo2a.dll` members are byte-identical (SHA-256 `f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b`). Their repeated counts represent the same wrapper bytes distributed in three directories, not three separately demonstrated algorithms or patch changes.

## Verified DX8 pair changes rounding bits, preserving precision bits

The audit independently checks exact bytes of the well-formed pair `6000b631..6000b664` in `drivers/dx8/dx8a.dll` (51 bytes):

- First helper saves incoming CW with FNSTCW to stack storage, copies it, ORs DWORD mask `00000c00`, loads the low WORD with FLDCW, and stores the original DWORD in shared cell `6001ef78`.
- Second helper reloads that saved DWORD through stack storage with FLDCW and returns.

For the effective low16 control bits, `0c00h` changes rounding-control bits10–11 and leaves precision-control bits8–9 (`0300h`) intact. The verified sequence is therefore **not a precision reduction to24 or53 significand bits**. Its restore uses a shared saved cell rather than an automatic caller-owned token. The caller follow-up below verifies one complete normal-flow pairing. Nested use, synchronization and exceptional/alternate paths remain outside that proof.

The first helper begins with two PUSH ECX instructions. FNSTCW overwrites only the low WORD of the newest pushed value; the high16 bits of the subsequently loaded DWORD therefore come from incoming ECX, not an uninitialized stack value. Writing the modified DWORD into the older pushed slot also means the two POP ECX instructions do not preserve incoming ECX. With `O=(incoming_ECX & ffff0000h) | saved_CW`, the first helper returns EAX=O and ECX=`O | 0c00h`; the second returns EAX=ECX=the saved DWORD from `6001ef78`. These are local register effects, not a claim that callers require them. Only the low WORD is consumed by FLDCW. A C adapter must define which of these machine outputs it preserves rather than assuming ordinary push/pop register preservation.

## Consequence for precision claims and reconstruction

The executable evidence establishes removal of selected original24-bit arithmetic contexts and Modern's extended baseline at those inspected boundaries. This DLL scan does not overturn that finding. It shows why **full control-word state**, save/restore timing and imported-component contracts are broader than the PC precision bits alone. A temporary rounding change is not an80-bit-versus32-bit storage conversion or proof of a different simulation trajectory.

Before a game-facing ARM64/native reconstruction assumes one global floating-point policy, select the actual renderer/audio paths, validate any relevant candidates and trace their calls and restoration. Candidate presence, file names and package inclusion do not prove a path is loaded or reached. No replay/multiplayer compatibility or actual runtime FPU-state conclusion follows from this scan.

**Status: candidate inventory and one local helper contract done; confidence: verified member identities/bytes, bounded decoding and interpreted DX8 pair.** Reachability, remaining candidates, packed code, original DLL counterparts and runtime state remain unresolved. Executables, established Ghidra, raw C exports and maintained reconstruction sources are unchanged.

## Caller follow-up: normal loop exit restores the saved word

The expanded inventory independently captures complete caller `6000c281..6000c352` (209 bytes) in the same pinned DX8 DLL. Its only decoded direct calls to the two helpers occur at `6000c2bd` (enter changed rounding) and `6000c347` (restore). The manifest retains their asserted relative targets and the entire caller hash/capture.

Before changing CW, the caller requests `wrap32(EBX << 4)` bytes through thunk `60011256`, bound to MSVCRT import `??2@YAPAXI@Z`. Its null-result branch jumps to unwind `6000c34f`, bypassing both helper calls. On the other path it computes a binary32 ratio from integer inputs, enters the changed-rounding scope, then either skips the loop to the restore or builds16-byte output records. The normal loop termination joins the same restore call before loading the result pointer and returning. This is a local control-flow proof, not an allocation-success or runtime-reachability test.

Inside the scope, the body performs FMUL/FSUB, binary32 and binary64 stores, a call through `6001124a`, and FISTP. That thunk is verified as imported MSVCRT `floor`; merely recognizing FISTP and replacing it with a default C cast would omit the surrounding rounding-sensitive operations and imported-callee contract. The helper's PC bits still come from the incoming CW. Callee FPU preservation, special inputs and actual numeric results are not established here.

The same decode finds five direct callers of this record builder, at `6000c3b2`, `6000c3ce`, `6000c701`, `6000c71d` and `6000c739`. Higher-level rendering/export ownership is not inferred from adjacency or arithmetic resemblance. Indirect calls, exception paths and concurrent/reentrant access to the shared CW cell remain unverified.

**Follow-up status: complete normal local caller pairing and import bindings verified statically.** This narrows the prior caller unknown without establishing a universal DLL or whole-game floating-point policy. No target execution or new instruction probe occurred.

The [selected local DLL inventory](original-modern-dll-candidates.md) now records distinct legacy-style renderer candidates and their interface/import surfaces. The inspected local sound DLL matches the official member, so it is not a separate original sound baseline. No original-versus-Modern FPU implementation claim is added by those metadata matches.

## Sound reference counterpart: unchanged implementation bytes

The [author-reference/final sound comparison](original-modern-sound-reference-pair.md#complete-file-byte-accounting) now supplies a distinct hash-pinned candidate beyond the previously identical local installed file. Its entire existing code and initialized-data sections match final Modern, so this pair has no changed sound-DLL implementation bytes at the previously inventoried control-word locations. Headers and version resources do change. Equal instruction bytes do not establish equal ambient x87 state: the EXE policy, callers and runtime dependencies remain separate. This is bounded static correspondence, not a universal sound-thread precision or numerical-equivalence claim.

## Four reference/final DLL pairs now compared

The [paired control-site audit](original-modern-paired-dll-x87.md) supplies distinct author-reference counterparts for DX5, software, sound and Glide. All102 primary control candidates and six FSAVE/FRSTOR candidates retain their VAs, bytes and32-byte surrounding contexts in these four pairs. They remain linear-decoding candidates; this does not establish runtime control-word equality or cover other providers/backends. The EXE precision-policy difference and this DLL site-retention result are complementary evidence, not competing global precision claims.

## DX8 retains this rounding scope from 1.6.0 to 1.6.1

The retained `dx8a-1.6.0.dll` and `dx8a-1.6.1.dll` have
SHA-256 hashes
`92e352738012fe1098d98e125bdafae089275ceb7d40a9c1aca9c5b31423a1f7`
and `ddb8a55514bc650384e349cf3830946c149f71234e90a41327f69aca793e81b8`.
Reading the PE bytes at image base `60000000` verifies equality
in the complete caller `6000c281..6000c352`, the helper pair
`6000b631..6000b664`, and the floor thunk `6001124a..60011250`.
In both builds slot `60018070` binds to `MSVCRT.floor`.

The pair and its complete caller at `6000c281..6000c352` also match in all eleven retained DX8 archive members from 1.1.0 through 1.6.1. The 51-byte helper pair has SHA-256 `822d52e074537538b5542b456eba4920ec1724cbd71e331f1431a980e3d0c509` in every member. Each PE imports `floor` at slot `60018070`. The renderer's temporary truncation scope therefore predates the executable's 1.6.0 precision change and retains whichever precision bits arrive on entry.

A linear `objdump -d -Mintel` scan finds the same direct edges into the half-open helper range `6000b631..6000b664` in every retained DX8 build. The only decoded direct entry call is `6000c2bd → 6000b631`, and the only decoded direct restore call is `6000c347 → 6000b654`. The nearby call at `6000cd4f` targets `6000b664`, the prologue of the next function, outside the range. This narrows the known callers of the shared saved word to one paired path. Indirect dispatch, reentry and execution on multiple threads remain separate questions.

This places the same temporary rounding scope in the renderer
that shipped alongside the 1.6.0 executable's extended-precision
change. The 1.6.1 video-mode initialization refactor did not
rewrite this renderer routine. The incoming control word and
the behavior of the loaded MSVCRT are still runtime dependencies.

The saved DWORD at `6001ef78` lies at offset `2f78h` in
`.data` in both builds. That is past the section's `2000h`
file-backed bytes and inside its `2a000h` virtual size, so the
loader supplies its initial zero. Both DLLs have HIGHLOW
relocations on the write and read operands at RVAs `b64dh`
and `b656h`. Both helpers therefore refer to the same
module-relative cell even when the DLL loads at a different base.

A linear disassembly scan in each build found only the save
at `6000b64c` and reload at `6000b655` as direct references
to that absolute address. The cell belongs to the module rather
than the thread or stack frame. If two scopes overlap in the
same loaded DLL, the second save can overwrite the word the first
scope will restore. No such overlap was observed. Caller
serialization and indirect references remain unverified.

### DX8 device creation does not request FPU preservation

The inspected `IDirect3D8::CreateDevice` call at `60003d4c` passes behavior flags `24h` from `60003d3f` in retained 1.6.0 and 1.6.1. The [object and argument trace](original-modern-renderer-texel-alignment.md) identifies this as the device-creation call. The `D3DCREATE_FPU_PRESERVE` bit (`02h`) is clear at that site. This evidence concerns the flags passed at creation and is separate from the explicit rounding helpers above. It leaves the graphics runtime's actual effect on the calling thread's control word unverified. [Wine Direct3D 8 header](https://github.com/wine-mirror/wine/blob/master/include/d3d8.h)

The full 16-byte argument and call span at `60003d3f..60003d4f` matches in all eleven retained Modern archives from 1.1.0 through 1.6.1. The member moves from root `dx8.dll` in 1.1.0 to `drivers/dx8/dx8.dll` in 1.2.0–1.3.1 and `drivers/dx8/dx8a.dll` from 1.4.0. The absence of the preservation request at that call site therefore predates the executable's 1.6.0 x87 policy change.

### The shared EXE DirectDraw cooperation call leaves both FPU bits clear

The original and official 1.6.1 match at `004ebe50..004ebec9` and `004ebf0c..004ebf27`. The DirectDraw cooperation call at `004ebec6` selects `08h` for normal mode or `11h` for exclusive fullscreen. A nonzero `00564edc` on the fullscreen branch changes the flags to `51h`. All three values leave `DDSCL_FPUSETUP` (`0800h`) and `DDSCL_FPUPRESERVE` (`1000h`) clear. This establishes the argument at the shared executable call, independently of the DX8 DLL's device flags. It does not establish which renderer setup routes use this object or how the live DirectDraw implementation treats x87. [DirectDraw cooperative-level documentation](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdraw7-setcooperativelevel)

The executable's decoded direct caller at `00507b5e` reaches cooperation setup only if the legacy DirectDraw initializer `004ebaf0` returns nonzero. In the original, the legacy creation thunk imports `DirectDrawCreate`. From 1.5.0 the same entry is a missing-import diagnostic, as dated in the [import-thunk comparison](original-modern-small-entry-followup.md). The retained cooperation instructions therefore establish a conditional argument contract. They cannot by themselves establish the cooperative level of the separate DirectDraw object used by the bundled DX7 device. The DLL's [device producer](original-modern-dx7-viewport-depth.md#device-producer-identifies-the-receiving-interface) queries its parent interface through the object stored at `60058d80`; its upstream object ownership and cooperative-level call need independent evidence.

### The DX7 driver has its own DirectDraw cooperation path

The retained DX7 1.6.0 and 1.6.1 code matches at the inspected object and flag sites. The call at `60002222` goes through the DLL's own `DirectDrawCreateEx` import and supplies `600186a0` as the output slot. On the selected path, `6000226f` calls vtable slot `+50h` on that object with window `6007b880` and flags from `60018684`. The later device setup copies the object from `600186a0` to `60058d80` before querying the Direct3D7 interface. That chain is distinct from the EXE's legacy DirectDraw initializer.

The flag cell starts in the zero-filled tail of the DLL's `.data` mapping. The inspected mode setup paths at `600030c6..60003108` and `600034eb..60003528` clear or set low mode bits and OR `408h` or `411h`. Starting from zero, these writes do not set either DirectDraw FPU bit. They also preserve any preexisting bits `0800h` and `1000h`. This establishes the effect of the checked instructions, with indirect writes and effective runtime flags still unverified. [DirectDraw cooperative-level documentation](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdraw7-setcooperativelevel)

### The installed original D3D renderer also leaves the FPU bits clear in its local flag writes

The installed original `D3DA.DLL` (SHA-256 `ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02`) has two cooperation call sites, `6000199a` and `60002112`. Both call DirectDraw vtable slot `+50h` on the interface in `60010eb8` and pass the DWORD flags at `60010ea8`. The first call path obtains that interface through QueryInterface at `60001952`.

The original flag DWORD is file-backed and starts at zero. The six decoded stores to its base address change only the low byte, clearing mode bits with `e6h` and setting `08h` or `11h`. The bundled DX7 driver instead uses a zero-filled DWORD and can add `0400h` with its mode flags. In both drivers, the checked writes leave the two higher FPU bits clear from the initial state and would preserve either bit if set elsewhere. This comparison covers the inspected writes and call arguments. Runtime effects on x87 still depend on the DirectDraw implementation. [DirectDraw cooperative-level documentation](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdraw7-setcooperativelevel)

The official 1.6.1 DX5 driver (`drivers/dx5/dx5a.dll`, SHA-256 `6bd5865b05a7a9918da37ad09f643908d9decdcfdb341a23dd60a8cf70c08b42`) retains the two original cooperation argument blocks and both flag-write spans byte for byte. The checked ranges are `60001984..6000199d`, `600020fc..60002115`, `6000205d..600020bc` and `60002313..60002383`, with exclusive ends. The four initial flag bytes at `60010ea8` also match. This extends the original flag finding to the packaged DX5 path.

### DX6 requests FPU setup on its mode-change path

At the three DX6 cooperation calls (`60001a3c`, `60001b73`, `60001f36`), the first pushed argument is the flags DWORD at `60014974`. The next push is the HWND from `6003bce0`, followed by the object pointer. The callback at `60001e0c` supplies the HWND, correcting the earlier interpretation that it supplies flags. The Modern EXE passes the descriptor at `0056afd0` through renderer selector `13h` at `00524734`. DX6 copies its eight DWORDs to `6003bcc0`, placing descriptor offset 4 in `6003bcc4`. The selected EXE descriptor supplies `004eba70` there, which returns the game-window handle.

Initialization clears low mode bits at `60001e4f` and ORs `08h` or `11h` before storing the flags at `60001e6f`. The separate mode-change path starting at `60001ad0` instead ORs `0c08h` or `0c11h`. Those values explicitly set `DDSCL_FPUSETUP` (`0800h`) before the cooperation call at `60001b73`. The masks preserve any prior `DDSCL_FPUPRESERVE` bit. The flag establishes the request issued by this path, with actual runtime x87 effects still open. [DirectDraw cooperative-level documentation](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdraw7-setcooperativelevel)

The DX6 `DDSCL_FPUSETUP` request is already present in retained 1.6.0. The flag construction at `60001ae3..60001b14`, initialization at `60001e4f..60001e74` and argument setup through the mode-change call at `60001b5d..60001b76` match 1.6.1. The preceding zero-HWND branch at `60001add` has a different destination, while both nonzero-HWND branches fall through to the same flag instructions. In both DLLs, `60014974` lies beyond the file-backed portion of the `.data` mapping and starts zero-filled. The mode-change OR establishes the FPU setup bit on the inspected path. Because the initialization mask preserves that bit, a later initialization pass cannot be assumed to clear it.

The same flag construction, initialization and mode-change call blocks are already present in the retained 1.2.0 archive member `drivers/dx6/dx6.dll` (SHA-256 `81cc2b24972d37efca68ad277b714f5053672994df1ed266c529e1e24cd3420f`). The 1.3.0 and 1.3.1 copies have the same hash. The three blocks also match in every retained build from 1.4.0 through 1.6.1, where the member is named `drivers/dx6/dx6a.dll`. The retained 1.1.0 archive has no DX6 member. The explicit DX6 FPU setup request therefore predates the 1.6.0 removal of the executable's own startup single-precision selection.

In official 1.6.1, the first two calls to the record builder are in the routine starting at `6000c352`; the other three are in the routine starting at `6000c693`. The dispatcher starting at `6000cce0` tries these at `6000cd91` and `6000cd9c` after earlier candidates return negative results. A nonnegative result from the first of these two skips the second. This makes the verified rounding scope conditional on reaching one of these processing paths. Runtime frequency remains unverified.

The official 1.6.1 export table identifies `_THRASH_tupdaterect@36` at `60007a20`. Its call at `60007a66` enters `60007c90`, which can call `6000989a` at `60007e30`. That routine reaches the fallback dispatcher at `60009a87`. This establishes a static texture-rectangle update route to the rounding scope, subject to the intervening guards and fallback results. A second decoded call to `6000989a` occurs at `60007c3e`; its own upstream entry was outside this trace.

The second call is reachable through the DX8 full-texture update export `_THRASH_tupdate@12` at `600079e0`. Its nonnull texture and data path calls `60007b00` at `60007a08`. That body contains the call at `60007c3e` to `6000989a`, which in turn reaches the same fallback dispatcher. Official 1.6.1's EXE binds this full-update export through table entry `004f8480` into slot `009ef964` and has decoded indirect calls through the slot, for example `004d0d25`. The EXE contains no plain ASCII `tupdaterect` literal. Thus there is an evidenced game-side route through the full-update export when DX8 is selected. Reachability of the rectangle export from the game and the frequency of either fallback remain open.
