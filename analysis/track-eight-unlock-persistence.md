# Track-index-8 unlock persistence

## Static finding

The unlock flag `g_nTrackIndex8Unlocked` at `006fd2ac` belongs to the configuration blob beginning at `006fbb40`: its file offset is `0x176c`. It occupies four bytes within the `0x20f0`-byte snapshot. Thus the absence of a direct file-I/O reference to this global does **not** mean the flag is transient.

`SaveConfigDatSnapshotIfAllowed` (`00472820`) copies the configuration blob to a temporary buffer and passes it to the `config.dat` writer. Its explicit snapshot edit clears offset `0x1860`, which is distinct from the unlock flag at `0x176c`. The preceding `RefreshPreparationHeaderPrefix` (`004723f0`) copies only the first three DWORDs and does not reset this flag. Direct callers include frontend restoration00473080 and the race-cleanup wrapper004c4820. These establish ordinary lifecycle call sites, not proof those calls executed after a particular unlock. Saving is conditional on playback mode being zero, the drive-space check succeeding and loading-abort being clear. A successful disk write was not observed.

`LoadConfigDatAndInitializeSettings` (`00472980`) accepts a file of length `0x20f0`, copies it to `006fbb40`, and checks its leading size field. The accepted version branch (high version byte zero and low byte at least 6) avoids the default initializer. The default initializer (`00472404`) clears the configuration block and explicitly resets the unlock flag. Consequently, the ordinary accepted-file load/save paths provide aggregate persistence for this flag; missing or rejected configuration follows a reset path. This establishes the serialization mechanism, not a completed save/load cycle on the user's installation.

## Existing unlock routes

The reviewed direct writers are the default reset at `00472436`, the EMPIRE cheat store at `004527a4`, and the postgame store at `0044e252`. The postgame route tests mode 2, selected track 8, and result DWORD `+0x2c4` not equal to 2. Frontend reconciliation reads the flag and enables menu ordinal 8. That menu ordinal remains separate from the eight-entry series selection map.

## Evidence and remaining work

Ghidra 12.1.4 readback of the saved analysis confirmed the loader, saver, header refresh and default initializer. Assembly at `00472869..00472898` shows the snapshot length, source, copy and separate clear. Loader assembly at `00472a1a..00472acb` shows the file-size gate, destination copy, header checks and accepted-version route. Executable SHA-256: `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`.

**DONE:** identifying the flag's aggregate configuration serialization and reset distinction.

**OPEN:** observing an ordinary successful save, restarting with that same resolved configuration path, and confirming menu visibility. No game file or live process memory was changed, and no installed configuration field was decoded for this finding.
