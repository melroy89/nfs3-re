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
