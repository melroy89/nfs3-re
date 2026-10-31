# Original versus Modern: track-length text formatting

## Evidence and boundary

The [static audit](scripts/audit_track_length_text_difference.py) pins both executables and retains aligned tails from **`004565d6`** through original exclusive`00456664`, Modern exclusive`0045663a`, including their return sequences. The [manifest](evidence/audits/track-length-text-difference.json) records disassembly, bytes, tables, strings and all changed addresses. These are corresponding formatting tails, not newly established complete functions; enclosing entry/registration remains unresolved.

Within outside-function interval`00456318..00456800` (1256 bytes), all152 changed positions lie in`004565d6..00456670`. Modern’s shorter tail is followed by NOPs through`00456670`; the preceding coordinate-selection code and remaining interval bytes match. No game, renderer, language lookup, instruction probe or Ghidra mutation was performed.

## Selector and formatting changes

Both tails index string tables with DWORD`006fd4ac`, whose selected-circuit role is independently traced in the [music-selection research](original-modern-music-selection.md). Neither tail locally bounds the index to the nine retained entries.

| Original DWORD`006fbb4c` | Original formatting |
|---|---|
| 0 | Table`00559644`, language ID6 through`004d1850`, format`%s %s` at`00539a78` |
| 1,2,5 | Table`00559668`, literal format`%s km` at`00539a80` |
| Other | Table`0055968c`, literal format`%s km` |

Modern instead reads DWORD **`006fbc68`**. Values3/4 select table`00559668` and language ID`078ah`; all others select table`00559644` and language ID6. Both paths join one formatting call through`004df690`, using **`%s %s` at`00538d7c`**. Modern therefore removes the hard-coded`km` unit from this tail and obtains the unit token through language lookup on both paths. Exact displayed translations and selector meanings require separate evidence; the change of selector address is not a proven one-to-one enum remapping.

Both then call text helper`00452190` with the same two stack constants0 and`00488cfd`, ECX18 and local string pointer`EBP-50h`; the placement inputs come from the matching earlier code. Matching call arguments do not prove identical renderer behaviour, since language/text helpers can differ.

## Retained and removed initialized data

The first two nine-pointer tables are byte-identical across the pinned EXEs, and their pointed strings remain:

| Table | Nine strings |
|---|---|
| `00559644` | 3.6, 5.4, 4.9, 5.5, 5.2, 6.3, 5.3, 6.4, 4.6 |
| `00559668` | 5.8, 8.6, 7.8, 8.8, 8.3, 10.1, 8.5, 10.2, 7.4 |

The original third table at`0055968c` is zeroed in Modern; all original pointed strings are retained in the manifest. The old format addresses are empty in Modern, while old`00538d7c` contains`credits` rather than the Modern format. Same-address string interpretation must therefore remain version-bound. Zeroing the third table does not prove absence of other original readers or complete removal of every associated data path.

**Verified static:** changed selector/global, branch mapping, language IDs, format consolidation, retained tables, zeroed third table and local drawing arguments. **Unresolved:** complete widget/function contract, selector producers, localized unit meanings, index bounds, final text/render output and historical release attribution. No precision, replay or multiplayer conclusion follows from this UI formatting rewrite.
