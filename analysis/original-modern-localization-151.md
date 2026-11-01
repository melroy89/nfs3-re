# Historical1.5.1 text changes: exact packaged entries

**Confidence: verified asset bytes. Work status: partial for MP151-005.** The [audit](scripts/audit_historical_localization_151.py) verifies the same pinned author-hosted1.5.0/1.5.1 archives used by the [lockwindow comparison](original-modern-lockwindow-history.md), then parses all six `fedata/text/text.*` members in both. The [manifest](evidence/audits/historical-localization-151.json) retains archive/member hashes, entry offsets, exact changed bytes and reversible display text. No assets were installed or executed.

## Complete table partition, not a strings scan

Every inspected1.5.0 file begins with a7,744-byte table of1,936 little-endian offsets; every1.5.1 file begins with7,764 bytes and1,941 offsets. Each offset is in ascending order; each NUL terminator ends exactly at the next entry or file end. The audit therefore accounts for the complete offset table and string payload of all12 files, with no unexplained trailing region. This describes these inspected assets, not a complete parser specification for arbitrary game files.

All indices below are **zero-based positional entries**. Latin1 is used only as a reversible display convention; raw hexadecimal bytes are retained, and game font/codepage interpretation is not established.

## Changes to existing indices

| Language | Entry1283 | Entry1932: old→new |
|---|---|---|
| English | Unchanged | `km`→`Full` |
| German | Unchanged | `km`→`Voll` |
| French | `Champ de vision`→`Champ de vue` | `km`→`Compléte` |
| Spanish | Unchanged | `km`→`Máximo` |
| Italian | Unchanged | `km`→`Piena` |
| Swedish | Unchanged | `km`→`Max` |

**Every other shared index is byte-identical.** In every language the old `km` bytes reappear at new entry1936. This is a positional remapping/addition, not proof that the game replaced a distance-unit label with a detail setting at runtime. Consumers/string IDs and loaded language selection must be traced before making that UI claim. French spelling above reproduces the bytes; it is not an editorial correction.

## Added entries1936 through1940

| Language |1936 |1937 |1938 |1939 |1940 |
|---|---|---|---|---|---|
| English | `km` | `Rear View Detail` | `Rear View From` | `Active Camera` | `In Car Camera` |
| German | `km` | `Rückspiegel-Details` | `Rückansicht Aus` | `Aktive Kamera` | `Innen-Kamera` |
| French | `km` | `Détail de rétroviseur` | `Vue arrière de` | `Caméra active` | `Caméra siège conducteur` |
| Spanish | `km` | `Detalle retrovisor` | `Reflejo retrovisor` | `Cámara activa` | `Cámara interior` |
| Italian | `km` | `Dettagli Retrovisore` | `Retrovisore Da` | `Active Camera` | `Interna Camera` |
| Swedish | `km` | `Backspegel detalj` | `Backspegel från` | `Aktiv kamera` | `Kupékamera` |

These establish the strings present in the package and their introduction in this pair. They do not prove first introduction in every distribution, translation quality, control availability or rendered selection. Rear-camera controls have separate [EXE/asset binding evidence](original-modern-viewport-pose.md#rear-camera-menu-binding-identifies-the-fixed-path-selector).

## What the release-note claim does and does not establish

MP151-005 advertises corrections to new German, Spanish and French strings. The direct pair verifies a French wording change and the full addition/remapping above. It does **not** identify an independent German/Spanish wording correction among other shared entries: those remaining entries are equal. The vendor may refer to the new entries, a semantic index correction, or another reference distribution; intent is unresolved. Do not turn the absence of another changed shared entry into proof that no translation issue existed.

The entry advances vendor-only→**partial**, with the exact observed change and mismatch in scope explicit. Required follow-up: bind the changed/new indices to menu consumers, inspect any relevant intermediate/distribution evidence, and qualify actual selected-font/translation behaviour if needed. No new runtime test, Ghidra mutation or executable change was performed.


## Track-length consumer follows the moved km entry

The extended audit also extracts and hashes `nfs3.exe` from each same archive. Complete historical track-length helper **`00456590..0045663a`** is170 bytes. Its **only differing byte is`004565f3`**, inside MOV EAX at`004565f2`: lookup index **1932 (`078ch`)→1936 (`0790h`)**. The captured branch selects that index for raw profile values3/4 at`006fbc68`, then calls language lookup`004d1850` at`00456605`. Other values retain index6 in this local helper.

The complete lookup envelope `004d1850..004d187e` is captured for both versions. Its direct maximum index changes **1935→1940**, matching the five-entry growth. For a valid selected full package table, lookup multiplies the index by4, reads its offset and returns base+offset. The first table offset is larger than4*1932 in1.5.0 and4*1936 in1.5.1, so these selected indices pass the local loaded-table extent decision; fallback and invalid-pointer cases remain separate.

Across all six package languages, old index1932 and new index1936 contain the identical bytes **`km`**. Thus this particular code/asset path preserves the unit token while allowing1932 to be reused. This is stronger than inferring meaning from changed table positions, but remains conditional on the matching table being loaded and the inspected branch being reached. It is not proof that arbitrary mixed-version assets work or that every UI consumer was updated.

The [original/final track-length comparison](original-modern-track-length-text.md) covers a wider formatting rewrite and final index`078ah`; that final index must not be substituted for the historical indices here. Historical string numbering is version-bound. Remaining: bind the new Full/detail and rear-camera entries, all other lookup consumers, fallback compatibility and actual rendered language selection. No formatter or game instruction was executed.
