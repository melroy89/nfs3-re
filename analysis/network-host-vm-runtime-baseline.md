# Host / Debian13 VM TCP multiplayer baseline

## Verified bounded result

The user connected two instances of the documented NFS3 build through **client-to-server TCP**, with host192.168.1.227:9803 and guest192.168.1.111:34019. Host and guest socket readbacks show the established connection. Both lobby screenshots show two player/car records, and built-in chat `Melroy: hi` appears on both. The VM player was subsequently renamed `Melroy_VM` to distinguish it from host `Melroy`.

Both peers then loaded Hometown multiplayer racing: screenshots render the track, cars,1/2lap HUD and two-player labels. The host reads2ndof2 and the VM1stof2 in asynchronous screenshots. These prove race loading/rendering and displayed participant state, not synchronized position/latency or race completion.

[Retained evidence](evidence/runtime/tcp-host-vm-lobby-chat.json) includes socket endpoints, the identical executable SHA-256, screenshot digests, user observations and remaining gates. The VM runs Debian13/Wine10 with a separate WineGUI nfs3 prefix. A persistent NetworkManager br0 bridge uses physical eno1; the host retains192.168.1.227 and the VM receives its own DHCP LAN address192.168.1.111. Host-to-guest and guest-to-host ping both passed. This is two OS peers on one physical machine and LAN, not an internet/WAN or peer-to-peer-mode test.

## Input/display qualifications

The VM uses a Wayland desktop with Xwayland. Its game menu/race renders despite a logged display-mode-change failure. The user reports mouse motion is unsuitable and uses the keyboard. Mouse capture is not fixed or qualified.

The user reports feeling Fanatec force feedback on the host, then clarifies that wheel driving controls are not really working. This is a positive user-observed force-feedback result alongside unresolved steering/pedal usability. It neither establishes a calibrated force-feedback implementation nor identifies a Linux/Wine/game cause. The VM keyboard is used for the next motion check.

## Acceptance still open

- The user observed both cars moving in sync during this LAN run; measured latency/divergence/recovery and input/focus-switch response remain open.
- Quantified timing, divergence/recovery, seams, collision and input-provider behavior.
- Normal two-finisher race/results agreement, ready/next-round behavior and a complete online series; the exercised abort summaries agree as documented below.
- Graceful leave/rejoin and disconnect outcomes.
- Peer-to-peer mode, independent physical machines, separate networks and public-service availability.

The basic TCP lobby, chat delivery and two-peer race-load/rendering checks are DONE for this scenario. The broader networking research and enhancement issues remain open.

## Subsequent driving observation

The user confirms both cars are visible and movement appears in sync while driving `Melroy_VM` with the keyboard. A bounded read-only VM snapshot independently confirms sessionmode4/racemode0, Hometown/forward/2laps, two configured human racers, zero AI/traffic and local index1. Both vehicle records are active category0x05. At simulation/sequence18970 their progress values are9 and60, wrap counters0 and result states0; neither is proved finished. The exact executable digest and fixed-code signature were checked before opening the process memory O_RDONLY. These asynchronous fields do not measure network latency or cross-peer position error.

The user also feels wheel effects while driving the VM car. The generating process and any device-forwarding route are not established. Host wheel driving remains unsuitable; no calibrated force-feedback or general controller-compatibility conclusion follows.

## VM finish followed by host abort

The user completed the VM car's two laps. The guarded read-only monitor observes local participant1 with wrap counter2 for configured2laps, progress1921 and result state3 at tick32158. Its view subsequently shows the unfinished host car. This is a completed VM participant, not a normal whole-session completion.

The host then used Quit Race because its wheel controls prevented finishing the other car. **Both peer race summaries display both entries as Aborted, place N/A.** They agree on the player names and top speeds: Melroy121.68KPH and Melroy_VM262.51KPH. The established TCP connection remains. Screenshot digests and the pre-abort finished state are retained in the evidence artifact. The earlier VM finish state therefore must not be presented as a preserved final winning result: the subsequent global-abort summary labels both aborted.

This verifies matching ordinary abort summaries for this exercised sequence. It does not qualify a normal two-finisher result table, final placements, a complete tournament/knockout series, all interruption policies or reconnect behavior. The user ended testing for the night. The working host/VM setup is retained; no further test is scheduled or automatically launched.

Evidence retention: the selected JSON observations and screenshot digests are committed, but the `/tmp` screenshot files themselves are no longer present at final review. The historical screenshot observations are documented above; this checkout alone cannot replay their visual inspection or rehash the missing originals.

The later [bounded normal-results follow-up](normal-tcp-race-validation.md) confirms the opposite role’s host finish reached the VM, but persistent VM black rendering prevented the VM finish and normal result/next-race checks. Its raw evidence is archived persistently; no successful normal-results claim follows.
