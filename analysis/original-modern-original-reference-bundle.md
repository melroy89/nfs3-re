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
| `d3da.dll` | Final DX5 renderer member | Explicit member pairing, exports/layout and bounded function correspondence |
| `softtria.dll` | Final software renderer member | Same; packed/changed layouts must not be treated as address-equal functions |
| `voodoo2a.dll` | Final Glide renderer member | Same; distinguish game renderer from wrapper DLL |
|80 menus /6 HUD-position files | Corresponding Modern members | Case-normalized pairing, duplicate/absent entries and asset-format-aware field comparison |

No semantic driver change is accepted merely because files differ or appear under familiar names. These candidates remove an acquisition gap while leaving original-retail authenticity, complete feature attribution and runtime acceptance open. Local backup equality, if later checked, would corroborate file identity rather than authenticate a retail release. The broader original/Modern investigation remains incomplete.
