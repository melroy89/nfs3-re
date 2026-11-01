# Original versus Modern: language-table marker and fallback strings

## Evidence boundary

Static supplied-original/official-Modern comparison, with exact fingerprints in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_language_table_difference.py`. The [manifest](evidence/audits/original-modern-language-table.json) retains loader/lookup/release instruction spans, six filename entries, the Modern marker and all 27 fallback entries. No language asset was loaded or rendered; no game/instruction probes were executed.

## Loader ownership and marker test

Both use filename pointers at `00563a68` for `text.eng`, `text.ger`, `text.fre`, `text.spa`, `text.ita`, `text.swe`, appended to directory buffer `007a2eb4`, and load the result through `004e0ec0`.

Original `004d1750` checks a signed upper index bound of 6, releases an existing resource before loading, then stores the new pointer at `00563a80`. That local bound alone is not a proof that every index is valid; the six inspected names and caller validation must be reconciled separately. Modern's rewritten routine indexes its table without that same local guard, relying on upstream selection, which is not re-audited here.

Modern loads first, then exchanges the pointer with `00563a80` and releases the prior nonzero pointer. It inspects the new table (`004d1788..004d17a5`):

1. Require first DWORD to be unsigned **greater than `0x1e24` (7716)**.
2. Read the relative string offset stored at byte offset `0x1e24` and compare that string with embedded **`v1.6.0`** through `004ee310`.
3. Store flag **`007a1b94=0`** on a matching marker; otherwise store **1**.

The first DWORD acts as the offset-table coverage boundary in this code. It is not independently established as the whole file length. The check locates string index **1929 (`0x789`)**; it is a language-table compatibility marker, not the running executable's exact patch release version.

No explicit null-new-resource or full payload-bound check precedes these dereferences in the inspected routine. Resource loading, allocation and validated offset/payload contracts remain dependencies. The marker comparison is not a complete parser validation.

## Lookup gains guarded fallback

Original `004d1850` routes signed IDs below `0x7a7` through direct relative-offset lookup, with no local table-coverage check; larger IDs go to dynamic lookup `004d17b0`.

Modern first compares the ID **unsigned** with **`0x7a2` (1954)**. Larger IDs go to dynamic lookup. Otherwise it computes offset `ID*4` and:

- If mismatch flag is nonzero and offset is **at least `0x1e24`**, choose embedded fallback.
- Otherwise require `[table] > offset` unsigned; if true, return `table + [table+offset]`.
- If that coverage test fails, choose embedded fallback too.

The fallback base is **`0053d310`**, with index derived from `offset - 0x1e20` when that difference is signed-positive, or zero otherwise. For ordinary handled IDs this maps **1928..1954** onto **27 entries**; lower IDs that fail coverage select entry zero (empty string). In particular, mismatch-marked tables fall back from ID 1929 onward even if their offsets appear present.

The manifest retains exact entries. Examples include empty entry zero, `v1.6.0`, `km`, `Port`, the legacy/modern port explanation, occupied-port notice, `Menu Sounds`, `Fog` and `Rear View Detail`. These are executable-embedded fallback text, not evidence that the selected external language file contains the matching translation.

The direct lookup path still trusts the stored relative offset and NUL termination. A passing table-coverage check does not prove an in-bounds string payload. Negative IDs are routed differently by the changed signed/unsigned entry condition; arbitrary invalid-ID equivalence is not claimed.

## Dynamic IDs and release helper also change

In `004d17b0`, the display-mode label range changes from original **`0x7a8..0x7bc`** to Modern **`0x866..0x8ca`**, with callback target changing from `00448400` to `00448428`. This links to the expanded [display-mode menu](original-modern-display-modes.md), rather than treating these IDs as external language-table offsets. Other car/resource dynamic-ID routes retain their surrounding structure in the inspected span; full semantic equality is not asserted here.

Original release helper begins at `004d1880`; Modern begins at `004d1890`. Modern exchanges the shared pointer with zero before conditionally freeing it; original frees first, then clears the pointer. This establishes ordering, not thread-safe language reload or successful ownership under every alias.

## Upstream language selection: install.win becomes INI setting

Original selector **`004a6e10..004a6f60`** opens embedded filename `install.win` with mode `rt`, reads/parses lines and compares the resulting buffer at `007a2634` against six strings from `0055fd24`. Its final comparison uses each candidate name's length through `004eb390`, so it is a prefix comparison on the inspected path, not an independently verified exact-token check. If none match it explicitly supplies EAX0 to `004b5e50`; the [verified diagnostic/exit follow-up](original-modern-startup-requirements.md#corruption-diagnostic-callers-supply-zero-or-a-language-value) establishes that this is a termination route, so its apparent later index6 store is not ordinary returning behavior. Open failure returns zero before that final selection route.

Modern selector **`004a6e68..004a6ec0`** instead calls configuration string reader `004fb714` with section **NFS3**, key **Language**, fallback **english**, destination **`007a2634`** and count **8**. The [configuration comparison](original-modern-configuration.md) documents the reader's INI/environment/caller-default precedence. It then lowercases ASCII in place through `004f93dc`, and compares against the six complete names:

`english, german, french, spanish, italian, swedish`

A match stores its index **0..5** at `007a3a50`. No match copies `english` to the buffer and stores zero. This guarantees a six-entry index from the ordinary selector return path, without relying on the resource loader's removed local guard. String truncation follows the reader's count argument; no overlong-setting test was run.

Modern config initialization later copies `007a3a50` into active field **`006fbb4c`** (`00472aff..00472b08`). Both inspected loader callers read EAX from that active field before calling `004d1750` at **`0044b28a`** and **`0044b976`**. This provides a producer-to-consumer route for normal startup; it does not exclude later writes, saved-state restoration or indirect callers changing the active field. The INI selector index is not a global proof for arbitrary loader inputs.

## Catalog conclusions and limits

**MP160-013**, checking language-file version: the marker test, compatibility flag and lookup fallback are statically supported. This routine does not visibly reject the entire file solely because the marker differs; it changes selected lookup behavior.

**MP153-008**, corrected fallback regression: the historical comparison below now verifies a mismatched admitted range and fallback table in1.5.1/1.5.2, bounded by a consistent predecessor and successor. Original versus final alone could not establish this history.

Pending: all later active-index writes, actual localized asset contents, all IDs/consumers, null/malformed input paths and rendered translations. Historical release attribution and complete format compatibility remain separate from this marker mechanism.

## Historical fallback regression: v1.5.0 through v1.5.3

The author-hosted version archives are now retained for all four releases. [This audit](scripts/audit_language_fallback_history.py) checks archive/EXE/readme hashes and internal banners, retains disassembly, decodes embedded fallback entries and records conditional out-of-table reads in [its manifest](evidence/audits/language-fallback-history.json). Reproduce with `python3 analysis/scripts/audit_language_fallback_history.py`; acquire missing archives from each manifest URL into its specified ignored path first. These are author-hosted artifacts with internal version labels, not signature-authenticated publisher releases. No EXE or language file was executed or loaded.

All four historical lookup bodies occupy `004d1850..004d187e` (46 bytes, exclusive end). Only their upper-ID immediate differs. IDs above that unsigned limit call dynamic lookup `004d17b0`. Otherwise the function computes `offset = ID*4`, reads table pointer `00563a80`, and returns the external relative-offset string when `[table] > offset`. On failed coverage it instead selects fallback base `0053d294`, indexes by `max_signed(offset-0x1e20,0)`, adds the DWORD found there to that base and returns the resulting pointer. This historical code has no1.6.0 marker test; do not import the final release's mismatch-flag behaviour into it.

| Release | Highest ordinary ID | Embedded offset entries | IDs covered by embedded table | Result when external coverage fails |
|---|---:|---:|---|---|
|1.5.0 |1935 (`0x78f`) |8 |1928..1935 | Admitted fallback range fits |
|1.5.1 |1940 (`0x794`) |9 |1928..1936 | IDs1937..1940 index beyond offsets |
|1.5.2 |1940 (`0x794`) |9 |1928..1936 | Same four-entry mismatch |
|1.5.3 |1946 (`0x79a`) |19 |1928..1946 | Admitted fallback range fits |

The table sizes are corroborated by the first payload offset (0x20/0x24/0x24/0x4c), each decoded entry and the start of the string payload, rather than inferred from lookup limits. In1.5.1/1.5.2, index9 starts at fallback+0x24: those bytes are already string data. The four DWORDs read for IDs1937..1940 are `65685400`, `726f7020`, `73692074` and `726c6120`, fragments of the embedded text rather than offsets. Adding them to the fallback base yields pointers outside every mapped PE section in the inspected image. The lookup returns those pointers; it does not dereference their strings itself. A crash or corrupt display depends on subsequent consumers and process mappings and was not observed here.

V1.5.3 supplies valid entries for those IDs: `Rear View Detail`, `Rear View From`, `Active Camera`, and `In Car Camera`, followed by six music-mode entries. This repairs the specific structural overrun while expanding the supported ID range. The predecessor/adjacent versions support the release note's introduction in1.5.1, persistence through1.5.2 and repair in1.5.3 for this mechanism. It is not evidence that every fallback failure, localized asset, malformed offset or caller was corrected.

MP153-008 therefore moves from unresolved history to **bounded static support**. Whether a particular old language file reaches these IDs requires its coverage and caller inputs; full rendered localization remains a separate validation layer. The final1.6.x marker/fallback scheme described above is a later change with a different base and entry set.

## Removed defaults-time language mapper: 00472250

The [default-block audit](scripts/audit_removed_default_block.py) now captures
complete original mapper `00472250..00472300`, its complete comparison helper
`004ee310..004ee3b1`, and the Modern publication span in
[the evidence manifest](evidence/audits/removed-default-block.json).
Original default initialization calls the mapper at `00472561`; Modern
replaces that call with a jump over the following profile/audio block.

The mapper compares buffer `007a2634` against six literal lowercase names at
`0053afd8 + i*8`: english, german, french, spanish, italian, swedish.
A matching string writes ordinal0..5 to `006fbb4c`. These are six sequential
exact case-sensitive comparisons, not the separate installation reader's
prefix comparison. If none matches, this mapper makes no local destination
write; it does not supply a fresh English fallback. Its comparator's DWORD
reads also mean byte-level string equality is not an arbitrary-pointer safety
contract; this analysis assumes normal valid storage.

Modern's previously documented INI selector performs lowercase normalization,
validates the same six names and explicitly falls back to English. At
`00472aff..00472b09`, config initialization loads validated selector
`007a3a50` and writes active index `006fbb4c`. Thus removal of the old mapper
call is consistent with relocated language selection, not removal of language
support. It also establishes the language identity of the branch operand in
the immediately following original profile-default block. The separate
[HUD/unit comparison](original-modern-hud-layout.md#default-speed-units-header-selector-reaches-the-digital-kph-path)
qualifies the MPH/KPH consequence; no newly inferred unit conversion is needed.

**Status:** done for the removed call target, six-name mapping, local no-match
contract and Modern publication route; verified static evidence. Installation
buffer provenance on every caller, later active-index writes, actual assets
and runtime fallback outcomes remain separate. No target, language asset or
instruction probe was executed; executable/database bytes were preserved.

## Original installation reader also produces the remote-prefix source

The expanded [language audit](scripts/audit_language_table_difference.py)
asserts the filename/mode, zero-fill setup and indexed-copy instructions in
[its manifest](evidence/audits/original-modern-language-table.json), reusing
the already captured complete original reader `004a6e10..004a6f61`.
This closes the selected producer gap for buffer `007a26b4`.

Original's reader clears5120 bytes from `007a2634`, opens literal
`install.win` with mode `rt`, and repeatedly reads into its local buffer with
count127. It removes LF and CR when found, skips a processed empty buffer,
and copies each retained NUL-terminated result to:

`007a2634 + (record_index << 7)`

It increments the record index after each copy. Consequently:

| Processed record | Destination | Verified consumer |
|---:|---|---|
|0, first nonempty result | `007a2634` | Existing language-name selection |
|1, second nonempty result | `007a26b4` | Original six-byte `remote` prefix classifier `004b62a0` |
| Later results | Base+128×index | Consumers not qualified here |

The [config-load producer chain](original-modern-config-loading.md#mediaaudio-gate-snapshots-the-original-remote-prefix-classification)
then stores that classifier's0/1 return at `006fbb54`. This identifies the
source as installation-file record data; it does not establish that `remote`
means multiplayer, a remote player, a network mount or any other precise
external mode. Those meanings require separate evidence.

The cleared extent accommodates40 slots of128 bytes, but the shown copy loop
has **no local40-record bound**. Do not describe the zero-fill size as enforced
input admission. The read helper's return is not checked before scanning the
buffer; its exact failure and truncation contract is not established here.
“Second nonempty result” therefore describes ordinary successful processing,
not a guarantee about arbitrary long lines, failed reads or malformed files.
Record/address arithmetic and byte copies also retain machine-width/access
requirements in a faithful reconstruction.

The Modern selector documented above reads only the language setting from
INI instead of this installation-record path, and its config-load tail
explicitly writes0 to `006fbb54`. No whole-program exclusion of other file
readers, aliased/bulk field writes or later initialization is claimed.

**Status:** done, verified static for this original source producer and its
classifier/publication link. Actual file contents/provenance, all callers,
read-helper failure/truncation, other record consumers, later writes and
runtime media/audio effects remain unresolved. No installation file was
opened through the target, and no game/API/instruction probe was executed.

## Installer settings move to early INI, but RemoteOnly is not retained in final

**Verified static local configuration paths; startup success untested.** The [installer-settings history audit](evidence/audits/install-settings-history.json), reproduced with `python3 analysis/scripts/audit_install_settings_history.py`, pins supplied original, author-hosted1.1.0 and official final EXEs. It reuses the original processed-record ownership and remote-prefix publication above, plus the [config-tail comparison](original-modern-config-loading.md#mediaaudio-gate-snapshots-the-original-remote-prefix-classification).

| Settings stage | Language source | Remote/media gate source |
|---|---|---|
|Supplied original |First nonempty processed`install.win` record |Second record's six-byte`remote` prefix classification; published to`006fbb54` |
|Modern1.1.0 |`[NFS3] Language`, default`english`, capacity8, profile-string API |`[NFS3] RemoteOnly`, integer default0, normalized nonzero→1; published to`006fbb54` |
|Official final1.6.1 |INI language selector, already mapped above |Config-tail literal0 store; early RemoteOnly helper span replaced by NOPs |

Early complete33-byte helper`004b62a0..004b62c1` sets EBP to section`NFS3`, EBX to key`RemoteOnly`, EDX0 and calls`004fb6f0`. That complete19-byte wrapper passes the filename buffer`007a263c` to imported GetPrivateProfileIntA. The result is tested:0 remains0, any nonzero becomes1. Config tail`00472b38` calls this helper and`00472b43` publishes EAX to`006fbb54`, retaining the original caller's destination while changing the source.

Early language selector`004a6eb0..004a6f0a` supplies key`Language`, default`english`, destination`007a2634` and capacity8 to`004fb704`. That complete21-byte wrapper calls GetPrivateProfileStringA using the same filename buffer. The selector then normalizes/compares language names and publishes the selected index; full string/failure behavior remains governed by the linked language analysis. Filename-buffer initialization is a separate startup-path requirement; a static buffer address is not an observed valid filename.

Final's checked config tail`00472b1d..00472b2b` clears ECX and writes zero to`006fbb54`. The former early33-byte RemoteOnly helper span is NOPs, and the final file contains no case-insensitive ASCII`RemoteOnly` literal. This is a local changed producer plus a bounded string census, **not proof that every later alias/bulk write or computed setting name is absent**. The exact intervening release removing RemoteOnly is not dated here.

A literal-search qualification matters: early1.1.0 lacks the lowercase filename literal but retains **one case-insensitive INSTALL.WIN occurrence**, within`RENDITION not yet supported (INSTALL.WIN)`. This diagnostic is not itself a file-open call, nor is its presence evidence that the new INI path still depends on that file. Its complete caller/lifetime is not qualified by this audit. Final has no case-insensitive ASCII occurrence. Original file reading is established through the captured open/read/copy path, not merely its filename string.

**MP100-022 advances to partial historical support:** the original installer-record settings path is replaced by early INI selectors, while the old bullet's “Language and RemoteOnly moved to INI” must not be presented as final Modern's configuration contract. Actual startup without the file, every file-access path, original file/read failures, later gate writers and1.0.0 introduction remain unverified. `RemoteOnly` is the observed key name; it is not independently equated to multiplayer or a particular external-media arrangement. No installer file, INI, game, API, instruction probe or Ghidra database was executed or changed.
