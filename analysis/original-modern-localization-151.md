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

The entry advances vendor-only→**partial**, with the exact observed change and mismatch in scope explicit. Selected code/menu bindings are resolved in the follow-ups below. Remaining: the specific German correction, other lookup consumers, any relevant alternate-distribution evidence and actual selected-font/translation behaviour. No new runtime test, Ghidra mutation or executable change was performed.


## Track-length consumer follows the moved km entry

The extended audit also extracts and hashes `nfs3.exe` from each same archive. Complete historical track-length helper **`00456590..0045663a`** is170 bytes. Its **only differing byte is`004565f3`**, inside MOV EAX at`004565f2`: lookup index **1932 (`078ch`)→1936 (`0790h`)**. The captured branch selects that index for raw profile values3/4 at`006fbc68`, then calls language lookup`004d1850` at`00456605`. Other values retain index6 in this local helper.

The complete lookup envelope `004d1850..004d187e` is captured for both versions. Its direct maximum index changes **1935→1940**, matching the five-entry growth. For a valid selected full package table, lookup multiplies the index by4, reads its offset and returns base+offset. The first table offset is larger than4*1932 in1.5.0 and4*1936 in1.5.1, so these selected indices pass the local loaded-table extent decision; fallback and invalid-pointer cases remain separate.

Across all six package languages, old index1932 and new index1936 contain the identical bytes **`km`**. Thus this particular code/asset path preserves the unit token while allowing1932 to be reused. This is stronger than inferring meaning from changed table positions, but remains conditional on the matching table being loaded and the inspected branch being reached. It is not proof that arbitrary mixed-version assets work or that every UI consumer was updated.

The [original/final track-length comparison](original-modern-track-length-text.md) covers a wider formatting rewrite and final index`078ah`; that final index must not be substituted for the historical indices here. Historical string numbering is version-bound. The later menu/Frame Size follow-ups bind the new labels. Remaining: all other lookup consumers, fallback compatibility and actual rendered language selection. No formatter or game instruction was executed.


## Historical menu assets bind two new labels

The audit now reads `fedata/menus/camera.mnu` and `graphics.mnu` from both pinned archives, retaining complete member hashes and compact line diffs. The following are the **only line changes in these two selected files**; this is not a comparison of every menu asset.

**camera.mnu:**1.5.1 inserts15 lines and retains every original line. They add:

- A `[button]` with `buttontype=arrowtab`, ypos6, priority11, **`text=lang1938`**, `listname=rearcamera`.
- A `[cascade]` with ypos6, priority4, notitle0, text`lang1164`, maxvisitem5 and the same list name.

The1.5.0 file has no `rearcamera` assignment;1.5.1 has these two. English entry1938 is `Rear View From`, so the new packaged label has an explicit authored control association. This dates the selected menu addition to this historical pair; it does not prove the controls instantiate successfully, expose five valid choices or select a working camera. The [existing final menu/EXE binding](original-modern-viewport-pose.md#rear-camera-menu-binding-identifies-the-fixed-path-selector) supplies separate consumer context.

**graphics.mnu:** the entire raw-file difference is the single replacement **`text=lang1537`→`text=lang1937`** on the button whose listname is **`mirrorlevel`**, ypos6, priority9. English entry1537 remains `Rear View Mirror` in both versions; new1937 is `Rear View Detail`. The selected control therefore changes its authored label while retaining these list/placement fields. This is not evidence that the mirror-detail control itself was first introduced in1.5.1; the existing control was relabelled.

These bindings explain two of the newly added text references without conflating them with a translation-quality fix. The new entry1932 (`Full` and localized equivalents) was pending at this checkpoint; its descriptor consumer is resolved below. Generic `langNNNN` parser resolution, runtime language selection, instantiated control state and rendered outcomes remain outside this asset comparison. No menu or game was run.


## Frame Size first-choice label switches to the new Full entry

The audit now verifies historical descriptor **`005567a8`** as five DWORDs: key`00538008` (`widescreen`), label-list pointer`005562d2`, two zero optional fields and selection pointer`006fbc4c`. These descriptor values are identical in1.5.0/1.5.1. Their WORD lists are **`184,1933,0`→`1932,1933,0`**. The consumer is a packed WORD-label table, explaining why a DWORD/immediate-only search did not identify it.

The [existing Frame Size investigation](original-modern-frame-setting.md) establishes the key/UI association. This historical pair retains two choices and the same selector pointer; it must not be conflated with final Modern's separately documented four-choice layout. The inspected difference is its **first choice's language index**, not a new selection-storage address or proof of changed framing arithmetic.

| Language | First choice via old entry184 | First choice via new entry1932 |
|---|---|---|
| English | `Full` | `Full` |
| German | `Voll` | `Voll` |
| French | `Infinie` | `Compléte` |
| Spanish | `Máxima` | `Máximo` |
| Italian | `Piena` | `Piena` |
| Swedish | `Max` | `Max` |

All six retain `2:1` at entry1933. The new descriptor target1932 is therefore a real choice-label consumer, while the historical track-length consumer moves away from1932 to preserve `km` at1936. Code and assets change together; listing the changed text entry alone would miss this distinction.

This supplies concrete French/Spanish **choice-label changes** relevant to the advertised translation corrections, without an editorial judgement that the new wording is better. German uses a new index but the displayed bytes remain `Voll`; its claimed wording correction is still not independently identified in these shared-entry/selected-consumer comparisons. Other consumers of generic184, menu parsing, selected files, font rendering and runtime behaviour remain pending. No game or lookup helper was executed.
