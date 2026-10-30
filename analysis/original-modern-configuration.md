# Original versus official Modern Patch: configuration lookup

## Scope and artifacts

This read-only comparison covers the official package's game-settings INI reader, its environment-name helper, and the settings caller at `004b5580`, against the supplied `nfs3_org.exe`. It does not cover renderer `thrash.ini` parsing, runtime environment mutation, or every original registry call site.

| Artifact | SHA-256 |
|---|---|
| Supplied original `nfs3_org.exe` | `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` |
| Official archive `nfs3.exe` (`analysis/captures/modern-differences/upstream/package/nfs3.exe`) | `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6` |
| Installed and archive `readme_en.txt` | `02bf4684dce1073b4fe7c00c747f020b43508b0cf1407b5dc3f3b864ea46d81d` |

The two README files are byte-identical. The official README says the patch moved system settings to INI files, and its v1.2.0 release note documents the rule: when an INI setting is absent, check `SECTION_SETTINGNAME` in the environment, then use the default if no environment value exists (example: `NFS3_NOMOVIE`). This documentation agrees with the official executable's call sequence below.

## Official Modern Patch code path

`LoadGameIniSettings` at `004b5580..004b5708` is identified in the official executable capture. It sets `EBP` to the section string `NFS3`, places setting-key pointers in `EBX`, and calls the integer reader `004fb6f0` for its values. It also calls the string reader `004fb714`. The constant pool at `0053f5e0..0053f6e4` contains `NFS3`, keys including `NoErrorReporting`, `SingleProcAffinity`, `ThrashDriver`, `NoMovies`, `OwnHeapLimitMb`, and `AllowHugeTextures`, and the string default `dx7`.

The integer reader at `004fb6f0` calls `LookupIniEnvironmentOverride` (`004fb734`) with section/key, and if that returns a non-null string, converts it through `004f0430`. It then calls the imported `GetPrivateProfileIntA` thunk at `00534670`, passing the converted environment value as the API's default argument, followed by key, section, and filename-buffer address `007a263c`. Thus an explicit INI value wins; the environment value supplies the default used when the INI key is absent; the caller-provided default remains in force when neither source supplies a value.

The string reader at `004fb714` has the corresponding sequence: call the environment helper, substitute its returned pointer when non-null, then call imported `GetPrivateProfileStringA` at `00534674`, passing that pointer as the default string, along with the key, section, output buffer/length, and filename-buffer address `007a263c`. This yields the same precedence: INI value, then environment value, then caller default.

`LookupIniEnvironmentOverride` at `004fb734..004fb769` allocates a 256-byte local buffer, uppercases/copies the section, writes `_`, uppercases/copies the key, then calls `0050ead0`. That lookup walks the environment-entry pointer list rooted at `[00a0b154]`; it compares the candidate name over the constructed name length and requires `=` at the boundary, returning a pointer to the value after `=` on a match. Its comparison calls `00523d10`, which compares folded characters. The resulting spelling matches the documented `SECTION_SETTINGNAME` convention. The local buffer/copy-length caveat recorded in [INI environment-key construction](ini-environment-contract.md) still applies to arbitrary overlong inputs; reviewed direct settings callers use fixed constants and section `NFS3`.

## Original-to-Modern differences and retained bytes

The supplied original imports `RegOpenKeyExA` and `RegQueryValueExA`, and does not import `GetPrivateProfileIntA` or `GetPrivateProfileStringA`. The official executable imports the two profile APIs and implements the INI/environment fallback above. This is consistent with the README's statement that system settings moved from the registry to INI. The import-table change is binary evidence for the configuration architecture; this bounded review did not trace every original registry query back to each individual setting.

At the named official caller address `004b5580`, the original bytes are a data/pointer area, not the corresponding `LoadGameIniSettings` routine. The original-versus-Modern function audit records `004b5580` as `different_same_VA_bytes` and `original_entry_identified_by_autoanalysis: false`. Therefore the official caller must not be treated as a byte-for-byte edit to an original function at that virtual address; the old and new settings paths are laid out differently.

There is also a concrete retained-code witness in the vicinity: bytes at `004fb790..004fb81a` are identical between the supplied original and official Modern executable (139 bytes; SHA-256 `873e147b44b3a605e46f81e39ec3837a2f3ffd125f00d27e75f6fbc4bfa837f8`). The disassembly at those addresses is byte-for-byte the same. This establishes that the official INI/environment implementation was placed beside retained original bytes in that region; it does not establish that the full configuration loader or all surrounding data was reused.

## Retained instruction evidence

The [configuration evidence manifest](evidence/audits/original-modern-configuration.json) records exact hashes and half-open spans for the caller, readers, environment search/comparator and unchanged-byte witness in both binaries. Raw `objdump -d -Mintel --start-address=... --stop-address=...` captures remain under ignored `analysis/captures/modern-differences/configuration/`. All addresses are virtual addresses in image base `00400000`; static instruction inspection only.

## Evidence limits

- This is a static comparison of these exact supplied-original and official-package executables. It is not a claim about every retail revision or later Modern Patch build.
- The environment helper's construction and lookup behavior are statically visible. No process environment was changed or queried at runtime.
- `007a263c` is pushed as an immediate buffer address (not loaded indirectly from a pointer slot) for the filename argument passed to the INI APIs. This report does not resolve every initialization path that assigns it or prove disk-level INI loading.
- Original registry imports, new INI calls and the README support the system-setting migration, without proving elimination of registry use. Specific original registry key/value mappings have not been reconstructed here.
- The separate renderer configuration (`thrash.ini`) is out of scope; its parsing and environment-variable setup should not be conflated with game-setting fallback.
- The locally installed `nfs3.exe` has a different fingerprint from this official-package executable and is not used for this comparison.

No executable, runtime configuration or Ghidra project was modified. No game or instruction probe was run.
