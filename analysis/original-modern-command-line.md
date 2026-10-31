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

Argument iteration decrements the saved count before loading an argument (`004a50a7..004a50cd`). It therefore visits trailing arguments before earlier ones, excluding the executable at index zero on the ordinary path. Full duplicate-option precedence also depends on the called setter and later configuration writes; it is not assumed solely from iteration order.

**MP110-003** is statically supported by the original renderer-option table versus Modern's universal prefix route and INI bypass bit. Exact release introduction still needs the v1.1.0/predecessor binaries. The local Modern-derived executable's separate About-text edit is outside this official-baseline parser comparison.

## Remaining work

Pending: every original parameterized option, downstream semantics for each retained flag, malformed/empty/overlong arguments, duplicate driver options and actual help/driver selection on the OS/Wine. The report establishes this table and prefix mechanism, not complete command-line behavioral equivalence or runtime robustness.
