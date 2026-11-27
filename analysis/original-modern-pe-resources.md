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

**MP100-035 has static payload support:** the stated16..256 size variants exist in Modern and are absent from the supplied original resource tree. The retained 1.0.0 comparison below dates these variants. Which image a shell/window chooses and perceived icon quality remain unverified. No icon was displayed by this audit.

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

No DPI-awareness element is present in this complete manifest. These are declarations, not proof of actual loader behavior, applied privileges, control theme or Wine handling. **MP140-075 has static presence support.** The retained release comparison below dates the manifest to 1.4.0.

The local analysis target's manifest is byte-identical after replacing only assembly version`1.6.1.0` with`1.6.2.0`. Of all13 resource keys shared with official Modern, only `16/1/0` (version information) and `24/1/0` have changed payloads locally. Icons, `ABOUT.QFS` and `SNAP.WAV` remain byte-identical. The separately redirected local About string is outside these payload identities; see the [three-way provenance](original-modern-differences.md#1-three-way-provenance). Do not attribute local version preparation to the official patch.

**Bounded status: done; confidence: verified resource payloads, references, headers and XML.** Runtime resource selection, visual/audio results, OS enforcement and full version-history attribution remain unverified. No executable, Ghidra database, game configuration or raw reference export was modified; no target code ran.

## Resource history across retained releases

Comparing resource keys of the form type/name/language and SHA-256 of their payload bytes gives the following release boundaries. Extract `nfs3.exe` from each retained archive with `7z x -so <archive> nfs3.exe`. Use the resource-directory traversal in the linked audit to repeat the comparison. This dates payload and key changes. Resource RVAs and directory order can move independently.

| Retained release | Resource change |
|---|---|
| 1.0.0 | Eleven leaves. Numeric group `14/32512/0` references all six 16×16 through 256×256 variants, and `14/32513/0` references the original icon payload, now at `3/106/0`. Numeric resource `10/200/0` and version information are present. |
| 1.1.0 | Same eleven keys. Only numeric resource `10/200/0` and version information change. |
| 1.2.0–1.3.1 | Numeric resource `10/200/0` and version resource `16/1/0` change in every retained release. Main group `14/32512/0` and icon `3/105/0` also change in 1.3.0. |
| 1.4.0 | The icon payload moves from `3/106/0` to `3/200/0` unchanged. Named groups `MAIN.ICO` and `ORIG.ICO` replace numeric groups `32512` and `32513`. Numeric resource `10/200/0` is removed. Named `ABOUT.QFS`, `SNAP.WAV` and manifest `24/1/0` appear. |
| 1.5.0–1.6.1 | The resource keys stay fixed. About and version payloads change in every retained release. Manifest bytes change in 1.6.0 and again in 1.6.1. The screenshot WAV and all icon and group payloads remain byte-identical from 1.4.0 through 1.6.1. |

The original icon's three IDs identify identical 744-byte payloads. The [About page comparison](original-modern-frontend-page.md#numeric-about-resource-in-131) identifies the early numeric resource consumer in 1.3.1. The same report compares decoded image bytes across the retained releases. In-game rendering remains unverified. The [retained 1.0.0 archive](original-modern-dll-candidates.md#recovered-100-package-separates-code-changes-from-renames) contains an EXE with SHA-256 `988fbf599af256d1486bef967959893c6b26c9fa8ed21b76310bbb7798b4d9df`.

For each group, hash the group payload followed by each referenced image payload in group-entry order, resolving images in the same resource language. The digests below cover the group and image bytes. The table records resource names and IDs separately.

| Retained versions | Group | SHA-256 of group and image payloads |
|---|---|---|
| 1.0.0–1.2.0 | `32512` | `092670f17c153cf11c1bb39de39d474d25cfc87f9e572f96ec826c8f0a052c8c` |
| 1.3.0–1.3.1 | `32512` | `670e08886a4a331cba65767622f6d222147f7f7e33d9e219dd68d40e7afa48e6` |
| 1.4.0–1.6.1 | `MAIN.ICO` | `670e08886a4a331cba65767622f6d222147f7f7e33d9e219dd68d40e7afa48e6` |
| 1.0.0–1.3.1 | `32513` | `4b8d1aecbd37b4c007b2e7403cd431f788027c3eb3f0b367c8beedf1942c9545` |
| 1.4.0–1.6.1 | `ORIG.ICO` | `068d579cd61973df8e838f5cfc8059dfd58e8e29bcdc5d7a826dc5ce4a460d76` |

The 603-byte manifest first appears in retained **1.4.0** and is byte-identical through 1.5.3. Its own assembly version stays `1.4.0.0` across those builds. The only payload changes in 1.6.0 and 1.6.1 replace that assembly version with `1.6.0.0` and `1.6.1.0`, respectively. The execution level, UI access, Common Controls dependency and absence of a DPI-awareness declaration are consistent across these manifests.

| Manifest version | Payload SHA-256 |
|---|---|
| `1.4.0.0` | `a74a453c565f3b485ab30c359a7b61f8146bd8f145d230653d47c925e283d4ec` |
| `1.6.0.0` | `5b225855803ab1a36494e46f4edd2e1003a72957183392ea1a6b5be3157c624a` |
| `1.6.1.0` | `9dab66dde3ecb916b9ba533b478e5059ea0f190b2dd65948fa3edc65c307c45c` |

## Version resource identifies the retained builds

The fixed product version in resource `16/1/0` matches the archive's release label with an appended zero in every retained Modern executable. The product version string matches the three-component label. The file version is a separate date-and-build field.

| Retained Modern release | File version string |
|---|---|
| 1.0.0 | `2015.05.17.0034` |
| 1.1.0 | `2015.05.23.0039` |
| 1.2.0 | `2015.06.10.0063` |
| 1.3.0 | `2015.06.22.0078` |
| 1.3.1 | `2015.07.14.0085` |
| 1.4.0 | `2016.02.16.0164` |
| 1.5.0 | `2016.03.20.0227` |
| 1.5.1 | `2016.03.25.0235` |
| 1.5.2 | `2016.04.10.0241` |
| 1.5.3 | `2016.05.03.0262` |
| 1.6.0 | `2016.09.22.0286` |
| 1.6.1 | `2016.10.28.0301` |

The supplied original reports fixed file version `2.0.0.0` and fixed product version `1.0.0.1`, with strings `27, 2.0` and `3, 0`, respectively. Read the fixed pairs from `pefile.PE(...).VS_FIXEDFILEINFO` and the strings from `FileInfo` → `StringTable`. A manifest alone cannot distinguish Modern 1.4.0–1.5.3 because those builds share the manifest version. Use executable SHA-256 for exact identity.
