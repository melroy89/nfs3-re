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

## Hosted-reference/final about and mode-construction comparison

The audit now captures both complete413-byte `THRASH_about` bodies `60001bb0..60001d4d`, the complete624-byte reference mode helper `60001940..60001bb0`, its132-byte query helper `600018b0..60001934`, and the already studied673-byte final helper `600018d8..60001b79`. Reference and final helper ranges overlap differently; they must not be paired by one shared start address.

Both about entries use descriptor `6000fd10` and return early if its first DWORD is already nonzero. In the setup path:

| Operation | Hosted reference | Final Modern |
|---|---|---|
| Initial descriptor+3ch count |16 |0 |
| Descriptor+40h table pointer |6000fdd4 |60013000 |
| Normal helper target |60001940 |600018d8 |
| Alternate branch helper target |60001940 |600018d8 |
| Null tests before normal query path |Checks slots60011010 and600110c0 |Replaces these tests with a direct jump to the query setup |
| Normal path surrounding calls |Calls slots60011010,600110d8,600110d4, then mode helper, then60011014 |Keeps the argument4 call through600110d4, invokes new mode helper and jumps over the other old calls |
| Later cleanup call target |60001560 |60001108 |

The complete about body has six maximal differing-byte intervals in the existing map, covering these pointer/count, guard, call and cleanup changes. The unchanged descriptor cache guard must remain distinct from the final mode-builder's own once-only state. Setup values are not a claim that every subsequent failure/success path publishes a fully populated usable list. Import/resolver failure contracts and cleanup helper semantics remain separately qualified.

### Fixed reference records already use a query helper

The reference table at6000fdd4 contains17 file-backed40-byte records: zero record0, then16 fixed width/height/depth entries. The captured helper iterates indices1..16. Their dimensions are:

| Index | Width×height | Stored depth before helper |
|---:|---|---:|
|1 |640×480 |16 |
|2 |800×600 |16 |
|3 |320×200 |16 |
|4 |320×240 |16 |
|5 |400×256 |16 |
|6 |512×384 |16 |
|7 |640×200 |16 |
|8 |640×350 |16 |
|9 |640×400 |16 |
|10 |960×720 |16 |
|11 |856×480 |16 |
|12 |512×256 |16 |
|13 |1024×768 |16 |
|14 |1280×1200 |16 |
|15 |1600×1200 |16 |
|16 |400×300 |16 |

Other initial fields differ between records; the manifest retains all ten DWORDs per record, including eligibility/buffer-related fields rather than assuming every entry is active. The helper queries capability/string slots, derives a memory-like quantity, and updates the existing records. This is not arbitrary insertion of provider-returned dimensions into a newly grown list.

Its subordinate `600018b0` uses the record index to read an enum from600100a4, forms a four-DWORD query, and calls thunk6000d89a twice: first with a null output and then, on a nonzero-size/successful-allocation path, with allocated storage. The thunk is explicitly bound through its static IAT entry to `_grQueryResolutions@8`. The helper scans16-byte returned records and keeps the maximum signed result DWORD at+8, with zero returned on its inspected size/allocation failure paths. Full provider field meanings, malformed result sizes and allocator contracts are not inferred from the API name alone.

Thus the reference already queries resolution-related capability data, but its about path begins with fixed dimensions and16 count. The final helper instead constructs the [query-driven sorted list](original-modern-dll-candidates.md#mode-producing-helpers-fixed-records-versus-inserted-records), using the separately verified dynamic query binding and insertion helper. Reuse that final-side mechanism and its [extra-slot boundary qualification](original-modern-dll-candidates.md#extra-slot-boundary-checked-against-the-executable); the hosted reference side is now independently checked rather than borrowed from the different local build.

This establishes a substantive **fixed-record update versus list-construction** difference for the hosted/final pair. It does not establish all supported dimensions, successful rendering/Z-buffer use, a trusted Future Cop/NFS III lineage or historical introduction. The fact that query calls exist in both versions must not erase the changed use of their results.

## Loader and cleanup lifecycle differ

The audit now captures the complete hosted-reference loader `60001020..60001552`, module-release helper `60001560..6000158d`, final loader `60001020..60001107` and final shutdown gate `60001108..6000111e`. It verifies imported `LoadLibraryA`, `GetProcAddress` and `FreeLibrary` slots in both DLLs, plus final resolver-table bindings for Glide initialization/shutdown.

| Boundary | Hosted reference | Final Modern |
|---|---|---|
| Library acquisition |Calls LoadLibraryA with bare `glide3x.dll`, stores handle at6000fd0c |Checks saved handle first; on empty handle tries an assembled module-directory path, then the bare name |
| API binding |Unrolled GetProcAddress calls store individual slots; the captured successful-load path does not reject each zero lookup |Walks required name/slot table and rejects the first zero lookup |
| Binding failure |Later callers have their own partial slot guards; complete provider admission not implied |Frees the newly acquired handle and returns0; earlier slot writes are not rolled back by this local failure block |
| Initialization |About performs the previously listed initialization/callback operations around its helper |Loader centralizes resolved Glide init/error-callback calls behind cell600127d0 |
| Successful loader return |Returns1 after the captured unrolled binding sequence |Writes0/1 into saved EAX's PUSHAD slot, restores other general registers and returns |
| About cleanup |Module-release helper conditionally FreeLibrary(handle), then clears6000fd0c |Shutdown gate conditionally calls `_grGlideShutdown@0`, then decrements600127d0; it does not locally FreeLibrary or clear6000fd0c |

Final slot60011010 is bound to `_grGlideInit@0`;60011014 to `_grGlideShutdown@0`. These are proven resolver relationships, not names guessed from adjacent strings. The hosted-reference loader's corresponding name pointers and stores are captured too; its old about path separately calls shutdown before invoking its module-release helper.

This is **centralized API initialization/shutdown with retained module acquisition**, rather than an equivalent helper moved to a new address. It should not be called a general reference-counting implementation: when600127d0 is already nonzero, final loader skips initialization and returns1 **without incrementing it**. The increment runs only on the zero-to-initialized path. Cleanup decrements any nonzero value. Under zero initial state and ordinary serialized entry/cleanup pairs it behaves as a0/1 latch; arbitrary nesting, concurrent/reentrant calls and other state mutation are not validated.

All four exact literal operands for600127d0 in the complete final file occur in these two helpers. This narrows direct ownership but does not exclude computed/external aliases or prove runtime initialization. The state lies in the expanded uninitialized-storage extent; do not invent a file-backed initial DWORD. No normalized scalar return is assigned to the shutdown helper: its EAX can depend on the incoming state and underlying shutdown call.

The lifetime distinction also fits the static-import difference: the reference has a Glide3x import descriptor, whereas final uses dynamic resolution for the inspected interface. A reference FreeLibrary call does not by itself prove unloading/dangling function pointers, because other module references—including static dependencies—can retain the provider. Conversely, retaining the handle in this final helper is not proof of a leak, permanent lifetime or absence of another unload path. Windows/Wine reference behaviour and actual provider identity were not observed.

The final pathname path, required-provider completeness, partial-bind failure slot contents, module-detach cleanup and every init/shutdown caller remain separate follow-ups. No initialization, callback, unload or other target code was executed.

## Entry callback supplies the module-directory handle

The audit now follows the actual PE entry rather than assuming that the directory lookup uses this DLL's handle. Both PE headers specify entry RVA4342h, whose retained five-byte jump reaches `60004ab0`. The complete409-byte CRT wrapper `60004ab0..60004c49` and its four-entry reason table at60004aa0 are identical in the hosted reference and final driver.

The wrapper reads the three incoming arguments into ESI/EDI/EBP and passes them in the same order to user callback `60001010`. Under the normal32-bit Windows DLL-entry convention these are module instance, notification reason and reserved argument. Its reason table is:

| Reason value | CRT target |
|---:|---|
|0 |60004bf9 |
|1 |60004af3 |
|2 |60004ad1 |
|3 |60004bdc |

Each ordinary selected route reaches the user callback through its captured call site, subject to the wrapper's runtime-preparation/error gates. This is local linkage, not a claim that every callback runs after every possible CRT failure.

The reference callback `60001010..60001018` simply returns1 with `RET 0ch`. Final callback `60001010..6000101f` loads its first stack argument, stores it at **600127cc**, then returns1 with the same cleanup. It does not inspect the notification reason. Thus the final module-instance producer is explicit; this is not an anonymous data-held pointer inferred from a filename string.

The only two exact literal operands for600127cc in the complete final file are the callback store and loader's pushed API argument. The latter feeds verified import `GetModuleFileNameA` at6000e1ec. Together these establish the ordinary self-module filename input used to form the directory-prefixed Glide load attempt. They do not validate every API return/path length, prove the backward separator scan is safe on failed/truncated input, or observe the actual Windows/Wine provider selected by either attempt.

For notification0, the CRT wrapper calls user callback at `60004bfc` and then continues its retained runtime-finalization path. The final callback itself only records the module instance; it does **not** invoke the Glide shutdown gate, FreeLibrary or module-handle clearing. This closes the question of direct cleanup in the changed callback, while leaving the wrapper's optional indirect callback at600105a4, registered CRT finalizers, other export callers and process-exit behaviour unqualified. No global absence of unload/cleanup follows.

This is another concrete paired change: a previous always-success callback now also supplies the module-instance state needed by Modern's directory-relative dynamic loading. It is not a new whole-driver detach guarantee. Executable bytes and saved Ghidra state were preserved; no notification or loader API was invoked.

## Next required comparison

The about/count/pointer/helper changes and reference fixed/query machinery are now traced above. The local loader/cleanup change is also traced above; next qualify partial-bind failure consumers, indirect/registered detach finalizers and other callers, then select another changed function from the paired map, retaining the already verified final insertion/extra-slot limits. Do not repeat the local-candidate baseline substitution.

**Done:** three artifact identities, export correspondence, static dependency differences and selected paired raw-region map. **Also verified:** complete about local differences and reference fixed-table/query contract. **Pending:** remaining hosted/final function/ABI/data comparisons, transitive failure/registered-finalizer lifetimes, authenticated lineage, historical introduction and runtime rendering. No release-note claim is promoted solely by this inventory. Existing EXEs/database, raw exports and maintained C remain unchanged.
