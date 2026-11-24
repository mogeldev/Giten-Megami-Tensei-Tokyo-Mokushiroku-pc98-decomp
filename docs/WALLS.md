# Compiler walls

Everything that currently stops a verified C transcription from matching the image,
with a verified example for each. Every entry below is a *code-generation habit* of
whatever compiler built the original - the C and the encoding are understood in each
case; only the instruction selection, register choice or ordering differs.

The order is roughly "most units affected first" where that is known.

## 1. Frame/instruction coupling (`ENTER` versus classic)

MSC 6/7 tie the prologue style to the target level: `/G0` (8086) cannot emit `ENTER`
and uses the classic `55 8B EC` + `83 EC nn` frame; `/G1` uses `ENTER`. The original
uses the **classic frame together with 80186 encodings**, which no flag combination
produces.

- Frame itself: **solved** - compile units with locals under `/G0`
  (verified on `103b:000c`, 63 B).
- Residual: a unit containing `6A` (push-imm8) cannot match under `/G0` either.
- Examples: `200d:0006` (one byte wrong under either flag), `1036:000c`.

## 2. Nop padding after short jumps and block ends

The original pads with `90` where MSC does not, so every following branch distance
differs by one. Verified on `1036:000c` (`75 06 ... EB 19 90` versus `75 05 ... EB 18`),
`13d5:000c`, `4998:000c`, `3b88:000e`, `31e3:0064`, `3cd1:02f2`, `3b9b:000a`.
No optimizer setting (`/Os /Ot /Ox /Od`) emits it. **This is the single most valuable
wall to break**: ~139 units / 21 kB carry the pattern.

## 3. Immediate pushes

The original follows the 80186 rule - `6A` for small values, `68` for large. MSC uses
`6A` always (`/G1`) or `B8 xx` + `50` (`/G0`). Example: `41e7:000a` (one byte).

## 4. Register-parameter assignment

MSC and the original disagree about which parameter gets SI; four units contradict
every simple rule (see `CONVENTIONS.md`). Example: `218f:0004` / `2191:0008`
(two prologue loads swapped), `3874:000a`, `4e58:0004`, `3ede:00a0`.

## 5. Assignment persistence

The original keeps a value in a scratch register across several statements; MSC spills
it to a frame slot. Examples: `122f:000c` (original stores `r` *earlier* than MSC),
`1e38:0002` (original keeps the saved global in DX for ten statements and needs no
frame at all).

## 6. Register reuse

The original reuses a register once its value is dead (`a` in SI, then the result in SI
again). MSC allocates a second register and saves it in the prologue. Example:
`4ab2:000c`.

## 7. Scratch-register naming

Where MSC reaches for AX, the original often reaches for CX or DX (and vice versa).
Examples: `1486:0002` (`lea cx,[bp-4]` / `xor dx,dx` versus `lea ax,[bp-4]` /
`xor cx,cx`), `4e72:000a` (`8B D8` / `8E C2` order), `322c:002c` (push AX versus push SI).

## 8. BX as a register variable

The original pushes BX in the prologue and uses it as a callee-saved register variable;
MSC only allocates SI/DI and treats BX as scratch. Eight units (518 B) start
`55 8B EC 53`; example `11a2:000c`.

## 9. Scheduling

Two distinct effects, both verified:

- **hoisted constant pushes** - MSC pushes a later call's constant arguments before the
  preceding call, because they do not depend on its result (`3e34:000a`);
- **load/store interleaving** - MSC loads a second parameter between the first store,
  where the original loads both then stores both (`3b2b:000c`).

## 10. Argument evaluation order

The original evaluates a later argument before an earlier one in some calls; MSC pushes
left to right. Examples: `31dd:0008`, `3a51:0004`.

## 11. Split far-pointer loads

The original loads a far pointer word by word (`8B 5E 06` + `8E 46 08`); MSC emits
`les`. Also covers the mirrored inlined `MK_FP` (`8E 06 <disp>`), which MSC turns into
a helper call. Examples: `2aa3:0048`, `465d:0000`, `3807:0004` (and its two duplicates),
`21ee:0008`.

## 12. Byte arguments and byte selection

The original pushes a `char` argument unpromoted, or stores AH directly
(`26 88 27`); MSC promotes, or copies AH to AL first. Examples: `3c3d:000c`,
`2d60:000e`, `29ed:0004`.

## 13. CX caching, constant folding, `or reg,ax`

Three small peephole-level differences: the original caches a parameter in CX for
repeated compares (`1e1e:002a`, `1f45:00b0`); the original does not fold
`(v << 1) & 1` to zero (`29ef:0007`); the original ORs a register with AX where MSC ORs
it with itself (`200d:0006`).

## What would unblock the most

1. **The padding rule** (wall 2). It blocks whole families and is the reason several
   otherwise-perfect transcriptions miss by exactly one byte.
2. **A pre-MSC6 compiler build.** Walls 1, 3, 4, 6, 7, 8, 9 are all "how the older
   compiler allocated and ordered things" - a working MSC 5.1 or 6.00A driver would
   settle several at once. Both extracted drivers currently run and exit without
   producing objects (`GAP.md`), and the remaining hypothesis needs an observable
   console.
