# Original versus Modern: startup resource and desktop requirements

## Counterpart evidence

Original **`004b5f10..004b5fee`** corresponds to Modern **`004b5748..004b57c1`** by shared resource-check operations and subsystem callers, not by address. Original setup calls it at `004b6092`; Modern setup calls its counterpart at `004b5c0c`. Reproduce with `python3 analysis/scripts/audit_startup_requirement_difference.py`; the [manifest](evidence/audits/original-modern-startup-requirements.json) retains both complete bodies, caller witnesses, diagnostic helpers, imports and final messages. See [baseline](original-modern-differences.md). No API, dialog, game or instruction execution; no Ghidra edits.

## Memory arithmetic changes before the threshold

Both initialize DWORD+0 of global block `007a3ac0` to32 and pass its address to imported **GlobalMemoryStatus**, then read DWORDs at block+0ch and+14h. The report retains offsets rather than assuming a complete reconstructed structure declaration.

| Policy | Original | Modern |
|---|---|---|
| Arithmetic | Add two byte-valued DWORDs modulo2^32 | Logical-shift each DWORD right20, then add |
| Admission | Unsigned byte sum >=`01000000h` (16 MiB) | Unsigned sum of truncated MiB >=16 |
| Extra operation | Logs the shifted wrapped sum through `0042d500` | No corresponding local logging call |
| Low-resource message | Selects from six-entry tables using incoming EAX index | Fixed English text: “Your RAM resources are too low.” |

Modern’s shifted sum cannot overflow32 bits for these two32-bit inputs. Original’s byte sum can wrap: two hypothetical2-GiB fields sum to0 modulo2^32 and take the warning path, while Modern computes2048+2048. These are arithmetic examples, not injected API returns.

The change also discards fractional MiB separately. Hypothetical8.75-MiB and7.5-MiB fields total16.25MiB and pass the original threshold, but Modern floors them to8+7 and warns. Thus this is not universally equivalent admission with only overflow fixed. Preserve the demonstrated arithmetic instead of silently summing in64 bits as a reconstruction “improvement.” API errors and platform-specific field population are not tested.

## Shared disk-check request and changed diagnostics

Both pass **EAX=1 MiB** to helper `004516a0`, testing its result and entering a warning branch on zero. The Modern message explicitly says the hard drive has less than1MB free. This establishes the checked request and diagnostic association; complete filesystem selection, unit conventions, helper failure causes and actual free space remain outside this comparison.

Original low-memory and disk warnings call MessageBoxA with flags31h and select text/caption pointers through the incoming index. Return2 leads to `004f2a7d`. Modern routes both through **`004b5728`**, which uses flags51031h and a shared caption, calls the same termination helper for return2, otherwise returns. The desktop-depth failure uses separate **`004b570c`**, flags51010h, followed by `004f2a7d` regardless of dialog result. Complete termination behavior/nonlocal exit guarantees are not established here.

## Added desktop-depth check

After the resource checks, Modern calls **GetDesktopWindow**, **GetWindowDC** and **GetDeviceCaps** with literal index12, then uses signed comparison against8. A result below8 invokes the fatal-diagnostic path with **“Cannot run if desktop bitdepth is less than 8.”** The manifest identifies the imported APIs at the actual IAT operands. The original counterpart returns after the disk warning and has no corresponding desktop-query sequence in that body.

This branch checks the returned capability directly; it does not multiply by a second planes capability, verify a renderer-supported game mode, or prove movie decoding compatibility. The local routine contains no ReleaseDC call; ownership, other cleanup or actual resource leakage is not established by that bounded observation.

## Register and reconstruction boundaries

Modern uses PUSHAD/POPAD, preserving the incoming general registers including EAX when its ordinary path returns. It does not provide an ordinary Boolean success result. Original saves EBX/ECX/EDX/ESI/EDI/EBP, consumes incoming EAX as its diagnostic table index and leaves an operation-dependent EAX result. The two should not receive one guessed C success-return signature.

Verified changes include memory-sum order/units, warning selection and flags, removed local logging and the added desktop check. Historical attribution, full localization fallback, resource API failures, the disk helper, termination and observed startup acceptance remain unresolved. This is an independently documented code delta, not a claim that every system-requirement path in either executable has been compared.
