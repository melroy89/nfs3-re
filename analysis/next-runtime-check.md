# Next coordinated runtime check: ordinary Traffic Off

Status: **PREPARED, NOT RUN**. This is the missing Off comparison for issues11/12, using the completed [Traffic On baseline](evidence/runtime/ordinary-single-race-traffic-observation.json). It does not qualify other modes, tracks, larger grids or a density slider. Do not launch the game until the user is ready; do not edit the executable, configuration files or live memory.

## Player steps

1. One Player → Single Race; Hometown, Forward, Day, dry weather.
2. Stock Lamborghini Diablo SV;2laps; Number of Opponents **None**; Traffic **Off**. Keep AI skill Aggressive to match the captured baseline if selectable.
3. Wait for the assistant to confirm capture readiness, then start the race.
4. Drive normally for about60seconds after the start countdown. Report whether any traffic appears; pause when asked so the assistant can retain the roster snapshot.
5. Quit the race to the actual main menu. Confirm that the menu remains responsive. Leave the game open until capture completion and the process-survival check.

A menu label alone is insufficient: the assistant must read back the effective setup and race roster. Not seeing a traffic car is also insufficient without the roster evidence.

## Assistant capture and acceptance

Use `analysis/scripts/launch_music_shutdown_capture.py` with the installed, fingerprinted executable and existing NFS3 Wine prefix, a fresh output path, `--gameplay-state`, `--interval 0.1` and at most600seconds. The launcher must remain the game's parent to permit the read-only capture. Do not start a second game instance or change display modes as part of preparation.

Before player start, confirm metadata executable SHA-256 matches the baseline and sample records are growing without read errors. Retain actual loaded-module maps after initialization; early-start maps do not identify the racing backend.

During advancing race samples verify:

| Field | Expected for this comparison |
| --- | --- |
| session/race mode |0/0 |
| track/reverse/laps |0/0/2 |
| opponent choice / traffic disabled |0/1 |
| configured humans / human racers |1/1 |
| AI racers / AI police |0/0 |
| configured vehicle count |1, if the ordinary builder behaves as statically traced |
| readable vehicle categories |One player category0x05; no traffic category0x12 |

These values are predictions, not recorded results. If the effective settings differ, correct them through the ordinary game UI before interpreting the comparison. If the roster differs despite matching settings, retain the discrepancy; do not adjust the expected result to obtain a pass.

Retain timestamps, paused screenshot, selected setup/roster samples, raw-capture SHA-256, sampling errors and the user's observation. Confirm the actual main menu separately from the pause menu. After sampling ends, check that the same game process survives; the disposable-child launcher probe did not establish Wine survival. Read back the primary display mode and restore1920×1080 only if the game changed it, consistent with the user's requested desktop resolution.

Only after those observations may the ordinary local On/Off comparison be marked DONE. Other modes, density/performance, historical audio slowdown and overall research completion remain separate.
