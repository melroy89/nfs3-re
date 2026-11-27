# Original versus Modern: menu navigation and multiplayer chat input

## Scope and evidence

**Static code comparison, no interactive menu or chat test.** Baselines: supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [provenance](original-modern-differences.md).

Run `python3 analysis/scripts/audit_menu_input_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-menu-input.json) records identities, token strings and instruction-span hashes. It asserts byte equality of the lobby handler, send routine and previous/next selection bodies. Raw assembly remains ignored under `analysis/captures/modern-differences/menu-input/`. No executable or Ghidra mutation, UI/network execution or new instruction probe.

## 1. Tab/Escape bypass the earlier multiplayer interceptor

Matched dispatcher `0044a2d0` receives menu context in EAX and key code in low DX. In original, nonzero session state `007a22e0` routes all keys through `00441700`, then tests `004499f0` before normal menu handling (`0044a2e0..0044a30a`). A nonzero first-handler result or failed second gate exits the dispatcher.

Modern keeps that path for other keys, but at `0044a2e9..0044a2f3` explicitly recognizes **Tab (9)** and **Escape (27)** and jumps around both calls to `0044a315`. The lobby handler `00441700..004417ee` itself is unchanged. Thus the change is a routing decision in its caller, not a rewritten text handler or new underlying keyboard transport.

This permits Tab/Escape to reach ordinary menu processing while the session/text path is active. It does not guarantee an unconditional focus change: the selected entry callback still runs before navigation and can consume the key. Callback/asset validity and every menu state were not exercised. See the existing [network input routing notes](detailed-analysis-notes.md#network-lobby-pointer-targeting-and-input-routing-00441680-00441700).

## 2. New Tab and named arrow actions

Original generic fallback handles Escape and arrow codes `4800/4b00/4d00/5000` but contains no Tab action. Modern adds the following behavior after the selected entry has declined the key:

| Key | Modern path |
|---|---|
| Tab | Call Shift helper `004f1fcc`; Shift held → `00449f30` (previous), otherwise `0044a0c0` (next). |
| Escape | Find enabled `escape` action through `0044a240`; invoke it if found, otherwise return consumed result 1. |
| `4800` up | Try named token `keyup`; if no match, select previous. |
| `4b00` left | Try `keyleft`; if no match, select previous. |
| `4d00` right | Try `keyright`; if no match, select next. |
| `5000` down | Try `keydown`; if no match, select next. |

Shift helper sets AL=`0x10`, calls the imported **GetAsyncKeyState** at `[00534738]`, converts signed-negative AX to EAX=1 (otherwise 0), and executes `TEST EAX,EAX` before restoring ECX/EDX and returning. The dispatcher uses **JNE**, so the final flags are part of the interface. The POPs and RET do not overwrite them. Merely declaring a C boolean return would omit this machine-level caller contract.

The previous/next selection routines at `00449f30..0044a0b4` and `0044a0c0..0044a23a` are byte-identical between versions. Modern reuses them for Tab and as arrow fallbacks; it does not introduce a different selection algorithm inside those bodies. Their dependencies/data can still change behavior.

For arrows the original requests sound ID 0 with EDX=`0x2d`, then calls previous at `0044a40e` for Up/Left or next at `0044a423` for Down/Right. Final Modern tries the named action first and calls the same selection helpers on a miss at `0044a3db` or `0044a402`. Neither direct fallback path requests sound before entering the helper. A named hit instead branches to `0044a409` and invokes the selected entry as Enter. This comparison covers local call order. Audio from the selected callback or other downstream code remains separate. Reproduce by disassembling `0044a315..0044a429` in both baselines.

On a Modern named arrow hit, the dispatcher sets DI=1 at `0044a36a` before scanning. The scanner preserves EDI. After invoking the matched entry at `0044a41b`, the dispatcher uses DI as the sound ID at `0044a420` and calls `004181d0`. The standard panorama button handler `00461270` saves EDI at `00461272` and restores it at `004613d7` on the route through its item callback. Thus that route requests sound ID 1 after the action. Other entry handlers require their own DI preservation check, and the sound helper can decline a request. See the [panorama callback route](original-modern-credits-panorama.md).

## 3. Escape-specific lookup becomes a token-parameterized helper

Original `0044a240..0044a2c8` scans entry records of stride **0xbc** at `00604ee0`, starting from the signed WORD at menu `+0x18` (recovered through a wider unaligned load and shift). It searches specifically for literal `escape` at `00538fbc`.

Modern retains `0044a240` as a wrapper that pushes `escape`, then calls new scanner `0044a24c`. The scanner takes EAX=menu, EDX=relative-index output pointer, and one stack token string; it returns a matching entry pointer in EAX and cleans the stack token with `RET 4`. ECX is saved/restored. Its visible filters retain entry type 5, non-null metadata at `+0x10`, token lookup through `004429c0`, and flag bit 0 clear. It remembers the first eligible match while scanning to the table sentinel.

The caller uses a match to write menu selection WORDs `+0x1a/+0x1c`, then invokes the matched entry's callback at `+0x30` with action code 13. There is no additional callback-null test at that invocation; valid entries depend on template/producer contracts. The ordinary currently selected callback, which receives the original key, remains a distinct earlier call and can suppress fallback navigation.

Original Escape requests sound ID 3 with EDX=`0x7f` at `0044a3c4` before looking up `escape`, so the request precedes any matched callback. Modern sets DI=3 at `0044a3a9` and performs the lookup first. A miss sets EBX=1 and jumps to `0044a420`; a hit calls the selected action and then falls through to that same tail. The tail uses the low WORD of EDI as the sound ID. Thus on a hit the ordering is reversed, with sound ID 3 assuming the callback preserves DI. On a miss both versions request sound and return 1. The revised route first appears in retained 1.4.0, where the tail calls adapter `004181c4`, which supplies EDX=`0x7f` to `004181d0`. From retained 1.5.0 the same tail calls `004181d0` directly. The [transition archive hashes](original-modern-differences.md#5-confirmed-menu-routing-difference) bind 1.3.1 and 1.4.0. Actual audio and indirect callback behavior remain untested.

Both dispatchers normalize callback result 2 to returned EAX=0 at their final block. Modern uses PUSHAD/POPAD and writes saved EAX explicitly; original restores its narrower saved-register set. EDX preservation therefore differs across the outer dispatcher, even where its returned action code agrees. No full register-state equivalence is claimed.

## 4. Empty chat guard is added above an unchanged sender

Matched network-text keyboard handler `00441b20` branches to its Enter path at `00441b8e` in both binaries. Original constructs a sender-name/separator/text string and calls `0042d810` at `00441bfa`, without a zero-first-character test in that Enter path.

Modern first loads text pointer `[005f3fdc]`, compares its first byte with zero at `00441b93`, and on empty input jumps directly to its handled-return epilogue at `00441be1`. It therefore skips formatting, `0042d810`, and the following text-clear operation on that path. This tests **empty string**, not whitespace-only content; it also does not independently establish a non-null pointer before dereferencing it.

For nonempty input, Modern sets ECX=99, preinitializes the last byte of its 100-byte local buffer to NUL, then calls bounded copy helper `004f93ec` three times for sender name, separator and text (`00441b98..00441bbe`). The remaining-count state is shared across those copies. The original uses inline prefix/separator copy loops and then `004eedf0` with EBX=`0x57` for the text append. The Modern construction's cumulative bound is a code change; exact displayed truncation depends on the supplied prefix/text and consumers, not just nominal message length.

Sender `0042d810..0042d855` is **70 identical bytes** in both executables. It has no corresponding empty-string guard: it builds its message and invokes `004a60e0`. Therefore the release note's protection is verified for this input caller, not as a universal contract of every possible sender invocation or provider path. Successful transmission/delivery and all other routes remain untested.

The 1.3.1 and 1.4.0 executables date the local Enter guard.
At `00441b8e`, 1.3.1 begins building the sender string, while
1.4.0 loads `005f3fdc` and checks its first byte before formatting.
The first 1.4.0 copy also sets ECX to 99. The same release starts
padding the 42-byte old tail at `00441bef..00441c19`, which
remains padding in all later retained releases. Message delivery
and other paths to the sender were not tested.

## Catalog mapping and next work

- **MP140-007:** static empty-string rejection at the UI send caller is verified; whitespace filtering and universal send rejection are not claimed.
- **MP140-008:** Tab/Shift+Tab reach the retained previous/next selection routines when earlier entry handling declines the key.
- **MP140-009:** explicit Tab/Escape bypass of the multiplayer handler/gate is verified; actual chat-focus UI behavior remains untested.

Next: compare asset-defined navigation tokens and affected menu templates; trace named-action callback producers and menu-sound differences; validate the relevant UI states if an observable behavior claim is needed. The [Modern-to-Modern runtime observations](normal-tcp-race-validation.md) are not an original/Modern input comparison.

## Panorama named-arrow integration follow-up

The [panorama callback comparison](original-modern-credits-panorama.md#conditional-leftright-to-panorama-callback-chain) now connects the named Left/Right scanner through the generic button template/input handler to the initialized panorama Previous/Next callbacks. It retains the required code/template witnesses and official tokens for all three related menu assets. This advances the earlier asset/callback follow-up within that bounded context; other slideshow callbacks, admission states and runtime input delivery remain unverified.

## Complete packaged-menu named-arrow inventory

The existing audit now scans **all52 official `.mnu` archive members** and all52 matching uppercase `fedata_org/menus` backups. It records every member hash and parses exact whitespace-separated `codelink` tokens for `keyup`, `keydown`, `keyleft`, `keyright`. Six official matches occur, all button sections:

| Menu | Left binding | Right binding |
|---|---|---|
| `credits.mnu` | `keyleft previous` | `keyright next` |
| `credits1.mnu` | `keyleft previous` | `keyright next` |
| `slides.mnu` | `keyleft prevslide` | `keyright nextslide` |

There are **no `keyup`/`keydown` bindings** in this official menu-file scan, and **none of these four named-arrow tokens in the52 uppercase backup counterparts**. The code nevertheless supports all four tokens; lack of packaged bindings does not make its Up/Down named-action mechanism absent or prove it unreachable through runtime construction, resources or modified menus.

The backups retain ordinary `next`/`previous` bindings in Credits and `nextslide`/`prevslide` in Slides. Their `CREDITS1.MNU` instead has `GlamNext` and `escape`; it is not paired as a simple token-prefix edit or proof of equivalent callbacks. Original retail provenance is unauthenticated, and this inventory does not establish historical introduction.

This broadens the [panorama-specific linkage](original-modern-credits-panorama.md#conditional-leftright-to-panorama-callback-chain) into a complete named-token inventory of the pinned official menu set, while reusing that chapter’s callback evidence. The matched fields identify concrete authored consumers of the dispatcher’s Left/Right lookup. Full callback semantics for Slides, selected files and disabled/focus states remain separate work. No UI, network input or target instructions were executed.

## Control and Alt entries share Shift's register-and-flags contract

The existing [menu-input audit](scripts/audit_menu_input_difference.py) already retained complete Modern region `004f1fcc..004f1ff0` (36 bytes). It now also asserts every byte and the `GetAsyncKeyState` PE import binding. [The manifest](evidence/audits/original-modern-menu-input.json) identifies all three entry points:

| Entry | Selected key code | Shared-body route |
|---|---:|---|
| `004f1fcc` | `10h`, Shift | Jump to `004f1fd6` |
| `004f1fd0` | `11h`, Control | Jump to `004f1fd6` |
| `004f1fd4` | `12h`, Alt | Fall through to `004f1fd6` |

The Control entry's four saved body bytes are a prefix plus jump; they are not a complete independent implementation without the shared tail. The Alt entry includes the tail. Each zero-extends AL into EAX before pushing the key argument, saves/restores ECX/EDX, calls the API, tests AX, materializes the signed-negative result as EAX=0/1, then executes `TEST EAX,EAX`. That final TEST supplies ZF to callers; POP/RET preserve it. A previous-query low-bit indication alone does not produce EAX=1 because it does not make AX signed negative.

Both EAX and final ZF are outputs. Other general registers are untouched by local instructions beyond EAX/ECX/EDX, with ECX/EDX restored; no standard C Boolean ABI promises the same flags. The direct Shift/Tab consumers documented above demonstrate why reconstruction must keep this hidden condition-code contract when calling original instructions. Complete Control/Alt caller coverage and actual focus/timing behavior remain unverified.

**Work status: Modern local entry/shared-tail contracts done; original functional counterpart mapping pending. Confidence: verified static code/import.** The original same-address region falls within the older timing/calibration code discussed in the [CPU-tier comparison](original-modern-cpu-tier.md); matching numeric addresses does not identify matching modifier helpers. No keyboard or target execution, Ghidra writes or maintained-C changes were made.


## Tab and chat-bypass routing appears at131-to140

The [historical routing audit](evidence/audits/menu-key-routing-history.json), reproduced with `python3 analysis/scripts/audit_menu_key_routing_history.py`, pins131/140 archives/EXEs. The complete131 dispatcher `0044a2d0..0044a439` matches the supplied original.140 contains the Tab/Escape multiplayer-gate bypass, Shift-sensitive Tab fallback and named-arrow scanner described above. This dates those selected mechanisms to the immediate retained boundary rather than inferring their introduction from the original/final endpoints.

140's Shift entry is `004f1f78`, with Control/Alt at+4/+8 and the shared tail through `004f1f9c`. Its36 bytes match the official final region `004f1fcc..004f1ff0`; the import binding is verified in140. The dispatcher at `0044a3a0` calls the helper and uses JNE directly. EAX and final ZF therefore remain separate machine outputs at this historical boundary, just as in the final contract above.

The Shift, Control and Alt helper's complete 36-byte block matches across all seven retained releases from 1.4.0 onward. The call at `0044a3a0` follows its two moves, and the next instruction remains `JNE +0x32` in each EXE. The import slot `00534738` resolves to `USER32.GetAsyncKeyState` throughout.

| Retained releases | Shift entry | Control entry | Alt entry |
|---|---|---|---|
| 1.4.0 | `004f1f78` | `004f1f7c` | `004f1f80` |
| 1.5.0–1.5.2 | `004f1fd8` | `004f1fdc` | `004f1fe0` |
| 1.5.3–1.6.1 | `004f1fcc` | `004f1fd0` | `004f1fd4` |

Reproduce by resolving the relative call, comparing 36 bytes at its destination and checking the PE import slot in each extracted executable. The intermediate placement accounts for the [temporary reuse of the old CPU calibration range](original-modern-outside-function-index.md#when-old-code-ranges-become-all-nops). Moving the block preserves its register and flag behaviour at this caller.

The complete previous/next routines and lobby handler are byte-identical131/140. This qualifies **MP140-008/009**, not **MP140-015**: it establishes routing to existing selectors, not a replacement ordering algorithm. Entry-array construction, selection fields, callback side effects and authored navigation data can still change order despite identical selector bodies. The distinct callback-selection/rendering comparison likewise does not independently prove keyboard order. At this routing-only checkpoint MP140-015 remained vendor-only. The following template/asset comparison now supplies a partial order-producing mechanism; repeating the unchanged selector-body checks alone would not resolve it.

The selected entry callback still precedes fallback navigation and can consume keys. Chat focus, every menu state, actual keyboard timing and complete caller ABI/flags remain untested beyond the retained local witnesses. No game, API, target instructions, compiler or Ghidra change was used.


## Keyboard-order candidate combines template eligibility and asset order

**MP140-015: partial static/package support; live traversal untested.** The [entry-order audit](evidence/audits/menu-entry-order-history.json), reproduced with `python3 analysis/scripts/audit_menu_entry_order_history.py`, pins131/140 archives/EXEs and both Load/IPX menu assets.

The unchanged loader increments ordinal `00660bac` on each parsed section and calls template copier `00449060` at `004496f1`. The retained copier writes a BCh-byte record at `00604ee0 + ordinal×BCh`. The previous/next selectors traverse those indexed records, checking eligibility rather than sorting by screen coordinates. This links authored section order to a conditional keyboard-order input; source section ordinals are not assumed to equal global runtime indices after menu dependencies/base offsets.

Two changes occur together:

| Boundary |131 |140 |
|---|---|---|
|Selectlist template at `00556ff8`, flags WORD+4 |`0200h` |`0000h` |
|Load relative authored order |Back/Cancel before replays list |Replays list before Back/Cancel |
|IPX relative authored order |Gamelist before Join and Refresh |Join and Refresh before gamelist |

Class registry row `00557acc` identifies selectlist type21 and that template. Button row `00557aa8` identifies type5/template `00556e40`; its flags stay0800h. Retained navigation tests include mask1301h (`0044a1fe`), so0200h excludes an otherwise admitted record on that route. Clearing it in the selectlist template changes initial keyboard eligibility, while the section reorder changes where the newly eligible list sits among buttons. This is not merely swapping two controls known to be equally focusable in the older build.

The complete selected loader, template copier and previous/next bodies are byte-identical131/140. The mechanism therefore lies in data consumed by retained code. Later initializers, parsed fields and callbacks can still modify flags or selection; the Race Now policy predicate and selected-entry callbacks remain separate gates. Missing files, runtime-generated controls and global entry bases are not reconstructed by this package comparison.

These facts advance MP140-015 from vendor-only to a **partial candidate**, without proving correct order in every menu or reproducing a keyboard session. The earlier routing audit remains independently useful for Tab/chat/arrow changes. No target instruction, API, compiler or Ghidra mutation was used.


### Complete registered-class flag census finds three changes

The expanded entry-order audit compares the flags WORD at template+4 for **all32 registered frontend classes**, from registry `00557a84` through the zero sentinel at `00557c04`. IDs, names and template pointers match131/140. Exactly three flag WORDs change:

| Class |Template |131 flags |140 flags |Effect of0200h under the retained1301h skip mask |
|---|---|---|---|---|
|selectlist |`00556ff8` |0200h |0000h |Removes this initial skip reason |
|performance |`00557070` |0000h |0200h |Adds this initial skip reason |
|Compass |`00557a44` |0000h |0200h |Adds this initial skip reason |

The other29 checked flag WORDs match. This refines the preceding selectlist finding: the initial eligibility revision both admits one class and excludes two others on the checked navigation route. It is not a global removal of disabled/skip policy. The census covers these flags only, not every template byte or template allocation extent; runtime parsed fields, initialization and callbacks can change effective flags. It does not prove the semantic interactivity of every performance/Compass instance or correct traversal in every menu. MP140-015 remains partial, with no target execution or database mutation.
