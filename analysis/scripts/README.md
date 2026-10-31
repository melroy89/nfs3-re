# Analysis helpers and reruns

Run the commands below from the repository root with Python 3. Internal reconstruction defaults are anchored to the script location, so they also work from another directory. External inputs and output arguments are explicit. Outputs below go to ignored `analysis/captures/reruns/`, preserving reviewed evidence.

## Inputs and dependencies

All helpers need Python 3. The nine `probe_*` helpers additionally need the Python `pefile` package, GNU `as`/`ld` (power also uses `objdump`) and Linux i386 executable support. They enforce the documented executable SHA-256. Inventory and reconstruction use only the standard library. Runtime samplers require Linux `/proc`, a running matching NFS3 build and permission to read that process's memory.

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
| `probe_line_boundary_helper.py` | Synthetic finite, boundary, zero-slope and NaN cases through unchanged `00485c30` bytes | Explicit JSON path |
| `probe_triangle_corner_masks.py` | Finite triangle grid through unchanged intersection/segment-clip bytes; evaluates the two assembly corner selectors | Required JSON `--output` |
| `probe_rectangle_fragment_masks.py` | All 16 masks through the unchanged rectangle-fragment helper and jump table; checks output union and paired-coordinate mapping | Required JSON `--output` |
| `model_hud_fragment_worklist_capacity.py` | Assembly-derived caller-loop model using the retained 16-mask helper report; synthetic exclusion rectangles only | Defaults to `analysis/evidence/probes/hud-fragment-worklist-capacity-model.json`; override with `--output` |
| `inventory_vehicle_effect_tags.py` | Archived FCE effect tags, positions and extents | Required JSON `--output` |
| `inventory_track_map_segments.py` | COLL type15 record extents and track-map sampling counts | Required JSON `--output` |
| `inventory_coll_basis_vectors.py` | Signed-byte basis-vector lengths and within-record pairwise dot products from installed COLL type15 records | Required JSON `--output` |
| `inventory_track_frd_basis_indices.py` | Sequential FRD packed-basis counts and indices selected through COLL type15 segment descriptors | Required JSON `--output` |
| `inventory_frontend_text_boundaries.py` | Longest raw token and contiguous tab run in retained `fedata_org` `.MNU`/`.TXT` files; does not parse indexed localization tables | Required JSON `--output` |
| `inventory_localized_text_table.py` | Validates the six indexed `text.<language>` tables and inventories HUD speed labels, token lengths and tab runs | Defaults to `analysis/evidence/inventories/indexed-localized-text-tables.json`; override with `--output` |
| `inventory_sky_grid_parameters.py` | Labelled cloud/dome settings from installed track HRZ files | Required JSON `--output` |
| `inventory_car_physics.py` | CARP physics profiles, including raw and low-byte `usesanti` values, from a complete installed game directory | JSON on stdout, or `--output` |
| `inventory_car_selector_categories.py` | FEDATA selector fields across installed VIV car archives and supported language suffixes | Required JSON `--output` |
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
python3 analysis/scripts/probe_line_boundary_helper.py "$NFS3_BINARY" --output analysis/captures/reruns/line-boundary-helper-probe.json
python3 analysis/scripts/probe_triangle_corner_masks.py "$NFS3_BINARY" --output analysis/captures/reruns/triangle-corner-mask-grid.json
python3 analysis/scripts/probe_rectangle_fragment_masks.py "$NFS3_BINARY" --output analysis/captures/reruns/rectangle-fragment-mask-audit.json
python3 analysis/scripts/inventory_frontend_text_boundaries.py --output analysis/captures/reruns/frontend-text-boundary-scan.json
python3 analysis/scripts/inventory_localized_text_table.py --output analysis/captures/reruns/indexed-localized-text-tables.json
python3 analysis/scripts/model_hud_fragment_worklist_capacity.py --output analysis/captures/reruns/hud-fragment-worklist-capacity-model.json
python3 analysis/scripts/reconstruct_spike_contact.py --output analysis/captures/reruns/spike-contact-reconstruction.json
```

The reconstruction's optional `--input-dir` defaults to `analysis/evidence/runtime/`. It requires `spike-contact-and-recovery.json` and `spike-contact-and-arrest.json` in that directory; original raw captures are unnecessary.

For inventory, point to your complete installation (the repository's two game files are insufficient). This is the verified local installation:

```sh
NFS3_GAME_ROOT='/home/melroy/.local/share/winegui/prefixes/NFS3/drive_c/Program Files/Electronic Arts/Need For Speed III'
python3 analysis/scripts/inventory_car_physics.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/controller-profile-inventory.json
python3 analysis/scripts/inventory_car_selector_categories.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-car-selector-categories.json
python3 analysis/scripts/inventory_sky_grid_parameters.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-sky-grid-parameters.json
python3 analysis/scripts/inventory_track_map_segments.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-track-map-segments.json
python3 analysis/scripts/inventory_coll_basis_vectors.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-coll-basis-vectors.json
python3 analysis/scripts/inventory_track_frd_basis_indices.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-track-frd-basis-indices.json
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

- No retained helper requires original raw JSONL input. Reconstruction needs only the two retained JSON files listed above. The nine original-byte probes need the fingerprinted executable; the HUD worklist model needs only the retained rectangle-helper report; inventory needs installed car assets; samplers need a new live game.
- Existing local HUD originals remain at `analysis/runtime/hud-layout-live.jsonl` and `analysis/runtime/hud-layout-target23.jsonl` and are ignored. Curated transitions are retained under `analysis/evidence/runtime/`. There is no retained automated extraction helper for that selection.
- Historical `/tmp/nfs3-astra/torque-live.jsonl`, `/tmp/nfs3-astra/pursuit-live.jsonl`, `/tmp/nfs3-ai-strip-FPDMiT/assignments.jsonl` and `/tmp/nfs3-reverse-deployment-kAJugn/samples.jsonl` are currently unavailable. Notes and retained samples support bounded review, not regeneration of missing full captures.
- Other JSON reports came from historical one-off analysis; an existing result is not a promise of a retained generator. Consult its provenance and related Markdown before attempting reproduction.

At the initial evidence-reorganization checkpoint, five probe reruns, the inventory and spike reconstruction reproduced retained JSON byte-for-byte after relocation. Reconstruction was also run from outside the repository, and help checks covered the then-current nine helpers. Later additions and their validation are documented below. Runtime commands were checked against their CLIs but not executed during that reorganization.

Probe stubs and input coverage limit interpretation; see script docstrings and [detailed notes](../detailed-analysis-notes.md). Reproducing a result does not newly validate caller reachability, gameplay behavior or unresolved contracts.

The added audio-delay partition probe executes the unchanged initializer, prime search and truncation helper with no stubs: 35 cases across seven rate inputs and five masked-exception control words. Five recognized rates fit the cleared workspace;0/65535 are synthetic controls, not demonstrated settings. An independent rerun from outside the repository reproduced its report exactly. This validates initialization arithmetic, not audio processing or startup/concurrency admission.

`probe_line_boundary_helper.py` extracts unchanged bytes `00485c30..00485f1a` from the fingerprinted PE and calls them directly in a freestanding i386 ELF at their original address. Its 40 records combine20 synthetic cases with helper policy ECX=0/1; all preserve seeded mask bits. The retained first report is `analysis/evidence/probes/line-boundary-helper-probe.json`. It exercises representative edge/axis mappings, signed-zero vertical and zero-length inputs, a line-extension candidate, a parallel out-of-bounds line and two NaN cases. It does not run the wrapper/callers, so direct calls at an endpoint already on the rectangle boundary do not establish a reachable caller path. The policy-zero pointer behavior is not evidence that a candidate is finite or in bounds. Control word037f masks exceptions; other control words and caller-admitted values remain untested. Help, JSON validation and a byte-for-byte rerun passed.

`probe_triangle_corner_masks.py` executes the unchanged helper and `ClipFloatSegmentToRectangle` bytes at their original VAs for 117,649 finite triangles (352,947 edge calls) against a seven-value coordinate grid and rectangle `[0,0,1,1]`. It applies the statically reviewed pre-clip swap and corner-selector predicates; it does not execute `00487a30` or its emitters. The retained report `analysis/evidence/probes/triangle-corner-mask-grid.json` contains two unmatched-mask witnesses and counts: 495 of 7,979 corner-selector cases lack one of the four explicit adjacent-side pairs. This establishes a synthetic function-boundary path to unassigned corner scratch, not reachability from `RenderEngineRpmNeedle`, visible corruption or a game defect. No raw captures are needed; the fingerprinted PE is required.

`probe_rectangle_fragment_masks.py` executes the unchanged helper `00486340` and its absolute jump table at their original VAs for all16 positive-overlap masks plus disjoint and edge-contact cases. The retained report `analysis/evidence/probes/rectangle-fragment-mask-audit.json` verifies `count=popcount(mask)`, paired-coordinate interpolation, and exact union coverage of the source outside the intersection. It also finds overlapping corner strips for masks`0xd`, `0xe` and`0xf`; the report quantifies their duplicate area. This is not evidence of a visible blend defect: caller data, queued texture/blend state and actual rendering are not exercised. No raw captures are needed; the fingerprinted PE is required.

`model_hud_fragment_worklist_capacity.py` maps those16 retained helper outputs through the reviewed replace/append/delete/restart loop in `ClipAndSubmitHudTexturedRectangleFragments`. A fixed witness of four pairwise-disjoint exclusions yields28 modeled fragments; the caller's two local arrays each hold15 records, and the first modeled out-of-bounds append targets record index15. This is a synthetic caller model, not execution of the caller bytes. It does not establish that live HUD producers can admit the witness, so no reachable overflow or game defect is claimed. It needs only the retained rectangle-helper report and Python's standard library; no raw capture or PE is needed.

The sky inventory helper uses only the standard library and reads uppercase `GAMEDATA/TRACKS/TRK*/*.HRZ` paths. It reports file hashes, labelled values and skipped files; it is not a replacement for the game's complete positional parser. All36 local files had both labelled groups, with no skips, and a rerun from outside the repository reproduced the retained inventory exactly. No original raw captures are required.

The track-map inventory helper uses the standard library and requires installed uppercase `GAMEDATA/TRACKS/TRK*/*.COL` files. It validates file/directory/block extents, records hashes and derives sampling counts from type15 blocks. It needs no original captures and does not execute the loader or render a map. All nine local type15 blocks matched their36-byte record extents, and an outside-repository rerun reproduced the report exactly.

`inventory_coll_basis_vectors.py` uses the standard library and scans the same installed COLL type15 records. It hashes each file and measures three signed-byte XYZ vectors at offsets0x10/0x14/0x18 after dividing components by128; it reports host binary64 lengths and absolute pairwise dot products. No raw captures are needed. These measurements follow statically identified fallback-basis reads, but do not establish branch admission or cover packed FRD bases, loader execution, runtime transforms, or normalization behavior. The retained report is `analysis/evidence/inventories/installed-coll-basis-vectors.json`.

`inventory_track_frd_basis_indices.py` uses the standard library and requires matching installed uppercase `GAMEDATA/TRACKS/TRK*/*.FRD` and `.COL` files. It follows the loader's first per-block FRD pass through the packed-basis tables at block+`0x598`, maps COLL type15 segment ordinals to FRD descriptors, and checks each selected material byte0 against that block's basis count. It records file hashes, table offsets, counts and index extrema. It stops before later FRD loader passes and does not execute the game or establish successful runtime loading. The retained asset report is `analysis/evidence/inventories/installed-track-frd-basis-indices.json`.

The selector-category inventory uses the standard library and reads FEDATA members in installed `GAMEDATA/CARMODEL` VIV archives whose suffix appears in the executable's language-code table. It records archive/member hashes, the little-endian DWORD at FEDATA+8 interpreted with the loader's arithmetic shift, the identifier at+0x18, and related metadata flag words. It requires the complete installed game directory and no raw captures. The retained report covers58 archives,139 supported-language FEDATA members across24 model directories; six languages are present and localized selector values agree within each directory. `KNOC` has selector255; this file finding does not prove loader admission or a reachable group-store write. Other FEDATA suffixes, loose files, modified cars and runtime state are outside the report. The current script inventory has23 Python helpers, including the unchanged-code geometry probes and the assembly-derived HUD worklist model.

The vehicle-effect inventory uses the standard library and scans FCE members in installed `GAMEDATA/CARMODEL` VIV archives. It records archive/member hashes, tag bytes interpreted as ASCII, finite positions and member extents using the verified dispatcher offsets. It requires installed assets, no raw captures. All47 local FCE members yielded216 entries; an outside-repository rerun reproduced the report exactly. File admission does not establish post-load mutation, rendering outcomes or supported modified models.

The effect inventory also records per-part vertex extents used by the render-record builder. These support the documented nonoverlap with effect header fields for the installed models; they do not validate all triangle indices, render allocations or live ownership.

`inventory_glyph_geometry.py` reads installed `GAMEDATA/RENDER/PC/TEST.GFX` using the cached loader layout. Standard library only; no raw captures. Run from the repository root:

```sh
python3 analysis/scripts/inventory_glyph_geometry.py "$NFS3_GAME_ROOT" --output analysis/captures/reruns/installed-glyph-geometry.json
```

It reports file hash, glyph counts, vector finiteness, triangle-index bounds and packed extents. It does not execute resource resolution, generation, lighting or rendering. Retained findings are in `analysis/evidence/inventories/installed-glyph-geometry.json`.

The glyph helper additionally derives exact zero-area triangle counts and host binary64 normal lengths from stored binary32 values. These diagnostics do not model original x87 normalization or prove triangle winding. An outside-repository rerun reproduced the report exactly.

Glyph winding diagnostics compare stored face normals with `(v1-v0) × (v2-v0)` using host binary64. Sign/cosine results describe the cached asset convention, not driver culling correctness.

## Music-shutdown capture

`sample_music_shutdown.py` is a bounded read-only sampler for the unresolved race-exit/menu slowdown. It fingerprints the supplied executable, verifies the live fixed-map code signature and process identity, and captures16 raw voice records plus the music handle/target. It does not suspend, write memory, or follow voice pointers. Output creation is exclusive to preserve prior captures.

After rediscovering the correct PID and coordinating the scenario:

```sh
sudo python3 analysis/scripts/sample_music_shutdown.py "$NFS3_PID" --exe "$NFS3_EXE" --seconds 180 --interval 0.1 --output analysis/captures/music-shutdown.jsonl
```

Set `NFS3_EXE` to the exact installed build; never embed credentials. Confirm the READY message and sample growth before asking for game actions. Start at the main menu, enter a normal single race with music enabled, then return to the menu; record action times and reported responsiveness. A smooth run does not reproduce the historical GOFAST slowdown. Capture snapshots cannot establish callback cadence/writer order by themselves. CLI help and invalid-duration/interval cases were checked. A completed ordinary-race run verified image/signature, read-only access and5,251samples with no capture errors. Traffic and responsive main-menu return were observed; the historical slowdown did not reproduce. The optional `--gameplay-state` adds named setup globals and bounded activity snapshots for up to16 configured vehicles. Those fields can retain prior setup values at the menu, and active bytes do not prove visible traffic. Reads remain asynchronous. Normal Linux parent-to-child access can be used by launching Wine from the capture process; a separate same-user reader may be denied access. No global permission changes or memory writes are required.

## Bounded HUD exclusion model

Run `python3 analysis/scripts/model_hud_bounded_exclusion_capacity.py` to enumerate194481 ordered two-rectangle topologies from the retained original-helper templates and assembly-derived caller model. Output: `analysis/evidence/probes/hud-bounded-exclusion-capacity.json`. It records peak and final populations separately and checks overflow across every case, including cases later deleted. Parent rerun reproduced maximum peak/final11 and no overflow. This is a model, not original caller execution or runtime admission proof; see `analysis/hud-exclusion-reachability-audit.md` for default producer gates and nondefault/stale-state limitations.

## Replay encoder original-byte probe

Run `python3 analysis/scripts/probe_replay_encoder.py "$NFS3_EXE" --output analysis/evidence/probes/replay-encoder-original-byte-probe.json`. Requires GNU as/ld and Linux i386 execution support; it validates the executable fingerprint and executes unchanged extracted encoder bytes in a temporary freestanding ELF.520 synthetic rows match (including the Handbrake04 action witness) the branch model, including44-byte maximum witness and8/8/15/34 intermediate lengths. Recorder cursor arithmetic is checked against static caller evidence; recorder/game/Wine execution, actual input configuration and runtime overwrite are not established. Temporary harness files are removed after the subprocess returns.

The temporary launcher used for the first run shared its process session with Wine; stopping that capture was followed by game exit. The permanent `launch_music_shutdown_capture.py` launches Wine in its own session and runs the sampler in the same parent process, retaining normal parent-to-child read permission without sudo. It refuses an already running game, the wrong executable fingerprint, invalid timing, or existing output/log paths before launching. It never intentionally signals the game or restores/changes display settings.

For a separately coordinated new run:

```sh
python3 analysis/scripts/launch_music_shutdown_capture.py --exe "$NFS3_EXE" --prefix "$NFS3_PREFIX" --seconds 180 --interval 0.1 --gameplay-state --output analysis/captures/music-shutdown-new.jsonl
```

The Wine log is created exclusively beside that capture. Readiness still requires the READY message and growing samples. A disposable child-process integration probe verified parent read-only access with a separate child session and child survival after the parent/tool command ended; the owned probe was cleaned up. Existing-output and invalid-duration checks passed without launching Wine. The corrected helper has not yet been exercised with a new game run, so Wine survival and display restoration remain explicit next-run checks.

The sampler also emits a `kind=maps` record every30seconds, in addition to the initial metadata map. Later module presence can establish mapping during that interval; it does not prove API calls or successful rendering. The previous completed capture predates these periodic records and therefore remains early-map-only evidence.


## Fixed reference-export sample

`export_reference_samples.py` and `ghidra/ExportReferenceSample.java` export only `00485c30`, `004abd9c` and `00518640` from an isolated, hash-checked saved snapshot. They create reference C/headers under ignored `analysis/captures/reference-exports/`; they do not create maintained C, install tools, compile/link C or execute game/probe instructions. The coordinator pins options/tool/runner identities, retains per-entry diagnostics/results, imposes deadlines and compares two runs. Inline warnings embedded in exported text require the additional source inspection recorded in the run manifests.

See [completed results and exact invocation](../reference-export-results.md) and [the bounded export procedure](../recompilation-readiness.md#pinned-reference-export-procedure-executed-for-the-fixed-sample). Existing results are never overwritten. Raw files stay local; curated metadata is tracked separately.

## Original versus official Modern byte inventory

`ghidra/ExportFunctionInventory.java` exports function names, half-open address ranges, thunk markers and program identity. Run it on the saved Modern project with `-readOnly -noanalysis`; analyze the original in a separate capture project. Do not import the original over the maintained Modern program. The comparison requires Python `pefile` and the retained metadata inventories:

```sh
python3 analysis/scripts/compare_nfs3_executables.py \
  --original 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3_org.exe' \
  --modern analysis/captures/modern-differences/upstream/package/nfs3.exe \
  --local 'nfs3_decomp.rep/Electronic Arts/Need For Speed III/nfs3.exe' \
  --functions analysis/captures/modern-differences/functions-modern.json \
  --original-functions analysis/captures/modern-differences/functions-original.json \
  --output analysis/captures/modern-differences/comparison-rerun.json
```

Compare the rerun JSON with the retained [curated inventory](../evidence/audits/original-modern-function-diff.json). Inputs and their hashes are recorded in that inventory; raw downloads and Ghidra metadata remain ignored. Same-address bytes establish byte correspondence, not semantic function matching. Original autoanalysis entries are boundary candidates. See [the measured report and limitations](../original-modern-differences.md).

## Original versus Modern THRASH loader

Run `python3 analysis/scripts/audit_thrash_loader_difference.py` from the repository root. Requires Python `pefile` and GNU `objdump`. It checks both executable hashes, captures pinned instruction spans, decodes Modern's name/slot table as data, and compares all 34 bindings with the original explicit lookups/stores. Output: `analysis/evidence/audits/original-modern-thrash-loader.json`; raw assembly remains under ignored `analysis/captures/modern-differences/thrash-loader/`. The parent repeated the script and reproduced identical curated JSON. This is static evidence only; no renderer or game execution.

## Original versus Modern window registrations

Run `python3 analysis/scripts/audit_window_initialization_difference.py` from the repository root. Requires Python `pefile`, GNU `objdump`, and the baseline definitions in `audit_thrash_loader_difference.py`. It hash-checks both binaries, captures pinned initializer/callback/dispatcher spans and extracts 26 original versus 27 Modern direct registrations. Curated JSON: `analysis/evidence/audits/original-modern-window-initialization.json`; raw captures remain ignored. No target execution or Ghidra changes. See [findings and limitations](../original-modern-window-handling.md).

## Original versus Modern screenshot paths

Run `python3 analysis/scripts/audit_screenshot_difference.py` from the repository root (Python `pefile`, GNU `objdump`; shared baseline definitions in `audit_thrash_loader_difference.py`). It checks input hashes and retains instruction/filename witnesses in `analysis/evidence/audits/original-modern-screenshots.json`, with raw assembly under ignored captures. No game or instruction execution. See [the screenshot comparison](../original-modern-screenshots.md).

## Original versus Modern network port paths

Run `python3 analysis/scripts/audit_network_port_difference.py` from the repository root (Python `pefile`, GNU `objdump`; baseline definitions from `audit_thrash_loader_difference.py`). It checks both fingerprints and captures matched service initialization, endpoint adapter/dispatch, menu bodies and new Modern getter/parser/retry spans. Curated output: `analysis/evidence/audits/original-modern-network-port.json`; raw assembly stays ignored. No socket, game or instruction execution. See [endpoint findings](../original-modern-network-endpoints.md) and [menu findings](../original-modern-network-port-menu.md).

## Original versus Modern startup policy and RAM pool

Run `python3 analysis/scripts/audit_startup_policy_difference.py` from the repository root (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). It captures removed original error-mode sites, Modern configuration/API resolution, RAM pool entry/adapter/allocator and original null-pointer guard. Curated output: `analysis/evidence/audits/original-modern-startup-policy.json`. Raw assembly stays ignored; no target/API execution or Ghidra mutation. See [startup policy](../original-modern-startup-policy.md) and [heap comparison](../original-modern-heap-initialization.md).

## Original versus Modern display modes and texture extents

Run `python3 analysis/scripts/audit_display_mode_difference.py` and `python3 analysis/scripts/audit_texture_extent_difference.py` (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). They capture matched enumerator/list-builder and texture caller/helper spans, retaining `original-modern-display-modes.json` and `original-modern-texture-extents.json` under `analysis/evidence/audits/`. Raw assembly remains ignored. No target, renderer or UI execution. The display capture also includes original video initialization and Modern lookup/application spans, paired default-setting paths and Modern request/menu/desktop-helper witnesses; see [mode selection](../original-modern-mode-selection.md). See [display findings](../original-modern-display-modes.md) and [texture findings](../original-modern-texture-limits.md).

## Original versus Modern viewport and border geometry

Run `python3 analysis/scripts/audit_viewport_geometry_difference.py` (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). It retains initializer/setter/border spans, six builder caller instructions and exact file-backed float values in `analysis/evidence/audits/original-modern-viewport-geometry.json`. Raw assembly remains ignored. No rendering or target execution. See [viewport formulas](../original-modern-viewport-geometry.md) and [border changes](../original-modern-border-geometry.md).

## Original versus Modern menu input and chat

Run `python3 analysis/scripts/audit_menu_input_difference.py` (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). It captures matched dispatch/named-key/chat paths and asserts identical lobby, previous/next and sender body bytes. Output: `analysis/evidence/audits/original-modern-menu-input.json`; raw assembly stays ignored. No UI, network or target execution. See [the input comparison](../original-modern-menu-input.md).

## Original versus Modern HUD presets and loading artwork

Run `python3 analysis/scripts/audit_hud_layout_difference.py` and `python3 analysis/scripts/audit_loading_artwork_difference.py` (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). They retain input/span hashes and preset/constant provenance in `original-modern-hud-layout.json` and `original-modern-loading-artwork.json` under `analysis/evidence/audits/`. The scripts check the retained shared HUD tail and floor/ceil bodies. Raw assembly stays ignored. No target/renderer execution. See [HUD](../original-modern-hud-layout.md) and [loading](../original-modern-loading-artwork.md) findings.

## Original versus Modern startup paths

Run `python3 analysis/scripts/audit_startup_paths_difference.py` (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). It captures original setter/frontend witnesses and Modern startup/CWD/INI/directory helpers. It resolves initialized path slots from the file-backed source table, without misreading destination BSS as file strings. Output: `analysis/evidence/audits/original-modern-startup-paths.json`; raw captures stay ignored. No filesystem/API/target mutation. See [the path comparison](../original-modern-startup-paths.md).

## Original versus Modern clock and loading timing

Run `python3 analysis/scripts/audit_clock_source_difference.py` (Python `pefile`, GNU `objdump`; shared hash-pinned baselines). It verifies 16 paired clock calls and exact timer-body equality after normalizing only the identified IAT operands in temporary comparison buffers. It also captures loading helpers, settings and timing/input consumers. Output: `analysis/evidence/audits/original-modern-clock-source.json`; raw assembly stays ignored. No target/API execution or executable changes. See [clock](../original-modern-clock-source.md) and [loading timing](../original-modern-loading-timing.md) findings.

## Renderer selection and DirectDraw compatibility

Run `python3 analysis/scripts/audit_renderer_selection_difference.py` (Python `pefile`, GNU `objdump`). It hash-checks both baselines and captures the complete original selector body/environment writer and Modern type/optional compatibility dispatch, including exact file-backed names. It also captures callback installation, original/Modern video initialization and environment setup, and asserts the shared `005176aa..0051776b` tail is identical. Output: `analysis/evidence/audits/original-modern-renderer-selection.json`. Raw captures remain ignored; no target/DLL execution. See [renderer findings](../original-modern-renderer-loading.md) and [initialization dispatch](../original-modern-renderer-initialization.md).

The screenshot audit additionally retains the resource-loading/playback wrappers and hashed `RCDATA/SNAP.WAV` payload metadata; it does not play the resource. See [repeat, numbering and sound](../original-modern-screenshot-feedback.md).

The screenshot audit also captures the original TGA builder and depth-16 conversion helper for the [pixel representation comparison](../original-modern-screenshot-pixels.md). Header/bit-copy findings are static, not encoded-image tests.

The window initialization audit additionally captures original/Modern creation bodies and asserts equality of the pre-tail creation range and three complete sizing helpers. See [window geometry](../original-modern-window-geometry.md); equality of these instructions does not establish identical inputs or runtime results.

## Original versus Modern CPU tier

Run `python3 analysis/scripts/audit_cpu_tier_difference.py` (Python pefile, GNU objdump). It hash-checks both baselines and captures the original estimate, Modern feature-score producer/CPUID wrapper, matched consumers and exact default byte tables. Curated output: `analysis/evidence/audits/original-modern-cpu-tier.json`; raw captures remain ignored. No CPUID/benchmark/target execution. See [CPU findings](../original-modern-cpu-tier.md).

## Original versus Modern frontend sound

Run `python3 analysis/scripts/audit_frontend_sound_difference.py` (Python pefile, GNU objdump). It retains paired request bodies and Modern volume-slider/restore witnesses, records floating constants and asserts the normal record initializer is identical. Output: `analysis/evidence/audits/original-modern-frontend-sound.json`; raw captures remain ignored. No audio/target execution. See [frontend sound findings](../original-modern-frontend-sound.md).

## Original versus Modern music selection

Run `python3 analysis/scripts/audit_music_selection_difference.py` (Python pefile, GNU objdump). It captures paired contextual policy, original race selection and Modern race/menu helpers, caller witnesses and exact selection tables. Output: `analysis/evidence/audits/original-modern-music-selection.json`; raw captures remain ignored. No audio/RNG/target execution. See [music findings](../original-modern-music-selection.md).
