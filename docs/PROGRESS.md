# PROGRESS

## Round 65: two more classes named (no new rows)
Both came out of probing units that had failed before for reasons I had assumed
rather than proven.

**`char` arguments are pushed unpromoted.** `2127:000c` (32 B) is
`if (h1(a, b)) h2(a);` with `a` a byte parameter: the original loads `8A 46 08` and
pushes AX with AH untouched, while MSC 7 promotes first (`98` = `cbw`, or `2A E4`).
Declaring the callee unprototyped does not change it - MSC still emits the
promotion - so this is a pre-ANSI language difference. Thirteen unmatched units
(885 bytes) carry the pattern.

**`sub ax,ax` zeroing.** `3da5:000a` (67 B) differs from a full match only in
`2B C0` versus `33 C0`: the original zeroes with `sub ax,ax`, MSC 7 only ever emits
`xor ax,ax`. Twenty unmatched units (4 224 bytes) contain the older form.

`docs/BLOCKED.md` now lists **18 classes** and the unclassified pool is
**177 units / 10 957 B** (from 186 / 11 319 B). Three of the classes are heuristic
patterns (`nop-padded branch`, `byte argument without promotion`, `sub ax,ax
zeroing`) and each is documented with the units that were verified by full
analysis, so the map distinguishes "proven unreachable" from "suspected".

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 64: the largest padding-blocked unit found (362 B) - no new rows
`3bab:00aa` (362 B) is the biggest function the padding class has claimed so far:
a `switch` on its parameter with case blocks that each issue a run of
`h(g_17d2, n, 0x8000, flag)` calls, twenty-one references to the same DGROUP object
overall. It is transcribable and I started it, but the first case block already
shows the padded jump (`EB 2C 90`), so the whole function is out of reach for the
same one-byte reason as its smaller relatives.

Two more units examined and left alone for stated reasons:

- `1eab:0002` (58 B) - two calls where the second's arguments are the *long result*
  of the first plus a byte-swapped parameter (`8B C7 8A C4`), and whose segment is
  then written back into a parameter slot (`8C 46 0C`). The older compiler reuses
  the parameter frame as scratch storage; MSC 7 allocates a local.
- `3ede:00a0` (64 B) - the byte stream stops looking like code after the first far
  call (`9A 09 88 3A A3` followed by what decodes as inline data), so the unit is
  a function-plus-table rather than a pure function.

Sweeps (`reuse.py`, `probe.py`) report nothing new after the reclassifications.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 63: the nop-padding class generalised - 4.5 KB reclassified (no new rows)
Chased `3b9b:000a` (124 B), a nested guard in the `g_17d2` family
(`if (h4(a,b,c,d)) { if (h0()) { if (h2(2,0x39)) { h3(a,b,1); h4b(g_190c,-1); } else { h5(1); h6(0x20); } } else h7(a,b,1); } h8(g_17d2,c,1); return c;`).
It matched in every instruction except a single `90`: the original pads the
`jmp` that reaches the shared tail (`EB 0E 90`), MSC 7 does not (`EB 0D`), and
the padding shifts every earlier branch distance by one.

That is the **fifth** fully-analysed instance of the padding class
(`4998:000c`, `3b88:000e`, `31e3:0064`, `3cd1:02f2`, `3b9b:000a`), which was
enough evidence to generalise the `classify.py` trait from the narrow
`EB 02 90` / `EB 03 90` forms to any `EB <n> 90`. The effect on the map:

| | before | now |
|---|---|---|
| unclassified | 233 units / 15 801 B | **186 units / 11 319 B** |
| nop-padded branch | (narrow forms) | 147 units / 23 745 B |

The trait is explicitly documented as a heuristic in `BLOCKED.md` and in
`CONVENTIONS.md`, with the five verified instances named, because the pattern
alone cannot distinguish padding from a coincidental byte pair - but five
independent full analyses of 30-124 byte functions is strong support.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 62: the pointer-exchange family matches modulo a scratch register (no new rows)
Two more members of the family found in rounds 60-61, both now down to **two bytes**:

- `50ff:000e` (138 B) - `h1(&a,&b); h2(&b,&c); h3(&a,&b); if (h4(b,c) != 1) { r = h5(b,c,0); if (r >= 0x20) r = h6(0,a,1); } else { r = h6(b,c,1); if (r >= 0x20) r = h5(0,a,0); } h7(); return r;`
  ('the two branches tail-merge into one call with different arguments);
- `511b:000e` (96 B) - the twin of round 61's row, differing in the same place.

Both differ only in the scratch register MSC picks for the **second** `&parameter` in a
pair: the original computes both into AX (`8D 46 08 ... 8D 46 06`), MSC 7 puts the
second in CX (`8D 46 08 ... 8D 4E 06`). Notably MSC's choice is *context dependent* -
the identical prefix in round 61's `5108:0008` does come out as AX/AX and matches -
so this is an allocation decision, not a source shape.

Also confirmed the nop-padding class on a fourth unit: `3cd1:02f2` (56 B) is a
bounds check (`h1(&x,&y); return x >= 0 && g_193c > x && y >= 0 && g_193e > y;`)
that differs only by the `90` the original inserts after its `jmp`
(`B8 01 00 EB 03 90 33 C0` versus MSC's `B8 01 00 EB 02 33 C0`). The if-return,
ternary and bare-boolean formulations all give MSC's form.

Ledger 455 rows (unchanged); verify and checkled green; own-code coverage
9 796 B (3.341 %).

## Round 61: the third member of the address-of-parameter family (95 B)
`crelay59.c` (`/Os`): `5108:0008` (95 of a 96-byte unit; the last byte is padding) -
`h1(&a, &b); h2(&b, &c); h3(&a, &b); r = h4(a, b, 1); if (r >= 0x20) r = h5(0, c, 0); h6(); return r;`.

Found by scanning for the `8D 46 <n>` + `16` + `50` idiom (address of a parameter
pushed as SS:BP) that round 60's row introduced: it returned ten units, three of
which are clearly the same template. `511b:000e` is its twin and matches to a
**single modrm byte** - the original computes the third `&b` into AX
(`8D 46 08`), MSC 7 into CX (`8D 4E 08`) - so it stays out, but it is the closest
one-byte miss in the ledger's history.

The idiom scan is the right generalisation of round 60: a verified shape becomes a
search key, and the search found the family in one command instead of several
rounds of size-band guessing.

Ledger 455 rows - MATCH 38, RELOCS 393, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 796 B (3.341 %)**.

## Round 60: a guarded initialiser chain (86 B)
`crelay58.c` (`/Os`): `5116:0008` (86 B) -
`h1(&a, &b); h2(&b, &c); r = h3(a, b, 0); if (r >= 0x20) r = h4(0, c, 0); g_4090 = 0x0A; h5(); return r;`.
Two calls take far pointers to the **parameters themselves** (`8D 46 <n>` + `16` +
`50`, i.e. SS:BP), so the parameters must stay addressable on the stack, and the
status guard is a `7C` that jumps *over* the second call.

Four iterations on the same unit, each a different question, and all four were
worth asking:

1. the two pointer calls take `(&a, &b)` and `(&b, &c)` - a chain, not the reverse;
2. the status call takes `(a, b, 0)`, not `(c, b, 0)`;
3. the guard is `if (r >= 0x20)` (fall-through call), the mirror of my first guess;
4. the second call takes `(0, c, 0)`, not `(0, a, 0)`.

The size was again the object symbol's (86), not the 82 I first used - the fifth
time `verify.py` has caught that, and it caught it here within one run.

Batch screening continued to pay: this unit came out of a six-candidate compile and
took four cheap iterations instead of four compile-heavy rounds.

Ledger 454 rows - MATCH 38, RELOCS 392, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 701 B (3.309 %)**.

## Round 59: batch screening pays off, two units down to one prologue (no new rows)
First round with the batched method: six candidates transcribed mechanically, one
compile, all matched at once. Two of them came back **byte-identical except for a
single prologue instruction pair**:

- `1070:0008` (67 B) - `r = h2(g_4ad0, 4); v = h3(g_4ad0, a, b, &c); h4(g_4ad0, r); return v;`
- `103b:000c` (63 B) - the same shape with the pointer passed in as a parameter
  (`(char __far *)p`), so all three calls take the far form of a DGROUP pointer.

Both are `G0` cdecl functions with locals, and there MSC 7 splits the reservation
into `B8 04 00` / `2B E0` / `50` where the original emits a single `83 EC 06`.
Declaring the function `__pascal`, dropping the `&parameter` argument and casting
the pointer all leave the split form in place, so the two units stay out of the
ledger - but at 130 bytes combined they are the closest miss in many rounds and
are now a documented class.

The batch method itself worked as intended: six candidates cost one compile instead
of six, and the transcription of each was a straight read of the push order. That
is the throughput fix the last five rounds needed.

Ledger 453 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 615 B (3.279 %).

## Round 58: `/G0` confirmed on a near function, and a change of method (no new rows)
`13db:000c` (50 B) is a near-Pascal function with a long parameter
(`void f(long v, int n) { if (n) h2(h1(v) + 1, v + n); }`). It confirmed two things:

- its epilogue is `8B E5 5D C2 06 00` - a **`G0` frame** (`mov sp,bp` then `pop bp`),
  and under `/G0` MSC 7 reproduces that epilogue exactly;
- its cdecl cleanup is `8B E5` rather than `add sp,4`, matching the `/G0` form.

It still does not match, for a reason already documented in round 38: the original
evaluates the **first** argument (`h1(v) + 1`) before the second (`v + n`), while
MSC 7 evaluates function arguments right to left. No source formulation of a
two-argument call changes that.

**Change of method.** Rounds 54-58 produced no rows because I was deep-diving one
or two units per round; the remaining pool of 97 "no known blocker" candidates is
mostly small relays whose tell is a single instruction. From round 59 I will
**batch-screen six to eight candidates per round** - transcribe them mechanically
into one file, compile once, and run `match.py` over all of them - which cuts the
compile cost per candidate by roughly five times and should restore a row every
round or two. Anything that survives the screen gets the deeper treatment.

Ledger 453 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 615 B (3.279 %).

## Round 57: the inline-long-shift class (3.8 KB) - no new rows
Chased the oldest open PENDING row, `20b4:0160` (_read24, 37 B), and proved why it
cannot be written: the original **inlines** a 32-bit `x << 8` as `8A E0` (`mov
ah,al`) / `2A C0` (`sub al,al`) for the low word and `8A F2` / `8A D4` for the
carry into the high word, whereas MSC 7 calls the shift helper (`B1 08` + `9A`)
for every formulation of the same value - a single expression, a chained
`v = (v << 8) + g`, and both signed and unsigned variants were tried and all emit
the helper.

That makes it a class, and a large one: a scan found **12 unmatched units carrying
the idiom, 3 810 bytes** - six of them functions over 130 bytes
(`1a51:000c` 248 B, `1a61:0004` 224 B, `1a6f:0004` 196 B, `1c0c:000c` 183 B,
`1a81:000a` 138 B, `224b:0004` 131 B). They are now `inline long shift` in
`tools/classify.py` and documented in `docs/CONVENTIONS.md`.

`docs/BLOCKED.md` after the change: **233 unclassified units / 15 801 B** (from
241 / 16 231 B last round), 17 classes.

Ledger 453 rows (unchanged), PENDING still 22; verify and checkled green; own-code
coverage 9 615 B (3.279 %).

## Round 56: a wrong hypothesis withdrawn from the ledger (no new rows)
`31e3:0064` (W_COND, 32 B) had stood PENDING since round 18 with the note that its
extra `90` "looks like jump-target alignment decided at link time". Round 45's
nop-padding proof settles it: the padding is emitted by the **compiler** (the same
`EB <n> 90` form that makes `4998:000c` and `3b88:000e` miss by exactly one byte),
so the link-time-alignment hypothesis is withdrawn and the row now cites the
proven class. Ledger accuracy matters more than the row count here - a wrong
diagnosis in the ledger is worse than an unexplained one.

Also re-checked the two most persistent PENDING rows with this round's tools:

- `20b4:0160` (_read24, 37 B) - a 24-bit read assembles `g_f3a/g_f3b/g_f3c` with
  inline byte shifting (`8A E0 2A C0` = shift a byte into AH) and no runtime call.
  Every natural long formulation (`<< 8`, `<< 16`, chained `v = (v << 8) + g`)
  calls MSC's 32-bit shift helper, so the source must operate on 16-bit
  intermediates; not solved this round.
- `1871:7874` (SEG_OF, 24 B) - still needs `les` + `mov ax,es` after zeroing a
  local, which MSC never emits for a far-pointer parameter.

`tools/probe.py` was swept again across every calibration symbol: only the known
`3670:00e2` hit, already in the ledger.

Ledger 453 rows (unchanged), PENDING still 22 - the row keeps its status, only
its diagnosis changed; verify and checkled green;
own-code coverage 9 615 B (3.279 %).

## Round 55: the three codegen profiles mapped (no new rows)
Following round 54's cdecl finding, I checked whether another optimisation level
reproduces the original more often. It does in part: **`/Od` matches the original's
instruction selection much better than `/Os`** - stores become `C7 06 <g> <imm>`,
the cdecl cleanup is `83 C4 <n>`, comparisons use `3D <imm> 74`, exactly as the
original. The blocker is the frame: `/Od` emits ENTER unless `G0`, and `/G0 /Od`
emits `55 8B EC 81 EC <n> 00 56 57` (reserving all locals and always saving
SI/DI), while the original almost always has the bare `55 8B EC`.

A scan of the whole unmatched pool found exactly **one** unit with the full
`/G0 /Od` prologue (`1971:0006`), and it is a mid-routine fragment, so the profile
is documented but not usable for rows. The three available profiles and where each
one diverges from the original are now recorded in `docs/CONVENTIONS.md`.

This closes the "try other flags" line of investigation: `/Ot` and `/Ox` behave
like `/Os` on these units, `/Od` fixes selection but breaks the frame, and the
original is unoptimised selection with a bare classic frame - a combination MSC 7
cannot produce.

Ledger 453 rows (unchanged this round); verify and checkled green; own-code
coverage 9 615 B (3.279 %).

## Round 54: cdecl argument order and cleanup form corrected (no new rows)
`2d9b:0002` (85 B) came close - a global-flag init unit
(`if (!(g_1bee | g_1bec)) { cd6(...); g_1bec = 1; g_1bee = 0; h3(...); }`) - and the
work on it corrected two beliefs rather than producing a row:

1. **cdecl arguments push right to left.** The original pushes the four ints and
   then the far pointer, so the pointer is the *first* argument in the source
   (`cd6(g_1bf2, g_1be8, g_1bea, g_1bec, g_1bee)`), not the last. With that fixed
   the push sequence matches byte for byte.
2. **The cdecl cleanup form is context dependent.** An earlier note claimed an
   unprototyped callee always gives `8B E5`; a minimal check disproves it - a
   prototyped cdecl call with no locals gives `83 C4 06`, as the original does.
   MSC 7 switches to `mov sp,bp` for calls inside a continuation block
   (`2d9b:0002`, `1dfc:0116`), where the original keeps `add sp,<n>`.

The remaining mismatch in `2d9b:0002` is exactly that cleanup byte pair plus the
register allocation MSC does around it, so the row stays blocked - but both
corrections are in `docs/CONVENTIONS.md` now and apply to every cdecl call site in
the pool.

Ledger 453 rows (unchanged this round); verify and checkled green; own-code
coverage 9 615 B (3.279 %).

## Round 53: the `+ 1` guard idiom (33 B)
`crelay57.c` (`/Os`): `42ac:000a` (33 B) - `if (fc(a) + 1) h1(a); else h2(a);`. The
guard compiles to `inc ax` / `jz` - the idiom for testing a call result against
-1 without a compare - and both branches relay the same `register` parameter from
SI. Two `99`-style details made this round: the call must be declared `__near`
(the image has a 3-byte `E8`), and the `+ 1` must be *in the condition*, not a
`!= -1` comparison.

The idiom turned up in 59 unmatched units, so I scanned them as potential
siblings. That scan was mostly negative but informative:

- `3aa3:0008`, `3dc1:0046`, `3dc1:0074`, `31df:0004`, `42b9:000c` - all use the
  same dispatch chain but each block is nop-padded (`EB 0A 90`, `EB 04 90`), so
  they belong to the padding class.
- `49f0:0004` (42 B) - `r = h1(a); if (b && !(h2(r) + 1)) r = -1; return r;`
  matches structurally; the original pushes the *stale AX* copy of `r` for the
  second call and assigns `-1` through AX, while MSC 7 uses the SI copy
  throughout - the round-22 AX/SI staging difference.

Ledger 453 rows - MATCH 38, RELOCS 391, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 615 B (3.279 %)**.

## Round 52: tooling - nop-padded units ranked last (no new rows)
`tools/nextup.py` now recognises the nop-padding class (`EB <offset> 90`) and ranks
those units **behind everything else** instead of letting them head the list. They
are not hidden - they are still listed - but every one of them is guaranteed to
miss by one byte, so promoting winnable candidates is worth more than another
compile cycle on them.

Two candidates reached near-matches and both landed in known classes:

- `49e9:0002` (61 B) - `if (v < 0) h1(a, b, -v); else h2(a, b, v, 0);` with the
  long negation `F7 D8 83 D2 00 F7 DA` reproduced exactly; it misses only because
  the original pads its `jmp` with a `90` (`EB 14 90`).
- `3b2b:000c` (66 B) - a two-global guard
  (`g1760 = b; g1762 = a; if (h1(a,b)) return h4(a,b); if (h2(a,b)) return h3(a,b); g1762 = g1760 = 0; return -1;`)
  matches in every instruction; the older compiler merely hoists the `mov ax,[bp+08]`
  above the first store.
- `3bd3:0002` (52 B) - a range guard (`a >= 0 && a - 0x800 <= 0`) where the
  original uses `or ax,ax` / `sub ax,0x800` / `jo` on a once-loaded AX; MSC 7
  reloads and uses `cmp`/`jg` without the overflow guard.

`register int b` on `3b2b` was worth finding: it makes MSC load `b` into SI and
leave `a` in AX exactly as the original does, which reduced a whole-instruction
mismatch to one moved load.

Ledger 452 rows (unchanged this round); verify and checkled green; own-code
coverage 9 582 B (3.268 %).

## Round 51: a guarded four-argument relay (57 B)
`crelay56.c` (`/Os`): `3b72:0040` (57 B) -
`if (h4(a,b,c,d)) { f1(1); f2(); } h4b(g_17d2, c, 1); return c;`.
The guarded block is skipped by a single `jz` and the DGROUP-pointer call always
runs; this is the sibling of the round-20 `3b72:0002` relay, and the two rows
together cover the pair of functions that segment holds at those offsets.

Probed in the same band and blocked:

- `322c:002c` (43 B) - correct in structure but the temporary is pushed from AX
  right after the call and from SI later (`50 ... 56`), while MSC 7 pushes SI
  both times; the round-22 AX/SI scheduler difference again.
- `1dfc:0116` / `1e12:0006` and `2daa:001c` / `2dad:000c` stay blocked as recorded
  in round 50 (postponed cdecl cleanup; byte global pushed without extension).

Ledger 452 rows - MATCH 38, RELOCS 390, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 582 B (3.268 %)**.

## Round 50: milestone summary (no new rows, one artefact)
Fifty rounds in, the ledger stands at **451 rows** (MATCH 38, RELOCS 389, ASM 2,
PENDING 22) and **9 525 B of own code (3.249 %)** are byte-verified against MSC 7.
Every metric that matters has stayed green throughout: `verify.py` rebuilds and
re-matches every row on each run, `checkled.py` keeps the bookkeeping honest, and
no unverified increment has ever been committed.

The round's artefact is a **rules table in `docs/CONVENTIONS.md`** that collects the
eleven source-level rules earned since round 12, each with the example that
proved it and the round it was found (register staging, the fastcall tell, `__far`
vs `__near`, statement splitting, negated conditions, `default:` first,
unprototyped cleanup, the unused-`long` frame, single-use call results, Pascal
push order, moffs byte loads). It ends with the list of older-compiler artefacts
that no source formulation reaches, which is what `docs/BLOCKED.md` classifies.

Two probes this round, both blocked on scheduling rather than shape:

- `1dfc:0116` / `1e12:0006` (34 B each) - `h2(cd4(a, b, a, b))` with a cdecl
  four-argument callee. MSC 7 cleans the cdecl arguments with `83 C4 08`
  immediately after the call; the original postpones the same `add sp,8` until
  after the following call. Everything else matches.
- `2daa:001c` / `2dad:000c` (32 B) - a byte global pushed without sign extension.

`docs/BLOCKED.md` regenerated: 1 425 unmatched units, of which 237 (26 KB) are
mid-routine fragments that can never be functions.

Ledger 451 rows (unchanged this round); verify and checkled green.

## Round 49: a fastcall tail and a long sum (76 B)
`crelay55.c` (`/Os`), two rows:

- `3bfc:0004` (38 B) - `r = h1(); h4(a, b, 0, 0); return h2(r);`. The tail call
  is **`__fastcall`**: `8B C6` loads the argument into AX immediately before the
  far call with no push. This is the third distinct way the same tell has paid off
  (rounds 20, 37 and here) - a value moved into AX right before a call is an
  argument, never a leftover.
- `2a43:0004` (38 B) - `h6(a + b, c, d, e, g);`: two long parameters summed with
  `03`/`13` (add/adc) and the result pushed as the first argument (high word
  first), followed by four ints.

Ledger 451 rows - MATCH 38, RELOCS 389, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 525 B (3.249 %)**.

## Round 48: a nested two-argument relay (27 B)
`crelay54.c` (`/Os`): `388d:0006` (27 B) - `h2b(h2(a, a), 0);`, the inner call's
result serving as the outer first argument, with the parameter `register` so both
uses push SI and the result arrives in AX with no staging.

Probed and blocked, both by named classes:

- `1270:000e` (22 B) - `fc0(); if (g_4abf) fc1();`. Caching the byte in a local
  (`c = g_4abf; if (c)`) reproduces the original instruction pair exactly
  (`A0 <disp>` + `0A C0` instead of `80 3E <disp> 00`), but the original also has
  a `55 8B EC` / `5D` frame although the function has no locals and no
  parameters - MSC 7 only emits a frame when it must, so this stays
  generation-blocked even though the interesting part is matched.
- `2daa:001c` (32 B) - a byte global pushed without sign extension (`A0 <disp>` +
  `50`), the same odd idiom as `2127:000c`.

`reuse.py` reports no siblings after the row.

Ledger 449 rows - MATCH 38, RELOCS 387, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 449 B (3.223 %)**.

## Round 47: a four-case switch (93 B) and the `default:`-first rule
`crelay53.c` (`/Os`): `1f5f:0000` (93 B) - a `switch` on the fourth parameter whose
four cases return the callee's long result and whose default builds
`((long)a << 16) | (unsigned)b` (`8B 46 0A` / `8B 56 0C`).

**New rule (recorded in `docs/CONVENTIONS.md`):** the `default:` clause must be
written **first** in the switch. Written last, MSC 7 emits the default block after
the case blocks and every branch distance shifts; written first, the default
lands directly after the compare chain exactly as the original does. That single
reordering turned a 12-byte mismatch into a match.

This is the fourth source-level layout rule found in four rounds, together with:
negated branch conditions (round 45), separate statements for accumulation and
for divide-plus-offset (round 46), and no variable for a call result that is only
tested once (round 45).

Ledger 448 rows - MATCH 38, RELOCS 386, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 422 B (3.213 %)**.

## Round 46: a running sum with a signed divide (78 B)
`crelay52.c` (`/Os`): `5155:000a` (78 B) -
`t = g1(nc(a)); t += g1(nc(b)); t += g1(nc(c)); t = t / 3; t = t + 5; return (unsigned char)h1(t);`.
Three call pairs accumulate into one register, then a signed divide (`99 F7 F9`)
and a byte-truncated return (`2A E4`).

**Two source-level rules, both found by iteration:**
1. the accumulation must be **separate statements** (`t += g1(nc(b));`), not one
   sum expression - the expression form makes MSC evaluate the operands right to
   left, so the pushes come out in reverse parameter order;
2. the divide and the offset must likewise be **separate statements**: the
   combined `t / 3 + 5` loads AX before CX and folds the `+ 5` into the
   accumulator (`05 05 00`), while the split form matches the original
   (`B9 03 00` then `8B C6`, and `8B F0 83 C6 05`).

Also confirmed again that a callee the original reaches through the /F-translated
`90 0E E8` form must be declared `__far` - declaring it `__near` produced a
3-byte `E8` call and shifted everything after it.

Sizes are read from the object symbol (78 here); my hand count said 71 and
`verify.py` caught it again.

Ledger 447 rows - MATCH 38, RELOCS 385, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 329 B (3.182 %)**.

## Round 45: the nop-padding class (0 new rows, one byte twice)
Two large candidates came within **one byte** this round, and both for the same
reason:

- `3b88:000e` (119 B) - a nested guard
  (`if (h4(...)) { if (!h2b(2,0)) { h3(a,b,1); hh(g_18ba,-1); } else { ... } } h4b(g_17d2,c,1); return c;`)
  now matches down to a single `jz` distance byte.
- `4998:000c` (112 B, round 43) - the same story at its `jmp`.

The cause is recorded in `docs/CONVENTIONS.md`: the original pads a short jump
with a `90` (`B8 01 00 EB 03 90 33 C0`) while MSC 7 does not, so every following
branch distance grows by one even though the code is equivalent. A new
`nop-padded branch` trait was added to `tools/classify.py` (narrow forms only -
the padding also appears as `EB 23 90`, so the class is not complete).

Structural lessons from `3b88:000e` worth keeping:
- the branch condition must be written **negated** (`if (!h2b(2, 0))`) for the
  then-block to be laid out first with a `jnz` over it - the positive form emits
  the mirror layout;
- a call result used only once in a condition must **not** get a variable, or MSC
  pushes DI as well and the prologue grows by two bytes.

`docs/BLOCKED.md` regenerated: unclassified down to **241 units / 16 231 B**.

Ledger 446 rows (unchanged); verify and checkled green; own-code coverage
9 251 B (3.155 %).

## Round 44: a fastcall chain and an init unit (120 B)
`crelay51.c` (`/Os`), two rows:

- `3e15:0000` (66 B) - `f1(1); f2(a); f3(b); f4(c); if (d >= 0 && a == 1) f5(d, -1, -1);`
  with four **`__fastcall`** relays (argument in AX, no push: `B8 01 00`, `8B C6`,
  `8B 46 0A`, `8B 46 08`) and the first parameter `register` so it reloads from SI.
- `1ec4:00ae` (54 B) - `if (g_466e) h1(); g_466a = v; h2(); h3(0x0871, 0x6614); g_466e = 1;`
  (the leading function of an 81-byte unit).

Both needed one correction each, and both corrections are the same lesson:
- the stored value is **1**, not 0x100 - reading the immediate from the *hex
  dump* (`C7 06 6E 46 01 00`) as 0x0100 instead of little-endian is a classic slip;
- the row size must come from the object symbol: 54, not the 45 or 55 I counted
  by hand (fourth time this has bitten; `verify.py` caught it every time).

Ledger 446 rows - MATCH 38, RELOCS 384, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 251 B (3.155 %)**.

## Round 43: the biggest single row in twenty rounds (77 B)
`crelay50.c` (`/Os`): `3ba3:0006` (77 B) -
`r = h4(a, b, c, d); h4b(g_17d2, c, 1); if (r) { h1(1); h2(); h4c(h3(g_98e4)); } return c;`.
The third parameter must be `register` (pushed from SI twice, and returned from
SI at the end), the first call's result lives in DI, and two DGROUP object
pointers appear as `1E 68 <disp>` pairs. This is the same family as the round-20
`3b72:0002` guarded relay, one nesting level deeper.

Two near-misses recorded:

- `4998:000c` (112 B) - a two-branch relay that matches for 111 of 112 bytes: the
  original emits an extra `90` between a short jump and `xor ax,ax`
  (`B8 01 00 EB 03 90 33 C0`), which shifts both branch distances by one. Writing
  the else-form of the same source changes nothing, so that padding byte is an
  artifact of the older compiler.
- `3e4f:003a` and `2f3f:0006` are units whose first function is already verified;
  `nextup.py` no longer lists them because it now excludes claimed units
  correctly (round 42 fix).

`tools/nextup.py` produced the candidate for this round directly - the first time
the ranking tool has been used end to end.

Ledger 444 rows - MATCH 38, RELOCS 382, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 131 B (3.114 %)**.

## Round 42: tools/nextup.py, a 442-unit accounting error fixed, one row (29 B)
**New tool `tools/nextup.py`** replaces the ten ad-hoc scan scripts used in
rounds 12-40: it skips claimed units, CRT, fragments and every `classify.py`
trait, then ranks the rest by "translated calls minus conditional branches" so
the straight-line relays that keep turning into rows come first.

Building it exposed a **bug in `classify.py` itself**: it passed `re.M` as the
*pos* argument of `Pattern.finditer`, which silently matched nothing, so the
"already claimed" set was empty. Every `BLOCKED.md` produced since round 24
counted already verified rows as unmatched. With the bug fixed the real numbers
are:

| | before (wrong) | now |
|---|---|---|
| unmatched units | 1 796 | **1 433** |
| unclassified candidates | 516 units / 25 427 B | **254 units / 17 098 B** |
| fragments | 339 units / 27 814 B | 237 units / 26 163 B |

So the honest remaining C-transcribable pool is **17 KB**, not 25 KB - the
decompilation is further along than the map suggested.

The round's row: `crelay49.c` (`/Os`) `2d3a:0002` (29 B) - `h1(c, d); h2(a, b);`,
two two-argument far relays back to back.

Also extended the register-pair trait to `C4 76` / `C4 7E` (far pointer in
ES:SI/ES:DI), which correctly classifies `2d6f:002a`.

Ledger 443 rows - MATCH 38, RELOCS 381, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 053 B (3.088 %)**.

## Round 41: a negated six-argument call (29 B)
`crelay48.c` (`/Os`): `3e7f:0118` (29 B) - `return 1 - h6(a, b, 1, 0x10, g_98e4);`.
The negation is `48 F7 D8` (`dec ax` / `neg ax`), the DGROUP object pointer is
the last argument (`1E 68 <disp>`), and the two parameters are pushed before the
two constants.

Probed and blocked in the same band, all by already-documented traits:

- `21fd:0006` (30 B) and `3ea9:005a` (29 B) - `8E 06 <disp>` (`mov es,[seg]`):
  the inlined-`MK_FP` class.
- `3dd8:0000` (29 B) - `8E C0` right after an argument push: same class, segment
  from a parameter.
- `29e9:000a`, `2a28:0000`, `3a3d:0006`, `4b6a:0056` - register allocation and
  operand-order cases from rounds 39-40.

Sweeps after the row: `reuse.py` reports no siblings.

Ledger 442 rows - MATCH 38, RELOCS 380, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 025 B (3.078 %)**.

## Round 40: two DGROUP pointers relayed and one returned (28 B)
`crelay47.c` (`/Os`): `2183:0008` (28 B) - `h3(x, g_10d8, g_6cf6); return g_6cf6;`
in a near-Pascal function. Both object pointers are pushed as `1E 68 <disp>`
pairs, and the returned pointer is built with `B8 <disp>` plus `8C DA` (offset in
AX, data segment in DX) - the far-pointer return convention.

Three further candidates probed and classified this round:

- `29e9:000a` (28 B) - a list walk keeping the node in ES:BX (`26 C4 1F`,
  `26 0B 57 02`): the far-pointer-in-registers class.
- `3a3d:0006` (28 B) - the pointer parameter lands in **DI** (single register
  parameter), i.e. the reversed register-parameter assignment.
- `4b6a:0056` (28 B) - a table walk through a global far pointer loaded with
  `C4 1E <disp>`; the addressing is reproducible but the index scaling and
  operand order are the older optimiser's.

Sweeps after the row landed: `reuse.py` and `classify.py` report nothing new.

Ledger 441 rows - MATCH 38, RELOCS 379, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **8 996 B (3.068 %)**.

## Round 39: a far-pointer base in ES:BX (46 B) and the DX/BX allocation class
`crelay46.c` (`/Os`): `37fc:000e` (46 B) - `h1(nc2(nc(n, n)->f4)); h2(n); h3(n);`
in a near-Pascal function. The far pointer returned by the first call is used
directly as a struct base and stays in ES:BX; introducing a local for it makes
MSC 7 switch to an `ENTER` frame, so the working formulation is one nested
expression.

**New class: DX/BX register allocation.** `2a28:0000` and `2a28:...`-style clamps
(`if (b > a) return a; if (c < a) a = c; return a;`, 28 B, signed and unsigned
twins `2a28:0000` / `2a29:000c`) show the original keeping `a` in **DX** and `b` in
**BX** (`8B 56 0A` / `8B 5E 08` / `3B DA`), while MSC 7 addresses both from the
frame (`8B 46 0A` / `39 46 08`). `/Ox`, `/Ot` and `/Os` all give the frame form,
so this is the older compiler's optimiser choosing DX/BX, not a flag.

`37ef:000c` (29 B) was also probed: a bit-clear in a 0x34-byte record table
(`6B 5E 06 34`, `21 87 36 6E`); MSC 7 reproduces the addressing but keeps the
operands in a different order, same class.

Ledger 440 rows - MATCH 38, RELOCS 378, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 968 B (3.059 %).

## Round 38: a sibling pair (67 B) and the argument-evaluation-order class
Two rows, both from re-using verified shapes:

- `2dbb:0000` (36 B) - a sibling of the round-13 `2d97:001e`
  (`fc1(a); fc3(g_1bee, g_1bec, 0x1BE8); fc0();`, DGROUP pointer at `1A0C`);
- `2a0f:002e` (31 B) - a sibling of the round-34 `2a0f:000e` (`F_2A0F`), found by
  `tools/reuse.py` immediately after the first row landed.

Both sweeps were run after adding them; `reuse.py` yielded the second row and
`probe.py` reported nothing new beyond a row that was already in the ledger.

**New class identified: argument evaluation order.** `31dd:0008` (27 B) is
`h1(fc2(a, fc0()))`: the original evaluates the **second** argument first
(`90 0E E8` before `FF 76 06`), MSC 7 pushes `a` and then evaluates `fc0()`. With
no local in the original there is no source formulation that makes MSC 7 evaluate
right to left, so this is a compiler difference, not a shape problem.

Ledger 439 rows - MATCH 38, RELOCS 377, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **8 922 B (3.043 %)**.

## Round 37: two straight-line relays (93 B) - own-code coverage crosses 3 %
`crelay45.c` (`/Os`):

- `2f3f:0006` (38 B) - `g_1c36 = h5(g_1c36, x, 0, g_1c48);`: the long global is
  pushed as two words (high word first), then the ints, and the long result is
  stored back with `A3` / `89 16`.
- `3e4f:003a` (55 B) - six calls in a row, of which the first two are
  **`__fastcall`** (argument in AX, no push: `B8 23 00` and `8B 46 06`), then two
  no-argument calls, a one-argument push and a three-argument far call.

The first attempt at `3e4f:003a` failed because I wrote the second call as
`h2(a)` (Pascal) - the argument in AX with no push is the tell for `__fastcall`
(same rule as round 20's `3b6e:0002`).

Also probed: `3da5:000a` (67 B) differs only in `2B C0` versus `33 C0` - the
pre-MSC6 zero idiom again, third sighting.

Process note (third time): the row size must be read from the object symbol, not
counted by hand from the hex dump - I guessed 52 for `3e4f:003a` and `verify.py`
caught it (real size 55).

Ledger 437 rows - MATCH 38, RELOCS 375, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **8 855 B (3.020 %)** - past 3 % of our own bytes.

## Round 36: two far stores of one result (36 B) and the register-parameter reversal
`crelay44.c` (`/Os`): `388d:0022` (36 B) - `*a = h(x); *b = h(x);`, two
far-pointer stores of the same call result with the argument in a register.

**Register-parameter assignment is reversed in the original, now proven.** A
direct compile shows MSC 7 keeping the first declared `register` parameter in SI
and the second in DI (`8B 76 0C` / `8B 7E 0A` for
`(register int a, register int b, int c, int d)`); the original `3ae7:0000` has
the same two values in the **other** registers. This is the mechanism behind the
`20f9:000c` puzzle from round 12 and behind `218f:0004` / `2191:0008`, so all
four are now classified with known source shapes rather than "unexplained".
Recorded in `docs/CONVENTIONS.md`.

Three more candidates probed this round:

- `223e:0004` (32 B) - `8E 46 08` (segment half of a far pointer loaded
  separately): the split-far-pointer class.
- `2f3d:0008` (30 B) - `26 A3` (ES-absolute store): the ES-absolute class.
- `322c:002c` (43 B) - correct except `50` vs `56` (the temporary pushed from AX
  in the original, from SI in MSC 7), the same scheduler difference as
  `3e34:000a`.

Also confirmed the straight-line relay filter (no conditional jumps, two or more
translated calls) is a good candidate source: it produced 26 units, of which one
matched and the rest fell into four named classes.

Ledger 435 rows - MATCH 38, RELOCS 373, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 762 B (2.988 %).

## Round 35: a nested relay (34 B) and the `or reg,ax` peephole pinned down
`crelay43.c` (`/Os`): `3a4a:0052` (34 B) - `h1(h1(h3(a, a, b)))`, three calls
nested through AX with the first parameter in a register (pushed from SI twice).

**The most frequent remaining one-byte blocker is now named and documented.**
Four candidates this round were perfect except for a single byte, all with the
same cause: when a call result is compared, the original writes
`8B F0 0B F0` (`mov si,ax; or si,ax`) - it ORs the register with **AX** even
though the value has just been moved out of AX - while MSC 7 emits `or si,si`.
Recorded in `docs/CONVENTIONS.md` as the `or reg,ax` peephole, because it now
accounts for `4690:0000`, `31cd:0006`, `2b9a:0000` and the `or ax,di` cases
(`1f72:0044`, `1f7c:0008`).

Other candidates probed and classified:

- `218f:0004` / `2191:0008` (36 B) - the original puts the first parameter in
  **DI** and the second in **SI** (MSC 7 does the opposite), the same register-role
  reversal as `20f9:000c`; the source shape is recorded.
- `1233:000e` (34 B) - an indirect far call through a global (`FF 1E`); with `/G0`
  every instruction matches (`B8 FC 00 50` constant pushes, the `FF 1E` call) but
  the original keeps a `55 8B EC` / `8B E5 5D` frame although the function has no
  locals, which this compiler only emits when a frame is otherwise needed.
- `41d8:000c` (30 B) - `03 F6` (`add si,si`): trait-1, ASM-only.

Ledger 434 rows - MATCH 38, RELOCS 372, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 726 B (2.976 %).

## Round 34: two small relays (62 B) from the candidate pool
`crelay42.c` (`/Os`):

- `2a0f:000e` (31 B) - `h1l(h4l(a, b, c, d))`: a four-argument call whose long
  result is pushed straight into the next call (`52 50`).
- `3891:0006` (31 B) - `h1i(h3i(a, b, a) * c)`: the first parameter is `register`
  (pushed from SI twice) and the multiplier is the **last** parameter, which is
  why `F7 6E 06` reads it from the frame.

Three more candidates probed and classified:

- `2216:000a` (31 B) - correct except the CX staging pattern again
  (`8B 4E 06` + `0B C9` + `51`): compare-then-push goes through CX in the
  original, through memory in MSC 7.
- `41d8:000c` (30 B) - differs only in `03 F6` (`add si,si`) where MSC 7 emits
  `D1 E6`, so it is the same trait-1 shape as the `add bx,bx` probes: ASM-only.
  The classification predicate only listed `03 C0/C6/C9/D2/DB/ED/FF`, so `03 F6`
  and `03 E4` were added; no unit moved, because `41d8:000c` is already counted
  by an earlier predicate - the map is stable, the predicate is just complete now.

Ledger 433 rows - MATCH 38, RELOCS 371, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 692 B (2.964 %).

## Round 33: a triple relay (30 B) and the fragment discovery
`crelay41.c` (`/Os`): `31f1:0002` (30 B) - `h1(a); h2(a); h3(a);` with a
`register` parameter, so the value is pushed from SI three times instead of being
reloaded from the frame each time.

**The candidate pool was over-counted, and now is not.** `tools/classify.py` has a
new class *"fragment (no prologue)"*: **339 units / 27 814 bytes** are inventory
windows that do not even start with a function prologue, so they began in the
middle of a routine and can never be matched as functions. With that class (and
the broadened jump-merge and MK_FP predicates from rounds 31-33) the honest
candidate bucket - "unclassified" - is down from 922 units / 50 096 bytes at
round 24 to **516 units / 25 427 bytes**.

**Six-unit family narrowed to one byte.** `3dde:0006`, `3de0:0004`, `3de4:000c`,
`3de6:000a`, `3de8:0022` and `3dec:0000` (30 B each) are one shape:
`void f(unsigned seg, register int off) { hh(seg, off, *(unsigned __far *)MK_FP(seg, off + 2) + 1); }`.
MSC 7 reproduces every instruction except that the original inlines the far
access (`8B 46 08` + `8E C0` + `26 8B 44 02`) while MSC 7 calls the `MK_FP`
helper (`83 C4 04`, `99`, `8B D8`, `8E C2`). So the "inlined MK_FP" class now
covers **parameter** segments too, not just globals, and its predicate was
broadened to `8E 06` / `8E C0`.

Ledger 431 rows - MATCH 38, RELOCS 369, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 630 B (2.944 %).

## Round 32: inner functions of large units (1 row, 12 B)
Large inventory "units" usually contain **several functions**: a 248-byte unit can
be one 65-byte function followed by further code. `tools/probe.py` now enumerates
every window inside an unmatched unit that starts at 0 or at a return and ends at
a later return, and sweeps those windows against the probe library too. That
found `3670:00e2` (12 B, the `cfarl2.c` relay symbol) buried inside a larger unit.

The first attempt at this shape was also instructive, even though it did not
land: `2d08:007a`'s leading function matched byte for byte over its first 40
bytes, but the full 65-byte function differs at one instruction - the original
zeroes AX with `2B C0` (`sub ax,ax`) where MSC 7 emits `33 C0`. So that unit is
pre-MSC6 in exactly one instruction and the row was dropped rather than resized
(verify's window check caught both mistakes: the truncated size and the
regression).

Ledger 430 rows - MATCH 38, RELOCS 368, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 600 B (2.933 %).

## Round 31: `_based` ruled out, map sharpened again (0 new rows)
The round targeted the biggest new class from round 30, "ES from global"
(`8E 06 <disp>` plus ES-relative access, the original's inline
`MK_FP(variable_segment, off)`). Two formulations were tried:

- `__based(...)` - **rejected by CL 8.00** in every spelling except
  `int _based(b) *p;` where `b` is a *near pointer* variable; that form compiles
  but emits `push si; mov bx,[b]; mov si,[b2]; mov word ptr [bx],1`, i.e. no
  ES-relative access at all. So Microsoft's based-pointer feature does **not**
  explain the original's `8E 06` idiom - the hypothesis is ruled out, not just
  unproven.
- a plain `strncpy`-style loop for `10d3:0022` (42 B): the original is a
  hand-optimised `lodsb`/`stosb`/`loop` + `rep stosb` walk, which MSC 7 never
  emits for a C pointer loop (it addresses through `26 8A 07` / `26 88 07` and
  keeps the pointers in the frame).

Map improvements in `tools/classify.py`:

- the jump-merge predicate was too narrow (it only looked for `EB 03 B8 01 00`
  and `EB 02 33 C0`); it now also catches `33 C0 EB` and `99 EB`, which took that
  class from 32 to **94 units / 9 533 bytes**;
- new class "string walk (`lodsb`/`stosb`/`loop`)" - 3 units, 691 bytes.

`docs/BLOCKED.md` regenerated: 14 classes, unclassified down to
**819 units / 40 595 bytes** (from 922 / 50 096 at round 24).

Ledger 429 rows - MATCH 38, RELOCS 367, ASM 2, PENDING 22 (unchanged); verify and
checkled green; own-code coverage 8 588 B (2.929 %).

## Round 30: two more classes mapped, unclassified down to 44 KB (0 new rows)
Three transcription attempts landed on generation-specific codegen, so the round
went into the map instead:

- `1b17:0002` (75 B) - `long f(struct N __far *p)` with a list-maximum loop.
  Everything matches except that the original loads the pointer **once into
  DS:BX** (`C5 5E 04`) and tests it with `mov ax,ds; or ax,bx`, while MSC 7 keeps
  it in the stack frame and reloads `C4 5E 04` each iteration. `register` on a far
  pointer parameter changes nothing.
- `1b74:000e` (68 B) and the earlier `3141:0002` - `MK_FP(variable_segment, off)`
  with a field access. The original inlines it as `8E 06 <disp>` (`mov es,[g]`)
  plus `26 <op> 44/47 xx`; MSC 7 calls the `MK_FP` helper and then does
  `mov es,dx`. Source shape is settled for both:
  `long f(int a, int b) { long r = h3(a,b,0); if (r == 0) return 0; ((struct P __far *)MK_FP(g_97dc, nc2(a,b)))->n++; return r; }`.

New blocker classes in `tools/classify.py`:

| class | units | bytes |
|---|---|---|
| ES from global (`8E 06`, inlined `MK_FP`) | 69 | 7 927 |
| far pointer in DS:BX (`C5 5E`/`C5 5F`) | 7 | 749 |

`docs/BLOCKED.md` regenerated: 13 classes, and the "unclassified" bucket - the
only place new rows can still come from - is down from 922 units / 50 096 bytes
(round 24) to **859 units / 44 452 bytes**.

Ledger 429 rows - MATCH 38, RELOCS 367, ASM 2, PENDING 22 (unchanged); verify and
checkled green; own-code coverage 8 588 B (2.929 %).

## Round 29: a flag-guarded cdecl relay (42 B) and a build hazard
`crelay39.c` (flags `/G0 /AM /Gs /Os`): `13ad:000a` (42 B) -
`long r; g_5284 = 1; r = h6(a,b,c,d,e,f); g_5284 = 0;`. Three details decide it:

- the callee is **cdecl**, so the six arguments are pushed right to left and the
  caller does not pop them (the epilogue is a bare `retf`);
- the build is **/G0**, which gives the `8B E5 5D` epilogue instead of `leave`;
- the never-read **`long` local** is what reserves the four bytes behind the
  initial `83 EC 04` - removing it loses the `sub sp,4` entirely.

**Build hazard found (cost half an hour):** the first version of the file had
this comment: `the build is **/G0** (the epilogue ...)`. The `**/` in `**/G0**`
closes the comment early, so `G0** (the epilogue...` was parsed as C. The compiler
aborted *silently* - no object, no `CL.TXT` log - which looks exactly like the
known MSC 7 crash class. Rule for the calibration sources: never write a
`/`-flag immediately before a `*` inside a comment; keep flags unadorned
(`G0`, not `/G0`) or outside `**` emphasis.

Ledger 429 rows - MATCH 38, RELOCS 367, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 588 B (2.929 %).

## Round 28: an unprototyped call (41 B) and the CX-staging class
`crelay38.c` (`/Os`): `1fc8:0074` (41 B) -
`if (h(a, 0, 0) == -1L) h2(g_013a, 0x4F);`. The callee is **unprototyped**, and
that is what makes MSC clean the arguments with `mov sp,bp` (`8B E5`) instead of
`add sp,6`; the long comparison against -1 is `3D FFFF` / `3B D0`.

**New blocker class found and added to `tools/classify.py`:** *CX-staged value*
(14 units, 993 bytes). The original compiler loads a value into **CX** when it is
both compared and then pushed (`8B 4E xx` once, then `cmp cx,..` / `or ch,..` /
`push cx`); MSC 7 compares from memory and pushes the stack slot again. This is
the same mechanism that blocked `1f72:0044`, `1f7c:0008` and `37a8:0008`.

That also closed `2061:0008` down to a single demonstrated difference:
declaring the parameter **unsigned** turns `7D` (`jge`) into the original's `73`
(`jae`), leaving only the CX staging (`8B 4E 08` + `81 F9` + `80 CD 80` + `51`)
between our output and the original.

`docs/BLOCKED.md` regenerated: 11 classes, unclassified down from 922 to 909
units (50 096 -> 49 227 bytes).

Ledger 428 rows - MATCH 38, RELOCS 366, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 546 B (2.915 %).

## Round 27: wildcard every fixup site (2 C rows, 1 ASM reclassification)
`tools/probe.py` now builds each probe symbol's pattern by masking **every
FIXUPP site** it finds in the object (2 or 4 bytes), not just the call-target
shapes its normaliser knew about. Two instances of a shape that differ only in
their relocated operands - call targets, global addresses, DGROUP pointers - now
compare equal, and `match.py` still confirms every hit, so a wildcard can never
produce a false row.

That found `3238:009c` (8 B, `_get_l`) and `3e34:0044` (7 B, `_init_234e`).

**Important guard added:** the first run also proposed RELOCS rows from
`src/calib/casm4.c`, which is an *inline-assembly* probe (`__asm add bx,bx` for
the `03 DB` scaling that MSC 7 never emits). Claiming those as `RELOCS` would
have smuggled ASM-derived evidence into C coverage, so `probe.py` now skips any
probe file containing `__asm` outright.

**PENDING -> ASM:** while checking that, `4fad:0006` turned up. It had been parked
as PENDING ("trait 1, not fixable from C"), but its bytes are identical to the
ASM-verified `35ca:2306` modulo the table address, so it is now an ASM row with
the same inline-assembly note. PENDING count 23 -> 22.

Ledger 427 rows - MATCH 38, RELOCS 365, ASM 2, PENDING 22; verify and checkled
green; own-code coverage 8 505 B (2.901 %).

## Round 26: four rows (137 B) from a masking gap in the sweep tools
The two 41-byte units `3d99:0004` and `416f:0042` turned out to be plain members
of the round-13 `36e7` family, already covered by `crelay25.c` - the sweeps had
missed them for **four rounds** because their normaliser did not mask the
relocated DGROUP far-pointer push. `1E 68 <disp16>` is a fixup site, exactly like
`9A seg off`, so patterns that differ only in that displacement were treated as
different shapes.

Fix: `tools/reuse.py` and `tools/probe.py` now mask `1E 68 xx xx` as well. The
re-run immediately produced:

- `3d99:0004` and `416f:0042` (41 B each) - `36e7` family members (pointer at
  `1B1A` / `2A88`);
- `416f:006c` (41 B) - a tenth `36e7` family member;
- `3b5e:0008` (14 B) - a `cfarl2.c` sibling.

Both sweeps are exhausted again afterwards (0 candidates each). Lesson recorded:
the pattern normaliser must mask **every** relocated operand form, and only
`90 0E E8`, `9A` and `E8` were on the list - `1E 68 <disp>` (DGROUP pointer),
`B8 <disp>` and `BE <disp>` (immediate symbol loads) are candidates for the same
treatment if another near-miss shows up.

Also filed as blocked this round (2 bytes each, source shapes settled):
`37a8:0008` and `37ab:0002` (42 B) - the original keeps the range value in DI and
the argument in **CX** (`8B 4E 04` once, then `3B F9` / `03 C1`), while MSC 7 puts
the register local in SI and reloads the argument from memory.

Ledger 425 rows - MATCH 38, RELOCS 363, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 8 501 B (2.899 %).

## Round 25: the 36e7 shape with a zero constant (41 B) - and a layout rule nailed down
`crelay37.c` (`/Os`): `509a:0042` (41 B) - `fc4(a, b, c, d); fc3(g_3970, c, 0); return c;`,
the round-13 `36e7` family shape with a **zero** constant instead of one.

**Pascal parameter layout, settled (this kept being mis-derived):**
1. arguments are pushed **left to right**, so the first argument is pushed first;
2. because the stack grows down, the **first** argument therefore sits at the
   *highest* offset: for a far function with four words, `a` is at `bp+0C`, `b` at
   `bp+0A`, `c` at `bp+08`, `d` at `bp+06` (a far return address occupies
   `bp+02`/`bp+04` before the arguments).
3. a `register` parameter keeps its declaration position but lives in a register:
   the first `register` parameter takes SI, the second DI.

Two near-misses this round, both two bytes from matching and both filed under
their class:

- `1f72:0044` and its sibling `1f7c:0008` (40 B each) - correct except that the
  original stages the first parameter in **CX** (`8B 4E 06` at the top, then
  `51`) and builds the test as `or ax,cx`; MSC 7 reloads from memory and ORs
  `[bp+08]`. Source shape settled:
  `long f(int a, int b) { if (b | a) { h2(b, a); g_46ec--; } return 0; }` (the
  trailing `83 2E <lo> 01` / `83 1E <hi> 00` pair is a 32-bit decrement, not the
  `and/sbb` idiom it looks like).
- `3877:0000` (41 B) - correct except the order in which the two register
  parameters are loaded into SI and DI: the original loads DI first.

`docs/BLOCKED.md` regenerated.

Ledger 421 rows - MATCH 38, RELOCS 359, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 8 353 B (2.849 %).

## Round 24: tools/classify.py - a map of what is left (0 new rows)
Three transcription attempts all landed on generation-specific codegen, so the
round produced `tools/classify.py` and `docs/BLOCKED.md` instead: every
unmatched whole function is sorted by the code-generation idiom that blocks it.
That turns "probe this unit and see" into "this unit is in class X, skip it"
and stops the next rounds from re-deriving the same dead ends.

The map (upper bound - segment aliases inflate the counts):

| class | units | bytes |
|---|---|---|
| `ENTER` frame | 589 | 85 535 |
| unclassified (real candidates) | 922 | 50 096 |
| `add reg,reg` doubling | 84 | 21 170 |
| split far-pointer load | 99 | 16 124 |
| jump-merge boolean | 32 | 3 219 |
| redundant `or reg,ax` | 20 | 1 727 |
| ES absolute access | 20 | 1 333 |
| `rep stosw` memset | 16 | 1 288 |
| AH argument | 6 | 928 |
| operand order | 8 | 732 |

The three near-misses from this round, each now filed under its class:

- `2b9a:0000` (46 B) - a polling loop, correct to two bytes: the original has
  `8B F0 0B F0` (`mov si,ax; or si,ax`) where MSC 7 emits `or si,si`
  ("redundant or reg,ax"). Source shape settled:
  `void f(int a) { register int t, d; d = a; do { t = fc0(); if (t >= 0) d = t; t = fc1(fc2(d, d)); } while (t == 0); }`
- `3141:0002` (47 B) - the double far dereference
  `*(struct V __far * __far *)MK_FP(g_61b4, 0x8E2)` compiles to `8E 06` +
  `26 C4 1E` in the original but MSC 7 calls the `MK_FP` helper instead.
- `437e:0032` (58 B) - `C1 E0 0B` / `C1 E6 02` bit assembler; not yet decoded
  far enough to write a source.

Ledger 420 rows - MATCH 38, RELOCS 358, ASM 1, PENDING 23 (unchanged); verify and
checkled green; own-code coverage 8 312 B (2.835 %).

## Round 23: tools/probe.py - the probe library is exhausted (0 new rows)
New tool `tools/probe.py` generalises `tools/reuse.py` from "unit the same length
as a verified row" to "unit the same length as **any calibration probe symbol**":
it loads every `src/calib/*.OBJ`, takes each public symbol's bytes (sized to the
next symbol), normalises call targets, and compares against every unmatched unit
in-process before confirming hits with `match.py`.

Result: **zero new rows**. Once its ledger parser was fixed it skipped every
candidate it found, and spot checks confirmed those units were already verified
in earlier rounds under their original symbols (`2b8e:0006` = RELAY_9326,
`3220:00a2` = RELAY_80A0, `2e35:0006` = SCAN256_A, `4e6f:0006` = NESTED_PTR, ...).
So the 120-file calibration library has been fully exploited: no unmatched unit
in the image reproduces a probe shape.

Three bugs in the new tool were found and fixed, all worth remembering:
1. `omfdump.load()` returns `(list_of_ledata_dicts, pubdefs_dict)`, not raw byte
   blobs - the first version crashed on it;
2. the ledger rows have **five** columns (`va | name | size | status | note`), so
   a `len(cols) < 6` guard silently skipped every row and left the "already
   claimed" set empty - which produced 57 alias duplicates;
3. a unit window can be one byte longer than the function, so the row size must
   be the *symbol* length, not the unit size.

`verify.py`'s DUP check and `checkled.py`'s unattested-source check caught all of
this (three times now for the DUP class), so the safety net is holding: a bad
sweep cannot land in the ledger silently.

Ledger 420 rows - MATCH 38, RELOCS 358, ASM 1, PENDING 23 (unchanged); verify and
checkled green; own-code coverage 8 312 B (2.835 %).

## Round 22: a counter guard (62 B) and the argument-push order confirmed
`crelay35.c` (`/Os`): `505f:000e` (62 B, near Pascal) -
`t = n + g_395e; if (p3(1, 0x64, 2) > t) { g_395e++; if (fc(4) != -1) g_395e++; return 0; } g_395e = 0; return 1;`.
Both returns share one epilogue, so the compiler keeps a single return block.

**Confirmed rule:** Pascal arguments are pushed **left to right**, so the literal
order in the source is literally the byte order of the pushes
(`6A 01 6A 64 6A 02` = `p3(1, 0x64, 2)`). Getting the literals backwards was the
only difference in the first attempt, and the same rule fixed the `3d94:0010`
parameter order in round 21.

Probed and generation-blocked (identical everywhere except one instruction):

- `3e34:000a` (58 B) matches byte for byte up to +0x18, where the original
  pushes the temporary from **AX** (`50`) after saving it to SI (`8B F0`), while
  MSC 7 always pushes it from SI (`56`). Source shape is settled
  (`f1(8); t = p2(0x0F, 0x4000); p5(t, a, b, 0, 1); f1(t); g_1bb8 = 0;`), so only
  the older scheduler can reproduce it.
- `2d6f:002a` needs the far pointer itself in SI (`C4 76 08`) and the loaded word
  in BX; MSC 7 always uses BX for the pointer.

Ledger 420 rows - MATCH 38, RELOCS 358, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 8 312 B (2.835 %).

## Round 21: a loop with two register variables and a five-argument chain (116 B)
`crelay34.c` (`/Os`):

- `416b:0006` (58 B) - a six-iteration loop
  `d = fc0(); for (i = 0; i < 6; i++) if (h1(i) >= 0 && (flags & 0x20)) { fc2(-1 - i, 0); d++; }`.
  Both locals must be `register`: with plain locals MSC switches to an `ENTER`
  frame; as register variables the index lands in SI (`33 F6`, `46`) and the
  counter in DI (`47`, `8B C7`), which is the original.
- `3d94:0010` (58 B) - `h1(g_78c4); h2(g_78c4, 0, 0); h5(g_78c4, a, b, 0x400, 1); h1(g_78c4);`
  in a **near**-Pascal function (`C9 C2 04 00`), with the 0x400 constant pushed
  as imm16. The two parameter pushes are the first-declared then the
  second-declared, so getting them backwards shifts both bytes.

Also closed for good this round: `20f9:000c` and `2b25:0048` both need the OR/compare
operand loaded from memory *before* the register operand (`8B 46 08 0B C7`), while
MSC 7 canonicalises to register-first (`8B C7 0B 46 08`). That is an operand-order
difference between compiler generations, not a source shape - the same class as
the jump-merge booleans.

Ledger 419 rows - MATCH 38, RELOCS 357, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 8 250 B (2.814 %).

## Round 20: a guarded relay pair (125 B) with a fastcall signature
`crelay33.c` (`/Os`), two members of one shape:

- `3b72:0002` (61 B) - `r = fc4(a, b, c, d); fc4b(g_17d2, c, 1); if (r) { h1(1); h2(); } return c;`
  with the third parameter `register` (so it is pushed from SI four times) and
  the DGROUP far pointer argument emitted as `1E 68 <disp>`.
- `3b6e:0002` (64 B) - the same shape, but the branch's second call passes a
  **constant to a `__fastcall` callee**: `B8 24 00` loads AX and the call
  follows with no push. Declaring that callee Pascal instead produces `6A 24` +
  push and shifts the whole tail by two bytes.

That is the first place where the *calling convention of a callee* (not the
caller) is what the byte pattern encodes: an argument in AX with no push can
only be `__fastcall`, and the repository already resolves `@`-prefixed
`__fastcall` symbols in `match.py` for exactly this case.

Ledger 417 rows - MATCH 38, RELOCS 355, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 8 134 B (2.774 %).

## Round 19: two long call chains (113 B) with a shared rule
`crelay32.c` (`/Os`):

- `3e4f:008c` (54 B) - `fc0(); t = h1(1); h5(a, b, g_1bba); h3(t); return fc2(c, 0);`.
  Two details decide it: the temporary is assigned *after* a discarded call
  (assigning it to the first call puts `8B F0` in the wrong place), and the
  three pushes `a`, `b`, `g_1bba` belong to **one** three-argument call, not to
  two calls (splitting them breaks the match at +0x18).
- `31f6:000c` (59 B) - eight calls in a row:
  `fc3(h1b(a, a)); h2(a, 2); h1(a); h4(a, 3); fc0(); return fc3(0);`.

**Rule confirmed for the third time:** the parameter must be `register`. With a
plain parameter MSC emits `FF 76 06` (push memory) for every use; with
`register int a` it emits `8B 76 06` once and `56` (push si) afterwards, which
is exactly the original. The same rule produced `JSON`-style staging in rounds
12, 13 and here - it is the single most reusable source-level lever found so
far for this band.

Ledger 415 rows - MATCH 38, RELOCS 353, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 8 009 B (2.731 %).

## Round 18: the smallest units (3 rows, 22 B) and two source rules
Walking the remainder of the sub-30-byte pool for units that actually end at a
return turned up three that are worth keeping:

- `crelay31.c`: `1270:000c` (1 B) - an **empty far function** is exactly `CB`,
  the smallest possible verified row;
- `1534:02a5` (5 B) - `return g_0004;`: a byte global read uses the moffs form
  `A0 <disp>` plus `cbw`, **and the function must be `__near`** - `__far` would
  end in `CB` instead of the original's `C3`;
- `48d6:010a` (16 B) - `g_234a = -1; fsub(g_9b40);`, an immediate store
  followed by a global pushed into a far call that stays `9A` in the image.

Probed and left open, all blocked by the older generation rather than by source
shape:

- `1a20:0002` needs the inline `memset` to use `rep stosw` (`F3 AB`, 9 words);
  with `/Oi` MSC 7 emits `rep stosb` with 18 bytes, and without `/Oi` it calls
  `memset`.
- `4d98:000a` needs `(a + b) & 3` computed in DX with word ops; MSC 7 always
  uses the byte form (`8A 46 06 / 02 46 08`) and `/Ot` does not change it.
- `3e5c:0006`, `48d6`-style boolean merges and the `B4`-argument DOS wrappers
  stay blocked for the same reason (jump-merge layout, `mov ah,imm` before a
  call).

Ledger 413 rows - MATCH 38, RELOCS 351, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 7 896 B (2.693 %).

## Round 17: tools/reuse.py - and a lesson about segment aliases (4 rows, 122 B)
New tool `tools/reuse.py`: every verified row is reduced to a **normalised byte
pattern** (all direct call targets masked) keyed by length, and every unmatched
unit is normalised the same way. An exact pattern match plus equal length makes
the unit a *sibling* of that row; `match.py` then confirms it before anything is
written. This automates the manual discovery of the round-13 `36e7` family.

First run reported 38 "candidate siblings", but only four were real:

- `2e55:003c` (23 B) - another `F_2E55` sibling;
- `31d3:0004` and `31d3:0038` (29 B each) - more `F_31CF_08` siblings;
- `36e7:01bc` (41 B) - a seventh member of the `36e7` family.

**The other 34 were segment aliases**, not new functions: the inventory lists the
same code under two spellings (`458e:8650` and `4df2:0010`, linear 0x4DF30), so a
pattern match there re-finds an already verified row. `verify.py`'s linear-address
duplicate check caught this, and the sweep is now hardened: candidates whose
*linear* address is already claimed are skipped, after which it reports **zero**
candidates. So the sibling vein is exhausted - the remaining unmatched units are
genuinely different code.

Process notes from the same pass: 13 of the swept rows were plain `MATCH` rather
than `RELOCS` (no relocations in the window), so the status must come from
`match.py`, never assumed; and four rows had to be dropped as alias duplicates
before `verify.py` went green.

Ledger 410 rows - MATCH 37, RELOCS 349, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 7 874 B (2.685 %).

## Round 16: a five-call long chain and a guarded double call (143 B)
`crelay30.c` (`/Os`):

- `33c1:0006` and `33c4:0006` (48 B each) - five calls in a row:
  `h4(h3(c2(c1(-1), a))); return h5(1);`. Two rules decide the match:
  `h4`'s result must be **discarded** (a separate statement; folding it into one
  nested expression keeps the value and changes the pushes), and the wrapper
  must return **`int`** - declaring it `long` makes MSC insert a `cwd` before
  `leave`. The chain mixes longs (`c1` returns long, `c2` takes two longs) with
  an int argument/return at the ends.
- `48aa:0008` (47 B) - the same outer guard as `48ad:0008`, but the body calls
  twice (`fc0()` then `fc2(0, 1)`), which moves the `75 21` skip.

Process note: `match.py` accepted `33c1` at 47 bytes because that is a prefix
match; `verify.py`'s window check (window must end at a return) caught the
missing byte and the sizes were corrected to 48. Keeping that check strict is
worth the occasional round-trip - a prefix match alone would have put a wrong
size in the ledger.

Ledger 406 rows - MATCH 37, RELOCS 345, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 7 752 B (2.644 %).

## Round 15: two medium wrappers (88 B) and two source-level rules
`crelay29.c` (`/Os`):

- `2a45:000a` (43 B) - `fc1l(fc4(a, b, c, d))`: four ints widened with `cwd`
  into longs for the first call, whose result is forwarded as a long.
  **Rule:** the first callee must actually *return* `long`; declaring it `int`
  makes MSC insert a `cwd` before the push pair, which breaks the match.
- `50c4:0004` (45 B) - `t = h1(fc1(a)); return t - h1(fc1(b));`.
  **Rule:** the temporary must be declared `register` to stay in SI; with a plain
  local MSC spills it and reorders the argument pushes.

Probed and left open in the same size band:

- `20f9:000c` needs `b` in DI *and* the temporary in SI; every declaration
  order tried gives the pair the other way round (`b` in SI, temp in DI).
- `4448:0002` and its three siblings need a far-pointer *constant* pushed as
  `68 27 48 68 06 00`; MSC shortens the offset half to `6A 06`.
- `1110:0002`, `1113:0000`, `1115:000e` are a 32-bit shift/divide helper whose
  `D1 1E <disp>` word-rotate does not parse cleanly yet.

Ledger 403 rows - MATCH 37, RELOCS 342, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 7 609 B (2.595 %).

## Round 14: family-first harvesting (5 rows, 243 B)
Instead of walking the pool in address order, this round grouped every
unmatched unit by a **normalised byte pattern** (call targets masked) and worked
the largest groups. That found:

- three more members of the round-13 `36e7` family - `36e7:013e`, `0168`,
  `0192` - which the address-ordered scan had skipped; they match the existing
  `crelay25.c` source unchanged (41 B each);
- `crelay28.c` (60 B each): `1f57:0008` and `1f5b:0004` - `long f(long v, int n)`
  with `if (n < 0) return lfc1(v, -n); if (n > 0) return lfc2(v, n); return v;`.

**New decompilation rule learned:** the two branches must call *different*
symbols. With one callee MSC merges the two identical call sequences into a
tail jump (`EB E8` back into the first block), which the original does not have;
two distinct externs prevent the merge and reproduce the original byte layout.
This is the first case where a *source-level* naming choice (not a flag) decides
the match.

Family scan caveat recorded for the next rounds: 22 families are "identical
modulo call targets", but most of them are blocked by other traits -
`4101:0002` by the split far-pointer load (`8E 46`), `391a`, `2edb`, `3117`,
`1dfc:000c` by `ENTER` frames, `1131` by a `rep movsw` intrinsic sequence. The
clean remainder is small, so family-first scanning helps but does not replace
transcribing new shapes.

Probed and left open: `1dfc:0116` (cdecl call with `83 C4 08` cleanup and
SI/AX-staged arguments - MSC uses `8B E5` instead of `add sp,8` for a
long-returning callee), `1e1e:0046` (the original keeps the value in CX and uses
CL/CH; MSC loads AL twice), `33c1:0006` (six-call long chain).

Ledger 401 rows - MATCH 37, RELOCS 340, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 7 521 B (2.565 %).

## Round 13: thirteen rows (508 B) - the 36e7 family and nested chains
The best find of the round was a six-member family with one shape, in
`crelay25.c` (`/Os`): `36e7:0042`, `006c`, `0096`, `00c0`, `00ea`, `0114`
(41 B each). Each relays four parameters, then calls again with a **DGROUP far
pointer** (`1E 68 <disp>`), the third parameter and a constant
(`fc3(g_21c6, c, 1)`), and finally returns the third parameter.

`crelay26.c` (`/Os`, 38 B each):

- `2d49:004a` and its sibling `2d50:0000` - `fc3(1 - h(fc1(fc0())), a, 0)`;
  the `1 - x` shows up as `48 F7 D8` (`dec ax` / `neg ax`);
- `3a3f:008c` - `nn(fc1(fc4(a, a, b, c)), d)`, a four-argument relay forwarded
  through a near-Pascal call;
- `48ad:0008` - a guarded store: the `g_234e = 0` write sits *inside* the outer
  `if (!g_234c)` block, which is what makes the `75 18` skip reach the epilogue.

`crelay27.c` (`/Os`, 36-37 B):

- `1ec4:0100` - `if (fc0()) { fc1(1); fc2(a, b); return -1; }` with **no**
  trailing `return`: the fall-through leaves AX as `fc0()`'s result and the
  branch jumps straight to `leave`;
- `3a3f:0066` - `fc1(fc1(fc4(a, a, b, c)))`, nesting that does *not* trip the
  compiler bug reported in round 9 (the inner call has four arguments);
- `2d97:001e` - `fc3(g_1bee, g_1bec, 0x1BE8)`: the third argument is a
  *constant pointer* pushed with `68`, sitting between a relay and a
  no-argument call.

Left open: `223b:000e` needs the call result staged in SI (`8B F0 0B F0`) while
every `register` variant puts the temp in DI instead, and `3874:000a` differs
only in the order MSC loads the two register parameters.

Ledger 396 rows - MATCH 37, RELOCS 335, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 7 278 B (2.482 %).

## Round 12: five framed wrappers (169 B) incl. the 32-bit long helpers
`crelay23.c` (`/Os`):

- `3e19:0024` (31 B) - three **fastcall** relays from a framed Pascal function
  (`B8 0D 00` for the constant, then `8B 46 08` / `8B 46 06` for the parameters,
  no pushes);
- `2e39:000a` (33 B) - two far-pointer stores of zero-extended char results
  (`2A E4` + `C4 5E xx` + `26 89 07`), i.e. `*p = (unsigned char)csub();`.

`crelay22.c` (`/Os`): `2d9b:0058`, `2d9b:007c`, `2d9b:00a0` (35 B each) - the
same wrapper three times around a **32-bit global** operation: `g_1be8 += g_1bec`
(add/adc), `-=` (sub/sbb) and `&=` (and/and), each between a call with the
argument and a no-argument call.

Two more compiler crashes were found and are worth avoiding next time
(silent aborts: no object, no log):
1. `if (nf(a) + 1 == 0)` - a call result combined with an arithmetic constant in
   a comparison. Rewriting as `nf(a) == -1` still aborted in that function, so a
   local or a two-step form is needed.
2. `fc1(fc1(fc3(a, a, b)))` - triple nesting with a two-argument call inside,
   the same class as the round-9 crash (`sub3(sub2(a, a), 0)`).

Two more came from the same pass in `crelay24.c` (`/Ox`, 33 B each):
`31f3:0000` (a two-argument call, a relay of its result, then a two-argument
call with a zero - the parameter stays in SI) and `4a41:0000`
(`r = fc1(a); fc2(a, b); return r;` - DI keeps `a`, SI keeps the first result).

Ledger 383 rows - MATCH 37, RELOCS 322, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 6 770 B (2.309 %).

## Round 11: the second generation is pinned to "MSC 5.1 layout + MSC 6 zero"
This round was an investigation, not a harvest: no new ledger rows, but the
largest open question - which compiler produced the jump-merge/half-register
modules - is now much narrower.

Two candidates were measured against real units:

- **Turbo C 2.01** (`toolchain/tc201`, TCC -c -ml -O, runs under DOSBox 0.74):
  it reproduces push-bp frames, the bare `5D` epilogue, the merged-return
  layout (`... B8 01 00 EB 02 33 C0 CB`), `33 C0` zeroing, `33 C0 50` for a
  zero argument and SI-staged temporaries - i.e. every "-style" trait except
  two: its comparisons use `3B 06` (`cmp ax,[g]`) where the originals use
  `39 06` (`cmp [g],ax`), and its array scaling uses `D1 E3` (`shl bx,1`) where
  the originals use `03 DB` (`add bx,bx`). So Turbo C is **not** the source.
- **MSC 5.1** (/G1 /AM /Gs /Os, now runnable through `build.py`): its layout is
  **byte-identical** to the originals for the whole family of merge units -
  `A1 <g> / 39 06 <g> / 7E 05 / B8 01 00 / EB 02 / ?? / CB` - including the
  `39 06` operand order and the `EB 02` merge, with exactly one difference: it
  zeroes with `2B C0` (`sub ax,ax`) where the originals have `33 C0`
  (`xor ax,ax`). Every source form tried (`return a > b;`, `if/return 1/return
  0`, ternary, `!= 0`, `!!`, unsigned/char returns) and every flag tried
  (`/Oa`, `/Ol`, `/G0`, `/Ot`) keeps `2B C0`.

So the missing generation is *MSC 5.1-class layout with a different zero
idiom* - i.e. a compiler between 5.1 and 6.0, most plausibly **MSC 5.0** (or a
QuickC 2.x built on it). It differs from MSC 5.1 in two observable ways: `33 C0`
instead of `2B C0`, and push-bp frames without the `33 C0 9A` stack-check
preamble that MSC 5.1 always emits.

One more data point sharpens it further: `1ab9:0004`
(`g_536e = sub0(); g_9652 = 0; g_9650 = 0;`) compiles in the original to
`E8 .. A3 <g> 2B C0 A3 <g> A3 <g> CB` - i.e. a **`sub ax,ax` + `mov [g],ax`**
zero *store*. MSC 5.1 emits `C7 06 <g> 00 00` for the same source and MSC 6/7
emits `33 C0` + `A3`, so neither of the two compilers we can run has that
zero-store form at all: the original predates the `C7 06` immediate-store
optimisation. That points at MSC 4.x/5.0, which is consistent with the two
generations the rest of the analysis implies.

Obtaining that compiler (MSC 5.0, or QuickC 1.x/2.0 built on it) is now the
single highest-value step for the project; until then those units cannot
verify.

Ledger unchanged at 376 rows - MATCH 37, RELOCS 315, ASM 1, PENDING 23; verify
and checkled green; own-code coverage 6 535 B (2.229 %).

## Round 10: a shape-driven generator for two-call relays (3 rows, 89 B)
`tools/shapes.py` parses a deliberately tiny grammar - frame, optional `si`/`di`
saves, pushes of Pascal argument slots, constants, register copies of arguments
and globals, exactly two `/F`-translated calls, `leave` plus `retf imm` - and
emits the C, builds once, matches every candidate and appends the verified rows.
It is honest about its ceiling: only **two** pure two-call relays were left in
the pool (one matched, `3e19:0044`, 31 B), because the remaining ~190
framed+call units have real bodies (loads, stores, arithmetic) instead of plain
argument relays.

Manual follow-up in `crelay21.c` (29 B each):

- `2d49:0016` - `return d3(c3(1, 100, 0), a, 0);`, a constant-argument call
  nested as the first argument;
- `31cf:0008` - `return l3((long)l2(c0(), a));`, the int result widened with
  `cwd` and pushed as a long.

Near-miss recorded on purpose: `31dd:0008` calls `c0()` **before** pushing `a`,
while MSC evaluates Pascal arguments left to right, so no source order
reproduces it.

A fourth row came from the same pass: `439f:0006` (22 B) nests a
**near**-Pascal call (stays `E8`) inside a far-Pascal one.

Also probed and left open: `1dfc:00fa` needs the original's combination of
Pascal push order with the cdecl `8B E5` SP restore after the call - an
unprototyped `extern int __far cs2();` produces the restore but pushes the
arguments right-to-left, a `__pascal` prototype produces the right order without
the restore, and no single declaration gives both.

Ledger 376 rows - MATCH 37, RELOCS 315, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 6 535 B (2.229 %).

## Round 9: eight more framed-family rows (211 B) and a compiler crash
`src/calib/crelay20.c` (`/Os`) continues the framed + translated-call vein with
the shapes that repeat most often:

- call for effect, then the same argument relayed again (`register` parameter
  kept in SI) - `38b7:0008`, `3a18:000e`, 24 B each;
- `return h(sub(a));` with the argument in SI - `4a41:0022` (24 B);
- `return sub3(sub0(), a, b);` - a no-argument call ahead of the real one:
  `4e72:0022` (24 B);
- `sub(a); return sub2(a, 1);` - `3a6f:00c2` (26 B);
- `h(sub(a)); return sub3(a);` - two siblings, `31cf:0026` and `31d3:0056`
  (30 B each);
- a three-call sequence whose last call is **not** `/F`-translated and stays
  `9A` in the image - `31f6:0048` (29 B).

**MSC 7 crash, documented:** while transcribing `388d:0006`
(`sub3(sub2(a, a), 0)`) the compiler aborted with *no object and no log*.
Narrowed down: a two-argument nested call in the **first** slot of a
three-argument Pascal call crashes, e.g. `sub3(sub2(a, a), 0)` and
`sub3(sub2(a, b), 0)`, with or without `register`; `sub2(sub1(a), 0)`,
`sub3(sub0(), a, b)`, `sub3(a, sub2(a, a), 0)` and `sub3(a, a, sub2(a, a))` all
compile. So the unit stays open for a workaround (or a different generation)
rather than for lack of a source shape.

Ledger 372 rows - MATCH 37, RELOCS 311, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 6 424 B (2.191 %).

## Round 8: the framed + translated-call family pays (12 rows, 279 B)
A census of unmatched units with **no blocking trait**, bucketed by structure,
put `framed + contains a translated call` at 219 units / 10.9 KB - the largest
reachable group behind the `ENTER` modules. Twenty-two of them turned out to be
just two-call combinations, so they were transcribed as one batch:
`src/calib/crelay18.c`.

- six siblings forwarding a **long** from one call into the next
  (`52 50` = `push dx; push ax`): `372a:003a`, `372f:0000`, `4727:00ec`,
  `4a95:000e`, `4aa2:000c`, `4ab1:0006` (22 B each);
- the three-argument variant, 28 B: `473f:003e`;
- two siblings of `return h(sub2(a, b))` with the result forwarded through
  `push ax`: `3a57:0002`, `49f2:000e` (24 B);
- a leading no-argument call before the real one: `2d52:0006` (23 B) and
  `2e55:0024` (23 B);
- `3a58:000a` (25 B): the far result feeds a **near**-Pascal callee, so the
  second call correctly stays `E8` while the first is `/F`-translated.

That batch took one compile and one match pass - the family is regular enough
that the rest of the 219 units should be mined the same way next round.

Two follow-ups in the same round: `2160:0006` (`/Ox` swap-and-return around two
calls, old value in SI), `2b91:0072` (early-out guard `if (sub1(0)) return 0;`)
and `388b:0008` (a `register` parameter in SI feeding two relays) - 91 B more.

**Compiler-generation evidence (important for the next rounds):** every
compiler available here emits either `ENTER` (with `/Gs`) or a `__chkstk` call
(`B8 xx 00 9A`, without `/Gs`) as soon as a frame is needed. The originals with
`55 8B EC` + a call + no `__chkstk` therefore cannot come from MSC 5.1/6.0/7 at
all - the same generation that produces `add r,r` doubling, `8B E5 5D` and
`B8 00 00` is implied. That generation is not in the toolchain directory; until
it is, those units (including the 251 `ENTER` units) stay out of reach.

Ledger 364 rows - MATCH 37, RELOCS 303, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 6 213 B (2.119 %).

## Round 7: two parameter-store and register-argument wrappers (74 B)
- `src/calib/crelay16.c` (`/Os`): `4c96:003a` - three parameters written to
  consecutive globals in declaration order (`A3 <g>` each), then `sub1(1)`.
- `src/calib/crelay17.c` (`/Ox`): `22fe:0000` - a `register` parameter stays in
  SI, so all five pushes are `push si` (`56`) around four near-Pascal calls with
  descending constants and one far call. The trailing `F_TAIL4` only exists so
  the last symbol can be sliced out of the LEDATA.

Also re-tested and left out (documented so they are not retried blindly):

- `4690:0000` needs the call result staged in SI *without* a frame; every
  source form with a named temporary makes MSC 7 allocate a frame and switch to
  `ENTER` under `/Gs`, and the `(r = ...)` form does too.
- `1bc0:0000` and `2123:0002` are blocked by `add bx,bx` / `03 DB` doubling
  (trait 1) - the table index multiply.
- `481c:000c` / `4820:0006` need SI as the far-pointer base (trait 8) and take
  three argument words where the body uses two.
- `4448:0002` and its siblings need the far-pointer *constant* pushed as
  `68 27 48 68 06 00`; MSC shortens the offset half to `6A 06`.

Ledger 349 rows - MATCH 37, RELOCS 288, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 5 843 B (1.993 %).

## Round 6: the folded far call is a one-byte shift - matcher support + 1 row
The 3 507 NOP-prefixed `0E E8` are not the only /F output. When LINK knows the
callee is in the same segment it can drop the NOP as well, leaving
`0E E8 rel16` (**4 bytes**) where the object has `9A seg off` (5 bytes) - the
whole tail then shifts one byte left, which is why 36 unmatched units could
never align.

- `tools/match.py` now detects that form (`shrink_sites` / `_walk`): it anchors
  the comparison on the 5->4 shrink and masks the call slot, exactly like the
  5-byte translation. It only fires when the object byte is `9A` with a full
  4-byte fixup and the image really holds `0E E8` there, and it is covered by
  `--selftest` (positive and shifted-tail-negative).
- `src/calib/crelay15.c` (`/G0 /AM /Gs /Os`): `13c6:0000` - a flag cell set
  around a long-returning call, with the `83 EC 04` local, the folded call at
  +0x1a and the `/G0` `8B E5 5D` teardown. 39 B.
- `docs/CONVENTIONS.md` drops trait 5 (`8B E5 5D`) from the blocker list - it is
  `/G0` output for a function with a call - and documents the folded call form
  next to the NOP-prefixed one; `HOWTO.md` item 6 says so too.

Storage order caveat for future rounds: the `11a2` / `119c` long-through-pointer
family also uses the folded call, but the original loads the pointer into BX
*before* pushing the arguments and stores the high word first (`89 57 02 89 07`),
which no source form tested so far reproduces.

Ledger 347 rows - MATCH 37, RELOCS 286, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 5 769 B (1.967 %).

## Round 5: the `8B E5 5D` epilogue is plain `/G0` (5 rows, 129 B)
- `src/calib/crelay12.c` (`/Os`): `h(sub(a))` without SI staging (the sibling
  `32da:000c` does need `/Ox`), `if (g != -1) { sub(g); g = -1; } return g;`
  with an immediate `C7 06 <g> FF FF` store, and constant pushes followed by a
  second translated call. 79 B.
- `src/calib/crelay13.c` (`/G0 /AM /Gs /Os`): `void f(a,b,c,d) { sub5(0,d,c,b,a); }`
  is **byte-exact** including `33 C0 50` (the `/G0` way to push a zero) and the
  `8B E5 5D CB` teardown. This settles the last "unexplained" epilogue: `mov
  sp,bp` appears under `/G0` **only when the function contains a call** (the
  8086 has no `LEAVE`), while a call-free `/G0` function gets the bare `5D`.
- `src/calib/crelay14.c` (`/G1 /Ot`): the rotated loop
  `while (n) { sub(); n--; }` - test first, body starts with one alignment `90`
  before the translated call; `/Os` omits that `90`.

Tooling: `tools/gap.py` no longer treats `8B E5 5D` as a blocker (it is `/G0`
output), so the reachable pool is now **1 210 units / 81 246 B**; `IDIOMS.md`
records the proof and drops it from the exclusion list.

Left as a documented near-miss: `13c6:0000` matches in every instruction except
the call form - the image holds a **4-byte** `0E E8 rel16` where the object has
a 5-byte `9A`, so the whole tail shifts by one byte. A matcher rule for
size-shrinking same-segment far calls is needed before it can be claimed.

Ledger 346 rows - MATCH 37, RELOCS 285, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 5 730 B (1.954 %).

## Round 4: four /F rows; MSC 5.1 runs through build.py; the ENTER vein measured
- `src/calib/crelay10.c` (`/Os`): `h(sub2(a, b))` and
  `if (x == -1) x = sub2(y, z); return x;` (54 B).
- `src/calib/crelay11.c` (`/Ox`): a call result kept in SI and returned, and a
  `register` parameter that feeds both a relay and a two-argument call (50 B).

Toolchain: **MSC 5.1 now runs through `build.py`** as well
(`--msc-dir MSC51 --no-dpmi`, same recipe as MSC 6.0) - it is the only tested
compiler that emits `ENTER imm16,0` frames under `/G1 /Gs`.

That matters because the next structure family is large: **795 unmatched units
(117 436 B) begin with `ENTER`**. The first transcription (`1e9f:0004`, a
14-byte stack buffer passed twice to a far function) is byte-exact except that
MSC 5.1 emits the stack-address `LEA` twice (`8D 46 F2 16 50` / `8D 46 F2 16 50`)
where the original computes it once and pushes `SS:AX` twice - no `/O` variant
tested (`/Oa`, `/Os`, `/Ot`, `/Ol`, `/Ox /Oa`) performs that CSE. So the ENTER
family probably needs the same older generation that also explains `add r,r` and
`B8 00 00`; the frame itself is no longer the obstacle.

Ledger 341 rows - MATCH 37, RELOCS 280, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 5 601 B (1.910 %).

## Small-wrapper harvest: 23 rows from the /F pool (456 B)
A survey of the 420 unmatched units up to 56 bytes that contain a translated
call produced 23 more RELOCS rows in two flag groups.

- `src/calib/crelay8.c` (16 rows, `/Os`): nested relays (`return h(sub())`), a
  char-returning call sign-extended and stored (`98 A3 <g>`), two calls followed
  by `g = 1`, a near-Pascal call with -1 before a far relay, `b - sub(a)`
  (`2B 46 / F7 D8`), `sub2(b, c) - a`, `sub1(c + b + a)`, and six siblings that
  pass a DGROUP far pointer as `1E 68 <disp>`.
- `src/calib/crelay9.c` (7 rows, `/Ox`): call results OR-ed with the first one
  staged in SI (`8B F0` / `0B C6`), `(unsigned char)sub(a)` (`2A E4`), a near
  Pascal function with a `register` parameter kept in SI across the call,
  `sub2(a, 0x8000); return -1;`, two relays from one SI value, the 32-bit
  unsigned product (`F7 66` = MUL, where `F7 6E` would be the signed IMUL), and
  a far-fastcall relay that keeps its AX argument in SI.

Two practical findings recorded while iterating:

- **MSC 7.0 is strict C89.** A declaration after a statement makes `CL` abort
  *without creating its log file*, so `build.py` reports only "no OBJ produced"
  and the real cause is invisible. Declarations must stay at block start.
- Near-misses left out on purpose: `1270:000e` (original keeps a `55 8B EC`
  frame and tests the flag with `A0`/`0A C0`; our frameless `80 3E` form does
  not match) and `439f:0006` (the original pushes SI twice around a near call,
  our `register` variant still reloads from the stack).

Ledger 337 rows - MATCH 37, RELOCS 276, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 5 497 B (1.875 %).

## Relay harvest from the /F pool; compact FIXUPP offsets repaired
The /F discovery paid off immediately: **49 more rows (926 B), all RELOCS**,
from the 1 232-unit reachable pool. Every one is a wrapper around a single far
call, and they fell into two passes.

- `src/calib/crelay3.c` (15 rows): six two-argument relay siblings (18 B), three
  `(a, 1)` relays (17 B), three single-argument relays (15 B), a
  multiply-after-the-call wrapper, a constant forwarded in AX to a far fastcall
  (`B8 1A 00 90 0E E8`), and a call-for-effect-then-`return -3`.
- `src/calib/crelay5.c` (3 rows, `/Ox`): `return sub() != 0;` compiles to
  `cmp ax,1 / sbb ax,ax / inc ax` in a near function (two call targets), and a
  far fastcall state reset whose old value must be staged in DX
  (`8B 16 <g>`), which needs `/Ox` - `/Os` uses CX instead.
- **`tools/relays.py`** (new): recognises the whole family mechanically -
  `55 8B EC <word pushes> 90 0E E8 rel16 C9 C2/CA imm16` - decodes each push as
  a parameter (Pascal slot) or a constant, emits the C, builds once and matches
  every member. Second pass: **31 of 32 candidates matched (641 B)** in one run;
  the one failure is `41e7:000a`, where the original pushes a far pointer
  constant as `68 06 00` while MSC shortens the offset to `push imm8`
  (`6A 06`) - documented, not counted.

Two tool defects surfaced and were fixed on the way:

1. **MSC compact FIXUPP offsets are modulo 256.** The offset field is one byte
   and MSC sorts the entries descending, so in a LEDATA larger than 256 bytes a
   call past the boundary is listed as `offset - 256` and silently loses its
   fixup. The 286-byte relay batch exposed it: `3390:025a` calls at 0x10E but
   the record said 0x0E, so the matcher could not mask it.
   `omfdump.unwrap_fixup_offsets` rebuilds the true offsets from the modular
   differences (guarded: only when the result is strictly descending and inside
   the LEDATA) and has its own `--selftest`.
2. `match.py` now also resolves `@`-decorated `__fastcall` symbols.

Ledger 314 rows - MATCH 37, RELOCS 253, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 5 041 B (1.719 %).

## The `90 0E E8` idiom is MS LINK /FARCALLTRANSLATION - 77 KB become reachable
## The `90 0E E8` idiom is MS LINK /FARCALLTRANSLATION – 77 KB become reachable
A byte census settled the biggest open question in the trait table: the image
contains 3 564 `0E E8` (`push cs; call near`) and **3 507 of them are directly
preceded by `90`** – a NOP that no compiler emits. It is the linker: Microsoft
LINK's `/FARCALLTRANSLATION` (`/F`, normally together with `/PACKC`) rewrites a
direct far call `9A seg off` into `NOP; PUSH CS; CALL NEAR` whenever the callee
lands in the caller's physical segment. Reproduced locally with the MSC 6.0
toolchain: two objects linked with `LINK 5.10 /F /PACKC` give
`90 0E E8 F3 FF` where the same link with `/NOF` keeps `9A 00 00 00 00`.

Consequences (all byte-verified, not assumed):

- `tools/match.py` now recognises the rewrite: a `9A` whose 4-byte operand is a
  fixup matches an image `90 0E E8 rel16`, and the whole 5-byte slot is masked
  (the rel16 is link-layout dependent, like any relocated operand). The
  selftest covers the positive case, a wrong opcode, and a partial fixup.
  `90 0E E8`-only units are therefore no longer blocked.
- `tools/gap.py` stopped treating four idioms as blockers, because each is now
  reproducible: the translated far call, plain `9A` (ordinary output), the bare
  `5D` epilogue (`/G0`, round 1) and `C7 06 <g> 00 00` zero stores (MSC 6).
  The reachable pool grows from **441 units / 24.1 KB to 1 232 units / 77.0 KB**
  (the remaining blockers are stray `90` padding, split pointer loads,
  `add r,r` doubling, `SI` bases, `8B E5 5D`, `B8 00 00`, `B4` register args
  and ESA addressing).

First harvest of that pool: **20 new rows, 203 B**, all RELOCS.

- `src/calib/cfarl.c` (13 units) and `cfarl2.c` (6 units): six
  `g_78cc ± 1` fastcall relays, a constant-relay pair (`return psub(14)`,
  `return psub(0)`), four frameless `return fnone()` six-byte relays, one near
  relay, a conditional `if (g_192c == 0) none();`, two-argument relays from
  DGROUP, a `1E 68 <disp>` far-pointer argument and a nested `h(none())` –
  each object call site is `9A`, i.e. the untranslated form.
- `src/calib/cfar6.c` (`1aa1:0130`, 11 B): MSC 6.0 with **`/G0`** materialises
  the long constant as `mov ax,0x800 / cwd / push dx / push ax`; `/G1` would
  use the push-immediate form and MSC 7 calls through `9A`. That is the first
  ledger row built with a toolchain other than MSC 7, so `tools/verify.py` now
  understands optional `msc=<dir>` and `nodpmi` tokens in a row note (MSC 6.0's
  real-mode CL hangs when the HDPMI TSR is loaded) and refuses two toolchains
  sharing one source stem.

Ledger 265 rows — MATCH 37, RELOCS 204, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 4115 B (1.403 %).

## /G0 explains the `5D` epilogue; MSC 6.0 turns out to be runnable
`1000:1364` (abs_branch) was PENDING with a perfect body and a wrong teardown:
the original ends `5D CB` (`pop bp; retf`), MSC 7 emits `C9 CB` (`leave`). The
ledger recorded that as a compiler-generation fingerprint; it is the **CPU
target**. `/G0` (8086) cannot use `LEAVE`, so `--flags "/G0 /AM /Gs /Os"` makes
the same cdecl source a byte-exact MATCH. `/G0` also restores SP with
`8B E5 5D` where the frame is left, so the 386 units with that teardown are a
flag question, not a second compiler.

Second finding: **MSC 6.0 is runnable**, contrary to the round-46 note. That note
assumed the only `CL.EXE` was the Windows PE one from `msc6\disk2`; `msc6\disk8`
ships `CL.EX$`, which decompresses to a real-mode `CL.EXE` (81 184 B). With
`C1/C2` (disk1/2) and `C3` (disk7) it compiles under DOSBox-X without DPMI
(`--msc-dir MSC6C --no-dpmi`). Codegen measured on the calibration probe:
`55 8B EC` frames like MSC 7, `/G0` gives `5D`, but it differs in three ways —
`0E E8` (`push cs; call`) for a same-segment far call where MSC 7 emits `9A`,
`2B C0` where MSC 7 emits `33 C0`, and it only parses the single-underscore
`far`/`pascal` keywords (`__pascal` is a hard syntax error). No PENDING row is
fixed by it, and of the eight units whose only blocking trait is `0E E8`, the
single candidate is a 5-byte `push cs; call; retf` fragment inside the startup
area, so no row was added.

`/G0` was then applied to the 29 units whose only trait was the `5D` epilogue:
most are CRT/runtime helpers (`rep movsb`, DOS INT 21, 32-bit mul/div) or
mid-instruction fragments left by the splitter; testing the transcribable ones
against MSC 5.1, MSC 6 and MSC 7 closed `4c96:0006` (`return g_2c14 = 1;`, 7 B,
RELOCS). `11d8:000c` (SET4) also carried a wrong size: the function is 41 bytes,
not 60 — the inventory window swallowed the next function's prologue, which is
why the old note claimed "58/60 identical". With `/G0` its body is byte-exact;
only the redundant `8B E5` before `5D CB` is missing from every available
compiler, so it stays PENDING at the corrected length.

Ledger 245 rows — MATCH 37, RELOCS 184, ASM 1, PENDING 23; verify and checkled
green; own-code coverage 3914 B (1.335 %).

## Constant and conditional far-call relays verified
`31bc:0004` (8 B) is an independent entry inside a merged inventory window,
corroborated by direct callers. At `3b21:0004` (15 B), the preceding zero
check belongs to the wrapper; matching just its call tail would omit it.
Both verify as RELOCS.

## AX fastcall relay and second save/reload pair verified
`3220:00a2` forwards a Pascal stack argument in AX. `36e7:020e` and
`36e7:0218` mirror the previous save/reload pair at a different DGROUP word;
the save entry is inside a merged inventory unit. All three add 33 B as RELOCS.

## Three far-call adapters verified
`307b:000c` and `4182:000c` save a far call's AX result to DGROUP.
`4183:0006` reloads the latter word into AX for a far fastcall. The three
routines add 29 B as RELOCS in the existing relay compilation unit.

## Ten more direct far-call wrappers verified
One build covers ten wrappers that add constants, DGROUP words, or DGROUP
far pointers to a Pascal call. This adds 163 B as RELOCS, including the
22-byte routine at `3616:000e` inside an 85-byte inventory window.

## Nine direct far-call relays verified in one build
Nine inventory-backed wrappers forward one to three words to far Pascal
callees. The caller's own return can be near or far; the original `C2`/`CA`
selects the declaration. The batch adds 147 B as RELOCS. Direct `9A` is
reproducible here; this is distinct from the `push cs; call` form.

## Four more scanner wrappers verified
The `2e31:0006`–`2e37:0008` batch adds 132 B as RELOCS. The 512-entry pair
passes a DGROUP byte table; the 256-entry pair passes `4827:08E6`, whose
segment and offset immediates match without masking.

## Four packed-table scan wrappers verified together
The `4386:0024`/`4386:0044` and `43ac:0004`/`43ac:0024` pairs share one
source and flag set (31 B each, all RELOCS). They pass 64 or 16 entries,
a four-byte stride, and a DGROUP far pointer to one of two far Pascal
callees. `capacity - result` reproduces the original `sub; neg` sequence.

## Packed-table pointer getter verified
`42bc:000c` (6 B, RELOCS) returns the far address of the table used by
`_clear_entries`. Its offset is an OMF fixup; the `mov dx,ds` and far return
match without masking. The getter starts inside a merged inventory window.

## Two register-staged relays verified in one batch
`21ff:0004` (31 B) and `4dac:0000` (33 B) both verify as RELOCS from a
single source and flag set. The second relay leaves the setup result in AX
and moves the saved index from SI to DX for a two-argument fastcall.

## Sentinel-based table dispatch verified
`42ac:002c` (31 B, RELOCS) keeps the argument in SI across the first call.
Testing `!= -1` before the fallback reproduces `inc ax; je` and the original
branch order.

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
