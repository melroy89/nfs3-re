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

## The API version call invalidates the capability cache

The shared `_iSNDdllversion@0` body at DLL RVA `0x13c4`
returns `0x100003` and writes −1 to DLL RVA `0xa8fc`.
The exported `_iSNDdirectcaps@4` at RVA `0x1428` tests
that cell at RVA `0x1438`. A nonnegative value is returned
immediately. A negative value enters capability discovery,
and its common result path stores EAX back to the same cell
at RVA `0x14bf`. Thus querying the version invalidates the
cached capability result. This behavior is shared by the
hosted original and final DLL code. The device-dependent
value returned by a fresh query remains unmeasured.

The cell at RVA `0xa8fc` starts at zero in file-backed
initialized data in both DLLs. It lies at offset `0x8fc`
within original `DGROUP` and final `.data`, both at RVA
`0xa000`. The negative sentinel is installed by the version
call. On the [checked game loader route](original-modern-startup-requirements.md),
the game calls that export before resolving the setup export.
A reconstruction that returns only the version number would
leave the cache's initial zero in place, allowing the
capability export to take its cached-result branch unless
another writer changed the cell first.

The game resolves `_iSNDdirectcaps@4` at `004e1e7c` and
stores the pointer to `009ef61c` at `004e1e8f`. The checked
indirect calls to that slot at `004e220a` and `004e22a9`
each test the returned value and take a separate branch for
values at or below zero. The local caller instructions and
pointer publication match in the hosted original and Modern
1.5.2, 1.5.3 and 1.6.1. Reproduce by inspecting those
instruction sites in each game EXE and resolving the export-name
pointer `00549db0`. The cache reset can therefore matter to a
subsequent game-side admission decision. Actual device results
and the order of these calls in a live session remain untested.

The two nonpositive-result branches have different local effects.
At `004e220a`, the wrapper returns a nonpositive capability
value unchanged. For a positive result it sets bit `0x10000`
before returning. At `004e22a9`, a nonpositive result jumps to
`004e235a`, skipping the downstream call through the
`_iSNDdirectstart@8` slot at `004e230f`. The branch stores the
raw value at `009ef60c`, sets the byte at `009ef607` to 1
and returns zero. These local return and state-update sequences
match the hosted original and the three Modern builds compared
above. A nonpositive value therefore matters to the audio start
path, but this check establishes no process-wide startup failure
or actual audio device outcome.

### Where the DLL sets the capability bit used by the game

On the fresh-query path, `_iSNDdirectcaps@4` initializes its
result DWORD to zero at DLL RVA `0x1431`. After three register
pushes, that DWORD is at `[ESP+0x94]`. The branch following the
successful capability method call at RVA `0x1477` tests the
DWORD at `[ESP+0x38]` at RVA `0x15ab`. If it is nonzero,
the instruction at RVA `0x15b2` sets bit 1 of the result's third
byte at `[ESP+0x96]`. This is bit `0x20000` of the result
DWORD, the same mask used by the
[game's saved-mode predicate](original-modern-config-loading.md#sound-mode-identity-d3deax-falls-back-to-stereo).
The relevant DLL code is shared by the hosted original and
final Modern Patch. The provider field's meaning and its live
values remain unverified.

The capability buffer starts at `[ESP+0x0c]` after the three
register pushes and has size `0x60`. That makes the tested DWORD
at `[ESP+0x38]` offset `0x2c` in the buffer. Matching the
size and field order to the
[Microsoft DSCAPS layout](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee416821(v=vs.85))
identifies the field as `dwMaxHw3DAllBuffers`, the maximum
hardware 3D buffer count. The bit can therefore indicate a
nonzero maximum even when the number of free 3D buffers is
zero. This is a static layout match. Actual driver values and
EAX effect availability remain unverified.

The hardware-buffer bit is provisional until the DLL chooses
a result path. At RVA `0x17ee` the routine tests the low nibble
of the result. At `0x1869` it also tests mask `0x3e` in the
second byte. A positive result that passes both tests reaches
the common return path at `0x148d` with bit `0x20000` intact
if it was set earlier. If either mask test fails, the fallback
at `0x17f8` overwrites the whole DWORD with −1 before querying
the buffer format. Successful fallback format matches can replace
it with a small format code, for example 1 at `0x183e` or 2
at `0x1898`. Thus a nonzero hardware-buffer maximum is enough
to set the intermediate bit. The returned bit also depends on
the later format checks and fallback outcome.
