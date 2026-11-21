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

This supports a bounded interpretation of **MP140-055**. The serialization follow-up below establishes counter inclusion in the configuration block; successful cross-launch preservation remains untested. Four decimal positions are a minimum formatting width, not a 9999 cap. Atomic selection does not reserve a filename, coordinate with the non-atomic reset, prove encoder success or guarantee completion order. The linked lifecycle report covers those limits; no concurrency failure is claimed observed.

## Shutter sound: resource-backed request after launch success

Consumer `004c4480` calls sound wrapper `004f1fb0` with string `SNAP.WAV` only after both directory preparation and capture/thread launcher return nonzero (`004c4495..004c44a7`). It does not wait for the worker to encode or write successfully. A shutter sound request therefore corresponds to successful launch on this path, not verified file completion.

`004f1f58` calls FindResourceA with type **10**, supplied name and module `[009f3d48]`, then LoadResource and LockResource. If a pointer is returned, `004f1fb0` calls imported WINMM.PlaySoundA with that pointer, null module argument and flags **7**. API return is ignored; actual playback is untested.

The official PE contains **RCDATA / SNAP.WAV / language 0**, 3,240 bytes, with RIFF/WAVE signatures. Its exact RVA and SHA-256 are retained in the manifest. This is an embedded resource, not proof that a disk file named SNAP.WAV is loaded. These call and resource witnesses statically support **MP140-056**. The original synchronous capture span does not contain this new resource-playback chain; this is not an assertion that original has no audio elsewhere.

## Remaining questions

Actual held-key timing, file success/completion ordering, cross-launch numbering persistence and audible output require separate evidence. Historical introduction dates require prior patch releases. All statements here distinguish observed instructions/resources from runtime behavior.


## Counter belongs to the saved configuration block

The [serialization extent audit](evidence/audits/screenshot-counter-serialization.json), reproduced with `python3 analysis/scripts/audit_screenshot_counter_serialization.py`, pins the official final EXE and retains complete selected save/load bodies. Screenshot counter `006fd1e0` is **offset16A0h** from configuration base `006fbb40`, inside the `20F0h`-byte extent. The save body sets source/base and size at `00472869..00472875`, copies to its temporary buffer, and requests writing `20F0h` bytes. Its explicit temporary-field clear at `00472898` targets **1860h**, not16A0h. The load path sets destination `006fbb40` at `00472a7f` and performs the corresponding block copy before header/default decisions.

This supplies a concrete **conditional cross-launch persistence mechanism through config.dat**. It supersedes the earlier serialization-unknown boundary; the counter is not merely isolated process-only state. It is also not proof that every screenshot immediately updates the file: no save call is established here on each capture, and save admission, successful I/O, later startup/default/profile writes and shutdown ordering remain separately qualified. A copied block can contain an older counter snapshot.

The [existing header decision tree](original-modern-config-loading.md#modern-header-decision-tree) and [directory reset](screenshot-lifecycle-contract.md#filename-counter-initialization-and-wrapping) still matter. Directory setup can zero the counter for an empty/non-dot-entry-negative search result, including search failure. Existing-file collision skipping can avoid overwriting old numbers even without a successfully restored counter, so continued numbering alone would not prove serialization. Conversely, a restored counter can retain a larger number after files are removed unless a reset path runs.

**Verified:** field inclusion in declared save/load extents and the distinct temporary-field clear. **Unverified:** successful actual saved bytes, all helper/register and direction-flag preconditions, synchronization with screenshot increments, all later writers and real cross-launch results. MP140-055 remains partial; its historical1.4.0 introduction is not dated by this final-only check. No configuration file was written or loaded, and no target instructions or Ghidra changes were made.


## Saved-counter mechanism appears at131-to140 boundary

The [historical counter audit](evidence/audits/screenshot-counter-history.json), reproduced with `python3 analysis/scripts/audit_screenshot_counter_history.py`, verifies author-hosted1.3.1/1.4.0 archive and EXE hashes. It narrows the final-only dating limitation above.

| Selected mechanism |1.3.1 |1.4.0 |
|---|---|---|
|Counter |`005600f8`, outside config block |`006fd1e0`, config+16A0h |
|Increment |MOV/INC/MOV in `004c44f9..004c4531` |LOCK XADD then INC of old value in `004e31cc..004e31f7` |
|Format at `005401d8` |`%s\nfs3_%02d.tga` |`nfs3_%04d.%s` |
|Config save-copy/request suffix |`00472869..004728c3` |Byte-identical suffix |

The relocation into the existing serialized extent supplies a concrete mechanism for MP140-055 at its advertised boundary. Four decimal positions remain a minimum width, not a cap. The earlier selected counter's location outside this particular block does not prove the absence of every other original persistence mechanism.

Historical introduction of these selected changes is now verified; successful cross-launch preservation remains untested. Save timing, default/reset paths, full I/O/helper contracts, concurrent snapshots and file collisions retain the qualifications above. The audit executed no target instructions and changed no executable or Ghidra database.
