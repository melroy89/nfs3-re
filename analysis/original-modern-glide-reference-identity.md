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

## Internal provider failure is not a null about result

The extended audit now pins the official EXE and captures its descriptor-validation tail `004f84d9..004f8513` and complete mode enumerator `004bed90..004bedca`. It connects the driver-local failure branch to existing [EXE loader contracts](original-modern-renderer-loading.md#3-descriptor-checks-differ), without running a missing-provider test.

On the inspected final driver's **cold about path**, descriptor setup occurs before the internal Glide loader call. It writes the nonzero descriptor marker, checked field+8=`68h`, count+3ch=0 and table pointer+40h=`60013000`. If internal loader `60001020` returns0 normally, the test at `60001ccd` branches to the descriptor-return epilogue `60001bc6`: EAX becomes `6000fd10`, **not zero**. EBP remains the descriptor across that loader's PUSHAD/POPAD contract.

| Layer | Local failure/result meaning |
|---|---|
| Internal Glide acquisition/binding helper |Returns0 on its inspected load/required-bind failure paths |
| THRASH about export |On this cold failure branch returns the prepared nonnull descriptor with zero count |
| EXE renderer loader |Rejects null descriptor or+8 mismatch; accepts this pointer/field combination without checking count here |
| EXE mode enumerator |Reads+40h pointer and+3ch signed count, starts index1 and exits when index>count; zero count calls neither eligibility helper nor supplied mode callback |

The descriptor therefore passes the **local descriptor-validation gate** even though internal provider setup failed. This is not proof that later renderer initialization succeeds, that a mode is selected, or that no higher-level driver fallback occurs. The earlier mandatory34-export binding requirement still applies before the EXE reaches this about call; it is a different layer from the driver's internal Glide binding table.

The nonzero descriptor marker is also its fast-return guard on subsequent about calls. With no intervening state changes, another about call returns the same descriptor without retrying the internal loader or mode helper. Other exports, cleanup/initialization callers and external writers may alter the state; no irrecoverable-failure or universal retry claim is made. Existing partial binding-slot rollback limits remain relevant separately.

This explains why “loader returned0,” “about returned null,” “EXE accepted a descriptor” and “usable display modes exist” cannot be collapsed into one success Boolean. Preserve these separate contracts in future reconstruction. No provider failure, loader API or target instructions were executed.

## THRASH init retries provider setup and has a separate failure channel

The audit now compares complete hosted-reference init body `60001eb0..60001f92` (226 bytes) and final body `60001eb0..60001f8c` (220 bytes), plus the official EXE platform-init ranges and their direct callers. Export-binding row004f8418 explicitly maps `_THRASH_init@0` to slot009ef978.

The shared init prefix first checks initialized-bit0 at6000fca4. If set, this body returns0; otherwise it prepares its retained float table/event/callback state and calls internal loader60001020 at60001f03. A zero loader result reaches60001f0c and returns the initially zero EBX through EAX. This call is **independent of the about descriptor's nonzero-marker fast path**, so an earlier failed about call does not by itself prevent another provider-acquisition attempt here. Actual re-entry still depends on the retained initialization-bit gate and other callers/state.

On the admitted successful-provider path, reference init directly calls Glide init/error-callback slots, while final jumps over those now-centralized operations. Its mode-helper call changes60001940→600018d8. Reference's tail calls the shutdown slot60011014 before returning; final removes that tail call. Successful status remains derived from display/capability operations, not an invented always1 return. The final loader's own init latch and the separate driver initialized bit must not be merged into one variable.

### EXE consumers test the init result

| Location | Observed branch |
|---|---|
|0052473a |Calls THRASH init through009ef978 |
|00524740..00524744 |Zero result branches to0052479a, bypassing the local success path |
|0052479a..005247ab |Calls cleanup004cdaa0, then returns the current byte0056aff0 in EAX |
|0051763e..0051764b |Mode initializer calls platform helper005246a0; zero result branches to its return epilogue0051777e, before selectdisplay/descriptor refresh/mode setup |
|004b5aa3..004b5ab6 |Startup tests mode-initializer result; zero supplies `Cannot init the thrash driver.` to diagnostic004b570c |

The platform helper's early nonzero-byte gate and success path remain in the captured ranges. Its failure return is **not blindly normalized to0 after cleanup**: it reloads0056aff0. Ordinary cold-entry conditions start that byte at0, but all transitive cleanup/message/callback writers are not qualified here. The table therefore establishes error-branch linkage and a conditional outward zero path, not every runtime cleanup result or termination consequence.

This completes an important distinction from the earlier empty-descriptor finding: passing local about validation does not bypass every later initialization check, and cached about failure is not proved globally unrecoverable. Conversely, a later retry opportunity does not establish successful provider recovery, valid modes, rendered output or complete fallback policy. No provider absence/recovery scenario, diagnostic dialog or target instructions were executed.

## Selected-mode activation and optional extended open

The audit now retains complete paired `_THRASH_setvideomode@12` bodies **`60002400..600024d7`**, complete callbacks **`60002390..600023f3`**, and workers starting **`60002110`** (reference ends exclusive60002389 including outlined tails; final ends60002367). The215-byte exported bodies and99-byte callback bodies are respectively byte-identical. Their direct/callback calls both reach the changed worker; unchanged wrappers do not establish unchanged activation.

| Operation | Hosted reference | Final Modern |
|---|---|---|
| Ordinary resolution source | Fixed DWORD enum table600100a4 indexed by argument1 | Eight-byte sidecar at60012cd0+8*index |
| Special resolutionffh admission | Tests6000fd7c==1 and6000fcfc!=0 | Tests6000fca8!=0 and6000fcfc!=0; meanings of these differing gates not assigned here |
| Open call | Slot6001101c only | Extra selector0 calls6001101c; nonzero calls optional slot600127c8 |
| Failed special open | Tries fixed selected enum | Returns to sidecar resolution load and retries; ordinary non-ff failure returns0 |
| Dimensions when grGet selector26h returns0 | Uses selected fixed record width/height | Uses selected constructed record width/height |
| Selected depth state | Existing setup path through60001940; no equivalent new depth publication asserted | Copies record+8 to600127d8; depth32 selects600127dc=5/mask6000fcb0=00ffffffh; other depths select4/0000ffffh |

Both normal-open slots are verified as **`_grSstWinOpen@28`**: reference's name literal6000f044 feeds its retained resolver/store600010b9, while final's required name/destination table explicitly binds6001101c. Final's dimension query slot600110c0 is `_grGet@12`. The [existing optional-binding audit](original-modern-dll-candidates.md#dynamic-glide-bindings-behind-the-mode-builder) traces the `grSstWinOpenExt` lookup/result600127c8. These names identify static binding intentions, not the actual loaded provider or its behavior.

### Constructed record and sidecar stay paired

Insertion600012e8 uses a zero-based insertion slot, but writes the40-byte record at `60013028+40*slot` and its two-DWORD sidecar at `60012cd8+8*slot`: both correspond to published **index=slot+1**. The sidecar copies candidate+0ch (resolution payload) and+10h (extra selector); its entries move alongside sorted records. Therefore the worker's index addresses corresponding record and sidecar entries, under the existing valid-index/construction preconditions.

The queried16-bit candidate supplies extra selector0. Only when optional slot600127c8 is nonzero does the builder additionally insert depth32 with extra selector5 at60001b44..60001b55. Worker6000215d tests this stored selector, not the extension pointer. Ordinary arguments are `(window,resolution,0,0,0,arg2,arg3)`; extended arguments add the stored selector before arg2. Both paths may clear arg3 when it is nonzero and signed arg2 exceeds selected record+18h. Raw argument numbering avoids assigning undocumented provider meanings to every zero/count.

After a successful open, final chooses record `60013000+40*index`, stores queried or fallback dimensions into6000fcc8/6000fccc and publishes its depth/format/mask as above. Its success tail sets driver flag bit1 and returns1; open failure returns0. Numerous later state calls remain in the captured worker, but their transitive effects are not fully interpreted by this increment.

**Verified:** changed resolution/extra-selector consumption, ordinary/extended call selection, special-resolution retry, dimension fallback and local depth-dependent state. **Unresolved:** provider constants/ABI semantics beyond the captured call shape, all index producers, subsequent state/render effects and historical introduction. The worker contains no local index bound or extension-null check; constructed-candidate admission is a dependency. A special retry is not universally bounded if a corrupt/exceptional sidecar itself retainsffh. Callback/event code equality does not prove synchronization, reentrancy or successful delivery. This is static evidence for a32-bit activation path, not universal32-bit rendering or Z-buffer support. No DLL/API/target instructions were executed.

## Hardware-name classification explains the special-resolution gate

The same audit now decodes final's five-row table **`600018b0..600018d8`**, captures its query/scan/byte-store prefix and compares the complete retained string helper **`600047c0..60004861`**. Slot600110c4 is verified `_grGetString@4`; both mode helpers pass selectorA1h. The comparison is exact case-sensitive string equality, not substring matching. The table's last null-name row supplies the unmatched-name default; this does not make a null returned string safe to compare.

Final unpacks one DWORD payload into three separate **BYTE** stores: low byte to descriptor class6000fd7c, next byte to6000fca8, next byte to6000fcc0. Reference uses explicit string branches and DWORD stores. The resulting local classifications are:

| Provider-returned name | Reference descriptor class | Final descriptor-class byte | Final6000fca8 byte | Final6000fcc0 byte |
|---|---:|---:|---:|---:|
| Voodoo Graphics |0 |0 |0 |1 |
| Voodoo Rush |1 |1 |1 |0 |
| Voodoo2 |2 |2 |0 |1 |
| Voodoo Banshee |3 |3 |1 |0 |
| Any other valid string |0 |4 |1 |0 |

Reference sets6000fca8 to1 in its Rush/Banshee branches but does not explicitly clear it in every other branch. Final writes its low byte for every selected table row. This supplies explicit low-byte classification rather than proving universal state normalization: the actual mode-opening comparison reads a **DWORD**, not a BYTE. Both images' file-backed initial DWORD6000fca8 is0; cold-path examples assume its upper bytes remain zero. Other aliases/writers and all reinitialization sequences are not exhaustively qualified.

Under that ordinary initialized-state premise and the shared6000fcfc!=0 condition, reference's `descriptor_class == 1` opens first with resolutionffh for **Rush**. Final's `6000fca8 != 0` admits **Rush, Banshee and unmatched names**. This directly explains the changed gate captured in the preceding section. It is a provider-name policy, not proof of a physical GPU, a particular wrapper being loaded, or successful special-resolution support. Final unmatched classification4 also differs from reference's fallback0; consumers of that classification beyond the inspected mode path remain a separate question.

Preserve the packed table, byte-store widths and DWORD consumers in a reconstruction. Replacing them silently with three Boolean variables would erase both the fallback classification and upper-byte/lifetime dependencies. No name query, provider or target code was executed; historical introduction and rendered consequences remain unresolved.

## Selected depth also changes lock and rectangle-transfer contracts

The paired audit now captures complete exports at60003270 (`_THRASH_lockwindow@0`),60003350 (`_THRASH_unlockwindow@4`),600033a0 (`_THRASH_readrect@20`) and60003410 (`_THRASH_writerect@20`). Lock bodies span214 bytes each; unlock bodies76 bytes each and match exactly. Read bodies are103 reference/88 final bytes; write bodies107 reference/110 final bytes. Retained names/entry addresses establish correspondence, not output equivalence.

| Contract | Hosted reference | Final Modern |
|---|---|---|
| Read/write row-stride argument | Low32 bits of `2*argument3` | Low32 bits of `(unsigned_selected_depth >> 3)*argument3` |
| Write format argument |0 |5 when depth==32, otherwise0 |
| Allocated lock descriptor+08h | Fixed4 | Current600127dc, set4/5 by mode activation |
| Unlock body | Calls provider unlock operations, frees descriptor, optional callback0 | Identical instructions |

With valid depth16/32, the final stride factor is2/4 respectively; reference always uses2. This links the previously traced selected-depth producer600021ef directly to transfer arguments, rather than treating depth32 as unused metadata. No local validation in these wrappers establishes that arbitrary stored depths are valid. x86 SHR is logical and IMUL keeps low32 bits; a C reconstruction must make wrapping explicit instead of introducing signed-overflow undefined behavior.

Required final bindings verify slots60011078=`_grLfbLock@24`,6001107c=`_grLfbUnlock@8`,60011080=`_grLfbWriteRegion@36` and60011084=`_grLfbReadRegion@28`. Read forwards `(selected_buffer,arg1,arg2,arg3,arg4,pitch,arg5)`. Write forwards `(selected_buffer,arg1,arg2,format,arg3,arg4,1,pitch,arg5)`. The raw call shape is verified; full provider format definitions and actual loaded implementations remain outside this comparison.

Lock retains the24-byte allocation and writes six DWORDs: offsets00h/04h copy provider result slots from its stack-local structure;08h is the format field;0ch/10h are stored width/height;14h is the selected buffer. Modern changes08h from fixed4 to the mode-dependent global. This does not prove all provider-produced lock information is honoured, or that the returned memory is valid. Both bodies still make a second lock call whose result is not checked locally. Allocation/failure ownership must be preserved and qualified, not silently repaired as part of reconstruction.

Read/write save the provider result across the optional callback0 and return it. Their callback1/0 bracketing is not a synchronization/reentrancy guarantee. **Verified difference:** depth-dependent stride, write-format selection and returned lock format. **Still unverified:** transferred pixels, endian/channel interpretation, caller buffer sizes, provider failures, full buffer lifetime, runtime32-bit success and historical release attribution. No target or provider code was executed; these findings do not establish replay/multiplayer compatibility or a precision-policy change.

## Depth clear value survives the changed state-setting routes

The paired audit captures the complete **1,982-byte setstate body `60002ab0..6000326e`** in both DLLs. All61 differing bytes lie inside two envelopes, `60003068..6000308a` and `600030b9..600030dc`; the manifest retains every maximal changed interval. This accounts for all changed bytes in this function, not every transitive state effect.

Both envelopes belong to **state selector4**, payload2 and payload1 respectively. Original writes `0000ffffh` into **6000fcb0**, calls slot60011068 with1 and returns1. Modern removes those local stores, still calls that slot with1 and returns1. Payload0 takes a retained different route; unsupported values are not converted into these admitted cases. The earlier comparisons/branches and the remaining state body are byte-identical.

The required bindings identify60011060=`_grDepthBufferMode@4`,60011064=`_grDepthBufferFunction@4`,60011068=`_grDepthMask@4` and60011030=`_grBufferClear@12`. The clearwindow path at60002860 passes **`(DWORD[6000fcac],0,DWORD[6000fcb0])`**. The [3dfx Glide3 reference manual](https://www.3dfxglide.com/download/GL3REF.PDF) defines these positions as color, alpha and depth; the third is an unsigned depth-clear value whose use depends on enabled buffer writes. This API contract supplies the meaning missing from the earlier raw “mask” label; it does not identify the running provider or prove a successful clear.

Reference's clear path falls through alignment instructions to the shared return at60002880. Final uses direct PUSH memory operands and returns at60002874. The argument values are locally equivalent for matching globals, but register clobbers differ (reference loads EDX/ECX; final does not), and calls under changed depth state need not produce equal output.

Combined with mode activation, the local chain is now concrete: final selects depth-clear value**ffffh for non32-bit modes** or**ffffffh for depth32**, and these selector4 branches no longer replace it withffffh. This preserves the selected value through these local branches, assuming no other writer or transitive provider mutation. It is not proof of every global writer,24-bit Z-buffer operation, correct rendered depth, full ABI equivalence or a historical release date. No provider, target instruction or clear operation was executed. Do not silently reintroduce the reference's fixed store when reconstructing Modern.

## Texture tables expand from256 through2048

Complete `_THRASH_talloc@20` body **`600024e0..60002654`** (372 bytes) and upload-level helper **`60002660..600026dd`** (125 bytes) are now compared. Each has exactly six differing bytes, confined to two table-address operands; every other body byte matches. These operands are data-table addresses, not changed provider bindings.

| Table | Hosted reference | Final Modern | Verified contents |
|---|---|---|---|
| Exponent-to-LOD byte table |600100f4,9 bytes |6000fe34,12 bytes | Integers0..8 versus0..11 |
| Square-size DWORD table |60010110,9 DWORDs |6000fe40,12 DWORDs |4^exponent, through65,536 versus4,194,304 |
| Side-length DWORD table |60010134,9 DWORDs |6000fe70,12 DWORDs |2^exponent, through256 versus2048 |

The allocator redirects its two byte-table reads at60002523/60002534. The upload loop redirects its side-length read at60002686 and square-size-derived buffer step at600026c1; the latter uses a base four bytes beyond the square table with an index decremented by four, retaining the corresponding exponent entry. Existing aspect/format tables and provider-call instructions in these bodies remain unchanged.

For admitted power-of-two dimensions, the retained integer-to-binary32/exponent extraction maps512,1024,2048 to9,10,11 exactly. The final tables supply these entries; the reference's documented nine-entry tables do not. Neither routine adds an upper-bound check merely because the tables become larger. General non-power-of-two/invalid input behavior, x87 state and source-buffer bounds remain dependencies. Reads beyond a reference table must not be described as a clean original rejection without further evidence.

The [existing renderer capability investigation](installed-renderer-capability-inventory.md) and [EXE texture-limit comparison](original-modern-texture-limits.md) explain memory admission, producers and configured extent reduction; reuse their qualifications. This new paired evidence provides **partial support for MP150-011**: final Glide tables and their consumers cover512/1024/2048 where the reference tables end at256. It does not date the change to1.5.0 or establish actual larger-texture allocation, provider acceptance, every upload route, source layout or rendered quality. No DLL, texture or target instructions were executed.

## Historical texture-table boundary:1.4.0 to1.5.0

The later `python3 analysis/scripts/audit_glide_texture_release_boundary.py` compares exact member **`drivers/glide3x/voodoo2a.dll`** from author-hosted [1.4.0](https://veg.by/files/nfs3/nfs3_modern_patch_v1.4.0.7z) and [1.5.0](https://veg.by/files/nfs3/nfs3_modern_patch_v1.5.0.7z) archives. The [manifest](evidence/audits/glide-texture-release-boundary.json) retains full archive/member SHA-256s, complete allocation/upload bodies, table bytes/values and changed intervals. Archive labels/source are release correspondence, not publisher-signature authentication or development-history proof.

| Named package | Archive SHA-256 prefix |Driver SHA-256 prefix |Table entries / maximum side |
|---|---|---|---|
|1.4.0 |8181722b8aadd9b7 |67764a56917fd93f |9 /256 |
|1.5.0 |de6cbbbce4b77765 |bea4abc9ff9b3e54 |12 /2048 |

All named export addresses match between this pair. The two complete functions still differ by only six bytes each, at the same table-address operands identified in the reference/final comparison.1.5.0's tables contain exponents0..11, square sizes4^exponent and sides2^exponent;1.4.0 ends at exponent8. Both1.5.0 function-body hashes equal the previously pinned final bodies, while the whole DLL hashes differ.

This establishes the specific **shipped1.4.0→1.5.0 table/consumer change** for MP150-011, superseding the preceding original/final-only historical limitation. It does not establish earlier beta/branch history, other driver variants, provider support, successful huge-texture uploads or rendered quality. The release claim remains partial because actual operation is untested. No archive content was installed, loaded or executed.

## Historical initialization boundary:1.3.0 to1.3.1

Run `python3 analysis/scripts/audit_glide_init_release_boundary.py`. The [four-member manifest](evidence/audits/glide-init-release-boundary.json) pins both author-hosted archives and **both** named members, `drivers/dgvoodoo/voodoo2.dll` and `drivers/nglide/nglide.dll`. It captures complete loaders, new cleanup latches, old cleanup RET and the about/is/init/close/restore/mode-worker envelopes. No target instructions or provider calls are executed.

| Member |1.3.0 direct init/shutdown sites |1.3.1 direct init/shutdown sites |New shutdown helper |
|---|---|---|---|
|dgvoodoo/voodoo2.dll |4 /6 |1 /1 |6000110c |
|nglide/nglide.dll |4 /6 |1 /1 |60001110 |

The name/destination tables independently bind60011010 to `_grGlideInit@0`,60011014 to `_grGlideShutdown@0` and600110d8 to the error callback interface. Counts are complete file searches for the captured direct CALL encodings, corroborated by their code envelopes—not observed runtime frequencies or proof of every indirect target.

In1.3.0 both loaders already test cached module handle6000fd0c, and old cleanup60001560 is a RET. Therefore the1.3.1 optimization must not be described as introducing module-handle caching from scratch. Instead,1.3.1 adds initialization state **600128d4**: loader admission skips initialization for a nonzero cell without incrementing it; the zero path calls init/error-callback setup then increments it. Cleanup calls shutdown/decrements only when nonzero. This is the same kind of ordinary0/1 latch later seen in the final driver, but its historical address is different from final600127d0 and must not be conflated.

Old direct init sites include mode worker60002169; old shutdown includes context close60002069. Those direct sites disappear in1.3.1, leaving the centralized loader/cleanup calls. The newly pinned cleanup callers include is-tail60001e1e and restore600020d6. This gives **partial static support for MP131-002**, specifically its removal of init/shutdown calls during the inspected mode-change route. All transitive provider paths, unusual re-entry, actual invocation frequency and measured optimization remain unverified.

Under ordinary zero initial state and serialized acquisition/cleanup, the cell behaves as a latch; it is not a general reference count. No universal once-per-process, balanced arbitrary nesting, reentrancy or shutdown-success guarantee follows. Archive release correspondence does not authenticate every earlier beta/branch. The historical comparison does not transfer every final-driver mechanism into these older members.

## Context close no longer shuts down the provider directly

Complete context-close helper **60002050** is now captured in both versions (reference57 bytes through60002089; final41 through60002079). Both return immediately when byte6000fca4 bit1 is clear. Otherwise they pass stored context6000fd08 to slot60011020, verified `_grSstWinClose@4`, then clear that context and bit1 without testing the provider result.

Reference additionally calls `_grGlideShutdown@0` through60011014 immediately after context close. Final removes that call. Its local state tail uses EAX=0 and an in-memory byte AND; reference instead loads/masks the flag through DL and zeros ECX, restoring saved ECX/EDX before returning. Thus these internal helpers do not establish identical EAX/flags contracts. No scalar status should be invented for the close helper.

Export **`_THRASH_restore@0` at60002090** has a complete118-byte body in both versions. All13 differing bytes lie in600020d6..600020e3: reference calls GlideShutdown, zeros EDX and calls handle-release helper60001560; final calls latch-based shutdown helper60001108, then zeros EDX and skips padding. The remaining restore instructions match. The earlier [loader/latch comparison](#loader-and-cleanup-lifecycle-differ) establishes that these cleanup helpers differ in handle retention and shutdown admission.

Restore's unchanged admission matters: DWORD6000fca4==0 returns1 without any of this cleanup. On its active-context branch it calls setvideomode(0,0,0), then helper60002020, before rejoining the event/provider cleanup tail. The complete38-byte helper60002020..60002046 matches: if object6000fd00 is nonnull it calls vtable+8 and clears the pointer, then returns1. This is a release-shaped interface call, not proof of its complete ownership contract. Restore also clears its callback/event-related local state, and returns1 without checking the close/provider results.

Together these callers connect centralized initialization/shutdown to mode switching and restore. **Verified local difference:** ordinary context close no longer directly shuts Glide down; restore routes shutdown through the latch helper instead of direct shutdown plus handle release. **Unresolved:** all admission/state lifetimes, callback failures, transitive object cleanup, exact runtime shutdown counts, unload completion and provider behavior. A return1 or cleared pointer is not proof that external cleanup succeeded. No DLL/API/target instructions were executed.

## DirectDraw creation moves from a static import to conditional lookup

The complete126-byte conditional creation helper **`60001fa0..6000201e`** differs only in the four-byte CALL displacement at60001fc6. Reference calls thunk6000d894, whose `JMP [6000e26c]` is verified against its DDRAW.dll import entry **DirectDrawCreate**. Final instead calls new wrapper60001420. Thus the absent final static DDRAW descriptor is not evidence that this renderer never uses DirectDraw.

All three new helpers are retained in the manifest:

| Range | Verified local operation |
|---|---|
|600013ec..60001407 | Takes module-name pointer in EAX; calls imported GetModuleHandleA, then LoadLibraryA only if the former returns0; preserves saved EBX/ECX/EDX |
|60001408..6000141e | Takes module/symbol-name pointers in EAX/EDX; obtains handle, then calls imported GetProcAddress if handle!=0; returns0 if acquisition fails |
|60001420..6000143d | Supplies literals `DDRAW.DLL`/`DirectDrawCreate`; nonzero symbol result is a tail JMP; failure returnsffffffffh with RET0ch |

The caller requires object6000fd00==0 and policy DWORD6000fcc0!=0. It passes `(0,&object6000fd00,0)` and tests the result for zero; the wrapper's missing-library/symbol result is therefore rejected by the retained caller, which returns0. The wrapper itself does **not** clear the output pointer. Its tail JMP leaves the three original stack arguments and return address in place for the resolved function; actual provider ABI behavior is not observed.

After successful creation, the retained caller invokes object vtable+50h with its stored window and flags10h or11h according to6000fcfc. Zero returns1; a nonzero result calls vtable+8, clears the object pointer and returns0. These instructions establish local result handling, not complete COM ownership, cooperative-mode success or compatibility on a particular OS.

The resolver does not locally call FreeLibrary or cache a separate module handle. Its GetModuleHandle case borrows an existing handle; its LoadLibrary case acquires a reference. Do not infer one lifetime policy, a leak or permanent loading from both cases without tracing the remaining process state. Loaded DLL identity, OS search behavior, concurrent unload and all API failures remain unverified. **Verified difference:** conditional dynamic resolution replaces the static DirectDraw import at this call site, retaining the local failure gate. No DLL or API was executed.

## Suitability query retains lexical scoring but changes provider ordering

Complete **`_THRASH_is@0` at60001d50** is captured through exclusive60001e5a in reference (266 bytes) and60001e54 in final (260 bytes). Its override lookup60004960..600049ba and signed-decimal parser600049c0..60004a17 are also captured and byte-identical. A nonnull lookup result for literal **`VOODOO2_IS`** follows that parser route, bypassing the provider path. The environment-vector producer and active override value are not established here.

On the provider route, reference's loader is followed by local null checks for grGet/init slots, then grGet selector0fh with a four-byte output. A zero API result supplies score0; otherwise the output DWORD is used. A zero value skips scoring, while a signed-negative value bypasses the positive-value string path and is returned. Reference directly initializes Glide and registers its error callback after the nonzero query result. Final removes those guards/direct calls because its already traced loader resolves the required table and performs initialization **before** this capability query. This is a concrete call-order difference, even with identical later scoring instructions.

For a positive capability result, both use grGetString selectorA4h and skip bytes until the first ASCII digit or terminating zero. The audit verifies all256 entries of the retained character-class test: bit20h selects exactly `'0'..'9'`. The complete suffix is then compared case-sensitively and **lexicographically** against literal **`3.00`**, yielding0 below,100 equal or95 above. This is not numeric version parsing. For example, the retained instructions imply:

| String supplied to the comparison | Derived score |
|---|---:|
|3.0 |0 |
|3.00 |100 |
|3.01 or3.10 |95 |
|10.0 |0 |

These are static comparison derivations, not instruction probes or observed provider strings. The comparison/helper instructions are retained, but identical numeric output is not established under every provider state. Do not restrict all possible returns to0/95/100: the override and signed-negative capability paths can return other values.

Reference's provider-path tails perform direct shutdown and/or release through60001560; final routes them through latch helper60001108. Its override path still bypasses that provider cleanup, as it bypasses acquisition. These changes reuse the lifecycle evidence above rather than proving matching load references, initialization counts, failure side effects or timing. Null/invalid provider strings, complete environment ownership and actual selection preference remain untested. **Verified:** retained score computation with changed initialization/guard/cleanup ordering. No provider or target instructions were executed.

## Complete code-section cluster routing

The audit now assigns **all3,307 differing bytes** in the51,712-byte paired code section to18 nonoverlapping envelopes, with zero unassigned bytes. These envelopes intentionally include alignment, removed code and embedded data; they are **not**18 independent features or semantic completeness certificates. Every byte is counted once, even where reference instructions become final table entries or padding.

| Address envelope, end exclusive | Cluster | Changed bytes |
|---|---|---:|
|60001010..60001020 |Entry callback |15 |
|60001020..60001590 |Loader, binding table, insertion, dynamic lookup and padding |1,340 |
|600018b0..60001bb0 |Hardware table, query and mode helpers |737 |
|60001bb0..60001d50 |About and padding |63 |
|60001d50..60001e60 |Suitability query and padding |77 |
|60001eb0..60001fa0 |Init and padding |48 |
|60001fa0..60002020 |DirectDraw creation |4 |
|60002050..60002090 |Context close and padding |42 |
|60002090..60002110 |Restore |13 |
|60002110..60002390 |Mode worker and padding |588 |
|600024e0..60002660 |Texture allocation |6 |
|60002660..600026e0 |Texture upload |6 |
|60002860..60002880 |Clear and padding |28 |
|60002ab0..60003270 |Setstate |61 |
|60003270..60003350 |Lockwindow |52 |
|600033a0..60003410 |Readrect and padding |97 |
|60003410..60003480 |Writerect and padding |106 |
|6000d888..6000d8a0 |Import-thunk space reused for copy helper/padding |24 |

The last envelope previously held four static import thunks: grVertexLayout, grCoordinateSpace, DirectDrawCreate and grQueryResolutions. Final replaces them with ten-byte helper6000d888 and NOPs. With DF clear, it copies bytes from ESI to EDI through the terminating zero, leaves ESI past that zero and EDI at the copied zero, and returns EAX0. Final loader6000106e calls it to append `glide3x.dll` after its module-directory prefix. The helper has no local length bound or CLD; source termination, destination extent and ordinary direction-flag state are reconstruction preconditions. Filename API failures/backward-scan limits are not proved safe by this byte map, nor are failures observed here.

**Complete:** code-section changed-byte routing for this exact named pair, with the local mechanisms and explicit limits described above. **Still incomplete:** full import/data/header/resource/overlay meaning, all transitive callees/global lifetimes and callers, authenticated retail provenance, historical introduction and actual rendering/provider behavior. The raw import/data interval maps at the beginning remain inventories rather than completed semantic audits. This closes a routing gap in one driver; it does not close the original-versus-Modern whole-game objective.

## Next required comparison

The paired code-section routing is complete above; do not repeat that inventory or substitute the different local-candidate baseline. Further driver work should target a concrete remaining data/import/lifetime or provider question, using the existing final insertion/extra-slot limits. The broader EXE comparison can proceed independently; unresolved projection capture/lifetime and original/Modern runtime compatibility retain separate evidence gates.

**Done:** three artifact identities, export correspondence, static dependency differences and selected paired raw-region map. **Also verified:** complete about local differences and reference fixed-table/query contract. **Pending:** remaining hosted/final function/ABI/data comparisons, transitive failure/registered-finalizer lifetimes, authenticated lineage, historical introduction and runtime rendering. No release-note claim is promoted solely by this inventory. Existing EXEs/database, raw exports and maintained C remain unchanged.
