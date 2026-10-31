# Original versus Modern: idle movie admission and available-file cycling

## Scope

Static paired comparison of controller **`00496200`**, using the [baseline identities](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_idle_movie_difference.py`; the [manifest](evidence/audits/original-modern-idle-movie.json) retains complete original `00496200..004962fd` and Modern `00496200..004962c2` envelopes, the Modern availability builder and file-attribute wrappers, and identical timer/input helper bodies. No movie playback, window interaction, instruction probes or Ghidra writes.

## Availability replaces a single disable gate

Original begins by rejecting nonzero `007a1fdc`, then nonzero `006fbb54`. Modern instead requires **`[007a2768] & 0x0e != 0`**, then also rejects nonzero `006fbb54`. This requires at least one demo bit1..3, rather than accepting a title-only availability mask.

Modern mask builder **`004a2f90..004a2ffc`** first clears the entire DWORD `007a2768`. If **bit11 of `0055eb2c`** is set, it skips all file checks and returns zero. The [settings-loader analysis](original-modern-startup-policy.md#3-current-settings-exact-defaults-and-immediate-effects) independently establishes that the final executable’s **`NoMovies`** key sets that bit for a nonzero setting. The release notes call the option NoMovie; this chapter preserves the actual loader key instead of silently treating those spellings as proven aliases.

Otherwise the builder checks directory `007a2cb4`, appends each of four names and sets the corresponding bit only for a file attribute result that exists and is not a directory. Its helpers call **GetFileAttributesA through IAT `00534520`**, distinguish invalid attributes `ffffffff` and directory bit10h, and preserve the loop’s ECX/EDX in the attribute wrapper. These are file-availability checks, not decoder success tests.

| Bit/index | Modern filename pointer | Name |
|---:|---|---|
| 0 | `0053beac` | `titleav.mad` |
| 1 | `0053beb8` | `demoav1.mad` |
| 2 | `0053bec4` | `demoav2.mad` |
| 3 | `0053bed0` | `demoav3.mad` |

Modern’s table at **`004961f0`** holds these filename pointers. Original’s same-address table holds **code targets** for its four-way switch; its case arms load the corresponding filename pointers. Table addresses cannot establish identical data types across versions. Modern’s builder has a direct startup call at `004a3e66` retained as a five-byte call witness; full caller ordering is outside this audit’s retained spans. No claim is made that changing the setting dynamically rebuilds the mask immediately.

## Idle timer and inactive application gate

Both versions compare two current input-state values `0055e5e4/e8` with remembered values `0055e550/54`. Changes copy the new values and reset idle timestamp `0055e548` through **`004961e0`**. That complete helper is identical and copies current counter `0079c1a4`. Both compare the wrapping subtraction `current−timestamp` against signed **`0x1400` (5120)** before playing. This chapter does not assign seconds to those raw counter units or generalize the signed comparison across arbitrary wraparound states.

Original also calls **`004438b0`**, which simply returns byte `00558b10` in AL, and resets the timer when nonzero before proceeding with the remaining checks. Modern moves that check after the unchanged-input comparison and adds **`009f3d4c != 0`** as a prerequisite. Inactivity or nonzero returned input byte branches to timestamp reset at `004962b6`, then returns0. It therefore keeps resetting the timer while that gate is closed, rather than merely postponing an already-expired playback attempt.

The [window-handling comparison](original-modern-window-handling.md) establishes the producer: Modern’s WM_ACTIVATEAPP handler stores raw wParam at `009f3d4c`, and window creation/destruction also set/clear it. Thus the verified gate is **application activation**, which is broader than an explicit minimized-window query. No IsIconic call appears in this retained controller; the release-note claim about minimized demos is partially supported by the activation gate, without assuming every driver/minimize event sequence was tested.

## Selection and return behavior

Once admitted and timed out, Modern stops current music through `004109d0`, increments the low byte of stored selector `0055e54c`, masks that byte with3, and tests the corresponding availability bit. It repeats until it finds a set bit, stores the selector, loads the filename pointer and calls `004960e0`. The admission mask guarantees a set bit among1..3 for ordinary selector state0..3. Only AL is incremented/masked, so arbitrary nonzero upper selector bits must not be silently normalized by a reconstructed full-width `selector = (selector+1)&3`.

Original selects the current value first through a switch for unsigned values0..3; after playback it increments and uses signed IDIV4 for the next selector. Modern increments before selection and skips unavailable files. These are separate ordering and availability changes, not just a rewritten switch.

Both paths then request menu music through `004104f0` with operation22, configured menu level `006fbbe8` and EBX=0, reset the timestamp and return1. That return denotes taking the playback-request path; no aggregate decode/audio success check is established. Early rejection paths return0. The [movie-volume comparison](original-modern-movie-volume.md) separately documents the menu-level parameter override inside playback.

## Catalog conclusions and follow-up

- **MP140-029:** partial static support. NoMovies bit11 forces availability mask0, and the idle controller requires demo availability. Full startup mask-builder ordering and live option changes remain outside the retained caller scope.
- **MP140-030:** partial static support. An inactive application resets the idle timer; the Windows activation producer is independently documented. Minimize/restore behavior under particular drivers and runtime timing remain untested.
- Additional verified differences: file-existence filtering, switch-to-filename table conversion and increment-before-selection.

Next: retain the mask builder’s startup ordering and intro consumer, compare playback admission `004960e0`, and inspect any relation between old disable global `007a1fdc` and startup flags. Preserve those unknowns independently of the documented final controller changes.
