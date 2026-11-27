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

## String reader history

Version 1.1.0 passes the caller's EDX string fallback directly to GetPrivateProfileStringA from entry `004fb704`. Version 1.2.0 moves the entry to `004fb714`, calls the environment lookup at `004fb734`, and substitutes the returned pointer for the EDX fallback when nonnull. The Windows INI call still runs with the same file, section, key and output arguments.

All retained 1.2.0–1.6.1 archive members retain this setup sequence. The import operand names GetPrivateProfileStringA at `00534678` through 1.4.0, `00534670` in 1.5.0–1.5.2, and `00534674` in 1.5.3–1.6.1. Thus both string and integer environment fallbacks appear at the same checked release boundary. Actual INI lookup and environment pointer lifetime remain outside the static comparison.

## Environment key construction by release

The complete lookup body at `004fb734..004fb76d` is byte-identical in 1.2.0–1.4.0. It copies section and key around a one-byte underscore, then uppercases the assembled buffer in a separate pass. In 1.5.0–1.6.0 the body differs only in the three relative call operands for the copy and uppercase helpers. Version 1.6.1 replaces that sequence with two calls to `004f9424`, which uppercases each byte while copying through `004eede0`. It writes underscore and a zero byte together at `004fb74b` and removes the separate uppercase pass. All three versions of the wrapper call `0050ead0` with the assembled key. The comparison dates the construction rewrite and preserves the observed uppercase lookup for ordinary shipped keys. It leaves arbitrary-length input and locale-dependent conversion outside the equivalence claim.

The lower-level environment lookup at `0050ead0..0050eb29` is byte-identical in the supplied original and all eleven Modern archives (90-byte span SHA-256 `b457b67c61410eb28ba8d75c682f111ad05dbdc34f16bb35cf467be96e406dbc`). It scans the runtime environment vector at `00a0b154`, checks the name prefix and requires an immediate equals sign. It returns a pointer into the first matching entry, immediately after the equals sign, or zero on a miss. The INI readers therefore reuse an existing lookup routine when they add environment fallback in 1.2.0. The span equality leaves comparator behavior outside the body, vector initialization and pointer lifetime unverified.

The lookup's comparison path is shared as well. The inspected spans at `00523d10..00523d81`, `0052b5e0..0052b63a` and `0052e350..0052e39e` are byte-identical in the supplied original and all eleven Modern archives. The comparator at `00523d10` calls character helpers and a normalization path before comparing. A direct, case-sensitive byte comparison would therefore be an unsupported substitute for the original routine. The comparison establishes that Modern reuses these existing instructions. The locale-dependent mapping and its state remain unresolved.
