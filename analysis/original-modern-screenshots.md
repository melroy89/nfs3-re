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

The capture launcher at 004c452c allocates a per-capture record and invokes CreateThread with entry 004e3078 (entry pointer pushed at 004c459a; API call at 004c45a3). The handle is closed immediately after successful creation; the worker owns and releases the capture record. The worker formats nfs3_%04d.%s using the prefix .\\screenshots\\ (data at 0053f7f4; format string at 0053f804) and writes BMP or GDI+ PNG/JPEG output. The configured default string is png (constant at 0053f6cc, passed by LoadGameIniSettings at 004b568c..004b5691); unrecognized/unsupported format is normalized to BMP. The prefix is relative to the process working directory; startup directory selection is not established by this capture. The asynchronous handoff and relative output prefix are proven by the code path; completion or success of a particular file write is not.

The detailed Modern-side ownership and format evidence is in [screenshot worker admission audit](screenshot-worker-admission-audit.md) and [screenshot lifecycle contract](screenshot-lifecycle-contract.md). Those documents concern the locally installed Modern-derived target; the addresses and instructions summarized here were rechecked against the official package executable fingerprint above.

## Retained instruction witnesses

Run `python3 analysis/scripts/audit_screenshot_difference.py` from the repository root (Python `pefile`, GNU `objdump`). The [manifest](evidence/audits/original-modern-screenshots.json) hash-checks both baselines and records half-open instruction spans for the original key/wrapper/capture/Desktop/TGA paths and Modern hook/request/capture/worker/default paths. It also records the exact filename/path strings from both images. Raw assembly stays under ignored `analysis/captures/modern-differences/screenshots/`. This is static capture, not screenshot or instruction execution.

## Concrete before/after behavior

For the inspected original, Alt+P drives a direct call that captures and writes a numbered TGA file into the Desktop directory. In the official Modern build, Print Screen drives a pending request; the capture is handed to a worker thread and is written beneath the relative screenshots directory. The Modern default format constant is PNG, subject to the configured format and fallback logic. This is a binary-supported output and scheduling change, not merely a README comparison.

## Limits

- Conclusions are tied to these two fingerprints. The original artifact's exact retail provenance is not authenticated by this review.
- The original Alt+P sequence is supported by scan-code checks 0x38 and 0x19, the call through 00452410 to 004c4490, and the matching historical README note. No keyboard was used.
- CreateThread proves the Modern launcher requests asynchronous execution; it does not prove worker scheduling relative to later captures, shutdown overlap, or successful encoding.
- The Modern worker's shared format/encoder state and teardown risks are documented separately; this comparison does not claim an observed race.
- The original registry query establishes the configured Desktop path lookup, not every possible Windows shell-folder redirect or write permission outcome.

No executable, runtime configuration or Ghidra project was changed. No game, test, or runtime probe was run.
