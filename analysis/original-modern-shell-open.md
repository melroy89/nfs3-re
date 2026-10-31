# Shell-open wrapper: owner argument simplified

## Evidence and boundary

The original and Modern wrappers both start at `00418cc0`. Original returns at `00418cea`; Modern returns at `00418cdb`, followed by NOP filling. The [static audit](scripts/audit_small_wrapper_differences.py) compares the complete original envelope `00418cc0..00418ceb`, verifies both executable hashes, checks imported symbol bindings and records [span hashes and disassembly locations](evidence/audits/small-wrapper-differences.json). No shell operation was executed.

## Verified behavior

Both pass incoming EAX as the file/path argument to `ShellExecuteA` through import slot `00534480`. Both pass the file-backed string `open` at `00536c30`, null parameters, null working directory and show-command integer 1. Both preserve incoming ECX/EDX and return EAX=1 regardless of the shell function's returned value.

The original first calls `GetModuleHandleA(NULL)` through `0053454c` at `00418cd3`, then pushes its returned module handle as the first, owner argument to `ShellExecuteA` at `00418cdb`. Modern removes that query and pushes zero as the owner before the shell call at `00418cd0`. Original also saves/restores EBP to establish an otherwise unused frame; Modern removes that frame setup.

The confirmed difference is therefore **module-handle value versus null owner**, plus the removed API call and frame. An HMODULE value is not established as a valid window handle by this code. Whether this change fixes a particular desktop, URL or Wine behavior has not been tested. The wrapper's constant return is not proof that the requested path opened successfully; neither version checks a shell error result here.

## Reconstruction and remaining limits

Preserve the chosen version's owner value and constant-return contract when reconstructing this wrapper. Introducing success/failure propagation would change original behavior. The incoming path's lifetime, all caller intents and resulting external application behavior are outside this bounded comparison.

**Work status: done for this wrapper. Evidence confidence: verified static bytes, imports and argument construction.** Runtime effects remain unverified.

## Retained URL-selection caller bounds the practical difference

The expanded wrapper audit now pins complete `004a4020..004a404f` (47 bytes), identical in original and official Modern. It reads selector `0055e894`: value1 supplies `0053ce9c`, value2 supplies `0053ceb8`, other values return without the shell request. The paired file-backed strings are unchanged: `http://www.NeedForSpeed.com` and `http://www.NeedForSpeed.com/download.asp`. These are inert reference strings; their current availability or ownership was not checked and no URL was opened.

At `004a4048`, the caller invokes `00418cc0`, then returns without testing EAX. Thus the verified owner-argument simplification reaches an unchanged URL-selection path, not evidence of replacing those URLs with a Modern Patch website. This also distinguishes the path from the [removed original DDE routines](original-modern-removed-dde.md): both versions already have this ShellExecute caller, so DDE removal must not be presented as proof that ShellExecute was newly introduced. Selector producers, callback admission and actual user-visible launch timing remain unresolved. No browser, shell or target code was executed.
