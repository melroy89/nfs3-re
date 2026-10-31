# Setup website button versus Credits

**MP100-052 remains partially supported.** The official Modern Patch v1.6.1 menu asset removes the old website button found in a local uppercase backup. However, the original website callback and its binding remain byte-identical in the supplied original and official Modern executables. Removal of an asset entry must not be mistaken for replacement of that callback's code.

## Evidence

The [reproducible audit](scripts/audit_setup_website_difference.py) checks both executable baseline hashes and retains [asset hashes and instruction witnesses](evidence/audits/original-modern-setup-website.json). Addresses below are virtual addresses; range ends are exclusive.

| Location | Original and Modern observation |
|---|---|
| `0053965c` | Both contain `SETUP_NfsWebSite`. |
| `00453051..00453068` | Identical lookup through `00442a40`; if a matching entry exists, store callback `00452e60` at entry offset `64h`. A missing entry skips the write. |
| `00452e60..00452f16` | Complete callback body is identical. It calls `0049f790` and conditionally `0049f880`, selects language IDs `1c0h`, `1c1h`, `c4h`, `c5h` or `1c2h`, `f9h`, and calls `004446d0` with branch-specific callbacks `00452de0` or `00452d80`. No claim is made here about the untraced callees' runtime effects. |
| Official package `fedata/menus/setup.mnu` | No `website` or `credits` text occurs. The former website button is absent; there is no explicit Credits replacement entry in this file. |
| Local backup `fedata_org/menus/SETUP.MNU` | Contains a button with `codelink=SETUP_NfsWebSite` and `text=kMenuSETUPNFSWebsi001`. Its backup directory name does not authenticate retail provenance. |

The executable assignment is conditional on asset lookup succeeding. Consequently, retained callback code is consistent with a removed button and does not prove that the old button is still reachable in Modern.

## Final package uses Options, not an explicit Credits button

The audit now records all six `[button]` sections in file order. Their first four entries and sixth Exit entry have identical selected routing/label/type fields in the official file and local backup. Only the fifth button differs in those fields:

| Field | Local uppercase backup | Official v1.6.1 package |
|---|---|---|
| `buttontype` | `LR1of2` | `LR1of2` |
| `codelink` | `SETUP_NfsWebSite` | Absent |
| `text` | `kMenuSETUPNFSWebsi001` | `kMenuMAINOptions001` |
| `nextmenu` | Absent | `options` |

The README's **MP140-017** (v1.4.0, source line 301) says an Options button is placed near Exit on the first Game Setup screen. This later claim matches the final asset's Options/Exit pair. The earlier **MP100-052** reports Credits in v1.0.0. These are release-history claims, not two simultaneous descriptions of the final first-screen layout. The final asset supplies an explicit Options route; there is no reason to assume this particular final button must activate Credits.

**Confidence:** verified asset fields and unchanged selected executable ranges; inferred chronology linking the later note to the final layout. Actual screen/resource selection, translated label appearance and execution remain untested. Neither the v1.0.0 Credits implementation nor the v1.4.0 introduction date is verified without intermediate packages.

## Reconstruction implications and remaining work

For reconstruction, preserve the distinction between asset-defined controls, callback installation and shared Credits page rendering. The [page renderer investigation](original-modern-frontend-page.md) establishes a separate changed Credits/About rendering path; it does not establish this first-screen button's activation route.

To finish the historical MP100-052 claim, obtain v1.0.0 and inspect its first-screen asset and activation route. For final-package behaviour, trace the first-screen loader and generic `nextmenu=options` handling, then verify the selected resource or external menu at runtime when a suitable session is available. Do not make recovery of a superseded Credits button a prerequisite for explaining final Options routing. Historical introduction in v1.0.0 requires that release, rather than inference from the final v1.6.1 package. The local backup comparison is bounded evidence, not a universal original-asset baseline.

Reproduce: `python3 analysis/scripts/audit_setup_website_difference.py`. This uses read-only PE parsing and disassembly. No executable bytes, Ghidra database, reference exports or reconstruction sources were changed; no target instructions were executed.
