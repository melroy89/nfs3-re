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

A useful next DLL investigation can now choose one candidate pair by exact hash and a specific THRASH export, first establishing descriptor/API-version compatibility and functional counterparts. Original-retail attribution still needs independent media/provenance evidence. The [packaged control-word findings](original-modern-packaged-x87.md) remain current-package analysis until a distinct, justified original counterpart is compared.

**Inventory status: done for selected identities, surfaces and static imports; confidence: verified bytes/PE metadata, unresolved historical pairing.** No function-level difference, rendering success, sound change or compatibility fix is claimed from this inventory. Executables, Ghidra, raw C exports and maintained reconstruction sources remain unchanged.
