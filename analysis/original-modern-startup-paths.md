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
