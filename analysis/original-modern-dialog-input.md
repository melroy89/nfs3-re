# Original versus Modern: dialog input dispatch

## Evidence boundary

Complete paired **`00445e60..00445efa`**,154 bytes. Reproduce with `python3 analysis/scripts/audit_dialog_input_difference.py`; the [manifest](evidence/audits/original-modern-dialog-input.json) retains baseline hashes, both bodies, dispatch tables and Modern Shift-query helper. See the [main comparison](original-modern-differences.md). Static only; no game/input/audio or Ghidra writes.

## Tab normalization and direct handler table

Both derive a dispatch ordinal from **`00558b14-1`**, accepting unsigned0..3. Original table **`00445e48`** points to four local wrappers, each sign-extending DX and calling a handler: `00444910`, `00444b20`, `00444f50`, `00445520`. Modern changes the table entries to those handler addresses directly and invokes them with an indirect CALL, replacing the original indirect JMP to wrappers.

Before dispatch, Modern treats low WORD input **9** as Tab: it sets DX=`0x4d00`, calls **`004f1fcc`**, and changes DX to`0x4b00` when the helper leaves ZF clear. It then sign-extends DX into EAX for the handler. Non-Tab inputs retain the existing sign-extension route.

The complete Modern helper **`004f1fcc..004f1ff0`** queries **`GetAsyncKeyState(0x10)`** through the actual import at **`00534738`**. It tests the returned signed WORD, normalizes a negative result to EAX1, and ends with TEST EAX,EAX before restoring EDX/ECX. Thus the caller’s branch consumes a real flag output: Shift held selects left code`0x4b00`, otherwise right code`0x4d00`. EDX preservation keeps the prepared DX value alive. A conventional C declaration omitting the flag result would obscure this interface.

## Handler result3 requests sound while preserving the result

Modern compares the selected handler’s EAX with3. On equality, it pushes that result, calls **`004181d0`** with EAX still3, and pops EAX afterward. Other results bypass the request. This adds a local sound request without converting the handler result into the sound helper’s return. Original has no corresponding request in this central dispatch block. Existing [frontend-sound analysis](original-modern-frontend-sound.md) establishes the changed sound-helper interface and its own gates; a call does not prove audible output.

Paired prefix **`00445e60..00445e9a`** and complete tail **`00445ec7..00445efa`** are byte-identical. The retained tail calls optional callback `00558b18` for nonzero handler results, passing a local byte pointer in EDX; that byte controls the later close-helper call. Callback result2 is normalized to0 for the outer return. The initial scene/global admission checks also remain in the equal prefix.

Handler result3’s action identity, full per-dialog navigation behavior, callback preservation and audible consistency remain unresolved. The finding gives partial support for the mini-dialog keyboard-sound claim, but is not complete validation of every dialog or every navigation action. No keyboard layout, held-key timing or UI state was tested.

### Release boundary for Tab and Escape feedback

The 45-byte dispatcher span `00445e9a..00445ec7` matches the hosted original through retained 1.3.1. The original passes Tab through to the selected handler as value 9. In 1.4.0 the same span gains Tab normalization, direct handler-table dispatch and the result-3 sound call together. From 1.4.0 through 1.6.1, the only differences in this span are relative call displacements at `00445ea4` (Shift test) and `00445ebf` (sound request). Mask those four-byte operands when comparing the seven archived builds. The four DWORDs at `00445e48` point to local wrappers `00445ea1`, `00445eab`, `00445eb5` and `00445ebf` through 1.3.1. From 1.4.0 they point directly to the four handlers listed above. See the [modifier relocation table](original-modern-menu-input.md#tab-and-chat-bypass-routing-appears-at131-to140) for the Shift targets. This dates the dispatcher changes. It leaves individual handler history and audible feedback separate.

## First handler: Escape versus navigation feedback

The expanded audit retains complete paired first handler **`00444910..004449c6`**. Exactly four byte positions differ, all within the two relative CALL operands at **`0044496b`** and **`0044498d`**. Original calls dialog cursor-position helper **`00444570`**; Modern calls wrapper **`0043eb88`**. Existing [cursor-position analysis](original-modern-cursor-position.md) verifies that wrapper requests sound0 only when cursor positioning reports a valid item. No other local instruction changes occur in this handler.

Both handlers map low-WORD **`0x1b` (Escape)** to EDX3 and return it in EAX, whereas **`0x0d` (Enter)** returns1. Left/up codes `0x4b00`/`0x4800` decrement the selected index with wrap; right/down `0x4d00`/`0x5000` increment it with wrap. The cursor-call wrapper preserves EDX, so the navigation route keeps its initial result0. Unrecognized inputs also return that initial0. Count/index validity remains a separate invariant; this is not proof of safe empty-dialog navigation.

Thus the new central result3 sound is concretely an Escape/cancel-associated request for this first handler. Navigation can instead request sound0 through the newly retargeted cursor wrapper, then returns0 and bypasses the central callback/close route. Enter’s result1 follows the retained callback handling without this central sound3 request. The conclusion is scoped to the inspected first handler; the other three handler contracts and all dialog callback meanings remain separate work.

This connects the added sound request to an actual input value and separates it from navigation feedback. Audible volume, throttling and device behavior still depend on the changed sound helper and runtime state. No dialog key was pressed during this audit.

## Remaining handler coverage

The audit now retains complete paired timed **`00444b20..00444b60`**, edit **`00444f50..004450bd`** and toggle-menu **`00445520..0044567b`** handlers. The timed body is byte-identical; edit/toggle differences are confined to the cursor CALL operands listed below.

| Call address | Original target | Modern target |
|---|---|---|
| `00444fd5`, `00444ffb` | `00444570` dialog position | `0043eb88` dialog position/sound wrapper |
| `004455a1`, `004455fd` | `00445160` menu position | `0043eba0` menu position/sound wrapper |
| `004455cb`, `00445627` | `00444570` dialog position | `0043eb88` dialog position/sound wrapper |

All eight inspected cursor call sites (the six above and the first handler's two) keep their original targets through 1.3.1. All switch to the [cursor-position and sound wrappers](original-modern-cursor-position.md) in 1.4.0 and retain those destinations through 1.6.1. Comparing the two wrapper bodies and their intervening space at `0043eb88..0043ebb8`, only bytes `0043eb96` and `0043ebae` change in 1.5.0. They are in the relative sound-call operands. The remaining bytes match through final, including the branch that bypasses sound on a zero position result. Reproduce by resolving the eight call operands and comparing the 48-byte wrapper span in the extracted EXEs.

Timed input first tests byte **`00558b4c`**: when zero it returns0; when nonzero Escape returns3, Enter1 and Space2. Edit input maps Escape to ESI3 at `00444fa6`; toggle input maps it to EDX3 at `0044566d`, and their epilogues return that value in EAX. Together with the first handler, this establishes an Escape-associated result3 route for all four dispatch targets, subject to their own gates. The added central sound3 request is therefore not limited to one handler.

The paired local changes and previously verified wrapper contracts support a partial mini-dialog keyboard-sound mechanism: cursor feedback through position-validity wrappers, plus central Escape feedback. This does not prove all actions emit one sound, that callbacks do not add requests, or that audible timing/volume is consistent. The timed handler’s enable state, full edit mutation rules, toggle semantics and runtime audio remain beyond this focused comparison.

## Localized notice wrapper: moved counterpart and constructor inputs

The [notice audit](evidence/audits/localized-notice-difference.json), reproduced by `python3 analysis/scripts/audit_localized_notice_difference.py`, pairs original **`00444be0..00444c0d`** with Modern **`0043fda0..0043fdcc`** through caller **`0043fe09`**. The paired caller prefix`0043fdd0..0043fe0e` changes only its CALL displacement. Original code at the Modern entry address is an unrelated preceding routine’s tail; the saved same-address difference is not a semantic function pair.

Original resolves the incoming localized ID through`004d1850`, stores one pointer at`00661090`, then calls`00444a80` with EAX1, EDX pointing at that array, EBX`226h`, ECX1 and one zero stack argument. Modern resolves the incoming ID plus fixed ID11, stores two pointers at`00661090/+4`, and calls the same constructor with EAX2, EBX/ECX0 and a zero stack argument. Its EDX points to the shared array through the preserved setup; full localization-helper preservation remains an interface dependency.

Complete constructor **`00444a80..00444b1d` (157 bytes)** is byte-identical. It stores EAX as line count`00558b1c`, EDX as pointer-array address`00558b20`, timestamp`0079c1a4` into`00558b44`, and the absolute value of EBX into`00558b48`. Zero EBX sets byte`00558b4c` to1; positive EBX copies CL there. The wrapper therefore changes line count and configured timer/state inputs without rewriting this constructor. Visible wording, elapsed-time behaviour and dismissal still require their own localization/event-loop evidence.

The call at `0043fe09` targets the one-line wrapper through retained 1.3.1 and the two-line wrapper starting in 1.4.0. The new 44-byte wrapper and the common 157-byte constructor each match across all seven releases from 1.4.0 onward. The old 45-byte wrapper is still byte-identical in original and final, and final still calls it at sites including `00438284` and `0044e768`. This is a redirection for the inspected notice. Both one-line and two-line wrappers remain available in final.

Modern’s PUSHAD/POPAD preserves incoming general registers, including EAX, while original restores its narrower saved set and leaves a constructor-derived EAX. Neither saves flags or x87 state. Both use shared pointer storage, so a maintained C interface must preserve its lifetime/overlap requirements rather than assume stack-local text arrays. Reentrancy and all notice callers remain unresolved. No dialog or instruction probes were run.

## Initial edit state stops requesting first-character replacement

The complete dialog initializer `00444c20..00444f48` (808 bytes, exclusive end) differs only inside `00444c90..00444ca6`. Original sets byte `00558b10` to 1, sets DWORD `00558b2c` to 1, then loads the same stack-supplied selection into EAX. Modern still sets the byte to 1, but zeros `00558b2c` before loading that selection. The common store to `00558b3c` at `00444ca6` and the rest of the initializer remain byte-identical. It is the DWORD's value, not a newly different initial selected index, that changes here.

[The expanded dialog audit](scripts/audit_choice_dialog_followup.py) verifies pinned executable identities, this complete initializer, renderer and full edit-handler witness; [its manifest](evidence/audits/choice-dialog-followup.json) records hashes and exact float arguments. The insertion tail `0044504f..004450bd` is byte-identical. The full handler also contains the separately investigated cursor-call retargeting earlier in this chapter; it is **not** entirely byte-identical.

That retained insertion tail supplies a concrete consumer of the changed DWORD. At `0044505d`, nonzero `00558b2c` can allow the path even when the current length has reached its limit. After character-admission helper `00443810` accepts the input, nonzero flag at `00445079` triggers:

- Clear the flag.
- Clear the 256-byte buffer at `00558b58` through `004e0640`.
- Set current length `00558b50` to zero.
- Continue to the ordinary append/increment sequence.

With flag zero, the clear/reset block is skipped and the retained append sequence uses the current length. For an otherwise valid prefilled edit dialog, original's initial flag therefore requests replacement on the first accepted character; Modern's zero requests normal append behavior instead. This is conditional on reaching this edit path, character acceptance and buffer/length state. Other keys have their own branches, and all dialog-type admission/initial-buffer producers are not proven by this local chain.

## Four renderer float arguments receive small adjustments

The complete renderer `00444000..00444350` (848 bytes) differs only in four PUSH-immediate arguments:

| PUSH address | Original binary32 bits / value | Modern binary32 bits / value |
|---|---|---|
| `004440d8`, `0044410d` | `3f0d0000` / 0.55078125 | `3f0d4ccd` / 0.551953136920929 |
| `00444220`, `00444255` | `3ef80000` / 0.484375 | `3ef8999a` / 0.48554688692092896 |

Both pairs increase by approximately 0.001171887. The respective sequences still reach draw helper `004db000` at `0044412e` and `00444275`; the surrounding pushes, x87 arithmetic, calls and branches are byte-identical. The audit establishes exact changed argument bits, not the final visible texture sample or a texel-alignment fix. Assigning texture-coordinate/depth semantics requires the draw helper's complete argument mapping and resource evidence; a nearby rendering call alone is insufficient.

The retained releases show two edits. In 1.0.0–1.5.3 the four immediates use `0x3f0d4fdf` and `0x3ef89fc7` (each twice). In 1.6.0–1.6.1 they use the slightly lower Modern values in the table. The full 848-byte renderer matches within each group, and each boundary changes only the low two bytes of the four immediates. Reproduce by reading RVA `0x44000` for 848 bytes in each archive and comparing the PUSH operands as little-endian binary32. The display effect remains unverified.

### The changed values reach two vertex fields

For both draw calls the changed immediates occupy stack arguments 5 and 11, counting from the first DWORD after the return address. The intervening rounding helper `004dfd56` returns without consuming the pending arguments. The draw helper saves ESI and EDI before establishing its frame, then subtracts `0x4a` from EBP. In that adjusted frame it reads the two values at `[EBP+0x6a]` and `[EBP+0x82]` at `004db0f5` and `004db163`. It copies the DWORDs unchanged to `[EBP-0x4e]` and `[EBP+0x12]`, respectively, at `004db0f8` and `004db16c`.

Each destination is offset `0x18` within its 32-byte vertex record, in vertices 0 and 3 of the local quad starting at `[EBP-0x66]`. This identifies the affected vertex field in the original and final draw helper. In final 1.6.1, the submitter at `004db365` passes all four vertex pointers to `004c12e0`. On its all-zero-outcode path, the latter rewrites depth at vertex offset `0x08` but leaves offset `0x18` intact before calling slot `009ef94c` at `004c1433`. The [renderer export mapping](detailed-analysis-notes.md#pursuit-marker-backend-quad-export-boundary) identifies that slot as `_THRASH_drawquad@16`. Thus an unclipped submission hands the four changed values to the renderer in their respective quads. The partial-clipping path and visible sample remain outside this check.

In the packaged 1.6.1 DX8 driver (SHA-256 `ddb8a55514bc650384e349cf3830946c149f71234e90a41327f69aca793e81b8`), that export at `60002790` copies input vertices to the vertex buffer using the configured stride. The first copy starts at `60002872`; the other copies use consecutive positions at the same stride. The per-vertex adjustment at `60001ff0` writes X/Y and can write diffuse and specular, leaving `+0x18` intact. The [DX8 format and submission analysis](original-modern-renderer-texel-alignment.md) verifies the 32-byte `0x1c4` format: four position floats, diffuse and specular DWORDs, then one texture-coordinate pair. In that format, `+0x18` is the first texture coordinate (U). The dialog changes the U coordinate on one edge of each quad on this path. No actual format selection, clipping outcome or rendered sample was observed.

**Bounded work status: done; confidence: verified static initializer/consumer relationship and renderer constants.** Actual text-entry behavior, input limits/aliases, dialog-type coverage, draw-argument interpretation and rendered output remain untested. No target execution, Ghidra writes or reconstruction edits were performed. Preserve the original's replace-first policy or Modern's append policy as appropriate rather than silently choosing a preferred UX.

## Network-service callback changes only its notice wrapper

The expanded [localized-notice audit](scripts/audit_localized_notice_difference.py) verifies complete same-address service-selection callback `0043f680..0043f75a` (218 bytes). Its only two differing bytes lie in the CALL at `0043f6f3`: original invokes `00444be0`, Modern invokes `0043fda0`, both with EAX=12. [The manifest](evidence/audits/localized-notice-difference.json) retains full-span hashes and the callsite evidence.

The call at `0043f6f3` keeps the original wrapper through 1.3.1 and switches to the two-line wrapper in 1.4.0. In all seven retained packages from 1.4.0 onward, English resource ID 12 is “Connecting...” and ID 11 is “Press escape to cancel”. The wrapper supplies those IDs in that order for this caller. To reproduce, resolve the relative call in each EXE and read the little-endian string offsets at `4×12` and `4×11` in the archived `fedata/text/text.eng`. The wording is verified for the packaged English text. Input timing and actual cancellation still require runtime evidence.

The call is conditional on incoming action 1, a zero result from `004446c0`, and nonzero result from service helper `0049ea70`. Its caller first copies the selected string to `006fbb7e`, marks the output byte 1, requests the notice, then enters the retained local refresh loop and later service call `0049e800`. Those instructions and all other callback branches are byte-identical. API/helper success semantics and actual connection state are not established by their local nonzero tests alone.

The [moved notice comparison](#localized-notice-wrapper-moved-counterpart-and-constructor-inputs) already verifies the wrapper difference: original supplies one localized string and fixed constructor arguments; Modern supplies the requested string plus localized ID 11, with revised constructor arguments. This callback is another concrete consumer of that change, rather than evidence of a rewritten network protocol.

**Bounded status: done; confidence: verified static full callback and linked wrapper contract.** Actual notice text/timing, service availability and multiplayer behavior remain untested. The callback's retained calls can still reach other version differences, so whole network equivalence is not claimed. Executables, Ghidra and maintained C are unchanged.

## Replace-first policy bound to IP and player-name dialogs

The expanded choice-dialog audit now retains three paired constructor-call prefixes and verifies their bytes identical across the supplied original and official Modern. It pins the final package's English text asset and decodes the localized IDs used on those paths. These labels identify the intended dialogs; they are not a validation of original-retail translations or observed UI text.

| Constructor CALL | Localized evidence from official English | Initial text pointer | Requested maximum length |
|---|---|---|---:|
| `0043f543` | ID10: `Enter IP address or domain name:` | `006fbb7e` |29 |
| `0045cf53` | ID201: `Player One` | `006fd2fc` |10 |
| `0045cfd3` | ID202: `Player Two` | `006fd368` |10 |

The complete 38-byte argument-and-call spans starting at `0043f522`, `0045cf32` and `0045cfb2` match the hosted original in all twelve retained Modern releases. The call sites therefore retain their filter, prefill pointer and requested maximum across the 1.4.0 constructor change. Reproduce by reading the three spans at their PE RVAs in each archived executable.

All call `00444c20`. The initializer stores3 at `00558b14`, binding the existing central dispatch to edit handler `00444f50`. Stack argument2 (initializer `[EBP+14h]`) becomes initial-text pointer `00558c58`, while argument3 (`[EBP+18h]`) supplies the requested maximum. In retained `00444db5..00444e2c`, helper `00443860` validates the input pointer/content using the selected filter; on a true result, the initializer requests a bounded copy through `004e0e30` into edit buffer `00558b58` and computes current length `00558b50`. A false result selects zero length. Complete validation/copy-helper contracts and guaranteed NUL termination remain separate requirements.

This connects the changed initial replace flag to the relevant ordinary prefilled path. Original initializes `00558b2c=1`: the first accepted append character clears the existing buffer and length before insertion. Modern initializes0 and skips that clear/reset block. The proof concerns **first accepted character insertion**, not literally every first key: Escape, Enter, navigation, invalid characters and full-buffer admission have separate branches. The raw maximums also differ between the IP and name constructors, so a single unconstrained-string test would not establish all behaviour.

The [existing local-name/roster evidence](original-modern-ghost-loading.md#player-identity-fields-are-explicitly-restored) independently binds `006fd2fc` to local player identity; the localized Player One/Two paths and their text pointers provide the direct dialog correspondence. These caller prefixes are unchanged, so the observed difference comes from shared initialization/handler policy, not a newly added name/IP constructor.

MP140-035 now has **partial static support** for the reported previous-text-loss repair, with constructor, prefill, flag and insertion links. The constructor store at `00444ca0` retains its original EDX input through 1.3.1. From 1.4.0 onward, `XOR EAX,EAX` followed by the store at `00444c9d` clears the flag. Compare PE RVA `0x44c94` for 22 bytes in each retained executable. Real typing, all character filters and later state changes remain unverified. No input event, game dialog or instruction probe was executed.

## Retained filter1 and bounded prefill contract

The same audit now retains eight complete helper bodies around filter dispatch, character/string validation and copy, asserting them identical between the two EXEs. It also checks the full six-row,20-byte-per-row file-backed table at `00558c70`. This resolves selected filter/copy questions above for the IP/name callers, which supply filter1; other filters and later callback mutations remain separate.

For active language indices0..5, filter1 character dispatch `00443810` reaches `004436c0`, which selects callback `00443510` from each row+0ch. That callback masks the input to one byte and calls `004434f0`, accepting values0x20..0xff inclusive. This includes DEL0x7f and high bytes; it is not an ASCII-printable-only, Unicode or IP-address syntax validator. The six ordinary file-backed rows share this callback, but the dispatcher does not locally bounds-check arbitrary active language values.

Filter1 string validation `00443860` reaches `00443700`, selecting row+10h callback `00443520`. Null/empty strings are rejected. A nonempty string is scanned until NUL, calling the same character predicate for every byte and stopping on failure. Validation is **not limited to the requested edit length**. An invalid byte after the portion that would be copied can therefore reject the entire prefill. Readable, terminated source storage remains an input requirement.

The retained41-byte copier `004e0e30..004e0e59` takes EAX=destination, EDX=source and EBX=count, copies until count exhaustion or source NUL, then zero-pads any remaining count. It returns the original destination. When count is exhausted first, it does not add a terminator beyond that count. Forward copying and register effects must be preserved rather than assuming arbitrary overlap safety or a universally NUL-terminated result.

The constructor supplies the missing termination premise: it requests a256-byte zero-fill at `00558b58`, normalizes the maximum to1..255 (otherwise255), and copies at most that maximum. On ordinary successful initialization with these disjoint caller buffers, byte[max] remains zero even when the copied prefix fills its limit. The later length scan therefore has a terminator within the256-byte edit storage. This is a bounded constructor/copy derivation, not a generic copier guarantee or validation of malformed pointers.

At a full prefilled length, Modern's cleared replace flag causes the retained capacity gate to reject an additional ordinary character, preserving the existing text. Original's initial flag can bypass that capacity gate, clear the buffer and accept replacement. This boundary is part of the policy change, rather than proof of a new overflow or an unlimited append path. Other key branches and real input timing were not exercised.

MP140-035 remains partial: the local mechanism, selected caller/filter binding and ordinary termination contract are verified statically; all filters, callback/active-language lifetimes, malformed storage and actual typing remain unverified. No target instructions or external input API were executed.

## Glide conversion of the dialog texture coordinates

In the packaged 1.6.1 `drivers/glide3x/voodoo2a.dll` (SHA-256 `f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b`), `_THRASH_drawquad@16` at `60003480` makes four local vertex copies. For vertex 0, it adds `0x04000000` to the raw DWORD at source offset `0x0c`, interprets that result as a binary32 scale, and multiplies both texture coordinates by it at `600034bc..600034d3`. The other three copies repeat the conversion. The two triangle calls at `600035cc` and `600035df` receive the converted copies. See the [Glide callback analysis](detailed-analysis-notes.md#nglide-triangle-callback-identity-and-state-replacement) for the callback selection.

The changed U values therefore reach Glide's triangle path after a per-vertex conversion. For ordinary positive normal reciprocal-depth inputs whose biased exponent remains normal, the bit addition scales that input by 256. The instruction operates on raw bits, so this equivalence is conditional. Live driver state and the visible sampling difference remain untested.
