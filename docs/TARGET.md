# Analysis target provenance

Recorded on 2026-10-10.

## Upstream and local version

The maintainer obtained the Modern Patch from [VEG's NFS III project page](https://veg.by/en/projects/nfs3/). That page identifies the published release as **v1.6.1, dated 2016-10-28**; the local patch readme also names that version.

The research target is a local **1.6.2 preparation**, based on that patch. The maintainer describes the small changes as copyright-line and version preparation in `nfs3.exe` and the menu. The existing local scratchpad additionally records updated attribution/About text, Windows version metadata, and the setup-menu website/version prompt. This document does not assert a gameplay change or an upstream 1.6.2 release.

The local scratchpad remains in the separate Wine game installation, outside this checkout. Published findings and retained evidence are indexed in [analysis/](../analysis/README.md). Older scratchpad claims were not independently rerun during initial repository preparation.

## Current executable

| Property | Value |
| --- | --- |
| Filename | `nfs3.exe` |
| Repository location | `nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe` |
| Size | 1,699,840 bytes |
| SHA-256 | `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb` |
| Ghidra installation | 12.1.4 |
| Open program language | `x86:LE:32:default` |
| Open program compiler | `windows` |
| Open program image base | `0x00400000` |

The file size and digest were measured directly during preparation. Language, compiler, and image base were read from the active Ghidra program; a full comparison of database bytes with the executable was not performed.

On Linux, calculate a local fingerprint with:

```sh
sha256sum /path/to/nfs3.exe
```

On Windows PowerShell:

```powershell
Get-FileHash C:\path\to\nfs3.exe -Algorithm SHA256
```

The upstream download alone does not reproduce the local modifications. Before publishing transferable annotations, document reproducible modification instructions or a suitable original helper script, and verify the resulting hash. The standalone executable and `FEDATA/MENUS/setup.mnu` are tracked under `nfs3_decomp.rep/Electronic Arts/Need For Speed III/`. All other installation files remain ignored. The menu contains `Visit veg.by (v1.6.2)` and has SHA-256 `d55b7c5a1e169408ddd20e8033f429be35f77614b02b7a6756363e1bf16f2782`. Both tracked files match the copies used in the local Wine installation; imported executable bytes also remain in the Ghidra databases.


## Separate original/backup comparison artifact

The installed `nfs3_org.exe` is present both in the NFS3 Wine prefix and the ignored game directory beside the tracked patched executable. The two copies have SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and size 1,589,248 bytes. Its supplied original/backup identity is distinct from independently establishing an unmodified retail release/version.

Limited earlier work compared its RaceNet callback registration; it was not the main Ghidra reconstruction/probe target. A later [precision-policy comparison](../analysis/og-modern-x87-precision.md) directly inspected both binaries and verified original single-precision control blocks removed by Modern Patch. That does not authenticate every original-version provenance claim or establish replay/multiplayer compatibility. The current saved Ghidra project remains Modern Patch analysis.
