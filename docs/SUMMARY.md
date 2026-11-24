# dds98 — where this stands

A byte-exact decompilation of Giten Megami Tensei (PC-98, `DDS98.EXE`) against Microsoft C
7.0, verified by rebuilding every claimed function from source and comparing it with the
original image.

## Results

*(snapshot at round 209; `tools/report.py` regenerates the current numbers into
`docs/STATUS.md`)*

| | |
|---|---|
| ledger rows | **517** (MATCH 38, RELOCS 438, ASM 2, PENDING 39) |
| verified against the image | **476** |
| own code matched from source | **11 351 bytes of 293 211 (3.871 %)** |
| code functions inventoried | 2 523 |
| unmatched units classified into walls | 1 402 across 20 classes |

"RELOCS" means the bytes match with relocation fields masked; "MATCH" means they match with
no masking at all. Both are rebuilt from source by `tools/verify.py` on demand, and a full
sweep of all 512 rows takes about ten minutes.

## What was actually learned

The decompilation itself is the smaller half. The larger half is a description of **how the
original compiler differs from MSC 7.0**, which is what stops the remaining 96 % from
matching. `docs/WALLS.md` holds seventeen numbered walls with witnesses; the important ones:

- **frame style** - the original always emits `55 8B EC`, MSC omits it for functions that
  need no frame and uses `ENTER` (`C8`) when they have locals under `/G1`. `/G0` gives the
  classic frame but loses 80186 encodings;
- **nop padding** - the original lays out a block with a 3-byte `mov ax,imm16`, shortens a
  constant to `33 C0` afterwards, and fills the freed byte rather than re-laying the jump.
  Six witnesses, all with the jump distance counting the `90`. MSC emits `33 C0` before
  laying out, so it never has a byte to fill;
- **register allocation** - follows *lifetime*, not declaration order: the longest-lived
  value gets SI. The source can move a short-lived parameter into DI
  (`register int r, a; a = a0;`) but not a long-lived value;
- **register naming** - the original reaches for DX and CX where MSC uses AX. `/Ox` fixes
  this for register *reuse* and for the CX cache in large functions, and makes it worse in
  short ones;
- **encodings MSC never emits** - `mov si,[disp16]`, `8B E0`-family direct loads into a
  pointer register, `sub ah,ah` for a plain byte load, `and` where MSC uses `test`,
  `inc`/`dec` chains for dense switches, a shared epilogue where MSC duplicates it.

## Method that worked

1. **`tools/dis.py` first.** Hand-decoding produced at least three wrong conclusions; the
   rewritten decoder (ModRM, absolute branch targets, `68`/`6A`) removed an entire class of
   error.
2. **Screen for candidates, not for functions.** The productive filters were: units sitting
   in segments that already have matched rows, and units that begin exactly where a verified
   row ends (same source file, same style). Together they produced six rows.
3. **Extract a rule from every miss.** The prototype-decides-widening rule, the `void`-vs-
   `return 0` rule, and the `8A E0`/`8A C4` rule each came from a one-byte miss and each
   then paid for itself.
4. **Try flags before theories.** `/Ox` resolved four units that `/Os` missed. MSC 6.0 was
   tested and does not help.
5. **Verify everything, always.** `verify.py` caught a wrong row size, a duplicated row, and
   a "match" that was really the next function's bytes.

## What would move the needle

- **A pre-6.0 Microsoft C.** MSC 6.0's codegen matches 7.0's for every wall that matters;
  the original is older still (unoptimised selection, classic frames, 80186 encodings).
- **A different linker** would change nothing: `verify.py` compares objects with relocations
  masked, and `/FARCALLTRANSLATION` is already modelled.
- **Nothing source-level** reaches the seventeen walls. The 39 PENDING rows are the proof:
  their C is recovered and every one misses by one to six bytes of compiler choice, re-
  testable in one command via `tools/recheck.py`.

## Where to start reading

`docs/MATCHING.md` (the ledger) → `docs/WALLS.md` (why the rest doesn't match) →
`docs/CONVENTIONS.md` (source rules learned) → `docs/README.md` (tools).

## Which PENDING rows can ever match

The 39 PENDING rows fall into two groups, and the difference matters:

- **proven unreachable with MSC 7.0** - the pad byte (`90` inside a body, round 206), `add
  reg,reg` doubling (round 199), `and` where MSC emits `test`, `mov si,[disp16]`, the
  `bx=ax`-before-`es=dx` order, `inc`/`dec` switch chains. No source form and no flag reaches
  these; they would need a compiler closer to the original's;
- **unexplained** - the rest, where the difference is understood but its cause is not yet
  named.

Both groups are re-testable in one command via `tools/recheck.py`, so the split is a statement
about the compiler, not a closed door: if a matching toolchain appears, the first group is
where the rows will come from.
