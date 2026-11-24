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

### The mechanism, from five witnesses (round 172)

Five units now show the same two-byte fingerprint, and they are all the *same* shape - a
constant stored on one path, a jump over the other path's constant, and a `90` in the gap:

| unit | the padded sequence | note |
|---|---|---|
| `3cd1:02f2` | `B8 01 00 EB 03 90 33 C0` | range check, one `return 1` |
| `2e68:000c` | `B8 01 00 EB 03 90 33 C0` | two-word long comparison |
| `1fe2:000a` | `B8 FF FF EB 03 90 33 C0` | guarded `return -1` |
| `48eb:000c` | `B8 01 00 EB 03 90 33 C0` | (round 121) |
| `4998:000c` | `B8 01 00` ... `90` | (round 121) |

In every one of them the **jump distance is correct for the padded layout** - the
displacement counts the `90` - so the padding is not dead space that a later pass could
reclaim, it is part of the address arithmetic. That is consistent with exactly one
mechanism: the block was laid out with a 3-byte `mov ax,<imm16>`, the *second* constant was
shortened to the 2-byte `33 C0` afterwards, and the freed byte was filled rather than the
jump re-laid-out.

Because MSC emits `33 C0` before it lays out the block, it never has a byte to fill and so
never produces this shape - and no source form changes that. The practical consequence: any
unit whose only difference is one byte of branch distance across a `90` is at the wall, and
should be marked PENDING rather than retried.
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

### Parameters are allocated before locals (round 158)

A related ordering fact, verified on `20f9:000c` (44 B): the original keeps a **parameter**
in DI and a **local** in SI, while MSC gives SI to the first `register` declaration and
parameters are declared first, so it produces the swap (`8B 76 06` where the original has
`8B 7E 06`). Declaring both parameters `register` moves the local to the frame (`ENTER`,
`C8`) instead of fixing the swap.

So a unit whose register assignment is "local in SI, parameter in DI" is unreachable: no
declaration order can put the local first.

### `|` operand order is not source-controlled (round 152)

For `return table[bit] | array[index];` MSC always loads **`array[index]` into AL first**
and ORs the table byte second, whatever the source order and whichever of the two
subexpressions is written first. Five shapes were compiled (`|` in both orders, the bit
index in an `int` and in an `unsigned` variable, and `n % 8` instead of `n & 7`): all five
produce byte-identical code. The original does the opposite - the mask table goes into AL
first. So `2603:463c`'s single remaining difference is not expressible in C.

## 15. Direct memory-to-SI/DI loads (`8B 36` / `8B 3E`)

The original sometimes loads a word straight from an absolute address into a pointer
register: `8B 36 10 00` (`mov si,[0x0010]`), and `159d:190d` / `159d:1914` do the same with
`A1` plus `8B FE`. MSC 7 does not emit that form: it loads through AX or BX instead
(`BB 10 00 8B 1F` for `bx = 0x10; bx = [bx]`), and with a `register` pointer it emits
`push si` + `BB` (under `/Os`) or `BB` alone (under `/Ox`).

Five source shapes were compiled for `159d:18f2` (the 9-byte byte-mask on the BIOS pointer
at `0x0010`): plain pointer, `register char *`, `register int` plus a cast, subscript and
explicit `+ 10`. None produce `8B 36`, so the encoding itself is unreachable - a sixth
form of the register-naming family, but a distinct one worth naming because it is about
*encodings*, not allocation.

### The zeroing opcode is context-dependent (round 174)

`3d85:000e` shows MSC emitting **`2B C0`** (`sub ax,ax`) where the original has `33 C0`
(`xor ax,ax`) - the reverse of the usual complaint. The context is a `long` global being
cleared, which MSC does with `sub ax,ax` followed by two word stores; three spellings of
the zero (bare `0`, `0L`, a braced block) all produce it.

So `2B C0` is not unreachable in general - it is unreachable *for a plain `int` zero*. That
narrows wall 12 rather than confirming it, and it means any unit whose only difference is
`2B C0` versus `33 C0` should be checked for a wider-integer context before being written
off.

## 16. MSC duplicates short epilogues; the original jumps to one

Distinct from wall 2 (padding): here the two exit paths differ in *size*, not by one byte of
displacement. `315b:0008` (53 B) is the clearest witness. The original ends

    6A 0F 56 90 0E E8 ...  EB 07  90  56 90 0E E8 ...  5E C9 CA 02 00

with **one** `pop si` / `leave` / `retf 4` shared by both paths, while MSC emits the same
five-byte tail twice (once after each call), and the two branch distances grow by exactly
that difference. So a conditional whose two arms end in a call has a shared tail in the
original and duplicated tails in MSC.

Four other units differ only in this way (`3cd1:02f2`, `5026:013e`, `3d91:0020`, `37c1:0004`),
which makes it the second most common remaining cause after the padding itself - and, unlike
the padding, it is a *layout* choice rather than a missed peephole, which is why no source
shape has produced it yet.

Practical rule: a unit whose two arms end in identical instruction runs, with a short `jmp`
between them, is at this wall and belongs in PENDING.

## 17. Range guards cache the index in BX; MSC compares the frame slot

A recurring shape in this binary is a bounds-checked table lookup:

    if (i >= 0 && i < N) return table[i];
    return -1;

The original loads `i` into **BX once** (`8B 5E 06`) and tests the register twice; MSC emits
`83 7E 06 00` / `cmp [bp+6],N` and only loads BX to index. Four units show it:
`43a1:0000`, `4a9f:0004`, `3e48:000a` and `2141:00a6`. It is a register-*caching* decision
(wall 7's family), and no combination of `register` on the parameter changes it, because a
parameter can only be register-ised when the function also keeps something else in a
register.

Practical rule: a unit whose guard tests a register that was loaded once from the frame is
at this wall; a unit that tests the frame slot directly is probably not the same function.

### The prologue push order is fixed (round 196)

When a function saves both registers the original pushes **DI then SI** (`57 56`); MSC
pushes **SI then DI** (`56 57`). Verified on `31cd:0006`, whose count variable lands in SI and
whose parameter in DI - the same assignment as the original - so the only difference is the
order the two saves are emitted in. It is not affected by declaration order, by `/Ox`, or by
using an early `return` instead of `if (n) { ... }`.

Practical rule: a unit whose prologue is `57 56` and whose body otherwise matches is at this
wall; a unit whose prologue is `56 57` may still match if the assignment is natural.

### Doubling: `add reg,reg` is unreachable (round 199)

Six source forms were compiled for `x * 2` - `x * 2`, `x + x`, `x << 1`, `y = x; y += y;`,
`2 * x`, and `x * g` - and **all six** produce `D1 E0` (`shl ax,1`). MSC never emits
`03 C0` (`add ax,ax`) for a doubling, in any context or under any flag.

So this class - 37 units / 4 767 bytes in `BLOCKED.md` - is closed for this toolchain: the
original's doubling idiom cannot be produced, and the units that carry it are unreachable
rather than unexplained. The same applies to the index scaling in `41d8:000c` and the value
doubling in `4e11:007e`, which are now understood as one behaviour rather than two.

## 18. Windows that span two functions

`1ab4:000c` is inventoried as one 72-byte function but contains a `ret` at offset `0x1A` with
another function's code after it. A `C3`/`CB` in the middle of a unit, with code following
that cannot be reached from the start, means the window spans **two** functions - the third
such case found (`2141:00a6`/`00b4` is split at a `jmp`, `2daa:0000`/`000a` at a segment
boundary).

The first function of `1ab4:000c` is 27 bytes and matches as a row; the second is a separate
function the ledger will need its own row for.

Practical rule: before transcribing, check for a return instruction that is not at the end of
the unit. If there is one, match only up to it and treat the remainder as a separate
function.

### The nop is unreachable too (round 206)

The padding mechanism needs the compiler to put a `90` **inside** a function body. Six
statement shapes were compiled to see whether MSC ever does - an empty `else`, a trailing
`;`, a `switch` with `default: break;`, an `if (x) { }`, `do { } while (0)`, and a two-armed
`if` - and **none of them emits a `90` in the body**. MSC's only `90` is the alignment byte
at the end of a segment.

So, like the doubling wall, this one is closed rather than open: the eleven PENDING rows whose
sole remaining difference is a pad byte are not waiting for a flag, they are waiting for a
different compiler. That distinction is now recorded in `docs/SUMMARY.md`.
