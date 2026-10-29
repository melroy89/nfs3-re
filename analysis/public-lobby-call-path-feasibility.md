# Public-lobby call-path feasibility

## Scope and build

This is a bounded static trace of the selected installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`). It follows the active RaceNet menu route, ordinary provider enumeration, and NPS server-list API references. It does not query external services or execute the game/provider.

## RaceNet frontend route

The active `connect.mnu` names a RaceNet item with `nextmenu=mainmult`. In active code, `004405c0` performs an availability check for selector 3 and looks up the item, but the callback assignment is absent: `004406c7` jumps over `004406c9–004406dd`, which are NOPs. If the item reaches generic Enter handling, `00461270` has no RaceNet-specific callback to invoke and uses the ordinary transition action for the non-null `nextmenu`. The resulting path is a transition to `mainmult`, not a RaceNet provider dialog or a server-list operation. The separate selection-state callback's `006fd3b0=4` assignment does not supply the missing callback. See [connect menu selection state](connect-menu-selection-state.md).

The selector-3 producer is still unresolved outside the reviewed catalog builders; those builders create selectors 1 and 2, not 3. Thus the expected enabled/disabled state depends on any other catalog writer or externally supplied catalog state. Even if enabled, the inspected item route remains the generic `mainmult` transition.

## Ordinary provider enumeration route

The IPX game-list Refresh action reaches `0043f220` → `0049e3d0` → `004f4eb0`. The last routine dispatches through the current provider object's operation at `+0x10`. The registered owner keeps two distinct pointers: generic operation descriptor `005689e8` at owner `+4`, and backend method table `00566e24` at owner `+8`. The enumeration broker `005143d0` uses the backend-context pointer at owner `+0x0c`, then invokes backend methods through the owner `+8` table. This establishes an in-binary backend callback route, but not an NPS server-list call or a specific transport discovery mechanism.

### Callback pointer provenance

The concrete in-executable registration publishes generic operation table `005689e8` into `009f25b0[index]` and backend method table `00566e24` into `009f25d0[index]` (`004f6422–004f6441`). This backend table is produced by the `IPX`-labelled initializer `004f63d0`, which passes the literal at `0053c6d4` and returns an identifier-data pointer at `00566e28`, four bytes into the backend descriptor beginning at `00566e24`. Owner initializer `004f4d10` copies the registry's second array to owner `+8` and first array to owner `+4`. At `00514280`, initialization loads owner `+8` and calls its `+0x1c` slot; the active backend table bytes at `00566e40` hold `004f5c10`, which constructs the backend context subsequently stored at owner `+0x0c`. The generic table's `+0x1c` pointer (`00514650`) is not this constructor.

The backend table bytes at `00566e54` and `00566e58` hold `004f5fa0` and `004f5fc0`. These, rather than generic-table entries `00514af0` and `00514dc0`, are the broker's actual method targets: `005143d0` calls `[owner+8]+0x30` and `+0x34` with the backend context as its receiver. The active `004f5fa0` writes the `0x30`-byte field at context `+0x26` using a bounded string copy from EDX plus zero padding (`004e0e30`), then calls `005127d0` with the socket handle from context `+0x58`. `005127d0` is identified in the supporting provider-helper audit as `SendFamilySixBroadcastProbe`: it constructs a family-6 destination with broadcast-shaped address bytes, network-order port `0x0452`, and payload `00 01 08 be`, then reaches the `sendto` thunk. `004f5fc0` clears the context byte at `+0x26` and falls through to return 1. This links the IPX-labelled backend path to a broadcast-shaped probe when this candidate is selected. The exact protocol/reply semantics and live availability remain unverified; the path is not an NPS server-list lookup or proof of a public lobby. See [provider runtime helper audit](provider-runtime-helper-audit.md).

In the active image, the NPS export loader `004a54f0` resolves `NPSGetServerList` into pointer slot `007a21c4`. A whole-image disassembly reference scan found that slot only in the `GetProcAddress` store; it found no load/call through that pointer. The same is true for the server-info, locate-player, start-server, and users-on-server pointer slots. This is direct evidence that the reviewed executable's ordinary in-binary code has no direct call site to those NPS list/lookup methods. It does not prove what an external provider DLL might do behind an opaque callback.

The distinct NPS session route is present: `004730d0` enters it only when the outer session flag at `0055b03c` is nonzero and the network-parameter string at `007a1fa0` is nonempty. It selects `0049e220` or `0049e2e0` according to `007a1ffc`; both initialize through `0049e080`, which reaches `004a5b00` and the dynamically resolved `NPSConnectToServer`/channel APIs. This is a configured session connection path, not a public server-list lookup path, and the observed gate is not the RaceNet item's callback.

## Findings and limits

- No active RaceNet callback-to-NPS server-list chain was found.
- The active RaceNet item falls through generic menu transition handling to `mainmult` if it is selectable; this alone does not establish a public lobby.
- Normal provider game-list enumeration uses indirect provider callbacks. Static evidence does not resolve their implementation to NPS, and the direct executable references do not call NPS server-list lookup methods.
- For the concrete IPX-labelled candidate reviewed, the broker's backend slots resolve to `004f5fa0` and `004f5fc0`; the first sends a broadcast-shaped probe through `005127d0`, not an NPS server-list lookup. Exact discovery/reply behavior and live availability remain open.
- The executable contains a separate NPS connect/session implementation, reached behind session-state and nonempty-parameter gates; it is not evidence of public discovery or a live master service.
- External provider DLL behavior, other selector-3/catalog writers, and runtime-loaded components remain outside this static route result. The local NPS installation evidence is separately bounded in [NPS provider installation evidence](nps-provider-installation-evidence.md); no external service was queried.

Evidence anchors: active-image assembly for `004730d0` (`ev_141481d6381e21d6ada2ea280ff4ef2798e28021b78a73a2b827716fbefa9fcc`); NPS export loader `004a54f0` (`ev_5f2e5562722af65acc8f871518690febb3ba07f8b5e2cb454869f3dbbf8240c3`); generic operation descriptor bytes (`ev_838e65574ecd9974310b0cfa916135785d750f8840aeb86b049cd571304cd2fa`); active backend table bytes at `00566e24–00566e60`; provider-helper evidence for `005127d0` in [provider runtime helper audit](provider-runtime-helper-audit.md); selected-build disassembly at `004f4d10`, `00514280`, `005143d0`, `004f5c10`, `004f5fa0`, `004f5fc0`, and registration at `004f6422`.
