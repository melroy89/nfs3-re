# Original versus Modern: Race Now entry-state helper

## Evidence boundary

Modern `00437614..004376fb` is a complete helper, previously named `UpdateFrontendRaceNowEntryFlags`. Its entry is inside an original instruction; it must not be treated as a rewritten original function at the same VA. Original `00437600` is a larger frontend routine containing a related credits gate. This chapter compares that explicit shared rule and documents the Modern helper; complete extraction/caller correspondence remains unresolved.

Run `python3 analysis/scripts/audit_race_now_difference.py`. The [manifest](evidence/audits/original-modern-race-now-entry.json) retains both baseline fingerprints, Modern's full body, original partial span `00437600..0043762c`, exact token bytes and disassembly hashes. Ends are exclusive. No menu, instruction or game execution; no executable/Ghidra edits.

## Modern helper's exact branches

The helper takes an EAX context, returning immediately if EAX is nonzero **and** `00559234` is nonzero. Otherwise PUSHAD/POPAD preserves general registers while calling lookup `00442a40` with the context and token strings. Null context is passed through rather than rejected; the lookup's null-context resolution must be established separately.

| Condition / operation | Instruction-level effect |
|---|---|
| Lookup `2btt` (`0053a998`) succeeds | Initially OR WORD entry+4 with `1001h`. |
| Global `007a276c == 0`, `2btt` absent | Look up `3btt` and `racenow`; if `racenow` exists, OR its low flags byte with 1. No local modification to found `3btt` in this branch. |
| Global `007a276c == 0`, `2btt` present | OR WORD flags of existing `racenow` and `3btt` with `1001h`; clear those same two bits on `2btt` using AND `effeh`. Then return. |
| Global `007a276c != 0`, signed `006fd3b0 > 1` | Find `credits` (`00537494`); if present OR its low flags byte with 1. |
| Same nonzero-global path, `00662968 == 0` | Return after the credits gate. |
| Same path, `00662968 != 0`, `racenow` found | Call `004cf090`; zero result ORs low flags byte with 1. Then update the entry's text pointer at +3ch regardless of that result. |
| Text pointer update | `006fd3b8` equal 1 or 2 selects localized ID `f1h`; all other values select `f2h`, through `004d1850`. |

The flags are literal bit effects. This chapter does not assign both `1001h` bits complete visibility/enabled meanings, expand `2btt`/`3btt` into UI labels, or infer a network transport from unnamed globals. Setting a bit and clearing it elsewhere are not symmetric operations: many branches only OR and do not clear previously set flags. Initialization and subsequent menu passes matter.

The helper's text-pointer write depends on ECX retaining the found entry across `004cf090` and `004d1850`; existing analysis documents the resulting write, but full custom register preservation and all callees should be read back before using this as a reconstruction ABI. No scalar return or flags-output contract is established.

## Original credits rule and remaining comparison

Original `00437600` first stores 1 to `00559c68`, looks up `credits` with `00442a40`, and ORs low flags byte+4 with 1 only when the entry exists and signed `006fd3b0 > 1` (`00437611..00437628`). Modern retains that signed mode test and byte-mask effect, but places it within the `007a276c != 0` branch of the extracted helper. Modern's initial return gate and preceding `2btt` policy also affect whether that branch is reached.

The original routine continues with coordinate writes for other tokens beyond the captured span. Absence of Modern's whole helper at the same address does not prove that all its other behaviors were absent everywhere in the original. Likewise the token bytes are identical in both files, which establishes names rather than complete UI behavior.

**Verified:** complete Modern branch map, exact token identities, original credits gate and invalidity of same-VA function pairing. **Pending:** map all original counterparts, determine globals/flag meanings from producers and consumers, trace helper call sites and null lookup behavior, identify actual localized `f1h/f2h` text, and validate menus at runtime. Historical release attribution is unresolved; no catalog row is promoted solely from these token names.
