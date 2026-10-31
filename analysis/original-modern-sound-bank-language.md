# Sound-bank loading: cached selector and shared path

## Scope and evidence

The [reproducible static audit](scripts/audit_sound_bank_language_difference.py) verifies the original/official Modern executable hashes and retains full-envelope disassembly and [byte-difference evidence](evidence/audits/sound-bank-language-difference.json). Same-address original counterparts are established by identical instructions outside the explicitly enumerated changes.

| Entry / saved Modern label | Complete envelope, exclusive end | Bytes | Changed bytes |
|---|---|---:|---:|
| `0040a010` InitializeRacerIdentificationSpeechBanks | `0040a010..0040a32c` | 796 | 3 |
| `00413750` LoadRacerIdentificationSpeechBank | `00413750..004138d9` | 393 | 3 |
| `00413bc0` LoadRaceVehicleAmbientAndVoiceSoundBanks | `00413bc0..004147f8` | 3,128 | 61 |

These are analysis labels, not recovered source names. The last complete envelope includes 43 bytes of Modern NOP filling at `00413bea..00413c15`. Saved Modern body ranges omit that gap, so the address index's 3,085 body bytes and 18 changed bytes are not full-envelope counts. Both measurements are valid within their different boundaries.

## Five selector loads move to separate cached storage

At `0040a1a6`, `00413794`, `00414294`, `00414320` and `00414684`, original loads EAX from `006fbb4c`; Modern loads it from `007a2764`. In each case the next indexed lookup and surrounding instructions remain unchanged. The two smaller functions have no other byte changes in their complete envelopes.

The [language-table investigation](original-modern-language-table.md) establishes `006fbb4c` as the active language field in the inspected loader/configuration flow. Modern therefore decouples these sound-bank selections from direct reads of that field. This alone does not prove that every language gets distinct audio assets or that an arbitrary selector is safe: unchanged indexed lookups still require their established domain.

A retained Modern initialization witness `004a6ec4..004a6f2e` reads configured selector `007a3a50`, works on the path buffer `007a2b34`, calls `004f9448`, `004f93b8` and `004f916c`, then writes ECX to `007a2764` at `004a6f26`. The branch after `004f916c` either reaches the store without another local ECX assignment or takes a path that explicitly zeros ECX before the store. The cached field consequently has an initialization/fallback route. The three helpers' full contracts and register preservation are not established by this bounded comparison; interpreting this as a fully verified language-availability test would overstate the evidence. Its original same-address bytes are retained for inspection, not asserted to be a corresponding original initializer.

## Language-indexed path switch becomes one shared buffer

Original `00413be1..00413c15` loads `006fbb4c`, copies seven DWORDs from `0041296c` into the local pointer table, checks the selector with unsigned `>5`, then dispatches through six DWORD targets at `00413ba8`. The resulting source buffers are:

| Original selector | Source address |
|---:|---|
| 0 or 5 | `007a2b34` |
| 1 | `007a2bb4` |
| 2 | `007a2c34` |
| 3 | `007a2cb4` |
| 4 | `007a2d34` |
| Unsigned >5 | Skips the local path copy, continuing at `00413c32` |

Modern retains the seven-DWORD copy, removes the selector read, bounds branch and indirect switch, loads ESI=`007a2b34`, and jumps to the unchanged string-copy loop at `00413c15`. It NOP-fills the removed block. Thus this path always copies from the shared buffer; it does not retain original's out-of-range skip branch. Original's jump table itself is NOP-filled in Modern, outside the selected function envelope.

After `00413c15`, the entire remaining envelope is byte-identical except the three selector loads listed above. The removal changes where paths and selector state come from, rather than establishing a different sound mixing/decoding implementation.

## Reconstruction and follow-up

**Work status: done for the three bounded code comparisons. Evidence confidence: verified static bytes and control flow.** Keep the cached selector separate from the active text-language field, and preserve initialization order and the shared path buffer's lifetime in a Modern reconstruction. An original reconstruction needs the original six-way mapping and out-of-range behavior instead.

**Unresolved:** full cached-selector producer/helper contracts, other writes or aliases, path-buffer capacities, installed language/audio assets and actual playback. These affect runtime validation and initialization/data reconstruction. Follow up by reusing the language/configuration research to qualify those helpers and asset provenance; do not treat these three functions as proof of all language/audio behavior. No target instructions, audio tests or Ghidra changes were run in this pass.
