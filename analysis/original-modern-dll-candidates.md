# Selected local DLL candidates for deeper original/Modern comparison

## Scope and provenance

The [candidate inventory](scripts/inventory_legacy_dll_candidates.py) hashes selected files already present in the supplied game tree, parses exports/imports, and verifies installed Modern candidates against the pinned official archive. The [manifest](evidence/audits/legacy-dll-candidates.json) retains full hashes and every export address/ordinal and static imported symbol. No DLL was loaded or executed.

The uppercase game-tree files below are **local legacy-style candidates**, not independently authenticated retail originals or proven companions of `nfs3_org.exe`. Similar names and34 shared THRASH export names establish useful interface leads; they do not establish one-to-one function correspondence, API-version/layout compatibility or rendering equivalence.

| Selected file relative to supplied game directory | Bytes | Identity / role |
|---|---:|---|
| `VOODOO2A.DLL` | 93,382 | Distinct local candidate; SHA-256 starts `f65f00e6fa6a` |
| `D3DA.DLL` | 98,641 | Distinct local candidate; SHA-256 starts `ae676272438d` |
| `3dSetup/D3DA.DLL` | 92,514 | Different local candidate despite same basename; SHA-256 starts `988cae4d164a` |
| `drivers/glide3x/voodoo2a.dll` | 69,120 | Byte-identical to official archive member; SHA-256 starts `f15f4f574ddd` |
| `drivers/dx5/dx5a.dll` | 72,704 | Byte-identical to official archive member; SHA-256 starts `6bd5865b05a7` |
| `eacsnd.dll` | 44,032 | Byte-identical to official archive member; SHA-256 starts `63f3d1bff4e6` |

The game-root and setup-directory D3D files must not be silently merged into one baseline. Conversely, the [packaged x87 inventory](original-modern-packaged-x87.md) already verifies that the three distributed Modern `voodoo2a.dll` wrappers are exact duplicates; they need not be analysed as three distinct binaries.

## Export and static-import comparison

Each renderer candidate exports the same set of34 names as its selected Modern comparison, including `_THRASH_about@0` and the remaining recorded THRASH interface. The manifest preserves version-specific export addresses and ordinals; name equality does not imply that implementation bytes or register/data contracts match.

| Candidate comparison | Static imported-symbol difference |
|---|---|
| Root `VOODOO2A.DLL` versus official `drivers/glide3x/voodoo2a.dll` | Legacy candidate additionally imports `DDRAW.dll!DirectDrawCreate`; no Modern-only static symbol in this pair. |
| Root `D3DA.DLL` versus official `drivers/dx5/dx5a.dll` | Imported-symbol sets match, after DLL-name case normalization. |
| Setup `D3DA.DLL` versus official `drivers/dx5/dx5a.dll` | Setup candidate additionally imports `FreeEnvironmentStringsA`; Modern additionally imports `GetAsyncKeyState`. |

These are dependency-table facts, not execution observations. In particular, disappearance of a static DirectDraw import does not prove all DirectDraw use vanished: dynamic lookup and other loaded components remain separate. Matching import sets likewise do not imply identical behavior. Compare each selected function's instructions, descriptor layout and callers before attributing a patch mechanism.

## Sound baseline limit and next evidence

The inspected local `eacsnd.dll` exactly matches the official packaged member. It therefore supplies no distinct older sound baseline for a version-difference claim. This is bounded to the selected files; other installation media or backups were not searched, and no universal statement about all original sound libraries follows.

The bounded Voodoo about follow-up below begins a function-level comparison for one pinned pair; complete descriptor compatibility and functional counterparts still require additional evidence. Original-retail attribution still needs independent media/provenance evidence. The [packaged control-word findings](original-modern-packaged-x87.md) remain current-package analysis until a distinct, justified original counterpart is compared.

**Inventory status: done for selected identities, surfaces and static imports; confidence: verified bytes/PE metadata, unresolved historical pairing.** No function-level difference, rendering success, sound change or compatibility fix is claimed from this inventory. Executables, Ghidra, raw C exports and maintained reconstruction sources remain unchanged.

## Voodoo about descriptor setup

A bounded follow-up now compares the actual `_THRASH_about@0` entry prefixes, rather than assuming correspondence from export names. Run [the setup audit](scripts/audit_voodoo_about_setup.py); its [evidence manifest](evidence/audits/voodoo-about-setup.json) retains both pinned file hashes, prefix bytes/hashes, disassembly and twelve exact instruction assertions.

| Observation | Local legacy Voodoo candidate | Official-matching Modern Voodoo wrapper |
|---|---|---|
| Export entry | `60001a60` | `60001bb0` |
| Static descriptor base | `6000fd54` | `6000fd10` |
| Nonzero first DWORD | Returns descriptor immediately at `60001a73..60001a79` | Returns descriptor immediately at `60001bc6..60001bcf` |
| ECX setup immediate, subsequently stored at descriptor `+0` | `33444658h` | `33444632h` |
| ESI setup immediate, subsequently stored at descriptor `+8` | `68h` | `68h` |
| Later ESI immediate, then store at descriptor `+3ch` | `10h`, store at `60001af4` | `0`, store at `60001c4a` |
| EDI immediate, then store at descriptor `+40h` | `6000fe18`, store at `60001afa` | `60013000`, store at `60001c50` |

Both entries test descriptor DWORD `+0` as their lazy-cache guard. A nonzero value bypasses setup and returns its address in EAX while restoring EBX, ESI, EDI and EBP; the Modern entry also removes its four-byte local stack slot. These are static path/register observations, not proof that the cache is initialized at a particular runtime moment or safe under concurrent first calls.

The initialization prefixes pass descriptor base in EAX and `80h` in EBX to helpers `600048b0` / `60004940`. Those helpers save and restore ECX around their subordinate calls, so the changed ECX literal is not merely a different temporary discarded before the `+0` store. Both also copy a NUL-terminated source string into descriptor `+4ch` with matching inline byte-copy control flow. Neither observation establishes the complete structure layout or string capacity.

The unchanged `+8=68h` agrees with the literal accepted by the [executable loader](original-modern-renderer-loading.md). It must **not** be called a structure size or API version without separate layout evidence. Likewise, `+3ch` and `+40h` are deliberately recorded as offsets, not yet named a mode count/table. Changed pointer addresses alone do not prove changed pointed-to content.

**Stopping boundary and remaining work:** the retained prefixes end at `60001b5e` / `60001cb4`, before the subsequent hardware-dependent paths. Later code calls helpers and indirect targets before returning; it can modify the descriptor. Consequently the table describes setup writes, not guaranteed final returned fields. Follow descriptor-mutating callees and consumer offsets before claiming complete interface compatibility, interpreting the changed fields, or connecting this DLL edit to a particular release-note feature. Retail provenance remains unresolved. No DLL/game execution or Ghidra changes were performed.
