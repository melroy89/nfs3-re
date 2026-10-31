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

## 3. Escape-specific lookup becomes a token-parameterized helper

Original `0044a240..0044a2c8` scans entry records of stride **0xbc** at `00604ee0`, starting from the signed WORD at menu `+0x18` (recovered through a wider unaligned load and shift). It searches specifically for literal `escape` at `00538fbc`.

Modern retains `0044a240` as a wrapper that pushes `escape`, then calls new scanner `0044a24c`. The scanner takes EAX=menu, EDX=relative-index output pointer, and one stack token string; it returns a matching entry pointer in EAX and cleans the stack token with `RET 4`. ECX is saved/restored. Its visible filters retain entry type 5, non-null metadata at `+0x10`, token lookup through `004429c0`, and flag bit 0 clear. It remembers the first eligible match while scanning to the table sentinel.

The caller uses a match to write menu selection WORDs `+0x1a/+0x1c`, then invokes the matched entry's callback at `+0x30` with action code 13. There is no additional callback-null test at that invocation; valid entries depend on template/producer contracts. The ordinary currently selected callback, which receives the original key, remains a distinct earlier call and can suppress fallback navigation.

Both dispatchers normalize callback result 2 to returned EAX=0 at their final block. Modern uses PUSHAD/POPAD and writes saved EAX explicitly; original restores its narrower saved-register set. EDX preservation therefore differs across the outer dispatcher, even where its returned action code agrees. No full register-state equivalence is claimed.

## 4. Empty chat guard is added above an unchanged sender

Matched network-text keyboard handler `00441b20` branches to its Enter path at `00441b8e` in both binaries. Original constructs a sender-name/separator/text string and calls `0042d810` at `00441bfa`, without a zero-first-character test in that Enter path.

Modern first loads text pointer `[005f3fdc]`, compares its first byte with zero at `00441b93`, and on empty input jumps directly to its handled-return epilogue at `00441be1`. It therefore skips formatting, `0042d810`, and the following text-clear operation on that path. This tests **empty string**, not whitespace-only content; it also does not independently establish a non-null pointer before dereferencing it.

For nonempty input, Modern sets ECX=99, preinitializes the last byte of its 100-byte local buffer to NUL, then calls bounded copy helper `004f93ec` three times for sender name, separator and text (`00441b98..00441bbe`). The remaining-count state is shared across those copies. The original uses inline prefix/separator copy loops and then `004eedf0` with EBX=`0x57` for the text append. The Modern construction's cumulative bound is a code change; exact displayed truncation depends on the supplied prefix/text and consumers, not just nominal message length.

Sender `0042d810..0042d855` is **70 identical bytes** in both executables. It has no corresponding empty-string guard: it builds its message and invokes `004a60e0`. Therefore the release note's protection is verified for this input caller, not as a universal contract of every possible sender invocation or provider path. Successful transmission/delivery and all other routes remain untested.

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
