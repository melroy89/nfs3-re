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

### Descriptor producer and extent source

The configured `voodoo2a.dll` export `_THRASH_about@0` is at DLL RVA `0x1bb0` (Ghidra image VA `0x60001bb0`). Its static descriptor is based at `0x6000fd10`; it writes descriptor size `0x68` at `+8`, returns that descriptor pointer, and initializes the two fields at `+0x14` and `+0x20` to `0x100` (256) at `0x60001c34` and `0x60001c5e`.

Those 256 values are defaults, not the final values for the selected wrapper. The DLL's resolver table at RVA `0x1120` maps its function-pointer slot `0x600110c0` to `_grGet@12` (table index 44). During driver initialization, internal routine `0x600018d8` calls that function with selector `0x0a`, a four-byte result size, and a pointer to a local DWORD at `0x60001a0c..0x60001a1a`. The configured `drivers/nglide/glide3x.dll` exports `_grGet@12` at `0x10001096`, a thunk to `0x10008950`; its selector-`0x0a` arm at `0x10008a4e..0x10008a62` writes the hardcoded value `0x800` (2048) through the output pointer and returns 4. The driver copies that result to descriptor `+0x14` and `+0x20` at `0x60001a1b` and `0x60001a20`. Thus this driver/wrapper pair advertises 2048 in both extent slots after initialization. It is a constant reported by the wrapper; the path does not measure a physical GPU limit or read `AllowHugeTextures` from the game.

On the executable side, function `0x004b5a58..0x004b5bfc` reads the descriptor slots at `0x004b5bdc..0x004b5be4`, takes their unsigned minimum, and halves global `0x007a278c` until that configured extent is no greater than the minimum. With current `AllowHugeTextures=0`, the configured extent starts at 256, below the nGlide pair's advertised 2048, so this initialized configured-pair path would leave it at256; the effective live value was not captured. The exact semantic labels (width versus height) for the two equal descriptor slots are not present in the reviewed driver code; the executable treats both as extent bounds.

The executable's binding table at `004f8390` identifies `_THRASH_init@0` at slot `009ef978`, `_THRASH_selectdisplay@4` at `009ef944`, and `_THRASH_about@0` at `009ef980`; page-flip slot `009ef940` is distinct. The initialization path `004b5aa3 ->00517620 ->005246a0` reaches the driver init call at `0052473a`. On the successful path, `0051766b` refreshes the descriptor through `004f853c`, which calls about and publishes its pointer to `007a3a5c`; the enclosing renderer initialization later reads the extent fields. This ties the reviewed init/query/descriptor chain to the cap consumer without claiming the selected DLL pair was mapped during the earlier race.

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

## Configured driver allocation and mip upload

The selected `voodoo2a.dll` adds a separate memory-admission gate after the executable has chosen/resampled an extent. Export `_THRASH_talloc@20` at `0x600024e0` converts its first two integer inputs into base-2 size exponents using integer-to-float conversion and exponent extraction (`0x600024ef..0x60002517`). It then maps the largest exponent, aspect difference, and format index through tables at `0x6000fe34`, `0x60010100`, and `0x60010104`, and calls `_grTexCalcMemRequired@16` through resolver slot `0x600110a4` (`0x60002555..0x60002569`). The format-map bytes beginning at `0x60010104` are `00 05 0b 0a 00 00 0c 04 0e`; the normal input-index domain and semantic format names are not established here.

The configured wrapper's `grTexCalcMemRequired` export at `0x1000110e` reaches implementation `0x10012440`. It uses size levels 1, 2, 4, …, 1024, 2048 (`0x10012482..0x100124b3`) and selects bytes-per-texel from the format value: below `0x8`, one byte; `0x8..0xf`, two bytes; `0x10` and above, four bytes before its additional special-format reductions (`0x100125e1..0x100126b1`). These branches calculate required texture-memory bytes; they do not establish the names of the game-side format codes.

After this calculation, `talloc` queries `_grTexMinAddress@4` and `_grTexMaxAddress@4` through slots `0x600110ac` and `0x600110b0`. It rounds the allocation cursor/range at 2 MiB boundaries (`0x60002575..0x600025a9`) and returns null when the remaining aligned range is smaller than the calculated requirement (`0x600025ba..0x600025dc`). Only after that comparison does it request a 0x20-byte record and link it into the driver's texture list (`0x600025e6..0x60002651`). This is the concrete driver-side dimension/format-dependent admission condition beyond the descriptor's reported 2048 extent. It is texture-memory availability, not evidence of a physical 2048-pixel device limit.

For an admitted record, `_THRASH_tupdate@12` at `0x600026e0` calls internal `0x60002660`, which iterates its stored mip range and calls `_grTexDownloadMipMapLevelPartial@40` through slot `0x600110dc` (`0x60002686..0x600026ab`). A nonzero auxiliary input separately reaches `_grTexDownloadTable@8` at `0x6000271e..0x60002726`. The reviewed driver does not test the partial-upload return value or add another per-level extent check at this call site. This identifies the allocation preflight and upload path; it does not prove every executable producer reaches it, or the wrapper's complete internal treatment of each upload request.

## Installed alternatives and claims

Other driver directories are installed, including dgVoodoo (`glide3x.dll` SHA-256 `9b06129d8afcf934f51676f1b8ce3a240fbb5ee0723eaf5de27735516e051d54`, version resource 2.5.3.0), Direct3D 5/6/7/8 Thrash drivers, and `softtri`. Their presence is not evidence that the current configuration selects or loads them. Their per-directory `thrash.ini` files describe their configured choices if selected.

The patch `readme_en.txt` identifies itself as Modern Patch v1.6.1 dated 2016-10-28. It claims nGlide emulates Glide3x through DirectX 9, dgVoodoo uses DirectX 11, and both support fog; it describes the larger texture settings as experimental. These are vendor/patch documentation claims, not measurements from this session. The root `D3DA.DLL` is the EA original D3D Thrash Module (version resource `1998.08.10.1148`, SHA-256 `ae676272438d93fd7a8da7a19250d6e8b664d8570824ab8042e2b20b38395a02`); its presence is not evidence of current selection.

## Remaining decisive evidence

To close renderer identity, a later read-only module-map capture during the running menu/race would need to include the actual mapped wrapper and driver files (or equivalent loader evidence) and their paths. To close higher-resolution support, static use-sites of `0x007a278c` must be connected across all texture producers and allocations, then normal rendered output at configured levels must be observed. This report did not change the game, configuration, executable, or persistent analysis database.
