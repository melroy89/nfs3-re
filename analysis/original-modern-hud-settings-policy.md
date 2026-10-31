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
