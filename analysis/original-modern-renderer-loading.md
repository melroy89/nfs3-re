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

## 4. Failure cleanup, return and fallback

Modern stores the module handle before export resolution. Missing export/null descriptor/mismatched `+8` all call `004f8514`. Cleanup exchanges `00564a6c` with zero (`004f8517`), calls FreeLibrary when the previous handle was nonzero (`004f8522`), then clears every destination slot through the same table (`004f8528..004f8537`). Loader clears EBX after failure, writes EBX to saved EAX at `[ESP+0x1c]`, and restores registers with POPAD (`004f850b..004f8512`): EAX returns zero or the loaded module handle. A successful load also registers cleanup via `004f7c20` at `004f84ff`; the exact registration facility is not re-established here.

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
