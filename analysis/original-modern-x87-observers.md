# Original versus Modern: x87 status-observer candidates

## Scope and reproduction

Run [the static inventory](scripts/inventory_x87_status_observers.py). The [manifest](evidence/audits/x87-status-observers.json) pins both executable hashes, retains summary/context and identifies the hash-pinned [complete site index](evidence/audits/x87-status-observer-sites.jsonl). The JSONL columns are baseline, reader address, mnemonic, operands, preceding non-WAIT address/mnemonic and lexical category.

The scanner uses objdump executable-section linear decoding. It searches status-word readers and floating-environment save instructions, **not control-word-only reads**. Candidate counts are not reachable-function counts: embedded data, alternate boundaries and indirect entry points require separate validation. A lexically preceding comparison is not automatically a dominating comparison on every control-flow path. No target code, new probe or Ghidra operation was run.

## Counts and address changes

| Candidate class | Supplied original | Official Modern |
|---|---:|---:|
| FNSTSW | 1653 | 1651 |
| FSTSW | 6 | 6 |
| FNSAVE | 1 | 1 |
| Total | 1660 | 1658 |
| Lexically preceded by FCOM/FCOMP/FCOMPP/FTST (ignoring WAIT) | 1651 | 1649 |
| Other contexts retained for review | 9 | 9 |

There are1652 shared reader addresses, eight original-only addresses and six Modern-only addresses. Every nonshared candidate below is lexically preceded by a fresh FCOM/FCOMP. These are address-set differences, not fourteen independently established features or paired old/new algorithms.

| Baseline | Reader addresses absent from the other candidate set |
|---|---|
| Original | `0041aa7e`, `0041aa92`, `0046524c`, `0046a58c`, `00495273`, `004f1ec4`, `004f2040`, `004f206d` |
| Modern | `0041aa72`, `0041aa83`, `00490180`, `004901a3`, `004dbc70`, `004dbc81` |

The [CPU calibration chapter](original-modern-cpu-tier.md) already explains removed estimator/helper regions around original `004f2040/004f206d`; the [loading-timing chapter](original-modern-loading-timing.md) covers Modern progress estimation around `00490180/004901a3`. Reuse those mechanisms before treating these locators as new investigations. Remaining candidate correspondence and incoming-branch ownership are not established by this inventory.

## Nonadjacent and saved-state contexts

| Modern site(s) | Bounded interpretation |
|---|---|
| `004ff62c` FNSAVE; `004ff63c` FNSTSW | Saved-image atan wrapper; see the exact-entry follow-up below. Full floating-state propagation is distinct from branch dependence on incoming condition bits. |
| `0051a1c2` FSTSW to memory | FTST at `0051a1bd` precedes a local stack reservation, then the reader. The intervening SUB is integer-only. Full caller/path admission remains separate. |
| `0051f3a7` FNSTSW | FCOM at `0051f3a4`, then PUSH EAX, then status read. The intervening PUSH does not read/replace x87 condition bits. |
| `00523385` FSTSW to memory | Immediately follows FPREM, which is a different status-producing operation from FCOM; quotient/reduction-state use needs its own arithmetic contract. |
| `00526fd1`, `0052701d`, `00527069`, `005270b5` | Exact adjacent FNSTSW AX / AND EAX,3800h sequences. The mask selects TOP bits11..13 and excludes tracked C0/C2/C3 mask4500h. |

The four TOP masks are independently asserted from bytes, and `3800h & 4500h = 0`. Their subsequent masked-EAX result therefore does not carry these three condition bits. This is a concrete exclusion for those local reads, not a claim that all status readers are harmless or that complete floating-point state is equivalent.

## Saved-image wrapper is retained, not a new Modern observer

Complete **`004ff624..004ff658`**,52 bytes, is identical in both EXEs and corresponds to the existing `RunArctangentHelperWithRestoredFpuImage` research. Correct entry decoding begins with PUSH EAX, stack reservation and FSTP TBYTE temporary before FNSAVE; a whole-section linear listing can misdecode bytes preceding the correctly found FNSAVE. The saved-entry boundary is independently established in existing analysis.

After invoking `0051f320`, it reads helper status, stores the result into the saved image, masks helper AX with00ffh, ORs it into the saved status WORD at image+4, then FRSTORs the image. The inventory asserts those mask/merge/restore instructions. The saved high status byte, which includes C0/C2/C3, is retained by that merge; it is not replaced by helper-produced C bits. The saved image reflects state **after the wrapper's initial operand pop**, so this does not prove arbitrary entry-state bit preservation through that first FSTP.

This wrapper demonstrates why an environment save cannot simply be discarded from an observer review: state can survive across another computation without being used as an application branch input. Complete atan numerics, incoming stack/exception requirements, all callers and the later consumers of restored state remain separate. No arithmetic or environment instruction was executed by the inventory.

## Consequence for the precision investigation

The [precision comparison](og-modern-x87-precision.md) establishes changed control policy at selected boundaries; this inventory does not turn arithmetic precision into a storage-size claim. The [line-boundary caller audit](line-boundary-x87-callers.md) traces selected paths and now has a complete address-index reference for possible status/environment readers.

Most decoded readers have the compiler's adjacent-compare shape, and several special cases have narrowed contracts above. Nevertheless, global branch dominance, indirect/alternate entry, environment propagation and actual runtime use remain unproved. **No whole-game absence of dependence on the differing C bits, replay/multiplayer equivalence or game-facing replacement qualification is claimed.** The next work should select unresolved reader reachability or a specific outer-caller path, rather than infer safety from these counts.
