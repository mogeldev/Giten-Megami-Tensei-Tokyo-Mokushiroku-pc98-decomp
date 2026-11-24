# PROGRESS

## Round 217: the char-parameter slot, measured (no rows)
Round 216 left `2d60:000e` one parameter offset out and unexplained. This round measured the
cause by compiling pascal functions with `char` parameters and dumping them:

- `f(char a, int b)` - `a` at `[bp+08]`;
- `f(int a, char b)` - `a` at `[bp+08]`, `b` at `[bp+06]`;
- `f(char a, int b, int c, int d, int e, int f)` - `a` at **`[bp+10]`**, `b` at `[bp+0E]`,
  and the epilogue still `retf 0C`.

So a six-parameter pascal function with a leading `char` gets an **extra slot**: seven words of
frame for a twelve-byte pop. That is MSC's behaviour, not a mistake in my declaration, and it
is precisely why the unit cannot be transcribed - the original's six-parameter function reads
its byte parameter at `[bp+0E]` with no extra slot.

Two facts now in `docs/CONVENTIONS.md`: the offset table for `char` parameters, and the `cbw`
(`98`) that follows a byte load when a `char` is stored into an `int` - which distinguishes
"this parameter is a `char`" from "the compiler narrowed an `int`".

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 216: a six-argument pass-through, one offset out (no rows)
`2d60:000e` (31 B) is the simplest possible shape - a function that forwards all six of its
parameters to one call:

    h(a, b, c, d, e, f);

Five pushes and a byte push (`8A 46 0E` then `50`) match the original exactly, in order, and so
does the `90`-prefixed call. The single difference is the **offset of the byte parameter**: the
original reads `[bp+0E]`, MSC reads `[bp+10]`.

That is the pascal offset table from round 210 applied to a `char` parameter: with six
two-byte slots the first parameter should land at `[bp+0E]`, and MSC puts it one word higher.
Two declaration shapes were compiled (with and without an explicit `return`) and both give
`[bp+10]`, so the extra word comes from how a `char` parameter is counted rather than from the
call itself.

Not recorded: the C is trivial and certainly right, but "certainly right" is not the standard
this ledger uses, and the offset discrepancy is unexplained. It is worth returning to - a
forwarding function is about the cheapest row the project can produce.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 215: BX is never a C variable (no rows)
Round 214 left the `119c` family blocked by a `push bx` before any argument push. This round
tried to force it three ways - an explicit pointer temporary, explicit field temporaries, and
`s[0].x` subscripts - and MSC answered `push si`, `push di`, or an `ENTER` frame. **It never
allocates BX to a C variable.** BX stays its scratch register (shift counts, far-pointer
offsets, table indices).

Measured the class: **9 unmatched units (672 B)** whose prologue saves BX. Five of them are a
tight family (`119c:000c`, `119e:000c`, `11a0:000c`, `11a2:000c`, `11a4:000a`), 30-32 bytes
each, differing only in their call target. Two members are otherwise *transcribed exactly*:

    struct S { int x, y; };
    long __near __fastcall h(long a, int b);
    void __far __pascal f(struct S *s, int v) { *(long *)s = h(*(long *)s, v); }

That is wall 20 with an unambiguous tell: a `push bx` in a prologue means the source kept
something live in BX, and no C declaration reproduces it.

The class is small, which is itself useful: it means this particular barrier is *not* where the
mass of the remaining code sits - unlike the doubling wall's 199 units.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 214: a sibling family, blocked by the BX save (no rows)
Narrowed round 212's clean pool to **30 single-call candidates** (no doubling, no zeroing, no
segment or port work, exactly one call) and transcribed one - a function that overwrites a
four-byte struct with the result of a call taking the struct's own fields:

    *(long *)s = h(a, s->y, s->x);

Everything after the prologue lines up: the two pushed fields come from `[bx]`/`[bx+2]`, the
call is near, and the result is stored back with `89 57 02` / `89 07` in exactly that order.
The difference is the very first instruction: the original **saves BX before pushing any
argument** (`push bx` at offset 3), because the pointer is live across the call; MSC pushes
the long argument first and only reaches for BX later.

That is the register-allocation-by-lifetime rule again (round 193), now seen in a prologue
rather than a loop - and it blocks a *family*: `119c:000c`, `119e:000c` and `11a0:000c` are
three siblings of this shape that differ only in their call target, so a fix would produce
three rows at once. None of them is matchable as things stand.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 213: evaluation order before pushes (no rows)
Round 212's clean pool has **77 call-bearing candidates**; three were transcribed this round
and all three are blocked, but one of them produced a rule.

`31dd:0008` (27 B) is `h3(h2(a, h1()))`. The original calls `h1` **first**, then pushes both
arguments, then calls `h2`. MSC pushes each argument as it evaluates it, so `push a` precedes
`call h1`. Reversing the argument order changes which value is pushed first but not the
interleaving, and a temporary either earns an `ENTER` frame or keeps MSC's order.

That is now recorded under wall 9 with its own tell: **a call sequence that starts with a
`call` and only then pushes means a nested call in a later argument**, and MSC cannot
reproduce it.

The other two attempts hit walls already named - `1e1e:002a` caches the parameter in CX before
comparing (wall 17), and `3eb9:0006` loads `es` before `bx` from a far-pointer result (the
`3ebd:0068` sub-case).

The clean pool is real - 77 candidates with no doubling, no zeroing, no segment or port work -
but each one still has to clear a handful of named walls, and most do not.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 212: a clean-pool screen, and a nineteenth wall (no rows)
Round 211 showed that 23 % of the remaining code sits behind the doubling wall, so this round
screened for what is **not**: unmatched units with no `add reg,reg` doubling, no `sub ax,ax`
zeroing, no segment/port/string operations, starting with a frame and ending cleanly - **145
candidates**, the pool that should be matchable if anything is.

Two were transcribed:

- `4d98:000a` (18 B) is `return (a + b) & 3;`. The original loads both parameters as **words**;
  MSC loads them as **bytes**, because `& 3` bounds the range and narrowing is legal. Four
  forms were tried (plain, `unsigned`, via a temporary, `% 4`) and all four narrow - so this
  is **wall 19**, a range-narrowing wall, and a third case of the original's optimiser being
  *less* aggressive than MSC 7.0's.
- `1270:000e` (22 B) did not compile as a unit at all (the symbol came out shorter than the
  window), so it was set aside.

The narrowing wall is worth naming because it explains a family: every unit with `& mask` or
`% n` on a parameter is likely blocked, and the original's word loads are the tell.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 211: how much sits behind the doubling wall (no rows)
Round 199 closed the doubling class with six source forms. This round tried six more
(`(unsigned)x * 2`, `x - (-x)`, `(int)((long)x * 2)`, `x + (x)`, `(x << 1)`,
`y = x; y * 2`) under both `/Os` and `/Ox` - **twelve compilations, twelve `D1 E0`**. The
closure is as firm as an experiment can make it.

Then measured the class instead of guessing at it: unmatched units whose bytes contain any
`add reg,reg` doubling (`03 C0`, `03 D2`, `03 F6`, `03 FF`, `03 DB`, `03 C9`) number
**199 units and 66 381 bytes - about 23 % of the remaining unverified own code**.

That is an upper bound (some units double *and* carry another wall, and some hits are data
bytes inside immediates), but it is far larger than any other class and it explains the shape
of the pool: half the units that "nearly match" do so except for an index scale, which is
exactly why so many PENDING rows are two bytes short.

Also attempted `2b33:0006` (23 B), a far-pointer field subscript; it is blocked by both
`les` and the doubling (`add si,si`), confirming the measurement from the other direction.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 210: parameter offsets measured, not reasoned (no rows)
Round 209 stumbled on a parameter-offset mismatch and guessed at the cause. This round settled
it by compiling `void f(int a, int b, int c)` in both conventions and dumping the object:

| convention | `a` | `b` | `c` |
|---|---|---|---|
| `__far __pascal` | `[bp+0A]` | `[bp+08]` | `[bp+06]` |
| `__far __cdecl` | `[bp+06]` | `[bp+08]` | `[bp+0A]` |

Pascal numbers parameters **backwards**: the first declared has the highest offset. That is
now in `docs/CONVENTIONS.md` as a table rather than a sentence, because it is a fact to look up,
not to derive - misreading it cost round 209 a candidate.

Re-reading `19a3:000a` with the correct mapping (the dispatch is on the *third* parameter)
moved the transcription from "first byte differs" to "only branch distances differ", so the
unit is blocked by the pad again rather than by my parameter order. It is not recorded: 5 of
the 6 extra bytes come from something other than the pad and the C is not settled.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 209: the summary audited against the ledger (no rows)
`docs/SUMMARY.md` was written at round 195 and its four headline numbers had gone stale by six
rows. Audited it against the ledger and `tools/coverage.py`: **517 rows** (MATCH 38, RELOCS
438, ASM 2, PENDING 39), **476** verified, **11 351 of 293 211 bytes (3.871 %)**. The PENDING
counts in the prose were updated too, and the file now says it is a snapshot with
`tools/report.py` as the live source.

Then tried one more candidate from the large-unit screen, `19a3:000a` (79 B) - a flag
dispatch:

    if (flags & 2) r = 1;
    else if (flags & 8) r = h1(a, flags, c);
    else if (flags & 4) r = h2(a, flags, c);
    else r = h3(a, flags, c);

A plain local gives an `ENTER` frame (the original has none), and a `register` local fixes
that but the parameter MSC tests is at `[bp+08]` where the original tests `[bp+06]` - a
pascal argument-order difference I could not resolve in the round. Not recorded: the C is not
settled.

The audit is the substantive part. A stale summary is worse than none, because it is the one
document a reader is invited to trust without checking.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 208: MSC 6.0 has stopped working in this environment (no rows)
Tried to re-open the "is the original compiler pre-6.0?" question by rebuilding the doubling
test with MSC 6.0 - if 6.0 emitted `add reg,reg`, the original would plausibly be a 5.x-era
compiler and a whole class would reopen.

It cannot be tested right now: `--msc-dir MSC6C` reports "no OBJ produced" with **no compiler
output at all**, while `--msc-dir MSC7I` on the same source succeeds (341-byte object). The
CL.EXE exists, `build.py`'s existence check passes, and the failure is identical with
`--no-dpmi` and with `--run` substituting the CL line verbatim - so the DOSBox invocation
starts and the compiler produces nothing, rather than the toolchain being absent.

Recorded in `docs/GAP.md` as an **environment regression, not a compiler finding**. Nothing in
the MSC 6.0 conclusions depends on it (rounds 140-146 established that 6.0's codegen matches
7.0's for every wall that matters), and no ledger row was ever verified with 6.0, so the
ledger is unaffected. The note is there so a future session does not spend a round
rediscovering it.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 207: thirteen PENDING rows in the registry (tooling round)
Added four more hypotheses to `src/pending/pending1.c` and `tools/pending.txt`, bringing the
machine-re-testable set to **13 of the 39 PENDING rows**:

| row | what it waits for |
|---|---|
| `2e68:000c` | a branch distance across the pad byte |
| `41d8:000c` | `add si,si` instead of `shl si,1` |
| `1ab4:0028` | a DX-cached state word |
| `3b5d:0006` | one pad byte after `push ds`/`push imm16` |

All 13 compile from the single pending object and all 13 still differ, so the command that
answers "has anything changed?" is now one line for a third of the set.

Two of the four are worth noting for what they represent rather than what they test: they are
*functions the inventory does not name* - the second halves of mis-cut windows, recorded at
their true start addresses (`1ab4:0028`, `3b5d:0006`). Earlier in the project those would
simply have been lost between the ledger's rows.

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 206: the nop closed, and what that means for PENDING (no rows)
Round 199 closed the doubling class by asking whether MSC ever emits `add reg,reg`. This
round asked the same of the **pad byte**: does MSC ever put a `90` inside a function body?

Six statement shapes were compiled - an empty `else`, a trailing `;`, a `switch` with
`default: break;`, an `if (x) { }`, `do { } while (0)`, and a two-armed `if`. **None emits a
`90` in the body**; MSC's only `90` is the alignment byte at the end of a segment.

So the padding mechanism - seven witnesses, and the cause of most of the remaining one-byte
near-misses - is closed rather than open. That changes what the PENDING column means, so
`docs/SUMMARY.md` now says it plainly: the 39 PENDING rows split into those **proven
unreachable** with this compiler (pad byte, doubling, `and`-for-`test`, `mov si,[disp16]`,
the `bx=ax`/`es=dx` order, `inc`/`dec` switch chains) and those still **unexplained**. If a
matching toolchain ever appears, the first group is where the rows come from.

That is the honest end-state for this phase: not "these were too hard", but "these are the
exact behaviours the original compiler has and MSC 7.0 does not".

Ledger 517 rows (unchanged), PENDING 39; verify and checkled green; own-code
coverage 11 351 B (3.871 %).

## Round 205: screening for split windows (no rows, PENDING record)
Wall 18 says a return in the middle of a unit means the window spans two functions. That is
easy to state and harder to screen: **161 unmatched units** contain a mid-unit `C3`/`CB`, but
most of those hits are the byte appearing inside an immediate or as data.

One of them was transcribed to test the idea on a real case - `3b5d:0000` opens with the tail
of a function (`8B C6 5E 5F CB`) and the next function begins at `3b5d:0006`:

    if (!g_995d) h((char __far *)0x1766);

It is one `90` from matching: the original has `1E 68 66 17 90` where MSC emits `1E 68 66
17`, so the `jnz` distance differs by one - wall 2 again, in the padding after a
`push ds`/`push imm16` pair. Recorded as PENDING at the second function's true start.

So the split-window screen works but is noisy, and what it finds still lands on the same two
or three walls. Both facts are consistent with where the project is: the *inventory* has
recoverable functions the ledger does not name, and the *compiler* has behaviours no source
form reaches, and the intersection is small.

Ledger 517 rows - MATCH 38, RELOCS 438, ASM 2, **PENDING 39**; verify and checkled
green; own-code coverage 11 351 B (3.871 %).

## Round 204: the second function inside the mis-cut window (no rows, PENDING record)
Round 203 matched the first 27 bytes of `1ab4:000c` and left the remaining 45 bytes as a
separate function. Transcribing that one gives

    if (g_536e != 0 && g_536e != -1) h(g_536e);
    g_536e = 0;
    h3((char __far *)&g_9950, (char __far *)&g_9b18, (char __far *)&g_9b10);

and it is blocked by exactly one thing: the original **caches the state word in DX** (`8B 16
6E 53` / `0B D2`) and tests the register twice, while MSC compares the global twice (`83 3E`)
or, with a `register` copy, reaches for SI. Three shapes were compiled and all three give
MSC's form. Everything else - the far-pointer triples, the final call, the store of zero -
lines up.

That is the same DX-versus-AX choice as `2141:00a6` (round 123), so this unit joins the
PENDING set at `1ab4:0028` (the second function's true start, 44 bytes) with the diagnosis
written down.

Worth noting for the ledger's own sake: a row at a VA that is not a unit start is accepted by
`verify.py` and `checkled.py` - which is what makes mis-cut windows recoverable at all.

Ledger 516 rows - MATCH 38, RELOCS 438, ASM 2, **PENDING 38**; verify and checkled
green; own-code coverage 11 351 B (3.871 %).

## Round 203: a mis-cut window becomes a row (27 B)
Round 202 left `1ab4:000c` (72 B) unexplained: everything matched except the `if (g_536c)` arm,
whose branch distance was one byte out. Disassembling it properly showed why - there is a
**`ret` at offset 0x1A with a second function's code after it**. The window spans two
functions, so no single C function could ever match it.

Matching only the first 27 bytes did:

    g_9950 = 0;
    g_9b18 = 0;
    if (g_536c) g_536e = -1;

Two details fell out of the disassembly and are worth keeping:

- the two `long` globals are cleared with `2B C0` and **four** word stores (round 175's rule,
  seen at double length);
- the guard is `cmp al,[0x536c]` - it compares the already-zero AL against the byte rather
  than comparing the byte with an immediate, because the compiler knew AX was zero.

The mis-cut is now **wall 18** with a screening rule: a return instruction that is not at the
end of the unit means the window spans two functions, so match only up to it.

Ledger **515 rows** - MATCH 38, RELOCS 438, ASM 2, PENDING 37; verify and checkled
green; own-code coverage **11 351 B (3.871 %)**.

## Round 202: a reset function, mostly right (no rows)
Next member of the long-store zeroing class: `1ab4:000c` (72 B), which clears two `long`
globals and then either stores -1 or cleans up and calls three functions with far pointers to
its own globals:

    g_9950 = 0;
    g_9b18 = 0;
    if (g_536c) { g_536e = -1; return; }
    if (g_536e != 0 && g_536e != -1) h(g_536e);
    g_536e = 0;
    h3((char __far *)&g_9950, (char __far *)&g_9b18, (char __far *)&g_9b10);

The two `long` clears match exactly (`2B C0` plus four word stores, round 175), the far
pointers match (the `(char __far *)&g` cast of round 132), and the trailing `push ds`/`push
imm` triples line up. What does not is the `if (g_536c)` arm: the original's `jz` skips 6
bytes where MSC's skips 7 or 8, so the `-1` store or the return path is one instruction
different, and every following byte shifts.

Two return types were tried (far pascal and near cdecl - the original's `C3` says near) and
neither fixes the arm. The remaining difference is small but structural, so the unit is not
recorded as PENDING: unlike the others, its C is not *known* yet, only close.

That distinction is worth keeping - PENDING means "C known, bytes differ", and this unit is
still in the "C nearly right" state.

Ledger 514 rows (unchanged), PENDING 37; verify and checkled green; own-code
coverage 11 324 B (3.862 %).

## Round 201: the long-store zeroing class pays a row immediately (64 B)
Round 200 split the "sub ax,ax zeroing" class and noted that its 72 reachable units are all
over 40 bytes. Working the first of them, `2e76:0000` (64 B), matched on the first try:

    long r, z;
    r = h1();
    z = 0;
    if (sel == 1) z = h2();
    h3(a, r, z);

Three things had to be right and all three came from rules the project already had:

- `z = 0` on a **`long`** local produces `2B C0` plus two word stores (round 175);
- the frame is `enter 8, 0` with `r` at `[bp-8]`/`[bp-6]` and `z` at `[bp-4]`/`[bp-2]` -
  **declaration order**, which round 158 established for locals;
- the whole thing needs `/Ox`: under `/Os` MSC allocates the two longs in the *opposite*
  frame order and every store shifts by two bytes.

So the largest remaining class is not just reachable in principle; its first member matched
in one compile, and the reason it did is that three separately-earned rules composed.

Ledger **514 rows** - MATCH 38, RELOCS 437, ASM 2, PENDING 37; verify and checkled
green; own-code coverage **11 324 B (3.862 %)**.

## Round 200: the biggest class measured, not closed (no rows)
Round 199 closed the doubling class by experiment; this round asked the same question of the
**largest** class - "sub ax,ax zeroing", 74 units and 15 KB - and got a more interesting
answer.

First, what MSC emits for an `int` zero in eight different contexts (local, through a pointer,
global, `char`, `register` local, array element, a value used afterwards): **always `33 C0`**
(`xor`). For a `long` *return* it is `33 C0 99`. But for a `long` **store** it is `2B C0`
(`sub ax,ax`) followed by two word stores - which is how `1ab9:0004` matched in round 175.

So the class is not closed; it is **split**, and the split is measurable:

| shape | units | bytes |
|---|---|---|
| `2B C0` followed by two word stores (long-store shape) | **72** | 15 495 |
| everything else (no MSC equivalent) | 5 | 15 475 |

The first column is *reachable* - declare the destination `long` and MSC emits the older
zeroing form. The second column is the real wall.

The caveat, which the round also measured: **no unit in the reachable set is small**. Every
one of the 72 is over 40 bytes or carries another wall (segment work, ports, string ops), so
the class cannot be mined by transcription alone - the long-store zeroing needs to be one
detail among several in each unit, which is a slower kind of work than the small-unit screens
that have been paying lately.

That is the right note to reach round 200 on: the ledger has 513 rows, the biggest class is
understood rather than merely counted, and what remains is understood work rather than
mystery.

Ledger 513 rows (unchanged), PENDING 37; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 199: the doubling class closed by experiment (no rows)
Round 198 found `add si,si` where MSC emits `shl si,1`, so this round asked the direct
question: **is `add reg,reg` reachable at all?** Six source forms were compiled for `x * 2` -
`x * 2`, `x + x`, `x << 1`, `y = x; y += y;`, `2 * x`, and `x * g` - and **all six** produce
`D1 E0`.

So MSC never emits `03 C0` for a doubling, in any context or under any flag. That closes the
"add reg,reg doubling" class - **37 units, 4 767 bytes** in `BLOCKED.md` - as *unreachable*
rather than unexplained, and the same statement now covers `41d8:000c`'s index scaling and
`4e11:007e`'s value doubling: one behaviour, not two.

This is the largest class the project has been able to close with a single experiment, and it
is closed with six lines of C and one compile - which is what the accumulated documentation
was for.

Ledger 513 rows (unchanged), PENDING 37; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 198: doubling in address arithmetic (no rows, PENDING record)
`41d8:000c` (30 B) is a far-pointer subscript through a call result:

    int __far *p;
    p = h(g_2f5c);
    return p[i];

Under `/G1 /Ox` **28 of 30 bytes match**, and the two that do not are the index scaling: the
original emits `03 F6` (`add si,si`), MSC emits `D1 E6` (`shl si,1`). That is the same
doubling difference as `4e11:007e` (round 139), and seeing it here matters because it is
**address arithmetic** rather than a value computation - so the doubling idiom is not a
property of `x * 2` in an expression, it is how the original compiler scaled any index.

Recorded as PENDING with that diagnosis. Two shapes were compiled (`p[i]` on a variable and
on the call result directly) and both give MSC's `shl`.

The unit is also a good example of why the ledger has a PENDING state at all: the C is
certain, the difference is two bytes, the cause is named, and nothing source-level closes it.

Ledger 513 rows - MATCH 38, RELOCS 436, ASM 2, **PENDING 37**; verify and checkled
green; own-code coverage 11 260 B (3.840 %).

## Round 197: the push-order rule tested against the whole pool (no rows)
Round 196's rule says a unit whose prologue is `56 57` (SI saved before DI) can still match,
while `57 56` cannot. That is directly testable: **seven** unmatched units have the
`55 8B EC 56 57` prologue, and this round read all seven.

All seven carry a different wall, none of them the push order:

| unit | what blocks it |
|---|---|
| `1118:000c`, `111b:000a` (18 B) | `les di,[bp+06]` - a far pointer loaded in one instruction |
| `1119:000e` (18 B) | sets `cx`/`di` and calls without arguments (a `rep stosw` helper) |
| `194e:0004` (26 B), `194b:000f` (37 B) | `mov ax,cs` / `mov ds,ax` - segment registers as values |
| `1265:0004` (43 B) | `repne scasb` inline string search |
| `10b9:0007` (59 B) | far call through a stored vector, plus segment work |

So the push-order rule did not unlock anything, which is itself the answer: the units that
have `56 57` are blocked earlier, and the units blocked *only* by push order do not exist in
the pool. The rule is still worth keeping - it prevents mis-diagnosing a future candidate -
but it is a rule about a corner this binary does not occupy.

That is the fourth "rule confirmed, no units behind it" result in ten rounds, and it is
consistent with the summary's conclusion: the remaining pool is blocked at the level of
whole idioms (segments, string instructions, far pointers), not at fine register details.

Ledger 512 rows (unchanged), PENDING 36; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 196: the prologue push order (no rows)
`31cd:0006` (34 B) is a counted loop:

    register int n;
    n = h1();
    if (n) { do { h2(a); } while (--n); }

Three shapes were compiled - a plain local, a `register` local, and an early `return` instead
of the `if` block. The `register` version gets the *assignment* right - `n` in SI, the
parameter in DI, exactly as the original - and then differs in **one instruction pair**: the
original saves DI first (`57 56`), MSC saves SI first (`56 57`).

That is a new, precise fact and it is now in `docs/WALLS.md`: the prologue push order is
fixed by register number and cannot be steered from the source. It also explains a couple of
earlier near-misses that I had attributed to the assignment rather than the save order.

The practical value is a screening rule: a unit whose prologue is `57 56` and whose body
otherwise matches is at this wall; a unit whose prologue is `56 57` may still match.

Ledger 512 rows (unchanged), PENDING 36; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 195: a one-page summary of the whole project (documentation round)
`docs/PROGRESS.md` is now ~190 round notes long, which is the right record and the wrong
front door. Added **`docs/SUMMARY.md`**: results in four numbers, the seven walls that
actually matter with their witnesses, the five working methods that produced the rows, what
would move the needle (and what would not), and a reading order. Linked from the index.

The section worth quoting is the last one: the seventeen walls are not reachable from
source, and the 36 PENDING rows are the evidence rather than the excuse - each has its C
recovered, each misses by one to six bytes of compiler choice, and each can be re-tested in
one command if a matching toolchain ever appears.

The round itself added no rows; it also produced no claims that the ledger does not already
support, which is the only standard a summary should be held to.

Ledger 512 rows (unchanged), PENDING 36; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 194: the long comparison recorded, and a full sweep (no rows)
`2e68:000c` (50 B) had been transcribed in round 170 and found one byte short, but never
entered in the ledger. It is now a PENDING row:

    int f(long x, long y) { if (x < y) return -1; if (x > y) return 1; return 0; }

The two-word signed comparison matches instruction for instruction - both halves, both
carry chains, both branches - and the only difference is one byte of branch distance across
the `90` in `B8 01 00 EB 03 90 33 C0`. That makes it the **sixth** witness of the padding
mechanism and the cleanest of them, because nothing else in a 50-byte function differs.

Then ran `tools/verify.py` without `--fast`: **512/512 rows ok** (MATCH 38, RELOCS 436,
ASM 2, PENDING 36) - the seventh full sweep.

Worth noting what the PENDING set now contains: 36 rows, every one a function whose C has
been recovered and whose bytes differ by between one and six bytes of compiler-internal
choice. If a toolchain matching the original ever becomes available, `tools/recheck.py` can
convert them in bulk; until then they are documented evidence of where the boundary lies.

Ledger 512 rows; verify (full) and checkled green; own-code coverage 11 260 B (3.840 %).

## Round 193: a retry loop with two register locals (no rows)
`2b9a:0000` (46 B) is a do/while retry loop found by the adjacency filter:

    register int r, x;
    x = a0;
    do {
        r = h1();
        if (r >= 0) x = r;
        r = h3(h2(x, x));
    } while (r);
    return x;

The original keeps `x` in **DI** and `r` in **SI**; both declaration orders were compiled and
MSC always gives SI to `x` - the value assigned first and live across the whole loop. That is
the clearest instance yet of round 161's rule that the assignment follows *lifetime* rather
than declaration order: the longest-lived value gets SI, and here the original's compiler
chose DI for exactly that value.

So the round-159 DI recipe works when the parameter (short-lived) goes to DI, and this unit is
the mirror image - it needs the *long-lived* value in DI - so the recipe does not apply.

The adjacency filter has now produced rows from both directions and is delivering roughly one
matchable unit per three candidates, with the rest landing on named walls. That is a fair
description of the remaining pool as a whole: it contains real functions whose C is
recoverable, gated on about a dozen compiler decisions that no source form reaches.

Ledger 511 rows (unchanged), PENDING 35; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 192: the pending registry grows to nine (tooling round)
Extended `src/pending/pending1.c` and `tools/pending.txt` with three more of the ledger's
PENDING hypotheses, so that a third of them are now machine-re-testable:

| row | what it waits for |
|---|---|
| `4aae:0006` | a `90` after an early return's jump |
| `3d91:0020` | two return paths joined differently |
| `31df:0004` | a two-case switch walked with `inc`/`dec` |

All nine registered rows compile from one file (802 bytes of object) and all nine still
differ - the registry is 9 of the 35 PENDING rows now, and `tools/recheck.py --sweep` retests
the whole set across five flag combinations in about a minute.

One small defect surfaced and was fixed on the way: `P_3D91` referenced its globals before
declaring them, so the *whole file* failed to compile and every row reported "source did not
compile". That is the registry's own failure mode - one bad row hides the others - and the
tool reported it per row rather than crashing, which is why it took one command to see.

Ledger 511 rows (unchanged), PENDING 35; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 191: a small switch, and how the two compilers differ (no rows, PENDING record)
`31df:0004` (48 B) is a two-case dispatch:

    switch (sel) {
    case 0: h1(v); break;
    case 1: h1(v); h2(v); break;
    }

The original distinguishes the cases with an **`inc`/`dec` chain** - `inc ax` / `jz` to the
default, `dec ax` / `jz` to case 0, `dec ax` / `jz` to case 1 - which is only valid because
the cases are consecutive, and which also folds the default into the fall-through. MSC emits
a `cmp`/branch chain instead, and an if/else chain gives frame compares (`83 7E`). Three
source forms were compiled and none reproduces the chain.

So this is another sub-case of wall 9, this time about *strategy* rather than opcode: for a
dense small switch the original compiler walks the case values with `inc`/`dec`, and MSC
compares. Recorded as PENDING with that diagnosis.

The two large units tried this round and last (`4a9f:0004`, `31df:0004`) both came from the
reversed adjacency filter and both ended up as documented walls rather than rows - which is
the filter doing its job, just at a stage where most of what it finds is blocked.

Ledger 511 rows - MATCH 38, RELOCS 436, ASM 2, **PENDING 35**; verify and checkled
green; own-code coverage 11 260 B (3.840 %).

## Round 190: a seventeenth wall - range guards and the index register (no rows)
Worked larger units from the reversed adjacency filter. Two transcribed, both blocked by the
same thing:

- `4a9f:0004` (34 B) is a bounds-checked word-table lookup -
  `if (i >= 0 && i < 6) return g_9965[i]; return -1;` - and the first difference is that the
  original loads `i` into BX once (`56 8B 5E 06`) and tests the register twice, while MSC
  compares the frame slot directly (`83 7E 06 00`).
- `4690:0000` (34 B) is `r = h(a, b); if (r > 0) return r - 1; return g_9946;` - under `/Ox`
  MSC gives it a frame (`ENTER`) because of the temporary, so the shape diverges.

The first one is the fourth unit with the identical pattern (`43a1:0000`, `3e48:000a`,
`2141:00a6` are the others), so it is now **wall 17** in `docs/WALLS.md`: a bounds-checked
table lookup caches the index in BX and MSC compares the frame slot. No `register` placement
changes it, because registering the parameter costs the function its other register.

The rule is useful in both directions: a unit whose guard tests a register loaded once from
the frame is at this wall, and a unit that tests the frame slot directly is probably *not*
the function I was about to write.

Ledger 510 rows (unchanged), PENDING 34; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 189: a shape-matching mode for sibling search (tooling round)
`tools/reuse.py` only found *byte-identical* siblings, which is a narrow idea of reuse: two
functions that differ only in **which globals they touch** are the same source with a
different identifier, and the project has several such pairs already (`1ab9:0004` and
`3c09:0006` are both lazy-initialisation shapes).

Added `--shape`: it normalises a second time with absolute data addresses masked
(`A1`/`A3`/`A0`/`A2` operands and `C7`'s `[disp16]`), so units that differ only in their
globals become candidates - `match.py` still has to confirm each one, so a false candidate
costs a compile rather than a bad row.

The run over the current 510-row ledger finds **0 candidates**: no unmatched unit is a
constant-renamed copy of a verified row at the same size. That is a genuine negative - the
globals in this binary vary in *kind* (segment values, table bases, state words), so
functions that differ only by address are rarer than they look.

Ledger 510 rows (unchanged), PENDING 34; verify and checkled green; own-code
coverage 11 260 B (3.840 %).

## Round 188: the adjacency filter run backwards (no rows, PENDING record)
The filter so far looked for units that *begin* where a verified row ends. Reversed - units
that **end** where a verified row begins, i.e. the function immediately before a matched one
- it yields **57** candidates, and two were transcribed:

- `4aae:0006` (26 B) is `int f(int a) { if (a == -1) return a; return h(a); }`, the same
  shape as round 122's row `37ec:0006` that matched, but this one has a `90` after the early
  return's jump (`EB 07 90`) where MSC emits nothing. That is the **seventh** witness of the
  late-peephole padding and the first in an early-return shape - recorded as PENDING.
- `47e8:000e` (28 B) is `int f(int a) { if (a == -1) return a; return h() + a; }`, two
  branch-distance bytes from matching for the same reason.

So both directions of the adjacency filter are productive for *candidates*, and both have now
handed their discoveries to the same wall. That is worth knowing: the padding is no longer a
special case of return paths, it is the single most common remaining cause across every
filter that finds anything.

Ledger 510 rows - MATCH 38, RELOCS 436, ASM 2, **PENDING 34**; verify and checkled
green; own-code coverage 11 260 B (3.840 %).

## Round 187: full sweep, and a scaled-long argument that resists (no rows)
Ran `tools/verify.py` without `--fast`: **509/509 rows ok** (MATCH 38, RELOCS 436, ASM 2,
PENDING 33) - the sixth full sweep, and the first since round 178. The false-positive risk
noted in round 186 therefore did not affect the ledger: every row's size is within its
object symbol.

Then tried `3aed:0006` (38 B) from the adjacency filter, a call whose first argument is a
`long` built by scaling a parameter:

    h((long)p3 * 10 + p2 + 0x14, p4);

The original computes `ax = p3*10 + p2 + 0x14` and sign-extends into `dx`, but MSC under
`/Os` pushes a constant before doing any of that (the parameter offsets differ from the
first load), and under `/Ox` it evaluates the two parameters in the opposite order. Two
source shapes were tried and both miss at the first load, so this is wall 9 again - not a
finding, just another data point that the scaled-long idiom is not reachable.

The adjacency filter has now yielded four rows and is thinning: of the seven mid-size
candidates, one is this unit, two are wall-2/16 witnesses, and the rest carry segment or
port operations.

Ledger 509 rows; verify (full) and checkled green; own-code coverage 11 260 B (3.840 %).

## Round 186: the padding wall gains a sixth witness (no rows, PENDING record)
Continued the adjacency filter with `4962:000c` (48 B), a table scan:

    for (i = 0; g_f623[i] != -1; i++) { if (g_f623[i] == a) return 1; }
    return 0;

Under `/G1 /Os` the transcription matches for **46 of 48 bytes** and the difference is the
now-familiar one: the original's loop entry is `EB 04 90` (a jump over a `90`) where MSC
emits `EB 03`. That is the sixth witness for the late-peephole padding documented in round
172, and the first one found in a *loop* rather than in a conditional's return paths - which
broadens the mechanism from "duplicated epilogues" to "any block shortened after layout".

Recorded as PENDING. Deliberately **not** registered in `tools/pending.txt`: the object's
symbol is 46 bytes while the unit is 48, so a size-48 comparison reads two bytes into the
next function and would report a false hit. That is a trap worth naming - `match.py --size`
must never exceed the object symbol's length, and the one time it did here it produced a
"match" that was really the following function's bytes.

Ledger 509 rows - MATCH 38, RELOCS 436, ASM 2, **PENDING 33**; verify and checkled
green; own-code coverage 11 260 B (3.840 %).

## Round 185: the adjacency filter pays twice (28 B)
Worked further through the 80 units that begin where a verified row ends. `1ec0:0004`
(28 B) took two attempts and the second one is instructive:

    struct S s;
    s.x = 0;
    h(&s, &s, 0x33);
    return s.x;

Without the `return`, the epilogue goes straight to `leave`; the original reloads the field
into AX first (`8B 46 F2`), which is the only difference in the whole 28 bytes. So a unit
whose epilogue starts with a load from the frame instead of `leave` is telling you the
function **returns** something it stored - and the frame size (`enter 0x0E, 0`) gave the
struct's size away as 14 bytes.

Two of the last two rounds have produced a row from the same adjacency filter, which makes it
the best remaining source of candidates: the functions adjacent to matched ones were written
by the same hand, in the same module, and often with the same idioms - the struct-passed-by-
far-pointer idiom here is exactly the kind of thing that repeats within a module.

Ledger **508 rows** - MATCH 38, RELOCS 436, ASM 2, PENDING 32; verify and checkled
green; own-code coverage **11 260 B (3.840 %)**.

## Round 184: a new search heuristic pays immediately (18 B)
Screened for units that **begin exactly where a verified row ends** - the next function in
the same translation unit - which is a tighter version of the "segments with matches"
heuristic: 80 such units exist, the first of them was transcribed and it matched.

`4e75:000a` (18 B):

    h1();
    h3();
    h2(-1);

The one subtlety was the epilogue: the function is `__far __pascal` with no parameters, so
it ends in a bare `retf` (`CB`) rather than cdecl's `ret` (`C3`). That single byte was the
only difference on the first attempt, and it is now a recorded tell - a `CB` epilogue with no
`pop` in front means the function is far, whatever the calls look like.

The "begins where a verified row ends" filter is worth keeping: it is the strongest form of
the "same module, same style" idea, because the two functions were adjacent in the original
source file, and there are 80 candidates against the 49 the looser filter produced.

Ledger **507 rows** - MATCH 38, RELOCS 435, ASM 2, PENDING 32; verify and checkled
green; own-code coverage **11 232 B (3.831 %)**.

## Round 183: a fragment proved to be one, and a clean probe (no rows)
Tried `2daa:000a` (17 B) as a `__fastcall` long XOR - `g_1be8 ^= v; h();` - and the
transcription came within **one byte**: everything matches except that the original ends
`C9 CA 02 00` (`leave` / `retf 2`) where the object ends `CB`.

`leave` implies a frame, and the unit has no `push bp`: so the unit is a **fragment of a
function that starts before the segment boundary**. Reading backwards confirms it - at
`2daa:0000` the code is already mid-function (`call`, two global loads, the XOR pair, a
second `call`, then `leave`), and the prologue lies in the previous segment. The inventory
cut the function twice (`2daa:0000` and `2daa:000a`) and neither piece is a function.

That is the second mis-cut region found (`2141:00a6` / `2141:00b4` was the first, a function
split at its `jmp`), and it has a one-line screening test that the classifier already
applies: a unit that contains `C9` or `5D` but does not start with `55 8B EC` is a fragment.
Both cases are in the "fragment (no prologue)" class, which is why they were correctly
excluded from the candidate pools - the lesson is only that the *reason* is worth knowing
before spending a compile on one.

Also ran `tools/probe.py` across the whole calibration corpus: **0 pattern hits**, as in
round 146.

Ledger 506 rows (unchanged), PENDING 32; verify and checkled green; own-code
coverage 11 214 B (3.825 %).

## Round 182: the pending registry gains a flag sweep (tooling round)
`tools/recheck.py` now takes `--sweep`: for every registered pending row it recompiles the
source under the registered flags **and** the four common alternatives
(`/G1 /Os`, `/G1 /Ox`, `/G1 /Ot`, `/G0 /Os`, `/G0 /Ox`), stopping at the first that matches.

The first run covers six rows in thirty compiles and reports all six still differing - which
is the expected result, and also the point: the negative answer that used to cost a round
per unit now costs one command, so the set can be re-tested whenever a wall's understanding
changes.

Two useful properties of the design:

- the sweep reports the flags that came *closest* even when nothing matches, so a row that
  improves under a different flag is visible;
- adding a row is one line in `tools/pending.txt`, so the registry grows as near-misses are
  found rather than being re-derived.

Ledger 506 rows (unchanged), PENDING 32; verify and checkled green; own-code
coverage 11 214 B (3.825 %).

## Round 181: the PENDING rows become a testable registry (tooling round)
Thirty-two ledger rows are PENDING: the C is believed correct and each misses by a byte or
two. Until now each one was prose in a table, so re-testing them meant re-reading and
re-transcribing them by hand - one round per unit, or nothing.

Added `tools/recheck.py` and `tools/pending.txt`. The manifest lists, for each pending
hypothesis, the source file, the flags, the compiler and the address/symbol/size; the tool
compiles each source **once** and matches every row it lists, printing which ones pass. The
first six are registered in `src/calib/pending1.c`:

| row | what it is waiting for |
|---|---|
| `2a28:0000`, `2a29:000c` | the clamp pair - working value in DX, not AX |
| `20b4:0130` | saved value pushed from AX rather than from the frame |
| `3ebd:0068` | `bx=ax` before `es=dx` |
| `20f6:0000` | `and` instead of `test` |
| `2603:463c` | `array[i]` loaded before the table byte |

All six still differ, so nothing changed - but the set can now be re-tested after any
change to a wall's understanding, in one compile instead of six rounds. That is the point:
the pending rows are the project's most valuable asset after the verified ones, and they
were the only part of the ledger that could not be machine-checked.

Also registered `tools/regsweep.py` in `docs/README.md`, which had been added in round 151
and never indexed.

Ledger 506 rows (unchanged), PENDING 32; verify and checkled green; own-code
coverage 11 214 B (3.825 %).

## Round 180: the `bx=ax` / `es=dx` order gets a second witness (no rows)
Screened the smallest one-call units (9-18 bytes, classified by call count) and transcribed
`3ebd:0068` (17 B):

    return *h(g_29c0);

where `h` returns an `int __far *`. It is **one byte pair** from a row, and it is the same
pair as round 146's `3ede:000a`: the original first moves the offset into BX and then the
segment into ES (`8B D8 8E C2`), while MSC loads ES first (`8E C2 8B D8`). Four source
shapes were compiled - a direct `*h(...)`, a cast, a subscript and a variable - and all four
give MSC's order, so the sequence is fixed by the code generator and not by the expression.

Two witnesses with identical structure now make this a distinct sub-case of wall 9 worth
naming: **the segment register is loaded before the offset**, always. Recorded as a PENDING
row alongside `3ede:000a`.

The screen itself is now thin: eleven tiny one-call units exist, and the others are
fragments (`3d91:000e` starts mid-instruction), a doubling (`29e6:0002`), a long XOR taking
its operands in registers (`2daa:000a`), or the `b451`/AH-call wrappers.

Ledger 506 rows - MATCH 38, RELOCS 434, ASM 2, **PENDING 32**; verify and checkled
green; own-code coverage 11 214 B (3.825 %).

## Round 179: `__fastcall` is the missing calling convention for a whole family (no rows)
Several unmatched units begin `56 8B F0` - save AX in SI, no frame - which I had been
treating as an "argument in AX" oddity. It is simply **`__fastcall`**: the first argument
arrives in AX and the callee saves it.

`20f6:0000` (23 B) is the clean example:

    void __fastcall f(unsigned x) { if (x & 1) h(); if (x & 2) h(); }

and MSC reproduces the calling convention **exactly** - same `56 8B F0` prologue, same
argument handling, same far calls. It is two bytes from a row, and the two bytes are
`25 01 00` (`and ax,1`, which destroys AX and is why the compiler reloads it from SI) versus
MSC's `F7 C6 01 00` (`test si,1`). Three source shapes (`x & 1`, `x % 2`, a register
temporary) all give `test`.

So this is not a calling-convention problem at all - `__fastcall` is supported and matches -
but an opcode choice (`and` versus `test`) inside it. That makes the several `56 8B F0` units
worth revisiting with the convention identified, even though this particular one is blocked.

Recorded as a PENDING row with the diagnosis.

Ledger 505 rows - MATCH 38, RELOCS 434, ASM 2, **PENDING 31**; verify and checkled
green; own-code coverage 11 214 B (3.825 %).

## Round 178: wall 16 resists its obvious fix, and a full sweep (no rows)
Tried the natural way to produce a shared epilogue on `315b:0008`, whose if-arm ends in a
call: write the arm with an explicit **early `return`** so the fall-through path is the one
that reaches the tail.

    if (i >= 0 && i < 0x1A) { g_7d22[i].v = 0; h(0x0F, i); return; }
    h2(i);

MSC still duplicates the five-byte `pop si` / `leave` / `retf 4` tail after both calls, under
`/Os` and `/Ox`, so the difference is not about which arm falls through - it is that MSC
never emits the `jmp` over the else-arm to a shared tail in a function of this shape. Wall
16 stays open, with that negative result recorded.

Then ran `tools/verify.py` without `--fast`: **504/504 rows ok** (MATCH 38, RELOCS 434,
ASM 2, PENDING 30) - the fifth full sweep, covering every row added since round 145.

Ledger 504 rows; verify (full) and checkled green; own-code coverage 11 214 B (3.825 %).

## Round 177: a sixteenth wall - duplicated versus shared epilogues (no rows)
Following round 176's queue, `315b:0008` (53 B) was transcribed:

    if (i >= 0 && i < 0x1A) { g_7d22[i].v = 0; h(0x0F, i); }
    else h2(i);

with `g_7d22` an array of 4-byte structs whose only member is a `long` - so round 175's rule
supplies the `2B C0` and the two word stores exactly. Everything matches except the
**epilogue**: MSC emits the five-byte `pop si` / `leave` / `retf 4` tail twice, once after
each call, where the original shares one and jumps to it (`EB 07`). The two branch distances
then differ by exactly that five bytes.

That is a *layout* choice rather than a missed peephole, so it is now wall 16, with
`315b:0008` as its clearest witness and four more units that differ only in this way
(`3cd1:02f2`, `5026:013e`, `3d91:0020`, `37c1:0004`). It is the second most common
remaining cause after the padding itself.

Practical rule recorded: a unit whose two arms end in identical instruction runs with a
short `jmp` between them is at this wall and belongs in PENDING.

Ledger 504 rows (unchanged), PENDING 30; verify and checkled green; own-code
coverage 11 214 B (3.825 %).

## Round 176: the six-byte zero resists, and why (no rows)
Followed round 175's note on `2b2e:0000` (29 B), which zeroes six bytes through a far
pointer returned by a call:

    p = h(1, 6);
    ... 2B C0 (sub ax,ax) then three 26 89 47 xx stores ...

Three source shapes were compiled - a three-`int` struct zeroed as a whole, the three fields
assigned individually, and a chained assignment - and all of them make MSC emit
**immediate stores** (`26 C7 47 xx 00 00`) instead of zeroing a register once and storing it
three times. The original's register-store form needs a single zeroed *value* to store
three times, and no expression form MSC accepts produces that; a zeroed
struct-assignment would go through a copy routine.

Also looked at `1fff:0002` (33 B) and `324b:0008` (40 B): the first sets `es` from a global
and clears a word through it, which needs a segment register (`es` is never a C value);
the second is a 32-bit clamped subtract whose comparison is exactly the long-comparison
idiom, but it needs `2B C0` **and** `2B C9` together and is a good next candidate for the
long-zeroing rule found in round 175.

Ledger 504 rows (unchanged), PENDING 30; verify and checkled green; own-code
coverage 11 214 B (3.825 %).

## Round 175: round 174's narrowed wall pays a row immediately (15 B)
Round 174 found that MSC emits `2B C0` (`sub ax,ax`) when the zero being stored is
**wider than AX**. That prediction was tested on the first small unit containing `2B C0`,
and `1ab9:0004` (15 B) matched on the first compile:

    g_536e = h();
    g_9650 = 0;

with `g_9650` declared `long`. The `long` store makes MSC choose the older zeroing form,
producing exactly the image's `2B C0 A3 <lo> A3 <hi>`.

So wall 12's narrowed statement is now a *rule with a use*: a unit whose zeroing is `2B C0`
is reachable when the zero is being widened, and the way to get it is to declare the
destination `long` (or otherwise wider than the source value), not to look for a flag.

Also tried `2b2e:0000` (29 B), which zeroes six bytes through a far pointer returned by a
call (`2B C0` then three `26 89 47 xx` stores). Not yet expressed: writing `*(long *)p = 0;
*(int *)(p + 4) = 0;` gives a shorter symbol, and `p[0] = 0` drops the zeroing entirely. The
six bytes are probably a small struct zeroed as a whole, which is the next thing to try.

Ledger **504 rows** - MATCH 38, RELOCS 434, ASM 2, PENDING 30; verify and checkled
green; own-code coverage **11 214 B (3.825 %)**.

## Round 174: a cut unit, and a zeroing opcode that goes the other way (no rows)
Worked `cutwin.py`'s list - units whose inventory window cuts the function short. The
smallest pair, `3d85:000e` (window 10 B, real 47 B), was transcribed in full:

    if (!g_1b0e) g_1b12 = 0;
    g_1b10 += a;
    g_1b0e = h(g_1b0e, (long)g_1b10);

Everything matches except **one byte**: the original zeroes AX with `33 C0` (`xor`) where
MSC uses `2B C0` (`sub`). Three spellings of the zero give MSC's form.

That is the *reverse* of the usual "sub ax,ax" complaint, and it is informative: the
context is a `long` global cleared with two word stores, so **`2B C0` is not unreachable in
general** - only for a plain `int` zero. Wall 12 is now narrowed rather than confirmed, and
`docs/WALLS.md` says so.

Two tooling notes: `tools/dis.py` crashed on `mov al,imm8` (opcode `B0`-`B7` had a
malformed table entry) and that is fixed; the crash came from using the dumper on a unit
that starts with `lds`, which is how the bad entry surfaced.

Both units are recorded as PENDING, since the C is known and one byte is the difference.

Ledger 503 rows - MATCH 38, RELOCS 433, ASM 2, **PENDING 30**; verify and checkled
green; own-code coverage 11 199 B (3.819 %).

## Round 173: the call-free global screen is exhausted (no rows, PENDING record)
Screened for units with **no calls at all** that touch globals - the shape most likely to
transcribe directly, since there is no prototype or calling-convention question. There are
**eight**, and all eight carry a named wall:

| unit | shape | wall |
|---|---|---|
| `3e5c:0006` (18 B) | `g == 1` compiled with `dec` | 9 (opcode choice) |
| `3d91:0020` (17 B) | `return g < g` | 2 (return-path join) |
| `1090:0007` (17 B) | value arrives in CX | 7 |
| `2141:00b4` (14 B) | tail of a split function | 14 |
| `4e9b:0008`, `39e9:000a`, `3dbb:0006`, `3f44:00eb` | long/segment/pointer work | 5, 11, 15 |

`3d91:0020` was transcribed and is the **sixth** unit in the one-byte-branch-distance
family - the same shape as `5026:013e`, now recorded as PENDING alongside it. That the
entire "no calls, globals only" class is walled is a useful negative result: the remaining
work really is dominated by compiler-internal choices, not by anything the source can
express.

Ledger 502 rows - MATCH 38, RELOCS 433, ASM 2, **PENDING 29**; verify and checkled
green; own-code coverage 11 199 B (3.819 %).

## Round 172: the padding wall stated as one mechanism (no rows)
Round 171 found the fifth unit with the same two-byte fingerprint, so this round wrote the
mechanism down in `docs/WALLS.md` instead of leaving five separate "so close" notes.

The five witnesses - `3cd1:02f2`, `2e68:000c`, `1fe2:000a`, `48eb:000c`, `4998:000c` - all
have the shape "a constant stored on one path, a jump over the other path's constant, a `90`
in the gap", and in all five the **jump distance counts the `90`**. That is what makes the
mechanism identifiable: the block was laid out with a 3-byte `mov ax,<imm16>`, the second
constant was shortened to the 2-byte `33 C0` afterwards, and the freed byte was filled
rather than the jump being re-laid-out. MSC emits `33 C0` *before* laying out the block, so
it never has a byte to fill.

The practical rule now recorded: a unit whose only difference is one byte of branch
distance across a `90` is **at** the wall, and belongs in PENDING rather than being retried
with another source shape. That saves future rounds from exactly the work this one didn't
do.

Ledger 501 rows (unchanged), PENDING 28; verify and checkled green; own-code
coverage 11 199 B (3.819 %).

## Round 171: a lazy initialisation, and another padding witness (21 B)
`3c09:0006` (21 B):

    if (!g_1934) g_1934 = h(0x100, 2);

A near cdecl function with no parameters and no locals, which is why it has no frame at all
and starts with `83 3E` (compare a global against an immediate). Both spellings of the
guard (`!g` and `g == 0`) produce byte-identical code, so it matched on the first compile.

Also tried `1fe2:000a` (21 B), the `if (g_9b30) { ...; return -1; } return 0;` shape. It is
**two bytes** short and the two bytes are the branch distance across the padding in
`B8 FF FF EB 03 90 33 C0` - the same late-peephole form as `3cd1:02f2` and `2e68:000c`,
now a **fifth** witness. All five are the same shape: a constant assigned on one path, a
jump over the other path's constant, a `90` in the gap.

Revising the wall's description is the next round's job; five witnesses with identical
structure is enough to state it as a single mechanism rather than a family of coincidences.

Ledger **501 rows** - MATCH 38, RELOCS 433, ASM 2, PENDING 28; verify and checkled
green; own-code coverage **11 199 B (3.819 %)**.

## Round 170: the five-hundredth row (46 B)
`4df7:000a` (46 B) is a guarded chain of calls whose last value is returned:

    if (h1(a)) {
        h4(0);
        h2(1);
        return h3(1, 0);
    }
    return 0;

All four callees are **far**; the first attempt had them near and the diff was one byte at
the first call (`E8` where the image has `90` - the start of the LINK /F translation of a
far call). With them far, the whole 46 bytes match, including the `33 C0` that only the
else path needs because the if-body returns through `h3`.

That makes **500 ledger rows**: MATCH 38, RELOCS 432, ASM 2, PENDING 28, of which 470 are
verified against the image and **11 178 bytes of own code (3.812 %)** are matched from
source.

Also tried `2e68:000c` (50 B), a two-word long comparison returning -1/1/0. Its structure
matches exactly and it is **one byte** short: the branch distance differs by exactly the
`90` in `B8 01 00 EB 03 90 33 C0` - the same late-peephole padding as `3cd1:02f2`, now seen
in a fourth unit.

Ledger **500 rows**; verify and checkled green; own-code coverage **11 178 B (3.812 %)**.

## Round 169: two byte globals, two different widenings (37 B)
`4c9c:065e` (37 B) pushes five arguments from globals and then calls a second function with
two constants:

    h1(g_995b, g_995c, g_9954, g_9956, g_9958);
    h2(1, 1);

The interesting part is that the two byte globals are pushed **differently**: the first as
`A0 <g>` / `2A E4` / `50` (zero-extended) and the second as `A0 <g>` / `50` (not extended).
One prototype explains both - `h1`'s first parameter is `int`, so the `unsigned char` is
converted for it, and its second is `char`, so no conversion happens. Declaring the first
parameter `unsigned char` instead removes the `2A E4` and loses the match, which is the
reverse of the intuition that matching the argument's type is the way to get matching code.

So round 165's rule now has its converse recorded by the same unit: **the prototype decides
the widening, in both directions.**

Ledger **499 rows** - MATCH 38, RELOCS 431, ASM 2, PENDING 28; verify and checkled
green; own-code coverage **11 132 B (3.797 %)**.

## Round 168: a missed sibling, and the tool bug behind it (32 B)
While looking for the twin of `2daa:001c`, `2dad:000c` (32 B) turned out to match the *same*
source - the two units differ only in which helper the middle far call reaches, i.e. a
relocated target. `tools/reuse.py` had reported **0 siblings**, and it should have found
this one, so the reason mattered more than the row.

Two real bugs, both now fixed:

- `tools/dis.py` did not decode **`68 imm16` / `6A imm8`** (push immediate), so it printed
  `68   ?` and the instruction walk desynchronised. That also means every `?` in a previous
  dump could shift everything after it - a silent hazard, now gone;
- `tools/reuse.py`'s `norm()` masked operands with a **byte scan**, so a `68 E8 1B`
  (push 0x1BE8) looked like a call `E8 1B ...` and it masked the wrong two bytes, leaving
  the actual `9A seg:off` target in place. Two units that differ only in that target then
  normalised differently and the pair was missed.

`norm()` now walks instructions with the project's own decoder and masks only genuine
operand bytes; the two units normalise identically, and `reuse.py` finds nothing new but
would now catch pairs like this.

Ledger **498 rows** - MATCH 38, RELOCS 430, ASM 2, PENDING 28; verify and checkled
green; own-code coverage **11 095 B (3.784 %)**.

## Round 167: a third row from the `char` prototype find (32 B)
`2daa:001c` (32 B), the next unit in the byte-argument class:

    h1(a);
    h3(g_1bec, (char *)0x1BE8);
    h2();

Three details, two of them already known:

- the byte global pushes as-is because `h3` declares `char` (round 165's rule);
- the constant pointer is `(char *)0x1BE8` - a near pointer pushed with `68 imm16`;
- the last call takes **no argument**. Writing the sequence as `h2(h3(...))` inserts a
  `push ax` that the image does not have - the only difference between the first attempt
  and the match was that one instruction.

That last point is the mirror of the usual C idiom: the natural way to write "call h3, then
call h2" when h3 returns a value is to nest or to assign, and both leave a push behind. Here
the original simply discards the result.

Ledger **497 rows** - MATCH 38, RELOCS 429, ASM 2, PENDING 28; verify and checkled
green; own-code coverage **11 063 B (3.773 %)**.

## Round 166: two rows in two rounds from the `char` prototype find (32 B)
Round 165's discovery that a byte argument pushes unconverted only when the *callee*
declares `char` reopened the "byte argument" class (23 units). The first one tried,
`2127:000c` (32 B), matched:

    void f(char a, int b) { if (h1(a, b)) h2(a); }

It needed a second insight: the function is **`void`, not `int` returning 0**. The skip path
falls into the epilogue without zeroing AX, so an `int` version adds a `33 C0` and the
branch becomes `jz +0x0B` instead of `jz +0x09`. The zero the caller sees is the one left
over from the `or ax,ax` test, so both behave identically - only the code differs. That is
now a section in `docs/CONVENTIONS.md` ("look at the skip path").

The size was also wrong on the first attempt (30 instead of 32, a prefix that happened to
match) and `verify.py` caught it with "does not end at a return instruction" - the tool
doing exactly what it was built for.

Ledger **496 rows** - MATCH 38, RELOCS 428, ASM 2, PENDING 28; verify and checkled
green; own-code coverage **11 031 B (3.762 %)**.

## Round 165: a row from where the `char` is declared (21 B)
`2d49:0034` (21 B) is a three-argument call whose first argument is a global byte:

    return h(g_9944, a, 1);

Three compilations, three different widening behaviours, and only one matches:

| callee's first parameter | the byte is | matches |
|---|---|---|
| `char` | `A0 <g>` / `50`, pushed as-is | **yes** |
| `int` | `A0 <g>` / `98` (`cbw`, sign-extended) | no |
| `int` with the argument cast to `unsigned char` | `A0 <g>` / `2A E4` (zero-extended) | no |

So the fix was in the **callee's prototype**, not at the call site - the opposite of the
usual instinct, and now recorded in `docs/CONVENTIONS.md` as a three-row table.

The same screen that produced this (`segments with verified rows`, 16-34 byte units,
excluding the register-pair family) also surfaced `37c1:0004` last round, so the filter is
carrying its weight.

Ledger **495 rows** - MATCH 38, RELOCS 427, ASM 2, PENDING 28; verify and checkled
green; own-code coverage **10 999 B (3.751 %)**.

## Round 164: a table scan down to one byte (no rows, PENDING record)
Picked `37c1:0004` (30 B) out of the small-unit screen and it turned out to be the closest
unit found yet:

    int f(void) { int i; for (i = 0; i < 16; i++) { if (g_6e34[i].f0 == -1) return i; } return -1; }

A scan of a 16-entry table of 0x34-byte structs, ending at address `0x7174` - and under
`/G1 /Ox` **thirty of thirty-one bytes match**, including the address-limit loop
(`81 FB <end>` rather than a counter compare), the `bx += 0x34` stride and the `-1` default.

The single remaining difference is the epilogue: the original shares the final `ret`
between its two exits (`8B C2 EB 03 B8 FF FF C3`), while MSC duplicates it and pads
(`8B C2 C3 90 B8 FF FF C3`). Three source shapes were compiled - two `return`s, a single
`return r` with `break`, and a `goto` - and MSC duplicates in all three, so this is the
mirror image of wall 2's usual complaint: here it is the *original* that shares a bare
`ret` where MSC makes two.

Recorded as a PENDING row. Note that this is also the first unit where `/Ox` both removes
the frame *and* keeps the address-limit loop, which confirms `/Ox` is the right flag for
"no-frame loop" units.

Ledger 494 rows - MATCH 38, RELOCS 426, ASM 2, **PENDING 28**; verify and checkled
green; own-code coverage 10 978 B (3.744 %).

## Round 163: full sweep, and one more unit on the register boundary (no rows)
Ran `tools/verify.py` without `--fast`: **493/493 rows ok** (MATCH 38, RELOCS 426,
ASM 2, PENDING 27), `checkled.py` consistent. Fourth full sweep; every row added since
round 145 - eight of them - rebuilt from source and re-matched in one pass.

Also worked `1e1e:0008` (33 B) from the `55 8B EC 57 56` family:

    register int b, a;
    b = b0; a = a0;
    h(a, b, c);
    return ((long)a << 16) | (unsigned)b;

The return is two registers assembled by the compiler (`8B C6 8B D7`), which MSC does
produce for that expression - and the call's three pushes and both parameter loads line up.
What does not is the assignment: the original has `b` in SI and `a` in DI, MSC the reverse,
under both `/Os` and `/Ox` and with both declaration orders. That is the same boundary as
rounds 160-161, and it is now the *dominant* remaining cause in this family: seven of the
fifteen `57 56` units have been read and all seven turn on it.

Ledger 493 rows; verify (full) and checkled green; own-code coverage 10 978 B (3.744 %).

## Round 162: a row from telling `mov ah,al` from `mov al,ah` (48 B)
`2b4b:0008` (48 B) is two calls whose results are combined:

    d = a0;
    x = h1(d, b, c);
    return x + ((unsigned)h2(d, b, c) << 8);

It took three attempts, and the third one is the interesting part. The original ends with
`8A E0 2A C0` - `mov ah,al` / `sub al,al` - which builds `byte << 8`. Writing the same
arithmetic as `h2(...) >> 8` on an `unsigned` return compiles to `8A C4 2A E4`
(`mov al,ah` / `sub ah,ah`), which **is a different program**: `8A E0` means the callee
returned a byte in AL, `8A C4` means the code is reading AH, i.e. the previous call's
leftovers. Declaring `h2` as returning `unsigned char` and shifting left instead gives the
original's bytes exactly.

Also had to fix the copied parameter: the original loads `[bp+0A]` - the **first**
parameter - into DI, not the third.

Recorded in `docs/CONVENTIONS.md` as the `8A E0` versus `8A C4` rule, because misreading a
byte-return is the kind of mistake that produces a plausible but wrong decompilation rather
than a compile error.

Ledger **493 rows** - MATCH 38, RELOCS 426, ASM 2, PENDING 27; verify and checkled
green; own-code coverage **10 978 B (3.744 %)**.

## Round 161: the register rule slips again (no rows)
Continued through the `55 8B EC 57 56` family with `3877:0000` (41 B):

    h2(h1(b, a, c, b, a, c, d));        /* seven arguments, then a nested call */

with `a` from the first parameter and `b` from the second, both in registers. Under `/Ox`
the unit is **two bytes from a row**, and they are the register assignment: the original
loads `di` from the second parameter and `si` from the first, MSC does the reverse.

Trying both declaration orders and both assignment orders produced a contradiction with
round 160's row:

| unit | declaration | assignment order | result |
|---|---|---|---|
| `3a3d:0006` | `register int r, a;` | `a` first | `a` -> DI |
| `3877:0000` | `register int a, b;` | `b` first | `b` -> SI, `a` -> DI |

The first is consistent with "first declared goes to SI" and with "first assigned goes to
DI"; the second fits neither. So the allocation is probably driven by **lifetime** - the
value that has to survive a call gets the callee-saved register, which is why the round-160
row worked with `r` (survives two calls) in SI and `a` (an argument) in DI.

That is now written down as the practical rule: for a unit that turns on a register choice,
try both declaration and both assignment orders, and expect lifetime to decide. Recorded in
`docs/CONVENTIONS.md` with the two data points, explicitly marked as not yet a law.

Ledger 492 rows (unchanged), PENDING 27; verify and checkled green; own-code
coverage 10 930 B (3.728 %).

## Round 160: the DI trick pays a row (28 B), and a second unit down to two bytes
Round 159's "move a parameter into DI" recipe was applied to the 15 units with a
`55 8B EC 57 56` prologue, and the first one matched:

**`3a3d:0006` (28 B)** - `a = a0; r = h1(a); h2(a); return r;` with `register int r, a;`.
The original keeps the parameter in DI and the call result in SI; the reversed
declaration order plus the folded copy produce `57 8B 7E 06` exactly, and the far/near
call pair is far then near.

Then `437e:0006` (43 B) was transcribed - a masked-struct write after a guard:

    r = h1(a);
    if (r >= 0) { g_866f[a].f0 &= 7; g_866f[a].f2 &= 0x7F; }
    return r;

It is **two bytes** from a row either way round: with `register int a, r;` the index
register is right but one access uses the other register; with `register int r, a;` both
registers swap (`8B 7E 06` where the original has `8B 76 06`). So the unit sits exactly on
the boundary the round-159 trick moves, which makes it the best next candidate for a
declaration-order sweep.

Ledger **492 rows** - MATCH 38, RELOCS 425, ASM 2, PENDING 27; verify and checkled
green; own-code coverage **10 930 B (3.728 %)**.

## Round 159: a parameter can be moved into DI after all (no rows)
Round 158 concluded that `20f9:000c` was unreachable because parameters are allocated
before locals. This round found the way around it, and it is now recorded in
`docs/CONVENTIONS.md`:

- MSC gives **SI to the first** `register` local and **DI to the second**;
- a parameter copied into a register local gets the load **folded** into the parameter
  fetch (`b = b0;` with `register int r, b;` emits `57 8B 7E 06` - push di; mov di,[bp+6]),
  so a parameter can be moved into DI without any extra instruction.

The swap in `20f9:000c` is fixed by that, and the unit moved from "two bytes, wrong
register" to "two bytes, `or` operand base": the original loads `a` into AX and ORs DI
(`8B 46 08 0B C7`), MSC reuses DI as the base (`8B C7 0B 46 08`). Four source shapes were
tried - `(a | b)`, `(b | a)`, `a != 0 || b != 0`, and the copy-to-local variants - and all
give MSC's form, so the base is chosen by "operand already in a register", not by source
order.

So the unit is one named wall (9) from a row rather than two walls, and the DI trick is
available for the other 14 units with that prologue.

Ledger 491 rows (unchanged), PENDING 27; verify and checkled green; own-code
coverage 10 902 B (3.718 %).

## Round 158: parameters are allocated before locals (no rows)
Screened for units whose prologue is `55 8B EC 57 56` - the two-register-local shape that
round 154's reverse-declaration trick solved - and found 15 of them. The simplest,
`20f9:000c` (44 B), was transcribed:

    int f(int a, register int b) {
        register int r;
        if ((a | b) != 0) { r = h1(); h2(a, b); return h3(r); }
        return 0;
    }

with `h3` taking its argument in AX (no push). Under `/Os` it is **two bytes from a row**,
and they are the *swap*: the original loads `b` into **DI** (`8B 7E 06`) and keeps `r` in
**SI**, while MSC gives SI to the first register declaration - and parameters are declared
before locals, so `b` gets SI and `r` gets DI.

That is a sharper statement of wall 4 than "assignment is unpredictable": **MSC allocates
parameters before locals**, so a unit that wants a local in SI and a parameter in DI is
unreachable, whatever the declaration order. Making both parameters `register` does not
help; it pushes the local to the frame (`ENTER`).

Recorded in `docs/WALLS.md` next to the register-reuse notes.

Ledger 491 rows (unchanged), PENDING 27; verify and checkled green; own-code
coverage 10 902 B (3.718 %).

## Round 157: a fifteenth wall - the encoding, not the allocation (no rows)
Sorted the smallest frameful units in segments that already match (7 candidates) and read
three of them:

- `2d49:0034` (21 B) pushes a global byte straight into a call's argument list
  (`A0 <g>` / `50`), i.e. a byte pushed without promotion - wall 12;
- `3ea9:0042` (23 B) doubles a value with `03 C0` (`add ax,ax`) - wall 8;
- `416f:011c` (31 B) builds a far pointer with `add ax,imm16` / `push ds` / `push ax` -
  wall 11's inlined `MK_FP`.

Then moved to the fragment class, where `159d:18f2` (9 B) is
`((char *)*(int *)0x10)[0x0A] &= 0x7F;` - a byte mask on the BIOS data area's pointer.
Five shapes were compiled (plain pointer, `register char *`, `register int` with a cast,
subscript, explicit `+ 10`); none produce the original's `8B 36 10 00` (`mov si,[0x0010]`),
because MSC always loads through AX or BX.

That is **wall 15**, and it is worth separating from the register-naming walls: those are
about *which* register the allocator picks, this one is about which *encoding* the
compiler is willing to emit at all. Recorded in `docs/WALLS.md` with the evidence.

Ledger 491 rows (unchanged), PENDING 27; verify and checkled green; own-code
coverage 10 902 B (3.718 %).

## Round 156: a no-frame comparison getter, two bytes short (no rows, PENDING record)
Widened the "near matched code" heuristic to segments with at least one verified row and
sorted by size, which surfaces much smaller units. `5026:013e` (17 B) is the simplest
candidate found so far:

    int __near __cdecl f(void) { return g_3950 < g_3952; }

No frame at all (it opens with `A1`, not `55 8B EC`), two direct global reads and one
comparison. Two details had to be right:

- the comparison is **`<`, not `>`** - the natural reading gives `jge` where the original
  has `jle`, and only the inverted source reproduces the branch;
- it is `__near __cdecl`, so the return is `CB`.

Under `/G1 /Ox` exactly **two bytes** remain: the original's first branch jumps over a
`33 C0` to a shared return (`B8 01 00 EB 02 33 C0 CB`), while MSC returns directly and
pads (`B8 01 00 C3 90`). That is wall 2's duplicate-epilogue form, the same one that
`13d5:000c` shows.

Recorded as a PENDING row. Also noticed along the way that `2141:00a6` and `2141:00b4`
are two halves of one 28-byte function that `units.csv` split - the second half starts
with the `jmp`/`nop` that made the first half look truncated.

Ledger 491 rows - MATCH 38, RELOCS 424, ASM 2, **PENDING 27**; verify and checkled
green; own-code coverage 10 902 B (3.718 %).

## Round 155: another unit down to two bytes (no rows, PENDING record)
Continued the "look near matched code" heuristic on `20b4:0130` (27 B, from a segment with
three verified rows):

    void __cdecl f(void) { int r; r = h1(); h2(); h3(r); }

with three far `__cdecl` callees. The `ENTER` frame matches under `/G1 /Os` - worth
noting, because it confirms that a cdecl function *with a local* is exactly the case where
`/G1`'s `ENTER` is correct - and every instruction matches except **two bytes**: the
original loads the saved value into AX before pushing it (`8B 46 FE` + `50`), while MSC
pushes the frame slot directly (`FF 76 FE`).

Three attempts to force the load (`volatile`, `r + 0`, `(int)r`) all still push memory, so
this is the "push memory rather than load-then-push" habit that also shows up in wall 10.

Recorded as a PENDING row with the exact difference.

Ledger 490 rows - MATCH 38, RELOCS 424, ASM 2, **PENDING 26**; verify and checkled
green; own-code coverage 10 902 B (3.718 %).

## Round 154: a row from the reverse declaration trick (33 B)
Rather than sweeping more variants, this round looked for unmatched units in segments
that already have several matched rows - the same module usually means the same style.
`3e19:0002` (33 B, a segment with 12 verified rows) is

    a = h1(); b = h2(); h3(); h4(a, b); return 0;

and it needed two things that are now recorded in `docs/CONVENTIONS.md`:

- **the register locals are declared in reverse**: the original assigns the first result
  to DI and the second to SI, while MSC gives SI to the first `register` local, so the
  declaration is `register int b, a;`;
- **the function returns `int` 0, not `void`**: the original's `33 C0` before the pops is
  the only difference from the `void` version, which is two bytes shorter.

The "look near matched code" heuristic is worth keeping: of the eleven unmatched units in
segments with three or more matches, this was the first one read.

Ledger **489 rows** - MATCH 38, RELOCS 424, ASM 2, PENDING 25; verify and checkled
green; own-code coverage **10 902 B (3.718 %)**.

## Round 153: four more sweep runs, and the linker question closed by construction (no rows)
`tools/regsweep.py` was run against two more units with known candidate sources:

| unit | template | variants x flag sets | result |
|---|---|---|---|
| `3874:000a` (38 B) | `h2(h1(c, b, a))` | 64 x 2 | no match |
| `4ab2:000c` (32 B) | `r = h1(a); if (r != -1) h2(r); return r;` with a `register int r` | 4 x 2 | no match |
| `4ab2:000c` | the same with a plain `int r` under `/G0` | 4 x 2 | no match |

Then the objective's "alternative linker" thread was closed. `toolchain` has three
`LINK.EXE` binaries, but `msc6b` and `msc7i` are **byte-identical** (LINK 5.1x), and the
only other one is the old `msc51` linker. More importantly a different linker *cannot*
change a row: `verify.py` compares the compiler's **object** against the image with
relocations masked, and the linker's only visible contribution - the
`/FARCALLTRANSLATION` rewrite of a far call into `90 0E E8` - is already modelled by
`match.py` as an equivalent form.

So that avenue is closed by construction, and `docs/GAP.md` now says so, next to the
compiler findings.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 152: the `|` operand order settled (no rows)
Continued the sweep work on `2603:463c`, the close PENDING row. Five source shapes were
compiled under `/Ox` and compared byte for byte:

| shape | code |
|---|---|
| `g_4642[n & 7] | g_76b4[n / 8]` | identical |
| `g_76b4[n / 8] | g_4642[n & 7]` | identical |
| `int b = n & 7;` then the OR | identical |
| `unsigned b = n & 7;` then the OR | identical |
| `n % 8` instead of `n & 7` | much worse (a full division) |

So MSC's evaluation order for `|` is **not** source-controlled: it always puts
`array[index]` into AL first and ORs the table byte second, while the original does the
reverse. That closes the unit for good rather than leaving it as "one more shape might
work", and it is recorded in `docs/WALLS.md` with the five-shape evidence.

`tools/regsweep.py` (round 151) was also run on the unsigned clamp pair:
`2a29:000c` with 64 register/signedness variants across two flag sets - no match, so the
DX-versus-AX difference is not a parameter declaration issue there either.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 151: a variant sweep tool, since guessing one shape at a time has run dry (no rows)
Round 150 named the bottleneck: the remaining near-misses differ in choices MSC makes
internally, so each unit needs several equivalent C shapes tried before one matches. Doing
that by hand costs a round per unit and has been yielding one row every five rounds.

Added **`tools/regsweep.py`**: it takes a template containing a function named `CAND`,
generates every combination of `register` and `unsigned` over its parameter list, compiles
each variant, and reports which ones match the target unit. One round can now test 64
source shapes against a unit in a few minutes, across several flag sets.

First uses found no hit, and that is itself informative:

| unit | variants | flag sets | result |
|---|---|---|---|
| `2a7e:0000` (67 B) | 16 | 3 | no match |
| `43a1:0000` (38 B) | 2 | 2 | no match |
| `1f72:0044` (40 B) | 4 | 2 | no match |
| `4d98:000a` (18 B) | 16 | 2 | no match |
| `2a28:0000` (28 B) | 64 | 3 | no match |

So the clamp unit's DX-versus-AX difference is **not** reachable by any combination of
`register` and signedness on its three parameters - which is worth knowing, because that
unit has been the project's canonical example of the register-assignment wall since round
123. The tool is now available for every future candidate, and its cost is one compile per
variant.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 150: half-way point; two more units read exactly (no rows)
Round 150 of 256. Two more small units decoded with the new tool:

- **`37f8:0008`** (20 B) is `int __far *f(int *p, int v) { *p = v; return (int __far *)p; }`.
  The store is a plain `mov [bx], ax`, but the return is `mov dx, ss` - the compiler
  inlined `MK_FP`'s segment half, which MSC cannot express without inline assembly. Wall
  11 ("inlined MK_FP"), but now with a witness that is *only* that: the whole function is
  otherwise six instructions.
- **`29e6:000c`** (22 B) is a fixed-point multiply, `c++; if (c == 0) return 0; return
  (unsigned char)(((unsigned)h() * c) >> 8);` with the 8-bit `mul bl` and `mov al,ah`.
  The original emits the **call before the increment**; MSC emits `inc` first, and
  forcing a variable to hold the result gives it a frame the original does not have. That
  is an evaluation-order difference (wall 9).

Five of the last eight rounds have been row-less, and the reason is consistent: what
remains is register allocation, evaluation order, and inlined segment arithmetic. Each of
those is a compiler-internal decision, so the bottleneck is no longer *reading* the
original but *searching* the space of equivalent C. That suggests the next tooling step
should be a shape generator - compile a batch of template variants per unit and let
`match.py` pick - rather than more manual transcription.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 149: the new disassembler pays for itself twice (no rows)
First round using the rewritten `tools/dis.py`, and it immediately produced two clean
readings that hand-decoding had got wrong or half-right:

- **`2603:463c`** (38 B) is `char f(int n) { return g_4642[n & 7] | g_76b4[n / 8]; }` -
  a bit-test getter: the mask table at `0x4642`, the bit array at `0x76b4`, and the
  signed-division idiom `cwd` / `and dx,7` / `add ax,dx` / `sar ax,3` that MSC also emits
  for `n / 8`. Under `/Ox` it is **one byte pair from a row**: the original copies `n`
  into BX *before* the division (`8B DE`) and masks it in place, while MSC uses BX for
  the quotient and reloads `n` afterwards (`8B C6`). Three source shapes were tried -
  operands swapped, an `int bit` variable, a `register int bit` - and all give MSC's
  order, so this is register-copy placement, not expression order.
- **`2a7e:0000`** (67 B, round 144) confirmed: the three-way dispatch with `push si` at
  the top and `si = b` loaded inside the second branch, i.e. the original keeps `b` in SI
  from the first use onward. With `register int b` MSC instead *duplicates the epilogue*
  three times - worse, not better.

The ledger row for `2603:463c` now carries the exact remaining difference instead of the
older summary.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 148: `tools/dis.py` can now actually disassemble (tooling round, no rows)
The annotation tool used to print `?` for anything with a ModRM byte, which is why so
much of this project's analysis was hand-decoded - and hand-decoding has produced at
least three wrong conclusions (rounds 93, 108, 121). It now decodes the 8086 subset this
binary uses properly:

    before                     after
    0003  8B 56                 mov dx, [bp+0x6]
    0005  06                    or dx, dx
    0007  6B 34                 imul ax, [bp+0x34]
    000c  F7 D0                 neg ax

Concretely it now handles: ModRM operands in all four `mod` forms with the byte/word
register tables (`[bp+0x6]`, `[bx+si]`, `[si+0x8870]`, `ah`), the full ALU group with
correct operand direction, `mov`/`lea`/`test`/`xchg`/`segment-register` forms, the shift
group, `imul` with an immediate, `F6`/`F7` (`not`/`neg`/`mul`/`imul`/`div`/`idiv`),
`FE`/`FF` (`inc`/`dec`/`call`/`jmp`/`push`), `les`/`lds`, the string ops, segment
prefixes, and the sixteen real condition names (`jl`, `jge`, ... rather than `j0c`).
Branch and call targets are printed as **absolute VAs** so they can be compared against
`units.csv` directly.

That is the difference between a tool that stops interpreting and one that can be trusted
for a first read - and it directly addresses the failure mode that cost this project the
most time.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 147: mining the reopened `2A E4` class (no rows)
Worked the 74-unit class that round 146 reopened. The classes' units come in four shapes,
and each was pinned:

- **`call` then `2A E4`** - the "promote a char return" idiom. Verified that MSC produces
  exactly it (`int f(int a) { return h(a); }` with `h` returning `unsigned char` gives
  `... 2A E4 C9 CA`), but a scan for that byte pattern in the image finds **0 units**, so
  the original does not use the idiom;
- **byte-table lookups** - `4344:000e` (19 B, struct stride 4) and `43a1:0000` (38 B,
  guarded, stride 4, `-1` default). Both transcribe cleanly and both differ only in
  *order*: the original zeroes AH **before** the load, MSC after it (`C1 E3 02 2A E4 8A
  87` versus `C1 E3 02 8A 87 ... 2A E4`). `43a1` additionally caches the index in BX,
  which is wall 7 on top;
- **`les`-based** (`479e:0004`) - blocked on the split far-pointer load regardless;
- **`43a1`'s `-1` default** was a useful detail: the return type is `int` on one path and a
  zero-extended byte on the other, which is why the compiler bothers to clear AH at all.

So the class is a genuine candidate pool, but its units need the scheduler to emit a
zeroing *before* a load - the same wall 9 that the `3ede` pair hit - and in two of the
four shapes wall 7 as well.

`docs/WALLS.md` now carries the correction as its own section (12b) so the misleading
description cannot be quoted again, and the two decoded units are its witnesses.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 146: `2A E4` is NOT a wall - a class of 74 units reopens (no rows)
The "sub ax,ax zeroing" class (20 units when it was written, 74 after widening the trait
this round to `2A E4` / `2A C0` / `2B C9`) said MSC always emits `33 C0`. **It does not.**
Compiling

    int f(unsigned i) { return (unsigned char)g[i]; }

gives `8A 87 <t> 2A E4` - MSC emits `sub ah,ah` exactly as the original does for a byte
load that has to be zero-extended. The same holds for a byte field of a struct with
alignment greater than one. So **74 units / 15 007 B**, which were filed as permanently
blocked, are candidates; `tools/classify.py` now says so in the class description, and
`BLOCKED.md`'s unclassified pool drops from 140 to **129 units (8 455 B)**.

Two of the class's units were then transcribed: `3ede:000a` and `3ede:0024` (25 B each),

    int f(int a) { return h(a)[1]; }        /* h returns unsigned char __far * */

and they differ from the object in **one instruction pair's order**:

    original   8B D8 8E C2      bx = ax ; es = dx
    MSC 7      8E C2 8B D8      es = dx ; bx = ax

`/Ot`, `/Ox` and `/Oi` all keep MSC's order, so this is wall 9 (scheduling), not a flag
issue.

The lesson is worth as much as a row: a class description is a *hypothesis*, and
"compiler X always emits Y" is the kind of hypothesis that silently parks a whole class
of units. It has now been tested twice this round and was wrong once.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 145: full sweep, and the state of the pool written down (no rows)
Ran `tools/verify.py` without `--fast`: **488/488 rows ok** (MATCH 38, RELOCS 423,
ASM 2, PENDING 25), `checkled.py` consistent. Third full sweep of the project.

Also tried `register` on the dispatched value of `2a7e:0000` (round 144's unit) in case
that put it in SI as the original does; it does not - MSC picks another register under
`/Ox` and emits nothing extra under `/Os`.

The shape of the remaining work, stated plainly:

- **488 ledger rows, 10 869 B of own code verified (3.707 %)**. Every row is rebuilt from
  source and byte-compared on demand, and all of them pass;
- the 144-unit unclassified pool has three clean units below 100 bytes and nothing above;
- **every unit transcribed in rounds 137-145 differed only in register allocation**, and
  that family does not respond to `/G0`, `/G1`, `/Os`, `/Ox`, `/Od`, or MSC 6.0;
- the only lever that produced rows in that stretch is `/Ox`'s effect on register
  *reuse* (`50ff:000e`, `218f:0004`/`2191:0008`, `1f45:00b0`), which has now been applied
  to every unit where it plausibly applies.

So the C coverage is at the limit of what this compiler can express for this binary. The
remaining routes are a toolchain this machine cannot obtain (a pre-6.0 Microsoft C), a
linker-level explanation for the one-byte padding (three witnesses, no mechanism), or
ASM-assisted rows that document the functions without claiming C coverage.

Ledger 488 rows; verify (full) and checkled green; own-code coverage 10 869 B (3.707 %).

## Round 144: a three-way dispatch transcribed, blocked on the register save (no rows)
`2a7e:0000` (67 B) - one of the larger units in the CX-scratch cluster - decodes cleanly
to a three-way dispatch:

    void f(int a, int b, int c, int d)
    {
        if (d < 0)      h1(a, b, c);
        else if (d > 0) h2(a, b, c);
        else            h3(a, b, c);
    }

with four far-Pascal parameters (retf 8) and three different far callees. The original
keeps `b` in **SI** across the whole body (`push si` immediately after the frame, `pop si`
before leaving); MSC keeps it in the frame under `/Os` and reaches for other registers
under `/Ox`, so the transcription is 65 or 67 bytes but `+0x3` never matches.

That is wall 7 again, and the seventh unit in a row whose only remaining difference is
which register the compiler chose. The pattern across rounds 137-144 is now explicit:
**every unit I can still transcribe differs only in register allocation**, and the
register-allocation family (walls 6, 7, 13a) does not respond to `/G0`, `/G1`, `/Os`,
`/Ox` or MSC 6.0.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 143: the CX-scratch cluster mapped (no rows)
Screened for units that load a parameter into CX (`8B 4E xx`), i.e. the cluster where the
original uses CX as its scratch register for a test: **10 units, 36-130 bytes**.

Two were transcribed (`1f72:0044` and `1f7c:0008`, 40 B each, sharing a shape and
differing only in which long global they decrement):

    if ((a | b) != 0) { h(b, a); g_46ec--; }
    return 0;

The source form matters here and is now recorded: `if (a || b)` makes MSC emit a compare
chain, while `if ((a | b) != 0)` produces the single `or` that the original has. With the
right form the code is otherwise identical - and still differs in where the parameter
goes: the original loads `a` into **CX** (`8B 4E 06`) and `b` into AX, MSC loads `a` into
AX and ORs against memory (`/Os`) or keeps both in SI/DI (`/Ox`).

So this cluster is wall 13a, documented with its examples: the only unit of this shape
MSC reproduces is `1f45:00b0`, whose function is large enough that the allocator reaches
for CX by itself.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 142: MSC 6.0 available, and it does not help (no rows)
Round 141 concluded that the DOS 6.00A compiler sits on DISK8 behind KWAJ compression,
and that unpacking it was the next step. Before writing a KWAJ decoder, one check was
worth making: is MSC 6.0 already available elsewhere. It is - **`toolchain/msc6c` compiles
fine** (`--msc-dir MSC6C --no-dpmi`), and that is what the round-55 profile work used.
`msc6dos` was simply one of the non-DOS distributions and can be ignored.

So the experiment ran immediately, on the units whose only difference is a scratch
register:

| unit | MSC 7 /G0 /Os | MSC 6.0 /G0 /Os | MSC 7 /G0 /Ox | MSC 6.0 /G0 /Ox |
|---|---|---|---|---|
| `2a28:0000` | AX | AX | AX | AX |
| `2a29:000c` | AX | AX | AX | AX |

The original wants **DX**. Both compilers give AX under both optimizers, so MSC 6.0 is
not the generation that built this binary either - which matches round 55's conclusion
that it predates MSC 6.0.

That closes the "try another compiler" avenue for the walls that matter: MSC 5.1 is the
only older Microsoft C here and it cannot be made to run (round 92), and DISK8 contains
no 5.x toolchain to justify a KWAJ decoder after all.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 141: the MSC 6.0 driver works - the compiler passes are the wrong platform (no rows)
Round 140 installed the DOS driver and it still did nothing. This round found out why,
and the answer overturns two earlier conclusions:

- **the driver is not silent.** `CL.EXE > file` with no arguments writes
  `usage: cl [ option... ] filename... [ -link linkoption... ]` into the file. Compiler
  messages *are* redirectable, which means rounds 70-71's "cannot be observed" was never
  about the console;
- **a real compile fails one level down.** `CL` echoes the source name and then writes
  `This program cannot be run in DOS mode.` - that is `C1.EXE` refusing to run. Every
  `C1.EXE`/`C2.EXE` pair on DISK1, DISK2 and DISK6 is the same Windows/OS-2 pair
  (148 060 / 354 338 bytes), so the `msc6_disks` set simply does not contain a DOS
  compiler.

Where it does live: `DISK8.IMG` has `C1L.EX$`, `C2L.EX$`, `C3L.EX$`, `CL.EX$`,
`SETUP.BAT` and `SETUP.CMD` - the DOS-shaped set. Its `CL.EX$` unpacks to a stream
starting `KW`: Microsoft **KWAJ** compression, which `tools/extract_disks.py` does not
implement (it handles SZDD only).

So the next step is a bounded tooling task: add a KWAJ decoder, unpack DISK8's compiler,
and the DOS 6.00A toolchain finally runs. That toolchain is the one most likely to
explain walls 3 (immediate encoding), 4 (register assignment), 6 (register reuse),
7 (scratch naming) and 9 (scheduling) - all five are "how the older compiler allocated
and ordered things".

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 140: the installed MSC 6.0 was the OS/2 build - found the DOS one (no rows)
Went back to the compiler question with one specific doubt: whether the `msc6dos` set is
really the DOS distribution. It is **not**. `DISK6.IMG`, which round 68 extracted from,
also carries `OS2.LI$`, `CDLLOBJS.*` and `LLIBCDLL.LI$` - it is the **OS/2** disk, and its
28 858-byte `CL.EXE` is an OS/2 binary. That is why it always ran and did nothing.

`DISK2.IMG` is the DOS compiler disk, and every pass differs in size and md5:

| file | DISK6 (was installed) | DISK2 (DOS) |
|---|---|---|
| `CL.EXE` | 28 858 | **29 859** |
| `C1.EXE` | 148 060 | **146 928** |
| `C2.EXE` | 354 338 | **345 721** |
| `C3.EXE` | - | **152 683** |

The DISK2 set is now installed in `toolchain/msc6dos/BIN` (the OS/2 driver kept as
`CL.EXE.os2`). It still produces no object, and this time the diagnosis is tight: `CL`
returns control - a `; echo` marker after it is created - with no object, no stdout, no
stderr, from both the C: root and its own directory, with `TMP` set, and with EMS/XMS
enabled in the DOSBox configuration (that change is harmless; MSC 7 was re-verified
afterwards).

So the DOS 6.00A driver is finally in place and remains silent. Two explanations are
left: a `SETUP`-written configuration (the `msc51` distribution carries `NEW-CONF.SYS`
and `NEW-VARS.BAT` for exactly that purpose), or console output via INT 10h that the
dummy video driver hides. Both are recorded in `docs/GAP.md`.

This is the most useful kind of row-less round: it removes a wrong assumption
("msc6dos is the DOS compiler") that had blocked the whole alternative-compiler thread
since round 68.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 139: `/Ox` does not help the scratch-naming wall (no rows)
Two PENDING rows re-tested under `/Ox` and `/Ox /Oi`, both previously blocked on a
scratch register:

- `1e38:0002` (56 B, RECORD_CFG) - wanted `8B 16 <g>` (the saved global in DX);
  `/Ox` gives `push si` instead;
- `4e11:007e` (40 B, WEIGHT2) - wanted `8B 56`; `/Ox` gives `push si` too.

So `/Ox` swaps one wrong register for another in this family. The two places it *does*
help are now precisely known: register reuse across a push (`50ff:000e`) and the
CX cache in a large function (`1f45:00b0`). `docs/WALLS.md` records that boundary.

Also tried this round: widening the far-pointer-to-parameter screen from `16 50..52` to
any `16 50..57` - it returns **zero** further units, so `3cd1:02f2` (round 138) was the
only one of that shape in the pool.

Three rounds without a row now (137-139). The remaining candidates have all been tried in
at least two flag configurations; the honest position is that this toolchain has been
taken as far as it goes on them.

Ledger 488 rows (unchanged), PENDING 25; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 138: a range check down to the padding byte exactly (no rows, PENDING record)
Screened for units that pass far pointers to their own parameters - the shape that
round 132/133's `int __far *` casts unlocked - and found one: `3cd1:02f2` (56 B).

Transcribing it took three attempts and each narrowed the diff:

1. `h(...); if (a < 0 || a >= g_193c) return 0; ...` - MSC merged the four checks and the
   jump layout was 8 bytes off;
2. with `h` as `__near` instead of `__far` the first diff disappeared (the call encoding
   was the only issue there);
3. rewriting as **one** condition - `if (a >= 0 && a < g_193c && b >= 0 && b < g_193e)
   return 1; return 0;` - reproduced the layout exactly.

What remains is **two branch distances**, `1C`/`1B` and `14`/`13`, i.e. exactly the
`90` padding byte in the original's `B8 01 00 EB 03 90 33 C0` (ours is
`B8 01 00 EB 02 33 C0`). That makes this the **cleanest witness yet** for the
late-peephole form of wall 2: the compiler laid out a 3-byte `mov ax,0`, shortened it to
`33 C0` afterwards, and padded the freed byte instead of re-laying out the jump - and the
jump distance is correct for the padded layout, which is why every path to the epilogue
depends on that one byte.

Recorded as a PENDING row; it is the unit to re-run first if the padding is ever
explained.

Ledger 488 rows - MATCH 38, RELOCS 423, ASM 2, **PENDING 25**; verify and checkled
green; own-code coverage 10 869 B (3.707 %).

## Round 137: the CX cache survives `/Ox` in short functions (no rows)
Round 135 showed `/Ox` makes MSC cache a selector in CX - but only in a *large*
function. Two short units tried this round show the limit:

- `1e1e:002a` (27 B) - `if (x > 0xFF) return h(x); return x;`. Under `/Os` MSC compares
  the frame slot twice; under `/Ox` it keeps the value in **SI** (`push si` in the
  prologue), not CX. Two source shapes were tried (early-return and `if/else` with a
  register result) and both give the SI form.
- `2ad6:000a` (34 B) - `if (!a && !b) return 0; return h(b, a);` returning a `long`.
  Same result: `/Os` compares memory, `/Ox` uses SI, the original uses **CX**
  (`8B 4E 06` / `0B C1`).

So the "CX-staged value" class splits in two: in `1f45:00b0` (59 B, a long-taking
selector routine) `/Ox` produces the CX form and the unit matches; in functions of
30 bytes or less MSC reaches for SI instead. The difference looks like register
pressure, not a flag, so short CX-staged units stay blocked.

Ledger 487 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 136: the `/Ox` win applied to the next CX-staged unit (no rows)
Followed round 135 by transcribing `1e1e:002a` (27 B), the other CX-staged unit I had a
candidate source for. Under `/Ox` it is now **two differences** from a row, and they are
not register naming but *structure*:

    original   cmp cx,0xFF ; ja skip ; mov ax,cx ; jmp end ; mov ax,cx ; call h ; ...
    MSC 7      cmp x,0xFF  ; ja skip ; mov ax,x  ; jmp end ; ... call h ...

i.e. the original returns the parameter on one path and calls `h` on the other
(`if (x > 0xFF) return h(x); return x;` compiled as an if/else with a shared tail),
while MSC keeps the early-return shape and reaches the common epilogue by falling
through. So `/Ox` resolved the register question but the unit needs the other C shape -
`if (x <= 0xFF) r = x; else r = h(x); return r;` - which is what the next round should
try.

Also recorded: the "CX-staged value" classifier trait is **too loose** - it matches far
more than the 9 units the class reports, including multi-kilobyte data blobs, because
`classify.py` assigns each unit to the first matching trait. Tightening it is a tooling
task for a later round; the class ordering already keeps `BLOCKED.md`'s numbers sane,
but the raw trait should not be used as a work list without a size bound.

Ledger 487 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 869 B (3.707 %).

## Round 135: `/Ox` also resolves the CX-staged wall (59 B)
Round 134 bounded `/Ox` to "use it when only the register name differs". This round
found a second family where it applies: the units classified as **CX-staged value**,
where the original caches a parameter in CX for two comparisons.

`1f45:00b0` (59 B) now matches under `/G1 /AM /Gs /Ox`:

    if (sel == 0x19 || sel == 0x14) {
        g_4688 = sel;
        h(sel == 0x19 ? 0x6C : 0x68, g_46e1, v);
    }
    return v;

with parameters `(long v, int sel)`. Two things had to be right:

- the selector is the **last** parameter, at `[bp+06]`, which is why the original's first
  instruction reads it; my earlier attempt had `(int sel, long v)` and every offset was
  wrong;
- `/Ox` is what makes MSC cache it in CX (`8B 4E 06` / `81 F9 19 00`); under `/Os` it
  compares the frame slot twice (`83 7E 06`).

So the "CX-staged value" class (9 units / 690 B) is a `/Ox` candidate, not a wall - which
reclassifies it from the permanently-blocked list to the work list.

Ledger 487 rows - MATCH 38, RELOCS 423, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 869 B (3.707 %)**.

## Round 134: the `/Ox` lever tested against seven blocked units (no rows)
Round 133 found `/Ox` resolves some register-naming misses, so this round applied it to
the units that had been blocked on exactly that:

| unit | under `/Os` | under `/Ox` |
|---|---|---|
| `37ef:000c` | index in BX, compare in memory | same, plus `push si` - still differs |
| `3874:000a` | register pair swapped | still swapped |
| `4ab2:000c` | register reused differently | still differs |
| `3ae7:0000` | register pair | produces a shorter symbol - further away |
| `1486:0002` | frame 4 versus 6 | frame now 6 ✓, but MSC keeps `a` in SI |
| `322c:002c` | pushes SI where the original pushes AX | **reverses** the assignment instead |
| `13db:000c` | pushes memory where the original loads first | hoists a register save |

So `/Ox` is **not a blanket fix**: it aligns the allocator on some units (`218f:0004`,
`50ff:000e`) and actively diverges on others. The useful distinction, now recorded in
`docs/CONVENTIONS.md`, is *which side is optimising more*: when the original and MSC
nominally agree and only the register name differs, `/Ox` can align them; when the
original is doing **less** optimisation than MSC (no value kept across statements, no
register for a dead temporary), `/Os` is right and `/Ox` makes it worse.

One partial win worth noting: `1486:0002`'s frame size was fixed by making the call
result `volatile` (6 bytes, matching the original), which confirms the original keeps
that value in memory rather than in a register - but MSC then keeps a *parameter* in SI
that the original reloads, so the unit is still a wall-5 case.

Ledger 486 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 810 B (3.687 %).

## Round 133: `/Ox` is a lever - three rows, 210 B (largest single round since round 96)
Round 132 left `50ff:000e` two bytes from a row, differing only in which register MSC
used for a `lea`. Trying the other optimiser settings on that unit produced the answer
and then a second, larger finding:

- **`50ff:000e` (138 B)** - the largest row in the project. `/Ox` makes MSC reuse AX for
  the second pointer of `h2`'s argument list, exactly as the original does; `/Os` takes
  a fresh CX. Together with the `int __far *` cast on the parameter addresses (which is
  what produces `lea`/`push ss`) and the `h4(b, c) == 1` guard, the whole 138 bytes match.
- **`218f:0004` (36 B)** and its byte-identical sibling **`2191:0008`** - the pair that
  round 116 used as the fourth counter-example to every register-assignment rule. Under
  `/Ox` the allocation matches; under `/Os` it is swapped.

So the "register assignment" wall - four contradictory data points, recorded as
un-explained - is at least partly a **flag artefact**. `docs/CONVENTIONS.md` now says to
compile a register-only difference under `/Ox` before concluding anything about the
allocator, and `docs/WALLS.md`'s walls 6 and 7 should be re-examined the same way in
the next rounds.

Ledger 486 rows - MATCH 38, RELOCS 422, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 810 B (3.687 %)**.

## Round 132: the 138-byte state machine is 136 bytes right (no rows, PENDING record)
Round 131 left `50ff:000e` decoded but with an unresolved question about the `h5` call
sites. The answer turned out to be simple: the three `h5` calls pass their arguments in
the order written, so one declaration covers all three, and the two `h5` calls that look
shared are a jump-merge where the differing argument is pushed before the jump.

Two more things had to be right, and both were:

- the **parameter addresses are cast to `int __far *`** - that cast is the only thing that
  makes MSC emit `lea ax,[bp+0A]` / `push ss` / `push ax` instead of a near `push ax`;
- the guard is `h4(b, c) == 1` (`48 75 1D` = `dec ax` / `jnz`), and the two branches
  differ only in the third argument of their `h5` call and of the merged second `h5`.

Result: **136 of 138 bytes match**. The remaining two are `8D 46 06` versus `8D 4E 06`
(and its `push`): for the second pointer of `h2`'s argument list, the original **reuses
AX** - the value has already been pushed, and `push ss` does not clobber AX - while MSC
takes a fresh CX. That is register reuse across a push, the same family as wall 6.

Recorded as a PENDING row rather than a near-miss note, because the C is now exact and
only two bytes of register naming stand between it and a 138-byte ledger entry.

Ledger 484 rows - MATCH 38, RELOCS 419, ASM 2, **PENDING 25**; verify and checkled
green; own-code coverage 10 600 B (3.615 %).

## Round 131: the last large candidate decoded to block level (no rows)
`50ff:000e` (138 B) - the only remaining no-wall unit above 100 bytes - is now decoded
to the block level. It is a three-parameter far-Pascal state machine (params at 0A, 08,
06) with six calls:

- `h1(&a, &b)`, `h2(&b, &c)`, `h3(&a, &b)` - each passing **far pointers to its own
  parameters** (`8D 4E 0A` / `16 51` = `lea cx,[bp+0A]` / `push ss` / `push cx`);
- `h4(b, c)`, whose result selects one of two branches (`48 75 1D` = `dec ax` / `jnz`);
- in each branch `h5(...)` returns a value compared against `0x20` (two different
  argument lists), and then a third `h5` call and a final `h6()`.

What is *not* pinned yet is the exact C: the two `h5` call sites push their arguments in
orders that do not agree with a single three-argument declaration (one is `b, c, 0`, the
other `0, a, 1`), so either the callee has a variable-argument shape or two different
functions share the address `0x0948` at different call sites. That is worth one more
round, but not a guess.

With this, every unit above 100 bytes in the no-wall pool has been decoded; the only
unknowns left in that pool are three small ones.

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 130: full verification sweep and the long variant of wall 5 (no rows)
Ran `tools/verify.py` without `--fast`: **483/483 rows ok** - MATCH 38, RELOCS 419,
PENDING 24 - and `checkled.py` consistent. That is the second full sweep of the project
(the first was round 107 at 476 rows), so every row added since then has now been
rebuilt from source and re-matched against the image in one pass.

Also folded round 129's finding into `docs/WALLS.md`: wall 5 (assignment persistence)
has a `long` variant in which the original keeps **halves** of two longs in registers
across calls while MSC allocates both as whole frame slots. A partial spill of a long
has no MSC equivalent at all, which makes `1c97:000c` the strongest witness for that
wall rather than an outlier.

No new rows. One more large candidate remains undecoded (`50ff:000e`, 138 B, six
parameters with address-of-argument passing); it is the last one above 100 bytes.

Ledger 483 rows - MATCH 38, RELOCS 419, ASM 2, PENDING 24; verify (full) and checkled
green; own-code coverage 10 600 B (3.615 %).

## Round 129: the largest remaining candidate decoded (no rows)
`1c97:000c` (110 B) - the biggest no-wall unit in the pool - is now fully decoded:

    long __near __pascal f(long a, long b, long c)      /* ret 0x0C, three longs */
    {
        long r;
        r = h1(c);
        if (!r) return 0;
        if (h2(r + 0x600, a + 0x600, b)) h3(a);
        else h4(r);
        return 0;
    }

The three `+0x600` additions are the `05 06 00` / `83 D2 00` (add + adc) pairs, and the
parameter mapping was pinned by their offsets: `a` at 0C/0E, `b` at 08/0A, `c` at 04/06.

The transcription produces the same operations but only 57 bytes, because the original
keeps **halves of two longs in registers** across the calls: `r`'s low word lives in SI
(`8B F0` after `h1`) and `a`'s low word in DI (`8B 7E 0C`), with only `r`'s high word
spilled to `[bp-2]`. MSC allocates both longs as frame slots (`89 46 FC` / `89 56 FE`)
and merges the two `return 0` paths into one epilogue.

So this is the assignment-persistence wall applied to `long`, with a partial spill that
MSC has no equivalent for. Worth having decoded: it removes the largest item from the
"unclassified" list as a known quantity rather than an unknown one.

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 128: a documentation index, and the mid-size pool measured (no rows)
Screened the pool above the sizes previous rounds covered (100-220 bytes): only **two**
no-wall units exist there, `1c97:000c` (110 B) and `50ff:000e` (138 B), and both are long
arithmetic / address-of-parameter routines with `+0x600` carry chains and six parameters.
They are transcribable but not in a single sitting, so this round recorded the state
instead:

- added **`docs/README.md`** - an index of the seven documents, the command list for
  building/matching/verifying, the screening tools and what each is for, and a
  five-point "reading a new candidate" checklist built from the mistakes of the last
  twenty rounds (run `dis.py` first; check the walls; distrust the inventory size; a
  bare `55 8B EC 56` prologue means no locals; `/G0` for locals, `/G1` for 80186
  encodings).

The pool is now visibly finite: 144 unclassified units, of which the clean ones number
three below 100 bytes plus these two above it. Everything else carries a named wall.

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 127: a table-mask routine decoded, blocked on register choice (no rows)
With wall 14 classified, the "no known wall" screen dropped from 38 to 36 units; one
untried unit was decoded in full and transcribed:

`37ef:000c` (29 B) is `if (b != -1) g_6e36[b].f0 &= ~a;` with a 0x34-byte struct. The
decode is clean - `83 FB FF` guards, `F7 D0` complements, `6B F3 34` scales, `21 84 36 6E`
masks the word at `[si+0x6E36]` - and the transcription produced the same *operations*
in 24 bytes. Two differences, both register choice:

    original   8B 5E 08 (BX = b)  83 FB FF (compare BX)  6B F3 34 (SI = b*0x34)  and [si+disp]
    MSC 7      83 7E 06 FF (compare frame)            6B 5E 06 34 (BX = b*0x34) and [bx+disp]

So the original loads the index into BX and scales into SI, while MSC compares the frame
slot and scales into BX. That is walls 7 (scratch naming) and 11's cousin (which register
the address arithmetic lands in) at once.

Three more units from the same screen remain untried or blocked on named walls:
`4e9b:0008` (long staging through BX), `1cc3:000c` and `1cba:000a` (AH-argument
interrupt wrappers), `10b7:0006` (global address kept in SI).

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 126: wall 14 is now a classifier trait (no new rows)
Round 125 identified "frames where MSC omits them" as a wall but left it detectable only
by hand. This round added it to `tools/classify.py` as **frame without frame use**: a
unit that opens `55 8B EC`, ends at a return and whose body contains no `[bp+nn]`
reference (detected as a common opcode followed by a ModRM byte with `rm = 110` and
`mod = 01`/`10`).

The effect on the accounting:

| | before | after |
|---|---|---|
| classes | 19 | **20** |
| unclassified | 160 units / 9 511 B | **144 units / 9 511 B** |
| frame without frame use | - | **36 units / 1 583 B** |

The unclassified pool is now 144 units, and the count has been falling for the right
reason each time: 160 was the count after the return-predicate fix, and every round
since has either matched a unit or moved a group into a named class.

`docs/BLOCKED.md` regenerated; `verify.py` and `checkled.py` still green.

Ledger 483 rows (unchanged), PENDING 24; own-code coverage 10 600 B (3.615 %).

## Round 125: a fourteenth wall - frames where no frame is needed (no rows)
Screened the smallest clean units (8-40 bytes, 23 candidates) and found a class that had
been hiding as "frame mismatch":

**The original emits `55 8B EC` on every function**, including ones with no parameters
and no locals. MSC omits the frame entirely when nothing needs it:

    original   55 8B EC 90 0E E8 <h1> A0 <g> 0A C0 74 05 90 0E E8 <h2> 5D CB
    MSC 7      9A <h1> 80 3E <g> 00 74 05 9A <h2> CB

(`1270:000e`, 22 B - `h1(); if (g_4abf) h2();`). Neither `/G0` nor `/Gd` makes MSC
emit the frame, and the same thing is visible on the 9-byte units `141f:0000`,
`1420:000f` and `1466:0052` (`55 8B EC 8B E5 5D CA 0A 00` for an empty function).

The class is **detectable without disassembly**: an unmatched unit whose body contains
no `[bp+xx]` or `[bp-xx]` reference but which still opens `55 8B EC` and closes
`5D CB`/`C9`. That makes it a good candidate for a `classify.py` trait in a later round.

Also examined: `2141:00a6` (20 B) - `if (v > 0) v = -v; g_0f80 = v;` - blocked on the
DX scratch-register choice again.

`docs/WALLS.md` now lists this as wall 14.

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 124: the reading rules written down (no new rows)
One more pool unit examined (`25f0:0092`, 39 B) - a subtraction loop that keeps its
counter in **BX** and its accumulator in DX, i.e. walls 7 and 8 together, with no frame
at all. Not transcribable, but it confirmed the pattern.

So this round recorded the two *reading* lessons that the last three rounds taught, in
`docs/CONVENTIONS.md`:

- **"No frame means no locals."** Two units were first transcribed with a temporary for
  a call result; that makes MSC allocate a frame and adds `83 EC nn`. The original
  consumes the value inside the expression (`if (h3(x) == 9)` rather than `r = h3(x);
  if (r == 9)`). On a unit whose frame is just `55 8B EC` plus a register save, assume
  zero locals and restructure until nothing needs storing;
- the same holds for a modified parameter (`a -= 0x119; while (a > 0) ...`), which the
  original keeps in a scratch register instead of writing back.

And `docs/WALLS.md`'s scratch-register entry now names the signed/unsigned clamp pair
(`2a28:0000` / `2a29:000c`) as **the best single test case in the project**: three
otherwise-perfect units that differ only in which register holds the working value, and
two of them resolve together the moment that choice is explained.

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 123: three more units, all on the DX-versus-AX scratch choice (no rows)
Widened round 122's no-wall screen to include call-free units (38 candidates) and
transcribed three:

- `3e48:000a` (24 B) - `if (a < 1) a = 0x0F; g_1bbc = a; return a;`. The original loads
  `a` into **DX** (`8B 56 06`) and compares the register; MSC compares the frame slot.
- `2a28:0000` (28 B, signed) and `2a29:000c` (28 B, unsigned) - a clamp pair:
  `if (b <= a) { if (c < a) a = c; } return a;`, differing only in `7F`/`7D` versus
  `77`/`73`. Again the original keeps the value in DX (`8B 56 0A`) where MSC uses AX.

So all three reduce to the same two bytes of register naming. Both also taught a
reading lesson: the first transcription of the clamp pair used the wrong parameter
roles (the function modifies `a` and compares against `b` and `c`, not the other way
round), and the first transcription of `3e48` invented a local for the value, which
forced a frame the original does not have - the same mistake as round 122's `F_438C`,
which suggests the rule "no frame means no locals, rewrite the expression" is worth
applying before anything else on a `55 8B EC 56`-style unit.

The clamp pair is a ready-made test case: two 28-byte units that differ only in their
comparison opcodes, so if the scratch-register choice is ever explained they both
resolve at once.

Ledger 483 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 600 B (3.615 %).

## Round 122: two frame-less shapes (65 B)
A screen for units free of *every* known wall (no `les`/segment moves, no interrupts, no
padded jump, no two-register prologue) returned 23 candidates; two matched:

- `crelay76.c` `F_37EC`: `37ec:0006` (31 B) - `if (a == -1) return a; h1(a); return
  h2(a);` with the parameter `register` and the calls far then near.
- `crelay76.c` `F_438C`: `438c:0004` (34 B) - `if (h3(x) == 9) return x - g_2fce;
  return -1;`. The first transcription declared a local for the call result and MSC
  built a frame; the original is `55 8B EC 56` then straight into the body, because the
  result is compared in AX and never stored. **Declaring a variable is what broke it** -
  removing the local and comparing the call directly matched.

That second one is a reusable lesson: when the original's prologue is only
`55 8B EC 56`, the source must have no locals at all, which usually means the call
result is consumed inside the same expression rather than assigned first.

Ledger 483 rows - MATCH 38, RELOCS 419, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 600 B (3.615 %)**.

## Round 121: the padding has two causes, and I can name both (no rows)
Tested round 120's hypothesis on the unit that motivated it. `4998:000c` (112 B) has a
**single shared epilogue**, so "the compiler does not merge return paths" does not
explain its pad. What it does show is:

    0x64  B8 01 00     mov ax,1
    0x67  EB 03        jmp 0x6c
    0x69  90           nop
    0x6a  33 C0        xor ax,ax     <- 2 bytes where a 3-byte `mov ax,0` fits
    0x6c  C9 CA 08 00  leave / retf 8

with `48eb:000c` identical. That reads as a **late peephole**: the compiler laid out a
3-byte `mov ax,0`, shortened it to `xor ax,ax` afterwards, and padded the freed byte
rather than re-laying out the jump - which is why the jump distance is correct for the
*padded* layout.

So wall 2 has at least two causes: non-merged epilogues (`13d5:000c`) and late
instruction shortening (`4998:000c`, `48eb:000c`). `1036:000c`'s pad (after a jump,
before a `push`) fits neither exactly, so the family is not fully explained - and that
is now what `docs/WALLS.md` says, rather than implying a single rule.

The practical consequence is unchanged: neither cause is reachable from MSC 7, which
lays out after peepholing and merges paths under `/Os`.

Ledger 481 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 535 B (3.593 %).

## Round 120: the nop padding is a non-merged epilogue, not a padding rule (no rows)
Tested whether MSC can be made to emit the `90` at all, and it can - just not the way I
had been thinking. Compiling

    int f(int a) { if (a) { h(a); return 1; } return 0; }

gives, under `/Ot` or `/Ox`:

    ... B8 01 00 C9 CA 02 00 90 33 C0 C9 CA 02 00

i.e. MSC keeps **two separate epilogues** and pads between them. That is the same shape
as the original's padded units (`13d5:000c`'s pad after `CB`, `48eb:000c`'s pad after
`EB`). Under `/Os` MSC merges the paths and the pad disappears.

So wall 2 is really "**the older compiler does not merge return paths**", with the
padding as a side effect - a more useful statement, because it predicts that padded
units also contain repeated epilogues and it makes `/Ox`/`/Ot` a lever rather than a
dead end.

Applied to `48eb:000c` (30 B, `return h(a, b, c) == 1;`): under `/Os` it is **two
differences** from a row (the pad and the branch distance it implies), under `/Ox` the
whole epilogue shape changes instead. So the lever reproduces the padding but not the
surrounding code for this unit - worth retrying on units where the epilogues are already
duplicated.

`docs/WALLS.md` now carries this refinement.

Ledger 481 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 535 B (3.593 %).

## Round 119: the walls consolidated into one document (no new rows)
Two row-less rounds in a row, both ending in "the instruction order is the only gap", so
this round wrote the analysis down instead of repeating it: **`docs/WALLS.md`** now
collects every blocker as a numbered wall, each with a verified example unit and, where
known, the byte pattern that identifies it:

1. frame/instruction coupling (`ENTER` vs classic, only half-solved by `/G0`);
2. **nop padding** after short jumps and block ends - the largest remaining family;
3. immediate pushes (`6A`/`68` selection);
4. register-parameter assignment (four contradictory data points);
5. assignment persistence (values kept in a register across statements);
6. register reuse;
7. scratch-register naming (AX vs CX/DX);
8. BX as a register variable;
9. scheduling (hoisted constants, interleaved load/store);
10. argument evaluation order;
11. split far-pointer loads and the inlined `MK_FP`;
12. byte-argument promotion and byte selection;
13. three peephole differences (CX caching, constant folding, `or reg,ax`).

The document ends with what would unblock the most: the padding rule first, because it
blocks whole families and is the reason several otherwise-perfect transcriptions miss by
exactly one byte; and a working pre-MSC6 compiler second, because walls 1, 3, 4, 6, 7, 8
and 9 are all "how the older compiler allocated and ordered things" and one such build
would settle several at once.

That is the useful form for this stage: a reader - or a future session with a different
compiler - can now see the whole blocker set in one page instead of reconstructing it
from a hundred round entries.

Ledger 481 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 535 B (3.593 %).

## Round 118: both sweeps empty, one more unit down to scheduling (no rows)
Ran `tools/reuse.py` and `tools/probe.py` again now that twelve sources have been added
since the last sweep: **both report zero**. The sibling and pattern seams are exhausted
for the current source set.

One more pool unit was transcribed: `3b2b:000c` (66 B) -
`g_1760 = a; g_1762 = b; if (!h1(b, a)) { if (!h2(b, a)) { g = 0; g = 0; return -1; }
return h3(b, a); } return 0;` with `a` in SI (so the parameter list is `(int b, register
int a)`). The whole body matches - all three calls, both guards, the zeroing pair and
both return paths - except two instructions at the top:

    original   8B 76 06 8B 46 08 89 36 <g1> A3 <g2>     (load both, then store both)
    MSC 7      8B 76 06 89 36 <g1> 8B 46 08 A3 <g2>     (load, store, load, store)

MSC interleaves the second load with the first store; the original loads both
parameters before storing either. That is the same scheduling family as round 117's
hoisted constants, and no source order fixes it because the store order is already
correct.

So the pool's remaining units are now dominated by scheduling differences: the C is
known, the encoding is known, and the instruction *order* is the only gap.

Ledger 481 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 535 B (3.593 %).

## Round 117: a scheduling wall named - constant pushes hoisted across a call (no rows)
With the clean relay subset drained, two longer units were transcribed:

- `1f45:00b0` (59 B) - a length selector that caches its argument in **CX** and compares
  it twice (`8B 4E 06` / `83 F9 19` / `83 F9 14`). MSC compares the frame slot twice and
  never uses CX for a parameter, so this is the CX-caching habit already seen on
  `1e1e:002a`.
- `3e34:000a` (58 B) - `h1(8); s = h2(0x0F, 0x4000); h3(1, 0, a, b, s); h4(s); g = 0;`.
  Two things came out of it. The first call is `__fastcall` (the value arrives in AX
  with no push, `B8 08 00`), and the immediate is **8**, not the `0x800` I first read -
  a byte-order slip in my own decode that `dis.py` would have prevented. The remaining
  difference is new:

      original   call 6A 0F 68 00 40 call 8B F0 50 ... 6A 00 6A 01 call
      MSC 7      call 6A 01 6A 00 FF 76 08 FF 76 06 6A 0F 68 00 40 call ...

  MSC pushes `h3`'s **constant** arguments before calling `h2`, because they do not
  depend on its result; the original keeps strict statement order. That is a scheduling
  wall, now recorded in `docs/CONVENTIONS.md`, and it explains a class of "the calls are
  right but the bytes are interleaved" misses.

Ledger 481 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 535 B (3.593 %).

## Round 116: a fourth data point on register assignment, and the clean pool drains (no rows)
`218f:0004` and `2191:0008` (36 B each, differing only in call targets) decode cleanly as
`h1(-1); h3(h2(a, b), a, b);` with both parameters in registers - and they miss **only**
in the two prologue loads:

    original   8B 7E 08 (DI = a)   8B 76 06 (SI = b)
    MSC 7      8B 76 08 (SI = a)   8B 7E 06 (DI = b)

That is the fourth unit in the register-assignment series and it breaks every rule
proposed so far, so `docs/CONVENTIONS.md` now carries a four-row table instead of a
claim: declaration order fails on `3ede` and `4e58`, first-use fails on `3874`, and
"lowest offset wins" fails on `3874` and `218f`. The practical rule recorded is to treat
any unit with two register parameters as test-me-not-predict.

Also worth recording: the "clean relay" subset of the 160-unit pool is now nearly
drained - five units of 41-52 bytes and thirteen of 18-41, with overlap, and every one
of them has either been transcribed or is blocked on one of the named traits. What
remains in the pool is longer, messier code, not more of the same shape.

Ledger 481 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 535 B (3.593 %).

## Round 115: a long-parameter guard (59 B)
`crelay75.c` (`/G1 /AM /Gs /Os`): `1e88:000e` (59 B) - `if (!v) { h0(); return; }
if (h1(v)) { h2(v, c); g_40b4--; }` with `long v`.

The unit matched on the first attempt once the shapes were read correctly:

- the zero test is the word-OR of the long's halves (`8B 46 0A` / `0B 46 08`), so `v`
  is a `long`, not two ints;
- the global decrement is a **word pair** (`83 2E <g> 01` / `83 1E <g+2> 00`), i.e. a
  `long` global decremented in place - a plain `int` would give a single `83 2E`;
- the no-argument call is `__near` while the two long-taking calls are `__far`, which
  the image shows as `E8` versus `90 0E E8`.

That is the fourth row from the pool round 110's fix uncovered, and the third from a
unit that only became visible because its final `retf 6` was no longer mis-read as "not
a return".

Ledger 481 rows - MATCH 38, RELOCS 417, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 535 B (3.593 %)**.

## Round 114: a long-result guard, and `MK_FP` as the wrong tool (43 B)
`crelay74.c` (`/G1 /AM /Gs /Os`): `1fc8:0048` (43 B) -
`if (h(a, 0x760E, 0x0871) == -1L) h2(0x48, g_0128);`.

Two things had to be right:

- the far-pointer constant is passed as **two plain int arguments**, not through
  `MK_FP`. With `MK_FP(0x0871, 0x760E)` the pushes come out the wrong way round *and*
  the callee gets an extra call to a helper - the unit grew to 49 bytes. As
  `h(a, 0x760E, 0x0871)` the two `push imm16` land in the original's order;
- the guard compares against `-1L`, which is what produces the `cmp ax,-1` /
  `cmp dx,ax` pair (`3D FF FF` / `3B D0`) rather than a single word compare.

Worth noting from the same round: `1fc8:0048` was invisible before round 110 because it
ends `retf 2`.

Ledger 480 rows - MATCH 38, RELOCS 416, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 476 B (3.573 %)**.

## Round 113: the register-assignment rule is not characterisable yet (no rows)
Two more units from the 160-unit pool, both one trait short, and between them they
**refute** the rule I wrote down last round:

- `13db:000c` (50 B) - `if (c) h2(b + c, a, b, a, h1(b, a) + 1);` in a near-Pascal
  function (params at 08/06/04). Structure and call forms are right - the first call is
  far (`90 0E E8`), the second near; what differs is that the original loads `b` into AX
  and `a` into DX before pushing the last two arguments, where MSC pushes both from
  memory. The register-push habit again (`322c:002c` was the same).
- `4e58:0004` (51 B) - a two-call initialiser with `register` parameters `e` and `g`.
  The whole body matches except the two prologue loads: MSC puts `g` in SI and `e` in
  DI, the original the other way round.

That second unit breaks round 112's "declaration order" conclusion, so
`docs/CONVENTIONS.md` now carries a three-row table instead of a rule: `3ede:00a0`
looks like first-use, `3874:000a` like declaration order, and `4e58:0004` like neither
(it gave SI to the second-declared parameter). The practical advice recorded there is
to treat these units as test-me-not-predict, bracketing with `register` on one
parameter at a time.

Ledger 479 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 433 B (3.558 %).

## Round 112: a two-register guard with no frame (40 B)
`crelay73.c` (`/G1 /AM /Gs /Os`): `3238:00fe` (40 B) - `old = g_1cf0; if (v == 1 &&
old == 0) h(old, old); g_1cf0 = v; return old;`. The unit was invisible before round
110's predicate fix because it ends `retf 2`.

What made it match is declaring **both** the parameter and the copy `register`: SI holds
`v`, DI holds the copy of the global (`8B 3E <g>`), the guard pushes DI twice, and the
function needs no frame at all. With only the parameter declared, MSC builds a frame for
`old` and the two prologue pushes never appear.

Two near-misses on the way, both now understood:

- `3874:000a` / `3877:0000` (38 and 41 B) - `h2(h1(c, b, a))` with `b` in DI and `c` in
  SI. MSC puts the *first-declared* register parameter in SI, so it assigns `b` there
  and the two prologue loads swap. This contradicts the round-93 note that MSC assigns
  by first use; the accurate statement is that it assigns in declaration order, and
  round 93's unit matched because there the two orders coincided.
- `322c:002c` (43 B) - one instruction off: the original pushes `AX` immediately after
  `mov si,ax`, MSC pushes `SI`. Same "use the register the value is already in" habit as
  the `or reg,ax` peephole.

Ledger 479 rows - MATCH 38, RELOCS 415, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 433 B (3.558 %)**.

## Round 111: a lost row recovered, and the symbol lookup made forgiving (32 B)
Worked round 110's corrected list of 160 complete unclassified units and immediately
found `49de:000e` (32 B) - `he(hd(a, b, c, d), 0);`. It had been **verified in round 86
and never written into the ledger**: that round produced three matches, two were added,
and the third was dropped between the match output and the ledger edit. Re-matching
reproduced it byte for byte, so it is now row 478.

Two process fixes came out of it:

- `tools/match.py` now falls back to a case-insensitive symbol lookup. The mangling
  difference between `__pascal` (`F_xxx` / `F`) and `__cdecl` (`_f`) has cost a retry in
  three separate rounds (`F_103B` vs `_f`, `4dca` and `49de` as `f` vs `F`); the tool
  now just finds it, and the error message already listed the available symbols when it
  did not;
- the lesson about round 86 is worth keeping: a round that produces several matches must
  have every one of them entered, not the ones that fit in the remaining time. The
  verification gate cannot catch a row that was never written down - only a re-scan of
  the pool can, which is exactly what the completeness filter did here.

That is also the first concrete payoff from round 110's bug fix: the corrected predicate
surfaced a unit that had been invisible to every earlier screen.

Ledger 478 rows - MATCH 38, RELOCS 414, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 393 B (3.545 %)**.

## Round 110: my ad-hoc scans had a bug - the unclassified pool is 160 units, not 11
Working round 109's cut-window list, `41e7:000a` refused to classify. The cause was in
the *scan scripts I have been writing all along*, not in the tools: their
`ends at a return` test was

    c[-3] in (0xCA, 0xC2) and c[-2] == 0 and c[-1] == 0

which only accepts `retf 0`. Every function ending `retf 2` / `retf 4` / `retf 6` /
... was therefore treated as *not ending at a return* and silently skipped. With the
test fixed to accept any `ret imm16`:

- the "complete, unclassified prologue units" list goes from **11 to 160**;
- round 109's cut-window count goes from **84 to 13 units (931 B)** - most of the
  earlier list were simply functions whose final `retf n` the scan did not recognise.

`tools/cutwin.py` now carries the corrected predicate and the first-return-from-start
logic (it previously extended forward from the window end, which also mis-reported
windows that merely overshoot a complete function).

The 160-unit list is the real remaining pool and it is roughly fifteen times what the
previous screens suggested. That does not mean 160 rows are available - the traits still
apply - but it does mean several rounds of candidates were never even looked at.

One such candidate was tried: `29ef:0007` (21 B) - `*p += v; return (v << 1) & 1;` with
the pointer declared first (`f(int __far *p, int v)`). MSC constant-folds the mask to
zero (`33 C0`) where the original emits `D1 D0` / `83 E0 01`, so it is blocked on
folding, not on structure.

Ledger 477 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 361 B (3.534 %).

## Round 109: a cut-window row, and 83 units behind the same mistake (34 B)
`crelay71.c` (`/G1 /AM /Gs /Os`): `4dca:000c` (34 B) - `h3(h2(h1(c, d, a, b)), 1);`.

This unit had been **filed as a fragment in round 89 and never tried**: `units.csv` says
28 bytes, but the function is 34 - the window ends inside its last far call. `dis.py`
showed the `C9 CA 08 00` four bytes past the window, and the transcription matched on
the first attempt.

That mistake is systematic, so it is now measured and given a tool. `tools/cutwin.py`
lists units whose declared window does not end at a return but where a return follows
within 64 bytes with no intervening `55 8B EC` prologue: **83 units, 9 471 bytes**.
Some are still false positives (a unit that tail-jumps out with `E9`, or whose real end
lies past 64 bytes), but the list is small enough to work by hand and it contains the
class of function that has been silently excluded from every screen so far.

Both results came from tools written in the last two rounds, not from harder analysis.

Ledger 477 rows - MATCH 38, RELOCS 413, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 361 B (3.534 %)**.

## Round 108: a disassembly helper, and two rounds of mistaken analysis corrected
Added `tools/dis.py` - not a disassembler, just an annotator that prints offsets, bytes
and the few facts that keep causing mistakes (jump targets, call forms, returns,
push/lea/mov encodings). Instruction lengths are computed only for a listed opcode set
and anything unknown is printed as `?` without advancing further assumptions.

It immediately paid for itself on `13d5:000c`, the unit rounds 98-99 argued about:

- the `jnz` at 0x0D targets **0x2A**, which is the start of the following `cmp` - it
  skips the `90` padding at 0x29. The displacement is correct; my "one byte short" claim
  was my own arithmetic, and round 98's link-time explanation plus round 99's withdrawal
  are both superseded by this;
- the `EB E0` at 0x43 targets **0x25** (`8B E5`), the shared epilogue - not the function's
  first instruction as round 98 said. So the unit is an ordinary
  `if ('e'||'E') { h6(); return; } if ('f') h5(); else h6b();` with both other paths
  converging on the epilogue;
- its only remaining obstacle is the two `90` padding bytes after the `CB` and the `jmp`,
  i.e. the nop-padding class, on a fully decoded 94-byte function.

`docs/CONVENTIONS.md` now carries the corrected rule in place of the withdrawn LINK
section: a branch whose target is one byte past an apparent block boundary is padding,
and `tools/dis.py` should be run before any displacement conclusion.

Ledger 476 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 327 B (3.522 %).

## Round 107: full verification sweep - all 476 rows reproduce (no new rows)
Ran `tools/verify.py` without `--fast`, i.e. every ledger row rebuilt from its recorded
source and settings and re-matched against the image. Result: **476/476 ok** - MATCH 38,
RELOCS 412, PENDING 24 - with `checkled.py` consistent. That is the first complete sweep
in ~35 rounds (the recent rounds used `--fast`), so the guarantee that the ledger is not
drifting now covers every row rather than a sample.

Nothing was added this round. The remaining work is unchanged from round 106: the
`/G0`-eligible units are down to one- and two-trait misses, and the traits are
code-generation habits (scratch-register naming, assignment persistence, branch
padding, immediate encoding) rather than unknown C.

Worth recording for the next sweep: `verify.py` takes long enough that a full run
belongs in a round of its own rather than alongside new work, which is why `--fast`
exists - but it should be run at full strength at intervals, and this round's result is
the baseline that any future regression would show up against.

Ledger 476 rows - MATCH 38, RELOCS 412, ASM 2, PENDING 24; verify (full) and checkled
green; own-code coverage 10 327 B (3.522 %).

## Round 106: a PENDING note corrected - the blocker is a spill, not scheduling
Re-examined `1e38:0002` (56 B, RECORD_CFG), which the ledger described as "scheduling
difference only - the original loads the global before the parameter". Transcribing it
in full shows that note was incomplete:

    int f(int a, int b, int c) {
        int old;
        old = g_40ba;  g_40b8 = a;  g_40ba = b;
        if (c) { if (c == -1) g_40bc = 7; else g_40bc = c; }
        g_40be = 1;
        return old;
    }

The original keeps `old` in **DX** from the first instruction to the last and has **no
frame at all** - `55 8B EC` then straight into the body. MSC 7 builds an ENTER frame
under `/G1` and a `83 EC 02` frame under `/G0`, because `old` is a local it will not
keep in a scratch register across ten statements. So the two-load ordering is a symptom;
the cause is assignment persistence, the same family as `122f:000c` (where the original
stores `r` *earlier* than MSC). The ledger note is corrected.

That also means the earlier claim that `/Ox /Oa /Os` matched "every instruction except
the order of the first two" cannot have been measured against this body as written.

Ledger 476 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 327 B (3.522 %).

## Round 105: `/G0` on the system-info routine - down to scratch-register choice (no rows)
`1486:0002` (89 B) is a system-info routine: it calls one function with a far pointer to
a DGROUP object (0x9740) and to a stack local, derives a value from the local, and ORs
three flag bits into globals 0x9738/0x9739, returning a far pointer to them. The
transcription gets the whole structure right - the `lea`/`push ss` pair for the local,
the flag tests, the two zeroing stores, the far-pointer return - and differs in exactly
three places, all scratch-register choices:

    original   lea cx,[bp-4] ; push ss ; push cx      and  dx = 0 ; push dx
    MSC 7      lea ax,[bp-4] ; push ss ; push ax      and  cx = 0 ; push cx

plus one argument order (`[bp+08]` before `[bp+06]` in the original, i.e. the call
passes `b` before `a`).

So the older compiler reaches for CX and DX where MSC reaches for AX and CX. That is
the same family as the `mov bx,ax` / `mov es,dx` exchange from round 74 and the
BX-as-register-variable class: scratch-register naming, not structure.

`/G0` has now been applied to five units - one row (`103b:000c`, 63 B), and four
reduced to one- or two-trait statements. The remaining classic-frame-with-locals
candidates are `11e1:0004` (91 B, a loop) and `10fa:0008` (105 B, a buffer formatter
with three global far-pointer stores); both are decoded at the block level but need
their parameter lists pinned before transcription.

Ledger 476 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 327 B (3.522 %).

## Round 104: `/G0` applied to three more units, all one trait short (no rows)
Continued the `/G0` sweep. Three units were transcribed; none matched, and each miss is
a different already-named trait:

- **`41e7:000a` (22 B)** - `h(0x4827, 6, a)`. Settles the push-immediate question
  from round 89: `/G1` gives `6A 06`, `/G0` gives `B8 06 00` / `50`, and the original
  has `68 06 00`. So the original's compiler picks `6A` for small immediates and `68`
  for larger ones - the standard 80186 rule - while MSC 7 either always shortens
  (`/G1`) or never does (`/G0`). No flag combination reaches it.
- **`122f:000c` (66 B)** - `r = c << 8; p++; r += *p;` inside `if (!h1(c))`. The
  source shape is now exact (`unsigned char __far *p`, `register unsigned char c`,
  the increment inside the branch), and the second load correctly zero-extends with
  `2A E4` rather than `98`. What differs is that the original **stores `r` to its
  frame slot before the increment** (`89 46 FE` ... `FF 46 06`) while MSC keeps `r` in
  AX across it - the older compiler does not keep an assignment in a register across a
  statement. Two-byte side effect: its local area is 2 bytes, MSC's 4.
- **`1036:000c`** - already recorded as PENDING in round 102; the padding wall.

So `/G0` has now been applied to four units, produced one row (`103b:000c`, 63 B), and
turned three long-standing mysteries into precise one-trait statements.

Ledger 476 rows (unchanged), PENDING 24; verify and checkled green; own-code
coverage 10 327 B (3.522 %).

## Round 103: a 63-byte marshalling wrapper, and the value of `/G0` (63 B)
`crelay70.c` (`/G0 /AM /Gs /Os`): `103b:000c` (63 B) - a wrapper that calls three
functions through far pointers it builds itself. What made it work:

- the callees are `__cdecl`, and **mixed**: `h1` near, `h2` far, `h3` near. That mix
  is visible only as `E8` versus `90 0E E8` in the image, and it took three attempts
  (all-far, all-near, then the mix) before the call sites agreed;
- the `__far` casts on a near pointer produce `push ds` / `push si`, and taking the
  address of a parameter produces `lea ax,[bp+0E]` / `push ss` / `push ax`;
- `register char *p` and `register int t` put the pointer in SI and the temporary in
  DI, and the locals are declared `u1, u2, r` so the result slot lands at `[bp-6]`,
  which is where the original stores it;
- everything else needed `/G0` for the classic frame - this unit has six bytes of
  locals, so no `/G1` transcription could ever have matched it.

Its sibling `1070:0008` (67 B, same shape with a DGROUP object at 0x4AD0 instead of a
pointer parameter) came out one instruction short: the original puts its single
register variable in **DI** (`57` / `8B F8`) where MSC puts it in SI (`56` / `8B F0`).
Same family as the round-93 finding, but reversed - MSC's first register variable goes
to SI, the original's went to DI here with no other register variable in play.

Ledger 476 rows - MATCH 38, RELOCS 412, ASM 2, PENDING 24; verify and checkled
green; own-code coverage **10 327 B (3.522 %)**.

## Round 102: the two bracketing near-misses recorded as PENDING (no new rows)
Round 100 and 101 produced two units that are fully understood but unreachable, and
they bracket the original's compiler between them - worth recording as ledger entries
rather than leaving in prose:

- **`200d:0006` (42 B)** - under `/G1` the only difference is the `or reg,ax` peephole
  (`0B F6` versus `0B F0`); under `/G0` the only difference is `6A 01` (the original's
  push-imm8) versus `B8 01 00` / `50`. Same source, two flags, one byte wrong either
  way: the clearest single demonstration that the original combines a classic frame
  with 80186 encodings.
- **`1036:000c` (52 B)** - under `/G0` everything matches (prologue `83 EC 08`, long
  staging `89 56 FE 0B D0`, pushes, teardown) except the original's nop padding
  (`75 06 ... EB 19 90` versus `75 05 ... EB 18`). It is now the cleanest test case for
  the padding class: one byte, no other differences, four optimizer settings checked.

Both are PENDING rows now, so the next attempt starts from a precise statement instead
of re-deriving it.

Also decoded for the next round: `103b:000c` and `1070:0008` (63 and 67 B) are a
matched pair of marshalling functions that pass far pointers to stack parameters
(`lea ax,[bp+0E]` / `push ss` / `push ax`) and to a DGROUP object (0x4AD0), with three
calls and a local spill at `[bp-6]`. They are the next `/G0` candidates but need the
parameter list pinned down first.

Ledger 475 rows - MATCH 38, RELOCS 411, ASM 2, **PENDING 24**; verify and checkled
green; own-code coverage 10 264 B (3.501 %).

## Round 101: `/G0` fixes the frame; the nop padding is still the wall (no rows)
Applied round 100's finding and measured its scope. Units whose image shows a **classic
frame with locals** (`55 8B EC 83 EC nn`) and are still unmatched: **32 in total**, of
which **10** are complete, call-bearing and free of `6A`. So the `/G0` correction is
real but its reach is tens of units, not the hundreds a first reading suggested - the
big "ENTER frame" class in `docs/BLOCKED.md` is about units where the *original* really
does use `ENTER`, which is a different population.

`1036:000c` (52 B) was worked to a single remaining difference:

    long r, u;                    /* the unused-but-referenced second long reproduces the 8-byte frame */
    r = h1();
    if (!r) return 0;
    h2(r, a, b, c, d, e);

Under `/G0` this gives the right prologue (`83 EC 08`), the right long staging
(`89 56 FE 0B D0`), the right pushes and the right teardown. All that differs is the
**nop padding**: the original's `75 06 ... EB 19 90`, ours `75 05 ... EB 18`. Four
optimizer settings were tried for the padding (`/Os`, `/Ot`, `/Ox`, `/Od`) and none
emits it: `/Ot` widens the branch to `08`, `/Ox` drops the second local (back to a
4-byte frame), `/Od` switches to `81 EC`.

So the padding remains the single obstacle for this family, exactly as recorded in
round 45 - and it now has a clean, otherwise-perfect test case attached to it.

Ledger 473 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 264 B (3.501 %).

## Round 100: the frame is `/G0`, and it costs the 80186 pushes
Chased the alternative-compiler thread into a **concrete flag finding** that corrects a
standing conclusion.

Measured on the same source with MSC 7.0 and MSC 6.00A (byte-identical in both):

    /G0 /AM /Gs /Os   55 8B EC 83 EC 02 FF 76 06 9A ... 8B E5 5D CA 02 00   <- classic frame
    /G1 /AM /Gs /Os   C8 02 00 00 FF 76 06 9A ... C9 CA 02 00              <- ENTER frame

`/G0` means "8086 target"; `ENTER`/`LEAVE` are 80186 instructions, so `/G0` *cannot*
emit them and uses the classic frame. Round 55's conclusion that the bare classic
frame is "unreachable with MSC 7" was therefore wrong: it is reachable, via `/G0`.

What is *not* reachable is the **combination** the original actually uses: classic
frame plus 80186 encodings. `200d:0006` demonstrates it in one unit - under `/G0` it
now differs in exactly one instruction, the original's `6A 01` versus our
`B8 01 00` / `50`. `/G0` cannot encode `push imm8`, and `/G1` (which can) forces
`ENTER`.

Practical consequence, recorded in `docs/CONVENTIONS.md`: units **with locals** must be
compiled with `/G0` (all 473 existing rows used `/G1`, which is why any unit with a
local frame had to fail), and a unit whose image contains `6A` cannot be matched by
any MSC 6/7 flag combination.

Two experiments along the way, both useful to have settled:

- the MSC 6.00A tools need `--no-dpmi` (they are real-mode); with HDPMI loaded they
  exit silently. The ledgers MS6 rows still reproduce (`1aa1:0130` verified again).
- MSC 5.1 and the disk-extracted 6.00A driver still produce nothing even with the
  fixed harness; only `toolchain/msc6c` and `msc7i` work.

First `/G0` application: `1036:000c` (52 B) got down to two differences - its local
area is 8 bytes where we reserve 4, and one branch distance follows from that. Not a
row yet, but it is the closest any locals-bearing unit has come.

Ledger 473 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 264 B (3.501 %).

## Round 99: the LINK /F idea does not yet explain the miss (no rows)
Tried to substantiate round 98's link-time hypothesis and could not. A sweep of the
image shows folded calls (`0E E8`) only where the callee is in the **same** code
segment; units whose callees are elsewhere keep `9A` - `34b7:001c`'s image is
`75 07 9A ... EB 05 9A ...`, and its displacements are self-consistent against the
five-byte `9A`. A shrink can therefore only affect units with in-segment callees, and
no matched row has yet been found where a branch crosses a folded call - which is
exactly the case that would decide whether LINK repairs the displacement. Until one
turns up, `13d5:000c` stays an **unexplained one-byte miss**, and the note in
`docs/CONVENTIONS.md` now says so instead of presenting the idea as a finding.

Two more screens produced nothing usable:

- complete relay units (18-60 B, no walls): exactly **one** unit (`1233:000e`), an
  interrupt wrapper;
- if/else shapes with two far calls: 14 units, but ten of them open with an `ENTER`
  frame (`C8 xx xx xx`) and the rest are long-arithmetic or tail-call constructions.

The pool of matchable shapes is now genuinely exhausted for this compiler: what
remains is either a named wall or code this compiler does not generate.

Ledger 473 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 264 B (3.501 %).

## Round 98: `13d5:000c` decoded, with a one-byte displacement puzzle (no rows)
Worked the 96-byte character dispatcher from round 97. Its structure is now clear:

    0x00  frame
    0x03  cmp [bp+0E],'e' ; jz 0x0F
    0x09  cmp [bp+0E],'E' ; jnz 0x2A
    0x0F  push 6 args (12,10,0C,0A,08,06) ; call ; mov sp,bp ; retf
    0x28  90 (padding)
    0x29  cmp [bp+0E],'f' ; jnz 0x44
    0x2F  push 5 args (10,0C,0A,08,06) ; call ; jmp 0x0F (EB E0)
    0x44  push 6 args ; call ; mov sp,bp ; retf

i.e. `for(;;) { if (c=='e'||c=='E') { h6(...); return; } if (c=='f') h5(...); else { h6b(...); return; } }`.

Two facts make it un-transcribable as a ledger row yet:

1. The `jnz` at 0x0D targets **0x2A**, one byte past the block boundary at 0x29 -
   i.e. into the middle of the following `cmp`. The block itself is 26 bytes long
   (0x0F..0x28, including the trailing `90`), so a displacement of `1A` would be the
   self-consistent value; the image has `1B`. The plausible cause is LINK's `/F`
   far-call folding: the object's `9A` (5 bytes) becomes `0E E8 rel16` (4 bytes), so
   a block that the compiler measured with the longer call shrinks by one *after* the
   displacement was emitted. That is a link-time effect inside a single function, and
   it would make several "impossible" displacements in this binary explicable.
2. The backwards `EB E0` from the `'f'` path returns to the *frame* at 0x00, not to
   the first comparison - so the C form is a loop whose top is the comparison, which
   is fine, but combined with (1) the exact byte sequence cannot be produced by the
   compiler alone.

This is worth recording because it is a **new explanation for a whole family of
branch-distance misses**: not the compiler's padding and not scheduling, but LINK
rewriting call sites and leaving near-branch displacements one byte off.

Ledger 473 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 264 B (3.501 %).

## Round 97: the last unclassified units, assessed (no new rows)
Widened round 96's completeness filter to 64-130 bytes: **12 complete, unclassified
units** remain outside every known class. Two were transcribed or decoded this round:

- `10b7:0006` (33 B) - `if (g_4a4c.lim < p) { p -= 2; p[0] |= 1; if (g_4a4c.base > p)
  g_4a4c.base = p; }`. Semantics are clear and the struct layout (+6 lim, +8 base) is
  right, but the **addressing style** differs: the original keeps the parameter in BX
  and the global's address in SI (`8B 5E 06` / `BE 4C 4A` / `39 5C 06`), while MSC 7
  puts the parameter in SI and addresses the global absolutely
  (`39 36 06 00`). A new detail on the staging family - the original prefers a base
  register for repeated field accesses.
- `13d5:000c` (96 B) - a `for(;;)` dispatch on a character: `'e'`/`'E'` runs a
  six-argument call and returns, `'f'` runs a five-argument call and jumps back to the
  top (`EB E0`), anything else runs a third six-argument call and returns. The `90`
  bytes in it sit after `CB` (between blocks, not after a short jump), so they are not
  the nop-padding class. Decoded but not yet transcribed - the loop shape has no
  obvious C form that produces the backwards jump while still ending both other paths
  in a return.

The other ten are interrupt wrappers (`1233`, `138c`, `103b`, `11ea`, `11e1`), `les`
users (`1070`, `1486`), an address-arithmetic walker (`12aa`), a five-`movs` copy
(`4f67`), and a digit parser (`133f`) - all in families already documented.

Ledger 473 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 264 B (3.501 %).

## Round 96: an if/else over two calls, from the unclassified list (25 B)
`crelay69.c` (`/Os`): `34b7:001c` (25 B) - `if (!a) h1(); else h2();`. The two calls
share a tail, so there is no nop padding and no branch-distance problem; the unit's
inventory window simply runs into the following function, which is why its size had to
come from the object symbol rather than `units.csv`.

The candidate came from a new view: filtering the unclassified pool to units that are
**complete** (their core ends at a return) rather than by prologue bytes. That leaves
just **11 units of 24-64 bytes**, of which this was one - the rest are either
interrupt wrappers, `les`-based, or have multi-branch range checks.

The remaining complete-unclassified units, for the next round:

- `3bd3:0002` (52 B) - a four-way range test (`jl`/`jo`/`sub 0x800`/`jg`) guarding a
  four-argument call; the exact source comparison is not obvious from the branch
  layout (signed checks plus an overflow check suggest a hand-shaped expression);
- `10b7:0006` (33 B) - a struct update against a global at 0x4A4C, with `4B 4B`
  (decrement twice) where MSC would likely emit `83 EB 02`;
- `1233:000e`, `138c:000c`, `1137:0002`, `11ea:0002`, `10b9:0007`, `103b:000c` - all
  interrupt wrappers or `les`-heavy, i.e. already-known families.

Ledger 473 rows - MATCH 38, RELOCS 411, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **10 264 B (3.501 %)**.

## Round 95: probe.py re-proposed claimed windows - fixed (no new rows)
Ran the full `probe.py` sweep (all 150 calibration sources against every window in
the image) hoping for free sibling rows. It reported one hit, `3670:00e2 = _F_3309`
(12 B) - but that window was **already in the ledger**, and `--write` appended it a
second time. `verify.py` caught it immediately (`DUP 3670:00e2`), the duplicate was
removed, and the ledger is back to 472 rows.

The cause is in `probe.py`'s second pass, which walks every return-delimited window
inside an *unmatched* unit: it never checked whether the window's start address is
already claimed, so any window that a ledger row happens to cover gets proposed again.
A guard on the computed offset fixes it, and a re-run reports **0 hits** - so the
sweep is genuinely exhausted rather than being suppressed by the fix.

Two smaller screens were tried first and produced nothing: a declaration-order
register-parameter screen (no units, as round 94 predicted) and a single-register
parameter screen (no units survived the wall filters). The pool's remaining units are
not reachable by byte-pattern screens alone.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 94: screening with the new rule finds nothing new (no rows)
Tried to turn round 93's finding into a search: units whose prologue uses the
declaration-order assignment (`56 57` push order with `SI = a`, `DI = b`). The screen
returns **zero** units in the 24-90 byte range - because the original's prologue push
order is DI-then-SI even when the assignment is declaration-ordered, so the byte
pattern I filtered on does not exist.

The attempt did sharpen the rule, though: the original separates the two decisions.
**Which register a parameter gets** follows the declaration (`a -> SI`, `b -> DI`);
**the order the prologue loads them** follows first use. At `3ede:00a0` it pushes DI
before SI and loads `b` first, yet `a` still owns SI. MSC 7 couples both to first use,
which is precisely why a single exchange in the prologue is this class's signature -
and why it cannot be screened for from the prologue bytes alone: it depends on which
parameter the body touches first.

Recorded in `docs/CONVENTIONS.md`; no new rows this round.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 93: register parameters, pinned down (no new rows)
`3ede:00a0` (64 B) is a global-writing relay - `h1(); h2(b, g_838e);` then six stores
including two byte globals - and it was transcribed in one attempt. Everything matches
except one exchange in the prologue:

    original   8B 7E 08 (DI = b)   8B 76 06 (SI = a)
    MSC 7      8B 76 08 (SI = b)   8B 7E 06 (DI = a)

That single exchange explains the "reversed register roles" class that has blocked
units since round 36: **the original allocates register parameters in declaration order
(a -> SI, b -> DI), MSC 7 allocates them in order of first use** (`h2(b, ...)` touches
`b` first, so `b` gets SI). When a body's first use is not its first declared
parameter, every register reference in the unit swaps and no source reordering can fix
it without also moving the stack offsets. Recorded in `docs/CONVENTIONS.md`.

This also means the earlier phrasing ("the original reverses them for multi-register
functions") was backwards for such units - the original is in declaration order and
MSC is the one that reverse-allocates.

Also re-read the PENDING list against the newer rules; nothing there is unblocked, but
`20b4:0160` (_read24) is the most promising remaining unknown.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 92: the alternative-compiler thread is unresolved, not negative (no rows)
Continued round 91's corrected diagnostics. With `--run` working, both DOS 6.00A
passes were exercised directly - `CL.EXE /c /AM /Gs /Os` from its own directory with
`TMP` set, and `C1.EXE` on the same source. Neither produces an object, a stdout log,
a stderr log, or any touched file, and both return control to the shell.

Two supporting checks this round: `CL.EXE` is a plain DOS MZ image (`e_lfanew = 0` -
no OS/2 or Windows header), so it is the right driver, and `CL.MSG`, `CL.ERR`,
`C1.ERR`, `C23.ERR` are all present next to it, so a missing message file is not the
cause.

Important negative result: **`if errorlevel` cannot be used as evidence here.**
DOSBox-X's built-in shell reported success for a run that produced nothing, so it
does not distinguish a zero exit from a shell that never propagates exit codes. That
rules out the simplest "did it run" probe and is recorded in `docs/GAP.md`.

The thread stays open with two live explanations: the tools report through the console
(INT 10h) which the SDL dummy video driver hides, or the 6.00A DOS driver needs
something the extraction did not supply. Distinguishing them needs an observable
screen, which the headless harness cannot provide.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 91: the diagnostic harness was broken - a correction, not a row
While trying a fourth screen (call-free setters, 37 units) the `--run` diagnostics came
back empty again, and this time the cause is identified: **`build.py --run` never ran
the given command.** It appended the normal `CL.EXE` line unconditionally and used the
flag only to skip the object check, so rounds 70-71's conclusion that the DOS MSC 6.0
driver "produces no object and cannot be observed" was measured through a harness that
ignored the request. That conclusion is withdrawn as stated.

`build.py` now substitutes the command for the CL line; the harness is verified end to
end (`echo X > E:\BUILD\E.TXT` creates the file, and `; echo` after a compiler run
proves the compiler returned). Re-running the DOS MSC 6.0 driver with a working harness
still yields no object and no stdout/stderr capture, but two caveats keep that
inconclusive: compiler messages go to the console (MSC 7 behaves the same under
redirect), and a hung shell can still leave files behind - one run created its marker
and then timed out.

Also screened this round: `4d98:000a` (MSC narrows `(a + b) & 3` to byte arithmetic
where the original stays 16-bit), `4344:000e` (correct 4-byte element scaling, but
`2A E4` / `8A 87` come in the opposite order), `141f:0000` / `1420:000f` / `1466:0052`
(the original gives even an empty function a full frame; MSC `/G0` emits only
`CA 0A 00`). No rows.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 90: a branch-tolerant screen, two more walls (no new rows)
Third screen: units with at most one branch, no known wall, 20-52 bytes. Two fresh
candidates transcribed, both blocked on habits already named, but with a new detail:

- `4ab2:000c` (32 B) - `r = h1(a); if (r != -1) h2(r);`. The original holds **both**
  `a` and `r` in SI, reusing the register once `a` is dead: `8B 76 06` (a),
  `56` (push a), call, `8B F0` (r). MSC 7 allocates SI for `a` and DI for `r`
  (`57 56` in the prologue) and never reuses a dead register variable - a new detail
  on the staging wall, and the reason the row is out of reach even though the shape is
  identical.
- `3a51:0004` (36 B) - `nc(z, h2(h1(x, x, y)))`. Register staging for `x` is fine, but
  MSC evaluates `z` first (right to left) while the original pushes it last: the
  argument-evaluation-order class from round 38, third sighting.

Also seen and skipped: `1233:000e` (indirect `call far [0x51A6]` with AH arguments,
the interrupt-wrapper class) and `39fc:000c` (five-call sequence with a `-1` guard,
not yet decoded).

The screen is small enough to finish next round; its remaining units are mostly in
classes already named, so the expected yield is low - the honest read is that the
pool is now dominated by the compiler habits rather than by source shapes.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 89: three more candidates closed, one new narrow class (no new rows)
Worked the last untried units from round 87's widened screen:

- `4dca:000c` (28 B) - the inventory **cuts the function mid-instruction** (`90 0E E8`
  with no displacement). It is a fragment, like the 237 units already classified that
  way, and cannot be a row at that size.
- `31dd:0008` (27 B) - `h2(h1(a, h0()))`. The original calls `h0()` **before** pushing
  `a`, MSC 7 pushes `a` first and then evaluates the call: the argument-evaluation
  order class from round 38, confirmed on another unit.
- `41e7:000a` (22 B) - `h(0x4827, 6, a)`. Only one byte differs: MSC pushes the small
  literal with the 80186 short form (`6A 06`) where the original uses `68 06 00`.
  Four formulations (plain, cast to `char`, `6L`, `0x0006`) all give `6A`; routing the
  value through a variable gives `B8 06 00` / `50` instead, which is no closer. The
  original does use `6A` elsewhere, so this is a per-site choice - recorded in
  `docs/CONVENTIONS.md` as a narrow, named reference difference.

No rows this round, but the widened screen is now fully triaged: every unit in it is
either a row, a fragment, or one of the named walls.

Ledger 472 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 239 B (3.492 %).

## Round 88: a long-result relay (29 B)
`crelay68.c` (`/Os`): `2193:000c` (29 B) - `h1(-1); h3(h2(a), a);`. Three things had
to line up and each was one of the existing levers:

- the parameter is `register`, so all three uses push SI (`56`) instead of the
  frame slot;
- the middle call returns a **long**, so its DX:AX is pushed as a pair into the
  tail call (`52 50 56`);
- the tail call is `__near` (`E8`), which the first transcription got wrong by
  assuming a far call - the far form alone accounted for the last two differences.

The unit's final byte is padding, so the row is 29 rather than the inventory's 30.

The candidate came from round 87's widened screen (stores and loads allowed), which
still has a handful of untried units left.

Ledger 472 rows - MATCH 38, RELOCS 410, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **10 239 B (3.492 %)**.

## Round 87: a seventh wall named - register variables in BX (no new rows)
Widened round 86's screen to allow stores and loads, which surfaced the `11ax` family.
`11a2:000c` (30 B) is `*p = nc(*p, v);` and it is now **fully understood**:

    push bx; bx = p; ax = *p; dx = *(p+1); cx = v; call nc   ; fastcall: DX:AX = value, CX = v
    *p = ax; *(p+1) = dx; pop bx

with `p` a *near* pointer and `nc` a `__far __fastcall` function - that combination
reproduces every instruction except the two that preserve BX. The original treats
**BX as a callee-saved register variable**; MSC 7 only allocates SI and DI and uses
BX as scratch, so it must spill to a frame slot and build an `ENTER` frame.

Eight unmatched units (518 bytes) start with `53` in the prologue and are now the
`register variable in BX` class - the seventh distinct compiler habit that blocks
whole units. `docs/BLOCKED.md` has 19 classes and the unclassified pool is
**166 units / 10 430 B**.

Also screened and blocked: `3c3d:000c` and `2d60:000e` (char arguments pushed
without promotion), `1cbf:0020` (an AH-argument interrupt wrapper).

Ledger 471 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 10 210 B (3.482 %).

## Round 86: two more pure relays (58 B), and a push-encoding observation
`crelay67.c` (`/Os`), continuing round 85's relay screen:

- `4f5c:0004` (25 B) - `g_2e2a = 0; hb(g_860e, a);`, an immediate store followed by a
  call with a DGROUP object pointer;
- `3bd6:004c` (33 B) - `hd(a, b, c, d); nf(c); return c;`, a four-argument far call,
  then a near call forwarding the third parameter, which is also returned.

Both units include a padding byte, so each row is one byte smaller than the
inventory says - the same trap as round 85.

Three further candidates were screened and are blocked on small, named things:

- `41e7:000a` (22 B) - `h(0x4827, 6, a);`. MSC emits `6A 06` (the 80186 push-imm8)
  where the original emits `68 06 00` (push-imm16). The original uses `6A` freely
  elsewhere in the image, so this is a context-dependent choice MSC makes for a
  literal `int` argument; a cast or a wider constant did not change it.
- `2054:000e` (30 B) - `hc(q * 0x50, p + q * 0x50, r, s, t);`: MSC pushes the
  `imul` result before adding the second parameter, the original adds first. One
  instruction of scheduling.
- `3ea9:0042` (23 B) - the original doubles the call result with `03 C0`
  (`add ax,ax`), MSC with `D1 E0` - the doubling class, now on a fourth unit.

Ledger 471 rows - MATCH 38, RELOCS 409, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **10 210 B (3.482 %)**.

## Round 85: seven rows from a pure-relay screen (159 B)
Screened the pool for units whose body contains **nothing but** framing, pushes,
calls and a return - no `les`, no segment moves, no stores, no compares, no shifts.
Twenty-nine units qualified; five were transcribed in one compile and all five
matched, and the sibling sweep then added two more:

| row | size | shape |
|---|---|---|
| `47c0:0000` | 22 | `h(a, 1, 0x64);` with `a` in a register (pushed from SI) |
| `4aa1:0006` | 21 | `h2(h1(a));` |
| `2d3e:000e` | 23 | `h2f(h1b(a, b));` with the outer call `__fastcall` (result stays in AX) |
| `2d58:0006` | 23 | `h3(h0(), a, 1);` |
| `2e7a:0000` | 30 | `h2(h4(h0(), a, b));` |
| `4aaa:0006`, `4ab0:0000` | 21 each | siblings of `4aa1:0006` (found by `reuse.py`) |

Three levers did the work, and each was already in the rule table: `register` on a
parameter that is pushed (SI staging), `__fastcall` for a tail that leaves the value
in AX, and reading the size from the object symbol rather than the inventory - two
of these units include a padding byte, and `2e7a`'s inventory size (28) actually cuts
the function two bytes short, which `verify.py` caught as "does not end at a
return".

The screen itself is the reusable artefact: excluding the instruction families that
produce the known walls leaves a list where each unit needs at most one lever.

Ledger 469 rows - MATCH 38, RELOCS 407, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **10 152 B (3.462 %)**.

## Round 84: the cdecl reversal pays again (38 B)
`crelay65.c` (`/Os`): `1ebd:000e` (38 B) - `if (cd(b, a)) h2b(1, g_4668); return 1;`.
The first transcription pushed the two parameters in the wrong order and differed at
exactly two offsets; writing the cdecl call as `cd(b, a)` (round 79's reversal rule)
made the whole unit match, including the `8B E5` cleanup that MSC 7 chooses in this
context.

The other candidate examined, `4718:0008` (48 B), is a far-struct word swap
(`p->f80 = p->f82; p->f84 = p->f86;`) and is blocked on staging rather than logic:
the original holds the pointer halves in SI/DI (`8B 76 06` / `8B 46 08` / `8E C7`)
and indexes through `es:[si+..]`, while MSC loads it with `C4 5E 06` into ES:BX and
indexes through BX. Every instruction is understood; the register choice is not
reachable.

A second row came free from the sweep: `tools/reuse.py` matched `1e10:000a` (27 B)
against round 79's `F_1DFC` source, byte-identical modulo the call targets, so it was
added directly.

Ledger 462 rows - MATCH 38, RELOCS 400, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 991 B (3.407 %)**.

## Round 83: two giant blobs explain the byte count (no new rows)
Checked how the remaining unmatched bytes are distributed by segment, and found that
two entries dominate:

- `515a:0008` - **26 882 bytes in one unit**, starting with an ordinary prologue
  (`55 8B EC 57 56 8B 7E 0A 57`) and ending in a run of zero padding;
- `2603:000e` - **14 458 bytes in one unit**, opening with `83 C4 E2` (a 226-byte
  frame) and ending in what is clearly a data table (`10xx` values every 0x20).

Together with `2baa` (4 612 B) that is roughly 46 KB of the unmatched total sitting in
three entries that can never be a single ledger row: either one enormous function or
a region the inventory merged. This is why the pool's *byte* count looks large while
the *candidate* count is small - `tools/nextup.py` already excludes them by its
100-byte ceiling, which is the right behaviour.

Nothing here is matchable, but the accounting is worth recording: anyone reading
"10 KB unclassified" should know that 46 KB of unmatched material is outside that
figure because those units are classified by their first trait, not by their size.

Also re-read the three most promising PENDING rows (`4fab:000a` 16 B, `11d8:000c` 41 B,
`1871:7874` 24 B) against the newer rules; each is blocked on a redundant `8B E5`
teardown, a `C3 90`/`EB 03` padding pair, or an `les` that MSC will not emit - the
same walls as the rest of the pool.

Ledger 460 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 926 B (3.385 %).

## Round 82: two more misses named, one of them a known peephole (no new rows)
Round 81's `200d:0006` curious null test is explained: the original emits
`8B F0 0B F0` (`mov si,ax` then `or si,ax`) where MSC emits `8B F0 0B F6`
(`or si,si`). Both test the same value - it is the **`or reg,ax` peephole** recorded
in round 35, not a semantic difference. So `200d:0006` is blocked by that peephole
(one encoding) rather than by anything structural, which is worth knowing: the
remaining difference between that unit and a row is a single byte pair MSC will not
produce.

Also examined:

- `1f5f:005e` (32 B) - `long f(a, b) { h2(a, b); return ((long)b << 16) | a; }` with
  the parameter roles `a -> SI`, `b -> DI`, which *is* MSC's assignment order. It
  still misses because the original stages the second parameter through AX for the
  push and then copies it to DI (`8B 46 08 50 8B F8`), while MSC either reads the
  frame at the push or loads DI first - the same staging difference seen on the
  `1f3x` family.
- `1f45:00ec` (37 B) - the sibling shape, blocked on the reversed roles.

Three of the four remaining walls (padding, `or reg,ax`, staging) are now confirmed
on multiple units each, which is the useful outcome of these rounds even without a
row.

Ledger 460 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 926 B (3.385 %).

## Round 81: two cdecl-list candidates narrowed (no new rows)
Working round 80's cdecl list, two units came close:

- `21ec:0004` (36 B) - `if (!nc(a)) { cdp(g_1200); h2(1); }`. Every byte matches
  except the cleanup: the original emits `83 C4 04` after the cdecl call, MSC 7
  emits `8B E5` in this position (and the branch distance follows). That is the
  context-dependent cleanup class from round 54 - confirmed here, not solved.
- `200d:0006` (42 B) - `p = (char __far *)cd(x, 1); if (!p) return 0; g_5ba++;
  return p;`. Four transcriptions (far pointer, near pointer, `register` on each)
  bracket the shape: the *near-pointer* version with a plain `register` local gets
  the prologue (`55 8B EC 56`), the cleanup (`83 C4 04`), the register staging
  (`8B F0`) and the DGROUP return segment (`8C DA`) all right, and differs only in
  the null test - the original ORs the offset with the call's segment half
  (`0B F0`, testing the full far value) where MSC tests the offset alone
  (`0B F6`) - plus the branch distance that follows from it.

So `200d:0006` is a one-instruction miss with a fully documented cause: the older
compiler tests a far pointer in a way MSC 7 will not.

Ledger 460 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 926 B (3.385 %).

## Round 80: a six-unit family mapped, blocked by register roles (no new rows)
Turned round 79's cdecl rule into a search: 21 unmatched units of 20-64 bytes contain
a cdecl cleanup (`83 C4 <n>`). Six of them are one family -
`1f35:0000`, `1f37:000c`, `1f3a:0008`, `1f3d:0004`, `1f40:0000`, `1f42:000c`, all
44 bytes, differing only in the pointer constant they pass:

    push di / push si; si = b; ax = c; h1(c);
    push ax; push ds:<const>; push a; push si; di = a; h3(...); add sp,10
    ax = si; dx = di; return            ; the long (a, b)

so each is `h3(h1(c), g_<const>, a, b); return ((long)a << 16) | b;` with `b` in
**SI** and `a` in **DI**. That is the reversed register-parameter assignment from
round 36 (`a` is declared first but lands in DI): MSC gives the first register
parameter SI, so no source order reproduces it while keeping the stack offsets.

Transcribing one member confirmed the whole shape (`cbg1.c` matches everything except
the staging and the return), which means the remaining five need no further analysis -
they are the same unit with different constants. 264 bytes total, all blocked on the
same 2-byte lever.

Ledger 460 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 926 B (3.385 %).

## Round 79: cdecl argument order, and the round-13 puzzle solved (27 B)
`crelay64.c` (`/Os`): `1dfc:00fa` (27 B) - `h2(cd(b, a) + 1);`, where the cdecl call's
arguments are written in the *reverse* of the push order. The result is incremented
in place (`40`), forwarded, and cleaned with `8B E5`.

That rule also closes the **round-13 puzzle**: `1dfc:0116` / `1e12:0006` (34 B each,
transcribed and abandoned seventeen rounds ago because MSC emitted `8B E5` and
memory pushes where the original had `83 C4 08` and register staging) fall into place
once two things are right - the arguments reversed (`cd4(b, a, b, a)`) and the second
parameter declared `register`. With those, the cleanup becomes `83 C4 08` and `b`
stages through SI, exactly as the original. The last difference is that the original
loads `a` into **AX** once and pushes it twice, while MSC re-reads the frame slot;
not reachable, but the unit is now a one-instruction miss instead of a mystery.

Also probed: `4daa:0002` (30 B), an indirect `call [bx+0x2C28]` through a near
function-pointer table. Getting the pointer width right (`__near __fastcall`) made
the table access match; the remaining difference is `03 D8` (`add bx,bx`) versus
MSC's `D1 E3` (`shl bx,1`) - the doubling class again, on a third unit.

Ledger 460 rows - MATCH 38, RELOCS 398, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 926 B (3.385 %)**.

## Round 78: a scaled-divide relay (25 B) from a near-function sweep
`crelay63.c` (`/Os`): `486e:000a` (25 B) - `h(a * b / 100);` in a near-Pascal
function: `imul` by the second parameter, then a signed `idiv` by 100
(`B9 64 00`, `99`, `F7 F9`).

Found by sweeping the pool for functions that end in a **near** return
(`C2 imm16`) rather than a far one - a direct application of round 77's rule. Only
six unmatched near functions of 24-48 bytes exist, so the sweep was both cheap and
targeted.

The other five, and where they stand:

- `5069:0004` (44 B) - a clamp. It comes out one byte short because MSC expands
  `r += 2` on a register variable as a reload plus two increments
  (`8B 76 04 46 46`) where the original emits `83 C6 02`; the branch distance
  differs by exactly that byte.
- `21ee:0008` (34 B) - `8E 06 <disp>`, the inlined-`MK_FP` class.
- `4daa:0002` (30 B) - an indirect `call [bx+0x2C28]` through a word pointer table
  after doubling the previous call's result; transcribable but the table type would
  have to be guessed.
- `230e:000a`, `385d:0002` - both mix far-pointer table indexing with 5-argument
  calls and remain undecoded.

Ledger 459 rows - MATCH 38, RELOCS 397, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 899 B (3.376 %)**.

## Round 77: near versus far, and a stored-back parameter (30 B)
`crelay62.c` (`/Os`): `4db8:0006` (30 B) - `c = nc(a, b, c); h2(c, 0);` in a
**near**-Pascal function: the call's result is stored back into the last parameter
slot (`89 46 04`) and forwarded as the first word of the next call.

The one thing that had to be right is the frame: the unit ends `C9 C2 06 00`, i.e.
`ret 6` (near), not `CA` (far). My first transcription read it as far and came out
with three push offsets each two bytes too high - everything else matched. That rule
is now in `docs/CONVENTIONS.md`: when every parameter offset is two bytes off, check
the return opcode before rewriting the parameter list.

Two other candidates were examined and blocked:

- `1e1e:002a` (27 B) - `if (x <= 0xFF) return x; return h3(x);`. The original keeps
  the value in **CX** for both the compare and the return (`8B 4E 06`, `81 F9 FF
  00`, `8B C1` twice); MSC 7 compares the frame slot directly and never caches a
  parameter in CX, in signed, unsigned, and `register` variants alike.
- `1e1e:0008` (33 B) - a struct-returning call whose `struct L { int lo, hi; }`
  parameter and return can be transcribed, but MSC 7's `__pascal` struct return
  refuses to compile in this shape (silent abort, no object and no log - the known
  symptom).

Ledger 458 rows - MATCH 38, RELOCS 396, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 874 B (3.368 %)**.

## Round 76: a field-forwarding pair (24 B)
`crelay61.c` (`/Os`): `2b8b:000e` (24 B) - `h1(); h2(p->f6);`, a no-argument call
followed by a call forwarding a far pointer's field (`C4 5E 06` load, `26 FF 77 06`
push).

Three near-misses this round confirmed classes rather than adding rows:

- `2b33:0006` (23 B) - `p->tab[i]` on a far struct. MSC emits `D1 E6` (`shl si,1`)
  for the index doubling where the original emits `03 F6` (`add si,si`), and
  rewriting the source as `i + i` or as explicit byte arithmetic does not change it:
  the doubling idiom is the `add reg,reg` class, confirmed on a second unit.
- `3eb9:0006` and the `3ede:000a` / `3ede:0024` pair - char-member getters, blocked
  only by the `8B D8` / `8E C2` swap (MSC sets ES first).
- `4e9b:0008` - the long load/store where the original stages through BX.

One process note worth recording: while transcribing `2b8b:000e` I mis-copied its
`retf` count into the comment and briefly believed the row was a prefix match. A
direct byte comparison against the image (`img` vs `obj` in one script) settled it in
seconds - that check is cheaper than re-deriving the size, and should be the reflex
whenever a row looks too good.

Ledger 457 rows - MATCH 38, RELOCS 395, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 844 B (3.357 %)**.

## Round 75: a nested call with a register parameter (24 B)
`crelay60.c` (`/Os`): `32da:000c` (24 B) - `h2(h1(a));` with the parameter declared
`register`, so the inner call pushes SI and the outer one pushes the returned AX.
The plain-parameter form (`int a`) pushes the frame slot instead
(`FF 76 06` vs `56`), which is exactly the one byte that made this unit fail when it
was first transcribed in round 74's batch.

That also resolves round 74's open item: the candidate compiled cleanly there but
its match output was cut off by a neighbouring symbol's size error, so it was never
actually compared.

Two char-member getters (`3eb9:0006`, and the `3ede:000a` / `3ede:0024` pair) were
tried again, both as a struct member and as explicit pointer arithmetic
(`*((char __far *)h3(a) + 3)`); both forms produce
`8E C2 8B D8` where the original has `8B D8 8E C2`. The struct-member offsets are
correct either way, so the only remaining difference is that two-instruction swap -
the same allocation difference as `4e72:000a`.

Ledger 456 rows - MATCH 38, RELOCS 394, ASM 2, PENDING 22; verify and checkled
green; own-code coverage **9 820 B (3.349 %)**.

## Round 74: struct packing is a flag, not a source shape (no new rows)
Five tiny candidates (20-26 B) were transcribed in one batch. None matched, but one
of them produced a **new compiler-flag finding**:

`4e72:000a` reads a word at `es:[bx+7]` - a far-struct member right after seven
`char`s, with no padding. MSC 7's default aligns that member to +8; adding
**`/Zp1`** moves it to +7 and removes the offset difference entirely. Recorded in
`docs/CONVENTIONS.md`: when a unit's field offsets land on odd addresses, try `/Zp1`
before doubting the structure.

The other four, and what stopped them:

- `4e72:000a` and `3556:000e` - after packing, each differs only in two swapped
  instructions: the original emits `8B D8` / `8E C2` (`bx = ax`, then `es = dx`)
  where MSC emits the segment load first.
- `4e9b:0008` (24 B, `long f(long v) { g = v; return v; }`) - the original loads the
  low word into **BX** and the high into AX, then rebuilds DX:AX before returning
  (`8B D0` / `8B C3`); MSC loads them straight into AX/DX and returns for free. A
  worse register choice by the older compiler, and not reachable from source.
- `32da:000c` (24 B, `h2(h1(a))`) - block reason not yet isolated (it compiled
  cleanly in the batch, so the match output was cut off by the size error on the
  neighbouring symbol).

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 73: the bitfield layout pinned, and the real blocker named (no new rows)
Round 72's open question is answered. `437e:0032`'s table entry is a 4-byte struct
whose second word is a bitfield group laid out **8 / 3 / 4 / 1** from the low bit:

    struct E { char pad[2]; unsigned a:8; unsigned b:3; unsigned c:4; unsigned d:1; };

which reproduces the original's `and ch,7` (preserve bits 8-10), the `shl ax,11`
(field `c` at bit 11) and the trailing `or byte [..+1],0x80` (field `d`).

But three transcriptions - with and without a local pointer, with the index and the
pointer declared `register` - all fail on the same thing: MSC 7 **spills the table
pointer across the intervening `h2()` call** (`89 5E FE` / `8B 5E FE`) and therefore
builds an `ENTER` frame, while the original keeps the scaled pointer in SI
(`C1 E6 02`, then three `[si+0x866E]` accesses). `register` does not change it: MSC
only keeps SI/DI for values with no call in between.

That is now recorded in `docs/CONVENTIONS.md` as a class-level statement, because it
will decide several other candidates the same way: *a value that must stay live
across a call* is out of reach even when the logic is fully understood.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 72: a bitfield writer decoded (no new rows)
Back at the unblocked pool after the compiler thread. `437e:0032` (58 B) was
decoded byte by byte and is a **bitfield writer into a 4-byte table**:

    si = b;  h1(b);  di = h1();          ; result kept in DI
    ax = h2();  ax = a - ax;  ax = -ax;  ; = a - h2()
    si <<= 2;                            ; 4-byte entries
    ax <<= 11;
    cx = [si+0x866E];  ch &= 7;  ax |= cx;
    [si+0x866E] = ax;                    ; word field
    or byte [si+0x8671], 0x80            ; top bit set separately
    return di;

So the word at table+2 is written as `(old & 0x0700) | (value << 11)`, and then bit
15 is set through a separate byte operation - the shape MSC produces for two or
three bitfield assignments in a row. The exact field declaration order is not yet
pinned down, and without it the `shl`/`and ch,7` combination cannot be reproduced;
one more attempt with a `struct { short x; unsigned v:5; unsigned m:3; ... }`
should settle it.

Two probes and two sweeps came back empty (`reuse.py`, and `probe.py` over every
calibration symbol), so the pool's easy seam is closed for now.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 71: the pre-MSC7 thread shelved, with a correction (no new rows)
Per round 70's own plan, this round either finished the MSC 6.0 diagnosis or
shelved it. It was shelved, and the round also **corrected round 70's conclusion**.

`build.py --run` was used for three probes:

- `C:\MSC6DOS\BIN\C1.EXE > D:\BUILD\T3.TXT` - no output, no file;
- `echo A & CL.EXE /? & echo B` - nothing at all (the DOS shell here does not
  support `&`), so that probe was worthless;
- **control: `C:\MSC7I\BIN\CL.EXE > D:\BUILD\T5.TXT`** with the *known-good*
  compiler also produced no output and no file.

The control disproves round 70's inference: a missing redirect file does not mean
the driver crashed DOSBox, because the working CL 7.0 behaves identically when run
without `/c`. `docs/GAP.md` now records the correction, and the next attempt must
observe CL's behaviour from inside the program run (exit code via `if errorlevel`,
or a driver-written log) rather than through shell redirection.

The thread is shelved for now: three rounds, no rows, and one wrong inference. The
remaining 154 unblocked candidates are the better use of the next rounds.

Also tried and blocked this round: `2daf:000c` (97 B), the sibling of `2d9b:0002`,
transcribed with the cdecl pointer-first argument order learned in round 54. It
matches structurally but keeps MSC's `8B E5` cleanup where the original has
`83 C4 0C` - the class documented in round 54 - and MSC also stages the two global
stores through AX instead of `C7 06` immediates.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 70: the DOS MSC 6.0 driver crashes the DOS session (no new rows)
`build.py` grew a **`--run "<dos command>"`** diagnostic mode (it substitutes one
DOS command for the CL line and skips the object check), which finally makes the
DOS session scriptable through the same invocation that is known to work. With it:

- `dir C:\MSC6DOS\BIN\CL.EXE > D:\BUILD\T.TXT` works: the mount sees the
  extracted driver (`CL EXE 28.858`), so extraction, mount and redirection are all
  fine. Manual conf files of my own, by contrast, never ran the autoexec at all -
  `build.py`'s environment (APPDATA redirect, cwd, conf path) is required, which
  is now proven rather than suspected.
- `cd C:\MSC6DOS\BIN & CL.EXE > D:\BUILD\T2.TXT` produces **nothing**: no
  banner, no error, and the redirect file is not even created. A command that
  fails normally still creates its (empty) redirect target, so the DOS session is
  being torn down mid-line - the driver is *crashing* DOSBox, not exiting.

That is a much more specific symptom than "no object". Two plausible causes to
test next: MSC 6.0's CL wants a particular memory configuration (the phase
binaries are huge - C2.EXE is 354 KB - and CL may need all of conventional memory
plus XMS), or the driver needs `TOOLS.INI`/`INIT` to locate its phase binaries.
Running `C1.EXE` through `--run` directly will separate a driver crash from a
phase crash.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 69: two harness fixes, MSC 6.0 CL still silent (no new rows)
Chased the last blocker on the pre-MSC7 toolchain. Three findings, two of them
lasting improvements:

1. **DOSBox-X needs the APPDATA redirect.** Run by hand without it, the emulator
   exits immediately and *nothing* in the autoexec runs - which is why several of
   round 68's manual probes produced no files at all and looked like compiler
   failures. With `APPDATA`/`LOCALAPPDATA`/`USERPROFILE` pointing at
   `dosboxx_home`, the same conf works. Every manual DOSBox test from now on must
   take the same environment as `build.py`.
2. **The extraction is byte-perfect.** `tools/extract_disks.py`'s output for
   `C1.EXE` (148 060 B) and `C2.EXE` (354 338 B) is **md5-identical** to the
   copies already in `toolchain/msc6c`, so the SZDD decompressor is correct and the
   DOS driver from DISK6 (`C 6.00A Sep 6 1990`, `-DMSDOS`, references
   `c1.err`/`c23.err`) is the genuine article.
3. **`build.py` grew two options it needed**: `--cd <dir>` (MSC 6.0 loads
   `c1.err`/`c23.err` from the current directory) and an absolute
   `C:\<MSC_DIR>\BIN\CL.EXE` path (required once `--cd` changes the directory).

With those in place the DOS driver still produces no object and no output at all -
not even its banner - so it is failing before it can print. The next probes are
`dir C:\MSC6DOS\BIN\CL.EXE > file` from inside the session (to confirm the mount
sees the binary) and running `C1.EXE` directly, which would tell whether the driver
or the phase binary is the problem.

MSC 7 is unaffected: the main toolchain still compiles and `verify.py` is green.

Ledger 455 rows (unchanged), PENDING 22; own-code coverage 9 796 B (3.341 %).

## Round 68: the MSC 6.00A distribution unpacked (no new rows)
Built `tools/extract_disks.py`, which reads the eight 1.2 MB FAT12 images in
`toolchain/msc6_disks` and decompresses Microsoft COMPRESS streams (`SZ` + `88 F0
27`, 12-byte header, LZSS over a 4 KB ring). It now provides a real DOS
toolchain tree:

- **CL.EXE (28 858 B, DISK6)** - the plain DOS driver: `e_lfanew = 0`, no NE/PE
  header, unlike DISK2's `CL.EX$` which `PACKING.LST` calls the "OS/2 compiler
  driver" (that is the NE binary behind round 67's "cannot be run in DOS mode");
- CL.MSG / CL.ERR beside it, C1.EXE (148 060 B) and C2.EXE (354 338 B) from DISK1.

That resolves the round 67 question: the workspace *had* a Windows/OS-2 CL, and the
DOS one was one disk away. The extractor documents the preference and is reusable
for any other compressed file on the set.

**Still open:** the DOS driver produces no object and no console output under
DOSBox-X even with its message files in place and the phases on `PATH`. Two
findings for the next attempt: DOSBox-X in this workspace silently does nothing when
its stdout is redirected to null (all manual tests must capture output), and the
driver exits without printing even its banner, which suggests it is not reaching the
phase binaries at all.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

## Round 67: the MSC 6.0 failure diagnosed, and the original disks found (no new rows)
Round 66 left the older-compiler route blocked. This round found **why**, and found
the means to fix it.

Running `toolchain/msc6i/BIN/CL.EXE` with its output captured prints

    This program cannot be run in DOS mode.

which is the 16-bit Windows (NE) stub message: that CL.EXE is a *Windows* hosted
compiler, not the DOS one, so DOSBox can never build with it. A header check over
every toolchain in the tree gives the full picture:

| toolchain | CL.EXE | verdict |
|---|---|---|
| msc7i (what every verified row uses) | 71 680 B | runs |
| msc6i | 29 859 B | NE, Windows - cannot run in DOS |
| msc6b | 71 680 B | PE header |
| msc6c | 81 184 B | MZ, but no object and no CL log |
| msc51 | 31 329 B | MZ, EXEPACK-packed |

**The original MSC 6.0 distribution is in the workspace**:
`toolchain/msc6_disks/DISK1..8.IMG`, eight 1.2 MB floppy images. The DOS-hosted
compiler binaries are almost certainly inside, so extracting them into a fresh
`toolchain/msc6dos` (FAT12 read of the images) is the concrete next step - and it
is the only remaining path to testing the `2B C0` / `add reg,reg` / padded-jump
classes by experiment rather than by reading.

MSC 7 remains working throughout (`build.py` compiles the probe, `verify.py` is
green): this was a fault in the alternative toolchains, not in the harness.

Ledger 455 rows (unchanged), PENDING 22; own-code coverage 9 796 B (3.341 %).

## Round 66: the older-compiler route is blocked at the toolchain (no new rows)
The `sub ax,ax` class (round 65) is exactly the kind of thing an older compiler
would emit, so this round tried to reach MSC 6.0 to test it. Result: the
alternative-toolchain route is currently **unusable**, not merely untested.

- `toolchain/msc6i` and `toolchain/msc6c` both contain `BIN/CL.EXE`, and `build.py`
  starts DOSBox and runs it, but **no object is produced** - not for the target
  source and not for a three-line `int f(int a) { return a + 1; }` probe, with
  either `/G1 /AM /Gs /Os` or the minimal `/AM /Os`.
- `toolchain/msc51` is documented in `docs/GAP.md` as EXEPACK-packed and unrunnable.
- MSC 7 itself is unaffected: the same probe compiles and dumps correctly
  (`55 8B EC 8B 46 06 40 C9 CA 02 00`), so this is not an environment regression.

So the `sub ax,ax` / `add reg,reg` / padded-jump classes cannot be tested against
MSC 6.0 until that toolchain actually builds, and the honest status of the
"alternative compiler" line of the objective remains: **MSC 7 is the only compiler
this workspace can run**.

Ledger 455 rows (unchanged), PENDING 22; verify and checkled green; own-code
coverage 9 796 B (3.341 %).

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
