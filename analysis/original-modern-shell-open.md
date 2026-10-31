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
