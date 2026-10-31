# Original versus Modern: idle movie admission and available-file cycling

## Scope

Static paired comparison of controller **`00496200`**, using the [baseline identities](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_idle_movie_difference.py`; the [manifest](evidence/audits/original-modern-idle-movie.json) retains complete original `00496200..004962fd` and Modern `00496200..004962c2` envelopes, the Modern availability builder and file-attribute wrappers, and identical timer/input helper bodies. No movie playback, window interaction, instruction probes or Ghidra writes.

## Availability replaces a single disable gate

Original begins by rejecting nonzero gate global `007a1fdc`, then nonzero `006fbb54`. Modern instead requires **`[007a2768] & 0x0e != 0`**, then also rejects nonzero `006fbb54`. This requires at least one demo bit1..3, rather than accepting a title-only availability mask.

Modern mask builder **`004a2f90..004a2ffc`** first clears the entire DWORD `007a2768`. If **bit11 of `0055eb2c`** is set, it skips all file checks and returns zero. The [settings-loader analysis](original-modern-startup-policy.md#3-current-settings-exact-defaults-and-immediate-effects) independently establishes that the final executable’s **`NoMovies`** key sets that bit for a nonzero setting. The release notes call the option NoMovie; this chapter preserves the actual loader key instead of silently treating those spellings as proven aliases.

Otherwise the builder checks directory `007a2cb4`, appends each of four names and sets the corresponding bit only for a file attribute result that exists and is not a directory. Its helpers call **GetFileAttributesA through IAT `00534520`**, distinguish invalid attributes `ffffffff` and directory bit10h, and preserve the loop’s ECX/EDX in the attribute wrapper. These are file-availability checks, not decoder success tests.

| Bit/index | Modern filename pointer | Name |
|---:|---|---|
| 0 | `0053beac` | `titleav.mad` |
| 1 | `0053beb8` | `demoav1.mad` |
| 2 | `0053bec4` | `demoav2.mad` |
| 3 | `0053bed0` | `demoav3.mad` |

Modern’s table at **`004961f0`** holds these filename pointers. Original’s same-address table holds **code targets** for its four-way switch; its case arms load the corresponding filename pointers. Table addresses cannot establish identical data types across versions. Modern’s builder has a direct startup call at `004a3e66`; the expanded startup witness and its ordering are recorded below. No claim is made that changing the setting dynamically rebuilds the mask immediately.

## Idle timer and inactive application gate

Both versions compare two current input-state values `0055e5e4/e8` with remembered values `0055e550/54`. Changes copy the new values and reset idle timestamp `0055e548` through **`004961e0`**. That complete helper is identical and copies current counter `0079c1a4`. Both compare the wrapping subtraction `current−timestamp` against signed **`0x1400` (5120)** before playing. This chapter does not assign seconds to those raw counter units or generalize the signed comparison across arbitrary wraparound states.

Original also calls **`004438b0`**, which simply returns byte `00558b10` in AL, and resets the timer when nonzero before proceeding with the remaining checks. Modern moves that check after the unchanged-input comparison and adds **`009f3d4c != 0`** as a prerequisite. Inactivity or nonzero returned input byte branches to timestamp reset at `004962b6`, then returns0. It therefore keeps resetting the timer while that gate is closed, rather than merely postponing an already-expired playback attempt.

The [window-handling comparison](original-modern-window-handling.md) establishes the producer: Modern’s WM_ACTIVATEAPP handler stores raw wParam at `009f3d4c`, and window creation/destruction also set/clear it. Thus the verified gate is **application activation**, which is broader than an explicit minimized-window query. No IsIconic call appears in this retained controller; the release-note claim about minimized demos is partially supported by the activation gate, without assuming every driver/minimize event sequence was tested.

## Selection and return behavior

Once admitted and timed out, Modern stops current music through `004109d0`, increments the low byte of stored selector `0055e54c`, masks that byte with3, and tests the corresponding availability bit. It repeats until it finds a set bit, stores the selector, loads the filename pointer and calls `004960e0`. The admission mask guarantees a set bit among1..3 for ordinary selector state0..3. Only AL is incremented/masked, so arbitrary nonzero upper selector bits must not be silently normalized by a reconstructed full-width `selector = (selector+1)&3`.

Original selects the current value first through a switch for unsigned values0..3; after playback it increments and uses signed IDIV4 for the next selector. Modern increments before selection and skips unavailable files. These are separate ordering and availability changes, not just a rewritten switch.

Both paths then request menu music through `004104f0` with operation22, configured menu level `006fbbe8` and EBX=0, reset the timestamp and return1. That return denotes taking the playback-request path; no aggregate decode/audio success check is established. Early rejection paths return0. The [movie-volume comparison](original-modern-movie-volume.md) separately documents the menu-level parameter override inside playback.

## Catalog conclusions and follow-up

- **MP140-029:** partial static support. NoMovies bit11 forces availability mask0, and the idle controller requires demo availability. Local startup ordering is verified below; live option changes and all application paths remain unverified.
- **MP140-030:** partial static support. An inactive application resets the idle timer; the Windows activation producer is independently documented. Minimize/restore behavior under particular drivers and runtime timing remain untested.
- Additional verified differences: file-existence filtering, switch-to-filename table conversion and increment-before-selection.

The follow-up below retains startup ordering, intro admission and the playback wrapper. The complete purpose and producers of gate global `007a1fdc`, live mask rebuilding and decoder success remain separate follow-ups.

## Follow-up: startup ordering and title admission

The expanded Modern startup witness **`004a3e3f..004a3e6b`** establishes this local sequence:

1. Calls `004a6e10`, `004a6e68`, then path initialization `004a6ec4`.
2. Calls settings loader **`004b5580`** at `004a3e4e`.
3. Calls command-line parser **`004a5080`** at `004a3e59`; a zero result branches to outer exit `004a3f6c`.
4. On nonzero, calls movie-mask builder **`004a2f90`** at `004a3e66`.

The [command-line comparison](original-modern-command-line.md) establishes Modern’s `-nomovies` table entry at index11 and matching flag-bit write; the [settings-loader report](original-modern-startup-policy.md) establishes the NoMovies INI branch. Thus both parsed sources precede the builder on this path and use bit11. This is not proof of runtime rereading, every alternate startup path or successful settings/resource initialization.

The frontend setup prefix is retained from entry **`004730d0`**, ending at the reviewed movie-admission continuation (original `00473169`, Modern `0047314d`). Original checks `006fbb54 == 0`, abort flag `0055e88c == 0`, byte `0055eb2d & 8 == 0` (the same DWORD bit11), and `0055b03c != 0` before requesting `titleav.mad`. Modern instead reaches a check of `0055b03c != 0` followed by **mask bit0** at `00473135`, then requests the same filename at `00473143`. It resets the idle timestamp afterward; original also explicitly writes movie selector1 after its request. These are caller-prefix differences, not equivalence of every setup path. Other setup policy changes remain outside this bounded movie branch review.

## Follow-up: playback wrapper, relocated path and CPU-tier input

The paired **`004960e0..004961db`** wrapper envelope is now retained. Both versions first reject nonzero **`007a1fdc`**, concatenate a movie-directory buffer with the requested filename, check existence through `004e0e60`, prepare playback, call `00495bc0`, then restore state. Both return1 even on their early rejection route, so callers cannot treat the wrapper’s result as proof that a movie was decoded or played. It contains no direct bit11 or mask test; those policies are enforced by the reviewed callers and mask builder.

The directory source operand at **`00496104`** changes from original **`007a32b4`** to Modern **`007a2cb4`**. Aside from that operand byte, the prefix through `0049616c` is byte-identical; the suffix `004961ab..004961db` is also identical. Modern later uses the old address `007a32b4` as its RNG state, documented in the [playlist report](original-modern-music-selection.md#modern-playlist-seeding-and-race-load-update-placement). This is a concrete global-storage reuse, not evidence of a shared path/RNG union in either single version. The buffer contents and all initialization writes are not reconstructed by this operand comparison alone.

The middle block changes its interpretation of **`005652a4`**. Original compares it with133,000,000 and200,000,000 to choose ECX1,2,3; below the first threshold it also forces local field+7eh to1. Modern computes the signed value minus1, clamps ECX to1..3 and forces that local field when the unclamped result is at most1. The existing [CPU-tier analysis](original-modern-cpu-tier.md) verifies the producer changing from a frequency-like estimate to a small feature/family score. This identifies the formerly unnamed second consumer as the movie wrapper’s ECX playback input; its downstream display-conversion use is traced below, while visual-quality acceptance remains unverified. It offers partial static support for **MP100-019** without claiming a measured improvement or historical introduction proof.

Remaining work: precise original rating accuracy, decoder consumption of ECX/local field, producers and complete semantics of `007a1fdc`, and runtime movie acceptance. No new game, decoder or instruction probes were run.

## Follow-up: CPU tier reaches display conversion, with unchanged consumers

The audit now retains and verifies byte equality for five complete downstream bodies:

| Body | Role established by the inspected instructions |
|---|---|
| `004957a0..00495852` | Store dimensions/placement, allocate frame-buffer slots and forward display setup arguments |
| `004df1f0..004df2af` | Store display inputs and conversion selector; choose presentation backend mode |
| `004df2b0..004df306` | Dispatch presentation, including raster conversion fallback |
| `004dee80..004df1e5` | Surface presentation and destination-rectangle construction |
| `004fdc90..004fe1c9` | Clipped raster conversion with selector-specific branches |

In the movie body, the incoming tier ECX is saved at `[EBP−30h]`. At **`00495cf5..00495cf8`** it is pushed as the third stack argument to `004957a0`; the immediately preceding first argument is literal6, the number of frame-buffer slots. Distinguishing these stack positions avoids misidentifying tier1..3 as the slot count. With that callee’s three-register prologue, the tier is at **`[EBP+18h]`**, while the literal6 is at `[EBP+10h]`.

`004957a0` forwards tier as the first stack argument to `004df1f0`. There it is loaded from **`[EBP+10h]`** at `004df202` and stored to **`008ca2cc`** at `004df233`. The second stack argument controls a separate backend-capability check. The tier is therefore a stored display-conversion input; it is not consumed by this setup chain as a frame-duration or frame-skip interval.

On raster fallback, `004df2b0` reads `008ca2cc` at `004df2d6`, pushes it, then pushes the stored height and calls `004fdc90` at `004df2f5`. The converter’s large local frame places the selector at **`[ESP+0xa5c]`**. It accepts0,1,2,3, selecting scale factor1 for0 and2 for1..3; unsupported values return−1. The 15/16-bit destination-format gate is separate and can return−2.

After clipping, nonzero selector3 takes a distinct row-processing branch at `004fdee9`, while selectors1/2 share the branch at `004fe06e`; selector2 additionally enters the pass gated at `004fe0d0`. Mode3 calls `004fd892` and `004fd61c` on its shown row path; the shared1/2 branch calls `004fd6ef`. The mathematical filtering performed by those leaf routines is not reconstructed here, so these modes are not given guessed labels such as nearest-neighbor or bilinear.

The surface path also reads this same selector at `004def55` and `004df0c7`, choosing multiplier1 forzero and2 fornonzero when building destination extents. Ordinary movie tiers1..3 therefore share that size multiplier even though their raster processing branches differ. Surface-driver acceptance and the exact choice between backend paths remain outside this static mode mapping.

**Result:** the changed original-frequency/Modern-score policy selects a display-conversion mode through an otherwise byte-identical downstream chain. This narrows MP100-019’s mechanism, while original rating accuracy, actual raster-filter quality, driver behavior and measured visual improvement remain unresolved. No decoder quality, cadence or pixel-equivalence claim follows solely from the tier numbers.
