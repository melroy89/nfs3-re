# Network series state at next-round setup

## Finding

On the selected installed executable (`nfs3.exe`, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`), the host-side setup sender copies the entire `0x890`-byte range `[006fd39c, 006fdc2c)` into type-5 setup messages. The following bounded series ranges fall inside the **first** `0xd0`-byte data chunk:

| State | Address | Offset from `006fd39c` | Range in first data chunk? |
|---|---:|---:|---|
| Knockout progression WORD | `006fd3bc` | `0x20` | Yes |
| Knockout eligibility WORD array | `006fd3de` | `0x42` | Yes |
| Mode-one progression WORD | `006fd40c` | `0x70` | Yes |
| First eight cumulative score WORDs for the normal eight-entry mode-one roster | `006fd44e..006fd45d` | `0xb2..0xc1` | Yes |

The mode-one roster builder `00474310` sets the total participant count to eight (`006fd510 = 8`) after filling the remaining slots to that count; this is the ordinary roster extent relevant here (evidence `ev_834ef8dd2e667d174b7718c3ab31c091b1cffed7ed14697b45ddd7d2005d8c39`). The backing score addressing is identity-indexed, so this report bounds only the normal eight participant score words. It does not imply that a hypothetical wider identity-indexed span fits in the first chunk: the 16th WORD, at `006fd46c` (offset `0xd0`), begins in the next chunk. The broader setup transfer still includes that address.

The client receiver appends incoming type-5 data at that same base. On its branch, `004c5e80` copies each of the 16 participant records (`0x6c` bytes apiece) from `006fd52c + 0x6c*i` into a separate snapshot before the synchronization wait. Afterward it restores snapshot field `+0x14` to the corresponding record only when the saved signed value is `0..49`, and restores `+0x68` unconditionally. These addresses correspond to `006fd540 + 0x6c*i` and `006fd594 + 0x6c*i`, respectively. None of the four global series ranges is part of that selective restoration. Thus, under the ordinary complete host-send/client-receive sequence, the client adopts the host's transferred series bytes; this code path does not preserve those fields from the client's pre-transfer local copy. The restoration is limited to those two fields and is not a full local-record restore.

This is byte-transfer and local-write evidence. It does not prove that all packets arrived, that each peer computed matching result state before exchange, or that the peers' live values stayed equal afterward.

## Next-round ordering

The normal result path at `00455410` runs on each peer without a host-role gate around its mode-specific updater. Mode 1 adds round points to the cumulative score words and advances `006fd40c` when its state gate allows; mode 2 updates the eligibility/order tables and increments `006fd3bc` when invoked. The normal Race Again route re-enters `RunRaceSession` (`004a3690`) without the main-menu reset, so these values survive locally to the next setup attempt.

During that next session initialization, `004a3690` calls `00474ca0` before `004a33f0`. The former builds the local race roster and, for Tournament/Knockout, consumes the local progress and eligibility values. `004a33f0` then calls `00477f60`; when setup succeeds, session mode is greater than 1, and playback selector is zero, `00477f60` calls `004c5e80`.

`004c5e80` resets the type-5 accumulation offset and cursor to `006fd39c`. With host flag `007a22da != 0`, it emits ten `0xd0`-byte data chunks and one `0x70`-byte final data chunk, each carried in a type-5 message. With host flag zero, it snapshots the 16 local participant records, reaches the synchronization wait, then restores only the two participant fields listed above. The setup range also contains the roster records that `00474ca0` built before the exchange. Therefore, on the client branch, a complete transfer replaces its pre-exchange setup block, including the requested series globals and the in-range roster data; the explicit participant-field restoration is a narrow local exception.

The ordinary type-5 handler (`004c6080`, selected by the packet dispatcher for type 5) skips the one-byte type prefix and appends each payload to the same cursor. The host sender's valid producer provides exactly `0x890` data bytes. The receiver append path does not itself expose a final accumulated-length comparison in the reviewed body, so successful matching of the whole producer stream is a condition for the conclusions about the client's final state.

## What is synchronized and what is not established

- **Included and not locally restored:** the eight cumulative score WORDs used by the ordinary eight-entry mode-one roster, beginning at `006fd44e`; mode-one progression `006fd40c`; Knockout progression `006fd3bc`; and the 16-entry eligibility array beginning at `006fd3de`. The eight ordinary score WORDs are byte-included in the initial type-5 payload; any wider backing score span remains within the full `0x890` transfer, though the 16th WORD starts in chunk two.
- **Explicitly preserved locally on the client branch:** for each of 16 participant records at `006fd52c + 0x6c*i`, field `+0x68`, plus field `+0x14` only when the saved signed value is in `0..49`. The semantic labels for these two fields are not needed for the ownership conclusion and are left as offsets.
- **Host/client direction:** only the nonzero-host-flag branch sends the `0x890`-byte block. The zero-host-flag branch snapshots participant fields and waits/restores. The type-5 append callback itself has no role-specific direction check. This establishes the normal sender/receiver split in the caller routine, not a transport-level role guarantee.
- **Peer agreement:** each peer computes result updates locally, while the next setup transfer supplies the host's copy to clients. This is an implementation path for host-to-client synchronization, not proof of transport completion or exact live equality. Divergent local results before setup, a missing or partial transfer, or later local writes remain outside a static byte-copy proof.

## Evidence

- Active executable identity as above.
- Prior result exchange report: [network series result exchange and local progression](network-series-result-ownership.md), including local score/progression update addresses and absence of a host-only guard in `00455410`.
- Setup transfer and receive framing: [multiplayer setup transfer and loading-abort lifecycle audit](multiplayer-setup-abort-lifecycle-audit.md). It documents sender `004c5e80` (`ev_33b5bd2b20703899f71f575be5029cc8aa12d1c9824a70f7d2d1249bb9726063`), caller `00477f60` (`ev_2e8074c5d736c6aac80e4c7bf0ac17e540d5682a89bcfe3fd8743d7cf8c37a38`), and the type-5 append/dispatcher bounded instruction reads.
- Current active Ghidra evidence: `004c5e80` `ev_5cf61ab20d7911071f8f27dd1550a4338bc00aff2d82a50a53d2e3bf0192f150`; `00477f60` `ev_92751c87545ea4659fcf1dd89191f897d2089626b95fefc95293622c19bdb358`; race setup initializer `004a33f0` `ev_3e72ec9f4128f34ce2d6e2d73b3e7dda6ac6e23fd66f4d6646a3943a91e3698a`; race-session order `004a3690` `ev_5ef3da5f33611b418a83775a987dffe3ecdd81c5e5a1d74914f383fc9be58435`.
- Local roster builder before exchange: `00474ca0` `ev_9e82a0ed4d94cdc62d8c99014ed6110330f6d8b4856ffdc832805884063b029c`; mode-one roster `00474310` `ev_5033d5674d8e7f98d711a8be5c08df27da5d9ff65690d3797eeee0be6c105461`; Knockout roster `00473ee0` `ev_d56348d940790d1f9068c930b3fbdec46daecb89cb6320e70745ab7d5ea3944b`.
- Progression and Race Again retention/reset details: [normal series terminal lifecycle](series-normal-terminal-lifecycle.md). Main-menu entry clears series blocks; ordinary Race Again retains them.

No gameplay, network, executable, configuration, or persistent Ghidra changes were made.

## Conditional frontend action forwarding

Parent review also resolves the numeric action handoff, conditional on the lobby callback action surviving intervening dialog/action overrides. `0044a4f0` retains nonzero `00441040` panel results in EDI (`0044a606/0044a632`) and returns EDI as EAX at `0044a644`. `RunFrontendMenuLoop` stores it at `0044b39c`. Raw action table `0044b208` sends actions6/7 to `0044b747`; that branch clears the loop-live local at `0044b76c` and leaves the stored action unchanged. Final return `0044b936` supplies it to the wrapper. Postgame wrapper `0047331f/00473336` saves/forwards it after cleanup; application table `004a3d94` sends6/7 to `004a3ee8`, calling race preparation `004a3690` at `004a3ef4`. This closes the previously unconnected callback-action/application-state edge for that surviving action. It does not prove that the panel is invoked, readiness succeeds, no dialog supersedes the result, or the next race initializes successfully in a live network series.
