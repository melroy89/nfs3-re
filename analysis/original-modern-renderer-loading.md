# Original versus Modern: renderer loading and validation

## Scope and evidence

**Verified static comparison; runtime acceptance not tested.** This compares the supplied original/backup SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` with the official Modern Patch v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. Their provenance and authentication limits are in the [baseline report](original-modern-differences.md).

The [retained audit](evidence/audits/original-modern-thrash-loader.json) records hash-pinned instruction spans and all 34 original/Modern export bindings. Reproduce with `python3 analysis/scripts/audit_thrash_loader_difference.py` from the repository root; requires Python `pefile` and GNU `objdump`. Assembly captures remain under ignored `analysis/captures/modern-differences/thrash-loader/`. Neither executable nor the maintained Ghidra database is changed. No game or extracted instructions are executed.

## 1. Loader correspondence and retained interface

| Operation | Original | Official Modern |
|---|---|---|
| Loader entry | `004f8390` | `004f84a8` |
| LoadLibraryA call | `004f839e` | `004f84aa` |
| GetProcAddress | 34 explicit call sequences, beginning `004f83c9` | Loop call at `004f84c8` |
| Module handle | `00564a6c` | `00564a6c` |
| Export mapping | Immediate name operands and explicit pointer stores | Name/slot pairs at `004f8390..004f849f`; zero terminator at `004f84a0` |
| Export count | 34 | 34 |

Every name-to-slot pair matches, including `_THRASH_about@0 → 009ef980`, `_THRASH_setstate@8 → 009ef96c`, `_THRASH_drawpointmesh@12 → 009ef900` and `_THRASH_drawpointstrip@8 → 009ef904`. The point-mesh/strip lookup order changes, but their destination bindings do not. This is retained export binding, not a claim that renderer implementations or all ABI behavior are identical. Decorated names encode stack-byte counts but do not independently prove each DLL implementation's calling convention.

Modern reuses the original loader's former entry region as **data**. Disassembling Modern at `004f8390` produces misleading instruction text from pointer pairs. Conversely, current Modern function addresses cannot be assigned to original code merely because the addresses match.

## 2. Mandatory export checks

Original loads the module, performs the explicit lookups, then sets success register EBX to 1 at `004f86dc`. It does not test each lookup result. At `004f86fa..004f874b`, a non-null set-state pointer triggers selector `0x1f`, value `0x68`. A non-null about pointer triggers descriptor inspection. If either pointer is absent, that call is skipped; the shown paths can still return success. Other missing exports are also not rejected individually in this loader.

Modern iterates each pair: `LODSD`, null-name termination test, `GetProcAddress`, `TEST EAX,EAX`, then pointer store (`004f84c1..004f84d7`). **Any missing export branches immediately from `004f84d0` to cleanup `004f8506`.** Only after all 34 bindings succeed does it call set-state with the same `0x1f/0x68` arguments and call about (`004f84d9..004f84e3`). It therefore requires all 34 entries, rather than just resolving and retaining whatever the DLL supplies.

## 3. Descriptor checks differ

Original at `004f8753..004f8791`:

- Null about result skips validation and retains the loader's current success value.
- Descriptor DWORD `+0` equal to `0x33444658` sets `00564410` to 1; other signatures do not immediately fail.
- Descriptor DWORD `+8` must equal `0x68` when a non-null descriptor is returned. Otherwise a diagnostic path clears success.

Modern at `004f84e9..004f84f5`:

- A null descriptor fails loading.
- DWORD `+8` must equal `0x68`; mismatch fails loading.
- Stores the accepted descriptor pointer at `007a3a5c`.
- This loader contains no equivalent DWORD `+0` signature classification. Do not describe it as stricter on every possible property: the new checks strengthen mandatory exports/null handling, while the old signature side effect is absent here.

The meaning of the signature flag and all downstream descriptor fields is outside this bounded comparison. `0x68` is the literal checked field/value; equating it with an entire structure size or API version needs independent layout evidence.

### Glide internal failure is a separate layer

The [paired Glide follow-up](original-modern-glide-reference-identity.md#internal-provider-failure-is-not-a-null-about-result) now traces a concrete cold-about branch: final driver internal provider-loader return0 still yields its prepared nonnull descriptor with+8=68h and zero mode count. That result passes this EXE's local descriptor gate; mode count is not checked here. The separate complete mode enumerator skips eligibility/callback calls when count is zero. This is conditional static control flow, not a successfully observed driver load or a proof of later initialization/fallback behaviour.

## 4. Failure cleanup, return and fallback

Modern stores the module handle before export resolution. Missing export/null descriptor/mismatched `+8` all call `004f8514`. Cleanup exchanges `00564a6c` with zero (`004f8517`). A previous zero handle skips both FreeLibrary and the slot-clear loop. For a nonzero previous handle, it calls FreeLibrary (`004f8522`), then clears every destination slot through the same table (`004f8528..004f8537`). Loader clears EBX after failure, writes EBX to saved EAX at `[ESP+0x1c]`, and restores registers with POPAD (`004f850b..004f8512`): EAX returns zero or the loaded module handle. A successful load also attempts cleanup registration via `004f7c20` at `004f84ff`; the [shared callback registry](original-modern-shell-open.md#startup-registers-the-callback-it-does-not-directly-open-the-url) now establishes the registration facility, with the failure boundary below.

Original returns its EBX success flag through EAX at `004f870c`; this is a different success representation. On initial LoadLibrary failure, it formats `"%sa"` using the requested name (`004f871a..004f872a`) and retries LoadLibrary (`004f8730`), before returning to the binding path. Modern's shown loader has no corresponding suffix retry: initial load failure jumps to its zero-return path. This proves removal of that local retry, not the absence of every alternative driver-selection path elsewhere.

## 5. Driver-specific configuration before loading

Modern `004b5844` implements a configuration-driven path absent as a corresponding routine at that same original entry. Static inspected sequence:

| Modern address | Observed behavior |
|---|---|
| `004b5845..004b5874` | If bit 0 of `0055eb2c` is clear, read `NFS3/ThrashDriver`, default `dx7`, into 56-byte stack storage and pass it to `004b57f4`. |
| `004b5877..004b58ba` | Get executable path, walk backward to its last backslash, append `\\drivers\\` and selected driver; call optional DLL-directory wrapper `004f1ed4`. |
| `004b58bf..004b592b` | Form driver-directory `thrash.ini`, require its existence, read `THRASH/File`, append it to the directory, require the resulting file. Missing config/file or empty File returns zero at `004b5a38`. |
| `004b5931..004b5978` | Read `THRASH/Type`, lowercase its first byte: d→`0x40`, v→`0x10`, s→`2`, other→`1`, stored at `007a3a58`. |
| `004b597b..004b5999` | Read `THRASH/FogSupport`, default zero; normalize nonzero to 1 at `007a3a54`. |
| `004b599e..004b59e4` | Read `DDRAW/DisableMaxWindowedMode` and `DDRAW/NoDwmOffForPrimaryLock`, each default zero; true sets bits 12/1 of `007a2790`. False does not clear those bits locally. |
| `004b59e4..004b5a2d` | Read an 8192-byte `ENV` section into stack storage, split each entry at its first `=`, then call SetEnvironmentVariableA on name/value. Entries without `=` are skipped. API return values are not checked locally. |

API identities follow the binaries' import tables, not string inference. The path walk assumes an appropriate backslash exists; this inspection does not establish robust handling of every truncated/API-failure input. The parser `004b57f4` lowercases ASCII, converts `/` to `\\`, splits an `@` suffix and stores a decimal numeric suffix at `007a3a70`; its 55-byte copying/termination limitations are already documented in [detailed notes](detailed-analysis-notes.md#renderer-driver-path-and-numeric-suffix-004b57f4). An absent/invalid numeric suffix retains the previous value. The [command-line follow-up](original-modern-command-line.md#duplicate-driver-options-name-and-suffix-are-separate-state) traces how reverse argument iteration can combine a name and retained suffix from different options, and how an empty driver option still suppresses the INI read.

This verifies the Modern-side mechanism and a changed loader, not a complete map of original driver selection. Original `004f87e0` separately handles `THRASH_DRIVERNAME` and a leading `!`; callers and historical selection tables still need mapping before a complete precedence comparison is claimed.

## 6. Original environment override and selection wrapper

The [selection/compatibility manifest](evidence/audits/original-modern-renderer-selection.json), reproduced by `python3 analysis/scripts/audit_renderer_selection_difference.py`, retains additional hash-pinned spans. Original wrapper `004f87e0..004f882d` takes a candidate name in EAX and explicitly preserves EDX:

- If the candidate begins with `!`, advance past it and skip environment lookup.
- Otherwise call `0050ead0` with file-backed key `THRASH_DRIVERNAME` at `0054d700`. A non-null result replaces the candidate; a null result leaves it unchanged. There is no nonempty-value test in this wrapper.
- Set `00564a68` to 1 if it was zero. If module handle `00564a6c` is already nonzero, call `004f87a0` before invoking loader `004f8390`; otherwise invoke the loader directly.

The inspected environment reader walks the pointer array at `00a0b154`, compares a name prefix and requires the following byte to be `=`, then returns the value pointer (`0050ead0..0050eb29`). This is stronger evidence than the key string alone, but the comparator’s full case/locale semantics and environment-array initialization are outside this scope.

Original selector entry `004b59c0` accepts an index in EAX, rejects unsigned indices above 10, and dispatches through a jump table. Its first inspected branch obtains a candidate from table `0055fd68` and calls the wrapper at `004b59f9`. The 11 table strings, in index order, are `nulla.dll`, `softtria.dll`, `softlina.dll`, `voodooa.dll`, `voodoo2a.dll`, `ragea.dll`, `d3da.dll`, `powervra.dll`, `powervra.dll`, empty, empty. These are candidate names, not 11 proven successful drivers or a complete account of every selector branch. Modern’s INI/driver-directory path is already traced above; no general claim is made that environment overrides disappeared everywhere in Modern.

## 7. Modern DirectDraw compatibility dispatch

After configuration succeeds, `004b5a6c` loads mask `007a2790`; if nonzero it invokes `004b57c4` **before** renderer loading at `004b5a7f`. The compatibility helper resolves the file-backed pair `DDRAW.DLL` / `SetAppCompatData` through `004f1ebc`. Its underlying module helper first calls GetModuleHandleA, then LoadLibraryA only when no module handle is returned (`004f1ea0..004f1eba`); GetProcAddress resolves the export. Missing module/export makes the compatibility helper return without calls.

For a resolved export, the helper scans the least-significant set bit using BSF, clears it in its private ESI copy with BTR, and calls the export after pushing **0 then the bit index** (`004b57df..004b57ec`). Thus mask bits 1 and 12 produce calls with index 1 then index 12 and a second stack argument of zero; it does not pass the mask or its powers-of-two values to the export. The loop stops when its local copy becomes zero, leaving the global mask unchanged. ECX, EDX, ESI and EDI are explicitly saved; API return values are not tested.

This connects `NoDwmOffForPrimaryLock` and `DisableMaxWindowedMode` from their configuration writes to actual optional-interface calls. No export implementation was executed or inspected here. The undocumented operation meanings, supported Windows/Wine versions, module lifetime and actual performance/DWM behavior remain unresolved. A successful lookup or an unchecked call is not evidence that the requested OS behavior took effect.

## Release-note traceability and remaining work

- **MP161-006**, stricter driver validity: statically supported by the mandatory-export and non-null descriptor checks above. Exact introduction in v1.6.1 requires a preceding-release binary; comparing original to final cannot date each edit.
- **MP140-040**, renderer initialization refactor: loader table loop, shared cleanup and changed return/fallback behavior are confirmed examples, not exhaustive coverage of initialization.
- **MP140-042**, ENV settings from selected thrash.ini: the Modern path is confirmed. Replacing every previous hard-coded environment write is not established.
- **MP161-008/009**, compatibility options: current key reads/defaults/bit writes confirmed. Historical rename from DirectDrawLagFix and the downstream OS effect require separate evidence.
- **MP150-044**, driver-directory wrappers: existing [optional DLL-directory wrapper analysis](detailed-analysis-notes.md#optional-dll-directory-export-wrapper-004f1ed4) and its caller support a search-directory mechanism. Wrapper loading on each supported OS/DLL is untested.

The [initialization comparison](original-modern-renderer-initialization.md) now maps all original selector targets and Modern type branches. Next: trace selector producers/callers and remaining descriptor consumers; inspect the actual renderer DLLs for changes attributed to those components. Static acceptance checks do not establish that any particular third-party renderer loads or renders correctly.

## Removed original renderer snapshot bank

The [snapshot audit](evidence/audits/renderer-context-snapshots.json), reproduced by `python3 analysis/scripts/audit_renderer_context_snapshots.py`, classifies the large NOP region **`00517170..00517580`**. Original complete bodies **`00517170..00517362`** and **`00517370..0051755e`** restore/save a renderer snapshot. Both bodies and original cleanup wrapper **`004f87a0..004f87d9`** are entirely NOPs at their old addresses in official Modern.

Each snapshot is **35 DWORDs /140 bytes** at`00564a70 + 140*index`: module handle plus the34 THRASH pointer slots already mapped above. Both functions accept signed EAX indices0..7; out-of-range values are replaced with0 and processing continues. They do not return a checked invalid-index error. Restore additionally writes active index`00564a68`; save does not establish the same active-index update. EDX is saved/restored; EAX is working state rather than a verified Boolean return.

Original cleanup wrapper reads current module/index, conditionally calls FreeLibrary, clears module handle`00564a6c`, calls restore with index0, then saves into the previous index. Thus the bank participates in the observed cleanup sequence, not merely an unused table inferred from data. Slot0 contents, all bank producers and runtime switching admission remain unresolved; do not infer complete lifetime safety from this local path.

Modern's table-driven unload-and-slot-clear routine is documented earlier in this chapter. The change is removal of these original snapshot-bank bodies/cleanup path in favor of the inspected Modern mechanism, **not proof that multiple rendering APIs or drivers disappeared**. The existing loader comparison already distinguishes static DirectDraw removal from dynamic renderer support. No DLL, snapshot helper or cleanup routine was executed.

## Release-note reconciliation: directory layout, type fallback and reporting

The loader audit now asserts the final parser literals and exact instructions behind three additional catalog links. This is final-pair/static evidence, not proof of when each change first appeared.

- **MP120-004, directory/configuration structure:** the executable-relative driver directory, per-driver `thrash.ini`, File checks and type dispatch are established above. The final game-setting key is literal **`ThrashDriver`**, not the historical source bullet's `VideoDriver`. Moreover Type is read with a null default argument at `004b593e`; only its returned first byte is lowercased and inspected. Returned `d/v/s` select64/16/2, while any other byte, including0, takes `MOV AL,1` at `004b5965`. An empty returned Type therefore selects the generic mask in this local code; it is not a locally rejected missing required field. The File/existence gates must not be conflated with Type validation. Provider/string-reader failure behavior remains untested.
- **MP120-005, configurable capabilities:** `THRASH/FogSupport` and its default0/nonzero-to1 store are verified, and the initializer's state-query gate can clear it again. This supports the fog-override mechanism, not guaranteed visible fog or the entire bundled claim. The final parser does not establish the named `LightBeams` capability; its [historical reader and packaged settings are now verified](#historical-lightbeams-reader-and-capability-defaults), with rendered effects unresolved.
- **MP120-007, failure reporting:** the Modern initializer routes inspected configuration/load/init failures through the MessageBox-based diagnostic helper `004b570c`, documented in the startup requirements comparison. This supports explicit failure reporting in the final path. The original already has diagnostic paths: for example `004f8830` tests the about pointer and, when absent, supplies diagnostic metadata and calls `00401010` at `004f88a9`. Thus the source bullet's broad absence-of-original-reporting assertion is not established. The [shared terminal ExitProcess boundary](original-modern-startup-requirements.md#shared-termination-chain-reaches-exitprocess) is now verified for paths reaching the exit wrapper; other diagnostic sinks, pre-exit hooks, all failure paths and actual dialogs remain unverified.

**MP120-006 remains unverified as a whole-lifetime claim.** The final low-level loader `004f84a8` starts with a LoadLibraryA request; it has no initial nonzero-handle guard that by itself proves one load for the entire process. Cached descriptor use in enumeration and removal of the original snapshot-bank paths do not establish how often all higher-level initialization/recovery callers run. Establish caller lifetime and unload/reload ownership before upgrading that claim. The separate Voodoo wrapper's cached `glide3x.dll` handle is a different module/dependency and must not be substituted for the EXE's THRASH-driver lifetime.

The [catalog](modern-patch-change-catalog.md) therefore labels the three supported claims partial and retains the lifetime claim as vendor-only. The evidence manifest records final key/type/fog contracts; earlier original callback-installation captures remain linked through the selection/lifecycle reports. No configuration API, driver or game was executed.

## Final package capability-key inventory

Run [the packaged configuration inventory](scripts/inventory_packaged_driver_configuration.py). Its [manifest](evidence/audits/packaged-driver-configuration.json) pins the official archive, all22 selected EXE/DLL/INI members (two EXEs,11 DLLs, nine INIs), the parsed settings and exact literal file offsets. It reads archive members without loading code or replacing installed configuration.

| Packaged driver directory | THRASH/File | THRASH/Type | THRASH/FogSupport |
|---|---|---|---|
| `dgvoodoo` | `voodoo2a.dll` | `voodoo` | 1 |
| `dx5` | `dx5a.dll` | `d3d` | Absent |
| `dx6` | `dx6a.dll` | `d3d` | 1 |
| `dx7` | `dx7a.dll` | `d3d` | 1 |
| `dx8` | `dx8a.dll` | `d3d` | 1 |
| `glide3x` | `voodoo2a.dll` | `voodoo` | 1 |
| `nglide` | `voodoo2a.dll` | `voodoo` | 1 |
| `softtri` | `softtria.dll` | `software` | Absent |

These are **packaged defaults**, not effective settings on this machine. Six of the eight driver INIs explicitly supply FogSupport; the inspected EXE parser supplies fallback0 when it gets no configured value. The packaged game INI uses `ThrashDriver=nglide`. That does not override user-edited INIs, command-line selection or earlier initialization state in this analysis.

A case-insensitive byte search finds **no `LightBeams` or `VideoDriver` literal** in the22 selected members, under either ASCII or UTF-16LE encoding. The same pinned README contains `LightBeams` at line403 in the v1.2.0 capability-settings bullet. This is a historical/final-package mismatch in available evidence, not proof that the old feature never existed or all beam rendering was removed. Raw searches omit compressed/encoded or dynamically constructed strings, external components and other encodings; packed provider contents are not unpacked here. The result does not qualify game or provider behavior.

For **MP120-005**, the FogSupport parser/configuration portion is supported; the [LightBeams historical reader/configuration pair is now verified](#historical-lightbeams-reader-and-capability-defaults); final control mechanism and visible effects remain unresolved. For **MP120-004**, the final ThrashDriver spelling is independently confirmed by both EXE literal and packaged INI. Keep those distinctions when choosing a reconstruction interface: a historical README spelling must not silently become a final-binary option name. No historical introduction date or runtime rendering success is inferred.

## Compatibility mask persistence and adapter return contract

The expanded [selection audit](scripts/audit_renderer_selection_difference.py) now asserts the exact BSF/BTR/PUSH/CALL loop, both configuration BTS instructions and the actual module/procedure IAT names. Its [manifest](evidence/audits/original-modern-renderer-selection.json) records the bounded state/register contract in addition to the complete existing captures.

Within the two-setting block `004b599e..004b59e4`, nonzero reads set global mask `007a2790` bit12 (`DisableMaxWindowedMode`) or bit1 (`NoDwmOffForPrimaryLock`); zero reads branch around BTS. Thus, absent other writes, the local update is:

`after = before | (disable != 0 ? 0x1000 : 0) | (no_dwm != 0 ? 0x2 : 0)`

This is an accumulating set operation, **not assignment of the complete mask from current Boolean settings**. False/default0 does not locally clear a prior bit. Reconfiguration lifetime, initial global ownership and concurrent writes still need caller analysis before inferring an observed stale-setting bug.

Adapter `004b57c4` copies incoming EAX into ESI, obtains optional `DDRAW.DLL!SetAppCompatData`, and iterates its private copy in ascending set-bit order. Input`00001002h` produces `(1,0)` then `(12,0)` stack-argument calls. BTR modifies ESI only; it does not clear the published global mask. A repeated adapter call can therefore reissue those requests. The selected provider's signature, callee stack cleanup and interpretation of indices remain external ABI requirements, not implementation proof from the name alone.

The adapter saves/restores ECX, EDX, ESI and EDI. It returns without a provider call if lookup fails, leaving EAX0. With a resolved export and zero input mask, BSF sets ZF and the loop exits with EAX still containing the resolved pointer. With a nonzero mask, EAX is whatever the last provider call left; that result is not tested or normalized. Therefore it must not be reconstructed as a reliable Boolean success API merely because a decompiler gives it a scalar return. Its ordinary loader caller also does not establish OS success by checking that return.

Underlying `004f1ea0` first uses GetModuleHandleA and requests LoadLibraryA only on a null result. `004f1ebc` resolves the export afterward. These local bodies do not track whether a module handle is borrowed or a newly acquired load reference, and show no corresponding FreeLibrary; whole-process module lifetime/cleanup remains unverified. The evidence establishes optional requests and local state handling, not a DirectDraw/Wine compatibility effect, reduced lag, supported OS range or historical default. No DLL/API execution, compatibility toggle or timing test occurred.

## Optional driver-directory export: caller-to-wrapper evidence

The loader audit now includes the complete31-byte wrapper `004f1ed4..004f1ef3` and asserts its strings and caller, extending the earlier [annotation](detailed-analysis-notes.md#optional-dll-directory-export-wrapper-004f1ed4). Final Modern settings construction prepares the driver-directory buffer at `007a3930`; at `004b58b5` it loads that address into EAX and calls `004f1ed4` at `004b58ba`. The next instructions continue path/configuration construction without testing EAX.

The wrapper saves EBX/ECX/EDX, retains the supplied directory pointer in EBX, and resolves **KERNEL32.DLL / SetDllDirectoryA** through `004f1ebc`. If resolution returns zero it skips the call and returns zero. Otherwise it pushes the original pointer, invokes the resolved function and forwards its raw EAX result. There is no per-wrapper lookup cache, local path validation, module release, automatic restoration of the prior directory or error translation. Reusing the common resolver means a previously loaded module can be reused; absence of a lookup cache must not be described as loading a new module on every call.

This is a proven dynamically resolved interface and a concrete directory-search request preceding renderer loading, supporting **part of MP150-044**. The stronger claim that *all* renderers can use *any* wrapper from their directories on Windows XP SP1+ is not established: successful export lookup/call, each dependency's actual resolution, supported OS behavior and DLL lifetimes have not been tested. The final binary pair cannot establish the introduction release. The catalog therefore marks this mechanism partial, rather than upgrading the whole compatibility claim. No DLL search state was changed during this audit.

## Missing-driver diagnostic correspondence

MP161-007's missing-driver subclaim maps to `004b5a58..004b5a6c`. The caller invokes configuration constructor `004b5844`, tests EAX and, on zero, supplies message `0053d1a4` (“The thrash driver is not found.”) to fatal diagnostic helper `004b570c` at `004b5a67`. The loader audit asserts this complete20-byte sequence and exact message. The configuration constructor's missing INI, empty File and absent target-file returns described above therefore share this diagnostic; its wording does not establish that only an absent DLL can cause it.

The following load attempt is distinct: `004b5a7f` calls `004f84a8`; its zero return selects `0053d1c4` (“Cannot load the thrash driver.”) at `004b5a88`, then calls the diagnostic helper at `004b5a8d`. Both strings are pinned by the audit. Together with the [root-path diagnostic](original-modern-startup-paths.md#release-note-correspondence-root-path-diagnostic), this maps both named final-build mechanisms in MP161-007. Actual dialogs, all error causes, absence of analogous original diagnostics and the release-specific introduction date remain unverified. This is static branch/string evidence, not a reproduced startup failure.

## Deferred cleanup registration and zero-handle boundary

The expanded loader audit asserts `004f84fa..004f850d`: it supplies callback `004f8514`, calls the shared registrar and ignores its EAX result before publishing the loaded module handle as success. The shared registrar can return−1 when its signed count is at least32. That local failure therefore does not turn this loader path into failure or trigger immediate cleanup. This is a conditional lifetime limitation; actual registry saturation, resource leakage or missing shutdown cleanup was not observed. Other explicit cleanup calls and process-level module teardown remain separate.

The cleanup callback itself uses PUSHAD/POPAD, preserving EDX on ordinary return as required by the inspected callback-dispatch loop. Its zero-handle branch at `004f851d/1f` jumps straight to POPAD, so it does **not** unconditionally sanitize all export slots. When the exchanged old handle is nonzero, it calls FreeLibrary and then clears slots regardless of the API result, which is not tested locally. A reconstruction must preserve these version-specific conditions rather than turn cleanup into a stronger always-clear guarantee. No callback, loader or DLL API was executed.

## Cached descriptor is separate from cleared export slots

Modern cleanup `004f8514..004f853b` has no literal operand for cached descriptor cell `007a3a5c`, and that cell is not a destination in the34-entry export table. Consequently the inspected cleanup does not explicitly reset the cache as part of its slot-clearing loop. The expanded audit pins this distinction, the complete refresh helper `004f853c..004f8548`, and all ten literal address occurrences in the official executable. Eight are known consumer operands; the two direct publications are loader store `004f84f5` and refresh store `004f8542`. Computed/alias writes and external mutation remain unexcluded.

The refresh helper calls about slot `009ef980` and immediately stores returned EAX, without a local null check. The [renderer lifecycle comparison](original-modern-renderer-lifecycle.md) establishes a refresh call during mode application; the [texture comparison](original-modern-texture-loading-followup.md) establishes consumers replacing fresh queries with cached reads. These observations define a required ordering/ownership contract: those reads require a valid current descriptor, and clearing export slots alone does not establish that condition or invalidate every cached reference.

This is not proof of a reachable stale-pointer fault. Descriptor storage could have other ownership, consumers may be gated away after unloading, or other code may reset the cache through aliases. Required follow-up is that lifecycle/admission contract and the driver's descriptor allocation lifetime, not an assumption that FreeLibrary necessarily leaves a dangling pointer. A deliberate reconstruction can strengthen invalidation only as an explicit behavior change; it must not silently attribute that stronger policy to this executable. No DLL or target code was run.

## Historical DirectDrawLagFix configuration relocation: 1.3.0 to 1.3.1

**Verified statically; work done for this configuration-source question.** The
[reproducible audit](scripts/audit_directdraw_config_release_boundary.py) and
[retained bytes, disassembly, imports and archive/member hashes](evidence/audits/directdraw-config-release-boundary.json)
compare the adjacent author-hosted packages. This establishes MP131-001's
mechanism, rather than inferring it from packaged INI contents.

| Detail | 1.3.0 | 1.3.1 |
|---|---|---|
| Filename producer | `004a6e8d..004a6eaa`: GetModuleFileNameA into `007a263c`, replace final four bytes with `.ini` | `004b5775..004b57bd`: module directory, `drivers\`, selected driver name from `007a3a74`, then `\thrash.ini`, into `007a3930` |
| Section/key | `[NFS3] DirectDrawLagFix` | `[THRASH] DirectDrawLagFix` |
| Reader | Helper `004b55d8` calls integer reader `004fb6f0`; API call `004fb70a` uses filename `007a263c` | Direct GetPrivateProfileIntA call `004b5862` uses filename `007a3930` |
| Default supplied | Caller supplies1; reader's existing override lookup can replace the fallback before the INI API | Literal0 |
| Application | Zero skips optional compatibility call | Zero skips call to helper `004b55dc` at `004b586c` |

Under the shipped executable basename, the old filename is `nfs3.ini`; it is
actually derived from the module filename, so renaming the executable changes
that name. The new driver name is obtained from `[NFS3] VideoDriver` on the
ordinary configuration branch (`004b5748..004b5772`); its parser
`004b561c..004b5668` normalizes slash characters and separates an optional `@`
suffix. The nonzero preselected-driver branch reuses existing name storage.
The string-copy helper `004f93a8..004f93ba` leaves EDI at the copied terminator,
which explains how the successive path components are concatenated.

The optional compatibility tail is **57 byte-identical bytes**:
old `004b55f2..004b562b`, new `004b55e0..004b5619`. It tries
GetModuleHandleA/LoadLibraryA for `DDRAW.DLL`, then GetProcAddress for
`SetAppCompatData`; a successful lookup reaches `PUSH0; PUSH0ch; CALL EAX`.
The INI guard was removed from inside the helper and placed in the selected
driver configuration loader. Neither API availability nor its effects were
observed. The later final-version bitmask dispatch documented above is a
separate implementation; this historical evidence does not verify the 1.6.1
key rename.

**Limits and follow-up:** configuration routing and supplied-default changes
are verified. Actual settings with overrides, driver selection, API effects,
Windows performance and displayed results require controlled runtime evidence.
Path interpretation assumes successful normal module-path retrieval, a
backslash, sufficient capacity and DF0 for string operations; no robustness
claim is made. No target/provider/API execution, executable edits or saved
Ghidra changes were performed.

## Historical compatibility rename and section change: 1.6.0 to 1.6.1

The [read-only release-boundary audit](scripts/audit_directdraw_rename_boundary.py)
retains [pinned complete setting/adapter spans](evidence/audits/directdraw-rename-boundary.json).
It verifies the historical portion of MP161-008 while leaving OS effects
unverified. This is more than a string rename:

| Contract | 1.6.0 | 1.6.1 |
|---|---|---|
| Section/key | `[THRASH] DirectDrawLagFix` | `[DDRAW] DisableMaxWindowedMode` |
| Integer API/default | GetPrivateProfileIntA,0 | GetPrivateProfileIntA,0 |
| Local state update | `004b5932` assigns the returned integer to `007a2790` | `004b59b9` sets bit12 only for nonzero input; zero skips the write |
| Additional option | Neither named key present | `[DDRAW] NoDwmOffForPrimaryLock` independently sets bit1 at `004b59dc` |
| Dispatch | `004b5a02..004b5a10` tests nonzero; helper `004b57bc..004b57da` requests index12 | Helper `004b57c4..004b57f3` scans set bits and requests each index |

Both resolve `DDRAW.DLL!SetAppCompatData`. The old helper pushes0 and12;
with only bit12 set, the new helper requests the same pair of stack arguments.
Thus a nonzero old option corresponds locally to a nonzero new option's
request12, **not** to interpreting the old integer itself as a bitmask. This
does not establish whole-state equivalence: old settings overwrite the state,
whereas new nonzero options accumulate bits and false options do not clear
previous bits. Bit1 is an additional request with separate configuration.
The new section literal at `0053f730` is **DDRAW**, not THRASH; copying the old
section while merely renaming the key would not match this parser.

The final dispatcher ABI, return-value and lifetime limits in the preceding
sections still apply. Historical key/section/default and local dispatch
mechanisms are verified; Windows/Wine effects, timing, all initialization
writers and reconfiguration outcomes require separate evidence. No executable,
DLL, API or instruction probe was run, and no saved database was modified.

## Historical LightBeams reader and capability defaults

**Verified static historical reader; rendered effects unresolved.** The
[audit](scripts/audit_lightbeams_history.py) retains
[EXE identities, instruction bytes and all six1.2.0 driver INIs](evidence/audits/lightbeams-history.json).
This closes the missing historical reader/configuration evidence for
MP120-005. The final-package negative search above remains valid, but cannot
be used to dismiss the historical setting.

In1.2.0, `004b57e3..004b581a` derives defaults from the first lowercased Type
character. `004b581d..004b5844` reads `[THRASH] LightBeams` using the selected
driver configuration filename buffer `007a3930`; its fallback is the existing
DWORD `007a392c`. Any nonzero API result becomes1, then stores to that DWORD.
The separate instruction at `00470ad4` tests bit0 of the same global and
branches to `00470b1b` when zero. The [three-version setter comparison](original-modern-state14.md#historical-lightbeams-key-controls-this-setters-admission) identifies this as the state14 setter: its historical name is not proof of beam-render identity. This establishes a real local consumer gate,
not complete beam rendering or physical capability.

| Type prefix |1.2.0 LightBeams fallback |1.2.0 FogSupport fallback |
|---|---:|---:|
| d |1 |0 |
| v |1 |1 |
| s or other |0 |0 |

The adjacent FogSupport reader `004b5844..004b586c` uses global `007a3a64`
as its fallback and stores **0 or4**, not0 or1. Do not transfer the final
version's different destination/normalization contract into this historical
build. In1.3.1, `004b580a..004b5851` instead supplies literal0 to both reads,
retaining the LightBeams0/1 and FogSupport0/4 normalizations and destinations.
Thus the fallback change is distinct from the configured values.

The pinned1.2.0 archive explicitly supplies both keys in all six driver INIs:
LightBeams1 for dgvoodoo/nglide/dx5/dx6/dx8,0 for softtri; FogSupport1 for
dgvoodoo/nglide/dx6 and0 for softtri/dx5/dx8. These are packaged defaults,
not observed effective configuration or proof of successful fog/beam support.

**Still unknown:** full downstream effects, compatibility with borrowed
renderers, visible results and the exact key-removal boundary. The final
pinned1.6.1 EXE lacks the case-insensitive ASCII literal; this does not prove
beam rendering was removed, or exclude another control mechanism. No target,
API, driver or instruction probe was executed; executable/database bytes
were preserved.

## Removed legacy DirectDraw enumeration wrapper and register adapter

The [read-only audit](scripts/audit_removed_ddraw_enumerator.py) retains
[complete bytes, imports, disassembly and bounded reference searches](evidence/audits/removed-ddraw-enumerator.json).
It explains all64 changed bytes in outside-function interval
`004ed904..004edbc0`: preceding636 bytes `004ed904..004edb80` are identical;
only adapter `004edb80..004edbb7` (55 bytes) and nine alignment bytes are
replaced by Modern NOPs. Adjacent COM helpers are not therefore classified as
rewritten or removed.

Original wrapper `004ebae0..004ebaf0` (16 bytes) saves ECX/EDX, pushes incoming
EAX as the enumeration context, pushes callback `004edb80`, and calls thunk
`00533e80`, which jumps through imported `DirectDrawEnumerateA` at `0053466c`.
Modern NOP-fills the wrapper as well and lacks that named static import.

The original adapter receives four stack arguments and forwards them to the
context-supplied callback using the game's register convention:

| Incoming callback argument | Forwarded register/behaviour |
|---|---|
| GUID pointer | EAX; if null, substitute a pointer to a local16-byte zero copy |
| Description pointer | EDX |
| Driver-name pointer | EBX |
| Enumeration context | ECX, invoked with `CALL ECX` |

The zero template is file-backed at `004eb420`. Four MOVSD instructions copy
it to the stack, assuming DF0. The substituted pointer is temporary; a
reconstruction must not expose it as permanently owned GUID storage. The
adapter saves/restores EBX/ESI/EDI, discards the callback return, sets EAX1,
and returns with `RET10h` (16 stack bytes). It does not locally promise
ECX/EDX/flags preservation or validate the callback pointer. Under normal
callback return, the adapter's return remains1 regardless of callback result.

**Reachability unresolved:** both executable code-section scans have zero
relative-E8 candidates targeting wrapper `004ebae0`, and whole-file searches
have zero literal pointers to that wrapper. The adapter has one original
literal pointer (the wrapper operand), none in Modern. These are bounded
encoding searches, not proof that the original path was dead: computed or
indirect entries and external callers remain possible. Static import removal
also does not exclude another dynamically resolved enumeration mechanism.
Required follow-up is a verified caller/registration or runtime trace before
claiming a changed device list or startup behaviour.

**Status:** done for these removed implementations and interval partition;
verified static evidence. No DirectDraw API, DLL, game or instruction probe
was run, and executable/saved database bytes were preserved.

## Historical nGlide configuration precedes provider loading

**Verified static mechanism; provider effects untested.** The [historical audit](evidence/audits/nglide-config-history.json), reproduced with `python3 analysis/scripts/audit_nglide_config_history.py`, pins the author-hosted1.2.0 archive and its `drivers/nglide/nglide.dll`, paired `drivers/dgvoodoo/voodoo2.dll` and nGlide `thrash.ini`. These are bundled adapter counterparts, not authenticated retail-original drivers. No archive member is executed.

| Step | Historical nGlide address | Observed instructions |
|---|---|---|
| Cached handle gate | `60001028..60001035` | Nonzero provider handle skips configuration/loading and reaches success. |
| Adapter-directory setup | `60001049..6000106b` | GetModuleFileNameA on the stored module handle; walk backward to the last backslash and leave destination immediately after it. |
| Added configuration call | `6000106b` | Calls complete helper `6000d8a0..6000d916`; the paired dgVoodoo loader instead begins copying the provider filename here. |
| Section read | `6000d8a8..6000d8ca` | Append `thrash.ini` using retained copy helper `600012c0..600012ca`; read `[NGLIDE]` into8192 bytes through GetPrivateProfileSectionA. |
| Name/value loop | `6000d8d0..6000d90d` | Build `NGLIDE_` plus ASCII-uppercased key in a256-byte temporary buffer; split on the first `=` and pass the unchanged value to SetEnvironmentVariableA at`6000d900`. Skip entries without `=`. |
| Provider request | `60001070..6000109c` | Overwrite the filename suffix with `glide3x.dll`; first attempt full adapter-relative path at`6000107f`, then bare name at`60001090` if loading fails. |

The complete118-byte configuration helper and217/212-byte loader bodies are retained with hashes, bytes and disassembly. The uppercase helper `60009850..6000985e` changes only ASCII a–z. Packaged settings translate as follows; these are requested strings, not verified nGlide enum semantics:

| Packaged key/value | Requested environment variable/value |
|---|---|
| Resolution=0 | NGLIDE_RESOLUTION=0 |
| Aspect=0 | NGLIDE_ASPECT=0 |
| Refresh=0 | NGLIDE_REFRESH=0 |
| Vsync=1 | NGLIDE_VSYNC=1 |
| Gamma=5 | NGLIDE_GAMMA=5 |
| Splash=0 | NGLIDE_SPLASH=0 |

**Release-note qualification:** MP120-025 has partial support for a concrete special adapter mechanism, without an exhaustive adapter difference map. MP120-026 has bounded static support: the writes precede both provider-load attempts on the cold-handle path. MP120-027 has partial support: an empty returned section exits without writes, but this helper does **not** clear inherited or earlier environment values. Removing the section therefore cannot by itself guarantee use of global nGlide settings; provider precedence, registry access and effective settings remain unverified. Reloading with an already cached provider also skips this helper.

Profile-section return, environment-write results and filename API failure are unchecked locally. Name construction has no local256-byte bound check. Missing sections, truncation and malformed input are not runtime-tested; ordinary well-formed packaged entries are the established interpretation. The helper preserves ESI/EDI but consumes incoming EDI as the filename-suffix destination; it is not an ordinary parameterless portable C routine. Its stack scratch storage does not establish safety of shared filename/environment/provider state or concurrent calls.

This is the historical special `[NGLIDE]` implementation in a DLL. The final EXE's generic `[ENV]` mechanism above is a separate, later configuration route. Neither static mechanism proves successful provider loading, visible rendering or original/Modern race compatibility.

## Early filename and device suffix interface, then driver-key rename

**Verified static parser/settings history; no DLL or INI execution.** The [driver-option audit](evidence/audits/driver-option-history.json), reproduced with `python3 analysis/scripts/audit_driver_option_history.py`, pins author-hosted1.1.0,1.3.1 and1.4.0 EXEs. It connects early filename/device parsing with the adjacent key-rename boundary, without claiming access to the1.0.0 predefined-alias implementation.

| Version | Captured INI key/default | Selected read branch |
|---|---|---|
|1.1.0 |`VideoDriver=dx5` fallback |`004b5748..004b5775`,48-byte buffer |
|1.3.1 |`VideoDriver=dx6` fallback |Same address range; selected-driver directory mechanism already documented above |
|1.4.0 |`ThrashDriver=dx6` fallback |`004b5a23..004b5a50`,56-byte buffer |

These are code-supplied fallbacks, not observed user settings or guaranteed loaded drivers. They establish **MP140-045's live1.3.1→1.4.0 key rename**, rather than relying on README text or a changed string alone. Captured branches have no alternate-key retry; computed/other caller aliases remain outside this inspection. The final directory/configuration mechanism is separately mapped earlier in this chapter.

Early1.1.0's complete151-byte parser`004b57d4..004b586b` accepts ESI pointing to a byte string. For ordinary nonempty inputs it writes path buffer`007a3a74`, prepending`.\` unless the input begins`.\` or`./`, converts`/` to`\` during copying, and terminates the copied filename when it consumes`@`. It appends`.dll` unless the copied path already ends in those four bytes. The preceding settings branch passes through an input-normalization helper; full locale/exception semantics are not requalified here. LoadLibraryA receives this buffer at`004b5775..004b5780`.

If the consumed delimiter was`@` and the following byte is ASCII0..9, the parser supplies format`%d` and destination`0055fdbc` to`004f0548`. No suffix/invalid-leading-byte path clears that device field locally. The scan return is not checked here; complete overflow, trailing-input and destination-state semantics remain dependencies. Thus filename and device setting can have separate retained lifetimes, as in the later [duplicate-option analysis](original-modern-command-line.md#duplicate-driver-options-name-and-suffix-are-separate-state), but their early storage is different.

For well-formed lowercase inputs, derived requests include`dx5`→`.\dx5.dll` without a local device write, and`dx5@2`→`.\dx5.dll` plus an attempted integer2 write. These are string/instruction deductions, not parser executions or successful device selection. Empty input returns before local path/class/device updates. The decrementing copy counter and extension look-behind are not a general safe-string contract for malformed or unusually short inputs; do not silently replace their access footprint during faithful reconstruction.

Early basename first-byte classification writes d→6, v→4, s→1, other→0 at`007a3a54`. **That address is not a stable cross-version semantic field:** final uses`007a3a54` for FogSupport and type mask`007a3a58`, while its numeric suffix goes to`007a3a70`, not early`0055fdbc`. A port must map contracts by version/producer/consumer, not reuse a final Ghidra label at an early address.

**MP110-001/002 advance to partial historical support:** the early retained EXE has a filename-based loader request and an integrated`@device` parser. The missing1.0.0 predecessor prevents independently verifying replacement of all advertised predefined aliases or removal of a separate VideoDeviceId option. **MP140-045 advances to bounded static support** for the adjacent live key rename only. DLL availability/export checks, actual selected hardware, full parser domains, user configurations and rendered results remain unverified. No DLL, parser, game, API, instruction probe or saved Ghidra database was executed or changed.
