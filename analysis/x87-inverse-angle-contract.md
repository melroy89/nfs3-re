# x87 inverse-angle helper

Full wrapper assembly004f9482 and sqrt/error helper0051a1ba were reviewed,
including dispatcher004e06d9 and compatibility wrapper004ff624. Ghidra names
are ComputeX87AcosWithDomainHandler and SqrtX87OrDispatchDomainError.

Entry ST0=x becomes the pair(1-x*x,x). Positive radicand is square-rooted;
two FXCH operations cancel before FPATAN, giving atan2(x,sqrt(1-x*x)). The
wrapper subtracts that angle from the extended pi/2 constant0056719c
(bytes00c06821a2da0fc9ff3f). This is acos on the ordinary domain, preserving
actual extended intermediates rather than claiming libm bitwise equivalence.
AX is preserved by the wrapper; its inferred integer return is not the result.

FTST/FNSTSW/SAHF/JNZ routes both zero and unordered radicands to FCOMPP.
That comparison consumes radicand and x; ordered radicand>x loads pi,
otherwise zero. Consequently -1 returns pi and+1 zero. NaN inputs take the
zero branch if masked exceptions allow continuation. Negative radicand
enters the error helper. Its XCHG saves the incoming selector in[EBP-8];
MOV EAX later restores that selector before comparing AL with3. Wrapper
selector1 therefore always pops both radicand and original x, passing the
latter as a double to0051655c. That handler delegates selector2041 to005243a7;
its returned policy-dependent value bypasses the angle/subtraction sequence.

Compatibility flag00567858 bit0 selects004ff624 instead of direct FPATAN.
That wrapper saves/restores FPU state and merges status.0051f320 has a custom
normalized-finite-nonzero operand path; other encodings fall back to FPATAN.
Exact custom-path approximation, exception policy/unmasked behavior, and
quaternion caller normalization/range remain unresolved. No numerical or
runtime equivalence test was performed. The local stack/domain trace is
established; the broader inverse-angle contract remains partial.

## Quaternion caller domain gate

SlerpQuaternionsWithLinearFallback begins004b71e0;004b725b is its acos call
site. Full caller assembly verifies negative-dot sign correction at004b7217,
then comparison of1-dot with binary double0.0001 (0053ff60,
hex2d431cebe2361a3f). JBE004b7256 takes linear weights on equality or unordered
comparison. Ordered finite dot values reach acos only after sign correction
and with1-dot>epsilon, bounding this call inside the valid acos domain.
Values with magnitude>=approximately0.9999, infinities and NaNs use linear
weights instead. There is no input normalization or clamp. This closes the
local caller's domain-admission question under ordinary masked arithmetic;
unit quaternion/output normalization, exception policy and compatibility
approximation remain unresolved. Earlier generic caller-range uncertainty
is refined by this explicit gate, not by assumed unit inputs.

## Viewport blend boundary

004223c0 is now BlendViewportPoseWithStoredCameraTransform. Selected view
quaternion+120..12c is loaded raw; input matrix converts through004b73c0.
Optional row0/2 sign conversion and004b7300 sign alignment do not establish
normalization. Result interpolation is converted to matrix without a local
unit/orthogonality check. Ordinary-range weight uses the sigmoid expression
1/(1+exp(-4pi*(view+110-.5))), with actual float constants/x87 operations.
Stored float weights may round to0/1; arbitrary huge/exceptional exponent
inputs and source-field units/range remain unvalidated. A mathematical
sigmoid interpretation is not a proof of strict runtime interior weights.

## Mode-specific producer alias boundary

UpdateActiveViewportSceneModes00426680 requests mode17 through00422610 and
then reloads the active base pointer005e10b0 before writing+114=raw1/6. If
transition eligibility fails, that pointer is mode17: updater00425640 uses
+114 as an effect-definition ID and+118 as effect index. If eligibility
succeeds, Begin selects mode19 and the caller writes the transition-state
field, consumed as float by004262a0. The immediate writes therefore cannot
be described universally as float progress increments. Old-scene eligibility
byte/matching fields decide identity; no installed runtime branch or stalled
transition is established. Quaternion storage comes from extracted old pose
matrix conversion/sign alignment, without local normalization validation.
