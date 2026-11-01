# HUD settings: single/split policy replaces race-specific branches

## Identity and complete delta

The [static audit](scripts/audit_hud_settings_policy.py) verifies the shared `hud` callback registration at `00555ea0`: both files bind initializer `0045e960` and retain the other two callback addresses in that row. Complete initializer envelope `0045e960..0045f07c` is **1,820 bytes**. All **242 differing bytes** lie in `0045e980..0045ea74`; the earlier prefix and later body are byte-identical. The [manifest](evidence/audits/hud-settings-policy.json) retains executable/span hashes, registration bytes, strings, list WORDs and full disassembly paths.

Neither saved function inventory recognizes this whole initializer, so these differences appear in the [outside-function interval](original-modern-outside-function-index.md) `0045e95a..0045f300`. That gap is not just padding and must not be treated as a single function boundary. No game, menu or instruction probe was run.

## Local Credits gate delegates to shared policy

Original uses token `credits` at `0053a844`: if lookup `00442a40` finds it and signed session DWORD `006fd3b0 > 1`, it ORs byte bit 0 into entry `+4`. Modern calls shared helper `00437614` with the saved incoming menu/context pointer instead. The [shared-policy report](original-modern-race-now.md) maps that helper; its contract must not be replaced with an assumed identical local Credits check.

Repacking also moves the nearby settings-snapshot copy sequence five bytes earlier within the changed region. The copied source/destination and surrounding unchanged prefix remain in the complete captures. Differences in byte positions there are not an additional independently established snapshot-format change.

## Original four-way selection versus Modern two-way selection

Use raw inputs **P=`006fd3b0`** and **R=`006fd3b8`** rather than assuming every numeric value's gameplay label. The following table describes direct writes and lookup/flag operations in this selection block, not final rendered visibility or all later writes.

| Original condition | Entries whose BYTE `+5` gets OR `10h` if found | Direct list-pointer write to `006788b8` |
|---|---|---|
| P=1, R=3 | `singlePlayerDefaults`, `splitScreenDefaults` | `005562c8` |
| P=1, R≠3 | `singlePlayerDefaults`, `hotSplitScreenDefaults` | `005562d2` |
| P≠1, R=3 | `splitScreenDefaults`, `hotSplitScreenDefaults` | `005562c2` |
| P≠1, R≠3 | `splitScreenDefaults`, `hotSplitScreenDefaults`, `singlePlayerDefaults` | No direct pointer write on this block's path |

The last row is deliberately not described as a new null/empty list: the block does not clear the pointer before those branches. Earlier initialization and later consumers determine the effective value. Do not invent a deterministic replacement value for an unstored original field.

Modern's complete replacement uses only P:

| Modern condition | Entry whose BYTE `+5` gets OR `10h` if found | Direct list-pointer write to `006788b8` |
|---|---|---|
| P=1 | `forsingle` | `005562c8` |
| P≠1 | `forsplit` | `005562c2` |

Modern always writes a list pointer on these two paths and then sets EDX=0 before joining the unchanged initialization loop at `0045ea79`. It no longer tests R in this policy block. Bytes `0045e9e8..0045ea74` become 140 NOPs. This establishes consolidation of the local race-specific policy, not elimination of every race-mode distinction in the whole HUD system.

## File-backed lists and widget bindings

| List address | Original WORDs | Modern WORDs |
|---|---|---|
| `005562c2` | `019d,019e,0000` | Same |
| `005562c8` | `01a0,01a1,01a3,01a4,0000` | Same |
| `005562d2` | `01a0,01a3,0000` | `0000,0000,0000` |

The first two arrays are retained; the third original array is zeroed and is no longer directly selected by the inspected Modern block. These are verified list WORDs, not independently identified localized labels. Zeroing does not prove no other code references that storage.

The [common-menu control inventory](original-modern-common-menu-buttons.md#long-list-authored-visible-counts) separately records official `hud.mnu` droplist list names `hudtypesingle` and `hudtypesplit`, each with authored `maxvisitem=15`. The new `forsingle`/`forsplit` codelink lookup tokens and those list names are distinct identifiers; their similar names alone do not establish a one-to-one item binding or flag semantics. The follow-up below verifies the asset grouping and one callback-suppression consumer; complete rendered visibility remains untested.

**Bounded status: done for complete initializer delta and selected data arrays. Confidence: verified static.** The follow-up below resolves the direct asset grouping and selected flag consumer. Remaining scope includes alternate dispatch/visibility paths, lifecycle/initial value of `006788b8`, localization and runtime selection. The unchanged later code may still contain its own session/mode logic. No executable bytes, Ghidra state, raw exports or maintained C were changed.

## Asset and flag follow-up: the two list groups are now directly bound

The expanded audit verifies official `fedata/menus/hud.mnu` byte-for-byte against its member in the hash-pinned Modern archive. It parses the authored droplist sections and follows their exact names into executable data:

| Official item `codelink` | `listname` | List descriptor | Descriptor's list pointer | Shared selection cell |
|---|---|---|---|---|
| `forsingle` | `hudtypesingle` | `005567bc` | `005562c2` | `00678900` |
| `forsplit` | `hudtypesplit` | `00556938` | `005562c8` | `00678900` |

Both authored items use x101, y69, priority0 and maxvisitem15. The identical authored position is consistent with mutually gated alternatives, but the asset alone does not prove exclusive rendering. The two descriptor records are verified five-DWORD values, so the list bindings are now established beyond similarly named strings.

For provenance comparison, the local uppercase backup `fedata_org/menus/HUD.MNU` contains three droplists: `singlePlayerDefaults → buyERTS`, `splitScreenDefaults → buyERTS_at75`, and `hotSplitScreenDefaults → buyERTS_at100`. Their codelinks agree with the original executable's inspected lookups. This is corroboration from a **local unauthenticated backup**, not proof that this file shipped with the supplied original executable. The adjacent lowercase `hud.mnu` backup is byte-identical to the official Modern asset; its directory name must not cause it to be labelled original. Hashes and parsed fields for all three files are retained in the manifest.

The paired executable consumer `0044a5cb..0044a5e5` is byte-identical in both versions. It first requires nonnull entry DWORD `+0x2c`, then tests BYTE `+5` mask `10h`; a set bit skips that callback dispatch. Otherwise it calls `[entry+0x2c]` with entry in EAX and sign-extended AX-derived value in EDX. This establishes the bit's effect on this callback route. It does not prove the callback is the entry's only draw path, nor that this bit independently excludes every input route; navigation bit0 is a separate consumer contract.

**Follow-up status: done for official asset grouping, descriptor/list binding and this flag consumer; confidence: verified static.** Runtime lifecycle, complete input/render dispatch and localized list content remain explicit unknowns. No menu or target code was executed, and no backup file was changed.

## Outside-body interval closure

The outside-function inventory now independently checks the entire2470-byte interval `0045e95a..0045f300`: six leading bytes precede the1820-byte initializer, and644 trailing bytes follow it. Both surrounding spans are byte-identical across the pinned EXEs. **All242 interval differences** are confined to the already documented initializer policy block`0045e980..0045ea74`. Per-part hashes and changed-byte counts are retained in the [outside-body manifest](evidence/audits/outside-function-differences.json).

This closes localization of the interval’s byte differences to the researched policy; it does not identify the unchanged surrounding bytes as padding or certify every callee, callback, language or runtime outcome. No Ghidra boundary edits were made.

## Police Cone Stats and Tutorial Icon: claim remains unresolved

**Historical checkpoint:** the later [role-specific asset comparison](#police-only-widget-omission-is-authored-in-the-role-specific-menus) now establishes partial package/static support. The unresolved assessment below records the earlier code-only review.

**Evidence confidence: verified checked boundaries and preset contents; unresolved hiding mechanism. Work status: pending for MP100-048.** The new [bounded role audit](scripts/audit_hud_editor_role_boundary.py) and [manifest](evidence/audits/hud-editor-role-boundary.json) record what the nearby code/assets do establish. This is not acceptance of the release claim, and no HUD editor or target code was executed.

| Checked boundary | Result | What it does not establish |
|---|---|---|
| `pshud` callback row`00555db0` and complete initializer`0044d4c0..0044d669`,425 bytes | Registration and initializer are identical in supplied original/final | No new police-only hiding change identified in that initializer |
| `HudItem` registration`00557bd8` and128-byte template at`00557928` | Same class ID32/template and method bindings | No proof every dynamically constructed editor item uses this route |
| Complete rectangle loader`0045ca90..0045cb46`,182 bytes | Identical; maps item values below/above23 to view/slot, selects a profile using vehicle role bit20h, copies rectangle and geometry fields | No local special-case test of slots6/7 or new hide-flag write |
| Registered helper`0045cb50..0045cb55` | Same5-byte balanced-frame no-op | Not a visibility filter |

The previously explained242-byte delta in general HUD settings initializer`0045e960` concerns shared policy and single/split list selection. That difference is not, by itself, evidence of hiding these two widgets for police players. Do not relabel it to match a release-note phrase without a concrete item/role chain.

### Named records do not support a zero-rectangle explanation

The hash-pinned author-reference `EDEF.POS` orders Tutorial Icon and Cone Stats at zero-based slots **6 and7** in each23-record profile. All six profiles’ named records, including Cop-prefixed names, have nonzero coordinate tuples. The audited final embedded table also has nonzero16-byte records at those two slots in all six profiles. Raw table pairs are retained in the manifest; they are not presented as final pixel coordinates. This rules out the simple explanation that the inspected final defaults hide these widgets merely by replacing their stored rectangles with all zeros. It does not prove visible rendering or rule out other flags, overwritten layout data or admission conditions.

Author-reference `PSHUDPOS.MNU` authors17 `HudItem` records covering item values0..16, including6/7. The rectangle loader’s low-ID mapping connects these to the named slot order under its ordinary profile assumptions. This menu is omitted from the final patch archive, as the [existing complete asset inventory](original-modern-reference-assets-index.md) records. **Omission does not prove deletion from an installed base game**, or prove which editor route is active. The author-reference asset is not authenticated pristine retail or independently paired to the supplied original executable.

**Required next evidence:** identify the active editor item-list construction or retained asset actually used in final; follow slot6/7 and police-role variants through descriptor admission and subsequent draw/input flags. Then establish whether the original/final difference occurs in code, authored items or later state. Only after that linkage should MP100-048 advance beyond vendor-only status; visible acceptance and1.0.0 introduction remain separate. The checked method/template and nonzero-preset boundaries are retained to avoid repeating these routes as if unexplored.

## Registered editor draw chain retains both widget cases

**Verified static linkage and bounded negative comparison; MP100-048 remains unresolved.** The [draw-dispatch audit](evidence/audits/hud-editor-draw-dispatch.json), reproduced with `python3 analysis/scripts/audit_hud_editor_draw_dispatch.py`, follows the registered callback beyond the previously checked rectangle loader. It pins supplied original/official final hashes, the shared23-entry jump table and eight byte-identical code spans.

Template`00557928` at offset+2c binds`0045bcb0`. That104-byte callback optionally calls`0045a120` for nonzero incoming EDX, then unconditionally calls renderer`0045ab30` at`0045bcc3`. Only afterwards does it compute signed item%23, call classifier`0047bc20` and conditionally invoke`00459440` with one of two colours according to item+70. Thus this later classifier/outline path is not a newly added police-role filter before the main widget draw.

The renderer prefix selects view0 for signed item<23 or view1 otherwise, subtracting23 once on the latter path. It obtains the vehicle through`00422bd0`, chooses colour using item+70 and time state, bounds the slot unsigned against22 and dispatches through`0045aad0`. The table and249-byte prefix through the indirect jump are retained.

| Named slot from prior POS evidence | Retained jump target | Retained case behaviour | Comparison scope |
|---|---|---|---|
|6 Tutorial Icon |`0045b8d0` |Calls`00482030`; renderer-bit2 fallback sets state via`00431900`, calls`00482190`, then resets state |74-byte arm identical |
|7 Cone Stats |`0045b837` |Computes percentage from vehicle+2dc/+2e0, with100 for zero sum, then continues its draw path |153-byte arm identical |

The percentage numerator uses32-bit wrapping arithmetic equivalent to100×the first counter before signed IDIV by the wrapped sum. These fields' complete gameplay semantics, overflow/division corner cases and reachable domain are not established here; a direct signed-C translation could introduce undefined behaviour. The callback's signed remainder is likewise not an always-positive modulo operation for invalid negative item IDs.

The complete3,598-byte renderer envelope differs at just`0045ae28`, `0045ae29`, `0045af5f`, `0045b4b2`, `0045b664`, outside the two captured arms and dispatch prefix. This is not whole-renderer or transitive equivalence: changed operands, callees, globals and assets can alter other paths. The audit retains exact span hashes and decoded instructions, not a runtime result.

A second checked route at`0044d8cd..0044d8e8` calls shared policy`0044c2d0`, then selects`0044c360` for nonzero role-local ECX or`0044c4e0` otherwise. These selected369/289-byte policy bodies are identical between EXEs. They perform named-entry lookups and flag writes; equal code does not establish equal authored item names, objects or earlier admission.

**Next action at this historical checkpoint (authored-item evidence now supplied below):** trace the instantiated editor item list and its generic admission/dispatch, binding the actual loaded menu asset and role state. The registered draw routine cannot establish that a callback is ever dispatched. Keep the earlier archive-omission and nonzero-rectangle limitations: neither proves hiding or disproves the vendor claim. No new slot6/7 police-only predicate was identified in the checked callback, prefix, cases or policy helpers. Visible acceptance and historical introduction remain pending; no game, instruction probe, compiler or Ghidra write occurred.

## Police-only widget omission is authored in the role-specific menus

**Verified paired archive records and selected EXE bindings; partial support for MP100-048.** The [asset-admission audit](evidence/audits/police-editor-asset-admission.json), reproduced with `python3 analysis/scripts/audit_police_editor_asset_admission.py`, resolves the missing authored-item evidence. It reuses the existing complete asset inventory, verifies both archive hashes and each selected member hash, then parses repeated `[HudItem]` sections rather than treating arbitrary `item=` properties as widgets. This supersedes the preceding vendor-only assessment and its open authored-list question.

| Menu | Author-reference→Modern widget count | Removed item IDs | Retained racer-side tutorial/cone items |
|---|---|---|---|
|`ps1pcop.mnu` |15→13 |6,7 |Not applicable |
|`ps1prace.mnu` |18→18 |None |6,7 |
|`ps2p1c2r.mnu` |31→29 |6,7 |29,30 |
|`ps2p1r2c.mnu` |31→29 |29,30 |6,7 |
|`ps2p2c.mnu` |28→24 |6,7,29,30 |Not applicable |
|`ps2p2r.mnu` |34→34 |None |6,7,29,30 |

No new HudItem IDs are added in these six paired files, and the retained IDs are not renumbered. Named POS slot6 is Tutorial Icon and slot7 is Cone Stats. The previously verified item mapping assigns29/30 to view1 slots6/7 after subtracting23;6/7 belong to view0. Consequently the mixed-role files omit precisely the police player's pair while preserving the racer's pair. This is stronger evidence than the generic, omitted `PSHUDPOS.MNU` asset inspected earlier: these are six actual same-path author-reference/final menu pairs with role-specific content.

Both EXEs retain the six corresponding page callback records at`00555df8..00555e88`, with exact names`ps1prace`, `ps1pcop`, `ps2p2r`, `ps2p2c`, `ps2p1c2r`, `ps2p1r2c`. Each binds initializer`0044de80` and companion callback`0044dfd0`. The complete331-byte initializer`0044de80..0044dfcb` is byte-identical. It reads the two vehicle role bits, snapshots selected layout rectangles, binds two named entry callbacks and updates HUD geometry; this comparison identifies no new slot6/7 hide branch there. The retained HudItem registration/rectangle mapping and draw-case linkage from earlier audits explain why unchanged EXE drawing code can coexist with fewer authored editor items.

**Interpretation:** Modern implements a concrete police-only editor omission in the packaged role-specific menu definitions. A reconstruction that recreates editor items directly must preserve that chosen asset policy; copying every nonzero POS rectangle into an editor would restore items Modern deliberately omits. The underlying layout records and drawing routines remain available for other contexts. Other menu property/layout edits are separate from these exact item-ID removals.

**Remaining limitations:** the author-hosted reference archive is not authenticated pristine retail and is not proven paired to the supplied original EXE. Therefore these are verified reference-package→Modern-package differences, not proof that every retail installation had those original menu records. Actual installed asset selection, generic menu loading/dispatch, visible output and historical1.0.0 introduction remain untested. MP100-048 advances to **partial static/package support**, not runtime acceptance or a newly discovered EXE patch. Earlier negative findings remain valid within their checked code spans. No target, menu, instruction probe, compiler or Ghidra modification occurred.


### Early package already uses the final widget-ID policy

The expanded [asset-admission audit](evidence/audits/police-editor-asset-admission.json) also pins the author-hosted1.1.0 archive and parses the same six role-specific menu members. **All six ordered HudItem-ID sequences already match final Modern**, including police-only removals and preserved racer-side items. None of these six early files is byte-identical to its final counterpart; item-ID agreement does not establish equal layout, other properties or visible output. This bounds the authored omission to **present by1.1.0**, without authenticating retail assets or independently proving the claimed1.0.0 introduction. Exact early member hashes and sequences are retained; no historical menu was executed.
