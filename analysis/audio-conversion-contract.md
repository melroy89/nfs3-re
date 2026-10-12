# Audio conversion and pitch contracts

Static assembly evidence from persistent Ghidra program `nfs3.exe`; no
runtime observation or binary changes. This report indexes the bounded
findings in [detailed notes](detailed-analysis-notes.md#sound-pitch-dispatch-boundary-refinement).

| Boundary | Established | Remaining |
| --- | --- | --- |
| Converter004e1ae4 | Signed channel upper check; range enabled only for end>0; inclusive length and shifted working pointer; ignored free result; DLL callback publication004e1e46 | DLL argument producers, allocation-base ownership, bounds and failure reachability |
| Packer00500910 | Mutable first source lane; one WORD per8-byte pair; exact mask saturation; zero count returns without access; no rounding helper | Amplitude domain, ambient x87 state, count/pointer wrap and aliasing |
| Factor00522e90 | Per-selected-factor float stores; zero and INT_MIN return1.0 | Caller bounds, table admission, signed mask overflow and numerical equivalence |
| Ratio00522f10 | Final truncation toward zero for finite signed32-representable truncated results | Earlier arithmetic precision, zero divisor admission and exceptional behavior |
| Dispatch00522f50 | Unsigned upper cap0x80000; stride0xde4; no local index guard | Index admission and backend callback lifetime/ABI |
| Rate producer004e225c | Conditional nonzero selection with precedence0800/0400/1000/2000/0200 | Initialization ordering and indirect/overlapping writes |
| Playback00522510 method3 | QWORD FISTP then low-DWORD callback argument; distinct from DWORD ratio conversion | Pitch bounds, backend ABI and exceptional values |

Packer00500910 has no CALL instructions. Its FSTP float at00500942
uses ambient control state, unlike the explicit truncation helper used by
the pitch converters. Source advances8 and destination2 per iteration.
Count0 exits at the initial unsigned end-pointer comparison without access.
Exactly count pairs are processed only under positive nonwrapping extents;
negative/wrapped counts and source/destination overlap require separate proof.
Parent verified Luna's assembly findings and saved the expanded plate comment.

The broad audio item stays Open. Astra should trace the DLL conversion callback
argument producers before any targeted runtime test; establish voice index/rate
admission and callback ownership separately. Numeric equivalence needs explicit
x87 control state, exceptional-input policy and instruction-equivalent cases.
No uncaptured gameplay or local lack of checks proves a reachable failure.


## Signed16 expansion and x87 stack capacity

ConvertSigned16SamplesToFloat005008a0 converts unscaled signed16 values
exactly to binary32 when source/destination extents are valid, nonoverlapping
and the x87 stack has capacity. Its grouped path005008b5..c9 pushes eight
values consecutively before popping any: it requires an empty incoming x87
stack. The scalar tail requires one free slot. Nonpositive signed counts skip
sample accesses. Caller stack occupancy and stack-fault policy remain Astra
questions, alongside buffer admission and aliasing; no runtime fault is proven.
Ghidra plate comment saved after direct assembly verification.

Direct xrefs to005008a0 include004e1b6a plus0052cd30/0052cd84
(finite reader),0052ce57(looping reader),0052cf41(refilled reader),
and0052d068(queued reader). Ordinary selector0 converter entry through
004e1b6a performs no local x87 initialization/clearing; it calls VirtualAlloc
first. Thus this local path does not independently establish the empty-stack
precondition. Incoming ABI/callback guarantees still require evidence.
Parent inspected complete assembly listings for all four reader bodies,
corroborating Luna's finite/looping/queued reviews: none contains x87
instructions or local initialization. Finite reader calls memory fill004e0640;
refilled reader can call005678b4 indirectly; queued reader calls00511998 and
005118fc. Those callees and incoming ABI are separate state boundaries.
The absence of local floating instructions establishes no occupied-stack fault
and no empty-stack guarantee. The eight-slot requirement remains Open.
