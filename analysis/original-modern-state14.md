# Original versus Modern: renderer state14 setter policy

## Evidence boundary

Paired setter **`00470ad0`**, original ending at exclusive`00470b1e`, Modern at`00470afa`; retained helpers **`00470b20..00470b6a`** and **`00470b90..00470bb8`**. Reproduce with `python3 analysis/scripts/audit_state14_difference.py`; the [manifest](evidence/audits/original-modern-state14.json) binds both executable identities, complete bodies and helper equality. See the [baseline](original-modern-differences.md). No target instructions, driver calls or Ghidra writes.

## Enabled input zero changes meaning

Both use DWORD **`007a3a64`** as an admission flag and cache the incoming EAX at **`00678b40`** when enabled. Original treats input0 specially: it passes EDX0 with EAX14 to state setter `00431900`. For nonzero input it forms signed32-bit `100-input`, clamps that signed result to1..100 and multiplies by5 before passing it in EDX.

Modern delegates to the existing scaled helper **`00470b20`**, setting incoming EDX=1. That helper performs the same complement/clamp/multiply policy but has **no input-zero exception**. Thus ordinary examples are:

| Input EAX | Original state14 value | Modern state14 value |
|---:|---:|---:|
| 0 | 0 | 500 |
| 1 | 495 | 495 |
| 50 | 250 | 250 |
| 100 | 5 | 5 |
| 101 | 5 | 5 |
| −1 | 500 | 500 |

These are instruction-derived examples, not executed probes. Arbitrary values require the actual wrapping SUB and signed comparisons; an unbounded mathematical clamp is not a complete C contract. The scaled helper additionally multiplies by its caller-supplied factor modulo32 bits, but this Modern wrapper supplies exactly1.

## Disabled path can now clear stale cached state

Original returns without a state call or cache reset when `007a3a64==0`. Modern instead checks **`00678b40`**: if it is−1, return; otherwise call reset helper **`00470b90`**. That helper is byte-identical in this pair: it writes−1 to `00678b40`, zero to **`00678b44`**, and invokes `00431900` with EAX14/EDX0.

The change therefore combines removal of a zero-input exception with conditional cleanup on disabled admission. It does not prove the feature’s high-level name, the backend interpretation of value500 versus0, or that every driver accepts this state. The [renderer initialization comparison](original-modern-renderer-initialization.md) already warns that enable/global roles and initialization stores can differ across versions; this local flag use must not be mistaken for equivalent whole-game initialization.

Original saves/restores EDX/EBP directly. Modern explicitly saves EDX around its enabled helper call; the reset helper saves ECX/EDX/EBP. Full transitive ABI, state-cache behavior inside `00431900`, all callers and enable-flag writers remain follow-up work. No normalized EAX status return is assigned to this setter.

## Retained setter cache qualifies driver dispatch

The expanded audit verifies complete **`00431900..00431a99`** is byte-identical in both baselines. For selector14 it compares incoming EDX with cache **`00554e68`** at `004319b0`. Equal values skip the renderer callback and return the initially selected EAX result1. Unequal values update that cache **before** calling slot **`009ef96c`** with stack pair `(14,value)`. Existing [renderer export binding](original-modern-renderer-loading.md) identifies that slot as `_THRASH_setstate@8`; this is a proven binding, not a name found only in strings.

After the state14 callback, it saves that result in EBX and reads **`00554e5c`**. If that value is signed nonnegative, it calls the same slot again with `(21,cachedValue)`. It ultimately returns the first callback’s result rather than the reapplication result. A signed-negative cache skips the second call. Complete meaning and writers of state21’s cache remain outside this finding.

Consequently the earlier0-versus500 difference is a **requested state-value** difference. Whether a driver call occurs also depends on prior cached state. The cache update is not rolled back on a failing callback in this local body; a later equal request can take the return1 fast path without retrying. No actual renderer failure is asserted, and the callback’s complete status conventions remain unresolved.

Disabled-state cleanup likewise requests state14 value0 through this cache, so it need not invoke the driver when0 is already cached. Separate local cells `00678b40/44` are still reset by `00470b90`. This distinction matters for reconstruction: local cached-input cleanup, state-cache equality and renderer acceptance are three different events.

## Official DX7 interpretation: small integers become reciprocals

The audit extracts **`drivers/dx7/dx7a.dll`** from the hash-pinned official archive, verifies it equals the retained package member and records its hash. Export **`_THRASH_setstate@8`** is **`60003ca0`**. Its selector dispatch uses WORD selector14, byte table `60006aec[14]` and jump table `60006a34`, reaching **`60004df4`**. The retained dispatch prefix establishes this route; it is not an assertion that every renderer uses the same translation.

The case handles the second stack argument as follows:

- Values **1..4095**: convert the signed DWORD to x87, compute **binary32 `1/value`** using constant `60015448=1.0`, store at **`600170e8`**, then pass its bit pattern with downstream selector **38 (`0x26`)** to `60008a10`.
- Zero, or any value with bits in mask **`0xfffff000`** set: store and forward the input DWORD unchanged with selector38. This permits raw floating-point bit patterns as well as the zero case; negative integer interpretation is not uniformly appropriate.

The helper **`60008a10..60008a47`** performs setup/flush checks and dispatches `(object,selector,value)` through vtable offset`0x50`. Exact interface identity and the semantic name of downstream state38 remain outside this bounded audit. The state14 case itself sets its local result to1 without testing this helper’s return, so case admission is not proof of backend success.

For this driver, the game’s changed zero-input policy therefore changes the translated payload from **zero bits** to the binary32 reciprocal of500, approximately **0.002**. This is a driver-specific numerical consequence, not merely an integer-cache difference. It does not establish a visible fog/lighting effect, runtime driver selection, original-driver behavior or equal behavior across DX6/DX8/OpenGL backends. Ambient x87 rounding and exceptions apply to the reciprocal conversion; no driver was loaded or invoked.

## SDK cross-check: downstream state38 is fog density

Microsoft’s maintained legacy SDK header [d3dtypes.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/d3dtypes.h) declares **`D3DRENDERSTATE_FOGDENSITY=38`** for Direct3D7. Its [d3d.h interface declaration](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d.h) places `IDirect3DDevice7::SetRenderState` at zero-based vtable slot20, or **`0x50`** with32-bit pointers. The observed driver call passes object, selector38 and value at that slot. These SDK facts resolve the state’s standard semantic name and match the inspected call shape; they do not by themselves prove the complete provenance of the driver object stored at `60058d9c`.

The driver-specific interpretation is therefore **fog-density translation**, supported by the enum value, method layout and reciprocal/raw-bit handling together. The game’s changed zero-input path requests approximately0.002 instead of0 on that route. Fog enable state, selected formula, vertex/pixel mode, actual accepted device state and visible output remain separate. Microsoft’s [render-state documentation](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3drenderstatetype) describes fog density as a floating-point value used by exponential fog modes; that newer API description is contextual support, while the legacy headers establish the actual Direct3D7 constants/layout used for this comparison.

These external declarations were inspected during this audit. They supplement the hash-bound binary evidence rather than replacing it. No SDK or toolchain was installed, no driver interface was invoked, and no universal meaning is assigned to game state14 across other renderers. Follow-up should bind `60058d9c` to its creation route and trace fog-enable/mode state before promoting a specific visual-fix claim.

## Device creation linkage strengthens the interface identification

The expanded driver audit retains **`600096e5..600096ff`**: it passes output address **`60058d98`** and GUID at **`60015bf8`** through the source object’s vtable slot0. The GUID decodes as **`f5049e77-4861-11d2-a407-00a0c90629a8`**, `IID_IDirect3D7` in the Microsoft legacy [interface declarations](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d.h). This identifies the queried parent interface, rather than relying solely on the DLL filename.

Retained creation paths at **`60009f8a..60009fb0`** and **`60009fd9..6000a0c9`** use that parent pointer’s vtable offset`0x10` with device-class GUID, surface pointer and output address **`60058d9c`**. That call shape matches `IDirect3D7::CreateDevice`, slot4. The decoded class GUIDs include **`84e63de0-46aa-11cf-816f-0000c020156e`** (HAL) and **`f5049e78-4861-11d2-a407-00a0c90629a8`** (T&L HAL). Other branches and fallback details exist; this is not an assertion that either class is selected successfully on the host.

The same output cell is read by the state helper before its offset`0x50` call. Parent-interface GUID, creation ABI, output ownership and consumer method layout together establish a coherent Direct3D7 device route. Successful runtime creation, all teardown/replacement writes and actual device acceptance remain unverified. This strengthens the fog-density interpretation while preserving the distinction between static interface linkage and a graphics test.

## Modern scene entry recomputes fog admission

Modern helper **`00431c1c..00431c33`** computes exactly **`[007a3a54] & [006fd1d4] & [00559234]`** and stores the DWORD result to **`007a3a64`**, the setter’s admission cell. This is bitwise AND, not a normalized Boolean conjunction: nonzero inputs with no common set bit can still produce0. The helper uses EAX and does not return a separately normalized status.

The official Modern20-byte descriptor **`00556924`** binds literal **`fog`** at `0053a87c` and selector storage **`006fd1d4`**, with list pointer `005561be`. The audit retains the exact descriptor words. Existing [graphics-menu transition research](original-modern-graphics-menu-transition.md) documents save/clear/restore writes to that live setting; its value is not immutable merely because it has an option descriptor. The support flag `007a3a54` and scene-state `00559234` still require complete writer/lifecycle analysis.

Paired scene-render prefix **`004bc160..004bc176`** establishes a changed producer: Modern calls the new recomputation helper unconditionally at **`004bc16d`**, after saving incoming EAX in EBX. Original instead tests incoming EAX and, only when zero, calls **`00431c30`** at `004bc171`. The retained original helper is only `PUSH EBP; MOV EBP,ESP; POP EBP; RET`. Thus this is an added admission-state recomputation on the inspected scene route, not a rename of an original equivalent helper.

Together with disabled-state cleanup, this connects the setter policy to a concrete changing admission producer. It does not prove every caller first runs this producer or that the three inputs are normalized0/1 in all modes. No runtime scene, menu option or renderer state was changed.

## Frontend transition also refreshes admission

The other decoded direct call to Modern recomputation is **`0044b346`**, in the frontend transition loop. Paired span **`0044b316..0044b360`** is retained in the audit. It invokes active descriptor initialization **`0044ab40`**, optionally invokes **`0044a0c0`**, normalizes a nonzero local result to3, then Modern refreshes fog admission before issuing the existing sound request. The [slideshow transition investigation](original-modern-slideshow-navigation.md) documents how this path is reached and why active/pending descriptors matter.

Original’s same span has no recomputation call. At `0044b346` it instead loads ECX1, followed by EDX127 at `0044b34b`; Modern inserts the5-byte call at the first address and moves ECX1 into the second slot. Both then load sound identifier4 into EAX and call **`004181d0`** at `0044b35b`. The removed volume setup belongs to the separately changed [frontend-sound interface](original-modern-frontend-sound.md); it must not be treated as arbitrary dead-code removal or as a new caller-supplied EDX contract for Modern.

This places recomputation after the inspected descriptor initialization/transition work, as well as at scene-render entry. The two observed routes can refresh the cached admission value at different points in the menu/race lifecycle. Complete transition coverage, indirect calls and every writer of the three source globals remain unresolved. No menu transition or sound was executed.

## Coupled state21: fog mode and enable policy in DX7

The audit now resolves selector21 through the same driver dispatch tables to **`60004c44`**, retaining its case through exclusive`60004df4`. This identifies the state reapplied by the game’s cached setter after state14 changes.

| Game state21 value | Observed DX7 requests through `60008a10` |
|---:|---|
| 4 | State35=1, state140=0, then cached state34 colour and state38 density |
| 8 | State35=2, state140=0, then cached state34 colour and state38 density |
| 2 | State35=3, state140=0, cached colour/density, then state36/start and state37/end |
| 0 | State28=0; clear local mode-enable bookkeeping |
| 1 | Conditional state28=1; further capability/previous-mode tests apply |

Microsoft’s legacy [render-state declarations](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/d3dtypes.h) identify35 as fog table mode,140 as vertex fog mode,34 as fog colour,38 as fog density and28 as fog enable. The mode-value4/8/2 branches also test capability cell **`6005ab0c`** before their listed requests; unsupported paths branch elsewhere. The value1 path has additional handling for previous mode`0x10`. The table is a scoped mapping, not a complete success matrix or proof that all input values are valid.

The density cache reapplied here is exactly **`600170e8`**, the cell written by state14’s reciprocal/raw-bit route. Thus the game’s retained state21 reapplication has a concrete backend coupling to density and fog mode. Each case can mark its local result successful after issuing helper calls without validating every helper result; the game’s own cache also stores requests before dispatch. Accepted GPU state remains a separate question.

This resolves the previously unnamed coupling for the official DX7 backend. It does not prove fog is enabled in any particular scene, establish equivalent original-driver behavior, or explain all game callers’ state21 choices. No fog mode was set at runtime.

## Support producer: configuration opt-in followed by mode trial

Modern **`004b597b..004b599e`** reads `GetPrivateProfileIntA("THRASH","FogSupport",0,path)` with path pointer **`007a382c`**, normalizes any nonzero result to1 and stores **`007a3a54`**. The official DX7 `thrash.ini` contains **`FogSupport=1`**; the audit extracts that exact archive member and retains its SHA-256. A setting of0 bypasses the following trial, so this cell is not a pure hardware-capability result.

The already compared [renderer-initialization route](original-modern-renderer-initialization.md) reaches **`004b5bb0..004b5bd6`** in its software/d/v common path. When the cell is nonzero, it directly invokes `_THRASH_setstate@8` with **`(21,4)`**. Return0 clears the cell; nonzero retains it. It then issues **`(21,0)`** regardless of the flag. The generic initializer route described in that report skips this common block, so no universal “all renderer paths query support” claim is made.

The newly decoded DX7 case above identifies value4 as a fog-table-mode route and value0 as fog disable. The game therefore uses an opt-in plus a mode-setting trial and its return, rather than a separate dedicated capability API. Driver capability gates and its local return conventions qualify that result; later lower-level device-call failure is not necessarily reflected. Configuration path construction, all alternative initialization paths and actual hardware acceptance remain separate evidence.

This gives partial static support for **MP161-010** (“asks a renderer if it supports the fog effect”). It does not date the behavior’s introduction, prove successful visual fog or turn the opt-in cell into a fully verified support Boolean for every backend. No INI value was changed and no renderer was invoked.

## Distinct follow-ups: removed no-op call and fog-gated state helper

[The legacy-render audit](scripts/audit_legacy_render_call.py) verifies complete original/Modern batch envelope `004c6f00..004c70eb` (491 bytes), original no-op target and a separate Modern state helper. [Its manifest](evidence/audits/legacy-render-call.json) records pinned executable hashes, full-span hashes and disassembly locations. No renderer or instruction probes were executed.

In `ProjectAndQueueNearbySpatialQuadBatches`, the sole changed region is `004c6fbc..004c6fc8`. Original sets EDX=5, copies EDI to EAX and calls `00431c20`. That original target's complete body is exactly `PUSH EBP; MOV EBP,ESP; POP EBP; RET`: it has no renderer call, data write or lasting general-register update under normal return. Modern replaces the twelve-byte caller region with a jump over ten NOPs. All other bytes in the complete batch function are identical, including preceding call `004bf4c0` and the subsequent loop decrement.

Consequently this removal does **not** establish a removed renderer operation or changed quad formula. The omitted argument assignments still change incidental EAX/EDX values at the next instruction, so whole machine-state or caller equivalence is not proven by the target being a no-op. Modern's saved 481-byte union excludes the ten NOP bytes and reports only two changed in-body bytes; complete comparison includes all removed instructions.

Separately, Modern `00431c34..00431c4d` (25 bytes) checks DWORD `007a3a54`. If zero, it returns. Otherwise it sets EAX=`15h` (decimal 21), EDX=4, and calls retained state wrapper `00431900`. The [fog-support producer](#support-producer-configuration-opt-in-followed-by-mode-trial) and renderer-loading research qualify that global; it is not an immutable hardware-only capability.

The saved label `SetRenderState15ToFourWhenFlagSet` must be read with hexadecimal `15h`, not decimal state 15. The exact verified request is state **21**, value **4**. Its full contextual/driver meaning and all callers remain separate. Original byte `00431c34` is a RET at the end of another stub; numeric address equality does not establish a corresponding original state-helper body. This helper is **not asserted to replace** the no-op at `00431c20`, and the batch function's removed call does not reach it.

**Bounded status: done for batch byte differences, no-op target and Modern helper contract; original helper counterpart mapping pending. Confidence: verified static code.** Follow up on register dependencies, full helper callers and driver effects before claiming a visual change. Executable bytes, Ghidra state and maintained C remain unchanged.

## DX5 rejection provides a backend-specific trial result

The [reference/final DX5 audit](original-modern-dx5-reference-pair.md#exe-fog-trial-connects-to-the-rejected-dx5-selector) now connects the same official EXE trial to the final DX5 export. Its bundled INI lacks FogSupport, so the captured reader requests default0. If a nonzero flag reaches the common trial route with that DLL bound, its selector15h/decimal21 rejection returns0 and clears the flag. The captured recomputation then writes zero admission while support remains zero.

This is distinct from the DX7 accepted-mode/capability path above. It verifies a backend-specific negative result, not live API behaviour, all initialization routes or blanket absence of rendered fog. Later writers and actual selected INI/DLL remain unobserved. No new renderer or target instructions were executed.

## Historical LightBeams key controls this setter's admission

The [historical capability audit](scripts/audit_lightbeams_history.py) now
retains all three complete setter bodies in its
[evidence manifest](evidence/audits/lightbeams-history.json#setter_evolution).
This connects the [historical configuration reader](original-modern-renderer-loading.md#historical-lightbeams-reader-and-capability-defaults)
to the original/final comparison, without treating an INI label as a proven
rendering feature name.

| Artifact | Admission at setter entry | Enabled body |
|---|---|---|
| Supplied original | `00470ad4 CMP DWORD[007a3a64],0` | Original zero exception and inline complement/clamp/scaling |
| Modern1.2.0 | `00470ad4 TEST BYTE[007a392c],1` | Byte-identical remainder of original setter |
| Final Modern1.6.1 | `00470ad0 CMP DWORD[007a3a64],0` | Delegates to scaled helper; disabled cache-reset branch |

The original and1.2.0 complete78-byte bodies `00470ad0..00470b1e` differ
only within the seven-byte gate instruction. The historical reader normalizes
`[THRASH] LightBeams` to0/1 at `007a392c`, so its configured result controls
whether this setter updates input cache `00678b40` and requests state14.
A false gate returns without that cache update or request. Other callers can
still reach the retained scaled/reset helpers independently; this is not a
whole-feature disable proof.

The final global at the same setter has the separately documented recomputed
admission contract. Neither numeric-address reuse nor the old key establishes
that it still means LightBeams. The final key's absence therefore does not
establish removal of this setter: a changed implementation remains present.
The DX7 state14 route documented above couples to fog density, which further
warns against naming the setter's entire effect from the historical key.

**Status:** done for the three pinned entry bodies and historical reader-to-gate
link; verified static evidence. Complete historical downstream effects,
intermediate removal date and rendered outcomes remain unresolved. No target,
API or instruction probes were executed, and no database or executable changed.

## Menu fog admission becomes contextual at150

**Verified historical support/effective split and selected context writers; taillight-specific attribution unresolved.** The [menu-context audit](evidence/audits/menu-fog-context-history.json), reproduced with `python3 analysis/scripts/audit_menu_fog_context_history.py`, pins author-hosted1.4.0/1.5.0 EXEs and their DX6 members. It supplies a concrete earlier boundary for the final scene-admission contract above and complements the later [152 mode/enable split](original-modern-renderer-loading.md#fog-formula-setup-separates-from-ordinary-enable-state-in152).

| Contract |1.4.0 |1.5.0 |
|---|---|---|
|FogSupport reader |`004b5b0b..004b5b2f`: fallback0; nonzero→4; store directly to`007a3a64` |`004b58c4..004b58e7`: fallback0; nonzero→1; store support at`007a3a54` |
|Effective gate helper |`00431c20` is a five-byte balanced-frame no-op |32-byte`00431c20..00431c40`: support AND option`006fd1d4` AND context`00559234`; nonzero→4; store`007a3a64` |
|Menu loop at`0044b346` |No gate refresh call at that site |CALL`00431c20` |
|Scene entry at`004bc16d` |Conditional call to retained no-op`00431c30` when incoming EAX is zero |Unconditional CALL`00431c20`; branch over two NOPs |

The checked context producers are byte-identical in both versions:

- Main frontend route`0044b271..0044b27e` clears EDI and stores0 to`00559234`.
- Pause initializer prefix`0044b958..0044b96a` supplies EDX1 and stores1 to that cell.
- In-race initializer prefix`0044ba38..0044ba4d` also supplies/stores1.

These are selected writer routes, not a complete write census or a universal “menu/race Boolean” type declaration. With context0, the new bitwise recomputation necessarily publishes effective0 regardless of support/option values. With ordinary support/option/context1 it publishes4 in150. The later152 helper keeps raw intersection1 instead, as the linked report explains. Do not transplant the final normalized-looking mask contract into150.

Complete116-byte scene-state restore`00431b40..00431bb4` remains identical in140/150. It passes effective`007a3a64` as payload to cached selector15h at`00431b89..00431b99`. This gives the changed admission a concrete downstream state consumer while preserving cache/provider and all-caller limits. Actual fog output and the policy of every menu/scene transition remain untested.

### DX6 has a separate small code edit at the same boundary

**Later follow-up:** the [descriptor/insertion comparison](original-modern-display-modes.md#dx6-public-mode-count-gains-its-leading-slot-in150) now resolves this cell as the public mode count; the counter-meaning limitation below records the earlier checkpoint. Lighting attribution remains unverified.

The paired `drivers/dx6/dx6a.dll` members are94,208 bytes with SHA-256`d32ee0f11361977ecaa01402b33a0a1ea4f4732b118355a5b98696768f8d25cb` (140) and`6c4a300fd55ed5e6c3c85983d43903717543d1b69146275856322da61a76b152` (150). Their complete equal-sized`.text` sections differ at exactly **eight bytes**, `60001c7f..60001c87`.

At the end of initializer`60001c50`,150 inserts `INC DWORD[6003bd3c]` before POP EDI/RET, moving that epilogue six bytes later. The retained prefix zeroes the cell, supplies callback`60001cd0` and performs an indirect call through object`60014988` vtable+20. The added increment is unconditional after that call; it is not guarded by a local result test. It preserves EAX but changes arithmetic flags. The counter's exact purpose and full producer/consumer lifetime are not established here, so this edit is **not labelled a fog or lighting fix**.

Section differences are `.text`8, `.rdata`0, `.data`0, `.reloc`44 and`.rsrc`24 bytes. Relocation/resource and PE-header semantics are not closed by these counts; code-byte localization is not complete driver equivalence. Exact initializer captures and section hashes are retained in the audit.

**MP150-033 remains vendor-only:** contextual fog suppression is a real EXE change at the advertised boundary, and the selected DX6 code edit is localized, but neither alone identifies the taillight draw/light-colour path or proves its visible repair. Follow the actual menu lighting submission and effective state before attributing this release-note claim. The broader fog-option/context mechanism can be reconstructed independently without resolving that visual investigation. No menu, game, DLL/API, instruction probe, compiler or Ghidra modification occurred.
