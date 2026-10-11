# Best-lane percentage and cone-hit display

The display identity and ordinary static sampling cadence are closed. Assembly00489900 uses text IDs0x152/0x153/0x154 and formats `%d%% %s` and `%d %s`. Source keys are kTextHudBestLanePct, kTextHudOneConeHit and kTextHudConesHit, obtained from the00561c44 pointer table. Installed English pack FEDATA/TEXT/text.eng resolves these to **in best lane**, **1 cone hit**, and **cones hit**. Thus the first line is, for example, `75% in best lane`; the second is singular or plural cone hits. This is resource/render-call evidence, not a screenshot or proof of the selected runtime language.

Renderer00489900 is now named RenderBestLanePercentageAndConeHits. EAX carries percentage and EDX cone count. Its first rendering helper004897f0 explicitly saves/restores EDX, preserving the second-line argument. Six stack arguments retain their original signature; RET0x18 verified.

The count chain is0042b900 (+61c callback, priority50 on even-tick list007d3690) ->004297d0 ->00493ad0 ->00493a30. Outer callback requires byte+88==0 and+89!=0 to reach the contact dispatcher; dispatcher additionally requires categorybit04 to process cones. Cone processing requires effective cones006fd498!=0, ordered vehicle+b8>=5.0, and excludes bit01/state3 for the lane tally. Hence at most one lane sample per ordinary even-tick callback, subject to all these gates; it is not every elapsed tick and is not stationary-time coverage.

Before signed tick1152, every eligible sample increments matches+2dc. Afterwards the profile lane qualifies when the center or either lateral edge matches; otherwise misses+2e0 increments. Display consumers calculate signed integer100*matches/(matches+misses), default100 for empty counts, under ordinary nonnegative/no-overflow assumptions. Cone contacts tally+2d8 independently; cone processing precedes lane sampling and can tally contacts even when the lane result is a match.

Sampling identity/cadence is statically resolved under unchanged callback registration. Actual on-screen presentation and trace cadence are not runtime-tested here. Opponent recovery attempts versus successful resets and pursuit/network suppression remain separate open questions.

English resource SHA-256: `63e013c04341706543c6e59ec00475cce281bad68dd46220b41fa5ccb8a62886`.
