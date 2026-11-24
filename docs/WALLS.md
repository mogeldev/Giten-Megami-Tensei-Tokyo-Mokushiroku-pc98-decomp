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

Round 120 refinement: MSC **does** emit the `90`, but only between *duplicated*
epilogues. Compiling `if (a) { h(a); return 1; } return 0;` with `/Ot` or `/Ox` gives

    ... B8 01 00 C9 CA 02 00 90 33 C0 C9 CA 02 00

- each path keeps its own epilogue and the compiler pads between them, which is exactly
  the shape seen in `13d5:000c` (pad after `CB`) and `48eb:000c` (pad after `EB`). `/Os`
  merges the epilogues instead and drops the pad.

So the wall is not "the older compiler pads"; it is **"the older compiler does not merge
return paths"**, and the padding is a side effect. That is a more useful statement: it
predicts that padded units also have repeated epilogues, and it points at a lever
(`/Ox`, `/Ot`) that reproduces the padding at the cost of a different epilogue shape.
`48eb:000c` under `/Os` is two differences from a row (the pad and the branch distance
it implies); under `/Ox` the shape changes too much.

### Original text

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

Round 129 added the `long` variant: `1c97:000c` keeps **halves** of two longs in
registers across the calls - `r`'s low word in SI and `a`'s low word in DI, with only
`r`'s high word spilled to `[bp-2]`. MSC allocates both longs as whole frame slots
(`89 46 FC` / `89 56 FE`). A *partial* spill of a long has no MSC equivalent at all, so
this is the strongest form of the wall.

## 6. Register reuse

The original reuses a register once its value is dead (`a` in SI, then the result in SI
again). MSC allocates a second register and saves it in the prologue. Example:
`4ab2:000c`.

## 7. Scratch-register naming

Where MSC reaches for AX, the original often reaches for CX or DX (and vice versa).
Examples: `1486:0002` (`lea cx,[bp-4]` / `xor dx,dx` versus `lea ax,[bp-4]` /
`xor cx,cx`), `4e72:000a` (`8B D8` / `8E C2` order), `322c:002c` (push AX versus push SI),
`1e1e:002a` and `1f45:00b0` (parameter cached in CX).

Round 123 added three units that are **otherwise perfect**: `3e48:000a` (24 B) and the
signed/unsigned clamp pair `2a28:0000` / `2a29:000c` (28 B each). All three differ from
their transcription in exactly one thing - the original keeps the working value in
**DX** (`8B 56 06`, `8B 56 0A`) where MSC uses AX. Because the pair differs only in its
comparison opcodes, both units resolve together if this wall is ever explained, which
makes them the best single test case in the project.

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

## 13a. CX as the scratch for a parameter test

A cluster of 10 units in the 36-130 byte range loads a parameter into **CX** and tests
it with `or`/`cmp` (`8B 4E 06` / `0B C1` / `74 xx`). MSC 7 puts the parameter in AX and
tests against memory under `/Os`, or in SI (with a prologue push) under `/Ox` - it
reaches for CX only in one large function (`1f45:00b0`, 59 B), which does match. Examples
of the blocked ones: `1f72:0044` and `1f7c:0008` (40 B each, `if ((a | b) != 0) { h(b, a);
g_46ec--; } return 0;`), `2ad6:000a`, `1e1e:002a`.

The source form matters and is worth recording: `if (a || b)` produces a compare chain,
while `if ((a | b) != 0)` produces the single `or` - the original has the `or`, so the
bit-or form is the correct transcription.

## 12b. `sub ah,ah` is NOT a wall (corrected in round 146)

The class used to be described as "the original zeroes with `2B C0`, MSC always emits
`33 C0`". That is true for `sub ax,ax` / `sub cx,cx`, but **false for `2A E4`**: MSC emits
`sub ah,ah` for a zero-extended byte load (`int f(unsigned i) { return
(unsigned char)g[i]; }` -> `8A 87 <t> 2A E4`) and for a byte field of a struct with
alignment greater than one. 74 units / 15 007 B were reclassified from blocked to
candidate on that basis.

What remains in that class is an **order** difference, not a missing opcode: the original
zeroes AH *before* the load (`C1 E3 02 2A E4 8A 87`), MSC after it (`C1 E3 02 8A 87 ...
2A E4`). Examples: `4344:000e` (19 B) and `43a1:0000` (38 B), the latter also caching the
index in BX.

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

### The padding has (at least) two causes

Round 121 checked the hypothesis on the unit it came from. `4998:000c` has a **single
shared epilogue** (`C9 CA 08 00` reached from both paths), so the non-merged-epilogue
explanation does not cover it. What it does show is:

    0x64  B8 01 00     mov ax,1
    0x67  EB 03        jmp 0x6c
    0x69  90           nop        <- padding
    0x6a  33 C0        xor ax,ax  <- 2 bytes where a 3-byte `mov ax,0` would fit
    0x6c  C9 CA 08 00  leave / retf 8

and `48eb:000c` has exactly the same shape. That reads as a **late peephole**:
the compiler laid out `mov ax,0` (3 bytes), later shortened it to `xor ax,ax` (2 bytes),
and padded the freed byte with `90` rather than re-laying out the jump. The jump
distance is correct for the padded layout, so whatever did the shortening knew the
padding would be there.

So there are at least two causes: non-merged epilogues (round 120, `13d5:000c`) and
this late-shortening pad (`4998:000c`, `48eb:000c`). `1036:000c`'s pad sits after a jump
before a `push`, matching neither description exactly - so the family is not fully
explained yet.

## 14. Frames on functions that need none

The original emits `55 8B EC` on **every** function, including ones with no parameters
and no locals (an empty five-parameter function is `55 8B EC 8B E5 5D CA 0A 00`). MSC
omits the frame entirely when nothing needs it: `void f(void) { h1(); if (g) h2(); }`
compiles to `9A ... 80 3E <g> 00 74 05 9A ... CB` with no `55 8B EC` at all, and neither
`/G0` nor `/Gd` changes that.

Detectable without disassembly: an unmatched unit whose body contains no `[bp+xx]` /
`[bp-xx]` reference but which still opens `55 8B EC` and closes `5D CB`/`C9` belongs
here. Example: `1270:000e` (22 B), `141f:0000` / `1420:000f` / `1466:0052` (9 B each).

### `/Ox` and wall 7 (round 139)

`/Ox` makes MSC cache a value in **SI** where the original uses **DX**, so it does *not*
help the scratch-naming family - it just swaps one wrong register for another. Verified
on `1e38:0002` (`8B 16 <g>` versus `push si`) and `4e11:007e` (`8B 56` versus `push si`).
The one case where `/Ox` did align a scratch register was wall 6 (register reuse across
a push, `50ff:000e`) and the large-function CX cache (`1f45:00b0`); everything else in
this family stays blocked under every flag combination tried.

### `|` operand order is not source-controlled (round 152)

For `return table[bit] | array[index];` MSC always loads **`array[index]` into AL first**
and ORs the table byte second, whatever the source order and whichever of the two
subexpressions is written first. Five shapes were compiled (`|` in both orders, the bit
index in an `int` and in an `unsigned` variable, and `n % 8` instead of `n & 7`): all five
produce byte-identical code. The original does the opposite - the mask table goes into AL
first. So `2603:463c`'s single remaining difference is not expressible in C.
