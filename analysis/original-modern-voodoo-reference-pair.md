# Voodoo2 reference/final provider: matched interface and difference inventory

## Baselines and reproduction

This pairs `voodoo2a.dll` in the [author-hosted reference bundle](original-modern-original-reference-bundle.md) with final `drivers/glide3x/voodoo2a.dll`. It is distinct from the earlier local `VOODOO2A.DLL` candidate used by the [about/setup investigation](original-modern-renderer-loading.md); that candidate has a different hash and export address. Do not merge their instruction addresses or attribute every candidate difference to this reference.

|Role |Bytes |SHA-256 |
|---|---:|---|
|Author reference |92,662 |`99b978fd6b0e94cca7ef0b671b9be0d630f929ab3901ebddaafa5d121213503b` |
|Official final |69,120 |`f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b` |

Run `python3 analysis/scripts/audit_voodoo_reference_final.py`. The [manifest](evidence/audits/voodoo-reference-final.json) pins archives/members, exports, section metadata, normalized imports and every differing byte interval in the shared code/import/data extents. No DLL or target instruction is executed. Author hosting does not authenticate pristine retail or Future Cop source ancestry.

## What is mapped, and what is not

All34 export names, ordinals, RVAs and forwarders match. Both preferred image bases are60000000h. The [debug-record audit](original-modern-original-reference-bundle.md#dx5-and-voodoo-debug-records-have-independent-export-anchors) independently matches those34 entries to `_VOODOO2_` names in the reference overlay; it supplies no automatic final ABI guarantee.

|Shared file-backed extent |Bytes |Differing byte positions |
|---|---:|---:|
|Code, RVA1000h |51,712 |3,307 across141 maximal contiguous intervals |
|Imports, RVAe000h |2,048 |1,218 |
|Data, RVAf000h |7,680 |363 |

Intervals are an address-based work list, not141 functions/features. This chapter does **not** assign all3,307 code bytes to semantics. Raw import differences likewise do not mean1,218 changed APIs. Normalized imports remove DirectDrawCreate from DDRAW and three GLIDE3X names: `_grCoordinateSpace@4`, `_grQueryResolutions@8`, `_grVertexLayout@12`; no normalized import names are added. Runtime resolution, remaining indirect calls and replacement mechanisms must be checked before claiming those capabilities disappeared.

## Matched about prefix changes only count and table pointer

The260-byte prefix `60001bb0..60001cb4` differs in exactly four byte positions, inside two immediate instructions:

|Publication input |Reference |Final |
|---|---|---|
|MOV ESI at`60001c24` |16 |0 |
|MOV EDI at`60001c29` |`6000fdd4` |`60013000` |

Retained stores at `60001c4a/60001c50` publish these to descriptor`6000fd10` offsets3Ch/40h, cells`6000fd4c/6000fd50`. This establishes the initial count/table publication in this prefix; later enumeration can change count/records. It is not proof of16 valid reference modes versus zero usable final modes.

The reference table pointer targets file-backed data. The final pointer instead falls in its enlarged declared BSS extent. BSS raw-size fields change1a00h→3000h at RVA11000h, with raw pointer0; VirtualSize fields and actual loader mapping remain separately qualified. The old data address is not assumed cleared or unused in final. Preserve required data initialization and pointer provenance instead of treating an exported C function as complete reconstruction.

## Priorities and limitations

First assign changed code intervals to the matched mode producer, provider resolution and initialization paths, reusing the existing about/setup work. Then qualify changed data, callback ABI and static versus dynamic imports. Resources, headers, relocations and reference debug-overlay semantics also need their own scope. The two different legacy baselines must retain distinct labels.

MP140-037 now has partial historical support from the complete131/140 about comparison below. The reference/final inventory remains an incomplete semantic comparison and does not date every changed provider mechanism to140. Source ancestry, device acceptance, rendered effects and race/replay/network compatibility remain unverified. Existing EXEs, saved Ghidra state, raw exports and maintained C are unchanged.


## Historical131 to140 about calls retarget without changing its publications

The expanded [Voodoo audit](evidence/audits/voodoo-reference-final.json) pins131 `drivers/dgvoodoo/voodoo2.dll` and140 `drivers/glide3x/voodoo2a.dll`. Their complete413-byte about bodies `60001bb0..60001d4d` differ in **exactly five byte positions**, all operands of three direct calls:

|Call instruction |131 target |140 target |
|---|---|---|
|`60001d11` |`600012f0` |`600018d8` |
|`60001d2d` |`6000110c` |`60001108` |
|`60001d3e` |`600012f0` |`600018d8` |

The two first/last sites select the mode-producing helper under distinct existing branches; the middle site retargets the local cleanup helper. Target-body semantics and complete provider lifetime are separate from this exact caller comparison. All other about instructions are identical131/140, including its initial count16 and table pointer60013000 publications. The archive directory/name change does not itself prove implementation behavior.

|Inspected baseline |Initial published count |Initial published table |
|---|---:|---|
|Author reference |16 |`6000fdd4` |
|131 |16 |`60013000` |
|140 |16 |`60013000` |
|Official final |0 |`60013000` |

This separates changes previously easy to conflate: the new table pointer already exists in131; the selected about call retargets occur131→140; the initial count0 publication is later than140 in the checked lineage. None of these initial values is a final visible-resolution count. Exact first introduction and every intermediate behavior remain unverified.

**MP140-037 advances vendor-only→partial:** the historical pair has a concrete internal-call refactor example, with exhaustive byte accounting for this one caller. It does not prove that all3,307 reference/final changed code bytes belong to140, that helper semantics are equal or that device/rendering outcomes improve. Existing setup/mode-helper research should be reused for those next target-body checks. No target instructions or Ghidra writes occurred.


## Historical mode producer changes fallback and register contract

The expanded [audit](evidence/audits/voodoo-reference-final.json) captures complete131 producer `600012f0..60001545` (597 bytes) and140 producer `600018d8..60001b5a` (642 bytes), tied to the about call sites above. Their resolver-table rows bind query slots600128c0/600127c0 respectively to `_grQueryResolutions@8`; this establishes the static target identity on successful binding, not an observed provider call.

|Selected route |131 |140 |
|---|---|---|
|Cache guard |DWORD600128cc |DWORD600127d4 |
|Incoming register use |EAX copied to ESI as descriptor; later fallback writes descriptor+3Ch |PUSHAD frame; global capability/count/table state used |
|Query fallback |Zero query result, or selected signed first-record test failing, enters fixed-record fallback |Seeds a640×480×16 candidate through helper600012e8 before query; unsuccessful first attempt changes request fields and retries |
|Fixed fallback writes |Sets descriptor count16; calls60001940; copies72 bytes from600100a4→60012e68 and720 bytes from6000fdd4→60013000 |No corresponding fixed-table copy in this captured helper; retry exhaustion reaches cache/return tail |
|General register preservation |Saves EBX/ECX/EDX/ESI/EDI/EBP; EAX remains working/output state |PUSHAD/POPAD preserves entry general-register values on ordinary return |

The initial query-result value controls stack reservation; a later result is shifted right4 to obtain the number of16-byte records for parsing. Do not substitute an invented API status/count convention for those machine uses.131's selected first-DWORD comparison with255 uses signed JG;140 uses unsigned JA on its first-attempt threshold and separately tracks retry state. On fallback140 resets its stack request, sets bit0 in a local flag, changes the first two request DWORDs toffffffffh and tries again. The flag prevents repeated unsuccessful retries; a successful retry can enter parsing without the first-attempt threshold.

The140 parser interprets low resolution identifiers through a WORD-pair table and other values as packed WORD dimensions, applies its selected640×480 lower bounds, then calls insertion helper600012e8. Optional extension state can request an additional32-bit candidate. These are requested records, not guaranteed insertions or available display modes; the existing final-helper/insertion research supplies a separate later-version contract and must not be copied wholesale into140 without comparison.

Both helpers have cached completion paths, but cache initialization/invalidation and complete provider lifetime remain unverified. In particular,140 can reach its cache flag write after unsuccessful query attempts; that does not establish valid or current mode data. The about caller reloads its descriptor into EAX after the call, so these sites do not establish dependence on the old producer's incidental EAX result. Other callers and hidden register/flag contracts still need inspection before choosing a C interface.

This strengthens MP140-037's partial support beyond a moved call address: selected fallback, register and data-source policies change. Full metadata classification, insertion/capacity ownership, all query outcomes and runtime mode selection remain pending. No target instructions, provider APIs or saved database were executed/changed.
