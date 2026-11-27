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

**Confidence:** verified asset fields and unchanged selected executable ranges; inferred chronology linking the later note to the final layout. Actual screen/resource selection, translated label appearance and execution remain untested. The historical asset comparison below now verifies Credits in retained1.1.0/1.3.1 and the authored Options change at1.3.1→1.4.0. Exact1.0.0 introduction and runtime activation remain unverified.

## Reconstruction implications and remaining work

For reconstruction, preserve the distinction between asset-defined controls, callback installation and shared Credits page rendering. The [page renderer investigation](original-modern-frontend-page.md) establishes a separate changed Credits/About rendering path; it does not establish this first-screen button's activation route.

The 1.0.0 first-screen asset is verified below. Its activation route still needs a caller and menu-state check. For final-package behaviour, trace the first-screen loader and generic `nextmenu=options` handling, then verify the selected resource or external menu at runtime when a suitable session is available. Do not make recovery of a superseded Credits button a prerequisite for explaining final Options routing. Historical introduction in v1.0.0 requires that release, rather than inference from the final v1.6.1 package. The local backup comparison is bounded evidence, not a universal original-asset baseline.

Reproduce: `python3 analysis/scripts/audit_setup_website_difference.py`. This uses read-only PE parsing and disassembly. No executable bytes, Ghidra database, reference exports or reconstruction sources were changed; no target instructions were executed.

## Generic Options transition: retained code, changed asset route

Existing [menu dispatch research](connect-menu-dispatch-crosswalk.md) established `nextmenu` at item offset `40h`. This follow-up compares the relevant bytes against both pinned executables instead of transferring an active-build observation without checking the original.

The expanded audit verifies byte identity of these bounded code and data ranges:

| Location | Role and verified scope |
|---|---|
| `00557e10`, 16 bytes | Field-definition row `{5,00538550,4,00604f20}`: button `nextmenu`, arena-string field type 4, destination entry-base `00604ee0 + 40h`. |
| `00556e40`, `bch` bytes | Button template, type 5, input handler `00461270` at `+30h`; file-backed `+58h` and `+64h` zero. Later writes are not excluded. |
| `00461270..004613db` | Complete generic button handler. On Enter (`DI=13`), with `+58h=0`, no specialized callback at `+64h`, and neither special codelink command matching, non-null `+40h` returns action 5. A registered callback takes precedence. |
| `0044b6c8..0044b6de`, table slot `0044b20c` | Subtract 4, unsigned range-check 0..7, then dispatch through table. Action 5 selects `0044b7ec`. |
| `0044b7ec..0044b8ad` | Compute current entry from signed high-word descriptor indices and `bch` stride. If it is the helper-selected default entry, use action 3; otherwise for type 5 take its `+40h` pointer, search descriptor names using `004ee310`, and on a match assign active descriptor `00559230 = 006040d0 + index*24h`. Missing/null targets take other branches; successful transition is conditional. |
| `00449762..004497c9` | Loader dependency scan reads current entry `+40h`, skips empty target names and searches existing `24h`-stride descriptors. This captures only the lookup region, not the complete loader or queue-creation branch. |
| `00555c48`, 24 bytes | Static registration row names `options` at `00537c10`, with callback `00442aa0` at `+0ch`; other words zero in both inspected images. This static row is distinct from the runtime `24h`-stride descriptor array. |

For the final asset's ordinary Options button, these witnesses explain a conditional path from the new `nextmenu=options` string to generic transition lookup. They do not establish the actual loaded descriptor list, later item overrides, successful external file loading, current selection or pixels. The full loader differs between binaries and is **not** declared unchanged because its selected dependency-scan region is identical.

For maintained C, keep template defaults, string-field parsing, specialized callback precedence, action codes and descriptor lookup as separate responsibilities. Replacing the old website callback body is not required merely to represent this final asset's Options route. Preserve normal missing-target/default-entry behaviour until separately validated; do not silently turn the conditional path into an unconditional transition.


## Early Credits route and140 Options replacement are present in assets

The [historical menu audit](evidence/audits/setup-button-history.json), reproduced with `python3 analysis/scripts/audit_setup_button_history.py`, verifies archive hashes and records member hashes for `fedata/menus/setup.mnu`. It supersedes the earlier uncertainty about intermediate asset availability, while leaving first-release and runtime claims separate.

| Retained package | Fifth button text token | Codelink | Next menu |
|---|---|---|---|
|1.0.0–1.3.0 |`kMenuOPTIONSCredits001` |`credits` |`credits` |
|1.3.1 |`kMenuOPTIONSCredits001` |`credits` |`credits` |
|1.4.0 |`kMenuMAINOptions001` |Absent |`options` |
|Official final |`kMenuMAINOptions001` |Absent |`options` |

The original audit’s four packages and the inspected 1.0.0 package each have six buttons. The fifth retains `buttontype=LR1of2`; the sixth Exit entry retains `LR2of2`. The selected text/codelink/nextmenu/buttontype fields of the other five buttons match across all four packages. Other properties and complete file bytes are not declared identical. File ordering and these type names alone do not establish pixel placement.

Thus MP100-052 has explicit **early authored Credits-route evidence**, not merely removal of a website entry inferred from final assets. The retained 1.0.0 archive already ships this fifth button and its target `fedata/menus/credits.mnu`. Its `setup.mnu` SHA-256 is `30e1bf780668caa1c471d67494671c6256bf2d0c2dd503ef94f5a2ce7a23310a`. The intermediate 1.2.0 and 1.3.0 assets retain the Credits text, codelink and next-menu fields. MP140-017 has a verified **1.3.1→1.4.0 authored Options replacement**, retained final. The existing paired original/final generic transition witnesses explain the final route conditionally; they have not been revalidated against each historical EXE and do not prove successful historical Credits activation. Loaded resources, callback precedence, translated labels and visible screens remain runtime/loader follow-up work. No target instructions or Ghidra changes were made.

### Early EXE lookups can mark Credits items disabled

In retained 1.0.0 the lowercase `credits` string at
`00537494` is supplied to the item lookup at `004374dc`,
`00437616` and `004377e6`. Each site checks for a returned
item, then ORs bit 0 into its byte at offset `+4` when
signed `006fd3b0 > 1`. These local branches update the
item flag. They do not install a dedicated activation
callback. The inspected lookups alone do not establish
which setup contexts receive the item or whether other
paths install a callback. The authored `nextmenu=credits`
remains independent evidence of the shipped route.
