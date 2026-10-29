# Provider runtime helper audit

## Scope

Read-only static audit of five functions in the active installed `nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`. I followed each direct caller and the normal provider setup path. No target execution, network activity, or persistent Ghidra edit was performed.

## Findings

| Address | Supported operation | Observed register/return contract | Conservative descriptive name |
|---|---|---|---|
| `004f5c10` | Allocates and clears `0x140a8` bytes of transport state; initializes two queue heads at state `+0x70` and `+0x8c`; links 256 nodes of `0x140` bytes from `+0xa8`; configures a socket using arguments `(6, 2, 1000)`; and starts receiver routine `004f5b10`. It returns the allocated state on the success path, or zero on failure. | Inputs are carried in registers; observed call from `004f63d0` sets EDX=0 and EBX=0, and passes EAX=0 after successful Winsock initialization. EDX and EBX initialize state fields; EAX input role is not established. EAX is the returned state pointer/status. The complete source-level prototype is unknown. | `StartIpxPacketReceiver` (operation-derived; socket family/protocol values and surrounding `IPX` label support this transport association) |
| `004f5ea0` | Signals the receiver state to stop and closes its socket. It then waits while state DWORD `+0x1c` is nonzero; only after that field becomes zero does it destroy the two queue heads and release the transport state. The normal caller invokes it after `004f5c10` succeeds. This is a state-field barrier in this routine; the instructions do not establish a kernel thread join. | EAX is the state pointer; EAX=1 on the observed successful close/teardown path. EDX, ESI, ECX and EBX are saved/restored on the observed body. No stack arguments are consumed. | `StopAndDestroyPacketReceiver` |
| `004f63d0` | Initializes the IPX-labeled provider state once, calls `004f5c10` and then `004f5ea0`, registers provider-related pointer pairs in tables indexed by `00566de4`, and returns `00566e28` if the provider-ready flag is set; otherwise returns zero. The ordinary caller passes the string pointer `0053c6d4` (`"IPX"`). Its ESI=1 preload is overwritten by the callee at entry. | EAX is a provider-name pointer and is retained to `00566e24` on success. The caller preloads ECX=`0x2580`, EDX=`0x64`, and ESI=1, but this body does not consume these as parameters; ESI is overwritten from EAX at entry. EAX returns a provider-state pointer or zero. | `InitializeIpxProviderState` |
| `004f7830` | Initializes the second provider path when its guards pass: ensures shared state exists, calls `GetSystemMetrics(0x3f)` and checks the low bit of its return, requests Winsock version `0x0101`, creates a socket with arguments `(2, 1, 0)`, registers callback/context pointers in the provider tables, and returns `00566ee8` on success or zero otherwise. Its ordinary caller passes `0053c6d8` (`"TCP gather"`) in EAX and 8 in EBX. | EAX is the provider label/context pointer. The caller also preloads EBX=8, but the helper overwrites EBX from EAX at entry, so this is not an established parameter. EAX returns the provider state pointer or zero. The helper preserves the observed saved register set. | `InitializeTcpGatherProviderState` (label-derived; runtime availability is not established) |
| `004fa5f0` | Ensures the TAPI record table at `009f4d94` is initialized if absent, rejects negative or out-of-range index values against count `009f4d80`, and returns DWORD `[table + index*8 + 4]` for an admitted index; otherwise returns zero. Caller `004c41d0` treats the result as a NUL-terminated source string and copies it into a displayed row. | Zero-based index in EAX; pointer/result in EAX. EDX is preserved. No stack arguments. | `GetIndexedTapiEntryString` |

The names describe the observed operations and caller context. They are suggestions for review, not applied labels. The `IPX` and `TCP gather` names are literals passed by the sole observed setup caller, not proof of a successful session or of user-visible naming. `004f7830` gates initialization on `GetSystemMetrics(0x3f) & 1`; the significance of system metric index `0x3f` in this path is not resolved, so its label-derived association is deliberately qualified.

## Direct caller paths

- `0049f150` is the ordinary caller of both provider-state initializers. If the service-row count `0055e718` is zero, it calls `004f63d0` with EAX=`0053c6d4` (`IPX`), ECX=`0x2580`, EDX=`0x64`, and ESI=1; it then calls `004f7830` with EAX=`0053c6d8` (`TCP gather`) and preloads EBX=8 (which the callee immediately overwrites). If the latter returns nonzero, the caller sets readiness flag `0055e720`, then calls `0049f030` to enumerate service rows. This is a provider-catalog setup path, not evidence of an actual connection.
- `004f63d0` is the only direct caller of both worker lifecycle helpers in the bounded direct-call scan: it calls `004f5c10` at `004f6409` and `004f5ea0` at `004f641d`.
- `004c41d0` calls `004fa5f0` at `004c41f0` with the current source index in EAX. It copies the returned string to its list and caps its own enumeration loop at 15 rows. The surrounding connect-menu initializer disables the Modem item when the resulting list count is zero; it does not establish that the names correspond to a separate displayed modem table or that a modem is available.

## Evidence and reproducible boundary

All instructions were decoded from the exact executable identified above. The bounded raw disassembly command pattern was:

`objdump -d -M intel --start-address=0x<start> --stop-address=0x<stop> '<selected nfs3.exe>'`

Function/caller byte evidence:

- `004f5c10..004f5e9d`: `ev_1b95a36c814341538edc63b8c924a9010b71257d9aa03f33650f341bc1e95db9`
- `004f5ea0..004f5f46`: `ev_3a2e6a451fa84874f4fc6db97126cb1981ebc91a7aff0c0a88ad54845dbfeaac`
- `004f63d0..004f648b`: `ev_e255a076c1d81a3a098a3bae89ea3751726e493a97e786b24836bcaf011fff00`
- `004f7830..004f78f1`: `ev_b9a57c0a26ca85f114e183d548be8f05416de25a610bf2cb458094ac116b8d96`
- `004fa5f0..004fa61d`: `ev_50b7851ad39ddda37ea2d4c0dce66ebf9689068c4f235df677d795df8a387796`
- Provider setup caller `0049f150..0049f1b7`: `ev_91a43046dda9f8a8a96928105929e98ec95d7150167f84d49d025c742422148a`
- TAPI list caller `004c41d0..004c422e`: `ev_c081a4c1ca19a6de6c59175047d59c018309f3d22adedca1c4bc7b01af44fe1a`
- String bytes at `0053c6c0` establish `IPX`, `TCP gather`, and adjacent labels: `ev_3b1dca89c6ffe00dafcfc093ac6ffa2b2989cf0644ba0b90d06017ef141a8edb`

The direct-caller inventory was a bounded full-image `objdump -d` scan for direct `call`/`jmp` destinations to these five addresses. It found the caller sites listed above; it does not exclude indirect calls or pointers elsewhere. No indirect provider method targets were followed, and no OS/provider availability or live transport behavior was tested.

Parent reviewed all five decompiled bodies and full instruction listings of the two provider registrars, shutdown helper and TAPI getter. The API call was corrected to GetSystemMetrics(63), and shutdown explicitly waits for state+1c zero before freeing; neither a key-state gate nor an independently verified kernel-thread join is claimed. Parent saved/read back conservative names and ABI comments in the shared Ghidra project. No target/network execution occurred.
