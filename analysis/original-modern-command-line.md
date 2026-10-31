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
