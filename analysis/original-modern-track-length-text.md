# Original versus Modern: track-length text formatting

## Evidence and boundary

The [static audit](scripts/audit_track_length_text_difference.py) pins both executables and retains aligned tails from **`004565d6`** through original exclusive`00456664`, Modern exclusive`0045663a`, including their return sequences. The [manifest](evidence/audits/track-length-text-difference.json) records disassembly, bytes, tables, strings and all changed addresses. The follow-up below now establishes complete helper entry00456590 and a shared direct caller; the registered image/glow route is established in the final follow-up, while live menu invocation remains unresolved.

Within outside-function interval`00456318..00456800` (1256 bytes), all152 changed positions lie in`004565d6..00456670`. Modern’s shorter tail is followed by NOPs through`00456670`; the preceding coordinate-selection code and remaining interval bytes match. No game, renderer, language lookup, instruction probe or Ghidra mutation was performed.

## Selector and formatting changes

Both tails index string tables with DWORD`006fd4ac`, whose selected-circuit role is independently traced in the [music-selection research](original-modern-music-selection.md). Neither tail locally bounds the index to the nine retained entries.

| Original DWORD`006fbb4c` | Original formatting |
|---|---|
| 0 | Table`00559644`, language ID6 through`004d1850`, format`%s %s` at`00539a78` |
| 1,2,5 | Table`00559668`, literal format`%s km` at`00539a80` |
| Other | Table`0055968c`, literal format`%s km` |

Modern instead reads DWORD **`006fbc68`**. Values3/4 select table`00559668` and language ID`078ah`; all others select table`00559644` and language ID6. Both paths join one formatting call through`004df690`, using **`%s %s` at`00538d7c`**. Modern therefore removes the hard-coded`km` unit from this tail and obtains the unit token through language lookup on both paths. The packaged translations are verified below; runtime file selection and selector meanings require separate evidence; the change of selector address is not a proven one-to-one enum remapping.

Both then call text helper`00452190` with the same two stack constants0 and`00488cfd`, ECX18 and local string pointer`EBP-50h`; the placement inputs come from the matching earlier code. Matching call arguments do not prove identical renderer behaviour, since language/text helpers can differ.

## Retained and removed initialized data

The first two nine-pointer tables are byte-identical across the pinned EXEs. Their **pointed strings differ** in the second table: original uses decimal commas, Modern decimal dots. The first table’s strings match:

| Table | Original strings | Modern strings |
|---|---|---|
| `00559644` | `3.6; 5.4; 4.9; 5.5; 5.2; 6.3; 5.3; 6.4; 4.6` | Same |
| `00559668` | `5,8; 8,6; 7,8; 8,8; 8,3; 10,1; 8,5; 10,2; 7,4` | `5.8; 8.6; 7.8; 8.8; 8.3; 10.1; 8.5; 10.2; 7.4` |

The original third table at`0055968c` points to decimal-dot strings matching Modern’s second-table values; the third pointer table itself is zeroed in Modern. All original pointed strings are retained in the manifest. The old format addresses are empty in Modern, while old`00538d7c` contains`credits` rather than the Modern format. Same-address string interpretation must therefore remain version-bound. Zeroing the third table does not prove absence of other original readers or complete removal of every associated data path.

**Verified static:** changed selector/global, branch mapping, language IDs, format consolidation, retained pointer tables, comma-to-dot string changes, zeroed third table and local drawing arguments. **Unresolved:** complete machine contract, live widget invocation, selector producers, runtime language selection, raw selector enum names, index bounds, final text/render output and historical release attribution. No precision, replay or multiplayer conclusion follows from this UI formatting rewrite.

## HUD-profile producer and default branch

The selector is profile-header offset **+18h**, not an isolated new unit global: the existing [HUD defaults comparison](original-modern-hud-layout.md#3-header-default-changes-preserve-offsets-not-guessed-widget-names) maps six headers at`006fbc50 + i*1a4h`. The expanded audit verifies Modern producer **`0048595b..00485984`**,41 bytes: MOV EBX3 followed by six direct DWORD stores to`006fbc68 + i*1a4h`, for i0..5. These bytes establish a concrete default producer without guessing a human-facing enum name.

For that default and this path’s direct read of the first profile cell, Modern chooses table`00559668` plus language ID078ah. This ties the changed display branch to existing profile initialization. It does not prove the default survives saved configuration, which bank should represent every runtime view, or which language file is actually selected at runtime. The [HUD editor dataflow](hud-exclusion-reachability-audit.md) already records independent per-bank selector writes and reachable cycle values; this display comparison must preserve those alternatives rather than treating default3 as a permanent constant. Runtime loading/selection remains unresolved; the selected packaged label meanings are established below.

## Official language assets establish the unit labels

The audit reads all six text-table members directly from the hash-pinned official archive, without executing a loader. For IDs6 and078ah it checks that the offset slot is within the declared DWORD table extent, the payload offset is beyond that table and within the member, and a terminating NUL exists. Member hashes, sizes, offsets and raw selected-string bytes are retained.

| Official member suffix | ID6 | ID078ah |
|---|---|---|
| eng | Miles | km |
| ger | Meilen | km |
| fre | Miles | km |
| spa | Millas | km |
| ita | Miglia | km |
| swe | Miles | km |

Thus, with these packaged assets selected, Modern selector values3/4 display the kilometer table plus`km`; other values display the mile table plus the localized miles label. The [language fallback comparison](original-modern-language-table.md#lookup-gains-guarded-fallback) separately establishes embedded fallback`km` for078ah; lower-ID fallback can instead be empty. These observations do not prove runtime asset selection, every malformed-table outcome or that all HUD selector enum names have been decoded. The old exact-label unknown is resolved for these official members, while installed replacements and original asset provenance remain separate.

## Catalog claim MP140-032: partial static support

The pinned README line316 says track-info length follows units chosen in the first player HUD. The audit now records the exact source bullet and README hash. The final-pair code change supports its mechanism: original formatting selects via`006fbb4c`, while Modern reads first profile cell`006fbc68`; the selector branches and six official labels establish the kilometer/mile display choice. The default producer and existing editor research connect that cell to HUD configuration.

**MP140-032 is therefore Partial**, superseding vendor-only status. This does not establish actual first-player bank selection at every runtime entry, successful formatting/rendering, installed replacement assets or that the mechanism first appeared in v1.4.0. Decimal comma-to-dot payload changes are independently observed and need not be treated as part of the same historical claim.

## Complete helper boundary and direct caller

The expanded audit now captures complete helpers **original`00456590..00456664`** (212 bytes), **Modern`00456590..0045663a`** (170), with exclusive ends. Both entries save EBX/ECX/EDX/ESI/EDI/EBP, establish a frame and reserve80 local bytes; both epilogues restore those registers. Their first70 bytes match through exclusive`004565d6`, where the formatting rewrite begins.

Both files contain identical direct CALL`004566a5 → 00456590`, verified from its displacement. This establishes pairing independently of equal addresses and strengthens the earlier tail-only evidence. The shared prefix chooses coordinate inputs from the selected circuit: index4 uses EBX430/EDX200; indices0/7/8 use410/250; other indices use390/465. These are raw caller arguments to the later text helper, not independently verified physical pixels. No input-dependent path in this prefix bounds the subsequent table index.

The preceding routine at`00456320` returns at`00456583` and must not be merged into this helper merely because the saved-function inventory leaves the whole area uncovered. The static image/glow registration is established below; caller scheduling, invalid indices and drawing/helper state remain unresolved; no Ghidra function object was created.

## Registered image/glow update route and admission gates

Both EXEs have registry row **`00557a9c`** `(type4, token00538360="image", template00556df0)`. Template+2ch at`00556e1c` points to **`00460100`**. Its identical41-byte entry prefix compares item+10h with token **`glow`** at`0053a954`; a match calls`00456670` at`0046011f`. This establishes a static registered-component route, not just a raw direct caller.

The complete393-byte wrapper **`00456670..004567f9`** is identical in both files. Before direct call`004566a5 → 00456590`, it rejects nonzero`00559c60` by returning0 and checks selected circuit`006fd4ac` against cached/current value`00677d8c`; mismatch returns9 without formatting. Matching indices reach the length helper and subsequent drawing/update work. Equality with the cached value is not a nine-entry range check.

The audit retains registry values, token witnesses, updater prefix and full wrapper bytes/hashes. This resolves static component ownership through `image`/`glow`, superseding the earlier general registration unknown. Actual menu-instance loading, runtime scheduling, all generic dispatcher paths, interpretation of return9 and source-table bounds remain unverified. No component callback or renderer was executed.
