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

The constructed rows are Single Race, Hot Pursuit, Knockout, Tournament, Cancel (IDs213,220,215,214,198). The original's identity mapping therefore points modes1/3 at the opposite named row under this explicit construction premise. This is a local static consequence, not an observed dialog screenshot. The caller/storage follow-up below qualifies the C=1 construction and establishes C=0 at both checked direct calls; other admission and actual resource pointers remain separate.

At`00452ced`, ESI0 takes the retained XOR EAX,EAX branch, bypassing both the original mode read and Modern remap. On nonzero ESI, the chosen DWORD is pushed at`00452cfa` and passed with the constructed arrays to dialog helper`004446d0` at`00452d24`. No additional array reordering occurs in the replacement itself. The captured `racetype` callback`0045dab0..0045dac9` remains a separate storage-update route; no end-to-end input test was performed.

## Machine contract and remaining work

The remap loads the whole DWORD but compares/changes **only AL**. It maps00000001h→00000003h and00000003h→00000001h; other ordinary small values remain unchanged. It also maps00000101h→00000103h and00000103h→00000101h, retaining the upper24 bits. It does not clamp arbitrary state or return only a zero-extended byte. A C implementation using `mode==1 ? 3 : ...` would differ for those wider inputs. EAX and arithmetic flags are exposed; the helper does not save/modify other general registers or use x87. Preserve the caller branch and full return DWORD rather than assuming an ordinary Boolean interface.

**MP120-002 advances to partial support:** the named mix-up has a concrete local explanation and a direct1.1.0→1.2.0 correction boundary, retained in final. Live initial focus, dialog-helper interpretation across restricted states, input callback effects, every caller and stored-mode lifetime remain unverified. This is not a general proof that all race-type selection paths are correct. No game, dialog input, language lookup, instruction probe, Ghidra write or executable modification was performed.

## Checked direct callers exclude the compacted-array premise

The expanded audit now retains both decoded direct caller prefixes, the complete257-byte selection callback`00452ac0..00452bc1`, and48-byte dialog selection-store/clamp span`00444735..00444765`. These four spans are byte-identical between supplied original and final Modern. The four historical baseline captures retain the same relevant setup witnesses; no new target execution was performed.

| Final direct call site | Checked setup before call | Builder implication under ordinary unchanged state |
|---|---|---|
|`00452d6f` |EAX=1; ECX zeroed, stored to`006fd50c` at`00452d57` |ESI1, C0 |
|`00452f4c` |EAX=1; EDX zeroed, stored to`006fd50c` at`00452f34` |ESI1, C0 |

There are no intervening calls between either flag store and the builder call. Thus the unrestricted ordering used above is supported by two actual static caller paths, not only a hypothetical entry condition. The executable code-section relative-E8 census has these two candidates, both decoded in retained witnesses; whole-file literal-pointer search finds no`00452bd0` pointer. Computed/indirect callers, alias/concurrent writes and all reachability are not excluded by this bounded search.

When C=1, the retained builder instead constructs Single Race, Knockout, Tournament, Cancel: its index arithmetic compacts rows by subtracting C. The1↔3 helper itself has no C-dependent adjustment. This is a distinct local case, but the two checked callers initialize C=0. Do **not** promote an arbitrary C1/remapped-mode combination to an observed restricted-mode selection defect without an admitted producer/caller path.

The receiving dialog initializer loads the candidate from stack argument`EBP+14h`, stores it to selected-row global`00558b3c`, and clamps signed negatives to0 or values above`count-1` to`count-1`. This closes the earlier question of whether the pushed DWORD feeds initial selection storage. It establishes an initialized row index, not proof of rendered focus or user acceptance. The builder's final count still depends on incoming ESI and C; a generic clamp does not independently correct every possible ordering mismatch.

The separate callback reads current dialog selection through`004446c0`, dispatches a five-entry jump table and uses C-dependent stores to`006fd3b8`. Its retained body is captured, but complete callback/event admission, callback table interpretation in all states and end-to-end interaction remain later work. **Status: done for these caller/storage checks; confidence: verified static. MP120-002 remains partial.** No live menu, instruction probe, Ghidra change or executable mutation occurred.
