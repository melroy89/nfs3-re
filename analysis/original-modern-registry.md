# Original versus Modern: retained and replaced registry paths

## Evidence and scope

**Verified static instructions for the hash-pinned supplied original and official Modern v1.6.1; no registry or target execution.** Baseline identities are in the [configuration comparison](original-modern-configuration.md). Reproduce with `python3 analysis/scripts/audit_registry_difference.py`; the [manifest](evidence/audits/original-modern-registry.json) retains import identities, executable-section direct-call candidates, exact strings and paired disassembly/body hashes. Raw captures are ignored under `analysis/captures/modern-differences/registry/`.

Both executables still import `RegCloseKey`, `RegFlushKey`, `RegOpenKeyExA` and `RegQueryValueExA` at the same four IAT addresses `00534464..00534470`. Modern adds INI readers; it does **not** eliminate registry imports or all registry-reading instructions. A scan for direct `CALL [IAT]` encodings finds **15 original versus 6 Modern** open/query sites. The inspected sites disassemble as calls, including their CS prefixes. This is a bounded encoding inventory, not proof of reachability, absence of aliases/dynamic lookup, or behavior inside DLLs.

## 1. Renderer selection: a confirmed migration

Original `004b6400..004b64b4` opens `HKEY_LOCAL_MACHINE` (`80000002`), subkey `SOFTWARE\Electronic Arts\Need For Speed III` (`0053fe50`), requesting literal access `000f003f`. It queries:

| Value name | Query call | Destination / immediate handling |
|---|---|---|
| `Thrash Driver` (`0053fe7c`) | `004b644f` | Caller-provided EAX buffer, initial capacity 64 bytes; open/query failure takes the fallback string-copy path. |
| `D3D Device` (`0053fe8c`) | `004b6479` | Four-byte local result, copied to `0055fdbc` only when this query returns zero. A type-output local starts at 4; returned type is not checked locally. |
| `3D Device Description` (`0053fe98`) | `004b6505`, helper `004b64c0` | Caller-provided EAX buffer, capacity 50 bytes. Return code is not translated into an explicit local fallback. |

Original selector producer `004b5720` calls description helper `004b64c0` with buffer `007a3a74`, then driver helper `004b6400` with a 64-byte stack buffer (`004b5732`, `004b573c`). It compares the returned name as a prefix against table `0055fd68`, tries indices 0..10, invokes `004b5e50` if none matches, and writes the resulting index through its incoming EAX pointer. The diagnostic helper's full return/termination contract remains unresolved. Command-line bits can subsequently override that index; this is not a registry-only choice. The [renderer initializer](original-modern-renderer-initialization.md) maps numeric selectors to loading branches.

Modern replaces this with `004b5844`: unless command-line bit 0 of `0055eb2c` is set, it reads section `NFS3`, key `ThrashDriver` (`0053f61c`), default `dx7` (`0053f62c`), into a 56-byte temporary through string reader `004fb714`, then calls parser `004b57f4`. INI/environment/caller-default precedence is established in the configuration chapter. Its subsequent per-driver `thrash.ini` handling is a separate layer, documented in the [loader report](original-modern-renderer-loading.md).

The complete original registry helper ranges `004b6400..004b64b5` and `004b64c0..004b6513` (exclusive ends) are all NOPs in Modern; the script asserts this. No claim is made that a Modern key directly replaces each old D3D value: driver-specific configuration and DLL implementation must be inspected for that correspondence. These original helpers contain no local `RegCloseKey` call, including their success paths; preserve that observation rather than silently repairing it in a reconstruction.

### Original selector precedence and call chain

The selector body is now retained through its actual return at `004b5855` (exclusive end `004b5856`), including all override branches. The switch names/bit indices below are cross-checked against the [command-line table evidence](evidence/audits/original-modern-command-line.json). After the registry-name lookup and initial selector write, it tests flags in this fixed order; the first set flag writes its selector and returns:

| Priority | Flag bit in `0055eb2c` | Original switch | Selector |
|---:|---:|---|---:|
| 1 | 2 | `-voodoo` | 3 |
| 2 | 3 | `-voodoo2` | 4 |
| 3 | 4 | `-ragepro` | 5 |
| 4 | 5 | `-d3d` | 6 |
| 5 | 6 | `-pvr` | 7 |
| 6 | 7 | `-pvr2` | 8 |
| 7 | 8 | `-verite` | 9 |
| 8 | 9 | `-verite2` | 10 |
| 9 | 0 | `-softtri` | 1 |
| 10 | 1 | `-softlin` | 2 |

For example, when both ordinary recognized flags `-softtri` and `-d3d` are present, this selector chooses 6, independently of their argument order. This follows from the explicit flag tests, not an executed command-line test. The registry lookup runs first, including its possible diagnostic call; these flags do not bypass that earlier lookup/error path. Flag production outside the ordinary parser and whole-process behavior remain separate.

The retained original selector-name table has entries `nulla.dll`, `softtria.dll`, `softlina.dll`, `voodooa.dll`, `voodoo2a.dll`, `ragea.dll`, `d3da.dll`, `powervra.dll`, `powervra.dll`, empty, empty. The byte comparator `004eb390` explicitly returns zero when EBX length is zero (`004eb391..004eb398`). The comparison length is the returned registry string's length, not the candidate length; matches select the first table entry. Consequently a matching PowerVR registry prefix chooses 7 before the duplicate entry 8; `-pvr2` can override to 8. An empty returned string supplies length zero, so this comparison path can match entry 0. Registry failures use a copy from `softtria.dll` with requested length `strlen - 5` through `004e0e30`; that copy helper's complete termination contract is not established here. Do not assume the fallback is a full DLL filename merely because that source string is present.

The caller chain is explicit:

1. Original wrapper `004a3390` calls subsystem setup `004b6020` at `004a3393`.
2. Setup passes address `007a3a54` to selector `004b5720` at `004b6074`, then loads its result and stores `1 << selector` at `007a3a58` (`004b6079..004b6086`). This is an x86 masked-count shift; do not translate arbitrary selector values into unchecked C shifts.
3. Setup reloads selector `007a3a54` into EAX and language/state global `007a3a50` into EDX before `004b5860` at `004b60c6`, then reloads both before renderer initialization `004b59c0` at `004b60d6`.

This establishes the original registry/flags-to-selector-to-initializer data path. It does not prove the diagnostic helper returns, authenticate every table name as a supported renderer, or validate the DLLs. Modern uses the different configured-name/parser/type-dispatch path already documented; original selector 6 and Modern type mask 64 must not be conflated just because both select the d-type neighborhood.

## 2. Online DLL registry lookup remains byte-identical

Original and Modern complete bodies `004a5780..004a587c` and `004a5880..004a59ba` are byte-identical, including these four open/query call sites:

- `004a579e` / `004a57ca`: open HKLM `SOFTWARE\EA-NPS\DLL` (`0053da94`) and query `DEVELOP MODE` (`0053daa8`) into a 64-byte local buffer. Exact string comparisons accept `ON`, `1`, `on`, `yes` or `YES`; failure/no match returns zero.
- `004a58ab` / `004a595b`: reopen that key and query a name selected from table `0055eca0`: `NPSDLL`, `LoginClient`, `AnalyzeAPI`, `NPSClientDLL`. If the preceding helper returns 1, append `_DEVELOP` before querying. The result buffer is `007a2020`, initial query capacity 128 bytes; successful output normalizes `/` to `\`.

This establishes retained registry lookup machinery and names, not working online services, successful DLL loading, or safe bounds for every possible selector. Full caller reachability and external modules are not audited here. “System settings moved to INI” should not be expanded into “Modern never reads the registry.”

## 3. Desktop path removed from the old screenshot route

Original `004b6520..004b6588` first clears 256 bytes at `007a3ae0`, opens `HKEY_CURRENT_USER` (`80000001`) subkey `SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders` (`0053feb0`), and queries `Desktop` (`0053fef4`) with initial capacity 256. It returns the buffer address even on open/query failure; the API query result is not explicitly checked. This helper has no local close call. Its original caller is `004c44ba` in the screenshot path.

Modern fills that whole helper range with NOPs. The replacement uses a relative screenshots directory, asynchronous launcher and worker, as traced in the [screenshot comparison](original-modern-screenshots.md). This is removal of this Desktop-registry mechanism, not an INI key replacing `Desktop`. The historical v1.3.1 claim about changing access rights cannot be verified from this original/final pair: the final helper is gone rather than a surviving open with changed rights.

## 4. Runtime memory query also remains byte-identical

Complete body `00522250..005222e8` is identical. It opens predefined root literal `80000006` and subkey `PerfStats\StatData` (`00551928`), then queries `VMM\cpgLocked` (`0055193c`), with open/query calls at `00522287` and `005222c4`. It closes the successfully opened key. This is retained runtime memory-accounting machinery, not evidence of an original counterpart to every Modern heap/configuration option. OS availability, successful results, complete arithmetic purpose and callers are not established by these retained bytes.

## 5. Generic original wrapper and coverage boundary

The original generic wrapper group `004bbcc0..004bbd70` contains open `004bbd13` and query `004bbd50`, supplied with key/value pointers through registers rather than fixed strings at those two sites. The outer helper passes them through `004bbd00` / `004bbd30` and closes the key. Its complete incoming call graph and key producers remain unresolved; no literal setting name is assigned to this wrapper based on nearby strings. Modern has no direct open/query calls at these two addresses; the range is partly reused and must not be interpreted as the same function with two calls removed.

The auditable partition is **4 online + 5 renderer + 2 Desktop + 2 generic + 2 memory = 15**. Modern retains the four online and two memory sites. See the manifest's exact address list; these subsystem labels do not establish runtime reachability.

## Remaining work

- **Pending, static:** establish the original generic wrapper's incoming key/value producers or explicitly unreachable status; trace the higher-level callers of wrapper `004a3390` and any alternate writes to selector state. The direct selector/override/setup-to-initializer path is now mapped.
- **Pending, static/external:** determine where old D3D device preferences move in the packaged driver/configuration files; do not assume a one-to-one INI rename.
- **Pending, historical:** intermediate releases are needed to verify the Desktop access-rights release claim and date individual changes.
- **Pending, runtime:** actual INI/registry precedence outcomes, permissions, renderer behavior and online functionality. No such tests were run.

The Modern setting table includes opt-in policies, new mechanisms and relocated settings. This investigation supplies a concrete renderer migration and retained counterexamples; it does not invent original registry counterparts for all Modern options.
