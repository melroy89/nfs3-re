# Modern small conversion helpers: contracts and counterpart limits

## Evidence boundary

[The helper audit](scripts/audit_modern_small_conversion_helpers.py) verifies both pinned executable hashes, exact Modern bodies, retained ASCII character converters and the wide-character import binding. [Its manifest](evidence/audits/modern-small-conversion-helpers.json) retains paired original-region hashes and disassembly locations.

| Modern entry / saved label | End, exclusive | Bytes |
|---|---|---:|
| `004f93c8` CopyAsciiStringToLowercase | `004f93da` | 18 |
| `004f9400` CopyAsciiToLowercaseBounded | `004f9417` | 23 |
| `004f9424` CopyAsciiToUppercaseBounded | `004f943b` | 23 |
| `004e3000` ConvertAnsiBytesToWideCharacters | `004e3013` | 19 |
| `004f939c` ConvertFloatBitsToInt32UsingX87Rounding | `004f93a5` | 9 |

These are verified Modern helper contracts in changed code regions. Original same-address bytes are **not established functional counterparts**; this report does not claim original lacked equivalent behavior elsewhere or assign their prior containing functions. Counterpart recovery remains a separate comparative gap. No API, game or instruction probes were executed.

## ASCII copy helpers have pointer and count outputs

All three take source ESI and destination EDI, preserve incoming EAX, use LODSB/STOSB, and do not issue CLD. The ordinary forward-copy contract therefore assumes direction flag clear and suitable readable/writable flat segments. They are byte-copy loops, not overlap-safe memmove replacements.

The lowercase helpers call `004f0ae0`; uppercase calls `004eede0`. Both complete 14-byte character converters are byte-identical in original and Modern. They map ASCII A..Z→a..z or a..z→A..Z respectively; other byte values are unchanged. The copy helpers initially zero EAX, so loaded bytes reach those converters as values 0..255. This is ASCII mapping, not locale-sensitive Unicode case conversion.

Unbounded `004f93c8` copies through and including NUL, then decrements ESI and EDI. Under the forward-copy assumptions, both output pointers therefore address the copied terminator rather than the byte after it. It has no local capacity check and does not return a conventional destination pointer in EAX; EAX is restored.

Bounded `004f9400` and `004f9424` use ECX as a byte budget:

- Initial ECX=0: copy nothing; no terminator is written.
- Nonzero byte copied: decrement ECX and repeat.
- NUL copied: leave ECX at its remaining value, decrement ESI/EDI back to the terminator, return.
- Budget exhausted on nonzero bytes: return with ECX=0 and pointers after the last copied byte; no extra NUL is written.

There is no zero padding. In particular, these are not ordinary `strncpy` contracts, and ECX/pointer outputs are hidden ABI results that a maintained C interface must represent explicitly when callers depend on them. With a terminator encountered, ECX is not decremented for that NUL copy. Destination/source aliasing and all caller domains remain unqualified.

## Wide-character wrapper duplicates one count into two API arguments

`004e3000` preserves ECX/EDX and invokes imported `MultiByteToWideChar` through `00534598` with stack arguments equivalent to:

`MultiByteToWideChar(0, 0, ESI, ECX, EDI, ECX)`

Code page and flags are literal zero. The same incoming ECX is source byte count and destination wide-character capacity. The API result remains in EAX. This is not a general wrapper with independently supplied source length and destination capacity, and the body performs no local error handling, allocation or terminator addition. Passing an explicit positive length does not by itself promise an output NUL; preserving this call construction matters when reconstructing filename conversion. Actual platform conversion, API failure and all caller lengths remain untested.

## Float-bits conversion obeys current x87 rounding

`004f939c` pushes incoming EAX, loads those bits as binary32 with FLD, converts ST0 to signed DWORD with FISTP into the same stack slot, then pops the result into EAX. It does not call `004dfd56`, change the control word or explicitly truncate. ESI/EDI/ECX/EDX are untouched locally; x87 status/exception state can change.

For ordinary representable finite values, the integer conversion follows active x87 rounding. A C cast instead imposes truncation toward zero. Invalid/out-of-range/NaN and pending unmasked-exception behavior require explicit machine semantics; a cast or undefined signed overflow is not an equivalence argument. See the [precision comparison](og-modern-x87-precision.md) and [HUD conversion finding](original-modern-hud-layout.md#pixel-conversion-removes-explicit-truncation-before-fistp) for separate arithmetic-precision versus conversion-policy evidence.

## Readiness and follow-up

**Work status: Modern local contracts done; original functional counterpart mapping pending. Confidence: verified static instructions, not runtime validation.** These helpers can support ABI/data reconstruction once their callers' pointer, count, direction-flag and rounding-state assumptions are qualified. The changed address index can link this evidence without implying that the original containing code has been fully explained.

Required follow-up is original counterpart/removed-region classification, complete caller contracts and effects on specific game features. Runtime string/API/x87 comparisons require a separately scoped phase. Executables, Ghidra state and maintained reconstruction sources remain unchanged.
