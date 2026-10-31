# Original versus Modern: movie playback level initialization

## Evidence and scope

Static comparison of the supplied original executable and official Modern v1.6.1, with exact identities in the [baseline](original-modern-differences.md). Reproduce using `python3 analysis/scripts/audit_movie_volume_difference.py`; the [manifest](evidence/audits/original-modern-movie-volume.json) retains the movie address envelope, parameter initializer, forwarding wrapper and new Modern helper. No movie, audio or instruction execution; no executable or Ghidra changes.

This addresses **MP153-009**, “Menu music volume will be used for the movies.” It establishes the changed parameter source and forwarding path, not audible loudness or the historical release in which these final bytes first appeared.

## Changed call and parameter byte

In movie playback routine `00495bc0`, both versions prepare a parameter block at **`[EBP−68h]`** at `00495df9`. At **`00495e01`**, original calls `004e9b20` directly; Modern calls new wrapper **`004962c2..004962d6`**:

| Instruction | Effect |
|---|---|
| `PUSH EDI; MOV EDI,EAX` | Preserve EDI and retain the supplied parameter pointer |
| `CALL 004e9b20` | Apply the same default initializer as original |
| `MOV EAX,[006fbbe8]` | Read configured menu music level |
| `AND AL,7fh` | Retain the low seven bits |
| `MOV [EDI+8],AL` | Override parameter byte+8 |
| `POP EDI; RET` | Restore EDI and return |

Complete initializer **`004e9b20..004e9b93`** is byte-identical in both baselines. Its ordinary nonnull path writes defaults to a 16-byte block, including **byte+8=127**, then returns EAX=0. It saves/restores EDX. Its null diagnostic path proceeds back to the writes rather than providing a safe null-return contract. The movie passes a stack address; do not generalize the wrapper into a nullable interface.

Thus original supplies the default127 at this field, whereas Modern supplies `menu_level & 127`. This is masking, not saturation: configured0,80,127 produce0,80,127;128 produces0; the low byte of−1 produces127. These examples are instruction-derived, not probe results. The related music-backend level checks are documented separately in the [audio analysis](original-modern-music-start.md); they do not establish that this movie wrapper clamps the configuration value. No decibel conversion or linear perceptual-volume relationship is established.

The wrapper changes the return value relative to the initializer: EAX contains the loaded setting with its low byte masked, rather than0. At this callsite `00495e06` immediately overwrites EAX with1, so this caller does not consume the differing return. A reconstructed wrapper must preserve the actual pointer and register contract instead of relying on a guessed ordinary C return signature.

## Forwarding and remaining boundary

Both executables retain identical bytes **`00495e06..00495e3e`**. They pass EDX=`[EBP−68h]`, EBX=1, ECX=30 and a handle in EAX to **`004f3a60`** at `00495e39`, with two additional stack arguments. Complete wrapper **`004f3a60..004f3a7e`** is also byte-identical: it moves the parameter pointer from EDX into EAX, rearranges other register/stack inputs, calls `004f3fec`, and returns while removing eight stack bytes. This verifies that the modified block is forwarded to sound-stream setup, rather than being an unused stack write.

The full **`00495bc0..004960e0`** address envelope is retained for context, but it includes other changes and is not asserted wholly byte-identical or fully explained here. The new helper’s location `004962c2` belongs to different original control flow; it must not be paired with an “old helper” by address alone.

**Conclusion:** MP153-009 has bounded static support: movie playback now overrides default parameter127 with the configured menu music level’s low seven bits. Complete backend field interpretation, every movie entry route, decoder/provider effects, audio timing and audible acceptance remain unverified. The next useful extension is following the parameter through `004f3fec`, alongside the separate NoMovie and idle/minimized admission policies; those are distinct release-note claims.
