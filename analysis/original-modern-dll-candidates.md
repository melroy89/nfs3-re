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

The unchanged `+8=68h` agrees with the literal accepted by the [executable loader](original-modern-renderer-loading.md). It must **not** be called a structure size or API version without separate layout evidence. Likewise, the prefix alone does not name `+3ch` and `+40h`; the consumer-backed interpretation follows below. Changed pointer addresses alone do not prove changed pointed-to content.

**Stopping boundary and remaining work:** the retained prefixes end at `60001b5e` / `60001cb4`, before the subsequent hardware-dependent paths. Later code calls helpers and indirect targets before returning; it can modify the descriptor. Consequently the table describes setup writes, not guaranteed final returned fields. Follow descriptor-mutating callees and consumer offsets before claiming complete interface compatibility, interpreting the changed fields, or connecting this DLL edit to a particular release-note feature. Retail provenance remains unresolved. No DLL/game execution or Ghidra changes were performed.

## Mode-producing helpers: fixed records versus inserted records

The setup audit now also retains complete selected helper bodies: legacy `600018c0..60001a53`, Modern `600018d8..60001b79`, and Modern insertion helper `600012e8..600013e9` (half-open ranges). Five additional exact assertions cover the insertion limit, record stride, count updates and completion store. This extends the preceding prefix-only stopping boundary, without claiming every indirect dependency is understood.

The independent [EXE enumeration consumer](original-modern-display-modes.md) establishes descriptor `+3ch` as the count and `+40h` as the array pointer, with 28h-byte records and width/height/depth at `+0/+4/+8`. Those consumer findings justify naming these fields here; the setup prefix alone did not.

- **Legacy candidate:** descriptor count is initially16 and table base `6000fe18`. The helper starts at `6000fe40` (record1), iterates indices1 through16, and updates fields `+14h/+18h`. Its arithmetic uses the low32-bit product of width, height and arithmetic-shifted depth/8, followed by signed division of a hardware-derived quantity. It applies width-dependent exclusions and clamps positive derived fields to3; it does not insert additional records in this helper. This establishes fixed-table processing, not the meaning or validity of every hardware quantity.
- **Modern wrapper:** descriptor count initially0 and table base `60013000`. Helper `600018d8` has a separate once-only guard at `600127d4`. It submits an initial candidate containing640,480,16 to `600012e8`, then makes a two-call indirect query using the same request pointer, first with null output and then stack output sized from the first return. A fallback alters the request and retries once. These are static call shapes; the dynamic target's API identity and units still need independent binding.
- **Candidate processing:** Modern reads16-byte returned records, decodes dimensions directly or via a lookup for small identifiers, rejects widths below640 or heights below480, and submits a16-bit candidate. When cell `600127c8` is nonzero it also submits a32-bit candidate. That cell's runtime value and capability meaning remain unverified; this is conditional32-bit mode construction, not proof every wrapper offers32-bit output.
- **Insertion and duplicates:** `600012e8` binary-searches the first three unsigned DWORDs using `REPE CMPSD`; equal keys update an existing record. New records are inserted in order, shifting both28h-byte records and parallel8-byte records backwards with `STD/REP MOVSD`, then restoring DF with `CLD`. It rejects new keys when the current insertion count is unsigned>=100. Duplicate updates remain possible at that limit. It returns EAX=1 for accepted/update paths and0 for capacity rejection, while POPAD restores the other general registers.
- **Published count boundary:** after insertion/query processing, `60001b67` increments the count once more, then stores1 to the once-only guard. Thus100 is the insertion helper's limit, **not an independently proven maximum published descriptor count**. The EXE enumerates through its count inclusive. The role and initialization of that extra final slot must be checked before calling it a sentinel, valid mode or off-by-one defect. Neither label is established here.

These bodies establish a substantive algorithm difference for this pinned legacy-style/Modern wrapper pair: fixed-table capability processing versus query-driven sorted insertion with conditional depth variants. They do not authenticate the legacy DLL as retail, date the change, prove a particular release-note claim, or validate rendering. Remaining work is dynamic-target binding, exact query-result contracts and the final extra-slot boundary; no new game/probe execution is needed to pursue those static questions.

## Extra-slot boundary checked against the executable

A follow-up of the same [audit and manifest](evidence/audits/voodoo-about-setup.json) pins the official EXE and checks four consumer instructions. `004bedad` compares the one-based index against the captured descriptor count and exits with signed JG: the final increment really does expose one extra candidate to enumeration. It is not an exclusive-count interpretation.

At the insertion limit of100 unique keys, the inserted records occupy indices1..100. The extra index101 addresses `60013fc8..60013ff0` (half-open), from `60013000 + 101*28h`. The Modern wrapper's `.bss` header starts at `60011000`, has raw-size field3000h, virtual-size field0, raw-data pointer0 and characteristics `c0000080` (uninitialized, readable/writable). Using the section's nonzero size field gives an end at `60014000`; the extra record fits within that declared extent. This is PE storage metadata, not a read of file-backed zero bytes or confirmation of runtime loader mapping. The zero virtual-size field must not be silently represented as a conventional nonzero VirtualSize in a reconstruction manifest.

The EXE eligibility helper first tests record flag bit0 (`004bee67..004bee6c`), then bit1 and signed field `+14h >= 2`; only later does it divide by height at `004bee7f`. **If the extra slot remains zero-filled, it is rejected before division and before a menu callback.** Thus the inclusive count alone does not establish a divide-by-zero or out-of-image read. Conversely, fitting section metadata does not prove the slot's live contents or rule out aliasing/writes. Exhaustive DLL write ownership, loader mapping and runtime values remain unverified. The intended sentinel interpretation is plausible but remains inferred, and no original defect or compatibility fix is claimed.
