# Car profiles: dedicated path source and removed timestamp rejection

## Scope and evidence

The [profile audit](scripts/audit_car_profile_difference.py) checks both pinned executable hashes, complete function envelopes, path literals and the retained `GetModuleFileNameA` import. [Its manifest](evidence/audits/car-profile-difference.json) retains hashes, changed-byte counts and disassembly locations. No profile file was opened, changed or deleted; no game or instruction probes were executed.

| Entry / saved Modern label | Complete envelope, exclusive end | Saved Modern body union |
|---|---|---:|
| `004dc800` BuildPlayerCarProfilePath | `004dc800..004dc8af` (175 bytes) | 138 bytes |
| `004dc940` LoadPlayerCarProfile | `004dc940..004dca4e` (270 bytes) | 240 bytes |

Complete envelopes include 37/30 NOP bytes excluded from the saved Modern body unions. Same-address correspondence is established by the unchanged code outside the specific regions below. Analysis labels do not establish original source names or a complete profile format.

## Path builder changes source and removes a directory component

Both preserve the incoming EAX string pointer in EDX and build the result in shared buffer `00564188`. Original copies its base from `007a2fb4`, appends file-backed `carspecs\` at `00549770`, appends the incoming string, then appends `.spc` at `0054977c`. Modern instead copies its base from `007a30b4` and jumps over the literal `carspecs\` append (`004dc835..004dc85c`). It retains incoming-name and extension appends and returns the shared buffer address in EAX.

The verified formulas are therefore:

- Original: `contents(007a2fb4) + "carspecs\\" + input_name + ".spc"`.
- Modern: `contents(007a30b4) + input_name + ".spc"`.

This does not prove that the final effective directory differs: the Modern base may already contain the component. Producer values and installed-directory observations must be established separately. Nor does a changed source address prove a user-writable or per-user directory. Both retain unbounded string-copy/append loops in this body and shared scratch output, so capacity, reentrancy and input aliasing remain reconstruction obligations.

## Loader removes the file-time rejection branch

The unchanged prefix selects one of two destination records for incoming index 0/1, checks configuration admission through `004721f0`, clears `960h` bytes and calls the path builder. It then retains `GetModuleFileNameA(NULL, local_buffer, 249)` at `004dc9b9`. Modern does not remove that now locally unused executable-path query.

Both call `004e0e60` on the generated profile path. Original copies the return to ECX, tests it, and when nonzero calls `00472940` with the profile and executable paths. The [configuration-load comparison](original-modern-config-loading.md#retained-file-load-prefix-removed-timestamp-comparison) already establishes this helper's file-time comparison and its legacy failure-semantics limits. If that helper returns nonzero, original calls `004e28a0` on the profile path and goes to the reset/default path at `004dca37`. Otherwise the retained ECX test decides whether to reach the load sequence.

Modern replaces `004dc9c7..004dc9eb` with `TEST EAX,EAX; JZ 004dca37; JMP 004dc9eb` and 30 NOPs. It no longer calls the timestamp helper or `004e28a0` from this function. Thus the original timestamp-triggered rejection/delete route is absent here. Complete behavior of the initial path helper `004e0e60` is not re-established in this audit; the direct machine-level statement is that its nonzero return reaches the retained load sequence and zero reaches reset/default.

The entire suffix `004dc9eb..004dca4e` is byte-identical. It retains the size/read path, calls `004dc8b0` only when the signed size is positive, releases the loaded buffer, and performs existing validation/reset branches. This is not evidence of a newly permissive parser or complete format compatibility. The changed path builder can also supply different inputs to that retained suffix.

## Reconstruction and remaining work

**Bounded work status: done; evidence confidence: verified static code and literals, with timestamp-helper meaning linked to existing research.** Preserve the selected path source and gate policy. Do not automatically restore timestamp rejection to Modern, remove its retained filename query, or convert shared scratch storage into a new ownership contract while claiming exact compatibility.

**Unresolved:** base-buffer initialization and capacities; all indirect profile consumers; exact `004e0e60` failure contract; actual profile assets, serialization, validation coverage and runtime reset behavior. These affect data/initialization reconstruction, interfaces and runtime validation. The original executable, Modern executable, Ghidra project and maintained C remain unchanged.
