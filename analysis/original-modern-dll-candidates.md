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

## Dynamic Glide bindings behind the mode builder

The [setup audit](scripts/audit_voodoo_about_setup.py) now retains the complete resolver `60001020..60001107`, parses its terminated name/destination table beginning at `60001120`, and asserts the relevant Windows imports and Glide names. Successful resolution is a verified code/data relationship, beyond finding a DLL name in strings.

The resolver calls imported `LoadLibraryA` at `60001074`, with a path assembled from its own module filename and the literal `glide3x.dll`; on failure it retries the bare literal at `6000108b`. It then walks name/destination pairs, calls imported `GetProcAddress` at `600010a3`, and writes each nonzero result through that pair's destination at `600010b0`. A missing required name frees the module and returns failure. Successful completion saves the module handle. Provider selection under Windows/Wine search rules and the actual loaded file identity are not observed here.

| Destination call slot | Required resolved name | Mode-builder use |
|---|---|---|
| `600110c0` | `_grGet@12` | Numeric capability queries, including selectors17,12,14 and10 |
| `600110c4` | `_grGetString@4` | String queries with selectors161 and160 |
| `600127c0` | `_grQueryResolutions@8` | Request/null-output size query, then request/stack-output population |
| `600127c4` | `_grGetProcAddress@4` | Optional extension lookup |
| `600110ac` | `_grTexMinAddress@4` | Subtracted from `_grTexMaxAddress@4` result when deriving descriptor `+70h` |
| `600110b0` | `_grTexMaxAddress@4` | Supplies the initial value for that derivation |

The full table is retained in the manifest; the table above selects dependencies of the inspected helper. Decorated names record the requested interface, not independent proof that every provider implements its expected ABI correctly. Numeric Glide selectors remain literal values until independently mapped to the relevant header/version; they must not acquire invented capability names.

The mode builder obtains selector160 text and tests it against literal `PIXEXT` via helper `60004870`. When that test returns nonzero, it requests `grSstWinOpenExt` through the resolved Glide procedure lookup at `60001a01` and stores the returned pointer at `600127c8`. The conditional32-bit candidate path tests this same cell at `60001b3b`. Thus the earlier anonymous cell is an **optional extension lookup result**, and the two-call query is statically bound to **grQueryResolutions**. The extension string test, successful lookup and subsequent branch do not establish32-bit rendering success or the loaded provider's precision behavior.

This resolves the dynamic-target identity gap for the selected paths. Remaining scope includes exact provider-specific query structure/constants, all writes/aliases to the final extra mode slot, and original-retail provenance. No DLL was loaded and no runtime test or source reconstruction occurred.

## Author-hosted v1.6.0 baseline now retained

On2026-11-01, inspection of the author's [public file directory](https://veg.by/files/nfs3/) located explicitly versioned archives, including [v1.6.0](https://veg.by/files/nfs3/nfs3_modern_patch_v1.6.0.7z). The author also points readers to this directory for older renderer versions in a [project comment](https://veg.by/en/projects/nfs3/comment-page-12/). Earlier statements that an older matching package still had to be obtained are superseded for this particular pair; they remain valid for uninspected versions/components.

The retained v1.6.0 archive SHA-256 is `9e1bb8f034026f6f2641417d59f46203f787771394767ca4c6ae4474e4324bb8`. Its internal English banner identifies v1.6.0 dated2016/09/22. The already pinned final archive identifies v1.6.1. [The new baseline manifest](evidence/audits/official-160-161-baseline.json), reproduced by `python3 analysis/scripts/audit_official_160_history.py`, retains both archive URLs/hashes, readme hashes/banners, and full hashes/export metadata for each EXE and DX6/DX7/DX8 renderer.

| Member | v1.6.0 bytes | v1.6.1 bytes | Identical file bytes? |
|---|---:|---:|---|
| `nfs3.exe` | 1,697,792 | 1,698,304 | No |
| `drivers/dx6/dx6a.dll` | 94,208 | 94,208 | No |
| `drivers/dx7/dx7a.dll` | 110,592 | 110,592 | No |
| `drivers/dx8/dx8a.dll` | 135,168 | 135,168 | No |

These are author-hosted artifact identities corroborated by internal banners, **not** publisher-signature verification or proof that each claimed feature first appeared in that release. Equal file sizes do not imply equal renderers. This step removes the acquisition blocker for focused v1.6.0-to-v1.6.1 texel-alignment/fog/mode-policy comparisons; actual export/function correspondence and changed behavior still need analysis. The archives remain ignored reference captures, and no component was installed or executed.

For reproduction, retain the two archives at the manifest paths. The historical acquisition command is `curl -fsSL https://veg.by/files/nfs3/nfs3_modern_patch_v1.6.0.7z -o analysis/captures/modern-differences/upstream/history/nfs3_modern_patch_v1.6.0.7z` after creating that ignored directory. The audit rejects changed archive hashes before parsing members; a future different download must be treated as a new artifact rather than silently substituted.

## Additional original-side reference candidates

The [author-hosted original-reference bundle inventory](original-modern-original-reference-bundle.md) now pins d3da.dll, softtria.dll and voodoo2a.dll alongside two other DLLs,80 menus and six HUD-position files. The bundle is mixed and its EXE differs from the supplied baseline at one branch byte. This makes bounded original-side renderer pairing possible without upgrading any artifact to authenticated retail provenance. Function/feature comparison remains the next step; nothing was installed or executed.

## DX5 author-reference pairing

The [DX5 paired audit](original-modern-dx5-reference-pair.md) now verifies that the author-reference `d3da.dll` matches the local root candidate and has the same34 export entries as final DX5. It records all25 changed-byte intervals in the shared code-section extent, equal import/data sections and the exact `about` descriptor-pointer change. This is bounded correspondence and localization, not complete mode-policy recovery or authenticated retail provenance.

## Distinct author-reference sound candidate compared

The [sound pair audit](original-modern-sound-reference-pair.md) now compares the separately identified author-reference eacsnd.dll with final Modern. All41,472 shared post-header bytes are identical, including every existing code/data/import/export/relocation section; changes are confined to headers and an added version-resource section. The older local-only acquisition limit above remains accurate for those selected local files, but no longer prevents this named pair comparison. Runtime equivalence and pristine-retail attribution remain unverified.

## Author-hosted Glide reference is a different build

The [three-way Glide identity audit](original-modern-glide-reference-identity.md) verifies that the hosted reference differs from this chapter’s local legacy candidate at all34 export RVAs, while hosted/final export entries match. The hosted file already statically imports three Glide3x APIs absent from the local candidate. Earlier local-candidate mode/descriptor findings remain valid only for that pinned pair; they must not be transferred wholesale to the hosted reference. A new raw map localizes3307 code-section differing bytes for the hosted/final pair; semantic follow-up is pending.

## Hosted/final loader lifecycle follow-up

The [hosted/final lifecycle comparison](original-modern-glide-reference-identity.md#loader-and-cleanup-lifecycle-differ) now distinguishes reference about-time FreeLibrary/handle clear from final shutdown/latch decrement with the module handle retained locally. Final acquisition and required-name binding are centralized; repeated nonzero-state acquisition does not increment the latch, so it must not be described as general reference counting. Partial binding, detach and runtime provider lifetime remain unverified. This is a new comparison for the hosted reference, not a transfer from the different local candidate.

## Glide self-module filename producer verified

The [entry-path follow-up](original-modern-glide-reference-identity.md#entry-callback-supplies-the-module-directory-handle) verifies the unchanged PE-entry/CRT wrapper and changed user callback: final stores its first DLL-entry argument into the exact cell passed to GetModuleFileNameA for the prefixed Glide load attempt. Reference callback only returns1. The changed callback itself has no detach release; indirect/registered finalizers and other callers remain separate. This strengthens the earlier own-module path description without asserting provider identity or universal cleanup.

## Early Modern renderer filenames

The retained reference `nfs3_orig.7z` (SHA-256 `374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127`) and author-hosted 1.1.0 archive (SHA-256 `31365ebb12f826a031378d5555aadd899873eb1a896f1e10ba49c464c0e4d7ac`) contain the following root-level names. Each code section begins at RVA `1000h`. The counts compare shared raw offsets. Modern Voodoo2 also has 512 additional raw code-section bytes.

| Reference name | Modern 1.1.0 name | Changed code bytes / raw code bytes |
|---|---|---:|
| `d3da.dll` | `dx5.dll` | 283 / 55,296 |
| `softtria.dll` | `softtri.dll` | 16 / 245,760 |
| `voodoo2a.dll` | `voodoo2.dll` | 345 / 51,712 shared (+512 Modern) |

The reference D3D and SoftTri members match the corresponding installed files by SHA-256. The reference Voodoo2 member is a distinct artifact from the installed copy. The archive evidence supports the three filename correspondences and shows that each pair also differs in code. It leaves the exact introduction release before or at 1.1.0, the authors' source lineage, and the behavior of the changed bytes open.

### SoftTri mode-list callback changes by 1.1.0

The 16 differing file bytes in this DLL pair are all in the same routine at
`60002480`. Extract the two DLL members from the archives above with
`7z x -so`, then disassemble each with
`objdump -d -Mintel --start-address=0x60002480 --stop-address=0x60002580`.
The original-reference SHA-256 is
`8ea15aac0a7095b7d750cd75bbc9095553b6f708d1b89ca807864294a1a12b02`.
The 1.1.0 SHA-256 is
`5b956278ca5444badf233f571140ff6fc8767534467c7ea6c0e7a1e71e6a6cd9`.

| DLL address | Original reference | Modern 1.1.0 |
|---|---|---|
| `60002494..60002499` | Converts the incoming descriptor value 15 at offset `+0x54` to 16 and passes other values through to the format helper at `60002e80`. | Requires exactly 16 before calling the helper. Other values return 1 without adding a record. |
| `60002537..60002545` | The reachable general-size path calls `KERNEL32.GetSystemInfo` through IAT slot `6003d200` into the stack local. The shared tail divides the dword at local offset 4 by 40 and compares it against the output count. | Skips record insertion for a signed height below 480. Otherwise jumps directly to the shared capacity calculation, which still reads local offset 4. |

The 640×480 and 800×600 special paths still use fixed record locations for
admitted modes. The 1.1.0 general-size path has no visible initialization of
the capacity input in this routine before the division. Consequently the
static comparison establishes the added filters and lost API call, while
actual enumeration results and reproducibility of the capacity check remain
unverified. No renderer was loaded or run.

The retained archives date the two changes separately. Extract the exact
member listed by `7z l -slt` and compare PE RVAs `2494` (5 bytes) and
`2537` (14 bytes). Both windows were checked in every retained Modern release
from 1.1.0 through 1.6.1.

| Retained releases | Archive member | Depth gate at `60002494` | General-size path at `60002537` |
|---|---|---|---|
| 1.1.0 | `softtri.dll` | Requires 16 | Height floor of 480, skips system-info query |
| 1.2.0, 1.3.0, 1.3.1 | `drivers/softtri/softtri.dll` | Same | Same |
| 1.4.0 | `drivers/softtri/softtria.dll` | Same | Same |
| 1.5.0 through 1.6.1 | `drivers/softtri/softtria.dll` | Same | Height floor removed, system-info query restored |

The directory move is first observed in 1.2.0 and the original basename
returns in 1.4.0. The 1.5.0 bug-fix span matches the restored-path bytes
through 1.6.1, while the exact-16 depth filter persists. See the
[1.5.0 fix analysis](original-modern-software-reference-pair.md#historical-softtri-fix-initializes-a-mode-bound-input)
for the separate allocation and registration evidence.

### Early Voodoo2 adapter changes display setup references

For the same archive pair, the hosted reference `voodoo2a.dll` hashes to
`99b978fd6b0e94cca7ef0b671b9be0d630f929ab3901ebddaafa5d121213503b`
and 1.1.0 `voodoo2.dll` hashes to
`b1ef2f398978584ccf5891a2fd4a1b94d406e4a68afc2f823be3107692c7ba5b`.
Comparing the first section at equal raw offsets places 43 of the 345
differing bytes between `60001c2a` and `60002374` inclusive. The other
302 fall in `6000d8a0..6000d9ff` inclusive.

| Instruction addresses | Verified 1.1.0 change |
|---|---|
| `60001c29`, `6000215e`, `60002368`, `6000236f` | Retargets the record base from `6000fdd4` to `60012880`, including indexed field accesses at offsets 0, 4 and 24. |
| `600021ad`, `600021e0` | Retargets a separately indexed dword table from `600100a4` to `600127c0`. |
| `60001c4a`, `60001cba` | Replaces two stores to `6000fd4c` and `6000fd7c` with jumps over padding. |
| `60001d22`, `60001d3e`, `60001f64`, `60002218` | Calls the new entry at `6000d8a0` instead of calling `60001940` directly. The new code still calls `60001940` at `6000d908`. |

The references can be reproduced by extracting the named members and
disassembling the two ranges with `objdump -d -Mintel`. The call and table
changes are verified statically. Table contents and initialization, the new
entry's complete behavior, and the effect on available display modes remain
open. The supplied installed Voodoo2 copy is a different baseline.

The full new routine extends through the return at `6000daf0`. The earlier
302-byte count covers only the shared raw offsets. The original section ends
at `6000da00` exclusive, while the Modern section extends to `6000dc00`.

At `6000d8a0`, a latch at `600127b8` skips setup after the first completed
attempt. On the first attempt, thunk `6000d89a` resolves through IAT slot
`6000e278` to `glide3x.dll!_grQueryResolutions@8`. The routine queries once
with a null output pointer and again with a buffer sized by the first return.
If either return is zero or the second call's first signed dword is at most
255, it invokes the legacy setup at `60001940` and copies 18 dwords of table
data and 180 dwords of mode records from the old bases to the new ones.

The other path walks 16-byte query records. It checks the first two words
against signed minimums of 640 and 480, finds an existing width/height pair
or an empty 40-byte slot, and caps new insertions at 46 slots. For accepted
entries it updates both retargeted tables and keeps the greater signed value
from the query's dword at offset 8 and the record's field at offset 20.
The fallback stores 0 at `600127bc` and the query path stores 1. Both set
the setup latch to 1 before returning. These checks establish how the
adapter populates the tables. Actual provider output, the meaning of the
offset-8 field and the resulting in-game list remain unverified.

### Early DX5 adapter rewrites mode insertion

The reference `d3da.dll` SHA-256 is
`ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02`.
The 1.1.0 `dx5.dll` SHA-256 is
`8609a2f9d67bbb3be61b8519f1339d2854354b60046f59ec2618c27c0484966e`.
Disassemble both archive members with `objdump -d -Mintel` and compare
the callback span beginning at `600017c7`.

- The original treats incoming 16-bit 640×480 and 800×600 modes as fixed
  slot updates. Its general path appends in 40-byte steps and returns 0
  when the unsigned count reaches 30.
- In 1.1.0, `6000181c` rejects signed heights below 480 after the
  memory-per-mode calculation. The search starts at slot 1. It updates
  a matching width/height slot unless its stored depth exceeds the incoming
  depth. At the first empty slot it increments the count only when the
  unsigned count is below 30. The full-count branch returns 1.
- At `60001852`, 640×480 forces the outgoing depth to 16 before the existing
  format-class-3 override can set it to 15. The comparison against a
  populated slot uses the incoming depth, before either output override.

All 283 unequal code bytes fall within `600017c7..600018e2` inclusive,
covering this callback rewrite and padding after the shorter Modern return.
The renderer API's enumeration order and the resulting in-game list remain
untested.

The code change also accounts for the changed effective relocation targets.
Comparing decoded PE base-relocation entries as `(RVA, type)` pairs, with
type-0 padding excluded, removes five HIGHLOW entries (`1801`, `1828`,
`189a`, `18ad`, `18c4`) and adds two (`180a`, `1826`). Each falls
inside the callback span. The raw import, initialized data and export
sections match byte for byte. The resource section grows from 1,024 to
1,536 raw bytes and both resource directories list type 16 (version
information). The resource payload and headers are outside the code-byte
count. The zero-raw-pointer `.bss` is excluded from file-backed byte
comparisons.

#### DX5 version-resource identity

Both resources have string table `040904b0`. Parsing the extracted DLLs
with `pefile.PE(...).FileInfo` gives the following fields.

| Version string | Reference | Modern 1.1.0 |
|---|---|---|
| File description | D3D 3rash Module | DirectX 5 Thrash Video Driver |
| Internal name | D3D | DX5 |
| Original filename | d3da.dll | dx5.dll |
| File version | 1998.08.10.1148 | 2015.05.23.0038 |
| Product version | Empty | 1.1.0 |

Modern's Comments field credits `d3da.dll` and names NFS III build
`6552.8.16.4424/1998.08.10.1148`. The trailing version agrees with the
reference resource, and the paired code comparison shows that differences
are confined to the mode callback. The build credit is embedded attribution.
The file-version string also differs from the catalog's release date, so
it does not independently date public availability.

#### DX5 callback history

Extract the exact DX5 member from each retained archive and compare the
complete callback from PE RVA `17bc` up to the exclusive end below. The
callback survives in three byte-identical groups across the 11 archives.

| Releases | Member | End RVA | SHA-256 prefix | Callback policy |
|---|---|---|---|---|
| 1.1.0 | `dx5.dll` | `1897` | `93cf8f359657f8c8` | Signed height floor of 480. Width/height matching replaces an entry only if its stored depth is no greater than the incoming depth. New-slot count guard at 30. |
| 1.2.0–1.3.1 | `drivers/dx5/dx5.dll` | `1895` | `2c67f48570cd464d` | Unsigned 640×480 floors. Retains width/height matching, now with an unsigned depth comparison, and the 30-count guard. Calculates the memory-derived fields after the depth overrides and writes 3 to both when the quotient exceeds 3. |
| 1.4.0–1.6.1 | `drivers/dx5/dx5a.dll` | `187d` | `ab47edabb85608fb` | Retains the size floors and memory-derived fields. Matching requires width, height and depth. The new-slot count guard rises to 100 and the 640×480-specific depth override disappears. |

The callback's 1.5.1 neighboring code changes occur after its return.
The complete final callback and the separate caller-side seed record are
covered in the [DX5 reference comparison](original-modern-dx5-reference-pair.md#mode-callback-and-selected-initialization-paths).
The count operands describe local insertion guards. The game-facing mode
catalog also depends on the caller and on the display modes supplied by the
renderer API.

### The EXE selects the renamed adapters by path

The original EXE's [indexed renderer table](original-modern-renderer-loading.md#6-original-environment-override-and-selection-wrapper)
contains `softtria.dll` at index 1, `voodoo2a.dll` at index 4 and
`d3da.dll` at index 6. In the 1.1.0 EXE, the
[filename parser](original-modern-renderer-loading.md#early-filename-and-device-suffix-interface-then-driver-key-rename)
instead derives the following paths for well-formed lowercase
`VideoDriver` inputs. Each derived basename matches a root-level member
of the same 1.1.0 archive.

| Input | Derived path | Early renderer class |
|---|---|---|
| `softtri` | `.\softtri.dll` | 1 |
| `voodoo2` | `.\voodoo2.dll` | 4 |
| `dx5` | `.\dx5.dll` | 6 |

Extracting the archive's `nfs3.ini` shows `VideoDriver=Voodoo2`. The
fallback literal at the EXE's profile read is `dx5`. These are two
different sources of selection. Successful DLL loading or hardware
selection requires separate evidence.

#### Voodoo2 fallback depth in 1.1.0

The 1.1.0 file-backed table at PE RVA `fdd4` contains 18 records of 40
bytes each. Reading each as ten little-endian dwords gives zero dimensions
and depth in slots 0 and 17, and depth 16 at offset 8 in all 16 populated
slots. These include the 320×200 and 640×400 entries, so the query path's
640×480 floor cannot be generalized to the fallback.

The legacy setup loop at `60001a09..60001a5d` traverses populated slots 1–16.
It reads depth at `60001a0f` for the memory calculation and updates fields
at offsets 20 and 24. The alternate local write at `60001b73` updates those
same fields. The fallback copies all 18 records at `6000d920..6000d931`.
Together with the explicit depth-16 store on the successful query branch,
this gives static support for both sources of populated 16-bit records.
Later writes, the exact exported mode list under nGlide, and the Alt+P
screenshot consequence remain unverified.

The hosted reference table at the same RVA also has 16 populated records,
all at depth 16. Comparing the width/height pairs shows one substitution:
`1280×1200` in the reference becomes `1280×1024` in 1.1.0. The four
larger modes (960×720, 1024×768, 1280×1024 and 1600×1200) occupy slots
3–6 in 1.1.0. The first two populated slots remain 640×480 and 800×600.
This is file order before the setup loop or game-side selection.

The legacy setup block `60001940..60001b80` is byte-identical between
these two DLLs. Both import `_grQueryResolutions@8` at the same IAT slot.
The observed changes are the new callers that reach the query, the depth
written on that branch, and the fallback table's content and order.
The fallback's 16-bit depth predates the patch.

The companion fallback table at PE RVA `100a4` contains 18 dwords.
Joining each entry to the 40-byte record at the same slot shows that all
15 unchanged width/height pairs keep their lookup value despite the
reordering. The substituted mode also retains token `0d`: the reference
pairs it with 1280×1200 at slot 14, and 1.1.0 pairs it with 1280×1024 at
slot 5. Slots 0 and 17 retain `0` and `1000h` respectively.

The fallback copies this table to `600127c0`. On the inspected retry,
`600021ad` reads a dword by mode index from that table and pushes it at
`600021b4` for the normal Glide open call through `6001101c` at
`600021bc`. Thus the reordered records carry matching lookup values into
the open route. The actual dimensions the provider selects for token
`0d` remain unverified.

The [3dfx Glide 3 header](https://sources.debian.org/src/glide/2002.04.10ds1-12/glide3x/cvg/incsrc/sst1vid.h)
defines token `0x0d` as `GR_RESOLUTION_1280x1024`. The 1.1.0 fallback
therefore brings the adapter's declared dimensions into agreement with
the Glide token it already passed. This establishes the API meaning.
The shipped nGlide provider's internal mapping and successful live
mode creation remain unverified.

#### Fallback tables across the early provider split

The 720-byte record table at PE RVA `fdd4` and 72-byte token table at
`100a4` are byte-identical in seven retained adapters: root
`voodoo2.dll` in 1.1.0, then both `drivers/dgvoodoo/voodoo2.dll` and
`drivers/nglide/nglide.dll` in 1.2.0, 1.3.0 and 1.3.1. Their SHA-256
digests are respectively
`5827c1a7e312a9be6393d39e792b105b9608caa7eb15f5d43803530e89179c34`
and `6635dc5a03d5f287ccd18cf67417441b0d579d5b573397812da536d7df5a9795`.
The 1280×1024 / `0x0d` pairing thus survives the introduction of the
separate nGlide adapter.

The 1.4.0-and-later archive members lack that record at the old RVA and
stride. The [final Voodoo2 comparison](original-modern-glide-reference-identity.md)
traces the final descriptor to runtime-built records at `60013000`.
An absent record at the old offset does not establish that 1280×1024 is
unavailable in those releases.

The destination moved before the fixed fallback disappeared. At
`60001c29`, 1.1.0 loads table base `60012880`; both adapters in the
retained 1.2.0, 1.3.0 and 1.3.1 archives load `60013000`. The three
1.4.0 adapter members retain that address. Read this instruction with
`objdump -d -Mintel --start-address=0x60001c29 --stop-address=0x60001c2e`
on each extracted member.

The [historical producer comparison](original-modern-voodoo-reference-pair.md#historical131-to140-about-calls-retarget-without-changing-its-publications)
shows that the inspected 1.3.1 dgVoodoo helper can still copy the fixed
table into that destination. The inspected 1.4.0 Glide3x helper instead
uses query retries and has no corresponding copy. This dates the pointer
move to 1.2.0 and distinguishes it from the later helper rewrite.

#### Shared adapters after the provider split

In each retained archive from 1.4.0 through 1.6.1, the three
`drivers/{dgvoodoo,glide3x,nglide}/voodoo2a.dll` members are byte-identical
within that archive. The comparison covers 21 extracted DLLs across seven
releases. Thus the 1.4.0 mode-builder result above applies to all three
packaged copies. Provider DLLs and directory configurations can still
differ.

The complete final-sized mode builder at `600018d8..60001b79` and the
413-byte about routine at `60001bb0..60001d4d` are already byte-identical
to final in 1.5.0 and stay so in every retained release thereafter.
Extract each exact archive member and compare those two PE RVA slices
to reproduce the result. This dates the captured instructions only.
Provider binding, configuration and other code outside those spans can
still affect the live mode list.

The 1.4.0→1.5.0 builder change adds a 25-byte sequence at
`60001a0c..60001a25`. It reserves a four-byte output, calls the resolved
`_grGet@12` slot `600110c0` with selector 10 and length 4, and stores
the output dword to both `6000fd24` and `6000fd30`. The caller does not
test the API return before publishing the output. Version 1.4.0 starts
the mode-query setup immediately at that point. The query setup and
record loop shift by 25 bytes in 1.5.0, including the retained 640×480
seed and optional 32-bit insertion. The early cached branch is retargeted
to the moved exit. The selector's provider-specific result and the
downstream effects of those two stores remain open.

Selector 10 is `GR_MAX_TEXTURE_SIZE`, defined as `0x0a` in the
[3dfx Glide header](https://sources.debian.org/src/glide/2002.04.10ds1-12/glide3x/h3/glide3/src/glide.h).
The [Glide reference manual](https://www.bitsavers.org/components/3dfx/Glide_Reference_Manual_3.0_199806.pdf)
defines its output as the maximum supported texture width, in pixels.
The two destinations are offsets `+14h` and `+20h` in the descriptor
returned by `THRASH_about` at base `6000fd10`. The about setup seeds
both fields with 256 at `60001c34` and `60001c5e`. The added query can
therefore replace both defaults with the provider's reported size before
the game receives the descriptor. A decoded direct-operand scan of 1.5.0
found only those initial stores and the two query-output stores. Game
consumers can read the fields through the returned pointer, so the scan
does not establish their downstream effect.
