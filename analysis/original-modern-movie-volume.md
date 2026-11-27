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

The full **`00495bc0..004960e0`** address envelope is retained for context, and the expanded audit verifies that its only changed bytes are `00495e02..00495e04`, three bytes of this initializer-call displacement. This is not equivalence of the full movie subsystem: callees and input providers can differ. The new helper’s location `004962c2` belongs to different original control flow; it must not be paired with an “old helper” by address alone.

**Conclusion:** MP153-009 has bounded static support: movie playback now overrides default parameter127 with the configured menu music level’s low seven bits. Complete backend field interpretation, every movie entry route, decoder/provider effects, audio timing and audible acceptance remain unverified. The next useful extension is following the parameter through `004f3fec`, alongside the separate NoMovie and idle/minimized admission policies; those are distinct release-note claims.

### Movie sound setup switches to the volume wrapper in 1.5.3

The hosted reference and every retained Modern archive through 1.5.2
match across the complete 1,312-byte playback envelope
`00495bc0..004960e0`. In 1.5.3, 1.6.0 and 1.6.1 the same three
bytes differ at `00495e02..00495e04`. They retarget the call at
`00495e01` from `004e9b20` to `004962c2`. To reproduce, extract
each root `nfs3.exe` and compare PE RVA `95bc0` for `520h` bytes.
The call target is the signed displacement at RVA `95e02` added
to VA `00495e06`.

This dates the call-site change independently of the
[CPU-based conversion choice](original-modern-cpu-tier.md#the-movie-conversion-tier-changes-in-100),
which was already present in 1.0.0. The playback bytes alone leave
decoder and sound-backend behavior outside the compared span.

The complete 20-byte wrapper at `004962c2..004962d6` is byte-identical
in 1.5.3, 1.6.0 and 1.6.1. In all three releases it calls the default
initializer and then reads `006fbbe8`, masks the low seven bits and
writes byte `+8`. This pins the setting source and transform to the
same 1.5.3 boundary as the call-site retargeting. Compare PE RVA
`962c2` for `14h` bytes in the three archive members to reproduce.

### The stream context retains the parameter block

On the admitted creation path at `004f3fec`, the caller's parameter
pointer is saved at `004f3ff6`. At `004f413e..004f4149`, four
dword copies move the full 16-byte block into context offset
`+3ch`, placing the movie volume byte at context offset `+44h`.
The creation path publishes the context pointer to the active slot
array at `004f4172`. This success path matches byte for byte in the
hosted reference, 1.5.3 and final across `004f3fec..004f418b`.

This verifies that the changed byte survives stream construction.
The eventual gain application and audible output still need separate
evidence.

### Stream startup passes the parameters into voice setup

On the stream-header path, `004f3c3f` supplies context `+3ch` in
ECX to `005112d0`, the voice setup routine. At `005112fd..00511309`
that routine passes the config pointer in EAX and literal 1 in EDX
to `00523f90`, with its local output record addressed in ECX
afterward. The config helper explicitly checks the signed byte at
input offset 8 at `00523fa4`, branching for negative values.
The movie override produces values in 0–127, so its byte alone cannot
take that negative-value branch.

This is an observed consumer of the saved parameter. The separate
load of `[EBP+8]` at `005113c1` uses the header pointer that arrived
in EBX, so it does not by itself establish that the movie's config
byte is copied into that channel field. The gain calculation and
backend submission still need a value trace.

On the admitted voice setup path, `0051138f` reloads the config pointer
and `0051139a` reads its dword at offset 5. Arithmetic right shift by 24
at `005113ab` extracts the signed byte at offset 8. The subsequent
left shift by 16 and store at `005113b8` publish that value in
16.16 representation at channel offset `+20h`. The channel address
is `00a09b3c + 60h*index` on this path. Thus a movie parameter byte of
80 reaches channel setup as `00500000h`; the original default 127
produces `007f0000h`. This closes the config-to-channel transfer.
Conversion from the channel field to the backend gain remains open.

### Channel volume enters the voice submission

At `00511446`, voice setup calls `005014a0` with the new channel index.
The helper reads the integer part of channel dword `+20h`, multiplies it
by the signed byte at `+30h`, the integer part of dword `+28h` and the
signed global byte at `00a09af5`. It divides the signed product by
`1f417fh` (127 cubed) and stores the low result byte at channel
`+31h`. The multiplication uses x86 low-dword results and the division
truncates toward zero.

The optional table branches can replace that byte when channel
`+58h` or `+4ch` is nonzero. The inspected setup clears both before
the call. At `00511453..00511477` the caller then reads signed byte
`+38h`, multiplies it by global dword `00a0a260` and signed byte
`+39h`, divides by `3f01h` (127 squared) and pushes the result as
a separate input to `00523d94`. In particular, that later push alone
is not a read of `+31h`. The calculated movie-dependent byte is
verified in channel state. Its platform consumer is traced below. The
resulting audible gain remains unverified.

The movie-dependent channel byte does reach platform voice submission.
The unaligned dword read at `00511481` starts at channel offset
`+2eh`. Its high byte is offset `+31h` on little-endian x86, so
`SAR EAX,24` at `00511487` sign-extends the calculated gain.
The caller moves it to ECX at `0051148d` and calls `00523d94`.
That routine saves incoming ECX in EDX, then uses EDX as the level
argument to `005222f0` at `00523e01` on the inspected format path.
This is distinct from the preceding stack input described above.

The helper initializes both output levels to the input level. At pan
64 it returns both unchanged. For pan below 64 it replaces the
ECX-pointed output with `(pan * level) >> 6`. For pan above 64 it
replaces the EBX-pointed output with `((127 - pan) * level) >> 6`.
These are signed arithmetic shifts. This establishes consumption of
the movie-dependent gain during platform packet setup. Hardware or
wrapper output and perceived loudness remain untested.

### The two levels initialize the mixer record

On the admitted packet path, `00523e5a..00523e63` pushes both level
outputs from the locals written by the pan helper. In the call at
`00523e7a` to `005000b8`, they arrive as stack arguments 5 and 6,
numbered with the first argument immediately after the return address. After the mixer prologue those
arguments are at `[ESP+28h]` and `[ESP+2ch]`. The shared setup tail
at `005001ff..00500218` copies their low bytes into mixer record
offsets `+1/+2` and duplicates them at `+4/+5`. The record becomes
active at `00500243` after the setup callback returns.

This verifies the movie setting's propagation to the active mixer
record on the inspected path. It leaves the selected DSP callback's
sample scaling and measured playback outside the static trace.

The setup immediately calls `00500654` at `00500228`. If mixer
record byte `+3` is zero, the helper clears `+8` and returns.
Otherwise it reads unaligned dwords at offsets `+1` and `+2`
and extracts their high bytes, which are the duplicated stereo
levels at `+4` and `+5`. It averages them with a signed right shift
and stores the result temporarily at `+8`. Before returning it
overwrites `+8` with `(signed(+3) * signed(+8)) >> 7` and passes
that final byte twice to the callback at record `+ddch`, along with
the subrecord pointer at `+dc4h`. This is the mixer setup's secondary
level path. The separate stereo pair remains in the record, and the
callback's effect on output samples still requires inspection.

The secondary branch is not selected by the menu-volume byte directly.
The platform packet routine reads its second stack argument at
`00523e4f` from
`[ESP+20h]` and forwarded as mixer argument 9. The mixer copies its
low byte to record `+3` at `0050021b..00500222`. The source is the
separate quotient pushed at `00511477` from channel `+38h`,
`+39h` and global `00a0a260`. Channel `+38h` comes from stream
header byte 9. Channel `+39h` comes from config byte 10, which the
movie's default initializer sets to 127. Thus the patched movie
volume affects the stereo pair, while a different input determines
whether the secondary callback is reached. The live header and
global values remain unverified.
