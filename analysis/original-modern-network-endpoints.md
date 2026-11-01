# Original versus Modern: network endpoint and port handling

## Scope and evidence

**Static comparison of the supplied original and official Modern v1.6.1; no new network execution.** Exact SHA-256 identities are original `b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b` and Modern `240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6`. See [baseline/provenance](original-modern-differences.md).

Run `python3 analysis/scripts/audit_network_port_difference.py` from the repository root (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-network-port.json) records instruction-span hashes and input identities. Raw assembly stays under ignored `analysis/captures/modern-differences/network-port/`. The common endpoint function and its common caller/dispatch neighborhoods establish correspondence; the new getter/parser must not be equated with unrelated original code occupying their VAs.

## 1. Original constant becomes a configurable default

| Site | Supplied original | Official Modern |
|---|---|---|
| Service-selection initialization `0049e70c` | `MOV EAX,0x406` (1030) | `CALL 0043fd10` |
| Endpoint conversion `0049ea86..0049ea97` | Loads EBX=1030 and EDX=input address | Saves EDX=input address, calls `004a2f50` to obtain port in EBX |
| Service replacement `0049ea09` | `PUSH 0x406` | `PUSH EDX` (incoming port carried from EAX at entry) |

New getter `0043fd10..0043fd1f` zero-extends the WORD at `006fd1dc`. Nonzero returns unchanged; zero substitutes `0x264b` (**9803**). These are host arithmetic integers passed into the connection layer; the external provider's eventual sockaddr byte-order encoding is not established here.

The initialization site forwards the chosen value through the pre-existing stack path to `004f4d10` (`0049e727/0049e743`). Endpoint conversion forwards it through EBX to `004f5050`. This establishes an actual operand/control-flow change, rather than relying on finding the constants in a string or resource.

The getter has no range issue for nonzero storage because it reads 16 bits. Startup/persistence writers still determine which value is present. The menu toggle and its DWORD write must be considered separately from the getter's WORD read; do not infer a two-byte-only storage allocation from this reader alone.

## 2. Address normalization and colon port parsing

New helper `004a2f50..004a2f8c` accepts a **mutable** address pointer in EAX:

1. Saves the pointer in ESI, calls the getter, and copies its result to EBX.
2. Replaces each comma before the first colon/NUL with a period.
3. At the first colon, overwrites the colon with NUL and parses the remaining suffix through signed-decimal helper `004f0430`.
4. A nonzero parsed value accepted by unsigned `CMP EAX,0xffff` / `JBE` becomes EBX. Thus normal accepted results are **1..65535**; ordinary negative results are rejected by the unsigned comparison; the converter itself wraps, so oversized signed text needs the qualification below. Zero or out-of-range results retain the default in EBX.
5. Returns with ESI restored. EBX is the port output. EAX is not a uniform success/port return: no-colon and rejected cases return zero, accepted cases retain the parsed value.

The caller saves the address in EDX before invoking the helper. Existing decimal-parser preservation supports retaining EDX/ECX across this path, as documented in [earlier ABI research](detailed-analysis-notes.md#mutable-network-address-suffix-normalization).

Consequences derived from these instructions, not executed test cases:

| Input, with configured WORD zero | Mutated address | EBX |
|---|---|---:|
| `192,168,1,111` | `192.168.1.111` | 9803 |
| `192,168,1,111:1030` | `192.168.1.111` | 1030 |
| `192.168.1.111:65535` | `192.168.1.111` | 65535 |
| `192.168.1.111:0` | `192.168.1.111` | 9803 |
| `192.168.1.111:65536` | `192.168.1.111` | 9803 |
| `192.168.1.111:-1` | `192.168.1.111` | 9803 |

An invalid suffix still removes the colon/suffix from the address. No validation of the address itself occurs here. The follow-up below resolves the local decimal grammar, wrapping and first-colon boundary. Complete hostname/IPv6 support and eventual address acceptance still require the provider’s own grammar.

## 3. Retained endpoint and provider boundary

Matched function `0049ea70..0049ead2` only proceeds when service mode `0055e71c==2` and the address is non-null. It invokes object `007a0390`, method `+0x38`, with address in EDX, port in EBX and temporary endpoint output `007a03ac` in ECX. A nonzero provider result copies **20 bytes** to the caller's destination and returns 1. Failure shows notice `0xc2` and returns zero; the destination is not copied. Other modes/null input return zero. Input mutation may already have occurred on failure.

Wrapper `004f5050..004f5065` is byte-identical in both binaries. It reads the method table from object `+8`; absent method returns zero, otherwise context from object `+0xc` goes into EAX and method `+0x38` is invoked. The wrapper does not itself validate pointers, create a socket or identify endpoint fields.

The 20-byte endpoint payload's schema, exact runtime provider and complete dynamic import/call graph remain outside this chapter. The literal port/default change is confirmed at the executable boundary, without claiming that this wrapper proves socket-level behavior.

## 4. Service replacement and failure notice change

At `0049e9d0`, original treats its incoming EAX as a value preserved in EDX and pushes it as one initialization argument; port is the literal 1030. Modern instead preserves incoming EAX as the port in EDX, pushes incoming EBX in the former EDX-argument slot, and pushes EDX as the port. Its callers must supply the revised contract; keeping the original signature for this function would misrepresent the new behavior.

Original at `0049e9ef..0049e9f2` returns success early when current service mode is already 2. Modern replaces that comparison/branch with an unconditional path into teardown/reinitialization. This permits changing the service parameters rather than always retaining the existing mode-2 instance.

When `004f4d10` fails, original calls the notice function with ID `0xc2`, clears EAX and returns (`0049ea4a..0049ea56`). Modern jumps directly to the epilogue at `0049ea67`, preserving the initializer's zero result and suppressing **this local notice**. This is not proof that every occupied-port error is suppressed or that a failed listener can always join another host. Caller behavior and provider bind/connect paths still need inspection.

## Menu selection and retry callers

The [menu comparison](original-modern-network-port-menu.md) traces a two-value 9803/1030 toggle, not arbitrary digit editing. Its setter writes a DWORD at `006fd1dc`, although the getter reads a WORD. A conditional retry helper attempts the alternate on one menu branch without changing the configured global. This addresses the earlier writer-search gap; storage extent and aliased/persisted producers still require separate review.

## Catalog traceability and compatibility boundary

- **MP140-001:** 1030→9803 default is statically verified in the chosen paths. The stated reason that Windows often occupies 1030 was not tested.
- **MP140-003:** colon-port handling is verified at the adapter boundary, including invalid-suffix mutation/default retention. No network connection was made.
- **MP140-004/005:** the removed local failure notice and revised reinitialization are relevant evidence, but exact menu error behavior and joining with an occupied local port remain partial until callers/provider paths are traced.
- **MP140-006:** selecting/passing 1030 only aligns a transport parameter. It does **not** prove original/Modern race synchronization, replay compatibility or full protocol equivalence. The [precision comparison](og-modern-x87-precision.md) is an independent numerical difference.

Earlier [host/VM observations](normal-tcp-race-validation.md) concern two Modern-derived peers, not an original-versus-Modern comparison. They must not be reused as cross-version acceptance evidence. No executable/Ghidra changes or new game/probe execution were made here.

The [network launch consumer comparison](original-modern-command-line.md#retained-launch-consumer-versus-changed-peer-endpoint-policy) now verifies two retained bodies and separates that Port handoff/literal6666 route from the changed1030→9803 peer endpoint policy documented here.

## Historical comma normalization and exact suffix grammar

**Confidence: verified static instructions and historical boundary; work status: done for local adapter semantics.** The [historical audit](scripts/audit_endpoint_comma_history.py) pins author-hosted1.4.0 and1.5.0 archives and EXE members, alongside the supplied original and official final. Its [manifest](evidence/audits/endpoint-comma-history.json) retains complete bodies, instruction bytes, hashes and classification sets. It executes no target instructions.

| Compared artifact | Verified result |
|---|---|
|1.4.0 normalizer `004a2f50..004a2f83`,51 bytes | Scans to first colon/NUL; has no comma replacement branch |
|1.5.0 normalizer `004a2f50..004a2f8d`,61 bytes | Adds ten-byte comma comparison/store/back-edge at`004a2f61..004a2f6b`; rewrites comma to period before continuing |
| Official1.6.1 normalizer | All61 bytes identical to1.5.0 |
| Historical/final endpoint caller `0049ea70..0049ead3` | All99 bytes identical across1.4.0,1.5.0 and official1.6.1; existing provider handoff remains |
| Decimal converter `004f0430..004f0487`,87 bytes | Identical in supplied original,1.4.0,1.5.0 and official final |
| Classification table `00564ef0..00564ff0`,256 bytes | Identical file-backed bytes in all four; leading-space class is ASCII9..13 and32, digit class ASCII48..57 |

This dates the **local comma-normalization mechanism** to the advertised1.5.0 boundary (MP150-019), rather than inferring introduction from final bytes alone. Original's matched endpoint path forwards the unmodified string with port1030, as established above; the normalizer's VA in original contains unrelated data and is not an original parser counterpart. Provider-side treatment of commas in any version is not established here.

The decimal converter is already documented in the [shared numeric-field investigation](original-modern-common-menu-buttons.md#numeric-field-parsing-digit-only-validation-and-wrapping-conversion). The network adapter calls it **directly**, without that investigation's separate digit-only wrapper. Therefore the network suffix accepts leading classified whitespace, one optional sign and a decimal digit prefix, ignores the remainder, and has no overflow-error check. IMUL/ADD/SUB and optional NEG retain only32 bits. The adapter accepts the resulting nonzero unsigned value up to65535; it does not validate the mathematical value of the entire textual suffix.

Examples below are **derived arithmetic/control-flow consequences**, not executed parser tests. Assume configured WORD zero, unchanged classification bytes, clear direction flag, and readable/writable NUL-terminated input:

| Raw input | Address visible through original buffer pointer after normalization | Port output EBX | Reason |
|---|---|---:|---|
| `192,168,1,111: +1030junk` | `192.168.1.111` |1030 | Leading space/sign accepted; trailing text ignored |
| `host:1030:9803` | `host` |1030 | First colon ends address; second ends decimal prefix |
| `host:1,030` | `host` |1 | Commas after the colon are not normalized; conversion stops there |
| `host:4294967297` | `host` |1 | Decimal accumulation wraps modulo2^32 |
| `host:-4294967295` | `host` |1 | Wrapped accumulator`ffffffff` is negated to1 |
| `host:4294967296` | `host` |9803 | Wrapped zero retains default |
| `host:0x406` | `host` |9803 | Decimal prefix is0; no hexadecimal interpretation |
| `host:` | `host` |9803 | No digits produces0 |

The first colon is overwritten with NUL even for a rejected suffix; suffix bytes remain after that NUL in memory. No-colon input retains the default port. The loop uses LODSB and assumes DF clear; it contains no CLD or buffer-length bound. These are ABI/input prerequisites, not new claims of a reachable defect. Classification mutation and upstream input restrictions can narrow actual reachable cases. IPv6, hostname resolution, UI filtering and successful connections remain unverified.

A faithful C reconstruction must preserve unsigned32-bit accumulation and explicit truncation before the final port gate, plus mutable-buffer and EBX-output contracts. Replacing this with strict whole-string validation or a saturating host `strtol` would change the observed arbitrary-input contract. This finding does not establish original/Modern multiplayer synchronization or replay compatibility.
