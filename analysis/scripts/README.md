# Analysis helpers and reruns

Run the commands below from the repository root with Python 3. Internal reconstruction defaults are anchored to the script location, so they also work from another directory. External inputs and output arguments are explicit. Outputs below go to ignored `analysis/captures/reruns/`, preserving reviewed evidence.

## Inputs and dependencies

All helpers need Python 3. The six `probe_*` helpers additionally need the Python `pefile` package, GNU `as`/`ld` (power also uses `objdump`) and Linux i386 executable support. They enforce the documented executable SHA-256. Inventory and reconstruction use only the standard library. Runtime samplers require Linux `/proc`, a running matching NFS3 build and permission to read that process's memory.

Set the binary path for probe commands:

```sh
NFS3_BINARY="$PWD/nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe"
```

| Helper | Purpose and inputs | Output |
| --- | --- | --- |
| `probe_audio_delay_partitions.py` | Original delay initializer at five recognized rates and synthetic controls | Explicit JSON path |
| `probe_binary64_helpers.py` | Extracted subtraction/multiplication instructions from the binary | Explicit JSON path |
| `probe_binary64_division.py` | Software and x87 division instructions from the binary | Explicit JSON path |
| `probe_x87_atan2.py` | atan2 values and GPR/control-word preservation from the binary | Explicit JSON path |
| `probe_x87_power.py` | Power/helper instructions and exception-selector recording from the binary | Explicit JSON path |
| `probe_packed_prefix_decoder.py` | Synthetic canonical codebooks through extracted decoder instructions | Explicit JSON path |
| `inventory_vehicle_effect_tags.py` | Archived FCE effect tags, positions and extents | Required JSON `--output` |
| `inventory_track_map_segments.py` | COLL type15 record extents and track-map sampling counts | Required JSON `--output` |
| `inventory_sky_grid_parameters.py` | Labelled cloud/dome settings from installed track HRZ files | Required JSON `--output` |
| `inventory_car_physics.py` | CARP physics profiles from a complete installed game directory | JSON on stdout, or `--output` |
| `reconstruct_spike_contact.py` | Retained spike-contact-and-recovery/arrest JSON samples | Defaults to `analysis/evidence/runtime/spike-contact-reconstruction.json`; override recommended for comparison |
| `read_memory_sampler.py` | Live physics, pursuit/reset and spike geometry; PID required | Required `--output` JSONL |
| `capture_hud_state.py` | Live selected HUD descriptor, item23 and split bounds; PID required | JSONL on stdout |

## Offline commands

```sh
python3 analysis/scripts/probe_audio_delay_partitions.py "$NFS3_BINARY" --output analysis/captures/reruns/audio-delay-partitions-probe.json
python3 analysis/scripts/probe_binary64_helpers.py "$NFS3_BINARY" --output analysis/captures/reruns/binary64-helper-probe.json
python3 analysis/scripts/probe_binary64_division.py "$NFS3_BINARY" --output analysis/captures/reruns/binary64-division-probe.json
python3 analysis/scripts/probe_x87_atan2.py "$NFS3_BINARY" --output analysis/captures/reruns/x87-atan2-probe.json
python3 analysis/scripts/probe_x87_power.py "$NFS3_BINARY" --output analysis/captures/reruns/x87-power-probe.json
python3 analysis/scripts/probe_packed_prefix_decoder.py "$NFS3_BINARY" --output analysis/captures/reruns/packed-prefix-decoder-probe.json
python3 analysis/scripts/reconstruct_spike_contact.py --output analysis/captures/reruns/spike-contact-reconstruction.json
```

The reconstruction's optional `--input-dir` defaults to `analysis/evidence/runtime/`. It requires `spike-contact-and-recovery.json` and `spike-contact-and-arrest.json` in that directory; original raw captures are unnecessary.

For inventory, point to your complete installation (the repository's two game files are insufficient). This is the verified local installation:

```sh
NFS3_GAME_ROOT='/home/melroy/.local/share/winegui/prefixes/NFS3/drive_c/Program Files/Electronic Arts/Need For Speed III'
python3 analysis/scripts/inventory_car_physics.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/controller-profile-inventory.json
python3 analysis/scripts/inventory_sky_grid_parameters.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-sky-grid-parameters.json
python3 analysis/scripts/inventory_track_map_segments.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-track-map-segments.json
python3 analysis/scripts/inventory_vehicle_effect_tags.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-vehicle-effect-tags.json
```

## Runtime commands

These commands start new read-only captures; they do not replay historical ones. Discover and select the correct PID with `pgrep -x nfs3.exe`, then set `NFS3_PID` to that PID. Coordinate the scenario before sampling. Use `sudo` only when required by local process-memory permissions; never embed credentials.

```sh
mkdir -p analysis/captures
sudo python3 analysis/scripts/read_memory_sampler.py "$NFS3_PID" --seconds 300 --interval 0.02 --output analysis/captures/pursuit.jsonl
sudo python3 analysis/scripts/capture_hud_state.py "$NFS3_PID" --seconds 300 > analysis/captures/hud.jsonl
```

The general sampler offers mutually exclusive `--reset-only` and `--spike-only` modes; default duration is 900 seconds and interval 0.02 seconds. HUD sampling is five Hz, defaults to 300 seconds and caps duration at 600 seconds. Reads are non-atomic; neither sampler suspends or writes the game. All helpers provide `--help`; explicit output files create their parent directories (shell redirection requires `mkdir` as above).

## Capture dependencies and reproducibility

- No retained helper requires original raw JSONL input. Reconstruction needs only the two retained JSON files listed above. The six probes need the fingerprinted executable; inventory needs installed car assets; samplers need a new live game.
- Existing local HUD originals remain at `analysis/runtime/hud-layout-live.jsonl` and `analysis/runtime/hud-layout-target23.jsonl` and are ignored. Curated transitions are retained under `analysis/evidence/runtime/`. There is no retained automated extraction helper for that selection.
- Historical `/tmp/nfs3-astra/torque-live.jsonl`, `/tmp/nfs3-astra/pursuit-live.jsonl`, `/tmp/nfs3-ai-strip-FPDMiT/assignments.jsonl` and `/tmp/nfs3-reverse-deployment-kAJugn/samples.jsonl` are currently unavailable. Notes and retained samples support bounded review, not regeneration of missing full captures.
- Other JSON reports came from historical one-off analysis; an existing result is not a promise of a retained generator. Consult its provenance and related Markdown before attempting reproduction.

All five probe reruns, the inventory and spike reconstruction reproduced retained JSON byte-for-byte after relocation. Reconstruction was also run from outside the repository. Help checks passed for all nine helpers. Runtime commands were checked against their CLIs but not executed during this reorganization.

Probe stubs and input coverage limit interpretation; see script docstrings and [detailed notes](../detailed-analysis-notes.md). Reproducing a result does not newly validate caller reachability, gameplay behavior or unresolved contracts.

The added audio-delay partition probe executes the unchanged initializer, prime search and truncation helper with no stubs: 35 cases across seven rate inputs and five masked-exception control words. Five recognized rates fit the cleared workspace;0/65535 are synthetic controls, not demonstrated settings. An independent rerun from outside the repository reproduced its report exactly. This validates initialization arithmetic, not audio processing or startup/concurrency admission.

The sky inventory helper uses only the standard library and reads uppercase `GAMEDATA/TRACKS/TRK*/*.HRZ` paths. It reports file hashes, labelled values and skipped files; it is not a replacement for the game's complete positional parser. All36 local files had both labelled groups, with no skips, and a rerun from outside the repository reproduced the retained inventory exactly. No original raw captures are required.

The track-map inventory helper uses the standard library and requires installed uppercase `GAMEDATA/TRACKS/TRK*/*.COL` files. It validates file/directory/block extents, records hashes and derives sampling counts from type15 blocks. It needs no original captures and does not execute the loader or render a map. All nine local type15 blocks matched their36-byte record extents, and an outside-repository rerun reproduced the report exactly.

The vehicle-effect inventory uses the standard library and scans FCE members in installed `GAMEDATA/CARMODEL` VIV archives. It records archive/member hashes, tag bytes interpreted as ASCII, finite positions and member extents using the verified dispatcher offsets. It requires installed assets, no raw captures. All47 local FCE members yielded216 entries; an outside-repository rerun reproduced the report exactly. File admission does not establish post-load mutation, rendering outcomes or supported modified models. Syntax/help checks passed for all13 helpers at this checkpoint.

The effect inventory also records per-part vertex extents used by the render-record builder. These support the documented nonoverlap with effect header fields for the installed models; they do not validate all triangle indices, render allocations or live ownership.

`inventory_glyph_geometry.py` reads installed `GAMEDATA/RENDER/PC/TEST.GFX` using the cached loader layout. Standard library only; no raw captures. Run from the repository root:

```sh
python3 analysis/scripts/inventory_glyph_geometry.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-glyph-geometry.json
```

It reports file hash, glyph counts, vector finiteness, triangle-index bounds and packed extents. It does not execute resource resolution, generation, lighting or rendering. Retained findings are in `analysis/evidence/inventories/installed-glyph-geometry.json`.

The glyph helper additionally derives exact zero-area triangle counts and host binary64 normal lengths from stored binary32 values. These diagnostics do not model original x87 normalization or prove triangle winding. An outside-repository rerun reproduced the report exactly.

Glyph winding diagnostics compare stored face normals with `(v1-v0) × (v2-v0)` using host binary64. Sign/cosine results describe the cached asset convention, not driver culling correctness.
