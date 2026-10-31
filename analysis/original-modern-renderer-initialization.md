# Original versus Modern: renderer initialization dispatch

## Evidence and scope

Static comparison of the supplied original/backup and official Modern v1.6.1, with the exact fingerprints in the [renderer loader report](original-modern-renderer-loading.md). Reproduce using `python3 analysis/scripts/audit_renderer_selection_difference.py`; the [manifest](evidence/audits/original-modern-renderer-selection.json) retains complete selector spans, dispatch targets and file-backed strings/state pairs. No target, DLL or instruction probes were executed. Selector values below are observed code values, not authenticated original UI labels.

## Original: numeric selection before loading

Original `004b59c0` saves the EAX selector, clears `007a3a6c` and `007a3a70`, rejects unsigned values above 10, then dispatches through `004b5994`. The table and candidate-name table give:

| Selector | Candidate name | Branch target |
|---:|---|---|
| 0 | nulla.dll | `004b59ef` |
| 1, 2 | softtria.dll, softlina.dll | `004b5a28` |
| 3, 4 | voodooa.dll, voodoo2a.dll | `004b5ab8` |
| 5 | ragea.dll | `004b5bef` |
| 6 | d3da.dll | `004b5c76` |
| 7, 8 | powervra.dll, powervra.dll | `004b5d65` |
| 9, 10 | empty strings | `004b5e0a` |

Each of the six loading branches calls `004f87e0`, then `004f8830` and `004f8930`; each tests `00564364` and calls `004f2a7d` when zero. The wrapper's environment override can replace these candidates, so the name table does not prove which DLL actually loads. Branches 9/10 instead invoke the message path and `004f2a7d`. The out-of-range path invokes `004b5e50` and `004f2a7d`. Their full error/termination behavior is not established here.

Branch 3/4 invokes `004f8b50` with `SST_SLIDETECT="0"` before loading. After loading it invokes the same helper with empty strings for `SST_RGAMMA`, `SST_GGAMMA`, `SST_BGAMMA`, `SST_GAMMA` and their four `SSTV2_` counterparts. EBX=1 requests replacement in these calls. In `004f8b50`, an empty supplied value with that flag becomes null before SetEnvironmentVariableA at `004f8ba1`; subsequent code also updates runtime environment bookkeeping. These are environment-removal requests, not numeric gamma values of zero. API success and actual driver effects remain untested.

Branch 6 calls GetDesktopWindow, GetWindowDC and GetDeviceCaps with property index 12, then takes its diagnostic path when the result is signed-less-than 8 (`004b5c76..004b5c92`). These API identities were read from the original import table. It then performs additional renderer calls before the shared-looking state sequence. These operations are absent from Modern's smaller type-dispatch body, but may have counterparts elsewhere or in the DLLs.

## Modern: load configured driver, then dispatch by type

Modern `004b5a58` first invokes configuration `004b5844`, optional DirectDraw compatibility dispatch, and loader `004f84a8`, then clears `007a3a68`, `007a3a60` and `007a3a6c`, and calls `00517620`. Failures route through diagnostic helper `004b570c`; this audit does not assume that helper returns or terminates in every context.

The type parser documented in the loader report supplies nonzero masks: generic=1, s=2, v=16 and d=64. `004b5ab6` uses BSF to select the **lowest set bit**, rejects indices above 6, and jumps through `004b5a3c`:

| Lowest bit index | Mask example | Target | Local setup |
|---:|---:|---|---|
| 0, 5 | 1, 32 | `004b5bfb` | Immediate return after prior common initialization |
| 1, 2 | 2, 4 | `004b5acd` | Software-like state sequence, then `00431c50` |
| 3, 4 | 8, 16 | `004b5b78` | Set both `007a3a68/60` to 1; common hardware-like state sequence |
| 6 | 64 | `004b5b0f` | Same two flags, five table-driven state calls, then hardware-like state sequence |

Only the parser's four normal masks are established configuration outputs. The other table cases are not evidence of selectable supported drivers. BSF with zero input has no defined destination value; do not invent a safe zero-mask contract from the normal nonzero parser outputs.

## Retained sequences and important differences

All state calls below use retained `_THRASH_setstate@8` slot `009ef96c`; pairs are **selector, value**, inferred from the observed push order. Slot `009ef970` is called between setup groups; its implementation is outside this audit.

- Original software branches and Modern `004b5acd` both issue `(10,2)`, `(3,0)`, call slot `009ef970`, then `(4,0)`, `(6,0)`, `(2,0)` and call `00431c50`.
- Modern d-type emits five pairs from file-backed table `0055fd94`: `(13,1)`, `(13,0)`, `(4,2)`, `(206,1)`, `(104,1)`. It then emits `(10,2)`, `(104,0)`, calls slot `009ef970`, then `(4,1)`, `(6,1)`, `(2,0)`. This is not equivalent to merely loading a different DLL.
- Modern v-type emits `(10,2)`, calls slot `009ef970`, then `(4,1)`, `(2,0)`. It does not issue the explicit `(6,1)` present in the Modern d-type branch. Original Voodoo setup also omits selector 6 in its inspected branch.
- Modern software/d/v paths reach the fog check at `004b5bb0`. If configured fog is nonzero, `(21,4)` is tried; a zero result clears `007a3a54`. Then `(21,0)` is issued unconditionally. This proves a query/result gate, not the undocumented selector's full semantics or visible fog correctness.
- Those paths next read descriptor fields `+0x14/+0x20`, take their unsigned minimum and reduce the configured texture extent until it fits. See the [texture comparison](original-modern-texture-limits.md). The software branch jumps to the same common block at `004b5b0a`; the generic target returns directly and skips it.

Original branches also write `0055fed0` with fixed values 4 MiB, 8 MiB or 2 MiB, plus distinct flags at `007a3a64/68/60/70`. Modern does not perform those same stores in this initializer, and `0055fed0` has a different documented role in Modern's border code. Do not carry original global meanings into Modern just because the address matches.

## Limits and remaining work

The tables and instruction sequences are verified static evidence. Driver category names are interpretation from candidate names/configuration letters; state-selector meanings remain opaque unless independently established. The [lifecycle comparison](original-modern-renderer-lifecycle.md) now traces original callback installation, the actual original `00517610` counterpart and Modern’s direct `00517620` mode path. Complete error-helper and descriptor-consumer contracts remain pending. The [registry/selector follow-up](original-modern-registry.md#original-selector-precedence-and-call-chain) now traces registry names, fixed command-line priority and the direct setup-to-initializer chain. Higher-level callers, alternate selector writes, DLL implementations and actual renderer behavior still need comparison. Historical release introduction cannot be dated from original versus final alone.
