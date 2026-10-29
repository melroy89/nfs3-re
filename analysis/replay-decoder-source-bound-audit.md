# Replay decoder source-bound and adjacent-table audit

> **Deferred draft:** preserved with the final session checkpoint. Not reviewed or qualified as completed in the current research pass.

## Finding

Static analysis of the installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`) establishes two distinct boundary issues:

1. The file backend clamps a read to the opened file's recorded size and returns the actual number of bytes read, but the replay load caller discards that count. The subsequent RLE primitive has no source length/end pointer. A zero byte is only treated as EOF by the playback caller at a channel-batch boundary; inside a channel decode it is a valid zero-output token. Thus the caller's file I/O is length-limited, while decoder source accesses are not proven to remain within the bytes actually returned.
2. The recorder's 128-byte preflight can admit a 176-byte four-channel encoded batch (see [recorder reservation audit](replay-recorder-reservation-audit.md)). Its excess begins at `007c3f48`, which is not padding: it is the first cell of a 600-row by 16-column DWORD replay statistics table, initialized and later read/updated by replay code. The legal-size batch witness can therefore overwrite table cells, although the report does not claim that such an overwrite occurred in gameplay.

No game execution, malformed-file execution, executable modification, or persistent Ghidra metadata change was performed.

## Decoder source extent

- Loader `004bd2e0` requests `0x296f8` bytes at `007a3e50`, then validates fixed replay metadata through `00478090` and `00478100`. It does not preserve the read result as a stream length (REA evidence `ev_f98e1b2d9e98aab2dba9251ae017a93d4e0fad044d206f4139389a20a5bac7a6`).
- The backend read helper `004e3ae0` uses its file-record size when limiting the requested ReadFile bytes and reports the actual byte count back through the wrapper. This bounds the OS read itself. The wrapper result is not compared with the requested `0x296f8` nor stored as an end offset on the replay path, as documented in [caller/admission audit](replay-rle-caller-admission-audit.md).
- The compressed source begins at `007a5f48`; the playback cursor `007cda54` is reset to zero on load. At a batch boundary, `004bd090` tests `byte[007a5f48 + cursor]`; zero sets mode 4 and skips that batch. Nonzero calls `004bcee0` (`ev_f763864800575f8d99c1201012538d18cd8a8191c3f326cc0129a0c235360d8a`).
- `004bcee0` invokes `004bca80` four times, advances the global cursor by each returned consumed-byte count, and copies the first 32 output bytes for each channel (`ev_55e2a41b874ed991a9dfb60cd902b3b27069e162aef93ee95c6979d9e5272100`). The primitive reads from the current source pointer until its output count reaches at least 32; its signature has no input length or end pointer (`ev_2441da83012ff56c4011f069c14aa42a5d29a6ed4ba769595054430a6846154c`). A zero control token inside this primitive consumes one source byte and produces no output, so the caller's initial sentinel test is not a universal input bound.
- Consequently, the exact malformed/truncated-file outcome depends on bytes resident after the bytes returned by the short read, including preinitialized or prior buffer contents. Static code shows neither a short-read rejection at this caller nor a decoder source-end check. It does not establish that any particular short replay file is admitted by all higher-level UI paths, nor that an out-of-file read was observed.

The established malformed-token count bound remains separate: a `-128` literal control can request 128 output bytes in one run; if a prior run has produced 31 bytes, the primitive reaches 159 before its post-run `>=32` exit. Its scratch starts at `007a3e10`, so this exceeds the intended 32-byte channel slot and reaches adjacent globals. This is an output-staging overrun, not evidence about the file's actual source extent.

## The recorder's neighboring table

### Direct table shape and meaning

- Initializer `004bcb90` sets `007cda50` (record cursor) and `007cda54` (playback cursor) to zero, clears the `0x1e000`-byte stream at `007a5f48`, and initializes the table starting at `007c3f48` (`ev_b52a0232e04a9c00da430e74190c85263c376b469b37ed2b72df11d67a4eb042`).
- The loop writes `0x0b` into all 16 DWORD cells of row 0. For each row 1 through 599 it writes zero to column 0 and zeroes columns 1 through 15. Addressing is `table + row*0x40 + column*4`: 16 columns, stride `0x40`, 600 rows. This is the same base computed as `007a5f48 + 0x1e000`, the nominal end of the compressed recorder stream.
- Recorder-side routine `004bda00` computes a row from elapsed ticks (subtract `0x200`, divide by `0x78`), iterates participant entries, derives a small count from their fields, and stores the maximum at `007c3f48 + row*0x40 + participant*4` when it exceeds the existing value (`ev_a7c100ebf4368300c019009fd8eb2197a0e016be974c41c624238b6d5cee24f1`).
- Consumer `004bdd10` walks up to 600 rows for a supplied participant column and returns the maximum cell value. `004bdd70` calls it in the playback/state path (`ev_03b9e84286a2f8d109d734c0a8abd8a0b114e8a0857a6c0541e8ae6e587bf9a0`, `ev_5111d0e09f4f7483faa2626cfd2636faf8fb0e5520a9ad9a8341c783c96a4c6c`). Direct references to the table base are the initializer, writer compare/store, and this reader's load (`ev_b1728c1efa9d9872d107192c227059c61aa298398e7fa51da29883bdb5ed53cc`).

### Exact overlap from the admitted recorder witness

The 176-byte combined batch at cursor `0x1df71` ends at stream-relative offset `0x1e021`. It overwrites table offsets `0x0..0x20`: row 0 columns 0 through 7 (32 bytes) and the first byte of row 0 column 8. Those row-0 cells were initialized to `0x0b`, and column cells are subsequently read as per-participant maxima. The byte-level overwrite can therefore alter initialized table values used by the consumer, not merely unnamed adjacent storage. The specific resulting DWORDs depend on the four appended encodings and the prior cell values; the existence of the overlap and table consumer is established, but no live corruption or user-visible consequence was observed.

The 176-byte batch construction, 128-byte guard arithmetic, and independent four-channel output lengths are detailed in [recorder reservation audit](replay-recorder-reservation-audit.md). Its value combinations are supported by individual evaluator domains; joint binding admission, a specific active profile, and long-run gameplay history are not established.

## Evidence boundary and remaining questions

The static evidence supports: bounded file ReadFile requests; discarded actual-read length on the traced replay load; an RLE primitive without source-end input; zero sentinel only at the outer channel-batch boundary; a fixed output scratch overrun for malformed controls; and a legal-size recorder batch whose excess intersects a semantically initialized and consumed table.

Still unknown are the exact admission/rejection behavior for deliberately truncated or malformed replay files through every UI path, the contents of unread tail bytes in a particular runtime session, whether runtime playback reaches such bytes, whether the demonstrated recorder channel histories co-occur in an active profile, and any observable consequence of table-cell damage. These are runtime/reachability questions; this audit makes no claim that they occurred.
