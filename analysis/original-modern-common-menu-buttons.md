# Standard menu controls: official assets versus local backups

**MP140-018 is partially supported by package evidence.** The official v1.6.1 menu definitions for Connect Players, Connect IPX and View Car Interior explicitly contain Options and Exit buttons absent from the corresponding uppercase local backups. This establishes an asset difference; actual runtime selection and introduction in v1.4.0 are not proven.

## Source identity and inventory

The [inventory script](scripts/inventory_official_menu_routes.py) checks the retained official archive SHA-256 `c023058bde17d1430d874c29dae71b61cf998a66e8a1b6994dae401205b444b3`, inventories **52** extracted `.mnu` files, and compares each file hash to the corresponding archive member read directly with `7z x -so`. Every file has an uppercase counterpart in the local `fedata_org/menus` backup. **Zero of these 52 pairs are byte-identical.** That does not mean every button or semantic field differs: whitespace, ordering, comments and unrelated fields can change the file hash.

The [retained JSON inventory](evidence/inventories/official-menu-routes.json) records file paths, lengths, hashes, exact-match results, button section line numbers and selected routing fields for all 52 pairs. Uppercase backup names do not authenticate original retail provenance. These are neither original source files nor proof that every supplied-original installation used these assets.

## Three release-note targets

| Official menu | Added control definitions relative to selected backup | Relevant details |
|---|---|---|
| `connect.mnu` | Options `LR1of2`; Exit `LR2of2` | Options uses `text=kMenuMAINOptions001`, `nextmenu=options`, `codelink=escape`. Exit uses `text=kMenuSETUPExitGame001`, `codelink=exitprogram`. |
| `ipx.mnu` | Options `LR1of2`; Exit `LR2of2` | Same selected label/routing/type fields as the Connect pair. |
| `interior.mnu` | Race `LR1of3`; Options `LR2of3`; Exit `LR3of3` | Race uses `codelink=racenow`, `text=kMenuMAINRACE001`; Options uses `nextmenu=options`, `text=kMenuMAINOptions001`; Exit uses `codelink=exitprogram`, `text=kMenuMAINExitGame001`. |

The script asserts presence of Options and Exit in all three official files, and their absence in the three selected backups. It ignores commented-out lines and retains section boundaries. It is an inventory of the authored fields, not a full emulation of the game's menu parser; duplicate-key and lexical edge cases have not been qualified against the original parser.

## Code connection and reconstruction scope

The [setup-button comparison](original-modern-setup-website.md#generic-options-transition-retained-code-changed-asset-route) verifies the generic button handler and relevant transition ranges are byte-identical in original and Modern. A simple button with no overriding callback and a non-null `nextmenu` can return action 5; the loop then conditionally resolves a loaded descriptor. `exitprogram` and `racenow` are separate recognized commands with distinct action/state handling. The authored `escape` token is recorded here without claiming that its complete Escape-key admission/priority has been traced for these menus.

A reconstruction needs both the menu assets and generic routing machinery. The observed added controls do not themselves require three bespoke new C callback implementations. Entry initialization can still alter visibility, callbacks or selection; actual selected files, initialized fields, multiplayer state and rendered output remain untested.

Related release entries **MP140-019** (controls persist when Options opens from race results) and **MP140-020** (Race hidden when Options opens from the first screen) describe lifecycle policy, not merely these asset definitions. They remain separate from this finding. Reuse the [Race Now policy audit](original-modern-race-now.md), then map the entry contexts and global writers before promoting either claim. Do not infer these dynamic behaviours from the presence of the controls alone.

## Follow-up

1. Confirm actual runtime selection of these external files versus fallback/resource definitions.
2. Map menu initialization overrides and Escape routing for the three contexts.
3. Inspect historical v1.4.0 assets to verify release attribution; authenticate original assets if a universal original-versus-patch asset claim is needed.
4. Validate controls and return navigation in a suitable game session, separately from static comparison.

Reproduce: extract `fedata/menus/*` from the pinned retained archive into `analysis/captures/modern-differences/upstream/package`, then run `python3 analysis/scripts/inventory_official_menu_routes.py`. Target binaries, saved Ghidra state, raw exports and maintained reconstruction are unchanged. No game or instruction probes were run.

## Controller reset button: authored position7→8

The focused [controller-reset asset audit](evidence/audits/controller-reset-asset.json), reproduced by `python3 analysis/scripts/audit_controller_reset_asset.py`, reads `fedata/menus/control1.mnu` directly from the hash-pinned official archive and compares the uppercase local backup **`fedata_org/menus/CONTROL1.MNU`**. Each has one `[button]` with text token **`kMenuCONTROL1ResetToD001`**, `codelink=reset` and `buttontype=tab`.

The backup specifies **`ypos=7`**, official Modern **`ypos=8`**. Both retain x0/y0, priority11, listpos0/listoff0 and align0 for this control. The preceding Predefined control remains `ypos=6` and links `hardkeys` in the inspected files. The reset change is therefore authored tab-position metadata, not a change from literal screen y7 to y8 pixels.

This gives partial asset evidence for **MP140-027**, the reported one-position downward shift. It does not authenticate the backup as original retail, prove which asset is selected at runtime, establish parser defaults for omitted legacy fields or verify the rendered result. The text token and reset binding remain associated; full reset callback semantics and layout interpretation are separate investigations. No settings were reset and no menu was opened.

## Long-list authored visible counts

The [visible-count audit](evidence/audits/menu-visible-counts.json), reproduced by `python3 analysis/scripts/audit_menu_visible_counts.py`, scans all52 official `.mnu` archive members and uppercase backup counterparts. It pairs sections only when `(section type,listname)` has exactly one `maxvisitem` field on each side. Nine unique pairs differ:

| Official menu | Section/listname | Backup → Modern `maxvisitem` |
|---|---|---:|
| `graphics.mnu` | cascade / `winsize` | 10→16 |
| `main.mnu` | cascade / `cars` | 7→9 |
| `main.mnu` | cascade / `opcars` | 5→9 |
| `mainmult.mnu` | cascade / `classLimiter` | 4→9 |
| `mainmult.mnu` | cascade / `cars` | 7→9 |
| `mainmult.mnu` | cascade / `opcars` | 5→9 |
| `mainsplt.mnu` | cascade / `cars` | 7→9 |
| `mainsplt.mnu` | cascade / `car2` | 7→9 |
| `mainsplt.mnu` | cascade / `opcars` | 5→9 |

Seven Modern fields lack a unique matching section/listname pair; the manifest retains them explicitly instead of treating them as unchanged or added. It also retains hashes of all52 official/backup member pairs. The comparison checks authored fields, not comments or whole-file similarity, and does not infer equivalent defaults from omitted fields.

This gives partial support for **MP140-025**, increased visible elements in long lists. The actual count can still depend on list length, initialization and layout code. These changed sections are cascades; the separate droplist renderer/alias analysis must not be generalized to them solely because a list name overlaps. Backup retail provenance, runtime selected assets, actual rows displayed and historical introduction remain unverified. No UI or settings were changed.

## Unpaired counts: cross-menu appearances and backup-only fields

The audit now records unmatched fields in both directions. Its original seven Modern-unpaired values are:

| Modern member | Section/listname | `maxvisitem` |
|---|---|---:|
| `advgrph.mnu` | cascade / `fog` | 5 |
| `advgrph.mnu` | cascade / `widescreen` | 10 |
| `camera.mnu` | cascade / `rearcamera` | 5 |
| `graphics.mnu` | cascade / `mirrorlevel` | 5 |
| `graphics.mnu` | cascade / `viewlevel` | 5 |
| `hud.mnu` | droplist / `hudtypesingle` | 15 |
| `hud.mnu` | droplist / `hudtypesplit` | 15 |

Five backup-only `(member,section,listname)` bindings are also retained: `advgrph.mnu` cascade `viewlevel`5; `graphics.mnu` cascade `widescreen`10; and `hud.mnu` droplists `buyERTS`, `buyERTS_at75`, `buyERTS_at100`, each15. “Backup-only” means no matching field in that official member, not absence of the underlying feature throughout Modern.

The same `widescreen` binding/count therefore appears in a different menu (backup graphics versus Modern advanced graphics), and likewise `viewlevel` (backup advanced graphics versus Modern graphics). This supports authored redistribution without inventing a count increase for those two values. Complete menu routing, widget equivalence and historical relocation still require separate linkage. The HUD names are not paired as simple renames without descriptor/consumer evidence.

No “seven new controls” claim follows from the one-way matching result. The nine uniquely paired numeric increases remain distinct from this unmatched/redistributed set. Both sets retain the same backup provenance and runtime-selection limitations.

## Executable binding for `maxvisitem`: parser packing still open

The visible-count audit now verifies the executable baselines as well as assets and retains two16-byte descriptor rows at **`00557d80`** and **`00557dc0`**. Both refer to the exact NUL-terminated literal **`maxvisitem`**. Modern rows decode as **`{11h,0053852c,1,00604f34}`** and **`{1dh,0053852c,1,00604f38}`**; both original counterparts are retained separately in the manifest rather than assumed equal from addresses.

The destinations lie at **`00604ee0+54h`** and **`00604ee0+58h`**, within the shared menu-construction record used by existing [menu text-field research](original-modern-menu-text-fields.md). This establishes a binary field-name binding for the authored values. It does not yet establish how the descriptor’s other words select section/type behavior, how an integer is packed into WORD components, or which final widget field receives each value.

Required follow-up is the descriptor consumer and construction/copy path, then the cascade layout consumer. Until that chain is verified, the asset increases above remain authored-limit evidence, not a measured or fully derived runtime row-count change. Direct reads of nearby widget offsets are insufficient to bridge that gap by themselves. No parser or game code was executed.

## Descriptor consumer resolves the two-byte store

Following writer **`00449240`** corrects a prior four-byte row-alignment error: `00557d84`/`00557dc4` are the **name fields** inside rows starting at `00557d80`/`00557dc0`. The four-word row descriptions above and manifest now use the aligned starts. Values`11h/1dh` are the first word of their respective rows, not trailing conversion metadata.

The writer multiplies its descriptor index by16 and reads conversion type from table base **`00557c10+8`**, destination pointer from base+`0x0c`. It subtracts construction base **`00604ee0`** from the latter, computes **`00604ee0 + 0xbc*instanceIndex + destinationOffset`**, and dispatches conversion type through **`00449218`**. Both selected rows specify type1, whose target is **`004492aa`**: call numeric conversion helper `00449130`, prepare a local DWORD but set copy length to **2**. Shared copy tail **`00449393..004493a3`** then copies exactly those two bytes to the instance destination.

Thus the authored count is stored as the low WORD of the numeric conversion result at instance offsets **`0x54`** or **`0x58`**, rather than a full DWORD at a fixed global address. The audit retains paired writer spans and checks the type1 dispatch target. Numeric parsing bounds/overflow, the first descriptor word’s complete section/type admission, and the separate cascade effective-count calculation remain follow-up work. This closes the local storage-width/instance-address question without claiming that the authored value is always the final visible count.

## Droplist effective count: signed WORD minimum

The audit retains paired input-handler prefix **`00463ff0..00464052`** and lookup/count helpers **`00442bf0..00442c49`**, **`00442c50..00442c74`**. Both baselines use the same calculation. The count helper result is saved as a DWORD at local−4; the separate descriptor lookup result is saved at local−8.

- Load widget DWORD+`0x56`, then arithmetic-shift16: this sign-extends the authored WORD+`0x58`.
- Store the full count at `[ebp-4]` (`00464032`).
- Load DWORD `[ebp-6]`, then arithmetic-shift16 (`00464038..0046403e`). This unaligned read spans bytes−6/−5 from the descriptor local and bytes−4/−3 from the count local. The shift discards the descriptor bytes and sign-extends the **low WORD of the count**.
- Compare that signed count WORD with the signed authored limit. If less, select the count; otherwise select the authored WORD. Store the resulting WORD at widget+`0x5a`.

For counts and authored limits in **0..32767**, the stored value is therefore **`min(listCount,maxvisitem)`**. Outside that range, signed16 interpretation and truncation matter; do not translate this into an unrestricted unsigned or full-width integer minimum. The audit pins the key instruction bytes and includes host byte-layout witnesses, including count32768→−32768 and65535→−1. These witnesses check the interpretation of overlapping bytes; they do not execute the game or establish reachable list sizes.

**Correction to the prior analysis:** the shifted DWORD at local−6 does not extract the high WORD of local−8. The earlier claim that descriptor address bits affect this comparison was incorrect and is superseded here. Helper `00442bf0` returns the DWORD stored at descriptor offset+8 (not the address of that field); its result is not the count operand in this comparison.

Count helper `00442c50` separately obtains a WORD-list pointer through `00442c80` and counts to a zero WORD sentinel. This handler consumes the droplist cap at offset0x58; the nine uniquely paired authored increases above are cascades with a different destination, and are not linked to this handler by that evidence. Actual list contents, construction-to-widget copying, initial layout and rendered rows remain separate verification requirements. No runtime row count or historical introduction is established. The parser, list scan and widget handler were not executed.

## Expanded-list extent consumes the effective count

Paired span **`004645e3..00464601`**, now retained by the visible-count audit, connects effective count WORD+`0x5a` to expanded layout. At `004645f1` the helper loads that WORD into AX, shifts EAX left4, adds2, and stores AX at widget+`0x20`. Its low-WORD result is therefore **`(16 * effectiveCount + 2) mod 65536`**; the untouched upper EAX bits do not affect that stored WORD. Original instead adds5 at `004645f8`, so its stored extent is **`(16 * effectiveCount + 5) mod 65536`**. Modern therefore reduces this extent by3 internal units for an equal count. At the adjacent width-padding addition `004645ea`, original adds5 and Modern adds15 to the local padding before adding it to DI; that is a separate +10 padding change.

Within the normal small positive range, hypothetical original→Modern counts5→9 produce this extent85→146,7→9 gives117→146,4→9 gives69→146, and10→16 gives165→258, in internal layout units. These are illustrative arithmetic examples, not established consequences of the nine cascade asset changes, measured screen pixels or evidence that a populated droplist reaches its cap. The surrounding helper takes this path only when the widget is expanded (WORD+`0x40` nonzero) and list lookup returns a nonzero pointer. Width calculation and alignment have separate inputs; the cap does not by itself establish the final rectangle.

This closes a local effective-count-to-extent consumer. The attempted construction follow-up has not yet established the complete pointer/copy chain from parser instance to active widget, so that linkage remains open. Do not replace that missing evidence with the matching offset alone. The extent span was inspected statically; no layout helper or list scan was executed.

## Complete layout-helper difference coverage

The audit now compares the complete **379-byte** body **`00464560..004646db`** (end exclusive), including both RET paths. Every changed byte falls within three half-open regions: **`0046456b..00464587`** (selector rewrite), **`004645eb..004645ec`** (width-add immediate), and **`004645f9..004645fa`** (count-extent immediate). The manifest enumerates exact changed addresses; the audit asserts that there are no differences outside these regions in this body. This is bounded body coverage, not whole-menu or whole-callee equivalence.

Original selects local padding35 whenever global `006fd3b8==3`, otherwise15, without checking the list name. Modern calls the [track-policy helper](original-modern-car-alias.md#separate-adjacent-helper-track-list-policy-alias) using widget+`0x64` and selects35 only for mode3 with ASCII-case-insensitive `tracks` or `rectrk`; otherwise15. Including the separate original+5/Modern+15 addition gives:

| Condition | Original padding contribution | Modern contribution | Difference |
|---|---:|---:|---:|
| Mode not3 | 20 | 30 | +10 |
| Mode3, `tracks` or `rectrk` | 40 | 50 | +10 |
| Mode3, another list name | 40 | 30 | −10 |

These contributions are added to the width WORD with the final store truncated modulo65536. They describe the arithmetic for equal incoming measured widths, not guaranteed complete width differences under changed assets or callees. The mode’s semantic name remains unresolved. Modern does not universally enlarge this helper’s width.

All local instructions after the selector through the list scan, except the two immediate bytes above, are retained. The scan starts width WORD+`0x1e` at40, traverses WORD IDs to a zero sentinel, calls `004d1850` with EDX18 then `00452020`, and updates width when the returned signed width exceeds the current signed WORD. The expansion tests, alignment arithmetic and collapsed-layout path are locally unchanged. Callee bytes/semantics, live strings, callback admission and constructed widget identity require their own evidence; unchanged CALL operands alone do not establish them. No target instructions were executed.

## Type registration separates cascade and droplist consumers

Direct file-backed registration rows establish **`00557ab4={11h,name cascade,template00556ea8}`** and **`00557ac0={1dh,name droplist,template00556f0c}`** in both binaries. The droplist template contains initializer`00463e60` at+`0x24`, renderer`004634d0` at+`0x2c`, input handler`00463ff0` at+`0x30`, and layout helper`00464560` at+`0x34`. The audit retains both rows, resolved names, template addresses and callback DWORDs.

This resolves an earlier scope mistake: the signed-WORD minimum and expanded extent studied above belong to **droplist**, not cascade. The nine uniquely paired authored cap increases are all cascades. Their parser descriptor type`11h` stores at construction offset`0x54`; the droplist descriptor type`1dh` stores at`0x58`. Matching a list name across widget types does not bridge these different layouts. Earlier statements connecting those nine increases directly to the inspected droplist handler are superseded by this type evidence.

Template installer`00449060..004490d8`, now retained in both binaries, searches12-byte registration rows by type ID, loads the template pointer, and copies **`0xbc` bytes** into construction record`00604ee0 + 0xbc*instanceIndex`. This establishes the callback/default installation mechanism alongside the parser’s later instance-field writes. It does not yet prove every callback invocation or that every template’s source object has an independently verified0xbc-byte layout; the observed copy length is preserved as evidence.

Next, inspect the cascade template’s own callback targets and offset`0x54` consumers to connect its nine authored changes. For droplist, trace active instance selection and callback invocation before declaring full construction-to-render linkage. No initializer, parser, callback or template copy was executed.

## Cascade cap reaches its own effective-count and layout fields

Following the registered **cascade** callbacks now supplies the missing widget-specific chain. Its type11h template records initializer **`004623a0`**, renderer **`00461d00`**, input handler **`004624a0`**, and layout **`004628d0`**. The type1dh droplist registration remains separate.

The complete **251-byte** initializer`004623a0..0046249b` is byte-identical. It tests WORD widget+`0x54`; if zero, it writes **2000** there. Nonzero authored values survive this local defaulting step. It also clears expanded flag WORD+`0x42`, selection WORD+`0x52`, and WORD+`0x58`, while storing cap−1 at WORD+`0x5a`. Other asset/resource setup calls in this initializer remain external dependencies.

The paired input span **`004624d7..004624fa`** is byte-identical and calculates:

1. Obtain list count through`00442c50`, using list name at widget+`0x60`.
2. Sign-extend authored cap WORD+`0x54` via DWORD+`0x52` shifted16.
3. Sign-extend the low count WORD using MOVSX EDI,AX.
4. If signed count is less than cap, keep count; otherwise select cap. Store chosen WORD at **widget+`0x56`**.

Within count/cap range0..32767 this is `min(listCount,maxvisitem)`. Signed16 edge cases and truncation remain part of the contract. The preceding prefix checks for a nonzero list pointer before this path; it does not establish a complete list-length bound or the validity of every data pointer.

The [complete cascade layout helper](original-modern-car-alias.md#complete-004628d0-layout-helper) reads exactly that WORD+`0x56`, then stores WORD extent+`0x20` as original`16*count+5`, Modern`16*count+2`. Thus the nine uniquely paired **cascade** cap increases now have a supported local consumer chain, distinct from the previously misattributed droplist path. When a selected list is long enough to reach both authored caps, their conditional original→Modern extents are:

| Authored cap change | Conditional extent change |
|---|---|
| 4→9 | 69→146 |
| 5→9 | 85→146 |
| 7→9 | 117→146 |
| 10→16 | 165→258 |

These are internal WORD arithmetic results, not measured physical pixels. Shorter lists can produce different effective counts; cap defaults, callback timing and expanded state also matter. Active file selection, parser section admission, actual list population and callback invocation remain unobserved. This closes the **registered local field/consumer chain**, not the rendered outcome or historical release attribution. No game instructions were executed.

## Cascade input changes beyond the cap calculation

The paired audit now covers input envelope **`004624a0..004628c8`**. Original’s last RET is`004628c0`; Modern extends the final navigation path with a JMP at`004628c3` to a reused return/sound tail. The manifest enumerates every differing byte and asserts coverage by five half-open regions: `004624d2..004624d7`, `00462509..00462525`, `004625b6..004625c0`, `00462658..004626bf`, `004628b7..004628c8`. The envelope includes original alignment bytes after its last RET; it is not a claim that those bytes were executable original handler instructions.

The local changes are broader than sound-call relocation:

- **Closed input admission:** both test Enter`0dh` and right-arrow code`4d00h`. Original’s other-key path jumps directly to the ordinary return tail`004628b7`; Modern routes it to`004626af`. These local no-action paths return the saved local result without entering opening logic.
- **Opening:** original requests sound selector1 through`004181d0` before setting expanded WORD+`0x42` and performing layout/cursor work. Modern removes that early request, retains opening work, then jumps from`004625b6` to the shared sound1 tail`004626a5`. The request therefore moves after layout/cursor work. Audible output and helper failure effects are not measured.
- **Commit/close:** original has duplicated sound1/close/layout/return sequences. Modern writes the selected index through the lookup-provided output pointer, then joins the common close path`00462691`: clear expanded WORD+`0x42`, call layout`004628d0`, store result local2, request sound1, return that local. The descriptor/selection admission tests preceding this region remain separate from assuming every key commits.
- **Expanded navigation tail:** after cursor helper`0049bfc0`, original returns the existing local result. Modern explicitly stores result2, loads EAX0 and jumps to the shared sound-call instruction`004626aa`. This adds a local sound0 request and changes how the returned action code is assigned. The meaning of result2 in the higher dispatcher remains unresolved.

Original sound sites explicitly prepare EDX127; Modern’s shared requests do not reproduce that preparation locally. The sound helper’s actual register contract and configuration-dependent output must be read from its own research before treating selector equality as full call-state equality. The cap minimum and most navigation arithmetic are unchanged in this envelope, but callback return codes and side-effect ordering are reconstruction-relevant differences. No key, sound or layout code was executed.

## Dispatcher consumes result2 and normalizes it to0

The audit now retains complete paired dispatcher bodies **original`0044a2d0..0044a439`**, **Modern`0044a2d0..0044a436`**, ends exclusive. This pass establishes its local callback/result contract; it does not claim all dispatcher changes have been semantically explained.

The selected-item path derives a construction-record pointer from the signed menu WORDs+`0x18` and+`0x1a`, using stride`0xbc` and base`00604ee0`. It tests callback slot+`0x30`, then calls through it with **EAX=item record, EDX=menu pointer, EBX=sign-extended input key WORD**. Original’s call is at`0044a36a`, Modern’s at`0044a35d`. This connects the registered cascade/droplist input callbacks to the construction-record storage directly; no additional widget-copy stage is required by this invocation path. Active asset admission and whether a particular item is selected remain runtime/state questions.

After that callback, both versions copy EAX result into EBX. **Any nonzero result skips generic key-navigation processing**, branching to`0044a428`. At that shared-address tail, both compare EBX with2 and replace2 with0 before returning it. Therefore result2 is locally **handled without generic navigation, then normalized to outward0**. It must not be described simply as callback failure because its externally returned value becomes0. Result0 instead permits the following generic navigation logic; other nonzero values pass through this normalization test unchanged. Earlier menu-level gates and other callback routes have their own admission conditions.

This gives the newly explicit cascade navigation result2 a concrete effect: its nonzero local result prevents the dispatcher’s generic arrow/key fallback before being normalized. The resulting outward0 alone would conceal that distinction from callback result0. It does not establish the next caller’s entire return-code interpretation or prove which inputs reach the changed navigation tail in a running game.

The dispatcher itself also changes register preservation. Original saves EBX/ECX/ESI/EDI/EBP and places its result in EAX before return. Modern begins **PUSHAD**, stores the result into saved-EAX slot`[ebp+0x1c]` at`0044a42f`, resets ESP, executes **POPAD**, then RET. Thus Modern restores saved general registers while replacing EAX with the result; flags and x87 state are not saved by PUSHAD/POPAD. The Modern prologue sign-extends incoming DX into ESI; no standard ABI or full arbitrary-upper-register equivalence is inferred from this local contract.

These observations narrow the remaining work to upstream selection/admission, other changed dispatcher branches and its external caller semantics. They do not require unrelated race/network dispatcher recovery. No dispatcher, input callback or key event was executed.
