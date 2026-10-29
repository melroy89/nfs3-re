# Replay recorder batch-reservation audit

## Result

The encoder's exact greedy packet format admits a 44-byte output for one 32-byte channel row. Four independent channel rows can each realize that maximum in the same 128-byte sample batch, for 176 encoded bytes. Channel ordering, 32-sample row alignment, and the action-latch filter do not exclude the witness.

The recorder's single preflight at `004bcda0` checks `cursor + 128 < 0x1e000`, then appends all four returned channel lengths without a second capacity check. A valid sequence of prior batches can place the cursor at `0x1df71` (122,737), where the check passes (`+128 = 0x1dff1 < 0x1e000`) and a 176-byte batch ends at `0x1e021`, 33 bytes beyond the nominal stream end. The concrete boundary trace below lands at that cursor using a 65-byte intermediate batch. This establishes that the 128-byte reservation is insufficient under the encoder's supported channel values; it is not only a theoretical missing-check observation.

The length witnesses were additionally checked against the unchanged encoder bytes extracted from `004bc9b0..004bca7e` and run in the parent's isolated i386 harness: [replay-encoder-original-byte-probe.json](evidence/probes/replay-encoder-original-byte-probe.json) reports 519/519 vectors matching the branch model, maximum observed length 44, and the same boundary arithmetic. This executes only extracted encoder bytes with isolated synthetic rows; it is not game or full-recorder execution. No input executable was modified, and no persistent Ghidra metadata was written.

## Exact per-channel maximum

`EncodeReplay32ByteChannel` (`004bc9b0`, detailed-analysis-notes section “Replay encoder paired-stream partition and expansion”) scans exactly 32 source bytes. A maximal repeated run of length at least two is emitted as a 2-byte `(count,value)` token. A literal span emits one signed-length byte followed by its literal bytes. The final source singleton is emitted separately as `FF,value` (two bytes).

There are two row endings, and both are bounded:

- If the row does **not** end in an equal-byte pair, the encoder leaves the last byte for the separate `FF,value` case. For the first 31 bytes, let `k` be the repeat-run count, `j` the nonempty literal-span count, `T` the number of repeat-run source bytes, and `L` the literal source count. Then `T+L=31`, `T>=2k`, `j<=k+1`, and `2k+j<=31`. The encoded length is `2k+(L+j)+2 = 33+(2k-T)+j <= 33+j <= 44`. The maximum `j` under both constraints is 11 (at `k=10`).
- If the row **does** end in a repeat run, that run consumes the final bytes and there is no separate final singleton. Across all 32 bytes, `T+L=32`, `T>=2k`, `j<=k+1`, and `2k+j<=32`. Length is `2k+(L+j)=32+(2k-T)+j <= 32+j <= 43`; the same integer constraints cap `j` at 11. So ending with a repeated run cannot exceed the non-repeating-ending case.

In both cases the greedy encoder alternates nonempty literal spans and repeat runs, so `j<=k+1`; adjacent literal spans are coalesced. The 44-byte bound is attained when the row does not end in a repeat: ten 2-byte runs and eleven isolated literal bytes in the first 31 source positions. The 32-byte source witness is:

`[0,1,1] * 10 + [0,2]`

For an action-channel witness using the configured level-sensitive Handbrake bit `0x04`, use `[0,4,4] * 10 + [0,2]`; its exact output is ten copies of `FF 00 02 04`, followed by `FF 00 FF 02`, also 44 bytes. `FF` is signed `-1`, a one-byte literal token; `02 04` is a two-byte repeat token; the final `2` is a separate one-byte literal. This preserves the max-length pattern while using a button bit with an established input writer. The parent’s exact-byte probe now includes this action-value case; no target instructions were executed by the probe.

## Four-row sample witness

The recorder passes one 32-sample row for each sample byte to the encoder: channel offsets `0x00`, `0x20`, `0x40`, `0x60` in the participant ring, gathered into a 128-byte stack block. Four rows may independently equal the same 44-byte witness, so a batch returns `44+44+44+44=176` bytes. The four-byte sample producer admits these values under supported bindings:

- Byte `+0` is low byte of `(binding1_result-binding0_result)>>1`. Class-0 slot 0 returns zero; a class-1 axis slot with endpoint bounds `a=0,b=255` can return 0, 2, or 4, yielding sample values 0, 1, or 2 after the shift.
- Bytes `+1` and `+2` retain the low byte of independent class-1 axis results; the same endpoint bounds admit values 0, 1, and 2 directly.
- Byte `+3` is an action-bit mask. The level-sensitive Handbrake bit `0x04` is supplied by binding slot 6 / row 4 / text ID `0x4a`; it is not among the bits latched by mask `0xf2`. The action max-row witness uses repeated `0x04` pairs, with zeros separating them, plus final singleton `0x02`; bit `0x02` has a configured writer as well. The previously proposed bit-0 witness is withdrawn because the reviewed setup contains no writer for that slot and it remains zero after initialization.

Every byte in the four rows lies within the individual sample-field value domains documented by the static evaluator. The action byte witness also survives the previously exhaustively checked latch filter. This is an evaluator-domain witness only: the joint binding-table selection, simultaneous histories across all four fields, and active profile were not proved. The installed `config.dat` is not claimed to realize it, and no physical controller was tested.

## Boundary trace respecting 32-sample batch alignment

Let `N=0x1e000=122880`. Each batch corresponds to four independently encoded 32-byte rows. The following sequence uses only realizable per-channel encoded lengths and keeps every earlier recorder check passing.

1. Record 697 maximum batches of 176 bytes each: cursor `697*176 = 122672 = 0x1df30`. Every preflight before these batches passes, and each batch ends below `N`.
2. Record one intermediate batch of 65 bytes. Its four row lengths are `8, 8, 15, 34`, summing to 65. For the 34-byte row, use a 31-byte literal span plus the separately emitted final singleton. Example rows and outputs:
   - 8-byte analog row: `[1*10,2*10,3*11,4]` -> `0A 01 0A 02 0B 03 FF 04`.
   - 8-byte action row: `[0*10,4*10,0*11,4]` -> `0A 00 0A 04 0B 00 FF 04`. The repeated `0x04` action bit is level-sensitive and not latch-suppressed.
   - 15-byte analog row: `[100,101] + [10*6,20*6,30*6,40*6,50*5] + [60]` -> `FE 64 65 06 0A 06 14 06 1E 06 28 05 32 FF 3C`.
   - 34-byte signed-differential row: 31 distinct values `0..30` followed by `31`; the first three binding results can produce channel-0 low-byte values through `(result1-result0)>>1` (for example slot 0 zero and slot 1 values `0,2,...,60`). Exact output begins `E1 00 01 02 ... 1E FF 1F`: signed token `E1` is `-31`, followed by source bytes `00..1E`, then the separately emitted final singleton `FF 1F`. The literal token and 31 payload bytes cost 32, plus final token/value costs 2.

   All four are 32-byte rows; the sum is 65. The action row uses only the configured level-sensitive `0x04` bit, which the documented `0xf2` latch mask does not latch. The `15` and `34` rows are placed on analog/differential channels, not the action-mask channel.

   Cursor is now `122672+65 = 122737 = 0x1df71`.
3. The next 176-byte batch passes the actual guard: `0x1df71 + 0x80 = 0x1dff1 < 0x1e000`. It appends through `0x1e021`, so 33 bytes lie beyond the nominal `0x1e000` stream extent, beginning at adjacent initialized table `0x7c3f48`.

This is a constructive cursor path: the encoder returns the stated lengths; the global cursor advances by each returned length; the guard is evaluated only once per four-channel batch. No 4-byte or 32-byte alignment restriction applies to the compressed cursor because it advances by byte counts.

## Safe-domain condition and limits

A batch is safe with this reservation only when its actual combined encoded length is no greater than `N-cursor`, and its cursor is nonnegative and below `N`. The preflight's weaker condition `cursor+128<N` is sufficient only if every admitted batch's actual encoded length is at most the remaining bytes. A 176-byte batch violates that implication at the demonstrated cursor.

The static trace establishes that the encoder processes fixed 32-byte channel rows and that the binding evaluator admits the sample values used. It does not establish that the installed active profile produces these exact histories, that the race lasts for at least 699 full batches, or that this conditional overwrite was observed at runtime. Those are reachability/frequency questions, not questions of whether channel format or batch alignment can cap the encoded batch at 128 bytes.
