# Race-exit/menu hang observed in Wine

User reported progressive slowdown after leaving the GOFAST race for the menu, eventually appearing hung. The reset sampler was stopped, its process absence verified, and the game remained alive. No debugger was attached (TracerPid0). A two-second /proc CPU delta measured the main thread at100% of one core. No kernel messages appeared in the preceding five minutes; memory and I/O pressure averages were zero at inspection. These observations do not establish the cause of the earlier slowdown.

A separate bounded read-only perf capture used cpu-clock:u at19Hz for3seconds, PID88396, yielding57 samples in /tmp/nfs3-hang-perf.data. It completed and did not suspend or terminate the game. Displayed samples included00410a03 (StopMusicStreamAndReleaseLoadedMap),004e76d1/004e76d6 (ServicePeriodicCallbacks),00500e21/28 (sound critical-section entry),004ffc9d (voice-handle validation),00501671 (sound voice status), plus Wine addresses. This is statistical instruction-pointer evidence, not a complete call-stack trace.

004109d0 waits while004e74f0 returns signed positive, servicing periodic callbacks between polls; no local timeout. The sampled00410a03 lies in this music-stop polling path. This strongly directs follow-up to music stream/voice shutdown and scheduler progress. It does not establish which state remains positive, the audio backend failure mechanism, or GOFAST causation. No memory patch, game termination or executable modification was performed. Further runtime/reset testing remains on hold until the hang is resolved.

## Recovery and bounded static follow-up

User subsequently reported responsiveness returning with lingering slowdown, then normal speed after a clean restart. No hang fix was applied. A persistent deadlock is therefore not established; the sampled stop loop may have been a temporary wait during shutdown and does not alone explain the progressive menu slowdown.

Assembly narrows the stop condition:004109d6 loads006fbb54 intoEDX and enters only when zero. No intervening instruction changesEDX before004e7470, so that wrapper receives duration100 inEAX and target volume0 inEDX. It stores target byte00564702=0 and calls004e9420 to fade the stream voice.004e74f0 returns the effective signed voice-volume byte via00501670 when the handle is valid, otherwise falls back to signed00564702. Thus an invalid handle by itself returns0 and ends this wait if the target remains unchanged; it is not sufficient to explain indefinite positive polling. Getter00501670 samples voice+31 after releasing the audio critical section, so this is not a lock-protected snapshot of subsequent state.

Remaining candidates include delayed audio-service progress, a competing target/voice update, and backend scheduling; none was established by the short profile. The game binary remains unchanged. Reset capture now supports --reset-only and configurable interval; use0.05 seconds for the bounded reset test, omitting repeated physics/spike reads. This reduces work but does not claim sampling caused the slowdown.

## Static fade progress dependency

ServiceSoundVoiceEnvelopesAndCallbacks00500c80 visits16 voice records.
Only byte+0c==1 with a nonnegative handle enters update. Nonzero signed
delta+18 adds to current16.16 volume+20; crossing target+1c in the delta's
direction clamps to target and clears delta (00500d16..46,00500da4..b7).
The dirty path recalculates effective output005014a0 and dispatches00501540.
004e9420 computes delta as signed integer(target-current)/max(duration,1);
its duration is a service-update divisor, not independently milliseconds.
Zero delta bypasses this ramp, while modulation/envelope paths may still
change effective output. Registered callbacks run before the voice loop.

Thus repeated music-stop polling does not itself prove fade progress:
service invocation, callback return, eligible voice state and absence of
competing writes matter. Actual service routing/cadence and sampled state
remain unresolved. This adds no runtime observation or explanation of the
reported slowdown. Ghidra00500c80 includes the bounded progression proof.

## Installed DLL host-callback route

REA decompilation of installed eacsnd.dll (SHA256
63f3d1bff4e6526753524423be47146e82416d1b170cd7b2e0133699587b01b3)
closes the missing static callback link. Loader004e1e55 passes
InvokeSoundDriverHostCallback004e1adc as argument5 to DLL setter004013d8,
which stores it at DLL0040a914. DLL fill helper00402110 calls this slot
when signed chunk budget0040a8e4<1, before replenishing that budget.
Service export00402324 reaches fill after eligible cursor and region-lock
paths. No universal one-callback-per-service or wall-clock cadence follows.
Game wrapper004e1adc dispatches00a09b08, ordinarily00500c80.

Evidence: setter ev_3b1a168b4b4859ff741d79d60b3af9911b6471a7cf6017c36ba88dfa948ecfea;
fill ev_5536bd1c01beaffa5308035855a2a30f1c0f7cfbcfe556e5da1943d0dc6cdb32;
service ev_d85c67f9fa9b5a0f6579deeefa2580876628ebd85987af9b9107ad559eb35115.
These are static provider pseudocode observations, not execution traces.
Backend errors, stalled cursor or unavailable fill regions can bypass this
route; none was captured in the historical slowdown. Its cause remains open.


## Zero-delta and effective-volume narrowing

Parent follow-up inspected live Ghidra pseudocode for004e9420/005014a0 and independently decoded original bytes005014a0..00501537 with objdump. At stop target0 and duration100, for a stable nonnegative current16.16 value C, signed truncation gives delta=-C/100. Delta is zero only for C0..99; those values have C>>16=0. Effective-volume recomputation at005014b5..005014e8 multiplies that shifted value by the other factors, so its initial effective byte becomes0. Optional modulation via record+58 multiplies this byte and therefore preserves0. The final optional response table at record+4c can replace0 with table[0] (00501526..31).

Therefore a zero delta alone does not imply a persistently positive effective byte after recomputation when C is nonnegative and response mapping is absent or table[0]=0. This is a conditional arithmetic result, not a closure of the hang: zero delta may bypass recalculation in the service path, an earlier effective byte may remain stale, table[0] can differ, and concurrent writes/service eligibility are not captured. Negative or mutated inputs fall outside the bounded argument.

A future read-only capture should retain the selected music handle00564690, target00564702, sound initialization state, all16 raw0x60-byte voice records at00a09b3c, and caller polling/service progress. In each eligible voice retain handle+0, state+0c, delta+18, target+1c, current+20, effective byte+31 and response/modulation pointers+4c/+58. Resolve the selected handle through the validated handle contract; do not assume its raw value is a row index. For a mapped response table record table[0] only after verifying readable mapping. Samples are asynchronous and cannot establish writer order. No game was running during this pass; cause remains OPEN.


Capture preparation: `analysis/scripts/sample_music_shutdown.py` implements the bounded fixed-map voice snapshot above. CLI help and three invalid duration/interval cases passed without creating output. Live memory acquisition remains NOT RUN until the game is launched and readiness verified. The user has been asked to wait at the main menu; no race action requested before capture.

## Live preflight for the ordinary-race comparison

The exact installed image was launched in its existing Wine prefix from a parent capture process. Direct sibling-process reading was denied; parent-to-child O_RDONLY access succeeded without changing OS policy. Capture verified the live code signature and all fixed ranges, reported READY, and produced growing0.1-second samples. The sampler now optionally captures setup globals and bounded vehicle activity alongside the16 audio voice records. This proves acquisition works; it does not reproduce the slowdown or establish race-exit behavior. The coordinated scenario is a stock Diablo, Hometown forward/day/dry,2laps, no opponents, TrafficOn; approximately60seconds driving, then Quit toMainMenu and20seconds waiting. Scenario execution and resulting analysis are pending. Raw capture remains outside the repository until a reviewed bounded extract is prepared.

## Completed ordinary baseline: slowdown not reproduced

The coordinated ordinary SingleRace test completed with Hometown/forward/2laps, stock Diablo, None opponents and TrafficOn. The user saw grey and likely red traffic, paused, then confirmed return to the actual main menu remained responsive. The assistant independently captured the MainMenu screen. This is distinct from the earlier responsive in-race pause menu.

The race music handle5327 was last matched to an eligible voice before its sampled retirement at capture time454.97seconds; target then reads0. A new menu music handle6912 is present from457.99seconds, with target/effective volume95 and no ramp delta in the retained menu samples. The retained follow-up covers more than60seconds after that new voice appears. Handle resolution uses the reviewed low-five-bit index, nonzero rowstate and full handle equality, not an unchecked row assumption. These asynchronous observations demonstrate a completed ordinary transition and a stable new voice, not the precise service callback or retirement instruction order.

Capture ended normally after5,251samples at0.1-second requested intervals, with zero capture-error records. [Retained audio/transition evidence](evidence/runtime/ordinary-race-menu-return-audio.json) includes selected states, the completed capture hash and the main-menu screenshot hash. [Traffic evidence](evidence/runtime/ordinary-single-race-traffic-observation.json) is separately bounded. The old progressive GOFAST/menu slowdown did not reproduce; its cause remains OPEN. No fix or universal shutdown guarantee is claimed.

Stopping the parent capture was followed by the game process exiting, despite the launcher's intended leave-running behavior. Future orchestration must place the Wine child in its own session and verify that it survives sampler completion before promising to leave it open. No executable or live-memory write was made.
