# Original versus Modern: screenshot repeat, numbering and sound

## Evidence

This extends the [screenshot comparison](original-modern-screenshots.md), using its exact supplied-original/official-Modern fingerprints. Reproduce with `python3 analysis/scripts/audit_screenshot_difference.py`; the [manifest](evidence/audits/original-modern-screenshots.json) retains both paths, the Modern sound wrappers/imports and hashed sound resource. Raw captures remain ignored. No target, keyboard, audio or instruction probes were executed.

## Repeat requests: threshold, not guaranteed save rate

Original frontend routine `00451810` checks Alt/P scan codes and calls capture directly on a matching invocation. There is no one-second gate in that inspected chord path. This does not establish the number of invocations per second or every original input path.

Modern hook `004ccb84` derives key-down state, checks the enabled screenshot setting and VK 0x2c, then calls `004cdc50` with EAX=0/1. That helper uses clock wrapper `004f2790`; the [clock comparison](original-modern-clock-source.md) establishes milliseconds from timeGetTime in Modern.

For nonzero input, it reads now and applies these ordered rules (`004cdc50..004cdc9b`):

1. If request latch `007a2778` is already nonzero, write it to 1 and refresh timestamp `007a2770` immediately.
2. Otherwise, if unsigned low-32-bit `now - timestamp >= 1000`, queue a request and refresh the timestamp.
3. Otherwise, if held-state `007a2774` is zero, queue a request and refresh the timestamp.
4. Otherwise leave the latch/timestamp alone. Every nonzero-input branch sets held-state to 1.

For zero input, an existing held-state is cleared without queuing; if held-state was already zero, the helper sets the request latch (`004cdc9c..004cdcba`). Thus it is not simply “capture once per key-down,” and an isolated zero-state call is not always a no-op.

Consumer `004c4480` handles a nonzero request, then clears the latch regardless of preparation/launch success. Requests can coalesce; the latch is not an outstanding-worker counter. These instructions support **MP140-049**'s one-second repeat mechanism but do not prove exactly one saved image per second under arbitrary event/consumer timing. Release/repress can queue sooner; existing pending events can refresh the timestamp. No repeat-rate measurement was performed.

## Numbering: atomic selection, not a directory maximum scan

Original increments ordinary counter `005600f8` before formatting `%s\\nfs3_%02d.tga` and probes file existence, trying another number on collision (`004c44f9..004c4534`). Modern worker uses `LOCK XADD [006fd1e0],1`, then INC of the returned old value, to obtain low32(old+1) before formatting `nfs3_%04d.%s` (`004e31c4..004e31dc`). An existing non-directory file leads back to another atomic increment.

The existing [lifecycle contract](screenshot-lifecycle-contract.md#filename-counter-initialization-and-wrapping) already establishes the reset/directory path: ordinary MOV0 when directory setup succeeds and the non-dot-entry helper returns zero, including its search-failure case. The cached-ready path checks directory existence and ordinarily avoids that reset. This is retained counter state within the process plus collision skipping; it is **not** a scan to recover the highest directory number.

This supports a bounded interpretation of **MP140-055**, while persistence across process launches and save-file serialization remains unresolved. Four decimal positions are a minimum formatting width, not a 9999 cap. Atomic selection does not reserve a filename, coordinate with the non-atomic reset, prove encoder success or guarantee completion order. The linked lifecycle report covers those limits; no concurrency failure is claimed observed.

## Shutter sound: resource-backed request after launch success

Consumer `004c4480` calls sound wrapper `004f1fb0` with string `SNAP.WAV` only after both directory preparation and capture/thread launcher return nonzero (`004c4495..004c44a7`). It does not wait for the worker to encode or write successfully. A shutter sound request therefore corresponds to successful launch on this path, not verified file completion.

`004f1f58` calls FindResourceA with type **10**, supplied name and module `[009f3d48]`, then LoadResource and LockResource. If a pointer is returned, `004f1fb0` calls imported WINMM.PlaySoundA with that pointer, null module argument and flags **7**. API return is ignored; actual playback is untested.

The official PE contains **RCDATA / SNAP.WAV / language 0**, 3,240 bytes, with RIFF/WAVE signatures. Its exact RVA and SHA-256 are retained in the manifest. This is an embedded resource, not proof that a disk file named SNAP.WAV is loaded. These call and resource witnesses statically support **MP140-056**. The original synchronous capture span does not contain this new resource-playback chain; this is not an assertion that original has no audio elsewhere.

## Remaining questions

Actual held-key timing, file success/completion ordering, cross-launch numbering persistence and audible output require separate evidence. Historical introduction dates require prior patch releases. All statements here distinguish observed instructions/resources from runtime behavior.
