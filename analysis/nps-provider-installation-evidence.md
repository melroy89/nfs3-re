# NPS provider lookup and local installation evidence

## Exact registry lookup

`ReadNpsLibraryPathFromRegistry` (`004a5880`) opens a key under HKLM and obtains the selected DLL-type value name from pointer table `0055eca0`. The key bytes at `0053da94` are exactly `SOFTWARE\EA-NPS\DLL`, including the hyphen and final separator. The prior symbol-derived spelling `SOFTWARE_EA_NPS_DLL` and older `SOFTWARE\EA\NPS_DLL` comment were inaccurate paths; the saved Ghidra comment is corrected.

The reader optionally appends `_DEVELOP` to the value name, queries the selected path and normalizes forward slashes. This establishes the lookup mechanism, not a selected provider file or successful library load.

## Bounded local observation

A read-only scan of the NFS3 Wine prefix's saved `system.reg` section headers found zero exact or descendant matches for `Software\EA-NPS\DLL`, compared case-insensitively after decoding the registry file's doubled separators. No unrelated registry values were decoded or emitted. This is the on-disk Wine registry snapshot; no live registry API was executed, and an in-memory Wine registry can differ.

A recursive filename inventory confined to the active game directory found19 DLL/ASI files and zero whose filename contains `nps`, case-insensitively. The files were graphics/audio/setup components by their names. A provider with an arbitrary name, a library outside that directory or a dynamic registry value is not excluded by that filename inventory.

Thus the saved prefix contains no registration at the exact key inspected, and the game tree supplies no NPS-named library. This does not establish an active provider, prove that none can be loaded, or test any public service. It also does not change the separate TCP built-in dialog/provider findings.

## Evidence and status

Selected executable SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Exact key bytes independently read with `objdump -s --start-address=0x53da94 --stop-address=0x53daac` from that executable. Ghidra decompilation reviewed the HKLM open, type-specific value-name selection and subsequent path handling. Saved registry and directory inventory were read without launching Wine or the game; no configuration, registry, executable or live-memory writes.

**DONE:** exact NPS registry lookup path and bounded local saved-registration/library-name inventory.

**OPEN:** live registry lookup, actual external provider identity/availability, RaceNet click route and any operating public lobby/server. No external service was queried.
