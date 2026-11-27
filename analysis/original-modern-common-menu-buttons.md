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

## Reference-source identity follow-up

The [reference asset audit](original-modern-reference-assets-index.md#property-changes-and-reference-identity) now verifies all80 local uppercase backup menus against the author-hosted reference bundle, and crosschecks both hashes of all52 pairs in the retained visible-count manifest. The earlier authored-field findings therefore have an identified second source for their backup bytes. This is an identity/provenance improvement, not authentication of pristine retail, a rerun of the binary audit or runtime asset selection.

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

The same `widescreen` binding/count therefore appears in a different menu (backup graphics versus Modern advanced graphics), and likewise `viewlevel` (backup advanced graphics versus Modern graphics). This supports authored redistribution without inventing a count increase for those two values. The release comparison below dates the authored relocation. Runtime widget equivalence remains open. The HUD names are not paired as simple renames without descriptor/consumer evidence.

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

The pre-existing [menu-input comparison](original-modern-menu-input.md) already explains Tab/Shift-Tab, named arrows and multiplayer-interceptor bypass; reuse that evidence rather than treating these as newly discovered dispatcher features. Its [complete packaged named-arrow inventory](original-modern-menu-input.md#complete-packaged-menu-named-arrow-inventory) now bounds the authored tokens across all52 official menus and uppercase backup counterparts.

## Numeric field parsing: digit-only validation and wrapping conversion

The audit now retains complete paired integer wrapper **`00449130..00449166` (54 bytes)** and converter **`004f0430..004f0487` (87 bytes)**, asserting byte equality of both. It hashes the256-byte classification table at`00564ef0` and checks its bit`20h` for every nonzero input byte: exactly ASCII **`0..9`** are accepted under the `(byte+1) mod256` lookup used here. This is a file-backed classification snapshot; later table mutation/locale initialization has not been excluded.

The converter skips bit2-classified leading characters, recognizes an optional sign, and accumulates decimal digits using32-bit IMUL/ADD/SUB with wrapping arithmetic. It restores incoming EDX before return. The enclosing wrapper saved the original string pointer in EDX, so its subsequent scan starts from **the original input**, not a conversion end pointer. It returns0 if any original non-NUL byte lacks digit classification; otherwise it returns the converter’s result. Empty input returns the converter’s0. There is no separate success/error indicator.

Therefore, with the retained classification table, raw helper inputs`+9`, `-1`, ` 9`, `9 ` and`9x` all produce0, whereas digit-only text is accepted. This describes strings presented to this helper; upstream parser trimming or overrides can change which raw string reaches it. It is not a claim that leading spaces in a menu file necessarily survive parsing.

For accepted digit-only inputs the converter wraps modulo2^32, and the previously verified field writer stores only the low WORD. Consequently digit strings`65536` and`0` both store cap0; `65535` stores`ffffh`, interpreted as−1 by the later signed-WORD minimum. The verified initializer replaces a zero cap with2000, but leaves a nonzero`ffffh` value intact. These are static arithmetic consequences, not observed menu inputs or reachable defects. Original and Modern share the parser logic; their authored cap changes remain separate asset differences.

A C reconstruction must model unsigned wrapping/truncation explicitly if preserving this arbitrary-input contract. Substituting signed C overflow, saturating conversion, permissive whitespace/sign parsing or a range-checked error API would change original behaviour. That does not prevent a separately chosen validation layer, but it must not be silently attributed to either executable. No converter or parser instructions were executed.

## Outside-body cascade interval partition

The outside-function interval`00461cf4..004628d0` spans3036 bytes with207 changed positions. The inventory now partitions it into12 unchanged leading bytes, the1556-byte cascade renderer`00461d00..00462314`,396 unchanged intervening bytes, the1064-byte input comparison envelope`004624a0..004628c8`, and eight final Modern NOPs. The last input instruction is an unconditional jump at`004628c3` to the reused return/sound tail, so these final NOPs have no fallthrough from that path. Original’s same locations are the tail of alignment LEAs after its RET. Alternate-entry exclusion is not established.

The [outside-body manifest](evidence/audits/outside-function-differences.json) retains exact per-part changed-byte counts and hashes. The renderer and input mechanisms are already explained in their paired audits; unchanged intervening bytes include the retained initializer and must not be labelled all padding. This closes interval routing, not full UI or external-helper validation.

## Location and Opponents dropdown priority changes in150

**Verified authored priority boundary and selected code consumers; visible overlap fix untested.** The [priority-history audit](evidence/audits/dropdown-priority-history.json), reproduced with `python3 analysis/scripts/audit_dropdown_priority_history.py`, pins author-reference,1.4.0,1.5.0 and final archives and parses repeated droplist/cascade sections in`location.mnu` and`opponent.mnu`.

| Control/listname | Reference and1.4.0 priority |1.5.0 and final priority |
|---|---|---|
|Location top dropdown `tracks` |1 |0 |
|Location lower `laps`, `direction`, `mirrored`, `night`, `weather` |0,1,2,3,4 |1,2,3,4,5 |
|Opponents top dropdown `opcars` |1 |0 |
|Opponents lower `ai`, `oppnumber`, `traffic` |1,2,3 |1,2,3 |

The selected top controls keep x101/y69 and authored maxvisitem15 (tracks) or10 (opcars) in all four snapshots. This is a priority change, not an increased visible-item capacity. Other properties are separate: opponent cascade`ypos` values also change1/2/3→2/3/4 in the historical pair; these are not literal pixel y positions and are not used here to infer keyboard behaviour.

The original/final descriptor at`00557c30` is the common kind1 `priority` property with form1 and destination`00604eea`, entry base`00604ee0`+0a. The [existing property-writer evidence](original-modern-control-component-keys.md#common-property-stores-do-not-directly-overlap-either-byte) establishes form1's two-byte write. The new audit checks the paired descriptor directly and retains four identical draw-loop spans:

- `0044a524..0044a536` updates the maximum signed priority using an arithmetic shift of the DWORD at entry+08, whose high WORD is priority+0a.
- `0044a59c..0044a5a6` compares that signed priority with the current group and skips nonmatching entries.
- `0044a5cb..0044a5e5` checks callback+2c, suppresses it when byte+05 bit10h is set, otherwise invokes it.
- `0044a634..0044a63a` decrements the group and returns to the nonnegative-group loop test.

Thus, within this ordinary group traversal, priority0 callbacks are visited after positive groups. Modern moves the two top dropdowns into that final group, separating them from the old priority1 ties and Location's old priority0 laps control. This supplies a concrete ordering mechanism consistent with MP150-024. Actual compositing still depends on callbacks, flags, render/depth state and providers; later callback order alone does not prove every popup appears correctly over other content.

The state-preparation span`0044a5a6..0044a5cb` differs and is explicitly outside the retained comparisons; the later [selection-state audit](#callback-selection-gains-a-none-check-and-narrower-sum-in140) now explains that separate change. This is not complete loop equivalence or a claim that its changed instructions implement the asset priority fix. Historical EXE consumers were not separately qualified; the1.4.0→1.5.0 boundary is directly verified for the authored assets. The reference assets are author-hosted, not authenticated retail or proven paired to the supplied original EXE. MP150-024 advances to **partial package/static support**; active installed loading, visible overlap and full input behaviour remain unverified. No game, instruction probe, compiler or Ghidra write was used.

## Showcase and Compare subtitles adopt the Race Results text style

**Verified package boundary and named property bindings; actual font-bank/rendering identity untested.** The [subtitle-style audit](evidence/audits/subtitle-style-history.json), reproduced with `python3 analysis/scripts/audit_subtitle_style_history.py`, pins author-reference,1.4.0,1.5.0 and final archives. It compares selected controls in`showcase.mnu`, `compare2.mnu` and`postgame.mnu`.

| Menu/list binding | Reference and1.4.0 |1.5.0 and final |
|---|---|---|
|Showcase `statsmode` |Cascade`notitle=0`; no list-bound text subtitle |Cascade`notitle=1`; added list-bound `[text]` subtitle |
|Compare All Cars `compcat` |Same old pattern |Same replacement pattern |
|Race Results `posttitle` |Existing `[text]` subtitle |Retained matching authored style |

Both new subtitle records match the results subtitle in **nine explicit style/layout properties**: x163, y113, priority4, texttype1, color2, italic0, scale0.750000, ypos0, align0. This is not replacement of the main page headings at x101/y17. The new records use token`kMenuSHOWCASEStats001`; the results record uses`kMenuPOSTGAMEracesumm001`. List bindings remain purpose-specific (`statsmode`, `compcat`, `posttitle`), so matching style is not evidence of identical text content or selected values. Other button/cascade navigation metadata is separate.

| Named property descriptor | Kind/form | Runtime entry offset | Paired EXE result |
|---|---|---|---|
|`00557cc0` texttype |3/1 |+40 |Identical |
|`00557ce0` color |3/1 |+4a |Identical |
|`00557cf0` italic |3/1 |+42 |Identical |
|`00557d00` scale |3/6 |+4c |Identical |
|`00557db0` cascade notitle |17/1 |+44 |Identical |

These offsets use runtime entry base`00604ee0`; field descriptors retain concrete destination pointers and exact bytes in the audit. The [common writer review](original-modern-control-component-keys.md#common-property-stores-do-not-directly-overlap-either-byte) establishes form1's two-byte store. The current audit does not qualify the complete form6 conversion path, every scale override, cascade title-rendering consumer or actual font-bank selector. It verifies authored values and bindings, rather than claiming those runtime behaviours were exercised.

MP150-025 advances to **partial package/static support**: at the claimed1.4.0→1.5.0 boundary, both pages replace the old cascade-title policy with explicitly authored subtitles that share the Race Results style. Full font-face/glyph-bank identity, localization, visible size/appearance and active installed asset loading remain unverified. The author-reference package is not authenticated retail or independently paired to the supplied original EXE. Reconstruction should preserve separate text records, their list bindings and the chosen cascade title policy; merely changing a global font would not reproduce the observed asset transformation. No target, menu, instruction probe, compiler or Ghidra write was used.

## Callback selection gains a none check and narrower sum in140

**Verified complete code-envelope comparison and historical boundary; live UI effect untested.** The [selection-history audit](evidence/audits/menu-callback-selection-history.json), reproduced with `python3 analysis/scripts/audit_menu_callback_selection_history.py`, compares supplied original, author-hosted1.3.1/1.4.0 and official final EXEs. It resolves the state-preparation difference explicitly excluded from the earlier priority-group comparison.

Complete callback-loop envelope`0044a4f0..0044a65b` is363 bytes. Original equals1.3.1 throughout;1.4.0 equals final throughout. All37 original/final differing bytes lie at`0044a5a6..0044a5cb`. This includes five final NOPs at`0044a5c6..0044a5cb`, excluded from the saved split function ranges; the envelope comparison accounts for them rather than treating a function-range gap as missing semantics.

Let **S** be signed WORD at menu+18, **R** signed WORD at menu+1a, and **I** the signed current entry index at this loop branch. These raw offsets avoid assuming every caller constructs valid menu state.

| Original selection preparation | Modern selection preparation |
|---|---|
|Load DWORDs at+16/+18; SAR16 extracts S/R; add them in32 bits; flag=`I == S+R` |Load R into AX; if R=100 flag0; otherwise ADD AX,WORD+18, sign-extend resulting16-bit sum and compare with I |

The operands are each signed16, so original's sum is within signed32 range. Modern wraps the sum modulo65536 before sign extension. It also explicitly suppresses the selected flag for R=100, regardless of the current index. The retained tail at`0044a5cb..0044a5df` requires nonnull entry+2c and clear byte+05 bit10h, then CWDE/MOV copies the computed0/1 into EDX, places the entry pointer in EAX and calls`[entry+2c]`. This is a callback argument contract, not a claim that every callback renders selection identically.

| Derived scalar inputs (S,R,I) | Original flag | Modern flag | Meaning |
|---|---:|---:|---|
|5,2,7 |1 |1 |Ordinary selected entry |
|5,2,8 |0 |0 |Ordinary other entry |
|5,100,105 |1 |0 |Explicit none check changes result |
|32760,10,−32766 |0 |1 |16-bit sum wrap changes comparison |
|−32760,−10,32766 |0 |1 |Negative sum wrap changes comparison |

These rows are **derived scalar arithmetic**, not original-instruction probes, live menu observations or evidence that extreme/negative indices identify valid records. The audit implements signed16 interpretation explicitly; a maintained C translation must preserve the selected baseline's width and sentinel policy instead of silently replacing it with unbounded addition or relying on implementation-defined narrowing.

The complete41-byte selected-entry query`0044a440..0044a469` is identical across all four EXEs. It already checks R=100 and returns−1; otherwise it retains32-bit addition of sign-extended S/R. Modern therefore aligns the callback loop with that query's **none policy**, but not with its arithmetic under16-bit sum overflow. Whether overflow inputs are reachable remains unresolved. Neither the historical equality nor scalar cases establish whole flags/register/local-stack equivalence or complete event/render behaviour.

This is an independently explained EXE change at1.3.1→1.4.0. It is not assigned to MP150-024's later authored dropdown-priority fix or forced into a vaguely worded vendor bullet. Callback consumers, producers of the100 sentinel, live selection and actual UI outcomes remain follow-ups. No target, instruction probe, menu, compiler or Ghidra write was used.


## Shared list bounds change padding and special-width admission in140

**MP140-026: partial static support; visible alignment of every list untested.** The [bounds audit](evidence/audits/dropdown-padding-history.json), reproduced with `python3 analysis/scripts/audit_dropdown_padding_history.py`, pins131/140 archives/EXEs and compares complete declared envelopes `004628d0..004629bf` (239 bytes) and `00464560..004646db` (379 bytes). All48/28 differing bytes respectively lie in the captured predicate-selection regions or four changed arithmetic immediates.

| Arithmetic site |131 |140 |Output |
|---|---:|---:|---|
|`00462971`, `004645ea` |Add5 |Add15 |Width-like WORD at entry+1Eh after adding measured extent and selected allowance |
|`0046297f`, `004645f8` |Add5 |Add2 |Height-like WORD at entry+20h after row field shifted left4 |

The width allowance also changes.131's first routine selects35 for names tracks/rectrk regardless of R=`006fd3b8`; the second selects35 for every R=3 case, otherwise15.140 replaces both decisions with shared helper `00472924..00472959`: allowance35 only when **R=3 AND name matches tracks or rectrk**, otherwise15. This is a second mechanism distinct from the5→15 padding term.

Under equal ordinary measured widths, the shared normal allowance15 produces an additive total20→30; retained special allowance35 produces40→50. Where140 removes a former special allowance, the total changes40→30 instead. Height's fixed term decreases by3. These are derived arithmetic effects, not observed pixel dimensions; row fields differ between the two controls (+56h versus+5Ah), and their other geometry/placement consumers remain separate.

Both paths ultimately store WORD results. Preserve low16-bit/truncation and x86 shift behaviour for exceptional inputs; do not translate the ordinary formulas into unconstrained signed C arithmetic or infer bounds safety. Complete byte accounting for these two routines does not prove every dropdown calls them, loaded label metrics are valid, or all on-screen padding is corrected. MP140-026 advances vendor-only→partial. No menu, target instructions, compiler or Ghidra write was used.


## Four named dialogs have authored layout edits in140

**MP140-028: partial package evidence; final visual alignment untested.** The [dialog audit](evidence/audits/dialog-alignment-history.json), reproduced with `python3 analysis/scripts/audit_dialog_alignment_history.py`, pins131/140 archives and all eight menu members. Nine controls are matched by exact section and unique symbolic text/codelink, or by the single InteriorBx section, rather than assuming section order survives added controls.

| Menu/control |131 authored position |140 authored position |
|---|---|---|
|Predefined Keys: Escape label |42,138 |35,173 |
|Predefined Keys: Tab label |35,173 |32,208 |
|Predefined Keys: Keypad Plus label |32,208 |31,243 |
|Predefined Keys: Keypad Minus label |31,243 |34,278 |
|Interior view box |y187 |y147 |
|Interior ZoomSlider |227,400 |222,360 |
|IPX gamelist |230,180 |250,158 |
|Load DESCRIPTION_BOX |400,176 |395,205 |
|Load replays list |185,176 |183,158 |

The Load list additionally changes authored `maxvis=8` to10. These are selected fields from `hardkeys.mnu`, `interior.mnu`, `ipx.mnu` and `loadsave.mnu`; other additions/removals and keyboard-label changes are not presented as alignment effects. The shared bounds arithmetic documented immediately above is a separate EXE mechanism and must not absorb these authored coordinate changes.

This supplies concrete package changes corresponding to the four named dialogs. It does not prove final pixels, successful control/resource loading, text metrics in every language or actual input behaviour. MP140-028 advances vendor-only→partial. The manifest retains selected geometry and all member hashes without duplicating full assets. No game, target instructions, compiler or Ghidra writes were used.

## Controller and Connect tab layout changes at130

The [historical asset audit](evidence/audits/controller-connect-layout-history.json), reproduced with `python3 analysis/scripts/audit_controller_connect_layout_history.py`, pins120/130 archives and `control1.mnu`, `connect.mnu`, `pscntl1.mnu` members. It also reads131/140 Controller definitions to distinguish the later reset movement. Existing menu parsing is reused; no UI is opened.

|Controller entry |120 `ypos` |130 `ypos` |
|---|---:|---:|
|Dead Zone |2 |1 |
|Force Feedback |3 |2 |
|Audio Feedback |4 |3 |
|Function Keys |5 |4 |
|Predefined |6 |5 |
|Reset to Defaults |7 |6 |

Each entry is matched by its symbolic text token. Selected text, callback/menu binding, button type, x/y and align fields remain equal. These are tab-position metadata changes, not six one-pixel movements. Done/Cancel controls retain position0. `pscntl1.mnu`, the separate split-screen Controller definition, has identical parsed records after removing the two demo-admission fields; the selected restructuring must not be generalized to that menu.

|Connect binding |120 `ypos` |130 `ypos` |120 authored x/y |
|---|---:|---:|---|
|racenet |1 |5 |5/173 |
|ipx |2 |2 |2/208 |
|tcp |3 |1 |1/243 |
|modem |4 |3 |4/278 |
|serial |5 |4 |9/313 |

The130 Connect definitions omit those explicit x/y fields and retain `buttontype=tab` with the positions above. Text tokens, protocol callback names and next-menu values stay associated with each named entry. Omission does not independently establish parser defaults or actual aligned pixels. Both files also remove legacy demo fields; this audit does not assign runtime effects to that cleanup or prove executable protocol equivalence.

**MP130-006 advances vendor-only→partial:** the historical assets substantiate Controller position normalization and Connect tab-order/coordinate-policy changes. Their actual rendering, loaded-resource selection and consistency with every other menu remain unverified. This complements the [Connect dispatch crosswalk](connect-menu-dispatch-crosswalk.md), rather than replacing its separate executable evidence.

### Reset moves6 to7 at131 to140, distinct from final8

The same audit verifies Reset `ypos` history **120=7,130=6,131=6,140=7**. Thus the advertised one-position downward movement in MP140-027 has a direct131→140 asset counterpart, in addition to the earlier backup7→final8 observation above. Those endpoints represent different comparisons and must not be conflated. The final8 value does not date all later layout changes to140. Complete intermediate introduction of position8, active menu defaults and rendered coordinates remain unverified. MP140-027 remains partial, with its historical boundary now supported.

No menu interaction, settings reset, target instructions or Ghidra changes occurred. Executable and database bytes are unchanged.


## Graphics controls move in Modern 1.3.0

The retained `fedata/menus/graphics.mnu` and `advgrph.mnu` directly
show the menu changes described by MP130-005. The line numbers below
identify both authored occurrences of each binding.

| Binding | 1.2.0 | 1.3.0 |
|---|---|---|
| `widescreen` | Graphics 51, 72, immediately after the Resolution group | Advanced Graphics 54, 62, immediately after the View Angle group |
| `viewlevel` | Advanced Graphics 14, 34 | Graphics 93, 100 |
| `viewangle` | Advanced Graphics 91, 111 | Advanced Graphics 39, 46 |
| `nextmenu=advgrph` | Graphics 274 | Graphics 107 |

Extract each member with `7z x -so <archive> fedata/menus/<member>`
and search for `listname=` and `nextmenu=`. The exact member SHA-256
values are:

| Release | Graphics | Advanced Graphics |
|---|---|---|
| 1.2.0 | `51f742e65620d9d06b709270f1e425213701db35e54a48d1680facc0181284ab` | `c0baf1c660e78d72cf032e3df229f3a43087192f3310145eeaa99f07d108fc16` |
| 1.3.0 | `a35586b203f428881017792e1495a2b59b6fac92c7bcececd888be92a334fc61` | `b47c16694213257ca626dbeeab4d8e7679455aa18c48bba62aa920085725cb49` |

This establishes the packaged menu placement. How the menus render
and how the setting affects projection are separate questions.

The two controls kept their executable setting bindings across this
move. In 1.2.0, 1.3.0 and 1.3.1, both 20-byte descriptors below
match byte for byte. Their name strings and zero-terminated choice
lists also match.

| Menu key | Descriptor VA | Name VA | Choice list VA and WORDs | Setting destination |
|---|---|---|---|---|
| `viewlevel` | `00556730` | `00537fc8` | `00556252`: 184, 183, 182, 181, 0 | `006fbc28` |
| `widescreen` | `005567a8` | `00538008` | `005561be`: 229, 228, 0 | `006fbc4c` |

To reproduce, read each descriptor as five little-endian DWORDs
from the executable's PE RVA, resolve its first two pointers, and
read the WORDs through the first zero. The third and fourth DWORDs
are zero in both records. The [View Distance analysis](original-modern-parameter-preset.md#user-facing-binding-view-distance-and-the-full-preset)
and [Frame Size analysis](original-modern-frame-setting.md) trace
the corresponding settings into their consumers. Descriptor equality
establishes continuity of setting storage and choice IDs across the
move. It leaves layout, localization and projection effects open.

The two inspected consumers also retain identical instruction bytes
in 1.2.0, 1.3.0 and 1.3.1. The viewport constructor tests
`006fbc4c` at `004be625`. The distance preset routine reads
`006fbc28` at `0041d62a`.

| PE VA range, end exclusive | SHA-256 in all three builds |
|---|---|
| `004be5e0..004be872` | `721c9740440a2f6393ca2b03c72662d3c3ff19b0f69781960fdce902d52178f5` |
| `0041d620..0041d6c6` | `b85a0bb88eda14d18a2d363d98dea59fc4b551663f65ce0c61c0e0d3d7d3418a` |

Extract each archived EXE and hash the bytes at the corresponding
PE RVAs through the terminating RET. This establishes that the menu
move left these two instruction ranges intact. Inputs, tables and
callees can still differ, so overall rendering equivalence is open.

The View Distance routine's static inputs match across those builds
as well. At `0041d625..0041d649` it selects one of four 64-byte preset
blocks at `0041d6c8`, then adds 0 or 32 bytes and 0 or 16 bytes
according to the two race flags. Each selected row supplies eight
WORDs for two records. The complete 256-byte table has SHA-256
`ea9fba78c204613874515b7f5861cf361d90bda5b7e8aad03822249e2713c2a9`
in 1.2.0, 1.3.0 and 1.3.1. The eight-byte conversion constant
at `00536ce4` also matches and decodes to exactly 1/65536.
Reproduce by reading those two PE ranges from each archive.
This covers the static preset inputs for all valid ordinals.
The record count, pre-existing record fields and downstream
rendering remain outside this comparison.

### Hosted original menu baseline

The hosted original archive `upstream/history/nfs3_orig.7z`
(SHA-256 `374b30edda891569327091e14828a3df04ac9350f73ba0f190ce4d3c54b6f127`)
contains both uppercase members. Each matches its local backup
byte for byte:

| Archive member | SHA-256 |
|---|---|
| `fedata/MENUS/GRAPHICS.MNU` | `d8af15a148fff2ec865c9ce6337e095bb340bb7f863419cfba245fb2574c6722` |
| `fedata/MENUS/ADVGRPH.MNU` | `5900f10ec59b68b9fed049ae08cc4bb112d90322bcc91826c3313d5f7f278f4d` |

The hosted members place both `widescreen` bindings at Graphics
lines 51 and 72 and both `viewlevel` bindings at Advanced Graphics
lines 14 and 34, matching the placement in Modern 1.2.0. The
Graphics link to Advanced Graphics is also present at line 274.
This establishes the baseline against the hosted original package
for these two menus. Retail disc provenance and other backup
members remain outside this check.

A case-sensitive inventory extends this provenance check to the
whole hosted menu set. All 80 `fedata/MENUS/*.MNU` archive members
match their exact uppercase filenames under the local
`fedata_org/menus` directory byte for byte. The local directory
has three additional uppercase menus without hosted counterparts
(`MATTMNU.MNU`, `RACETYPE.MNU`, `SUB.MNU`) and 52 lowercase
`.mnu` files, which were excluded from this comparison. Case
matters here because uppercase and lowercase files can coexist
with different contents. To reproduce, list exact member paths
with `7z l -slt`, extract each uppercase member with `7z x -so`
and compare to the exact local basename. This ties the 80 matching
files to the hosted artifact. Retail disc provenance and the
selection of active files at runtime remain open.

### Official 1.6.1 menu archive coverage

Pairing by case-insensitive basename across the two archives yields
52 shared menus, all with different contents. The official 1.6.1
archive has no menu basename absent from the hosted original, and
28 hosted originals have no counterpart in the patch archive.
Those 28 are `ad`, `aituner`, `ced01dbg`, `ced02dbg`, `ced03dbg`,
`ced04dbg`, `ced05dbg`, `ced06dbg`, `ced07dbg`, `ced2bdbg`,
`ced2cdbg`, `ced2ddbg`, `ced3bdbg`, `ced3cdbg`, `ced3ddbg`,
`ced4bdbg`, `ced4cdbg`, `cedmain`, `instcar`, `makecsv`,
`mspause`, `msquitto`, `perdata`, `pshudpos`, `psoption`,
`psoptn2`, `pstats` and `quitto` (all `.mnu`).

To reproduce, list the `fedata/menus` members of both archives with
`7z l -slt`, pair unique basenames ignoring case and compare extracted
bytes using each member's exact stored path. This supplies a hosted
original counterpart for all 52 pairs in the visible-count audit.
Archive omission leaves installation retention and executable
reachability unresolved.

Across all twelve retained Modern Patch archives, the 28 omitted
basenames are already absent in 1.0.0. That first archive ships
51 of the final 52 files and omits `cedbasic.mnu` as well.
The hosted original includes `CEDBASIC.MNU`. Version 1.1.0
adds the patch copy at `fedata/menus/cedbasic.mnu`, and all
retained builds through 1.6.1 ship the same 52 basenames.
This dates the change in the archive member list. Individual
file contents and the installed menu selected by the executable
are separate questions.

The car tuning menu first included in 1.1.0 is a byte-for-byte
copy of the hosted original `CEDBASIC.MNU`. Both 1.1.0 and
1.2.0 have the same 7,908 bytes, with SHA-256
`4f11c887f984597786af7ea723413320ccc580873f898e32b0457854644d58b6`.
The first content change in the retained patch archives is 1.3.0.

| Patch releases | Menu bytes | SHA-256 prefix |
|---|---:|---|
| 1.1.0–1.2.0 | 7908 | `4f11c887f9845977` |
| 1.3.0–1.3.1 | 6788 | `36cca1de10c9c36a` |
| 1.4.0 | 5642 | `38b6e81c7c7b9117` |
| 1.5.0–1.6.1 | 5467 | `3e78623958fe48c6` |

Extract the uppercase member from the hosted original and
the lowercase member from each patch to reproduce. These are
content boundaries for the asset. The [slider analysis](original-modern-slider-percentage.md)
covers selected tuning controls separately.

Normalizing line endings, trimming each line and dropping blank
lines isolates the first edit to 60 deleted lines in 1.3.0.
These are 29 occurrences each of `EnableForDemo=0` and
`EnableForE3Demo=0`, plus two commented `;nextmenu=car1` lines.
Removing those lines from the normalized 1.2.0 member produces
the exact normalized 1.3.0 sequence. The seven tuning controls
keep their authored bindings and fields at this boundary.
The runtime defaults for omitted demo flags remain unverified.

The normalized 1.3.0 → 1.4.0 diff drops explicit zero fields,
including `postonly`, `mainonly`, `borderColor` and selected
navigation fields. The 1.4.0 → 1.5.0 diff changes the authored
car-tuning controls and navigation:

| Field | 1.4.0 | 1.5.0 |
|---|---|---|
| Advanced button `CEB_GOTOADVANCED` | Links to `cedmain` | Button and link absent from this menu |
| All seven tuning sliders | `percenttype=1`, `ypos=0..6` | `percenttype=2`, `ypos=1..7` |
| Slider type | `slidertype=0` | `slidertype=0` |

The title moves to the start of the definition and several background
image coordinates change. The [slider analysis](original-modern-slider-percentage.md)
covers how the executable interprets the percentage field. Removing
this authored link leaves any other route to `cedmain` open.

A scan for active `nextmenu=cedmain` fields across every packaged
menu identifies nine matches in the hosted original: seven
`ced01dbg.mnu` through `ced07dbg.mnu` return links, the Advanced
button in `cedbasic.mnu`, and the pause-menu Car Tuning button
(`PSE_LAUNCHCAREDIT`). Modern 1.0.0 ships only the pause link.
Versions 1.1.0–1.4.0 ship both the pause and Advanced links.
No exact active field targeting `cedmain` occurs in the retained
1.5.0–1.6.1 menu archives. In 1.4.0 the two links occur at line 17
of `cedbasic.mnu` and line 147 of `pause.mnu`.

To reproduce, extract each packaged `fedata/menus/*.mnu` member
using its stored path and match whole lines against
`^\s*nextmenu\s*=\s*cedmain\s*$` case-insensitively. This establishes
the removal of both shipped navigation links in 1.5.0. It leaves
direct executable routes and menus retained by an existing
installation unverified.

The executable still looks up both control names after the
packaged links disappear. The hosted original and all twelve
Modern releases have identical instruction bytes in these
two ranges (end exclusive):

| Control | String VA | Code range |
|---|---|---|
| `CEB_GOTOADVANCED` | `00537184` | `0042838c..004283a7` |
| `PSE_LAUNCHCAREDIT` | `005392e0` | `0044cdff..0044ce14` |

The first range passes the string through `00427c20` before
calling `00442a40`. The second passes its name to `00442a40`
directly. In each range a zero result skips the write, while a
nonzero result sets bit `0x10` in the returned object's byte at
offset 5. These are lookup and flag-update sites. They contain
no direct transfer to a tuning screen. A bounded search of the
hosted original and Modern 1.4.0, 1.5.0 and 1.6.1 executable bytes
also finds no NUL-terminated `cedmain` string, ignoring case.
That search leaves computed names and external asset routes open.
