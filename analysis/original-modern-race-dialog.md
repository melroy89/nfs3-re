# Race-selection dialog: convert stored mode to dialog ordinal

## Evidence and version boundary

**Verified static remap, choice correspondence and historical boundary; live dialog behavior untested.** The [race-dialog audit](evidence/audits/race-dialog-preselection.json), reproduced with `python3 analysis/scripts/audit_race_dialog_preselection.py`, pins supplied original, author-hosted1.1.0/1.2.0 and official final EXEs. All four retain the `racetype` descriptor at`00556528`, binding label list`00556214` to stored mode`006fd3b8`. The unchanged list IDs213/214/215/220 decode through the official final English resource as Single Race/Tournament/Knockout/Hot Pursuit. This is not authentication of the original/early language files.

| Inspected version | Instruction at`00452cf1` | Result on nonzero ESI branch |
|---|---|---|
|Supplied original |MOV EAX,[006fd3b8] |Pass stored DWORD directly |
|Modern1.1.0 |Same MOV |Same direct value |
|Modern1.2.0 |CALL`00448558` |Remap low-byte1↔3 |
|Final1.6.1 |CALL`004728e0` |Identical19-byte remap helper at relocated address |

The complete354-byte builder`00452bd0..00452d32` differs between original/final only at four bytes`00452cf1..00452cf5`, within the replaced five-byte instruction. No same-address correspondence is asserted for original`004728e0`, which is unrelated timestamp-reading code, or early`00448558` before the new helper is introduced there.

## Why modes1 and3 need conversion

For local construction state **C=0** (`006fd50c==0` on this builder's entry path), the retained label-writing sequence constructs dialog rows at`00559548` in a different order from the stored race setting:

| Stored mode | Named race choice | Original candidate row/name | Modern candidate row/name |
|---:|---|---|---|
|0 |Single Race |0 / Single Race |0 / Single Race |
|1 |Tournament |1 / Hot Pursuit |3 / Tournament |
|2 |Knockout |2 / Knockout |2 / Knockout |
|3 |Hot Pursuit |3 / Tournament |1 / Hot Pursuit |

The constructed rows are Single Race, Hot Pursuit, Knockout, Tournament, Cancel (IDs213,220,215,214,198). The original's identity mapping therefore points modes1/3 at the opposite named row under this explicit construction premise. This is a local static consequence, not an observed dialog screenshot. The alternate C=1 restricted construction, session/caller admission and actual resource pointers require separate qualification.

At`00452ced`, ESI0 takes the retained XOR EAX,EAX branch, bypassing both the original mode read and Modern remap. On nonzero ESI, the chosen DWORD is pushed at`00452cfa` and passed with the constructed arrays to dialog helper`004446d0` at`00452d24`. No additional array reordering occurs in the replacement itself. The captured `racetype` callback`0045dab0..0045dac9` remains a separate storage-update route; no end-to-end input test was performed.

## Machine contract and remaining work

The remap loads the whole DWORD but compares/changes **only AL**. It maps00000001h→00000003h and00000003h→00000001h; other ordinary small values remain unchanged. It also maps00000101h→00000103h and00000103h→00000101h, retaining the upper24 bits. It does not clamp arbitrary state or return only a zero-extended byte. A C implementation using `mode==1 ? 3 : ...` would differ for those wider inputs. EAX and arithmetic flags are exposed; the helper does not save/modify other general registers or use x87. Preserve the caller branch and full return DWORD rather than assuming an ordinary Boolean interface.

**MP120-002 advances to partial support:** the named mix-up has a concrete local explanation and a direct1.1.0→1.2.0 correction boundary, retained in final. Live initial focus, dialog-helper interpretation across restricted states, input callback effects, every caller and stored-mode lifetime remain unverified. This is not a general proof that all race-type selection paths are correct. No game, dialog input, language lookup, instruction probe, Ghidra write or executable modification was performed.
