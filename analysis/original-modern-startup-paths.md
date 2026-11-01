# Original versus Modern: working directory, INI selection and data directories

## Scope and evidence

**Static startup-path comparison; no filesystem/API operations executed.** Supplied original SHA-256 `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b`; official Modern v1.6.1 SHA-256 `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline](original-modern-differences.md).

Run `python3 analysis/scripts/audit_startup_paths_difference.py` (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-startup-paths.json) records input/span hashes, API identities, 22 initialized path slots and the required/create directory tables. Raw assembly remains ignored under `analysis/captures/modern-differences/startup-paths/`. No game/Ghidra/executable/configuration changes or directory creation.

## 1. Modern explicitly attempts an executable-relative working directory

Modern helper `004a38f0..004a3937`:

1. Allocates 260 stack bytes and calls GetModuleFileNameA(NULL, buffer, 260) at `004a3908`.
2. If the returned length is zero or at least 260, returns EAX=`0xffffffff`.
3. Otherwise walks backward to the last backslash, retaining that backslash and terminating immediately after it (`004a391d..004a3927`).
4. Calls SetCurrentDirectoryA on the resulting directory at `004a392b`.
5. Returns the **directory prefix length**, not the API's BOOL result, through saved EAX (`004a3931`). Other general-purpose registers are restored by POPAD.

Startup calls this helper at `004a3e24`, compares the return with **210 (`0xd2`) unsigned**, and only proceeds at `004a3e3f` when it is no greater. The extraction-failure return therefore reaches the error branch, as does an extracted directory prefix longer than 210. It does not prove SetCurrentDirectory succeeded: the helper discards that API result and returns a length even on an API failure. There is also no local backward-scan lower-bound check; the valid executable-path/backslash precondition is not revalidated here.

This statically supports **MP140-066**, the startup attempt to use the executable directory. Effective CWD under Windows/Wine was not observed. The instruction sequence does not guarantee a permanent working directory for the entire process lifetime.

## 2. What the original comparison establishes

Original `004a38f0` is an unrelated routine, not an earlier implementation of this helper. The inspected original startup block `004a3d4a..004a3f7c` contains race/session control paths, including calls at `004a3e2a` and `004a3ef4` to `004a3690`; it contains no direct call to the original directory wrappers below. That bounded observation does not exclude indirect/startup paths elsewhere.

The original already imports SetCurrentDirectoryA and has two wrappers:

- `004e3340` clears last error, calls SetCurrentDirectoryA and diagnoses failure; tail thunk `004fce30` jumps to it. Its indirect/function-pointer reachability remains unresolved.
- `004f0260` calls the same API, returns zero on success, and delegates failure translation to `00500ff4`.

Original frontend routine `004475a0` saves CWD through `004e33a0` at `00447689`, calls `004f0260` at `00447696` with a path from `007a2f34`, rebuilds its file-stem list, then calls the wrapper again at `004477f0` with the saved directory. This is a scoped directory switch/restore, not proof of executable-relative startup policy.

Therefore the verified difference is **Modern's explicit new startup hook**, not “the original never changes CWD” or “the API was newly imported.” Such universal claims are contradicted or unsupported by the original witnesses.

## 3. Executable-basename INI selection is independent of CWD success

Startup calls `004a6e10` at `004a3e3f`, before the [settings loader](original-modern-configuration.md). The helper writes a path into buffer **`007a263c`**:

- GetModuleFileNameA(NULL, buffer, 260) at `004a6e1e` supplies the executable path.
- It scans backward until the last dot or a directory backslash. At a filename dot, it replaces the suffix with `ini` plus NUL (`004a6e3b`).
- File check `004f91ec` accepts only successful attributes with directory bit `0x10` clear. If that candidate exists as a non-directory, retain it.
- Otherwise it walks back to the filename position and copies literal `nfs3.ini` from `0053f5d4` (`004a6e4c..004a6e63`). A filename without an extension also takes this fallback. The fallback's existence is not checked here.

Examples derived from the string operations, not filesystem tests:

| Valid executable path and candidate state | Selected INI path |
|---|---|
| `C:\game\race.exe`, `race.ini` exists as a file | `C:\game\race.ini` |
| `C:\game\race.exe`, candidate missing or a directory | `C:\game\nfs3.ini` |
| `C:\game\race` with no extension | `C:\game\nfs3.ini` |
| GetModuleFileName returns zero | Relative fallback `nfs3.ini` |

For an ordinary valid full executable path, this produces an absolute INI filename even if the earlier CWD attempt failed. It does not just search the inherited working directory. The integer/string profile readers **push the immediate buffer address `007a263c`**, rather than loading a pointer from that location.

This helper does not itself reject a returned length of 260, guarantee capacity for every suffix replacement, or validate all truncated/API-failure cases. The preceding directory-length gate is not a complete filename-length/capacity proof. These are implementation boundaries, not observed failures; no long-path test was run.

This statically supports **MP150-041**, the executable-name INI preference/fallback. Intermediate release provenance and all filesystem edge cases remain untested.

## 4. Path slots and directory preparation

Modern `004a6ec4` copies 22 consecutive NUL-terminated strings from file-backed source `0053f42c` into **128-byte slots** beginning at `007a27b4`. These are initialization writes into runtime storage; interpreting the destination addresses as file-backed strings would be incorrect. Several slots can subsequently change, notably the speech/language path. The manifest lists all initial values without asserting they are final runtime contents.

Startup calls directory routine `004a3984` at `004a3e6b`. The first pointer table (`004a3938`) requires 13 existing directories, resolving these default slot values:

- `gamedata\tracks`, `gamedata\carmodel`, `gamedata\render\pc`, `gamedata\dashhud`;
- `gamedata\audio\pc`, `gamedata\audio\sfx`, `gamedata\audio\speech`;
- `fedata\menus`, `fedata\art`, `fedata\text`;
- `fedata\art\slides`, `fedata\art\track`, `fedata\art\showcase`.

The second table (`004a3970`) calls `004f9214` for four destinations, in order:

1. `.\fedata\save\`
2. `.\fedata\stats\`
3. `.\fedata\config\`
4. `.\fedata\stats\carspecs\`

That helper returns success if the directory already exists, otherwise calls CreateDirectoryA through `004f9204`. It is not a generic recursive mkdir; ordering creates `stats` before `stats\carspecs`. Failure in either table returns zero from `004a3984`; startup tests it and enters its error path at `004a3e74`. This verifies the concrete Modern mechanism relevant to **MP140-065**, not automatic creation of every conceivable game-data directory or original-version behavior at all other paths.

Paths are relative unless a preceding initialization/configuration path changes them. No real directory was created or removed for this audit.

## 5. Consequences for earlier chapters

- **INI:** complete ordinary producer-to-reader linkage is now traced. Original setting-by-setting registry migration and later aliases/writes remain separate.
- **Screenshots:** [the worker](original-modern-screenshots.md) uses relative `.\screenshots\`. Successful startup CWD selection anchors that ordinary path to the EXE directory. Because the API result is ignored and later CWD changes are not excluded, the relative prefix is not an unconditional absolute-path guarantee.
- **HUD:** original [preset loading](original-modern-hud-layout.md) uses prefix slot `007a29b4`, whose Modern default path is `.\gamedata\dashhud\`. This default does not independently authenticate the original asset set or original runtime prefix contents.

Next: original complete installation/path discovery, live file/API edge cases if needed, and later CWD/path-buffer writers. Preserve ignored return values and fallback behavior during reconstruction rather than silently substituting filesystem “improvements.”

## Release-note correspondence: root-path diagnostic

MP161-007 bundles two diagnostics. The root-directory part has a verified branch and message: unsigned EAX greater than210 at `004a3e29` takes `004a3e30`, supplies string `0053d049` and calls fatal diagnostic helper `004b570c` at `004a3e35`. The exact string says the game root path must be no longer than210 characters. The audit now asserts both the22-byte branch/diagnostic sequence and the full message against the official hash-pinned EXE. The return value includes the retained directory separator; it is a byte-count path-prefix contract of this ANSI helper, not a Unicode character-count guarantee.

As established above, extraction failure (`ffffffff`) reaches the same message, so the wording alone does not prove the actual cause was an overlong path. Successful CWD change, full suffix capacity, displayed dialog behavior and release-specific introduction remain unverified. The original comparison documents a different startup-path policy; it does not establish absence of every analogous diagnostic elsewhere. The bundled missing-driver message requires its own branch-to-message mapping before the whole release-note item can be accepted. This is partial static support, with no long-path/API/game execution.

## Config path history: root-relative then restored

The [historical audit](scripts/audit_config_path_history.py) pins author-hosted1.1.0 and1.2.0 archives, their EXEs, readmes, complete path initializers, callsite and config-formatting witnesses in [its manifest](evidence/audits/config-path-110-120.json). Run `python3 analysis/scripts/audit_config_path_history.py`; first acquire missing archives from the recorded URLs into their ignored manifest paths. V1.1.0's internal banner calls it **Widescreen Patch** and uses `readme-en.txt`;1.2.0 says **Modern Patch** and uses `readme_en.txt`. The differing names are retained rather than normalized into unsupported artifact identity claims. No archive contents were installed or executed.

| Build | Path initialization | Config slot17, address `007a3034` | Derived ordinary filename |
|---|---|---|---|
|1.1.0 | `004a6f0c..004a6f2d`;24 strings from `0053ec2c` | `.\` | `.\config.dat` |
|1.2.0 | `004a6f04..004a6f6e`;same24-slot copy scheme, then language-path work | `.\FeData\Config\` | `.\FeData\Config\config.dat` |
| Final1.6.1 | Previously audited `004a6ec4..004a6f2e`;22 strings from `0053f42c` | `.\fedata\config\` | `.\fedata\config\config.dat` |

The two early initializers copy NUL-terminated strings into128-byte slots starting `007a27b4`. Their caller at `004a6e36` targets the respective initializer. The config read witness at `004729aa` pushes that slot and format `%sconfig.dat` (`0053b00c`), then calls formatter `004df690`; the saved complete config-save envelope uses the same slot/format. Thus the changed initializer value has a concrete config consumer. These are default/dataflow-derived paths; effective CWD, later writers, API success, case-sensitive host filesystem behaviour and actual file I/O were not observed.

MP120-013's return to the original-style FeData/Config destination now has **bounded historical static support** from the1.1.0→1.2.0 transition. MP100-044's earlier root move has partial historical support because1.1.0 exhibits the root-relative config path; v1.0.0 introduction and the supplied original's complete prefix producer have not been traced here. Reading MP100-044 as a statement about the final executable would be wrong: a later release reverses the path policy.

The final22-slot layout also explains the player-path builder follow-up in the [config report](original-modern-config-loading.md#executable-update-deletion-config-and-both-player-specifications). Final slot18 (`007a30b4`) contains `.\fedata\stats\carspecs\`, so Modern's removal of the explicit `carspecs\` append avoids duplicating that component under the initialized default. In the early24-slot layouts, slot18 instead contains `.\FeData\Audio\`. Applying the final slot meaning to an earlier EXE would therefore misidentify the path. This establishes the final default player-spec prefix; it does not prove absence of later mutation, scratch-buffer aliasing or other callers.

## Early four-directory installation check versus final preparation tables

**Verified static history and helper contracts; no filesystem operations executed.** The [directory-history audit](evidence/audits/install-directory-history.json), reproduced with `python3 analysis/scripts/audit_install_directory_history.py`, pins author-hosted1.1.0 and official final EXEs. The original/final startup-policy comparison remains separate above; original same-address bytes are not treated as this early Modern checker.

| Version | Required existing entries | Additional creation stage |
|---|---|---|
|Modern1.1.0 |Four static strings: `.\GameData\Tracks\`, `.\GameData\CarModel\`, `.\FeData\Art\`, `.\FeData\Text\` |None inside this complete local checker |
|Final1.6.1 |Thirteen runtime path-slot pointers, listed above |Four save/stats/config/carspecs entries, listed above |

Early pointer table`004a3998..004a39ac` contains four direct string addresses plus a zero terminator. Complete38-byte checker`004a39ac..004a39d2` loads each path into EDI and calls complete33-byte predicate`004a3974..004a3995`. That predicate pushes the path for imported GetFileAttributesA, rejects`ffffffffh`, then requires attribute bit10h. A regular file without the directory bit therefore fails, even if a path exists. The checker stops at its first zero result and returns0; passing all four returns1. It neither reads asset contents nor creates directories in this local body.

Final uses the same attribute-success/directory-bit rule through complete helpers`004f915e..004f916a` and`004f916c..004f9184`. Its complete66-byte table walker`004a3984..004a39c6` checks all required entries first, then the preparation table; either stage stops on the first failure. These are runtime buffers populated by prior initialization, not direct file-backed path strings.

For preparation, complete21-byte helper`004f9214..004f9229` first tests whether the directory exists. If true, it returns1 without CreateDirectoryA. If false, it passes the same saved path to complete14-byte wrapper`004f9204..004f9212`, supplying null security attributes, and returns that API result. It does **not** distinguish a missing path from other attribute failures, recursively create parents, retry or requery after failed creation. Consequently an API-reported create failure remains a local failure even if another actor creates the path between check and create. That is a conditional code consequence, not an observed race. No rollback of directories created earlier in the table occurs in this walker.

**MP100-041 advances to partial historical support:** early Modern has a concrete four-directory installation check, and final expands the inspected mechanism to thirteen prerequisites plus four preparations. The exact1.0.0 introduction and intermediate expansion date are not established here. The existing MP140-065 creation mechanism remains separately qualified. A passing directory check does not prove a complete installation, readable/correct assets, writable existing destinations, successful later I/O or startup completion. Effective CWD, slot overrides, concurrent changes, error diagnostics and all original installation-discovery paths remain separate requirements. No directory, executable, saved Ghidra database or maintained C was changed.
