# Host / Debian13 VM TCP multiplayer baseline

## Verified bounded result

The user connected two instances of the documented NFS3 build through **client-to-server TCP**, with host192.168.1.227:9803 and guest192.168.1.111:34019. Host and guest socket readbacks show the established connection. Both lobby screenshots show two player/car records, and built-in chat `Melroy: hi` appears on both. The VM player was subsequently renamed `Melroy_VM` to distinguish it from host `Melroy`.

Both peers then loaded Hometown multiplayer racing: screenshots render the track, cars,1/2lap HUD and two-player labels. The host reads2ndof2 and the VM1stof2 in asynchronous screenshots. These prove race loading/rendering and displayed participant state, not synchronized position/latency or race completion.

[Retained evidence](evidence/runtime/tcp-host-vm-lobby-chat.json) includes socket endpoints, the identical executable SHA-256, screenshot digests, user observations and remaining gates. The VM runs Debian13/Wine10 with a separate WineGUI nfs3 prefix. A persistent NetworkManager br0 bridge uses physical eno1; the host retains192.168.1.227 and the VM receives its own DHCP LAN address192.168.1.111. Host-to-guest and guest-to-host ping both passed. This is two OS peers on one physical machine and LAN, not an internet/WAN or peer-to-peer-mode test.

## Input/display qualifications

The VM uses a Wayland desktop with Xwayland. Its game menu/race renders despite a logged display-mode-change failure. The user reports mouse motion is unsuitable and uses the keyboard. Mouse capture is not fixed or qualified.

The user reports feeling Fanatec force feedback on the host, then clarifies that wheel driving controls are not really working. This is a positive user-observed force-feedback result alongside unresolved steering/pedal usability. It neither establishes a calibrated force-feedback implementation nor identifies a Linux/Wine/game cause. The VM keyboard is used for the next motion check.

## Acceptance still open

- Visible remote motion on both peers and response after focus switches.
- Quantified timing, divergence/recovery, seams, collision and input-provider behavior.
- Complete race/results agreement, ready/next-round behavior and a complete online series.
- Graceful leave/rejoin and disconnect outcomes.
- Peer-to-peer mode, independent physical machines, separate networks and public-service availability.

The basic TCP lobby, chat delivery and two-peer race-load/rendering checks are DONE for this scenario. The broader networking research and enhancement issues remain open.
