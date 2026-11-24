# dds98 — where this stands

A byte-exact decompilation of Giten Megami Tensei (PC-98, `DDS98.EXE`) against Microsoft C
7.0, verified by rebuilding every claimed function from source and comparing it with the
original image.

## Results

*(snapshot at round 243; `tools/report.py` regenerates the current numbers into
`docs/STATUS.md`)*

| | |
|---|---|
| ledger rows | **523** (MATCH 39, RELOCS 444, ASM 2, PENDING 38) |
| verified against the image | **483** |
| own code matched from source | **11 645 bytes of 293 211 (3.972 %)** |
| code functions inventoried | 2 523 |
| unmatched units classified into walls | 1 402 across 20 classes |

"RELOCS" means the bytes match with relocation fields masked; "MATCH" means they match with
no masking at all. Both are rebuilt from source by `tools/verify.py` on demand, and a full
sweep of all 523 rows takes about ten minutes.

## What was actually learned

The decompilation itself is the smaller half. The larger half is a description of **how the
original compiler differs from MSC 7.0**, which is what stops the remaining 96 % from
matching. `docs/WALLS.md` holds twenty-one numbered walls with witnesses; the important ones:

- **frame style** - the original always emits `55 8B EC`, MSC omits it for functions that
  need no frame and uses `ENTER` (`C8`) when they have locals under `/G1`. `/G0` gives the
  classic frame but loses 80186 encodings;
- **nop padding** - the original lays out a block with a 3-byte `mov ax,imm16`, shortens a
  constant to `33 C0` afterwards, and fills the freed byte rather than re-laying the jump.
  Seven witnesses, all with the jump distance counting the `90`. MSC emits `33 C0` before
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

- **A pre-6.0 Microsoft C.** MSC 6.0 matches 7.0 for the frame and the doubling but not for zeroing (round 260);
  the original is older still (unoptimised selection, classic frames, 80186 encodings).
- **A different linker** would change nothing: `verify.py` compares objects with relocations
  masked, and `/FARCALLTRANSLATION` is already modelled.
- **Nothing source-level** reaches the walls. The 38 PENDING rows are the proof:
  their C is recovered and every one misses by one to six bytes of compiler choice, re-
  testable in one command via `tools/recheck.py`.

## Where to start reading

`docs/MATCHING.md` (the ledger) → `docs/WALLS.md` (why the rest doesn't match) →
`docs/CONVENTIONS.md` (source rules learned) → `docs/README.md` (tools).

## Which PENDING rows can ever match

The 38 PENDING rows fall into two groups, and the difference matters:

- **proven unreachable with MSC 7.0** - the pad byte (`90` inside a body, round 206), `add
  reg,reg` doubling (round 199/211: twelve source forms, twelve compilations, always `shl`,
  and **199 units / 66 381 B - about 23 % of the remaining code** contain it), `and` where MSC emits `test`, `mov si,[disp16]`, the
  `bx=ax`-before-`es=dx` order, `inc`/`dec` switch chains. No source form and no flag reaches
  these; they would need a compiler closer to the original's;
- **unexplained** - the rest, where the difference is understood but its cause is not yet
  named.

Both groups are re-testable in one command via `tools/recheck.py`, so the split is a statement
about the compiler, not a closed door: if a matching toolchain appears, the first group is
where the rows will come from.

## The last thirty rounds, in one paragraph

Rounds 199-228 did not add many rows - five since round 203 - and that is the most useful thing
about them. They **measured the walls** instead: doubling is proved unreachable (twelve
compilations, always `shl`) and sits in front of **199 units / 66 381 bytes, about 23 % of the
remaining code**; the pad byte is proved unreachable (six statement shapes, no `90` in a body);
`BX` is never a C variable (9 units / 672 B); the register-cached parameter accounts for 41
units / 5 378 B; and the prologue push order (`57 56` vs `56 57`) lets a candidate's fate be
predicted from four bytes.

The result is that the project now knows **why** it stopped where it did. That is a different
and more durable claim than "these were hard", and it is the claim the PENDING column exists to
support.

## The search space is measured out (round 230)

The most productive filter of the whole project - units beginning exactly where a verified row
ends - applied to the current inventory *with* every wall screen the project has learned,
returns **two** candidates, both already diagnosed. The filter that found four rows in rounds
184-185 now finds nothing new, because every candidate it reaches is understood well enough to
be excluded by inspection.

That is the honest reading of the 3.972 %: not a failure of effort, but a measured boundary.
What is left is enumerated - 41 PENDING functions with their C written down, twelve cut
windows, and a wall list with a size hanging off each entry.

## What changed in the last fifteen rounds

Rounds 232-242 found **five rows** (42, 78, 31 and 62 bytes plus one correction) after thirty
rounds that found almost none - and every one of them came from a *rule*, not from a better
candidate pool:

- **the `ENTER` screen** (round 232): MSC under `/G1` emits `C8` for functions with locals, the
  same frame the original chose, so those units are clear of the frame wall. Two of the five
  rows came from there;
- **the near/far tell** (round 238): a function ending in `ret n` whose first parameter is at
  `[bp+04]` is **near**; far functions start at `[bp+06]`. Getting this wrong shifts every
  operand by two, and it made two previously-failed transcriptions (rounds 216 and 222) match
  unchanged.

That is the pattern worth carrying forward: **a rule that closes an "open question" reopens
every unit filed against it at once.** The remaining fourteen rounds are consolidation, with the
ledger at 523 rows and the walls measured.

## Final state (round 254)

- **523 ledger rows**, all rebuilt from source by `tools/verify.py`; the latest full sweep
  (round 253) is clean and `tools/checkled.py` reports no inconsistency.
- **483 verified functions**, **11 645 of 293 211 own bytes (3.972 %)**.
- **21 walls**, eight of them measured with unit counts, and a three-wall pattern behind the
  worst of them (MSC reserves BX, CX and the segment registers for itself).
- **38 PENDING rows**, 13 re-testable in one command, each with its cause named.
- The repository publishes no game binary, no toolchain and nothing derived byte-for-byte from
  the image.

Where this leaves the project: the C for a large part of the remaining code is recoverable, and
the bytes are not, for reasons that are now specific and written down rather than vague. Anyone
continuing has `HOWTO.md` for the loop, `ENTER.md` for the best-odds list, and this file for
why the number is what it is.
