# INI environment-key construction

LookupIniEnvironmentOverride004fb734 creates uppercase SECTION_KEY in a
256-byte local buffer. The underscore word write and remaining-count
decrement are unconditional after section copy; arbitrary exhausted input
is not safely handled locally.

The observed direct callers are ReadGameIniInteger004fb6f0 and
ReadGameIniString004fb714. Integer reader has12 direct call sites, all in
LoadGameIniSettings004b5580. String-reader caller functions are004a6e68,
004b5580 and004b5844. Reviewed arguments use fixed sectionNFS3 and fixed
constant-pool keys. Longest used key ScreenshotterEnabled has20 characters:
NFS3_ plus key plus NUL totals26 bytes, below256. ScreenshotterFormat has19.
Pool presence alone is not use; unrelated longer strings do not alter this
observed bound. Parent checked helper assembly, integer xrefs and pool bytes.

Oversized-name construction is excluded for these direct static arguments.
Unrecognized indirect calls, altered/aliased strings and arbitrary generic
helper inputs are outside this conclusion. Search-table/environment-value
ownership and other INI boundaries remain independent unresolved contracts.
No executable or environment settings were changed.

## Integer reader history

The retained 1.1.0 reader at `004fb6f0..004fb702` passes the caller's EDX fallback directly to GetPrivateProfileIntA. The 1.2.0 reader adds a call to `004fb734` before that API. When the lookup returns nonzero, the reader calls the integer parser at `004f0430` and uses its EAX result as the fallback passed to GetPrivateProfileIntA. This dates the environment fallback path to 1.1.0 → 1.2.0 for the inspected integer reader. The environment value feeds the API's default argument, with the INI lookup still performed.

All retained 1.2.0–1.6.1 members keep this instruction sequence apart from the import operand. The PE thunk names GetPrivateProfileIntA at slot `00534674` through 1.4.0, `0053466c` in 1.5.0–1.5.2, and `00534670` in 1.5.3–1.6.1. These are static call contracts. Actual parsed values and operating-system INI behavior were not exercised.
