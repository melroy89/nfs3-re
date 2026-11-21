# Author-hosted original-reference bundle and baseline distinction

## Identity and reproduction

The author directory also hosts [nfs3_orig.7z](https://veg.by/files/nfs3/nfs3_orig.7z). The retained archive is1,087,633 bytes, SHA256 `374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127`. This is an author-hosted reference bundle, **not an authenticated pristine retail distribution**. It contains later nGlide patch files and a wrapper alongside older-looking assets; archive timestamps do not authenticate build dates.

Run `python3 analysis/scripts/audit_author_original_bundle.py` after downloading the archive into the ignored path in [the manifest](evidence/audits/author-original-bundle.json). The script inventories every file, verifies case-normalized member names are unique, hashes all98 members and records PE metadata/exports for the six PE files. It reads archive contents only: no DLL, EXE, registry, batch or compatibility-database file was installed or executed. Existing analysis targets/database were preserved.

| Member category | Count |
|---|---:|
| Menu `.mnu` files |80 |
| HUD `.pos` files |6 |
| EXE/DLL files |6 |
| Other files |6 |
| Total files |98 |

The six PE members are `nfs3.exe`, `d3da.dll`, `softtria.dll`, `voodoo2a.dll`, `eacsnd.dll` and `glide3x.dll`. Presence in this bundle does not establish that all five DLLs came from the same original game release. In particular the nGlide-related files must remain distinct from candidate game renderers.

## Hosted EXE differs from the established supplied original

| Role | Size | SHA256 |
|---|---:|---|
| Established supplied-original baseline |1,589,248 |`b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` |
| EXE in author-hosted original-reference bundle |1,589,248 |`8ace9af9d197a938f0ddd6b013f552104d23b34580b900a52f052ed800938fe2` |

The complete equal-length comparison finds **exactly one differing byte**, file offset `000b579b`, VA `004b639b`. Supplied-original bytes are `75 5a` (JNE rel8); hosted bytes are `eb 5a` (JMP rel8), both targeting `004b63f7`. The surrounding code belongs to the already inspected [original admission helper](original-modern-startup-requirements.md#removed-installation-and-media-admission-helpers). This inventory does not establish who made the edit or its complete runtime consequences.

All other file bytes, including PE headers, match in this comparison. That is useful near-identity evidence, **not** a reason to overwrite the baseline or silently substitute artifacts. Existing original-versus-Modern findings remain bound to supplied hash `b390…d51b`. Any use of the hosted EXE must name its different hash and the branch difference.

## What this enables next

The bundle supplies separately identified candidates for previously missing original-side renderer/artifact comparisons:

| Hosted member | Proposed comparison | Required next evidence |
|---|---|---|
| `d3da.dll` | Final DX5 renderer member | [Pairing and bounded correspondence verified](original-modern-dx5-reference-pair.md); pointed-to table semantics and remaining intervals pending |
| `eacsnd.dll` | Final sound DLL | [All preexisting raw-section bytes identical](original-modern-sound-reference-pair.md); headers/resources differ; runtime effects untested |
| `softtria.dll` | Final software renderer member | [Pairing and raw-depth callback filter verified](original-modern-software-reference-pair.md); remaining code/PE consequences pending |
| `voodoo2a.dll` | Final Glide renderer member | [Three-way pairing and selected byte map verified](original-modern-glide-reference-identity.md); hosted build differs from prior local candidate; semantic follow-up pending |
|80 menus /6 HUD-position files | Corresponding Modern members | [Complete suffix-scoped pairing and HUD literal comparison](original-modern-reference-assets-index.md); menu-control semantics and runtime layouts remain follow-up |

No semantic driver change is accepted merely because files differ or appear under familiar names. These candidates remove an acquisition gap while leaving original-retail authenticity, complete feature attribution and runtime acceptance open. Local backup equality, if later checked, would corroborate file identity rather than authenticate a retail release. The broader original/Modern investigation remains incomplete.


## Reference renderer debug-carrier leads

The [SoftTri debug audit](evidence/audits/softtri-reference-debug.json), reproduced with `python3 analysis/scripts/audit_softtri_reference_debug.py`, now records related trailing-overlay checks under exact artifact hashes:

|Artifact |Trailing bytes |Observed signature |
|---|---:|---|
|Supplied-original game EXE |0 |No trailing overlay |
|Reference `d3da.dll` |26,449 |ELF signature |
|Reference `voodoo2a.dll` |24,054 |ELF signature |
|Reference `softtria.dll` |28,514 |ELF32 carrier; bounded debug extraction documented separately |

Offsets are computed from the end of nonzero-pointer raw PE sections, not by treating BSS size as file-backed data. An absent overlay does not prove absence of debug information inside sections. ELF signatures alone do not establish useful symbols, source code or a supported decoder for the two unparsed DLL payloads.

For SoftTri, the [canonical report](original-modern-software-reference-pair.md#reference-debug-records-recover-names-with34-export-anchors) records173 units,1,034 bounded name records and34 export/address anchors, alongside the stock-reader failure and custom-parser limits. The [DX5/Voodoo extraction below](#dx5-and-voodoo-debug-records-have-independent-export-anchors) now supplies bounded records and independent export anchors; general address/signature application remains unverified. No PE/ELF payload was executed and no target/database bytes changed.


## DX5 and Voodoo debug records have independent export anchors

Run `python3 analysis/scripts/audit_renderer_reference_debug.py`; the [manifest](evidence/audits/renderer-reference-debug.json) pins the same reference archive and both members, preserves every extracted unit/record and records the shared parser's hash. Both payloads have the same four-definition abbreviation layout as SoftTri. The parser accepts that declared extent without adding the missing zero terminator; its bounds/form restrictions remain explicit.

|Reference member |Units |Named records |Independent export anchors |
|---|---:|---:|---:|
|`d3da.dll` |193 |961 |34/34 |
|`voodoo2a.dll` |176 |877 |34/34 |

For DX5, replacing export prefix `_THRASH_` with `_D3D_` finds a debug record for each export; Voodoo uses `_VOODOO2_`. Each listed record independently satisfies stored address+1000h=PE export RVA. The manifest retains stored addresses and exact anchors. This corroborates names for those entries; it does not validate every nonexport address, structure layout or internal ABI.

Together with SoftTri's173 units/1,034 records/34 anchors, these three reference providers now expose **542 units,2,872 named records and102 export anchors** under the bounded parser. Unit and name records include runtime/library material as well as provider code. They do not reconstruct source files, authenticate pristine retail provenance, supply complete types or establish final-patch signatures. A debug name can guide analysis while its contract remains unresolved.

Reuse the [DX5 reference/final report](original-modern-dx5-reference-pair.md) and existing Voodoo loader/driver evidence before assigning semantics. Proposed names must remain tied to the reference hash and checked instruction/data addresses; none were applied to Ghidra. The supplied-original EXE still has no trailing overlay in this check. No target/payload instructions were executed and no executable/database bytes changed.
