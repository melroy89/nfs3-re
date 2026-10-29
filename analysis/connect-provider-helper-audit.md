# Connect and provider helper audit

## Scope

Read-only instruction review against active `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. Focus is the five helpers parent flagged and their ordinary provider/menu path. The worker pass made no runtime, config, executable, or persistent Ghidra changes; parent project annotations are described below.

## Findings and cautious naming suggestions

| Address | Supported operation | Register/return evidence | Suggested descriptive name |
|---|---|---|---|
| `0049e360` | Search service rows for an EAX selector in `g_serviceRowCount` (`0055e718`), comparing each row's selector at `0055e734 + i*0x2c`. If absent, call `0049f150`, then search again. Return EAX=1 if found, otherwise 0. | Input selector in EAX; preserves EBX/EDX; bool result in EAX. The fallback initializer's EAX result is ignored before the rescan. | `EnsureServiceCatalogThenHasSelector` |
| `0049f030` | Clear service-row count, then invoke `004f4c70` with callback `0049f200` and forwarded context/arguments. On success, it checks a global readiness flag; if set, records selector 2, copies a 16-byte metadata block into a 0x2c-byte row, clears a byte field, and increments count. It then calls `0049f790`; failure clears the row count. | Called by `0049f150` with EAX=`0x2580`, ECX=`0x64`, ESI=`1`; internally snapshots incoming EAX/EBX/EDX into a provider-call setup and passes `0049f200` to `004f4c70`. Returns after its helper logic; do not treat it as a simple bool predicate. | `EnumerateAndInitializeServiceCatalog` |
| `0049f150` | Ensure supporting state at `0055e864` exists via `004eb2e0`; when no service rows exist, initialize shared network state (`004f63d0` with string `0053c6d4`, values `0x2580`, `0x64`, and `1`), call another setup helper `004f7830` with string `0053c6d8` and value 8, set readiness `0055e720` on success, then call `0049f030`. | No explicit arguments are read before the no-rows branch; preserves EBX/ECX/EDX/ESI; EAX is returned from nested setup path. Exact user-facing meanings of the two strings and constants are not established by this function alone. | `InitializeServiceCatalogIfEmpty` |
| `004c41d0` | Given a list structure in EAX, returns immediately for null; otherwise calls zeroing helper `004e070c` with size `0x1c8`, then appends strings for source indices 0 through 14. It requests each string through `004fa5f0`, copies bytes through the NUL into the next 30-decimal (`0x1e`)-byte row beginning at list `+4 + count*0x1e`, and increments the count at list offset 0. | Input list pointer in EAX. No useful return value set. Maximum index count is explicitly 15; the copy is NUL-terminated, with source length bounded elsewhere or unknown here. The zeroed extent `0x1c8` is 456 bytes. | `PopulateIndexedServiceNameList` (tentative) |
| `004f4c70` | Iterate `g_nProviderCandidateCount` at `00566de4` candidate entries. It initializes/queries context via `004f4c50(0054d0c0,1)`, checks each candidate object's `+4` state, and dispatches either an indirect method at candidate `+4` or the supplied callback when the selector value is at most `0x20`. The supplied callback receives the candidate's `+0`/`+4`-derived values and fixed size `0xfa`; loop continues over candidate records. | Saves incoming EAX (callback), EDX (context), EBX, and ECX; ECX is compared with `0x20`; EAX is restored as callback for indirect invocation. Returns last callback/method EAX in EAX. Exact semantic roles of the forwarded context and fields are not fully resolved. | `EnumerateProviderCandidatesWithCallback` |

The names are suggestions only, not persistent annotations. In particular, “service” here means the binary's internal row/catalog model; it does not identify a public provider or current network service.

## Menu/provider connection

Active connect initializer `004405c0` calls `0049e360` with EAX selectors 3, 1, and 2 while configuring `racenet`, `ipx`, and `tcp` item availability. It also tests `005f3df0` before enabling the modem item. The menu callback assignments for TCP, modem, and serial are established in [connect-menu-dispatch-crosswalk](connect-menu-dispatch-crosswalk.md). Thus the newly inspected helpers explain catalog-presence tests and catalog population supporting menu availability, but do not make RaceNet's callback assignment reappear in active `nfs3.exe`.

For modem availability, active `004405c0` calls `004c41d0` with `005f3df0`; if the leading count DWORD is zero, it ORs bit `0x01` into the modem item's flags at `+4`, disabling input. The helper clears `0x1c8` bytes and enumerates up to 15 source strings into 30-decimal (`0x1e`)-byte rows. The precise source/meaning of those strings remains unresolved. The Serial item is mapped to callback `0043fee0`; this helper set does not establish serial-port enumeration or hardware availability.

## Evidence limits

Instruction ranges checked in the selected PE were `0049e360–0049e3cb`, `0049f030–0049f141`, `0049f150–0049f1b7`, `004c41d0–004c422e`, and `004f4c70–004f4d03`, with focused adjacent caller/callee instructions where described. Names and some semantic roles remain inferred from data flow. This review did not enumerate every indirect provider method, resolve external provider DLL behavior, inspect registry state, or perform a live provider/hardware check.

Parent review verified full assembly of0049e360/004c41d0/004f4c70 and decompilation of0049f030/0049f150. It corrected row strides to44 bytes and30 bytes, respectively, and confirmed zeroing plus the count-zero Modem disable gate. Parent saved conservative operation/ABI annotations and names for these five routines; provider/hardware availability remains unobserved.
