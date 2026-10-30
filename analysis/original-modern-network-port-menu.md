# Original versus official Modern: network suffix menu

## Scope and artifacts

Static comparison of the supplied original executable and the official archive Modern executable. This follows the added Modern suffix value, its menu display/toggle path, and the closest corresponding original menu initializer/callback. It does not establish a complete networking compatibility result or observe a live connection.

- Original `nfs3_org.exe`: SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`.
- Official archive `nfs3.exe`: SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`.

## Modern: a displayed suffix choice with two values

The official Modern PE has a getter at `0043fd10`: it zero-extends the WORD at `006fd1dc`; when that value is zero it returns `0x264b` (decimal 9803). `0043fd20` returns the other member of the fixed pair `0x264b` and `0x0406` (decimal 1030). `0043fd38` calls that helper and stores a DWORD at `006fd1dc` (therefore writing bytes `006fd1dc..006fd1df`, despite the getter reading only a WORD). The menu label helper `0043fd44` formats localized resource `0x78b` plus the getter result using `%s: %d` into `005f403a`.

The Modern initializer at `0043fe50` loads title ID `0x10`, item IDs `0x15`/`0x17`, and Cancel (`0xc6`), obtains the formatted suffix label through `0043fd44`, and calls the generic menu builder `004446d0` with four selectable rows and callback `0043f760` (`0043feb1–0043fed3`). Thus the menu includes the current suffix as a displayed, selectable menu item. This describes menu construction, not a captured UI frame.

The callback `0043f760` calls `004446c0` to obtain its mode/state. In its mode-2 branch (`0043f7a5–0043f7af`), it calls the setter `0043fd38` and then regenerates the formatted label with `0043fd44`. The writer chain is therefore bounded: this menu callback can toggle the configured value between the two hard-coded choices and refresh the label. It does not accept or parse arbitrary digits as input. The getter and setter are not a general-purpose port editor.

## Original counterpart

The original executable has a different body at `0043fe50`. Its initializer uses title ID `0x10`, then three selectable rows from item IDs `0x15`, `0x17` and Cancel, and passes callback `0043f760` to `004446d0` with row count three (`0043fe78–0043fed1`). It does not format or insert a suffix label. The original callback body at `0043f760` is also different: it follows the existing service-selection/menu flow and has no call to the Modern suffix getter/setter. The bounded direct-instruction scan reported no literal reference to `006fd1dc` in the original; aliases or block accesses were not excluded.

These are comparisons of the menu initializer and callback bodies in both binaries, not an assumption that equal addresses retain equal meanings. In Modern, those locations contain the added suffix path; the original page has fewer rows and no suffix display/toggle in the inspected route. This does not exclude a separate original networking option elsewhere.

## Retry behavior at the caller boundary

Modern menu choices returning 0/1 from `004446c0` call `0043fd70`. Its zero-input branch attempts the configured value once. Its nonzero-input branch first tries the configured value, then, on failure, tries the alternate value from `0043fd20` (`0043fd86..0043fd99`). This retries service initialization, without writing that alternate back to the configured global. Assigning host/join meaning and proving occupied-port success still require the downstream paths; the branch itself is static evidence. Both failed choices reach the menu notice ID `0x78d` at `0043f7b1`, rather than reporting a failure merely when opening this menu. See [endpoint and reinitialization comparison](original-modern-network-endpoints.md).

## Evidence and limits

- Run `python3 analysis/scripts/audit_network_port_difference.py` for the [retained instruction manifest](evidence/audits/original-modern-network-port.json), including both menu/callback spans and the Modern retry helper.
- Function bytes were rechecked in the official archive and supplied original with `objdump -d -Mintel`; relevant ranges: Modern `0043fd10–0043fd44`, `0043fe50–0043fedb`, `0043f760–0043f7c8`; original `0043fe50–0043fedf`, `0043f760–0043f7ca`.
- Existing Modern-side helper analysis is in [detailed analysis notes](detailed-analysis-notes.md#network-service-suffix-selection-and-provider-retry) and the original/Modern binary fingerprints are recorded in [the difference overview](original-modern-differences.md).
- The name “suffix” is intentional: helper `004a2f50` parses a colon suffix and adapter/caller semantics are treated in a separate network review. This report does not claim the value is a universal socket port setting, that every provider honors it, or that the two builds can interoperate.
- No game, UI, network session, or probe was run; no executable or Ghidra project was modified.
