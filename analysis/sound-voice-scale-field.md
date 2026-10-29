# Sound voice scale field at record +0x0b

## Finding

For the active installed `nfs3.exe` (SHA-256 `2a20f80465ed53d320f1a6f41c9dde2c07de0bc5525af1f23f8e6aff3e6181fb`), voice-slot byte `+0x0b` is populated by the ordinary tagged patch/timbre voice constructor. It is copied from byte `+0x6c` of the constructor's caller-supplied context object. The tagged parser is a normal caller, but the available static evidence does not prove that this offset maps to a named header field or particular tag identifier. Stream startup later reads the selected slot's byte `+0x0b` into global `005646ff`, where the remaining-count helper uses it as an unsigned divisor.

This establishes a concrete data source and its arithmetic role. It does **not** establish that the descriptor field represents samples per second, kilohertz, milliseconds, or any other physical unit. The multiplied-by-1000 numerator in the consumer is insufficient to infer such units.

## Producer path

`00501de8` parses tagged patch data. Its normal `0xfe` record branch calls `00501978` for records that pass the key/velocity range checks; after the tag loop, it can also make one final `00501978` call for the encompassing range. This identifies `00501978` as a normal record-to-voice construction path, rather than an exceptional-only writer. Evidence: `ev_7d3e62b6925d251e8a26bd76027a80aa035aba573c73b052d7adc10c4066bfcc`.

`00501978` obtains an available voice-slot index from `004ff86c`, computes the slot address at base `00a09b3c` with a `0x60`-byte stride, and fills fields from its caller-supplied context in ESI. The decisive instructions are:

- `00501af4`: call allocator `004ff86c`;
- `00501b03..00501b14`: calculate `00a09b3c + index*0x60` into ECX;
- `00501ce4`: load `AL` from `[ESI+0x6c]`;
- `00501ce7`: store AL to `[ECX+0x0b]`.

This is an exact byte-for-byte copy; no conversion or scaling occurs at construction. `00501de8` invokes `00501978` in its ordinary `0xfe` tagged-record path after checking the record's key/velocity range, and can invoke it once more for the encompassing range. This ties the write to ordinary tagged patch/timbre creation, but does not identify which parsed tag or source member supplies context offset `+0x6c`. Evidence: `ev_fc537c02d3fa381e58cdd5f03bd52b81b23d6a6f0a7e1dd98ad3b386c9509953` and assembly from the same procedure; parser evidence `ev_7d3e62b6925d251e8a26bd76027a80aa035aba573c73b052d7adc10c4066bfcc`. The allocator's normal selection logic is in `004ff86c` (evidence `ev_ceb63f2c93c7a5afadcc6f11ee9c62b8f2b6033ce7138e5487c86c031cb3ee52`).

The stream-start path `004e89f8` validates/selects the current voice with `004e8fd0`/`004ffc9c`. On successful stream creation, it computes the selected record address using the same `0x60` stride, loads its `+0x0b` byte at `004e8a8d`, and stores it to `005646ff` at `004e8a93`. Evidence: `ev_63519f41896eca32140fc1a47bb4cbeaf56261b92830704cfb0fec851bad3ff4` and `ev_5eefb0322b6a54eb9dbfc4f6c25d3fb4e4f216d94e7061dbf474989119ef3ae9`.

## Consumer and interpretation limit

`004e7ce0` calls remaining-count helper `004e7c58`, constructs `count * 1000`, zero-extends byte `005646ff` into ECX, and performs signed `IDIV ECX` at `004e7dbd`. Since the divisor came from an unsigned byte load, its numeric range at this use is 0..255; the surrounding ordinary code does not name or convert the field. The resulting quotient is compared with signed threshold `0056476c` in `004e7df4`.

The evidence supports describing `+0x0b` as a caller-context-provided byte scale/divisor in this estimator. Neither the source field name nor a producer-side unit conversion is present in the examined path. In particular, `1000 / byte` does not prove a time unit, because the numerator is a count-like chunk quantity and the byte's encoded meaning is unresolved.

## Similar-looking initializer, kept separate

`004e9b20` initializes a temporary stream/patch parameter block and writes zero at that block's `+0x0b`. In `004e89f8`, the caller passes a stack temporary (`LEA EAX,[ESP+0xc]`) to this initializer. This is not the allocated voice-slot record written by `00501978`; it does not contradict the later descriptor copy into slot `+0x0b`. Evidence: `ev_fc7b1c72bfff52abfba6b2408b40275a16af24547c383e03fb1ebbb3ed9fa60b` and `ev_63519f41896eca32140fc1a47bb4cbeaf56261b92830704cfb0fec851bad3ff4`.

## Reproduction and boundary

The selected executable is the installed file at `/home/melroy/.local/share/winegui/prefixes/NFS3/dosdevices/c:/Program Files/Electronic Arts/Need For Speed III/nfs3.exe`. Useful bounded disassembly commands:

```sh
objdump -d -M intel --start-address=0x00501af0 --stop-address=0x00501cf0 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004e89f8 --stop-address=0x004e8ac7 '<selected nfs3.exe>'
objdump -d -M intel --start-address=0x004e7ce0 --stop-address=0x004e7dcc '<selected nfs3.exe>'
```

Analysis was static against the executable identified above. REA's temporary binary session was closed. The specific source-field semantics and units remain unresolved; no gameplay/audio runtime observations were made.
