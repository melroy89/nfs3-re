# Original versus Modern: window-key translation

## Evidence and complete boundaries

The [static audit](scripts/audit_window_key_translation_difference.py) retains complete original **`004ccaa0..004ccc67`** (455 bytes) and Modern **`004ccaa0..004ccaf6`** (86 bytes), exclusive ends. The [manifest](evidence/audits/window-key-translation-difference.json) pins baseline hashes, complete bytes/disassembly, both Modern tables and selected original branch witnesses. No keyboard, OS API, target or new instruction probe was executed.

Both admit incoming EAX message values **100h/104h**; other messages return0. EDX supplies the raw key value. Original uses a comparison tree with immediate output constants. Modern scans two zero-key-terminated tables of `(WORD input, WORD output)` at four-byte stride, comparing the zero-extended input WORD against full EDX. It returns the stored output WORD zero-extended into EAX. High EDX bits are therefore not silently discarded by the lookup.

## Primary table and toggle-gated keypad table

All key and output codes in the following tables are hexadecimal.

The first table **`004ccaf8..004ccb54`** has22 nonzero entries plus a zero pair. Matches return immediately, before consulting toggle state:

| Inputs | Corresponding outputs |
|---|---|
| `25,27,26,28` | `4b00,4d00,4800,5000` |
| `2e,21,22,24,23,2d` | `5300,4900,5100,4700,4f00,5200` |
| `70..79` | `3b00..4400` in order |
| `7a,7b` | `8700,8800` |

On a miss, Modern calls **GetKeyState**, independently resolved from its PE import at`00534744`, with argument **90h** (Num Lock). It tests only AL bit0. A set bit returns0; a clear bit admits the second table **`004ccb54..004ccb84`**,11 nonzero entries plus a zero pair:

| Inputs | Corresponding outputs |
|---|---|
| `60..69` | `5200,4f00,5000,5100,4b00,4c00,4d00,4700,4800,4900` |
| `6c` | `5300` |

The exact11th key is **6ch**, not6eh; preserve the observed value rather than silently substituting a more familiar keypad token. A miss in both admitted tables returns0.

## Original contrast and machine contracts

Original has no toggle-state API call in this complete translator body. Its branch tree maps raw65h to output4c00h directly. Modern maps65h only through the toggle-gated second table. Another concrete difference is raw6ch: original’s admitted-message path follows comparisons at`004ccab5`, `004ccac4`, `004ccb13`, `004ccb1e`, `004ccb2e`, then returns0 at`004ccb37`; Modern has an explicit6ch→5300h entry when the second table is admitted. These examples are static branch derivations, not an exhaustive original input-equivalence test.

Modern preserves ESI by PUSH/POP. Its GetKeyState call is followed by second-table comparisons that **reuse EDX without a local save**. Consequently the intended key lookup depends on the provider returning with the relevant EDX value intact; this audit does not establish that provider-specific register behaviour. Do not turn the conditional table mapping into a universal OS/Wine guarantee or quietly repair the machine contract during reconstruction. Original’s EBP frame and Modern’s ESI save also produce different stack/register effects; arithmetic flags and API side effects are not equivalent merely because many returned key codes match.

## Data replacing original branch bytes

Outside-function interval **`004ccaf6..004ccb84`** spans142 bytes with116 differing positions. Modern contains two NOPs followed by92 primary-table bytes and48 secondary-table bytes. Those table bytes overlap original branch-tree instructions and must be reconstructed as data, not interpreted as Modern code or function pointers. The original body continues beyond this interval; the inventory boundary does not define it.

**Verified static:** complete bodies, message admission, exact table entries/terminators, toggle-test placement, selected original contrasts and mixed code/data boundary. **Unresolved:** full message-to-consumer routing, provider EDX behaviour, all input-domain contracts, actual physical key delivery, runtime/Wine behaviour and historical attribution. This change alone establishes neither controller compatibility nor a replay/multiplayer effect.

## Retained message callers connect conversion to queued input

The expanded audit now verifies complete **`004cd020..004cd0dd`**,189-byte key-down callback, is byte-identical across both EXEs. Existing [window registration research](original-modern-window-handling.md) establishes its message route. On its translated-input branch it supplies message in EAX and raw key in EDX, calls`004ccaa0` at`004cd0a9`, saves a nonzero result in ESI, and enqueues that encoded value through **`004cc8e0`** at`004cd0ca`. A zero conversion skips that repeat-enqueue path. A separate mode selected by`007f7488` bypasses this translator and queues zero-word records with scan/index data instead, as recorded in the [key-down contract](detailed-analysis-notes.md#recovered-key-down-callback-boundary).

The callback computes its repeat count in **ECX** before conversion and decrements ECX afterwards without restoring it around`004ccaa0`. Original’s branch-tree translator does not locally modify ECX; Modern’s primary-table matches also avoid a native API call and leave ECX alone locally. Modern’s primary miss reaches GetKeyState without saving ECX, introducing a provider-preservation dependency for the repeat loop in addition to the translator’s EDX key dependency. This is a machine-contract limitation, not an observed Wine/input failure or a guarantee about actual OS register values.

Identical message-loop span **`004cd5b9..004cd5d3`**,26 bytes, supplies saved key/message values to the same translator at`004cd5bf`; it branches on zero result before its subsequent OS message processing. The two direct callsites are independently checked in both binaries. This establishes a static message/queue effect route, while real physical events, all queue consumers, exact repeat count on the API path and provider behaviour remain untested.
