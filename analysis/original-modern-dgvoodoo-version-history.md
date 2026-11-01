# Historical dgVoodoo bundle update:2.51 to2.53

**Confidence: verified packaged metadata/bytes. Work status: done for bounded version identity, not runtime compatibility.** The [audit](scripts/audit_dgvoodoo_version_history.py) verifies retained author-hosted1.5.3/1.6.0 archive hashes and reads five members per package. The [manifest](evidence/audits/dgvoodoo-version-history.json) records all ten member hashes, PE version strings and complete binary-config bytes. No wrapper or configuration utility was run.

## Component identity and boundary

| Member under `drivers/dgvoodoo/` |1.5.3 |1.6.0 |
|---|---|---|
| `glide3x.dll` |83,456 bytes; ProductVersion`2.5.1.0`; description identifies dgVoodoo2.51 Glide wrapper/Napalm |89,600 bytes; ProductVersion`2.5.3.0`; description identifies dgVoodoo2.53 Glide wrapper/Napalm |
| `dgvoodooconf.exe` |95,744 bytes; ProductVersion/FileVersion`2.5.1.0`; setup description2.51 |101,376 bytes; ProductVersion/FileVersion`2.5.3.0`; setup description2.53 |
| `voodoo2a.dll` |69,120 bytes |Entire file identical |
| `thrash.ini` |54 bytes |Entire file identical |
| `dgvoodoo.conf` |127-byte binary file |128-byte binary file; changed |

The wrapper's **FileVersion remains`3.10.0.0`** in both packages, while ProductVersion changes2.5.1.0→2.5.3.0. Those fields describe different identities; reading FileVersion alone would miss the bundle update or mistake the Glide-interface version for the dgVoodoo product release.

This supports **MP160-014's packaged dgVoodoo2.53/Napalm identity** within the inspected archive. It is not a new NFS EXE implementation or a rewrite of the unchanged game-facing adapter. The resources are component self-identification, not an independently authenticated upstream build/signature or a demonstration that the game loaded this provider.

## Binary configuration and unresolved semantics

Both config files begin with ASCII`DEGE`; the manifest preserves their entire bytes, changed shared offsets and appended byte. Their size/layout changes alongside the provider update. No field meaning is inferred from matching version-looking bytes, and the config is not treated as a text INI. Parser ownership, field semantics, effective defaults and compatibility with mixed-version tools remain unresolved.

The unchanged thrash.ini/adapter establish a component boundary only. The provider itself and setup utility change; their code-level differences, dynamically resolved APIs, actual graphics effects, performance and OS/Wine compatibility are not established by version metadata. Those require separate provider analysis or scoped runtime evidence if pursued.

**Catalog treatment:** MP160-014 advances vendor-only→bounded static support for bundled version identity. This does not promote other dgVoodoo claims or authenticate earlier WIP builds. No installed game files, executables, saved Ghidra database, resources or runtime configuration were changed.
