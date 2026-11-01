# Glide renderer: three distinct baselines and a new paired byte map

## Why this distinction matters

The author-hosted bundle's `voodoo2a.dll` is **not** the local uppercase `VOODOO2A.DLL` used by the earlier [legacy-candidate analysis](original-modern-dll-candidates.md#voodoo-about-descriptor-setup). Their export names agree, but all34 exported function RVAs differ. Earlier fixed-table/descriptor findings remain bound to that local candidate and must not be relabelled as findings about the hosted reference.

Run `python3 analysis/scripts/audit_glide_reference_identity.py`. The [audit](scripts/audit_glide_reference_identity.py) verifies both archive hashes, all three DLL hashes and PE metadata, then records the selected reference/final raw-region differences. [Manifest](evidence/audits/glide-reference-identity.json). No DLL was loaded or executed.

| Role | Bytes | SHA-256 |
|---|---:|---|
| Local legacy candidate |93,382 |`f65f00e6fa6a5a67e11ff38d661b3d493474d0e075c9183a7b244b1143cea88e` |
| Author-hosted reference |92,662 |`99b978fd6b0e94cca7ef0b671b9be0d630f929ab3901ebddaafa5d121213503b` |
| Official final Glide driver |69,120 |`f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b` |

The hosted bundle is mixed and is not an authenticated pristine retail distribution. Its filename must not determine which game/build supplied each member. In particular, the hosted reference resource reports FileVersion `1998.09.11.0041`; final Modern's resource attributes its base to Future Cop L.A.P.D. with the same version suffix. Those are useful metadata leads, not independent proof of lineage or authenticated build dates. The final driver resource's ProductVersion `1.3.0` is a component label, not the containing final package's1.6.1 identity.

## Export correspondence

Hosted reference and final Modern match all34 export names, ordinals, RVAs and forwarder fields. Both use preferred image base60000000. Selected examples:

| Export | Local legacy candidate | Hosted reference / final |
|---|---|---|
| `_THRASH_about@0` |60001a60 |60001bb0 |
| `_THRASH_init@0` |60001d50 |60001eb0 |
| `_THRASH_setstate@8` |60002790 |60002ab0 |

This supports targeted same-address inspection of the hosted/final pair, but does not establish equal function boundaries, bytes or ABI contracts. Conversely, all34 changed local/reference RVAs are relocation/correspondence facts, not34 changed features.

## Static dependency distinction

The hosted reference statically imports `DDRAW!DirectDrawCreate` and three Glide3x symbols:

- `_grCoordinateSpace@4`
- `_grQueryResolutions@8`
- `_grVertexLayout@12`

The local legacy candidate has the DirectDraw import but no static Glide3x import descriptor. The final driver has neither static DDRAW nor Glide3x import descriptors. Full imported-symbol inventories for all three files are retained in the manifest.

This makes the reference's query API presence an existing baseline fact; it must not be called a Modern-only API merely from the earlier local-candidate comparison. Import presence does not prove an API is called, and absence does not prove an interface is unused. The final driver's [already traced dynamic Glide bindings](original-modern-dll-candidates.md#dynamic-glide-bindings-behind-the-mode-builder) remain relevant; raw static dependencies and proven dynamic routes are different evidence.

## Hosted-reference/final region map

The first three file-backed regions have matching RVAs and raw sizes:

| Region | Bytes compared | Differing bytes | Maximal differing-byte intervals |
|---|---:|---:|---:|
| Code section, including padding |51,712 |3,307 |141 |
| Import section |2,048 |1,218 |207 |
| Initialized data |7,680 |363 |138 |

All intervals contain both byte strings and preferred-image VAs in the manifest. These are localization aids, not function boundaries, counts of semantic changes or complete whole-file coverage. The final BSS extent and later section RVAs also differ; the header/resource/relocation/overlay consequences are not fully interpreted here. VirtualSize0 and raw-pointer0 BSS retain their metadata meanings rather than invented file-backed zero contents.

## Next required comparison

The first semantic follow-up is the same-address hosted/final `about` and mode-table construction: establish which fixed/query machinery was already present in this reference, then locate Modern's actual modifications. Reuse the earlier final-driver insertion and dynamic-binding evidence, while rechecking the reference side rather than importing the local candidate's assumptions.

**Done:** three artifact identities, export correspondence, static dependency differences and selected paired raw-region map. **Pending:** hosted/final function/ABI/data comparisons, authenticated lineage, historical introduction and runtime rendering. No release-note claim is promoted solely by this inventory. Existing EXEs/database, raw exports and maintained C remain unchanged.
