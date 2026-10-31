# Camera-choice cleanup: Done path extracted, non-Cancel exit path added

## Scope and identity

The [focused audit](scripts/audit_camera_duplicate_callers.py) checks both executable fingerprints, paired camera callback registrations, action-handler paths, complete transition callback `0045d9e0..0045daa4`, and the shared duplicate-comparison instructions. The [manifest](evidence/audits/camera-duplicate-callers.json) retains addresses, span hashes and disassembly paths. No menu, replay, race, file save or instruction probe was executed.

Registration rows `00555d50` (`pscamera`) and `00556008` (`camera`) are byte-identical in original and Modern. Both name initializer `0045d920`, transition callback `0045d9e0`, and final callback `0045d9a0`. This establishes the transition counterpart using named registration evidence rather than same-address assumptions. The broader [registration/layout research](original-modern-menu-callback-table.md) keeps callback fields and layouts version-specific.

## Existing action path: comparison instructions become a callable helper

Original handler `0045d770` examines its action input. Its action1 path marks the output byte1 and calls `004446c0`; a zero return at `0045d7a4` jumps to inline comparisons at `0045d7ae`. After those comparisons original loads EAX=3 at `0045d832` and unwinds the handler's frame.

Modern's corresponding action1 path calls the same helper, rejects unsigned results≥2, sets the output byte1 for accepted results, and when the result is zero calls extracted helper `0045d7ad` at `0045d798`. It then restores its PUSHAD frame and returns EAX=3. The result1 path exits with EAX=0 after marking the output byte. These are verified raw action/helper-result values; no general replacement with a Boolean contract is justified.

The 132 comparison bytes `0045d7ae..0045d832` are byte-identical between versions. Modern adds PUSHAD at `0045d7ad`, then POPAD/RET at `0045d832`; the original same address was a RET on a different handler path. The [small-entry comparison](original-modern-small-entry-followup.md#duplicate-choice-code-receives-a-callable-register-preserving-boundary) gives the complete six-check order. This is extraction of existing checks, not a newly invented algorithm.

## New cleanup on the registered transition path

Both transition callbacks derive a menu entry from the incoming context and inspect entry type5 plus token match against `CANCEL_CAMERA_OPTIONS`. The matching Cancel branch restores saved state and bypasses the normal continuation. Their restore implementations differ: original explicitly copies saved cells to camera globals, while Modern uses four MOVSD instructions and also restores `006fd1cc`. Complete snapshot-source meaning and lifetime are not established as equivalent here.

On the other branch, original proceeds directly to retained call `00472300` at `0045da49`. Modern instead reaches newly inserted `CALL 0045d7ad` at `0045da44`, then falls through to that same call. The branch displacements at `0045da0c` and `0045da1d` are retargeted to include the new cleanup. The full tail `0045da49..0045daa4` (91 bytes) is byte-identical, including the existing update calls and return sequence.

This closes the missing local mechanism behind the bypass claim: normalization is no longer confined to the action-handler's inline completion path; it also runs on the registered camera transition's non-Cancel continuation. Exact routing of every named Race, Credits and Exit game button through this callback still requires the full dispatcher/lifecycle chain. Equal later call bytes do not establish equal persistence results or transitive callee behavior.

## What normalization guarantees

The helper checks the four DWORDs `006fbba8/ac/b0/b4` in priority order and clears later matching entries to zero. It does not exclude zero from comparisons and does not guarantee four distinct raw values. Its relevant established effect is removal of later repeated **nonzero** choices under the ordered comparisons; zeros may remain or be introduced repeatedly. Intended meaning of zero and every choice's localized label are separate data contracts.

**MP151-002: partial static support.** The original completion-path checks, extracted register-preserving helper and added non-Cancel transition call are verified. Universal duplicate-free saving, exact named-button reachability, runtime behavior and introduction in v1.5.1 are unverified. No camera selection was changed, and no executable, Ghidra, raw export or maintained C was modified.
