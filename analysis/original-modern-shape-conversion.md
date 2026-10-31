# Shape conversion: cached renderer descriptor and removed fallback

## Scope and evidence

The saved Modern entry `004d37a0`, named `ConvertShapeForRenderer`, has a directly corresponding original entry at the same address. The complete envelope is `004d37a0..004d3f42` (exclusive end, 1,954 bytes), including the Modern NOP gap. The [reproducible audit](scripts/audit_shape_conversion_difference.py) checks both pinned executable hashes, retains disassembly and records the [comparison manifest](evidence/audits/shape-conversion-difference.json). Names describe the saved analysis; they are not original source symbols.

## Verified changes

| Location | Original | Official Modern |
|---|---|---|
| `004d37be..004d37c4` | Calls the renderer's `_THRASH_about@0` through `009ef980`; copies returned EAX to ECX | Loads the cached descriptor pointer from `007a3a5c`; copies it to ECX |
| `004d37ef..004d380c` | Tests descriptor ECX; if null, constructs a local fallback and points ECX at it | Tests saved incoming ECX (now EBX); zero branches directly to shared `004d3852` |
| Dimension selection before `004d3827` | Uses signed maximum of descriptor DWORDs `+10/+1c` and signed minimum of `+14/+20` | Retains those signed maximum/minimum values, with different instruction placement and equality branches |
| `004d380b..004d3827` | Contains fallback/selection instructions | 28 NOP bytes, skipped by the preceding jump |

The [renderer loader](original-modern-renderer-loading.md) establishes the about-export binding and accepted descriptor cache. Its [lifecycle report](original-modern-renderer-lifecycle.md) documents cache refresh. This change therefore removes a per-conversion indirect call; it does not establish that the descriptor can never change between refreshes.

The original null fallback writes DWORD `2` at frame offsets `-2` and `-e`, DWORD `256` at `+2` and `-a`, then uses frame address `-1e` as the descriptor. These are precisely the four subsequently selected DWORDs at descriptor offsets `+1c`, `+10`, `+20` and `+14`. For the inspected selection, the fallback maximum is 2 and minimum is 256. This does not imply every field in that local descriptor was initialized.

When saved incoming ECX/EBX is nonzero, Modern dereferences the cached descriptor without the original local null check. When it is zero, both versions skip the dimension-selection block. A valid-cache initialization requirement is consequently explicit in this Modern path; whether all callers satisfy it is outside this comparison.

## Coverage and reconstruction implications

All differing bytes in this envelope are confined to two maximal runs: `004d37be..004d37c3` and `004d37f0..004d3827`. The 1,819-byte suffix `004d3827..004d3f42` is byte-identical. The earlier type normalization also remains identical: descriptor supplied through EDI has its first DWORD retained for values 0, 3, 4, 6 or 7; other values are replaced with zero. That EDI pointer is distinct from the renderer descriptor in ECX.

For reconstruction, preserve the selected version's descriptor source, fallback policy and signed comparisons. Do not silently restore the original fallback in a Modern-compatible implementation or assume calling `_THRASH_about@0` has no side effects. The maximum/minimum equality paths choose equal DWORD values, but instruction flags and transient register contents are not claimed equivalent.

**Status: done for this bounded static difference; evidence confidence: verified.** Renderer descriptor lifetime, all caller contracts, pixel output and runtime safety remain unverified. This report does not prove full function equivalence: identical instructions can consume different descriptor data.
