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
