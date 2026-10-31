# Original versus official Modern Patch: screenshots

## Scope and artifacts

This is a static comparison of the supplied original nfs3_org.exe and the official Modern Patch executable captured from the archive. It traces the original key path through its capture/save routine, then compares that with Modern's hook, request processing and worker launch. It does not claim that a screenshot was taken in either build.

| Artifact | SHA-256 |
|---|---|
| Supplied original nfs3_org.exe | b390be67925b2ad0857fc67dd6431ce68be597253eaa47c30789dc885a19d51b |
| Official archive nfs3.exe | 240a083a78ac3b836f0bdf3fe643a1c6568c12eefa5a186a2f6edd808596dca6 |

The official archive README matches the installed README byte-for-byte (SHA-256 02bf4684dce1073b4fe7c00c747f020b43508b0cf1407b5dc3f3b864ea46d81d). Its historical screenshot notes say the original used Alt+P and TGA, while Modern uses Print Screen and supports BMP/PNG/JPG. The binary paths below independently support a concrete portion of that change.

## Original: Alt+P enters a direct TGA capture path

Original 00451810 checks two keyboard scan-code values using helper 004eb1c0: 0x38, then 0x19. Only when both checks succeed does it call 00452410 at 0045182f; that wrapper immediately calls 004c4490 at 00452413. The scan-code pair is the Alt+P chord documented in the release notes. The same capture routine also has a direct call from the race loop at 004c547b.

004c4490 constructs a numbered path and performs the capture/save inline:

1. It calls 004b6520, which opens HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders and queries Desktop; the returned directory is copied to a local path buffer.
2. It formats "%s\nfs3_%02d.tga" using that Desktop directory and counter 005600f8, then uses 004e0e60 to skip a name that already exists.
3. It requests a capture buffer through 004ef190, calls the driver capture slot [009ef920] with current width/height, then calls 004eb160 directly with the generated filename. 004eb160 invokes the TGA writer at 004eafc0 and the file-write path before returning to 004c4490.

This establishes the old artifact/path behavior from code: a synchronous TGA save named nfs3_<number>.tga under the user's Desktop folder. It does not establish that every old build used identical shortcut handling or that file creation always succeeded.

## Official Modern: Print Screen queues capture for a worker

The official Modern keyboard hook callback at 004ccb84 handles configured keyboard events. For screenshot handling it checks nonzero setting 00561288, compares the virtual-key code to 0x2c (VK_SNAPSHOT), and passes the key-down state to 004cdc50. Hook initialization at 004ccc40 installs callback 004ccb84 with hook type 0x0d, with a fallback installation using type 0x02. This is a different input chord/path from the original Alt+P check.

004cdc50 updates screenshot repeat state and sets pending request latch 007a2778; its held-key path gates repeat requests by elapsed ticks. The frontend, loading-progress, and race-loop callers process that request at 004c4480 (direct calls at 00451969, 00495274, and 004c5481). Processing normalizes the selected format, prepares the screenshots directory/index, captures pixels, and launches a thread.

The capture launcher at 004c452c allocates a per-capture record and invokes CreateThread with entry 004e3078 (entry pointer pushed at 004c459a; API call at 004c45a3). The handle is closed immediately after successful creation; the worker owns and releases the capture record. The worker formats nfs3_%04d.%s using the prefix .\\screenshots\\ (data at 0053f7f4; format string at 0053f804) and writes BMP or GDI+ PNG/JPEG output. The configured default string is png (constant at 0053f6cc, passed by LoadGameIniSettings at 004b568c..004b5691); unrecognized/unsupported format is normalized to BMP. The prefix is relative to the process working directory. The later [startup-path audit](original-modern-startup-paths.md) establishes the ordinary executable-directory attempt, whose API result is ignored; this capture alone does not establish effective or permanent CWD. The asynchronous handoff and relative output prefix are proven by the code path; completion or success of a particular file write is not.

The detailed Modern-side ownership and format evidence is in [screenshot worker admission audit](screenshot-worker-admission-audit.md) and [screenshot lifecycle contract](screenshot-lifecycle-contract.md). Those documents concern the locally installed Modern-derived target; the addresses and instructions summarized here were rechecked against the official package executable fingerprint above.

## Retained instruction witnesses

Run `python3 analysis/scripts/audit_screenshot_difference.py` from the repository root (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-screenshots.json) hash-checks both baselines and records half-open instruction spans for the original key/wrapper/capture/Desktop/TGA paths and Modern hook/request/capture/worker/default paths. It also records the exact filename/path strings from both images. Raw assembly stays under ignored `analysis/captures/modern-differences/screenshots/`. This is static capture, not screenshot or instruction execution.

## Concrete before/after behavior

For the inspected original, Alt+P drives a direct call that captures and writes a numbered TGA file into the Desktop directory. In the official Modern build, Print Screen drives a pending request; the capture is handed to a worker thread and is written beneath the relative screenshots directory. The Modern default format constant is PNG, subject to the configured format and fallback logic. This is a binary-supported output and scheduling change, not merely a README comparison.

The [repeat/numbering/sound comparison](original-modern-screenshot-feedback.md) follows the 1,000 ms request gate, atomic filename counter and embedded shutter sound, with runtime and cross-launch persistence limits.

The [pixel comparison](original-modern-screenshot-pixels.md) traces original depth-16 conversion versus Modern masked RGB565 copying and the four-to-three-byte output path, without claiming measured image fidelity or compression.

## Limits

- Conclusions are tied to these two fingerprints. The original artifact's exact retail provenance is not authenticated by this review.
- The original Alt+P sequence is supported by scan-code checks 0x38 and 0x19, the call through 00452410 to 004c4490, and the matching historical README note. No keyboard was used.
- CreateThread proves the Modern launcher requests asynchronous execution; it does not prove worker scheduling relative to later captures, shutdown overlap, or successful encoding.
- The Modern worker's shared format/encoder state and teardown risks are documented separately; this comparison does not claim an observed race.
- The original registry query establishes the configured Desktop path lookup, not every possible Windows shell-folder redirect or write permission outcome.

No executable, runtime configuration or Ghidra project was changed. No game, test, or runtime probe was run.

The [movie-stop input comparison](original-modern-movie-screenshots.md) now traces the screenshot consumer through movie polling and bounds the claim that screenshots no longer stop intro playback.

## Directory contents and numbering initialization

Modern helper **`004f9184..004f91e9`** is a Boolean non-dot-entry test, not a count of screenshot files. The [directory audit manifest](evidence/audits/modern-screenshot-directory.json), reproduced by `python3 analysis/scripts/audit_screenshot_directory.py`, retains its complete body, preparation caller and copy helper against the official Modern executable hash. This extends the Modern mechanism above; original code at the same address is unrelated and is not a semantic counterpart.

It copies incoming EAX’s NUL-terminated path to a stack buffer through **`004f93b8`**, replaces the terminal NUL with `*` followed by NUL, and enumerates using `FindFirstFileA`/`FindNextFileA`. Exact names `.` and `..` are skipped. Any other entry returns1, including a subdirectory or an unrelated file; there is no local extension, attribute or `nfs3_` filename filter. It closes a successfully obtained search handle through `FindClose`, ignores that result, and restores general registers through PUSHAD/POPAD except for the saved EAX result slot. Flags are not preserved by that mechanism.

`FindFirstFileA` failure returns0, as does enumeration ending after only dot entries. A failed `FindNextFileA` is likewise treated as the end of enumeration without examining an error code. Thus zero does not prove the directory is empty or readable. The copy helper has no explicit capacity argument or bound; the enumeration helper reserves a260-byte path area followed by its find-data area. Its known caller supplies the short constant **`.\\screenshots\\`** at `0053f7f4`, so the generic unbounded interface is not proof of an overflow on that normal call.

Preparation **`004c44e8..004c452c`** first uses cached state `007a277c` and a directory-existence check. Its slower path calls `004f9214` to ensure the directory, then performs the non-dot test. If directory preparation succeeds and the test returns0, it clears screenshot numbering state **`006fd1e0`** and sets cached state to1. A nonempty directory leaves the numbering cell unchanged; it does not discover the largest existing screenshot suffix in this path. Preparation failure stores0 in the cache. Subsequent file-name generation and write success remain separate from this initialization policy.

No directory or screenshot operation was executed. Remaining questions include concurrent captures, filename collision handling, later numbering writes and error propagation. The static evidence explains why arbitrary directory contents and enumeration errors can influence numbering initialization; it does not establish an observed overwrite or data-loss event.

## Worker filename collision search

The directory initialization above is followed by a separate collision loop in the asynchronous worker, **`004e31b8..004e31ef`**. The expanded directory audit retains this route, the complete later save/cleanup tail through `004e3248`, and the attribute predicate. It copies `.\\screenshots\\` into its local filename buffer, then uses **`LOCK XADD [006fd1e0],EAX`** with increment1 and adds1 to the returned old value. A zero counter therefore produces candidate1. Formatting appends **`nfs3_%04d.%s`** at `0053f804`, using the candidate and extension string at **`007a2780`**.

The worker calls **`004f91ec`**, which returns1 only when `GetFileAttributesA` succeeds and directory attribute bit`0x10` is clear. Existing non-directory files cause another atomic increment and retry; directories and attribute-query failures return0 and end the search. Thus resetting the counter when the directory test returns0 does **not** alone imply overwriting an existing screenshot: the worker separately skips candidates recognized as existing files. A subdirectory named like a candidate is not skipped by this predicate, and an inaccessible existing path can be indistinguishable from a missing one at this boundary.

The atomic counter gives concurrent workers distinct increment results until wrap or another reset, but the check does not atomically reserve a path. Another process may create a candidate between the query and save. No local iteration cap or explicit32-bit wrap check is present. `%04d` is a signed decimal formatting conversion with minimum width4, not a four-digit range limit; high counter values can produce longer names or negative signed representations.

After finding a candidate, the worker reads the **shared** extension setting again: PNG/JPG dispatch to `004e3014`, otherwise the BMP-buffer write route calls `004eeae0`. This capture does not prove the setting remains stable across formatting and dispatch, nor does it establish every downstream writer’s replacement/open flags; the BMP follow-up below resolves that branch. Those helpers’ return values are not checked before the worker frees its buffers and returns0. Consequently this is a collision-avoidance attempt, not an exclusive-create or successful-save guarantee. File-system errors, races and actual overwrite behaviour remain untested.

## BMP write policy: the probe is not exclusive creation

Existing [BMP write research](detailed-analysis-notes.md#bmp-filename-admission-and-write-completion) already traced this path; the expanded directory audit now retains the official Modern instruction spans needed to reproduce its open-policy finding. `004eeae0` calls `004e2ae0`, which passes **EDX=`0x232`, EBX=0** to native file opener `004e3620` at `004e2b2c`.

The opener maps those flag bits to **access`0x40000000`, share0, disposition2, attributes`0x08000080`**. It calls the executable’s `CreateFileA` import at **`00534498`**, from `004e37c8`. Disposition2 is the overwrite-capable `CREATE_ALWAYS` policy; this is not `CREATE_NEW`. Share0 governs sharing once the handle is open, rather than reserving the earlier candidate name during the attribute probe. The retained span includes the bit tests, disposition branches and API argument construction; exceptional/native opener routes beyond that span are not presented as fully audited.

This resolves the BMP branch’s prior open-mode unknown. An intervening file creation or a candidate misclassified as absent can reach an overwrite-capable open attempt. It does not prove that any existing file was actually overwritten. The worker still ignores the save helper result, so normal thread return does not establish successful saving. PNG/JPEG use a distinct GDI+ route whose replacement behaviour remains outside this finding. No filesystem write or race test was performed.
