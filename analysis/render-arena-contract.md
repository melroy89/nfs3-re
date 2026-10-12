# Render temporary arena contract

Initializer004bbd80 requests0x800000 heap bytes, saves raw base,
aligns the initial cursor to32 and sets capacity0x7fff9c.
Reset004bbd70 copies raw base back to cursor without realignment.
RenderRaceViewport004bc470 unconditionally resets at entry; frame
dispatcher004bc680 invokes one or two viewports. Cursor usage
therefore does not accumulate across successive viewport calls.
This is not proof of backend completion before reuse.

Within a viewport, RenderRaceScene004bc160 sequences builders
without another reset. World transient builder004cbc90 considers
600 records and emits at most one160-byte command each: maximum
96000 bytes, aligned-size multiple32. Its initial peek request
0x17700 does not reserve/check that extent; it writes first, then
commits emittedCount*160 and ignores allocator success.

Allocator004bbde0 advances/rounds cursor before checking capacity,
and does not roll back if abort returns. Peek004bbe40 checks only
the existing cursor and ignores the requested size. Existing
headers already document this ordering; no overflow was observed.

Resolved: configured allocation/capacity, per-viewport reset boundary
and world-builder payload maximum. Astra later: aggregate spatial,
weather, overlay and HUD maxima; pre-write extent invariants; raw
base alignment guarantees; backend retention across cursor reuse.
Capture cursor/base/capacity at viewport entry and each builder,
plus backend command consumption timing, before interpreting reuse
as a lifetime defect. Static evidence only; executable unchanged.
