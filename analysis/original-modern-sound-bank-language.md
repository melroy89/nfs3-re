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

A retained Modern initialization witness `004a6ec4..004a6f2e` reads configured selector `007a3a50`, works on the path buffer `007a2b34`, calls `004f9448`, `004f93b8` and `004f916c`, then writes ECX to `007a2764` at `004a6f26`. The branch after `004f916c` either reaches the store without another local ECX assignment or takes a path that explicitly zeros ECX before the store. The cached field consequently has an initialization/fallback route. The initial bounded comparison left helper contracts open; the [producer follow-up below](#cached-selector-producer-checks-a-directory-and-requests-english-fallback) now resolves their selected register/path behavior. Individual-file availability and successful playback remain separate. Its original same-address bytes are retained for inspection, not asserted to be a corresponding original initializer.

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

**Unresolved:** complete producer lifecycle, other writes or aliases, path-buffer validity/capacity on arbitrary inputs, installed language/audio assets and actual playback. The selected helper contracts are resolved in the follow-up below. These affect runtime validation and initialization/data reconstruction. Follow up by reusing the language/configuration research to qualify those helpers and asset provenance; do not treat these three functions as proof of all language/audio behavior. No target instructions, audio tests or Ghidra changes were run in this pass.

## Sequence and police-radio loaders use the same shared-path policy

Two further complete same-address comparisons extend the path-switch finding above. Reproduce with [the voice-bank path audit](scripts/audit_voice_bank_paths.py); [its manifest](evidence/audits/voice-bank-paths.json) verifies pinned binaries, complete spans, original jump tables and their Modern NOP replacements.

| Saved Modern entry / label | Complete envelope, exclusive end | Replaced region | Identical suffix begins |
|---|---|---|---|
| `004c94e0` BuildIndexedSequenceBankPathAndTryLoad | `004c94e0..004c9588` (168 bytes) | `004c94f4..004c9526` | `004c9526` |
| `004c9890` LoadPoliceRadioVoiceBank | `004c9890..004c998f` (255 bytes) | `004c98a6..004c98d8` | `004c98d8` |

In both original functions, the replaced region loads active selector `006fbb4c`, checks unsigned `>5` and dispatches through six table entries. Their exact selector-to-source mapping is the same as the race sound-bank mapping above: 0/5→`007a2b34`, 1→`007a2bb4`, 2→`007a2c34`, 3→`007a2cb4`, 4→`007a2d34`. Original tables are at `004c94c0` and `004c9874`. An out-of-range selector skips the initial local path copy, reaching `004c9543` or `004c98f5` respectively; the later code is not thereby skipped.

Modern replaces each region with `MOV ESI,007a2b34; JMP copy_loop`, followed by 43 NOPs. The complete string-copy loops and subsequent indexed filename construction/loading instructions are unchanged. Modern's old jump-table locations are also entirely NOP-filled. Both Modern functions therefore use the shared path buffer independently of the active selector at these callsites; they do not implement another cached-selector lookup here.

The sequence loader preserves its incoming index in ECX, selects a pointer from `00560b34 + 4*index`, formats through `004df690`, and calls `004c9240`. The radio loader preserves its incoming index in EDX and appends a pointer from `00560b50 + 4*index`, retaining its later mode-dependent suffix and loading branches. No new local bounds check is added to those indexed lookups. Identical code does not establish that their tables, assets or initialization inputs are identical at runtime.

Saved Modern body unions omit each 43-byte gap: their 125/212 body-byte counts must not be mistaken for the 168/255-byte complete envelopes. The audit includes those removed switch instructions, not just the surviving bodies.

**Bounded work status: done; confidence: verified static paths, tables and complete bodies.** The shared-buffer producer and runtime/audio/asset limitations above still apply. This establishes consolidation of additional path consumers, not that all audio localization is fully reconstructed or tested.

## Cached-selector producer checks a directory and requests English fallback

The expanded [sound-bank audit](evidence/audits/sound-bank-language-difference.json) now retains complete official-final path initializer004a6ec4..004a6f2e and its helper bodies. This closes the earlier helper-preservation question; it does not establish every writer, runtime initialization order or historical120 introduction.

The initializer copies22 consecutive zero-terminated literals into128-byte slots starting007a27b4. The manifest records all22 names; each initial literal including terminator fits a slot. Slot7 is the speech base `.\gamedata\audio\speech\` at007a2b34. The constructor then takes configured selector007a3a50 in ECX, finds that base's terminator, appends normalized language-name buffer007a2634 and a trailing backslash, and tests the resulting path.

|Helper |Verified selected contract |
|---|---|
|004f9448..004f9451 |Advances EDI to terminating zero; does not modify ECX |
|004f93b8..004f93c5 |Copies through zero; leaves ESI/EDI at their terminators; preserves EAX and does not modify ECX |
|004f915e..004f916a |Calls imported GetFileAttributesA; explicitly saves/restores ECX and EDX |
|004f916c..004f9184 |Returns1 if attributes are notffffffffh and directory bit10h is set; otherwise0 |

The ECX preservation is material: a true directory predicate leaves the configured selector intact for publication to007a2764. On false, the initializer rewinds EDI to the saved append position, copies literal `english`, appends backslash and explicitly clears ECX before publication. The final shared buffer and cached selector therefore have a concrete selected-language-or-English policy.

False includes API failure or a path reported as a nondirectory, not just confirmed absence. The English fallback is **not checked again**, and individual sound-bank files are not validated by this directory predicate. A present language directory with missing banks does not trigger this local fallback; an absent English directory can still leave an unusable requested path. These are limitations of the observed code, not claims of reproduced crashes.

The unbounded string loops require valid terminated source/destination storage and ordinary clear DF. Validated language names fit comfortably in the128-byte speech slot together with its initial prefix, but the local code does not enforce that bound against arbitrary corrupted inputs. Current directories, inherited path edits, aliases, later writers and concurrent loads require separate lifetime evidence.

## Swedish filename code changes in two verified consumers

Both seven-pointer filename-code tables00409ff0 and00412950 change **`E,G,F,S,I,E,E` → `E,G,F,S,I,W,E`** between supplied original and official final. The manifest retains every pointer and decoded byte string. Their corresponding functions copy these tables into locals, then the previously captured selectors0040a1a6/00413794 index them. The language mapping identifies Swedish as ordinal5, so the changed sixth entry is specifically E→W; it is not inferred from filename spelling alone.

On a successful directory test with validated Swedish selection, the final producer preserves ordinal5 and the shared speech path's Swedish suffix, allowing those inspected consumers to select W. On the fallback route it publishes ordinal0 and requests English/E. This does not authenticate installed Swedish banks, prove case-sensitive filesystem behavior or establish all speech filename consumers.

**MP120-012 advances vendor-only→partial:** selected final directory fallback and original/final Swedish filename-code changes support concrete portions of the claim. The [historical follow-up below](#historical110-to120-dates-the-selected-fallback-and-swedish-code) now dates these selected changes110→120; every failure path and the promised absence of crashes/playback success remain unverified. No game, audio/API operation, instruction probe or Ghidra modification occurred; executable/database bytes are unchanged.

Decoding all seven DWORD pointers in both tables across the hosted original and all twelve retained Modern executables confirms two groups. The original, 1.0.0 and 1.1.0 decode to `E,G,F,S,I,E,E`. Every retained release from 1.2.0 through 1.6.1 decodes to `E,G,F,S,I,W,E`. To reproduce, extract the executable from each archive, read 28 bytes at PE RVAs `0x9ff0` and `0x12950` as little-endian pointers and resolve their strings via the image base. The 1.1.0, 1.2.0, 1.4.0 and 1.6.1 patch archives have no direct members under `GameData/Audio/Speech/` in their member listings. This leaves installed speech-bank contents outside the archive check.

## Historical110 to120 dates the selected fallback and Swedish code

The [historical speech audit](evidence/audits/speech-language-history.json), reproduced with `python3 analysis/scripts/audit_speech_language_history.py`, pins author-hosted110/120 archives and EXEs, both complete selected path initializers,120 helpers,24-slot literal banks and two filename tables. This directly dates the previously described selected final mechanisms without assuming their final addresses/contracts were already in use.

|Selected behavior |110 |120 |
|---|---|---|
|Path initializer |004a6f0c..004a6f2d copies24 literals and returns |004a6f04..004a6f6e copies24 literals, appends language and tests speech directory |
|Speech slot7 initial value |`.\GameData\Audio\Speech\English\`; separate following language paths |`.\GameData\Audio\Speech\`; selected suffix constructed afterward |
|Directory-false route in this initializer |Absent from captured body |Replaces suffix with `english` and publishes cached selector0 |
|Two inspected consumer selector reads |006fbb4c |007a2774 |
|Ordinal5 in tables00409ff0/00412950 |E |W |

120's complete directory predicate004a38f0..004a3911 calls GetFileAttributesA and explicitly preserves ECX/EDX. It accepts a nonfailure attributes result with directory bit10h, so cached selector publication has the same local true/false policy later verified in final. No second check of English or individual bank files occurs in this initializer.110's short initializer lacks that predicate, but this bounded comparison does not exclude every possible fallback elsewhere in110.

The24-slot historical layout must remain distinct from final's22-slot bank. Likewise **120 selector007a2774 differs from final007a2764**. The historical copy helper004f939c returns EAX0, advances ESI past source zero and leaves EDI at destination zero; final's later helper preserves EAX and leaves ESI at source zero. Both leave ECX unchanged. These are relevant register/output contracts for C reconstruction even though the higher-level suffix policy is similar. Full incoming register/DF/pointer-validity assumptions and every caller remain separate.

**MP120-012 retains partial status with its selected historical boundary now verified.** Speech path/fallback and two Swedish-code changes occur110→120 in the inspected pair. Successful Swedish/English asset loading, complete consumer coverage and avoidance of every claimed crash remain untested. No game, audio, filesystem API or target instruction executes, and binaries/Ghidra are unchanged.

### The Italian speech slot becomes the menu path in 1.2.0

The original and early Modern use `007a2d34` for Italian speech. A scan of decoded direct operands in Modern 1.0.0 and 1.1.0 finds three references to that address, at `00413c10`, `004c9521` and `004c98d3`. These are the Italian cases of the race sound-bank, indexed sequence and police-radio path switches. In 1.2.0 all three paths load the shared speech buffer `007a2b34` instead, at `00413be3`, `004c94f4` and `004c98a6`, then jump to their existing copy loops.

The same release repurposes `007a2d34` for the menu directory. Its only decoded direct reference from 1.2.0 through 1.6.1 is the [menu graph loader's operand at `004495ff`](original-modern-menu-loader.md#release-boundary-and-first-initialized-prefix). Reproduce the census by filtering `objdump -d -Mintel` for exact operands naming `0x7a2d34` in each extracted EXE, then disassemble the three replacement sites. This covers direct references found in the disassembly. Indexed initialization writes and possible aliases are outside the census. A reconstruction should associate the slot's meaning with its release.

### Version 1.4.0 moves the cached speech selector

The five filename-table consumers at `0040a1a6`, `00413794`, `00414294`, `00414320` and `00414684` all read the active language in 1.0.0–1.1.0, the cached selector at `007a2774` in 1.2.0–1.3.1, and the cached selector at `007a2764` in 1.4.0–1.6.1. The initializer's ECX store moves with the readers. It is at `004a6f67` in 1.2.0–1.3.1, `004a6f28` in 1.4.0, `004a6f60` in 1.5.0–1.6.0 and `004a6f26` in 1.6.1.

The addresses cannot be named consistently across releases. In 1.2.0 and 1.3.0, the intro mode-selection path multiplies by the DWORD at `007a2764` at `00472e59`; it is not the cached speech selector in those releases. From 1.4.0 onward, `007a2774` is instead written by the [screenshot key held-state path](original-modern-screenshot-feedback.md). Reproduce by checking the five load sites and filtering `objdump -d -Mintel` for decoded direct operands naming either address in each archived EXE. The scan covers these direct roles and does not establish indirect references or live state.

### Local installation has English banks and no Swedish speech directory

The inspected Wine installation has uppercase `ENGLISH`, `FRENCH`, `GERMAN`, `ITALIAN` and `SPANISH` directories directly under `GAMEDATA/AUDIO/SPEECH`. A case-insensitive name inventory found no Swedish directory there. The English directory contains 44 files with a `.bnk` extension, including `LAPENG.BNK`, `CNTENG.BNK` and `TUTORENG.BNK`.

To reproduce from the installed game root, list the immediate directories with `find GAMEDATA/AUDIO/SPEECH -mindepth 1 -maxdepth 1 -type d` and count the English files with `find GAMEDATA/AUDIO/SPEECH/ENGLISH -maxdepth 1 -type f -iname '*.bnk' | wc -l`. This is one local installation. If the game uses that root and its Swedish directory query returns false, the checked Modern initializer selects English and the five cached-selector consumers read zero. The inventory does not establish asset origin, successful bank opens or actual playback.
