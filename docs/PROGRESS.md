# PROGRESS

## Register-local staging recovers two table relays
`439c:0006` and `439d:000e` (23 B each) verify as RELOCS. Both had been
near-misses because the original saves SI and pushes the lookup argument
from it. An explicit `register int` local with `/Os` reproduces that sequence.

## Packed-table reset verified
`42b9:0064` (21 B, RELOCS) marks 64 entries empty and zeros their counts
without modifying the flag bits. The reset starts after a return and padding
inside the preceding entry's inventory window.

## Verification now checks the recorded match class
Both MATCH and RELOCS return success from the matcher, so checking only its
exit code let the ledger report an incorrect class. The verifier now checks
which class was returned. The audit corrected `37c1:001e` to MATCH: all four
bytes already matched without masking. This does not change byte coverage.

## Backward packed-table traversal verified
`4332:000c` (TAKE_COUNTS, 59 B) verifies as RELOCS. The entry pointer walks
backward in DI while the index stays in SI for the helper call. The loop
stops early when subtraction leaves a nonpositive count.

## Packed table count adjustment verified
`4369:0084` (APPLY_COUNT, 49 B) verifies as RELOCS. A signed 11-bit field
reproduces the shift pair used to extract the key. With `/Ox`, the index
stays in DX for the conditional helper call.

## Signed bitfield swap and conditional stores verified
`477b:0032` (33 B) matches the compiler's signed 14-bit bitfield access and
writeback. `4b23:000c` (31 B) uses a local copy to keep the first argument
in DX, resolving the earlier STORE_IF near-miss. Both are RELOCS.

## Two frameless constant relays verified
`218a:0008` (6 B) and `4e45:0000` (15 B) match as RELOCS. Both call near
Pascal routines without a frame. The first wrapper ends in `retf`; the
second ends in `ret`, with one extra padding byte in the inventory window.

## A four-byte helper recovered from an oversized inventory window
`46e1:005c` (`_return_one`) matches `mov ax,1; ret` without relocation
masking. The near call at `469e:0000` targets it directly, distinguishing
this entry from the preceding routine's return path. Only its four bytes
are counted, not the 84-byte inventory window.

## Configuration comparison recovered beside the global relays
`4e8e:002e` (COMPARE_CONFIG, 65 B) verifies as RELOCS. Four ordered comparisons
share the `-1` exit; the optional fifth comparison can return `1`, otherwise
it returns zero. The 80-byte inventory window also contains padding and the
already-verified wrapper at `4e8e:0070`; those bytes are not counted twice.

## Two global relays matched by correcting the callee prototype
`4e8e:007e` (26 B) and `4e8e:0098` (35 B) verify as RELOCS. The missing
`sub ah,ah` from round 88 was an argument-width mismatch: the first byte
is passed as an `int` and must be zero-extended; the second is passed as a
byte and does not require its stack word's high byte to be initialized.

## Round 100 - signed threshold classification matches
`489a:000a` (CLASSIFY, 32 B) is an exact C match with no relocation masking.
Two early returns followed by the zero case reproduce the block order that
round 69 missed; `/Ox` keeps the input in DX for both threshold comparisons.

## Round 99 - explicit register shift yields an exact match
`4e23:0006` (SCALE64, 20 B) now verifies as MATCH with no relocation masking.
With `/Os`, `offset <<= 6` on the register local shifts SI in place before
moving it to AX. `offset * 64 + a` also generates a shift, but moves the
unshifted value to AX first and shifts there instead.

## Round 98 - two swap functions recovered from merged windows
A near-twin scan found `1fb1:0006` and `3bd6:001a`: both share the verified
swap-and-return body, with different DGROUP operands. The inventory reports 62
and 36 bytes, so the existing exact-size sweep skipped both. The actual bodies
end at `retf 2` after 19 bytes. Both compile from C and verify as RELOCS (+38 B).

## Round 97 - new tool finds a real function the inventory had lost
A different angle, and it produced a verified function plus a reusable tool.

- **`tools/framecheck.py` (new)** scans the load image for `55 8B EC` and compares the
  1184 hits against `units.csv`: 1161 are unit starts, **21 are mid-unit** (the merged
  blobs already documented), and **2 sit off-boundary right after a return** - the
  signature of a function the splitter missed. It reports the two with their bytes,
  so the finding is checkable rather than a claim.
- **`3d59:000c` RELAY2 (16 B, RELOCS, `src/calib/crelay2.c`)** - one of those two:
  `NEXT(a, b)`, far pascal. `units.csv` had recorded a fragment at `3d59:000e`; the
  real entry point is two bytes earlier, after the previous function's `retf` plus one
  padding byte. The call target (`E8 04 00` -> `3d59:001c`) lands exactly on the next
  function, which confirms the boundary.
- The other candidate, `2d3c:0000`, is blocked by trait 2 (`90 0E E8`: nop + `push cs`
  far call), and `29f7:0004` needs an absolute segment load. Both stay out.
- Ledger: 187 -> 188 rows - MATCH 32, RELOCS 131, ASM 1, PENDING 24.

## Round 96 - narrow-ASM policy is now enforced by a tool, not by good intentions
No new rows. Round 95 left a rule written in prose; prose does not survive 100 rounds
of an agent working alone, so the rule is now a check.

- **`checkled.py` enforces `ASM_LINE_LIMIT = 3`.** Any source referenced by an `ASM`
  row may contain at most three `__asm` lines. More than that means the row is a
  transliterated disassembly rather than a decompilation, and `checkled.py` fails with
  the file and the count. Verified by negative test: with the limit set to 2 the tool
  reports `ASM row 35ca:2306: 3 __asm lines ... exceeds the narrow-policy limit` and
  exits 1; restored to 3 it is green again.
- **Why the doubling family is not swept.** 22 framed units contain `add r,r`, and
  several are small enough to be tempting (`2121:000a` `g_6cb6[i]++`, `4db6:000c`
  `g_2c30[i & 0xF]`). But in every one of them the scaling instruction sits *inside*
  MSC's own index code generation, so patching it means writing the whole indexed
  access in assembly - four or more lines for a 24-byte function. That is exactly what
  the narrow policy forbids, so they stay blocked and the limit stays at 3.
- Ledger unchanged: 187 rows - MATCH 32, RELOCS 130, ASM 1, PENDING 24.

## Round 95 - inline assembly works; one ASM row, and a policy for it
The significant finding of the round is a capability, not a match.

- **`__asm` compiles in Microsoft C 7** and references C variables:
  `__asm mov bx, i` emits `8B 5E 04`, and `__asm mov ax, g_142a[bx]` emits
  `8B 87 <off>`. Verified with a probe function (`src/attic/casm3.c`, `casm4.c`).
- **First `ASM` row: `35ca:2306` IDX_142A (16 B)** - `g_142a[i]`, where the original
  scales the index with `03 DB` (`add bx,bx`) and MSC emits `D1 E3` for every C
  formulation tried. Three `__asm` lines reproduce the scaling; the prologue,
  epilogue and `retn 2` are compiler output. Byte-verified like any other row.
- **New status `ASM` and a written policy (`docs/ASM-POLICY.md`).** Inline assembly
  may stand in *only* for an instruction the compiler provably cannot emit; every
  other byte must be compiler output. Whole functions in assembly are forbidden -
  that would reproduce a disassembly, not a decompilation. `ASM` rows are
  byte-checked by `verify.py` but **excluded from `coverage.py`**, so the C coverage
  number keeps meaning what it meant.
- Tried and failed to use `__asm nop` to reproduce the jump-padding trait
  (`42e8:006c`): the nop lands in the right place (`EB 04 90 33 C0 99` matches) but
  the `__asm` clobbers MSC's register allocation, which then uses a memory compare
  (`83 7E 04 00`) instead of the original's `8B 5E 04 / 0B DB`. Inline asm is not a
  free lever for trait 4.
- Tooling: `checkled.py` and `verify.py` now report `ASM` as a fourth count; the
  ledger reads MATCH 32, RELOCS 130, ASM 1, PENDING 24.

## Round 94 — no rows; documentation inconsistency found and fixed
No new bytes. Two attempts and a real fix to the deliverable.

- **Stride-4 table accessors** looked promising (the family that gave ADDR4/SEXT11/
  MASKBYTE): `42e8:006c` (`at`: bounds-checked `&g_866e[i]`) and `43a1:0000`
  (`fetch`: bounds-checked `g_8870[i*4]`) both reproduce *almost* exactly under
  `/Ox /Oa /Os` — same `8B 5E 04 / 0B DB / 7C .. / 83 FB 40 / 7D ..` prologue — and
  differ only by the `90` padding the original carries before the failure block
  (`EB 04 90` vs `EB 03`). Trait 4 again.
- **Documentation inconsistency fixed.** The README still said "seven traits" while
  `docs/GAP.md` measured nine, and `CONVENTIONS.md` was missing row 9 (explicit zero
  materialisation) even though `gap.py` had been counting it since round 87. Both are
  now correct: **nine traits, table and counts agree**. A cross-check script
  (`GAP.md` trait names vs `CONVENTIONS.md`) reports only the expected naming
  difference (`interior 90 padding` = trait 4 `jump targets padded with 90`).
- Ledger unchanged: 187 rows — MATCH 32, RELOCS 130, PENDING 25.

## Round 93 — the three-unit duplicate group is now in the ledger, not in a lost round
Maintenance round. No new bytes, but round 92's analysis would otherwise have
evaporated, so it is recorded where a reader will find it.

- **Three `PENDING` rows added** for the duplicate group `3807:0004`, `380c:0000`,
  `3811:0004` (28 B each, byte-identical): `*p = HELP(*p)` through a far pointer
  built from a `seg`/`off` pair. The note names the exact cause (trait 3, split
  pointer load: original `8B 76 04` + `8E 46 06`, MSC `les`/`8E C1`) and the fact
  that one transcription would cover all three if the load were reachable. Ledger
  PENDING count 22 → 25 as a result.
- **All generators re-run** against the current ledger: `setters` 0, `wraps` 0
  generatable (33 skipped on `push cs`), `swapgen` 0 and correctly refusing to
  overwrite `cswap4.c`.
- **All derived docs regenerated** (`GAP.md`, `STATUS.md`, coverage) and the README
  figures synced to the tools' own output rather than hand-edited: 162 functions,
  MATCH 32 / RELOCS 130 / PENDING 25, 2646 bytes (0.902 %), ceiling 455 units /
  24 528 B.
- Ledger: 187 rows — MATCH 32, RELOCS 130, PENDING 25.

## Round 92 — no new rows; three duplicate units understood
No increment. The round pursued round 91's `register`→SI hypothesis on counter-driven
units and found one family that looked ideal but is blocked for a different reason.

- `3807:0004`, `380c:0000`, `3811:0004` are a **three-way duplicate group** (28 B
  each) doing `*p = HELP(*p)` through a far pointer built from a `seg`/`off` pair.
  They are blocked by **trait 3 (split pointer load)**, not by SI: the original loads
  the far parameter as `8B 76 04` + `8E 46 06` where MSC emits `les`. Tried three
  formulations (inlined `MK_FP`, local pointer, direct double evaluation); all give
  `8E C1` plus BX/DI, never the split load.
- The SI-counter hypothesis itself holds (round 91's `_six_calls`), but the remaining
  SI units hold *parameters* or *far-pointer bases* in SI rather than counters, so
  `register` does not apply to them. The trait-8 count of 196 units therefore stays
  an upper bound and that is stated in `CONVENTIONS.md`.
- Ledger unchanged: 184 rows — MATCH 32, RELOCS 130, PENDING 22. Verified rows total
  **2646 bytes across 162 rows (mean 16.3 B)** — a distribution worth remembering:
  this is a project of small functions.

## Round 91 — one RELOCS, and `register` turns out to be a real lever
- `4f89:0008` **_six_calls** (15 B, RELOCS, `src/calib/cloop2.c`) —
  `register int i; for (i = 0; i < 6; i++) HELP(i);`
  matches byte-for-byte: `56 / 33 F6 / 56 / E8 / 46 / 83 FE 06 / 7C F6 / 5E / CB`.
  **The `register` keyword is what puts the loop counter in SI**; without it MSC
  spills the counter to a frame and the shape is wrong.
- **This corrects trait 8's blanket claim.** `register` *does* steer a loop counter
  into SI, but a far-pointer temporary goes to DI instead (`cswap9` in the attic).
  So the SI trait is narrower than I wrote: it applies to far-pointer bases, not to
  counters. `CONVENTIONS.md` corrected.
- Two more attempts, both characterised:
  - `2a65:000c` (`memset` of a 512-byte table): `/Oi` makes `memset` intrinsic and
    gets very close — `57 / 33 C0 / rep stosb / 5F / CB` — but the original uses
    `rep stosw` with `cx=0x100` and sets CX before DI. `_wmemset` is out-of-line in
    this compiler, so the word fill is unreachable.
  - `37ef:000c` (flag clear): `register` puts the index in SI while the original has
    it in BX — and the original does **not** save SI at all (no `push si`), which no
    MSC convention does for a non-leaf helper.
- Ledger: 184 rows — MATCH 32, **RELOCS 130**, PENDING 22.

## Round 90 — HOWTO written and verified; README numbers regenerated
Consolidation round; no new bytes, but the project is now usable by someone else.

- **`docs/HOWTO.md`** — the missing piece. Six sections: prerequisites, checking the
  whole ledger, reproducing one row end-to-end, reading a signature out of the bytes
  (near/far, argument offsets, callee convention, which flags), an **eleven-item DIFF
  checklist** distilled from 90 rounds of real mismatches, how to add a row, the
  existing generators, and what is out of reach with the reason.
- **Every claim in it was executed, not assumed**: `match.py --selftest` (ok),
  `split.py --selftest` (ok), and the documented `PICK_PTR` reproduction run end to
  end (`build.py` → `omfdump.py` → `match.py` → `RELOCS`, size 44).
- **README figures regenerated from the tools** instead of memory — they had drifted
  again (149 → 161 functions, 2323 → 2631 bytes, 0.792 → 0.897 %). The README now
  points at `HOWTO.md` as the entry point and at `checkled.py` alongside `verify.py`.
- Ledger unchanged: 183 rows — MATCH 32, RELOCS 129, PENDING 22.

## Round 89 — the strictest filter, one survivor verified
- Built the hardest filter used so far: all nine trait patterns excluded **and** the
  unit must start with a real prologue (`55 8B EC`, `53`, `56`, `57`, `1E`, `06`).
  Survivors: **145** units out of 488 reachable — and most of those are the same
  families already characterised.
- `3d1a:0008` **ADD_200** (23 B, RELOCS, `src/calib/ccomb1.c`) —
  `HELP3(a + 0x200, b, c)`. The tell: the constant is applied with `80 C4 02`
  (`add ah,2`), which is what `+ 0x200` compiles to on a word.
- Two more tried and understood:
  - `439c:0006` / `439d:000e` (`HELP2(HELP1(a), b)`) differ only by `push si` — the
    **SI base-register trait** again.
  - `3556:000e` (`FIELD_AND`) differs by the `8E C2 / 8B D8` order, the same trap as
    the `3883` family.
- Ledger: 183 rows — MATCH 32, **RELOCS 129**, PENDING 22.

## Round 88 — no new rows; three more near-misses characterised
Third round without an increment. Everything tried is recorded so the next attempt
starts from truth rather than hope.

- **Unframed 12..20 B units (23 of them): almost all fragments.** My terminator
  filter is not enough — a fragment can end at a `ret` too. Discriminator: a real
  function never starts by *using* registers it has not set (e.g. `26 89 7C 0E`
  storing DI, or `or ah,2`), and never relies on AX being preloaded. `155e:000e`
  looked plausible until `80 CC 02` (`or ah,2`) showed it was the tail of something.
- `3e5c:0006` (`return g_1bc0 == 1;`) — the original tests with `or ax,ax / je /
  dec ax / je` (decrement-based), MSC 7 with `cmp [g],1 / jne`. Strength-reduction
  difference, not fixable from C.
- `4e8e:0098` **RELAY_GLOBALS** — `HELP6(g_995b, g_995c, g_9954, g_9956, g_9958, a)`
  is otherwise byte-exact but **MSC omits the `2A E4` that zeroes AH before pushing
  the first `unsigned char`**, under `/Os`, `/Ox /Oa /Os` and `/Ot` alike. The
  original zero-extends explicitly; MSC implicitly assumes AH is already clear. Two
  bytes, not steerable.
- Cleanup kept honest: two probing sources moved to `src/attic/`, `checkled.py`
  green again.
- Ledger unchanged: 182 rows — MATCH 32, RELOCS 128, PENDING 22.

## Round 87 — audited my own PENDING diagnoses; four were wrong or incomplete
No new rows. The round re-tested PENDING entries whose stated cause predated the
convention and frame-type tells, and **four diagnoses did not survive the audit**:

| Row | Old diagnosis | What the bytes actually show |
|---|---|---|
| `4fad:0006` CONV | "identical except …" | indexes with `03 DB` (`add bx,bx`) — **trait 1**, doubling |
| `352a:0004` reset_9b30 | "pascal, callee cleans up" | **two** traits: `C7 06 <g> 00 00` zero stores *and* a direct `9A` far call |
| `4527:000a` reset_9b30b | same | same two causes |
| `2603:ccda` NEG_MINUS1 | "original stages through DX" | true, **but** the same source *matches* at `418c:0266` (NEG1, memory-operand form) — so this unit was built differently or is not the same expression. Row also had the wrong size (16 → 15) and is **not a `units.csv` boundary** |

- **New trait 9, measured:** the original materialises zero explicitly
  (`B8 00 00`, `C7 06 <g> 00 00`) where MSC 7 always uses the xor idiom. Evidence:
  `473f:0036` — `return 0x43A30000L;` gives `33 C0 / BA A3 43` from MSC, the binary
  has `B8 00 00 / BA A3 43`. `tools/gap.py` now counts it: **106 units / 32 862 B**.
- Ceiling corrected again: `blocked by nothing` is now **457 units / 24 568 B**
  (was 468 / 25 867 last round, 495 / 27 062 two rounds ago).
- `checkled.py` caught my own leftover: after the failed experiment I had left
  `src/calib/clong2.c` unattested — it is now in `src/attic/` with a note.
- Ledger: 182 rows — MATCH 32, RELOCS 128, PENDING 22.

## Round 86 — no new rows; the `SI` trait measured and added to the table
- Sampled the **unframed** reachable units (22 with a call and a clean terminator).
  Two looked like real functions — `3a24:0006` `clear32` (zero a far struct field
  after a call) and `38ad:000e` `swap14` (swap a field of the struct returned by a
  call) — and both fail on the same thing: the original keeps the pointer in **SI**
  with `push si` / `mov si,ax` / `es:[si+N]` / `pop si`, while MSC 7 puts the offset
  in **BX** and saves nothing.
- Tried to force it: a `register int` local made MSC use **DI** instead, still not
  SI. So the trait is real and not steerable — recorded as **trait 8** in
  `docs/CONVENTIONS.md` with seven units as evidence.
- **`tools/gap.py` now measures it** (`push si; push [bp+x]` or `mov si,ax; es=dx`),
  which corrected the ceiling: **196 units / 26 435 B** were being counted as
  reachable. `blocked by nothing` drops from 495 units / 27 062 B to
  **468 units / 25 867 B** — the honest number is lower than last round's.
- Ledger unchanged: 182 rows — MATCH 32, RELOCS 128, PENDING 22.

## Round 85 — one 41-byte RELOCS from a relay call
- Enumerated sizes 32 (8 framed) and 42 (7 framed), calls first:
  - `23d7:0000` **BIG_CALL** (41 B, RELOCS, `src/calib/cs32.c`) —
    `HELP12(a,b,c,d,e, 0,0,0,0, 0x4F, 0x18F, f)`: six parameters relayed plus six
    constants. **`retf 12` fixes the argument count at six words**, which is how you
    know the constant run in the middle is literals rather than parameters — 12
    pushes against 6 arguments.
  - `3ea6:0008` SLOT_INDEX (32 B) stayed PENDING: the original loads the byte global
    (`A0 <disp>`) *before* the parameter, ours loads the parameter first — load
    order again, unchanged by `/Os` or `/Ox`.
  - `42ac:002c` and the size-42 group are the usual blocked shapes (`3ea6`-type
    arithmetic ordering, `1bfd`/`1c00` interrupt wrappers with `CD 21`,
    `37a8`/`37ab` far-field arithmetic).
- Ledger: 182 rows — MATCH 32, **RELOCS 128**, PENDING 22.

## Round 84 — three RELOCS; nested calls are the productive shape
- Enumerated the size-26 and size-28 classes (10 framed reachable units each).
  Size 28 yields nothing new — it is dominated by the blocked families
  (`3839`/`3898`/`39ed`/`3a66` use the `8B D8 / 8E C2` order, `2a28`/`2a29` the
  evaluation order, `2dce` a `rep stosw`). Size 26 gave three:
  - `4dae:0002` **NESTED4** (25 B) — `HELP2(HELP1(z, 0, x, y))`, four arguments to
    the inner call;
  - `4e6f:0006` **NESTED_PTR** and `4e71:0000` **NESTED_PTR2** (26 B each) —
    `SINK3(WHERE0(0), 0x1F, v & 0x7F)`, where the inner call's **far pointer result
    is pushed as two words** (`52 50` = `push dx; push ax`).
- All in `src/calib/cnest1.c`. **Nested calls are now the most reliable remaining
  shape**: they are pure composition, so the traits that block arithmetic
  (register choice, padding, load order) rarely get a chance to interfere.
- Ledger: 181 rows — MATCH 32, **RELOCS 127**, PENDING 22.

## Round 83 — best round in a while: seven RELOCS, two families enumerated
- Instead of guessing a shape, I measured: among the 488 reachable units, **size 24
  is the largest framed cluster (16 units)**, so I enumerated all 16 and found two
  families worth transcribing.
- **Chain family (4 units, all RELOCS)** — `call → read a field through the returned
  far pointer → call again`, `src/calib/cchain1.c`:
  `SINK(*(int __far *)((char __far *)WHERE(a) + N))` for N = 0x16, 0x04, 0x1A, 0x1C
  (`37fb:0006`, `382c:0002`, `3842:0008`, `3844:0000`).
  **This is the same semantic shape as the blocked `3883` family, and it matches** —
  because here the binary uses MSC's `8E C2 / 8B D8` order. So the order difference
  is contextual, not a blanket property of the compiler.
- **Three more from the same size class** (`src/calib/cmix2.c`):
  - `21fb:000e` **FIVE_ZEROS** (23 B) — `HELP5(a, 0, 0, 0, 0); return 0;`
  - `4e2d:0002` **DGROUP_CALL**, `4e2f:000e` **DGROUP_CALL2** (24 B each) —
    `HELP(&g, a, b, c)` with a `char` argument.
- **New diagnostic:** if every pushed offset is off by exactly **2**, the frame type
  is wrong — `C9 C2` is near pascal (arguments at `bp+4`) and `C9 CA` is far pascal
  (`bp+6`). Both candidates failed that way first (`orig 04 vs object 06`,
  `orig 08 vs object 0A`) and matched after switching to near.
- Ledger: 178 rows — MATCH 32, **RELOCS 124**, PENDING 22.

## Round 82 — repository consistency: attic split, new checkled tool
Maintenance round; no new verified bytes, but the tree is now self-consistent and
the bookkeeping is checked by a tool instead of by eye.

- **All generators re-run against the current ledger**: `setters.py` 0 units,
  `wraps.py` 0 generatable (33 skipped on the `push cs` form), `swapgen.py` 0 units —
  the mechanical families are genuinely exhausted, and `swapgen.py` correctly
  *refused* to overwrite `cswap4.c` (the round-59 guard working as intended).
- **19 unattested sources moved to `src/attic/`.** `src/calib/` had accumulated
  experiment files that no ledger row references; a reader could mistake them for
  verified work. They are kept (git history alone is a poor place to look for "what
  did we try") under a README that states they carry no claim of correctness and the
  rule for moving one back out. `src/calib/` now holds exactly the 60 files the
  ledger references.
- **New tool `tools/checkled.py`** checks the bookkeeping that `verify.py` cannot:
  unknown statuses, duplicate addresses, zero sizes, referenced-but-missing sources,
  and unattested files left in `src/calib/`. `verify.py` proves the bytes; this proves
  the ledger.
- README numbers refreshed (149 functions, 2323 / 293 211 B = 0.792 %, ceiling
  restated as ~27 KB blocked-by-nothing of which ~9.7 KB framed).
- Ledger unchanged: 171 rows — MATCH 32, RELOCS 117, PENDING 22.

## Round 81 — no new rows; a diagnostic insight and a 7-unit family still blocked
No ledger increment. Two results worth keeping.

- **New diagnostic: `pop bx` right after a call means the callee was declared
  cdecl.** In the `3883` family MSC emitted `E8 rel16 / 5B / …` because it was
  discarding the pushed argument itself; the original has no cleanup, so its callee
  **cleans the stack**, i.e. it is `__pascal`. Declaring the callee `__pascal` made
  three bytes of mismatch disappear — all my earlier attempts at this family had
  used the default (cdecl) convention. This applies to every generated wrapper: get
  the callee's convention from the stack cleanup, not from the caller.
- **The family still does not verify**, and the reason is narrow: after the call
  MSC emits `8E C2 / 8B D8` (`es = dx; bx = ax`), the original emits `8B D8 /
  8E C2` (`bx = ax; es = dx`). Two instructions, same values, opposite order — the
  instruction-order trait. Seven units (`3883:0008`, `3884:000e`, `38a2:000e`,
  `38ac:0008`, `396e:0004`, `39f3:0000`, `3839:0008`) are blocked by exactly this,
  and no source formulation changed it (tried: pointer arithmetic, struct member,
  `int __far *` and `char __far *` callee types, `/Os` and `/Ox /Oa /Os`).
- Also tried and blocked on load order: `3de8:0008` (far-field swap; the original
  reads the new value before the old field regardless of statement order) and
  `29e9:000a` (list walk; the original rotates the loop with `EB 03` instead of
  testing on entry).
- Ledger unchanged: 171 rows — MATCH 32, RELOCS 117, PENDING 22.

## Round 80 — one RELOCS from the selector family
- `1e3b:00f0` **PICK_FLAG** (29 B, RELOCS, `src/calib/cpick2.c`, `/G1 /AM /Gs /Os`) —
  `if (flag == 0) return g_pa; return g_pb;`, a two-way far-pointer selector.
  Useful contrast with round 79: here the parameter is compared **in memory**
  (`83 7E 06 00`), so `/Os` is the right flag, while `PICK_PTR` staged it in `BX`
  and needed `/Ox`. Which flag applies is visible in the bytes, not guessable.
- Scanned for the whole family (units with two or more far-pointer global loads):
  only **4 units** exist. The other three are `1e2f:0008` (already blocked on a
  `7C`/`7F` branch pair), `3d52:000a` (84 B, long global-vs-parameter chain) and
  `3074:000c`, which is a four-way selector — but it carries a `90` after **every**
  jump (`EB 22 90`, `EB 19 90`, …), i.e. the padding trait, so it is out of reach.
- Ledger: 171 rows — MATCH 32, **RELOCS 117**, PENDING 22.

## Round 79 — one 44-byte RELOCS
- `1f6f:000c` **PICK_PTR** (44 B, RELOCS, `src/calib/cpick1.c`, `/Ox /Oa /Os`) —
  a three-way far-pointer selector:
  `if (kind == 0) return g_a; if (kind == 2) return g_b; return g_c;`
  Two details pinned it down: each pointer is loaded as **`A1 <offset>` + `8B 16
  <segment>`** (the halves separately, not `les`), and the globals must be declared
  in *memory* order (0x46EC `a`, 0x46F0 `c`, 0x46F4 `b`) even though the source
  order is a, b, c.
- Two things kept failing for the documented reasons:
  - a two-global comparison (`3d91:0020`, `5026:013e`) — the branch polarity is
    always inverted relative to MSC's layout, and flipping the C condition just
    moves the mismatch to the other opcode (`7D`→`7C`→`7E`); it is the branch-block
    order trait;
  - `1fdd:0000` (two zero stores) — the original uses `C7 06 <g> 00 00`, MSC emits
    `33 C0 / A3 <g>`, the zero-store trait from rounds 25/26.
- Ledger: 170 rows — MATCH 32, **RELOCS 116**, PENDING 22.

## Round 78 — missed-split vein measured and empty; one RELOCS
- **Quantified round 77's lead and it is a dead end.** Scanning every unmatched
  unit for an internal return followed by a plausible prologue (`55 8B EC` or `6A`)
  finds **90 candidate starts**, but after requiring a complete inner function with
  no blocking trait, exactly **one** survives — the `4e8e:0070` already recorded.
  The other 89 hit the documented traits (mostly `push cs; call`, `9A`, or register
  arguments). So `units.csv` is **not** materially incomplete for reachable code,
  and the coverage denominator is trustworthy.
- `20b4:0004` **_spin_wait** (8 B, RELOCS, `src/calib/cspin1.c`) —
  `while (g_6e4 != 0) ;` compiles to `83 3E <g> 00 / 75 F9 / CB`. The loop
  **polarity names the condition**: `75` (`jne` back) means "wait while non-zero",
  `74` (`je` back) would be the opposite.
- Also confirmed: the unframed "clean" units in 8..48 B are almost entirely
  splitter fragments (tails starting mid-instruction with `8B`, `9B`, `89`), not
  functions — 179 of them, nearly all unusable as standalone rows.
- Ledger: 169 rows — MATCH 32, **RELOCS 115**, PENDING 22.

## Round 77 — a function that is not in the inventory
- `4e8e:0070` **_five_neg** (14 B, RELOCS, `src/calib/cfive1.c`) —
  `HELP5(-1, -1, -1, -1, -1)` to a near pascal callee.
  **It is not a unit boundary**: `units.csv` merges it with the 65-byte function
  before it, because `split.py`'s prologue set has no entry for a function that
  starts with `6A` (push imm8) after `C9 C2 0C 00` + one padding byte. The ledger
  row is therefore *finer than the inventory*.
- That is a new lead rather than a one-off: if the splitter misses functions that
  begin with `6A`/`1E`/`56`/`57`/`B8`/`A1` after a return, then some of the "one
  big unit" rows in `units.csv` contain two or three verifiable functions each.
  Quantifying that is the next step — it changes the denominator, not just the
  numerator.
- Also re-checked the candidate filter: excluding any unit containing `90` was too
  aggressive (`90` is a legitimate operand byte), so the "reachable" list used this
  round kept them. 156 framed candidates in 10..60 B, but most still hit the
  documented traits (interrupt wrappers, bare `5D` epilogue, `SI` registers).
- Ledger: 168 rows — MATCH 32, **RELOCS 114**, PENDING 22.

## Round 76 — the traits are now one table with evidence, in CONVENTIONS.md
No new verified bytes; this round makes the accumulated knowledge usable.

- `tools/gap.py` gained the **register-passed arguments** trait (`B4 imm` followed by
  `E8`), so `docs/GAP.md` now covers seven traits. Regenerated counts:
  padding 1400 u, `push cs` 1232 u, `9A` 881 u, split loads 367 u, `add r,r` 204 u,
  `8B E5 5D` 144 u, bare `5D` 74 u, **register args 12 u**, absolute ESA 6 u,
  and **498 units / 27 144 B blocked by nothing**.
- `docs/CONVENTIONS.md` now opens with a single **"Codegen traits"** table: each row
  gives the trait, the unit that isolates it as evidence, and its measured size.
  This replaces knowledge that was scattered across 40 rounds of PROGRESS entries —
  a reader can now see *why* each class is out of reach instead of inferring it.
- Recorded the three softer variants separately (branch-block order, operand
  evaluation order, register choice) because they block matches too but are not
  cleanly countable as patterns.
- README points at the table, so the ceiling is stated on the front page.
- Ledger unchanged: 167 rows — MATCH 32, RELOCS 113, PENDING 22.

## Round 75 — one RELOCS; the interrupt-wrapper family is out of reach
- `21f4:0000` **MUL_THEN_CALL** (23 B, RELOCS, `src/calib/cmul1.c`) —
  `return HELP(a, b, d * c);`. The operands must be **unsigned**: `F7 66` is `MUL`,
  and declaring them `int` makes MSC emit `F7 6E` (`IMUL`) — that single opcode was
  the whole difference. `F7 E1`/`F7 66` vs `F7 E9`/`F7 6E` is a cheap way to read
  signedness off the bytes.
- **The largest remaining cluster in the call-containing set is not reachable.**
  `1cb7`, `1cb9`, `1cba`, `1cbf`, `1cc2`, `1cc3` and their siblings set a register
  (`mov ah, 0x45` / `b4 0x0B`) and then `call` a helper — a DOS interrupt wrapper
  with **register-passed arguments**. There is no C construct in Microsoft C 7 that
  produces `mov ah,imm` before a call (its `__fastcall` uses BX/CX/DX, not AH), so
  this family needs inline assembly or a different compiler. Six units in 16..24 B,
  plus relatives above that size.
- Also confirmed unreachable: the `3883:0008` family (call → far pointer → field
  read) and the `1110:0002` trio (`push cs; call`).
- Ledger: 167 rows — MATCH 32, **RELOCS 113**, PENDING 22.

## Round 74 — four RELOCS; the call-wrapper vein extended
- Re-scanned **all sizes** for framed units whose only unusual feature is `E8`
  calls and no other blocking trait: **66 units**. From them, four more verified
  (`src/calib/cds1.c`, `/G1 /AM /Gs /Os`):
  - `4e2e:000a` **CALL_A** (20 B) and `4e31:0006` **CALL_B** (20 B) —
    `HELP(&g_2c82, a, b)`: a **DGROUP far pointer as the first argument**, pushed
    as `1E 68 <off>` (segment and offset pushed separately, not `push` of a
    pointer value);
  - `218c:0002` **TWO_CALLS** (18 B) — `HELP_A(-1); return HELP_B(a);`, first
    result discarded;
  - `39dc:0026` **SIX_ARGS** (27 B) — `HELP6(p0, p1, p2, p3, 1, p4)`, a constant
    argument in the middle of the push list.
- One family stays out of reach and is now understood: `3883:0008` and its five
  siblings (`call → far pointer → field read`) differ by a `pop bx` that MSC emits
  around the call plus a different `mov bx,ax` / `mov es,dx` order — a register
  allocation difference, not a wrong source.
- Ledger: 166 rows — MATCH 32, **RELOCS 112**, PENDING 22.

## Round 73 — three RELOCS from call-wrappers
- **New vein that the earlier filters missed: functions whose only "unknown" is a
  call target.** `match.py` masks relocation bytes, so a generated call to an
  external symbol compares clean against the original's `E8 rel16`. That makes the
  whole call-wrapper family harvestable, provided the *call form* is `E8` (not
  `push cs; call`).
- Verified (`src/calib/ccall1.c`, `/G1 /AM /Gs /Os`):
  - `3eb3:000a` **PLUS20** (16 B) — `return HELP_A(a) + 0x14;`, arithmetic on a
    call result;
  - `355a:000e` **NESTED** (17 B) — `return HELP_B(HELP_A(a));`, nested near calls
    with the first result pushed for the second;
  - `3725:0048` **CLEAR_BIT1** (20 B) — `*p &= ~1; HELP_V(); return 1;`.
- Only three framed units in 10..40 B have exactly one `E8` and no blocking trait,
  so this vein is small at that size; it should be re-scanned at larger sizes next.
- `GETBYTE_U` (zero-extended byte fetch) remains blocked: the original zeroes AH
  *before* the load (`2A E4 / 8A 87 …`), MSC 7 loads first then zeroes — an
  ordering difference, not a source error.
- Ledger: 162 rows — MATCH 32, **RELOCS 108**, PENDING 22.

## Round 72 — quantified gap analysis, and the README brought up to date
No new verified bytes; this round turns 70 rounds of near-misses into a measurement.

- New tool **`tools/gap.py`** classifies every unmatched unit against the eight
  codegen traits established since round 34 and writes **`docs/GAP.md`**. Over
  2365 unmatched units (290 897 B):
  | Trait | Units | Bytes |
  |---|---|---|
  | interior `90` padding | 1400 | 225 317 |
  | `push cs; call far` | 1232 | 180 177 |
  | direct far call (`9A`) | 881 | 183 276 |
  | split pointer load | 367 | 84 175 |
  | `add r,r` doubling | 204 | 66 762 |
  | epilogue `8B E5 5D` | 144 | 24 280 |
  | epilogue `5D` | 74 | 6 814 |
  | absolute ESA access | 6 | 17 323 |
  | **blocked by nothing** | **514** | **27 492** |
  | — of which framed | 185 | 9 744 |
- The rows overlap (traits co-occur), and the trait counts are **byte-pattern upper
  bounds** — a `90` can sit inside a displacement. So `blocked by nothing` is a
  *lower* bound on reachability. Both caveats are stated in the document.
- The number that matters: **9 744 bytes of framed code** are reachable by this
  toolchain — about 19 more rounds at the recent rate, assuming every attempt
  succeeds, which the last four rounds show it does not.
- **README corrected**: it still claimed 53 functions and 0.242 % coverage (stale
  since the 0.2 % era). Now 137 functions / MATCH 32 / RELOCS 105 / 22 PENDING,
  2067 of 293 211 bytes (0.705 %), with `docs/GAP.md` linked from the front page.
- Ledger unchanged: 159 rows — MATCH 32, RELOCS 105, PENDING 22.

## Round 71 — one MATCH from a branchless sweep; the vein is nearly dry
- Built a **branchless filter** (no conditional jumps, no calls, no blocking
  traits, 12..160 B) on the reasoning that padding and block-order cannot bite
  where there are no branches. It yields only **18 units** in the whole binary,
  which is itself the finding: nearly everything left has control flow.
- `37ad:000c` **SPAN8** (23 B, **MATCH**, `src/calib/cnb1.c`):
  `return ((p[2] - p[0]) << 3) + a;` for `int __far *p` in a near pascal frame —
  the pointer occupies `bp+6..9`, the int sits at `bp+4`.
- Of the other 17 branchless units, the misses are all previously named traits:
  the fixed-segment group (`2d62`, `2d64`, `2d84`, `2d86`, `2e4a`, `21f0`),
  `SI`-with-push/pop register choice (`37ef:000c`/`37ef:002a` flag set/clear on a
  stride-26 table — parameters and strides all correct, only the register
  differs), and one `rep stosw` loop (`4080:0008`) that MSC compiles as a frame
  with a counter instead.
- Ledger: 159 rows — **MATCH 32**, RELOCS 105, PENDING 22.

## Round 70 — no new verified bytes; jump-target padding is the fourth blocker
Reported plainly: **no ledger increment this round.** It went into the 65..128 B
band (only 34 units survive the reachability filter) and the one candidate worth
pursuing turned out to be blocked by a trait I can now name precisely.

- `2aa3:0002` VALIDATE3 (69 B) is a clean three-range validator
  (`a ∈ [-0x9AB,0x9AB]`, `b ∈ [0,0x175]`, `c ∈ [0x119,0x902]`, returning
  `-1/-2/-3/0`). I got the source *right*: with an if/else chain assigning to a
  result variable and `/Ox /Oa /Os`, the instruction stream matches including the
  shared epilogue — **except that the original has two `90` bytes** aligning the
  `mov ax,-2` and `mov ax,-1` blocks, and the branch displacements are 2 bytes
  longer as a result.
- `47ef:0008` (CLAMP_1_999, round 69) has exactly the same residual (`EB 03 90`
  vs `EB 02`). So this is **not** a one-off: the original compiler pads jump
  targets **even in size-optimised code**, while MSC 7's `/Os` does not, and its
  `/Ot` changes the block structure to early returns instead of just adding the
  nops. No flag combination gives "shared epilogue + padding".
- Second candidate, `4e9b:0008` (two stores returning a long), differs only in
  evaluation order: the original loads both arguments before storing
  (`8B 5E 06 / 8B 46 08 / 89 1E / A3`), MSC stores one at a time, and `/Ox`
  switches to `SI` with a save/restore.
- Ledger unchanged: 158 rows — MATCH 31, RELOCS 105, PENDING 22.

## Round 69 — one MATCH; the branch-block order is not steerable
Small round, reported as such: **1 new verified function** (`4a91:0002` KEEP_PTR,
27 B, **MATCH**) plus four candidates with fully understood misses.

- `4a91:0002` **KEEP_PTR** — `char __far *f(char __far *p) { if (!p) return 0; return p; }`.
  The null test is `or ax,bx` over **both words** of the far pointer, and the
  /Ox flag is required for the shape.
- Four near-misses, each one to three bytes apart, none a source error:
  - `489a:000a` SIGN_BAND — got `jl` right but MSC lays the blocks in the opposite
    order (`xor ax,ax` first vs `mov ax,1` first). Semantics identical.
  - `47ef:0008` CLAMP_1_999 — differs only in jump-target **padding** (`EB 03 90`
    vs `EB 02`); the original was built with padding enabled, /Os disables it.
  - `2a28:0000`/`2a29:000c` PICK_S/PICK_U — the signed/unsigned pair differs only
    in operand **evaluation order** (`mov dx,[bp+0A]` before `mov bx,[bp+08]`).
  - `2a28`'s twin is useful evidence though: the two units are identical apart
    from `7F`/`77` and `7D`/`73`, so one source with `int` and one with `unsigned`
    is confirmed correct even though neither matches.
- Ledger: 158 rows — **MATCH 31**, RELOCS 105, PENDING 22.

## Round 68 — MK_FP does not rescue the fixed-segment units; two more verified
- **Tested the hypothesis from round 67 and it failed, cleanly.** With
  `MK_FP(0x4827, …)` the compiler still emits `BB 27 48 / 8E C3` (segment via BX)
  and then addresses `es:[bx]` through a base register, while `2d64:0008` uses
  `B8 27 48 / 8E C0` and **absolute** `es:[62 08]`. So the earlier conclusion
  stands, now with a second attempt behind it: MSC 7 cannot address a far object
  by absolute `disp16`, and the whole fixed-segment family (`2d64:0008`,
  `2d7d:0042`, `2d86:0008`) stays out of reach. No more attempts on it.
- New verified (`src/calib/cmisc1.c`, `/G1 /AM /Gs /Os`):
  - `4977:0006` **CLEAR_AT** (20 B, **MATCH**) — `p[i + 5] = 0;` for a far char
    pointer with a near `int` index (`26 C6 40 05 00` = `es:[bx+si+5]`);
  - `2e01:001c` **MIX_LONG** (23 B, RELOCS) — **two statements** are required:
    `g &= 0x3FC0; g |= (v >> 16) & 0xC03F;` gives the memory-operand
    `81 26 <g> C0 3F`, whereas the one-expression form loads the global into a
    register first.
- Two more candidates stopped on register choice (`SI` vs `BX` with a save/restore
  the original needs and we do not).
- Ledger: 157 rows — **MATCH 30**, RELOCS 105, PENDING 22.

## Round 67 — padding-tolerant generators; three more verified; MK_FP identified
- Made `setters.py` and `wraps.py` **padding-tolerant** (prefix match, remaining
  bytes must be `00`/`90`), and made them record the *matched* length rather than
  the unit size. Re-running them found no new members — those families really are
  exhausted — but the tools are now correct for future re-runs.
- New verified (`src/calib/carr1.c`):
  - `4342:001c` **ADDR4** (18 B, RELOCS) — `return (char __far *)&g_866e[i * 2];`
    (array base in AX, DS in DX);
  - `4342:0004` **SEXT11** (23 B, RELOCS) — `(g_866e[i*2] << 5) >> 5`, i.e.
    `C1 E0 05 / C1 F8 05` sign-extends the low 11 bits;
  - `37a6:0016` **REC6** (17 B, **MATCH**) — `return MK_FP(0x4363, i * 0x1E + 6);`.
    The long-arithmetic form produced a spurious `cwd`; **`MK_FP` with a constant
    segment is the right way to express a fixed-segment far pointer**, giving
    `imul/add` plus `mov dx,0x4363`.
- `verify.py` caught my window error once more: REC6 was recorded at 18 bytes when
  the function is 17 (one padding byte). Third time this guard has paid for itself.
- Ledger: 155 rows — **MATCH 29**, RELOCS 104, PENDING 22.

## Round 66 — 10 more verified: the swap-and-return family was bigger than it looked
- **Templating caught seven hidden members.** The four `swap-and-return` units from
  round 65 looked like the whole family, but a template over *wildcard
  displacements* found **8 more**, seven of which were 20-byte units whose real
  function is 19 bytes plus a `00` padding byte. New tool `tools/swapgen.py`
  generates the whole family from the template and verified **8/8**
  (`375d:0008`, `37b3:00d0`, `3d51:0006`, `3e5b:0002`, `42ab:0006`, `48d6:011a`,
  `4dcc:000e`, `4df5:000e`) in `src/calib/cswap4.c`.
  One of them is the **near** variant — same source, argument at `bp+4`.
- Two more from an arithmetic batch (`src/calib/carith2.c`, `/Ox /Oa /Os`):
  - `47ea:000a` **CLAMP63** (20 B, **MATCH**) — `if (v > 0x63) v = 0x63; return v;`
  - `4384:000c` **MASKBYTE** (20 B, RELOCS) — `g_8670[i*4 + 1] & 0x7F`
- Four batch-mates stayed PENDING for the usual reason (DX staging of a store:
  original `89 16 <g>` vs our `A3 <g>`; and one ordering difference in a
  zero-extension). Not rewritten to look better.
- Ledger: 152 rows — **MATCH 28**, RELOCS 102, PENDING 22.

## Round 65 — best round so far: 8 verified functions, 150 bytes
The round-64 finding paid off immediately. Instead of guessing, I built a
**reachability filter**: exclude units containing any of the four blocking traits
(`add r,r` doubling, `push cs`/`9A` far calls, `8E 46` split far-pointer loads,
`8B E5 5D` epilogue). That leaves **127 framed candidates in 12..64 B** — a much
better hunting ground than the unfiltered band.

- New verified, `src/calib/creach1.c` (`/G1 /AM /Gs /Os`):
  - `418c:0266` **NEG1** (13 B, **MATCH**) — `return -1 - v;`, the memory-operand
    form MSC *does* emit (the contrast case to NEG_MINUS1);
  - `1dc0:0006` **PACK2** (13 B, **MATCH**) — `((long)b << 16) | (unsigned)a`,
    identified from the swapped halves `8B 46 08 / 8B 56 06`;
  - `3e97:0004` **STORE_AT1** (17 B, **MATCH**) — unaligned word store at pointer+1;
  - `30c7:0076` **STORE2** (19 B, RELOCS) — near pascal two-store setter.
- New family, `src/calib/cxchg1.c` (`/Ox /Oa /Os`): **swap-and-return**
  `int old = g; g = v; return old;` — the old value is staged in DX (`8B 16 <g>`),
  which only `/Ox` does. **Four members verified**: `3220:0006`, `34dc:0004`,
  `3f3c:0002`, `1e88:004a` (19 B each).
- Ledger: 142 rows — **MATCH 27**, RELOCS 93, PENDING 22.

## Round 64 — the `add bx,bx` anomaly is solved (it is not hand-written assembly)
No new verified bytes this round, but it closes the project's oldest open question.

- Clustered the 33..64 band (646 units) and filtered to **pure straight-line
  bodies** (no calls, no jumps): only 10 units. Two were transcribed.
- **`4e11:007e` WEIGHT2** (`return 2*(5*(abs(a)+1) + abs(b)) + c;`) matches under
  `/Ot /Oi` in **every instruction except the final doubling**: the original has
  `03 C0` (`add ax,ax`), MSC 7 emits `D1 E0` (`shl ax,1`).
  **This is the same instruction family as the `add bx,bx` (round 48 census, 74
  occurrences vs 18 `shl`)** that had been unexplained since round 34 and was
  tentatively attributed to hand-written assembly. It is not: it is this
  compiler's strength-reduction choice ("double with `add`"). The
  `CONVENTIONS.md` section has been corrected accordingly.
- Two new flag facts: **`abs()` is an intrinsic** (`/Oi` → `99 33 C2 2B C2`), and
  `/Ot` is required for the `*5` form `8B D0 C1 E0 02 03 C2` instead of `imul`.
- `43b0:0200`/`43d2:000a` (the duplicate pair) remain PENDING: the original loads
  the far pointer as `8B 5E 08` + `8E 46 0A` around the global stores, while MSC 7
  emits a single `les` — the split-load family again.
- Ledger: 134 rows — MATCH 24, RELOCS 88, PENDING 22.

## Round 63 — wrapper family automated; a 213-unit family identified as blocked
- Measured where the remaining mass is before choosing a target: small units
  (≤32 B) are only ~4.7 % of unmined bytes, the bulk is 65 B and up (85 %). Since
  function count still matters, the 17..32 band (467 units) was clustered by
  opening bytes — and **85 units share one shape**: thin wrappers
  `55 8B EC (push ...)+ (0E) E8 rel C9 CA/C2 imm`.
- New tool **`tools/wraps.py`** parses the push list (parameters and constants),
  generates the wrapper source and matches every member:
  **4/4 verified** — `23ee:0008` (46 B, 12 arguments), `256e:000a`, `257d:000a`,
  `39dc:000a` (27 B, six pushes including a zero constant).
- Two generator bugs fixed on the way: the parameter mapping was **reversed**
  (pascal puts the *first* declared parameter at the *highest* frame offset), and
  the call form had to be classified rather than assumed.
- **The important negative result:** the binary uses two far-call encodings.
  `E8` (near call) is generatable; `90 0E E8` (`push cs; call near`) is **not** —
  MSC 7 always emits `9A` for a far call, verified with a same-file far callee.
  **213 small units in the binary use the `push cs; call` form**, and 33 of the
  wrapper candidates had to be skipped because of it. Recorded rather than
  forced, and `wraps.py` now counts them so the gap is visible.
- Ledger: 133 rows — MATCH 24, **RELOCS 88**, PENDING 21.

## Round 62 — no coverage gain; the epilogue fingerprint isolated to one function
Reported plainly: this round added **no verified bytes**. It went into the 56..120
band (59 call-free framed units) and produced three near-misses, one of which is
the strongest single piece of toolchain evidence the project has.

- **`11d8:000c` SET4 (60 B): 58 of 60 bytes identical.** The body is byte-exact —
  three parameter stores plus `d & 0x7FFF` into a four-int struct, returning a far
  pointer to it. The only difference is the epilogue: original `8B E5 5D CB`
  (`mov sp,bp / pop bp / retf`), MSC 7 emits `C9 CB` (`leave / retf`) under /Os,
  /Ot, /Od and /Ox. For the first time the fingerprint is isolated to a function
  whose entire body matches, so the epilogue difference is not a side effect of
  some other mismatch.
- `1e38:0002` RECORD_CFG (56 B): every instruction matches except the **order of
  the first two** (original loads the global before the parameter). Scheduling
  difference only; `register` on the temporary did not change it.
- `465d:0000` UPD (60 B): struct update through a far pointer member at +4; the
  original keeps the struct offset in SI and the inner pointer in DI, MSC 7 uses
  BX with `les` and no save/restore — the register-choice family again.
- Ledger: 129 rows — MATCH 24, RELOCS 84, **PENDING 21**.

## Round 61 — sweep families exhausted; two stragglers, both MATCH
- Re-ran **all 14 families** under the round-60 convention fixes: every one now
  reports 0 hits at ledger-free unit boundaries, i.e. the mechanical families are
  genuinely exhausted, not mis-generated. That is a useful negative result — the
  remaining units are not formulaic single-statement bodies.
- A shape census for candidate new families found only two members:
  - `3ded:001c` **FIELD1** (14 B, MATCH) — `int __far __pascal f(int __far *p) { return p[1]; }`,
    the same accessor family as `3ded:000e`;
  - `37f9:000c` **IDENT** (10 B, MATCH) — `int __near __pascal f(int a) { return a; }`;
    the near frame places the argument at `bp+4`, which is what distinguishes it
    from the far variant.
- `verify.py` caught a size error of mine again: I recorded FIELD1 as 13 bytes,
  cutting the `retf 2` immediate (`… 02 C9 CA 04`), and the window check reported
  *"does not end at a return instruction"*. Real length 14; corrected and re-verified.
  This is the third time the ledger checks have caught a short window, which is
  exactly the failure mode that passes silently in a naive matcher.
- Ledger: 126 rows — **MATCH 24**, RELOCS 84, PENDING 18.

## Round 60 — three RELOCS; the sweeper itself was the bug
- Re-ran every `sweep.py` family against the split inventory: only `byte_store`
  still had a member (`1466:005b`, 6 B). Added two new families — `param_store`
  (`55 8B EC 8B 46 xx A3 <disp> C9 (CA|C2) imm16`) and `far_get` — and
  `param_store` yielded **2/2 verified** (`29f3:006e`, `3fcc:0022`, 13 B each).
- **Three bugs in `sweep.py` surfaced by writing the new families**, all in shared
  code that the earlier families happened to avoid:
  1. `far` was inferred from `CB` only, so `retf imm16` (`CA`) was treated as
     near — generated wrong conventions for every `C9 CA` unit;
  2. the recorded size stopped at the `ret` opcode, **excluding the imm16 bytes**
     of `CA`/`C2`, which made every window 2 bytes too short (the exact defect
     `verify.py` was hardened against in round 41 — the tool was producing it);
  3. the generated functions were declared without `__pascal`, so the epilogue was
     plain `retf` instead of `retf 2`; and pascal-uppercased symbols were then
     looked up in lowercase.
  All three fixed in the shared helpers, so every family benefits.
- Also repaired my own damage: a careless `str.replace` had duplicated a block
  into `sweep.py`; restored from git and redone with a targeted edit.
- Ledger: 124 rows — MATCH 22, **RELOCS 84**, PENDING 18.

## Round 59 — store-setter sweep automated: three RELOCS from one run
- New tool **`tools/setters.py`**: finds far-pascal store-setter units
  (`55 8B EC (8B 46 xx A3 <disp>)+ (C7 06 <disp> <imm>)? C9 CA/C2 imm16`),
  generates the C, builds once and matches every member. First run: **3/3
  verified** — `1ef8:0054` (13 B), `3bd6:003e` (13 B), `4c96:000e` (43 B, five
  parameter stores to 0x8600..0x8608 plus a `C7 06` initialiser).
  All three in `src/calib/cset6.c`.
- **Own mistake, and the fix that came out of it**: the generator was first named
  `cset5.c`, which **silently overwrote** the round-34 calibration source of the
  same name (OFF4/OFF6/OFF1/WRAP3/TEST80). `verify` caught it immediately
  (`BUILD FAILED … source missing`), the file was restored from git, and
  `setters.py` now refuses to write a file the ledger references. Lesson: any
  generator must check name collisions against the ledger before writing.
- Ledger: 121 rows — MATCH 22, **RELOCS 81**, PENDING 18.

## Round 58 — one MATCH from the band, two near-misses at a single byte
- `1e14:0008` **KIND_OF** (32 B, **MATCH**, `src/calib/csm1.c`, `/Ox /Oa /Os`):
  `int __far __pascal f(unsigned v) { if (v == 0) return 0; return (v > 0xFF) ? 2 : 1; }`
  The value is staged in DX (`8B 56 06 / 0B D2`) and the compare is unsigned
  (`76` = `jbe`) — the signed/unsigned choice is visible in the branch opcode.
- Two candidates stopped one byte short, both worth recording because the
  remaining difference is not a source mistake:
  - `50b1:0008` CMP3 (33 B): original is `cmp bx,dx / jge +4` returning 1;
    MSC 7 emits `jg`/`jle` for every formulation tried (`a >= b`, `!(a < b)`,
    `a < b ? 0 : 1`, early returns with both polarities). One opcode apart.
  - `2ad2:0006` LOAD_LONG (33 B): original is `... EB 04 90 / 33 C0 99`; ours is
    `EB 03 / 33 C0 99` — the original carries one more padding byte before the
    zero-return block, the same jump-target alignment seen in round 39.
- Ledger: 118 rows — **MATCH 22**, RELOCS 78, PENDING 18.

## Round 57 — toolchain thread closed as blocked; one more RELOCS
- **Toolchain decision, with evidence.** MSC 5.1 cannot be tested in this setup and
  the loop is now closed rather than left open:
  - every compiler binary in that set is EXEPACK-packed (so the passes are no
    workaround either);
  - `Z:\LOADFIX` does **not exist** in this DOSBox-x build (verified: it answers
    `Bad command or filename`), so the packed image cannot be relocated;
  - DOSBox 0.74 does not rescue it either — a packed-driver compile there produces
    no output at all.
  Remaining option would be writing an EXEPACK unpacker; not worth more rounds
  given the matching yield elsewhere. The `add bx,bx` / `5D`-epilogue / split-load
  questions stay documented as **open with evidence**, which is the honest state.
- `1e35:000c` **CALL4** (38 B, RELOCS, `src/calib/ccb2.c`) — third member of the
  callback family and the most informative: the guard is the same
  `A1 seg / 0B 06 off` null test, but the callback is invoked with its arguments
  **permuted** (`g_cb(c, d, b, a)`; push order `[bp+6] [bp+4] [bp+8] [bp+0xA]`)
  and the result is written back into the **first parameter slot** (`89 46 0A`)
  before being returned. Reading the push order is what exposed it.
- Ledger: 117 rows — MATCH 21, **RELOCS 78**, PENDING 18.

## Round 56 — MSC 5.1 blocked by EXEPACK; one documented near-miss
- **No new verified row.** The round went into the toolchain question and into one
  candidate; both are reported as they came out.
- MSC 5.1: every compiler binary in that set (`C1`, `C1L`, `C2`, `C3`, `CL`) is
  **EXEPACK-packed**, so bypassing the driver and calling the passes directly is
  not possible either — they all hit `Packed file is corrupt` under DOSBox-x.
  Only `QC.EXE` (QuickC) and a few utilities are plain, and QuickC is a different
  code generator. `Z:\LOADFIX` is not available in this DOSBox-x build (probing
  the Z: drive hangs), so the packed driver cannot be relocated. Consequence: a
  **PE/EXEPACK unpacker** is the prerequisite for testing MSC 5.1 codegen; that
  is bounded work but was not started this round.
- `29ed:0004` **PUT_BE** (35 B) added as PENDING with its diagnosis: it writes a
  big-endian word then a zero byte and returns `p+2`. The original stores the high
  byte straight from **AH** (`26 88 27`) and advances with `83 C3 02`; MSC 7
  copies AH to AL (`8A C4 / 26 88 07`) and uses `8D 47 02`. Body semantics match,
  byte-selection does not — the third unit in the split-load/byte-selection
  family, alongside `1df5:0008` and `2aa3:0048`.
- Ledger: 116 rows — MATCH 21, RELOCS 77, PENDING 18.

## Round 55 — MSC 5.1 obtained (DOS-native), one RELOCS, one new near-miss
- **MSC 5.1 acquired** from the decompme compiler archive
  (`compiler-microsoft-microsoft-c-5.1-dos`, SHA1 checked). Unlike the 6.00ax set,
  its `CL.EXE` is a **real-mode DOS binary** (no PE stub) and it *did* compile a
  probe successfully.
  **But it is not usable yet**: `CL.EXE` is **EXEPACK-packed**, and DOSBox-x
  reports `Packed file is corrupt` on most runs (only the first, smallest probe
  got through). `Z:\LOADFIX` did not change that; the log file is not even created
  when it trips, which is why the failures look like "the shell never ran".
  Next step would be an EXEPACK unpacker (or driving `C1`/`C2`/`C3` directly),
  so the `add bx,bx` / `5D`-epilogue questions remain **open**.
- `4e8e:0008` **STORE5** (37 B, RELOCS, `src/calib/cstor2.c`) — five arguments
  stored to 0x2D02..0x2D0A, source order equals store order (second confirmation
  of the rule from `STORE4`).
- `2aa3:0048` **ZERO_Z** (38 B) added as PENDING: it zeroes six struct words in the
  order +6, +0, +8, +2, +0xA, +4. The original loads the far pointer as **two
  words** (`8B 5E 06` + `8E 46 08`) and keeps AX=0; MSC 7 emits `les bx` and
  alternates AX/CX. That is the **second** unit showing split pointer loading
  (`1df5:0008` skip-whitespace was the first), so the pattern is now real
  evidence rather than one observation.
- Ledger: 115 rows — **MATCH 21**, RELOCS 77, PENDING 17.

## Round 54 — callback-through-struct MATCH on the first attempt
- `4665:0004` **CB_STRUCT** (32 B, **MATCH**, `src/calib/ccb1.c`, `/G1 /AM /Gs /Os`):
  ```c
  struct S { char pad[0x10]; void (__far __pascal *fn)(struct S __far *, int, int); };
  void __near __pascal cb_struct(struct S __far *s, int a, int b)
  { if (s->fn) s->fn(s, a, b); }
  ```
  `retn 8` plus pascal push order pinned the signature down (`s` is the first
  declared parameter), and the round-53 pointer-null idiom made the guard
  predictable. Byte-identical, no relocation to mask.
- `4737:0002` **SLOT_PTR** (32 B) added as PENDING with its diagnosis: the
  semantics are `i = (v < 0 || v > 0xF) ? 0xF : v;` returning a far pointer
  `0x43A3:(i * 0x21F)`. The original keeps `i` in **BX** and lays the guard out as
  `or bx,bx / jl +5 / cmp bx,0x10 / jl +3 / mov bx,0xF`; MSC 7 uses `DX` with
  different block bodies (`jl +9`) at `/Os`, `/Ox` and `/Ox /Oa /Os`. Body
  verified, layout not — recorded rather than forced.
- `tools/twins.py`: no new twins.
- Ledger: 113 rows — **MATCH 21**, RELOCS 76, PENDING 16.

## Round 53 — CALL_CB (RELOCS) and TWOBITS (MATCH) from the 30..64 band
- `39eb:000a` **CALL_CB** (29 B, RELOCS, `src/calib/cind1.c`, `/G1 /AM /Gs /Os`):
  `void __near __pascal f(int a, int b, int c) { if (g_cb) g_cb(a, b, c); }` —
  the null test on a **far function pointer is `mov ax,[seg]; or ax,[off]`**, and
  the call is `FF 1E <disp>` (far indirect through a DGROUP pointer).
- `49dd:0000` **TWOBITS** (30 B, **MATCH**, `src/calib/cbits1.c`, `/Ox /Oa /Os`):
  `r = (*p == 0); r |= (p[2] == 0) ? 2 : 0;`
  The original's `sbb cx,cx / and cx,2` is MSC's idiom for a ternary producing
  `N` or `0` — writing `<< 1` instead produces `neg cx / shl cx,1` and misses by
  three bytes. This is a genuinely new codegen idiom, not a flag tweak.
- Two more near-misses diagnosed rather than forced:
  - `2d64:0008` (fixed segment 0x4827): the original addresses
    `es:[<disp16>]` directly, MSC splits the constant into `mov bx,0x4827 /
    mov es,bx / mov bx,0x862`, so absolute ESA addressing is out of reach from C;
  - `4665:0004` and the `43b0:0200` duplicate pair need struct-plus-callback
    forms that the decompiler does not recover cleanly yet.
- `tools/twins.py` after the batch: 0 new twins.
- Ledger: 111 rows — **MATCH 20**, RELOCS 76, PENDING 15.

## Round 52 — two more rows (STORE4 RELOCS, XOR_AND twin), allocator lever tried on PENDINGs
- `37b3:0004` **STORE4** (31 B, RELOCS, `src/calib/cstor1.c`) —
  `void __far __pascal f(int a,int b,int c,int d) { g_13fa=a; g_13fc=b; g_13fe=c; g_1400=d; }`.
  Useful confirmation: with pascal calling order the store order in the code is
  the **source** order (`a` first at `[bp+0xC]`), so a four-store setter can be
  read straight off the bytes.
- `3ae5:000a` **XOR_AND** — an unrecorded twin of `3b1b:0002`, found by
  `tools/twins.py` right after the batch. The tool is now part of the routine.
- The **"dummy local steers allocation"** lever was tried on the three big
  PENDINGs and did not move them:
  - `NEG_MINUS1`: `/Os` gives `ENTER 2` + CX, `/Ox /Oa /Os` gives a memory operand;
    the original is frameless *and* stages in DX, which is neither.
  - `get_39f8_clamped`: `/Ox /Os` gives two `ret`s, `/Ox /Oa /Os` gives a BX-based
    merge, `/Os /Oa` a frame. The original merges through **AX** with two memory
    reads — no combination reached.
  - `4b23:000c` STORE_IF (31 B) is a new near-miss of the same kind: the original
    stages the first value in DX (`8B 56 08 / 83 FA FF / 74 04 / 89 16 ..`), ours
    compares the memory operand directly.
- Ledger: 109 rows — **MATCH 19**, RELOCS 75, PENDING 15.

## Round 51 — three MATCHes: one twin plus two far-pointer ALU forms
- **`tools/twins.py`** added: for every MATCH/RELOCS row it searches the image for
  the same byte sequence at an unrecorded unit start. Result: **one twin**
  (`3aec:0000` = `35ca:5550` TEST_AND), now its own ledger row.
- New MATCHes:
  - `37b0:000a` SUB_P2_ADD (20 B, `src/calib/cfar2.c`) — `return (*p - p[2]) + a;`
    reproduces `26 8B 07` / `26 2B 47 04` / `03 46 06` exactly;
  - `3b1b:0002` XOR_AND (21 B, `src/calib/cfar3.c`) — `*p ^= mask; return mask & *p;`.
    This one needed a **copy of the mask through a local** (`int m = mask;`) plus
    `/Ox /Oa /Os`: only then does the allocator stage it in `BX`
    (`8B 5E 06 / 8B C3`) as the original does. Adding a trivial local to steer
    register allocation is a new, reusable trick.
- `1e1e:0046` (put-a-word) and `1df5:0008` (skip-whitespace) remain unmatched:
  both keep the far pointer in `BX:ES` and never write the parameter back, which
  MSC 7 does not do at any tested level. Recorded with that diagnosis.
- Ledger: 107 rows — **MATCH 18**, RELOCS 74, PENDING 15.

## Round 50 — duplicate scan bug fixed, three MATCHes (two of them duplicates)
- **Correction to round 49.** The claim "no copy-paste duplicates in own code" was
  wrong: the scanner tested `b[-2]` for the `retf imm16` opcode, but it sits at
  `b[-3]`, so **every `CA`-terminated function was skipped** — which is most of
  them. `tools/dups.py` now has the corrected terminator test and is a kept tool,
  not a scratch script.
- Real duplicate groups among unmatched units: **4**, of which 3 are game code
  (`1df5:0008`/`1dfc:0066`, `1e1e:0046`/`1e1e:0068`, `43b0:0200`/`43d2:000a`) and
  one is CRT. Two further duplicates were hiding as unrelated candidates:
  `3b16:0030` = `35ca:5198` (OR_MASK) and `3b1a:0000` = `35ca:51a8` (ANDNOT_MASK).
- New verified rows, all **MATCH**:
  - `3ded:000e` DEREF_WORD (13 B, `src/calib/cderf1.c`) — `int __far __pascal f(int __far *p) { return *p; }`;
  - `3b16:0030` OR_MASK and `3b1a:0000` ANDNOT_MASK (duplicates, reuse `cunit6.c`).
- The two duplicate groups that are *not* yet transcribed (`1e1e:0046` put-a-word,
  `1df5:0008` skip-whitespace) resist for an interesting reason: the original
  keeps the far pointer in `BX:ES` and never writes it back, while MSC 7 either
  increments the parameter in memory or spills an 8-byte frame. The plain
  formulations are documented in the round; the shape looks like the same
  second-generation codegen as the `5D` epilogue.
- Ledger: 104 rows — **MATCH 15**, RELOCS 74, PENDING 15.

## Round 49 — one RELOCS; duplicate-function idea measured as exhausted
- `35ca:804e` `@exch_zero` (16 B, `src/calib/cexch1.c`, `/G1 /AM /Gs /Ox`):
  `old = g_78ca; g_78ca = v; g_78cc = 0; return old;` — the exchange family with a
  following initialiser. `/Ox` is required for the DX temporary (a `/Os` build
  uses CX). The unit also appears as `3dce:000e` (same linear address).
- Swept that family over all units: **one member**, the one above.
- **Tested a higher-yield idea and measured it as empty**: byte-identical
  duplicated functions would let one transcription verify several addresses.
  Among unmatched units there is exactly **one** duplicate pair
  (`1131:000c` / `11c3:000a`, 72 B) and it is CRT code, not game code. So the
  binary contains no copy-paste duplicates in the own-code region; every match
  really is a separate transcription.
- Ledger: 101 rows — MATCH 12, **RELOCS 74**, PENDING 15.

## Round 48 — three functions verified (2 MATCH), second-compiler fingerprint found
- `src/calib/cunit6.c` (`/G1 /AM /Gs /Os`), three new rows:
  - `35ca:5198` **OR_MASK** (16 B) — `*p |= mask;` through a far pointer, MATCH;
  - `35ca:51a8` **ANDNOT_MASK** (18 B) — `*p &= ~mask;`, MATCH;
  - `2603:c476` **count_up** (18 B, RELOCS) — `if (g_1cf0 > 0) g_1cf2++;` where the
    counter is a `long`: `83 06 .. 01` + `83 16 .. 00` (add/adc pair).
- **Phase-0 evidence**: counted epilogue styles in the image — 1 754 `C9` (leave),
  230 `5D` (pop bp), 156 `8B E5 5D`. MSC 7 never emits the latter two at any tested
  level, so those units come from a **second compiler generation** or hand-written
  assembly. Recorded in CONVENTIONS.md; this replaces guesswork about the
  remaining toolchain question with a measurable fingerprint.
- `1000:1364` (abs) stays PENDING with that diagnosis: the body matches exactly
  (`99 / 33 C2 / 2B C2` from `(v < 0) ? -v : v`), only the epilogue byte differs.
  `abs()` itself is a library call in MSC 7, not an intrinsic.
- The two biggest PENDINGs resisted again with the new flags: `SLOT_FILL` gives
  ENTER 8 (original ENTER 2) or no local at all, and the 32-bit exchanges spill
  the low word where the original keeps it in BX — both are allocator decisions
  that no flag combination reached.
- Ledger: 100 rows — **MATCH 12**, RELOCS 73, PENDING 15.

## Round 47 — MSC 6 dead end confirmed, one more RELOCS from a hidden unit
- Closed the last open question about the MSC 6 set: it is **not** a DPMI issue.
  Loading HDPMI32 before the driver (it is labelled "DOS-extended") produces the
  same "This program cannot be run in DOS mode" message, so that archive.org set
  really ships a Windows PE driver. Recorded in `docs/CONVENTIONS.md`; finding a
  DOS-hosted MSC 6 stays the open prerequisite for the `add bx,bx` question.
- One new **RELOCS**: `20b4:014c` `calc_f3e` (19 B, `src/calib/cunit5.c`) —
  `return (unsigned long)100 * g_f3e + g_f3d;` reproduces
  `B8 64 00 / F7 26 <disp> / 8A 0E <disp> / 2A ED / 03 C1 / 83 D2 00 / CB`
  exactly: `mul word [disp]` for the 16x16 -> DX:AX product, then the byte is
  zero-extended and added with `adc dx,0`. Scanned for siblings of this shape:
  it is the only one in the binary.
- `1466:0052` (`push bp / xor ax,ax / mov sp,bp / pop bp / retf`) stays unmatched:
  a plain `return 0;` compiles frameless (`33 C0 CB`), so that unit uses a frame
  for a reason the source does not show.
- Ledger: 96 rows — MATCH 10, **RELOCS 72**, PENDING 14.

## Round 46 — PENDING cascade gave nothing; an earlier conclusion turned out void
- Ran every PENDING source source against the new `/Ox /Oa /Os` flag set
  (`NEG_MINUS1`, `IDX_142A`, both `SWAP_LONG`, `SET_BIT`, `W_COND`,
  `get_39f8_clamped`, `RESET_9B30`, `CONV`): **no new match**. `CONV` and
  `IDX_142A` still emit `D1 E3` where the original has `03 DB`, so the
  "add bx,bx" question is untouched by the aliasing flag. One further source
  variant for the slot allocator (if/else with a local) was tried with
  `/Ox /Oa /Os` and `/Os /Oa` — no match; the original merges both branches into
  one `retn` via `jmp`, which MSC 7 does not produce here.
- **MSC 6 test invalidated, record corrected**: while retrying MSC 6 with the new
  flags, every build failed. Cause: the archive.org 6.00ax set ships a **Windows
  PE driver** (`CL.EXE` has the "This program cannot be run in DOS mode" stub;
  only `C1`, `C1L`, `C2`, `LIB`, `QCC` are real-mode DOS). Worse, the failures had
  gone unnoticed because `build.py` left the previous OBJ in place, so the
  round-26 comparison actually measured **MSC 7 against MSC 7**.
  `docs/CONVENTIONS.md` and `README.md` now say MSC 6 is **untested / open**,
  not "disproved". The stale-object guard from round 45 is what exposed this.
- No ledger change this round: 95 rows — MATCH 10, RELOCS 71, PENDING 14.
  Coverage stays 897 / 293 211 (0.306 %). A round without an increment is
  reported as such; the value here is that two wrong claims are no longer in the
  documentation.

## Round 45 — the missing flag combination `/Ox /Oa /Os` closes a round-23 PENDING
- **Root cause of a 22-round-old PENDING found**: the clamp family needs
  `/G1 /AM /Gs /Ox /Oa /Os`. `/Oa` (assume no aliasing) is what makes MSC keep the
  global in `DX` instead of re-reading it (`8B 16 <disp>` instead of
  `3B 06 <disp>` / `A1 <disp>`); `/Os` (after `/Ox`) is what removes the
  jump-target padding. Round 23 tested every optimization level but no aliasing
  flag, and round 39 blamed the extra `90` on link-time alignment — that was
  wrong, it is `/Os`.
- Both clamp copies are now **RELOCS** (`src/calib/cclamp3.c`, 20 B each):
  `1f2d:000e` for g_4688 and `1f2f:0002` for g_468A —
  `if (v < 1) return 1; if (v > g) return g; return v;`
- **Two tooling bugs found while chasing it**:
  - `build.py` never deleted the previous OBJ, so a failed compile reported
    "OK" with a stale object. It now removes OBJ/stamp/log first. This is why an
    earlier source edit appeared to have no effect.
  - a comment containing `**/G1` ends the block comment early (`*/`), which broke
    the compile silently. Avoid `*/` sequences in prose.
- **Splitter false positive fixed**: an early `return` looks exactly like a unit
  boundary (terminator + prologue). `split_entry` now skips a cut when a short
  jump inside the current block targets it. 31 bogus splits disappeared
  (2 554 -> 2 523 units) and `1f2d:000e` is one 20-byte function again, added as a
  fifth self-test case.
- Ledger: 95 rows — MATCH 10, **RELOCS 71**, PENDING 14; coverage **897 /
  293 211 own bytes (0.306 %)**.

## Round 44 — prologue measurement, widened splitter (598 hidden), 4 new RELOCS
- Rather than guessing which prologues the splitter still misses, each candidate
  opcode was **measured** (how many boundaries it would add, plus surrounding
  bytes). Accepted: `8B 16`, `8B 0E`, `8B 36`, `8B 3E`, `8B 1E`, `A3`, `A2`,
  `80 0E`, `26 89`. Rejected with reason: `31` (xor) — it fires mid-function
  (`31 46 FE` = `xor [bp-2],ax`). Hidden units: 561 -> **598**.
- `tools/sweep.py` now works on `ground_truth/units.csv` (with the old
  `functions.csv` fallback) and gained five frameless families: `word_get`,
  `byte_get`, `word_set`, `inc_get`, `dec_get`. Two of the tool's own bugs were
  found by using it: a non-ASCII em-dash in the generated header, and a 9-character
  object stem that MSC-CL rejects (`sw_wordge` -> `swwordge`).
- New RELOCS (8 bytes total, all 4-byte forms):
  - `1534:02aa` `@set_near_a4` and `25f0:013a` `@set_far_409e` — fastcall store
    setters (`A3 <disp> C3` / `A3 <disp> CB`); the near one needs an explicit
    `__near` because the medium model defaults to far;
  - `159d:007b` and `1ee7:0028` — word getters, generated by `tools/sweep.py`.
- The 4-byte class is now **exhausted**: a dedicated sweep found only the two
  setters above (`get: 0`, `set: 2` after excluding the ledger).
- Observation for later: the CLAMP family (PENDING since round 23) reappears at
  two further addresses as the same 11-byte shape
  (`8B 16 <g> / 3B C2 / 7E 02 / 8B C2`), so it is a genuine four-copy idiom and
  not a one-off.
- Ledger: 95 rows — MATCH 10, **RELOCS 69**, PENDING 16; coverage **857 /
  293 206 own bytes (0.292 %)**.

## Round 43 — splitter widened: 561 hidden units, 15 new RELOCS in one batch
- `tools/split.py` now also splits on **bare `CB`/`C3` terminators** followed by
  frameless prologues (`FF 06`, `FF 0E`, `FF 36`, `C7 06`, `C6 06`, `89 06`,
  `B8 ..`). Hidden units: 507 -> **561**; a fourth regression case
  (`3e24:006c`, host splits into 95 + 4 + 8 + 8) was added to `--selftest`.
  The self-test immediately caught a wrong expectation of mine (4 units, not 3,
  because the address sits inside a larger entry).
- Harvest from the widened rule, all in `src/calib/cunit3.c`
  (`/G1 /AM /Gs /Os`), **15 new RELOCS**:
  - **11 word getters** `A1 <disp> CB` (4 B each);
  - **3 initialisers** `C7 06 <disp> <imm> CB` (7 B each);
  - **1 near `return -1`** (`B8 FF FF C3`, 4 B).
- Two pitfalls worth recording: `void __far f(void)` keeps the C symbol
  `_f_…` (no pascal uppercasing), and the ledger rows for a generated batch are
  best written by script — hand-copying 16 rows is where typos would creep in.
- `473f:0036` stays PENDING: it returns the long `0x43A30000` and the original
  materialises the low word with `B8 00 00`, while MSC 7 always folds it to
  `33 C0` (xor) at `/Os`, `/Ot`, `/Ox`; the far-pointer formulation gives the
  same xor.
- Ledger: 91 rows — MATCH 10, **RELOCS 65**, PENDING 16; coverage **841 /
  293 206 own bytes (0.287 %)**.

## Round 42 — metric switched to units, 3 more RELOCS from fused frameless units
- `tools/coverage.py` now measures against `ground_truth/units.csv` when it
  exists (fallback to `functions.csv` kept, both paths tested). The denominator
  changes honestly: **2 463 functions, 294 182 code bytes** instead of 1 956 /
  294 603 — the difference is the 421 gap bytes that are not code plus the
  functions that were invisible.
- Mined hidden units in the 18..40 band. Found that `3e24:006c` is really **three**
  frameless units fused together (`A1 .. CB` / `FF 06 .. A1 .. CB` /
  `FF 0E .. A1 .. CB`). All three RELOCS in `src/calib/cunit2.c`.
  **Known gap in `split.py`**: it only accepts `C9`-prefixed terminators or
  prologues beginning with `55 8B EC`/`C8`/`A1`/`A0`, so bare-`CB` frameless
  sequences stay fused. Widening the rule is the next tooling task.
- `20b4:0160` (37 B) is a hand-rolled 24-bit packer with no runtime calls
  (`A0`/`2B D2`/`8A E0`/`2A C0` … `13 D2` carry handling). Writing the obvious
  `v = (v << 8) + g;` chain pulls in the 32-bit shift helper, so the source form
  is still open — documented as PENDING instead of approximated.
- Ledger: 75 rows — MATCH 10, **RELOCS 50**, PENDING 15; coverage **752 /
  293 219 own bytes (0.256 %)**.

## Round 41 — inventory split into units (2 463), six wrong windows fixed, 4 new RELOCS
- **`tools/split.py`** added with a `--selftest`: recovers the functions the
  decompiler merged into bigger entries. Result: **2 463 units from 1 956
  inventory entries — 507 hidden functions recovered** (lower bound; the rule is
  conservative). Self-test asserts the three known blobs
  (`31e3:000c` → 5 units, `458e:705a` → 3, `458e:8642` → 3).
- **A real defect in my own ledger, found by the new self-test**: three rows
  recorded windows that were one byte too SHORT (`458e:8642` 12 instead of 13,
  `458e:8650` 24 instead of 25, `35ca:1e7e` 22 instead of 21) and three that
  included a padding byte. Narrowing a comparison always passes, which is why
  `verify` had been green. All six are corrected and still verify.
- **`tools/verify.py` now rejects both window errors**: every window must end at
  a `ret`/`retf`/`retf imm16` instruction, and trailing `90` padding inside the
  window is reported as "real length is N". The check found all six rows
  automatically, so this class cannot return silently.
- `tools/mine.py --units` mines `ground_truth/units.csv`, i.e. the functions that
  were invisible before. First harvest: **4 new RELOCS** in `src/calib/cunit1.c`
  — two long getters (`2e01:0014`, `4a91:001e`), a 14-bit sign extension
  (`477b:0028`, `shl ax,2 / sar ax,2`) and a copy-plus-reset (`3eec:0058`).
- Ledger: 71 rows — MATCH 10, **RELOCS 47**, PENDING 14; coverage **752 /
  293 640 (0.256 %)**.

## Round 40 — close-out: clean rebuild green, 53 functions verified
- Wiped `build/` completely and re-ran `tools/verify.py`: **21 objects rebuilt from
  source, 67 ledger rows re-checked, exit 0, 47.7 s**. Nothing in this report
  depends on a stale object file.
- Final state: **MATCH 10, RELOCS 43, PENDING 14**; **711 / 293 640 own code bytes
  verified (0.242 %)**; 12 211 B of the image are data, 963 B foreign CRT.
- README rewritten: stale figures (12 functions / 0.022 %) replaced, and a
  "what is proven, and what is not" section added so the state cannot be
  misread as a finished decompilation.
- Open list re-ordered by importance; the inventory undercount (461 hidden units)
  is now item 1 because every coverage number depends on it.
- Tooling as of close-out: `build.py` (cached compiler driver), `verify.py`
  (rebuild + ledger recheck), `omfdump.py`, `match.py`, `coverage.py`,
  `report.py`, `mine.py`, `sweep.py`, `markcrt.py`, `gt.py`, `disasm.py`.

## Round 39 — merged blobs quantified: 461 hidden functions (53 verified)
- Built a detector for merged inventory entries (terminator + gap + new
  prologue) and measured the structural damage: **189 inventory entries hide at
  least two real functions, 461 units in total**. The inventory's 1,956 entries
  therefore represent roughly 2,230 real functions. This is the single most
  important measurement of the whole project for future work: coverage numbers
  computed against the inventory understate the remaining work badly.
- Verified the biggest regular case: `31e3:000c` (one 120-byte entry) is **five**
  units — four wrappers of 21 bytes that differ only in one constant
  (`ext(a, 0x1000|0x2000|0x8000|0x4000, b)`) plus a 32-byte conditional. The four
  wrappers are RELOCS (`src/calib/cwrap2.c`).
- The conditional stays PENDING: ours emits `75 0A … EB 08`, the original
  `75 0B … EB 09 90`. The single extra `90` after the `jmp` is most likely
  jump-target alignment decided at **link** time (the unit sits at an odd image
  offset), which no compiler flag on our side can reproduce — a new class of
  diff worth keeping separate from source-form diffs.
- Ledger: 67 rows — MATCH 10, **RELOCS 43**, PENDING 14.

## Round 38 — six RELOCS from two multi-function blobs (49 verified)
- `458e:705a` (inventory: one 44-byte function) is really **three units of
  19 + 19 + 4 bytes** separated by gap bytes: two far-pascal exchanges with the
  old value staged in DX, plus a getter. All three RELOCS with `/Ox`
  (`src/calib/cex1.c`). This settled the family question: the exchange is
  `__pascal` with a frame, not `__fastcall` — the argument comes from `[bp+6]`.
- `458e:8642` (inventory: one 60-byte function) is **three units of 12 + 24 + 20
  bytes**: a shadow copy, a three-argument pascal setter, and the copy back
  (`src/calib/cex2.c`, `/Os`). All three RELOCS.
- Method note that made the difference: when an address inside a merged blob is
  unclear, locate the next unit by searching the byte pattern in the blob rather
  than computing offsets from the inventory size — the gap bytes are not
  uniform (1 byte here, 2 bytes there), and guessing cost two failed attempts.
- Also caught a wrong-segment match attempt (`35ca:` instead of `458e:`) because
  the diff showed completely unrelated original bytes — a wrong address reads as
  a huge diff, never as a near miss.
- Ledger: 62 rows — MATCH 10, **RELOCS 39**, PENDING 13.

## Round 37 — four near-misses documented, no new verified rows
Honest round: every candidate landed within a few bytes but none matched, so the
result is four precisely documented PENDING rows instead of forced ledger entries.
- **32-bit exchange** (`1871:5c26`, `35ca:209c`, 38 B each): the original keeps
  the old low word in BX (`8B D8` … `8B C3`); MSC 7 (/Os, /Ox, /Ot) and MSC 6
  (/Os, /Ox) all spill both halves to `[bp-4]`/`[bp-2]`. Three source variants
  (initialise at declaration, separate assignment, explicit low/high split) all
  give the spill form.
- **Bit set** (`2603:463c`, 38 B): ours is 34 B. The `cwd / and dx,7 / add / sar`
  prefix proved the source uses `n / 8`, not `n >> 3` (the latter gives 23 B).
  Remaining difference is allocation order — original loads the argument into SI
  first and orders `and bx,7` before `mov si,ax`.
- **Segment extraction** (`1871:7874`, 24 B): original gets the segment through
  `les` + `mov ax,es`; MSC reads `[bp+8]` directly and never emits the `les`.
- Conclusion recorded: these four are the first cases where the *shape* is C-like
  but the register allocation is not reproducible at any compiler level tested,
  which strengthens the hand-ASM suspicion for the affected modules.
- Ledger: 56 rows — MATCH 10, RELOCS 33, PENDING 13.

## Round 36 — far-pointer algorithms: one more MATCH, two RELOCS (43 verified)
- `2603:452e` SWAP_IF_LT (34 B) is a **MATCH** in `src/calib/cswap3.c` with
  `/G1 /AM /Gs /Ox`: `if (*b < *a) { t = *a; *a = *b; *b = t; }` through two far
  pointers, including the `push ss / pop ds` that follows the `lds`. Under /Os
  and /Ot the temporary is spilled (ENTER 2) and the frame differs — fourth
  per-file `/Ox` case.
- `458e:5e66` COPY_PAIR (35 B, RELOCS): `*a = g_2b0a[13]; *b = g_2b0a[14];`. The
  global far pointer appears loaded twice, which is simply the compiler reacting
  to BX being reused for the destination pointer — a useful reminder that a
  "redundant" reload in the original is often just register pressure.
- `35ca:8012` @swap_reset (21 B, RELOCS, `/Ox`): exchange plus three zero stores,
  temp in DX. Same family as the round-33 exchange, so the flags were predictable.
- Two length corrections again: inventory 22 -> real 21 (swap_reset) and
  36 -> real 35 (copy_pair).
- Ledger: 52 rows — **MATCH 10, RELOCS 33**, PENDING 9.

## Round 35 — three MATCHes with far-pointer arithmetic (9 MATCH rows total)
- Swept the far-pointer accessor family (word/byte accessors, far stores): only
  the three found in round 34 exist. Wrapper/thunk families are almost absent —
  exactly one forwarder in the whole image (`37ce:000c`, RELOCS).
- Three new **MATCH** rows in `src/calib/cptr2.c` (`/G1 /AM /Gs /Os`):
  `35ca:1e54` SUB_P3_P1 (21 B, near pascal `(p[3] - p[1]) + a`),
  `35ca:1e7e` SUB_P1_P3 (22 B, far variant),
  `35ca:5550` TEST_AND (22 B, `(*p & mask) != 0`, the
  `cmp ax,1 / sbb ax,ax / inc ax` bool form).
- The only diff was the **declaration order**: pascal pushes left to right, so
  the argument at `bp+4` is the last declared one. Writing `(int a, p)` produced
  the pointer at `bp+4`; `(p, a)` reproduces the original. Confirms the round-33
  rule for mixed word/pointer argument lists.
- Two more candidates skipped with reason: `2603:5306` and `1871:8b0a` scale the
  index with `03 F6`/`03 DB` (`add si,si` / `add bx,bx`), which neither MSC
  generation emits — consistent with the hand-ASM finding.
- Ledger: 49 rows — **MATCH 9, RELOCS 31**, PENDING 9.

## Round 34 — five MATCHes in one batch (73 bytes, six MATCH rows total)
- Mined the 12..22-byte band and transcribed six forms. Five are **byte-identical
  with zero relocations** (`src/calib/cset5.c`, `/G1 /AM /Gs /Os`):
  `35ca:825a` OFF4, `35ca:8268` OFF6, `35ca:8d52` OFF1 (word at +4/+6/+1 of a far
  parameter), `2603:53a0` WRAP3 (`((b - a) + 2) & 3`), `458e:8e08` TEST80 (`v & 0x80`).
- Two fixes were needed and both came straight from the byte diff:
  - the dereference must be `*(int __far *)` — with a near cast MSC emits
    `8B 5E 06` instead of `C4 5E 06` (`les`), losing the segment load;
  - byte arguments follow the same pascal rule as words: `[bp+6]` is the last
    declared one, so the subtraction order had to be flipped.
- `458e:8e08` was 13 bytes, not the inventory's 14 (trailing gap).
- **`add bx,bx` (03 DB) is never produced by MSC 6 or MSC 7** — tested /Os, /Ox,
  /Ot, /Od, /O2 on `return g_142a[i]`; all emit `D1 E3` (shl). Since the binary
  contains 74 such sites, this is now solid evidence that those functions are
  hand-written assembly, not C. Recorded in CONVENTIONS.md.
- Two new PENDINGs with full evidence: `2603:ccda` (DX staging for `-1 - v`) and
  `35ca:2306` (the array index above).
- Ledger: 45 rows — **MATCH 6, RELOCS 30**, PENDING 9.

## Round 33 — first MATCH, plus two RELOCS (31 verified)
- **`2603:3efc` F_3EFC (13 B) is the first MATCH in the project**: bytes identical
  with no relocation to mask. Form `return d - b` with four word arguments
  (`retf 8`); the pascal argument order (left to right push) puts the last
  declared parameter at `bp+6`, which is what the original reads.
- `458e:8306` f_8306 (10 B, RELOCS): `int __near f(void) { return 1 << g; }` —
  terminator `C3` proved it is a near function; the decompiler's `& 0x1f` is its
  own invention, the code shifts by the raw byte.
- `35ca:8072` @swap_78cc (10 B, RELOCS): `__fastcall` exchange. **First function
  proven to need `/Ox`**: `/Os` and `/Ot` put the temporary in `CX`, `/Ox` puts it
  in `DX` like the original. Third per-file-flags case after round 23.
- Rejected on byte comparison and recorded: `35ca:8072` under /Os (CX vs DX),
  `458e:a4c6` (ours frameless, original saves si/di).
- Ledger: 38 rows — **MATCH 1, RELOCS 30**, PENDING 7.

## Round 32 — family sweeper tool; small-function families measured as empty
- **`tools/sweep.py`** added: takes a family definition (regex + C template),
  finds every hit at a real function boundary not yet in the ledger (compared by
  linear address), writes the C, compiles once and matches all members;
  `--emit` prints ready ledger rows. Seven families are defined:
  `byte_store`, `word_inc`, `word_dec`, `byte_inc`, `word_copy`, `byte_copy`,
  `word_add_imm`.
- **Measured result: those families are effectively absent.** Raw occurrences in
  the whole image: `C6 06` 5, `FF 06` 1, `A1..A3` 2, `FF 0E`/`FE 06`/`A0..A2`/
  `83 06` 0 — and **none** starts at a function boundary. The compiler preferred
  other forms, so this vein is exhausted (recorded so it is not retried).
- Framed leaf clustering (prologue `55 8B EC`, epilogue `C9 CB/C3`, bodies
  disp-masked, 8..30 bytes): only **8** candidates remain, 8 distinct bodies,
  and all of them are CRT or interrupt-wrapper code at the image start.
- SLOT_FILL retested with `/Ox` and `/Os /Oy` after the round-23 discovery:
  `/Os` yields 162 B vs the original 166 B, but the difference is structural —
  original `ENTER 2` + saves `di`+`si`, ours `ENTER 8` + saves `si`. Stays PENDING.
- Ledger unchanged this round: 35 rows — 28 RELOCS, 7 PENDING.

## Round 31 — global-immediate family swept: 4 new RELOCS (28 total)
- `tools/mine.py` added (template phase 5, step 1: find candidates) — lists
  call-free, jump-free small functions with their decompiled body. Fixed it to
  dedupe by **linear** address, otherwise segment aliases of matched functions
  show up as candidates (seen: `1871:d0e4` = `257f:0004`).
- Swept the `C7 06 <disp> <imm16>` initializer family: 4 more RELOCS in
  `src/calib/cset3.c` — `458e:a206` (resets the slot counter proven in rounds
  17/18), `458e:35ae`, `4df7:0002`, `3db4:0006`. Two further scan hits turned out
  to be segment aliases of these (`0x48E8E`, `0x4FAE6`).
- Ledger: 35 rows — **28 RELOCS**, 7 PENDING.

## Round 30 — mining call-free bodies: 2 new RELOCS, 1 false lead caught by verify
- Wrote a mining script over the decompiled output (call-free bodies, size 5..24)
  and transcribed two leaf forms (src/calib/cset2.c, `/G1 /AM /Gs /Os`):
  - `1871:37ce` set_9b3c (7 B) — `void __near f(void) { g_9b3c = 1; }` (`C7 06` store)
  - `35ca:8df8` get_b98ea (6 B) — `int __far f(void) { return (unsigned char)g; }`
    (`A0` load + `2A E4` zero-extend)
- **verify caught a false lead**: I recorded `1871:8c0c` as a duplicate of
  `set_flag`; the duplicate-address check proved it is the same linear address
  (`0x2131C`) under a different seg:off — a segment alias, not a second function.
  Row removed; this is the round-23 alias lesson applied automatically.
- MSC 6.0 retested on the slot-allocator PENDING (/Ox, /Os, /O2): always emits a
  frame (`C8 ..`), so MSC 7.0 `/Ox` remains the best variant (14/16 B).
- Ledger: 31 rows — **24 RELOCS**, 7 PENDING.

## Round 29 — build cache implemented (verify 18.6 s -> 0.8 s)
- `build.py` writes a stamp (`flags`, toolchain dir, DPMI flag, source mtime and
  size) next to each object and skips the compile when all of it matches; `--force`
  bypasses the cache. Template phase 3 asks for exactly this.
- `verify.py` reports `CACHED` vs `built` per source file, so a stale cache can
  never pass silently — a flag or source change invalidates the stamp.
- Measured on this machine: first verify (8 source files around dosbox-x)
  **18.6 s**, cached verify **0.8 s**.
- Matching vein for the round: two-parameter canonical shapes (`retf 4`) and a
  masked-skeleton clustering over all 589 remaining candidates both produced no
  family — documented here so the next round does not repeat the dead ends.

## Round 28 — three more canonical forms matched (22 RELOCS total)
- Shape scan over real function boundaries found three further canonical
  far-pascal one-parameter units (src/calib/coset2.c, `/G1 /AM /Gs /Os`):
  - `2f22:0006` SET_1C48 (13 B) — `g_1c48 = v`
  - `1fc8:0000` OR_RET_F6 (17 B) — `g_00f6 |= v; return g_00f6`
  - `1fc8:0012` ANDNOT_RET_F6 (18 B) — `g_00f6 &= ~v; return g_00f6`
- Two measurement lessons, both recorded in `docs/IDIOMS.md`:
  1. Inventory sizes here are wildly inflated (340 and 214 bytes) because Ghidra
     merged several units into one function; the real length comes from the
     `leave / retf imm16` terminator.
  2. A window two bytes too narrow silently "passes": the last byte of the
     `retf` immediate was outside the compared range. Always include the full
     `C9 CA xx xx` sequence.
- Ledger: 29 rows — **22 RELOCS**, 7 PENDING.

## Round 27 — setter family matched: 5 new RELOCS, repo translated to English (2026-11-23)
- Targeted pattern search for the canonical far-pascal one-param form
  (`push bp / mov bp,sp / mov ax,[bp+6] / <op> / leave / retf 2`) found real C.
- **5 new RELOCS** (src/calib/coset1.c, `/G1 /AM /Gs /Os`):
  `35ff:0004`, `3b20:0006`, `4c9b:000a` (setters, 13 B) and
  `1fc6:0004`, `1fc7:0002` (AND-return functions, 14 B).
- Opcode direction mattered again: original `23 06` = `and ax,[disp]` (result in
  AX, function returns it) — writing `g &= v;` produced `21 06` (store) and failed.
- Sizing pitfall: the inventory size for the setters is 14 but the real function
  is 13 bytes (the follow-up gap byte was counted). Matching with the ledger's
  real length fixed the spurious `90 vs 00` diff.
- Whole repository rewritten to English (docs, tool docstrings/messages, source
  comments); logic, numbers and ledger notes verified unchanged (verify green,
  AST/comment-stripped diffs identical).
- Ledger: 26 rows — **19 RELOCS**, 7 PENDING.

## Round 26 — MSC 6.00ax obtained, hypothesis tested and disproved (2026-11-23)
- MSC 6.00ax fetched from archive.org (SHA1 verified), disks unpacked.
  Format is `SZ` (not `KWAJ`) — the MSC-7 `DECOMP` handles both; 34 headers +
  8 compiler passes decompressed (now under **dosbox-x**, one environment instead of two).
- `build.py` extended: `--msc-dir MSC6I` and `--no-dpmi` (MSC 6.0 is pure
  16-bit, no DOSX32/DPMI). MSC-7 default path still green (verify: 14 RELOCS).
- **Test of the hypothesis:** init family with MSC 6.0 under /Os, /Od, /Oa /Od ->
  always `33 C0 A3 A3`, i.e. identical to MSC 7.0. The assumption "game modules
  with MSC 6.x" is therefore **disproved** (documented in CONVENTIONS.md).
- Consequence: the hand/inline ASM hypothesis for the slot subsystem, clamp and
  init family as well as CONV is supported; the caller context remains the cross-check.

## Round 25 — suspicion: wrong compiler generation (phase-0 relapse) (2026-11-23)
- Init family (2x22 B: `g1=0; g2=0; far_call(0x18,1)`) fully decoded
  (pascal convention, argument order proven from push order) — but not
  matchable: /O2 gives the C7-06 stores WITH frame, /Os|/Ot|/Ox frameless WITHOUT.
- **Byte statistics of the binary** as cross-check: `add bx,bx` 74x vs `shl` 18x;
  `C7 06 .. 0000` 130x vs zero fold 32x; frame density 1184x (fits /Os).
  MSC 7.0 produces the most frequent original forms in no flag combination.
- Working hypothesis documented (CONVENTIONS): game modules possibly translated
  with **MSC 6.x**, linked against CRT 7. Before any further hand-ASM classification
  this must be checked, otherwise a toolchain assumption gets misdiagnosed as hand ASM.
- Ledger: 21 rows, 14 RELOCS, 7 PENDING.

## Round 24 — integrity hole closed: verify builds itself (2026-11-23)
- Ledger format canonicalized: every MATCH/RELOCS row carries
  `src=<source file>; flags="<cflags>"` — verify.py reads that and **recompiles
  every (src, flags) combination**, instead of relying on existing `build/*.OBJ`.
- Proof: `build/*.OBJ` deleted -> verify built all 6 source files and reported
  14/14 RELOCS ok, PENDING 5, green. Previously the same run would have checked
  against stale or foreign compilations (round-23 finding).
- `--fast` deliberately skips the rebuild (intermediate check only, never close-out).
- Duplicate and size-0 checks remain in verify (template phase 6).

## Round 23 — optimization level discovered as a codegen class (2026-11-23)
- Family scan with masked disp16: 3 groups. The largest (3dd3:0000..) is a
  **segment alias** of the already-matched getters (linearly identical to
  35ca:8090) — lesson: the linear address is the identity, otherwise double counting.
- Clamp siblings (1f2d:000e / 1f2f:0002, 2x20 B) decoded: min(max(x,1),g)
  with __fastcall and DX temp. 6 variants tested, MSC7 produces neither
  frameless+DX (original) — PENDING.
- **Main finding:** `/Oy` and `/Ox` remove the frame; all previous matches
  used `/Os`. `/Ox` brought get_39f8_clamped to 14/16 B (remaining: `C3 90` vs
  `EB 03`, i.e. early return+pad instead of jump merge). Flags are to be chosen
  per source file — recorded as a rule in IDIOMS.md.
- CONV cross-checked under /Ox: `D1 E3` remains (hand-ASM suspicion confirmed there).
- Integrity hole noted: verify.py does not rebuild, it checks the existing OBJs.

## Round 22 — report.py: STATUS.md is generated (2026-11-23)
- `tools/coverage.py` split into `compute()` (numbers) + `main()` (console output),
  so `tools/report.py` can use the same numbers without duplicate logic.
- `tools/report.py` writes `docs/STATUS.md`: ledger counters (MATCH/RELOCS/PENDING),
  PENDING list, coverage table, regions table. The hand-written part sits
  between `MANUAL-BEGIN`/`MANUAL-END` and survives every run (tested).
- Counters are therefore no longer maintained by hand — STATUS can no longer
  become stale or contradictory (the cause of the round-21 cleanup).
- verify green, coverage numbers unchanged (100 / 293 640 B = 0.034%).

## Round 21 — inventory cleaned up: 1956 code functions instead of 1970 (2026-11-23)
- `functions.csv` now carries `section=CODE|DATA`; `gt.py` sets the marking from
  `not_code.csv`, `coverage.py` counts only CODE rows as functions.
- Rows are preserved (size depends on the distance to the next function) —
  nothing is deleted, only classified. One source instead of two counting paths.
- Numbers unchanged correct: 294 603 code bytes − 963 CRT = 293 640 own bytes,
  100 verified (0.034%); function count now honestly 1 956 + 14 data.
- verify green (17 rows), no ledger entry falsely marked as DATA.

## Round 20 — two RELOCS + two new idiom rules (2026-11-23)
- OR_JOIN (20b2:0000): `void: g_or |= x` — the diff `09` vs `0B` was the
  assignment direction (or r/m,r = store vs. or r,r/m = return), not the expression.
- _wait_change (20ab:000c): spin wait on `volatile int` — without volatile MSC7
  hoists the loop load (18 B, degenerate cmp), with volatile the reload stays in the
  loop head and hits the original exactly including `74 F8` (20 B).
- verify.py now passes the **ledger size** through to match.py (--size):
  according to the template the ledger size is the real length; inventory windows that
  run into the following function (here 18 instead of 14 B) would otherwise
  falsify the comparison.
- Status: 14 RELOCS / 3 PENDING, 100 of 293 640 own code bytes (0.034%).

## Round 19 — 12 211 bytes of misinventory classified as data (2026-11-23)
- The 38 Ghidra decompilation errors sorted: 14 entries provably not
  code — CD-3F sound-driver command blocks (NMUSE/MIDE, 6-byte stride), linear
  word tables, 10.9 KB null field, ASCII string 'num err floor'.
- ground_truth/not_code.csv + coverage.py data category: metric now threefold
  honest — 293 640 own code bytes (instead of 306 814), 66 verified.
- ~24 further FAILs look like real functions (ENTER frame, parameter
  loads) — candidates for later rounds.

## Round 18 — conv decoded: 14/16 bytes, pattern thesis hand ASM (2026-11-23)
- 458e:a1ea == inc_39f8_capped (already RELOCS ✓) — 'slot_update' for free.
- 4fad:0006 (CONV, 16 B, near-pascal lookup): 5 source forms + 3 optimization
  levels — /Os matches EVERYTHING except 2 bytes (shl vs add bx,bx). Frame
  compaction (push bp/mov bp,sp instead of ENTER) confirmed in the original and reproduced.
- Pattern thesis matured: the slot subsystem (4 functions) consistently carries
  hand-ASM idioms — documented in IDIOMS.md as a working basis.

## Round 17 — slot routine: form decoded, 4 hypotheses, PENDING (2026-11-23)
- 458e:a20e (166 B, pascal, far param) fully disassembled: slot index flow,
  8 field offsets 0/2/4/9/11/13/15/19, conv CL push, retf 4 (=1 far param, Ghidra's
  param_2 was an artifact). Odd slot size 0x27 -> char array, no struct.
- Reconstruction v3 reached 162/166 B — remaining difference: register walk without
  stack write-back (MSC7 C writes the param back). PENDING with form analysis
  in IDIOMS.md; cslot1.c keeps v3 as the next starting point.
- Practical corner: __pascal uppercases symbols; >127 jump distance produces the
  jge+3/jmp form automatically (branch explanation for the 4fab:000a kinship).

## Round 16 — PENDING semantics proven (2026-11-23, evening)
- Caller of 4fab:000a found (FUN_458e_a20e): slot index allocator,
  sentinel -1 is checked, slots 0x27 bytes, array base DGROUP-relative
  (-0x6d58). Jump merge remains a hand-ASM suspicion — PENDING note deepened.
- FUN_458e_a20e itself (52 B slot fill routine) is a candidate for the
  next family round: parameters, field writes, RTC-free form.

## Round 15 — coverage separates foreign code (2026-11-23, evening)
- coverage.py shows a 'foreign CRT' column: 963 B (35 unique library signatures)
  are subtracted from the own-byte metric — percentage now against own bytes
  (66/305851 = 0.022%). The CRT share grows with further signature hits.

## Round 13 — CRT region mapped (2026-11-23)
- markcrt.py repaired: MS librarian aligns modules (padding after MODEND)
  — scan to the next THEADR; now 379/379 modules from MLIBCR.LIB.
- **35 unique CRT hits** (reloc-masked library signatures) in
  DDS98.EXE, from 10bd:0002 upward: __int86/_abs/_srand/__NMSG_WRITE/__dos_setvect …
  -> ground_truth/foreign_crt.csv. CRT lies at the start of the image (linker order).
- Open for the next session: extend coverage.py with a foreign-code column,
  report the CRT byte share separately in the honest metric.

## Round 11 — coverage.py + PENDING deepening (2026-11-23)
- get_39f8_clamped: 5 construct/opt combinations exhausted (ternary x2, if/else+r,
  /O1, /O2) — MSC7 never produces the jump-merge form from C. PENDING with
  hand/inline ASM suspicion documented; proof via caller context later.
- coverage.py built (template phase 6): bytes per 64-KiB region against the
  original inventory — the honest metric is 66/306814 bytes (0.022%).

## Round 10 — 0x39F8 pair: 1 RELOCS, 1 honest PENDING (2026-11-23)
- inc_39f8_capped (4fac:000a): RELOCS — `if (g<0x10) g++;` form exact.
- get_39f8_clamped (4fab:000a): PENDING — MSC7 /Os compiles the ternary to the
  early-return form; the original uses jump merge with one RET. Two
  hypotheses (ternary, if/else+r) documented; the third follows with caller context.
- IDIOMS.md populated with verified MSC idioms for the first time (template 4: add
  after each solved diff cause — here: the unsolved one too).
- verify: green — 13 ledger rows, RELOCS 12, PENDING 1.

## Round 9 — 32-bit getter pair + flag op: 11 RELOCS total (2026-11-23)
- cget3.c: get_l (far) + get_ln (__near) — DX:AX return, 2x disp16 fixup each,
  original 1871:d0e4 / 35ca:3c34 (Ghidra had mistyped get_l as 16-bit).
- cflag1.c: set_flag = or byte [0x0F44],0x40 — single member, range <=8 bytes
  thus fully classified (GET 8, pair 2, flag 1).
- verify: green, ledger 11 rows, 0 PENDING.

## Round 8 — GET family complete: 8/8 RELOCS (2026-11-23)
- Family scan (functions <=8 bytes by code shape): GET family has 8 members.
- Part 2 (cget2.c): four single-scalar getters on DGROUP 0x1A4/0x2FCE/0x2C50/0x2D0C —
  all four RELOCS; verify: green, ledger 8 rows, 0 PENDING.
- omfdump: compact 0x9C fixups with variable entry length (3/4 bytes, target index).

## Round 7 — phase 0 COMPLETE: 4 byte-verified functions (2026-11-23)
- **First RELOCS matches**: getter family 35ca:8090..9c (get0..get3),
  `mov ax,[disp16]; retf` — disp16 as the only masked linker fixup.
- **CFLAGS confirmed: `/G1 /AM /Gs /Os`** (medium model; /Gs = no chkstk
  prologues in the original; /Os = bare leaf form; /G1 = 186 idioms).
  Correction: earlier huge/large assumption wrong (near-data proof).
- match.py complete: OMF extraction (omfdump.py) + reloc masking + classification.
  MSC7 fixups run as compact 0x9C records (COMENT class A2 extension).
- verify.py is in place, runs green: ledger 4 rows, 4 RELOCS, 0 PENDING.
- Practical corner: CL dies silently for source files >8.3 characters (calibration source
  renamed cget.c); LINK.EXE (DOSX16) under dosbox-x so far unusable (hangs
  in all DPMI variants) — phase-6 topic.

## Round 5/6 — toolchain breakthrough (2026-11-23, 01:35)
- **MSC 7.0 (CL 8.00) compiles**: `triv1.c /G1 /AL` → 480-byte OMF object.
- Verified recipe: dosbox-x + HDPMI32 TSR (HX-DOS 2.17) + `-nopromptfolder`
  + APPDATA redirect + `cycles=max`. DOSBox 0.74: R6901/no DPMI; dosbox-x's own
  DPMI crashes with MSC7 (GitHub issue #3844).
- `build.py` switched to the recipe, verified end-to-end against itself.
- Toolchain decoration complete: 224/224 files from the KWAJ disks (DECOMP under
  DOSBox 0.74; findings: BAT without `CALL` eats the rest of the autoexec;
  background jobs leave DOSBox-0.74 children hanging — foreground runs only).

## Round 1 — 2026-11-23
- Parameter block documented and recorded in `CONVENTIONS.md` (MZ, x86-16 real mode,
  load-image/overlay geometry, MSC-8 candidate via CRT banner, entry `0x1871:0BE5`).
- Skeleton created: `include/dds98 src tests tools docs ground_truth`.
- `tools/`: `gt.py` (inventory), `disasm.py` (hexdump + Ghidra instruction dump),
  `match.py` (byte-match core with self-test; the BUILD step aborts in a controlled
  way until calibration), `ghidra_run.py` (headless starter with APPDATA sandbox workaround),
  `build.py` (stub, `TOOLCHAIN_NOT_CALIBRATED`).
- Phase-0 scans evaluated (ScanIdioms, 68 452 instructions): CPU base 80186+
  (`/G1` candidate), memory model large/huge (tendency `/AH`, DGROUP ≈ 102 KB),
  crt0 sequence at entry `0x1871:0BE5` confirms Microsoft-C-16-bit.
- Overlay analyzed: dense binary payload (~141 KB), no archive signature,
  no self-path reference — clarify via loader routines later.
- match.py self-test green (MATCH/RELOCS/DIFF core, reloc masking, length diff).
- Open: toolchain acquisition (MSC 8/MSVC 1.5x + DOSBox) — user approval needed;
  then calibration compile (phase 0) and first MATCH round.
