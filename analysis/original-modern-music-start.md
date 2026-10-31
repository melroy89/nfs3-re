# Original versus Modern: music start changes and retained volume/fade code

## Scope and evidence

Static comparison of the supplied original/backup and official Modern v1.6.1. Fingerprints and limits are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_music_selection_difference.py`; the [manifest](evidence/audits/original-modern-music-selection.json) now retains both full start-routine spans, stop/start/level/fade helpers, and asserts the retained ranges listed in that manifest. No audio, game or instruction probes were executed.

This extends the [selection comparison](original-modern-music-selection.md). A changed callsite and an unchanged backend body are separate evidence; neither alone proves an audible fix.

## Old menu choice is removed from the common start routine

Both `004104f0` entries take operation in EAX, a level argument in EDX, and context flag in EBX. The first **143 bytes `004104f0..0041057e`** are identical: save operation/level, set local 1500, normalize operation 99 to zero, reset state, check admission and operation upper bound, then set context flags.

Original next performs menu choice at `0041057f..004105d4`:

- Setting `006fbbec=0`: call `004e0d88`, take unsigned remainder modulo 7, add 1, and store the low-byte result at `005525fc`.
- If that byte equals 6, replace it with 2. Under ordinary remainder semantics the effective IDs are **1,2,3,4,5,7**, with ID 2 receiving two remainder outcomes. Uniform helper input is not established, so this is outcome mapping rather than a measured probability distribution.
- For nonzero setting, copy its low byte to the same field.
- Command/config flag bits at `0055eb2e` bits 4/5 or `0055eb2f` bit 0 can force that byte to 1.

Modern replaces this whole block with `JMP 004105d5` and NOP-filled storage. Its menu operation branch later calls `0040ffb4` at `0041060b`, as traced in the selection report. Thus the change includes removal of this local flag-forced choice, not just adding two masks. Whether those flags have other effects elsewhere is not excluded.

The same address **`005525fc`** also changes use: the old block stores a selected byte, whereas the new helper uses a DWORD cursor into its cycle table. Reusing an old name/type would misrepresent this state.

## Retained tail and helper bodies

The entire **250-byte tail `004106b8..004107b1`** is identical. It appends style-dependent suffixes, formats paths, requests a map/resource, starts the stream and makes level/fade calls before setting active global `005525a0=1`. This is instruction equality, not proof that the same assets, inputs or provider state reach it.

At the tail:

| Callsite | Retained input setup and call |
|---|---|
| `00410768` | EAX=0, EDX=formatted path, EBX=local 1500; call `004e73d0` |
| `00410772` | EAX=`[00552598]`; call `004e6f0c` |
| `0041077e` | EAX=1, EDX=0; call `004e7470` |
| `0041078e` | EAX=127, EDX=saved incoming level; call `004e73d0` |
| `00410798` | EAX=100; call `004e7470` |

The first row is reported literally: `004e73d0`'s inspected body consumes EAX as a numeric level and explicitly saves/restores EDX. A formatted path in EDX at that call does not make it a path-taking function. Register contracts take precedence over guessed decompiler prototypes.

The evidence script also verifies these **complete bodies** are identical:

- `004109d0..00410a3b`: stop/release path, 108 bytes.
- `004e6f0c..004e705b`: stream-start backend, 336 bytes.
- `004e73d0..004e7465`: level setter including diagnostic branch, 150 bytes.
- `004e7470..004e74e0`: fade helper, 113 bytes.

## What the level setter actually consumes

`004e73d0` pushes EDX and copies EAX into EDX. When audio state byte `00a09af4` is zero it returns -10. Otherwise it checks the copied value against signed 0..127, taking a diagnostic path for values outside that range. It calls `00500e20`, stores DL at `00a09af5`, visits 16 records of stride 0x60, conditionally invokes `005014a0/00501540`, calls `00500e7c`, then returns zero on the shown ordinary path.

This establishes EAX as the supplied level. The incoming EDX preserved on the stack is not used as a second level parameter here. The full contracts of the deeper helpers and record fields remain outside this comparison. The code's parameter usage must not be rewritten to match its callers' apparent intent.

## Limits of the volume/fade claims

**MP153-001**, different race music volume each race: the follow-up below now establishes removal of a track-dependent level adjustment in a second stream-start routine and two level-control paths. The unchanged common-start backend alone was insufficient to locate this policy change. The claim has bounded static support and remains partial until complete call coverage and audible results are established.

**MP153-006**, double fading when pressing Race: the selection report establishes restart/continuation gate changes, but a complete audio-settings action-to-Race caller trace is still required. Do not promote a plausible connection to a verified fix.

Next evidence: trace every relevant volume producer/caller, backend dependencies and track/map assets, then compare observed levels only if a runtime phase is authorized. No audio was played and no suspected original behavior was silently corrected.

## Follow-up: circuit-dependent Techno level adjustment removed

The expanded audit retains the second start routine, **`004107c0`** (original envelope ends `004109cc`, Modern `0041099b`), level-update routine **`00418620`**, toggle routine **`004187e0`**, complete backend **`004e8b60..004e8bce`**, and the file-backed ten-DWORD table **`005525d0..005525f8`**. No sound or instruction probes were run.

| Circuit index | Original signed adjustment | Modern file-backed value |
|---|---:|---:|
| 0,2,4,6 | 15 | 0 |
| 1,5 | 6 | 0 |
| 3,7,8,9 | 0 | 0 |

These are initial image bytes, not proof of every subsequent write or a valid circuit domain extending to9. Existing selected-circuit work establishes ordinary circuit IDs separately. The array's index here is **selected circuit `006fd4ac`**, not playlist index `005525f8`; the two must not be conflated when translating the policy to C.

Original code applies the adjustment when **music setting `006fbbe4 == 1` OR style state `00552854 == 1`**. Its original choice list labels setting1 Track default (Techno), and style1 selects `tech`, as traced in the [selection report](original-modern-music-selection.md). Otherwise it passes the configured level unchanged. The predicate tests state, not the successfully opened asset’s identity; restriction flags can affect filename selection elsewhere.

| Path | Original level computation | Modern |
|---|---|---|
| Stream start `00410976..004109b7` | Under predicate, subtract table[selected circuit] from saved incoming EDX; clamp signed-negative result to0; call `004e7470` with EAX=100, EDX=result | `00410976`: load saved EDX directly; EAX=100; call at `00410981` |
| Level update `00418620` | If byte `00552908` is nonzero, apply predicate and subtraction to configured race level `006fbbf0`; clamp signed-negative; call `004e8b60` | Same admission byte, direct configured level at `00418637`, call `0041863c` |
| Toggle `004187e0`, enabling branch | Apply predicate/subtraction/clamp to configured race level, call `004e8b60`, set enabled byte1 | Direct configured level at `004187f8`, call `004187fd`, set byte1 |

On the toggle’s disabling path both versions send level0 to `004e8b60` and clear the enabled byte; Modern refactors the final byte assignment through AL. Level update retains an earlier EAX=120 call to `004e73d0` before checking that byte. These retained operations prevent mistaking the patch for removal of all level management.

For ordinary configured level80 and initial table values, the old adjusted backend inputs can be65,74 or80 depending on circuit; Modern supplies80 in these paths. For level5, old adjusted inputs become0 for adjustments15/6, whereas Modern supplies5. These are arithmetic examples derived from instructions, not executed audio measurements. Original subtraction wraps at32 bits, then `TEST/JGE` checks the signed result; the shorthand `max(0, level−adjustment)` is scoped to normal small nonnegative inputs. A C translation must not introduce signed-overflow undefined behavior or silently extend that shorthand to arbitrary machine inputs.

Backend `004e8b60` is byte-identical in both executables: it checks audio-ready byte `00a09af4`, accepts signed EAX0..127, stores AL at target byte `00564702`, forwards stream handle `00564690` and level to `004e95fc`, then returns0 on the ordinary path. It saves/restores incoming ECX/EDX. The already-retained `004e7470` likewise validates EDX0..127, stores DL to the same target byte and forwards the request to `004e9420`; its EAX input is passed onward separately. Exact temporal/backend semantics remain outside this bounded conclusion.

A direct Modern caller at **`0043812a`** supplies configured race level `006fbbf0` as EDX, selected circuit as EAX and EBX=1 for settings>2, otherwise0. The previously retained outer race envelope has another direct call at `004a37c1`. The new evidence therefore identifies a plausible code-level mechanism for **MP153-001**, without establishing every control path, historical introduction version or audible loudness. **MP153-006** still needs the audio-settings-to-Race transition trace; it is not solved by finding a separate level adjustment.
