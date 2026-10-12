# Weather mode contract

Weather enable006fd4cc and particle mode are separate inputs.
GetEffectiveWeatherMode004dcdd0 returns0 when enable is zero;
otherwise returns particle mode. InitializeWeatherParticleState
004dcdf0 zero-extends source BYTE008ca1e8 and takes unsigned
remainder3, establishing initialized modes0..2. Mode0 skips the
remaining particle setup. This is not signed-DWORD modulo.

The initializer clears shared runtime/metadata/overlay blocks,
initializes two slots of800 position/metadata records and two
slots of20 overlay records. Configured counts derive from
percentages and have no local clamp to those capacities. Source
settings, later mutations and caller invariants require separate
evidence; initialized storage size alone is not an active-count
guarantee.

The in-binary menu label is generic weather. Numeric mode/texture
suffixes do not prove mode1=rain or mode2=snow. Atmospheric names
and visible appearance remain open for Astra, using loaded track
HRZ/WEATHER.FSH contents or a controlled capture of source byte,
effective mode, counts and corresponding appearance. Broader pool
ownership/rendering contracts remain in the historical backlog.

Resolved: enable/mode distinction and initialized0..2 range.
Evidence: current Ghidra decompilation/assembly annotations at
004dcdd0/004dcdf0; static only, no runtime or binary changes.
