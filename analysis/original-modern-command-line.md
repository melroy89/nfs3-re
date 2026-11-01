# Original versus Modern: command-line switches and driver override

## Evidence boundary

Static supplied-original/official-Modern comparison; exact fingerprints are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_command_line_difference.py`. The [manifest](evidence/audits/original-modern-command-line.json) retains the complete `004a5080..004a54e3` parser spans, all 33 paired switch slots, five help aliases and Modern case-copy helpers. No game or command-line test was executed.

## Table contents change while layout remains

Both parsers scan 33 pointer entries at `0055eb34` and recognize five help aliases at `0055ec3c`: `?`, `/?`, `-?`, `-h`, `/h`. Modern's only nonempty switch entries are:

| Index | Original | Official Modern |
|---:|---|---|
| 0 | `-softtri` | `-driver=` |
| 11 | `-nomovie` | `-nomovies` |
| All other indices | Other original entries | Empty string |

The manifest lists every original entry, including renderer choices `-softlin`, `-voodoo`, `-voodoo2`, `-ragepro`, `-d3d`, `-pvr`, `-pvr2`, `-verite`, `-verite2` and diagnostic/debug choices. This is not just a shortened help description: table-driven recognition reads these same pointers at `004a5108`.

The original parser's flag-bit calculation and table scanner remain; successful matches OR the corresponding bit in storage beginning `0055eb2c`. The first 32 indices map to bits 0..31 of the first DWORD; index 32 maps to bit 0 of the next DWORD. The x86 variable shift masks its count, including the index-31 path's intermediate -1 count. Do not translate this mechanically into a C shift by a negative count.

Empty table strings are not the same as deleted table slots. Empty-argument matching and other parser routes are outside ordinary named-switch behavior. This chapter does not prove every removed switch is universally ignored or every old flag consumer was deleted.

## Modern driver prefix route

Modern obtains the original argument pointer in ESI and scratch destination in EDI, with ECX=80 (`004a5168..004a5172`). When no ordinary table match was found, it:

1. Calls `004f9418`, which copies up to the supplied count while converting ASCII A..Z to lowercase via `004f0ae0`.
2. Compares the scratch prefix with **`-driver=`**, length **8**, through `004eb390` (`004a517d..004a518e`).
3. On equality, passes **the original argument pointer +8**, not the lowercased scratch suffix, to `004b57f4`.
4. Sets bit 0 of `0055eb2c` and marks the argument recognized (`004a519c..004a51a4`).

The driver parser then performs its own lowercase/slash/suffix normalization, documented in the [renderer loader report](original-modern-renderer-loading.md#5-driver-specific-configuration-before-loading). Modern renderer configuration checks bit 0 to bypass the INI driver-name read. This connects the command-line prefix to actual selection precedence; it is not just a string found in the image.

The two copy wrappers preserve ESI/EDI/ECX. Later `004f943c` recopies the original argument into scratch while converting lowercase ASCII to uppercase, before the remaining parser logic. The 80-byte bounded loops stop on NUL or exhausted count; they do **not** append an extra terminator on count exhaustion. Long/malformed argument handling is therefore not proved safe or fully validated by the presence of a bound. No such input was run.

Original uses an unbounded local copy followed by `004f8020` and has a different special-prefix parsing block in this region (`004a515f..004a51f7`). This comparison does not assign the Modern driver route to those original bytes or claim a complete audit of all original parameterized arguments.

## Help presentation and precedence limits

Modern's help-building loop explicitly tests each switch text's first byte and skips empty entries (`004a543a..004a544a`). Consequently only nonempty current table entries contribute switch rows in that loop. This supports **MP100-043**'s reduced debug-option display mechanism, but not the historical assertion that each old debug option never worked.

Argument iteration decrements the saved count before loading an argument (`004a50a7..004a50cd`). It therefore visits trailing arguments before earlier ones, excluding the executable at index zero on the ordinary path. The setter and INI bypass are now traced below, establishing bounded duplicate-driver behavior rather than inferring it solely from iteration order.

**MP110-003** is statically supported by the original renderer-option table versus Modern's universal prefix route and INI bypass bit. Exact release introduction still needs the v1.1.0/predecessor binaries. The local Modern-derived executable's separate About-text edit is outside this official-baseline parser comparison.

## Duplicate driver options: name and suffix are separate state

The evidence manifest now also retains Modern's complete driver setter `004b57f4..004b5841` and configuration admission prefix `004b5844..004b5877` (exclusive ends). These are Modern-specific mechanisms, not corresponding original functions at those addresses.

The ordinary parser follows each recognized argument through `004a51f8` to `004a5334`; when the recognized marker is nonzero and the help marker is zero, `004a533e` jumps back to the decrement at `004a50a7`. The next argument is therefore processed even when bit 0 is already set: that bit does **not** suppress another `-driver=...` setter call in this argument loop. Later, `004b5845..004b584d` tests it to suppress the INI driver-name read.

Within setter `004b57f4`:

- Empty input immediately returns (`004b57f7..004b57fa`), leaving both name and suffix unchanged.
- Nonempty input copies into global `007a3a74`, converting ASCII uppercase to lowercase and `/` to `\`. An `@` is written as NUL and ends the name. The routine preserves general-purpose registers through PUSHAD/POPAD.
- Only when the last consumed source byte is `@` **and the next source byte is ASCII `0`..`9`** does it call decimal converter `004f0430` and write suffix global `007a3a70` (`004b5823..004b583a`). There is no suffix-clear operation on ordinary name-only, empty or invalid-suffix input. The first-byte gate rejects a leading sign or whitespace even if the converter itself could accept them.

For ordinary short, NUL-terminated arguments which reach this path without help/error interruption, reverse iteration means the **leftmost nonempty setter input wins the name**, while the **leftmost qualifying numeric suffix wins the suffix independently**. If no argument qualifies for a suffix write, the preexisting suffix survives. These are effects at the end of argument parsing and through the inspected INI-skip prefix, not proof that no later code overwrites the state.

Illustrative static traces below use symbolic driver names; they do not claim those DLLs exist or can load. `S` means the suffix value on entry to parsing.

| Arguments in command-line order | Final normalized name in the inspected path | Suffix |
|---|---|---|
| `-driver=Alpha -driver=Beta` | `alpha` | `S` |
| `-driver=Alpha -driver=Beta@2` | `alpha` | 2 |
| `-driver=Alpha@1 -driver=Beta@2` | `alpha` | 1 |
| `-driver=Alpha@x -driver=Beta@2` | `alpha` | 2 |
| `-driver=Alpha@-1 -driver=Beta@2` | `alpha` | 2 |
| `-driver= -driver=Beta@2` | `beta` | 2 |

The exact empty spelling `-driver=` matches ordinary table slot 0 before the prefix route, sets the same bit 0 and skips the setter for that argument. A nonempty `@2` setter input instead writes an empty name and suffix 2; it is not equivalent to empty input. In either case a recognized driver option can suppress the later INI driver-name lookup without establishing a usable driver name. No load failure or success was exercised.

The earlier 80-byte parser scratch bound and the setter's **55-byte** copy limit remain important: exhausting the setter count does not explicitly append NUL. These illustrative results are restricted to short inputs and small suffixes; overflow in the decimal converter, malformed/overlong strings, preexisting storage contents and later consumers require separate investigation. This is documentation of observed instruction semantics, not a proposed cleanup of the original behavior.

## Remaining work

Pending: every original parameterized option, downstream semantics for each retained flag, malformed/overlong arguments, decimal overflow, later driver-state writes and actual help/driver selection on the OS/Wine. The report establishes this table and prefix mechanism, not complete command-line behavioral equivalence or runtime robustness.

The [original selector follow-up](original-modern-registry.md#original-selector-precedence-and-call-chain) now establishes fixed priority among the ten ordinary original renderer flags, including their downstream selector writes and initializer caller. Modern duplicate `-driver=` handling is now bounded above; runtime loading and later state changes remain separate questions.

## Retained network prefix parser: the movie gate is a port value

The audit now records the separate12-entry prefix table **`0055ec50`** in both executables. Its pointers and strings are identical: `-IP=`, `-PORT=`, `-NAME=`, `-PLAYERS=`, `-PNUM=`, `-RACE=`, `-TRACK=`, `-CAR=`, `-LAPS=`, `-LEVEL=`, `-CLASS=`, `-AINUM=`. These are separate from the33 ordinary switch slots above; shortening that ordinary table did not erase this parser path.

For a matched prefix index1, the retained dispatch **`004a5317..004a5326`** reaches **`004a5268`**. It passes the suffix pointer, format **`%d`** at `0053d68c`, and destination **`007a1fdc`** to `004f0548` at `004a5273`; nonzero conversion result marks the argument recognized. There is no local0..65535 range clamp in this assignment block. Complete conversion syntax, overflow behavior and all later validation are not established by the format string alone.

At **`004a5480`**, nonzero `007a1fdc` also activates checks for other required launch fields. The retained error text names rebroadcaster address, player name, player ID and number of players. A network-setup consumer at `0049e1cb` loads this field into ECX before `004a5b00`; this address is a locator outside this parser’s retained function envelope, not a complete network ABI proof. Together the matched `-PORT=` table/dispatch establishes a concrete producer, without claiming that it is the only write to the global.

This resolves a [movie-policy unknown](original-modern-idle-movie.md): both playback wrappers reject nonzero `007a1fdc`, so that gate is associated with the network-launch port, distinct from **NoMovies / `-nomovies` bit11**. The original idle controller rejects it before music stop/playback policy; Modern removes that early test but still reaches the identical wrapper gate. Consequently, a configured port can suppress the actual movie request even after Modern’s idle controller reaches its stop/select/restart sequence. This is static control flow, not proof of a visible or audible network-session defect.

## Retained prefix handlers and storage map

The expanded audit verifies **byte equality** for complete network-prefix dispatch/assignment envelope **`004a520b..004a5334`**, final launch-field checks **`004a5480..004a54e3`**, and copy helper **`004e0e30..004e0e59`**. Thus the following are retained behaviors within that scope, despite changes elsewhere in the containing parser:

| Prefix index / name | Destination and matched-handler behavior |
|---|---|
| 0 / `-IP=` | `007a1fa0`; reject empty or length>=60 suffix, otherwise copy including terminator |
| 1 / `-PORT=` | `007a1fdc`; `%d` conversion, mark recognized on nonzero conversion result |
| 2 / `-NAME=` | `007a1fe0`; copy at most11 bytes from original argument suffix, zero-pad unused count |
| 3 / `-PLAYERS=` | `007a1ff8`; numeric handler |
| 4 / `-PNUM=` | `007a1ffc`; numeric handler |
| 5 / `-RACE=` | `007a2000`; numeric handler |
| 6 / `-TRACK=` | `007a2004`; numeric handler |
| 7 / `-CAR=` | `007a2008`; numeric handler |
| 8 / `-LAPS=` | `007a200c`; numeric handler |
| 9 / `-LEVEL=` | `007a2010`; numeric handler |
| 10 / `-CLASS=` | `007a2014`; numeric handler |
| 11 / `-AINUM=` | `007a2018`; numeric handler |

The common numeric branch computes **`007a1fec + 4*prefix_index`**, passes the suffix in the scratch argument and format `%d` to `004f0548`, and marks recognition on nonzero conversion result. It has no local per-field range checking. This does not establish every field’s later gameplay interpretation, protocol width, valid domain or successful network launch.

For Name, the caller deliberately returns to the **original argv pointer plus matched-prefix length**, rather than copying the transformed scratch suffix. Helper `004e0e30` preserves ECX/ESI, returns the original destination in EAX, advances EDX while copying and returns EDX=0. It pads only the remainder of its supplied11-byte count. For a source at least11 bytes long, this helper does not append an additional terminator or write byte12. Preexisting destination bytes and later consumers remain separate concerns; a reconstruction must not silently change the retained bounded-copy behavior.

The final launch checks require the IP and Name buffers to be nonempty and `007a1ff8` nonzero when Port is nonzero. They do **not** individually test `007a1ffc` there, despite the error text mentioning Player ID. This is the exact local check sequence, not evidence that player ID is optional throughout the remaining network stack. No command-line or network probe was executed.

## Retained launch consumer versus changed peer endpoint policy

Complete launch consumer **`0049e080..0049e212`** and connection wrapper **`004a5b00..004a5d10`** now have paired byte-equality assertions in the same manifest. This establishes unchanged local instructions and register handoff, not identical external services or transitive callees.

The launch consumer branches on whether IP buffer `007a1fa0` is nonempty. On the configured-address branch it copies the launch Name to `006fd2fc`, then applies these raw fields:

| Launch storage | Consumer output |
|---|---|
| Race `007a2000` | DWORD `006fd3b8` |
| Track `007a2004` | DWORD `006fd4ac`, with no local domain check |
| Laps `007a200c` | DWORD `006fd4b4`; also derive `006fd4b0`:8→2,4→1,otherwise0 |
| Level `007a2010` | DWORD `006fd470` |
| Class `007a2014` | DWORD `006fd4d4` |
| Car `007a2008` | EAX to `00439a10` with EDX=0 |

At **`0049e1c6..0049e1d8`**, it passes Name pointer in EAX, IP pointer in EBX, Port DWORD in ECX and the low WORD of Player ID (`007a1ffc`) in DX to `004a5b00`. Only DX is loaded at that site; EDX’s upper16 bits are not established by that instruction alone. The callee explicitly zero-extends the saved low WORD at `004a5b65..004a5b6e`, so reconstructing Player ID as an unconstrained full-width input would misstate the consumed value. This does not establish the valid application-level ID domain.

With an empty configured IP, the caller instead supplies a fixed address-string pointer, literal ECX **6666 (`1a0ah`)** and EDX=0 to the same wrapper. The complete purpose/availability of that default address and provider behavior remain outside this local comparison.

The separate [peer endpoint comparison](original-modern-network-endpoints.md) traces Modern’s configurable getter and default9803 replacing original1030. Those changes occur in another endpoint route. They must not be applied indiscriminately to the retained network-launch Port field, literal6666 fallback, or NPS connection wrapper merely because all concern networking. Port byte order, provider libraries, actual connection success and full launch settings validation require their own evidence. No network traffic or target instructions were executed.

## Help banner, error text and dialog title change

The expanded [same audit](scripts/audit_command_line_difference.py) now retains
both sets of header/error/title strings, verifies the MessageBoxA binding and
captures complete Modern copy helper `004f93ec..004f93fe`. The
[manifest](evidence/audits/original-modern-command-line.json) already retains
the complete parser. This explains72 NOP-replaced outside-body bytes
`004a537c..004a53c4` as part of a larger help-building rewrite, not an
independent removed function. That interval begins inside the original PUSH
at `004a537a`; disassembly from the inventory boundary would be misleading.

| Presentation contract | Original | Official final Modern |
|---|---|---|
| Initial banner | Format at `0053d6ac`, with build time `19:22:39`, date `Aug 27 1998` and an empty field | Copy embedded text at `0053d698`, identifying the1998 game and Modern Patch1.6.1/VEG |
| Invalid-argument format | `Invalid argument: %s` plus one newline | Same wording plus two newlines |
| Extra separator | Append an additional newline before switch rows | No separate separator append at the old location |
| Dialog title | Branch selects `Invalid argument` or `Usage` | Always literal `About` |
| Output API | MessageBoxA at `004a546f` | Same imported API/call site |

Modern `004a5344` supplies count1024 to helper `004f93ec`, with EDI pointing
to buffer `007a1ba0` and ESI to the embedded banner. For a normally terminated
source shorter than the count, the helper copies the terminator and leaves
ESI/EDI pointing at that terminator, so the following invalid-argument format
can append using EDI. Exhausting the count does **not** append a new NUL.
The selected pinned banner fits; arbitrary mutated input is not qualified.
Later invalid-argument and switch-row formatting still calls `004df690`
without a locally supplied remaining-capacity bound. Thus the initial copy
limit is not a proof that the whole message construction is bounded, and no
actual overflow or crash is claimed.

The original append sequence rescans the existing buffer for NUL using
REPNE SCASB before formatting at its end. Modern removes that work for the
initial invalid-argument append and removes the separate newline append,
then resumes the retained switch-row loop. That loop still rescans the
buffer while adding rows. These are construction changes, separate from
which switches the parser recognizes and the existing empty-entry filter.

**Status:** done, verified static for the strings, helper contract, NOP-span
classification and title branch replacement. Actual dialogs, invalid/long
arguments, formatting-helper internals, complete buffer ownership and runtime
failure behaviour remain unverified. This compares the official patch; the
local executable's separate About-string modification remains excluded from
VEG attribution as documented in the baseline. No game or API was executed.


## Removed fpuerrors startup consumer

The [x87 startup follow-up](og-modern-x87-precision.md#removed-optional-startup-exception-unmasking) now connects original slot25 `-fpuerrors` to bit25 and five conditional control-word updates. Modern empties the switch string and removes that startup sequence, while retaining the byte-identical runtime CW helper. This concerns exception masks, not arithmetic precision, and does not establish removal of every helper caller.


## Removed demo startup writes and precedence

**Verified static writes; field meanings unresolved.** The [audit script](scripts/audit_removed_demo_startup.py) and [manifest](evidence/audits/removed-demo-startup.json) retain both baseline identities, complete branch-region disassembly and selected store/gate assertions. Original slot21 `-msdemo` sets bit21 (byte `0055eb2e` mask`20`); slot20 `-e3demo` sets bit20 (same byte mask`10`). Final Modern has empty strings in both slots.

Original startup tests `-msdemo` at **`004a3b3d`** and conditionally executes `004a3b4a..004a3c22`. It then independently tests `-e3demo` at **`004a3c22`** and conditionally executes `004a3c2f..004a3d05`. This is two ordered branches, not an exclusive choice. Both branches perform these raw writes:

| Storage | Common write |
|---|---|
| `0055b041..0055b049` (exclusive end) | Eight bytes `32 33 34 38 3b 3f 40 38` |
| `00554f50` | DWORD0 |
| `00556382..00556394` (exclusive end) | Clear18 bytes through fill adapter `004e0640`, then write WORD1 at `00556388` |
| WORD locations `005562b4`, `0055628a`, `00556224`, `00556208`, `00556262` | 1 |
| WORD locations `005562b8`, `00556220`, `00556222`, `00556264`, `0055637c`, `0055620a`, `00556286`, `00556288` | 0 |

Their differing stores are:

| WORD location | `-msdemo` branch | `-e3demo` branch |
|---|---:|---:|
| `005562b6` | 1 | 0 |
| `0055621e` | 0 | 1 |

When both flagbits are set on entry to these checks, the later `-e3demo` branch overwrites those two locations. This ordering is independent of command-line argument order once both bits are set. The existing [fill-helper capture](original-modern-config-loading.md#original-header-initialization-narrows-the-migration-example) covers its preservation behaviour; the raw pointers and store values above do not by themselves establish named gameplay settings or keyboard actions.

Final Modern replaces **`004a3b3d..004a3d05` with456 NOP bytes**, removing both local startup override bodies as well as emptying their switch names. This is a separate difference from [Modern's changed save gate](original-modern-config-loading.md#removed-save-gate-belongs-to-the-original--msdemo-flag): removing these startup writes does not imply every bit21 consumer was removed. Other writes, aliases, all flag producers and user-visible demo behaviour remain pending. No demo launch, target instruction or Ghidra write was performed.


## Later demo branches also change application flow

The extended [demo audit](evidence/audits/removed-demo-startup.json) captures **original `004a3d71..004a3e34`** and **final Modern's complete application envelope `004a3db0..004a3f7d`**. These later original branches are separate from the earlier456-byte override region. They occur after original installation/media/subsystem startup calls.

Original bit21 (`-msdemo`) at `004a3d71` conditionally executes:

- WORD0 to `00554fac`, `0055500e`, `0055513c`, `0055519c`, `0055519e`, `005551a0`.
- WORD1 to `0055519a`, `005551a2`, `005551a4`.
- Load active language DWORD`006fbb4c` into EAX and call language loader `004d1750` at`004a3dcf`; see the [language comparison](original-modern-language-table.md).
- Stage pointer **`0049bfb0`** in ESI before the language-loader call, then store ESI at DWORD`0056446c` (`004a3dd4`) and call display-default routine **`00472d10`** (`004a3dda`). The stored value equals the staged pointer conditional on transitive ESI preservation across the loader. That preservation, callback contract and downstream consumers are not fully qualified here.

Original bit20 (`-e3demo`) is then tested independently at `004a3ddf`. Its body writes WORD0 to `00554fae`, `00555010`, `0055513c`, `0055519c`, `005551a0`, `005551a2`, `0055519e`, and WORD1 to `0055519a`. It clears EAX, calls race-preparation entry **`004a3690`** at`004a3e2a`, then **jumps to cleanup `004a3f08`**, bypassing ordinary state dispatch. The local zeroing with no intervening calls establishes EAX0 and EDX0 at this call; the complete callee ABI remains a separate contract. Successful race startup or completion is not implied.

If both bits are set, both later bodies execute in order; in particular, `005551a2` is written1 by the msdemo body and then0 by the e3demo body. Stores to different addresses, such as `00554fac` versus `00554fae`, do not overwrite each other. Do not conflate this with the two differing fields of the earlier branches or infer the UI meaning of adjacent WORDs.

Final Modern's complete application body has neither of these exact absolute `TEST BYTE [0055eb2e],20/10` encodings. The earlier part of the original sequence overlaps Modern's new jump table/application entry, so describing the entire later branch as a NOP deletion would be incorrect. The supported comparison is removal of these inspected direct demo gates from the replacement application body, alongside the empty named-switch slots. Other flags, aliases, callbacks and transitive demo policies remain outside this bounded negative search. No game launch or race was executed.

## Movie switch spelling changes at1.5.2

The [four-build option history](original-modern-idle-movie.md#historical-movie-option-spelling-and-the-early-title-gate) verifies switch slot11 changes from`-nomovie` in1.5.1 to`-nomovies` in1.5.2, alongside the INI key change`NoMovie`→`NoMovies`. The captured disable-bit branch and movie-mask builder remain byte-identical across that pair. This dates the observed table spelling; it does not exclude every alternative parser/alias or prove an actual launch option was consumed.
