# Original versus Modern: screenshots and movie-stop input

## Evidence boundary

Static comparison of the [identified original and official Modern binaries](original-modern-differences.md), addressing **MP140-059**, “Screenshoting doesn't stop intro movie.” Reproduce the paired playback/abort/input bodies with `python3 analysis/scripts/audit_movie_volume_difference.py`; the [manifest](evidence/audits/original-modern-movie-volume.json) retains their spans and equality checks. The Modern keyboard-hook/request consumer is independently retained by the [screenshot audit](original-modern-screenshots.md) and [request/feedback analysis](original-modern-screenshot-feedback.md). No keypresses, movie playback, target instructions or Ghidra edits.

## Playback stop rule remains

Complete movie abort helper **`00495b10..00495b2d`** is byte-identical. It calls **`00451960` with EAX=1** at `00495b18`; any nonzero result stores **`0079f330=1`**. The main playback body calls this helper at **`00496068`** during playback and **`0049609f`** during its later wait path. The playback loop checks the same stop global at `00495e7a` and exits the decode loop when nonzero. Screenshot handling is not a special case in this abort helper.

The complete shared playback address envelope **`00495bc0..004960e0`** differs at only **three bytes `00495e02..00495e04`**, belonging to the [movie-volume initializer redirection](original-modern-movie-volume.md). There is no changed local abort branch to explain the screenshot claim. Earlier wording that this envelope contained other changes has been corrected after the full byte comparison. Equal local bytes do not imply equal input providers, assets or called routines.

## Input poller changes its screenshot call

Complete **`00451960..00451b1b`** differs only in the displacement of the call at **`00451969`**:

| Version | Call target |
|---|---|
| Original | `00451810`, the Alt+P chord checker and synchronous screenshot path |
| Modern | `004c4480`, the pending screenshot request consumer |

All other bytes in this input-poller envelope match. It still polls other input providers and returns a filtered input value to the unchanged movie abort helper. This comparison does not assume those providers themselves have identical bodies.

The original screenshot chord is checked through held scan codes **38h and19h**, whereas the new [hook](original-modern-screenshots.md#official-modern-print-screen-queues-capture-for-a-worker) recognises **VK2ch (Print Screen)** and queues a request. A held-key screenshot check and ordinary stop-input polling are separate mechanisms in the old path; this evidence does not prove that every old chord invocation produced a stop event.

## Modern consumes the matching screenshot hook event

The retained complete hook **`004ccb84..004ccc3f`** requires hook code0 and active flag `009f3d4c != 0` before its filtering path. When screenshot setting `00561288` is nonzero and decoded virtual key is2ch, it passes the derived down/up value to **`004cdc50`** at `004ccc13`, then jumps to **`004ccc31`**, returning **EAX=1**. It does not take the forwarding call through IAT `005346f4` on that matching branch. The helper may rate-limit or merely update held state; the hook's handled return does not depend on a newly queued capture.

Thus the matching screenshot event is handled through the hook/request path while the movie's own abort rule continues to depend on the ordinary input poller's result. The changed call at `00451969` consumes pending captures even while movie playback polls for stop input; it does not itself reinterpret a capture request as a movie-stop return value. The hook and worker details are reused from the existing screenshot investigations rather than inferred from the release-note wording.

**Bounded conclusion:** MP140-059 has partial static support through the distinct handled Print Screen path and its connection to movie polling. The patch preserves the movie's ordinary nonzero-input stop rule. Actual hook installation/selection under Wine or Windows, downstream input-queue contents, simultaneous other keys, disabled screenshot configuration, capture success and observed uninterrupted movie playback remain unverified. This is not a runtime proof that every screenshot attempt can never stop playback.
