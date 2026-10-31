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
