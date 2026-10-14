# Lap-count producer boundaries

Live Ghidra assembly review, program nfs3.exe. This separates local write
domains from game-wide admission and storage capacity.

| Direct writer | Local value source |
| --- | --- |
|0044c29b frontend reconciliation|Decoder004cf190 yields2/4/8 from selector lowWORD|
|004743ad/004743b9 mode1 roster|Literal2 if signed session>1, otherwise4|
|00474011 mode2 roster|Literal2, EBX set before store without intervening call|
|0049a829 network settings|Zero-extended BYTE0079f8f4, local domain0..255|
|0049e17d supplied transport setup|Full DWORD007a200c, previously traced CLI -LAPS source|
|0047248f default initialization|Literal2; explicit transitive ECX preservation verified|

Ghidra's direct xrefs-to audit for `006fd4b4` corroborates this writer inventory: the only direct write references are initializer `0047248f`, menu reconciliation `0044c29b`, mode1 roster `004743ad`/`004743b9`, mode2 roster `00474011`, network-settings publication `0049a829`, and supplied transport setup `0049e17d`. This closes the direct-reference inventory in the current program database; it does not rule out writes through aliases, bulk copies or unmodeled indirect paths.

Network writer0049a822..29 has no local menu decoder before publishing
the packet byte. Therefore frontend2/4/8 normalization cannot be generalized
to every lap-count write. This does not prove an arbitrary byte is admitted
by a peer, survives later reconciliation or reaches per-lap storage.

Astra residuals: packet authority/length and setting admission, all ordering
and alias writers, later initialization ordering, participant/track-specific lap
consumers and complete per-lap array extents. No safe expansion maximum or
reachable runtime defect is established. Binary unchanged; existing Ghidra comment at0049a520 already documents
this network writer and was corroborated against assembly. No new network
comment was needed.


## Default-source proof boundary

Default initializer sets ECX2 at00472462, but calls004cef00 at0047247b
before storing ECX at0047248f. The helper does not directly assign ECX;
it calls profile helpers0044f5d0,0044f670,0044fa90,0044f510 and0044f5f0.
A direct register scan therefore cannot alone close the stored default value.
Luna and parent verified the complete bounded preservation chain:0044f5d0
and0044fa90 are leaf bodies without ECX writes;0044f670 saves/restores ECX;
0044f510 and0044f5f0 also save/restore it around nested calls. The intervening
caller instructions leave it unchanged. Thus normally returning inspected
initialization paths store literal2. Ghidra initializer comment saved.
This resolves the default-source question; later writers remain separate.

InitializeRaceLapEstimates already has saved comments documenting signed
global-count loops over object+240 and+298, no local clamp, and the+298
seed read even for nonpositive count. Their0x58-byte spacing is not an
allocation proof. Establish object schema and callers before capacity claims;
this complex extent question remains Astra work.


## Lap-estimate consumer overlap boundary

Sole decoded caller004ce7c9 passes an AI-list005efb08 record when
category+200 bit10 is clear and status+2c4 is not3; status4 still qualifies.
Initializer entry is004ce5a0. Its float entry+298+4*i equals maximum
accumulator+2b8 at i8. Count>=9 therefore makes the loop treat that accumulator
location as a per-lap entry. This exact address identity does not prove
allocation capacity, unsupported-lap reachability or intended schema.
The ordinary menu2/4/8 choices use indices0..7, while broader writers require
separate admission/order proof. Ghidra comment records this boundary for Astra.


## Existing type evidence

Live Ghidra type inspection confirms Nfs3RaceSettingsWirePacket is40 bytes,
alignment1: decoded lap count is BYTE+4 and encoded lap option is separate
BYTE+5. The receiver cache0079f8f0 therefore places them at0079f8f4/f5,
matching the reviewed writer. Packet width/schema is established independently
of supported gameplay capacity. Searches for Vehicle/Race types expose no
complete lap-estimate record type under those names; this bounded type-name
search is not proof that no alternate type exists. Do not create a guessed
22/8-element structure merely from field spacing.
