# Original versus Modern: Race Now entry-state helper

## Evidence boundary

Modern `00437614..004376fb` is a complete helper, previously named `UpdateFrontendRaceNowEntryFlags`. Its entry is inside an original instruction; it must not be treated as a rewritten original function at the same VA. Original `00437600` is a larger frontend routine containing a related credits gate. This chapter compares that explicit shared rule and documents the Modern helper; complete extraction/caller correspondence remains unresolved.

Run `python3 analysis/scripts/audit_race_now_difference.py`. The [manifest](evidence/audits/original-modern-race-now-entry.json) retains both baseline fingerprints, Modern's full body, original setup span `00437600..004377be` (expanded in the follow-up below), exact token bytes and disassembly hashes. Ends are exclusive. No menu, instruction or game execution; no executable/Ghidra edits.

## Modern helper's exact branches

The helper takes an EAX context, returning immediately if EAX is nonzero **and** `00559234` is nonzero. Otherwise PUSHAD/POPAD preserves general registers while calling lookup `00442a40` with the context and token strings. Null context is passed through rather than rejected; the follow-up below establishes that lookup has no null-context fallback.

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

The complete original setup capture includes coordinate writes for nine other tokens, detailed below. Absence of Modern's whole helper at the same address does not prove that all its other behaviors were absent everywhere in the original. Likewise the token bytes are identical in both files, which establishes names rather than complete UI behavior.

**Verified:** complete Modern branch map, exact token identities, original credits gate and invalidity of same-VA function pairing. **Pending:** map all original counterparts and alternate layout paths, establish full caller preconditions and lifecycle-state meanings, verify language-lookup preservation, identify actual localized `f1h/f2h` text, and validate menus at runtime. The follow-ups below close the direct caller census, lookup-null behavior, selected flag consumers and direct branch-selector writes. Historical release attribution is unresolved; no catalog row is promoted solely from these token names.

## Lookup and result-predicate follow-up

The manifest now retains complete lookup `00442a40..00442a95` and result predicate `004cf090..004cf11e` and asserts both bodies are byte-identical between original and Modern. Their local behavior therefore supplies retained dependencies for the new helper, not two additional rewritten routines.

The lookup immediately reads an unaligned DWORD at context+16h and arithmetic-shifts by 16 to obtain a signed WORD start index from context+18h. It walks 0bch-byte entries rooted at `00604ee0`, stopping at a zero type DWORD. For entries with non-null token metadata at +10h, it calls `004429c0` and returns the first matching entry. It preserves EBX/ECX/ESI/EDI/EBP and does not establish EDX preservation. No local context-null or index/capacity guard precedes the walk.

Thus the Modern outer helper's EAX-zero branch is **not** evidence of supported “current menu” lookup. If EAX is zero, its first lookup attempts the context+16h read unless an external interception or other unestablished environment behavior intervenes. No such invocation or fault was observed. Treat a valid context as an input precondition until callers prove otherwise; the outer helper's partial guard alone is insufficient validation.

Predicate `004cf090` does not consume the entry pointer as a parameter in the inspected body. It reads global mode/result state, invokes `004cf000` / `004cef80` on relevant branches, and returns normalized EAX from its local EDX accumulator. Its prologue saves ECX and epilogue restores it at `004cf11b`; this supports retention of the caller's entry pointer across this predicate. Its existing result-state interpretation is documented in the [series menu contract](series-terminal-menu-contract.md), including limits on terminal-track and human/result filters. No successful race continuation follows merely from the predicate returning one.

For flags, the [menu-input comparison](original-modern-menu-input.md) establishes that the fallback token scanner requires entry bit 0 clear before selecting it and invoking its callback. Consequently OR bit 0 in this helper has a demonstrated **navigation exclusion** consumer; this does not establish that every selected-entry dispatch is blocked, since those paths differ. The separate bit `1000h` has a callback-suppression consumer verified in the follow-up below. The text-pointer write also crosses language lookup `004d1850`, whose ECX contract must be kept distinct from the predicate preservation just verified.

Closed: lookup null behavior, record stride/start-index source, retained helper correspondence and predicate ECX preservation. Pending: all caller preconditions, language-lookup preservation and complete original policy correspondence. The bit `1000h` consumer is verified below.

## Direct caller input witnesses

The manifest now captures and validates eleven Modern direct CALL sites found in the retained disassembly. Each instruction's relative target is asserted against the hash-pinned official executable. This is a census of the inspected direct calls, not proof that no indirect callbacks or embedded references can invoke the helper.

| Call site | Immediate EAX input producer / local condition |
|---|---|
| `004374d7` | Copy ECX to EAX. |
| `0043760a` | Inherit incoming EAX in wrapper `00437600`; preceding store only sets `00559c68=1`. |
| `00437e44` | Copy ECX to EAX; skip this call when `00559234 != 0`. |
| `0043d5de` | Copy ECX to EAX. |
| `00442ae3` | Copy ECX to EAX. |
| `004432eb` | Copy ECX to EAX. |
| `00447e09` | Copy ECX to EAX. |
| `00448451` | Copy EBX to EAX. |
| `0044863b` | Copy EBX to EAX. |
| `0045d923` | Keep incoming EAX; immediately before the call, PUSHAD and copy EAX to ECX. |
| `0045e993` | Load EAX from caller local `[EBP-4]`. |

None of these immediate producer instructions forces a null input. Conversely, register copying and inheriting a callback parameter do **not** prove non-null values, valid record extents or correct menu lifetime. Full producer chains remain pending. The earlier lookup-null issue is therefore a conditional precondition question, not a demonstrated reachable null call or runtime fault.

Wrapper `00437600` now consists of its initial `00559c68=1` write, the helper call and EAX-zero return. The original routine at `00437600` contains the credits gate plus additional coordinate work. This gives a concrete extraction/delegation witness while leaving the fate of the remaining original coordinate work unresolved. Calls from several other contexts show that the extracted policy is refreshed beyond this one wrapper; they do not establish that every call is admitted by the helper's own `00559234` guard.

## Bit 1000h consumer and original coordinate writes

The script now retains the callback gate `0044a5cb..0044a5e5` in both executables and asserts byte identity. It checks that entry DWORD+2ch is non-null, then tests byte entry+5 mask 10h (equivalent to WORD entry+4 mask **1000h**). A set bit skips the callback. Otherwise it supplies the entry in EAX and a sign-extended AX-derived value in EDX, calls `[entry+2ch]`, and retains a nonzero callback result in EDI.

This establishes **suppression of this entry callback**, without assuming that the callback is universally the sole draw path or that the bit alone makes the entire entry invisible. Combined mask `1001h` therefore has two separately evidenced consumers: bit 0 excludes entries in the inspected fallback navigation scanner; bit 1000h suppresses the inspected +2ch callback dispatch. Clearing both on `2btt` permits those two gates but does not guarantee invocation, which also requires the surrounding state and non-null callback.

The original capture is now expanded to the complete `00437600..004377be` routine. After its credits gate, it finds nine entries and conditionally writes their coordinate WORDs at +6/+8:

`FUNTXT_1`, `FUNTXT_2`, `FUNTXT_3`, `FUNTXT_4`, `FUNTXT_56`, `FUNTXT_7`, `FUNTXT_8`, `FUNTXT_9`, `FUNTXT_10`.

Values come from the `00559c6c..00559cb4` data neighborhood, with offsets added to one coordinate: 156 for `FUNTXT_1`, 150 for the other inspected entries. The stores retain only the low WORD of the computed value. These are entry-token and field observations, not authenticated screen labels or a complete coordinate system.

Modern `00437600..00437612` instead sets `00559c68=1`, delegates to `00437614`, clears EAX and returns. It contains none of those coordinate writes or token lookups. The full new helper also has none. Thus their removal **from this setup/delegation path** is verified. Searching or validating alternate layout producers and packaged menu definitions is still required before claiming removal of the visible text or universal removal of its positioning.

The initial report's unknown bit-1000h consumer and partial-original-body boundary are superseded by these captures. Remaining limitations include alternate callback consumers, complete menu resource correspondence, calling-state admission and rendered behavior. No menu was opened or modified for this check.

## Branch selector producer witnesses

Modern direct writers to `007a276c` in the inspected disassembly are now captured and asserted against the baseline bytes:

| Store address | Value established by instructions | Context boundary |
|---|---:|---|
| `004405a7` | 1 | Literal DWORD store after entry-position setup. |
| `00440725` | 0 | XOR EAX,EAX followed by store, in existing `InitializeConnectPlayersMenuCallbacks` (`004405c0`) analysis. |
| `004530b4` | 0 | XOR EAX,EAX followed by store, after entry-flag work and call `004961e0`. |
| `0045d2dc` | 1 | Literal DWORD store after optional `00444be0` / `004a65e0` path. |
| `0045d60f` | 1 | Literal DWORD store after conditional entry flags/text update. |

This supplies concrete producers for the helper's branch selector. It is mutable menu lifecycle state in these paths, not established as a static INI option, renderer capability or network transport identifier. It can change without the Race Now helper being called immediately afterward; the separate caller witnesses establish refresh points, not a universal ordering guarantee.

The observed direct writers use only zero/one, but no universal boolean invariant is claimed: bulk initialization, indirect aliases, external state and the complete menu call graph have not been enumerated. The current function inventory resolves the connect-players initializer; other enclosing procedures are not assigned speculative menu names merely from adjacent token strings. Exact meanings of the two lifecycle states and why they select `2btt` versus normal `racenow` policy remain pending.

For next comparison work, trace the two clear-path callers and their menu resource definitions before naming this global or attributing the extracted policy to a particular release. The address/value producer gap is closed for the five captured direct stores; runtime state admission is separate.
