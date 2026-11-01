# Sound DLL: implementation bytes retained, headers/resources changed

## Baselines and reproduction

This compares `eacsnd.dll` from the [author-hosted reference bundle](original-modern-original-reference-bundle.md) with the final official Modern archive's root `eacsnd.dll`. The distinct reference removes the earlier acquisition gap caused by the local installed sound DLL already matching Modern. It is still not authenticated pristine retail provenance.

| Role | Bytes | SHA-256 |
|---|---:|---|
| Author-reference | 42,496 | `30288653eb2e0b59a3173530433a4adb8ea0dc66cdbc46aadf742dc53ab62b46` |
| Final Modern | 44,032 | `63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3` |

Run `python3 analysis/scripts/audit_sound_reference_final.py`. The [script](scripts/audit_sound_reference_final.py) verifies both archive/member hashes and compares the entire shared post-header file region. [Manifest](evidence/audits/sound-reference-final.json) includes all header differing-byte intervals, changed named fields/directories, section hashes, exports and resource identity/strings. No DLL is installed, loaded or invoked.

## Complete file-byte accounting

**Every byte from file offset400h through the original file's end at a600h is identical in Modern:41,472 shared post-header bytes.** Existing raw section locations/extents are unchanged. Differences are confined to the first1,024 file bytes and the appended1,536-byte resource section. The raw interval list uses file offsets, not VAs.

| Existing area | Result |
|---|---|
| Code section,29,696 bytes | Identical |
| Import section,1,536 bytes | Identical |
| Initialized data,6,656 bytes | Identical |
| Export section,1,024 bytes | Identical |
| Relocation section,2,560 bytes | Identical |
| All16 export names/ordinals/RVAs/forwarders | Identical |
| Entry RVA and preferred image base00400000 | Identical |

Section names `AUTO` and `DGROUP` become `.code` and `.data`. The BSS header's RVA c000h, raw-size field a00h, VirtualSize0 and raw-data pointer0 are unchanged. BSS is not read from file offset zero; initialized runtime contents are not established by this comparison. Neither file has a trailing overlay according to the parsed raw section extents.

For this pair there is **no changed implementation byte in the existing sound code or initialized data**, including the locations of its x87/control-word instructions. This is stronger than matching export names or file sizes. It does not prove identical execution under changed callers, input data, resolved APIs, callbacks, thread scheduling or ambient x87 state. The EXE's separately documented sound/policy changes remain relevant; this DLL result must not erase them.

## Header and directory changes

The manifest lists exact changed header fields. Notable examples:

| Field | Reference | Modern |
|---|---:|---:|
| Section count |6 |7 |
| OS version fields |1.11 |4.0 |
| Subsystem version fields |3.10 |4.0 |
| SizeOfImage |f000h |10000h |
| Stack reserve |10000h |100000h |
| Heap reserve |2000h |100000h |
| Heap commit |1000h |10000h |

The timestamp and checksum also change. These are PE metadata values, not authenticated dates, observed OS requirements, actual allocations or proven compatibility fixes. DLL loader treatment of reserve/commit values is not tested here.

The import directory keeps RVA9000h but its declared size changes574h→50h; the import-section bytes themselves remain identical. Modern adds an IAT directory declaration at RVA911ch, size cch, and a resource directory at RVA f000h, size600h. Those directory/header changes can affect loading or introspection independently of instruction equality; import-resolution equivalence is not inferred merely from equal raw bytes.

## Added version resource

Modern's added `.rsrc` occupies file offsets a600h..ac00h. Its single resource leaf is type16 (`VERSION`), identifier1, language0, payload at RVA f058h with size3cch. Version-string table `040904b0` includes:

| Metadata key | Value |
|---|---|
| FileDescription | `EacSnd (API v100003)` |
| FileVersion | `2016.05.02.0259` |
| ProductName | `Need For Speed III (Modern Patch)` |
| ProductVersion | `1.5.3` |

The comment attributes the base to an NFS III build dated1998/08/04. That is an embedded attribution claim, not authenticated retail/build provenance. In particular **the DLL's ProductVersion1.5.3 does not change the containing final package's independently established1.6.1 identity**. Component resources may retain older version labels.

## Acceptance and remaining questions

- **Done, verified:** exact artifact pairing; complete file-byte localization; equality of all preexisting raw sections and16 exports; changed header fields/directories; added resource identity and strings.
- **Unresolved:** pristine-retail authenticity, semantic effect of loader/introspection metadata, all runtime dependencies, actual sound quality/compatibility and historical introduction.
- **Not claimed:** whole-game sound equivalence, changed sound algorithms, identical FPU state at DLL entry, or that metadata addition alone fixes audio.

Two successful audit runs produced identical evidence. Existing EXEs, saved Ghidra state, raw C exports and maintained reconstruction sources were preserved. No new instruction probes, compilation or game/API calls were used.
