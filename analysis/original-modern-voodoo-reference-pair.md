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

MP140-037's historical “refactoring” claim remains vendor-only as a release-specific attribution: this reference/final inventory is not a140 introduction proof or a complete semantic comparison. Source ancestry, device acceptance, rendered effects and race/replay/network compatibility remain unverified. Existing EXEs, saved Ghidra state, raw exports and maintained C are unchanged.
