# PE resources: retained icon, new variants, media payloads and manifest

## Evidence and counts

The [resource audit](scripts/audit_pe_resource_payloads.py) independently verifies supplied-original, official-Modern and local-analysis executable hashes, enumerates every type/name/language leaf, parses icon-group references and manifest XML, and checks icon payload headers. The [manifest](evidence/audits/pe-resource-payloads.json) retains every payload RVA, file offset, byte count and SHA-256. This supplements the earlier whole-PE inventory without loading the game or extracting new C.

| Baseline | Resource leaves | Sum of leaf payload sizes | `.rsrc` raw bytes |
|---|---:|---:|---:|
| Supplied original | 3 | 1,548 | 2,048 |
| Official Modern | 13 | 111,527 | 112,640 |
| Local analysis target | 13 | 111,555 | 114,176 |

Payload-size sums exclude resource-directory metadata, names, alignment and other bytes outside the current payloads. Leaf counts are not feature counts. All enumerated leaves have language ID0; that metadata does not establish all displayed game text is language-neutral.

## Original icon survives under changed identifiers

Original icon payload `3/1/0` is exactly the same744 bytes as Modern `3/200/0`, SHA-256 `d571a0094014104eb8e7c4c80558f4836c9137c59506c46fa6f1a8ef3340d207`. Original icon group `14/32512/0` has one entry for that icon. Modern `14/ORIG.ICO/0` has the same group bytes except its final referenced icon ID changes from1 to200. The referenced payload size, dimensions, planes, colour count and bit depth remain equal. This is verified resource correspondence, not inference from the name `ORIG.ICO`.

Modern additionally has group `14/MAIN.ICO/0` with six entries:

| Icon ID | Image extent established by payload header | Group bit depth | Payload bytes |
|---|---|---:|---:|
| 100 | 16×16 | 32 | 1,128 |
| 101 | 24×24 | 32 | 2,440 |
| 102 | 32×32 | 32 | 4,264 |
| 103 | 48×48 | 32 | 9,640 |
| 104 | 64×64 | 32 | 16,936 |
| 105 | 256×256 | 32 | 24,070 |

For100..104, the BITMAPINFOHEADER has the stated width and twice the image height for the stored icon/mask layout. For105, the group width/height bytes are zero and the PNG IHDR independently records256×256. Every group entry resolves to an existing icon payload of the advertised byte size. Original's retained icon is32×32 with group bit depth4 and colour count16.

**MP100-035 has static payload support:** the stated16..256 size variants exist in Modern and are absent from the supplied original resource tree. Which image a shell/window chooses, perceived icon quality and historical introduction remain unverified. No icon was displayed by this audit.

## Added raw-data payloads have independently traced consumers

| Modern key | Bytes | Existing consumer evidence |
|---|---:|---|
| `10/ABOUT.QFS/0` | 47,372 | [Frontend page/resource arm](original-modern-frontend-page.md) maps the new page route and retained decode/render dependencies. |
| `10/SNAP.WAV/0` | 3,240 | [Screenshot feedback](original-modern-screenshot-feedback.md) maps the embedded shutter request after capture launch. |

These resources are absent from the supplied original tree. Their presence is independently verified here; the linked chapters establish selected uses and their limitations. Neither proves successful runtime decoding, completed screenshot output or audible/visible behavior under every backend. The existing raw reference exports and maintained C are unchanged.

## Application manifest: declarations and local-version distinction

Original has no type24 resource. Official Modern has `24/1/0`, a603-byte XML assembly manifest declaring:

- Assembly type`win32`, name`nfs3`, version`1.6.1.0`, architecture`x86`.
- `requestedExecutionLevel` attributes `level=asInvoker`, `uiAccess=false`.
- Dependency `Microsoft.Windows.Common-Controls`, version`6.0.0.0`, architecture`x86`, publicKeyToken`6595b64144ccf1df`, language`*`.

No DPI-awareness element is present in this complete manifest. These are declarations, not proof of actual loader behavior, applied privileges, control theme or Wine handling. **MP140-075 has static presence support**; introduction in v1.4.0 cannot be established from the original/final pair alone.

The local analysis target's manifest is byte-identical after replacing only assembly version`1.6.1.0` with`1.6.2.0`. Of all13 resource keys shared with official Modern, only `16/1/0` (version information) and `24/1/0` have changed payloads locally. Icons, `ABOUT.QFS` and `SNAP.WAV` remain byte-identical. The separately redirected local About string is outside these payload identities; see the [three-way provenance](original-modern-differences.md#1-three-way-provenance). Do not attribute local version preparation to the official patch.

**Bounded status: done; confidence: verified resource payloads, references, headers and XML.** Runtime resource selection, visual/audio results, OS enforcement and full version-history attribution remain unverified. No executable, Ghidra database, game configuration or raw reference export was modified; no target code ran.
