# Original versus Modern: cursor positioning validity and sound wrappers

## Scope and counterparts

Static paired comparison, using the [baseline identities](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_cursor_position_difference.py`; the [manifest](evidence/audits/original-modern-cursor-position.json) retains complete positioning bodies, the identical cursor bridge, new Modern wrappers and four direct call witnesses. No cursor, audio, input, target or instruction execution; no Ghidra writes.

| Entry | Record base / count | Original body end | Modern body end |
|---|---|---|---|
| `00444570` | `00661000` / DWORD `00558b30` | `004445ce` | `004445ce` |
| `00445160` | `00660fd0` / unsigned byte `00558c64` | `004451c2` | `004451c1` |

Both entries accept an index in EAX. Negative indexes and indexes>=count skip positioning. Both use eight-byte records containing four16-bit fields. For record signed WORDs `w0,w1,w2,w3`, the retained arithmetic is **X=w1+w2−2, Y=w0+w3−2**. They store X/Y to `0055e5e4/e8` and call `0049bfc0` with EAX=X, EDX=Y. Geometric member names such as left/width are not established merely by those sums.

## Same ordinary coordinates, new return contract

Original loads overlapping DWORDs and selects their signed high16 bits with SAR16. Modern loads the corresponding WORDs directly with MOVSX. The arithmetic selects the same signed field values in ordinary little-endian storage, but original’s wider reads include adjacent bytes; the read for w0 begins two bytes before the record. Do not translate that into an unchecked or unaligned C `int*` dereference or assume equal memory-access footprints.

Modern additionally saves/restores EBX and uses it as a Boolean result: initialize0, set1 after the positioning call, return it in EAX. Invalid indexes therefore return0; valid indexes return1 after making the call. The return does **not** verify platform cursor movement. Original has no corresponding explicit status: an invalid path leaves the incoming index in EAX, and a valid path leaves the called bridge’s result. It must not be annotated as the same Boolean interface.

Complete bridge **`0049bfc0..0049bff7`** is byte-identical. It stores X/Y, conditionally applies coordinate helpers when `00559234` is nonzero, and calls `00435230`. Platform output acceptance and the full downstream coordinate transforms remain outside this comparison.

## New wrappers occupy the old HSV tail

Modern adds **`0043eb88..0043eb9d`** for dialog choices and **`0043eba0..0043ebb5`** for ordinary menu items. Each saves EDX, calls its positioning helper, and tests EAX. If nonzero, it preserves that result on the stack, calls sound helper `004181d0` with EAX=0, restores the result, restores EDX and returns. Invalid indexes bypass the sound request. The wrappers do not locally set a new EDX sound argument; the positioning helpers restore the wrapper’s incoming EDX before the sound call.

These locations fall within the old **`0043ead0..0043ebb8`** HSV-handler envelope. Modern’s HSV counterpart ends earlier at `0043eb85`, as documented in the [colour-control comparison](original-modern-colour-control.md). The new wrappers must not be paired with the unrelated original release-action instructions merely because they reuse those addresses.

Four retained direct-call witnesses show actual navigation retargeting:

| Callsite | Original target | Modern target |
|---|---|---|
| `004455a1` | `00445160` | `0043eba0` |
| `004455cb` | `00444570` | `0043eb88` |
| `004455fd` | `00445160` | `0043eba0` |
| `00445627` | `00444570` | `0043eb88` |

These establish adoption of the validity-gated sound wrappers at those sites, not every outer keyboard/controller path or an audible result. The broader replay-list keyboard-position claim **MP140-014** is not promoted from this generic helper refactor; its specific caller and record producer still require inspection. This chapter records an independently verified change even without a unique release-note attribution.

The [replay-list follow-up](original-modern-replay-list-cursor.md) now traces a separate registered selectlist input handler and its8→68 cursor Y offset correction. The replay claim has partial static support through that path, rather than these generic corner helpers.
