# Original versus Modern: music start changes and retained volume/fade code

## Scope and evidence

Static comparison of the supplied original/backup and official Modern v1.6.1. Fingerprints and limits are in the [baseline](original-modern-differences.md). Reproduce with `python3 analysis/scripts/audit_music_selection_difference.py`; the [manifest](evidence/audits/original-modern-music-selection.json) now retains both full start-routine spans, stop/start/level/fade helpers, and asserts six identical ranges. No audio, game or instruction probes were executed.

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

**MP153-001**, different race music volume each race: this investigation has not yet located a changed low-level volume or fade algorithm. The bodies above and their final call sequence are retained. Changed upstream state/selection, other callers, deeper callees/data or asset changes can still alter volume. The claim remains unresolved; equal bodies neither prove the fix nor disprove an effect elsewhere.

**MP153-006**, double fading when pressing Race: the selection report establishes restart/continuation gate changes, but a complete audio-settings action-to-Race caller trace is still required. Do not promote a plausible connection to a verified fix.

Next evidence: trace every relevant volume producer/caller, backend dependencies and track/map assets, then compare observed levels only if a runtime phase is authorized. No audio was played and no suspected original behavior was silently corrected.
