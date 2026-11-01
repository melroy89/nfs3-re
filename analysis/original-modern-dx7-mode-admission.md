# Official Modern DX7 driver: minimum resolution admission

## Artifact and boundary

This extends the [executable mode-admission comparison](original-modern-display-modes.md), which did not find a below-640×480 exclusion in the executable’s generic eligibility helper. Here the inspected artifact is **`drivers/dx7/dx7a.dll` from the retained official final package**, not the game executable and not an original-versus-Modern DLL pair. The [manifest](evidence/audits/official-dx7-mode-admission.json) records the archive/member identity, DLL size/hash, ImageBase and exact instruction spans. Reproduce with `python3 analysis/scripts/audit_dx7_mode_admission.py`. The script extracts an ignored reference copy and disassembles it; it never loads or executes the DLL.

## Enumeration callback admits only sufficiently large modes

The caller witness **`60002578..600025ec`** passes callback **`600025ec`** through an object’s vtable slot+20h. The callback reads an incoming record, calls pixel-format classifier `60003960`, and rejects a zero classifier result. It then reads width at+0ch, height at+08h and advertised depth at+54h:

| Test | Rejection |
|---|---|
| `60002613`: unsigned width <640 | Branch to callback return |
| `6000261e`: unsigned height <480 | Branch to callback return |
| `6000262a..60002644`: depth is neither16 nor32 | Branch to callback return |
| `60002644`: matching capability bit absent from `6005aaec` | Branch to callback return |

Depth16 uses capability mask400h; depth32 uses100h. For classifier result3, the output record’s depth is changed to15 at `6000265b`; the pixel classifier’s full meaning is not established here. Thus even this callback should not be summarized as “every output depth is16 or32.”

Accepted records are built with stride28h and passed to insertion helper **`600026d4..6000276d`**. The helper compares the first three DWORDs (width, height, resulting depth), inserts in sorted order or overwrites an equal entry, and caps the reviewed count at99. The callback returns1 even when it rejects a candidate; that value is not a per-mode admission result. Complete graphics-interface ABI and all API return handling remain outside this chapter.

The exported **`_THRASH_about@0` at `60001000`** writes the mode-table pointer `60017250` into descriptor+40h. The reviewed enumeration producer clears the pointed storage and builds records starting at `60017278`, matching the executable’s documented index-zero exclusion and28h stride. Export/configuration and descriptor-refresh calls may have further effects; this is not a proof of every advertised mode over the DLL’s lifetime.

## What this resolves, and what it does not

**MP150-030**, hiding modes below640×480: partial static support is now located in the supplied DX7 driver’s callback. Its unsigned width and height comparisons reject smaller ordinary candidates independently of the executable’s generic gate. This does not establish the rule in every supplied renderer, historical introduction, successful runtime enumeration or a difference from an authenticated original DX7 driver.

**MP120-019**, 640×480 always reported as16-bit for intro movies: still vendor-claimed. The reviewed callback admits dimensions equal to640×480 and has both16-bit and32-bit admission branches; it contains no exact-size branch forcing16-bit. This neither proves nor disproves a later descriptor override, other driver implementation or historical version behavior. No universal negative search is claimed. That separate depth policy requires the remaining descriptor/setup paths or the applicable release DLLs.

Next: inspect the descriptor refresh and actual menu/intro mode request path, then compare other renderer implementations only where they address a specific catalog claim. Keep movie decoder format limitations separate from enumeration policy and observed display behavior. Executable bytes and the saved Ghidra database remain unchanged.

The [menu-startup depth comparison](original-modern-resolution-defaults.md#menu-startup-depth-fixed-original-request-versus-optional-modern-32-bit) now distinguishes original’s fixed16-bit request from Modern’s optional32-bit request. This does not resolve the separate “always reported” depth claim.

## About descriptor ownership and EXE cache lifetime

The same archive-pinned audit now establishes a concrete ownership case for the [EXE's cached descriptor](original-modern-renderer-loading.md#cached-descriptor-is-separate-from-cleared-export-slots). Complete export `60001000..60001191` writes descriptor fields and returns immediate preferred address `600fc7c0` at `60001188`. That RVA`fc7c0` lies in the DLL's writable `.data` virtual tail beyond its raw-backed bytes. The result therefore points into module-owned storage, rather than a newly allocated return buffer or a stack local. PE relocation can change its runtime absolute address; the recorded addresses are preferred-image coordinates.

The body also calls `60002060` and `600092c0` before returning, and rewrites fields on each invocation. It must not be assumed pure solely because the returned pointer is stable. Replacing repeated queries with a cached pointer preserves the address in this implementation while potentially changing when setup/helper effects occur; those callees require their own contracts.

For this specific packaged DX7 driver, consumers require the owning module mapping to remain valid. EXE export-slot clearing does not establish continued validity of the cached descriptor after unloading. Conversely, the static pointer alone does not prove a use-after-unload path: load reference counts, actual unmapping and post-cleanup consumer admission remain unverified. This is final-package component analysis, not an authenticated original-DLL comparison or a runtime fault finding. No DLL was loaded or executed.

## About query rereads environment overrides

The expanded audit pins complete reader `60009250..600092bd` and the override-helper prefix `600092c0..60009300`, resolving actual MSVCRT imports `sprintf`, `getenv` and `atoi`. The reader first formats `%s_%s` with supplied prefix/key and queries that name. Only if getenv returns null does it try `THRASH_%s`. A present value is converted with atoi; if both lookups are absent, the reader returns its caller-supplied default. A present empty or malformed string is not treated as an absent variable by this control flow; exact CRT conversion edge cases remain unqualified.

The about export passes prefix `DX7` and the module descriptor to the override helper on every invocation. Its captured prefix reads key`signature` and stores the result at descriptor+0, then key`version` and stores at descriptor+8. Therefore `DX7_signature`/`DX7_version` take precedence over `THRASH_signature`/`THRASH_version` in these paths. The remaining fields of the longer override helper are not fully audited here. The separate `60002060` helper also conditionally reads `THRASH_DISPLAY`; its downstream selection routine remains unqualified.

This establishes actual setup effects behind a nominal about query. The EXE's [loader acceptance check](original-modern-renderer-loading.md) compares descriptor+8 with`68h`; this driver can supply an environment-overridden value there. A cached descriptor read does not itself rerun these getenv/atoi operations. Equal pointer addresses thus do not establish equivalence to a fresh query if environment/setup state changes. Conversely, no evidence here shows that the game changes these variables between queries, that an override is installed, or that a supported driver is rejected in normal use. Final-DLL evidence must not be used to date this behavior or attribute it to an unauthenticated original counterpart. No environment was changed and no DLL was run.

## Sorted-list subclaim in MP161-004

The full source bullet MP161-004 also says DX7 returns a sorted resolution list. The retained insertion helper now has explicit instruction assertions for that policy: `600026fe` sets ECX3, REP CMPSD compares the candidate's width/height/resulting-depth DWORDs against a midpoint record, then JE accepts equality and unsigned JA moves the lower search bound upward. Under ordinary initialized count/table state and clear DF, this produces ascending **unsigned lexicographic width, then height, then depth** ordering. It is not an area-based or refresh-rate sort.

Equal keys reach `6000274b` and replace all ten DWORDs of the existing28h-byte record without incrementing count. The unsigned count>=99 rejection at `60002718/1b` applies to a **new key after the search**; duplicate replacement can still succeed at capacity. The shifting path uses STD and later CLD, while entry/search/final copying assume clear DF. These implementation details matter for an exact C reproduction and duplicate metadata policy.

This gives partial static support for the sorted-list portion of MP161-004. Its other portion—no unsupported640×480×16 advertisement—still needs an exact-size policy and all producers/consumers review; the minimum-size callback alone does not prove it. Actual runtime ordering, later mutations and historical v1.6.1 introduction also remain unverified. No list was enumerated by a graphics API and no driver instructions were executed.

## Reviewed enumeration does not synthesize a fixed640×480×16 record

The audit now asserts the complete reset at `600025b2..600025cb`:1000 DWORDs at the descriptor's mode-table pointer are zeroed and count `600fc7fc` is cleared before enumeration. Accepted callback records are constructed from the incoming candidate and inserted from `60017278`, one28h-byte record beyond table base `60017250`. After the interface enumeration returns, `600025e1` increments the count once to include reserved index0. This explains why count1 can describe a table with no admitted candidate records; it is not proof that a usable640×480 mode exists.

Within the reviewed `60002578..6000276d` path there is no unconditional fixed640×480×16 insertion. A candidate of that size can pass the ordinary minimum-size/depth/capability gates, but it must arrive through the callback path. This gives a bounded mechanism consistent with MP161-004's unsupported-mode subclaim; it does not prove every advertised mode is supported or exclude other writers/descriptor overrides elsewhere in the DLL. Full graphics-interface binding/error semantics and a justified earlier-release comparison remain required for the whole claim. In particular, lack of an exact-size forcing branch in this path must not be confused with proof of no such branch anywhere. No graphics API or mode enumeration was run.

## Direct v1.6.0-to-v1.6.1 comparison closes the two local mode mechanisms

The newly retained [historical pair audit](evidence/audits/dx7-160-161-mode-policy.json), reproduced by `python3 analysis/scripts/audit_dx7_160_161_modes.py`, supersedes the older missing-baseline limitation for MP161-004. It verifies both author-hosted archives/member hashes using the [package baseline](evidence/audits/official-160-161-baseline.json). Addresses are paired by the common mode-table publication, record layout and enumeration roles, not assumed to be matching functions merely because their VAs overlap.

| Mechanism | v1.6.0 DX7 | v1.6.1 DX7 |
|---|---|---|
| Fixed entry before enumeration | `60002555..60002586` explicitly writes640,480,16 and metadata into table index1, then count2 | Reviewed producer clears table/count and does not add that fixed candidate |
| New candidate ordering | Callback `60002710..600027d5` scans for equal width/height/input-depth or first empty entry; new keys append in arrival order | Callback builds a candidate and invokes the already verified sorted binary insertion helper |
| Table connection | About publication at `60001161` supplies `60017250` through `600fc800` | Corresponding publication at `60001150` supplies the same table coordinate/layout |

This directly establishes removal of an unconditional local640×480×16 seed and replacement of arrival-order insertion with unsigned width/height/resulting-depth sorting between these two supplied releases. With no admitted enumeration candidates, that older seed explains count2 versus the newer reserved-only count1. The older setup witness does not test whether the display interface actually offered the seeded mode before creating it. Subsequent candidates can overwrite records; no unconditional final output for all API results is inferred.

Both named code mechanisms in MP161-004 therefore have **bounded static support from an actual historical pair**, rather than final-build interpretation alone. Actual system support, API failures, all later writers/overrides and rendered acceptance remain untested. The pair establishes that these mechanisms differ between author-hosted1.6.0 and1.6.1; it does not prove every intermediate development revision or independently authenticate archive publication dates. No DLL was loaded or executed, and no original-retail-DLL equivalence is claimed.


## Missing display environment stops forwarding saved ECX

The [display-env audit](scripts/audit_dx7_display_environment.py) verifies the pinned1.6.0/1.6.1 DX7 members, captures both complete wrappers at`60002060` (86 versus64 bytes), and verifies complete **295-byte consumer `600020c0..600021e7`** is byte-identical. The [manifest](evidence/audits/dx7-display-environment.json) retains hashes, imports and branch witnesses. This resolves selected argument/consumer details behind the earlier helper reference, not the complete display lifecycle.

Both wrappers only reach the environment/selection calls when signed DWORD`600170bc` is negative and at least one of`6007b864`/`6007b880` is nonzero. They call imported **getenv** with `THRASH_DISPLAY`; a present value is passed to imported **atoi**, whose result reaches consumer`600020c0`.

| Path |1.6.0 |1.6.1 |
|---|---|---|
| Missing environment value | `600020aa` loads DWORD`[ESP]`, the entry ECX saved by PUSH ECX, and passes it | Skips atoi and passes the zero getenv result |
| Present value | Pass atoi result | Same input route |
| Negative current selector, before the two-cell guard | Writes1 to`6005ab60` at`60002071` | No corresponding local store |

The old missing-value route therefore has a **hidden register input**, even though its wrapper is not conventionally presented as taking an ECX argument. Caller initialization of ECX is not established here, so do not automatically call it uninitialized memory or silently replace it in an original-compatible reconstruction. The newer zero argument is a concrete behavioural change. The removed store is another local effect; complete meaning/other writers of`6005ab60` remain separate, and it is not assigned to a visual workaround by this audit.

The retained consumer clears`600186d8`, conditionally releases an existing object through a helper, then reads its stack index. For signed`0<=index<[600186e0]`, it selects the corresponding pointer from table`60018250` and publishes that index at`600170bc`; otherwise it selects table entry0 and publishes0. It copies selected descriptive data, then performs further callback/setup work before returning1 with RET4. Fallback0 is **not** proof that entry0 exists or is valid, nor is return1 proof every subordinate operation succeeded.

Conditional static consequence: if entry ECX is a valid nonzero index and the environment is absent,1.6.0 can select that entry where1.6.1 requests0. Invalid old ECX also falls back to0 through this consumer, subject to pointer/state prerequisites. No index, environment lookup or driver was executed.

This comparison was inspected while triaging the claimed black-polygon workaround, but **no causal link to MP161-003 is established**. It is documented as an independent display-selection difference. The black-polygon location/rendering claim, full callbacks, selector lifecycle, source-string bounds and actual display acceptance remain unresolved; existing catalog status for that visual claim is unchanged.
