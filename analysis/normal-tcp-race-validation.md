# Bounded normal TCP race validation

## Scope and outcome

The user requested one normal TCP race with matching final results on both peers, followed by a return to the lobby and start of a second race. The same host/bridged Debian13 VM and documented executable were used. The host NFS3 prefix was changed, at the user's request, to Wine virtual-desktop mode; the physical primary display remains1920×1080. The VM Wine display settings were not changed.

**Outcome: BLOCKED by a persistent black game window in the VM.** This pass does not establish normal two-finisher results or the second-race transition. It does establish a completed host participant's state propagating to the VM before the failure prevented the VM driver from finishing.

| Check | Result | Evidence |
| --- | --- | --- |
| Two-peer TCP session | Passed for this LAN pair | Host192.168.1.227:9803 and VM192.168.1.111:42941 remained ESTAB in socket observations. ESTAB does not prove every application operation remains healthy. |
| Host completes two laps | Observed | User reports host finished; VM vehicle0 then has wrap2/result3. |
| Remote host-finish state retained by VM | Observed | First sampled at VM capture t316.628815/tick14963; still present at t599.797045/tick33086. |
| VM completes two laps | Blocked | VM participant1 remained wrap0/result0/progress4 in retained endpoint samples. |
| Matching normal final result tables | Not reached | Both participants did not finish. No normal results/placement agreement claimed. |
| Lobby return and second-race start | Not run | Stopped after the VM display failure and the user's decision not to restart/replay. |

## What continued despite the black window

The VM process remained alive. Its captured simulation/sequence counter advanced after the host finish; a later guarded O_RDONLY snapshot has tick73828, while the two result states remain3/0. This separates a persistent rendering failure from process exit, but does not establish the failed graphics call or prove complete network health.

The VM's four active driving bindings were keyboard-class values in the nonzero race binding set (`0x4b04`, `0x4d04`, `0x4804`, `0x5004`). Their configuration does not itself prove responsive input while the picture is black. The user could not continue driving the VM in that condition.

## Recorded graphics evidence and recovery boundary

The VM Wine log contains `NtUserChangeDisplaySettings` return-2, failed display-mode restoration (`0x8876086a`), swapchain cleanup errors and an unregistered-window message. Earlier session inspection establishes a Wayland desktop with Xwayland. These facts support investigating graphics/display handling; they do not isolate Wine, the virtual GPU, compositor, focus changes or the game as the root cause. The untimestamped log also does not establish an exact causal ordering of individual messages.

The user tried Alt+Tab and other actions without restoring the picture. An Alt+F4 request was sent as preparation for a proposed Wine virtual-desktop recovery, but the game stayed running. The user then cancelled the restart. **No VM virtual-desktop setting, driver, VM display hardware or executable change was applied.** No normal-results success is inferred from the completed host or the prior aborted-summary test.

## Persistent evidence

[Curated observations and source digests](evidence/runtime/normal-tcp-race-display-blocker.json) retain selected state, screenshot digests, errors, outcomes and limits. The complete VM race capture has2,396samples over600seconds, with zero capture-level errors. Capture-level success is independent of the failed game rendering.

Full raw sources and screenshots for this pass are under `/home/melroy/.local/state/nfs3-re/runtime/20261030-normal-tcp` on the host, outside `/tmp` and outside the public repository. The VM sources were copied to `vm-peer-evidence.tar.gz` there; SHA-256 `a99645a68733532faed878cb1c8c72dda1117e41c85f164fe7a0275818628c10` matches the guest archive. `SHA256SUMS` inventories the persistent private files. Unlike the older temporary captures, these sources are available for reanalysis on this machine. Startup/preflight attempts are retained separately and are not passed race observations.

No further user driving was requested after cancellation. A future recovery attempt could test VM Wine virtual-desktop mode in isolation, but that remains unperformed and would require restarting the VM game. The broad research acceptance gaps remain open.
