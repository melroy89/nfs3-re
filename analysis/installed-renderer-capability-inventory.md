# Installed renderer capability inventory

## Scope and evidence boundary

This inventory concerns the selected installed NFS3 build, SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`, at:

`/home/melroy/.local/share/winegui/prefixes/NFS3/drive_c/Program Files/Electronic Arts/Need For Speed III`

Evidence combines the install's INI files, DLL version resources and hashes, the patch README, selected executable bytes, and the first metadata line of `/tmp/nfs3-gameplay-capture-qjhkt_79/samples.jsonl`. That capture line is an early-start memory-map snapshot: it was taken before game startup completed. It is not a map of the later race interval. The 5,251-sample run had zero read errors and observed visible traffic in an ordinary race and a responsive return to the actual main menu, but no later module maps were captured. Therefore early presence is evidence of early mapping; early absence says nothing conclusive about later renderer loading.

## Selected configuration and installed files

`nfs3.ini` (285 bytes, SHA-256 `a700df1b45d789159978cb514f6580c5720ec1a9401f02a853e473f3493ca2f1`) sets `ThrashDriver=nglide` and `AllowHugeTextures=0`. The selected driver directory's `drivers/nglide/thrash.ini` (166 bytes, SHA-256 `e2c4e128a3c9dd7fb6cddf10a83e29613f70c392e8b938eac0577a66ff98022c`) selects `File=voodoo2a.dll`, `Type=voodoo`, and `FogSupport=1`; it sets nGlide VSync on and selects game-controlled resolution. These files establish the configured choice, not successful loading or actual runtime use.

| Installed file | SHA-256 | Identity evidence |
|---|---|---|
| `drivers/nglide/glide3x.dll` | `87842a85d1bfda4217e691a9d4412915c74905eed818c5a727e2f2d6b814edb6` | PE32 i386; version resource `3.10.00.0658`, copyright identifies nGlide 1.05. Exports include `_grGlideInit@0`, `_grDrawTriangle@12`, `_grTexDownloadMipMap@16`, and mipmap-level download entry points. |
| `drivers/nglide/voodoo2a.dll` | `f15f4f574ddd94b057c7b6e43c17c290d12baf9f362d34004c488487033c689b` | PE32 i386; version resource identifies Glide3x Thrash Driver API v104, product 1.3.0. Exports include the driver's `_THRASH_init@0`, `_THRASH_setvideomode@12`, `_THRASH_settexture@4`, triangle/strip/fan drawing, and window operations. |

The same `voodoo2a.dll` bytes are present in the dgVoodoo and Glide3x driver directories. Their `glide3x.dll` wrappers differ, so the common driver DLL alone cannot identify the wrapper/backend in use.

## Early runtime map observation

The capture metadata has PID `192231`, process-start marker `1808931`, interval `0.1 s`, requested duration `600 s`, and states the sampler used `O_RDONLY pread` asynchronous snapshots without suspending or writing. Its early file-backed maps include the installed `nfs3.exe` at `0x00400000` and `0x00a1f000`. At that timestamp the map text has no `glide3x.dll`, `voodoo2a.dll`, `ddraw.dll`, or D3D driver module. Since the snapshot precedes completed startup, this does **not** establish that those modules remained absent during menu rendering or racing.

The one captured executable identity matches the selected installed executable. The capture contains no later map snapshots with which to prove the configured renderer's load, wrapper identity, API initialization, or backend. Runtime renderer identity remains open.

## Higher-resolution texture settings

The selected executable contains the `AllowHugeTextures` INI key at `0x0053f6d0`. At `0x004b56d5`, the parser passes that key to `0x004fb6f0` with `EDX=0`; it accepts values through 3 (values outside unsigned0..3 use shift0), computes `0x100 << value`, and stores the result at `0x007a278c`. Thus the binary's direct configuration mapping is:

| INI value | Stored extent |
|---:|---:|
| 0 | 256 |
| 1 | 512 |
| 2 | 1024 |
| 3 | 2048 |

The installed `nfs3.ini` selects value 0. The patch `readme_en.txt` describes values 1, 2, and 3 as experimental 512, 1024, and 2048 texture settings; that is documentation, not proof of supported visual output. The separate [setup normalizer audit](setup-normalizer-gameplay-domain.md) finds an alternate track-strip texture-descriptor branch (`004d41a0`/`004d4120`) that chooses a square power-of-two extent based on the smaller source extent and caps it at256. These facts show a 256 configured extent and a 256 cap on that reviewed producer path. They do not establish every texture producer's use of `0x007a278c`, successful larger allocations, or what the selected wrapper/backend accepts. Higher-resolution texture operation and image quality remain unverified.

## Configured extent is reduced against driver values

The direct-reference inventory for `007a278c` contains the INI store, a renderer-initialization read/write, and reads in packed-color buffer building, vehicle texture loading and indexed shape texture building. At `004b5bd6..004b5bf5`, renderer initialization takes the unsigned minimum of DWORDs+0x14 and+0x20 from the descriptor pointed to by `007a3a5c`, then repeatedly halves the requested extent until it is no greater than that minimum (or reaches zero), storing it back to `007a278c`. This is a concrete driver-dependent reduction. The precise descriptor field/API contract and actual returned values remain to be verified; a configured2048 is not a promise that2048 survives initialization.

`BuildSquarePackedColorBuffer` (`0049cea0`) starts with the resulting global and halves it until both supplied source dimensions are at least that side; it substitutes1 if repeated halving reaches0, then writes equal output width/height and calls its resampler. `BuildIndexedShapeTexturesWithLoadingProgress` passes the global into `004d4080` on its selected branch. The vehicle-loader read at `004b7d43` can instead start from256 on a gated path. This bounded direct-use inventory establishes multiple extent policies, not complete upload/atlas/backend coverage or higher-resolution output.

## Installed alternatives and claims

Other driver directories are installed, including dgVoodoo (`glide3x.dll` SHA-256 `9b06129d8afcf934f51676f1b8ce3a240fbb5ee0723eaf5de27735516e051d54`, version resource 2.5.3.0), Direct3D 5/6/7/8 Thrash drivers, and `softtri`. Their presence is not evidence that the current configuration selects or loads them. Their per-directory `thrash.ini` files describe their configured choices if selected.

The patch `readme_en.txt` identifies itself as Modern Patch v1.6.1 dated 2016-10-28. It claims nGlide emulates Glide3x through DirectX 9, dgVoodoo uses DirectX 11, and both support fog; it describes the larger texture settings as experimental. These are vendor/patch documentation claims, not measurements from this session. The root `D3DA.DLL` is the EA original D3D Thrash Module (version resource `1998.08.10.1148`, SHA-256 `ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02`); its presence is not evidence of current selection.

## Remaining decisive evidence

To close renderer identity, a later read-only module-map capture during the running menu/race would need to include the actual mapped wrapper and driver files (or equivalent loader evidence) and their paths. To close higher-resolution support, static use-sites of `0x007a278c` must be connected across all texture producers and allocations, then normal rendered output at configured levels must be observed. This report did not change the game, configuration, executable, or persistent analysis database.
